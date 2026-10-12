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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/053b8a4984e340ad94f3b563594ff09d/part_011.stl', 'relative_path': '053b8a4984e340ad94f3b563594ff09d/part_011.stl', 'source_sha256': 'd788892ccd3159a31d65c4bdb626604215c2293eacbd4bc1ecdf9fba0c6500f2', 'input_faces': 96, 'input_vertices': 100, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.046554502099752426, -0.1798623949289322, -0.11602567136287689], [0.059138089418411255, 0.14880850911140442, 0.11707469075918198]]}
GEOMETRY_BASE85 = 'c$}qIdrVek9Dcb~Dk>l%7nLI#w@^Mr6cys22?}1&0K+ssL?|Y4k1TMWT*_wIW){s`ej;Wh8i+R%{Z2Be)+XJ6nQ2U$)gtE{e`r?geShaUcFq}Xt-kHq^Ssabo!|R=uRC8xx|_Q%(|(g!VY<hP{$Y#>crssBT~JX~lwVLet)%QF7v@F2`02cJY1WdA92Zv2YQokPROVNN&5^<q3gg3~q_D!$imHmdlHAgYbp^st$t$ib;C|(Ed1VE>9Ufz|MM<#{QPM`~KmLY`QvT>U>=d<peXEuDeCWI+PWG(<jiRmG?Izzo|3ZuKCHQP$LZfKQ(@wPs?%!gLXRmH-aT<L2Sa7?DQ$LSCP5HN&^YoXLw~4l7iI+VGPl>kr{`@y7-$%b+5I*bD>Qs_f@1Xc_&rZtk*U&)Et^Pay4V0%Xd#7kSng+V)d3}U~;!kM4bk^e&s;gVeFP|{SGu5`A>dbn*iJn*Xk#CRBr*SFp9s0bzvblrCXNgz#1)iqo+2(ll<HQc?r`Nri{C8J%Qrqt~wPpB9snaQZM@n{!$?v*&hUz<PJ8ty#{Eq9RPEedBzoWje*=g{Vs+0qiC-|$A#&}k2%Ojq(i^i*3>QRo2q;*#<^(a67qV0=5OFgMw+Pe3d`?cq8KS}G;XYN<slR@(){}!bAAH=;u`)SYJb2Q%jW?#M1c8=<4nM}St;i|S?^;h@Mx>$TU^6YM^_nSFdJy~mMex&=heN;DmcJ&gCS8A`O{i9mq<@*!%It{)&`ZCRfV=%M96kqT?&4X-<)y{z>Kdbzf_8aRl=TXjg9x(c9@Sn859XswEN;3HD=FxH*Z&UkW+TT6qe${&i4pRS?JpJB9hv+?Po(P+EUu@gZY&sX0wezC;>b>=yMqh@{(ylp&@}=6J&KP|=d|AJj;46B+pPg(p`VKw+75}Y9U)}nHmS?(+>gjLYdxYj0KJ)QZ$-h2$%;+m;3#m>ua`J~1SEu<>c1SzLA5CmE`i@`AsDAa!Op~uPhaac)y6E0!%G39(c0c?aM82fQvjsH&(zO;kr*fUSezj)A5vRe|>$f-OA0w_a*Y6nILB3+CU%GX-#pvtx%RXM(xwO_F*+Hyc@;R!Vvp8*^x0KMi(0%38F;owGJJ(_I!>g&D{_nPv-w$8vjG=mzFA^J!zOt!S+vonp+I`+_?pK|+n9i5(Kj=5IdB4d=zw#P)htZb;<F#>lj&C&PXGN9Tx@4x2FX?_jFP#(nlpA!u<Zg5Q((YzDkGikdFYUT+^7VdM@3w<RU+-6%*iOD;=~ue7oX(@_m#q266SebI+E|=q@a0WGG!M$lp6i@L_||x-ev39gcWxIthw$yuu4S|?@KsxK`%u0z@S3)N)>oBNedEmWdVbxP>Qc3Nc%i3gDBqfg^={VgtAX}n=McW5`DO*ZulHM<d&n4X_4Rn!=Z2OiVRfxw`(O>-ld8p+tM0r<{pO_7J;6Gj-#~dwhQBzJZ=dp3O;U#G>u`NjYb*2Ml4BVEIxNgHd>YaN#vbs{pN2&<{?(`9?3w@b%TO9FzEB_Hco-1+5kP2nl<LOe3JC22xM4WsI3mP+07B;jLdSB5DH_Ew1`yf@5ZW6&651O&m}4q<1X$O4TYTe6fG2n=v?ufk)H#8}4?GIm4_ee1$PvKd1@?y)JQmsudNeQ=eU9hI<A?&Ug^q%bMNAOKL~tPVL})L}xhvMd73(1MLXJ?5C&AIssT`9z62N1j6H)g<a42*FViLjr&~aFg8DMYd`5Ym59)f3acqU@zfhR$);F!jd366%&hF%G_LC<2^o|p;tfu0Hd1ULkGCEi^Co&uePyo<o0&^d_90!KqHLd@e}f9NEv{St5(w2XE#I1qX%Vq|at^fHb}j#c0o=w!UR3>*plG-A@gk3y$lj8B1W(6gDgXXC+RpwsZ~Y_KnMF2{6^#o%!0bi}Oz$3V|z+S!-`_Jv-IcjtorpqFzz#_<ezI`nGf%m7D1XQaEh`nvtoU+cerinwe{f3&S{ny+2sn-lrv@Zb{8NcRxuh#x9fR?ay`oL=@9QUh-R'

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
