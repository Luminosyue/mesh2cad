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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/404f12ba60f444bca620c4405ef50bab/part_010.stl', 'relative_path': '404f12ba60f444bca620c4405ef50bab/part_010.stl', 'source_sha256': '3f3acb2338db7cfbc582080d45b630359311d27737698fd4674ade5c11e0b315', 'input_faces': 92, 'input_vertices': 68, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.36561959981918335, -0.17903579771518707, -0.21732956171035767], [0.36182576417922974, -0.1501515507698059, 0.3339290916919708]]}
GEOMETRY_BASE85 = 'c$}qIU1(HC6rN2sX%nNS$+{ZzH;I}}HtVL1F>c~dt{Pe}s7pbL7EPk=#-M22je#KIRr*lrOF{Z%3!(Uj81YH)q0RR9p(3=@B(xyxLxs@SK9tfI=gj@ix;s09=v@xqcfa$^*|~G(-ph>-mHGq1J6c5Y^8d+fxeydpA|R#`smbwUiFEYz#I#RTYn=|ptNRY@jUV)hDRDk@Jdr+@3iZp-wqz_6k)h<7)MRS(^zfO~@dWAbkDf{=l%75@I+0N4?Y*&x+|&_~7v$?6m1+u^{mI2S!p_(agzn^Tj|jy_|1Rir_XDjvgB@DWRNvHk=G<AWi{QOqwC~8Lo<4WS(*u{ZF2YOmgxQH*KkD-pPseP!o4o$nK%VZb@>%_?v)>t<(fUX_<@s;^mz=ZdS5A8Vec5XRmg{BR4STv=Gdxe{*$+Fv9I&hd>*AuPOR-G*<-x;RH`j;tkxA&|kDt)_%%Lf*%Nu|Htk*9x{6)U*T=#Ub^q|1c>);rEH-L3B{AOQrb-slTe|F?gt(*NabzXng&3?(Ts;>qteJRq>7g=)tYh7nb{G|0Ge_YGg-E*Fv9o+w<z>ojU9ya_~2lhLAo@qVPxL4Pa2c~c3>w@+Bjlb*bn!a+|=4ajX%kTfWZJj^#qWQDmoIm@G`Okd5bl0|?MLO0qbJaI%>!Yc2A6Ym1=q&cl+V&^w=Kjp-#{Oj8+@GwQ`!iR^*q<}2omt!c#kzTa$&ZI;ZTBzh=KbqF{lu$pJRev$pAVwp=)A2jMLPQ8`tHoz`eN$b7uL<bn0oH{*}G@K)-Tr0e&uvyot>qz1>1UNq7N5r>*j>o7mL;>UhsDO?wh|xe)S7MQK8<B$<e%5BZ+h{+Fy<1J+Jg??CXBxSEHmBs%QnS2X6&$0j>jY0dEG@gSR3lfz9AFwhdmw4dCm*>w%5n_23P_Ch%tDB(MRz7M>blBX|^byMS%rHSk1%8^F8ZsRcHHlfDri!U#CksfLH}9q=eTHNa}{2Gm>+Yy+>w*e>8kaN1)#aJ~bzh_6sVTdf=TE_jKGQshgKBVGmU0d|A?Fs2H~-b!FEum@aVOeK)Ln^e4~VkK}D_)ZlL@(yyuHv^XgSAy@tn9V@;ZUHU>E(hO@F<XG_4XNl*Q3niy$5iwq-;W&ewJKJtXa|PDD^!#rUxpm<J{4P0Z!2oWFeZ$A7&+o^tMH?qAGIow<8d*}r5(ZZ3SsVR5p@__hq_#|9CZob0;hRx!*vpNf_H!ifos5n;C^5^I9<nf)Z30){g^`#^9aIAJU-+r36#F<Q{lzo(k3eSa4<&}K1TCLHmQruJyhdEW%?_lME%av1?qo!4v2DZ$^'

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
