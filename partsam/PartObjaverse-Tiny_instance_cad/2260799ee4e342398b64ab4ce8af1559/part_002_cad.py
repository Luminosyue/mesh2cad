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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2260799ee4e342398b64ab4ce8af1559/part_002.stl', 'relative_path': '2260799ee4e342398b64ab4ce8af1559/part_002.stl', 'source_sha256': '9258fea4a61626300a2f4479439fec877bf41a8976058a58c256cc9b1acfad0d', 'input_faces': 54, 'input_vertices': 44, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.04751880466938019, -0.3487766683101654, -0.13525408506393433], [0.4925532937049866, 0.01770070195198059, -0.007072508335113525]]}
GEOMETRY_BASE85 = 'c$}q{e@s<n7{}ksPep`lUQ`tEa6u0w<DX!+shejZu)J}1<A+z&<O1GnqygQlG{o%8{8esYS<uFhU~5u}goYYOaQY)hQ*V*g%m{CrtH{=z`J?{O^}gTtp`g{)>TJ)x-}iH#_j#Z9oO9n@r#&>x!sM02_LN^}Xb)pdL^QLoT90pAWrfF|QB_lCVrFo0P3U1qalW&}#A;c+y2<0O@Ttobb%pm~HC<7?)xK@MvZ~T*-zJaXxn*1Z9?tzwmeqLpI5jgfU3n-iU3pIVuU8arK`$?QdnMQ4u9m=%7~hB-6sm1`?Wo|!cE<%VZvWQa5B_Y|altiv-e+PQytw6*<h{gKfxAZvPYX5bGP?!W^IRjyuWEQ#D9di_5!_u8_(F`8{)0WJlXva})~zw0$NbUReVCUQ0B0{Weu6$t&JR(?vGG0B&o1~B^FOxrBEO)m7yURQFCp&(+X<{w^dq>k>UrcVUe|HlUsHYx_4B*Yzc#kNPjVl4`(w>=zgMqM;Y!YctW(-_4C*=uZme7KCHg%7J^Ins`A%cM>kGh*?7MGCUJK6rE!eL<zH$KfH_ShS`a8-mg5P`GK>icUz>S=1Sl77H`99X&+}$Vn53--ZYPsLdCne9d;`y_)op{cA<?4R)^XRaAFM&?HM}2GJS>zXwe~$GY*^fSrr*kD=dkpVOA4o=h_qC|6(Eo7oWz_cu-UR>dMaiprj)0eDw4tAI+ZFI=Z7-f{VN5gfuLmUG<7~oug${7zr{u4}cU*o4>n<NXi0|>{;Zg7sy#skm9j{;?H_u3JRbGYWY(zcnmyaa(2C*M^&Y<MC?n{11+l@ZWzwSi+TXVhve~O`hBW>&u=H1Sge9et^^rP)+gx)TYyx08_>a34x#eVP9N?u{cx_a(TJSXGM5y?Hn;B57V2ISxEll<~fJ#<CJ>$v}0))>YIj5jdOA4NX9mvt3<H|s**Hnl^3FGZ5?3xXTPKQ~M6lDtmG^VD397U=!GlGm?2ihbJVb__YEoNks&tzFYX851#`pKji=Nk^N2;+oLEKiVoY|JBi!_5Y7HEAL?ukA*zacs$4>h15#kO7~MJCzZ!iVvDe4sj1{sDKCjMg?tiuF)yCS0v-vZ$>bBrFQyP)r4W7zh46`_3&<yupHCtDJkogbD$Q3&6UnQj6YDC}OFZd3iUg{iKsgg@DO4+j#|$Q3ybR&v$P2Yl%$$@Xd>DoBCJNyrNG;?e$eT&y$eYQ}BAr2g7Wqih5b}}a8Lh==eMUTtbUJzQxkmE{CygN=PCk}&F8NsUb9g+!V;Yayq*3If=)UkyyD7vH`cHom{=9TFJNXa8UuRDJ`AwcV#%ulYV|3cXBjjd7*fV0H=#2din{&a#'

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
