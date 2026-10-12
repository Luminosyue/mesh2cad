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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3b204e1c8fa34183821cf925128f545c/part_001.stl', 'relative_path': '3b204e1c8fa34183821cf925128f545c/part_001.stl', 'source_sha256': '25e0f85f742cda52cab7aed0b3235f38c20963e6b2d95e0c82a90d842ffaba57', 'input_faces': 160, 'input_vertices': 111, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.01462547481060028, 0.30029773712158203, -0.0014252057299017906], [0.11961217224597931, 0.40186500549316406, 0.12980812788009644]]}
GEOMETRY_BASE85 = 'c$}q}3s6+o8OJXmQ4y83U=UPRkcYAoP(eh|iw^{O1PQ1p;v(z{f=Ga&LDX)kuQ)Lw@%`3lQKQinA1I=1M<!$27)`*a$)usqB+*1$Gd0nqn)Kf9|4&>q?M$cLnQ#8T^WSsNJ@-4`IeTX_Qrx<DEBFjj%2#^T-SSWrJv<d}rP@+aRa{`Hj3_IwaZ$X)*FQh$y7cU{j2suGTB!{!v{V*UgvJ>|$68}UO~z2`qKc}D{Ia==Dhe&SpO{}-Y0>=3qWp4;)((q`iZU5T3^5s(8vn<S%;MXBtR1hbm(NvQ9VK;Wt6#n<nw0&a_|+S>>uS5$rC$8Q<F8A5SLz|rj$!Z*OvN~DYhM#TC?CG>m*OioSFRU7IrDYg*QG<+KHX|X>yzFPfBU|6X}bkhh@P*8pBs<<i?97g+SYpbsh4GZ+w_vHn8#N5wxPJM$89{<y7Ta7mdg0b!z0CV-FFk$NxLHv{>>G6;)hhgum2SDx#Rw8(W8&xZ{CgmDa9{}dV8)%e%fT7ic9s&qO)B$h?Xuv|G(tQeU)C5;om94b0r6^l(t_P{KBQzB%kK@4odrU2m3!S>td@4z`7h6v=Q^4E9;_M^EoLRFbn?0ak#JDZbCj|Hc2}p8uOfUw+_!&2wy2d|IQy~iSIZJe{hlHQ~hV9v~6{-ZWe#iUgYQ0M_4b#x&`@&#W<}wGg@`M`y>388u-m2s_3TIux@R)P(N;|=ofYg{;eS7=Y!2lMIU=_6TjSsar*mb%lL&`;dg0-Z@L{Ry77eMNx9wu|H6(8>7Q-fA?<h9NS@UK(+L@W(@^+DuE>vZQG#f#VW;TsPRW1g=XLv~f80{|hvP8M^j+1`HjLSY{WJvQEDM+@_dT))z9|>JV?w%Iw`b^X^v{?1*p}ax@s$P1@HdY`{+kY>j_=KZ|7bDyQBak%AO8XVfigVT@#eGg{g0#e;JQB|&&39*CtJfb_>K;Y)9w38x$Z{8o5=sDtIp#)$~Npp-UncR#f&z~_ZLsWw`aoN+qYEwNxu6~Cm$nkN6$3MIGIiG9eJ3~%HUV9Z$E>7Z=>|zedn*u^1UJG_gJrc$iwn}a*jCmZG+Eq#ui*xBWen15dXwM8Aow_N9L!lJ4Ank<j2^wOzx*1jzzw++A+?Zs#Vx``S2gj#yHzT<a|`GesloOI}iKO)wDv?_cQpZpNg+426-+uX3JZ6zI3chq~988do;kWzk>de(Z7>%&fS9V{khC%ciZAK;`@Iq=dSY7TAUB9EizBr*DoE${#u6d+gB}@_Vm^8muHHvq+I{4T-Va`ZE4@1k9vE380w%gfc__Vt`SDmQ~O}}2lj|>emKi6?H&p6bBAM`_w(TI%Yt_K0rNB*l6_)(Yo*<Jo=X4G*q;N-kBP2+Th1}{a;^C4yp!-#<HUEo*D2?Nt;w$u`|}X$VM)IxX}7L|9~N;#`bArDjzl-Xe^`R~yu*CiKY^d*!0*~C$K-r-OjC|K*RA7>xAb@X-3ot61;%fvk#kUe&<_8~BJq{G9diEKD!zxGkuJV^wpsR_<FUJ(H%e@r_>Q)P*pCm~aDKOWArIaLsRKtsEqtC=j?*>ryP&!Tp2GUBka-$wmtow*`S3m4F;3i@QkQDk&Qs2HWgLA}`m6iDfp5%_{>FyC;e3lci@f?;@LYT2u^&oTpGG}|%Y4k+eC0V+`z82SPN9E9KiO}#8DGFRSK;?!?GA^u&qbYa-tWqdaEy~>g&%er<AfK<K37}!!!Q2|>%P%&2J2&o&);A3l%40~J}2*U{BZG&do8WvkLliwI=zo`z~C!&VEgJ%%}>=yPQOOv`6m3r?KrQ}%Fm*%x<ad3kbip(@^#i9{!9<)Z@&DnMcRv3!7tq)c{W@697Epb;QRIIIQKrdjeKob)8f2OjaiLS2afNyz#n@7dAJlP^Ru~MfZzEI>bW8j`)$|4bJ#~Xmu&mrm-SZNmcoyHfcJ-!w~mURcLRR;yK>*omNeAKxv$|TZN~GOd&u*uU+g@OI{7p5w(jHO<1?OmOCIu})vk2YP>b%`Te3CZ=@nVNP?Vqb-@hUkkNodmkz*qN-&f>O+8h$K7_CJdHJO@7PA1QwW|3!*En3W{nyFc2GkF?y5_uX~r4A>n<e^&lQ2SGdllzl{sH4b1<S^=Jau_+>={dt0I-9f@L5-)zk>kl})MRoRIfpufoI@_ATFAxZQm1^CGIU<R(AlcRJZb@TK6yTKTENhGCUqKlCV47VB~K+sQ-_kH$^K4x_h;y=RjtyK+MDV__ThT;X6W3P8bt0(_G9QgkQzoFNFGEDCl4YAQ%&Sxa)i_RMKE+8M~x>xPfe%BljFIT=?tB7sX63aatXDVTtY6RmXgcJ3#kjp3&}-PE4heVs61KwLWa(BwU|ZCqs}Aek>^kg$hyuX&mq4+ol1UzJdqkro=6U%`jbP*eW+gKKIC4?lUnIT^(6Nqcc*qGcPDpY=<KH8qpLf$E7_g=4AqnT4B3O)lk7q6LG4Y}wJ*5`*_-M|_9pjZ=sbWrkUW4KKpjL5AP=SnlLwQBQ6tF1$m6Nw$UoKYc!tgyT1?g=Q;P&@Dmj5Xk~)Drk{n2VjvPofP>o~**_EO5ue2CKjiMUKQRK1I=g4EpNz@7CByu)2m7GnUP0b|FCg(GBo=%-io=%>k#TYG8w1}lnA;*$qsFTSt<Vb1)*_RqhO&}*Qr=bj;pQQ$ppCxyr8pz$qF8W%gxVU<|{ina!o_uV2=coQ~`{k8SzjioZ8KM>V&o3bvDen4S(H7NJc~MWMzKY7f0DPv8m;'

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
