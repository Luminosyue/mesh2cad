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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/062c791e78a643f7bd380c336f809389/part_003.stl', 'relative_path': '062c791e78a643f7bd380c336f809389/part_003.stl', 'source_sha256': 'ecbd59618739959d4391407e20f66f32484a165ddeb3f99719ecfc421fee50d7', 'input_faces': 288, 'input_vertices': 215, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.3362312614917755, -0.40759605169296265, -0.31208887696266174], [0.44813835620880127, 0.37031689286231995, 0.3414250910282135]]}
GEOMETRY_BASE85 = 'c$}qL32+rv7H#%TNPw^@YQunGmmP-ff7t{B7zAXIr4vY40t6BQ1_YXQMnD0<fiMcqzJ^@_0qLI*NLaIw1$2;aA;Qd9j5viOV#)M<eO~+e(Ni@wld4na{Bv)=e((0}?)N`LMwBTVrr3WCl>Q-^|J-AJBs`~tDYIh|W=$R+lh|tdjO0>EDD&x$^SVL921br7rOa05g-?h{9G?*0MGfy3+c~_28Xg;;Fe@Qy`ndRn2{GjNjhdPmWBG}bqGrTcpPRI8)1ighu4xN(zWP7@Rko&}<}EGqS*)$ym}e3{?3LmZ{9yI!%-3T+-fnvNNi$A}`Fe-)SIH0Fzk1U2@B>AsGR1uV#2Pu|8*6T6nqK~@W*5bL?eNwNHcs;8Y}3Qnlj>h{&8M0FILn)K?~>`^``dn!C*~XH7q1~-nfT*n)5DkR!+rmbM)|JuK6$j;=XGBA@_B>peogmztc&~dy8I^|p7VLtjr&sF)Gc>%d>+?@`|@=$K6rZB=W*Q~U%Kwbs%lq#Vtt;Z+2e1nTFm^=&(513zPh#Q6*1rFbF74Yj&7b|dia4KmSnSa_)3@`s9O6AQ^=QnIbZK|r-bF7D}BNA@Qoqwu=!{|ZDaEb^jujijxYOseC^f_d!3_h7mD+jeV(s&&$P!W|5c%@ui)!OYumpUf57zezq^?(<_C{-C}8uMd>~+Y_)5gn3u3-<@TF@k?}s}%riZUTXrC+Q8;$R=>lfJFI@k2@wXBQ+F<;xd*Y2|p>+?-7|Ja#A*Z8=Pf_wZ0riZW9n^Gj^tG-ExeIDaGzBInJIxEBHF@NsM^Ec}JV&6YfeYh{zM~`j9?q|9F+<&J2{Zw{7`T9D(bbYncR|>@YOIsaezJF=7-G|GTv3{0)<H>FN{(A6tyFMfK+I?8DJ<FGUW5I_k-)Qu+yFYtHr-;7Ohi5f5f7uV}U#E-tybtv)djh71@2^!RTg>Nu7z_{Qm>#}<vU9GO@AToV7P+Q}Z|pr+Am;NvR3bmhH$8l9<Jm&j_~^sHxgG_khj08ES0v{1K9tAjzC6CuhtmAHFVCO%p<ExQKc)KcK9uXv{b%aW`%t>R+?TJf)1T-QweYEDow+a9CwOx{d%hcGH`&kc5z8~Yd?n=@`*{vuOS|Wp&wZY+UfX8-$J^g9g?#QC-wtt&Bm43=Mp4UR&wThi-`JJLe5JwO>#Poseq!%;+2`+tXY%8QToZkD<4Jb?l!kTk#c_g#=hE4IwDjzC(br!&f0X4n`K!xUMrSZTu&_;mD}P${Hg>*VkKN-0?lNB;Il`5%o((<9&i`PCD?iw$)+tt>eZB1K+wG2>-#yAzf7y4gFZ|$`aQF3<d^ukmJF3_#pZm^r`A6#;?6?zCT=S8AIbZ$eMb~^}|C#(7<BL7>;XCs$nalh@|3U8hNWPq}4({TvkL1hw!6~m7d*ySV=WCA+GGAX&(={L2m-CI#B-eao|C#*#&lP*-!*}kx9|O!+KF=<3-M^AA=c``@-1oKQJM+0+|0c`3`!BXGzCV<GXMfmpG4uUh$KGW5e7`68&i*iNE%UWzi(UI++2{M=;D-Cm4=%iK`+R>Z`Of|}qtX{_oO++y^}&8X_W6Fmm^GaF>eSA5eXt*peZC*iO3v8hy!Ca7YrT^1>~D8g{L<$4ip2TLzBB*0yUf=o-Lm(qw`19RP4@M8lRXau@xH&X>vtuI?Kk`bQta=AlCRu)$i~+P9Atjr`-mboZ@j0t?+<LU_cP(WQ%w&)*nY@qF<<G}ls)hCL)+K6#!pypKOf((ond<T`qLS%`KXUqFkf4pvETIY^}>T`Vtz0+-TvNvMl($hUwI=X%eAgnC)s|<_~pSR)58y3*q$fmYjuyX@4dm;MLDL2uTPtFRm?X+hOxfUdw-W}dichahSyzn+t@OT^+AQ7ub3WwVEOm1`N;1(Xa1=J&oV#y=`~j!r1zjR|6wnjV&^^Cq(~fJ@A~Blw%+_efy<ZPo6bC?_og$?@=cDg@ejS1=c)tWAEq8C@bvHBbj`<jxv%|uLdxIV<G>GA8|SL0@vxo2`0{2~zWg3{eCa*z)bs5bsXmW7s7;IQ?^9CU<oCW)pM7=M?*hTcgIxU}?*|+|q<+BX(GT30`$0=?%YLVj`;Gf@zxmf}vERq9M!EW#`)bF2u6|bMZ@9$HU+bdle&K%L{94z1^y}m8<E8tN`||y$bXd%em+yD(%lEtT{8Hx2&lB#;&l4p<Wxqo`^IV#^!rq@t&o}PN&o^Ud7gk61oQ!n+%9+r2XtGkxk`^i{VM=V2@DnEsD2l`0KXFcO|KI(@*}3!o`xEClYYy=iW>}aFjt7$9y$4PL=D}MGo(C*~_eby|;1BQ?T3BWw86ceqkd6jOj{!)(1CZ7L(lY_la{$uw0n$sr??bPEUJhOcy&PHxFNA*A!UAd=fOHf<dNe?KEI@iZKzbHHdM>a4<Ll6T4ht|x;-%0!<}(+ZER2(kv6E3pey&8EKM^(M^NGeBqfuWz=P_8v7}R<+);L<Izb33*Lp?NH174q*sM$<hk9UDNSkoL_8@|2;!u47rta&LuFTr&p@1lkC7A}Lcq0d?P+(H)EguZ4W&q4vX2>LS%XDl2Cr$cYEu*<?0@K)&aI7c=(3;Mc+TnokELg;{n3l=iKInaA79I&thybpT6h20kRg11A{T25m<#HXOIq89n!%g~pw<}2U==)+j^LGW>C8uKK^B~F9hiCP%oEzp#66nSaTN5F@miBqBTP@^JnG4vVKC>@*uy$dzk3f=*I2sKIt?}g4qEegT;&=*jP9PkzB1E|G5@ImO^So3zU0bNC*f2LCSvz+NrfOHLjbQnOoHbA;AK)Mb<x)wmXCP2D6Ksp2<T@@f*86aH|AYC3HT^1l+8X(R8NS6XgmjOtZ14vf@NLK<^fo^M|HEPouKI!&|g@UU=cSNiPI25`wVqxGK&|MI#4Gx3uhFD#2ZRoCu)dAOq{yk!~z;&QIAyyMy3%Ubh)xkBP+aVSLt`6M>v8vz@=vNV|46X{@60wTl%FxXbD-W&+-4wC1;PTMnh?NGHg>H<P0xk{x3Sy<e3Um|1%79BjH$$u(xD0d)#43QxLAOGz61W0%Ys9L6D?w9l3__fE05tj3ACbTy!K40o3y6eAy)hKAp@?;aPyO*WFccp3#t6hlAV!*cV>sf&5$gt@`ePU{T=1wrh5*ChQEv=JY%pS-;8TCR2@DoI>W_iIn}SFE5djPoJnE1BK!o5?f4mO#hey592eCegHHT0A(F^DUk9y-Z#9l*;H1$SL#Csyv7(Vq!Z=feU>W#jL^+l`+eCm&WKwrV5{&)lE2akGU0Ad3WBOPbqtc9sy6MC|RNfxGnCkpx)J`*2-reia4JaLwwr{Od4bV0}Aa~#e&9eyUfOpF_c`JBM{PvG2KQ!EWU1^O6bN5E;&({Zj*$fdcDwD6&YjTTmc*F&#@R>3`>Rp^(%4WVDQ(A~mH@H*&~&>w&|K)<Na*B$$~1~`WF^A`LT)`0&6y$1Rt@FwW`78>EWMmUD_S_>%_R)ar=UJYFj?1Qcc{Q~%R(6qi7)P{I7^hW6Q;7_2}L-zp3Lid1f2#$fKbx%NTi2n?|4tfLlQ|JxQRI|v4Ql-Pn{HOmS^V^?J4`tVXn30ckf9({H{MJfxzJx|bl%w~D^-?I!Ht7whO3J?h#4>;#'

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
