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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3b204e1c8fa34183821cf925128f545c/part_002.stl', 'relative_path': '3b204e1c8fa34183821cf925128f545c/part_002.stl', 'source_sha256': 'eb63ad0e464a1139f287d49ae42769b9b54254aa42753426554de809bf3f93d0', 'input_faces': 496, 'input_vertices': 265, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08204291015863419, 0.2965364456176758, -0.1481403410434723], [0.08751332759857178, 0.4999971389770508, 0.04811269789934158]]}
GEOMETRY_BASE85 = 'c$}r12XswYxW`Y5-pOdATw?Uzqux=2Acz*h4T%Y2L?Y2S1`#EC7hD9<lhFz8=siJ@QLo+!qE3c)_xJzj-Q=zJ)_Uu`JL_Bj-~F#`pKpJApMCbZS>xHk$=OB2r;MiMu*UT&rfDj2Yc5)tfAGk`1N}p){~k2PLCY_``lRc^PTf0t_IA+1v~d;u{6hu?S7>CY&}2}<3RMji1`Q7$8SMLe|KY)Y{>pFT8yMnm^FsoBgZypZE7q=Gud1O=rK*MrhX3Oyr!58Zac$30l}q%|d(CZP@OXjmEg$X{4Y(q{)pA#S!{Vjz$FC9JTq10*`fi%2!=L>|d`om9`nfR(zK;?8Oz=CPzFStehd<g2?IXI1ueUeA5A+aUTi!r?<F1#x#BUWMzW$^J+Uuv_?@vJfMUKWv`;Q0VKl>oQY1*&I(|rs4@ej~Xcs$xW`@>J{jq3*I+Mmg<xe<9DE%c}QZVnj$->^b_qxW;P-{1k?{a>_icmn-9Rfb>A1^KL=b4c>(Q4D@S7WjR3$4mc%zRPvAszu?at%M&H4d1IFuAAg1zG>3}_^&?0zh6|oTg!*S{}PXW&hFhO^*`+ce^DUnkgKrdV~A@FKYL5~xg8`wOCPI@LrZ;mSLzc};Gm4F`wsYt3F4ck_BbNGn>mxO+0vAJ=7+;y^gw+5;cD>>{e9slM`N87_<}mussrD}8RI(DUE1p*j_?iL;J=BI^`O;%8;d$rM*WZMKP>s*KLI~&8}jVjSk{>(Yzlm{AMz<t`!D(aM2BCqv-s8l?+#`17xh9vl?GWPe^Vg*_|f7UD;T67%iz-R=dDEhCm*D}R^`RcjPq+OQd;t{K8c2JI*9gNvRII3ApH2F$Y-gK<fDhy%IvQ@79;&6XMvw|ReVcWg7}6kUw2>~Y8Y>WddFnGz9ztL;sQU;AilX=1bn~OcclMaWA|k8BbMU2^%`%Me1diOxnD_p%fx|F2lMI>_-P+dpWDTxz2@i+-{OXTvc5t6D|g;5YVDG#ZpI!hwrA|e5Oh)cF-5w<zkOP+tL;9Ad9UaK-+dtJ@UflbZ#*_<8|qdM;|-a(Me=_$8NSCI=|{hK3U&BpApHC(@YlzQZ*BE{E7n_KjO)f2)N@rb{E<fZb6q4K<DFXYQ=)O*W`*Rt)i)RXh*Rj_ln?z(DkphqvDKu#dD%j#kM;b0)Nk7wjJH)I$<H`q8vH1aJGgE+x!<*h)!`e`;J5rF{p&4Cz_;c_eG>19udO&8gL$uu{EKcxK9^(Q8;ipKvJZ7h90vc<dFkJf{hI8z#=>Veiog2>uDjh&`mwZ#haa;N>nin#+}D;sH~7gN(SM!$SP#DW;m7)*{n&A`ZuE+&8*tr%Xus;A>_4VX)1pxa6Y8A*GV+g_06%*$_NCPaQHPH0;on|__A@49ek<pM?-_nu+Q*byE$!dGUN64OD)>cvif=ry1ir^v@y-1^t`UFoSonqk;_K%7=%?7hb;u_f{frMYOZ%MGwYVR9BF}$(kbkda__=eTpCZ3Wd&|=`@V)-TJl;;0x*1QcU_Xb^|K!E89~rmjf$z6OeA7P>^4%B^Dg9~AMNsDrE3vO`E(70V3FdKg2|ULOhpowY-&r<o!2XsC<JPiIz9rYabwv8tT{QSb8zaxgmC(NJ$5o;wiby_|vzMeUmO)eDTW@h(L6|SsvG7NpLw&Y}W8IE7!OxzC_PgEC-v9Xu@kgJ$DSol0G9SiecbALbY6$Z5tt0cTTX!zQeNzt4kz+BaXOa2v$6vyF^Q??{nK@|@*7-j8YeTSK)o_K+=ZIm{C+z3-O$$-y@{*6iDIDwgwiEo6Pm+(`@_{@D^--w{#Q!oC^LYG(_{O>~;LpA${b(gS;Xaw=4L^VJzoj2j4EoK|27W{X`1MlYFU|wMYAF2k#THBdF(LEOe`>O<lL4h<JeCdr&J#avA=<~USt5C+4TEp4g>%&DG^v}O(hC0Q0ytMV*2X@Nr3`#O2h_Q0Tg=zJH<75@N$e++TjO~*bpd?K63NF}qmtyQMJCL~{f>RlTs#HsvmS!Kt()X&e3Vt@PcIri1MA8k&)*+9@_hVpy7-9&k!QZ|@aJC-7e6SUT-P{ev5Z&yy$}3=Wbw6^0a#C^E5eU&hx5$caG7`gbcw0R^99yz@0{p==^Y*OJM@Os*{eD7^tuY)uRZ$z_XE~(#qXnWKd#04d9fe+_>CH2$TLO8YdX~w{`)H<MbEU9{tW?-G2b_J_#RQ$rG4>8%tzeBAW=OT?Jx7b3Rp8t)a&W>O!?&O87TU!H_wM7<Xoz)emq1pa3S6oygFe&e=#9I^wluT`^FXUZ(j5hJ<$>Kvi$;lkNX2Kk4>?z=33!9zw{M#>45%+AAtX0IQ+VM<bJXK^&IaN(d$g8C(bjLe6<f_zFmDpef(uyX6HE6p-BU8QP0At&*jH+Fi*zbSkE7>Nqru5fbZqlQ*_ZTjBD0X>~Gex?L`~bkbDgHYUBM#Z(mu)!}ku;;bO>Nzfo8GR$b(}`nV3fpFg)2KQ&ygs}FFUi*a=uB))cCeAD$!Xn&&W5b@1Fk|dw`r_ny*Ng(>!A@ghTJc9kb{kIX~kMx&*tRZ=^KlE}97XM6MjH^u{)UA;oB7TWOlBXqM8us_8VIy(fP`R%5x*zJ9@-$Swr#Vai<{>83&6sVJ_>Z<rd*il*S>k*5hQEIX`k7D#e$B|y^8NNptdkpYsB`ruW5xF?i2i$gME-j{;d|}CKD_xh^3NVLPJI0$o(tyOI4|b?JQ4jwBxTC;*v?7f^Zi%bUl#MVue6T&s)joMatL{5?FQfCB)<NsF#P^I;iq=NI;>)l^OBaU`DF1uHeHo@yp|hviy99<{dwVhALp(`&HoTTq7>>@XA<&ESqVS+DeCj?KI${eaf<l)k4XQP+K-S=X(RlKv&1(#8sXn7GgbWE=W&0P%8&8BY7hTeD#lgfIQHRur{D+FL;r4N&`-BS_~t{I>(=ip{MmV>y?IMr?8}exOcTH6b@*{Tux^Kzh0pVnxxbFOg?4~%{7KqtqnpnZf5j>IBfnjdJddo1$mF}5(0{W$cuoX=3m5;wKhoZ4sW&T=?^g@`mrX$blU%2x|3tZuG`9;l&$+jN|LPIi59xz-`1d6ENoM?B(QGBw;iMxo#Ls<D+Uqk<^11l)Eb&wNiEo&53-jwX5PteT9Gex_b^HT<Y%W><#y1C+ivQp}{4>p@A8XE{c#gjPd3MI}nn$dHANdFTBq!u^D`a*iKfoRPRnDPu-qxH;&Jn+EKb%`$y}^53H&6H#FQE>dN@8F7+YkP{0(h@^l7M*}yKk=e@!pcZ<w{{ZPe0e5hxHSK^*Q>R)Kg#W0soaZ#`Pu%b&CjspI8X%^XH1F|M{`-OEkf}YcuC&^0zgY=d4~Q3(kQHm&3Q_LLK@%k@kAiO7n4D{N7^yoDX&AUwwYY^>1yOUCvK>yRPtKcjLOl%Ss*eAwA){pT~TK4#x8|(g(iRc<d)X`QjY8!x#Rx^0>cTjWS+6dIx--Z>{H^<NfI5F8Jl9BY(qNoacJIgKyf%bADraPt>QDULgLLFuAT_vzx3ReR#_S8SgL4hH9u=Qdju%%3}Z7?vHti8Ua7HGWIc^EA(?~;4k}({oL3L=ct88;P3x|b>6Qw`f1~^Q2d7NWStv)nnX$au9e|?4wL&%f6zzH^SYNA{=A)7pWDyKyy&4D;MZJ_>lW{b{i@_q_`5ITd|T!w=6&)d_V0-2V4@l4u@lMgQ-5F|yE_W=Ua!C+`R+3n&x=>3q<?+xF!=EW@Lto#3BLy|cnDvAf^%leW61N<d-yRsagO@tk9i69S}fmB+~DtW_i^2c6X3@Vz&=p$BkJQG1wSSd=Yjr_SXYDB!oSc~>SnY~!*hS`f+d)D7wN}%y#o4)x4_TcSI(2xMaS`;a`z<s(M6<gmbyl~Cl7a8Dt^)z+`oBppr1Wc;0Mmc{t%l(>Yz8tyA1Qb9rHWo49*XFQTXZaO|HqP!xZP`xUaY3J?J0)9#^;pd_#WRk2kO5caO1M;Gfwc`CHZv!28kbAMhK-;#@txKE`#b&Pvp63EHQ4qkYhE_(_FP|DC1e_g;O3Ta@@Nf8o6^hY|knmh?;E{ixPk>0h@5!Z&%te_LAm*B^|4&-0-vd^YOyW(E9|thi5KUdMQ|zJ~v*mGq<aFNuDJq`~j?6?F?~Bl&1M$FCAU{k`L>H}d@YY_)uU=7{&Kav#wDXv-R`w>9{k!SjjumWw6Ln6I1g15?p{vI#za_pp>oL;C`*8?fF|u)j?$hJ9zh?<Uc-K3KOa%j0<v?G-EP{2k}g0$Y(^sh~K~i0yd)N*IT6w)t%@*5_6Djn>69_ssNHnb5$wftDh+u56J*bI}I*X84ngGSw$t|NB4546ggX`jbpuxBCCzKgmqA<uJ$=o2YZio5)wGf0D0~-%_uU|DnF4UL(IFAET}z&!di|t|5;l`%!0-{m8wjA>>}<*3=&4*5o?WX5>2LGSsT%GUOuE(&QrKTnxp9sZGg+$@Qqc$@R!xZ4pczMeR)<MIJ}(Paa49gX&K{KwU=lCo7#uUPeAl-9$c2zC*oAzC(UZeM?TC*Vhci9~p`r91x1X(0fPzLcU8qMoypmy9~waY!N{Xqs}9Tkq1!6k_V8xQ2oeV$gQZo$gRkYsjbP4$<?WK$koYZsb$Dz$wjF}$VJKdsJY1b$XOYR9jS%Mj^y0bdgR>XYSgaeYUIwEeQkASC=RrRPF+9^CNCf_qK+ajA}^<oBQGa!r2aupUyF+OQZ3X2WDEHML-A?qGP2Uc<kRHq)H~$s<onduWThX;_sP#~kwX1S{YX}-*6UY(SM0=4{DYoayFVC;pHlCVpOSY{*O7OUr)%~#J)NOAh#E!?BKM^ZAonG=qjn*;BR8kEA~z@3r#2?nCs(FcCs!sLsAb6paxrRAaxrp#YCdv)vNJU+*_o_S9X0z$adv8Ma&~e>YBh32vIn&@*@HZo8b}^Yj@0b;KqNzP6m<bPiX2T{M2;qJr7kCLCGVhaB&Xj4I~a<0*&>#@o4S|0oBS8mLjH?<gL;8{gZwu`@fGT6@)hzWhT<gZb#fB<7WF>)7WpCdIr$;^jb^{E-Y^vZOZ`e#s_rGlEo{-p7A9LvrjDofA&)1Iw#7(lcWNJUcXA_Y3vwg!&$e)({z7d*{)OC@Y9hBK2V}@EfT4J?EsjvPQzw(RlUGy6lUI|MP)C!OkQZhc=R$_!`L>uu9Y!5V9!B=0b|-t1Yf~GMYm*C6e<l|q=g3g691O*I7>a+gMJZ}YstehLH7&_dT$kFGT$k)c4Iq1wCr}rYCy@7NsQZ3~;#0ObOFcn7LO#OzIKfbSh`O45h#bdI97A0~jv=q5E+nrdub|E+uOQFLFn_Zciic8%k%y8yQ9a3>$Tg_7$u-D%sfEaS$xhT9WG8YqY94YnazW}(<bvc98RokLLvcA<)TEZDmLiuYSD=<8m*m`6U?^@$^&+<<|3;la{*7#=?kAhc=c%X2=gEnheSIWSFOw6=x2ZSDx5+OUil5oyCG{TlCixyYnR=O=OirMlB`1*2P*0GR9wMJ1$5Z3T@#H-W#apN`<Spd&)V1XG<dxJF<dx*v)LG=&<RR3d<RRpa)K27%<Vw^U<Vxh6)V$=JWCyAf*@2venvI-=T!31TT!37hT7q1h>`E<1b|qKQ?CZD+LvaIJ7^w}ZHOURhwW#IEwa9MN3S^}%$!_GH)ZfTG$up>C@(l8E>Ur{UvXz=hwvt~_Z<Ak<Q>ib=N}rKa$)7a)TK~jQ{7u6%Tj?9>OU?eQSNxEAPqUv56yKsIYxc8*;v{N<W<Pr<zC=AkzCt}mJwrZ6K1z)zA0_Xj?ji3Z?_wxUKaVNiO5LK_&vJ^Rsp~cS*-vp4b){xMD=Lnp&erT_OT~k!Lp1wYRIvxOqh>$5Dy~Saq}k89inCL5YWB0SVvXvc**}V%saZ7p*;{dbY5~oDR##k%T3oZA?G+oSuA2Q_KyhVi70v$cptwG@fo6Z#P~2Rz-(%_TCW_U&OJ8bxs*&8D{42E~`B!oiYAtdTvOCp{th6WDojig%gFJ$~fqI<0f&7SSB|jp+r@kV;C#O+U$x1(w)5vOqlzvN}GzYMwgZ<uf<hfa$pB)*BztdCiqTd;cA5))_ACtFHcapb}!>QBB;pE}eAo6gs54A73FXzdJp|}I}S8@k(8)_4B8?ramo$Su}@Mb8ULft@~LOw}-L_SG=LVZtuLjFKaBd4+UANXDIXR0IFk@fz}Q2c=UnEZgenYxWUl{$^Ojl7Mup2kr8J9RkucXB_f57~z`?Z;5ujoOCXjXaR*P4;H(1~L>crJf`&B_E_dAs-}Pq<$cOU|lX!ACNDSS5Y^U)9bQ|p*WN}jXaIx4`nF!rS>ED<2Zd8ipNj~k_U1;W2gtoW5{!;7s(fy(;R9jIh5B>oZYq_ve_c5Eu5)YsM*M#9UL58oc^c(CBy#FW#i8HKWO~df0_Bu1{we55?f#Y`9}oL4q4>46-V2D>PDHbc0lbv0H%qx6#'

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
