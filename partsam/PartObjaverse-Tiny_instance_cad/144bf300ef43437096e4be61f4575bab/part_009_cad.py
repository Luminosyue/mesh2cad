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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/144bf300ef43437096e4be61f4575bab/part_009.stl', 'relative_path': '144bf300ef43437096e4be61f4575bab/part_009.stl', 'source_sha256': '44dfd925f9ed7bd378a3526da44a07f8a8d3557eb1d738a238b7fea37557ec7c', 'input_faces': 95, 'input_vertices': 79, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.03158688545227051, -0.030259529128670692, 0.37006327509880066], [-0.020483721047639847, -0.011037010699510574, 0.39099574089050293]]}
GEOMETRY_BASE85 = 'c$}qI4NR3~6#hU&KoCTfKamdvE*B6*1ig5L4@DqQeli>4#LE<>L?9Q$zoO4l^WVfI{O#Iu%ci1hg{;)iCW0H*P)jmbcS-p}+H^M4)$DuEbEs>pt<~Mm&N&a~KIeJQ`+hIqEyx|<;wRw~CWR)<h`KpQl7x9meo}pzwQli(vfB8nB`cgHAHv0_-|xtqJ+okrlT<IQGAt~sU0^k&$Od!yBtx8RD6h8GSxc+tS6dgB2|Tm3vbIdeYZsL+Dbw@liKaL?(HJMcEdSS!htLomXFIJsrLB9j@V18DD`^5h9z(d~GUE;5<%tgnmm}NWCVZ^dM)I#pJp$J<ju0;At=TTTJ*0)|)gfyL*NT)aRKIpK)vG_20bem>E8(ZkQN7)B4EQ}wJA_vY-M}xM-%okt?seq-LkPDt)DW(G)bOV8mil(+KbA_k^w@1Z;aRR!Z~MRmo-e94(D%&uP(RPQk92E+q+hk(CfwG0b}!ZSv^3HB%9Dvl3Oq@;R+vM5Z8b*1mFA6vOHVSXue>=O`bUMKzIE_U;tMJV?%_qa{QO?xu{R6`zGx8PYIz*ZK|7RzzI_sSyuW;l`n~}DO6S@=R6pBu8};Ad4n1d<6Rx;r()?vx5_l4fsQ0bdMSNb_sIUBGH`R@7#T>Fqv0pn*60UwTh5D*DGJ)?o0lc}rk@|j{h&lH*5w7es5pHP(zv{mV^?SY}9%bQj=$T(kxc0tE-hRLZbNJ~u(kHn;qPa<3iwL(5J4v|Q5lTGLmRQs;YefB(YMeuN^wr+0AzWD|lOARKX7p`~1y6Aw^iEv|{u^!0G~Z4)!lkTvSXapj!qtLJv|rN2wcv@bAY4kkfO&3j0A7+xxblvX^jppy0iHJw_>%inuP!}^`Q!%@ZeM+k^lK$puTtcT`mmR%uM&*8+4F(h`=$`TZCeg_Cb|%=UCt)`Hd89*FzYeR%VLYbJm#!Kecy5H>%~aS<KunM>9Ya*R5B9J*<llS0_t%79v-E0q}@9JolDbE|4A`?)owhek!h4`^SW@JufK@;uP3AK{)bpc_j%wyM1jBfSM;qYg3ij@^c?EPm~czVE8sWx5H1ykVjnKGV?OpS!ZrCI=Hapn{Li%$ZZY4)x&vMV{+R}zjyvSlLwCWy=_vZn{T%zXzZ3Im-VZ!*JI+N&1$a(v1<$+P@cFl(f9^`?DZGw*#frIUu~z8WWy3ii=K2-YZ>b{O9?$`u`F-G7oJF`|>?GXYcm_J1QgBc8tU{l&+;_MU_?cVS|C~F}X$SyMx<>b(b}0sWp7nt4S%>jlv~*y-uj4tiU7kf=^H#yLua|N);wrwkbTyurSFfQi%1rwuo9m(HQV)18P9t19l#9L(yKz6p;~YsH--F+J7(Cf~asSmdLr=s(;HmXEUqv^;6W2tz+}(xexbQT1T2~TozfgmFZvCgwlN<y6r&Qv%T#dx}xjO=SoSSf8I_)G}p6`eHCm}R9rLr3QEsyYj$n|IJZ^-nXw1TJJ60Rp6%Xr`-Ny6Oqw}kRihgSpvici1)`&Wd;6aLjJf+^{Lzak9NHMr?EST|SQe01~T*o||sH1S3=gkyKkopf{NWsBH_bHO=KHxG^na6VPHB;BTQY~Wn@c!xNG^C0#S9LG4|VVsM2IOoy28FdThcoOH6xZgC6qd5=Z@A~sPJ$daS_T@Z^HH~E-s#`ewkq)sp=ibcMAA54{%Y8%GM=_@-WBwfbavs6`!g-DUtTl+a{do=1%#*}x>tAD-!`fpw59Ge1I5u!DbdJz%D953k3+@1}H*mkPtRb9r1hLj|t`ByYtC9N-XWYnIl6W6uSYHzN4CKC{+%J%4GL-klll2YdUOucZn&&3+WZfp~X3{N{eSbcV|DMRPz|t5qb6qlH6WN=2J;A(=RIba^Et`FRK864O495bSp<9-2GudZ2#N#<n;W&#ehcV&PIaYMb(`~wLxg0B;$8ns%@pQHf#xj^cf!97kw^-IVfw5SgiHIXPj%6FonD8>kV|Yf9?8kB3Kf84HV>nLdSgfTW*U8y$z(4)0`tzfTOXaB_S%3ZJ(^swIH>32+>yL}KAa|g+&-Ba5S*p?fY;l^T-vQdx_Q('

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
