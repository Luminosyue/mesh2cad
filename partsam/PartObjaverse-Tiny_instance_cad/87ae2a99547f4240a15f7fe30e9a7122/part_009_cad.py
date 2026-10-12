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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/87ae2a99547f4240a15f7fe30e9a7122/part_009.stl', 'relative_path': '87ae2a99547f4240a15f7fe30e9a7122/part_009.stl', 'source_sha256': '55d3dfed807bc7a8039c469a69c928ee9e0a1d4f81ba4b544e41eaccf8f9548b', 'input_faces': 272, 'input_vertices': 183, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.24617360532283783, -0.23224572837352753, -0.23631957173347473], [0.22920840978622437, 0.24733185768127441, 0.2804194390773773]]}
GEOMETRY_BASE85 = 'c$}qK33N`^7QPWfqqNc*UJZ4%2u~U_k>dX)s+AZ*P!zclL5z{aO#F#4hSm^XQCvbIq7ouOwDKDoq^7p7R3Cl!DV?-BXsfe#_uk*Fo4fMXdh5Ncwb%FE@9cZ_8TL8%oIjBfzLje$^4CP!bm>a+Zhu7~tD)3ZX2c~X$H&Gc1x-nq?W5FUo&GFb*Kcs&$YDOp3}tS>n7E|a#DEYrpzGM+fIu~1?9{~M#F#13QxnI;k=`q2Qc|3$CykFuh%=vCv<+?_sJ3qzsLoga$G_@k6O1is7fYxuTCX=;giq~1M$g(O*Derxvu>8MzM}aX^z2@{hjq1b@eb16IV0I$_30u0@5gdI`j8sO>DefCvF@(qVqI(aFzd?nm(CM<{2whK-H6}Hy4vICbL{UbI$_uKb3d}KE$DrLbWh6JLmbaI%DOW2#~u9M&1*+l|DoV*e!e_wC;5BhqfT<X!}D0za(y$oo!!^5ZbaQFWB<)l-eSMsT5)@g)SG1zUp;NF$H=_Mx_6$7buBHPb=^IJb>)>J(fb@>UA_H?=<dQ(9OuB!lRT~~zdXzOvtb*!{<~jD`7>p#8%su=<~aQZ?q&ZGch9ii;w+DYyGkt?A9ptEO0A1L4&Lys(w;6V>)MzfxIXu@4NACQzx#^+Hm`@{Hm_gG&&xjHc-l-4w?qG7;~6fma*TE3`dqHZyJ{h~U%m4ozo))1L;ClXYjs7sJ1X=r*E6>{>sn|D&x2?5Nv_9eSebRbc)HX-bSRIX=e^@RA8Nr+o@Y<#!Q<TT<qJeV*7j|C`;DMdZnxr_BIEejvNtQz)iz(9<9hmU;AgEtq~zVqW|HscC$nzMdQtML+ox$I73kiMdB?b(o8u*3=6P<9*7^<UXY5Pj-*(?w`#c&={iHp~pQf|l+M6;TdAE7qw9;-Dc^sR!<9_P%cCxNaIx6#<9?Jfn&`g=<iSu}z)pOxnWSxzZJgt_*>r9y#cZ&7!k)r1<=Jt5j&puL8fo^<ztBn2Y1)bpfr>04NAG%jqQh~1JHa*MjO{vbhwltsTS6QB&%;VY9k9Flv%M8Z2%N$32{JO0BoJeWst!%v_-J?eFe&GK4j+g6yd9IB2wSio(QR_p|LyE<}Pwat;bocq;oL726Yu5F55@cQUTvWpTP3|+gn+!kC?H({f*3b0bCH8suEUdelpX-IPuK#w6$KNwdUCHg-c8B*xy<LR(Z(P9pl2-J&?5}-);keq>9y;gwPdjBFO^z>@C+frfrJleH>DTbXdrK<PyS?}puLE@s@6*}`_qqMvI6v86p6toG+IWhLgMYuntj}p9`}*otoNs#n9^7B|u5Y-#%KW0O+@8{pWj`HxmUZ`%FC`C8zAp2;W=1i$XHSv%{n~@a#ak(?*gihWwPEo*u0g)6D_V8gub&wr``QIV^08y8<l8qLGP%A3lBa5~B+1Wz9+mG%|EjFJckh*Ttjap~HZ0-(son?~pJq7+`Mq%EP`UN~_eL^~*DrEj8{<aF_<y{5Gmqb=SNJ_|m6N>RT6ybPG=_Dx=&JPV=k}Zr?o|T{xW4gg&e-SCv(=D%%<3!s`ucvcjOzr^8+|V8VVTPLtlse1&v8bMmj2(xI{t2YKEHRk9?zHe-f)hu{q*ZT)<?7wJ$tt3gFa(jS-YEcPt#7aPkdCyy8G&FuHVxpm+RN#W{Q8tFB12Oe2LqjKI?k@7~YS(+mFh=G~jp6N9FA2k{5yBNM3K~lFR+NabNbe)XR%FzXF%<=J!sI=XMy8I<G_H-D8W{uX4;TuIFM1pBt3O=v1z6zb@-Ets(E*maguImUuanO6|J7V5P*J6y&w*#)ZY@zo(YIrXTBi+rg(wD$un+*E@E9<-IIfH=Cl$?Edb{6QuozUFF)Zgr~~*hx{S?#K1!SPU?l<O239CaQi(cFRddqnkI-}W@G-I7;A^EXG|F;{#QrwcTjn#aGT3Ep2{pa7ihoT*v|fAu8ZC$j_cR%r1QD$&v{8XbcCMWYX|Z<$vKbSX%lw2Z1b*-`HsiI7(SJC_x$^kKT-Q-U&%Vhx-);gxxrbk3i8k$Jb-om>ulaPj3vJO9kFz0K70S@oXznc|CfwUR2rWj^ag`+TotSr@6BfNy~X<SUTJ!X{WAPtXC3QNX`CbHh-r6OcdlO}uSPzhwcg!XtvRpM$Kpg^Jy6zlY8@VDqxNRjo%@D9f6jg`$3CNMpIFHAGGq4vMr&X459a;b^TN1;TtD_PrFcG{$MiY-Shw~)Z{|#ym+MWqK5L&;s@>x8Gp4MNIM`RU*dO_O>K&HLx^o}a>%1@ZBz2c_W?qEsPeHd?xAt>=!P2Are%mHRtYiPzzBnW8|2^ptzwh{77?)mU-T8gdc6}iJj_;Ay`%BiX@0YiAB%e>zK2Pzv()qnJI^E;Ec77j?r~4N3dyem{G9-g_>$~iUY0KlQmu+C(`i?8#f5v&Dhka3O9|tAug0y4%x2*qpKD^h8^Teo8P3}e3d87Aj8K1r*-sJZj=M$y+647za(S5pe-g*a&=JUJrT;wSzX5D$dQd+#px^*7&ykCvy%d_kk(L*wMKh@uTP4>BQzT95txlY^E?zpUj^5;YM(3z}T=TBqPeI7T@+F7zcInJy4sS?(m=UXHBBk^~fhqZz>au0NzpWPk0%X!dw-fk3jqTKl7e6IK0#JcnRuOyC?dyL~A;r)IxpO@8x$=pvPbfbLteDg$i+-p21{=xa>yia*o&y(+x<6dS=J1zT!;~r;(ZsqxR-uv9wj!RxR?upuvHoPA=@0<FOOu4r??x)5(M`ZtS+-E%(B4wVP_u}W$Wj}V@qm4FecwC(KZqJP}xi>iO>Fzo2iGR)+nYUFt<=%SbL&+oOeSbt3o)72m14i9Ca&L3|o?z+D-yhW7DXcqxuh4$W7k|g^8=it8a_+bP9uisZSDwJrS5LTWnpK(Rr_@%)#@K%1A(8$ptoSFM_zwToPdx29xBGv8;^||yVW4TVVZ^5aqrj(uk1?&0X;0Jm!H92x5nm7N1Wwo;d_DLw81YnKAMjLgYD<o3draF6BfcHB$JT~DXjdcfM_|Nj!id)}Egw7&m=E15t7=+-X$SC}4_*~m8N4dEuW7laWt+Aam<di;2b{1LIAL}0z2JWEp?8`AH-i(d18)Z28n_s|HFytT5_k{r0Wji&fm6T<hk#E8w={Zw2}V2??WI0c0zM923H%|93yqHgtO8yIeYO7lZ14J^?tO~P_b%`pJm=uK5WEm`xCcBBR%n~MLd<6YcoBFJ=JNpfepnIagz%tkj)>>Nh-bry?}QP5U6K5!Tx<>_{uqon<tD8sT4RHNeZU8SyJ5t;!#dgYPPY0xAtueuXv`JiP}|%Qr}?D(2~Z^00x(~7V8m;|kNgM2hz|fhr##3d;-QM<7-4H*fbt+G0}wMCW0VOaz8OY*qarysQIR~G3?2)ch(3|uI_1Hdpy$Of;)`G&MRGg|d<x8ix+tG$AK3-e!3np3?*iWhTn|pT415##5@0Gg;cRfiY2Zu1rz)~9(Z1sYtO`!(3+@9>f0Q@X6v?BS;FeYszLd|D$CZIq!2Q7Y0{4TzVA_kOJr9foCme2CIIurB`DiHDP)0n^w7;6x1=tasupR1bhj`D!=Sh@5iL#D}(;Kk}UEu9ep9?$?&*ak;dRLUWY<&m=hJ#ye3Ije59*+0IfL*}nn>NX`6kswq;ds;L0;hwMPYlXqP)2-%X@4_qCGZt+!ZoOK4dSK1XB*15q3jjJnTJ?}OTky8zNO$B@Jv4G(9==2)YgZEz`5X7n-&67z~|z<g}{~I&zjcMv=CqmaKgWs76fbpPCou9_eUA=zNQT`ttT)7oUkA2?1y+E@QFrwG|D0nrww8eb_OTxg*tm7UQhURMR`}0b++{(7#IX@wJ8`F0&c|!2KEG}`Jx<10FDJG9AR1<a3nbS#GpI|WyEKiw!pMR;4JW2nBxTCbnpe3?^(ck;1p*RViAr5C!ByfCm>!Te4<evjk0mJKEwm#z^yjL0~5fl81cYF@JCI1*tB}U+TeswnAQ;Z6gc_#qud{5#Gf&(m1!!l0XSh@)L9qt>cOWm${VAs0phepEW(!HgdI?42gFn1(+%a_P}b7chx)*V;8vUJ1M7iXG3o<V@U5n;H7x`9GWg4w<22w*aPmn<c{<97FE{Nq(^ddq1t;8rI(Hym27Izmo`tek5oZEo5zYZ8oPj!LAl?f2M58<!WpiwOSOrW2x7xG{m;r9ZSOr`G9vR_NskZNb`WO3yKM#Ez%l*UM`DXcRoBhpC%)0)(#6?C_q3^SKV6DU-@)*h<<=@@)S4s'

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
