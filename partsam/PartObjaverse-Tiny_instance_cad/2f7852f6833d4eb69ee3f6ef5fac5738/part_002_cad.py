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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2f7852f6833d4eb69ee3f6ef5fac5738/part_002.stl', 'relative_path': '2f7852f6833d4eb69ee3f6ef5fac5738/part_002.stl', 'source_sha256': 'f01bf9951fd33a310217a59f29ca06dd417b3d0e7faf7f5da00b01e6eef20e23', 'input_faces': 84, 'input_vertices': 59, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17010530829429626, -0.5, -0.08875124156475067], [-0.049576688557863235, 0.004750549793243408, 0.11151005327701569]]}
GEOMETRY_BASE85 = 'c$}qH3v3is6n(p0wxwO#f~AyC%NA<4r9WH>v{meaLPVh128=-?-4(V4A#L3SlmI%$1WAZ|EEqzfp-^gCDpsgiKGG>@!5=|EJ{4qxQAv;lL#puy&O7g{%o<IM&gSNvIdkv3_r3e(&3b3V*iwYLGR1(owYE6B5YikXMJx{lmoAzg2o=`Wuds+@=<<qSL&YPrymKvLxmf915D3i=y2_lc`>IP^`A%1LU2tj8Ut3idTo91@H2;!Nz|cbr{q+IkK4*MszH?k|zH_znzh3c13A(lCgDwNZ<<`$7dak+~%MJ7`Y=ABwNz~d)JER^SSPNZGTJ#0{Z=T#Db$w2i(r@2?332(4@0Ggdm>oTiwPdSVcUJUWH0vTZ<9+y_oBA2>%9L$*Zn=F7_{6KIQ(R1Y0r9Cl(DmlFGkAV^$xh(U4bXjC51fVnjgOzh__tm;X0AsxpM4GU*!Z&23!6I;zxebf>F+F`3EjE55Os>hUvI$k(gf(9XY)=#KlQts*OCX1;(m1&@_Js%ZIZbC()4a~UeECOeP&(z(eb5O7mjOsl>hhZ4$JX9{*%x>Ims6g*BRG{`L~3W-sHgg>(d_Ul>Xa;JzePU9G~j%f%JXQv)_a+yvssZm)vz5(Z^d4E4|C{A>t<d(vH4wOogsz9Y^1V?Z#X1-?Qcj?t9&*vEF@+Em*g*bMK)(yX_pt>08}|ya7$=-OCPO{uM2#N9@^o7<y$>FY+|TG+;eve{u+Qchp}{c`5_&AD#wXA5nE&&7)&7?#K3EToJa{ApY{rR^W@-N<aGDDU3I<t{M4$YgPU3i&g6rN`>x>-wHjP*sJz=#+u!#uI146O%>R0`mTd*h@a(F{uevX!~fG?;qTL~y^H5H2?vqC@|n%Rt2_6b`>R)X?l<e&^rO9IJzO$ZJ=aD)iuteVTZ#MW-@FsGpBpc!zAvbS?)j-3`_|_@v>)rxJhKDi&-Y;8YOC^gp^snr_ae{2p=w`UzqbK#i@$x_{2u8?rfft0tL^RZ=egl*yWR%f5^6Ws<4aoq2KK`PLF(SgYW=HTM?I4YpzHo5^?p6()-cYT9Hp;00^L(|1^dTmw<w+Gk2YyXGv13G>-U)7J8kB%Er|2hKo6g9Qs;)fYy;|9*Qok7?}F+}c>%^3Q*Z5#TF?3w&m%tE-HQ9jxpd~KYG6%MtJz<h_feZ!kG$6reS7+oEvTR8m8d(hzRMf+6<NDBGrrztWHzk7@fE4|n?4~@L|MeY|AZ_m{#T!nlH&jU2^lVAk@9mVjOr9768n=UlE={`w-SevTgiveBzF_@$=&2-#Bt;!iKB?)$VZW95=+T5$+Kya-%XReggBPGgnR<=9`Xs~g~VL)Lh>BqUF13B18I_5h%w|AavQN9xs5!Y=pc_LPcro&iI!}dSF&lo$y|eE_9n6>iCnWp_9?Q4aa`k(<aVN!+)gftL&Tj+@)Vln1w=P_0r^B?8F{3yk{214Vc2+@<ilu^ClCjdrxUY?gUPeVUBnFX4CZjris)O!e397k96OzS3~?Cw81ht_<O7Ha<dOO$&oivpun~q0BF54rPa_tSr;$f;6`Sgj+)2zMcao1Ljv$ZZ8%-NT-$BeBiH$XlAIqA(Gc4AWn1A}qd*{;RMvnRe{MX3nW6m5o%^2&?L(e;-AO0;{jo;G-{vda}_yaa&KjH'

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
