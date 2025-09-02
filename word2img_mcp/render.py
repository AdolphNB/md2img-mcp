import os
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

ASPECT_RATIO = (3, 4)
DEFAULT_WIDTH = 1080
DEFAULT_HEIGHT = 1440
DEFAULT_BG = (255, 255, 255)
DEFAULT_TEXT_COLOR = (20, 20, 20)

SIDE_MARGIN_RATIO = 0.08
TOP_BOTTOM_MARGIN_RATIO = 0.08
LINE_SPACING_RATIO = 0.5
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
	max_font_size: int = 80
	min_font_size: int = 40
	bold: bool = False


def load_font(preferred_size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
	# 如果需要粗体，优先尝试粗体字体文件
	if bold:
		bold_candidates = [
			"C:\\Windows\\Fonts\\msyhbd.ttc",  # 微软雅黑粗体
			"C:\\Windows\\Fonts\\simhei.ttf",  # 黑体（本身较粗）
		]
		for path in bold_candidates:
			if os.path.exists(path):
				try:
					return ImageFont.truetype(path, preferred_size)
				except Exception:
					continue
	
	# 常规字体
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


@dataclass
class TextSegment:
	text: str
	is_bold: bool = False
	is_header: bool = False
	header_level: int = 0


def parse_markdown(md_text: str) -> List[TextSegment]:
	"""简单的 Markdown 解析，支持标题和加粗"""
	segments = []
	lines = md_text.split('\n')
	
	for line in lines:
		line = line.strip()
		if not line:
			continue
			
		# 处理标题
		if line.startswith('#'):
			header_match = re.match(r'^(#{1,6})\s*(.*)', line)
			if header_match:
				level = len(header_match.group(1))
				text = header_match.group(2)
				segments.append(TextSegment(text, is_header=True, header_level=level))
				continue
		
		# 处理加粗文本 - 改进版本
		parts = re.split(r'(\*\*[^*]+\*\*)', line)
		for part in parts:
			if part.startswith('**') and part.endswith('**') and len(part) > 4:
				# 去掉 ** 标记，设置为加粗
				bold_text = part[2:-2]
				if bold_text.strip():
					segments.append(TextSegment(bold_text, is_bold=True))
			elif part.strip():
				segments.append(TextSegment(part))
	
	return segments


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
	for size in range(options.max_font_size, options.min_font_size - 1, -2):
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
	
	# 解析 Markdown
	segments = parse_markdown(md_text)
	
	img = Image.new("RGB", (options.width, options.height), options.background)
	draw = ImageDraw.Draw(img)
	
	# 计算基础字体大小
	base_font_size = options.min_font_size + (options.max_font_size - options.min_font_size) // 2
	
	y_offset = int(options.height * TOP_BOTTOM_MARGIN_RATIO)
	x_left = int(options.width * SIDE_MARGIN_RATIO)
	max_width = int(options.width * (1 - 2 * SIDE_MARGIN_RATIO))
	
	for segment in segments:
		# 根据段落类型确定字体大小和样式
		if segment.is_header:
			font_size = min(base_font_size + (4 - segment.header_level) * 8, options.max_font_size)
			is_bold = True
		elif segment.is_bold:
			font_size = base_font_size
			is_bold = True
		else:
			font_size = base_font_size
			is_bold = False
		
		# 加载字体
		font = load_font(font_size, is_bold)
		
		# 文字换行处理 - 支持中文字符换行
		wrapped_lines = []
		current_line = ""
		
		for char in segment.text:
			test_line = current_line + char
			w, _ = _measure_text(draw, test_line, font)
			if w <= max_width:
				current_line = test_line
			else:
				if current_line:
					wrapped_lines.append(current_line)
					current_line = char
				else:
					# 单个字符就超宽，强制添加
					wrapped_lines.append(char)
					current_line = ""
		if current_line:
			wrapped_lines.append(current_line)
		
		# 绘制文本 - 修复居中逻辑
		line_height = font.getbbox("Hg")[3] - font.getbbox("Hg")[1]
		line_spacing = int(font_size * 0.3)
		
		if options.align == "center":
    			# 计算整个文本块的宽度，以此居中整个段落
			max_line_width = max(_measure_text(draw, line, font)[0] for line in wrapped_lines) if wrapped_lines else 0
			block_x = (options.width - max_line_width) // 2
			
			for line in wrapped_lines:
				# 每行在段落内左对齐，但整个段落居中
				draw.text((block_x, y_offset), line, fill=options.text_color, font=font)
				y_offset += line_height + line_spacing
		else:
			# 左对齐
			for line in wrapped_lines:
				draw.text((x_left, y_offset), line, fill=options.text_color, font=font)
				y_offset += line_height + line_spacing
		
		# 段落间距
		y_offset += int(font_size * 0.4)
	
	return img
