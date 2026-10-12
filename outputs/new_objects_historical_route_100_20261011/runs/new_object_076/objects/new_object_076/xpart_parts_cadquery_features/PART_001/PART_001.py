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
    -0.0953061628513973,
    0.004584333750217881
  ],
  "profile": [
    [
      1.0868789032201094,
      -23.114759788339775
    ],
    [
      3.187938232577933,
      -23.109104773041516
    ],
    [
      5.313131079973352,
      -23.099493695255358
    ],
    [
      7.438215771879406,
      -23.081224081862246
    ],
    [
      9.563158357841115,
      -23.05584442770764
    ],
    [
      11.687983105971718,
      -23.02906086279608
    ],
    [
      13.812813797904731,
      -22.995901585183226
    ],
    [
      15.937587587941186,
      -22.954587170590813
    ],
    [
      18.0623747644477,
      -22.905070554615197
    ],
    [
      20.187142417060024,
      -22.84932529710737
    ],
    [
      22.311797988954226,
      -22.79609299288813
    ],
    [
      24.436188945299307,
      -22.74016574040077
    ],
    [
      26.56083831735085,
      -22.688114572604693
    ],
    [
      28.685507528968362,
      -22.67497323263772
    ],
    [
      30.780508856317827,
      -22.927710522358737
    ],
    [
      32.785903464170936,
      -23.45380011969515
    ],
    [
      34.65859782382546,
      -22.84841798863352
    ],
    [
      36.07474121098943,
      -21.30048055077345
    ],
    [
      37.27979260695043,
      -19.557948902835072
    ],
    [
      38.438446795343864,
      -17.775943460420432
    ],
    [
      39.54141894120005,
      -15.957891527264175
    ],
    [
      40.600496704822255,
      -14.111858642707212
    ],
    [
      41.58629322512175,
      -12.23016851606713
    ],
    [
      42.503003109007196,
      -10.32866060596836
    ],
    [
      43.389042094946845,
      -8.403272686501056
    ],
    [
      44.216987927988086,
      -6.435919518539638
    ],
    [
      44.97978376644522,
      -4.452308442614331
    ],
    [
      45.696443830181956,
      -2.4631586208528597
    ],
    [
      46.370715180075344,
      -0.45961385541344313
    ],
    [
      47.00074648625107,
      1.5698466495098402
    ],
    [
      47.58766070393578,
      3.6154061678183886
    ],
    [
      48.11157573567521,
      5.673212606837444
    ],
    [
      48.53543862811327,
      7.746471316115953
    ],
    [
      48.89534415923102,
      9.833010806894325
    ],
    [
      49.18037240193139,
      11.932450015344664
    ],
    [
      49.4107164341619,
      14.042255771535181
    ],
    [
      49.603058227835604,
      16.158935588758332
    ],
    [
      49.74596092918054,
      18.281190873834305
    ],
    [
      49.86282817611739,
      20.405760296787733
    ],
    [
      49.835589514556546,
      22.482668137383527
    ],
    [
      48.939118641858286,
      23.27338501784719
    ],
    [
      49.002175513001596,
      21.777181008783103
    ],
    [
      49.00905164164868,
      19.70597122818046
    ],
    [
      48.89382528740127,
      17.584654093309638
    ],
    [
      48.7372237113807,
      15.46559681069155
    ],
    [
      48.52599450378284,
      13.351251565091518
    ],
    [
      48.26762987821315,
      11.244821993333195
    ],
    [
      47.952552658646226,
      9.145186288729949
    ],
    [
      47.54366761522079,
      7.057105875362096
    ],
    [
      47.05774807223516,
      4.986371709251888
    ],
    [
      46.51023281148788,
      2.936821780561636
    ],
    [
      45.90425329320986,
      0.9025096421668979
    ],
    [
      45.2350602548023,
      -1.1104806640684812
    ],
    [
      44.52607101795005,
      -3.1006005439088753
    ],
    [
      43.780953942849465,
      -5.085456072054761
    ],
    [
      42.98047499283751,
      -7.056127853441233
    ],
    [
      42.122898874110405,
      -9.00055673850053
    ],
    [
      41.222658435908016,
      -10.922269776809516
    ],
    [
      40.24642571495192,
      -12.808009213490337
    ],
    [
      39.212528396131646,
      -14.655111423678395
    ],
    [
      38.114292793048776,
      -16.478599610433815
    ],
    [
      36.98883068626375,
      -18.283615568191948
    ],
    [
      35.832589273602984,
      -20.05935527628154
    ],
    [
      34.567837265701954,
      -21.740746053021404
    ],
    [
      32.83755906513969,
      -22.518269865502482
    ],
    [
      30.799986810656158,
      -22.085846631904168
    ],
    [
      28.689425488549126,
      -21.902467448179756
    ],
    [
      26.564428784012556,
      -21.913041437570094
    ],
    [
      24.439355016156764,
      -21.942309951583393
    ],
    [
      22.314582510757294,
      -21.980089642372242
    ],
    [
      20.18977662025086,
      -22.02419631532221
    ],
    [
      18.064743898212217,
      -22.06095975629193
    ],
    [
      15.93958175655368,
      -22.07893206571096
    ],
    [
      13.814321303263236,
      -22.085543866729545
    ],
    [
      11.68904962416687,
      -22.09510960771435
    ],
    [
      9.563783043403085,
      -22.10701579285918
    ],
    [
      7.4385097114243335,
      -22.121261481566407
    ],
    [
      5.313228049428878,
      -22.136658689582596
    ],
    [
      3.187945298367972,
      -22.14236518811918
    ],
    [
      1.0868652092862416,
      -22.14198982290896
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
    0.00024219999999999797,
    -0.0007111949999999978,
    0.0005427349999999886
  ],
  "construction_scale": 100.38786961571293,
  "expected_solid_count": 1
}''')
def build():
    return build_model(PARAMETERS)
if __name__=="__main__":
    result=build()
    assert result.isValid() and len(result.Solids())==PARAMETERS["expected_solid_count"]
    result.exportStep(str(Path(__file__).with_suffix(".step")))
