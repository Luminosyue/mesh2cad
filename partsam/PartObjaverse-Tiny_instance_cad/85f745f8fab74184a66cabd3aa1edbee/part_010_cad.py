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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/85f745f8fab74184a66cabd3aa1edbee/part_010.stl', 'relative_path': '85f745f8fab74184a66cabd3aa1edbee/part_010.stl', 'source_sha256': '0f22d911e03364e1dd7238d3a69181a9dcab2bab80178c23431b28b45e70c1d9', 'input_faces': 144, 'input_vertices': 111, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.23905685544013977, -0.20080508291721344, -0.2796987295150757], [0.26929718255996704, 0.49999934434890747, 0.33007797598838806]]}
GEOMETRY_BASE85 = 'c$}qJ3s6<p6+NK%L*oa*5L7NoL_rkfBNCMxQDOuIREnQaACZS*@y9dNmS}FG)=URtkXT35@S-&zMO2KxM&&AqpQwo>Hfl{I{TMYNMx9RD8i(Gq&U*S_>`bS9GkexL>+ZA9KEHi0q$Rg$+f%4tkjTv1(dkAfA*6K{Jw>6tU`gI=yJN_LMZfY8-Jr{#3(F>DOiY{ZAqquNNRHhxyC5W93mKUk7cy82$z52mq#%32tc3+RcBv<2=R53{?wFgs$ZoX<Mn*;s)}jUt)|P4i<4<Ox&)aamM&?qIaUsD1v$DBdq7n6m(#MSW1KQn3RMxobRZkz2y56<xeu>V2XQ3OF`_9X@_DZ`0vfUVb=p1yv?FWJSg<A9zZ=XdRpVW6Gn#;d0g&wf|W9Vz`zk|O$q_~BCwCGKVdf*Af7ruASz^~Ybe9SK04nI!U%fidiuj;naJ-1wf|D`+cV*GgRjGC8YFWM)*SqZ<LKb?X;(f{|--{${gG3Mo2uk<&sU&Q*XopoHcov99`pYT13IHlEF6Wny8PU($zvTC58^@FZo&N+d8(WC37F79WaMEge8T8Xwl`W=CPa3XXwxA$ilH!tP@=5gU_J>pMWUx)dYTsbbWF*XXi2rE1a|B0a(Uw^NI8gEc%#M8fRull+4^OI^3Z+*@#jC*lP9rVJ*m*H1Ea0B-F^eXs?+xcH0@Aw{w_fW66b`|S(qj8VBu0LqLhPc$lh-R#x2%d2TaU4}9*6IFN(2cu+r!gOIr&_<mKFa?_)w_sOy;q&nfv+5czA_Q}rw15YTj;aGu#O`4n^!T9yPsejJtzt1UyqrOc^bjzOtn6f_v85?$63r{g;@hVwE_F)teA>^+Lg^m)Osyd_ed+mI_g?1biHX3=4GtAegW&SDnjWSzJ{Nfk&k=hy!Gdg5a&$!Zs5{5=%(GN&ikS!8|L3{F6LqOTE7{7|1|%E_JhA7ug2&MoEzb}?JYd7&`%|}>(TXVkk5f$$K7>f$z7ZS^XB!F?z$PC+kkc3Roo)Jo;Ch+`2RBHSc^DqGjYH4d5LFQ<dYnVJVoQJ58VCr!%mfdU`SmH{|gOY!oS$F8tYaXrS!CQOK~rvc7BxLuIKFeE#~#=KdPZGKfVTfxi{*D7QLye#$CT$06$}y&pzb6(QmQJ^QKz=`3KO?xahSIc`iMo@_)bPH2i+3%|ic|d@z6G$4GULk~SFdJ5av`{l=~M1nnLDR{&qDz`3{eO;_h7|KjV=OM0Px>C=KXs(9_o@Vx3h+!u4}J*<P6`S-W*ysinlQRYBA!z*bM{JJ#Ye%JyR?8dpx-RVSL!`G<%zgn^n`nok+;9tEA_ttn}ovNcJM^(b#_Z;enxqKAzbk?RIp7^O8>+Cv*+Q>e8f%o@fU2M&PsEcNT<HLl<-HQn?9Yp+A_s)5-3A!-;H3~ZK??e5;dDKnAuI{fbtL!k^t?GkbzY)6rR4D3??y55-;p+a^?ZWvtzhBOMYgBrxI%X6OMcou_y%5h<_crQ*dE8L?oinQboU1v6_TjF`Ppn$K9e#1@eW-U|ru0_z(|Ieygq~iCeK8i6Vc*QVzACT%iKrV|^AXe?eY3h}y5G0RQ+s*Br&za@&*2`ouK&gtJAtj=7kbk@^}N9w=Ulwl{4wUYc{Tcr+@K0PA3mo9_wjb=3Ft+C!??!H*lozCs7k%BPJ5|(S^JuL|4*z@di*7ft1l17bM5s@(2Y$iYt=bb@9WmOlkaP-AQp8<Uz4Za3txY^19`qt3SBe~aA2QSSKwZ>)&;*G9_qgiLLC>b?~|)HReXo{r@)=+`$wx>k9sM>K2ZDUH=|hH_p?eLzpY%&H+?<g|7I@EpIMsnxjJt_*jN4XdFV#bHPm(e2akR3x}a{PB&zlOE(7~u+<RZWSMFcMIcxl^61r&rq1vzVvD@8sqaF34DeC@aq@M%6d|SOgr_WRIGB#j;jMYwj=NL(;@Ylj;tNL^;U!Bt#Hmr+t#~!6`o{alp>^`OX4g3q%%Q$vl?N{5QsKa{bNQ`4#yNr2>X{(PVq_y};4*%|8x!&G#wXCD{m7JUH_K7S-`E%jpKaumI|GQ7*=;;6V6FJ7p;W@b+#F^wBEeo`)12Kj?z%uz={S>hm`4Gz@ESpSBBbWaEmJKJ4B!806f{6pk{TXu<F@b!xW#N|nf*3|Vl<gOYx#V&?JS^)?Y(w6gTw@OXE$c$m$Tj*%KGw2i%f=C>laC`GPn<<Qo;-z^Pu`#74JHmDA51=$m`pDF&1c^f@;KrYau3ealNd+tLkuIvk;k#G<j-4{X<0hQOy@k(sZXb6avl<G<g>{0X*T91_e-9M9z;RjgWQKEn3o5!4N;J{A@4%$ME)c(fY^!Lbte7AqciC`N0H<bBgp;91H_|qID{BM?mExOv<R+E1Y@PsBDt2&lMf~KA|FZ~PV7P6gKH5^3=@ye^%U}O@~Oo6<ny`aQ)!Z?5;Ms&nNuopD7ovtNWQ?bxt8S-Gsq>zljo5q(j@Ok3?lDG-i_FmJj${pq3VjnpOZ_RNiKb4ed$Z=NG`D*d3Vb~*ltJOmlnbp5{HpX977&O?iyd>1mYO-3FL!_!^np*?jT}!^3IldS=NWxmR#Zh@;>CD#1Z5_vuvVeFVZBRN0WRKF_b)%eI>UG`F{oLPXOX*@*MIx#AnFokY^KP$+O9`h|%OTh%v-y@)+_CG|Ai3B=;u9l6#XsL41b%335N;XmUStU!qR#Oa3%X@@Hw1PqQp7*~7DEoB#ALsz*OV7Mm9Tuxj12<!jr$=KyO$4`1SG$zJjdS_R8fEVl3+RJVTv5qJWR'

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
