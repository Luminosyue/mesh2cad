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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/da0ea36b7904452dbd00952aeb4c453e/part_011.stl', 'relative_path': 'da0ea36b7904452dbd00952aeb4c453e/part_011.stl', 'source_sha256': 'e462ff55446d767d6976f51ce982a7bfda39a42c118cfccb99c59db7611eda95', 'input_faces': 100, 'input_vertices': 85, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09727449715137482, -0.40779703855514526, -0.3905348777770996], [-0.01412692666053772, -0.2926490306854248, -0.30703026056289673]]}
GEOMETRY_BASE85 = 'c$}q|Z)jCz9LJx#xu(~pYp$(LU3XjCy~{ag-qq4A@3gJvRqwSa6cI7?u7uEaCz6D44Jra5NFjP7rLh;WcLV!F<ON^(vb615Z<3-nK_L_bQuI9Q^E{sCcTNy>;K%o~FTeBK@BGero^x(KTfMAN{e85n#K7$5uPj%}M4f6>Ckn;mM-CNc`i@SYjH&u1-yBxY?me(4|4dAsP_HHr7iJC>lUozXp{c=SZz4H$ta!XQdGz^X#lr>Tk4?TbQ_%j*i<8p@{da0`pf|Clr#Epb@n4U)ZXt8~$4@S6EkE7z&656*TeuwXzf0V@5#^VX)z_B({^Ee=C$4<<RnRZ3`|{(c`qr0qtS{?io;&H)QL`T|2L1Q(OP#l`2YuVW%(uSGxBaNnM~hK@<`4CC(6@cceAhqu>h-rSd2={(dNJtR{?%*iy?i%+k#GAcO}!cIKilcmvHi$==aXOl?d-faXLY_3^lhKztFh}rU$rx5k?;B!`L55li<KxpbFtRTcYTU{W#>%3Iu-Z(j~}cAeK+Uwu$S-p7x}Kw?_Y@a-`nZcaeaz>+o#LFd3r9`XJ+pAN|ayzW#04M{BQhpEy~Xvob`NrU9!IQWqo_UWF5CI-uSZ;<(IC08tIqkZ$;M`n)7_OjzoPoPf_2_Q`Wb>tAF9w3z5$Qe&~6?4?Pd~q31#R_Wt6Bo(EfBJ`W4ueh{_ptS{G{_2s&=zFc?Km+Q;bk?Uys=DXf=X!jrd(0+v<+OLE!^F#ZX^zA-|AKJ&HZ}V4mob%?%{%?KxzOcT0Ur1l(%lCryL;HWjm3O>(@*cFle9u~6z8|eG-;e6t&u1d*<9qe<-dD>)YxeE_8l_CE&|fW6lYvhbW17Qi^e4-a^uPLK+1%g%KfhVxY2CxaI=Xe-qhqz11=<ED;0MuexSMkg@6hqMjvShYbMOec=Kt+PN8k~14A&|%G^Lt!WOa<|7)H0j!*CDU1^2-Bp-pfTH4U3D#W=TW1^+LGDp-+Ycu2=%I#PJ%{1&tsZh<$TDLBQs8|dF$&jg;SyBpmF?}qoI6YvD*?q{AOcoXnAnuf>WZA6-Rq`7BZXdB!GHxX^j!{}<b7FOso*l4}FbJQ~%qxZwh;bt@mH^V6+$vlh>z(#k#L+~y%2j`fD;YV~ls$(O%8QuuDqn&U&+<-R14R8&57hD6cLGOjvz#ZrVa0lFnJ_Pr{gXmUx5FSIHgva20=u_}Mc$Dik*Z%}M3XhUwc#n>~I<})3cssla-2!id*P`p;wQwD}3a*2z&}z5}UWwifuY_CCb#N=(i}u6$Y^<uW`k#Ix-Z@H33px0MQJ(2<)4?+@=~`~n&Sz`PebyIHrCv5CnyXTO0Rd26U;'

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
