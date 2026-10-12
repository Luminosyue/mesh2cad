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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/358eb80d4d074dee8cd65b4b0fa187f7/part_007.stl', 'relative_path': '358eb80d4d074dee8cd65b4b0fa187f7/part_007.stl', 'source_sha256': 'd9aeae69d848dacf92ff5a03bac801fd90098a6adf0dd4f80f73d628d3fb2e9c', 'input_faces': 206, 'input_vertices': 184, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.26047074794769287, -0.07736463844776154, -0.28776514530181885], [0.24444222450256348, 0.36174705624580383, 0.3011611998081207]]}
GEOMETRY_BASE85 = 'c$}q~3vgA%8OJvdsX(PbVnrZw@*ocqMBWKOatRTE07-1Y3Q4#T5(roll7JurhggI_QSu-VOy#CVAOR%uatN5*j#v{2!PwfCQ9IXGVzotQq*6;QbiY0SJ)E;S&UD(${O9}c@7uF?&v*9jSuW|R0fE8H_zPuq4GBxV0~jNHp9QluxkV-Ui*t(~Tv@ozkM$Rv{$#A2J8w?<6Mk$BTOYL~w|H?;)Fdrxa$bB?oEDW=P*hTsvvN^E(UM%^({r9G&gHy#Sx#XtZ%2=g9~Y;MjfvAXX#eA1A3g<r=izr-dDQ+M@oo}L?W^GjTP@r(XPe+YUr?hH*8=0~t=xU^uSS22;|W?PxZW1`ju`*Im2+0k+6~U?Kd4T!a93lu!ADJMX?5b)(`&8$eVMVg`AhDeFxzoHT4;^ndRJb96ZZsN75C*TUMje^=mTT^7Zcue;(C1M-XtqOam(PJth4u*{H4qqYk&8N=f&r`9_~Ka>co>49T5D<M8|qcuGUj>wVpjV>M6NePs!DKO0L#Z<+7gavyRIm1`gUK_?8uCZ2WG6>!X9WBw2a))e6BAPucr_ZgBQ-&Q@FhUH4as`#HI++19_x;QEaFcG~&}{JD<W?q&L^RtL^jmz7w#YhuE$1<$wlH@U9#&pO&B=5xwEAIaHNV?Nr37Qww|Dh1d7c5J(ihwT&G8&V*~k=%8wtzGo53@){DZ^tFUeK$TlY2%+ZcZ&MsIZE!?GsX7YwdZCEt`A(@EXFxDxl6QTx;w>vyij+>%3Y~vI-TmNa#>Hw)q3{esHZo+tkbDJCRgesxmq8yzfvEQEA^3Ft&cDN_9an|%k$0&{`%D}@tphD3eIMgp0)9m-5r8&JlZPell>2)ZVET+39jn~XK7#B#*y6f?}qn8zE|Nz!CfI<>o}5oryAV5`3o_QcX~g;+34lA&y`#s3y%JJ$+H&(FONTKoxjS>bpp<+3@+!dayftRg-h+?^V52t5chu}-&n7b&jEjH?0M0@?yb|*c5j{aJF(u*PBfmM!r92Ow*_CY%f@}#8J$jCFDnrJ-B}03dr#f3Os?!#CRg?!lPmj=<m&#Qa=Aa~0e*YLe3kc+%H{jW<jVV~2gmzJa`k=GgX4X~Zgf;R)l=oNp580BD;=Mg!sYYQ*W9k4*yDTx-s60taPxcuuAWa^$zPR=?{VIZ_r*M0mcM7^o}~u&BuxK}xbN`Sb_ni^#{J^^t8iD-WE*#XY;ez9e18@0!ut0FF3%9x#deBy&aQtUzUPwbt1cOQd)u$9{n^b9<9jg@`?%y;?jxeUnS0OM`u{6Sa6PQuK90La>|^?-H*MqSEA|=t+loE*aXvA)EA>m;JiQr1#JJug*KFLi+~BOS+CI+b;GdoopX*-m#`PAeZ}{84wLTZgJrM?%&&BNj%@x7DcrGf}@LbGs{%LUeTvRTfi^+#gdEaS#$<^`Qn!(laC0ECHe;E0Dr~B1DGPt~7PteI7Ne=5!<#HWLuC7Cs%lWW`ugjAhz88|K-wQV2aj}o6>sE4g-Ab;mTazp6*5t~%HMz2G&CgZVt=V5$x00*t*1Rue-J0Vl>y}kk82dH*Lx_m$H!J*FsHpd~kIvh<zj!aOUVpUn&R&9hYf6px;KCZ?+!Nl>L~U*Uu@)<5dp|oYuCIN$+1B5`)TqzE@wRc;;B4bukrOA*E56fs-*kN|>g*|<)@tMPzY*N^$joLd*KeLT#*ei3*W=$2-1C<iqQ57mQ=GTd_q)lJ_q#Ue>vpGl-r@Fo-r@Fonp~-;HtJ@(Q#~bD>uL5^>S^{@>gg@(cfqNiCRgeyxmr(?EA`Y9)*D<sk15<dkAe3%k11T9$J~AIxhS}DK9pQNANrOQ8eBPlO0J$iwO4j`i1C&4u*&5)lB?%omCO12R@Pn;{giXKx9zsz>bYIp)-BHc>c4B)pJrY*p10-SLFu+%f4bVf4T<i<7^yc4W_dZ5pMD6^pN!5w{p64PuYUR&^U#F<_otr|d=6{44s)e&P3BsSxCEZ!I(Ukk;3*!5Uk%^LHI1u;D-j~U7$UzGBEJzL|2jmzfh(D75?3+elkgOuhNrjzo?;VxG5jH}BV4a>okn~E{utL$u2YC7;p4cbaE(NC!6$G{<%&m4f=}gof@>kyPq=1qEr6eeb}I5Sp@rZJ(U<&euEAV$5g&jb!Zn9$7-AayLtJ584<c&tqq)M74@ZvtC`QZE$cG{~8rNvZYsit0;7Z3l(lHnE!?`k$&p<8$b4o)#4Y}dCm)W?F*|-Pt<G7-^CLoT0AI}wod<=5qkROjeBaox^7_LaJv4~Od6S-oMk40__a#6@fAvY1@jX*mVJ`yn+J`z3(F$O*c*N_k3TEyjtm<8|8m5qEha^&eR6ZuT!{Bcbd@>$3+T;pfy!{7&T(Kgfvv6saUM4MtD{9}xMo@VUFi2dN_bM;5QKXQ-ZI=cRD#2>;_41%Y47yKZ6{(XqO;qOQ6i`X0fdtCRz--~{IF<ubzLCBH+0oOfT^ALYz@dMDN_&EHtT<f`V5Z&;lT$_>Kj2!tQu2smdLar3oxRG}wSA=VFEPaYB*Sc}N8{?CwJ(Kp{6vRj1Y44&vFd1<gJnh4|%-Dk|J_ApDG8n~&Ej|V96pT-v_D|Z2pGI5@Pka&>#YBrwMmrhvNyPjcF?WiG;c5PdFn5X#@S8AS9q}1>dIuecKaPGn#%n~r5jpZ3FyD=cYvJkL(FEUwejD-mhmb#n9Ql{H9_8AHI31q$tD(%;>mGoo{f+j;5N7O~6o<i691b52ABGqK9|o@>4uv0z&(om6_?%(*j3J1j@S*5K{-<0kxV9s1gI|f<4#e&7g~;th+yS4*wT$aI#4YdzTu*WR9I*_3IafZ{R>bGwmm>Ew#I5kvTzk3d5f4~=4cZhBTKpcgDZXm))o52^j8~z0^r^=f<jc8saqUNZ+2UVBo8m7l{sput)>?cy+T|Fd7TS+K`!NRj3a%<H58^K^emB|_U$OW~v?<nEd<EL+seb;!0pImsjCcNY@j|fvhogF>{dj7<@)jS<Jglat-bL>S{$lYL8(0plRQ4Z(eAtr'

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
