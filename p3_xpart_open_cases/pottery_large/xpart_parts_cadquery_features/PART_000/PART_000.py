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
    -0.136589265705923,
    0.11331554587303298
  ],
  "profile": [
    [
      1.7169834496267804,
      -48.759437702925936
    ],
    [
      5.031551108710742,
      -48.776019448218655
    ],
    [
      8.355688114171423,
      -48.8712853891988
    ],
    [
      11.694229650725184,
      -49.027186500229234
    ],
    [
      15.037912683713271,
      -49.30003220864597
    ],
    [
      18.38324618425161,
      -49.49186267853304
    ],
    [
      21.728498432489324,
      -49.54872705781224
    ],
    [
      25.07713451696489,
      -49.581408751606595
    ],
    [
      28.425214013987816,
      -49.59868989513006
    ],
    [
      31.733384029588994,
      -49.398581512600614
    ],
    [
      34.75590030143428,
      -48.2676741332826
    ],
    [
      37.31067782572468,
      -46.095463505954015
    ],
    [
      39.39863130685323,
      -43.4601315800528
    ],
    [
      40.979466201316214,
      -40.60056299456441
    ],
    [
      42.14383293498471,
      -37.55260530000879
    ],
    [
      43.057833979594676,
      -34.29992007391096
    ],
    [
      43.83645391514972,
      -31.064579246289647
    ],
    [
      44.49687566871418,
      -27.79244639772117
    ],
    [
      45.00067379901333,
      -24.47339256871475
    ],
    [
      45.48343411628933,
      -21.154795862923837
    ],
    [
      46.01836462992058,
      -17.842074239138974
    ],
    [
      46.56082613069552,
      -14.52524223729008
    ],
    [
      47.05122439045504,
      -11.212393475675825
    ],
    [
      47.565316383869146,
      -7.90645743451482
    ],
    [
      48.03213508095385,
      -4.581705041479347
    ],
    [
      48.39390950491298,
      -1.2473156170348423
    ],
    [
      48.62937352424812,
      2.085788318884789
    ],
    [
      48.76529953579504,
      5.4261825535974015
    ],
    [
      48.88457410291855,
      8.77352519748256
    ],
    [
      49.05980725711035,
      12.120202034537876
    ],
    [
      49.263204083978835,
      15.465804629656805
    ],
    [
      49.45434247247647,
      18.811242160573137
    ],
    [
      49.615259050749756,
      22.158264087327655
    ],
    [
      49.7331440405608,
      25.506334689262154
    ],
    [
      49.80489849337228,
      28.85473807440531
    ],
    [
      49.8410226719307,
      32.203719333326646
    ],
    [
      49.88497381384193,
      35.55330754027526
    ],
    [
      49.972069020657585,
      38.903324369785814
    ],
    [
      50.07056073564581,
      42.25246053036373
    ],
    [
      50.15417386422874,
      45.597386786167675
    ],
    [
      49.54686643418549,
      48.55548905908955
    ],
    [
      47.13339667250656,
      48.76002099265369
    ],
    [
      45.94524268335917,
      46.11252351020034
    ],
    [
      45.68968552971305,
      42.7898732575688
    ],
    [
      45.51757684682249,
      39.445754776850805
    ],
    [
      45.395861359776426,
      36.098185964575805
    ],
    [
      45.27789859389793,
      32.750500891184615
    ],
    [
      45.141866983135415,
      29.403220229365367
    ],
    [
      45.00064580613045,
      26.055837014457236
    ],
    [
      44.8224176785255,
      22.708831125698698
    ],
    [
      44.61535854353237,
      19.36218364828808
    ],
    [
      44.45846609254183,
      16.016005671764738
    ],
    [
      44.3266589427907,
      12.669709649162023
    ],
    [
      44.19374678600742,
      9.324995455356298
    ],
    [
      44.05777409526884,
      5.983136595331683
    ],
    [
      43.87398839730568,
      2.64300207803894
    ],
    [
      43.655443719556644,
      -0.697388583957707
    ],
    [
      43.43887291703925,
      -4.034406396839028
    ],
    [
      43.15621016187728,
      -7.354611535634913
    ],
    [
      42.855520283791975,
      -10.671356769309906
    ],
    [
      42.51124008014289,
      -13.98656080299457
    ],
    [
      42.07590440010827,
      -17.300714856994613
    ],
    [
      41.60657547669261,
      -20.621250849340214
    ],
    [
      41.146119558123175,
      -23.969113027495794
    ],
    [
      40.612884074295906,
      -27.339471788808545
    ],
    [
      39.938856116419146,
      -30.662411369295683
    ],
    [
      39.10702277410627,
      -33.903581068156015
    ],
    [
      37.87967391188522,
      -36.948506633097516
    ],
    [
      35.673936341462436,
      -38.91639822755083
    ],
    [
      32.44099140234396,
      -39.160908049391566
    ],
    [
      29.103812225099936,
      -38.97269519865511
    ],
    [
      25.76182603982985,
      -38.744754836771136
    ],
    [
      22.412567396272227,
      -38.552147915156866
    ],
    [
      19.06308104205099,
      -38.381076437004126
    ],
    [
      15.721474012457026,
      -38.24625735013341
    ],
    [
      12.383002400087532,
      -38.10684409823178
    ],
    [
      9.07370279857,
      -38.08260158501365
    ],
    [
      6.039914939338575,
      -38.10657079963026
    ],
    [
      3.6293217579254664,
      -39.74578100551702
    ],
    [
      1.3418763556965279,
      -41.5362848489989
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
    -0.003993734999999998,
    0.001400929999999967,
    -0.0002717999999999887
  ],
  "construction_scale": 50.57663995083789,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
