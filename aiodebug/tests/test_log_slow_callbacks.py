import asyncio
from unittest import mock
import time

import aiodebug.log_slow_callbacks



@mock.patch('aiodebug.logging_compat.get_logger')
def test_slow_callback_causes_a_warning(get_logger):
	logger = mock.Mock()
	get_logger.return_value = logger

	loop = asyncio.get_event_loop()
	aiodebug.log_slow_callbacks.enable(0.04)

	async def slowcb():
		time.sleep(0.05)

	loop.run_until_complete(slowcb())

	assert logger.warning.call_count == 1
	args, _kw = logger.warning.call_args
	assert args[0] == 'Executing %s took %.3f seconds'
	assert 'slowcb()' in args[1]
	assert args[2] >= 0.05


@mock.patch('aiodebug.logging_compat.get_logger')
def test_waiting_callback_does_not_cause_warning(get_logger):
	logger = mock.Mock()
	get_logger.return_value = logger

	loop = asyncio.get_event_loop()
	aiodebug.log_slow_callbacks.enable(0.02)

	async def waitingcb():
		await asyncio.sleep(0.05)

	loop.run_until_complete(waitingcb())

	assert logger.warning.call_count == 0
