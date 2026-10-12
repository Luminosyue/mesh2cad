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
    -0.13442836497837762,
    -0.05950615651440421
  ],
  "profile": [
    [
      0.8088733030491516,
      -22.61907439318087
    ],
    [
      2.3726192613988255,
      -22.624208286776216
    ],
    [
      3.954456580700459,
      -22.634882094188704
    ],
    [
      5.536342127482921,
      -22.64845515122377
    ],
    [
      7.118208351123876,
      -22.65968986712641
    ],
    [
      8.700230268239682,
      -22.669578242749104
    ],
    [
      10.28235619994124,
      -22.681229899883906
    ],
    [
      11.864444087196116,
      -22.694978437844764
    ],
    [
      13.446630847691662,
      -22.70595048221817
    ],
    [
      15.028741689593119,
      -22.7220289605893
    ],
    [
      16.610544355035614,
      -22.77250022271889
    ],
    [
      18.191892344270272,
      -22.850685759513034
    ],
    [
      19.772880695835003,
      -22.926723921670483
    ],
    [
      21.354029821138376,
      -22.99925383861912
    ],
    [
      22.9353410196198,
      -23.055642845973995
    ],
    [
      24.517112560794686,
      -23.102788702723046
    ],
    [
      26.09903543854875,
      -23.151238802322403
    ],
    [
      27.681090957558375,
      -23.17890663229826
    ],
    [
      29.26320738103889,
      -23.216522740730234
    ],
    [
      30.845256334379627,
      -23.27482451741999
    ],
    [
      32.42737799083897,
      -23.320747395486713
    ],
    [
      34.009597707319045,
      -23.33966720233019
    ],
    [
      35.591664772151624,
      -23.354031735726856
    ],
    [
      37.173777053197426,
      -23.36758966028269
    ],
    [
      38.75546160570441,
      -23.384431030379332
    ],
    [
      40.320973956957026,
      -23.407170158488235
    ],
    [
      41.896787330897986,
      -23.433893861076445
    ],
    [
      43.47821400187603,
      -23.454080604549254
    ],
    [
      44.96334771159382,
      -23.289835729734857
    ],
    [
      45.50169635417319,
      -22.09914792921313
    ],
    [
      45.456409459514404,
      -20.526364492922028
    ],
    [
      45.665549026694215,
      -19.021485804456262
    ],
    [
      46.73680285817473,
      -18.106071653265566
    ],
    [
      48.1433558154074,
      -17.53169409735426
    ],
    [
      49.28378505838457,
      -16.53215346986205
    ],
    [
      49.760184223282266,
      -15.064282606978328
    ],
    [
      49.773445126808284,
      -13.490810490114695
    ],
    [
      49.60837550728739,
      -11.922134564623228
    ],
    [
      49.376618588704375,
      -10.364965060693297
    ],
    [
      49.10496621981193,
      -8.812866571845245
    ],
    [
      48.76943662933619,
      -7.270391842942898
    ],
    [
      48.37316025697554,
      -5.73958860097104
    ],
    [
      47.90946469254693,
      -4.229014261360593
    ],
    [
      47.36837621101827,
      -2.7466234888946146
    ],
    [
      46.77962737110704,
      -1.2749391543772546
    ],
    [
      46.115020677076075,
      0.1659900946853355
    ],
    [
      45.39099861848415,
      1.579853667485875
    ],
    [
      44.61218469424902,
      2.955452883202476
    ],
    [
      43.75341795688493,
      4.292184867608654
    ],
    [
      42.822363989736274,
      5.5805181516102955
    ],
    [
      41.848956401597405,
      6.814062597802016
    ],
    [
      40.814658242215344,
      8.01076034397898
    ],
    [
      39.72732534738886,
      9.183548729437373
    ],
    [
      38.60020932039514,
      10.293173210970023
    ],
    [
      37.42594149361615,
      11.347571609528721
    ],
    [
      36.20644303386063,
      12.360587685412046
    ],
    [
      34.958203673106034,
      13.3233401800424
    ],
    [
      33.68575824222751,
      14.25047288412514
    ],
    [
      32.38545792612878,
      15.14983786159378
    ],
    [
      31.053826187909007,
      16.013207297766865
    ],
    [
      29.688178859243813,
      16.818952945934505
    ],
    [
      28.294742554833707,
      17.580609381477508
    ],
    [
      26.889175162107676,
      18.301732773583954
    ],
    [
      25.456656129292973,
      18.96140754710102
    ],
    [
      23.999815451576094,
      19.581257148424413
    ],
    [
      22.52387234774829,
      20.162444969434482
    ],
    [
      21.031839879051983,
      20.65605385597111
    ],
    [
      19.529687586346835,
      21.11920188950827
    ],
    [
      18.01316604722498,
      21.54813198441662
    ],
    [
      16.48167884068433,
      21.94395060053052
    ],
    [
      14.941756816085332,
      22.29025056451873
    ],
    [
      13.38848564521594,
      22.585173312880407
    ],
    [
      11.82698481848098,
      22.84092959132493
    ],
    [
      10.261414951305728,
      23.065280529315658
    ],
    [
      8.689682855613409,
      23.252386599894166
    ],
    [
      7.113314307613278,
      23.39743976639941
    ],
    [
      5.534546305069623,
      23.503219377789904
    ],
    [
      3.9545505047624627,
      23.585462197301908
    ],
    [
      2.373250097326162,
      23.640370529458053
    ],
    [
      0.8092121580279732,
      23.667225710176012
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
    -0.01563182000000002,
    -0.0036830850000000304,
    0.71719069
  ],
  "construction_scale": 83.98738438937069,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
