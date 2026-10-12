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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/45adf40fce0a4690878d1c23c95f8477/part_003.stl', 'relative_path': '45adf40fce0a4690878d1c23c95f8477/part_003.stl', 'source_sha256': '2ffb4fc453eda0b33b7d99fabef0b1f1cda470014bb4847a9030a9f97f30eab2', 'input_faces': 100, 'input_vertices': 86, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08150288462638855, -0.0015699565410614014, -0.05323602259159088], [-0.014651387929916382, 0.010538071393966675, -0.01461193896830082]]}
GEOMETRY_BASE85 = 'c$}q|c~F#f7{_1al0!j2Qc_&dxD@12<kST`&{bGjFtLOsK*a-*MF!7SMZ?JhZ}SQj4F!zQ8uP#%Q!CSSnx;QY8*;MDK?ZGVG%efr`F>4lYNn}o=AG~7{mjF&zvF%1dC}`^?YtBmev0A9-Sq0NilUybikDJeSXx$;UuX&|E?HosxQkbhr@1LDYl1%8Mk!Yo1r`*V@=F8bG=T}zVgd(g0;kO_Ei26{&YfFYP^kLRd9zK0R&Sb-S5j!b4vL8$q=^b1q*<c*uZOdB2<F@y$Ihr@>8O2egf+A`+SaPq=8p^D-TUXM-g0#BR=Hjg2Cwm$p?W1QNxZpw>rwdHSET;plilLa6~pVRr%C^%JH#u7M0n%tbEIC|3-#@$X7QHknX0cjnzc`SaV~sQuYA>ORz<+iPk?XzYL@EFSMTo?zpp#Id;UBbXY79Q%4x^<&|jA%{nsZPkb2#dCX6RJSNb##6tB!|hwoU4`8IYzeacmM_kAVOXX1%kxo$iJ-_*NI>g#jhPo6&_sWls99nS4}N3I(_gja3`si|>W-PvFLp+MHB;!XIIyWqorl6BJ_m<r!>Cj9ZqCe<5jUEp&D!lzy>mp(5aJSf+Xg6pvkQ*vaSCzl?Q>q#1T<>7Gg4n^=a&hWQ)$$Dx(je#H572fPKM$OhW5%8w(4@*vVlixM|{B50FM}Gi+d({HzZ)<{Y9*6PP=rW{#@6)J@Pk>h@JE&=iUID){0RF-G3aP&o2H)%lZ}B$BJ{dIdA&&4>iHqfT9ZzDM?&J4kU(!d)zFU$opP9+<sYQ!q-P-P;kBt`IT%naLyAFRZ3cj^<sq}9tgRhEU{pBo4r(F2t3wuzXFXL>j`Vr&Xa|+(*n=SL5x)JL$;0WuFi?6ZQV*E>M;Vs)U)zq5r!(ZD$e`}PigHzSvPX5$qW|?oxZurOz@XEab;>+yoJNeuFWM104p73?Ex1)c$+z&M^Umxh?t9Q<qb$E0W{>$m`<~c=DZ@LE`o&$e;*+Ti<M=rQOt1{ths*G6wAo$@)toM0c`UGdgpNnMw^=aZaRl?s7g)ccS^R1b`1^!h>cxAh{%<Js0@W+1JCb@a$a;b0iz`l(C0^Z!1B>VF8c|7<DeBG86GT&|c;b&}z*ZNP8`h|nBkL|1B8)7Tvck2xB$FkuqlhS0r{BOX=>EMk4Qm^Q3u)n|ia6F4sq<_>}KEFNSUFTvv83*9oZ{hu|%y`(M#+|;{_tfj~u7NUN?b}iC-!#FGoF(gKxqJwImET4@*ADW2vt+npADjEYhiAz1s9Em`@9GI}xmGOoj{fkLCmYZwW{K1X#KD)h!RxOSs=l=`6Tb2aeA8`==T0U3#^w!N=PBYdo8a5);4PjqFXQDF_<}<EH&W$(Yx2Xsw@qT7Q&_jhL*Vb&!7IKRxgSF6;Y)w1mVD5GeHr@^{G}c6%KM?RFWG#rH7tjJym_V6`_6{HHW1#N5}~H%d<XmqPxyvqQg2-Cf%_q-WIg(y?IC@3yagX)fHz*0@o3WDh5v5nIy^5GGOwD*c-#+bY~ZUeER+808V;S&clw&?7++xux3})7^>ng+%}mRC?o&pUvfa$T|CA{j@~=K+BErM}=eLY=Z|fLdu%4bw53(n@8`G8CjjVo&*)biNu4G5D3$q8=h3v-cNp>T9GhZZollw3=<UVA7=0LJPIhZ+u986ARW{}m?lM~7D%rtU5IhHw|97`U?97i5T9?DE54<$!2N0Xz-5zLX~2=ZWNGI=mLl$k;fC5JIbk;BO0%rWF}awKysIg&htsUr^|M>8joqscMMbaD(ijyaJWM^0cG$O+`(%uModvX+@eRx^pLC5JEvkweJ+nSSK{<bKS)<bGryW^b|&*^B8(_9Ay@b|ZHuJ2AVGoyhjev**X2r^;Ov9BSGy?Z`G{Tc#t~mh8ZEAv=(rnQmlfvOCk8>`v~*>_hHF_GS8$eaQou!Q=ttAZ8+2&3JMUIglAk4kQOKhmixwFIi8$&Zdi(?LYnN`0OyN3)bl$$-n+(=hyV}fBCt!*PkzKz0TeNo6<#@rw&ZrUF8pcm))2'

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
