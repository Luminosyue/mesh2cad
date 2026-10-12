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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/94f6eb48b8fe44c69dba4ef04cea53b4/part_010.stl', 'relative_path': '94f6eb48b8fe44c69dba4ef04cea53b4/part_010.stl', 'source_sha256': '50a32ac6bcf9159aa8cddbf5a93222878268627adcf5db7db4853d6026be7d46', 'input_faces': 95, 'input_vertices': 67, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10927669703960419, 0.13932916522026062, -0.4835171401500702], [0.1092420145869255, 0.1595497578382492, 0.44048693776130676]]}
GEOMETRY_BASE85 = 'c$}q|Uu;ul7{<SDYjOV&Ss8<Ea2VJFT{i~p{?JWYFd<`gSWS%a!f+~dak^~S?oXC6SKM5pCWd5D@vec)8$!ej4P;wa)DjaKdZENbjr7*U3t3DI@j}n{o##FMPN|8}v%GnJd(yt&`+WUQPZ|!DS2&q*?O}b-|Cs#7!5FU^=46x6*!b|7XuN&&+_a5t5k9|2mrlJf7=FpdCfSU7HX1(@Q~iqCH`Jqg6m@7UHXe(No*s*xjdK4)WF#Kd{rIbqb5Z^O{axK2#e2Y`%qsu&s?tYDzyEM$o$Gh?Uj}ql#-?-YlAmmI3ttP>-j@B~pVPw6Cw8s{BtQS!$HwcY?q|6s<|=QL>Q6rPS3<VivQPb!3CEh;hx!Mn?pgY?iEoWQzjgd1{K&EE)^%r$b>Y*x$$?)ovQO)>#1E@-A6l19-O9@TBkO)Ka82}IeC}(p4{sk&$-btH2wxeui$2<?v8&?sOFO<2^NifQyDs_K1-Ic3E*txQ>D^^Hmo_$=ll|Z&kMI)%-)Ag7?dM!d<TCsG^`Y?7lb>Z}zc`n6@s%rbuJnQ{CHs^sAAfj9tn;4xa;aS8Q!Z`rBath);n_%)$VEQo%Afo^WATwI{pO;`W%fa?;N%Bc*)PsTeqqj)yK;Y;QyHAG%t`ye7B<%8KC};s_<gYt3Ff*SkoxCG)<l2uwO>8PK0I?;^bgvHt_0-sGoKRu$*2Coct-TsY8RJ9{&()(68#@M_<3FS&HbFq$v*9;c5*3W@#(&vJ+*4-Pv>M}IxG9d`^ol=UbW_WR^(DzPh698<=^^5<RYJPvG`4qE8qC^^-{S^-@LCc<Yd2)Yd$0U%Ec+epKV{Y^hd7b#Oqnve<YW``bMdFOuuLz@@bxQ|8Pe3X`cLf$Eu}2o!f~Qv$9`2Prm<;m6H2IzWKS&=Vagfe&~NWBl|Q@^8Ch%rN22(C@cGxdBT>b;NFHi3%^$|#;a0)3Jyi2M<6%(MOyk1IPCjZkH90H|N9Z>)n{ne%ME=J>;^YM_kf$gb<myQI&c;A32+s-61oLk3Em3b0p1F3geu@h@B!#PFxSK27QOcB<<hG|uY-E2P#4&R*QhAYyHK3Bp*S}{TfkhmgB!q)LpOtKpw-aL;A*fFx*hBUH$z*%&EQt33)~9!K@Wm`;7(`<xD)Jws$dnFIrr#wM6aVL&H<<&8~_LPItJ~9`oX<mTGx-c{OIMw{_wrn1a*Knfy+^x%b<2}8Q8{*i)#hc4z2*x8RJ|9b$}gMo6aZaI;fKs&NJsGXfrFEf6i`bD=XYDoV`#V*oW+1Xb;#6=4Y3mZGL|Dqc|Ue9tIx*cSC!?-QcI7N5RMOIrTw%!F}K^XeYP}+y?c4+rYb_yTH4__0VnLdT=eY23!k%Os{arR^}}Kr=JalD<M8;`A0<YJFQ=}@;e>+fik~%!y&u)#ZjjJy}<*DRsIH=VvVE'

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
