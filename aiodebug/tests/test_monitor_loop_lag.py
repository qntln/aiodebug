import asyncio
from unittest import mock
import pytest
import statistics
import time

from aiodebug import monitor_loop_lag



@pytest.mark.asyncio
async def test_no_delays():
	statsd = mock.Mock()
	monitor_loop_lag.enable(statsd, interval = 0.2)
	await asyncio.sleep(1.5)
	assert statsd.timing.call_count == 7
	lags = [ args[1] for (args, _) in statsd.timing.call_args_list ]
	assert 0 < statistics.mean(lags) < 5 # milliseconds


@pytest.mark.asyncio
async def test_long_delay():
	statsd = mock.Mock()
	monitor_loop_lag.enable(statsd, interval = 0.2)
	await asyncio.sleep(0.15)
	time.sleep(0.1)
	await asyncio.sleep(0.01)
	assert statsd.timing.call_count == 1
	lag = statsd.timing.call_args[0][1]
	assert 50 < lag < 70 # milliseconds
