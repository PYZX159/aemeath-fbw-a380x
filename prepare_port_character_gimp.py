from pathlib import Path
root=Path(globals().get('PROJECT_ROOT') or Path(__file__).resolve().parent).resolve()
exec((root/'helper_export.py').read_text(encoding='utf-8'))
im=Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,Gio.File.new_for_path(str(root/'references/02-official-website-lihui.webp')))
im.undo_disable();item=im.get_layers()[0]
if not item.has_alpha():item.add_alpha()
item.set_name('Official Aemeath portrait — original RGB, clipped right edge blended')
backup=Gimp.Layer.new_from_drawable(item,im);im.insert_layer(backup,None,1);backup.set_name('Unmodified official reference (hidden)');backup.set_visible(False)
# The website source clips flowing hair at its right canvas edge. Blend only
# this outermost strip into the aircraft paint; keep the face and main silhouette.
im.select_rectangle(Gimp.ChannelOps.REPLACE,-200,-200,1320,1600)
Gimp.Selection.feather(im,35)
mask=item.create_mask(Gimp.AddMaskType.SELECTION);item.add_mask(mask);Gimp.Selection.none(im)
pdb_run('gimp-xcf-save',image=im,file=Gio.File.new_for_path(str(root/'artwork/source/aemeath_port_edge_mask.xcf')))
im.remove_layer(backup)
save_png(im,root/'artwork/assets/aemeath_port_hero.png')
im.delete();print('PORT_EDGE_BLEND_COMPLETE',flush=True)
