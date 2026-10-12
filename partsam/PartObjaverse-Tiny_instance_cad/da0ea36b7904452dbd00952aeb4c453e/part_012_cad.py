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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/da0ea36b7904452dbd00952aeb4c453e/part_012.stl', 'relative_path': 'da0ea36b7904452dbd00952aeb4c453e/part_012.stl', 'source_sha256': 'f18fbce2ae81e32de2364cf7a4c83c36c441645014bd1f52c526f3d1712744b3', 'input_faces': 114, 'input_vertices': 122, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.12770047783851624, -0.40779703855514526, -0.402138888835907], [0.17413656413555145, -0.255174845457077, 0.17704318463802338]]}
GEOMETRY_BASE85 = 'c$}q}ZBSHI7{?C?il9Y+rGm9cwOWLNs}gD~z5qhJl#-%`5G+C}AWM`L(-lo72b-oo*oSb?Y^EH)g%Rb*ov~4~KKMeiYmKc)HVnPkSUP>{oV)+$cFx&trl~vg%>TFldG6)j^E~ICb15&L5S7G&M=Be+arNZQIL1UwVM(mr)7sWp>+xnZwd{;w@s=+R(sxQLO3EuESUY>gS?BTAwmNeh&ZYI)&UA;fzPYunwWeuvb8DSP`1v*4ydLg*8){lS{P&#9tgLj$g1PCA4#$5yV)-q&JJy?nT#c_HF9@x!^q&^WI`S>w{lnYCLIXu*r!4=~sGxr?aNhDOKRTT&&b#x|pmm+mJyyP1vg4HS-TS`#+&a%UGGv{1vf}cf<QvsJif_iB4d!2O^M&(`_Qi_NvP**bJ(*$sz_u~v`bJej@H!`6_J#8Udk?7h(;f4fPzUax4aN9mpPtM7`OuK;({t(h)$l3b&F%~+&wF^HFPv{&Iilp-<Dlh}Px-8G|A0I`M!}t7*$=!2e_@}JPvfTNo8(jenSBGwxOLwi4(FRUgZb_&U6$WV<BxpusV<anq+IB?ey^W##nRET%d#JE{N|T^_WB#2DEZyHhGoAOKI@$IjqKak(elZse0Rar<8nV39~Agy-|q9_+Do!e{h;SlKTy75L>*V^zI=sW_5&k9-^^)H@_VW7T0Zpy<+G$Sead|Kb&g;5?S9zbspQ-9NXxhT0r_s{7kzSl*-ocl_U-x>?pE?ySFlg?e7k>;&pKj1R_bUj8<KsyUgTffbxh7T{o|Kp->$pn)BT&32mG>6_s`Ojlzh8hd;67qs+V#5)<xy|R4*;xp1)c?)r(DgSG_*!WgbgVp9^)-^Qm5XKJ~MC<b;xM_p|R8<$kE2^?bXZwS20tKAu!xdpr;SemHD>;fK`s#_faQ`i*?O-^kbdjr@>)bB!MiJ73_3%op<Y`2t^`FRb&Ao^bP>e0{!?ug`b#L*{$K#U8o7^!_1Ve_xTWzpu#G-&d^V+5x3r^j?LpzdxDle3x7=d%b|KzyHY(Szk2Y&Tlx>CD+Sdzu<?gcjW8q9sH2>E@s^xxn8vX>b|}H!q?Yp-M905&+V4$Mf(Tx_5B9<`hJ6aeZRrxf9RFR+1@X~*Y`i{ts<|||C+DwuNceOqKuE`hwR_ZAFWgRQ1kWup=0dZPjkg{eO+tqSB-Uv*8Y=?{b>2UBXPm~MCtq1{xdNC+JL2J*IN5k+TWVvU6${-9--`StCNd@``PQWv5&3qlYQg+1;P7R^JZVJ<oBK%wXSbg9qpHW_T|>#-`%jcf3RHnTKKc<>MdV1e{vp^`PV{yjr6G?Olw%6;Xf4`UH|S=A=CALKNTWy+b=-dz&m-o$fF%9e!s-S%cGUY1ZX6<k;e`mTcHi$t>8`2XTY1lMbPEoBJfJ+gW#3m`Ov$-^TE@h(ctOeIOyHrIPeUF;7sU4;7sr;=nC*Ea4~cpxETB_v=Q8h=NG(P^a_u9gy6N%Qt(=^8~OxTXgb&po{bPZ1$r-d3OEWn85{+k3cU|3^fB;Ma2hlhoCeN=mVxuY70?=R1$YZ|J9rDY1zHbo;!(@vd4%AN(5Ju~!K<N<gI9wWBLvTbI>Gb6$<TYi$>3P%L~ty4CNv&A6Py8k7@PrK1kDBuEe9_G7eb!{7lJoHo4`#N3&B-9w()322=+iXgFWCi&=T+(@Dk`U@DlJ`=%e7d;6&&&u+SKAB6t!s2|Nj$0DT0U0G@*ooC9477WyPO2mCZba2>P?T!pa^oW)}S4;PP09_x7&K=Z)`;Dt~Z*oAWi-_OIrBL$wgZYuNva4L8fGzFZ3a|M?dM?@w~_@{p%{e2kL3t0Y#l76PToXBTp@C(_COL=j$=u`eej<jCDd1A!bUu=WlMg'

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
