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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f000c34e5d2a4d2399ccf1ebb83f956c/part_009.stl', 'relative_path': 'f000c34e5d2a4d2399ccf1ebb83f956c/part_009.stl', 'source_sha256': '96fec87cc532c755ef7555a8381e9f48a2cabee9c1cd7ea987bb77f5cd2f2223', 'input_faces': 128, 'input_vertices': 122, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08566776663064957, -0.15930147469043732, 0.15090452134609222], [0.06290629506111145, -0.05507546663284302, 0.3511459231376648]]}
GEOMETRY_BASE85 = 'c$}q}d2AF_9LHY^Z7D~&3O%T}<=U23pa-@<VHTlPS-_RM7U(YR))q=zcT1rfbU+d?iWty8Dn}Lyh=_;?a>FPXz>CBnB3>&P2>#(gObiJc-+TLg>&%ZaF}lq!-_L&L^*3*3-b^#~xI1)AW|2=OyE^HcE5CGMOjK8v%v$_`=DI3>a9BfAYYgilz4)lyFm>h>Pk9V$VNW@${lTh$bF{-*Qd8{AbvSDp1I+<nLuF&2+An;WuRiGKK3MB(^7HRmdHMOdj)Lr5$8yJi{B-712u=Ix;3+Yeij&7hI-a?6R<rT?CsWS}&z$F_ceSlLVIEJt8m})3MEt9xWS>y{&9ipiTjjHiXUaFGd@8*6`v&Rtj5|ln`=vg*-z_<j{vUpE!m?lDqx*$t%45IL@xwPCwe16cS0ClkCtTD?dZVA)GJopT{9SkE9FToxjXh=FFZF7_${RD`vES(Uw8BV#+6Uf6`=r9758IUbj`$uPG1xHAhk7+1<qhRYALFyE!{+%=?;?G4<<ZBn^4fmsGnXHd$AR-ny;q&jIfJBU>k2L7saNB@KdgOQ_6gTpj+c6Myvlo(SL;@dFWz{_e7w}VNFSH-s?WDyy=6Ne;-m9{ziU2fJe?2mF4Bk2hxM;`Q=Ye5GtS8CR$uvn*}K-KN9IYq{$#dXSK&*Z)3$!2=Zu}#NgrchjJ$8Wm-k!7vmt-V^&1}lv!%Z=eeHg`{VLBszGdraf92JDytmKqvAZvnr|X>h=y`^x>pb-9n%&Ybt~g~rpUN9o_a3$Qy`|FA=SI|%=K%F;KFZVQfcLldUGh75u0}n1P8t__MLc=_hgNTW&2IiI^XZ7sOE_$~?!+4xuSfjlik-6m^4pQ;Xm0BzIiDMa(z7f1d(3@8ZLjRG9e@2<>GkK+j+nhsc5b`u^IWXOhbt#bug}_USr62!c{&CZNpI}f`mT9A^=iCcmD(=HO^iQo-Y@Ihx=qeM|A6(p5g$e$Z%klY<h;+d+^4Rk4broN7mr!agRXChT;DY(E&KJ>Z<hZ32^MeEwY)6*6qFd2J~{g~$or>9cZ+u=u3jO&JMu1B{YQo_{i+=nZ;b2TAkRl_=l5*=u`ey-9YN;`d7b~LlE=$F$N7hMwcW5>FY2S$3!bhY<Hrl@G@E&{>}fA)HpitOE83{poQF_S+$PQDyoG;n-KN=`XYcxicFpFxIL?pUso7k|@WJn-r|Tz_^ujL9Zao*fU)OBbf5=xZJ-uJ_J{i01eE4YG8=B2}qh4JXR+=dNUF(^6wVv78(|a_V`-pmV9YZgEEj_(YsgFKSvJ&>mKJ@uReDppIrAIt@j!`e?@3FisBwcHttH+B+F=L7RZK1|zdQ}iod{o-MD%2JJ%U6Zs|NE-&AfLl@ULNFp@KmH1IUl?P8AQ$pi+lnc1TRIlnz)fy6S4u^ifzk~P2i>2)`DCH4q{sX*#cgIZOzC4Sk1c<*$mF%HJaB@<S6i9Y#W3e3hvL#!RsF6z2H8)`teFerh_~2>cJ}k*&Q6ms~fM5$gbcHykdC8A{n?BFY!*-6PXB3#kLe=Pw)V2%S5Jt#WA{YoFX+7i*4gkg2y0pz+=F<$id)T@DOA_@DOkYvJW@|+!xsm+!vgLi~}cu<B^@g@!&4VUf?d^-pEvNZ*UrN05}ai5SaxY2+l@|ZBAq+crmX<yy{Vc7b5Gx3&FL>$HBGW8l)dw1Fl9^fvdp_kaNKc!1Iugf#-oMkaNHl;Bw?Fa5;E3uSvWn^Lhv+*o~YCc7q>9&IZp$AHm|j5$kIZN^m+#a5748SCrt6D8Y#+!97ueQ&6LDJu<;gl;C2N;BhFy51<53L<ydN)W9Qo74j-T4hM@I0WJXNBlEx_i@+l92hZR&jn{q1Qt&Wj39=Mi0v?Mj1CIsgAs+#YoC3}R7oh|{j1uhQ<#ETvCU^L!e|7!+(d7fl{EsjCo7O*j=HDE~8%6&JdfajHPhTwm5fA&D;x1)>0hb4M$p'

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
