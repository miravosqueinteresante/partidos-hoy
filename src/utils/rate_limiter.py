import time
import threading


class RateLimiter:
    def __init__(self, max_per_minute: int = 10):
        self.max_per_minute = max_per_minute
        self.timestamps: list[float] = []
        self.lock = threading.Lock()

    def wait_if_needed(self):
        with self.lock:
            now = time.time()
            cutoff = now - 60.0
            self.timestamps = [t for t in self.timestamps if t > cutoff]
            if len(self.timestamps) >= self.max_per_minute:
                sleep_time = self.timestamps[0] + 60.0 - now
                if sleep_time > 0:
                    time.sleep(sleep_time)
            self.timestamps.append(time.time())
