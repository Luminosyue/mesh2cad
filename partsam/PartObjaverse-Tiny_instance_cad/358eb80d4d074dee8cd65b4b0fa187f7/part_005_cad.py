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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/358eb80d4d074dee8cd65b4b0fa187f7/part_005.stl', 'relative_path': '358eb80d4d074dee8cd65b4b0fa187f7/part_005.stl', 'source_sha256': 'e8c880f405790483674ee321f9a856a2e98d200503c4c72ba35ca80703fbffc9', 'input_faces': 62, 'input_vertices': 51, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2063674032688141, -0.07737177610397339, -0.24799123406410217], [0.04267951846122742, 0.2625757157802582, 0.2852219343185425]]}
GEOMETRY_BASE85 = 'c$}qHTS!zv7@pmAuWH%4uD8<F($!ooExQry+Cv1JwFNyCiEg^$rM&E#5D}iIsHk3|(t?sMP$oST^klh#pq6RvqrFH3MW6<~)kDq9`OfK_VS}iFpYNOR|Ia@&-*RS8C}>J?5qT7m*NM)Dd(4EeNFy%NABpz0H%DSsT|K7^B!la0D0pSxq59Ba1L-HHy)BVgbJV-T<K5Z1&Fk}cTf3uu(QsE|ceEwK^xfg(u?W>;ZQ-5>otM>C`#hV<eV#L(e;p3Gg@C`~)i~SB-PxxMJrma_{2Dz_A?xJZ(#*I<mwMmG`h}^N+IsSRhU<aK7jxQr(syi>;qc`#z24Bo_4v_2-MZvNBiE%P`gO^V23aqj)~zdj9voxy;jMa|G!1cG8hEZ-SL(dM^?0ZLyyT;-2ZGD`^FGMqeHTvZ&l^9G&*$;cMO}TML)OX2HGTgt&_BsOc&s-klliacqW_96`mgp8{8x3se^nR!S9QUERTunM_apeP)(ift^@9Iuz2LuEFZi$MqW`LIg8yoN!T<Q3p>eM7-#*FLy_EjWuhHX=WS#ij39TMj4o>s^j0pPTUam{$(I@u!8P~u1`MOfQpdYN0&ohKR(Br#oQ@sACP=8z2$t}5l;p(|3$@;6h&|lHT{%XC@Uz)GIm&_kU7yVIm(H~V8{2|%%_j%vJi8+4G(!zvRkH437DYH(eH#uhC^8N#Xgg>Oag_kaVNNqC_!op5(;nuL`3T7f33MRjT+c*E!6}+Y9zpr2?-Gh;afkr-!R2pue1w0oy7tjrEM=k~E0%y;rBhPRpxE(wfSO{K-`5It4xCOnGo_25(_L~B<fM+7-0;Yf)Fkc1C1ka&i!<lSYgYj${PMp(;TE?x&S%7YEBXS0y1w03JHlP(ek46^qS;#TY{twN_n~`ID1z~^Zay|_`7%xChsd0d(VZItz0B%KJ8_)r6#Tm>%0*<c)z7IAsz%wv+0*&D1G|FgH0M~<iX_V3^0j>jAa^=7h@G2S`XcPn2f)~;7(5M9Zz?EDTuoAqQ#zq=7G(tgx(PjG6r_%2su^&$N;Uqq(f4#L&o~6Cimpv3TTV!*Lq?a9x*Zu+%Nbs-'

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
