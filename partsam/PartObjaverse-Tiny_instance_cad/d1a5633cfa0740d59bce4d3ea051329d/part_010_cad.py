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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d1a5633cfa0740d59bce4d3ea051329d/part_010.stl', 'relative_path': 'd1a5633cfa0740d59bce4d3ea051329d/part_010.stl', 'source_sha256': 'dc81dfb9dcc98c3a5eeb0190c2804ecb9346cda65ab3e87216d65acb09cea9e9', 'input_faces': 115, 'input_vertices': 75, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.03192569687962532, -0.165141761302948, 0.4857584834098816], [0.054415252059698105, -0.14265155792236328, 0.48669344186782837]]}
GEOMETRY_BASE85 = 'c$}q|TWH%=9LG<acJ0zm+nLQeFHKz5q)mEBZ%NZz+I4N$q69CvAzn(GZiBH)It#K1!KZ;f2rBMLqG-#u7x6{k7SbyCpeXD~99CFWeDlQzt>FLs^Es#apZpckKODZFeEQ4D@BD9vrsq91K2bUXBK_*>7gy_qkfTxf#A+sc>C9qgrR&^<m#ajR?d75J&Bvd9EPb*{tcuH_rOe7=Hk9;-MwSzys6VuPK6@#<aPEck*`<v1(+g);GL~OCy>KC8eGbP5qW-@2sQ(rJe?7cb3;8!r<j1Yd{rvI9Eh`H*4t_5`7e2|`zEBKqx_RN5aMZuJ6M3(E9x>M9?styZK7VS__M+3fSzce^jr!cRXE)sHwWq%D`$gNQUV6>hKR%cKw&?IbdEU2w_tz7Sek#10AD_G3xZzf>z3RXB)6zViJC1&o&lRsa`q{eur|nZ`-*NO);hA6ilV24b{oGA_VEfl^ZT_QI>%!-T)*SO}{qcnD3r{wG=I9eIvQIhs&;9oHhqgcUrQ>%iJin`a?)hs)w|ebWpG$|<Z2#P0M?cDo)058Yd&OBVZo2!z*FlF@^O*H|e(JY=d3Viiy{1p8>xDPhYkF0m-~M5}{QRqaOt1P;UR@WnUSBV@-j1Dh*ZaiqsvqUe`^5CRJ{iC6c0ZfGqTalp4X^6Ooh#SNpD(pu)2sC=ubw-zUO$iO{DfjR?7y4u2gB?B@fGg}!|Ut&W6}2NeWkCL;q~>!tM`~$uitN~|MhQ5eH!mu)9e26=KI$4`uuO#-z=R!=lkFEdj4nLvc1}0^z&tS-M{kHrG2NO9<QIr^mopFs5iY`pLXoxAFW?*y<01U9DA)@e0ia43zt$JD&4p6GyVT+3y;PA?;h@*v3eM`#wghbkHQ0F2p)jj$yT@>4p`%;H72YvP7cB2aGZ?6ak!i8guCGgc?6EYhZ#X!8@`L|guCEgG6wg;Npc8I!jt3#JPA*cN8u?rMUKNMI6=nY1l&V*!#!}6jKC4r7-d~;th)`b&Vl^=C_{1w*#&pNgJdr}2#=9TcnqE;C*fImj+}z$;At`iPs1Z*0v>_;$sV{L4wF$h4ExC-9AwRYMk}=ed^_18cJEcm1LUCCy|*Qgl4D}`S&%$K&cZYBadHkm4j&_@;bZVHIRX#EePln}2ZzWo9A=Fn))ipg0leggt#Q9K9$`psA@7A-;3je}+yr~cD%cBGGbGF70c$*H4Ig<BmU$oSgPX~Ha5LOM*1-*MEkm-0`5$8LL;Usu(gz=a_mj==ez=irfE(dGWG%c0t|2{e4O~yw!S(Px<UTk(Usdh%{N2BKyGPDGq2>SdncsA7E#=?*+?q>oH0k+T*}HX-s>MYsw`C{dFXPqG*#'

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
