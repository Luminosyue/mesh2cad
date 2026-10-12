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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ec56d0baa8f492da805fcf2ea98de4b/part_003.stl', 'relative_path': '8ec56d0baa8f492da805fcf2ea98de4b/part_003.stl', 'source_sha256': '136809483a539d83189a9bec08b1cfa163c9effcd51b4060725e2f3cec6998cc', 'input_faces': 68, 'input_vertices': 62, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.01347561925649643, -0.14616276323795319, -0.20218326151371002], [0.0926131010055542, -0.12315890192985535, -0.15234901010990143]]}
GEOMETRY_BASE85 = 'c$}q{4@{JG7{`D75fw-j&Oi}(QRF}mkpG~dZ&4<(^mHOC$_^1iNWeQsP=mecfB*+5kigjO1{p<ZWJog=-q6IBtI2FRo9n14wqT{Lvdyx4zt3YztF6_`e*1p;+;h+G`91G*_ntAs#Z@Qh3Klg@F~1w#gwU3!(224<^X?tFd6vlH(h4Ur7hJpUYRme}CyY-zi8Aq$etVuJ*Q{SD=~MEP^ae?vUt->E&MAJj#JoLE<7;!Cx8ymvr68v?&+&g)LX1I*4L3-Y(to|&wHo|88rC>Oz53~g!<vdU=QI_~TlZ;PNy{hREEBKZ11`OiIHLV8|HSb@=0=T+@leD|!)e5CCO09^)^fzFb(BXb3g54Bd+Qy<E2Wn|#_KKn!R5pPiobatT=DGyH|4%c`9sEu*B=EJ-oL4+r)m@Jdq{r(dB*l2j|h1jT<z-uSMFrezWrYykLbMyZo2pe;w94%@y~w+x9NJ2-+p}KDEP_f7R1k&sm{I);PSxfR_yB;i2SzJO5~9XSGS>WWycV&L_SB{;&l*x=)OSptP48}{U!_C)D(t&B|C9Bbg~`y>r@r>|En76=f)}G>N)Cz+(G<&TNn7=8p_|P{|IWjO+5I>FwPSlM*N|Nt?19|QIx;p#ZkI%SHOiw3G$mV>*&09Qo50+unhS{yZH?2oy-DPvTBiEexwv!PHO;{PTZ!sGPKZnhkgLJ7sMgIdd&(hjrAWwo`Vy}V^R;C#_Q?h#51-bkG-)CTwL|)MV<Axz~%lQaV~rRGvI3Va^zP|-U3%2`vhFda;0;nhNDhp@s|`|K1h9A9|JDBeBQ=9L>19I`0>71Ea0Z%i!`4VR&bNgti!0sEdu?tz4-z572mD^R}P!#y!!^hZ8zeNAitNH>U@vtG40F-7k&ZAW51pRZcod27kp*}owug}``R{b0k@~OQ#}R+++LUqZY%zt=BnTwiuc$_yvvpD`^$|~|2&2G)9Ezlg(v8|nV*5nPrXI+)@P%0ZQgJc{rq_xT$CkH{k}$U^-?9}S+I`gA-i?}@jb86xvUk`XVCyI*SC&PA9XZWDV^YI&{{gzqn^|ULl?!{H&gtj3DhZNTfv1bnC7jf2=VHmjrgT%;;XMy{E}|U^W7B9^T1`Aw-+u@e8?2_t<OTAm)frfQIByE&B^5uaA{!M`-o3INT2uKN$Nv$9r0aTsL$I+=)6N#aP@2&?dv^3{Tb^cUQYF>;m0Yy>KM3kV=wW}(KExwX-}hHMs}R)cM(EcvmH;P{G9t9MH<wuyZZN!q8)Mn?opKVzaK@595pP~`o>H1p{&c;hq8}!tT@&f)@AHt*vGSmv5#k;z#7gzfqg9Na`v(8qgf5?quH<ErTHk<CG4Zv>sbTX2jI4l*Rv1drTIWsKlYmH*axy-$U2w(LiP{x(!4k81MI!od$G=D@5SDO)s?*mdpA~R_HOKFunP7w*w18jVn36;JF5$OclL8wXR)8d-iOtby$^d|)_LrG+55B3XYbEGh;;$`AofdHCH70%N3e#nk6@q38p%G9eUi90i%GmRzlt@6{VMjUtnutMO<<qOK7}=weG2=PyfmNeSjG$|XPwJG{q($dDO%&F{Sf`@JEwn5-2cu-N3K7=G>jQD@T=9?@wdyN75Me|2gz7%YX'

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
