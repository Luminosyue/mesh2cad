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
    -0.3382911750861179,
    -0.15259157267661347
  ],
  "profile": [
    [
      1.1971880077839483,
      -9.760156583731524
    ],
    [
      3.5553052129290608,
      -9.314774756562226
    ],
    [
      6.019349369149397,
      -8.725439256979616
    ],
    [
      8.547722482152182,
      -8.2712077557765
    ],
    [
      11.037857844463929,
      -8.047834242931739
    ],
    [
      13.437325875032743,
      -8.573864437556242
    ],
    [
      14.833859974173542,
      -10.35245737684593
    ],
    [
      15.583169145380694,
      -12.82630245161682
    ],
    [
      16.037442172515995,
      -15.330215109589059
    ],
    [
      16.19178660102509,
      -17.820722496625333
    ],
    [
      16.565603298847883,
      -20.265939539504046
    ],
    [
      17.55505810753003,
      -22.528216934706897
    ],
    [
      19.009217708457946,
      -24.396438497181336
    ],
    [
      21.003167046035337,
      -25.767607062582513
    ],
    [
      23.38251898498163,
      -26.40266682864606
    ],
    [
      25.94375614544964,
      -26.52234803355713
    ],
    [
      28.53624913113827,
      -26.534363884035095
    ],
    [
      31.14007624819707,
      -26.510964517321803
    ],
    [
      33.76429588677633,
      -26.346893230179624
    ],
    [
      36.388417931580435,
      -26.185806883677223
    ],
    [
      38.94629116404852,
      -25.59765385955762
    ],
    [
      40.68917365877614,
      -24.08154483388854
    ],
    [
      41.54201926527422,
      -21.845318650940442
    ],
    [
      41.919115081583485,
      -19.30999695335384
    ],
    [
      41.98916072738884,
      -16.734924332625752
    ],
    [
      42.01096275288227,
      -14.15782222923216
    ],
    [
      41.98759084904154,
      -11.591821687711874
    ],
    [
      41.955118999947395,
      -9.045988792992384
    ],
    [
      41.928937942856116,
      -6.503641234132239
    ],
    [
      41.90489726914315,
      -3.9619638650332143
    ],
    [
      41.88363030919778,
      -1.4189582317781362
    ],
    [
      41.842174561611586,
      1.1216485507317984
    ],
    [
      41.807998004423055,
      3.659092715554177
    ],
    [
      41.81911345225654,
      6.223319006917226
    ],
    [
      41.81156620810008,
      8.791976601845395
    ],
    [
      41.77832922953617,
      11.360587569942421
    ],
    [
      41.77349826034184,
      13.918805016436988
    ],
    [
      41.79012406947497,
      16.43482279918205
    ],
    [
      41.752813157865646,
      18.89796758754685
    ],
    [
      41.67927962281018,
      21.34868951797808
    ],
    [
      40.86019683621323,
      23.55840183813968
    ],
    [
      39.018423034751834,
      23.74303782922966
    ],
    [
      38.227464985727906,
      21.66753983384145
    ],
    [
      38.19780539453446,
      19.15434399412626
    ],
    [
      38.279573468878695,
      16.581371432838772
    ],
    [
      38.31902605068771,
      13.99377792221999
    ],
    [
      38.360571175278075,
      11.411441139408204
    ],
    [
      38.39551448906633,
      8.87062497566943
    ],
    [
      38.390904072418664,
      6.338391710713397
    ],
    [
      38.384739037297216,
      3.803948380429298
    ],
    [
      38.35603674068011,
      1.2376437039153
    ],
    [
      38.35661455355581,
      -1.3513833481583668
    ],
    [
      38.395644167192714,
      -3.941424587923268
    ],
    [
      38.416829284034435,
      -6.531382999170685
    ],
    [
      38.448403153432416,
      -9.103607882527092
    ],
    [
      38.474711477056395,
      -11.655225383679191
    ],
    [
      38.508819674687714,
      -14.206160202312798
    ],
    [
      38.48204381902285,
      -16.75705711918718
    ],
    [
      38.28720966518206,
      -19.301007568398152
    ],
    [
      37.59132033430298,
      -21.58364331191209
    ],
    [
      36.101754884735556,
      -22.71089790362893
    ],
    [
      33.57237983685977,
      -22.950049236873852
    ],
    [
      30.980856893005182,
      -23.142161285208406
    ],
    [
      28.38822904838699,
      -23.202267488966307
    ],
    [
      25.80215232854372,
      -23.16678854725906
    ],
    [
      23.322691057098023,
      -22.794791611787666
    ],
    [
      21.282574345761233,
      -21.560871354436948
    ],
    [
      20.008175470483422,
      -19.556978763762437
    ],
    [
      19.621254054047263,
      -17.14463168576874
    ],
    [
      19.45363013840245,
      -14.64454602028178
    ],
    [
      18.9462681101388,
      -12.138020919874105
    ],
    [
      18.2875010097128,
      -9.640000289636507
    ],
    [
      17.646104593169845,
      -7.219099469101636
    ],
    [
      15.987177903509217,
      -5.30622906370542
    ],
    [
      13.635952861493937,
      -4.688970125573744
    ],
    [
      11.151864533993932,
      -4.531193430725526
    ],
    [
      8.64972250296059,
      -4.665464341259508
    ],
    [
      6.152169258558313,
      -4.9580112734109605
    ],
    [
      3.6342001427241537,
      -5.378112031411959
    ],
    [
      1.211812934594089,
      -5.679763810904763
    ]
  ],
  "method": "axisymmetric_spline_revolve",
  "segments": 12,
  "fitting": "median of 16 meridian cross-sections; spline profile with shared endpoint tangents",
  "operation": "revolve",
  "basis": [
    [
      -0.4386793474230642,
      0.8902323361974633,
      -0.12266547082566105
    ],
    [
      0.026301103419881757,
      0.14916110312322148,
      0.9884630581230441
    ],
    [
      0.8982586944212514,
      0.43039209205498913,
      -0.08884798812105162
    ]
  ],
  "axis_candidate": 5,
  "center": [
    -0.30403057,
    0.38624657,
    -0.55420477
  ],
  "construction_scale": 344.4700975153509,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
