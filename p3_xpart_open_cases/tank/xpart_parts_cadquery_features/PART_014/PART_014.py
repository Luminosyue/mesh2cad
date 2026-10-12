"""Editable CadQuery sketch/feature reconstruction. Approximate inferred design.
Run with Python + cadquery. No mesh or other input files required.
"""
from pathlib import Path
import json
"""Pure CadQuery feature builder. Input contains sketches, never a triangle mesh."""
import cadquery as cq
from math import sqrt

def sketch_wire(points, z, smooth=False):
    wp=cq.Workplane('XY',origin=(0,0,z))
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
            features.append((shape,feature.get('cut',False)))
        shape=features[0][0]
        for addition,cut in features[1:]:
            shape=shape.cut(addition) if cut else shape.fuse(addition)
        shape=shape.clean()
        b=p['basis']
        shape=shape.located(cq.Location(cq.Plane(origin=(0,0,0),xDir=tuple(b[0]),normal=tuple(b[2]))))
    return shape.scale(1/p['construction_scale']).translate(tuple(p['center']))

PARAMETERS = json.loads(r'''
{
  "center_xy": [
    -0.712049433347991,
    0.09834808688428752
  ],
  "profile": [
    [
      0.8784864505165274,
      -13.592399871669905
    ],
    [
      2.554561635123168,
      -13.324038006955352
    ],
    [
      4.2012112923518625,
      -12.80603531335479
    ],
    [
      5.765925951671049,
      -12.018706099630052
    ],
    [
      7.14934855768484,
      -10.995796784360753
    ],
    [
      8.362792926929163,
      -9.774215862421805
    ],
    [
      9.30276308985841,
      -8.31026396076684
    ],
    [
      10.147312340839498,
      -6.80871289633942
    ],
    [
      11.121704093916183,
      -5.3723014417097135
    ],
    [
      12.169178141973267,
      -4.05046001993502
    ],
    [
      13.524212714541818,
      -3.062810752834065
    ],
    [
      15.1044366700572,
      -2.594512621651404
    ],
    [
      16.77797455796207,
      -2.691391780874973
    ],
    [
      18.41006777563645,
      -3.2283010177648674
    ],
    [
      19.959308400356726,
      -3.8678305594594065
    ],
    [
      21.55430492359737,
      -4.438217610473231
    ],
    [
      23.24364086375958,
      -4.84423780044653
    ],
    [
      24.965446620941446,
      -4.997096883324467
    ],
    [
      26.686069435104955,
      -4.919647816097344
    ],
    [
      28.4051598219143,
      -4.738928550934964
    ],
    [
      30.019636052614786,
      -5.035700431850815
    ],
    [
      31.38133291371738,
      -5.962838986344762
    ],
    [
      32.3590348260795,
      -7.351497746402415
    ],
    [
      33.109912827016785,
      -8.956988006839158
    ],
    [
      33.98484105256753,
      -10.45121579186497
    ],
    [
      35.09512745598835,
      -11.778230261592437
    ],
    [
      36.49449095256503,
      -12.788331621501452
    ],
    [
      38.116923594232254,
      -13.385120780340223
    ],
    [
      39.818459674512354,
      -13.709474883016462
    ],
    [
      41.55363228596211,
      -13.833551427243968
    ],
    [
      43.281916572759016,
      -13.748845280983637
    ],
    [
      44.953970605764326,
      -13.403984431552129
    ],
    [
      46.51707419834835,
      -12.649613808214237
    ],
    [
      47.68006389803265,
      -11.409725601921702
    ],
    [
      48.456271429775654,
      -9.919256064160734
    ],
    [
      48.664900080172934,
      -8.246135359227694
    ],
    [
      48.7144076882145,
      -6.5049842366883315
    ],
    [
      48.694441019871704,
      -4.772626727134989
    ],
    [
      48.72176528025204,
      -3.0493274681694986
    ],
    [
      48.764959596840505,
      -1.3204943030397627
    ],
    [
      48.809879223819316,
      0.40939123617725515
    ],
    [
      48.83154404871735,
      2.1357006129049236
    ],
    [
      48.82194852508874,
      3.867134746629745
    ],
    [
      48.83473573611625,
      5.616405230120563
    ],
    [
      48.84919930700568,
      7.367201409141031
    ],
    [
      48.67673180160502,
      9.069658061934682
    ],
    [
      48.190460916006494,
      10.696743784409751
    ],
    [
      47.241199288446694,
      11.99597926325041
    ],
    [
      45.806096344765876,
      12.99572413860361
    ],
    [
      44.16329147724983,
      13.56715161699432
    ],
    [
      42.447917044174545,
      13.784627816776437
    ],
    [
      40.730095939736046,
      13.754862230226507
    ],
    [
      39.04722814721289,
      13.370527496622099
    ],
    [
      37.501585857073295,
      12.724194457841687
    ],
    [
      36.10254070655711,
      11.831203074226995
    ],
    [
      34.97482734924413,
      10.649417101628888
    ],
    [
      34.05401031176452,
      9.168034231550767
    ],
    [
      33.154765134327455,
      7.650563607471366
    ],
    [
      32.186619940606214,
      6.291255492063428
    ],
    [
      30.876085004166217,
      5.35811002345825
    ],
    [
      29.24782315650223,
      4.879035307532277
    ],
    [
      27.525542138295897,
      4.770767828479917
    ],
    [
      25.838163913354528,
      4.751108344780416
    ],
    [
      24.151564918389106,
      4.9251563832031815
    ],
    [
      22.42866299148701,
      5.109610850562634
    ],
    [
      20.721354181400834,
      5.1043239110177705
    ],
    [
      19.013141064124035,
      4.788910532278003
    ],
    [
      17.32815524711286,
      4.293714907706866
    ],
    [
      15.702877745559215,
      4.054277710103639
    ],
    [
      14.148555623666626,
      4.287098172222102
    ],
    [
      12.763121570249872,
      5.039269344388252
    ],
    [
      11.759104829342014,
      6.369226835423565
    ],
    [
      10.899835160548058,
      7.863296171141123
    ],
    [
      9.918923018648108,
      9.287153553648897
    ],
    [
      8.823007245180515,
      10.628046067863973
    ],
    [
      7.454332632604724,
      11.664479646764063
    ],
    [
      5.909706561954277,
      12.451631962013213
    ],
    [
      4.27158539005124,
      13.028484359873369
    ],
    [
      2.5771985183284274,
      13.423795660238
    ],
    [
      0.8809987846323108,
      13.622332433670415
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "center": [
    -0.043870046734809875,
    -0.5707218497991562,
    -0.3415134400129318
  ],
  "construction_scale": 525.1153849283778
}
''')

def build():
    return build_model(PARAMETERS)

if __name__ == "__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==1
    cq.exporters.export(result,str(Path(__file__).with_suffix(".step")))
