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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ed24b6e27921449f935509d9f3da043f/part_000.stl', 'relative_path': 'ed24b6e27921449f935509d9f3da043f/part_000.stl', 'source_sha256': '57588ee4957479abbc3b87ecb1fbbcf476b3ef0d34a2f8fc4ed1743befec651f', 'input_faces': 87, 'input_vertices': 70, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15177811682224274, -0.12229961156845093, -0.0820169597864151], [-0.009832773357629776, 0.08949410915374756, 0.09225323796272278]]}
GEOMETRY_BASE85 = 'c$}q|2~bs49L5iuATFR1n}`>*9-Fd=fFy7eMU7FI#KIXyA1X}lvZQ0VT+5ZIY?N@p@Cm4+B7));7LQCFqHJ?AjqJ@dImwihhE8f}?|kR8fU%jT?#!9*cfa>P|NB4Nz4J2Dot(Xdx`IT?Hj}fbs}QpF7G7dWUSaW^S$Rdn7cO4rAUxsA>yd7mJatm$GzYOnykeT2S2U~8l&G0T=O>sVG*kYf!s5c*g)<fv&d!s5TJHR!JiA}?V(#KR`+Z1!RD?DnG(uaU{nyLgUV^rC!I>tz8f_2WmnvFI7p6!p^Mx<!1Dm8;+miN4-+1%q58%6Iz_*xhSEB!f)y>eY4PEl+_fwVM@Tv0qwN^^s92=y3y#v1WoAWzye|MS{dVAb^$lt&G5aRCzDgXHr_#!7@Kl;r*j5>^>J@BpTD^REY@oVr!NXuquqpHWK&QkHl6%{|zyGp7yc9p8H<IWbTy0)qszdyV4UHHydOL0G?@c`m0bCf?jqEV{t)|Df8Zu_}Y@Y7bq*KRJalWI=&fp7Gg4_};5tCR7Tn_Ex9Ur?v~=T09)eC@X<a3B5sajeIFRlm6^LHXX-;oDAySHYit<2d~0lPbP<&MxE$b~y(B?k8RH*w&Xcs64J^c>d+H^-Z09#vA6d6&P1phVmEehi~1mYb)j{&3qL8m==}4U?0XMLdPk8*srM9JTOE3-XfHLu@d7JQ}v^GPWD$vaR2*C6*sf`5bDV<hi|-<jd;t2i|B9eH&4Zv|DpWtr!mi#t7Y|F=AnK30pwpEUEd{t%!a*KpEJFbKlETV;=J2YkDgV4eB#1&%&(@msW|h8wa|@K$fJM03-RXiyNA>~EWtjpZBNGU+N+zC|I0+RUc2j%#~kIU{GYa|dCs|9i+mZ4HSn8?8_<8o56G`g+ELSGy<FSXJlywJe*Iy@i=gVmDV_Z{vQ(X$Zeri+PAjm##BY9x*W0e49z8oi`N4Blo{~D;+r|&TITI5`VIS#hI`DgU-}v#J6Y!&3_NjBU9llmG73-umSHL$mRjWLn57mCkD&4Ej*LQ0EFO?p{^NW-BsQGt?Z}U_8OfS4-f$zIa?ZfHO^(l|>Efx>tvGm-5b0EGPuI70~B-YO|)Jgf}erjFB9n@*fFRy^#U{U9N?HY`?yKjjJ#dtLzf4sLuV#nL4uT>zAIqqyZ{D6sSy&?}_yt>;*=r3vl_aN^B54GRA`9{G?)Nk09s`uB+^DqyVW5=;CZ4ZN$e{BkUy-&D0SJxMnsC9V>?^)yAJ-nB?`_`~(<hQ<_z7f7LUY%R-xcbNX*<OgZ?Py&Ke_iWtj6ZBM>e0RqQvTH%_!e`bTCciWYv9-3z`oSKxPX0c#12uu+h_2#4(pMo%r0NkE6p$TD0LP>wx0H{X?|{}PpLHJ^++H8DV-DhuRf&-@&Ef%+S6V`FMD%jlk7_EO?D;sr9MIKOAer#$N}U?>L_v~c{rQo1ZpZdfjq|EMpKihspM4lNurv_QlrUI$B~oBquC^nrH&+zCCA!ZI5mtql01@m!>B>zaOzNM5LxO#ayT`VI*=Sn9!woT9!&P3_9Od{z1SpsQ~Q&>$$?Z~av=FhdkdikQ+>%&HF5~`DXK=68by{mf*eAPp^hNOkag-aWSyMICi!V<6j|yJvebC8)D&_eHJO@1PA11u<H>R42sX*Xs6)t7{m2nif2tqZpX@>HL-ruMQG1Zx$j(#;vNPF<D#-G3Bs-B^sIFuevOBde*`4f34Iq1x2T>!*gUIq+W~MthdO7{m--Ev|1I2d!v(UX~*H>ZZo|Eml{(3QHrn~e|gLM=IvKTz&Pe4PG`v'

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
