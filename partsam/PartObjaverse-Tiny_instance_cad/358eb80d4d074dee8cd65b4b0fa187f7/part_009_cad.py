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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/358eb80d4d074dee8cd65b4b0fa187f7/part_009.stl', 'relative_path': '358eb80d4d074dee8cd65b4b0fa187f7/part_009.stl', 'source_sha256': '6db15980bb9092a39d7e8646db9e67ea69125ab111888c3ea6325785f9b9f9df', 'input_faces': 520, 'input_vertices': 420, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.25631409883499146, -0.31443729996681213, -0.2757352888584137], [0.24444223940372467, 0.34600064158439636, 0.288348913192749]]}
GEOMETRY_BASE85 = 'c$}r23!F_=`^VQo31Kh_6OK`alDk6VokOm<4f2+2XN;l2xQs}-ZI|TEAjDw1=6<JPs@d-M%pjp;m+GYp-FPFf-nG{ATf4QF`S<yM{(qm(^ZEVO_dMrW&t7NmJ!hZ2E523Ue36X)RbUBqFSl}I7!&a@i)6!+QeR6>Od3*cz@Rq*EJAYePwAYto!Z2A4zOWtL`<)wA&IFm4T3STz3atP4aW2ynEG03!hlx>ruIq_yjep3AxWGMc{O2B5+7HtQ>#YRVC^bZgQJ4~$A1NR3!x!>va`54+wUEY6Z-WVA7<skt@Lj1#%VnG_WW!)9?*MDRxaEwe0h}^hgZ)$C12nE`3YHP@7!5BcY>FQmp-)3$Mc*xDf?O7d55pg0OG8`j0uvDZz;J|V(1>px5Vb?oJA53Eq&&&>`&zvC+=>he8m~+1XX^iQj!OUSETKVxVBo1-TWmee@?wjy}rrA@1{6nY%4ySxT<gR5b}dxN6@?t!!+;7A6EPLLvtl}22WY#;}eM6yIaxc((Crea(fpar*%lVx;0MYYzc98)^TKCDnA_@`HC~tanDe`UFBQKpRsJWzW$1{nZ(ulgj#GRUL<MH-*Io<3eF>5>i6Ax|B74Ss()u)H1XS+ay_kieb#4boZTVrre5D7>nM)=F!F7qj;-=n7N`6(?P(p#RHr_{E%0DW*9~$%RQxn?2l-*6j>-@A{qv;cFP8s6@^0yS<8t9vxh6+-Ze@3poP9F?SZ>_i`c011Wblqu$L&h>O&&shkDv0_H@SoQq4rtS=i2Z0=<BJt1+LaV^vxE^A3t`tzMhI(;NE&hq!Z8EE>mA0ldJVnoV6O4srPSkwLYw{bt1Rp&f_@lTpV{EH;%jTh2g}F^M><6Kyr0Hba6gZ+&mw8+&CY4b#Okka6Sw@IOw?4Mr9q}@nvue$Cu(3xUD`fa0lE`pBFf5Ogxy=aBprrymq-<f2Qh(h^zCh;tsevADUd92NY*UpUm7Y^vR6vV(8Q4A)`-kd&gd<<E2><nzvTpESZP%o8lI@cm6lHT4%3LZQ`nbFCSd3vzK3oxLRkEt9AD3sQhv0f8f#sa($lNb6oa+@!a?<o%aC$VbBhpJLT8Xez-8O%g2kYlbj7|nIgx7DoO6fSCIR;HTyf-&o>4S=*N+Z<H+MUj#w%kM;^y<<f`MSdD`CG>UbP=f~ezhv(AL6dvohE^j7h`xvh`KjrCF7Tpy2{>ytMyU#ju_%H-<%mEz|2E0e45SI)p6MoWJA@pH1ys#Q6;aR>XS;$d*MkoHfLI}7l46Wj(552pR|KAuhcr^)R#w0|n@g1c>BJ1u#Gv8l4pdpACj`Ko_|d;Nol!M*+s?)49DtNN;cldJv>?yCO5T{Ukz>fbFnJvA<u{!Om>SKRF1<f?zg&HnG>=-=e3f5q?X|ApU2$K|sBnB40h+}wXm?)49D?mzc&)xW{j{-e0L|AY#CJ6rZy==-yB-lWi`ERBa(61Pq?ULg06Keo-4`NjH3Zg&{EKThK|xMMH*Q09%CJ72zjyE*Z$EjQ}i?%YChR(|RP*;n*Yc^tbFC&_gV-Jy9Ew^tFj@5ISI!;$kA$@=T_QGN>g0S|5fKS%w9-g$kAeE*zpsGoz>kK*pH#I3{AWIxXB2wT=``PLb!r55hY(zv^pcxdZ6y6$k#QvRJ};@ua~`4!wQ(pPdjsUUriN{nAF>)ebyE03Gj+vRnL$*n$fPv|@}U<duZZ{yEb+(o|Ab-)U}4qJ2kl+Nv=cVvDTJUnq6<zI=W_4(@EojMOUsYvTHkG9vDQgfxuYqaR7+;36~X6xLVewpfn+x?qK?#|6m`%hn5AH{=fi3crOpU`KWeD$qI*3xw>xT<f1yTcQy{-CIX`udn$txst1*i~}7P9z-kt;4nVCAU8;?^`#M2M6x(@z9h4M{=v9xP^RY;o|pXKmFJF<~6y>4?VwZo#esk`}OTIx!Nv!>z?&;-jQea`}(PUX@l&4VwVGd$Gv&e$8D3xXZ`&Cc@3`SwK^8vF8kTl);F(pwyNaeGGG2JSM!G7K1X#T8p-cr&ebos=-eI;-X%6o&R;RlPFd&fV)|Y*DSz8Ioj<ii^6-(n^89K2-g_q<FXvCmI=9Mf^zp|oNNzo_jIKMscygE2CIuvSi_SW%^H8UPRA<EXeRABazU09xQFNZY*I4$cxclg1l3S^++%EUh3gVYGQU8@s({&Yi@H%n3OSc1ZY)8K@w<l*ZeIHAR+Ng88@)WA`9Q7aGP+#)U@;x6*-XcOCj~?%yDY^5`Cv-h<ppWFiZo}!iu2k(daT<505D%CCL#}6V)fJjIHk$f*lGexL2Z)E}(fU{q=F5<E&s9Gy=gWFo_M><(a=1L+!zRznL&p)gQ|%F|gZ$w6XdhSkA#ipeHY2zF(Bx`A3}$wc+^&}@`*c&gWb52LR4XSpZe6%5`(Z=;+_^dGu#Y$Gl9Ai-!YcRm&Ff5kJX`0gzH4x={xtAL*D`WDeogM3H&TC*JoM>J+Rq!%exkUOc1v<L0{hA02j%YzcEic^`^A`S`W?>T)=k=P?as0C_YV8BklZdS&mgJ~?#xci$(7^$ZyQ{l{~d64INo1Bs)3Jte@6`N{T%@hU+heE8qBBjREGnnbnaYgCV&61!R_lk{rT@t^Kma9JQ(*j&0DZO<;_3j<E+T4lR6J|oaN8IJHyAle8p2UY2Lm!sh`h}`1!`G^m&7aCm!(UH%jw!l@D&;yF<UPrN&a-rq5>UoK3J#=ElvxJ0@4hoqaMOzpq)(kEV6$8I$ef+j>xaa3}pC$=M9*&sh`c=jii3jy_H9_G#tg!GdLd^+UHaPWd?MhfR+9CRg=6UZsWP&b1WzyJk4EmYg@#u)U943m>C(D3C(@=|1wjZ5;{h^YJOf+4;uX<@@5M(f42D`+yUj?yJuR){*tyXIA;=y<CpgA?gJ2VzKgfv(S;&^7!`nlf<2-?;VkR|JNVt`-v5fr8?kheH0JP{@(YwTcfJ_IX-vA!wJ9mJ{NYNw4Y<%pvf_>$<^ngxIH=FN51+s_Mh@`Ro~>QzQMiv;4C(ZxbeNt<m&v)>=qyC$0_^j!YLoeaT){<?r87JcavB6Ir3Rw@G~PNSLc~v%;!F?&NGUKt4{Lev(2k~T;(h7KD$nGb)IDXzwmK&o(zJs*4usg;hfbzuJSE#_t--D`<?l{+T`jy!`7Xq-}{~@LidBLCfj{{6LB^wk37D@cT3Xmo+%yZcYLc0eXmqJoj9wMM!!$@f0X#vpXmEl$u>DYeiYoL<HgBoM!(M**BvHT*By$R*BvHT+iT74M869g*E{Zyi|F@d^Sa64-gV_m7m1tKmEh)er8DXV^|Ssr+RnyR_xX7Lo08lAsw?|t*}u~7$jhe7-w(qxXq^=g{Y>1-nMuDRZV&F&`%%}?CRf+diksKbCRf|*y2pvT)#<vlGWGBAWi^POr2eg)HRShP=WrML{pGiza{D|!tgGaqKMKfkcv>y_yM^=8M~7tIJN1s}oR!WZ{!=xX&n6~Pe%%PU4sN9aetwQP+cHen2@P8&d8m6Y)E}|H#}9(1?V;<S8%5;zwa~QN@_T$}3-zP8)8>xk;X>8rymtA1#6Pb<pKqmGALu-EJz8?swci@~z6+y>PhCR4-;SVp6?f8>67N4!_UT@kcu?}>YO+t(ZZiFy0uOB`9&CB#nB1>!EG9nU9R2>-?cel02HctUDe*%ovY+7d8S?$kLsw|t0M%DK)B$|cSF%34=hC_~kCOdb$@^)&!C5?U_umd(w{<Tr=d*g`$oa#a_WC#*Mm)50AJzG3|1s(#o9@d@*_@_xrzr98q3LuzJM{wb5wFs5^H~CY&jq(G5D$(C$lux7jQ`Mi%9%uU+T^ACJK$E?$#mamU83yIE>xKMGVbFjZr;Z+xw?<z)iLhlc=^VC953Ivk7IImAIGa>-pA=Rh`4bdO>y%+n#t9DG{w#PXo{Qn(Y$$$`)DRt_tCt0jr(Z9B!7MHc?^TAbynQGFR8eBUs7@NzNE?3ItQIwG;hR2x}HzmnWl5AEb(ycOuAq2T|v696IGVZQ;lf<bbhQRxznQ|<zJ=!Q1Q?Q#97l`H1EK4x?gMDzc#sde;?eue{FJg|Jqr*nYeL3U2*e%dT>h?<s0|w6*uqKJ4gN`ZahC=a`pUx$BpL)Os<|EU`L6Y&p()4t&ig7^A9Fh>l4mfg045r=P|&|=P_)9d(V5QI!3-#pd#fP&yy&A-}58}SI?^`Za%MKCC?*nJP)I|`8*6OyoK_O=WR@`&JW>9-%=gpc^<{h=Xsocw<+IvUPy8Cc_FqR`Ns1|ikr_Pg?pEv-)oHLrcAD$o3a!)p35@1_gukOE$Mes<9RT}?|U9h<r~kNDeimTEZ+BYVA(!Rmb#_*6g&#BNY*<+e>AWZr76w*(ZJ+7|Eos>>;C^A4g8k(a6v2s^ep^I9-nAqp;w@vz<(_EUmmBR%iuqTe#+w;9#?sM4gDAVH+cOjLio?1r{F(>&*8BOx(s>>Ud+1^ekJl0{}^l~d^YqPd^Y?=^mP%vT?GFc`JZazbLjn?wtbHW7<-II8ANn|*bn@*-+26j_>K{Kg1=UQM|niW0I~1+Yd3iOh`7dx1yL^=Q7%BN0<;{WJlIc|=R3r8M(hUkI^svLvY5XjA}T<vEWFqTp}$~zennr`5I=+c3NO||Xc=u?enxH-=1^-Q{CCjufxmhd{yJ)i_eDd0WPh!L@a3S_;jiPp!WZC?kH=j`Q4H)MXfedYV0obrBW^Nc`S6+;-$X4{SB!5X{=jRI{Ix&1MnM077a@ER=xzAhs8a-Uh`EcPH&L%7lm*BaL4Og@Vu8Qv3m*wB2`}dQ6TSV3I>L)JD9+<Qj3S@5K85jGagB*JxW(wT!Wzqm8n+ONiJYQ5O5pW-JnkTFVa`YKdLD%EDo<!pj7y+aVf0WGdIvs$IUa$Ez8^t;iNIfDp^rjKzy~n5cwZjOCwvU|m3Y+TQH@7+9yOpf;cFsC_}}?^{*Ctu6<ql3+;8KNf!9UeY3LdF)9~*@GvG7uUg0<K*vP2fMsVTR@mR}a1Gvar58VL20XgfT>F{;2ZO=e!z&`_D3t9=j7JPoF*q;0t3x6KlcpCmZ{4VJG@Vnr*Lbt(hg<k{R2)_n?F?2ordTh&LY>VjoIfU>H5yIDo)`G7MUkaKZz7+iD*fy~Z!Y|;l5c8$OFGegxk3v^#J+H<#3Eix1<7TXZ&>iqQFwZXNdH6HfS2CbtpUQyNgs+MHQh1^3ke`A5W4pGmY=Ulpe-3LDixB=F2;u8MYs1%pFAXgPUmE@rBNf|l2_gJW9`Ev4gtc4%zYwtq>m>9&_|@>6p<CcL!|#CZgx`s|gnyU!uz*K@Xg~PzJjU@zf%b=gi^l{W1E4AJZ!^+~&=mL-yjOS;!oS5Rgr5NI2QNbS@m!a2wRyY>?E^2=V&sL6g<s4gokueCRd}HyCmA{pekzYCJo-YD;f0EvzR>aT<I!7Rgzz&E!q4O}P;5VsRy>}DRz(Q^0(1cUQ_v?7!ncGDfEStqFSI}WqtHhX!nc6-hZoupz5+Ce5WYFIAN&*0#}UFe;}HQZiV(gjk3!Ib2;rL`gntzwd@{5dd@_7rXmj}H=tp?*FAtAi(BANUc;w}g1P#Cs<R;8x1#~|AARY-kmO|fw7dhfRbD>M%2lMF3V>)yUd;)5XhE9V|<&nrE4LTOSCu&*HS@4N?&ur*I_#r%c@mK_%qj~Y#o6w2yuklC{#~*Zr=EZ9xp_AZeW3D;SMeuK;<_PH9@FVfwQP9co)3GMgprhfJVr`c|=fbbRXR#bQ4?YcRH4AFNkHkDl(BAMu$1w6jN5j8~etSWa;Dw5uUeHnSv$5TY&|dIDMNT4gB)o<GdO{Q7g^HY>Sc5UxN5<gw1gwEri!d|+eje816=)cKI3s-n8ip4k{F~4OcoD*nfcAv%iQa@S&7%zy7u%%&fREzQmPZk29DHHql!3N^ugRkwkBZO`d^Fx$1KJk8I*)iB<)Mw>%i+D%pzYuzk@FZd9=<G(_B={L8^c$EuLW%nUz<k<9x>48;VZ+}fp&mbb3{T*!mC=9pfT{`J#|q}Xcc(17B!(Y;MJN&LCe64&)^|^K0-^ut2L?)tp-1c$6y|<k=q*irQzE^2g3_Z)jq#Am^TW(Ei@Hg=n(DmYm5GC!ncDC(LS?w=&d@u`pn|7mSy49XVV^QSsPw`1|6`Lb>TZAgnu0&{4i*H_+juvq4DrT;a`KcgKvlah3~}UWgh=T2;UVUd}oC4T@b>*gb@Bk9uF|_pSd#jAVT;O2;qw%gfET|K0iYEd^{3(^yKjhv<JM<Ztz08!wXG>e+53w<2fF&JnBR1!3%u`Ug)#%LL0)@hi@R(ho3{9;_))Hf##pYSZICC{}W@OFKNCL#+^{(CB)0fc^Nf?FC@;1eEz4QD>Oe3W1-76Uob#pp;a|s2xFm7!&il0j=C#QYd?>vJX~m+=BHpRbe851U@Y`Y&F{x}KWco5aFOGphVYGf4-VI+&=Z=^!dU2W%{L0rSZFiNH^x|KQ}|}^$5HnLYIWzniTIlXeL?fjV=T0#=6hf)^bO5-$GAIcynz^woZ+Y;d}kibc?^ZN)qD$#g|^Xr7mS4t(|l))JEO)h#8Bi6MGfIw^Z1Z&cL(S}&3}Zk&_kMU6`--u_L^^vvCt0i?cooh?m^Vb<T0JcQRp1aPs3Q~Y|VdwvCw0h&%`(rHI5;UBIhV-2)~=hBp&;qGc`XMW1%xNzXxNXdo{ls<K3vS7qJgH`%pvp2l%$X!?g-@spjWmEOd$H9}Lh~Xl2bmfU(dj@Ri}0pzc!CYRCOyt{tIYX#NPsLN9ARK0srkFKWIW#zH&7zX*RBb-zHZuH4t-@j5i5`DZZ}8mIYg7{|8?<cZAtKmD&0{`x1rgEHU$NWpxk|F(+$&T{<AiFcDFzSRTbZxp|v$|JuZ)Ndq4{{@P`@b~'

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
