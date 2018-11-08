# created by Sami Bosch on Thursday, 08 November 2018

import asyncio


class AsyncTimer:
    """Used to put timers on async functions."""
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback()

    def cancel(self):
        self._task.cancel()
