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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f1150d2342a8470e912942c49e978f28/part_004.stl', 'relative_path': 'f1150d2342a8470e912942c49e978f28/part_004.stl', 'source_sha256': '7cc2e88f12b707e1825e1e9fce4a7b6ca6cf7b300ffba0b1a97fd63bdfbbff9b', 'input_faces': 56, 'input_vertices': 64, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4739833176136017, -0.18470332026481628, -0.2110934555530548], [0.42393550276756287, 0.4765872657299042, 0.4620301425457001]]}
GEOMETRY_BASE85 = 'c$}q{OH30{6ozk$1yKYasDO%7L0Yl$kcSA>*7pK2U5JmkU@8>B_`nv4hM3HfL>3wsu1qj$q9$ro(8MTKG@9sw6ol|j<3cwkM%}vbKK>b}H={9nlav4SJLjIc=T2wt1ZtCJWfC!*<Y-D}u9i#)vow-PIzr+0*2Ykz=tSFD8=22J8@gWFQ(qT2Xd@k@)72D;G=^Q(ip$$v<?<-5=9A&}aPUOK$#7GM@twhAkr3sPmS9_m{&rWEdz7*@9_5_!uVW5fg3@0<^PH_^+vS@+D$$qYZ=Rd^4)7JDcM^ERmwT4^LBUC`$XD-vnC4o(Wr%T2eZ|$_pZAL2U7uoRt~Bl*{u9?`B3z@<_f!134zE~Gx|grV;3<M@Etl?@c{Jo6WZa*TnD1{ETstcAwS9-DtoFy?(*77++8={U`x778Ho>od=sM3+tKW|MOk4wxf4n$t=Kkri*OvUpi<i8fyLu>rKifaR_iw~DYUbqXfhSCRkgpyu8RvYL=t~<Yidk``aMf@EZxns0ay~dgJ{kNv#(664*T<Te6<2QshRi&Q`_hAaweU&Is*cR{Iy#r@#LsuetooI?-mk%>er2xrt32p?=rh;vDvnuk@+dDcU#~CcgU9<szINkwpU+|+WUlXn&gFd|zW9(;9hn>V1zfHZ)x^5wer2xrYjCMwnd|*Vd%utHyppZ_`u^pPcl>{S|MjR9k4`=n&l5O#{7tMIyr-c~T&Ls0u$e0xPxI%>fBQ_gna7W4Gko4H!Tr5&IG5jV2AAG%I+x#XGS}a4>UPhB<$8+xC#?EX2b_~ued#=5{egtjYoPnu6(xyYidrf?y_$ojql-Z{bhSRZTFd|H=&Gpv@1tu2T|))?8$vh3-$bpPnwQ#oYGu?ap<ei2<S?I|#13jH&{^<P;MYK_;3p$i4XuG+g}jYW2YeT`)znI%#qbNL<s+Vtm<utMQvxl5?=sCR1uH<j7&VGfhxu-5YpAV-df>aEh0t~Iv#BkmmIrmh&!V;j@g<05BgS%8K^6Gfrg?c_S%^DP!-+b~&!M)A+6rhc{2b_V=t}r@A_o43#0Ec|uum=#PeaU(7|Y3k&Vz3^%}WAHN8E-QHq>E0`&ODwZ7wtw{$gs2sIkXr0kwtH=2HvQ+U%K0zxy=&H8g$^^M|55Gx4!B&+MnQjE6K(>qr(&+sP?*BiM?`Pl+W|{{'

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
