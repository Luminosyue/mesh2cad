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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/73fc1424ee9c4dd9bee17702aab2b7b3/part_001.stl', 'relative_path': '73fc1424ee9c4dd9bee17702aab2b7b3/part_001.stl', 'source_sha256': 'a043a9c05f651ffb79f01cb4c45fc7cfa781d9ff539618a7a47f055afe386ff3', 'input_faces': 106, 'input_vertices': 70, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.2040887475013733, -0.2262578308582306, 0.005324117839336395], [0.3931434452533722, 0.018782824277877808, 0.2108788788318634]]}
GEOMETRY_BASE85 = 'c$}q|dr(wm7{(7bMJ|f4fQZ6b6i`_12#8$P#HK`<ozY6vazUUh#dT3e@wSzTh6ajS<M_vFhGFX9B^5GR$-Lkd6f!eg3zf2q(>R8i+MefosAZ~|rVjJX^V^5_yyyMi^PWAR%XV^BN#amT`FU=wUcDtrSss!~DlIh5n>nMfB)ZtJ&_VKouN>W4o%75DU9N*vDlG~xC@h&_3{REA(~45UHF9{-9OFD=Uh(uf#)3k{e==`YNukXzc`46OX!|@YIaVVl4A;m@<o|lO*-9|24{pv>YN-pYRMeCZYEjg(xf8y%)_SH<@hfj1Q9f%oO*oBs>8Y*^B`)&eUifWR;UCEodCmtMhtBGRuXVnMJle`N`|x>}<}Bi!YvG%V-H+jVUzQ7h=!z;u<>#v!k>_B+IZ>yf81>!1_96WHH-&$0R5jGM?Gvb>;ym<@>Mhh?e0vk(mu@|8zb|dq<oA@%=JgR5@cSDt!<Tn;e2hB7BH>Fp73I*zYp0;8ufW&W8WC@;2s?!Mz`Y{=*oxN`U%Fnn1NFYKU--J}*|=`+0@2U3diWOgWYLG5Nk@@)$#wYF%<1qgn(Py(FZYhf6RTg2{8xhNasC6(7Wl@NwK#v-BJ|(7J5cylHIop3M2q~g@6;Ci{Yu;Ga9{N8^&<Y@#<i$(+V=g()9{t>7mr4~zT=lB_+|Hn?-iX3f5%Sv+BJTyVon~Wqdu>N=%;mQbSwLikNc8k_y~14r3pW!TrcJ@9`{{tE))LYE(7YUXcqfjwyM>BeoTJf;QpF@>s#&nDLEb3gL-0)i};lfDn%d8&4)kr3*leeup0Z__rVsNf9k66uWZ|h{Cj6(&P|>-;hW1mPvgFCJAN4PU7aGn!*2oRXT}4}gZ#C05x#j`F7{uUBc8A40)*fB?TfhXcR`q2)3h+**R|m}($5)>`)=MECH%!Hm_x1V5uQ(NR~CGeS|j%R+fFh6)l-<KY$@`8pNzg)jkAO=dBoxTllR2))mbC_6Mo{k$hDkAeE&M($2wwPT1#;Q>Up<8__~Et(4UBjm}lu~i|{u$;C`8m<3xXM^tl9o?a{a4>s>K#mZq>v_H$(#dl-GTG)4)3f9-r+w{$M%O8<BreC^#p5g+P~{mMW6$ULuA!+&$!0o4CUYJ=Z5|5ZFkKj)(V`f?}X>j$q8eh|I~q^xw||EgP!I_fTcit9B!E&Sybm=o)S@t9j}Tz;GVb1K~}!~962P4M+<(NFW13%IVfWVOhXXkCT)&3iVAd2MRzv9HHJi09&+$achQ&#Z(R#C<XOq{5fIuVW6)&0EEs3~3bc9qnbvpX^_Uya$_wZ+0=^yo=7FpYjWziRX9sMD)3N8|Fkh;By)I-ajky*CeCQmUZdyr8`4JKifCez^{5%_=a1h$S;*5UVCf9W&1j{k3Fz2dCc(75$}4k2z9z-9Lm)7e4AdpSHHkTl9biQ_BJibvwM{)rgC)a-@i&{CjP5eX<Tg5|9qFa4Y1V^Xj>|309i%uXItLXfz$x<Kym~%kgVuXas)Y!8cNQjCQ(DlN#ro<0CE`FhpHm`kX@<$$gbpGc6;c>rLgjsOkb)W)tfwoI*95`_U4`kaVZ={jUY#n6RC0J?mZ`RVa9Ch3F=sCCV4D*3^j>7hMYzXBd3wWsXpXzvIo_b>_K*-_98oxB`W{o!=bRFUGE&Z6z*eN!Bm;rmn@UjR6lZeuhm=%59d-?LmfockfW(l<Y;m-HIbaio+fiCoMG4Z3~DMlgFJ#7Ob+HAMsO({LsgU2tUHFPA;*vtsL|wT)|5caAZPFz3a8jskZld7`jQ8e-Kd^qH?lL;o$O3@pn8!V$SzcWvJ1ICbr`unIg%PrjwGj3N0QUYqirjTI*K}yJc=AbjVH(R8X;7FvOjALp}LdZx#tk7FWHy93*k~Y*0yxn4vs3PfBF~b&%>lNsmDJ=e>t<q*S-CjIksGXeEI9LUGQ8v+J5FL%~z_Feh1@Te&Y'

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
