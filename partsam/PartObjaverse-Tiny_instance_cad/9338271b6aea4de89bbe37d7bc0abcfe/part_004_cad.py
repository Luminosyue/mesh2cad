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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/9338271b6aea4de89bbe37d7bc0abcfe/part_004.stl', 'relative_path': '9338271b6aea4de89bbe37d7bc0abcfe/part_004.stl', 'source_sha256': '4e102af2182719593bef1de217d6b2a154aeb85c723a827d688e19b39b0707bc', 'input_faces': 266, 'input_vertices': 208, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.21434640884399414, -0.11383000016212463, -0.17991329729557037], [0.3051408529281616, 0.18939945101737976, -0.05179538577795029]]}
GEOMETRY_BASE85 = 'c$}r04{#LK9mh9<AOV3YA|T)aV!$L2{s&N5L6ib&+WIeGB>@9O1T+a!3Brn^BA|#^kw0<}6~RPQ2uMiCCYJ;V5mcPc)LMJ3Sf?Vj9jvvTw$pukpSSG(ZadRyZ|2AMlTY5gef!?qz0D0dQ(Cp|VkBODj7^hPpEJ~tPIYkpdAOjcq;OV2@t_3{K9XW|cD?%|U%2&-TXJ$!jE9ZVwEGH*XBDN5iKJaSJ3B2Sk~Vu`QAtt$f*A{o?kiCKru+wr3mjiOH~+x`=jQ=Kv$8WH!v<zV9*z8uuT(XLeG8A*s$4tj@Hmx!>}S{dyfwtARo-5@xh~9Gi>B51y*c?ZJG7tlyIpVI(z`Cq+aKS4*zb)c>s=rDtfD^9J~!ri>)ffTfZx@rPWk9J9|!t3SDCK2K3G{D@R{xE-Tt#KiG_LN!^;E5H7*{L@EwinFmK(~J~*B=tzu#0vDOVscrhL;zTEYuIA7C#I~IDr9nU2CnSa&}^Ldw@3#^O%O=g2T&!@hu4YcnQbG^Cs{<=`V|NG!Li_;pFkJFER>g8ju|LRwVTz{s$9q_IGQSHv#s{Zw1KKlFL9rAml{M(waevH}{cYo$JZL16OM!!E*`@Olot-DX+-|mTpdeOi3M$^gn0^{6xTVmf1=w27<XZ*7!;Ip1h?B_#G^<m!3-cc3sC%Po|?TTO5g?VdtN#MNf)V}V1i>8<jVcu*U8VmDs{yqP7a2~X`#kzR?_isKJ+P-|xfx!6Z4RZIPEzb*|bYAT$T^|?orhU@9Z9f+aT^GD1*2UgA*4@v>UxNF=^Ku^W5xE~e`PB86*oWGiavz?a)EL&knce96h*%fxjW2`qZ$<8G^7j*I&J4ZoJTI<0>GgG|y}Vwe*Vl#iavw^s_k-uf{7WAZ{mc20UeAwrUSfW1yY8s#Q`=Mpu6MlgQh_^fM#|>;FmF}-tt!yZ@T=U<yS(($hA?mBjy~Y`-aP#In#M41wfwR&aNNi{iG3yd*WMKUo0Fe+&({>=*FG-BZ;mjJxbw;USR+b~sLcDWpL?CePe&X4-o)pf3AT^mt<TTy_xtGD-tO_DS-oR^Z{cM>d3bZ`xr2UhWGyLl$1nQPJ}Uar-j@AzUHYs$KVJmT%jlNyN&WOl_{izRc|||j)#U!3^EG#@YVvynZ_n+yH{dyLRJNyot1!_%ul~DOSpV9~{yi`H_q^<XPDU(jeYKbCtG!%b?dAGvFW1*Qu2^5~<@!n=75&Kd^}JYL&x`f-yjb77Pd{_--}3(Hd2#=gUf(~pm-kQU_5D+OdH<AN-#<Ms?w`^}ME~;sDZRdbdgmqYpRcwJogdH3=Q`oN=Q@1S^O*47a~D48IY)Ro&ZOrM?d9jb@DXv`q|asHz0YNRzGB{@ZGO?Le$Jb)(f!=9zkXu3-^V*PCZ40t2EBFN^+(<I@mB)<MDdXqQ{VA>TesK!l;$1}JuW`!xOmx*ZS-n!+tE*SL*lsF>we<G%kgV3$8YD%3GYXEJOA4X<>Oy;d*6NkZ!;6m)wGx1679`p_axTq#bA5S&rGzB<fgwLHXiBqc&rYw#BtlKv;FO*m+j5mzc={DljIqXwd`Lf-1o0rSM5Jv?c;cTzMk(o{)m5`wKpzLcvJUZmUq(i(@)m~`WN2oA0HpGu_-Wq>FMA2Yx4*0`#;Y(<nLd4-M{wc;>zl<_IY^OK3X<7aK75xcvFt&?77hP+Uxd_Enj>XHb2tq@n|pSC&|-)^sTNRg{`mla(z87)>nJEzR@}RJ__5P((C=Hz1*KkUhkjsV~O#6HPik3G%~yG5x<Xey+|J~PHPDGh;b_Hx|3dy(<p6s%749k`$Tw4w3qjRB(KkF;>_^z2=86j^Pfr_x3oO*cfpR;jef7^A<6${uX|ie`JBMFhg0tOL)G^k3`12rql+;+-}lv_lIo>1{Hw#l;s4!Nha*S+zh51;amH|wQ|dd!j!t!Usy&$sr_x4o7VQSXo%#7PwS}D;MJXOlc7;d7+2jx4Y<LKHF+2p$aOx_uEqO6~0n^@#Qm-q>6!;3bCu1JKxI4qCWIs3+ZbSBjd(w~Mc82<D*f6f96sJ2i)Tt3pT|z1DLJotwz?YJP;Y;C8WICKq|DBlY_RRkvc%V~#ox0Mg3n|5|$Ubl@xHZ`yZVg{V4ul8Nzv5|5<vMj2rT9+rZun044str2PtKwg-%C!1Ro(;N3(p{b3eSM^$Z7C2#-#W@awd5fyvV7CoqCK?yaIll-!Fm}lPlrH@FV2Y@FQ?3`3zhNKT58FABC5bYvJXvMXrV|cp140UIs5EpM;mfOUNhSCGgM474Qn?L2-dobDS!4YN1mPz=iPr<b3#kcpkX`p6k?Xr%K3q@I2a-kPpEna54EHTnrbH3*m)~sfe5d|In%HoSIBt4^M`t;#IqG<P>-ud;@t4d;>gzybYcJPb7Z?PlRtKe*)hOPa<!JC&4$7KZb9DZzOZz8{zTft?+o*B&WhtId{eC9;NOh*N}r@mBV0_BVd(7;eq5Jawx2FlyUxEq*&cwyBUdlZg;XL+#T*s_Je!FY2*Mn4IWNr!NcJ(<S2Lyd@VT|z7`%!X2WCQk>n6~B%DcRz?pEwIRBXxp%nMveAW5)B749+Xw!?l+BpB2rMNG74cr&Ll2Y7<QrzFSHj35t{*;lpzMp_sP>S_^Px0fF;+2%*rzyqHP>R=3iq}$#S5t~tkx#-6PMvfrMxKCUa6S1xT;|kvr#4fHw~?>G+u&Vf1-uKcB=^FVa1D77u7R7$I=C5bA)DY9_$XNmAB7K*2jD~S9`YS{54@9n6W$4LCClJ4=3*=D-{$u!cf)VOW#kUH4Bk#g;qCBi<g4&&a0UIV<LxI8!299DWG#FcZX}!FM%X6nU>kmqJP5xBzf10g--XM`3b=wXmov9-G50E~d}~p~TD?WP*U6pm>+lwGE4&5XL~e#R!LN|p;8)-`$X)Oo@IJB<-UnBcHE=b2jBJLF!N<uK_&9uoJPIG>+!a6T)C*2MM{a<hgV&QU!m7>BaWCUvA~(PrXrukhymvkPJf(OYxe?Bpl5#<pR{!b0T%3Pd>VZ4(A28%QgMV)M-+8^$$ou0fXUc`@x!w7L;R5$T;~{k?HU14sZBSn'

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
