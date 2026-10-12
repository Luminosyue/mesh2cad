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

PART_NAME = 'part_014'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/423121778c4b4e849a029b8281c68bda/part_014.stl', 'relative_path': '423121778c4b4e849a029b8281c68bda/part_014.stl', 'source_sha256': '030d92a984bb0e50f6c2ba3e9ef209a938851fdb4296cb025f3ecee292e7da15', 'input_faces': 398, 'input_vertices': 315, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-23.962444305419922, 100.3105239868164, -11.758769989013672], [23.962444305419922, 152.84075927734375, 30.753347396850586]]}
GEOMETRY_BASE85 = 'c$}qM2Xs|Mw>}{SLJ0vvLg!LK0%??lUM^Dnl_E{0DBb`;5djS-?E#mf{5GUWZ&zso(o_%w!j&je1eD$+SCl4*5v7U1Kl|HXG|YN$t+(FGT6^tpzS(!ro;l}C*#n*01&2gA`d7s{Q?zvdLX{jxq^J|+ypoYQY(U?Pp~-_^92w+9f|tKMJ)`5}9Xj<0a$a#p$Mwq?+BY+<u`8}=|AujiuDJd~GKXcR4}NAyX1@&K+or!TG{f*ipG$u+!<6Ie)k#Zq)vKB48sqvu{uMSM`1{;w;5XX4v2eOu%E|L<NZH?OA9#P~!ye&%6=qeFvMZr=eb{?8D?k1{@SdY3!MkQ&2k%Z>S4qn5*2~jS|62q2_f<ORg5MRNr-JXgzqjz7UrJPk-=)LAI}eWo@2x#B7JjmtDnGLNGvMd7r~*G1FV_QKI|1!_+w?*_{;P+;drIVhclEdxt#NOyD>~4;4B~NLI#wFLpP2>T^K=pT54_Q&g2wT0@XlX8#N(e-wLJQHs55xqs$n_~N3+o{cT9couAKul&Jsz8Gw|!5bzr~zZP*8*VoM>Ov8TbikHxG1!+%vqc~Lv?o*8cV@z>pi_yajL!Mg^9YJdNl0sp@7M{0vFS_i!U%B%42{%tFGcg{%l<9iwL2VTnp?;8`;2mI_Z7h6bs{Z@kyT>nb#_rC%^0oM}s^W*P`)3<eDNyI;DB6#nR574eNphzU*@C{dc&vA^iXXlb4cn-0{)P8oF+GnrUcm}6|_qT2cduRWQBiqs60^psWZ|ZwhcG(W$os#!cFg`0LBYx-838m1^>TBQwU+mE5ez#W?{C53F`4){}@6H}j7XABj8F=p>U#kD$>3_oij>X`8nXPo32P_XoznaZfzL8tUq4{Dw7iV$@@XjZlwO?=aJ_$c3T7h?ct<T;2c<*(>ySKDdK1RPI@0zW*Wc;0u5gO0vY5JZtYj_`giJWAN=af5mF7E2VKZqZ1pU=PtqECVMY^)cC-=AC$-V^T8aaepS3_58wc<=dH7-w&bofW}PUZj3brz(G7Zh7=$d{^a%hQN>K{<wnBqaOqBPx)Nm{|l>2!%zEI^?z`VzK7cvMI+uqx04Y6vH{8ud_D$#9y$Qtzj800i>vE)JQv^gW#FB@@#vQm?|^rGzXW{XhQ<@<b*T*e^?6q9!)n0ZHS-$A!Er*h-4qA@{nNs#Af6wy6EQw9`kn-)`CN!6d<1y^^u@~0428Y#`xeTFuZ17qGy7rhoW7ZW=eTr`+RvQ^d++O8z<YMB!h7Pnlo^5Yywc#^sdu$se_pMM`j}s8Vchl=()h~^u7>*D`QY8xg8QP~+w;(_?_3gi|06H!y#3Wq*t`3MDStExd|-8!@^4<K2|qnY>3jQAd!6^zrh#`o`J9eVu?^LsJ4S;KjNYSu(x-xVu564)oIRK8d^KzpzF+^e#o*oNg7rQ8ww2EF=idVFY`XC@+I4L}yMd3ofcF&Q_}{swagOdAhx(to=zE*&jYYeUo~R+bFQhU2c+UspyY_UR3f?=sB;pTbyi`N$yJ6jM{d5Fzx?8r6hyM5><tHZSJhQbM{Cjeng7-&eXn#kR2Jg*jqWtNj`dyb94&EQ0Qyu*c(|O6+xd6Pc_@~MrU8;U=js@>pJs*4^>X_O;w^IEl6;ylg3VrUaAFGMqT@42B_gzMRJukP#c=~RP$NJ`EoKpWAA4Y#&hsS_-AMW-P`q?}f^S0;bZn_>OEynoxQ*z><>ute$>uwvZ@6~6|!H;kJc<}y?)ph(A^h7-FZ!YROHZMWPxz}clr}vHPh|6284B~Xpc@e*NdSzk#bT_Swc)U+Nf_2SX;xS!UeT{V<xVI_=^`nY{_lybFb|<}=fN=_Y2k)0JI$YZw$LCnKTRHgq^_K1*W|dEbpO){I0iQ8L*RP4k;6JeDlNhx7^J$$wzc~hbf5FGW`*TCp|L9EZ*Rn!t|3|X&FNM@XJ5$%|I=m}G<80mnak?`m>-V%t_aUC7jArnEYcAeXCu)g~e}kp)<67HU-`}F;bo}e2W1O9cC|$4i#rJ|;!9f^zcj1|Mp8gS&)qi4d^&eDP*XM(O==;!aA>wz&pV9UC@<!dyG;0ET*X@r=z<y_xj>DTvl3@SM3*eo-MYO*+(-5a~usqgtXJ{Cnqo?f^eJ>9VFOKK3@T9i8_(Qbo$qCYVZuuGIyN=d=xu+FIJm0TUe&}l0`v>g~7vA-Hs*X>O4mzG+zg7_a&X}wA;~#<_|A{?e@bk<C<<A|_I6JNc?+V|h<I^S<{dH=5hIQK$Usva)Ix#wK*F4~z=}BsT?4{<=1KNaukKCf~Rqr2@VPBz70q~<Hs(roEuy+@@8HDjzzfj}3ld18<eRm)0|JBcR{3|D^|CVF#3Gdn8Lg$}98^Ye*q5YAq691|YjdN-N#Od9X3f`SNU+3Glk2V1x9eP-JZ$>Ab-%b{41b;7h4+-yy)csqaMPIb*q<8!d_E*^7Q-1LN>F2(M{|SxN&zRF`qJ61n_6qMiKTho<9@6*|?(GuZzo@&eBOg6k7wr@q^CkGoU#tDA)inP8F<angkIs{>1``p#|L%wt=<iJ3hr5<UX#9u19R&NFQaw<vIA7<x_X|vED!+TJs@l&vg*ZKTM)-txjW6C4@kds|`|0!?x?Xs1iy}JCZ@cSi|DtyZ?+o$i^R0gr&)2z~avb)roY(zK#0>C(WBbktALw#U<Iif2dBgXf|2*2gb4%y*?yd0N`X3Ivgg8UEkA30-o^RmL&C6)F!Bl-uinY}FZS(I}VSn}#zl){deVdNtf?u!uReyRm_(0CaYv7ZYD!+Y%+VB4D55#|g^GU%9I$xRh4f}fQee;%{hkd2L!)=X!)YiY>TkJQj_g3C>v}e8N@?GffAN(%lJJRQ2eMjcIgT3|L$#;sf^_|Lhjd8cWYj5@*@b)|)^9HmvZ+J)T0`H9ePW#(-o<1)#|G>XB|HyoW-&ymOGv`s9WBfIbYdp6vp<nJT)rz8i;6mN+tsA7@MXmT^@YDLDzCQ(D$NMkyB(yb8298|;?@c|c-{Z1$*gMacE)M?q9gV+TU-*}KShPJ4%e)P3&D*}rj^KTZT=>3Rfg3oddpj)yA6Ocy-&b}?e2?y_hrxU97E}KC_xSEy-CLJ{|M1r}&JzLf?(Bi!1LLaVdvqP{gZ+W5FR-`P7g>)`w$>xJa{|2k%zHZT%`1j@JPjW$2|uk?=s27`q0h^#cNiaQy_5A3Wovzu^%V8idMfKLcx(NY^%{28dhNY37yRGrdm~-nWj_Gk+7HP70dZLS2ib4H-r8@-{sh|EpU8d&_SSyJ{boTu4?V2o<8fx`{_2JH;63fz;kg8k?Zo;m`z6#{`z6m;t;?z33F^Pg0=$Q^??T+yx$l~(`!0Wh2%H!FkNfl--BImj|Az6h_HX_}o56c_pFup%^OvyCkbNL{Yab~4M%Y>VMxWDH`HJh+{?|$PE}XVA!F!*0O83=6-%;M|OA(*7FZHzw;2i8UenR^j>C*RY!;_U@7tvn%1DEwZUoaGWU~4VyZ~IN!-#O!y-?2gY>t*#j>b+b2Z2DOFN&3Awjr&zbKi=-A@7vj2?87|6_TZf7{WwMYwQHQNUws35?o8DA*4fh-`+3=iLtFcB*T{Ep9t{L)YP$*AFQ-Zlcvm#}_#d=iW}gpxYoG5PdqwT<57Bm?`VH;Mc>&MEIxooi0>87)7jhm!y>%Xu^9$^)^NXB!(4KwXd1o7V-<7!<PnREXo|1DD{95NGk2z<dJdWqAR(j5o^BUT-&TDe+gCFbMC+9@));UqmmGEnwE9D#t-a3cMxfS)+xmC`&h|4<Xdb>8qIC)M@*LbF^)VR%g8NavA%W}Sky>-5p^EiHQoyX<;4u979UC#T6!#?kKjMnwa&JV0j18?UOB>w<y=O6lo={%R0uUMk_3dwJPxAPmh^L2i;@*$ExL7Z0pMDi`LxAHBLpFzEqpOJhH%2qx{@;`{f%Ku2d2)vaqlKc|tt^AVYqfl?<qr5%Czz4DuInJYT9+tcoerM&iBo79AD-R}lGuT^sGs&~Tua#$$yd1QZmy<jm;<EC1PF6$kuHYu{@5`QreVF6}VQ1w7C4Y$cto)(m8^K%oM#)d2Y~?2<pQ+>hU_MjwpYUVlKP6v^e&yv$ztnuG<X7=KE59oFSopQ`u_sz7Z{=?#-;4fP`Ck9!cXj>TnWF1s>}H*Zo6Xks%FY|_SggF2XO_G)%2r-l^4N&m%41938@!eGmOMG?tvtEp)ls(c>XL`YbF}jClD9`ZR^DFn{P?|<=a+i{XzN};?h#;b-6P1o1LCsp9bU@<Z{JhMy$1YP_Zo5!g8p0gAaZX4-nuuDdltlP-Lv?{dBA(O1nE6dqmH^y9(x+ReP1K@JBZV|-*I;@r00NvGxR=d%p~MD<(>%f*!M)wD(_9JtnCge@%Mcb{9E@;azBOfweF|nJ`4S_?z80n3uWv6OYX~HZ{3&4{TlpR_iIj<@~McUUlYC88<ws4#H^;^?Rz@8*8^|e>&ZPJ+O_Th<=zlw>)z0{O!r^j=nr)MIr}f1YvleBaa;F~a$gC1>%P+6b_saTT9@)yvk;HBahCdt9jpG^G}Ab*?ga0?o2l<r;YrH(+SdSO>z*_)Ef>7+U^V5-O{oF<J~zNWaNpYLfm`JCX4fjkmohWAk#Hx<>7SnO3Ry_`%hUh;74m@8|J@aGqlW+AE9B-ThW17}7@2Eiz4Xb*4@NE-$u;tUk!42SGqTah0wZ&blnrv6QbtM`Ic3UwjGQ;J!$^*ioklJiInHu#BhMRo#fY@qCSTj4A2Tw<$Y3Lbj0`t2)X1~)JdMb$dl`8Jjr1_m)krTRos2w9{e+RWMxLV&@ikE16LNynS$>h_Ov(r&Q>ot}7Cp+y6!N3UiTz9DGTF{c^f#E?K(;xUZKabF+>d3^8Acu_7Tt|D)5!^*#`25wJ&k%QaX;2)P|qOlM}O(mPZEnf#c}w_$nQq}puR^e`Yv%9^Ngd7R4@`2q~(&tqW^SM3m-*YfjF=3D)miAvFQ6ou91&oo#^|l52Y_@CzLTrxiqnGMOYSGnB`zf5%NK-3ugJYqgZrM&_DPV%c7m2fA9^KMQ(6hZg6Y_7p84NYKOQWaR{~8hLA7Dn2NC+LM%F*QpiXo`EcUA-xQ^eBrZx^g1RiRJYV_#^1e&?9_8Eo#L@3szVCG`ZzUGJ#gX&5<18e%knh{<eBZ`wzHifLJB@V<^OXf}rk#)2m(Tw?;&qJYlYH$hqh6E`&t`cxV|bT(3bFV<VdPWdlPqs0H=TM0@fO-_CO*pYmn_Rz#F%lcWTZT`l&cX(@;OzaE>HcJqgZq~@}gZq|M1sYC%QQ6MFhuFS0ye-?V_$p>>{p69ZMX^n5q$1<2xZb&PW1r49juEl_@dwQ<*xJzn9<D%I7PAQjfgoI{C2FrBcTci!@|?J>ojljfp>ZbS=tTlcfALbr$g~BlC@XY-AqGd06ykl#S#>&moRu-x8@~i61d_jg2&+2(Ck2m$<Bv((-(b)G|_;oZwWJMJkf7Nc*y^ce7q}17gu~2T(g-xgvFK;smx)mbffqNT9A@B$j2tNyM?lqH7pQX1NCI1*cIb6Q>c^r%oZRPu!5YE^%FsQA7Hz$=}taT^>$kIg!6fAuqqFMoA<mIF4n}RUA1ID_@12{H{8=>g4mVi{&cBvVX|iD?CCidkEP#lrs`-q!gt%xl(Mi3UM^c@x=A0V~Ar|E|IU?h`MS%T$E+ek;F0lT~UhQBGggDMTjF9Q*p*sh5ai|E&o0+oH(4kNHO-SIQe3flH^O$e;$rtIh;O&sY8fG3b4KaedS@P3!)Ao7VQu}<LI8SH>D>z(S3+V8W~_@n30!>M-umCxi8DlQV%DVSPHQpC5fd!vRB<?WF_$-NB6EPiSxKK<VF8XEc%L(U&&t~C-^eUv7C#OscYxM@hsOSu1YLAB}n(SFBs|XD3<+hcXB<5yOZxs-I`dmoUb3sSI)ztTNx?n=sOfa9qQ=2R)lq-lrTr%%TQ{udDPLpdk1QnBiaxru-u$>?TAG;qwYxDjJPFr7vh%0{~{KhO6?}D#ky4bX-O`D<viS+<?VddUr~RX5AR`F^eN)+jT|&`%*X|n1z%)24~v$)l<Wa-kQ052b~mVnf6d6hjjW<xODt=btXZR}#}bcac^vgTV$pMmMUN+5PGA2;J(_rokqyKfXeZcfWDV=ruukv<BTHDngmr@bj;^=g8QINp9u|FsSoAln-%THLSzf}rHLP1hF3)ZPZAHI9{Dq_I_;Tv`#GkSJ1+nOTlx#=W`F+%R^?QvRCO(|c{xE+ddOxw~)x@Hg=EJYDEP4|07mRB!^#<a-#NSY_A^yn7Hb?g{+c>s@UpF$@$O`HY^Wj%newA^2$hIYh1=JIXx3P`)sTUK!Py8nJTf{5qZx{6e;%(GlQ-4Q%n9uqE@d1w6e&W^CALbj!rF<Ss8KYo%f9EjnIphV)SxoW|x2P`==dvvIa*oR-&Sm*G>M&vv!M{+;SyZrSIfI@fK1W{kY2sgq1H=LP6MfeC$NyQjFZxH~nU0=CrVxvMoAMU9xA+WZvR#SiDD_EVISa~}u>kcwVi))1<*8$c8*mSsMqQV<hLI#ARf05UQ-ioH_vxjmYY<0pJ-XwlE>4`xwW>bXv-)hKE^!)lBjRM%#Zo5{%XvrEPw^}I4si<Gtxg?5+^JnqfvDjB>A!0H^XHXK#RLCw!~W%i>AC#BY-@b|oviEBE>zY(vxzBy#Li0D^*jFonFr%W'

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
