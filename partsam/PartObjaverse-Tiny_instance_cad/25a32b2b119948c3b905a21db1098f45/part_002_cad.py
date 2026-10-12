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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/25a32b2b119948c3b905a21db1098f45/part_002.stl', 'relative_path': '25a32b2b119948c3b905a21db1098f45/part_002.stl', 'source_sha256': '3d1f6ec5ef26bf8faadd65c88b37502c00f4199c81f77d5d773844924957f604', 'input_faces': 66, 'input_vertices': 50, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.23853130638599396, -0.4132537543773651, 0.4674358665943146], [0.25939372181892395, -0.38725680112838745, 0.48975759744644165]]}
GEOMETRY_BASE85 = 'c$}q{YfPI}7{^bc6)2@LR_=qng-W?}g*nzN3)!ksmJD4A0cFNzt*i*faA_xz$Y%9};^JZ=Gtp!-bs6$SgC_I7Wer)(mLS6~Q&A>{Xw(qQ5;iXz>ia(b|Fkul7=4qI=YM|Z;klf1IBB3I-Rw~Koa$6g`@sf_QpT_;hZ+h;_V;#$qu#!OVUx-gZhSZF*shMd1G`OXNImA>7mjvC+*>twQ}-6PM{{@gNA^cTeS7;O`@#lq4m}(V>pa>M8VKw2>dg%vZBva$JD~m7&#IRY-#9w6UAMvf(z!E6O=(YDGUf}-&k0w7V&Spt^TJ~fye@p9eC0EP$0xkPgFR=3CuWv~Ytx=D#n1i?{6~EfXJPk2@z=Jlr0`(-=g52ZN5rvBN}O2k>bx=czm;)8_@o{6{8op0#tVhV9TVd3Z|Ib~e&4Mr{>oJ=Tsyi=c<_2F@-7Wa9DiY(aP`4CiIeF0Wj=+!ut&Ih>Sy8F@ebks6YZ$Sd{N>g-nk!n_f#YA^KSIp`5^qaee|j1eJ_f<Wxep9Jty3Mau)ojLG<<bJ(4##-Y)g4XPy-vJ9a*W$6p>pUu}KJyE2G+hL0j|v>yFlt`z@Z`#AERF2H$ZxUm1l6W}e2*w1TMq+j*WYskBNJK~IJ@L!n(&m2zi_rL$9@P#uG@z-oKxF`3W0zZ_C{q$6zuc0}_X<CwfNL-AFziM4XUq`+Z9{>0PxMwLPZ@i=x=R18B{EJoaua~8s#8<1>&#EQdtH>_gleg8Z)Z+`FuYywHiAsxbHF5;^;qc}8WFEh|3H9%FqMjY4DO`J{9QWVp5*{qGp&su5&bP#q!V}HY*q<q{@YoNy|JtM9OWyd?4XEedW5{dSiGHs%f<KZg^(Ri=fxMq=M*R9##J8`*dA-{K|2sQzUVTOI4|WRo|5^wCYrUw`)P?=o*$-aeK%7PJ;HzHY3u`~bJ~Z|s{^%6?-QmZ5n>z$Pbr<S)hVcLU<YDlk12~sA?C9&;m%#Jdkax@JOWOk}uWi%F`LP$%l`=+_{@QkjlAc-v8s823_fKta<G*@peZK$w)UMNODAh+U?akC>`l!^$8rl--Jg#NZuAw%#(NY$5Cg&D16Ky)RnQMyHM4iF4G+ITS&9$3o)2Op)ZTcwEN4`EPsBKAeqc<0Ie$w3N{}$>}&fWT`Wq-Bo-_Yy1mPcDg?ciD#Z639Qz2#76ac(6u(^{yl?9EPX=DdI`n>K^m$+aTdZ0Z`WRnQhu*Ranz>WZYfi~C^oyMaA#ATx9W*Nnca_2Ff&UNS>#TyxN_r`FhKF|~v9wPaS>9O^=@*=eoRh3vDO+Rk|unUl7Fx{7^zsGXeGlhx7IP}j5Pjrs_*n9>~S|MU~;&o3qyH~9zEU;i@oIY|D?K0VeSk3*ovV%%f>VyCG=-QFg?zXMCu^*8'

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
