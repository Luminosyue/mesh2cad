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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/844fc9a82f46421c9f10804bd8055212/part_009.stl', 'relative_path': '844fc9a82f46421c9f10804bd8055212/part_009.stl', 'source_sha256': '7c2a009ef55641e6c3164d8dae031b9e44b712be09ded3163bb89ed8ab2cdf1a', 'input_faces': 230, 'input_vertices': 138, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15697211027145386, -0.11491450667381287, -0.056722596287727356], [-0.15543723106384277, -0.10086435824632645, -0.04267245903611183]]}
GEOMETRY_BASE85 = 'c$}q~Yiw0j8isdUD3=z>rBV<IyWD!ATzavT0%e0%(JG!&N?R&rx8)Qn(3Vpu)N0v<A`oRp$BCKwF_R<FwzSn4qedu~laaYN{?OsaWXxzh8qs)((ZnlG9QWnf$GsMNlF7_TR^Dg5-`CZ3zHhJ9bJ9S0!kARWd1Wa1XDT<hPf`?XBrB;(XE1c2r7764thK!>PMKo+*2~o=HdWmdsEt!PmF~=)!H%X-W{H})rnxvXSIum03mphGwC-pN?F?G}?G1Z7f~McGyP-X3&a?6gigVS1>|FIB^?!U#G`C=!O}ld0RBhYuMlChc9vQmq@%7&Qwy*uZTkw^?-DUgH-fF=Qzq7>252XsewmQxB)oFh|YiZ=O6x)w{bo7F~p57+-#*>F_Uw`x8zJ7G(2ZO>oldCUy_bL0v{3an^>003Uuf0Fy>wojZfY(=lb<L^I^XjmluT8lm<h%7$x=X}-e6{RpA>Vkp+IM{&|AzIcr@VjF^`-qsSABTiw?6oCebg7OIKEVW*H>nV^;a6s+rH}d@miwuJWM?&_7`8v9dYXX>f9k;|6i8}y}tXLsLx&+^7D<=i^P1T?1E5#$&b|^KbrKlUAM?TPYnC{+6P;O{8)eA=oj*1{rz&KkZ%l@`L3_y%j-w)`0l*#{_*AgyY<(k`b2fd4@>pY=REHCQvGATRR3sEpU_`Tx&EsCzFzuK=&$SR1D`qPblk=vKVN<2$w9BL^p84yESfs(=c_MV9T3(jYjyI!9Uk`e|B^4{8yk|H{al|k;^#;H_-4P?cl#TjkuT)C{WZ>x2>EJa-l*UDitEekC%oa*S=zsfFYiBmrq{`r>SN$*QhlPyo1EuoyjcGTz9!XQd!kh6uM+&+S%1Qwi{Adae)MXk?d$x#kbPsYa?tBXs;Aq2c(h``>$~SYeEMX+;Qw{0)5q3$!H=D<oVT74@_SO8eo6Vt$zRy-D<Z8Q`6Ao#rTs(>etgdUz0&&%<A<g9rLMbr&RaL*;ZK~py;~^M&Gpr_s_knF_YV2_`jtb2UO&?Fk@I|hb?303ufG240k0n|KJA>x-XFz$*IyUy_xjp}+0HtP503cx#vfY6eD~hl@LM6@?TgY=CgkgnW;pkoygt6XekA4j^M3me<EzsCBd=B2epISY7+;g>qbH@?zAn{Y!#AY*t1aWjb5VcI|6Jflep%=1-*8?eKXzX5)!N&f=j2buke?s<e!GzGo-cjO>0v)VcJA=CP@?Te8x9Zq`D%T$n9n&?>gq=P{Mh+*>(lnM^ZY!vUdY$+wVE?Re(bzgyglOUyXV?{Ur%K@pAYLV3i)AttuaGf-@UglO?=kR*I)lsSjT;ywe;_v@$+N%556*xI_kHdXg|KRAD#Q^hW9JqW3K<!Z=CyIs;7!C*Hh)*Q>A|0a38w+`FoLb?i!`%0bi4zhbZ@_AwO^Oz3T3#?wfOd&$EKBT$i3_`5t!rE8oNJeqMP`xQAoE*Lyz)gl}t~UVQN%8<P~p8WYTKYt0RwuWFWQy<GMGs@78YUwu`}FIe&aepQ>yw&Tn(%^XwA5s${fsl*b{cz6b}F=zsuYmOXq%tU9vmY-&hCGbq<*?2dhX>ca7>F7=HB4Sg~>9FOem}3Dvm3ao<Bs2w{M=S}Q1g8_5fF{ASiH$=iz?MJO9JAnYo_V4<ZidG)pMy6ZO@!wXn~08wRbt8LMA-7J{>_JzJ#(vn3*pJk7voJsr@&dnQqgH}4zU?%DqKqcG&sjIxB9mZ&Skz9FB@F~uO^m>X2Yw9EkZNlmBbdHi{M*`WuOb-0%G&f3^<QiIyw(tPHZ-s4lgA(3!M!wrGLxdS)RGozZLM!%=7W)qI2LvVk$ZpE+RG`RpDY{3(@&-39-fKLU;|aEOaqkN-PJ>f_Kor2DsESxB92U8uNO*wdgvyp8nkjuVuasZxy;4t|7J(T?N<Bzpd~}=3DRz&|Bcm#PZMrI6!PUng<8y-zIoD^Lz1@p-bTkVk^*Pa3!&PbOl^RtPstItLR@fT*$l@uNW<Y>xh-0#c&<{+YXm7-+@<(u7OXQqmLf;k!SI7VmjIYAE$r4u<n^#{d)+m_sp&Sb;0*B@5HM?x51tCuLG`O-iEgY-3sp^wi(?5?;;jJH^aN=UlSbg%&q=4!<(4jk5_@-3%3%hL@VGBu`09@K1i$@t%45|t3|8f2Z`08wXi{KJ6Z=D^sW!y&isTqPSLAV^zt~q)u&_dapt}B=@`S}BWM?V1nxG+A+!_ig7*{aKs(`m#M;mfxQ#yTV_4i`jv%@V-2(^dQzN{Kc@uqVWLUfty&v8Q??zkU-SA#C1n-60(SvY1d;mQRAAlb~AA}!(dr$-JfsfLohw0NvxDP!FA0^-7d(2VJ&y|yB@!iBupr_!wh#f;uz;_Zmf*yl666;2fz;_Tkgu2hd?Zoz@hu|_|`_TRHZNys8eekWsf~fl}tS8op2H_3FtlkF7<Kj~j{?orqetsF&hg#tuDDqE=AK$${`JA~{?8AJZe601k&HOMNZ@;lT>#x7^6L=cFd;'

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
