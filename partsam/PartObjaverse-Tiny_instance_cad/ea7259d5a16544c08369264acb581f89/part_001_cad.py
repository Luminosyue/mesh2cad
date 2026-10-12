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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ea7259d5a16544c08369264acb581f89/part_001.stl', 'relative_path': 'ea7259d5a16544c08369264acb581f89/part_001.stl', 'source_sha256': '1a9c3f36c8e33dbb2f0c3daf349b17d5e3c6bda8305b21136530a18633de905b', 'input_faces': 92, 'input_vertices': 75, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2811504006385803, -0.39630457758903503, -0.23873291909694672], [0.229460671544075, 0.39682960510253906, 0.2608587145805359]]}
GEOMETRY_BASE85 = 'c$}q|4Nz276vr>HASo*pgdidhMHUrtMHEGhr-&kE;Z$QzqKm)^8K`JDROVAtR7M)Vk};bW!w<&P7(Y-_Sw#sygYqLs)U~m)augX2M;q(D|2bQ0Q!`C1bLRg)zrF9g^X|RxJvM!uhao`FCtT#Uo(NgiK?ps3M1UyDDV&>^l`|)%U{<l4@B`OBPF?fDE928Axrrk2wkbPjPFA5QK`|v-hnS)jlXYg{+``O)sWS_+b96pB^Nl$<lF!M_oRuT<sQ5wA%D~>y%6#R&emcq))G3df>!jNHZ{DAz_jI98p|1AZV~MYtd`VaFa^42;Ys9sN$rqqAtl(->Z*cp9#C>|M<?buT_*?Ga%2lpYdA$Vu3USpx19il?%i!YC{U+2g)a^y?cd7*E*%?keYQk>txH3&wW$fB7b?)$``s%weRrub6xER5G&W;6l+|LHL8@HlQF(aZ>S4)c*jbFh11cxj`-}8t&9=}HYo4SB&*8)!9`{&I^k*|tbh&sE8+f(2B9OFHsz(vH>2ISXiyttLP2zA@9fNO<IXnavJxQL%f<GXL8J~t$-K>wvjk7N91>R;Piw+nfO=?LnzFgI@8g5wX>?1z3&+_Am(80Kw3$2}OYP<=;PkR9vNn7k9?x8+<yzTzI{S+w2Rf$_ZVmfy0^;ynJh!IjN4|Bj8sMdkS_)G2uU4fcoHwhrfMtJ{WgKm7<Uer?IZd^LC5in=lVF+a8=2~c}Dan-m8^JD2VjOKfA2CmPsn$Byx*Lo7;8Yh7(7pYHM4RLXHLM6t3wg~6dY91_s2DMe-I6tamzggXczAEk#PvQMj%iO<YBkKK3{ir==AH(;Ji@~*e>fch#e0c2#$OE@yo^35jG;g1zfeZ5%n*VQOkAs&ST8lo78R*Ay;?5b=DL)7<l4*ZhB3p?^Si#lHw2rp<ku*OAZEH{`yb4@hH}DjW_nQW;jH2sRZkEz@^~eMl#eBU7n9qG!iuw;|e`=SfH-ay12Upg`(0ZM=60c4y#yq}A^WeDZeVq1n7`RwT^Jd?{{9dPd$lH1U%q%+#p5P5`i>B*!oMxW8Js;;W@IE<bZa{wHJL11AM16<n0OGcn@H}(u;(d}CMEmpAiNtU4el`%-n!Z{Jow}H=_ii)I=fk+wnBQsKXTtlZXuk{sx38x<j`hr24{rkhh}Kv8I=B}7zZv)`&L2qkqs_Jp_pQ2oQw?~3el9gzt97+_=i|Oqf{ClW+VNbp?RGl?UP1N6fw$1N?cz$}Ui_S~zFrCLQ3h^5NY^FmbHUZ~_4VNI@c5*z>v4SDF>v(<dX8z0A>fwj?k6$6AMcY@6}V1ujku!|&5!0~16RU2gIk92b8LJ$?mJu7RB+`1zZY&-e~5KhNL=*e=kSF+;L2gQGdS-&9v{0L&qKxF4lb&wAMvmp+@ehZSIU{sx|EOgZzpak;yUKG{JQif-r^rW`eIX)K?psbl5cTqrpqf_hx*5<fBy>4i~Cov@S(B)`xPFeZy6bb^`(<BLPj^%9_&M8^px=&tI9rvwHs@ai&r^Uxt7!S<h&=>clr>{L%4?Sqh$<~(V5kcy-|j*zQnAt?2W9QS)*NiEa$OY%jtbN_vQLdZ{*y_HFVzv%PYia*0JnUWTeRmVpZ6uu#RT!;^Gy~6|Uv<X`H8VeWy?1JcVoM-d*S$Oo#!jL)e>T#LIAF^=5Bo9l+}D;=MWd=2}i4&v`u8cX~7DX0D<8kup+cbZ0fO50w!qBbjv!`%u>ItRr3g7|zFVt&x0eDziwgpUOUz^H8p#`@S*;$?#<D#9qJkd}Q=tjbm?M^<?eq;^R1v<62Jd!?_RFcX|Wo2Ckv|p)z{QNMIku`Li-2WCXD9#ks!>{eSFd*gwtrFd3s{B(fjQc~=>MGQwDc+3UX+JY;yW3icgX!&tkzc)_{gT2Al5xd+#G`VO3@k8^Vm@c5^nG=F|HebYVh1Lv<tKKU4RJ+eX8`s1ORKF$;Uy34=WQk!v>-vOzY(-8'

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
