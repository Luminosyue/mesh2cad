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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/25a32b2b119948c3b905a21db1098f45/part_000.stl', 'relative_path': '25a32b2b119948c3b905a21db1098f45/part_000.stl', 'source_sha256': 'd92fca43418ddbfa170db173e7106803b7db44aa79476047956d96a3b26db163', 'input_faces': 384, 'input_vertices': 296, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.0721183642745018, -0.4735710024833679, 0.36047542095184326], [0.3106309473514557, 0.029613278806209564, 0.3914448022842407]]}
GEOMETRY_BASE85 = 'c$}r033L=i9>yyPh(NePI3$4#2qb70l}kX_8392JM-Y@l(aGk}0D>fv01+5KFc=j~h%o{>cr7cqg51b4EU@v4KoAWXBaszl5fBh0uB>cV)mKILe`@#b+s%9b_kH!NFWuGERXsg~<fMo?(M<ldXXi_Q80(2;j8`O!W;y9uPiCg3XLp_Q#LO_(RB-;Iv}pMK!;;5^u^g5cpO&7Tnib#I72hwTcYLBNK4WUulUXTK9+{ezmd^R$l*!rY7SDbx<%x8wozSgMuS8e(E{U$$uK)3;fi(p0xSaRhmby|`jpXX97xksvz`co0E4kL}D;1o*y)tXJEl)Yk``+o9=QiXO*ZF#NHgNUC4|>{he8Oqo*JWwG+mKgW=bLwv{M(oUd)_~0#RmKJ`Zw+}a&??Q$$G)PWe>byA1CEBUz0ZSMYkcZxXOEa?~vnsYUAU(ZR4Sw=2`EoT(=>wxX$m7-YCwWvd!l>KH)Ua(&{dB8}f?ld471g;Qp$YiyZfnaGDPUcNM!0dByd3uD&I>Yp8p%WBi2EymxrP^KL_4ag}$CpS(%5&x~GbKR)F&?>jrI&~3;ouJZmJn*|U2>@Km-59KuPx|Ck(Hslr8^SNf+W}#!J6xqj5InA^2%ZlBGyy7bFYx;}eo?btf+Q&~h&HH=Au5cUjitGC|q2Ct4KiPJ#WBmOe65N~heYRtsGbakp?%Ytk`#*4fzreljqa~)}D6Z#!=rO@-s!C?qkI(kqx>ek-I>ied>uUQL!F>Z>TW+5p%Jubv*Le1?bQ|)D>-juiBsiPiqQpKP%4yz}b4RJ$kXKw^@2Mu+M1Q+;^X<p?4xA@Bo~!!4wE0kQ@43Vkj{Q!!UT@(3%gY?&r<~>kwcATg=T)5Medq6c)omD$;wtYwvS7QI@A8TTj`h>^lHlIy?>^%=@7CJwrunB_j|ZI2KjkXV&h_}fw0<b3dAfcm*Y|hy=Yj{4-<$0i|D7FnnD!Cn`ntgBKB8QI4u0B6@<H|I+4KHaiUg<66Uz1Y!Rhmaay`zf)$%xtkES`+^KJVD_kH$8reptJ?Y2|=9(jIJe(m!`a{BzFT#x_k5y3;A|Af<g$n&3Yy`Ga@yM&U@FUo12etuD|*W23f1gD?Bl+!%@{H0uvXXtss>H7oaG*90jDA)JvMDA|E>H81iG#~Q*L%7ao9TYs|{f%&%4|#thT<@c(px`0zpM=wV$onVZdcBQ0CwR#FFyVUqBL@Y9lJ|DXX`a5fQ?B=K)=a@ezIPB#^C90m2-o?9f`I+Hbe?d%p4U$}D0uD4uf+Y0bs4#DN~5FV_i`Q)+&A+>N1k$;ugS?a<`q}@nt}|$S?ddqJmoa+t-QyWS6t;iiPI$C98+!2Q%>`NKCZ7!dByehj+ra@l7WunQ%>`KZ*9<&S6t<N6@~J?ESl&zKIJs;nRqB@$}6s~cT<t^zWZkt%Y2u;M$XD+IPc5HugLuPlSW=sJjyw5`ESbkSshtz;{GAGIFEB_wOntXzu=e$%4t3j^KQ_TS6t--2iHp;Z0KA+d-llj^gQLvFWM`wYt}l)cqpfN-}Hi@DX+N7yW+l(=N<jAlfV9r9Or`v9p|N-=6%a11x<Oy_4Rf-BkymYwa)8J4?iTXYyD~G^%73=-rtW1n(~UPJlkAPaNqu=&hbQcl)P20gZmG45}bLj``Uhd%4y!Sv}e$iS6r{d1_R}Bu2fZ<xaXqRIiBz&!TtUi=XeOG`M?NQ(3DqP&*!={dEVT!)h1puW0*4^%o5zyr>kQ;l!xTEGzuE?;Cdcn^W``n{jJ)>z4`r}`B^LEankxZ#zQ&Hv*)f>nevM3{XTK6TqorXoX7dPOwNCuA<pv>PV<2uE>@ZHitGD0r$S!u>gJB)xCZ<r`R&6T=cSzHYqp-PGUXN5<1DO|*IV1#c^~uRDuiAc?!51W(>&YN#>l-tovtz+M{&JR=MJtgjmLK&slqf5l+!$&2g>!l6-}-%&A+#MZiVr_6HfCX_nmOP-rg>(Fs--1##I%jbxt|W({)a{p65%OD@^;&GwPEH(|)HsBv1A`<@))YQYAQj{<xZ4l=DfRdz8~WeeO}N_gBYX<vft*u*-A9VZq7spK_X~&wtAGdF#dq9;n>seBM5IyWswt)(GysZF{AO>-?I2f`@!=5>E3WpPPj1{c?Jw9RHRjj`2{g^HV3t>mu(Dl+!$Yf1q5?b3vZGF7p1PIDP-2T<@=#m*jZp`y1i<`0lmxddYh)<$9jK+$HZ9c@L*t&%=pwIsfE)1m!eOzeiB6$Fs0fu3Pdwh;o{z--9UE&$s2r<UG^wafH)+$oDwH^?vbwBRKtDNx8@;JO27OV2G!#FUsn&sy>Tm87a0uJ#xr@l$!tanAzjM`qN|g-aY=`KRq@JV=U6D#?b5FueYj>RbkMpO!_eRD@^J?;IF`6hF*fd41WQ74*mlC8R!r2XW&mlzk@#se;oQZ_~Y=^&>HwktAbV?hJFEm7`_~O5WXC~4EiyA8T=mTKKPfdT5Z)b=-cqi;Fm(*gnz-RH>@gzz6D<h{}S|%@UK|)C#znC{u%yN_}8KD!M|(OMyocUwpq0mY@3bk0^bV16S^CIC;VRMe)x~9`oyXO&_nQbv1S@VBjNvU^?hsADd-9KvrP8=2t5V=6Z$Sfe}u0^-!IUM@c%^LZ_r=h!^31>1oSuf`eCxK0W<=h^QKlcfp1`IbB%&FhmV4fhPHr@hHnXN1>X|BHS`8}u5GP~MRD(fwug7YcZ7C=?+D)+8V}zYz610|_;yysS=9y_1K-HD*O^uIu)phpasMlmeOI7i@IN!zcNuyG{yh3FKrh3eM&B9e1^DmLcM^IA{u}fihn|H03Vqek<M3aiuM(=B0Tt*w46TI!6n*8;!|;DaUm3I<K7hVG&@%Y#==%V=2YwU!HbXyv-vnI;T@Sww{vGHV_;=u6gZklLgI^9^0nfF>=3hp;1ilEm4890{33Ms^68PuYwddFKDDGc`7Q(*>UkrT-z8JogU3;#TLiw|7C5ro1(AVKt!LMc4o^fkY+`kXq0KdbkElfVcxNe323;Om#cfx;&zK@{lIrka*4nRMG{~Ucspa<ZOqOS^i1paIE9fMZEe~Z2o&|~oPteS6C9`q^rR#vsPsyQ?oJ`b5(=nVMg$TWmT!sjA075W5xLu8skqu{3^GYL8wz8Nwtpe^AiA(IMCgKvRMTWCA@RAk0N$HBKnraiO+{8(g0K$GFyBhv+X6Z{BdhCuIz?}AKsXb<=y$he^%`0mK`hyETu)2fM9Jr11$-yfN~po8IiTGh*{o1uyDkK=czLv!G#!_S1yg1^zKj#kA%UGOuJnFpN@e?P|h2r3iz){8dx<I$dq`#2tcD)Ri;d1!N=3!jH`<bh}6dS*hW!}B%V9OI0GZ;SbjgTE2}W>g&dQ=vm~PZb*qKLEvjZ`?;Wvc2KEq1-rEPn?6dZ$lsFx1-JdooI8Pf;RU_@F|$vB=}6Ux$h6<`3K;Kp;Z4}Xmj5M%JbcAtUZ+TvACvG+#fXulWeRl=9cf#7HBsEYY3mu<ob9Tngjo&RgYQaLvcSEdEVyFm}lYh(dK>zihK2(@ZonC!9R;WANrpI%g1>hMt;8S*t6g{d&sH`tM0RE5VS8e1HLn~F^YS&U%4NQc3*aFUvfVjngM?kexGMMz;o6Pp0k$loJGNNRu`VLNVK_+hUcs`JZCO=&N{+##-9xdU<u&dH-+ac7H#fth4w=wU_L$Yz0gho>jlrxb1!~}_oqR}p}0>*aep^T9lJip!^gp2BO}m`z&vnY4?Y6(%jbCviu*sHxSxpPp0CL%Xmg)~HuqUp&4JHAoBK9Qt^<C)fmV%Va=mc9&*mRQo9jdHahUs7(AMxgla5?E&Zqn|w5MSV+|S0?ra`md7hsIDp>yD$VRD@>fIbahz~nx82AU7Qn903U0DTUAA(Q)UG4xsZxlHc6h0sOt*-Y;FxlkWG=Z}JMeaz-3pw0DRn;(TX*U>hA587PswfQ^H=GxEZZ$X>utu`NzHrE83k3pMjEPN9t*JBJc7QQ~(*F&4Yb8P@$hsia2J+wYN{|Q5X82Y#mXL4OLXc+u;Os@NIXaqdxjlj4zhQEQywc7~V7@qS^U|c)f{O{1_+STU!pv|?f%@0JI>mc~#q_FVlh=2EA=db<v#D&@aBR&01=RbSde{+s?Ed7sQ$w_tj99WYPE;dCUes|fw0F^$}Sp'

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
