import asyncio
import os
from word2img_mcp.mcp_app import run_server
from word2img_mcp.render import RenderOptions, render_markdown_text_to_image

if __name__ == "__main__":
	# 本地快速验证：渲染示例图片
	text = "# 标题\n**加粗** 与 普通文本\n长段内容会自动换行并居中显示。"
	img = render_markdown_text_to_image(text, RenderOptions(align="center", bold=False))
	os.makedirs("outputs", exist_ok=True)
	img.save("outputs/_sample.jpg", format="JPEG", quality=95, subsampling=0, optimize=True)
	print("Sample saved to outputs/_sample.jpg")
	# 启动 MCP 服务
	asyncio.run(run_server())
