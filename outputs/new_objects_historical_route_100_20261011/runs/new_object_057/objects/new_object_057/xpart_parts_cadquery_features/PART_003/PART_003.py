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

PARAMETERS=json.loads(r'''{
  "center_xy": [
    -0.013673878133905975,
    -0.31887261834734215
  ],
  "profile": [
    [
      1.3217473098970833,
      -6.364461065727035
    ],
    [
      2.6429895226234503,
      -6.359197178015344
    ],
    [
      3.964553628841597,
      -6.361581329521199
    ],
    [
      5.286119042032878,
      -6.365503312158399
    ],
    [
      6.607676786184431,
      -6.36592522446799
    ],
    [
      7.929234188308577,
      -6.366230626663709
    ],
    [
      9.250782256424099,
      -6.3680973165122285
    ],
    [
      10.572348274243847,
      -6.36999415025811
    ],
    [
      11.893884844755274,
      -6.3674957132230015
    ],
    [
      13.215355852698202,
      -6.363327618263407
    ],
    [
      14.536818758636961,
      -6.366668041402618
    ],
    [
      15.858305366728871,
      -6.370719458760675
    ],
    [
      17.179839261020916,
      -6.365586677046505
    ],
    [
      18.501389317737654,
      -6.364059000124994
    ],
    [
      19.82295202847999,
      -6.360011053629112
    ],
    [
      21.144525157608456,
      -6.358757026337939
    ],
    [
      22.466095326960158,
      -6.357926844203622
    ],
    [
      23.78765037873876,
      -6.354922117930506
    ],
    [
      25.109201863539077,
      -6.355713185471277
    ],
    [
      26.430761832059176,
      -6.356601990587504
    ],
    [
      27.752291644315438,
      -6.353155469795151
    ],
    [
      29.073787537655946,
      -6.347216453461839
    ],
    [
      30.395317085974348,
      -6.343120349354393
    ],
    [
      31.71687587456556,
      -6.344413376284502
    ],
    [
      33.03841859555617,
      -6.3475607517637425
    ],
    [
      34.35998353139433,
      -6.34688969817795
    ],
    [
      35.68153640957151,
      -6.341504084897394
    ],
    [
      37.00306602357274,
      -6.334109950111728
    ],
    [
      38.32460728431234,
      -6.328997990380292
    ],
    [
      39.64614741117912,
      -6.326775904617416
    ],
    [
      40.96769427338678,
      -6.325568223354008
    ],
    [
      42.289242641451246,
      -6.320894745991444
    ],
    [
      43.61076628424418,
      -6.312635400977883
    ],
    [
      44.932237041064894,
      -6.30752453677767
    ],
    [
      46.25259485316052,
      -6.269126604731081
    ],
    [
      47.53770643947476,
      -6.072518285591325
    ],
    [
      48.478317091301,
      -5.282949717988251
    ],
    [
      49.023055572325305,
      -4.156609493531663
    ],
    [
      48.85622753706494,
      -2.8946842849257557
    ],
    [
      48.42944002642102,
      -1.6497495195048493
    ],
    [
      47.99110825180223,
      -0.41822927626743994
    ],
    [
      47.620731256561555,
      0.8406997190573386
    ],
    [
      47.27600180799078,
      2.115937889089528
    ],
    [
      46.73001459001905,
      3.2900591099841168
    ],
    [
      45.88233906674063,
      4.227855908119237
    ],
    [
      44.75741900405909,
      4.850290808995384
    ],
    [
      43.50302148512037,
      5.296263492495835
    ],
    [
      42.23148023119907,
      5.689384594464784
    ],
    [
      40.94283341903491,
      5.980129826087154
    ],
    [
      39.63774242197444,
      6.162485669437986
    ],
    [
      38.321498559545205,
      6.225151440675102
    ],
    [
      37.0005102346245,
      6.254413002809268
    ],
    [
      35.67953683621273,
      6.238284413975007
    ],
    [
      34.35864401772421,
      6.204782535413067
    ],
    [
      33.03750736727868,
      6.182313769602675
    ],
    [
      31.716233677132244,
      6.161075653013341
    ],
    [
      30.394841131197172,
      6.148493066755389
    ],
    [
      29.073404864267413,
      6.125188534093375
    ],
    [
      27.75186529162864,
      6.117242679734446
    ],
    [
      26.43032755401717,
      6.115743272356109
    ],
    [
      25.10882390236403,
      6.102881552497513
    ],
    [
      23.787327160612232,
      6.090126594963712
    ],
    [
      22.465792119678422,
      6.079344267837395
    ],
    [
      21.14424088244913,
      6.067339069700088
    ],
    [
      19.822697666687365,
      6.059128079301565
    ],
    [
      18.50116937313122,
      6.057476046675053
    ],
    [
      17.17971554038408,
      6.054333002791662
    ],
    [
      15.85820382020604,
      6.050132451840364
    ],
    [
      14.5366661911479,
      6.045023913028855
    ],
    [
      13.215144657659124,
      6.038634644817135
    ],
    [
      11.893589272062307,
      6.035514048569356
    ],
    [
      10.572065691869629,
      6.036468025242482
    ],
    [
      9.250532608059109,
      6.032863630697797
    ],
    [
      7.929015278866252,
      6.033106885748719
    ],
    [
      6.607482933263002,
      6.0393819204852965
    ],
    [
      5.285956010821806,
      6.045322464850724
    ],
    [
      3.9644340599587027,
      6.042817476032422
    ],
    [
      2.642980595915944,
      6.043540827683113
    ],
    [
      1.3217862331944603,
      6.046005914588591
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      0.0,
      1.0,
      0.0
    ],
    [
      0.0,
      0.0,
      1.0
    ],
    [
      1.0,
      0.0,
      0.0
    ]
  ],
  "axis_candidate": 2,
  "center": [
    -0.198762615,
    -0.00013372499999999427,
    0.0008714949999999999
  ],
  "construction_scale": 718.6072643864636,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
