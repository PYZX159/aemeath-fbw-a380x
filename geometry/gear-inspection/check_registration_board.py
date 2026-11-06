"""Read-only geometry test: Aemeath registration plate and cyan border."""
import json
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'geometry/gear-inspection'
def load_tree(name):
    with np.load(ROOT/'geometry'/f'{name}_coordinates_uv.npz') as data:
        xyz=data['xyz'];ofs=data['face_offsets']
        polygons=[list(range(int(a),int(b))) for a,b in zip(ofs[:-1],ofs[1:])]
        return BVHTree.FromPolygons(xyz.tolist(),polygons,all_triangles=False)
body=load_tree('A380X_FUSE3');tail=load_tree('A380X_FUSE4')
cache={}
def point(y,z):
    key=(round(float(y),7),round(float(z),7))
    if key in cache:return cache[key]
    xs=[];missing=0;blocked=0
    for side in [1,-1]:
        origin=Vector((side*45,float(y),float(z)));direction=Vector((-side,0,0))
        hit,no,idx,distance=body.ray_cast(origin,direction,100)
        obstruction,on,oi,od=tail.ray_cast(origin,direction,100)
        if hit is None or side*hit.x<=0:missing+=1;continue
        xs.append(abs(hit.x))
        if obstruction is not None and od<distance-.005:blocked+=1
    result={'min_abs_X':min(xs) if xs else 0,'missing':missing,'HTP_blocks':blocked}
    cache[key]=result;return result
def values(start,end,step):
    return np.unique(np.r_[np.arange(start,end+.00000001,step),end])
def summarize(points):
    points=list(points);xs=[];cap=[];holes=0;blocked=0;blocked_points=[]
    for y,z in points:
        result=point(y,z);xs.append(result['min_abs_X']);holes+=result['missing'];blocked+=result['HTP_blocks']
        if result['HTP_blocks']:blocked_points.append((float(y),float(z)))
        if result['min_abs_X']<1.85:cap.append((float(y),float(z),result['min_abs_X']))
    return {'sample_pairs':len(points),'side_rays':len(points)*2,'min_abs_X':min(xs),'top_cap_sample_pairs':len(cap),'top_cap_affected_bounds_YZ':{'Y':[min(p[0] for p in cap),max(p[0] for p in cap)],'Z':[min(p[1] for p in cap),max(p[1] for p in cap)]} if cap else None,'missing_side_rays':holes,'HTP_blocked_side_rays':blocked,'HTP_affected_bounds_YZ':{'Y':[min(p[0] for p in blocked_points),max(p[0] for p in blocked_points)],'Z':[min(p[1] for p in blocked_points),max(p[1] for p in blocked_points)]} if blocked_points else None}
y0,y1,z0,z1=20.30,25.45,4.31,5.43
ys=values(y0,y1,.025);zs=values(z0,z1,.025)
plate=summarize((y,z) for y in ys for z in zs)
border=[]
for width in values(0,.020,.005):
    for y in values(y0,y1,.01):border.extend([(y,z0+width),(y,z1-width)])
    for z in values(z0,z1,.01):border.extend([(y0+width,z),(y1-width,z)])
border_report=summarize(border)
envelope=[]
for y in values(23,25.45,.10):
    low=4.31;high=5.8
    for _ in range(20):
        mid=(low+high)/2;r=point(y,mid)
        if r['missing']==0 and r['HTP_blocks']==0 and r['min_abs_X']>=1.90:low=mid
        else:high=mid
    envelope.append({'Y':float(y),'highest_Z_at_abs_X_ge_1_90':round(low,5)})
polygon=[(20.30,4.31),(24.95,4.31),(25.45,4.47),(25.45,5.03),(23.40,5.43),(20.30,5.43)]
def inside(y,z,poly):
    sign=None
    for a,b in zip(poly,poly[1:]+poly[:1]):
        cross=(b[0]-a[0])*(z-a[1])-(b[1]-a[1])*(y-a[0])
        if abs(cross)<1e-8:continue
        if sign is None:sign=cross>0
        elif (cross>0)!=sign:return False
    return True
polygon_fill=summarize((y,z) for y in ys for z in zs if inside(y,z,polygon))
polygon_border=[]
for a,b in zip(polygon,polygon[1:]+polygon[:1]):
    a=np.asarray(a);b=np.asarray(b);direction=b-a;length=float(np.linalg.norm(direction));inward=np.asarray((-direction[1],direction[0]))/length
    for distance in values(0,length,.01):
        center=a+direction*distance/length
        for w in values(0,.02,.005):
            p=center+inward*w;polygon_border.append(tuple(p))
polygon_border_report=summarize(polygon_border)
text={}
for label,coords in {'B-38AM':(20.5,24.15,4.79,5.25),'AM-01 / AEMEATH':(20.5,25.2,4.43,4.63)}.items():
    a,b,c,d=coords;text[label]=summarize((y,z) for y in values(a,b,.025) for z in values(c,d,.025))
report={'coordinate_system':'Blender Y longitudinal, Z height; both +/-X orthographic sides','top_cap_threshold_abs_X':1.85,'top_cap_feather_abs_X':[.65,1.85],'rectangle_bounds_YZ':{'Y':[y0,y1],'Z':[z0,z1]},'rectangle_fill':plate,'rectangle_inside_border_020':border_report,'safe_upper_envelope_abs_X_190':envelope,'recommended_beveled_polygon_YZ':polygon,'recommended_polygon_fill':polygon_fill,'recommended_polygon_inside_border_020':polygon_border_report,'unchanged_text_regions':text,'geometry_only':True}
(OUT/'registration-board-visibility.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report),flush=True)
