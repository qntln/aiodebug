import asyncio



def enable(statsd_client: 'statsd.StatsClient', interval: float = 0.25, loop: asyncio.AbstractEventLoop = None) -> None:
	'''
	Start logging event loop lags to StatsD. In ideal circumstances they should be very close to zero.
	Lags may increase if event loop callbacks block for too long.
	'''
	if loop is None:
		loop = asyncio.get_event_loop()

	async def monitor():
		while loop.is_running():
			t0 = loop.time()
			await asyncio.sleep(interval)
			lag = loop.time() - t0 - interval # Should be close to zero.
			statsd_client.timing('aiodebug.monitor_loop_lag', lag * 1000)

	loop.create_task(monitor())
