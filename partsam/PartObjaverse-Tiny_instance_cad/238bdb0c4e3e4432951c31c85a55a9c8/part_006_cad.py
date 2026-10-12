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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/238bdb0c4e3e4432951c31c85a55a9c8/part_006.stl', 'relative_path': '238bdb0c4e3e4432951c31c85a55a9c8/part_006.stl', 'source_sha256': 'eee978a52d73e44bf1eddf9181711a6fe2e45c4cb2969bfa17915e8dcf019f1a', 'input_faces': 248, 'input_vertices': 198, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.39553219079971313, -0.4145633280277252, 0.006012275815010071], [0.3936278820037842, -0.1340215802192688, 0.48991790413856506]]}
GEOMETRY_BASE85 = 'c$}q~dvH|M9mg;40zqB@wE`~B@CXD#6bO$j1S0Q*M}Y9kMv@dPBq2c%kg^~J1i=S^P!(K7i&#V=53#9uK@z}3C51Ie%dm9X+COxxwN5+jKRsvnb2j&$J<fF6o%zo9lh52e+~3@Lmz+)3v}VoYt;nmV^-Wgh^$wjaOD4{Wx7HSvu353HplnD{$@(T%hp?9~)%#{<&&bMYVy(3{Cgc~CEh|k(^(2fb9GQ^lNhmBXT~nG@lv`YyUm$%(-paB9;melil@y4d`wts6GSM@9K%!@p=YM>)5vSlS%=+R((V^?@ZpyYYYWAf$d|-NAgUNfR9|)Sf{pot6x1PLKZ}R?%Dzi@=TW4ISUrVF6mnPM?d|9S@t`h?fI(;Cgw!!4>(tSab_kF+C=sllbtv9a!?P;U8v-{VXym!$zwI*-f?NsCRR{CJqT>jRRt~kB#OS{47|Bx6odH=yUqqlZkzGm{F;0dGme)a7YleZUC8ohPl?ggi}@8;ih&SlT~N1fBFxnewX>0ZsHdo`Et)m*w)bLn2q6|+8bDQ}&MZ*bj*e^0&U^lGjc&s@4!bLn2qrF%7(?$unnS98Uz&s@s;m!H4koXhuC(;H5&=8EymrF%7(?$unnS99rJ&82%aSIqj%rM&O8?csF;DLZe4`|HsSPOs*Q@yw-rHJ9$yT)J0t>0ZsHdo@?g`pgyenTIYr=kols@|M&4%C0t;yyvA&L6f(;=NWzIXnDQKTemlv{pO9eChy%g!RW1v$<<CDIPm8WU2_F~_j{+0&ZYV2T$+#0rTOSwnvc$<do`ElqjTxUtGV#@ns+LlbA@tF-gbI5m+sYEx>s}QUd^R@HCK#hF5RoSVvc7n<$b67x#sfBsC4=0_0qg|%jTfThng)jdheQp^(G&9d8^S|mAh(9-v3#q(Ob9DtDWAz;ro-}^MCdE$miaX)H_b^`EF6r<o$iTM(=H1QExo{$`+%yYd)?u9{<q`MsIypRqgcNF0Ed7-EV(7ciZLpJy7?)w2Gj~hfZ%adSCYSdXu+H&YS)F8FeP_eWSh6TbEL6jK^2}t=j4R$NzmKJXf>w$mh8){f^Uz@=Jpz?=PQk^xm<N-*0vA*<WS!-dX-S<N8yl8od>Ntj6g>7g}r!|9ov<<bFFl-R14V)j^Z@9hhhI{>MM5H+k<T=ZxMeUsq>bXU}+}x1K#z<Mf_a4sUhdZ=TW%w_Tq5P4{Zwp?kIO(7oDs=w9tRVm$kfn0459#QeMLJ7SJc{<7NX1CJ$bbzZN)wS{+_UR^KUtLvqEb-i@2u9xoB^@>@C>lJf6*GqZ3V)_0w$MfRZo8j{6dC|RkUUaXX7u~DpCFXdZmzec=UUaXX7v-&q8{U-dyAk<(_DoK3d3*QbpvhYwc#YovE&so0-kbZB(c6Fhtk&fHUso8tef(mz(|fB@Zidfa?c@G+<FeC7_i>t!?&CBc-N$J@x{uR*bRVa$ul8~J@k90+z5j4R#OEIkd;g`J$nk35ZTH^q^!~rBGkV|EkLyj|{^J>=_m3G^XY>i*)f(4%yK9ZfTU$P@Hm;MF8S&4>M|^VAFT%(7<a?62fhU~a@7ZAVR;T)UlMi&PGJ3n^xH_Y6(bDCu;lsi{G=T4O=7wCp@jTtW@jSKTqvz@Njpyn1jpwQP=y?jC<@z>lcj)suo;dLch_trit-?IVS7}npmumA@X)99xtFO|MQ~vL-(vFIAcvIvgkz7e1gDc^8>9^o_;ZyXl;8XBv`Z#<VK106^pMlTPC*ZU2d-OZ-d+<4tt|AYLbRm*^(EZ^aZ~{FHPJoBfsqj#E6rB!_f+x_^;R*0Gc{|YA^mI5Io<}6lpwr<Q@I*Qlo(PYohry%aWV%0`3=g0mga^PLx-0B~?<JD&A(GqCUEp?b9FZJP_kiQ!?sNj&9qvaDh5Nxt^e8w99!XDtN5bRjY4CV>s^fZ0C6eceET)&xbKxcMQaT%63g^=E;9S^8B+sX3!1Ljm^h9_jJc%9+PlCtL$?zC>I6VL!4iBU~@IbgHeJ|V-zK=+5Pu~N#hg%ZKE$DV|3%EHQ2RDbCi8Q6#(s8itc(^UxneGmEhP%=I;BIhVItlIz51~iGL*Nngcz6WtrKiGPcnUoSo&wLd8t<XmMDik$mGmllF}w;cqL;u$a523UE{03!T(|^YP5a>0a4C_TN6&}z;05$dcmbSAPl7Yy40;Tl0gt7J!(-tTdLWzv52Aa*gWz8DeQ+=Mej>R8-5%}$x1w9ZO{~a0*M@Ej%kB)ffjiON;7;%ZbYJ)ZxDP!9?gI~|N5F&OhiNbTFq}qDfz#m0^lW%CJd0ig&w>|PjrZI_BKfBxKc~0TE8*?%4tf>51Kvp&!8_rn>0<b4co$s)?}B&JtKr@7Gju8Z47^8VjmTb+GI|fZhhxg<Jh%*glwJTo3g^(7a1NYBXTVwTBlKAK5qKP(0*`|qq6fhb!HIM)I1%nm-w*eOe@rBIq&vVJ;UCehVEK~wdTY83EV~o@Gm*6-n~3Dc>3mrBGI+npA&~<_@?rW7SoSaB0+Dqhg+%fbB7S-^y$=3~$a<0GMDhlat@IXpJ-k9>qsU`K@{=Ol=%?t7@UtQnBF_=Y2kBQ}*#Y=9krzc?C6a$3@;v<l{UW?i<Ry`EBKc+d2rT<`SndsMk@rQaMb3*{A|Hr+M1CW3kyMFX5cxIlm7F!LNz?ddKlG>i#+P5-2(CZe>+f`LOPueVDb|W^QnIGCke{dG1GH)QVLc{)Q?&jAm^6=q'

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
