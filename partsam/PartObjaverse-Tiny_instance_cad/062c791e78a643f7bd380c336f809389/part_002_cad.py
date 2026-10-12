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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/062c791e78a643f7bd380c336f809389/part_002.stl', 'relative_path': '062c791e78a643f7bd380c336f809389/part_002.stl', 'source_sha256': '0633f518f522b40e2479e654e95c1b903830155eb4b53ca4bb24a38b096d0ad3', 'input_faces': 518, 'input_vertices': 352, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.45172327756881714, -0.4676419794559479, -0.2917894423007965], [0.49934136867523193, 0.4360497295856476, 0.3414250910282135]]}
GEOMETRY_BASE85 = 'c$}qM2b5Gr+I>9)K}ix-QiEZLB1r+kX$c}Qz>t$d69rK~hOjKDWl<yz5)=>@ddN|U&d4C$Fu(-DkQtJ+%d(&-i|&r%qOk8)-B<gn=>MGm?9Ms&+}pRluex5PucsLj+U3h%+LAw2tTPoWejBJ_SwIo1v^8$<=rO|v4o-Y_#Ha}#tAz0J<M6@`-P$Mg@>t`niLrwQCk`AP+r%5&bV#GvTHe?pBS()J-G4;Ck)sC<hW|?cw-N{2e&W#nqXyfrtJQB<ua>ud^;+J^-v9FFVS5PSLf>8rVMtT^eGCphG-Xtr&EAaj!uNeXd4=$M#QWg~|NhU5c<tYMcDFm;^sS7mYvKD(d?@_L?OI`Xyy-jf-uo>t;B|Or?F?-^hOhens)+P`M{>mLlw$ir(fp<DG6Yx4FZ^J~PMPBQR;=y^KeA`{dEwuEeZKpB0|U1R-~Z9trS5s~P242?dzo48c;CS3!jDuba6<GO_x|2cG~W|A2oB$TQNFLgOBk=Mcdx7y+_;MLC$!!d=XzdiV?O!5kNhtB2@b6<=g;)pjyfdf?T=sQiuM;5r)cwO_)h=6dJBXfcp~Ybd)|V#rwQMGYtbHU-3{OACot>eIWhkwpFgh6r{O#C;g7ltKhQn-fIHswRsThv628A?^`q`}f57MX!^11c_Z_zJpnKhegA2*{XNI28p3Csn`*t~UR`he}_e1XZ$Riu1pIJA@z3!&(^z%Txvmesy3qN>s!g2TdKHzhGeQ}k~2tO_6sJ0IcU%hYQ?9*agA1yqsjo<Lq`KmQkybc_wnWLRw!&m#Wee6lR_TC$N(j9O5YCfCn7xU|_QTL+gx5uxWLQ(wS$Z@;H{LHx}_KmmM4dHwJgOfv1{BUBeT{6Cf7@z;<v0QimrtkFcYj!})m;dyb^X~pl-|0VC^0>H1teiF%-Om-=Hc#ABf%vu3&wo#x>)_5LvH$#)X60(@vUh~o-;t7+bKUWQAIph-6n=cuW$hdpzPdkqbx#v<xjzWsH+5^@XucZHGb6qfadF!&X#3yrRsRit{6dVs(+?N4{te&h-}`gYPVsuvliK`v@1~p)yu9dHu`VTciFq-7Z*tKi?)YG<9p}XB0X6r9qWIyT{*>X4kNkW|_>p=IwEi7GxIXEyJ3est)!b<PJHFF@B<`H>t=}$-=XK&u-;58;nJs*O`6&lOQGD<G+{5npaM7|+`*-{Y`hVf7xVOCNF^57?{9u<pVm|$MR*LxzH=ljh-M{HO{rfMkmh05}%4zrfn7)di7ZJX1`T*I_d+&+ycyHa5>)LaJj4#w6svn$^B-j1)eL0?jUyJ+3-(tX0w;u>TC;h$t&7mlMB=F5{cYI`9LvjBER;&+)qWHct`7+$`)@PNDiGE@unV~3tAhl7BJ3jdIb$Pxo*UAY+@q-)EPrBp%$s1C|xky-WA{52<FWGxq>;K@i55;_@zjQJb#Sh*ae#RZ|jT^c(E=vE7Z}#t>cVJ&!l<_;hIsRa|-?HMO%#Y)n^Ai~Il&D|k{5$>w^Z%+>yq~$gj&H87KkbN&=ROIpO_BG)?RIBEQG8$c6S;q4TW$$O@gohoq`Bj*DjQCT^~$@G5sKnF=fd=zbMZhw!@C^Q#yNVCteZ2-YW+BV;QlDBAK$a7Vjl*7yOkY^;)f5dI_{1S7Vjp`TcG9lIiV<i@Xe~H-0|Kesq*t>)p94?@&0b*MSbw5Ry(6T*K7N>i}#&c_oUXpvp=_Nj_%($uk{lMUt1~OzgJH!-dp{w*th2UMp~8mQq0rF7Wz0R)Y~5y<#`?df#;pPI9v2rCQF-7#}6Nzug$0R#B}-ESTDyn*DH{@M0`Fs_le`1`y~9vEV-YJ{ptAT{tT{Za>~8`BeTDh`(b-$z3v#kQ+NF9vgG*Fmdf8FPQ5Aix#?Sj(#7X%Z_^WUJasQ<b;|TrT`tl^)X_liu6ms{d{x)3b`!57dD&VWH+`p$`>#}xpU<xSB0fhsb<p%x9c(^L_`VnWo_CMm^i^FOK419$8q>7TEvD~$Ziy_uA^gbH8)x0mYx-*4$Mm=$;@)Z`>pbhD={xn&e{PTP{hhx#r;Xq6)%>q1BtJK=nRG^*f5TVv|K=(Ad3xqqv7f^=^2B~H{XklKagRlYUlV>{=w<mi|H=?i7fe4eG9==|BjYZK{d8okxNm*&OT~Ch-@5!`hC4o7y0_T>!Ib%0yyFLIe=p(#@t;ZGxc?pBy#Gz#IbW(D<9;@M=e(<ajQiR2o%`AG&HLH(o%_o1&HLH$&HLH$&HGvPZ`{uh_`IJT-@KpIc#Qkm@y+{LjnlZFP5*)CHSTBAckXBPyvF@(`sR9>_pRxh`@y_#ebYX;BHHIXCg#Qe@Rm>AzQ1@eIbVGiC%S#_Mvw3#lk07C`&R5#IbVx+EC{*#8JZ>h@UOpY*ZR5gv5fC$t#QYD(?-e9e<wq!?)XT}8q)u{!B%&C<l{T?`<WU2_qyYQdCP?#h)vz4^?%ndd|%pk`?T@@;XARek@Ui8?szM?hy4Bfu@4St@z?vvbJ4PBSc|{6OZ@&FsUklgs`1=jd_?%e-`TH?=jn@w#rP|C&(h|9(Q>hG{9kN1pvA8^F22VL$4x%0^`AIieoxqR=OK4|xa$&m4=x*b)E)0jsw#h<DKjtA9UrJI>z02(lN@(^c>20@5tsU0w$^|4Ch<Ix`GbyY>s7pn{M=A<*<p8l@V6NGdAeP(6Iy(o)#7`(NXzUa+WKZpli%Nt{X~loOpFoV2L|TuKB~>X=a~3CKGLAzNo~KaYO+nt+x6kc-0{AVdGhnhq|RD=pw8B{VjhNH(&B?D)mDn}_nM-|zrFq=;Xn6qjuxNi72nhP6Ur{p)^~jAnIir#Gqiq!aX*XiZLR0?wD%3X(dT_JANNOT@&5X$^7qWaEA(-8?3yh6?Tz*LEz{NuK2uPO_j~@jS@fU(8*QG0@jq=7{fw-w&2wN^shy%dGE`re4ii#De=+5>b@Z>9A@0>k%M;o@@!!neBY0lAwy%8s_KWlEf1-jGAI$wheE;mb*C0zf7mY8;-v>7=I;Ne|atY~TpFZ?XhPF?huOrTLI5q8v7T<Q3_<l3EY5YO$dE<JD?=i#mwq<Ma#}~<ZKPw?!+qc_0W{P%ee5Uri;kUEoeB9OUjmZ2mqF?X6(ucHj(e6?Cy-%S6Uup48R?5$jednZW{U=Y9&(k40MT_5(C;bnvhTZYL+>P@4=f2&yYv($qnEZXOl5dX|UuBu_{auD_(BcEv<h)m#_k|WeF<$<=MynmmwD=NJ<oC&6r)_n|hs&l3KiF^eC@ntgjQn1@;HEWN{KXr>59B5-6x=W`YF%@Dv#vS5S=SujtZS+tqpqobjJl?Lqpmr=S=W?r)HTO9>zeA{sB3EcMqN|BQP-4j)HUTBbxn=OsB3CGMqN|$X4EwmZ`3u_zfsp5->hqnZ`L)nAB?)D`Z4O7@{PKt*2So6YMe%0Q}IS!Q@&Bx)Hsd0rsm(MYiiz%x~AsAsB5Z!qpqp(8+A>^8+GkJ`%tfIYJH8mrs9pdrusMPn(D`>YpNfkuBmvVt|{NBYpNfkuBq`Dbxrw3T~qxVbxrw3T~q5~)HO98qpqp-HR_t$4@O;6zERhdZ`3vQTt;0}@kU)!`_`yy>UoX2rs9pdrhKEWDc`7Ts(+)dsd%HVsd+Z)nmX4;T~qN!T~qN!T~qN!T~qN!T~oeM*OYJ6HRZeOT7vf18<Q)KteE+jWdVh)($<jvu0P#?i64if|LMlC2LG==-Dp_1(f|6V8(Zx${J};y0=gG@JoP#oeQYcyw$NKgy@|YodJ}a|@`uztsr!%@Q}?hj&&EdbcIu7PYss6bdy_X4AJgki-Ge-jx{ZxiHrkO}Q-5k>CEHiB4f+!stJ%JqZJ%;HtJ!A{YNxN(%xg{m6XrPmwP74|yp30Fv?aen-IK4KIfPzgV;MP~{3`XIZLDJZDpzb<_W5V>D(Ypfym-bzC)ns}qXW4!^+z^VuzdyFpqJW6W_vQ*pf~V!cOu!<S7+vRroWUqPJaoEgKlr5lZ}q#F4W!ldOZOhw6TQTp4^Fgk&WeSU+#+S$UYa5ms2ls<+W!VH1^VLOYSG|Tx#sS47O*m4H|nji|tu#+svG~Y@f?EXq<&4OP&Yt9BQ1MY_?~!4H{=HlkJ&o+rgYUY@fq6=s((+Vq*e%67}accC&pq+n~4ENM(B}+dgN`B(_gt8#L~UiI%)Cz>}$Qx1_K=g>BHE+4z#}U$Sj0b0)KWGTWfvw=vzuFk-rk-=N0a&$RJ2c{uf4wv8meP5q9I`D~x-@)puhB)>zwfNi76iPTAK8$}*XJ%?>0$fKxdvF$DL2<kU&%wYR0m-in1q2xEIr?G7ac_?*&ZG*@|sHd=P0C^DgB)0j<1E|NbtuNV6J%(+sk^54QW!vlI*Qonha^1%gjyIWpe{w(Sscaia?oa&z*Lfx}jB7m1rQc=#U}CC^2U26t{K=)kZ@6-x!))76exEwT+%S1M^+Ap)gFKrW=No(LFnK=pVd|sgh15r>kB}EoAEC}BCsE^kV-Fo7&!Rp=olc%Xold=v{2ui_>b>M?)O)G-kOS0vsCSd6P~$$pUipGNj`|Dgo#ZjpJE?b($5QX2P9aaE#(jW2kw%_MeZZ3Y;~;q^bsA&7BEL&r&tq9H+IWtDewKi)ML^depsNwk&k)d05zti$XfFX>iGZ#^KtDl1KSn^8BcLBApvx1`6$$9d1auVw`bh%%X#zTyfUZtJ*Ce286VP=C=(+@SeFC~60sR62-I#!GN<hCvK>G;j<^*(00{RsK`c(qDEdd=*KzAUZ6A0+e1awydx;p{glYs6`K)*&n_a&hF5zwy_(0vH#UIcUx0=gRk-GzYeL_l{WpxYDB?Fi^L1axZxx)lN4f`ERRfQ}=en-S1W2<S!x^z#IC19Cm;oAw#|$;J-^^xp~S9|`Dx63{;r(02&ve-Y5X5zzMtXv-r39pjOJ&hL?cF6fbfF65Dbe%K=cUBn{+UCbi^UBV*)UD6`~UD_i7UDhK3UB)8;UCJW?{isI*y0}LIx~NA2`Vo%=bYYJK^g|vA=mH)I=zJatXpct%`aS{uI{|%{fc}+${)K?fBcT65K;I^yZxPVn6VTrg&^HL^zY)-XC7}O8Kt~AZuL<Z&1oQ<0I+uVxOF*9{pidIe#|h|T1auAoeS&~KML?e+pwAJ|=LzVG1oUMB`U(O44FP?XfWAgRUniiyCEuiO#WRd^0LIyX#@&cJ5$g=T&oxJ_L5;z4fKTw5TJZcMAB^+%FXpyoep~LR`<xTxJ9R3D-pjl@kPpTgzQf#j=Erl7dYD^|`QT%m`#9b^$Oq$IfJSZy=6B$}&&NI<XFm8i*RvV#EaZc6*FYmTf%yqMO9j|RdFF#pa*s6OeTRH7?k{NMc4mHOp3jHaM@8m?PjlZj;$4Y+Fz!TX<aT9#SDyL8?4vUC!DqRbk=uaz&OHl_-0sZp&U@q$_EClT;9Q;$<kn+8_*?ER<o0BKPu@*M*~gR22VdZsLribR_2#`+oUu<c4t$B{^-;z-HMA6S5EIKdFwQ)5DaJW<whVI+Q=M_(h$S^*`Y{e%mO8>X=d%s&8hD6#opIpO)QG9gI56%hXvFkk9JnMkV(Kssj5`h*F})ZEE<uf$x{L$ke*7EP;yJDd_&U!!a(gfzT#OpI^_dUGoqL11&oUo;jduxhyD=YJgc`XGnGeQ2{vC5`F&})D_Y-ovFdzIdHF95IJ{Yy(d*;?)KKL8ndC2X=d~hLZ<ThqL81?2BbE`2Qe1-QYayv2~T#y>MO_>iy4ZF?UXP6Jh9Sx1#_RI(8r$+8e%m<?`{)4$sF&~V39~!ysm=BJjMy`+fVAR??=2m4s7_|f%xowyawy2TYocUnX?_ZefWj+}72^zVrnGeQiCX0QvWIh<534Ud6CFX-s^PrL2iuqvFoO{fDh52CAoV(1ez<e-j4)oJ#!*dhRj}p)&$YrTZVy<lzB3GoYhdUAbo!o%BF7`3b1o;K(!tA#cIhML4`zyv6c*XfXc)uqZTZv<DY@?Bl7s*Yi@&6!;+NeyfN?j9s*G3)kv(#J$>k)Dh>L+YGZlgN68nxHLKQGwliCmkyIrbCwCb=o~LpBOx?#bn;^Vx{8QHETa`ehp}Y&0XsQRlZ&z(zUpW7LRg$+(1eo|w}4{;&VS`k$Ww9#s1et!AeF&nNE8y>?&fA5#+A6~Hsu4-g~1q}zv8u>K9SgiIj'

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
