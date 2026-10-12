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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3a5ed2b8d5c5468897e797dcaba508a1/part_014.stl', 'relative_path': '3a5ed2b8d5c5468897e797dcaba508a1/part_014.stl', 'source_sha256': '4c9e50f31de855930d1fbef6ff0d7c9d33790689b44fc30174131ec30d553678', 'input_faces': 314, 'input_vertices': 170, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.11767395585775375, 0.3419482707977295, -0.13360221683979034], [0.1385507434606552, 0.3482833504676819, -0.11258144676685333]]}
GEOMETRY_BASE85 = 'c$}r0dvH|M9mj7HA_R~ihDbnUF-Uj>n~?BmB(MYwkMLLs5D<Y4$tFBP-avRHT%PiNOBK|tfT4^Xr_)xaPDyeyQ~#*Nmca_uj?P9I_@~yX4V?~H?VjDwx!iNT&UD(H*}0$3cYbWX_nvzXO9o#-T(=}6`Wk91y|waKbzj4f@7_j|u_;hnzqTY$_jG0TmKdXNB$qFBJT-6eT;H-7W0SEhtu#<qQk$0JNt;wQF)iJbR#sJ8Ut3(cs;ag$AoKj<in>5JuUk`G9SHk~%n2Fko~)7So<`6A`05$1;O`vLHYI#C^W$&Gqmhs#+Ff$b^-tSmZr+~}%?Et>kvw`ABnr1YIQ5P;@9p)(4Yzrft9frxOC&e8eIEH7u{Tb*<>sHi)#k+`BW}3Ot6a_d$G@weZ^I?wmV3J1X_a{>bW=Mov+1mG%SGOY+Ppe1=e)|*y!U5cL_cR|X7u{p`d7PKF23s>$wT+Pi(ZFvPxQK7`@3syKANQE=GbYj^D0;K!C!Q1*Uqc{E7#m#m8|8~c{%1)uI9ZlL)-1^Xf$jQu6b9#HhZqt(K&DB%m=Tgw`=Pdf4ki+4}CTylA9&dqj_OUwCCJT*F1P;n3j9<XS>d;T+N3LE^N22qmf%GT=R9gk^bVn@^)<<KX^{qb8EeRAU9_DqR(Apg|=S7nx(=m7sg_3-g+J#^Va$@@2%da_4K}ft=%mTrHs>Z)zdkzay9R{x?fu_v!Ot^=KrXS_IdN1wqBxiy0GVJT~r=wJFi{;;5)x-cgxK&lOnnC@%!4(^?w-O;hN{(yAoNK<A2nygZLm_*mHHhD)$;6>(5u$*RHvFe@Lr6x1KM@ytV%@AN>6-?Yz7zQ={v<`Wx-J^LPE$H8<{WYqjU<xpU52&m;4}ZxV!dpR?bZzv?5j`<#7J<<@;p?*BYd*snvV>x^q|-n-dq&((Es&Rf@qdE=kS!oH58{~qC%2Y>zV=sv$=ps?R>YF|>hy5Fq*YD=1SzUui>xwSu&8=2|abyN4hxLd2`p?3?Td1}4(`QFZAEw`RKa`P_@T7PreUM*MsRqjvNs$B<f=P}n@480w_KLgvfbus>SLAd3jdz&_|*2Ot*?LUrrb-wDpvOZt!hvc4)ChfZUo8OLJ=Ym~AyU!awa?MTOidK96;O`@S-uk}5yvW$Eov+$AzL%?ggWP(q9rISseDLr={r(K4bhzc-)a#LXGxlxmI(YBqM6X-&743Qok+0>}ex>r%Yuf$eO)SxJb^oY5H2$X6C)8Bonv2`%(eG)0>eTO_*hb-+hk9xA*8Ss{w{qsav0rG{L3GAP`)AzJufriz%dP7`9;*4P_Bo!S!;w6A|114@yxUvLt>=;4|I03YpZt1P^zWV2Z?*d{G^<6p=5PL{)t;;S&^d4A%!^NAJGAGBpR01~IU@J8^y#p#yV)>U*mG;&AP-JU>Co=Oj3-@lb9YDd`&-Sx4*U9sO8y{R^FeD{?YXtjJLavNc_Z;Dt-p1h$*p}`<+;Q4o_9VIu6h5N(d*eYO6w__M+>*yfAOt0dv5J-j(O{OXFli~qpg?v{-AQ__X_iq46UbiUbAyL?Dw15nH8PCGhOSc=2dPzN96vRnXdPb%ANO5@TDak_WRaI$P;dP@cPa+dv5Kwj(L?k=bg`yr)HD>a~-+$`RaTp?Q*Q+GU1koE-q}d=MUCVpSSKq=7V3J(w__VNoO8<Z%Sl7bhX8GT~zK|mr(aB-(Pp1_S=foPxF30G0`yOJHbdY%8G5js*s_4siXU^D%NKISHG&r%FO<Me^v2FxWkC>yMOpC`6;{~-WPrpm+Zkkk<)#^V{mzV+Q#E>c^nV_2p$J#;F6!j<uTR9Nq7={Q|Z^AtS=p<566eW{cy=ycow}S{}|4K$KaBu;8W<UI0w(6x8iI(o8FSs;A}Vv9|otveeq}U>F{t|@?3l_eHG8g=hIvA0(d?=1^2-V;2eA&?1Qs$$@zFbeY5G8MmC*}(pTWC;Aip0@CtY?F1Zjdq_5<Ka3Q<^Uj#3NefSc15j+o<yb@nYU&X8NRdkfR32%T`;F34s8|W>0J-h)f#Mi;=;e~hwybfN3SHczW5?u0Td^5cjH{cC)lzb9@5#EIFf=|L5@GbBzcs;%m-U6?~x569Y3Vb)b6|Tf3pTbYkyOMsJ$zG(R^q270;FGxIgZM%EDmHPGzLK}WCcF{f32%e9;*t;Hhv=>NW&CCO?xx=<ve)P+{e1X+Is9&cFX58U;qurFAA`@qXK=}Tad|v#;}f_%{sev%J^=^ui}0)PPw^J`B77Nt0Y3tt$0ax7jr3Jqi`UXyay48F@5SrkYWM^$c?Z6OzLF2XJK&4>5%>Vyg0Bs~17rbuOD={3a3lU4TnyLZl9%F3=_~npcqv?uOD@4n=qtG#E`bl=<#av3@d!K#p9lwV$y4#E^i@0)pGj}UbMQIzl{_1s13!;XgJ;7f_+)q*T#iqsV>!pQ@WXg7coIGcei)vLOCE)fqPOI+@F;i=o(_+NXXBCw<AdodIT0QVPsV$}iSR@`Cj5>gi=(gP?r<DD2!9Oj4v)fzz>mRW@f3InoQ@~JDez!C9!`K0@fbKB?uE-&ELkjl6+eVOL|?_pcrtwzKY>3%U&RCP0rXYe1Mfj!#oh33^i7~=Jefg9>Amrua4ar)AU=@Zl1IV=;bdHLCZ0)e#iQ}j^p^ZMJR0tSOYVdBp>GfRbtCIZN9oVt6X4#sWH0WeujCo97aoaAF2D=uEqNAP0FTBc=izzuR-B9H()V%t^&y);N9m>b8u%I950}DTd>QPAXW){H@FMz3UJe(*v+&jMaySn!gIB}3co`jYIZl8Nhu{0i_R&}Jc6cA`$7|s2@G`s#u7Qj2I=Bj6j!SOBo9HWfKimYD;rr=Y#&He&I{pT{50`uvKTBW5NAaWdmAnT&3RmIB;XQC2{tA2?Zo)6XufY59H{c8KVf+$)8Gap?+>AHVTk;vW89s_jK8>HIuVi0AOl(rz5B(Q`2QO1@DB6D*aQ;dCpX>HN`BwO|tbe@w3gYE{65ecLBNuR}N7{b?cjJB9'

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
