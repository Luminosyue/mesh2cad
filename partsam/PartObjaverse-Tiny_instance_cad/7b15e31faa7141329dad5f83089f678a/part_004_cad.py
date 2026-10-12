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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7b15e31faa7141329dad5f83089f678a/part_004.stl', 'relative_path': '7b15e31faa7141329dad5f83089f678a/part_004.stl', 'source_sha256': '7d8a27f49049610b4e5270f46d339589b72bf8a5c12bd3fbf17f5e7604fbd410', 'input_faces': 122, 'input_vertices': 84, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08355208486318588, -0.04942253232002258, -0.3718724846839905], [0.05906010791659355, -0.03936092555522919, -0.32511281967163086]]}
GEOMETRY_BASE85 = 'c$}q|T}&KR6vyxK&GL;4r3mftv7KGmQlYdi6uJuqM7CSE_4`F2bcw`5>4GF^NJf(;jnN0wXre~rLwD7Z_)u#wnpiaP!J<ZEjWIE{rcu*0e#Ph;iTBR@@9oTSx-mNB<p00FxpVG0cZS{BL@YPY$E>4?eevUyeG^5Di6~`0wv<dQ&P*j2I_Bn=J*?8?;*fg!(7o}*gC4fT9@md17p78rucr4+hxL%APajV$rY7gckEf0%1s|C_wvgm};o-^oBp(OD-63svFr=+$|Ml>SQdXzlzQEPkyX$qK>*Mc!b-{&4hvOz^<8hO-2YxX*`(eYKKiy~Lxz4OS^O3Y8KjAXJ<ZQV#D`)LjE(yJ|`P+Fj&#}{I?D;8|d0wsj-s11Crn7OGU-7P4_dMWg{vV%O{Dloizm&^7>w7*hIm--X?DHvC`*7{7#aDJZ`lVdWpMBO^cky~U8<+Jf-l)6h0hjZmKiy;TFMm(lp9jiios`S`|Hy;qNAdgPXI%4utNXHc*wL49@gY}!v-#>iQl9zD>i6P+>+?Xl%(MP&r^Qd6bnFA=GLP|V(|Nb&pK_UBa>Mw>u|Jfne((G9E%W-=csd(b|6jwOpL3f}x$1Y~nR9OYPr2Mr<MKOo=J@BU8LRH)uN{1I#pLXz=N;Tw`_9_Wk6t!;bnWV65tlrQlRT2sJVxSj#+-jG{)Rd4!%v)?<X>NY<TaDeoU%SA|JopY)3L7N?>%MZ`FPIBNu7#6ihbLcbZ}a~;vEMq-Z|^ca{`~Yxz9OyeSvkq>Yp&V7Qb}Xt*;y0*_YyEe-tNuDNg#5oc5(S=}YAyeJM`*iY`s8y4_#JN&ORA|C?DkxsQsIeibMEN>2M#ob;>mkbV`n_nUCMot%2n9}O2UCZd?XolH;KUQGlPhgA1hlbP;+^=i`D)%8E$O}v%7hOIp6P`()FK<nTedECMy2rY&W!uz55@Ks`acvL|B@P5pxK;B%eDbxe+!MF-~E4(~c39W*!=Fz~T2pWJF=gQIBR`^zE9(*3=wn78&`RFGPQH=A&=)VYBZS##7SHm|zgYZG*Z$Le**qeHIKQsUzz%_o<P>#Ct;VTg3*o$)XEc`Ye+j+F{Xy>6Z@mMmp6XRXbCiphY-vRZ(i$}DShZkB4FSHrH8FRf*AH2xhfi;DO;6oU<LASw|@hIf61zG|x>eSJL244ehfp5Xw8fXc8Giq%?)Z%<C`q=_4v-tvy%is&4UU)C^7owgT?AdmBAG8F%1lRabgO0kI;ddZ(?1PS;+idqQglNYej_^qE7=j*x7kU8xAiQA1JnrDphY)^0^iFu8QTToy5v(%;KZ-e{m^TV8e2mASZS4aXhk5Mf(F465z6ZV+b&49}&;)!O{x0Yd_`}e<p-12cc#L7qF{~FxZDXis4D$w2cLe?JhnM>kL2VK2MK5X=x)0h9KZ2h75kuf%Tr+^^!MZ&-KL{Oy@8YqCM<=u!Ug&M`yWs^(#5_5^+?)L*zHu1l2dn)DGQHCIb!ETu6`o6dc_m``=2un@|2x68N__gTzX5T&P4N'

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
