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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7fce3003d95479a9226f7cb639df893/part_001.stl', 'relative_path': 'b7fce3003d95479a9226f7cb639df893/part_001.stl', 'source_sha256': 'a0f2ce40b37a2cc7d67be0b5c9d16992ebe19f8379aa95a34d270b4f67fea60c', 'input_faces': 116, 'input_vertices': 88, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2964036464691162, 0.21142345666885376, -0.23755155503749847], [0.20023518800735474, 0.41006314754486084, 0.2590872049331665]]}
GEOMETRY_BASE85 = 'c$}q|ZEO@p7{~Xng|;X3N;$4V-?ncYwb#NG?zqz0mUpo2aVRbE1F^MS(<TJ)ij9qEHYRFJh+i;-NR$#{Z2Cb!p$160XQ{Lo`l8}d!K60$#i&V1&`3f;+?oDonH|Q&=q6A8zx&_pGc(WZ-0X!Ll9FA@{8gabJTcrBOH~vSixijA6Nw(_YL9eR96a1>Q!=PeE~dvr%}wDKZAy>wx@Ui+yFKdJpn7ULf*!Bx={OWU5^X#9(xK@72=TYI9q5i2es^cv;fV2hRWRsP*Oq$KH`M=nImj5cKln~3+Sfi_N7R=54$=C1Yb^fk$9K=`5?_5786?{Gp@aI`@6H>1o>u3sZ+SmfdGwqv@wHbsUZVG@KTYxZWA8S7rAz!izjK6+Yal@V*zwnXp!eT&_v;d0yK?`i%%81ZcvhAtcGdd@RmbH?-mjnDdy)2YVBe%=UJv~-UE-?)e+|?8?OQB)w8jTLy2MvX5@%@ptECe(-`s^;mU#)jIWNIC=Oy@TUd-2eYwyVNGhfWld@(=s&HTUpI!^t!f4Rlijrq#YDR+2ZJ9&QIKfPj_uaD@n`Y>OMCvMByGv91qJ}~ch&L#NgQ?tDnm-Z|8W*+!Y^egzRz4}=wE~^9c#X6`n&bVydMW3yU=(BYZeYP&l7uQ|%#r)#Bi@v$;j}l}2KAr7vp`S%xEzO$WALsUsS=J?d@k`n+@aL#(zlgrMU!p^!mi_q0_t$laube#*r<(qjC68JEIlDDKtB>HD^$~otK7!Bcqnv*Enq|Jh1pVEZJ$7H`>r>x#dtBygS*NDx_bF3D{JgYJm)+21e)IGM)vDkXzF%!JWrVi>v9F(RuMQm>m-$L<(|o`1&GmJ6PU;e0yZga6e0$b!>tMmxwB0ACdg~<P(ej5+)=B2|gwN&`*z-}Hq;8_m>K5ym8RYY@=S1|)=j6@Bm-#&Gc@};4Jhyt&hb{SWE{Hxm7qrjczsBcb=bh-A=iN-`x+Oo(Q_*MVsWv(?YMB>)_h$Pt$1L;0`7ZkGeAhx};=E7uge`ABmnNe5_ZBD$i8SNwr=yK~^&uv?n95&$y4L-xS0A4*@IT*u9BYg*<QuU8LAVY<cnfqZILQbMonD0P&~&gJoB~}3P64lm)`C}qYoHs!HQ>$A?cmMeozMpGPH+=+7q|($8~OrxH@F452iyYQiy+(#eI86S1a1b0q0fQC;6~^+a3gpJv>v<zyb1a&coVo9x)xjwuE1K@us%uPWavV0GI%kx0$hPSggr*AH$p`a_Cd?QK5!w_4K4)d;@)iJ^MEs<PH-kT4VnwiMIOQhMpPQH3PCssUW)Gvz&TI{I0u{o%>rkD^PpaE9=He^1P9SC;gv=NxOoLo8=}vE*MrNT%fMw|H}1_uzLnr5&@}K8a4OUdb|X(J>OjU<iXdDC^@6Lw<!IyL>ghtwh&}~g3U)xB20Or6&~k7&@@HY)ecZbEP&=Z9;7V{2+T<vYpEttU&<t=k*a^)8JHffoB5)D%6ZRWXVni{5@Nxv<MF_$x5G9yXIk*by=j!Q4E&a&L>R*gn7NZXrVmWFVZm`*1N&oa$`SGQZjcfViEZ%87X81cF8M(|uC)}`r>~-Tu*{-}o21%->{0;7RO|<'

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
