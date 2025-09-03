#!/usr/bin/env python3
"""
imgkit/wkhtmltopdf 方案演示脚本
"""

import os
import sys
from pathlib import Path

# 添加项目目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from word2img_mcp.render import RenderOptions, render_markdown_text_to_image


def demo_imgkit_rendering():
    """演示 imgkit 渲染功能"""
    print("imgkit/wkhtmltopdf 渲染方案演示")
    print("=" * 50)
    
    # 示例 Markdown 内容
    demo_content = """
# 🚀 imgkit/wkhtmltopdf 渲染演示

欢迎使用基于 **imgkit** 和 **wkhtmltopdf** 的高质量 Markdown 渲染方案！

## ✨ 主要特性

### 🎯 高质量渲染
- **HTML 引擎**: 使用成熟的 HTML 渲染引擎
- **CSS 样式**: 完整的 CSS 样式支持
- **字体渲染**: 优秀的字体和排版效果

### 🛠️ 丰富功能
1. **多样式支持**
   - 自定义颜色方案
   - 字体大小和间距控制
   - 文本对齐选项

2. **内容支持**
   - 标题层级
   - 文本格式化（**粗体**、*斜体*）
   - 列表和表格
   - 代码块和引用

### 📊 示例表格

| 功能项 | imgkit 方案 | 其他方案 |
|--------|-------------|----------|
| 渲染质量 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 样式控制 | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 中文支持 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 复杂布局 | ⭐⭐⭐⭐⭐ | ⭐⭐ |

### 💻 代码示例

```python
# 使用 imgkit 渲染 Markdown
from word2img_mcp.render import RenderOptions, render_markdown_text_to_image

options = RenderOptions(
    width=1200,
    height=1600,
    background=(255, 255, 255),
    text_color=(0, 0, 0),
    accent_color=(70, 130, 180),
    watermark=True
)

output_path = render_markdown_text_to_image(markdown_text, options)
```

### 📝 引用示例

> "imgkit + wkhtmltopdf 提供了卓越的 HTML 到图片转换能力，
> 特别适合需要高质量输出的场景。"
> 
> — 技术文档

---

**测试完成！** 如果您看到这个图片，说明渲染系统正常工作。

*注意：如果未安装 wkhtmltopdf，系统会自动回退到其他可用的渲染后端。*
    """
    
    # 创建不同样式的演示
    demos = [
        {
            "name": "默认样式",
            "options": RenderOptions(
                width=1200,
                height=1600,
                output_format="png"
            )
        },
        {
            "name": "居中对齐",
            "options": RenderOptions(
                width=1000,
                height=1400,
                align="center",
                font_size=18,
                background=(248, 249, 250),
                text_color=(33, 37, 41),
                accent_color=(13, 110, 253),
                output_format="jpg"
            )
        },
        {
            "name": "暗色主题",
            "options": RenderOptions(
                width=1200,
                height=1600,
                background=(33, 37, 41),
                text_color=(248, 249, 250),
                accent_color=(108, 117, 125),
                shadow=True,
                watermark=True,
                watermark_text="Dark Theme Demo",
                output_format="png"
            )
        }
    ]
    
    # 确保输出目录存在
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    # 生成演示图片
    for i, demo in enumerate(demos, 1):
        print(f"\n{i}. 生成 {demo['name']} 演示...")
        
        try:
            output_path = render_markdown_text_to_image(demo_content, demo["options"])
            
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"   ✅ 成功生成: {output_path}")
                print(f"   📊 文件大小: {file_size / 1024:.1f} KB")
                
                # 检测使用的后端
                filename = os.path.basename(output_path)
                if "imgkit" in filename:
                    print(f"   🎯 使用后端: imgkit/wkhtmltopdf")
                elif "md_pdf" in filename:
                    print(f"   🎯 使用后端: markdown-pdf")
                elif "pil" in filename:
                    print(f"   🎯 使用后端: PIL (备选)")
                else:
                    print(f"   🎯 使用后端: 其他")
            else:
                print(f"   ❌ 文件生成失败")
                
        except Exception as e:
            print(f"   ❌ 渲染失败: {e}")
    
    print("\n" + "=" * 50)
    print("所有生成的文件都保存在 outputs/ 目录中")
    print("提示: 安装 wkhtmltopdf 以获得最佳渲染效果")


def show_backend_status():
    """显示各个后端的状态"""
    print("\n渲染后端状态检查")
    print("-" * 30)
    
    # 检查 imgkit
    try:
        import imgkit
        print("✅ imgkit: 已安装")
        
        # 检查 wkhtmltopdf
        try:
            # 简单的测试命令
            import subprocess
            result = subprocess.run(['wkhtmltoimage', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ wkhtmltopdf: 已安装且可用")
            else:
                print("⚠️  wkhtmltopdf: 安装但不可用")
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            print("❌ wkhtmltopdf: 未安装或不在 PATH 中")
            
    except ImportError:
        print("❌ imgkit: 未安装")
    
    # 检查 PIL
    try:
        from PIL import Image
        print("✅ PIL/Pillow: 已安装 (备选后端)")
    except ImportError:
        print("❌ PIL/Pillow: 未安装")
    
    # 检查 markdown
    try:
        import markdown
        print("✅ python-markdown: 已安装")
    except ImportError:
        print("❌ python-markdown: 未安装")


def main():
    """主函数"""
    print("欢迎使用 imgkit/wkhtmltopdf 渲染方案！")
    
    # 显示后端状态
    show_backend_status()
    
    # 运行演示
    demo_imgkit_rendering()
    
    print(f"\n详细使用说明请查看: IMGKIT_USAGE.md")
    print(f"安装指南:")
    print(f"   1. Python 依赖: uv add imgkit markdown")
    print(f"   2. wkhtmltopdf: https://wkhtmltopdf.org/downloads.html")
    print(f"   3. 将 wkhtmltopdf 添加到系统 PATH")


if __name__ == "__main__":
    main()
