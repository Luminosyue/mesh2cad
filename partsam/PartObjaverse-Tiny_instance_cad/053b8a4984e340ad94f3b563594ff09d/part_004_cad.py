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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/053b8a4984e340ad94f3b563594ff09d/part_004.stl', 'relative_path': '053b8a4984e340ad94f3b563594ff09d/part_004.stl', 'source_sha256': 'f6bd1ed364b0cda55470e7fdcc3077da0d9832124474cdb40a948480651648b9', 'input_faces': 138, 'input_vertices': 133, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.14442862570285797, -0.06384077668190002, -0.1677819937467575], [0.13756920397281647, 0.49999940395355225, 0.17094182968139648]]}
GEOMETRY_BASE85 = 'c$}qJdr%hF6~8=`8fc23;nm3c1Qd*j@s$V*CE7^P&j1D#VG%wA{X_&L8Xs(I%^$|`6*@Mgg-<AIHA#~ggQ(~lYmz3#iIbWp(b}b%q!Zf?ooSMhj;X!(+~3-7@7S44i*x4p+uwKYx#ym}d+x5DypYgQO#Y2!1-qm6-;7{PSOgozn!OE8wUyq+sde?6f><Q!;?Ke778T`tN`hE3+niM8ZLDlanyV!}Ts=D}RZFT~*U;2ZQCGgMp~@@t`4zrKFV`DuD(b!bIypTfBUQ^tN!7M$|Ks01JO!<5%bVvo>ZLcYWQm-HT5<&X(}vCq-P~DmRa{%=pDGck#l36^-72m6g#5pO|JYX2?dIQJzMJmEH<w<1g;3Rhvhx)hzqm%~*Ot?~{+3n8X?{g#Ykv9~U4Q=2S;9+yk@HTnDZbu3mvr`E9_4B58z7yj`ulA(uO1Xny4C&}#nF3w(qGlTo=E<zDo)NDD|ME*R<5f%@eI}N$!XUp?~Af->=EeW(n&XiI;7s|KSgn}^J!iBrw1$=cTnnVFqZu7R^v4qchK!`6;GqOn2Nt)?t7K=k2*-Vro_p4_m@)~UD4Ua-Q=&I-qlNSh9&otKFp;1Xuka{=~mV2e<1z&LsB0-UHZ3V9HF=cH?jkD|C!9wfjV0kM!G%k7sn`1Mc2ai^#<ztwV0DMZ_B5YkI_H+SG4XXshdasM7kCnO}eS*cFT^JY5ejC()F`%N&g*xm2o!SLppmWQts!0kUpAM(e1=Ox_|nzuX;%Ta**n8j!8L7aZ22}v81?<{H=eGZtjx07Mv{o&$)HuZ_?k4-`f*dAG=W2!GP}6$I<OH>kXkBzTZp#&hfp0y4HSFUWfW=U8dsiAG%8GG!%csS3>z%pByFKZrecjmwj}D?x!C*d#{|X*?~sdx4PnQP3<~OaTR}ip-1l9Q-dc+FE6HjWrerDL~#_|eme3cihJoK>Dt~m4^bXVu}^M1dg5+%aCEf}_7`q{rw-N^ZvQ)V$ZR}L`RKj!d2I8Yq<Sj4_TfZX&&h4npR~)LQ=VG-rEWq+H*f3RREPKW)AMJK3_nbMrAJRt{)%p1sHFV-UAJDO{e^yL+>ZY>VW(SX8;)O~@pDs-QJ&}zPM@*oxOJzW=pA#8QeKmCI%&Qc;j~_+>gN1cWnKxSvky{9*9s5H=TO!6T$O#M=f*DypUsi|bbwJ^n4<f)|4u%)p?gSY!3#;Zvc}Q8s;<R++(Y;CgCf!`ec5j)?<m>Fw2q%0p}caV{z&>E*~jeGU8J*>1MgBD(f<ua*U<mX$5+ZY*S6BSj4`cpT`XVv57v>cpNW=rQ*`r6p3HxKx{P!E35sjf_fj0D>c#7+4*n(YAEw`(^K0<=^R!-%Teo&M%k$gY2|Zut-JLA&m!h+d0jis^){y&g=Udn5dUGE2N!#bv?Z5X?Up0$vbx~f<^S-C-jjRBjJ=Ra>H#5pk2I}^^vJV)ED^Ah4LM6`EG1M;{-HD^Ujs9Nfj^lskK042|f@9JjeZ$E9jN+SnLbns*{I$v&sBZd~;ZnzY4)YCMB>W0G&T;J){D<7SxjvlgYz?{N7z3LwQXca>&(VB1H;oB9sQ;VL&Hlr*4~-WW(0$P|p?`B*?#~{%KmD0*fA(i4_es|h86WRsX8+_1lxMeFw|rsL2UzJSI{)vyC!i0Qita}ruuDgie&_w+vh+7rDEjIL$e%_2OTJ&A|Cs1YmZIBDvM*Ube_HMj+%G@w7i)Lx_U86ea=#V7o)xeUE$mNA(GBcRHm8;PsPkNy&hw(^empOF?mths>imwZzrL;c3|-@VXU_TFCw1o>H*vn3iq3GpThkNi{Bh0;{RMfB=oxO^x+2dJ^BJjIZP2evf9vpwb2M)65qTbMiI(qk?c=46_e0aUza5J1^!bkuoO9JbLY}{-qBESoX6{u>)<wP-nRs8a6y3o4l6L)t^MU)HeaP$SaeXy~r|FAs4(DG*+(z)Prs|5oPp0A0&B42WGS$xbmY+<s|KCq0FVA5qw=!;G3DdZJ4;TafeQt@|z6<;gcr~|G+!g|#03XdQo!fZeZ1A<*)^mFjxEcH@QFm_jzy|Oii`&Gl8Q2KE5Oc)<)4`kJQw>}NUXPenKri?>ZnLoNSy;2+K8z^`R)LqHR<nT9z{haAkBLuYi6H^}eq0L-2M+;fz)<iA{5A~8!0$(_Jm8}Nd<?DyJ_bII+vD5}U=8>tZd<vv0DlA?#!Y-X2LXe@Be`jary-W$V(X5;?<4S=;89F$e;IEqVhO&D+jednfm^^^ki$CQ2JqpCHxf7jJPdh71MdZ&hxKIvE5I|6lMb8+F6OA@wg$Koybigp25tloLQeMrM}iv|QvqBJUWvI^0(I~f%)JS?20RLDn+S{skHp$00JFeF%mR!nK&_(?a|7lVSPL$4Yr>kEa1XX&UBOsWFz)4Wtg8m&YA~h_v1&1YE#?;dVQzD|O$AN|p9&reoC7ZKA@Er6R9G>$G++sM8u&794{%$7*aAxf<`R54w;9}0xFrD-z$bBw=avCX2G0PW0Zaj($!!X^2Z58pCu6>NU@W+pCl0=G$aM<xPe9x>{FZ=m$ru}p^(Q0O1k9g+7&8Oro&<~s&*rw6TMqalTo-aH;<f<zL-1T~Kj8KVa6Y&|PXJ$n>jfB_1Iz|rjJXPdMc}!Jkq`8MFTgnA<H-vO9u@N6{;Tmnf2P=^uK##cN4k&Oz>zcgA$8~Q_2dnsBR81;6NgVNMff)$h_rz'

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
