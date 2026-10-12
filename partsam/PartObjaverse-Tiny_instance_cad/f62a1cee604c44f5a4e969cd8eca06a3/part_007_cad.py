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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f62a1cee604c44f5a4e969cd8eca06a3/part_007.stl', 'relative_path': 'f62a1cee604c44f5a4e969cd8eca06a3/part_007.stl', 'source_sha256': 'a36b4a9a8d01c77d03a2a10d74080f8b9bd5ae97d2572eb3795351356ae22a1f', 'input_faces': 128, 'input_vertices': 179, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.49945068359375, 0.12114155292510986, 0.16456136107444763], [0.49291956424713135, 0.13853763043880463, 0.19477561116218567]]}
GEOMETRY_BASE85 = 'c$}q~ZEO@(6o#i15DExtMHJMfSPD|Gw1pM~+45N^lr3NK(QS96yHG5&wopZET@?^T1njbH5p)z0`4CZm@`LRU2aSn|sF9c$mf$Z<<PQi$Q#`YM&$RdKH8Hy6<-GIo&b?>uOlP)(uOzj1y3zF+Y22K5G_UwB!*DdvNH-dT^_#2L1{)@9s@s}k3`ub3!?mS!`6Az{6r<7DmQ@vOSX-Yp)sr<XRG5|R$qLohZ>~2tRo2#51sy)utZ4`mZ&+{E1!;TC#DXc=p1iTyo+i(K{G=tCxN+$m{T<8v^V|%lt{n13qTaru@Id*^1dn%~(dGl4`?dLS=U#<-D{5>lH*?PS<W}qW4qe{m$a^|>Cb*|%P|Vr3{0nRykD1Gqe4urBhc3^&JKv=3KZ(2jG%54O{i|&q51TWUJkKlh%w=A#PZCEzfg3;m+_O*1Kik&vu<2Fu+^5%{YwLK-T%zQ=*G=Wz50CG;aaNf(;4ieb+$>b`Jg>(;+SYN)ELQUF`4yb|;qk3MPAK#8@k$;rCo6fL*YJC69p`zOb3ZaK`(*B(N6}Ar|6TpWuWwQM^!UfvI?n6Q+`T@_huS(GGkr?ly*@?0`@E}p?o;+7uLtXTP^{+&TgNSPp_1=jPc`4Yo}8}|=QqdJarb%v?_Pg3FRvf(wSnq7S2Wu??g{*=aCaR<-d#831J?$q*MG$ZEe{9&QaG=J%)9p!<UQ9?)p07eYq=5lMd9u^BJZ9T&R?E?(c#|6V&(iw9$WYQmp!=^sqX5hyqB%x-u1sLc_VsWn`bWb;pk;;Kg_wG*jIHI65~XQl)U6JABe0``jMRbVeXCopv^Ovc`JHV+YfWMpPFeW6X$VMN#Z(;R~)o;+zKvG^4`qvkUwN=dF4-9ZdIje$FYLNDsL<6(2mbsjt`zRK65#K`+*MK@iKRhcV)k5;{0a}?)pCCFST_%9*Qb?EAy(B8*Q^XbmK6W`B?ks+B|bNzh;=ykEbGJ>v%ZStmMNPqY~VxD7SUo3hh$zd|Z+nEq!7-9&4S{p&Orh(l}TLnP;BVPy2Cgo_SI~SU0&o%-!`_RopdiMyh(=1$XBa+?`i&_k4lJGjD4-uV*Z@PvN|7asLWi$7Md=I=w^JKl7x1+Ry6q;PQBx%j0Fv<A*oqpG>T~xX(z=KX=UKeI|+HJ|H>Y2a-7M11=Z$nIta97x$SYF2@)58Oiy0t*^hikXXN#0`+^2;C$a^?v0cw&jrc(xxhRey`;@Em-%?~mbM?}?sNIdv5SdZWRCjW6kO)RkxKQsEV%nz2KPq4)#jPYycPXT+YfW@C(s$bl-TC)W4J#^&flw<ds_M{zsE_=zn3u&w~p-4<(bR8`+ZOJBfsYdI(I1Z^3QJ)H%pZ~&nxpTM?T!STUiIrOU`{t&V440BgW_BlH<#DkX(-Mj^m8)Q{KWHNjrKg+?S%H{zkeHGJCv&aiH_zs(%Gjo&WD%!Q>YH-&ZhesfQ*~E$TM-TKJ8m=SelBt*B4KZ-sw~R7I*IHKT5VZ-#$?w2o9wYD5jdH^Ofry+qnfdKq$j2y%SAvv#BxNe!q$_y+iANE=A&Nha#E@Fx6oq@$!Wq$8-Gz#oA>PC7yQjPwEI_zxk+e@c3n^d9LH>M{6J@Fz(hk=`erMz!Ei!+%VAgS4CUCgk`%sISBCfq#v(g0zzKB>XbcD#-E6Nw1Q2k#<6k-+{Uveh2(3q}8M~qzcIKm8j+LmGFMjLee7AY}7gMK2j;E7<DfEQqmGq3F-p)#iTOQJk<H{rI=$b>TLK$*k=yvJosXa=|f!tUxG20qL#rQCLJKXgBpczC+#P_joJc#h!i0mM12eX5cZ3pM&S=*zXPZ(@Xmhwu&-0w;P+y_R@8R*Hso4S_rj-=Qb@f}4frC`6p|OU5Pl+Q5@|Z>6!?5n4suSN20w_@$8cUJch%nTkCSGRrlQV-FCgXN-<>)GK9@9^^aScu_&Z4VkouzD4d0J6gmfo-8n&G`*8@m{QTxLeVXo=$v#>oA$MOWc7u%x@=T>bP<50)Kdq^3iF{qEiXOS{VkD-o-e}puel#Mz8J_q~eqGrR7!#Nm_n%85j0_<OaHJX6A^U+^E&Y9!yBi&1S5Op~GP|^dWbode2zMnLV^f2l}@V=6iUg@d-^j`?wpK#*h>iHiEa!>WK*K^OEG?x1i^p*5UJo<XkALmA0<aA^F4R)I^+5'

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
