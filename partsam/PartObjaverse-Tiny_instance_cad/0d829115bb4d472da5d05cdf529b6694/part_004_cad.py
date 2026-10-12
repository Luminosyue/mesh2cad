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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/0d829115bb4d472da5d05cdf529b6694/part_004.stl', 'relative_path': '0d829115bb4d472da5d05cdf529b6694/part_004.stl', 'source_sha256': 'c084fee4cbe866b46536145c4b9a47d9d24088295defb06d1bfd559357bfc0b8', 'input_faces': 546, 'input_vertices': 415, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.393018901348114, -0.4817200303077698, -0.3101256489753723], [0.1782878041267395, 0.2868534326553345, 0.3803081512451172]]}
GEOMETRY_BASE85 = 'c$}r233v`y-^M3I6%|S>r5J0pVhLi&B9GcBjVNl(6GWx8RqTRk?0c=Tn*_CsB($~EOq$r2M8w)+s+4}(D(%~9Des&!_nDqEnO@g-eV_OGzxVIC{hu>u&NgSx<9#E$6!!I(tUuMIqRpD?!vZ9U#4D1&G(L9B*to&5@eM|fp5!Byrat+@ba}U)T_gMWNaLj`0YhTr2agE|kpsepwg?E61BQ+oGj>eO$mmgHhQt!Tea!IqSksRm7Bf25{9LzbP;j8!<c&ais{DWaQ{1eA-Xh?dW~yRbK0?$8UAI_s^M@ubjv$|(oV-dtORchm`~p7m)pEV5uMB?l1uge}&Xc32dOmGo<=<|X>E^S1>7$C9H5XqGEwh=FFEy?#l%p6D&3F2qU4NyJe7)PPEA(^cqR08`GM|;N^mvi3x%i$sQU+~@>zP71a-%~jnv1VqI-J7i+x5)4m#(?^-c|S0NxpYloLGL@WSZ~vrSFqzzTwx!@@u4>=I_f`TVL>v=(e<;PG2d~p4L-sboDatOKs}W>pFeCT%c9Y+X>Y7rZmstugiS9zYeHh(e{t?3i-yUP05;z?=6>{%;&TAF>24F<tUFz3i)#V#c7(0uasGk#^>AZIlQe^&a|1A`1_KT{7l-O+IZ?K2`4WI?a6$0UqO$L)BN!MLcY@SqN=(0@~wQ8&$s)1|7BW^lu=SF=a0;Nnu~9Ib95h{Z;!WjiL@MV(c}4iJE-x&)_v8SpD*0+-QSMU{1su;mr}1@6#5Z9yI<pQ@iQb}E>=s(R}!>Mnv1WW_-d1o&*ppIA5PQu|M1#HK3}b}GF5Z&Jz1+#`Fwl)XU{&Zx%u_y(DIGM{EK|MdFzePdEXwlN@Lm%p3etd6z0XnZ%=71z7&4@6m9=AKjjJI#4kLXmftIv`ufb{mxS>H-(F89-#$;<=c|K4zPJ744VsIuE}go8&$rjN;KQ^W<92!;-)`QJr$>38-LF*P*-6dC_bSg$((zDotZ-dpUGyH!#aD;+*~91mv#xeLuetb2R41#RyP_=rLTEP4>$t}1r#q#ouf7PPzA~#9_2q^>d3^hOhb=tk<{K9lo}=~o`RWB>TrKg>;(gX%>Xd6IG&ldwwG$*?uQBKX-#&8dIcGH&U)ee5EFBNGTUzDdxhc(<Zr#ss!B%}<S#pIR56ripcUOWh&~eyL7V?eI-`8p`zB=>IwL(6dU*R$>N2&BAm-=`vtB1p_{+sn}E?<uP$=5sGd_DNa&Ir!8`>~1j+39<ReVa?i=ZTBCeEZ8!rdaE)!&hPw=z67omy|2aqqxvBnwy^&O4lD_;>29O-_<(SXQ%J!H<8vyjXs+rwA%;o9nv`8UI)_7<+%BtT4!@;IZ1jB-@l&MtaV4v?U=*Q3(t4==sLiBdp_puKBc+%dW$`DJyBl{&*A$^@1A6}pJvecB*oUd#*ZKG=);09zt?27=Hh!dH(O1|f6IR7`F8N`Z>ejXZ$DpF^gZwD|J|3)Uu97zp?qU+#qFAlue@7nJH4;43g`Itkx$*S=GVAQXN7V2bG0nZ#aDXESwcR0E?n4nR&(*aA)DxY)bCpJmDNY;p8Preo?qA*-uJYu_9gw^AH}J!tXO-UZ)bVc52txwO$l15x%kFUO;^(KUt-;9p`9mRI>!5UJLImlo>L#q63WqkFTYiD@xALSZYBBB*gdEC`m0?6GOhV-t?Mjb4$Ii@<{N(d_mgrwXL_F$=KGS~bp4m*>nDWz3|9_nF1`}+@j+Uj5s$5P;j_zM^X;ZSye#<2DQTJJ;_Lpt%V>WoiGuHuzqj^>4qrcZ&)OfZPdF~z?+L%7nv1XOE<vAz(vil;_;T33(dip67F+wqs`s;nen&gYox`*FeD!q70XJV?zxe>I=Q24<s3#ler~R{pe6+LEXYDLMQoo{~^KX2^x3d&8Pw>_4trux-{>8eB=zVQ#EBI3PSLlAj>3i0fqWcX`y)QF`e!+Y(_6BG2`EuHf-EO|#Yu0X3j(6w?UC2lKJAKyva-R^Lzb;#^q_n3;g>o>?ojx1qdhzo|#QU|@0i)%6);j)d_YJ;1l_Oz-@4fxjY|X_tCU%-l+vmjj!@MuGsj^CQ@jZ*>RkZyx`WzDa1<xb-?#T>Vk8a^NsUB%N-OV@3l${>I`|Gpm^S(ene3tL&nMQr7bE}*D{o4NOV^%qAzv|yZ$oFhJMBn$Fz8aoM-}h}F<rK(=&+_$ozQTQZ?^I3_eAHiFQ!z<%@mao-`pkNtX8Wk1TUY3OuXdOEY+odOnMr-Me+u>4zQypyS^m(b>HK{uWdb&8F1|kC&5c4n?yEpPYft3s3j(d{viFFxS1;51o43H42W)?yUy}Ozx;bfl`>=Bc+h^_bFTQ>L&_ko|k?c9{Sy}QD?VqwS`}q5k>wia|JGPJd|C_Jp-J#DTWnU6~Z?pF^U9VlFe)i$L!g%%%-XZv?r_?!ghvwq5e4|HS`u<_RPd$v!qyB_zyM+2@-lU(MzOmryE+L=Ymopze%a>~2r2As_d}RAu!zb0+FaI*zD*tAoaf08<kJe90|Ib*>#b^1Ryj?qla;8^XBKXMn{!np==Hjz_sZg^Wd^;PB57KsY`kpI?_6qrIeQ@T(XZeb!GTq<V`#QYGc}8#D#@Anct=k&S#W#j@UnAtB{sr>ceIZ{d@ecJp`<DyrmF*X*O!Mt^EcDu^e7<xbEHQ%jk*`#3mZ-V-EZ^KXZWZSHsc385JA8G$cb|~Y=7lq#t$WCqr_b5S*VEW}VX5Zg%fII@74lKf0{QS+zCQ0Y>a+a@I}edNAKt?Ei%0TJ7JSw(eGAcjm(yqYQbx>Xp`MK%(0+9K>am+^gnU*{XFhzEFTYWi`fNS-&TVm(_S@>Gbe*%$&HO7<U&=a?B8>B>+19?!;mft>qzU<KoICT`x{7@H{(kD)=Sz5w=#Sf5K6~GsTA%tx+I`x7_Wls(a(bZ@>f7fA9b)J@@A=U;neP|*^Dk(-JAJ+Xp)Eo_`lUcVe3q}Ay+qF=?Q^io1L*p%FPxwX^D94res=oGrtzwf&*q&opUp4idsDLMxuAUx^PpxvZJ*%4jl%q@(u6)2oxb!-lXM}U%`ay@e3tJSKArAo?Q^Ov2d#NC{#9$A%l3^p2lhlirROX5dl1e~jJQSA*Nac0=ck?$t#mivSU1aRj}68ezTLdlqv<$y`qBySW+5N#Rv@3PODun0n>E7x{bHxJZaREv#+GeDKAXSJeD<6|zBH``JwLGDi*c@~zvP$1&m*<0Z-(HrdDNh&wLf$CEMM8K(0#G2wxaLzo{0}G@V=pqu-@|ngRK5K){MSq+wY+`H#YA6xZJg096sw8<~y&;eCKt&4~s10=Px^-_ng1HROsKIW?Jj7!`GM2-YVp?{&nWFd4znqQOzZMKN@#-?ht&|j}bfQbK2>%eB*KUVtyWZHb!L#KHIOJ=}!C0>D&1;0vGY~h5i1bX04v@*8WbPwLkNn?a%xI{r+4|6y{5}tDg!!YtQYM>GRv^vwZK=O4IpqtBgFEA@~@dwm%_tGOcIbhV&dnZMXBB;3q~~=l<(nvEDyA6(1+`SGm1A1)uc`eCgv+k6Mv>D*3{G#`f9sv}(6)e7?ONp533p`}X@aeqXbFcAkLWr)-~{|KN8VyL>j^@q2{rV?AW&(#*HdIa}uD3HfaQKRzs9xGwuWYr}*~yl?*wn4NH0Xdm`Gebo7i;Irp1d%t7XW%~i_6YT4<_rWK<1m8Jsojx14%y*7k<~zr&T_5&5a`czI|8exMa=xFik5#+>JT}5*T-m;3TzQiRO`zre`ZXQ5daZlsc;CA{*IG9>#!z4F+GkRP%Q&}v$2j*yh12r`=RC4~=R6wO*xGkH=CAEL=Ba*S{`?4+esTKta~8g{UzlHDJ^wY_I`?v{W76Z#=sARQowR+&dZ=z{x<u#~thcuBScg5iIZOF=u%8RecdY;3N6)G6eD28KTwmtazsz^`uW|40a<}$$`u6h?eu3vB`~u_rWJ7w+?R+ll1Lm!A?HBmYa+IUxllXCE?-Q8s*gr^05d9s)xj&I2-d@A^i@l#=zGI)G^!#CsFg~%rvVF(CORc_Yty_CKeS6)g;Jc2hV?QYeR@%UiL$?3)R-a4#0{hkGwKwwP)7}p=-?8siwtPu{Z+Gsuz4xZ5{Qa{1xzaVyQpbCNcZ5$e-=6k+MB+y3JKtZ7#&?tXam(I!jQBS6{K@%#B(*(g`HuG~wMu3RKOWfom+d>>%YJ=9edqh2I-`QspN{uO@0}`J`EkqMi}i@xTlsco@9DPhcz;(iD{SY-Av+II`-kk{>(9<l^pxv6`SHNck@Sl<cJbF`=T3U+z&-qUVCP+)Mk`YJ{$=NEhLX9D??-mNr+l_3jqfk}T=8IobiQBMIi#{)P3QZCor@Z8-%ID)*?#~1=6O2b&g{9YG^?)B>&AsyzwcJ*K%XaahdG(NFAe>T?nAs~n$me7FKKG6cfESi-v^}wf!Tt;v9PtyO}~~cl%F)1{=TNv$U82SZ<Ib65h?sDy@invqAFIBBof6We`#n8_fPbQN&YZ(|0jBJP5)Q_L@&5$v;Xfu(QED_NzKgY1?>rb-;5q+41>N4USq~OGuA@abG!kciEaeHZAMo!8bTX^N18Fpj1Qs1!2`?~i0=)=cL-NALpGxlv@-Yue0L&r6u2t#8bBL?`=i_spu@opkkbX)72E~fA36|R5_PBwmBAmP%mL7WU{a?ExE9ek@CV@j(0<_lU~>H`D7!wi0k}T6Gqel13%=VK`BhL~qOX7(;y$ZEWpFohOtv%QU1)nSiJ_A9_e2MQ3!72M3?HZjZfyS7n`Q(+D}sp@1rx0W{?+_W5mU?fSXu*2Gz3g?h<+<sLD&y}7Xto|>3?U2zmKJ*eJu7v&Qr<ar_w*=5Wa{Yd=l{#H$#+smvCv6`!}w02~6}fm}ns%i#wR{wiyu!!kwZ0z@5Q;5QK-AF$Ve}v>*6GuowC^*b5#2?EoGC?u{VahV&7%8MFhq1L{inp&60py*x1Wm}Kc`!~@*t1LPD!MB?86hELjzd^Z!{$waw?$C>f58PgDi=R+5P=Yv-x2(N{H0$vN=08IjK0B<s5D|9_H3A`S>1VMNq^b_zx@LcF3@FLW8E`sn>=s56H@Mr|#56p;$j)jf`k3(A!zH7#3W?Y3H0Tb21M1KMkC1dp}^e+5|X!q;TFTwZFN7tbb;gi4r0{jK?SU&lD0h$KBh3{X0-h)s6elK`0@(ABR-g#5EOP20MoJZby<lI8eE_l1}eZt@1KF>jKN){XVZjPxtBujT8a`62e<lI0`D!f#DpKw_-Dw<IlLAVyQI=B|N0kj^t0XPiW5*!AOg1!Te0>?q$2giXYLdSzAf@eWzfM<bMK$n46fKw2JRWp*I%c0A_%fU0DGr%*!6QJY46Triu?}LYdyF=drcL#?;TY^Ku^`Z5^^}#iv)xkBvm7o>DmB9YcvS5F3Noa9!N$|@E!bK#qiL=xXS{&>LE(a|OCR!O>4qO#MH~?A;8~_f2HUI~K--3pL-val7MuB^QM?&MkBf$yKiQokA9Ox|Y9PldW3h*lM7HA513wRHL@HVIl-Ui+&{WIovA_#wK#%}0lXfk*+cqMc>cqMo?bS8K<cnWj^cnWv~bQpL9xF@tbxF@(ZG!)z#+z479+z4C;S`%CcTm@PQTm@Vn>JKgteid30{3^H<^kr}<a0vwAm!L(!FM)lff5x;gf^boZ{7;H3Ee$OOE)6aN^#hjySAdoS6Rip+>+?CTuL-m9KzI-ICU_q-7kU#+l&tT$$RYYUg7EiHl0*2uWUcLarlw1lrXmO%P?BRH=ODa;_<kPBC1qZN{w!Hc&QQNH<7?<I;EiT1He;O`YoH6Di@^)P(-DLd&6o#W3SA6djB*LLHKU0c9ih#^9l>3p9&lH1e=}mCU7#Lt3urLZ0}cki32hF36I>VC1Y8$f8$q}sv@N(HI2=LvJp|!_(2n4N;23CEa13}jv_E(_IG(%bcm(0e&{5#YU<E;Vk{KUC2SZ1J2ZQ@UW5Ka#yS`kT_C*lxWJW7!Q)mltQ}7$mVDKAY8Tuwz23LdD1y=*V4y_G-9sC-Ca1Cffa1C%EG#nfV4lyGV+5;L64oCkHCi8>Llm9U_Te9>Ng0K(%j^q#~^M=fyAEC#=WPXwPbPz%KK7ufrw?uyd7sh+XkNErx$|+^?ZBw5~mga-=QKx56QkQ4Y5HQhF;LB#*G2=P(RUeCgL%C&f9g<JDrWr4RiT;M1QYgPHv?iF8N6IY+{T)p7Wgm-))&|$c=ep3>z?V_SGYG<k(LT@7HqTN2NL;rZn3YSo3A8S>Hke$e9=IOz>O#rqme64EEHgToF%#MzJQJJ<Z3j*SE6}!J1w0Mf20RTs1^O0v3V0H<HFy$u4AcW210Dg50FM9<MG$UfMs?`x&<ODB;POxpxIDN7v^BT{xES;;a51niv<=u7{6ey{Etmx1zo6~FBnUr&wg;0S{0FoHm;~X+k`;tI;_qjHJA&sT2(LmAUJ0EEUI|_SO$4t1FNZ4N<=|z|Y2anxrO+whrQjvdN#G^mMbI(eMd10+5#agY8PK8N8Q{qX!qL!H;An6-H$K7<gagee4*gTIv^tms;UA!{gGms+0xb_FLHI1R1egTj6VPH{5`?p$zF-oBH7FTF8iMd)=wIN&;6u<S;6va8&_BQj!26+(!TZ4(2*Qt`WNbacXTqH@-sXZkf#;dA8kz*13!aOyNI1xh7G}JGAlwu|I1CyJ?hWk@4Fw0``*oldz(ijH6Rim*8Un5Z4nl<Bnk~Sgh!9+>H`I$D+y@#0ChKcAA8U<m34RAbI12h6c!(JZW(>mj2XW;S9t}+Z_rbLWL5G0*nh|5hVCY9+qEo>{W5MIhSYSpx%817`62P;e3&2Bgy?E$2@OU5VIW*RcInb$yvAEt?<isK(QHR0czG#mav`GxSC}<=&3e4Iwl51!7Y$SD9h-)rH{Rl6{y?hKE2Ofv}`4~AwKS2<l4h;cEcJV3XU-;ktuOI&TL)J%0_&<VhepCE8ivQ-PW?A-+Q;}VYkat9>koh07`Tess`Sf3ujZMe'

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
