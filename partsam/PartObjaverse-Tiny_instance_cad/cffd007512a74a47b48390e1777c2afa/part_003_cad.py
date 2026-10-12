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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cffd007512a74a47b48390e1777c2afa/part_003.stl', 'relative_path': 'cffd007512a74a47b48390e1777c2afa/part_003.stl', 'source_sha256': '21ce20d38e1f0427e2142693cd07ead882be5828fb8202989e864d20176dfa05', 'input_faces': 138, 'input_vertices': 88, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3889009952545166, 0.13922730088233948, 0.40573033690452576], [-0.37281036376953125, 0.16215309500694275, 0.4233330488204956]]}
GEOMETRY_BASE85 = 'c$}q}Urbw79LH}d$e_@{%32v4UjBAKp>!Rt8w?6_6e)!QLn9AT!b-Mi*nn+uIt|1Jeeh3|7|pW9CipOox@78uiHTrlGLvNw!^qqW!JsB1W(Jc*G-P^yJ>Prb9FK|7OMdx&_@uq(&pr2^3(>GOHBaM5kv8}KTlSevnnsnS<!PtlV<(Od#m8$#j-R$@IZ024kyD+0k?3O<?UeS6`*3`GXw1D&cQ*_N+#cOMd~EE**x<;(v9ZH(@~wkUj>nlFKQeec&VJt+2zYdVg-3r@|F1_T^<j4D#^=<fk=e^lEMsSW`?g8pCzf2dl78VE?(N-Q(C>@S#c!&-{{6e$FMXZ#!B_LSAALgU7w=4SfA=c)%PX_Vc85mQe(gN>YhMZN&RlCz`rvC<xwl*q+D&}fs`Rn5SGae~a9?yY*>14^q|ztS&WaxWOneei`q+E3+<QM3&J&yNQ~JbbpK|ZNB#bNOC{y~y&fDDYy(o+;m|3CpGkrgC-}nLd{_Dwh_3qPZpZf;)?H7b`X{)tre`JCC-gkuaOuRIp^s%{%+&})dFb|6h^-3R{oa6q?>*D#RFALt7pNR&C+Lx?x|H8}SI;nFieX#O(?x$W9uWw1A(kB{LxSyVs)=!nv2m62E{-dYGaXo*X`;`H~YfsG!ex~fktgucbKhd!)`a8ey&--0UpYW`T{+xra!)@9v!B4sPIt<yxer^x*d3IQZ&j%e{d>wY$_~&a5s>j>dsGc{;oAcHYP+u3xo7bg(m-@O(-n{PdYV~@9|J!<#y|LaVi`47+l>+tsB6;(EdDEr7A7yXckJDS!_q*(k`~5<W`gtOG^Lg@Nw)%M`dGmR7$)<iDO5S`PUi))iyzVEJ-h4hAUVc7H-h4hUtj-JT!PqY(Z|)aA-ksk#E^|MUytyC!{HxHex!=j&*zfKw3+<ZwspQT5)OuTJ*W9lqZ|>LncihYG1Cmd^4@8BxAH6>Q$Lf7-#j(m@Z$HC>8(w`#CYK{p{pxdc_rH4e@%jJnyHDnB)`wlJs*n|6$}(^jxCFT!TmrryMQlgrfbC!!ZaOjxnFFTW2F?OIkquxcIEW%{L$-n`qhQKza2xnx6mbX{22<99L*M|?4-SBR$VxEfPOuN`MplB|;Buq~Oj!yp2k$`UgDE$IcYt$|>EK*&HZlvG4R#@&U?=9$g(7Z7wt?F)U(G1u{m2kFgn8MIA}&Pwz&?z>5Lpf`$9M{nx!^)@0Wuq$jlLEjo59U!o0$Hhp!fL{6mhD?*BhlBnW?R>Phw*Y6Xzi}f%CvyQ247QnJM5jRyI~v6mbSC2XZUY2HpzJN7-;aZ8+CvRGPMa-=w4O>F}vYD>xNwjNPiOAH)`92H5ByvCgWPl^0nJrrZOj+z0l8A4L%#L=hiA?g1YFH=&5@kk#Nium?q4iYx|~f{l4A##|O-4948*7@GrZjL{4BqTd!|7pp#G1l$Mi)%df5GK`FX!(d}v5sWp0a~Wgr!rXMBJ>ni#9jp$ah&x$5gls`}fLp+gDB^Zx54as1MfITX-QZqS560JnwvF)~+Hg&YA3=74js6ioz^YcGEsqy*4T|_d6!BhEExsEKTT=3@|MV||^<#oAknj%#`J3W)yYZX%*tyKjHyTb$Zn-J!XOyLnb{*|6BU41W'

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
