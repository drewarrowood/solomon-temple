# Solomon’s Temple (First Temple)

A readable 3D reconstruction of King Solomon’s Temple for orbiting and study — not a game-asset dump, and **not an archaeological claim**.

**Live viewer:** [https://drewarrowood.github.io/solomon-temple/](https://drewarrowood.github.io/solomon-temple/)

The browser viewer loads a glTF model, with orbit controls, a cutaway so the Holy Place and Holy of Holies can be read, and labels for the porch, nave, inner sanctuary, pillars Jachin and Boaz, and the bronze altar.

## Sources

- **1 Kings 6** — house, porch (ulam), Holy Place (hekal), inner sanctuary / Holy of Holies (debir), side chambers, doors
- **1 Kings 7:15–51** — pillars Jachin and Boaz, bronze sea and oxen, stands and basins, furnishings
- **2 Chronicles 3–4** — porch tradition, veil, ten lampstands, bronze altar, ten lavers

Biblical measures are architectural traditions preserved in the text. Later commentators disagree on cubit length, porch height, chamber offsets, and how the furnishings were arranged. This model chooses one internally consistent, *readable* set of decisions.

## Scale

| Unit | Value |
|------|-------|
| 1 cubit | **0.5 meters** (chosen for clean units) |
| Model unit | 1 meter |

### Key dimensions (meters)

| Element | Cubits | Meters |
|---------|--------|--------|
| Main building (nave + sanctuary) | 60 × 20 × 30 | 30 × 10 × 15 |
| Porch (ulam) | 20 wide × 10 deep × ~30 high | 10 × 5 × 15 |
| Holy of Holies (debir) | 20 × 20 × 20 | 10 × 10 × 10 |
| Holy Place (hekal) | 40 × 20 × 30 | 20 × 10 × 15 |
| Side-chamber stories | 5 / 6 / 7 high and broad | 2.5 / 3.0 / 3.5 |
| Pillar shafts | ~18 tall | ~9 |
| Bronze sea | 10 diameter × 5 high | 5 × 2.5 |
| Bronze altar (text) | 20 × 20 × 10 | 10 × 10 × 5 |

## Orientation

- Entrance / porch faces **+Y** (east-ish for viewing)
- Holy of Holies at **−Y** (rear / west)
- South is **+X** (Jachin); north is **−X** (Boaz) — 1 Kings 7:21
- Origin at ground center of the main footprint (before the foundation raise)

glTF / the browser viewer use Y-up: Blender `(x, y, z)` becomes `(x, z, −y)`.

## What is in the model

Named objects (Blender and glTF) include:

| Group | Role |
|-------|------|
| `Foundation`, `Court`, `PorchStep*` | Raised platform and courtyard pavement |
| `Porch_*`, `EntranceDoor_*` | Ulam, open cedar leaves |
| `HolyPlace_*`, `HekalDoor_*` | Hekal walls, floor, ceiling, doors |
| `HolyOfHolies_*`, `Veil` | Debir volume and the veil before it |
| `SideChamber_{L\|R\|Rear}{story}_B##` | Individual bays, three stories, both long sides and the rear |
| `StairTower`, `StairStep_*` | Winding-stair hint on the south side (1 Kings 6:8) |
| `PillarJachin` / `PillarBoaz` (+ Capital, Lily, Abacus) | Bronze pillars |
| `Roof` | Cedar roof slab (toggle in the viewer) |
| `Ark`, `ArkMercySeat`, `ArkPole*`, `ArkCherub_*` | Ark of the Covenant |
| `CherubNorth` / `CherubSouth` | Large 10-cubit winged forms over the ark |
| `Lampstand_{N\|S}1–5` | Ten menorahs in the Holy Place |
| `ShowbreadTable`, `Showbread_*` | Table and twelve loaves |
| `IncenseAltar` | Gold incense altar before the veil |
| `Altar`, `AltarHorn_*` | Court altar with horns |
| `BronzeSea`, `SeaOx_*` | Molten sea on twelve oxen |
| `Laver_*` | Ten side basins |

The viewer’s **Cutaway** control hides the south (+X) long wall, south chambers, and stair so the interiors can be read. Turn it off for a closed exterior.

## Local rebuild

The same geometry spec (`temple_geometry.py`) drives both paths.

```bash
# Without Blender (writes the web model)
python3 build_temple.py

# With Blender 4.x (blend + preview PNG + glTF)
blender --background --python build_temple.py
```

Outputs:

- `docs/models/solomon_temple.glb` — glTF 2.0 binary for the viewer
- `docs/labels.json` — floating labels (Three.js Y-up)
- `solomon_temple.blend` / `preview.png` — only when Blender is available

## Local viewer

The site is static. Serve the `docs/` folder (module imports and the `.glb` will not load from `file://`):

```bash
python3 -m http.server 8080 --directory docs
```

Then open [http://localhost:8080/](http://localhost:8080/).

Dependencies are CDN Three.js (r170) plus OrbitControls / GLTFLoader / CSS2DRenderer. No build step.

## GitHub Pages

The live site is published from `docs/` to

**https://drewarrowood.github.io/solomon-temple/**

Two equivalent ways to keep it live:

1. **GitHub Actions** (this repo’s default): `.github/workflows/pages.yml` deploys `docs/` on every push to `main` using `actions/deploy-pages`. In the repository settings, set Pages source to **GitHub Actions**. The first run after that setting is enabled publishes the site.
2. **Branch folder:** Settings → Pages → Deploy from a branch → `main` / `/docs`.

## Approximations

- Cubit length is a round 0.5 m for clean modeling, not a claim about the “royal cubit.”
- 2 Chronicles 3:4 gives the porch 120 cubits high; this model keeps it with the 30-cubit house (a widely noted textual tension).
- Side-chamber **heights and breadths** follow the 5 / 6 / 7 cubit progression. The house wall’s “narrowed rests” (1 Kings 6:6) are implied by upper stories that grow outward; individual rooms, windows, and the winding stair are schematic bays, not a measured floor plan.
- Interiors are hollow, with open doors and a veil, so the two rooms can be read. Wall thickness is a modeling choice (~0.5 m), not a recovered specification.
- The Holy of Holies is a 10 m cube inside; exterior walls continue to the 15 m roof line.
- Large cherubim are 10 cubits high with a 10-cubit wing-spread (1 Kings 6:23–27), drawn as angular winged guardians, not figurative sculpture.
- Ten lampstands follow 2 Chronicles 4:7 (Kings mentions the lampstand in the singular). They are stylized seven-branch forms, not museum replicas.
- The bronze altar’s **height is reduced** (~2.2 m instead of 5 m) so it does not swallow the court in orbit views. Horns are kept.
- The bronze sea sits on twelve oxen, three to each quarter (1 Kings 7:25), south-east of the house (7:39). Oxen are block stand-ins.
- Gold overlay, cedar paneling, and cherub-carved walls are suggested with materials, not carved in relief.
- Flat roof slab rather than detailed cedar beams / paneling.
- No claim is made that this matches any particular reconstruction (Wight, Busink, Schmidt, the Temple Institute, etc.).
