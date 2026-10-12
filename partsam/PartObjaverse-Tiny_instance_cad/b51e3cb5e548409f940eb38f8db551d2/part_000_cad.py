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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b51e3cb5e548409f940eb38f8db551d2/part_000.stl', 'relative_path': 'b51e3cb5e548409f940eb38f8db551d2/part_000.stl', 'source_sha256': 'de5bc753bb78121386f3ec20100fbf9df4bb441f5d8e96a1c581c60477428efd', 'input_faces': 86, 'input_vertices': 54, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.016433045268058777, 0.22246071696281433, 0.05117788165807724], [0.0768652856349945, 0.2612343728542328, 0.05787745863199234]]}
GEOMETRY_BASE85 = 'c$}q{drVVT9LH~Y$g72l1t*Vrp+Kn?L;-o3am_%-iddI8LSkl#me7QW7NcR0tiGaSnHELKHll@uEJI1Q;VW~=?vnknWTQGA*^+Gualt+KXOBp>xMaKM_xqOhEL*Z{H#zx!?uT>F{oS5>4%g$3Pp~O`6et7TPY;I@6-6|&Vp9(I0{i{De0}A6_V$|;D|vB5^Gw_JEuIdOazJ_3vD??TE8wVC9UHo89WK?;)f?C!=-jijH?Z3${HD&HKA++Hx;yv!jPug!DwkU6bg9p)|Mf@}HQc!qdd~>`#+x@Ajhrnzb*VAdk57?TzG^0~Rk+#v-X<UX?1JRA2Up2^Pt@`_dB;vs|97tNI7d#)e*8N7buH|ZZyY24TV+I?>-WMJW4-pxdh*`+?d-EZI!gX_9eK53O7eQwBjji2-Rz6MI6{8gM)Ki?H)P+?#N%jBv2R-2PR|#~nx^y7^AnUqUF7wzGsy=>zGFY~+79xTJo2;6zstTxC9k!fW8e0zm(K5&@Hm_9%YNF){{BVs!FQWZ(>TNZA5)!Mj?4bgbL7L@Ht;w;KY6X^DEZ*Ri0n--k~e;D9>;Q${d|bW86A?mK68fqd)z$EGrePUuAh_oFZzjBr2fIkLGs$h0jZv-*Jn<W*Iuul;NSfa_wRW@dfr9fepq^5{pTW@H@%>S=j+D>*{9V@zo+ukX7buKmporlf473XzA()9ZT7Q&*)Gj{)awU%9>eZ1-}i%*x9IP49n$-@=x^=d_x$^v<kd%u;h*6CbC+fR;7RFy4!*C!xAM9e9FzUMt=#`?JJ&s)Jw@4no7ZpI(4|<fM`p-}zkHm0@Ru6y|LaX&r-w&nU-T*a%6eYEtsU&QMtJ<sL$a^?g#Gc&?A_huy`d|&=>CO|O;SJAPkuJ%GW)*4NzMWC;lyj?!}dDzO3O>^f8hRF{uue-zDXYE)vG+theMM0TCa2e>6XbxkF=Ywnr@prk)SA|r5L+;S7*#tE~Gf3`S)A7zv^FY<+bbo_g0>5)Ue!WR-=jkE~2b7WGXlfycB5#TXC)6IHM)wx&&}4G98=>7T2vc+A1;qXo6kHBCrcwf_xZU0#=a^fmLu0G8>!&wjr%xE9!|(-4Z-U95@+i0VjjgQM0J83Qcf1vIJZXE=8)~Qg9(M2V4lwL)yT3;7nvXI34w5qJ9(V6`2GUX$CI=TTrv8uNqD88e}PW4cLh+1UtcYWFFWK&PQf~^TErI7O(~N2##08V&U3N;3Q-QI0<Y<&7!__XoAa-PH-96fwY4i-~wbmxB#4sTn5esXCcjCGwKm6)=nCpBOaWBTnbJBXP{<LUj>@r)kp_;HMkgA04@fvMCO85f>$83z$?JZks06&)FasAHpSWE|LK$T&m$-%NBThh>y`5M7kg#I7;AAe^tcnn`)Dk-IAx!agY;GT2bnMXUH'

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
