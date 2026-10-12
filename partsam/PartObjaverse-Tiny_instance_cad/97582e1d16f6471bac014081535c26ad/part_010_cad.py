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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/97582e1d16f6471bac014081535c26ad/part_010.stl', 'relative_path': '97582e1d16f6471bac014081535c26ad/part_010.stl', 'source_sha256': '55525454b1ab12db5b8f9cc8a957c958965489fb62f0a08c985f10b42a9cadf7', 'input_faces': 100, 'input_vertices': 81, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.13146190345287323, 0.31137794256210327, -0.05395478755235672], [0.1000884473323822, 0.48859649896621704, 0.11515378952026367]]}
GEOMETRY_BASE85 = 'c$}q|3s6->9L5)s3=mPo2R`sZ;zdM7Gyw(fMS;`{dY!R?(S}R%2z3O35K-|kW@st+$S0E5N9GeXM?**9HZ_`=kI}?OmV`6ejMbz$MrqmIZ@&`G&`eWjX6O5z@9zG0_kVWxo@2GRw)Yk43J}eyPd@GWtPrwv6uzP;GrurrdS=0p*?IF^L}&Q&`b*bLd@<RY>LQB7d}Bst!SsCND1$LNE7BNhFlOcE7v`tWPRq^D$drC!`mBOXr(f_|dS0gUJ~(n%sA2fPP{TsQf4w}ML$K9dcGNpnJ7@gD<W#$Od_<}(z5>2uL74KbukV-YC||Dp>K`u4dr@0*68?c%@XcwPub}?b^N8b^83A9Mt%7g3KM!$iV@JZbX&K5-d2~W*qtOd~W8XhieD~ee_&u(=9&sk8qrR5(0sO`lraI{x%x^Tne<fmzRP(t@ClLQsdyHQ+ZODT^s1|<XuK9=~^0MZ_FEPN^{8u85s5`X`@!j7#j(N?Tdlm6dezOYm`t{voh`+vvieKTm0&z34;cFE~RQ#%-a^%Z3qZa;655y7II!%}N_JPYj#JuYKufb3Lu^i*^@H~q8W*g#bRoPXT=cNfp5U=cK6@OaS4e)QI9maST<*WF?&C3w?asNZm(}{@VIBMUHxQ#y@ggSmx{pM~f!+b3l;F|+OZon^IZi8R21HO3l5dE5`_-#Xf$C3}A|K6|OMEyp$T=bJtRD<|u)OfUWYc?W3%@6k@{)}E<<GF4xwWGe<C(3tJeuX%tI~Sqfk$v_dPaCu^;g{c80_|0@7yXO*s^6xm3(>wIUiqgEsCkWPT8j47DSPnyn>VgwJTIrL!g!1icEaB`1^F@W*|Q6N!#((h!_!p1D+ebb@Aq!Q7Z+SGej#=?$4Y6~2w$65tLAlfE#_sORIdCwH>@ki@`LZAy>I;vXoqZ!UppPV8snT(0l#rZI`U>te6SV%y-4KSyrUBH(!RZd=Wah;jo%%kk6~Woj#iC&h4psCSrDhjU-elT#u1&Sp2Lz<HU94%CCJw=?;)PJ9&iis(<g7mK0Thg4)tAA)%vkTBfo}I=hvctYof}3RoW)BFY5;1?ESl1Cmm~cqu%26SL<Y)s2r8&hg<fx^hLG{@?(z6YE|Fh6|V9V|M}*YzN5HEjlcAw*3vhJBw+lF(VMoRUC=v~P~$G-#}Q#czC`ih)woY6Rr#EG8}V&XH`mB}yWOhtf9q}R7jye&_}bz~l~3;)wZAHS)|%Rwui^4p`1<_Va;B~`wUJM8*S68r)^o8qu#WW4(J*l{o{#>y8_q;w-uiW79$&e`)W*8f?$*QCuS45_r8`Y+tXo@g6MX&px7FN-uir0*ClBE3_m{mebr0@!`_Z;PVK3I5ZvWcs#md+1cM&$X2JQ9d%+c)!QBQYXIkJNe!PlLK_5|Bu#Mhmlju?yjAJd(;qR8_o`qQ7!xf!*%*PZj)#q4A7b^i-m<`(#^{zt5>-YQZ)4*o98%{fzNad*B|WTm%wrI04lKyCY#B4@<EdZic^7WO~iDLh6x$MC$f#8O9)W63ep2yzTLT0SFc6g7e@br?B{98Mif4kw3DgUBJ|Ko-e;S%Q#Wr31+U<bKp(azC;^)ku~)fb389qxL6D?Lqb<ccuD}rFJ5BC3~|-mhWov5xY7|I~G^*^pfmCZBLfkf$TzlhDEYF)r0I#_M&zody%_PeaJqXLl+jwzSRC?U$TKkawv5OIg~t<8b+2HNghfbMU5kmBFD2xo<JQ>o<L5fCXubwNz^3rM5=|FL{4IR3yb7&)Ht$K6L}mtks3>u8beMbCs3ow3FNWj>E0O2BKZXt$zxa~kETYErG}G7lZR77$ivBlsDb1`<ma5F7qvGvkSw(?xi`5di{w7k0CFF4cWOU!cXBtXKUu0DS!!3ZRBv)Oa%UkwyOerTy~$EN$ev{R6=t=#wDWcSr%$-2mnJt*s}DMT%htzq%a$)WWBq+-TP<#K|2a2sJ2A(pAIaS%{sbfE^RE'

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
