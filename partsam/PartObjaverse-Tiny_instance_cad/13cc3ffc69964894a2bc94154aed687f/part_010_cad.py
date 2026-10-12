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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/13cc3ffc69964894a2bc94154aed687f/part_010.stl', 'relative_path': '13cc3ffc69964894a2bc94154aed687f/part_010.stl', 'source_sha256': '32606646a6622d439486f5f0e8defd062bd9db37ce9ed867907cb46e0d10f18d', 'input_faces': 572, 'input_vertices': 358, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17692598700523376, -1.0952353477478027e-05, 0.3694955110549927], [-0.12290032207965851, 0.026916489005088806, 0.4472036361694336]]}
GEOMETRY_BASE85 = 'c$}r133wGnw#PecB7%TMjevM%i!8G5B3uwuKuB1Of&yVl1Z6NLh-~6DARq{YRZx~FvI>Zf8wzrTpbRjI8=x{88DJa+Wt(Afoj$2w71c$*?|a{S@jIUX`BmM%)m5jK?u68?#Y-f5>gOgeVO+nH6{>ljSXnR88<mkga@gREocbfO#w2(Zin#n}Kezim-BSA`c%!^=$wM-724^R?jwH9qY?)jylAQTS_Q>pkBL+N@JtRZ;9Rr8wWcWO1=)kNDKfbw1vzGNDO={PRJQ4Xn{*>{X5YJul;Z|wOsJV07`7XA1#eVUTW6KoJDL*HaXV#i;^XNBo6n|uTUML^7c7e^k7se_+wad&<KCi+;o5v3KRea%prib!!w=S}I;oD6VPdoTbD37;%K5$=qODkS))YMSE?dL%K{FDPbR6k6a63T03zYyT3Rw(}UEmK1IAG3n>=jMc8UvuaB@sk~Qgtgyrr~R?INjt*&$8e{A;=i9P2<v~to&Hb1>(hd;@ip8T-$?0A1!4JPxRXE83$GM}<)`6Je&(mIEC|c<^t2}wpYVQBKg8#3JWy1B%j1d<Dn2=sZ@Yg+fS<`!ylQ4{D9;_AXY=U!E{gBzI3bh|s5-~y@!i!G&&nDd%DFGiy&4r2f4!^9pQPk(ipo!yRQ%Y1Nj8s`I=8)uKl@=$pgo$O*fKA`yPi>e_10YbI{AM(wLQ?E#X1)8NZtv>+pd@r$`5avZu4lHql$0*=;=_N{oD+j7nb=(@eTzsyFG;|`xTEIn;59Cx%b#Co2RcX2(&-aG)2|lwQYM~eD!rSAKQ9rX#KS{riXH!5Bk1-jML6LvjY9B`K~4NZ60a7Me*^m3HJTQdcUW5>KBvk?=}3hY0ug`QhlT1zfXTUl-K%vhRwb8s}<jK!&7$q4PO_TZS#2Z7Zsm8aFTr;!<YUxGtkcXBJ!~A_(0wc&r|&U?1_QvXg=iltN?%QS;b2<hy~iCdHIEbcIKa*s(AY0hXeCh^HNO~1p2?s*g*c9e$#wQN}kQ5zYJG=UXv#S<F5JoLxJ|BuNoZ4H+>z$$scpS9lI&saKb}&I}NY5c|xEcG#_3kH}pF9KOcVm$=;mM>+Bv7=%4%&%|hF6xYPdV%v-|yM{}ot3SX=m+W&?-{qN1K7&^X&JL6lpzg%ek81CdxVU;qW`DwVDpFJ;Z3!N95yYu4Uscm8N&TwbmMKh0W3!B%5JM%iy>^sGsb;EFH-H5-xUvX!>GTd1w4R_W_!<}`~aA%z~+*uE!-+!sNvu?**ZKs{V_1|!3{f~BgLveTC(cIa0Vi(pb?(A!ZJNsIC+f{*fn(I$ouDHAZYVPd6>4hT|cg_QbJLiGO>=g1Rc-}DFId2rsZxS3wmpkW~!rj#rcg{<OJLjcnlN*Blpxbl!+y_Pc(B7gvFYHz4>oA@_Zp6W&e(ri&@#8Ozx9hw7lKOY2J{?*gZt6evz2ZB+dn{1j;g{4eHE(KYeYmb4N!=H?FR$^;BJR!qOz{$FPlR&LZ<@ykf28>6Wslh3>vH|QhLfL{)Q9W(`Kz}pzWS-h?e8`GWZ@K>$9~)zdSB^{H!GfW`Gip3d`aNGV%1+&JhE<dDCc}@t~2x%#n;uy4&}pVO|yCA^m4_g9vKqIH;0??(mZ|W%+UI9UB58CQ1JuPa_sLloaZmopC#u9`)&Og#k<T_yztzFQ2s^DNjCRhpRPFP0h2$Pw=6azkUwXqD8BKTvG#QgPi!~Y=CK{)6;Ew7A}}tR^PFh<zswlLqgUN$_nXUgzZuRxeo1|}t{+W#jQ*K3%5JCOJ@1<uxUWZZ0{tA@G*6B1yhq9NqfdtNtPK-wo*o^lxIVACoc&kx_@GSsCvQ-o|21ddH~o3MKlAtMoIw9;UOH)-%?o?=Q9RcA!9c!gzV{!a?e-Y1-%GfhbAoBlgI$98`Rh`3zw7Q`p4RRd7%zvL@ztF5)AXC>?>rO>z5bOgCWi8FUz-|w9nM9Uv<GhT=TryA_lm4Q{%Bry@$|sFySlyN?5DathWCGRlFegFT9Kb8`ULt@^COM&0`uiiGuDk0;{x}q`Mxzz+dP`wnE8HvAg>G`Re6@p^E)>TtV_Dz4A<|4;IYqdW?y)IOyIsWAN|(kKzsV##CoXC+onG?U$^?%Kt5ldL_c46JaB!@IbWIUcTZ%$UjL}wPQ$D2o)+M9D=6-rsbS}X%S}FL{>#eQq4nWrfBd<O;`w8G2Krg^yVeB8H`eYl#%uEfp`7OhlMj=M2iG^951MnX);#{N-{M8QbkZ=ppAF|cX7-C-=M~?Zn`QT#;kg~A2m14mpW^oXHRGZ=^U=(U#RnAk&L4f>>Q9%O{?t6yHzm-Yn&*GpH<U+f4-L#y&3R5Sd9HcV%a4V&^Q}+9+uwA;^w8_@TyV+vo~xD@+Rk$O!g>7jK)$)$oHMU02<?Bvo&Jw+e>Ze|4R^-ZtNUhX{uu7$PyCJb@v!_f+{w@M{jbEs^51YL|07ja$HV5A;m-U@pZHQdY`(kP>_?hA^WEj9{?4U}JL`|(&ia#H?gho2_04c+eT!|Ht+=y(8t$y0(c7mf?yS#-JL|Le*IdP&_1|!J{XY?7yn_3S;m-b&-t-Bs@9bZiyZhIeG2~Bhe>B|LAHCw)iaYzS;m-b>Uo%T_XMZ=`+25lN4QJg5o@ZQc_6yCO^NiundB$+(JY%?Xo-y1x&$!&Q=hdN#JLj~*ZGBi*o%5mQ&Ur6-<X+Z|;JMLo=iC^r)0=z?o>vWb&#QmFTXE++Y`AkCPT$u>areBfxpUr*<+fMcInNvJoabX7-4<NO^t{vDd0sHwdA^91ZOwiZeBN=nS<f|ho_Abs#<xdv#hvFb!=2|ZFH%===lRZX=lL!^B$@dhe10_Cd47!Sxru%YKA#%yJfB7?Rt@H-ZckdJz`A7GuetlYT%)|=&hxv=&ACEz=lR{`W}V+~8S~3|pP;$(J|TLhIO{|3eTCu9`-=F^AGa29=Y5Fb&ij!3o=3L^`c1dz;J1o9?`I5m-p_cM`xSTI7r9*bgW=BmBA1(f^N*!P+<AXxxbyxhI%8AledX6#uDJ95&E;l%HFw^>x!laV1y3pNzCU#MCH39+hYmOMG-FiYzRbGq@S^&ufxjl%uzJ^;)XM%0_w8~o(aRiY{V9n+`O!Z7Pf3O~{a^hlNwXG>|G$4qGR<$pR8M|A<atl~Hqp09_@~g5(7E_0(Yfdt{t0vpJpmi%+j!VGi~R{c9-WOJfX+sz<9ngg(f46pW%yuSEp{vXZgd-bU343CJ$y2{9{Ogirf;=iH7!;hUJG3Ve-pX}x*8@r;@geB-QZhQd}VZ1bQS#d=ql(+`0LP>&`H=ezFiBu#$s2)uSF-~E20z8SK-T}uR>SA%K3IBtenNJfM1C&i@zLQ7F`B^8M+L*G*;5LQm~R1D-JJ(E`d)#mp~W8M9WVzU)1)kg>N;{n$>{UrmP0Os#PYwDgFjaS0xr-$tn}y7=OK`D-nxNw93TS!(VObL}Kw3tTOS{@#QUDfmnPAv{-T9uAyFebb0C&$3*|;sWOSn;f0l>{C7{qV*l~&56XT+OZi!=&ROb-|H=A{_<!SnwDeEJ;(xHp#QzKb4@>_*EdHQXCjM{uZ!CR~So{I2O#GMl{gysJEdDd}e)Okk@jLj;e)JCbR{USlThZ^}KSaNSehV*UAECFww-JAYeeB!Y)cqK?4gV(oZM6RUn=q-r36pz?!#=av0eBp}6O+E%2RjJc#~6GI`vLYXV|g6*lf}-$kE73Fl0!0a&!W!}Oa5I+4vO}OCD*T|yn@9N;n$*TVKVn_fmMRt!W?b_s|stvTF?wu6ZRSX^(po-<M4`ae`Y*i!Asw-B7Tc8ScR6cSP5GR7rmPJZN_6YdL3HW8^n5y*1>mD7H15$z_!3e?;+M>v<Lk)TG%mSJw{){&rx=qaXAk=4;NhwuE(et<8>8UScF)Q(N*wTlwHdhG=MdLi*8A*$EYPbiWb(9xEU6Ox1daztks=ho#3KxCzkTY#G>1wg*7LxhqZ%Or>q|9Y<*aLxab>+uVJ0N5nT~2EP+_oOR<V@Sq~H7veupP6gvYK{ZC>k{~NLBuh7DF6Mu<)1>ZrLFj=oQ!#2ZrkmH*ve}`D~-+lYsw@-X~AH5sBo6oE#-puFLqh)@)40{<adNHw-KTo_0TMS=GnXpCZmCThzXqg``z+QlhUP3J8D~R8~mcX}ACTs(G3v*=yTIR<Gun*v(zaW<Kqr}IsFW~1X6LtZ8o_TZuE%T!k^QRPCbP}<Y*Cmc%N$>`g32TdPz+7pImicif>`u7o6k;jwLEI5bfp?-zSWk2(=1Nbr%#T!9DqM7TVky6axH;AxUY{~yx1sAZS8hYg{HOz~0~dWAv6Po2PQb2%%Umf5JB>cWTsh5LlKF82b_D)Ua{LJ8yNN}wA#a!Z)`33k=G!tqUPultB*#`TXFg|cRAG!7`F7HePxw|QL7C{weP4}O^i9N~Tlv-+)*3FlGqIH4MJzfEEvz5$Jy;t20m_7>`!*0Z5H31{SjvYGiyn*?Hi%gCd*uIK-x@L&l@pY%L!8Iloa3qfOQ8?Dp?l+dpnIeHVv=L`!+OH*M@!E2Ax<UN`k;HEyOV3Z(08MSN!#CJZi`=w{s6rJzYM*Mao#{)tYM84|1SDn#$WVw-{hHm3MN{f&7UC_J(XDW479LkiAB#t3wx1xE;bLIPnob+ecK4z2p3&IEaip7+pz-pca&`>XHUXT!bQv2wr75}r%!KVe#ks&i*JN(#9U}g-S*^V8oD#SA-XfVHP(>4szxmOGGftX(85kJ&qSX@pJKcgGnbd5pTk7Uelwd`^de%>dFVytavoady6l%n@Tbs6(5EqJOG(-xTC>XVrF`!^>^a8!IlgxWHk<sIO&gxU^2jIgbF6%uLk^0`IyDQn&|=Hrv(O9hYtakP%kl4_m!n_DWDVE_+iS7I@LlLb_@B{-(7)nKCn)_Zx-2H^>CFj>Rk2tj_|51x_zvhc=&tx~=&tDdFj;p7z<OJ(FMI%cu(bva#zbe}`=B$>12I{1`oVf7TwHg1F(=Z9Mb9D6WM7f%590g9_qW>9pLUAB*SeQ`xj*q;to!Xke~7=;>YrQbKk>;{e<st<;;*pA;tIw{{4d_c@%qIYQ_<fu?uXESAr}1_Ir10$F7$HZ*T_AIU&5Bd=Tr6)dAk5MlXyP)JqtFCcqa2w=ITjIbRqr|bRoI`6D{ldMq<%xh(*7M7PgdF^gQ%Zayf~dm3`+Z^J6diF#ZDiF#2b_oDY8{F2y_$E5&uQe4gXm7`()fpv8~1%En^CM`I8BHVXDIO!RPK@eiRNMh`;|<FmptiHD&x(Bel@Zy0(cd<1?ldIb7Gd_VMq=z;h?=z-|_v3q>$4Z8;>aSz{8U_D@>dlHN9j_!f(hVI5^h22Hm4SgqCd}r!)LwAOEz&iTY0@l%DQFse<Q+!)=Q*<MIOLQZ21H6>ALN|vuCvJr`^sPR+9dUEw`dp)(Ro>pW#`t!$D~fK*=i5<7*K3A#@~t(jlf~|Ww?^NNN&j|%b%%9fY*Jx8VG^hLb}uZ=VtwKFq94HbNB1Z0gHJ;XAL82}yu^bs(fzRg)YsP<WPN5RCi(v;EYo5S!5>9GhRGaz95x&#vCQQ$uq;?6*Ui9&(8e_S;vU+UhVH}|NUq&U+>w6n<Xz0i_KdC0oBDjGe7CFzwSB8Yx%ftwzQwzklcJmAn|K#<Sab{gZQjM47p>>W9iEyusa+F_B^Ljm{%QBcpICzY-~NZ*?k9u4#<M@!-M^OkrCw^+lJa{AubBUz49-{5D(}DHU1KN'

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
