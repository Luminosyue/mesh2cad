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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ca86a57984f948e1b5c46a20c09a6223/part_002.stl', 'relative_path': 'ca86a57984f948e1b5c46a20c09a6223/part_002.stl', 'source_sha256': 'b5e05e77efc1f596a7674e8b76edb157eb939a6e8fbacf9df2677252f2981e44', 'input_faces': 384, 'input_vertices': 273, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3122107982635498, -0.13331465423107147, -0.4414409399032593], [0.2606462836265564, 0.1035989299416542, 0.43457111716270447]]}
GEOMETRY_BASE85 = 'c$}r02Y5|cyT^AV!3fcU@L@J$^iiTS?9od?)QOsdB%*~7Z3IV2j899VmvD5^qSs*SJxX+g6a7<zWX2%oX8qs4d-C1q-sic`y_sh{|KIta_q^*}Yp=a_F@9~GT|6}TE2Ujq^yvrBVw$E}Zp}j*6*N42K);|7KZXt)>!js_ul~O2+;&}j{kl16qqK450)s~M8(yxyUanzq-Ex)na=}A~hY#-)8ZdNtV36`#^cg%NDAOMi(q~vu=I8P?>UdYyy(?7K$Ls&czg((@rk|6KWQsK+c(qb<cE^*AGu0UOhxof@u2-t{PCcP~^Z7gY_9m@th+mO{cx_RN#8(Pi1$C(a-)waszVXAMb<j4)kViXsSNyB<mLpG(-O_K|P4SCVTZTOE*PMcX`KaU%(3YT{fC=!;TkGLle1do3`+SkeZ+$#Z>g?7PzUET{z7abWzIHZa5&F3qbOwI&Q21u-_yzbr!WX`^bARzW#jZqr+F_Z8gg#PFj!$c$$2!Tl(tB_|H=}-Im5<C%X+!*DIWRw3@@~m9s<HSBN=rR+3d?w#)P-;B9EN$*zIKsu9rTv@2|E{u-z{!|{MKyMq|VUSiTFP5s>J(yO8kdji}8I(F3I1sfXv&Yw4KN^!90$72IP}G0TmBH2d$QQ+wUrQl3yK$f2fL#EBwV({9fNO4|T47cp7;sJcV!1xQ_g0^fSrt^$5NhROblt-ODERU$`xKf~uI%6?<hp{BTPAPfzCKcPXck-|Bh*zNNH3;*FQnWxZA30AFviTJnq-jqzFs&y{}1UBUcl*K5kSip-JxDV0#a*`dHi#4n!)-!}1@<Z04g@>Ceb@n*!J-|+Mc==WNf<UbrB^Z!#_Ild+O!`Cw2VBU=Bi)5Y5X(@TuS>an}MN2)y#J43#zgnBxScm3?Ix?=Rwc(q|y3GG1FPVq%d`A(Vt2pAd@t#tT?G5HxD^*<Pxwf<P`&)wKDf3L`c}3b4_%EtQ!>>3&#`WeId~L@%_=bDfCB#pB0^jm7ROUbUcggecisU))Rp#e?Kjg8NTmj!qd?x*-ZIg9Uaw>fL<MlGnix$Z7EgCHSChnevJdZyo!Ow4jueW}?19=|$o`=7!tMogu{#N*v{iOamO{L!>x24~ucKBKY@r^>uWxUNENdDOkWL%HhZpZhv2O{2xt1t15yC)$2*kQ@vvxd~^(hKqC=s59bRuliyDa2b}K9hdkb*cYdP8=_z{4t3?UR>gf#BV~LywO;P#sp9ClRC-%mKG@Uxz$7bz6-a&ZxDlc%{RY{H+2Z+!5A4Ud799lUk`aq>munlLz8iBkK6<8)Kv06e0Lf7=QNstdSCavh2Qz#gKx}ugZ!FbAIzJv<+{Z0PYXwUMlHk}si)yvC(o8T$DK#KneC{=Z_5{f^&YZD@(<Y!-}3twIbQX8V!fGeaq#WuAILgc*G7&@a*V{6xi9PR*iRBaGfMKO#z>x~H6%WCsQ8n+Y(&0Y!RS}Z-c0<5J!V4n@mG*%R8#RAdJaOKpsP~n%|<e=+h60+|CKE=-VASvU;9YrA<gYJ;v!3lf2Y6z#Es7;{YJS<{V#S&{gyMBA4~1@OQ<jG3D&vxb_e3^i{6T#8Z6_A-6HXoW8fRDyKaUaAA$Pyxntm)p8c@T=$~}tu`CaOuch=t9{Ywf62G{o<caSk`_;yCH}QRL@wI=ok@5an5aY7-?kM>$`Xb&QGg9h2TvY1pI~)0RxBbX(E9)%z=j=wjEuy`|_j#8DKdSU$IUa}L>ysbBH^=Ukdj39+dUX9Jd~2ORnV%1ys7KFJ625*_=ErhqxQuH?Ve$7?lzQfWz6!s8A<6%+3dUu-Gfc+y<GYLK@0F*_Pm4h0v8Ue?e`rgo|J6&G&-d5iYo(9ix@lkTCH43x!?z^#kbb>iqF?*6)#87hgnh$Sa-_ujtdcyx?eRgL(kW6;%wqBF4P~Bl7MFQjF;o1sYn`yZbDx$x%Z9?YHu1zdx1_~Mo<=34{xM6pVcfY^!nbTHB7XR6>_7GeyCgpO<pt#5>W_WQ)?kn1_qq<>e$ZRiVeopH&&LTD<b3Rp`y##G3&~$|!v$HF7jZqZ#4kX+t@K3rX2<6nph+iXKBKEh{DS3jo_=@^-`4f}3o>7eP`@60R@O;NC#iE;W2^`JiB#!#*<a`3w=6FE@Y5GEZ*C{x+a_IJ1OHeJ8SnI!@U1ShQK!}X`x?fT6d-y0Q{mh8zJhNLEhK*1G#p30T|Jqf2k!7qb3g6}^t*pa{(cY7AwHlA)``Bt4&Q!ujQGdbBfq`FeChW@d-!IJJn;38Q{dZHH<I{}Tymf0)mQTS<$-TZl6d=sf80><mftR(g|CN--^x||^C@RAP7g2fd+oT6arHU`U&}iK>&=q19KJrN(rLsO7%@qGHVcouE9*oT|MY}N{Qhny`1a1PPoZBQSIJ|0eiM0y?ht=^e_79)FTuC`@bM)4<SKHX+1euU9d3#5zX0R4PHiLcBcGpuf1)#dTi?sK;P>4v{`-S+KI*&S+ssAq&1tO<NWHV9&by=GTdy5HAbEzs*9#YeZwcK6U)z;(2Y##6<H#R30r@Qj+e*LoYvM;f$8ooJuP*(DKbP|)J?$XApIqh+{B4KC&*&}dWUwoIJt9!92Q8!KVV<wM{EqMA0>nSLDpvX0^K$TQ!+hkrIJS}WdvxM$9EV@(NqmD%(r>MP@Xf`1PB>N!zPWD?`Zbrv%l+|#Y4B~%3&l^_h|ku+eZ{wWh(B;CK3guG+KcaF4Af&BnJe*b*JM7c{DFQAzp+xscw-;@4kac2Xj91(-%k8eGco_BZx7s;SeG_jhWVZR3BGZyp4_jTuDJx`>|I3iEW3f{4a3E{AM@~V@LlwqZ<YATZ{b@8v=x7GTX{ao^<4Zs2W4D!o6B?2;O>&A@-p!U)sy?enbW2J>LaAi=7r_{@0oo!j#G|mQqS!i@U_(bGLC#6@U7eO<9<lLJ4?n}I3D#_JD<h%+gzwgzj>yKzw`_CWo_aB#M@inLOs@z&%`gDCV77TD1PPI@b$7@E3wYrPeGm5Bm1zQS__8Quzs|);t#Kn=TdX=cc|ZbD~I^K7s_+~{3P5r>O<n-Ykvg7*Gu$*Z##8J{KPkSj?z2c!g#d~Ur>)WCt9Ab!h2(#*lU)=xU`^=^4xgiHsUSLm&G6K0pFU`PT~U-#Gn4pSmZf<VhxVRlrcCTwUI^eykX0kx*C3~Sn>ULg&^<L+c=*3(;VU(eH&w*PCUSPEg#-UoyJ%{=oC4QmhQ)--^-`rn}_?MPW$%!;+rWQalZcO4_`mAN_@Y8A&AdC4*l8&vYwCALa|=&y~lOR=(S1w2_I&o9`~y8SeJ=+<o<AF>lozm4%>j^cpy#uUbB`X&(<oke#^;ym$hU*j9+h>D9=aF(#8K=3%(ZSh2v$3Tq^6N{6g{5*2?i+BkN!Luok}IURUZYl~?X#uS~|g+qV3Mc>CPevOY^phi^UQF6&|DK$(ZJqc+0-(l$Zjn%+SDE&6Rjo%4dWLeo3LH_o_kN8H-t7?<VD>+A3vtlNQnP7$a_k9I+w#`llm8xKFqb^o51_z8n{V&1kd6#tS1`OTJ7;aiiF;amD{lk@t`cKEhQ8hoo6CUrh8yBqoHZIpiMHIw%vdv?LMH2qoXO6)4{ac+0qkI&&za@^y-$n*c5B?sX@zK;7ABe9I^hvDzU_icxL!ji2Sd`tR!@l(@fymtfTz14<Ji8${20^r-Mqr`vs2EMkjkmOl;3VF01Z%vG=Oa~kn<M-impS}E-WBC5auXv8L_D#X{)U<@aH%{)9{cm<PxnCa_CH|=ixQ{Z5e?h!8stn%iSi63f=k6+FaJ@6uRuVsAhV=X9D(*kbSJlM#^%dWLy7=4E@&3aS`$+oTQ(o?GO3Hf<OKi04-*X=$UT^$W-uFBTk>{PiBX7uYtRwGfnsmbcY6)Hm-?sX-yf3_;h<JO+f~ep4^Q*k)+vSA)(wgj!`y5+r!?T#5ztiCxE?)38=W6E=f3v#WC;QBh`=YhY;9G3H_u%)F-yJ}IE!&H~<0#gJ<%xa>{>EU*v-qm`c~|228Ovu#{H^22W1kc#$8~HBd|Q`Q@b#^q;aeZY!q@K=+>76J+63Rcl_vR@*s$Ll0m;e8A6XagOSC7w<vm07C-Ak1{_xGl>HF}x@j@IYTaTCWe&tF~G(PJ)FfKi#g1jei8-dT3uxn5)RNfyLA7{vOM|d6FuNocN!nb=|L>`OF&zJ|hR{(t5$VmL&zAP`+y{%yce7(h0j7#sf2j3f`BIUh>WfFY*kumUX>o>{!m7!5G4<Fr;$LN(Reh~}mu_c$mbBEcap1c<+S4*ywM`~P^^W|swcDGH~ca1y4F%L#Fd5@x<?1A;8?;S4V)t^Zok0|(-t>a|=%hE4;628s$2=(ZtzQ8xfcgFg(_bZQh-KQ3w<Mr%)<T=8aA?JC#ulVWR<vFpLn;iG#5P9#?z6r*qTO#Cn>d8oXkEPv%Z#J%c8S_zcl)QI2JyY^;m?e4ko02Ejez}i0R}1m>rzP+nMZZ`Q`<3>!J?6pEuM2!@nYwb`ea<1rW8Yx-wum7T|7UZ=Yf~o4`@;BKvOmmQj`w@ErW@gF{oWyucFkRmQ?X=;PfU{cOJ$eId%_I6^qaE{>a^Ye6X%U_`>Et{`9sdfn%=TLi#cN)*2WbjzTs>+UNdvRH+#m*yj2;D&$cA-jbAp&bLHJevaXA`$$TtLg>PT?7{0Y{Y54kUc@DK@|5euK$4JQ^H3R#kR`e_OP5ni*_&z7(y!%j9=55GUsWWUA)`NC(*6GH6|Mss+9etYTv=&g0T$=Ws=Ai}m$?{K1%2a>f^uPZnr2#enSO28sUAN}{_n(xGXV$PMvmIkoypOt#ypOz{x|Y11ypFn@ypFtrI-k6Pyns4~ynq}{{f!(=o=%-go=%RWP9R5;CsId|Cz3}~1IVMvfz&SKKyo)~3vxGdD{4)0D{_7659Ipf^3;;#^5jy~e~?R&OHhlDOOT6E3zCbG3sZBF3zNTNQ|v-@BD;{CsT$dt>`Ki>b|vSaW+&$$yHRtI-N>b>I$3FDa%plUYISlYaxH3GveHgurOn8-$PK7X$PLIpQ5%t!)+7H!u0yR$u0yU(ZA@0$kX)NwgKCg#kc(2wkc*NFu_^wZT9*7h*^63%>_sj|twJtGu1Kv$u1Ky*ZB4F9Zb|J(Zb|l|_96R`dsBy!dy|JyBgjL@<EWF!<H%O(G_sW(MV(EKBG01EBhMnwr7kAVB`>6|Brhb}sO!l#@&@Ww@&<AObvHSIyq9`}yq9cJPm@jZ8R{kS8S-W7b@FBMP3k@JP4a!JoqV61Lj4yxh5Uk=Mt(s~r+y`;lhr1mG@FyKYKmQ{E@W47cB&IOJK34~Src|9|IMcO3!CCkY>Gcp)$c#@v*NeZKQv*bFUfDo&!~^d&&bcIPsq>7@2IcIN>j;7KaiEaCo6qQen<Y6^C|mO`iQLbRhD{QWvTfU$EWm9veLga$JqbMGCzuQI*I0R5?1;hS!o`!QaAD^{_YFajjS}cljB$@{&tLV^SCK>cXAv@cOGY@`LZ1Md|Vew^JZBmdAW|1=E}0J6svWoG$YG8%-}jz`X<Y|eZzIF^kJ5DuJ}Inf#x_b6yK!Y(j4cJ;>*-z&2io-K0`gHInGnXCiR%+IIk7&rS8)l`+(vE>UPbsZz$eCU8gzr8O1j03eB-EDPBljpgHz2#dE3Anq%KnJc~MAbL^9fqo|RZV_#KlrB2iw`>^71)X|z_-&Q<?8mKw;dBwe{-89E_L9rjTmFBpPC~iruuQ{$eimOt~YmV!b;)>K#n&Y~rxE!^F=C}?j_M#ReD=n-!uAz#*U1t>+qJBqK>Y_QW(Tel1Db7uGCM$I%7ofURUCBywklo4osBYwZWKU{oveHUqPx6n{T4bdS$Ul<3sXvjG)*&mcO;%cith6ZEo1C9oh+K$sk)KU*UTSXgx4Fp6rr3k(PIl**J=hc%r+Sh-IiBKFZ?ZT0E>6u$_MocI!!lb~W*f<-cnme1taLazG_(CPvyEU=JeE!I4C*5C4Du4{YVs2D8aBn7sawdK$@{4X$ot8MsYl6YspqLj$>+%@*%T*I50DedJE>d9JINcVtH~S5anwcRIC3oYpX6BbWNIjRGC4T2waIKhXEtAIbF$KQWMA?xY>F+^U~({XTG$j1U{gGZP4Qsr2=ZX^KsLoe)Ujlx{m4P&UTlgxP<xO&ko~FM$^PWdnXN0eC$&4dC%HeH;=a@#<R0v=FPq|Dsbk4XXOMp-k7rXnle&aFlf0C=hP;%#icRq*>SppL@-FIr@-Ffr>S6LB@+r-+j!&^EPReY*XSO?;?Jo5;`7Zee^&0sG`3g0OoWz`0*c4x-o+n==U!<NSU!b0#o+O_jAEYLdmF^@TB=4YZB<~={Q{%|-<YjD%W2mv@81fYAWU|s=@)U9iwH-Nx>_cr%ZclAWZBF)U>y*vI`G5Lfq8)!$yd=o_KS=-AU;g`RudKi9nwjfAUxN9ybye>Pv}~FGsm(aQdTQ1F1GbYa=K'

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
