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
    0.0851417001256534,
    -0.05310883998380757
  ],
  "profile": [
    [
      0.7947548128202009,
      -49.84007259624791
    ],
    [
      2.3311754695473073,
      -49.84130314650662
    ],
    [
      3.8853084347432563,
      -49.84370178459531
    ],
    [
      5.439370769927416,
      -49.85108563058125
    ],
    [
      6.993331366305399,
      -49.86248909636336
    ],
    [
      8.547269740071002,
      -49.877093515592605
    ],
    [
      10.099971040526807,
      -49.86602968445108
    ],
    [
      11.61421765116091,
      -49.63058105222022
    ],
    [
      12.86802532385494,
      -48.81147961998719
    ],
    [
      13.599503874781146,
      -47.524445796474126
    ],
    [
      13.756760108973417,
      -46.00030980495236
    ],
    [
      13.763177053887532,
      -44.44656737371538
    ],
    [
      13.77144783204146,
      -42.89115262496116
    ],
    [
      13.774045734542213,
      -41.33849855290616
    ],
    [
      13.772046706797983,
      -39.78859052353975
    ],
    [
      13.765320788324965,
      -38.23698683447803
    ],
    [
      13.759165241644165,
      -36.68512806181108
    ],
    [
      13.758403012550268,
      -35.13324253118783
    ],
    [
      13.75588943060816,
      -33.58128197558384
    ],
    [
      13.756145286473485,
      -32.02670083563738
    ],
    [
      13.749300475368575,
      -30.469736977928854
    ],
    [
      13.748753661278013,
      -28.912671612315968
    ],
    [
      13.743916066115748,
      -27.35630539186203
    ],
    [
      13.736115483405637,
      -25.803771729556473
    ],
    [
      13.730023306012527,
      -24.251908361747105
    ],
    [
      13.722440101200444,
      -22.700161245410477
    ],
    [
      13.728165017022286,
      -21.148364108225785
    ],
    [
      13.73039078382157,
      -19.59647520648275
    ],
    [
      13.72566999825876,
      -18.04389638399742
    ],
    [
      13.725562634252038,
      -16.48979858780996
    ],
    [
      13.722287939601525,
      -14.93558325423918
    ],
    [
      13.723914146999514,
      -13.381384259359002
    ],
    [
      13.723270752444236,
      -11.827093303302814
    ],
    [
      13.72071233589324,
      -10.272780010490163
    ],
    [
      13.7182152524955,
      -8.718496606281796
    ],
    [
      13.718836829197265,
      -7.164203468074097
    ],
    [
      13.713513057798721,
      -5.609904730505827
    ],
    [
      13.709967123700636,
      -4.055419640491119
    ],
    [
      13.70978928253837,
      -2.499270909398412
    ],
    [
      13.70813871536296,
      -0.9421553695732998
    ],
    [
      13.70190753894799,
      0.6149844630695759
    ],
    [
      13.701927553506241,
      2.1721192768771784
    ],
    [
      13.70091880388097,
      3.7291996581473246
    ],
    [
      13.697794938177049,
      5.2843394876941625
    ],
    [
      13.697081974630887,
      6.837140935454524
    ],
    [
      13.695735018714885,
      8.38978483474598
    ],
    [
      13.689681993538557,
      9.9423159647881
    ],
    [
      13.681733564423443,
      11.494916342782094
    ],
    [
      13.679074937322273,
      13.047602984964815
    ],
    [
      13.682402424963122,
      14.600311112368708
    ],
    [
      13.677180559111175,
      16.153174444750842
    ],
    [
      13.680842207010423,
      17.70852425220138
    ],
    [
      13.679459369710205,
      19.265865534099724
    ],
    [
      13.686195007881803,
      20.823227131053493
    ],
    [
      13.692673402225521,
      22.380596441585723
    ],
    [
      13.69828175629034,
      23.937997546318307
    ],
    [
      13.69818735661434,
      25.495352194993764
    ],
    [
      13.696852424731677,
      27.05274006229225
    ],
    [
      13.696338476036157,
      28.610149005211447
    ],
    [
      13.70489930946808,
      30.167452714535628
    ],
    [
      13.707740219828,
      31.724268563067326
    ],
    [
      13.709407959295136,
      33.27883453994684
    ],
    [
      13.709342881461488,
      34.83233064611937
    ],
    [
      13.712251095379134,
      36.38580280232565
    ],
    [
      13.704070255742128,
      37.93911964130561
    ],
    [
      13.703362295269098,
      39.49228185706771
    ],
    [
      13.701188103816254,
      41.04558021538406
    ],
    [
      13.691433120106415,
      42.59896024371307
    ],
    [
      13.676604100643814,
      44.152358789282815
    ],
    [
      13.654246313178515,
      45.70527553890178
    ],
    [
      13.471008176831408,
      47.23249535020692
    ],
    [
      12.781449017706953,
      48.58456183749702
    ],
    [
      11.587315442713043,
      49.507024117015575
    ],
    [
      10.09952746192804,
      49.85690277676913
    ],
    [
      8.547594451729815,
      49.90038887866509
    ],
    [
      6.993616690196108,
      49.89621051361648
    ],
    [
      5.439533161029033,
      49.890975065648185
    ],
    [
      3.8853622263244727,
      49.89427781147975
    ],
    [
      2.331188591454773,
      49.893293123223486
    ],
    [
      0.7947704150148638,
      49.88993449117406
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      -0.06498479021396827,
      0.9978861479515571,
      -0.0004612670042516015
    ],
    [
      0.9978848444407558,
      0.0649854685351103,
      0.0016510950066723207
    ],
    [
      0.0016775804885013632,
      -0.00035299529015111005,
      -0.9999985305579349
    ]
  ],
  "axis_candidate": 3,
  "center": [
    -0.342861305,
    0.216618795,
    -0.07656132
  ],
  "construction_scale": 216.4114216581348,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
