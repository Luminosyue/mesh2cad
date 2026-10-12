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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/9f43d0ac857541e8a3a92e20ba284c44/part_007.stl', 'relative_path': '9f43d0ac857541e8a3a92e20ba284c44/part_007.stl', 'source_sha256': '00f8f5dbd8f5ef6bf07dc9602f19367153188d7ed8c8d6ff6978cc16b9cd8789', 'input_faces': 568, 'input_vertices': 342, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.06309795379638672, -0.2923002243041992, -0.041210073977708817], [0.08621544390916824, -0.06949794292449951, 0.056661054491996765]]}
GEOMETRY_BASE85 = 'c$}r130P0r|Hp5HNZGPiZbGGn$R4gGB#~`o|0Y?oMM9J1n(UG6lI4q(r7Vdt7%pR(?Ayrh%Zz2_$1s=~Kg-Oo^ZC4^&TszD^MC&Tp6BztU*EU${oHfUJ@?#m&-n@oDr)VZ@SlrPugs*#BvnyFlvW&+Nf8q!jtq~8_8A)$Yo(MWU;O3kvaY>@L;6}Nlax5Op%KyH6Wp4sZvMlXx_PN?!^TaRI3aB8;Bga%MhL${*y!kpJU@CwSX4ybXZMDF4ZPHb9$xA+_5b)+O4Omg+wP-zVpLjkL8vw`b9`%|yH4*CpY;bz&IwhcZbS=TciKU|wsj8q#`%uZ>GQ>r?9Xt!BvkpBwnUUy_WZq*%9WXThVtBd7(@Qr_v9-<DRf+Y;!7%TIR8k#etRU9*Zi)3Nvgzho@(p(xFdQjrSgB2XTQ2P9oOtIa0AtUMouQ>SvmZB@@+a#CcpPF^0lry<u{j1r98^>4E6^Opz>Pmf+_U<8(TTgtTb+)L(?d~(Y-F0@3occqbH=1ua`WKLFYAbD*4L%@k^<GXLhiEX#(X}`#j>~zWa)N!?flU<-61{mg@OvI{R}IxSq3fDZkQc5c^(9R9?-w6GNX*IgqcX52o^_{XZvBzDkKZNUf*QaTQO+O!=)Au)iXe^VDp;jLs`Fmi@7<P71XQEHRDBzv@N4(%g@H^=-s>`W)j=zOl6)wZHMENg9>^rZV}uPfu=7>(z^?ynbstmD`+gf!p7o%3Gqgkgu)lNcqjpZ*hHWmaw0*lj^B#tzs_dD>v($pnQAV%%nVBMsxY?PULG=N5knnnv7t7Y$ji?{Nwg1#r63(hx0EvvWVJm?t^Vq?m{ifqkD{5PRH%^1Np|rBx+|%gZ7k1t#O`w?Q(Z+x30~&ox`_sp0gg`(Z6^4X%=0_%L$xkp%eMak<%?HPxZ!}r>xgWKJRM@^!?Mdx%`64R3B3>8_NI5cPLJIOu=bXPjjP^d|cOfYJYt|7pkX`_;f3k&+LDk^!4$%blf`E$kzvVAzur089{lpbn>+(CAgg}F7xO(-zAc-n5t2E_1y|OuG;@g&j0GlG5Yt#0rRMyz7yDw&ZhFFJ>Aw*`<IC1<1Ri*<;_0djV1qX80YW%fXXX_KI&AiW=qbKy&UEJ>A1RGGtTogoA0CXA!!ADCFU8GH@f>xq|X&>IM0d!<m<L|N7H$Xev(f9>;&>nql4Gdb=-ZNe7#!?^&gY>;1p8lH1ah=q4Mg`8Y$Gy_mer#%RY1+^^TpWKITIv&f}A1(Dx_0$5VYqgpjYqhjPDq{cbhoEoRH*zp$hBS3~!0q53?yoJQrRdvcz`j?^F2D{IL&N_L^^ZiIARMR_VsAzv@Q>?nP9enkCB*%{7x0%G|(MtP))Jf?Ad$k)#J@p%O#E}-`Q(~kWz8GKx;8k?v-ZjZK*e{%-4zrNOMCFMPOiF`ey#}WGMmb8)D!6uIVx@p`G%jVE{W!e`>zS3dRw{*O>-sBsT2C@IF7PY6T{>&A0ys6&oUwh5{-@4jz^4DHWCBMlzI$u>8u!Pj_5c&GT+K1`igL0@oYU{pSK0Ti5so!tEnfg!N-t5;2JVf;<!Q+^z&XLXB-@>V$TEL)X^zT<P$yfFlKS=t+*E|lq?#6zm|2L$e@8{F`Ww+xzkF2RahP@*l*YG~MiTpO+2gvVLZXI2hPOHgRa;|WG{VF|Ql#P?Qe947h^Zk-IgU_b}`^^^6aaEUNbiR5<MfL+P?Wg=UuT~0QS!dZuzSSV|_3Fh#NH^_bzp*v@6Q3l~eHy-bBln+Zo+oUurq5cp4eUqV-A8(O)>OLg%~RM<$fbJfyADu$=KK2HT9jXH|7s@rR)g68*SF-GPbF|W><ngq$`^FM7}X!Fr|<bT;{0bq>A2=bkt^tYU%9jIP?YO)&dWsi*<MGk@0(IQp6u(fmD)e`iJ9_`nVwDg(<5pAU|Rem`O5FB$yYAqCQyF2i|oJa#Lv6>N7hpQoKW&L`?fs(#KiOcxUU!IKM_awi}BZ78c)<A?K#i=TGVfix-HWwziU(Wi*MlZ@bWPlAIvRn+4q>5Mf%I0G1NaDin5=p^7vD#4&^uWM;qw)2Y;peMgMKV8qz*@$yZjo?d9vecou2V^X$*7OZj!TNAz4!24;}2M_xb5_wh!mk3J-h%a_?k<t^>!CsF@z7R}`^HRU{EFXE}411)sjl<N(-|Hu8x<C|{)`TCZ(IIp?fKP%i`NB(Ooy6@CE_mk;+D~_}OzAE)|(}i5RkF<_6*^i9p^LlFVyr}F{x<1O9N7Nro_nhdyP_Cs@J1J`~@_qUTkHdPJ#_ja))GV&&K^o_^$kB9sT^&mOQ+bm@*Vm{WNvd~z%=Pcd<FMtB506`&C-OYDe+b?G=D=(ox1xLVd@qvwz4@LE`NoS5Ja25~&i(1c7#eSsgR%U))2dPXnp_>p*Uvfgb?@*qx9??J9-jg;`1yXqippE2zF*4y@Fn#J19{AUKjeAqu%6U!wKnYQnj4QdZ7y*Cy!;pUr=%N6e4SG0I+~~WQ9TX6dWrPC&DUuh(~dUa{^2leA!$ViY9H017hMl+Y8KCTQk?j@yo%-PS4^Eu<uT5f{L*<GKU-}Q`D1%gyXpIf^Z2-VFFoh=UjlgEd#^0t|0fnjQ@ygM@N?>94Bv;Yw&ZK4op}DadpzGiw{j*FY#+7dQ9iHv^VlD>o7z*)&u>1#^WvGIJpWlSjQw-|QH9!V?<MvdIFBL?o<{Aazq-TYTDPe~$=`Zz4}G5J&DZf{Bbv`DMP_q*4)EYSSKACC9kGkXCH-+_?k5{ldA^BuGf%C$rI3$y)7tIZRM5|FH?>ITjRpPub~FE#RXG1~M}985A1dVMx10Xjp-`Sr?RIrSAzzu(m;2k@8->dUU7~igJZ@E}o=WHp?r*h&3j6u((><YZezcD^D6DY(*Po$w*6MYocGgztD+`v-Z%?Cs(N%@==eK_mFZQMDrL|I4xBiFgtL)gpzT6+ocFC>(q5tS>S|t~1xBUM0ylZm7cFymgN}Ivt%l+B(WJYqq>zLpF)xkN*1+V+3`^D3BO~HPWe}5U1hps8uuk!Cl^>%ZfUr6__W(?=?Rl46zHn+IEG(Kpv4${0*9#8b!VVeuJ8^#~Yp`$!+lE<reXEzsYpZxL7aJ|OmrSZ@RzQg6E@l$gyM)P8Myw$h&AYUGzEvBvH%j0?8^M-wC{8zdb<@Xiod7+NC=I6ike9;z<WnX?C)vihN7y0?6wO`1-^t?0Qx8Fv2r01hDryl##^VEEz1^d$T*L*FCeffDEc7%NS`EI^ZVmp<W<^$SuTk_@kgC1Fn%S-bO<6A#2FU?PkC;se9^BL0zjeL3jWA4_S%S-bmb8KJsrTLXUcn<s0d`w%nlznObX8LUt*I%0NS&F4|eWdxJF~n&H<&ox-rnA26OY={~(ujO{zG`_9NxnS4)qN&&9%(+TjgDtuo<IMb!uh57wz*{n`_lZ}nDjH}k>>gNzC6!2B|PWy())sC!*A?M?-%;LkDNz(A2EFGGpPKtWWKLEU*P_C(}#Tdy+(Z+&c5^>WInKv^XL`ny<2guO~*4oT+ZdC_bK)6N%p1pFFpP-=aJsm)MxM5f83kbc~Y-Ye$&VbnUqI*?^6QDlW*MEL;c5ew;X+6d%1+mOYe^spY`O+@0%w359~|tr%JHRPSX5!Lf@KvK0`{AFTdxi-8XRgY4dsh;ONZdhiztGdS6!K(%F~ZuhpoMyXbq;`?!`|j{U$iUav!bORf|7@_W5DbQJl<^ew!ejQX1n#Bq6PeZa`dU|(8KQ0`>!;^TYKdZwvE9m->Vd4S7H>k{VnIb2U^9Ygc8+D+xpJ>vE7UCp_Drj;RIUJudtR3%?tKQUMJVP9HrG5a*&{F7&0rgk_oj`RP}gUd_nHpZJ!E-$U~s2<^5A8B1kZx}(o@wD<4@!6v8<Ni7~hJ9&$$!wp*`K9$JEqE>YrVo24kDghC`>Q#Fk1MTfDLpQ79%&uS9GA=GrFAol-5aitw9ck^zvFh0*5%YmHhU<Kw2r4-t498Rt^2uovM;R@>Z$EGkG$RpUtVuCb_Q@BY2DH&9m?gUbxy-&0Oyz1MUBQL&Lgd(nu3P1FRi;8Gsbd$X`NO(@+JB5x~`@E5<af94y;9_aDHjs*f_9*%ggJ`RtLGfv|jzmm)5IIp2xX9^165N=UiS|C)c~Z=i^H2>ZVM)EXpIT!<&wmBVS&(Hy%_bUtZ@|I(u<>X<xu-)}QlB`v`jbf$U5B4yH}x*q8P%@_l*#Lc1Qz<>h^lfy=o*(!Po5T^840+Go*1PjY!_U&gZXG9Opk$FaQm5$9ES-$!?T#=g8y<o+xB(!P?>;}5RS?Wc5HOG+s3kBs)-OUJdIOXHP!%Mrd$XZn&a?^`J?zaU@U=hBjfu`lh5ee$J!H1n>}<eT1Bqwz->6-e_jt>`qakF+1B*NkUh+P_m??_j_5KFXu@yF+=*z6Z$Hw#CtPQE!%`=Zm?+VfLl{L1n>vK3{1+(X{*{mzVY*&EJ>ECSTgGG~cx)U*6wTlk1Z&?}wU~g>m_=kNLU`Sx>%YT{xGQ_f<EoBtQT8qMYx}{Wfzo=aKejm1n73UfRz!{gKA`rTt&y)I~n8QC0Z5EV85LpsCm$_N9GfBjW@6(!R6h7n^-_+!<Mv#|S&m?=`=dB46IWw)|b1%V$~mzW6hj@~gL-kgwgE&i&KFp8C1^vIYBhXY=*y$K$g(xGVYpwQs(E2>Tbx^Le>k<nh)ahJ4faj@<rUv%jL_kDtr+eCWdG>p6EE)o;lnF8?rt^R!(}^HNLLe$Kz@HkZFOEQ&tc<Z?ZYSgODNBlg)-UUU9zJIbT3FFl>kt4aC&^u2&|elA~Y5#Ktb(61R1W6C6|)y0;iqLfq|lwn~7e##(B@t3dv{8NUJe*deVGBj%3^#A))hDgx`#CaeDFN7`vF9at;*MNnlgOkBqq5HsF!PyAGXY%3=^gMJQ_&j(oG#$JboCaM3P6MYP1SdilffK<qp)<fU!NZ}E;Njp-c~Lnpob#d%)C*h(+!5Ld+z~ty8VMc=o(|Q))4>VQh2RA6YG^Vz8Ev{6A$S`!8@vs?A9@D7AAGjJH8_h9{5!Ow74z@l>Q=0-;OgMIdC?H+33UZ~f@|l66Vwsv3U&mSg;oTY1;54dMV;QFZs);o!Iz+W!I!|N5rVUzY2YmI7HA513wSL;@M35pcro}Z=uGfe;4uinL!raLL%{*iPT)@HLjefEzEEedFSvGI)Pg!eoxx7vO3=#SO5n1J7?4=YLo0*JgH>o9unKMm?FeoMj)0B?M}Vh6r-P?~7eEuh3&5+OtHDCIfmeaIL-&KXgTIEJ1%C~`2>l&=5&Rx1`tf^w7VLt)T^H;E_ASuYeW5MEzTg(n_TU!awg|z2dC?B4LED2hus^gV*dN>o+7R3b>;?4%dx7gfYlG{6)dKgViV$2aFC3tip-$k+;7U+Oa3!!kv@F;j{FlNi?p47;FM<C8zk;3yzXCr)2tE$Y0v`wOfo=is0jEOOf>Xik5Q3ASi@{0Yc<5K)c<==181MveFhX!3bSO9w+y)u|7U~Ob1NMW~2K#|MmCyIQCqi)Dyzqv)Lu-NE!7flIunV|4v=X>FxFWPHxFWcW@_FnigAgo!2U!AY4J`?_2HQf*gKfc8p(?m4xD~V=xD_}Y8UYRmPlZkcPX*71E&$I5uY|4w3*8Q03Elzy8oUF10D2L80DKwx9();G1mlYsM~WZ>yF-1!z8Eju5rXSO+k)$ZJ3<4&9l^l`#+P7(;0}4w3fdgn4%{5v461>ffg3>m!TuO`8XyFFL%qP>;9Af+;96j3s0wxlSA|vsR|S_ZFgBG(2)50OqR^612XIMn8E9p28E^$?C2$3BIjB9j9Jn-8j9I1eS#SyHE3gQ`3iKIRgy28(;#cTT&}U$w$H6~=k3jc;kAQbWQ^C8zo1p8!o51T4f|o**z)Qiipz+{Y;7QO4;7Q;f&|q*EXa{I8xC6K~G!Wbx+#K2l+#K8p>IZHFt`GGD*9ZGR>w<m24V2GgWdnrZrg_m4+8F8$ZVavmbqCi2yFp#RZeUkvb+9Yg5n2)K2zG#$0Xu-pK}&)2$JufS!FG!HsXS{jXbEsJuocu=`P2=Gi$iU}#laPzRlya&EugKyEx-ez;oyPbIOtSx9C#jdK6oB@1#~4?=nn7-a0c`MI0O6*^fLGxa4uAgxw-f(xVROoJJ=m#YjK3&#?X%7#^5f{U~m_32($w@1l-x`^Z45t+8W#$90Y9x4gz;Y2oA^#KWIH@8*n|a541Jd2kZfD1@-{DL7Ri!z%`-Gz%{`&pbfx6y}>oWRiL%NRls&oXRsaE23i$t11<(F4=x7&TVb^YixB)l`TRT(EcBhiEJE-L=u7Ym@Kfk7;HTh+(8u71;2Tg2_y+ho^e*^1_zLtk_zL(c^gj41_y>gGThJfDx4<`{KZAw-3KsekSm+V(P4HppZt!97PUt4^PVh$PdhkZ@287^c(52vI;5pD);5pza&`IDa;C|2^;QZ%GKWI0w(4OFa;Qr7r!2Q945rV^@eZgViA<#bHA>cvK-rzyt0nqN?0pMQHuHata5NKy`2sjAZ9vlR23vCG&+8EpxtU>F6HLyR_4eSqY26Y8D12=>^f*XQ8pblUUa7}1Auuwa2O>hn6^Yf_&LU6Ubr~<WtmIm8^i$aTmi-HxXmGb#da1m&6u+R$NB4B%H3$Q)733MR12{;rQ2Mz^)37rT25<C~W0z4PI93eOpngPxPAB27bJ_x=8%>~~9m%{T*JgZ9KnbjCv3fvUh1>6+e4H^RO2JQjv4DJE$2@L}G1owh=1@{8?MhNZ>4FGosce48YJnMuI+yo)m8X?#US`Tam{;06}fJF%YH`D_xLhv6@H?Ro7uc0-;A_V^itpOGx_&Kx+ScKqzLG8dI1V4e=fJF#?1T6*@A^3s9A^09tJm>Bq1Yd)G0AB-NfW81<0H1(91q*!$J^?-ky#YQ37JD4uLcfFF01Lei{tkQ!dIfw6d=h#Ud=mUU^at?w;ByGUInZ0+9Iyes2^M-7Y=93zcY+UrcOe9ChHeCJ2AiQ9z(SXS&EO@_Ip8JW*$Bb0&?(?p@I+`ou+aYCiQrMt!QfHg5eUJfp<&?B;Bn9);Bnxw&_Up_;PKD_;K|S!=m2mGI2zgu91V_whJb|zfuq2~pl!j!z$T~$4hga<;!yN|`me&D|8#mV6#S3F@;3`_%N6|Qg}hv!Ht9lwiiu}P-ov8^owSE|f-3(3b{SR2'

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
