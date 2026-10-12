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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/404f12ba60f444bca620c4405ef50bab/part_001.stl', 'relative_path': '404f12ba60f444bca620c4405ef50bab/part_001.stl', 'source_sha256': 'f06e26cdbfbfbe4802990ec11d0dc26953b3d2fd2a142512e5ecc52912e9d93a', 'input_faces': 774, 'input_vertices': 466, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.24951279163360596, -0.3738255500793457, -0.2545579969882965], [0.47711217403411865, -0.12879177927970886, 0.24280919134616852]]}
GEOMETRY_BASE85 = 'c$}r22bdMr*~jOCsDKT{LX(Sv6j4EGF$h-?LQz~00j2DvEFirpDxz13aV?1SBIQbzCMZZ*2wst5D9ai|66@Lv(IC+n6QbXF@A;j{%zG!#^F80UdEV#$oBy17=bZP<Id|?ZF|SkE(<*!Rr<QlL&w|m78hW0@SzcxD-h#2??;cPv?&^`F?~i%sWqtW^I-~O)x8~g$^X~N~)*V<dZot^O*T?I&9Mqz2!+706qsERO+izt4sIdbJ#BbMc__zY&j~mi&bb&dp*Q8mqhVkp_H;hk;{~v!UNFU0dINaJurm)@aS4DrQd+5~&KUshIfslXjTI(OJ7xLp*Hp=?x-X-BY(|&qA>-XHcKj@eC|2FG;jT6N|->a6k{>Obo?bE{xvwmjgh*0~)qHApXm32bx6IYy>^%D!ahTC`CxGQ^nyi%yWH~9XnpPqIy)PL{Wp^@z~d4GIOj!SQB5b~1^+gpFx=y3mkdMA_3f9(CRKYM1@_f8EC*SYnBw*8_;2c!JNJkR=z|MX^XzT(~L9E$S&d33&>M|?MrsR6~IJc&!I+4ddwgzlUEvXXs%s;vs;Nvy44{nW%zo_Mjh+a9+F_eVb``0hDLl(s4k-S=>D)=#xL7HaQZeb7E9PktY|Z_ab&`nmh@tY6w@cqo6o(IZ(uzU+xm`&8jzd*2pyLhW;&L)Xu@YTEY8dxZSt(bKKpsY@tND*b8pc}p!iBb;A9x2`@t)@S|rQ|&^2X2gW7pPYLlREN^SQIYL)o^#j!+b-5$zc`#{*T>oCJelYnzOP;vuKyPg&id({^TTz}>&4~SUM}mWcAW~>Q?DbJf7aftA0K&N=(+MrH(0+(xzKYPZ@V_@C%>v1exCJubp6rmQTc8?rk>t<Bx*fs->paASL@OFdObQ{uSe(W_2{=(>(S4z)}!AawH}?X*Q0-5wH}?X*Q4*N_2~Cgtw+C~YCSq%uSY+RT91A|)p~TkUXOl$wI2QaYCZb(QR~sKr&^DGd$k_@`l$8jw^!@Y_tkpz@2l3M-+#3p{W_@i=;u-E(XXdkkA8l&9{q8t_2|#9T91BywI2QcsP(9Q|MT&IxkrQR&VSEQzW@2?eEs=|pYxvM+Uw6R{G9h3{G87t{G9h3{G87h=j-<z=j+c4cVGRU<9xmUyK(9L96x8@cKz4;v-9=7>hkM-RrzinGgI^5&HC?d_+z%+_?|^UKQZBjte>gSu_SxGWPtT|zi->uyR#_d|827MGd;3?0zZ>~H0!6E+dR%scbu5@Q}1`Mew8t{edY2;vi?z<-}&AbJ+ti-7uftM=MVR??MwUH{LW9b%FDJ-zHIZSdi~DkKhY@LK5@@oMM2+dUoY!tp6nQE?^SGU>oBf+sC}Y;J=^~$$$!pL>t}AadAwdlK|l55*|z^*++pkN{EItf+o#vr`#L`}y_~)8VCwV19^1a~yEn6SzQ^Wqe(8r_X8qERv@iN5>nGd2XWPeVkDpn1B<rV}+V+{fm%Nu9@4t&}`{Uh;f_`f5-mIUhNB;F~vwmjB{;Z$*vu*EuuktRNr?zeH<+rzfl_|Df1LNDHeD6T_SEBsPqSmt_+jkq@w{?V{s8aB3l%I+HxG~C)pK84~vi;#F_eJ@s&sV<@<tHzjbTG>I@+%(>`lXj}-}{elj`B10Ki?Yk;|Hc5imHS2Jw0CM>pDAM*V*}bs-Et?x^DOh)qlUe>c8J!*BL*p>Q=g+JgWZA*Y$V4uCw>?zq0#XVzGLD@N=FY*Iw5XU)Q1ZBl4&^`@X8P^K<4Mzf{%DZ?Ed+{G2-A>w0GJbL#owkm!Em>$*8Vr$6{P_jUPIot>}i?0j8k=j*yTU)RmgqsHreUAMIBr<%w3tDo$Ps)O@$)&+jfbLH~r=L%ns%lSF$$hFt?-^qRTJmTlfJHD$!!sXxfmt(;^+IMxxY0r3b+B075ySi!L)gh-nb;xN?9dg<;UhV7gW*V<P8Z}<$>+$;S)wrCm$K`xIF2B7Rm-BT$)9${i&d%3$aK5fXY4@An3O?sKzN&-s^*lO1r=G68uA9rR`tSUly5Z;4&9&EcbL~|f{PwC2&UgD&PCxk^@%_Rs_PtR*C(hU7b-sR1@N>qCU#iE2pEEA}q^>`HN{uV+`lIIE`8m&(yRWLh^V6!HetYVc8qoCpsCqj8zqNPoKf1mCd`~6kWc_&Ic>A2MD&F*J!1wSIwUcv#etJgjx1!oRU$^(3X=CfNTII*r?c>K^EQ!kR`<JW!ymxMKWPhAbd#~1En@4}{;Oozqg!A=&u6+Nw)$QH$pxghK{QmQdpR=zjU*9)ppH#lT-tlwxL+z`6ruF`;e1CoE_U<`XzQ6Cee(HTy`??N#pVaNuxH5XbRldKEIbZKf%1^2GIs1e5RsVDL4do|QKlS%J?Yr+a+SlXN-?N<W_KlS4zrUZTe(LX2etz}+D96uJ>q32h@$b7o{QXP&dR+Q@M2@feuix|i`BmQw{Pya-UHdtC)O)-3^**5A+qGY+)~|j)*S_w*em~c~zi;&T&dy76jNJ!neg9CDpBdI;R+OJQb<?IOzqHm5k@@|7N%`@{YxYFu8U4}T$bMdWVqeftG^lC!fy=`EcYaFs-}y<^f9LD|J74$TZ?F34{J838x>9+Yr^6%LqWsduqxVGl@q1^5@~1|1Jrb42`8tpDb)M4hEssRi&H1`+&ewJG^Qd`rzOGNk`Kr#ouj=f4J@1*0OG={p?|l8-I$!tS`8oY@d31m9^>gd@XN(%J^Hu-7;`^*$WoBWd|7PoXQGVvKhc`v}iF?l364_p_JD2~T4faI&$&%Yb{ZGD8#s2+C_0#zY)jr*czx%3r@qJaF6uw?BsU=GfMb*dox}T}R1-8A~$9!MiH;J$Bo0-)x^m{q&>-(nhbw7Py&7<@6Jo@d`yrl5;{3a&9b1-V1I$y6N=j-RzZ?D#A9AD3)^YuD%zOJX|^0U6Y@)bYGj_b8k_V@gS`-`Id(tm%qJJNsq#GasUKHy8D@;Kl7Ih@D$kJ&t#nw4z+ugcl?%r>RlqWnzrTO!-1ek#}-^wV?hI1-h|`8tpDT^=w0x~!ksU&s0j=WmPh6HgWFiSpyk9}nkwduvH#9{i-vgYWXB7B{uyJ>yKf4^JId6zLDTXit=%+<9p@&lPW%MCQSd>pb`_Ph!DMb{>Zo*gRjKHzUeVWlk-M@{=_VY>M&|i)wF)^izM{8s(=OkKP^WcbK#%=w}vRRUFkH=j;ABU+4GpsQhVsT?gmuarwR)SLUJ2p~!yXXLNt?^?1{+{a30#_<Fp~*ZoO3U-dt8bGPU`_&MWszRK@>Juc_#aiv^)H7@77x}}~Qne~%3>hrmI+ABdnfuCvAU`eE3<LWI@e(Kn^t&#0pz5II6kAJ!6P}F@re0^WvSNC<kzOUb&`+7?!*?CdlyS4BCy#qhz?^DWm?K8Jdws}ro9m=nL-QJtAIWkY_^v$9BW+pvu>-l-D;!u11IKJP{hpeC8@l)vgyY}7h4N|cuY=72oi1bTe+z`s+eEs_e=j-1a`1#fMeLw#t;olGV`KxXWjn~hQpKYHP`q#!M`%d2eMs3fNDDPGF2K5X4Q)4mZ$7%FGHNLya|LUI_H*enL|NBpkQ>G6Ons^kQ6yW<f7JVSV<2e?+H^5^#79AJhdpH)I5a9bc7M&R2hd35}IKYo^EIK*BzvWo;u>k*$W6{S0T*$HL69ImbW6`JJGfb58WFl<{S47LgWtsYlg#1(@<mY@e2A>a~hn9iQgU>}zgU^M}K~IOzfzL+IgheaBXTxWi7-V9IiGk=)cp%)L5Y9(O!=hv0d^m}Yf|GDRbR^sl9)OO32fzjBaJT>-j1Geb!*`pgPpzAymEhY<bTZKuy(PfyI2LUm;F~xWy*a=wITmdl;9qepdIK!~&w(rGmuQ^;U&gU$JiwQ7ELuIlRX7&CD8LtUEP4Ulm2osguLy8^j@xrT$2W6)Gxu}cn&Z~o&+!c$-@v_vhfwRGa3_uj!9(D791nyC!8dW-A07y|<XAYL<9uq}lG;_Iw!-B(j>C1}GdQje$Ki4uUj$c&%W`}XwJnQ!@HHkHnYaqQ8Xn5HN27h<+f8&caR=HRZtB_Rv<cb*zRN^k6TQ$raGr@S<m*B%;Z`QDH<3Vp4PRoSGV@fKF$h;RaUtg~<lH5ULB`Smy%KH!*E4as3Hi9Hi`Ikd(WWl_@5NYpG0rC3<6`<NdIK!icIG~v8K>}_<hl-R0{7rtWAr-s4$fVJHimEK+*Rl`a31FxpjW|F>8q<@E4T*d+Mo%z7UzD0wt;JNt|R&zxE|*^qa9)CTX*^{+7p(2Ri2~1XdhUv>%g_5x5Dx{;xVuCa{(;%xR&vYHiG3k*+;ve!(i##<@8;&COnEh^+x-`J?QhDXm5BV*Yret!%~m7jH4}M5FWub-O-+~%yTow(Tp(&59gY0Xm_|4eXfC4gNJcV7qlCECw;pM?F*NorWc}>VVUO}8OM!`LHIPTsfJz%%k$fUakO9z!l!dhO|)8|-@;YV3*j@l=5n+q+?lz|L%YBgxTY?8Ih^q9UeN}<5tel+du%K8diYl6=x%gyfZK8`S`gqHITjrd;9qkr+AqM@b1a$+@UJ))&4*>bk$vhc^y~mP;#l;Y0AI_o=(z!I#<A#m0dB#u==rdGrpjkdQ?xl;fx4cBUI};QnqFvASfUT-MQ?*!kn?=B5?o>)zG4%53E|y@@M~yo_%*nJiTx)2VB#S9IxPAsELs&l2v;}pripzf4x@Wu(F`ow5IziFZsLH6LnhuJgm)3bJJC426Ru+7@1E_$m*^Ls<$ri~TtA}K;n^l;nOKf4ftSNSp;8aw3}bi=-5ub49Pgvnj^E^1v;;oD*!H7;2=FeBcTsD{J2~D--CyV44X9-UYM5azsx!CMnN#8Aj7i4*cWUz^`UCtU{10?CJezBUcT(?H(W-DUb9s<4?q{y{;~hc|!~Zt9E;jlLS`GfEiHe5*g`Ne=W?IX{&z{vw;h53OOq50I!g5a9oI)>xCD&QpU-V*F!ks@wKZGS$nV7wgs0YX3U+A0M?-$}{^8HLM;Xj%<V&V<-4*~u&$D;dTi8Erhjp*sHoIf*W&x@V`%YCcSuWHmnc#q7PiI>rh0nTtNx*2}oL@E6(rGJh;;`k%_D!jnNJQGvUX9B#CW6`N_S>~t=S`U^w$sGL?tq6Z*;%oZ#HT`gWlH-%~Nw^F-J+v0Q#>fi#yMq2XUdi!F`YQa2xn{A6O=ub}GO;3N&#&N|@D90$iS6iGc(aLRCbpo<;Z5Y+hOUOUbM0ny8NAiR^Co_eu7tPIC)c-E;NR1yt;7!QyMudd3G`3+H8W=Uz0?+TEBt|pk4?OV9);(dSY+Z^bQ-+Q<hsYiMsz&<YZK?1Xo;Q&-)y1{+=h0-b4?^o%tQOZT}<S0T^`p6KWJi{iTlv;u*}a=u3bvrdCc7^&adK}u#9~d;}_iq%h*3*{GxBe51VVQH!;aX6Ykj*odi#!jj+^eG4&Fi1NSoL2AH@D?GL|bVnWQ;bpkbA$Na8jK3DS0?ciCGam+{O!Skr$e6&AYiMgnNmWNL>QI0;BV{F20srL<NOSmQ1-+)$vrG~FlN6{kqesiu_%+{|N^?8_U<l0u~+3<Y&{2V#}zK^+{gx&*Bf*(dFz`acjjM;h*B#-cV6Jx0N7}^U@G|}9|188ITGc$(IO}vA?3-30u*Tg1tJNyo94x=S-Ym@676AAQuc$$g6CZ0w6z|Wg&mYSH3&VZjb=enDig5C~KH8G28MQ6j)WA>UE=oI)d6LU=b7M%^JxaJXb2K=OnCrmt!{tkZ1#BH1x?F`HLj<gZ&1j`r)F;39}cmeaY5G{aTGBMV~2J~K7_A=RHx1!I(!(#RwX*AjhUSeX1i5Jij@XIl~kE}w6!?Mp@XJRCJHT)|Rzc=%66}lSEkJ)$IVQ52m5#wBf4uRzwx%Nu*IrtT$*UA{tYhVfCC1?X!u3f|RYxt}a9!a0?M(e{pV|Jgt8yyVG=Zkzc6`?EORn%lDIv8FG&qb5)2IgozItE_IoGwBK!Sb0go_QG09K6hYF6X+1@B(xhya1N{VLqBhm%(XxHM$mF#TZ{ER?wFfoZm<YuS3_u>);pBHSmk@dUPec9+uj?guZ~TgkOM{pwGig;6>;{xDR#gjShr|#_TiJ7aauO&s;o!-U~kf%l`KeIvO1XkA{a4qXPF49f6L5N5EsziSR`3B`kaN1o}0BJ_*aSD9_VKbT~W`eh?i8%bp^8OCfp-EPK?gF}n|mc7$bb>dg7hoD+VEbA{;R@a?qghTaBugWIFG!1AtAGiKjcL@$Bm-Ss%{ug7`c68?^N-}lh>Vfh{=Yy2N*ZCJiv%J<A-^e|i_W^-MLz6Tf5x2MqC;G0ZTHqimC0?S@6d;X*7Ojte}<TGM2It!i*r_kweid?SEBjk7tbvYk_ALU+;p>tsA!xTKxXW(b)$24>fJd-wa&}s0~^ld6S3zq23dC~6hGtBWcv@bk`XW|*O8!Y?k70mw?%)PKY&-FQ9pL4<sdAFX5J_|4N?7lt|odrL~-u^T?1(xsf^8NqsXjNFA3;7&6gvQ}IF?(GN^gCESd*mK<(5K;i#@-`lpYINgxdUD|v@b0C!%(gpil0xLI2@->`Q)j>`6`?fmOWhF*%qJ!;k0Mpjpm}$;ic4W209a#=cEtw+=n?9mi<=tsh7~Pu)LGWyV;HC1+eUmEn;>L6KxL5JK=}C>xupemUqH^ycde@fZwG}3Hm1djfrnfd`bv^hJFu!27iwJ75*Il5Iq5Z2)o~riT;3|fPa8z6DN4)PLOLB@mFg4SMEKN_?|j{PhV#c-!eDfGPdc&H_Vsl-{5s7Ui9qTrs3z&m*D5&rRaKiDeTsb=mvDX_n&ts;a7<D%*T3i?I2!aj$Y#4+X>-K=sI{4T!gNLi{NeODtH^b6@3BT3d?tJd7qTu*{mjn*Pt8WHSh{_GrR&`iEe?nkbfm1ypRx{kFJ8}!;8?h@FI9Ix(;5)oGm7V=b&@pxy<z(^e^xnSiTp_ej|I@cZBd)=rizF@Ym>6_-pti`Ye1BK8{X<r*YrogzyK1@W<%i;E&-?&~ISTPvKACx6xy;{0>Eae{g^hK8U^zAA}E~$KXS7G5QWHdKi}P+VWkr2;BrrA3o!{&$veTH)hYe!$do@D=go~<@<MAv>n`zHtzQUqFvCgu;`t!|NPFT3!iaa@P+d_#mZDJ```YPi~sqN_XaQYA7Ip1hX46g@XC=Um;aBc@;a51zk_*Y%>U#Ml4ImAU*7)!85j6='

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
