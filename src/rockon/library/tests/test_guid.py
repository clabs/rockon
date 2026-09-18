from __future__ import annotations

import string
from unittest.mock import patch

from django.test import SimpleTestCase

from rockon.library.guid import base62_encode, guid


class Base62EncodeTests(SimpleTestCase):
    def test_zero_encodes_to_empty_string(self):
        self.assertEqual(base62_encode(0), '')

    def test_single_digit_values(self):
        self.assertEqual(base62_encode(1), '1')
        self.assertEqual(base62_encode(9), '9')

    def test_values_above_nine_use_letters(self):
        chars = string.digits + string.ascii_letters
        self.assertEqual(base62_encode(10), chars[10])
        self.assertEqual(base62_encode(61), chars[61])

    def test_round_trips_through_base62(self):
        chars = string.digits + string.ascii_letters
        encoded = base62_encode(12345)
        decoded = 0
        for char in encoded:
            decoded = decoded * 62 + chars.index(char)
        self.assertEqual(decoded, 12345)


class GuidTests(SimpleTestCase):
    # guid() rejection-samples a random number below 62**length, so the
    # base62-encoded result has *up to* `length` characters, not exactly
    # `length` (e.g. num=0 encodes to ''). Only the upper bound is guaranteed.

    def test_default_length_is_at_most_fifteen(self):
        self.assertLessEqual(len(guid()), 15)

    def test_respects_custom_length_as_an_upper_bound(self):
        self.assertLessEqual(len(guid(length=8)), 8)

    def test_uses_only_base62_characters(self):
        allowed = set(string.digits + string.ascii_letters)
        value = guid(length=64)
        self.assertTrue(set(value) <= allowed)

    def test_generates_distinct_values(self):
        values = {guid() for _ in range(50)}
        self.assertEqual(len(values), 50)

    @patch('rockon.library.guid.token_bytes')
    def test_retries_when_sampled_number_is_out_of_range(self, token_bytes):
        # First draw is >= 62**2 (out of range for length=2), second is in range.
        token_bytes.side_effect = [bytes([255, 255]), bytes([1, 0])]
        self.assertEqual(guid(length=2), base62_encode(1))
        self.assertEqual(token_bytes.call_count, 2)
