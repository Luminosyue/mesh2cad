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
    1.2765075786681135,
    -0.23690146365686476
  ],
  "profile": [
    [
      1.1970221812734292,
      16.1490563799424
    ],
    [
      3.5033271499537584,
      16.226332557576793
    ],
    [
      5.50901146520766,
      17.32647383918905
    ],
    [
      7.152112828235126,
      19.360148949153178
    ],
    [
      8.127404755096018,
      21.74365477925816
    ],
    [
      9.449436650843534,
      24.00066823728542
    ],
    [
      11.540146615673944,
      25.492781431878967
    ],
    [
      13.851444381273915,
      25.723500448836194
    ],
    [
      16.394197706522238,
      25.673258229915085
    ],
    [
      18.88310109534777,
      25.57065130352064
    ],
    [
      21.395674728090324,
      25.621312770556464
    ],
    [
      23.922222481039878,
      25.7011597357911
    ],
    [
      26.45047747083594,
      25.703006859913394
    ],
    [
      28.955906234306624,
      25.700536447992846
    ],
    [
      31.404152714583823,
      25.708133264158768
    ],
    [
      33.94729407579869,
      25.6546725608273
    ],
    [
      36.40435857654403,
      25.265621535100102
    ],
    [
      38.44367786365319,
      24.164124305557927
    ],
    [
      39.867928769911515,
      22.21073298168667
    ],
    [
      40.57190592867239,
      19.80503794063975
    ],
    [
      40.80340584658232,
      17.299585175059313
    ],
    [
      40.8477632751442,
      14.777221053033706
    ],
    [
      40.81137732813602,
      12.257974247559057
    ],
    [
      40.757617622226405,
      9.773260801185033
    ],
    [
      40.73118994409738,
      7.302479941614596
    ],
    [
      40.65924433234167,
      4.831363040757827
    ],
    [
      40.61142626246395,
      2.3599923546763626
    ],
    [
      40.612864053874,
      -0.11874072141945716
    ],
    [
      40.65533765718081,
      -2.6403911997646983
    ],
    [
      40.71895071679894,
      -5.174794382395936
    ],
    [
      40.72506409111983,
      -7.707189956689502
    ],
    [
      40.692454480375304,
      -10.240894509517055
    ],
    [
      40.669268647208966,
      -12.774679581227772
    ],
    [
      40.64392105121708,
      -15.314183706496856
    ],
    [
      40.62535950424031,
      -17.866578424125095
    ],
    [
      40.618663576176594,
      -20.42375120004401
    ],
    [
      40.62903246747911,
      -22.983570206761527
    ],
    [
      41.081358548112775,
      -25.461251521213622
    ],
    [
      42.29036901277706,
      -27.324580174071308
    ],
    [
      43.81209722326764,
      -27.29629111866808
    ],
    [
      44.24824603504692,
      -25.170110017668172
    ],
    [
      44.31576016474243,
      -22.656617152582086
    ],
    [
      44.35294997044801,
      -20.128684706301414
    ],
    [
      44.39439554607315,
      -17.591010365857855
    ],
    [
      44.40442263231957,
      -15.036766740639807
    ],
    [
      44.414519645063734,
      -12.48010783112434
    ],
    [
      44.431665099336406,
      -9.926107395610035
    ],
    [
      44.45893268511874,
      -7.372804182966913
    ],
    [
      44.44613911046966,
      -4.820001144947366
    ],
    [
      44.38081715424721,
      -2.265048493935022
    ],
    [
      44.35205618705152,
      0.23527056567349974
    ],
    [
      44.34926434456111,
      2.6648063291822552
    ],
    [
      44.4029405602393,
      5.20712664199109
    ],
    [
      44.47098915941628,
      7.76743861783477
    ],
    [
      44.50666814587278,
      10.319621057285852
    ],
    [
      44.494045547884355,
      12.838256204876881
    ],
    [
      44.31229632178298,
      15.338684368971577
    ],
    [
      44.10082410182822,
      17.76536140446139
    ],
    [
      43.96337826366146,
      20.149733501250928
    ],
    [
      43.62101116108219,
      22.55842011016803
    ],
    [
      42.77102602778992,
      24.87733529418887
    ],
    [
      41.325357004791755,
      26.91243137364092
    ],
    [
      39.433789284325336,
      28.29827471677097
    ],
    [
      37.14755826453778,
      29.112257180182652
    ],
    [
      34.641307761628916,
      29.442875458797808
    ],
    [
      32.127363726748655,
      29.540621773313894
    ],
    [
      29.593673351187284,
      29.517614226339937
    ],
    [
      27.03749041680539,
      29.45054042095932
    ],
    [
      24.51861673350391,
      29.420432644488923
    ],
    [
      22.007650805554285,
      29.439215691900134
    ],
    [
      19.47623688528558,
      29.48442448476531
    ],
    [
      16.944155117271613,
      29.494441157457583
    ],
    [
      14.412814710059203,
      29.51792249751496
    ],
    [
      11.884259379273544,
      29.525544333344985
    ],
    [
      9.379720504464718,
      29.20230355363269
    ],
    [
      7.060139503424507,
      28.17191070124615
    ],
    [
      5.040784815755705,
      26.50009373875911
    ],
    [
      3.7669135139972814,
      24.139940999318803
    ],
    [
      2.698994389044107,
      22.15609925644697
    ],
    [
      0.921931962311179,
      21.6286261527159
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      -0.4099601553350316,
      0.8935345710157869,
      -0.18310827790493658
    ],
    [
      -0.052831149939343784,
      0.17715438541666656,
      0.9827640578102814
    ],
    [
      0.9105720952421964,
      0.4125679266827198,
      -0.025419780466376427
    ]
  ],
  "axis_candidate": 5,
  "center": [
    0.56246191,
    0.01361288,
    -0.063472265
  ],
  "construction_scale": 376.8113036759224,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
