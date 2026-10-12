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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/abdad363791d456786cdb511082d9d63/part_003.stl', 'relative_path': 'abdad363791d456786cdb511082d9d63/part_003.stl', 'source_sha256': 'b10b80e14b748c61c9447cc5e7e4a9a94a442316c1b02aadc5ccccbe6f864cfc', 'input_faces': 84, 'input_vertices': 73, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-1.9515012502670288, 4.764152526855469, -1.8454093933105469], [3.1122689247131348, 7.9242777824401855, 2.2613816261291504]]}
GEOMETRY_BASE85 = 'c$}q|ZERCz6vv-#E!&Xy)-hn+Dk$BsFxbWz6YSk&lUO!u%oH@yJ4Yv|fw=(*F<>ReKokO)s00E_P?LR-81$1-Z$B8{;Dbx#+hRIq$5;mJg)l68@i|Y=xt?d%#OO^<{{Qpq>GO7O@7=<oOs7Yrt_Q@^?xcHbmJkrLgh%X)wC&m19BE&*t98Fa%u^gL()Sx0>%-d|VxM@!zdh34+~%+H`8Tvw`U5_H%kH*4ZB4sg+}*Z40=%y2wf2bQ?K_%UBQh^qR~GP<6$g9=eE;>DDVJbwTR&w<jrRN82B<On+aTi|_qsfsi{fLGyx#cYVvof*)f0~$&DQG8W2deM8K-*U=BW?Iwe@^gKhC+m9^|p1<63>Z^zt2xajGZoThXAnI5<b!ub3>+xKUNA)*m0LzQ?)w{iSQFe*eLw#$TvQs&xiJI&U1i4Y@HoFshxKt6CV0+vkQ{oPBRZTc_vd1dQ+d$UCB)r}>LoA94FUk&906u(qDgBY&v%6rW6J=lNysggQ6x@q~8%ZySn7@2*VnapJ?zsC^ojMtik=ee;yVVBFpp@|a`!Rc&9tbx*;*jLeVE@o~iEchtPZX&mCwvGeD&eVsY2))Py-dsJJ`lM6Ep#_jbWH}Vhk1o=3FHK}o4&FT%N*%$HY`|9}p39UYQBuA~2xP8vZ#fAD2ZC>Y<yK3D@G0Mk@b#77j192LMc&yubo7cyqYgFHf+xI{6cqo?S^BQlt)cqHCH;;2}KL;95=)7{ETlFP;dYsQ|K6glsOWeK>k()o{PiXa@f31EO#O-?IhUl8q>hJWZ=L2!O9(k;$VM;rHTtD&Y&oOi4S*_kk)Wj{u?fxQ<wr_E%?>nu0HSfgXzO+2=LVu9)j!zdCsLwZ^zhR~0TYtR8>*ISb7OHuFEgZ7a@s~=6)j6zQl%?jYa(fkTxTbz@)4920Rv)i7@;9q_&3MItm4-)?&kyo?nm78>;Xx}MzxvrtRevLqt;T76IkldSTJ`+=8~^H+US1zNu{X7zLqGRf>G+vj{k)#$HLrK|Tj{uSY#<oc-pX%&a>du`6apegzLi^=*ee+zT%_q=$veyc)hoHO{C~fa=gT!LmXRl8KI&W<voR+RIzzyp8L6B+C~RdW=HzjE;y%pD!<8Xp4(8-Rvt@WNCl9(n#zM@=gXYTcVon}(i3}g+<UyCocnEXyphYrPU``&iL`DE}@}O&FJd8Pc&@vfoP|MMSmdaR(IeE}kGL~ab9@MXHqf|~Fbg7I2%*lfmV&4jw2VI1H%VQpN9`<c6^PpMSw;9ZXy0C9f=0P3UH^Dq;CiX3ZdC(l}TQ>8cZtU9v=0WerzU49xnvZ>3!aV4M*tccOgBD}oikJsojeRR&9<%~`xR&_}?BymIbwa3j;U?5ak!_YygT4koGth594_bxaF_;Ifl<|m+Y8gTFpzD!6E~6HGEq)e6{}_7Ejrg4)^PuZwghP%DPv$@U3-Q+#g+^-sP)z@({+Q$6{6LOnKlH*O7u-+sX2=k)!{XH}e*zjMf&T'

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
