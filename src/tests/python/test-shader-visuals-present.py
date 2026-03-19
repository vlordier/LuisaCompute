import math
import sys

import numpy as np
from luisa import *
from luisa.builtin import *
from luisa.types import *
from luisa.util import *

backend_name = None
if len(sys.argv) >= 2:
    backend_name = sys.argv[1]
init(backend_name=backend_name)


@func
def comp(p):
    p = asin(sin(p) * 0.9)
    return length(p) - 1.0


@func
def erot(p, ax, ro):
    return lerp(dot(p, ax) * ax, p, cos(ro)) + sin(ro) * cross(ax, p)


@func
def smin(a, b, k):
    h = max(0.0, k - abs(b - a)) / k
    return min(a, b) + h * h * h * k / 6.0


@func
def wrot(p):
    return float4(dot(p, float4(1.0)), p.yzw + p.zwy - p.wyz - p.xxx) * 0.5


Data = StructType(
    lazors=float,
    doodad=float,
    p2=float3,
    d1=float,
    d2=float,
    d3=float,
)


@func
def scene(p, t, data):
    bpm = 125.0
    data.p2 = erot(p, float3(0.0, 1.0, 0.0), t)
    data.p2 = erot(data.p2, float3(0.0, 0.0, 1.0), t / 3.0)
    data.p2 = erot(data.p2, float3(1.0, 0.0, 0.0), t / 5.0)
    bpt = time / 60.0 * bpm
    p4 = float4(data.p2, 0.0)
    p4 = lerp(p4, wrot(p4), smoothstep(-0.5, 0.5, sin(bpt / 4.0)))
    p4 = abs(p4)
    p4 = lerp(p4, wrot(p4), smoothstep(-0.5, 0.5, sin(bpt)))
    fctr = smoothstep(-0.5, 0.5, sin(bpt / 2.0))
    fctr2 = smoothstep(0.9, 1.0, sin(bpt / 16.0))
    data.doodad = (
        length(max(abs(p4) - lerp(0.05, 0.07, fctr), 0.0) + lerp(-0.1, 0.2, fctr))
        - lerp(0.15, 0.55, fctr * fctr)
        + fctr2
    )
    p.x += asin(sin(t / 80.0) * 0.99) * 80.0
    data.lazors = length(asin(sin(erot(p, float3(1.0, 0.0, 0.0), t * 0.2).yz * 0.5 + 1.0)) / 0.5) - 0.1
    data.d1 = comp(p)
    data.d2 = comp(erot(p + 5.0, normalize(float3(1.0, 3.0, 4.0)), 0.4))
    data.d3 = comp(erot(p + 10.0, normalize(float3(3.0, 2.0, 1.0)), 1.0))
    return min(data.doodad, min(data.lazors, 0.3 - smin(smin(data.d1, data.d2, 0.05), data.d3, 0.05)))


@func
def norm(p, t, data):
    precis = ite(length(p) < 1.0, 0.005, 0.01)
    k = float3x3(p, p, p) - float3x3(precis, 0.0, 0.0, 0.0, precis, 0.0, 0.0, 0.0, precis)
    return normalize(scene(p, t, data) - float3(scene(k[0], t, data), scene(k[1], t, data), scene(k[2], t, data)))


@func
def render_kernel(image, time):
    bpm = 125.0
    fragCoord = float2(dispatch_id().xy)
    iResolution = float2(dispatch_size().xy)
    uv = (fragCoord - 0.5 * iResolution) / iResolution.y

    bpt = time / 60.0 * bpm
    bp = lerp(pow(sin(fract(bpt) * math.pi / 2.0), 20.0) + floor(bpt), bpt, 0.4)
    t = bp
    cam = normalize(float3(0.8 + sin(bp * 3.14 / 4.0) * 0.3, uv))
    init = float3(-1.5 + sin(bp * 3.14) * 0.2, 0.0, 0.0) + cam * 0.2
    init = erot(init, float3(0.0, 1.0, 0.0), sin(bp * 0.2) * 0.4)
    init = erot(init, float3(0.0, 0.0, 1.0), cos(bp * 0.2) * 0.4)
    cam = erot(cam, float3(0.0, 1.0, 0.0), sin(bp * 0.2) * 0.4)
    cam = erot(cam, float3(0.0, 0.0, 1.0), cos(bp * 0.2) * 0.4)
    p = init
    atten = 1.0
    tlen = 0.0
    glo = 0.0
    fog = 0.0
    dlglo = 0.0
    trg = False
    dist = 0.0
    data = Data()
    for _ in range(80):
        dist = scene(p, t, data)
        hit = dist * dist < 1e-6
        glo += 0.2 / (1.0 + data.lazors * data.lazors * 20.0) * atten
        dlglo += 0.2 / (1.0 + data.doodad * data.doodad * 20.0) * atten
        if (
            hit
            and (
                (sin(data.d3 * 45.0) < -0.4 and (dist != data.doodad))
                or (dist == data.doodad and sin(pow(length(data.p2 * data.p2 * data.p2), 0.3) * 120.0) > 0.4)
            )
            and dist != data.lazors
        ):
            trg = trg or dist == data.doodad
            hit = False
            n = norm(p, t, data)
            atten *= 1.0 - abs(dot(cam, n)) * 0.98
            cam = reflect(cam, n)
            dist = 0.1
        p += cam * dist
        tlen += dist
        fog += dist * atten / 30.0
        if hit:
            break
    fog = smoothstep(0.0, 1.0, fog)
    lz = data.lazors == dist
    dl = data.doodad == dist
    fogcol = lerp(float3(0.5, 0.8, 1.2), float3(0.4, 0.6, 0.9), length(uv))
    n = norm(p, t, data)
    r = reflect(cam, n)
    ss = smoothstep(-0.3, 0.3, scene(p + float3(0.3), t, data)) + 0.5
    fact = length(sin(r * (ite(dl, 4.0, 3.0))) * 0.5 + 0.5) / sqrt(3.0) * 0.7 + 0.3
    matcol = lerp(float3(0.9, 0.4, 0.3), float3(0.3, 0.4, 0.8), smoothstep(-1.0, 1.0, sin(data.d1 * 5.0 + time * 2.0)))
    matcol = lerp(matcol, float3(0.5, 0.4, 1.0), smoothstep(0.0, 1.0, sin(data.d2 * 5.0 + time * 2.0)))
    matcol = ite(dl, lerp(float3(1.0), matcol, 0.1) * 0.2 + 0.1, matcol)
    col = matcol * fact * ss + pow(fact, 10.0)
    col = ite(lz, float3(4.0), col)
    fragColor = col * atten + glo * glo + fogcol * glo
    fragColor = lerp(fragColor, fogcol, fog)
    fragColor = ite(dl, fragColor, abs(erot(fragColor, normalize(sin(p * 2.0)), 0.2 * (1.0 - fog))))
    fragColor = ite(trg or dl, fragColor, fragColor + dlglo * dlglo * 0.1 * float3(0.4, 0.6, 0.9))
    fragColor = sqrt(fragColor)
    color = smoothstep(float3(0.0), float3(1.2), fragColor)
    image.write(dispatch_id().xy, float4(pow(color, 2.2), 1.0))


@func
def clear_kernel(image):
    coord = dispatch_id().xy
    image.write(coord, float4(0.3, 0.4, 0.5, 1.0))


res = 1280, 720
image = Image2D(*res, 4, float, storage="BYTE")
gui = GUI("Test shadertoy", res)
clear_kernel(image, dispatch_size=(*res, 1))
time = 0.0
while gui.running():
    gui.set_image(image)
    render_kernel(image, time, dispatch_size=(*res, 1))
    # use seconds
    time += gui.show() / 1000.0
synchronize()
