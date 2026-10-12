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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8d3d39516f7b40d5aa19e85226940899/part_007.stl', 'relative_path': '8d3d39516f7b40d5aa19e85226940899/part_007.stl', 'source_sha256': '9b1986f13fa873d43f3fa1685fefcd2b0f57d7338c335c6022e0a754a522f3d7', 'input_faces': 508, 'input_vertices': 298, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[4.326755523681641, -30.697420120239258, 19.432872772216797], [37.41896057128906, -11.083612442016602, 36.227455139160156]]}
GEOMETRY_BASE85 = 'c$}r133N{9x5iJz5JQNFRAl;)NJ7LEA`u*EX=7@%hL)<t5K~DaLRHIG{-~*Ks2~zj^O%yF$5TT?5i{j)2&Jm1c`p5D@8?Mycip?zUH8U%*7N(e*L(K6-{G9|Wr=C)SlrFPPc`F8zu--YUWOqmXSf-|`wks8pm*QokRgd99Sj$Z%TJ-t=+L=+%=-?;aAQ<JpT5bxhXzF00wUv^1O(dx;uD4r8yYvHXTs1veI?#H?xW<s1@Ywmafy8kJ_j}kZxU>47!+*#%=Ul$DI+<|=}^%uu-H{G4J`TGX>o*nHqKpk6}L^9P+#KK7pEdM-Zi6=#<Tsjz1cCkiN=%Pa2L<YNDh^_eQ5Ef8h_MY<3>=IdfI<#c60q)bNOrH`TfUe|Mup-jWu4*Rz>?iHM^m<9}(J2<6oT7xIL(e_HSk{#C7{O^AI<kSBFU47VKhb+`+?B+zPs-*EL-~3e|W=7caf;lU5k-A5JYaK6aVLt#R{%wf*Pg&`(sNx8^e-5&1+XA<x}^`RH}yrv_<#y6;0jtxNl=r&g?`ao;yF-u<o`w<i6dapS{|sOLL%(caNl`!P~_;JT-pp#7qcYioRoJLYB3D2>}9Yhqq*m}qb8K>Ncl(EiVpVOp=Vb!{4-)=kG{f9q@`jkh19adXKMjazLxX?^U?GBs{YOKYrkD4C3T{AIPqZAW)$-K?eAsOO=B8n>U>q}R2XKWRSp!(r95|FL$|$9p&OEHg#pM%tD}8ZWa@=hwbI8|}BetSj-@2RqPDzpEOLz5c%DV??=z>%Wi5t*+ymdjoYiGNd8uGrETQyHDy!Jb#iyOYJ9koW`w9{jh#=KE`|<n}N7f%K)uUz-V0eY(+oysIGw;e|8k{J@qsm`~D2g-&}P;*Mog}ca2+b9IdJOgx%8q?Nyuli{}q~L)TA!*D<I=&uER?uiip^q6VY>whkIM_a<mR#_^6=KbPOpxN)yI=CPv(#+CK}{fyhLd79g=V}6&_sj2N#ujqKKN98qccn#3FdAOGLZ<dY5IxII=<92JZ*1?>6T-T4$<1peKrXrvErF0$IQ#=FIU;fcV^GUd`>%{)VPvf@Qo>(V?oi$J6;inq6(hur*v(A-9JgRh{dJ{M8$9law#_Rs3#!YWm%vbzc%&!rT_T6)E-IddIJ=j-HLi@Z6T8G%A^_Z_JIU2Wr6rk%Q)+H8oThlX0`zii`wl~tNqy1jTTG~%73+t`jGpv&fZzCT6nXdD~^=~gZP~(>ORji*InVP@7$6AdW2X2IEKkGlheq8sY7V=8NI)64Ab?_`-Tl@KU13e$?i$ihFe7_a(QR&z(?muGvY|cac{S?esudj6;?KK~3+*oxQ>)~EiJtys6k-?h(&>zq~pdIG1WwyqRhRrok^TrsgpWBgjwEq*wb-md>?uk4@+iKi+=+{)+PZ)&tvwDuk^P>mh{QtH$>THCEh{uMsiO~Ef&qaL($7$TEmZ0^_>h}!w?=b`M&#!BHV^<mEnVlPgygt%-u_rp>{AvDJ<L3B2y1%S1_Takl73-o7`?Q|6ab2~4^O-|E{rlAWdOjG{USJ+;IcnT^8IJRL<WuCCT1DfQ?Ge`7{&3{kw+q^PPsaKA?NpotJrdCVZgq_JzzOW5*QROQ_WL?rhi22Ony1xj3;Ky!sr$kVxu*5B+8#olEz4?s%pFNOk5;3bi1XYq?=R5$SONDmZdT00dUJC^9S#q!uk{Za7Ow4mZZ;|!x2N2}Iy|=l`D{O+adS#O&d)xP8aI2NLp=B!t-n<@2kRmGg~qMHJG2h@(c@8{x8obAn|Zh&9WiwuS)E5}+`Ksu=cl)Kl=jnY6XHF6^geFPKC1P!GVW>I%6CE?W(4AXF|@dz2lk|R+^=hVuk|rEx@z1Ci$VMMu3-Jl>ZjwjP0neq^XSz|`!Sat#JM=&w`SVD<8aN>EcG1msS~ul<#8SN-|~x*SIW9bjr*^_emwhJ<EDGQ_G4Yyh<%sRQRhE@MY`@6TQBT))BBLdts1XudwZ+>*zazRdY!B}^K|`~18U<wQlhlR%}p;5Uwa4p{c(AWFE<qX<-_S_(YO(1>AYL(6ER=O^|4;MM`%9A>1?!n5Rd+ccf-EUT8{kZPe%W<<Iw)o^T=~{gr4_Shp9NXw++U6%ju?Z^Y=^GFB#L2k4K`$vyy6QK1OFBoU4~6;=ZwE1lDKdC5-Fid5Ami)wsRJBIGf8EuKf_l)`u`EWvZ2xdH9psEvJh?jrKs(?$D>?f#zbi`elAs6&g98aLBcYCQkomwfK}3h`U_!caFG@|?F+<F>}8j?2jW1?OI)9q=*JP=|F(QO`6B`}pB1+%KL~z_^+og}WU=KZ(nbf5vfKx8q~ft=VOsCqJYAySaRRJAnJhntZfx-bwfA-}j5FHeJ_NQdiwa_IrnMzLn^N=jiBm=x5zMd|o>O?PtHP{g}ReQRhBm@%OINaZdWR!E;y5iP(S6jr1I_{hEY%Ka+}h<!BwRJ+B(Zd2|K#*`RlEP8Obr#a5yHwei|d{@zrqll2>r56=_xa(9et&MvfXehBB!(wf*8_0AwZu`15JudbtBPwr?u_DDaC+n214cqM)_1n(mew{ea{{)IfNEXH_Cl*azgE2j4WtM3Y|hq!Fa*Gor@n~o>Yf8F0OUuA0HzERZ|b^bLMb@Xq8xbH)a8~fKGpY-?9|JYub#|bvnxyEqBA6?h`k-4ZL>e=>dJRjY>i*q&UD(YD`1MQc0K%HGCp>7^qHEw(4ujj4p;xNpYZywsmjMnqtez-pFrw=b8&xBz(pKs5^zL@X}#+w+Vd0IcU!+m7xBecK#9ojz&!G7t*_bQ)UtbZ5GtG$LZ<}JG<-Y*Kzu^WCGj~&(q@%}jxMdRkSi5OSmIs8LojpyIkgXe*qyN!#+ty{AZU$+70*xfK(*WU^2{89zf*>w=|Y>|aJ^Lf}la00Fyx(s#x`5Ef$lZy6y4may>!@OUdiT1zc<Nn^~Jf2r)WZ}9mF6e$VM}Cev-`tAv`e)<)bVX;3>$9C2&kEnFar=}<c)qQE1lN6h7ImnUj{48Ki1D7PtIu6oONZlpYjy|md3{m;F*(>*;l*@5V_&3b`&j!N{cQbI0>0S`{ZFWf^L@7y_NC8qT_=Xue9X6Zd8~`Q)9`+=IvnF4&G+w8%h8W-S<T-Z;DP6_st&qN?8hIY&eOdSZ`K=iNS}!N)7EMl&o4d-`!xR;=BvHG#<Moo!t-$0TC|^EN8`4PLx}(Q68Gt_5R9wv`T5lLCPm}+1D)~y_|zBkvNa6(KTpQ_nR4cpxZNcg&*uwz;(VXg8trq(;M|+<iv9!J;JQ~Yp#GQdVV(5+5aT^i8uj#>fc;#pH~N{JgL9+9EuCNMMH0r9?}YU*`+MGBhN2E;7k%z6+}B1(GV)wz!@BidgMHU^1g_h?HtPA?X3R^J9oHSRANhBR#QnP|zW=aYnU43?mh;f>aegmy`U?8FJP`Hyath|l?yv35xHno9jT>v?aPIAN!gV9K?k>3FePQnl+|L?jpndn@=!g5o>Ya)BqF~HR!^Wu3t%ayV@gLFNArt3D_;<)>`X=q)=>G%e<tXFB?%=u^F4))Ox1j&GhhTowKgRrC*oizJ#Oie|?_|u^v;C;Y({p&weQrbDrsMk$BXBJ0zb_c~i~9#(Sr6vJ+PII`$isfzG+ygzP1(Zp;V{~laMW?xjgpx6tH&^pi@Ra{G(L~@f9hvkH-9zamzUt&n0@}0b!BaCiFN4qJM!P*fc5$3GMo>&4>0eokLkGVH@6|5*oTN;KBW7_*q+$DXxxm+z_{E7<J?$j;6AgfI_i9VCGMx^@O_N&V-)hKQv!LGbHw{crU&MCY?`(=2ba)z)|DpszAoVd^dErl6>RP6V;vUWuPwyQv;?&8u^;_^QW@?2pJJVq+KKhB5Z|NNO4Y|Y=@W=~ndpyvcJIUUz*})R_x=p!^CRvT_UWluw>`pe-Bb6p{)P9)!nl>U7VkBorIEi6-m9#XNUWdF|H5<HwPqOawP>763u17e9@8Ax{jRe1Z<d>><FaP7#dQa+#(Zsb#B<D^c4*&kCGJO~#^U+7a}2KA+ZFr$(M+^|vx~-Kr;Nb&oK?;=DjNU$d$y?MxNc%M%<t_v=x5?GjO*$Ejptu{7yS(1iaICY{llvF1=jP_D6O+uKjqatOTUGEJ!AsL)$J`jZxnuy`gAJhEAcSq{ZMn%=a-pi|5FuwFI}Z1p1VFxL!K`^v91cwH@8`c^Lf?E`~-DaoR0dxsD*WYA`{~}IT!I#r!imsopFDOpO1c8&BXnE@tE*e;{0CJnsW*L<bI3%bKUX1_t#(JJ|4IT`7dzBxv_O6?vEDZeo4q@@GSKIdN%s+J|5?4{4Lb^&^px9+==zDWE;+($D7c;LICQ?_al427R=YYTi7qHV{sn7w-xO(1JS=n9Nw?L*oOW$3`2a@H+YYY*@1DTjmCZI+G&hy#cs48@*V1L>x%be`^i`KwbiB->e=!v)=AUrxDQtI#J*c_4)ICvq5pso%zMOn<hgnp>NC;_^WNneuKOqx`}g<JsQ-rR{62COo;P}I!M-T=5dAnmMgO@IaBe(!hU?yIfO>{mc%Gd49Qo&UMcwL+!Fv9=WR$i){0-J~kI|^}@TwX&gVvyK>Bq3%_E*=qeacas+p+E#SE`@JjrC!8FBowa@4dDB5&yvv`|(T}oZD_8xNiBz7}uL;(0(=I`CINF-eLpl-@F0Z*Sm}Q1lPy&RcZwC$=r$c*=By&EAi+_{5{T4w6ESA`D}5<{8ng(_MR;@ZcAB=I?UdM^<#C!b$?%nI;=d8b^hKvs1Kiu%o?{*pK6_O-O$O1f9a0(miz(w>5_{0ItRS>z3heY7CtwYDTnp&xbG|DHGR$_&#&TfUGGsipZ#~E{pTN{ed}YW|4*~9zb*|yKK9@6Ja8uv=f7(r;{2Z3D83!{ksY5Qp8yZc*S_6NipI@i>+$||s}Y`y=1xWY-RoEnh3h##9r-jpi#m64z;j)Lg}ClC1J4iU6<jxKJ+8am0de_0D(02nR#w`0zfMdQ!w{7=+>H3RBEPDXp!^j2fB&n>0ipk^UsX1$_y7J?rFTIN^$Qe4f0Hb3lB?6h=_Xmc6Ir|iS-dqloZNsCu0xL^i@!mxL#{^&H>S5Ei@!^5Opc_4U#E8^i+3Z7zeNtAhtl67i@!}4k06T&kVDBnlyDVF*n<ktB>@T7rG#73BghfFUQ2psvUnGAOL8kpIGX+*S^Rx+G`TG$97F$rEdC)mhWrjC+>zdcEZ&_g-k#i?-jv>+EZ&AJ9!3`TCpRSrQo?TZ%4G4<WH)jNO1K>THL`dRxo{l|m!f;otCPjU$>I&j;&sSgWOquqD!m?AyfL{d*_RUbqeqg(Undu?OJP^KCq0BL9!eJXA&XZbdy>mi!Y*_VvUoMJ3)w~qH>B4ki?<|;w<3#2lN*v7QNm5=ZOP&><R;{1lyD3BJ7n>W<id5<f)cJxZ%P&qB#XO|Ym+O{OOPv(i_y!G3)hOUL3gB=B8z*G#ofu`RmqOzl9X^6x-Z$6b6m#wXYR{T!cKHgvM1-&i4u0EyO5p9HRv|7jq_B4-iX|Y^HGBmu1N{kqBkQq;~dnYgoEj|$-(4`^h)GPtYgI@^{q(Bj|1J2?8w?V(94h=$i?YS<l^M=bZ4?N$5x(RlU$QyC{GDjpa+wKnO_CE1KEMs6CP2ZFA6lA5}rs2&!&XaDdD-4@FYt3WBLek5<QVVf;@uPOQeJoDB&TLa0(?no<5O0k@=0MgwrVD6_oI5O87f^Iys%=`Hm9Kp@i2_!t*HMsq{(YNgU@?O865>cxaKj2oItUq$iP+SeJp6a6d{oo}NHXV7=lg;r<2cQ=nc28bI$)?$0&@DB;1B@GyD`IfeBdMhTClgukJuk<(cBZz$nql<;;+_y<aOH+?mEHRoeDCA^ms-bc?N=Ww3(QNsHv;h!ks?<wI-`aJSH&R-@aJdF|_MgN5S3FmJVC7etNe^g|?h5OQb(+81zljG<E$#LYK^nT=?<XCz<Ii7PIOYcSYD%kv03KU59B?pp&=+($UWPeJyG9~=NfP@_=;bL@OaxwB>2D}PcBwU;^FY+%2+>sJ?qkECPn711xT!Rw!qX&_LI0ipT_%%xSi2<)nuFUa0p@h#;!g+KVa~{1IStNYefP_!bWy~iy_Tr46AphI=XZ*ss^z-yz$l_9$^ZYFQ%z%W;vu<u=H`b**CG1WKd(i#JeyocJC0v#gzGlFsF4tI}v*c^!J(Tb!dLB8Cb=gD-Z>EH|(oc|2aQs_~)J1qHeFHt0oXfgwpoEW5!guJ;$l_9$JNztMf)aM7yOZ5n7iUVi93}jx0WV7~%bNX32_L6~v*~-tdsvrjO88q!cmaJgc{9hqph#VWXV7QSmy(yVF0&}%MU?O^`VsOG)@2tZe3cS@OqY5+raO~G!i5h&!Y>&sM=r-Yy`+S1Qo=jw$H~W8mz|XGd`fsa{af<49RKtpbrJp-eFA+3c?Rn;ffAlV3D2Z2A}?ZHW>UiIDdAJ}tK_S!%PC6u1|@u(F7>)if64f5*60sP_yYYV`6lafff8Oz34cwWPoB^5e_f<5!k^PWrT>fkFV^K#O87HMcr<+qc?#<?ni8H&2`{9tC$DE+7E;1LQo?8GH^?_wmot=bJ|%pS{s;LF*5x84e3TMiLSIW>%keKMQWxP01@lt1Ko1Q___+ZIKQ$oXij;75N;rUCfgC`#708obl3syaf!8d_&%(b`!k6jK$<LX`WlH!KC0v@hN`9r8XLWLEvNt7MlO8}0V16}=<Spz&ccFWdJ(;%)C4AR_giq3CJSRD>%jA>f1C;R3^jqXx9MjMIEd0QLge!4e-ehm)SE)$e!e!{LbRV)0^LC|#OHsm?47iNv632Cte2Kh+65dEZKt8~{H&VhDC47bcfGjTgT`~U2Tlg6N{t;c`kLa#sk+2gbe2=kG<Wd~dJxcf>CA^%zgS>-zFQ<gFDB+cKi)=B!mBv4L3un-`(T|ajG4E}Z@O4V~K3&FhpMH<=`y9isl<*e%LGnT7y@e8<LkXwSv&dP@FSSVC!sF;)(KE;y%=;@!cnu|dj((kdoq3<5gny%iPt$)T|H`~iQ^Kn#;V<cP$a9$Amqqdx9z!2VA4eX?yhl>Pc1n0LeGPdH^Il8|A1Y8xTZdw9j{nnto%-j;F3%3H{70()`Y&JoHAc~YnO)G=-@nv|X<I_Rk1>iB{E?UJaQPO=_zy+R?J)'

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
