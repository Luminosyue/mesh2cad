"""Inferred standard-feature CAD. Approximate reconstruction, not recovered design history."""
from pathlib import Path
import json
"""Pure CadQuery feature builder. Input contains sketches, never a triangle mesh."""
import cadquery as cq
from math import sqrt

def sketch_wire(points, z, smooth=False):
    wp=cq.Workplane('XY',origin=(0,0,z))
    if isinstance(points,dict):
        return wp.center(*points['center']).circle(points['radius']).val()
    if smooth:
        return wp.spline([tuple(p) for p in points],periodic=True).wire().val()
    return wp.polyline([tuple(p) for p in points]).close().wire().val()

def build_model(p):
    if p['operation']=='revolve':
        pts=p['profile']; n=len(pts)
        wp=cq.Workplane('XZ').moveTo(0,pts[0][1]).lineTo(*pts[0])
        bounds=sorted(set(int(i*(n-1)/p['segments']) for i in range(p['segments']+1)))
        def tangent(k):
            a,b=pts[max(0,k-1)],pts[min(n-1,k+1)];x,y=b[0]-a[0],b[1]-a[1];d=sqrt(x*x+y*y);return (x/d,y/d)
        for a,b in zip(bounds[:-1],bounds[1:]):
            wp=wp.spline([tuple(q) for q in pts[a+1:b+1]],includeCurrent=True,tangents=[tangent(a),tangent(b)],scale=False)
        shape=wp.lineTo(0,pts[-1][1]).close().revolve(360,(0,0),(0,1)).val().translate((*p['center_xy'],0))
    else:
        features=[]
        for feature in p['features']:
            if feature['type']=='extrude':
                wires=[sketch_wire(q,feature['start']) for q in feature['loops']]
                shape=cq.Workplane('XY').newObject(wires).toPending().extrude(feature['length'],combine=False).val()
            else:
                wires=[sketch_wire(q,z,feature.get('smooth',False)) for z,q in feature['sections']]
                shape=cq.Workplane('XY').newObject(wires).toPending().loft(ruled=feature.get('ruled',True),combine=False).val()
                for pocket in feature.get('pockets',[]):
                    pw=[sketch_wire(q,z,True) for z,q in pocket]
                    tool=cq.Workplane('XY').newObject(pw).toPending().loft(ruled=True,combine=False).val()
                    shape=shape.cut(tool)
            features.append((shape,feature.get('cut',False)))
        shape=features[0][0]
        for addition,cut in features[1:]:
            shape=shape.cut(addition) if cut else shape.fuse(addition)
        shape=shape.clean()
    if 'basis' in p:
        b=p['basis']
        shape=shape.located(cq.Location(cq.Plane(origin=(0,0,0),xDir=tuple(b[0]),normal=tuple(b[2]))))
    return shape.scale(1/p['construction_scale']).translate(tuple(p['center']))

PARAMETERS=json.loads(r'''{"operation":"extrude","basis":[[-0.016785692486113613,0.02484282487944811,-0.9995116889458585],[-0.0018922053347982803,0.999633766709394,0.02484282487944811],[0.9998779222364647,0.0023805163889396574,-0.016785692486113613]],"features":[{"type":"extrude","start":-0.4886162485503266,"length":0.9777818470365622,"loops":[[[0.4710370506012329,0.2526399316364525],[0.46774095098577795,0.27180614051150576],[0.45602148568638223,0.2843801501556491],[0.4486968198742598,0.28682170542635665],[0.1779283403528047,0.28291521699322475],[-0.4341695660135506,0.2895074162241347],[-0.4491851309284014,0.287920405298175],[-0.45394616370628094,0.28242690593908315],[-0.4567539522675944,0.27510224012696094],[-0.46053836293719097,0.2106451809802845],[-0.46957211743880856,-0.14765305499603243],[-0.46883965085759627,-0.24653604345968383],[-0.46798510651284864,-0.267289263260697],[-0.46542147347860585,-0.2747360068363548],[-0.46078251846426177,-0.2786424952694867],[-0.45345785265213945,-0.2791308063236282],[-0.3367515107123238,-0.2802295061954465],[-0.04669474455227984,-0.2917048159677714],[0.32320087895989746,-0.29719831532686325],[0.45394616370628094,-0.29439052676554966],[0.4587071964841605,-0.287920405298175],[0.4606604407007264,-0.2711957516938289],[0.4660318622962827,-0.07611548556430447]]]}],"axis_candidate":3,"center":[0.0001831166453030164,-0.002258438625404424,6.103888176767214e-05],"construction_scale":1,"expected_solid_count":1}''')
def build():
    return build_model(PARAMETERS)
if False:
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))

_original_normalized_build = build
def build():
    return _original_normalized_build().scale(2.0).translate((0.0, 0.0, 0.0))

if __name__=="__main__":
    result=build()
    result.exportStep(str(Path(__file__).with_suffix(".step")))
