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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/474fd643f4204ee59ff73fe9b1916239/part_002.stl', 'relative_path': '474fd643f4204ee59ff73fe9b1916239/part_002.stl', 'source_sha256': 'ea0c30d3951bc9e419551bf7cdd35f7859e7162ae631905b65f34c95e23dc7c0', 'input_faces': 82, 'input_vertices': 90, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07178569585084915, -0.12102013826370239, -0.4594481885433197], [0.11253232508897781, 0.2159566581249237, 0.25120609998703003]]}
GEOMETRY_BASE85 = 'c$}q|c}!GS6vi)$8)C77pta%%RZs`2Xel5#Bkodlq++o(1yn@h0v&W*iPPFfw6#XT25|w2wrVADty&ewC5RLab%Tf`)Hbn={iCK;x|#Hz@1A+`UZ+XZPV(jZ-fzy_x#zw+mxnFI$2Ul*SAS77aADa`orNIziy-01wlB?{n_UpSB!8us=nhUVw---Mn_`>gB^+XP#Juc+x%P+zQ$*tYxCpZ;Vt$@|sXc2+MxK3MHu3RUiwd$OFIbS3pDnK=<A<6}!v~p7g{J@d@{?0AeUy3hJk90!-c{tT+VHyb?YZ^-atmD-eo%||Z_j34o<Ux*KA=v=OB+xxqPkwy^NXd#E0P@bIvzY`J8|cYHa(viyc2x!7CmoB*hSox7<^5~9kVO&y_pI6dY5@G_=GC(imZ|&;FpJ@U+16w>U7-Dm&Wt=p)Y6Ex>_AK^!tqK`_;IiUyU33)wrQwjT`#axS?O?Ij?<KkDoIyVf;SDH&8e0!5+9*?&ria-;TI|>%#TB$*rloz9Qc0cyb5h^qR91yvySn)Nj~y8~oOy?f6_+CyZ}e`<xm-cV`LSuYCVJ=Ksn1yWlN(;NsW`)VJPU+k|W1ELGoh4!q)CR3muRiOukdr!T2~uVFsoQ@>59pT6uc`dSszqSnQkgSs`T2f&Zsb*cN>rg(DmA<Tb!PD^|Kw|TmG{U|k`JKb*R#xc&{U4QK%)<+b7e7ik&E#HgvwAP2HzS8@apw84|H$1d_3)VMm9k{VCXZ_V}77y!?`TMjo)IB`|ZoRM8&2?yTnWuSLGd?Wy)UUJdt#XTp`)DeP++*=@-$la6N{femA{I2N{b$%$&L90h1Akcf1$^?DBl!NBn~F!rZH0^USd0_@8@O@bI-3jBechLH0{5jk=?eI!)%ZS<v>D?&H#F3MhlgMt#l7ZtF|O^=0jy8#M#aDH>OdcN_8-IVXjv8JC02Y_f%;z$zK8G0|5ow*r$wkAI1cr$vyDg9{a&#R_4!*4V%`h<kAWM{NjHz%hI7Lj$LFM*8_t>5(C&(xV{l%H{-Jd`Za8N&el{8BjA(nT=Z14e<4=a{Qu|AtGaC0x!#QJJn4qsWoHMSlJjES@w_=_-1Jr$Ox#e*kG;UZ2jT`#XxS=nN8~W0?p)ZXa`qH?eFH>=o;>N#^Zr;?Y=3lAqm+)J29Q;va8Tw5h`8C$<mk{h%=Qri2QCAeJ&S&2p;8uG~HO8Oz;37Qjy84|2{jd@HX-?y1eEw#~lc=vQJ&w93qp|<3d2gOnzn{Y!)H;P<!TMEKDjxL*#<#8*hVe5i?WZu_m+|{CPFb7UpSdf+tuuOJe9_zs<BJCwr!h{AV+ZOk1~#Csr2iT4QvvGl(dF5gr|IGKv$(D<RqLD<Uu&`Ho|dk!u1QMwl|Oi?F7jz<epb6jC4%&FyXQxx+!6okQ7JCwe?Ka{Eaxy(YJgO%)EL^jEXvc_(>asR;yj)6>nzG|NZF*ONu{z+<($enO=<?$&16sIoXYQ0j+6?M8pNVJnBByAFz10R%KccB`?4taW)I`soAV1S%6(XrUu044#R|hMR-!zFMLB{!l5;ny9#Vnq-8lzxex5}+fc-hn<Xt%jaQ0*G#@UavKYJi&+FBi@I<a@=+=+7+7G*DXAI?<MfyeOW?9DDX3$FEM_u-r%6)%;@qCAQ{i8Hx{^C-?%7Ug92(VR!~xXCQaBiR!<kC&PxHIYSmGJ6VV@+q7ra~{W{JeK`6&XaiD3G8DzkL4Q5W~p$gC>G_HSd@cVltWmQgIJV%vM7hLC`Yp>4`VlT9wGIL)T`_<oXLlCwxxJ^2l@Qdzi`i9PP&1*f9Q;#)E{T<KN&4AwZqMp(t-Ax+z8&{9qAWnM~c4y6to)%'

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
