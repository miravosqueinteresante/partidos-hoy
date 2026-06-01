import time
from src.utils.rate_limiter import RateLimiter


def test_rate_limiter_enforces_limit():
    limiter = RateLimiter(max_per_minute=60)
    start = time.time()
    for _ in range(60):
        limiter.wait_if_needed()
    elapsed = time.time() - start
    assert elapsed < 2.0


def test_rate_limiter_slows_down():
    limiter = RateLimiter(max_per_minute=2)
    start = time.time()
    for _ in range(4):
        limiter.wait_if_needed()
    elapsed = time.time() - start
    assert elapsed >= 60.0
