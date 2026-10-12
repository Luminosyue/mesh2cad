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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/358eb80d4d074dee8cd65b4b0fa187f7/part_000.stl', 'relative_path': '358eb80d4d074dee8cd65b4b0fa187f7/part_000.stl', 'source_sha256': 'f22119540ee4a632952b80f9faf4a63eaf29f4738b1b8e0ff992eb2cb47954cc', 'input_faces': 178, 'input_vertices': 130, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2421814203262329, -0.07436083257198334, -0.24570946395397186], [0.20160408318042755, 0.338469535112381, 0.28237056732177734]]}
GEOMETRY_BASE85 = 'c$}q}ZERCj7{|{xUYsB>-Vq07bBy6&Y-59smzKdMTQ^pQ1L_!SH`=WNE415Syk0(NRQ#Zls4;$+64WImq6;5b5SD?wDfp6*5I>O+-x5O%AN7Nt=k|Y2Z=ZWfj5c}l|Mz#Fo}T{C>Ako0c{9dL7m3FL;h&H-?%YHns3wZ(qAwKdiFAbGOS|{=r->;hr-#y0o0=PZ{xs1i4(IO*#XDm8m9G5N;g$J?uKaK`))NbMw?$*SLd0u=d*UI<<6XghA^Ch!ap|%`S7||^>!|BLKAxmG-2VH{Who;UPTg=zHGco>b+?u0yl?W6?C9`i3m<rQ?RO@Bl=lfe_joUuTx2}>ka(cWIPb(o?`u6)?paZB&E%2Pe$9<Uf1vx9o216>qnC-_?~H$I&hOT3laDlJ4w<jJ6-ng{;8#kox-Hxo{dFYqJhk7r0zR7PH^$$+ZXW;gp2>~k)8CU0<WBm)?0<PMG0z=Sf3R}T!}{w^d}Qd%Ek{1Q^=m5^f6ac!X?(@`_=@xKHD}`+S+x<T@fGLeE6&H)oQ>~keQTb%PtMN0Yd%MAuAeVu5qBLKyqnl3iFNd>FWT#Nc;EZA1E<aBZ<fc*=ato?PTWY3UQOW_J5M_HgWLL}^`{;C!EOCt{c*;zAKcde>XFaQeZ~9xe=~W2^&5HqAxA#*+K}ToUsMm9`{^;<!^ipajf+nGimQIljLDxm<<Ggn`;qg&tie$yZtK6%^pRsf%U^Srv*r(e`q*(C<Zp1!@>iVauQ~F!jf0#6kKsH|o<HZRKTtk@$SHr$4c^c4=iJuM^4FZ@uQ|(KbC$p6EPu^e{)+SbHD~$jaajJG^E`R}oU8tUAJ3k5%Aa$C_p|&txAn99HD~#2&hpos<*zx*Uvrkf;yi!NS^jz)mOtk_Po6*LdcEFz`=aCiXWZcZeE&0U>*xDlalZc*=lfrAzW){H`(JUs|G{nhUva+w)i`|rGtTq0?SIDgdR2XM$#MTPZt#9~{pH-&&#u3m+xpq{mvdV`yZ&+>VEz0$%Q^4o*I&+gp0@qZxL&W5=MwiruiQ?#|MWZ>y_wjz9Vz$20|j?X&hLjcXZOR3^ZQ}Vt@p#elwUh@=CpR+dqN1RO!;dk9JKt@AxICU&Odb`%m3X^ofRwp?@yiCat<{0Y0xR~q?6&N!B2%wf+u|no-_-dbO!uX_?ghT@T9ZgSIVl8wE|iWzf{&TS;eR#uz;+cvf5BVuufTFSzXWw{Bl`kvPz*P@Ex++W$l87;Me1L391T==HijH4pj`c7V|1Xxxrq*cp+3X7|nB=tgWapSQqBJ9qNat`EQU_jVc3s9yyhxYQQMZjk0P{6<}LrHQ{qN;WLx>A-^DMGuS3sjmWwYS?@#!Yw<bV$ijn+sxa3o%yk3iRD(IyU``v6!FGI3KeE_{jG8guX3TX9=HtWsHe*i2vSrPe^$d#qJm>=WdGIc1F1!mqN7iCli)1~AB3}T_hcAF%2z?fQA$%S*2R;Ym=V8oMc%Q}al~6ByC48N%L$Y3ybr?l{H}pmL-S92YI`}$_(}LIbW4uG~2cZYx55o6Bd*S=wdt~jA)h%l;ihLBh4?YUN9~y(-4<Cp2!1rMMIL2(n`|N?=0d0Wa0bh@`E)<FN&xT(DT@Akkehsu9z8>R{r#(q~uNLZur!_6dnv+(D<Q}LH$$e6RHCzSnh1SA*;ai}7c+v=b3%pv>h-KX)SS!*nd_VjFWE({Gq-~b9XtS(W8?tPLZ-6$!H^5US^c|t^k2?2~FM?*nXCvPt=o*nc2a<O~8%6S5L4F-{vq+vx$v2_Mw?l*QL43}3XdJ#BJ_PNB??pBtXc#_>HCE?j^6DHzS`FO_Pg*0A=U(z<&~kXvh47?#@MZ8N&|LUj<XZwQhA&1I>bgU|3fctUgn5u3D=S0RIOrI7`u~z{FD5`U;SE{GaQqmKkv}2pIF293F$1s3#PLiVBR^i&)3S~V`a4&MBeLemN)w4kx-6eJEq!{%<Ng9pJ`D3k)<1;#D^qW$tgn112hulJKJVCZi8oI-H%J=YS%`lC&RJlY'

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
