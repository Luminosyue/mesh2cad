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
      "start": -21.85034573491854,
      "length": 14.567771170441757,
      "loops": [
        [
          [
            2.342405,
            -49.333194
          ],
          [
            2.8597,
            -49.868195
          ],
          [
            3.376995,
            -49.931416
          ],
          [
            3.894291,
            -49.757512
          ],
          [
            4.343121,
            -49.295356
          ],
          [
            4.583875,
            -48.77806
          ],
          [
            4.748651,
            -47.599709
          ],
          [
            4.495044,
            -31.046269
          ],
          [
            4.445569,
            47.180152
          ],
          [
            4.401224,
            47.956093
          ],
          [
            4.132648,
            48.67211
          ],
          [
            3.635643,
            49.548504
          ],
          [
            3.118347,
            49.857065
          ],
          [
            2.601053,
            49.631033
          ],
          [
            2.342405,
            49.304458
          ],
          [
            1.652327,
            47.438797
          ],
          [
            1.025619,
            40.570202
          ],
          [
            1.068829,
            36.058312
          ],
          [
            0.822158,
            33.615599
          ],
          [
            0.874865,
            30.885359
          ],
          [
            1.620197,
            23.643233
          ],
          [
            1.710384,
            19.648636
          ],
          [
            1.849536,
            -45.932937
          ],
          [
            1.943907,
            -48.260768
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -21.85034573491854,
      "length": 14.567771170441757,
      "loops": [
        [
          [
            -4.695646,
            -8.687703
          ],
          [
            -4.586019,
            -48.634297
          ],
          [
            -4.133935,
            -49.812652
          ],
          [
            -3.606486,
            -49.980975
          ],
          [
            -3.08919,
            -49.775211
          ],
          [
            -2.691104,
            -49.295356
          ],
          [
            -2.23453,
            -48.260768
          ],
          [
            -2.183398,
            -47.743471
          ],
          [
            -2.043036,
            -31.304917
          ],
          [
            -2.314434,
            -23.430608
          ],
          [
            -2.479914,
            -1.704221
          ],
          [
            -1.583902,
            20.16593
          ],
          [
            -2.095199,
            37.495311
          ],
          [
            -2.082711,
            47.438797
          ],
          [
            -2.81697,
            49.507978
          ],
          [
            -3.34784,
            49.818923
          ],
          [
            -3.69886,
            49.766628
          ],
          [
            -3.987364,
            49.507978
          ],
          [
            -4.354238,
            46.662855
          ],
          [
            -4.340567,
            26.114823
          ],
          [
            -4.570008,
            9.302737
          ],
          [
            -4.435402,
            -1.043162
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -7.28344857830618,
      "length": 26.48614157130642,
      "loops": [
        [
          [
            2.342405,
            49.397981
          ],
          [
            1.782577,
            47.956093
          ],
          [
            1.696939,
            46.921506
          ],
          [
            1.832067,
            27.522945
          ],
          [
            1.83012,
            -46.96753
          ],
          [
            1.905569,
            -48.260768
          ],
          [
            2.150538,
            -49.036709
          ],
          [
            2.730376,
            -49.812652
          ],
          [
            3.376995,
            -49.992831
          ],
          [
            3.915623,
            -49.70857
          ],
          [
            4.405711,
            -49.036709
          ],
          [
            4.624659,
            -48.260768
          ],
          [
            4.675495,
            -47.196369
          ],
          [
            4.465442,
            -24.465198
          ],
          [
            4.455402,
            46.692662
          ],
          [
            4.346747,
            47.697448
          ],
          [
            3.609259,
            49.507978
          ],
          [
            3.312369,
            49.766628
          ],
          [
            2.8597,
            49.836401
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": -7.28344857830618,
      "length": 26.48614157130642,
      "loops": [
        [
          [
            -4.444157,
            25.971059
          ],
          [
            -4.680381,
            14.331923
          ],
          [
            -4.577036,
            -1.186926
          ],
          [
            -4.723188,
            -1.962868
          ],
          [
            -4.78234,
            -5.554126
          ],
          [
            -4.647409,
            -48.260768
          ],
          [
            -4.361467,
            -49.554005
          ],
          [
            -4.123783,
            -49.870777
          ],
          [
            -3.606486,
            -49.962778
          ],
          [
            -2.821821,
            -49.295356
          ],
          [
            -2.428801,
            -47.743471
          ],
          [
            -2.649073,
            -26.793027
          ],
          [
            -2.573097,
            5.796556
          ],
          [
            -2.494802,
            8.930132
          ],
          [
            -1.730598,
            17.982794
          ],
          [
            -1.565102,
            22.349994
          ],
          [
            -2.177015,
            38.903434
          ],
          [
            -2.206943,
            47.438797
          ],
          [
            -2.903552,
            49.507978
          ],
          [
            -3.606486,
            49.911215
          ],
          [
            -4.037667,
            49.766628
          ],
          [
            -4.123783,
            49.512117
          ],
          [
            -4.411607,
            47.180152
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 19.201818979170845,
      "length": 2.6494007695770927,
      "loops": [
        [
          [
            2.324484,
            -49.332342
          ],
          [
            2.856523,
            -49.812652
          ],
          [
            3.376995,
            -49.943293
          ],
          [
            3.871783,
            -49.812652
          ],
          [
            4.152115,
            -49.554005
          ],
          [
            4.670879,
            -48.519413
          ],
          [
            4.795614,
            -46.793034
          ],
          [
            4.691303,
            11.745448
          ],
          [
            4.826547,
            45.802763
          ],
          [
            4.669476,
            47.180152
          ],
          [
            4.343186,
            48.214744
          ],
          [
            3.813115,
            49.249332
          ],
          [
            3.118347,
            49.683139
          ],
          [
            2.647418,
            49.249332
          ],
          [
            2.165113,
            47.956093
          ],
          [
            1.852349,
            46.921506
          ],
          [
            1.767481,
            45.802763
          ],
          [
            1.767717,
            -47.226175
          ],
          [
            1.947305,
            -48.519413
          ]
        ]
      ]
    },
    {
      "type": "extrude",
      "start": 19.201818979170845,
      "length": 2.6494007695770927,
      "loops": [
        [
          [
            -2.599407,
            -31.707327
          ],
          [
            -2.448135,
            12.262743
          ],
          [
            -1.817174,
            25.453765
          ],
          [
            -1.831557,
            44.593679
          ],
          [
            -1.935553,
            46.662855
          ],
          [
            -2.133482,
            47.438797
          ],
          [
            -3.043721,
            49.507978
          ],
          [
            -3.34784,
            49.766035
          ],
          [
            -3.865136,
            49.898393
          ],
          [
            -4.123783,
            49.880902
          ],
          [
            -4.382428,
            49.574892
          ],
          [
            -4.646237,
            47.781598
          ],
          [
            -4.705158,
            -3.7734
          ],
          [
            -4.62924,
            -48.260768
          ],
          [
            -4.351222,
            -49.554005
          ],
          [
            -3.865136,
            -49.961544
          ],
          [
            -3.176274,
            -49.812652
          ],
          [
            -2.669573,
            -49.295356
          ],
          [
            -2.273685,
            -47.743471
          ]
        ]
      ]
    }
  ],
  "axis_candidate": 0,
  "thickness_regions": 3,
  "limitation": "Inferred few-region profile pads; curved transitions simplified",
  "center": [
    -0.288639955,
    0.023644679999999973,
    -0.042226360000000004
  ],
  "construction_scale": 104.8930752507747,
  "expected_solid_count": 2
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
