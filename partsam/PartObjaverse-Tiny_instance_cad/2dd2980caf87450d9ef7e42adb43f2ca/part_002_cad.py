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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2dd2980caf87450d9ef7e42adb43f2ca/part_002.stl', 'relative_path': '2dd2980caf87450d9ef7e42adb43f2ca/part_002.stl', 'source_sha256': '04d2f2826c2605950afa9045a3e3355ffcb096a3e5842045f628c6b73c692841', 'input_faces': 288, 'input_vertices': 181, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.20833322405815125, -0.48611098527908325, -0.13888880610466003], [0.34722211956977844, -0.34722208976745605, 0.27777767181396484]]}
GEOMETRY_BASE85 = 'c$}r0dvI0N6~;H9V1Ode$|Jzx8Nf(+8v`WAX9X1F0}<qL10;flBqV`?s2sF{yeXu-#aj{OAxM;}GtQ8ULNn88s~t+;k2^#C2esAGnf}v1de%L^b=YT<&UD&4v*-KvcQ<=~d#!bL&c0eUt<4SHP4pRH=FTihuj*oqw2r2`Sy@qAzhq%W-N>q%)vZkDoGu^5UDIbgST?JbS!vc3EUKtmSX)r+6-=ruDk$^{DywVjYs;(VSJy785dFULrF9jdUbncsrXuVQ8(lQI&>K6v(0k7NA3yCw3z=ibe^M%#H}4NkAqF4!I@e_B{@&xi%jtcZ6T0cW{@2p?o}6_yp>N;*E9s~AHGGiJFBj!>v!J<AFpKULfAUA^r<f<}_%ZeMAC+2q3O{~+^Eq1&rvCFcIo%oW;nUP!Y-maMH<h1H==e9E-`$+^eVjNf&;N67{Cf6-?y1hc;_(+Q{3+L;c=bqPJbIS+xO(P_vo7&5%On5S>G)SYt8u&O#0p!F<N1%{E9`Xx;whmmvGmk6eX*^liL*Pu#^0Ua*Z9w!bv6+Pt)I_Uf122r#(z>WZmI_d8a_zOgPvK^<>!g<)LU@r$Bl{cs*^|0$**C&=j1V9e$S0_P0cTCUE|=P`))npU-cAu4CX}f@!k9qAJt8J);-_roUI4WbK$#r%x_Nk(LDOhlRdrsr-|piyU8?Jx>r8^x4Affe&wvKr+O6R=E*L*^r5Y1e^j2!Z?>f9{oMMEk)HmtD2k^(FX;ZEtGWGprOEM`l95pys-pSh@mJeMaTv9AXQ`!o=$Ugp&)d2|&*ES8xc=*Fw%Ft2xDDF&v90^W;ktEIAF*|3Q%m|sNk3`gW(qDJvh_gqL6;9TwWO~*d?B%~_o6tPuTLCpN%wpHz1h|^FTr0=98Kh<GCvwmUObHhc`;u_^IxYkzvtx9{4JVabyG?n*{|wZ@|y{weR*!)iG%0lSL5ut`C3}DB{7~j1b)%`_WW^tCN2C~VqM~(=Z5FRN6!sk$5YRGZum}}`_A}4<AWdHjVFG5H*VFJKD2d>n}4zK6I<8kBKYFUSzFh*c~cI3n((7>>tQkpKj^8wmlNaT`u{RHzv{j-zt(x+_}6+4@E^>daVdwyEkhlup0eu79<TM5=G<`gfI4*b%q>yfs;==gL!$arUF$H#`Qz#`z9l`No>h<Qc4TyJsIKRd|3!2zxw<Kg>fF@>&bK%|n#Y>x9E<mhp5Z)qbs68H&bb%sns>*4e7-q8<G&Y<PlN6``;E^xC;s~P#dqSLvc|WhXPo%Q=j2z(`iXU($G9FiCsR&cscxLQiuImOU8&A<9oGrxiJlv($LBETMjRhKe|Rp^I*<N6{be+d>U#bd=22arqo6d}uj=u0F){L~x;_^{RrLI(-TLSGjpxz2<@`yz_0RdBx_kbloqE>uC+*Z>;Lfjg<<75lQl0d#x}KkMKgrFb?|b?lj&9IX`+09ikKfa(ct6*9(6iiYTs^aq_jdI7ebVq=jUK<Z|BLr(N6*wn_Z`*Ks&kK1-Flxlf$d+<2kv(*>Gu5bd%oi{rFwnRPkjHXPR2*?kMaFQ$LssQ-kTg<-^1g1&^;$Fs+;1gM_SS|PJZ=XpwDAG9$o()xw<~5p2m%Pgg%d|>pju9<Mm!p9PQWDgZ<Hc!E@@<*ZYWDhukAvJ^PpF9^pB4XlgDtG+BDqsvmp2)?2ok`;OLwQzxENZ=s$T?_aCKvJy*=@0I71>&Ep~lU!HpDsc82*VSjq{l@o7xqp=<ezhr@J^A;hQ%J*>XS$opa_c9X+!w~g*z!*{OUC_IKiP~aD*Atavbiht@JQJ1r3oJkJ_a8Pp8!4%p8&rDd;)$4d=fYtJ_%j|PKB4i9|&99u(b=@PH;C|zU$9e!47coGm!NKhr`!|?X|G21`onzk6pud7uXs8y|BF%wim!-@TXY+JK%2k!mw@U`|W)96rMV;SHbr1$MN<AI0(KfY_H<?RlKgjlX#mBc7(4F+bR5>!mIH4VcU$a&3IbK+U?1S;7wM329XEB-tfAx?Z?-CJgs7F@lXa1fWI8JMtn8mN%-?&dmUe|<7qx?i-!qdJNRroOa=SGtHQPyUwiRX$J*lI5pXDcQ`p|c*SmOnnKfjsv0z(x5Vkk*`zBtWXKnHD0N5Wcx!;Yi-FT{EZSn9JI1ny1cMx9(@wADx#lyW|SNJh}yZ{F9cEoEpxYy$C>9;37$~(~SKpvI%r!V-L#rx9li&y2n>G#IJ@<H?m5ohJY=?k8+_(1xCZ&`dO{h{n%`2hL@h=uZw^gEI-<(=sZZnk(=`hwdn-j=@LPWW?Sn-jLRU<$q#z7AXjUk85?Tnv8^{t~zp{t|oxSOebx-w4*jH^NuYgg+Cu2gCMI*zN=$hTjRlhbDXs_$Yh~d^|V<J|2EMI1_$5ycnDXFNRMBr@$w}r-iMXkymkJc7P3V`K}*h1^d9oPXX%-4ui{{)5JjV3|#iug?$Tlf=m2QkRQRLR<3rClO6b3Ois7*{Z_tPgr`32RWJ`e18+0I5pc=R0sJ1o>oa)jMBW5FxYWZ*{GP<CaH+i`_&S286l>>^6Tw@o{EQ$Eg1z8UOZ)J(4^Q>1Egl{M2g9WfPvh$}o`lPDaTs5R@id3E#lv{82YePDrhxfysrfzl+JmPW))o&BgG1m_|L@@I9XxGd4Owdp*bOev=^OZc1Fz4qws@EZ_Jd3A8}QYDr=_ed9v%e?;8JsE@O1`H8(CXC+yi!jAH~Nya4ozC@oE6~SUit@9`RA$hkhUOsJtJ2!L-Hm>F48Bc`y3C@UMIX{Sm}j`7ru|CoNt;U+{#*htMCw{*@1=KbTl3_vm}%OL-^yf=4Xgg}&fci+7_hxC8!V*ye_99#{^a2VVeIz!$(P!6ooY_|srD{Au_ya5;P#ycS#uuZ4e?Cj8m3eJgBthiw#iAAA&iG)?$8@Z0cl@LR$A;kUvI!6JAe{5EhR{5JSVuoONL?wjb-Dr~#JAHe0i8yG9t1}=WOv%cUr;j-r+5(B|QaM|OH>|5|=xWxba<VWzhm8)IkWEXyxkkf5^zm4xI@YIIA3buydkGCSQCtULL3VvU~>$7;enY;;p11|OOHh$m6t8l5kE%@4kC*ft&TD9)p=0E)>|7)K>f}Qvu0Nj6>yms3E^1X1b_!3$+?M8Xu2{+z4SD0VRo1ghNSxNR-'

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
