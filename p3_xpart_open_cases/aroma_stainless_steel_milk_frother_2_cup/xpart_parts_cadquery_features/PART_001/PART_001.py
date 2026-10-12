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
    0.018509399333858652,
    0.03239583849690207
  ],
  "profile": [
    [
      1.0377881299216747,
      -47.621776580092
    ],
    [
      3.0437952457331168,
      -47.62007622917919
    ],
    [
      5.0728981161233495,
      -47.61828638238755
    ],
    [
      7.101901269087293,
      -47.636145817316766
    ],
    [
      9.127128142921578,
      -47.760469871983545
    ],
    [
      11.147800535219947,
      -47.88742100285178
    ],
    [
      13.150411372719994,
      -48.08159027202291
    ],
    [
      15.156164868821655,
      -48.25359360151748
    ],
    [
      17.149840353527377,
      -48.55936016998564
    ],
    [
      19.123621377780154,
      -48.64670648950982
    ],
    [
      21.129306712997007,
      -48.592541134971356
    ],
    [
      23.13256976239784,
      -48.64641583816877
    ],
    [
      25.08654554344263,
      -48.80870924655527
    ],
    [
      27.005435587430377,
      -48.60731293247669
    ],
    [
      28.78465402572477,
      -48.221779373268426
    ],
    [
      30.495668643817474,
      -48.0931833085846
    ],
    [
      30.978614949336894,
      -46.491411940688636
    ],
    [
      30.063631500440287,
      -44.7821036847091
    ],
    [
      29.717719988480738,
      -42.89712508888037
    ],
    [
      29.585788362082035,
      -40.87708994647453
    ],
    [
      29.586829614698207,
      -38.85493620066608
    ],
    [
      29.585801410816487,
      -36.83204263031729
    ],
    [
      29.510171028990687,
      -34.80883784020739
    ],
    [
      29.41543315298403,
      -32.78548341779155
    ],
    [
      29.261141131753185,
      -30.762077995550687
    ],
    [
      29.10916421094897,
      -28.73836655124327
    ],
    [
      29.048825872588267,
      -26.713781521320158
    ],
    [
      28.99472765782879,
      -24.688999065578074
    ],
    [
      28.929344597977455,
      -22.6647838729185
    ],
    [
      28.87888964223297,
      -20.64019406720356
    ],
    [
      28.862948529322466,
      -18.61467734986224
    ],
    [
      28.84023801909386,
      -16.58895008682685
    ],
    [
      28.819559582259828,
      -14.56343187629774
    ],
    [
      28.81058134898397,
      -12.539117175316328
    ],
    [
      28.794882536172516,
      -10.514669321608253
    ],
    [
      28.726668274840662,
      -8.495311812337773
    ],
    [
      28.70869809119912,
      -6.495106965046508
    ],
    [
      28.802202258985666,
      -4.4749955394319745
    ],
    [
      28.845160589312577,
      -2.4495095607149175
    ],
    [
      28.83138627189572,
      -0.42401641893314346
    ],
    [
      28.81731746739314,
      1.6029053277742311
    ],
    [
      28.820579377198648,
      3.6366368456272697
    ],
    [
      28.838788454689695,
      5.672067376997568
    ],
    [
      28.842800617591394,
      7.707296169695336
    ],
    [
      28.853830318293486,
      9.742769338476315
    ],
    [
      28.8637064878792,
      11.77805914186177
    ],
    [
      28.871102873624444,
      13.81165695705897
    ],
    [
      28.879432965700143,
      15.844193877851282
    ],
    [
      28.88755351466608,
      17.87658928792274
    ],
    [
      28.89293696157254,
      19.908686342802252
    ],
    [
      28.905125878356692,
      21.941100357847574
    ],
    [
      28.911009851557083,
      23.97346893160819
    ],
    [
      28.911164722943575,
      26.005766157945217
    ],
    [
      28.905366456458033,
      28.03808677594848
    ],
    [
      28.891389548580293,
      30.070373349034703
    ],
    [
      28.88233542077559,
      32.10270452235824
    ],
    [
      28.883370983437047,
      34.134994101962725
    ],
    [
      28.888330524747573,
      36.16693213594267
    ],
    [
      28.89494160379974,
      38.198021268369075
    ],
    [
      28.897177457517564,
      40.2261952861976
    ],
    [
      28.90095763046616,
      42.25164408035165
    ],
    [
      28.952136149267936,
      44.262903058594674
    ],
    [
      29.412559918863277,
      46.084032062553774
    ],
    [
      30.5884492591896,
      47.66887046931741
    ],
    [
      30.37881613282015,
      49.04279909530461
    ],
    [
      28.74683632829688,
      48.684514683083336
    ],
    [
      27.0290089532965,
      47.50510663449362
    ],
    [
      25.1895351167227,
      46.6023019652519
    ],
    [
      23.272005187312622,
      46.00909949945378
    ],
    [
      21.282813085423037,
      45.61486103848094
    ],
    [
      19.2671851942024,
      45.39335557327127
    ],
    [
      17.24088178984154,
      45.29207291994159
    ],
    [
      15.21452453469765,
      45.243266465184476
    ],
    [
      13.18886573829867,
      45.20912989196528
    ],
    [
      11.16006876604003,
      45.17027607131949
    ],
    [
      9.131170873091923,
      45.14916355791121
    ],
    [
      7.102216321073909,
      45.12659128488391
    ],
    [
      5.0731237257035415,
      45.10401771224726
    ],
    [
      3.043913120196366,
      45.09082083672081
    ],
    [
      1.0377555660217548,
      45.09613001464591
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
    -0.30483876,
    -0.41565362499999997,
    -0.0024865949999999803
  ],
  "construction_scale": 53.367151029597764,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
