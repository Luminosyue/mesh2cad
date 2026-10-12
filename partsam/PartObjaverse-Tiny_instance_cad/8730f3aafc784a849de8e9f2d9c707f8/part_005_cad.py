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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8730f3aafc784a849de8e9f2d9c707f8/part_005.stl', 'relative_path': '8730f3aafc784a849de8e9f2d9c707f8/part_005.stl', 'source_sha256': 'dfa889c5510a18cbff68d260aaca6d34ab6a6faf11d9374faf519076315bdf5b', 'input_faces': 348, 'input_vertices': 221, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18242309987545013, 0.01462891697883606, 0.03194141387939453], [0.14416834712028503, 0.3037763833999634, 0.2053779661655426]]}
GEOMETRY_BASE85 = 'c$}r02~ZW+wuU!qoTC^~l*siUBH}EVh$AhD8Z^!$h;mdwML+}uaqKwbfFf#80gr$KDk6#s$j~YxI1msgG$tpBxiK*@nz}v{tt9X4wSGg+x!$T<?@_ht|IY8~-Md%s-o1O5V@KAlXCwH}LF~TpG|#=25Hgwy8xa){9yxDzKtzwwuox?0O}_kltqG$ijT-B1C8ESqXa9hR+2PLpb<P6=-JQGXoC6nxM~2S~^;;0`A0Yi<GlL@nOn$`NnPCB@-<@4udw0{hxpdPl*Zm*=8k@RcO!K~6Ec;?8+v-8;WAJ!`uT(rbWagJViI=~%GY;u=T%g;fH?{MZZ;`LB<9g{$?W-kCF21RqzkG{!lyzYjq^}NHTTZ_ZR25P`r~0x#u-|3Mf9rGd_1{coKjg+$`CEs4{j_%Ei|)D#I`6i-<cqiM*zf;E3ALMelzd%f;dyE&&9zegHh61%-tr^l3;XB`<XaCWU&|cG{)dCAD6jeh_VapkJ3nMm|Ao89d1`-nd-nbRq<*TIp5!Y5?YNzyS#(|M-u~q4e|@Y`e)t&f|Bw&J7mg3LH{O@mzC}HC55DAf{H-og-twl@j`r>z_Fw95(D@E^Euj1jySbfHUQ`Dqr7QQdI)?LC@1Qy;gNik3$Hs|#ZS;7mgZAhi`T85S+|G@ebi68dkgw~IUQE9K*K}T;*V25d>rZy%t0Vf5uXb|d_LC<Tkw5e<*YlSn7fIXpCtoz{a*guCPLi+v%Z2@4VyT|u`CjtXelH5iztw^2U~rpEzJA~%^3|YaRA>F1<Lnn^aeh)3U9U*0;`{HIM7|RAocgIP@++e2s2jui{_$~ieCzcFGyjKyX7|NtoX+ix^P@WJR>jhJ4X@lef72kkel@o-pVxC|0p+^}Qk|8>j(lBF>(5dDBZl#P44KCLecm~r^1T{VQ(ouJd>@W~nn(GX57oigawe&2yC{#x&sTK3db^sQ4`qEf_|LacKgK1~bs2j6o=bk?DDJ0=6XhG)q>`^Xs?<;Y<)6qG=Yu%^NoyKsO4Mw=-e0rMQvP~BuBTI7elB0lKSO?h2kO62dE6P2;!aaL-|nS;>;3MQQvGZk*thOT?J7<o<Qw)kBVTh#p#B)Pv?X6mTb@Jt-{<mp9eJPH)Ae#8U;QJ3>p83w*QagpDayBbO#L@@9m(}e`1vHY|G=I4sl*$2{EV7GzL-*)OTU+W&h=^0Gn?*9uz{bKU%3DJI&H`oo9FZR?t6sBuhM(t3F=R1J)Rd*Ta#~iG>?2`>uT=j(Qmmw#?x8Ujza{^M}`?u)V`X1>^S8|e@y+<qNh@S)DEvQDL+ohqvKP*;<|=5IYQ?>kim8PZ4^IGi<@MS|J87w*IYW4QG4DG4paN9<G4R3eYpN^jmQ^0Uh%yAYzfcb6<&v^ZsUBZKgMmhs6YDK`3Jeqh14H4_6oP-xgnLuLyPNFm*_Z}57b60$rm}-uF&!JW#k*eeL4St*Jt$mSqt)Yvxl<(u1fvZ<zFM;nD}Zx^{06b&wKW>=--vG_sJLk>_Po7?$74;()b|uf6wCQ@#`IQUHbS*<g4Cy=sxO}hjISyQUm!bmh=4E>KV6ho6P>mT~s&ak0c%sQ*Fr?6GLczF)SQL`9@dAeUx7_hw7#qg!!ypU<&0&y3l;86s_TL61{0V`N0pUK3b_Gskpz6{q*)+&+>1mpL*}<?7xiX^JRCTe8cK7?026;^)&AA;d-{SB46#T@N-qaIpwR>#(1jdtX!(6{;Nc4&!9z-FV;Wi`dqB!^Um{Nzu*)<7p)4Y|GK=&ZR9si;_+WGoANc!`Q)o9d-y%FvzYHsYD><4ahmHk`vRR;Y%GqW{E|=}|1qPeZp!_!<cnuvR5$&l-}t;y)(z=6=UDawbX<?JbZhdzyh`mGKl;whS6`&^`_gw+xtTxW8Qv>T%>Cy>`F=b1xMJ3R(Wg8<s=ds7wdXf{KPGyb`$|W;k6J@v-p>2pbiedh!_CgCRp;@0XW~(_{wv?)@bg|$cG=8to<wyvJTEUbJMTLSc^nq-`$TzfBfbCrt)BLEXuV=tf8&^5+dSTIzx10olW%!{b%8%|zQuS@#{|&()pGo3AqnhTj5kw%wtKu`eCo>W$rmXeX5(489>%`K_&27mV1JJJ^P)R{jD3se?l0f+x$Cwfh5XT-scu>qettz;uYGiV7SFr!xD&7YEanHL@d@%ZD~tK$=bOClwwQm^?`H2O#eAiHzkt_SFP4yRIlqbLk2!xl&xcAg%!iwsrBb^V^QXw4K)&UCtG5kd-(r3?W^QF)XFi{6-zBndG5;%Hlpdt>;C&(fhsUQH;X~gaS_AX<ixz8pnDQFF<n{e@ypKM9O1|a$ORZ>|!S}`deWyG3FoU08UXQ8^&a&UK-4VVn^Y^Bbn8<!|Gk%|4vF85&@DuyPk5S!3UOk>C+qfMiKZon6uI$C{wWbT$f7plX)^HEMf79aGAC<+=|KpyV?|+c}uwQANtiNu><3Fa+aXMe1M;<@l{N5J_ipf{I^EyF!IEB|OeM_?F-(M~?TUY1?grA`Nq2}uly>C4E;(lEoZ_Rk!qIPeeP5!SzJRhcIaD6tpldp8(b&(G1I_1F@^3`+qcz#)J&-J;PPrg=cpt`9`qq+U`e{%ai{kd+#C-QtUpwUV4SJ+bBv{gUy`_ZvI`RXt0cwUY6=5f2mh5dirq`Da{^yBj`4&ZirUZQoK_UJyZqu&0Fd@X_3f!go;_<Q8Th*La1dEKZ_9KrAF4A&g`_Z(hlYA2nzZtK>NFD9F>OU1uhpC&bK=lZ;C!}am#%>FX|9x%iQ^St%*F80UqI@x&j4v%N2Eb^6axAAlOeH!^%*$d7u<ngC3?Zo$GR+BSy+}0=bePmEy@O|Iq%6{4ee&1hwkJmpB`;aec(y4CB>vl#*lCM40QGN73Ch&L4$lSAZ{2*Tc>$cb7?}Z;1QhmkcR#Z1JW)_c^?MJ!pH7j|Zcf<FEPd#2QMlGVc8FzN%_2m1L$=B{J<?G!W%=PeG#`(SYdq;f0-#c1O3j5voeWq9SoL_X2=a<ZUs)IK75Rb?96`a4Ml;;t@G`_#BU$MV0h{umh0r{F$9h%=oJ6nEEL-RR5)Rlbo&-(nmv(uTL8)Mnlb99^wf8QBve7L_mlc_FRN<bCg=MGdKV<&~4PxZw>u0u!ue$=}K^8Q2v{@zrdY~cJw>71|Q?^$*9j3OS_XV`DZ-@nGlN>VNEDet4)SxR+KluRDy{(o?OrUQ>x!zBKW(e<YG#MKR4pX+=0`)s~v5!cOy=OwRf?$6J@>}TKM_xcQc?<<bQbiCmG0p-u${M{LOjC{q8_Y*{iC0xgwcKq*yvHwuBoqmhKF060yeuZul?^h_dma+eo$EBK4#QP8S$?VVL{SdV=?}r#aOksZx@1N+rU3mZG%dgq55<GssZ^Gwyc*_2lqp5Djw!HsieA%A=y$kREh=#oXql7u~eoxgOv|l9bIA1^JJ<gxZ`%7y2U~cEO!pFTFNY|yV9m4OotC^f18^z<`!T_GX1J3ij?9KaKN|Pe?Q|)<twS2(y{)i0r*XY=<-=6xf4!O<aAjX&LHLQyIX`K8S=Rfgd|FApH%V%qN{Jk5=?bxm1_t1*ULXWX#yRPwjtQS^V3n8PCun~bX|F-2SP5Jj)-@N5Iug`zA<?7bQ{r|h=+Qrld7gM-Gdx2fS?$Gza?qCn-K(GgRDD(sHQ1E!@81Q(oA42kU=qT`X@HFU1@HDVD)C=qlo&p^Ko&uf>{TMtMJQX?`JQeH%9SimW`$EToeZe#2_=HY?jss5s4}*RP9tKvRgTV^8A3}0p=peAv_rQI@JrR<-L;HZGb^~_@J3<}6ZK1894&c_{cc41(J78<*Kfu=D7SQ(K7T}i94&avHHc)498?YVJ1#AblhjsyXgm#5?0e1zvL0!Ra;Qml|aDVU+s0VlmcsO(@csO_>bUb(>cqY^jJQKVCAvqK}9UKY{fldR5fP<ml;9&54=oIjLa1eAdI0!rsIu$$*JQwN%o(rA>^##uX2SR6n1Hl2J_SpzPNcK0yZ0Ibg9y|*?2|58h3H%Xs82BTwCsYA@f(JnRfd_zlL;HfI_5}9^cZPNcOLYXler7r&B)^N0+zcVPDYP}XDYy~z9dILXL#Q>lA-FNL1-LP|3A81+3HWVj8}QrU=1@CubFeMc9{l>bvW2z-r<x+m6lu^C;56`lgyiF<$b+7Po&cW%7eKSX1>k&y<V<KPI1_9zMZ76eOpyRJfD^zwp{d}V;9bx(@GkHU=zj1H@OFgcebD3Jec)q%yXIpE$!AP)9$Es;1DAj=L(hRPgUg@=;4*M2G#^|FzJ!pR3(W-Qf{#KCU;}D*6e0NtLUIx`9xQb$I0?KLAvw+zpFmeZw}MxJ*FfXJYryNE3E*|$4bYw74d7VlE^sV(J#+_nJ$Nm2J9sU4HA3<>=sxf^a5D55I2oJ)Jp;}F=ZM;SpM#KGjF5Z{A-Mut0<Hj8K`(==z}3()a5eZQv=n?3d;@w3d;?r*itEse&`V&cx!{Z7v(TepsYk$P!KV?D4?~l{Qul%ngAXDk?}o;KcY`;J+Of46A$g@K!l9ASPr#AjDCjD16nHUo4R|ql33MHJ33w@V19&NT88jBW3>*Vp4~_vxL)U_%!Hb})!Hd8V2+1mR8(0NzfhL2ufcHQ%z<a=lpgG_};FHi|@JVnHLUK9u8n_(%8A9?cXa)Ed_ztuRd<R?utp?YC??G>Z?}0yu-T;3Nz7MSg-v{3nwPXD*Lh@~d<f{nD8uTJq>RGVV(_jsJ3VIkU^&t2ZI32nhoDTjJx*7Z_cq4Qrcq4eZs2%sq5t73Mudk%~L&L%T-~ec(s9l>$4unRD+O?eIInc$TcI_v5E_8{gT`NkS2VE*^*Orolpvy$<T2%6UXpE>`yGjm*MvL0DuH+EtB2l|GmK+L=5VdP*$*<Sjk{3c%@Ivqk=oat_@FwUU@Fs8~^bj}^d;oe9d;pvcEdpnQ3!&xULhuFXXJDyUzzs}M&lGPVBwHaQ*Ae_DwJx+CxGuOpv;nw2*aq4PYy)<Jb^<$rdzfPENUJ(Fb^p_UL96{!We3gvLz?B0=G!QLKQhYH)?b?{V@JMKpD(Zu-M~*|PsINM29t%I'

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
