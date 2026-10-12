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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/78c7c67eae00428b9bc50c288776c75b/part_010.stl', 'relative_path': '78c7c67eae00428b9bc50c288776c75b/part_010.stl', 'source_sha256': '00d0d3476890ab3374875fc86310c500c98751e511c1c7f9bd2f7a7d05d78b43', 'input_faces': 472, 'input_vertices': 264, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.020721301436424255, 0.040491700172424316, -0.15183258056640625], [0.13608628511428833, 0.09572261571884155, -0.08722284436225891]]}
GEOMETRY_BASE85 = 'c$}r133N?oxQ2Iv7%oDapvFUMR&$A<J%$oO1W_}`kQh=#k|LxW5%UycrW`TFJjWPz%+x#;HAHC<V~r^-H{bWZr*iJPcdfhbjrFbP+3(u<_rL%B@4f$XvIP2P$?9d`r=(G<e%`0n&kRE<x8Y?B2@a3!*DE-p^1!etHzS|s^5bNDK)aTK9o>u}#)z`LgClx{m-V%jtry}`wvwf6$e{4Z@E!xZ4+`%cEP0b2-$w*z<Pm*)gav18m#bc@W+h9F@|7$<TK<nexug$oYR}#;Y&jt5n+%xIb$04@uNCpiE1sHL&)?rA+xCYiW@w&k=61<bE05cwd2BP}Z+&%t+qDx(x?TFvbY(+#-QQ}xwHL?xb*i#bvgVE-{Bhh0<tHoc{jq<Se7kkKe{SSeD{s^GtK`|I+X>N=l<SNgk{g|8WB&&C#w(jdY?a(@4cV{Tbt93leXs3UA8gb98&U0%dk@q8TNVySKigD~#c}d#J7&A8XeZD0G0JMIH8)n>Lp~{COy={lAI*n;X77jGKU9xvIpLA4+lwy!sI>f|xiNSE+9|XMdB4Tze`_DK^GSK+tH)^jW@*nIx*hj4T6yQ*W*yJ1jZNL|**;1+z5}jT^BoxH^R<U5>n+rAvwilJUSDH(=n$pHG;POTstVev+~NmiwokWcUTY-s3AS)$t#aB<YD^7`XUyZl%HeNty=G3rbqSvphVzKjcC3j#alTJFA$P><`C9#2qy09IgOxX9^tw1=zrwiH+|Wz8VzRcMdan+ySH6ih<+$dXbbN+iL_5RYw^A;1*WB@7pKD%Yt&Wf7+FguuKKG`|oUyvU;g&5$w{6S5QJ(!2<LvKey5zq<K>ugVK|hTMALaL+dcMZ3tJvT0%&tuRpyOuWum{&M@qU2r*X;<d%i;03E@9Tznm-A`yegX?`K;${H7|D<^LbK5wEr?k7tP&^X@4Arj^VtH{n|_O?hUkk$MjjaUT0H!qy6q1^|%Gjpq<M#gEfC}8{<6iF0SJfqmSkb=3_hy`D1*HPJJ~`-?v_wHw1ZwQK7mW(?fIX{YJ<GmJih29=bu>=`#*_owZ@OuSR43H$R2`?7fTp>lr#9jE6}W=hOAWb^Fdh++RsMFdteEMZP?%j=!a^fp*%bA>Y<l`(tTe8OI%v6sfsy2^|MV`a<M+s|?kA)-F7kmPTUU&ghH$^HbVS%iNq8=a!ae%||@cd6F6(h;}ZXMD9KZ<JNty_Q!5|+cn>RO#5#x9gO_Q1mv@<JN3A$PGO$-9YEf|!1WDisQs}|DKuJhKA$a9;&gv|5uX^%-&fOdw!bc+{jo0|jJ$Y&_Q#&KAN{;@6nRt@J+4tA5%VqBZH#VvJzJyuzt4L>^ZUNYOP$o*TzfsmB_9^8{c%2L>>E!YPw-r)`N2|XXYf7b&rYvZ_MVP@`V5WL?X=%8f2!xv{q3WzV>KT-9M9pm1+f44t;n0-)$zBEsgLX4>@4!%hGYJJavJZi`1#{BkI0E}D^(hKlK(`_+nm>S%(x{fF8Pduct1L?``78n5B!Yz<MS5RaYD)@&H22tb}ou}d-b2mng?~l{nD^E+Fvqtif&g;bQ#Zo^ZsSfe%W#uhZV+D&Bxx*{u>)EVSYY4j(l33)q33RO%Ax^Z7*WnzOtkLuj@_I?V_pcaR2p3`#U-!f7VpnvG*O1{Ov~MXXk4_jep|Nezogyy4`fN&L6Yodd$P;>Bx6p!+XJ8f$>QXouPTV%XqKV>8ATz3(rM<H4EnXqn$Xf5i5`%YO3u!x=z-4WnI>2rsk#3U|q4_3;C4y$oX6~*PO%kt=20(^Zc={Z?EHQUOpP1`MTTP?U+BiJ!fgo^@;sX18v9JJreni>{y4S7sPn3u0LD1FXY7gXxitvj{Q3!Pv5NVTXMd1%{e}HZ~tWUCt!}|0R!=T{$()6zjjyTT&J0N?_zwSw<14T6xV&UpYCs7PeH!!-YRV;&m-5|y|`X?N6bO(k9F})<X`8)`Xn$J=k?(c@=n{e9s9mb=#QCmuI9yC>2WOy>1hAAnsYPX*OnG%u>XgM`M4in;JN*HyN<Kfj6>e5BA%;0|LA#H=SMBnJna&$ONZ5_OU~<P`VPT(mMpVK^Qmogp4e~i)OD#PBpP|~zL=j|w(7db@?bmiq`P=t9T}nfTTlLj{KFDGuI-Hl^Zd))KVkl_!gcw!bBaqI?v3_ych-4g#!p3V&8^of)vLZ9*PL%G*4*!%KA&x6*7N?#i+pF0j+^<Dp}D1~FY-5yF`xYp>pXGX_-=9Ld2Y;!)c&W&>_Oh9MWW7!MPm=R<Q<xz{aV=$y5w9B+v^3nwlkm@)_YmIBhU5<dA>(0wf_y$4!GojX;|kB?5gMM2+6Vp_irW4pSaQoUGg~z+E24XRn2Wj^DoJK-x&uBCA;K9-S8atKBVgtvzb5gB};H$j48X*C6DvNxbgFj)gJ56{EHy0E2ga3?~?Doi2fhTitE^5De^fR@xCsRr1ypG&^1Tq<Jz}v*Zx>aKS0iPmoel#`ni7gQr-3_iSevG1n-5j=2Dk=Qo&nui$~oA%(s;|ucCGEe5lc4ndXnW;q%Lr8t8xTw#YXP#=52bTJ5LVISu)NeOO<0ErRFp-gM+O%V7UqJMi2a>AhU@#2h&8>KodQ^*|`{!Z+}q-Ev&_H^)psKC&<FU%tmJX*pMDzTiu}U+iaMaGw^=kNid?+TnZ39yl4frK{c-sl#sJz8gIgdC`t|?@aj;`Rv=sAGOANvvotAKjy2a$VXn*`DuM<V*eevb=#OXPv>Fks!-kE;#Uf}ZK?jA_0Z?8d59M{qO<14tu@$g{tWN;ZysX&J+~m|y3zT$%uN4Yk7xMK$9rU6c8q_a@>ur-^uV}z48`*;sy6b0lkmQ%_b1v}*c18UpYXm2&ZXm-`YsIld2emUHZ>7>z%t~{^)}bHHtSL3)k<NVv$>UykE8lS<ROVz{}*hIe!j?#^#MOu8iy8Po{TMqJn%bx{+o~LYCE<jzQ{cm>N>|9{HNyDRes3%xyH=b1?~Se9C^%19e=aPG3;L<26@<MwBI}k*SE+@<U{_@d1p;8>6%+#;5t|bA@^U8{50m5S>QW7f7(>l^EZlh!n(-!2knm|tp@UyqwwB|_ygxVrZ)1gmg4;w-AZ$te?#PDnqxhgCm7f3&bP=<SJ3e{KTO1WV?;CL?OS6$Oj)J-Th;|4=ep56?uqLd*%>+C??!x)11|aMzwtTUHc$6=T<V8BEF1bC<b&%wU;y&CM2tiE<+xs_M{LeKp8vkb-^U>L8j8<Nh0Y<LGj4O{@wC6Jfcxd>)XgsApZ2Y5zNt5^<CMyp+h04jWxnrHLr3DgrY%Qaxgz#o{siMt2J_Mg+N1rn`(43#jZfnB=&0>j`s6<7l22=j`S1MPx-%L1dX5L@vuVfYF{Ah~?Z5LqWskbH&1IhRy=lF6ANk!unCD#+(4Sm*E*L)faDSb9pW>3|`wQO>cn4uVjKcfI$Q7l>HD8p+dw<if$P?dTU3Y92o~wShkngUCaho>{_e+C6k(W8UA@jVoUVVxDc@nNyt0TDX=RNRw?~A&4FGpX-aepp^e8@{2ciL(^KMz$vzU~9&L$OB4lj|YhgL!RDS&8-J6=RR)dk^CISAH4BAx946{QPL^Rus>rbDtm|-V5_*K~Bs!x5CJC6w>!dY8~9C_MYXC|GfzNvp=abs~|TD>$<}JdrOQ@XJ6!TNjNS)huUM?BIk3`3^<H=(j*M|R@`UyJvDG%-FEENe9bVdZ@G>&OI$?WI82Z0C{ZWHB`?}X`)~C4ME6hK^Z>bgJ{=$D=S|1zcgW}9{a`J=591T=k&GPcC0pb@w4aa%c~C>N^XXO0lM7zR52au}<nM~}I_!hIMR&}9=l4{XXYAAMVI%Z;>HL1la%LHFuYNdgwcHqoKC6%?{ety>xddF7xf_r#ADNi>zWX=-?zrx6i|UB}9NUik`FV^F*E5D~7xME3v_H=8ZOmO)kw0nYGSBVdQ}=7W?KZA&kp_64XIX}PW_^60aBzvXZ|l7o`G!|G-?6)J9sk~j{EwS>-hP;X_Fo-A9#TrLi;dq?S@)eoo+H;9mv)M$A~!bbd0AKVMLVOOAU|0I-#0oxkH@w&F`nJDKjzz6+E24kC*<|KF+bbX!f~$+LH<QEe6JF;9p4Lm9gVzHTRmUrde2N4jhxRzbJNfJFi$2RUx4?geb93pcVRs8&^-7&8@m^I(pluzD9vr9*6F&`+W0B*aX0b2ojncf<m=Co2i?Xxuu?&7$KvjtqPg>P?)WXbzr9H)@(uU3ed~~p$@>Fc{`wN()oh!iK*k|5DyQLPg!IVtrxyw3$I1WxPcQvy{;&S@QnPmT|L>n(KFR1q7P)=MZ1m4a4>B7)8&A`NbfXL1=^pf4EOAdVD_xkK?n%$j5-&{Vrk5fMkh$r?ob&?pPg&vx$vkvn5qd%T7cB8QEb(eA@p5E7x-c)j9NoeaFG~IgU6_L|EJQC#uRwa!E6~f3rRinp4aj=*2K26EN4hYQ-j)6XOFWhwNf*Y@W9gGv;uFcybm0*CMEY=+csH^$UHCP<8@(}Emfo0NiS(j7=cRZJvKaXpUFbm<=AsKd>BZ=uv&74j`RT&K^z!tYEOB4s<Gd9AhO9`Iq6-VqE7D7_#EX-k(uD=-#pxwk;$M<q(1msALMy!%*_5=>za!g_R=SnH--adLf+g-pR-+5c(f#OkS>m-x3td>0UYlN>tU#|$Z^;sGPL`ny8_<Pa>CNfgS>jRT4|HKHJ&HbsB|e>;L>Eq^Pp3~~iBBMh(}msW6X-oz;{Ie~y08-6Ij8+u;;mTXK4dYv@N>GbJl%(0pC#UmtVtL8(wor(SmJ@k$2lFy5^q9Qqzk{IH=$P{E7FA}=)&UkD)h=M@v3A=y6{W7b52(!o6@V&zh#McFh0)p4lMD3Eb&2P8~Px6AF>6#4?URlqX*M%WL>(A-ifSD??i7)R;LSF()*IV$d+_rbGooQT^L30MgNf{9!E~03#ZfL=rdX3GstOl;RN~&`goRj2-%Y^^rs73(Z46#k*(-LAG)wUy&b&^*^J(W-h&LF_n`MC1L?i#p&8YWY)uBzg-z%KxL*+2n%<iG1hK>$kyYqp`1@m7;{93T?a3f|dwN5%5xo)HY)Dq73#-zF-_nI0=nd)4_B-(S!hxCkGmw20j-y}7sN)%RnI(RbC4PuJNEdFWAEIw#i95&ydIFE*Aji=clXh|(eH{B|CkN4medu=j2$uLzGMFy3(TCC_SmI%1C%UjL-FZ)jvBW2nz39Rp>B2brWO_VHd@ebYE}TK1OP|FOpGuCW3q$D6`)Vpnd@$LLF6=@V_Mi`@hqJ_ok-h1{Q2H=>G)sJx@$tSIMGl|~$IzFMOUW^G;aIvbfiB!mUrOJ~5>Fuy(uK$ADfDA3@eAZ7`UUz;@-kg`i!QuRze#_<5`UUe=^6D`Mm-~+(w}mlXDso1Eb&zG7X22Foyrpbg(ZH9JV_TGqMxE4W{Gbhx6y?Tx^OXlBe{rNOc&be!Vz@gQ2HYJLYDY^GJ-A)qtB<$At%%4(3g|(bm3h3a{3CE_%d=9T{xA#j6RzjOrK4kM~2gd!|3zq3s~Ymk<oPFD7tfgi*Fz|lS}BrrF7v|x-f;lnQpSgkC4ac!VB~x^m8onYZ-Ny{DUQaoxDI7-lSir|3N;;^t<AZ$)|MTU-ZZHH$1NV&J*%6{R#ag`G)>C`JQ}3f5SH4v&7xpP~sn$rPKc*Uz6!{;WPSc`g8Ig{W(32Or@vMZ?nX&kiXD{r|4Jcr&;0$$isBu7P|A^6W>p+B{$NAi|E3Ibm4sZTKa01cp^E6E?iDeq_1a*Zz5OFh0Exh=<8VGE6Le(;XL|E`YM+A8gc<$_!HfE&xr3PlgSNq;bywfqzjMGlj%oU;^)b8bm2AndHSy`@jJ%H`{xcz{1N$tE__LUM1RE+moLGb^IKf_o-QSx)eR-?LCXC0;5`4p+=HIY4JGdG_Ho{e3t!Wv#NV>SUy#q~!Zi8|`a_oZZ{%&d@CyAm`c;<r8S*q;c!2Jl-{NP<edK<+a4lW9nl4PF@1yT!iSHrT(}kPpd+57Z;ycN8bm2<+PI?kcd<VITE?h%*&R6lD$rI#mx-gk8JW3ayr=Or-WQpG(f29lW&~MOxXNmtwKBE6ge@DKe3uXSj<F<GfmUwnDD?KacpLn3Zo4Z$*|LMOLeEhLX8!rFR;J^N+>(}C$e{*C;TmODZ9_XJ<zgu?C_$M#wj`C^8_)kkTS)u'

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
