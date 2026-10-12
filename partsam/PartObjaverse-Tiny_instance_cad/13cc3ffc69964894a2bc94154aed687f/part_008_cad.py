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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/13cc3ffc69964894a2bc94154aed687f/part_008.stl', 'relative_path': '13cc3ffc69964894a2bc94154aed687f/part_008.stl', 'source_sha256': '920c17a356068fcc96b664cfa2a85d7226e71cf19bbd2f04d72eb15523f91e4a', 'input_faces': 86, 'input_vertices': 88, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.20998471975326538, -0.17278489470481873, 0.2205355316400528], [-0.14501982927322388, -0.02329856902360916, 0.37150585651397705]]}
GEOMETRY_BASE85 = 'c$}q|du&rx9LG=Fbqb=ehYw(by8-JqI|goGH^#Vw**WUA;&{YIv~_eqn2dGJ5&`9g#2^WYBrb|zv?5GUCkz5+sNpi*7Resn0H=;%O^ihT*c78CV$`0~@9lby$HeGOZoZ#=cJA+<-SgPJZkHt?l|+vW67pQ!rr$~kJ*SXV(&F<6Hr4r>=Wp5ijEPKRo*qWNRK2Fk{fLRQknOhhzUDf=tyr;@)H`f;#a7?w5BR-Xo^155_fhZkHZ=PpzImf}t1t3%w!>jp3Uchqv&w%xCP%uU^@cB;qkS1w&(YMrOdVVn@B5zmh^Bh<$UwaJly2;#sbAg6c_sPjGqU!o<;7F7`ksB)Pq6zme8zdDv#_0A*Z4$;t217IjOC6SocA1QZKE09e{d+?>tBx?rWs7D9j0Erk@yL_KJ=W<`qO)}FW!6RI6r3BWp3s@{$6EQG3WKOdrr&R>r00_WcAg&3-2*s`dvTgn|fLQwY?dG@m?$X>P=QJeN`ylle3=J*zY&khq(5wqpz^`&Kd0QB`qCYvhj_1VSEj*zp;TEU&D*zYj|;d4KI#wtd20gu{y%|#_9;;8|$YqzM6So)Q8f0*nRb+i}Bv`&UiPw|8Ul@%m*+3&b1E)>X{FJP(CE}<5w?n_uXafmfcqkUip+=m$H0V=9SiO`1^M4W<J~y2uXeM@ynclzAjp)YTJ;^2OmAg^^<(@I-4)y+^&$+@9=W<)gK>=&b#-w56ZkA@_iofwZxaB&$UkpN&TpqZ{Iz3p4GWhGa&O?=S{ACu(FnUwbwBy^Gf+{zJ7i+Tkm>qQ@_l6k~fcV&tY;8TQ9-sfdQEhANZcDul|z4_6_p$wLY0w+mG}0e`sUtj{Nyszs#%ISzLQ#|Ir3Ix%$RB^}Jd<BJ-Nw!+B*a`;4r9_}Yi3W&Jn2*njoXq*JozKz0_Kls#v||Lr-ua!$y`OKtnMT{a&KFU|+`P{q5ld8PiEe^fee;l+8YK0fzt+5A`9k`Bw(m*K_rrFUp=$<}Yo3+q>1l6Q#J5%&jpaep8u_ptv9;yy#JTZ62=uwTWzuwQBOx(>4X!hUFYaX%zKxevtd>*n5m)Uy1s7ZM1e=cLHnPrWzp)rU%Y7%6}C*;M%NUVRq-?^mDVNFNqQP6tlPg~<EBh2RCq`QQa$J2Dq+2WKI(!CBx8<XmtDcs6nlcs6(zavpdVSV8816>ui<UT`MZhRg@sz<J05a2|Le@_z6_@FL_A@FH*#aw)h7T#8%<E(Mn%mxIf|<;VxX<=_hBgWwAAN~8<C5?q6<0@r|7BUgb}gV!P-2CoILL%PB1z-y2Xfoax)>2kP}OdOO=$h*KMuo-zb*bKHH?*UuD3CQW-1hAFR1xE<|sz}F4ISqLWI1M}#nFyW<o`JN2t*B3#ek<HYCe{UI2XYFTSVxpgkhg<Nz$)?%unJy*oC;n6b|R;No#0Aj61WmvjZ6ktgKLo~;1rA%Ww*;@PPP2gC)~uL(Lv)r=)^1e?JxeyKO(hao1xofrO!Ar*k;lc$@BDykiP)HrCM+'

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
