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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5fad3a288517425e96b5cc4a86ebfb46/part_002.stl', 'relative_path': '5fad3a288517425e96b5cc4a86ebfb46/part_002.stl', 'source_sha256': 'eebe2c87d228ab0cdbf6c217df2ce5c6808c537b5ab480406d91500e9bcf521c', 'input_faces': 102, 'input_vertices': 108, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4676342010498047, -0.17613063752651215, -1.2620370388031006], [0.44283467531204224, 0.17613063752651215, 0.6235123872756958]]}
GEOMETRY_BASE85 = 'c$}q}e@s<n7{?DFq6vn96<T^M3gwsL4+IqM$rOPraxoPy{<<I+F-`PRuGX*fN1JWgGHHhX;ZCwOr;XKMYEI#BiTI~dGqa}HX^nD~)}q;*xO(3Ad|!Ld;kLCp+jq}%KIeI#_c_n|p4TfrZ_KD<#lEH~?M+1sjk^?uDPBodb_PRFZ{8Se&fd2DxhN%(b9M>avV2v!&mX1iRGv?(4>oTMr4^`Y3mfv%GS#$(rqI)&+HD(}LiIt$i)*(w2Z=W~)@~2d{q&q!d70{*8JX&f>VLd=6(_C@bdw4Ahr78wJ2ccSajV+qdf)zEWge)qxfvUKLFW3TKVI&NkjJ>*_-t3CJgbJgJ(1=WJi@$;E2EwBnu32m)XV3)6?>Uk?Mmh;ZtGrga1~si7$26o@=fL`Po#Ko5pNFuc8T+I_I#p#!L7447w;>$0v_-deBsD*W~kQ_Ax}VXS03#wxGPTpTv2ZJ@caFFcKoI~d%gZV7LLS~jv`0A-dM-`sVT?9k+_a{^QoI(^FFOle2K3w>JJQee8u1E^#s!+apRWFt(F9{TaF)l?4sN^1Mh3qbzYSFBjR;%(H{%(f!&ubINocp<D|@0!I$+Om$`T^5l`!MUe14K--3(&ThGLulesSXe}1Tg*MG+5rdW6JUf^Wy_eCDT4RDdi=o^1V&abC;ekyZA%zNmCckOv>Zi+mJ7yM3s#H%;A_i_Hiz)>Fe>imlyiECE}j`IBguD9oW#K&DLI>P7K(|=j!=Jlc@9+`)0?C&P4-`)?UH~2cL;M&Z7dq03{+4jANH_LN=m$^dY<UCdu#`oI!++5@rc>-nOE*=+qyNy5pB;#9;%*Whr^GMw4()qs7<`jnI{urliZV;FIqb1)s!RLEBt4HpSnq+gMHLHh@7yWrFny<66B>kjZkI@3YH2tJpkG{otkMoiPd$AwClX<{*V6R8w%GA_DJpRj;UA*tZeg{{-Z`tLMxSspLJG|~6{fFiJ);#cE{D<ZIYV+28JkOYcgK~Z~WOIGOz(Gg;m~oZtys$#AeJuCWifZyPZhW|)Pwt!6@>vPvS~$aW^k-U6F5~L%ly<q!KuYIS{_l{Q)F#hs#_b!&=cW8||IMpgq8L|tGfcV9T4#kK>Xg@4N$4Lu&G?>_c1NFE-?&uB@=Z=^ll!1kA9!7^KA7O@SZCi9>OYVF$=QFwbyxqbDXE9}`&@9Yui)ySYkg^-@c5-8_YbeD!nuD`+Mm20*Z$N5FLv%vllD0u*XrE=7I?t5|26u)ICp(t0dURreX;M9=NmQh`{jA#oZoLC+dfC!=YR$7K2MaHICpUV7>G9zH{!hNwYmFzW9K2i|9Rv&$@5-wo|Ejn<u<}OEV$eUV~5%=&nw<b4cXj%9t!U6gSM&a@(Av8{JL#@|IL(=SUPb?W9ipzL#_1FmO*w28~La0=DGj!r|s<j`_pzk)lf}ZL0S*HnzWF8LZl-2%q}7=AT4F}!)Nv}(mIS^4WHRnBrnD<g3oL@sgzWK`AT8S!B%2?1?&p2Cy;X`>}oI{sS<uAo-wu@_4!~c!5&A=%VA5v*t!<NFT^vx)_8vpY$4cUypIN31XhZ7Sq#gbEhFWT3g9za1{I)3Ww5MI4Wvz^Abe))p&)u)56k*JpR|Nj44>J2s2FRO54!-hWRkMsXQPe+__^?NQ4_0WEvW{64eAKOuZCZZnpiDsNPhT!)KLt-3Vs!8Vzp$DvfyW-j%@hz;Lk%%YthFt_+_Z02EG@*7d5RxAM4@QqYgj(b@11rrVR8kAAUaS7^kq0n$8E(6cYRFCrbBI@tnoQ<2k!$|A)MfbT4A#5yS2uBHcquB8`D%_v1--lcJ$G(r8jD=@C48m^7V~MtYQ#j{6z#85@Ohv9J?JiKGO~5e3WcCqt=V4<PnIjGG2O5zkUEj$M<Gi_I59x*trz+$mriNOMU!q&e^zt0iqD)sbeAW+H}ZHYq^bLVA+aNZJgaF`qXoIyvT_{>1S2rLzJZe{gV*bROUG$SaiV&SCEJ#<E`0!bB@OSn;eQ%3mkxKgI'

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
