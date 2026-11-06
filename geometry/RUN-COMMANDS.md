# Aemeath A380X geometry pipeline

The geometry/UV caches (`*.npz`) and Blender scenes (`*.blend`) are local external dependencies and are not tracked in this repository. Exporting the thirteen final UV XCFs with `export_from_xcf_gimp.py` does not require them. The commands below describe the optional projection/rendering workflow for a local workspace that already has those paintkit-derived inputs.

Prepared for B-38AM / AM-01. Scripts and geometry are independent copies; Megumin and Air China projects are unchanged. Initial production bake and final PNG rendering are complete. Rebuild projection masters in GIMP before rerunning a bake.

Dependencies: Blender (tested with 5.2.3 LTS), its bundled Python/NumPy, the local `geometry/*.npz`, `engine-wingfence-report.json`, NLG FWD caches in `gear-inspection/`, and `A380X-neutral-preview.blend`. No external Python package install or GPU is required.

All three scripts infer project root from their own file location. Default palette is pearl white `#F2F5FA`, navy `#172340` under the legacy `crimson` key, and deep slate `#101A2F`. `artwork/projection/design-metadata.json` overrides palette values. Horizontal stabilizers use the navy value; FUSE5 uses deep slate. Clean final rendering requires all four cleaned wing textures and never falls back to dirty source DDS.

## Commands after ART_READY

Run these PowerShell commands from the project root (the directory containing `Run-Gimp.ps1` and `geometry/`). Set the executable to your installed Blender path if it is not on `PATH`:

```powershell
$BlenderExe = 'blender'
# Example alternative: $BlenderExe = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
```

Seven 4096 main textures, with UV-coverage alpha and 16px margin:

```powershell
& $BlenderExe -b --factory-startup --python '.\geometry\bake_projection.py' -- --materials A380X_FUSE1 A380X_FUSE2 A380X_FUSE3 A380X_FUSE4 A380X_FUSE5 A380_EXTERIOR_ENG_LH A380_EXTERIOR_ENG_RH --no-preview
```

1024 wingtip, without starting temporary full previews:

```powershell
& $BlenderExe -b --factory-startup --python '.\geometry\bake_projection.py' -- --materials A380_EXTERIOR_WINGFENCE --resolution 1024 --no-preview
```

Transparent B-38AM wing and AM/01 NLG-door ink layers:

```powershell
& $BlenderExe -b --factory-startup --python '.\geometry\bake_identification_decals.py' -- --mode both
```

After GIMP has composited all 13 clean final PNGs:

```powershell
& $BlenderExe -b --factory-startup --python '.\geometry\render_final.py'
```

Final output names: `preview/aemeath-port.png`, `aemeath-starboard.png`, `aemeath-three-quarter.png`, `aemeath-top.png`, `aemeath-bottom-identification.png`, and `aemeath-a380x-preview.blend`. The blend packs the 13 final PNGs.

## Inputs

- `side_pos_x.png` and `side_neg_x.png`: 8192×2560 opaque RGB. Y[-38,40], Z[-4,20.375], port U=(Y+38)/78, starboard U=(40-Y)/78.
- Four `engine_local_01..04.png` masters plus `_neg.png` variants; only text is mirrored in negative-side variants. Order: left outer, left inner, right inner, right outer.
- `wingfence_local.png`: wingtip design.
- `wing_registration.png`: 2048×512 transparent B-38AM / AM-01 artwork.
- `gear_code.png`: transparent AM / 01, normally512×128.

Initial eye-placement check, pending final mask metadata: port uses source#02 (1200×1200), anchor(530,255), width18m, world(Y10.3,Z3.35). Its lower window band maps to original source y≈323–348; upper band≈146–166. Starboard source#07 (1300×1080), anchor(693,450), width24m, world(Y13.0,Z3.15), mirrored; lower band maps to source y≈495–515 and upper≈350–367. Human and robot eye locations appear clear; robot crown near Z6.8 may touch the fuselage top silhouette and requires the first model preview. Crop offsets must be applied from the actual GIMP cutout metadata.

## Timing on this machine

- One 4096 FUSE rebake: about7–10seconds; the last measured FUSE3 shader/mask pass took7.516seconds.
- Seven 4K main bakes plus1K wingtip: allow40–70seconds.
- Both identifier ink bakes: allow10–25seconds.
- Final five-view rendering at48samples: previous measured run48seconds; allow50–65seconds including startup/packing.
- Whole bake-plus-render cycle: about2–3minutes, excluding GIMP composition, approval/review and design revisions.

Rendering is a paintkit-model inspection. Simulator loading, LODs and opened-door animation remain separate checks.
