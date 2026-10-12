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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/00790c705e4c4a1fbc0af9bf5c9e9525/part_011.stl', 'relative_path': '00790c705e4c4a1fbc0af9bf5c9e9525/part_011.stl', 'source_sha256': '438239e71c31d7b1a54291ed5b57e5310b98adfe7f2fdda06289908a8be60822', 'input_faces': 120, 'input_vertices': 112, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15782210230827332, -0.20779931545257568, 0.1555592268705368], [-0.1503853052854538, -0.19930076599121094, 0.1614028960466385]]}
GEOMETRY_BASE85 = 'c$}q}3s6mY9LG<Ih*TsZoIH9cNwtJ<J&KByR}yv7L(x`lP2_oK$ZIT;$y)1RZN|19Gc3a{XK5L`Yj<ph*<E9A9xF>4<ZZUS_y7H7-JRW;o!#5q`F{G&ukZi&|DFFm=T5QF&Fowyyga4G$=CKst<7kDw~<_>!gOOnR%&{FKu%tfjpQtR@uHT-Oc@`WU?UYui@ej)^HYu9gJtiqj8JcX**hcGSYS-aNzOH<rCa=nl<fR;v!9=tl9z7&-KT&5Ab&a7*I!;D|HqeuxdpvAxazc}mlbYbTU4nFtr~9mePNLB<v93K!64zQ8~UR@p*iY1_Yl4z3BJJ#^@dv1>*oW7Zz@K;-nS=m9`qBweuREVFZjpc%c?ilT^5J@-2uYa8oh+CD)5z6ebG-5{eG;k?*l)v;ezOMd0X_e1-|k#eC??dd{6kM#3#a6lU;<bZSO67)gu)B+|Lree5M!n8!=G$au4|0jh<L{&H&Vp%S4}Xp2(kbTjc9ew&*h)zP{y_@TJ2N>b>D>r)~=0<lJ~x%;zUJtlRyH@a4hJgs&vRR~}zR&ihY<ub=9G{EOA7ml}jG<-u1R$6{`wDz3XT>+eM1y3{O%f6x{Ep9~kiX~7cVn_9L({n7JS_h~))>DU@`8+;D?UHAa~T(m(>`U%wEzlVNSOW0S%anx7*#y;Vz+7!&QW+To?7x;RIc$~x1&6u0>tFt2Kt16LWNbyJiXI=_liam?#zQ+&qZx3Iq{S5Q@peu4#zd(JTqc{(rdLZZGbK$EQ2XL;E(5JE+{+l^_3`NcY_@-Sy;5t@>q5t@2$Vsb2&dj^m?}?|#$=nY=0q0P@^8`8B`!Jt0XXJEvgq*^im}iwe)@=p9>HMgtW3b=qhp4Z;fqpdjYDSa42XkA4eaRAhJ#q(fYFeP5bM>e{xC`^Vg#J~xI?OF{EBf4z^Q>0g6TWh<6!WRWd6qwhZ*tp?b-(0!czG9oWjS&T@Rj+s$Zy;Lf9EUYjDfEQr{X-<?ZAH5-x0p-wgvN9Rfl{p`0ArH)SudkxxM<8^IVU5N8~G);5Xe*^oC@7-qYY4E<c9vr{I24eH%F?n{XWiv98*1%ew#N_`JxK@U=s0u&%>%;TyWZH~o%!!;Aay!*0TlN1xhg<Vfw{YfdGoKY;s#I^zcB&wZ(vk)yw^!Q2X0Vcjg;H`HSK?8np{`KFa7<fN`de%NEIJJn>BV+eVOoC)yN3&qF}LcXc$7pp#Xcji}L$9xX0z`DN3SN2@D&Iv%iKJqH+o1RC8T+Bb~3a(24pD!oi8)ClW_07foWYJ!n&xCKWFXKGi&pj)U<6edQrsreQBIF!A!}Cf18GJSD2=e_F!Y@OPrXJ?!eX;PhANQeNJAgj<yfb7MW8Kn9%(I0L`o9m~P_`ZCIiMK%4Ikm$8q1N-=aep&pnd>+Y4b{~yA%7BkCpNKqh5<cy;`&q{-m|YKl~x?^Df1h51$u?tE-T|YdP|-t%v^!>h-E+=yOmc`YB<3xe@y<eh+i@-HQHi<YK?PpQ}dfS6z^Ub^C0FKer4yU9++7x@owM8&_ao<5F>5_M=`oz8?4O?~|=Q@A^nQ*W}kp=qITR{YS1t{mDf1e>emF$;DVVb&}ONk@hZt-xt0<e=GW|SdRX?Pe6W7KK!+XsJ|M6{{6P0pMquZYoe_BQA>+3|IeeW&rf|m^4CV-bL3Kv`bWrD75K`grRXzd9_D-}+<KmOk)wSPZgoziK-BB~Mq>`VzKRR|O(T%=%@$n8#ys?&0$;B$!M>t%ux|Bm^qGe1uDP21SgUW(C$om`l3SRg%<op_Z_gPiZ+&&Pn3h+Q{{2_ytdM{A)j25e|9*9LH}_y^y*<^1+@9=AZAEq_J5X)O4rDv3M7AT_P+O2~$oAAWWP7qBwFB9a>_+WMb|ZUG-ywUDgQ?NvU~&|70y&BtL!C^HAy1@EBTpnxrOqHvB~Pa+<mu!jzAc<eO($D4lblM<puS7aAkU%ZlIM`KsX63q@?2^bc`kW2HH|!*Jd2t_o<&Zk&Lk(36R8R0L~=ZJ3OSxUi5f?qM2@A7C&!Y<Q6tIY$YZIY<gw&|)IQ{aWM678vM;$OwL7^dxf|7!+>I<#y~#4!i|SAIBKuJLk$uPk)B)rGau9VGIfy)jI+{F$Y@kMv4djv3G31ftQPgnqDDnvEaI!_i$Ro%@se{Nv$%FZ}a0s<OIfNWY?Mn_M`%!z7{m4D2UC2GiovH5R&g4$i_T*0Fc2s9_JF*kif$T(XO|>JpCO4<rkeid6QSHgi$StXk<d)>NR5x;4a!0BMIX2qH*0tF`{cGmWmnv?sZ~vp_uYYO%SbF;}hnch9Jfvcyn~O)2t@&r3S+`m4{?Z>r!BWr'

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
