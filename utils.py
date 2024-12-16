"""
"""
import logging
import time

from config import HEX_DIGITS

logging.basicConfig(level=logging.INFO)


def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logging.info(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
        return result
    return wrapper


# Convert a number from 0 to 255 to a pair of hex digits - used in calculating RGB colour values
def hex(n):
    n = min(int(n), 255)
    d1 = HEX_DIGITS[n // 16]
    d2 = HEX_DIGITS[n % 16]
    return d1 + d2
