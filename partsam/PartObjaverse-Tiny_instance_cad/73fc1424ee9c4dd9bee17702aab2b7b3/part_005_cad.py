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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/73fc1424ee9c4dd9bee17702aab2b7b3/part_005.stl', 'relative_path': '73fc1424ee9c4dd9bee17702aab2b7b3/part_005.stl', 'source_sha256': '7a3e560a0d77748651c7c337845bed282102e3e1a9bc1efeaa27f5065cfbe7a9', 'input_faces': 42, 'input_vertices': 44, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2224283367395401, -0.21742838621139526, -0.31791356205940247], [0.14052771031856537, 0.13725674152374268, 0.03402376174926758]]}
GEOMETRY_BASE85 = 'c$}qGeN0nV6u&KYj;iQN!HM7=2t1&T*#ON(Oz3nU#ENT7HaC~dBD51-P+A1kXr2;<EMoj%evmNBGPjIPm@rX?LhV3g1Hp~`<J2^M>?4}Y_=jf6Mt1M-o^Fq2CPrU#^84N2z4yFx&ON=)<&2tOW%5a8^|u=~1|~2jY%;U5N{_FiwAkaHQ?_n{flY%ho(S$+@_M1`Ed#4$o757Izu2edDe8Rh^Qv7@y=#3HzM`@fYkegip}$h}p5McD|Ei*O9zM><&9y5znRaEf@~DrQhoIC|5B6{jZb%ObboAc;N}&5x_kh6g*sX5pTR#l}7uO7oTYq%ncLFt+p&uCC4xObQY!axfo^=l6nDmZ(k@_`LC&s%vdVymXzZAN=$%g&zyejCLWydk0YlWBLFL)zEu0LIe_dD|J=LH7JPkaM?MK9uGyVo>}eXPxiad=}E)@ipceTIEDdq|&GFs^SH^Xxzm_S+hf4-2m>1-`r*>$LdGJ@A`Q&<DNp4d|?3&QYNUyZ%C4+OmQ(&^!FdCpdRE{3-8bpTxLk<ypkh+4uv-KfQ1Q>*JlLg`e=Y*|HAFOK}d43t8V{KD2%W<6o@M*{UV2sOQgK=vwO^ZO}izc?R+1Y?0@(=<62fKXwLD=ajxKj4LchFkk409{hb7@^_mqd<^}@+j9MmyNEY1@7_mxKgt#NDa3yz`!Mw8J!ggP7)U*i`r3yZq1RTUF7B%L5vLOM?jhiq1?QkGuSFfS;k^fdubxMp9oL&=o!a;Bho6Z<U3hPc8T}f#Inn_A`{pn5_4V2A-i5dt(h!eQ_L{8kpkoW>Yj(<f=XS_`IXJpVuZL|P$o?Ja_oDyq^vm_?C$eu_W7gn(Ee!s{FXhO3mV|1d*Hv}P{+ls`d`!jl$mhl1;77BZlYO%(_7KL$M&&sbBwvL7;ZPIyU%iC$Wya;u9o}D$AdaPZ=y#?4%~9l8UV{FM)H(3nvv{v#L1JgVuFlH5JF-vq-9DMG>np9T4gZhu@Sn&h(x1xa1%o}Vaktx~Q2p_0BV)p%`R(Q{(p_yr6i)>I|7t7EeYmSF`?0UKcpk${ZgJe6<~E(%EVAiHN1EU%gjV7y#8V05h^G=)2xk&kh(E(k<(A1UjZE+iZdrsj!c5}P+$M30B7Bm#D5JQaCz1&s!|f@;sf1?YGiWY>a4PXMno|iAh^xfY36qGY6Q50(NIZdjCJ|bQClOC1j3sX3Hihyq5|6}crnP3$Eo4(@e=PB7geKwwCleQ6&?jW80S&}mPJ_`J^`KAkzmJ9u`VaJfcaCp&{m!f0*FVkga+(l_k^jm$?h&WO{su->$fE'

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
