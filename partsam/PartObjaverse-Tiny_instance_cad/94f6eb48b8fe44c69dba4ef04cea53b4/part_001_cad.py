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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/94f6eb48b8fe44c69dba4ef04cea53b4/part_001.stl', 'relative_path': '94f6eb48b8fe44c69dba4ef04cea53b4/part_001.stl', 'source_sha256': '7b4478300cf309fe659f70e6b50d9d0a3556861048f823a4809e027e0a1d48d3', 'input_faces': 131, 'input_vertices': 114, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11753019690513611, -0.1353575438261032, -0.49566689133644104], [1.4074075807002373e-05, 0.08781138062477112, 0.4493986666202545]]}
GEOMETRY_BASE85 = 'c$}q}4@{J09LFF2i6kZhVw&QcsHZ|Eg8%vRLTW04mr5n39>O7(!pR?7xyBh=y0&K8!b-DqsTnGoBAcdi$+XF=i6nO?sApR^ZJdd%xtgu#&-Xpw=iRlnI`-T5d!PHgzvuTn@1N%#=A4kwSRy{pkhto$BNO`(!XlEyk`301sx?K{$_Zt*H-ktN=j@~Dhk5zA=A}Vo1KDUQwpJEZm}V%Zw32D2B*j!xUQtz1ShljfqS(s#oWix0R>~_&3vE{VeQa`aYLb#NE=hS?`H!C`Xbbl0xU<bvokvoSW>Qr>@4K6IoD?n-yruPu;L)7hyYs$c+}q)H={d<<#W`tP-68Rht2tLM4Y(@RnN`ENa$$43lz(AIJ<oSNl<SW;$hq_KY^lEejkBCvE+tF#$>lcA?dPphef#v3!@SSiEuPE(+|skIQ_qR1y@B)Y9iBkk+p~k`d+P?Gf3vhc8n?$6OY5Un2aEjQt`;%waK*R-apJn~lDN9x%IkX?<ow925}uFs^z$ge9p{S!a<%2+6^Rd9^A2C<o=tpSeqPhWxy5%#=6iS7^8EYncJXoQg3$j1L;ruB;k<V7d(FCWN%bF`+ds&w<JY6-kX!Ix!N2?Q08>Y|gRj5FN#qQ{J@rz)<!-?~xxSBcHU7a-Uf*@%YGwfLy|%SO&lPY-=Qk2}4i{YQ-QOkENlf6};yK{fkLw&Sxc9s`FGg<1c`<Uu(7%!&FSx6}I}mqt{NmDc$BjKl`1gCQo%%j4o0cEu{rYxsuGIC2{;k8MI?k%QqRzwEuX+EzOUS<?^0%suJg?&}^1C_rwl8Vaud~LT;MzJHxwg(4SM%ox?)lQKudmc(ajv=|B~HMN{g91<lY4EQ`ud7v1m~9CgI!WT-w$onpD!cV&X<vE=S!*kS&X~kj>z}z!@3EsPE-y3{3P--!cL3+Z=-*~z3JeW#dAaBPH=+fs>U7QkNX$gk`a1R%=dVg=;xN`XH<kVuErIO`^UW@#vQY(SzPB|xb<8G*Ve(GzhTQ+`MeA60Jq;#-Fj{ZcXsdh=(z=)+`G`J=cNAl8TtCbxU~(ue~T+Z>eB&k$3Eg87hJ(U;vZMb_n&vvx6L@MpRf0$>!N<*W~on&dsiG2>+0Jn_Lr(_qP}(UxBB}<;{@E%drmxO*84;shW%IL#{JjN4g0UZ&aYdf{nxU+N8}s!FO3`bFQ@H>$T#d$es0*0l<n7%FYgO>TdTOv49`i8lbRvYbIH5yBIm~Em3P~D!41zPyX_q6WCi5L`(3r2Jss$N)VT3})VT3})VT3}bZk2#uA972slLXE#!=r<dg>I<pX-zMBYWvF&Yh1IHp;w#b8mZtbYGB!p~v~Wop(;K@0O4~H=Ff*&#ETDcXMv(npMy1k6aJ_8RyQfG|ox(LtaM-`J8jdqt;J(ogdz65`34aAD#FKUyqhPP5ONG_u8HeR<F2<zh^pvPRe}NAdI{7X0us(+y1j)a{1mq^v#1t1by2sDb&4cGsr%g27c9Ellt#owNsM+@2mDO+QT>+;}OiqvD<?Ndk^mq?FZi<elRo+J`TqYh9<!ehJOmd{73}zlcA~bOkaSX44;W${zU}yX6PJvrnBLh&Vo0?Pk=rLKLLIOf_a6;YJM6CDWx%&#u^$Ep{4Mp$YFj4jp;P<pbOz&rLmI6D+uNnK?~s*!7oNIzlz2Z8bvhn5zH?|Fux4JyamC0F^zC>X%Spv^dclA2)|_@m+2JUu~Sfw=_p<OQ5chHjIM_m^u;s`p7k7xKA5J%v-zfAZcJyw7a^w@ngP$|pN92d8UjBWeN2T;fu9P$0Ga_mpGFSWBLZvD7a9&9jvVHr@LM#ze*Fev4VjO{_iP&TXe2`?!H=b3!d%lZ-+73c$eW4ZCqYfR<C!KvP4G|C7>?ee;iI4l@CnF|f{uk}IuJezz7I4Qz7KpjGz2~zem*n}J`MAk56y<356{+g8jUeHZ%pIinGS^?inSaKjU|uIGt(GoEPM=n7&HPt3_cXv7d{j|9hw854xfQwegQNap6T=OOmpFLF}DQ>=BGkO!{?)?CD2g#muNgmqX0Stz5sqXG!cF|{0iu^@KzcsjS^@U{L3^3V4MLMgZcF|Y&6PgltI@**TJuae;vX6Yc$L`LBX*h|Mc&q#~(YpL8N~!8IP2=M*Wdxw3dIPH0OlzdoP&&vBq=R6;J*Kr>&A6'

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
