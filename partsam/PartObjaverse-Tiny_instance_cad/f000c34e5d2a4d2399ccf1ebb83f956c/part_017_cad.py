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

PART_NAME = 'part_017'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f000c34e5d2a4d2399ccf1ebb83f956c/part_017.stl', 'relative_path': 'f000c34e5d2a4d2399ccf1ebb83f956c/part_017.stl', 'source_sha256': 'a532551b625b02dbb8f56bc05a71e101fb266b7cfb632bbd87ab7e3940422e1c', 'input_faces': 382, 'input_vertices': 314, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10314583033323288, -0.22223801910877228, -0.26444923877716064], [0.09078419953584671, 0.04135316610336304, 0.47271066904067993]]}
GEOMETRY_BASE85 = 'c$}r1349IL9>*s%BuYdYs<qt^O+&<55=(PQrPR{Apla<^BB8BBEVUHZuBd245}MW(MA{HZ5V2-RA}T1)S_!VD)T3xo&r`g!{LYv;nfLj;&wJ_T|M`9Icg{U?X6DSyy>lzPSLK(y75?X=Was}Lb+3V<(5kL@E0ZJRCXN{yIU#Ud>{J)UlX?0laz)<(eZmL1D3g`xexo8MjEwW^Xz}YjI>;};;x{@bZerYsaUaFRjf$i`Y{aJ%B8i_6Jt8)eyneH7>vjQ_w*CQ@8J7R?uNoPGvoLB`0ZCgzR549Q`Pt$SomY-DFVuVcpKhk!8v6TAeLvRB$3=Q?g|{bcJE-^e1A&ER?VY8(f4RLnyY60^7OA}*-iG$hNeQO?3orLCyxhOmkJP{NNk+b5dqV~k>AkkSa|f2_z1F|fUh5z2tugg>FyAZg2<z|BqaO=Qye&J%;8oWHrDpAg7wwhjck&F!eQsSo9(XZ+wJ@PX@5T7-QhPCe2iiN{?a2G@xVMP;ImyQgblwrnz2#J`9DRE`ykpw&?S_8folSfS_1>}6)wF--67H=FI%n(KtMHb7cej~&_4JC}hW>>wPdUKm|E@ZGocB_)+44;r&HZT`8>f=qa=Ym~fv+%6;491%czK>!-hO2pYZs^T<288a1v78ATrzm|htE{A_QH$y>e1_4&CYA#<?~v2`8*Q7!g+Mr$-L6$mt@x8%%>L&-g<EbYyWW;yUwVg6Aa@K*B{}v`6+y=8~47q_<X3;`GnqE;nl@IT+n;_tqj$yy#lYbZyKM=e8Pk@!#IVH=U(hj=dy9R`t#Rby6$j+&THpymkj2WB`0#&eq33|$FswJCPe3*iQKE*Pn7AslB}}zDpGqT3BL4rIrY|@V(u+bOWEsd){6$etHXEfHMYxMH8aQTyl_7DG>)gXv&_s}tHzY;y*8frubO(*8PE2ct?lz{{r(ZxF?GNP%qxkf64*E^d9v|q{;+=%dmZF)-r%E8CA0k!So560|I0s3zrB_QsawqEkMQz55ni4r_SB|Z^vB&XbQIeT;l*~T5m9{mVy<Pe*XtG(uy*n8Z2wg7A@dDhS-(G>jb}}i(XZoP&6vv1_d`>&%;uHdr)HMf{IPBPWwY6Qwmmp%@JefM-hZucGR@8lTaO_d*!GM0zvuSx0-e|HYo%9?>b(>DM{cjp2dTaA_N4<#P1|GsXyaM`2Rq-?>jw@S#shEZ5p8ULGL2n-oKkz?t!S^_9lzFW{KCuQm%U@ohoyQik5lu~cr2-%*P88Tb%+b|cK<4--U@H=dv;jw)!<HS9F`@~2Cr=|y!GRr3s}1g+YYkr8sDD3?{UC<w!SO=C1&0k(bdr2w*TyG)}P0U5;L#(oh#OR=SH8YEM2abn0Z^<`G)rPr=jCmKW_(Y(4X&i|AEnLz2{#$WM~g>zuDW+kFqBtl)g`?-{O#&S2qS5+S^KMj}I~FUwFBHyS3BI5R>f^UfwQiNc>zjo_puMW$SOjuWw{R%?mNvUiEx$=H>k?yu6?7UTF(MOpc@Q@^MrH&MXQsn-AyLI9UH~sr-1lG~w5iqknL}$ZHOJ|G^&o^T76$wIL?+R(Kn{IFE#v=d<wgd=_4w&uYCx+)L+?_2Eh8m3MN!X79&!PxIBkWaGE{Mj5@b#KP9!tv&a19x*RpAB2~$53(262jS)GgXZPyL(O{ZKBpwCV&fO%(Y(^56Wgxjf&6nz(nanw?k_j>wv-Q9KMy8xA0E1n`BOLearB(c?}JMkuIJ~=tayEU&4+gz!{^OX?)x=h^Hu2`kiynm+ui8z1<qyrtxAf~Pl=tz_S5jLd_Nxz;~t+gl`+kX-gDaL?ESGLc|Yo^4Q9t(c=<jhynGymmye_D#c{0A9``A2Jks&i#v|RQwD!_*m%X@8Icz)lei*eXiS-{C&h~@mTX`*I9-qfFADujr^*e5j(I1bEW!o`y2A>ZeG3m_j>YvE^Svt<>ol6F??TAR^$HjB#M&?t)`23u*$mks<!`ONouj8M?FC~7@{Jg}~?D&pwHTt}_xZnPU(Whszd8JP4ZS)^JU&;Kru|}UiErI!>c}8D-GM|TM(v4nO7-s5^zdj~JH*Yl`n>2;J#`&Uo&*65~9@i7iXSmH_uf4kCbLPoRv;C%dX}>wYRX3R)7vZJjV(C3)v)Me+yfjZVFU=FpOY_8W>DSF>=c(qU^VB-XD~oyQ`k;B~`k;B~`e65Xbqn+IbxC;Xx}>^{WnNqd#OHS5weuRE^M%(wZ{JPg-^=dC@czfP$T#&hp0MXP;`6z+Y!dg<=X2F<2VbxBeW8NK_XXkQ?+cojzAq?4Z*wnQ&#kwrvF9rlKIdPq!M*rifb-FE>=lF8z85Dp<zBwO2ru1V)S1(nukgJdzQXr+c=>yov+rVz-*_L?ymTK_%QkZ_-S;&w-S;&w-S_Qj1>8&DLp3jb4^_QxXPeC*+1nR=aaQlGzxB&EYp-<d%%3~1U&!0XG-S`=<j-B!(LOo)`7G{7&YSP@_R{A!C3_I__65HA`gtq7a>1SZzG-I-UVdI7d27QQ*4`O5Er-twJZG43qs+`}&l%vg=M10RG4<N@>e>xsKYMzX>Ag0d0WDcS%Co>+meTVR%}dWuoM$`cn)NSx@jOR(dA*t!+coPH_xqPKuRS-$b0p!l@5OlT<cNNfYj*x>UOG?JE52J<P8!0_JKHedBE5IOJ6zLC^xl$t?Ev%r{0!|Ccstr#diFQ%UwFBH;pP5?m;1K`4C6j@7wgA9{eGd|JG*gjo%NHUy;`z$4;zov-VSd;d!>oZ(7*FpV6mB3{#tQR??wNr)LwY!6W-pD`lYcSFYh8VFV<V3{a?m@#P%wqvP<+{TW>96|MEC1w3o&y_K$NU?_a5r$J<NSZQ<qTvBJyObKxsIk8SZDd#*1(Pu9HrJbCdK%*)TuWv|VDc=`Fc>_vMeyp;WpA^%=b!Q=M=XZaoG<=;(&mwz`AUjE%g>qq+CMC(WT-9&i#cN5{|-%YfB<ljeH`R19OU$PhTR(N?H%3hq0!prBQ?8UqlUY>`t7w4}ft;-JPrQh9TFYbfFYoGV#-#7KFeYoM*;=Y5oL_~X$PXMIc6>nwq2;EP`RMJ0@=06pWY4_j#R2<ai|NW`B4H-jQQZ0}z!7ac|k$&K&;5x{<;5uLrq$ilB8<=Jlum|`hR2A$#nl50PuF8u)%9T-+YapwFY1RbS0M|yo3a$<IMZN*{1qUDl!2#els6gze4y4+XdJEYO+?P}zEboJ59k85oZ)6{E1G16zNYzKa4!(qC7m@YBbom8^zovN+Tn+oKI?@g7g4dOh)xa-ff4L)F!S3KnNEh%ZQbS2aB8Pz^!K0DG!K1-ZNE<i`9F3y<F{yQ=){<I|Tnb(eUWlSR7C8ny7CZ_$7(5tbrM#Y08rGABb*#hk!5BNuA>i*x{Xl9XG6PIA9ZYircqF!C1kwf`0saU%92`t`YzI<7$oAk@$g*0bypdkuAhda|@O-9lrbYP}@+kNics()={3EF&q>7OH!A0N#<SuXlcqcL&yc3*@{05v0-c0IS<SOJh;8oydD9S0wY;X!V3%LuN1>TL^58e$fMjindgUeBr&mw;Wp9L49DCZ-Kz(v>>`N*B%o!I7l<Yutg{(KbWO(@E%k*mO~!O6&F;5EpV$YtP_;04GO@B(lWG7Fppb|80y9pF94V(=bt39=kq0=`V@7V;{x99)ildKE>v6j=x^1@A-VgZF`VpeW}cH-U4&Tac^4TfmvfWU$zenJCKJNF73MMXmvF1*alcf>Xg?As2wZ0?$V#f#-wckq&S?_&ekt@OR+7$P(~g@L}X-@L}*Z-SN1FqWl}FD@Z5u7T5_cLtX`6#jz<vQC5-r!257)R21brWDYn7$0H9#c{?%_oQeIu9Yy(|?${heUIAahxDTQzA3&CY%P^(`$UJZ!)<HQ4*HL;64hG*=cpd}a2B)JaZ$PdG(`z-oHg`h43+@CCM}7pRIUG!L7`PVt>WJ(F?g)M#84i9QJOnumOz)?kDf}Kw^Hb%;J(u!m<R{=nQY%O;K`z#D0$$Vn5=`&Ei<B4lWy)Wp7NPATw5Lq}Z^+k3HAKD+ZU}CKtOsrcwxB5cAnSvhk>k~z)Eg+ue#ii@ANWmV3ouQ8a1~N+q^cs_!R~nNihK!N1<NZTD}!I9_iR$0NDpuwQeIf@g=Li6l4^<NEwPMp8&ZK-9*AX>tJBYRSY8dw+F%_XSnh#kl<ShJMamml6Z{&M)kb=Q+hJKNWNq+USk@ZZ3S0xrUPiVC*TS-z$d|z}<d}^kH6BHI0*dlv6y+%>%F|Gkzd%v8qbScoQJ#m41<wP|MNyuOqC5jdc{+;nR21dUkrTmj;8@IOI=|^0Y=C)5xiR4;q<md?Hg)0bi}}|L%V^TJ-7v2y)4568*T?&sh<Q)vEj=fYZ-Sf9d5`5Z{lSe%HB<O<n$5xVJ@mbek<Gw#nRuTM+BL?ynqz&<(Vp^YQvFDsME(ujnbg~)1|UBGKO}XZ)C1%n;1IOyg6s?qBh{VMJIGM*1HAVs@(H**`U*vM0sl_wE~$ISJK$5KA~2Q+^iBB;mOVt?2lvOaFyupU1eU#n3<ICUJ~@Sq0G~vjMxN2_%hTxNG<<)&w;$f$4=w`RaRS>y^Y7rN*e8D>{{{Y&)FZrp1V{NFq<$rJ6L|wn^CvLP<KW|1-%aEl@LlwE2YC~Gjuia@`7?<iQiDhZBR>QOg9oB0pGW=-{u%w8N4kKolbT8D7gDpp*U^TqyAg5_co4=xnPzJ+Ey|DKx`H2rucNwRJ+r`*kiEbSF}6lX1>6e#1|x&OR=mFzvNiah=<6}E5x5uHy@#UQ6GgcP(h9zgeM8?H-pi$ucjf=|Pa0nQ+3C0q|G+_hr}6QY{+)s3#;!f=3h(90p6OH~|IrKo3A$y<zX1jAFj)'

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
