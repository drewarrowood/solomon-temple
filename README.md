# Solomon's Temple (First Temple) — Blender Model

A clean, historically-informed massing model of King Solomon's Temple for orbiting and study — not a game-asset dump.

## Sources

- **1 Kings 6** — primary dimensions of the house, porch (ulam), Holy Place (hekal), inner sanctuary / Holy of Holies (debir), side chambers, and the pillars Jachin and Boaz
- **2 Chronicles 3–4** — porch height tradition, bronze altar, pillar details

Biblical measures are approximate architectural traditions; this model is a readable reconstruction, not an archaeological claim.

## Scale

| Unit | Value |
|------|-------|
| 1 cubit | **0.5 meters** (chosen for clean Blender units) |
| Blender unit | 1 meter |

### Key dimensions (meters)

| Element | Cubits | Meters |
|---------|--------|--------|
| Main building (nave + sanctuary) | 60 × 20 × 30 | 30 × 10 × 15 |
| Porch (ulam) | 20 wide × 10 deep × ~30 high | 10 × 5 × 15 |
| Holy of Holies (debir) | 20 × 20 × 20 | 10 × 10 × 10 |
| Holy Place (hekal) | 40 × 20 × 30 | 20 × 10 × 15 |
| Side chambers depth | ~5 | ~2.5 |
| Pillar shafts | ~18 tall | ~9 |

## Orientation

- Entrance / porch faces **+Y** (east-ish for viewing)
- Holy of Holies at **−Y** (rear / west)
- Origin at ground center of the main footprint (before foundation raise)

## Named objects

| Object | Role |
|--------|------|
| `Foundation` | Raised stone platform |
| `HolyOfHolies` / `HolyOfHoliesUpper` | Debir cube + upper mass to main roof line |
| `HolyPlace` | Hekal / nave |
| `Porch` | Ulam |
| `EntranceDoor` | Wood-toned door recess on porch façade |
| `SideChamber_L1–3`, `_R1–3`, `_Rear1–3` | Three-story stepped side/rear chambers |
| `PillarJachin` / `PillarBoaz` (+ Capital, Abacus) | Bronze pillars before the porch |
| `Roof` | Simple cedar flat roof slab |
| `Court` | Courtyard pavement |
| `Altar` (+ `AltarHorn_*`) | Bronze altar east of the porch |
| `Sun`, `FillLight`, `Camera` | Lighting and 3/4 exterior view |

## Materials

Principled BSDF only (no image textures):

- Limestone / sandstone — walls
- Darker stone — foundation
- Bronze/copper — pillars and altar
- Cedar wood tone — door and roof

## Rebuild

```bash
blender --background --python /workspace/solomon-temple/build_temple.py
```

Outputs:

- `solomon_temple.blend`
- `preview.png` (1920×1080 EEVEE, or Cycles fallback)

## Approximations

- Side chambers are simplified as three stepped rectangular volumes on the sides and rear (not individual rooms or staircases). Story heights are equal (~2.5 m) rather than the biblical 5 / 6 / 7 cubit progression.
- Holy of Holies interior is 10 m cube massing; exterior walls continue to the 15 m main roof line via `HolyOfHoliesUpper`.
- Bronze altar height is reduced (~2 m) for composition readability (Chronicles gives 10 cubits / 5 m).
- No interior furnishings (cherubim, lampstands, veils) — exterior-readable architecture only.
- Flat roof slab rather than detailed cedar beams / paneling.
