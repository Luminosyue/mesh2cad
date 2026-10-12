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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_007.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_007.stl', 'source_sha256': 'f3785d941104f8eb767a00e0c694dafb9a002c239eddd033aff01f41dcbc8b2c', 'input_faces': 106, 'input_vertices': 136, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.26545268297195435, -0.2670775055885315, -0.27297988533973694], [-0.07723468542098999, -0.08171597868204117, -0.21712826192378998]]}
GEOMETRY_BASE85 = 'c$}qJ3s4nR7(R$*iWwDIY35cYsrW#^%tx*UmYH_VG|UHk!;6vz3PR?CwybotEVQVp%v)(>_8Ltg(O6Up#0NG$O0%|d(sCMmIN3w1bI$*r+c|e^rm4&P^Zon%yZ`yle_p!;hQ&5bVD!6^)t_nov3(w6!dkHeRvaprnVTId?4CFM{umZ7dGS-YY{cl{fw3{Hn9WI?6e`RvNbGAR_Rr~)m}Dj9<QL2=2<Bzw7fcEXen@ayVTkjEQ-ae&{QBDDl-@~JO6MeNp7kGpErpbBXBw+HI`bc?6&OA-ez!n3`B%yNIWs<#*WlTR&n53Ibv}^T`c&iDc(;1z4vC`<N<RGj@~uYxtlgA9aA&=q-*tA8o|Prr^!$pq!H1FG&u)NzyH3Af@ius+hvn2$eC}eSzfSH4q%%L)=&!xFoZ6qi&d_g{EvI(x9boA9mzPog*IwHqQRxBifmiySS4t^f(q_A^U-2GzH|l=-<=PruPx#d(l;^35vi_EJwDD}b_u}y#q~kG)U;dk{r(5@FgRD=*1H_N$+MxH#sw|;#UR1VC&mYbE$nRFoA^j^l)#>*~^Gc6@AV~4z?~H!2gIUy0T%WDFPWRgY>6{y5>ilsi-CuA}*4b7%!87nmr+xA!<ZmhGgZ1flnJ;`Qope@wS#Q)cidXvGnEsT1*|(lP?uz%960gSHYMDxW*+&ifxQE+yq&y4bJY&9Hbp^Hi)wr#O&g6Ky|LX-cdVT!V^C;hp!!&Qy`g-Pjs_XDUX8!Oo!t`D>dflRVRX4WwW18<r7dGhiVcWORe0-zaXqO#dN$tN{Q={wm+RP*V-Dls|>!x@cyob8knS+S8k5|if&|f>R8}SeSxJllx+FkYgE_wa+sA|1mig&@Y6<8Owhb8a-RJ7U1vv2n<y>3cBn>Ix9_GcAUx_-qo@Dcr`9VPE%w%x4j_m1t|DX)(_w@KHjcn5q$r{bUJwo%vV{^3d9TeMH+x0TM6QsR%)nfIUmgvP0K@O!#W7Q2_)X})@+u9F2zs2}azDm}j&noaY%C}X3pU-AA-;+1~3FM-z0m?tWAJ$CtMYNyYdN@IMh2hx16Nv|;KdEz2!KdtONU5_3Av)niRN3$!9`3yb`KB8w;9__#Oo(+Z`|2A6xtzs&SJmCE};v;!td(yrz{wZ32ST9cLTXMf+OD5C0KZN=J^y`ujm%g~(Xt!>eJcq0^*K9D_1@E6GUbX8tE|$E#<B~nHJ#}7uN9VVHb)BKd&5WmWE@40NVtnsml4n^<4V~6=d*%7TGJb#8(7CyR&e1#euQzmpcfc#1_Nrg#{2p`M$m6VymAu`ut<hh_Gw_lAuCeGm*j#MX&3Pe1?(c4=Z_GU4ZSavi;Y`|(7C&x`dwALkxz4@SHyZOt@h<pCzfNSzeZ<O`LF>hxwa4JAQjB@-Jy|RFHLLGZId7ds`SO0RcX!FNm)aZaNbz2{y}6E#l+%9q!;(#UyKZ_wUOQQ1jrDG?J}K9&Q`b<Xw`->r(e-6hjr~XQ7I@XJoAwH=x2XNruI(WCa0koSZx!!=kJRmlQ?f4Z*q><sQ1?giYTnxAxpKWZ*#9H-Jaj#+!%%{8ens<<bN{#Yk`JFd)i}Qt?}CrKFU7T%y#MDo>c2V{f(PXMv!32)yl*I;fmiK%#an5<9^7KQS48uwT~@k=)>Y&4#(R-{XtLy;{cmsA^>`ys%XMYFS!}$gDV~9kyr<oDlGfptbIkX&C_Yk$mG4lV${URLOvU>Z#7FA<<t)jEznEaYKVLXp@^<|<bw)kQ_N|lr;S}TjoR!x~o;6<Z_xpLk`1+c-C#A`(W{e4I!N0z8g4(B-AjMDN*+0E<Q~%wkSI__b={16DxP#kmz%lT<aBIgc4VVN!m0MTDyCT*F&yK?L0!PCi$gMZGbYOq@H*)KTct6C1-<?}GZk>VGz;DY<e66+sHiJKmTL!n`z+2$o%55m(LlF~xdu~^8YXiIh{*{Qu1KYsAlUsn>Sm5pOGr5gKd?aGRkK-n$LJTk#zR-0Ox0``O;7{Oo7q=|nc=!{!jYE7KViVB!%g}#;=fa=F&EYl~csKkUZb8I@hzb8vZsNPUIgr6m#~2L;-T?nzZn@m@fz#mUahr<xRK$dT5o*x{7z4i*w+`Hz0?&s(ms<h1`++mz&*D~ycp+kQq3wF;6WABN=*uPOkHB-_Kg#W4Zu5Z;z<-Ea3F0M)317^2F}FJcFNFUHw*}nh03U=uo12Tci<t0j)N~MVF#Ib}i`KxV@YB%tb-*6*@8dR)+YDea{OR0^5HCVZ_}Sb-+@=8UfuD>vdI7J4pM?JP0A34U^t~(kFYs#kqW-;6dx0tN#h8k@l?b%pcR_odfXVRB$1|4$6XB=gnV!H-@I}t%$Sd$-_ybYj0YDqR(AE$71onX+7#7ncA@-mCW%l>a6%*I^2U_%#=60_?S;BKgHvhn|W^yhz;eTS_lEn&Pe*ronoca'

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
