import math

import numpy as np
import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from hexapod.kinematics import LegKinematics, UnreachableError

LEG = LegKinematics(0.05, 0.08, 0.12)


def test_fk_known_angles():
    np.testing.assert_allclose(LEG.fk(np.zeros(3)), [0.25, 0, 0], atol=1e-12)
    np.testing.assert_allclose(LEG.fk(np.array([math.pi / 2, 0, 0])), [0, 0.25, 0], atol=1e-12)
    np.testing.assert_allclose(LEG.fk(np.array([0, 0, -math.pi / 2])), [0.13, 0, -0.12], atol=1e-12)
    np.testing.assert_allclose(LEG.fk(np.array([0, math.pi / 2, -math.pi / 2])), [0.17, 0, 0.08], atol=1e-12)


@settings(max_examples=10_000, deadline=None, suppress_health_check=[HealthCheck.filter_too_much])
@given(
    st.floats(-math.pi / 4, math.pi / 4),
    st.floats(-math.pi / 2, math.pi / 2),
    st.floats(-5 * math.pi / 6, -0.05),
)
def test_ik_fk_roundtrip(t1, t2, t3):
    """FK(IK(p)) = p với mọi p trong vùng làm việc (đầu chân ở phía ngoài khớp coxa, nghiệm knee-up hợp lệ)."""
    p = LEG.fk(np.array([t1, t2, t3]))
    assume(math.hypot(p[0], p[1]) > LEG.l1 * 0.2)
    q, ok = LEG.ik_clamped(p)
    assume(ok)
    assert np.linalg.norm(LEG.fk(q) - p) < 1e-6


@settings(max_examples=2_000, deadline=None)
@given(st.floats(0.10, 0.22), st.floats(-0.08, 0.08), st.floats(-0.14, -0.04))
def test_ik_fk_walking_workspace(x, y, z):
    """Vùng đầu chân thực tế khi đi: IK luôn giải được và chính xác."""
    p = np.array([x, y, z])
    q, ok = LEG.ik_clamped(p)
    assume(ok)
    assert np.linalg.norm(LEG.fk(q) - p) < 1e-6


def test_ik_unreachable():
    with pytest.raises(UnreachableError):
        LEG.ik(np.array([0.5, 0.0, 0.0]))
    with pytest.raises(UnreachableError):
        LEG.ik(np.array([0.051, 0.0, 0.0]))


def test_ik_clamped_flags_limits():
    q, ok = LEG.ik_clamped(np.array([0.1, 0.2, -0.05]))   # coxa ~63° > 45°
    assert not ok
    assert LEG.within_limits(q)
