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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/01fe14f50de443e4b11ad1fe033df666/part_007.stl', 'relative_path': '01fe14f50de443e4b11ad1fe033df666/part_007.stl', 'source_sha256': 'c08521ea04dbda9a5fad17c47395fc62a61d6177bef6e20af71ef0583ca026f6', 'input_faces': 744, 'input_vertices': 437, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.36773696541786194, -0.29345273971557617, -0.2801857888698578], [0.4114905297756195, -0.20207752287387848, 0.2809242904186249]]}
GEOMETRY_BASE85 = 'c$}r22ecGLzQ(%=K1HHn4h$j-C?FZcG%5;+C<asvID`wL#0!GtK_nwcQj#!aP=bi7u7b=3bKqVuqU$=lx`tJBcg?P@+y7g?f4}bk%sc0u_pYbT_x1PH?W%8XRZ-K`$L?J#R;uH<pL$-ycR%TTcVo|!Qq`;DjVdZ0Ik0chh-O2Ejq$yj<+}VRF1)fwx9&ZCZ<IH#VZWjgeTy4*NHjdJfBS|_5)JzgEgo6id&q4=i~ALcep&B9BZ>lj#O=L@6$RIgTDNM~B+;sIlf;C?|M90v(1naQ^PLN&FJHZQa8Cd^e`(pCh@L&{^wf6?vQa&Qo;cL9{e=-dt@U5ul8x#~bnmP6WidVTO<AFKRZp9CJ*~ep-fni4)03uM)x&nro$va2z<;e=uRy!#N%V}ii=Hc^{@t{z_d!o+yLun=+~Ih;*&i#vTBzMLx@|Y1^@qgU&HmtY+in_N+f8?WJ@)tY9>4Rzo&tJy)tu6(u7CGL&-Qx@>FLwo-yPL;JY*kUG_#PNeCznx(f;T-@!qKZY#}|>;+nltJsdxGZzwIOXYM`_)l-ZUn>QS9Ca>yAlQ)5$F?n?ydRyXoL;cNo-W=mFcQBqe9JeN~>bcSJycr$O<n=yz!|9CM+`j(hc~#eOo=QJZ8r5~2dt;jIjp_;X>_=bij_Nx8lN-OEQAp43A2Tb~AFaRe^k<{G&X;WW&U>S}&X>fEkCsOD1bSxsh*;hn^TOuU`DOF!{IYpddLNTl=Uv+54Rw<@r}NR|)p=_3>O8f1Q|OvEIr@8d|4xTrDenjChUyt~T{l!uYW=}(-3ae<nbURM2=9Zg>qfHZsCUcrF1RnYKCAAb>-wyEc0TnVp<VP0x~|Wvr_ptN4%=<jDz-kWo@?1EwmygVLHEYS+fAS+OuM-jtzzqQ>Vu=p_0*<*vCmoc1iH4XdUhlF0M~AKA9QUumum2C^zWFPd{+6mwR-ZNBg&$>{(ZCGK3Njg)98sW-+wl$>)$<DG<R}AeNL?@(f)YospU2H#QMp2$h>x-B&zE;Nero7R!GkbZeKob6P4P;#!qH{qCBtFy(5n)i|XOH`aDxoNKaL$vL~wRcuQ|NHC<3Y^O?yP7SJ;TI_!z+IzCe+PnSgXaD0AyT3JE;vnKJpjN7cui=Hrf!|`nLX3^6oZ#d4k#q)-G<9Obr-pAzCd66`E!+G&dJa4FfO5XA9V)G^0xUS1<^z_!+Wl>${QL^KzlBn*Xr@B?!6V=1{Rq^1YLV9-Mw8_!_q|v=!lY3(QL{E)+(v9aeDW`Ay;N|FiS3QBQ^Ii4qR;MTXxcMI52R)qcdLMLMXL7HOi?{pTm#$r-Cu&?8)3rb8_dApn(zB<%y(g+`KT`|Gj3}gMKAbcv)*sFFX{Br--P?IxNmLJW{d{#<Aw8S>sa*GVrQP3`eP-(ZuiU@aMo-R}u|KNoKGPd~-o8S5_UD7oMD_6d$TxpmR8XI>WpT7Wy3b6fD()(zdzW6nFRJT4Gudy={z7_g^UnvOy6!)1UfpM=OkUL!Ca>;4b0)9uGczV{s85gQ)%|D6<PG<k9piabPnf*A|J1yR)>E9W`^FxhxOD(s_n+wsOZP|h@O##Zru(A0?mts2{{Bo<*L`NX<A6nl^i;*Ri(~!K{pS^D?278T|MW^P-51q$|CwpMV}DfF{bzQ_KVx}y|7r8;{?q0Szu%d>y8ld@yt>cKn7pbdP2O<-Y4Ym+)8^Ivr_HPTPtBViyT*;H&g>JaOmp9-&~@LE{^o|#sIL2#T;;)gqk6b+d1d(SsIL2y^j#m$DWoTt_L&>&kM3K>tlu5g!+pyK)AmMn-Jc|19bOvM)4HGeenENO)cKoSyX-fzUyUfwt9rPfDV<On)pdW8EbY9vke+S(^zNvx`;g>OD`pkaz1DT-Tv$NQeR6nrRM&k=*6+PHs)zfN3J;VP)Zb6X^Rhq5*}S@+F?n_0k}`R9-;y(Vb$^nr63?r8x@A1C?pv}ZukKqiCU3Yu@#A^3s=w#*CTebW?Xus<b}4rA7hU%)nUf}$Ms?k{BtE=kZ&VNWEyq8%JF4scBza`FS%vg;v$EN-{%HO2-|mj;x^KxnajVPQe_w2$kXl{O{k^Q-rdC;0*L{LFZ%s*5_jLd8<Pm$KdbrQ2+&*1UZ{+rws;6~daZ0;Av3{!Fe^*IV*L^~wp4(?yJ^gf3_x-o>*Rg+R!|#dcc7K%}b@HJ?pHH67=cBs)d{noekLvdG$<z6KRJWf`*dO!xg#9s}kJa__@m_CpsL*&;-HvC~?RZw*j%U^Fc(%HZ=deF!Jcs=;<2k#kZMkmOTh;A)tGZopt*+~>>UO=gx~{iY*Y#F)yWWQVH|uBEf3tq7Zr9JSU9*0wZr4w%>-rh?$E=@Wf6V$B_Q$NBVSmi}neKC*`<(5506lL%fS$J>K+oF`py%xej2`X>v_Ez~p#8D?0qu|74`_ePejvB$W>??rZ&kPZTh;CUR&~3-Ro(7yt*-mqus>#h8}`TSZ^QnW{cYGEv%d}7HTzrD?fy1w*X(aqxBJ_$U9-QndeY>z``fTTW`7&@$Lw#z{+Ru(SFe{FKlb~n(Zlbj=y~5yjUIkKMbG<wYIXg7ik|oV)ac>&Q}n#=r$!IIpQ7h|Kh^s7`>D|rCU4&NQ~liR_fxA+kLS(%eyX3R{eEingvo2apC)Vdjs3f?&s(gn&s$Wt&s(gn&s$Wt&s(gn&s)NF&GQzk>+_bdUGu!f>iWDT(P3gdFVD49x6idyx6if0`<Uli;eG6Lt<=WYenX!JT3w$9s&1bLs&1bLs&1bLT3w$9s&1bLhW#<m1HD6=<NFPs-&$RtSF3KHS6f}5SF3KHSLf+GueQ2AuU6eYuMYcZo<CbXVft^MKZos_=g+F!=g)b1<9Pq=^XITX=J|8jAM^Y<Pv`k_dh=7U{f3^WSY6LkRJZ3Ts@wAv)$Msop3ZrS>h?S(?2kE53HxKtQ>?D%DcRo+#^#aEYt`-fl<M|;D!h+9pBnvEY@F+PpX&C!Pj!3Vr@B4w3-52v^;Ea#daB!Vz3@KfTra$jIoHb-eHI%JVY}$|{8V*&ej47#oS%mGG3Te=4^`eP*X_AHdfvG_dfvG_dfvG_dfvIb(Zh3j?T<Z|*Z$aZdF_uqm)HK-b9rsop39@>oy%*x_FNu4?_6Hnwde9yH+l2U<+VTdTweQQ&*im0=3G8Ar&hUc->b2@zE`8VeXqvq`d*Fd_PrXb>w7h-+xKd$uJ6^TZr`iP(|ONCb^BgTSl_%?WA&uTYu~F0KR5GUO`iT{Jg<GPCj30jdo@<q_iDn=)4W%cTHP%+Ps8^C(CvF-s@wO(!uy!_#KQZS_rz4U?}>%?G4F|~Zr>9N?_=H*3-4pz6HEQEM{L~c`mefu4^Vac9-!*>JwVm%bG%SD?*UppZQ8Z(0fzlF?*Ur9yxs1xw>CF?{K14&{h(@4j`Hew{d-4V*%VQJ6brwyIk5Hr>XprQty}+pU)g*q=)<!?xfARSzY~5rcq#mH_#m(kd=UI)a1T5gl-fbL5j+=uLr^;4cfb?=cu*e3e;7}A72oqt^PMmFFm;OpKHGQxZ0ZQVTk81Ee;7}A|DeplpMxj-=%CcauZt)A_dy$vc+MBBOWhmE@_X<Rxa6pgCfEWlIhx})$E!`o41NZ$0~za(Q!qna$uXInlc{qWIo6YNJ>G0`+=G7)-os=(7XMhhIb>W-PQhcTdoEcX0awGTGbUPqgW$~>L)F2{;gaJe{Fm^WlhGrm;7in%95<8mX6n=-#|Uzcz?)2tTkvneTTezG-^aU$j4zW@(5G$-vaAMQh94D_N<nD|o(lh6P)@-=1yA?`L79U;2Typ*pp8bp^9AQncU8a_`_5lX9pR4$WxMbE?Rdg7au56m@PxMtN@M)Sc)}kH+PKeizF=eOHYCe~;C=8bgCgtQNbq|2h@kYq?|~=0EGUoRKZYm#tDqd|J74fI>UIfuU*GwHN5bz2aJ29I(bN%sc~JWK&hLjO{A>BV@sGk2ejw0ydd}ZTov+CtSq^|Z;UmGx6yb-!ui=N_e+8wTzj7`7T-v?^elGkXunYVmcn45&ci>w1$9!&O@Q>l|f+OJX!qecD@HG5xa3p*r*@UO$?-7&+@Qz#yo)O`<aeW4S5x5J!2;SUx_&r>T@Q1*weaEE;-w6(Z?}V=euYs?Gw*Y_e9B%<%>^a;GUkq;mrr<Af{TuiL{5SYb+)vuLi6Xoh90D(f_XMwo_k{nOtdjZP6yYy`yWlUt2ZFc32g1969pPQzcYrDQ9q<>y-Ef(g$9Qgx3!Vd)dD$MnJ)Urxmz(f6;R%;{c?$DZa1(W9Ue09R&ZLg;&CJ=+@R?l8yqtwT3vV=Y_Eh{+@r28~-0V4D@KowvPnMnFX1L_2h9-D6TyiwSZ-#da8CT-3#A{E+W5_AElDd*(5;-SP=M-|RBj-B2ndC_0r|~wEu{M5fyjf&iMNYxm)IEnRo55A^YK)1q!8_p17(>;-F7TC%xn|%%{ahHcD;cXVz$Y=Lj{*Np-F3`?NnlTSnmMx$EQU)CnPX}2ChD$YoQnS<^HBKNWLX8i2$%J!qUYwa;K^`VmrlYz2~W7JOSAB2;R%;@>36>K1!qxL)}@8M^A}R5IqT9k-}&3{9%5Zugue)HC+ku}{DyeKWnG%>IbX0LbsLanF*qCEEhrZRr5L;pK0GMb;$Mp=e1A|L#eWn}_?JOB!gs#lqtxx~JFk=P_z_$W3~-e1^ig=iI|rqY@BBV^!v72Ju;+Lmu1kaK9iG#7;2kD|WGMxAz>C326yfiHhvDzQKLVwlkGK|o4s8#Fp94>Vo#07$dr)$>=UVt*_}uox{{nv-91edQJ`wB&p9mif7Q>6lCcKw?CPAqWzl3YS(<A&=u1|+A0H200fH(6UehZf(d^vcP@3<7<kAZ{XkHJ@f-Qg?XXM^8)j-L%*=sA1_z7Sp?>;-?G>tDg|;J?Ce<bKk|jTGU-!NKt1@EgFZ;5Wd3A**Emg(Cbp@M-vS@B!eh@B#47;3e?R@Y}&&@Y~_fgU`TaUe;oa3$}yHylji#7Eid$%MJJ&@Px~}Jc)TLxPiJdFQ+qar&H$$=H({l?Iyh5%*z@0Gw?<+e^16g8Be&(%Z;A%1y82#b!6EAZiGvYs%U~u;gX{XeiOV}WL$y20<SF@Ym!rN1$8CI1aeNG&Pn80OU|`;)5$Rre<I!{GS<Scg*StY50O)_7IoW^Wh3|yyeea&DR?`)31g@#*crZpG1mkf0I$iIUBOs=4nBb~T@(C;x@(yO6Tlnb6PYt>!QpVpA#-dZcq4TmVw{TqJo8X^Q?fh+J`b1msDkI_vfznuS(i@0KLJm;tV=WSXW$8!b?FS>`GPa3E9=sH-}&>Y(~Na#tMB}+c*|Lr7T_<ydyI9d0e%BK;j%8x^qeo)fV%a`vJjjJzal8-2W1#|4SZ-&uExI_Pxxy=*@nLjPx#-0QptC|;5O=B8t~hE=L=SX-yYyyzVq**j_}KZlJcFO!V~^Q@H>_9E8_`&J<zv%&fiX*FUTNSUI(|shk+9)!rubFfWHO*Gbru+nQP(gX!~|}JNSj*rSJ>kZ9&Q1mTTcTKDXE4Iry94Q23kh@!%Ek@$gaLF!(UC3BM&MM|kqs*71wE7EDC=&0Hto_k&Nt?}s<>9sUz8Mfg&%oA0<3;XA-V@E!1F;Fa)Y@TTB5p5sm7^F4=ufX|2518;%v<N9CVH}HSKujhW!#`P58!@xoCVelScH+T>D&t#R%KU0M71)qZNg%^Q0!;9dZz>DFX;Qhf{;QitIz(2rcUe@&77#C~<mwDM5zcrq4nV0ME*Wn45d3gf!R&X74WnNBY-cF^C@QuvbyWmr~mU%f1eHz|f%-Iw1Ps9^0^K!lCe8Cf`dktB(gX`gv<7hO&v*42BO#CzPYLamo{xZDQWUNk3!DZBy9OKA2jyflhV+}di;7ujRc>M8r8_8G$zXskkGA<{lU=8ZFA<KGjIs9nG#93f}_?e8Mqrpz_WsJEq!6JBd#_Tf2>R$Lb#&mV?XX>tD4vYhPz{fLZ)_}v{l0)X$c<_4aE@zyIzmIt+{4BC82lv5cJqqmdxh!}*JQ0-R@Q=e2F6+`X{AqZ?WnDVmcfQ~>>dLw_&v*Vj>Ij#0X^ZdtEqKCZUAiCtemvo_F4f1ck0)H#rRkpY1?y9{9$Dst)8So%a$Zn|fZgGPgK`!ARd~W*3Cb4yEqKB|3rYpw`GQ-hdr81=^_?$R0X`tWk-qasQb%~lp!D*c-wRLp=fUq(#IJ}a{MA6;>N$Tabv`G9WO)_b3LgTFqX>Tk{2cxU{6kRM`H*YjZD@M{ybb&U@Dlh1@YbN@Zq2puKk>P}0{;{IAUGI)5Iz>{3Lgu<3mgI;LN?(y1*LLO>cTJLTJW?8@5%LP@VVd<@VW3aeTRRCOA-Dc*wuGjittClJK>MQmw;Emm%z^g|KT})7JQ!P@JaYQcwO)&cnQ}(f&YO21iy~^NgLNugbxMpgb#&Z3wDKH3;&U<lKDr9@GSTQJPYp&_JsF^Uj|+TzYN|Fyb0b9UIIP|mw8!(F)r8&F7vV_eoH*zGB4NQufY>8^YS?6t>7B!%DkMyyq!Xw3e3w5%-aokw=ys9#lIJCBy;w7{NwS2%e-9cIbZO2>UJl~R&Xs`a#TSRYz&tijqn@c)ga>%{3UoT$yk+~f=j3?ImVE440Vnp$7*t}#+yQpvG`;0HjuFzel@&%$+(o9g4L+oiY#lvrSK|@iN;_*cq7J874S0n62@F3urItSV|EE+H47iZn63)`NZr-Ufid8<@UhI9)!<OL<d8Ww7QBwSOBtu)3;qOeOqQi!30&4A`Kb#Y3zv1N4!*t$B3#y`d-3nZ6E5pg!gs#lz0{R;=|122_fbc<tV@sh&VK|?xU5Ta@#o?RmvyNgemy+lvMx>aoG)09x^>Ai51b005|j_*??4fL4@LNU6ycvxgrDcTBK%_C72)Umt_c5>BK&=D3S7>g|LD2%X(__x4Eq7NoO5r7%USqhxSW?ag3FnD_pW}0Iu-w?|E1c0|HxT{7yBQq+24%6))W2BCxUy0FZp!uT3Pm8UWMR4c^G`PJo)wh10f7MjQ'

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
