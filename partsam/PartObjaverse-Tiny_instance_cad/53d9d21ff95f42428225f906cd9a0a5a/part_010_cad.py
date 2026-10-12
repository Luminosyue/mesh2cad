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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/53d9d21ff95f42428225f906cd9a0a5a/part_010.stl', 'relative_path': '53d9d21ff95f42428225f906cd9a0a5a/part_010.stl', 'source_sha256': '694e0d7de81d6041f75d3d6f85eb0b6cc3164712c352f66016c3a19188590089', 'input_faces': 192, 'input_vertices': 150, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0827770084142685, -0.11275264620780945, -0.05229978635907173], [-0.002495218999683857, 0.1517375111579895, 0.1095244288444519]]}
GEOMETRY_BASE85 = 'c$}q~33QET9>zaJB|#7=p){YMiHHzuqRNdWNT`qzLNqs<HJgZtCGv%eSP~-9#C{Xh5?hHxOSqJFoVKQ&qUg}8n9&(cOB?NU)B8UEr^TF^bLPz4bN=V~z0ZB~e((2x*GpJv0|z%vJ{>gwuew{-x@ek;CYqa;k&u=?BQ9Z%UvldFdRlY%>hqfxy*z$&SY$mdLtE$-pD-sb&8xreHDGFhm#^+MH6<-QEhafSB`rQd`N1)Xa}w<Soar&C3HGwLf1e({dao|NdY1k_ew^)HuzuF#=qc5gi2Ngi?4rB&DpzWX|GE->^LEEnSv&0ax>DQi{o=cfeM6P4cS8!4n)9;6@7w4g>OX%EzAbpN_#;*xKzZNb-B0-^D$tH4?dTq*#?QUQk4--T|K{nP(0AR%|LH7z<NnUoD3>{ipXPiR&&@1uKIlnbb3^~FzN?q3vXN1H1pd%Bs?qO9&+e1w-xI${@@BOE$5VJ;%Y+-^Z*5b9c5?mJqMeHy#CM3=kGxeG(BJ*a0OZqX;b)+Hu2B44ZSlU^m<Z&<VxA)Y`<{o8cWcEYv_Co=zR_s-X|$8kZVj~OF!8&MvEsSgW|!eTo(q(AP8{Bd_Om{!Kzn!EiT^jFTJn41;8T9>5w??)rplJ28;9X%JIVWwsMw3~az8A7MG5+;b-S|^^}F;De|qp7XtNxQqjt|t{Ju7MuX*3+tFm5l_YHaOkQ&MFCFIS#IRU;gx8@kWA2Y8MzHe8lpIBCf?>Fq(fc`XWE%i_8$d9>y^bWkoEeEOZ)%H!L*0RKHc#pU<hfx2^p=Zz^$6DmmI;u+iE)La7O*^Jpkf+<(;^&&sA5(Fs81(nOx`Swc;1@D3qb4p!y;PI<Ti3%kb$<u*)6~&j{3}P`TYrhbyfW^5cL4r7N6{ZGX$$(JhgXPyu`9;UJS_VtzTX%^f8A>+e{!l4d2sr6AN&Cgmf(GdevWlu4O}jMN}jZT%OeNn>k<3pz1qHweg^)8b!w@*UV-l~EP6|+x$fpJ^r!P|_{M?)X(uxqdA61LO8v{RC|f`OaUII5bnzc9kh}%1!g{y7TCx{@=@)2MJD0Z}^TB)CUdewp#@AeI!u-)IeZ=n^i|1MjL(sl$%)>osr~M4+f75IE(%ydf#u9h<*1=aXF1Fo8yWvlB7XRip>~EIhtX*j5hg&F{OPZFVe$ou_gSp?WD&2r`hamWdXCm6MbXYSV`Tp2l{1g}XdWZ}52m1qGhb~+y^JMibSvTA7?s&2teP;M7v~w*RzV<;cys!0sXY3F9zG>p099S-SIlBq<(~gy+op-BbT>hLX>pkvJxy+M9?3<<sw^85Rx25=3I$%BP{@!ol{l2a(Lp$dipTPT{nTY(`Hl2a59hzE<^6Y_c;yKHz#LxAVJm!wviodTMDSkgc%pZMausmmC8}al0l8b()ynubk;#y~cA3qRzHr<+!cJ!E1@%N0w{IQ))mG`QP7XPP?+u&FAmUR){Sp4a(=#Oo|MSO3Z+yd2xmSFrX4+daA*48fD_T>2LD@yS9hTAalFBM_kYhx#1pEiEfx1hW+6Zz367h?XJHcdfZwUIUQzCmj+&y5L{8{tp&kaO@k@8i%B`@~=OGxBTwx&?e=|77tUU65z3L350Y<<j3}-W|VHh4%{WD}G41_*e3Ao|&%Ql6;<ugl{x+!M<lIIw$Ms&{(M-byLbdvoRieVUYL%X3S4ZlThTx<d=tapuMvi`7k^G6?wKE9uD7_d>wf()gG69!0S;7>fiN{_i{}@`<5+L;@5tK{M-CKm;4tT5Wna&_FLP%M|)*HB#XbNKK5^Y=w-?OH&fsn(;vyc+V4a7`j;19L;dzqI7js1CCGz*;jH+Mz9(dTpTWLpdKeDhsJ$cmjJqe!ef^UmQh)I)$1y(()??k+%FD4oX%P!$edQ!z{hA+Gi_wn9x41Xi4lcs^WxC$ISmwhIa=yHjf_bH%^pN_;ec<bHJGUc09sg8>`nT#~{%EVW$$r!41MG9gfDh1rBinZ}^!t6{`$S3}UbrFmi?<t#-|9ThabwGU*^efCTnKILD)S*cAM@6d9a|{lF84Gepa%0$Pn{(7$JfbuI&2Eg5sP`8)KB~Z<7;-_iTc)-KH_h_R0O|a3Fobo_#e9DAwQ?1<o>nmzU+$?pJG0nU#>xYEq;XfPP>qQV{XNCj6=9d{IE;1-Y<vAI_T^z{y);OKNz=P+5Mz%3`myzFR#UT>DLO@p#Hc{I3FzEg;dIVtSLbK;o~viESEj;zNXSoaZk~n36pu{;fVh0&p3<U=oidetL`B8oTd*~!cX$SI<aNlME=c7wy%JH^_2AI+-cbd^F77ya81TBf7DKlkN*SY%eZhJ^U7Rjk$X{Oj`)p7qQ3rqZ}ea9a|8RS(f1B~?VD=!-)Mb7`~&M`J}i~>XY60K4A0f;%f31763?w!^rK~-`wy4(70?g&JIyUy?nNFe<Xq4i$UVaIN1RXEdrr8In`{r{p6fjb{WS+}I`)(wab5O@9d$C_;tz`-brkc*`s!882P3##{9RWu-ujt;%DhVU7eDO|=7Xu<QhaaemXi&CMh`jvN6kZiEY^WI|FzO=jIY^kh}?@V4akCjFG%jU3j<_)r(Mj%-&fbjx=y``{9C*A692PmSr;GGVZ46xwe8!HH(S6jvhO``mHM@TGQMr5pg%^)p$z!XeInz<dz!6PGx%Ec47rDIFz_Dc^3iiq-!WY7Kl$@8F1Ca3r=xzG=do{?cEoN)`_-Z1f18T&wK%<t`;)cNOu3hDHenpiS7aR<*HYu*fA$FbgVwWb%b>8Qe$BRCd*0D-vRAc-ll|B1)R-rJ$|_TRe$#*dQ+7u0|L&)3V9)>er))DdRqf%-P~3{zmaMcBxfQuRL$L?7Gue~ch1!`MK<&j)>_hEL_96RHJCS|KFH!@^O2?C5Bu7!Fk)z177>ctPiWe~yXHch*Gsr2_vE&r;OzO*IrDMo5$%zcbNz^cMx;<vwBa)#wf|^W@AdjOak(1cYIELaN>L79u*^BxDS!q+U7r7-vu>-Xs*@0Z2p;)6jYmYyQ>rq>g>ye*fD0Zc`CoA<JyOLXIkLObhhT>=Kq5dUEEukjVM&w5Pz6sTn+=Seb+J)Sa?5{nZqyE%*vOjq`bpcuFV)AryracDRW0*ZgFcgPS|3D5QPh=?0re=~e*{0$m>RRez@?!R5Ekp5Yd*oB+Qx}luljErI<T!GFY5=)ExgWI`xgWVF)rZ`Z+?(o4?oED)`Xc!yatt+!taKJRhCGL%*q~;S4RRqv@fwEW0_q}i0eK}ggS?WQOHCo?l9y0tl9eWsmylm&C|*WQA}dWMFC#ByC|*vTO<qpUqo$Md$SbIG$x0WJSCCgR6c<x-$i?LK48`jhisw-ml1JOaWRFqy@Uur(dkmqP$R^es!cZJ;j|8fjI+|=IPoRz>r`ltxJzmk&v1<QGXpeT(=gIBJI<+ggEBmK26!)MGA@?8$Q^U!@<VjETdlGd9c@jCAnnsQ$$5Q8!=P`$|)VbtX@?>f{S!pCWlsb|cNghcaPK_WBCl95LBP$IeEA=7|C3`azyHi_|-N}uq4&=t<2GsiG2IS^cN3v2Ea&vNPY7?^3HssdiZq)8%rG3fW$bF~-$$iKJsKdxg2b04>>(zH_@SpxG;_=5&huBm9G4Zc|`Si8#$-lf{Z|nC<U|48Fbq3m#QXdO?h03h<E8y-}-~'

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
