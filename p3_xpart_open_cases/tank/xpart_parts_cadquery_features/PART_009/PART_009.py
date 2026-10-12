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
    -0.8076129778299881,
    -0.14538766114897514
  ],
  "profile": [
    [
      1.0609022917913047,
      -29.823382913972324
    ],
    [
      3.11179106575064,
      -29.826866095932168
    ],
    [
      5.186336197176893,
      -29.82665024728174
    ],
    [
      7.260879459962015,
      -29.82579724768715
    ],
    [
      9.335426403693777,
      -29.83464669781153
    ],
    [
      11.4099882138902,
      -29.84192099170891
    ],
    [
      13.48454748150603,
      -29.84605258003545
    ],
    [
      15.559074057592994,
      -29.84904885128057
    ],
    [
      17.633568439268117,
      -29.863709078454235
    ],
    [
      19.708060781917574,
      -29.866088297354157
    ],
    [
      21.782585737613104,
      -29.871015839696618
    ],
    [
      23.857124969525916,
      -29.878593973317603
    ],
    [
      25.93166117544001,
      -29.876151282182626
    ],
    [
      28.006194100457094,
      -29.882251566669495
    ],
    [
      30.08066575404341,
      -29.86482385731097
    ],
    [
      32.15513427564417,
      -29.8512027937141
    ],
    [
      34.22963489557169,
      -29.856359518241675
    ],
    [
      36.3041961962291,
      -29.857197431407602
    ],
    [
      38.378724103115246,
      -29.85420236805222
    ],
    [
      40.453230104428016,
      -29.862012425507668
    ],
    [
      42.52754402197347,
      -29.869614902071028
    ],
    [
      44.5934923718618,
      -29.745364392583667
    ],
    [
      46.49053462289709,
      -29.13048345980821
    ],
    [
      47.632818559649166,
      -27.658256249078782
    ],
    [
      48.34344228475736,
      -25.74600325332783
    ],
    [
      48.73652833896555,
      -23.737529291553763
    ],
    [
      48.92192348602596,
      -21.697976850786326
    ],
    [
      49.013839505110155,
      -19.648549649937276
    ],
    [
      49.063534894517105,
      -17.58621042960452
    ],
    [
      49.09459908324213,
      -15.509452797166695
    ],
    [
      49.10899893921311,
      -13.430874312544084
    ],
    [
      49.15323839918746,
      -11.352131972208074
    ],
    [
      49.169516176699894,
      -9.275103861950678
    ],
    [
      49.06276062041934,
      -7.231356943400277
    ],
    [
      48.63357260876173,
      -5.273028202872796
    ],
    [
      47.85937783595314,
      -3.412505687073253
    ],
    [
      46.76817709974121,
      -1.711237696570279
    ],
    [
      45.50433945303024,
      -0.11149608247062132
    ],
    [
      45.32211987267857,
      1.761734821585328
    ],
    [
      46.507240173721854,
      3.199007279765761
    ],
    [
      47.98928867290819,
      4.467345850181607
    ],
    [
      48.744401162332764,
      6.252642588469727
    ],
    [
      48.88156626052772,
      8.306466778211405
    ],
    [
      48.90837584419691,
      10.362658475502869
    ],
    [
      48.95680370384862,
      12.417393895887116
    ],
    [
      48.983364449739014,
      14.47891430000293
    ],
    [
      48.99278568007422,
      16.543633576043497
    ],
    [
      48.99004412326903,
      18.608745236173895
    ],
    [
      48.98492291520016,
      20.67388645706948
    ],
    [
      48.96204129029067,
      22.73868445676102
    ],
    [
      48.7799352097151,
      24.793170405969065
    ],
    [
      48.09732941797978,
      26.67885793203169
    ],
    [
      46.75505672024032,
      28.253164973728794
    ],
    [
      44.96094808218952,
      29.078986412084916
    ],
    [
      42.9332308388113,
      29.359150007448914
    ],
    [
      40.878762212398584,
      29.438876504400447
    ],
    [
      38.83849980377576,
      29.316069380325438
    ],
    [
      36.90088920450599,
      28.714553318496684
    ],
    [
      35.20605275478151,
      27.519288330692795
    ],
    [
      33.74972211562916,
      26.014684210857276
    ],
    [
      32.663176292119836,
      24.30096494237387
    ],
    [
      31.736397676656903,
      22.537565448171637
    ],
    [
      30.583027882978342,
      20.96803558541012
    ],
    [
      28.73514658614718,
      20.485494222627683
    ],
    [
      26.694645327529713,
      20.731135587787684
    ],
    [
      24.63859610502996,
      20.777319283478494
    ],
    [
      22.650052110878658,
      20.315017079927728
    ],
    [
      20.760764996658917,
      19.508948890304296
    ],
    [
      18.89287785837282,
      18.658060523415415
    ],
    [
      16.959504698206707,
      18.0827993415066
    ],
    [
      14.954919707507464,
      18.21377271342825
    ],
    [
      13.163754362372833,
      19.0461303268539
    ],
    [
      11.76532353058677,
      20.43561245867152
    ],
    [
      10.584993588482094,
      22.15530780672274
    ],
    [
      9.42637578305915,
      23.88307001799474
    ],
    [
      8.174631861453683,
      25.529774433357787
    ],
    [
      6.714183348493841,
      26.971548168827674
    ],
    [
      4.9974025260990835,
      28.105209394077118
    ],
    [
      3.0740430948093884,
      28.84757909830629
    ],
    [
      1.0583218731325126,
      29.12964102845197
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "center": [
    -0.04398589767515659,
    -0.569969967007637,
    0.31046172976493835
  ],
  "construction_scale": 527.1352406968648
}
''')

def build():
    return build_model(PARAMETERS)

if __name__ == "__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==1
    cq.exporters.export(result,str(Path(__file__).with_suffix(".step")))
