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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ed24b6e27921449f935509d9f3da043f/part_002.stl', 'relative_path': 'ed24b6e27921449f935509d9f3da043f/part_002.stl', 'source_sha256': 'ca9b1fa317463d45d17107c0fde8e4c39e57cefa3392e802faad65981a7fdf14', 'input_faces': 532, 'input_vertices': 333, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1827189177274704, 0.04896891117095947, -0.09266636520624161], [0.21358329057693481, 0.3608148694038391, 0.07536182552576065]]}
GEOMETRY_BASE85 = 'c$}r12UHbD-^K?43)nyuD_$F@U_}rsYr!6CY!USm#TJc<C3e@ug3(|@1*Kd&HV{E9F>x)}HC9YC>Q!HRkH#dH`0o7w&((WZzH`3weZJ>;pWi-r?(FRB%<Sytq;q>`7cas8DhM&ya%We0A*2clFEKtcYV6Pfkz;CpJ!+zpC`!5fXY(Z;yMNZXx04tzCi@MH95W!wuc67W@t_dD0F&RKkx^r#BEIfFGHPI?%v(ha9}}tPV}?YGiqwy*1_lNOm;$Q>n5LTkkN@2CCYZYqII>T+CE?gFp}HxB5?0D%HLV-xipz1z3vw>DJUmRFAGyZmL%MCuEf*VFMag5O#c!00>jO^6Ttz+RpU!jne>xwLx#rHfwM`b6f7Fc5E4+_v$~E7T^aUMzg>yYO-yXAXr`98w^HY=Qyo&qYO}XWwvIwVo+IVrE@ywx}+J+n1^!dFZ+|E{aHs_X$%$VlV&7<~Hu8vMVM|olNXTCHp->NRRzj(CSK3B`t<9?nV&DR^Uipw9Ve1^_jugrFNY>7yA$dz677LgC0!u4G4P4!sRc~t(B{M_}$RDR}2%C!rJ&QkpkYHitPmy6)Tl#BI~yGpkX?~Oc$`bWEKrt?~s_H@V<#h1=2-Z=4jSLZ)T^{iV!^^1`AhaB?4WBSqe7C${?e}C1VytnPkCD-<R_ARw1rNsftJ$6z5EA8qnrTXqDl&eKKHz%1g<guyetNoPU_oDlvoxGfuTdux&t%lm=BDBnTsvq~!-2Ne#uh)+6S8p}LJ{Lipn+IH9MxXoN;PN}?Qf}(fF>9Y)E_QLQPJ3XnFE6sPs6Q<cu{-R`tH`ZQA1B$DSKdX?crd-Vwt~(-<Qmt5-1=8cCbe^~h3hH&9qvnVhJ7xIaIQ^iwVc{@H9(`hbPVSe$58uixr$sp6tIfg>*u<U@+RUG9q0F@^V)LJlyl{BU_7<=Zt~Ce<3~NeZw-AOv4V0nt^$v%mDRW(Y<Uoux4hZ4la8;%ay{`}-cqG`B3*a0{d*}N;ChtKhk9(eYRi35{>;NYbe<#QsNXEbD|30|DspvLAeGmeEZ<GJ>v)H8W!<^RAva@Ospi3yi@Rwwu2hUGs}jT4(Yzbi@4O<@KG%?Ihn!bZeRalg`JyJ8r{)ne)=;@}BX;um`GN0ypj(!Gu6i%vanj;T8gJ^Ozxne$vnUtU=MSU2%LN{%8JDPjC3HaQzFczkeUI^Up1koqE=t~`{<OF?U&ZsPZ5Gda%*QY*<>uWjId30)!M-1qWtBMpY$dOs(_d}NHP>3q<^K4W?vIFicFumDTBjvZt{%^!=aCk2o9>HNekPZ{5O;viTW#4lbX?<e%C(H0yzb2?nMCdU{1Dv-^^7yM-{KOqn!e|s%z0J^p1*CMaR2nXP4h`O58qDx(t6Z<a*<8Bdb8X?s^8Lc1kH<rR$4FB2YV>D?43dNo80|5w+z*&{t^F<rg}QON~d;a&*$rHHg_qNi`h@PSeUSfzP~GMCVf758RySeQ~lNv{#3unKZSC2^C;>E%_${?`YkG*`dh6wn4d3oGie<&7hgoV@a{+DMfZy|-b{lQP``>Czim`*YYyLc?*^PloK2_lXFO8q{B?e#ei9Sb@Oskc*m^oo(m~GC^IxR$eKVF&|M*Yd%HuhQ`a#?Gkk$w5)K2_789RSBeZS1VRF9?1Y<fP6L9zR&o{E1Y(siXYq35co+A@psvUTIA{=;WCI-J*M_yQ^)<43u2xCB2ReNM#Ed24m0e$u|==c8INK4za?uHG{7_^iaanh~|0>W?0Lh{{j?A~n=5SI5TjxXR}K6ZH#le!Lcyx6X3iLiv=V>v;Um<8`2MIn_Q_Ew_2yKyG?FjB*9{(bT3pjX&*3=2|L0G?m(Knv<38kWYU=>yo8XGOhn&p&RFsyuUKH&F1Gw-V${Gg=a90b7gN{zR!(%tfsuekCa=&ve=9Hb3Wn`U8hzpg7YaAC|BF~a=*<<noaFakDzfRChg_&s|Hd1mdx&)-#^IDi|0=_)8`X+TBx4bhTP8qlhWw=?yRC*8{CWTuld<?8poziaTfdQ)ynbxRlCloT=-PlN#%3aZ?n&p*i$@CipJKW&j(yert)Q{@_AE(shy_6@yYh}h!MWq9r7B(4|BU;aldtbLgQ47s(+fUb8E2;bpKB#aGp|NKh^KriLT2$uTO&gb*asKX+D_ywn^Z5QH#czR_Y4PE3L6>f_*)rOa*S|lT_Z<hyP0R+We;*uT#~^t{`6*&Fe$4RNgP;c^*&waJ?@-AD^|S=ZJZF#xkm>_%WU@N0-nzw&lvnlIQGmrD%Uzx5R<>KhyXLzPEvnS6q#y_HHXr<*m0Zv|d@Cnkg5}J$atYolN~{uDogqkHcp)4#c{~G;ggp`!A-v@5~*PH%aFCu%iR#LCvWi%l&p4)PK9ZY2GV2op~QvIS=h;#PT<zxj#KO@_k%P^ZY~pdiPeku4OIL9P(a~TyKPXhC@BR3#dKHwPR}?%43{Z(=FQ_%D;ZX{j<8wMu+l+iqL&j`mIWLD8K(I-7o7_-*kua<=^mq{3SNSAuoNDo(oz7tHXKK@cr48$GvuJPfa)8$L<`s!=av`gJ?dQqepIasHgWS-tSd9ywN__TIA#XNw3)}9P&9;c^&ItVvWOjPqgKA?{QM5{du)RyuZ~9^(gCNXdGHbW^Z?Br)_**^x0sae;A*JTs!?Y?@umnwm7sC^G^Hf$E^<K<HISph|v!HuRiOPL*?_0qw#8vc{njNm+_{YOQiRkPsV5VDb5Y!Sxav<i;fNBUuk`KHXR%0i_$E94z<HDzeJ6MXmZ1RRNTYnh1&O<ZT=!R&TB2dbs^=3^+D8jr}stUdZN8dr1w$d`eSbKl5@j)B^I|^LT*^!Z22ea;rV&7_Vw7-PfL%hoEz3#vsd&o?hnKIT-d_7VLdkoo#5QC{%f1^#Zf;Po)_xc@^SX{e0aVfH$IQFb9LkFugmuQ60iGmdBgM0+Ax{kt3G)?F3aZJ@H|!D*P-_b<MY?*+jk{jr{nY5v?-Ny!}HzLtY#vQL&yDq$=4;B>No5ktnC8${ll;i`H&m;A=7VCu5FBT+|LYbPV>gNFS6yveUaFsa&FjPSrQ)cdT-dL+44{JX&J|8eKPI?ZMktDX!S^5OZ{TlPik%3uA_3s{pW$7IXCWClitxj*SNn`-<{jQ^TMzn4tq=cZsY#hG^fcXhx1~;t)_=_KGDMa^FPi}J?7<mIXCR*6}2d@JI4Kgu>{_?8r~Nyk#{IJzF(M@jO2Z>;eEu?Wi92#_ZM@07aH%z_Z@55fs`BHkIeC>(s(>LzE3HqSMvNbynks2RGuHk_qB)X`1%d+cjkv?IySx!DkW6T4eyWU;}<zU*`A&+if3!uZ<!t!r}h4m_s|=mypJ%vw_2N;`S}oe*6}^J@mE}a<{NtMDDT_xKKQ^WE?=lO<tF5&za~<y^oZa*ab9|ExhNbvhOT?kB(6VeJ<U^*RFtmwlYB|&H1f@^ndFAw0o3s7lxu~i^LX$;KTK#zx!TNw&a0;K@5$oG7n~b@XE3+g#PzIv$iG+I>yw^aZk~FBo=@7AJ=~t?nGU~un3`VZe8LcJPn;_~-;KE%@^Tz~9{iHqGbJBCN4h4_K18kS!_VnA3gy;=KJ=W{mRIKdZDY#Cff&AD$kpz=FH%y%SJ;<Vf6ULhH-1NWUXSyuJ`TVCh<m4Ky-<rJ(fn21$8bHFr+FPgE^PIbxX*d7N+<cg&PdNSfBilG&TOi=i*nZ*w4R$xSjR5b;B{xY_a*!BChqN|TuYqI_puO<A6u@xpW`szlt1(SNO_4Gyzg=kiwVsow}u>~=a993LC(urc)UF-OV3ARZYp_#_dTBNDc6>yIgEep+pj1WXJcsoS~rf~W}mBxi+Ela8vQ+ePo2#9yI$N*%wJJ#71z^!3(ZH9d1R)2t|C`Yy7Kcf9_337<o5LahWCwzTomjaMeW|ap7T79`Mxi#P5avqdC(Ki)pm4Wl<@X@DZkN&_X8gM`;;wLky{u4&c7S4cKwOU$G$zp<C%YlH|C;RJk4vZadp}+ial-VeZkxmzb6=SYZkAQ>X)&UYm0e(wtUa~KVvRdhS9!3+4D2+N0S@y@9@`KB-!V}sS)4bfHgEeO=bLOeODgtru$+($iJ6rX&osSuWs;q`#zlZix#H@F5loP^_%s<mDt>J?Z&U%o*@lrAE}KV?Kp0ct9_#!)=BNHnfI^tZaS>PB6AwQzb)#*zXM<1wk5Y*wCqUrD85eo96j&B?-!R#(RG<l7NuO-9mM<I5@UFOT)Y&Q@0!EoVg1#mx#gyRp3rq^wSD=yyU?GXo2lDq-81H5ZTw`a?{x_0V_)%ov5kKpe%`CKI`Q+UyK^#+KQo_qLQl%A=f`qCSD41-_rIj)tTL@E{Z98G_xqEdztL@isQ#44T+dGY{VO6YHMd+<|CmnaY4n2gcSC8tRTGva^L=j3=liuF?<X_*a6fEqhxg&aT+iCSxId44$?bSvmG?yrU-NsPAs1cZr&9et%tD?-`!uch7<!-5Ud-XVS3K|EHYARx@w0n7=M~EF{&RKq7Ki+CdCucr(s(ch4&!-P%ah-~@Z41259e|NTJ!kL-mo#ZT-40!O7nW;B(CSXk<>q0k^MBktW7)7ycH1*dHxmV`mJlba6VRbcwSrg55?~V$9X(ddY(YXkEe0@j2K?`(!Ql!98Kl?`cC?NKr71iSmO6`Jw3g6{9pegk>|5Jy^o2*PV~7_gv)F9i*cT>JoTrFcA8>4)BZr*TF3qK`}iNo-Dh#WybABH4wR$!BJ)qloIi-9@}@E!XkV&s@4<g34ov2Kg8aK!XNSM~w^?<i^{7(%o20G+!b=Q_u=|t04COzY=l&=Eq4oY(fAS9sto#4{lYd($AzJBb4-W!&fVYDrw}c0Q6?jc}5V#(^79=?s9s~{sSA$mvR|A{i6~HENX?PiMX>d7sS#UXUUR}=xdp;bO1?L0%z^j9+qc42mEx^+Kz|yONeZb}6mB8h}9*|@=cxABkieTwQ!O~s9ZeV9f@_oVnP%uk>0KN}?1b+^eF0c6!jwQRGAAG<*XtxX81MGozxWJvk&S;C|0=nnXRT7fy0WS{r09S(~m#1mNUKm~+TpZso4CTQzlU_i4{3qE3lI#RY&I>OI&I>LENv;e@_Jw<ZJ<wKPNOAxqIT&6Z91ISzyS5NWazjXR16}puCU^yK1zfWUl3W6k><kxRXRsUG1?+;paDyc0)74m4ZC!!zD&RnHCAb&361XfpAGj>I2qZZ_+zIT2e$Nj{E(%F511|<H1Fi_K46X>SqpK0TF1#|hGVW7dcmOy6_ognsE4?W^7#xiI)D&f;w}OX&Lva6E!Nb6f;LYG+;AY@9kmTm*f9b8^Vc;;-+Zx^g+!!7TZveK9p-_|w#r+ILUK^5J1Cm@7ZURd$0j>)6ggb*h!QOB;up92TH{1&>y$aYH><6z6u8lVN!K;F+;(UJS+j_ccLXxY)eZbYhrQij@rNHiRSFrR#V0Un7csX!sus`~?maZVUKiD5-f^dy~Xt!KrU9djB(e+Z-U(i3u{)PVoIXQ85Th|j^1@z;$y1&--3VI<pdoKh{tk?M5mgU#8$Ef2a>am?y@-z5t@C(%Y82$|W3}qfevR+xXi0;L8g}_UJr8fqLfLp^u!P47+r8fn)1~+ozYw)ry;7-i$@RDG6a0z%La0zg2cvEm~a07T7a075NNOD7XD7YcG4!kkA4%i!B3hWIo2rmvU2zG*s<6cWI0{$2M`vzVNEG5}?KVM>OyhL6AWqrZ7@p&N}`+{XIJwGJ53M9D(+!tH}8~`r{4gd$ji-3#Z-UmXG!{DvKVc`1kM&L%cm-XRZ;QHXga5+8-!{36XBzwYNfL~zTdg6MkfIY$f@ETx$a1(d{H~`nv1d`kw9tLg>t_!aZu8;QBg?oZMalX3nCgA39d7PrR|5shxp&xY3hf<KO*R@~QK4>GdOE{LFMeCZTs~0@luAU!|eXnbduF=p)WWB*MyQb^1t~<KU>bk1yrmo*~-PLtN*A-n)alBgB7F`)|d7P|kovvfL65;arN0d2(@@H^-8lRm;S=+Jv{GwgiTe|+hxn=wQ)b$Q+x~}US{3_bMRhOpg6eRg5BzXliO4ndW@|Te0nW)F2Yb|^xcrExF_$cr<;8pMy;1xLUDoFBf_*U>%)GN8GuJ*cm=<2Aeo38%4dg|(=tDUay@RsQNsk**{l9A2BeHa3bL-rlYo1p>7#-ZE*$c(HHSbpa-oU;Ym*hH72tDmkeXkWIjBwcGD$-^MY3Gi(223-quZH6xbZw9Bqmw?m2+u*U_L-6JBSnzPT3XcWH;`=Hjc?NtDcm{YDd;xeCcrNadyg$7l$<gq+;JGLt4N11mQ^_gt4PZI<<oa+Ho&rum8Ohh-=inQ_8_;*>;A!9+@ZaER;577?ZLUkd0^bI<^{;IWkbVn(2rTF1JzYoOx4^eh<_LT_Sb73jdN%kS{0=1f8ax|(5xy6m4VJzJd=Z`jUjxnnuZAScvE2tg7QO~7eHge8yeoVdSk41EABMuag1e&3P<R430oOlNd>o@gQIGVtkmS$c!^Ow>C%rp-I9R$WKCTVYd%{()^cmvgS|Yt4d<IzhEU@&sVCntA(!1DkHymf_TBd6kBzY+$c>*MP5+peeo&}Br{|re!2}wQy-vyTb6Zi!9I3zg}z6+cQPKPfA?}RUgF9lD8PlqoBFU9ptha^vdj{#2s4}v5QgiioZKwk`mBu7G$qu_DiDDY%>Ja{trTV1o^E8+3rP4HBBJUA7+10DyC!#&smNzQ?v1m}SN13v-&57-Jx{vCcC{5$vpJQI8Yd>)d#2c8bL-LpNA<b#mp1CZo}@Wo);eO(Ai{u+`z0+Ku)J{>$A_jNoZxi2I+96ksf4*ncI5d1l~GbFhKJQCai`~^G;9EJP+1teMS8M?wF;FH19zXjXIM+C}C{|Y`E+!fvjl5B<~kAu$!j|0zxBqzdGf^Fk35t6(Pk}UUsw)Oom{0#UEK0gfK1il9U1-=O^Jryi{2lyKNGJFSEdXD(G50?HXB>8W64p{nsz<-1DIPqRp`ct^fpF)!F!mZ%D;2ZGY!8gFy;TOQy!B^qu!B@dIA<38Ed%)5Uf-iw>?-!Cc!ViEqg4aWmW8e$H(!U1BfWL<%&w-Bs&jH)sM<n-#j|WTd3+@f>2ubb+4+nQ{@07>O`G5LPG(Y}Ro#g-9{|B4KZ#w>&$NrnI^twL$(Wi5JSNXf9$fN&HUc@T-Yn}KnA2p6T'

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
