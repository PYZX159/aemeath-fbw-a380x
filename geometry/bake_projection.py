"""Bake GIMP's two opaque side projections to the official A380X UV layout.

Run only after side_pos_x.png and side_neg_x.png have been finalized:
  blender -b --factory-startup --python geometry/bake_projection.py

No image Y flip is applied. The unflipped DDS->PNG/OBJ alignment was verified.
"""
import bpy, json, sys, time, argparse, struct
import numpy as np
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GEOM=ROOT/'geometry'
ART=ROOT/'artwork/projection'
OUT=ROOT/'artwork/baked'

parser=argparse.ArgumentParser()
parser.add_argument('--resolution',type=int,default=4096)
parser.add_argument('--materials',nargs='*',default=[f'A380X_FUSE{i}' for i in range(1,6)])
parser.add_argument('--no-preview',action='store_true')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
palette={'ivory':'#F2F5FA','crimson':'#172340','charcoal':'#101A2F'}
metadata=ART/'design-metadata.json'
if metadata.is_file():palette.update(json.loads(metadata.read_text(encoding='utf-8')).get('palette',{}))
extra_report=json.loads((GEOM/'engine-wingfence-report.json').read_text(encoding='utf-8'))
OUT.mkdir(parents=True,exist_ok=True)
sources={'pos':ART/'side_pos_x.png','neg':ART/'side_neg_x.png'}
for path in sources.values():
    if not path.is_file():raise FileNotFoundError(f'Awaiting completed GIMP projection: {path}')

bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.device='CPU'
scene.cycles.samples=1  # Emission has no stochastic lighting to converge.
scene.render.bake.margin=16
scene.render.bake.margin_type='EXTEND'
scene.render.bake.use_clear=True
scene.render.bake.use_selected_to_active=False
scene.render.bake.target='IMAGE_TEXTURES'
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGBA'
scene.render.image_settings.color_depth='8'
src={k:bpy.data.images.load(str(p),check_existing=True) for k,p in sources.items()}
for image in src.values():
    if tuple(image.size)!=(8192,2560):raise ValueError(f'Projection must be 8192x2560: {image.filepath} {tuple(image.size)}')
    image.colorspace_settings.name='sRGB'

def math_node(nodes,links,operation,a=None,b=None):
    n=nodes.new('ShaderNodeMath');n.operation=operation
    for i,val in enumerate([a,b]):
        if val is None:continue
        if isinstance(val,(int,float)):n.inputs[i].default_value=val
        else:links.new(val,n.inputs[i])
    return n.outputs[0]

def srgb_linear(x):return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4

def hex_linear(value):
    s=value.lstrip('#');return tuple(srgb_linear(int(s[i:i+2],16)/255) for i in (0,2,4))+(1,)

def smooth(nodes,links,value,low,high):
    node=nodes.new('ShaderNodeMapRange');node.interpolation_type='SMOOTHSTEP';node.clamp=True
    node.inputs['From Min'].default_value=low;node.inputs['From Max'].default_value=high
    node.inputs['To Min'].default_value=0;node.inputs['To Max'].default_value=1
    links.new(value,node.inputs['Value']);return node.outputs['Result']

def mix(nodes,links,factor,first,second):
    node=nodes.new('ShaderNodeMixRGB');node.blend_type='MIX'
    for i,v in enumerate([factor,first,second]):
        if isinstance(v,(tuple,list)):node.inputs[i].default_value=v
        elif isinstance(v,(int,float)):node.inputs[i].default_value=v
        else:links.new(v,node.inputs[i])
    return node.outputs[0]

def sample(nodes,links,path,u,v):
    coords=nodes.new('ShaderNodeCombineXYZ');links.new(u,coords.inputs['X']);links.new(v,coords.inputs['Y'])
    tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(path),check_existing=True)
    tex.image.colorspace_settings.name='sRGB';tex.interpolation='Linear';tex.extension='EXTEND'
    links.new(coords.outputs[0],tex.inputs['Vector']);return tex.outputs['Color']

def material(name,target):
    mat=bpy.data.materials.new(name+'_Projection_Bake');mat.use_nodes=True
    nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links
    emission=nodes.new('ShaderNodeEmission');emission.inputs['Strength'].default_value=1
    output=nodes.new('ShaderNodeOutputMaterial');links.new(emission.outputs[0],output.inputs['Surface'])
    position=nodes.new('ShaderNodeNewGeometry')
    sep=nodes.new('ShaderNodeSeparateXYZ');links.new(position.outputs['Position'],sep.inputs[0])
    absx=math_node(nodes,links,'ABSOLUTE',sep.outputs['X'])
    ivory=hex_linear(palette['ivory']);crimson=hex_linear(palette['crimson']);charcoal=hex_linear(palette['charcoal'])
    # The legacy 'crimson' palette key carries Aemeath's navy. The wing box
    # uses the new deep-slate charcoal, never an earlier project's colours.
    if name=='A380X_FUSE5':
        emission.inputs['Color'].default_value=charcoal
    elif 'ENG_' in name:
        # Four independent engine images. Rings keep the same Y coordinate;
        # only the text was mirrored in each *_neg.png by GIMP.
        group_colors={}
        numbering={'A380_EXTERIOR_ENG_LH':{'outer':1,'inner':2},'A380_EXTERIOR_ENG_RH':{'inner':3,'outer':4}}
        for group in ['inner','outer']:
            b=extra_report[name]['clusters'][group]['bounds']
            ymin=b['min'][1];zcenter=(b['min'][2]+b['max'][2])/2;xcenter=(b['min'][0]+b['max'][0])/2
            u=math_node(nodes,links,'DIVIDE',math_node(nodes,links,'SUBTRACT',sep.outputs['Y'],ymin),8.8)
            v=math_node(nodes,links,'DIVIDE',math_node(nodes,links,'ADD',math_node(nodes,links,'SUBTRACT',sep.outputs['Z'],zcenter),2.2),4.4)
            number=numbering[name][group]
            pos=sample(nodes,links,ART/f'engine_local_{number:02d}.png',u,v)
            neg=sample(nodes,links,ART/f'engine_local_{number:02d}_neg.png',u,v)
            local_side=math_node(nodes,links,'GREATER_THAN',sep.outputs['X'],xcenter)
            group_colors[group]=mix(nodes,links,local_side,neg,pos)
        color=mix(nodes,links,math_node(nodes,links,'GREATER_THAN',absx,20),group_colors['inner'],group_colors['outer'])
        links.new(color,emission.inputs['Color'])
    elif name=='A380_EXTERIOR_WINGFENCE':
        u=math_node(nodes,links,'DIVIDE',math_node(nodes,links,'SUBTRACT',sep.outputs['Y'],13.5),3.5)
        uneg=math_node(nodes,links,'SUBTRACT',1,u)
        v=math_node(nodes,links,'DIVIDE',math_node(nodes,links,'SUBTRACT',sep.outputs['Z'],.8),2.7)
        pos=sample(nodes,links,ART/'wingfence_local.png',u,v);neg=sample(nodes,links,ART/'wingfence_local.png',uneg,v)
        links.new(mix(nodes,links,math_node(nodes,links,'GREATER_THAN',sep.outputs['X'],0),neg,pos),emission.inputs['Color'])
    elif name.startswith('A380X_FUSE'):
        # Port +X: nose at image left. Starboard -X: nose at image right.
        u=math_node(nodes,links,'DIVIDE',math_node(nodes,links,'ADD',sep.outputs['Y'],38),78)
        v=math_node(nodes,links,'DIVIDE',math_node(nodes,links,'ADD',sep.outputs['Z'],4),24.375)
        uneg=math_node(nodes,links,'SUBTRACT',1,u)
        colors={}
        for side,uvx in [('pos',u),('neg',uneg)]:
            coords=nodes.new('ShaderNodeCombineXYZ');links.new(uvx,coords.inputs['X']);links.new(v,coords.inputs['Y'])
            tex=nodes.new('ShaderNodeTexImage');tex.image=src[side];tex.interpolation='Linear';tex.extension='CLIP';tex.label=f'{side}: opaque RGB, alpha intentionally unused'
            links.new(coords.outputs[0],tex.inputs['Vector']);colors[side]=tex.outputs['Color']
        side_mask=math_node(nodes,links,'GREATER_THAN',sep.outputs['X'],0)
        side_mix=nodes.new('ShaderNodeMixRGB');side_mix.blend_type='MIX'
        links.new(side_mask,side_mix.inputs[0]);links.new(colors['neg'],side_mix.inputs[1]);links.new(colors['pos'],side_mix.inputs[2])
        # Outside the declared projection rectangle the aircraft remains white.
        inside=math_node(nodes,links,'MULTIPLY',math_node(nodes,links,'GREATER_THAN',u,0),math_node(nodes,links,'LESS_THAN',u,1))
        inside=math_node(nodes,links,'MULTIPLY',inside,math_node(nodes,links,'GREATER_THAN',v,0))
        inside=math_node(nodes,links,'MULTIPLY',inside,math_node(nodes,links,'LESS_THAN',v,1))
        color=mix(nodes,links,inside,ivory,side_mix.outputs[0])
        if name=='A380X_FUSE4':
            htp_mask=math_node(nodes,links,'MULTIPLY',math_node(nodes,links,'GREATER_THAN',absx,1.5),math_node(nodes,links,'LESS_THAN',sep.outputs['Z'],6))
            color=mix(nodes,links,htp_mask,color,crimson)
        if name!='A380X_FUSE4':
            # Paint the top and belly as unified surfaces instead of exposing
            # a hard +X/-X artwork seam. Keep vertical tail artwork untouched.
            center_top=math_node(nodes,links,'SUBTRACT',1,smooth(nodes,links,absx,.65,1.85))
            top_factor=math_node(nodes,links,'MULTIPLY',center_top,smooth(nodes,links,sep.outputs['Z'],2.8,4.2))
            top_color=mix(nodes,links,smooth(nodes,links,sep.outputs['Y'],18,23),ivory,crimson)
            color=mix(nodes,links,top_factor,color,top_color)
            center_belly=math_node(nodes,links,'SUBTRACT',1,smooth(nodes,links,absx,.65,2.0))
            lower=math_node(nodes,links,'SUBTRACT',1,smooth(nodes,links,sep.outputs['Z'],-.65,.55))
            belly_factor=math_node(nodes,links,'MULTIPLY',center_belly,lower)
            # Front gear doors stay pearl white for their dark AM/01 code; central
            # belly fades to charcoal before it meets FUSE5's wing box.
            belly_color=mix(nodes,links,smooth(nodes,links,sep.outputs['Y'],-25,-18),ivory,charcoal)
            color=mix(nodes,links,belly_factor,color,belly_color)
        links.new(color,emission.inputs['Color'])
    else:
        raise ValueError(f'Unsupported paint projection material: {name}')
    # Active unlinked image node is Cycles' bake destination, never an input.
    target_node=nodes.new('ShaderNodeTexImage');target_node.image=target;target_node.label='ACTIVE BAKE DESTINATION'
    for node in nodes:node.select=False
    target_node.select=True;nodes.active=target_node
    return mat

manifest={'resolution':args.resolution,'margin_px':16,'bake':'EMIT','device':'CPU','source_alpha':'ignored; opaque RGB only','mapping':{'Y':[-38,40],'Z':[-4,20.375],'port_pos_x':'U=(Y+38)/78','starboard_neg_x':'U=1-(Y+38)/78','V':'(Z+4)/24.375'},'palette':palette,'top':'unified pearl white, navy transition Y18..23, absX .65..1.85 smooth cap','belly':'pearl-white nose to deep slate Y-25..-18, FUSE5 solid deep slate','HTP':'unified navy, absX>1.5 and Z<6','outputs':[]}
for name in args.materials:
    start=time.time()
    data=np.load(GEOM/f'{name}_coordinates_uv.npz')
    xyz=data['xyz'];uv=data['uv'];offsets=data['face_offsets']
    # World-space mesh reconstructed from the original polygon-loop data.
    # Each polygon keeps its exact OBJ UVs; normals do not determine side.
    mesh=bpy.data.meshes.new(name+'_BakeMesh')
    faces=[list(range(int(a),int(b))) for a,b in zip(offsets[:-1],offsets[1:])]
    mesh.from_pydata(xyz.tolist(),[],faces);mesh.update()
    uv_layer=mesh.uv_layers.new(name='UVMap')
    uv_layer.data.foreach_set('uv',uv.reshape(-1))
    obj=bpy.data.objects.new(name+'_BakeObject',mesh);scene.collection.objects.link(obj)
    target=bpy.data.images.new(name+'_Projection',width=args.resolution,height=args.resolution,alpha=True,float_buffer=False)
    target.generated_color=(1,1,1,0);target.colorspace_settings.name='sRGB'
    mat=material(name,target);mesh.materials.append(mat)
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.object.bake(type='EMIT')
    # Cycles fills unused texels with opaque black even on a generated RGBA
    # target. A second, white emission bake provides exact UV coverage/margin.
    # Use it as alpha rather than guessing coverage from black artwork pixels.
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    emission=next(n for n in nodes if n.type=='EMISSION')
    for link in list(emission.inputs['Color'].links):links.remove(link)
    emission.inputs['Color'].default_value=(1,1,1,1)
    mask=bpy.data.images.new(name+'_UV_Coverage',width=args.resolution,height=args.resolution,alpha=True,float_buffer=False)
    masknode=nodes.new('ShaderNodeTexImage');masknode.image=mask;nodes.active=masknode
    bpy.ops.object.bake(type='EMIT')
    colorpixels=np.empty(args.resolution*args.resolution*4,dtype=np.float32);target.pixels.foreach_get(colorpixels)
    maskpixels=np.empty_like(colorpixels);mask.pixels.foreach_get(maskpixels)
    colorpixels=colorpixels.reshape(-1,4);coverage=maskpixels.reshape(-1,4)[:,0]
    colorpixels[:,3]=coverage
    colorpixels[coverage<.0001,:3]=1
    target.pixels.foreach_set(colorpixels.reshape(-1));target.update()
    empty_texels=int(np.count_nonzero(coverage<.0001))
    path=OUT/f'{name}.png'
    target.filepath_raw=str(path);target.file_format='PNG';target.save()
    manifest['outputs'].append({'material':name,'path':str(path),'resolution':[args.resolution,args.resolution],'faces':len(faces),'transparent_unused_texels':empty_texels,'seconds':round(time.time()-start,3)})
    print('BAKED',name,str(path),flush=True)
    # Each FUSE is baked as one object, avoiding multiple-object image clears.
    bpy.data.objects.remove(obj,do_unlink=True);bpy.data.meshes.remove(mesh)
    bpy.data.images.remove(mask)
    data.close()
output_index={entry['material']:entry for entry in manifest['outputs']}
for prior_name in [f'A380X_FUSE{i}' for i in range(1,6)]+['A380_EXTERIOR_ENG_LH','A380_EXTERIOR_ENG_RH','A380_EXTERIOR_WINGFENCE']:
    prior_path=OUT/f'{prior_name}.png'
    if prior_name in output_index or not prior_path.is_file():continue
    with prior_path.open('rb') as file:header=file.read(24)
    width,height=struct.unpack('>II',header[16:24])
    output_index[prior_name]={'material':prior_name,'path':str(prior_path),'resolution':[width,height],'note':'previous successful bake; file header dimensions verified'}
manifest['outputs']=list(output_index.values())
(OUT/'projection-bake-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')

fuse_materials=[f'A380X_FUSE{i}' for i in range(1,6)]
all_materials=fuse_materials+[n for n in ['A380_EXTERIOR_ENG_LH','A380_EXTERIOR_ENG_RH','A380_EXTERIOR_WINGFENCE'] if (OUT/f'{n}.png').is_file()]
if not args.no_preview and all((OUT/f'{name}.png').is_file() for name in fuse_materials):
    bpy.ops.wm.open_mainfile(filepath=str(GEOM/'A380X-neutral-preview.blend'))
    scene=bpy.context.scene
    for name in all_materials:
        mat=bpy.data.materials[name];nodes=mat.node_tree.nodes;links=mat.node_tree.links
        bsdf=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
        tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(OUT/f'{name}.png'))
        tex.image.colorspace_settings.name='sRGB'
        links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])
    scene.cycles.samples=24
    scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0
    for obj in scene.objects:
        if obj.type=='LIGHT':obj.data.energy/=4;obj.data.color=(1,1,1)
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.32,.32,.32,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'A380X-projection-preview.blend'))
    for camera,filename in [('Camera_Port_Side','projection-port-side.png'),('Camera_Starboard_Side','projection-starboard-side.png'),('Camera_Three_Quarter','projection-three-quarter.png')]:
        scene.camera=bpy.data.objects[camera];scene.render.filepath=str(OUT/filename);bpy.ops.render.render(write_still=True)
print('BAKE_COMPLETE',flush=True)
