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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/abdad363791d456786cdb511082d9d63/part_004.stl', 'relative_path': 'abdad363791d456786cdb511082d9d63/part_004.stl', 'source_sha256': 'e26c9495dfe615fc32893c78a356c0976f85b1677476ba939aaefb40dc6a99f1', 'input_faces': 84, 'input_vertices': 81, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-2.2272210121154785, 4.764152526855469, -2.0954041481018066], [2.19836688041687, 10.123408317565918, 2.3301854133605957]]}
GEOMETRY_BASE85 = 'c$}qIU2IfE6rSymXaxkj+KM2n)-JS53$)m!{OoP9wRPLFJQRcR=Qd?G)<S=_wFwf)#e@gaHpW1FsnMGHQXdQtCisGT4G~EiNQm*lgvb`CR-$OTE!1sooilUJWoEM`MsITR{q*eIGiUDHI}HUhv)oKxPqRyf?L+wwG6u1nxmjO0+S}F|?kVZ$I^trhgbx?t>89q!&;b|gV@JIQ!#%B0Z>7h(GvfF9Jl;rWv^Uz)@kVF#U>N+`mP0*Z?)SXe(iP@<gMW+9Q?}9PIp+DVR}L@1IB?ZvbM)-nQDAVi>Q;Oe;AltI2;VFXNZ*kDaDRfS`Nr(}8?iLLSv&HJ7-z7CspA;m?HZ4z@y&v-Cn4YZ;`%~N9jET>UGU8m-x$6#Ep$<n@Y(T|xoVx{dm^{os?QcnwS1#;tEh*3$|v7Edu~3a*8g7KbUNRx_+b{tkN;6Mua0kC9Q#@IX?*h8k>g1%|Ml9W>O1-9o4%l)-+XT-rua@i`gVWLtlBrL`{bfrN8L9sU6A7*Et^s2WgUL)FH!$Hx^I3n^ry)GXkc3Fzx$5JC*SEm`J?NmwE9O+$#Kwk>L>ro%Rg!B{?<j8z{|RC6^|{6=kT+)C$#lClrQsBd~0*(B4}%F(}Y@2d}@DE^{F26jj_Z{@%KrOe16XF6XV;i!W&v2e!R96P<*Ek=v((jKGyp1;gGy9`c5Cvw{Q0kYJF(EAoh<vA$_Nwy?GhpKI19*{!fK(UXi}jpYG*i9P6_5sUG{>C(KZMs)u~`tv-%j^PBAR$oBC-nm&-9+6QCpF)iQxwOaNWeWwrT+wIG42GaFEc<NRl&HCC6x=+u8b+~;ZkmmU@J9M9(H*;WMN}Jc2)nXr!@5~E*_Icy9Hm|Jj=VFTQ%nN-h$r9?k?9m3<=Z5nMZC<z^tyj;?X!S?szV=LaCAIrT2Io}Yxi9+hpsnQ_C$bYU#dqF^=-Vf%=GA&kzkKi6tvL(YeM{Vvs_)zv{djJxmQU|z@>Ad2=E=4Nb-rdjeixeG*T?bSz7|t_XB_m6(9nX~XY-YJ#XJpmby4&0j?3>?b<>jSJ9YNui1kVRehv42Dg682FZms0d#`Kx&b+EVaH;v?`y0|u6~9+)i+5!)2JsL-RYY2pBL$dn5vD&<w3Yw6BSrcDK2j9%8p?QV<57g@<*^<$almyv@=y~8e2l^INowMN%Xnm=CJvav!-bl72DUF7HF3Byd8|N99Pj}ikE13I2utx4YT|%vd2B*W9B?C#a@52DpXad?HF3aQJgQL>2Yiu7BWmJ+P4GCOCJq?l@dA%p9yQ1T_wWdyCJwlphaWX@zzQCvsEGrX@bIA~4p_{i05x&IXL&q<nmAxSkJYG&1Fqun2x{VhD;YfaQWFP+Q}n~Ai37s9HWxK<z(;vJiJCaz8V1`;YT|$%9)+lh13t%N3u@wkn|V~CCJwlrM-^(~fCi6x)WiYna1HAfUZ<=jU;}c%Ag<dUg#*5X>$Y3rfID#ADijX571ymq;eZ=(-HH_s_zaIw(3RoN{HK3`?q8PJgz7&;slU`;bLubm^Rb+lUMQFidy;SP4A#xj1-q5~4PLyIvj'

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
