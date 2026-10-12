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
    -0.006496892178964801,
    -0.005805074908422183
  ],
  "profile": [
    [
      0.22350515110578828,
      -49.922956354568214
    ],
    [
      1.635019235527111,
      -49.92028027475116
    ],
    [
      3.26932849094289,
      -49.92135670321083
    ],
    [
      4.903997310259965,
      -49.92119077520407
    ],
    [
      6.538663503218262,
      -49.92141039784556
    ],
    [
      8.173324740224615,
      -49.92378435909474
    ],
    [
      9.807973500808556,
      -49.931699197495135
    ],
    [
      11.442418439584614,
      -49.94042642300441
    ],
    [
      13.054110856007036,
      -49.8051156402353
    ],
    [
      14.259746349747557,
      -48.96261646563333
    ],
    [
      14.492454375737557,
      -47.41965875187287
    ],
    [
      14.474934657620885,
      -45.78578525947239
    ],
    [
      14.311602513606534,
      -44.185482593640586
    ],
    [
      13.477921752395863,
      -42.84266813812765
    ],
    [
      12.377955082704563,
      -41.639838841396546
    ],
    [
      11.28121456729687,
      -40.43477460196908
    ],
    [
      10.365166574049294,
      -39.136605742254474
    ],
    [
      9.993527919282531,
      -37.57467855833768
    ],
    [
      9.901215117437875,
      -35.943748674090074
    ],
    [
      9.893133357089205,
      -34.30853904568432
    ],
    [
      9.886575208348187,
      -32.67304921911631
    ],
    [
      9.887477580055414,
      -31.03757486618845
    ],
    [
      9.88821800585368,
      -29.40208864709654
    ],
    [
      9.886661636737283,
      -27.76660503305728
    ],
    [
      9.889191323074524,
      -26.131144468486454
    ],
    [
      9.893698651836647,
      -24.495643431257864
    ],
    [
      9.90152344863495,
      -22.860139907308895
    ],
    [
      9.903456526773347,
      -21.22465043670534
    ],
    [
      9.901844376872006,
      -19.589141862831
    ],
    [
      9.89855886696019,
      -17.95365714484057
    ],
    [
      9.895532652001641,
      -16.319075784329407
    ],
    [
      9.894627812997069,
      -14.685487151664187
    ],
    [
      9.893219989691467,
      -13.051160233032235
    ],
    [
      9.891902993079565,
      -11.416320703051872
    ],
    [
      9.890832142549822,
      -9.781484348297496
    ],
    [
      9.889649894866507,
      -8.14653639252132
    ],
    [
      9.892971666767956,
      -6.511082335611093
    ],
    [
      9.894515784338758,
      -4.875161653319449
    ],
    [
      9.893600873114796,
      -3.238551410615265
    ],
    [
      9.894582392578934,
      -1.6031900082515245
    ],
    [
      9.894636484666957,
      0.030888098168136903
    ],
    [
      9.894320448709037,
      1.6637682605178492
    ],
    [
      9.893237066507158,
      3.2953378738002006
    ],
    [
      9.892316872800192,
      4.927002071531895
    ],
    [
      9.889598306576193,
      6.56024109772825
    ],
    [
      9.892069065015797,
      8.193595150540537
    ],
    [
      9.893187489476023,
      9.827458977315082
    ],
    [
      9.892105517856056,
      11.46259119179251
    ],
    [
      9.891299931946193,
      13.09792185192839
    ],
    [
      9.892063845173123,
      14.733283697100177
    ],
    [
      9.894082164775565,
      16.368400899438036
    ],
    [
      9.900685789661566,
      18.00273818940724
    ],
    [
      9.905680777555732,
      19.636977485480116
    ],
    [
      9.904615893674722,
      21.27122388110294
    ],
    [
      9.897807904505488,
      22.905435583322276
    ],
    [
      9.891803244104771,
      24.539576263407966
    ],
    [
      9.889690332144712,
      26.173769609863434
    ],
    [
      9.888558766595718,
      27.807983132435623
    ],
    [
      9.888084910068855,
      29.442182566723247
    ],
    [
      9.887515886505785,
      31.076381788298804
    ],
    [
      9.891292766723518,
      32.71060921901286
    ],
    [
      9.899948683905937,
      34.34481402948962
    ],
    [
      9.913111607168384,
      35.97876523479092
    ],
    [
      10.033685601773048,
      37.60516904505137
    ],
    [
      10.465835742871043,
      39.15083941926784
    ],
    [
      11.437167995487068,
      40.433949657680024
    ],
    [
      12.535533421676387,
      41.65046575892862
    ],
    [
      13.63886929598721,
      42.85913662577896
    ],
    [
      14.387015599308555,
      44.24155811348299
    ],
    [
      14.48735834836812,
      45.85661572739076
    ],
    [
      14.49557388562743,
      47.49097108347638
    ],
    [
      14.274775197168985,
      49.03860648951344
    ],
    [
      13.05601618438795,
      49.84475801244514
    ],
    [
      11.442255372427418,
      49.96248377184327
    ],
    [
      9.807832373363876,
      49.947734745810095
    ],
    [
      8.173241220247899,
      49.93611538969682
    ],
    [
      6.538579739485428,
      49.92872685245716
    ],
    [
      4.903915502746216,
      49.92589140468526
    ],
    [
      3.269224898105643,
      49.92508368971827
    ],
    [
      1.6349175136520122,
      49.92193752728927
    ],
    [
      0.22347876010506107,
      49.92537232116341
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
    0.00036395000000000177,
    0.0002539150000000004,
    0.0002616650000000012
  ],
  "construction_scale": 253.22911435902773,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
