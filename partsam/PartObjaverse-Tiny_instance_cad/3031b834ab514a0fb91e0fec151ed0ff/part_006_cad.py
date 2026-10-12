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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3031b834ab514a0fb91e0fec151ed0ff/part_006.stl', 'relative_path': '3031b834ab514a0fb91e0fec151ed0ff/part_006.stl', 'source_sha256': 'c15326be70c61bcfd0cca818d0132a3a2266391b7ff56acf348dfca0efc1346c', 'input_faces': 224, 'input_vertices': 160, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18907231092453003, -0.019752711057662964, -0.18694889545440674], [0.19847430288791656, 0.49715089797973633, 0.2540122866630554]]}
GEOMETRY_BASE85 = 'c$}qK2UJy87Jb-auUHBAB`RppDE2~l7El8yw%AZUQdCqx#9nw96=NX^Sc&+JEv8to#At+PFR_o<HD6;anK+qDx;ioM?z1(Ytjt=oW?1X4z2Cm)o_FrK=idANB0Qvc33pBY>S-13Ovy1SX_{)~HFs@dY;ww|=-Ba16OyL5X_cX?zvr0Mvwv9lAUAEIHq9p{c6@ZQPkWnB$GEmWem0-D#N?FZsD#MG<d|5c2S<$=A8YC3M@A*ZTF<`CTQ~EwwP@sLn_>GO|H`UR=Cn9opklfDs4&n1`>4wY0x_E^&`t0B%j(%NGu2dRj4gf?dicYuurJ=?5cCfJI-+#r>^EW`{OK|H$@heAh7P}`p7jAMMZX<+2=*y;uS2ipc?5pGUw06CkNu*5bwljks~kX_3ES~r+vt9$V1K=s3IC}hZsPes_F>p}T$&F*)6T$;=^g-k?dZ1s&?gjJfxUm>N$B(2?tz~HA-6Cu`yTPr;LvW^AIXJ(bLwreKi^~*>~9>$yo@om&Om>2%}&_Y^MdYt>+)IXbIax-{^-OT@H0LAG{%jpx*hi4dO<fbUiutZcGWiM^L(H?R!lhoKkE;FtaRPB7;!omkCu4GtPuTigD;S`p~(_|<sF+5=lFLqU$gl}yjOE;z8?Pdh48Ou2TPn0g{u&!f4k+#bDxb^C#|#RQsClAc(2*^0^-!RoXv#pn*w{Ier42$HaUC=(0w-YV5{LK`6;n31NzLF%i!lVZ>+Z#T51t+_vkF(ZyUtV&QBHsE4I%@yk4_WPuiH%^MK!!hHl!k4&!-6elniZgRt(}<GFjG|B@(rYJcd4#~#s*rD4z?^p-r=T_W?+esF``{L?bumv2d&+QnYbw~oId^>k43PhIPC{tH=;NYt}cU=hGlU63E`yGO_1$8lEl=kcGIaj1y?{zl}%n0T(JJ@aOG)RFz*SU(QW=@TTLk88*}{_;Z_*7f#c>=*O1PUoQab6;HKz0dPDu}o&*U*-95vrN}`UaZT@&oW)(d9jX9w`SqJT};^*JwMzBJ)>PV^hT$ln~66>?>S?cYkpqTk5*>|>^#<Ey=?s&%e=Y{TM0i?3USV8!F5@;89Bgi7j~h)T?+QOR-$_@^j1I1`Ov~w&Vk3XME`T0SDm*3?>!JBb?eby_RIAx8-Wj7$T@I7M(U(dqxXScepq+=g#$PzwUEKkjV1B0w>JnB|LM8gWZ!>|c{!u1$bN5{2VEQTPdOiahT_~a?$y|i=llXW593D4Ik0tz=p|R*Dze|JyuKUwAQATVIxUaGPht>sBi`$#%qv>X+wSqu&6ny*oGbc^uAPOhhsu2Q)(yq~weQ7$jmFR&PwI=l+Vc~PyY36!8QD$rvrR?c^n=vr-@A(5v^8|StmtO5>7tLGA^Nb^5>KxY(5?GG{6s#GbF!Tq@?cc!|0&QrQtpLSTO^<3BA}ZUhf4folW<RIwUfktK}F=vR&}i0Ygvm#KN>D|vL;RJ$L5Kj=-#sK#xl{}+w6tkP6-m{zU6Wc?%M}ld!orbIPRdF^L20Sb)A<{@8g58`~JS@mzznPwf93e8oTeq`#xwd`ue?MUwuAwBW1AM*8yQTSB(wtiM}VOsQ-?a#81G`3$pJM5RZOk>1WVS{3vyma0q$U`|g0Q6@(uJo=-n1aX%Ej`em_i{z%s4N~!%t?2E62y_s64i0*heK+eg4Mn!b}{w%Q{7`UJ7Ec;?`#UoPR2}SIkn?I6xrY1o*H{HQLb=*oozj1tdQUCj+PX3i{Up80balTmqObC{9zO)<moql$r=#%%z{g^XJzKhlw(9OJ0rJjo=ivC8n=surGeSY~Cbn~k_(Dle?$iE}2Q0~EX---Y5y<%T09`=qszH)y2`lQg+-j*hH`uu#bFRYDcb7U&U8MdY3|J9$c-yPMrK-Y&vN&VPwK-Vkei$2@)nyY_(<5AHA3gz5*5CZ>>r#EFD+uW{5{=O9d11qDx%*=b2V1H?*<lC=~=zUH?*Qb00d;4`y(eHhTed>(Zi99<twvjr0<+UrWejH&TVt?cq@?f5tA@P@<BYKn1<(}QK3H#2R*Hrf9`<{hG{PfI~{;5snd&!ZB`PhaZhOXazb{=+a+fmQ<C#S^EvrzdSSQWhk`R#I5_V=+RvhIgh=ga<|Am`Ry$KT*L>W<tO=^u%{Hx;_(UJc_N4}O(>Hty;*+5fw7ub2nCQ180$Rh%2n{2b)pSt(fdL4WV7Mf5G#M9({ib=T+C#JQ*cd{6YJ!!R%7aY@v@-Q$sbkEF%Hk3KyS_ntlMH_<(Ev0lzzHpK7zuA}UyfXbI#->dl#5`C8g`7{QU#kx4}O_Ke8<|o|8j)LECUfaLP6n*B?i?Cb!m8`c<Hgxl0X?&NMI|jhs@p!e=(T9~pKaqs{#@YD;d2iN_@NZshCHK>U-QvI8Y3TYFk8%Gyj(j4z<Dks9TRp6!?tfDB)>|Y$_x*6bJGVBGeZMOhaoYN(;k<MHyPxR2??^mH>dU>mex&>^DN`W7Yc||P{v8=(<=zfGjXHEb>5lx^vgbiJzaE13YL#Z^0k`Ff|1t5f*UoiGfPMaE(bLvS{p5T*wLs|u^2Gn<Mew7qJ--uv4;_|x<~PJX(qndQM*jC*6hBY%u#SdDr3}Pb{I=LfbVvOdoi3+KJ!-Pgz7B^UN6j)=7uza#(W~v0-&0AaQ2+MwokcI>CBFxE#7ce6jg;?>h?|#O<IyY46Z>cB5>K8t*2~<mPwdCJ7rNSOsZQvopBL7}cyt^2cRuix`+vw}$<ML(HX+W`-tv9K?-S>>LhLtN&Iqw@{}1^dUR&l^V0e*V?|FBl&S>RSDOsy({d$j!a{1|w4o!Q3fBn;aRLlSBr@Oy@%m4SMdqq`3R(pw9hP=4dN-$J~ZrUGzikBr;ATLYqPOMGtueONQ8WEe5yVJ&>*qYqeYAvl+omi7xjcddHHth3dUrolYu&T>E$}@I_rN}GMrVOz>c?sIM5sQ(#kyjvACa*wVn`m>HM|;NGp0PG(pN;)C_O<3b0vNl(SIE`44(#v1zUTRPg|REF<}#0Rj9p=A@~X5cPb}w>kJ6lz!jdlYtHKx+db`Bik#TioOl{cb&3<q8DV}b%cdRy-m`Og*Y75!FkbR2JvD$pAy+xc!K9^(X5a*MtajU5*e3xALT+05X?0bjf7SON4Ddd?PJD<3KT#d`2rf?Ox^0|clOW3!X<I?C?;dt_QId%atja-deNloE0a^-U|`xmn>hvTNvufnn9t2j1|IE`G5%c7?6ZF1!^oBi4BTgh?L=~rPA`7(~3Mx0Kr#!aQBa3Z<#naciD_GNM0X!=z+l>BXuolYE0uIfwGQXuhl^4B>wkWF!&*q>Y{?@Am%-hpER*c9(%wJuicOq;IcI<XUZC)(>AtDf7kDc-|sp;il_zb@pRi9N`B&|dLjR-0h8Na76gfmVyL+MC3F<dL+AAWkNaARkDKAy+<U(^g>yx$2LjUxj_hXV7Lc(IB5p9z%>HS3XzJR^b|Q)gMp43VV`g(8eGxA~(q6i1Fmg=W^OA%q3U-qv%&*ck(r~Swx&gzKA@YIEq~PoJ3oNDdei(PQMDfk>}E87BQK87WpWmo%{`}^|IOsHpPb%!^ww}M-h9IN0CPp`;teK#}ZS>Q#c33RlN_<q?Q#1k#`{m6NAX@#BRhOa#eGxE(WnFK9bmnd?fieVo&mM<O#&?<O$?sh~3D?kS7v@$b&cs#noQx!Mwgf-isJQ-ith(7)l;a-kTUk-kZEHF_}D>Iql251#?^|d6-M?!idS_k<8aH^1*x_$ea!)4kE8-wYpYo$ENseL@#oMP01Tut%=nd5PisBwOT9ow_=~-4Xsw+YJS9K<bLF@5?hgbTCI-NUMAKcZ@_nX66=tASgjV{Q;Y9t$T2n8UxR%fjH?BGgon5lb1(j%{`K|8pMeih*MEfld1TSgZr73dmai8d;o%`A)whrJu~Q61`m36S_B)K%vO@'

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
