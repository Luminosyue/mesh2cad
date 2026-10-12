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
    -0.06596280016600031,
    0.04254444496346381
  ],
  "profile": [
    [
      1.0173539963107783,
      -49.90445176645771
    ],
    [
      2.9840024019511393,
      -49.905663262337946
    ],
    [
      4.973264304961364,
      -49.90636650512842
    ],
    [
      6.9624510623266875,
      -49.90809272486922
    ],
    [
      8.951581923906446,
      -49.90993277397017
    ],
    [
      10.940854505914032,
      -49.91468695805978
    ],
    [
      12.93006192698115,
      -49.92438529723624
    ],
    [
      14.899952465450497,
      -49.90834283204835
    ],
    [
      16.308112438210845,
      -49.057933729345905
    ],
    [
      16.56513606142388,
      -47.16410243588468
    ],
    [
      16.574508785586495,
      -45.182566832674915
    ],
    [
      16.567293670469624,
      -43.19020405407195
    ],
    [
      16.564125530099172,
      -41.1978071834904
    ],
    [
      16.56808807079607,
      -39.20623824423675
    ],
    [
      16.557920047890136,
      -37.21466808518157
    ],
    [
      16.555226788245836,
      -35.22306674807909
    ],
    [
      16.550642002487965,
      -33.23143867512056
    ],
    [
      16.549254089838378,
      -31.23975058517362
    ],
    [
      16.5557811030836,
      -29.248054926929377
    ],
    [
      16.56929349926508,
      -27.256566076151906
    ],
    [
      16.589325105705697,
      -25.265004793765893
    ],
    [
      16.59876044942165,
      -23.273446322811353
    ],
    [
      16.605340355564262,
      -21.281933886045977
    ],
    [
      16.60378993080323,
      -19.290561808063877
    ],
    [
      16.608854484972106,
      -17.29909762537028
    ],
    [
      16.62172793878226,
      -15.307617830634499
    ],
    [
      16.628838053597608,
      -13.316193888856764
    ],
    [
      16.636793410782005,
      -11.324699171988257
    ],
    [
      16.635010998431987,
      -9.333356164209832
    ],
    [
      16.630715038749535,
      -7.341886888189728
    ],
    [
      16.627666817464146,
      -5.350302438708658
    ],
    [
      16.63122902161038,
      -3.3587734079971567
    ],
    [
      16.63601492798536,
      -1.3672157115026535
    ],
    [
      16.635104694401484,
      0.6242835026041959
    ],
    [
      16.632824517080245,
      2.615828409322084
    ],
    [
      16.631891494021794,
      4.607291264689868
    ],
    [
      16.627503914626352,
      6.598855023108774
    ],
    [
      16.620374037642016,
      8.590460077644954
    ],
    [
      16.623026913158654,
      10.582137377059759
    ],
    [
      16.62455043994106,
      12.573529947355999
    ],
    [
      16.693888608324436,
      14.56299810333061
    ],
    [
      16.881484761006448,
      16.436011238348918
    ],
    [
      17.609963187067088,
      17.2895046428304
    ],
    [
      19.40541208042309,
      17.525604464927586
    ],
    [
      21.264610690048876,
      18.266861629041205
    ],
    [
      22.418508715875497,
      19.505245334543744
    ],
    [
      22.960244542888606,
      21.36253441644525
    ],
    [
      23.365866957867674,
      23.319458200682146
    ],
    [
      23.748082993789154,
      25.281296699342235
    ],
    [
      24.12444845891251,
      27.244675860082168
    ],
    [
      24.46452407268241,
      29.20944599033092
    ],
    [
      24.816748341367518,
      31.173464968349695
    ],
    [
      25.205006792435285,
      33.13716382456393
    ],
    [
      25.572197178681805,
      35.10517991185296
    ],
    [
      25.929908271882162,
      37.074242035883344
    ],
    [
      26.27105913936166,
      39.042648444139246
    ],
    [
      26.52416529897664,
      41.01578527034356
    ],
    [
      26.661270435484084,
      43.0006944394394
    ],
    [
      26.77695009303147,
      44.99051457277577
    ],
    [
      26.841813134754858,
      46.97162997382368
    ],
    [
      26.12119873653966,
      48.466271202962574
    ],
    [
      24.268384365473292,
      48.67352209096862
    ],
    [
      22.47765930213559,
      48.08279832056992
    ],
    [
      21.582392235714487,
      46.4950397728361
    ],
    [
      21.236019671033823,
      44.5559579909256
    ],
    [
      20.95115201844734,
      42.591341645294875
    ],
    [
      20.680691272314874,
      40.618033100277074
    ],
    [
      20.41305936419858,
      38.64343808331427
    ],
    [
      20.10891208491312,
      36.6671632521615
    ],
    [
      19.6830933233625,
      34.71891433877131
    ],
    [
      18.677540045341054,
      33.132618069025106
    ],
    [
      16.902647927849735,
      32.44997994156684
    ],
    [
      14.91939257831362,
      32.361424509436446
    ],
    [
      12.930181865760613,
      32.3673472659084
    ],
    [
      10.940916217688466,
      32.37361356443063
    ],
    [
      8.951634136387668,
      32.38279286801619
    ],
    [
      6.962361308603327,
      32.39745532094341
    ],
    [
      4.973063838275788,
      32.40228382074022
    ],
    [
      2.983848381439926,
      32.40100176993864
    ],
    [
      1.0173332010790426,
      32.40145913037442
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
    -0.7124998,
    0.782093425,
    -0.45213101
  ],
  "construction_scale": 134.35653538134255,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
