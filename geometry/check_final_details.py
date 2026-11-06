"""Read-only close-camera renders of the completed Aemeath blend; no rebake."""
import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'geometry/qa'
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'preview/aemeath-a380x-preview.blend'))
scene=bpy.context.scene;scene.cycles.samples=16
scene.render.resolution_x=2000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
for name,x,y,z,scale in [('title-port',130,-22.5,3,8),('character-port',130,13.8,3.2,21),('character-starboard',-130,13.8,3.5,18),('registration-plate-port',130,22.8,4.9,8),('registration-plate-starboard',-130,22.8,4.9,8)]:
    data=bpy.data.cameras.new('QA_'+name);data.type='ORTHO';data.ortho_scale=scale
    cam=bpy.data.objects.new('QA_'+name,data);scene.collection.objects.link(cam);cam.location=(x,y,z)
    cam.rotation_euler=(Vector((0,y,z))-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.camera=cam;scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
print('DETAIL_QA_COMPLETE',flush=True)
