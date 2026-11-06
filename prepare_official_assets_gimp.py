from pathlib import Path
import json
root=Path(globals().get('PROJECT_ROOT') or Path(__file__).resolve().parent).resolve()
exec((root/'helper_export.py').read_text(encoding='utf-8'))
refs=root/'references';assets=root/'artwork/assets';assets.mkdir(parents=True,exist_ok=True)
records={}
for path in sorted(refs.iterdir()):
    if path.suffix.lower() not in ['.webp','.png','.jpg','.jpeg']:continue
    im=Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,Gio.File.new_for_path(str(path)))
    ly=im.get_layers()[0];w,h=im.get_width(),im.get_height()
    records[path.name]={'width':w,'height':h,'has_alpha':ly.has_alpha(),'samples':{f'{x},{y}':list(ly.get_pixel(x,y).get_rgba()) for x,y in [(0,0),(w-1,0),(0,h-1),(w-1,h-1),(w//2,h//2)]}}
    targets={'02-official-website-lihui.webp':'aemeath_pose_A.png','07-official-website-five.webp':'aemeath_pose_B_official.png'}
    if path.name in targets:
        flat=Gimp.Image.new(w,h,Gimp.ImageBaseType.RGB);cl=Gimp.Layer.new_from_visible(im,flat,'Official pixels (no redraw or upscale)');flat.insert_layer(cl,None,0)
        save_png(flat,assets/targets[path.name]);flat.delete()
    im.delete()
(refs/'ASSET-METADATA.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
