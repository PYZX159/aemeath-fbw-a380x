"""Read-only verification of the final packed V4 blend and one title crop."""
import bpy, json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'preview/aemeath-a380x-preview.blend'))
images = [im for im in bpy.data.images if im.source == 'FILE']
report = {
    'images': len(images),
    'packed': sum(bool(im.packed_file) for im in images),
    'pngs': sum(im.filepath.lower().endswith('.png') for im in images),
    'srgb': sum(im.colorspace_settings.name == 'sRGB' for im in images),
    'dds': sum(im.filepath.lower().endswith('.dds') for im in images),
    'unpacked': [im.filepath for im in images if not im.packed_file],
    'old_theme_refs': [im.filepath for im in images
                       if any(s in (im.name+' '+im.filepath).lower()
                              for s in ['megumin', 'airchina', 'b-38mg', 'exp-01'])]
}
print('V4_PACK_QA '+json.dumps(report), flush=True)
assert report['images'] == report['packed'] == report['pngs'] == report['srgb'] == 13
assert not report['dds'] and not report['unpacked'] and not report['old_theme_refs']
scene = bpy.context.scene
scene.cycles.samples = 16
scene.render.resolution_x = 2000
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
data = bpy.data.cameras.new('QA_title_V4')
data.type = 'ORTHO'
data.ortho_scale = 8
cam = bpy.data.objects.new('QA_title_V4', data)
scene.collection.objects.link(cam)
cam.location = (130, -22.5, 3)
cam.rotation_euler = (Vector((0, -22.5, 3))-cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam
scene.render.filepath = str(ROOT/'geometry/qa/title-port-v4.png')
bpy.ops.render.render(write_still=True)
print('V4_TITLE_QA_COMPLETE', flush=True)
