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
      "start": -9.344191406965152,
      "length": 1.6993176598317612,
      "loops": [
        [
          [
            11.779405,
            36.663318
          ],
          [
            8.759789,
            36.221333
          ],
          [
            0.570192,
            35.845131
          ],
          [
            -1.653571,
            35.38541
          ],
          [
            -6.953131,
            34.959284
          ],
          [
            -7.789054,
            34.832125
          ],
          [
            -8.427663,
            34.549486
          ],
          [
            -9.884783,
            34.358121
          ],
          [
            -11.486019,
            34.362148
          ],
          [
            -11.968681,
            34.503289
          ],
          [
            -12.767771,
            33.71356
          ],
          [
            -13.109318,
            32.877637
          ],
          [
            -13.267278,
            30.36986
          ],
          [
            -13.163363,
            7.799892
          ],
          [
            -13.302856,
            -16.441927
          ],
          [
            -13.176977,
            -33.160424
          ],
          [
            -12.799979,
            -49.042994
          ],
          [
            -13.640531,
            -49.878635
          ],
          [
            -14.761363,
            -49.87892
          ],
          [
            -15.312378,
            -49.694143
          ],
          [
            -15.46759,
            -49.042994
          ],
          [
            -15.391335,
            49.596133
          ],
          [
            -14.476454,
            49.842513
          ],
          [
            -13.640531,
            49.793649
          ],
          [
            -13.060148,
            49.596133
          ],
          [
            -12.845319,
            48.760207
          ],
          [
            -12.767493,
            35.38541
          ],
          [
            -11.968681,
            34.583289
          ],
          [
            -10.29683,
            35.009406
          ],
          [
            -9.460904,
            35.601864
          ],
          [
            -8.964468,
            36.221333
          ],
          [
            -8.773037,
            36.665498
          ],
          [
            -8.624981,
            38.114681
          ],
          [
            -8.139515,
            39.565034
          ],
          [
            -7.71562,
            42.146244
          ],
          [
            -6.490446,
            43.744657
          ],
          [
            -4.774154,
            44.580584
          ],
          [
            -2.773507,
            45.127437
          ],
          [
            -1.937581,
            45.590206
          ],
          [
            -0.265734,
            45.817941
          ],
          [
            1.41548,
            46.254914
          ],
          [
            5.235926,
            46.552803
          ],
          [
            14.780914,
            46.628465
          ],
          [
            15.174912,
            46.252434
          ],
          [
            15.278088,
            43.22918
          ],
          [
            14.984816,
            40.40096
          ],
          [
            14.780914,
            39.677156
          ],
          [
            13.956238,
            37.893183
          ],
          [
            13.109065,
            37.019248
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -7.645247514789669,
      "length": 16.989812689411107,
      "loops": [
        [
          [
            -13.158405,
            44.580584
          ],
          [
            -13.416295,
            36.95821
          ],
          [
            -13.346117,
            35.38541
          ],
          [
            -13.593767,
            32.041711
          ],
          [
            -13.704378,
            -23.129327
          ],
          [
            -13.529098,
            -47.371147
          ],
          [
            -12.804604,
            -48.166452
          ],
          [
            -12.25386,
            -47.371147
          ],
          [
            -12.424718,
            35.38541
          ],
          [
            -12.188148,
            47.088357
          ],
          [
            -12.21158,
            47.924283
          ],
          [
            -12.445415,
            48.661157
          ],
          [
            -12.804604,
            48.982967
          ],
          [
            -13.212881,
            48.760207
          ],
          [
            -13.43219,
            47.924283
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 1,
  "thickness_regions": 2,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.013126579999999999,
    -0.6345412500000001,
    -0.32235284000000003
  ],
  "construction_scale": 84.75118822437157,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
