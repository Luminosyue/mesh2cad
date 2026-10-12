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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_009.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_009.stl', 'source_sha256': 'efe3452274c1c04b517c210d1f8aca8e84c0682ed5a38ba449371cd8afadcc7e', 'input_faces': 100, 'input_vertices': 71, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.11697904765605927, -0.3597361147403717, 0.1093839555978775], [0.19138942658901215, -0.2660077214241028, 0.1576961874961853]]}
GEOMETRY_BASE85 = 'c$}q|4NO&K7{|}$8-(~qh0r647Zl|pB8mtH70gUWGe5}8i+m`<p<K}Ata+x=+-z1eO>^ocCv7@4MXe>m#msC|C#I=2^XgKWv!VpGT-JS`|KG$`TdT9Z`~S|LhxdKn=lwWPILX^5O2gAnTQ+fjVv@h6sTQn7X-mo+wG}00HAAZwEwyN2;;ZM8uA4G#a$%80TcRzqmX_6&IILN^HM@MIHAT0UFLcy8imT=<bd;7Uzo2+QO_|59nP0r9%=4a<nU<obC#UGI>HqZ!@}%IJ{_~Msj~ZXE{HjI09}E0cy}Qr+(yUZ(j2GV>yZfkm*B<z^D7DWyD!vgHB);o#zW7GPD#T}YN<aF;QpCUY#(9bFF%JD)TPMEr;#7&Zhn#7ZxT1~XyBjZ@6F<3LeCOaZ=zm;>_(tCW;=4~?5#MYMm45VnbuzBj9OaVujjb}S<}Q_Z{R12Pxq;%_W8aZ?voT9lzqR&Dsl&H#%ey-`N7UX~A@S~p0O{YnoG-rXUM2F${$28LovlQF?M=x4-K{cT_q=NOH`=6secmytuge?b>s7y=Rla%83vmUFqRv~s7nJYZk%78(p2W`=ua)_l%?&aySNLi4(=%84*D|Nex|;PjFyEy0h%ZS!CjBIKA^))>uwI+nuwL6^q(5zrKla1PF?ipZ-irFKlRB8=XGy#(G!N@@eU{|!diIXYOY1)$>zPr6`ahV9JW?Ivo7X;)`nawpVO{O-!C#PsdbV^*{#qo~-$=WP_#?Mb&mZ?=J?r<%xW)#pN#YKlLj3mW*bnAx?1xLIk!RqmsKbg0(vLBt1NA$<2X!#EO1$&KJMgR9us_pV5r4Z2^>Cj;9SYi!Pt$Mc|H=WWzZn*QbM<nF{9Hfy9Ol)w2>q<?C2IQm;2cGLkMY`Gz&elmSo(2azJU2GuM*#xSAuaD#3TM<HTrpekoeBh0*v=l9r9|JA^jN1OQk-p^d0zl<uvS*ZHqA<V=wx#eZl(Mv0m-pz~A?#_|6_q#BaWaJnxPcUoY8-b&R-)`1^^{ztb-a`R~EK;tact`n=vH`^5aN5B8lSO4iZsIM{@G4aELh`w(?#e+uJTb8!Bu4&t1?)W~y~kN88bHi^I4j(g|CWZY+;Y`}awTChJiO+!BRWjK#%ui(4|Z-L*HAo(~qM`It)Iu8H%b@8>;6{u(RWI0dnsfUpN#R=G#k+b2?EWmslR${(eR*P>|us*zJTsa#NUv)t8H#$e){Msy^iEdktarf8CxaRx4#CJ}qlz8)pnbMCIa!7o8!6otSar1Cb-m@H+aq8~kysTW0d<MNJzWe?PoZp$7u&=sm5#P~)_`REOA5L5&zLD>T{%h-T|Hdr+T=MZhFY$WVF62L<UVLp$9rDaRfqFJSb3*DAS0wTFRp*eWW4ZW7${o~ycZDmr@QJT%c&1~Q%~#V@3-o+t%Zs~xVwI_$NBZ}l*oxu*>Jyu0v;EI+Y|vAl9Q-u(=Kz{wA5A3=4WjyygUBINe{u*pl-h$FN{*z4kt50R)Lvwz>Ew8_jZN_wHpMyA5#$`QK^;lXqh?V@lC#Je)S+ahgUA`=Vbp=-VdOOG0CE~Rh59r(g`C8uIDy)eoIviwrZ}1!OpYc8uqn1seaIHFZ@0DdWm6o%rZ|QgM2;c%riPGvlVho&<XCbXHIf`h?oW*;_a`S)ZRBKfrl)07M^kNNrDMpW$z$0RkEiC4$CLA^205QxpgrCnipNoNsd?mF@+fK+c@%j#HG`~l7<o83m6}FQB@dydkcW^5Q<KPp$yRCt*-B2N_8}*d`)cY+g6h;hWTnw$ogBrc*qa(aR%#)8lQk-@GkFwyu_+FxMv%kF{n#RyS6^}>HHNITH@R?<#VgADpZ=wJ{Fstl_kVEy`kPN))7^iw+|$>emv-SKUv<xUCgY`5d$dhP`2%a<v)%'

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
