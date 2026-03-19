import math

from . import StructType, func
from .mathtypes import *
from .types import *

RandomSampler = StructType(state=int)


@func
def _f(self, init_state):
    self.state = init_state


RandomSampler.add_method(_f, "__init__")


@func
def make_random_sampler(v0, v1):
    s0 = uint()
    for _ in range(4):
        s0 += 0x9E3779B9
        v0 += ((v1 << 4) + 0xA341316C) ^ (v1 + s0) ^ ((v1 >> 5) + 0xC8013EA4)
        v1 += ((v0 << 4) + 0xAD90777D) ^ (v0 + s0) ^ ((v0 >> 5) + 0x7E95761E)
    return RandomSampler(v0)


@func
def make_random_sampler3d(p):
    PRIME32_2 = 2246822519
    PRIME32_3 = 3266489917
    PRIME32_4 = 668265263
    PRIME32_5 = 374761393
    h32 = p.z + PRIME32_5 + p.x * PRIME32_3
    h32 = PRIME32_4 * ((h32 << 17) | 0x0001FFFF & (h32 >> (32 - 17)))
    h32 += p.y * PRIME32_3
    h32 = PRIME32_4 * ((h32 << 17) | 0x0001FFFF & (h32 >> (32 - 17)))
    h32 = PRIME32_2 * (h32 ^ ((h32 >> 15) & 0x0001FFFF))
    h32 = PRIME32_3 * (h32 ^ ((h32 >> 13) & 0x0007FFFF))
    return RandomSampler(h32 ^ ((h32 >> 16) & 0x0000FFFF))


@func
def sign(x):
    return copysign(1.0, x)


@func
def fmod(x, y):
    return x - y * trunc(x / y)


@func
def mod(x, y):
    return x - y * floor(x / y)


@func
def _f(self):
    lcg_a = 1664525
    lcg_c = 1013904223
    self.state = lcg_a * self.state + lcg_c
    return float(self.state & 0x00FFFFFF) * (1.0 / 0x01000000)


RandomSampler.add_method(_f, "next")


@func
def _f(self):
    return float2(self.next(), self.next())


RandomSampler.add_method(_f, "next2f")


@func
def _f(self):
    return float3(self.next(), self.next(), self.next())


RandomSampler.add_method(_f, "next3f")


@func
def ite(a, b, c):
    return select(c, b, a)


@func
def make_float2x2_eye(v: float):
    return float2x2(v, 0, 0, v)


@func
def make_float3x3_eye(v: float):
    return float3x3(v, 0, 0, 0, v, 0, 0, 0, v)


@func
def make_float4x4_eye(v: float):
    return float4x4(v, 0, 0, 0, 0, v, 0, 0, 0, 0, v, 0, 0, 0, 0, v)


@func
def distance(a, b):
    return length(a - b)


@func
def distance_squared(a, b):
    return length_squared(a - b)


@func
def radians(x):
    return x * (math.pi / 180.0)


@func
def degree(x):
    return x * (180.0 / math.pi)
