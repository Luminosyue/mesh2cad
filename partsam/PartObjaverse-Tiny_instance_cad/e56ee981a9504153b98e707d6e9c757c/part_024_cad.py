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

PART_NAME = 'part_024'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_024.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_024.stl', 'source_sha256': '7ccc96cc9c47779efd65797df08e3ec3e4db377e77301edeb8d78adc207b8e9f', 'input_faces': 438, 'input_vertices': 331, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.46006545424461365, -0.19271989166736603, -0.1740683913230896], [0.4890356659889221, 0.24846072494983673, 0.23686698079109192]]}
GEOMETRY_BASE85 = 'c$}r12b2{>+J<|GLmWV&C^RTZhA@CgrU{a>ipa9-MY66410v#%UL(4TA{Yq^S0ygakYPwp4<o|>f`9~3!bN0vU2z2iATI1*)%Dcf?wa0n{`3EH&UfCopZe<Ss_MGkeJ_VWeTx>WY^lFG){U%p>%LsuvSgICDqGXWq)(kNYRr_T6DK{HWL5CE{L}izfcyFndLYS~W<Awl^q485(i^n18*~`kra`LRVC-Y*Q`1LIeDJaK(PJd<G4l6Q#t1%T{K!dT#BsxxEz?r%mW@*F4Ez81S6U1qvT5?E9HDMxUv_7CoVtHi=MWyvIJqIfd*<fIW82J!N62?_Upgtdb!^caQlmen<>mPK5yj)fhAa*6^fIqYjeOwl4Dd;c+huN9?&tQ3=6mG%;zoW1?vxAW$F98RaqFkxc<ih2->C6Ke#%hieg52X$=#PX<@$LP9%*uAM}R;0^QzE%xXzFNv480LB)G9Ynw!_l<obFgxN*Hq9x?LG_0im1pJ<eEe%F4XSMPMs`~W|%cyx5n{LX$pX@NJd$jTOZf&7VzM@QZhs2?l;zPi3fzMZ0YY?P7z+Wt?y^PLHfCpKGgca$2B+d3_Dza_Y_-!wP(o95<zi`r?S`$uzg|0KAve@w3P?Ssu#{gm=*oPW>R8Q|p<k5#;Rxu3@$Qsayn`SvKq-J4Xt)v(!@-u$k<y4IUtQq_<B+_|E-J+sQkUcbiQo$$t4cg<#xR~ot|$H(0|iaUFTt_kFyP<0$5--6rZ+jT6Je<OFBzrN<~b;Wi4SjO?sz4_KZ_mP)3AkCYv<}tW??Z%b>ucvtYmm6FBbt3Rs|FoR}{?0&EXYZ^)eH(5i^$OIt-&WkQdIjpo-%>mx>iD@^q5qDs`cb%9KboSrS>J)1^`on|ZVy`@2Oc-p$H`LMHP*+1>-Di}&R6sOY*db?=^0*q&EtpR>&9*g@I#8n){focuM^XJaz>!Ob#0bf|0`bw>bt)vZZBVu9pG0Lk1kt~?XMGsJED%CM^0AQ5mw)ZoAvE46*ue0zfjz)?-XsfJ#2j}xMQr3RYdWqu|95+;(C3YC&#Mszj%x5@u8R0^AYaABd=s+`?>pq;;!>_w!cmc9$R-QSby~(bsa~K%k$T<;gN}RHV1f?;#U2+oBeg-nTp4A#^w3BwX)y#u=?%_#iK@jce&#6dcpcp&5ioz{UlMxxSu4}q5o))yT*D(;89~eBmESQ8S81oqsDrg_rt_G827`dO`Qw-y>Udg@w|gO-zx5G?2+%!w|<!A)rlGT)<wlF^5aAI9{1X34A|xAJ%cvn__z(X@&<eF57De99*^fA-0kIes^&c}G>^d}-Mg>%a|a$@fA@NS9Sa_7Q`LLEM2CKG)LZvQFKv{^wtl{A{uo@pZ@?p8Z{01ABSwDYyy9`*2cm0M9}carxmh1xsJ`Y#{aDdtRj1q%wSUrk1-MhW+h#wHcN}ssEMIdo-$`n+FKqoaH`mkY>Ff>LKbo8S$1S~}z^fDM>-zH(e6iw*{np~-&anIhH}dVvt#iZ1qq#Yrc>6wX*nBlN=W9)=9t+Da#78X2^Yi~!#~i2T<~S2|jL)6s?j^<D6GwIh>hO7ty?%68ppNl5jZUAh-oK6aG|kQTH0#K`g`w*JFEn3xq4~lK%~#hk=L;`1UtPzXudZXxx8tz4y<_uxhvvrj4l9~G#~XKEm3;r_RP)%LwR;1+;*6PI|G9fV^yZyec2|JURy?|_j2b80daJz0V>7-D<XdwUkEUHv`H$wNd;9%~ir#Z5Hsh$;uke`W&5yZW{)Dq0kHi&s^f)y?tGK1-oBr$TUj4FZxoY1GRQ2I8c=VA0u0KEC|96TzO>_PEkpb|_O+B@Do%q13V|>p_aPxcC!WGLphpfNm=K8xA@>Txeo~nL&%1%Fz!`;i}z2~Mq|D5-nk5AgI>X5H_WU}IM@~x)Bw}h^z=H`0BW4AiNeWH0S#r1vOdGF#!Ve7BCx&E4)>#w=F{#Ju$yneCF>fW)_c8>a<0k^Z@cg*(syF2!|Vf#&UbHBOUhUNOlqw8y~$D`}p!z1c*IW;TG>wjiUUKqD)9p2^VPDTmuy&-1gYi=3&Zf27$VfmWt{Al(Bb>4UOXL|E^`jNaa9zCV*Gx1hY#iuP+<KOyXUKqE#t@H9@>t`zd)=969J>!+UFdi+kNsWKNDmBh-r@Z%@_-AYKLV2T^UVfzUcEyXo>Af%7Yjg9$c(mU%HU9ib1!4In*ZGkvlM7UP@cys4zW+xmFU{*5!V}MhCC?Uw&8raC^V;!YLD)K*T(7fRb5lXsI-6XtvzxuQAZ#C+T<=58&3$O{#J+m>lY+2)XmXt&zkIYHY#*9j??bodxzOvPxp`eouCGgE;%x7C9P{~=;KuVybMyI?;KuXI`F^Q)zl)Yl&Ghn8FRSlmnwL`Ct@pDU=Zimh+<bq~T)#iWdG4EBzgNV@joBAgM{~1|$#tDbe#SokeD(MfocZeUTh~)Q@zi*aO>o|0^?6O6crVi2d@q6*dM|<(dN0y-jQ1jY=@gGgJ4{pa+TSUZ#~ZKo_D!s4hB|NSGU|Q&)voygo|moO0~S8H+s`8<kE!1QrVkI)vDb7_-`{5i>sWAmUsfRBs&T*CCuTm}BHv!7xHD`~U>!8K;Cdb0QO_tod{JPXHFqCa6j<l@>E}YPZ-N`w*W`))8JnZld0U4192JZR=gt45?iZ&QDn5T;rrO63<%e<m;%h2D**y?ezYwRsJ#No|u=*xX)GvDaK-m5<x!ylc*KZDl?VkiU_K)V~{?XjrKbo8SC&7*VV{*NJqW7d6_O6@xy9C_4f4YZWQ28A?soy&;ezGLT$0KlO|EEj*`R=?%>%#IKxXzC^e#PVFeN1!ne&x&=`dQfiOmJf#M*cALh_~;`tn$8>yEV@3_w(qbf2#f~1|RTqx873qd04tCH(2Kz@BZlCTV4H5RlWVuu=<*tb?nydkA;mt!Oh<d79<}JTOZ8}Jr|}tcRcL+YF_C29&LBR>o=~J_dA`duNOQDw;%8HzMngAYe<*({dH`3MDGWkzqo_<JC|eBvEcE+!8(QZkFI0vAE!jq(_!<~-29zQbMtpL&CT_R$98zU(C>b5^LIaIM87j(*Guy_*UKI?Vxyl&;nv~bZuHkFwEy9*-X}&KN8g_h1?$A>zO8;=HOFHsZp-?E0{@D?esirmldD*kj8ax*YwSqhKjBL#|Fnkx6aIu&|Eqt(Z`HER|M#EpJ0w|Fdl9#zx8duGXoHv90pD80og&(z?eT5#?a052K6k-7pzZOpZyk>7a9-`}a$J{lN<UYu)$<}=w3N@_So%jemiiQahKLCw{(wG<f0lObpXa!bI7e?0CDGFOpGDhc5x=7U!pkU0-mh?Zd{yW#A}*qr@P8BWcM(6LKjANua|}I>KSm$jSLe!e$a9rVQpb{CMay#jvgAlVN5t!_jns$nuZWl>VkY_;UiK}=+@&Vt-)3y@qL=XUJl8qbb>@7PdUL5cm+L0|bBy5y5ig;y64K8`AI85#+so)5@$;F_0(1`k9TDG)cndv>?;+-Jcapl!QhVW_Vm)S{6Y!HoJj3xb?3D@BX^|v<4_Dd>|0CB_uAfx7cG8a*J}P1&`ZT_yXlp5=8=8ifHRU;)qkZtQ?|9a4JnJL<4<hP`_P?UF@#7iq!{{UUzliuy#QW$H{8ka$Y2QxUUucs#|3EL`zY+1Ri1*MB@LNP|qkS7~-_Ry=R-&u$-&yK2wgb(@|I<>Rx9`xO@gIrUN&8OPq|f1eOVL&MmG~{_HoP3yHO3-!9)6jKh0K2;bN&!6)kU}CbLhVf{TBZZ)@m!d9lwOS7trhYWsG+LIv=0Q+;h-t`0ey_(d+nC%ws7!5ATw*6TOVz!8txccj6xt@q0_{RjK3g-Pxx-(cbu8XdkpU-lb*^nv1tZTm2+;FRagJMtb>K>dM~l%4b#j9N#>avR=|pveakwQO5ZwV;zs5fKJBCHGh{ixQ_n?y@dahrS38EUekyBpS%y2;(p(od;T@+KhFnQ>tBp(0q2pQIeG7!!<grBU7NEu4bf!$Ppm~b)}|r8Avw~^&$#@|H$clIDc_BINN=<mz8USki3ZF=Y8m`I=JF1D1uyk`d}pqQ!@1->=!kZ~cf@x}Qui8pUzYdqb|PAf=tM~06}=1J72geQkMD+;?_6y}v=Y&QklsP>#5?#dXj^<2d`D{D!#Sl6@r_{!W0X1oFV8)Yego;F$JLkizO;3w&j98vwGX}>zBSszw+20_*OOZ9Y3o6I58CcxE`yn?)Iq+v4`OYk_QT6L_orWf`snrOO?z+JI?|^f>n*hxz74(=+TFMIcT?|fYPF@UJMG<Rll~SFwM5*ER>$8eqBiZdX_NkOj;EkC@Y6*s7cmX}GkzLA9j%T}$4^CT;Wvm_CnAfGJ`-Jw&%|#=*W)+iv(XLs4b+nU4H2n~C6#ka-$cZl%tz`Xd`<LLv^GAAanwd@`PO3*Ycd7@1iAwM1pZ0-JWjpGVOi)3-?*i2LRa8poO=zr8NUX<8r_IrjbDr|$4_Pa)6q<PCg+%rF2*mWuk<&whBZ;WW~r=cb+iV46XV~AF2^^a&ztBQ_&4#3&_ClB;a8x`@!6bXGrAEkzv9WSg+<XKcyW95{%%4m;gis!Xcc@V^7L2CBKSK*G!)SoZG^8cqP&O(XbQfbh;kxsN6X@G$Ja;8`+PZ$%TY)BdK}lIw)Dv&>RR$kuhQG_#Y9vPQ5>y^FCoIFpG}`++GI`{v>LtywMwGJ@g?!4&@%W^_++#+J{eyEE#~u8Ij+iBi_y0l?bT>2P5s+AztlRu@zkMa9p)x|a}i@jG({u$ruY^j(nK^9F%E5sABP_);&&oOix^HwKNKB<ABw*peGq>?{x>2<h<HfEFhcr!(NXw&@%N#>#ovd2K#pH*+$JI#qmA%V@4!n<#W!cpX=pQi3+C7qZH6DoaRhCF|4hVJA`YRu@rOkeh&Y0t!yh8&Fj{~=LaoE7u2DgZwW5gfXo}BQ;aKWT_{t(G!79O}uRy=bXeImsagKc=_FKw-!tp8m0sNO7pA_*0><joQ_<q=aYDoVz$0zZ7eC>JUNIi|0=lGcRk7?V-IQDWbsps*s-VK=4f8+P!&!g3nl$T?unxy(ky+Muh<a~`*_4yRmQF>V`h4rfnuS(lZtm&<+x76bJ6#AA&Z{TZ+C`xWo@}(~(;uaAl&|3KFB5KH+G@9h|H*+kt2wv{H6YNc?pX0y6??ylM?Z<=c*Ms!Yd-oiB^Bn!9kJI;a{4S1V-+cN@J&XU8oP%gSem89ezWxQ|<dK)hp3wEqaLzOApEz-vey8cPi*ui4oM*|C{!9AHeK)9YQjy9<|J#3s`p;j~dwBZ)W0cu5`17m3XTGSF_%U`+-{SI~EFPvsyf25P<eRDWKbjI7G5'

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
