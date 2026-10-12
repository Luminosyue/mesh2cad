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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2e5436e635dc4336984c76a5f92c7141/part_005.stl', 'relative_path': '2e5436e635dc4336984c76a5f92c7141/part_005.stl', 'source_sha256': '6985a26a7f294a7fda1449a4ebd3e33977517630d3ec2046a7abddf7f31868da', 'input_faces': 492, 'input_vertices': 367, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.009584452956914902, 0.0548369362950325, 0.26575201749801636], [0.025031547993421555, 0.1825915277004242, 0.4999998211860657]]}
GEOMETRY_BASE85 = 'c$}r133L@zwuUQ!B8m(W6p$ed5<n)IXD-N~L?FzA42h61gAEa+#rA@Nh>S7_?a*-o2WWW=F#(mUARzP<(5JS7X$3@^*GRY8>TBiIuKG^hoL$vxz4cz!+Ux)B&$*}So;qjWU3D&*8D-0*I{sgMXTbd<d!BFLI1&||RA+w9+`MU%a^|(1efPo?r;6vxpV9S$Mhwgxlj6*G?n|GXGjGz|^e$=X-EupnH&08?oijIYZuabnbLLLY5x-yd%y~JkKW}RG-8t^-CT%-(Y@XJ(Y4f!E)BcZtSG%VWFZ;}c2jpDFZF#Myyxz0n)1Fa&*Ec*rvH6=N;>S9^UQoJy$XD$X@%e>O?E|0ovB6yymp*Rn@@4;gMqiAJpTF+hUh6!yPd~<wcgQG;Y9ILKJU@HV_uC&YD1F?(Uoxf8^1IKtU;L6)<qD#Fr&-IQ(tfPhK+lhj_dl0Yy-cxp{M`DBym4ssaY3ZNaa5t@#|Pi%9k-}~Jr3G8<A5KlRC!-i`@lEjaB};-;%D90&^jOEJA*3~S^nvv_eRa1kWc^4&%+jY<N4mey`{$|@IOCejho~2_5A$$Us>}l<eUES<6HX|Mzs%o^LcYB=6U0g+uNSc+E?up*%u3=+6TUw&r7eJ=Z!<+zP+W#&G@k&3+(ZHe8F6=ea{7ZymqF4?VIy4{=)s%^$q!Ee9H8m?HzaX4zC}_j5B_s-qL;6_*XqP%Nw_Mw^{Qo<eUDD|F;!Ik?oCd+V^cdGitpDKI<huz4HlA7fqh-o##&#?EGN-pDRSR&pMV~7}Y+0-1kj;=dUHX-uUeL!W*ANs()RK?_8C!&svXlyXScQv|McEfxvI&`@#7bf6LCosP_54-f5rD`rQ-7Py4E#J^tD^<B4B#s_MR|_JMEOzj%3qcRq<PcbA@TAz!u6FMr#9tAFjA_QReW<DKVk%UI)M{Mf5ytno2^NzGP8QSF@@eLrabZQgM2xc4@-=QDoR;H&mq{k-{2FYma2nPp#J{F3tr{p*{$?qq4-`SPH3-L;>nedP(O|7u;|j%pwHrvKIhdU(gJTmN8`@6_}CM7PPsrTy5njqgOYkK^n1iI0jS+dF?Qj%*)Wy!o&<&X;}_>BpX!Zy)zS(<5F#YmXF1`SC;xt9_!$MBhKt>_n8Gn0d_ioto*Mf8z%G`vSkDw(ke?0YB}@r;DQ6$DVrHo<A4rH}G`oPAlJrd^4Z%)3O%Z>r4CQ`*+}XLp=R`+*)5D|KGKL;I!rE|G3jycOl>OGv}w#-g$NGY>k`o(>isw#w}>S_=lp%_Dg=S$1VGwG2ZKPM|WH64nJ%6bbH-(*qr6P-c)V7_r5>2IuYeNS1hx9XI;$mW8c-X{QT^Fe*5?}cKa6DJFNAHpY}oZSH0J(d!Dq8YkYOwEPUOMb77X>e#lg-pZGsp?DYB@xXkXqZ1GNO-I?~i&hCox^YQg@6UI0B%JhGs+MdY%@pb#esXF_k+LsvL<g3^3ne2_*-^bhQLi=W2;Fr9A(q0$ZH}muBbJIP)!vrfI8sF*Y`>{Edi>>x5PX_H(o;1GBlg8J1()c=02K}o%8T7C6r1njo434Yvr1njo49-X8N$s0F89y{=roXPfvAzcb|4+UjGwU5c|NCxMy=VNy558~Kd+g%TUwG@{rkIt-LcXbcwND;1e*UwUtUMO-&Ad8MIM>sPEA2dkU-HUUE6>Dsy*AJL_vb#@UHUo(e)@?0QGS~7&HP_qkmsHM=$q~Nul=Cz^8NgY<?Xsi`=<TyJ@Y+(!*RQA!B1>FZe1_q$J^%G^||S%U9NS#vYzj=sPy`Zz4E^0oAu><c&xazpXhSsp(sC=`Lw?-wrx5Q<(vMUu1`GR>E>p3J*j;&4%%m)7(YIHfqmWav(CP2U0>tpuc)~v>bQZgjvHI{#-7OjAAZ9gfBZzRJbV1{OM2&7;~$)V_Zs$m(7rmK{4-PbM}4k@@y+}+{fybSKk9s(*5zN1I&R=|+>$Br#ZmLb_<EigU(XZc>v^L6V4keK?V-r|j~|-<_@Vi4`cd;g|L*=vqt<W8XB>>L*Kf!-_uVCjJzwXUz*l+3_&U#|4e7Vcd#&=D@k9Bo_nV#{%EQ_>d06`<595dOu=dUTtgvRe_ga0w1it!yF~0tOF~0tODf#LA^3wCrjGOUwJrJ~4^+3>G)dR-Y^?>npJz#uY4+Q<IdLZau)dSi$^+0f3RS#(2)C0l!sCq#A!F^N4(iPr3()FA6&Gp3()o<E2_1pGEk9zM{^}O~?U2S|_&l_LY^Fe!6&l_LY^TBadJ#Tzn&j<ahdfxcDo)7w0^?cA?)$_sUQuVy?bv+;Suj=`re^t*1{iu50_@R2fQr=4M-}U_(zP?|JReW%zzwYe&N8{`J$DqBse+=5I`^T)WC#~{ctNY@R&wLB{<T2yx`{Iyq`e`$Ejdz~vem~@^_WFK5<ePO=_p;}Qo>$<9o>$<9o>$=O=M{;i1J-)|sJv%<o%f8d^Pcf_-ZQ?=dqMvy?*;v<yr+GW_k!c9yr+GW_k#0Lc~AR6-Yc8!A6Gx$!w)^*!w)^*Q+{wiZu-~H_q0#{S=(!@^X8#?K52aYd@|NxhUe?&rN-CKOO3Ceml|I`FO83SYn?y7_VeD5Z}PnM&GRUH{Tw*t(@)x_-}#?QJ;x6Ds=a=W9r8^*<}7^7d##?s2flg^ANcAyyz%vO`1mh(c)s2jFuvXw$iGl$z1L3dQv|-+r!c<Wr!c<Wr-<J)((^<6q{dhKCTYJ};rFBVaYDWsf8(otoRDwo%%`?^zTQ_derR9m);SwIRr_2a-{e)}t9`DJZ_ek<4Zg4U-SG9kTWtP&zOVKHL%!)BU+)8kd^4U;J-gAno@yU6<g502A2Z~ebvkaV@2h>)z*qaK`KjkNmYzSs{f_p{_&@e9&)56H#@GA8PWKl!dFxc|Q-^%hKfd0l4*6!i7kuRTdfz<o)xLSwjz*7r{iyx-tme%<U+?1^U+?2*{h{7w?>yA+1Oi|EP9Uqo?VhiHw-EA8y@9WPw-EBped|NBH<!L%LH>U!V~eNicN!tz%x8T4JB^TU#{cv)TcYMq$d~q+)~{sx9c^E6?G5goyBigpR3|sP)K6r@ls}`<KarW%?tk?YnRcDq{C|HUlOa>vje+POcp!X-8;9g`yKxYG3qA<H?Zyr_w!85X`U?CK{IVMbZX9-FEBYb472bfBN%46DJRPkJO9+og(_snWzGypGLbx;91(pzQi}rvegl|E+!4ksl(GIYLa96Y`EFs(<tqMyBPejYX62ddlKRZ542ya4<!kge13E@IF{^iE6+^C!4>i}3nxFgyDmJq%jZ3IgQk3z49C4|SLRbUC>iD+e5LU;mN6_yYljotuD2oFGSf+d7Ip&elf;WYFPSVH(`yf`eH5C07Rkq~~}je72T>$}kqO@kZ44cxfXZ8z49G3aP`3_J=Q35$+^N5R9<VeoKxC^`fl3TL8&V9~*FL(c0uv>JRJoQhV5Q{n5;8{q5VnrIDJv=&?wzR`_3Xl=9>EbCr!!Q1FTCz&fGFC0P>@FCjlK)1v49?3JWpfAH8yYUI$Tky;1GWccqC3LBi%u7o-_EP#vpl`ve+*rwV8wrm<SHL6SVd!#rIoHWt!{uD7<($VLLfBj@(bJ9}!k?haN`0o~obOWjVRQxjF#HI*5`F}J6kP>B3a>`jz^mc4ZajvrL)XAER;M_(PvFz&r%v*-2$!ILflJ`e&@=F7@aO0`_;dKI8(*O3(Q~j|qtSehRqz^gEW8F@M~vn3iQWl62CqfOz^l<w=oq*f*G<-toTsdl&(IrElAlYs1g#EN=e@!;SwCm^?84`q<QhB2XB9rrXBPeftqn^EpJm+6axOLSYN54RtABI(Za4l5odaJ)e}T?{rTsr>D|!!nzZ<`F<7q;8mmB}>#_!$u9^D1+qRsc{Lil_5pKg4I-it1T<viwcju+vt(RuLK@FjFUd<p&ry$=@s0ltUNmdEiHa4z4$-=cZ&xA5Q5f51OEeqR2A<A?Bm#}DD(IDQB};P@ddIej(r>rr&LlU%dHkDx<g(M%_~-i04V2Rq69AZ&7o@W-ee_hViQ%Q}{MDC^VYd|~q)A)JbS>LkBYgs($S!Kdg`c#+FLGTuKj=E6tZc+K%^m_qnPbeof`bA&gc8=Yh=Bs>$H;UsG(;fd%3Cs}I=_ec9V$=Xb~E84|L)^ft_(RNO<_7lDZZS5p$Md7w+8z)&?3U@|3Imud7xG&nrN!G5y<I!<Wvep%zj!tuuwXyI9biI?TrG>YmFF48CTetw-3m3qL(Rbj(@Q3IJ@Q1L}>7pqqK1&E!Mk~RU;dHbyoDR1`+rsVOE@)@C3)}<k4)=h&p<Ur_a0j$K+yQQiHi4VMRnaPNRk$2l7A^-%oi6&3<FkbDQS=CWgt;zU?8Y0+_t)TU=u_}Ecq2L+-U!b?Z--~V6VRLC32;C3Mz|l`1+4^kf!m=K;dXFq^h&rj+y=b{ZUc8huZ26oeb8EPA9x(v3?2thLvMqp!Rygk@Ot<K^hx*ycrW@N@Lu>G^iS|R@CWE+_ybtxxM(BhyF?@Axah5LCAcv<3~mg!MYG_xaA))`xHH@xoeFn{yP}ieu5f!a8*UFbL5IUl;3{YzxC&ery$LQ0%N!SVU<u(PXfboYn7J-|z>WWO<9CGc1++qn&llipQ+#a+UkkTEZ-d*wz0q-SZ+H+o1s((sMQ6f8;gRTUcqE*OPKPt$JJ1~X4mgI6g=27Qv>)6Wz6QM+z6Sov@%2hrLiiYZ((zeBcn|t2ya#?3-3&hqFF|wQC2%&{3(khSqv>#WxCL4bZUNUvuY&8tb<nbK9k?c%0@sA=p;y55;D+eca6`BiS{-f$_e7h*J>f~{t?(rHA#^JI5d1v)1pGX_4?O@MV6F?l@5Y;M6cNJDp}&TogC9hvzz@QAp}pa|;2vlbxCh)4O@&*+4bTd31Gp|)4z3H=KpnUSTpKL|*M`&3@^Bj59K8;14tGNv!`<L4GzMqEi_yvOV)z;KarhZ{H~L$6H~cPo0)7|%61^hD=P%)_Q+#a(Uk$fH`@*f@p6D33C!B#!hBM&7=rnjRJOZ5skAR1uGvFccKr|N~2=_wognPlap#9-n;EHGqxFY;l$JeW13E|_Y%ynVWB3SZ<<dj@Ocni82-U9DLUxjzV@1ZB*_u%s6Ldl8c3E}4G&2VN$N}1HM|L(uMCja7+Y^?tPtKVsF1C)MeV>bx}n*x~`S4e&2E`~DRP3<MAw4DC|62r<O'

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
