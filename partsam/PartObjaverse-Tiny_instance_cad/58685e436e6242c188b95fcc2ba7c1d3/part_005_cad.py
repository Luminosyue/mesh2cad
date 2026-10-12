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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/58685e436e6242c188b95fcc2ba7c1d3/part_005.stl', 'relative_path': '58685e436e6242c188b95fcc2ba7c1d3/part_005.stl', 'source_sha256': 'ddc7cb004a99146360a9c148dbb4699643b9c8c67d5b5aeaa0c7b313cdc4a113', 'input_faces': 166, 'input_vertices': 112, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.36487653851509094, -0.23297297954559326, -0.06632424145936966], [0.44038131833076477, 0.2914324998855591, 0.06631050258874893]]}
GEOMETRY_BASE85 = 'c$}q}ZEO@p7{{kAFXhb&v_PSh?Ta2@=_@TzD7Qc<#cPiPTA&5Wm2%};$`#rMC5CW81c48JAb>(*4ujHAUQO^ND7RqHVnL9I5=C;Fp!mV4UsQ}5cV_=Hw=<rJ(M=}*-~IFK?6b4`JhQFGmC!GlSVsn_@B8#4GQ>o43?<2Ai?5@rrODTs8`!ipjy%eIc0l*LYpXqVabyd5#<9-V+0@}E)f}^$r#o^qM{|2eS4U%DO?$^WAN4C5+d6%w-|27M<THOyEGQ_<(TXPJXxp^^cnmgE(6Z`3bJARrZe0&k?c03!qTT;yGV}H9_`_kFAGvS&kpq9e<g~{>y|j<{Yva4^@y1h@ZyYAwQhfIQUN--s6=$UQEXxlrX*gq#*B;hfVR0}2c2>&gSIZB*{qU?b|NfiT*zb@W&;8Jwa=gAM@g}?e5jh|36Stg?zSaLRi(fC_FZUw{<onh0Yi_alTzNgY@7*V_XYiBPm`}WEU()A7eh+-k;(HFf&d&e&)w^~-c%zp2#s}ffa11}xb*|HC_k%~zQQy0_ct<#vzoBY}J)T@U$ktJhzq30W!w=oQxm$|g`NnA$cl)h9;TXPt{>C0DpVk*|F#Sr7=f2S`$CJb~_FS|iB_H@kubhv5zJd9nL-PG{Uu#hA_v$_?{%d(Xxo_0T>uH3KFyH&faQ3_m{lORPJ$QcSWp;j#qsM9U^*hc>Y~2!Cy6wJpA;VznbNtFNyHECZU1ag;?vUL#N>bis^MAYjpyapCeTUW23-@+~WB8$M_jcLigQ>q<VDWuFU8nhbm!;l~)gOef^at*%{XxVl{ek;xe-QCXe-QCXf8f5_A4EP%f8f4aN8DHINcDLg316wBzxk*mabHRusXnhG;VX5d`n-;Wuk=0D=Y3D)snnh7^STr3ru0eG=Y3LKSE*Cg=XEOPQR-Cnd7X-RlsZ*?UZ>*yQR-C8uk>@(=lxvxN<UY9-p|E)D*aq5&a?6ip1Q`K@3`aF?SAmwF6Kw}TJ@{?`VOmpxo^0}GvD}r`$2nr2)_26)gQ!lU)jj&j%2z+_ITr{<%cF%eMa~{KKCK3yAxNAN%_Fnx~+aC;vex}W%&<i>6YT*>;0_0C-T{u&FWe^?dXy6dDim1=%3t=1TMeN<~iMaQo3LGT2Jpud%V_S^#T1s(<ys=#BcfJe$y#?e6Z~Pd+dId`E~e_6UzL1tUe!9@>l!6m>>N=I8a_6bzk7V7yE*@M_zw*zYz0dzaUxi^Hui|vCh~>B0tFQkGj7IU)f(&pYJasAN&5|k-na@S4}FfOeBPkLFU(UbEECknVR(A8vE0^W$M5CbS^3Rzn{+I%pAs>BNc=4Xy^p+XmAQN1DpaL3C#kJ1do7bf=7Upp&B?DJPMi)9t9o)O#_bsk2S||bC`dSkVP1j-OxwCZg3TJD7Xqd4>}k;5A1{{f}P;0&;j77;6i9Wa3MG!8V}9~=RyfM7n}o)1LuIJKoh`Iz<JRA;5={vbRf6@T!gi%#`+BhCqZ4{B=9ikT<|dP5a?|15bz*q5x5A~rL3D{7ILRr3Z^<8Otl0|wb*vQ#aIuj)4)_`fT_*|Q!TTtVHwugiDxzsT1cYLopKd4pG4mi%5G>bI2Uuep>x1g=acBWHy`Uwbpe>_LNL`Q!Bi_r^nI?xGoe}mrdkdz$C_3{r+}-$F04O&9tF_3B>Fy3&V#zZE}WZ(e6nzTsu|!)a0PS%xB^@b9S<%C>(Fsvs;OWdJPU(zDXvTN$b>EgXM#280<Z>7ht3D5gVUgMz-i#I&@%8?@EGV!674^fM?q(hXuqPI44p=z{f+VnXfcWQL&_teB_!HEDW^cElW4!CJQ`XGF2!0=USp0%bF79ofmef9LVe(s;5z7fa2<F#v<18zTnpU*t_3fJZUip{FNU^*7lS>}0N4Xw0&N2?0oOoV!8PDzP(OGXcm=c>yaHSgT?eiQuY#@xuL3t<Q1+VR3FJKqJQ=^+!2#$*Z~)u}b%5Kzt<cB8tzbX&F|Z%p49y06TygQq3IFsjyyy|68;JA|J@ria^TmGVY;!L0G2?Odr+b~bfyI-}re30NE%^&SYxIf'

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
