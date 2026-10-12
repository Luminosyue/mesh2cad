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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/73fc1424ee9c4dd9bee17702aab2b7b3/part_004.stl', 'relative_path': '73fc1424ee9c4dd9bee17702aab2b7b3/part_004.stl', 'source_sha256': '83664e1f9285c2da0b2810ae05a9b06e3d60a9efd9bd7222d32c5cc38b0668e9', 'input_faces': 46, 'input_vertices': 38, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2224283367395401, -0.21564233303070068, -0.21300283074378967], [0.11898501217365265, 0.14327439665794373, 0.07952722907066345]]}
GEOMETRY_BASE85 = 'c$}?OZD^BM6uwE?s<m}Zn|7Mc^i8d%Tf?MSM1t6WP6jnKAQnZjpDDJpRg>zhuJoO{Sw#22%KX4MWgFE&v0r{`6SY;#ChhcxI)w$Nj%gLTDOJR>_dNGxCgNZWFC3odJ~{WCb8pVQue-nyV-j*$#c;W?Hz`I4vIJogYdzk&s&bF--P%?4I*|mOMi{>;T<CHy)`_)ZgRR2jEBD$Qifv})44YlCRj%~bc}r`HS9&Wvq|Yr~;qz#^Z+Yn|k2cSqHp8w=d)uxwDF1iFYb7X6>wXGo7_6TXBy{!+cM+Bx@9rZEjoj~s{&CA$;Ji(JQU0y7e<W1hx(mQD9neMAPCw#YD?5+*sV1yb`YlI+)fTCbo6?!D!M<CuM=<}avj;fxa~tU;{v5<DaeN3}P5!i<bk%hec|w0Il>VJQnZL2~4C=d`-4mJD>9AiU+_(DZIq1bb*pK+)gZ&gw94f#(wEi9VsrP?52<&wsp1O2F2mEFhwIJS!(Q==Ow}PmDk@*Dt#Et;;oZUDV5h|+!{#t``R2TWX5vS^bT>oCR)YEPTpqt<CMICi6srNT^L4UHm2>P~x<5+ja1%K!Kwhs7RIw{ZZ>JMk&@0cU&e7YWbXs8MMQv=Hm;QT(njCIaufA+~b?G1?6ngU%sHp;wicO&$tvs&T5aTE3{mRi5XIiF768@1mZH@?B|cU%3D=d9jY(iNrub?z|c^A-4q2DA4d{_l>nsPD@yJK=Zz{AT#w7(`w*w`D){vBs^KkCe%{6>~qr{Og46`4Ru42o-NY{WbUe`H}tkiB+CM#sy$-pa^-z@X&YYx93yQf8qWS!Gkrj?p^J2ABD1h)sT-k3x;GJ+=s&Y2>l~|%RGkod|y;075(PCv<7_;zF%tdLw~>>^_rxAuQVUf3qdwUdrc}!Bc2ixX@v3BPf1nYe|k#troWD-MCde&VIw|TP~j5wj5_9e=5dUpn8z_sVk7<rV=QyRMCO!hEFT%6LA)3S_9aYU9?LwDF_}5}#Ir_dWS+o0nK6aAS+g|FCNP?qPhdWtjd-eN;~3)^P0Zt&8yVA>8=0rD5r31>%$zWtd8TF)HOpemV4lU?%0}G6wOP1c3+v(fGdOkz$1<}`<b3JO-(t*UPN*=aT$4CI;bi9S0-fGu__t5yi=k3eM14SCUKxEoB3Bk_vHrO%?t)nADXro3Vzq|3)JfuRpVo}u'

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
