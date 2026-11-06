# Aemeath identification bake preparation

Prepared for the independent Aemeath A380X project: fictional registration **B-38AM**, unit **AM-01**, nose-door shorthand **AM / 01**. The AM-01 wing and door identifiers have been baked and composited into the final textures. Rebuild their GIMP source images before rerunning these commands.

The script calculates its project root from `Path(__file__).resolve().parents[1]`; it does not point back to Megumin or Air China. The copied NLG caches and node evidence are geometry-only inputs, reused from the same official paintkit/installed model. The new project's front-door report contains only the two FWD door entries actually needed by this bake.

## Required new GIMP sources

- `artwork/projection/wing_registration.png`: 2048×512 transparent RGBA, containing B-38AM and the desired AM-01 / AEMEATH line.
- `artwork/projection/gear_code.png`: transparent RGBA, e.g. 512×128, containing AM / 01.

No old numbered PNG or ink output was copied. Root/parent is separately preparing the geometry-root cache `A380_EXTERIOR_WING1_underside_coordinates_uv.npz`; the two required front-door caches are already in this directory. The identification script does not need the neutral blend.

## Commands after ART_READY

Both ink layers:

```powershell
# Run from the project root. Replace 'blender' with its full executable path if needed.
$BlenderExe = 'blender'
& $BlenderExe -b --factory-startup --python '.\geometry\bake_identification_decals.py' -- --mode both
```

Use `--mode wing` or `--mode door` for one layer. Default `--door-orientation bottom-consistent` makes both closed doors readable in the same underside viewing orientation; `side-readable` is available for the per-side convention, but actual opened-door animation still requires simulator checking.

Outputs are `artwork/baked/wing_registration_ink.png` and `gear_id_ink.png`, each 4096 RGBA with 16px margin. RGB and original source alpha are baked separately; black text is not treated as transparency. sRGB conversion and the independent linear alpha pass are unchanged from the verified geometry workflow.

The wing layout retains the 9×2.25m rotated rectangle at world XY origin (29,6). The door layout retains Y[-33.20,-32.35] and |X|[0.45,0.75] on the selected FUSE1 door skins. New ink colors and glyphs come entirely from the new source PNGs. For the requested clean finish, composite over clean albedo/panel/stencil layers without importing old weathering layers.
