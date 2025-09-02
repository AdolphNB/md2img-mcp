# word2img-mcp

一个将 Markdown 文本渲染到 3:4 JPG 图片上的 MCP 服务。

- 输入：Markdown 格式文本
- 输出：JPG 图片（3:4，白/浅色背景，高可读性），返回 Base64 或图片路径
- 工具：
  - submit_markdown：提交文本并生成图片
  - get_image：根据任务ID返回图片（Base64或路径）

## 使用 uv 管理

### 准备
- 安装 uv（若未安装）：参考官方文档或使用 pipx 安装

```bash
pipx install uv
```

### 安装依赖

```bash
uv sync
```

### 运行（本地测试）

```bash
uv run python server.py
# 生成 outputs/_sample.jpg
```

### 作为 MCP 服务
- 直接运行：
```bash
uv run python server.py
```
- 客户端按 MCP 方式注册该服务后，可调用工具：
  - submit_markdown(markdown_text, align='center'|'left', bold=False, width=1200) -> task_id
  - get_image(task_id, as_base64=True|False) -> base64字符串或文件路径

## 说明与约束
- 背景默认纯白，可改浅色；不添加多余背景元素。
- 自动换行与内边距：左右 8%，上下 8%，避免贴边。
- 字体在 72~24 范围内自适应，JPG 输出 3:4（默认1200x1600，可通过 width 成比例调整）。
- 对齐方式默认居中，可设左对齐；加粗通过 bold 参数控制。
