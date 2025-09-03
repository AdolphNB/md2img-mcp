#!/usr/bin/env python3
"""
word2img-mcp MCP 服务启动入口
"""

import asyncio
from .mcp_app import run_server

if __name__ == "__main__":
    print("🚀 启动 word2img-mcp MCP 服务...")
    print("📊 支持的工具:")
    print("  - submit_markdown: 提交 Markdown 文本生成图片")
    print("  - get_image: 获取生成的图片")
    print("🎨 渲染后端: imgkit/wkhtmltopdf (优先), markdown-pdf, PIL")
    print("⏳ 等待客户端连接...")
    
    asyncio.run(run_server())
