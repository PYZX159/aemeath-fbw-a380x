from pathlib import Path
import json
root=Path(globals().get('PROJECT_ROOT') or Path(__file__).resolve().parent).resolve()
exec((root/'helper_export.py').read_text(encoding='utf8'))
src=root/'references/FBW_REGISTRATION_original_no_flip.png'
final=root/'artwork/final';final.mkdir(parents=True,exist_ok=True)
source=root/'artwork/source';source.mkdir(parents=True,exist_ok=True)
im=Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,Gio.File.new_for_path(str(src)));im.undo_disable()
base=im.get_layers()[0]
backup=Gimp.Layer.new_from_drawable(base,im);im.insert_layer(backup,None,1);backup.set_name('Original FBW registration reference (hidden)');backup.set_visible(False)
base.set_name('Original SELCAL RE-PS and labels preserved')
right_before=str(base.get_pixel(700,65).get_rgba())
base.get_buffer().clear(Gegl.Rectangle.new(96,118,405,110));base.update(96,118,405,110)
right_after=str(base.get_pixel(700,65).get_rgba())
font=Gimp.Font.get_by_name('Arial Bold')
if not font:raise RuntimeError('Arial Bold unavailable')
text=Gimp.TextLayer.new(im,'B-38AM',font,100,Gimp.Unit.pixel());im.insert_layer(text,None,0)
text.set_name('B-38AM | Aemeath fictional aircraft registration');text.set_color(Gegl.Color.new('#FFFFFF'))
if text.get_width()>361:text.set_font_size(100*361/text.get_width(),Gimp.Unit.pixel())
text.set_offsets(112,117+round((113-text.get_height())/2))
pdb_run('gimp-xcf-save',image=im,file=Gio.File.new_for_path(str(source/'A380X_REGISTRATION_B38AM.xcf')))
im.remove_layer(backup)
flat=Gimp.Image.new(1024,1024,Gimp.ImageBaseType.RGB)
composite=Gimp.Layer.new_from_visible(im,flat,'Final registration composite');flat.insert_layer(composite,None,0)
save_png(flat,final/'A380X_REGISTRATION_ALBEDO.PNG')
tex=root/'package/aemeath-fbw-a380x-stable/SimObjects/AirPlanes/FlyByWire_A380_842_Aemeath/texture.AEMEATH'
tex.mkdir(parents=True,exist_ok=True)
save_dds(flat,tex/'A380X_REGISTRATION_ALBEDO.PNG.DDS','bc3',False)
info={'registration':'B-38AM','font':font.get_name(),'text_bounds':{'offsets':str(text.get_offsets()),'width':text.get_width(),'height':text.get_height()},'preserved':'SELCAL CODE and RE-PS; transparent background','flip_image':False,'dds_export':'pending package directory confirmation','selcal_before':right_before,'selcal_after_clear':right_after,'selcal_composite':str(composite.get_pixel(700,65).get_rgba()),'layers':[(l.get_name(),l.get_visible()) for l in im.get_layers()]}
info['dds_export']='BC3/DXT5 with mipmaps; transparent background'
(final/'registration-edit.json').write_text(json.dumps(info,indent=2),encoding='utf8')
bg=Gimp.Layer.new(flat,'Dark cockpit preview matte only',1024,1024,Gimp.ImageType.RGBA_IMAGE,100,Gimp.LayerMode.NORMAL)
flat.insert_layer(bg,None,1);Gimp.context_set_background(Gegl.Color.new('#20262c'));bg.fill(Gimp.FillType.BACKGROUND)
flat.resize(1024,260,0,0);save_png(flat,final/'REGISTRATION_B38AM_dark_proof.png');flat.delete();im.delete()
