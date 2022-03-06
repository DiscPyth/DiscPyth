from ..constants import BACKEND

if BACKEND == "anyio":
    from anyio import Event, Lock
else:
    from curio import Event, Lock


class Bucket:
    lock: Lock

    def __init__(self, lock: Lock) -> None:
        self.lock = lock
        self.deferred = False

    async def __aenter__(self) -> Lock:
        self.lock.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.deferred:
            return
        await self.release()

    def defer(self) -> None:
        if not self.deferred:
            self.deferred = True

    async def release(self) -> None:
        await self.lock.release()


class Route:
    method: str
    url: str
    _bucket_id: str

    def __init__(self, method: str, url: str) -> None:
        self.method = method
        self._bucket_id = url.split("?", 1)[0]
        self.url = url

    @property
    def bucket_id(self) -> str:
        return self._bucket_id


class BucketManager:
    buckets: dict[str, Bucket]
    global_limiter: Event

    def __init__(self) -> None:
        self.global_limiter = Event()
        self.global_limiter.set()

    def get(self, key: str) -> Bucket:
        try:
            bucket = self.buckets[key]
        except KeyError:
            bucket = self.buckets[key] = Bucket(Lock())
        return bucket

    @property
    def is_global(self) -> bool:
        return not self.global_limiter.is_set()

    async def wait(self) -> None:
        await self.global_limiter.wait()
