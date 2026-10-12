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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f634e3aae845402ca63e015086c9dbb4/part_005.stl', 'relative_path': 'f634e3aae845402ca63e015086c9dbb4/part_005.stl', 'source_sha256': '6710fdb74f0105a0ac73d9391023a4f2bf0298804217d7f1267b77925bd3472f', 'input_faces': 316, 'input_vertices': 254, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.23750591278076172, -0.22661805152893066, -0.34212684631347656], [0.20538148283958435, -0.19913597404956818, 0.3421264588832855]]}
GEOMETRY_BASE85 = 'c$}r03tUuH9>=fv%C*c~-K58M#R^SCK|nx-Ybt7{p{1pnjUl9|sDO_|^rDC;qU9^i(veKX%E(8W5?miRjUx&Jq^ap_=3<tQd~e{k_nh;)vvY6%{e1SbJD<=0^ZWWeXU?3tbLZT18RG}kZ_rW_k2ca-f3+;WwIs2+Uur2$OH4@{mynnmoILsMdQx-l*~7@?gN6=_A6`$ICZz|CNlZ;h35=ElyC+2k2FZa*lTy-BMkl{MDP>F|^Kqjmq$cV<b?oTLiTc0Wg@%U($z9q9$r<wh`1li>!|J4CB`km2=wzvNojbXN@U~u_m9d1kchBBHd0U$QR$s3)exG}(&6QOCI`5hLE8nVxv4poDy0(+@@{*W6%&Qi!MzuIhc_k;^LH5s><0QS`uSa~nt&u8@&qr5EnO7|RrMoweQeK;tbd2(HRCqb%?X{OluiU;`L5{y?i<=*3>-=|Yt)#r?>eMPePE?|JU!9hVaW<_J$2n4XEpLSwC%J98uQ&Ru9fphJX7t~(T8w|{Y=y5k`b(?Vi20mO;9hN$CEnLhnJf5wP6@B2yd%c%TgH#4I_nMY?fo;vJg0n7Ao}+gUR^KxD_1s<{?YA)zTW$OpP$OlAMHDHe`(=L2j!LeO<iRFGnwM^P46d;^Eta1|L|_NulJ5KqK+R=xqZ8$Sl{nU#4Y~0cveK3yc&Flk8dB`&EzH5GCoh+12Ja5SbQ%$PQ~PvNbx<DU1qOsspaF_r2gC+^R%lOd>px+@U|ZLVm^Jg^Vjth4KVvQ4f6T(iwBtB*OyQ5_a&zfGI@JzrGoOBe+zz|*x-%v<;E@eIJStvrv7r3ST}54h1b@8g!4a{A7^`4bAPGPK)0_q`fCjp?&TXVn&%TO);+^}k571W?rreKJe7<R{ynnYG>;=S9#TemPlNPwU+<mIm?+-g{`oL-|II_U`g$c`otV#}`rLag{nZ0v{j?PhGtFNaQpeXZd!ePjw#w=2y`S%~cz*uNUkI;#xmg_l>;V3Gc_s`uAGfbR;s2H=4!4|#Vtw|&tFLSl?<*@_oDa{8G>_9@o0IZNP$Zv^Cx5hQp4vAh;ySWz6hBWTcfB&+e^Xp_3E|}xyQ;V^G<#|JE`GjQy|yu~n$NpU>^J;%pLV(U{QGBDmk{25ZE6+eZPBYM`FIwucG>5qypr*K1?i_rq?fdSa?+>d9;3Y0u>2@*53u+<tz48>b4NHypJ8`UUV7+4DcS!<%|ZS?tgl;rX+PzqohM7k{xi<*qrBSV$K8~-_o>-Ij??ng=lppV?^$<YGv)20POPWA?fjXgl$Wm8%%QwC=-woLp0%~SZpztxl$W=iETOzqd1*i8wQDs8$^OkQi2aPkt26Bm(&vnDQeL{%%0+q2uly+4e^Tx-a{S@|z8<R9anhs;(x-n<dMR|Do9rLCx{~rT_C;22>z6IQ?;o_~`$6w|KK6oGPu7{eGVx*F-|B5i7r2*dpX6SvJt_QBf4)8_7O%~WuB5yi(A!OUb<~&&a-4?A<z)XK9zRZbB_xEebE<Wmf+;S_t9Qjd?hpR>VF%@<+n!R=AHDAoInF-m0Dpb!eBN!RQC^OVDWbe|J#P=?m5Pj=lvgv#3i<QuEaNCs3n(wIZkbPc`==L|lYaV#Y5euA{+B#)U-O6875ltD_@(VM%4>V11C&>s_Z=er4G&)jG>cb{9(IuaR+f|U+NLQk$}7PkW#l;L9zRa@Zy@$>(mk{Hj2u%zdAr=(O?l<*=t|0KdH&-1Ue!U|=V2eBWIo2{qr4kz`u?ieC#zRGnSK5mhp+eU1Jm~kKQP3+4&>s#72fDCVZW_?5^Cx%cNP0~!yEfU`<f<vzb!Qh6aKPO9G~JkzMe=;&EEEPomk&WBgFV24l&Qzb7CEHn7yaRIk8?n6=|A}mLUE<pw5dj&j;tTlx6nPodj`RfH(G^@{F-!-G-N26^QY#$MVlh`ytxAuAT@MpX2#x)8}RD99re;z4sTLV}<Y8-PGT{YlPd^dyn%!hl=~_^*y*Z_SH(qOmRJe_a28vZ@MXO@A{ZHZueqLuj{$jZ6)cG@plq<?|Bj_?mHBVS1a*%5_n@DuC*Cf=Ig!l?6^dHk47lwd4A{-`_)$!(>V6+4t~F2_3B&mi+sKJeq{eObARLhCF_8gC%p0bDnXn1x*?4;kE1o7z~`@6yz+rZTu;C1Y3|=5NgTJmJ<aD&v)@a7z4!CQ{fOGSm-#x5`w?k+Z}aO8-7EGv)qTvz|8{?VK1-o}#rHR9mpBe>+luSB#Y?|E=cc^v!uSfxD|1rINk2XCIO&^2itDw-Ynd}#lvj5xa8h1b>~xUcxL#Y|*TSZUNdJhRxL#ZRXF(d}<ymn>l-D+_-9vfhP|i+roQ|i(^}37M+gq<HApNE2e9C(Uhp(W#bfR`D>7&BM-><CWoQ=+>yzTx~1*8u=T}XMkIA<q0{@S(TI%1vAw74S5YXw0X<&}s14v_ulH$6m-Z|oDSexcJr`t1vxlvifYaFP8RMV661E$}$ywTx7;zJ*zi&-w8cl(*e|&P{nWpslz*zSGZq{B6C&K75(k+eh^h*QqQ0&Fe|5TU<{qUi~<T^mf0-!e29ckJMPKdloNk3?jX)hr2p9-t=ok&9YlB#Xl%XteQwIrKHimKSew!x*19T6frLBzxpYnOGw23`%^?OeGX2&_9HKX+p)K-R}6~r0lof?tU+!B*ML7pG46nD2kroV0>!v7ig6=k47e3C5*Y)I1Z&6xU}Jua59)P6uObv<2l7WStL|uL845m#?1u~m_XGbG#ke7gaeZWW@MFjx$nM}C;Jru(*nzn*Zm-uSy&_PI_v!Tm@;q`A_&j(sig8C|dvHha<0!^{D8}`W5#UFVU6B#suHdhb`@qKh7~j%shhDXM?a`}FuNlZ%a4q`GKn8<nfS=N<CGyY6V6Z<j1Q`qt0dGg{0Pnz@7>DWAS+Cv5FTlIOH&Kl5pcogT7(a{b41N~e7R9&)G7Q`T{E%L)k>SWNa5#7;ayNK4=EV5AUc2<VfnxkQig6!gCvYF|lPJc`k<sAhV74s%1=$4|4ekQ|62-U}*$LbUuU(A14lV|>=SAuDv|gpi4d7DnH5B7tQH<><#?K(120sH1KrwEHi~=_UKcLs6$Zp6ea5wPR$Wm}A=EOKoufBS@kVnBT@D&u}t0>0XP>g#b`+|Fd+n^XXMaF@fg4yrK4<i+199RJ#Lb|{%%!zSty#n<*g3JdW0sn$xd>O^~BNXExWFR;QETb4VLG}hW0pBOFpXo)$B71{l!QUW{fRA8KjM?K;y&9kxe}-cGH;G-xMJ_=u1)oD(9&!ozEZP<$^T6MuEf={Md<Jcckh$Q~Xj_O}1U`kf9OOdqcW7IH%mJT7TQ+h5_ypSKBeTKZqAd$KA6$*LdB`kq724(^=YcEHmWiATcB4&2W`ZlwHV3JK%h5I)IR|_kZ5hbf;A3c;h0FloMq4^^7Pt&;Gm+_FR$I_s2L27j_#Y_7clDaC7u&~eMcxJ9MW3xG#sl?wPOtuY4MGkC4@93q$eG|l;1`hT;1|I0$XVcc@L*&HcrbVfayEDf_(kL#@QdJ=kSh2k@K9tXcqn)naxQon_+{ig@XO#=kXhhYz{8RA!Nb8LklEl7;8&3gz^{TwB6Gka!LK0~f?orVLM{T20>6&T1-}lqAs2&f;L*rD@M!QG$R*%6zzN8u-~{j(6yrp_2Iw_aujf&Wry&c#)4-qT^)~V_it#-Z<2n@MT4VvZ7JLiEcs+6|m}MIH7Sh=BFkXjD1G7v8-$5GtCB`2jQ^71#z&DY`zJ>7z$P_TkDc~E(>nO%+kyF4dCxfpejXeY7_mPvqEGL0~MH>4J#%qw1z$}x&*O10Fo$+d9GMME=@KvO-A7K0*aw3@J1n?E4am{7C3ONDHay<Al(zsqTUWptJX89KQ7v#?<#w(C-fmx0N|BSqZV!RwV4$N{a_!9Cb6ys&cv0#>Of`39@L@|CB`6ifU68Iw0xZh;_4l)TGKcJpp%liN6zXtyMp|Tqq(|;7SKGS>~@B7Rp`dHqZ`uG72*}bWL6XnNGMt^n(EBy<+97fU'

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
