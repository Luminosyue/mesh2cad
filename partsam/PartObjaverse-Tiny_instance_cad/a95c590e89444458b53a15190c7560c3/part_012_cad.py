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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/a95c590e89444458b53a15190c7560c3/part_012.stl', 'relative_path': 'a95c590e89444458b53a15190c7560c3/part_012.stl', 'source_sha256': 'a5045dce7c42bc1b817312456c3c4ee3103bcb85a135a4dd727c17a182108db1', 'input_faces': 92, 'input_vertices': 71, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0929064154624939, 0.11129605770111084, -0.01231124997138977], [0.14110350608825684, 0.30421245098114014, 0.1705690324306488]]}
GEOMETRY_BASE85 = 'c$}q|4NO&K7{?Fb2N!RA2x0`r1)&Q{*9%_n1w{E0HihW6W}^@7l3XUMfxsQ}3p?{$r}jY>t=cq!6cbQF%tCG&Mu>o>vs`m#tu<w~xs_$OI`8xRuibO7t<~9{{eSPD_dNG`pL5Rp4ts&$xG;&Y80pOJCD92JB}s%{3X^J`)voeo&Kgt2id8;RF!|#0XnoP*$Lvr0NVU=$W2v)dS+z0UV9Y2>H6|I1WtG*g>XM4*E2~SL!p|>xsm7`JHOos@IF)gNEjh_BJ2A;nXZWvIfT*FXud7E9dFW<erlMK5TRJkmd?`BdOEH#x7P7Cq&`JK#FEn4eQ+kjz@euoO{>pw)WsA!H?TvoQzpLN~`4!fWgrBvcb(r#ZU;d2z;f@ZPZ|@uuWA~G<sC>C&<2f3a`ko~1DdPEGyFRCJ*4=iMpB{Re@*6{rl0SIz2<15}(Yhp)<u%gm=EF39=_$^0qq|w<yGtmK^rDONpWD$+{zx6wzbCbc?<=&iKTu5d?>TQ(`xl?0`mbI)!2X1~R^hv!jX5vIhK4-$7lo29{V~6n#-sL)q{nX@Am8utuPD#mdhXBG*8Svv_q&_M<}C-keL3K5>X-cTCGNku`2+ghZ!#&5)W3rJ*_Yo;dGzZz@4E~4s{D$mQ{0Ct&Trn?NYAmeociFlT;zHi>&TZ!lBo{{T`~LC#pFu`182z}bnto;PVb}nd()^M`P)IRC%lq<+e-2cBPOnE`KtFR&*eg%XJ7jQ>2?SCa_S<gN7|jn&;5>_=Wm)${g;=<vu{87D*4@)2FZ`l|Cs!^Lh|MIBC6j}you{H=kB8UYgY1e-+P;V$A%r`M;_{?amRa&-oE^^i=WH--d57$6Wge7PAk{xyY?8rzvWx_d%1an#!*3UdHeE}DZKtAZB1OyWb)nD18H6EA2xFy$F+5;-#w<UrM%K=6ZsYUXkGG!K<=O0^aS0%*`J@|pZ&ZJDdagCo0`aX%q!vfSFbN8?YhGAFGq5{rR@!*Kh}N9&-MH}Du1+>^F~>=s{EGYJ*3|U?^pS~XV`DFQoru`#`V0eTedx<4ck7<yx)3{Zs&e$`w4$cKVt{mGVk{s;g5Na&(wF4YTv_v)m^08@5tk8zoV6H{M@wPFZ?mz?;^)1q}u)Ar%|q3yN`K%?LOv;p#F~84{tSd-?jUy$Jg$w)53Y3+H=9<C-eR<IZt!_twFpV?YRSAb?(?zr|j9+zZe)Er<@2%=#*2oti<bx6{fg6djBJ~-14uE*tC@YeZ*!dHRLLhhw}ZD@I?p~XRuz0NlKt($p?S)f#(OE<aLkG5a=Xux)Nzh%z;|KbHFLkS>P0~5&8(&2%d@%9F7p2h!C6%odr$?&xTsSv%#s*G;k_-9zyVZXgYX4SiBE8&<togI0I~h&H>xNW@rl7432{u!ExX)=u~hRScf`AO<4%RxzJ2-E_i`g-3#Cg%|i&zhvtCupxMwIa5i`@Gy^;rY=zpuR<H?b2Ajasp>g2p;8187I27y;)q(xNo=dRjofWEw>cBemP!A0U>%pG)Sm-opI9O;R*r3G2O2k8>!9o+j@!*-zN5M0}GoVS}8Q>UbEchX41T+>b^g(b0I1u^(I1oGmA$UAA2s|D<5g|BOiOEV#Q6dT&3APvb_=frY)4v>lU$SVt>K_p8o$77W`_3{Y*S$^EUNBzNu54JoQk9}r^ecY>m%3Qh'

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
