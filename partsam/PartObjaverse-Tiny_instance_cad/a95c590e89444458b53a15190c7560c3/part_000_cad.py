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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/a95c590e89444458b53a15190c7560c3/part_000.stl', 'relative_path': 'a95c590e89444458b53a15190c7560c3/part_000.stl', 'source_sha256': '20003e44226cadf1e101fc20fb8d6546294b6b665e0d05be765c3c301288703e', 'input_faces': 300, 'input_vertices': 154, 'input_watertight': True, 'input_winding_consistent': True, 'input_bounds': [[0.06921505928039551, -0.45533356070518494, -0.06653031706809998], [0.13715922832489014, -0.1592094898223877, 0.03545725345611572]]}
GEOMETRY_BASE85 = 'c$}q~2~btn9fvQV5iKeTE+nWJQNRT^Tx$aE77>wXMR9>BD9U2kG#K&8;)(=CKr#*?iFVA=EM1Io3D{WE(R4E1QYT5Lsgq9Ana;FMJDtXMGQH=X@4R>Jxv!m0^Jf0@eedVtzH`sH_uO;Gtd(JXqAmFuYyIi^%UAv~$g)I5SkYE>L3w4-wt|Y}(mhXySdmUHK8mfG>sDoL2(hZI{R!I(Dz=p;%#TZ0P&hYXa$G`TS$So7e(Bb-^6dp8UzT57QDEm4JM;Gx*xwVU&q|pbH#2E++=00N^D{v7A^P%Lse(m+{Yj7DKT0q31k3A|o^g0@{P#re+qmhr^Zj>;7lP)m|IF1sZPl^&gSGePs{OM3?>oO+{L&rgdq(d0p!vte?RxGjTzo57dw;Ilr=<SC`Q10}%j1NUyc9G)cdNr;<$xc$#^IyZ*MsJ1*S5-kpDOctxgR;-n^&Ak)$_19GGB4vpq{6-cKyo9KQC){<(q3{e*Qtdlh4kS`RNNEIC<+R*?%)XfB&qW`{(8U-R}m?eNDSv$5HcQwD;#``(bH64%#1;tNxS^z2ut5uAWze=673a_1r&?Mtgs*+Bc*-dH0F0e(8Mw>ODE0<e$~ulX>^r<4*oX^(EK5w>7@p6D<E?;t_{0zUJg{*TR3}e78<!>G@|}fBw|@9<jAv&#l3~m-8O`ZcD0`_ujuF^L-0_^86#-c8*iLPv)0$yYxKn!x)+OcIEeIx%K{4d7XT`pj&UBmb6*s*1y6XPFVD|>pEGu|6<Vm(+y3oT+O4|UgfHN#yc{<9xZ>j^tkLldGFOba{PVIR>^U=D%+pS_^Fde9eJTASe`NLoSyq;KX)@&dw;Il5BR&2cX!0f`I^?dH&x4fr+gykEAL{9-rn+kDaSdpw?l8AHvF>8t=eoSPrq^5-A~pZGgs>md7z)}_WoS84<C3%<atx$W&ii297@&l-h2O){m-ed(%W0@zmR!TcB`KEjtKd+^Sx%*bNX?tKfWQ)EA2{-t9@g=%&SJeptsMvG)U%&@%voue|t;Ldu76ldV61Fw#>6~%3S^QjgtAso87MV&F{(Uq-F0mJ@?;_-}&U#o?!Wdwa*95FW%nIdCTM9ZItt}z5RJT_s^Gl4w|`o4ys(;FQ*Q_5;X6g+@R<F^-VoT%v?Q3R6kjteHYu_43=BI&Z1QPI6RMhW5eI-36fhmf2+{jtM%MGeqfz<AK$;;8vXa@M*scmgE>AbH^#?*{Tt)&&yDf79^~D0&EqRk*Mi=UX0Glpa?kx}=BoXhW1ZZyo{)Ri6LQabLhe~linqwzTtCS@>*x7_*9AS#3v$o%g52}GAon~kvSY5h#!aoaX0Fy-a?ko~=Bj;hiR`EOJSF!$Psu&cQ*zJq^n=saUH7AUewn#?eyQAi-kG^-|MPB{oBIbdSNn&i51rhzKOy(*PwIa3t~@_uzhvfW|3mKCFPXV&|M?%}am@Xy%FX>Mxo5wsa&y1hd$`9n&T4;X=4yXP?%A)Jx!QlK<CyzZGdJ6t`&Bbn{i(g}<evS%nX7fL;cky>-qrhsnXC7UyYKY6=25LbX0FyBa?ksYnXC54*57cAn|l8;bM^j3?s;D`bJf1A`G#v8)VgivV%^Siy)EAk@3*7HeiIhe-+o&z%-3F(TX;oo`LD0aMJfN&tMbfg)4uMj@;JK>kJ<GoB|L=^zJL<`Bqe;0T}$j*WLFYQz?1MHa4<dukA#EpNIVfvz!UMsa3Q`J-$e=EY1ej`3K!z3_-r@<pN+@EL3lhq9uCIG<8xpFJ_k>Oi|{nOfD&E=m*7SCZo78CWpD|;44(><@TvG1I0PSqkA{)>XgnDv;>q|@xENoG7s6e5AzniXuY)`BI^3ttjgJyuZpmv%@JYDc3S48t7r<02a2*OyfwQf^wJQ8k7;goxXW`@Eczhf_3(mo3;g7>K{Be96EWo$nPf@}vU=dz{AA-B_LwLOvnEQH4_<p;Z;Xb$n--j=U%WzREv^Fa^Ml=2_CH!eh__rwGV=3X^po9;ggvY_<_;UIX2dCn3_y9OYJI)x6EjU{Ht<n6xV6xVqWcnz$RO|Cn&O@+JJFh~{Rj@`o_Zn?XY8Y3+I($D~4}IFa_?S1ra%~=kS6G2-TFtxgr{H5&;5remt{>s*8WTPXj>9+Fm2cN3xEbGsf0GhElM+4y&c|oqlkHj$H^BM$20RyT#&hvJN_Z(HybR{!W%ypW5#NjF*p+2hwq1`<!iT}N_%M7R{5C!i9|3dl5%?&$5g&z5ft&D6jNKGUcnqA0$KWI3415M-H<A(_tBr3gT!+Wv!{HP7a6H1U)pm((#2OfZN6=;sCHycYya}$uoA9G>J$@9gg&Xi%yc*`>xy*MpCHy!n#gF4BU>RP<e4n6%AA~u04)b@A5`GM>#gE}9VK#meKLWGxBlrQks$eF}!ZYzn@DY3x9%a|Vc1^VFAvhF&2=51@@F@Pa9~_4F!^7Y}JPZ$kBk&NsFC2yU#rwl4xL^$4kK?L-3J--LcqneczE<EPybtV;_rb$q3@$hl7mURPhvVUR9~hw>GlJg~R9j~Y52gR1%tI*o!*I1WKZ2{^YJ3%5NeO=juE7Nl<ImtNl<+gK2|t6Mg-7wTcss1c+ws$|8W%i{pT=9^30&|XE_e)Y#XI0hyaVrqNAOO(4IaST@KaXcJ~;&&@m7wj`q{xbb#PpDj-8A_C&yJ|(#DvzaXdAKrx@c?{8kHW(8j+(o0kUWa3b@%k`lfJR^nUmV%UHe<0Y^WFTuCMDts%R0W<Lod>)*H&%>v~D116T4GzVp;d9|cd?M#ImlB>1x8PeipLAG)m(cHYn1N@|zjQbqpH4s0`K@%mXRQngjSl-y|MeUA_?$&V|BqnvFWs-f`d=p7FHioL;;fZ@#l3Fd<e|>y=u5G>S^ow;=9qH'

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
