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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/85f745f8fab74184a66cabd3aa1edbee/part_009.stl', 'relative_path': '85f745f8fab74184a66cabd3aa1edbee/part_009.stl', 'source_sha256': '0311c1a6c3ad1213a42bc224713af9825652282e79990693a489bfad177e6490', 'input_faces': 68, 'input_vertices': 65, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2692997455596924, -0.1835235059261322, -0.3255975544452667], [0.2355038821697235, 0.3984483480453491, 0.2705760896205902]]}
GEOMETRY_BASE85 = 'c$}qHe@v8R9Dn#J!a)=q5x;yD^f)<4kY5sTr@5A4aMsweWgg0rEQWOFT<(T@XR>TT2!<HCL8)sZ@hh|$DTjdkFqoz?T`aCYn$60kt+v+6p6By^@4CBaYxT0vKA-2q_xbgGzW2PZvB=Lqk}1zp_R7J|mLq|T38+{k+ikY&s@!h2rd8MM@nPZc#pC2d#ih?0H~X;N%%&+fTen*@d6Fi-B3Gl6G!;87yDVkZTX$N@&BA}GtjcQUzI8`gjhVNTv$J&4YOPMHmHz7!EY^^fe|1Rko^@S<?R7(!1WVfSY4~%|ZwofnogDP=>(|SAPKJ$^ArHTD?SSwdckcGN`}Utht_ojD8y*&ILu}_|#5bD{3zp5AdcC`U!FCXFOU6DyTYYZ|arLHQ5oZq#|7;=Oa45A6^W{nKS-16Lw8w7mclYIw6yMQvyI=G(MFmVEe%s5Zu;0le$V*3wbprmF`U3hl^&i)}`SPgZJML{6!oI5;#u0yKLz8H;lm_J0<v-BA4?lKopNC&He-`VgZEo}M4;0Q|U*FUWp#58!;(xoP8S9*lI*;{iK8|x^D)n1f*Y`KD50@`**a3g)+zeP>0^jZ*a1;4_MyurgO1cu?-Fq5wgOe9A|A#?i@U<$;Z}@J}sE0pOJc9Vv@*d<N`aaH?U5sePxu58(8*=jv)pOU72V<cf{gS5b%J|Qn#sAM)KS#g1Rp-%u?`zCsFRem89GRuqKl45LF8a3{COrIgVJ)I9&wqt;boz3td<*l&sjeU{^64h<>-qJl*VftVm@mAm5%C!zH;|uCb))c$BW#GzC^>=k{1H8c@lGec0p8b+b2TMwLcN<>8b3h){#xWseyK&N-|>Pj<WD`VoWtG%#CL4{Wl+CB-dIB_&Y6w&G@}3Ay%>jWn?v2PpzB95{{2_SFs~{M=jL4xF5jyj3_tt?U;ZMbSNR=0xQu+(9UjpyRL@S|yPloCcRf3OuX>g{`$m<0c>eATw(d*tCj*qa7}<w@(t(@s<zxFXp7S2?_B-evFul_>j&U3-teEf3_Wp%@M)!}@)jFZ<^He9!CF(_`E}Z^K#b*`2_8~uCrcc86x+h(}*FEX-z3xe;|F?Vc)(m{vHji-)Kl+@}yZMZKdE=8fcgM9ZoEuv-pqyjd`c8LW4kX|9yi$k1Cn2vM_rKBOt+wd}cBa>lF@eSWtyWRy_DU0`c$~cOE3Go~-@Vdu|Mx2`iLar6Bb_6MBbh@_5ITh;k$4$#GU;Wc;|W4*h;vA5NM~`ZCe9!Tok<Wnn>dGbHt9lQJ?TQy`2;=fp@4KcaSG{l(#zfUvz#Dw97i<AqfC5;@KWFqUmQUMp#wM`Ar2-EBrSL`>0r{K#46G%8b6dcj&vyLSmH#|iIm@1g3wXK@ucHvO;N<bq=RW(p?x`=rO8N#5QLV96G%&>S8*7K*ARqWNt{6XA(|tMBZA{G4j<w$(qR-M^a>6whmJUxw2pKt@fy-gIhJt5&=_JqKjLuGex&`0A13WjT1^~7I)=tn(;Q;1G~ztcX`~+~euA{I$j3L*@1H(l|9WJxS&t7|@1CC5gnQ3fK9=j!Fct;i>(`h6y~cSMU!i{jWz%R#'

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
