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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/a95c590e89444458b53a15190c7560c3/part_010.stl', 'relative_path': 'a95c590e89444458b53a15190c7560c3/part_010.stl', 'source_sha256': 'e3003c0cbbade7d3ac14b0114a8cde0be78f72159449788337dd4ff0f675fc21', 'input_faces': 288, 'input_vertices': 168, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07895553112030029, 0.22003239393234253, 0.08650770783424377], [0.13090133666992188, 0.30421245098114014, 0.1705690324306488]]}
GEOMETRY_BASE85 = 'c$}q~2~<?q8OI->h#QFDQd}4fiVLzy5EpdnRt$=0P!U`P5QBsO0wOBtxFBf6s04~TvWS{!P+ZW64!9&S#u^ii+C)ieJw2(WCpm3WO=3IW_x&e6-fPb3X*uVf-;cj{?z`{4JM&$}$Z&^N?uz{MQ9J@`cNse=3bhW3yON!lk+moxG1E6SeVLuoiF5j~u{dJJl*rk3O184XdqHAmLWcJUgZHR~A>KX)?}cd@Ss8Ju^V2dGBvL*xE+sS3nr9}(r6*c{9}o~6;$s*((8rKx_#c1T(Hv5PkDsS0tvzymjFskwyNyI8=6)UJ=JtQ#T=}DO1M_+v=St*>KhW=%m)~eq=jOU~AM@`E?3<W(=W}j!cja-6&ptfcB47J1_qX&uCgV?i@feSjGx8e$etbY<i+p6*4f@^ior8@3{^O%OpNnPO-_rQEv+CT^oX!0$q5IEq{_&<-?*Ax{=Tjb1eUbCY!z8~N&G%J)Be-RLb0*KT`KyDHAG-Vw&*!@PN8CTK)}qc8=ZAdV@;hJ1{M(r%&x+>$7N?~R>fCa_%_p4Cym6lM_$izl&%5(=jq93Eao)532w(TsNO@l0-)oU8U;SCuzuTpHremJ;|LzfA*ASC@L7iJ-`^b8hO_2M#-R3a&cl}b<^WM37b*?z=l=X~Ra)$FG*>7>~^7&O6H>ydU8xMcL{guP3<+{C-4srkKMLZv)W6BwIZi(p2>tKv}PoCqMzaHfN59Z1E%K~Jb@12yqc{S&j_!;Naxy5YaaZJHQ(%*l74fo$><o<>U&hlK09+H2tTgLg*nX~HLyed_m%i~q@T>Oiw_`Xgo;`O%#-MqwkRUYT&M*+Nl3~i%Z<QBVe{9H`UA4(oPgL5VPsyvr#ri<#_Qq@VGONUX?-?5vF|BnkiPtz^O3oY{U2JUal3zBgLT(0E2PZ0Mv&q|T|?V2We>p`3w^D^bW?7K@IP$TQ$9C)@xJ}^_(q5BWA&I8`7;C$#_+0QXar(5J>221|~7vAOk`$Eo@!B2Q!nL}rvQs)-;8lJ!Tw2O?h(In%9yd<ALCBsjub7lPBc|FZ1JY}4xk&@@XAo;w0(*JhBULI#jsO+D|-i_+q5<Z&esbp-FeQQ~?hsSB$A?r5uo3rZN_-)E3GXFYRxAKS`+&^=+^v{a5sB`nfaOwY~L9YAY!FKMSmMinQS|jV({ZSd`pWT%8SMr<GxpC`ddEYf3mFND`wNmcyQ6TI8<40%Ixh2q3)_>AK`J8$C?PBhq_<;MHe?ELcom-Cfl=aUll>HOgw1xXOd?wGU-^A1E+&s5b`n&xo*Y%n#d2Iyme^Ye+MRjgTn8weg-0z9x{^K_D_$zYcb9mnmk{AB7i1QQeWS;fUEb82-d@0wR?<4EuG;b4MH#$Q4S9Ce2&XpVX@_CXIBI87#+rZ-_2Ft#(&#hPI%Hn3(KeY*Rzy6&Ic>Z5IOPzYKUivFPE#>}oK2oPPl{Bhz<87mS?m48(Jk7f@d7jTU$a*gRph2A*SEkAHwSCSg%YC_jY9+6y`BUd6b#CmRE9?2z8thx&Y5e;2PV%|*uPY7e+_>$S)Dgo`Ss%r94)^n|=KiM8I2ot;>m=r>dos@59@77=<3WDC_MFhOo^#zf!Pn)G>=(^B0lDs+(EAkUx^sdp*Pau)wmr<_XwM0@TzgLND&t&tPC%|ZCzSctGPUP~Uh5>+o)c`j_MG5$n{(Yc0lDs+kkI}pQ+rN8t~)2xyK}BPC&bR@Tz5`Dt~)0@%$5Gya{_YRIU#r0G48KDCm`3I6FMt(Ozk-Vx$c}0T_F9n=LF=sbHb)e(%)e!=gmJC%X&V&Fa5RWfu@JYIlnVTKL4-aeH!L_g6~UP_pfJhJ<-+u(p=7UbsxE|?qA&^bxB+Ik?ZRI!*^tSZQZx!+PZ)FmgM_}OWpbWn%vht2Y&wMVL6-|9{I}pEcBCHTi-vOCAqe~+j4Dv|0Y}Zm$tqm*VT8g*JT`SeMhdV?{l^awe>yY4(~f%9Z&Y;>*(rrV1M36y1MK?mUH9#bLGC0Ps%=tH_N`$)@9_nx_qFGtcSKPBiGgC(buKFwk{*r)#Y0oWxs3dGICvAHXV>$TbGgR>T=e%GQPGhUwJCIwk{*r)#d$ue1E#Sj9gcjJFVedSC^6N>T=&Zoa^ec#|U}O+PaKfSC=bRbFQn)$aQtO>r9@nt}Y|j)n!*R=eoL#TvwM}N~FKGE}I%<oz!(Xvc<O#cX~J{D9%>3wzi79vM^5d)dT;7qWr@D{MEyvp#SQthrp2k`>TiH);YXrZKJ>e@KNyoU>7*C1H3=n3v34`_Jw=F$Ac5#<Kff68Sv@wC~zh`3LXwlhWmqo;AA*)C_E7EhDPoR2Ebk6ooNe!eqaEc_*=LiJQR&Q%-U#AjI_2X;6(To_*5_q9){OW1z&;_UxrVGPXVW?#+-(0634-b{Zw-ydV~Go-tg{d<nG`LaAJG7JKPbphdaWZ(8ybX3cMBE4s?Lq!CNczMiI6F9pJ<+aN=*^L}z##cw4X&ye+&N8hH<}H=Ni9-UIFn`oMkRqrqWt;w1Q3FcO>ukAz2nzk^4>jo>Iau|J&X1t*S&6Q{$CaNC&EaZO^BY7SADBQYFqd;i$xJ{I>n7P;--{Z;GZkF_KQ!ijFGb#_y&zZ;$>(G}hrZU=T&p6>_pR?74Dp>6+=)Bd8pN_(**=m_r!cLAN?E^rU9E8GJ<1oVRwL*YZ<!D!?oz%cj-cnCNV9s&;nN5X^P13_>2K)5H^9qtM533i0{g!ckn;Jx4m&;xFO4+e+8hv41@qmd5+N5Dtmeg=U-@F2{45a<c_#QX+<z2Lnt5Ato+mTzr4!2&pOH+(0&3ao)w!7IT1@Cx{wU@3e#m;;u=iA&)*@OUr|9uJ?5Mm`HnfX{-*ppmCoTc))wv9?v<O8D#GMl|w5a3#DDo`<oB>EKHEN{pM1MxF>}!V}@Ippj>RtKeDiY&3E+8u<p*yf>hc??59j12@9U;6-2|yb$+LghswXb)PH11o#U0GB6Gvhv&2mjl2Xbg_po9!Ts<`cr{o9uZHgecf;3#>%rY{VgY<TJQ<BV3CxEl!53NEYv5WiA5Po`Ukl%iM!wzJwpiOHYuf|<9=-=&4sM5U$7{>Mop53myd1s<tWb?vfol@qgxlU%wz&{<!R7E=cp4h{t6&bC7!Q9HJ{Oz~p9`OlMji{!g2%$6!5DZne2%r5z<FQ{oR|V9ro)Me@Of|(_zK(vPemio0JGr4Y<LEI4QPh1fxiK6fD?DXi@|;14){L!Ua$<l7rqrNf)iK3iOb-`5;(CEz7=j8vl7=NR;%VvjX4r`!ENs!+uVzBuf@o1_r6ZGKI^cS#Px7uvTB`^RqLOO=SfV0&w)pSi<Ia4fjm}u{ywzrA9C7Xv{z{_E&%7k7r+;S^Wh8Oi^136i{Y!mwQ%BQcx1Spy}QG&{nz#LA2T1G)&G&LePzo(JJqjTX&vjAKSCqJThsZ-dO)}537)1Cu<~zZH2@0'

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
