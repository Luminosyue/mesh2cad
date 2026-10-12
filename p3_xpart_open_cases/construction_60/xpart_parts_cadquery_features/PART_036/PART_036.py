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
  "operation": "extrude",
  "basis": [
    [
      -0.8355098545401627,
      -0.22807747146417234,
      -0.49990394074940636
    ],
    [
      -0.4852317898858756,
      -0.12063052214518438,
      0.8660244726398496
    ],
    [
      -0.2578243453408265,
      0.9661412651043787,
      -0.009882449700578309
    ]
  ],
  "features": [
    {
      "type": "extrude",
      "start": -13.918110942633879,
      "length": 27.768752426694746,
      "loops": [
        [
          [
            -44.31616,
            -5.273818
          ],
          [
            -36.660622,
            -35.937227
          ],
          [
            -34.868095,
            -38.410758
          ],
          [
            -33.629877,
            -39.450134
          ],
          [
            -31.756482,
            -40.12286
          ],
          [
            -27.537928,
            -39.968402
          ],
          [
            -7.764151,
            -37.438757
          ],
          [
            39.721013,
            -30.53369
          ],
          [
            42.24412,
            -29.948267
          ],
          [
            43.382146,
            -29.438707
          ],
          [
            44.383539,
            -28.689288
          ],
          [
            45.294278,
            -27.220325
          ],
          [
            45.517656,
            -25.337258
          ],
          [
            37.47622,
            33.169391
          ],
          [
            37.098417,
            34.705429
          ],
          [
            36.177244,
            35.927823
          ],
          [
            34.521872,
            36.726397
          ],
          [
            33.019266,
            36.880575
          ],
          [
            31.266339,
            36.768207
          ],
          [
            -4.524873,
            32.095506
          ],
          [
            -19.334213,
            29.975186
          ],
          [
            -37.997073,
            27.672661
          ],
          [
            -49.682689,
            25.878964
          ],
          [
            -51.006901,
            25.028395
          ],
          [
            -51.615233,
            23.841241
          ],
          [
            -51.929579,
            21.905657
          ],
          [
            -51.774263,
            20.24119
          ]
        ],
        [
          [
            17.464315,
            -9.01373
          ],
          [
            15.447156,
            -11.129882
          ],
          [
            14.131738,
            -11.995599
          ],
          [
            12.699544,
            -12.70694
          ],
          [
            9.573251,
            -13.538537
          ],
          [
            7.229579,
            -13.61297
          ],
          [
            4.074182,
            -13.076691
          ],
          [
            1.660718,
            -12.062491
          ],
          [
            0.271904,
            -11.110049
          ],
          [
            -2.080936,
            -8.959953
          ],
          [
            -3.004041,
            -7.738681
          ],
          [
            -3.737675,
            -6.408036
          ],
          [
            -4.655127,
            -3.429377
          ],
          [
            -4.721531,
            -1.348454
          ],
          [
            -4.115729,
            2.144358
          ],
          [
            -3.73391,
            3.126008
          ],
          [
            -2.228355,
            5.497728
          ],
          [
            -0.009957,
            8.022623
          ],
          [
            1.673593,
            9.455805
          ],
          [
            3.012728,
            10.280685
          ],
          [
            4.498528,
            10.853016
          ],
          [
            6.142463,
            11.153061
          ],
          [
            8.298735,
            11.064608
          ],
          [
            10.400703,
            10.523823
          ],
          [
            11.894215,
            9.631813
          ],
          [
            12.856299,
            8.433042
          ],
          [
            14.344648,
            5.783928
          ],
          [
            18.211244,
            0.99938
          ],
          [
            18.863212,
            -0.378402
          ],
          [
            19.516519,
            -3.509536
          ],
          [
            19.384581,
            -5.33982
          ],
          [
            18.647192,
            -7.247856
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 5,
  "center": [
    -0.02004663999999999,
    0.65449342,
    0.13524002499999999
  ],
  "construction_scale": 308.03438698754326,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
