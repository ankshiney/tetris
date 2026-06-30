"""Easing and frame-timing helpers for smooth animation."""

import math


def clamp_dt(dt: float, maximum: float = 0.05) -> float:
    """Cap delta time to avoid physics spikes after lag."""
    return min(max(dt, 0.0), maximum)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def ease_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) ** 3


def ease_out_back(t: float) -> float:
    t = max(0.0, min(1.0, t))
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def ease_out_elastic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    if t == 0 or t == 1:
        return t
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi / 3)) + 1


def smooth_damp(current: float, target: float, dt: float, smooth_time: float = 0.08) -> float:
    """Critically damped smoothing — great for HUD counters."""
    if smooth_time <= 0:
        return target
    omega = 2.0 / smooth_time
    x = omega * dt
    exp = 1.0 / (1.0 + x + 0.48 * x * x + 0.235 * x * x * x)
    change = current - target
    return target + (current - target - change * exp)