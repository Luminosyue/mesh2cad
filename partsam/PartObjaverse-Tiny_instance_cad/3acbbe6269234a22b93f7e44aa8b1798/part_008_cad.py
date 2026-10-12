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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3acbbe6269234a22b93f7e44aa8b1798/part_008.stl', 'relative_path': '3acbbe6269234a22b93f7e44aa8b1798/part_008.stl', 'source_sha256': 'ccd6886e5025f0670edb726a499007411961438ac27fdaafe8fd0c98a5611bea', 'input_faces': 348, 'input_vertices': 237, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[1.0783818424897618e-06, -0.21254092454910278, -0.49508845806121826], [0.10680676251649857, -0.008132904767990112, 0.4999997913837433]]}
GEOMETRY_BASE85 = 'c$}r03se==8pj7h)Y8&2P1737L=w}0@{x~$@)ee-<vW|Bf+!^h2x>}WmZYYoq=;fpqTu`ez|<H~F%Edm%(P5AYMGQ-x9o9y-r3*xpTq34x@+Ba?^)|x{~!Oe&$svf_MYb=KJJE)MhbsgDl1b4Tqtg=C?e`9jg*Xp)b#OV64D-+IB9B-(tv#NaWv=2r=N%)7Nle-FNTdxNE?$H)<q5Ln%F5ULJdnyNlj1nOnf#ab!>w0dwHHqOR)X4B+sM-`|mc9Q5_@HsPG7NhWbB#ZnTG>uV}KpyBN!+l?5fXsDJ%+zK5;mckS8FI!eA47Rr8BH2K=a^+m$BMxCw_zR@>E^7UT_k?)(kRr1Zp&V3?$Yy3GmPhx{J<ezO-O#S{|WC&jw(xytN@1KvepBOe%{B2}!IZxlmgr`&gb>>kXBWpkPtBtzCenAn9-+cTE`Fd_*2Km_~<SVs)qj~8mU(9y<dh|*1eckVVo$|Fxqx|ZKV9ww1Px7tuY-(?OIfmz3U7RCSNj^=!?|6UCpWbr`{qEyi%Bg+n5So`|c*s{qG-JO@FY>jVdE^@tcfU`5{^R7ED~s5VEFs@&)S25?Mdi|XO4BHha&a*GeePLG<ElHB+ADiwInPtw$+wO@$9dvAaGmwMWi;LmcXRt8-MRg^BJz#Rt;yGpNAUP#7Ufg>7K+r~*V`oDP-{!=eQ7Z($zSy4QJPoB9^@<2`jc-izIN2zUK_sC?BUuc+Q_D~Pkci|-*M-$wzT8?@YVQ>QhxQ9<W=;$(?4+gYi&9IZ>g)?{W{~fCT0{+eJ-!&`tQDej=oQwA^FPlDV!%Ok9>3Pk5YR*z<1gkhDpAD;566Av)~i*b5D?O6cuv&j<dP_vNN3LhQU&P6TW_Uh?L(~@D1n5z9!{S_usdg@^}-t-zM>&()S10SNe{Y+AD{mxc!7~<?epf0N?3XJ<^4IZTApv-(cYx(u-5c*T=RmcjvdREne;3Z^q4SalGeqp0#)I{><pc{`CU#jV~L^>+)lP)ZV`?4KI<ecDP@zry9D3{5|EI-;>38qB@XoG|iTL6}}RjD%C-Quf<G~>Y()+PQLleNNK)mza-A{-CiC~k13odz&B<$rS>{}eTmNdb6q0WVL%4?zVPPU{*N`Zj>gk7c>K54E_aXLa{Rn;y#G5);q`rX5$9R=dzm!;(RtjycUHN({(4dok2CaZY5b1w)XnjYfcDP3jDYrzZ%*9Bb(=lC+`S(x_}bMVuEVLBT!-{SypB!2KPv5q$+GXv%kiD#-8m0yS!cKo&iUc~2|VAK=Xsnsk2&k8Wq-5AeLOmK)^i&aQl9D!Jg<GHxqbd!<m-8bT+e1FPSf`**!R79qnGkK=Uez@r(;qct1yau^++8rA3r!=;OhsL@;cs}%JbdPpM33PopSfO`2Bw4rS(z++B@r_2DEp4Ywt7UD?ReL-zBry-#?bySH314FTMcZf4+k68<iu?SFw@{-N&6%e_v@T`G(nA+UI&@Hn)$xDA(=mdam1ZI@Qg&E?5_e3#H>R_9Y%?fbZW|7iC{lFY!M4qJ+ou)kt0!T#uArs(D?`y&;W94f>1cn-wSTANc<3sk7fgLW`(wgQ}%{uERI1Dk;An(B5C?2KN;G-G1=<0sBE|D7Sak-R}qN2Nk}$JWe{F7`KI!udKR}^S9vhm341F^3CS`sl9dG;B{#|h<yL`*Vzy4JUrir%H(=RrI7Edw_aLbqw@^Tb7ymDpP2Bqd4<&8x!+J8UBr3*oDgu{F5>oe4Eg*Y;QQx0!prjwI8Qo$;Ca#vXzxEC2DJBI7m~l>_Vtsc{bOa;T`TQpXMF>F|9WLLA>V3!yR_eYZ^o>3kH>#~T*$s!6(k)OYJl(5L0>kQd_!r#`vKQ4y&#!<EorTk-+-@#S4-zZeN8HlGd_pc@$1cW{`74$$Tu%vlGkx-Hu=8T+o@k8J`?A$1>Enqy`}ZlE6O<k&S;+3_y=i!s+H{fI*yRn9ln}5Oup_P_VRr3JYwN_$9Lgpp4Yxusm|8S;C19L+{4c)J8FMMd4syIlg8up8{qr<4e3d~n%hvCmr;K>=YO$bg}a_=lN9oOnKxFr>!vl!V81k)uY+g%aD7_LU_W=3JpR^;$k%Fh;q%g%;k<9d^VYeKJ7@e>fbWdo@qL*U@_pLMgXBBUaaQAyPwDqv5Al4j|8Rub<9Wvydt#lmZ*d)WeCw_0@_lm8Gvxcv&(8fPe5bwt{2zCj`yJJi$6q|0?r$~t+B-|RefCpyKd<)xhV$ILSh|nZ23{xMe|>k(=kV2@)$HT`L=R~1KfWA)^3Pm{2}xYH`BT@^yeb-d-Rq(*TTH&y_cpJ4eU1GW*)NaeeS+si-;tlmH_O_R?>r|OXWML`b@`(XA76NGHLeXLUwNrsnS1<d$SdTV+uCs*aNnZW&m&)pdQf_Pv?9)P{?A(Q@s9gd<EC%9J)Q@Rc}-7K-mbwL-R+(8jOiInzWH<yzP{jjSxp+t?dL|*yqxE2$2U)WAw5?bFH9xhfBki?FYxuoF=g&NM!La%cDo99zvjk2x!-F`q~}~~d%aDx?l0z)x$CU#ZAQMnWvSG!S<;4l=e*?H51Xa!*?(klnR^}8<8kCW&t?ASwGRh!{yH)8bN3mY$5Z`lncFw2CbC~1D?Kl(S7u4={qF&O-NgR8w^T^`p|+RD^HXSrd;jPUM{TC@S8eBU;(pTTIhcGSe-rz-zx9nPV88h>uY3QSnPudgLl3i$^Mm6XwQuJAkNXX6?sw$tA+^2k`k3>7CSQ%3#K#e?Bfk7*TWI_#<Gk+urlxn_PJY8#{J!h;J7|Ae1M2Oh@pL=5o$|bt>ZN&3FCpKkb#4uf<B|JLQu~3I$k#p&DWtqdN-F8^>yf+Y`zgsLwSQpfhm^Nu)Gl|wmXUgj@~)ajzR~^|^{ZW(c$~)dn0J?ZJXZhrPLYQGNxm{Ejq)qgz1;pni`{PDX|IKxB3}z0%I~}Ws6+iKnf>;VD#<G-&-YzEqWRX^%0AxjX}Ze$|H@Ixx7vR~`OT{1?0<Ze-v^Gk%;S0MregA&jidL0)~Qug2enu0z0^;OojbVSYO1qpZX@4$&uN^D;BmfEPQJ13Q$C+8-Awh@r=1|*YSf3{fBvf;wKwB`<o45o*HXXTA3R2W$V2Z^K2Q1Ew2w;?XukT<B=)C8<Wv4fd+~ZLf0O-RPVR88i`C6Xz8d;I`9{QNR0pH&Rc^2KruiyW%PEib*KPaU`L(7YACR7JFZouR^OQ#~?ae;kqiWB5PW}3J4U+x&>*@Wfx^;-;)4Ie<Z@m-EyqzC3P!th$l}1XU$MwovnBwE;-@o!6AN^mw@{Wq`^#8u{eo)NGjt&UHcOwM1fZhde0lpL3416cJDfAAo(8l1V;3f#cw?i9&ZwKEBZ3q^63;0%W1L$qw#dfT><28if$q2z?5P}CH1ouJ+E<_04fe>7R5PTFNxB?;g7(#G4LhuoU;JpaJ8=;HA+w3@C$2w>kSg02)v=S`zeQ-SVS%ly;gy7i-!EYf1Z$Jp%g%Erg`abwDxExyPnq#GF?v<!VCC2L1$BUYIF(0RfWvFWz=Iqq@0BU~#b=iS+5&AZC8+aSW`ZhvvjH@m&h<Mjp$162^K=2sovr5fA5j+{1rqt{u!LLDQgJ+|r&fa?q>$(`c5xN1q5xf_=3%m=pcJ_(jBhYg2K|7Y%VIc&+ix9jUA$SWyu!#`-I6`n&gkTLJco0JHM1<g15Q0}A1aCqJ-iZ*r4|)(R&Y!*QSPC5q7CH$mbPibPTJTor9)#fi2*ITY!G{on-$Mv4MhM;vT?^g}UICrsn&TYT+~=Skb1+t?K9f+hNtlmQ!=b3_P|Vq>b8pnXH|o+A>moD`+5_AJV~s-yUhS&OYQ$EhW~~J~dqD7R=pLnJp9p>zx?ic;OM)$EDYz6hwGfA}t_Q*UpzneAfp<cS!NsVxvrhzXg028(*pXz%T!i2pXeu}dyc{7o7y1G?7yJf7umK$lHo%Dp!Tq2k!2Q6{2*GWkPlDTmTO$OA+tJyM_I3<_hJ(Y=W&lF)Xy^#=2#jMi^abz>nCEC{5_mLt6f^@o3Ov$|;m|423~&Z&Jq00nK0@#^XbyN8xCpu&Tm)VT%>}OnFM_@SUId;6HNdmL<DrS*@!-DDe&D{~C}=b|3fu<T7TgAW541J-9&jsYIJgzK9ke~T9k>&;Gq@9YIHEJ^JrX<$IsiNX>nFI69UeQzVLUA{UZG*G@rPl4LL*)CjYK^nk;|!1AJnf8ay#`Lhk6Tr*;W6Su|7f<y4GtU)>G&^uJsjM1YM)l><7Wipm|Eo{t-MM`npoH-vm#AW-2v%G845FI?PquVW@XY)azboEAYMG2xvQS1h^x#6Sxy{c0{cru^y4AwFlY~+!B3wpb_8*<nTa;xz^Q#y1oovi146(?||1JJg8G1_;rK__3$9S;4XGNVn;0WF>oySDd=GEQ{V~E=fD%dQ=u<{r-HMfFM+eb)6lONM^EUZ;GW<i(5Jyez|TXI!Ow%IL#KhKp)bJ+c06H6H$)1&8PF8OJa|G2z%#(FA_UKbt^%h+S0S?DrGuY=_6G~??&1gV_e0PJ5ck1*2>dYge(=NKC!pQHBCqZmgO2gd1UqxlU31h?iv;i!2;J3}?i!DdvFhkga4kDR>}U>M0B#Q6ZpTUJKcEZ13-FtI&>O(@z;zIUgYEd#j<4;gjR=MJksZhF_yQrg3VH%u1-=OV04&r8{u=qNLeGM)g1>@(2L1^Boq}Elp8}tTR)d9J0So;Y?87)dhbO-K5c)azbF>jGKH~q=f)Il1LT>`s1=ok(46YB(hrS6Gb2^84eFgp!A@~yX6YwSQ1?U;@1@L)0;^TsX8{P1q{spk+V~9ye{}34XOZhd5`<Fl2x%@9x;^S(GJz;N_V7eg+5?4g!-!7K4ng'

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
