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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ca86a57984f948e1b5c46a20c09a6223/part_005.stl', 'relative_path': 'ca86a57984f948e1b5c46a20c09a6223/part_005.stl', 'source_sha256': '05f5bd54f17336f0d02d2183b00a3a8bf58df29d0162c53eb0162312bebc2176', 'input_faces': 136, 'input_vertices': 135, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.11962240189313889, -0.09964459389448166, -0.20001912117004395], [0.23614449799060822, 0.14641955494880676, 0.08240171521902084]]}
GEOMETRY_BASE85 = 'c$}q}2~-v58HNW0L~unG4K5cHF^Gr@L<Dr)5kzsJE?~R}7bQl-3%H_=ipIn}(V7U2*QC*)(YT<v1RWP#h+1t^gSMd)YYf^DiMFP#N83B^_oj_K?KwT|_5A03=JlKJ|NdqExtElrMsB`}e1en*Lu0<~+DuW*)>QFT=GyE9IhnTnh}^sdE=o)I=H~}}YgB4-$|M(MuCgdJ%a)&M5AA0Ojmz#E8g2>Ao^3C%XXH+uZO^iq{;-T!^KDK)e?~^0&3WCmXYZ(ROYaxMEsHJx<HyTcg7N0|lLMS;4GuYKs@~A`;wkg`z=!blF+YQ^ezE+5>8lBs;TzSp;?D_%ua(w{uY6a5`#egKM{ivx{t}mCrYf`6Azrz8AHF4Ri}X9H3*uFeC-5EZy%Dche19JCwS!KX*P4gV5#;ICRq{L=312UtBzZjElYX<8!&mD9CEmLpdDKxg62D6=$Nvv*fUoW7pd+r%CVAo?NIh|J@Et23%6QWT!*~343Vchi$;fY=Iv9EM7TMyT4wUhp2|>JeOnhx!0DP^;VEy7-6Qkg((G@b!nRfVw_EYq$rGE)upI8WAFBD%NaTLDgp7_?&?vm$VV_C;JOQoKKQmH@3Q|9N!Ycj4b^h@57b$nx!%tP5T_{xk>#4F3*5r4x@@m*w}D7lB>tA1|Mug@CzM)VP>C!w*d<LVfx=Xj;m6H+dD+V+$9b|+<iJ}Z%W&IVsXomKSXf@QpYM#Hyw>QawAO#1bhB<qq?CHaG2$NCz6K3Eq^qgwIryddl17BBJVZ%h7+Em%iw;Y8%u{_>T?SD%r7OC?@g?{XS(;iHjXpIlP~|7%zH)~hix-q(A`JkM?l-;#Pw@~Dxrul5AMH=eAM{n>Jr<f-on-|<bFjO&-aGH+YE!B>o1GH(a{q@JK2lE3>>*;nTt$T|i_N}f9<QqP|A;)nK;elJNLJ;4FrS`;tinrKM=ng-c#UIXFlD-E6x7sNl6CgUxYb3ku7Q08seJoxI+JlVJY^WZC6%B0`<wHU9uYNf<`pO*ZOtKjQN=gwihcAS;*K8-vM?NoLad92^cxRQ8oJSj#VwbKKszulX7zAahFr?I{_9!kG%+p%6+<BQ1e=-=dwJU=&O{s&bfzq+O=e8=@$a(+C@KprijHGHGLJI*(y-!`d#kuQApOxPjlx@zRto5V`|goEhU@$?GvJNBi+xBB%*ymiGj_{Q3)@U_i0S<iHPCDvtRE_|i5Gx}BYGGzbfEfK%ITIOj{&?l%TvRL}Pw@T*Y_Ce&agqKR4Q*X<B*R(l-ehc1}dZsmquZ@sA0S@?<-A_@!5^j_6&N?LV4L&k|c@dH)q48Pd|KO1H>*sP3_4{>z@7S3m=R~_=%%?Fk48HZ&G<jcCu9frTrF8gOUF>1#f{lDm3*jrj?kVH`!$;*<uTASD-YZkaT~H2R^V|VnU(i=Wd_o=8MT@;Bd3=5aU+w>`>?^Of=TN6TTh@Q<rH>Kcp*wta{$^R9u)FZ}&nw_-GiJ&>m3+BV`mKd;B)l#2GsI^X>W}YUh3mb&PoV#otMI(*^TpRLNAJV6;sM{$el&c?ha2`I?<!A;e|wzxw>HRnK5i(%JhaP@{4t5xw@TV^+0T2Y!&i+;nYW!`rI`Och0<@Amgrac-dpx<%2vsrT7-V}qUJJh!4C10yyQ78H&BnU@?-c)*8{R|7arEp?}E$lEfKO_*6Ei|p`XONQs?A#vTqmfM7-ms%X#>_Uz2%mws#r)qyYHprlV4S?wsY=&(+7_TLU9MK|h{%Fkb7QFN&XDQi=GeSXtkaE8;(xg!4pmiIsD}Ru5nMO}_Ly>*_}Im;FfM&sN}^F>b^oUVY|%0oU*RT;l8BMZ9%)Gx$nKEY?>&-5mW|yaV8C>s`^WS~gDn7H#0`4K~S>_`A)xKQJD?qs3bBpI+N6`zBT5tK@vr#`|wWy!T4UU))3HXJ8V1%l%Oo<@wq!@3%)$yKujo9lr9XbMif6d^CLZ7m1f}y=x@Ce<|5D`*DBJIQT}^In1+FYk}udKVgIK*mwf-Y&;xr5P53yB~L{&_ztgDh*v!e;H%Z8lHdO}^6RUY!PjEl<ojS|GV*9=Ka>0o@}9E(F`3`jzLPu!W%9jicpJ$-*R>jX)8%`bQJaE1mO3B!de11tS>jqltpoeOx4iNx@;IiCkoxbY!gqvDkofc=lBaO{r?~I0LuI|se=hap--d5ozasu!PsCfl>UIVF)(7pzb27eE;@?Pyui3r!V!w{qD(|J==fYQ9Ys;`-3$GkNp4A&A&#Lnu;W^B?2w$z-4Bt}w9-dQcqmy`_7-P1<SF=)&VZRn_{{V4$XC#k(4dRV@9eEs)7vUSDmLpzyzZCK6{c6eIa}Ul_<8PU$(_(upd7jpY|Bd+SSof=_e}MZD?C(3lSYPFi_>L3y!+74Z)}vo-UpRbq&-?I=h;35OlbEZr-+LpE@<rJG0V&V@%341<;=1ACyv5m?IDchjXZ+|VmT8)wAN1e<#LDUOU;f03{(paBY0er}IolF8lUGnzl2?$6smsZxE+ZF{mr@s#my(O93(2M~AQzDrQRk5tk>|6SJeOKPo=YyI+R3KQAs3SKsjrgr$+M`rWK;9Vv&b{4v&l2bIn-CkIppco8RY3?8#SA3>NK*AY-KY!jhaqQBafwyC!0EoJeHiyW^xjBB-zviauRtsbr5+tc>tTq@l=&;YJYM(Io8>FQ=_T<$<gE?)WPH-<cZWtWK$=TCz8ieUnY+uPoZX#P0b=tAy1`dkf)MIQzwu|lZR4=k%yAwr~}ESzC?~A_oDV7_aaA7Eo4*Mkt4|6se$C~<Tg}qvcI#nb+-0wCU<nUFlT$w*}|z^$>HQ~)Gp+1<WOoSawxeowIjJRIf&Yp97KMB&Ex>8KRJNxOKnZ|CAV@mKWFoCww7!rx1hEnw_<z?Hj|rE{mK5Em*&(q<mTk2RBy7Wp5&%vcWNWDsS4TrxRBk+ZfqvIQX7*^Z9;Y>d$5_@jOs-;wF9{sIfNQaHnk5qgdFK?J*iP_CdW|wkYmXGsC~)($cfYuWK&bfiR4u37;-B4C#Ij|;_BPzKm7^vpC8Sfr04!1`LB0A|62X=o!QP@|9Hu!B)Q|&>gxPw9`?(S;qL^SzPk'

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
