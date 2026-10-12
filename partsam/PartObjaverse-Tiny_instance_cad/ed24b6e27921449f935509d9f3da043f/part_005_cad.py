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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ed24b6e27921449f935509d9f3da043f/part_005.stl', 'relative_path': 'ed24b6e27921449f935509d9f3da043f/part_005.stl', 'source_sha256': '3fad8423a6f81656e69f74838b52983375ca60f9283a104aec742bb129f03bfd', 'input_faces': 100, 'input_vertices': 67, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.00015626149252057076, -0.4046591520309448, -0.06789467483758926], [0.08680371940135956, -0.16258779168128967, 0.0461973138153553]]}
GEOMETRY_BASE85 = 'c$}q|ZBSHI7{|{p3+T$rqNL=4UQArXby;3SP}GYUL!q_3Fq7j47I7)FRCdua)47%}Loy+tAf$Fv1}PC)O}|*vrPM?;1$C;iX2=;Ur^cL|v6}kOJ<t7{cemS2Q<r(>|2u!qea^YhIrrRIPg#T|k!e>dOWL}>^K2AjJYrZPTkG@JF0b+hTq{?vGcg<a{JN*jkCiX-EH<&VY`tTdFHq%o%n}@h)%gym;HX~Zuk}~1tXSn==Hq@z<qH9y>Ia^yT<ufa>3K7qLe5mDutE5*mzB?9!TQPbR2jZ?edr@q#UE-~xUzu@k8_`STvy0{;^*C5g~2D+b6?o_>LuP*8Vh!Cl@o4n;J$ppO?edm2k%mz%kn15bA01v-j*^ye2?<=mA%e=acJK~YG>DV(tS7Ak?$Scb(QW<TGdXv=aJ2nrzhn+<@sdcHtPTUqjlt;eD+IfKm1EG^&jz~=4Z_Ql={#2Nc8_3E!%0_L-OY|uJ7$OE#HrCa$gE~X<TVh<RQ}FiU#tpjivd^=lZFiILF$^Rrz=s)km;t^AP&)lJ6~5s6Nd6(oVX6US1Pv@okzvJHM}k#&?x9(>x<zqxnc;7u8L&uGvNXH{Jb$x4pkD*h>8dm$Z;S`x4DlwA-mJVnyw4@^6(>exZJ;OzW}m4*Bw#e#$?bxrgd2-)`GOI-qEETlziKU$}F6FXbz#I7jWn$^jaufl)psshH|1I}aYD=j@r=N#p)>gYrlfTWNjo`Et`On!jYL-J$P4+<leiqqOCQ`0SN>@>z7p5q%!v&bQk01`jlajN6b-zEacItM5O2xax|w-%4Bc{l)S`Z69v_x?S%pXK&KJmA6+0^?AhA?Sqv6;@yz^Y+N_3ue9zPIb=S^cYa3xeoIeC9w|WUBAy%S()*IDn0(p&bVta1P8U%9rC$rWL-H(~M)eneZwjfuc=+Nes@orLY5CV|={8!g;ZX%WM(ZxOrX2|x_o-6KBV9A~8tortiKEwOzp=RPUZefVvcBsz+|OI`f|Rd(3guC%_R@S<S5469z3}#(2^zg$ik}@ddLLPR`B9_yS6S{mYV^K)Gf$8&;+zpo-gju6p#jYgJ2!+W_G2_o`1x~v%Q5}B2=yx{k074Z`iGrkQp$kl4?d&$J5smPeDbc6AATMRi*4^y|FCn_>-Ui#ehy2U>a_k{UupZq-uedhFKHnEZ|8Y+#0lyjcK$1;^2rbRUU)*jf-fJ>YIH|3#$%-V6|An*eFC}3uX}3z30$80uReiUZukHE23n`9bC{||8q@*iIu4u$9s?Z-9s`bsjs-`9<DrwmTpt3*gCn7-;7D);g0ldf3+6fpEPzv>Gr%ceJA!kT8Z)7V&>7%Da1nG4nCpCS5jYnrf^)&y&{<%v)4|!`NzgQK8tOO+!8r~Z4UPkwq4D5&)XR*(mLiQ{_b<*Cr~npFBMXA_D5xDg3T#v30caA`4z{C?NeIpvx>{!-IOnU8pvHr0jE81|$Ag{Fd~iPQbs{*spoL%;I0sq;F2dU6AUIEiW`na)_leLr@I-J7)C@MGrZEV9nV=T11+_CFI7dNk;3%+FS6?f11lS5rgeHI!P_IM;=VYi8>_lCX5u7JLbHF)x&It(4vCtTB44xqt8U>C8kA_;oR?KNMG#Q+XF*r|AW11T2YUHU=fHn`e&P#{K+q2c+=dP#BWKN9ur=J}6FNqdK{{tla&d_68e`l2XlKpjPd&(l|*NR#Ft5LOvM)?z53WgB'

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
