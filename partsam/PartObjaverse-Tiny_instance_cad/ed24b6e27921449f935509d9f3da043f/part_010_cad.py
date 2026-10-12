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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ed24b6e27921449f935509d9f3da043f/part_010.stl', 'relative_path': 'ed24b6e27921449f935509d9f3da043f/part_010.stl', 'source_sha256': '8dbb64b77bae3c4527bab984c69150552b4ed03dbd5280495bcf41949f0bb277', 'input_faces': 98, 'input_vertices': 63, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0954926609992981, -0.4046591520309448, -0.06789467483758926], [-0.008845215663313866, -0.16258779168128967, 0.0461973138153553]]}
GEOMETRY_BASE85 = 'c$}q|drVtZ9LG<gg$)7gRuSc~J5bA`LZRKpqhr_M7PQ+^BmAK;p&b-PGy~dY2A!mC3ucdujcv$Fc4dT30R?r$M9r>`DNM{BZtA8>>dcJB1r{}!#U*;ruiv@b=9(D2%`e~2`S#r3J?D4NJ-2l^qxB{hIu^5fDbcwhhA|%T%)~Z(eVZC;y#Bn6O)WZRB%dEQb^p4mwXVl?Y%_b#T<i7M_{=4O*-=+ywg~3BM&Bl%XJd7vuhz@`)t;yQUd8us@HBaqcGgmxMX+UCgy)6-dc^TDEb+Z_T#?|+<+EJHpPM^LE6T`cuDo;9e)N|vuJXj>1XrPT%V}!wE8a_bxu1OLb1UVMeeb=>H8Axs`RrKh7u3#w|269Ol!<)tZ2u|J!W~284<(ZCK6CIqotNC$L+!EOj#1va^l8fT(V7=YJ1fa&@77<S?^pf4pZqiHLVix^r_^5Q3ea^{8ps!irLRc6hq@`hQ+k{F`Q4%GTIUT@`^KJ-|4kB&UphIpX9Yj+`(pCt4{NDDg7J|Z+z%8m^4%3O)rUnrbAbD-^4eRJr~Dd?pH24<()E*v$!CVGG@gKXl<FqFB82+CF!wd(yZ%rcUAOhho8*_Crg4fXDcdRkv^(U_R8f9m_j-x@L1!uX(kD}tKbYUQjq*6A$7%d0icivck5wEcovR{W`b-YhbN!EWUxfO2^2OEF)L$5t57W4Fw~SH0<Z`OBWI1w#=XbY{(|r!iUZFgJ>NaZM^rem&niu=BWv{w_aO6CVQ|`8h`Rv)<<g?hpH`IBAUw@!FxUat45q917Eb`^%560B}gQGR)LhG>NC3SzX$`o3k+b{K~eR=XHTF=rh&$v2|=pUi`8)*4X3cGGzIn`gXRt|>cL7nA`j*+lDYjUY>;vXGhbrVNVeN6Mc(M$Iw*ytbBs<Uvh>af;*5iT4b(7KPowyTondN7VkTI)ydc<_+cdUH=d(XX{W-Luv{&GoEH?bTZU(#~&tG@qA0XS=nYFR`b$OY3=*GN0^HKfi&s26}#(eY{iac@M7YJ4oM0><_`YogqJBKMA(Sk+Rp*!uB6FG0;KdkJzsQ1G~tN+~4G!iG9>Baz8xbp?x%R{}eq9?KJ<0{nqWC+(vmK_vfaxtu$Wse(nl;OC69el_ndMkt#7?c}vxKRIey*(lnsjuc!w5zj{R#7ya*7RK7BXEG3pfmw=anbD?H%E;ti<ADC-0I1{`OIv>0c91Fb*%=LC~EI0~k07rotG@9KyIP0N{!A2!+Qz8|?IUTA8>(M_Q!MOxl3N8VcL5sm<U<WiGoR8W$5S*>hT(A|K0nG$wqDC1A&WX@ia4c$(h~OL#W#D+Q4yp(1F@GI`a}3l7jsf%EF7u#CP$M`Ad^a=|oDI!`rh@apHfTCH9rd*#I4_5mftP~|p$@PEbu2`17N8m64Ae+~#)AcL0#paqVg3mS&I_P%;00ilszxU09bgkU1$qyd>jU5va1L}SI0tNpW`na)M>~RZ5!42@p<YD@&IQmya3SVjfZ)6cngC9~JQpE2r$J3%6XuWx%>k!@El@kyjxkxF1>gc)gY&&g+^@u)O1PZ5C{y%5{q(<e1Za_~{|H2$8NMB>&m2;6{k=K6oCf;W5T$&Y6}`@%3icO!;gJ^'

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
