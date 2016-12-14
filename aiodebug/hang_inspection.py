from typing import List, Optional
import sys
import traceback
import asyncio
import time
import os
import threading
import datetime

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter




class TraceDumper(threading.Thread):

	def __init__(self, dir_name: str, interval: float, last_loop_iteration_time: List[float], lock: threading.Lock) -> None:
		self.interval = interval
		self.dir_name = os.path.abspath(dir_name)
		assert os.path.isdir(self.dir_name)
		self.last_loop_iteration_time = last_loop_iteration_time
		self.lock = lock
		self.stop = False
		self.monitor_task = None  # type: Optional[asyncio.Task]
		threading.Thread.__init__(self)


	def run(self) -> None:
		while not self.stop:
			with self.lock:
				if time.monotonic() - self.last_loop_iteration_time[0] > self.interval:
					for i in range(3):
						dt = datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
						self.save_stack_trace('stacktrace-{datetime}-{i}.html'.format(datetime = dt, i = i))
						time.sleep(1)

			time.sleep(self.interval)


	@staticmethod
	def _get_stack_trace() -> str:
		code = []  # type: List[str]
		for threadId, stack in sys._current_frames().items():
			code.append("\n# ThreadID: %s" % threadId)
			for filename, line_no, name, line in traceback.extract_stack(stack):
				code.append('File: "%s", line %d, in %s' % (filename, line_no, name))
				if line:
					code.append("  %s" % (line.strip()))

		return highlight("\n".join(code), PythonLexer(), HtmlFormatter(
			full=False,
			noclasses=True,
		))


	def save_stack_trace(self, filename: str = 'stacktrace.html') -> None:
		with open(os.path.join(self.dir_name, filename), "wb+") as file:
			file.write(self._get_stack_trace().encode('utf-8'))

		
def enable(stack_output_dir: str, interval: float = 0.25, loop: asyncio.AbstractEventLoop = None) -> TraceDumper:
	'''
	Start detecting hangs in asyncio loop. If a hang for more than `interval` is detected, a stack trace is saved into
	`stack_output_dir`.
	'''
	if loop is None:
		loop = asyncio.get_event_loop()

	last_loop_iteration_time = [time.monotonic()]
	lock = threading.Lock()

	tracer = TraceDumper(stack_output_dir, interval, last_loop_iteration_time, lock)
	tracer.setDaemon(True)

	async def monitor():
		while loop.is_running():
			with lock:
				last_loop_iteration_time[0] = time.monotonic()
			await asyncio.sleep(interval / 2.)

	tracer.monitor_task = loop.create_task(monitor())
	tracer.start()

	return tracer


def disable(instance: TraceDumper) -> None:
	'''Stop detecting hangs'''
	instance.stop = True
	if instance.monitor_task:
		instance.monitor_task.cancel()
