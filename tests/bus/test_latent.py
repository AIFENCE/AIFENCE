import base64

import pytest

from aifence.bus.latent import pack_latent, unpack_latent


def test_latent_quantization_round_trip():
    vector = [-1.25, -0.1, 0.0, 0.5, 2.0]
    packet = pack_latent(vector, "worker-a:hidden:v3")
    restored = unpack_latent(packet)
    assert packet.dims == len(vector)
    assert len(base64.b64decode(packet.data_b64)) == len(vector)
    for original, recovered in zip(vector, restored, strict=True):
        assert recovered == pytest.approx(original, abs=packet.scale / 2 + 1e-9)


def test_latent_checksum_detects_corruption():
    packet = pack_latent([0.1, 0.2, 0.3], "space")
    raw = bytearray(base64.b64decode(packet.data_b64))
    raw[0] ^= 1
    broken = packet.model_copy(update={"data_b64": base64.b64encode(raw).decode()})
    with pytest.raises(ValueError, match="checksum"):
        unpack_latent(broken)
