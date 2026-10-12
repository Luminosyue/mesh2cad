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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/58685e436e6242c188b95fcc2ba7c1d3/part_002.stl', 'relative_path': '58685e436e6242c188b95fcc2ba7c1d3/part_002.stl', 'source_sha256': 'df34461e68be42fa03928f5b18fb188dfcc1fb80c95f5e2a465dd26e76679257', 'input_faces': 842, 'input_vertices': 483, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10439977794885635, -0.16974887251853943, 0.005383400712162256], [0.17734427750110626, 0.28185075521469116, 0.14443150162696838]]}
GEOMETRY_BASE85 = 'c$}r23AjyF|Ht>q93?`A)J0qhQIe$G3dJ?tGNr;*?u`f;Q{<AFTO#w&y>iVBh~gR!nL|<Lp-Y3_=Dcr%>aBOJvp>Ie&iQTs=lMVHtLOK8KfcfM+iS1A_iz8sS?4JwIbZ%#p8uzkx9snXJ-cgpo{eH&DQ|FE|A9T9NE=YQPrsod@2ZGz|A<a&-M&>yr;s<;dp@yy+JGneCpJt-Y?R(0v1USIdf)y7`*-WpwQv9KY1VJnt@nU5;}7W3tzVk?d-Zw^ZmpScYmJ%-!xR3?KbM;+Wc{>$!xlT2?^1R|v~=T~#xZ{0x4xg0zAiV`PyOrS_Q?1Ne`d$}N%*NNJ8p{eAFbh!Pt3`R^%L+jCKT8l>xY{p9gO_Fa{PF&sqd$biy!aJSQ_!YQF9l>9Tz{V`<l4%8CQG~@$=3X8+<80p=X&{aq|(sagFe${G{Ar+akyR<~e_T4$g_JTh_FKIkA3{_<tYCjrB9y)`|EDnTgqPdGIqjY~K{?=e^RvU+1A07R35t{Dc+rH^=!ml=sJ%I2e~dV_Ad9{KNfJ9(-?Ed>$|Fe&4?$K2Nw;rl057SM%b=_xAmaa}~G5t-}v1{q_9HUw=0re7&AYQ{MFb^qiS-<MG3T8ieEg@cX{Mv2s@2JSSfCkK22ke|`6yTOaY;ZSdE5#J7uL{VefMpUsW+6N)#B_~EAevSNJ?KX3mJo8tUy8vFP8Re#Tq_4CU3e%`~!Hph*>aGQUB7K$IAgdgsp#^)R5`+qc?7dIY1VQli2SU;oI{J3>?>u_L!?@#VAGcNy!zMu8^U6FN8YSV1}rS5a_^?feBzRz7Ab)So`?{o3>eeUwB``L|G_p|fWeJj4cZ{2yR`_>&--M4PMx^LZhb>HT_*<fMhxT+3|uj{b*x(<u4>#*}x9Ts2LVexexcJowq*!ijsyW^@lEWWP8+Lt=)=A-Jc_TBxQy&*et{uc`P>-IoKPOP7VpHX#AZmgfNWqV{Dl1?997?%e>qxN?jV|`s$#m~Y|c(w1QSYOvqHy`n*#*f$coAcFu<>s&Io|`9rUS^ZcalWpHGS5lAAHJ?aIBtCD-+ljl{CvDJzsIeALYIkI5x?)3etpX~BPZ6+>*M=L6*6;U{nVo?{dL<{^YvIi2|sJ%mW{D~cx@@)zpl-~SU(FtBeTw?xbc;f{dty;AMaK1{nSbE<CCOLvi>fQs*~bpEI8n=XZ{zm;>P1=l_|G5F8|iTha!KUo;xcp4}QjrSBK;LqeUWq)_FA_d|Ch0`tK}=tf#8a;_Lb>zOK(MkE+kkSI?KrubwZLUp-$gk9xku*Y#g~UH_f0o=5TZ^XTTI-WM*9dS8gIpI>*r>iKnf)ceKdQSTR*M?LRup6dPL#;ZEu#;f;>^HqIt^HlZ0`Kms+`K$Wi#;f|^#;f{}SK+<+5nsRW@B{BV{J{GTKk&X2U%&701MfTh!23?-so!_v>-U`;SHJJ@1MfTKyZ4>UN5Ais@A~A!7yUk0t*7{UJ;m4SDZXA$=d1M;U$3Y5dOh7d)p|N#t*1M#T2JxydTL+R)6GY%r}kw%!)J&1&$p_d;_Lb;zOJ7xkE)-}SM}57SM}57SM}57QT0=NT|dRw_0##Peu}T_r<;$epDvH8pW^HK>CRWxPnSp4PnSp4PnSp4Pd86hKizm$Kizm$Kb^1Yr<<p$pUzkH)6HMiPd8rGPd8rG&+zb-{`FU%TgBI(TgBI(TgBI(Tb-}^H}Q4<Ccf_9#Mk|s%db8cyZq{Nu{&SY@453;{hrIOK1aLxsL#<Zzv>TN9@QT@Uw!U&`PJuc=c|5FeEoUc%}4c_?zrmnxXYvZPnSpapKd;?|8#j&|LJ_yf4cmt{|uKq8@c|0`iUQ?pZJ0LDS34L6kpd*$*=3D<k$66^62`BAE=-Bf%+-FuAlgU`YH3#^;7cb`iUQ?pK`vseo7u)KP8W@pOQz{PnoB#pE6$8PZ_W4r}(;l$~<-b6kpd*nZK@|GG5nD8L#SRMzyYyda3&*@pZo>zV4UA*Zq?7Rlg*@?w7>Z{gRuf>X)3a`XzT<)h~&!`z7s5zvSkl`X%kV`(bqX4VPL^@%4I&uh&z2y`Iij>nXloPx1A7x_PSgbiP_ocU-le;_LO)zO1L4k6KUdyMBIBCx3nPJ_3GV9|1qGk05#UK7#nFe!Bdse!Bdse!4uWeu^L1r@#;FQ;4tkDe!gubo0^s7m`QsU*HG!FXVhx{d9TszJ}z{`x=r*?`z0B^}dFT*ZUeWUhiv&ulF@%o~nL2U)4`He^o!-cvU~$c-?=l{K+4$`%nBp|A`;yKk)<or}(=6#1HhJ_<{ZtKhS?le%*gce%*h{`Re{t&R6%Jl3(|qG9TT4N`BpcN*>*Rim&@m$*=oQ@pb=+ALu`2KDz&u<LdrX^636k^636k=A-*h$)o#E@pb<x`Bnd!abSY~y`!q1;_Lb;zOJ7xkE)-}SM}57SM}57SM}57QT0=NT|dRw_0##Peu}T_r<;$epDvH8pW^HK>CRWxPnSp4PnSp4PnSp4Pd86hKizm$Kizm$Kb^1Yr<<p$pUzkH)6HMiPd8rGPd8rGPw((<-w%9W=lj9$>wG`>eVy+Izpuj&d|&7L!SCyQKlpte^9+1nhadR9j^hTtuk-!j_jU1p^!qyI6ZpO^-goQy+3_8hTu=PKdg2Gx6F;z?;_LOq53DDCU_E7?dOgM0>nX?8>xmy&PvyJyl=<lORKD9^NWbW>kKRAR59}Y|2lkI7kKR8LU+*7De!YJr`St#h<k9;__<{W+{J{Q^_<H{cKd^r!^U?c9l1J|!;Rp7Q<b3u1k>t_)N0LYHA4wj)e<btN`$sZf?;pu{y?-RW-anFg>ir|}_5P8}U+*8uc)fol<5m4k&1|+aGEViM;_LoXeBFPFulrButNv4b-G7R&`%m$8|LO9p{?p}G{ii!$)qlG4RsE;Suli3nAJu=l{Hp(Sc~t-DeAR!t{Hp(SzUn{4*ZrrPkLo|&aaI56@~HmP<x%~on~&;0T^`kcI$!mlF2CM?e`lJ1Kj`|2AE=-Bf%++Vbo~@x*H6i>>!;+`^;7cb`iUQ?pZJ0LDZZ|s_<{N<^U?KF^62`BAE=*lzPf%&9$h~rkFKARN7ql8r>>teUe`|<uj{Ayx_-($b^R1y*H4+huAeeq*H0O*>SxyNYkXh-?iWAsyI=gk?|$(Ezxx$m|Lzw*@Vj69!0&!#p89vc;_Ki2%5nAYe(?jp`&GXC-LK3?|L#}$k@ZZ8`xSWEqMu*(TcYRLDB_j!(!0g{1l*eTkLaa;0^YOU|LZ5<4eH(Uzy1U~znO!bdO`FWxFB2@y$&u67e%j!tzHgWEe~707A^|g9QO3fn5c?g4OfM$pe5ica3!=jTnSD<uY?oe$|i0=uR^bcFGD@_N-z4yatJLBhv0l@2{<2I0KFP602e~bz=hx<CMuY?!bC;17+eu9hZcd0@NdhZiLf1ClYAB68%;Do8=^JghH!ntat*X1T#?*0&_uXCS`STx>%q66RpDFUI%pNR4qO|p1lNXZp$Tv;_-3>+d^23vi(c=#gymb&YVfV_ZG`3OCd#6v(Q0sMxFmW5Z1pNw?x&Jyez+uD8Z8);vmnQ`S{Sx^Eo}8BxGY?qIa|F0y$QB@JG|H2tgB7DX<{lm16>WzfL|pnzinb4dH`JwTipwPU}BYtw@ge!r=zRjxh962m~A54#6lCB3Cm#<+f6Jrv74~G(!@Fw@0gfHSe}Begr~rh(WUTYcsyZw5xO1T&hZza3*qtTSacyg79N9U!(-ragyq*wY(Y1n*>E=JZ~35!wI)79*T5gbyU-QzF8F<P3H(01g;>Hd$DxzZCGaHpWpoAnGCUJq1J8tKqif;W@La<3yXZmqUHD@YpQ3r_K{yXSjeZE9hEJlq;FIui^nLg^d=%XRAB7L2o8ZIn5p*+r1U`m_;bZWLQ1sqCL0CS8?uJjnXF~q-V$Xj+ng{QP_n@cYJ@5|nB)kLOiXMlz!nx>CI2T@z9){P$8_*;026!WS4BiNDLr=il;GO6xcqhCUJp=EB51?n^1Moh=@;MWqpoh@2@FDmk^bCB4HU9`*30r*!{s=yVu8YaJj$?iTzh`0|ItN_`Tb%`GFm41o2Oa?rLubLm;OEdO@N@99=w$d=crZF19t;me$HD{Q0q7Wb06YjC2M>aWpp)Ps@KE$+cqsflIum{#egT~gTOAHtod#Q-4!;1~9Lr6-WMVNo5nc>up`+m}cmX;JUI5QWN5b>r*G%M~FQOyiLFfQ<WXu|lWQ|9XSJr$K*JKp)kZUxWYdD&D%Qc<IHJ`|N$~|D&-Xr$CZ11fZ=!j7C-EDa)It(7hznzLMho{2!{l6F8i7pRCpIOV>(8ZzXGj4e!niY!H1j`%H1)*pSvAiCgABxr-%em-lp=gb=yfx-}NKLc616>x1)<DZrCoR8W;uSO#T?S{u6VMzuhwC~a=6X*+hrkoyOmt{W&Y>LB>hrMG>9EyR@GI~e%-QOGbQNs%1Nc!B_n2smR)rhGRZQGu;tCTrOw=`Ti;32R<rK6YoC3E)8^G=0hY8D#Ox$RqnThIX6Sz8@fHr~?;A_za@U?JRv>sd*E`#0zmw`*8b>Y(RHH76`O|(H<p>^T9tcB%nCYqY)irxozg*&2m!X4qZ=<RS@xD9bT$GirufZh&QfUigIgs+Da(fi;;xCYu3t^wafSiT?a2Hy`qVWKbE5A6o`gP%sb!cW7!(2j5~xF^~c?g>AMwt=67)6iCM8k~-{hST95XbRi|ehO^|KLz(jABKCweM0`TW6!@c+7IpwcS4_rJHhSIUT}N(L9{3QAe@Xo2`9tN(KNU@+yYI9Tfi;R9&k(eA@nKuA-DtD8}0x<g7$$QfxDp3z+K?S2+RFVbVnaYpMf8TQ_((fAJ#k-Z3J6w0;j@{qs?M+HshGx;Rnzg;RoQFCayw@qc_6E;bLfYxEOpnngCx87e=pz3&RD`vT#8-KUxOP59dQm!};I>=rwQwxDZ+aE(8}ruZN4kMbSjKD10Sa1GahvY_$q(wJLliY;!a;ah-|!XnD9kTn8-$*MV!JCE?m|Ewlt&3%=RJZRpi#3Ag~74=oY1h9y|z66BRNFUd72$vos5mEszfV%~C1%X7`kbDnY!Shn}b4I%&Ds)iPatHG7gVsJ73ZDq6}Y{%bAz8m1AkpFyH?SkGLiavvu<vF!{H(Cv@M((@OhVUb32ee@*S_dpYgw_v5>xSi)Xq`~B&RA}N)(%DMlI7-Ttx&X%Sx!c84n^yp<p*P~x710??a@0z(Yk6`YOm$HOjJTEqIbX*;d1D0u+^(!xu43Rh2U~<MYKpv&LSMsYEjr~RoLo1a3%OI=4`bydJk;%QTS`me4aFMz{F~F9eM~}2fssD{>a3)==bO$*y`8tHzp36_|U`}bS-)i&NVUL#Cj83O>8r9hOnGx;&T(bO?*XI-e=;7iBC+tM_7Iv-3Px7uS9plE8(St<?ZO_@aG(VJGu>CiY`XC!HeM>bSs<#FCi?yZ{kz*G`bbu%K2OV$;4q3KcFAOKfveF58(6gXXq~YGx$?t7sp(Ju0VIeE8w@#58$`pchQgGcj5KuVR${9OISXN{sbR||7qfH)NW+_6JItqEdLwt2l(IcALx1b5BMVb8GI4`75x<c75*7L4gU=Pf}VkYfqz5u;NRfiz39FBJ7M`x^egyJ_%F|YUhMgQhuU-gj=x*}2WrpxAB5#E&_CcW;IrsO_$+)9{S`h5A4h+NkHaU>U*Hq)DfBn^6nqZ-9X<ztiT(+H34e|L1%C~HkA^}%e-GQ*^DTUtiGO*%UO+?e1;+e{+FU=9^DEfuKG^Cf@Q?5X^oSSDY58A-<zpr`q8rd7u+{hAEXKWtZh&8d=b`Vx^WZt?+wdHC7P=Ci1<yd2!ZYAk(Z%qq@H8|Bo(4}xm%!8Endl05COjK`3!V+nMc;+z!VA##u+{mn)itoyweSMi=GbfEO%prO<?v28j4p!1@Md%&ycynvX2Y9c`x}5A=<8@UJRO~eX2+~yHfx+sURm>nT$6>&L$1*xuHho)E!T88*L*qWDffV7dym-na+c@6tF6A~Mc>_)SEKXbdHmbe=w5g=Y~TN1qhF$Xz34M*`5d~_i$3F)PoZHiS`#dvKsS5Q8e;i4y2*>y9Lp!sEnc)nSw0(cJ*1{t{sP_OMQfmCsgsuXn^=Xuf$o9dfR~{=;2m7oWnT1pFGFX-%iuTA*)ch1b4;sqVXJFls|Vp#@P6iO^*i(+Z1o%Xc@vMD=!QN7cY_}^(a}Ux6YWiOGVzFsK7{3d=wom{cp%yZ9tb~6SWY$3!9===c4&9F9h`!u!YOcTv<uuCZizkyw}e}ukH9V9=4dClIh;&be$+%?^l7vc+=;cYJkms(i4o`%@CbMa+7%uG4?sJ^1K_?yXO5YSwn96@t>89jSGWz_7JUM43%5tp;P!Aw!t#^oNcc(kMH4ThQ_zv{6gU$d0cXOK&>`?7cmg^Ao&b+S`@-YkG3e9q7<eq&2ObNLNBhC!;fd%#cp^L*eHNY!zvTJPjy?b3=oEN3JQU4@hr)x<N$?=}8FT{t4BQJH2ls+|qGRBm@Kfkm_$jzIIv(x~_eUqf{o%prWOy+A9QqRc9Q*?M3j6{*jIcb_#AtLB`U*S>&Ol#+Ut-NO&{WuJcQ^wcg{H^kOy`)R;T~uQxCi{Oi3ia8(GKwaa1*p0+yuTCO@Z%)lhD?15_~t>622R5gtmYi!FQs~;XC2G&}8^7xG~xaZVcapwt??~??c<d_rcB3_OR8au+;})s}I4=V4EW)Idoa6eE-+~IyU;p?)iCf|07xbFXMl182c{^*7l-5K1@k2V1H-iU1t8X56~U<YI*+w7I4YJ'

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
