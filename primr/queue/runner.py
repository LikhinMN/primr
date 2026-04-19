import threading
import queue
from .task import Task


class TaskQueue:
	def __init__(self):
		self.tasks: list[Task] = []
		self.lock = threading.Lock()
		self._queue = queue.Queue()

	def add_task(self, step: str, depends_on: list = []) -> Task:
		task = Task(step=step, depends_on=list(depends_on))
		with self.lock:
			self.tasks.append(task)
		return task

	def update_task(self, task_id: str, **kwargs):
		with self.lock:
			for task in self.tasks:
				if task.id == task_id:
					for field, value in kwargs.items():
						if hasattr(task, field):
							setattr(task, field, value)
					return

	def get_pending(self) -> list[Task]:
		with self.lock:
			status_by_id = {task.id: task.status for task in self.tasks}
			return [
				task
				for task in self.tasks
				if task.status == "pending"
				and all(status_by_id.get(dep_id) == "done" for dep_id in task.depends_on)
			]

	def get_all(self) -> list[Task]:
		with self.lock:
			return list(self.tasks)

	def clear(self):
		with self.lock:
			self.tasks.clear()


task_queue = TaskQueue()
