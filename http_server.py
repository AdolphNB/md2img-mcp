#!/usr/bin/env python3
"""
word2img-mcp HTTP Server
支持 Streamable HTTP 传输方式的 MCP 服务器
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from word2img_mcp.mcp_app import server, _store
from mcp import types
from mcp.server.models import InitializationOptions

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="word2img-mcp HTTP Server",
    description="MCP服务器 - 支持Streamable HTTP传输方式",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量存储服务器状态
mcp_server = server
server_initialized = False
client_capabilities = None

class MCPHTTPHandler:
    """处理MCP HTTP请求的类"""
    
    def __init__(self):
        self.request_id = 0
    
    def get_next_request_id(self) -> int:
        """获取下一个请求ID"""
        self.request_id += 1
        return self.request_id
    
    async def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP请求并返回响应"""
        try:
            method = request_data.get("method")
            params = request_data.get("params", {})
            request_id = request_data.get("id")
            
            logger.info(f"处理MCP请求: {method}")
            
            if method == "initialize":
                return await self.handle_initialize(params, request_id)
            elif method == "initialized":
                return await self.handle_initialized(request_id)
            elif method == "tools/list":
                return await self.handle_list_tools(request_id)
            elif method == "tools/call":
                return await self.handle_call_tool(params, request_id)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"未知方法: {method}"
                    }
                }
        except Exception as e:
            logger.error(f"处理请求时发生错误: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"内部服务器错误: {str(e)}"
                }
            }
    
    async def handle_initialize(self, params: Dict[str, Any], request_id: int) -> Dict[str, Any]:
        """处理初始化请求"""
        global server_initialized, client_capabilities
        
        client_capabilities = params.get("capabilities", {})
        
        # 服务器能力
        server_capabilities = {
            "tools": {},
            "resources": {},
            "prompts": {},
            "logging": {}
        }
        
        server_initialized = True
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": server_capabilities,
                "serverInfo": {
                    "name": "word2img-mcp",
                    "version": "1.0.0"
                }
            }
        }
    
    async def handle_initialized(self, request_id: Optional[int]) -> Dict[str, Any]:
        """处理初始化完成通知"""
        logger.info("MCP服务器初始化完成")
        if request_id:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {}
            }
        return {}
    
    async def handle_list_tools(self, request_id: int) -> Dict[str, Any]:
        """处理工具列表请求"""
        try:
            tools = await mcp_server.list_tools()
            
            # 转换工具格式
            tools_data = []
            for tool in tools:
                tools_data.append({
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                })
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": tools_data
                }
            }
        except Exception as e:
            logger.error(f"获取工具列表失败: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"获取工具列表失败: {str(e)}"
                }
            }
    
    async def handle_call_tool(self, params: Dict[str, Any], request_id: int) -> Dict[str, Any]:
        """处理工具调用请求"""
        try:
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if not tool_name:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "缺少工具名称参数"
                    }
                }
            
            # 调用MCP服务器的工具处理函数
            result_content = await mcp_server.call_tool(tool_name, arguments)
            
            # 转换结果格式
            content_data = []
            for content in result_content:
                if isinstance(content, types.TextContent):
                    content_data.append({
                        "type": "text",
                        "text": content.text
                    })
                elif isinstance(content, types.ImageContent):
                    content_data.append({
                        "type": "image",
                        "data": content.data,
                        "mimeType": content.mimeType
                    })
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": content_data
                }
            }
        except Exception as e:
            logger.error(f"工具调用失败: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"工具调用失败: {str(e)}"
                }
            }

# 创建处理器实例
handler = MCPHTTPHandler()

@app.get("/")
async def root():
    """根路径 - 服务器信息"""
    return {
        "name": "word2img-mcp HTTP Server",
        "version": "1.0.0",
        "description": "MCP服务器 - 支持Streamable HTTP传输方式",
        "transport": "HTTP",
        "initialized": server_initialized,
        "endpoints": {
            "mcp": "/mcp",
            "health": "/health",
            "tools": "/tools"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server_initialized": server_initialized
    }

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """主要的MCP端点 - 处理JSON-RPC请求"""
    try:
        request_data = await request.json()
        logger.info(f"收到MCP请求: {request_data.get('method', 'unknown')}")
        
        # 处理请求
        response_data = await handler.handle_request(request_data)
        
        return JSONResponse(content=response_data)
        
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "JSON解析错误"
                }
            }
        )
    except Exception as e:
        logger.error(f"MCP端点处理错误: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"内部服务器错误: {str(e)}"
                }
            }
        )

@app.get("/tools")
async def list_tools_endpoint():
    """便捷的工具列表端点（非MCP标准）"""
    try:
        tools = await mcp_server.list_tools()
        tools_data = []
        for tool in tools:
            tools_data.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            })
        return {"tools": tools_data}
    except Exception as e:
        logger.error(f"获取工具列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取工具列表失败: {str(e)}")

@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE端点 - 用于流式通信（可选功能）"""
    async def event_generator():
        """生成SSE事件"""
        # 发送初始连接事件
        yield f"data: {json.dumps({'type': 'connected', 'timestamp': datetime.now().isoformat()})}\n\n"
        
        # 这里可以添加更多的流式数据逻辑
        # 例如：任务状态更新、实时日志等
        
        # 保持连接活跃
        try:
            while True:
                # 发送心跳
                yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"
                await asyncio.sleep(30)  # 每30秒发送一次心跳
        except asyncio.CancelledError:
            logger.info("SSE连接已断开")
            break
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

def run_http_server(host: str = "0.0.0.0", port: int = 8000, log_level: str = "info"):
    """运行HTTP服务器"""
    print("word2img-mcp HTTP服务器")
    print("=" * 50)
    print("传输方式: Streamable HTTP")
    print(f"监听地址: http://{host}:{port}")
    print()
    print("可用端点:")
    print(f"  - 主MCP端点: http://{host}:{port}/mcp")
    print(f"  - 健康检查: http://{host}:{port}/health")
    print(f"  - 工具列表: http://{host}:{port}/tools")
    print(f"  - SSE流式: http://{host}:{port}/sse")
    print()
    print("服务说明:")
    print("  - 将 Markdown 文本转换为高质量图片")
    print("  - 支持多种渲染后端 (imgkit/wkhtmltopdf 优先)")
    print("  - 3:4 图片比例，可自定义样式")
    print()
    print("输出目录: outputs/")
    print("=" * 50)
    print("正在启动HTTP服务器，等待客户端连接...")
    print("按 Ctrl+C 停止服务")
    print()
    
    try:
        # 确保输出目录存在
        os.makedirs("outputs", exist_ok=True)
        
        # 启动服务器
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"\n❌ HTTP服务器启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_http_server()
