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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/85f745f8fab74184a66cabd3aa1edbee/part_000.stl', 'relative_path': '85f745f8fab74184a66cabd3aa1edbee/part_000.stl', 'source_sha256': '06546951e5086e9eae31ac6affb2a48afeb4f616b2914231bae0a6437025270b', 'input_faces': 76, 'input_vertices': 56, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08928267657756805, -0.44095176458358765, -0.0790300965309143], [0.0637296661734581, -0.08027103543281555, 0.05863681435585022]]}
GEOMETRY_BASE85 = 'c$}q{Uu+ar6vofCU6!`8+tvkYTXfdiPP?ot_P<55^+5?~ge8Cmk=h2fLPDVIHWk#$X!>MoA_7HIH!jK2m}p8RXd;BL4;nO>n2?y%*oPY5j3GXN4?Ym)oc(6Ga~%_-lYIGp^X<%?bLQT?ndD%3MVN|5guWU&9w_*USocwwCQ|9~1A9}M_@S|5KB|$N564e#+4)>@myagsb#q@Tvo~$_8|IUveP+xsM-QjR(<6soKAhf{;{4f>gPD|_XZDYbrR?*z?w**@*&Z_{jsJR7aVh;je|gpR;oq;`V7D62OtBAqGjl=Co&0#@b2T48UYKv1OW2-EoL`XZ+Ug4O`-O@3*q5WTpGrRUMKNz3{md&b%#D8_<1B5@OCEpml3aImw~S-mIhYf_@tfqvwU5ur`LC}?PVrlk(;rWyc$~syZdQKJPhXTgxJkwtUfcbln&&!NKa%JF5_RR)`@4_G^(Uh5sPBQcZM>-F&U>J9{`rJ@{r5YI{k}1=pk7}fQ*!IuH*>D*hZ>6YPtHxc^4V3A7fuE9u6j_Xv285tmDBc{`^9hG-s;sC^_}11^&V)tc~IWpyM0TNzqIGHnh)I0|0MI$ZJu!DJN7I}zdi1J`SN!^O8r9^=lakK36FW9#Z#{(Jm%4wzashH=Dn)ZQtKr8Gv}2LWU_Cm`SK6fq<-sUTSm=u4R1?Mo2Ig^{CTU`m!2Q%m)tt-9>?jIeC~RjeE8L3J+$?&>4e8RUtT&h<JFg*JAFC1-j|c>eU);puTrk{RT^LGOV6FYtgoxH(wFvs*K_CpUU+6P>$TpTTwiacTw8BWuCF(%XLDYjtM5xs*MB0pw!b;KzP}C6Bp1ZheKP6V{Wl(+f2yW}h*fFt{-Yzx*3Tgyj(czY2fF^%*5CX8xBdt18XmG`!rQ<mcmu@zIK<omUk~m8cS6jM!XE~+KLT#H^?<xCqII?mTWcWZwGeYXJOYm3-g-PMhUc?Km3pG6m%Sal0p1F42e*RPLG5^^0gk|<;0U-G9s{qm72^4Ym>X@iz#oH$z(HGa;?IPln7bk7UU(O{3-|Rx%smkEDtHJS#JCl3ADErMSc+5*@qsTBDg&2cJU=`H4xwj1d<EDKE{6w{@dL_p1E?_wuC-MMuYw1_0gP1zF;~J@f-Aw*@EUM6_<o2v3~vO7!41lsH9*X(;Z5K=crCmMTnl#kYQh}G!Cmkca0}*)IXUPn3zz@Xr{ulEk_l8lEcH9x+mL$a9eb?Orj#7?uP9D*86B~GGrw873rE8>3j'

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
