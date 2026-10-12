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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5f1e1e7148424a6bae25b5138ba0088e/part_017.stl', 'relative_path': '5f1e1e7148424a6bae25b5138ba0088e/part_017.stl', 'source_sha256': 'd2cdc41675d7cb2266ef663379ace5490d7356d9df4628d66c9a0d0ec559b810', 'input_faces': 198, 'input_vertices': 166, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.27233976125717163, -0.13626991212368011, 0.18736961483955383], [-0.17763561010360718, -0.048400700092315674, 0.24739784002304077]]}
GEOMETRY_BASE85 = 'c$}qK3v^Cb7CuR66R&!v)FT%eDN<#SqKqq1G?7S3h*$DQBt(#iNTq`7RpU`wv=k$ksZQ%v(t6Y@myVH#cumpLayt)G2E#HerF72O`@7~|tFzXunSZTs?eG8YKKt&o&pzkg{E3eVs8V0>r@4r1oOZZ&Z6OqDi25QwJvT2iEq!vki8%#+qBiO3<JjeKiLvoR{Y1W)7B)J4a$0U!H!ZAtMwhT~Ei5BDH!nAJVoG-I=yav`NgY2qUFws^rskx}@6UILhzQp@whq^(Yyab?noPk8n0Ts0TH}kRpOU?`w7jRZ`VSLG*XO0~AzN>1h0^VRvThZRCVzWfQW^O>dY5{|<R4XdT<KON;zW+wLDw&Ds#LmhgmrU7-gb&J-KP8cplhXdJ|{hAE!|h_W!+BRx|6P(mrCirdvM?UmAmOaDH|vsa~tcvf<Veg)QX}w=0}L5-JyKUq|2QDD&%=3=@Y6$?X#4py%Ku$WfaHWbcOP?mgByc=a9d?b{ECh7GhpK4)A<?)T25W`K%iY>}_;?z|CV6=XN)a6JCYuw)eqN%I7Nd&Lb(l$hT>}<~i2I{i7d|zwbQ75zzJQ1s~IW>~zY<`T+XuvduJZadpby{_5^Yia-A}-PgL;nd6*dT_2Xf{os%Km$2^Zah?02Uv9ZaPaL|-tsARY*CIC1x|kP7u>XoD;;(5$_3<tC=A&<%$@PDeb+PbwoM+($uG?JJ%_40t`JdfU?$))+mOI_LK7n;(Y~#;JKlUv5!=>Pp?sc(B{z38e3#>bRZl-geo2OZ~lM85G#+gI3F7{^DoqjfYb3Yp!5eI!D#_p#3>ZTKi`&o?PezuoDM}O)e+@IzQ)}8*;&z+(AXjA*0aMxdq<N8~JSa<4aG~o5sUSZv-zaFxN`?f9X&UzVQB*oEMc>Rq7yk16KZ+!hIua_BsI8OcVas9=YeNTAme}n6<?O@$mU-NzLXMJmL_Q$y-?&Dlq!n$+L*fD(0m>I15+7xhqR^35$GlJod^T8U!=Yt4<Kh6gun9m36Ow<YYe)oOK`(58X=C~)%2<}6@Q^;}m{?!ig{?(d8$NseodH-q;n;m!WQ|odZ<!?V=-PzY-4A;TF@AcRI#{1fM4?6a>wT$<*cI!x`C(n*wah%W+k8ZSQ-IsN+(!GvW8uy8vwcq2fcSSyfwveuu9%X%6GWXTsT@~b?5qW^-oA@KwAqx7vl_iu<o$sg)B7}A0e9uE<rw!mbG-ch6o<zF!fbVNI@%oFx41OM^?j+s%e!E52TW}rpHfzc_{{{Og&%^$_?hjX!u6Iize``}s?%TVpTf=*kE+Wp6?ki$lyf~2Zw}RtNQ2mEPkJv-H{;-6fU(ofp+fW?s<}}VT68`rps6M`_GbkS|Jc0dx8clgxrICC-w`AQoJM<vwTPi4yuQ}^h{S_3)xOkACvwp0bA7<_2ee@@aZ(oh)`_9`;akTq>G%xWv>sJ1E6vzB?H}0zq(6`Pee?4IxKd+m|mbus0_$&9hQ42cOS6`1lzuLddy<U2CUSItR>(2Tbi}3vV-s^8w$NCnr{&;=&ZKC>%7reSwT#ftxaAhgwQ$3IBDc<0IHi}udy4<1qSaWdhE%oYJi|6<}S;D&Wyfexs@p(Se8{ckgaR216?mUmI5yj<h-8l~(U2BH>1{QIDKEnRGdW_>&Y0Y`Y@;T|~&iVORuO&*|eXAF8-`aow>8QK^jR5X{>mch+|BGui$lsa_fAq5%WpVz{oqjeV3b{{G;qUB=A+fYB+HmOTbL$}Yx$o?*qwan){>c4imq16qX}!4L^xmvH`$9Yu#dYh>y0b6z+q^IAu84zuA<sKLPa3iA><jx6?+ZPEb!T4~x<A(~`Q#tSZ@~dx$Fv|m--fVmEty5{rFwQU_fI7BAzR4b&OgZgAXwKUr<1=JH<I`7{S%~{r(!sce-`I|mvv)zDCMbtc7^-l7VAD^4#hXV{)Eq^zpyR_HsSZ5m8*GOzF}Q^`4Po8-`&jbIp<lo*Iyui^Ts$nSIgmF`Yp$~*pJVLGU(T;aX!8KbA5Io|FnIa&(Nojx%J0+Lf5y#|4Jt1W35W$JU>MI33s?|!TdaRbi2=Ok8ZAeqCO3-@$+j9;tZR``G2{M-;3rW&XGX&Z<@yW%tf3VKTtl#-L1Tid93S+=O~W&x-ZA^!N0tibgjjY{QfrFJ70a!Q=ESs*2USsuYb$uTevsAFM2%p)t%#>ez23cAGEcVo;rx%a~;Gxm7e+fW^q5*@s*x@e12Sitx<({zA@Xl-vTSV^KHlLZdv6XT`%H1?Nx_8x^X>=-@`{A_T*_b_=eY|(P3|W268^)+96Lq`c1CCec_NNzIB@GZ>~AOdfi^Uk7ndmxOJaVb(dQgNzm~gD7HuQzUvSD#wE@Ne>d5!SU1id;`RM0oAZ3MpXU{p!}S?ggXeY4s~g21^L{x2J@7i`If4Hkbab(B=uWq8e6iniUtiNcl|AD<zb5QTojav8NC<@>QD0=Fx_(MfqWU=Y=YLAb?DXILl+d-y|NB$I2$@5FH9gqZz$buDmRKh7Yl#hj;y&0yaAl{0PsKPN>}%i~G2RD^f;LPolf+QivEZ{LawO&hicgbR0y_mZ2YejtSlAp_EM;E-6pxWugZsY=D82}G6!;==19mXD0X_>DjQb5n>>Sv!;OP>B5MvbhVAyEzXpB+3555lrqA|Z{j2Q<E!dzELydzNr`zCl1cslGn@Oh|XI_wniDTt}KiSg+`GPIErSrWrx$Ad4B$d$+k6rU}z7&aR=7d#7gJZ!Ejma=^T#p5Ja;{NXeiZ6vt244z36E*>SCins%0ryKl>|EIK;3*P`h>;AQ02>P)i!q9?mv~=dxkNu)8wtc>uCW-O1tenLYRnwOSPz~8`xf|HsACFjHh4DTDE?cFPXRKZt%h9zD83Lj1AHO)4A^+^8Q{|a#V5fI09SURi}%KNWs|^%NMz!BCbT5@t5~lBiVuX%09Q5*JPLk8fL9T3t;E~#Q}zvTW#@t`n+Ki-J`gq&JQFboV!moluLFt~AWi|s6+m}l<Y8`k(49IAK<)z&U-49lb;xBM=Aig5Bsxj7fb9tWv_v4T2jZIIO(mX^cox<Vyrx8`M0cPbG-cJ}sw&`UT_svcbb)OSu0A0`{WQ)t$i;*4y%ok+gRKLutoqg5A8@o6G2Z!ffYt@~tqtoB{u_zW5+A^h0T02rX0YwRn}Ii!Xe-f3;(6GH;0@uUcpHfbiO%31@VyP<cEB7XkXHn>=E&b4-~FL=fL;T0u7+y@V_V@`D_m2&2i7SRXbG(<)~h9K5Aaar+Y&YcyavWZz_tWe>r@lhYvNiBj19&0P+SYb+|{*U*dTEA9uz6@E7+Hw;4l3QZ|~x*@m+Bp-*p#P@q6KVV~H0enjoKG_$b=|yft`x*e2jjFjny@6160%1J6KHwyuN*`!cw)-6X;QM+=a6PU4ra;o$Kxe*X0X{?osd{{1o3=Jfo7>B*7a*GKorI2r5l%Vc~^Rkhb;Q~A?Dlc2H@{{kL!n~w'

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
