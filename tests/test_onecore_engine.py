from Core.onecore_engine import speaking_rate


def test_speaking_rate_maps_wpm_and_clamps():
    assert speaking_rate(326) == 2.0
    assert speaking_rate(5000) == 6.0
    assert speaking_rate(10) == 0.5
