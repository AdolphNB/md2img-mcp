# 📚 word2img-mcp MCP 服务使用指南

## 🚀 启动服务

### 方法 1: 使用启动脚本（推荐）
```bash
uv run python start_mcp_server.py
```
这会显示详细的服务信息并启动 MCP 服务。

### 方法 2: 使用模块方式
```bash
uv run python -m word2img_mcp
```

### 方法 3: 直接运行服务文件
```bash
uv run python server.py
```

## 🛠️ MCP 工具接口

### 1. submit_markdown
**功能**: 提交 Markdown 文本并生成图片

**参数**:
- `markdown_text` (必需): 要渲染的 Markdown 文本
- `align` (可选): 文本对齐方式 - "center" (默认) 或 "left"
- `bold` (可选): 是否加粗显示 - true 或 false (默认)
- `width` (可选): 图片宽度，默认 1080px (高度按 3:4 比例自动计算)

**返回**: 任务 ID 字符串

**示例**:
```json
{
  "name": "submit_markdown",
  "arguments": {
    "markdown_text": "# 标题\n\n这是一个**测试**文档。\n\n- 项目 1\n- 项目 2",
    "align": "center",
    "width": 1200
  }
}
```

### 2. get_image
**功能**: 根据任务 ID 获取生成的图片

**参数**:
- `task_id` (必需): submit_markdown 返回的任务 ID
- `as_base64` (可选): 是否返回 base64 编码 - true (默认) 或 false

**返回**: 
- 如果 `as_base64=true`: base64 编码的图片数据
- 如果 `as_base64=false`: 图片文件路径

**示例**:
```json
{
  "name": "get_image", 
  "arguments": {
    "task_id": "img_12345678",
    "as_base64": true
  }
}
```

## 🎨 渲染特性

### 多后端支持
1. **imgkit/wkhtmltopdf** ⭐ (最高优先级)
   - 专业级 HTML 渲染引擎
   - 完美的字体和布局
   - 支持复杂样式

2. **markdown-pdf-cli** (备选)
   - Node.js 生态系统
   - 快速 PDF 生成

3. **PIL 本地渲染** (保底)
   - 纯 Python 实现
   - 无外部依赖

### 支持的 Markdown 语法
- ✅ 标题 (H1-H6)
- ✅ 段落和文本格式化
- ✅ 列表 (有序/无序)
- ✅ 表格
- ✅ 代码块和行内代码
- ✅ 引用块
- ✅ 水平分割线
- ✅ 链接
- ✅ **粗体** 和 *斜体*

### 样式特性
- 🎨 自定义颜色方案
- 📐 3:4 图片比例
- 🔤 中文字体优化
- 💧 水印支持
- 🌗 明暗主题
- 📏 可调整尺寸

## 🔧 客户端集成

### Claude Desktop 配置
在 Claude Desktop 的 MCP 配置中添加：

```json
{
  "mcpServers": {
    "word2img-mcp": {
      "command": "uv",
      "args": ["run", "python", "-m", "word2img_mcp"],
      "cwd": "/path/to/word2img-mcp"
    }
  }
}
```

### 其他 MCP 客户端
任何支持 MCP 协议的客户端都可以连接此服务。服务使用标准的 stdio 通信方式。

## 📁 文件输出

### 输出目录
生成的图片保存在 `outputs/` 目录中。

### 文件命名规则
- `imgkit_[pid]_[hash].[ext]`: imgkit/wkhtmltopdf 后端生成
- `md_pdf_[pid]_[hash].[ext]`: markdown-pdf 后端生成  
- `pil_[pid]_[hash].[ext]`: PIL 后端生成

### 支持的格式
- **PNG**: 高质量，支持透明背景
- **JPG**: 压缩格式，文件较小
- **PDF**: 矢量格式（部分后端支持）

## 🔍 故障排除

### 常见问题

#### 1. 服务启动失败
**检查**:
- 确保所有依赖已安装: `uv sync`
- 检查 Python 版本: >= 3.13
- 查看错误日志

#### 2. 渲染质量不佳
**解决**:
- 安装 wkhtmltopdf 获得最佳质量
- 调整图片尺寸参数
- 检查后端使用情况

#### 3. 中文显示问题
**解决**:
- 确保系统安装了中文字体
- Windows: 自动使用微软雅黑
- macOS: 自动使用 PingFang SC
- Linux: 安装中文字体包

### 调试模式
启动时添加环境变量查看详细日志：
```bash
export PYTHONPATH=.
export MCP_DEBUG=1
uv run python -m word2img_mcp
```

## 📊 性能信息

### 渲染时间
- 简单文档: 1-2 秒
- 复杂文档: 3-5 秒
- 包含表格/代码: 2-4 秒

### 文件大小
- PNG 格式: 2-8 MB (高质量)
- JPG 格式: 100-500 KB (压缩)
- PDF 格式: 500 KB - 2 MB

### 内存使用
- 基础运行: ~50-100 MB
- 渲染过程中: +100-200 MB
- 并发处理: 每任务 +50 MB

## 📚 更多文档

- **[IMGKIT_USAGE.md](IMGKIT_USAGE.md)** - imgkit/wkhtmltopdf 详细使用指南
- **[README.md](README.md)** - 项目总览
- **[IMGKIT_IMPLEMENTATION_SUMMARY.md](IMGKIT_IMPLEMENTATION_SUMMARY.md)** - 技术实现详情

## 🎉 享用服务

现在您可以通过 MCP 客户端享受高质量的 Markdown 到图片转换服务了！

**专业提示**: 安装 wkhtmltopdf 可获得最佳渲染质量和完整功能支持。
