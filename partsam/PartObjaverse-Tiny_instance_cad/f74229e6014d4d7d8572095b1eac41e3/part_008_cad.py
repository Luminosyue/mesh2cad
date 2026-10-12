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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f74229e6014d4d7d8572095b1eac41e3/part_008.stl', 'relative_path': 'f74229e6014d4d7d8572095b1eac41e3/part_008.stl', 'source_sha256': '84ce9378d52ac5f65a11bc88d668a6ce37facaa9b14550d236b4db2195404a6e', 'input_faces': 518, 'input_vertices': 331, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.060518838465213776, -0.15462759137153625, -0.05639064311981201], [0.11301188915967941, -0.04760351777076721, -0.003745250403881073]]}
GEOMETRY_BASE85 = 'c$}r133L=y+J<jK*g;Sun;^{^mIR1l4@d{uK>~uxPJ)7L0<tdx4a%a(BAc=Z2?>w|0wh2P31f?jz$lvtBO-=Xn8COVFe4&N-KyvI^sO$>`OiN&r_THITi^Hft-80WtL{DN*{yI$sIdO3i~FyPKeVWt5OOOmLdBF}6DEy(dDz5;W5-W-iE^ed|CFxm@xpUG`?<svF*EFyVH01T5Z1~a)_Qo0uyA+S@Np9+O^6>mWZZ;ThDpC;{FsTu41eN?`0>Mx&vm1sBE#KL^}^k=-2czNl139ez3*qVm2DY&EA=Boyw#6wl<GTKc&F)Kd~RQ$FIu<R85l1TLN+`3-ogvknsr)q((0&qyYDTu*o^mXn_~Itw>}E|UT@_MJDu9;S)Q%Md+HV>I{D&uwprg(_&dG*>DLpTeD9Bkt@yhSbw7JavZMdiv{h2`Te)_beq#OYTKj(s*`*zC&Z1;T|KvQYPNQmC9g%rD(b2zHV4b(&Eq7_>q4VHmCtqZpv+7@qw*07Y?R>`Ncip9(pB}NvPQEwgj#cM;Kdp|hWnQ9_FHSzW&TLog46Xg1fnmu`zITadwOQ}j0?YqsQ$}Dr^XIQ}Y`-|PNo%Js{_<8QUp&~j%+#38T76&pjfqaacmGRf`+eRdt-m~1&u?||#c!Ereb4=!`uXX&Hqpr!`{K>|3DLXt;~H}>$<ZIR$vQvvuIR^GXu(z|-|KmEx%oX;?r6s)TpuSn`t8fCG4lo&+8y}4o{;P$CtpO@G2_L6(z~^OEFZho$rt7Cn(fK&?Y8_`LsGQ<?b=fFMgO6Rj{dR}=6Q2>c}8oGH>1>6NB@VZ@0sWGa0k=(oIUo5S!duNv%a_K<lWkNt8**G$rnFPU1*+<+tYSy{hoR?#nHdA*ovPxb9dl*_H@tL;^cdGR9RuR^XGZ`@uqi6a`L?e_s#R~D_E!>Z?Cj1j{c^$W_|aVW!ic0WW<>D^Aj?(<MqW(PjT`^=V#wG{jW~z{eH7?ijyxc^?%3w-qJTr-+OQ5uE2g*zWsXleRfYj4{w*<;^cc9PhM%(DRN&Qw+k<BbMnQgjK$V<|A*EdaW^#4$@jiAYJH&Zzg}$d{`M0eH=%K+=0{B2=H!bry_T4D#<t4T+Szo-Hb;MN;u34TM`s4M(-WVy*~u4kBR&Z9{o~LU?{5$B`4whlYUAPEwP{Yi=yS+x)_ebr%)s&QDZ3)g$rqjT&G>{;A7*O(`1{(ePQK_dz`BneOVEzX+cz@V(SI*;b)fG*|F(F)PrR?#HvPB`K9=U_FaK_y+0KKXWNPF8+k>f2zNi%WmZ?u))%)>bzf?zm@xJ-yd3(7`mew!n-={eG-=>=PnYjGWEUnI-!zqsbfx?T-eymtOOB*Mb=4^5Dy>nNs2=x8mYm4`vPZi&OXqMKGMK5i0^j}Lhug8Rlq^!X6?5X@sx|1(Fi>8|X_AOa~<H}q0M7onNYW&TNj~jYOtK&QANq6$a(q?a%?HqVYKR>fqY<2WIj$0n+`_GRp-tQCd8E`gB8$YjKO>^?ayofnc-Cy0(`*H1*G)KRBkGbaeE-JAn@Oyn-e@u1q#gK__n*M@E_5{}PoH>>1<cn74%y{?hc6+pbJbcX@hxt+Mb${1MYaI4nzDGN6+~0!ytn?*;zQ3Kec)w4)Z~FB;+W9=Qe!J$Y-}gW9#n=h2o5z*&!=AwL<2(1>b|+u-$uQ$RlkVvC%iK?Q^2O$XQ_S%>{-M@R&#rapPQG||=5+IWZ<X4s^-KTS=}x|AU1yfLe_N%!f#=76AGY}-_N;jyj;m8eufw<s@)=hN8=CJ8>|gJU;i*o(SijV~kNJ8G-mCR*@eA7=ef7JH?{B9q-tQCdiD|Y^>le@0+a3KXJ;nw4{_mY$G{w>15~9~v_qQ2;O>^??b^QLH)DbQ2%+Y++@2$Vz?&z;So9^g8y<w{6tMO*9qwcGBTRZxq@5o7x{=kf}ny=n#J{z3w<a_7uNOSVVlo4J>|8mEfny<#s$PZE-{VRvf-_y9;rL&#JRglj(QNDd#1^L8#w?<_<jdQ!N#<{mjY_`*N6y&S>^ZH)e_p0mE?)$IPHE~)Ubsw<%{`<h`(b<9HMBQiXzPisO9G{#W*zf8-X7|;7%zN~$?7-_w-6!q7x=-d8U!d3LK5X~>_u={%^nT?2ALMiYSHAuCBFI<27d`6k*ZPs)sUV-<HIX-PzjprleYE@P_tE#;(EWkmtA2m&zWV)*+c`(Cqwd3YpYanHwq}1|KdR>kyRV)f#PzlNwe!aFNs!O;iSq5wGeJJ_3Hd4e1N%`uU)g>C^VQdf_Xmy>_55b{)$?1z6GyZ<{^vuRubvO%9u&{f`jO|)AfM+?Q9mX}I}beH+I{tWt9<+Ou-#Yj2}57Z(fX0+^B|w+bCEwtug~*;kk9kK`_YAZ9o{d3eBLkeKTXNe#t-i=c3-`}xT8PK(atmPM?pUCNBPr^>F162uOOfIFXh|c*MfZF6Ph2_`qBUXX!HH=kJ}4!0>_oQ-`aikekvOLq8*od|F!$-{nve_@qxhOQt#JxU%g)|-~K*s_k-eX^8-OX^8*PdTWNLF{Da+B^AGuL#_8>3e#7po`3>dU=R@p%P`qt^#_s!ne`k$9p!Fm3KXzZu|HMssOK+!|-^RDkFC}EGJ)n($=CAC&fBtH7-T`eqFh6GZ{qtihuWHAo=H-HX=H<N4-_Vbjc|W_a=KT^*{G^W`<`wO}npccl`p*N}IA`86$Y<WtSLUvETxwp_?yGrGaW6bqJ1*v9gM8*=ea)kCwc};JH^^tc*VnMS=KJUWZw$`W`cch4+k7?u9Cvku)*dy#ZTHpuws+H%Ty2~)e;(vBf9~u1cCI!~)cm~7_s`FF%GJ*g^Z#~Vts~fdwT=)}hxG#Qq0e&z`&X@B*nPErk?%UH9hX`kvHNO$B*FKEe!Q%|*nR){%fYjHJJtMu_BFk}TJMYcRqIFp`jO37>qlb5qj}nSV|~i*tMw`GP<NizPS(HdzFPl^8`LPzsr_*mA}!yx?j|1Zo~MmN*7bsX*7Xv)49^Sf7qxB}<g;$*>oi)c<DWlQzHJ>d$Y&i>xMu6;fpt>5uhvPu2bSx{%X+J5_MslH=J~H5(b})ph3&pt7tT-qLT?Z8c3-VKd;8zi>!@+nw;;GZJ+)Q*fu+tz9jPdU+)9X0F+4tC316D>PpR_~{>Uc(rzQNRkuCn$CH$hYON4BwrA6SD#)me>_AJ^F_Q;`TY)#SPaBE}VZ-&-Ke}elPI?dQ7p$p)RvI~suU348Rb7bxl=p}d(xl7RX@Vn$rMCZdYN9Nw4#@Fx?ayOxg@I-R^p;O^I<bI2O4sRm&Q*;m9kK7jMX!u)lKS8tLPszQ29)VksTLT>ge?sm?Gy%Rq?p^dOT!Y-QXm9u~G38yBUWUsO6M}Yw<vtnH0R0&bA;yJvfaN|J(+0f<yND@*c8BFY8PgFh#F#5WOgXd<EceNnE@%n395FS~!EhI1I-oANCNVA1F>nWBTBCAIOD;isL(y`u95V~)bE(r|IcCn$=TeWta?B*t=Ti5<Q^_5Tz6O6zZWg*1-b3yY^cXyv+(GCNIE&l_GzmUJ?pgG2@E~$~qc6Z`iMfnkg?kgz4Sf#2Ow7;duW&bFI-nilpNYAL-iJF7(;e*r-y=qj1*sv7i|)kqL0^RBz7WQO)RJ%?Vg{pea0y~uXkmCTF=NoNu!|TuZlwM$EFMG5G;{_m_sN)_&|lzb#4JD;!3p%;I&=g46S<erEARqx*P|c8>&TstE`%?U`!#wFZpkt9N2kH7$lr`6!E>m&3f%y|Dy;E62VDrq3TwQ+icW`H32XetqOZaAg*DDvp+jJ|u*Oq;^aZ$zu*QuWeGab9_^5(*gc~pps-r#NX!^SW`XbzuevL-s;1Tp+PjoEor9VcXGvL+qkr!PAZxPo0Vm109oF}a7e+!xnpA^>hoQLj%ZwTwUJ&7KJ<qi5O`>(Q3a;VF?4h4D@uF3Tliv9{ma9!0z<vz)gTt5+L2prD!5{Z_CYjEv^qlJlm++~gL8tCuvLt%|qxnJrp@DIWo!w=Cb@CjkvPk%tq!MVb^Kb}C3!g5R}u|J7@lAkuV+Q!xxtqNB$zPqlmJ%(0?+Zg*I$crFHa#dqrW0#fJm>kKSjeYXDvke*nKWXd>b6I&|<VYT9?0a5VdC!w0`B7t^+hygs$&ozX*f&a8d85dYT-Igf6mwbZ=JT7zzInpRn@5i14~%V%vF%1P;C~w1AHu5h2X!T{HTZpD)q9^>lHW46xzw9WEy>>-+coN4qo(9cW7{dLdON8ld7QD0q~1tsN&c&`eM!A9sU>;8u^ph^0cuGeU~Ijp*Na+`vyCl>dO6gR{DrX{r`~aDN$zB9&rt6fY7O8VWl%4JT9WgP?K<_YQ%iDdV+*HVIJG3-Hns=kJs?MNq_Nc^uNFCyi_2#wmz5{=0X5{<tx8^1awPAdeJjv4@CtYqIv1V=4?{=7!{9DxFSrXFg+2pE!FAAZxDH$qtp!(vpFpd^Pr#MX+HfT}42^)p;3jBWxCz`9eID)#4@XDA!{OQJJa{&|5`7<D3GYI8!n@$Vpa<Z;z^BpU@M-w(=ymw-a8Z|~58$GVfy$^H6P4K{*F&qr_28yxUAQUS0&NVpfSaIUa1*!=>W1sUmC&+qCAbJG?*m2nEcvFe^cs8<K81b>pMnpfIq*Sv2buxPepyDpNu2`AaXwjC*MZcfu>9U1X`9qCv{CkBI`z`2C0Sk<@zjf_)-2lj4fVdE=1uzj5aZ$ywIs{yD2945)EdTdeN4TNsdb8Ra-MqUsU=xncXg>(ms(vo7irW>qt-#jRRQ%1s3lomr{$?vo?20ixkp@9p40+r$m_Qxc_qoI!?>)?IIT^t<YMH=>$?~^^0OSD%^APV$&oCt_fo`{B1f_ux9u3$?Z}ZV?*kQtl~;ir$?X~Ia$L73M}C&~hkC-wt4EGxInHB<k0D30yl=D<R$e=DBsb&Qkk>&oa^z=uKN%{lyrJYsme)ls;%kv3c{XEpI64$w!C2jarooSKJr_sI!KuW&gD!>NfnP@_!>_|Hq4Drba5FRpZU#Sv)`g#fOQYrC(r_WPBwPp<Xfg5MKgosBQgC6o3|av$16M=q!PVgAXgjz$+!q}R_k|~*Q{V~kVssh27~YPi!`tD*=ppzpd=WhlUxfdS7Qp|8D{{@r>!>1|<VI+1xDo6@o5LQsGujUB40lD_!(HJ{Xbjv5Zi_a9+rkaeT5v<S0$K*H0RKx^D({p3Vw3zG`VIUY{2BT&{282zromogdqY_7TvFeI<vZ<iVZFmjoe9f#j8ZP^okHqAgvG1L-GZjTbI5%aeHoTHGWP`f6}*MqJk$rvyjXH2Kg;J6<mRFu!FlAKM9;vn<hDW^!nx#bMz_Hy$-RNzf?JVWAFT|_{qjBX23*=@eXdW88+{a(`(#WgS`Bs+Qw4nl4ke~08U<G&raJl<T$7jxG#ai>Oat^uID(i+^clDTG0|uvIFgufv=tmpOi#2u98OFP^l7*!F(c4d;2Oj{jy?sCAjXTn0dJ=7R-wybIX5Kd78229_-$ggqTAq}-CTu23;)@_GXD3^EBjab$3}amzI+mxdDy7sUrg!Qt%zK^FmCjP%paMfa>iWz2R#(A=l'

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
