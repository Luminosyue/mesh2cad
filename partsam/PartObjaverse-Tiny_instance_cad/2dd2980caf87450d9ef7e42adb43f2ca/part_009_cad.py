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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2dd2980caf87450d9ef7e42adb43f2ca/part_009.stl', 'relative_path': '2dd2980caf87450d9ef7e42adb43f2ca/part_009.stl', 'source_sha256': 'b557fce01990022e1c9e771c5ab8b631b7f8107b00f83c0cd32877185c90a827', 'input_faces': 116, 'input_vertices': 74, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.19441579282283783, -0.44444435834884644, -0.20834150910377502], [0.1944187432527542, 0.4999995231628418, 0.0743054524064064]]}
GEOMETRY_BASE85 = 'c$}qIU2Kz87(Q*+{glB**THb$zHMTeb}Jhj`-OgEKWu5l#z@peu?uvHHe<AN!6?aR#xB%E6GX2xDK|<MG8~hs$z){-vgnmDi+_L>Z}bKYdgF!YIp=%cdU~vh(I#)6r_cMG_kDMEc1{)vy9#{F{?xK#zqXBy7cnNHl=;|XEHQETU@X}*HvX)Gl}lZG2w&T`|Gvm04mQc2^B;;O4<`IwhQDXD!yhpGqel`GiIK6#k0cJogg!VDPsX^Od~#$w#=mcCZw(kb8Un^~<G+49e1yzfH&&K7rawM<RpQN=PnHxt3f*{kWiF)Xtn<oe0?nUt{izOHHy*P6?9*G9W!>N_pUdypf05rwH@Dk*YSuk3&{_;H%lu0ZUXb6f+5W8lvaPe|dntj@)%YcK9xJ$C`bke?9_v8zP1PSgUwy@%E7zZyvvuoH_y=3;I=}z%t(@n?s~;^XI=gM_=^swLBll-^W>Na@XJ1Nv%J%CzTfJ~n*8k$^Ik^v*$C~QAxTNTe=JZBhS9J^flR1&=C*7>F{nn40&&oR3XX}aSg?u`D$~C3xG-pQhlWxUrzwu(z+p^yW%U5Nc!55B)6y1WJsqnt5>TG!8T0XxCJq5pYa^D&0d!WXyKV<t!H=$>A|LLmh68kkjbgIuTR-O&z*&kh}{UKf7A6=*YVbk4Gx8_fOqs~uy8amBSx*2*SXZ~y*=rq4sch3H~&p(z^pY$~JjP5tT&Z(dEL#O(w;<)@f*3T#D`uQYXKcBiz=aY>-GoNpM()IbXer^7&Uz^{$?Oe#W|D@~tA3gTl`}xir>3=(K&zF3d@BEXlpMNtmv#6dEx*v3%?uX2QmP=CC?jO?i`^UT)w{`74BwfD`N!RZ~()Ih0t%jE+YWH(i*Y4-^_qQ%f)b4-M_4_}yaAQUKwfBg0{XHUGe~(Ddd5<DFul4lgcfOz9jEN}Wul4AN@>B~^d<gSD)rVXE)l=Qvyz_s))gF1YcsPK2!Han~nfL*0bb;@MZx}cP?m*5390q5|Ie{*4C)P6HAh-v;*8oevORzQs90uQw^~FFZcnF@|z#;H*^jHsE15Q19fgx}c>pZ|>@LqUKWe&l;=urV&4^BNAfxX}XtSbk4z#HKSD02v2h#p123UKNX1U7;<VVxIP4jzQ3Ntr|N0`zbLi@>QzA20~M2kQ!fUhqD6_9$}*?n94Cpc|Ze3;_GU`?0P7SO`7<ProvU;2Y3mBd`*jdej03zzwYP0Smxu;W3ms45d~*uok=y`3*oHcs)FIN<YEZAzudE2wsZZT3{J?89d#<dhjl#UL9(!L#`fqnosauJbF;G2mRJ6J$3=R6>k@OU8r4(TsQJGhu|$d?%}ZmcrW<fJp9o7&;`GfM-B2d$O(Q2k80$rkrTX%$0p=AAt(4|9$S##f}G%Y@z{#|R^$ZV#-joG2IK_a&Z8OmX5<8K<<W+G8*+m0<k60NJ92_|@aROo6FI>nVTaS_`lo;G{`y$rvdsBMPhXk)%&048d9CcD6A8P;-weMPo$M&buf%Vf{Rxh&w^#'

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
