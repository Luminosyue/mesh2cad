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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3d55d8d947c2402498c23c1d6dbce934/part_007.stl', 'relative_path': '3d55d8d947c2402498c23c1d6dbce934/part_007.stl', 'source_sha256': '63d4c37895921a34728cb379274ebe7a05c5715b2133fa5edc34462602cdc4a2', 'input_faces': 246, 'input_vertices': 154, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.41754013299942017, -0.46701815724372864, -0.370238721370697], [0.3152562975883484, -0.3066234290599823, 0.22232209146022797]]}
GEOMETRY_BASE85 = 'c$}q~eQZ_b9mk&n1-ceSSD*shyi8q@RW{{i6oFn40j-pZya)`rrQGt`7H;1_tzKR%@A!f^%`(=oKlTzAqgy5d;-PLXo6f|wYb&~W7qcu`w#+}a#Vj$|`Q3hg=RW7@S+eL&o_s&QFTeiobDr~i&T~(wsTw|FyczsVHPh?HZTx7gF*1tGc+-|lwd|-%HqU6>vp>&_%lh(BJyX4AMa}v=(`Ftj+nQ{yOO?%wmCdi8TUH(`t8YrRq-q;CH>I{F#a~*xyE*Cm&D(4DB>i~Wt+Qv9$7bGK9_xsG%FpNgDa8MC;o57W=RSH*G(G)aKd+4N<D~;vZ9g;N=-|IQ`5u1E$&WubGppw1%nMPzH}Z#<L-ohKIS`evzMG$j9m@LYbC<fK{8&rruWdherF9@`{s!Njzj=0Ye^h<--TL0_G5wM2gYVW)OnIX(`|k~@D^Y%;=<F|}d~>4ojVM1;)cRIvo@X}wK0AM>zWQ;ezWSNt;rfB^)Q`tUXZ?h;KI*&cV=jEJCn`Vl@}RHz>D6N+`_uKcKh<~pQ+>BTgE~%sy1w>XP~YiK*LU;X{&ao!dfon1-|f%9cly)y-TH2Sy1rZA?N8U&{&aoqPuJJ}3Fhhar|ZX^`fh&?@tyi^f4aWAK5l;o_t)u9Q+(<d+4!B)**;8M_`%?H+>p%r-k;xoKg!SisQQ}i$IJ7wew;eyz32OEU+Z_BJ>Q$H)A7gG?fP9GobQYB&6CfE^7VV&eDyWo9QjGsk9B?chwMC<r~2uCRJ?1?Ka*cOSf^rLr0?c?2P#AL(;v6=MftIP*LrPV>$v&qYkqwFC*AgZy8cw#7v;wu|9dE3>$v$ree%2BJlJjDuXy3^e%lZFA^BmpUoyRogWs$7<!2lEZ9lkQKmKPpU+;^PANb^VjV$T5*Uii+?2qy@WlMT(Ke#R@Uwt!eFy9;a+f{qrGE@KB7wK0gL-|_A%@2I?<DL6Fd!F9h#r;vf_Tdo!rZJ&9!8(sR7pfDi^ST#%Y+vuA_sNUl@5Rrgz8lI9*59cg_)dLYpZLd9`lI}Wb6uXUXL4rfy1H05cYV}%>j&%X)KOp8EwOF%m8knW#OHpg@7~`bKKbdw%dbZDr|WBfs_*uv>uZ0SrV+13?JxD+{T1Xp`)i0#e)_=sm!tN(`tE*D)c@s@y>9wEaeaNBsP8_1Twn9O-)y;LuUqgubo}7?i9h7|>G+zT=)OKQPwh|j-RHUSIxj};Q}u`B_uP2VzAt(nxqfgS;k)OT>uY|(``{J(e(8CtzI&d=j+DM)f3MC{efPZf{{5>9q5H1>mGkdZO3b>YH~uvHdq(}3u0MYI`!9v^y|>==Y+v)$_nKqB3)OF**lqhkef3{|JCtt*E{1%~SKsuU?g`Cj>~}(bFduwx+AY1I`82+E)%Jt=h+h+WTfT17qTh}#GDb#$|F&FTYrQIqDIeA7SLGeE{;yZ%+h)!Atgp(2{v70exeWcP#bb#@r(67aV$rWzTu59<4dIdg7~zjmXg-`zJQa;uJd#-SD;AF;7QMmZeByj+2oK|S3`g_eJmN2*U$l4_vFMjA9!@NJy~TONdDIY|=#MY>qZBQHONhUY&aikQvFL3UmlBK4w77)0gc`z={c)W?rl6DHNyM|!Sr$(w7M)}96k^eDT0Dt(5;cUS?Z^3J0$L0g6W@ZCTRfgv^cxmWAQrvV;$q@rY6#2r8SRfTXaQV6d=q-3#YM!T(<~lCEPAuW1;ho^5Z>yK?fzJYu7}sbccE4AUGN>~68H}IZuB1bZuow51AISRkM4l$;oWE>yc>QHeHeZaK7byC55W7;hv5D2F0NOuzX9C^?;@vxA^a#q_%M19J`AVPhv77wLL1=}yc694?}XQ)8{oC@a`YZ}IlLHM0xyP_p;hoQcn!K9UITAKx5L}uy=Vj6z*-1*`s27iTF`xP3%nVvg*U@BXf<2|FGT0V3*icME?faGKyQZ^z$+QTEBtXUT8Z8cSHknqx$rzVj?RbU@G7(#UIo{owQwEWhVFyg;G^hq_$YjmA$$t$gipaI{E_fSvp*j2$40aXZHAlR4)ig&13rYFfDgfspq=m|@E)`U-UDw!H^ZCY)o2a88eWPngqOmL&<c1Fd?&g9z7xI=T?yX@Z)B`wJw#W)55NhN>yHFOc#9eAf6+DQy(YI`gqNX}Cbz$Y7o+n`Za)eyN8={9e}&hgt4wac3-3hhOz!z0oI=}7?s+1dMvt1@^GEnFdeY>cSHil7MUS8-VbN3Y5%?H-0v3G?J_fg=&2Teo+Kz64+u>Ggty|H(@Ls;V6+H&aGdyW>&v{`z3xxH&5Y{tASkE0{J)4B}{1VnPPFT-D;jIkeUFd#T_Sd&euHS^U4~4Z?g|(lBwdaL(UkK~o5!U@Btb0&c_o;9P+61?=PO@I7{qeXzo<N_3pMal2&%jT?Pornyr{QPNZ^O^P&!W%4HC1`T#t;8r|K*nZq_aO@?f-yt|1$jgVgKa}|3`Z8GE!5OFTbh%AGpJ^jk8yN;hFyeWrKon'

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
