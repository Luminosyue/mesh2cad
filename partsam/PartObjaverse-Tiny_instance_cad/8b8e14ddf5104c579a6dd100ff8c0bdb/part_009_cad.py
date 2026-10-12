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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8b8e14ddf5104c579a6dd100ff8c0bdb/part_009.stl', 'relative_path': '8b8e14ddf5104c579a6dd100ff8c0bdb/part_009.stl', 'source_sha256': '7a5ffd7d750b4238fda6b3ed0e56903e74d6220342d1fa65c0002e026bf19931', 'input_faces': 360, 'input_vertices': 268, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15172606706619263, 0.21337208151817322, -0.09260452538728714], [0.05162224918603897, 0.460971862077713, 0.18825030326843262]]}
GEOMETRY_BASE85 = 'c$}r02UHf<w#UaVV!1|wnnWE<>|8}O>a~u&A|zOXhz?S1Kv1#Ai6vY+Vhu(e5U_v+QHf%7V#UOUn&P$GPZLYjSQ1UtSl)N`{(l$d@ZMT)y~kR6{eRz|&7L!7X3jZtKK%QYD(#{0PhI8BN0s8unu;Q#qT->%hsRAA6&gOiS#<1_63XAm7e6jtHeisie_#nEUYXV~EPQ-uT*G#1!wwN`8+xe?BVytv#DzqUh=~ge7k<x>vE##?{`jbn*l_3PMn0|EdZ{fNd#N+j|Km>uXA_J=V-6n_O^V(0eP_|8Ge?$*&)Ses_J`;EKz>2f<>IsDK7f2j(AMwB&zd)1d{(RVV?QE`>#S_MnEt*&H}ds1sg!S=eJ@FTHkNyG{aTwZQ2tMECQ_YR)!27Wq2n5J(#SX3l_Ov6x{LGApZkpRhCMq(zHiof@+ZVBp!`KQ$k%6X{*mf*U%Zs^kDeyqQ9A1!<!4@}I+~KpbvEX4oxU$-QGT;D^35OSQXQrFk%g3hY8B_lZz~|*ttaJM2S#yy-$Pvg%ab!GKRB4%V`ZEr-{Zt&s+-b<{TWBOPBXuF%8#s1zE-E*8S)=?2&MCSR*QV=wfiaZYg`DT<9WGpJ4+wr`mz2|;<J)dmfIN{ev$k+K6JelzrVhwzboj-{;fgOetql%@~uw4oh1KGi;492C2o<g)%D@y<~JBh{o3~g=W9B*bI0gbLNz0Y^8?=EI{UlCQhv@l&Ohe&Ew^*naG_R@Rh%Dph4Zf@d`j&MUBLNze?D#=*HK^3<orsJT<78Z5p@1f{5b#Z73`l0olfoP(t>=opwhp%{l8D8{`{~B=YO`A^Yz+vy{y27<eLjGasTWuh$P?lsYS;<d5_y!CUp^g_8iZCsq<XtS(^oX{zJ)kJWl50X4M@={ovV|eARt8`%CiT$p7WUK{`&|S6qMZ`4yD+_{jm%%M~y2{Xai}bo~zYS6f`ix6MN8pI;Nnw<fuBon|ZP{<ltte?{%7#dQqt%E{C}1!3f?DIbw<E$g|OejlLkr~Be+ee%_%^V5Vn4*QU=UH=L9$*Iq&{+yrlC_ia9*D-f(pgPa{lW*O4gY!>g90<wVNA0QBg!Ai+%Oc&|oPD>E<m+jXne=xvwJ)iDxlr;=zlPc5XLyruR!bt^@p{q@I<JRabLqGno74Sc%sQS-d2fx}L+wwB;`YQ%rT$SyUfE5@4eEZG{4hVNqwfx2ze^6)*M6$EliFEpeh$?eyp8hJ)}^*lyGF#2ueS-Jam@VYcRpT_8~Li|eHu^97gfkNX8g62e!s91KSvYuQz>sv0{N;>4AnQ9r*Eg@ADTqIqe&aO?&ivoRM*jH0M~h$d7AQXd90_;e<fzq?|b&)`zLbgHfr||XLeBiDW$2twtPPw*YwCG-w~Y2{V+R@?sKDg7Uz#`MB}_ZBA424eOZxwvtH9H)Gw39Z0uarj}0VW$%+1i+I8^RcB+$Tu>WnCN#_x9liQVch>zRIhpxLeXCC=_g<5={_s%@ZzaP&2pab-rs>x}`$j@xdbr$sE{0es{-w{)e{V~@lUmNn^n9Yx!$N9IWAE9>cd%TtE=ggz|OAo(6_ko(`V87!w%2)rnlk!bHn|v$xHC;z5XmdJ!9=L*hvqld-Zq=^G>A0IGvESC8d}G`=@{I}ivZ((@J*N7OmSKmfU02qzzv>{}KUV16<3)Y*WEH+YM<;Rqgk_xH*y8!?mvqY4HjQO};tZ;94D3SvU{sGHUqARg``HTho1PHL{{3>~TSiB2|E~VztDjWne)C^N`DSuU&Y!WH&-c>=s;~Z0hTA!LBG*|rmHT-n`_`+e+;72dX;gR7^GvFf7fJ2c-pl9n?eUa+)e*t{5U`ccYwRP=_tELNdhiPF&$w&kn{#`T?+9x|zSVI%`Hrg{cs#k0cZk~Q9nbaGHR5q;^#$rrt;#sAQ}z;H_ZuIRZ*=R)$6bD$pX;U3$BX)o`rnYRCLJeV9n+cXM+NXW-01-wSF`G}U(kZrE$x4ye6z9#*MG;0`$6G4=IEPS$nP<Lulvb?)E>vhYwQoH$9}0(RNw4#g?w}OM7|$t{>=Rrx|aRazPA2UMlWLjF8fCQ6Ta?mn47uZs&IQkZrc5&HM#!E8u>+ivwB<ho9(dWtB*SHaeX~)`HolIPAj>h-CuTs{iZ>-I{KJ%T>tnpn{Os`<?$i5qCLOaXueOvuG-s^v4woI_Sj>#I_+QadZ5*;qqh8m_4t0Cw9Q^8Kb)V72T@0C{*==^Zr=?#Y&);7&yuev?zbOzHb2)^?zuxY{|hg^f5rsZ+N0O?<#E2mWLv%(7R-LcpZ4QcnZoyf%R%=1kEZecQ^C`gZ+g$-_H5Y9`J>je-`$PYpT^Q<H14^4^)UO&_5_=6?rKcFHuGFYQQvW_KCOqf!TMHPoq$fXu6E3By2Ivsx2AQwBRDSG=HD)VfuEC#Ikw|Q{Ybw4nYqiBpS6(2c{T9P?xMc#*^lNsb6uHSTmGdQG{39&ciH_9qUk<#Sby%Zo!8yde82q~Z#%A@|D4D9szYt(Wi~j#*Y{RRn$1rQ;`#AhtwdX$$V)tr->S69c3nn2=KQTqr`Y`bw`u;>cHBrS>N_HW*`K~*EuG)~otr3M8V3~jboQlj!{`xBzMd4v`PEjje|aS5OXH8#Z#d^m<CT#Y$i6hbDb>B$m&QX!cy03K@l(lD*q6uK>(4e)9ckQl`SQ4Jc%CP}*!chC1o`rOq1;a7I@0`N{iSmqX+Bc+4dC`j^Ot(97uT2OJLU5poG;CfnqPbJ<@r?cZpX)!=idbtxsEhn>wBNjb1Bd7*1F5&%j*H7@{jCG>j&l7cl>-y>kV~h7W>lrMD3HpzO>G9`SLo)%nrc#VP7w4)AMP(k=Ivx!4~$V^_UjDgx71*`c0WNf>d7bX&(LAm)3{+t9D#pT4!o|+OjXLGqq`+>`Uua?cr~9-OQ4mXq>ceRpI;T<u&r<b+0335Bt(OS&JIVb)<E*;?ZLRU0-P(t_3$FUtZ7u$CuXg%8{4+zEb%mjjImxC68}0w^PWM-WQDYbL7kK7fRKQ<eQs1@c4XoC%<3SN#Q!udy1o4C-U_=5j^j_=tR%C(Y*=R_cmz0Fwb`5dBJhVr2Hl`X?`)*Orv$b@%DN09V26C9x?C5@O#vici5NSo7CsM*V6B$_bhdJ>KBwRy_Xs7Mv!0ZJ#N!7dLNbF`*iPN<je1gX6+-Z>G$$`WrINS<@ZqQxDUP8%I~d8(;BotC%@+^5x>o&deVEbvG*?TZ%OabO0^fXUnReHD+#Y?->BGodjC5ilqbK}o7+DoU)l#y+%8U~&(gkua!;K_`33fU2Ic3ZIdq=VzJ#H_o=eA*_A!(J?=Gg#(!Ph%zA5?gK8aHO&@z4=?E5OpRc$%dk@jH}pTR50m-lVTXV7uveICVg(i+N__k~{ge?je$_K_5i>NG#g`%X%f$<ML8Pqlhj3SAFrUrU)5MZUZbX0)C|ezASCa<4gG+Gn%=elV4eEA7i^U)>{L-p4b#)u!uKY~SzoKgch(PuOA+=S%yF)}Wi5FYQAb?+4L!miH~K>(j}X_c^U`S-cLC_C>Xq7s)TSkLuuclf3V0Rd16{^`(7U?Zja6<$YZ%_bB<r_JK26WsooJ8*5$><jecaN{CA1w7f5^-18&9*gm$;8qSyYy_Me2$(Q%ZmB>M~u9WxHjSXq!%lq(}=T-KleS0h2eKWO3+UM71*JNM%UO+kdE&0X1N0@P!eEE9^P5+a9>3a%easMq;U;17{Yah*i(eFY0ZQt&+pZB!1Ue(zIXSgXIN<>JJuXcnfeq8$Bf3-8J)&J_NotCY=|G!`DEO54=zcUs>yMl%O1H2Ht2-*(32)q~}cnP#4SZHVP5^y3^11Ex)Lc4&Mf|H=#!Aaod&>rCB;FZvB;FaJNqQ9X%q20hj+k$(7J0JwNfwl&>0sBB(f`zsK`+&U>g1w;4z+T`c(57Ia4Z%&ojSzzCL*E0}2iJwx0oMh;3H1QK39blr16Kr>g_Z!91($*<;8Ng{(9+<N;BwG1V4>x~<-qRH3Sf6|WoRXEW$@n+f~!HRfQ42CR|D5T2!01z9b6k)6IvZy6Z{tR4e(pwT2N1LEwBoG8?1ugh1LTLZ2*23+!*?IaAR<Dgy8p~t-wOtgWm^tf(`(80tZ27gM+|xpnJe`z?%_*PeIRuPl3OO{s0zw75qK;GD7fm=ne37@NMWXV4)Aex50OzPr!G<_o2_g_rZ^#kHL??zd7Sq=mY3uu+Zn=2jJfkf}cWPfQ7ySKL!7V5d0Eaq6G6xuy}}smI5o_($KPCq2<7(!ER7@up78Mv;w$1xD2!;xD5EU!uqGeEJE-f(0kxNz;~dxz<0nmp+AFff`38?z6N!Gg<b()1OFTPFYv#?mk@$4LVpAc{SJH)d;xkMd;xq0A^0HlYw$AY3h3A172uUnODUXF1TTjkQVQoF!Aa1gO5vO(cq#O_QaHy6PK2IR3g<+@OQ5I0LJO3_`BboL{uR6kdQK^vqXjR79svveQYoC@1usAdo)0|?o)4Y}Jq8x~EqEUIp9sMT&=X*x-+&XqpCJU#h312W?gtB<4PN7n>CX5BItm=-jM2^*5B(UN0!@Z~3{D2GLI{pU2p$U^4UT{ggN_D|#<7PX1P??A_D2XFju1Q%Iv(t5>qLa$420la2*EoLf;T~v!O1wEO$fp35Q3wjvEW#oPjr#<6dd4;51io(?FaS+_dy8m<%~dQ^mfKa&|ctP$oU8%cql^fNazRPkzgGf0M^0b2*FVZ!68sza0qxXv=4YNc#t!OK>I@bfcv1`eWAU<eZhVR!6Tr7;0e%pXdpNc=O2#{JP9Fq3UnxVDEeXwLhw|C;OPj#qo6u?6!;T_U;`QsHo&u>QQ%qNPZ5G=LPNkI=*O7|!7~tor$GmSU41<bA$YRF_qovF&>`R<=xf*WBG@15rxZR@g2i*T(;2zW$Uz9+2h9WT10O&L-s_C5(CyGX@OJPvXfAjgcms4Ncmwzggy8iE!D-MOa2hxjx(}QR-hvRE1w8=Hgnk7*06u_o_zEF-x58tE&|T2IO5u1SIHO2kWZ=4F;F@H>pN!awYq%ACG!43~$n_QMx*r73gl+(DKp(m8AHlBsP4Fz}dZqB56l_4#l)`&hu<Je-yat*IUITVLFM?gqk>DxNE#NKaQ`d7R*!7$WjxTZz1W$mbLo>mdxCZIa-Cz@%4c!fPU8ih>;Em8t;Emw5&~;#;(crb<aR|YY&<L>5Vc<w`Fmxa|82lmB4=i*9_(O0gLU5c?I1a`^)4{Iuk3$Il9GVTz#(92@5WE_?7Q7bcwi+Qg1|fKiGyMCNDCtq^fBM(k!XJZPYK#6OuKbtwZJnZjdDU6#Kbt)M{mO`UW#<cUNm@8e5pVL!e*t}&Yy<'

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
