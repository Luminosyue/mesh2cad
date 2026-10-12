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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/dd76ce99626246889beeb477d6ad2c17/part_000.stl', 'relative_path': 'dd76ce99626246889beeb477d6ad2c17/part_000.stl', 'source_sha256': '3ddb42f81196a3dc1e26bef70a5181c41840db1aac0a164eb73aceb939bf94ee', 'input_faces': 94, 'input_vertices': 73, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.02401873469352722, -0.07158292829990387, 0.17469894886016846], [0.07320751994848251, -0.04627116024494171, 0.23910550773143768]]}
GEOMETRY_BASE85 = 'c$}q|c}x^{6vuxH2<6a%9Lpgv9LsXK6#)TJnSxLnt`*t}(%4yGsWg?<#k1CSQj<nZo7B<*Js?{YlvKe&B-SGg)mDoaNfWgi=^72y_Me{7CbjMS-g|3jn>K0MNnYN2pWk=h@BQBF?qtnno?amguQ)b-%73KRhcRveEQD>c+BdW`TH8#m>$d7xAaH)Ud`IPz73Mk}+r+jRo2+e(cH?5fxTHDPm@XKbZT1azOY1W>dy|#(63g>#R+YD{v8=PId2&u>x{#TYE^HV6>*dFLSl!)S!2OY-kH%FeUmpF8=W_lia5>?1;EwVx;Eq8BdCIrIoj-npd^qMEt)4Y+1}^IQfs3}oz@;}Wz=i2?)X!9nz`myjk>84bmwUzeJ=SS|8tYW20T&BvK+mSzfjfI@fU{~7aG_=`aMs)RKKR=O*#GW3*yo)|<o6<hE8gdUOSM;k%XKdT7l!WP9L^Q>KtDAxz(wI8_LIK?I6Hd;&sF_1_8&6|TrMhdo162s%gDoS;M}IJW1qUBUZ@|q1NnCyz!jUhSF0Dh$Fa|2TaYIm$9-q-!E@b@aKL@3*A79Qve?t0PcS*O=M~nN+<E>O=-Gq^aIt(naJgkA_8*Yu#$9@G=Pf*M`Z0%gZY(bp^zzLK<gZSHUT&DedG_3O(~Imb&gY5W-1=m7XK@ZM%>6*ykF@bB^2Gzd6<LP*4ofZU>yVBjuTZehDJyVx@ig)`>VYel@_`HO_koM!zXF%yn}9p-`t@n`u6a6y%0BJqL8+|7^OiIKXNK*d7n1yuvu-!N^JE70W9vu#565xeNgv?K^%3B5<1e`HOc?4ndhP*VoQZlv2R_G}fxzW48=kAffzQj=09@(u!G21&AV0YZ>m(n*`Q-Ls9mhuGg<i-{)Z-k2MzH?z^H@jOh5CUnfQt)Lu%F_`vClz|y|Aw|iFLADvCf4s;H<O(pVysYoafR+<e`12udTs42QrWcpBsjAbza1IMiu~<FBwoj>pJR(CFI+-fnI)g49{Eiirc=*;Fs7x`+BeT^CNwA2K(vC>4!QK#ZX5Wn|%iEuUgixeZG>%5Z3W7Mt%LKxNl+<=p8H1qTcJq5Y!o+#(oCk2Y_!a2fb9W8ucLykZ+21JFh6!0++9}LLKLkC7^fyv=#Mro!DpoIh^x{@__caKR9pn3Dl3Sf;v);0qQ8bllMXW#4h0Mb3LBdZU@fHzF0ph47lWc8TmImfjh6o0T;dBLLPDLAk0B;!}=NC`+@J$Lw)6`M(jVx3|v0kj{6Q;fD4(WBfzg7+6R4Ze(3_}vo`~0Z_faiS3Cz?I(h<m)x7=qT;97-V0L>ehplb;{kE6-CQ!{+eJeLxG_Pb1`Q`F||4MGj`d6>yysZEIN)A$ccv!Vrs?Ad^QZ>%zQXWJsT*JA4h>XWRWI<FXkaT?An{pn{p_nr-%6aTbF=qi3bEc!5$G)oh5o46=hy_sWL7ZRy6mu3#F=ru^`;!l)wOEQdizXjKajYf}rW(nr8HpK5$Kwpj7gC%_Irk}=HKV3REZv_%u}hyuEQMmemP>Vcjm4@hBDRQlF6rXvJZTiWSb}PLisw@vO1Yl&^ELPDX};V?(6iCgeG!_qIh1oAMR62y&J2`CQ9O@g?gL2|MKRYuLOSjjP|Pif?lBNgBIB`%;zZIUQf{J{`*_V-Bv~Tyc+#XZ{JcjJ3nwp-=j*AOJe63sCN@z%pU%L~<V!R4BMYVZ1yWD^J2RX13nL4seNw4j7S+z7{8814RV!3&Ddjv~MtLEvbH1F6$08Yz^T{uzcsZ>Vk>{*Hle=Q>myqY0Jc{#(m#X%dY9*?f%XA(gp8xdM<<CooFSz!P%wO+x|9REk*{Rlg@MCK(o5g=y)E@v3wqErg!!CaSH4d0m'

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
