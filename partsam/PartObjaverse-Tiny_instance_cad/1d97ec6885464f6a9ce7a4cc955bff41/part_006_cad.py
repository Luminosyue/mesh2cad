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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1d97ec6885464f6a9ce7a4cc955bff41/part_006.stl', 'relative_path': '1d97ec6885464f6a9ce7a4cc955bff41/part_006.stl', 'source_sha256': 'd762584e819eaf8bfd9c84a22e549c05d7139924ba46b38ae85e8e03f6105019', 'input_faces': 56, 'input_vertices': 50, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[1.3602360486984253, 3.9643843173980713, 0.05194332078099251], [1.6795014142990112, 4.108766555786133, 0.2861615717411041]]}
GEOMETRY_BASE85 = 'c$}q{e{54#6vtnGZR>vjXjvJQy)m{9){T(~L!7L-pkgEG5)n`XuYr!S%??`}&Y$%Ue-VumLR=(j4HAQKi!PcuH{^|ibGXScD4O7`1l>#kr^FwdV7&Kx4$6!sMsIU+&;6Y9&i%f7-g~LfYcksu8U@Nl&o`C|i=s$NRcuOYAhd1E#z43{xV6ooWP;0adET{Z^)0@22BlTG-?b?a-WYN%Q(e{dOI>c&Ro@cY7V-x-w1hSVB)`Gm91aK`Zt!mnh;_;03b$H0->p8V{@0N#B*Y(!{a7Pr{W(XbN6ea|q+hP1Z+``@S&iWFb*J8!>-gHQ!Q=ZYz!mGfZn^e+U;Pv2&7&ET>&NqlQ0G)F@iR9fKk93LO|F&h9pI6Es-t-a4k7RQm%x?H1>pL%`?0Um_cFL%cpd49T{s}us&@!n9gSgMt*&YW``+;d)!A)BzS_L}DDEfgH0inEqkVUJpg(?o`OnCIIt4tERW=NLjVp-1vYzyRJG%=y_GsW*C+X3h6EWy8Hi1XSuO@!e*b!V`+f00NCFx&d!u@K!kASNg-O%r8=sb@6&<=1<Qze~qd-nkHPdr6+rs_yfWt|S4!FNgLqD0#F&C+A2d$Jc?|EwI`(_T4<y7>pe<Kt_ozLxYJ>Zcu|`lAh0rzocrb?=;_I(yxu-@XLr8Lj$_&S3_fk3QJehx(^$enGyejPj4{L%!#5EqLTS>5P_`(Jy_1xNh*1&Q2%lC=YwV<Ja`ye4_XIKF0L}#Ff24(qHrH>sar36kPpoA@#jyJNAvVK1uccTtD*?>TACa5O;5&=OM*-5cv-c)4pA4q;pLN&Qo)KLi)89;-jf=;2g9`;?Lhs^%F0lFY2fENz^GjO8woJM*2q_;EMBBs&m^go`*=m&EU~<xpbZ#g&(2L3qIoJCaOO-`7P+VuLIokViDzkzVkz@E4siV7wLZE&0{^t|6z#otH<d*-F}wN|JXTj{jSBN$FuYU?6-1)_Fb@=>YRB3_Z2^3o`SBC6{P26<6*4F)`Q2FC6S&7vY}sZJOHlUlTZD6rkI|?^nS{>ucGr0ztf9#^_Sq0$E#@Hwr68CzG+|EzO%!1s!41q%qqUN_5Le9wGzs4dH(xP?Ut+l-KTcR|NhjPg$ARrL}6y0lbOk3Vc)_rISj%Q*iYb?Wb&4*>{~e|S(306_ER_}S*EZY_H#HU*=%8X?B{VzvUxaO@(Va7*#cq3>=$!PvT|W1?3Zv%vW3D**)QdoWQ&BAv0uh9$tr}o*>`hH&hv#8vM=W%W-i%Z_EnBaHdk0a`}rJ`%qeUZ`?EME*$iP0_8lCPELE7DeLKfexo_F*XLBr>`<B6e2FDV)Z)xnOam>PfOJ_fwV+q{1EcUZFX63%w*tc;kh5MGvelEvyxNkGrpUJU2?%N#p=WxvDH5hHCfBGx)=ZMIMZrUH4zg{{0wY>7mps4l7OX~Al@N65!?`|;<%BNHL9jbk~S^'

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
