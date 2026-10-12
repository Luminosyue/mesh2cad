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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f62a1cee604c44f5a4e969cd8eca06a3/part_003.stl', 'relative_path': 'f62a1cee604c44f5a4e969cd8eca06a3/part_003.stl', 'source_sha256': 'bbb7b0c3a1c406c40a9732c2b56a2d57b80c28155b0cac87708502a233f60f6e', 'input_faces': 128, 'input_vertices': 105, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09777716547250748, -0.005507787689566612, -0.3688047528266907], [-0.0048550795763731, 0.021065253764390945, -0.15209800004959106]]}
GEOMETRY_BASE85 = 'c$}q}YfKbZ7={ljC{``4sCWTZ5LVcgf?PyI97Po5wpbLfcv;<D#Trx=R?yOp)oL5HC@UtlH!rcFHYQE`gZihg5v_^Q#<WS(MyrveZQ7=>{<4iRJ(u@P=S;_>X~%qdAKp29=R4n-vpeFc96lnRh-*3-N=-Q3IGPX^V@Ny+`P<rCHu!^Ct=qbyNF4XsB{f{LqT16GMM7kk)8`LvXmb`hoW+4cr`zESY;9|A^R}+t+UD~!e~EWX&`<r~Chs;s{ds0icD~z@o8fkJJO1OvsyOlM$nzIiE#=)yxt8<{UNHOQY#CF%+4Y5;uT|f^%=O(VpK*Uww#LWzFS=^$KiF|e@gu3p3rzW~{y*}=mvw3>rv|vM-AU);gK1Z7{rWJUSHFJoBd%FX+xh)1U02OMIWf51)=%EsYU@9Kxy9BW8|^ducjHf;;P+SbgzS8>Z*|bt@87i9>}vxn5AmP96Smv>waZ^L`;pc=yZF41N)NL>L}s|YG5gw?Sx0#PNfq}=^cn7x$$tue{YLKVIoV?T!7IHy&wZWyTH=_UeEd6aEBOuoY)Hwke|ocv`+M?u9=$W5`uQJ+`F_1}T-0;7nfsB8Lwr10)-A@jr*L1}7I#Eh*XW-*`Te0=%DmFoQVxndJ${k@<T>s~z7H#Tq)%!l_1gK7#L`}+Z}7E-4{gVj2Lra_jdfY;aV3d99NMY)`W1KBcHZobV*HJRqW^P(%6Ma6;A_Vk!{&LVA31(f$#3{yer`Kni%mOf_9NE{#d@!Gh&-peRG);EdZZs2aZC8;I~89m`a{e+sZ!0eV9`;#@sV+@+}F<dRR8u{%6PK=@eZzmy&`|f>x!?Hf6d41KZL}3A70vFu2ZkyulV}=KdXI)FYC09m%dz=k*BlYcD(fEx{N&Czl%J(UlZrz%{PRfK>Bz+k2(}T@}rCU+Tg2Vy{War-(AFgG7{(de7u-<^L5dmj>C$tZJj9UInbl}cpi*Cz?b`CtXKN|FWKhNOAm-X>@WLD$v=L8`;Jw0Hx(cICHte-eit&YSMH<q^}2x42R+UeQucA`QN=f&w<q~nuaQUAFF*IBkA1Y}(a&90)@$UK`-}5s^<^In|C4cIT@T;8!Po!6{SJPAT1B67UZlToPoMeuA&+A^%;zrhTc6?^>$UpddXzp$U!FVT^9sJv2Wy_8drBV+-_i%em+Ou0v-M?vjC$nrkNz0-3^XYHG5RpQx6gbY^<VA<?ba)O>w1mx)_s(|rA{M{rB3Nv>y*Ayr$>1!Z8>%%R*#{#XvEUD(ty|WO3F-jNwt3^ZOQw0ucWgJ|L-g5T3SPZ#u}&}%=85?QxA9zcsX<lnCVh5)91lV*Mh5QET&OPqYzpIT?{S)7t`28!%Jf$4IgwJ)C*?10=y1f4_yYX2UkEfFw+un1-Kkq3@%1J<p{<#&}uN#MsN+d3A!H4bOX2v+zj=BeON;?v>x0Hu7g&9D^OD%v<6&*IT$}n;~5&`p<`)`qwzEi_WzNmXv9Is&=^73Lo2RPG=|fNhDL#-!7<Qb;27{oC;=1XWSl}HjYbkQ8Jq;3j9@&4#x!U;G#Q)@&Vr_av%uLjW<xWfY2Y-}k%?eDgRrA3)B#NaJHUz1Byb`)0Xi9+0FFm6o&cQ!o&cU`TIWOr<4H88LT5s!foFpAq3Pg!@Em9scn)|jG#fk@JkQjxc?ibyi8!b1Og={=1DXRZ0y8ZJ=YVseCE#3e0aODsT>vfs=RxO#=cArH1Y<We6P$@Xb0Zi#P5bJErh=Vd7c>K$fi<|GxnLJ~7PJ6dfSP7O-C#H7V7!P%6^(@m#+5WyLK~n};0Ew28mpnT&?;~h^4204mtjxKu;*p)<ukxIAG#3isf-#HKm195Qu+JR*+EzSz+(MP^=r@ko5yG_<4e#}8O^`?hS7i9sn)SiCGr=QoxK4'

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
