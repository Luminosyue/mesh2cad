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

PART_NAME = 'part_014'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1d515a6cbe847ea91e2c5680b8fc67f/part_014.stl', 'relative_path': 'b1d515a6cbe847ea91e2c5680b8fc67f/part_014.stl', 'source_sha256': '2c6aa272a10791d354ec692b9f1c79e572dac274e86c9e3684c582ad5ac1c67b', 'input_faces': 192, 'input_vertices': 120, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2250165045261383, 7.496484279632568, -0.21477729082107544], [1.4011082649230957, 10.652337074279785, 2.159986972808838]]}
GEOMETRY_BASE85 = 'c$}qJ3v`WF7XIT=?+D_NdgLdG2$G0I#52E;2oe&HqzG;zH-Zon)uP&eDTA@9%Cbsd?l8u)r5&%d%2kha6)~Y6HH@q3*<nOIB3|>KZ+~}O*34S7X6{;h?Y+OV&))m&v(NcYk}{xj6<<w$Ew!5At8X}KX_}(iny)t9UNCL^SbJgE<S8?}G#}vV=jO`>4oglM?xjuFW(8;43&$1&ch!Tt=fniJ*MoEN3#JuhP9BqAkZo6ZLS|l}-NFlVGpE=sy-h^N4(;{GkoNj){eS$`v{EqAj~>};aa&<rkfC_9OJ%Vt#k2hmD_rk5FHqsGoj=|KKC|R|g&VQU17QEztp^G>4)_-XKdu3H^q5f&`<7{k6z;6Lq80EPH!2jaeLCl$!nOG!z+HiJpTK^XegJrt`7IT0c=ym0cYYZ2ox)u$ign=Y`g*}%ts<ww9S64vUh?K6_^(y42kXl30NgAtM_hec`L_x;^_7y(N0S8KxEHu%-4oz?c`oudFOT^ee(v6Fp>XZ?EZ7^49!0=&9ydoFDr~Z@QF*(7H){hw#??EI6>bYzzZL6B_&wI;ICbP1?8`#_gu1=*4(x5MT08`9D_aZP{|xfCE#8SbXics!ME>&{N!{Wb$a>qXcnj;OStj}SY=r!^68!_k9lk3N*ZgyD)LGm1a1+*7d|B$2dr0yhIq`GYAFL#K)*bQ``?7xKHt<tj#s2+?uy+P5+>W>>;v{Z`#5Kd_?!<WA>k@a}V(EwXmV6ESxvPL{?M`F8rmt(a;;vscf7oZ%f`8XnNB1C~qWY-6`MblgH%jO4gP&)~=v$*pbM&owee-vi*LR=fQ`>?5G|znr+$?%q>TKT)-0AGLAN=x1=yS)b6?ajG^V<$!-%1XlpS4gQ>GQPBhmcQP0`k|hqa~kpkG_YW>HB0|n+{0a(}Rv7&%Hs2tM%zEcvvxT=gDC4?^r5$Ok^qiXUviP-B)%W{@>jXT;I_T^>=NTxLQ{Darjwv0rt*?TVSsTnI|x>N}$y9-Y?P*yH@^)@rp>))A5rXxGk;ZuZTOb9`bh<WFQ~ggRSS_=d%RV*-V^!6ZNfm7PxcvQrX|!u86Bm@H>z3O(T$}^U6i|(OMt<8}O9j$j5dgUFsPVZ~^(48K{FZcqII|re^?m*&9n8>^pJ)*z*1W-0)A8e)!;Hsn06ig*fST<X&nRDfiWiEZ~l}7K@+3qkx<5ju*UmyX^al_IKo5%)JEuM?c_(Z#C(M{^x+(4&TGNw2SxPN56FgxPCQX?wM~6OP-%3UPk^2yRcqkj6ZPg&2hkOOXng_m(P{Eat@yYcPyEWbr}Qi{095vwpU=^Ncu#dRR-KP{0?w)_5#?uLeG^+A9lP7KYc#NdX0k*VDGHc1-P@t>$1N~-<EZqSOQ$DD(6V^@<txUvZ!nD-=wMZ)le_kJ0lhe{`kDyOYy0|ZCiI=$N1Lw1&`Z^xUTndZ-C#FJk5&IpAoN>3%FxxOW5muW=s83(td^g;^Xq&IS?myt4|0XnJE3U?8<G#eRLkUbLATNw>6)J{?t$Q`aA4v_{n)()f)MjiBTAL+*vF2tbJX+cg2%|8{SE%gLCf;oF8q(4`N@o8F8KM15N>tUV97ndGXRG<%ePCe7FI)?i(ljTN;6NIg)mXeezFoE{eX8{Yu~Q57?K?l6!UI0nvNa$NF43-$?z}oQ1t3Fi_TAIam5H@9|#vDUSxO4XGo3LbswW+R8z<<-FIGy8ZBp^wa&#z#YA=A%F96{j<OWw*WV4Y?gC9Fhllb(LJ#b%@aK0kkswsL&-BVMDXLY@osR`OTxJ8WOwB6ct`rvw0$Ui{$4rn3y#S?rQH+z2lb>r9dhJe2xx=&`h$70-o~b!lO2)3ZF7E;ek(qP{xi-e6VH_Q!{g;r_jZMMq_1sQueK)${<X%ZWPRi2NZsl^!TsnejYPjVO0U6>Eo7Y3w`r{Ok)IJD`}G&(ujNmYbGD>Z@_#b^2<ESuDtHUY)78lz_l~pWDmlkXPDvdiLw<oDXI(i@)1=Ney}ICw;(;5_5`nw2%TL2kVHR-Lr{Plnj0s=JeKHfczWR)OUlMAfZ}p`0VjsRA`(n)dR{EsUQMrfC{48~g7;shmToON1mrLA|TKL{L+E$l)F7>+9;qw_^!f(xRxp!9|k$hsV;d`J*B?5O1O_F?$MPgmX&H2EM3q!=u(n}{{zw4;j*T|MU7uAz{V8Jc1zuyG7x#1SxCHnM-a<6ZE4Sr1DbsLdiMVtH5FKMvXQq7CN=eL#b)!Oyqzv)4ocUyTjaP!<b!H4DHem8GVknc?ABJq>I;j7q`7heBsX6=hMYgnch)v#XwIhh_$e+8<aoB#W#|M;l??&;s9<Ny2g_p@?nVo`l^AIeoNQhygzAy>M$MU5<KWsxsQ$*+?9IJZ8>6jqmWd@0wX{t9I`ru1r@>%*A!$-O!5?UBbToa;+FZ;~5Rc?Edn7Qp;kF@8gfsxx*q%8fkot4^C*9yO>!y)wDN8Zh4m)Z1AU$~d8nt7O$P=@zAtE4?4Nn$wv)mh;?Waimz<sJt38x5m^}D+M!7L(1;)WQ+P+G{PhAN+gwYOY%w_bL&ACMN{uU9z<E;Ix(GkC(2&Lz35ZP11vHu8b+Q#xwS<R7DbUOJ&<u!4lPJ+h$$ZFkw*}9RhJl#S}D0V>lw!J&Xi+Vr(lk^qZ~$`UAdmF)Vq^MQdYIhVm-5{57gxB_%Z(gazEzZnz^^8?oa;%J?3|%|7g~y6L~cEFqv|HkNo<x=It$NPOfvV@|8;8snmON9X(&tqnKaROS*f1)Oy^#9Kp3Iu6nW;c?4~gu6lepxqDo#WeoRy4E1Ej>cw1oY0rD1Cw-)nyT|<*-`y+z+Vgu$)z;lNJ{<GmxRN#2r#ZR$d2uiEEwYol_jU|(w3CmZJk_G<7EK_}r|hnE7O^binVd76d;;a+lvByGJl31WdFl+S^WBuZHsz+2n~~R{9LzZ(<V`7uP;N`!jB*&~gp-F*4yW9aye;KKi-uU#mt5&Xsduxe2Pu(Q7y9Z(-jQ+`$6_dlQ}5<6uM6dPk9hGUC8tnUyf;b7gD5NRz7v$J?$lh1##uC$T<Lihjik?^<Vw%5$VTp|XInJbqSrWoFuC%X&V5t+H_@VL-1DiFRlnrW$2ihtVnY}sg{0(Bqzul<rtK)&jN;k`Q6A0l(J$!}nb&B_6PZ&cDV<}ZStobBMsut;_bQ&e3+1t_iK;;#)@dlY(vwJoX_rK<#wS@c-l9VCDU{XyWoUAr8QSx^P@P9RZSAyo&vT#MeAajh=?(gPgZk^F0%9oxyej!t{!jn9ef~4mMe)Kva$lbL;<L|l=2OepzaD`p1FEXGi}i7=gbgTCUux~2E0-nK'

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
