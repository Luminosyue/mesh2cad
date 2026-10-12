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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/00790c705e4c4a1fbc0af9bf5c9e9525/part_002.stl', 'relative_path': '00790c705e4c4a1fbc0af9bf5c9e9525/part_002.stl', 'source_sha256': '869c0f4c6bdd3f6c64ab271fe4673ee6f79cb5e9f6dde9df05c20f468b2e6565', 'input_faces': 96, 'input_vertices': 98, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15659062564373016, -0.2045098841190338, 0.1580551117658615], [-0.1554591953754425, -0.2029103934764862, 0.15967649221420288]]}
GEOMETRY_BASE85 = 'c$}q|YfKbZ7>3X8a&eIgDniww!$p?`L=cOpTxJD9MQ{aHP^-*}i{cf5+M6U}(xm-i+BE&4e;}h0V`AgAO|_|Z3`V1A(l**Qnp!t$wbonJ)`}OjJM+F+rfHL=on-Pp`||B~zH`oZhFNcgBP>qfN)oRwE=}9-6vDWpMV#0eXl-w9476pfYkAEkVol$;`t|)PU!`}UO>7izxRwXn8e3h{Bv(OGzAIC5HLY)LZ}qQhSl_xlVEASJHEn^A-?q}<5(s@xo0^{~<+?Ma4(Y#MQK1qP_uvzs8Ty_$W2lr`e4^N>EfIe3fF1rl+4R++@b&FaPMd$<U1<8jD^aE|_l249s<Q<CIr!?m$7a0fC@_8Hb^2|QX1wsvG<~Vx-}1<emkv!gecc9MtbK@ai{Oh6C;ZL_rmu{Lul5c?o$aV!KQzPiW%}Zp19hH9oyrBqcZ6fU*{p}YmS;o!w;qeHCSzQ^nRV`jFQ;HV)qKQjTj47On6G}c40X<fFI7H8p6|HMIm|!Yi9DNTVZQYBv%|1%v0l`ZLH~X)@(jW{YgZ$Y|3mDTd;<AJ3w*hnKKEB%1z+R5)IQ{qE=9o4MZDUKdFeagi}ORxdgL0^Beq6Z_C@y;VP3V&6B&>C57uD)XGB=)5lPrDWly+e-?gvNpTRBRmU(G0*hfu*udRr~y5%6h^m&+NomEdM>f9S<>9^oP&TArkJ$@wec<K=Uz+u^6xeI*~+~%<KxpWHksO|9ei}5@c3lKltVd*O|sT}z?*e&Nv9fm$plI@m$R<EHS<a0L6>(OY_S9UEzd?$T3>JNTek8#s&mh-N^gFMnmo8?^S$LFAar?8w0`M_M{Kl`)?`-gh8lnT_p557Jd_2}~#V_&M^%R9y(&xIwZ=jM~1f#*UwQiXXn!tZ~c=wDVM|H;0df#*Uw&i>yGU!IzX_1VY#!N-W_b4Gp>@!Ed)QbZE+pHVQcF8HD^3VBXfqn_=LkmoY$m%eF0pKOG$-Hk^4SG5?o8op#l9=#BKDEl5_zE_7}-;bjogbltbrC`5SHzNMn1Ju)r{J|f6@OQyit0atj#E*Fu!<W8~#rkw%-=%_H#Gk@*Be(#4BGTcDq8Q|9L%e?UKJu)?`Y1K1M>N8hFQ;NXKMtUtI`~=_&YgZ6`>t>Q9r^iuP=CO<`n&MuB{&zs2JDyCdk^ClCBxsj9Pu~k-$}swcQ57t5%@|I`dm4HeUb9vtKFk8?pxSjEeC%8^FdGJxEFszJyql3?^=QRu7<B3W<A}UZ}8Wif#+H(#JI}gyFCNXoiYmhqP`7Zp65b6lbg{eC+}F!i}J}b%s1hVrJtn)tb@AewxtiXY}WHKeEAmg%gQRm@4toh8J7k>eKqD=cGD8CY=bZRZ&=QST)z_QS#rZ#e>d|SyKe2<y_lEy;JRf!g%9!S=IfUJ(f6(5bKqzA{s|cO?0Upcyo!2K;VYgN#QT0?U$GCDtwH=RS5Qw=Ch9Clym$q^=12YF_FBZt@Rh6##9zX=ay)#o$&Ga$5%Rs3x4rg{c6=eiLm0Z9p|`yz|A1FL^AAEi)4zY!Yo7e?UiI?+_p9EpPz|F(_w&3B9z#tck0Ga0)5xi0H+3S}P0pgeNX{bXQm2!1$y2B^$WzFL)CzJT*+ZR2_K?e{HRLk#T;2xPQWujAeTiI4_EDFTedIc-Lark(r25GV$&08B<VECq>JqY{3&{24YU+G)HF-8~gJ)5_<XPl$Y8APhJd;{Uo=GmD&LNkOi>amLVsa5xCKr*XQ47e^$obT%<a}}-buu}RJc*h^o<z>3P9SHKGpXt1OmYTwJUN5xqNb2t<Z)DqJdT`9eSw@z9!nib9!pN7#*-7tqp8Emqsa->=g0}<5!6BC5#%^(Bsq>8ON}7Ml7~>k$V14{R69AE?4$}Zf1Qdbs*M~)9!zzR2a{u{;p7<d(9rFzu-W4r|MXM&&r3BDTYfnI^_$km?!a%}3VnR`5cXDt8*31nm|biLsoSVV`~ix&oeK'

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
