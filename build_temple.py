#!/usr/bin/env python3
"""
Build a historically-informed 3D model of King Solomon's Temple (First Temple)
based on 1 Kings 6 and 2 Chronicles 3–4.

Scale: 1 cubit = 0.5 meters (Z-up; entrance +Y; Holy of Holies −Y)

Runs two ways:
  blender --background --python build_temple.py
      → solomon_temple.blend, preview.png, docs/models/solomon_temple.glb
  python3 build_temple.py
      → docs/models/solomon_temple.glb and docs/labels.json
        (used when Blender is not installed)
"""

from __future__ import annotations

import json
import math
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from temple_geometry import MATERIALS, build_scene, labels_as_json  # noqa: E402

BLEND_PATH = os.path.join(SCRIPT_DIR, "solomon_temple.blend")
PREVIEW_PATH = os.path.join(SCRIPT_DIR, "preview.png")
GLB_PATH = os.path.join(SCRIPT_DIR, "docs", "models", "solomon_temple.glb")
LABELS_PATH = os.path.join(SCRIPT_DIR, "docs", "labels.json")


def write_labels(scene) -> None:
    os.makedirs(os.path.dirname(LABELS_PATH), exist_ok=True)
    with open(LABELS_PATH, "w", encoding="utf-8") as fh:
        json.dump(labels_as_json(scene.labels), fh, indent=2)
        fh.write("\n")
    print(f"Wrote {LABELS_PATH}")


def export_with_python(scene) -> None:
    from gltf_writer import export_glb

    export_glb(scene.prims, MATERIALS, GLB_PATH)
    print(f"Exported {GLB_PATH} ({os.path.getsize(GLB_PATH)} bytes, {len(scene.prims)} meshes)")


def _blender_material(cache, spec):
    import bpy

    if spec.name in cache:
        return cache[spec.name]
    mat = bpy.data.materials.new(name=spec.name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*spec.color, spec.alpha)
    bsdf.inputs["Roughness"].default_value = spec.roughness
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = spec.metallic
    if spec.alpha < 0.999:
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = spec.alpha
        mat.blend_method = "BLEND"
    if spec.emissive != (0.0, 0.0, 0.0) and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*spec.emissive, 1.0)
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = 4.0
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    cache[spec.name] = mat
    return mat


def build_blender(scene) -> None:
    import bpy
    from mathutils import Euler, Vector

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for block in list(coll):
            if block.users == 0:
                block.remove(block)

    cache = {}
    for prim in scene.prims:
        spec = MATERIALS[prim.material]
        mat = _blender_material(cache, spec)
        if prim.kind == "box":
            bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
            obj = bpy.context.active_object
            obj.scale = (prim.size[0] / 2, prim.size[1] / 2, prim.size[2] / 2)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        elif prim.kind == "cylinder":
            bpy.ops.mesh.primitive_cylinder_add(
                radius=prim.radius,
                depth=prim.height,
                location=(0, 0, 0),
                vertices=prim.segments,
            )
            obj = bpy.context.active_object
        else:
            continue
        obj.name = prim.name
        obj.location = prim.location
        obj.rotation_euler = Euler(prim.rotation)
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        for key, value in prim.extras.items():
            obj[key] = value

    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    wn = world.node_tree.nodes
    wl = world.node_tree.links
    wn.clear()
    out_w = wn.new("ShaderNodeOutputWorld")
    bg = wn.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.55, 0.62, 0.72, 1.0)
    bg.inputs["Strength"].default_value = 0.85
    wl.new(bg.outputs["Background"], out_w.inputs["Surface"])

    bpy.ops.object.light_add(type="SUN", location=(20, -15, 40))
    sun = bpy.context.active_object
    sun.name = "Sun"
    sun.data.energy = 3.5
    sun.rotation_euler = Euler((math.radians(45), math.radians(15), math.radians(-35)))

    bpy.ops.object.light_add(type="AREA", location=(-18, 25, 20))
    fill = bpy.context.active_object
    fill.name = "FillLight"
    fill.data.energy = 400
    fill.data.size = 15
    fill.rotation_euler = Euler((math.radians(60), 0, math.radians(150)))

    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    cam.name = "Camera"
    cam.location = (28, 42, 22)
    target = Vector((0, 19, FOUND_VIEW_Z()))
    direction = target - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 35
    bpy.context.scene.camera = cam

    scene_b = bpy.context.scene
    scene_b.render.resolution_x = 1920
    scene_b.render.resolution_y = 1080
    scene_b.render.resolution_percentage = 100
    scene_b.render.filepath = PREVIEW_PATH
    scene_b.render.image_settings.file_format = "PNG"

    engine = None
    for candidate in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene_b.render.engine = candidate
            engine = candidate
            break
        except Exception:
            continue
    if engine is None:
        scene_b.render.engine = "CYCLES"
        engine = "CYCLES"
    print(f"Using render engine: {engine}")
    if engine == "CYCLES":
        scene_b.cycles.samples = 64
        scene_b.cycles.use_denoising = True
        try:
            scene_b.cycles.device = "CPU"
        except Exception:
            pass
    elif hasattr(scene_b, "eevee"):
        ee = scene_b.eevee
        if hasattr(ee, "taa_render_samples"):
            ee.taa_render_samples = 64
        if hasattr(ee, "use_gtao"):
            ee.use_gtao = True

    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print(f"Saved: {BLEND_PATH}")
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {PREVIEW_PATH}")

    os.makedirs(os.path.dirname(GLB_PATH), exist_ok=True)
    export_kw = dict(filepath=GLB_PATH, export_format="GLB", export_extras=True)
    try:
        bpy.ops.export_scene.gltf(**export_kw)
    except TypeError:
        bpy.ops.export_scene.gltf(filepath=GLB_PATH)
    print(f"Exported: {GLB_PATH}")
    print("Objects:")
    for obj in bpy.data.objects:
        print(f"  - {obj.name} ({obj.type})")


def FOUND_VIEW_Z() -> float:
    from temple_geometry import FOUND_H, MAIN_H

    return FOUND_H + MAIN_H * 0.45


def main() -> None:
    scene = build_scene()
    write_labels(scene)
    try:
        import bpy  # noqa: F401

        build_blender(scene)
    except ImportError:
        export_with_python(scene)
        print("Blender not importable; wrote glTF only.")


if __name__ == "__main__":
    main()
