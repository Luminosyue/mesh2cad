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

PART_NAME = 'part_014'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/13cc3ffc69964894a2bc94154aed687f/part_014.stl', 'relative_path': '13cc3ffc69964894a2bc94154aed687f/part_014.stl', 'source_sha256': 'dd33950ac0148f437c876c05699acf4dd527f1dc40977c3dfbbb6a3c5ffb3687', 'input_faces': 266, 'input_vertices': 233, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1677265167236328, -0.09900541603565216, -0.3568820655345917], [0.1804068386554718, 0.1559102088212967, 0.23567208647727966]]}
GEOMETRY_BASE85 = 'c$}qL2UHc;79GWgQKJ!i8%-2@#TpD_Y*8$zF^UR4R8(vz_JWzH7>p%Y5U@Tg7K#N$EI42R6ckXg|No3p6XN=@#w0%`f9^T^jqlCpul3jetaaAjv)`R_&pr3tJ9lQ`<Ly$yP2#`$Qjewe-VU!SNy5rWZql5<kXb=v1826JHhq3EsUqp(&yMQ{4DIjZTTGfGEp#6jICE@>dl%W=b9^WF=Cb?v;E-7%0n<hYhl~ppdar;fGXr&f=EQ*Mf%<jhw(Z(Am)kXIE{Dqh<6l`3L&bR)&I%lLYQL8b)*ot}6KJ_Hmi2~pHi~QMQeqlmazE0w^1G7>e{XtOpxo1&^_v^w1zMgIX4Cz7t=P}3!}Ccm{#Uy2WAh0+PkKn9RiKiv`YK&-h&#u6rzp~+F6IifzAj8B{rBRlsh^tBd8BX6PIvS#o!m(A8#>}wUVfJDsH?T&6G;C==Jsp5a(g9m5%nwi=2N_dmD5P~sWeZZEq@B<$F8>sBmZ)_dg)HO{DAz+!+s%Mnh<o7^zbn=2<ulp=cEUFMpHZ^GSeJ&RXd$Xe)eqVyv1KQM(rmCPoq3Uymi(aW<)#Am!VfEc8K&UUvr$RHykT!9u3_zk9OTWU+;A1`7(6Vd>Oha&vMJ<)SuS!>%$^G?fJfIl<%K?_fUJUzhX!qJe9`<U3D8s<FdZri|4nbE4P;ik0V@pnsn_(_D;GU-*YSVw=n7~<wMKdL2*nTo<jBH7JT@ugDyS$Xt$%Tp4vdVx_87b@{^Esg68M?pmo%KXCr4l^rr~Y%a$QO+LOFQy8qB&)<5okfb@HL6qjwb+X}kATlXNf%g;%m>m?(@2@iJU_Dj=Z2sbw?{G^EZ?Yen>4c#=qc3lc9@7%B5f2<4jD^-`a6{Ra~IZpAI^JeHtzwC0%gI!m*zM%P0d{d%|((U;){Fv&{&@TpUp*WM)o^@{TT%U$+s!u~V)u*A$yGBypVpGzc{M+tq64&aqNokI{_D2}kXS423?d^3geU)_0X<mw@B+>dzo|fU*UMVx`I9;nvuh4z-28DYSQ4jLuvMaobs2};y6%lmbU77MPWyMoI)GjAjH`Sr+dzEzMOlk6?t^6*IaPDJnZ>neQO22hpMby8t>mRHabSA&jq{4l4U3$xU%2!ZxYOh9|-Aj2|R3nn~Hf>2)QrggbDw|uAE<Jt5?F-_leyvR(N0I)@hx}Vxj6X>0Zr^3vFI257wYO}_qvx9{MeiUqtzW5RHtGMi4?s89voz$=PSVZ$$<k7L2u=Hs&BKp$rC-oK%Gb@u*^auDUyA0>GOtmFlWyMkpquwSL$9%f>POl<!^w~4(wOSU+WW&RJboX}$B_oHl&_6Hl7GwaSkk4L7dU@I7LYEd-KV@tSq<Z;U6UsK967i&-piq$jeWb-#$$AC+J6k)wEx(3^SXYgJFj0uH?3boH?3dml=Gx3z9silyTXN(f4eR%?7NBlgigqC(oN4<LpMEV4ZXr?%8&YbjB|U_^VhCxA9&DwY1Si7{c1IC5?Y4N%^|(v#FOMVsV~K^%&3>`s7tMHQ2e&?YKD_;I&T=d>AYd+-i18B{l7|g>eqA*G4#Mn6u-JN+o@k=N)nITrvt@rTfF|HQ=NqM;5vb>PAE7+?c8q`P+fRVruAf9{*dFYdnJ~}oj9L#**l$dwRczAALRKlq^p(~ieGwrhT>ELa!I#E`SW>8OMj6n;KggwEj?zDu5>QNb&*zHqyFx{;&a}cp|l@ZhO{GH9-PU37r&+TVO!OOb^l@1UdtLo>%lgoFZ-GNlKsaYr}>vhZDu{nmDkVH;S{g-;SScf#c{u#M(w5X`t4)=`YImppLJ-Sts4_rKYfn<54%cn+M=^aw<*8!danAEpBsy^InD`_IR2kX(>`R$&t*SzTX23ZwHrw7LvOR6vyr^N_&w+I%;tye=SVjm@40ZA7i*u&d~O}uh@K<r%Hmv~cKxBs`?yw+;iQ|+)rM|5R~!1O{<J^YpTCA~I&a%`ZNsjk6#sYiGoAD=`|vuOJ%r-4RI0)G`fUrJ*PlJ-`90H;*T+APbKVZUrTxn4reNJ1<@}YX&HL+b16hCO!Fjv9^8~HG>JvE5&@ifV>znml=jRu3zw;jP@3zyl&)P!b*w0u#H`qKQs2;R<jh_Q|!dRcWhT>7{rIW7s@8!B~a-HH*OXRcvgy}qQIR)I0*JIw-k5%UJzN}C6qeZ^qe#dlR|I4=L(7YY1Mb~oaE#yaW3+44a_7lF}wBH)~+dH)04gEzQ&SOfqGxYn-d%T|8^1h<Y_?Vxg39a}XADlzF>N|qZnY(XY_Hxjrg|GO$7b|5t>8AHVLpQw-8vaf1gNA<KEyZssn|R()*J7H}_^o>$Q9R0wC#>gMXg{;R=W3r9azEyCCUou6ZQ2*?x+1;g`d!tQ@@&ceo!_HFUUB>G!Msn`d2o@gJO9q@J=}O+E{AcRhn3*<+3mn7%5U03T6dP&{C;oGzoy+vrFl+h!0lV#rfW+;EIqfaKl!k}{b;J=JX-UnvY(FbTyKxB^LgsM*}Q*!Q=RMWk5v@E96E>n<mV>SeQ%~w{MO^4q{~w)P<v^|7OFQ(<1e{=avu3tYI^cHd}}Q0XD(4ZTD7*czAP^f^1PYfL+$$OCG`BV>+-3?h-U%i)3)88=lgah>(3*|zm!{r$9w+|*0;HycAPKEUtOp!w1sXdH14WD@;+9(C+pirlddi=#qXb8267#xdeU>#x?>XO;oBjkD^LA-zphz<&xdh->}NnP>R0ujPW`I0#&Y|@7|N%bT9KZ!%AsZK-*k>L^nxk0zu0xz^$`27@+<FOi|cV+<sM@_{1C;jt$RuHs4Plly}&ocF`w$<TdaF#^K+tb9Mz8{u=oYiTZK`3+vF=0mwMBM^@p!hxIRzuxo(>)>vP-VTo6h1px&-Sy0ZTP=QBNwze}`kMY?@|kQRE;dbI2I{XzSAVuq7$`W~h3?#um}&ZTx;>UNvX(RN)4@6YW`=UYRMd_#Fqtv_=fR*Yaj)`mEr*XDWOJC1eJcQz$>F8i64!R_m;*iQZ*%;WZ^?{#wLD9%rO)#HxyYw=8FKkb`PooI^2dSW)~AC=&9arX#{Q%-iLxRlY=an9|{-zCa-=DKJ)nD@QkYSOy17I>4ce!7ItG0Ko&e(yUql62|d3EEdR*9^{I3qNlEu-{R~e9GJXx!-bY>G>!%DV0g{xio<NL=GU`(yc9hPgGm-y3t&&QGR6Ww^S##2{Tx?@2f2mDSkD4C;KTF$<HH?R=jW6G>)faG{qyWSj_uvhYQ?3rv$ARYvl#JkMFz4arS>n@n~1?WKh2=v$)@sqx^g?lqpVm|26hsOy>83ep$SaguG-uCxOn3lI1wh&oCFNQ?=R^+OMRwlQ?hjrAe2*$)@;i4U#B+WnDGWl?q>wu7193^I0FKuhPj)!VdphPLhPVN^a8l0EbV~LKJ^?Ec%mlkjH=bNxDOa|M!!03q6L`x^)G5fs1b-pX%03w?@E^V1l;-ehS`Ax8As~H+1@rqFXQg-V478-bc3{x_t)T6W6D7JE_}F;0|!1pOM6|gK<B2Ecklh2JrRZi-BK(F9x3noDbelH*eiq(iAevFu@xGy}@_sc0#vApa!0=+xPhWd;GQwziAkgz^mZyx`{bx2ot<Ha@P#GY6h(vtU2=99PJfgSMY(l`RFzpXaTRQTSwjM0o#E$0DcG)ybZ7&cpLEUFv0u61n&>*2rh5{xDU7m7yvGCqC<QFCjcjcPXJ#ETn4@rd<$?ZcqT9lxD`AL{1Qy?Z7{*ZfXl$cz=MDj!6zba!N1ULkZwbDo2=Vd-NpfjfsX?p3>*qR6!#8>3Emml30z=p@Xp|MfR(}PfV%-Jg1doN0+t7_1YSY6ViNzk0?UGz#qX}b^57+KPZ^*qxGUO}feBs?SP{G&`1`=h;O~Qf0IUuE0eD?tC-A!99btkG01g5l03HDR0$ku2@Br{2;3V)M@G#(V>0LbtF6!kHFc&8HcHnaGTwp#-a4T>*xWKQ$t>EFnncxB^gNK7p0geOzST|4Ih5$bY9|9f-91k7{K2^7GbX%d@G~iV5sc0j(zi!dG1p{NiYwFfPw^}g4yTAk=4)g~P#=X;l--3_Q%|o}5z_#Ec!AHOZZweE<DopTdKo9V0;MH}j0c;QS0QW%O?O}rZ!2~}F6Fe0-5<C_BGH?X=W$+xB;J(17;J)BZV1icxRt2vDUK}R43$Plv3wTLjb?}nlr5wgz3MP1I-QEM%1l9nr3ElzN9=tvB(gEfty{ij>yMcb-e#o8Rf79&;-SU71;CbLFx-HRdwr*>IUxKd%j|XlBj|V>wOaV`UPr=1=_n5@%Pv8Ua+qykQT#pfx;4^evs9Olyi~A1%H-R4jj{>d+j{=VXE&z`JUkRKGz7kvo&H`7#7Xd@SLlD~{j6sa$7UCD<c?7%#ehY0LA)iYyz9sM@_#NGBx}^a#z|+9@0u#XZg0BLu1OK~jPjtHnd<cFI{4Vf2@Vnr5fHv?sx`pbt27ZL!o4_03H^Hv}&w*b7KLR`megr%cxCVR;`ijIDHe!4N4>^qY5b`1LqC<WzB4&a2!NvQ*HQkbc>EKD=dtibm>vkG=0hkVc0sK1f8u)ea`><>1_Zs@X;}A!-#CwszRNz_Z-QFemQDBnvZm$!3H*gR5Zt!TB;4#2t@EGtohp`EMShsz;9S6pN`*;^C?&k8J{*~w5pGt=m$A9cG-|76i<#^{t-Iww5<>Osa?0@=ZTAYeMOPqA2e*sy>vH}'

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
