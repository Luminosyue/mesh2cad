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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2260799ee4e342398b64ab4ce8af1559/part_006.stl', 'relative_path': '2260799ee4e342398b64ab4ce8af1559/part_006.stl', 'source_sha256': '60295d88c9d553e5c924a80678482846c4b6b85a5e1cb533244acbf0262968fa', 'input_faces': 54, 'input_vertices': 44, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4925532639026642, -0.3487766683101654, -0.13525408506393433], [-0.09421350061893463, 0.01770070195198059, -0.007072508335113525]]}
GEOMETRY_BASE85 = 'c$}qHe{54#7`<KhgLPx8Y!0V$dvvg_uq-BQnGqt7{V17*rZUHv5clTR1~#&db}oS-yda2!1W+QFFk~bIq6lKb&obCUf>}hW2pW(vo{3QjY6v*w54UjdxnFfNni##w$vOA*`@Z+x`|i7`&tr{EXL3wpS?iWv>xpGdAep7J4u7zHX@fsh*wVJb!tC(Hi1IdX^*mp#g>|q_XQMyV5OhAHIA;c)b`~hkKx?o)Sl?3D8f^3n-(9~f<mY~9Nqw82&-06l3Y6)t0_9cZzYZI3K^a+pvrqKWx$u3#TFJyc;NcqSuh8EUtk!tD!NV^||8?^N!AA8jJHfvfOMfkc-&5j59rHo)ApAFscfj)ow!puC@&@Kt`#NU{o>};|nCtiVN#EbU7yR5}89&q^{RTUH-Mwlv`Wc!p{Uh2&@S>Dm;Gr_<FSyf#cy;x5tn1ed={K=`=-V~874`3p48Y&2t_9m4tODOVFa3at=V}#ab|C)lap^mhx6psZOYqgZ+oWHsWBtZ7@0-|<pK`CmUwIY#sm~bLg!tQ$Z{V-<A>XL-Vn59vOQfHyt{3%ts#4%9-*;Vu-*OoJv%11}QRh3G^!v@tvfs#V^y}Sq4s{nE_zKVM&HV^<yj{|-zI6rpr5mt5b#4xPt+M|T`iSg53g2`2W5l~1@Y$*Thf&Afbr!tx<%_64{JeqnmKVckq3#RtZ_VnJ{&e`-qWNE=UfFMZCI5^(v#R}yj2ppu(aLVXH(ty`ynf+_Bbb*SmCu>G^GoF2ynS-CuT=DY0j}F|0C}Yc4SD_!AzmHafOvg&tBfySBjW=#2N5^B629t9xQzMf66~AV@yTh-U)%mU@-4oz(htKo+U!`bF_4D(EVvQt)@mcze<i#L`=%{#f^RN(3O@53$NMy!Q%<4ooEo|REn7a6{zzEve?ELIyasjD=15q+pK`2AyHs@y`_l9&`E%s{Tx`aB)El3b`}B(UGsJ!Ck#Sn~3B;}Ljv($%!kIqbnA@%Fe5HGwl`(-te!B(gM_p~g6eG%if3+<w`d3$5@&CWt5_u0P;`8B%;Yi@H5QI)7Bv70fR*DsK8|5aGwi3sTinCF^jdFxe<FIo)LJ)d9@i@}sNyia{jwJ{kPY^nl*iJf?^aSEG(jqsB>Lt-L;>eFDFP`$Fzb8?TN#sX+PNlkOq(%Ly9C;kmI2;@~9FKA2a%9u*Q%UC$vT<xAgq}#8OImOy=}E*H#F?Zs={Xt1Iixd4N9zmiB6g5=P`@tXJkl=GA}^m~GRKnyp|gk|C!Iw)ognn198)-)98VA{q!s#IXrIRtlWzT|zX*R0T^!6Ye;EFnIrj4#ojJ&B{qZsSJaOVZ^8*^gmWxDjde}o`wAx$'

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
