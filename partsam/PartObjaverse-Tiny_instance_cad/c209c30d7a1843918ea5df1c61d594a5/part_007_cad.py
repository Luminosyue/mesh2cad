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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/c209c30d7a1843918ea5df1c61d594a5/part_007.stl', 'relative_path': 'c209c30d7a1843918ea5df1c61d594a5/part_007.stl', 'source_sha256': 'b6a0c35af30d83c84b76ac3eb7feef2dda5460454aea572e7ca156e159252287', 'input_faces': 120, 'input_vertices': 104, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.12187589704990387, -0.05060279369354248, -0.1466505527496338], [0.10261686891317368, 0.14566916227340698, 0.14426428079605103]]}
GEOMETRY_BASE85 = 'c$}qJU2Icj7(Uw=t~j<S6|DnyP_WyWV_nCXh_;<<1Ik9n7>Ivc?M{(I0o#EZWa*Wfc&CXPV+@&r=mn7xj6WpQE%Bb1XylG?LEw^TxHIv4PoMAj_WeE+qi1>Z{PaD~-kqNF^;<LPx@BRfa;$eg&Yx~cu5cWxMknl?^a`^_a$d3f=<&B|oEG1wL*s{IlcSkKHO@)rRCLBG<_ghmZghKoAll_d^T!Iah3wI(V}%)y{Ne1YMNj#~SF*=FrQ2gYeO+$6qsu+*{>Ou+NDju!Wt!!+%iksl3qLKDEq*Ea#!`a&-+13!`{C>UGx5<YzJK`VMZf>oKNrguzw~=&m0#L*cFESSeckW=lDpvNe0J+AA3vJAX!Y;TEhM=A=Bh7!e7Ad{Z1dl{^L17K$j!=i*u0_o_i8_PW3j6L+STuTKl=8MWsC2m+bVzeiGlOB`3)cQ2fmo!@G*bji}?*7^9R0|U;29f>EfNUzW?cb<$b^Uho5iwzx7&u=V0ERv$uVT`=uVtC-MVd<ZEB%2mQ!D^TF+T+x&))eCg|aqhI99`3+y>%lVCd<R>>q-?7ajec3Pbr62SUHP2e}g)jS!eBtZ<(uq@_BrMn8@Ns>luk($5kuR^m;fs7ZztNBU>;3P4ZkylmkuQCnZ}f|NIltkHd^x|-udh$+i+R6Ku0PV(>yP&3`Xhb4{%BvWKhoFhkM`yIBYeI7T=#m<+2%KV%pdq-e#6K7fiLDae9RyCVt(ld>*svKdE5PC_<DU4ez3mDe!YIeH`Y(-i+p4Kl>PetNi|%sKEKk}&zJCn=S%jBeB=3*zQ{M8U)hg*cWR;Xeu({#^!0uw@WuW|`nrEQGW3J*i~W!E^?pYCa{nWJzduv8`#g8)=3RHW8bwt|?LPBaw)G^F4vqG$=aIgDxApAp`M+Dw8jPI<PJ`E~s#EncFbCeO>RweVfg$h^^nJipj5k9QKFIh=Xu<~=4?%~JLHvNKeRLZEC%`A5p9en2_yK6bml!_?O*qB)1oQ+lh>xgxM%5571)hT51xzzO0!_G=@gZo!QN~lyDP$1uQ`Mtt3or&AgMI=yz<3`t;daKiKodU2cnms*4B~54J)~+aFajQdUJrB`Ujt3Jf$_D_gc});Ku3^4yg?QHAJhnJ0>2-+1=s-Igx6MsuYeBYyw$)a@D`jK1~!8CtLjy?6&MGPLq7@J#&|z8;nR$7g(gfe9*2%2gZMI4Gpg!=9^>>{9=M$GdT7FX826wF4}-5$^{}coU@Lel^rOH>7+(iX_!#4D(1cOOTcKN#L43cejH*fCIQTg9A>gx&?}sLQf$>Rb!WS7IhaN`;@uaFjRXc#g;JcxB0+Zll=-CY%1mA=6#(=}%J8|wF;12LkRqd)a0Xx7updSZzG2RJH*v<GRXu{3lnRHEUxbC06+W7k@`3pJ!qC=ip{jtQ)oKsoBhg2qA?|(Gas-M>tUZW?+`3uu)mZ$'

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
