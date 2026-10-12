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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1d515a6cbe847ea91e2c5680b8fc67f/part_013.stl', 'relative_path': 'b1d515a6cbe847ea91e2c5680b8fc67f/part_013.stl', 'source_sha256': '78a3efe61cbe07f5bec9cf56a4ec3245403f10527c63fdf057a2029663ea5804', 'input_faces': 100, 'input_vertices': 80, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.457444429397583, 7.326992034912109, -0.7667659521102905], [2.0729870796203613, 10.042476654052734, 2.084808826446533]]}
GEOMETRY_BASE85 = 'c$}q|2~d?)6vr<hinySHLh6GLd4Md6<_4(vL_rqyp$&$OO;1@AheVbnGpCnf=s3CJGL|zh%MubdT+-3_97P)uNkQ!u#uMBd2n7^TvU~sckk6)On)+tWoO6HoeCM8f?)~ofeQ~jNom`l_JlX7q(n{vQO)lM;3tN($nVp)LoHcaO;-xmM7dS4`o2JK4i<@o3mat{MNy%A>nZBWl@3@p;-$2DTB|S4cbMB(I(le8i1&^GYmX*wT)`Gc<lX-h^@UTE-gkPYtT=}n;qsXB&@_GqZ2G=p3I<Ac~n_DMvZSr>h3A}jpAi>pvw;v0xn2XJVvmTq^Z>j(C33y_@<c-zf%K0}D$FTY874Rpm3iwt3-{D_#q6)ld9sEs|p6!BLd>&K^u6jFRTxD%b8~oL}%Ys`f-j(^d*<)PY`lA(s>&~o{`R_UY9K7JxMZrxWl^9pIzlh<!C?mMCMT<DB_~tYCCoU_;eB-x(8xrPWT-9^dS>$8C4cv79J~-R4q7?b(`GH%sxiWwK+5PZ$UW;+ngw=Q9_rvOa;8Q|nK0z&Y$h-MsA@n;D9>~8@Q;l|D<mb@EyEO1Wxmwn@>Gd-hf5IVf_H(Cen9uQ=?~$)*A>t@c`@&!StmU$tUzv=PbrSPbBZDdt=h}2|W0Fr1{ASDoH#`bQp6uHhH{ieTn<~MLVY{V&)QO|0Z_|pah?5iT4*zrWk%wu>5pZ49Y~-VUm{5i|dw;!#_3UDn{*694@HcHWBYuy3S)aq<x3C^N&DDs1^aJ=CvK*10CBW5!IQIr2zNv7?Y4Gyzz}diZaJJpN5q0Yve*^KGW&PDPA6-EHp}DtEH@~ys#^MPU?6Xf6+(*3nRT$UUcBvL|-#A~7d>`zQ^9uCBJWX0{BkE?iK-MkoSqbv{Di~bto+|g})ZTdB)EiI0Ekpbyzq}mvVXjvnVx0LaWF309qwXyI?Iy%oe@W)wo_Ya%%VNnZhGHKwqjN3h^+kr{?oIHwjPj6mDaiq6DLvtDIhF7W#@*Jl8Ts^;c^bx>@f<SM3EYsKCb{Bp6Zfx)0M|W_lIK8DE7n!bnkVDz2$J)fvv4o!esDXuy5X7R#~<K)VXO9o8%z3XF|VAeo8Y$PlK)r>f8FrdJ7}M)16MLO%W*GullwdJsf?fM>V-P=doJtX@6dw$XWRqV6)io0cB~t?#r&!C|2P-Vqh)CzxGB30+|=fG3EVLVT-|v=<{y0bI^v9&2(GJmHc0N1bnG8fz(+F9!_MG_12vc6SDz>SYhIK2Y^=M2I0wpPK5i?))dySgoSIfONdHG}GJZkBA<Tct6L4c;0{o3GUl$@y+u%nS_sA@{A7&V_?+tnW;B41!aNU4X`JA^Vfg7u<C67<5L%VSyxNgib87IBqAh=^LxM4$uoL7%IIIq-<Me_ZS6N7w|b<Xk}KlR&VIlmaxO+9^GMLn|}@qSP>4l;f~*)jOX`+*x<hRSs*J%1SIn^TGOZ#XLbZ8jW$fA(o`oh1YDS(6s$m8D_%Q{;1gzI?y9RpWi5+{ni{ZP2vKb#!sN1OJdbyq7G~^5wb&&%BL&xWfhS6VpLQnU6;){ME8G;Ox2F&n)zPd2aAsig{k!AlEUa3S9TzW^lI5M#itw*OtV+^!1R@$17);J!3+;@~?-KxmKSJ0*b3c|NW;!>d1ff=`eiQ|NVAw9LIAI^AF(?Mz)w&C~47tmCHEt8A`TbV@QXPJ%rl6T>QBBkoKj%;amdAcMOd;oOB3{6-Irc9m!=pmx*KxJ%#MC)HjyelemoLGLqOxtA5cJ%VjFrLWgq+<}!+WMp1hN#hXsPlgJkLyL0j8;ze4tJ-9?rT_%%`pc+jiJ%w}x*?NlC5m!$+>8XDj=?Jo8xI}Y_A{|3qPxe&Odg9TPi|`L1J(=u|90N#u(|q-mkDl6M{Qg{Cv6`nlwKY_OL8LX**Ppb8MD!0N?Mb#mV|tJlZ7ml!x?e-KhWrI{p>bWP?Mgm<t!!7Te1)Gg={{sTliiC%*u5za(btc(2gT@UJCQikeLcAhp#Gkuoro#aRw$0JJNA~?o5M(pw%Au4dvFqI;p<O!I7tw(aI1BWA>Pp+Lu(wwUaWZ#X@An*R<Q>&xzB@%4JPePYoWDbVn2y}7)^RI**0A4xO67zLaZB?9!&f;NiEv=KjBv=E_Ccc+foc$ieXE<Gil-PK)Ng0aj`bGE_VO)tM=kDiez5;ar^6?FCWv^cZTs;e;(R#vGyV#o}4Yq;JQG}iv0oqVbU7'

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
