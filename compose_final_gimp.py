"""Finish Aemeath UV sheets in GIMP; save editable XCF, source PNG and DDS."""
from pathlib import Path
import json
root=Path(globals().get('PROJECT_ROOT') or Path(__file__).resolve().parent).resolve()
exec((root/'helper_export.py').read_text(encoding='utf-8'))
out=root/'artwork/final';out.mkdir(parents=True,exist_ok=True)
src=root/'artwork/xcf';src.mkdir(parents=True,exist_ok=True)
tex=root/'package/aemeath-fbw-a380x-stable/SimObjects/AirPlanes/FlyByWire_A380_842_Aemeath/texture.AEMEATH'
template=root/'artwork/clean-template';baked=root/'artwork/baked'
def png_canvas(im,path):
    flat=Gimp.Image.new(im.get_width(),im.get_height(),Gimp.ImageBaseType.RGB)
    copy=Gimp.Layer.new_from_visible(im,flat,'All visible artwork');flat.insert_layer(copy,None,0)
    save_png(flat,path);flat.delete()
jobs=[(f'FUSE_{n}',f'A380X_FUSE{n}_ALBEDO',f'A380X_FUSE{n}.png',4096) for n in range(1,6)]
jobs += [('ENG_LH','A380_EXTERIOR_ENG_LH_ALBEDO','A380_EXTERIOR_ENG_LH.png',4096),('ENG_RH','A380_EXTERIOR_ENG_RH_ALBEDO','A380_EXTERIOR_ENG_RH.png',4096),('WINGFENCE','A380X_EXTERIOR_WINGFENCE_ALBEDO','A380_EXTERIOR_WINGFENCE.png',1024)]
if 'ONLY' in globals():jobs=[j for j in jobs if j[0] in ONLY]
for group,name,ink,size in jobs:
    im=Gimp.Image.new(size,size,Gimp.ImageBaseType.RGB);im.undo_disable()
    base=Gimp.Layer.new(im,'Clean fresh-painted surface — no DIRT',size,size,Gimp.ImageType.RGBA_IMAGE,100,Gimp.LayerMode.NORMAL)
    im.insert_layer(base,None,0)
    color='#101A2F' if group=='FUSE_5' else '#172340' if group in ['FUSE_4','ENG_LH','ENG_RH','WINGFENCE'] else '#F2F5FA'
    Gimp.context_set_foreground(Gegl.Color.new(color));base.edit_fill(Gimp.FillType.FOREGROUND)
    source=Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,Gio.File.new_for_path(str(baked/ink)))
    if source.get_width()!=im.get_width():source.scale(im.get_width(),im.get_height())
    l=Gimp.Layer.new_from_visible(source,im,'Aemeath AM-01 — projected paint and identity');im.insert_layer(l,None,0);source.delete()
    if group=='FUSE_1':
        detail=Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE,im,Gio.File.new_for_path(str(template/'FUSE_1_safety_only.png')))
        im.insert_layer(detail,None,0);detail.set_name('Official maintenance markings only — DIRT excluded')
    if group=='FUSE_1':
        gear=baked/'gear_id_ink.png'
        if not gear.exists():raise FileNotFoundError('Awaiting nose gear identity ink: '+str(gear))
        l=Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE,im,Gio.File.new_for_path(str(gear)))
        im.insert_layer(l,None,0);l.set_name('Front gear door identifier AM / 01')
    if im.get_width()!=size:im.scale(size,size)
    pdb_run('gimp-xcf-save',image=im,file=Gio.File.new_for_path(str(src/(name+'.xcf'))))
    png_canvas(im,out/(name+'.PNG'))
    dds=tex/(name+'.PNG.DDS');save_dds(im,dds,'bc7',False);mark_bc7_srgb(dds)
    im.delete();print('EXPORTED',name,flush=True)

# All four wing materials are covered with clean paint; retain the official walkway.
for wing,side in [('1','LH'),('1_2','LH'),('2','RH'),('2_2','RH')]:
    if 'ONLY' in globals() and 'WING_'+wing not in ONLY:continue
    name=f'A380_EXTERIOR_WING{wing}_ALBEDO'
    clean=template/f'WING_{side}_clean.png'
    reference=Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,Gio.File.new_for_path(str(clean)))
    if '_' in wing:
        # Secondary wing/flap UVs have no separate PSD art group. Apply the same
        # clean base colour; mechanical lines remain in inherited normal maps.
        bg=reference.get_layers()[0].get_pixel(0,0)
        im=Gimp.Image.new(4096,4096,Gimp.ImageBaseType.RGB)
        l=Gimp.Layer.new(im,'Clean flap paint — no DIRT',4096,4096,Gimp.ImageType.RGBA_IMAGE,100,Gimp.LayerMode.NORMAL)
        im.insert_layer(l,None,0);Gimp.context_set_foreground(bg);l.edit_fill(Gimp.FillType.FOREGROUND);reference.delete()
    else:
        im=reference
        im.get_layers()[0].set_name('Official clean wing paint and walkway — DIRT excluded')
    im.undo_disable()
    if wing=='1':
        l=Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE,im,Gio.File.new_for_path(str(baked/'wing_registration_ink.png')))
        im.insert_layer(l,None,0);l.set_name('Underside registration B-38AM and theme AM-01')
    pdb_run('gimp-xcf-save',image=im,file=Gio.File.new_for_path(str(src/(name+'.xcf'))))
    png_canvas(im,out/(name+'.PNG'))
    dds=tex/(name+'.PNG.DDS');save_dds(im,dds,'bc7',False);mark_bc7_srgb(dds);im.delete()
    print('EXPORTED',name,flush=True)
print('AEMEATH_FINAL_TEXTURES_COMPLETE',flush=True)
