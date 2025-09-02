import base64
import os

# Prefer the official 'mcp' package; fall back to 'modelcontextprotocol'; else provide a shim
try:
	from mcp.server import Server  # type: ignore
	from mcp import tool  # type: ignore
except Exception:
	try:
		from modelcontextprotocol import Server, tool  # type: ignore
	except Exception:
		class Server:  # type: ignore
			def __init__(self, name: str) -> None:
				self.name = name
			def run(self) -> None:
				print("[WARN] MCP packages not installed; running shim server (no real MCP).")
		def tool(*args, **kwargs):  # type: ignore
			def decorator(func):
				return func
			return decorator

from .render import ASPECT_RATIO, RenderOptions, render_markdown_text_to_image
from .store import ImageStore


server = Server("word2img-mcp")
_store = ImageStore()


@tool(name="submit_markdown", description="接收Markdown文本并生成3:4 JPG图片，返回任务ID")
def submit_markdown(markdown_text: str, align: str = "center", bold: bool = False, width: int = 1200) -> str:
	height = int(width * ASPECT_RATIO[1] / ASPECT_RATIO[0])
	options = RenderOptions(width=width, height=height, align=align, bold=bold)
	img = render_markdown_text_to_image(markdown_text, options)
	task_id = _store.save_image(img)
	return task_id


@tool(name="get_image", description="根据任务ID返回图片。可选base64返回或文件路径")
def get_image(task_id: str, as_base64: bool = True) -> str:
	path = _store.get_path(task_id)
	if not path or not os.path.exists(path):
		raise ValueError("任务ID无效或图片不存在")
	if not as_base64:
		return path
	with open(path, "rb") as f:
		b = f.read()
	return base64.b64encode(b).decode("utf-8")


def run_server() -> None:
	server.run()
