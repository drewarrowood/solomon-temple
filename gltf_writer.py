"""Minimal glTF 2.0 binary exporter for box and cylinder primitives (Y-up)."""

from __future__ import annotations

import json
import math
import os
import struct
from typing import Dict, Iterable, List, Sequence, Tuple

from temple_geometry import Material, Prim, blender_to_gltf

Vec3 = Tuple[float, float, float]


def _euler_xyz_matrix(rx: float, ry: float, rz: float) -> List[List[float]]:
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    # Intrinsic XYZ: apply X, then Y, then Z. Column-vector convention: R = Rz Ry Rx
    return [
        [cy * cz, sx * sy * cz - cx * sz, cx * sy * cz + sx * sz],
        [cy * sz, sx * sy * sz + cx * cz, cx * sy * sz - sx * cz],
        [-sy, sx * cy, cx * cy],
    ]


def _mul(m: Sequence[Sequence[float]], v: Vec3) -> Vec3:
    return (
        m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2],
        m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2],
        m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2],
    )


def _add(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _xform(p: Vec3, rot: Vec3, loc: Vec3) -> Vec3:
    if rot != (0.0, 0.0, 0.0):
        p = _mul(_euler_xyz_matrix(*rot), p)
    world = _add(p, loc)
    x, y, z = blender_to_gltf(world)
    return (x, y, z)


def _xform_n(n: Vec3, rot: Vec3) -> Vec3:
    if rot != (0.0, 0.0, 0.0):
        n = _mul(_euler_xyz_matrix(*rot), n)
    x, y, z = blender_to_gltf(n)
    length = math.sqrt(x * x + y * y + z * z) or 1.0
    return (x / length, y / length, z / length)


def mesh_box(size: Vec3, loc: Vec3, rot: Vec3) -> Tuple[List[float], List[float], List[int]]:
    sx, sy, sz = size[0] / 2, size[1] / 2, size[2] / 2
    faces = (
        ((sx, -sy, -sz), (sx, sy, -sz), (sx, sy, sz), (sx, -sy, sz), (1.0, 0.0, 0.0)),
        ((-sx, sy, -sz), (-sx, -sy, -sz), (-sx, -sy, sz), (-sx, sy, sz), (-1.0, 0.0, 0.0)),
        ((-sx, sy, -sz), (sx, sy, -sz), (sx, sy, sz), (-sx, sy, sz), (0.0, 1.0, 0.0)),
        ((sx, -sy, -sz), (-sx, -sy, -sz), (-sx, -sy, sz), (sx, -sy, sz), (0.0, -1.0, 0.0)),
        ((-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz), (0.0, 0.0, 1.0)),
        ((-sx, sy, -sz), (sx, sy, -sz), (sx, -sy, -sz), (-sx, -sy, -sz), (0.0, 0.0, -1.0)),
    )
    positions: List[float] = []
    normals: List[float] = []
    indices: List[int] = []
    base = 0
    for a, b, c, d, n in faces:
        for v in (a, b, c, d):
            p = _xform(v, rot, loc)
            nn = _xform_n(n, rot)
            positions.extend(p)
            normals.extend(nn)
        indices.extend((base, base + 1, base + 2, base, base + 2, base + 3))
        base += 4
    return positions, normals, indices


def mesh_cylinder(
    radius: float,
    height: float,
    loc: Vec3,
    rot: Vec3,
    segments: int,
) -> Tuple[List[float], List[float], List[int]]:
    segments = max(8, segments)
    hh = height / 2
    positions: List[float] = []
    normals: List[float] = []
    indices: List[int] = []

    def push(v: Vec3, n: Vec3) -> int:
        p = _xform(v, rot, loc)
        nn = _xform_n(n, rot)
        idx = len(positions) // 3
        positions.extend(p)
        normals.extend(nn)
        return idx

    ring_bot: List[int] = []
    ring_top: List[int] = []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        x, y = radius * math.cos(a), radius * math.sin(a)
        n = (x / radius, y / radius, 0.0)
        ring_bot.append(push((x, y, -hh), n))
        ring_top.append(push((x, y, hh), n))
    for i in range(segments):
        j = (i + 1) % segments
        indices.extend((ring_bot[i], ring_bot[j], ring_top[j], ring_bot[i], ring_top[j], ring_top[i]))

    bot_center = push((0.0, 0.0, -hh), (0.0, 0.0, -1.0))
    top_center = push((0.0, 0.0, hh), (0.0, 0.0, 1.0))
    bot_rim: List[int] = []
    top_rim: List[int] = []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        x, y = radius * math.cos(a), radius * math.sin(a)
        bot_rim.append(push((x, y, -hh), (0.0, 0.0, -1.0)))
        top_rim.append(push((x, y, hh), (0.0, 0.0, 1.0)))
    for i in range(segments):
        j = (i + 1) % segments
        indices.extend((bot_center, bot_rim[j], bot_rim[i]))
        indices.extend((top_center, top_rim[i], top_rim[j]))
    return positions, normals, indices


def _minmax(values: Sequence[float]) -> Tuple[List[float], List[float]]:
    xs, ys, zs = values[0::3], values[1::3], values[2::3]
    return [min(xs), min(ys), min(zs)], [max(xs), max(ys), max(zs)]


def _pad4(buf: bytearray) -> None:
    while len(buf) % 4:
        buf.append(0)


def export_glb(
    primitives: Iterable[Prim],
    materials: Dict[str, Material],
    path: str,
) -> str:
    mat_names = list(materials)
    mat_index = {name: i for i, name in enumerate(mat_names)}

    gltf_materials = []
    for name in mat_names:
        mat = materials[name]
        pbr = {
            "baseColorFactor": [mat.color[0], mat.color[1], mat.color[2], mat.alpha],
            "metallicFactor": mat.metallic,
            "roughnessFactor": mat.roughness,
        }
        entry = {
            "name": name,
            "pbrMetallicRoughness": pbr,
            "doubleSided": True,
        }
        if mat.alpha < 0.999:
            entry["alphaMode"] = "BLEND"
        if mat.emissive != (0.0, 0.0, 0.0):
            entry["emissiveFactor"] = list(mat.emissive)
        gltf_materials.append(entry)

    bin_data = bytearray()
    buffer_views = []
    accessors = []
    meshes = []
    nodes = []

    def add_f32(data: Sequence[float], target: int, count: int, typ: str, with_minmax: bool = False) -> int:
        offset = len(bin_data)
        raw = struct.pack("<" + "f" * len(data), *data)
        bin_data.extend(raw)
        _pad4(bin_data)
        view_i = len(buffer_views)
        buffer_views.append(
            {"buffer": 0, "byteOffset": offset, "byteLength": len(raw), "target": target}
        )
        acc = {
            "bufferView": view_i,
            "componentType": 5126,
            "count": count,
            "type": typ,
        }
        if with_minmax:
            acc["min"], acc["max"] = _minmax(data)
        accessors.append(acc)
        return len(accessors) - 1

    def add_u32(data: Sequence[int], target: int) -> int:
        offset = len(bin_data)
        raw = struct.pack("<" + "I" * len(data), *data)
        bin_data.extend(raw)
        _pad4(bin_data)
        view_i = len(buffer_views)
        buffer_views.append(
            {"buffer": 0, "byteOffset": offset, "byteLength": len(raw), "target": target}
        )
        accessors.append(
            {
                "bufferView": view_i,
                "componentType": 5125,
                "count": len(data),
                "type": "SCALAR",
            }
        )
        return len(accessors) - 1

    for prim in primitives:
        if prim.kind == "box":
            assert prim.size is not None
            pos, nrm, idx = mesh_box(prim.size, prim.location, prim.rotation)
        elif prim.kind == "cylinder":
            pos, nrm, idx = mesh_cylinder(
                prim.radius, prim.height, prim.location, prim.rotation, prim.segments
            )
        else:
            raise ValueError(f"Unknown primitive kind: {prim.kind}")

        nvert = len(pos) // 3
        pos_i = add_f32(pos, 34962, nvert, "VEC3", with_minmax=True)
        nrm_i = add_f32(nrm, 34962, nvert, "VEC3")
        idx_i = add_u32(idx, 34963)
        mesh_i = len(meshes)
        meshes.append(
            {
                "name": prim.name,
                "primitives": [
                    {
                        "attributes": {"POSITION": pos_i, "NORMAL": nrm_i},
                        "indices": idx_i,
                        "material": mat_index.get(prim.material, 0),
                    }
                ],
            }
        )
        extras = dict(prim.extras)
        extras["material"] = prim.material
        nodes.append({"name": prim.name, "mesh": mesh_i, "extras": extras})

    gltf = {
        "asset": {
            "version": "2.0",
            "generator": "solomon-temple/gltf_writer.py",
        },
        "scene": 0,
        "scenes": [{"name": "SolomonsTemple", "nodes": list(range(len(nodes)))}],
        "nodes": nodes,
        "meshes": meshes,
        "materials": gltf_materials,
        "accessors": accessors,
        "bufferViews": buffer_views,
        "buffers": [{"byteLength": len(bin_data)}],
    }

    json_bytes = bytearray(json.dumps(gltf, separators=(",", ":")).encode("utf-8"))
    while len(json_bytes) % 4:
        json_bytes.append(0x20)

    total = 12 + 8 + len(json_bytes) + 8 + len(bin_data)
    header = struct.pack("<4sII", b"glTF", 2, total)
    json_chunk = struct.pack("<I4s", len(json_bytes), b"JSON") + json_bytes
    bin_chunk = struct.pack("<I4s", len(bin_data), b"BIN\x00") + bin_data

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(header + json_chunk + bin_chunk)
    return path
