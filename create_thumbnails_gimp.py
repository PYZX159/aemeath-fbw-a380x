from pathlib import Path
root=Path(globals().get('PROJECT_ROOT') or Path(__file__).resolve().parent).resolve()
exec((root/'helper_export.py').read_text(encoding='utf-8'))
im=Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,Gio.File.new_for_path(str(root/'preview/aemeath-three-quarter.png')))
tex=root/'package/aemeath-fbw-a380x-stable/SimObjects/AirPlanes/FlyByWire_A380_842_Aemeath/texture.AEMEATH'
for name,w,h in [('thumbnail.jpg',1024,512),('thumbnail_small.jpg',400,200)]:
    cp=im.duplicate()
    ow,oh=cp.get_width(),cp.get_height()
    if ow/oh>w/h:
        nw=round(oh*w/h);cp.crop(nw,oh,(ow-nw)//2,0)
    elif ow/oh<w/h:
        nh=round(ow*h/w);cp.crop(ow,nh,0,(oh-nh)//2)
    cp.scale(w,h)
    pdb_run('file-jpeg-export',image=cp,file=Gio.File.new_for_path(str(tex/name)),quality=.94)
    cp.delete()
im.delete()
print('THUMBNAILS_SAVED',flush=True)
