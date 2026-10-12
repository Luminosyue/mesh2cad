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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8512669067e448a9b1d3fb78bf0c61c6/part_002.stl', 'relative_path': '8512669067e448a9b1d3fb78bf0c61c6/part_002.stl', 'source_sha256': '1f1795bb7a80b01ea43d504818bfcf51b34dec2ede72ca44d3a103bd01cb23c3', 'input_faces': 112, 'input_vertices': 109, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.25056084990501404, 0.06811916828155518, -0.1066918894648552], [-0.16099333763122559, 0.15134461224079132, -0.033730555325746536]]}
GEOMETRY_BASE85 = 'c$}q}3s4o;8OIL_3Pw>0!ADG8QF#Ou3@Fi{Y!QjdLkOY>687>^zySqnLNwE@nn<fLadfP0oUjHAF(8T{f<j$U>jO27sf}YOTupD)YOA63m9|XJ{=Z{;$fPr!=Fa@)vcLQ7x95EOowGY6#PoOeWb_%w@_o<kZ63s!#bD;iR_7F#=4IuSOfFnm=ER1<Tc0Q2+v1bs5|%iz)ohJ#c1}rFvF{AUH$3-6-$2DTx2U+Z*jAWPRGgh-`DojUk{s?!mfKe5@MFIz!P5hk5dT2sP38amSfkK_-F|b-8q3KItr6DoWAmVOtPg4V6n;o*o8@)Sf_>Jp8oCeObexA*|61LIcv}s{7uOwuuf2jiYJDlZo;CYdmNza|QvS>+if{h#sO6Q)CAG*~5k~RTFC$)G+O{8Y7p9W$@WnXwU!)#Jd_fTTUE_~g-ppHY2>xSlc=cKf@@VzH#C4h1{fmg-aDei-HIe_|E_vrr<k9lx9>DoYH{s2yAHmyiUuneg?@v&?;}KoA#QS69xlwmfuAAC4Xus^Wg{dZd%-v?>w^zZdS_9&Zj1G)nW$(fpaS4dG_jsc|>cXE;{Il=D>y=%ozqu%r#yK+$UW+Kl{nB$6_leiu@}c|H8%^Wie!l_N-Q14(>VNX1__DpI8~Y;aBjgPmPWiX%n6Do7_ZG~n{muoP*O*Ur8*}{=oS)hWucr4>{Pvx=UwTO^#Ye3<4&QdE265}_;SEPJJgbPt__fn@@QTM#c(c3-<G1hKLwRa9!E1+H;5GXec$PY}33V>ZqdpYg_**^YFRZUd+~;rfiD&n6_agtTGP>@c-P@7>Oj9$}IhNv=UqZZcnl&K*zOgi($pMHrUUTfHJ|78h_Qt@gv({7pq`6c4)-rfD<?A|J*LMKrKVgtxcnk4H{5R(jfA%kjQMc5oG@dn&;MEK6n3wV3ZL0r2Z^9e9Q>e~P1*pHV*a5E%`zg)qK``p0&HoIZeVWmX>#l1@yy|rpUa7l9^9q?j@f%Olc<STmx;u{VL40)`<r(XbJjS>=yD_id*3vj5S`e>RwV;30ZSTR`?@Ty>_}9bH=k}HjH2%m8c;$5u>hrhOQvS%5^~mGViM}<vf+;>T1miT1JcoL!SA1x`_ca=S<07mtz4&1V^86u^_N(M~t8koniu}Nz(YokehxyuXHj?jg!G2|m`RcRl`^G2lK>rvWHSl`*3B+ra(~hE!Jr(eZ*EclIJN?lAEN&O&>Ait?{lkq%aNVU_;mwM0)IlrQM}2;J9p!%}t`T`+M^hgj3nsrh?-1%{k4K;ApA8_t_A0zSuoL%}jdYyD_xVbS-&jib%Qh3<Yzf5rRdYiyU-s1`cs(c)-pIaOiTOSbq&!>Os6VxK)YE=y0=yFIiv5SBM`B)D>C^CP)p&T*ahv>-+h>u#LP!6o|G0<i+F!Xw-c@a}yxlJW_2l~pJgdosXMVepN6&VJS4&f=->TcNF4!L*oxyl24cbqp4MrW5*Sg>h`!?$5_rJt_WJ52)>l?d8o<dqjg`45k;oi89`WA)O#ibH>wyYY@7iCp0#&0BLQ=ZNac(ceA_0gxLQT&`u^qjq(Ms;{2h2k9rv=6Krf&7YN9{Kyn>G@LNLVe}-@@e=l+YTa6wHNw<U7iJRo*O~Wi-Y%22Ypcxy!~-HywW-m^U}KfDNod!)X#^XLLTFWC%h7tNcZa_cgpk7jpDoF8mNB~u^x>dJHxZCU5GaV%V|Hk$|&CR1Ii!SPV4dW2fxPmvWMi0T4-ID-z9%_2Krp-nMcpZ?sj-{SvU2S=M1XP?Je*u++Xa6w7;pF^C(YO8T#BFlaKvDNwHD<4@beXJ+Abgv+GrgU*Ui^HvJsyPN_|z_|BcQj@Bm9dq{KhDfr1n)c-Yp$gg+Tl5f2VZya4s&#!Cm^o{pyrG0Oz4*z7IS3?6R|8*aVH%Fn*)w?#-hwU6o@md<Ki&Z^%Ua)uWoP=M0nY_P&Iv5Rh@@EQYy?pgMJg2lBUyu(tLVnUx)R`5&Pu?k(_Q~#@2ahH6dF#F4mT|yz;UnX?@weVwoAk<SNeo+jfA=eIUg-b!$~)zS@B7O83?IV_oEHTO$8wX!-%q?MTo@;sGg~lKxEM|%Cr&U=a<QEGf;h>|;Y11MOKv*nB|((rd^rJvmn8QCj<+B{IBQ&yRvQb#Bo`ybH&6U#xdmcA(Sms4rg3I*A_Oxf_cCX$AVPAla1sP_CAWl=EJ%>ttDJN}vg8(X77EfOw?K?9Ui@ac@tkKlqXiQs_cUj?V6^0(;tUWBmz*2NSuj9ygE_7OXUSQu?;&uN+;f~U0uRYe;P?o}NbY$~puk6R<HdX?ir*}k#aYJ57vxATkF!FMFS+HM0>KK&Wpi=`1(LIIG6lJkTgpilWJ+!kCrOYhxin6SAW3o=98HiSxhyfC9Pyjwg2ntp1T!RO-BUk7h~&m{CJFo`H-zIQm?Sx?2Sy6KBxm)2yI`c`oH#B5cgb0w{sI@tSv@mI&|h*^&kPd`l3YK|K*2D{4dsjw43wPJW1|EkBxm)QzhIQ)#&LoK{*s%*2^R!O&g#ifLAY=UF;4wF`~SCpdHm<2qX_apK)!uu-^Yf0<^!JV-w%<57#FL~eA4~cD*pYoRT=g#H9{uM'

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
