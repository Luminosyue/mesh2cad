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
    -0.1101644951629098,
    -0.022446459079715805
  ],
  "profile": [
    [
      1.1419316675401012,
      -42.0985601186383
    ],
    [
      3.3493892216175656,
      -42.10100157186977
    ],
    [
      5.582233354106392,
      -42.11594314607831
    ],
    [
      7.81498259546104,
      -42.14626812148717
    ],
    [
      10.047629869653942,
      -42.17878493085795
    ],
    [
      12.278382518668549,
      -42.23205830478109
    ],
    [
      14.508529330812252,
      -42.28670530667855
    ],
    [
      16.737897948128683,
      -42.34105638953413
    ],
    [
      18.96619130425515,
      -42.39857719241391
    ],
    [
      21.195829225059697,
      -42.461451492820345
    ],
    [
      23.426820968652635,
      -42.5278297960326
    ],
    [
      25.657656093791793,
      -42.587261499060546
    ],
    [
      27.88724681279668,
      -42.662927442023204
    ],
    [
      30.116720720979608,
      -42.72641891580081
    ],
    [
      32.34667159627887,
      -42.80187564337078
    ],
    [
      34.577827347467256,
      -42.881134592895236
    ],
    [
      36.80962267777085,
      -42.910802493911035
    ],
    [
      39.036432841591235,
      -42.823280786735225
    ],
    [
      41.220703754027326,
      -42.47495500016744
    ],
    [
      43.271122339892315,
      -41.726644493883285
    ],
    [
      45.134593273658595,
      -40.4761812251342
    ],
    [
      46.73888425656291,
      -38.88860660400647
    ],
    [
      47.989242262018834,
      -37.03477163505356
    ],
    [
      48.776970404107374,
      -34.962387475443926
    ],
    [
      49.21306829375348,
      -32.77687410486493
    ],
    [
      49.37593292981377,
      -30.554089495923172
    ],
    [
      49.4263099157955,
      -28.32317172256249
    ],
    [
      49.43939741131413,
      -26.091365884696863
    ],
    [
      49.438457324417456,
      -23.859730830478078
    ],
    [
      49.43472512710496,
      -21.62738012064586
    ],
    [
      49.431641162707486,
      -19.39098277782115
    ],
    [
      49.39847457373381,
      -17.15252612714672
    ],
    [
      49.4119512374678,
      -14.9138728224427
    ],
    [
      49.43411516153103,
      -12.675070500809209
    ],
    [
      49.46159219351887,
      -10.436241216736079
    ],
    [
      49.48050902593895,
      -8.197331207841197
    ],
    [
      49.49763318254341,
      -5.958529312626309
    ],
    [
      49.53443551020639,
      -3.721117081535688
    ],
    [
      49.53330319529627,
      -1.4872043888185131
    ],
    [
      49.53873207896732,
      0.7456719504830738
    ],
    [
      49.55364477599663,
      2.978545475522419
    ],
    [
      49.56707459871183,
      5.211660912046739
    ],
    [
      49.58632736280619,
      7.444870803657644
    ],
    [
      49.608762505995514,
      9.678931156855551
    ],
    [
      49.63151065866036,
      11.91651074325599
    ],
    [
      49.65275808343759,
      14.153667464937111
    ],
    [
      49.67622763898551,
      16.386331846691647
    ],
    [
      49.7056541024671,
      18.618484286139754
    ],
    [
      49.73404276372862,
      20.85021415135057
    ],
    [
      49.73607192703837,
      23.080937314340396
    ],
    [
      49.74547916776828,
      25.309038248542304
    ],
    [
      49.75907351938286,
      27.53730427803539
    ],
    [
      49.74513574205184,
      29.765155170480803
    ],
    [
      49.649214493336125,
      31.991249599289986
    ],
    [
      49.59510151698797,
      34.218569714805106
    ],
    [
      49.55024889481504,
      36.44721939605748
    ],
    [
      49.48381377987975,
      38.67440135379745
    ],
    [
      49.17414785658612,
      40.849848676290506
    ],
    [
      47.85394420439476,
      42.47075134109599
    ],
    [
      45.754252457191114,
      42.942741781234304
    ],
    [
      43.53357852874103,
      42.877514114777114
    ],
    [
      41.30351917783376,
      42.85953733246809
    ],
    [
      39.07322173729747,
      42.9221059084724
    ],
    [
      36.84166654027001,
      42.983501287249524
    ],
    [
      34.6091113324548,
      43.03737907760876
    ],
    [
      32.37627689243149,
      43.068914480095906
    ],
    [
      30.143455889743844,
      43.09029041271151
    ],
    [
      27.91059085792856,
      43.101304089748
    ],
    [
      25.67777424303418,
      43.10045155008547
    ],
    [
      23.44490393905778,
      43.11038087779065
    ],
    [
      21.211991475855815,
      43.127411487511964
    ],
    [
      18.97901045107332,
      43.159011563284224
    ],
    [
      16.746005745499883,
      43.181584588854086
    ],
    [
      14.51306861680413,
      43.20840907782275
    ],
    [
      12.280164667372526,
      43.22401253483157
    ],
    [
      10.047249294813202,
      43.25143093716585
    ],
    [
      7.814257418707519,
      43.260078187156296
    ],
    [
      5.581456349519072,
      43.263834952108866
    ],
    [
      3.349118727581317,
      43.22334027478623
    ],
    [
      1.1419389358017304,
      43.189688652819775
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      1.0,
      0.0,
      0.0
    ],
    [
      0.0,
      1.0,
      0.0
    ],
    [
      0.0,
      0.0,
      1.0
    ]
  ],
  "axis_candidate": 0,
  "center": [
    -0.010696054999999982,
    -0.00041210999999996556,
    -0.09977275500000002
  ],
  "construction_scale": 81.48487608105985,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
