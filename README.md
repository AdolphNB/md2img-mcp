# word2img-mcp

一个将 Markdown 文本渲染到 3:4 JPG 图片上的 MCP 服务，支持多种高质量渲染后端。

## 🚀 核心特性

- **多后端渲染**: 支持 imgkit/wkhtmltopdf、markdown-pdf、PIL 等多种渲染方案
- **智能回退**: 自动选择最佳可用后端，确保渲染成功
- **高质量输出**: 专业级别的图片渲染质量
- **自定义样式**: 丰富的样式配置选项
- **中文支持**: 完美支持中文字体和排版

## 📋 渲染后端

1. **imgkit/wkhtmltopdf** ⭐ (推荐)
   - 最高渲染质量
   - 完整的 HTML/CSS 支持
   - 需要安装 wkhtmltopdf

2. **markdown-pdf-cli**
   - 高质量 PDF 生成
   - 需要 Node.js 环境

3. **PIL 备选方案**
   - 本地纯 Python 渲染
   - 无额外依赖

## 🛠️ MCP 工具接口

- **submit_markdown**: 提交文本并生成图片
- **get_image**: 根据任务ID返回图片（Base64或路径）

## 使用 uv 管理

### 准备
- 安装 uv（若未安装）：参考官方文档或使用 pipx 安装

```bash
pipx install uv
```

### 安装依赖

```bash
# 安装基础依赖
uv sync

# 安装 imgkit 后端依赖（推荐）
uv add imgkit markdown

# 安装 wkhtmltopdf (获得最佳渲染效果)
# Windows: 从 https://wkhtmltopdf.org/downloads.html 下载安装
# macOS: brew install wkhtmltopdf
# Ubuntu: sudo apt-get install wkhtmltopdf
```

### 运行演示

```bash
# 运行 imgkit 后端演示
uv run python demo_imgkit.py

# 运行基础演示
uv run python server.py
# 生成 outputs/_sample.jpg

# 测试 imgkit 后端功能
uv run python test_imgkit_backend.py
```

### 作为 MCP 服务

#### 启动服务
```bash
# 方法 1: 使用启动脚本（推荐）
uv run python start_mcp_server.py

# 方法 2: 使用模块方式
uv run python -m word2img_mcp

# 方法 3: 直接运行
uv run python server.py
```

#### MCP 客户端配置

**Claude Desktop 配置**

1. 找到 Claude Desktop 配置文件：
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/claude/claude_desktop_config.json`

2. 编辑配置文件，添加以下内容：

```json
{
  "mcpServers": {
    "word2img-mcp": {
      "command": "uv",
      "args": [
        "run", 
        "python", 
        "-m", 
        "word2img_mcp"
      ],
      "cwd": "/path/to/your/word2img-mcp",
      "env": {
        "UV_PROJECT_ENVIRONMENT": ".venv"
      }
    }
  }
}
```

**配置说明**：
- `command`: 使用 `uv` 命令
- `args`: 运行参数，启动 word2img_mcp 模块
- `cwd`: **请修改为您的项目实际路径**
- `env`: 环境变量设置（可选）

**Windows 完整示例**：
```json
{
  "mcpServers": {
    "word2img-mcp": {
      "command": "uv",
      "args": ["run", "python", "-m", "word2img_mcp"],
      "cwd": "D:\\mcpServer\\word2img-mcp"
    }
  }
}
```

**macOS/Linux 完整示例**：
```json
{
  "mcpServers": {
    "word2img-mcp": {
      "command": "uv",
      "args": ["run", "python", "-m", "word2img_mcp"],
      "cwd": "/Users/username/word2img-mcp"
    }
  }
}
```

3. 重启 Claude Desktop
4. 在对话中可以使用以下工具：
   - `submit_markdown`: 提交 Markdown 文本生成图片
   - `get_image`: 获取生成的图片

> 💡 **提示**: 可以参考项目根目录的 [`claude_desktop_config_example.json`](claude_desktop_config_example.json) 示例文件

#### 验证配置

配置完成后，在 Claude Desktop 中发送消息验证：

```
请帮我把以下 Markdown 转换为图片：

# 测试标题
这是一个 **测试** 文档，用来验证 MCP 服务是否正常工作。

- 功能测试
- 样式测试

表格测试：
| 项目 | 状态 |
|------|------|
| MCP 配置 | ✅ |
| 图片生成 | ✅ |
```

如果配置成功，Claude 会自动调用 MCP 服务生成图片。

## 🎨 样式配置

### 基础选项
- **背景色**: 默认纯白，支持自定义
- **文字色**: 默认黑色，支持自定义
- **对齐方式**: 支持居中、左对齐、右对齐
- **字体**: 自适应中文字体，支持自定义字体族
- **尺寸**: 默认 3:4 比例，可自定义宽高

### 高级功能
- **水印**: 可添加自定义水印文字
- **阴影**: 标题文字阴影效果
- **主题**: 支持亮色/暗色主题
- **多格式**: PNG、JPG、PDF 输出格式

## 📚 详细文档

- **[MCP 服务使用指南](MCP_SERVICE_GUIDE.md)** - 完整的 MCP 服务配置和使用说明
- **[imgkit/wkhtmltopdf 使用指南](IMGKIT_USAGE.md)** - 完整的安装和使用说明
- **[实现总结](IMPLEMENTATION_SUMMARY.md)** - 技术实现详细说明

## 🔧 故障排除

如果遇到渲染问题，系统会自动尝试以下后端顺序：
1. imgkit/wkhtmltopdf (最佳质量)
2. markdown-pdf-cli
3. md-to-image (CLI/API)
4. PIL 备选 (保证可用)
