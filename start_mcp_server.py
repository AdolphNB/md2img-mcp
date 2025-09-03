#!/usr/bin/env python3
"""
word2img-mcp MCP 服务启动脚本
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from word2img_mcp import run_server

def main():
    """启动 MCP 服务"""
    print("word2img-mcp MCP 服务启动器")
    print("=" * 50)
    print("服务说明:")
    print("  - 将 Markdown 文本转换为高质量图片")
    print("  - 支持多种渲染后端 (imgkit/wkhtmltopdf 优先)")
    print("  - 3:4 图片比例，可自定义样式")
    print()
    print("可用工具:")
    print("  - submit_markdown: 提交 Markdown 文本生成图片")
    print("  - get_image: 获取生成的图片 (Base64 或文件路径)")
    print()
    print("当前渲染后端优先级:")
    print("  1. imgkit/wkhtmltopdf * (最高质量)")
    print("  2. markdown-pdf-cli")
    print("  3. md-to-image")
    print("  4. PIL 备选 (保证可用)")
    print()
    print("输出目录: outputs/")
    print("=" * 50)
    print("正在启动服务，等待客户端连接...")
    print("按 Ctrl+C 停止服务")
    print()
    
    try:
        # 确保输出目录存在
        os.makedirs("outputs", exist_ok=True)
        
        # 启动服务
        asyncio.run(run_server())
    except KeyboardInterrupt:
        # 终止时避免在已关闭的 stdout 上输出导致异常
        try:
            print("\n服务已停止")
        except Exception:
            pass
        return
    except Exception as e:
        print(f"\n❌ 服务启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
