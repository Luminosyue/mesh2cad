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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/98c26e7d386c466e982ec81e89d42b06/part_007.stl', 'relative_path': '98c26e7d386c466e982ec81e89d42b06/part_007.stl', 'source_sha256': '31378ebdc1418db0516bc0e3eea90a903a65f1f9af163707f0f40a15ae58c7ea', 'input_faces': 230, 'input_vertices': 150, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17929893732070923, -0.11815166473388672, -0.46452510356903076], [0.05912214145064354, -0.03815104067325592, 0.2028745859861374]]}
GEOMETRY_BASE85 = 'c$}q~3s6+o8OJXV35rpYfD#pRMJ=d+5+4zwxGMM}5F|b!#zk3$R1`r`@xfI=0gcj-Owx3wuEwdY@h!1x4Q`_N#<AMwF~(+%?X;=Qm{=$2)M?stzVClFcMqGHPP;ST{Qvj2-~G<>p37=(R!C@+!Jj_H><KGs8oL;VjLt@sQRymQRx;mJk-WHURge)$Tz-@`<xJ1cogHLU8mr@rTov=n<I~LeQ42=KCz|mKmXt3mFI+r#NqLb=@(G2DDqMnB6c?7c#C1Z-@F9uj&;g0&TJwMWbP`>#GX8$<wCu}}F)dQ9hMu=h+qlQsow%oDgdaEl7JihjFGqiB=T`QKBcz805qGcus#U6ERpBY(q4l@y+=}??Z%EId^yB80)hFq`d87Qecj<!@)PCPGKklAwQGXnJg938T!xrvmOAFWe><;s!g|`B6W6^xSe5+v=^ZfC*0&z#vc*^(O{6)a=Dz1-Laecgs>*G~iAFs~Uc-@_=TLZ0^;_cQ8+%ahAVbVV*-L!L0!J7ScZjCGmSVwWk$vMQGm%qI@#>P$Ohlc}k_l{l650qZ8bG<)`dlQ&jOHaMym!H`)aGkS94^jKB5$EjO`0YD~0@XLKF*k1Pyk_T~)(;NQ_p4uMwb%Kf`7v@Gdjr+6a+o{g{`G+$e-8QDxQwxH?51{(%<`ZAG2rhX^s8_5@xC1}|0!_fJNG|48)zOBSM%W9aK}F%{n7JPe=OviZMV73#e-DG+jf}dUvZ<um;31Z)cRICw|3<J(moH~;A70|>!|-$)$aFB+j$*xM@H-(;^p~VKb`xd=Gl4g!5Mo$ee2SabtX`KA4h$|)yU(E8$k7p)b+peTSvvUcC9nN^HBe^^FeX_d{A6J9~9Tm2gUXCLFc~n!F!79Xy>8M)p@A6eje&vorm7woy3i2cz(WLN9Owax?{HloFB#8y)VGqy)VGqy)VGqy)QJb=EwQ$by|P@98+9B#}wDkF<%|+98+9B$9(zPIp%9udyW*>pCcdF=3jAr{yjU_alUpAD6XFaI#<t;;#L~k)wls}{poU>AJ@(kUmfi{(RsW2Dqqzvxp~T7U!8}F>*uF0Upqg2`P%vEX!;B9%P;VrRrCDr72^8)*T?TN_nkl2n~9r8KWwIbbgGcwUpoKjOWJSdFc<SjcOAFy6UU6n#2vk>o9+8karbxUj|R$j@5nf6-&c<N7f%MP5ALn5_%-os2YDX`^`iHp_sTr3Q+<Q>q5J+helOPkfw(!Uh4<&-eB$1I!JPli=bWFHLHpQvq7Uak`5AFXWf*bK#u%Ol>lpLBHN4NlzUJ{Ry>(u4Z+#ANvwz{clz;vhanIM`#68)|xlZ~y;?6nG)AQhXwUqh1I^xzpOyZs`)2WX4cp=xx8|<d`7PN8wn1Ty-uG;nPs3mTiF~p7Sx4FK%n7HAJ^siI)&+~TfNV`h;-tfL$r|98&x_<MIoNq;QyPMx*o*zow40jOsUL8x^*c@_<@)Iikxcgvt?&qP6e9qhtVV?O0ap(I#C+@ym&_MkvZsK;6F7P~mQbpWz=K=S#`99BE^Ks6Pe8Bm?PvCy;`iQvdr+dx_?oZ=4%)i>m{VAQwd|%5?sb9m_@VIJra=ZPm61Q%A!s{M!h1<P1@Ga6QUl2E&yYjqUDkkp!_s3jkw84DbO3wEd^LWn=<nfN&`Zl%u?a#PQ+g;k{-rGl*e>{lC>x$y_YRlYB<7*nq`9(RrPj0?N-0^ubkJn7){$D&n+}*f`^DoV1KIhUtsz0TH-aF>r{b%WVow1+tv%3-Z7F{RqdHkdwckc=1ze_*uc7Vn=@jI?lbdU1AV>1uf>$`hLwT{X4`!!qDKdE$5gki|&D1OZ@D75{Ql~8_^2L35qGVH(lDf{%$|NE!xD$$235z7(MS0bceBVrxYf>yy>@av(g;Mc=fBcxvmt$<$%zf8mu=wfIE{9^br=yLcn_@&TF_@(gW2<cZq*TAoUUu_%PYUo<{Z6fMLG$N$mB4QJ?7FrKq3%?N|eI0Zgd>#BNB3^|yLASv-!M_e|gnu3WHH7rrp<Cd$!#CLa+JKP025V7+^{D|@>$M5%xe4P@>syPtsm0jVAvR*Z*1~Uq*1>Op-wb^Pelz@5+gxmg{sg|Oh{r^9K}a77eH=a#{s|G`@Q*+rgMS3R1GFoASJdqQ4TYCA!@$D8yP%DZ_`V~)i^M&lXeSh0wHt<hh2frXL`U?oBkD>&Lc}v7o`w#EpD1FohzSVkCqbvcPlC@9@vMk65u>4_;77x!BcvY#o{oCys52RLMx*`FU=z`YNvJ&ub(GJ-brx!?HnLDV3-!}cCk-{z(4O><iWqOme*$D32QSqD-x<CW^5t~|v=e+M<U}AR0`<njkA*tm$3w?K9q=!Sm?I(;IvhR~ewc`vA`(T+LP*~SA-xG51TX8%#{I+L`$1>H_k));o)eKR;z@+`J)l$Jd%*XG=D|xH3_n0byoiC&1e=%N&4m`i%l;;bm;o(-p8-D;`Xc;H_(W(j{9M#@Lg&E`gdYGcgm>aP0Xh&q5j6)vli)K&Oc#*>od!P}bDa-;2|gcwBs3L16}3h}GvEhf9*00*fbS(jzVe@k7QxFk>WOuengicgM0bPtKrd)FXm@z2(eTlz+YR@|;QJVSCw+*BAQ8b(13m`V(a;cEy=de_g9l@bPZ_*V<U9<s&1<G@%u-XJneds&PeBb?D-JpYJ`Vmz&=mL{XjAR&-k7uAsMQl8eJnH%J`OcvZFAZO8VlbK+8-JVAB%hYLsQ^WFqZy^VW=T>IK0!~{g@1mhfju2g3g6cf-itN;S1njgeJrH#dzcz%6+rY;AcG>z69~IjY~fjA$=b7$MDm!X49Z~@Oj9YhLFA#`Z9be{32)x{37^b=t6k;49I687wUqSIv>6l@?xR6@I9e9&|LUj+?xYk0G|Ud=P5TUC^#zQhyF|H`;SEriv2&B^gI3ke7E0uRn+qRF`t{&LB89?0~AbucutkO+4v8Aa3)C'

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
