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

PART_NAME = 'part_020'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/13cc3ffc69964894a2bc94154aed687f/part_020.stl', 'relative_path': '13cc3ffc69964894a2bc94154aed687f/part_020.stl', 'source_sha256': '13cc76ef9d16007e7c69cad25d30b79d3fd8616c2b9bf618ebacb08a436306a0', 'input_faces': 51, 'input_vertices': 53, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.16911733150482178, 0.07277631759643555, 0.060581106692552567], [0.16909904778003693, 0.1588411182165146, 0.3063845634460449]]}
GEOMETRY_BASE85 = 'c$}q{eQZ-z7{*UO_R%qLuqvO9J9Kp529AvcjM^F$n9E2Lk%XAZ?Yd5vm@!*I2AkxHU|fs}!}v9$EoOi4mtW~X2=TV-G7`aohB#wPnrOg(OpHN9{JiHm53(JrF?yPt=XamH_r2$w`<^!qw|KmMp+>d%b<ezoy+uOEt6ccS&RBd$S2UJb(cQDlB`V;{aZL|xdayOT)g^X{zCcGT5se4#FamdWt_jo`fzIvm9q~x_w(aqbnDp029!ta=Kk;a!C+6JOu5PR|8kf}>PZ<Aol*u`~H9YpA)V|33K}XE&;j>ahhj+oZpKM6O?_W6~HJNHv@x7_{<h?Pr^_)~I=~3|mtB=ZiJ5hNC{+r`D>4)}>A&=EJ19`+7QTX<=uOdE~n62Vp_bGpGn~L9a67kk+1Ea_@wEqO=_wWbf@L%!3w}*}>f7@5^lP{miB7Sc@@`UWgSeJMy3g4LQw(<P>BN@aWI+u~YIoSh0wBa-O#$XJ-)tkY3ty611!TJt906(7}%p$J+`D5@8RA$utoAF+e*`nTi;B#BWzleA{`aR;s3n}=?3&lCiqu={B^topE=7me6$iHsn9r*4?j;sAlBfp&;SNYxRl)rl|zN7WgPnf6q^WZV$xwr=Tt&LS!hkdmhe*WTS<=;E&UA*VJY+B_%ufF@}H^^^)yELupqz(D))6JhE{+YI6tapFS2<Df&3-w^^{xXGq>rW$Id_07B^Qo@OcmIQLKi!5r`P@A!kN=BQut0or$wR}z0`C<kYSg~#^E|2QPhXdL>L9*@zCY%~eaC|Z_S2r|QogqTp-cCpZuIYE{g8yOe_!kJBz(Od%pd2V?)3UGuWZf)3)EZkN(X$sKFzCV;p_Em{nD<U*Xlp?+iCcJIWNC^u^#<=3D*F8{X7~TUrx<mJHOtj^0o6GDjv_N{hZz(j1tcn;<bJfDs6?Y_n&-epNiM}m2X(ZPwj8vX<d8YmX`Lf-9pIA=XCAP$dr~XO*yV<;g;Ri^zT}B!~bsChBJp-oa<Izk^|Hla)7*?x{SP>Tu-ed*OMElE6EMyM(XY4MsgE%1-Xg5ih3J)6}gtWlw3=$rY<2@ldGtU$yMY<)SJnR$P1_o$x`Q$7m(*uZz9hp&!x^G&m~t<XOSz(<y0TJob09+lig%N^@{65vWr?oc9A{QQnH6!LY+Y_A(v5aAeWJ6QfHHAk}Ifwas~ND=L)yD+<wpB{jIq^EIHX}e{%FErys4UPmVab{yb>mmLlwt+xb22=y|z9@dq5~0tf'

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
