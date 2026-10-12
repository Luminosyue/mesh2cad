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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8d4357a4152e421884823d3c2d3da14a/part_007.stl', 'relative_path': '8d4357a4152e421884823d3c2d3da14a/part_007.stl', 'source_sha256': 'b8fa75825d57eea05614d67a12e63dd30daa4f88f4fb65cea1d40ced749a4cec', 'input_faces': 516, 'input_vertices': 298, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.27579551935195923, -0.06509709358215332, -0.1040608286857605], [-0.07186026871204376, 0.1676371693611145, -0.009323857724666595]]}
GEOMETRY_BASE85 = 'c$}r12UHYi*T)A%v7uOE17#Hj3$bAbb&1BFh}iJ8WKmJns0i5GXaKu{V#AWPBPtfEeHAQG>?Ib0Ya?pZsIkW+-`;!wo6Ni?p7WjW<D7f$|NiFAGtWG2o|)BvE(IOSDe_lMNn3MvLztVQkd;u%DdR)JBZm(TiKsU^Y?6cG!kqr>e(Be}z6$8;po~|hcnt}O7#!}^(%|Jcw7HkJ!E5N4@W}As(cg>-9}+^meekytAvPWn8XOj4i)%G%(cIhMQ`_4x&G3KxD`u;Lal@92N2o5_hHWHoELk&&ec8pruQ{z|KllB1=3hq%Ph7Tv<0r5AJWKvm;cMP)<~ZlrF7nn2qlL$$ZQ{7!zHNNGPl)h`j~0?Qow~l0{qq6BLqD3i{Q9wbbiC1um3;nMS1wPP5h#2`NsbNAPO>+KbrtS=d<%Istwl2XQ+0$dX}yBu`%P1HJk@m$mvdsQ)HkWB@FrP&pVk4V*7EU%WrWvTBlqLFo$IMMJK(+)ZU<}e!+am6S8pyb@4bWb)k5=k^YH>Vg;(D#^+)>~lCBH)JjLaxhp(pSc=I0IFP7I`rGM(26du-&%dz-h;`=rlvV_kqEA4QzA-A*IJW2TO{%RY_n|eU%6A&jnJD&5cDXY1?&6{F{ud+(J`<9n>ez#coXZ~9`&hO6cV_7y&c%K35na_EersK_*FXHlhgs$THJen&!)j5%Qo~w+Xm?+`DC+^_$7iV!jP4&JL-np0DkJ}4wf2-e6;pWzT*#DWDrsF}M&!+oTZpZNbSsu0(zGt|^;X7qq&o>IM+nVcRF7C|zW}4|Iysb0$lWEhpTu)1UHQ`^bVy<**n5yGWt=7x<-x|;H{3^otx8i(jsmAO0y5VKfU(b@|yl^hx@X|r}-LGVRrl&}|IXpeje8XsIx2x~C{+7gFn5(18a(kJL8`)d#StY;Ua+%M$1^GILs<Fba)Zq3s4tT@$Rh1~=6K_d9jt%1T4DpkNj~vYPvG_fd@t}qa&u_;4Wxm=$@|9rWbv${Ts4e@Z>$sbh=c6SrGLGBzNs#dDrMx~^(sMI)+}vaa^`ogu1s?zAb6thcYs~dj)5mYo@e3!o9_p4~`TEwsS_%K?w_3_+wwHN>`obe$a62gNNAdhs1{s7mPU3b{JzMUO{=0RKy^lY0qhoQtuBp#8;k&%Kea&}g@6~b4NAuBQ%lZEHWeV?qD~{)5fJ=ssE79w?o>4#WI5eI)bC&tud2+uS5|VZN%iA&z|1^Bh*SWGoc!!bF?*sa$>bNyi=IK_CrR<}J3l9#IahP#X=EtxB!Ur{3!`Joiw@=5deS+D?S*0IebQ5kE9YOWCOs~FQ$2(q3AZ{L0l&^1io|VHqbn0flUqd*rd!{kp3hz>i`^B($+HM`6KX$A1XAz!9mRa3}Kb)|h%2Ca$GITut@fPArn=CHR9PsuG^Fyn-eax=$Qr^8_;j>E1^YLl13>{ZKU(EG+cYdjkZ;DX4eS+5Q*YS2Wq<_83@ccF2bw&P_6<nYFE%)nq&+gm~2LJZl{)V!TPcuIpl*r{YxyS8eeY{lo^Ddlk_A8R1;~zq{aXF!*WF06yP<Xr3+zytcBze9>8ig--xRKlK!b2Xn>a=RY9XD^{{H(iaI$m|bR_2+0ybc?k$_Y>Ixq<65c6O?cFN)-H6jyh7z9;|s19OizvW|SYaIcO}e8S_+II5Y<$6krT6H0Uc8qYZG)A15M+&+fK-qN3W3E*|iT+gnH({#MRWxii)W_O-X%9$m?+il*(<^1-GwA<-_=cb2Kgdf|<^|8$FlA+^4ySSZ=JtxaN{d}D8>mBBDI~>@!U&o`o<-V?d%j>y%B|`X>e4ba9x&t$H-0U01^*Q$@LFVf);s5C%`?Ih*^1Lb(B7F40y<E>FXJ!33-Boz*+8xY&LwJ2Neu5i%wh?}N{BG{w?axzWy#6~k4=@PN>7UHwYFZ8McSBPb;TQ6G9Z+j-kbOdwv+%Ez(}<fePc26Z2#>qV<y*ELP1N!Hi78x8{|j>6POncfzh6oEJ*eAW9XB=R@o5=)S@xfoe-=LP#da>I$1_=PO8z8#%Mk8&<Ke|J?<yP??(&MCBgTnCx!=_atA)pIlX+dQfvl5<R|$VUiO0Wj-3WP(3|%R_({!%Cq2iFuI(}kdI@jlYlw7xtD!gMVk8`y{0ojLsf}4LGCOqAR*9YS$W1^1xmzDnVisa|A`U!4I?It`YeI?iP>g!Y;@9)U%ta#Vpac=sxo$#jTWxd+fOrFE#8wq#I;_;yT87K2GrKs>l3ClRI+Mg*pZp@j<<1+hu9@nbRyOYf8C2~1NYgZmumYZ*cPtN0UYxV2DNyi&M=JBuMIcuGNO?YYq_m{eSMv9JyrEvdR+f?BBuFSe5ypH2ezV4l^JdaH7XN5OtJ(lmQXKJR7_pHU`TO(U={SBi}3%}c!$CcvqjK`<)EK~TVC*00P->K<3-gz3Y4@$}{nUC&C!ZYV{zG+FOw8M>s!e{k8z~lVqbMpQ%DoVJe!xD~b2g>-bIz+hRFFZc2jp7n@yzBiW=9n+WPvjd%1q;tP$>U9#eMk1KeftWZ7SH2KE#Ani<6if9zAGUExnB&4z0sb}WSm5I;_;@=>nz-yDC^Rb_1r$j8y!#|mHWjKa#G6q1UJs}67KTNQs(B{dj8=8k7w($T-jd-l@*@bO2)~Ksi`{dQerLF6XQW$T12?hwM^z0{meSvx$i-qN9S9}b2j_h3Ffg!r5}rykbUWv)51U8;CZCfT`B9*(qqDR*XQ-h(kEZuL$4n=p}k*Yg2MAlnXy8+GA)qH!TkN3cdR^z%PBTf`mxV!;r*TYx|ZvwH|lsFpFPZ{Wb-(;wwNOP*;am@T821CJ%dAqUs=uj5bO2vvi~pAPWYU5vJRJS#p{FB>EF5Wm9Ovy?_-(oERv?<MVhbT^7qQTP^Q-teqp5SPkI%W_qCk5!Y%1sA9X<-_q+KM+&ID$?RI7iw`ZYHdG4F43*S3V+JEN*ZcjtbgX7F2tMa%qELq0=qCPq&Ji9ozkMeSsyie4~7CwEF?8jnUrN1)w3$Ln3{io*1d-}%|;a7S|J;Q#NeR9l}<J$VD<BNZ<<I%bNd@(u=mFH1tg7CR2&pWl$?06jyTfysw@>J%RsmmhajWVP@>MS0gmX`~Jo6E}nu#v1|hNBait3E|7d|j)&cN;&Bl6<UVR>$gmUxrU`CB`JY-dSEx)G}6iuaEwBZj7!h-17{NALAiU+24MGTQ65Y{lAyz@{;CTbv$;N%%dsOWt>O7&1Rmp{t)+X{I~=yS3_d>epT$Zt<Q=}zTYhFcf;h&ojN{io6N85F5J%Ml;5(L7YpWgHvbjBQOD~mJnxj-rMMpr+qMb!{$2Lf7mmw%5|AjokuN{*4F4&(RLA%E@8j!ke9QM`aE}+R4%yGw?Xh>Ej$icT`?5aFkp29dx5v0V|F=i^ejRSfcd{+1%#|Ex9?#}$@*UuBe!^Rx%UB02OXdnc@?6Hr3&)jOu6|)U#`T;ZEzi3-Z6yC-4!4i;We0g*xSe{G`J2=7JPqr%M#l$zlyRQEobT6sb+_=4W*Njy5tey6o?YxPU-!fZuBWw>NqFsAN4We`Q46$Oz3RgCRNLjr{x<vz;g3%;S6XKBe%{*YiG_K>J8m~+gwrZ5R|dIeaXCAd%DyfvUGkHMOZjU%aXXtPuMj>kfy*&WI4=95+)2V;USn?dyu4P+l_eXw9D}<-_JPhLg@+%Pa;kjI<KN`mQFxv|KYz`=|Jb7AKAU)4SxYC#dX=ikb=TjQ@qe~coR%wYxqMwypRTfB`f2kK<~1is|E{Yc{X1->@M|wpc|7bHxm?G${lw$bbYqn~_j|+&?>v>Cr>aM}d0MX4t-|+ZS#g}_yKzyp<cE65KBU(<S!V(rB|pKH>tl?5AoJy^_hFfLLDG*uR^k1rVZN8}qsOElGiS)Ycix>t%zNcBH?<9v{aDK>!Yk~M@l!c4mie4U%+*(Cq#b7e!RxSj^~HmnKd=e6gF0UN_ivuIHbcgFnymkiLYS*18%uox6L@@DVoZ|%HlEwfGElxl{>>*XlKNbVl>K&i8R5R&WgNzg<$Qz3`2)<e>hnCZ46Br^<!bb7zOK>VP3~*V2l@Un+)2h;tRHiO^K0RQYVrJ1YV}^O<*K8z)ITm?o(mmMO1{H!u8%cg4cEsw(^+_xH@uD+I!CY9agVD!9xU}7Wj<agCj7FitXIDz@i?(0e&BUf%~>h^n^9QmS@oEFS8z_`@odR)kKw!-1BJKp$mVkXis12J9_b_8{gjN)W=(kCYra!O_>bH8d13CKXV&owFS-4V>A%T-$?Z9>Pl~0lv_nMVT<+gK59Ganq&v5RW!hS<rxG_-^0NbEy=r(wo?jWh!tLwo)6c)-@^2TCa<KlW1E+EM2LFfhee1z6zAxq1C)_Vq<8gfVS|;Nmu{ggsSkl_d`|jzDQqRE^xqMTd&GNo7^S$Kn^yU6iPs)3Y+96iT@14u*ylL=e`JQys$lPeok?}CdPk6{0X=j6c@3qXiC+`8RhBG&v4V3R`*Ln)CKJGZTLyv6vohPA^>~l}{ll(sNyMvM}@0ZG?P0S6ozTxkOrlay*O|9$0<*3=yxqq!Y<a?z0ZVcyJL#J^4)gz^)ocC$W%|Gs4tK&xsb2-Xqb@{%``G3muxx{L@uiUS=p5{xJ<^6ALxa51(m+!3AE=vA`3({^2)=R%USSEZ-zFha%@A92&Oo;FgRk<8vm*_P|0(8GtTF!2Ly}P3A&B10xm2%3^V9igJ1nJN2|NW=R;f?=SKUFqq*!2JVQ)M*=MX6!4sxZ=?Fw(W*y`ah0gsu%;3r5-lzB)8{cW4i21B|pAd=+T&uF!7Km0_gI!&ibPUje#2v@?vf6MPwH^2MQ@pdDbOe^<mvJHkkphW`wjd_`#T<)F!zfG!PP3`V*j{GW<w@^7HYzlDB_dK5&R9C5BA$}Na83nI>^CB<gBFw*zn-$UPneg$9HLG&wV#X-Cav;tiezASW6=#ucIpi4p*fiDDI1o|&U{0Bue8R_5PpF#fyeHTXhfz56qCVd|<>FdzM@)6%hJ6s1#u-O!w&4s6U6EyjF&9QJ8>9MdW$caaOHaNwbVWiK&XG4=ei+W_^+_Rcv_WsI7&UGBW1%D0t7W7?k3t}=WIO!{hEzsAX4<jaj5&8;r9&{egC3XXG9`qAv@-L8=2mJ#4BlrvS;R~?8G_k$kiPN|sUqCZX3Sb<)w(+MpMmevc$^K9zhcxB<f#WxE4*5&aPoZx^-$wpz@FUPyZT1rWHn=_SCG3vPXinJkC@zXvLA_prQB22QA@4`!pSec*9y}d83Qc~q=GZydkKnmDb`CM+PlaC%Jrz0vejYUW(a@t2&xGx?+4o>O!6?qLSvpt_*d?@Y4)`T#vJ1%1LCyu(Pd2*@_LC-${3-a$(Bx^nok#AC|2lRW{ya2!8n0)NdlBqB*a=PE2^jG`@H?RQK(B<K3%wG0I(#_vbm(tkBWyMZY=nkUJQjK^`ezX02-pZs-;G7zjz(St>UkLTB1=GB4nyz2eIM4e1GU`~80pvWH=&Q9?{-4(ME|cwO!_J`v7?Ad-+?Ap662o6{1cQ-^Oe>kt0MD00d=z|vi>D#G<jOjdf04$%{swI2f$B)4uB4UH$#U&FM{6-y$Cu9ejjuabOwA1bO!Wx`1R1+p%=r?fL;te6n-G|Q0VS3(mid~88PWV#H8Cp2cjL?LwABER@r97ZB_=JVs~irpJ|Rc!AKW^6-Ulz$ZrBpaaDL?zM9w<)<n}UO;9KDe$efqJA=C;Ci@bcbR)#>(0;g&28i7eH-Zsw3*8py5;G!h3;h)|`EJN-3*8Mo6ucYypc~jwO>FPGQ1mVN*_ys4O=F?I&4wcmMLZj}3^}urvkb?(AST}ddN_1H=zhp2)&_Au=&sP@W02PmItF|gIK>(8#F8|zef$$&1pl@2&wL>r0{#VJvUcF@5I2PX0=g@-{XB~6LzAzByf2_DftLoSxEMUK!kV}+SV8E5h@D{`Hmd^W0Y-5Po7Dzu0oDfX+XB1|G+8U;w?IxS81<PySQiZ^)(q#gf^G)h9M;-qO~G1gSWEDx&|dI0puM2W!<T_B4_yM@3AzMy0T^vT6fg%3qqq=sA+)iAxG>BCyclw-qRkZ?r+PL(y~rw~E)AfG84<U{{TiV=LbpbnbkrOt{S}OKfA}uSKXa%f&a02U^MEE_8g*@my0?QS=8Kqg05q{qh)LVWH^p61K9x=LndVgn>PB^;c~9#attqsAj8f>|^eM^&n~gy{0iNPu`0>!e&?DiaphrSagI@(b4SG3zGW2rj-SGRNcS9eC&w@S<{R8{~=pUd@!ta7U37rNbz1C*y5Zg8RXc*}=@Y^(c7h<wZn<YZ;Lc9hs@vSyn0iB9C5f+PF(sK|~?n1DI;E5>r5H$H?(Buz7AH+56*II?^B}1noCmDJ_^g)!fA36*A7_OBCeE|9p>T>{^>Ny5=C7XbInFCJoc<6<=$MMiqzbLRM@D(^G8s$WzonmnxQ8;fG>Ogf-(SOl6SB0La$lhx(JjIisdw>sy?gJkPO`i5Oy`X!6lMk|4ZyXN->jl<Vlh+qUJQAGZZxDZjI1Kf$^DyYaIEVBs@JQ&1h{K>McRr3$P8|3w@HprV(8QJ^w(I#gcMCYN1&Hl>DRMS~6Z;OaT`xe+IK+0n1o0B&+s~so1x9*3{AB3Kh^Y({V$wsP?Tq3Xnsa8rh!2Dhf(}CbAJ`C-(;IOlbdV;;1a3dSC)hafeYhXGkG*K0eefHhHz20tX2hf?p<m4K8=xm5rsIx^Jj05@Q>;KcgWLBFr8IFVFnY$jLA!yI_q17c9QOos19R2n*)@6kR9p?-6;>UrDDvz%F3>JGX4j60%R;+AyWqSc;KV8*w(GLUF(9_<l88$p-+ms&_I(BE67UtFD<U>%;_~n{p=%<p1*?es&k<LHuBpi}fH%f5yRM74F7oZ?QEcBkk!}j_1MP#ju_kT~?+xvZxE{<0`E?LigZ9?sGzRwsuY>;d)aW|Mv0tMZyr=TdzL9ioO?%OODCmO%=+7cx?-cpA`y8I)_t5#^<mo%;V@>=RjJ})x4E-}W`9})<7aKYL2<&IDUu+i8#i2mCf}i@YS^xa0yaCnzN3H)pQ~xuG_RM5kS%3d%640d(?Ky1?P=G&<tfDte<$nM)TQ!v'

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
