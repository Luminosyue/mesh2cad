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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/01fe14f50de443e4b11ad1fe033df666/part_009.stl', 'relative_path': '01fe14f50de443e4b11ad1fe033df666/part_009.stl', 'source_sha256': '22261ef79b228294b401c4b94096a488fd7847f2b825d568e91eb82faa58e68d', 'input_faces': 640, 'input_vertices': 387, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4114878177642822, -0.2991793751716614, -0.2801857888698578], [0.2730967402458191, -0.09402504563331604, 0.2809242904186249]]}
GEOMETRY_BASE85 = 'c$}r22b2|6n#Ze~pc2|ZQsP625`=D&fb<h3i+~aY1RkNAoDm7458ZVf(2-<DeBwGroY@&?bX4GVV;Te94-6=}_O6a%fE^WF!|3e&x_)0-?|Zf9%$e<TzVrRw|9|UN-B7n~l^jQps8O?_=l`|#{`lm~+Ap{9Jc)W<LvLltvK4b@mMrhOXvyk4@3d-N{xomBblk|%6Z5>4-rDxFN|w)D*1m77egD!v?K{WXmo8qmV%hXX(-tqARU-P}=?j*ZIDPq?=}Su7?+!(MdUuW$b?h8l7yBpw>c}-@#=W~&^0Ai=NUqAet8#BhPapO5#EC8Gu%1GXy;InyIHV`F{OgaW!+IRuJN95@mY({$GU~jlC-uCykM!%$<h@q?JD>9CarBfapZ>Pit5M~X=vqFu{`9PV@SdEXiPF>e-CPmYwSQt0`;<rN$+Hjd4(r-)=|{KyGD?rX*<@pJNZ0=K4i@Z*(i7b;D-Y{IKd<_AMWmiul?m$!`q{QO7#GuC)#IkUG4vGeO@Cg;Zx`cIwXZZ2)^!{c$=fT!x{jl_x@&n@kD;eOJeE~|72{~@*KxP?>$uzc6Iu`TCnp_wr~3DhqpyVLkLoFOoj-{MZ&vHEEw^ONXVpFQq%B`mlr^7KuPQ9cn$OAO2deeN!?Uul2R()!%;z0XXI+2Q`c9cBJ$`-d%CN5ON*{l!EUYKdV_zKJQ(f-$N3z<R+8@hA>E6j_REG7SA3jZ$Md^wBI(xI~p?}i0e)O2BKj=48e;PeW{mF3;W%XygW2;P*p4`=-GOTMq$1lFGEUbIziIMfI>rZ#R*01M@_x~IoFV$n{I$o-$clmmJhQF=`^`OUCSA%-ctB(5XYP#0U?DL-Z!auLkW2X+v()D_hhx?XA>FJhl?G5XCor$fhmq+QT53XC8bv@dyPim&4bno|L%ffoluJ6ZGM(OFQ?|i+{RKNdOpA(yo`Rjnu<2T>5KdkHe>@DoSFG^2;f8g1$9z5^9{%l*Me$(T(g|A1~=VYSBb5XiCX#BpguIqDr*3SJ=detM}XTrL!+qS*BJ||3jRganW>bhM;dsFvL_S>cF?YNIKVO`hlWd2?I!+P-i-QHziSl4wsvHh=E_3OHA>(_PL)*n2tP5ruVC#gR^p}#-wL;dwCQRl`?Sl4wg`SpZ~u&(P~Rjq~PVLe#)URhfGTu5x|<+qphDt&BuCaeeRVa2+Nu&(P{ykcm1l%DSOOm_XOZ&kK_T@OwDy6z=R{krZ|QGcqer{6BttMssCnXs<wUaIMOzyA5nveu2n{jD>Rde74<!@8~;-mN>!!n&vH$y2rWhV@|GtJNnNsdspGeQ`)n>N?ZB_ujCs>q)Bgxw5dX>qe|~%gQJ{`Air8{`&6Nq3Y{2`(f4Xepq$8A6DJ&hgG-xVbyb<7w9?93%wruywG~=^Fr$}&kJwzzO3`=_~z)0uj+PuRk!1-x*gvfo$*!Oj&E>1W_*L|G2?6XV0>#nawuy4t8VANSNQOusQX=Yd%vr0?{}-~{T|eB?)RX6bHA%@?|0Sh{T^Gq(?73S4^_A8q3U)$RNbzJ=?*ve<<0X#b^E+f-99f=x6cdJ?eju)`@9IwYn~UX+vi2<x5=#gU7x2`*ZqU)cK={?-9M;q_YXNb`v=wS{=w?He^A}-AFQtX2i5KVAt-P54_1$v_S*eJBE2?y9b^A#b=`leZug&7*ZrsJcK>O0-G2t>HTzGi>;5x1ui1ZEUH6~KI}(xWw(54>R^6`KK|N;O4(hS{{3X4!)+>E~vAVv$q`&Qvy<YJ?Wp#aDQ{BF=SzX`Pf_lvRn$=^be*3<rx_w_ujBA^<Ug`U+)%AT=b^AW6x_zIm%GAy3x8V6Z@szCo3HAf%_PstRZ{F)wx9{~;^S^mJeEnKpb^Dzm_3lAmH{VrMx8GG%x8GG%x8GG%x8GG%x8GHQ^P2A}s@v}>-k{g3b^D#o>iV5cb^D#o>iV5cb^D#o>iV5cb^D#o>iV5cb^DzyN9Q}6>h?QZP~LoJvwGaL*M4V9blaRY?!k8?bo*UYb^Bd3sK<O4O`NzXYg~fwTIhB^th(I~t8Vwhs@wf=pquZ*R@eJ3RcEaKJ@3Y!{Q1T{O7#@F?xR$XJ&_+--b2^&>0xpIy>Q7I|Gq7lmx<C7n>J^aPj)@=bX0lOla!AgDe&tlYkRQz{2NDSqV&|4<yqycZt3o?tEPM!y^8Wxoj%}u-bwzr@9L9@(vweol~q1@a;5)0(Uey`Wy{w-<LSuq=xNF)y|O(~*JJghDQ~aG>M2{^T#wcDdc2#a?}_Svt84$OZu?*Loc>?^!|tg0V|ATBs@wTvb)7%)Zx8N{n*XZX`LDX2|Ek;hpZwFPjZyWhZtGXw)~~v)zv_1lHbnN1(S!a$&*>kdYyWryKfEz=e2pHAFM7`SqUVh7x=(J1yuXYd++XN9_m|OAw!FQ+jIQ%Je&omv#SzzI^`t3pugB^sTi#rc)%AK3kAHMyaYX-HUHe~k+yAQD{!hgkZ77bIKUUZIqq?0xR@eEHI(JO<ej(@if}ZnyLC<-<pxgQHwR>ZCRQ;;k`c=2}t8VL$KlH=ysQ$6K_K)hef2^+klm5f>JyGLpbsb;T?f9y0$2Z=!Y)|BTHhM6h(R1dr(Nng(ozF(s`J5W~L0Q!GSUqXV+v~A<%9c0RV|Bfrs-FtVqx#?K+W)HC{#V`he>xE_kD5PL5B5LkIr|@@>-<Ty9$OwY|5dm1Uv)eGRk!m$_R@xmsQOj6^{Z~{S3PHc_=_DCk^N)zpnuSF`p4+O`txZ;Mb!9OUB_2-JHD#tJii|NdqvcIwtDdVLeF`A89imo+vk_jbv~y%6lbEY$LdK_-d>N@Q?|Uh9;*lUSM3Rz$otFa!Tp7vbAO@R{!eUJl8Kr>R@eEXx}85(57y^-Ycf&uUv)eGRk!nB^{n|nI_qCS)gL@+QnIBxwTn}{hF<CP&_96^QT{YX{}ZUWJ^rD80@bTWxBu@yf$Ht9p@Z}<A>5bT2bO#x+|5O87iYq4_$|3fh|lA96L>6n7CaVyoct^Jark3$8T>K)75R1eEBF&~Is6H{i+n4*3m!)<fycpTlDolk`Ms5VE4&qckz5YH2v?9_hb!P0$Yt;g@D}o~;4SbR@+^1`Ttq$(E`r;U+raJM9^`It4|p!Q1U}n^{JXf$<QUw^MJxPPc)|%6SK?oZCw#k$9r!!&g#YZ~5dI-N;m`3h@F9M`;^H0jckqPoaB(00eR#stT};8Bf_DdPh~dZZrqhm-(IhvAr5(-io8i@=9arFAf!B(5+>L)X-j%fD4g5FocF>Mb@jt~oL_6NZe-rO>+Hnv5J$UcXj*0ja@$RDy&GDP#O`#p_&?NVOr5#21MR+IEjyd>q@S4$%E%;mTuAm(+;J<)(H|?mvufThQcD#uHBHpL8V=Mkvyf<mbT>QCs_t1tO_&xB1Wj)IC{Cin)0W9lMef;`(!m=(6#~+R-EbG!v{GE8hvM#-c{~n&OtV>7nkKzf-y7WH&`*^~#E<J$%0G_a{OC#_{;O(Lf1^5Mc!tFhI1bJRB^0{zN7aj3C;t9`lF%^F*p6~`2+wiyH3Ga6C68=kg!mqlh#IM8?-s9qB{Fm{BH@dhD|290~`7Wm6Ps7_t8_vZ)7jHhg<YGd2A$cRb5MEE-1FwgFLw*(h4g55DH~cjG1bGAe1e_$#gOl(Aa!+^xJb>ID9sr+D?gjUvZNgn$)N;`nK8N3u8-=(FzZ=1qk!Qe{!H<$}h98ALBJYJig1;oc27d|vg`9@}0zXE+1%3>^oIDf09BxeR3eV>EX7VlYX83t>8h#$$Pks&F5AP%Ih4;am$T!2A;8OAoxD@VA?gDp*+mg?L+row9u5ckdn>-Vi`|=depW~8S!g61>z;A&kEcfLk{7HDia$j!8-;O6N_vKsoZ{Z2cefb&wXL!PLU%rk1HlDEDm-ph|izh7i<z)QHc(>7pmiR64rqPa*&?Gm7r5$JCpM`e{?HG?g9<K%MxD)?Qyh*g<0R92I?X=?v{t>*lXvabPgLt3Oj=S*h!h4%`Ou(OjcQ0*dir*A(GVN%KCb<xnc67(@j&~C6D8(<uJBxN~!rz29o_6fR--mZ6?bwgMAMXI|cpm?Gyd$(@GyZ10gS2Bd{%pLvXhR`>A)c_TNAlO0To0CYsV;t9JYiXvhT;#!6P9%;g`dI`mUZb}{CDw$WnKCL{|h`}S(gsuAI1}wb?JWm`|*TjT^fcz4DT`8P!GQzp70PC*SWZW5FShjuONhPB82})2tP*%KSc=tk`TU%JOm!&VvUPO2;mP2;lC2X|3wHtObCxAgc}gTH3{K{<T3Cd7uUMzPY7R32rnaqZzP1DB!r(Og#SPY|AG)+P96l0a<SUQLxk{u62kvY2v-rpzb1q)C4^5WgliDOXOKt17r9vHq8}kVkPu!%2>%Nq{5wMU8AAB?gz&!-!b`~)!6RL)a`7M``~e|+j1c}0LipbZ;Y$eNQwiaGLijZDNLb$cukrkM|GsdX5MD$GUrz}CmJt3EA^h)z@C}6UV)BKs>}Rj`{Qd3&@cV@DQ9}4VLU<=3Je&}&PYCA`!Ug0Ju<Wzedj4MPd|3Bp!n%JGP7=bp4;0qDqOk5Kg>}y<ypUWB%lfg>^VgUA;lqUR7liP;gm8)w9!dz;C4}`)xE^^JoNyg6&qb2F2EN|KG8Z$*3*Z^>bn<+7nv1!4etmPPD}g6v){~dQ*ST2DajQ9I8s1XQzm#)d&o!;#xHTLjyw1f{F0Li7gs*Y2!o^zha=6sR5*H=p#qdlQ3th}2FM?;m*N|7h*K)2>@)Ed&I@gh}g4c2lGsz2K?dt@2MyTJW@p~HDj8NZACr^X5kJgi~gICdCbI9{x>F?S6o{ct-e!Uw1YP`7|y9$35-fG52`eXrl5xkJ`UPN91FK1jAlIO!KsB1ZSDXe3;j=UDuF)Jm{g0JTKW|QZ@I%c!TrSM9|XbE{StYcO}o(cDNG1$eG<ni!S7niyiKpqMYfG;2qf%~}_M16y(t3RHUnL-{3Pj)em<Hm7JKfIBge<bIg$~BGWxbYk#JkiA%7n8`B!B@B#?P3CX6g<$yB`z)`kARC^4091D4~OIM739(IB+fOEd<lFZbxtIYfhTYc#pGeI_H}>qfKb2n<99!_0inLTfZPw(KAJ+F43DM1E+!9#rN1xY_eE%f>DSBgFUK3iv19Sa;*Dc`q)&#Dhr`1d@8RU3@F>Q07<mXhnz}}jN5VRm6Uh@`9kYStID9$RcM<twSjQ|*9tdB?7+pdh0qdAuNG^uYbaA$eKIB5UuZweCG$przo5E+2&w-n`Xia^ssq0KUDRVx#Bi!3XcaH1MF-`C~a{i8-yD!&N$Z>@nBiz$P7Z<(AUEv-sI=d($cY<5G=-{FSxjo#>MOzom$?f3ga1U~4xEJSYN$vo*pw6D;E^rao(2U#`*1kTI+%(j0P59jet!b$5&LTH~wU5px_lCRCUorC8u=IB;ez!t9n|?hH|2(|b9NP`Q8(w$DNBX1<xgFe=@oq<M19xIv+mg?LJ5yIDaz|LlvM0F+)-h{IZVsQv^|d0$U>&pO<d$$(#;60iJ*;Eag4_%~?)GFqxoDW@=Yl++8@s6O;v3J;9xNezg8X;S=dWG-==t^iNS(*=q)a2q*2?p_fs6Wi{&A9jqz>_FasFCdLu0O~fa3}{R`_%mr?@zSTn9eQ#mO#CC7%R;@6J)v<?qNf;Qx{4IR2KL4@=}zUp{r6#yRRxpX8db)K!D)s=+m#&bj3p<UEq|VC`$^tH$*4@lc<BLp}~`--+LV{yX9Q+((Vb4d8n8*WVah8JE8?Mn5o4KcM}@Skz@aB>zC!0_v(yt_#<uPdsuyoX2?QlRdoABl7Ya*7(2v7al+V$)3{7`X74OBeVarclgNKZM~oWBlzeMwdB9ExEId+>KEHGdBgSo7pZ~*lK'

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
