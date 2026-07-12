import asyncio
import pytest
import time


@pytest.mark.asyncio
async def test_primary_returned_before_shadow_finished():
    primary_started = asyncio.Event()
    primary_done = asyncio.Event()
    shadow_started = asyncio.Event()
    shadow_done = asyncio.Event()
    events_log = []

    async def primary_worker():
        primary_started.set()
        events_log.append(("primary_start", time.time()))
        await asyncio.sleep(0.05)
        events_log.append(("primary_done", time.time()))
        primary_done.set()
        return "primary_res"

    async def shadow_worker():
        shadow_started.set()
        events_log.append(("shadow_start", time.time()))
        await asyncio.sleep(0.2)
        events_log.append(("shadow_done", time.time()))
        shadow_done.set()
        return "shadow_res"

    primary_task = asyncio.create_task(primary_worker())
    shadow_task = asyncio.create_task(shadow_worker())
    res = await primary_task
    assert res == "primary_res"
    assert primary_done.is_set()
    assert not shadow_done.is_set()
    await shadow_task
    assert shadow_done.is_set()
    log_dict = dict(events_log)
    assert log_dict["primary_done"] < log_dict["shadow_done"]
