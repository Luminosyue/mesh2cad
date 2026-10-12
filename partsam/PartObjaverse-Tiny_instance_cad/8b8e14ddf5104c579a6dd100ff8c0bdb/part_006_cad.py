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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8b8e14ddf5104c579a6dd100ff8c0bdb/part_006.stl', 'relative_path': '8b8e14ddf5104c579a6dd100ff8c0bdb/part_006.stl', 'source_sha256': 'f4dc5f0bab9c9d2e3b4108e10f78f6c51a3ede592de99a2a2d6b9652b127a1ef', 'input_faces': 384, 'input_vertices': 256, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17516566812992096, 0.1579466164112091, 0.10826370120048523], [0.06838101893663406, 0.4385267198085785, 0.19246378540992737]]}
GEOMETRY_BASE85 = 'c$}r03s{X=+sC(|VVI1P)4b>zMre$N7$&D}Y6e3N<22Ja>{JeuLn@l&ut!NW4%3(sN;^dkk(^09QpzdGSz>!NG{|wB2Vd*{|L6VmUEg<I-}Sz^?(6^S-`e-O*S*&B>}Qw$y(?F7FyQM0!{TNqyPE483@Y9=I2fk-1qP4v@e67_F(9;(p_cgS>u>#~?_kgV-&QhAHH0<y^$YR|Z0@Et?>xF=^Hy5((USs$1HC7XoD}Hmr~EIy#|Qb9`$1#91N_RrZ_&2>r>!*CmaViI+Q0c#y}ShNwEv;~N|&8K-A$ENz3xHL`i;al{ju|ueD8ZZOR0YOagOq>8Mn`<?~R|-mhpyp8RDC&7f2rCH^JFTEw<s}TM~9l9*dig_~xil@L!xMl)O!6Air}b_?9!s?=nlqYbEV4Z`sAO;$L^byjh{yGCqBe`1=0v><a#b%ya5{Q$G#s8kBud>hy{c-*96(#@E~@zP0_T^OFB9XBlsbZ79BF;w146!^g^atG#8N<hl9|{66pJRqze<#5XNCm0Q7|*-L!AZE^))JGvZsngmtwtv|Q8ApTgbqW}9C@y(xJKUBdl+a$hz!MmbAyz)gEe=IQPP2Z9g1mEAI!n!PBdEy&f0uEO2@6{@j@x>>yD&&9BPkh~JN(JB2?g#NLu7fL%&zg<#ZYwML2O^OFqjBOJN*AYypIJxNrERY(eK0-rTO<7(Um$(6tZ@@xk9UUekSBSJ$qx@m9$P2zwY8nGzfES#ercnsiEmvvtwR5`XMe4hJhuvwC#gT`>3J7^*<h*1xFB2lZ0vhQd~5MCj5j}!d3DEl@h$njSl7hHlE<<r7XG@9nD^^+%<DZwe9ir5?Bi8W$*<Xb1pi1K^exC=@)+-}O_n@oOL0z`dCLBpH~l8Q);<gSn^zh8xUmby4<7+P>Mxvgj|)k%u4^Nt9`lGE(jWcB4ETSxgYSMu>NIznvr7Ee`RHfLDj9FKbr)azqz3wva|iu-P>?9|&WXW#=XFH?*XN6G8kCOw-+JJj7xxw48sLxoFABvsWPXA1y#jF^b&C++xT=--T5J&d5b~wWtM473AoIR`4E~VTIRC4!#7my}y`&F%*$&)KVs^yioNO207#WNEQizB6mRb#^|AsYpWq-||+he>r5c`t50{+hAIH`a1X80Q-aUL=|#i7sFaUQ;l#rUXq;1|}qB=a6G#kswou|o1(ZjAF#cO~vKy)P}7@f%Cf&!Q&co8~-RCUw?ahkm-GqHj4xi>1!`x6#kUzu>2Dfp5DJ<F|z1I?^^RM*khrw|H;KZ&-9TO2&uH#5wQihC0vpog?GZxZai{;9uVMqtrR|clf{U!Fn@#n59miXzb%<U(}P)WTyC&@=)idOYk?_g~`0Gl~K=tny5!_*;THm{0`{D`*Sh=Pq(4ck0PFv=yUM<w(^zngPl-+!aZI5ROhkcuh?F3e7Jp(oKuglv0ppvu&$SFXUIOdPD7q8Q?V}V(%It2?3MQyEiVq&%Yn&}^8L_9;u{}cNB&<LMT`HaE$X+)fS*5PvD7nitDHmA-nCMvd7pcXe80Xq@_WT2|F}KkYs)U++;%;Qb-g^jM11Q|%<Ij0qdxyt{1=a9yfv>Y*5#45RD6e@@ctOI2jj2UFPC~|M#%fDq0?gcC(`3&e5MoTofn8Y`*e$!I*ZrIcnj|vh8GPIq`%GdW1_bYXTRxN=k><*nEMmzcixWi=ArrW{Ws1zxGrogGG8_KqcUIp5t2v0Sx0<p(s6lyF!T(-ym3v%w>+{dknwgOB9D!W_*%qCJXc)FL_dFZg`ZZV0Ow>L?yKvDiLVC-;(oWGQg#JDcX&Roi)`_Yw<e;_Y0u?;WH^?N`;3+de?YwCHKw_XZ#=mPd1|(WpE9(f-}>}n`F_+ethYfr>ios#r1-aIVO<Y)B7f^x)Eznz^B&!Y{^a>cpS8HB(q}y>2jjc=VLe5k$awwZi<tL9j_jAQ;5+<WdyaWMUrK*0VOLRa`YYs#?SS<cx59JRGee@}=~X86oBVHKUCE8%Cv=c~w4`pu>ujCj_p!tNwGKx8E!@S|*4LAHwT5XpKO4qid`vj@B`OK^KO85%@mucStA)r@77D*|hOA3_QeA$oPhAK<!8af4{0e=Zzf*k6;u_Lty<s)1w{s50mz80EdtJwRBXUvC-k!29W4BkBx6U#6vj<9k{rPvubLay6Ssn3yxvc~847rSXGfQ!v<I>QN7{e;*W9j3QxLymf?=NbIug{D`UQ12%IkkcKmd#ahp3iN?dT(@sf9UQ>To<k~zqw^!@r{Wi@f^_fbM#^N*O>Q+1M0ck8SlScLd4hBd?5MtVejFb+=)OvTl1vPhM!B(hYoX*zyCXU{j=_<vuGRgKX<@+t`&&=^*f9_DPdTr>8ZRgoAXa&{FFa&4i{C&`+jK|#^+|sdDDxRpq|hNSnns#uwD-@^eLlC60VmC*q6u@oS!0F@pbK~<T1N1L;WiTiEq{L`NiBt!@QS9BhRfivhUXAS5SZBP~=G)gT9ZmqJFz&@b~PJ{+LVge4;1Di*LG^FZs3mv#~F2S7F}7kFeghV^L@Ib>eHszrp9YpeneJt=K5O<xEw%znKoMg<oYi>U0}``;`~&8~Tz=)U&7r@2|-t4_5F!J#n2*io|}Uokjjf8m^1Mhj4C9C8#IlHTLmN4*C%G66<ob!F{;XQOp}`n=IqK6XbKE@w^|dCmVb5jg#$B_ey)zQ(Rws)4hL6e#1q4-qFW=EWY*KW^z8w3#a0BQJ=yuSdP!LjyV|rnFsQF9LM|7qh46otpTWK%Q^JlunzYR8-MZjl8Jafs{0(D3#O+bf5;uIYi?uI|8_R~(|DdY1P;LaWB60}2R@bYhI;XMp0~AKE&kGKg}6@a(YJsW;_DBKaSl%3!1+mc6JHBoBkR(tKEQb{bcg?A8|=%OYj}>$@e$wDs2J<&W{c~o#Vq6>;&en_Kg$Mv-W87VPPwRO*LL*ngGCr$X&}z|@h4et`c|_^&f&lA54$gkZ}Gl}{c;?S``q_8ktcmIo?qwQM<3kpWBmPO^etv5o(JyKT!V8q8vS2UBkN7yGMD=s_Y8F&s)O;o{}>lUq0Y&!;#>E)$vM%-hN8~8-WcCgN1t2oLp>vWFg|y)<kz<kz<Ky#y7=0TdiXs?&<D6boJoNnRU*Fe$spW+oUe&*+UkXKvh#a<F4$yBk#VisOaBe$BC#&hMDa}}U*S4R#peja+5qvbm$Q)HunYYx$P!<BH}e$wwjA>wE<_&NN!XX#U9n!TbC}o3Ed4iLoQZkEtm5mg*YW-}`hv`B48Di)E2<n9jU5hu$6ISfA3w$Yg!^R<`%HZ6>PJ$i<=7yct5!Y4*CJO+omS7Ps3$2J<5%MIh+$S6?0e7M@Vm4{p9iL*Z<>yISDcgkv!RkB>Q63#Kk)1cnP>Ow{ZfzZJ<Mx28`oV?Wyx=J_-vi@XXi+~FSHnld582CUte}p_QiZY2<u(x3BPJx+$W=5G4J=m;%j|Q;T)d-8TUh<2#o*OLHeV)+}e-pF+qIexd6OB+DD@v-(u8bvmc+!EWe;0z1n(tT?ZemcM$quxN0Z9<&P+wtKv@kWL&fh#yj?qK3GCph;JS`M11S*FK~XUC1KuDFXZtUkNbxIa~W?OFj{=m06Uzk+^6`wbM<@ijiy*R52l~iBY)Ewn0Iol^i3Om1o`uqV_w_&cupv-l_~jZZA6~sPEw~H*enx2--<k&-$#Ga_MvZnrKoc#)@!QdxL4+Vd>i9kyrdpW$L*5G-1RQ%&kaX^KH8Zfn(`d;hBd&vH-|_bV^-}A@_N51xb8lWN1lwP;u|}^!oH_`hV$^Uz4&_4J-m-hor?N9egl6-3Enpw?3Df(Zu*I@&7F??G1FyUJ!qQvra^;ozkR+7>s=C#c^eML{n@!6uCKGdB7cV(Qor?!0<7!FO7X2H?_<C6yW_rhVl~Fsb;NbO)I;(cJuhOt>4)WWpLI+voVTY>;J<2t_vQC)<MV>2YpT@m6Ncwcmul#L(nRr%DGpMnzTwb*T$g<|%DVo%fX|^@#vp%0fcTa>)A2l0r5^H>g^91b2cw^EFW`qP7T-9&1oxTP+VEqSiLdpTg6A>!`QjUzR^252PXVZNQ3Uq)Zlw6unkD$$w+ZLUxWqP1>In43{fg(%*f>mlYr+WJ|6jMkd3bHNS^VmEkY{#FS(oWS8}UusUg0_9osN><ss&?wdUxE1C)|)c*8F)G|6@PgH(DPT-(s7L@rjM_y!}<IoF8jd+jJS<1o<t=XOaJ&2mGRTl3%k~DC0H%AH~;d*TL`AoxAVv*1y7EFZ#AySjTK%K6QD#V{kBx_I~qE7xozTxBl;cx)|5)|MjN}*N*M}(?4A#m)G!3d3?uEJdiqotn@4LKyn|3Vt4B2WTl^x-N|kY#f=$?n^HTHo031Ib|8O9ZchD_+??E!q1c()o~*PT*_qseq1cJ)N><vM>_l$DP~4EAxDi9KM*W1Wv@Ka9H>0*8HzT(ykB_J>)HY<LUCA!wE)2!ps7A8VFUZ}<UosT;qV^;!?Mv=O?#EC(i25~I=}__@^0y4d)2SoK)5$BTv&l+-A+IEFVkq89O(1V2r&50=N0mo>d6=oG<W!C^GZZhNCXkh`ATJ;%QrD6b$?K^*$x8Q;*OPZs^U1r(+0;MCO3#tA$+-;0XQ;QyO0Sd8kdIQ&l8=&4QLmCukuNe77gK*H7n840%gFc3qqIC8FcjaTULjxM_<Ib+e=-z5ramMqeL{Xre!)=uiu#<a^e^%&@@t0Tm(*uurH{xj$xj)I?^17(l^!DBC7)y{PNyc5m3~J~Cx6dSJeWF=th5h#FxivpPWB{wFcf#9x{;MOCU+u#P#*77|3Pg`{s*}MwJEs)xjywna(!|=YIAZua$Rama$RyAsxw(>3vwN@14D6bsuNjh6LM{`J+&d(o@~cZT#MR>T#Ni3RU^Mgu1Rf1u1U6KD0ZZ_BL96~c4R32nCe3QnB1A#h1{9ko!X78^h<Jgau0^$-qc=XrTxgg$^99MhfoKRm3~VeLN+lJFQHB+D_u!mLf+0$yq~&>yq}yy-AY!PO3oo?G8Cs#<H>2{Bx)4dzdXj3$7qIPKZfGT48^_-#Xm3<2Qw5;r23On%40`)%%v_OFXGSVQvJ#PtYa=i@l1x|FsdIpj68=rnLLLa#85nn>Pz<J8b(onB#$DGq0S?ZAqP+wl9etd2au;Q6i=i6N}fiZMO{u_&OMn$jUszfCs3ovO3ma6<gpCJGpGy5N)yR5$n&Y|$@9s}7>d_WcaztUcTuy+N^{A($m<x2_fpT0l^!MUB_E-lA|D|iW+*<*P+Ua4NG>8<sl{ZaSIA0B$yV|;>V5Jx@=fX;@=fv$hT=l%KgmjulMBf@bq85#3Rx$|QRkAC&Lk@hBP*RljwAm@4I=+UokR^HD;-5vI)<z?fINvjoT1o@I)&^-9!8x;RyvFP_t_oBP&|@4fvj{ac_cZ6I)kiqJ~@OONnJ*cB*#+Mkd^KtD_uv9C9h^E-b39>R(gcIhkTHFn0%0Yf_j>Kf_$D@L{@4gpC@0YUL#*7mr!q#mEItikS{P4=TQsEdF0JhovbvDtn@eX-{)pCL-7WN;!x@&veMyXrC#Jv@_6bn@_4cjbtKt`Je8q1kQzb`;T{Jv6o*q|$>HP}>S}Tfc?)$9c@Ot*3-ttf3ptB=o}5K4U?{#sy-dE$y}3laK)ysi#!#F=%_HZr?-|q$<P7psYAAUrIf6Q#Jf1y`piU)6kfW)A<UsZ=nxS|VHHI9+zN}&>-bT$LZzCU|7LW_L{sYuw<YQdh0fyp@)TQL5ta~Fvv4t8<j%H03>NfH==2cw7pngH5{);O@adm1{a&>YwhT^xWZ;_Q6$ZwM?Gt^fVY9+E#8*=~NmELlw{D1w|+yDMDs~1)HkGTKyl@)*O_2w)0mFN1`FTwivwvig&D*vY*d_vWewBf%1I$aGO'

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
