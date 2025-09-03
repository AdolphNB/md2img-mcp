import base64
import hashlib
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, Any

from PIL import Image


class ImageStore:
	"""Image storage manager with task management, statistics, and detailed error handling."""
	
	def __init__(self, base_dir: Optional[str] = None) -> None:
		self.base_dir = base_dir or os.path.join(os.getcwd(), "outputs")
		os.makedirs(self.base_dir, exist_ok=True)
		self._tasks_file = os.path.join(self.base_dir, "tasks.json")
		self._tasks: Dict[str, Dict] = {}
		self._load_tasks()
	
	def _load_tasks(self) -> None:
		"""Load tasks from JSON file."""
		if os.path.exists(self._tasks_file):
			try:
				with open(self._tasks_file, "r", encoding="utf-8") as f:
					self._tasks = json.load(f)
			except (json.JSONDecodeError, FileNotFoundError):
				self._tasks = {}
		else:
			self._tasks = {}
	
	def _save_tasks(self) -> None:
		"""Save tasks to JSON file."""
		try:
			with open(self._tasks_file, "w", encoding="utf-8") as f:
				json.dump(self._tasks, f, ensure_ascii=False, indent=2)
		except Exception as e:
			raise ValueError(f"Failed to save tasks: {str(e)}") from e
	
	def save_image(self, image: Image.Image, format: str = "jpg", options: Optional[Dict] = None) -> str:
		"""Save image with detailed metadata and return task ID."""
		try:
			task_id = str(uuid.uuid4())
			filename = f"{task_id}.{format}"
			path = os.path.join(self.base_dir, filename)
			
			# Save image with quality settings
			if format.lower() in ["jpg", "jpeg"]:
				image.save(path, format=format.upper(), quality=95, subsampling=0, optimize=True)
			else:
				image.save(path, format=format.upper())
			
			# Get file size
			file_size = os.path.getsize(path)
			
			# Save metadata
			created_at = datetime.now().isoformat()
			metadata = {
				"task_id": task_id,
				"created_at": created_at,
				"format": format,
				"file_size": file_size,
				"status": "completed",
				"options": options or {},
				"image_size": f"{image.width}x{image.height}",
				"mode": image.mode
			}
			
			metadata_file = os.path.join(self.base_dir, f"{task_id}.json")
			with open(metadata_file, "w", encoding="utf-8") as f:
				json.dump(metadata, f, ensure_ascii=False, indent=2)
			
			# Update tasks registry
			self._tasks[task_id] = {
				"task_id": task_id,
				"created_at": created_at,
				"status": "completed",
				"format": format,
				"file_size": file_size,
				"has_metadata": True,
				"path": path
			}
			self._save_tasks()
			
			return task_id
			
		except Exception as e:
			error_details = {
				"error": str(e),
				"error_type": type(e).__name__,
				"operation": "save_image",
				"format": format
			}
			raise ValueError(f"Failed to save image: {json.dumps(error_details, ensure_ascii=False)}") from e
	
	def get_path(self, task_id: str) -> Optional[str]:
		"""Get file path for task ID with validation."""
		try:
			if task_id not in self._tasks:
				return None
			
			path = self._tasks[task_id].get("path")
			if path and os.path.exists(path):
				return path
			
			# Fallback: search for file with task_id
			for ext in ["png", "jpg", "jpeg", "webp"]:
				path = os.path.join(self.base_dir, f"{task_id}.{ext}")
				if os.path.exists(path):
					# Update task record
					self._tasks[task_id]["path"] = path
					self._save_tasks()
					return path
			
			return None
			
		except Exception as e:
			error_details = {
				"error": str(e),
				"error_type": type(e).__name__,
				"operation": "get_path",
				"task_id": task_id
			}
			raise ValueError(f"Failed to get image path: {json.dumps(error_details, ensure_ascii=False)}") from e
	
	def get_task_metadata(self, task_id: str) -> Optional[Dict]:
		"""Get detailed task metadata."""
		try:
			metadata_file = os.path.join(self.base_dir, f"{task_id}.json")
			if os.path.exists(metadata_file):
				with open(metadata_file, "r", encoding="utf-8") as f:
					return json.load(f)
			return None
			
		except Exception as e:
			error_details = {
				"error": str(e),
				"error_type": type(e).__name__,
				"operation": "get_task_metadata",
				"task_id": task_id
			}
			raise ValueError(f"Failed to get task metadata: {json.dumps(error_details, ensure_ascii=False)}") from e
	
	def list_tasks(self, limit: int = 10, status_filter: str = "all") -> List[Dict]:
		"""List tasks with filtering and detailed information."""
		try:
			tasks_list = []
			
			for task_id, task_info in self._tasks.items():
				if status_filter != "all" and task_info.get("status") != status_filter:
					continue
				
				# Add detailed metadata if available
				metadata = self.get_task_metadata(task_id)
				if metadata:
					task_info.update(metadata)
				
				tasks_list.append(task_info)
				
				if len(tasks_list) >= limit:
					break
			
			# Sort by creation time (newest first)
			tasks_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
			
			return tasks_list
			
		except Exception as e:
			error_details = {
				"error": str(e),
				"error_type": type(e).__name__,
				"operation": "list_tasks",
				"limit": limit,
				"status_filter": status_filter
			}
			raise ValueError(f"Failed to list tasks: {json.dumps(error_details, ensure_ascii=False)}") from e
	
	def get_task_statistics(self) -> Dict[str, Any]:
		"""Get comprehensive task statistics."""
		try:
			total = len(self._tasks)
			completed = sum(1 for task in self._tasks.values() if task.get("status") == "completed")
			failed = sum(1 for task in self._tasks.values() if task.get("status") == "failed")
			processing = sum(1 for task in self._tasks.values() if task.get("status") == "processing")
			
			# Calculate total file size and format distribution
			total_size = 0
			formats = {}
			for task in self._tasks.values():
				if "file_size" in task:
					total_size += task["file_size"]
				if "format" in task:
					formats[task["format"]] = formats.get(task["format"], 0) + 1
			
			return {
				"total_tasks": total,
				"completed": completed,
				"failed": failed,
				"processing": processing,
				"total_file_size": total_size,
				"average_file_size": total_size / total if total > 0 else 0,
				"formats": formats,
				"last_updated": datetime.now().isoformat(),
				"storage_directory": self.base_dir
			}
			
		except Exception as e:
			error_details = {
				"error": str(e),
				"error_type": type(e).__name__,
				"operation": "get_task_statistics"
			}
			raise ValueError(f"Failed to get task statistics: {json.dumps(error_details, ensure_ascii=False)}") from e
	
	def cleanup_old_files(self, max_age_hours: int = 24) -> int:
		"""Clean up files older than specified hours with detailed reporting."""
		try:
			now = datetime.now()
			removed_count = 0
			
			for filename in os.listdir(self.base_dir):
				if filename == "tasks.json":
					continue
					
				filepath = os.path.join(self.base_dir, filename)
				if os.path.isfile(filepath):
					file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
					if (now - file_time).total_seconds() > max_age_hours * 3600:
						# Remove from tasks registry
						task_id = os.path.splitext(filename)[0]
						if task_id in self._tasks:
							del self._tasks[task_id]
						
						os.remove(filepath)
						removed_count += 1
			
			if removed_count > 0:
				self._save_tasks()
			
			return removed_count
			
		except Exception as e:
			error_details = {
				"error": str(e),
				"error_type": type(e).__name__,
				"operation": "cleanup_old_files",
				"max_age_hours": max_age_hours
			}
			raise ValueError(f"Failed to cleanup files: {json.dumps(error_details, ensure_ascii=False)}") from e
