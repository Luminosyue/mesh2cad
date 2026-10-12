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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/00790c705e4c4a1fbc0af9bf5c9e9525/part_005.stl', 'relative_path': '00790c705e4c4a1fbc0af9bf5c9e9525/part_005.stl', 'source_sha256': 'f8e18301c127c13003ba0b3f55fddb4fc6133b0c44697825e94a3376cd5abb25', 'input_faces': 86, 'input_vertices': 88, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15670713782310486, -0.20466962456703186, 0.15771596133708954], [-0.1552829146385193, -0.2025901973247528, 0.15981069207191467]]}
GEOMETRY_BASE85 = 'c$}q|TWl0n9LCRX@1>MdmTk**fVNvoFZ2T4-ss`h0;S!RQbB_<OW6ekT4*as#AIH?CMXZ`;DaSujlv5kk}BGmFvfaoVxkr_k^qZnxdh7HV!639-&bXfCPpWje7}DA?|1&^oH>)Jw>BcuA#hC*Nong&=&?c=cY<(;ZT{Bw4Nd;Gyyh)CY$D0@jcZu<);HF9pRkE-;(6Cve_K<lt4wiK1l+D1#T962ZEy88uWo5w>o@#r-=;Qy*l%0!+u{%Zo#l4tC`HqAloyo$dc_;93?=p)3#;O||COP7z}-_7R*k;gEqV>r_LQ4`@I(5c-^_aLqgke}9)YhGMVj>@waWCBYUbMq&HCW3BGV7Wu|7K1tXBr-q5j>GrmyX|W!9@F3ovdrd=YwR`l71>eWt<>xzT^9xy<xsG<^N~2=t#;WBP)=?6IRy5BnTSK>q3*Sck5esQ;e+i6Qu}VSUuM;j4X7$ge{GvIV}@eFyW+DnWiJ{NTZB$Qh4({oV+yk1fv3QQH>6zXV^u{VVEoXJgz>`0B+`=znu9>izJ8?N_mGam=q{&daw=Umn1I$tdR3Bw*ari?Ggb#bZ5pWBv6#sMmMF7e@!M@7s~Do{K~N<(u#?vHmmq$H$oY`gb0TdyM{G_TRh|`*?u<4&<w?*mvDY|9$3nVIAbhvDSXh7NVcZSW7>$AL}m)==UXK+$1l??TN9hoA|aE^&Rl_11Z>F_j35lVl3+;wNmui6>Z($JdCR?ryt|QxJMe`*TWBSU&KzFFZoK8<vG-DAzv$uvOEvk*OlmJFcLYQ@n(ML#g$lxnn=qz5>C|X`S5jT8s;^31;%|CVR>$~^%CR$U`IbZzv3nM@{rwnE~@8a+<5w5Ov1VDT!s4MHazEd(WkoqN%$o;%lkymT7Y@cA3oP&RW<y54?i{iGkgzpE=HdL_=4{-Z5*HHdie59^dnC`g>^Xp!1VQ@DcF}56*;Hxqn_^vZ2-?_@bEp;SE5m`_o7~X{VvA+F&*=|+=M=DL#D4O)37fa;VTt)Oh4#zAtz=X>YD~J?k~uZNB!vM;w|LwoQ|A#HlUwV@MV1_a`q!f>$m~mgM6(R^`XzNW4?>I{@rU(-wj{Qn}PiE8?inq@MY;l>|@GW?ANo`;13{Qs?VVQ%K^+ckkgBEuo?A-;ScY-`~W$jr>|J{MH~sB-gnuu&T{2?_!;!mb5TFojGQYMk>i6e`&!V?p$nG%)t^J3TK)w~jyiV>avIND_EE0cg!-%fmU(G4s2AJ&E&C|0VZNH|x2&gj2K`89zhxhTW9fhMGy30Gh;bLTV}HBPA*Ue&^$yHedG9C8tAX{0P_NqIi-TG4%Q>&Iv*>?&0s4Fc_1ei0{7&?#-`t9MHPcU=2|ttd9{7549`fh3^;CH+Uq7#&I^NY08Gdty@3`>SPr&!cr;lM8*RcNmr_YAsfA{G#`+tA>%ntWZ6ut|oGs%VI0%{JqfSgO6PR=FIpk|V1kX_ViWEVMus*p3tQ>hclQ^}L4<H?iA6R0WV3FK7j7;-AvNgYLYk{#3$WCwXPHJUt{oJfr%Cz2DWc5(tamMX~n0v0h;8##s?PmLhQlSfjc$Ro)~)Hreyc`P-VJeE9;nnoT+o=lxWo=i@sW|7m$+0;C8HaVX<i=0m`rn<?+<PvHbxrAIwtss|@%c+uFPOhZRCs&f^P;1C@$n$s`yol;08@i0Vh`fZloV<j*l=?V%DY>4yf?QAbP#eh}avimSTt}{@K1MclF}appO<hQ?CeP(<a20g{*;{L~J0kw+U${Rn&3G6s|Iq#Qm)6(cqrZF*&idnJ=&g-1&Q16**u~bcequbq;&-~wO``'

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
