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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/67e2e51a2c87480a999293f3c554d61d/part_003.stl', 'relative_path': '67e2e51a2c87480a999293f3c554d61d/part_003.stl', 'source_sha256': '940373f0cae385af10a6349b15adb9eeaf16cff584f84a9d1d09e99bb2e1deca', 'input_faces': 48, 'input_vertices': 63, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.20713035762310028, -0.013708263635635376, -0.2859027087688446], [0.1377941519021988, 0.2046293020248413, 0.3031984269618988]]}
GEOMETRY_BASE85 = 'c$}q{4NO&K7{^~eL@=|PK!TDTOuS&A5~zqG*ES3Ui82<I)MW_bAh=u*Op8um#D;xRN#*FG1WamBU|@nAL4nkbkLKoD>P^`&KUOO&nvuQd|2*Wy+1Bc?|DON*yU%^z=e+NGI5#QY#nnsD<u9HxhjwSV388Dc@DfEC*1|3683l`SEzdd$1Gs)o#EQh^^+}IAi6XJXxGAF`-D-?fjH@yujKPXAGtXLRP0M{c&$=l?=WEk)3Nj=w$V#(h$Z_DZuwW%DC|G%3`LEYB*@8Lx<zt=b>0}XN%<py4GT5`e{TgHUmEdZ2f2Yp1izoZQn`~S4s44Fs)wwyKyl+yS=_Td(e7#>U#&PF*^gP>TbwD56Q(x&p-GtaaM=nOJ#5;dMzB$Hy5aZ7>iI-djSN4qeV_dueTv%$Tk9Du2j+WJR6g;qu`hW9OgC5QOp@+dwU7`LX3}1qm1Zv>Il8*6*o4-L{aYo`xI>7DcmJaFMWS>vm%X6nA*Pd8?2wa<oe5LrMTXI{ZAL?tbtswr~<?>1SH}Q#l)7<66Q(_8nUxjCzb*|Q2@1Q=%3J`}+W52{DKjLHiz_sGqZq)g?^&s(V)De}}Y~VAJiJwYEzG*zQ7d&zJ0Qi-0?3exYZrZQ2N5Iu>qm)<bHc027c@kGg!)af}Du}yY!aj<PHmb9(w2jW&MJw_WqmH9qQA(TR{R-RGZCIaczqMj)a>G8VH6sV<oV2%qw>^Y9rkpwb$p6!)neKCt)~EjJ8`$S-BVXWqISq7v>cWQ{xrh%vhCUlYz?IU}ChBK@KJxbdFo62riTl9&Xx&7Y)5ka$DYI*7Jw`1U+s_Z;zS@)afd54Mq6YclJgF6*RMYzVU|wbJTFfhURS`emjy~;?3B<4O{DA6r<9^jMWi`0(w)e{Exd_9&wg+CMbG63168F=zD;NFOtHd8{tpYb><<mK}ppJ6nL>=+;XE1(Y1pS*gpZOGAsY8A7PD>S?r>M`t)g3vQ*YG2)&!Zb#z|AM}keB0+_1B)P*-!Pq&&GH-2>Yd06(0b%SAd&B6LB8ITkjILQUBt?+uJd=KGN=(FXHlX?zBHfhzsgp^u|_W{mcCife&#0*jIQiv<(J&ZUpsXs&m!At%1Z%zVX<{?F;ZcitiS3eqsXdw{<7|e~1YoZa!Itb@Mh-e&b@|^%u$<^R>nl;ucyr^~^L{FaM7;ns+!3`5h+Y+md$^H*}$n{joLRO4Q!NwEm5;;19n(6rD8bE%j?<&vDIJPATOf-%^=r4zDO3V*5GX`W3Y${9nDI!Xy6oD@sAjLKrzNU_VRBM`{X3H}+H5yK;1Aug9tEUD;3MPvv^E*!yyHXYb2?Hb*!1ZalZ{r%TO{x}Bwa1IIhq8`$5;(*12xtEHl(R&k7EzlwbX#}(`&*e{n_EEOVkzf?HKl~PNkmPv(4g>qaXwTNS|)IyFyQuCzdOU;#<!|^UDFOHs4-cmEA{G{&TcrVX?pHu+HK=y(Bc>qiIce8Xqjiq}Jj(+St*t@WFFF4K=H!j^far9*G#9lwbN%2n3UM~Oi6Ya*O>R+1lgYD*TPJV10zga75{rwOn#ZSSnJ7@WqFJm=w{{l6xOd0'

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
