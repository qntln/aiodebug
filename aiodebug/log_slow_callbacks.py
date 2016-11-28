import asyncio.events
from asyncio.base_events import _format_handle
import time



def enable(slow_duration: float) -> None:
	'''
	Patch ``asyncio.events.Handle`` to log warnings every time a callback takes ``slow_duration`` seconds
	or more to run.
	'''
	from aiodebug.logging_compat import get_logger
	logger = get_logger(__name__)
	_run = asyncio.events.Handle._run

	def instrumented(self):
		t0 = time.monotonic()
		retval = _run(self)
		dt = time.monotonic() - t0
		if dt >= slow_duration:
			logger.warning('Executing %s took %.3f seconds', _format_handle(self), dt)
		return retval

	asyncio.events.Handle._run = instrumented
