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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/0c4e4a0b2a374553ae762bb33e8dd2d0/part_000.stl', 'relative_path': '0c4e4a0b2a374553ae762bb33e8dd2d0/part_000.stl', 'source_sha256': '3d8611f9d021547c066b66fcb3297b9e2ced3f4e7eb6212e378e947ac0994340', 'input_faces': 78, 'input_vertices': 65, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.16853120923042297, -0.12965473532676697, -0.30863064527511597], [0.3725041151046753, 0.06663674116134644, -0.10049726068973541]]}
GEOMETRY_BASE85 = 'c$}qH3s6;66g}_|e~5e)LgnIzhwxHR<RPHmNwdUH&nYuY^C3Reu>e6yEb>;P%=EKxMuEg`MMj#X=uC(r7yRIlC!qM5NqU*7P3B~SGisA{_d1)>re>PD%$l{%VxM#N+2@>lpJS@UCq&36O1L%!rj+^$LGTkHqQI56d`YG&e?)d}p_d4NPfr)GpD}B?V~&?75HDI6y7DvgtSO2$Ei2h-Q><AzdCT)MvghaIEp(ATIpeu}m+9v(&d7C{?U<x7Hf8j1n^L6w*Qb}6f|^}&XoAVwmerpS>+8mytf$;+Z#Gd|lmzU6?_6<&eB<G@M-acDYzwjRXoZ`6rTts@>VS3S@Ei8Ek?&mWf0Wuz@1|PBEpayy>w{hJjm)1vMZefHC&<^{cpkpm*0zV*>do}S@V{6k$GNkw68W@`YeAluUWTtvyRnzro;4GXV%{BD$B@5&_#WB5b`bH86vJ0VXdT9_d-WLdNmY&`pVM`ygF5DE)In)vf7OqlVZ543#2c1q_@dFj9{mgNB2U%w7<^^##t)Ehe0nS5Z3p1%{uMQd>wEP8#&5nZ{f?V5AG_-~c-|d3{;tYxn19h>)JM6z^aR?gZ)0B7r-!W1k$m`yUTDA{<wBi}3qzWbM`HneJ-7n#`eYk?@txOxwB52k>Y|D8m8wOESH3=reHXUJ;Tv1uMgGo}%aFggGFy(*>iaqR2{+=MnFTU_Qr$=R|LIQbm$Uda8DH}P<`uEKv0i6XIehg%`+KOz<z6^HT0*V#C(qdmj<1#bdGRawo`D09r?aK=5Y~I}lAL#Ksm$M)DbL%qDmUhh=(`j3@C!%0^T}P(uS(sH@s{Rdf0gr>;cK14FrU7rPOeu3pTzj>MaW;vNkRTbUNn5+)4de!`l3^)=ecC~>J!BnUz8n^`x2in{rpDkqmp<S`yyIb$Z@vk$n_>R<9>-ZS4scN>?(QQH@oFIS_5CZ-e&{iC(T3Ml<He@{8<;?LcZk&@)0Y;THxOa!ueDJr{H`#uSK`WeGJ1rH5P8ddC={4`1;OJtXJ7FO5T@WO5tnKHMke*<}$hOmD}JO8;8sLc&h_-)*ZX0FQ(v}dz$3AGQw)*I5BBum}kRJ$VZtgeevu2^89<^Wt|salKDFy+K2Uzoh|G6Qf@2aOB~N2{)Pv25c5~UH{PznIn)ATaSpYEufz9*_+h`axF2MEb%Pv74MF{#>*abqq35N)SF1q3y8$xK#&6(j&F|oS=y|HD8F?+MYD0hDD<5NB_C(xY!@di?`bxEq@hs=@p3!D@w8`~OM?LlZ3fARmi8uxS`%dhaaqeQXT-Pl49{1G}__;wc|8B*n;WzaE5dD_VmGK?7;VTt0<h<q2;(llmXU`)4->fd|--4*)^^W_#YOM)ANijY`5PF(lwXBSLK51mq)5U-PNn4WmuRdw^<p2Fii!^f>U?P=y0_#-P<C#^~#N$|xXC2KvoHen9wS~(P&FsaRIFfZF&qq4Q1eG$BL3$vA^e_hLK@8IU7^H(4r28-jvF^d_!yxU;9K_m}bx-C{);(GGWsvUA2*uV*9>_Y1bsY0B)^V&yFi4MLkRHiAi1kR;Hs*e;ZL9|~NI$?J9l#vSI)HUA=02>u>Owl)gw;eWgLEQ;bTWf<0)w=|ARWjc-J3a_b$4ce=5W^jtRontW0+%E$FPoPkhU`?vbM8MVUSK^PG+6PdMtx<5_1CUB-RfyNDpOJSPx|##vtv-9LU;_bvFiSZ|2^tyXr!k?iAevx({Pa3^6g<gk!3gcZlVmemej8Xmqje`yu_;p7+0=?(KQT9P5vlm1Al*{Oa~L|CUjqC`<7>Lwk6m'

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
