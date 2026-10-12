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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ca1867c11bb48a39eb2aca203beb70b/part_001.stl', 'relative_path': '8ca1867c11bb48a39eb2aca203beb70b/part_001.stl', 'source_sha256': 'da28babad43e237e0b0dbc08d999ffd0acf43c16694fa30269a8c871e5fc81ce', 'input_faces': 484, 'input_vertices': 359, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07722149789333344, -0.054210320115089417, -0.4999997615814209], [0.12415794283151627, 0.09748917818069458, 0.401107519865036]]}
GEOMETRY_BASE85 = 'c$}r12XqzH+J+|-1*L-o2<1>xNCF~+7D|pv35Js3g+OSBkOV<7G-;s>y(1=}3V2XLy&y>-6oDK>P!y!xi&Et%V7b_ps=z<r-tQh}zRbVYzy6!GzV$xy&Ug0gHZ%LooW#c!FHuF4e|5Em;Zw_m)zdVJGFlaFT<Ykt!-k}eY5e-gi2+&#;nSbetnR(K#rF-+#%UR$DXC+Ij1G-<g|<y=6&mRZO-mm=cJ$!a2c?frNhQD2;Mc~a8vdA929HcNw!@k=Zyo7s)-cjF#r6OEd&;PS@Ayagg;bX(hQ1R++cCA@Dzy5!({@;Wf9pV7zBcXR+!(8meA91uEZ3UvuCZccq18ve^4%|Pf8Uz#4=nXwjMYcJ@;&npZMBu(sE#Pt^i}!rwbbu7So6IZm;M=J^^vc9-+Pna5&n#oD~124+?7JBpVoAvD8J3wOSJ8Z-nquspSibp*?iTX%1?N-O!#`lB2sVS)QdKMXZmnae$7`d*!-U}WP3*^Ua|S7(>II$8Rfn#{J(#fezjr~$k(T}`pV`<Pk3L{N8cijt0ykX6gubAT_QiS))z4jzBeNIg6Ov<kz!tGJv{l=eD3pn{a{pqQ@-+5zVC1EV(W1|6{mjc<h$;kJ?G^64{a0WxMRW=+s5Te`COZ?#s$77^z1_6m${H{Judgvak;OKt9)HMu-mB|<@0isugdW*t0&738@^8Hx|w3WnZBpR5>fxX{lBvLJ9lJ>&sRu3Z}s)S_?_Z-5p6^{{${_-7x~X8=UK;v`)XWF|3uS0j`{FazV}Y>e5di^zG|<p&fU4fe^}Q(zRE8*#@27{N7rom=C~^#`DXdU+RYL5oYllOzT7vD%Y0srUS?>4Q#s1#<tSg3<2rw9rtpt$vmKZFMe;wpx!W-xzRK6q7fuoNuXa1vcHS}HJWrLM`CXp1UEEj4<vu^IK5k;ZQ@-+x<S!2@aLk8aq+J=?3moeSzeqjd7dh^&b+-A;ee=51C}ND$cyZsHC(38z#eMU9zjSS+sHb*N%wO-dByoK<eb=iAqP<HOiu;1^)A8xTZxS<u)IB}?s@2z9&z0BbeFY-llR0mM)BNYYd0k?@d3}S==Rfy(Ieh+m_peQJI^VfpB%fUexNr9V`DKHJ&+iw^SNZzCXABVSW!FRQtNCF1?0U$3mG7FA9VdKtf8oA)UNhgk4#4O47w+?NirilY-8t5t%2)Tt<6R31t-iWH!q?9)DH&twH+5X@tK)LtoIiCEJmNe{DYsJ0*RN}d`;qCN&siYyPkb!yUwTUWWKoXxb&l8$>U-JhYrgya#r_seuiE^MGrdBy7JX?e=kB|rKYiO%<@)DHvmqjnt!KDzjyrt5p5eaA_sqCH!rBiipZn%@c>R8{Zqu~BQ6lenH(AdUO?BZ%>7smh=Q|(9IQaU$Ye&R5_@0^J<ZA;a315$k-EA$0`#j$`(e^myD_`Y%l7ePhkLydFE$dUI`7Dt)Da}^C^0iTG?B$H8G+S&}ov_<lj_IFUu*d4VW0U8Ia!y2x^_@GTotRgq@6qLY>GD8vJ@lSAK3|mc>+oIHc5z?TNBP=cEA~3&E8pz5*G?^v^WvRdj(*q>TfRFicA?n+$H85;cEQ*0b=Yh5y@z+m{JsyoqCFcA$n~M}qhnSGE!9w*NB*FQ#bTSShfSZYhg~1MDgFCV;<~3@Dt^S#e{lDx_}q=kOT~8KtGU+vB0kS={xHumU-`(_8?;?&J+3=^{Rt=EKRfPop;N2BCH&y+xz>E{7s*FCuJjwnoP5uqQTB399msPmAHFKzm9by=y8mphwS4ZY@|CYG&CYYmS3b|zzbb2+&)hf9JLMnl>ga24jIhl^Gyjjwy-vOsQLxvsoU*s}I@L${D&M!@BU?ZF_U!u1$@iC=B>L0as#&J+EBuyg&F6lR{K4b$9P{C;eBYT?;(L^Ku$p~7b6?G8<)3=PHs83f=7aL}^;>Q8f%|HFO+V$Ft-ahYQvWiUc~1GtFOrXW%j={3BJ~OWGta5L$}iI1mI?Vz{b~B>PwhgiJnpP9;yH}(@C)L;Z~7~<<@21Kr^R(opA?fV{O_O6qHTAl<8nQm5u5EaPq=UPgYwxt;l9fEoQlhq^?xMSSNp1o`-{K&_H3v5%zagkyY*pN4!b^ZU-iH8`SpSO=6D77StfjTJ><SQUdm_JH}0!^?VHomXZJ7V^ZS>U5V&0U{QjtXc7Jr~&6nHyO<lJS4Uj&&?-cPduS}oacZ&GP_mo{K>%-Ow+&9-P@cBA{`zl}G=ac@2C&hKnUu(Nu-zq<`zIg8GdNWl%Z|t8b?(2H7cH()b|LyCSt-j`2pCRUb!NIFGzt)8fLeB?$X)EX6X)$lTjV_9Ls~6rB=Nn&lnLb;0c}66y5<XkkDW9+Fv@YLCpREslAGcgB^4PkR`{w-uK3|t|-<&^Hhp)CC*X;jqA4tDM_$tva9lw>=6Xkz?Le$q^sX(lweBRWzt>u`<Wxm<oExBuivggC5&z}#6HD4?I?7j0uKQ=FM#pYMOoFm3-d^tHEP9Bi{{&wPdwm+}IWt;zZp-}%{J~8gv^4sqUUtcj@X!~|oY<`~&n?!%5pA+9Z+*Ph`u-0EaCpUfe{M;Q8og>S6D9Us750Uk}|D*IfHk9?>_p0!<4JF0%bgg{OdZE5}yFWfb9;ew~vOc$T=}(B1{>uw5+5CzjLS3$|^0;HOHaZ>GwdR`i-)$<&@!XL4deCj@dne2CyHB_KhfaxdT*19%Ijb6p{?fv7#d)e-9ANir?-J$scej<_b2GmczCQNwHjx+p%oUqIdyx2^>;5tJvenn-tXwO`cW9*DA3c7#=&whQuG;(w-^k~J(|)r1^CG8;`gBgP9ap>Gc%9H+)6d&{_Z>OzbJu=p_XEXv`6njZ+NEusDEh&7JjL#BIwIfej96*+(f|4<^X-1;tFr$m{&3Oeuem9F*RkgI`~%g+`1rPVv-@ujkbajlU)cO>ON8$)8Dr0%(q6nz@q~Y9JFea|OMb6U*?Pg2-{gvX-WBkT=r?yk&St0iVETMML|xhJG~Z00%{O2EFPoj_t@~2U7RPzsr0W)^^TqVp`Qq7ja*NaXX!`7Y^o9E!kL$gcxmEb=I^cH~N}s*IGkyO4ZvSQZzK&n7l+UhLp8MP1x0Y|dH&i}<pEzi|crU`QpQg{QpZ)=Bq|dI;rq8a=zG|Uz{lV@prqAv#-hhvCZT*Ayq^8f_pZY75l+P>KdO-PnJz)B5Jz$o@)&t&&tz|x2pO`*dpZN2?kUm?7E1$2E_5M}lx}UA{O`osxmj&iq`$xTZHhuO!+7o=#mapDxn?8Hr?cP69tmpW171L+WRXkm4i1zU3PNvVFJ3Sa6t{43Io^My8T(7X_oXY3VIZdBE=QPXV&pAt{$b9zP)%4kOS9jVCu}<ah7nIN6FL-a<k@@`nh4R_^3)hX8J`g^8ziImH{if-&_nXS+?>Bu3Lk^03_8#2y*?VwpXqxoddwJ7m@8wOOy_YwA_Fmq5`jbN8v)>h%zV&wn@wQ)?T-Z0`T$4a!B#bDnRngK0TYh3frWhuu^G{5MMg5<CViMIV>c9PoN#y`di!q`Dv?sU&I1$<(oCqES9ReN%PKBm`Q^9G_f#5W-2l@}N2iynxJh%_IBeWj4Be=d1)RyB$pH>NwLHvUz^=0r6;4#oD;4$DZXc=%AxDvE1xDvQB^ciqva5(fI;BfF8(9gkdfNw&n9XFx%zzqxyF`_y&2wcX9r;R8FehS;+$O!@0z;>t+VMYXl8)CbW5ziVC0c{MfiG40;1elIf(ulIq(qPis7ItAf(uiuPOEuI-)vFBZMqCQp^!Zvwln2+wHhuO9<UWD?8fZsjw6`(J4nf;!Ujt|em_AzqpD%$nsAHEx`%1xo3Vj`fehxxjIehj><UNTtmqfcmQEwOeO>GCGEw$kV<FhsK`I`7lY3z?c-6PPphNx3{jP+CKqw*NLNaRJLABZ(0{-*f|{T596F_`odFzI(-(g$GDfB?y)b-_)ctq{a7Ac#95h&v;QUqleMMi4iH)&)l!(cOqj(0DLu4=`yPFlkjV=^afn=>jn6Wbke1d?@+E{R|##L|+7P5;Pf{1nvzT0PYR$27MXa4crpy2DbzULhFD7!H+bl|Is8<5NAWjg0sP+pbf#Jz&)WA!9BqV&<fxL@JMJVcqBLrIvSh>ehB>@{199*Kx%~m$rQvbpzXmez+IsU;I80a(0<^47@J;*zL*z%F*fmtB+QW{j7<+jZ_Jn87@IcGmf$wvs?b1iRWQw|K#b2Fj7v874tN1{6nFu6GPEbSC;ELdA_4O-0sTH7L3|sU1<pcW-$p#dTz-hYuY{<G^Qj{GIvUy)91ZRc?FH_Iek87Alu5r$U4|eo79jNrFa>cGv>2FzI2NjbDd_JdXbCU{aa(99Fa>cFXgM$i@qGmGt41t0qPVforO6<E8rmF8LHs1N3z&kqI5ZASK^y>W2c{q{34IPsL0lU8mnNBlxIBXRH6sQXG0=z}(0FhUa3^SIFll>mCvZDx6u2F@DT4S}XcO?W;OC&tz|Vo(K-+@bfIC1tf=RoBJAk`E`-8iI`$0Y6e&9jSf#8AY7vgb7Ofq6Tf;a;@0h|Gz2ps~R2u^{<fm6U;5yXw5jlhk;LC_lDAaEeGDmV~a9a;@s9UKXb07rt|&=@f3V6YpU3>^m^hrURL4h54Yf|J2+=!;;|mX`8cqAsNMEp@AJsegU6kF++JG{n;O5KI4rp#MmtE&Umd{w941OqygFizJK>>2S+<4Y!ObaRxLUoR0QqK*wv3=Lz*!8gwu?4cr?V1MUre0YTgX8Ubzrt_Q6KCanst2d;%64u;kMlQseegIh!6z^%bu5X60<L%@B(!=Mwu6VU!)2;$eFX<#}Z>0C{Ob_6GaUqleMgti5fHUqZ=*GCZ7hBg6{MuBUCLlDH#(Dq=`&fsY9O9<j5Xgrv7AUFv;96_88^?*HSe>#GAC^Qi~!iZPUSFeMILHk(xwhzXEG}baMv6ium#dwmovWzcrFtma8cs>x<g4Wa?&n4n|(7M{=`9|CV+FW})SBYPMJ`X1Cr9GbK#J!=Z+T(M9I1M@iJOX_|TwsKFh6CP>?OjG3G9n*(5PT5ZpF%$aA28wrBhEt4fd6g8zl``0dKi4(h%b%!2zms(--vxid;vWN-ebg9M(l-N1^bOSYQ)#jW8l5W`2czb{55j^1w9PT!TycV17O;}33Vpj45s?NhdPsP0KbEJd!hTm)StOV<bm@o+q=>CdGKg^wGpe(j#X$s@k%3BVE+p2BVJ>~+t~j$_N_!4k7EB(>|2BOu0~r|qio{!_*@QjHFy&~w;s9@d>F^r1YHB(g#DYL?^-wq+d1fC;<f0zbx<$(J?z^6T?am?$$5GL?8Ejyjo4<y1?VO41@Mp1pTR$Ze}&!x{|f#I`V06c@I~ll@I~-;=ngRHQt)<gCUg!s6Fd((4LlD#3pyJ-3p^M4CU`FRE$BAzHuQ_)t>}Yo$lHn_UId*DUId;Fod%u`o(i1<o(i4`T?(EFUIN_#UIN~UAie>;488&W6Z#AIPw+kHE$}_?@6eyYzk{zqFM%(i{nwydz@*=RuYrGu{$?rjHyo4nuB8rlQAg50EOq_^Z6dvHY2$VD0qOf-(#4kkS&Tj-onh(28R%ouDV9E;f-xc0En}o(3`rMS#&jXZd?DJu2)Y$a*ZWhNyyg?1#`a0@6(i!~0*X~B{=fZ8=i@(Je2=vLgD3x_{V~1ulW9g-=0p4VxRUh!)%dbnOng~CLw9BEe*j(}*=_'

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
