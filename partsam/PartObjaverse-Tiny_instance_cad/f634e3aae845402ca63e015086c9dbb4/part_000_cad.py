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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f634e3aae845402ca63e015086c9dbb4/part_000.stl', 'relative_path': 'f634e3aae845402ca63e015086c9dbb4/part_000.stl', 'source_sha256': '8690a02815858c96f6c6e111fbe119f7d860a508f64ef239c86e2900edc93838', 'input_faces': 368, 'input_vertices': 324, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.30777493119239807, -0.05008906126022339, -0.34370332956314087], [-0.10646485537290573, 0.33771705627441406, 0.3416479229927063]]}
GEOMETRY_BASE85 = 'c$}r12Xs`$9)~Yo0YM}RD1imV&|4^h09iVSVifF!r33+~As|Iy#V9S(0*IlwAVma}j!4NOi1a7L4zf>uDuPm;JiEM|JKwB3GuL<Cc`xV8`F;1BVKTXQXZJtJA-zkX!U>N2s^aXsX5Pt2CC3r1q?6!`%*f2@-#cS?-N8dg7jUk3z4%g@+x5P?(jO||jC95(^~o6CJ2R=dFR4Y}l%(3eq`pHkvod=Q?lB~@PloUvdJY_(5%t6S^&FZJy{?|zuu*Maa*f))alZfYt9Wz?p}8AQ<cqb8n)7U$$QD=M&-d{DCaJCu^eT8<WU$JQEAr#Uo8BDnD8DA{q?Zq8wmsoFzFEiPp5w3Ham>qyM%?|LrysTAsFx2GdHt}bzqI9`=X%EP+VAB9CHC#}96$faUeEE_AH415ePuoid(PA1&`#|>`|t^;w|V-y=Qn%$PQR{q)9{f!32VH(la;c}bNt<F=X;JHdg2)`?^~WaHqFC_CeEJc<%1<_z2fN~Ew<Xz&&gWv<(;t^n?1(|?%x*g9pxvt+v(*4Tl2zRK2$UJZO?gHP2KA`&-#h`JjdTQcE6Vozc~D$r(Zqbu;)CLdLQ-jk^Obv^Yr)DIOaJ|PPOBn<KL-r!gKu9#FN^6u8f~j;e9XfpK;ptzRs83ee5)>{F1nK4t(#vZ&*HihU+6G@CA;{7e4%RYj+;g2hMGi-?!j->6cVl7(c(|nLps*zb!W}e!S%wA0Bp2`Zg=(#;?cpYCX;n{QgS|;>Vl*ug0tU7M$?0^jkXR#;?=zv2{uxJoMe-`0<uk_o3=Xa-Q~^X2-A7^lF{K64D2MKD9W0yy^dHeC+j*zg^CM>za`EdN4if4DQ5N{BovtA55?AL*s4I?`beodtQcD>x@*vf3rTMz1|G3#)nhqN<X{obnQNyp7l71(g!!@Er}m*c{RS+EZ2v#RxHt8KZcL3|LjcpeLtU+qpjcYvGu3-<8_-qO<TX|S&uJO`tZQIOSR`^ddB-J^^!l=h1N^s*JFCMo=|b=o!`n&jUR9N*nU}%B7KMDtK6hMF}<o!ln=JYQ=gb#)hE_?>Jw``^@-_KePVg)6Vt2u#PZZ9)_SN<Ot0z_YdrOdHJ<v!^r}9w=Ak}`-Dl;gPb^P;VtMKl(}$@~OdlC8>l4dUpIGw@k@bn`1Joy`SM`bIsZT6VePVi5pO{|NC)RlClh}Q3ho?R<y{b=4uj&(P9_kZo9_kZoJoQN=Pxq=mu{`yO=~aDVdR3oTp8CX^hx)`CPkmyIr#?~MQJ(t5^s&#`()d60I>cWXKk5hf{U=sem|lJE6p%hVwU_ojX?eznj@6U%tZOqx_}KfN;bZUHZ{bTG)aoK<ne@TH=%xS3$3B;TDkgo|I@&rduRf2iNbgL3Q~SKIyc+-H@9z7b|43VXJ%(572|OUZGt#HM|C?To_nrMj`jh(SujN&p^M&;O3JbK)U(2iKIPIwGg9)!{pTDM$eSQs=-sv@6`}{S1Z2iMFN&jI)t7j~)>Yq;1hx68I^^)b)`n#==^K`DS*FT1j)emXXhie)2kKtplpI!6hJoj|b>r&IJ^{m4`aZ#^JO|R;W0h6S!yj819O&_cOyWvls(dtsu$9~>=+44Ci>*oc_tJiZ~>7A$b^Md8o`DMpA*6GvEJC;}P14XmAZ%gNDuOGw5>Yu{W2S4~uKVKL=_P)`7kesLdyW0DP>Hn<T!)~1tJYPh9uJp;1_y30tt`Dv1uldMV(ua#I-5u}!FRz#LBo}qZhp!%!`|iv#*ZT(c)x3Y3^iG)-yW@RiN{*c8a65he9@6`&y{oM!cy@wZPuiW@Jb_)(2QTGo-#2)<tNgvu#4BNK{)qI!X65#1^Pg!a{fv@(;^zs!D1CVM)v)HPUOnRee2H&r^M^`F?@a2h%^$k(qx6G1YV-T{NgvMHtIhBKWr^z}gJ)^;2d_vUJ}^d`-}m@p*9V6V)aLhhmp+jBvNnIPQ!6?C(<1uw!aJw**NMNf^nr`BwRr-Sq>psY*6%|i^EaBTtuufRyf9i@r<44d{C!>reVu`CPP^V;VvsgI*x?h`hc@Z=C)65WdaV9^mt@O&{0{v-hek>tzNkN!K%H@NJwI;M<_}bm-s!17-{AVD^7|&~uan3!>BHNN*VQ9+Tpwwtzdl2q@xR`rzkXK!cF29bJf*+R{p0aD`o0Jiz3BSDxqaGm44=B-djCW1wS5<O>_a);*r$Per1w9d@9V&#gNNk()ZYg}s}9KZY|!6N{0pV`m(t%)BKPi)<F^>Ex1ELE^N_#7M)~_J&V!~8s`DT|sK!$tn%<#4jAZoN<vxd`MRHtGd0w;pWqDo;8$Qf=&GZq@Yu0$qYu0$qYo-rzUNgPFr97`${ziFTvwS^yUbB2>d0q>d>v>0>*G%t>l;<^Td^dSsGrfP5Jg=EPG)JD-EI(eJ*GwNQF3)S0e^{Q^f~L=v=QYziW8`_w8s9^n*OZSaKS`d~Odr`I&ugalab7dM!+Fh`XPrE+S>rjc1q|=!yk>dMYo>QNubDo?dCl^i*R1(DuUX?cuUX?cuPN_T$E)8b8(!_lV5ipG-F@A=qqZL{&wdOTUhPNItNmz=SAX9z$E&~Z7+&p1)2sbxdG@2_*^icIKl;sevL8(!8NuIoOwWEay~BRA#<L$yulA$m*^icIKl%)>_M_?5ezeB3A1%**G`-r7rdRvX`o8Q(YaaHaHJ<(Gn9qy-XnFRd>D7KTz1okKXFpo=vmdST>_=-n`%(FT^6K{|9d+;S$8_zl<4fjce;qCpeJMuUwN8T5w`bg+#)TALD!u<S-oMd*_owkDDgW=E#(#>g;b(EX3&<w8GWiQEnqVLKD=eDeD&%jlXo9Pfzr&&lzLop~7ESPN<W*QS!PQ8ofMn4G-%b{QZ-<k}f^ZUCoh$@bhij09;TmvFvItxgu0<AwYr(b2VsLG^4tWh+2d+zA3)h9~k;UP9aDB1_Tpw;gmV_I?4aw`^hHx@j3QmR_k)`2AaAWd%xG~&>ECV-zo02!cP2m)>ESv&2BNO0eaC7oTxH+6k-UO$@Ey!|k3%Dg&9&QP@A}heH;571PI1Tobx4?e5HCYjE4Y!H5wqzn%5uWDAzItRLELvSh_D_SSl6Byz@D#E(JO!Ri)`BO)lgOIzB=~u<2K+qy99bQH4$dZ%;B5F=@^<)Hcp_O1o(Mlf-UdGd2gzIEAUuJr3QvH?lU3mH@Ho;3kAt5kE5lF2W64VJSa=MX2#<kBlNI67@F?;Ycoh5;c{BVJJd&&ckAz2%<>3)<7FiC?f`^kg!NcK9@<uol9!4g>!{DK0S$HTsguDSB0uLt3z=PpI<n{0%cpzCC9tb~4mV%#z2awmn1K|E-Nw`1Uk1PTAgP$Oa!%x6{$!p=ha0Yn|oB{VCi@|;1-egg@H{6RX0{4P@l7-=(aDXfX2jCvj_BdIPECfg2KAbC#{1W*CEZ!^H@P4D-kEZc&3NfY-|6Y70@*ef0BlBO5<g?NCk7)at{5vf26fE+6SmZHS<Plip0a)Z7SmfKV$i1-0{jkWxu*mmdktbo1pTZ&|u*ffAk>9`~zk@|yhDH7p7I_I4c^*E`eG$AP+IB`;nA{C-h_;RNZ=_G~Ytgov{?+seUKVZ3>0eHt;Jj#?6K%QV!?4JEVUc&jBHO|uo5La-!Xi^(k*#5ocfcaM!y+GrMb3gnE`%5IGvt!5!LRZ2<&rz#9o(l}au+Oe6P!mbr3qd`Zi2=4UBvfX#JyX_+Gf)~o4$pt|1tU>qi+^J<9+nsN8h8|hc5JYp|3mlstx^Z=o8$Gz7)6(*W#Wh<CE!2;kl&JpGu$L_R-cN+S-w+a9grDnF@>Nei!|B#f=rOjc)XJqffAS{X9bdBlHOtud%uG&!z8Sp2Y(C7tl9{=kf~uuh5srvsp|3TKbmq+&0s{nZ7kV_k8;E=@T4w<eu6^=EL7c+egv%HBImrG{I+Rf=|-~e?Sv_oF@1vP4FR_;C(c~@6ZIlOA~yMCirhO!6#^fKcor%geLein&8iAg1@2(K1UP$Jx%aMn&1oMxA0rh_GYwgC%47%>s*U`BaT;aEplZXFXme0%W%_ZYY=TYWMlZHXqyf<C0o%1ccuxxn<n@Hayq<{@0CNo1dH$EhedXTMcxC8d<Ygf6BhX*EOH4fauqCcJ-m{9gO<a++6Hf@3EoPshsC{`&)Vm+e#I|v{Q^I);`_P2pL?LVE7x7QUy3_%-HCguxFy#ux$labaNUGwqqsiT^?8<x8*$x;`>r^R>olH$;tpJQ;CU!c=Q^EdqxeCtALKbHp277Do|)o#T+ieADGqTR;#n$wmFrh|u8P-jy^iOlcnjBCc!rAK;#%Z(IK4}Of(eEG>c2+(`4w~vtoZ*ZVg5_~*GBRGvQqR=68j}mdY2-imW&o~1>J(Zf_NIvzX4@zENl'

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
