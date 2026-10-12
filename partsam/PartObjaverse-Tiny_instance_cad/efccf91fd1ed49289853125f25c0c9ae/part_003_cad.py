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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/efccf91fd1ed49289853125f25c0c9ae/part_003.stl', 'relative_path': 'efccf91fd1ed49289853125f25c0c9ae/part_003.stl', 'source_sha256': 'c16226019496109832ab7effee422ba6835346e53895ba9409bcbfddf5032d0a', 'input_faces': 488, 'input_vertices': 394, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0505923368036747, -0.0711604580283165, -0.45755070447921753], [0.050610098987817764, 0.2566036581993103, 0.4999998211860657]]}
GEOMETRY_BASE85 = 'c$}r133yG{+Q-)pK@2e^h#;pbLTPW!F~m8o1SK>z#heqIv{8ga4UKRN3At2Fx9Zk#w57DDDItdIq(rG%l~QgGrLC*3tFG(o?WetKt^Hry-tXDp^L)?u<$2!c|J(n)_S$Q|d+lkhla$`&%11E$?<p1?TKAt5V;K`sl|`^Ap6tn)qdhs#O_(@cV>P5N{**57JFrj65RFY?xp8AWIis`VIyvIHWW>j{bi`$3WlzpdpOBW7J;o#a?&;%lJlxNDEq$VgFE?w`v29C7o8~PYd5-_%UuE6|N5T)A4{`M_N?0W|Iq?Ihjqm7o*>C5w<mQL%eD8pyGF$)f-_P3C^X;umw*H;#SIj;u%ghq$zt{At#ee(uDA~@J?;N)CeZwL@xAVQ(=T6%B?EK~nX5SanZJAj1Pn)sL)=x|=weuY_KRsjTvo9}N>i75gZjI9>4~9?jpnRGK@3z}M>A#S@-Ogu8ub0~Sj{bL!n0?2U%b$p4_mKRfc0QXv_q3hwI+gRKrJdI{Z;^gV$~-%t_ABMne&uJ^b~<hPmGT|_=4Wlof8G6}<#?N%+Ao#^1J@QEvhi8o;zM@j-F^34+T(iu_+RAmprSH6-<9>?gq`od<hW>C{`RCRcE0yP`D?c2fB*ekOTS&S+HdFk*Iy{L^SvL=`OG#C@M#_bn*;jsC$_NkAGYnL>^JV7Z9cQ}X@1!Dv1NAc2^_q6%<g!7{zb=S{UeWmZs)6fy5m3HB-{U4jW5i8pna<JnY&kKx!ud5M{IrEAE@uhE;(uT)%EM@_sJ1E-#hY*rJg`sn-#L%vrc|$>nCNE+WG#xm1pdHcHVcvvfn}9t<$fg)7$NQb-h#H+rN65rT&Z8KbG|j-F(!}SJ!)xe=1#G@2+<DK9cz=Ek15OkF0f!^jX^?*`NHkmt3*)*@Ij1J{G9DXQMoiF<o}Z^IHA#yLNt{|LT2a-{;IOwkxlE|8Iljb>l0y;X~Q}uUgCN(?6%@wL>P~n?3lHY|rBGtMYi_(xmT?ZGJ$OSJw;i-DA!cI!(TNOTiJl^2&GTo?R^SwBYFv<aHg9E!)G=n#lGj-=C2z+v6P&skbLOb-irw=_aSl{XEFOzT|5=-*x9_nSXyBr%&d;_#gWD9#cs^Zw>#TUtW)aZpm_cS3!jIeVtb6?Tp=Y)$F_4M(O)aKKYGY)()<f<!8R5=eg^Ot7hM|q*z{8uC4cEdB=g%Yvgg?I--|fxcI8s4{WKaxBuK(Sw3*{d%eA_#>x9Wi>!7<?ypMtyE4zqI_#A7mCZQkwDDb+?tEqEv+sV8dGnn)wo=x&ELqm?jc+CEcRQP}ko#@;mb^Z_Ej-e9{W4;?Y;WYlJ@Wi^yC?6*zDJLj$@MiuZGB(8+k4Hv-#1tK?)z!7epY^_tUoY2Pxn{O(*0hkdV3z+T`G^WT2!&Q9_9NQoGUT=fuH&;F}KruvYY<A{;8q#eU+1n%;gO~X2U+S@4fWv+cICZnp^5ozN230UbF8%6TMjGE!<OV=ewixODydv8@5pHw_@RLOMBpZ8>jEL<n3^@^c_`q6j|zr&l+{yXZBsYqvy-KhD8?H`Ci9mOL?}VbAcsqC&Kjd+xF+ndTM3b`mVaO_nQ5{)?Dec(7U@V=LNni_Oa!-+?#Xf$?`RC6`Si(z9TBM#O!<5=gyJs3C}FH^Ig%iE#(92qNVSxxOBJqc$M#OJY>HmpDm}(lIN@1<05lC%J(<8YpLJSbWfh#Z@E0n@hU&ibo>EJ9vV!|HRsts=(>DPu?COclzE6)Z|l43^x13n{gG3rOTSj1J$Amo?ix#ZN9{+`Wc?LdS@NKKSCbNJ9%}88zQ4)_YaZZx8zt>C`>g7tDe|~#YS#9{SN8$Ke>^2ewx`CyVmsea|Jf3=?|SgBi87y+J(l(;-yM^0X^-pj_zAL}kam{yqI_@le9L~7@2~GEvGX0ximd0cY<#B7Tj;}GmVO1F#Xi*YSvKpOt*@@fU3bUG_JohHwg<i|`YlU)*v9ec@^~vJSn{C!K+IN49(?t_87T7~o@A-t@S`_a>i7M;?nYO!tTnXcP5CVJy5)G4@2dQ)r9Flpo=|L8e;|6R?S7f#px*wYCFg8?T7PWV0dt;%e9}&Dvs0Gy=zAx2pwlit$|v~=+*+3IH0K}f4D!|e2flG$NO^j`91m)FoHqSI`LsXyLzibdZTg||X+I3|RX?m(dxF#MdQm><|Bk5T(x=yv@`J9U<zbWL@v7?=c?j~=^$Xv)u1R@%y|XoiIa2BU1U|i=uq|OzrBCly@ag@^xAXWkxvcJos((^n^-uW5eUg-?_fN;Ju<3ID>i&%L738b?Hhkm0P09z|&x;DBAN0I{PoEd;Kv=F+`aFUk^gKFHD1G`|^OY6m$@Y-vqw?wV(R;dZmRwfPU*s*wSI>R;#&emJr_bxay(V+yvU(p-_h;&>`#F5$J%N;`?+@<#^Q3RQpP)TKzIxArZ@jmV^7MVi{mVQ#&SbnVsq)k(<&F0!Ql7qF1s>1Km-W#1H~94Z&Gp+6=^O8d>N=&qx~}0H?~SB<(EB7yDlqpe<Nir~bss1nI$y3=@4Yx*LB4wLg>SqMlk)UE*%1-DP^x+lSJxf&NqOV_oRp{U?cPX_^yznj^67VhFD6!gXB*!g>N!Y#^&Et6e2<Xw^gG4BJY<P%r}_?3&k^dA^2YZODNnzf+$$POpMIAaKKU+l{Hfm(%XwG%q`u1MdpDL!CEt(Ar{9lW{v9fp$#<yt#5~<6->trNA<JdIrQg5s>G!W|{ix;Ub{hK~`;0y=M!viK|31D_)<eG2eY-;BI8e|y0P&4+0OG50fI#&hSIPa7aR%29XXN-h9j{P+(0BzqxK{3mjE5+nj)(Z8Bjva}9dA)S9dGfD?I?Zk`jc|JPmMcK-;o-z(d^UlAH&D^Pf&R>F677>vR<~6jz>{njYkn*jYkC<Hj(pAbR10ibR3M$So)znUu2w(t=b@cI=-iTI=<(6f6qqglkrCCtMNwV)A2^?tMNux!BZc}{gLrc>Z|cj!^e0&_1$X@`0eU(uP-jOEAM|lLXOM3vZ|f5^VRvHKKp*-WlQ}#j_U6*KaRHS*Sq7q{vP8_J!a?A`VIfqYFWRx@V@ke#*G)gvPqUJy>Z-JKJdpO(hnNXr@k7`C%!SB4?k!;pZLajKK!8ZeCn(5eBvA9`NTKI^VNRocs}us@qFSN<N2z7I-XB_V?3YwYCM0@X6e)U6vxuro25_Zi-~W{>k;3W*Q52Qc|Gc@`C?j+nkS{cnkR)HG+(TII$unDW4@U9#(XjHjrn5uLG#7bSM$ZhH|C3pZ_F3N51KEgKFLGSe6h+Koi8T7F<(r4W4;)E(0noRjrn5Y8}r4gopipK__SXI%@-@5&KDEkm@lT~)qJr!UOHb)d}E%J_{MxOd^K-N>rp<fCun||_{RJ)@#%FMG`~!IW4@J^SM#%~pR4(0vR~!X{Tk)Tew9!68#I3n-@W!{zg^yxPxGdHnm1z}oU~v0wEc#U=MMF0`-A4$RezxK?8Fc1Kk#Y$gXZ6<Ps+28ZydHgk95AC_(Ap1`FhpPofVGi=Qqo8etkP@NZ&p3(C2nO&9mW?JO}+AK(*&k{BgVTLBA6qzT9t$<=0wqkH4MouFE&!5ym1|M!M;zTEY~6O6`BDmD%=x^;503@$vuPpK3j?F;<^PH>T?VrgJOK^Le}gEd)nt`nr117r+HPL|xA_T}2&&3*gO${sA1zV=Rv(rfXBCa}%sfWV#A35oKOSIiYb(XHiCM(-ay9ZVGP3<5?ch@o0_^{0#ID;Ag-spe?~IQAZ1C99SH4Kc?qn0CLwK8U>C*8Nnidt(l%Lp>4n-1lNQ11A9gLI4^*<0ypQ{jK?%h55W_mao{-QNU+$Z74|Q*HCX&ounCV$O%K7ZL7xVT5d13F3{BU@SQftE=^}Sr--NaR&k}iO`f&(-4*Zn3hIowD^bkCXYr3Xu43>p2c!oF!Os`MqvtSR8Y#uoX!MQy0pfeDH--Kp^r$Z+}v%!<VW1t@J7;rkmgSL)_W<Wh)589Lg9S6<;zX}}>eii&0&V|qk(DC32;3){fZ$QU^-vCdB=74i>{F4!a=bG{*SoD{%=rcmIz!SmKpi{LceNXUA=p67&@N9(O0%$(C06ZT$4?G`S2%QTq1TTQ*ffs<i2*I<UGr;|LxOvoIx;A1ux8>1^M<r-A6L-Y2(5hgUxL$eGfz|~(u`Uu?2i%@VJ06vxVPH{b0_qi7+r(Y5TpJt#b%LF!I|6NZ5$zCK&%|A@EVMef9gaB+S_#}4Z4HN326w@_>d<g-D39_y(x4;36|l|?O#_Fc&guxkRS=a?HWXYQ8U`*8E(fgyE(Z>QRs)BCHE30^24>LO?8%?tC};#Y3S1u=39b*0hSmW`gBw8Wf*XJvLhFGWf*V1rgByWsK&ybOAV)P2f@?x6fNO$lK`Vk^<_90oqZhO_xG#?mn!dgR)(PgXBFxESFtjUpFgO*O0PfAB4Uc4KTkt?0ow1+J*hgP%Beop`UzF<t9RwbPGJ=O{;<sITyIg3K;8%Eb!un2FHx$R#8trP0HuXlEMB7rJ9l<H!SD>B1BQ*WIj)XP<cjpnNp>Jw>{}<d-)AL>h>IRE##I|X;_lSE?LueW}4P^wssOkN37&Hnj_Ej1C6CpSaS_Ldr>^BYPUi5(hnyxQtI*YnQox^cl;yCL=hl7WsOnn?<ckEke4{&*0huz@|PJ)JjMF>vR^yBKLJ-O}#YtTe+BFbwxt{ylxp*_JVI6uh<!F>>d`ym9op+muLa2j+7I1M}!Iv6|>JOY{u9swQ>9RwZ@9tIr<9tM69+86vHxEu6ka5r!wv==xLoCNKyJ;`%#oCnp{)p<!q{*sZS9?*VZq5Z)<z#`W#K?gwln^>%?fId|b_Zv}<xHpM%wb1WsLi>aJql{qj92C#m1cczO&<^0PU?(&l>;$`*{=9pE>CdY!;LcDN*oE@yStqm|G#=az+!opa+yQNpK5u_JO~0=QZ4Yh@R`)-l9ii>P;{GJ=Ely}huoK)B+8*2$oB(YHP5^g-#)G?nJ0k>(dv0CP7kS$wp##AYJZkf(Bl?4QPVh*E_67IFazoL#xu)_M%yb@x<y3G@P1kCg&Z9VIpnL|l5nPe4D~I($#kx`0t`@cx9FFB$;EK?4;GW{%Bl;k;2ly$z&cWkpXk+jzd|fXdy_wD_SndUGr0E*1={$mSI?AVG8^Klix=L6tRID3;?P9R4;09QZ0at}q0$1lTgl|^^IutBIa0v8O@ENYBd7Oft1fK$*fPMx(0WO95!KL6s(0$-T;1cLAa0z%PbSro#cnfqRcnf#~bUk<j*auw$_JLPJSAtiA-+?XzzXM(hT>@STejEBn@Y~=*=mKydcs@dK0gnni*X4PHLK!#|tU>>q>8ybtGhKfMKL$U5-T*%Ue}@o!4tf@R4!jq-2fP>j3G{vNC*XIXe*(V?&WFwe=Yw;hZ-R5d+0aSgZ16bf>)>(VOz3OiOt1$!2J8Wk=J7F)O+1RBJHW-@FQ9(`e*wM>Jqo@Iz6<>dd>4EldJTLZ{0Mp-{0RIj^at>-;NPLQ!M}rlf!+fD0)7bn7W@!=5Bd%G9{3LQOYj}=CFl|GCGaum0q`;KZs@1r-QW+PAA&ysuY#@xuL3WGE(b3Jd!cWEz2G;XbHHzabD%T9Ip8el3~&~BJaig(Ja{a0DtIh-0(3ff0(c@c4?Gb(89EC*89W6#7d!<#8@d=g8@vd*0=x+P9&{b}J@CiSP2kNuKH~9bs94?(Edp-`AA}wU9|V^{zXq3qFF=0+UjSc){sVj!9Dx1{8~}e0{Wth~@Q={nz(0a-LjMbV6Z}``Kf!+mUxEG|d<A?S`Zw@-@L}jh@L}+N=;z@5;B7oodTSvO<^HFCrGD}!#*digAFJt>)?t0~mfLt;#vp%6?@;kR%s*s8<jwLW@pjAp1AEN&EC'

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
