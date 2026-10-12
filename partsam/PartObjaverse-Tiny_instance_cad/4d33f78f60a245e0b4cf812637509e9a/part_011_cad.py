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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4d33f78f60a245e0b4cf812637509e9a/part_011.stl', 'relative_path': '4d33f78f60a245e0b4cf812637509e9a/part_011.stl', 'source_sha256': '079db0455c2d47f118052cc6e84fe6c7fd79c4ac32879be4f0ab60754c97bf4b', 'input_faces': 169, 'input_vertices': 131, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10459752380847931, -0.4743637442588806, -0.14784783124923706], [-0.10221698880195618, -0.4713728129863739, -0.14571139216423035]]}
GEOMETRY_BASE85 = 'c$}q}+fP(S9LEpf4aIuD^kRFw;wpk%R6s7PA|fa*C<thA0e7pb0$mUlYTf!TG=1qqV|-|g?vlndrZJ5r#u(EyjcJ;uF^wTs#Wa2EOV3-+ET7@<8+VhY-DL9p_{lJPX685NoHfvpHDjqY`B`m!cD?SeM>&?IT8_2U8VW@RPxpid@_YL)WmpT7UVU_a+Sqb1(4JupStGe8Ljyh0+;Tg&B3zoAXXl3dqJz<{-V=S%lOg46yUq@TTt9HCt3Txadt+g7VV+&=%d;=r|M4@|y#)Wn!@J+9bo@_Mj>R9|S82bxkFQDkYw-ud+fGH&Tk%IpAA4~x>4Q#P()$x*!uy@-$^MCZ!rM;iWdHd0NgsT9m;QT_emwrI@V2v4jPIYglk_p?fEZtUzf;S+?h0=^JCZ&Yzc0Myl;D5hdv7zZ`bmH58{z%VF4o~|!&fn{JHqShH^<T6tJm2-G0MCS8S@$y`!as(w(xpAz4?wZej(%k$Ufd={Da~;wGTS`#Q56V&Ni_x+I!<aU|!c5zuDNw>ta2};$I1GIYlY^TTVXxA2Y8n<odAw+FMS6sOR9z&qbZY;-mQCq#tvRQCB}3zQd@`Va90__2c<gvHqTK7VGKxLn*IEua6zSDZH*{D}KZ9lXW<D>r3Iib9%$@`rO5Z*LCRai}qWMy48M*IFH(o|2^qri9Zd$nem^e^!k3{`AzhHlG0m=pV;>y)?u%hujl3Zc;26~zqvlzo9h#M9!<Gl+MDBRZ;r3Mxz4c{z0^sIs4LGmi~83-=roGD(%xJj&sV4MRcU;=oG;#X%H+K8udUmZ&o`b6+UFV1mtLcO9#anyc}}O!ulDW6{XCN9{6<)}{l>YAi2JQ~jv~yrGL5fDIgY;nzwWmg=Pr`w97T+Ec%H^TVco*wKJV2-SUhLF{S9+H+l}k#W}GJDdDqQ2yN!8ui#pfe>!0XkoXLF&CVnw|o7gYUw;IoD?T;AGyH0WL^!0eYO4O(JdLLi+JJa~Gl=IT{toKWMy^ngoVlNuG{-a_YJl`tT!ShGNb5?tO-|#2?Fnj^yJmWsITZ|Kn|7!Td;yuChP2zc~z2y|k@162R%xfH9&iM++`o!z!pgz}L|3-Nq!0Y!nJMl_*i*w|UKTZ0vXGM&o-w%HiKISxt=ZM$8UOe};*Y#i}UJ7qf59au~{`L6Re$S^4>%?_xuiv}$ea!1$E9$}XHDaATzf0_+_BQu<T@RkG68qx$N@HI(iSwSUpMdxkls(q5@$4MSQZ3v46%_88_7g}+_0gI7C(!AVfA<q;d)fc}33SQ5hELpfk)}9CehkOptK>)URd|FPf=A%<<cIKixSu==_rqt%58yL!m^==L;bU&wPu7#i;d;1&d>^iWE6Jm9C0s=wfvezBvH>oIi^*!Z7%p*}kK9I9!zvHJKC+BF0IO_)eWagkfmOD_K2o=~Y1wJ?*+q83Do?;Z@*sHvRvCnSWFr}bRd&HX@(|ettL%n-<ZiMXR@n~wNZs0}WvkI=57`Q<48T6JoD9G!YhWL_oveXX?tp!yZl>QvQ@nXvpUpJIdE`zw58guVg}1<4$y#_TTtx1Ji{L`?FkA>1kj-!boKI8SM4p73;2!cc+ykE?d*M^?IdT9#2S>?^a1_2k#^4L^74j;41-?v<z?b1+@;p2Y50d@xAlyfuf&1VH8HOWph&%>|;10{XA9c_a*SXCmSCjkU)$kg!9$o{lB`e^y@H(;*UI(uytKjwU2C@|10Oyj$a4x)&EP?gCOz}#$Ep*%4G{q~(x$p{j2{{{H0xuwEzzg6v$XW0k@O&~Go)0f3bKu4Ba&j5G9Dd7f?~$v>W$-HaO`76GWDdLto<nBCbKop;7MulVkTc*6*dk|J-bZmJITy}^XOauyneaSvB|HySuO#n~@479}kde7GE8TzBdY_oOK=Gfq=3mNJoaui#%iWx*7oI@FOf_$J0-4DNenPFL^$&Se)h7'

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
