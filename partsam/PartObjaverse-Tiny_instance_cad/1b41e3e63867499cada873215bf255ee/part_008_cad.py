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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1b41e3e63867499cada873215bf255ee/part_008.stl', 'relative_path': '1b41e3e63867499cada873215bf255ee/part_008.stl', 'source_sha256': '45c474aef6310b91d8315cfbd7a51af6c617f32f71e4a55607c84add35e5399a', 'input_faces': 170, 'input_vertices': 130, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10486523061990738, -0.0744427740573883, 0.3250693380832672], [0.1023692637681961, 0.14618651568889618, 0.49167782068252563]]}
GEOMETRY_BASE85 = 'c$}q}drTBp6vi(vK}B3~tpZiX7b}Vn6oFbFV^y>wx>&)Ypo6%m6#*B-2dJw>skTXNZM3LqmKyaB8{@lFjZQUfQWC6ITWeEgjjc_ZR#Vc%nm+8@JKtUBUZ+XZPIB`7_T%iiXU~~sS=`xS;Z9;+eaWiui{xlDVG&K7q{ic|URL6%8dhGpHiS5sPcN=JXXfR&3qnW@sdX*(RF!yLV-(le(o9#1;wr81R(p%f7gl%|d#ImPTvp{V{HmqJl^)~qpwv+#Qj}52Dav}~KVF@T7X03?&s;Fnck+ujs0Lo&dUJxsSK<4|ofCZhgz1ymrf;Yp*n5Nd%B;Azm_M}Prq$PH!e8kZ^7W8yJ6QcQB|^RiU%h)t$mf0PmkY)E=tup$MXaB&=QX?f1ioCKw0Ilr`d2@LFZE9rr8ijT6Fj%r^i^#+%h&FIY5FC;x7nN{&3x|r;gelrzItg6^R<mzg#5ro)A#jxU&!}s{n?y#=R6@_g|BXF75l+FwKt~=`Fx)Km|H?VS>S1~tzTsNa((h{=oY*F)!n8q_wUO;TyHlY6+WMjukyTkpX_Wk=dkbWO{=fM*FwsKe0}$O%vZ<N3;7y+UE43@s~_gEx%ofJ7xDwAO<()&iddiDpROz+--mfBHFw1PM~}AJ)hF=f`s6`*y<Pw6ebe_#{gdAu^>*{oADTX&kDk2)b*>2W<h}x5&JVOVnfa0RLcR|^pC|XV*a9}Uz^nN}K7mi-uL}8mo}_(>SReBY9KIvwV{T8?hyPUl%%$~q{S)|psegT9Ct;q!e&7f1x9w@>+zy^S#?*7cyq~j&nD5gKD~~gM(0bkKtMGY#provsJw6h1g602l+t$}F|7rT0yPaZr+dG>1$D-PpU+Xw!%@5X>{9t{__c{JD@1G6Mqjq&<pVyInb+%Y1*ypum)~7OUQ=?sd+2{3T-`Df8;0Nm;FJ<-h`6-`_r+K^%=FffkT-oR6%054r`}|z>;A(UJdp9>uusN6ePwhqWgL{#DelGXr*Q;G~9<@7{`|`Q6&(D>8zDMrMd(^KuPT8Hy{io(E`N26$KEDsSFW=|-jc(?-`+s2XBmKZM!Pmx}zDSi^SaFN_-*-3bq}DM%&~nK1e{wQE;ICnIe7`Sgv-<i0^L?!rlnK7le&mq37t!~(bZuh&ObHe1ByVqG{lrBGzILzW16Hr@;cct$yBcwl`6I4~zWYHlRaM<1_<F{!bFBXL#e(lYu}Npo`?RN+|IV);v!8GKip{~_T-I#2NAAmelzqNO+2_BnxF3AK6tuH`{1;Z3=kB}5=C5U?wpo3?M}O&Dv(MIwX6qh(%XgUm^-AUk8dtG8>O6Ow)er8mW{%*ie2;0O&-X}5e!MNz!5)?Lp9P=qQEhA!e7;9Dr&;u|N3CeHSRZ>-ewiWoe2@OSkA>IE_oyE{&wQ<M@EP`V>2pVIOJlwdpHs3ge15rwZ#(C|tv;|OiVzwdjc+@p#g?x+)T9?z`>#67(*E67os9qeRmW@eu+WGqs0OYAZ-6cbZvd}{z5-qku7fTE*MV!HOTo3^b<ic?b>OwoQt(>v8mI@n2D}=&7`z%>11$m9fLB2mfmea6p~c{8@Ji?c@Jetcv<O@Yt}vp&h%zJQL05pOmV@Vk=R+&N^TCDCA~4mL!G++t(3ik-!Lt#RbD%T9R9^(=fTtlSPliqbPX<qfjt5g62c8I4p<}^RCxEHG0H!(#tb%!+NjQ`0R7($2Eqzj+0nGwa%?8iK>(7PG0Ox|;&}=Z(>0qj}z*Oge-QYZE0k{CW%!AGc=YjK~h2TQ;mk-Sa=i-cfJU1VYeMW3DVxtky8}XbGV+j2PLr6~};-CY;abTAbNk$AX;u!>GCxUW6BZfgoKnH+FfJZ`;z$3wF&_Uoda5{7_I31h`O$KLzGoUVT26!}dAb2!*6tq8h6gbt0;n2R&{@}jg9?*f{ftXzn1m#F*M{p##Gc*p|8Jqxhfn9h#3DCjd1n{#6%JI-a;COH^Xc9OH`|E|E+zCNB3hD$$fjb~5$3pvoW5Eh}avvzr6tDvB104eH1MUqS3hoU~gboJ}#|{z^l)FQFfV+buppoDRFoAX^PcF(`pb6jv%(n}Iatt&c90QJq_5%09OrsH$L!nXNP;fZ31Gocb8jhgsfGS`GvvWXugB{?m2+G}{iQq)cs2hTE7&HPLfw_bs=oJF(0(NJIggV3i>0h)@E+2cM^&htKGsQo5tk1k}6bk<F<IawtvoQu2%04`s=yu89hM5dI'

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
