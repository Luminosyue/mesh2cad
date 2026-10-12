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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/358eb80d4d074dee8cd65b4b0fa187f7/part_006.stl', 'relative_path': '358eb80d4d074dee8cd65b4b0fa187f7/part_006.stl', 'source_sha256': 'a280e7f308251bac0ffadba5df4ee25edae61660c433bf503edcab9a42bae8d8', 'input_faces': 206, 'input_vertices': 146, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2063674032688141, -0.07737177610397339, -0.24799123406410217], [0.20424163341522217, 0.13366436958312988, 0.16089972853660583]]}
GEOMETRY_BASE85 = 'c$}qKYfx2H7(F238_`e<M6WL{Dk>rhzPgAnh!ju(<stV9mk<n<myxMgP~`1%5~^uvnrX6pG&c3aQMpb`fa7EQm47mSG-b_LQ%y}-W9_}q+MBaKZZl2YnQzwGYklWC=X`gcefFK3o;oBT#4tb8jF|AScVmJKgU4ti#HevsRP8KuSI#frQ|o603!Q%?p5B<bA$^;lQDf}47r847E9}c`_7%km_Gp{Ecy~org{!<^cSVt#>+4**D&0)4EOG5|vvJhIxFylHMYE%A2W<cGGm>3GqNDU?H^;emKH_Nn{Qa$Ni|%>Uan-@FE584R!=f8sy)N{`)F1Tx_rgTp!|FaQ-<uIG#@_RfMZOWc#jNvL{RM%CpSC-!dZDR%E?<0G)9?Lxo?}<t>Ta!0)^9>jT$^&ms(YUFi0kx3>iM38Uh}>lCF}XKg06|{ym(1J@3~;1dqRH_*J=CQVd@j^d?@bkK|_~S_sqB@bX(S?>)qD;j&DB@_~u(zG`;g{p?mDTC$u{Lb>{VtUwqe^?>Sn3)$H@rPqpjm$n6%_eeTyAnjW^@)LqfHMV+9frf!sni~1#hnRS$YKSJd1KYUlupJEezJNNNrJ^%4EK6XC-qDRX=_4{d|r;+;3r$T?YkJj-&BhDN6K(BKrQ0U&yI&nST^FQ|anm<Y>^GE4q{wSTyAF0#%qjWNVluqW4s!!&R5%6W7ulXZ&I)79?nLkP=^GDSo^GE4q{tVRD=a16K{4ti_@AEZ(26TP?4Cwm&8PN6lqjWNVluqW)KplPlD4on7+psr!h5nAY?%8_I_Bbp$T@R)1*?Zg6o6Yr2)p>GD=!x^L>-DR4nDedus;=idh3?Jk(9UbTR3LOuj(%R_k9<>~-mjgPuFopp*=c_7hpuVo^^}?Gwzo{bU%H;Fe6pTPov!DqZ>6Sgy#JbB|2yd4n0@F9D9!NIf2q^{OP%&#)gk>?I_baCN&l5j`mc1-e|0^i|0<vKU*(hjt9;Ubl~4LFb=rT`H`0GqpY-1tm)+~|(SNDa{!5+qU)3S~S32px(n<f7PWrEO(tmY5r2i_P^k3zZ{;Pb_f0a-AFZDtD8QC||e^sCM|MaOoF{bOM(#bk0b-Er(over6+)h&`?-!}l_lwFW?-7+x-WMvLye}Spa>3Neds*q^y)1S5-c<Q?-!<u%eqVhX(8>Np>U19>b-E8(@TA{Y-=schUnleFzE0|NUnlF(eVx?lzE0IA`#PzU_p-Ms=%%m!E1m9(pby%&$b7nQIXlzT>AC@Z(7FMA(7GY(&~-!Vbls3TT{omo*A1!DbwgecT{mPtT{mPtT{mPtT{mPtT{oZ)S~q0h=(-{6Ti1<r?bl}1nJpnv>^B^b5$xAyvCHyPlZ*T#(f3cyopJx_r)F%-|Ng02%C2D_i<c3c9{|1rUc%x<7S+Hi3wLA8vBJWOG3Hol;UyTCphhL48adUd!Fd^<J}hd1uUhynj5+SN@SPZQtg-MijLT4?22qQgTGZgYoW))i2Z4tzd=JJPJr=$jV~&R`yd2|l)HsAVh@69{!TB~8DJ*h<so+~#B*RaJ$9X=B4J=&14DbRLY4FqF<-_ASg}}|=IV_%MkqKN2o(Y}}To2yH;y8<DU_1B@7EYYUX*uU{c<n$JcovI#)Z};s+==^c12%$h$9+42x!^4<8sIm;<NPGf-2!X_FM=m?TELHEyaQMS-iW$wz!vaETz3QTD0l<-HsDt9tr%wk>%sGJAI-ov@I2gOHZTjk3FpoO=7JwV%_d+Yc)q1xGc?W%;N<}Gz+2%R1LlA?<9llbo&awJF8~&T7h>!Jwu3jJmaN$dUWa=)25bV)gqH(627UzNY+xpM5x&nYz>VM>p9AN(20WcbBK$;noNr>01V0I0I*wTbe+|4%_<s0zu@0CD&T%<7$0gwFz>|Rq;QYB<ZJ5t4M+f)|ELIriGs<xpIDanV;m5<{e1ySYM}{#BI2D|~dZxpl4v+KUENt*?@J8a8sqm-58;)a!S#pMhhqGA3Vlpred=iTo_%ZM}pU7f9{Q2-E;g~r1aquSMn8}u$iQwZ{%w`b;j0ESe=4klQ@HijK!VcdKF9gR#!jFVE7RLlxa>jx`%VHsmFkmeB1Qzq)&x6N#D2oN~7r>i<V`AaQ!VASQVV0aw@Ml=eWf2UF0w2#}4*WUrI3L4e7W`T8#^abM_)+l2;Fw@b&KU5~EM~G83XA|B#bO5h8Spp{WHAN)6nLX>Oa%N0c!4-(s3j*5e5qkRKPkXe@C10tz!dP6ELIuj`;TJ=xC34qa058cS&cl7o5A^Ww%9PAHI8d7JRW0?>%sk5_^}884gpWXITC>@!2^(!1Y8Ba1a<i*J=M=YWXM1Lr7`gF@Dpl(aL^<5?Wy(1a#l-iR?}05^1id1@fRDPd;AGA{sy0mMMV'

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
