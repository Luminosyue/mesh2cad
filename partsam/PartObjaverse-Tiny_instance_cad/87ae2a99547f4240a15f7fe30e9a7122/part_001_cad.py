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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/87ae2a99547f4240a15f7fe30e9a7122/part_001.stl', 'relative_path': '87ae2a99547f4240a15f7fe30e9a7122/part_001.stl', 'source_sha256': '0080c686913f4cfa57b50ac128dc5073d47b898d3641e5fb8b3cf7dd4ea4f1a3', 'input_faces': 224, 'input_vertices': 164, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.05568018555641174, -0.44692492485046387, 0.15823853015899658], [0.03948066383600235, -0.3049302101135254, 0.37243175506591797]]}
GEOMETRY_BASE85 = 'c$}qK33!cH8vc_=>_nx+eq%4OlprJ~mnb2ksiKyOn?@qBrh+1tD<nefiAW;kHny=&OGif;eznw6ghWCaZd*&OGfI`T=zqTV)%ndc^E~s+<ay5XzUTeE^PTT}XSvrE9_m)cOT(X!mVdccu(PVBsa8qz(xyaDoD>%oozQxG{4^KMQ*`zB64Uz)3=1FPqD|2fn~jW4h?>}}i=|m$jDIs<OS6~>6DLiK96w^h#F5cT?-@BZA==OrVk6_DjehetJNo%r+P~pznQ8eS|0<{)>LqPEpwKV$qC$(?dnG{zT2IA`ZoM8Ly3OxGvC=iY1N?g(x*&SVSn<~)nm}*7TXa3^2l)SbWUJ__*GL?#BvAbI=^I3M_H85nj!Lr-r!-G=t9vWaokyNZ9DVy>=zBj#o{r0i@2rD3`!|$GoXVx5+b35SUGJVPx^??Z#6N#{v-mqZNgRFLG{pIHp6L35#nAniLXTewJvmBr`-CmXzoSib`wgtu(j!^?t&ZWMTdVEIdgqT9e|v%t^adBi-`eId>fGtOKZ;+uj#zKMOsx0OLecfoK-6>kdF0<ePISwfJy=)URmk&EE72WKi?CnSHTd`Z`zG=4wMP7HtBa72$2HNNJ@U`XxW2`x+u6CIJ2vkW-R}F5=(chDH%cC(w@7^FgB+~)ScK@d>wB@@bnK%wp`z%{{@+O)o2{+*JADc^NdImK{F6|Bz5SXEsMm+0JFcV7)~ue;KS@KLxvr>xVxZ`H^{;S#a#{ab&(}-deSZ+$o`E`RIbVvd>qjx~*S^rZAAo<Yp4i9FSpUKp(Y5AbqHA|q|5b0nf5&mDr=E)XTj%)0zi2DY&!Ym=vvpa_TXO~K&}Rkwo19!HaRzUfIQB}2Z#nHDy7j<C@z;m?BcJCF^QE4P;w8TIlTg$l`KsuecLdfIcM9{a9FcF{UyJYS*!Mx5;a~L@&Rb9<^heF1-@SzM>GC(s8@T0T_zyxI;wEBW9<LMK_SL(n|LgZL?<gP9^_{0=UCt@cwP)V&?|%^Mt${dt#&L)Fyg5%CLLArm4)ghO22DUd7xt`{I9|UX{`FwQZ}=DJ_ZQ;6JVD(o5ub@}Jysj_(dwc84Z4c1ms^MZa=bV%^PVZr691FWN^nlT65TneP;|$E*?9N*{T2Q-&%(dAJMKl@e9^T=heX%AJwcuk2avzd0r<OQ;(P{uhJ2Rp72V#lE%vt`&Xpx;D(1bCihHqdA>wa}65aA(5AxqV33a>gE4uC0L)@44=fq#XUjy+Qxqc(|8@ENb#oo!3IOFRSi@r8dbjzwsqU+8(I6qf#e;o^pMYpcIg7+|a1>!F}f;g2tB))d0H}ZMxxm@%co)TYc8ijg(QBidJ=I2r$%f&3z^T+bgzdnb3zkLk4t(@r2QHiMAuqDX<vAgJ6`DZwvu?dJj!&P+sfgSsDaya5lez8pSf?|oUwXh=31HX#yJbMfE+%X+-Jbx73a<8GR%NhJV>hs{f=$hxxcnAFM;hp^THsasP#yu+e7W=;Krs&q&wIq(iV<`503iOwsN6t-$kx$}v_zyn}eODghKOL1~-Y+c&d1~WBQ_TBiztINs?h6uK^W%PPT#mX8Yyf?YJI+H%2<BaJZ0;-P$L*~6J67b1ZqIUo|L$9&TPIW$-SIBYr)Aj!)OpXhNz#wO`Lr%fKt7w}Mb|&V{jz2rMLidd5#1h+`{jJG7xB-=h;H3q2A^xE9muCk&m`P;)ZborKk9QPNOWz*O5D?HJF%{V0ho7Q8`Sf~O1vA(Kb<b|d*)-`?>s~PvplAWzM&L(R_%^By&g}MxKVg#wAP&v$N#42x;x$(TZcN(=k*Ad`FyY9J)hYF`_;MGV5x^*gmZZFR*~q(5@Y4u`CY`kJcn9xaGdBP_lUps#}w#0ED2JNpO51EPkyPyu{yemZjDL2EV?t~sQA}dBD%9m9P)3&dvWpjWXUI^$0f;gfhYW%`cDlq<?jgIBJu6dKc6P?3qtVT*1L-QGYh7Ry}}cGE+n)@o}>K}#lLAb?)8Ai&_|q_E%<#QzMpKoj`yTbfF1YX6wX81PONLx{5gVy@Ofc5xE1*yzcg3sFl7SveJswEc5U1|!7(|g!@<RerJvR^MdDP8l=W(FbQ9e=Gd0CrXWe-M>-xt=(H%9mU|;TSFT(xWIbY82Z4bQ9PgWwIYp$uHch#Y1Uq;<_?OP!8q&LDlwmu#4mz0REm0yefy*di#KkaFn#0lPp`}=tk=3V#GBJppLkMAvEvCy{`Eiu<ePp^hJ$=8-j{-yiy-kx>CeMw!sOziJnz`fYv4gY7QqB|{n3nk8_MC3W+&~lll_H=xnhV>TRdG4|3mV#k;_nKV8`}sltbXoUn>G(YL{#yKPJ1>gv7_+Mo`(7Zr<;gA4wM{?a{IuVN_iA(R4Dm0{6@RUuE#}ReD!TQ|DZDe8yP)^F3IDrQaUO<$iumgvuax+4Un2j2Amll8R;J*yJiI4<pW~ewlP0=$a~al^nvDEUEMFz@P9)*oXc#TJqqSF-=nwyd_qlI3=-oPs?$8&b{+^vMukR?)wRC*{*S6tv(01=k)+_ZNRu=DM(K+~+&K2G1w*c|A)NC17ClmE)?t(gOd?31gKn>i}oZ48|L7yCncV!3OE0<por*SXQ?E_CBpPyne?<KF*vhP!N%ew5(GvGgGhv<%zpNeiNcvy%!e**nz9_m*49`f=30&!Z*z`gi(E9zNNxW>G{_S4^BzjAu4Mg3Ax2hRZbCx4kIb$G{td@7vA`!KbyL-MbE5c+F4pZ4-L(H*O^ig6#0NS<2Qc89rcmfS_SM~{;8CEt^4v5(d~=no4;*DX1SQ}1~p&R@s%66a|uzDEW1FA55O<=25b**Au26%A^%@|u?x6KVQsKn$ApJO2Bh2IBnwtDgqiwfnz+8klF~u)t^^5vQB@BK8%|B+oEfHtpH8DL&h1bB&fpTt=QozLc0@;+gDcGFAr1rqG^3o8mD>8*Q|BVgh+Q`E24`6Q9cdRK}XivEykUPg?@ltkxGx97i5Y9zz^$;vcgAA!Ci^*qOA?q)qV=MjK+ZD58x#iu`@zU=x3jeT4(a)!2cw52Q`;0Hbv^S~&3?@^JDI#33gBHv4Zg))0;jrahQ8#r=&IXf!`!2Xa610Ag1Y4`M%vvAS|>ciOwt)`4qQ>kA?FCJ!O^CkC2$DEpy|709szXdghE;=_#=VYEo%2jr3DLy5yoJc|7&<~NLEN6<ckHpM#|t&7pZi2caJ$cGanOgx<ZaK?(@*Z|rCXj8nS(K;Ee9kD%mJMzxNE++2Bz8_<C;aGp#{b_5@HLLZ#MeIfX7I{ZvCle20KZLP5aqRoFzfYUu^^I1?Xf24%$Xk%NBsMqk2J9<rM6Skq)9y{1;;tJ0_=~GniM%R#ePSIGufl#6#;U`yWoR!$o8py?rhZ3tBf5~gaPF5}V_)&I?3ZOMjbkg)UXeBzu34?G9<ergJ@U%L3MO8Y{hEwbfnyud-iS8En`r8z$@pgg(U-gpd23=T@)qR2<Sp6vVf}oGEy&9o&E05T#A@VT<V}b^<W<S5k=JM6o%O3mtV;fx(Tq<|tsK#Vyc~IXqC2@8xd*u``<|?y2hokZHP_dWXd$<7?w8z?eGB)-lUSL&6>DW7)+1kHv@D~oBCaK0MZSjkv5DuiuW%i?8k<LZ9&L)J8*RSPa)~R*bIBdV)h3?IzQX0?YU~`^=g_8jlF=3$Z3Z!wd<OY6qTR$-vafI<xf+{8dk$@i&obH+qa_k2kSCH)B#tuiX!aG3Bv)g{(ms|p#noql`m78k_9YJ`?@kOd@weGm7)-9l4y1h`ZHm8Zv_VGeL+nZ3hrAo{4<_D&eT7zXHMT$P{b^HN-DUOG)g)FYuSs5!Sk}a=u&=NTxf<(DyEko$zhShtMypF~OkS7#bz%(@Z_2*HTI6c%o3y`4o8n`P7H71{#7X4gp)RgoZvW}O*8cftm&euoA8r3S^3|{1=8^S{i~0MP@bFM~b>EE#!BxJT4Ut#>H`(lIC;'

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
