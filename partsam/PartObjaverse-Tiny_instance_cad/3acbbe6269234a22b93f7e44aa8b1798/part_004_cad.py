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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3acbbe6269234a22b93f7e44aa8b1798/part_004.stl', 'relative_path': '3acbbe6269234a22b93f7e44aa8b1798/part_004.stl', 'source_sha256': 'ebd85ce9e8ee1a0fe35a850261e0db6f78d5d81cb9ffa9df06a7b66b748dd778', 'input_faces': 348, 'input_vertices': 225, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08450750261545181, -0.21254092454910278, -0.482612669467926], [0.07691562920808792, 0.0363997220993042, 0.2642746567726135]]}
GEOMETRY_BASE85 = 'c$}r03v^9a8pls4LQ|nq@obM)g@{)kl19l%JllBO(j=njjYtq0X}l*X2bJqlR5e5sToDn}D~UICq$F-aOSM9k-eJ+E6jP=;9W`_I{{H9Y?7KQ^&6<hzt^Y6o?E9T>e|w+DJ&Pr}?o&Pz{j`&oZ0_vLc}|j8cu79e%%t?`lM<7rbxlp1;~_QSKKn6r_0X6hmUs_orj+3~K51HFx?i~L_iA#OUx4hFJT-lKdP3^kQ`5&MF@He9lxa!2KW$<{T9W>I$H2gl06C~rfc&2PKmIh*ORx{h-*=qV^3$N~2wjwjk!QFL|AhS3zj0r6O#XtYHYtnz2A*rU|3YpRQ~7Zt^2exo=JAsEKTCx?*=xBkx4lPx*B`kr)%k!Q*V*lR^7kFvV6I0CzC!-J<>ZGoraXNvkpHfY*CY4O;PohjE6BgHeuKGA`#W37KQ)o+=@)j5{qD@jEfwaq?D19hyIeZ8RG1g)*Dene>Q}3GpAq~}d!D%-=MR0!_g<aP$3@1{eD6e%e|jg?`E)SPZ#R65SD)0c<od5}LVsL+i+otZ{o>iQj+mD=;6C}=;`qFjPwvsYEI*c*`y-vIBLDrP<X4ZRJcqyLzPe^liMbwmN+3V3T2Mg#<9wP|@MQ=8+|dt9%yk<5QLj%SKP`>-NBjH?9ryQ<LVk7EHSTNE|5nWXt6rOU-gWoM-+zew`;YBBkJn1>Tff*+Y|bMM8bjlow%W~9nL448`jO20BiDJfi)&CC_f^X*?o0o=$9?Nl4QTv3Q@L-wcZU1+ktfN&9?N~@&MEGz4H|P_d#G~X{#`!#ZO+p8l!=t*a18l*J009_oKEYtJ&^m(YsKWRSxEI{I(G8o{93<?e=d9g<(ayZ`|@FL^2_2V&*+8Z*Zf}2KOfhJ`|5~P@*PnXW?va%6~-%H2GDsiU^w@!o{<%1U+Wu9_3V#x2>l7|#(ih6Y&!0tD9Rt)k^IoNX#6+xX<l7hQU2XIJii(mLC5uPM)hQ@=6N(rcj{-mC!g|hch?B@SZn5S-)if^`=I%}LdU%|oBPU$8X>>oTboCg(>lCP^;}J){7ZwY{>-<Zzsd7xySq?57h}kei6}Q8SK8}AdA@7wFz+{e!Ob0JU+X@b>R*t<eI=;JY4f^Ba~5*nzPAhawY#0E{^WS>OY^+S&FijOI#T{WJj>1d#2)@=JJ<5gRpx$LdtB$f<_N4Zub1SVP5x`mXg^;WM8~Z&hx^v5=5)R!jv~L}!8V>h>@2TS-T#ozYxr{in$zYwWw-Ih{&D#;9-T6uFVe|7+}B>nrasK<O@7%;%0IRp_4(kaOZ@LA$X7Py&~a^VUgmiZS99NbbtU<Ysh@_geVi%Oue$k0o$7&e+?VR#rh5ESs1JL~sGf%psD4}@>>F|@PwO@gA-|jN$`9W;tBQ^rnnmlCyNc#jFTBFsf9a!48ozd-FkV_YgZ#4K3iCQTm!%?qqbl=xq%Mf3d1W-M68B+0n%CN<4s(8aW^by$G+5}H<mMamvd2Cu;=dn>66&-^mKO<mCiVE1*QbzgTsMsT8hm+HywEqN-wN(4_XY}eYVB>5C+aymFL0gL+Ns>P-?~w0?t`;UI@M!YP3P(DUDf<^Ehba`iAA*T33KVb17GS?Q)%v-vvDl<RjCPG4{;rE){86>_7C!C@a1bBLO<<pzH7d}G^aW{JSX&1yW>gu?;j#RVm9S*^VO`Dw6C0ZwsQZO$zna{99zwG8hH#~ZD|wpyNx&U+ug<+zI39H`--P3tgllOeb@duu!{T6Cn>`ET6bk`HJ?XD{R(_#S)s7LQc)`9@!C$;G29olO;)Niq@3zJQcdSY?r_R~t3dFToM`Ub+YF=YKkobLl8)4e{6^HDwp;jqma^JWJr_J3=DxZ7!IOl3Iv0uKjlQ{jj5mA@zMLCfZtj~k(~HI%_d)bofv;-U#Cf@mH}WVmpA_=r&y5!Li3H!;Rua$aDK+F9*IVS5M;+(B`qOB-zu<l<#T_gZ_HEQW>O-vPyRHLnz9QeC<65?JU!GzW*4L@nXnfRlp&n;wI@M$EAnYGCcruNzlP>Hxwa0kwD`yr9`_}5_yZR5`Id-*hTx-`cls_Vm)(g*jO2=V^f3{CtzS};L-NqaHL3SJOIv<}8r*%1&L&r6qKU)V;-%feby5M<3ZT38kUsp)|X?31o50z)hcP?rqT=!)7uIB-x&rdg@@ijZd^Xu`QEqr|4SYcnuzh2|MDmM`CYY(cq@2q}6_ch#q?KNfGmwkT`_POfjyY92_?b&x}yzv}$qm=xtOzJ0|6Rhx+J06q=&#~64h1_?)P8z=Zby9H~Z>)>rHr{o<U(6wY;9TlIo`19ptEdm#9t-EYdUhd=UpImJgXc_pWhVL0HW2o?e0m1u>C}df`v+aGl#{94x300$d~yF$PE6P$oTtV<bn{);rNi;m&)-H1=aEv>O_;B%9{9$2=X$PyuSBMa&r8|$XnhYj#QWEx>jm8J?l0aSr))2v<F^p*r`n{=+*f~SF5Z8W^Mvt6|K(9C_nm3c4)Z>A#?Ilsb$mDRIb=jS_qE_R9p?QeMMP45e4kRAtm4nH&d?z4+f#ar&p&Rys}CUo<X0xq_0ZSC*HP{9GWVs|#);SG7C&$1f4AKge8v0HX7l;zdY*@GJsBtTP4YTVdA1gcc^++~@yDvEo`e<rIb3;=L;08fUCi(1yXJK(ll#W~*Y!MbV}{_nuEW{o`TXyf3WV=j^2&qUcYW_R-UFni(|BA5T+h8fM{nZe{m%;DTeX^g<lp^9d_GC^wexlBbA{@`^SPG$`bIu3|15tWB0Fo&F}218a$ntdQ+N+xx3u3#bzc$Q1IW+Z-oSr1-fy%%$n(fjw><8rT^8><|B&;{^&8J8&J&62xEk*n&<E{E4EK%eyz!i@oDN*e|6VqY#^Za9RMwvR>d_?f@qNvnVqL?3f2$ScF}{b6>BoKLqPMXBo!f5Hdnn`m66R$Oi{2Pv>YIYTX-~Eko5vgPd1U|i60>i-M^erdkdOCNN(jBDl0VxcjJLD*S{C80?t=yy{^y!V5{rhCkCdEXdZo)u_G9RuztWu){9nD&4GIqXe_!cV={0<z#{mT6gHQ+fFtift05d%Ut^}Wjo(G==pM!o4J_o)4y$HSl{szIg8hQ!L^jk2~%itJ2BK3$sFb+a6_Cqj!5yAKcL?mB63dS!Z7<WN1eg(m}AA<2F1miUb#)}Y)rz03!p)uebJ(lPZ1)TwAnh0hZ3udZ-nf3&SL%SgucR(<H3Bg!KFm8`v+!5Ln><0~k_5}CDv5h_}=)HpajJ1fxJY&FCXd*Zf^RyynpieW<3!`sK(90$0m(klCQ_piuYr%LcGzz>GJjB$mAy`MIuRz1W;pn5W?u@%YJ4m&AgYnDIm!#VL!?+z(mTLDHV`J|zei7Op+#bDt(X<APJL~bL9z76@!w`)7AQ%rtFdmO!JQu+@8^O2;!T3`IV>^QJ>j=iLA{d7v7zZL42S7W6d+8CZ$8czOFjIdp(@tQfUBOI4z}ukt2*w{G7|%v9ejCAf0D^IEXb89uGz=O74#BaFK6gd$yP`g0EjnSIoxuT6f3QF18Gz`HK6OVgjJ^e<m%-?l(c508p7%1X1>=Fx;oyPb^`?HU$2zXZ+OCKHDKuZIU3bPs&<~~By}>veI$NsUKaA%>-<E3k7-M7aF&+vX03Lu|4>hd;<K23!)8i0=u?GDFtbspAFg^}l2|f-kMKI2Tz7Ng=FGMh&2%QC<2p)xCJOVlsJOca%f^nQ4>3WQn*n2(FIB*=ss0hZ3p|ilVP{(5EO7Kd|b1`%scrkb>bT@b@_yYvv6$r+~&_m#2@G+<cJ_as_ehw}NS3r-0E5K#YQg9h~A2biV54;h&5WEpQA36~{A3Om%3OoTE4;=xH2M>n60UiwQ4~+x&2V0<H!4~is1mkz1>EIR651{F${-<M2n5tkE>&JM59`p3Dp@*zrrxA=#K=*-9fcHZ;g7<?rK<9%ufagIcfaigeq4D5k@JQ%j@JMhpv_Ci++!tyA_XQ7wjsXt?kA}Vr9t}=2^)wB^csY7<N~+y&jLV@%rP}?;_!xArRJ)%U7ekkWmm_~MdXkK_NXDFP&}eWp=4OKq0}sO-Y|u1t8jfMZTG&kMWizd*&9v?|%;^;PD8h!?ZOF-ZryiU2*o9!c1-c5n1-u&i7w~FuCUgoo6Pya21WpB~;8=w?{!VZK^kZ-V_#^0h;E%u=(5c`I@H@~Ha0-sgc!3^s^w@#OHF-=YgPFdCVEh_%9C#2k2|5luO^*cpeUQo9uE!BQ*5dbN7?%KEi&$nF%d`Z{^rRl2LH9sQz&r4_T<9J!%a?^*+rcG>ER5R&&P8OQ7Yo3X5m}h$IB*go3v<fC@fcs#<C-4NLtBGe=;5o!_Xx&LJ+45%g8G8L!{5Gyeg$r$M>FJQ+6c`47u3^ww1WD8eek;{v<|pAKHnDF2F#AnzJ5Q8VC<!bw;m1fcVBQ5XkBn!jAdL8pMMJK1#XI5zNnei*bu?Ev8nFHsJ9_%ZV1m4>I1HeI_g8c!QS{xeMCd#`x5<ZsmC+WdWe>$xwk}}Eiv8~b6|7vfYt?jfF)>saD5z;{aB(s>iE?CPyfZO_D5yOg#Ym7{z>sQiuscl^<1u(DwgPaypB5hKX!BYEBp2({TpA;eKG'

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
