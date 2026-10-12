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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/245af7dde0cd4add9f7e11db3bbbccba/part_007.stl', 'relative_path': '245af7dde0cd4add9f7e11db3bbbccba/part_007.stl', 'source_sha256': '0a7439972f6d9278565708eeb67142e1f3b5bd371bda42fa46ac7a7b9239e2b0', 'input_faces': 84, 'input_vertices': 66, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.03676441311836243, 0.4195583462715149, 0.21476849913597107], [0.04356081411242485, 0.4992331862449646, 0.2269868552684784]]}
GEOMETRY_BASE85 = 'c$}q{eNa?Y7{(6^F5g19K%&@1l7+wxSlsw_o3t{*p&CWy50{U{oQjVHrG}i=(xh?BLNEmfE|^S~DKddJm8=mC2#gp_DIhY1Qh&6WWHt>t?S0?JT$-9`>h9cme)pMopYxt`@1DC^8Ln;`!AF=_@u^wesun^yeS}7AHe1R!=9|lOMI|q}2!HaG<BslGxhgYjt&7+!DzydXvV4m+S<<E!CTe3OZDFyc+>%?gzSvS=R{TeEpD!~z{IX|rOU#bzNP{6p(nrNeTcrPbcqu*fe%ajV5ZkhIqe~rXln?bQYN|iOzWX5g)^rW|#*5YD3;Baf%JulQ9qd~w*nhHxd};TueTv$4C6jM#;e6Z80jd`!9oHX;;QZ~!IOp)KCh|W%%sJl2xjuG3`NoE5&S|_rzU}o!nfkP!=l)&KlP~4@l5ed`A%8sf64$TxlAY%(&r9d|Cb-PVF~z;l{S4GJQjYG}80Ac7lW+Y#n|x8(M8379m*#6MxYj^9Thlma#S@%km>^&5GLkQ?@8EHLYuWF3k8(^`wvjJ;=nl}hC%Z;y+zXT3f5^gm%AYz*zErV#hHni&$G-b%?(=qg4Xv9xi+mAqlh@Pd$35h$Oe4<gX1Z~ed{LUi<NmgR`|s+hruwh8U#8qQqd4ct=j7Y2l#nk!(!lF*+neius${=&4d=MWy+wV7t|H%5Tg>zQr1Vv)@3}rq^V#DuK>2OWTPZ(J#eIs(erMlWt>!+rearW~U}_W9w+&Oit!fMPBd6z*Z_Kz(zO+-#{Zx&VQGMuDu6Il1e$+ckD1YcA`Noe{@%pUR7g7DKCeC@q!0Vr_w@}?a`>^x<GIiIm?>)@(n)Ic4$@+|Px{f|dIpeMI-2bu~_Vc<qKl~}qKYoM#;wkclJ&yaY>#ri6tY?33D)%2!@dn+eoHows%i(_3h3%xeWtVx}HEEnb;P*D=oC+Cn{=Eq6YvhX)?&Ql$U8#Rbm$aAakFMo)d+r(TzxxOBZ7;sS&q+i%k2|YoAJq@mvcG&C=cj&AN7sY-{M;VvV}Gc;p6Xkl=I8d*&pa>7F9)bTQ%k<pYl7Fo-Y3(zy+^tK#LqZKKgRxa8~wgSd<EB^Sl&e64{D-%+hgBx{gMsji&h)|9+%W{{g|nl>g+FbpV?pYycTq@e{q!e2keLPJ0S<jKQo{ArN>*jeypASoq?myIpe|I?C<a5eRW?o`$o;X)KBLC?|az?IcHNL`}Q8LpE$ww4ejI`r~7$dE$rp`viL)EecFX{5_lh$SKc_p&&?3$q<+Ztb(t-cv%8n-#aYLGk~QOPSNi)m@g;6TD5t06ZC9A<^r}-#<+!7N|Ek-V@ULEVi3$JvRTuB*;UVSr;#4>px)huYPKQ1WP6ww!jo>t}0h$OlfOXIZ!8&jh^Z{@bI0C8#M}Wg{Dl9?o154mw=mM~!_kx4LK2Tq<4_F0t1*^aU>H=1DmbiN;>;`oQyMaBS_kcaYemE7L1J!`%fCHiPz=7aU=>6bOa5yvu91f0##(|^3vCt*pSg;<N4Az5_py}Wwa4IwnoC;2X8o(*w1gH+20A37@0xt$fLL<PD;6>0d@FMU+oC=3PC2$CME;Jads1JB9*dM9_`-9a`0agw-uo~<E^#pr>y`g?!FX(KjA9yx606GU801ko%f`h>Gp`qZc3>THg^`HKl-#x7Ka6A7||LZqrZgbAxv^%o?-1M?CX3?6c9G_B$?pJ0d{s4g^cR&'

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
