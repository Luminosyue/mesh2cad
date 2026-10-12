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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/963c5f8b81c045fcab90387bf3aa5143/part_001.stl', 'relative_path': '963c5f8b81c045fcab90387bf3aa5143/part_001.stl', 'source_sha256': 'd844c148b623af52b80435809a8d5ca5925958aeb160eca893b010aab37d644d', 'input_faces': 638, 'input_vertices': 385, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17313745617866516, -0.22648899257183075, -0.28721922636032104], [0.17311334609985352, 0.4164932072162628, 0.3016783595085144]]}
GEOMETRY_BASE85 = 'c$}r22b2`WzK44dL9$4YBn~+&phOo~+#yJ2T@Vl?%>oOH0*gzA1xA#pfaE9)!h$5pQDBD55)>9CsK_WPMtoxABKN+js;_3ci+$(3^WNU`KfkYk)KpbhcU4zc^)<2GLph6D>aU!&@BW=RODbBHi2PPjYgBUDh(Z05hu0c9Y^=+ARQlpi>->Z+9TK~{tWnnZD*cm(_e-nN$Xz9FKx~y7?kWRP(?+Bv4egVf)<0SJEt3WhPY(OTQ<8=yhmWh)jjdn9UAI~d_XPL<@h@+<3ZCB8P6k9>*8FxbUTFM;Ie~0^-@GsO3H6RGEPY>(=I6w5@Zm4F1#G^1=t}8ZF^jj`eNSfHOVW>R{H7zHPD#oyICF~BiK9=*a<``)lI4yc_GTa(Klt+)Ss$zCwByo`OIae13;la)!0vmL@7wa>UZI{<-yW6a7Cb8JZ5_U!9>~TIo<6)smh;H0Bl0-&{1KHt_s~E#zAxs+Zkd1Se#&1nOXlbO`Sx1j``6tKisMknf6mGBZae+pXT^`ne02KeS<<)G?N;TU%he;0oqy|9S#I##71`$FUC~7P?#1_Ixt4o({eaC6EmFQ`P0ro+^g18Q=S&~*N$=~H8F2Vk$)?%)!4J;ulJy*wemJ{!2u`Yg$WhO3i&O2suBWf=ot?rDH7tKnrdzApIoRyiH36INqy2reZygrt-FHWSAoK4;xsCpQH(>Mq)F+tl6-RpObIz-=Grf=V@{-=l=%>=ZOFvrJSRHGBt@8cx#ZF7@)k>8+tI%=T?ulz<`)c3ge_8rgzyCOVZ;pg3vVGfL*y+gU&GFLrR4S$X{9hfg*WYuxysW?Wb^U!EEm?nGnHehm4*K1eDW_!l^QJ0)8-BVak3;AC?6>!?;PD+N<#k!pMfts(FOv27xc@%cZv8e%wP=6e@pJFk{UGh{eX_4?r_i50_R92y=#T5R?+(~~`l&DH^Cx8ah19=WXH<Xmm+ikZVDo+S)6kS^vR(aInY(1W(2x8b%j^i){9uOieVKEP$?J3dF_oVC)6=J_8sG4P+@IF^e2(<G{ryII-TuLKD!qGY#!h>B-|%_z{Inmr-?jyh%JUtNdxxVw6L)M5*nC|dU-7j^WP5&{w8?%ShW0&wMqbZ9J4oMOx!6^Cy+8YDkKGS#ZKnJ^4W#e!%-CSRPyCgGnX*1#?t9Okzi-}T`5f@K7_iQsKGZl~`RC7PIMQ$5^P$XtLVAY1Uweiw-xIL;k$(N%F?rqHsrT2)f9Jlkwr0uet$iQ&mG48ZBYmV_nCW#plivI0bVquB_X;w-_9OkMLLQmk_tKO#j($`uO`X@At7`n9o}s+c)b+#H<B$KJ1M2><;-nvHGwxH_zB@fZyYIfVUi!XfX9M!Q#!p&hZ%_Z|ITvMn|9hhBXP%ZnWyyM!s4VX%?fVOykk4P=A5*r<^J<c?LZ-jdPCXCKtv+e@efXidrB2v=YvjlB{_yYp<CG&G?XNp|%#lyK^!@U_y1W0hBcJxl_ax_Vq<2q!=mUA4PkrGi*BhL9FuQz$_+~!V;ySXuf@VFnZ`9M;S4_6MztYO%j&cW$lfJdAs3V_H+t+1(^X<#$Y`3ZVr0;q0-ciSSEiEGZv-NUUN4cJomF0cl`5{G?>zSRhT-K+V8gKo3cgcQd6)CXX(I2Y~k=Na-^!ZZhcgZ8~(_ryd7Xo&_;{4U}`fqq!-goYsi<U?~ruHUz-Cr7fUY^J7$<p_=j+gz=UG2h|fX%lq=ajy``ZwntzV&`Db-yNj<nV`e=_~7ZEcK$S*O?xR<-fb1lk){{&1GjD{_>h~zF__IU8dc)o+z_UwomPi7aV@!Rh#8?JeQOufB$s+BB{52l=BbI_4h7FE!K3Q{9U{9vfbUU)sy*0{M1uw{9jl{-dCQ{Neg8DJTE-;R<4fE#`mp@f6w6$`Rjl@-`Doa{^zcKX}<JBorlZzZIda_FXC_7FV8DfsK5!k@B6ge4w-L}L#G|-U&|}6yOoh&wu2}4^U7x)65Q8XJ>QPil)iUnK{aj+%979hh~FSx`TI-D{M?5gmA)tTifp&g$J^EX9^Z@anUVK|-M8MDDEqs6oBOogcjH^{FF$7YJ&k&*aiHt(j`V(f&m*Ug+Wp|gjq<$QMtUnt`DS|0^y#u+dyM*c@!dv!{M*zx>#jNcxTD<W`=uY;7IVr`Zrn9Te~+Xectky?->RU-tG)N<$@FgxQRg+dhP?l+S-(l&mwH>Z=guzjI=Wv@Rq1zsEAKP!>%T}f{oo6?*E{?JWjD%v%=Gwv())__Q2v?R+hzM#I;qBo#Al@+`aDkFuhyZPyB+?h5g*InZ_2w-p69SX=E{H1^@*C_XC%sg=WX?)^n<H^RPPyAA9^=F8$am!RMsc7@~FzkU;0&hzX;YD{<id&u8`xumFG=WuV(49?D_cbO?x*x-@4Idz1`RC7P{+9uYJ#Tl|I<5;9Ju7{?=QjFFrz!ZxMgcY;``~-X|RX&>?DE>e>2&!(Y^No6Ki#`Aoa-Tb)nM*FP;O$35@iUuVkn#fHlM9=i9Z96$YM@6V8arI}l0`>bvw^AA;7qWlE|rptV<%$DuunOsNtj7#1;Z^-9{>06hVZ;|<RJUG?S4nNmgmYwhOp4{y4xvwlUJ-(Op{_Q2FI<9+Q<+5!3akEwa3+qp|`<^4M-pSVgy51(cuj^?YcBYTi|0|U~G_}R|heiGL`{oy0<a>qo^}O1jUT>G(*Yj%c?zzY9`S|fe$q6Uzeq^3$<R9^S|GvlW>-l6T<JS}M+4w;-f8KYjw!;oM^5K0axP0p=dwTu8<6BvHzaxDC-ly)B%5>y!`M1b)gA-0W{9OgqeO;nqz;Rx|3SFdM;L2G?`e5Vkvi)mabEc=iTdT%6{n%wAq+fULc}G4!f3-#&yW7To<nWt!+N%0jor{ik+c;PDBj2(1PCs*#Tn`HFNVw$4r`(@%UCGn;ewM@M{nxX&k81Dli+=O0xDO7gd7AgD=_l;IZ{Qx~$KE||_k+X6$m`*K>KSJ~SMJLC`7Zsk$B|F^UOC=clkTi{<g;tFS_imTTJ=ACcfq^Yq(3J8u-*3zTCJY%`9725sHaBme}o^Ix2#N9VE1+Za(B47C_CRO)o__3AKmXN_gR#kA1rR9XM6}&GSX}R^7m`i{Ss3+-d1jK|2v!Qex%%e%J<IfQaavtUe?W7TkU?N{%<vZ-;tht{L7~}ed^=G_s#1s*SGZgfG6is*&jW>Rh=x;U%RB%6=RFab*tdAj+5=>>T&D=pK(n4<~U~hdK?SxsXx`xK8&jm_>8OmZda$;^U>qH>FaSm;v3_<>FaSmSg+9xd;9C>j_F69J6BgJ-+X?xS~AOCfBk$nef@mbzWIDNef@m5@{N95sxhx{k3Kn99vkxz|C7JWwU?{sGp4WSGu{{C=E-^(^Qee#%%i-`hR?ItQ_uHIU(fd<zA@i3eLdgv<|sa2rZeXA+BfI(+BfI(+BfI(k^GJMy!Orcy!Orce571sJ|D^7n9oP*Z_MW-<r?$(NV&#*K2okRpO2(B=JVF67*($EJ{9qe_bFeflgi(CFAH5gr+njm(3hAj$7A#TF*G)HfxRE;_fXT<@1fosv2uJh-+!%nZ>#+h<9$DLB-e838|w+~CViD}tUrX}+pm!M8tX;cH`j}_Z>|?b@-fznBKa8WMUi}r^&;(?>qXi(*Ne1ot`|k}H`a?H^)%LtBI%9wqDZ;MdXe_c^`gl68tX-o^D@?pBK0xWiz0r#BJ%m<`)ItpFWfmM$mfZ<9;p2X)&o1gzDky7tSee;o|WUDxjw0VbA2*6;1lH=>z~>;*FUW~lh@eqL%ojb8$DCb3(WOc?LV*{+wx!1H`j-?Z>|q(-&`M#q&L@x2TjaS?c-dp*8T(Q)fs0p?Clv@_pY6?&VIgno!s-`f%hEg^}71wQ#UyJDeLf_zuRw8$IkV9?VIcQ*2R9C?D^|`0Z-P$YQ4$WU(mj}zu=v-Zl}H7^!|nR&HW4i_}$9?>6omy_vt_7e93>Q$Sy~@?3-xc+-K3gxzD0~bDt%6`i#oo*!R)Cx$hHtc!wOn%zY*8oBK+^pL)vo3Ul8o;v4%`{tq{(eQaZ2O#9}(n6FT0H4d8lYsbCHH}>Pa)2FHDhp~Sb@s0gHe~z069QVK8H^evh4ZUBql;f<qkEwlgA5;70K4v5zV;|GKyuX^C8T+ac-`H2Rl1Hg=-`MBXzPZn<eRH2z`{q8cH^Y6<-rx1Uv-Zt>=itZ~wVrD3YvY^y+QGpS<nJE%P9Wio8b^(NcGK7U?Cz|%prc&&{k3oI`)l9a_kX}AeJJT2hadTFVeCcq95BCIFnzvT@PGbyFx&IRH}iLQ>?_9`^ZSa>>$8+^e5Yah`a2DGsatX!GQR^cef=GX=gKs79~<A9M112rlhDplvVWW3v6#O8jwRHvuzF4#-_>Z}{H{j(=65xbe9Z4^7F3nK`JIpH%kO*=9bYy5)vA4=l(Lp3B9B$n8jxiBq)C|KPiyv{G!3fvzxt%9LEYH@?<Y-FT$WWW9M7R2S&D_;g+&Oij$VL;E`o)2hJ|*4g)W9g2)>9{6}|{(p-o|-K3M3-u+V}o#aVE?OKC0mS+piv3$6(lKnubJ;7jBu%D6;XKKK$m3GD<=f;*y3;f}BetqObKD(J&-6*wpQ5S$avfmVidz?INsxDwo-5S)begN62mh4zG#U@sxKHzBwOA-Fps_(ei+S3+<%Lhwt3;9h7S_)W^5iF)Cg@N~2{JRP2j_JF6tZ=l`bH{i+Wi|}OlHMA@I8vHui4SpS-g1!V#fv2Ip;A!v-v=2N3ehcjjzXi`i`@yr|+2{axHhdoa5Efe1rT9FY-=(w?oFC4IR)q7xdC_ukUO0C+@`U4&a8w`!mq&BK<zY9P6L!N-pgG_t;L@lCmxfEC|FIO8giD|<mtqluOQ8?JrQkB?!*Ch+Ni;W{oAZ4Vtq2P(3ztDlp=IF`Xi2mzTpE1>EepHR@@QFG8<wSw%Tjg)v=S_|itSnmu1pB-hIWU$!Q;a*0Zm7{!$O~fg;s~t;TS^jzbvI<9RC*~xCdSqEL4oeg7p~P1APhZ0Z&9Hz!NBYA{qn7Q2s=IJCWo63df^iK5D5Dd?Kv(!tqZyej^0`j{XS$4&OpU@GbZ{x*5I>??UInyI?;$7xu%e!m$(GgwBOG!CQ#W!tp5~_$NZ}eM0cR3Bf-Tg1;mLzfTBWKnR|XZh^N@hxzC{cs{%U-E7NeGkI^OjdWQd$`8?|x;{Tr#~--{y3YS_9{+I7^m*OmT!sE%JNF-G5206W?Q@kj+k$RFuiD!AD%W8rd=32pz6O7b-h+ky2LBq4udV2P^)<fGEAY4QHFUcz|Lv47^c`D$1g}C@!mD6Ey2FazSAut;pIg!UQ1Er?_B-|c6~2Ssg73iJpx5E+<ns;ri?X*7f|sH1z{}vJ=yrH1ycN9yZ-p<TU&EK-@6cc2@8G}CJMdrd-{?2+-|+Y7=kWLN4Ri;*gLAt<2>yZ)yb)anZ-mF7OW`r_Xml$)8s30jhBv^Upx?otz_-!A;M?$HE~S6NA_NyfzlTK#{sr#_e1miQh2M*GLkYpDsQC9(js>?vzko#u{t9m+{1w~)9RoLjA45mOkHLk}4RB$&KKcn<9}b|m;Q-v$rBs|-TiRzRd?f5Q3&%0E1uQfHJ_er($JuaXhGPXGI0ZcgpCWw<>Hpy0g%)=y&V)tUCe))bdJGmJxHftUKE-cqlV1E@w{sJ&gU~Lp&~dKlH5$h?6gt)wy{2Pn7onYP_dsXbDnMJFLp#GqD7zWj0B#1yppU^ZaBj3PoEy%C)`xS!HP8So^c>te9M6b)5rP|{Pr?o1a%fSw99$eN1Q&-NMT^0Y!jGeF_;I*A8Vi?)8=-CBMsPcHAKVT;h}L&0J_tYKQrZfB25y7)f!n}I=*w^tJQy7Y4~Abw2f?qxub{o*S70yN686Ha!_fe(hqi?4!A}u_o1(qprf?!U2u_6iqr>3-@Bs8>cmSM?_JNb(j%X{mBiszF4>yCKM#Z&xnq$Fxxn6DHy>KEL3n#+QqHg$E_-V8l{4`t!Ed-Z=OQA*KQgCVXNw_rp6#5MO6x;-D4L5<G562#KH`*HB4ev+W!u#O^gy8mQL%2QM7%c}khO42);c9RR^ijA3Tm*d_E&`WC%flt%>S!alIvj_#gX7>1=s~yx`~fQZ;RhTGu1nu+1J{LHph<8G_(gOu{34u!z6z(nL(o^?A@D%d3lD_5qOIYsaC2K<ZB7WT<5Jg7=zg?;D|&qe??&snqW6Q~J?K-g`2SGm3&$gb;5=v@I1gMC4Z=0yf#^wiApA-=MxdwBlW<X&(qiaIScKrm(I6~B@C)ekF2y1Qk3mPlW8l$*;E~~o4M##a+7p8Nq9ftH@NhzK8afJ2gGUg8`=QUn{ooF$sCNgB1vhl55PX;r+zPD&w}R^tg3F@$;IeQ5LU2JeFI*7LPY8Y@9Cgv!XkNHBTnl{!t_4>h1Y2kxEBYtch1P^!a7A<=ToH~(UxDM{=C=E(IU)EtaZjLQ(Gl=i_zZd)*7x5Tjs+JEM-8+QS`=;s$DzgGIM{<e4twBU=nHT!*oTgReefi7G&~9JNeJ$Qj)X^Y?{*>t{~11~<CfB!sPJ#1v9Jiihb$GbuIO_?a2?XNhwH%2(Y~(exFonMI@}c<#{>^V(_GPUPw)_Qgey8u3Qj@$xuWB$;1|&juIM-{xCPqK6&<$)*F{CY(&N0~59n*Htmtz=a0j%W6@88fjzh~@(dUlf>SzHg`kWG65-n&&pKF4Pp!u!nb5L*z^a(5a+!S2RiuO<aoE6*{ZD~cH%Yxf;?b>ra+vDr&+mdVElHcD%Ys1IU<!EhKXf1d-JQ1w`pF?Y)72q0hF4VH3?+)TGH|nyY?;3(*(27>{-9&IRG~SB7%Ls0PHiuil3Fvch0-Rz+$Bq<2@CtOS6@8Z!d=@<e3l(F;S&jw&VMWIg!6F0~$7=)^hijv8aBa9T>TyNiHw8CAd%;cME~pRg0*^x{!Q<euXis=7tlt}j7UH-k+>`O85GuwL!S982TsYoE$HVW!YteLgEu0aKk>MB>j$!Dlu+YKqFn9?1GCTwxgbsxV!Kr8(oC*&o1TR4s!b{*e;h2EFjV^@Oq3h9w@OpR+ng*v)k2Qqg)!|5N=gLv^q5tVWy%GHr*UxhNhd9h%I=8p&zq}mIE3(<0*zRH3=W>MqCmMLH=oQv~19w3mzy'

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
