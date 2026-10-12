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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/a95c590e89444458b53a15190c7560c3/part_003.stl', 'relative_path': 'a95c590e89444458b53a15190c7560c3/part_003.stl', 'source_sha256': 'b573926111e105ff4b56b14f4ba5ce00476d91605f41d56beb884a4f12fea5a2', 'input_faces': 120, 'input_vertices': 86, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.22298777103424072, -0.1736467480659485, -0.03188088536262512], [-0.028727471828460693, 0.49999964237213135, 0.05030179023742676]]}
GEOMETRY_BASE85 = 'c$}q|2~d<}7{@;@1v~-;Btcw3cR`jF0TEDSB?RSi0r4msL0QKW5gaEE?DH5U4+K#GQ&90h%Dl@n7Zk-j$MB*Q(bCc+9CPv*wSAxGPcBW(H1#ph{D1F%-hJNZJ-!27jD@9x#8)>dt0^ok&svg1w3QsBnflBb6UXVZH0c?$%p^PV#nr3@@yT(zQD)LiX^tvQpEWL16{1k}A0MPrD^%mBWzNV<O&>EYGfgl2$kZuWdZV8;AvHs9Y<mU;suliTYDKo<zh1VYhMP;z9XE<W>vvM9H0l28FrlX-$d`uRXTP@d3i6u<kgq*={sj3;4eNz3rz}28?c3X`Nk<OJA>V%<`Eo)%_b<xXM0pOkA>S~<g8Ro`EF#|_{~Kz*Na1m}R&J&|i>{xcJnchHnbs-qyiC4fnWDNy{=((#7hkD1ty3zjrM4Wl`b+Y++$kiTpUeG5zy69e+P{RfB8UCqXAh7ru*oBJxkUBJA7>w;_MXIz)P8iD>rQRt{%yxBB>#LJ&wt-z9@p9>oBZg@?1ygup6YYIT1c9{l6+Zdaf{bw$Qqh&n1=f+@79sO?$)Q|uj<0SI_qGIapzvEB7IzU$h3a>X%+k4^_;(|JFn-|Pso?n@3}$#(W(;Cz~3vW|LzA||H*j^c>WFSzkX9s{d$&g{b|?8H&krCPVEu<H<HGckuUYX!u?Zh(@59mv%ljB*WWl{73IxM=KO7+ah(;GybkJP2I}|W?C;3e$-KXlzdg?T^@#IV1QnCMJjlLme~sFGEXqg=MzZhv6X$=HvX=CtWcCZHIFIMF4ALSE`Et7uUjOU2OL=|Peognqj!Rt6<-1(ZTsQKihF6^5H*x}>t69gWe?lCubEyxX+xvr$QvOkSoL}S4>sFm{gzqa2pOc!T4W#d@$(KtXUZHl9<yO+v-wu<%xSr>G(~;-9WDWU-4P`uT_E;X*vIm_H*}9R(Z8L($T{?#L!{9TH^EY(Z#^c10uRWl=O6?AbJZ_$feEDh>*BO+;bv}4T_my^85TA!5(Ol1#>Ez3?W<2f(g<MZV9QzrmH>v%@39hH8md>9%{SxQT2<3fgyvV+NU+!Ofg`Pi>wvO&Y?bC%k?)q^&uKy^$Kd;T<`kNMW{UcxOr}+k?@jl+$&g1^NZXe~Tn!>)XhfErk!@gX}{&Q!}U+G7_;YU}V*Ze{B9FvCGk}q{D<o*th`J}<m_fr3pcD&9v^xOG-rI4@HHgNq-VY5kN6S)80YOa6g1+Kr_`8|~XjDp9N_bw)#Q$oIWcroXB*=Y-DaRK{p%y?Ywak{@G@5!8JMQB}%a~1q(H}%(aWWVMizb{5tkZ+jkR7>rjm+`v!29Ph+6!N%Q$6V5MbIubzi_fQe<s#Dd5xdAAX36#3wJRrG;7q>UF_ZJu`|$c4?)n9dtBYd)&H%pOPwm=CdGep|`jkcRxxFy@bLyY_l<UlO!SlBKGxDSF@VMm#%SoqHS5W<DA99|t83m-~<9Co>-kS5Y8_wr8ePucMfli#~aVgjTdI9-zO*ZH8tlUBByktAo*(!<s3_U+@BkyjdJn^SE&o9cAq?1;$U)!4fZNdEBj5xcA@_1ujh7`{4JA-|jF6_U2#dRK?w1MWUzsLT(%Hl9xi?5l?n&@7NR+1#b#`rZeKGoz?MwsGi*1!LhnHcb|K4p6Q`Toyu8Cw@)4V{eP0PP5N0NWr0TSMOgTZ3Cc+k;zyEun3}mSA(JE!Z3^LEA`gFTrNec3`0vV4+rEGjQ`|Ws={@qy{UKI;~9RVuiU1Z4G`;oB?CRL8HNO;9&^CiN??v!`m2vP+xE$I2a)~03o;+LU2!nU?tQWtOTo|8n6niKnU)Q5F7*z1P6f!LW98r!BGgoVbB0@7&sImxDT`!xDVI|A=nGr6YK@<fe`EtRf4-fJ)lak5_9%I2zG@kz^-67Xm79^xEn&SKQsvJ4-SD21c!jbp;2I=gTdk82!!BRV<ba$(7|9GcqlXq9EG(WiV!>m8VXK=#zRBF@!&{kA8;hNAJhlj53EKA_Jn$YJ;7a}J-}VT?;->{LEXX4d+CG_+`$-jP<v<>uszrj>H+q^zB(cVJ44;TZrE36gy7By!QByp{h<C}KX6}Y2)HkJ05lvNjy)cL5ZoUjcn~xeJP4d1y*(2N2*EMXM6fQ#%-q4^pZ-;Td&%PA*Ww@Nzy7l2YsvJN7mT_7d`anItmxHbZv2}rHd;K{r9S|;HthZ'

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
