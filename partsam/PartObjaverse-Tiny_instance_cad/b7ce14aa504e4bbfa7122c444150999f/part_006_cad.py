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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7ce14aa504e4bbfa7122c444150999f/part_006.stl', 'relative_path': 'b7ce14aa504e4bbfa7122c444150999f/part_006.stl', 'source_sha256': '62d9e914f5ef9fff3a076b4b1f449cb5a0776b62ee88be4b1cfb8323a31f8840', 'input_faces': 133, 'input_vertices': 112, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.059424541890621185, -0.00020253658294677734, 0.02039187401533127], [0.025708850473165512, 0.30312567949295044, 0.1979345977306366]]}
GEOMETRY_BASE85 = 'c$}q}YfM~47={Oy7PcTPEz$~Tw>P(~h`>@>E0@z+XbS~aZiPw<xVscs1PX){ZDkuV5VWx^G}>Azq@kJ;HBo-Frb*XZ!T8fe8;kK)FOeo%WBgI0ac1_N^_)3lV)T$N?>o<YJ7?ybv%9mniY*ZdBzUbLPeixwB+=B;h#?82*W1<8;`Vl@wRiS~5gX_Hf{v6{mAGodNH2NP;qi96yBwSCj+~}Vj#Rs&siUi>tFgVlqs!xEys)vY+e>+Ob7QBMw%2B4WTx7k>r(B9?f>ywM5hqA(f0ZkHkXyRUdX4SY4bDr3hw{(C(gB*Gp}(z-9O6tsc+Q$=xrk}Z9b{Y7aaKwS0^uUKG!+L^L}3Rp^^{AaZWya<5kA}g9qQ@e6C!{1M^j!`=@Q3lN8$+Z})ATHSn4g&I7jXoNJl&uW&we>40JWG8gL=TwbrtkxzabIv=cC%te0Rfn&2OPDV$9^SpL(QdJ)lM}4$gYl6JfchE2&nTz=gF3(@)$oKzx{G6)(G8gqH=iZ*+yx{xGJpcLh85IwVIfHy)dO}$riHrJt`OJ^woZB``@Od2TQ}V#sL&5zWw2!OmY2v8o_|32&@0@#DUmp`keL`HSr-_UDkGaQG^^|$2o_|cetgNTRMLoyKvNNiB%3RcwTq-!F9ADyM{DuoDC;2$!x%F3c>osxleivM-kBN)tt>=qT&PTrE`$#q(nN{&X;ee6L?-!Y4e+4%^&k_%Po``XzddghXQ!CR(RrQp4sGh@>#~IgleESaPQ_)wId_3LAuUEgP%oiN_<m>ri)qa_{_`DKa+Ak9q`<2-1QN3SGT+WxqH*ql^t!h`kqW*+@UXrhRZWD*=IFBEDS6?3!7xl?3=*m|;4|(=OT>Gm(=GxuF=S6N_<6Pb^6BpxyliNQixx9}ij(mUo^~1bvtuW5#{Tom5c2u2`Yb{Md{?b>YN-pwkiTzxq?-3Ih`y#mfoXA}4`$uJdKK~OnhWiRmCf$a4nz)$f<R?eCO7C|Q7vGO({~S<0KQWy{T&3@Q6Bp|hTwbrt#pirt_OqNz=a3MW&LRHv(??a$p_cZ+3DtT{9P17Ia{k5OdX48d6URJ5Tw0fji+o?jY0l;Iq{R7o(q%Y3znSuT_T`0yu&~n8b5o=4=*%FygsP9uEm{BW=<Ia<-=lLiokJasDjLl1MSCyWk3uWqE1)INO88<LE*eG9GWa6+Qsm^KKNp<&a`Zg{ErQQMULG_bJ_qCFLd$gh<;W?=7<tel_&oR=XsPZ##TcU)uV?;F8h6l0fX2Wlz$Zdu;aUDt<T8zeUq#~q8f%~#@aZ&GqrDo8`84*3p?@X%(lJgN##n_u*0$h23!riEiJ03`L@fH4M!-iPHx6qFM}Ii_Vlk!#{TB3zTnq9n7>D^r8jsP~4XuH9qpuda8{R`>4|4Y)pZSMrY@x9oS^&?Y5dBQI>ijmenQHI_@Y~?GpzXnZ9*6qiS+t?Q7ISh#J@6jnxS_4^tyr7zKD2$fM<d4f;dMUbF~5XHBnkeqW*P>+m<IcuyAVp?7ekjpqu^7ZHfR+5TJ$ABZSd>RmkdpUzZ-q=&}8_#&}W6l!!JQ!B-E-~55e4{u`YIPps|s#kIkSubpAoKnck=K524NUex2WpHq%s{--I^P^*W!8Hq(3I?eJO9Z1{W7mkG^+UyeQ}G!x#5wJnFPfVX0wBH^RZwxWhnP#b(0`U!j_+BW1RL6hM-XtdC1g4V;g)9})0hVFyk58Vab2frWM0NnxK0Kb!lt2it?!SYZ4Hv0SW^Uc=(6G?uh@hemR$~-z&=nK?Uynxptoc<kPg=J4a`3qMU$qW'

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
