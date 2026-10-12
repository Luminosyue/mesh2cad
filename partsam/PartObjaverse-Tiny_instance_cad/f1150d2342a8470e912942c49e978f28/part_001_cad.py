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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f1150d2342a8470e912942c49e978f28/part_001.stl', 'relative_path': 'f1150d2342a8470e912942c49e978f28/part_001.stl', 'source_sha256': 'a3497d6312433f676ba614da6204fde9798906dc85b4dbbaa895d94554488004', 'input_faces': 128, 'input_vertices': 100, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.49999991059303284, -0.49963515996932983, -0.32038000226020813], [0.4999854564666748, 0.18495985865592957, 0.4620301425457001]]}
GEOMETRY_BASE85 = 'c$}qJeN0tl96tAQuY3rlso-}P&@Lz-f+iy1O%nwKZW<q#54nJs$x<+Iu14vpjX!ELE4P|Ti<%{D#+sR9E9XrXq+&Hc_)6p~2V2;mWUIN+`~J@J-p+lwZLJRb?Rn1gyzlS4@9(_tIfv`a3$n~t^dnjcz4TtU7OE&b!j<{TVNcVc`dUwOQp3TQP0Ae7`62K`K~cWbWl|0+E%v>h=GrEEy3L+Zmu63}+3Omc4mDLbR5dp3^>97AdVjNr>COA94|>>n+}h;i1Y2r+g6&n?e>}q25Zb4w$1XE;oH|12-q`ZvWrMDr)OFQTc5JgjSB3sV-EE`pC^<Sp{TGe(8}lg8y;mdN^~+z3_TyiiHRfrD?u{wG>37|}8`n767EAe|E8qL)7rJ`iKfj|Fx}3k^VlQ1+s)P4{uDAd0@~eXa-G(|SsSoZ2s)NwwItX2^gV5zV2wkp&FTYd=Sr>KijZ><FvU_Tj&T(DMyz5pV-7V$|UF2z(+6!ION4v9CpHKOjKFX7RZP=)*(6xzoMvc1i(F3Zp<Bn;-s5?f7dIPoh4(<CkP=3dwZ+gg&OTX!-Un;pm<3xV%*|r;j>LBZ)4nmjfAnT$Ij)K;!f!2?A>Hv*fD>|m%w;<$^bX96U<GPYA@~f+&&IQUZ>#EdV&M)gCzwObP4$9mAaDenBuid74ztQ|Y<&~ZrLZ7jZj=uH!=0NLE(%n+~8S7BeeRWR$`~>A0tT|8PF^}IOthb&b{k!{LQak8cu;o1Ed-wwFH}@Z|n>6mp;}<Fa&TjoVp`_~V6Myce{ypdV$alx+&nwHoSEO72)StIqt@NC6cZ_{a`A1?;b94_JA>DQ|{u1@ijU1%@zqRRl`G>l`%%kVs(Mh_RIjP@&X@3b_-d{qO_m|M+{pHIq?Jr+@X@B{2X@5B`%pEY!%iVhAI$eJ#XTVq=rGJ$6iMt?m&{$73B9i8<?Kw@lf;wo0`}KMZ{z|%<m`Qa~jwf|;Y`<GIMCX?AH)*}rhtqYnE$K85rLl(Aue#85fuCz_{lkIQp{$E_D0F!p%DV44@Jr_i%_|3WXe;}S#`#JQ=`-Gs&}Y0Kq0e~VL6@KNj*s8|iN?Pabz9ZmLF+DOh;;eAFLZhT`r1q56uLZ4q08eGx;##y%kN)b9{IU3F`<w1y1sw4Gpl>)KEJf)F8K}m{dIhz>)J>z>29ny?E}63-bt6<9`*5}y_(T=kH#tX@29%1^h}Q#@1w$Xr{C9M%Tz^|I*X-X5z4*}>#7Z(hFs)_z`&n|_3QrKr(sIk|NS(yu`w)X@hpP#Ex={q9G?N_b6>(Di^Y>Hw(`;e9pFpB7X!1vv(T6GO)PR*WCC}9XM$%SIN!#?2`mEc051a11LlJ70p<X6!E?a312=(h2j9rzY2bR`Ch+y(8-SVM8^Du*8Q@9aX$a2Kf!n~-!LtqX%tmnTW>EvI1v<fN!K;Bq;ML$&z&vnK7tT{ztYfhjm;zqFq7Z%|JkEEr$cLW~uK;~g;HSXjJdQ;?i>H8g@B|i#@Dt&2zKX?a_^aV1ppPBC9UkX=yYc_7<^ZkW3s{7~4}-_~To$w7&w{rAeXQ`U@Hl^hMKFuUfI;B%ScJe2fyepdEG+OX@aCaU5d0u`oIlT^oW(An3w$?=GWcciIDd{sDg07+yV1u5-vy8Jg)A1ahy+G~$Ff)fe+4|wqglkjkAWA9K2h+a;6<Z;5vVW6aByBfGki0=FwC3JUmTpz1_p!A1`h{@81jbW{+MwM6VM87MH>?^1Uv-SHUSmzQq-#i!FeUH9J~^|0$2uK0bUF&1usReV$?MPHH*NwqfpnC@K?eU_s5L-@^u~$e<gS_FcF;ZwRPah;FZ8a!}tp^CXV@r`EtI7g)`4&o*(p2KW+SdsJv)?KXk}F{a<^=p3B(+@Vx|`c~*M$nc3fq42Ss+RQ>`?Sp#7'

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
