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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1b4484ff850e4580a96eb29ade0c98a4/part_009.stl', 'relative_path': '1b4484ff850e4580a96eb29ade0c98a4/part_009.stl', 'source_sha256': 'f1bced83ed82de5ba67f4076eb84a62afc29d8e29cf12ea661a7f369b66954ad', 'input_faces': 165, 'input_vertices': 112, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.0019346175249665976, -0.03971998021006584, 0.18495336174964905], [0.04171585664153099, -0.005014470778405666, 0.2485923171043396]]}
GEOMETRY_BASE85 = 'c$}q}Yiv_x7{|}XHdfdeu(A!goxxbSl)+$Jc3~@*jmuaqw{aV+W9t|)26SVI0i}sx5C>?9ku6+GhlwUc#V8-tNR1jU0*g_C#wd01qwxbICWaV&pSS<_c+S(B7;W;;|F_?|)6?@lJ$*Az?T{3^7JKAt#hdEyYr_SKWN3D++vo4v-R$cu>e&Bmk~UI$`9Pm>Z>;ldNz%HtLyi_-XS3f?raLNH7df1|qjjIZ%iq+|xX<6>BVW_h-suy*v#n{rPy9TsxOlEppEup9Kd1l4$1rgUk;eBLt3-R>cOSkkI{I710R61F7j;rcGEa1wy|?g6H+8`A<8iZh{rV&z`<o|6ExtVZB6aln!B@$L^fS^2dcQp`eQ{k6`N+%x=|d0wJ@R$Re3!`U$GY#Cy<ReSR{DWm79X<bzfN8|aP_9;IPlT=y|>Ihk{$Db)93Cc^!GJ+{J<XfDcPT%upEc`&}V}QeIUho+w8r{S07C1U0;8a(ChZ}FU{Vi&gatFgg!FZm)KAF+2VC|K38YmN#tFRx-DLV*8-7*J{qyzP2?j<>!pw0E<G)M-o^9s_$RO2kgu2KlRg>_2g!TW`{X?6KV6OaU{$|7&r`(~@3mhK%j@rT$L98(Yto03+U4^jkHh!OK634suw||ee<Z#BC@AMD)X^)C6A7lhBK_t3K6#w3ayeIl-_xb{o_ry8eIC3kee_mUQ2L&t%kuiXIcLD^1OChX=JQluy>8&)R~GMWC=Xiv_ZMS+R=qsFzBTr~ln-U!={LVG<z26hy&zw=;lmqduMIDd@5}W=%}vYmhyHoiJm=i2Ip<!@x$?U5m~-ycoO7?{+&E8lKA3av)ttw9%(?Q>G@K9SoO?Cr%17YUoO7?{oO@%=)w;0zQq(o3FX1}E$E_oL+&aR?t)qHAUq|MRb!6UHNBFpPWZqau=8bh!=gHTRd1D>9SL+BLw~ovk>j)pWj?5eD$h@(RYF+sE%esSoi9YYj^Uu5T{PS)chkf2%AHQ`@dVZgI>22xxeM#T(;GFsR>OSWB;ydY$`=P7<p4s#Js`C6ksXV{m26~gv%j2;7wrgRY^!z>_J@T^j{QH!9V?LQT<`bTOpK@=^C-cU9!t?J_?v456Ud<;w|32m3m``~AeagKtpUfNcdF9Xr`M%hGNqN3s(%K3_^7m}t6*v-(dA3gr1;>Tu`(^vOfbCenY_<;!9epf4-#12YY<okVr+J_0vFx5dKOO#~B3;ucHnDqdZ8B}0Nzy}g;;r-Ul7F{#UNHavZk;EKbC@Agie3z+_vjR<M9&0Qf-}%ga0WP2WQj--U2F6#unRl_T?8Hh&JtNBGDl=7LOdHG9*Gc-LN5c)6)6^}Mu?Xq#G}!3!K1<1=xT6@$UKo12yqQUY)6-X?cg!!72s7O3q)2T#Pbp29E3Pmq*i2+$ZCXmAwryo5RXNOccE*+yTGmJ)!@}QRx3IW+zR%gbHTYdHy?Tx*avPwuLQ5eduu`GfOBv?S`gx9^a^k@cqh6BT!ZVo6P*p-32s7HgPXu!^m6cWthX0E3hV_pqL+ai!8_1P!PK+C)FZ(=z}wMTVCo_;^%C%Qa0A)}rXB%q0B=KQf~lQg>MHOy@K$ssm^uTz6}$#r3Z`BRUISi>5U)dsw;;q7=o#P&@N|UuDTFv5JsF%2PDhAs=u&Vg&eev_1ZU#9*w9(vEUbYIJqk=c8cdxHwt<JC?O^ILVCoz&buO4X4@^B4TqrVC#Dfq&jS#!h1z<P04m|}-?Eu$-%h1!nW#DpzcoIT95$ymwaNLOq@pyCrcszIldMbDVSVxG*p$ozENES&#h=(A=spu4N3jQt?T?j73wM#{apAp$7(jl@J-41TY@Ao3adl2HyXb;$f_1KIMuSbYCq21t3;Em`y@J8?kbQ!n|>#+eLu18M-Q>TIJ!ENZF;5P7X^l-4JHYwRY<e&a+_xB?}i(vUD9{)@0mc{&+mEu^&2F6pHnigB!WbJ_H59rgP{RK=PB(M'

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
