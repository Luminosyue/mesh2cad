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

PART_NAME = 'part_015'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5f1e1e7148424a6bae25b5138ba0088e/part_015.stl', 'relative_path': '5f1e1e7148424a6bae25b5138ba0088e/part_015.stl', 'source_sha256': '3011016cddeac277499b2b36ddab973d019fae1fc2f74e73db69ad486bf3adb7', 'input_faces': 230, 'input_vertices': 173, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.27056241035461426, -0.1254376918077469, -0.25932687520980835], [-0.14491800963878632, -0.05093882232904434, -0.14295640587806702]]}
GEOMETRY_BASE85 = 'c$}qK3v^V)8J<8=h{!_?K|x_vBtRoV5(yHKYlM_QLY68IdASi12^xZ%2Ovf+NQ6KVgkX3jvWX%}04qKSB5)gHfLa3{D{Ad&7XfY6V^L5nRoj{QzS-{OwCD7+d(L;hZ@xSC-?=mY{ByJMj%yzoBk;Lie9`ZVjZNKzP`F&gh>{$CQQoYa!a?)qFNzS|w68vftH)2w^xhjGO2p#0**S%?{BgrQaku9Vi;MTf<resh{MqyFEAY?GQGQzXLxnlgFPxJ-KS#Fv4@pjp_aqL8_mq16$IoSI3}?LW9+DIo8}*W6drkRUx_t_M@YvEO#UgkAVa3jI_`c(Jy{!EsUE8$Z0^k07{p-5@>aDuJZ$JC@jDAI5pEl^2Vrvh4r@^n|+q19yt^VF!@U6N$9mk%vU;EY$j_3I9{o1cccw5J9fG_@0hjAV{t;Zj%rGI4lKFw+0|3=5BZyh@DD;*~#SC7X>-(LUai@JYgyCa&bInLS7?9}aRM(F;*wS2BuKg0MxEYsr&tf4>jD~u=gm3MTzir<?U@rLdn@#9h5UdHb|`>7s}s7TiH8Cb&p-MjA9-{0wIt8SNa9>&J((f3`vLH7?XW}K(H?$-S~ChGBfiZ~B%r@yAJ&)JLhDxg2(u#PV}r|R_*Q~12~>-M8P330|UPs(;7&as>HJloy6VLaZIc-}L~$94a|bw!+ljfb?q>2n=F@K^fNV-9M+a)+KD&uO=BPma~k8~D9Djy>*#p6B2Z_`z*Ekq>Dp$g4NIy2fMoobaY@AAld2+{Mv;^PlwmJA2%5#K`3>I!?(x{Txo!9?bKj^{p;{O5yHsU*x;{i-<n@xty8ww|SBOL%(lz`M*nO4EF=m;EQ{A?Zr5QdYr*2?l@xnQN1smEc)e#^}1L?6R=*l!MA6=_NwN=mhNvS(?8}%{G@|=UwHbveeq3%{$5|dOX7UHM6YA82mR~5!#;XxIp(38dpzQ7CHBSY;n+8e2cgb%o~q|LFbTfNH~Td5EjS#$$v0<OKb>#B{_stm5nrIrINjlg>dcd<Gd|;UKiUN^Bj2uqAKH(%{D9}ZcpH4yAF&Db$9E2XsQ&yK^~X5{KU9CtqyG5*NZ;(cn%DHcvo<i!%FVidS|2Ub^WgFHXmjP;(%yQUc6<6}-S=L=JpUBi=E{>)<ca-#tgFA>b_99yajYx871_}0@|n-Z_tn4;<%ys9P{saceGekvL<#$wd>Dd!u(Ihhe?$}VFgU{<U%Y`lbW+^??NS@-+vSq)U09{(UyQy|`=$<yVW`8NNcf@pzl-(%!WCGD_r1Hc|N2XMy*yvRw^ucy{tu|bIdYW!S%)n@>TvJ{_@Vk)#QIqY-<+pnE6!7A6?}7^+Qm3etvL9hbFdKSpx9G~bu;xd5A{>j!uNf468UhZs#%YJwcB@&ZA2Yj$vCX5P8{m0D0auUd$F#j!4K8X&%L^Sii@@IO}*`XyUt_JY51YKx*2)s`>56x$ExSK&~{0j*fO2}zIWi8{IPN}nz3JMUE{Z-a9&tH^n#y$5%n|r6xL-%PrNV8+>ZQ@zgo|m=j&@Qulvs;e<sh?c^lXY-|QFX9QIf6$I7Fw@o&XE1pW*^G@etK&)^pLW*$Tq>vkFA@OiDbalZKOXB^JI)%q9YLk4`aj&>^6*Z9`<m>uDM@MidC-o*8p+IN~ywuaAxD2~+M8?1)!+b}_o#|c*RT!U{%o<}{LzZ!Ko9e!{{KH}R4^gQ@R!*|xC9MJywT8#V4AkMMf4XE4M^HAqcz<2hxM_n!3hdS8^-)`Eh-><9_Cv|)$8ui1o?;Gs9mm4uo0pH$x9_zB_9<1+Mk0Y<wwxO=RF%|Kf;5*fAdcQkaBk|tS2;cL`YUJCg8_|Cv<2cE9|2*&^&eIh77bl@EH8f&hcYyEfJs<r)ZNxm>{aCAOU$jR)SR>$@d~lW^AM7)wt>NqFywCh^h9BCe%UB0?!w>D#AF}kkSv%o}^5-Y!5B*U7&<}28eDgkbC-T`k_6N+9ssE*@|ITjuW}lAWdemIf|1j#gRYc#^|8myzB=~0ESr200g?zpj8DHE2-<)^i0^Z+5XZGj0<}~qr%=kRlj2}4kF?{pB<j46HEdQXzmCq-)==h$c@XdY^i`V0MXTcBcmrfNrj-3qO>=(P|L9ELV_@RAqK3})R*%K|{`ETbT|3wRYvtR5!ujB8s=i!IyTNC!RZ^a`m;rZ!QFhB2xZ}L;Ti~JO0*`IkXUi=92FbcleU-oG1FDIJ)xxYjf_Lul^QHyJTeR2o<3-HbUwKI2Ozn!IT_FW0~UEsa8=J0j2d*MAK<eT?x`c@VEP`;HTKdmR&->mQZSYIcf{Y~DcGjAte66ZbSt({1pdF!la-ky7>IXrL00_LspnYYHbzJedhTh;;Jq)P0+51xbHGX`~Ld?ok&fgOmq0{b}yzDOH@{7JnQ=S33yz|pB#udgwFUjqAYuYi9Je{VV$EAU*ShU0xH?+DiYJ@`&yxn4)xKLX#o6TWZmw|HLfw$?*l*RLL_-U;uH=_G_gw1^S8*<n9<C{uk5|NEaj@{<0mpF9#02mil6d90RWsFZkALh1EvD}E~Mn&KQn=?5j2N|Z>{5hc8*gx8-US5mK#SjhX9QkRhPsq=Y{(zDoJMC5af`MhT}v5@0^mb`+zkosA2fc!Z13%vF`IY2#IqCnz)^4u`3uB|0MLR~MhN#bcj=^B+Y5*6(C2=!WW4RsCsE4^IeVaBVc-b5~-E?{4!S4sGJ-*W1Q$#bda@}7tJ40Aayo4SJRr>>x`;j`56dur$_eIM6v75gZzBQK@i#%nvsb<{qInG$8><<t%2dh&AW?GihAy&=q7DN!h~g;08f#A6ccBytI*^T->hH?V&m@7)j<U+HRzQi(N;_Zam$ay4}|`>*4@)f{^n^#bx5>IKyEB(lk+<Tcb~?6;Cwz_Bi1zd~Xj$Dd2iCY#ucC8{Kr5K2Eu-c0=@^+t(W@>cR@>Lu*=0HO4J@<!_U)I}2I<XW<cJ%iVtka&h%OD?B=j@KH=wbWZVo@Ip6#pEjLV(Nz^=8zYYtEiW;UpZ0CF&4955%Cb8=>hT_vWfjmiQy8{$hT16B{5E7JoQ+%mA2Tvi`Q=^3+kIBu9CQc+=)6~B2A(%?^S(AlCP&8NqsxHFLhtutMnBT-6c8_J?JU!Eir^ViF&HUFt&%$Q#wK-ma!DKr&fM{i7av|wc^Y$oxyf0$Ckkuy(ALI_fSue7|ixydiSu8y5|~lEOjjVO(2YyML&WZOP$G>S>(ag-5EENoIvg29Q7bN(i_J4>PYrbXYyKia!2Y6&Sxfh7`0iC4Dt}_cwS2*XHds8-WAjlY{zpARC}PrXo-HDbLHPj{yFuX)Fa6KsQd9=rK2S}OLQQ*(z}(q4>5(F;)xQ;gz=&zx-gdFpHVA+kc5}~3u-U*7;<`;9?iCj(Nkh5c{=rEi6pj@=uKxIb<cI=F4SGvZ!%##Fa0QT7wR#L=_MyocV^r%<e}7kI9Jz_J5VQct~!vfr5?j;oyi@j(>b4G$jQ{vjGIorm3knrjV7m44`jS(>L|7cat)$5&q|LX51<}JeFr&?`VQ(8@{QD2N<>PuBgarHzFOio^1ak|OC++LNKa|?pTf%-Pw{2c-f<D_V%q<we?9)|W2;T!`bXrYce-ES!|(h~#tOa6d&fnowUrOiPQP3&QmZEZ392Sf-v'

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
