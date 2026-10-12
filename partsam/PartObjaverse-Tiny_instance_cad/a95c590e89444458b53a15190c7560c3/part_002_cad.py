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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/a95c590e89444458b53a15190c7560c3/part_002.stl', 'relative_path': 'a95c590e89444458b53a15190c7560c3/part_002.stl', 'source_sha256': '288f4acab8f70656e84b64be7ae34b44dcb267261a27bb2d4f1defebadc1493b', 'input_faces': 500, 'input_vertices': 302, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.26654911041259766, -0.49960780143737793, -0.2492595613002777], [-0.018430352210998535, 0.49999964237213135, 0.06818169355392456]]}
GEOMETRY_BASE85 = 'c$}r12UHc;x5noxDjHF2sIdeqh-k22VvAS*SYk<tVnKZogAgkqqEWGo8Zks8Q4)I;8=|73!H#gjfC6Gr5jFN0Tbd1wHU4Ms{f*4M;976JceD2Te)Dl=pFQWCY4;lMKBeudEAnZe^xNfsDYveoP*hZ^D^mhO!^ZdrOllbvGR>qovQHmfqdywh&)e6eOi{vJMg>gr4|VC_?9wUleHV9Um%!lAu+Wh~BZ5Om1(4rk<oHPenm=ju$dCYS+qI2HYj@{1&D@=5I{zO(6{v>Bl~1K;Vri0?NvgPRi0h(>da)pvw#^-b#eceEJ^4!13HH^arNxh(w~KsBL=gLytn$a%Z`gk&=kX1cJTbeojQP!<e<c3=#AECa3){{4xAbLS**iYV*stZ&*3$my7-_%r@&@*QY9#GHFl8C*QKGN@%-bUmX0V<=x|RL$BiT2*R}p`$YXa99(3gGH?Z@NBdeqE<le~Si#tEzOS(3@VrG6P{-?qzl?2k%i-~22$+iKimg2kT~kZo0G*H0vWw?H|r_k3d5uX!Rz#vxJa9NA%u^m|DBGNp5j^(dwY-nP_EK4I)v4G&{q4X&AGbzB((WdFCj{KWdAU@qrL?<@Xx2kAHc*beqbdrJNd{ZAO{SI<1;ZFNoZQTEqNjOO+;@3U|5ACqYuA7#N;;&*Q)?VaYV<vfF@NuI4kvaQw+d}Vm%apU-?nSCVBFAnMKCsvpGYqys?QFhr@>*{txX`j9|js4bhH?iNbzT`h2F5}=<W-0sSOp+((V3u*cDWxAt-e<LrTg^+AmF!z4XUlP^r`EB5Ih=jfY@cOZhw8;J@zX<&8OK>osw#fVV9DckNa|epg7;V7^2@YZw?Ah{-imE9tj3{#5Ah#fNw+$#{1d#t`QEJz<Giabsq9;#TBcjopZ1OTZKHoO)}uO15PxD|hH>82WhSYw&V_WV`F*@v#%uK_=~m<a?pev(qU&Yep8jMNxA$Bo{#YmRM+beu{?-WbJ6yiP{s)E2+27Su{EK_USB?g<p03Ki`LOFn-cC-H<64);<EuV-`3w7&59hPr`?QRE=Pj4mZ<sInKZzE9(yv$9zrSJ`YfzNrX<AzPt^VQn-2R<`;#WT)?air!+28T8<OxZ>!2Yo1a(&45690Un^sD3#;r+X`6u;>WsdLqp)vS9RCI60S$&=7%5$ipZ_~U9wJ#lkGc)Ku-*S*^Os`zP*<$P?tj(tn&UCDoK!YHn@Rmr{*8O^@=vq4g)8a$KpPKcEAYRzt`Cn=5RU1>K%+WXEt&)X5M8(E`<N&6MEWPW?qoG0VnS^8bpU)r~9yM#5mm9)QKAob_EPv(9<wU^`a%ac0IUj%bI_+}el_4+53^ZO)9oqpFQv%bMsXJ2Pu{r8p3quW|u56Y->(tg_psdI3mT$k3zOMBlAQs;U5`CL!GjqEF(&PpD?3Np^I;o|@Ov-BIYeK2po$-mW2e09C_Ti~Oz-W1<5+s5yH!@_>qyW(3O_u_uNO7@k*$?Pkq9HdT<9TR!`YMA(kKbGT)kLLMOJ2ztA?7BW*#^Ls6)@rv>*bg2k=iRp+<9L6kEb%j^Nc+>f<ve<RAVrR=$~oTlEG_FqnVZaYsujdf+8fFGYEH@ix1Y1GJX|Wi{o_zsZ*TBt)EEEyOF1r&9;12Nr3U-zJKe-z@xdJS^Y0zu`WJc0x>Cw?W&d~(`|9nra=gk^$&)@aiFM3$nMcbWU)F_F4|99F#mMuutBlVC@q@2j;(qFO$u|0yzq(yyow-=9qeI=L{klKSa-IQpGX8GY4)Oj|y~I!JF3$;$sqCxI|CTyqz6szw&*w|~_g2WfeA!FZPliAHO6|8L&!!-`{tO%}d1AZC`WYQMiPh%~{#|GB`;3$EA9`8l{mvWwKkcO7>qlkWl*S`uJ^yx){l{0Op0DqIE9Z9}`>J=wc^;pn+w%Me|Jq5{bL`iDPwtDo<Jq@#xhVbmDPOaG_y#{O>j3Y!_cG?IPE+ZB1pAg2{!-8Ns<EuM8jAm-k&Nfmzvi)KS7BeZWQp%SbPj9Q8+>!Yex8@T6Xbg9>?ZSdCYycBq{TAM2Tq2``6Rw->ql>6Ux|KtmH$5HkUV$5H%InoUnvNZb#-&Cv>(4w)?eRYn^@nClJ;pE@;GmcNO`VqJ6PHmR+I7Zp79xLrz+Ckf2y>fQTPMv(u(3g9w_5>rJ_7H4t=tZ{mFjfcWSoA%5PU!#;3x3xi759V_%(^E8`Q=IfS*)BJFoQkorv%Hl~#1ugO@>`fxM*O0cJl+xasx?+?Vc1ljnHmP^0pJXt3eU%4+l6yI#?PkFJI{pTko&$StH-<d4FV(V9UBL0|1^4ydky)&gG-<&jpb=zsl@A+0fZ_nCs$mpxf<Il1Vl69v0meIq`O8=dbjJ}fnB9ApMM$Wh1iIRWmW_ezYuD7v7f762%MqeE|T+X)#=XaFotBb~2<>?oBtfcm@ecSdm%;_c8qx*V2j*I1ZCsvbr@v)cZ<jQaGJv+-d_;-`*q`JNbtHb?7tMg)Q%J!6!{PW+=GWu%Ze=<sH|Jv8vKi|*3WomDkug{$J8GS$hG@ci=c0W1aRxC`kTF>9l-&&%7$87=YrGZjs$9@;MAD_ONR=(RAxqiCkTlwnI_hnsq+)T3a_asZ5t)BD!PZ{+5NA7oSsGO%S3gkSk{#g9|D<x0bXjxbAV`_I~Uwv?LpV2qZ$dPsEH~WauSFZ$#-~NWI^C6ZWt=3`J@VFBFOTLS&e0`nRw%2{VefR<CcYAZWz9r<2W4*UZ+NX_|b>h)T?wdWoV&4*TS*~N=p<l7)hfDiL>EdtLEZ4U-AF{9XI3VMhQeV~|eDg9NnfD|wIe#zrkb2s!lJ}l!3)YwD_pPypb#g_?b8nZ-d#g*wt^8}jGVlHH-U#3F#cG+CyLL%dzJA@9dQqOA+CSaH{!fl_To(fPy;%3n<@(F{6^HK`-WOl7_0RiBd-HX<9^UUVowZ%pJ=VvC`;o2x%lKui4RUs~W;)A!se2+=S4OjMer1w6%_;o8rhM$mzU72j?o)%`-p)F;FoD~9pXG5gKTVKvgKxQAS;n)=l1!to%<j$OX^xnfW%T{*b7lSaym!E={RNBo({>)V%0G6Z_|60N8GYvgzsmSOPENFHU#^|_(eI{MwQs&W&+0sduYU8s_!UN2_3IqzCg<1uO;&ZjzMjNh++L#p%x7JReq2^KYuQ~=XM-~`{so8RemZ=c_!FFD{O>N5@4?EfNU%D8W8A+?G5D{qxBC6j*4OWk@b&wS8uxudNxq`49AoTPzt5@-?02V>;44E4CRx>q`;=||qWhP1{@2%koBCh-Hub;0E-i`JR-$h+KCjP<CqbJ_^yhZ}&g!_H`H4SjnapEQDaqe^nw+QZQD3rF^4i6|kDbip4M%yuh`+p}#PihF*U!_(N$eN9F6qAQbqRj4>yqx<UY9a<NuDK-<bJf#OP<eNd&%>K?e!LZvFq*0;qjb*aiOfw#dYMl?!a9>4~pH_;1|2E>FsUrYw(NR*AjBJTaBB3owxP%>wHig`<C9n%Dluy%lAUAZgRfb-uHFi_P!6l*nMC3ZSVV|u5PnBPxbqz?%UpHZGF9cLbCX_&oj2Z{yg)00Q<$Bm*5wBUb-_<+K+85^BDe{T<1##N<VSs#CI4Z-^&F>NxkiyWIP|NlXd>@T=v!DGi6=5rpkMeH;&KtIS_ua=RjLuZ@<Wc{bJAa@QXdq!!Pzc55L&+e60mrIDgpzQh!K*d|x;BpIFXo``m8p>(Alvi#@m7`nK(DpWAJH{kdHUVZYdWkgcy@C!Y+6wOS|od!MbZzxVaHA=kx^GGu=LY#PNncB%Mz<;0I|zk;>($qiDs&3iQbV(-yTA?&N8d&;^RvnZa`E1S<_b8}ozEPk?nJi^2;Ur+q!FJ&Djjs1b=H{h1|vr_r@5ykEmpZCSS_kdsQdyn|leBCYf{Sy3Q-!Hw$mHR`av-BGoir<5-F6I3*3eWI%o!>Te@wWOkbX4q?U+&k`p5U}7uT)n8M;d+#C6hk7mi$xbn703`pF%x7JpR8wh5kz=o3z^!^dCi-g7_db3w#hf4M98~dJ#My{3T60bT0HFcrG{_`j$yJ8(hI8+7w&?+!#UZjv#IUZ2%^90h87Mw*b3C9l)doiZE#tL;fb{leD6thKi_*^e?5T&cARRq(_ya<2s7tCY@>+hp8AR($U~C;33dq;2~fyXg{zQxC8V*;11xn&`#jCU=L_Jum`v`^nGw^@O#iMVA8%|543BAAZ`PF58MXa9@-a7`Z2gYco5VNJP14zK|BNc6?g`CJ@f#0J$OGf6HJ-`-VdIqMX(l=wfF`>ybwA8ybwGSItolW5j+zd1)T?;hrXhqe}bdHKS7;M!leJgryyPj{RO-ZJRN!vJRLj^It@%ZA3P2m3jGos3LdW%ozLT;L%`#~L!n;aq2M0S4&WZ(&d|2t&R|cd2bi=K*c03lLHq%<4fq3aPiT8E=^$`V@L=djFzF2NVDMPzdhl5A7tsCS{g~G;5X1q{iQoY6XV6jLUQlo7D6lu!2RZ@l1O5~`9XuU#`6)CM{3&=ibUb)G=4m*BxIeT9xIefzv@^Ij*bMaqdtz?P&~9KexEF%BJG3LXBj&F=g7_n7PjFAn%|{4gf9P27Sj>SxGyv=m_Jw{1*5|+%+8x{-efVNuUu=)i;(xRl2ps?(2>t}x2mA^6Lugm<EG-sk5rZJ!30({(Jp>NYVhZ+~1zrRV0f%58;&3e%81gSb9?}SKgdu+nRL`&1vJ-6<LG}E4J>iHc$gS7202*PagYu?BzXj`c1|f_&reJ?PcZ4C|A%yX`!ofSiG0-4z5c(!=q+M4(*HlFi2O@~W5X8+)62#4+v_G*Mv>~(+xFL8p+EO30(N`e2A^z?L4FtO)?<8!KKM8*i15W}|+c4DViaMKv_4<e#EA)t}JqIC(-4Miew5SHH3T*(cq|iU_Q<T~WV)_?-4%l{t)&-Zv-|V1{;PP6OQ{-cUmWGxC*MQc7mIF7_!kNY&LEH%8j5f8vH4w!0pv}N`=&!7yj<N_7>NTNn2SZH`(0X78aBYlHMT}oXj8`>8C5&Yyw5@}vZ5V%IS7<$OJ=E-qHl!_}&6J{fByI_94t^Kv4s8ymSC9HyR7Mb2M-VrGx`17fs|nN{+yv~Tg}oMUX;BJ6Tn0g00qO*<0DcES+!X2#c1O)kp^d;z!TP?$Z$oQ=Ny~vr%Y)y6R)CfVmw}domIsq6VEWh@j?oUsP3mYE1A82YJ}y<Dj$qQdU?-?Pp2Q8Ib-|<+!PU{OGPEJMA=*@iRyE8oaZP9gFll3@Xf4#lJlBNpf*^huLEIAB0=!*|94)pXh*J>6ClJK<5yY>wIIBgT7JHz(!F#~Vpx=X+fxm-BgTDhOKzD%?z^9-;gHM5<B8Z=8@erB|{TZAKPKE9Qr-I|5(cpOS4(Rvb9pE(RZg3j-3^WgX2K)#?{0w>){0#hDi^tG>=vi<+I0?E3oCMwiT?XC)j)i^)js+ivCV&rvPeV_EPlF4gPr-#?dy@olRp=8i1#uNq(cBPI5SvW0hDh&2$=BBy@d;?IQnU_<Q=q9z(OM<m28~yW)-&;T=nn99umze1wt!DU&wx*YA3z_0AAtErV-hX}eFml=t_FP$rXa3vDw=y@3gYsb);Eckg_2(u+r;OvUp|=PyrB(oedHm2$0R{q&Lly60YSVKLHsp>I1)h|2R#QqhZ^FbN#HneBy@`*&lcn+jWzTYi~dOu8|pcX8c9zZYCer)AuTi<S0Rp<)ZSEd?DnRjF|o(E+GD+zM^wc;RK<GL=cNkfjnrf+nnx4nSzpuoyuZTQAk8tXlN`hP$uX?49IU|{tWn}STHMp(cjzDB-@(Tb#K{QaBhX{uBjCMS+=SkS9s}P7--Z4Gz6<^vLHq(i{1SQ({1RNoBzgx-L3~S#D_UIBVk3fh74%o|D)3V1Z{VfiHPBn&HQ>$AJK)XWebC>*zhmt7A&A#Plfi4jKR}Owk6`S6KoD;-jPEAs4e%!LYUp+FYVZ;*E^Dz;i>uHj;3a5t6+!G|k|3@Ny#b~mt_8gbrXa2iy$z-ywu9aU-^F|rQxLxmeF3H*t^<7ueu+7+gCKT<(%d*ge*;qx*M|NIrXa2dy#}Trt_i&YrXa4QX=#(_C2W&_2|=6)-3U$uuh3$H7C&k+2f7^W-N#g_dg(X)uTw=ImCkjm|B=dePwSr<jC)qnUK(Ei=-}O_48P-)(*C0_oZ8d3Gs=GfsT;~b'

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
