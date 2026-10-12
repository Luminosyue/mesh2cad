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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3d55d8d947c2402498c23c1d6dbce934/part_009.stl', 'relative_path': '3d55d8d947c2402498c23c1d6dbce934/part_009.stl', 'source_sha256': '9ff70a7cdf2612f64d6c611bb9052b9aaa678eb8a9518bf4faba614dbf324d1d', 'input_faces': 238, 'input_vertices': 196, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.41754013299942017, -0.4364590048789978, -0.2620979845523834], [0.4189116358757019, -0.09065622091293335, 0.27021270990371704]]}
GEOMETRY_BASE85 = 'c$}q~d2Cc=6vbabz=D-UY88ZzB9zhsg;F*Pj2ogAtP8TKOodiapx6S6SQ$hSMFd0z#o87`tSF11Al5Qe5s<C8fI?!%nCM?_{}~b!zdLij@y>aliP1@J&N;tcF7JJPy_A{aqL$}%_TsP0y=e9FpQD{TPwE1%vp2uAV(yG-rIr0=&smV-b%=3!SzR-3{Mh12Dc*c<Vb=80%4ro@!vk4`Wka)a16gI|6>}>}W=}1zm|iM;bji%hQo}3nFPT$na_<4d2ImIyvvUJgf&chwYc3&pZqJ#0M#C$=KPwu#rtt762ajf~JE3`?&4M$oe#^N(ysJmNzy7-enujdUDLksVm;2E-u71k{)F0V1=F8aMQ+)P-iwAlQN$L;fMNhi=E$9Bo&gC&4Eu7Hg<c+%yxp-*Aki$;C@5SWv$?4G?`#R0HoabB4^Fx-?{NRrDCt{rL*K)q!=)`p~9+}>;G3oljgM-SF&$;&Vqpta3aGvjtIe64H-*VslaouCwd-;OhE?#@|hy5-dEGlbq@o1na={$oY#~yagx18r&&hr!fG(Ws<!y(uGTF&?DEjxL@c|PFWAD&YZ?;m$$w~Kq(*CwCC)KyKce#^N(T=vuc*w+_*w%x_UeIEbV*`Kwf(Z!?bHObe%CAZNzAKW+J_Vavj-~7<&2Iu*J^Zk0G3U<5tEw}yQJ1%tYPv&+XTF(2EIrsB^V{U)GEa&~kocnpd`8f6ubGv_h9Q!A64z%Bx^L*ZKiR-8RW;yRS=6t`r-xAkP`z^s~za_4d_M7Fr-<bR6(|%)a_YZTsf0*0-mN*C6Z_If<?>ApR&FB5bobQ+S8*}dG{l=Vs9(lhp_x=3Req(O;kFOv5hq>K92~PWsxo<x0H|D<iwBMNX{qlZeZu=wsR(>1n`~8>L9`mNuHM@AQPti%u!!wqiarIly{gJ`5W53r$CMWmTf^&apYpc_){vf#RkDfag@4I+F()BRs{?PM>lCH<{AUOAjr))pv>bIQxgJ0h8wR1kW?XR5`I^{Zl=G@Qc&)hek&fjuAf6Mv&E$8zO_RDl$KXdNq>u2tpPuFibU%%yi{g(6fd&6tKay>uHxu2gO%lY}SoSz@&+|SPs^F;sVsqs0%yyWXA&i#Qs2a~U#IQNI1+IGs-Z#nmSe~$jz)o;1&56$}R3)l0*ocsCtVeXqx&yVH&{8-M<kLAAS=f}L0&hsbE{l4=j&i%ggC(ix8^Cxcm!^f^XBO1vskN^Jp(2mddIe6`_w|}a6XiMuaT>U|C?vK<Qk6-USX~#9M1&=J-aWH94Mp?6~-*R97lf9bb-_OsQoqTQH5zW0n79Ml;Cph{e6(^kM!`$Al<$OMt^Z6v^(D_)-=aZO2=fm9BPv_&~biaH)J}&*mN$-x$Tbi@?t#+O#mFji&%1YE*V*=%6)&17kj6whEt+9dmL;vqvV;`Dp_{h||&~3`^MHbzv{2pY{ci=xUwck_|Gy)$%-UWSM`A?8VcPrn7Ec$`+5#$JFh?nod$EF&g4e$-f+o3y@--j%^Q~5?@(f5>ZKyJVc@oP=JWNI^X6Z|IRH=r*nzZO~aW#u;`i@vG+Cge?+A^vGoPnoKLR>M~#zXp9$`KOUZmnvU_Ec&|g)yUPDA->$yEK`f1Rq$2Fk3nZDUydv~Tlq!EqK_+Ig<ORh;vY6O&(uoj3iuVs&q3!Z|1h%XeC1ani$1UX3gi`-A%4B7S4?ez*2C8$zXe^V{CZ^3SC!v_Ec&+c^~m*@A%3~3XH0E`*1^{y*Fu*mzZ_ZgS>-n(i*8W94!I69#8;Yn$kY<(V)(_#Vdxy?E0IMjlwX1@`h@a}kr!iz_=Tnxm|6o}4Zj+B74#A17b1&3s{9&c(HE3ojl3E&#1Ayp&s09NKYV}WY0!I>ABZekrhGoK=zYrfNA8aq;s=`=WNHYs0KNcu2K0XA2P2C<p!^VI(Fc_;KrX-x@p-0lO$~tdh3|`80u3pjhb%f>`2onHrONk3?u!}X`<Uu&DhHYkpN)Js^e*N5AdB9kd=9ecROPdgvoS;b6{fnI>H*D!&qTf*dYkfBAdB9qd=F&N3Cd?8XJUr<UZ$=zl?Cky-xGNfbfWUTkVPjepM@+sMfsk{JuyRkz|>`){Q42sZt&fZZ-o{sA3zqpL;1^*MaL`O4Y?a;i0@+RVpCnA8Soj%MbMj+?}98kPWi6LqPHlYft-OE;^mXY3r$@FZ4cib`C8~T%6CE*9j*LD$f7qW-yXR=W{AJUl>Dl9DKs5E9r;G+809ZP7QI>dOOZv#DxZ#=jv3-Rc=A!J=XHdp!KWc#4Gk*a0a^4q<vSvaUax!_avElcm(NbmH`NZB3ZIHR0$QkiTV&CZ%C|!n9i@CKaw=wsZ{fvXEuks!Daga1LzQoVEIM5ImdK)4DW8Izf*Imln>x=_8)z%|;-Zumom>9XN8o?I!m$g~ABgjxO#bhI{*&F!Lzno^LUB>6*72Ka5&OqBMYfFh7iKiQ;Q'

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
