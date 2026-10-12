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

PART_NAME = 'part_014'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/00790c705e4c4a1fbc0af9bf5c9e9525/part_014.stl', 'relative_path': '00790c705e4c4a1fbc0af9bf5c9e9525/part_014.stl', 'source_sha256': '9b00c8a4007d566e1ece3d6f210b6bd3a7bd58fcb4b736e56319ab1bf0a60be1', 'input_faces': 120, 'input_vertices': 112, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1579357385635376, -0.2081173211336136, 0.15538929402828217], [-0.14990267157554626, -0.19891202449798584, 0.161527618765831]]}
GEOMETRY_BASE85 = 'c$}q}32;qk9K~-E5=&xzNJNs0)DsEKLXd=9skKR-*!SdRm4ze{yP<btr)W^5wrAH;YHFCV)U9N+ma4XPhGz*TwQD4dYTx_Lp}D4=>9o(hIX`Fq?|lDnxyvLj+NqjB!l${kWzFbUQf(XBzOIr%nwXk5J|j6bzg>3j6bGrE@WqF^%rq!AZkU5KQJQ8<NzG5rGlt2=h_p_|0NI$9lQ%vuF*_kAFD2FP_e>m<pK9~-(-U)3ZU1i_6cijFhxi4^)8+s8sb%k>OUIHUHZiwta>A}sSZGP4T~k7ZuR6llD&Wh8_QJP*T@8MJFVyc15x!jDCwygKKjE8~z_(mOz4a4s;j2f3g|E4wUYf%CFZ_{{@btLI$*CcHWfgq$CHU6oHPO$R*2qZ@$GAyjgm0-qe^r?9EmyMO_mYLLMBNZMs_)BU;a~B=d}mnU&#Dx@a<nn#yD|njcV~$lYd(DQjA-GT&(1_YISnyx(ixGXb$=vsw3!W%-}gu1%f%0bFBLiqUz(v|zK`y~?@=9ndLBXjp1bJhffMpi92UNL_MKv^vm^579K!l!l_JOek7Dur<Pqq<_e#;HcKEgMrDG$pkNa0)AJ4uNzH)L8#_f%KZNiJ<s{LrWe%Qwz^!>jQz9j+UDy5ahRr^$qw8r|I;J@ipGQc<QuYkXD7uJ9NZOm&?g)U!nZ;C$YzgbT;AROnU73-r;BY$TY=6mwF@XgHEOdiPD4qxf^19JRPueOA5t@|a`^W-hjkM(uA&X)__k>m4B_?CSek$>C`=cM^l_@x%~;|yQ(dV=*guE)40SB!h^adFjiC>u=3&w#HTxQ?6)v6ye!BlPbCUn_!dp7%gEuGSv=VvV|w`uoc<uQDg(T>Vwok9LadUl+diYAMDYih4`T9jxd11@L$Mj_YV)sV-j|i*sv!cpK;N=se6T2KCAb_!6&o%OW$@p)Gu^><RiTf-jfe()D8=#QX#Bt&K9pc~*-zW8G%3z5qGeGUgQB#JGpDa9`@a74xdJBIj}e#$EdY^V)e`Ki`-#To?1;YpYfG`KY(LUenFjI+69KuEKYnj_aas1+LRAS9Ig55xhV2gRkzLiuy*Vw>G}4A9oJw)%%xFUoZvr-OG^^d`UO1dI9$(OYTLC>pKbc6Hu?j!`B8+#=h)(hMX1`b@@`|6O6n2g04?<=f~KWo9D64&n6(>`8VOqThHspwGMlVd2RRwKA$i0>0F%8bw8v3CGeHn<FLQ0f5JJ>Wql}oZR#=XSL`I*pV#kzUs!_rz$w`GM?2y7{08-W4r<+|!!J36^Bm9T<81imh=b^7KK*_0<*d(<f2{!L&<**@cU!RzFJ|e+ReQsK``kQ-=Zo55GuG3w4eFo4*ZMBTzO4Ef`LA$p<xdyE=W|f*JQw#L&xIKG+G5NravS`z1?V$40{P{0aQ-tUqMsqlv2HikVx67fzxy22F6Uu=cElpzi~XO4FCAQgd^2*?u}R2zScLhGT#EH+o~VBwHTa188;|^PYcMbGLX5j<6z1C^9`&2JUo-o|AGQ|059Xy*_SIeQifIz+KQm#S@2y9EAo`bj#GrogSoq2W^j{u@{5R)kXb#T9Hu#ER1NOytGR6&zM7_&2^s@)=C+dx^SpOB9(9d+_%ZXt)hwMj<%*K9shw09bqNO8$dnnd3b0hln#e0sL0AF#Li}Sf7mG3PbbnB_*jK(_nchH>^%l9eB*&U+a$8h-4w?SC9yX%l&pY?h0r6z@_&qzeRV<6VS9s918*zUt|y0_=M84FI!&bBGozBO%c&uNKOUY+fx{qsiu{?$37{l9y44i5akug?8!J;d6+G1T7V7;-OadvY&w5VbWqh-{?FWFy&|+LY`~_Mo;Pdysvo?~#4TzSID+FS!l%eR3OeTWTkATXHBhf*eW?qblSua#w11a#wOUY7cTZauoFgauhj|+JziR4ySe|hm$)}gUKDq?Wq3bc4R+lbFv@VliHAM*9K%yvOBdt*`3^&Upv>M)+N^?*P+%X*CE%UI+JUWU8s&^7jiYKM6O15pgNHq$knMe$koX;sjlRjWH)LfvK!ez?Lan=L#Q8;L&$xoeaU^uCh9=4iQJz$jNG3*m^zX?m^_?nCJ!ga^K0j1YAV^T>EvW`8g(o=jhso%A!m}uP_xNn$XV13au#_sHHAEyoJ36|Cy^7VqsR&55!9jN5#%A%LF6Ii0n~ov0pvJp3^|S*P3=XFCikQUk$aK@sYY@jxfRu$+=}c)^&oqZn^1koO~}otzT{@)mee-nxM&AQgVR6#Y38qwDlU+!f2eu)m-@$2)n9hCWxah!#YI;ak0wXkzi~D#vS01epTX5*rv'

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
