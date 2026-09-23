import numpy as np
import pytest

from hexapod.gait import GAITS, make_gait


@pytest.mark.parametrize("name", sorted(GAITS))
def test_min_stance_legs(name):
    g = make_gait(name)
    # lệch 1e-7 để tránh đúng thời điểm chuyển pha (một chân nhấc đúng lúc chân khác đặt xuống)
    for t in np.linspace(0, 3 * g.period, 2000, endpoint=False) + 1e-7:
        stance = sum(not g.phase(i, float(t))[0] for i in range(6))
        assert stance >= g.min_stance, (name, t, stance)


def test_tripod_groups():
    g = make_gait("tripod")
    sw = [g.phase(i, 0.1)[0] for i in range(6)]
    assert sw == [True, False, True, False, True, False]


def test_unknown_gait():
    with pytest.raises(ValueError):
        make_gait("gallop")
