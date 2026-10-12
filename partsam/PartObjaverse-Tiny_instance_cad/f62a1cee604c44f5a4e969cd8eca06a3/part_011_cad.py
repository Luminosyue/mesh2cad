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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f62a1cee604c44f5a4e969cd8eca06a3/part_011.stl', 'relative_path': 'f62a1cee604c44f5a4e969cd8eca06a3/part_011.stl', 'source_sha256': '16faffb472576b0381621552d303cf92508242e44bb2f66919d42184757670a6', 'input_faces': 128, 'input_vertices': 113, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10109028220176697, -0.11555814743041992, 0.14441174268722534], [-0.09521564096212387, -0.10168205946683884, 0.2839246988296509]]}
GEOMETRY_BASE85 = 'c$}q}3s4o;9mWqJid=|@pjWN1CLo~r;1RWovc6Ik6G>Ev@xg*z0xA!|U<@>DG(M|s)YRz2n43avYB1KQt?`xR5>p?I^<HCwW2fF|(>gUt>m+?RZDM!N_hEKBcBa#=bLRW`&AI>cKmYUC9rE+Sy2J@Q14Urr$R@W-2&+YjI8pDZU0$)sQ#Y)tW@U(ok-qhG>b6JbJe)r_MAVChlu}RKqS}-(N=i=I=#+FNrL4Mkd2Ml3QFU#p$MPR4URvid{krnv8jtz^)QpU*bR{b-UHPu^KR%IW3VQU%Z@*(|aLC_}S*is8bRpMNZTUs%3uE_j=`Y{zw|wK!d(zjJ-jw~-h8KL6uU<JNeWfAmg#2B}Wxw554;0A$;s*K~Z3f1D{ez>@kJyGdp@*bztf`j1HgJdZgNIw-cgsfq&v#2-3)_l(UP+aC8tzt^zqkGe(%01O(htt7miZ`q*TY|X74!A!KD!@$=~3i4{5j+^U@hWL^viLLW2=#WeiQQ9T7i82vJrX4G@x!jN`(Ip<nO&Y4*r-6GQJ+)=<wBZ(^1b=PG9-W`xv*O$=QEpDdOM1&KbWtUix~-cIoTsIha>ix~zk~Yp1M_m^Bvh53R!b-Y&-a#&toQ(La>ys4crGeR1i|5&OLK4|ZbQs((sfdAl6zHFgvHhQCVR8;blz=o+k7{1?(UJ~L2<h*b_>?U;-@JO$sF^Ly#*{usyls?)9@{{Bdrr{cPSJV$(Z#J*3|Y%lUT6Og`EITiW;Iw>Ii>+d1|)+)!mL?nFebOQ3<cO3aN`;brNbUAMDiO>9YKiG3M>ToAT##hd^A<x;F(pR?imcB?j>a5SP7qNe8j-bwGqTx3ux63>u4<r7`T<qJIxBBe9R{k;a_YFq;j6<x$VcB0BhW?$tGH0OdAAJ6r%wH=!i26@XJZ|r=wH&~>m%1VUWAX3G`rq1*I%GfN=zrHwnvL}h3_+dyz!!V7j^E4IE6?1szrH_$bvt`X)^q%unC~Sw@_%}<-|nk9F7!WJbXw+Lx)1Yh?16PDc<P+2^Tt-xe`;^+lSwaJu>0DzSe(0S8_&!2{b(=x8=D>ZD_{Q<@!J}4&)gU#*GtKJ9rIn0hJ9OjLi*~-A0tj)JL0r$@!9?0pe^u+;Qlmz*MfOPw4gr5ug=?j@6{)f=k24o$6WA@v>eC1tv~x3;(zp^BY)%8Zp5F`h`KfR!MxnN9sRw3`!mj$XP4vrdOwZCx+L#_-^=fKj~K3Ps6+i()L9%so|#)Q?$2&J>d@&2i;6I>`AM>F!E@h-UlMh~k-vL0>hO4u9M|Z2*yr%C{1)RD^u@e#H(}fjE*VFC@k_tm@4RQc`hK6?_ZIKNyq<Z>;fqgeaZXdO;~c%U0sG<Ne7@J><ar5ptVjIv60FO*R-CUp>rl7W1vtN5Ps@6$Gu9%{lliFgu6_Z#FM1UtexHSMpX;@2kZ1o=?6+6Cw%dJUK@$9;0Rg+O{jv@3yX*ZOe&_q8^Sp?i&!hgM;;>!~Q`_ynH&BWGk1g>#{LcLux>@d9?VZ(#Gi8bNy&JaR+<meNbvs`#<BL5BSl`U&P`As?$X|T}@3p2T%<CsBq_6sKVcb2>I{K>}H+^<r`{N+^*Dg5vYp)%^duK{ZyWRKZO_Y9c%+F>1YTriqTcWUz;Wx0~avR`#et~-+HZfrLgD=lR-Cn)u=&!%|2I@av;GW;K(h*1h>TBeA@M+X%_Pf~US<TpQmsh}d&BXn%{vf`8cGkgve+TN8cn<HEsAb6KrGTTJYF3S7ziA1pWqj|RO4K=XANtSjfqnAD668Pq6V!7W=BuiU9lrR3Kz~t&I(MAHyq2E9{*TtMpTF0E{$H8#^BrH+uYUgJExoICG=%7GepQzh+dio+QwVWa@BK+#k^SF&QfH3-e?O^<%^b?jmcwT8B<d2frB9M4k;hYu$m7XlsSC(s$rGq$<O$^IY!+8hmy)Z<HPl7q8gixCzC+EWE+XfWM^WdIN0En9XOoAMM^NXGN05h6A0-bXr&6bpQ^^ldRq_MmL^g|)s1K8q$b+emlLwPCsZWqI$q!QJk{=|Gq!y4zlC!Cgk+aEJ)O>OlIfMELIfI-|eTbY+9z-2S9z-5!wgjp|9Y<Ek$<)c@WO531DmjImMx8-UBM&j#P--4^2H8>%IgeaI)yO5}Lh3}arQaqOl4nszlPz6Ho<**pR+BAVOs*i$r%oYTI)*%-Jd-+<Jd|^oNi8AIB$rYP$%V|Rlv+Wq;20M7Fk64K^<zEzvEKdYch<i@*QcA=?lYTprG-<YsrQjB?M03z$5Q){W65r60@+f9>?Zf6CX<tyPhU2RW2imImPV3e$S!Iq+0rg#7deU=P7dcBqNuUtC~{A#o9t#zJ*hF|7>;3aZ?g?B+x-Ifp`{b31H?CXrp4BsYCREV3o%<5wL3L}Y-t?1J2{^EEpmQdNN8NxfBKWqH;--wcKm_p-+$?R?b&}>V8*)p63ovFm#@B1^WQRS@>Zq9zW|B)RzC'

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
