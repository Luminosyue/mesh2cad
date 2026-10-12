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
    -0.1488406368709688,
    0.12050761006557145
  ],
  "profile": [
    [
      1.068172036306253,
      -23.057676744894763
    ],
    [
      3.1330949880811287,
      -23.054292965346686
    ],
    [
      5.221810647820472,
      -23.04815259051754
    ],
    [
      7.310500697506102,
      -23.037441140501056
    ],
    [
      9.399157458476054,
      -23.017518650514667
    ],
    [
      11.487802934306202,
      -22.99311584066864
    ],
    [
      13.576435158301537,
      -22.97021824227746
    ],
    [
      15.665042388373909,
      -22.952480697016696
    ],
    [
      17.753599944063083,
      -22.929085984083283
    ],
    [
      19.842078992814443,
      -22.895511756206464
    ],
    [
      21.93045390055771,
      -22.855856141379526
    ],
    [
      24.018832434626,
      -22.815112899088312
    ],
    [
      26.10719254037636,
      -22.775712729885058
    ],
    [
      28.195625350307782,
      -22.742368073270836
    ],
    [
      30.284213018576473,
      -22.730133589770094
    ],
    [
      32.37182552191908,
      -22.709763488413742
    ],
    [
      34.41487621731223,
      -22.426524522047558
    ],
    [
      36.17661609042396,
      -21.41449015471904
    ],
    [
      37.55402643164608,
      -19.88198140990874
    ],
    [
      38.6962364531698,
      -18.13579436568919
    ],
    [
      39.737586824762175,
      -16.318148718963258
    ],
    [
      40.73827779764388,
      -14.481765733330732
    ],
    [
      41.69195775853348,
      -12.62765796805867
    ],
    [
      42.57928459409732,
      -10.74797169481052
    ],
    [
      43.4206888510651,
      -8.849263212565338
    ],
    [
      44.2537463145007,
      -6.925725408109327
    ],
    [
      45.027935332560055,
      -4.98305567926805
    ],
    [
      45.747049589519264,
      -3.0184823501206903
    ],
    [
      46.39385976634135,
      -1.0404008732147558
    ],
    [
      46.977004412620886,
      0.9561103724526958
    ],
    [
      47.51719269941602,
      2.9757181064256777
    ],
    [
      47.989221405594485,
      5.011138137718603
    ],
    [
      48.411063353866474,
      7.0557893291387845
    ],
    [
      48.75348041896494,
      9.11224604827591
    ],
    [
      49.0222860075439,
      11.17978048331337
    ],
    [
      49.23418786004798,
      13.254411763347468
    ],
    [
      49.39067365189974,
      15.335568742913008
    ],
    [
      49.49652628710978,
      17.419474275728398
    ],
    [
      49.607627494753935,
      19.503715602559218
    ],
    [
      49.697655408537116,
      21.561394350909325
    ],
    [
      49.33783100020792,
      22.25485572942407
    ],
    [
      49.125936673947564,
      20.45673686155073
    ],
    [
      49.01955809728435,
      18.373010437218767
    ],
    [
      48.918379198472195,
      16.288574515257032
    ],
    [
      48.78780585859792,
      14.205232396654338
    ],
    [
      48.59315165952277,
      12.1234266655059
    ],
    [
      48.358829838631024,
      10.048329825892726
    ],
    [
      48.04969465853072,
      7.988436423963858
    ],
    [
      47.66172643981645,
      5.9387208314318745
    ],
    [
      47.20381597275105,
      3.8993253636147145
    ],
    [
      46.69458453586215,
      1.8723100069584178
    ],
    [
      46.13058064955949,
      -0.1328485229839521
    ],
    [
      45.50799256452965,
      -2.126195747583564
    ],
    [
      44.82154207633211,
      -4.097174585484634
    ],
    [
      44.06148026228234,
      -6.039778563166323
    ],
    [
      43.23619667698017,
      -7.970210700610712
    ],
    [
      42.397931678851336,
      -9.883991650813707
    ],
    [
      41.52106397063002,
      -11.775158276192467
    ],
    [
      40.59315059309261,
      -13.635756874061787
    ],
    [
      39.59651398430739,
      -15.475995444445612
    ],
    [
      38.57095096285034,
      -17.29132551478699
    ],
    [
      37.4704548145056,
      -19.062263084323625
    ],
    [
      36.155894941620296,
      -20.650329165809044
    ],
    [
      34.42231238149194,
      -21.671088672021465
    ],
    [
      32.37225422611016,
      -21.894276556774038
    ],
    [
      30.283958445442757,
      -21.904331220002625
    ],
    [
      28.195436228940522,
      -21.918894194718668
    ],
    [
      26.10723733257484,
      -21.954942467839764
    ],
    [
      24.019076732197135,
      -21.992386899001566
    ],
    [
      21.930814252232324,
      -22.02561233857446
    ],
    [
      19.842442877563954,
      -22.063627125621025
    ],
    [
      17.753918347232243,
      -22.09315195318496
    ],
    [
      15.665296481196057,
      -22.1148725423038
    ],
    [
      13.576626843186727,
      -22.135311190179806
    ],
    [
      11.48793328359938,
      -22.151011028440312
    ],
    [
      9.39924295891895,
      -22.168528227999296
    ],
    [
      7.310537096945922,
      -22.184845184292392
    ],
    [
      5.221826265566298,
      -22.195303517773
    ],
    [
      3.133097403771961,
      -22.203783131486993
    ],
    [
      1.0681743361794798,
      -22.203487984034233
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
    -0.00046733500000001316,
    0.005056749999999999,
    0.00015806499999998502
  ],
  "construction_scale": 102.6961740571164,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
