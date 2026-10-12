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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5f1e1e7148424a6bae25b5138ba0088e/part_001.stl', 'relative_path': '5f1e1e7148424a6bae25b5138ba0088e/part_001.stl', 'source_sha256': '18f74e87893d0f350b9e9d2e2af69e5005591b0d39300c695cc0bd150fdce87f', 'input_faces': 128, 'input_vertices': 131, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.12926121056079865, -0.05743441730737686, 0.14517788589000702], [0.1530003398656845, -0.02499603107571602, 0.17037992179393768]]}
GEOMETRY_BASE85 = 'c$}qJ3shBQ7Ct;A5Jgik5s9Oy$U{>E1q40#fbs>RHb{<M<mm&@3u21oQHr&+NGHtHoV?%*%^uoV45?fd$5*I1BWf=7wp>|hKE@_f$865o-)F(BnYCt3hqc%Do$vm4|NGy2|Nl9c<k2p!-U_a6N{_(W@kiPyifL^WZ>2cPS~MdgtFUkWoCQuwd(qA7F;<S7G&Xs%lTxgd1Z8FwW>|w_)S%exsGu-4D7(N~WKGYXR$$G{GWCS?*@an#UYMIcC(F3+-G4y;Fm*t1m|Cj-pI2)m1Y6as_Ms-8PpGOl@k-i3^Io00O?16N5#8S2MRaZNA&hU8Vl#Eey}6=WijHIa{w<qje0_L>d2gR}R&+<$!cF3TQM%}A@HzO2h!sEf13vImcV2Ymc*7P`*ZdxeuHU)Bc^|?5=~0L??Uv~3!^`4dak-8-Pu>$<bGp4z^nbQPJQ)u#{^xz-M{jS3|HOxgKX8hSx4i$djJNnY?U#AK`(UfY@4R2e+v?hhu6G}{LG;EF=%0Fvu2|AUS3mL>-QKqo{M34gf9+zJ__q~8S5nJly_Pv$WV~{?v*=p%e9`r{-avl#JPkh~&xvj;J1>45H-h0OCmi`{bUh^Vz85OG<HJOWUq4kN<CTnoqN{smREvJ_ZTPt|M0ES4lp68#{wv6H#YpJWM#^~AJ{0+BN)+94{tn{&DiitC#$w)Yx=URg=X*&!j$P2Tq>kcW3oaHvy7xrnbLhwL<9h3W`29mF=Dm639jRlYAMzP81%86Q#rTun;$Od&4nONEWxSsCqKtQJ$U>Z9_fhx5(THbt4)VG8kmN_Lx`w(W<-vd6Tp6#$eIVmikHr{o+bjFRadb2C)_V!Yd%Z2|Qa&Fcy7n4$^@WeIzZNIL|Iww0b7COsa(FQM=Z!M>N%oO>ZC^Yu^IEE3fqr<9^pAZ?9O4ftM}B@RMZH$-L0vY!3jIi>=z3BT`X^;I^rThD+ofa3^VoOLKUJrZ=aKC&e&=TBm&>rf?1zx&*LR`5%g2dsxt}Y#E%{II-?JKi&dkKR&Ouk!+($efE0MQ~dgyl>Yp}n3kstqq@RR9;x>We0jy?Z^yjAB(K9!xwv*Xb*`0;PGUh0*$5`DY<IP$h)%~~0sg!9d|;Ux5-%h3P*6A}Ma==LeuIQJ^6k<X`^&_6!}AaCxwByWzvmzmE+vfs6p4@FmgxPkHgzQB3nd=mY$`6lA*7_v?LFU!VxcpJJ_UXSykbS~n#_cQeCxj0X1CL;bMXPHNBU4e75T!Fp<y5_b6`)lDpupc8lM7QsD*&*@V_Ch>6Jw>;bSY^H1uxP|{rmg7uJd5<9^7oBc?`$9ROOL5?ZY$fqLL3V_VP4PN_hen;L&U$<t=oa-^|Dp1LVZ(uz)$x+)##t$h$pfy`~<p7ejJbM`%yo{zrWod#s4`g)_XS`@i!J@UzFy<&%#K=yZV^)k0lQIQHus5Uax%VTdmQC`?fKNXL+Nn*O7k*ekTmZymc|?x4$*wes(OdY7O>X@lM2D5(oTlsl=oIbR2c8qCR}4<V`P$K|jxnN53?kSSR&e5ry-u^Kj@xBe5^yFJM2O8iRb+A4R<$^h7?dKvzDQjQ)wO!MIK1u#R#KeI8f~-6a$2z4%wjgYJv-R;z`sZ$0y_tk?Gv&gb#DSZ`Un%&Rv9AfNHGpszUrJ$f<fm7NEj=Z|B1D4shB3!rZ)L4I~j$NBa|3F4`rC-u_a`V8w`3*GVHLp;Z?-Nk+UB4AF0tjpmQiMqd5iums@!FqeUqyK+ejQngmD*MGzb_4S{m7)H84k{h-o}gB~j5voql5<Qg!1<|lE{C5>eWcIzt2dFKsTI(}mt()j?L*ynuZ5qQRIJNy9qMtTx<x-bj(edW+&3Zq>pISvLC2t5sPAsVd3e_!dG1-$a=isvh=0d6tS==2dA@KL?-f^B|Ab;Z*D}7v`XlNP*R|6a|6>yB;`u4`pqVmWJ^MNG@Yx>ZpXa}}?@RQ9vKM_cWPtRKcBu~MXXQSO-`t3EqiZPY((44`ala_*RU-VD|C7kiqAJw)`>uH2ojKiNzgucYA^&wvSV!;cqB{m{!~4&&bBKrUfsRYxV_b&|!0Qv>zpW?ov*j}K_UBJzy_SA&;(ia$IlebqTmv!hn6I&}rd5&$`%44R=kDJi{#ibFPrh{p-(P(j__bBWtEExs6JMM+dgmOR&%q7ILxUU6gM(+WuX~|yES?^ygSF3g@jq=V<{i-*b!fVZ^C19vw_NCe^RnxD)a%p=<a51-I;4GxeL80&-dh^j?*TzlN6XfC(QjpMLho0O=U0+3Z*q%YLCLj&OLaHHrC}b%ub}MoW<P;U(YzkxfBp$HBjSJi2^1dnTYmyQX~fXkuqS9HZ%^z=-k#i#*q_{wJcJlW9zs5dIGWtV_-1?(@8iiw5vP!kBA-B<N^auBX8d=&H*pO4Si>?6dyZ!EX~bgkY2-7Bi^yk^7ZG0~FCw2uTtGgLynvWRUO=8sOeRk!Pc&=*F@l&(?qpai<=4yP&Rk;>*ExoK7%`T77<m-2FL@MsDDi3XQ1Y(Cw&Y#Oy@<}_&Wy+8W<Qv{5==9BC*qUjoygk|Ta&jTcO$x!yOFyPJ;+_iT@CXjwj+9woAwkx_ayfr_8|8m?@kOS?@m6DsF4pOA3;nZA3>f<w2-Hg=Ne`u&LCRIP0QowR`M4On@^lg%p*4~o1f1opJP}K@daWwxoPA1c@Ftx;t=x5<O#%n<O$?4#6a>G@@I%$$e$tat(eb0pf|A#xoI8vxk~O&>`3lU9zgUZ4<PSF3?lDE-iH`T-iLg!Vb2mr5+lhM8&+u8LYm2E(M+C3%pgxAf0px_b9AGbJd8M)Jd8ZLSsc+claC{2kk8^AbBVtvH=i}n8#bI~^6A8U^6BIy#8UDS@+Cx_d<pqd!;(ikIeWYOw}0XNdg<nY)Z!m{|NhOEkG<yKbTbZ*Umk+Vqg%<N&)N7h7r5W7wDK=^zO!l'

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
