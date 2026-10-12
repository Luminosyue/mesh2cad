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

PART_NAME = 'part_020'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cbb199ae1edf41c6898c997ae785c4db/part_020.stl', 'relative_path': 'cbb199ae1edf41c6898c997ae785c4db/part_020.stl', 'source_sha256': '181009eb6a429732a184748657ef3650a24275be57c92e537162ba2cb07392a3', 'input_faces': 136, 'input_vertices': 124, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4874613583087921, -0.28624871373176575, -0.17392763495445251], [0.13957470655441284, 0.09645505249500275, 0.01565416343510151]]}
GEOMETRY_BASE85 = 'c$}?R?Nd}`9DM*4MKn;%VzaIYEa1i}FJ@+eU??o;f>B_|i?ArZ0PWHOK{NM*PWGuBYbu)xr_9D|%xbEMX56NiPfZ`1W}0%E_|#v~RKI8UJh!`NZ!=BPGH1@&^E=P)KKHlFy<EbfoMlBS_1di7d};nYD_<#%d{w04k?7Rea3oeeJ~^AE3X;Bl8NP6!yCdA2rQ&MNKN5)zNBz4j|L)P9{($8lorq3FhsFmcq9YOQw+x+%MZ}LCADWEF`-<%~bpflkGGIMz{l{0H-pcu!UvFyut@C@$iTzhUxar{!p8fs0+qbjlFKSk8>G?+EpG)N%pIy9_<hF}%H3%;>HGkvf+j|zjPV+-4f3V|^57Yeily6<meZIlvCk}r0wpV}SbN@s*<#Yc;XUbRHzxmQ9$^Px}^!@Bj`GdZh&a`~XjZZ!E`%=CtPUY=$)1K#>;iHf773R<wpguGo<MVvjH}i3Pnvdhte4OKAJ_+h?o4Ij+ny1r;=IP{Vo=%?Tsh;`vXRo;#pXX+L-jCCV_OoFB`D60?ekJ%-l5xK5E1a+Kmo8uV(kpL#&NtThK2I{`jc-vt5nR3Kl{Y@;)yEajxxWwW+myElK05D}H$LZ8<cABM{o!ZiCrV%T%)`&f&!2hSGY_Bh{QY$HPv1|=UiAFD*jJS2&x?JF@;p!WZOZd}*w4t*eAwqaU!U3MJYP@P&*)F{cg~mQzwpMZuQYgl-^jNqpYi#cJoQ)a-g>RU<MU--QJz0v_AScu?-%<v<@tQs=RE&@vCny)kJF##llW=FCH<bSZ|p0|^E}z-JkOJTi}HMZW8dWM7rMVl&Y>^wntML%+myGDHeL7f8%N-m;eG_)s=M*Ndv3;07=QlSRWCm=ede9C{nV#?t2DiT#{Janlkcad5AIV-bX?=Bne^jk+-FUHbD!lo@ZT*j{^C7n@|}6Y&zLj(j5)*4m^1v0Ig{_q+3bhsY>vxwHv8l`n?5{e@|`)G{yb;XpXY4y?m36ko-Vq-YmF?ekV6Yr$<xK?kn7PxoBCzg`_W>o?%zFH)b98n9xYV1APbxWU8qk@a5vb3z9)H#O05I?piQk1ybgLZ*80H3t~EYneDDj=$3hPa>$TS7(wi*+-wv&@9(B#R&>N9i4bFqk1+M_-K^Gvm9=s9S>^C3026~g=F2QZ!wa{z8`QWwC#mM=<o1jYt<$@jHozP_hKk9zeN>S69`@r`@>w1OYFt`u;alsMv&|C>^YUN;aj3ZcE39fLhsYIp{emVN|p+_IqYuzSj7xaJ+L-(Q{0(U@%pxeOh&^=h&>)Nx{C78#f;2!A5P~QSBgEqAi@D}J^tStkVy4I8-QwF~TeR|NtoR8Kmg8hOp_z~!Rf>zX9QENd>XF9>%(Axxcg5BV~(Ax#|sMn*m4K<y45d1Lou;92L3Z90J31$Q%;4$bZGBNNBw7#s}A=m)E6MC6orJxbq1g)_Lb<NA6n~_-sUI`r#)ChKgAA-JDP>XskY5~-A<^ga6bd{i5Z~)u|eNb>nuoWDHHnl47R_H@m8w6Lo)&!9W!mmP~F7)Wadae5fqk_}mC!xm$alrui81w*iKX?@SG}exT<Iod=Nx>j^2zpBJgdhSw3O#}Mli(?6-ES7h)O-SZPVkiA6!;|c3GgxSN$5Cov*0=Ca40LgDCeL4_4fD6);FEBf5h?1^xLX?Wxq6XZnELf^5m^GTYmJ3&g!eU`U}7tgK_'

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
