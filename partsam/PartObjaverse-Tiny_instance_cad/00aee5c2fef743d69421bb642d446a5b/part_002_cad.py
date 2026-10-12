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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/00aee5c2fef743d69421bb642d446a5b/part_002.stl', 'relative_path': '00aee5c2fef743d69421bb642d446a5b/part_002.stl', 'source_sha256': 'eb5204fdaf84b089cea3f2ac8195a4a10a0dbc295ea510ff2dad42e5875d335f', 'input_faces': 473, 'input_vertices': 283, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.00037969788536429405, -0.21475253999233246, -0.4705008864402771], [0.26155054569244385, 0.005733579397201538, 0.46216636896133423]]}
GEOMETRY_BASE85 = 'c$}r137k&V|Hto)v5b8gW6zT?c8XA{xv6A}A!SKCVu)-FS+d<wBr2i8PaZ-=8q3(S%pGGJ%NS$H?jaO4c1n`pbHC?(p1Du2`M+NO*Z)7S*Li*3&&T&UbM86k`@QGhd5LS4D<aBJKMxxlpN_qrubg2xt)LNQ42w?~+P7!?kU9egj|?-4itqerozdo%m*P5y8N-ZGF}>o4^h}6((i8Jk@5V8;JTbioB@9jIF|hlfgkJHE->gUfA@Ko!$eTR|#|J)Fd#rK&TAupVYk9_a{*OQToiQ{!*El&K{_rt-9JS7Ul98N)?@J5c@Ahqc?}JbF=HwgCrKRN<pRi(w+xO|;yCp8w?OWRKKQK8b-~ZyJb#C8_Z?|l=A}8M})@Fg*H+4V5>%Q&wJ=$+yVoq!hzOQ!k@7=zEZ$|B0laudn+<LRy_lGf_MX_7mzK!qgG=F<ezFB?!uAF?|g|U0wz7OA@czs_^zV%ApjF5h|_EPh<XwHF<`ANYqRs4WE-n(hbZt<7*JQ%W1epJ5YIg#m(H(TG^CGkxXj)bgZOZ*=$9S)hd>yx*OHnNYo<BhBMOB)>v>HkP=Tl%|E<zz_wA^iAxCqm-A^^)Y@*H1VVGM?A)Yu-B<GCwu1%D%D6M4k?rpGwL%rdp>$#=m#eaObm~SUx1)C_P$yv(ik7xBI8gignLtwYD;!+7Hg>+#NEXo@HgfaMZ_onfE8jdTHOwdKrTs$ol#YZV_M4zje8b%)j>a{9CVQ%KUpjGG)I9>p<yoQU|mj+*i?A`(^ySJac1R>t)thEbA5YSub;5d9_~sde3wB?=A6jda}z8?$5giWZ#<kR*J9J*UT4rGTG$^*LRd9>+7#rb$+aCeXVP~WPP=-*VpWMQr6e%x>0<+zIMCI60d!|zSg!LvR+p6-Qw%@HGjRY;<eBET3z0ec=J**pY*TmVZ>0WlR;nS_2oAtf32g>EpW$ssw7JN4Enl06!=Q&fNw<HLU+7XWRBF;pijJgd$QCM|H*1!%lC9$ihf4wt@d?Y^8Z~+)ukIJ#MkxKd$hHx!}z+s*^6pOeY4m1T@(_3AyewJ_Ji>&S4f@oH%%2^*Jra^BdOck*Y(!wP($ji@76yd@kZrXSs(4|c+ZI2v*q*ILW^Y`{#EDg8A}(3<lV3m2i?BTJNwd<Oto+RS`w0X=i5o%X+M~E9n(}@E&Rnd?z}VaM5(%muk+66J5}<|zpeCAcV5_gT1noS)vqsg=a+S}!?6&b{IYuQJu3aKue;pckN@ff$uIw_?=E-ek=1|23AZ22qcbs*N4^19e~|gpc{Djv_PO?bx=!A+B#(Uc$0WM*$S62X#p4I_Xl#V!h3E4b;#=gAwR*n92mMkikBq9NRNielBEFH4DC=T)_h%-%d@CLQU^8{!c{nREBrismmAv!q`+bGXPxm%z9iM&VfZO+V!%vzc>*(E9d8NA_@0D(nkNyXplt1vUs-J%>KJ5050r>qY$ohJ&RA1%JJ0t%qlBZVt@YQbL6Ca-H_H{mbT3t_(ej=V(?cRr0N+sDRzCLSKyYtSRadnH^51voD@7pACyZ5XP*;ikuA5C`qdS691lYQmwmZkjJ-Bn&py(9Cled`PS2LojOee0SexyNINPn9~LeLWs;dS9sn*8MM&+<9%D&Led|`#P_^9nzM`e!7(r5^r=bF8fRS!Sh?zT&V+=|BU$mt^?l4iEBdUb7&*U7puhbH6i)(cZCyfU+0TCXx4EVM^xdpA^UT-U-p&ugZr~!Cpky?zv`pn%Ux4-phL9UKlo-D<=Z=^9g^=4+`Kj<A6E~Q`=IuN`B?R$<gb09$~yU;KDYF{D)B*|d^At>mi+Y}XrTOk+}DbStNW(*qg6iI6Gy6iuQ@^adfq-isP^ft`Wxi?x~|?iEBn*-H{IZlx8JL%?rR;FZE){Hqjj;PAwK)i-ZJ?o8E3WBA7#FE9WGHp<x$3A@qIcUr#ybh?R#`S-v9ofd_N*$le-`L{DG}<z00D-_pt89?`@8U_^i9#ZHJs^{Au+zxv$qunJdpnc0z8sADZ;<e`3KFw{LU5@aG<<zF%&ndOpzSQtvF;Z`!w6Upup)THnj*A^m&f;?#W>U-xg9ucP*H)m&TL`@!s5T%Dt|ug|gjKUDqiE2;c+_Cv|aYX4}zB<Gw-b5;E9PU3qQkMU4yVzSHk>-*!{v68=@w%>%r`-^1xl3l)zx7xOo{51xoh;QirN2vVub<Wrlvfs8>*eCrAzpVP#=iX!0)pN>mBU$>tMt!?q?kBhJ(RFX|j3d%--H&YXb^qm?i~1+rwnO$w>!!y-eD;Zvyg}-xF|0+3dpzdQYwFydds2$Kf2+G^r(9S5y(#YfV6Gf>-0kcAU{t;-`_LS4F2#Lac3PIy6SLw&a*i|g`8L<B<8I&9bzs<AQpbF8)z!H#L#?}!9wGZM=tuGVVvd%0>t;vgGk*WsM0Nk#a6$R{dRI=AI^a(VOO<hMRPn~DT&ljdm>A-FuXSDT_PzM_rYBV$Y&at|Wd7^?q1JKL8S!o6%|$a;xP1%X<3BIwN&AJcZK8TVq`WV6!<$uNo4X&oif@72*Zr8I*2!~`wXU-GK0SW+r{{dDZSHySAJ35eX%6{Ne1CV=cfCjUk7vV06|eJj!e^oWBdp`?NL7D!-c)`jdD?BE+K1XNPTkHZBk|r9<J5CNE6$&Vo2cu!b8@?T9_+0b<o@pY<eYjBq38Lt0Y}vSd2ffr(~s}%wo->Zi|;6(>#~MUly&hGYQHlieo7^&xAtAH@@r6k(ysjE_D!zWc&fM5f8*jH@r^?~U$42Z)?NEW*`L+kk$7LJQR4f!F5_AO$vgAh@8bIpQ_p)Zk#+aYyQbn9r?qMNMz`<L<DWc8?oaj<uRMoY_-2<itCC&5spq-s3^`xgf6NbwH+paQI@#q1<L_PiO2#)jNqny!&q&TKz0T}%UzfG@p6n}M<1%UDGygW{QqS3`;#<tK`Agm-A-<mHF5~39YA&0n{3GnE3nkUMYrhcts^c^jUvE{Kdp^z0K6O4k6}emD8K-~ISh??;mu`vg)%(BVBvqfs|D}B5J(t#QbNfE(vp;>Y%JcdS<+<7B_gb+%)O*W(gVp;muGiXo`e2A(nd^;xRn7xe;&|mB<9X!7ZxSE$3vj(J^^|x|`<3FGI$vTE<hfY;Hskc&Y%BL;U*uzZ-SPhQE!HHvd>!wd7^BYj-;5UDL%eTXyCumk->>_RF0{}c@6+>N_t+kHypQ{lKWdlEqy6?YH6ER(>uN||Xy59}y3|;xo@alZDZZh{Gm3qfr>MNAv8%JMDvdbc_D$y5o_SUE^Ft-|KJp~<{PG0#zES)6c<$Trm&Dss-{0rHE??GMsWU-eUsvW7sZ(a=In@u><r`2>)mwa<>+-j+DA(hSXqztMpnrc-)s$qHZ_~ebPD#11o2UAVZ*sj>_-fTZzRmSozbsJeG;y5j|BSj`&(iG@AM_*C_4+?fQtOd*TzoI%@ougo=Q{2C^>`*1lyjYD$Diu=c2n2oIlEHM585|gXC8L=cBp+{Q{LN|dOjyK{5IL;8+snf+>rM>-ij}Z@4@$s<30J*57hg=YUEMF^1Ix=Sp~mb0aZ7P%~k#XOx><jQ{sbu7<D^uS&6r%?-Ad}by?eQ%erXa!*v<U&da)ZKddAB#bP|(zh991OVDRLzOxO~d22*n^?XnNzK@&9c_Zl4zty?2dQRKhSoL#}b*$4)`Vac|mG3WZa&GG)zK8yeIW50ScKJT~H|yq6@0$kp5#NvRAJ2QLn2{=PxGpPq;`$K3s`5P<Q`I;-PgLW%tj6QLv037S{$28J(_HnO`OhNd$Iwsl)iTbYPygN}1JyXqMD=^G(EmRv5+C&MFb~tmNW6V-mGbG|`aoTm^~`4F-yr_OfFBp~SF|=W+Ku}@+Ay3JX+#;ld$|6D=9tcp)|~%@*0;g`>Q8758vVcjgmy77hJAr{9^C_<htHwg;B)W^bSr!UK87a4$KXtK1Dpw`p+CTBu#GN)ZFmj(6}$%i7M%=#3(pU<_tAIJ$?&^yf11N1(68VT@C0-bJOQ4D{s2#d=b;<mdGG=>8D0P{Mz_L?;pONycsZPi?tv5G73e;A1-v@Y)}s5-eXye!;r;OMfo6m$4MQ)&PILGH-g)=|d=EVb--B<XC*a%gb@Ui~9sU)~gnxxkp=t0b_$X?_N8#P*8hAIHf_@99z^l;t@G5wrk-eW5(j5LM(1xM?(D&hf@Ehp6@EdSfv_ISx?v9RtyTg6Z32-0y9dsJ}4m=*62aks*q6^@O@Fa9GJPDqHE{CVUAESxz$M9$93ivblOLR5-B|OK--lKD94*w_6=A!G-weWiQ0J<M`^mq6G{ELyjr+?wI!+!@PFIoU~`~ozGi=bg}5x6Mo?E9j8cDOKl4|bZv`O(|3(;Uu&UWc9L@O`{r;rsAS^b~v(zKkA)FT=;t-SBbvAesUngj3N~a4P&Gx)A;mUV?rEFM&TbvUB58n!}?5?Nzh`It=arw?q5E?cg@(8*m%ACE68k3AaYO!>!>sv=1Byzl^>EzYKRn$HU#=9_U242iyyt1owjD(J62|{3iM_{3bjQ{R|!m4@SR)2g3>I95?|Uiv9;43J)=|b8HCB;kN^A5IP&33(tnvq3hvwa0Yq+cJvoG1HOR%4PSuo7}+^_htCfG6VN{mrMdX*__=5fN1_GbNVqs!1TGFoqebCpxC~ktE(4cD^TQ?KVrU+?7@QAv@-`oz9S%ot!cKGe54_9pA8;0W9L|DIqX*&B@F6r6J_K(^e}uQg8_^~3M)*7QQ}{c0COR6P36C|hb9*e!;ZA|}I9eZl6|N6Iigth>g=?ej;M#C?v<+Mxu7b9NtH3d6Yd8k3iN?V-;kxL{a9#Kbv>W^c+yw0bH-Vo<d%;h`v1mLT3qOm#2|o)zhYp0FgI_=g!!N)uq6zSea0_%O+yZWn4uPA)&Cs{uX7KYyc8z$R=5W(MGts{2Ah<6)1Dy@efRoU5a1xx3X26bKfYafh(L3<Z@D21I_y&B-$gU~3XbxWqw6o|n^iTL2{1@ufoxk|(aBgZ*B%B*AgcgSj!BJ>590iv~%fO}KvS>-TEL;jL2A6_Mp!whua6vR2E(k}UPTh&%v%_}{rCIP@_$qoDz6$%%L$Dt{f^LV8z&p{6@J@I$`W?I(UWU$um%*Q-W8u$X3+)73a2F%HHg%yn+$hi<K_5mRhaZM3qV?g5a0T>HxB^@btqqrh%b?ZaGH@xh3S0^<iN?SsVFRscWdArEhSr6{;BfQ_I2_J}Hi2`&5$Mx!1e_a<g>%Ds&}ZR1a9;E|I4_(JeF4q~N1`vnk#K&r1)Lu)fHsE<zy;A}a6z~b`aE0+E{ryX3&TZ>>>5{u=5WzKs}X2z1Fa6)9<BpFhQ0zn1~))E!VTbtG>1C}+BkF!+7TWD4@X~thr@57?culJo@iTm0Qx%G7JeOWh1P&u!BqpTG+Gv|0hfi#qjli&@I&Zh@I$Z%Z2)`VN@zp45?q<)aAUMH+!%h%HIJ{+9DXm*zCdT8<KS8FbaV_n9iEB~ho{0Hpl`t+z@yNfu%7o(G>1o`ufro@FWL(B!Y`p!;g{fQuC=L#M#I(MT4)qp3$BNjfa}3eqQ&7S;iu4I@Kf+JXi?Zv6MhEnjrN6m!=Iot;7{O{XcD{<-ixNgj{Xeqg-@b4;FItr^cH*x{tdkX{|28ivd;=<(4XKl@L_Zpd>Gz=Zh?2eo6zs!P4H6m3)s<F@KX32bUOSE{53ii{u=h7AHY8NLv$4E=twxORakgbuK(%3i)8;;&P^udKac$To1w4B-QR2$=qvcbJg!x4=e`lRIfct%v$j(ajQ;{h{K;<'

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
