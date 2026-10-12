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

PART_NAME = 'part_018'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/13cc3ffc69964894a2bc94154aed687f/part_018.stl', 'relative_path': '13cc3ffc69964894a2bc94154aed687f/part_018.stl', 'source_sha256': 'b72ed415c48d968d8f97993fc274d3bf71cd8ce0b9268a71dc72f1071af3f0fc', 'input_faces': 297, 'input_vertices': 262, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.20732764899730682, -0.11327013373374939, -0.38182857632637024], [0.19131720066070557, 0.1700112372636795, 0.4999998211860657]]}
GEOMETRY_BASE85 = 'c$}r02UHbT8pj6#W0wfFsOuPGi>7IeDMrR5>Kd#uCYBf<ASxCR5NwH#v1}9#LF^HEDyUQ`0xAlF2r3ptR0KsH%?g^e1;n!Ne&3(uy|?Z;dv-bJJOAJO-<@y1x%bY@ozYQF);10j|8<gb#%7h-wUs0hO(X}&&&_+TyQ`be+a7ZkSV?x|i@!Pz8ZmbGsPR^kpR}mk6gMAN?`|K<-TF`cuv;&=+f+~Qx!%qmlRdqsxCwu-^DG}Xqwh1_d5)WLyL;~sdiRq1^ynr3DF2Utjf^Gel2&D>iCW|_a~#F?xgHltlUA_*VV<AZma~J-3)K=Qu^&5OrcgP*{GyqkHFTxeHXO}8NB;hf>|br@FSeEWea}+<{SDb~);d6_;Y!PV+ApE(B>9!@0b*O7S(8oe6EfM)bP5rw6*s+1?c;Z_fBMZR+CKGK9_5P<AzwXPO1^Tg_XXN7ehatH-5E{!FMN4XZ0qAUaQg;thYM9olPJGFK8Sq%JIj)3zZ(Swv|oGx`HG`w3h9kXGhcmU-+tP!Vs!!MS<C*Q7l*n11M+q8D>zRFj~Jo4vWJ)1UqZgzHb0K`D<4GdmH0(m|Gq0*D1V7RwU^^P*)I%VP5pju2#up5&Xs)|-yrg{(`g*_abwtT>$aKd&ZwmE(#3twbxH&FP=A#V<2vIUxqWwgAIh8G=n~Zv_bK~*Y(sdw?qsw73Hz7gW9Ya=>+|V+;`*RJmr#GIw|*)Vze{mFxqVODV9M`z;|%*fxSq~F)Sv3j0o2|Q+u5u?b+`ACuf=xaJgqN9(ebW_7I6EH=HqocrqI+^TYJXwxIE(XjkV(TUKO!)KBqsVd8Nd@I6?j5)i#c=mw^}9uO(mdac2L5Bh4#0_5u5ahxXApm3UsJ`MIxz{kc^>v|Y53=YPx|@|C#<DUadm6z;beFZLa0QvHU?(N`#6jOPi{e$Xl>kT1o|<T`!3#8W-RR&-n`W*WDTiwL9qzB{O&4biS#Pg4ADnjaYtX+B8NJ=sq?zn8XsC-S&N_h3J{(H`1=Mqaj=f5e5`d;fNtevj(L{-IK8uX<#hV!t!jb6^7b(##ynqeZpm_QyVsp!&0-bLo7e9vnA4U-|CdE2e&3|44VkxF4b_xc#CH33R;E<M{p%Sw_D0LuLYBFQaK3^^rN`OSuc_{-Dh7%=fFvG|rRPo946r_%o_Ui`ZgzT;<+<I<7uq6X*AKqj6LhS>>4e(&7&LDR0qY8ee@xpxJq;_pGnde&Ito&zvHfhkBn!)St@U2U&bxOR0W!UM-Ky-U{-SRgaRW{h3vKzI%$`TP0Kb+!cI3+>=kfG|!#piR=+g<D!Lq%l_hzs7}MQhBPkvu#x0zOPeNAdoOpYM-6kzGOb^K|J+qmUv`|9V(Lp_ow%N$z=O1%cZ2FNgmz$m{Yml-XSP%Qa_GHGI_}C(>AbXQ)_kAYxqyBDU_LLm1t;nE9plMYwhuZ?+j%YMdenA|Wj|yo`MR@*xPL+lj?wR7JyI#p1%=y(<R3Gw-|)Do$kD{t-tnjVnEvrO^7SDXkD2y^?r}Q#x{!n9OY(0CwBMs(@|BRpV|>1ubiVTUn~sx)B(NV|MfFHIx2aBT`vyL){gPPv{gDsXvps<G|K4&J`(EU$+n2K6q*Vmf_3#U>Gk7HXYV<s6|DcM-MG1b7kGnbg5ape;;<%|V7wpu?KYNMCCAbIY33J*+{qt}F<(GoHk*_O=qV{S|V;W!GwwerTSJ)t(`~Lv<|JD%l<)ZEBrq`*m)r)*3a%md%%b?-(yMD_^&U3BJQOciZ!_RT}y5jES>#~#1Q@hQb**DB0U!T*A>QOh_vR`tDe8Z{sdF)$r{!1;m{z3ETxbmjRqf}>E`wYsH(IA(OyKyc1<x|Pm9qUcLwqY#!x@*<6zdHFo%~QkrcHI7YA?KOb=`3xpuS%zU#R}CUJAZtD+6NV+^Y~Wnq<l4tuF-x$x#_0!O{>{Rz8aLq?PtyA=gZ?#o^L@ZoWJY~9QPsJ=cJ%r<m-C(J3w_jNu)f6b;0B-O}f(jQL6jG|BZY@NB;z_XF2)Wx<EdzgFnqrsb(VAxo$1{j;?$kc#=WBZruX%<y$ew=zLu=_`bi+ncMF=wULff?aJpBIE33*=&62X!Cbl@>jFPw|HiwNM{)f-t!t#fE?no0DdekJ88j}+ulF?a?|hR<`wwYI<01W8!Tzla)Lt4a`><aE-@tkNiqFt_1Z0vg-+7brs9*fB!_2RoOTISk^+U8B5C>n!zGr`0rzipY$k$aa<UGT^OyKt6eB7IB_`F=&(0R$fxRI~F^BJ`_xRi0ft?hz(WaN>3*>A`Bt5W%Vr+-EDXlq)+k0)P0q&4+}y2cvy__04Iiq1=IQ=CTmt75qRIX^_1`ueJ)+<uq~-{)HSkZ%~+n%BKg9gFGsttO|L&D+}g<SPz&siyPLQ2Q47lKnFB)w{tw|7)Mqe2`ylo@zQj4NppWe%jR@F`fTvO#sg~yW%6J^H!^E%=zt7xV^sdM)vK<*EhJ4VmhCd+Ir+0tol&@NmHWd@b!|$^S?HR>egB=j^g@TQG4yNN3v-@7@qCn{EuCdP5VK4=E42*;Fl!wtK8^(wWm|amw!K+NXHHF-$44zm+QYffc@CQ8MI$*Q?4_*D8{URp3dMrYi92@8<!U^xV`_R-KO>EpJ#DBE22Xwf7KwWM}B^o>tC9=%QV0K*;>xCn4d$^b|<P+_xv;;cTvlorga*gx^ezx?vDq&?6~kP>#XxFk6Y(k*7>JzQO}>gMLlv$`<;$2@s+mib~(Q6yxM1w|8M=!F*4NgCG|*MC(=6G@_f~<KIH$~xD2@xW17Ei9MzP8iKcbdjk|m#oqdaWqSMyW`pI%$88Y0GP3x(fhg!z$WYc=;=B=F5m(~ZC^ItAHc*OA~*O8&9hJB0cQN7kQ)$F|LuHWLNybiOt-nBC4G}Aik?i*6MSDIPB;Xb4PqZdE7Z|$Y~r#34zlJ@)KeO^c0T*>#<&)f6;ty)LE<#R`0?ZWGl>uvbC;I7T$-@Q5ijW_tY@cmVOZ?5)(kLQv1Q@S5WHS_tn*KOGM7`KhiujW@iuEldxSF@FmYw?`b)oe>Q?YFw;vRbo~*HsqJajhnl>#5k8!Sm%=YpTCyKesQR%g<BS1N3|`)FiQAkwm`g(mtHqYw4!rShucFpA@ohu|CnB{LbfF+KAUh?$ujpyY>xU-<0g;b=TY`v<}fd{f5_P#b1(2UQ?pjpTO-(?YJI~@<^ViKl3`TB#L#i!(Q^AU*_#A@6z$L@4E6le*TpG!iTi3lg7PH*MnqTLwU8(3Yw?7&x`qY>sNT3LNm!%mt3cLrnm0F^T1-=E8C1_-*R1T^DX)MOE#R><uui)vzf&CqmJ<W9n(LI^4Tn4f7`(n@||kAKWvwAev9?IVjIA|#rj`oyMgDu#ruNJb_eI*VoUjz5qo$&XdA}uHy82x-{}>eFZB;{e#`fl`o}rX#(~scHzJzHxqd#c=Pcfv>U_)hCb_|AS~n<b4$?R&<0oZN`v#NYr<1Qu$Rpp-FrC*QD<{$T$-0&&XuDA@w_l!^XzCjpS<`;n`XYMI(gr*5JZ;>O{l(7oo~s|%kGA!VJFy=WPVJSizoT){H}1*4T14#?H?NaC9**Sy`CdOEoVS|{%;I^oihOPAk&}Ggjz@d*_iMGuH29s6-<9(>4dCN0bWbpCuWMGo?JeHlrRFc#_bs9C4~j=Pe{X4K&F^z_qUn2rI;NJ#qj_KUf5P)*(PsY6+Pok6l1E!=Z}@r)^{;F<lzhwY5;{9q_C3avFZq;^ui4G!JZd<f@6d979=6D3-{O0V(juSz%%AA{k2GQx-=A6(u%8uAzA~&c`LcaO8fP`Nl)gKuldWi5vTuCCG{5TXNAFXLeOt5k29JVM?6+gTAcDWweS4a|ld1L{I8SOe=O2;I_aXa^+&-ld`SSGlcwFo|v41F=zH8|w*B&?ZrIgqB``FAP^Y*E?InVHk8D{OZ-r>}b-WlA__MO>3@EPS-ruXCTGxl9LkHz;i)xI0IxA^|1+V^1J;(MKH-;;fd?|ypw_xL*V9?Rdgd`|?6aa0_}@^O#98OifJhOQgE!!-7DS9AZ5tEB#vTK>rSJ>7Wz3@+c1Hp=W@Q$`O@{$y4&<CDf14J8L@s<X*Ir3h2})#=OsDaHN$|L&hsKI-@X{!_~5#u~mb#wXAZ!JmM8L;HYxgS$h!fxCk{Ks$n)Lz_Z7f}4VyKwkql0XKuT2R8%13YEdHg6*Jx1KWWcLtB9xgI|HR0KWpZg?0hkg6lzBgX@7MsJ-;ppI|Gf1K0{|4Q&aw2HQZ}fo;I`5rW$w1iuA+6a0=b-ZjSC2*JIeZ-L)J`(DtVV4?4Udx1ZI_5%z32>b!KKlD?u(9gjA!3sj~K!o5S2*H0x2p$Ff1}xMWJPQ0BbSn5e@D!*wcnWw1^at<^un%-G*az$fT?+OC&xig5o)2CKT?SqVUIbkNUIbnMRly6uzR(}RzTi2~dEhx<H|SijP*<=U*afNsyMVukP6mGuo(P=;o(P@*9S@!W{uUv4G}H+!bSQW<_)CP~!O%fqp^o6e-~rIS-~r(Gp|6AA2X`_?1876&>)?jqM$pdSM&P#4uHZMIJ)m8|LO%xIH^wDn{1YMgvM~(CC^N=w_(Ch8WniJ#z?I+!(Cgp_;A-d%a5eY|^cMID_>nQ5LhnLvfvcc5p|`-dkn1Kwa0T=_xExvvy$-&Px=Rs)i=buTBJfqH0W9<i_zL>(Dnjr@=q2z)a4tgdDd=hNDey^XHuxks6Pg9i1Z&V^U=5rMO#>%`6QPH|iQxUv1K|DOgV1#FLGW?t3Gi`n4)h#22V4Rz2A6>ELGOU?fo-i=>sc|25Nrc|EHT@Ft)UOWLhpk`2(Cp4{sa0?u+U1d&<Ef@z%|fna1Hnw^a=PG_&M|u_&NB6^w(T}fe>8x&=qV2y$cp0_;=~A>p}1=WBkJy(~RK-^@sig><?aNj3i^k7$d_NN1$=g7_iWAa2z-Sx)U4$4uyt*L&4h-f;U08fH#2yq3giwP-h@Q@Xyd$;Ge-B#u#RdnZ_875Ihn(8$1&H71RU#75HoDEb!OhG0<t?y8a!55Ihbccq~G&J3{a(s6TiWcrA1tcr7>xA$Tiv3wSG74-El_U<~vK!8@Sg;2q$-2*J_N7;rRrA2bQP4}26M_$)&38HC_GXa=}$p5-9~pEpK<F$#^53e5+nf)7J4fDeOHpy$EokuwD$I2IZQ78(JL1@D1|g7<)TLAQf<frAl(H$yjpH-pzh1HnRn2CoPIf)Kn0>H!uy8@vX*8afla8obgN%b}jonP8#Az(PlWg-!>1f|o;AfR}><pud6xz#E_&!5hHapud5IhJm+%cS9q=yTMV=cyJUr!5E{Qtm-*f|EK@<_t&2)?ww};3D9y+^H*HcJx3UG{rSQ>%E?x|yBJ@V>d}S!NW2+J{{m*?Xs`'

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
