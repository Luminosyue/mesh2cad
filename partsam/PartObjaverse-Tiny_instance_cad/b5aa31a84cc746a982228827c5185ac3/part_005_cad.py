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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b5aa31a84cc746a982228827c5185ac3/part_005.stl', 'relative_path': 'b5aa31a84cc746a982228827c5185ac3/part_005.stl', 'source_sha256': '05b9b6e67cecdeaf7c7e0305133ff09453a3bd1716132231e1203a457e23a699', 'input_faces': 540, 'input_vertices': 358, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.44371461868286133, 0.2237376719713211, -0.13442620635032654], [-0.3868376612663269, 0.27372226119041443, -0.10152268409729004]]}
GEOMETRY_BASE85 = 'c$}r133N@@+r|$PB*Yl=bb?3_^E@RNi7AF42!G{9&{AWflv1~)+NxHSno8XmTBWF}p@!rdYY0Nom@g%Y8f$EYf8O&v`}S_jx7N45FKfN)`Q2x|-u>=<_Sxs$ASODOPoROHAfv&A-{J~YGz^LSMxZfvP~w;&34@Yqju<sQhf&D#<wxo4&OJKC^v+?7HQossI4CJ0F{G&((tL2^kT5f3@W{k5iSZ-)k4zjmNc=YO!;%JN`$=!aj~bNyIkaAb#$jf?s$u3N^Z)qcFFhO|bS^bp9OdE;N66>4<x=IdY4p{6N3EHbZ;XtDf3YU=YqU?%{Pm43-`0B8cKPfcL4StL@?CAtZ<Wu^q}K5N2t)nerL6i6`o@Gv<X<jn<-4Yb!>=8S{IAxcpE=D@=TvR@LpoZ%?Q{*~--(Amc9Z41&xaxZ%W(8xHxBvFgW(?>0)OCE_?60|PLGbLQ=zZr+nbhxKP{iW4iP0$XMP@SUdlIy7S`7%oPJa(ZG9ZAOQ25Oa@soB+7;K=f&Do96hZ#P0QjFpTE1(puU22JkL&o8vsS)O2>S08gF1sxTfQ+iBh9;ik3alOn)iG?eph#z_q@zEGf=-lW}5fBly6kJf&BEcnD3ZV$WJ(z=H0*T{a=y){2s;~nDw*u`TK)feKjxhj0^dB?xuOq%MrQC@}0&u_{lcpcl#Fpnl!DxGtp`JX5)3*I=J8Y8h)+y+B&$De>+8=mt!&Nm))qXk6rof$8%rIn~yq0H*4!)KlrIu-<a4A>y!09>I`0?^=Z%j9{k`9T0gFWli`nChB{?BrFi>h>~~t9w!n9h-*Sz99c#a><*RYcCS$e!)wo9ZTUx#v*U@T>R^M|DyySb<jlNoc&$>k?YU`=Swa1Kx-(j^juF+$ZR>yNc#*Wgim#2R3k@|J#Iq4cO9R5|8e%)Umrss29bJ&}&+z*EGU)m3j83W-z-mZ;nTNtnHThBT#vFrJ2zVua}uG(K(<2si0NB)6*s8jzE_Q|78xW7I+p^fYGiN^i)#c};Q(szVkLH!*j&MUtT+IgbJHR-GSU5)FQUmgC<hx$4vSB3xJFMZ$AH!eTc>f62vMgG1lt-kV&)wvFP_h~luLw>R^&dI!8Q#7CFxu>7-yr?tN@38l{PWtK`_Ke#)5By%mv~k@_{yO75FEy@X`F+hd8U&?!`!CPez4G3fSIyVC<}UJo%At+x@Vx+^=eC;H%f4qF{LiC4&s$sh1=zRr)p_m;x{7fNoP*DESdD9xJcBxgZtLe*PzLgc^*Untd@egD?a}7tdA`5D8~Jq}YtM1VCp#_Qo%^n~ZszAM&G*cUzMcC`&C59_75N!Y^?A{^t94#o8RyK&_3%5FIP5(y*TYr1uljkh67?fX>HCeoy=sNS+Bz#gAo#HNxXxUxQ@qk)t<S<MkUy%8Hm<w$GWf5zga0TN_Yr+}tyrzTy~0xDM|alxvC(%o?xv3$>O_9zT<bcj_Y+sdSI8ee$;x+D3`Rfg7Qhet#PaQGUY+J^`6m0cb(;sj>lEa(ACta4;zP@Kvmf_6pCLbQL#rQ?`^0|dE#!CEs`X<$7z00Ui#D$FNfPQrZAblli*bI^w-?wCe|{*=ldMGe)pnuJg4b~lG#QLK##yT$r+S}!t2g|;6ExqwyB++%EUiz+{<f%J{vY_i$EA4t?tCw_KJ6<1g#QumK8?d|;NSH*;@zj|*A)Ju*+;E?V!Pq8u46zGUYEs|?{e4QY5BdX!r#~y>s+WR=G8Y8byA~_c=u_<hams^_89l66X%$n{^woL=d(Yzdi(abdT9OIlS?7LZcw^4u5UY>Z|jO9KXj4SkNHzE&G+;}-~D8=H7_&3j(xi&5PtrpTAxn(_P<wXeJbC5?K|X83)6gi-VIiL$4>*T^|b9M3jfS@_}wzG&PNNPPQ<t9=i?t!HGkR>%eR%RYOTL{IskscGkyIp=R^Ij2I?H^o1*y*av$}cmyN!=qW@9v{@t1Wn(vwKO+Wa%V=dpA6^4ELAP?%V?4ynAQvQ?yT7AdU+^F+qKh)1$j(w~AwKKK)Hv0A>58>aB#(sY8i~R8eQUAtW^q=Lc?OS(JZOu20uypVJ@673|?SIw3EsqcCd^}I<)8m(3hx~nwvEP)>aaBLAe7Us!;7qaOoT2aj#Rb24bF5FHobVrR!nixX$8(`r4){y=Yx~L_m_yrF?jN6F+){>C-+Xus=U%1fr!}A7j~pRcmTynlg?`42O7Zs9xMt0??OJ}9Gw5g0DXSm5^4~mx{Ej1Wy~3WI_TJCt$?Dszyp9ho-<j-(>$3L=u1msQ)cNrr)ZduL+W)pU?!X^&9DPQ{Vjm8>jrwsJ@OPZoe0$Ip+()PTy0rZ3cTm5{M$31Mz6C%26#AUH4EK@p-S<%cT8P!ZYr;+V%`YIoc=!&hfBN>4nYb?BW?1>Q<(J|2EosfywIBfV+IAlP!j@Qvh9TBEyUw1%`b;li`9{v2Sm(#-@XJ)OeD}-_xGn|KQ0I_=b8_`1+($(Zq0c2R(C4fG-JhKw{oIVhI+Q(tIzx-0zIxxTwh#Wy0LynKR<q{ouDKWetji7m*I?X7CzG{#*=ldL>YEk5uza&b2=e)R8&{=SsM9JIeuL$x-*g82txZv<QYX}joR0oKj6(j5=UD%q)3kiE#YC$gcmJvIFV;=>UI*94W~dYK3D&`9I?m@a_0Xq%D)K`&V?SK13;%<OxGn=Dkbkcx{MqA?uim#G)j<8tqtWO5s~Go1b*#^ZMC5-x4(GY8Jp5Htk6C`X*|>kB%AwBMDe$LV$93#n2KhTD!&ko#=~W8-oF8xbuH|*mr@aL7GsjuJ^VU<GOCti2e{|w8?>?39JU9uy|2&MFR22P`8;1Jxhob(tBHFm>eatbjFzN)3fZu;Lp3CnQLY*f`mhU)F70=D-1yCnv;xX^*<(Qoxe!^?Vysww?RX@(FU*mk9pAUZY0Qg<rPSJdo&vV1I$RB?F*DYV28_IW9AA<aoZ{m6-`)R&;VISu8O<wdFJ_z$FS{n0OmmB_)7|S>I%+q{(+XU3PSsUlr24DD7dSYDl9=OE^eU9pbb?7|7^(x=dwKeXS9l6lw>wQt*c$DJpyL<OX{cZEm{~-f?o^6f#GnTnD|DztLqn<A>`)gNW{~UdhVfmY);dg79;_cg4cE&oFnC8;*xjv4|eKg-bt2^q%eu#Z|;<=V@jLPlu_Eo;~o8u|ozH>$_>ZtP}Bg^vL%euhl`=NRHAJi|<1pV||<MQ_HsqNw44#Gak{2TReMPS^uHB!8NwVuZHnOeU6a2wR&^IiGwtsT%0-#0vUxSq~p+i))3e5&VvKM>dP?i2VITWRNj<H2L}c`6e5{QhWr`Uv^9nz$}Jw>|!&7U*;4FwIx<Qunnh>mlal*A(M!UEuQeO`|#1;p0Z=Cnx>j`lyo`l;Z7s*7M!Msju?Y_c$ZZ1N2#@A;wKg#JKtXLO&%MVP3;q=sx>2H~FS|`);3R7<cXx?32KI$bY*c>X+N*^7hT<wJ@)_$(rx3TL<}lT4KJX?rQ7oxqs<9%?9Y_Y*xxEeg0nBEPn^%#)rVqS6cJ!HS5AZG8@;W;%(%&*kwI;97D&rG`~X_)~8(*-|KF{ukuT}cO8$<`Kt582>TP`4h_aWnX<z5N<V5M?(5n&F|T#Swf&}i_n<0R&xp2qe&0}Bmm>FZUpKgc{9aYzyJx=IkBGu`Y;qm_EH16>H|0CuGqrVag#Us04%mw4c%vIB-oAZiIqf={t*>eI)qe2!+&^mFTx~PqzrP{f`@T@VdCgxtf0XZ>Uq;(k9-sZI>t%Gk0{@fs=%0V@pnUsJ#kBiH`R1Im+CEgidwO|oA3A&dj`}AGz+Y5H^HqIy-`V<HhJUD#c0MRy?FV%~y8B(ixT{xTAM*X@W#7ra$5g((SPt#^<?%VLT4&{(t4nD2yCcDk{L=y2xo5s{5##PFtes2BH+L1$&L!8d3&_9er=7#L(dUt$KbQ7=RKD|RZtZ#D@h|7o&u!(a^;hp#W6xpSoW9!g#WCS5{EiRPwe_ET26giIXwNm}+n@Vt&m)h2H?Q{GaZNd`^{<{&j*l|nw|<Q4rQT=g+rysWJ)iFb$~Q|J+H=|X^fxWv$@c{1yF;?DPxwCIoOMde_q;#MJqf?*Q}}#u@%WXVqrQ57c**y?KP)_faX<P4-<$YeYA!#H{@=NYI_mwCzB}PA^3}OP-`VFr^40sB%IEb`=Z1YvI_mfQ3;BG1b8b3<{L#0N&-Y2&w!^4@;0(s)d%N<@%@@+W_m4X@4fFl#3cjE6eb}+*5c0psME>rPsouU?2lYN|9yo|`mtRJod_T7z-;ez3zryGD5#zUCFs}b$^vU~0`JO)cy})^PAL<;>KplRMa9`Pjaf=>8KEEG%eD_J@^Y^jF?Omu}Yp-_ByzHy*LCSYOPS?NR-QTJC=97h~sWIBWCMnx!|MK)wh9Ti+1R8_mz5XeQnDV3a)&G=aNd5oSKP72UzxMz4pOSRQVHmBlqZ_puxf{7XwIR7Z*+#8Rwvih%gu|#+$)Xj>VdTmT;WE^6WYH4jGUUS4Lgd0^e`-FmKRFje_?ZFCO%^rC62kWlgzydOQv)pefP8~|l_7kIdYdeIhkS{Aks<s$^)IsMWAg9hYYgF=)GV@SjvU~d<c9`A_&GH%Su{UcLfD615wZ_CfLe+iKrTitPcBBTK&?WqK(59RZbYp?7OhKeM2=txM^T%QMZ?Ka<W3CX?$p-g?&KcScH|!9-qdKaXh*W>f5^Sb@zg=&cya=D06BqNpIVPxpM1=KrW;@h;X~AYWKkFS5P1(n_-E>7vgr5ZpUG<&!rxL?kUz+d8QC$FAv~QSJcs%vS@bLN9P$E&a58l%c`3(9rmi3-lb2Cflb4ZKQ8$o9e<F)+B(EZ`WC*XNZX&NG@1X7^?;!7|rjk>+?)w?SN2uxKBjgZXL%EhAytV_#A>`Mn1IeQO$*+;)sNKkM<gV2AWKkQrE4eL0xCON_Su~8?f?S6o989fD7A->#CYNRi7o-*@i~5rbl6@J%{}|9*WKlV1|6vH<V+dcT-Y1LRAYUh6W(c37UL}iOBA+Aw#t_b+UL=eDPR<~oVF;h6UL%X%B%dc=VF>?8eMlC4PX3eph$`poBYqZsK@A{F2>UUFi&Be`MJtetl1+wiO=>l=Xd`k>a#MzIBsGF88byvIcV-C3Qah1FyOU$deW*RieaQW&y~(2S<i1opHJ&V*K(>>sQ|psO<vgv<&%#Fy=pph^@<E31Zt5Pg=+9))t>pFDu`4^aP<NAeGiM7!_y_9GWYINb(QnB=kiTOHFQ+agi+)93PX3x9JdgS%S#$<@9{E#-@HFZNWYKrY)5s2n@ObJtvS=cCJUNLvjGROso*i#c2UCZU2T_MohmnVpM^h8Yqse2b<H+OK-&lt5B<crb(W&G~<cSR7DGcF{snf}#bI2c)XETK7Qx}j$lgabRi>S-UpHOE}mytzRk!O)-Qdg2i*OF(FKhKW$v*W$&_=5U5`3v%o)U{;M9poR$+Ze)osr$*IN6350X;gXUrSY?HafWbD>T6`tII?J0a!+y>YFly_a!YCpa!YaphHxmg4p}sq97-<B5H3J1O)fyrNi9eg^(E&dKQW;4JbS_rzD2!9zD3TYUMFXgFEE5pQ!kT6&yi1)PcnpmrT#`1%^?3uKF$z6K|MnjJx@MCK1IDkK1DuD{gZr_>}Cl6L48F2gM63zf-EY}w!8c+{5Q2ISwc7uLpYFXl0|Eh1Ia<ursN=UErxJ&Y9v{-Gr2jr4K<eBh8#ofLyjT$qV^-J=b3OxY9(r4vZ$RbTAeH^&#FrNEPR+De1Lk8EV`R4x{Le^HHEs1EV`b&o$92nCx1j;OkGbF-9lbWUPt|bEczXJ9r+uE@Dl2B@)Ghw>epn^dE|xUxeVdYsGpKWr;$G+f5;G?Om&b&$CD?M-)0Dpq9&0=hm%K<-((2CZv6Yq6COZ~r@lcJ9ZZfV+l_ypi*|-^|Lo|S9sRN+fgwDQ+MnE?`2!ikL#RW^qNB+}$Rnv^$s@^cQ74f_Cz9oVLzT#m%G8qNPTA2dJ7O5ZJsHBi7{YN3;qDCK&eTri&gAygc4W~=a(i+VL)b=*Alt~zs7=YD4am*N4XJg=4as#G!eP|v<mz05Fotk2wIn&1EWZLQL@h`yNiNAXEyxfKU<emr2p4Av2T?1MgUHpWmC2RaYc*;eay4=-Y6EgDa(!x3a(!|WY6Q6nIh-0v4kx!_2)CuSBe&x<Zp#pkrpAz?$sHNOT^YhXs6EMY@ANTnuk@kUk0IQj+LPR$Y^U}z{=FZC<Ee4v0o2~qII?JWa&K}hL%0jIGg-7fxeK`iL%20HiY#g)w<fn>2sfrSBR3}3qc$Xq)+N^?*JKD+rG}BKk}FYz$tJZdL%1|Gm@Ha~T$)_i`1gJg&Q0~979xulB>RwaQ3J@i$T_J6$T`Wr27W|yFog3mgo{!Okc*PbP>YjAgUDsb6&S)*7{Z~{YUEII4QefN4RUR2eX?j1a&2-WhH!IgIJr5wCAAf~CAkf?Em<_0EZUKrKRe|AoED=7l8cecQ_GRdlS9~N2<H?^twIeUhcLei*R2ZIvI_k&)IhIw4&*fnWKZfE`FmYQf3NE+oQEOoN6k<6Bj=+QAy3GT5!vw$LwF2B_%-T($T875at7x5pZ;s{zdsIXO8bw-FaJsXuaUg}WasQ!p1)LziT0IyC3|z{v>xES<*FP11qi&dk^'

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
