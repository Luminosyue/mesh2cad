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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/63695230beb44ae68650bdd4d914917f/part_012.stl', 'relative_path': '63695230beb44ae68650bdd4d914917f/part_012.stl', 'source_sha256': 'f88eda87ef5bf60cd179ba8bfd3a9ef60b8dfc0d49a6b71cabeffc609ceca24b', 'input_faces': 195, 'input_vertices': 138, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.24035926163196564, 0.34914588928222656, 0.026760587468743324], [-0.027883663773536682, 0.4930759072303772, 0.08870115876197815]]}
GEOMETRY_BASE85 = 'c$}q}3shBQ7RL{W<_ke1MKR}q4+PN+ygo?tnu?fFcN7g$;UYqc1`0kvG!GhBtJJJkx-jaLywn6W9zIY`se$<zr)JWuvFl?rYbGsAo3xty{rBIx&YD?k*34aNum8{g+IN5Z?C<;T<?5Kw!Y4qJSFn~lpx~!@zM7_@y%wM?O3Pj_J2fq5K<2zWFU=pmdfnESADtZMNc7ScY5Acu({fU?L!<T3;psy|BlOVptn3BZDVfPx*)!9WACodSC(Z5W%u1P;=Kgoz`=f?N=uu%2`ZE20e6@AAV0JlpyixUX=)lJ#-C~s;ELUnjG5;9+f~)YgQ}#_tjj1v4jjL<m8`pm>Q)*7}lKiLJp2Yjp4wWi(tvr8J`Bt$Xe627Ub@a+3;?F-Pb;i3;N2^*7U;C*JzM1<8eAh>>!Z%jjg*whXaqz7_-79sfy1_SodHfBmKl$tt)VXGZZw4KB6aJwl@n<EVzI{<7>e#R3!?$<nCHdXINB{QFEcnKSDw$70xjgURXNte-5#(Fmg)*O){H6ZH8}eLX+mP@4YTpOwQ+LXI7CvdBPI4lA`?0|?pA%V9e`hp&?e5u9Kk(HO__4a=7nY&Ep6reNvQj%p{pJGc|Lc>e@4E5XVdP($EOQ$-O!~<+;akgtCBJhd>bU$$B>(DqS+{Z=p3AxYW%$Om1z6X$Yowf$Rq5i_9~J-B6XMq;OP%?fq)zyAn7{M%I9b=WLguim9CLOSpKZqTHp<+rAIeb2sG9=czPKLwu6>Og@!WmmB|o`Z`q!Tnf6D;LFFqmjy!Ha-pk0rU{K#W6hb{}@TL)T7{-qMBf8{OA$GGex{`xN^|MkJLzrjB=q5tD?@b#mUD&WuB(d2nw%nz&K+b>NQzwAZ1N8vH>^(-IpZ8v2O&9UgmnX~(StXoni{fy5;zU$yh_*yIPQ&^AZ!3tR<`Qt81eY1Eo>eTj!Z>;Nqd@HXO^EX=iNu9AT%Dy-<k#FRFe+d33on>yXzpw>;-MT1#n=i!wTai3(b0vIZG4I8V!^n3APLup4a^8%CL0eJB^p^am2BRPIv?2Fy^R0vE-!@vF>!au8^P##~{9e+(zUCEKciRs5*7FnLYezTZzFQC7CHdzPWZln}ZG-;d+XL_)mh<WSE~X0a3p@Z{8+umu@$zeLBmYDmeB;PG)OTLnFZ=#uf2q?L3*Wwepv)(5&wKFaCds<(rf-Meb(HwIYmx8TP=@}kG40`7K|!*=N7n9uU-Rv|$e+GJ>g3tr8#6Y**ZRI9`}oZp@?0+k!nXp8WS)&lvToB~EchqBlY6l^bSIv-`^WH&e!FGg6F0&)Y7)i2^tH@0V2R9U^=PScB|-M3Tt~k1l|Jz8gXTz`njhYQKR$Cm@?$E*H?P;ApRdj}p#O-8pWu0KR!SYmF7aO|mN_4bMZT7?7QPX6LC)K#>$O;ad;NB-yJpSjsGGbP`=XtCqZ)qSF!<)<Bjvt4n*-k%F+uV}zQpH=7IwM{{$n@JAm6Vw&c8kGJ^0$dc;s6j$i2SpTSckxoj2rjNvoa>-|p-VUr(%&?~D7#NS(_Q;cJt=k<asHyX0?Z!n*eO2Am)3;ULM64M4u@od)TrV@JuaohJQ%v`;<{hgEHZ-?ABXTtiRderZ}Me4})T<hPrII{JMj@U6z)(&vnNxpxl*!q+}Nen#dy4ChKu*Q9>$n`dO7Oxz1=>Xo<QcMU=vqiikKb)9`0z81D!>dcI*hL)sC{+bwhu9!KM@WUSyzewt6U&y_4?!B@VefGG7I#%;W)G<eV0N-ek{c>KrD)ZmiAb!dwndknKIR94UZt=atW!=h7SXW=S6~0|tDfyYb<lZ%wiXS;c=Gi-5{6}7dulWbdzL)Hm`3%Wq{uasKeqQ#sse|O_zbAbTOxq##yd=N8m7J?5{L!cLrQKWbydNgW-1h9nz0lv?3E!ALSmxYjEY6Ak=<AYy@~@KbABp-}`5?*fY?J&&ugZCd)ZyEs|9r-C{;tE_;cImpWzId?;{Muee%y@uV=hYnKh>eWxvLt!woK+=G@X!smY2b|A02~yZO)sxzgE*i@$Hvo-E*}#hh|c?)L-V5{&y_J{W5dMZ}xmHZE&=FKKRGLH;&8x>Zf-~|K`O?^fO|w^ndS4^soPN3cfKdN!ES85T6^aJ^Lho*N@`g>Mh?#WgEqRW`UfCu+LH7?4BldZWc<P>jt8ZbHn)x_@leXxwY-Zd9Z4;;M+HKk^F`}@_qXA$O_NrGE;n!?+oc%;n}B^TPok1)pu8TKCjmH4Ei*81ec@F>s~VdUW0IcG`|4&M%{T?w|)Tbi@m>D27ix3o-6+X?w9#My7-e1NPXXWxu-ARDuqA1pUino0s6GpUl9M<`Enk7YVf^a#umcYyo;qy!$9<-`{l#8|3mJt;kOm%$N6d0CeQO`t}B#t+q&p2)SvaB)G59q_xH6=-$b3=hozrU7vy{fl!^b{TausJ8@|<TmMQmci9GL$Kf>3ZTm2gHSJz2DJ!<PlI_~(jRuQsqZfP6$2d6vQxPPssr+EBSQ>J>|)_?y~ZT6u5?x)%?+yDDh?Ot~ezjH?@wKrL57&(+2$xu9)I*_dNKC;qbWNfKBT2fn)J5bwGTajBauRXOb*-ul$bpLE&DE4J2Zb9`S-$iZ7XrcY~QtU<bA^Y(CUJS*p8Hzhn{m6doqa#CccZT8~)UM=UYG-O!a#!Ycruve*Q3I&HWPfTqsxR4>&(qH1`P)%jl5fvlaUXZ+?g*!bkVm;=ggYLj+Q=iR4^VC7q0}g<jcjARDCz)m6uBQYoE**`6!)d}q=t}H1i2%Sq4*wZPjXM@-@^#uoI?1V0Suip?nds+(79K^<OpgXav$~@LA8<Zrw*ao$TrS#2z5Al7}ZW4P9DxYJ45jphT^f*QRGqFkFgBJF$~3{J@#)j^#Sr|@<R;8(H{F6O^qT)lLt}zkq43cd+c9-YEN>1axZEixfi($wG+85wLP^HxfAo+GZc5A-b3y{ZpTpUPrZGIGTkxT9n%<!=TkGuO7qDJsY|H&<fo|x)O@mv74CS3p?Ep9fLy?Q#mlI9)O>P2`^cj%Am@?iQZvbO$w|~{<RtQ=)OhkZY8*A59M8NshT<92`Q#boERPvwQJ0Xj$hi!~hR5s-Y600G7gC=g7m}Z)t|C82EuyX>uVP*iL-9)La`H;@Qja}YO3foLB`>DVB`+q=Vkk~$C{Cm%k&`&zM26zuGZa7Ku^)<`bVsT?=1?=p^QhU>4Dups4mE@P6g7>SL3UD;sTt%9u9r-mPEIB#P*cfDr;?RUAuF9sP9RUDP9ZCGkRPKyOm&cBspF{*@&xK6s)Ouc-AUBP$&<)WP^XZmuy4gF)S1+&WXA+A?|>Hn>A&NDdl~8vhdcgr{$JmD=bwh2@2qmy`t=V*$Ap&Z?;!UdK;F1mtJNo<_D}2p9nt'

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
