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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/186ecaa38ee9468eb222328852afbd7c/part_001.stl', 'relative_path': '186ecaa38ee9468eb222328852afbd7c/part_001.stl', 'source_sha256': 'c90d5acfbd2d26e36a5aa0ee4fe582049334135d0b277d90c90bd20ff7ec19d4', 'input_faces': 256, 'input_vertices': 205, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.06169998645782471, -0.27901652455329895, -0.25962311029434204], [0.29213985800743103, -0.16653572022914886, 0.27609339356422424]]}
GEOMETRY_BASE85 = 'c$}r02~-qU+J*}Rjfzo`#3V}W;DScPT>(MM-QW@wG%nG!N~3600;sqkCAi{_`vNqmQ3JT32<}A`Wplw~qH&wfO#ZlJlF5*X8pkBl^}Vl??m7Q|&Ybx<=brbem)qa{?ssq1t>zFmxQ3gTf}gjP`|kPYiyA44(L59{WsW5_K6<hx&VOdiJQt;b_{Pr*-8gLI(6BKs${b~ZZ=@w|a;$HV$u~GEz}L^@8#OC7K6c{F4`#(iS`2@{#1G>vc0X?F#2AbHx^<@xUHwd*+xVFhP5<Rj9V3SpTMwPHi@9u4m7z*uqm8}nqW=)N-?&!m$6gWt%<N-w9XWQdp{A=HuZjPt`4RC$L-xq^(V|L2wL#BM$aUbHY(w?G{JC8GFI;r#pF1c^bXdDG(b%d_<@ZT8tHf`z4Dnn2v`>Do^@g9n^OE>=-Yb#*z762Vwh&*Bx_?!EU%o6;=C$I)Md>%cNamrLD>IN^AMy2elP}Bl!W{8!mBHdGK5H<}lZN7(Vv1!vCD}vfr%X>tm-ss@;;SpoG7l|2L40l5DCB1;$GkI_Z<p~#j%I%01>(18vspght!t_H14m%q_xfxy)Y>i!c`UvtpVP)2*ob)qiLYJB#QHq^IZg7pS0eeV8N)EIq+a5iYWByxF8^8~{;BE>l277x^h<ntQhr}=z4)eEcaZ;u3dvuw_=vBSR%5<h=V88cJ;YbO$(Ojw-56P4WswW~qWf6injOwN`Jw$}zUqwZ5=Y-${W;d9doku6tgVuKdNjoTd?{->^0B3e#y^mL>L=-_Tl<d}%jf%cLwy!|!w(&(iS9jv_{*Q5Zgu7*O23CH_DS|OsfQBrmiVTrw`E+@N4_VG`$CCaH(%Bz{0#EG6@vZn^}M;Vf9ecJ-C9<oZvNxrWV|=csN1IbQV+%J^fb}>L0Fd?J22m{L!)K9a9nGx#$g<#Nl#;Z?XPW}?iVGYUzFjio_8_c@u%ldH_zFUujfhJk5yT?ABW^5NSud_v7f%5A@{Fxep<5J_XksCzM7k9uk`cDT`Jl&4D0*sz$xihBPCt@FS4Y+UeEoAjF%OdDgIA$rN8b~R~LW7yW(391YkXSMQxLDg1ThO@B0qNebT#ok;J!*`dH?5_9yYpuIZmjzpuuLucsu+xa$A795b%XTHHPvw=4#A_$2g<^!vy0{qngl%CWBZKa+9QXPt7yzxzJw6Me8m##4)OCC=R>iDO#w{RQ!D9rC1qJ8#5aKBm~Xw%yA;B>vTFnAgqjD<z-2ONV9rpNpjq>eI|ia@}XJ)XC=G1^c=0=H14%X?nEy>aa@OR~^dEOPp_Jim%mbfpN`GF3Nak*XE1<c_5xAddvXnzvRME8K<HP?(<90W#V5QDRt7zs<3~8ZkLK5JL<Uj8Ov}#d^J<@QIj^q?|KAvc=Sevte@?a_}aI(v40AZWuK_8yk02t7`s#IprutI&W1M&k^fQ|SMQToE`E6{@vWwfs9WLI^)jCm!Qz__+<^a8<u1g3jD3+h7kR$CUG|MNJ?MnQ_w0#%vioqQ#Cb0bew%g3Gxyy+(*HpP{NTQ*!@L>N-&)pN?r-bJ;n$qwCy1{-7z)3tI!*HFy-R$X#}fFnJ&~vP6uCc?8x63Z<CQDoUysLqQ|lXf?pgisNIlgWE5z3>x?^4iQ?k*&(P@cO9D+QTJ-RIY-U<_6PkN5?Z00YhbNA-5-<1VFU_W%4A#rTC28gds_zV0mTW*s6Z>NZFn%5Hfdux)vZStx!nBVs}kKE>9T(uB>z&6RpHtX*)FRifQS@G9Q!2K08NygP{eh0s#mDE9foPSmN|MEn9t<wO^H=$bc*P6a{PV{eK*eB-oh~ML(_{z<8$UiSu;+qcsEWUc=IM%&(+iTMQM+MKDH`=0qLWa!O7U3(t_E|Fg2gO*gYku&9|AhN)QUvmh3qzdoxs{IfRKpgczt#uO!vzU4u99*L{_;57ry<WIj`^c<@pa!dm!0N2?HS^SU6DAZkP?ZbKJP5g6@Aoih_gOaeB0bW_;U~9e!MqE;@kWN!r%BI_CxCgJWor)oP4F@W2uAvoDyGMR}BC3Q>lZVwGjP#Opy8N^}MQ(=XUWmzh@PW^*7HxD!#IGHJ)!Hwj%$uLd1U%falMoACc$HU(tWjvr5c2QsS$%J>|Ks-}<7`u|DRy-Qlk>!SDFsnxn71dJ*S~&p@pEr_t!Y;;7Wwnvx^&^$TlpZoHk3`Zr5KeSY2I?0-9Svs`=Yh(E;*^;zFO-O*QSm!LkEdmw(ldl>h%Ar+4GHz#+H=eJ(EO5&@w<*4V9k>aa^n>)={Ykmd&@B9P)t`)eCPTg?!^LA`Ty_5_1{Sf3oW1Qrv?)Da6iOei_oUe9qJ^J5_t8g0EQd`bFZRjAxZ@d=cW;As6r&P<h)(L^|FK>n4I}PsvzN5rf+CD9F%wO>@5noR(MLs`1!SiZ(fShA`;11L+Z6ltysj8E&wC=S<{BNV+k9`3D&9j(qX`1-jq3|-t{MBCH!H;U`JZ^lboWrX36Zm}2YaS8s`M#k%TqWbGe~5wKvp>dl{Uhd^eM5ZBy|~mdj%sq1bM?h@^2NCNxc1`f(`F(5$_zZm!h^(DJZ8c#ye#9ILi?ltqqEHCH|#^}5AZ)vg@4(UA=khD4Sqxq_%-*S{*Rv{{^LOStK7Cq-q&i#dx7c`iRT{A5#`+L;%md!%DlAa2a#vWD)eu19dVBJmT|4uvc*@5mcdUrhB_=g?Ce`Q$hc})HT<XNP@nOQ<XpC`=_l_6+Luo-Zd5t$qub-e*9%)#IQq7me<*jV=OurMqip{L{#9@6Ps<+3)7;rl&RgB>4%Ts`4e>{egnzaW`3(6M``@()=X07L`gaUPo^E%=*S39$_<^@2zM5IL((%5~f?TlfL*Ef!Z<fgS^P0Ht{C2=U@euKMTJV12e-7_2`WD>R^*rUh+2;FK@ztLq@O^DhQ@l5J^_TNmaSuTplMnoYMDbO1Kk{^6Eb&dFvv8i@56AQEW;ou<hgZRG>WOpY<pAu54;tVce)0TI4H4gZ?*sAmDHh~8YZvODoFcwbzah@q+*EuYSa1}6zpIF!5RN*msK)zIL?QD0`)I^JpyC`}=Yu@IER^_qjzxUE+ZDvuiY30XcQgFytKq+RkInxaac<2<o)hA+F3}BfZWsO$@%w&;_>Y>4Z~d(w-iwAmMf`vs@XK1jADoK%%p8X}uALF5bRFikC>iI{y<K?!%=sSm58H(PUuW|@xv^E&cStVI`MhMrFW8H7@UsfUY4Zc(=N-nlUsuBq_d}dl>d1SzwZIMM(p(pOzeotMq7F@Q-lo|Qzge-wu>}Ofug*c;8dsuj?@Sio);$&RlUhoArO9mZt+^8r|4-qFKXo<yIX&U8yn{Fyxrnp63&vf1AM^U{y7;E14-o&Mitn2)PmxcfG<*-`_Xxd)_jU0<O5@+1T(Mq(A>u1b)heevuMdD<s{r}z^hMoblf~D!eup?b2bJ^{;+r}zs&cG@d3wJ1=A_Q>-TUtD73TC;zY}}=ZPPrABgFo8pm-@!6CM8KXPB~0ssH<*{Gz-3XMghR+U@`QC%-B79HNYEYm|aIgBnGiXK!=uEso9LS=5inv&hq_Gsx4)7HSmPLY_pOOrAs@Pc@UrlgCiUk;jnVqmClKM;=anmuzS#c{q6(o56#q{m6sJy{Wy(y~#bP!Q`IgKzr*-?M4kI8`^_xXm@fqaz|=sa!0a1wFB8uKXS3Xow2ubYzCjAo*<th7g7tzh2*2uBjlsxL)1L-A#x7&06B-ekGhw<kGz}B;4FJfvbQDnwusH(6zWQH3V8)}EqMib4Rtel4S5T72YCy5CpDeClWe7Ck*(xC)V<_A<o(nG<o)DaY92Y4e3*KKe3*QUT0lNVE~1_w7m-g>&yY`(b!stLCtskJkS~xgQA^2}$mRA{Nv)ukk}Jq%YzAMXmXI%!&r^%ZhMpszCx6Oj@LB39@>%jpY9aX~`8f3``8YYBdWf7)K1j_WA0&T5-ADd}{4sSm`D1dny=71{sk_OBW|0j|Cufp(QFoAck+)GdledvKQrD6<lGjmJlGl+_sY}SI<fYUk@=~%!oln-t3#c*V1>|^YBsrcul{%I@mHa++1o?e(IQ1QJIC-$W^`-WqzC-RqR@n?5NF6~QNDiZpC5MqmQzOZv$rGtD<cZ`Dsq@Jnk`t&&WJ4E`jh~wK)>JWG1?*pc?X8`?b)p8@+Z=mKbf{q>Yiww;L(P-9CWbC|Sfk}!Lqk_Ptf|4N)D6n-d%)mz)HLPyJ!7!3r?yeIQq#y=$=lfs-bCF%-b7wcT}@t3UPWC_UPWF;O(riRFQz7v7n2uK=a3hYXH%z<XOp9;ACRNT6R0D}6UY(Nq2vhi5b6N(5ORNN5V=1&fZC31Xj^g!wF{fU?Wt|ahBhU)C%;XtNjB7#Y-oM5p|6nNCbyx!Ms7oHO?{o*n(Rw`gX~LgMQuWEMQ%xLOm0bTL4B3ng4~?yMQ%>^p*AA>kWExivWeWx-n{MYO?zv=W^hAlGjcQbZ^&lwOKb+$rZytiCfA{Qk?W8>sIQVe$S+eHlV2v+qc$PeBiE(AL9R=#MSY!Ii|kH)jqFZ#qrO6RBiEqTC)XgmP+iGkgI!#`YW!dSvhe$lW^{J?2Zn$Dr1RGv$4@@C$NJZops>O2#{RV@;3{7fju<Pd{1d$ot<n'

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
