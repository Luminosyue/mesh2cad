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
  "operation": "base_and_profile_pads",
  "basis": [
    [
      0.0,
      0.0,
      1.0
    ],
    [
      1.0,
      0.0,
      0.0
    ],
    [
      0.0,
      1.0,
      0.0
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -13.599906478787451,
      "length": 1.649017508839449,
      "loops": [
        [
          [
            -15.596271,
            49.080091
          ],
          [
            -15.628067,
            -49.080188
          ],
          [
            -15.226587,
            -49.761186
          ],
          [
            14.011696,
            -49.642812
          ],
          [
            14.533808,
            -49.136534
          ],
          [
            14.671705,
            48.554792
          ],
          [
            14.533808,
            49.221868
          ],
          [
            14.082473,
            49.599014
          ],
          [
            -3.218006,
            49.737737
          ],
          [
            -9.554487,
            49.608992
          ],
          [
            -12.624112,
            49.241858
          ],
          [
            -15.226587,
            49.704907
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -11.951432966207154,
      "length": 13.188332096901522,
      "loops": [
        [
          [
            -14.543596,
            -46.469625
          ],
          [
            -14.516355,
            46.988455
          ],
          [
            -14.182362,
            47.35085
          ],
          [
            -13.138138,
            47.430192
          ],
          [
            14.011696,
            47.485845
          ],
          [
            14.533808,
            47.73279
          ],
          [
            14.93712,
            48.554792
          ],
          [
            14.930898,
            49.076906
          ],
          [
            14.533808,
            49.742049
          ],
          [
            13.489584,
            49.923786
          ],
          [
            -14.704474,
            49.963172
          ],
          [
            -15.226587,
            49.94424
          ],
          [
            -15.686543,
            49.599014
          ],
          [
            -15.794407,
            49.076906
          ],
          [
            -15.748699,
            -49.197108
          ],
          [
            -15.613294,
            -49.602296
          ],
          [
            -15.226587,
            -49.884526
          ],
          [
            -14.704474,
            -49.925885
          ],
          [
            13.463478,
            -49.913692
          ],
          [
            14.533808,
            -49.701375
          ],
          [
            14.905627,
            -49.080188
          ],
          [
            14.886933,
            -48.558073
          ],
          [
            14.533808,
            -47.797099
          ],
          [
            14.011696,
            -47.529257
          ],
          [
            -14.187086,
            -47.513851
          ],
          [
            -14.532831,
            -46.991737
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 1.2363551344352164,
      "length": 1.6490175088394472,
      "loops": [
        [
          [
            -14.557728,
            46.466343
          ],
          [
            -14.526705,
            -46.991737
          ],
          [
            -14.182362,
            -47.507327
          ],
          [
            -13.66025,
            -47.524511
          ],
          [
            14.011696,
            -47.491921
          ],
          [
            14.533808,
            -47.691975
          ],
          [
            14.817483,
            -48.035959
          ],
          [
            14.945369,
            -48.558073
          ],
          [
            14.958513,
            -49.080188
          ],
          [
            14.676143,
            -49.602296
          ],
          [
            14.232003,
            -49.833068
          ],
          [
            -14.704474,
            -49.922997
          ],
          [
            -15.226587,
            -49.880844
          ],
          [
            -15.616763,
            -49.602296
          ],
          [
            -15.748699,
            -49.175965
          ],
          [
            -15.78432,
            49.076906
          ],
          [
            -15.665454,
            49.599014
          ],
          [
            -15.226587,
            49.938445
          ],
          [
            -14.704474,
            49.966188
          ],
          [
            13.709891,
            49.935595
          ],
          [
            14.533808,
            49.772045
          ],
          [
            14.730856,
            49.599014
          ],
          [
            14.953108,
            49.076906
          ],
          [
            14.82442,
            48.032677
          ],
          [
            14.533808,
            47.687677
          ],
          [
            13.489584,
            47.430587
          ],
          [
            -14.182362,
            47.349029
          ],
          [
            -14.516342,
            46.988455
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 2.884828647015512,
      "length": 9.067148315450785,
      "loops": [
        [
          [
            15.796102,
            48.554792
          ],
          [
            15.752981,
            -48.558073
          ],
          [
            15.50772,
            -49.602296
          ],
          [
            15.05592,
            -49.898291
          ],
          [
            14.533808,
            -49.941708
          ],
          [
            -14.704474,
            -49.916292
          ],
          [
            -15.226587,
            -49.879474
          ],
          [
            -15.621072,
            -49.602296
          ],
          [
            -15.792457,
            -48.558073
          ],
          [
            -15.788282,
            49.076906
          ],
          [
            -15.68685,
            49.599014
          ],
          [
            -15.226587,
            49.961703
          ],
          [
            14.533808,
            49.965495
          ],
          [
            15.05592,
            49.910534
          ],
          [
            15.578032,
            49.542977
          ]
        ],
        [
          [
            14.445499,
            46.988455
          ],
          [
            14.446187,
            -46.991737
          ],
          [
            14.011696,
            -47.521882
          ],
          [
            -13.66025,
            -47.513347
          ],
          [
            -14.182362,
            -47.476039
          ],
          [
            -14.495679,
            -46.991737
          ],
          [
            -14.526651,
            44.900007
          ],
          [
            -14.468823,
            46.988455
          ],
          [
            -14.182362,
            47.332454
          ],
          [
            13.489584,
            47.454736
          ],
          [
            14.011696,
            47.433559
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 11.951432966207145,
      "length": 1.6490175088394454,
      "loops": [
        [
          [
            -15.461753,
            -49.329144
          ],
          [
            -15.517105,
            48.803751
          ],
          [
            -15.226587,
            49.693384
          ],
          [
            13.489584,
            49.742103
          ],
          [
            14.730958,
            49.599014
          ],
          [
            15.162525,
            49.076906
          ],
          [
            14.776615,
            46.187037
          ],
          [
            14.676667,
            39.156771
          ],
          [
            14.63385,
            -27.051432
          ],
          [
            14.793624,
            -45.165585
          ],
          [
            15.161896,
            -48.558073
          ],
          [
            15.05592,
            -49.231854
          ],
          [
            14.540264,
            -49.602296
          ],
          [
            8.790575,
            -49.509276
          ],
          [
            -14.43132,
            -49.796184
          ],
          [
            -15.226587,
            -49.703601
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 5,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    7.750000000000812e-06,
    -0.39141287999999996,
    0.0028688300000000028
  ],
  "construction_scale": 211.73974948816152,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
