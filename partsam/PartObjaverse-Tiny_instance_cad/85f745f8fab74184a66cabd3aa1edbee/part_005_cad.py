"""Standalone mesh-derived CAD code, with embedded vertex and triangle data.

This reconstructs a faceted BREP, not an inferred sketch/extrusion feature tree.
Original numeric coordinates are retained; physical STL units are unknown.
Open meshes remain CAD surfaces. No guessed closures or thickness are added.
Run: python part_XXX_cad.py [--output-directory PATH] [--no-validate]
"""
from pathlib import Path
import argparse,base64,io,json,time,zlib
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/85f745f8fab74184a66cabd3aa1edbee/part_005.stl', 'relative_path': '85f745f8fab74184a66cabd3aa1edbee/part_005.stl', 'source_sha256': '1070dfb0a39940ffd55ee353a7d4c72779aff05825232203619e58cf5b845fcb', 'input_faces': 144, 'input_vertices': 105, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18066713213920593, -0.27496081590652466, -0.15936875343322754], [0.2338356077671051, 0.14615660905838013, 0.20234781503677368]]}
GEOMETRY_BASE85 = 'c$}qJX-rgC6uzJ+ZYU}$BJfaT0FgyTHpO`^D2l?U6>({O2!ohbMNk`Ct1q?IEp^|QI<~QH6<n}dH=c@uC|I@D8oNvz;}4TcTWhRq`tG^k*qIlaH0>lO-*>-r-#Pc(d)|_<W;ANto{3)w%iefH&S}mVx0b9un`0}UH8syx5<R_Wt_N#FI{!IwZRVH})^Q$e4tv*>Z!5_wHl;|Wz6D99D9KbXqj*+v?(|7Bit}w;ADsJEiA~o_3UiBW`Zzo;ws({i9}y+JC;i7CUxnr`RaNk{6y4d(QR|npw!&4PE_B7a=#WK6$GJ5Z_*nY+$`y|GPWkIO%B>$%()`P1)im}Ox+A*k9O+fVYf0bn%K=wiyC`(2jn8TxU;T5Mn4g(<jr<)E-=N!}tH;AhS5GZ<%PTuNk}lQ9UZU~Lk)^J><AKnnBR46p7I)w*#h*LBj_P&RW!@w7i?hUff|NxxHtH*U><#G(<~wTdX*92JC&iZ}p=$=6trT&Lx)v<v%k#FA&Ym9KNc#M5Y3z7=C83(w<RHagY(CEGQU)#;^E>t@U5(qhg09=TkaYR!4ca&Ltp8`OI)l!VY}q^xTi0C7f3!*Lzq4M0E~8#$!kRO*u7dk+bs2R#>T<MuewyaZ+FVZOvFe^i{bsEuT^(@r9O-*CLUzTEbfwlR_NmJxIxp>d6VmP3t*+8~aE{W2;uAEUT}bDypkAlWptBTFul$`X=C{tObM0HF&Y&ykTl=&C($(j+bpC2q(%uReU4hOvUz$(n(&YMa8sCbqaqUm1u6-kPXMZ}DhaV&T@L|!n=yRoJ=~0TaE&UYjOYQCRwEptF<&^(nU7g!L910^{8(&TLtBiFzbrm|>D%R;J3_U{QXXUgWhP+xvpF@=YkKex}3?47^QBkC8OVchA2H;#q*OpP9kh)VeUa)?btInV^`CuyLJ(fWG!PfZiqq@qUQ(Y{6(>~Hm79625dr1A@xcm<3_U-+}{v*CqSD`aS#Fr1miZ}zpML+r1R#Ja`WTO3GXLeCu?M2yHI<FV@J)~!=8~9jFcv0!5ckZ=~;w}ym@tR%TP5Zm9R6L)8#Qw<rCX&uJ-lcja?3<&5r_g^INB1p@c|>vSk=v<H*$-X!Qr@(w)l_d@3!!hhL-&guJBZdJ*Qb9<dQH$yv2Tf0REJOAC!}|(r{_33^_X-i+_a3=H`yxsuJY>Y3Riu@Z0ZYXXmo|^eD;2h$kVH!(se$|5B`Aiom4Kk&6oBpC%tXI^KN=k{${Exb5XUMzTw9`q%XO5$xSbfrgN8DK69V{BJc~+eIwoTu3C12@?P^KUA>>W$kM<*$Q~6-EDh|NeMddrf5v@QA2(fVY2aK`ukVF!I7e+;>y4HM`sbBy=pXGv-%XYV`cSP**kWm@Z@==|N@K%)p)3g$^%(9WZRpDbG&Vdp?E6!XQ69tdR+&DNbmQ|`u3t*~Yka>*IcrEazK>XLshDqge`)4B;{G;%hd6b^cZmH)0-Yy2@?<yN4*_O+PRV{Yp%+Ewi9UFfo=5iVwL%XYLUkxle-qEskob$FuL_<@^_1PD`7AU==rd=CKCH~6`0CdY)EBJP#}r2^UQBW9HBadLSwI2R=kRGHzCUhNQU5aSObNvw{VUZgB~Pj${chZT!V^*AK9XKurtxrglJIt!c)u@LafQa|rSmAx@Zt)pcl3i=as8&xsos>8=PImjU!~y-N1T?M>Qi-Vrhk<d<hp#4a*_X>*zhOmRP(?4BsH7=?<eUneGP+k8v)}y1IBq8jPrgl&ileRw*ZHLb4&;4m<rA@4%`CX7ntZ0GZA^xfCGVv-~+)2!8lI>#(^h+Cje8y6Ttfb)4}_I4~21_2^<cd2|g0|8u&<XD=-V(3hrEI7S^5y%m8M&?0FW>Aq%la0EdC+>1NYy5{&cLf%)JZ-vFPYn*vRNo{u;MxQ=5XxD7lXI0c-~nGB6%E_fmM6rchw>z1S2I2h*>VVqBZaXua>gO3Lv0OPzZuswKNaOaP64;bg|fHHVH@czJY;A3?gquXd0=c8bpX9LHA2j~{ATNfDTy<wd90tSHl>efOxe!F+Z*hjY@j63PpMmK-mI$|y#x58X6XdFGk`E_04?+TwUVn)Cp0bggt4uL-ez98gj41Z(z{E@>Geoy$?AWw5>92<f2JYn#M!RLiMQSe8>*A;oX!`~gg2<SXlGgx<Mp2*c0*bJQK=>UzRH#pBD!7str9C=Leo8SvWo?!Tc;fq2ZKluIN>y8}W@O#6@d9rTtx}^YPz>|Sy80WDt&U*r5z+-`-SbHe)c!LK5dx9q;ZZxn5xCtl$dw@&e9bi2WFBCi$Xa<i#J>7tj;C{ehU?g}jxCs`C{L$daz<BVU$PtJd0}<N~yc;kEyrpifb!(!VHN(TReWQQ+OX%;P${!4Fe-Ih3bboETUb#V!_39;V&G6!R^``V>Gj;UkPa^gg=(E8B'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

def build():
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing=BRepBuilderAPI_Sewing(1e-7,True,True,True,False)
    planar_faces=[]
    skipped=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        if np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))<=1e-12:
            skipped.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    sewing.Perform()
    shape=cq.Shape.cast(sewing.SewedShape())
    representation='faceted_surface'
    if SOURCE_INFO['input_watertight']:
        solids=[]
        for shell in shape.Shells():
            solid=cq.Solid.makeSolid(shell)
            if solid.Volume()<0: solid=cq.Shape.cast(solid.wrapped.Reversed())
            solids.append(solid)
        if solids:
            candidate=solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)
            if candidate.isValid() and len(candidate.Faces())==len(planar_faces):
                shape=candidate
                representation='faceted_solid'
    if not shape.isValid():
        # Explicitly represent troublesome nonmanifold edges as separate faces.
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    shape=shape.scale(1/construction_scale).translate(tuple(center))
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':1e-7/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid')
        if report['step_reimport']['faces']!=state['faces']:
            raise RuntimeError('STEP transfer changed the face count')
        error=float(np.max(np.abs(np.asarray(report['step_reimport']['bounds'])-np.asarray(state['bounds']))))
        report['roundtrip_bounds_max_error']=error
        if error>max(float(np.ptp(decode_geometry()[0],axis=0).max())*1e-5,1e-6):
            raise RuntimeError('STEP transfer changed bounding dimensions')
    report['seconds']=time.time()-start
    report['status']='SUCCESS'
    (out/(PART_NAME+'_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--no-validate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(export(args.output_directory,not args.no_validate)),flush=True)
