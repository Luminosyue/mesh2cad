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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2dd2980caf87450d9ef7e42adb43f2ca/part_007.stl', 'relative_path': '2dd2980caf87450d9ef7e42adb43f2ca/part_007.stl', 'source_sha256': '4cf7a6a9361a6ab45b2ae15b39ccc840b14c758a8ac45e58607f291845a58650', 'input_faces': 126, 'input_vertices': 84, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.34722211956977844, -0.48611098527908325, 1.4901161193847656e-08], [-0.20833322405815125, -0.2416640818119049, 0.19444690644741058]]}
GEOMETRY_BASE85 = 'c$}q|TWl3o6o%*Y2EEX7X@SzBQ&0}nS}46xYA*wnmR>oO^r4B$9HFHcLraS&F@_T#OiUyg;lXIqG+q)ZiIE3UV<LwHsxby6P!Z$hB#kjKVl;hF-`soVTf@v)6Qk3t{Qv&Xn!W$MX3yT!SXX*Rq2XR-#!DxEylyWv3>|q!p>b?*?C7EWgX5KlM~_F0#g48o!PC9{J+Xm^am;uodSGyT|5&uaj5ZF{M=Q+e(8$=)vH0PABVz{!wcZwgVti2P<HPaMLDgPgUsGXLZ>TVzHUI0Cqb!)S^<Q38n0RIC>x-_d;bxz1u6q8KqmSP>)1ndGI#T+*bKlJL`G9`q%6E?5IQQ0ky7}6f5B$2_aP3=-$%h9%4&<X7W5IEaoJYTLe!pCN$*-rfUERn#_oQE!d0C~O1o9_4fB$N}e9^=GTT+KdLOxHOa(y+0=8JBJ=4*jT>NdHrf5ypsv)3KJaJAEa0zG-B-l>~KzUYaGIk!H)oqOA_8!eTtzJ7MXuUm6jZhfjwz8vUBp8M0IF9!1Cy|?Gf7u~w^Q^4nBQPioMJu>rApnvqRAM--osb|uve?Q<KJrSB$a;Wr{f4zD7+-bL-e@tKU>rzkiofDV+daCsW*VoRg(^|Jf^-SQ$4%O3QUUsOSCUvkw^|XqNq@$ld^10KV$h_fTdH;KU-8^{qx^v&b$1nKxM9FhsICcHu#D`k9q#v0V>qPXV%qx^{{29OL@81gbZ&L@+Q%@bg=G;f!y#CSc(74v^U#>d+QGZi(Sw9=y^&|Qu&+Bjb%uB`<U7nYPPti^0Wn~O}>ep@RoO*pWpj*`0Cg1S#dG5cu>rM1jGw;zlcioC^%6r7Tynf_8I_kbhqI>H<)Q_xld4I#Y#X1yS*1zlnsdv%YAB>PL^D^j1beUJ`u)Cf`m-U?d*<H_~d;0_H*~{noro#C$U)~pEYU(p5U-t76_H%S^-_BqkMz`;tN3mv~o{)Vzl<%EWqrv`VA5Oi>J}mj@iHF#?C11`NspnaA&M$*}(Pi8O=T}nlIUkcZ-F}jxekSqb>D0#x_2bot^GI~>xp1zD?wxBoKNk2pNj~;Q?QoVl-&JI*ualv;@6$w!`VyS~)8tUizxp((+FbWPzfE$M=-R4S3YNi_!j}=67lLcxh43P9ExZW699#ik4lf2*!i(W0;3{|tyi^5Wa>h=u4X%GHAXnoexc0Mv@ik_{8&!1a<pp-Y^&GR9x5jk1rDBhY7BB|i!ua)I8@x_ME5En$+ZH@6Vy+q^@U?hb0p`LRRCMCE6R(YU(%zPUY4B|-`taL_SIuixbmOZVPj!qP;hAX6@jahho`c3b_*NCW@U;t14UDZlm|zBcyNbQ|+KVU6n^g4Ts~1nTjIBKsfd+gf9#(<*@Jbc!_-e<~R>syI%D_zc4i!E4>cP`?#?Y6%z6;@cFWima-FR(cZ0(^GEP(50--fR?JXJEb_OJ$A0M~1-1796@+QHb`!!j@n9>Yfq*bFzQR~y*w;}O~s>LYv+ZH=8iUO-!8myhSu&d00pJlc8q7oJNympTj2rmeBh#~0AnxW~scX=gHj;Tg0usD<z}+G#v5;pwzBcKdi1ZH=uyzL2)Yo$!q+qAE6l>*1T=Rp17A6?`*zAAB>s8oVD~4X**$!E4~<U<JG!{s5u*gDO_5xJSie@LqVVE0R{2{!jlx-@Ougfdu}c4&NC(-u!n?sJ^_zF4mRl9C2yt?})-}dL<cu0q{OTKm'

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
