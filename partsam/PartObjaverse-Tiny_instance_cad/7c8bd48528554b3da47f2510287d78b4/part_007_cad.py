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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7c8bd48528554b3da47f2510287d78b4/part_007.stl', 'relative_path': '7c8bd48528554b3da47f2510287d78b4/part_007.stl', 'source_sha256': '1b4d2dd333c64107a821ef5c8fd453b50fad63afbdc94db705cab2faa89410a5', 'input_faces': 248, 'input_vertices': 149, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.017718132585287094, -0.15614300966262817, -0.04434053599834442], [0.01772322691977024, 0.17698131501674652, 0.016782080754637718]]}
GEOMETRY_BASE85 = 'c$}q~2~Za28OL8hQ4kRn6_3aY3Ze+{h$qJNwjKzGRuJ`5_&iaO8x>qoxe-AdBY12y>WsHWO^DZeL~A|beblzu#H4DqrqeN#v`w6T@ALjQAG?#zblPub=l|P3&%W=oyYD{x><~TPt&txSzs@WuCLuA$n=!t5F+Y}NPs>=4WKR!YlA7zne8}fNLpMZCnHU}K!m`+kkYsy$Qd-C$DI{|4fRHdLWbV?mjI`NHW-U!iwsU{<?38r7!%v?-JJs&k@7AmDz%Z##Xqc2I{f|FSM+(|UU24ucR7&~BXG3{TBi{VsUB2IOVHNk4&>ZshyFo>KU+VzBw*DgbrBfqvxZ2=rZ4O)@Kd_SaCBt9iO1^Gu7td8~FMRdjSLgV?HsQqv8W+BDaUA)I$H*kU&*0le`)f4crLs*lZaa+AH25s{<$Yz@d|!qypQ<}W=e6fhE#(7W?|u9v<&$->fR6V^o-f?%DgWBIt&|6R+tE><&^Yx^=sM_ak!Nc9amsUR>2^9EzE*ta80FI;sGRbEFMs#N5jy{AdsNB?K07*xe0f{pIvTeP;<wf9r#v^teL#7@*Sx>nNAq^7UQhe2g)i0r_@Ox871a%WJtlh>#jn0b<4EvXdXFu1{fD^MH1xG*yUAy{emiJhKjicD(+bM-YN*Lq)_+F6^wrxmj@Am}>%aG-@o)I<F!`RFhg1A>Cgz1NFHI|>zrRVP{26@Zc47scNBCuN9a_Rauxtw*Cr>i@TK^_>6n~{$TpwRtpSpz~Qv8@oy3VTM2hG@Zw!wX2zQ#Jt-%sOwyKQ?zU#^SUNAYb&(EYXfU>#2Ec!c8OqKYXFzEX0Fd^xg;)|J)*^X9BOMt-BJLW+a0#LqcSaqk7tc`*3w2bWJMUJY1Id3ob}SG^`*pEBxw$_Kt4m~oQw8tlJ_<}>_VMW;w}*>C9h<``$k(=&AZkU_z;Uf}C?FO9}=jS=?+z8o2Lj`o#9sdS&ckbls9@}>SsbU$tI)tGP2lV0ypK=&WMt>5+wr2Ql4d6Z{%rt6_cOrZKBC9JBX=Rke^#TmZ8>;d^Um))Xn{PZpPY;pqCC0o)^idX*nihP@=8~J)vCS4!p{9nkItM{L$_53Dt4e6lg<SRSF$=4DO(fU%0zad}!{EetT&!^?mctuah*CG?hm;HLv`ccQ}BL0$khVu6>pGV_8_@l^Ys`qK~A6=n!t2BEo^4~n1>XK21m2MA(-)BD6B{inYPKv*FPvpPo>yPO?YhO{Fw5_-;;_VlxE~$CL#Ck8kDe`%?hU${Cczhbg-?%2?H+4En^CpJUbHK)474be@s4hvJzssTcu9wBUfBu2$l5O}Siq~8(3IFnHQJ1^|@+p4#IdMH-AEEkVdpvnJ`KLAV^^~(zucTLx6gsavC&f4ib*ex5%{q!_S@3WDt&Xm9+Sj6Pho8WG6!k|rIgr+k8YX=9Ow=po`bWD({W>iChnvPxK35*mINDnH+LJ)q58h1i`qq8IACgx}d2G2zdFp@KE6&R;wvytDqQrT{?H23dUorH)QRcnQqvHnb65~XM(ep3Af1j?K?)iaO5BvX4_tm)0(uVEA_q|7PvU?b*a-mL)f4F`x`N`#UALW;uMLq}H9H9AbMbUj{%ik089zJ)N#!X&gr#we(6xY9N*ip)3!bqB5?OiRNuijm$E=d(7{b}B9>%_dTuN@cbtP$07`9-<7{>Mr_rsK0t%%OGneTncdEUu?`_ZoUG^qocGy!yTTl=l5EX3}#JwOZu)w8d$fulO!qCv|3lIIpBAs!OuRmsB^jU3tQ998YygYuTEvx2?lUk>}P2<m)wiODX=J+2VZ9b*K7ci`S{{vHMv@{=$!qsHXTyX=42RAE_?MO?pw?lRUc=(z=Y@bBWgNg+jXjs^MGemHgY3Dq4S*K1wxwOCQCq2;bUA$%b#~qcr%|K1w&@Eq#>jcbM1GN2&02OCKd&MZBetlHp5z%zcywpS?8qQ969p(nl%Rkf)`OQsJ`_a~~yLM?RK5N`^06`Y0W~X6d8Y4aB!F_faZ*#nML^zAe_=N6DXKd`ll?_==agk773w|IFM+89u8q_fe|htB*~6)X#pPxsQ@>Vf@ABKFS84-7@!4>^Ab;Z|<WEU+ZV?qg426t+|iV3_sA^N7?RRUP~Wk_*$*Gk79Rmoh^No1YfrFQ7U{r+uTR#M!cnuvfabH-<$g=1-@eGqu71pyv%)+Z1|QwN`-IjqjdPzKFan0d0P4?6~48PVh=H|rH_)~Tl*;0Be;gvN5k*CXwz5g^oXBAB`@BJG3Md;YMnc~!6z#>`OnZ_{$yRy_rLmN?cI04|NF_h!I8sk$5suU1?D;fTn(;*P6t<kE1~h=N^m*!*Whw+DRc_B6kH6Q3@!$*fyRK>fLB8&fmeeS=tQsrUIiTwUIktW{S|m6csX=5csV#1Iue`<&V~*LXM;1KGB^XA27MQt22O=Wf>Xgupo73mz$wrH;1uveXg}~m@O)@r@O<!GXm9Xba58ibIMJ~sIJO?xIEO-~fkVL|(5c`Ma93y?xGOja8Ve2r2STI4f#3jW6gU9f2|5AX3ETlX4%`9U9y%7>9_$Yt1NH~EhK>Ta2DgHa0Jj3Sgbo9@1p7dTf_=c=&>>)NuorYN*bD3l9SHUWH-+{GHwC*x-vPUW8#y*tXdmc1;67kGHqP^){lW9V3!nqR3&4w@gTafyi=jini@{5wL%~bI%b>%+%fRW-5#V%iCUg`y6PyJd1I_~HK*xe}z$>8Rz$?Ic&<Wr?a6U8&oDVL5MuQ8$h0s`VA$Tn`4!jmz1f2>l0+&FiflI(;&;)Q9xB{98t^ludZ0n&jp^4y`;GWPP;GW=cY@EZOq2MrZcW4N>JGdLPE4Ujt7#ai)26ur5g1dk_Lj%B_!4k9+SOUKV?EroY+!5Ly+!5Rk>JM%QZVPP<ZVPS$Z3S)v_Jg(r`+<F-K44#P3#d1^1-LoX3)~#s4C)DP2KIn91$%&-K;6Mjz>T4ez>UFf%vn3!uyJ<5#@YCB?gi}w?gdVQ+QCWSjZD0MxF$pGV6OAP$>6!r1<d&_<2)a_h&kVVoEJhDGv~XKa|(1RbG}<SFM%#&&UZ2ARA@SLzPmZ6K{J{2UC%iKn#G*G0q1OJ4s-SroO7Won6vlbyd0XxoV^O?mC$_V>}@!&f)+4mFT`1a7BXk=#CbJzEpzr-oYz2$n6o$ITnsH?&R&jlDYT3^dq2+Q&<f`46**Tz*D+^r$+?O-Ym?E7ayI%^&Kt0Cu7S=3*MM!%o?sg|0vZmE0Kd&dpUia@G#tz|3_J@w1KJ%t13Vqt4Lltj4-E!Kk9TqPbNf&K5_A3({*ameL1sPD{8`fQ$P<pSe*Q>_9^aTh-;RgVl@_uuuX^m?&F{b|'

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
