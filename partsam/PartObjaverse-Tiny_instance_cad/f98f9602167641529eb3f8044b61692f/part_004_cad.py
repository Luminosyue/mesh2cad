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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f98f9602167641529eb3f8044b61692f/part_004.stl', 'relative_path': 'f98f9602167641529eb3f8044b61692f/part_004.stl', 'source_sha256': '2f15578f90086fd2953cb3c8a2a083b36038f2b0162b16a1a9f9a7ad6518f123', 'input_faces': 130, 'input_vertices': 142, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.49985942244529724, 0.09786106646060944, 0.1883007287979126], [0.4318893849849701, 0.2094208151102066, 0.25986555218696594]]}
GEOMETRY_BASE85 = 'c$}q}34Bji7RO&mD2*_owy`{_{vsJA2@)ZBu@g%yArXxi@{grNB&j7Sc_E5eW;$BiD1Y0aTH5j%G>d18Ae*R)?bByyr#hc9(=uZ^)y}==ciM61GxM44?{hxqyze{r+;h&m_r5%_F?GG0Y4~-}`dl>kRyWc#DZW}WZN57rYvwd}X1BETMP6DH;_~-{UOy^sWNd<$HebterMNSvWw`q2uD+>Zt{~l&IyWOLBROr#+>8{r<b#uEXSxN?oROUF7S~;Rga!xcApt@9V*P*oH54hBA3XWwgwT4;nzAUNJzuV^klGCSTH*Ho9Nhm)G5E;J3*<L-F>$>r<Cf&s<Hl#@wN*HwocN(R3b)H{o~LoYw5~{Q-;Y52E;XdJqp=?m|NZBu<h8N!KINl@4OaQMo5<&oc3E=Ijp`HRmv@lz($=}oN$zx6R4T8Xah+&hd+V~Zl4~Weo}@VK0>OKnJ}tRXy03`F`+S2qTl2S(f8Z+0-<X<3{@Rn7Z&F>^Zku?^Mc@y&tfT(yT>l~Q&j(zjdd*6jPaE{*8PdP4Ab-z_o8VQ&l)tA<C2^xPs*=Xdnn?G}dyA{7pBti8erFJI=lE2GYr_iA*HtMh@7EfAt4*jPzAfl9T}Mx#IQA!r#Pxh1;(BNY;?|OEm6xFZ_NO^Y9Ltk|^)Nb*xZ{;Xb(z=UZ%kN5+^A>_eggiEZ)ciEGfz{0oF#?u^L3%_WAo6r)EVGsgH^t;g!<;R4N>CQ2`>}3{KMg2XEi-v;~n^Wn)Ctx{$3&R_3$^=EJU1$EA-s8i!szkCvj0V#=D8@tJ_tg?p(!R4|Zt%7>9Eef1|e_*2Bg;^mX;ySSMA8<2e9s&$)P<?l&Jn+`hj;@waji$2qZ5@%Jpoyq?aRFmI=xSpT1Gz<%5XZbcMQKF$~5=9(Sg{k$l?Cv+om=b4>|GrJMRx5L1VLD#{9dr^F&;b!9YNpR1wBGl^#t{u1oo=}(K>+#^0>n`G~Y)tX>$>7ejkKo_?D$b3c$5J1(Tj2J->B#@}j_6N^Zxw$h>@Loy&~FugEz%!-o9lgv{PPc@|4YHOXdmKEY8B;U<|B^PXDD&QtBlr_ar+F`cla>kX2N{pX4yRA_E+Ooe*GNQVN9G7M=#>@#7IOw1K*(aY5A359Y#(jZbyGj>(lcH{?^uW;Jtcc-~BlW>(5h0+-l=TT>Bz`xcT6!!kvKoIB$2=Dsc?oeC+FqH;_;8T-vAlVE7w}H;HTC>EMCzw~nXR(EWocbk5j;dx)Dm<|*81-xKH0mVLyXYi^ul1#7VWmhM-$l|LTOHM#p`;?H%Zd7bhUtea*%E@MAsBcGBN@x1Nb#I1VX)K5LFmY$2%Y7hJ;>?Q7uUQS$_^pLoAv=r+<F`^RVz>UqnqxInIoI%`p{~N{Mt{;efz4WiDe}g9%FpvL7<QLx-`}e)W*mvdN=86F9_aop&)Ca_k%#QHCc?|oj5M0~Y4g1{z*XESNe`^K&<NM=0$pyET+=u^5>B#>~jpFa|4o3cOURM0=dfvosueMjnKh7WT$IW-E&?n~chtbdM*RlQsHW4=)7<ezAO2hNL1+GP|!}B_fbJ@Jo^<x^>EsLJJr^&DIe2W8B-f$Y$`M{CHtwL~pJN%u%Q3^LU!{07WQn+>GEY|s+DJtI=hkX%O23|fK`{><F#7Q`hd{%eFzS|y&eD>EW+<Bt~_G#iZC62M+UA*tU>v5IFjlNCifTzVHoF`9$iF>Sdcz+e`L_dEMsq)Il_`Ah7N{M5o{Tk=VfNbLSwLjwAt5}Zp;GaX>8NL+nskQM~4-@kge?7D{&cj)GioY2?l(;cv1M)dChR%Pjyqeab=LWb|j&oS62Db`}5a;n{I6t@k3Hxz(F>$l$L!8?-^3;xj8%KWu|M0!=Z(f2p+v3pARr7H^q=Rco%Mj<oNq8@`J%KzIbjEYp)F01lxQ#ed#v*@L4e~4nHx|?)|3GkK=t;yskd5`W3-3##`ze*bH52g<o>A)ZB(z6A%g!iyYSV|KpYN1n-Upx3e$>84{zfUdmG6yx?fV+)I&>b->qrD~CyVn8x&Z$>Lva2q<htrsDDjO0nAfhVP~sbVkf&Z!h5WViw6D$FCs=PstC9bOc6d)+KZtdH<r4V4?X<7$UG1?BPt_>>v5GEXf878#w?yMSw~m3oeOdK?FB$tZy>Bh~zkd(?sZ2tDjzra>&M5R@(8uUQS%1af$R34y6aH|G_>hq}w+GzC`C0VV4e}f1L+@Gpd^Y}Wj@m)oZjp#{a==$Ox0~)({GC^3U5tuVz6L9Nr#;wIPt&9{5MP6-$xnR>N+^Fn=zsnxI5YG=`xFf6{{MaoJ}Yu~Mo2@}_1TtOey#ek-H@*vvF*#c!Bcj9zLwhODcg&$rLMzv6OPrGwJ+Osg>Y*$ZyqCKtP!$WNCE2=Y!|S-l6~a$S{7-qVk!79eg55CuLzkhWD)CZw$p`V^8HM{C+)dH=JEY`d{5eP*)$c>l64EVGlXRExGWwcZ9|A$cLP}uVEZ*8`9hYnUdDDyj@gcNTekZM3Fmm>981~@ge>Iw7xLU0JVuUvo^>a-m-AdpS?95B3Yj7#h4nPH2MHN0WC-h_Y=;O5<-9^UCuz49(u(`kihI<IW678^SWjm=LC7Q_iL58H{XFL!z`85j1G$I&Sx2)ygJZtTdN$ibIOk!khqL`NA>Fu+Zd^kM_d@o>Vx7yjE~Guz*Pd%@&2z}P=CDp<d!mqdt}mWzOW+!0Ege{QWV=7t(wB7v+jBVPOxCm59>%qdU>(DD4<W%^Uoh7u?Jh!GT!)Km&^eZj>1LhE_IM%VxQ=mL!$i(i=KNFEZP>QBS4&tgX1g!f(u;LZw%t5eGV7^qkKkHjS&wGBw~#QdFN|xGc94)jt}l>l>%y^Q%$Havu{~DE7_M&&*EXJOkhMI=x;fjuIOp!HUt~L$a~s8aB-{OjL~_27oNI6Hh3v_ztaI4zEaU~Q;{~ok+7pDtalUb!>sZc7=JpfT{%ps_c-3iE_h0=N=ih&pJfM~T@chS->g(|7k$&Rk^5e@fHpYj}{W{{GJnU{$guek&YWMs'

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
