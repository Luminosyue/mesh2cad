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

PART_NAME = 'part_015'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8b8e14ddf5104c579a6dd100ff8c0bdb/part_015.stl', 'relative_path': '8b8e14ddf5104c579a6dd100ff8c0bdb/part_015.stl', 'source_sha256': '93e3e31b3747575ae7da1f6d31517cb49a8e5856d19a2927242577fbfa72d2af', 'input_faces': 264, 'input_vertices': 175, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1541319489479065, -0.21641337871551514, -0.04818342626094818], [0.05028723180294037, 0.17978987097740173, 0.15177981555461884]]}
GEOMETRY_BASE85 = 'c$}qK2Xs|c7QG<>gh7ddNE5$+iC}_KqzU0EBtuCclpqkwPosnoLK0dC@+g7?J|#gq_)&TZ5FivGe1cfw5*?68V!%(a4u}O&Y%}lfv%m8)%UNsI%wOxQv(LWgo_EVR_uZF7_wf&?tK|2nO7C#t))#?FX{n{^swqk7nd1_YGFqjkP4`oQ;Pua^^ZLd_MGy5;Q`C&$#H5Ub^x)2p;4Y&(28TF;M^8-8Opi+)H8DLgN%IkLDH%x?pD{KrEy=PUZ{6YP5J%e<A&!}j|M6GT8iKj{*y)p&He$M+(b^gI+tzND_T()o20zFjyyH~0gPJ#U!-S9B@ut@5cH11y8@W$`HzQo9zz5xQgI}5k+YIk6x-fn};<yxSBdP_SuP#OAoV4*~a{Mvq=W<@r{%Voa1AF{d@Q#AP`!w&)i2!fJXS|I#-h=_rweJ?eKcyJ{DzR)P`rUU1yqeH_H^vtgz6;~IcZ2vxmKGr1W1nLDj#|%x_dH*Qbx;?o9EE?)vJ>#{mwP~KxAW3ojHkvX@M_G#o$xz-73=1#@iKU$=l7VO<AZaD(O$g)c+ZIE-$K8<h?UrfY8Q^fPB^{;af4i&5U1LE!gsHL?JnGi^)#w32XCf*_d5EY9gX;^>U819{`L;~8AGSQ_J3I7Ou2~l^*kNE1@o<P0{vBw=(*bV7UoNQKbP?1cJIJ=Lmz&v67Tcx8omwj)HvZI*J3@@%Ci#?{~t>D)VjMc&QUI`oAKK`*(c|+c^F^UP>J(vits7X3$*qg43hl$HCpmx;L3y0C0T`t^UFQrKW07FU;UKf0{^q;DEJpTZp3ptzK8j$pZ5v>{2R!7vn=@-o_lw*@bfReg82I*kZ+E=*}{+RxDNf#7af8BPh*8ozqkQ*{bMgf-}&N*th;wA;=g}c_We$U@S|g7UtFatpzj<MeoS+$v-$gZj9>kbDSVf2=AeIY&Kj)u?KJR4%H0yQe~~Z<{l2d+{uz<G(SD}QA@uw1;$iUF%NAiD--(xX`|fS<M(-rlv6}SDX6SD-#ec|Ca}hVRd@bg6D+Ih56^{D#R#bc4&a3Q;8_?ct*lNVT6(D^0W;dSm#vM6NzP?x}`5%k?_mrkfecfCE-W=CK=2d#*B|PUw3V4;(8+B=19x2bgF<khRW3vBy>*4v%FJC%@xUpw&UKwfEFfZdX5AsGul}mo!jC6s&R!jJd5BH$HzAie6_*cECb2Vc4cI=09{Xp<nHXpF>yLl$V6y7cT@FI-M`*Eq{)s^+a$J~(o`~2()=quBNA9)e$<-L-19NIe;yqWY2^29v668UI&dx-z|gUA!57WiYGy&Z)&9FsBriXg0y_wqL~&&YlAG0q>_F2;B+dxf9TI3ID(7a*V2<>SJe-z?VJePJZ_#dB%1@W~0XFCX7ni1n>VVf;W7x_Zmy^8Dci_PSHw=PknXD+USQYxgER_x&O{ugcQ)Bi?{@Z(zQcT4DUgM*-lC=N96;SJ%t2KIVnR``|ZmE6x?;YBG4og-q~9qQ9(L$uQ)(dA>e)HSxf^Xm9PpIp*GU6!Z6_gn~DnNjR50OZ)GXyt;+?8l7I=BK)($Pq>48^Tfwu9`2=`z#F|Dkvf{SXglnsErcHz$~tAfE%{dVZ)8u@v*&sn<ij8Q)RcUz%k*#$=C$NYITw=GAdVUT!(KbDVrt<WQ(xs2Rr2qdUw}NARihZsalIq{Jsnf<yid+yo!zce!uM?>d9?UW9_q+-RQTQ%vR~&5ktcuf+0n=oRo3QMC4QQB8uU+faE>`#`(-?-S+ZZ(zdCN`)sP~o*UR%?uf#JyogW=LT8U4)E&I@W&E%7Ie*W926II^!#Y+B(fiB5|^LSsGt{uX64Z!<e&6D?(a;=eZCf<+y@suPN+IiLEbGeUvo{#-97taQ74DyqEg11EKE~kO;i9gEyB&pG>CvCiEXgJO#bJi}&lNpb0fli%@JaiOvmiJE96`Wh1)Gd;?9jYP^-KpPVKh&5#7^nNaCQ?VKWt*ff-jw(4wY6AhW85a3zpDFQ8ULq}Z)VAJa;^;e7Io+RWTT9~IDJE<`n`Ps_3J&=bi<$3yZ30*b+TU}Qcvg4B2OGgs|X*tOwOO%19ASC2hXhmpDgzZ<-8h#{MmnXwdC_{ndfH(7^ib@uJG|+pkCCqV$934r;6~Y)8rg3$(xPm?k-*het5Z@!xi-;uXdbUDfRWC)Yq+Yob&3H0rDP>Dwgx<%Shz4XG2r)W<(X#k!R+tQ&`WX1D1gw`k9<BbH7J@nStS`Z#6zy-bcG5)<f3{M?7;<Lz&Nu6Hdeb=gqj^m@{_D{nUFF<1}ydm?!o1HrCr{o`v^=c|CCs?6_{oE2Hc_)SbE>Fh}Yr8t-dQ=vR1On-x8<Pe#8(a^L=B3F51Dy{5y?9FBW}`%LdcQU|><z;{`O`-W=S5OLJh8flVmjio+R<`VFpymnG|a$j=q?~S}w?y{h6w)`<WUXb_RzQS<mQQ3H(8Wjy?JVy%qK&N-y2>zo|)Vuob<{0Qf$MAl3zx$@t<L@_<p?PmK!bafUsA_kZgn5Ux$2gqV<eX8Bf6RoQ*ckUu@2EpKKUM1vS@7@kg6#W{;B@d$9|rFk=KmJjhfJ1y37a|-n)hL|RTSPMW>Ku<cds`kPj2QQugrI17ec4^m3#LGrBbKoUq?L|;d7Bs?&-5}&Z|3@mchT@R-D7m{Vg#M^T)2JGc#kp+#9kRoDx0?yr<U)ymuVu`W_K}g7}Xp#Pggp{*L(O-4o&;Q+5V*8@fft|Le?L#Lc*k`;U6}tgN$NejeH*&tZL>!Abc3F#U?a8~tB<1Mx~q#oxcl3bZE=ko=DxiuZsSkS~1fX`FkW(p1^sz|>XXduCzXjK2+&@jrHXJ#<Pr;y4fNl)MW1UHJah<X&5}^#J%M!jL!SzyXrSrMVKn(Jc8MjW~_<@_h6F>cwcZ0K7S}p4@vp_Z^fx*(UFU<iYZt(QJbFH5n!IP8cBfq4HwHF&#gG_w>DsdUh5R$~Ygb{VLk0G%1oiZ!h<mrelOpZYgzMTqyV9=AR26u>jwR-ou6X-tj#CiR@3zRm{sMSc~|cC$?>d-DAAW>%>Y~hgQL;Gjm!lp6e+-C-GZ9Dc?D9axSX_B@(Co)NNd6slx;1GX7`AY?r*+TP%4x6W^moms{Y?>7^2Xe~#p5x0BM|y$;6X9l9aETXdzrl9V6MiSyR7nk=cI>Z;Lkwm*?*QvZDV&;LX+uHAq2Cz3Yp+x@?PBI#_6p}!^VEg4Ac<Fq}QSnH|u)Ak@rfAWK<r%^AlWCihL+P=0G#9C)jziP>5;w7|wZMl>c^wF}zlI@nfLVG(ojki$0N}Nku`!1tiO`L19wSJ9yJMn7j#ndm`@NU}q#ILbmK5;(Bw8u6+AGd}49^zdTjdxPqmTV*ECa3X6+FCZyN8@$0Hxj#v7t+?Ul0F*0NP8jiI^s#RwWM1zpLi1Om9*!R(|HojeI7_|GPN&WH2Z2DLmWdpjH2-~)B}mbsGC!3zB94bO>J#WDGo~>Anr`N9_<I{-;|tgyN`T5>iX20uW7R%q^?Q)Ao2b5(RMJk=9*a2jCK=STQg#<yHPamNZo|E8}%sa4wg8Ho6z>PX?`gCXl|q>-N|()uW=9BBZ)(3hj2{YDZ%X1ifuiJ8_^EooP){LC)b$ksJTaIH=@*|-y^hjyhrJyxrb=`u+~A8N9f;x_S3`<*?e?+SGENa52iiBlD5P?uB(l2K&}R{=ANLABCcVx+cHjHwrQ>%vF4I!Yn(`|xqg;(A=ibx#?R62N8FmW){hZ)A#O*l+a9;1E^UniiG5rk{k5)2d=Krq<O0e0)2>2XjdnH8-PgY==UJ8f6YNu!aTNP&&d-tnaslM^uZ|_v$<?Oq!vVH_)!FA^OYWszhjw+!y&Pk8YM*}#wrTkb+ca)Sy9Ke2ds0dMwIFUt(cDAq(~wxVKWj-#OTvktB!1Esqb2+6_AuHliJKE^-I#tYiHER{j`uumAJ*ESg!5U$*=7)H-HEyd*TZLP9814W#99xdXx!71HpF#kcd~I0lOM*mcw3*p+H4=zI)OUEhTG5{Prn3Wt;bTw*>D8yne-b=(cEb20mP$;BP|(2JCf4JlHP3ZW8-xHUgYD*>1T$LkE7j-qWPyN8rPz(O<arEkNw)PJ(TNLn_L}ovp6q3zqOX+5$CbZhiA~%I+=JDvF<;Pd!y}4+R2n*T<aNZ^YQWQYg&@Zwgt2^$;I0EOk0dtJ|l<zx_voqAJ%#)WdZxHr=3T<+~zZb{3f<-C0=E-*VAVe`)b=odk(dWZ9aPuWfkMip`Av(#*!)2i|FHPn?kJhV4L4`Vy&ZWZ5oeYAI*&<)?5m)=7!SNcmlEJM$y*TX~{%#6Ul3wLEA|@o3_?35Kko5eO|I;9_`t*U!Z6{n>d^P^SFlD6c^Vln>vMl*~B{DT=t9Z<5#7w|9|=y^1ptjE|5z9Q2zIxl|QTOJ%g;v)*l~P(S54wbKZLSRKdmbS$$Jd{{-3;jz$'

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
