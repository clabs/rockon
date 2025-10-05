from __future__ import annotations

import string
from math import ceil, log
from os import urandom


def guid(length: int = 15) -> str:
    """
    Generate a random string of length `length` using base62 encoding.

    - length: int - the length of the string to generate
    """
    # We generate a random number in a space at least as big as 62^length,
    # and if it's too big, we just retry. This is still statistically O(1)
    # since repeated probabilities less than one converge to zero. Hat-tip to
    # a Google interview for teaching me this technique! ;)
    max_num = 62**length
    num_bytes = ceil(log(max_num) / log(256))

    while True:
        bytes = urandom(num_bytes)
        num = 0
        for i in range(len(bytes)):
            num += 256**i * bytes[i]
        if num < max_num:
            return base62_encode(num)


def base62_encode(num) -> str:
    chars = string.digits + string.ascii_letters
    encoded = []
    while num > 0:
        num, remainder = divmod(num, 62)
        encoded.insert(0, chars[remainder])
    return ''.join(encoded)
