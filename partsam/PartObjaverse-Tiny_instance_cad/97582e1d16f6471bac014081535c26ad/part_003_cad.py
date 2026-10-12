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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/97582e1d16f6471bac014081535c26ad/part_003.stl', 'relative_path': '97582e1d16f6471bac014081535c26ad/part_003.stl', 'source_sha256': 'bdd7d404e9aedb1068e3a211860f1a36b981a852bf2ac5aa3b177fd5b186c5f0', 'input_faces': 96, 'input_vertices': 77, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.013724029995501041, -0.45818057656288147, 0.014719828963279724], [0.150157168507576, -0.2550773024559021, 0.18291699886322021]]}
GEOMETRY_BASE85 = 'c$}q|TTC2P7{||YX<?y2xl|Eo$I^96S-NexQ!WE-sf9}LmWU7SZra^QRA`|gn#MXNrZf$O2TOcw22pBlBAVF9i!ia8KA0Gzcxj?#ZEW;GoAkxogYlg6{lD$b1QVm1eEI+9$G6{{Idi^q*#6%1jAB8b`^CAL;e88hg;0?zip5xL<iy~S*y#45W6%3Uf#&MN`byv95A_fD#F#i4JQ^E4G7@Ytg01nUV8{r@heu9~M28L!j~tCD-W`2rG$#4zQ_*8FdA+r<F=W(Mg^U-B|N8OEAsA1TO>{`LW*+%&NsZ}?!E5>&+<xPw&ow_Co>bQf&i{n+&6D$vx;6%gJBLcY()ov)bbbWfd>{F9Hy3mr<~H$!KRTbv#jWetb)B=#ROd;IXPNSy^M$s)W<HPcn{7JZy7;vIySTkXb)Idf@n;8T^f)iQte?xO@XzWzKltm!#ds~<_f+L;TBoVL_1C$psoc3d^{wX1#4T`ZlJf1}e)%AkN2Vx0a_hF{Hn@2n&vjwTLMj*2s6P?V++lu|@*@)~@1}CwrhL1+?@}sv&fvZ`Z|M94^C`@Ko;91wBWJ-sqB_jQ9My5+FY0`w=EsZr`2wfD*8KZC%}sF8KwO+|rT4=8vX933@VZ$SpCc|FGbz7s@J)UH;YUAH+_;vl^KIr~;$kSE^Br*K#+7BwSL*1!gPWfcH-696bs|^(d~db&pX49@^o{0==nHVuvmTh+-u1wBex^ERoce{i*fgd4#e9zD&1SwbNqw}7`iOb5zYe>(QFh@=&AVy+JA7a6i%vK9zIW!4!aFqoueP}I6F%aJSe`52yB@5uCB3d4?|Wg+?<GO+#U2-nu5~ir>f*ev5?EIbc;YQuCl1yRbMN|zgpWI`y{{zq^c{2VUkClm-1~l+bD!Gi(`0@0yM=zYI3N9Mp?{h4dlC8cUYMKcNAWTBW3mqBKf&|Q<HtVWl)LkJAF!|wL=L_~ocFym*!Kb}RG;_HA=*E!fhJnlp8cP>fqmY>KA+6@o-fSN7m>KT4)>k0=+3u2>pz*#=hQfzQ#Ny)7sfQs3+CJxU2U#>1Lu*ML+26m#1A-+Cgge4?>hD0?!5Dd$dpz_wmkLY(Uc=!|3QePu72bX*8Qs^zq#RmANiZ)7&gjKXMcr^av3>LKfE6~%I}g<D<dSMOvZgOs-YqH5OS2iS4OFffQ%h7cFK4F8h{TVNBKq>buuc2`j<(Fbuu<XE8#1Vqx?NGN@UbPx53xIw?TKqx52kVTjAT`J5XDVqXF6s-vD0^ZGx|dZ-I8ecc5kq#;=|yADRcB55FE-0KXo-7+MHl3}1xjRnNZxS_EH&oDIlPx)z~)CbSSf6Fvi40G|P$2F-&{gBQ?TardLV0o@F5!0(0D!S99df;PZ+!S8|A!|#Fbg|@)=!XJRP!XJR|f$oOyfv<vYgRg?mf|kISVD6NEP=+aEy9}S8zDS49!L?fFYApw$=_$Sx*Xi(UpxN+i;Ir_Z{iwGCz7u*7z7xI{+5=w;Uk$B-uZAy!X2ECSzGWEOM%-WNR`?+NerOmzjCo;i;<^HJqUNSs#y+98N760u{k^`l;`D#|$#nN)sUof)P~LC4x82ll{wixFH{t%?Of|=H5vPgcQg^D(6n_Iv1Iq*'

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
