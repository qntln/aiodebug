import pytest
import statistics
import time

from aiodebug.testing import time_dilated_loop



def test_DilationMeter_set_subjective_time():
	meter = time_dilated_loop.DilationMeter()
	meter.set_subjective_time(123)
	assert meter.dilation == 1
	dilations = []
	for i in range(1, 11):
		time.sleep(0.2)
		meter.set_subjective_time(123 + i * 0.4)
		dilations.append(meter.dilation)
	assert statistics.mean(dilations) == pytest.approx(2, rel = 0.1)


def test_TimeDilatedLoop_time():
	loop = time_dilated_loop.TimeDilatedLoop()
	loop.time_dilation = 2
	deltas = []
	for _ in range(10):
		t0 = loop.time()
		time.sleep(0.2)
		deltas.append(loop.time() - t0)
	assert statistics.mean(deltas) == pytest.approx(0.4, rel = 0.1)
