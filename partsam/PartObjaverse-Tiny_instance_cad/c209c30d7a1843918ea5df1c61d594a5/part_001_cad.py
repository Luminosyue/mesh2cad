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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/c209c30d7a1843918ea5df1c61d594a5/part_001.stl', 'relative_path': 'c209c30d7a1843918ea5df1c61d594a5/part_001.stl', 'source_sha256': 'a5018164b5191ba9d7bdfca03fd94084b2ee24ce115248c40836eb8d05f8b56a', 'input_faces': 128, 'input_vertices': 108, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.25734734535217285, -0.5000002384185791, -0.25273412466049194], [0.24055252969264984, 0.3164389729499817, 0.2503446340560913]]}
GEOMETRY_BASE85 = 'c$}qJeN2^A9DXl&1&s>qCV>%`3a-Y@6i~p(d;7xbBHlm(tb{9Egd)KUBdfLeqs{uSY0H{r%+>l>%Tz>}YuqLFp#w3g&9NC<ZT->QTwi}wu72md&v`ri&fC`N-JU(q@8RL_zUTbTd)^U^q|WnM_Elg7_g$PBT4-4U8J5o)h$s5H+Twl7xAi{du`;DEF2%cR8`ejgJ=TErOrSm9*OmyZ@dv6pDgr@&pra?zpNMU1=}EN5g<l=(?u(P(*BR@LQ@wQMii)7WbXm~<tp7h=@-AXKrp5%n`N=nufB0@>%+0?T83}2A>yB?{-13f(d~##m8CmcD%pT|bp2K5q{-!?;>G|Zl*<ZQk9iQd>MOm(S$7lJWgKwRczSUbVbBot~EI9nq3HyG2JbT>LPpm#J#tA?D)2OHiEo)Z(z0*PY{M;XW+dHM_t^Pk}-15p-dH<7{$K2-4@bO&A=ksRxEYIi7@L8VE+wAZYM<suK&c2`NtTV2@Z+tSO`)l7g=bBeO%ZK;vb<I0I^8R06JtFJ2fny>4xwx;M3x0Ul#FSg!@mW6Un|94RJ|F+Z@N`I<xA3Ra!*2V|@Uf4S&-b0-BR{nLq`WWd(kt&so{Y%a@b@2(_t{!LZu=E4+x~AgvNrt64`trkb?Kn2FSH+${6U>vb3be3qdECg@uMNPyz-Gx&Og6b?uVx5?Ds_U{S&VK?$<xp{qPG@C*AUnkGyrca!{^U?&b--uM8i3l?)_yhTQIl`|5t+8~4L~<OkzFzZY_uPs7LjI6j+C!$*Gh`Gma=Y<&$M>pPU!Z~MG|xR3q`SN(4LY~L9^_J#8KzB7E5=ljm^`S@(#C9C(?{j2s@_xOmb|7E~Fzu-Iji{%|3`PNk}hvj^;_o3mVuN<Gf4-KE?`TNlD)%){{)5G$)*g0bOm^bC~bHwmjo}VLz&+^7OGV%Qp+1Knm<-R%}mCw&p?mOpi+b^S%+4*kxINxV4ADD2RH}0$Ff^W<l_gUVUH}12%F>l?cCf)kk@X?>j=lyK>A|IXebvx0MJ32U@rj)RNzHU2W+NZ5B#iiK&)3&SZ-+kJa{O?cOe7c7l2={>R*7S|21+UZeO{fLmr|Epu`4~g!Qo>3?8Mp*`4WWWi2`+~&L9PN^uIW<LrN}B>hFXoQbP4Jbj3IO};R-?!oB<scYf1=#Tc9(LYX!Gxx)^mavMm@Z1LI{NEA%SD^@P>nJZOP>{9JGybRKf`;5z6uf@mEd_!><wL@hX5(`l&FkQF+eFwYVVYO@!5F<}wmT5uM$7r8~?EKR4QPDfVh1*p}yN_$azF^15Mgog<2;5JQfLM?c!rW;W=A}e$O!B40L->d1HQ479b(*>vtkQKU#u#wOVZh-C}Y$3$KG3W;5wt!=rZbIFJtkTV>)woJGpl-kzLgx~$BP;>uKtD*>K!}2Cp>vSi0It<^F6vxlm0p5cjjMDH>Ku$AwCGXMld6|RZ;D<PeJJ`&^quH6(SzAo$40DMJJxV3)};XJP>nSa^S_L63*k=iUC_%3w-Tzrw?p4XSV6c0ycW8K@Bm>wI0F4Rp^NYsxDz^pTo<@g(>17TknO}+5sVi>R_GMVzEZ&+=%s`rLI7L{?Ln>xT&U?3)G5doVk{5F^B^nq)r2bvnc%CSHxnKqJPLjoIvVk$_)`DrUo(GSgYpLTf7I~boO|r)zj=Yiat^_0#5>=9s1$2E@oVC3Vf_WJ-4;I'

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
