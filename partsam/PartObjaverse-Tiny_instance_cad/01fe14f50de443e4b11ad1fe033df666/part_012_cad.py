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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/01fe14f50de443e4b11ad1fe033df666/part_012.stl', 'relative_path': '01fe14f50de443e4b11ad1fe033df666/part_012.stl', 'source_sha256': '56c6c242ac1bfbb275add3ba9fa1b6927bfac73a4374970e50b27c8a37c2f396', 'input_faces': 760, 'input_vertices': 716, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3003288209438324, -0.1248432993888855, -0.2983321249485016], [0.30032435059547424, -0.08914774656295776, 0.29909759759902954]]}
GEOMETRY_BASE85 = 'c$}r33Am2c+Q;9$6`=vqAj4K_XGlb*28t*WN=e9;wjqj;iqtO6D5c3%yFqDEO2m%6DP#=IBhAyPb2w?xiL=&zfA?y?|Mh&=^<CfRy6)@$JO5`{&wAGT-0NBI^WHf<x|Z9gdMf>=UTXHA6Lu7KNTq!2pQ@f3mp^*!utE7_np`pJ+N@NSQs4hEoqo>w-Fo!NN{vfR$h|aw%%IV^ZF6!@9^5*&aZc{wk)y|s9(cuok)too_kO2=BgW)Af6UN<qw?MVKDJe}mW^|oH)xzQG3WpIr;-~&-UF@QF7{)2abuC!_V?G>Qk>uy-dlZhhW~up&#7H+bGrn8d)-D`GW@|?7bW(OAN4;d?MMCNTmS99ZdmFUOnH7;+5XkH{)2x<+PD7IxBj<(Id^NRf7IgQvi+-X{RclM?OXrqhw=B?Q`%qZ)m<6w)sNcC{Hq_em-$rR+Lu)QGwm1c%D7(j?RtYR_mBEfd$}Lf5ACPb&p2<%ypOje`KiMTGujs{Wj?E|-IU}P?(DfC$xq$#;o8K0@-JDF*v}b1zL7B=^N$|8GRfaQ>bK$~zoco!q9i|WN6ke^e!(FP7i5fQ3GL@!JulJk-*Qfp-@bVFO-X*ip;K;dm*iL6J15C6EceO0vVO|?Kds+_B)_0mw?#>Qs^3XPNq*tR>LrQ&|1^1J#(2n=l8g3PmE;$UpRgv$Z$ESA+Qfb;4BwF0Pwp3+GRA{n`1o_1ll;_<ueK!l1<k+9^zU7fzTY10xHaQ*xf_4^?;A7Po8PMY)+B#>qn;Ul!N|(XOUJqU{mlMHr2U**zRK)pX1P*7_0EROd6<#*a~gl0+1~Pf+o5k4C-_nR;z#-W0_&URFMgE2_)-2^KbpVRkLIuWn!or_{+h4(i(jDmYyE5f&ZoWRFMf&Uulbt4_$kd_{2a|+JFn)iwb%T`&(r+H-`-d97eC5h{3w5Uent6<ALTE8l)w0ebGvUy>|gU5Kd;NiO^N5#d^f+&lbe(LXdS?h)&c8B*8#h(%j&<K;oI|3^9x_|tAOWwG!OWCy|y2S#)%(|6W_+!zS<k5c^vI$#1H!u^L0NXzO_$HU6%G`f1<waAA&FY6ZOOXZEDSoer!I~xAn?=-EXLG>y`SpUPb+|UPb+|UWM_<enWj*uhh5whWfVOP~Y|&VLY<mh<w&7^=-eQzU?<6pY=+8+i!$%%6>zA+i$3E`wjJNy^8v0y$a)z{f7FsUa4>ERn!mbQq&LYPZ*EvH`KTMRp0VA__E&!=av0NXfOK>^=-cq`jP!c@MXUd`jP!cXfOMX&|dZ%>PPu2`;E}Q>^Ibp@>lj7Q9qi$vfl{fk^P4HQU1z)L;V8HU)gVj@yLEd{SwVz*>9+y()^YEMs!}yU)gV{pQrgN`wjJ@{FVJi7?12X)Q|F4_8aQkb2jQ<^IG;B(RnrBWxt_*v<}FABkD)j0oiW^U-ld7Ykui|Lw&to-EXKLjZ^j;d4&hRRqD%rL;dhR%6xr)C4Sg%R86IQ-EW8=_8aEwenWg~U$AM;hNSVUZ{rERj9>lm{;I+)8<NJae%Sw*FXLA~jK52Rb&2B_KaAge9l!Wt{Cg^{OB}!WVf^On_{9(J8&@w}lX(A#AMPLX_5Kk*wBL2tnxyfoAI4+8zK<0@yw5zn{i>w#s~`5;=Ief2{BZxbt+6Wc{ue*o|K{ucFMfExw`~2&r17gC-cOn@<5xf2KTT(@OuT=@5BHDxdjE)T?F)aIw<4qe!5?f%^0!Z)k<mWv|4&@FDZ}S_ZJiAL*#3?6UwvCYgU`OM;JMScX7qng+D|>bZDWQn`@PVQ?Ds<Z+3EdQ!J{8!^q;~nT>kQg3}5zjp&!}Th4!+qQ$Lz#{AiwSpQiI{`=x0uGsdaUarL9mMV`y*N1uy4XM-=#S@rdL3-Wnx>UH6V>uS@xBq_htw|oh{<d^y(A9L%LB;}X-A>Yl{-wVVK`Sodo;>7$CKYZ@^QGS`P`DOiReu*DGNAoqmtbfff^EJP$AI&doulZ%|HNVW){IY&DzpTCHm-x{<Ykpb(nqT6F`_O#NFY%+#Me|Gi=yTEhGGFsce7)W%zr?reN)2CCl$2lUhv%vJl3(ga?dA77^}~MS<THzs@=^V;-!NbI8{&uk#y$0ylwQC5zNvnA{!Xs4xYU>5Th+JrIfFh~lr%r;N9|>P)DQcghUYFynjiJU^_nm9qrSDzIjrA;r2f^9+DrfHhy7LM4fB%vS3hd6`!Vsu{jjlkPU8I|e$-y?AMwL{mVawf;{1yrwb%I<Ka8i(qXilLlh^9oI%d8;FG71+=R<p0=YucncIZde?cmEgtbR0pS%<@UWgS-E)~nEutcU9Bd38NhKdke6A1-K@F#qa@=LmlEytelGoVE7)oHbvco7Rs$H_g}Qp!m`F^*Lzg)#sr2(fsK1NPInS^gI&Z`p=pC`J{~bxAjE)u>P2@>yP+hKUTPWPE!BsNA0D5^~3vwtJcp;>R<h+z4WjC-|JQ11xfv@AGMFxw@g2bXIsxjiQ^YPYOmuLKdk46eUkQd{~&(YKbWuk2l2yxzI~O&rT3LQuhkFlb2`;uQmV2aP(M7ccXlpHyg$Vc_ow-Ke~KUOx13dJU%&5&AHMIHuitmXkJ`(8svp`nX<VFfy_VPFhxG(MS`W?F?=RMmet!`^?32ycb=CUUb=7?R{$l;;_ZMrg>#()gb=Z9U{$l;;_ZMrg>$dpOJnOn`{p-3dept87*Y7XlN1uy+e-S_WT=e^k`TD#NU#~ZMUWgxEm%O)EKe{e?Z?C?MKb2j#Bq`t359^!xx?dGP><_E=E=kIF^~3((e0~2Ze)#@U>zNfv`K!L&SLSQ}24C_w^dtGJe)xUFe97O?zvOT5_4i!sM}N<?_L9G$z2tB3^><tAM}N1q_WHZ6_|ZH|{)YY~f7Q49Jox%Mo%qq`qQAR|AAK(RJDU0WJDT`<y_&!3N7tplyNMrNm;UZ1eyHcEJac7I{;D7H(R}^BCVtpoJ+yvhQvRwR-fx(%zrTnd_9xYAtV$Zc`e8q2zV64w596=ZepTZ5#Sh~*U&k+g*pJnowkB!(>WBBM=Ii@a@&DeRFI<x}e)YqC#(do`i67R_V=Avp8o&DC_ZRc^_ZRWQ_115&E@}Mghxs&Le?JmG>{q|Ic|+3p)erks^L4)}ez@O$eRxCC_|*^hv-$e_sraG&k9#*I-v8o<@tCjozxd()8GrCwiT98A;r=mS?;r8Q{7<O4x$HQt-avh;=P_UF@zl3^9`&uBC+dfKo~R${dBS+49#4I%=TYD4@zl3^JoT*}FN{a(@gkpk9`&srPkpP$i+t*N)VF%PFixq*Q{U?G)VF#(^{t*K>YsX^FdnJLQ{U=&)VF$`s2}QfqJF5)3FDD^JoT-PCHPWz7ksIs3+I(Oy5LJ4UFb*lSL#Q3Bz1A2f2oU8KguJii;McvJd(P&FdnIkQ$NZhsf$y;K=VlI;=*{OE>8Ut%_FIcQ$MA7Bz1Aoc{PuuE>8VC%_FIcQ$NZhsf!Eak-9kbqdbzjxTqh^BdK!><B@tc^`ktJ{dVwWzpZ|B|4Y4@`k~%z{IZPaPIw<Ee%K$HukR1V5AFB9p0RF({h|0_KWV=1C&dr@v5ED!lpSZN-xEL7$Kprz?c#^}Sn)%BtoCE|vD%N-$J%(bzFquKA1i*SZx=t*w~HU@+ig5r->$yZ$BG~7+r<y{?dn^7toWh6-Nvc)?c#^}cJV`fyZE6#R{OX5SR0Slw~HU@W5o~kvD%N-!D>HN?`q@G`gZX{U8wn5$8NsXrQ3P6F5P^sOSgXXeTDc@9%-Gq^{;j2;zxO;b>`ZS=8@K!+jz9jT>L1Hw9Z`o0?i|>Gq>?*ow@iWnnzk^E`Cb$NbAh?yqZT^XD)u8=8@K!iy!5Y)|uOQw9Z`oD37$xT>H^H(z<aQkJg8aALWt0zcOFnUx^>x|60E-e&~PC?u_To-}Sng{@?YzyEF1DYOnu2m-+JFo2wt5zo+fVSZBiXRQ&M#HD8~<;z#ZE-!~9H{C>A(Zs|It|Nemb;r+S!@_U^6VLaD1D*YVv-%n6K%#Zo<`=I*a`~IZXZzp|T>WB9U=Ii?b@uU9b^Ho3UUw^+7zqJ1z8UMOR=kik<=G1q8#YM$b_0-^jW&UXoZ~8x`$^W#+uonNjf7+vE)Bo>3?J?br;XxN|2+yYwo=-<-!(K~ZuY=(=E>^j?932iXck!BwO9{`Hpi5z|dGH%9UUzXBIt+fm#mO#ap{K#V&8xH<249TMf@jg*^S4>4)MqZfK|h6;yLiP#F}eu;hBnL5SKzN*eC*;Y^doqgi<de6GRHi>=Hexezr?X+oWq~%TVfI8+UjD1i)RSWPoNv&C*Zm0CU`FVB>Fb|B>XJl`33ZS_<hd*0=fwPmbtJwSq}R-`Gk3S1zw1L41dh^E@Uojp1xvUmT|rQI^RR*!(TDCuMr<He;;xDC3HSK(S=L2)OF}J@CX+}U0jY1gRi5_2y`es!NoWi<I$_&;VuSqd@#p6U*;m8<M|vL&N+rLu8FW8*Oe}=a50eZd@(u_z8D^Wj)DikdFW_3559!(d?`8>9?SVJMTfx?nG2hf5wM?=tC^Rf@DOwyJdW!f!d%!qjb~nlbG`mL$Do7Y@yzXI#8u4SRUFSp2f?jeG;z@qJr1tsqN0m~(MoVj+Eha;!Y8_D<e~-I5U%Q?0>>+G%yShN<vCuSV^ujvCC1eX_TxIzMJ*S5Qt9ygJ6ap|;rS1=4(!A8ZuBVFhv&Viba*bu@mx5U^Or*_!L67Jo0Dp=pOePSOGS7;v=Q8h>)nsJuz701yj10S{dFFLW@n|j1#?@4Xvq9E<al{B8?Na7?tU%~K=+52WxM=$u>viDk8sBhcTp2P4Bm&w@xEvlyw?4lRW9B{-+&joc*(^p=*#db&hrLZ0;d>X7FrQLfH5D69s(Z<k3mPnW8jVG26!X<F8U7qF8nF_3H&MiHTo6&HT)C$5BMi|7y1jl3qCw6t%qf$*@x$L=&5i!xGUNP?h1ED&w;zc=b`7q=fS<v3*g>xU-TllFMI=fJ$wT^3B3uP1mA|<3f~4#M(>0t!*`>1!FR*6(3$Wocoq5vybAsa{RjLLybJvW-Ua`K{s;aG-Zwj~`(&rthvx&({ow=P8fbO620RG81Rex0KwpGkB;OXG%itr(vwh3to9CCwpZx4}F8Z7ti(Unfg*TyZ!JFXs(D&i@;Lp%)@MrKh=(q4U@XzQ!;h*7O(cj=-;hI@#Jt8a3K0LQaPlMaTXQSQVv*8|SPq+u%3q2q11z(8vfiHynq5a{0Z~=NFTmavU-U8nY-;Uk^-wsbfr@~X<Y3M!hG<Y^T2c8YDM%Tcr;h)ie!au{mqQAkv!h6uY@E*8)c3LZBr`d<+1JQ%v1K~r^L*YZ<OVNBdpL^BwTAl;1lzAR_e!<1FF6N`pz<DnExfqD{hv(BK5A6p(?_#Qp=g=we02l2z-i~9QFLrS%$4}+h0M5~$alHWhaoz6XG8b(L&$ZCua4ontIs&c@*Fi6b>%eu<E8x0t4muLff$O28;Ck?p=#}u1@KNY!_$atOItH!}AB~QMkA{yyuY!+(bJ1~dE_^I{HGC}G0KEoo05?Rhg&V?+(D861xG_2bZVVrXUI!lsH$f-DP2l6v>*3?!rsxfDQ@9yg05^kAKyQRkfSaQ?!Oh_o=p?uWd?I=?d?MTuy#;Oww?c1)Tfwc-+u+u48}tsi4SW*e`4n_A?DbjLYk%11h|fvO%{<uW=F{2f{Okw!Md!hN;fv6x;EUis=#y|C_(F6pd?DN$eFE+cUw}RiUjUzvJ_er;_d*|qd%@?Sh46Xsx#%PCxo}VPVYnyU1Dyl+fV-o!;qLG`=q&ggxEneX?gpQY&VbK`yP^-lUEwb1gK!u4Ec5~REci_He)vqdGkPD~8SaEmhdaS%p!dROz#Y+h;Er$ybQ;_NJ{`RqJ{>*{y$e1KZjVldy|#n>v%#JlUN46I`tR5MJJFM2-)0K!E{0D<?}YE9y=VU(uf)Y_v=|=YB0rUWr{{GryqY#6(0q8Mi-%pTK<B_iU3BDlM~-<O;-Uk`J8*0$=kVuRLkwnI_q!P9;v~XzE%a)*7F-*>2Cfa)L9d1Dz;)5_a9ubDodD;+_0a3!dhn6xMEFSfDD-;xD7Zd)16&_I8ZCg2hL1sSgpYx9(VO60_*irjd@S4my%}x*H$-oN8^VpyTj54<WArw-F?<|)JA5461ib@p0w0gw2_FwPMJK~e;b!O*xEXu`Iu$+vZjRmsH-}rGcf&2<6VYk#iEvBw9=Ijk3cVL@1-C};gImLG(TCu+@Tr97_UKI5YYFUiFzj>0=cMK42-xT5vQ#=h^Wi~g5j+SUh%SK#!UNF7@Bp|!x(MzM_d{QS`@wzDg>YZ^BJ^eWBDfFw65I#A5M2OY2=_)`gnPpmpfA7|z~`g$;q&2M=<{$d_&oGE_&oSr^jY{^xF`Ay+!OABJ`MMPyQA~q?(jM2Q}8)(H}pxk8+<l87d{*Aiar5%g}b1S!(HIB(8u7j;4{%j;WOdRXd&Dg?u0%9cY@DAABMelg#EL@o*Q0=z<&Mr>;4S19qil8q1_O;13CkqL3_^~-1o}UU7Ue-ge$va{@=Yn2t5$4;o@Ky)zNBjc^B^SnW})6gU@n(b#`$k+6g|{MOzoApeMndIe#a#Bb?1R%Au9vgBV*?v<h4m9*JH7kA&BvZ^CQgE$C)=3;ZGa0sJBSIl3MG9R42t4*nkAf&L5L0oTY%YxS%&`|#WbZ4I~Pb83TjfNStMR4DU#cs_~wJv1x*S^3Xw6nZ5*3SNh<hu6Vd(YN8P@JHy!@JH|$=$G&p@DJ#Z@DK1#^xyDK_>io$`mrCvHME7#;yya1%>CrK*xe}0UA&I2gdcRr9&j-OeF%Qs#iK4BLkr>iT-@v8esns#-tQ4ztV37BOI^I`q6l3Aui^Zw(UtJMjAJ_bAUuPyJ%T<AKLW2s--Oq~JJ5f@JK#Ui-{C*ttn9S<#L6N(S48)NE5cRLDsWZ!aP%<vaCith7#;#IMi;@0_?#A_#qi^N4)>S&JUlO9eurhJKP&&4twYzt>)@T}zu}$mZuC!hH=LcF)^gct_Tjk_S{becS3?hmtHCwVBjB3wP;?kPjBD|{p8Ke%%>Cr~M>n1?UHpK40k3qi)Wz#)5&Q#fR-#Mc?_F$n@g2GiUg6?Zj=#z=&m}Gvb9^z!R&Wk~t{;ga#`TViw_H3&czz1q3_k_WL$|>5;HS}d;iuu}3C|1A58)3v{{plK{*k$`Iavw&Ir*G<Sqd*fx5L}H-X+Y1&C_?x%L=a7U*`wti|}{MZ3(fB`P;_v#psK0a~BO<oPZt;d#wkb05?N(;AU`Bv@U!+dMx3&K3W&9>|!4m`=cq?>z}DK?++h<{s;Eq`9Sn9_@Jz`?n`*iLVX+0C8=}`&2scX*z0t7IqYj>dUVaou3qkc`o9kP`;Y$(AeHfdB&2^cvn;9X-~7z=6^fL4blulKJKY+XUHUL=<9A!B{{kJ$`C$'

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
