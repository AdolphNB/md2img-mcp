import os
from dataclasses import dataclass
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

ASPECT_RATIO = (3, 4)
DEFAULT_WIDTH = 1080
DEFAULT_HEIGHT = 1440
DEFAULT_BG = (255, 255, 255)
DEFAULT_TEXT_COLOR = (20, 20, 20)

SIDE_MARGIN_RATIO = 0.06
TOP_BOTTOM_MARGIN_RATIO = 0.06
LINE_SPACING_RATIO = 0.35
MAX_LINE_WIDTH_RATIO = 1.0 - (SIDE_MARGIN_RATIO * 2)

FONT_CANDIDATES = [
	"C:\\Windows\\Fonts\\msyh.ttc",  # 微软雅黑
	"C:\\Windows\\Fonts\\msyhbd.ttc",  # 微软雅黑粗体
	"C:\\Windows\\Fonts\\simhei.ttf",  # 黑体
	"C:\\Windows\\Fonts\\simsun.ttc",  # 宋体
	"C:\\Windows\\Fonts\\simkai.ttf",  # 楷体
	"C:\\Windows\\Fonts\\simfang.ttf",  # 仿宋
	"C:\\Windows\\Fonts\\STXIHEI.TTF",  # 华文细黑
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
	align: str = "center"
	max_font_size: int = 400
	min_font_size: int = 200
	bold: bool = False


def load_font(preferred_size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
	for path in FONT_CANDIDATES:
		if os.path.exists(path):
			try:
				return ImageFont.truetype(path, preferred_size)
			except Exception:
				continue
	try:
		return ImageFont.load_default(size=preferred_size)
	except:
		return ImageFont.load_default()


def _measure_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
	try:
		bbox = draw.textbbox((0, 0), text, font=font)
		return bbox[2] - bbox[0], bbox[3] - bbox[1]
	except Exception:
		bbox = font.getbbox(text)
		return bbox[2] - bbox[0], bbox[3] - bbox[1]


def measure_wrapped_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int):
	lines = []
	current = ""
	for ch in text.replace('\r', ''):
		if ch == '\n':
			lines.append(current)
			current = ""
			continue
		probe = current + ch
		w, _ = _measure_text(draw, probe, font)
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
		w, _ = _measure_text(draw, ln, font)
		max_line_w = max(max_line_w, w)
	return "\n".join(lines), max_line_w, line_h, len(lines)


def auto_fit_font_size(text: str, options: RenderOptions):
	img = Image.new("RGB", (options.width, options.height), options.background)
	draw = ImageDraw.Draw(img)
	for size in range(options.max_font_size, options.min_font_size - 1, -4):
		font = load_font(size, options.bold)
		wrapped, max_w, line_h, num_lines = measure_wrapped_text(
			draw, text, font, int(options.width * (1 - 2 * SIDE_MARGIN_RATIO))
		)
		line_spacing = int(size * LINE_SPACING_RATIO)
		total_text_h = num_lines * line_h + (num_lines - 1) * line_spacing
		if max_w <= int(options.width * (1 - 2 * SIDE_MARGIN_RATIO)) and total_text_h <= int(options.height * (1 - 2 * TOP_BOTTOM_MARGIN_RATIO)):
			return font, wrapped, max_w, line_h, num_lines, line_spacing
	font = load_font(options.min_font_size, options.bold)
	wrapped, max_w, line_h, num_lines = measure_wrapped_text(
		draw, text, font, int(options.width * (1 - 2 * SIDE_MARGIN_RATIO))
	)
	line_spacing = int(options.min_font_size * LINE_SPACING_RATIO)
	return font, wrapped, max_w, line_h, num_lines, line_spacing


def render_markdown_text_to_image(md_text: str, options: Optional[RenderOptions] = None) -> Image.Image:
	if options is None:
		options = RenderOptions()
	font, wrapped, max_w, line_h, num_lines, line_spacing = auto_fit_font_size(md_text, options)
	img = Image.new("RGB", (options.width, options.height), options.background)
	draw = ImageDraw.Draw(img)
	total_text_h = num_lines * line_h + (num_lines - 1) * line_spacing
	start_y = (options.height - total_text_h) // 2
	x_left = int(options.width * SIDE_MARGIN_RATIO)
	for i, ln in enumerate(wrapped.split('\n')):
		w, _ = _measure_text(draw, ln, font)
		if options.align == "center":
			x = (options.width - w) // 2
		else:
			x = x_left
		y = start_y + i * (line_h + line_spacing)
		draw.text((x, y), ln, fill=options.text_color, font=font)
	return img
