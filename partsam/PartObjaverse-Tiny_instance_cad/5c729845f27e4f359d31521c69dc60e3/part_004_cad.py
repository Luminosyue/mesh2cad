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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5c729845f27e4f359d31521c69dc60e3/part_004.stl', 'relative_path': '5c729845f27e4f359d31521c69dc60e3/part_004.stl', 'source_sha256': '3dfe8b8711ecef0abced861c90a42218357563ac2005373cad775e046f40b7f4', 'input_faces': 256, 'input_vertices': 171, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17574894428253174, -0.4962303936481476, -0.2213374376296997], [0.17574892938137054, -0.1367698460817337, 0.13711944222450256]]}
GEOMETRY_BASE85 = 'c$}qK2~<_b86HFwSqvK7B|MC>C|YqBMV<?0K?Q@jBthOoQCuN_7^2|CeT@d(Si~m~7a*+?IH&~Qb&Z;~C$%+c>GqoTq$cU2Z9R=Sp0qP_zj<%&<>s86mUI5|eSY7(d2{FgXYR~1InldoFwy?P$Tx-Ovv&s(!XkhKlY-3L{8h^`^G2=DDfA*iTxWj*%jTudO<v+f3dp92<(YZQawB3b5mQ%8iioyEtjNyI&$X{l&(2+*$@JOwwRxFT&&#ssWYT{}#!QTfwv3I6wiH?Z$3H(dhDXJ>oD?kYe07JR?aS0N3|&EOHyM(^9d~8jac}uexxJE7ddW;D$388IXP8%iL+-~~Fp#%5>g4s9&8)p8DxB-e;*q-VRebMX=bvvVxGC$T%kb;E_I{xk&2$p`IE#;G&u^~D{g93;8M3anzRy2rTlCjfJ`Z1yxu$!r&wE}s)0I#5zsJX)e)y{VT*{hCt(`%){^d#oYj1lvN0rB^eD)r1*Ga$QdzOzg%3qbo?|8RJ>leCmDocC5`!Aef?Umr4JGp)~;`j2rS+~?(;p2+CrqgXcv#!YP)wfGp%ybfxR>Z%5`>=MoAH{2Ei<wTIRFv@Vz1OYXERU97R<!Bzl3v>^>+0OcT3rM<cJTQhlzUm8f7i#px6O1i{qjXV&$pbH<ndcV?fiL+y7EnU6>IMb-*-vQmu2GW51l4D=~>ju+FQroy(mAg<IWGY=QQX_U0ONMW1sV_y1KnRgs(%Ru8jU$Gtc9OO|A0$xEe2i;55-m%z-0(Je5g0-Qx8Jjz(QMwVL-&vRj(ud9b#%@H#T;%81BDKAr*IP4aW8k79ZIPP$KAJ!|inmvMpn3#zWmc~_tIydaN9EiJn$>+0CKJnz=MC$)Mm*?nGD{~P_Zehs>-c5FHSeDA}Jyj^37woVelRX#sMLK}7SHh9`br=+`@S8D4#r<~W5GW#bDa$Py<V?Q#})qjOJdH?%=Td%8=L`7To2HiUTTswcR=FiW{dAD@@hu5=FS5wYj=Kasx#&tC_L)%B~O}xF(U5}3O@vHVgt^JAYI^NIyi`u@}HFTS-TNgj!`Lj)L)9Smup;pej+VSrjX1XQycoQFg&BGcw@79VeZM_<F@{7U?ynWi=PwDD&R;@NJgRUg~?nk_SLN*=I)k$6!&!<sWX6BXgdd{-{d7AXSj((9^o(;PC)32N4_U`)6aO&C%-L)*DS#B@#=z4JIBd3Y3ym8m5>tE#8>**b*iB4)9ALzy}_OUw)e(W^S9sSR#a(nlDPG54vX`-v&2DY2&itXDr-E;k_AOE}~?6nKB?)u`kmM2%eZv3_<^R@R**nz8Zd-dZOZ67J@I4bL6JzCej$lF_K9(i3f<nsO<G2{6DCUo0|FSPZ0{BbhZX`RHI)QQm56aLrby0X$bj5n!Iqb}-`)p`7P)W58Y`X_W9$>VXaBZKZ<cXXY~y1agQe=%M+bnBPy1M#Hu{$SL_{y^wH6ED@F*nf<=*ng~aAB!iQ_cx<1_BS;wv{4?vTKq@;-Z$!EUsdQn98Ws$!{pZwxbCi>fGn<C=zgv}_X2Gn#(pkz+m2n@`p5q7pzjOac<>%^>l?#$?-BMs(&bB>f9U&5t_Sg6>!jno=33v<B-ev@ZyI&+-gH$Ywd(2t?_an6&vvbD@xHdv_q%RB@qQP&^1z{eAI<~p{2<qZe6Emnajvk?^NIXi;@o1?#kobH=O4L##JR|*i*u2Mp09N41?MiKF3w#JdVZ7ZO`PkDx;WQaCyZ><)z!{6-mj~&s7+T_!O_~fpyx^cxtX76`x4HXLRUK`Yv&ko&iq-ocC$LM((|ouesJzJ>f+qX&d>7m%I9iX7w2jVJ)g_{xWAX4=jHb9`&y*GDvwj#3xuwO5Z%3i-7j?YAl*B3I_@3p{vzjBzSqdQxYwxkex%D6?oCGBeQ&CK|C*df)!&=%=j>jln}6KPjJmkTSwH*gnw)p?X)W)^LhpmRb%A@LQ5W|_8@+Fu<(=J6b^VC>&#k|qn+M!;jk>t!D)hdrn+M#Zjk>r;v-`N*k9#~JPjAZerhNF1?Y#d##of})!<Pv=c|Q+}Z^`}hev);+VkCCI*P;ZlB|u0I5=>UurJpdENC<JG`A-<D#(l4!Fvg6Z@c;gVv4M_ZKaE`AUhp?)?4z*(xF38yjm_{k!()6ojePj|@ECucMjHGyc#JQhu@L@3c#OYDV>bNR@EB)v9s@rH9^>O_M8c1R$M{$pgW(T`$M_Fu41_-r9^+$Z41zxh9^(^eM8J=L$GDZoX!xVyG5!LL1o#Q?7+*jm1%3)V#$Thc6#i0pj4z{+2R{!U<LhV?!7qZh3_05ie=ods$lEDs46DFd-cG<j0dGI@b{PI)c>9pIx8T18Z!_|?0{#kk`N&%;{8V^p$lEmd)8H*c-iE^;4sSN{_ALBo;l&_te(?R^MIvwA;dh5O7<u!D?+<Sv^41%EZ+L@{w<!2g@FI}6IQVh!Mk8;F;4gxgfV^eG&xDtPylsNN3EooVtqgt{ygcNr3Vszl#;4MlK_eMB2Rs=(3zz|(1-=DX2)+gUC~yb(QE&%>@k0p4-$pQA0xSeC0pAGB0N)611I_`rfxir#0sb=hEE>Kv`qJnI3<mE8-UHYVya#wMpar}acsMW`JRE!~A{yU41AG>O@likv_$ct9z<%IE!3O|?!3Ti%0rmy&1Kyv;N*Z<=Nx($#B=9M~>EKhqhXF@`4+9SZhJpuy`yxW|-F?CPBN%@kI0F26@R7jj;3L6j0u#Y!g1-c`gTDlxPU9er?KF-c7%v9C30@4o67eQJZwF6DFkS%M4qgDR01tvI;0J)E;0M6pAzGa?JOnHScK~aErQkK-CxHjS58~MvKSrY#{3Lh{@Ql>Y8GH}JI^tQ6j2{IaC!RIS_!i(c;#uR2X8~6e&z`_|GH@R8>>-R#1;!H3x?nsUID~lC4&%Lm&k)aAW4s5@hj`W|<K2K>#Iu$e_XTz(p88}w2-uT&YMAk1z%b&edB&#zClk*aVLS;qmw46`<12xyh^NLFF9vQUo;uu$Ty8}!j{r}C*W%yrA{Z|RZUrv~-w9j=z7u>6a4z^7@cF>W;Pb&J0>i*3f`<Tmf`@<y0K0+*fOi3Ufp-BXKp*1yW853~47fLVAaDqHAoz2@Sn%h-CjsYyPXd1hxElNw@U_5g;A_Em0gr?40<QqpfmeW^2A%;w4PFnd1+PUe86QVuF^yM&IpD8?X9M?uXM^tsR)g;bucUDncn(+%ei~Q-td_=KjpwUIzv6lKU_SO>9AbWQFn`I3UR{E{zw5tXJ%0*My!;=s#!u?6J@O}S(Z1Z5pyWg!w!UdGb>SC>5>|!ezy2|wHU'

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
