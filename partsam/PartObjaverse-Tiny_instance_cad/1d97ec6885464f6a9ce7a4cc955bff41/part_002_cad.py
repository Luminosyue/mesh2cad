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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1d97ec6885464f6a9ce7a4cc955bff41/part_002.stl', 'relative_path': '1d97ec6885464f6a9ce7a4cc955bff41/part_002.stl', 'source_sha256': '3c1fd65a8abc6bc169c5df9dc2d4c0004e49df39d20ad5c28b19d87a222dbffa', 'input_faces': 56, 'input_vertices': 50, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-1.1617884635925293, 3.7190330028533936, -0.352276086807251], [-0.4946216344833374, 4.104440212249756, 0.27448412775993347]]}
GEOMETRY_BASE85 = 'c$}q{e@s<n7{?D>M1IImksk$e;DQ(Mg13-xjpBla(UrQnHI~IX*UKd>26SPtK;5a;mZqy_wpILbC@WpAq+nW0J;lhxQYq*U*7RP8p`k6Ain_LX-|zES*lKHawrB76{XEZk-sil}dC$FWmnAGop({%{G?nq0W1gZ&Tc9K<?LL3oMz626sHx@Y5G5X5UN^>__ditQemF#FSGsKVzE-c_cBg79Ygl2ktG0$_f1BUa^jNdM-Y0pLr?J&1c<TmFi%-n+N*s2zINz>rR{!f2B}&jgd~N247`1gT$2nz9hu`RvbG@q;Tq#w-b!GP;_=KBy#}#nxqv7Yv<^1CeaO1%V%Co8eQ#m&`jbD^wpt2L(NV|Si&YchZKzwsnyyWJdhMmYC&%EO@;>~8SDf2r!UI$m^_r@aso^2<Q=lphXb#)H%Xv>-omg9a0#iu4BPhg#K3iTYwAwIL3)(xNi0QLKOenI_1$>8di{$rBsWzFE`z8b7+c0czW?!Q(CuDQy&e#ao<6VfP;rJw3dw2q*@$p~=0!h?8c#S%Q15>faw_zScT+SWy<@Vr;2FJRr^Z!ySosdp54Jp<s{+tr8<Ol>$W<JGEWaA$TS)(xyE{2qDBt0{iw3B)T`uAxrj%)n2`cQ%dk<i0X2xq0t9;QGpwSl1j%Mjq|WPH@vziFp0$$`jb<ZFR(V-A&Ki`y$1^R06Ig)KmV`?|y~n9e;ER{oSijJ&k!-SACYa_Ns|>^~$~2x4>96xH{sX=enx|`=C!3gB!o*Q$6=}euI4*v4T5YHQ>hdxuaOu{mhTJuVfYSIM=(rMco&@;M%HDtQ*MQF$_MdQT$jQ_1733K%TWV;KtVdbS}z{)4ESqfICwx^t|1fcz=}ltH+UVq@DJss_1LX3vMTFT%tT);}h&>R5*BGO*G=QK6MCnTs|M9eRzw`U3Aaqh#wDv8;?{I9}N8xee4<wApXz*<=Jof0`+B`09V?#)4Dxty74}wZvhW@>u7%(cN|9Cg%*n6T}<a_*EyV*z}b3mbNwv6CzERrqRzfrTK91)<xi>Ihj}S+ZDN%Ac)jfa@<dLaLH#<_X`BvrBTw)>aA%W;>NkR=N8C4kZSUz?KBHPhYGIM$Yun(N^Qo0kUN^?S|I}_={_j4ucl_^9ZMdi*T3C#*a2_L=#S2Shoyb1P770sXox(oJZV{HjI)i<ZWec;iwz5yMJYhE0Hug!jOqiXuoqdwsCd|Rw!9K|fg)L>hlznnsA}ois9P^o}!ZKNBvQM&Gg{8AjXP;!r!ctkMvQM%EVGCI=WS?XUgvGLsWuIj875PGtj%1%?A;Q8~hp{h&UndJ|3;X01DvW=rF<O|(zD2Q)VqXOJEsk{@`(n6nNvxCDm&kofW1Ysn6z<z%){EJf!F|hOoy9&Y_br!oF8gfUw*uA$?6Y&<idYx1&+Q5cO|tycUztBI9UC_HkIi52y!lwpy|YQ=`s0wgUGu_elS7rK#CS~Zn({kIbm86'

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
