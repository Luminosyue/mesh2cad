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
    0.3366892793825673,
    -0.8488554650732056
  ],
  "profile": [
    [
      1.36306889806198,
      29.913446144207057
    ],
    [
      3.989329526171341,
      30.182372903788828
    ],
    [
      6.61338184801676,
      30.709525818608583
    ],
    [
      9.215070984935444,
      31.208129353434227
    ],
    [
      11.81433946233965,
      31.942008255380777
    ],
    [
      14.484581527167549,
      32.31466099899264
    ],
    [
      17.143350146001712,
      32.50374323812702
    ],
    [
      19.692246708834297,
      32.831576319753694
    ],
    [
      22.35140553102535,
      33.00473618158952
    ],
    [
      25.030915701720694,
      32.9009763452779
    ],
    [
      27.646007111603865,
      32.26834388341742
    ],
    [
      29.970799280289953,
      30.99629655571119
    ],
    [
      32.16954717953648,
      29.54492969484258
    ],
    [
      34.286061135936635,
      27.801529527427807
    ],
    [
      36.26590923436133,
      25.9480305965997
    ],
    [
      38.2057575276752,
      24.075502964799973
    ],
    [
      40.04196252333702,
      22.144702760264583
    ],
    [
      41.76646345868457,
      20.134847558948124
    ],
    [
      43.39889659551156,
      17.8480815784811
    ],
    [
      44.19412542228439,
      15.316915809003994
    ],
    [
      44.67405094939913,
      12.656353142035359
    ],
    [
      45.03133293689936,
      9.974225655255761
    ],
    [
      45.147712398681975,
      7.289419677972036
    ],
    [
      45.18961512714995,
      4.621127636402034
    ],
    [
      45.21195621518761,
      1.96453500388174
    ],
    [
      45.23037636415114,
      -0.6926347918958443
    ],
    [
      45.25435108597904,
      -3.3499299091049863
    ],
    [
      45.2717922079121,
      -6.007652464003035
    ],
    [
      45.30609193186699,
      -8.66526625419597
    ],
    [
      45.34469415358875,
      -11.323039302078453
    ],
    [
      45.42094366225121,
      -13.9809691866454
    ],
    [
      45.45442911152281,
      -16.638852851739923
    ],
    [
      45.46423870313582,
      -19.296314411904806
    ],
    [
      45.47446707396701,
      -21.93876244080858
    ],
    [
      45.50370297556513,
      -24.559563258949225
    ],
    [
      45.54275198518643,
      -27.216984942082547
    ],
    [
      45.59027103206257,
      -29.898306861655023
    ],
    [
      45.82338084873774,
      -32.56263273866165
    ],
    [
      46.76178116711759,
      -34.78986488215115
    ],
    [
      48.147830936685644,
      -34.603569666881576
    ],
    [
      48.99766657092139,
      -32.29030329711879
    ],
    [
      49.241791702789385,
      -29.63887910075075
    ],
    [
      49.24165917670311,
      -26.958310070570498
    ],
    [
      49.197694928285365,
      -24.26045055226173
    ],
    [
      49.193451759268214,
      -21.55907521430749
    ],
    [
      49.129678801395215,
      -18.87916706186386
    ],
    [
      49.06814575476915,
      -16.203112643177498
    ],
    [
      49.057261393272775,
      -13.527525753710787
    ],
    [
      49.01765473851379,
      -10.851505023815701
    ],
    [
      48.973326532546345,
      -8.181108800920581
    ],
    [
      48.974673735451276,
      -5.514560043668351
    ],
    [
      48.956174856046644,
      -2.839557372261277
    ],
    [
      48.89892496464569,
      -0.16038861599944326
    ],
    [
      48.7412156111656,
      2.515849566109366
    ],
    [
      48.45687053319265,
      5.192747186181031
    ],
    [
      48.23993433906955,
      7.868147482227464
    ],
    [
      48.093044799488496,
      10.541313835102773
    ],
    [
      48.06488412669917,
      13.215734884910812
    ],
    [
      47.96348337560845,
      15.876348494175742
    ],
    [
      47.51163690248035,
      18.393022057221742
    ],
    [
      46.247970686813126,
      20.719372659937534
    ],
    [
      44.61035280627809,
      22.887220215045737
    ],
    [
      42.89728485359669,
      24.886264225046716
    ],
    [
      41.08289454820989,
      26.806215501985733
    ],
    [
      39.1808985194112,
      28.60678163129809
    ],
    [
      37.24438094387222,
      30.421018125904148
    ],
    [
      35.28602896500598,
      32.205154176893785
    ],
    [
      33.016358087995144,
      33.685825886805624
    ],
    [
      30.51833951562675,
      34.49109866209818
    ],
    [
      27.919858402539013,
      35.29764482012529
    ],
    [
      25.273579415578794,
      35.696178646091326
    ],
    [
      22.609212462668573,
      35.73425161768019
    ],
    [
      19.93567346605248,
      35.7059290444041
    ],
    [
      17.24412710778669,
      35.66961110072192
    ],
    [
      14.597201223428454,
      35.306814974938106
    ],
    [
      11.927219334334627,
      34.86038138160738
    ],
    [
      9.253017110048727,
      34.383333565255
    ],
    [
      6.599553173940007,
      33.935197227813084
    ],
    [
      3.9633928276996775,
      33.903861790233826
    ],
    [
      1.3601067738284125,
      33.77067115448834
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      -0.9905669255034608,
      0.13519714950922054,
      -0.022335999265817776
    ],
    [
      -0.13554800645975446,
      -0.9906570019655166,
      0.015014739474284926
    ],
    [
      -0.0200973640910321,
      0.0179007044910459,
      0.9996377647604742
    ]
  ],
  "axis_candidate": 5,
  "center": [
    0.089886105,
    0.455060115,
    0.849889595
  ],
  "construction_scale": 407.9004608663357,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
