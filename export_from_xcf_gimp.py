"""Export all thirteen editable UV XCFs to the installable livery package.

Run with Run-Gimp.ps1. No Blender geometry or projection cache is required.
EXPORT_OUTPUT_ROOT may point to a scratch project root for verification.
"""
from pathlib import Path
root=Path(globals().get('PROJECT_ROOT',Path(__file__).resolve().parent))
exec((root/'helper_export.py').read_text(encoding='utf-8'))
output=Path(globals().get('EXPORT_OUTPUT_ROOT',root))
final=output/'artwork/final';final.mkdir(parents=True,exist_ok=True)
tex=output/'package/aemeath-fbw-a380x-stable/SimObjects/AirPlanes/FlyByWire_A380_842_Aemeath/texture.AEMEATH'
tex.mkdir(parents=True,exist_ok=True)
names=[f'A380X_FUSE{i}_ALBEDO' for i in range(1,6)]
names += [f'A380_EXTERIOR_ENG_{side}_ALBEDO' for side in ['LH','RH']]
names += [f'A380_EXTERIOR_WING{i}_ALBEDO' for i in ['1','1_2','2','2_2']]
names += ['A380X_EXTERIOR_WINGFENCE_ALBEDO','A380X_REGISTRATION_ALBEDO']
for name in names:
    source=root/'artwork/xcf'/(name+'.xcf')
    if not source.is_file():raise FileNotFoundError(source)
for name in names:
    im=Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,Gio.File.new_for_path(str(root/'artwork/xcf'/(name+'.xcf'))))
    im.undo_disable()
    save_png(im,final/(name+'.PNG'))
    dds=tex/(name+'.PNG.DDS')
    registration=name=='A380X_REGISTRATION_ALBEDO'
    save_dds(im,dds,'bc3' if registration else 'bc7',False)
    if not registration:mark_bc7_srgb(dds)
    im.delete();print('XCF_EXPORTED',name,flush=True)
print('THIRTEEN_XCF_EXPORT_COMPLETE',flush=True)
