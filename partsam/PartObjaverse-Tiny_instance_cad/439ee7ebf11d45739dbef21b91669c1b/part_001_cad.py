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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/439ee7ebf11d45739dbef21b91669c1b/part_001.stl', 'relative_path': '439ee7ebf11d45739dbef21b91669c1b/part_001.stl', 'source_sha256': '0c7299742cdad891d02c921995b4ae0ecb64ad3cd29d6fe85f0a00dfa781dc00', 'input_faces': 126, 'input_vertices': 122, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1311400681734085, -0.05467713624238968, -0.07739736139774323], [0.12921983003616333, 0.03648780286312103, 0.07719000428915024]]}
GEOMETRY_BASE85 = 'c$}q}3s6<Z8OIkeHlRhqD?W-IK)n(Xc`90z0}3dFgs24Z#X&$JF@pCZRvqK|ASP&IqV*YVjzlqPMG%OnJWfrMl9*1UNwj0r@z%zfWON#nCf3A;>D}-9-{jh9XFBb5cK*Nf=R4o-+1<0d$GjY$e!+r&;UcZ$RLkuFLZ~uO1dEz7dv!%gnImR-)oL#hK)(99b?0OGxp{?NqDHK>m6kb5?6%38EoDivEn2fJskB$yi<cKw+DprnpIN-jQRea;<;7KHuIn*z@$u1GLR7T2PWvB!ey%2%@$XpOF4YsiJ)u;l6>LjY*B9H#mmjwsRVv`iJx%QIl;q2dJ6n}+PCUwag5PeS`1O?(Z*~^3KlQ|G<Re~0)_2jhVarr%-n{jSQfuK9@~s4JkElvDsovd@9Pe(=6A9#tEg>B5Q%k<-9YVhIS$~eNLjLJfenstg-<Nz@o=)*v;4q3eDh2ua=64%B^UH_(Iw^j^J@U1PaISajdh)HtQ}kT=-~7opch2sh`<sep(0z4JZK3>^zdldbZ};q?``WMnlKjl8=g1#b^CIO9ok;zl`4zBVQcAuavTHr%g)iLkW#f;jYoqI}v(%2mebjGyp#D1bLqik!^3iiVULV-VH@CmS@#qIx>&x-ucd(D=6}twJFE2e$zKCtjq4+&F4p6(=F1M3^Xco6~TJI)OhZp(QwekC?ov$9*PuD?r&yapwdyxEZ!ZuL*r(YpozHpWLM=VY{O7(`dlCS@12-g?6lJc0D+c>^&H03uZOrSjGUti$-Rx<fAyO*BBd3!3yBaarphvKE5FXw-;p2p9L{c1C5((X6NzsK#A;{rEO{RK<OmxW>cyw2?X^!J_w_QQr#y%yrlh?{NXcSlgY*5o|N`ny(Y=W~tqbpJ=+(cg`==g5~AU!wNt=U=7#&dvoKkM>wHX)pO@^IAQ}UEb_zq<nodTRq2JKiS0oopkcWjh~ZmE!x5UJExl|ZuVYkk1=-V5vr%+82QHPO+4=}WgMpd3oWGg$$E|Jwa)Z5)AKf@vER|f@8e4snt7fllP^EvdSyim`Pw&M(EXa%R;t(PO*=t(_I*me^TGA}9u|ChjQl&b{J!m7!{Zea)adD3BQ{bV-L#(~t^DL5)rWTKduO%KeT}{Bqn$>D&i?0J<cs_rygsDIk*}|~{tL=)tKojQlGo(v>!;Rny$1w6m+1Lyfu}Fqo?-vD?7Q>mw>v41=wSc*_ME-Y;_18FBkP*Doyi$5Q@<j=;jVWQ`%dK7&`xXcSei%H9L}TTxy0&3@^#cJ(GMayi+%K)M8E0t&Kx4uxSu8Z*?@0iT=Y;L7jbg<af<WhaTIfT9JPg!<Xaeb`FkFB?L-Cn0`tU)c_Iclj(fJ#iFqa0)E)P1r)cMSXbrnS&#kTDd23?c8f!0df6w80u0``acfLNq#j{>n#P5aKw3vLE!|#!3<o8G)>}a{Ke{S)6Cwf+K{C8M4Hu8IFjQfCm<2`<_MJL|tTQ@j<3$FwE6<!C-4}IF``q#W}=u@$7q&AZ;kYA7Eb;bxD`37BY$2ykC>zH=0kbHR!>s}16d)lFT@~sQJPMR~ZPToDt@xsP_Jg=+H_uu3E$fJkzI_!Ka;0)#Y2iEhic|Dh-hO+->tp5jj{nxv{AYUHg{X%B(exY4I-cEVv^S-0+=6y$`x3a&K_bKZ+-lw$Yi|wA{B0uDP&FXQsdyb19#QUJtQF)f)qj=wRmhiqQgYD#ta_qAMd7pLO{gVAhINl24ecAcE|9SF%!~3{?p7(KQ#xnK|?EBk!-`6tX$MQKu)<?CF?%Ll$?K#Qk2l*ABAB@}v^2Nu8Ybk%;C5jjChIV@Pj}gh|5NG%h^2H`Tx9GF@++uEs==AJ2BM9f5I2*?cZjbfmy|q-o+t=7Prs2FaDTaLM&F3qp56)LJQpmTi@_Ec%uO9Fu$H(*eO<%$1H}Uyq&VPDC73Jxx<^ABJbL<Cjz2Y-I2g)zQyC~0Jy7@fN5LHKUtM-vEYW}{CeB;>zq%nW!ruL-pIa6lyIny}Z&!RlNgLYHB*Yu4P|8fHPRv@2O<z_ywTDMck7d!ZTD{?rG9GSuXANhG@CZC7JwtUWm=M`BvCui2NkMR|kqf1ls?)zG(i+wYpyuWMaxr(prYhg*T$ESiaX<9=6{ii}j;(z(6Fya6GRB*W3Q06Ktq2=I};HA*{V5JMdOTiV;W#9^M4fGjs4R{rb;-8@?UJhLdUJhOaeH6S1oa-uSt};W-M-;_b&|GjX;<KPRV5OPhEU*qu1uISQ$glXPD2kJy6TnKxgOk89&_}>Zqri!X8wZU6j{}c^MuEqGgP_6SAaH-^kHG!G?w?{W6vf`q2f^N8KWGTp4?GYW3RXG*JP_;y{V~`F+z&<ZAm}i#(ucu=!2Zw(us?V(G!m>d3_KY85OfGwX#n^k@B=7{eNhw#q9`5?9ReN>{t1fW5zsKO(vjd1;GxiP@KCUZqIfja238sk9t|FaqIfJc4m=hd3ylZIf)k(<!3p4G=wxs*coK@@DbT6lDd2SIG;lgN13Dd?0nUcb1ZRWuP!vB7eGII07Wi@SY!t<Fp-+J4g6BY=1S>5B&jA;pD9(o#gY&^f(5Jyg;8Isv0<DBT4Xy;+p;cfzxEe+AQ&0n}bRJk~3Ah@%0$KuAx)`j~0j`FwR(+e}<sIzvpZ-hhho4jn!+rn3^{;o{zrA_h8RJUy{brY!^8jse-mZVD5xwe-68{7N%tTc'

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
