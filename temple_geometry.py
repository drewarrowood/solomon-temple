"""
Solomon's Temple (First Temple) — shared geometry spec.

Scale: 1 cubit = 0.5 m. Coordinates are Blender-style (Z-up):
  +Y entrance / porch (east-ish), −Y Holy of Holies (west/rear), +X south.

This is a readable reconstruction from 1 Kings 6 and 2 Chronicles 3–4,
not an archaeological claim.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

CUBIT = 0.5

# House: 60 × 20 × 30 cubits (1 Kings 6:2)
MAIN_L = 60 * CUBIT
MAIN_W = 20 * CUBIT
MAIN_H = 30 * CUBIT

# Porch / ulam: 20 wide × 10 deep (1 Kings 6:3). Height follows the 30-cubit house
# rather than the 120-cubit figure in 2 Chron 3:4 (often treated as a textual issue).
PORCH_W = 20 * CUBIT
PORCH_D = 10 * CUBIT
PORCH_H = 30 * CUBIT

DEBIT_L = 20 * CUBIT
DEBIT_W = 20 * CUBIT
DEBIT_H = 20 * CUBIT

HEKAL_L = 40 * CUBIT
HEKAL_W = 20 * CUBIT
HEKAL_H = 30 * CUBIT

# 1 Kings 6:6, 6:10 — breadth 5 / 6 / 7 cubits; we also use those as story heights
# (a common reading of the “five cubits high” chambers + the 5/6/7 progression).
STORY_HEIGHTS = (5 * CUBIT, 6 * CUBIT, 7 * CUBIT)
STORY_DEPTHS = (5 * CUBIT, 6 * CUBIT, 7 * CUBIT)
BAY = 5 * CUBIT

# Pillars (1 Kings 7:15–21): 18-cubit shafts; capitals given as 5 cubits.
PILLAR_H = 18 * CUBIT
PILLAR_R = 0.55
CAPITAL_H = 5 * CUBIT * 0.45  # shortened slightly so they do not overpower the porch
CAPITAL_R = 0.88

FOUND_H = 1.5
FOUND_PAD = 3.0

COURT_W = 52.0
COURT_D = 62.0

# 2 Chron 4:1 — 20 × 20 × 10 cubits; height reduced for readable court composition.
ALTAR_W = 20 * CUBIT
ALTAR_D = 20 * CUBIT
ALTAR_H = 2.2

WALL = 0.48
DOOR_W = 4.0
DOOR_H = 8.0

Vec3 = Tuple[float, float, float]


@dataclass
class Material:
    name: str
    color: Tuple[float, float, float]
    roughness: float = 0.55
    metallic: float = 0.0
    alpha: float = 1.0
    emissive: Tuple[float, float, float] = (0.0, 0.0, 0.0)


@dataclass
class Prim:
    kind: str
    name: str
    material: str
    location: Vec3
    rotation: Vec3 = (0.0, 0.0, 0.0)
    size: Optional[Vec3] = None
    radius: float = 0.0
    height: float = 0.0
    segments: int = 28
    extras: Dict[str, object] = field(default_factory=dict)


@dataclass
class Label:
    id: str
    name: str
    position: Vec3  # Blender / Z-up
    note: str = ""


MATERIALS: Dict[str, Material] = {
    "Limestone": Material("Limestone", (0.82, 0.76, 0.62), roughness=0.68),
    "Sandstone": Material("Sandstone", (0.72, 0.62, 0.48), roughness=0.72),
    "FoundationStone": Material("FoundationStone", (0.34, 0.31, 0.27), roughness=0.88),
    "Bronze": Material("Bronze", (0.55, 0.35, 0.12), roughness=0.32, metallic=0.86),
    "CedarWood": Material("CedarWood", (0.45, 0.28, 0.14), roughness=0.56),
    "RoofCedar": Material("RoofCedar", (0.36, 0.20, 0.11), roughness=0.62),
    "CourtStone": Material("CourtStone", (0.54, 0.51, 0.47), roughness=0.92),
    "InnerCedar": Material("InnerCedar", (0.52, 0.34, 0.18), roughness=0.5),
    "InnerGold": Material("InnerGold", (0.78, 0.62, 0.28), roughness=0.28, metallic=0.55),
    "Gold": Material("Gold", (0.86, 0.68, 0.22), roughness=0.22, metallic=0.92),
    "Veil": Material("Veil", (0.42, 0.10, 0.28), roughness=0.45, alpha=0.52),
    "Water": Material("Water", (0.18, 0.32, 0.46), roughness=0.12, metallic=0.35),
    "Flame": Material("Flame", (0.95, 0.42, 0.08), roughness=0.4, emissive=(0.85, 0.28, 0.04)),
    "LampFlame": Material("LampFlame", (1.0, 0.78, 0.35), roughness=0.35, emissive=(0.7, 0.45, 0.12)),
    "HornIvory": Material("HornIvory", (0.86, 0.80, 0.62), roughness=0.45),
}


class Scene:
    def __init__(self) -> None:
        self.prims: List[Prim] = []
        self.labels: List[Label] = []

    def box(
        self,
        name: str,
        size: Vec3,
        location: Vec3,
        material: str,
        rotation: Vec3 = (0.0, 0.0, 0.0),
        **extras: object,
    ) -> Prim:
        prim = Prim(
            kind="box",
            name=name,
            material=material,
            location=location,
            rotation=rotation,
            size=size,
            extras=extras,
        )
        self.prims.append(prim)
        return prim

    def cylinder(
        self,
        name: str,
        radius: float,
        height: float,
        location: Vec3,
        material: str,
        rotation: Vec3 = (0.0, 0.0, 0.0),
        segments: int = 28,
        **extras: object,
    ) -> Prim:
        prim = Prim(
            kind="cylinder",
            name=name,
            material=material,
            location=location,
            rotation=rotation,
            radius=radius,
            height=height,
            segments=segments,
            extras=extras,
        )
        self.prims.append(prim)
        return prim

    def label(self, id_: str, name: str, position: Vec3, note: str = "") -> None:
        self.labels.append(Label(id_, name, position, note))


def blender_to_gltf(v: Vec3) -> List[float]:
    x, y, z = v
    return [round(x, 4), round(z, 4), round(-y, 4)]


def _rot_z(angle: float, offset: Vec3) -> Vec3:
    c, s = math.cos(angle), math.sin(angle)
    x, y, z = offset
    return (x * c - y * s, x * s + y * c, z)


def add_wall_with_opening(
    scene: Scene,
    name: str,
    *,
    center: Vec3,
    size: Vec3,
    material: str,
    axis: str,
    opening_w: float,
    opening_h: float,
    opening_z0: float,
    cutaway: bool = False,
) -> None:
    """Split a wall slab so a rectangular opening is left in the middle."""
    sx, sy, sz = size
    cx, cy, cz = center
    extras = {"cutaway": True} if cutaway else {}
    if axis == "x":
        # Wall in YZ; opening along Y, height Z
        side = (sy - opening_w) / 2
        if side > 0.05:
            scene.box(
                f"{name}_L",
                (sx, side, sz),
                (cx, cy - (opening_w + side) / 2, cz),
                material,
                **extras,
            )
            scene.box(
                f"{name}_R",
                (sx, side, sz),
                (cx, cy + (opening_w + side) / 2, cz),
                material,
                **extras,
            )
        wall_top = cz + sz / 2
        opening_top = opening_z0 + opening_h
        lintel_h = wall_top - opening_top
        if lintel_h > 0.08:
            scene.box(
                f"{name}_Lintel",
                (sx, opening_w + 0.02, lintel_h),
                (cx, cy, opening_top + lintel_h / 2),
                material,
                **extras,
            )
        sill = opening_z0 - (cz - sz / 2)
        if sill > 0.08:
            scene.box(
                f"{name}_Sill",
                (sx, opening_w + 0.02, sill),
                (cx, cy, cz - sz / 2 + sill / 2),
                material,
                **extras,
            )
    else:
        # Wall in XZ; opening along X
        side = (sx - opening_w) / 2
        if side > 0.05:
            scene.box(
                f"{name}_L",
                (side, sy, sz),
                (cx - (opening_w + side) / 2, cy, cz),
                material,
                **extras,
            )
            scene.box(
                f"{name}_R",
                (side, sy, sz),
                (cx + (opening_w + side) / 2, cy, cz),
                material,
                **extras,
            )
        wall_top = cz + sz / 2
        opening_top = opening_z0 + opening_h
        lintel_h = wall_top - opening_top
        if lintel_h > 0.08:
            scene.box(
                f"{name}_Lintel",
                (opening_w + 0.02, sy, lintel_h),
                (cx, cy, opening_top + lintel_h / 2),
                material,
                **extras,
            )


def add_open_doors(
    scene: Scene,
    prefix: str,
    *,
    hinge_y: float,
    z0: float,
    door_w: float,
    door_h: float,
    leaf_t: float = 0.1,
    swing: float = math.radians(55),
    material: str = "CedarWood",
    cutaway: bool = False,
) -> None:
    extras = {"cutaway": False}
    leaf_w = door_w / 2 - 0.04
    for side, sign in (("L", -1), ("R", 1)):
        angle = sign * swing
        # Leaf rests in the XY plane, thin in Y; hinge at ±door_w/2.
        hx = sign * (door_w / 2)
        local = (sign * (-leaf_w / 2), 0.0, 0.0)
        ox, oy, _ = _rot_z(angle, local)
        scene.box(
            f"{prefix}_{side}",
            (leaf_w, leaf_t, door_h),
            (hx + ox, hinge_y + oy, z0 + door_h / 2),
            material,
            rotation=(0.0, 0.0, angle),
            **extras,
        )


def add_menorah(scene: Scene, name: str, x: float, y: float, z0: float) -> None:
    """Stylized seven-branch lampstand (not a museum replica)."""
    scene.cylinder(f"{name}_Base", 0.20, 0.07, (x, y, z0 + 0.04), "Gold", segments=20)
    scene.cylinder(f"{name}_Foot", 0.10, 0.10, (x, y, z0 + 0.12), "Gold", segments=16)
    shaft_h = 1.28
    scene.cylinder(f"{name}_Shaft", 0.038, shaft_h, (x, y, z0 + 0.17 + shaft_h / 2), "Gold", segments=14)
    # Crossbar + 7 stems in the YZ plane so they read from a +X cutaway.
    bar_y = 0.86
    scene.box(f"{name}_Bar", (0.05, bar_y, 0.045), (x, y, z0 + 1.22), "Gold")
    spacing = 0.14
    for i in range(7):
        oy = (i - 3) * spacing
        stem_h = 0.28
        scene.cylinder(
            f"{name}_Stem{i}",
            0.018,
            stem_h,
            (x, y + oy, z0 + 1.22 + stem_h / 2),
            "Gold",
            segments=10,
        )
        scene.cylinder(
            f"{name}_Cup{i}",
            0.032,
            0.05,
            (x, y + oy, z0 + 1.50),
            "Gold",
            segments=10,
        )
        scene.cylinder(
            f"{name}_Flame{i}",
            0.012,
            0.06,
            (x, y + oy, z0 + 1.56),
            "LampFlame",
            segments=8,
        )


def add_cherub(scene: Scene, name: str, x: float, y: float, z0: float, face: float) -> None:
    """Large winged guardian (10 cubits high). Angular, not figurative/Disney."""
    body_h = 3.55
    scene.box(f"{name}_Body", (0.72, 0.58, body_h), (x, y, z0 + body_h / 2), "Gold")
    scene.box(f"{name}_Head", (0.42, 0.38, 0.62), (x, y, z0 + body_h + 0.38), "Gold")
    # Shoulders / pectoral block
    scene.box(f"{name}_Shoulder", (1.05, 0.42, 0.38), (x, y, z0 + 3.15), "Gold")
    # Wings: 5 cubits each (2.5 m), inner wings meet over the ark.
    wing_w = 2.45
    wing_t = 0.10
    wing_h = 1.35
    wing_z = z0 + 3.55
    # face: +1 means inner wing toward +X (cherub on −X side)
    inner_x = x + face * (0.42 + wing_w / 2)
    outer_x = x - face * (0.42 + wing_w / 2)
    tilt = math.radians(12)
    scene.box(
        f"{name}_WingInner",
        (wing_w, wing_t, wing_h),
        (inner_x, y, wing_z),
        "Gold",
        rotation=(0.0, -face * tilt, 0.0),
    )
    scene.box(
        f"{name}_WingOuter",
        (wing_w, wing_t, wing_h),
        (outer_x, y, wing_z),
        "Gold",
        rotation=(0.0, face * tilt, 0.0),
    )


def add_ox(scene: Scene, name: str, x: float, y: float, z: float, yaw: float) -> None:
    """Very simple ox: body, head, legs, horns. Yaw is Blender Z rotation."""
    def put(local: Vec3) -> Vec3:
        rx, ry, rz = _rot_z(yaw, local)
        return (x + rx, y + ry, z + rz)

    scene.box(f"{name}_Body", (0.42, 0.85, 0.48), put((0.0, 0.0, 0.52)), "Bronze", rotation=(0, 0, yaw))
    scene.box(f"{name}_Head", (0.32, 0.34, 0.28), put((0.0, 0.52, 0.62)), "Bronze", rotation=(0, 0, yaw))
    for i, (lx, ly) in enumerate(((-0.14, 0.26), (0.14, 0.26), (-0.14, -0.26), (0.14, -0.26))):
        p = put((lx, ly, 0.18))
        scene.cylinder(f"{name}_Leg{i}", 0.055, 0.34, p, "Bronze", segments=8)
    for i, hx in enumerate((-0.1, 0.1)):
        p = put((hx, 0.58, 0.82))
        scene.cylinder(
            f"{name}_Horn{i}",
            0.03,
            0.22,
            p,
            "HornIvory",
            rotation=(math.radians(18), 0.0, yaw),
            segments=8,
        )


def build_scene() -> Scene:
    scene = Scene()
    z0 = FOUND_H
    main_y0 = -MAIN_L / 2
    main_y1 = MAIN_L / 2
    debit_center_y = main_y0 + DEBIT_L / 2
    hekal_center_y = main_y0 + DEBIT_L + HEKAL_L / 2
    porch_center_y = main_y1 + PORCH_D / 2
    porch_front = main_y1 + PORCH_D
    foot_center_y = (main_y0 + porch_front) / 2

    # --- Court & foundation -------------------------------------------------
    scene.box(
        "Court",
        (COURT_W, COURT_D, 0.14),
        (0.0, foot_center_y + 4.0, 0.07),
        "CourtStone",
    )
    foot_w = MAIN_W + 2 * STORY_DEPTHS[-1] + 2 * FOUND_PAD
    foot_d = MAIN_L + PORCH_D + 2 * FOUND_PAD
    scene.box(
        "Foundation",
        (foot_w, foot_d, FOUND_H),
        (0.0, foot_center_y, FOUND_H / 2),
        "FoundationStone",
    )
    # Two shallow steps up to the porch
    scene.box(
        "PorchStep1",
        (PORCH_W + 1.4, 1.3, 0.28),
        (0.0, porch_front + 0.85, 0.14),
        "Sandstone",
    )
    scene.box(
        "PorchStep2",
        (PORCH_W + 0.6, 1.0, 0.28),
        (0.0, porch_front + 0.15, 0.42),
        "Sandstone",
    )

    # --- Holy of Holies (debir) — hollow 20-cubit cube, walls to roof -------
    dw, dd, dh = DEBIT_W, DEBIT_L, MAIN_H
    dcy = debit_center_y
    scene.box(
        "HolyOfHolies_Floor",
        (dw - WALL * 2, dd - WALL * 2, 0.12),
        (0.0, dcy, z0 + 0.06),
        "InnerGold",
    )
    scene.box(
        "HolyOfHolies_Ceiling",
        (dw - WALL * 1.2, dd - WALL * 1.2, 0.18),
        (0.0, dcy, z0 + DEBIT_H + 0.09),
        "InnerGold",
    )
    # Rear (−Y)
    scene.box(
        "HolyOfHolies_WallNegY",
        (dw, WALL, dh),
        (0.0, main_y0 + WALL / 2, z0 + dh / 2),
        "Limestone",
    )
    # North (−X)
    scene.box(
        "HolyOfHolies_WallNegX",
        (WALL, dd, dh),
        (-dw / 2 + WALL / 2, dcy, z0 + dh / 2),
        "InnerCedar",
    )
    # South (+X) — tagged for cutaway
    scene.box(
        "HolyOfHolies_WallPosX",
        (WALL, dd, dh),
        (dw / 2 - WALL / 2, dcy, z0 + dh / 2),
        "InnerCedar",
        cutaway=True,
    )
    # Partition toward hekal (+Y of debir) with a wide veiled opening
    add_wall_with_opening(
        scene,
        "HolyOfHolies_WallPosY",
        center=(0.0, main_y0 + DEBIT_L - WALL / 2, z0 + dh / 2),
        size=(dw, WALL, dh),
        material="InnerCedar",
        axis="y",
        opening_w=6.2,
        opening_h=8.2,
        opening_z0=z0,
    )
    scene.box(
        "Veil",
        (5.8, 0.06, 8.0),
        (0.0, main_y0 + DEBIT_L - WALL - 0.08, z0 + 4.1),
        "Veil",
    )

    # --- Holy Place (hekal) -------------------------------------------------
    hw, hd, hh = HEKAL_W, HEKAL_L, HEKAL_H
    hcy = hekal_center_y
    scene.box(
        "HolyPlace_Floor",
        (hw - WALL * 2, hd - WALL, 0.12),
        (0.0, hcy, z0 + 0.06),
        "InnerCedar",
    )
    scene.box(
        "HolyPlace_Ceiling",
        (hw - 0.2, hd - 0.15, 0.2),
        (0.0, hcy, z0 + hh - 0.1),
        "RoofCedar",
        roof=True,
    )
    scene.box(
        "HolyPlace_WallNegX",
        (WALL, hd, hh),
        (-hw / 2 + WALL / 2, hcy, z0 + hh / 2),
        "InnerCedar",
    )
    scene.box(
        "HolyPlace_WallPosX",
        (WALL, hd, hh),
        (hw / 2 - WALL / 2, hcy, z0 + hh / 2),
        "InnerCedar",
        cutaway=True,
    )
    add_wall_with_opening(
        scene,
        "HolyPlace_WallPosY",
        center=(0.0, main_y1 - WALL / 2, z0 + hh / 2),
        size=(hw, WALL, hh),
        material="Limestone",
        axis="y",
        opening_w=DOOR_W + 0.3,
        opening_h=DOOR_H,
        opening_z0=z0,
    )

    # --- Porch (ulam) -------------------------------------------------------
    pw, pd, ph = PORCH_W, PORCH_D, PORCH_H
    pcy = porch_center_y
    scene.box(
        "Porch_Floor",
        (pw - 0.15, pd - 0.1, 0.12),
        (0.0, pcy, z0 + 0.06),
        "Sandstone",
    )
    scene.box(
        "Porch_WallNegX",
        (WALL, pd, ph),
        (-pw / 2 + WALL / 2, pcy, z0 + ph / 2),
        "Sandstone",
    )
    scene.box(
        "Porch_WallPosX",
        (WALL, pd, ph),
        (pw / 2 - WALL / 2, pcy, z0 + ph / 2),
        "Sandstone",
        cutaway=True,
    )
    add_wall_with_opening(
        scene,
        "Porch_WallPosY",
        center=(0.0, porch_front - WALL / 2, z0 + ph / 2),
        size=(pw, WALL, ph),
        material="Sandstone",
        axis="y",
        opening_w=DOOR_W + 0.15,
        opening_h=DOOR_H,
        opening_z0=z0,
    )
    add_open_doors(
        scene,
        "EntranceDoor",
        hinge_y=porch_front - WALL - 0.02,
        z0=z0,
        door_w=DOOR_W,
        door_h=DOOR_H,
        swing=math.radians(58),
    )
    add_open_doors(
        scene,
        "HekalDoor",
        hinge_y=main_y1 - WALL - 0.05,
        z0=z0,
        door_w=DOOR_W - 0.2,
        door_h=DOOR_H - 0.4,
        swing=math.radians(70),
        material="CedarWood",
    )

    # --- Side chambers: bays on both long sides and the rear ----------------
    n_side = int(round(MAIN_L / BAY))
    bay_span = MAIN_L / n_side
    n_rear = int(round(MAIN_W / BAY))
    rear_span = MAIN_W / n_rear
    gap = 0.08
    z_story = z0
    for story, (sh, depth) in enumerate(zip(STORY_HEIGHTS, STORY_DEPTHS), start=1):
        zc = z_story + sh / 2
        for i in range(n_side):
            by = main_y0 + (i + 0.5) * bay_span
            blen = bay_span - gap
            for side, sx, cut in (
                ("L", -1.0, False),
                ("R", 1.0, True),
            ):
                cx = sx * (MAIN_W / 2 + depth / 2)
                scene.box(
                    f"SideChamber_{side}{story}_B{i+1:02d}",
                    (depth, blen, sh - 0.04),
                    (cx, by, zc),
                    "Sandstone",
                    cutaway=cut,
                )
                if story == 1:
                    scene.box(
                        f"SideChamberDoor_{side}{story}_B{i+1:02d}",
                        (0.06, 0.55, 1.35),
                        (sx * (MAIN_W / 2 + depth - 0.03), by, z0 + 0.72),
                        "CedarWood",
                        cutaway=cut,
                    )
        for i in range(n_rear):
            bx = -MAIN_W / 2 + (i + 0.5) * rear_span
            scene.box(
                f"SideChamber_Rear{story}_B{i+1:02d}",
                (rear_span - gap, depth, sh - 0.04),
                (bx, main_y0 - depth / 2, zc),
                "Sandstone",
            )
        z_story += sh

    # Winding-stair hint on the south / right side (1 Kings 6:8)
    stair_x = MAIN_W / 2 + STORY_DEPTHS[0] + 0.85
    stair_y = main_y1 - 2.4
    scene.box("StairTower", (1.6, 1.6, 9.1), (stair_x, stair_y, z0 + 4.55), "Sandstone", cutaway=True)
    for i in range(14):
        ang = -i * (math.pi / 3.2)
        r = 0.42
        scene.box(
            f"StairStep_{i+1:02d}",
            (0.55, 0.28, 0.16),
            (stair_x + r * math.cos(ang), stair_y + r * math.sin(ang), z0 + 0.22 + i * 0.58),
            "CedarWood",
            rotation=(0.0, 0.0, ang),
            cutaway=True,
        )

    # --- Roof ---------------------------------------------------------------
    roof_t = 0.38
    scene.box(
        "Roof",
        (MAIN_W + 0.7, MAIN_L + PORCH_D + 0.5, roof_t),
        (0.0, foot_center_y, z0 + MAIN_H + roof_t / 2),
        "RoofCedar",
        roof=True,
    )

    # --- Jachin (south / +X) and Boaz (north / −X) — 1 Kings 7:21 ----------
    pillar_y = porch_front + PILLAR_R + 0.35
    pillar_x = PORCH_W / 2 - 1.45
    for name, x in (("PillarJachin", pillar_x), ("PillarBoaz", -pillar_x)):
        scene.cylinder(name, PILLAR_R, PILLAR_H, (x, pillar_y, z0 + PILLAR_H / 2), "Bronze")
        scene.cylinder(
            f"{name}Capital",
            CAPITAL_R,
            CAPITAL_H,
            (x, pillar_y, z0 + PILLAR_H + CAPITAL_H / 2),
            "Bronze",
            segments=24,
        )
        # Lily-work hint: a second slightly wider ring
        scene.cylinder(
            f"{name}Lily",
            CAPITAL_R + 0.12,
            0.22,
            (x, pillar_y, z0 + PILLAR_H + 0.18),
            "Bronze",
            segments=20,
        )
        scene.box(
            f"{name}Abacus",
            (CAPITAL_R * 2.15, CAPITAL_R * 2.15, 0.22),
            (x, pillar_y, z0 + PILLAR_H + CAPITAL_H + 0.11),
            "Bronze",
        )

    # --- Furnishings: Holy of Holies ----------------------------------------
    ark_h = 1.5 * CUBIT
    ark_w = 1.5 * CUBIT
    ark_l = 2.5 * CUBIT
    scene.box("Ark", (ark_l, ark_w, ark_h), (0.0, dcy, z0 + ark_h / 2 + 0.08), "Gold")
    scene.box(
        "ArkMercySeat",
        (ark_l + 0.06, ark_w + 0.06, 0.07),
        (0.0, dcy, z0 + ark_h + 0.12),
        "Gold",
    )
    # Poles left in the rings (Exodus 25:15)
    scene.cylinder(
        "ArkPoleL",
        0.04,
        3.4,
        (-1.15, dcy, z0 + ark_h * 0.55),
        "CedarWood",
        rotation=(math.pi / 2, 0.0, 0.0),
        segments=10,
    )
    scene.cylinder(
        "ArkPoleR",
        0.04,
        3.4,
        (1.15, dcy, z0 + ark_h * 0.55),
        "CedarWood",
        rotation=(math.pi / 2, 0.0, 0.0),
        segments=10,
    )
    # Small lid cherubim (distinct from the large standing pair)
    for side, sx in (("L", -1), ("R", 1)):
        scene.box(
            f"ArkCherub_{side}",
            (0.22, 0.16, 0.32),
            (sx * 0.28, dcy, z0 + ark_h + 0.34),
            "Gold",
        )
        scene.box(
            f"ArkCherubWing_{side}",
            (0.38, 0.05, 0.22),
            (sx * 0.48, dcy, z0 + ark_h + 0.42),
            "Gold",
            rotation=(0.0, sx * math.radians(-25), 0.0),
        )

    add_cherub(scene, "CherubNorth", -2.15, dcy, z0, face=+1.0)
    add_cherub(scene, "CherubSouth", 2.15, dcy, z0, face=-1.0)

    # --- Furnishings: Holy Place --------------------------------------------
    incense_y = main_y0 + DEBIT_L + 1.7
    scene.box("IncenseAltar", (1.05, 1.05, 1.55), (0.0, incense_y, z0 + 0.82), "Gold")
    scene.box("IncenseAltarTop", (1.15, 1.15, 0.08), (0.0, incense_y, z0 + 1.62), "Gold")
    scene.cylinder("IncenseSmoke", 0.05, 0.18, (0.0, incense_y, z0 + 1.78), "LampFlame", segments=8)

    table_x, table_y = -2.55, hekal_center_y + 2.0
    scene.box("ShowbreadTable", (1.15, 2.15, 0.12), (table_x, table_y, z0 + 0.92), "Gold")
    for i, (lx, ly) in enumerate(((-0.4, -0.85), (0.4, -0.85), (-0.4, 0.85), (0.4, 0.85))):
        scene.cylinder(
            f"ShowbreadLeg{i}",
            0.05,
            0.86,
            (table_x + lx, table_y + ly, z0 + 0.45),
            "Gold",
            segments=8,
        )
    # Twelve loaves in two rows (stylized)
    for row in range(2):
        for col in range(6):
            scene.box(
                f"Showbread_{row}_{col}",
                (0.16, 0.22, 0.07),
                (
                    table_x - 0.18 + row * 0.36,
                    table_y - 0.85 + col * 0.34,
                    z0 + 1.02,
                ),
                "HornIvory",
            )

    # Ten lampstands: five north, five south (2 Chron 4:7)
    for side, sx in (("N", -1.0), ("S", 1.0)):
        for i in range(5):
            yy = main_y0 + DEBIT_L + 2.6 + i * 3.3
            add_menorah(scene, f"Lampstand_{side}{i+1}", sx * 3.15, yy, z0)

    # --- Court: bronze altar with horns -------------------------------------
    altar_y = porch_front + 9.2
    scene.box("Altar", (ALTAR_W, ALTAR_D, ALTAR_H), (0.0, altar_y, ALTAR_H / 2), "Bronze")
    scene.box(
        "AltarHearth",
        (ALTAR_W - 1.4, ALTAR_D - 1.4, 0.18),
        (0.0, altar_y, ALTAR_H + 0.05),
        "FoundationStone",
    )
    scene.box("AltarFlame", (1.6, 1.6, 0.55), (0.0, altar_y, ALTAR_H + 0.42), "Flame")
    horn = 0.42
    for sx, sy in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        scene.box(
            f"AltarHorn_{sx}_{sy}",
            (horn, horn, horn + 0.15),
            (
                sx * (ALTAR_W / 2 - horn / 2),
                altar_y + sy * (ALTAR_D / 2 - horn / 2),
                ALTAR_H + horn / 2 + 0.08,
            ),
            "Bronze",
        )

    # --- Bronze Sea / molten sea on twelve oxen (1 Kings 7:23–25, 39) -------
    # “On the right side of the house eastward, over against the south.”
    sea_r = 5 * CUBIT
    sea_h = 5 * CUBIT
    sea_x, sea_y = 13.2, porch_front + 3.6
    ox_z = 0.0
    for i, (deg, yaw) in enumerate(
        (
            # three east (+Y), south (+X), west (−Y), north (−X)
            (20, 0.0),
            (40, 0.0),
            (60, 0.0),
            (110, math.radians(90)),
            (130, math.radians(90)),
            (150, math.radians(90)),
            (200, math.pi),
            (220, math.pi),
            (240, math.pi),
            (290, math.radians(-90)),
            (310, math.radians(-90)),
            (330, math.radians(-90)),
        )
    ):
        ang = math.radians(deg)
        r = sea_r + 0.15
        add_ox(
            scene,
            f"SeaOx_{i+1:02d}",
            sea_x + r * math.sin(ang),
            sea_y + r * math.cos(ang),
            ox_z,
            yaw,
        )
    scene.cylinder("BronzeSea", sea_r, sea_h * 0.55, (sea_x, sea_y, 1.15 + sea_h * 0.22), "Bronze", segments=40)
    scene.cylinder("BronzeSeaRim", sea_r + 0.12, 0.16, (sea_x, sea_y, 1.15 + sea_h * 0.48), "Bronze", segments=40)
    scene.cylinder("BronzeSeaWater", sea_r - 0.12, 0.12, (sea_x, sea_y, 1.15 + sea_h * 0.42), "Water", segments=32)

    # Ten lavers, five per side (2 Chron 4:6) — small court basins
    for i in range(5):
        yy = porch_center_y - 4.0 - i * 3.6
        scene.cylinder(f"Laver_S{i+1}", 0.55, 0.45, (11.5, yy, 0.55), "Bronze", segments=16)
        scene.box(f"LaverStand_S{i+1}", (0.7, 0.7, 0.35), (11.5, yy, 0.22), "Bronze")
        scene.cylinder(f"Laver_N{i+1}", 0.55, 0.45, (-11.5, yy, 0.55), "Bronze", segments=16)
        scene.box(f"LaverStand_N{i+1}", (0.7, 0.7, 0.35), (-11.5, yy, 0.22), "Bronze")

    # --- Labels -------------------------------------------------------------
    scene.label("ulam", "Porch (Ulam)", (0.0, pcy, z0 + ph + 1.2), "Entrance hall, 20 × 10 cubits")
    scene.label("hekal", "Holy Place (Hekal)", (0.0, hcy, z0 + hh + 1.4), "Nave, 40 × 20 × 30 cubits")
    scene.label("debir", "Holy of Holies (Debir)", (0.0, dcy, z0 + MAIN_H + 1.6), "Inner sanctuary, 20-cubit cube")
    scene.label("jachin", "Jachin", (pillar_x, pillar_y, z0 + PILLAR_H + CAPITAL_H + 1.4), "South pillar")
    scene.label("boaz", "Boaz", (-pillar_x, pillar_y, z0 + PILLAR_H + CAPITAL_H + 1.4), "North pillar")
    scene.label("altar", "Bronze Altar", (0.0, altar_y, ALTAR_H + 1.6), "Burnt offering altar (height reduced)")
    scene.label("sea", "Bronze Sea", (sea_x, sea_y, 3.6), "Molten sea on twelve oxen")
    scene.label("chambers", "Side Chambers", (-MAIN_W / 2 - 3.2, 0.0, z0 + 10.2), "Three stories, 5 / 6 / 7 cubits")

    return scene


def labels_as_json(labels: Iterable[Label]) -> List[dict]:
    return [
        {
            "id": lab.id,
            "name": lab.name,
            "note": lab.note,
            "position": blender_to_gltf(lab.position),
        }
        for lab in labels
    ]


def extras_for(prim: Prim) -> Dict[str, object]:
    data = dict(prim.extras)
    data["kind"] = prim.kind
    return data
