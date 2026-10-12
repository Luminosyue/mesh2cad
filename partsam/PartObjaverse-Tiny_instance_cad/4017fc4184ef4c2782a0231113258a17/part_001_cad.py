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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4017fc4184ef4c2782a0231113258a17/part_001.stl', 'relative_path': '4017fc4184ef4c2782a0231113258a17/part_001.stl', 'source_sha256': 'ac38d88029deb6dfcaa1c90b8bad90d4eda9c5e9bd70e7092f363e125db33660', 'input_faces': 108, 'input_vertices': 110, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.16665276885032654, -0.24781590700149536, -0.10935206711292267], [-0.0009765755385160446, -0.1435471475124359, 0.23333323001861572]]}
GEOMETRY_BASE85 = 'c$}q}3s6+|8O1N4Q6Qp$<smA$5)qZBMk#853kHZHut5+osJrqI)Chth6K&#Z+qCh~vC$Td(X5T8mW;($qlktJ1_=scl8#AQF&i5)O(Ypp#!9Ab(!Jj~Np?HwOs8Gu&iU<`@1Fm+-~Hd+JD9V)hM5$+CMrp4QqEN$MKO+h6_Zk5Uc0`kw7f2MZOv02${6vD*EhN=ry$#0?4i^v8zalg>q=`Q=cthnRU}46tC1Dewd-rGYnNBomX#ZRhILI{xzn$!wAPe6-%pu7Jw94}aB8&rwE923j4pIXen+dJgR^@?OX5x&YKhAhUkQr1B7V?cUlZMxD!y&;J>qMhtvloDYk&KBkE`!!osIf8^ltHg5iY(hbsGFj_ru?@SJt&13U}*A8OUlj)LwM=4Y&HH$HZ5yci`{plYVS|TTh8@x+T8jo!8O-iZ7&pOUG}-S8@j~iH=@|{I`n5w`|PlmGe#8BuBlS>*ni~n1fQEF1|kEI&zkL*dl#}Bq9IHqg|rc%g|@~c=*>wp?>{jsdpR<ME?greN)c&dr9VFSBEZ0-Jul8vFV9trGDI?_<Hqt)c?If=B5<ixZt|3t=G|ldA*DJpZ!Sc^?B$=&wNIFTk~f4Ef=NU{--CAlbq8jno%P47N6CqkJ=)0P=+vP)pwQn_B}tve2UZ)(${4Z)_v=r*cY3ADLIOdKXRT+lziKy&oQ?rKWmrwNB)dCb$*EbbM8~|wLj!t6!l4#dS&~2;wxLiFu#E!)X%+woL~PK`^);Q%uRc~136|hK40ifnVTc*yxY3^xggB>#nbI>{l9x#*41|&z`B=DN{+TW8T)7Ba^&CKfV`DUF}JM=@?L%JkjzJ$ACCEKn}zz0SFzs~RX0if)fnW*9K)P$bzt2(N1Le5bvAv4>+9tyzGcR7T$e9bOOEF2A--+x8RXyD-zffweXUaOaT4|WUJ&0Nv=@G96Z}2hhfzP{y!2o63UZRV#8<rI#doCchX2)|U35g(S=aqw`{1q}^_}9Yfi=iaOWz~;-plZPa5@|QsPr9jepLys=ZjYObF-!1;(h1$lH-*KKlbZ7sjC_k-_n-`Un!6roA>sU*srnh+qc!G80VL4b@ylXOOD<9f#Z@lB?f-sw(Ul}Rx%NOOC<cWhb6}ru>Po9&dR?u7`}d{=BQhJ{vOHEgW#)g&&GbJ?XpWhLkEwz<@9umuQVSx;+E6@x#TOs@V}kI)fWyMzGbNQWvMTY!u>eyfcRQ)_sg#N_Lwz|vTms3C8-;TfS-`sB=xO<`(1s#BCQcQ{`=&8PPq7LMoJU<)b@%$VG?qB+g?RKxx3{$TnoT{@b^6-^*!*lzyf^F_x1INzhS=k_G4jEZ@Hu)e`)zo<bB~ae9vF~<7<ZRm<L}!ln%fB*qc&+ZiV>H8&G`5-m#Zu{uS_5?*{SJ3CCK*zp)(kErqD>*L2A#TnfK`GJfyQ|F&J`*1H7jUNK?a-TocY&liQ_J2D4R-&S`@^5286otlFDIZt;={;C4xG@OQCo!%_<X84xs$C2azahI%nGf#Z`hI;YsVZpCUP8WPVe>3{|B&XZ(?H2gj?Ktr*6XwaB^;@~(+bWZhGpoK$_H#G<Z?20vtyAh9rP;_|6LJOj=?53&`fkiZ4u6*&Dep_Yc4q-{{xK5!)8vioetm&kj`mUJMe!HDW0w9rE0NzFg3q<(ZL{lj(ezyTTuO1T*=^m)=dpkMT9MN_9ra01$mdde8&MxI5}(&}L;6>C{tEsl3f3LSKtHc+!n$KFVxQDpm;I*nJtMxB7mfVqk7K{BTrIw%?O8l;g#AwTm9l@8+4VZwt3qWTDpLzl?^uZXk5jPUo=CyEzT?r)jz-yU%8Gci>vhp08t{1&qTKqolm*B>RGtbqyUy7b8-e<^U^DK|kFej`*UA1=?gpXWIvV}V{UP?}8Bg>xP=I~{`nxb^1?z4;jQr7=%_(NLr{NP{=ML>0?wqjm@OC~8S6E#hg$+~2PyPN!;i{Sc-J@`P;{W?7e801Y2b@PZHIi)TWU`?uIh;I!hr#2hVdQb-vDArVL&uZHl7pzBWPhrO8cH@akZkCEWD|J|kNe~jK?BH!jwbt&eW;_zhK?Znkcaayco_8_@-VVO^-{ij8SFvzBpd2Y_8^bsVX!atUb3OVWM6U!brLy*96_Bzjv!B^P9skxM^U56QREnEEIEc8N1aZNBga!8B*&9yP-l^6kY`eVK%PlXpw1>IkQ1p7kqw<oP9)FaVQ>;PnVdvUp{9~k$QloW)2Q>vhGvk{$PZJC$q$orsH@0^TFE)&OzPw0OtP6;N;Z=hP#+^NAm>rb$$8`~>N0W`xqw<hE+8+YE+;P}7g8(9h2(6ig`7=ZLS0Q>Le8bGAm@@Fp{^l6LVlE5Mt+n$pISnmPhLc=A}=E6Q&*Dn$&0B=$%Yn@7n9SC`Db}}n!Ntgzc#*m*^Ham?H?Wgey01+fa{rl&KvsM9|d#PaQPnbbpEY#>ifpGnDQ?l02+w'

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
