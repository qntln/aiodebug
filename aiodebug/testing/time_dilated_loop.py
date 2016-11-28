import asyncio
import time



class DilationMeter:
	'''
	Measure the dilation of "subjective time" set via :meth:`set_subjective_time` compared to
	"objective time" (:func:`time.monotonic`). Read the ``dilation`` attribute to retrieve
	current dilation (dilation == X means that subjective time is running X times faster than objective time).
	'''

	def __init__(self) -> None:
		self._last_objective_time = time.monotonic()
		self._last_subjective_time = None # type: float
		self.dilation = 1.0


	def set_subjective_time(self, subjective_time: float) -> None:
		''' :param subjective_time: Subjective time as a UNIX timestamp. '''
		obj = time.monotonic()
		if self._last_subjective_time is not None:
			dsub = subjective_time - self._last_subjective_time
			dobj = obj - self._last_objective_time
			self.dilation = dsub / dobj
		self._last_subjective_time = subjective_time
		self._last_objective_time = obj



class TimeDilatedLoop(asyncio.get_event_loop().__class__):
	'''
	Internal time in this event loop may run faster or slower than objective time.
	Control loop time dilation vs. objective time by setting the ``time_dilation`` attribute
	(dilation == X means that loop time is running X times faster than objective time).
	'''

	def __init__(self) -> None:
		super().__init__()
		self.time_dilation = 1.0
		self._last_objective_time = None # type: float
		self._last_subjective_time = None # type: float

		_select = self._selector.select
		def select(timeout: float):
			return _select(timeout / self.time_dilation)

		self._selector.select = select


	def time(self) -> float:
		obj = super().time()
		if self._last_objective_time is None:
			self._last_objective_time = self._last_subjective_time = obj
			return obj
		else:
			sub = self._last_subjective_time + (obj - self._last_objective_time) * self.time_dilation
			self._last_subjective_time = sub
			self._last_objective_time = obj
			return sub




if __name__ == '__main__':
	SUBJECTIVE_TIMES = [
		# 100%
		1, 2, 3,
		# 200%
		5, 6, 7,
		# 300%
		10, 13,
		# 100%
		14,
		# 50%
		14.5
	]

	async def stamper():
		prev_obj = time.time()
		while True:
			await asyncio.sleep(1)
			obj = time.time()
			print('Elapsed: 1 subjective second, {:.01f} objective seconds'.format(obj - prev_obj))
			prev_obj = obj


	async def distorter():
		loop = asyncio.get_event_loop()
		meter = DilationMeter()
		for t in SUBJECTIVE_TIMES:
			meter.set_subjective_time(t)
			loop.time_dilation = meter.dilation
			print('\n--- Subjective loop time now runs at {:.0f}% of objective time. ---'.format(100 * meter.dilation))
			await asyncio.sleep(loop.time_dilation) # Sleep 1 objective second


	loop = TimeDilatedLoop()
	asyncio.set_event_loop(loop)

	asyncio.ensure_future(stamper())
	asyncio.ensure_future(distorter())
	loop.run_forever()
