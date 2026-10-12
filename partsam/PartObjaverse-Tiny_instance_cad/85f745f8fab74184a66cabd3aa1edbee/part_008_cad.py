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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/85f745f8fab74184a66cabd3aa1edbee/part_008.stl', 'relative_path': '85f745f8fab74184a66cabd3aa1edbee/part_008.stl', 'source_sha256': '4313dbcaece9d98dc06765ec75dd13af20d3684b14c7763ae9985c9736483701', 'input_faces': 78, 'input_vertices': 64, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2594183683395386, -0.11751964688301086, -0.33008918166160583], [0.21869279444217682, 0.3984483480453491, 0.22228160500526428]]}
GEOMETRY_BASE85 = 'c$}qHeN0tl9Dccc$j6lr<;%G00f~FBUWf}<K~(O|TB%Un*=+L<2ZS*0GCuBgl$q=F2eVd9C&N{1?vAu{qDV3oFt`wkfG83~OlNG>+*&ha%T3#?_kGUq(zz$wTAjOR&+|U#_x{fB{W$Nr&Z6Luc&1#bY%J6IgB-?~fS$#(hD!HtS4E{KtEO&G5Q~K`E<ZQDxa|e!_8`{4_8NCqdMez;0?D|(D&J_4j8(Pn-R|<5(pvY<O5s0OzROd|eNT0HT_tau*4QjkuGu2(lm6=!DM~5%WUN=z()CfRos(2>pkK6oBNNx*Z#w;!@EyhOUbI7>QT$@oEqpfJ<`ZqnJU9yfR`UCT%Nmb$2lyX6E35O&`>v-ugg^81-FCI_`z`7Q>dETs6K%(`qe}db){}T{mt_F)7xjwo>+vA}OS7oQ+g5lLeo9pr@<#__T;9%_VfYJ=oEN^&z5l#u&xF4{1i!xaxbWqHinFLA><z^~xZH*OZIh@|ZkfIUKjV4iDSLPid8CIY6u)j|1?o4wig@pZy^4SK!563}#fJRe5)XWNAfX3!+}qKMd^J`j{*TsH@aEqyf$!!GB7Ug!65<|(U>$r*B>3!3lMnd~Ej@z0+dsPuU!U+E`u#F_qF3$9o2%gucU}wdXY1OL*X$cs`ws6$tcz?rGLC-s68OH5(C-kx#XN%kV^$^4=`$x0*FDsax{~Lxo~(cIA<WOw_D1x#e5m-dQ;278W?aN`cg4c@Eo%N2@m+1obJIt$&dj{^9O~-yTt)sZk;*<TKKK>(NlNo&%){Do%&+{44sEu_{x#xl+YTYV`X<&xa?0rM_vOf~@a5_|!)l)uXYWTnx983U_#2~}F+bnmz7gP$HejE~O9!q8<WCwH$2w+7lWO0wW77oY^Y!9Bb)62^sVVHk;ddqi@?^@>7?(kh_t_EKdH~PW$u02PRvlCOa!%AF^84Q-`~3@c)jXHIc1D@!-d{WIk6V}0`^x*TSx3L`sJZnG?mG*yPL8;J*w?I~9(6jtG<}Tc%ynXX+Wk|ekH&t{?%R1^vv22p&A#>ff7`cHr{Mdl45(9ft;YJyG#<vjVDA=QL%*NuI*=#zQ^nW3kKUJ?@E&T<0eQka2w!u~c!wWcQTAovxioXrIs{*He$M-v^K;(UoS%MQdwxpNqY=cb&uwSG*X#3+<8D(3V*(NU>s3{*`g93XTz-E1r^{vgSD&uD{Qv#wTElB7<j5k<CY?okC9#RLC_8~8m^hB~I*vS!^~5=()5H>qdE>AUr*f<yP9UUGu2hPNBTgY5M>?1wbUbky=_iQI#A&3>q%#RZTZtvo{`#y03yo<V={(|8(*7~z5$BLj<VfO3Cw`K2I_X@3&^Ch5MuN}=;v~`r(#Zs&!w5o$5+{-lB^^RYRLyfD)tg8)tstb+7}BXe|N05uK%7f@1L;Cy8|gyQ*#x0i5gSPxXbeVTlWOcHiZM}tp(8kS91DpfNw4J)?_WM~0qLb2OE_XVR&zYXk--to5zY}qIYo{I#4)5}C}si0>!~d`h;#(q*Aawfbe~ZSBR`yC7}Xs~I*M{eQNJivj>R0yI2I9vUe4hx3ev>~|I=UOzb+YtsQ)l)dj=j)>YhD3*Zg7SEDFWHYaRd9i;k%BPb{xqGX'

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
