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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1b3e8b99913442308aa989e3f87680b3/part_004.stl', 'relative_path': '1b3e8b99913442308aa989e3f87680b3/part_004.stl', 'source_sha256': 'fcc4689a4b1a263d304f795885a519e2b13845c30a03b38efc792e247b928357', 'input_faces': 258, 'input_vertices': 170, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.16524638235569, -0.31989166140556335, 0.3350525498390198], [0.22097888588905334, -0.2728755474090576, 0.3671964108943939]]}
GEOMETRY_BASE85 = 'c$}q~2~^c(8pi)@A}-*9f{1tp6_6zXQE-9l&Y~;^D57!^5Kv?_5J|e?iiis;NN8Nm1!}Zhh8!)sQ>i4DO{s;;@kVK-mX@QaX?DNwd7Pm+Gv~~i!SkNy=W{;a@BQBI`~LTTF)G~5+*ZNQ0OiTO=E$6GiXx(mVyhIS<}J!dPR;ku$|*8Yx=COBJlD+;u~VbsO_Tzq*fk|JKRM5Jq{?;lyZ~2EmFv9hyhV9QS&7+sDXGGrl$4pDYV`BdlX6mxe|Pg4G1OD#=kBRms`?*)IvGn)H4i=+ENXeD{PXvPj?KL&{%%lDlD>Xbo%GcQ7D!+35F>qcTmr_wTM9oS5q|Q1_^Fm($~<k0;rG!?U+;8Jj#t+$$GjO4@J)ZXApgF2CH$ab<XK=Y^Qdmrpq{o2jL*0u$E!N;fnV>2I@3F&{`;+%w+{8|cjTbX{=H5~efcfq*Zd%T%|7_*tKVV#rMZ~bufOzFpFctVi4&!-Jq=&!y9NI20+~k@sFJ?s?ce?;{h#)so<%+wpPY($f3`v&THzaV{|vurmdvj=jKRD&UPV0>C*^phVJhlh=LkQ}0`>Ss!GAO#dAj<`@!D^rkv}pF{+ZRXZ<^t8Snu6T_zO2nUzar-b*}zO)~~E?MBiFcF#h^A=^OGQu&!h2Snsnz$P@f0nMc1n2lHMtJuiIiCvDQ#S}aGM9~hAT#BZoGaU=3%_LSrGOK)R;*TC1S4$1u5gLZPgx^tURXUh?pM<25UdG1w9Uwg=2=FtVd0N=X?;|J}>zMMOSb>;1Zzr$IMH~i2GeZEnTdCOi$pVJ;oUzczY`5TYQJenam&q`w>{E0ZvO3h95q4GHTR@nB1^sSoUyS|I@McYx2#cMc+E~ha*FGl7u+`@TQjyB;uwDiGwyBmo6_4OyH-><8zUrGNI`On-$p5uC%Up3MT^~c<SAJT%p6?ovB--oZ=;DNsR55ReT(DAhNgRA6tZCn!i>DWp78ao$^zc?IzLm%m@dv=xU)gMZf`IQJq>FZp3<2;;b!Fe-xlD_K0hjLw-L0X)DUr+coC(-}oMOg1#FX`)J24TG_GxTQ>e5JVn>#E#~em2nm%mni`oWpbGp)c|*K8ikDIm`T-5yP<FzaPPQ>+68}Z~7xoz}wj0+t#>uHZLO2;UyS<uY~zykY|@2&T}tI+?Nk$V0`yjjJJJ)KKvSw@m|x=hY5FaU(U_M_z6+i_lw`bU!4H|fD`J;n~c5%&qkg7r(?V}7xg?%#dtqo%zI-i=Y0kHHT`{@!w0UYbMad2*VRq9?=xoMd1ZMD`|_|6^D0kquByL~zF}Y!{9WjqVZyh_V@N|iE3A<x_cqph%nReUjYdCDK7t>bf<Bb}DC<-YvS^a)xU>h)jmL9ve|<Yj->|74?w4f<=3Q<ref{?Ha=h+qJO|WE9pIOClH=7^Q}H}$gs<_vh<di*+!|8+rLP_Sp7eFjXK>Cx4wAmEc|H7<HR$I%lclc;t6(1jG4H@g>8oRrU%%le^w~KY^Io2e{>(ju`#U8LzHJuz;Jse@hS9T--|0B=R2HM2{>jLnj`gaRmEc|kr=rd-W08M&C*1d<1z6XpbvXYj8;s9+8TnJqaZaYa2wz!=@d`dSRjpb)AAAp^|IdaXzv=+rAFg1(UNMz@)?PQ``vCn=-Y*Y4&-F)dVqeD1fqxeFMN`#=`d`K8vSx)N?&E_FA4`8kJ^G-!g>&9{p!Bsm^k4ntI`*YL1b!`j_e!j*XPETWD=%T*v?9!#nFYV~1orXda-6raHtFl*!p~#B@HwtsqMVVwO^WnY5AfX9mGzds(!&RRxcw0IRN6~l{p)y~+o8Vb=lMR;*NsX={=?UB-<$elymbVgCx#2S7c2ZR@1<Bg56uIxF8h)2vlqgz#`)KWO+)^_4#D#|^JC;MiI=|i?I8FkQqYIq>6q8Q1a*4$z<T#*O5boS8+BTLiE~?#gFLr(W50Hppbw_2q_0XyK>hbWL;cfNV|)VoW3cIid4FAp{0|F}|IT2n>-c)~vsH`xoA)*H{G}G_bxKBl7eC}t*P;Hccu!NZ;j23AM4r+OI6np5aBh=!p+7y>V86<P;D_x+Jq|^v=dH&$Z$Iuw{<MS0U&y|7Jpg~VFY2^^6Mc?80)KWDKX<OccYhCksPMqNi++LMtmk<ci~c9#zN?>ph&<PDPPEm}(1+`%;OmCT@tSLR{-~BT!CzC2I-f-%PyThx+lcpbr5<%^j@`j}3oB56zpKdK<v#j+r2yk^Dd^8fPvI*UaKBvEVcsOOW?6s37OZRdNcgVi(${~6=bN(D4Zcff>1&I(VPCRNp%0I`OJAAafalNUJoI^rJ^Y4oSnnJAQ0F%enD^aLs6QI-V~XAx`Q5arb9orfbB7`D6RT0@3fyZY%?p0{6!;#C;kS9iFByaUTlk!R5Que+$iwHtGkj0ceibf#jq`b|%YG-`Z@-Df_%Y$w->^>TXJ7*IPg;O;QrH*swrVim{7pQsP9MX1>*r&=pI%0OcYZG$pDlg0%~GuQ!bIe+%7s4--`DgR_<pDMTLeEO0ndSm_t3Y=OQf&*Wfk^o7~gMCtit#K@u<Hp9`{|h8{>zTBEMHx)ZcF}_UlnT`kDR{@;u%reZ!cIsPioEY4{<m_k(6UPfnjfJ^c=2z1#3Urag}5fXeM1_&3r~&j5F<tK|da|M>*pD`ucSGn<hAr5~}bnhcD0Zb6=+V?5_iG4G~JsJ{;Hjr#F;PuASJ3}0J|d5>(yxjJ|S`M)o~Ihi;P{dwaK_BZG&oagO$KiA*=8RM(4kLuR@_}uq=2H(sQd4h0{^me9aWxdxrV86cS`;t|t^z~LX7{6n}#o(wv{I=qwTW7!A*2VbdWeh9DR+*R7?pGDU6hF`P-~Xy2W7vQ7s|sKLfdBVb6&pmaj8VxDyo$Pnyoy{(%_0kZiCjuvNnJ!1`U-g^c`bD@S?Fr=TJl!va<b6PWT86pR&pJ6AGwaahgwhGL*7f>PTou2!4O<ctt3~n7u5{G>#3#WQm%77L+~bs;4Rd(<h5MG7KY$jY8|<bb=NWk@1pJ{?;`J{?jY|Z*HEj;)vT|Ex{17rb<|L6$+etA@J3^l8>5W6j9f-8rsk20$vF(cnGC^m8G_TO%gAZuY-%|<o4nK*`P3EEa&kFqUBM7sVT^6m*QguGuaRG62(F@*k*mmS7=nwa#pELLe1_l@Y7RMtoXQZqfFZbqnn^Ap7cc~;Q|FS?$r%j6$<#D*GI<^~n>>%akh+w-kX+cV*M$thxtuGP^XJlkUQa&j&F3BzP%GN4rGo2QKz*4ZcpbHZ{Cxiei?c1xqd1oh#(3QryN#hThLbV+Qu~nmlHI5S$wG&b-N-L61p870$-ZO{&gH>*oXB3(K=LSKj5fw3W6U;2tTCoiCy}R;1E{0PLS4uK<X%)8axbza)rxFMHem=hr*<Nnle;hkI~v2^7{iS*jv;si)t@|qJb>y*c4VFb48h&0R^;yFt_;CFsW#-E<iS)IvJ3k%m?3y1brg9N`#6#zcmg$+Jb@fxj48&LW{m072yz6+OsCE!PbX^_f|D46=TN7T=a8eR0pw_M5JRvnwHMizY(cdoTaXp13E71E`us<*8MO=9jNF+acql`#H`S5+{7iT=1dpeVBabIXQm2rouwRi3!SPfLS;OANQ)iLm$syD*au{n3p?Z_OSw{#pk}THSf&CC_N*3C&U9UQ_uR`tH_1V7NUI-3ionl`T7=ojy(d1~3jbaE6rrMK($?goncGQmKj;z&=A=sKBxCgZZxd*u$)r>5(Gr1ethdPuzl>PN#2o9&tB8QV_Qj^Ft$%)hiaw0j78byvHhf;&dp=34HovbE%Qtil|<bG6Zve4e-e&j(6!TlM6of(21sMcg__SAtPcnCwVE43Thl{|*(L-t|s#xMj=WC)I-&Lq!d?_wB&XHetFGsrJ81W%@hl0(_M$qd0`sh;GqWIwSN;U=cGX8-BGVE_4}l@Fcv{~`OY|MHJthuZ(k1IAqc_;M5#ZXxfdsqv3^iC89fOZgqY6pZ%'

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
