#!/usr/bin/env python3
"""
快速启动和测试 MCP 服务的脚本
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def show_service_info():
    """显示服务信息"""
    print("🚀 word2img-mcp MCP 服务")
    print("=" * 40)
    print("📋 可用工具:")
    print("  1. submit_markdown - 提交 Markdown 生成图片")
    print("  2. get_image - 获取生成的图片")
    print()
    print("🎨 渲染后端:")
    print("  • imgkit/wkhtmltopdf ⭐ (最高质量)")
    print("  • markdown-pdf-cli")
    print("  • PIL 备选")
    print()
    print("📁 输出目录: outputs/")
    print("=" * 40)

def show_usage_examples():
    """显示使用示例"""
    print("\n💡 使用示例:")
    print()
    
    # submit_markdown 示例
    submit_example = {
        "name": "submit_markdown",
        "arguments": {
            "markdown_text": "# 测试标题\n\n这是一个**测试**文档。\n\n- 项目 1\n- 项目 2",
            "align": "center", 
            "width": 1200
        }
    }
    
    print("1. 提交 Markdown:")
    print(json.dumps(submit_example, ensure_ascii=False, indent=2))
    print()
    
    # get_image 示例
    get_example = {
        "name": "get_image",
        "arguments": {
            "task_id": "img_12345678",
            "as_base64": True
        }
    }
    
    print("2. 获取图片:")
    print(json.dumps(get_example, ensure_ascii=False, indent=2))
    print()

def show_startup_methods():
    """显示启动方法"""
    print("\n🚀 启动方法:")
    print()
    print("方法 1 (推荐):")
    print("  uv run python start_mcp_server.py")
    print()
    print("方法 2:")
    print("  uv run python -m word2img_mcp")
    print()
    print("方法 3:")
    print("  uv run python server.py")
    print()

def test_import():
    """测试模块导入"""
    print("🧪 测试模块导入...")
    try:
        from word2img_mcp import run_server, RenderOptions
        print("✅ 模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def main():
    """主函数"""
    print("🎯 word2img-mcp MCP 服务快速启动指南")
    print()
    
    # 显示服务信息
    show_service_info()
    
    # 测试导入
    if not test_import():
        print("\n💡 请先安装依赖: uv sync")
        return
    
    # 显示使用示例
    show_usage_examples()
    
    # 显示启动方法
    show_startup_methods()
    
    print("📚 详细文档:")
    print("  • MCP_SERVICE_GUIDE.md - 完整使用指南")
    print("  • IMGKIT_USAGE.md - 渲染后端说明")
    print()
    print("✅ 服务已准备就绪，使用上述任一方法启动！")

if __name__ == "__main__":
    main()
