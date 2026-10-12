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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ed24b6e27921449f935509d9f3da043f/part_012.stl', 'relative_path': 'ed24b6e27921449f935509d9f3da043f/part_012.stl', 'source_sha256': '16e1e39fdd6151241da4447ab628386a9c5b1a440d946f8e316a5aec4bd5d6e9', 'input_faces': 476, 'input_vertices': 306, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.27748939394950867, -0.1640390157699585, -0.11815089732408524], [0.09087467938661575, 0.4668733775615692, 0.09574354439973831]]}
GEOMETRY_BASE85 = 'c$}qM2UHZ<wk^N_3WgB{b78^^iV0&oiU=a&m@t<C3}XO93^-1kvohw0rD6cg5i!u_IHqyTp&SGAd^%=~Z+!QjvwLh>|5|_j&sux!UAs=*dv2^-?J}&DQx129|GbpgB{zTcEvYCHu8O-77ZDRXpijiG>O-PNIVc6lmw#5C7uun9SZ4<%PKo#K8!@a;jCXz2yJ2KK@2aYI<j|Pdm|jDA4vpy>A^jG;1`Uf4{;>YNq9Vj~ML*v<RaL)ARn?!=|KndCk%H0t@Wl+7OIYTxCX!oj)+C$W&p1!Mb9*y!N#jT9t6hTFFR(DyHr_I+3H$o7cEl%p4$ZLjmHwVGPCqzwJjJItoh85d@Y%$9Qlsd8>D_1OI;!O)DnEyNxMVGS8v91saN^>pC@;O>WcHO`11Z1WF*7JWB9i?l6IM_;;g0p?wK2Xb`!#=0BEP_{F676%vp=ZTYU!J!-i^%WkJ&@MQgGQ2V()vW$-gkQuVhn`7Yj0MePdf+ireeFOtR4_i2XY|*HHOYe3xg~`l~yvqr4wYUrhY6D*J1r(}{Bzr*^4JmY$N==GX;0i1WOfC|R2~f_!DtuASuTx7U&Hu;C>6&GhY*=du_x<#Tm3`R2cS93(E&OQ*c{_v83_E*bQ^Dd`s)7q1BR=Um(-SzU8-3B?x+=W@bgEp)%VS*Pa|UygsaFO}L^s^cn}4+GrTADg(Au0IDR)Abf-_A9R4O#QaTcQDnn=*S83yTy$sc6>RC%Db+!|M1!_$|E{!7Ws`6+1EbOd^N95q<F3D4ECRVNF~2So5|!qoy5ND@)W8!>r!$ye^Os6U+ED=?Jx(nV1Is53zZWSJc;^sy%YQUEwi}4hb2+_(*Hcp{dRpP#n)It^WFIA3j6w?w)A}UY1AJ^;6?T))lH{$XavuteCi!xKgh!USU-9*J?C<W{e!0uQv6OYy087RkNpOpj}m(Y()=`)N+RE)O(9>snoRRio3M&})1OJ?TS`o)@m0ICuPhG!neO-hu!WvGJDdH@gZEIoQeLF+x|+uR#Rb$}lk?o{zUl2=iqCw`^J3v-u6JKUnm<Oxfvag<2Mj^KP1sHO1YTZG{olA3`R2L9Y2KQ4-AkbSFLh-9=*|Pw{@@Ur&!!(*a5?Gev@VR-Uejp)FY`ZcyY7rdI?wBT-t5nI;rPU^w0<p<UmT<IegAWm=EJ)dG|pP5XXGnU-D#buC(hHlG#$Rq@qL!=;Qqc%^UCCXmE%v3;PI_}a}mXbu44a>T<oU~*g*MY#dA5!#~-13-!z*;{Zk`^<6FKTN9ERTJ&~TP5XgS|^X=5G=x(&`^{GDW2QEEA?aC8E<8EqPj(v6YAR3n~i+(15jTiZ*Q%^Yl-U`~6)Six<&ri2#o|uZiSWNeuJ>z+{rU#ExEqCr$x5w;{ZBFw>>)di7`7xR7ukz#df8ppxdd@F~{o~OzUoGBzUyW-+zWMR%bCl<TAX;B)o&fgS-=O}nR6@LeBli2Rrg)`x7VRh6>rY2`KA+(C+Wbab|D{{(w~S7v@^1~9K+lDzu^&<S6#4&JJUzqK@7a@l%e~jMeofOo+5fBB3c4=SgT`0!SJ;1%l*;vmZKLuUpE*p|Yje_iQI<a$P5oRpjs0~a=2JV0PFzauYPE*_#5@bB-z^#Z9xI&4esT)0yYq*qlb<|~{m54or}@;}N_q8d$9{9Sxy(zbUdy@S?9a?i>(p}LJ@te3lN0=k<SXNv4<$d(lSAB}VX?$pyVHKAl)A|N95c;B?RYBHt5;5Dzw@0nl>hWDOR1haUD>~PgW@e4+w(dKtHJ)emK3jfG~Yt=XX0yq-%P$m{b_Q&N&B}s#{&!IRT}lfrjJywdO4Z>+$Z))UoYG%n{Td}c$nf{OHjY*DPuT(!U5XfjLS`S@cfBn|IBAvS6bJ~+~1EvxSZ7Bi<C$0EN)+?GVIs6aDnGjUOI=EYddl|O+M1TV-5(}O6A;}kip~Fh32!lQyjmy!^@FxF4pZd_0Qxi+V@OPin5;+L-X9?b9z2K7k!!E>oxbDr+Vuw-$eNyN@2fhL#o%ZzUvNZU)A~KE3S{%((}9dTw%P*!+zRpI{#R5@q61eu`BJfN^twrJl~ek`$&&`xS#xa@2KA_MNZTF)j!-|zvea?U!{cl3zffXDf^Gl@Oqf{k@h_!D1rS?-TD2p?i0V4=a$$<{{5>b$q#5v=TLq42|g#e=c9Pjn*@qCB4@IH*n#V{^UaG+(E2q^a+^o_mKn_Po(9M7Kbw$Y>o4=6c-@!#+47_x`(=Z;-kZ1QQGDwOX;glRjx?{7_?L7Zvn=jTzSf}kb?Wzm?RovWG~@V)|NKhjlpjg^rLv+P`(^u3Ic7D9`c3t9V?WxF_ocAcGpO9?4SUER_=fsNsprM-)5S65n@XxQKUGgN%}?FZeGm6r8yZLD;!PSybAei1&Y(OruQazMv`)1IKl1g?KT!VaB8|t_;XS>l&66haJTJFvAhmDg68M>vkLi!^>3pJ|YD~Tw_x2|Hfzv3zz{|U+9oxE6`C33r+CR1MmE<ewS9m^Oz0c>6CMoou);$|hyrKs3`OrZpUl|p`?Mi-5?b6nk<9MGJ*T}!SllsBjqZs+xROcJy2epskb{?a3uSXo=^6QPD{<J8=$yaX<;c`x_j-t3(@w8smmu1K|cOFjh#%x~aYGySm-#mO>9OZX$EBX4a=Uo2hg?xUS)RyB9^x*RIw;r6$pE!@=P2ojo-I&_6Am7LuLGh;kXLw%;e!=_h%KaSg`i%BZ-6@m(W{t@={~gbH^uI^G(QGE=ss53|`*F2#9A9fE_s{UjRIfO{vcI$_=UI0(o&S|eRk@t|;aq;&4LV0@uIKn15I>FLRS!N_m|JcpUq64~D$ScZQ+R)le?a4=UaL*@S{^vixlV7IgZG;;Be-4p1|yH-bdE4)+~$6s;zQ?mwR8>k&&2V#D6w=7QOf5cU+-n1dX-W+sa&gXBz(v7^LTzfzu%3g_l-UvoXcOnjoWqBo6foV$^4v8PYd;%-mxF;H@ZszulE%?^_yi>DL&sF{J`bhugvessV8ZlP+K}sz3T5(cwd~of_$URkGJUg7t6RDS3iyqenR=1e*KBpxnBl<PwZSx?bWN5<@KEUGx=KaI^55dLV1102eIFBD3!0hUPkXDWmy$|kD2b>rt53>>HAE*ZScNwHIvI%lW2Xan^M@n)SSxK_O|Esc0Diqjw5bxe?6f0jxtcC`L2JuLiHNsa+0r2ze@AS_+cW?!_NPv{!xo<SxNC-Z*iUzbMijDc`^CghY;@ns&{GJwZx(;ZP$y%C4kD;$3IV`a#ol*&!g#7j_K#(<Qr|{cs>4@!SDA)L+L!H?M>!+lE~v|6u&{=@#?V+6t8~_;BoJeNar<e({Y|}`G-<ImZ0IZU#iVN@c4!$@%+5qgZ;gAdA&G3r#vnGS@b^9cmGZOU_!k9(2xDq&A46t2XcS@c9-7|=M<hNKO}Mfdv=qr_b5#D8t|2I-}CoqS|={YW65sv-AdDbtWJpF@jd6y`4@RTh1wPS`3l9Y4d!|svgrF<HP-MxaAEIGTi^I=AD82NEL*(pp2hq8%4@r``I&A!?p@FE_xI*k(Nu3CSE^TE&+kR6Z!D-ozIh;jFIs)|`@`fLS%dc4`dW_hJnpG(+5PJGd0k{K&R$LfcivZz&Dm+2kJ0!P`NoLGyR+pPRe|S2u8L{4z8dQD?RNEUNWO9ELH6=7|CQ16_SpKm(Ua%Ty7Ae{*Gm1x{=j{Fell&T-{f240{^RVf&bOGSbe*3G5d%1Yx0fxVDb3CzZcrgAN6&!kxjla-^`gI<C=VHewJQI{#Wz4c_4l7+RuOUlQZ<Yq5XO>`K_2t<=Cw+CGTnW?bf4Za|oTUb?kd;*(Q8$?l7Ic^X=EQ=H)h*;<kU}_gb(A?VrZ|VRWuEmiY7h=`@Oe-@0~+eEWUF(yk|+EA96gbA!AKs2sa}Ng39i{X@S|`IhA>fA=>w$hY6$^e!&+-m~8iO@Hurxpw(G9<S|>D1S?6Px5sog!)1IbcoiAdEiuzx8HBCByzmn{%pFKxVVY(^?t4;_|or8_WQp+G&j9h?cWz#k$~mo+r3}3xNYp?ePqP)c~P(3jDG*Me}9=fAEI-F{rk>5?JfJ`>t=gDY6a`AB0qE$kNdb%^ggvbPFcm{&F^2c*C_I}L51mi$^Lz9jx>?~)%$(aeEL1+tMkB?mE;?(?{U2$F6*g3SE%&eV06gK{rNO{16|j;OTPViLrYmn-*xuq6YYEq{Z6Ak8PEGnzG9o`{()EI+n;lk{1vHwW8o#9=LZX<*!pVWD?G2p`I4_XjpcZ|bCl{ojePram+@%>$J?FL%vVZK`?Ou-d3;NAoIbKKx7+T#XP!Nm<5OGnK5#3I&%GU{(C<6;=SK6YN9@P8=5;jS7U$o&8?)W{)6{x9`PTEQdX0Zi&>jcS@5}b*Th;dh`S#~wwN%@URF2*G+3Y`>eY^9vWo-iaM&07%>!U0@FW(;Jc%0`g^}F$TzS@P2yngC%yJ|%(=Xq71#@YUyuMX=%zWw)tx+a1Bnj?81d$*3u|FamM2kpL7{_*X;Q;eW<<m>f<Xg(-~E781E&DYtt`wlW3`1c+?^cnkO2lBlCID~v{h8OQwug$uxZ~vWT8B>?mxBYjSzP9aFo)0;Be(H^A-dmpeQodh(-}y$8ub)lge2TkKy-LtH_U*nC_10H-{n>q2YV!?_xBCv&Hh$!IeE%vXf=5vvMOyK`{_GTw@53v+?^KWEeckT+R~fpD$J6@Wyz_$3d0G7Xni_L~{asrU>A6_`z1TY6)RT+mP(Rg4*kPN`Ki}iGGRRkZg>t<oAIDSwrF~%E?z>)Xfpvdq9QVWBGxQ#{Oesq5fBWA<)P!bxc%FuFo|(sIWrSt>*VcERDg<08B2F{{E{eMn*~{jiTBRxfto-eNY8_DPfAvqTwd(%A|EYDp$YGJdXh7<P;8oCT1oj9d3G5cwA&`jsiHI2uo(oQdP6Dq1CqgHp9BbK<cY$|6?*U&1?|{AxeFc#EDsrBWyym0sRe&}3-x0e9yc>EqVx-<Cuu~vSj+4NCfec*l6F7kDbb*5c>jbvox%C360viRk3v7i>$Mr$PtV5jSwKmUhv8j6}>e~l>9{HR{PUqq82XC>-bwBFd4?i8e)+U#9<d+WLn(J2NxE20-U@h{!fI1G?^hFx@Aaok^Ho)3X>!7WDl!{zZ;Y*z*@J`?a_!P9{4bUf`Q^50}Q=pdtQqKlYhn@{R3y^v$AoUDD>Y3nq&@-VIfHy!dfKCRVf=-4$4M_bK{0{mpbRh>tDeJ)O0hYc8I15@rYB#|J9GG*0rJobmQoqD=C!k+Kp9G}d3{HXG46TEgLF>?q!Ly+kL;nJv1^o;3N<iwRfYeLCQ=ykYF9*+nUJafDo&h}vIsrTrIstkGcmebZ=uO~c=uOaPz^9>4V{Fa<QojPrv3Z4Ssq;8|8NWP$)WyN&po>G75^w;!g3Ccmt_bZ4onOFHAeVp_I3ILA-1h=kg!Y0i4=x8?4mp(vdq9_mE)8~rw$8KCU{7dI)FJhML_fF-{?36}UVjp(VB=L2sNuk#WFLVl(A97)xg@mY5;k!@D9Z=_cc@3Q6Rt}@J3%{wOF}zBe?opGky}aB?QWB+HTMdr-<r47E&}((^NQfy0^R~;z?GrPKo<k6(2^DC2SVmW8B+fn*OLFVxtG_bY;T(~ROF(<cLC>xmMqJ0!L`&f?_zk~ny0lL3fh$$*HX*8jtD#wI4a;Q{7k_)1ph6#sNf<3PlZ0N@IC4I!Y=|{5L_5qat>%&_Gg95lV!-VjsZ_?>X-a4@KfkV;LqTvHf4Rb$)%`GosylwMWH2sM*BXa9B15nigp#m^VW7*`ydDU<ZmF;roSGcO^@J9{aE0cz(avM3cpit3fzTvTfl&KOW=jT2R!p$;I+UTfxn=iLmP<yfVel%A8np{kNEfSt<OHk^UvX1>o;t2lzbjJ-bFj^!g~z9W7EFJ$o(<=7hnV0KwU3@kI44|`rsz`A@oh?Ti|EV&+weJ?QfuO+4R$2(6SHC3Y-(T0Z4rjklF%13w=%Cy1*ZR)RzPf3+xp*1il1)2>Ms>b!fTA%KcLAo0G)#c!9|R)x~usfvN&e#PvOa-vp)!#0yLj7%4DBpp$^FKn;OfV1I$;0`jw>uz-g^6@kjQE{uE9t0eHfKvS?RtEND>KnH<PfwtflKrp=W0%ZkCz-xi)Qt%oHn832EK?3asI?FZ+loKckNF8Q#&r2XmAXXp_7z!^6aa{%4;W>G)zCZ&3AAyeO8>`ntpcmreY@Ta}`m2MzP_`G!j{?g)hJky5yFxbr`+&PbcSSiq$U|}kuotu!>a7572VEcB5!?>C9rCxfPx44`9P~)&Sd2@1^!+g8*8_-#7mWMXah4no9t17<M`+2dlrM869OE1g-#X@!OMzQKOD?T^nIn?RgG)n8R+TUFt2}Zn4?h@Cl`r$DJ;ty-{OW+z<-nz(%Rz^MTS2!%+rj{;hXPVZfd?sH=HVdJZ=E03{vU?^l^6oAx4=MwZa^D&ZE*bq&<vg&ivWe!l?VD%_L)EYP<YMoTqDHEYq^#^6<*Jh3qkur*8mEkJjunN{h<SZV#=4bUkqbX7P<tu5VQx_9b5>y5b|(GjN~F<Pvy&gB)JmU6WSB)k=jo{{?^hI*G=(UQ}|T?sVf6g7Y6$&U-m#h<RZC_P2Y7v|4Z%;Eja?Z4RmiH0^>Rmx*NDVba#|x9rrFa<0ZKRxC?X#=unJ><mTWm&|Q#gbFc@r2inpc<14uqxDK>0xF)y`bRG0XO>k4_n#z~=!%qTZ1tu!|E*dN_0GI-=pFn?sAl#SnqXYsGHyF=L-}+9IYzB{ojt370kA)6F*?~YGn;iNek15bU15!^A7zgeP?gQNiW%Wf&U$mh=bPzZYIudP?>su3OsPKN=3A#QYbpvoqX!(rXe|v%(Ku3ck!404r;8|;(k?4m&aBFZRbR^<igBwBzf<wR!p&OzN)_x7K8AHj#p@*Yy#zBw3n8-O110DfA0x>b*e$f3;ehgTH9t$1=)}S@?=@{@3=&|5Yz!>!37{o}OS0I-ne|Tl>hU<J_XJ}VkyCPQV{CGzG|C0h>c|RwfaYmdhGdDOVbQyt)0(Aw73U~_?2fl+>5L$Zmz*TLoYuj8~pO;=^lr8J12EQ@1qr!hVkcZ620qhLzjQb8?1v)p_39LXXDAx%wPH49i{9NE1&^c`SCajf%qr21p^k0v@{F$jj+y97U|77-`(QTg`BFg&bNA<8)IdgHsjx+&A$=yx)FC$ICng'

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
