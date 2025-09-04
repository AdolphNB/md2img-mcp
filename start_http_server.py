#!/usr/bin/env python3
"""
word2img-mcp HTTP 服务启动脚本
支持 Streamable HTTP 传输方式
"""

import argparse
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """启动 MCP HTTP 服务"""
    parser = argparse.ArgumentParser(description="word2img-mcp HTTP服务器")
    parser.add_argument("--host", default="0.0.0.0", help="监听主机地址 (默认: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="监听端口 (默认: 8000)")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"], help="日志级别")
    parser.add_argument("--stdio", action="store_true", help="使用stdio模式而不是HTTP模式")
    
    args = parser.parse_args()
    
    if args.stdio:
        # 使用原来的stdio模式
        print("启动stdio模式...")
        from word2img_mcp import run_server
        import asyncio
        try:
            asyncio.run(run_server())
        except KeyboardInterrupt:
            print("\n服务已停止")
        except Exception as e:
            print(f"\n❌ 服务启动失败: {e}")
            sys.exit(1)
    else:
        # 使用HTTP模式
        from http_server import run_http_server
        run_http_server(host=args.host, port=args.port, log_level=args.log_level)

if __name__ == "__main__":
    main()
