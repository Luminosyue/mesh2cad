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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2dd2980caf87450d9ef7e42adb43f2ca/part_005.stl', 'relative_path': '2dd2980caf87450d9ef7e42adb43f2ca/part_005.stl', 'source_sha256': '0018839a5cd97bcd62098925d5aa3d991ab5e90d7f42a7d88dec259faaa18ef6', 'input_faces': 116, 'input_vertices': 97, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.36111101508140564, -0.4166819453239441, -0.2916664183139801], [-0.19443930685520172, -0.2139057219028473, 0.2916664481163025]]}
GEOMETRY_BASE85 = 'c$}qJTWl0n7(Trzt-VnS7J6~oB3o)fN`bae+35|Dm9n5!mR@!@?G{l3blcDnW0)9x@R=796SE<{(8LE~AT}{}FxsNUVk@)}d_bu$J{S`pj4?+4GxPo9nd6!mo#fB=ov&xk`Obgl%s<<3C@Z^ExL389dFAcSi@8F`$QPyJOd>gcVkj}T_2lWZ8KT(H<;8fRr}tnuk|EBB*8;<dv7uyOw-IO?X$dqKfss?m@nrmD^i*;<A@zOnSH}{hkG&K>ouGDIYjcCqw7J1}-T1Fp9$AQuRxD2w+CNO*m6*Cbxj3Chk8PS=P;~*_Bt4i$w`m+zx89swa&WlUHxBE@x1(RG`u+2+E=Uii(Ni>zs@qpx-&S+${B#=K-j=+n>LzrP^k6!j#!>auV#O_Iobf+qed8~<x*%QcA3Nmw5Vb2e)c&y^=rt=he0dAiec|9YGuM4S54gH{Z|1tMe^-1iZU0W_=x;t~ar0}|J817IcKonz7fs!E@^<+5&s5!fC+92d<L9bwg^w(x>o3fYZ>1aGtiR*<x9@KG)Tb{7+;s(K9sdUVoS0ZntIrwB>NvV?ePDm6>L%7Je);X1s>iS{t9<r~s`I+UT=o0D@v$y_99|dCE3|y_ICix6j?+GV*%{x?ia7a6K~MdBVM$#t>vq>$?tR_!Gpa6rjo(f;4)2$B>48r-Ft0W8@-<br%HMF#o3(OoO4Vb~^?6ehXWcxksr<+{{?|XwtNtza^KQ?Q+TYUF#q+XmU|sApc4hRY?>WS}Sm%6-?1)ci|0evKJP!QW@16TZ)j1F1d)E)^yk5OO>lW5!@Hp5<i=SI<UcJA!znIt1)+_3Juc|ulqd1QIOuFaN4&wQ2!?}Yla4y6>oIB|J9?<)z@Z8#buAzH=xDAZqyy*S!!;gjY;`zaO(fxS(lzWam9q$J(pRD8kz&iWl_W+M0wDqzd*1h*0&Z*GXTj9PRSohw0{C*g6pGUoJ>N?j=*7drn>s&Wk*XyRPbKPWJubaBgb<^{y)lFUJy2-j;H~*%iZnCb|O>cayZnCb|O;6YArk6LZZhC&Sy6N@T>ZaFUt(#%rSKW7)&Nu#)BZQ1x`l=g=E1z^ylow<APr4I3{?#X4W8<#>`AwJi1bHZ<*a&<Se6w7uJZ`{h@Ft3<D0Tt6z#pe5r`QUt1aG5wmSPVu1l~gNG{p|!Uhs|ZPzPKGUJnlqz#8!F6dmx@0Z&bsTY7jBSOvb5q7%M4;i(OC$hiW*wcxE3`{8##ytZI&>0t|S19&4vJAAdn({{`)J!}Kkf;Uri!&f&v?Zn*D!zN%U_%raa8`uiI4*6;ab|}0I?K0$t`Fgb1V;`AsKwIKIh1Z~61Fy`h(XNJn<_6jZ^341(v?YcVUW>NG0}8J~y9(=PUWs-ka>2YD?Q-lF^9r;j?p1gx+7g2bUyHUx6I>qK42mPb9`M5y2Pv|F0{mf$EQ;rWVescD4pBS=%mg2xh*As!W8iDROMp@E)%aU6umpTH?kffkfEQA%67uJ!i@D(W;1S>p;1TdXU@v$dcp-2Vcmaj{omd2X1iYW(D8(`0i{M4*(+@lfehhsIfO+60n1|Pr4_*vD0E~bSfJcFS;8E}rV4;%F0_3s){y6vj$R+z5)b?jk*$>`_D3JFx9LmTn&HAT*0sM7Y^5OFRLqNaNUuM)hm#FC#op2~eK3DXBWr|V44CzMv38?ho2>'

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
