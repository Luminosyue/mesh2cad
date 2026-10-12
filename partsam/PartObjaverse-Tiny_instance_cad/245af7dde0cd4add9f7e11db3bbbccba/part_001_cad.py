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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/245af7dde0cd4add9f7e11db3bbbccba/part_001.stl', 'relative_path': '245af7dde0cd4add9f7e11db3bbbccba/part_001.stl', 'source_sha256': '05cbbf457c0119a2cfa4f4aa794852abc0267b963d08edea9c47e8acd0f3b5b5', 'input_faces': 84, 'input_vertices': 67, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.2515910565853119, -0.22659191489219666, -0.206321582198143], [0.3028106093406677, -0.10458829998970032, 0.3379245400428772]]}
GEOMETRY_BASE85 = 'c$}q{eN0tl9LFEtK|w$-@+NWs<??cUL6BF4qii%sDrw4)nwRNyvXu~!Ta@mYR%Vk53$3-hxn5woinS0!;YiAhVg@SZ7JB`oh0|8KhWWDAIltfc=5w2Etqyzk{hZI9^Lw82oQHF6S*ee&MevazejW>t9Pk&yY{9}JwmRw>sy8_5=WeNe#!G~eHxGC2Td`(&S%sI_DxS4&bkuLCv*s(-MVoT1HpRNBrmmr`YRmeXx{VIgmsCAb?=XD*=BiqUah{T$V^cCyZOS&~zaEo}DcHkfz9};2ayRc(j}c0_-)S?QhtkMvN$>TW=k}zwLD{Rt7kXu{++IaqU%iX^t4+>}=DDk(g6kJHk{8L%<n<rcasAV0=z7-_=Rl9-#XD`fhhJXJ;|BCmfAvip*MDR$*GV|Y{+A^3+PM#SKJ#~;A-~_7#&>&d&(-6ycm4hmkDHiA>)`6%OzWWR>Ev;5_tO0;uLP6VmLBE)rLWWV%DoWs_M3fN|MGSoH^gzlJhy)_#9p;>{bj|}Ujz<&czb0kuYbuH&p&<})pu^bJ}7&2WQ6A9x^<1$&*kF&LG?VJ#$ooBajw7W0IjEUs}I+C;Tre<wQErJn$35Z?n@jTBER#_Ne}<^;V#)L(ZS@kpZ4=U*nMq4_QJQ5#<fR|v;RDl{rfNS{H~uTuO7+dIuqUWTwH%R_`Ykhxc^|o8QJTX9_9XLi^)3!Dm;B!Y&Z39Dd+X@DQCYjo$DNbi1&5*ljQXYahCe6Khi6E;Tr!^_Nt|sef}O=2R*2gpXaW9><_%g>(=-fKhKbMu77JSdHeOpJ-itGtxN8&pJK0d<WhgFWDR-e^P?Wm#s2Zrx`)5f)+KwT=q}fJxR2&9)<%Ct^*_DG^J%(Cb@aX%^7eP9k5HYE4jwnm=IJY29_;t#b;(}6l0{x?y-d$htoZI2jnlq?`&Ycg{WC^+UnDxn>w(QwUpe$G-&c3zh`bJJsqYE$KR!1iucve29bNYB^|XI@m;DZnyjpOU_M6!D_EFhu>8-l#^^>2mf8!AEr`5ZU$lm>b=k{Xl2_6^kPwmFJ4)XoITqoift%J7iEq>qZxHuy3L(!T<`&5m+#C4WM(Ya>vqO?~}IZyqsw$MD)mn-Rcs^2G^m;b-Sf-&}o3(33RSK9WHPTHRvi?~i#bHD7BiIrRj?>!OOME7O?q>SrS4fFlhUZVbbQ5Dz0`$`{5?(8Y^_zI4_+IyweR|vBO8DGIoRnjNWl;+{i2Y&*qv;Ng5FgNRee*(>E_!un^82~nO3OLPZNk&UYGkF$r26z@Y4jBQC14ki4z)|3E<YaI-I20KS4h2s|TEJ7m(a2bEG<YU55j+z-8<`584W5IX2c84YMCO4r!3D@g-~#YsWFdGlcnMMkF99z_Guhl<S;%ap3eE=SA`8K};2h*4a1MAOG7r2EJQq0+JQtjTOa-Ta6Of7E1aKrW790tlgtUMsf&G!eV1KYTax&N(ERZ4M{$a8gG6L)c_CwA9`+<XyN#G#xbYvQMI#@B96*(W72A&UIfJ_JHBQucc;0&-0ISXt9CnMv)$>4Zo6gVCngA519fTtlt!PCHDMk_1z^0xT=(@*yMhh{FM#}D|wU+MXpldtqQULJqF^vX*8=-0lt@%NOG?esMN1d>y#ss'

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
