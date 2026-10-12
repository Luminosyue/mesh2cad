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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2f7852f6833d4eb69ee3f6ef5fac5738/part_008.stl', 'relative_path': '2f7852f6833d4eb69ee3f6ef5fac5738/part_008.stl', 'source_sha256': '658a24c8cf906120ac8a12cb99ba84864132a2169d5bce2d317721cc9e7846c4', 'input_faces': 78, 'input_vertices': 61, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.14076220989227295, 0.26593607664108276, -0.06746681034564972], [0.04564013332128525, 0.48566538095474243, 0.17242549359798431]]}
GEOMETRY_BASE85 = 'c$}qHeN2^A7(W;8y>bDO_>?cXc)<&L1&yx@IPUw0U=3`yBDb1>OfIQ&f?S4cOnog^=~kH^Q%CBJoEeP;h95AyyrNO9KOC7KL?X3nS!*~J7L~L2Jm+`qy?3{*)wz52`<>r;&U2slyw5r3bykJy<Ctg}?9+8gv34V4+#*>VYjd@<u3zhN=Wc3#UdN(I=go)v9(!t~^JyJxW9`-kmwRoCwbX1~)@Zld%+|)Hme!W~O?6Ez4KA)%)^BvXRNcL<zS*Vrvx}D6%=tMs^H%eJZQ(qJ?fRiX737pXHypfg>+R+!d8aOLUAb!?BYk9lA4lc#yQH&@yH|PN^XF&}jk{L}|H9Q@(fqo?Q-sY26pBBdN%7aruY8}Q`S%9Wr5^7!tv*rxtnmNlz;&AcNnbBV+4}_PN>bZR>Q^5*PjSjELO-V$`QQBRMc(&poAHu<dn?74e>`~Fq0!}vpKfS%w#q7W?;#PVBjqfOZ;2H8+wYBO<NI`G?4;*q`K|#+5Z$w_LZRpAa-S#t>&+BjntGLVR@O+m(kfGY=@AS4FVjyB1Y0+su5^$2<*y{ZHV|w*19hLj^qfQJHPfS{H^pBfJ)z?q>H2F|X#Q_U=slXFc9O1Ko+N+IaO_3O=h0%)+2oloY5w7mZkq3$JWKvHwd3?&SB-o~{$0mNmv?oEe9Cuqk>B<?XDCi(FV&T@?-_dU((WkIrK4Nue<%LXeMHYU^L-!9oBEj6O&RR%52mj<6f;EmXMIMxB)vfK&A%Amq4@R)(&a0wNtf?+en9&1H&2nCy!Q*z@0@s@=52^2omu-t{qMKXzF<rHdPv`!L-jdfiW%1GO8-WzgK?1Ztt&oB`dq^Z`5l{i*-v-;Eb^%gr}ccGS0#z(ZLJv6`b)>d#lG87(W~|M)uD1S{Gy+KO`h0CvlM^5|2pNVWUTaRb@~1eBLB{Nr~Ujh<8M*^pO-h$dVCvpG}t=$^uTrS>GJXp(xo>pQ60)JweJr09_9PxJA%~%lZPJ<T5oquC6v$fPSQQMszu#KuYb}Jq@Ly5D`ZEIeIc{yJv1+1|H=`=hef_c^t>$h>ILd&je975z<DL5mcK>)SJK6KvfL`phYh7Cs2^~yDw(xZr+(+K)9==){k6R`ThACblX~kk)@!aDF7oEX;8)K2f`4`86x;vzl~bnXP{g-|YQ?HOtXd&37d#i^g}@?kyJ`g(=ePvi3S0<W0=^JD4_E-62c8eKgXe>n087D3z?Z=|FN2jLzf#O80_K9xQ7u)qco^pv)nZlSuP{Nihrqd}N8f-k19Ss)pN~m3et*XR<A5gcIPe6R2{BBVZ$SB^sAdG3!8y(c=NJKQ1fLD#JPJHi;}eS593#OwhH3tjw{&0_csh6njPqn*Bsj;p;92ln089o?hR*^R=h?tW@NDqKz)<kT;5OiFa2xm{U=;Ww@Ej)Ujn`r(FbzBtJP8;Lo&-J%#<>od2Cf4SVWNH#nW(8W{Kq^P=N61{pHx^PbPM=AU_5vlFa#J6?yS;<#D)ITr|sWO<_Y?J=myU8Kc2KR+tgSO4l8Gsfxe1E)Zb<mN9pVIFCT?M`v'

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
