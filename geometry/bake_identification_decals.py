"""Bake transparent GIMP identification ink onto official A380X UVs.

Aemeath target: B-38AM / AM-01 / AM / 01. Wait for root ART_READY; run only after root approves
the completed GIMP PNGs. All inputs and outputs stay in aemeath-a380x.

CLI:
  blender.exe -b --factory-startup --python geometry/bake_identification_decals.py -- --mode wing
  blender.exe -b --factory-startup --python geometry/bake_identification_decals.py -- --mode door
  blender.exe -b --factory-startup --python geometry/bake_identification_decals.py -- --mode both

The RGB and original PNG alpha are baked separately. Black is never treated
as transparent. There is no image Y flip and no manual RGB gamma conversion.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
GEOMETRY = ROOT / 'geometry'
PROJECTION = ROOT / 'artwork/projection'
OUTPUT = ROOT / 'artwork/baked'


def math_node(nodes, links, operation, a=None, b=None):
    node = nodes.new('ShaderNodeMath')
    node.operation = operation
    for index, value in enumerate((a, b)):
        if value is None:
            continue
        if isinstance(value, (int, float)):
            node.inputs[index].default_value = value
        else:
            links.new(value, node.inputs[index])
    return node.outputs[0]


def within(nodes, links, value):
    return math_node(nodes, links, 'MULTIPLY',
                     math_node(nodes, links, 'GREATER_THAN', value, 0),
                     math_node(nodes, links, 'LESS_THAN', value, 1))


def load_and_combine_caches(paths):
    all_xyz, all_uv, offsets = [], [], [0]
    for path in paths:
        with np.load(path) as data:
            xyz = np.asarray(data['xyz'], dtype=np.float32)
            uv = np.asarray(data['uv'], dtype=np.float32)
            face_offsets = np.asarray(data['face_offsets'], dtype=np.int32)
            if len(xyz) != len(uv) or int(face_offsets[-1]) != len(xyz):
                raise ValueError(f'Invalid polygon-loop cache: {path}')
            old_count = offsets[-1]
            offsets.extend((face_offsets[1:] + old_count).tolist())
            all_xyz.append(xyz)
            all_uv.append(uv)
    return np.concatenate(all_xyz), np.concatenate(all_uv), np.asarray(offsets, dtype=np.int32)


def build_mesh(label, paths):
    xyz, uv, offsets = load_and_combine_caches(paths)
    faces = [list(range(int(start), int(end))) for start, end in zip(offsets[:-1], offsets[1:])]
    mesh = bpy.data.meshes.new(label + '_Mesh')
    mesh.from_pydata(xyz.tolist(), [], faces)
    mesh.update()
    layer = mesh.uv_layers.new(name='UVMap')
    layer.data.foreach_set('uv', uv.reshape(-1))
    obj = bpy.data.objects.new(label, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj, len(faces)


def projection_uv(mode, nodes, links, position, door_orientation):
    sep = nodes.new('ShaderNodeSeparateXYZ')
    links.new(position, sep.inputs[0])
    x, y = sep.outputs['X'], sep.outputs['Y']
    if mode == 'wing':
        # Orthonormal basis, with negative determinant as seen in world XY:
        # U x V faces -Z, so bottom-view lettering is not mirrored.
        dx = math_node(nodes, links, 'SUBTRACT', x, 29)
        dy = math_node(nodes, links, 'SUBTRACT', y, 6)
        u_distance = math_node(nodes, links, 'ADD',
                               math_node(nodes, links, 'MULTIPLY', dx, .8574929257),
                               math_node(nodes, links, 'MULTIPLY', dy, .5144957554))
        v_distance = math_node(nodes, links, 'ADD',
                               math_node(nodes, links, 'MULTIPLY', dx, -.5144957554),
                               math_node(nodes, links, 'MULTIPLY', dy, .8574929257))
        u = math_node(nodes, links, 'DIVIDE', u_distance, 9)
        v = math_node(nodes, links, 'SUBTRACT', 1,
                      math_node(nodes, links, 'DIVIDE', v_distance, 2.25))
    else:
        # Only the two previously verified FWD door skin meshes are loaded.
        # Therefore the same XY rectangle never prints onto adjacent fuselage.
        abs_x = math_node(nodes, links, 'ABSOLUTE', x)
        u_base = math_node(nodes, links, 'DIVIDE',
                           math_node(nodes, links, 'ADD', y, 33.20), .85)
        v_base = math_node(nodes, links, 'DIVIDE',
                           math_node(nodes, links, 'SUBTRACT', abs_x, .45), .30)
        is_left = math_node(nodes, links, 'GREATER_THAN', x, 0)
        if door_orientation == 'bottom-consistent':
            # Both doors share the same global U(+Y), V(+X) writing basis.
            # Each is directly readable under one common belly viewing angle.
            # For the RH negative-X rectangle V=(X+.75)/.30 = 1-v_base.
            u = u_base
            v_reverse = math_node(nodes, links, 'SUBTRACT', 1, v_base)
            v = math_node(nodes, links, 'ADD',
                          math_node(nodes, links, 'MULTIPLY', is_left, v_base),
                          math_node(nodes, links, 'MULTIPLY',
                                    math_node(nodes, links, 'SUBTRACT', 1, is_left), v_reverse))
        else:
            # Per-side convention for later open-door outside viewing:
            # LH U+Y/V+X; RH U-Y/V-X. Both UxV bases still face -Z.
            # This is a 180-degree RH rotation in one common belly view,
            # not a mirrored glyph. Simulator door animation needs checking.
            u_reverse = math_node(nodes, links, 'SUBTRACT', 1, u_base)
            u = math_node(nodes, links, 'ADD',
                          math_node(nodes, links, 'MULTIPLY', is_left, u_base),
                          math_node(nodes, links, 'MULTIPLY',
                                    math_node(nodes, links, 'SUBTRACT', 1, is_left), u_reverse))
            v = v_base
    region = math_node(nodes, links, 'MULTIPLY', within(nodes, links, u), within(nodes, links, v))
    combine = nodes.new('ShaderNodeCombineXYZ')
    links.new(u, combine.inputs['X'])
    links.new(v, combine.inputs['Y'])
    return combine.outputs[0], region


def make_material(label, mode, source, color_target, alpha_target, door_orientation):
    material = bpy.data.materials.new(label + '_Material')
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    links = material.node_tree.links
    geometry = nodes.new('ShaderNodeNewGeometry')
    vector, region = projection_uv(mode, nodes, links, geometry.outputs['Position'], door_orientation)
    texture = nodes.new('ShaderNodeTexImage')
    texture.image = source
    texture.interpolation = 'Linear'
    texture.extension = 'CLIP'
    links.new(vector, texture.inputs['Vector'])
    # Out-of-region color is immaterial at alpha 0. White makes unused RGB
    # convenient to inspect and never relies on black as a transparency key.
    color = nodes.new('ShaderNodeMixRGB')
    color.blend_type = 'MIX'
    color.inputs[1].default_value = (1, 1, 1, 1)
    links.new(region, color.inputs[0])
    links.new(texture.outputs['Color'], color.inputs[2])
    alpha = math_node(nodes, links, 'MULTIPLY', texture.outputs['Alpha'], region)
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Strength'].default_value = 1
    links.new(color.outputs[0], emission.inputs['Color'])
    output = nodes.new('ShaderNodeOutputMaterial')
    links.new(emission.outputs[0], output.inputs['Surface'])
    rgb_node = nodes.new('ShaderNodeTexImage')
    rgb_node.image = color_target
    rgb_node.label = 'UNLINKED RGB BAKE TARGET'
    alpha_node = nodes.new('ShaderNodeTexImage')
    alpha_node.image = alpha_target
    alpha_node.label = 'UNLINKED LINEAR ALPHA BAKE TARGET'
    return material, emission, color.outputs[0], alpha, rgb_node, alpha_node


def bake_decal(mode, source_path, cache_paths, output_path, resolution, door_orientation):
    started = time.time()
    obj, face_count = build_mesh('Identification_' + mode, cache_paths)
    source = bpy.data.images.load(str(source_path), check_existing=True)
    source.colorspace_settings.name = 'sRGB'
    source.alpha_mode = 'STRAIGHT'
    if mode == 'wing' and tuple(source.size) != (2048, 512):
        raise ValueError(f'Wing text source must be 2048x512: {source_path}, got {tuple(source.size)}')
    if source.channels < 4:
        raise ValueError(f'Expected a transparent RGBA text PNG: {source_path}')
    color_target = bpy.data.images.new(mode + '_RGB', width=resolution, height=resolution, alpha=True, float_buffer=False)
    color_target.colorspace_settings.name = 'sRGB'
    color_target.generated_color = (1, 1, 1, 0)
    alpha_target = bpy.data.images.new(mode + '_Alpha', width=resolution, height=resolution, alpha=True, float_buffer=True)
    alpha_target.colorspace_settings.name = 'Non-Color'
    alpha_target.generated_color = (0, 0, 0, 0)
    material, emission, color_socket, alpha_socket, rgb_node, alpha_node = make_material(
        mode, mode, source, color_target, alpha_target, door_orientation)
    obj.data.materials.append(material)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    nodes, links = material.node_tree.nodes, material.node_tree.links
    for node in nodes:
        node.select = False
    rgb_node.select = True
    nodes.active = rgb_node
    bpy.ops.object.bake(type='EMIT')
    # The alpha bake is the original PNG alpha times the geometric rectangle,
    # not a UV white mask and not an RGB black-key heuristic.
    for link in list(emission.inputs['Color'].links):
        links.remove(link)
    links.new(alpha_socket, emission.inputs['Color'])
    rgb_node.select = False
    alpha_node.select = True
    nodes.active = alpha_node
    bpy.ops.object.bake(type='EMIT')
    pixels = np.empty(resolution * resolution * 4, dtype=np.float32)
    alpha_pixels = np.empty_like(pixels)
    color_target.pixels.foreach_get(pixels)
    alpha_target.pixels.foreach_get(alpha_pixels)
    rgba = pixels.reshape(-1, 4)
    # Non-Color float target contains un-gamma-adjusted alpha in its R channel.
    alpha = np.clip(alpha_pixels.reshape(-1, 4)[:, 0], 0, 1)
    rgba[:, 3] = alpha
    rgba[alpha < .00001, :3] = 1
    color_target.pixels.foreach_set(rgba.reshape(-1))
    color_target.update()
    color_target.alpha_mode = 'STRAIGHT'
    color_target.filepath_raw = str(output_path)
    color_target.file_format = 'PNG'
    color_target.save()
    result = {
        'mode': mode,
        'source': str(source_path),
        'source_size': list(source.size),
        'cache_paths': [str(p) for p in cache_paths],
        'output': str(output_path),
        'resolution': resolution,
        'faces': face_count,
        'nonzero_alpha_texels': int(np.count_nonzero(alpha > .00001)),
        'opaque_alpha_texels': int(np.count_nonzero(alpha > .999)),
        'door_orientation': door_orientation if mode == 'door' else None,
        'seconds': round(time.time() - started, 3),
    }
    if result['nonzero_alpha_texels'] == 0:
        raise RuntimeError(f'All-transparent decal result: check world rectangle, source alpha, and mesh UV for {mode}')
    print('BAKED_IDENTIFICATION', json.dumps(result), flush=True)
    mesh = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    if mesh.users == 0:
        bpy.data.meshes.remove(mesh)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('wing', 'door', 'both'), required=True)
    parser.add_argument('--resolution', type=int, default=4096)
    parser.add_argument('--door-orientation', choices=('bottom-consistent', 'side-readable'), default='bottom-consistent')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    if args.resolution <= 0:
        raise ValueError('Resolution must be positive')
    specifications = {
        'wing': {
            'source': PROJECTION / 'wing_registration.png',
            'caches': [GEOMETRY / 'A380_EXTERIOR_WING1_underside_coordinates_uv.npz'],
            'output': OUTPUT / 'wing_registration_ink.png',
        },
        'door': {
            'source': PROJECTION / 'gear_code.png',
            'caches': [GEOMETRY / 'gear-inspection/NLG_FWD_LH_FUSE1_coordinates_uv.npz',
                       GEOMETRY / 'gear-inspection/NLG_FWD_RH_FUSE1_coordinates_uv.npz'],
            'output': OUTPUT / 'gear_id_ink.png',
        },
    }
    modes = ['wing', 'door'] if args.mode == 'both' else [args.mode]
    # Validate the entire requested run before mutating any output file.
    for mode in modes:
        for path in [specifications[mode]['source'], *specifications[mode]['caches']]:
            if not path.is_file():
                raise FileNotFoundError(f'Awaiting approved identification source/cache: {path}')
    OUTPUT.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 1
    scene.render.bake.target = 'IMAGE_TEXTURES'
    scene.render.bake.use_clear = True
    scene.render.bake.use_selected_to_active = False
    scene.render.bake.margin = 16
    scene.render.bake.margin_type = 'EXTEND'
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'
    results = []
    for mode in modes:
        spec = specifications[mode]
        results.append(bake_decal(mode, spec['source'], spec['caches'], spec['output'], args.resolution, args.door_orientation))
    manifest = {
        'bake': 'Cycles CPU EMIT RGB pass plus independent linear source-alpha pass',
        'margin_px': 16,
        'source_rgb_space': 'sRGB image -> shader conversion -> sRGB PNG, no manual gamma transform',
        'alpha': 'Original PNG alpha multiplied by rectangle; black/white RGB never determines transparency',
        'results': results,
    }
    (OUTPUT / 'identification-bake-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print('IDENTIFICATION_BAKE_COMPLETE', flush=True)


if __name__ == '__main__':
    main()
