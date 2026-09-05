"""
Build a historically-informed 3D model of King Solomon's Temple (First Temple)
based on 1 Kings 6 and 2 Chronicles 3–4.

Scale: 1 cubit = 0.5 meters (Blender units = meters)
Orientation: entrance faces +Y (east); Holy of Holies at -Y (west/rear)
Origin: ground center of the main building footprint
"""

import math
import os
import bpy
from mathutils import Vector, Euler

OUT_DIR = "/workspace/solomon-temple"
BLEND_PATH = os.path.join(OUT_DIR, "solomon_temple.blend")
PREVIEW_PATH = os.path.join(OUT_DIR, "preview.png")

# --- Dimensions (meters; 1 cubit = 0.5 m) ---
CUBIT = 0.5

# Main building: 60 × 20 × 30 cubits
MAIN_L = 60 * CUBIT   # 30 m (along Y, porch to rear)
MAIN_W = 20 * CUBIT   # 10 m (along X)
MAIN_H = 30 * CUBIT   # 15 m

# Porch (ulam): 20 wide × 10 deep, height ~30 cubits
PORCH_W = 20 * CUBIT  # 10 m
PORCH_D = 10 * CUBIT  # 5 m
PORCH_H = 30 * CUBIT  # 15 m

# Holy of Holies (debir): 20 × 20 × 20 at west end
DEBIT_L = 20 * CUBIT  # 10 m
DEBIT_W = 20 * CUBIT  # 10 m
DEBIT_H = 20 * CUBIT  # 10 m

# Holy Place (hekal): remaining 40 cubits
HEKAL_L = 40 * CUBIT  # 20 m
HEKAL_W = 20 * CUBIT  # 10 m
HEKAL_H = 30 * CUBIT  # 15 m

# Side chambers: ~5 cubits deep, three stories stepped
SIDE_DEPTH = 5 * CUBIT  # 2.5 m
STORY_H = 5 * CUBIT     # 2.5 m per story (approx; biblical: lower 5, middle 6, upper 7 cubits)

# Pillars Jachin & Boaz: ~18 cubits shafts
PILLAR_H = 18 * CUBIT   # 9 m
PILLAR_R = 0.6          # radius ~1.2 m diameter (stylized)
CAPITAL_H = 2.5 * CUBIT # ~1.25 m
CAPITAL_R = 0.9

# Foundation / platform
FOUND_H = 1.5
FOUND_PAD = 3.0  # extra padding beyond walls

# Court pavement
COURT_W = 40.0
COURT_D = 50.0

# Bronze altar (2 Chron 4:1 — 20×20×10 cubits, stylized as low block)
ALTAR_W = 20 * CUBIT  # 10 m
ALTAR_D = 20 * CUBIT  # 10 m
ALTAR_H = 2.0         # lower for readability (full 5 m would dominate)


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    # Clear orphan data
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for b in list(block):
            if b.users == 0:
                block.remove(b)


def make_material(name, color, roughness=0.55, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = metallic
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def add_box(name, size, location, material=None, rotation=(0, 0, 0)):
    """Create a cube scaled to size (sx, sy, sz) with origin at geometric center,
    then place so bottom sits correctly if location.z is center Z."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.location = location
    obj.rotation_euler = Euler(rotation)
    if material:
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
    return obj


def add_cylinder(name, radius, depth, location, material=None, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=depth, location=location, vertices=vertices
    )
    obj = bpy.context.active_object
    obj.name = name
    if material:
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
    return obj


def build():
    clear_scene()
    os.makedirs(OUT_DIR, exist_ok=True)

    # Materials
    mat_limestone = make_material("Limestone", (0.82, 0.76, 0.62), roughness=0.65)
    mat_sandstone = make_material("Sandstone", (0.72, 0.62, 0.48), roughness=0.7)
    mat_foundation = make_material("FoundationStone", (0.35, 0.32, 0.28), roughness=0.85)
    mat_bronze = make_material("Bronze", (0.55, 0.35, 0.12), roughness=0.35, metallic=0.85)
    mat_wood = make_material("CedarWood", (0.45, 0.28, 0.14), roughness=0.55)
    mat_court = make_material("CourtStone", (0.55, 0.52, 0.48), roughness=0.9)
    mat_roof = make_material("RoofCedar", (0.38, 0.22, 0.12), roughness=0.6)
    mat_inner = make_material("InnerGoldTint", (0.75, 0.65, 0.35), roughness=0.4, metallic=0.3)

    # Layout along Y:
    # Origin at ground center of MAIN footprint (nave+sanctuary = 30m long).
    # Main extends Y from -MAIN_L/2 to +MAIN_L/2.
    # Holy of Holies at west (-Y): from -MAIN_L/2 to -MAIN_L/2 + DEBIT_L
    # Holy Place: from -MAIN_L/2 + DEBIT_L to +MAIN_L/2
    # Porch attached at +Y end of main: from +MAIN_L/2 to +MAIN_L/2 + PORCH_D

    main_y0 = -MAIN_L / 2  # rear wall (Holy of Holies back)
    main_y1 = MAIN_L / 2   # front of Holy Place / porch attach

    debit_center_y = main_y0 + DEBIT_L / 2
    hekal_center_y = main_y0 + DEBIT_L + HEKAL_L / 2
    porch_center_y = main_y1 + PORCH_D / 2

    # --- Foundation platform under whole building (main + porch + side overhang) ---
    total_foot_y = MAIN_L + PORCH_D
    foot_center_y = (main_y0 + (main_y1 + PORCH_D)) / 2  # center of main+porch
    foot_w = MAIN_W + 2 * SIDE_DEPTH + 2 * FOUND_PAD
    foot_d = total_foot_y + 2 * FOUND_PAD
    add_box(
        "Foundation",
        (foot_w, foot_d, FOUND_H),
        (0, foot_center_y, FOUND_H / 2),
        mat_foundation,
    )

    z0 = FOUND_H  # building floor level

    # --- Holy of Holies (cube volume, slightly lower ceiling historically) ---
    # Exterior shell for debir — full height walls matching main for exterior reading,
    # but interior volume represented as 10×10×10 block (massing).
    add_box(
        "HolyOfHolies",
        (DEBIT_W, DEBIT_L, DEBIT_H),
        (0, debit_center_y, z0 + DEBIT_H / 2),
        mat_inner,
    )
    # Upper walls/roof mass above debir to match 15m exterior ridge line
    upper_h = MAIN_H - DEBIT_H
    if upper_h > 0.01:
        add_box(
            "HolyOfHoliesUpper",
            (DEBIT_W, DEBIT_L, upper_h),
            (0, debit_center_y, z0 + DEBIT_H + upper_h / 2),
            mat_limestone,
        )

    # --- Holy Place (hekal) ---
    add_box(
        "HolyPlace",
        (HEKAL_W, HEKAL_L, HEKAL_H),
        (0, hekal_center_y, z0 + HEKAL_H / 2),
        mat_limestone,
    )

    # --- Porch (ulam) ---
    add_box(
        "Porch",
        (PORCH_W, PORCH_D, PORCH_H),
        (0, porch_center_y, z0 + PORCH_H / 2),
        mat_sandstone,
    )

    # Entrance doorway recess on porch front (+Y face)
    door_w = 4.0
    door_h = 8.0
    door_d = 0.4
    add_box(
        "EntranceDoor",
        (door_w, door_d, door_h),
        (0, porch_center_y + PORCH_D / 2 - door_d / 2 + 0.01, z0 + door_h / 2),
        mat_wood,
    )

    # --- Side chambers: three stepped stories along sides and rear ---
    # Simplified as three stacked volumes, each deeper inward than the one above
    # (biblical: beams rested on offsets; lower story deepest outward).
    # We model exterior stepped volumes on left (-X), right (+X), and rear (-Y).

    for story in range(3):
        depth = SIDE_DEPTH - story * 0.4  # slight step-back upward
        h = STORY_H
        z_c = z0 + story * STORY_H + h / 2
        # Left side (-X): along full main length
        add_box(
            f"SideChamber_L{story+1}",
            (depth, MAIN_L, h),
            (-MAIN_W / 2 - depth / 2, 0, z_c),
            mat_sandstone,
        )
        # Right side (+X)
        add_box(
            f"SideChamber_R{story+1}",
            (depth, MAIN_L, h),
            (MAIN_W / 2 + depth / 2, 0, z_c),
            mat_sandstone,
        )
        # Rear (-Y)
        rear_w = MAIN_W + 2 * depth
        add_box(
            f"SideChamber_Rear{story+1}",
            (rear_w, depth, h),
            (0, main_y0 - depth / 2, z_c),
            mat_sandstone,
        )

    # Parent empty for side chambers grouping (optional clarity)
    # Skip empties — named meshes are enough.

    # --- Pillars Jachin and Boaz before the porch ---
    # Flanking entrance, just in front of porch (+Y of porch front)
    pillar_y = porch_center_y + PORCH_D / 2 + PILLAR_R + 0.3
    pillar_x_offset = PORCH_W / 2 - 1.5  # inset from porch corners
    shaft_z = z0 + PILLAR_H / 2

    for name, x_sign in (("PillarJachin", -1), ("PillarBoaz", 1)):
        x = x_sign * pillar_x_offset
        add_cylinder(name, PILLAR_R, PILLAR_H, (x, pillar_y, shaft_z), mat_bronze)
        # Capital (slightly larger cylinder / torus-like massing)
        cap_z = z0 + PILLAR_H + CAPITAL_H / 2
        add_cylinder(
            name + "Capital",
            CAPITAL_R,
            CAPITAL_H,
            (x, pillar_y, cap_z),
            mat_bronze,
            vertices=24,
        )
        # Small abacus / top plate
        add_box(
            name + "Abacus",
            (CAPITAL_R * 2.2, CAPITAL_R * 2.2, 0.25),
            (x, pillar_y, z0 + PILLAR_H + CAPITAL_H + 0.125),
            mat_bronze,
        )

    # --- Roof slab (simple flat cedar roof over main + porch) ---
    roof_thick = 0.4
    roof_w = MAIN_W + 0.6
    roof_d = MAIN_L + PORCH_D + 0.4
    roof_cy = foot_center_y  # approx
    # More precise: from main_y0 to porch front
    roof_cy = (main_y0 + main_y1 + PORCH_D) / 2
    add_box(
        "Roof",
        (roof_w, roof_d, roof_thick),
        (0, roof_cy, z0 + MAIN_H + roof_thick / 2),
        mat_roof,
    )

    # --- Court pavement ---
    court_cy = foot_center_y + 5.0  # extend slightly east for altar view
    add_box(
        "Court",
        (COURT_W, COURT_D, 0.15),
        (0, court_cy, 0.075),
        mat_court,
    )

    # --- Bronze altar east of porch ---
    altar_y = porch_center_y + PORCH_D / 2 + 8.0
    add_box(
        "Altar",
        (ALTAR_W, ALTAR_D, ALTAR_H),
        (0, altar_y, ALTAR_H / 2),
        mat_bronze,
    )
    # Altar horns (small cubes at corners)
    horn = 0.4
    for sx, sy in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        add_box(
            f"AltarHorn_{sx}_{sy}",
            (horn, horn, horn),
            (
                sx * (ALTAR_W / 2 - horn / 2),
                altar_y + sy * (ALTAR_D / 2 - horn / 2),
                ALTAR_H + horn / 2,
            ),
            mat_bronze,
        )

    # --- World / lighting / camera ---
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
    # Mild sky / horizon gray-blue
    bg.inputs["Color"].default_value = (0.55, 0.62, 0.72, 1.0)
    bg.inputs["Strength"].default_value = 0.85
    wl.new(bg.outputs["Background"], out_w.inputs["Surface"])

    # Sun lamp
    bpy.ops.object.light_add(type="SUN", location=(20, -15, 40))
    sun = bpy.context.active_object
    sun.name = "Sun"
    sun.data.energy = 3.5
    sun.rotation_euler = Euler((math.radians(45), math.radians(15), math.radians(-35)))

    # Soft fill
    bpy.ops.object.light_add(type="AREA", location=(-18, 25, 20))
    fill = bpy.context.active_object
    fill.name = "FillLight"
    fill.data.energy = 400
    fill.data.size = 15
    fill.rotation_euler = Euler((math.radians(60), 0, math.radians(150)))

    # Camera: 3/4 exterior view looking at entrance and facade
    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    cam.name = "Camera"
    # Position southeast-ish looking toward porch (+Y facade)
    cam.location = (28, 42, 22)
    # Aim at porch entrance area
    target = Vector((0, porch_center_y + 2, z0 + MAIN_H * 0.45))
    direction = target - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 35
    bpy.context.scene.camera = cam

    # --- Render settings ---
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.filepath = PREVIEW_PATH
    scene.render.image_settings.file_format = "PNG"

    # Prefer EEVEE; fall back to Cycles
    engine = None
    for candidate in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene.render.engine = candidate
            engine = candidate
            break
        except Exception:
            continue
    if engine is None:
        scene.render.engine = "CYCLES"
        engine = "CYCLES"

    print(f"Using render engine: {engine}")

    if engine == "CYCLES":
        scene.cycles.samples = 64
        scene.cycles.use_denoising = True
        try:
            scene.cycles.device = "CPU"
        except Exception:
            pass
    else:
        # EEVEE settings (4.x)
        if hasattr(scene, "eevee"):
            ee = scene.eevee
            if hasattr(ee, "taa_render_samples"):
                ee.taa_render_samples = 64
            if hasattr(ee, "use_gtao"):
                ee.use_gtao = True

    # Save blend
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print(f"Saved: {BLEND_PATH}")

    # Render preview
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {PREVIEW_PATH}")

    # List objects for log
    print("Objects:")
    for obj in bpy.data.objects:
        print(f"  - {obj.name} ({obj.type})")


if __name__ == "__main__":
    build()
