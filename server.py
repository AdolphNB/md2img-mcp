import base64
import io
import os
import uuid
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

# MCP server
try:
	from modelcontextprotocol import Server, tool
except ImportError:
	# Allow running limited rendering without MCP runtime during dev
	Server = None
	def tool(*args, **kwargs):
		def decorator(func):
			return func
		return decorator

# ---------- Rendering Engine ----------

ASPECT_RATIO = (3, 4)
DEFAULT_WIDTH = 1200  # 3:4 => 1200x1600
DEFAULT_HEIGHT = int(DEFAULT_WIDTH * ASPECT_RATIO[1] / ASPECT_RATIO[0])
DEFAULT_BG = (255, 255, 255)
DEFAULT_TEXT_COLOR = (20, 20, 20)

# Margins and layout
SIDE_MARGIN_RATIO = 0.08  # 8% of width as horizontal padding
TOP_BOTTOM_MARGIN_RATIO = 0.08  # 8% of height
LINE_SPACING_RATIO = 0.38  # relative to font size
MAX_LINE_WIDTH_RATIO = 1.0 - (SIDE_MARGIN_RATIO * 2)

# Font fallbacks
FONT_CANDIDATES = [
	"C:\\Windows\\Fonts\\msyh.ttc",  # 微软雅黑
	"C:\\Windows\\Fonts\\simhei.ttf",  # 黑体
	"C:\\Windows\\Fonts\\simfang.ttf",  # 仿宋
	"/System/Library/Fonts/PingFang.ttc",
	"/System/Library/Fonts/STHeiti Light.ttc",
	"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

@dataclass
class RenderOptions:
	width: int = DEFAULT_WIDTH
	height: int = DEFAULT_HEIGHT
	background: Tuple[int, int, int] = DEFAULT_BG
	text_color: Tuple[int, int, int] = DEFAULT_TEXT_COLOR
	align: str = "center"  # 'left' | 'center'
	max_font_size: int = 72
	min_font_size: int = 24
	bold: bool = False


def load_font(preferred_size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
	# Pillow loads TTF/OTF; we try candidates
	for path in FONT_CANDIDATES:
		if os.path.exists(path):
			try:
				return ImageFont.truetype(path, preferred_size, layout_engine=ImageFont.LAYOUT_BASIC)
			except Exception:
				continue
	# Fallback to default
	return ImageFont.load_default()


def measure_wrapped_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> Tuple[str, int, int, int]:
	# Greedy wrap by words/characters respecting CJK
	lines = []
	current = ""
	for ch in text.replace('\r', ''):
		if ch == '\n':
			lines.append(current)
			current = ""
			continue
		probe = current + ch
		w, _ = draw.textsize(probe, font=font)
		if w <= max_width:
			current = probe
		else:
			if current:
				lines.append(current)
				current = ch
			else:
				lines.append(probe)
				current = ""
	if current:
		lines.append(current)

	max_line_w = 0
	line_h = font.getbbox("Hg")[3] - font.getbbox("Hg")[1]
	for ln in lines:
		w, _ = draw.textsize(ln, font=font)
		max_line_w = max(max_line_w, w)
	return "\n".join(lines), max_line_w, line_h, len(lines)


def auto_fit_font_size(text: str, options: RenderOptions) -> Tuple[ImageFont.ImageFont, str, int, int, int, int]:
	img = Image.new("RGB", (options.width, options.height), options.background)
	draw = ImageDraw.Draw(img)
	usable_width = int(options.width * MAX_LINE_WIDTH_RATIO)
	usable_width -= int(options.width * (1 - MAX_LINE_WIDTH_RATIO))  # ensure padding respected

	for size in range(options.max_font_size, options.min_font_size - 1, -2):
		font = load_font(size, options.bold)
		wrapped, max_w, line_h, num_lines = measure_wrapped_text(draw, text, font, int(options.width * (1 - 2 * SIDE_MARGIN_RATIO)))
		line_spacing = int(size * LINE_SPACING_RATIO)
		total_text_h = num_lines * line_h + (num_lines - 1) * line_spacing
		if max_w <= int(options.width * (1 - 2 * SIDE_MARGIN_RATIO)) and total_text_h <= int(options.height * (1 - 2 * TOP_BOTTOM_MARGIN_RATIO)):
			return font, wrapped, max_w, line_h, num_lines, line_spacing

	# Fallback to min font
	font = load_font(options.min_font_size, options.bold)
	wrapped, max_w, line_h, num_lines = measure_wrapped_text(draw, text, font, int(options.width * (1 - 2 * SIDE_MARGIN_RATIO)))
	line_spacing = int(options.min_font_size * LINE_SPACING_RATIO)
	return font, wrapped, max_w, line_h, num_lines, line_spacing


def render_markdown_text_to_image(md_text: str, options: Optional[RenderOptions] = None) -> Image.Image:
	# 简化渲染：将Markdown当作纯文本排版。加粗/居中通过选项控制。
	if options is None:
		options = RenderOptions()

	font, wrapped, max_w, line_h, num_lines, line_spacing = auto_fit_font_size(md_text, options)
	img = Image.new("RGB", (options.width, options.height), options.background)
	draw = ImageDraw.Draw(img)

	# Determine starting y for vertical centering
	total_text_h = num_lines * line_h + (num_lines - 1) * line_spacing
	start_y = (options.height - total_text_h) // 2

	# Draw lines with horizontal alignment
	x_left = int(options.width * SIDE_MARGIN_RATIO)
	for i, ln in enumerate(wrapped.split('\n')):
		w, _ = draw.textsize(ln, font=font)
		if options.align == "center":
			x = (options.width - w) // 2
		else:
			x = x_left
		y = start_y + i * (line_h + line_spacing)
		draw.text((x, y), ln, fill=options.text_color, font=font)

	return img


# ---------- Simple Task Store ----------

class ImageStore:
	def __init__(self) -> None:
		self._tasks: Dict[str, str] = {}

	def save_image(self, image: Image.Image) -> str:
		os.makedirs("outputs", exist_ok=True)
		task_id = str(uuid.uuid4())
		path = os.path.join("outputs", f"{task_id}.jpg")
		image.save(path, format="JPEG", quality=95, subsampling=0, optimize=True)
		self._tasks[task_id] = path
		return task_id

	def get_path(self, task_id: str) -> Optional[str]:
		return self._tasks.get(task_id)


store = ImageStore()


# ---------- MCP Tools ----------

server = Server("word2img-mcp") if Server else None


@tool(name="submit_markdown", description="接收Markdown文本并生成3:4 JPG图片，返回任务ID")
def submit_markdown(markdown_text: str, align: str = "center", bold: bool = False, width: int = DEFAULT_WIDTH) -> str:
	height = int(width * ASPECT_RATIO[1] / ASPECT_RATIO[0])
	options = RenderOptions(width=width, height=height, align=align, bold=bold)
	img = render_markdown_text_to_image(markdown_text, options)
	task_id = store.save_image(img)
	return task_id


@tool(name="get_image", description="根据任务ID返回图片。可选base64返回或文件路径")
def get_image(task_id: str, as_base64: bool = True) -> str:
	path = store.get_path(task_id)
	if not path or not os.path.exists(path):
		raise ValueError("任务ID无效或图片不存在")
	if not as_base64:
		return path
	with open(path, "rb") as f:
		b = f.read()
	return base64.b64encode(b).decode("utf-8")


if __name__ == "__main__":
	# 允许独立运行进行本地调试
	text = "# 标题\n**加粗** 与 普通文本\n长段内容会自动换行并居中显示。"
	img = render_markdown_text_to_image(text, RenderOptions(align="center", bold=False))
	os.makedirs("outputs", exist_ok=True)
	img.save("outputs/_sample.jpg", format="JPEG", quality=95, subsampling=0, optimize=True)
	print("Sample saved to outputs/_sample.jpg")
	if server:
		server.run()
