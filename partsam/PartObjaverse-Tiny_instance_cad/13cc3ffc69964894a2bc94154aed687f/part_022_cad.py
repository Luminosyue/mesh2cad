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

PART_NAME = 'part_022'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/13cc3ffc69964894a2bc94154aed687f/part_022.stl', 'relative_path': '13cc3ffc69964894a2bc94154aed687f/part_022.stl', 'source_sha256': 'b27412b20ccf1db6ca0f002a20abef69534c4daa3dcee8f09a08f216641c4b2d', 'input_faces': 94, 'input_vertices': 112, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.20696142315864563, -0.0767688974738121, -0.27385079860687256], [-0.12510830163955688, 0.05635686218738556, 0.48309212923049927]]}
GEOMETRY_BASE85 = 'c$}q}dr(w$6vuynR+0ts5M2eXPejNEX!!tleSj%G$WlZ^mtaxQ<V`9$UUjrm9?I(El*Sd3Eelxil~!_BWKaPUXS7k<b+utgt#KwtsO6vT?|074-)(HBshv6V{hkkpbI<+l@BZdOe4IxgKLVd&WY6P=^T~^fRiZ!fBZa2i{ESpn-nb3fo7{*u<LrZKUbJ*!e4-mEBt;=<ro7bLkZD3lRQi;Va3Lf;D>pwkWy9*M+%yyAu_^2GObX9io04r(@-Y)9MuZEIq2a<7;Xi&nl@Sc5wp?zcvs9KJ(JLZm%4_u;7b_bWCnjf6BjcNZSNT*j9wn~SavktkXFkn^Qw6|3+YG#DOa<^9;1(C-qCQGubDYY8c`Tk)lsgj^RI~b%lYuw7KBwH+^!TcV%Mo8tE?-#O0X!1=H|iL7+77XLaxx6KtpVz7yBRlFdoQw|2gDp?^UN}4vvsic0M~T_UnOj0{jHCI2lxG$)fGrZdd43CAAXc^VZod#mRo-XKH>?~Z~47K%VR!a^CW&-{VZ;Xov<Bv7x2)XhuC^<{NPiXJL@`ukG;;gVDJ{%eb?OuKJMsY)+hOdh30bIb>N45B-ZCWC!1faYXx5M8*)RIhD$oOA7s7vHkupjnlJMEhfFY}@LW7n3HvHR+624_>Z`6npX4?Ra2s-W*bn&!53}#3?i=WHw1IJX^OOn=uRhPXGw~O;Zenc-@UJs1uuq<_?^mkb1N~1-t7bgsKpW4+le>Wz-fY*@pFPX^2+gS-(EmfIKU2=QWGiO<jkP<V{<II{Bs;nd_%=-+vN8IKhJUvL_Oq?vD$m7p_ZSzOcd+XkY74M_JJe?lX8oNtCa7;3ehjWV9eFC$w?6n1`t0fez8dOVA{dw64P*1jHOa_5p+4tun})aQzGCZOOTP*{5%{HJP@kXN&U13P0s0qqX}Eah7W8S(Wb;Th2~dCKJmaEmE3Cu*KWyy2bt4*Bo$I1Q&v7!yT+egE{zr@(hpb`svg?wDlYqtbJa?M!K>wi@R&R8*YPc}atDfhg`4aHKw;30^Wjnh+a|`qdyn}PLJ9sYm|6t|0Xl{Zzb&+u0ZkwIwa=_Mlo*T`lfe+c!0M|XQ;l_bs^*k5MHH<q0y^b?=eedA8(a&P#IWbqkoPoD-o(p!K8~kruc`lWgK%b!T$Kk%NIe6~$ec#G+v3w`=2?{<AbGF!dF8F<9<+)J4j&UhyHuk^a;JN6VW#u_3PlZ0gN!b6gUBi8otUMR@&4oFG;&6R#I(RPnuCwyoxGx&kKX?bs)7@_8x#SaR<vH0mN;ALg`q9C2b$*r0dwpSjgbJwd?y&P*@CmT;+_=|6v;L&_j)Ujw`m3Dm?UY%)V1fJXzG3G%@$s^1`A@QT|J-x%{OSGyE|#^({Qfuec51k~|5a`%J0olF_m-XKPwyAFP*yMV&#BYZ<>0ycoT{9ZRluBh4hX&XHC#OhRPHQ20R8ctG4wvraP^!~xm;?7>*6_}a;daT=J$!S+hOOqx=&OtlxE2Mz9l_(wH)`Y%B7OIGXESoyE`>peU4Nvl!VIsb1n3AX}J1at6VPjhxzfG5qj=xxO&d0Tq^Dd9M3V*^FYJZb4=x8v4>{egr0|XeZ1!FxjxWz?&m&)(CDYUJ*TH|ug(<GkE+jpb<UXduU?&}PWqp3&VuI)gbqoFCo0XKS7L$^;Yy6hpgt6X`q8MP(2qtx40SmAVd#UD7^lQ5N{mGfLr--Kda5Dl$D$vJIs*Mj^a2L;!Ad-*1YOp?O1LTEu7n4Ag85J-hA0t;LA?%xdOuVj^nU2QQN7T6qkmb6!AcBLA^>$DdaC~DsrsT1KtBNWCG-Q(_s5`~{)P395*w7rLcb1ks_QwQfjQMo&ac6o>RQg5FsGW%`BcoQrg44+=4t4YP~SqIgnlV%Jo=^R-#}e}p6Wu*zm7T8d7Phv`8@P7s0Q>g=x3rvp`VF98g&|as?*U=$NV)VQj{<%@izL^m{VPaeih~`QIpZHM86z05&d%X%TN>0FGIfs^-c6k&@Vz=jD8XN`KWQ|=cA8Bor^ve{Vdek=x3pyfvQJObqe~a==JDd#hmJ7&QHR8GWtl=2=r7ZqK}VrbNBQ3r++a#{fO*g<^SRE_uteWul#S$P<s7!*v7~8rRRb2(7Tfy`i0Ubmi!5<wNZH'

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
