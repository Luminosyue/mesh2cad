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

PART_NAME = 'part_015'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cbb199ae1edf41c6898c997ae785c4db/part_015.stl', 'relative_path': 'cbb199ae1edf41c6898c997ae785c4db/part_015.stl', 'source_sha256': 'ee74676afd57c0b70c0ea66b9962af6d23a4fb0e2705e6de3c4002128f3b909e', 'input_faces': 56, 'input_vertices': 59, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.03202015906572342, 0.12832073867321014, -0.08332739770412445], [0.027102092280983925, 0.1937718242406845, -1.1500598702696152e-05]]}
GEOMETRY_BASE85 = 'c$}q{Uu;ZS9LLXe`cD<5LtB5^JFU)iYD&?fh~7n{(U2h&iQV3bPQz|PJDms-$;HzyUI-o#*FO03AQDMmJaDV^=Y^2XW;ZsQ+(=6|@xtqR@H^*x&$#y*iE!nc@7Jf_`SqN0r@1%L8O#qcd4<`vKX2YDE@X_Wl!e&AR64V7Pik=C{{F)ORwg*Vl%L(aeN$prfE{E<qCKg>J?ZF5ExNjQMKrEOdk>^D>E!<I1L>X==NpoJgDK*Jdz1Ys`hP=fTU=Wji)%-<Z@o%r3HtjU>pr=;cH@(Fa{Jx3q5CdwgIn7gChl?n=k_Jet@de;-F?L!aD6l)`o_zDFLKV>pFeW<71zP_jO^=Mo?YNvTYc`K_`Pa9;08Dwn=kq-@!`B!|EexeUvV4UIV=0-rZ<9HC!TuttGEMh{4e)wtbcVz^e3uD-SZW9z*%0MoIm=P;I?_jb3Tf*W0GsXL`7d)S0=bN@p8mHUvUGR-KmxRkpkIo-s+jJxB+fdVSXlXO8oxuD-Sp~RUh02x58n0{+YKY#d$YXJo21BxCyTPS}(s313&&I_BC#J<}0p)TQ4-xw+A`|x8i?$?w8^YIBS#h&F(eF#d=@W54-0pZh#v<)X4eWA=z)d?73fx8{qa0dB61C!DE6y@3Y<W6}Q0ku4-?;{K0U}KDbjP_v`HFH^q8mKY7-pxD9Ua#P{dq@BLy<q;ABsUvNk9C-Qzdr9(f9{YJ(-=dZW{ZXA+*<85Du*v}u=J?mH8RQ$C(PiyPCWP6VDQQUt%*}m_5vVGtA*mq+Cx#lbGpP%jf=4bo9`TErVPUo7h_-FT5_5Jr(^?mcLYxc#Q=K%iMIjFvSPQvpPDZ1BHq6O)ek|xnpq&Mk$gmB0&<+&dr`&z#45wh&NA0chDhLxlhq!v;usTsZ)c{ynrX(@aO@?v;1d<k+3dadx~$Z=8=-#a{vyoj`rR0pp`4#PEgEpi;aCio)cxui-`BfJ5bYXN@FeI9ZQoho=G@;vxlcqMWpdJEt&<OnHB3c+V0*OTUxro+pSXTn49GUNz)QFuLaHK~U2R}$${kmrzQGyWx$UW_~iUJ5Tpu12p0J_mUgse)7pFG4OS%^(%P^O1|-h46gjS?E>3%aNy&rjhdCLFCCK{tgp>GvpwgcM_d}yio8<uV|kxlYhYT!sh>^_s`P($qh6s`$wASED&#ZdGv39{Ho}F1dM+^zy'

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
