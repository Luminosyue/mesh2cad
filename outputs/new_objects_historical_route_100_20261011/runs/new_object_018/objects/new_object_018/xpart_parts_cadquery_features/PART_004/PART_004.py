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
  "features": [
    {
      "type": "extrude",
      "start": -50.0,
      "length": 100.0,
      "loops": [
        [
          [
            2.119679,
            24.944145
          ],
          [
            1.735785,
            26.968048
          ],
          [
            0.936387,
            29.023812
          ],
          [
            0.20668,
            30.426184
          ],
          [
            -0.961221,
            31.944504
          ],
          [
            -2.331736,
            33.188913
          ],
          [
            -4.387498,
            34.44814
          ],
          [
            -6.411401,
            35.171424
          ],
          [
            -7.813775,
            35.313602
          ],
          [
            -9.184279,
            35.277505
          ],
          [
            -10.554792,
            34.968455
          ],
          [
            -11.925304,
            34.213942
          ],
          [
            -13.993947,
            32.631582
          ],
          [
            -15.602129,
            31.079577
          ],
          [
            -17.674497,
            28.338558
          ],
          [
            -18.755487,
            26.314654
          ],
          [
            -19.195536,
            24.944145
          ],
          [
            -19.65755,
            22.203125
          ],
          [
            -19.472013,
            18.744989
          ],
          [
            -18.67015,
            16.00397
          ],
          [
            -16.758803,
            12.577696
          ],
          [
            -16.322648,
            11.207186
          ],
          [
            -14.998527,
            5.039889
          ],
          [
            -14.566932,
            -0.442149
          ],
          [
            -14.638352,
            -1.127404
          ],
          [
            -15.34051,
            -2.497914
          ],
          [
            -15.418739,
            -3.183169
          ],
          [
            -15.153295,
            -5.238934
          ],
          [
            -15.368334,
            -16.888269
          ],
          [
            -15.754091,
            -27.852344
          ],
          [
            -16.425857,
            -34.019643
          ],
          [
            -16.349396,
            -36.075405
          ],
          [
            -16.020526,
            -36.760663
          ],
          [
            -15.351581,
            -37.106936
          ],
          [
            -14.666318,
            -37.084596
          ],
          [
            -14.146375,
            -36.760663
          ],
          [
            -13.897303,
            -36.075405
          ],
          [
            -14.047043,
            -31.24676
          ],
          [
            -13.293547,
            -4.553679
          ],
          [
            -13.195363,
            -3.868424
          ],
          [
            -12.588401,
            -3.183169
          ],
          [
            -12.281943,
            -2.497914
          ],
          [
            -12.644081,
            -1.127404
          ],
          [
            -13.158582,
            5.725147
          ],
          [
            -14.214647,
            11.239047
          ],
          [
            -14.597367,
            12.584923
          ],
          [
            -16.675354,
            16.689225
          ],
          [
            -17.323578,
            18.768329
          ],
          [
            -17.595744,
            21.486009
          ],
          [
            -17.253937,
            24.25889
          ],
          [
            -16.56173,
            26.282793
          ],
          [
            -14.857063,
            29.023812
          ],
          [
            -11.924387,
            31.704952
          ],
          [
            -9.869539,
            33.021074
          ],
          [
            -7.813775,
            33.339216
          ],
          [
            -5.75801,
            32.850536
          ],
          [
            -3.670376,
            31.636638
          ],
          [
            -1.843553,
            29.70907
          ],
          [
            -1.033999,
            28.338558
          ],
          [
            -0.275971,
            26.501005
          ],
          [
            0.135723,
            24.227028
          ],
          [
            0.010502,
            -2.497914
          ],
          [
            0.267031,
            -3.868424
          ],
          [
            1.094541,
            -4.440622
          ],
          [
            1.779793,
            -4.294889
          ],
          [
            2.08654,
            -3.868424
          ],
          [
            2.039514,
            -1.812659
          ],
          [
            2.252215,
            -0.442149
          ],
          [
            2.280952,
            22.171264
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -50.0,
      "length": 100.0,
      "loops": [
        [
          [
            19.683967,
            -1.80328
          ],
          [
            19.596428,
            -4.07039
          ],
          [
            18.911168,
            -4.649447
          ],
          [
            18.225915,
            -4.546675
          ],
          [
            17.65562,
            -3.868424
          ],
          [
            17.771251,
            -1.812659
          ],
          [
            18.225915,
            -1.209819
          ],
          [
            18.911168,
            -1.111915
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "center": [
    -0.428059695,
    -0.07238358,
    -0.31551035
  ],
  "construction_scale": 277.9014130286407,
  "expected_solid_count": 2
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
