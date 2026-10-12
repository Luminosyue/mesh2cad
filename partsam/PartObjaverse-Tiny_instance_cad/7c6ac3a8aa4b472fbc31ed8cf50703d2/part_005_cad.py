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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7c6ac3a8aa4b472fbc31ed8cf50703d2/part_005.stl', 'relative_path': '7c6ac3a8aa4b472fbc31ed8cf50703d2/part_005.stl', 'source_sha256': '0b17a2989186a9d52f0401f5ab38e8144a7492aa1d9898b7cd8381f6251793c5', 'input_faces': 80, 'input_vertices': 82, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.3354088068008423, 0.17625407874584198, -0.23556239902973175], [0.33973556756973267, 0.269594669342041, -0.11050619930028915]]}
GEOMETRY_BASE85 = 'c$}q|4@^~69LEp;1d#*;{F`zS@?k#yJS0K|x&Gsi$RDSbt(6buQA#}pjC5#SHs|J~)Y)oI#fuB)%$3bjGn6YJ4;~NHX0~P4Yv#n-Tw7`CTI=55`9kNk+FIT1?EB%f^M3c-cYpVAUwLs*a4h3T0-G1Uxh6e~F>6GySXS?<-LPi0t1i{Oep3L8B5xf-xu^80lJaK*SUqd7Rl4d{*V<+)ww$VLn_aP0t*hNoTj5^0uC~%;`TUBP>s+R<d#Pf*%ltbzJHxKboNiaPDF5{cH<zG2{n{6KW;$Qr*=?oTu(iKk@Oo)4dDfXCdG=z0$4c$@qdw6aZ)_s(pOq|mW#@77#{4UNqW7Q7>!Etx54}>IdmnLsw^;UBNxih*qyxR8*K$APesO<~w9dc`FI`vWD9IbQPLo%1=6fu!7<>78u6})y>NUq3qBk}~UZVQl4eg>=G7Gq0>o_NR^@D2i>YE;^j&`bvyz;qA^32o8ePN?iUvrPYOm%Xa&Pwyc=aJX%?`^ZZs_f(QmyP1*y?*n&<&8`5S!?LJoUMZ$qGv_#lUIJ&#=W+m`(y3=z9+rcFZs<6c%S%6C9l1`l;7V_pHK8g$35N;4G*OG>a|k3zs^(jk~dsu2I#t8`LWaT{`3RfFF8VWoC}J4qSxB|{Jh0?`$Vs7byI!i;v~tlUk;O3m)(`>s6pS5H=b*eykE`Y>sffbi@xXYP^ZgJ^Ys_pUeW72+|-9m_x6ciZMs2TPn%5Mxx1OKvvN6~|5kgi=vno*eEzaKJ)&3b&rsiL@iku2YiX;v&$UbQjXgJbpWi$v)mP$flXos!?UCxQsOqEZ9=I;mVa<2QYxOab*FqY6;&U`SKkrNK?|s@W&7V@(Pv;38LtcOPW4_K45!AQF_5wrl5h>j7?`s!58(Yfz{Ln#ZzUHeWud9vcM6brLBhPN-O7r#9!{q%n4ynF+^&y{Mm2*~FPfa2{ch0Gc>A5osKH)y+H+n9VNMFC`^<$YHsn6lnjz;qO;Isj$j^hmXyDm%fjiWKVKdVb5?_agHM|$pt>esgLK9AbS`}tSywTBMAPcCoi6TQ)D=ljDMqeJxSX*YSj`FY7Z>#uRYyN&i4cH|_#FZ)`lzViLgUeOy@w$O8=OzoiO+PUHspFd{;^`Tyu?-jk85>9<$d^UJN^m^HS^2&p4^gL=|r}=dqYUTU<tXF$Q@2^UxzEu)W^oZU#cAWRKchDnxB{rA(R{v?d<c*TO+#lUVee2(TmansHuC%`m`}mFIhxX4Q&$2J^|C=il$g8u@Nqx@VsWU`B)aS-m(MEf@^tN%KYsYyt*qmyPk>=Y*RfX`XVM*&4%D;crSd;nhUNzGH_p8Pza}DXtdM#pXra2xlhXWY_j=&rTvK;IHFGXg6mx43RF~%HEnj;#S1&#(sA)f$8fg_Qb;7IUjWCnONI0iW%90QI+&I8ARW05L27CZ^L5IhN-fGhwffYXrq;52Y5atSyUoPsO{r-1Fq#b7&l2C@h|13VpB2%ZkMAs2yd;3VV%a1uBXnFme;E6BNE1sspe1;>LYB6GkK!4ohno`Wm{TUiR81D=gxaS3u3xCESy90$$@k7fL@G5|Ra8~_ePjt2*VgOHDcgTTSa$>3mc2yzNI1Uv#c6+8kQihK+l3Jya~1BZb}B9p-*!Qsfq!R5sPfw4jV^i${0L$kgB>4(o>KPhip;wRl^t>I0qyg0<VCi9C6WHn~qrnCG3kiQol'

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
