import asyncio
import time
import os.path

import pytest

import aiodebug.hang_inspection


def test_get_stack_trace():
    stacktrace = aiodebug.hang_inspection.TraceDumper._get_stack_trace()
    assert len(stacktrace) > 10000
    assert 'test_get_stack_trace' in stacktrace


@pytest.mark.asyncio
async def test_hang_inspection(tmpdir):
    output = str(tmpdir.join("output.html"))
    print('You can inspect the stack trace manually in', output)
    instance = aiodebug.hang_inspection.enable(output)
    loop = asyncio.get_event_loop()

    async def hang_now():
        time.sleep(1)

    loop.create_task(hang_now())
    await asyncio.sleep(1)
    assert os.path.isfile(output)
    aiodebug.hang_inspection.disable(instance)


@pytest.mark.asyncio
async def test_hang_inspection_false_positive(tmpdir):
    output = str(tmpdir.join("output.html"))
    instance = aiodebug.hang_inspection.enable(output)
    await asyncio.sleep(1)
    assert not os.path.isfile(output)
    aiodebug.hang_inspection.disable(instance)
