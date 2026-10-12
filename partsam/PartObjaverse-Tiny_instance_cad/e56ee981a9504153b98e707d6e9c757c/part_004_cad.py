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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_004.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_004.stl', 'source_sha256': '7d80e54efe09b3d6347f8b7536665ae6d6750717126c0b194f0600575ef944fb', 'input_faces': 348, 'input_vertices': 346, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.49791428446769714, 0.02330206334590912, -0.018214166164398193], [-0.4469854533672333, 0.19559712707996368, 0.1550533026456833]]}
GEOMETRY_BASE85 = 'c$}qM30M|Y+n!fk0yk6?m(LtR#RYM}1(I|u6bu*4y-)K+0Wm8L6!&}$@v}5{6SZ_iR1%XEMF^BZa4oaU)LdUb%}le*%B8;YKg&ID^9=ph^<V$Tbv@qqxz97tIdkTmGv~~Cjg9fD?5D`T0408B!l=8dqHwFB_$jFg$x|kbOGpWMZSo9<;wyCiXX45ML;J^$bSSCHtf2UWlyS*HPpd%@iD5y(YEa^&<SEH<uZ@|M9G}4TK5?(4BrrWCDQ<ECOScN`+%;GYZ5^!6QU9NRKCBAvFE3pw;dMFb)_XEA?kDZ;Y1P;JZsKXZEMuotcYU8Lbl1{(dx<`#eI`$<u4&mM&ZDWDd0LBlqk!o3duNIGcizt=aUQqXD$*eXi-`Z3@NL5Xdel1N|5WY=LLcScPxS06IpV&`$1WrK%fEfd)5=f22GMht<%;xY9p+kfZBFVg;eW%cl;~+AMSE!v=k~Gc#<AOZqFmp(9}#_P^*y3}+NpUY&a6<OyX%#a_(sh&QqQ}cL-h533f(nhHEDliQcIC`&dNwGvFbCc<O_YNYa1!|(=4GY5gYdrU287V&a^%UN&K*S;`u4<J7*F9pg^I!Cda$1<!UdT7rOdE%|a6An+_if|4z$Dd@X&U(2d9eq(5jzchL`w>v|fwuT|ruezTaw*S5Bh{a|HP8Ygv-&|N|6Xt}#89}xHDyO!2-$OxfpD;%`kv%5<~oVp2{t^RKBP|=?>XCjHO{~00sS>vsw|2t>x5xOh-#B6JPXSaLO|NCBBt^TUJm*^kHt;hK!e!?!HE0=yD{YUSAM5LV)MsFweZ170xBaZJO`lVn|Z!Mx{lC?hS@g73geY9Ls|NK~?8v(t@yrF;Hs7yTfwS8%QMlBM$a<ayF5@+(*auH`mA{mdma#ZO0ynFLWJA|ek66x7F2S}V#=Y{SXHg_fQZ<Tsj#P8gxnCKUZgs#>qf1k9&&@M-W-fb%B5AG+&3*C7pjr4zK*~dcHlIPRsl6g+(dha=;{q-r8jtc$r6fzIEC)5zS(S5j>H}s2NN&ickB980Wxk9V%M11$Vr#BP-$Pf|78C;%E{F}uJUCC{_-KwiU&JwzozbKFRUr!ghJ32<rWBxgEyd>Tc<J7HI*=5y@J+<Y0-P~_C@vpN&=*|_bNgU(!w?cQFEFk`d-zNE-o~uU7jrvXK&Ux=r|IM?-xK@75q49s(Am;(+0Z~tN*m(IKiMX{^=nMDd61|C!c&|7e(RoDw{lR+CK7ag>P4uj&_e6WeWakt8)j{HYsubQVwCb+AbHsB}#{61L{8N{Ud08EiUqbx-r|b~v3pGovy78c@d>@t7I7sxh{$f09x4s~{<~2&p=f=pPWyC+)kn?T5)l^Rp7UN27xSZ(jUL9nAxVLkYRd)tQ%Kp}HIk{hVc9HDoC)$&CQ%6)eCh9--?oO+&5B3(iKH;W#zRrY^vVGd6ZxHnybtRYRO;=03Nryb5FY74UUwi$v53IUtRGfS+@5bj7Jt;`MC-ffAY$kf+NkVsq&L|}DPfgq+{Jmc+CjN^C%JSMgI6(B2dt$v|4BcQ@bz{&5Iez*rEw$=eV47Sf%!@uq^aA;wc0M>n_0ZGueVXT0Ms(dz&X4;Z6Mtt(s;tMg(F;l}y82F*(A7%C#9y!OCHs?C%{f+o{X&R*&#mf8{gbE3dA@w@aI3$&&qkrU6Q_~;)&D$JE}vJ}bgQnOy(9Hh7il+V!96+8H%(eX;;iu%^SNt!E@^*v_IGmrU!J{|#9!)=^Rv^3JV*WXcA+c3uFfRomKIBWWdP|9PRzGzhmvffhlk1e{LvGnzqud1E_7G(R-`|>f1N7l=lP$@`K^Cj`5Y(s%kl!J?I8LpP3p?j53RbfW`ulCJYJAP^lp0#<v4mk{Iy@s3td~#J%`5cCg=HUIn+O6pwP8z`>FqssX|wcB3e(aRIa<;8B6uu7lm$|9!={R<SYB_!$?~0jOT@J{QK~B;-9uc&R6z!`07&`=ezsFUyD)1Jgd~YOzX41iPWc`67_MGRFiS~j1%Kg_geIkRrie3s3-D>|B9+&9j?a2>>&Pa5{0f5joeH8>&MCd;ck{q{3kyYy7pewKB7MuAl8x27_TiPPHP{zUJ2Y#K>R1_@;N?(`OWlCOA+s1<(1xr#D9GsF&>NtV|NifuaS6O+WbE<Nt{o<7rN6N7p8xmxuQL_rjc1z-QBF27|+Jy9;BYmamVF)IPlR{qWd-w^M&^8NBLG=U$|WAH%@OS@dwF$l(Bf-9^&s^Mb1|zrsZ07^`W2CL%N7@r$<-&+i~a7ZR5_=?c>hlZyR48-8POqx^298blZ6GlxrI=9)H_-@%Y=ui$}MO7f&49c=71=@v<S}GS`*47uSgU@<;zM^~m2d#C^HTsDE#%tIu8DL-eR)>;5**ljp>GOkL--gXqnq?v6W1<LvDw)@kk`zh@CWU+S*;eF})asq#jVKL7F-qGw87IqXCIZygou3ibY*MMR(JFZZ9xgEv@p7j$h{TjKA!Iz`k^**)t3(N}F2_0U@RQvKRvF<<D;RR$@ytg3i^N=_`%T|O_!^;W>XQli)ID8_>}Wg^jy;uc~&C;|FGqC02E_tWftR1X;|<~2P&ri|!6t(EiMp`VGrHu<<{N8|1u>Obg)Y~P_Hsg8L`>oDtYb?32jMAyFAD*NY+l%*wB{f5*vTYT;CLFr$-bp`Q1B6ZzXPj{AF$7oj@zh(7zZjrjXoZhedmbbWGo3?n4)nC0Wb;H)4>adw&{o`K#aVHWVx?+1?&RgYTU8G&R@3QJTbbUMR5AMB}#JWgpZLA>W=1W}<qWw)THpKeJm_+-t8@g*K?a%J2iE{mOj*cU>n$*=pbR6kxK9T!~3_7k&U9pX8XYw8CZ@#C_HoGMHzkR=8>h}GDsoVDp&@1d0Ox?a;Fm?NW!PK9wA?{y^KD&;TYu`thdaZL}Tq`%9T}I;A_ZOya-(Ntlu)ly_VSi!j_Wgya+xHiyUb#@N2eQK7F0tzNeFyXk`wr+8_8rhG>^n@|zV9$~`@REug?)$VZ{K&A^|9|e%=+8+9cCQ+zQZinzV9&O+xH!29Q(e*EZ4s8Fm?OB!_@8j4zoV?eTS*r_8t0-I<g<yzLR)#+jkO=Zu?H+(QV&JOx;!FE#I4M6Elgw?fZ$xKdyloZ|c<<8AP{zSMkJg)D_=Vv>rR&Cc5o=izklldyA>tzqfdF+xHezw|{T(_}jj>c>I6(RIc~F+_t>L>TmlFW9sgNqjLS6*jIj^ac;gS>K{K+&SPFmHqjq1knMZ)%qF6*l<Nv3tWAbhS3)<6dB)v5XA$xLB2ToBYst%oRX1w>EcQjN)Cr|lUAuWw^bgni4hM;U`gOUl!Fc!RN+Y>{%&kW5%a|})e&5TiM|9_%e)4<q#Y=KNNLnxJx&JOb&ocED4e5Cnbmc+`J<l@r0X^k7oHjR`#Q8Q|es7JLSwQ@2^rz=prv9Ll*w1L8F-1f#?@Q0KOug|w(f&%DT<?3z&8RQd&1zoqGNQ*-68EG1T+1MOW`_K}xn%NOt8Pr6Df+W^(@|>G&GRgM<*et4zx_PR^v|qK&$CP&=UH0A5*puoJw4Ad<FBbC+kMV*(*D}SHZonUkvz{b{ik}1{^MG(a2xSIl1<OEOdaQ0dU_=3Cl$`KO#i?jxh~Cb?y{C^o@ePFdKZ#7S3Ar7b=SotzImRdL<}SS!934W+s37l`@(sadZ&QIH_x-wMYU)goM-8+GibRu&vN>$ruD>mmg`*Uo21-}JH<R`c)z;Y>TjNBxyHtm_!Z8xpquAe?j`Tcw#GNlv()Q-w_5!xoM)Nwah|1Kxkvhsd*C5@o@MIx^DI-p(ni+%XvuhMeJY%1nf?U>=y{f@U+|afp7l|rKKe^<$#uov>PbXTcFJ}8s(3OU-IWf@bwym=bkc5J=E-&Yyln@F|LJo=S9&j9N&MSPk>^(7A;qNJONDaX{+}=3C;l&Xl<V{Euao}Z3`mgriAALU>qqkGd6rq9tTXbwDI%S=f2u;yvrK)W&tK<RvE<hhlZM5${M=VjxOppnN@ASlrxIM`e<uF@PbDUF{y+XyBJ98YsYE`jLm|H(;J?9N;%&$*A6N)JjoA!lU4dcXUJiL(Jz#)C@)5Wu0@xLtms5r12RbDBf$w7aZe~}2m%&Ff8>PtnQOM)`pUh_Q=Lvio{3X=4A8-%&F2vgjtmKfKUpo`mbL<Yjk69kGYrw1Eam>abe+=^W;o28*J;z?)mr-YjLt?Ilk3yQ`^WeqIK4$hU@Eh=P%*G;rEb=&?&McK#IItV|Rn)DrL*hr^+-EraI6ebzFgw8PJK#<51ZMHbk4GNoBT;rwU^sX+R>pOP^?@xMl8?qShym^d=RP;!$1%tuc{$?;ncW870w2#TQIYwH$SX$-Z-=~|V*~IbOh3%*2jKVM6PP6_GCv7<N6=<t&|Vz-gMWiIf5IWL0Q@tC$C=#&-UWY^*+fO=Pek5l=qtP*?FCkKNFIm00l>ZBr<i@t>^|@p@Yk75LjEM=okE}B{iO)#<B*)!t1jcc91@#?pJDoGX1@U+f=^|ZqR9Ld<efnqjK%$P90-1%**Ru^0{;Wf=Za~_pN2fnZ=x?%cSzh1{sW%TGY*Mi4#_Vuev#Q@pyH66k2^kwF99!tk3(C;0*k;6MfU3wU=4@lUo*SF?04WF;C#GHNB(r=eT_QScF6j1Yy!^jB_8*~aS-@d%+4}<0DJ_V%xntsry!4W-rsrOuIZ3i3jPJdFPZ%e{1yB)W|I|}KN)$P*Fl^91IXKw^8~cT3&0Za+bFxULt=<S@)L}oWcDNQC-9e<y`sqcSCGef4@J(SVc;6lwH&gH#y}psG0Nii$IIi`2%O)0BJQ8#U~u04hw%(J9s>UkeXET_Vk?K_<+!&pAg@Omo<F~)A&~oW&gU6^%@AN2IFHHuDUZw1ADqt}ynT-XdAlD)9g|Q$jzhuuc;s^eAB!A61;4}a7&Bjo#81Hae8tNc20RMhkL5kfYyhw~ILBD<c4+%xV0Z9f@NjUBt%2RZTZ4B2=hzY$3f>aDBRI#WfbGGb0&fdzVbM8%62^G|IL9Wye}FduZwSuOA6O6EAG{_wM?YY7a6fQwaE^6=)xhh3R{`f(3+M%23)}(Du{KZvuMJ)aR@tI+UKhrBRd9~=flq+f2loNz*a%nyyb-uBILD^I2H;J>8-sIHfz7~G@IY{m&4I1Jn}dgda|{A@01pE11nX?kId22wyel}zcEB+3cHq4Ku4MKuv*j?(m%=!I2gdng80Sl1oG*iMz5>SiDj4T$V4SaoalRhL`TH==H^MmAVVrM(asD2R^K~%JGhm#r2Cf9}z&cYXv*s|)Tf#yy|8VRE-U_@8tQ+Ri7-rA&wK<IQkuc7OGwXqQq!*0yJ}}PteACV$>!iXse+t+fybH5V%-X^@Zw(9r4@RtJFwUO@s^Gj{QK;K+@S(uL;L*6ZAu!H|!D4W)8nXyyePNtG2kZ&XV@4wGVDLdO&Ie*%jmF#>3;qId2zWT|zblOMj<7D4_Gpi`2m)^b<2(>`3rGEWf<FxlN9;)4+dvrS{b3sJwLRK85XN}`EEsLi`$%_(>?a}Monf4Z0egUlfj<M|ocEVLtiMJwiv~Um9u3|X_#Aj&@F*DPy_uymo6l?^Z~^$+%oZ{G7w|1`GcO(ZFYt8mZNLvK{4Jz8=2-Y5q&a?Q;cp|&afgL3M4IDv3txaV$7~Cqk2J@v7M_lDI_k*z9A<Nwr2*%GzsbzSY&P%>a5HZXa5nfH@J!$)3x5M?j+-sqg*3-33x5-7j$6QEV;q(Iy#BZUI`Y?_%fbJ({znq~mGm=;^~#U{<*$z_u`yNnyOF(6D~ZieIDfk+{{wj*)no'

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
