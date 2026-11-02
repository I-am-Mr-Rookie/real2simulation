"""Fused canonical validation must match Meta's strict decode then encode, including bad finalization."""
from array import array
from types import SimpleNamespace

import numpy as np
import pytest

from Build.reconstruction import _sam_mask_codec as codec


def strict_decode(payload, width, height):
    # Original vendored algorithm, deliberately retaining the full canonical round trip.
    decoder = codec._RangeDecoder(codec._unpack(payload[1:]))
    counts = array("H", [1]) * (codec._CONTEXT_COUNT * 2)
    stride = width + 2 * codec._PADDING
    padded = bytearray(stride * (height + codec._PADDING))
    output = bytearray(width * height)
    for y in range(height):
        for x in range(width):
            pos = (y + codec._PADDING) * stride + codec._PADDING + x
            offset = codec._context_at(padded, pos, pos - stride, pos - 2 * stride) << 1
            zero, one = counts[offset:offset + 2]
            bit = int(decoder.frequency(zero + one) >= zero)
            decoder.decode(zero if bit else 0, one if bit else zero)
            padded[pos] = output[y * width + x] = bit
            codec._update_counts(counts, offset, bit)
    if codec._encode_raster(output, width, height) != payload:
        raise ValueError("not canonical")
    return bytes(output)


def outcome(fn, payload, width, height):
    try:
        return fn(payload, width, height)
    except ValueError:
        return None


def fused(payload, width, height):
    return codec.decode_mask_to_raster(SimpleNamespace(
        encoding="one_bit", payload=payload, width=width, height=height))


@pytest.mark.parametrize("width,height", [(1, 1), (1, 23), (29, 1), (17, 19), (128, 96)])
def test_matches_strict_codec_and_preserves_binary_pixels(width, height):
    rng = np.random.default_rng(53)
    for pixels in (np.zeros(width * height, np.uint8), np.ones(width * height, np.uint8),
                   rng.integers(0, 2, width * height, dtype=np.uint8)):
        payload = codec._encode_raster(pixels.tolist(), width, height)
        assert fused(payload, width, height) == strict_decode(payload, width, height) == pixels.tobytes()
        packed = codec._unpack(payload[1:])
        mutants = [payload[:-1], payload + "!", payload.replace("!", ";", 1)]
        for pos in sorted({*range(min(8, len(packed))), *range(max(0, len(packed) - 4), len(packed)),
                           *rng.integers(0, len(packed), 8).tolist()}):
            changed = bytearray(packed)
            changed[pos] ^= 1
            mutants.append("!" + codec._pack(changed))
        mutants += ["!" + codec._pack(packed + b"\0"), "!" + codec._pack(packed[:-1])]
        for mutant in mutants:
            assert outcome(fused, mutant, width, height) == outcome(strict_decode, mutant, width, height)
