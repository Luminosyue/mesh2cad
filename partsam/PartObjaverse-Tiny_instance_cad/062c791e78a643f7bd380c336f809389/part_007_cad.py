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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/062c791e78a643f7bd380c336f809389/part_007.stl', 'relative_path': '062c791e78a643f7bd380c336f809389/part_007.stl', 'source_sha256': '5beb07005892b5a272b2e08943b0cd4ce7284b90a27ef253e4077e40fc2206ca', 'input_faces': 361, 'input_vertices': 193, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.3584287762641907, -0.2401416152715683, -0.31234318017959595], [0.4412546753883362, -0.1587906926870346, -0.2303871363401413]]}
GEOMETRY_BASE85 = 'c$}r033OG(8OJ9O$`UoKkwxTTq+to0L5LFI0g{3t5)3;C4@iO$2pBMkY!6ffWEGTMAIQEHEJRj$bypgBFDVL2+ove@l%m+W9;BylW`2|0JErIKv^nQH|KI$X`@Ol}%$>U&vNEd1)))G(x%k_~PQ~l$3L)brQC}407EaF}pF6Ex!PJ>CqPFtopV8G149?6N9wUmxtfZXWY2yo%?)4<4<)tPidy?{|6izQ3TQFuyVNR~})5lJlmK*h_Jv?@5ZnWL9<2@<Ko|IO}o;jZX@vl~N2;O<uKI{=yf8@^hPe(QQr`@He9lodGtoLNwlaru)|AHIJ_l=7?quMJcxctZ{pUM+S_+!}RZ|tG+L|Xsd)!$$C{JXO4J2XuDR}(*yzBqMR<qw`pa{0k;)08jnTN8Hrk*ecWp5To(Wv>2RkG-SXU#wMm#FOKc@4bHL53(JYdo}FzMM@3j`|^gn{NP(_Ri0p4UYXPP-?;j=s?QsxdYtbT>-<x5N>rZO$HPwFv+KCZ@A<KX%NNTpt2|=w`ZA~QU({9kzK*|AzUQ6KbpLh<x^5jl4XJVEUizrA`4ZEw==!X>MbGcnD`BVafALF|C$iA%>L1v-Tl)pYAy@yy3sfCE*>Nh5r(5iK^}81~s{Gzlue*Hlb!Rmm-{NH<SO1|S^!O*`m%92-{!X25Ahnaq6WP{O`GI}kt9k~mu5kJO&-?2-pSvD%`2z>3Ji(GT%ACIFzxyrqdxJXYd3-8a`QD$Js&y5)wkhoNJ@LnMJx@&tx%ziGuh&EBic+T^j4xEb8;KpE@&qQ0)4!XQtn2?pddTJ9By|5LW~u(ZxbfP*u|i*8jb^)i@Ao<CcO&r!b=~I9IA7U%FuuRAk6xc2ZTdjzwAuQ+&KIfv;(@n9PCuA_Smh7Yz2Wlxx9w1Q{B?8Pd7izb>M1Uq(|)^UdcLZk)8nbNC*<_~gNCa7-XRUcPT$)<R{PJkbL9!HTd4CV#+_C9e5-Z;6XR9CK=#zI(+?gws@6l~!o`r&kM#Od<%vwVROZUlElsb7uLkJ#aD1B{fAUv)J)HA}UH-f!Y92jX+k~9Hh^?XPmVKtw>H9Bk(ZAd51%19{JC*NS(ps;po~uGmUz{DT=l92-OI-ce2<7{lb#&zko^P-6`;Mfk`UKuMqvs{DNatTQE9CS86SnL8>%t{YKY0DH-e=CHhn>Fge*UKN8$7J@KX^_1t5eiI7L3UZyZp;%_5NRSYsl$)eZSY&W71zrUHywjsqqJ%+oSU&{-DR-_^`fTtjiBMegEi7dOzQ_zr^VWV`u1n<DFryJl=jg)c7OSma6f4C)B;5{GB`WI=lU$u+tB2xvuw<ZSRGgz8JbqjnljN`!c8RANbRo`uE1`edb6@<p;j~RM-E9ks+raNv)%=yREBBoW8epKfMpUpBr}NDR^Av_xIbW>)*7O9?w5V>-)%NZ`kR3(yy!f`|{&LPT${ct;+9RdZpBrC!wQ0uOEtao)<^!{*V1j*Z;5CA*UZX)>dEFeHWBCeedpMUH=&ct~|l3BX#|AUsdCe#H`hMzB{SwpE)G#^u5>WDBoZ9ddTT}N+;{}mY(M7ANjI|ejcb--PPZIo-ux4ObuP1f`P97k(ayZ^U9u6;`Du^7wL8T+1IW-{+|=|zWR@;uJQP4EZ6lcxKZZxMVCADI?p`e>L09fN!3RT$#?aSc(b)X@}%DP-u|G{c`?2{FUGg$#rXETh|5<hU024p*Ol?@byc3nT35l$Y9Cj2T^QfKE{tzq7v*`Z>%zCG$;Xvl*T%Q6YvbG3wejui+7s!le0yIqzP&FQ-`<yuZ|_UuP&YjuYhNw*t$o$__P$!)-`ZC_-f?>T)_uYF_I<(l_I<(lzql`SSg3sazGi&;zE<Afy001EzOM!QE!N|-?#t!Abze5VeP1@deP8yyyg}E~ey+g(#d8JzFP<w*9_zUxa4w+7X+0Mi-+nGKzWrQeeEYd5^36d#zt(e|@$Kh2<J-@5<$0{<y1>)Lx}Mf^rt$6POy7_1>;Cq0tnsbqVdLA+x8?n<=VZ^P;uF>1dTuZGt>^Q=ycp%%&-2E&pW8jbc;(yg9mcocJIa0Qy~FtSdq*Uxl^&1v-c;^e??-{RwQs*qmHXCvljobB%D3P9jBmg91y}Ua=WD(98Q*^Ii)_AMkJJ7>ke2aDrR!u<k)9Xpz1aBnd$IBD_hRGQ@5KTC8J*vHuQ$H^UT=K+z25ltd%Y*2)<u=a`YvI7`@4kk?e7xh{q64(^E)Wt{;pzt`@2fHZ+%xWzWrUr`&2jW+uwQcUGtdb`l^*0U;O7ub%c;nQ`8rEV;!Hgq$&T5R{lvVztey9Nh_su$N%?}*0kstMn~gWLh=?u@^1;rzau2SN=QCINIp$SK1E1AMo2zFNIpbJewmQGjF9{oA$dF@xj!Mf6CwF_LUL_F@=b)~8ieFnVzj9ElU#+6{3}9oEkg1wgyh=@$#)Tw?<XXWK&Qcnsi~>wQM^u^!`)~zID=dxh>>^)nI|(xhw=K8D-*pNzKc95Xa>B6JX_I&a4vN>HP6Jmja*I96nLr7>&dL8t$2@-rwGl3Zy{Ga+7zBnt<3sdinokh%h4jZ7P;ckcz7iBnnp~=+a~myGwW?RUUlZ%%yk^zA^N|9ZiB1PzbaZCKEg4@=qs?`m>9Gwd|c@3#9SlAc(EK)4UK_M(f>8{I9yZc^=;O6HN4Xt6GUHwZx;I6FxN#*yb~OA5)Hz&>0bxE8Ge;xj-n^w+c~BgS_huUTr4GK;mP&*U^IH68O)cAQFyZdR*snkKZ72GpMlq-hvD_`X7ng5b-RO4(w4g0!9m));r-}q@P2p?dK{Lz!@<S0cfc<al3yV<;*H|`rxO$LGN@Au+8IuPo1(vlo5Jzr-^OojgcqaB;l=PAv<RL9Peya$$?#Y-6CMi>LhptL!S|uf;QQcIv<{pKC!sgPN$?$LP52JDF<K373^zby;0AC#v?^Q=u8&rS>%$GvIJhC~LF3_g>hBR1>$^9a4JR^gGtMS>8<~$y=n{C5&}-eS?G1SK8Ak%z2+m<XO#KJr$@MJP?q2i&+(qa$)Qjki*Mhp6Iw#@<gkG~|U2VdfE%dc&uFXYw^%!eiGyyIUdOex-lY_UNvF=3o!go^J&O{fyRK|G^+5+CeICr4|cp~GRgwBQ=FxFeqy6_yvITtN}UlMvR*-q@l^Dxfl=$&vMq1U}x=l9_4VXXVmU9em)a@~v~9>RNw_C#V5USrOo33@9m*U@58ab3^FThI76pfAC49W~@UJd9m>gBbr{v=6+Wb2xzRgQc#C##;JjMPpbr=J7i(5l`YZVa)B(Ht-s9?IKp<$+~ur#=Xo*el#BC*t#4qwWWg-XiIGk%bWr7u7sZ^ByS?-<Mm<gvIxn2(H3xD*h@%GB+~HqQJVwQVJEeC5?+Dsg;&6<(F5=S@~mcT!<ZLYlN{=j5066!!-MHRj(W;kHb>jR&0({@G@^Em@FkmdIfRfr2Au?tfhVA|;R)~*bP+rSo`G(FrOt!pIm$Voi_V1S!e$R$!u&14pU+%0VLqg`hh-h)-qM|roR0Q})8Pk*-qawQ^OxRlqA?&ELx~=ElDpED+<~^_WZKEJTcK?o+>y5AZnP!$q}`KtKSJ_Abhv}_XiI*C_9L_l3CT~O3mm+Vw&dq%OMZd2<aM+qKTlioD%z5tqAl4^Tk_+yB~PU-`C;0UeY9o0$I$liZ)P11WiEy?7iPW&Foy$}6EmlhyQ4is#s1Qrb`R#tTp#z+?#jHG>!BTOGncIi$t}@Va7(xi+E!HTeQjvBWuDC%ZBJW9H&L;tq|r9(z)MK(i}n*0dz9oXbfBo%(<Bc=hl`3mVi;{1d3gC~o~T$uX3vrQC|U?V3eQBJfM>$<(FO2)_-S+@yb_h|tc;i{^{f7;|9({Q=a&zCuK$c=AL;(Y<2>@iXs+@PK3N&n<hx+>1+R)ap*eEb5dQ{7C`gR'

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
