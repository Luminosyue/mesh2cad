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

PART_NAME = 'part_013'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ca1867c11bb48a39eb2aca203beb70b/part_013.stl', 'relative_path': '8ca1867c11bb48a39eb2aca203beb70b/part_013.stl', 'source_sha256': 'a304a26db0b7593377551e244b8506068ff84e97dd187054671c744ca762a0d8', 'input_faces': 195, 'input_vertices': 181, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.04493622109293938, 0.15199849009513855, -0.04197925329208374], [0.044939812272787094, 0.270162969827652, 0.09211897850036621]]}
GEOMETRY_BASE85 = 'c$}q~dr(wW9LF!HnWp7~@&&Xdi6)tp4?vQIKueOyGR1r>BKRnUc=-TqDFijN#8(RBwLml<2$)vR$Xe5sW+gLCmd@DfOj9~q&1g;kICXw!zh~L|yQi6^cIG#q4_|(qbNAl6ch9|~r*`QYV)$P78Q(RAu3gdBFsOPNAx3d_e&OP*?1E9t@>T{JePm8A#m#Bcr>18F8O26P<bv#ito+D0M`V0XOk|WJGAB2`Fh6tIyxjZ+*_2Ppe5oK?<OPc|^RmUy!=q!Oqa2Tph;o!U{^P5s*aX+5pr&>~PjlfX34-qS^4Homxg+%I7NR#V#iZOAQu&$e|NPiKZT|G}_XBg!`Ey_E`u#cj%`dmqQ|`_#`;>n6)UVmruF0KC&zXV!o}-t~==xR8`<>wpU&(pzJ6Y4N$(?hr)?3D3c3p0#;koH<*W{iHyEX^*JN|m)tQ>#kv|_pcMtolvxPOd(gO6(S(5=S;bG3hXzduL6yCSU4avTqJ+ug3oy-)4jBiTH3hxRzKT#c`C+i_&Me|wTIZj$>mcit(vUt(WrlKq2z-zf8Y%T5R8o(VUq0{fkn2juwX&JQc(`}ijObYSkPOqaRy=2dyTj5CSzb-Ab8$K`>!w|UB0UBAkCzbj(C?>MH-$kXNxQ%mLhs=ib%_rr{|F9P3}<J8sVa(@ooZ{7ZNX0bd^Dt?pWxJF)R(&fg-vzm3eGvvr&U2ZzIx9D<j)T&nPIA_b-wBt0cm7hmf{NN&azE^$k+n$!DW?k;7+i+NyyBf?^U2ZO#)n>{6?B1arAGvLO<Z2vuXi=feuYB#>o{vT!*5&TXTdkISTi=ere(#NU3gq#<@rmWQ@cf_p)&A$Xn%CBk{j73tby$aPUX}BCRnF&CIiJ_xk9p0u^EvXkhrMfgzdTp-@?6c!b2YE6pUvyan%JS6SLJ+OmGgO3&gb>_tNmPk%O&$Zrf)m<Z8@mR{ri*mU&}fYn0s>*J9OiyoR8!0$2ex(oS8B&sh8tBems9bmwT3`9n$6QiE%C3{@|P1+}*RgWnNd;<PP1uD(Ca6oX_j;KXKAG{)w;?6OGRA9V2aZW4k7IUhB6%u-}NgXt_?R+&Q_{a$QxqIc&T2yk)ubj|~TOxjDP`kS_P1Z!9-H>))cCcgc`eUG6^*`S>;7HcOr{r9->@$Zgw?+_wG5ZQGCBw*6}SaX%l?j*riaGk)~U1kL%$b9J8ZT%9Mjew?4Sew?2w=jSKS`Mmu6wDsfs^z{D8m0;Mf13XusUt2#uzbfa~0iN@5_;tWB;c|{7yAJbQ9bcZS@p-P!Lt8(Nugdv#nCE<6ejVmHpO;^UJs<2TkU9IF<++-d=l=c4ay755pUum^XL-)&<=?YB=kxOKS*LeJq5PSxPk64z@#k!P;xNLCWX{%OJXh-_o~!j3&(%80pR@HC&u!zg^_XL7gYUkFt#5g**0(%Y>sy}t&o`E<^{s6jtZ!}O_}2r!ESKBC*5~H+3-UgIujk#R$15b+{fN2h*NyULeqS^8hfOkP_d&+)h#ivb{)^}8eoE#1{)^|T-%}J`C&}&yd9LmU9U0%&S>{#un><(dr^s#hr#wf$>q?5Ld%w0E&jD1<->)rK&lxg;n=J1a&oOu|pJSw3p4udz{qage55u79VT2etnE{V%D5RI7{*le%G5_w7P3+kJ`^aXv*oMbMMWV=~MU56UR#ZF~4Ua}oJUAI151$04!HF~A#KmypBKTDBc@+6Va1nfksC-f7;6nI9^pt~(;lu(saV4DiD!d&2I#><g25v%;ZwIU4+u^lf9lS==8=@+~&G1Ti6<7<e#otze^>E@Acolpt_$HjV75)mi4%`YSz71ao--ROI2)+d;Zh&uuSAeg<iL2nmLO5{=yaN6riu_4%CY<;*ocIKsI1&CNJOO+JPJ9ra03V4Wj{_fuCxfxz!*JplIB^s_79InRfD?zqiIH&PL+}{*c<@m;F$(Sk$AM9B;xPC)_yZ{N3E*frF&;hvo&rvStIt>pI2}&Rfv3Q;QRHs$WjJvKoLCMgz7BW8*BhOmrS;%W_<Hyb6!{vk22QMmuYs3{O2@vN3(kSh!SCmy$X`N{7m0F-nkT9hTnb-`-<N_V@Dj{hiXtxqtKh`7@G|&nqw_Pl8e9%1=D~>z;H%+TDDua_=itPr;KXD&F&6$fJPC|}6UW1o;E6`(xtIt}ffJvBKZE_12)f{j@Jz52o(W%uA}<EZ;AMEv#VGPz6#0BG3!a7dHXlX)EQ&l8OoAt2`%+Ql)4)vly`sVl`pWhd`Tbxxoalh}H+-)QFbGZzffHxJiSNOQN8rRZcm{l*sIH>Ai5dX*g%5xa1pC477IlxPU{PJbyTE(k#6IvlMD;dkQR3sBaAGewu_ydCQQbw|4)%ceKo5D7sJ)_EM74qk!M*T<@I#`SMI9E^2=0eB!uO!a4~S|I^{%LQP~;}K8*aj10B6HrfJcBs;Sumqa4<X+J_H;DPfraB4(akw|CZ}~x#>i({F9FVrFCf-_?Jh;SpJ1#dTKY?_u@bX%Zu(-+6v=u$aQ=8'

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
