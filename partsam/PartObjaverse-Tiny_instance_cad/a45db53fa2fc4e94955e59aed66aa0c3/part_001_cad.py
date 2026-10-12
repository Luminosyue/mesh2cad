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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/a45db53fa2fc4e94955e59aed66aa0c3/part_001.stl', 'relative_path': 'a45db53fa2fc4e94955e59aed66aa0c3/part_001.stl', 'source_sha256': 'fd62a471e151e0f34b57f7bd1ac51d4535936de53ac8e7d105eb687fdca409e9', 'input_faces': 96, 'input_vertices': 76, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2750091552734375, -0.3953119218349457, -0.0820242166519165], [-0.17686206102371216, -0.11326411366462708, 0.12738627195358276]]}
GEOMETRY_BASE85 = 'c$}q|du$X{6vprNB`wegePPRE`k>pT5Bi{wt<X+sX@O!bMx^y0wrRHkf(6<_q68Tc6sbv5L~D)2svrhKvDFA^7j~&gv_K;&m|_BJBqXSb1{6#n#kuExv)-LxVsw&|@3-Hcy>sT?v-j@S)dU8`FmWZZ=|`U5+4m4*Jf^T1w#C`jv9`(Cp540f84HUfpI?T)TD$Vmx&{l|!nRtQo$XC+))K|KprzQFsaRV!v~{#KwyxgL*6iedRpa`0r|!3}Y24`4U#AxpW-9r%Ol6z$U#~D;gQxd`TNlUZ@^P-}mBazJ<SX#my&+eb<g4w8-*MHFhWh1v2A^f$8}iGym0cwL<@^D^eE5B1fuG9x+Pju->HW6;m*jj0eD#v;h@8)U?f!;7XD{vHzH)Q>SMqad`#L{%OTO`3+SBQ7IiLM>^%7U_oc#lGzUPMUwF&zPIbX3|5cM?KKaleod~Iy_m|y<>O;jg)b9R?sK73UPIV$ICmfK&GkLU8<$rApJo)c7Om5at#ryU<7-#g(VUA2q+zPr20XK}YFU+Y{!>*y`pD)N&@PSW!Yw+xa$ZKm+;ji1ryBJUie@pIyZzoGs#-8ad0i2GVaH2EH-d4%d*H2glT%c=-*-)Co>qWAY*KTLja{&{+Rt?~?w_uMwBQ;Sa^U%Oo7rhdqIjOtO6rjyU!Iz;uW<xf(+cW#`>zj^s{TIbhVDc`dqT#O%FO!a$%_E9~mGmLySJ)i3LY~C*F-w`D82dk)l7Udvc-Td=8xqsN6`=7Wa-`796wH`TN&2>?qsBhmIl=B(<KG)upe)&yZ)F+<3)rbA^;XAI69GCMw6N#eF>(6$(AK*LsBR-PzSx~QE|1b;kUr3;JVLNAjNb_m^k$f$$Q}n~pIO>zW`f*X`i=DJys<VN7^}yY;l$Vy_q5B>zqWO26`h$G6C{L_QWexdS&nWq<b2s^HO|4k>?_I(lZKZWrzAO=ayKcSk&xLx#b0&-XcB~WQzjKVn(cmj1Pm!<9DxmdMy&0l^B5OqcoJP@yA*tl6uHQ!~|CPs2i+P$y_jOc`3;)jmF+Zg#qRw4!kng#AfcnJK87;ndU9SuOiEeS<s6eVm`)vpLY<YvYZ|ePF%6~aW<PZEH`fc?s^4YbEU&#Gt>{o_w-meVbyk8l<dB5_FW7@BL<Cyj<U%qL-^5vWME5kSMSK7Mw&dASYoG*rNK1U4Se2)0?P3MR&-*k=`zWE&S)nhtGeB;RHNS)v5Ub(Vlm<8*oN2q?fw=_yeJH5e}Pak}=ubuy|j&}S1KiX6E8qyg586tvnxE_(vbZ8oQ5mbeyfmLuRG!<M5UI0x7KSEQ**g|Lucp<n9ItN?^E=O>-A~;7NI8TM9fTw~dLzBRh!J(*&*B1tz0uBRP5S#;{;ov}UurzmAe`5YCZW1&K8VQa9+o0)SW3Fuo&J_sGH3-hjpelG7cnP!=yaZf@`R8+8iQv2#S_WPWu7;L_tHDcA!&20>6n+KND%EV2p2dpiwqnhUd5FL~O#+8Nr-DPkLD0$IAaDRQ6dVBNSF|28^oZ3XUXM6EW+OPyf=&m|0xQsm!3uaTf^#A?795LvB|>w+iQp_~Avg;>AHlguk9<7}^vH(J180M0A~+`?IA<a_=OH*3Lkqyg;1XyNxCCs67J}{ITxbqB7n}i|0nPx&K%>E2r-AEgECDfr|Mb`B?@QxfKEFRo=1=->yYeTm=wtad;kue&-bZ?K1h7qf;dm#pzW@)L?VJ'

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
