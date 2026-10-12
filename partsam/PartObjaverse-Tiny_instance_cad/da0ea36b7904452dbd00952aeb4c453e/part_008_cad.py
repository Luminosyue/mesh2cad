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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/da0ea36b7904452dbd00952aeb4c453e/part_008.stl', 'relative_path': 'da0ea36b7904452dbd00952aeb4c453e/part_008.stl', 'source_sha256': 'db0f42992f06fcd827eacc464331edb944fcdd1eb96077b07a23eb650db30aa3', 'input_faces': 236, 'input_vertices': 231, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.190464049577713, -0.4053422808647156, -0.21941964328289032], [0.3157854378223419, -0.2926490008831024, 0.3075384497642517]]}
GEOMETRY_BASE85 = 'c$}r03vd<H8OIj_S{@=wpoB+Vt0g=_c*;vED{X)Z#I&OF(B_5^1c?L_9t8v<P@uf3Qbj0{tyrFlQV2l|WDSob_mYt0UY;T>6c|OIWm?A;>)1WJ|8G6#%XX&I-kERyzx&U3&z?PdzTI<nk~Tc9LA>UD?$-)>q!xB;rD-CXYVq34tla67GqduNr%sz)PiyY_;zPP7^~sTGW9n%$wYiBCvhp%>69?#t11I)NOwto4=HyP#&6t{=lRF_x_(L+X^RgU2Z&JpzEa!X2p1pb`>AgB7>GSme@zdDpf}v-Wmx#V(e;yN>e|%{5AjvoSZ&G}1R)XuBDSuJ(m$&l#^a91tzkgPl_^zXUE3Z?f?9*`#^XnSfr{nT`@+n^{>|ZALM_)CfGRO~&{@l$sAL-}%7WFeOwNmz}|9Zh^Zod8Z+lS@;+toY5vQPcDUK|jWed;IA*WsJU*RxI@miuY#z804KeE5de*3GwW#tzH<*E(Mh%RcpAOKIcg8&9nHSZV)O<FM@0dF2l~R3ZERb!R^H-zwaxv`_ufCpA^t_xsafx!3=kO~rxzhtK=3Ei#LP#>Yq-TO4#<$miql=d<xQ`j&p=p67`xQMY|_Ppv!O8ocECcFSU~Ki{5oeQn*S{cbyp%e{7PY;}FB_(D<8yds~^E3NumQP8|K8mAWp)eHH&F1Sy1VfEAZ2GyfBqW#{W`py66s=}apw~owq$4^UKb<*uuO1mTO@sr>2uG^_gu^`_F6{!A{onHQ>>8FEyV`g8~Prc#gZ|D)|n;0M8KYY{mL&bAW2l?ibwQ7Fiq=;K*bY7u1%VnR=*X(3^^SkS6*SB%LcFw|b*{5-^6ZR_kG!8spC!g~F_C`b=AG7KF@*rQIw_nK*VcdAWKc2`p)<+`pc-l{;mk0TJuQN(MjWf^Br}3x!rBxAm{6qG$<+5*(zwNA&PuGR#`#$omZ2g$)>$lFh{;SQ8$i9&n7geq=e7kgit>RzV7TgZ}I_<#c?HB`3xxR&V%=rCfvQO=s&7LcjeQMt>J5m<po29u*J{_0mlTZ29u91~;fArBa%4FZ~&!g`t`TqI7zMw47Ur?mv`{Tg!eV_8}FDvExvRikE$UfDVaq+=}u3z1xO0F-xg%**0sxRxtG$r4^&#-)|FF(Im^D4QH>=9pugM4GoLM5N-i|12)QND34xk|1hb8~4}_D%T4(Jz#IsxO{T_2uV>x>w2dWq()_mVK%(YvU~?-$EVne5x;F_f0Q<c6pUNf9$e%D`elVmvPfA+4twk+<g^6zS%5a$@k|8%lGFq@~s`sjw|)`N$(2T_viD_>q@>~U#pFZK>zkvO1@uTEZ_H$Z-29|TB)zKnc*Pc-g3G^_Wg02JIo65jfV3}WS_3DId@}3_UZZ>?Rp+ij!W}7b|Dhv8_(}5R@$fe%<}#D%<^eIhbFzP<kNh%1}7=~p?VM9YI#idsot&bDN6e^|9Sf~|9Sg#e=zU4rk*c+<F6Z(_UZn>^XdM;^Qm6=`1|$3#^0a+u@}OD{<zB(L4K&)C@aXf=D()Q2ftoe`@YZGC!e=ZzTbZ6i<+SNBA?e6`MkdB_*5_Od41LKDgPf0ymfT*$4|KZT$Xb{_U+E!c;la(;NGwFlDle^y2Jg7e15+opWm;zPxl}4`TdIfly64H)XMcs_gnJ${h54ze<q*bpY0`MYvp>R=LPxv`QrQR`9eN_zStKhd+oF5BlqcfM?QZ(lFy%yW>t2rT)*_ZCZ9jw$>+~^^7-@KJUYws*?NO~zTVKIhrIr@81K!ubw-Ko>qET#ky+Zxn-32}l=(*MEAsjJihRDls^eq5L_S|%)$x&U7u6`^W_)|h?SJUvc`yI$m)^K-?B@0V=ymnFN51yXH{s5xd|tGUC7-Wj$>-}>?$f%Ie7=t5zMtQyy>eVypOeqm=j8MCxtTvcupRPwJLK1CCvQbmu4~$-kk9uu<nw(^9Uu92^2(@O*R;>#KJBx}=le49`M%74d2>{*U)m>fpZ1C5^L-`xd|#<w*&dban)bQm^L;V-d|ymH-xuqj9f-<xP5X56`93|g?zVEh=sJ?m-viip|4SWb=JWRq`q4HqW!#w0-(!R>-xrg|f&2VDi5`0>CZCt<rzvllw+z~~{goz~CZdrRuT9L5UNH+(d`N>|F;DLOU%q1Q^Z&kLKIHTv>_h~57#snAgb=(A`UkMkSHbJRuOS4_faZW_fS-o`94z!_;HSYO5Q0ZTe*qp1o(Y`>7WzBzOz;}$+u$|e_0S{W_26QJ;BsgL9Kl!!e$t8IPUIm3uZBJa7CIfg8oU<zTku-&hX}!C&^N(C_k%Y(aoh<LA@~q{@qH!q6|m5$;FaL#5rT(6)4)T(y`jUvLLUeB2B$bN8TtYu1%I22?<=6Iz(O~ISAhSB5L^W<1y_MD;9M`@d=G)c&{FUjCq8lF1L&W?AApxZmxGsqpMm}o{0z7sbO5*?xGOXn+!fpx+8^8(JP!IScpP{s^f%z8;P;`s!0&@kL(hUwgD>NJ#ra=>UIt%Aj^M3M)Ht!niS5uRLhz^18t?=s7CSK(A$TG}@Djvgw6`6+2eBB(+zMU@od6c?3`W~R`+$WS(s2#^M%;UooOlQ!_)&!5o`@v0HyGRpk%YDka1ZDpuxKX>Z3`U(7Mdv?Hxs|v;>02+b|VCDLkRvgViDTQ0*^r~LR*>Om!Vt0)!=hZ)IzEKb2#QX<m^WNRVQr3Rb0y&@TUmDblnACL|nyjYQg8A)!=uX*y+T4Xg+v8I0PLJ4uJ<k9{~>pcY}5ZcLP5R{W17qa5^*toDQA`T>zd3-T{3NyaODAo&?9hmvCO<JWoMSfKP${47~)tgx?B&%ZZPjcn2Z468sYW{uX!+LU1;85;z;23jHZqXfJRocql^fNa#<%Bf(Rk&w+)`1y2FbLI^H^ZUPs8E$A_DCC>3Yv;tg#zn@1~_{|eeyy(PZ&|iTc1CK%o&V{}X&IQkg7J-Ex1<wY*0o?~KbYia)2c0+o-rz)u<Q;^60DlwwduSo}hniU8IqN<rx;T;OL??vc2M~hWKz{&k18xm%1s2*2+!}l@^bYX7;KtB;;KtxM=$+s=a1(^!7SOxFEx-xT?}LTj2TlODg?0qD1wRPw0`7vb5Zu{`A34zh+78?S+#VVaZVzsW5Zn~n9NZM#0Qx;}1F#0IuYLCs+z{Fb+z@;h^d4~9@Ot&*<NnjXjC}XW7lW<*0}217x($$jInim$-xQ<`Z+M5-$@*?V^bj*l`!|X;jkf'

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
