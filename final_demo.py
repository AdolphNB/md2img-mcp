#!/usr/bin/env python3
"""
imgkit/wkhtmltopdf 方案最终演示
展示完整的实现效果和功能特性
"""

import os
import sys
from pathlib import Path

# 添加项目目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from word2img_mcp.render import RenderOptions, render_markdown_text_to_image


def create_comprehensive_demo():
    """创建全面的功能演示"""
    
    demo_markdown = """
# 🎉 imgkit/wkhtmltopdf 方案演示

欢迎体验基于 **imgkit** 和 **wkhtmltopdf** 的高质量 Markdown 渲染方案！

## ✨ 核心特性展示

### 🎨 渲染质量
使用专业的 HTML 渲染引擎，提供**出色的视觉效果**和*精确的排版控制*。

### 🌐 完整的 Markdown 支持

#### 文本格式化
- **粗体文字** 用于强调重点内容
- *斜体文字* 用于表示引用或特殊含义
- `行内代码` 用于展示代码片段
- ~~删除线文字~~ 用于表示过时内容

#### 列表功能

**有序列表：**
1. 第一项内容
2. 第二项内容
   - 嵌套项目 A
   - 嵌套项目 B
3. 第三项内容

**无序列表：**
- ✅ 高质量渲染
- ✅ 丰富样式支持
- ✅ 完整 Markdown 语法
- ✅ 智能回退机制

### 📊 表格展示

| 渲染后端 | 质量评分 | 速度评分 | 功能评分 | 推荐度 |
|----------|----------|----------|----------|--------|
| imgkit/wkhtmltopdf | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 🥇 首选 |
| markdown-pdf | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 🥈 备选 |
| PIL 本地渲染 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | 🥉 保底 |

### 💻 代码展示

```python
# 使用 imgkit 方案进行渲染
from word2img_mcp.render import RenderOptions, render_markdown_text_to_image

def create_beautiful_image():
    options = RenderOptions(
        width=1200,
        height=1600,
        background=(255, 255, 255),  # 纯白背景
        text_color=(0, 0, 0),        # 深色文字
        accent_color=(70, 130, 180), # 优雅蓝色
        font_family="Microsoft YaHei, Arial",
        watermark=True,
        shadow=True
    )
    
    return render_markdown_text_to_image(markdown_text, options)
```

```bash
# 安装和配置指南
# 1. 安装 Python 依赖
uv add imgkit markdown

# 2. 安装 wkhtmltopdf
# Windows: 从官网下载安装包
# macOS: brew install wkhtmltopdf  
# Linux: apt-get install wkhtmltopdf

# 3. 运行演示
uv run python final_demo.py
```

### 📝 引用块展示

> **"imgkit + wkhtmltopdf 为 Markdown 渲染带来了革命性的改进，
> 它结合了 HTML 的灵活性和专业渲染引擎的高质量输出。"**
> 
> — 技术架构师

> 💡 **小贴士**: 如果没有安装 wkhtmltopdf，系统会自动回退到其他可用的渲染后端，
> 确保在任何环境下都能正常工作。

---

## 🔧 技术架构

### 多后端设计

系统采用智能多后端架构，优先级如下：

1. **imgkit/wkhtmltopdf** (最高优先级)
   - 使用 HTML/CSS 渲染引擎
   - 支持复杂样式和布局
   - 输出质量最佳

2. **markdown-pdf-cli** 
   - Node.js 生态系统支持
   - 快速 PDF 生成
   - 良好的兼容性

3. **PIL 备选方案** (保底选择)
   - 纯 Python 实现
   - 无外部依赖
   - 确保基础可用性

### 样式系统

- **动态 CSS 生成**: 根据配置参数实时生成样式
- **响应式设计**: 自适应不同尺寸要求
- **主题支持**: 亮色/暗色主题一键切换
- **字体优化**: 完美支持中文字体渲染

---

## 🎯 使用场景

### 🏢 企业文档
- 技术文档生成
- 报告制作
- 品牌化内容

### 📚 教育培训  
- 课件制作
- 学习资料
- 考试题目

### 🎨 内容创作
- 博客配图
- 社交媒体内容
- 营销材料

---

**感谢使用 imgkit/wkhtmltopdf 渲染方案！** 

如果您看到这张精美的图片，说明我们的实现完全成功！🎉✨
    """
    
    # 创建多种样式的演示
    demos = [
        {
            "name": "🎨 默认主题",
            "filename": "demo_default_theme",
            "options": RenderOptions(
                width=1200,
                height=1800,
                background=(255, 255, 255),
                text_color=(0, 0, 0),
                accent_color=(70, 130, 180),
                align="left",
                font_size=16,
                watermark=True,
                watermark_text="imgkit/wkhtmltopdf Demo",
                output_format="png"
            )
        },
        {
            "name": "🌙 暗色主题",
            "filename": "demo_dark_theme", 
            "options": RenderOptions(
                width=1200,
                height=1800,
                background=(33, 37, 41),
                text_color=(248, 249, 250),
                accent_color=(108, 117, 125),
                align="left",
                font_size=16,
                shadow=True,
                watermark=True,
                watermark_text="Dark Theme by imgkit",
                output_format="png"
            )
        },
        {
            "name": "📱 居中样式",
            "filename": "demo_center_style",
            "options": RenderOptions(
                width=1000,
                height=1600,
                background=(248, 249, 250),
                text_color=(33, 37, 41),
                accent_color=(13, 110, 253),
                align="center",
                font_size=18,
                line_height=1.8,
                shadow=True,
                watermark=True,
                watermark_text="Centered Layout Demo",
                output_format="jpg"
            )
        }
    ]
    
    print("🚀 开始生成 imgkit/wkhtmltopdf 全功能演示...")
    print("=" * 60)
    
    # 确保输出目录存在
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    results = []
    
    for i, demo in enumerate(demos, 1):
        print(f"\n{i}. 生成 {demo['name']} 演示...")
        
        try:
            output_path = render_markdown_text_to_image(demo_markdown, demo["options"])
            
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"   ✅ 生成成功: {output_path}")
                print(f"   📊 文件大小: {file_size / 1024:.1f} KB")
                
                # 检测使用的后端
                filename = os.path.basename(output_path)
                if "imgkit" in filename:
                    backend = "imgkit/wkhtmltopdf ⭐"
                elif "md_pdf" in filename:
                    backend = "markdown-pdf"
                elif "pil" in filename:
                    backend = "PIL (备选)"
                else:
                    backend = "其他"
                
                print(f"   🎯 使用后端: {backend}")
                results.append({"demo": demo["name"], "path": output_path, "backend": backend, "size": file_size})
                
            else:
                print(f"   ❌ 文件生成失败")
                results.append({"demo": demo["name"], "path": None, "backend": "失败", "size": 0})
                
        except Exception as e:
            print(f"   ❌ 渲染失败: {e}")
            results.append({"demo": demo["name"], "path": None, "backend": "错误", "size": 0})
    
    return results


def show_final_summary(results):
    """显示最终总结"""
    print("\n" + "=" * 60)
    print("📊 演示结果总结")
    print("=" * 60)
    
    successful = [r for r in results if r["path"] is not None]
    failed = [r for r in results if r["path"] is None]
    
    print(f"✅ 成功生成: {len(successful)}/{len(results)} 个演示")
    
    if successful:
        print("\n🎉 成功生成的演示:")
        for result in successful:
            print(f"   • {result['demo']}")
            print(f"     文件: {os.path.basename(result['path'])}")
            print(f"     后端: {result['backend']}")
            print(f"     大小: {result['size'] / 1024:.1f} KB")
            print()
    
    if failed:
        print("\n⚠️ 未能生成的演示:")
        for result in failed:
            print(f"   • {result['demo']} - {result['backend']}")
    
    # 检查 imgkit 后端使用情况
    imgkit_used = any("imgkit" in r["backend"] for r in successful)
    
    print("\n" + "=" * 60)
    if imgkit_used:
        print("🎯 **imgkit/wkhtmltopdf 后端运行正常!** ")
        print("   您的系统已正确配置 wkhtmltopdf，享受最佳渲染质量！")
    else:
        print("⚙️  **系统使用备选后端**")
        print("   要获得最佳效果，请安装 wkhtmltopdf:")
        print("   • Windows: https://wkhtmltopdf.org/downloads.html")
        print("   • macOS: brew install wkhtmltopdf")
        print("   • Linux: sudo apt-get install wkhtmltopdf")
    
    print(f"\n📁 所有文件保存在: {Path('outputs').absolute()}")
    print(f"📚 详细使用说明: IMGKIT_USAGE.md")
    print(f"🔧 实现总结: IMGKIT_IMPLEMENTATION_SUMMARY.md")


def main():
    """主函数"""
    print("🎨 imgkit/wkhtmltopdf 方案最终演示")
    print("🚀 展示完整的实现效果和功能特性")
    print()
    
    # 运行演示
    results = create_comprehensive_demo()
    
    # 显示总结
    show_final_summary(results)
    
    print("\n🎉 演示完成！感谢使用 imgkit/wkhtmltopdf 渲染方案！")


if __name__ == "__main__":
    main()
