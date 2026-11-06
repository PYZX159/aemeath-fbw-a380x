"""Build Aemeath / AM-01 projection masters using GIMP, without screen control.

Official character pixels remain unchanged apart from scaling and composition.
All type, orbit lines, registration and aircraft identifiers stay editable in XCF.
"""
from pathlib import Path
import math, json
root=Path(globals().get('PROJECT_ROOT') or Path(__file__).resolve().parent).resolve()
exec((root/'helper_export.py').read_text(encoding='utf-8'))
out=root/'artwork/projection';out.mkdir(parents=True,exist_ok=True)
assets=root/'artwork/assets';assets.mkdir(parents=True,exist_ok=True)
W,H=8192,2560;S=W/78
WHITE='#F2F5FA';NAVY='#172340';DARK='#101A2F';PINK='#EB87BA';CYAN='#8BDDF0';PALE='#DBEAF5';GOLD='#D9C49A'

def sx(y,side):return (y+38)*S if side=='pos' else (40-y)*S
def sz(z):return (20.375-z)*S
def layer(im,name,w=None,h=None):
    item=Gimp.Layer.new(im,name,w or im.get_width(),h or im.get_height(),Gimp.ImageType.RGBA_IMAGE,100,Gimp.LayerMode.NORMAL)
    im.insert_layer(item,None,0);item.fill(Gimp.FillType.TRANSPARENT);return item
def solid(im,name,color):
    item=layer(im,name);Gimp.context_set_foreground(Gegl.Color.new(color));item.edit_fill(Gimp.FillType.FOREGROUND);return item
def svg_layer(im,name,body,side='pos'):
    transform='' if side=='pos' else 'transform="translate(2 0) scale(-1 1)"'
    content=f'<svg xmlns="http://www.w3.org/2000/svg" width="8192" height="2560" viewBox="-38 -20.375 78 24.375"><g {transform}>{body}</g></svg>'
    path=assets/(name.replace(' ','_')+'_'+side+'.svg');path.write_text(content,encoding='utf-8')
    art=load_svg(path,W);item=Gimp.Layer.new_from_visible(art,im,name);im.insert_layer(item,None,0);art.delete();return item
def star(cx,cz,r,color=CYAN):
    cy=-cz
    return f'<path d="M{cx},{cy-r} Q{cx+.10*r},{cy-.12*r} {cx+r*.60},{cy} Q{cx+.10*r},{cy+.12*r} {cx},{cy+r} Q{cx-.10*r},{cy+.12*r} {cx-r*.60},{cy} Q{cx-.10*r},{cy-.12*r} {cx},{cy-r}Z" fill="{color}"/>'
def orbit_crest(cx,cz,r):
    cy=-cz
    body=f'<g fill="none" stroke="{CYAN}"><ellipse cx="{cx}" cy="{cy}" rx="{r*.95}" ry="{r*.38}" transform="rotate(-32 {cx} {cy})" stroke-width=".065"/><path d="M{cx-r*.95},{cy+r*.82} Q{cx+r*.8},{cy+r*.20} {cx+r*.82},{cy-r*1.18}" stroke="{PINK}" stroke-width=".085"/></g>'
    body+=star(cx,cz,r*.78,WHITE)+star(cx+r*.80,cz+r*.80,r*.16,PINK)
    body+=f'<circle cx="{cx-r*.76}" cy="{cy+r*.25}" r=".12" fill="{CYAN}"/>'
    return body
def fit_text(im,text,cy,top,width,height,side,font='Arial Bold',color=NAVY,name=None):
    item=new_text(im,text,150,0,0,font,color)
    item.scale(round(width*S),round(height*S),False)
    item.set_offsets(round(min(sx(cy,side),sx(cy+width,side))),round(sz(top)))
    if name:item.set_name(name)
    return item
def paste_character(im,path,side,world_y,world_z,width,eye_px,name,mirror=False):
    art=Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,Gio.File.new_for_path(str(path)))
    original_w=art.get_width();factor=width*S/original_w
    nw=round(original_w*factor);nh=round(art.get_height()*factor);art.scale(nw,nh)
    item=Gimp.Layer.new_from_visible(art,im,name);im.insert_layer(item,None,0)
    ex=eye_px[0]*factor
    if mirror:
        item.transform_flip_simple(Gimp.OrientationType.HORIZONTAL,True,0);ex=nw-ex
    item.set_offsets(round(sx(world_y,side)-ex),round(sz(world_z)-eye_px[1]*factor))
    art.delete();return item

for side in ['pos','neg']:
    im=Gimp.Image.new(W,H,Gimp.ImageBaseType.RGB);im.undo_disable()
    solid(im,'Pearl-white fresh aircraft paint',WHITE)
    background=f'''<defs><linearGradient id="night" x1="-18" y1="0" x2="40" y2="0" gradientUnits="userSpaceOnUse"><stop stop-color="#253A64"/><stop offset=".5" stop-color="{NAVY}"/><stop offset="1" stop-color="{DARK}"/></linearGradient><linearGradient id="ribbon" x1="-24" y1="0" x2="30" y2="0" gradientUnits="userSpaceOnUse"><stop stop-color="{PINK}"/><stop offset=".50" stop-color="#B3B6EC"/><stop offset="1" stop-color="{CYAN}"/></linearGradient></defs>
      <path d="M-38 4 C-25 2.8 -17 2.2 -8 -.4 C0 -3.0 5 -6.9 18 -6.9 L42 -6.9 L42 8 L-38 8Z" fill="url(#night)"/>
      <path d="M18 -6.8 C23 -8.5 26 -13 28 -20.8 L42 -20.8 L42 8 L18 8Z" fill="{NAVY}"/>
      <path d="M-36 3.5 C-18 2.8 -7 -.9 8 -5.1 C16 -7.1 22 -6.9 26 -9.2 C30 -11.8 32 -15.2 35 -19.2" fill="none" stroke="url(#ribbon)" stroke-width=".53"/>
      <path d="M-36 3.1 C-18 2.4 -7 -1.3 8 -5.5 C16 -7.5 22 -7.3 26 -9.6 C30 -12.2 32 -15.6 35 -19.6" fill="none" stroke="{CYAN}" stroke-width=".055"/>
      <path d="M-33 3.8 C-18 3.5 -6 1.5 5 -.2 C21 -2.8 31 -3.7 42 -4.2 L42 8 L-33 8Z" fill="{DARK}"/>
      <path d="M-30 3.45 C-13 3.3 -2 1.2 12 -.8 C25 -2.6 33 -3.6 41 -3.9" fill="none" stroke="{PINK}" stroke-width=".075"/>
      <path d="M-27 3.7 C-11 3.4 1 1.4 14 -.7 C27 -2.5 35 -3.2 41 -3.6" fill="none" stroke="{CYAN}" stroke-width=".03"/>
      <path d="M-33 -.0 C-28 -.2 -22 -1.1 -18 -2.2" fill="none" stroke="{CYAN}" stroke-width=".09"/>
      <path d="M-31 -.25 C-26 -.45 -22 -1.3 -18 -2.45" fill="none" stroke="{PINK}" stroke-width=".035"/>
    '''
    svg_layer(im,'Night-blue hull and pink-to-cyan aurora ribbon',background,side)
    details=orbit_crest(31.2,13.5,2.90)
    details+=f'<g stroke="{CYAN}" fill="none" stroke-width=".032" opacity=".7"><path d="M2 -3.2 L7 -4.5 L12 -2.2 L18 -4.6 L23 -3.6 L28 -5.2"/><path d="M22 -8.2 L25 -10.0 L26.5 -12 L30 -15.8"/></g>'
    for y,z,r in [(-13,3.1,.24),(-8,4.4,.19),(-3,5.7,.22),(2,3.2,.16),(7,4.5,.18),(12,2.2,.16),(18,4.6,.20),(23,3.6,.18),(28,5.2,.18),(26.5,12,.15),(35.4,17.6,.29),(35,10.3,.20),(22,1.0,.17),(29,1.7,.18)]:
        details+=star(y,z,r,PINK if y%2 else CYAN)
    # Clear, geometric light marks, intentionally no grain, wear or scratch texture.
    for j in range(10):
        y=1+j*3.5;z=.35+math.sin(j*.9)*.4
        details+=f'<circle cx="{y}" cy="{-z}" r=".055" fill="{PALE}"/><path d="M{y+.25},{-z}h.35" stroke="{CYAN}" stroke-width=".024"/>'
    svg_layer(im,'Starlance orbit crest and constellation lights',details,side)
    if side=='pos':
        paste_character(im,assets/'aemeath_port_hero.png',side,10.3,3.35,18.0,(530,255),'Aemeath official transparent hero — port')
    else:
        cfg_path=assets/'starboard-character.json'
        if cfg_path.exists():
            cfg=json.loads(cfg_path.read_text(encoding='utf-8'))
            paste_character(im,assets/cfg['filename'],side,cfg['world_y'],cfg['world_z'],cfg['width_m'],cfg['eyes_px'],'Aemeath official second illustration — starboard',cfg.get('mirror',False))
        else:
            # A deliberately different portrait crop, mirrored to look forward.
            paste_character(im,root/'references/01-official-wiki-transparent-portrait.png',side,12.5,3.35,13.4,(504,271),'Aemeath official close portrait — starboard',True)
    svg_layer(im,'Aft aircraft identity contrast plate',f'<path d="M20.40 -5.43 H23.40 L25.45 -5.03 V-4.47 L24.95 -4.31 H20.40 Q20.30 -4.31 20.30 -4.41 V-5.33 Q20.30 -5.43 20.40 -5.43Z" fill="{NAVY}" fill-opacity=".94" stroke="{CYAN}" stroke-width=".020"/>',side)
    fit_text(im,'AEMEATH',-28.8,4.40,13.2,1.42,side,font='Arial Bold Italic',name='AEMEATH display name')
    fit_text(im,'爱弥斯',-23.99,2.92,2.58,.58,side,font='Microsoft YaHei Bold',name='爱弥斯 Chinese name')
    fit_text(im,'WUTHERING WAVES',-27.0,1.40,10.3,.55,side,name='WUTHERING WAVES title')
    fit_text(im,'AM-01  /  GUIDING STARLANCE',-27.0,.58,10.8,.22,side,color=NAVY,name='AM-01 theme identifier')
    fit_text(im,'B-38AM',20.50,5.25,3.65,.46,side,color=WHITE,name='Fictional registration B-38AM')
    fit_text(im,'AIRBUS A380-842  /  AM-01',20.50,4.63,4.7,.20,side,color=CYAN,name='Aircraft identity line')
    fit_text(im,'AM-01',-31.0,4.3,2.05,.25,side,color=NAVY,name='Forward unit identifier')
    save_png(im,out/f'side_{side}_x.png')
    pdb_run('gimp-xcf-save',image=im,file=Gio.File.new_for_path(str(out/f'Aemeath_side_{side}_x.xcf')))
    im.delete();print('SAVED_SIDE',side,flush=True)

for number in [1,2,3,4]:
    ew,eh=2048,1024
    eng=Gimp.Image.new(ew,eh,Gimp.ImageBaseType.RGB);eng.undo_disable();solid(eng,'Night-blue nacelle',NAVY)
    body=f'''<svg xmlns="http://www.w3.org/2000/svg" width="2048" height="1024"><rect width="2048" height="1024" fill="{NAVY}"/><rect x="175" width="46" height="1024" fill="{PINK}"/><rect x="239" width="17" height="1024" fill="{CYAN}"/><rect x="1810" width="18" height="1024" fill="{CYAN}"/><g transform="translate(1040 490)"><ellipse rx="205" ry="78" transform="rotate(-32)" fill="none" stroke="{CYAN}" stroke-width="7"/><path d="M0 -164 Q16 -18 92 0 Q16 18 0 164 Q-16 18 -92 0 Q-16 -18 0 -164Z" fill="{WHITE}"/><circle cx="158" cy="-124" r="15" fill="{PINK}"/></g></svg>'''
    path=assets/f'engine_{number:02d}.svg';path.write_text(body,encoding='utf-8');art=load_svg(path,ew)
    item=Gimp.Layer.new_from_visible(art,eng,'Pink-cyan rings and Starlance crest');eng.insert_layer(item,None,0);art.delete()
    tx=new_text(eng,f'AM-01 / {number:02d}',70,870,750,'Arial Bold',CYAN);tx.set_name('Engine position and theme identifier')
    save_png(eng,out/f'engine_local_{number:02d}.png');pdb_run('gimp-xcf-save',image=eng,file=Gio.File.new_for_path(str(out/f'engine_local_{number:02d}.xcf')))
    tx.transform_flip_simple(Gimp.OrientationType.HORIZONTAL,True,0)
    save_png(eng,out/f'engine_local_{number:02d}_neg.png');eng.delete()

tip=Gimp.Image.new(1024,1024,Gimp.ImageBaseType.RGB);tip.undo_disable();solid(tip,'Night-blue wingtip',NAVY)
tip_svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024"><g transform="translate(512 512)"><ellipse rx="290" ry="110" transform="rotate(-32)" fill="none" stroke="{CYAN}" stroke-width="12"/><path d="M0 -270 Q20 -25 150 0 Q20 25 0 270 Q-20 25 -150 0 Q-20 -25 0 -270Z" fill="{WHITE}"/><circle cx="230" cy="-185" r="22" fill="{PINK}"/></g></svg>'
path=assets/'wingtip.svg';path.write_text(tip_svg,encoding='utf-8');art=load_svg(path,1024);item=Gimp.Layer.new_from_visible(art,tip,'Wingtip Starlance crest');tip.insert_layer(item,None,0);art.delete();save_png(tip,out/'wingfence_local.png');pdb_run('gimp-xcf-save',image=tip,file=Gio.File.new_for_path(str(out/'wingfence_local.xcf')));tip.delete()

wing=Gimp.Image.new(2048,512,Gimp.ImageBaseType.RGB);wing.undo_disable();layer(wing,'Transparent wing registration canvas')
new_text(wing,'B-38AM',360,55,12,'Arial Bold',DARK)
new_text(wing,'AM-01  /  AEMEATH',72,105,398,'Arial Bold',DARK)
save_png(wing,out/'wing_registration.png');pdb_run('gimp-xcf-save',image=wing,file=Gio.File.new_for_path(str(out/'wing_registration.xcf')));wing.delete()
gear=Gimp.Image.new(512,128,Gimp.ImageBaseType.RGB);gear.undo_disable();layer(gear,'Transparent nose gear code canvas')
new_text(gear,'AM / 01',108,20,0,'Arial Bold',DARK)
save_png(gear,out/'gear_code.png');pdb_run('gimp-xcf-save',image=gear,file=Gio.File.new_for_path(str(out/'gear_code.xcf')));gear.delete()
(out/'design-metadata.json').write_text(json.dumps({'registration':'B-38AM (fictional)','theme':'AM-01','palette':{'ivory':WHITE,'crimson':NAVY,'charcoal':DARK,'pink':PINK,'cyan':CYAN},'mapping':{'Y':[-38,40],'Z':[-4,20.375]},'port_eyes':{'world':[10.3,3.35],'source_px':[530,255],'image_width_m':18.0},'engine_projection':'2048x1024, local fore-aft, four independently numbered engines','wing_number':'transparent 2048x512','surface':'clean, no DIRT or SCUFF overlays'},ensure_ascii=False,indent=2),encoding='utf-8')
print('ART_MASTERS_COMPLETE',flush=True)
