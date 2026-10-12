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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f1150d2342a8470e912942c49e978f28/part_011.stl', 'relative_path': 'f1150d2342a8470e912942c49e978f28/part_011.stl', 'source_sha256': '816d02112ff6736fe622e37b6b8241c8890222d2af3a1a1eedb752f1946951ec', 'input_faces': 112, 'input_vertices': 85, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.46738100051879883, -0.4921022653579712, -0.46202343702316284], [0.4024432897567749, 0.2864585220813751, 0.2935203015804291]]}
GEOMETRY_BASE85 = 'c$}q|ZERCz6vv<Sg}peofu*SI<>HWbu5@oO$6D4ZY^ZgtL#FTrTSljghL;YP88UM}@YSgJ0YYNv1cHfC!Uu@)3pE-LA-pWIh>A8*KN!EL_|?ScdHO%~-qTBB^d=|ge}CsZ=bk=&PIs3~xII2myjF@#er9H-N(g1O!Y8IP*#nc~nW^xeeXmuB2F=w){+%sj!^s^LVp<#w?9NP$X9N94AUe?(2pNHiz1aiV^qv>?W_M>4A4<P6m63evrS!gxybt!R3mH9aA!F9~uUC!g;qWhaE=ZSezV?~&W;!_^vv9Gq@woD-$iW*ItbBWs=NfmtVawlI<Z)i-MC6RRH$RMAveh{Se*EwmE04Q^*Y*03?D=_cbIzWh8ynNl%d<WU#Ov*S8qXDZAyw=%zv|X^PJNa*>ytR|lQ{1)^?Xuu^VsV@==(3<zGLGHUwxt1F)oPDzI?;V<3FCg=#+0R)Sc6xoAN!IzR`6W+_!a{@);LDEw%Cdp<l1s>N6fke(v4hzt-zd7xzc}8MzsA;0DeE@wmIVKZU#YeBuK6h43dgo$7OLuzX&hbE+RdaqGI?mt8-f*ZX$W@5octmu*~3ic|XBuzcci<mcZ5AGg=%oa&p4?_Sf-?KSlGnEGqhnX`PcWO`0Nm*tl@_5bRj%TDu7oX;=uvU#c9f5fQ{abAZwuVZ?Ddo$*6J~^lJNt~Zg&gp!LBinQOd2e0$Ugvl3_}0pE;Ks6(^H!ce`tcRbd+hlpxQYDyv7PU0&gPnUoH*u@IPZrz?}s?=r}W%=^}~Koi1Xi*+{zEm#T@2~^V0l+m(4HZrTMD=<6_L=JeP4gpWysFmvQ6^|H7r1WsYdRI4{))FPnG9d4AcvGhUjn&kOTT`^h=&Cvm=?oYQ`qbD!SUeXzMB&gYJ}ZSIn`x0b|<fn?q*OG>MjZ!HsP%PWh5>LTy_$}+k3U%j$)b#?#Gcb1x<?4eECYWM*3khIOxg79t7o1_gQK8V;5)&vj_AV#?Xy)8vkx)r_+x)pjDelzqibOL@5dJwggepr1Ms9}J&Vy%il1OGI1(DM0KqsJlCX+;jLSNbVwk4SqGeiif+(l)Ad0slC3QraluqlhWJMcN4BBZw)zSlS|K_rZIh>!ej8UWu5}wbHzZdl9R{8V}+g#FTzW+6rk8z&{AxEUg9c7Q~cpl-7iJ6JpJ%r|MR~l&*qb1YHGP4POae4ef&WLVHomg=eYW+%TnU;8#G`K!@O4phM8@@J-N7sMU@=SKm<>rgR7VM(7UcZSbSe+n}F?AAuf0Ev2`@uYnIkuYrCPy$JLpz}n%%(CyG6_zvhEY2DJg;5(t0OY<Y{M@;Eu(tL>f5L=ElorrfLM!D*~52o}0d^hv}bOXE}x&gW#-UsbNEu|lmwn5rD_y}~bv?$_H#FSnutsn7z#CowNf_MZm%2oI4VM@o~H$car2jHWY&lN?lQPk>#Uk|+$pYwkBCD6%4h0Eu@*T1a)T&6ncwtryxO8cJ;>&o-8R_TvOGT~LTC5Of(_Dg?OO~3dXqm3xb'

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
