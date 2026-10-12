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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7c6ac3a8aa4b472fbc31ed8cf50703d2/part_010.stl', 'relative_path': '7c6ac3a8aa4b472fbc31ed8cf50703d2/part_010.stl', 'source_sha256': '642cdfa7beb0e6112629ecb4ae5dd475d1c1d47c24f1c7cae46c8a03419e4c1f', 'input_faces': 374, 'input_vertices': 269, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.34233954548835754, 0.21519500017166138, -0.29832151532173157], [-0.31112799048423767, 0.32659876346588135, 0.2741560637950897]]}
GEOMETRY_BASE85 = 'c$}r03s_BA|HpR;2^EuZ8#<U*k;_O-5f0-vA~mMue$vHdNQx$uHpVc+FjF#$$uV-93{uLJbh;|t#k|ICPK;<6w{gGqw%6}_&bwCs|NnXZ&->=t&-c^kS^f6fd#}CD+WYWuYhq?2(N8xiD0*G9lN}{V*;+|9QdmI9vITwtq5Xn_SC~lF%qu^JjB)px<T1@e3X@jZ`3Hphh1d;I*|`Qf+x1b|1uh9$7UCN;XGw^Efa1scE(#53@S*d4g993Vw|5-u(nmG0S07cR>OcIkXy}6KkJ}frmA)LcDjU%dvcv0h*__v<UaMBT`d)CAl3Mu+^Xe-jSbL4NWpy^^b*2fdz2^KRYF~Mo>bG$$Wj^&ft8ehS@jcHoU%i&K*QcFiUNbv`)mNpor~1vv>pW&r{aH>_A6~KzqdJejWM1Q)&b<C;W{L8<uKj(sU(JCv)PDb)bL@CK_>{B#Jd^3T){bUg-#j&+_fm5&=GAuJ7w}%SYaa8e&EFLAUancmye8zUGeRA^E#y0HEE3wsWHPT)>(2`P`S}|2(v9P#yw?x7Py4O^x=g6k+mf9hDY|Ec;1k|sUM{Q={oLMkeOtLz@?Mwd$h>}f6!~%JPl_2kU+V6cX`I08BKFexY#LuIwEuo6?YC1ptE1l@Mf(jdVExcc)}6@aymaXn^E&I7DZJM$vtoa*-sq6bd)0wMG;W$Z{KD6lJc?-?JYIQ<_o~ltFt1MgAe;BPt1oFhIiAxA{e0Y(9hdfyMXul{*wZ-iw#^gvTj5OC#p$KswZSLY_>>OMr~TBfrt@R3W#dzunMd~pyguwa^ZHJgt9Y+7dBwb@tE=GEj)U3wkbAAJ6x#0zVqV+w>k8g$Cv0I}|6OLeP$w>z###7^GTuwQ>#4qWL@Dp(4vuX6X$K7~5&TUJjZ0s%v%FU=s$}Cw3U$vB_UrdPyYAAXiKm7Bhs+><b8)87pA}1K{Iqt;5b6ZG&^S|D{Ur3q$D4UMx<#VUzAl>DyS@EJ@ZF9wFZD`aDEP=r%<EK_HVfDB#8dL#4)MH~BCKe9ZtwRa?=_A+X&l^ryr1{-#-Yqh_I^o1{eB)aZoT4<@?O`&pXy7s$wK>%;ne=SJ1IhY%gyBNny0bzHyHi2&0^O}@(3!*=Dgba74zzAzZUXdzSNanM{UHN0^aM)M$`PT{eHgCerPPsv!kx$@?Odfr}O4)8qd6+3!R_-L+HL6;Lqk^gO~Fsl7Bj*fcLs-b7=mI@Gj)NdUpu5Z#we~@1-#t$bYw}NT}0NOa9NKVxdk!4$a%<K_x<e>MH4e&v7Xg>a^C={1En1^p75rcfM67)NfW#^Zdkwa-se&7BoLUva1m4xV0tUf2-it!#mUb@BW77`4nfm-*bo3bs1Jn^R~gaIKtX#Pt8r^z3QC`=Jg|gO69%eYs#*d_U*l7-fQZTX<RvM$>8@ZYf6~c*$>X*y>#X}jdPn_*+Toin1}179Nw#|E$RF_Smz4uldiCNRol;n?gLZux-$v%xqojPJ6?lVrByL6M;))?y<uKeC$<;7dg(x#Kjqn#yqD#L<Y#_bA+#^vNb{usrgGj(;iqZ7-RxP$d+os&<e%A=3iX%U)BIV{xkRXc-HYbiH_wWN{%0Pe_Q#eK3GMIRq5HR{rjYk~FH1HaWZyRhLLI#m^Sal~1TTB9qx(JSZLZ*ZX3>1Ej?Ce`W|k$5zbSdAh5C!e(6}0ZKU3&u^-LPaOHX77bzb+T^~bQXB;h(bjiY(H<Gp>t`TT1>&GXY*CkW@i-8!1jXHAU}+V4uB_W2K@g#PR(qV<M*@mhXdH7ty2zPh5{#(VAH*W?ol5`^}DwPoW{wX1caFg~O0$X5p(<h|_dO7~0nn!~);M^2{p<!;A#ug;rG?PrWVF4R96#=N}PGgau%o*26CzVJ*JypJu-djU1M!hTEo(tNdQFRf=b*PUnmT)T<xmn|`Lf5EE<<S?(YO|Ig-D)LWS&wTW*;B|Mq)BRF8tCIK9>uGdf?DVYQy=HVc^SZqo%Z2tahnZKGx|i`@Z+eq?>BBCiLi<L~JI4N0yu-XMs8fmHR}E)g-}QB|aJ*h|<OeJ-66)7pp!+WGb|LSzlb_RmKQa@%w6Y7$&#PM%@Ln$RWL`h1MChmV;4^C9*DO!)x_xw?=B&*T&i~Zs)IPT4v`{~=Kizkmo@EMk%Er<<JS8hb@cwbktB1}?6RykR4CdwfJ*mR+Mm!{csy10TZ!c`c``S2uT*dp^aQ@?G)8~%2X@cO}(E33&ePWDoTyZgUzaQBVCDf12qWjdh<vM;mOJ%>&JWy*A%X{68hvW~|Ch%SrZ%+5o-X4j(*N^Bz_v6J?2Zj4(&;Yt0r5_Fp`*j#Yb)u&o6WRy+kk@-37up9dqUV|cb5e!=xPL{Tzvgq(g*w|02%pPF-#Ul-GjCuP@72pLQvW}R%jUiI(tX<R?s^^XHL@8!7hAN-75dq<9X$_@zAE|^J!qX1ze}7?uJosQ=IHEv!RL&mb)Ah@fpA^CKc)8ZlM99Ofah_;de3-WMn=$npM)0)b<AU_|L!M?h5d%4Q~z78C=t%X_CjjkWK^k8C*uP7=k<cu@4iL-d{I{>wD)^L^$+hZ7xrt{gw}7vJu8IcI%F=a_l)g#wjqDyt>6vsZM5zoRYLo>wc>i|-JR5a;~qNBgjkwq;H4cG>G`yON)_+r8zwa08rDmO_J2Fm{QSY3O5UqYgT?g{yx}?2xL$(SduLFc_Tgo`SG9O0u9pn`!Fowb?p`AFC&!b{d$;Ci1wSN-=J_XUiv(Xn>vCzs(?Z_soGfUabHG~g(wzRZUaIL(ARO<YC|X~AYn><be_uL12mNDfj?muKg67GcHK&E+avMq4)yn*ou;1f8G;ceXX9#uLG@*4%WL>gwK6mz_c`yHVl5kwrV`zTc(_%mGHN$8frS|KWAoM474b8)I7sm+4<@y8FS!gK>{`ML2-oLLE#@mt`RR7wYZM-+EqtuC)6L_z8Z7a^VhB{bB8RuI=Kk*!GoNo<vu#S?Z%sj?>!#c`1-x}(h(>h9b+&@+D529&aE%s06z2P}Xd*|B>p+AP_Ab<NT-W#8Twr<K6+DE>i{%1Yc3H`)#kW|+^SEz&ao2sc^@c(1|78p<GxzY2W(c^hgdOatN_v+9}8i(?MRNfn&)Ahl=`FwrZhMv>qzdZ^Be`q$%=b2Lq1wTrBE;jDB(Q~oEtIoEf_lj31SMa{^bFr~bqvv8{`x#f+d???i@uE$OBR_m8^{1!i4DaPX*3&%yZe)?*lM<+(R++`Tm)g;L1O4XJCA?R=(0c><{jsG&oms!r`SCHK=ec!Ls7_TH>!-SmKL7RSKA}2|-p3kz<M+Kr-{^g>!8d;2Ypmb+{cU&hs-f0&J|o@f{Xt%58gGr>x2ya*(Ku=JKHuPF?Mzljmo<o<Z{SrG^gdr-u!+_kA3tM%r>k-jzDH2SJ!M{Y9ZAo{I{H3BfBOlw$M+HHSbBeE^!VOEo4A3l`=CGRdxj-#h35jz`Z{Wl&r{iIdDRFH;ai_$>mPJ6Z!1a4)<Uw80)4r!d=#nt81jGr%4dPo|LZHCfgd{kw_o`*HEHN%!**JtYz0=*0<2^+u#&GOVkMt|mCOb!ISZ`h`(P!_!Adp-H%B(XrmzXJDR_3n_I1Oy7MsF4rM(Gpa}(MWZfQcB!saHlDQwn|Z}7K&VpI4#YzlvhP2u*+IZ^%&znkF_e~mN+E7=VEMZ>mU87J5j_C<aP_65&HZUD~(`yn@i{lNanufYD`0OTfc05}l285{_nhx`US4?G{a1w0?T0J#;s0K5?SEqEdLGh{UQGw>p040sWEF>)JtF*pbr3l0J=L2d^x0S6<$2M2?_kUPL$U~gm`*c&_*84sQcUW(iaUJ4FD?gEE^Ly<p#L&3|C3E*Ym<;dOO<=`-+790lt9JvSlIXE2oBRCwq0=XBw0=yEL2wn+Zh1>^T1&%=O2S<P-kq5w$;MK^3;ML$L<RNer*a!I&*atifnFO8&o{l^Wo(`UY{24q0JQH~YJQFM<kAh|J8sstX8t_<TGI%U_9P&7L9C$o31w0=7F)|hWF?a&<1b7124VeaZ15ZSzgC~L~Ay0xQf!&e6fZf59ks090U=L&_*aPg@uzi9&h0Fw>0{@Lo;YY{}@FVa;<S*cd;0MT);0NGW$aL^4@JnPG_$BxS@&xz=_&G8a{2crYnF4+Weu_K}ehR*iOa|Wv-$Nb)-vj@JJPQ5`T!%aYt^?mj{tUhizJ)vtz6GvDCV^|gH<3SqZ-W0o9s>UXzJWXlz5%|DJOI89u0iex*MRlNePBKKcVr^?ckngjUhp;WRpgK0tKcihJ>V<g%SbKwGWZg5H~13xH)I0%H}FN|58#X7e<F8*{|WvTxfA>=_yRH>d;xqO83#TOu14+vSA*{&zX#t1-$8B%-vOUP#)8j*tB~8kRp3fw47d_pfs6)MfXk8Jg3G~W$gSWqa4B*NxD;H1{03YCK8xH8J_{~JZUPsBi;!P|i@;})8^LG5g~$!yLT~}{OK<@=AGsc!56(k=0nP*GHf%Y_b;vKk>%eo68t^}mJ&_u4Pp}=*7i<T%N6rP?gL@(Uz`ek|k^bP`U<YIX*a6%J83^tJ?u(oU?hEdRoDc2?RwEaH)!>oHh2W9kQOM80qre{_7lA(lk47#Aj|TTg27&v7KR_-4e*hkU3<eJXJ0iWnj^Iv6Z*V7YXXI3HXYhN-rQr9#1Cb%%fnX<ODA)-+2DuD820RG496Sg-7#Rj04E_-LIru}cGcp|P40b`T0K0&PAXkEifQKSifro-!kr7~5@GxW~co=v%ay583cmy&EJObPW=>zTp?uwiS?h3X=P6yk9Rmd4&6}TI6Cb%28J5mOB2lqg(0rvp6M2-cw1h+zt1GfUVMve!!23sOO23vxykQ2aG;0{PPa0jq8aw6Co+y*%b+y>kh=?-oSwm?n>TY%p|dVt>n+aNu`HsE&Bzt^4Zuqpg*!`2Zw1^Eeh3OEaS3Y-OgjQkt?7;Iufo5B+E5m?z2u7`UFt_QzGJ^;T3o0?F*0(-cbnA$Y?zy9m+zkg(9pTd76Zv2<x>nHv%pElGozKrs4YpT4nkW3r?DHDu~GJ{M10`4AMas'

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
