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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1b3e8b99913442308aa989e3f87680b3/part_000.stl', 'relative_path': '1b3e8b99913442308aa989e3f87680b3/part_000.stl', 'source_sha256': 'e1a7d55e5fd9c1b5e665e6ac94acd5105aaee6e19cc01c8d6ddb204677d4d81d', 'input_faces': 360, 'input_vertices': 204, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4361456632614136, -0.3601078391075134, -0.4756477475166321], [0.4218842387199402, 0.31994280219078064, 0.4620080888271332]]}
GEOMETRY_BASE85 = 'c$}r03se>57RLwim2ZN?XC6hPl6;#;8Y8|Xl@tQg@^A%w5g;mx_!vx!GzA0!^K}peL?l!30U{$0MW8f+)YLqyhmZ7@WtLrQb?4jrKgT(D-MiLZ_a4_?|KI%i&Yo}f_n4Wp^z(IW>LT%{r{w*|{jL^gNfOaUa*<*}qnFH|6S}xxL{zMU)Pa2Q(KTgCz+}G}4pNL1=N=Necuustm&tuZn5Vmk$vrGGdP#I}#O%oEkWk@|3l3i#s`-oO1xJNy$IlNMFvP<&_yrHsD%1b?X{B{RIe+JBndr-eq$A!!i$@m<ReId`QuuORMTIz)*R*5bF_V00=T&NN?b7NL9k=Vq{x7XFgs(p5wx8Mu@4q5^_5DYb$K2;esW?`gmtUs#L1Em!b(fQLT$6N(+E;$43g6^<>>~AR@HFxzpHk|FbTFoX@@F`GLB3~g4*6qSl~DdY?b%Pcbcp)@+LX_!{Z<F^l{*<HssGoG)YI|fm5p@XH(k$Bp7CCEUZwj)_G8M=k{|x<Maml<(LnlV{m0}l`-N2T3?g6o$)$v@%W1-A^!Lx7<MufT+^+3*&eJQL&M!?XWPj*H*6msR_nm!mDbMlDV#?cTCi%+x8%5+Vn_b2A7|HEdq){EriMNl@aeC$Fq^*;9{6@b>$4b)c?0=WGk9@bA`J~UExIlhYFRt64awX-zmBfB+?@St(3y%-easP+sg_@@Y*VFeuYuv-v`vd!Pd$2#foaae+i_b{+PCr0?YCt))Z){yl{d%gA>ZUkU@w{yDR}JOqmrZ%hm*-!g_R?MQEf*STTrDSB^7RyykuUp((0Hlc(|BH{<&dx5?|6p%r^j5UJbshTk)M*p<FsJeRnoRS$d`7H;JO?g!~K4JN;S2Au#M)Y<u?<z-|R!aG%4&L<zMkCpLcdI_E(QRPVJMeoafZpv!nqRv*`N=rqlIXMlU5_J~Q})P}A>zJZ~(4>{pGa@isRGenIDvdXlf^450O6`Yemu%Tvyup?X%#DkQ&sG0ii1^>Xsnx^8<(J1*w=x1k^Ta#lU95A%*J%CGy<{RfS9epLs~|LY%gy~?$tv_9ps->OJsYiONYy1CN#qz>8SD-LbAos!3S;H$|cjYi+vVhj1wtgCMcwVLaBe!m#ad7k-=)~~d-falkQQ<da5v{_4a=~2h+T~jJKPs35F|M~=;KT&rojMuAlOlmOt`t{oU!hPhM&|dxF$`zxpx3~HCqAHBnYYj|oF#7uS>b^Q8klW|n*+lJX+Vi-)>SK3a^SWog^fvgmanXIVm)&_y*RNkO`ucfoe*3<hr&S@XM|s~kuG_fF<;MD0qT6%-;p^wM`FD!QS7LvseM5cZ^(py}=9Syk!R*{%^lf#}{f)t#e+Tb-mad0*-{}@?-=7m#Y20<+)*szp;mUsMcD}E@@)y<9@^1WTI&W<%?MKSY$vpm}f>g@?_0P0k6t@u07b}r(RpMy9D87fOy*!(JwP;`t`GF>Ge><X#{1~sTRL`SvJpUj0ml^AzUdz8k*SBIS?~9{4WYf4buBH6eW$ApM{NrvS<tZ9U>)Pt}9{WiTsJ+tpC2DVy<H?u5`9~_PhcjGP$-|BPyjULh>LYYsX+q0VV?C|kPrhpO^?KU;*B+d->wlJ`ov)9h?pqJMO1`-$l<H$n$mIT5Jh^?m8~N4+yV*B8lW#$O>GC5UNBDYv-M9MPqWioYawUc4TlzNs`|^rnV;;5nIL-s#)=%AESy*hWgIf0ZqR}_$>l(hP>k-<QmFC}XraCVy;{CbRR|n}j55I$bq~tJZ)4MdEtbT*Zw|?u%`SU&{-~3Z7`=*BDl;_B~0_uNt1?^KN=XBl&JTL60e!TT}x*w}<?_MXr>85<rZ%U8RJaJs~6&;6k$|DV`rFA5CF1bd>8H4s3uUDS5kjD|eKJGR@sP$gsxXX=w?0nn4t^2oEW%Iata{qrh%)WAM54HEcN%v**hGf3~F8|d+KJr@<@73G+$ZzxI^A=<Ol`gsVzP@kkzK1LM(hKSIJSxxVbA{`YyOY`vKYp70YR7BTe!#8m#{S4jyBq9${d#Twhz!aX9!>Wb`Q3r%$!~c-joM8-MdM{s9`L%m5S>c>`=Gd(>fpD9o?j%txMbtJHP4uJ$>^K0er>)IM!qt<q>PRe>$yLkgV{f|fSwOcVQ=vKl)hU<s<xo#J?o~`Jg=<#X&y`Wn$vTLQrU#}e`^x&JNi7CAI$d``1-oA`AWBBZ^^iRU$XO`tY7$10jYNRr;WDrZTWRSsU^QB==YJa3mfcw{XU}m2TyM|=C@W3v-kD=P4{J|-FEro|Frk@{JNjFAk&!NT;b4Y=j-=n-JiE^uQ9*bckm@UANg&*Utz9YefoRa`+9wJzbfPt($I=*$`_VM&)-tx8un*?P0z8?(mwp0JaG!$r=`pk`n%$Ch{t`-T)tn9-<3!6<j1u<o>QKs`DA^(hSs%tU>V<+uRi4Wkh`1dIbQjoKkqXSPSbjjVsa?IWpWVv{w}mnNg;vTNLL)==j1UzpP=Kt`E-8SJ)NJ&A9~aKfO+?ITF<7W$fMN0s)T&Y4}3q6ryl3?rA(veLM5?^p0}-Q`tthf;aW<5o99cp4&FSDyDCr7_cy-G@44>>ay>_mr{{ZhTL;=7)C-S!9=f&T{UY-st#jokC)(eXuwmTp$VPg<knRts{X|*kM|n*FU-N#nCYSqj?lSq(_v6#Jez*8JsjfeN-(xo4KSo@sr95|Uv+v?X^U<0d#?QNP(`i4I&y-TV%soD&_XsIsF2ApO7g$Iq#L|0+lJH$M9jA}t`$d;Nd>uuv)Q~#8PWzJT@e22IT(3I5p1_?{Z=WQ7e_5YHzWG2S%?HJE5{--EUqrs?%`(2vE!jlJ%Ff%Qa(O1tlll}|7s`)A_&L%4Tmsi8jrXNTk?dDjucQ8)D&gm>%5T`OOyu|f#thnDm5iI@%k?kvxIO%i-@~KQcpkmEh~~eXTgLn0)jaZ*?s+sHOj8T_c{o0i>Y=KWD4%uHYdr3eDZH;gI!MnON=YBOPfNr9V83)UtxMB5U!KQPmQY>PPUm_2TgZGLjL+nH^{k_HAwT5zRK@d4URQ1ws=Hh<N9A?!7r(C*4BtWZznwtO8H(p=9-nwudapO%yFv3_jSb-6Er!PPIvQ}A##Oqzn&;oT0(w7JzMgT2@_f6Q-=7klc^{a+p6geo(E3nrj^*Dm+C59xDG!R^{j5V+7@fCn9OaSf9`bk|h~?jf@?*IlH=A6-`11R&&rn(?Qg6pg+|O)YuLE*<{`fT|Uwt`&=BcIbJmpcHI&q%ttu&vl^CF8xd$ngK=UM!K#?f*zjjl)Se&aIFa}T<&sa`M8d6ggXXguY6ykA+q_=T_cIf>V?|L<IfTVu<;{p^0->y^B>%Iu_FvKCKCE>c*q;io-eijS`U{-?e9L;kCu_6EN^;Q#$;Z;IB3=~}#o5bOti3oP_+U_bCQ=$qha;2B!HuEk_6UeRJObRcvxcp&&iEnd*VSBvMgcplmh>I?1%o}|TSEtYFB1R;0@bUSzjco#GWybGKUJp|4N7ekMOi@~MPPr#+%W6-_eW8hq93OE;>3RS?V;5E>3;5A?w+6OFydqQ2oJ;Bb<XTZ+j4$v;(4&aW^(csajX-9<MLC_W8LEu%;UEo#V-3Y<^q50r^)O0^W@F|2~6<P`|MNL(N;FHi?@JaAKXexLgcq>BiYUmp9YVbs;43<&Ti3q{H5rUnd&R}QM)CnQDEkf|q(2n4asN>TJ!R`pbvCviESg-}U8*Bl84BZdjkD7jr5PTXTxDu*@E5T*Zli)IN0dya@0GtNh3QhwrfvyHG0lx&D2!09d0__d%jXJs@1h+&8ZUJozZi_m$KnQLJbq9-2Gc6p^#u51(;p_RE;haL-8~V^5{T1qF=)arc8U@eS;)E7Qwb+9YoDD4mXM;<$IG{z97I_H4hoMKnhr!#l_y~FsdIWqBT#gWY7Fq>93$B4403SeKYM_PS8t@tDQScdXHS`3y8eD-8T!avui4dFx-2=`7M?kZ|y|m~di5n`1;N}Ryt)V7xYj8J&;1Fm8I0E@Y5Q29?OTat9I}GEr10gsang`CqIHe;5XF#`sGr;o<V>u5YSj?X#&@|{r(v$TixBz-kda@n`mqE*=C+k<RzQzTggPsMS1J^=pz%>}-T4*)68sl1vs4(QIFq}*9X=su3Wd9MY?@NL$&`jyco+en|_XID6W`UQ2BcT!C2#j$gv<FydFK{GyDe?<-hxU@5?8AcFL7xJ*1MB;YU`J?kup?Oi2zG$B1`F*5b^v#RhJZVP=RkLY=YT_@JHVmfFlahhXa+b8JQq3-JQv&*Iv*_54cryn3fdmr3fu(R4BQOY-vl8(O`#582V7@Ugy7E5Ip8_Cw$9KnaA$CL=v;7j@Uzga;I8QFvk1X$piRI{(2q9I&fw0-+XmllgX3XZcxurX>H+Qx9;(GCs1HK$%TN#Sds?j5Vhc1Gyal{jiw)2Z5P~;BlffJCx5dzC@B}S_wHS{OY(@m5T`<}TUaQ4IE#eV^7a#-&XfaZY5n8+f4FCtAjo|mSh%)p!3i*Y;4UPtzp<}>f&{s2R=!0V)T+eu1ujq3ELhvGJFnAGoHgp15=vc5g*KnL?6nH4KKX@p(FZ5Ng&|%;asLL>@C)fw$JQg9?3+e&(0uO+Cf`xj6N20FY2*E+nh2S9YJJ7XYq3gh+Rv)5%8^D{PN#M=kEzosfq3?mkwFlz5M}PyM;ot!90_eM7q4D6g;P;^G!D7ycdHp^@@J47dcq2Fwx*oh9=SakNMY||?;qW&?<DlW-IPg?xAUF`$JQdm>JQX|>Ivgx?3|Q#f;F;hUXcRaKeTsp`f#Yxv!D9Z1xgzGRH^zGaJfZ&3Ah17pCG;KeI~dEA&?N9m@G|I!V4(?Mp^L!Fz_XyU!L!k)Sx|qlKh7aothMo|jkqqcCVfy_F`xAPbtJA;^i#|geZP#ycrHV}m8fkD>gDI_(8R^@KmFIMCm%)Ji0u9&*1vw!{%0NIH^0(y*?#2l^KC}={wCT#QH)semM;Ah-)=HI'

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
