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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/94f6eb48b8fe44c69dba4ef04cea53b4/part_007.stl', 'relative_path': '94f6eb48b8fe44c69dba4ef04cea53b4/part_007.stl', 'source_sha256': '877f1993088aa12f5543acdad3a0279272550e76b2cd8963abacf10cbdb77905', 'input_faces': 124, 'input_vertices': 106, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.1167234256863594, -0.13777872920036316, -0.2530348598957062], [0.11699394136667252, -0.06435064226388931, 0.3214004933834076]]}
GEOMETRY_BASE85 = 'c$}q}eN0tl9LEnR8NQSym7?eo3?zsbc@Yuhn4ln{R|yT%IK12omhozmGudsfnzNS?rL);~tGWIum#Kx4aeaY|w=1AIYtCy{TCKTetu@!n^ZcIgJ)Y+oZLO~R?fdb2fA@Eum*08L8IHnHqr)`unW;T}ZFoxkSWV+GUJKJUI~zA`sB|_Z)Yfka(k7D6KLKr9UQ*;J4bnDiTVtx6O_hx?nR-l?D<dXek8#yCZfY#AEvsv+a&muh`Nk$E^P6hQ>z(ZXvy+q3<Mou-czv7xA3uB)`mW2zI+=Pd)g0mK9jZQ?WAoknes8DmmlSk$+I+3~GWmMJJCg5tH~3?!GdPRt_+P&$>KwoDDOZ2q@TpFlul>1zd~-=!m)&=7`m2Nd;Z~`RvG*eR#^Rr)I(qxF9b%j-QRf2r=8Ye`^u3iYd@Zttd^hsFt~U>iv<{Z9%**TAb6~`AwtxLT<#oJ$oUU^u>J0t9{Y&BJZx{8P5&d@G%qbvWcV6$a`=0zQAJBZuuk;Fkh<xp8@gd6J*g0VLz0+U)kmgx)mFk=AJ>(m04IfcnZG+G5ySw)urvE<~2mge)F4i+J{(x^{-#zue`oy{)6?L$W`jKSH_eak-Nb8XuPwQY5CU*-zihOs(ceMWg+LwHG-;7I<d_5+Ge9ze5#C{c)blZJ@{!Ov}b!}3<>0TuIQOP%QdpbmZtCVlFHy@?>E!!dIr<YMb=(TI4e0O^(^@D%o%>ldbU3s0>*}HtwXLet^x?ZgF<7HC5XGaw6qp>RFv{Wa5_d&|9ZtIu)Uv|;{>Z>PwF4g&Qo!IxvxB8^(9?K=)Q~8SI>t}mK|E^8!k>=&wPrg=GLjC5At3E{e2d>cin=LyBa%{f)r+%-vU#h78wfH*nwU82V-?cn7VE5gjyTmy#)FkDbUu`2_Q}VqF#eQimO_Fas(bZwUPpvu`&(l5{7-zuump6-j99k%kGckeoQFo8?N%h~GA^gEVh9$qhPwdxrpOo)*RgiD`TBLlf<&xN!lh2)z>U@(!zS-9?B#r-zYqb9Uu5p8sf4Wti8{P9I-+-_6L{c3+Y3Jb)_uVmkjK1$5Pxqt0KBPCt?pKTz=T&oSpWWBs>(6}OFZnNAllI;6Uvx`-qB+i!Z+<(O>X>=^=o~g3m&jMohk&o14_5x3^W=NB`e;0spKwm}Tl4NdyRY_Pz*o<ifbZFo*-7_>QeW*`tB%sQ)^&#xKM~{Xm+Gkf9PrhCw(2YWY|U5cXRD6Vx0bK;tu-&DZ>{kweQVWG`qrA)Qja)Kx|0W`@hg36)lvG^<G3N#UpeOkzW3CS*sr{Er$+L<*&QcF%un0rwfp{)!q*!@d+paX@P1;XAD8moox=CjU+=N!tIwT)uReFI`pR?1@|EX{bzSB867bdMh&5m3d12+-&jE+@w)*mGZ^SunV|OTvQ1-U!D!09=a+7}oI`XUPhSY!esyZk2|Gui;#l|p^#U0Q)!CWVSx!w)tdJmXu7<e-DUIgd+pkZMCUL49IghddGU>0Mbw}Z!kM?*uvA^0ulaaii{&{5zCEN;X1SYF~8EUH*UKr6rz;HfOap^FimmqIJR2`rLWq(GCwDc}_d&PC89a1powngA{UFG6sRho*qJrh&Q61#_JT<~kqDH4Dr&8_Xk>#e>i}V6KVahoH-#iQr{m2XqeD0bT`71+M}Zv&djk!Xh173@%1aIy4@f4$eSu&V*)zOYq$qXeM|Kcr7#=ycS#v%>rj(y-E?BA3<<l4V?#G4SpCp7o3KDS_xeN=6kvj`^<HTZQnT;K?}88eNu?ub6pNLS(LMQ3|a=B#^O;HQxKf<pzFYS;9Tf>@Osq9MR3l6mVtA?2FA(fkPkJ$268yZv4~}{06H7I0a^o{4dxmRt^rp=XMwB1E@&j!1$IJbf}P+h1ZRE*L_nuPXM(4K!=aJjNL()*8V!!dxWl2b;8@H*9Qpv5YYdp{{a~(9V6HlN3UnG&2XmdS-P&`mmC)&6M`2KK*r<Q{)5)!mn;*c^A5zp`%8xPoFZZ)r)<exv7(!=lF#FfQbRK`AXnz9^4GBX'

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
