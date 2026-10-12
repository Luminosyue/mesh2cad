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

PART_NAME = 'part_016'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_016.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_016.stl', 'source_sha256': '0a28091589aff7f1e081286ecd89f5953efa5efac001413959229b6f5d312e3b', 'input_faces': 48, 'input_vertices': 68, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.23938050866127014, -0.26926523447036743, 0.21710392832756042], [-0.11011360585689545, -0.08050033450126648, 0.27295544743537903]]}
GEOMETRY_BASE85 = 'c$}q{e{2**6vwAOt_A!-IqrJW)3Vo=Zd=wCxdH_$ED#B#pl7ruH2k=eZlQ@O^?IqE6|zA>h>4m&h$i~S{?QntmOlveD5za(D{{cyH3W>|*ZyNMM*e`L*qFvR^Y(3>*=S;Pl9%`9GjHB}XK(gqBP|7mK4P~J$xM=iRuLi09wk1~tHl$YyS1MBuI^+WDFM!!<BvVxx;3&bkMxp0xn1ko9hX;0a&t$MtVnXlzIY-Y>)N$1-mWpeG4@)IMtRTPShq&|HOre6DO{^a`=$Td=1>W$r#~~yw4`@{m+ogSuVwx4ThKS&J#hv2^o>i5>qives`>!9n)?;<&3-R%>z7x6n{(5UuO5C5`ug_IvwVI1_zIhce#`Ln&B;5Lflnw|zCM|{1zbJ$L58nSg5Ll)(hWHn5ADoC{kB6kpYjOYRK_mBey8(u{JNw$1w8uEj-2oukgLdz&mQKWe&2rJR`1a)uSY+w+4Uz%bG&{xCqs9k4!P&I>#X}y)W7iOH1rb(1g-`PfE)6tpwrDAoo3s`i=Z!=6!bXUK<?-<CpH6*-Yyy!^b{+=iT|3Qhb#zx4?1qn8W*0Mi#vLxHS>U*;UPhf!wuw)p6Jw`3y{~p+NGz>=C_IkZfJ$TrT0>&U>~?{H2L5=$gBJPG^~Hd+3)+n$*weTtD<`x`29n`&6U>%p<daWz}4zjyUtlz+;78H;Fk9XVP6h6kvsb`ya&c0|B7GSS63ZyviY{4Q+=ZXxc<e*!oH-dnNjF3`%%ytwMKv&Z5d%-YV|w7^|G9x)6Hj|f3W{s=->TAJfE?4;Ko?%Ag|Lnyxz{Q3Y_M3S_9?4tq=F61f5r>M<DN%HpuI=eCL7dn?4nEy7|m|6u5pKbkvTB=X1je;QGMJDdBfdz75>!>^sBj(GMnUK3O}+>(@_ivg;>~q<EdiJ+I9_*(T_8b4RECFl55~qpylOTRg+Co^oCM-$Sk<cj~AwG<*&9FIZ=VbMn$+;Cejpm2hsiR{|&MXjWLaM29^6#VzNAb5h@K^BX@6@z25Bvjn)gb2!86baRX8i3qo2W2HP`=F=2vv+3>F5#z2#23d3b-(QWLjsNOuZ2bRM<0DkV<J9J$e+=Vw)ShMgM!yDQcB2<kD@O0ZI6!S4wKDWRjDyttIPS+W7B8pPNNolBWf;#T?4hyG3fs@ZIDqv^(LaGPoBK4*XTAaBMbw_6R)@Y4<HgjfaJ&k~7UA4_oX`9cjD4uti@t=5{n%%IKE`2c3biKm&tSZg+EN@}ieoIUrnZn;4f+tqm8h)({gW88oN~-#Uc#82%~jOaqhF2j25QYX-i%``mT~P`^fef>#*Stl`T~rD_!}%hUy5<0B`@Ds@K2wHe>I&I5k3^%GsV}2pIJ^1*vv~5Y4H@<BJ;`XOawcv<WEpGtbG'

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
