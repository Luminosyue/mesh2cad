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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7b7b140d42cf447d87ab5e1ef407d9ae/part_009.stl', 'relative_path': '7b7b140d42cf447d87ab5e1ef407d9ae/part_009.stl', 'source_sha256': '5ac0e1493b8ea590559689771f469ce82010a99015934f9dfb8c9ffb65748202', 'input_faces': 96, 'input_vertices': 112, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.33577650785446167, -0.315022349357605, 0.1816963255405426], [-0.33566951751708984, -0.30885225534439087, 0.1845138818025589]]}
GEOMETRY_BASE85 = 'c$}qJU2IfE6rOflmA23VTlyoyMX}q;g0#g-vBL7ximq+9mI7^&cIj?^6xwy$G{IWEQ4?aqi|7Lnh>eL)z8T-$L`;cBUlxcMHS15J#Rmw)h{iOYx%1tza~u<+H#s@q_wCG?Gjs2Lxx2AwpdcvJwLv7_PA!UJf)phpD5jI?sj;Et<d*T&$vjc!>E4C>Mn_M3tT#_gi<wX&IXRRL?QlXZ!`nk)Cp0{fo=V5Z2PV>qq}1Eu$0w7dPmab@N#eEj^$lUCu`cY)I{)!1q82hoW-ot8+3l{oB=cO&`T1Q-^hj;3r)Q?m7`l79%F~_Z5v!j2=p{qXd|Kh@k=OdII<Mn2K@UzDx+q@b>0%*m=yM;e_VmH(m(BXOR;qRPykL&MSf=_s&}!CiRQlkR{pP;jDpljpzG(K@U!>}1cU$#L-9EGa)@9Z{Bd-*w@w}hI0kz-juA%3``AWZe%B=I=V%Dn@j+*CCu5?i`WA5wPAD$lJ{k-|Rr|0^*&GC!BdHUd)l&NQLd-`0_fK|_Ym$2%&pUnH1S@o;6j<4sI4_oyNd){(gzgX+|I`7AM{g!pVzRvgSynDmb-4nA`ou8*$dc%7D;`!^=`{myLIcvSYpIyt^o(ErdQ?Hu!-&x37pDXCO^QX=8jQ*(3t>dhz5By-=m-ET@YCL<+wa)8IersJfcj_C}C;NUyZho!SW#30J|CM#WZoSeS_I=N!zO>($)~o9NUhOp3t^UILe7e0?RDI@S;=*NhUzm?Y0++1MXJpgo)_%moMeBWcM?O~P$$U7{azUK~d|RBGvHH2Mb3fPPnQ!|#_f=o#zUu4TKXrZPpT5q0QrBTVsrzR>smC*)^mXo&x(@S6y)WjIx_{=Ax(@S6J)Zfb)|pRo-S;Kk5A!#@FXnGt=XJQhah><ceN6Ysd`zD|^D#Z1`ItU8=3}}J^DD0VzM;>D`IXk0U+H}@zxtcb>oC94=gj;{?~D1B?w|RUJ|E^+dR^vMdOY(hy)N@BJ)ZfM?uYr6uEYFF>&&lo9p+bhUFKK1&QiaM8E?;h>)xLig#;;<(cANIeCexmA;uxwU!BLc{i|2!=BEGo=Ij)WQ4bGMj8I7YFu26q!6kkMyo;io;z{6pz~$#n7$fm0c${L3ywAW7f*+&UN|8iv1l~rGpcn>j03XGeCg3D^0yX2n4dAUp{W{qTyaHU-ZANX0p9MdPK8^v0!5_oiR^T#lId2E%N_-q#p35qV$AQbi<=iJQU*^@oa^54DEAa{NKJ;)DI0P=|wqw4`Yk=jv7R;4+96Ux*MbU{|3EV@mk>U{W2JlYQYzM9ce~MxqMK|(#;BL(A0bUQ@f%Rg*72qxC?NQ_j;DbUvOI^VCfgi%&`+zrs%YGd6BJlz62Pk?ejsVwy_oC)O;2Q8Kdg}lVf;*^rKk{K<S$7j^OZ+sr{JaihB<=@qqgY9?AGj2JkC5gd#6IK_U^#Cy=1M#Oz8Sb4c?eiuJ1O#zcLCpx^Ii*F34Rwvgkm>v0K5(Bmm-${-yxJ$<pbXdz82?H4O|7DkIxGzmQ%>z<|~kkfopLe@1=-E^YVj%fBNg;ugjI2GX99*GfmrFI&&x0(k2{>7Rr54qxs@F$|vQwQ2Yr(e@oi'

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
