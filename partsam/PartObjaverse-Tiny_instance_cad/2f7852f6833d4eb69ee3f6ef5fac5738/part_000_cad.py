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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2f7852f6833d4eb69ee3f6ef5fac5738/part_000.stl', 'relative_path': '2f7852f6833d4eb69ee3f6ef5fac5738/part_000.stl', 'source_sha256': 'db13f7636a30cd53b346ef1dad93bbb0f3a4056a71da14a0993ef808fedec709', 'input_faces': 168, 'input_vertices': 120, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.19856876134872437, -0.11690536141395569, -0.06642980128526688], [0.1898542046546936, 0.38783466815948486, 0.09955483675003052]]}
GEOMETRY_BASE85 = 'c$}qJ2~bwo8NG-`Dn>DCG>MU?Xwix&h-g{lcL5XGT`&ffA6W{DfNW_bHqXS2TU<thjbQaRiW|l?E>V$Zt5J!fU?&=5l0RyjsIf`v+KDE8_uNBxFm|TXGIQpfciw&9`|fw|`~Ew`MY^`^B-CFI@!=m%+%w#TkZ3D9iK4W;g3Oe(eBbQcS6ze$eEHYFB{37C<0iR?B2ny}nwFoE=N+VZholen_R+l4bMgxElCzU?@>0{JACa7upJw{`8Ogb6=5-%G|A9W*puRrZ9PNMnYh$LM@0ot8TIS-re|4Bi&V9El<h60(+Hv^e^AM|V>q!6DHjFo}ip`JpORlen?>fzZ-_iXj;=Gr+N3z}jY&Gt8{;pbH>$ZyJ^4eK_T>1Z6c0~F%pMxcm9SeP`ke6%vUU@CteU~B*eSN~QeTdU;%2LEx!13uf4<Jt1#T}BhBf<M{Kd<^P7~k*Qe&p3AY%k($?|2OU+2S?wTI=`qZshZ)hsek2Rq8<8LTv~5*83-r&&=08#Cwi;!WTE`-z`>tSHCTYw>|}RFjf>HU*q@`)Kz2;IEnWT=(`bdKRUGm?|n7qV~qRq2Q`mX^w%g~f1Q5o5$mMy$ScFVw7DA*SO2_!8OGn9c^vs%a66#tq<q68TltriFADwVBG0nbXHnn2ClOafl;$GN+R{^a-|$7qUo0wtFJ>#>NTTm?BoWtP8|zTF8NF9voThx?nF?R;z7p#q1}fiK{{ws>K8plb++K+HU3qvO@dn&c^I9^x6!*)n*5bZ<CDu#y*#lp1AFJjS<+1|T^;((Q$F+Y|?^AI^i$3MJUz2|t{6_Sf;M`aT>UjD5IqW~?Z_wA<cp^`O`8W8+{1lb{gG<QYC^)eW<LkaX1Ao}k*VVeOeh>A%AJ8Np+qdW7+lI}m$9oU)dyMJ29^-oNL7rkmLJr2y>8|{LK85&3K+lzUKCrd|`ClqSe61n={1-Q2{L!!Ktnu|_%6C*N-`P;-uPQbp|ERHuub1_oi};sfw;+!1yxnS@TVwuW`lGGj9cQXA?m_M<T;K7l1ZS?ry6Ddwdms0=4BUx2d|!n+8^dQ+RzJqKeWUt}QLlXcZ^{>oU3TGnZst1={=DgNzNq*HeMy{e>N`qmN-+NBE#-GvjPFP|*UrcIlkU6K_k02U$`SM9M&xy`gYq-}UZuug8;N;rX^B4P{Qd~m(f%>(|A78o<=Yz8<!nBD(c?4p3*rB60p`16HhkN`Wmp%D^A#n{{C8CTx?iP=^J%%-pZnLTKGn>(#V>hR`i{E+AHY97N9A#{W;?FGI1Jx-I^b-R{kg76`FjV!H@JW7^}|(PUYex(+H<>ifv=C;tM-`-=IdlW;zm<nXFj6U8WqR0tE$h$ecK-AJGZCedv|y!-w05?@x*?NH=6m{@-&RMUpoX}|LF_#XZ`MpCAc5rtNNDD&Qd(zy$ipG8_I9_!9vvcp-}67`GK0}sLr+4Iymwc<M%{Ncx{io)*eM*KiS$1L4S25&r*Gl`$6kVKVSKF*4g=Fkm|>?-&Fm6`3!t-j#a_RuTMAd-r({-BLB+^l%J4=er*h%h59>c532o?z8UqkUF?khpmlIN2!GKl*f;ijUm{QEonqzZE-A)*`}u6c_@K9xe>4EUhuW?a*eCW&hvDm&>(qDnk8<oY?Mko1s-B@b@=3gh{;T<U;X5(v9@SX)mHq2#_5Iu~Q0qOSssQ;vI<Ne9uA{ED8^>|J(1ja*kF~;9wbt)Q8}0#L>~uxH&^qkKes$hYRKD(!h4(EVt@`8Ga^?R#0)5B$BvIv=xkmX{H{f^MmO2Xk%btD(zW&B7oG)x%OH?0k6{5~Dx%1$QA0yBQHT!h<A}=1kmgt8%8wVU}d{AAjb=~djH!A<;^~0!t*a76P|2`1wtrf33ZJn=vaua-U&u=B3KfFTq_iNEOXNbg*L-4c8v5xw)m4Aj`=CT#@y?#jb@w-7d_lRy47f>%h=Hn5pe0SxGGwcJOR>HRpF1`rgpZO$pMt^sf4#9Zie#%y>FIFmFWX)6OiX4t#L_aDO<F#hKGx{xzcW(F&zRk1d6Kg)AM)}V6%Ks(*PQ5<Dyx%^8IQE3(oyez|@5qis{T#8Y(HD%XF7UO6dG(4`=d%~;F<-m%<C>iQ-(Ik(r`^rGW#U)n=|4T$a`cy`{A=LHAN?}}{=1`p;L!i~=<mX`TbPJ8F;ISTgw%e7)W0F5{xzSI&%2t4m0R1yX!0y-$ywB+seemI9YM~e&gJtFL>^-gH}SHG!6u4K6qtC0kb0(x8RTqo0d)bN$tI-E=lC3sm0U<Yle!^(A)hJaxFRBlab#X0CVodqJ%v1sdJ1(Kc@%XTbsQn}3xw1`gw%Zrse6-$Q4iz$dJ|H65>j_#4F{R<C-<Z7$NT=|5b6-l&7aTu^IDDxwZsqQJ0*u%atLF-lEW?ehg;?)^@~Kfr4Hei`h>H7;fytf9BQd;sHOg)%=2aH!Q^h#-8kpL<N)db&Qt2vLVmnLJV8j^l90L$xjl6o>L&@QJ2Q@a-i_Rf+Ksv`*`2yAbw{!Xbw}#w$xl;Deunya>K=sDUgYPfB|l5;MctE-x(gw72NPXQJY}L2A$2<w=_XQ5WSW>pP9djK$C#LC;w2My6Uipx37d&X6HzAmo0vpM9ZdG64yGPTNF7M-P8~??P1dNrse2Jp_aS$u?n6C*>`Og>dI-5c^$_ZjgwzS-DC#KAFM*JH0wMJ{vW<Ei^-F|}^^2jNNRGGEbRwUdNPiqTnR)_wDmj^YDs?)M%r#4;P9fW=Q>dpAQYR8pk0-}d$8&DuMdKQeCr_eIGBMdw!^y0x<gu1IkL5Z@9%EUTF<dvvK9+Tqx?!!Q_9l-Jjr&3BK=N48xPPQ>*ke)$lP8PDeK?tOn9Mm$B4>!kJ)FTgj;Br}Pq)-<x}}~{XL2nvxjvcnr;;-)YnLG!_mb2J<Rt1O)>P`aNS79!T>sO*CL8~B90aWYsBHdZ(_@YG$)C(vzZ`PnB3sEmXC5e8;KzRzBK#YO3u68'

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
