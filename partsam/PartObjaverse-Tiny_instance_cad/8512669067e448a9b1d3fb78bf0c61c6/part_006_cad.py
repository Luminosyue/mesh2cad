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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8512669067e448a9b1d3fb78bf0c61c6/part_006.stl', 'relative_path': '8512669067e448a9b1d3fb78bf0c61c6/part_006.stl', 'source_sha256': '813c0d972a83b7efbdffc134b794558fe9b00294184955d5749bd2214488408d', 'input_faces': 144, 'input_vertices': 111, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.02279273048043251, 0.3072112500667572, -0.035644516348838806], [0.05885063484311104, 0.384403795003891, -0.009334184229373932]]}
GEOMETRY_BASE85 = 'c$}q}4Nz898pki<7oY)(h@o=Hl^2pkK17kPo0Mosyr_tLEZ&!I62ZVQSE{RpBAB8gUzWb0g<6YEI%Z81H*412X4Z`aKPI<%)uqfBYF&3W)`|9>=lQ?JyW`I6?7lP4{D1d9hv%I0+;i?ZgE`50w3oy`f2sO_>U_&pl0;09yrimvij5_C1(kElHf(m1JjfS6yY7EFE!mvmBvnaUO!)<sc@?HbvMHu;p($846_!_Qtgw`=Ew9Kg5dIQNX=Q=oR~B0~6d2Eep`oF{a(Ga%{DS;H{=_Jhf39xsHdG#W_j0_U+Hib_c$U^!nn<^0lCQq(&i<C({iK-#<SVy7KP;a0fWCb~t$(N@UrI3_63<G)#RkgXUVBOS`q4J_y<5pw53IUE{Z>YjudQ>hCoK;pU-9j4rS_+aYpH#6ALY>wm9)_~p1)m8{SOs!`x~Qq+~KE-sQsii_7@KxAm7%JDxT%aFDZ|7C6?!--^muw*2sgL|5hr^M;rWl6V3nL9Ll5nbyIu2_MI)1w<??c!A$bC&+2Qay|)wRpYwbz=N}+n+i|*&{Hi@Ws9wX<wo|`5=W@S$>bd>6GV=AFNY2x6is~XKAKf9IZIg%ief@24H`V9W9`cpI@th~Uu7>8{IJ=g{(-h8msyC1?C1sFrJ-nOWqg%#a;oDx@Oukm3^Emepy-f2>&D}};ew5Dn13uVJd5&x&U#|a<^AGmFO7ptg!R@_gah~`yG+!-cY8^e7dsDyq*A>*SniaH*+CSsV>*34K>L~xRoIT`!)5P<A{nkzz&)lkg)bB($&VN3pW~8q_8qa=H>GqMnTDp~dE%`f#_F7E~=kHkU;7bFuX*^O%80E3q{pod_|Bo}MKGJa1fd`FKyScrI#$%byzI2u9qd#(*e5La|*Rv#(+S@kvHa(~g@)=w6$hs-taNU$+Q(GMBtZ<!epPO17-plv=Ui6^_Ee`L|#P3o2T`l=a<0{T`uam~3p6zZKxlVMf6Kl5AN`GH>xtH3<EZs%<?|HX6tk1i=J|(|*TOHQ(US7}2tZS_f>%W25zjp3UtHXZT#QR0ApVmhCosVOE4)Z$M9MI;l?}B;X=}&GVU#=SN8`-ZdpzR<%|4_r<tH)v+DbM*QUZ;Mq%;7qJ_bK_-Xz9?%{jPk^`(4TRAYVQ4BF}f`c>4ax9e3ErcSDi+yCIb)9Hu(NU!b}v0akvG{>kK9Z}f0IbB~a(M>mqMrY7<@&n>0=+PiI>r(5b9xgNBe!`$BUM;^aAK>gZ2@w3wSa(G`T-n;1gW?Qj_eA~XA-2TkNuTh@HHu9z4>laDKW*?++Ub;rU_3SG={{EXZ9_8e9^7Y+oIZr|y<&gq^B40`C;(1-nrth#m#kHN<AO92keVttAT^{7i@Aq;3x0}h=lo0aOkRQm`^%BY>SBH@=J@o~*_xYLHEAP!G-xhnF-%DaIofn$#GR~86oac41m(CqEeL0V(I*8Zdr|YObddqI|@1G0b^0{F3JVCw|{uipJekq6B-|oV^TDi`Xa@n8yEziq-?p)<_M|sh+gYthh2J2@djbC3MPQK(ilfPHRy)<9VZGH#WeID1j@bA2C1FFf_Q@L)^@=J8C>z};9?Y{^jUz^awb$I{S5%NF6{@wZ`owK%Q|4RP-b2EX@O>Lp`QOb{VR@xfF{z(`1^B?E-#R|VK%VhG^VIMvphyG0cs@D?8mzK@r_t?IH?*pALaUOFn@6)jnEj0d*8{VM${HCABIed`Tl~R57O{(WV7H}O_yvOUR+r5+g_PgBvln>octd?l<wVI!}{hb+<M~_J(U;l6d@2|}s)UWDXM84W}lE+gSLgUx#rW~U@x);~sP%iJstOoM!_Y=v=_Y>tp<Z<e6!e0J<_HUy6R+mNO+wVF0biU_UZ^V(Wc3<XkULB(MXsxR}LF-xD#_QzzbF?2NpJwu9S6=6OlpFc-^pDB6->;<S_<p5_eZ}o@A5-4s`<Q&r_7>IIet%2l`<r?p=WTkn-}eUizGsVh<G1A7?}xAO{m}ZBe;4Jq-zR@I?vrMRTXJ-lbB{94NM(eJaZ4_=jJP5TQ~d1u;45-T#D8~1j)?ewugD3;7#124gAhC)Avg}IfQ2pt$AQ;CGr()WxzM#>p@raFa4|F=TnsLP{u*2aRuO{D&=uenn1dN1I1)M^90?9a2#$irf#WcTD1_j2Xf8M%TmUTw7l2ElMc`8KI)vans0z*lr$EhMGsc~Q5Nv`5gN6PIEOa*51P+2e3JwB?K<9x&z!A`Ju+UJj&@gZWI2rmhI2oJ;jRy-&1!sY?5rWeYf>$C0Cqm=FiQri19B?c+(1>Y9%rIgmG!Pt!HZu`|{h(psFwD~r`Uuz$><;w?yMrHsP6j^&_JDeUg-!)~fIXo;U{A0c^kJ}2SFq4=U^nn+gkUGAGuR0%K}Siy`~;7Ijs=eayFkZ-UBDBe6Tm{JfQ3#1PXzlyr-OaL{!ke#bQahj8~~jQ4gfEJ27`r0frX}n7l2no3&5+vCD2lE3AhZp4qOIa56uIw2S0-lyd0VW7HR?u4FU@d0WSw9K_kFIlfg+~3p5LC0p~!o!8zbeBOW*6DI-=vGr^f?vkD=2F*FUl82kiuC3q3^Nrd2~(3N1JiQuK+CD2&#5^yv^@MF+Gu+SM`bCT02FX#XCFREXDnppS_|FHV^zjQpdNB(7iv9azS;^w3=VjmcrWR&!*q3vQdOaB5s4E+c'

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
