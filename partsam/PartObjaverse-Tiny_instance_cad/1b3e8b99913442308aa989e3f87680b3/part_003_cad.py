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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1b3e8b99913442308aa989e3f87680b3/part_003.stl', 'relative_path': '1b3e8b99913442308aa989e3f87680b3/part_003.stl', 'source_sha256': '2b360cbe73d9400c5b94ff1a7d3153f55ab09d2efdd7d2cd0164158e191f6e0f', 'input_faces': 168, 'input_vertices': 118, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.17284482717514038, -0.3146418035030365, 0.17414946854114532], [0.37315690517425537, -0.2617682218551636, 0.3637712001800537]]}
GEOMETRY_BASE85 = 'c$}q}3s6+&6~`|iqT&N877U=*=MqE|5CV#@Rz-z?s3<Bvc11vp<*_XINNcW-#Ky+>Hl}0KH5#ik(b`&LYNB1M5hF2JF(}5ERYN906H_(uQ8m5a`TuFL)6R67ojLRW?cc+>=R4nb@7^&x!>3h{hEEUe$kxNV*Z6CiiuPKNR#o6|7UvgKM3<B;^wI*vSD$8GpEWTvdy1D<r9EqzT~Lwlung8M$%ToQDBV(6>To*jB{NGMvkR1;W}jD4VEPqv>}3V!_lTI7#3()P$teBj`v3W9XSQHecR!x0dI{Zd=Fg^Br&rah?{3df@%7JtCBA#rd*T~$+2XtJ%@tqk5HG&xPj=L4xLhas$L@Y4dE3jx_k8MoR{6%MJK`I@%TVVpp1(?+!;etMZ@Ku^;SW&9o+7@hc0KF=QS#k6i_p)lSHw5|5F+(mNdw?Vzl!`myCvURdt7|&^PRZvi`%fSqWh@7XD{+|>)}`Cz|Z?V>c922)Uie0!hF`fgFffqkv_GyC$L`2yU1U-1=sa`4fz8P!5>*6^<Cu)#JBzCIO-(TOC8UPN2QLfS2cV`j^ul;`J?~0Phejfx?;b+NjfKf`Dx^5-a!9rHc7r7_!X|3XoznZzr(t6ZXkbj1Lj%PPwMF3wW*f;)J@_WlkAvhSUd4;!M!l&`ULc!=#TsmfAKYU7W%vtAii~Bja=83*c1MSVDa_h`Plbu7t!ZUU3`!63a&e-?K$+_TYSyehV?F;j5^N#@N25j|GFLMXBYj`UN~>NYGs~UQ#|~{y*RhmJ4$`q)lBpm+=%nmP>1tbk&Sg#KE&KAQD3{81ON44sqgOMhjV*$viR=6iO3InfI2Jk;P2^%>pDi^x}_!PC-!5k*NJ`9W6Ch+CEuf;s;;>11NhdBE3v=rs&U=AW$;thqRy&dspDC&Qhe7Z@I8~KVa{)?Mn4@&Ft=Y`#oRn=u&%8Qm~(h6t~+-f@`Inj`Cq;r=jY^h`1R$;Z#@hCYkRS-9XH{pI>op89ml@keG7BY9^zcxJj3h0jQr#4v91~q&cpicxbCfXSl5Wpur5y#@|Sl+{Yg!j+udup?}}n2-&%eh^$+&PbvGxA@6P-ReO_87`L1z0d43+De#8pYIdlp2`}m%a{0nd3+}@vo`#QFb_@1@lcn<iDMxV3e#WxZT;ePLV5_Q@qi*Mahhxs4*4*vNx@oh5?U>~<^#XJv;5?@bWh5lbpLVoYDs56nztJPm)zjDTl@0zG#KHqwypX6z%)9oGPuX`5rkD87?Z`R0l_3P-<=$?=IbI!tFvKaMK3sArPFw{@LzSuHeLjIB4n9r5NIB&80FrV)uk+1K;{#q|$p3iy9+>Aya?ALE?bu!lxpP<ecr{0&m>T>ZteL|&<-lo?F@_pkX@wMAr@4my5?|OGJ>g2D+oL>k$DSp&S@vRqzU=Hc`Ya}mh1M<V(=kLoX)F0m@zOiH%?xPh4a6T43z;z>LqR++vtY?n*S^0OL)2I`F4Ef`_itllc$9ZV%@}cyx#3H_)i~Gpq|M4mL?puQV)DLhTiY7?^o{UA}8}VPGpKBYXe^>fT;#)7BJ1ukAwny^y&o&|7c^`hp70K7i_M^V%P3-TjXv}%XN64>rOTLk@8Gcg({GDy_d~>^GKDGg0qE2!s?$Z&C;v3`PyR5&!9DcSyes65=U4y@LB(CdKi{Gc)_fV&457rg_Yw=yVk$8@tbYg$cb+46v{?-qE_jT|yF3LRJ&kcp2vl;smIUnb8bBg%Z5dJQ2;{9;16u%FBgK>Wy?1%Z!yTUpf(9clZC)(upxc_3u;JM-6iuW5wAnu!o(d@IE)G-=^aNYwuV}DNtif>B^!TpqQ5Oa9Sf%lJZ;CnXWx$Rn!j=3GpME%xl(dXay%X)RMJltowmDrbtJMew*exaS&iuLyW0(1Cw3!W>lK0^IgQ)R#0iS@{jIfS{LxQTst<M+Yn`ziKuVZ59ln{OcAJJO2bFWrdesV4-_gZc|tSFRJ!{q+%e?pE(ZKRYJickA*n{LY_Ug!}sW#hCvKQ{cZm4fo5{-SC&}$8#d96XuYdC4E}YA45N<$KZX#SSEeyJ8O~O)P!~27%ut7smti|Km_*d{HB`J?8n~b?R8(iX=`Jqn9<gJn=iDtc$HVC`ZVi*ew8mC^uN8zC;Z@7`5&7-_?Zz-?MMzMKS6CvR@$EY1UZ!IOIF&297^s({SjGdZ?e)s<UZs$>QBgV<P_=%ate7kbr^X#c?d&sJoPEE(kIFB<S1%5Ih^Z^VknMeD2||pl0&(M2!`SqY8*L^eaA2q52g+$4<=iwL&#Qg0yUl-&;Amqk>p7BkwA?h$M7182bvLWMt^EQa({9dwJSM{+=-#spP|@?p*Vorj~qbOsnKMe+}Df{Y7c5OIhwupU?{ejF@Tyx9Y{_hr!o{LQ~Q&X$*~N@y{KX2UgSWAVsC0EvNyT;qu7g~IEd;`4kCAEC~i&lA-5*CVJL1z4IsB7ccALz4&-jszT|G?o-JnGlc6}6*9zwKgXuT-6T*H&xCfo7mKJNVaD86Xb_~VcsTOkc{wcO<IFIUFjx;0DjG<=CHY48*n;A3Am}!RHj0!X6nc<*5LsnW$c92ULiVLWAvYj;x7>e_#GssFOlJm$}48^0V<H$<KlSh-&8H%&1x#Vo}bgGR!om@oCC+Bl6Mbx?EB61mZ9(f+;RmM<U&QM%Qb&xB`PHG9+NiL-pkW0yh)I4$_c?va)Jcax;bu{^DavC+AoJJl+%_ff`kEKp0k0no|7Llis=TOVYWt@fL3^T^Gs6U3+SDM+PpUf6LXL3zW&f=#G#j~h|<U;1oVkn+U%_L7HPhu#ZKpjJ#K+d6NkaNhB)l4$Hyn}rH+kZ9w>tm>!^|AkW{P(|n{I#a#Uw&xT`sYhdc80HdPM8lwZy9K@RQLyeD0;2'

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
