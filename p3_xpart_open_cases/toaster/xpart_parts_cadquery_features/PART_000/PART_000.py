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
    0.32399283306478827,
    0.08170520428058466
  ],
  "profile": [
    [
      1.2663749790063887,
      23.02754922103675
    ],
    [
      3.714251017082231,
      23.02706666780287
    ],
    [
      6.19039866802445,
      22.996801034455032
    ],
    [
      8.666190829144385,
      22.949228637970304
    ],
    [
      11.141561505174282,
      22.894295113579005
    ],
    [
      13.61579962560424,
      22.80801452703828
    ],
    [
      16.089625913245335,
      22.705651695751435
    ],
    [
      18.562384865147546,
      22.59607985690777
    ],
    [
      21.034487999554074,
      22.46896148107179
    ],
    [
      23.506370656304654,
      22.328377016528982
    ],
    [
      25.978338336129767,
      22.16317187699085
    ],
    [
      28.451325291526608,
      22.00942791044548
    ],
    [
      30.847180205023186,
      21.709319063257915
    ],
    [
      32.55088597100821,
      20.21200154986115
    ],
    [
      33.006482650151334,
      17.861746855196365
    ],
    [
      33.01530048516873,
      15.385146580945419
    ],
    [
      33.000267495010505,
      12.906517906047132
    ],
    [
      32.9901369879746,
      10.428022174980986
    ],
    [
      32.9769639764791,
      7.9494814422854585
    ],
    [
      32.97938194849425,
      5.471040536976243
    ],
    [
      32.99834224473183,
      2.9925974711507695
    ],
    [
      33.00554241140303,
      0.5145065392624383
    ],
    [
      33.00878569341144,
      -1.9612257311037906
    ],
    [
      33.02933041241819,
      -4.435330442702767
    ],
    [
      32.897295331395284,
      -6.90590431778502
    ],
    [
      32.66039612879589,
      -9.369581846015034
    ],
    [
      32.57100409719685,
      -11.83853639678345
    ],
    [
      32.6197403006731,
      -14.312477794518198
    ],
    [
      32.65572397131258,
      -16.787230620066463
    ],
    [
      32.6228038454817,
      -19.259940570129125
    ],
    [
      32.76563239443788,
      -21.7098944533294
    ],
    [
      33.31440899535511,
      -24.106076091168234
    ],
    [
      33.59117523833208,
      -26.548215590354076
    ],
    [
      34.47130194901498,
      -28.63716315493566
    ],
    [
      36.56146850689372,
      -29.41587227867825
    ],
    [
      38.66013561280707,
      -28.741529616964904
    ],
    [
      39.76893790443125,
      -26.831377354894748
    ],
    [
      40.61049878481127,
      -24.496600032420194
    ],
    [
      41.72830846871214,
      -22.29652659071857
    ],
    [
      42.04598545667594,
      -19.89265793510218
    ],
    [
      42.07062075307429,
      -17.420654251726813
    ],
    [
      42.10966982685933,
      -14.945919664462265
    ],
    [
      42.367204519806435,
      -12.528405971332626
    ],
    [
      43.8322324778246,
      -11.014116310687651
    ],
    [
      46.20849485349102,
      -10.73832495790441
    ],
    [
      48.537913505550605,
      -10.21527188004612
    ],
    [
      49.82524826148519,
      -8.325971540064003
    ],
    [
      49.742475013284235,
      -5.998193979643808
    ],
    [
      48.267259503269656,
      -4.369294606170937
    ],
    [
      45.9103664368109,
      -4.004190275076615
    ],
    [
      43.44828270404136,
      -3.981779446680841
    ],
    [
      41.226355147502105,
      -3.383676096475045
    ],
    [
      40.05128045832108,
      -1.4621651188190916
    ],
    [
      39.90251603725588,
      0.9751988846248135
    ],
    [
      39.86766743316423,
      3.440892605107455
    ],
    [
      39.86136278083604,
      5.906283014218698
    ],
    [
      39.86763628421259,
      8.374952107217853
    ],
    [
      39.849564687524776,
      10.854135942367723
    ],
    [
      39.85706443583646,
      13.335016722229003
    ],
    [
      39.83763658149849,
      15.815990364613306
    ],
    [
      39.81905112364904,
      18.296744423943966
    ],
    [
      39.79484183955313,
      20.7772283856278
    ],
    [
      39.73570493576817,
      23.248482772246803
    ],
    [
      39.103199893870226,
      25.608274349922972
    ],
    [
      37.685432081970646,
      27.63614752658018
    ],
    [
      35.71637110582524,
      29.06235307315142
    ],
    [
      33.37324484688389,
      29.51122648224207
    ],
    [
      30.922702910644944,
      29.337695041880373
    ],
    [
      28.45848968954398,
      29.149624526168687
    ],
    [
      25.983869170829788,
      29.144499948385366
    ],
    [
      23.5094347332956,
      29.24437874996414
    ],
    [
      21.03623921564506,
      29.356638872669585
    ],
    [
      18.562575115662483,
      29.46564731362516
    ],
    [
      16.089868514179344,
      29.59599714511433
    ],
    [
      13.617026002068988,
      29.72436190584947
    ],
    [
      11.14209715657993,
      29.82766101625783
    ],
    [
      8.66659615088519,
      29.89466145507474
    ],
    [
      6.190716073921543,
      29.931808971270463
    ],
    [
      3.714537259248465,
      29.954110096296333
    ],
    [
      1.2664194471557608,
      29.961465075256978
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      0.0,
      0.0,
      1.0
    ],
    [
      1.0,
      0.0,
      0.0
    ],
    [
      0.0,
      1.0,
      0.0
    ]
  ],
  "axis_candidate": 1,
  "center": [
    -0.27146199,
    0.814291835,
    -0.26385003
  ],
  "construction_scale": 405.94112700785587,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
