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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f56267bbe2ab41428f4d7148876eced1/part_005.stl', 'relative_path': 'f56267bbe2ab41428f4d7148876eced1/part_005.stl', 'source_sha256': '3a38cdfdd72ba79b44d38a951cc0dee9a14527a4b792ed9d547f1a4134602fd5', 'input_faces': 280, 'input_vertices': 222, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.05268291383981705, 0.20537294447422028, -0.03131353110074997], [0.04265507683157921, 0.3745364248752594, 0.12087489664554596]]}
GEOMETRY_BASE85 = 'c$}r030PIt7RQg6Ipt8|SjkmVG)+)bGzYF3IDm>dAenIu0Z9Y_hl-4&=7<W4h(p8`Qv`FufiXRbnnH>LN@Y)v4W^k{W~FJbxA$8A!#nrV`@Z+RN8kGPfBp74>+HLyv(L#u|JskZD*V?@X;j(JC$PDqNPA3iRc439&5R5Ui|-aa<E>gsQ{wW^C{ss{8xa^>OPQ@CcuWb44~_G9!Q#<BypKm$i${1&+|0Pi(IGK$Q^F+on;aD%CV2eR$uq))->FBB9$hUxJ9o9rwfv8N4MY>HgYM@Zl4buoXM9AdO*+3>me#ZZ+laU9dzN_5)~Qr(tV7&Z`e&u|Ezg#0l%*~6Mz-YYFzvkbmExdGS?alqi7Q(VQhxjG$_Zv}d9}|4x?gdbo$}-jC9X9aNB6Y^gnvl9pe5(;e3<gvy~ZvkUf7g*$D`cN?jF=mz2xpz$?Ykw<&=M_ZMT_gt|K}B!+&lyb49(+c|x<OAN0dz#I1Lt&Jm9qu!`<mTEck}no+#ct6?7TlS#xaMZ@WLSvqdoLV3;v5Vu)d5VxNTT}J$ids`@8Z$(_4)cGUgbrV0N`!4!|ey=ScZa?wIUS;0G%I&QC(hTCwo+hpqdQv;}<Cz@)RMlpRzj1`}sE3NX5pR2hxEA^o=dYKOPuyb`ar?yLGRptuLGHKC5ybURk6a|ax=j}GZUdM%Dk5&V^Kv$E&)$6B<HxC;>YRGhiF<i+{uLiny!uqv_lb9JM_lb5N9|WzR)!GwRkNtyUQVNUt6$=3Gq>DHC$0pPaK8;7PuzO6oafv0<XO}{|53!%AGY%RIU7?*@uRwOo_0+y@b8H@KxJTCzHgpN^W1)OZGi*N@T7Rn?X;EhkEu`Gp7;dE*SgC6IqtzGy6?QNxIMnPJT6h*#Ptta@j6;m#PRWe*(pB$$<y?^uElcyClnI5w;W6H`do$Ev*2ywmVwVxKiK1&%_6?&HR8&{?<;70{WkM`mkuMYU8~}LxcWWkNohb_|DzA(w<X@8_Gq44GU>j-Cuu$?KbG$z?j1s0b@_wxSYjg!%v>M%9FNP&z`exhHp`&)<Q(OBm=Hae+L1Qued783cs^h1{yOoD`ovXN3$<SjkEVXmPR-ju@v&aqKXo>6{)%|!=fi3K*c04n+_ke|#MN)gsQ=aE<L{WclC9Bw?cT8w#J}6Lp7`i_=eb{&6;uA33yIt6mvjFVzEDK`=Mlv94KMNf_3f5Od4BO>K6(L<SHuDCp9lBX(Rc*~^SICH!@SlR;`+G_Rph^NoAw{A_7URB$x?1lSvJjEt<FB;>d@#@)DMxtyUpCTW+mmZ6!gj=UUwbyhXKTuhE+R>H;N{1-@AsmnwLTQw${YP@t4MOd!DY~ebucpoz~ZHy#LroF5z|LUO?QwCx!RDpck2Yjwh~I_fb352A6l5x%$p`G``xHdOZI;hZ47}SxECo|MvZTJ|=EUUC#T4_ubcsdpG6yoMALStrz~}_2N^umd3$<J+;&3dx6_CcqegnZxHj#k23eQ6Su|(^K;?KU%W0tv^3(6zrnn0C&y3DBd(5~>d5CFT|@E73EV%uUZHuSCmtZKdCqa<`+r+ac>?^Yf3&LW-2OvZ#I0EmdE6&8;QSRWm=`=l^VxQOGV{-mtfGFn@5lR3{8(=Pw>IL+oKciVyF0Ul_^nRFt$n)ly4yQ1l=}Zx8{(?Ao7$saXvh18!8@JceWM^OiQ?}Uq!5qxrS)hJdC2#DkW1XsJhIZE{f*p+E34n+=T7oET3>pT+MH)m0q>K>{%r7wVs2;sB{L40dGdR--YqGsc%8a`pG^H+If0)e#y-=pBXR3`5AJ`rrW|kZeStiVxdptg2miQ|+V9q!`}4a(UZ+8R#I+lFd>$wYI%wwh{1AS=yZmzr#YGgYpgbcBXx`dR+o(Uam~i6uxC~x*zb@x}b#c~mir<mT_kHGCk(t|mI7{*NEfqNqJohTEcmL^hUeb~lF@HRpxV7U_KEI{+AYT2Py69VI=K8ajdA)z?P3JLf^AR5B<V;@I`zLXGwnr1U{BVNL19dx&rr-NZ`=vC#6@7U=pX$Gd%7!7-A4<s&wBGHWn>SM4epQQzFFnT31=|4XM}1n)g~U(9QXadtlILMeOXd$B<#}@WZlMF;*qYaM-Al!0uK(4T_uC$`dELc7c#qn9uM5uy&khqPE}@k9@dKQ{!xfGPH_jE+^Kd~7amBk9&41gVd)%JnCz;pFcbvBdUmL*lbK;_RiD&m)K;zZ>4StSf`0{vccVm9Dg3njSc5pxBm(QnhtT@2?`7fJj{^-T2%)h_F^CatLjsu_iGxMSIX`bkZ<`B2V6!N%t8_fHB=|tlC^;?|((}6S}^m2F3<C(?hrR}-gKj$mvQJ%6Yo)2y=HtI)@H|cq3t&j6(_hY<1=X^%bVe67y>QCMM7SF3hJ8{K7n8w}K|94(5i>ESw(1^$7<CaBcu8kkU{b@XZlf8(mQ};Razm|S4f%3fYEzhgGIL?!~gt$E|n)`od8m&()JCL|O>=HkZv@_fuaNEek+&_1=?J{$F#64b*LznV;+||k<-gr+jxPIdrkBj|2uj_pMZHjNQnfH_IQ{2u&+lX7P-{t$3`|>*dWCn5j$;;gT<(udnrQbeFzuVp+lF#!Q<@BDSSInABd9H;LS6kh8;L51pyncs|+vC8Kg7~>m{KtMXSKt1c`EIqyfgh}*^=^rs$LAp<PjM3-$C9>=@z=BYxwiQy2d=zS!RNQ2XF|+*)XzKc`n?k1Z{}9-KE#dlTXmj2QM}LhjB&_so$)TupXi(thxlpRc%R>uchI4o`zO+Twr=~`k>mZ;y1Gq@xjohMDt6BbGdIT9=5f}cJ<jv3I*;@C8hM=Nl`}WyXLWw3`Bpt2oaR;aeVyjB?z1I=erMX4a}MjbNm!)M-}Q6;Tk%vn?<d(eh}YP!4DP&NMYNtx_q{lr&-q!ubN=nA3n=gSApZVP^x8o)cYdzvnYG`ees_AFR&%H4sh+f*xbyQ`pO(Fl@;aRdbngiIKH+>m(LFPXJD-2F+j&cguUJp<%Do9R54Eq`(|3Xz=eLFtDdan!C+p85UgP|E>vj5WQRBRNa|ZDm=i7=vde5$L9!?#)hT84)9-${sVea(ap|4PhJHOZHor}_`J<jiU3*0lP-A?bhTKq2J&hN#V|6d;v?|*~xDE_7N9YE_@O7Af>-pA7(q4BTrzMnLKxRN%A_8H~3g}cnW#&?FqBI4?{9Nx$FOy}P_TiHau^Y@LJ&576eP7>q8-1)o8lnumde4m-96IZY9;q!LM6MSFGS?bps-;o+mq4`_mdsMwNel9tEztUZfGk5+z2CmNkhUb;#9OrrXCvmIGb<R_Do8Mo4_n><1`4Rm6XRyl-;=lGHuGGHDd7`#&C;n3iadmhcpAYNgZ8dY}?}YkS7l}K3hYWQ18rx;kq;z{DkxE#7#Z?KPZ2A-{q5Lz-zyA~)`TT$PDYlQ-|NAMnsc6IF@^=V(T3A!)rtll1z8$zMy`j4yM(V-vEii8|Y2m`6z{0_zpyvzo!?gzYgMLTY6tMa5qrm*2mxIgtRq&<W3N6_d_)_P9OMeBlWGV2a&V?^^qOf=2uY{ihHWxYtdIe%qkYhFCS3=8jyReU-bK$Q9+lDyFvV|psC4)=7K$r@a3O^Za9&|GFYQ!WXUlQU|p;N&Vz>}b5`5sK_%`mAygeBqH8MsEqhC)jg1Yc@TXvz9OOXdpS6XkT&4S|-dJxW*TA@BzYi-g|^{t#FsuI~iDJ?f?Z6in(Suuh113cd?U$?BT?+OQ_zbrB=mR!3MH#I`{$srw1Dg0+Ni=r*S7thh$jPlYebY0y^aLC}K`KMiqmyjA$~&<E2@EE3m5Aif{sq)voM{VvJ~Xju*v7KSnc*BW(_&xLPjSxzxs;{)vjF3VO5?;SpfX=SSOgZUt)75b|V^g#GVU1L})#0*3mWz2N^_64v=^vQJia=wPbPe7l@zL0BY1%A&vu(@dCa@0xI4Q-We=_@Q);eD<hd~cZK;V35ydqdb5=wQT-feuE!jDG>#sF(g|TsOv~N8=g~#Po&ki?(zDm#jI;cF^wd-4Q4Cv+&)ZJHU5`?t(gZ<dEz+@aN#m>-xi&x;K17KZ_i0$k7ZY_2aPSXlFfPj|yw3$p6L3zSOOupM<UjzaI3XsH=zTo&cAzz2HmT6XlcO2749$YtUZsy>P8j*9-BIj}z7wr5CPy0{Rh{mnmkJu;)=q|1H=!Tx-M`F|uwc%2#oJ!+#t07Wfj>N%p?5Il?l8#Xw889=_DR;L>k^{*!+#gmqNpfkwO%LrXRQzSLdeOFa}?vOs9b*1$LFr5+EHI#yUTv=JK(ZqzLjmIl2BzSL`B(Wp;Hon$?5zwv1A0I-hmrS1-2>dwNR5hjmmZwi}$Yh&R{y$m`Q_gMy=4lUURVT<9fgTD;67}u|ZpN{&CsFUSFXlZeXUko0HayGQIm(kWZ@RxB-9Jq{+N1e2Zh><!3emwMSXd8TK!x1C3KYSas!K6O|T9yHb^M{r;QrIx)QSe7V8}R{%nF#+y*l=*Um&kqO6=9jeJ`lE3*vG;S3DaOw9~O2Hb&~B6mM5%G*j`};!it5Jz%K@~n|LweH=)kBZWH2U`8u?0(<EVIg=L{`FSukgg%u&M%z0ecNnvM&T@dz#u+M~j4t)XoBK&e_$&Lv-0d@+!9PE^dOaB~9>Q7)NkmDlaF2PPAR`M#`_fuhI!p;k;gfDdkv}9kxm--*VPJ^8R{}SvB^ig4@@K3`(11rTflI@2tEnnCXuzV9gg7|#Y?M8V3`T+c+CVvmgeZqE`e5nKdYq_}A{!jnZ=HGv+e5g45!yD%-9bXI0SFRMfs$UWV{p--4>mvS>n@Oa6!Ycm)iuRYu'

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
