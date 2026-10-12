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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7ce14aa504e4bbfa7122c444150999f/part_000.stl', 'relative_path': 'b7ce14aa504e4bbfa7122c444150999f/part_000.stl', 'source_sha256': 'c631cd90d6e0826193bf5d49bda3ea2384af9b10f00194ffeb3808134b557ae6', 'input_faces': 674, 'input_vertices': 548, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11391936987638474, -0.2146051824092865, -0.4754112958908081], [0.07804112136363983, -0.07801200449466705, 0.2414674460887909]]}
GEOMETRY_BASE85 = 'c$}r22b2|6wuY;lAV|(humKg3;5bCX$YlVLj36L_(4c^*NK|Oz1<42qs2~V50xB{pIf%e*3<ym!jE*`g>gbpiQ5nO?JE!W~McrM;wcdJ<wf6e|^PPQmojO%@>)x{3t{n;#Ebj&XYI-N?e}4F6BhRx@+$-<hJ80CHp|=hi-SF-aIT>DQpWA<;OFH-H)U|hpcds|0&TWH6-#V(!Ratee8Qi>1{j55JhmRUFYQWw7hmX2#kmc76xNGzv!$;pfV8kHPzO+f>=Jm50)vcd3DeM3E?|eIzSL^QGZ!|mcL&|Eh?UF++Tzp@(W0vO*tL5|Do@afYDAxF}lTUlz&-eBmdfu-ydTd^_evDK9WX}UW&)t;Fi`I{E>gRs+(Qbcy*D3p>^)(OYsq<yObiUNjpXPHfvt`=)Xdc$r`BGo!Q$K4%-7P+E&}N_2RIS=hp8WKMG@e*rV6Q7*xa6l!Rt<Qs^Y%vPqq)o{*|3t&bF2U3<!HX<I^V0A+Uv>}9<JxgpEsxN*N@{<E}p2dJuN@nFO@G`@{?D7@AK?ietpsE$zn58E}mRmJ<r8crzanB=8vy<ILc+ebp3E0RDI#PewZ)ypM1mTsbOXJM$b3R<$O#2bRuotvJdS}Ir+Am@}gYUP3MQ4d~f2ufbT7_FM516m*bmSG{)!2nicj%=dZcUKjCF=cAamUOMT(`eA7I<zFK{=$>)75`8?~<N_j4x?A{`%Q~!lcuJcE8Ilh|9@r~tke1+@tM{`|YpFgpD>U$M;ZE{^-n#=VfTwh<BOMYV5dY>mJ@80FtYh5nS#Zx)YrsaE+Iyv)&OTIVkp`gyJQ_ltYb@N<2)n>JmXLoG&f{Q0QKkejRkKQl2c(UiKPM*4D#X)C&|1z&Q>koeEkaIq_|K+eV|L#5cPCla15$AlyUhG`AM9#{9-_;}F53~%f>(*`aoV?9cCr@?k@q&|gTIl479yu?$c(UhaCr|X-ebCAKpLTL@$R~%K{PqhEJLh@#yZO%i;T4WJw>z$tbKMd-lhXO*HM^YaDO|57Jhq;~^?Jf%>j{sor{wGP6t3439$Qc0dOc;HdOamyucvHRucvU<Gj&HH_~xMg*el#TXG0oKOd8<K4>|eCHx57RI{#yw<E6PAuNdceX)ec0b2(nIe2!O)bG$T{;}zo^uh={}Ua@?RS8Tf+uNdceg<PHgF|OBBo&Pbe*HfMUn#a~to&Pbe*HfMUF|OBBo&T|Xy`Jj)k8xSg-+KF8e?QS&zMmvtYai56_eag;{;0X!A2pZzW2`>+N6qE_7~3xQ$5=l1$5?&tkFoi1e~jgGe~fYNkFoi1e~i`V{+N5L+cUv&N&h~hxqLqnuD{P{9)6$Mx@4oj?(+TcgBMdSo;|p4UX+L5_f)=c$xkh7vcXkfbDgj2YcBb@iz@g$HRqUL$NPF*%Ec28_D;*sKAoB8$`>yA$-7oR;pY{8_khn^UY~ODRP|&U&uyI_<QE<2<T~Hmw$zy~JXZhvS<d+gm;6NGYn}7gT<7cgYaXkw=C66IzM8-0lApEtoyT3*i{|0?$!Bj4xc<JRxqM#|uD=gxPJZ^O<^j*|kcyr^n#=j)Jy6Bx`twtB`TWe@IDWlr{xL4|5w7MR<MMgF;g@x;_0&9E&nc_cI_Iyr%s;Dop~w8=sD3YN9{&D?>)*?ohri#?<m9^6UvpXiRJDSuUGvdAtPj`o(L8*9`0=P!{yH`sm+$xIe)!&g2hTdaCXFXX{20uq_OSO|+&j`fjfbCO8{RtF!oibWccslI{2WvH!gaoP!JuHjT3+_%eg{u}z5DNJ^LcUTc2~Y|$xmK$`HJW~<#=fxe%`|M=d<RLpY{B^%YClyFPh8!Lb$%aXdd2=8a}@~m}idvd^FW%K)#D7XXFIGJAPj4^W=i3cKY*teV~&ki%bakm?6P-|GhS?zUE>5-hBdo*`)OPic9_6@=cbzu6NDlde7Rw@DV@nmZib>*!&*(E}qyiJ=kuUHa?Gi-fAwNx5D-3t>*Ik>#^O-(ynXHXU*k&7M@u4pRLjJQ*${#Q^Pj+JXL0$zs`y37yI82HBa7I@0BP|Z2W4Mizn|{y3<uhxL0UQz>D6q)U|FgF6$s%ty_$fpD0?>=cz3vpNk$x&E+@>_ljoibma?|{A8gS54+AQ&Ci`zr5|=)r;3NyDLi(aDlYliH^2IjzulVE_C&8E&ArTV!TJ1MuFt(28|{eZYcAJa_9u0MI_(;y*H>KXC$hhM&~MkTnO0wOsh>FSoq((Rtmff;c39pLpLd$deX83*7f(z(oyHR*AKm537cTk96E%W5t=Id{W4&^@`7WO9S@B4eCujb5rz>B$<mYBTzSwVPPY$-*u3x^B4_+VCnb*eWsjv2?<;S?rf8$zrzHst$`?Ou;&%4%}>GRQC=RZ>0oiCjH)b>_BPh>xpc0Fn?*OzepIjp(PPxhI<!<8>Q%&*t(0oQuQxXfR;TF)4l{IR<hx{hy*lka`DVWI2%*F1dAFy!q8&hu08@ce|w&QHZ9Kda$`^PSh1;^FlLk6mAiOMWV+;XJ>N`h3t_J|B{kKA!83pTT|P^6m%I_-7-XJbB>yV83=YOyl0t)&VcqBzW$+?r4y&KHoGCKR+kT4eD&1n6_QvdOq3x#s+oNeOz<7j|<oLan0pEp6FRBeSMl;<8N2<<i&TS^Pyvc``SO7q;r|St^?O~%olfOezIEiAb)Y4bpBoCfPd2<I4<vfG$(C6i?(#~)QyAEcsNg$FFed&@NQ5?-S0FH??=-I`dr^nHJ9@td(o2FuK8;&^AWD+uX#BC%0p(mj<4o&TtcpnZ^+g0)m+!n$5*&Mz9Cn~H+A~US+46vxV~Nzrxwq0UGE|PgM59x3)k2C$rq2z^w(E?Kh#|A7sB=TL(RkdOM3>K=S#_Xn~u47YRG44T%IrK{P1~H$rI^yc)k>?FVCY?zC2%w)tBc^%qO+*#B|sEHP`ui{+i2t!a8dHn(KT$f6Zk+xl0>O^V{lojpp+EMY#T5BV7Nk(OiDlc)h=!>epA_TQm>PlbM~9{&@9!R&)71n{`9efUDojnuoua7mT0cxApIF#if3-R(qf8-}{<}pOf{<1$ET#AkF1>P-0Kf$$p-CUZlA^FA}bw7ilifi^4kUd6DLFpB1j37iq5Z_46Xl!~3#qS3NJ%Jp4WWbmNKs`K+JUDIPwrgU6oNDIUI`b3wTYexCZ>9pmylTDbb%9pmyl{cPDWuKF>q^Y!m~%_aZ4vLjsQo95y3+kwrqUF)fN_&gJ?*HiN_e|6pnU-^EXTKqxE#pQc@>a!Np{OfhpWBzutzB+q+zk_>iE==R8m)9L|<qMbm#7}ojbInKda6Z5FoYBIyo{ERpZ^2%(TDZ;!&E<J}*|+Ap@?%_{k5zr^e%E|7507t`L-Va>|LLo|==x|LuFsxo%Y*Hz_oEaK-;aXF-j7l|%)hkPa@Tw`m-!^Gduc`VxP<?GS@H0A9on-pn5TLlLvwi_10H)HLvzVrmsr)palL3Be*VD2=UTm|rCdB&y>?!dhtIWCet6yeLB5_(?0Ov5C4D};kEeO~J|0}Zzo&Wl{%4bZ0ax$u#rVmM$D&-nzZc`=r#>%~>pDL*m-9`yK0h@N^S>_P^VsK);^F5HJofpcxa6O#KPcCAK5H)LbMCeKd>+2PD(`PA9=^ZbqsE%(I?Ma9G0yw3!u9*HnuqT{3s>*o#<<kKYjVKl{cV}Q;^BMpCuXd1ou8V^`6gVSpPEa4?tryxT-UGW;r_z)^{csDkHYo!tN9=0>-og4-^;e79mnu}SIxOzgvZ{G)tvmS``%AKUh>~t6%W5J{odxW=yv6Oe$C~5e&PE4f6c@9|LgbK<kwMuzo5CCKe2rIJk<HjKYP(upX<NB&|K=r@~I!om-A=m!&`k-e-9Gla=#e5+~@l5O=4WmlM7A<b@bn}XfE}WzXWyE-^;|ft=~26uY;Z#I-zytEYGu1)GO}|9uWD{APen3QTLw)4Q>3t`qQAM%^LrI|1{{u49|Pn#9{Ome7=c8CSF1h;<uXEY2sOQCH@)oQFJB#8FUM}1HT2o72S#7MBZj}CEn(2BhTt~{G*K7fo_Y`+s^py)Uf`16J<^O*9-J#FYv#i|3QDo|ArRL2((N_;BAzlUKwgy|2z3-(Vy`)rx<xwi{ow1@AO+O7O7X9`B^<nt$Y*5O}v2S;SZoGG!K6OJ&Yd1AI9gS$MG+c_Y#_iw>d}1vw9StV$3o0NTl9T#vi4I^;1o(HZcJ0j?YHBq22M>XcAq8PvWPdtMPY}HyrJbw>b;Qv$_!9jWMgx1(A9S8NZMk)=x39(nNps27EuXD|!RIA37O*6h9e11zm~1i@agz4S1V#KY3Q?<GV8EQS|;uz4?rvPYvrQnOI@s7PJe#FWMRHg71q?M3>_y;wPai@OO}RC)x#XbLNs~bsoMmW0s?HBlYGnejYWfpJ3t<6MfK5_?yv=Xea#5=y-G)ems5x`Uw7Z@`j?F@HS^Qc~<A(J2GY&Iy+Kt4&&!g!}=T(OHK4fJK%3Z+oK)uH=*Ouhw<a^Ip|XSVDg5b9q=}1CV5t8;oCFjVRUAs-Ymw?qK5TjO*~|x7upWr6TKd7hwq8ri#~|I7e5w#2!9)SgV1((n=_p}t26M|Gv+~bdZgYA#?PRJ_4k-qVxkAy7Jnmp9oiOuBRU3Mj30x)2VH_6NZzezTfEJgMxNFC@YgYBF*+?$?>@%gM-A&wn0vu76R)Dj@n4(x(!^Kj7x?4keTjY%@h51XAXogWw56{2<Ft=c!}^hCP9sdbl@aKh8Rz^c+E)LOan6sXZT0PpbABZ4k<_!kwef#7(FSdWUu$BGiO0}fd@J(Spt%v>ns#e)#kZj?b;Y-$-HIC4|I^IreG>&U11+2x_(JG;Xkom~e~&R%KZtlc<^%LR{J%_i#(#wVo)P#A<IlpZ{*M2|=*RS1J&VsW-4~f?j$VVeye7=*#SwocZL5F5uQTzui6_yg@Eg#L=u>!`zn)yHPvE~Y@r{Xc8G%;F2z+_8B3c1&^S@?{)o<}NOw=;b6uk=H480n?3UBi-B-d)~h;K%_8M)S9U?O3nDtaxxI(^m9s`wV@wP;nm&2LF=OKOR4LAwRH)_-Qd@0sKFDSAHs^NgVH-{`0KVwr)SkA8}``6V)gT&u++z8LLd)VKaJv+Z9@|E1_p_+O2l$q3jPxb=0tp#KbcKhbaN)T2f{#*42@yDsCbFJsRI6Q$9zc&lYI@mBHWjF!m^SQ)tQ8CQn9(vl~2GXpJ`dCr%SdW^HawwY5+6BnVi@YkET&O}?Z4c_L|rd=B*{vz5kUVJUuwWwu%9TOMZwL~w$w>I%t6Rpse_=_3S5^WXnm(rH;;xD0n3AL<$+wA*4OuUP}gMZD$>n7en{~qyg(|(&=>vx-4yG-mspTj?8Vxx(_p-)HrZrZ!awZ4Ek2AL*`qDAoUn7(&SoJ2p2csu4pv?%@xGp9e9XoUV5U(rM*6P3{_5q|~kE6BCJsy!!6R75Ytm&^?M{*w`CMSLZEb@W2K&8bEWt2HCO675Rl)?{p@NX?%!&TXqC<E)m7)Tl;YHMsSK%sv?LN}}iEOXBOJ<?)5+I}a^|FJPh=HHtANgT7Mqm!i-52DIy=CGi#5Rx$K^d<C=tS_)s;>_;sV<<T1W-!g)}AJFpn3iu1q8hD#ig&J0~BEACc3gl)nwnC)lj~VB-Ww%`g{cpy(8db=%YPt0Vz2IMQv<SX9z9D)Ez94;t(Gqx5(kn`hqKxtAD?xt=`mDd4c0;r{z7E?eiWb4wK`%#3;1`*FC}LtES{Pr*?wg4P==_L3kG9nZBEAT1tBdf3sU<ZR;Fp+KY+@oh0YBbE4*fawS>M=1Bl;WBXMIT%CFn0fpY^|*efz}=`mL5Ax3q~;^p~Q~`sT(rqrVwBrJ0kRTXVD-z99Qk7+-`nC<rUUzRqWV7vdKY^I4xIY@;drvjpFmc2nlv82>B#)Rg(zc2nk58a|PBQ|4^funC%j&ta{ape67nSd%7bDR?RNy$L!2KgPrm6Ql7%Y2N|69Y2P4wuyo8f%IA5jlLW318EO{^~ZOkJ%nxbM+e~Vr9B3JH|^oDJMj0?w%h3g??a#U9qH?a??d}$*Z_P-+C$ma0QBaFx7)fCy$62}?Yq$7_?yr^=y1H<P6vDk^7^oyUi9~(uOr*Nlm0vDvwoO~u_i{K<M88Xk3vV{ZQNp_AATh5&S)omKia)b^o94OuM^wo&Gtvo*PCOR&9Uo`AA;VFAA%pvc1AFlzO*~jmi_39w|yH-^fd7VS^#hL-(KLKz<*-ml<}{d_!d2ix0;9l7Qf%bdJ{LASc_)ht$yqUel7k(6JMD4%*307^)I7;!@rDw#zYV1{Uo{p|EU+uIg`2D{mF#?i@txcPu6c>Kc7S&$M;}dPqYC3eKY2tCO$yl!>=)Yt4-vhtMKoUXPMPi8Rz`_w5{f5obw;hmb%uz#=3upp2DYC^CRd{yyg2~`#2_fjQf_cR=>f&#<<tfqxkL|zjf$({6}7J>^zR4J+2=7Bz-42w$`ubc&|er!*^%gjc5k`AjkVz^cnn@oGWjkZ{jWg9QHZq%@>UO8)L0LjX%h^m(e%zGt9PUnwW%6#!oSkG%*XEjh|{_nu+_+>G(M&=F&fxzNz%toO$T|_<8s_#Qlt$i<j+Lok7fIj<d;`iB88)Xa2H3li80c_#`oz`Auew^}Eel>@u+jeGb3b#3nE3-$bAFTTN`Ce+zw^8S@<d&(UZ7UK7uo*pKeRZ#S`x{%!Q_rO)Q<M0enK;<pn!7`F|-1>F?!`)KcD{+pQFF1ELeKI<<uYmsH51)9LWV)_o5IDx*3Z)~E8i3iX{_~*@-y(SKzFW}!W@plv7qo?t=nYh5jt!Op;t@w6mCA`h4466*czJ`gxCaR-@@PlY~LA&Cs;%lIT@m*+FL95~i(N`U<g0ITBDrj|lCFa)-ZI5ryzKOq$c4hXhJ$f7dv{}=KjV{H1Puqs|%h8|kHs=g^XW-U9Wct1{dJ6v_ZL7Au41EOuqZjy7=tB|zgBRpHLf#M5Sw_ue<XHbB+x!9j4u6LE{)AtV5wvZrVE<OI-`3ll)8tuQO8>Pc{$k=9^lJQ7Ca$FaO8Tt-lZngeznnhn>zk-Ye?9uFzsy8k`s>nXeM1us=x;!u^?x>T1^rjh*N{0~P5;&OS>LroMrQc}fAqf`J@?OketBvC15!OQ{dI)s$QtHi4PQ>^+M$sBO=*5aX8I4{N811L;r$PZ@vU+'

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
