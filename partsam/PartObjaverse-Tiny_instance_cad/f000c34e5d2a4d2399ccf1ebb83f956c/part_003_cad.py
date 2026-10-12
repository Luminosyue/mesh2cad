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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f000c34e5d2a4d2399ccf1ebb83f956c/part_003.stl', 'relative_path': 'f000c34e5d2a4d2399ccf1ebb83f956c/part_003.stl', 'source_sha256': '1b18ebc1f11baaa617039140f35e4ffa64511389ee70d7e4c2097fc3bd2314ee', 'input_faces': 434, 'input_vertices': 283, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10940626263618469, -0.1566494107246399, 0.15963275730609894], [-0.05629873648285866, -0.07180154323577881, 0.4236188530921936]]}
GEOMETRY_BASE85 = 'c$}r12~<^8+s8M9s0gSCrf7Ce4N^)|d?hCilv*0*M2V(d5D~3V!3JLyk6HPaTAD)`YWG!1%K--*K*B?!0xE+8gJN72!HiOK%o5(apXYzQ=d|8$t#5rFYd!1#yMH&&dG<bg@3Ze=IbxWLtB>HHj-vCj`W;Q$2_eHn_=xu=C(N2UX>#JT@iS&Si5BF`AG@v?9uYnw(n-80=J>}<PMnnB-`C{dKQ`Du(BvOGJz-WtRQ#LM6JjPye{j^>iIZ)9VqDaW$+ph{J%f7%ntDAQXqspGKmNGeN>DwVvku8x;x-?aYErMA2(hWwx#1vv9-2wMdE&%E>04`R$=A03!tF2q#O=FRk#Bk5DVOqPMpJv$JC57$8A<JxvTMgF&*Dh-U%AJAaxLXCXN@LbZSBc<+PzMB#PBfkt?QOkdu#ql%43QRVSiN&`J!4aqCB6rC*K^spWAo1OZiQwTCpE^lH1Q6M)}RxT97Z)P2As`>nM*Hcr}yy)zyuB%{`gxUw$Z)$BWym*K5fa&32J*E*Z%AGZV?TJY2!;bK=>rdW`F7y_|f_ZI7XTb>v&*s|S<VuN+Oj$*oVOemu>`mQj9l-V>bvdN;%Ph=a~tPw<)_X`Dlw6_Y<SJ%jpHokPAB+l72f|F6i`7PyhGw&_NBl$7D*E6P#!Z=K_Mst1v8oor?QBky9puU+%!`~iO!&~=l_4p2RV1If3PnJK?^w2=K4VeBt&&%Xa*@~!hja;SfAJM(x}eonr+=xy@VZyM8etqpH+p43S4MaM$Au4(X7oM-BMZr`Z`wKq?7A>R}j$Nv6*P=58&?fv8*PbA;^>2=Cu?p8;>(s~Q|=KiO6p3FZ?zWLeI9Q`<3W`0Y)wz!!_`G@=ReK|j1KhLYj$hTg*O!=)Nf8R%SmxYjTS@SaA-=!zm4-O(<JLYEedo(6r!Ms&lt|wm|wd4n?YgaLk+fT9NTi@xx?f)pC_7=;l+<u`a%@^g+L7pdmq2z15*V6qI!y3p}SM+56-C<m3bTs9$9u6d5IqO0Dih0yVn&;~6r#QdQyHt->_dT!Q+NR{2{DyFzpwuG0uYL3I2YtUxFV*j*&*S$|J?fg^LcOmRx25~3ZC`C{pZy_?w-~ghMDL61bNPO54l36Bn!g|W{Zb9SI@X8%6OU6K?SuR5n^#ePt>S)>-dBFR!|V9>IG&%&?(lVwK9)`Yp7D_9c|{#xH}=ni`uVB2*Rp>&ir0NZ0gwN}a=vc06Z>_}+^_Ug<XfJs;Pv=jdY;}_Pwu4osU;Q|d@<t+&%+7s`G!20pIYG824DSQ7S*p!sW<wcq|rEN^_AqS)hBoyLgVPZC_!GQXdEVF^K~Qg>HeDH^LgD}-^Tva)w~~<e8kU%;7#mb7|Q#~xJVxVxb^I>dOTad9?ff#4dY<lSCXgqmA!j-UEjWH@GW<5QGZQU0r`60>d{r>`J8U>)miiCy4I`h3k?2C$utg1=X=y%%m0$=Ja&faF$b*9)B9%oeiFOg;ER$9zHaahWBZp}*<X=l$glkx&*L!eqVc-J&hmY^<W+3&?`Y(!^Rf-?)%QdB`Fv)MvHd82zAv>Ae1E+^<MusLD32xK<O#j6m_qrwjh^HEcKia)(`W<V$2sYoKQW2h2h1nm)Xl%p;1^c%x|{Yzk-<L`#`~*fU5Vb;TzP-BU-yw8QMOONt{>%zKg0WId`HS-&U%;IcM0P<<LbD5?<rirdwW`UV&XCOSC40Z%}L%TV{h~NO&j}P*Q4G4`+Btd_VuV{c;y@N{B1ox%JaAN_{jg;dVG|BLSsI!dCVZ+QZ<VETQiXNE8i)FdS6`L$?G>Et4Qyw2imir{aJ~@$3ARc5>jl)lXHmfi<-2};43#X*zfAc_wnAV+&*aqkLSnl)4rj!2<P_GyHI{n+LC;8z)-F~cp%TiX_gZPziSrf$%vr*A~TrtN7vB)V@;h({Ze{$<@STd^ZLc}(eA4u%XoY|Cl>2{<;t)8-0`|i`PG#j*!ODA`@=8Wi}b!YvYYpLoLkg8-rRmfDW9iCgcj<3b$fq4r`VtG_Vy{Mye>AbD$)C*dM!WiUJf?of3z+tw-|i!cwfVF&EnaD{rKJd{ooBztoN0rPF(-;Sv(E{-8p|^8*YE3BcC5$zLrjY+H5|rt#YROWtm;g{@S~IAA5&z{hf-*SF0BB{VEGH_*&&q!+cP$9N_jofARTL8_Ca?hkMBvQSJGhu%&?W+(_m;UtQ$q=E@Sz)9O9;cP!=nPEq8WQe)UZ`Wf#7O%L(>bZO7N*J?u^G0&6z&HZ?Mp54OpHstOe@=bZXUi`OF9>sEve05SJUpGIE$NzjT`=KX!pP9a&^Av7o|C}e+Ge3;$uh~Stc-2JvnC0CKM``{~h-4r8s`hmst~21uZu-0+i^qRl0I#F5RphI=;Td}0I-`<&<@h{WFXB|fY4Up>;r96tso$2w^GB#o&#m0P=o!v4=0_gSHjBv@SysM3cmAOE=6-SPFMgWxt39Sue)HNlI6uyxYO6im-}FeXzf%#P4+{oSd-YOl&XaBCbEbO)`IaTl?C)O5`{Z9a<ZF#??;?NZdpv)x^d(<(xXJ$WfAW1h*PH6Jq*alxX1tT3zrS{0d{M#US-h3&blFe7(&{4Rv5p@@dDNJ#oM*x<9-rA;c|2F9vY%bc^$hM#zUlSPIsaz^_}n-?n|x*ZVs3vondhN@%QNH`&nMqpoX6iEx3@e`dD^~DzO~YwzYnhMSV8qXH;a7jyPG^dtCM*=Z@t0S-5SH+3xd~joo^54JUhbq``!Asl*f89jO)p4Lf_xD;lAhfzH%@6kiJe+O$g`5ej;j}*dG$a?U($M>*>Aew84LND6g+RZ&7=5)5kdvz87fD0bGAaKk_Zs<iq-U?7nRw7{*zoG=qPYpUY47pni$$t2@cRkVe;4BF6GKt0n9=^fQc)Ik}L0wYG_&zm}cH$yXBh@O8^J^L@N{gnZNQWB8m<6+qXujN8vX-m55Iwm+};)q`_rUR%oJb7`Ct(%H9`^K)uYJ>Rd>TiEaX8rONkgX$4=spM-N?;X;Q=OcgVajxI>I<J?Yb>v%K=J!JOdX(_5c^sPf^1Mn4;(0asEB5X0Te=3Gqx`FvbN+NbhijYWms6hR3%UL3DDGG2GU}IF@)nO<#xSmD;{&ee=QytC!9D)|9`ym`5q^_6|Li25Cws<FzpT;Ycs%ibNj=`3>QUyr&iPa8d3^d#qV{UU0QPV5Iaw@oI!o=>2XUR=>ke_fQ>eYR?>Qdlyc8avcY1MudvxOK-dM_YUiqBrw3I$bqjkC>n7@zjdxh)lbDezQ+K%^Ik6$={T_*X~0S%mI@IuO?hNrO~#qYbsrr|XH+K!E!|EihaOH3;*)BC2rGx<Du|4HhXscIePIn{{Yzcuee^{dU3$yZXY9@3AeSUHvRr)Kkeuxb6My*YOh=f9t6=&v%nJLm89z)+|4^XogPj@9F6y$iRGxt<%B$ye(?=JBkJsL=b0<!3&pO{?W`8&OWa#Vwcnm41!$>^{Nm+b8mMUFPz*T{_D7TX*1jxTQmx!B3ga-;cihgUA1cgXCK~_2cnuda2Cdw;f^_Pm!9&{=5skPi{C+ruW6!3!G=6tHIZP9L)9X+f{04?{kso$*|D|U(4IZ{<Vn)-{kE_zKCjN@Rd11ypERVQJq?&P27G}1Gj&0fZA*AVmSY|>3m;4jOX$68bZDq?=9`?&OE&z`<-`jJqbRX|C`=?UuJIOejPbS{WU+=na5|R58vPD?+m^r*OSIg{QG99-q#BFy`0uF#o#M}KXLs{UNQJ8-cyMSf1Ne75BrMebJ||=Enl|babESCVZJGy8*@DeLV5mdSj6+W=K6N}{hBrWeeJd1_`VORW`7F5R~Mf~R_J}<oW}EE(cv<^Z^eG7Zf$MwP4y;zpSdQtRPQUUi}<=HW|FULDJNg+7H62BcHh3<g-;vqZ}}<CgZCavT^DXYEr)!|lmmwOrXJtRbzUvyd7hHR^CTgL+n2lHJ?bSMXV=l>+xH*)`qF~Jxz1fH4fD!;v>)dQ4am{oM~i=t?fP}0jNQxQFt)34oUyLW|LV-+9Mj3LpD1%0bDodg`8?pVz0BZuapvc5*qu_nuh`!+pILA4%}Y=5_<#4R!ME=}N@R`Ux=PO%dEA1X4DD4{mFA%`GK25SRwo|k=gqvnu+J+4Zfw)f2X*L^RKK<GC-T*l0<QnXETez!B)31>%;1au!8!W%Zud=L>$zXg#2S3F{XO=?b_QSF=f(A(E#m$*l#_3ne#J08rXHus*KWAvJeofv41Y!2=ro{Xx$UEjrou<WM(O^9R*rUd{qKK5n;P`L`V(4Eub}_$pV0DbHC(sFDTL$-gyedts}plQ*c&0)584>)2W|^>150%Qw*`A4BsU1w-vqM^$z{-Da2fa*GzWYPybHP&EOi}t7kEANbMSiba_GOn%fXAGAAlEwKZ3pk{s=q|Is-fptRf`OhfW922PZ+}!Aan`(6_;J!E>N*fu)WG&jBYw`+^g}gP>1=2Z8+&PtlZSHGw;V+d=)nQd@!BfxV&4!QNm`gycrhreLY=;6`9KXiKmgxCKIT8|Y);HsDUsC&8V-J)qBkdw^#{-v!SGFMz%WmikZd0`NlU`{0G(4-t~1q2s{O;7QOZu+)#ilfa)qzW{#%UItwSUIt!`kh}r95xfDs2f7z5H50rCd;od~d;pvcJr2$W=R+@o^T8LOO`Vu8fEytsw}7?*OMML70^A(h8r&T0X^SSdXlaYPg7pu<EJJcBLUK8@5?l^0L`cp>NIq?gD(F3ECAbo~?m^|X@8PrLR;a59SgJc%YBO*vun*J&>;v|NdV)RCcVC3$zXa<;!7M}aRp`&)ThQCkpTSbEfp3HFK+l8kfa?&FOQ0vfCE)$g-QfM;ozN{{sj1+d;B8O~cpLazgygl*HDIY<g4cpqA|x+?ehOX!o&_BOo&_EN4FpT=1|9(J4}BioAN(3ZawN1LI1)St8Vr{D9C!@)C4}Uz&;YR1$H85}Pe6UZPk?=)O~Ah3W(dhHP$#ep*cmFo^2ZhI3~r2&>;?4zdx6_RTZ5&x2e$=xfOZCV0Cz!1?hbt#+#Ng^`Yd=bcs#Txcs%$GXfLqT-rzUD6QTbAPXxaS?E`)jY(_|)01X0904G3S1WTO>P5>{0eg<9yUW$;M0{sds^&4;scr!E&ycwJU)xa6xlL*O|p=ZID!S|s*fu+`h?}MG3SbqV_kn9Y#f@Mgi2?oA|e?J4h1TKOe0T+SyAtZkf%>#cA-j0xb5PAxH5PTR~0p15Kf>!9RTY<Wy*6Zr5M_;6Rqfg#AAKUxr=j7<SAI8QH=VSX=NtR>T7H4Jq*h;<(ZP4A92HZEPWxD%VhI=dZ7+C5q-F@GMc_DSZZk|X^fi4%0c_n!%bg^*ENy&?#9|_02m298ek|#jt3CFsSY=)}Bv5q9a37sz-YfbV*XcAcJT;W)!lI?3*@_6VR;n)Wx4~8a!r4AB~Jw$SMsK0RRIg;)BlH?B1j>55bNp1^m2bStB9Q&SRFQ}(*?3t47`>JGTXd~g+dnLO--M~^?2*(~S*}l(9_Jy_)j%R`7C!n2#<Jlp(E3}7jJZmJs1f30*x<ELdS(5F~GRcw9g~IV1l>8d>L$K6n;dq8h?hl<L9M4(F_Ghu=S<p{}<2f#Q33QooJohE9gsv8jbAsfx&<(<ImXQ1{bPrhS0pU24NZtm`7LId^Wc%4h@_uN(aGZ-Imq0HF$2m%J9aNr`>!2;19A_}ecc9Ik9OpF2_OqPiTToB149UMkJ-{9~gG!bm`6kpIEJN}Q!6ErqXcKS~oX3AfNInNG1)l>K*kT7X3t9@6S`N+v{|GGv{|HWp=7Q6~-yw2wogLr;=xJ~P_?&Q@`|WjB>H1QIe&2*vL#x2m;0MrqV5#z~{{ZR(mLd61s4v(T=lVYpl53z>!S*wK4fJ<#4fqQ5Cio`my8?Xxet>I84!6ZCwunPWo&p^Po&t_VNS=(4JQN{01R+^LNDhU*0uBX-LBqi>K!-!a!QrTHI70GNTfA<IX|{-fP6bDRM?>Slap=!zgyd1sSnw$DNQC4O(8=Ht;8zinW1vI9G2oXGk_SRVzyrbdJR!RLA-H}B#?fAnf*KW!qrK)(^eGf$H(EEQ_Wr(ru~}h@uWgYG-2_es{~ICs2k24oh+$67J}&>$e=TtQsPtt*{~rzh{+q_vsrug>Y|HiN<?4uGjpVb=_8@eo!*Zm28j1e^p<B~B'

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
