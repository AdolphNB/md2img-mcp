"""
word2img-mcp: Markdown to Image MCP Server

一个将 Markdown 文本渲染为高质量图片的 MCP 服务。
支持 imgkit/wkhtmltopdf、markdown-pdf、PIL 等多种渲染后端。
"""

__version__ = "1.0.0"
__author__ = "mcp"
__description__ = "MCP service to render Markdown text into high-quality images"

from .render import RenderOptions, render_markdown_text_to_image, MarkdownRenderer
from .mcp_app import server, run_server
from .store import ImageStore

__all__ = [
    "RenderOptions",
    "render_markdown_text_to_image", 
    "MarkdownRenderer",
    "server",
    "run_server",
    "ImageStore"
]
