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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4d33f78f60a245e0b4cf812637509e9a/part_007.stl', 'relative_path': '4d33f78f60a245e0b4cf812637509e9a/part_007.stl', 'source_sha256': '1ada6f0d904b6b82f3367097b89e309d123dcf9a9bbcd8c47a5817480e16df46', 'input_faces': 120, 'input_vertices': 92, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11343404650688171, 0.3707423210144043, 0.05738513171672821], [-0.07770860195159912, 0.39264461398124695, 0.14254631102085114]]}
GEOMETRY_BASE85 = 'c$}q|eN0tl9LJx_yMTgl<wagRV0clH%UcSha4bQB)Qbv)H3b#TazYo!da>;c*OqQsN!p|>ft*__e7SNj!?<{?t=7wGbERefT&e!aWofZ$Ypdtwd+Xk_Ut6ogzWaTj&-Xmf{oQk)!#&s46d7e_>d0fSRh&Mg&0<U_k=a>amwW%79bLV}`+A<Vv1G}`5v&92Th_VSZLE(y?bzAXyTk3M)*LH$RXU0^$F6Soes|}-ZQbsjU4qwl?(Oa3y!VmLo-RHvtST$g$`==D&uIVki03UBk@5aZyqYgvyH+cD+WnTNmf&V_U_w;g!u6y>rkuBMa#C<sb5Ze=UJu1t?M=CknIFzO4!$7QG2YFTykqT*T4!^{If|P%oL-8vy$$0OH-6hTDc7^E^Jd=^#fP%rzbx1L`lGi6ANonX-;S{b=P1tZRC_6|pK2bbxN&2z?8lrA=jOn{DT)sr_(b+&{Cwb|yl!8$d?CljUsj)sg=?Qatgh#Ho#a}-Q=MO*c822Ym7^Yto6}i7l3y>U`69pS$NIX1Yy2dCbSugAAKWIz*|8Px$m(?}zP3`WbNZy(S7YH^bMBPum{)(9ke_dHidsLW;0(oCR)LS?H*3`UwQ!@q*-vqE<6|V(W@=>r`tBo=o1gWn^AED|P#yr+&nHi+`!bvx7Zy%Yyd&y_+$W}Ewc>iKT7Mv6oZ|Y49J#(>;l`^aQxxxT4XgDdE{)6mnSMsCKlA!1#f>YUdrAJ`_hH-&a$mRn91RQCM{ZA&+@0X3I6GT!Qao@fR$hOjp-1w-@QdnvpJ$Zf#&p0-ar64GlIs?(Z)bjzZ^<Be;KwA@&)M@nxo-zX)cMD+jZ)k^((R$R@ziZE$r}@Vp<EC0<<G18)WY@rBtONCJB1|Ix?4<&v*vWQ&u6wv-jVYx?z`_sDQ>>^goosZfA><{=(qbwo;xVt7qh<ZbdK65J>_Ha`lsc6DaXe;M@e41%tP{{Z+J<5_%g}$TdO80ZZ=<3-$xeC8n2K%(CRQLKJ?tT@_y8P-&_!!4M(c=qxX+e+^DJaP+T7w^OENeeoS)xYNNW&7S2*Wm?U}p4Uz{&oF>Ih^Va2BSJ=~4?jH??7Q?q3*DU^YwW~Aq(JDrr7OeE6)t-uf^=MUER`Nfet>P1S4|BP)QSX9};ELu-K%EOOp2d=pCnFPnA+q`K$r!H&yO--e)NDxjEY$h%^D!?AH3B{xH32mO-o@3<RfbvxzXe${d^^Sufo+7}f^h{`HFz~L;S0HnkQX5nK9wsMc`h>H9b8M1FGZG$o~n>nA#<RovXGvFy;Q)Lqn5#!VO}|EDtrZMA!;go4cA((bksa}v3DDgHy{)Keq=g)1IC$L`QZ7;gcrXMl8`4M6W+!Zg**zG@Nryokk3J8Ltk;|Ee}~7dJ6WdhxC#OpMjbVpN@GMs5baa)LE!D_;p;ZTu#&#@awtSkhdWd{y}6L;M*`R<*Ed)L?-+qt|iEqAQL`?D+hTFGT{rj79(GbECqcPptlvs3eZ!q-wh$Xl){&wI^ms|SAv=XUy8a2H3j}2t~FeC)CKS>x$2PDArpQTS3UB2WWuL$X~;EX!pCyWMm`&v@ZyL>9*InN@ozH`c_K1~zGBeZ0%S4hDcJ9-kY3W@=b_r+?U*+YmBFW>#-cL#My^d<%TVuz-;AsYeiOzmU=P4=#<-YkIrws9!n>Mm5%$P``sx1nVTcVK_Cww}GyH2Qbmmq*{Oe1~)f6q?cLe`?oYx6)=dwQmhxAxR'

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
