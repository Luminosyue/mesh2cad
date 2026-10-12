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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f121301624174b179ca4d50158797b03/part_004.stl', 'relative_path': 'f121301624174b179ca4d50158797b03/part_004.stl', 'source_sha256': 'f073eb3d4e21c4e0c73a2bacbe63402b2b51120681d4c1b8f95b6a2c7a58062f', 'input_faces': 360, 'input_vertices': 285, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.14429929852485657, -0.20407764613628387, -0.2867724895477295], [0.12711471319198608, -0.003743201494216919, 0.43791869282722473]]}
GEOMETRY_BASE85 = 'c$}r033LtT-^V8*_AL>rt?EUKs?-`4>sTrxqFR(#Z;IF>iHO*0YF}ziY_Z)CYwX0X8EZAQ@4Jhll%iBo<v-8&_l@3r|9#JS&-*&(cfOzd$#Z9(d1mIBxieaXX3Orc$-k1?@6*Pftnsd<smiDMYw_J;<9c@K*8h{J=s{juA$avKD-)Zy4r>warNwJQ%69G6ze{Y{nzpjFBWskcU@IHhFE%bVBC2!0*sk4_ZyeF5e>cnb?-3E*&H7xfN{zq@wyGahunn{QAOGdCx}ZlU?8&gwQDM$Ol}4i9$_y8;zj*uue9E;IDz$)t;_G*Z*YY(;!{4{Z!8`jE`w_nPPIrH<9NOy#SFToR7Knj2j_YV|EUdG}&DZ=w*88f+I(%<l6uiBsH`+S`TEaWO?h9`YJBIdVhx_o3kNQYI*A2jS>0Pp|$M+M;?L@mKCGdCcQbJliwVngdcHr~baeI-U#IJPqPVX`Bx^2@cS8s;4lJ>bfFL(8N^=9y9#l34>y>a=WjQ5ATm%6R@tDmJmapl&zddJ(ceU8WHm$<F>yH2v*6Q;Sfx6Qx28|z<m#I3z!`4RDjC%UzFo@@i}Oq}o5AH7+qv=1rf*4}vhz=XeB!F_wL+=h3qneMi|wz8YWx3B3op5~Vu;kA2%FrKz06Q%v+?J{oNf7syaHNR9jE-pGYy0y0tl78+;a`#_#m*p=>#d1t%4cXpWa@;!KyLec6=kE0FXkXgIaiRt7IHbJ8rxUz(>*!Lf_qRvM7)M*U_(R#2AP>}?ha7xo8~R~iybtXo60v+^*$sFtD!_ri*NYpeynW9V@hkV>`{vXO2K=*A;@5^P$8xItJqLe3vse7k1&gtq0bS>#-^uO72c@Op_}<cSG}fCCB0kqMeBbC=Vi=Ym`!T%P`ZD^d&(4MIHFw_IiuRQvaDLgtrvIe8*5;!4_ddXS&1QdMz519=;+ti|@@-XL492*H{ILZ-b^l@+pAFK_Je%RoTW7Fe?7L@Rd>p-3z}pKXV*Kr8`(U2Q^4g{Q*kAU*S~CAUUn;(Igv>uFb1`3O{)^xpU-+T_=Bpwy|D-I0H@26O_8qfh{;}^&hSxXNl=-LFJa}iwZ1KfIrTxGOYtjDf4C#N<moiU2cnxoMO_b$#&XoD5Ofu#l`|nfXozwcEy&14h=B4EE(*KAPDYE}hjlyv|C_#L?#yHNLVflt)KbDLUKepg9tfxo!x%iyfQ+(fsI1Y_^n{XUCpEZ*8epYQi`qBABCieT@r<>8fP+uH}M%eff*zdg`h`(1~_G{g%!_j{C8F;;~>@R0bUK}U7*9q~)b~#QeoRQ^^*e3qVSJM8|GSWV}Ogh##Wfb~j3oRn;lkRT9xOD7=^T}w^^azeOL%bG4A0u9`c}4vA{JZ6NKaJ%WRS$`Ou?_9bzTKq#&l&KxI)P|!vpqz6&ATJK{YI`#^s{6Xykq9ojp)Dr0_TVARwnxIEVXB&j8_PjuMfEiujSpg0qgszmCQd2ieWjny6Ny*|4Z0jXVo=7qCdaA3$OPHkohbm^>~Jh*Crj4?fv?NyDt|$9G@%SIO^tWOdN#V5PS^%XnqveH)Hw7SdPP<jPuu-lrDalKepSEzV9f;|EKlhhYpeXY+^dv>!w5elYO$?+g6~xMz1Xwub&aGKWhrF*G`amJ*AWMpI+NF8q0U))=#+k9{ES0{q;6S-F&4hao9iMlVrQrRFv!Xr|)BbIckQ>es4Vp=aV+CHu|Iaw!?lmBfE%yeh=ehYhMrE7~Wj&7t+(QzwG(fW4|~$R~8>8*G<#s5WErp0Oz+hKMC7quha<JmF4vgJ!Ra6v^(MIwLTBAU0VB6N8Nn6V*Szo%w^av<NK!Y&Yrao;P1&xr9Y1v!yAQH$nwiLvAz1sCaeE-JhQyVxY;YrS%u}?uP*y>SRm$Gvt&Pbt?_L+jyAs|{?{_%kA~vBc7#lmajsNcyw6;uqrkOeIDR%i!u+aDet~pMJ_)ZcdMLhtcw?$~ZD?xRza9Ts{=bg%4k?(|?cWB<b-(`#jE`A%xZIx>93uBMYvSd+zR*>!10_4k{Zi~c*^kQ`!JBEB(mq<Y%T{6>t|$8Au^4~bq!8I&zbbN_sUL*z+1{^({yT5x5I-<ka&&-fZ-ZR8PHV$jW1O8wy2$+SVQI|E&OtlSAKU#<*^j4hrlLRZ-VlE}Qu?2BBfQ>YEACJAs2=d<i@ESxi^Ev2eQyNLJM;BGc;j-;U9ulXO8Z{1(!R_m(%vUn&fnSX#UBfj>-e3bC(u53CGoqG7rA=dFBQcP6|WU}3tq1~Sgz{@$IATL#aHI}RiDEf3qOT7COpM_Vgx_K^+wCq6lrseIxgqkVet=JF2sHrEnX|~2%ojT9>_Sioq_Y$xx^pd7*+Lqj8B|~<(pmSEx_kVBjL5ccV)fWkGM{nAOD5xk0bOMysh~Fc%x(*yxHNh_*K_u<NFtWLfXzuKZ)gpPZ7U)(k!(1ON7_EekVTqJ9zCj+jj{T@An@1>pYYl+hw2jP}&W>itDWQr+CNpzh~leVqctJwiR`-y^gy}#9usu^TT<*6uj-%`qSY{T$bzq)4>>jd#n4?Fb+p1$@SmMF2`YX0K8Vd7{2HH>@Dg4jk8nXJ6%BPU(+vGJqiA+AoSm?zE+O&%CpA7M{JgP>vdu2&#Sv*;SUy-c`NU8%qQB@Ju(lD$dL8itZ^ECm%sR(-cww?F~wJWJ}-FPD@fX}doTokc10}5Rx1_9p*AsbFnl#9`fCQz7cY|lfA|v|xAvE@=)W=RKs<cxRNQyz*Tie)`+d>x(nT>J8b1$|`;a_Qz0f}D0Iol_kdES;)e45!KOBkUYWbN{@LL0e;QbdFSpG`-1zWo!+e-h9nqNvkpDc_<>iaQIm_|$KXW-Kq_|P(PUpGd)cI{CdvUY83uWk3UGx+>6G#;66&jjq3J@hS_i+_?a!L_|{^&x(LXyaxLL;u^xNI&;3z<sDTdp5?;QCqxmZR8mE645hcoc+*$Bfi2|c%yO>d@K6c?c)D9B=d0|j{nLY<KV9cxckk$#UHF7{<j$M4+AH|+v}h|He<bPSN-nOkyS?Ecy^T9eNMJ_yZ9G6j(3MIeIk9KM$=r|o8jvd;g7Y&I5?-2#`fyPe@%k#<tO*UU2fq#)vGs}0q=cM?!W2HqfL@!`75I^4u{%FKX<L4i!A&c^P>IfeOXRHpLy_J?cDuf`cZ9Ve*Ig#Hlm97W6j2+edtv=PmKxUiys|>^>(56-6Fo&Ie2HA8Q5N9Yu@>?oX(@rzJqve%uMmk<#(*JiE#nTIe$ld1x@D5(c-lyzltyaN`4QA)3-NLkTa^_ytAE7xTrqcXQYX5J6+DZW8!Uh=tm`{xV4}4v-n&&a6hBnFNE>b!`Ci?FFGE_n=yU~w%2@e7T)u|BFlT;R~RW5#V3R%qJ5ey$EaK`ReUPuA;*F+IZlF`ieH+6<KJ1QpKR}qmg1w!$@%V(_Il+w@gs(zpZ0pv-f#{Q?{WY3#(UoP#?Qg?8|}zV%)>UHB<bhGed0?jk?Y=D;x(WB;#V$P;M!jMvp$~dXsrUUUCzx1F|V5KY|G$1?r*ca=l$)Q_8#}QZ@kC-tvP5ko)2l&Lgje4l;aXUcUUVvuRO2F@@CHU;!CY^^ICA}6>|J6#Cq+SIpw%LeE{C`cSn}@9OpOQ<9Ej!?=k*Hlg4;nr6oPWapI_4UH1E_e&VCjG5^@=h&L9^5&t45<{779$aSrC@3enAKC`^%@4h$Q^SI6O9>4qa=wDXJe%Xil%8}X<>(yTsUJc)549;u)8hvYj@ry>wbEk9SjrW7akNObT7h~Fvv)C_f`-@+`7}pVFf_Nj+cP;$qA=tmV&0F@@liK3ztW0tB`WJQ9y6$(aIQ{5m;=jp@^F@n!avsaSy%EnHwPumH4>D_XmGwUPQT(`aI3JCU;+@OauZJ&Q1<#}GAEaVA`rYrvw?84z-*Oa}?MnSY{Dr5uFSD1G_FBeC@gY^w-fST4wb%5SRpj|eSuSV5OYzfl$-LcmALcPfQ(ruH)Q0zz`|2d|_TBV_#oK3!H+PoD^Gna?MfQpT@Se||vb^VWC&RxAyyx>PZEQ919?!dMeS%~;9?!>&E4AP~pQkzY>hPY=-)z+z!h1f)%kuyA94|Oce1Z1zyP$ntjKA|^Q+%m-%zL^nUN2v4lZ^8n`CU>tTCO9}0pc%&h;Jxfe?)IIb!%_#m>|CAI^18`dR~-yK5n7-2w%DH>L=blmA;LyTYJrUFdf<QAfC%Pcb>*PU|V)Ye1nhNynPdWL-E>W@n-N%@n`nR@3lWp$~YAGOZ>hM+`J=@K2^MSOT1Pv$i#MgyzkJP)P(nZKcatI3*Pg6im|;myyyED=i@r!J>J*YBXxMs_dAY-^~HO<57PY_Nk2W`ABBDf@A)1o%e%dYYT@?QZC3k?aJ#S76{~V<{#s;&%PTh})xWI#_g8K`tNpKDxmB%R>Hqu6t$@`B_4cn2vpBgB*^l`i*^lhcEJ0RTl<ZH=!z@Nt`3_m-+hmn*kyREUt1L`b=}T5wkgPI4S!G_b%6w#%1;_=sZF!h}WPhgm9Bow>tNO7NM=;xwBgk!;Uy$39KWBbP{+!%`*`C~j9L{xh=lY|`J(ypUdyu;_!^z=Xj^ZD!I%w5d=4tX-@>S+#@>TLJ=Fj9?<lD@f<lAH?^9tEXKF9T{ejH^UBOfK7VV)zO<98MNSe4VNK$hZ9nYqcIl7rZ$D!=DL&c>`n&PLXlm9>BVDfVJkA$yU%nbpYN<m}Aq<m}`e%o^kz<Xp@kauEBk_$_N?udOV?d`VWNxG?iCvMR;?Y_GoW<t6zx*^8Ww`7SvdIXkmBIXl^#`3~8etTBsa4G#I0CRvoMO7Y)Jf3iROthk(2A6Qj}rMM*XLvl%SDXVH)Rokk1%sS+HWS#j5Str+GRv_0R2QbT$1IQmSOOZ>l4~lbG{r}y{KQzgEWR;i5e~=%t6koUM2s4AF_%QPl`7rqa^B(yC`4mg>4d(CUSgRtf8p%u`k0ejCY9VtBGl4vX`3*CH{0+GmGm_kk+|sIGW*9S)9LYX~u@rY^DUM+&9>N?+9zveLoJO8Np6#+dvssFlGFOwAlD9B-k++aDId+*G*G&3T9CMZF%w6Pkaw>B*Ih8z<xsbe&V>;7itY<RklV_4sxqOvr%=zTS%o)u2<Qe4A%qis2<blj@$OFlpn7zoI$f3-Z<WO>bm;GIzrMNsxab1?;M$9mB825c6mg43t#od@O<VO5k1D4{ZEX5s|-N?O}1DM^&1IUAzG2}tyvCJXlvE)SN1acxdg*ls?LSDyQN?u3a!Q4XLK|aCEB%dJP)&4my@3IvC$^4!CCpj<YBsDkXWhwS!DK5xToQtXEsa(v5WL1h^uoORFUMFYGWe-@2FR&EvV=3Ol%pmU}Z?tMTb3HSItnx5<J$Wnh09j=^S!EhI>pa=YTI{l%#a!od@?7Q&@?7#H=4kRH^0&-^<ZsD+nVrae$!(aS<Tm8bnDxn@kt;IGlPi)-TlGHE#w<@(S(j`hf6P+cfZ2$A+^Wr1ZDTGWZzHc^&LXcNJDB6i4)S#7F!FTrII9LT`!k1;?aVmlFmfDu1amxj1bHfR7I`Xp0dom?0eKa3GkFzxCrj}U%;V%A$iG;X-#Qn3tSZD(oX4ssn&cy<5BXP3@-b8S$Na1~C)?&Ho0dOh)n1n3^DM>pS&FY&^%L`Z<{`35ll(n-gH_F}>S$Ffmf}9lcyb@|aONoTaPmZE5_uwdj#bN;i<n8|MdXz%#q*e>$n(gPnepVw<e|)t<e}uA%x2`C<knV&FdH(PksFemFk6wEkQ=iUf5q%W{)!yM98QiR8!W}&F(;D0BPTQGkdw(PT*h$)OYtV=2J$BIZl+1zP2SJkOICTFyq|oLrT91Iee!SQ=gep1=j7a8lIobv%~D)|nV(#M?8_`f_9f?I<{@XDOZoU&@l#Fm7xGi`9hTyg%;V&f<n7FD<n83OR<#KA^7ha6KmC{JfBqTjH;vnWkoNqh`(qu~Z^m28dh?K{MW~PZ&1d~k^v2DFuljYN{RgLE<@o'

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
