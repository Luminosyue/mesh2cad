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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/144bf300ef43437096e4be61f4575bab/part_006.stl', 'relative_path': '144bf300ef43437096e4be61f4575bab/part_006.stl', 'source_sha256': 'b3c7962d90eac503d108567b48a235e84a03fcb4319676269b9bcc61cc021c0e', 'input_faces': 451, 'input_vertices': 318, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07342582941055298, -0.04459044337272644, 0.3224863111972809], [0.04196717590093613, 0.08030688762664795, 0.4149021506309509]]}
GEOMETRY_BASE85 = 'c$}r12UJzZyTuQ7u!0a#EZ2x223xQ<E=ENZ#n=nzwV>D)5d}q$6|kX*A_{u#y~P$=JR*N%EQ!W$EZ10KjlD&q@65NiFaF<pZ>_i9bFFXf-`&jp&di)Sb7tl)+qTM`$6dp}@>*EtwX<!@YMP2dn!6So867jAPvpp|Lx;yXX~o1>|32xwHXU2H?dqh(YGZx-Mvm+g?OWgC+pu3<Uw?~lzhTia(Y=QD92VU-Qu)n$4IUY3`Xi%y4UaTGR|=?6*WVK0=Wj`{{2%|hs5&^G`0k+6yDnjYrZ_roI;YffvFkSRy<>){&qi6V^GdCE7Ht*ZuE#00zkDv`9dCQXKe?cvQpe++;@fg;ThwQLZI{WC_dyTIqosep8F^X_l044s#kXX)gulpdn&|bf#n+ElgFmCze9^R$C|^5mllp92@47~=ms#+F<c~_-DCM5bTrA}(43hG;QwbZSJ{z5vtIzhk1yDZFvR?d<tVFrq>~F+(EIhSN@>FX!MB4Ryq_j(~^p*I!K5mZueOf`u?|9d5t@u|PY>{#yttF3srHuI6ujA%OedcbJJoftc)<}6<uOy|mGY`?vOFF@?(lS~4KVRO9qSIclR=)M{S?LG+qa)}C{WtM7OWP=EPxT~RHzz`TW5FD0ukrDM<k5V4t&;L@hV&PIagg}7KtJ(~fNe`8@AX0AJ1*~7DfRi#Wu}z>Wvuwt(G%cTA3IU{r_5rxu8}kj{;%~jq?|{6ls{Tud~HSjXld`FC@F7QRRw<8C8Ol}e-)7O_D#8w$CiJkw5Qp4)H8g`3MpTDVMqD=>L%{j%YpDy5097Y?Olm}`>wzE`oPum<nITjN_p$>?&4c=7u+g&B4begbr<9*o-tbL)3Y$@^IIYK_kK<g|A~|MmetP4pRSD)?VEu1p2&yt`yaHG>%5sIzJ5A<x!lKM(evec4S$5+0=^!1+%BI3!ZEJuv=CoQ$du>K+UTRy-&VVx_(sFv^^(U?6aBN^3%<{eG^vMk3i9tQh5T-37mA-S?2>4vv-pmbSQ%H2qqWhW-#=X@c^Vv)ac-Q?hQIxw_}bky6Q%vbFQcAIcEKN<G#TULD6Z=kfIRzKufX#>0N1Uu#V+;nkClF~-gt=l=kg-)wT`!Eie?N!Kc~%u-y&;(jN|jy(a!~@A&(I(&zH5_@3@Z>qv4nAD8AjfBKqe+cjPJCXp`g_I7`}PpSWPD)N}jIbX*_f&`1gqUz@lx8RPOA>QmH9d_BQ4Mf`-SXxBkk@$Hch7s~f49mPCTtO)Wv_mc6impF_3U0N*>zw&`uxK9O<=dFkM_8aM`QvPlPp6kl{GNt^QCZd)d-@!kThR@y;7sxodv>N^IJ`&|`ollj|ZIdOxHXYyBXCIs<*Xxu^e9Is8P`;u?o_A}+UG#JI^~KUZdzMd?zYqV2`Q*mEMUtmbj^xpuU64mxFTU1fbi91uH=p>%X&3R0eb3V5@8NDJKW$ise13CwwDf10Z_p2uI*4x!8!O}7G8XfIWnGZ?x=SV8XIli?`~0o+yM08U`1bV|F)z8?7vK6rN4c&sc{2K8+f|hBc1`97>$-OEa~6wl8RIJBU;k+p>ffRu%9lAQ*SF4IA-+S;hx@J9jun4qWB9e6VLT<>X(n31AMF}_L3~@M8@LZOFs>X0PKvKv3oVj<_+bI+laPZv9S)6=cK+pwew!R6zI92I^sDvbRPps9;V571bR*HQHt?Tz7T=ydSmr(B`8&*qlN!T6xEcMk{&&=~_$?Vv#-AyxrGBk)Fm8j+!N0R%t$g-u3BTu0;#)3M%96iN!aQS7-Xp$VZt)cP`-c&ze`=Wc+BKKq^7lIEf9s?5G9Ots#bN%_wxXWh?BW~aJZFn0UPgJxpBPWmjRa|@?=;*m=O5+1+RE0#I0;EXKe%iVU*C}vqttO>u=uuL65%)e2ID>aDe}04;{6da9rJC;JsAH}ljZr;;<I{4`G?bS-*-+B-|Fr!?^XMdG?Z@?Exu*aJLw;N>p|3~XdC#?=FXMx<>bFC?OIX?&%b-pc&X>EG3d`J6Q!JSvpMGVtX-&o+3w=odsfDK=G6@Nhl1g+8YS-~>ny%^+^dMMcbT?Mt{08>g?0B$8Ta;MGh|#C7u->w_iMy=EINVtek;fG`-WH#RhrZj{ThpQ-AzjoKeB?XM{LRMaNVTw;u{NJ$~sNInt<~AgT%KM3|=Mu_-G>f-`@k}5A2^VI{HVH-*QLBfp++@y!W+UeX&mS?KVsNJ*gAK_uGbg+FOaQ8;xZivyH-g)=0>Y_f5f6nXl~8Zdi})J2OM>%jwnfoEib1m+}0?i?0<4ka25F#(mc^>WObV{)3E1OILr4+XrsqTRYXlx}aS)>ff^<@|;<Mbx`6h%;zsROFOlQb|~L;A?kmA68yXyQP1P4=%4$ulf_Rti}m2baE!N0cVvC3FL9Y9dh;Bv`{zaR9s6A|?+$N_c3nFqzTq-Z`a=)9gX`|e5#Ji~8t<zk1u-51?Z_WANv>;8oQd({91cILoZL4@a9$~|1$IaNL4z@`Pi}!cSrx>$=jns_pl~(ujnu*@|1eUX7t8ia$TRp(qU3#C8S~tMV3co|EWUMdQ9Q5NKJa^7!M<W)DXc5qxIVF76koqrUgihmhK_mcWet>%>xy}0Xg&1Lgp%Uhdf&!8`9~Z0Pl_SW%b~bmhca<rt`?ASW{k+j^Iok6+I#!H%!B&wIIKf&p2U4|y)C}>+da(dRl1<P+kO+@+T^PAo8v<`{QSGbw|(4+b=*^5<oRML%2(HA9d0{v0`*xqTzq3r4Cd*0<TqaViErQCQ=V(vX>a7Y)q1kz35!5K_;f^j4+X#<aTE7(WhC+(_Y+^MTXm>>cDjz|qVs7Pe>M&K61`Sa^z-wh7?+KQjFIo{L_Mwfwuo<ZbdmM2z1O!`M};N8?;D13;qwmlyf7H~Z+XalcNA%keon6ezfwKSd#etiAD(&Rx{l(qf6<S=K|MEmh_AiLgXgtzN%V7i9{6nzW1ikn2fp!Pg7}MPApha{sLv1w{G>W~@9g38mHGtp_`v|IA5J_%`NK!VH{P6=b)uy+#+5dxsrXv?vdFWnKK#Tu>_eWu!n*Q)81iqpDf<vDW-p%8y|};n+Jt!d{-v*EA7Old9PQ0JKzvJdCf+l_80VTtkoa2ZY<ZrHj9kd$o)3QGI`V$hHcUtP0XdRa^DHX;VC=xUS}(mze8=*G*k45VL!K^);@f(;VLf<g7V?Z5iuw(1A@iIyyCVEYec%rdm3kT_+9S`LK;*B!b{_KBP~NF1>ND=6F70cF_o?1$tnBM7Jyu{o@oA5F@<OQij&teQ&kaw+eL45Dtmm}%Ph`Jr9fJ8#>ore&Bl|YW$8AEM_x;7!2d$L%zIEql_}#`~-@Cmk?#rACsAuH65#nFojrHaZykE3-AMsw9HejQSSNjp<DU>3<_F?u8@e94db72IE?}%-R^-|AbsOQj!!zBNiQ0ZrTiLS_BDqVa%;$FJ6)A1L|`}+(Qze#V|uUUs}f*=2Op!na;+AP=g%?p3bG4YMn;aGq62u1!~wFiiwo>%5EOYRW(xt>I!pTniS#)f9_XSVJypYJr6_r4MJEAqcO*<0#;FiqwqOW1m}x9=?Rbsx-oy3atA-*Me0c{)_Y{F%=FEObnKEx84rqceBVpWnwth(GHBp2rTpC||t<{6WQJec`C^3-VjXwUh5R--3Cr^#S;E?gxuLD2(+*9qbD<&n7KJbLPcLyGoCwe=ro~Z%cg~8HG@vm<F9iqp;uA7j{PZV#UMdeynRC<Hs6W0DkHH5pw@3-^2dq?S1%doowP?8;|lghoIkH6pIv{5)_ZTT(`XO?-wZJZxZ%@nRe7Cs;l_g?g-46%R*2-&wY6wEU|xKo%_@V-#ZQa^CQ2@b@idkkmpYEfl}V$iu0>zH`M1uY4NR%-^g_xyV;-insWYVaW9E|*~atmfASn5I(hF{$v?dg{I_ZFPtL^t>{d3ed(w!Oe&7DJyuYkr*Kl2*4KZ?EzX6yB=A^)Pycb_<`8UQxDeND$;xVH{lNw5XM`j=7Ke|`$tG=we?ANTTTBAN&=gB@+pPwrGZbxdGtV^}<0&(KIJ(l^?G5aL)d$bYXT7MJvQ+hY#f3Z+}ZGZ>vOM#x;4;H}vTmGHAH!Ve6;a@2wz8-%Z^)J`~dCK>J-}x2JbIxR-{KSlSJa1>PzFUj+yteWHeD7Gy1GTW9)oT3+Ke)WC9~{}v@b6q1EBW_5$3E}n68P`G7$<&2l)Mj(h_|TEeJ7mLSr1?znWq8DpLCY>x}MVq=YDrX;aBMof9H1Tf4$yWoF{i2g7tmqYMEDz`nQmOa0?ydcOlNP+n>aG@7O^2xev&BwWWT3%=5WUz#kot_u#{>xbE#xIp@;O&5-w=H8={_z1UNHYmzSeCcQ>H@=rNFN%UUrRd~*A@Pj<$TueLP5bOPt8{pSW#Ch4IrE+d;skII7&Ehx2w|6;}hWfOFf4#yK$@BO%)}K?yz~3GKf9_2gr@BuJ&d;M;z%SHukc`7CkI_FvkBM(>RbI}|wa8+qPjT0&qNmr%zR=OBApC*V#J9iei}R2lJdkHnWATm6hchMrkwIKXU7m`5+J<%DoNXxop`4r(X^oG|e6P>v`}gAlIe#~@nxfy5W8v@o3Fq<!p2+>NdT)oHRwYTa;Xv$9yA{WCl(P|j<1;vq9XAH$r)-1oT|m~uT2DXR_qf1hjIZT5Zz$Fi`^U9I;P-iuCGEQO2+!}H2k=LZm2qc;EJyzo`2hd*J88Eya0afMkTYG%HSCY|wbyLaGv90R_36R#{?%fepx?%}lXExi!FHJktj%j9|Di+T>%V5=cY$2{kf;4-IXBcAWMjYLIs@ZjSH^7le(SzCp9^k;@!-5(eEnKCS@&v%9>5>`82&eBao<`m!gYVBCFh&kjuaV>#+o>^E33WudeO&nKW$5J-mZQ53(6O}DCbVPZ3O%0z4+E&&*Jxv^3PEJjrDMD>v|jeiTG5U*DW3_zR~op>}&PVQt;oDn~Uo_#CWNPdEUAp2!7U8JlDQ`(GTNiiElieDD5?>UOFqEtr;kv>psp6ZhwnB4fcs|E!TB}w5wlf<OzeX#eI-*WJw){^3hdge%Jo^UCxm#mGK-|OIUH<`oc@<skwP!{EQ2lCwlO-JYSae!!Vy{HE~|w^q8EpX}gZ0-_B;hk9#4{sXgN&@}GYxzSiTEyl)+Ul|lcvjaeY=JKt-W)IW3q%71r3e68{;nYZj+uA^PeTVnimaFy|98@?I-Uw>d-7@SMyXZsMF)ZcnxmHd8S1o}&UV?EYU*6@n*{xiCyif{em9`0}5HSjCV#qU9rPa*&8OZa{6kb!mMi6-cupZm)^V(ndB)|uMhcTqmEpZqRm4G59-uzkT|^xL5^;%iHXE|u#Pe~a>G0%YH4goR5#89rH(-*9UpzBa8j&VOblqFuXAqx_a_IQMe(NBP@-p#0oscz#!&m+_;mDT($M-;ViVX%jq0BfP}dV!Y({DeZVX@~7mM-{JJrcV+&!2NgzpgI2D<b9`l})W_eC<Kzy0FR8W;8de48RNs%o{OHwO-lz7g6=wt6{@bt7K?kO9UFl)I!Od{i+_iqaKKm(Jnd;vs{qKK@9#Hdt^;2}sS~dQ^KSjrxbr@?#I79I;>UeUj8JT8Oq1GgqqL!i7Bp21x&+z6JkeZvEn_Z+hkES{YWs8!1s4nCKW{fnWBegoYI{)60p|}>+h3sZVelrTIF>Xe%8I>4{yHI<RyO0N&v7eev?M?PJD_+lx24)mAqnsK3)H-B;a&3m<`V7U5SjOFqXBzVOlMnFP@2Gdk<(;4!^$z)KC;aUzsz&Z);$SoSQFXG?Y2=C2DGbHQ)M?~o@=S)}Sq#NVRGpkep2|?1XvQS!XsS-uS-;T?#l5JV$i2v|8H!sn6o)btM^O8bBgoO8wK<xhc!C)jW{fdoF?9lYG1<;goJE~Tp2)t-Vkln5P`sR)OipG$E@voS!cd$}okdP3&!;Al=ac7Br;_KAQyGd=sEOoH_e1e&>Pj=_P~)j7<P?^VXDE)MjwVNuBdNW}k>vK&*5uZ_f9)BHTTw&Ft;pS|5#(;<{?ur4H1AD+>KL+(I+QwwJd~V3%^)X`hf~wYov9<JY2*>)BMij`HG^!BcT*RWcazss?d0|39Sp@Asaa&D%g7ta+Zc*BP?wXHE+KCqf5%X~otjSGPToSDPgc5+yoJ1#p?DKR@j7Y>`O}zN$56bMx{|z>yhi(HT&`g#Udm8Bn;K7^O&&*$B99{vU?}d%P~4RoNmkmPth5!mE4dl98(C=+ax-!TGxC~I%nVO62Aa{rjJ^!TA=KLB5OO`LKe-;c9K)YERTMX)pc$@I4{C9;2e|@6u@}{o?5n9|i@BtydXc?Y=1ZzS`Ac#QYHe~2a${->a$|B^>OgW^@(?rTQKwS}lBbg=Q~Q#~Q-@Lel82GQsUhTs)JD`0atQmk5kv7;)N<sn$Zk|mvM2Aa8$)q^hT?qGyySf3TnxpZ{wd}wTsRNalkCa+nunp-S^MYSJ2Mo!P)m}Fm{CCcXZ@qNG(+(hR2Q-fzpGd+Yb%>kjiLBkGy0ejV@40^x8xq=Kx$=jAh|9>aYd>-*`3#{$WZJ@ElKtxm!P_mOOVSl6nj%W$Vw}ay~*{dP001hZK&PIO8b*Py;s^W6nCfgA$KQtU?^@*?LqFrerZmvOKwhXK&?ow$o4m2C=M{=8#98;urd_ap$3rakgHPt$bRg*s?@UNs^qV!-ehm~(bo*cVbnI{Hf(<wwF9{W+ZM)9+>Y9S+<@(A$57mqY9(9Qo~G2Q<f^PwQ)(FbkQom(tl_iCZ_IFYg1+VFhvXVg_?r(^d5ZU%y3dS*)Eu(%57SfnFY>=wMsZcH%~ft+GxC{{n|f0NEB%G+%fI_E6uVGW85h<oAM5Ey^=0@lcL4uZ#f)m?Po4|?D&%4e#piepbuGnTn*4<sMX347st!+CkB8*9?DHe+(<Ag1zc<6fEc?OK;-(fg!^w;V=I3K(%rN7;88^(huA$s@e(ySc#iz|UYQ{x|;#JgL<fYUV)LrBn?4PQi^<7nlANxt|tr~J)Ri0ee33b@XI-VyVW9(%8XOLs5*U6vS6U*=Z&h{wH<pjP#eork*R-xE~o)_7JT-FJFqWa=jhT?0~yiVY2<Wf#hH?kXZl%jfl=Bsj<{GQ5{$(*amsy?}RAC;>1IPtUMdu-!*@;&k;>M`;q@(<JnWTo@SY8-lU40>`LDpvdFvu0doyw>17BY)bjEA?h5E<{yj3h}ezTMWe`8Hz_yFOx@+<EWd-apX_uC`uPmH<LZs*J@0ZWnX_9A0ODaO5NE1s?H7Aj&kHW48`hfL7gGI`>f9IK5NT6w(--Mg5rAYi<;Cz<eKEV)beC?rcvDqXBJA`$?BO>^P4MGBfFB-{Hj!)T_{$%pR6>S{Jj}_%s55;k*w4~K1IIGQ2aNwfD`y{a%m@MMY7Ub<ojlsKh1c>Q2d0U_z#BS-x!L|nDLVt$IZAxJwrajGFPbg$x44FUm>4hC_c$he1UqOT+*y-9y6Y6&=(q5{q3<CR~d@$QlFFWl3y|uf26)3mvMr6QeTigd9D1^Jbd1i7AEH>7onCQ7a@PiP;8+VCKqNd3$-M<GPM%5B)Jl~0z<JgRkg>N`k1Uj@m~zZ52zQ&7ue4asISNm$dAlu+sY}Id+z_~zZ?DYPgi68-~RK_fBoja9}R#0&DmzI|2!ye+bXZxE0~*vTynrLM4hZ^{{h_yu|@'

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
