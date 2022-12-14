from threading import Thread, Event
from concurrent.futures import Future as ConcurrentFuture
from typing import Any, Optional, Callable
from asyncio import new_event_loop, Future as AIOFuture, run_coroutine_threadsafe
from atexit import register

__all__ = (
    "AsyncWorker",
    "get_single_worker"
)

class AsyncWorker(Thread):
    def __init__(self):
        self._setup_complete_event = Event()

        super().__init__(daemon=True)
        pass

    def run(self):
        self._loop = new_event_loop()
        self._setup_complete_event.set()

        self._loop.run_forever()
        pass

    def run_future(self, 
        future: AIOFuture, 
        blocking: bool=True, 
        completion_callback: Callable[[ConcurrentFuture],None]= None, 
        timeout: Optional[float]=None
        ) -> ConcurrentFuture|Any:
        con_future: ConcurrentFuture = run_coroutine_threadsafe(future, self._loop)
        
        if completion_callback is not None:
            con_future.add_done_callback(completion_callback)
            pass
        
        if blocking: 
            res = con_future.result(timeout)
            return res
            pass
        else:
            return con_future
            pass
        pass

    @property
    def setup_complete(self) -> bool:
        return self._setup_complete_event.is_set()
        pass

    def wait_for_setup_completion(self, timeout: Optional[float]=None):
        self._setup_complete_event.wait()
        pass

    def stop(self):
        self._loop.stop()
        pass
    pass


_SINGLE: AsyncWorker = ...
def get_single_worker():
    global _SINGLE

    if _SINGLE is Ellipsis:
        _SINGLE= AsyncWorker()
        _SINGLE.start()
        _SINGLE.wait_for_setup_completion()
        pass

    return _SINGLE
    pass