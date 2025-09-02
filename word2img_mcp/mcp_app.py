import base64
import os
import asyncio
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from .render import ASPECT_RATIO, RenderOptions, render_markdown_text_to_image
from .store import ImageStore

_store = ImageStore()

# Create the server instance
server = Server("word2img-mcp")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="submit_markdown",
            description="接收Markdown文本并生成3:4 JPG图片，返回任务ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "markdown_text": {"type": "string", "description": "要渲染的Markdown文本"},
                    "align": {"type": "string", "enum": ["center", "left"], "default": "center", "description": "文本对齐方式"},
                    "bold": {"type": "boolean", "default": False, "description": "是否加粗显示"},
                    "width": {"type": "integer", "default": 1080, "description": "图片宽度（高度按3:4比例计算）"}
                },
                "required": ["markdown_text"]
            }
        ),
        types.Tool(
            name="get_image",
            description="根据任务ID返回图片。可选base64返回或文件路径",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "任务ID"},
                    "as_base64": {"type": "boolean", "default": True, "description": "是否返回base64编码（否则返回文件路径）"}
                },
                "required": ["task_id"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle tool calls."""
    if name == "submit_markdown":
        markdown_text = arguments["markdown_text"]
        align = arguments.get("align", "center")
        bold = arguments.get("bold", False)
        width = arguments.get("width", 1080)
        
        height = int(width * ASPECT_RATIO[1] / ASPECT_RATIO[0])
        options = RenderOptions(width=width, height=height, align=align, bold=bold)
        img = render_markdown_text_to_image(markdown_text, options)
        task_id = _store.save_image(img)
        
        return [types.TextContent(type="text", text=task_id)]
    
    elif name == "get_image":
        task_id = arguments["task_id"]
        as_base64 = arguments.get("as_base64", True)
        
        path = _store.get_path(task_id)
        if not path or not os.path.exists(path):
            raise ValueError("任务ID无效或图片不存在")
        
        if not as_base64:
            return [types.TextContent(type="text", text=path)]
        
        with open(path, "rb") as f:
            b = f.read()
        b64_data = base64.b64encode(b).decode("utf-8")
        return [types.TextContent(type="text", text=b64_data)]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def run_server() -> None:
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )
