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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ec56d0baa8f492da805fcf2ea98de4b/part_006.stl', 'relative_path': '8ec56d0baa8f492da805fcf2ea98de4b/part_006.stl', 'source_sha256': '2689083b78ada778204a2b81e36da52e98d4a6a53ee067f04425f8ea7eda281e', 'input_faces': 156, 'input_vertices': 95, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.09048337489366531, -0.14547516405582428, -0.30033186078071594], [0.14665722846984863, -0.12284919619560242, -0.23544619977474213]]}
GEOMETRY_BASE85 = 'c$}q}dr(!^6~+&bi-4fP@Q{}t1i27_1TQZU!&Om)3v%V*GvXx(#wQk(XcFT|qe+ZblhHA)@j-RehBiKunj#vxl1ZAEV(cHWiE)lLB^9I5GzpqaY42X&XN{e9rqiC8HQ$fV#X4)Rz0dIsPKS?gsD>*}J7ykz?2!OXQxT+vYRz?x%jVbCHKi?Cy3$L#M|^eN*3FZvN}V&jv}Wyb>)g7g+D2=xZq2LDv8L$O`i913jWtW=G&IhwQ~t!7MNM@czv+>hrFEX4lSXBx=(gk(eU<*dUV)w#^ef4~%lBx@6RjsZJZkh-oDqF3M|>?dtW*7LU+olMTQpvL<6|H3U9ZpUQfeNUB)-{|hdP!j)VVqp`CrdRow&u4Z#35;|DCOp@4j9qzU$mm;(P8V`EIW=spEF6Lw?##xAgHbd~?=b@%3vvQGecJQb%ihMSRyACFtiH^y%t;7yT?t5nnI9EOqRbQ^@~vyZ9}qE{X5D&@H}u`I~ZIBmRo`datET`b;xXKl?oT{A`f;`obqA-+lN`@ckmiccs0JI{s;x&+0hTIqZ))WIQT;+CNVc-zc0T>(V;Yk$-fA_$>=JVm>7su&z}u@!cgiq>lD@(rL+WUo5`%_ZgCJq~?mR1+Rhs$EPIUjEomwAGihg?WsinJ3BE4$1l-;^i9dPFF%2G4QPemdj|O{8$S|lJBT_b$6-DP7Kv{^^jq}Vw+ZVCt&;oNKRtmu71^k787aQIs1xfQ^f2c3I_jII34iuF?BnOP;_DGTm}g{y<m(j+#Mf>NI4b^*>!|bXR?Me2R(#i-^*BG5kKn$&bH#V}>+6ub%2KJ*a;5=wR_*7$7s3x&jXJd(q`vvwdYr>^KNnxu3Z%XnxE1@m{gn9HhF8#M<aMcI^qdpltd7EYuzm@@&%}M#j7I*eSFx_4f$ehNS+~&V!at**mx9}Iu4*vPjTbSW{V~XYA`$zw$%TDfo+-ZhY&Y`5X2DN<QGD&`Lmk+!_tDRY7WmtLiasyAg?`Gq#W!k?NWQ)AJ3KE%mSeJCJ9Z)eWjsgjm+IlS{T}-gG3~5qRipUE7Murnai#d0-wN@yjWdydzCwI`_b%~WPe)^2*B!`zVUPIkjwi9M{9^IV9e+dp{!Lhy&A@!VNH{KYyVisLe`AyUmZdiFjZb!B-?ycS?=H*~-<)8;U$+G3{J7&y+4t{a@H~!s4f$_Wi0^*ydF1atD84IdruatbA-v!A91!1bdldQJU6{i&d*Q#ZQhf7ZgXG(r_My-Ab>eHC`>?Kvukk#3wW6P0zmPhv4{=V6Z@+>cG68iizKDJX-+~|CgZpmWfcti3cgTDkQOI9k4gafZ@wJQR@%{`i!#-xs5#RWkFWx_=Eq{=IzYO30{x<ZpIRO5}1>(1SpNhGS_Z8nLS}4BxSG&~Ft9#LBWi#qG`~`Dcc?)yy`waa&d<1<)bmKhiy(GSCaXH?fY3Jb&PjpND&Dclnqj@qP*M*nGw~sV%-m2TNu9{cHcR5E(ot6dI7cKUP`1<G{a1KxONB>va#CNx@!F|K}Ft<(bp#HD7U_Mp4<m<=YMIBo{`dMNX-|ll-e50)z?~~~^@wNS3;<qfo`_Pz}A--9E7JWAM;yt-12mNfjf%|@c9R8>;@LoN)>ZJJgZmhQvb9PrgC%$P}i~sk-FX6m>@TvI5TI`o=ei-_1?na%c=drH${Luf39`Utbg~CrR$J|P<im%tNz;mh(lYIB$oA8HT#=1U9z`EALH^x+;&e3Shq4n)f>2t+&_<_65b~x|)N?Wx1t!rocX_|@v&sSP~&5u6Ol&P-U`tLu{=4bp@pJ?fsS^wuZTHr`e4-a_4N*zwNl4GcY$uZ<0hGO-d*Pj|m9ZZfSCsK!#6Uph+2gvE<T<R!tF1diAcmj1ac>;MNL-8br;xW{b<S}F$)k?OJlc+J|B=Qhy5P1lBfG7G<eW*d?AkM{y5y<0mdv>=k#a;}>ehkII)JSqLIhLA8jwL5k)5*!?3~DYpgPcb#Am@<_JyGU~Vox}!g=8nWoLWFG;C_@d6jxFwk}Js-48>EZlgLxZlNpMOsAI@QWINSHwv)4{N#rbY3UvrMg&ap6K#n7aYj^fIoS}H2C+?vJQ2UVs$QG&(*+;`=VW`WS>P7Y@`!W>!Q~k*P<UtI@A=F@U2swfpOO7B9qb8GwkyEJ|<WzDtHIJN49!o7GD=j9EC68w)E~S={OUct1if2%r<Qe4I)N-=YO7d*-L(~fLL*!Wu#nY)%$kWMFsgub{i^x;SB~&}PgglO#MIJ|fkeWh%keo@4BWIG+sNv)^@_p2S<on3++MTl)&rm#+p*WfvK#nGdQ7vSp-sCXyy;NWFz2s1a;wY*=If|@P2a%PAkacnbHG-T#9zh*O9znjJno7Q(oI}kf=aBQMW64U#lk>?AhT<w}DY=R~lRAw&lU(fyr^CxT)aO6_$>z>wsE7EjKj8f9Z{GbG@#Ejz=lSuU9~DlAMLp}Djq%og;?cuug4#a-{o2bO'

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
