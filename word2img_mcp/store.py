import os
import uuid
from typing import Dict, Optional

from PIL import Image


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
