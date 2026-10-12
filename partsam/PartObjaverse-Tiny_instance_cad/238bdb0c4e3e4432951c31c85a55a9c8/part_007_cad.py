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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/238bdb0c4e3e4432951c31c85a55a9c8/part_007.stl', 'relative_path': '238bdb0c4e3e4432951c31c85a55a9c8/part_007.stl', 'source_sha256': 'c1630e600fde56a2a51bf97d784bfc44a3e2951be9edd4dd26d0c8d4866122f7', 'input_faces': 510, 'input_vertices': 372, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.39851492643356323, -0.4145633280277252, 0.00967569649219513], [0.3935632109642029, -0.13404133915901184, 0.4906676113605499]]}
GEOMETRY_BASE85 = 'c$}r137k*m{>RUZY-I^UBK%NeX^0tHvit^7WXq+&O+UtrHOq{oY{yW!Nqa-O^81Txt7K`z%}))+k_<DJ!T2T7ddpH#=$_|1@8>wrnR8$F|N8&u_4@XCpSQ;|=XuWe96!g@r$>n!;tcs!*I4r8pOr%O4MS8pBhHwdmN98mYFcK~aTA`1F>bcK_)_^wul_yz42&@*8&ew$Ps>crXwWv$pj~>K1_^-%>EkmdWegqn$oP!mX~K6MIyN)S@|h!tPDrzk8z!|*Ob8@3N(f93{2#w=v`!(?W!BNH;#@Y(-zL(`e0*m|;m;@Nen!_^;f<ANkGQ?@^S-^po39Pmd?fZa+XqA0huuDS<G}s)`1*0WztYzB#+KTL#Buasd3(OVhEMX{K6Ey6*zF@ftSWGikCrrTZ#HhB`9Mmt^tVc{zHgv8e&i?l?(w13v2y-l(yQ^|Q6=R0)X2=Uk6X+wwDZLDBW|zGQ~Aj94BH3Gp3k+v@5j0~O1$Uqmwma-?agkt>)&^NW%+#{E7<S$q4p~d+df@-b^f86(g%NdTJzBk?Q9=f`m{Dr_{V!}AL%f8m)l1#o<HXHq0C)}HNWpM+ea$Qu+KM|enIo*8`Jjq`N+~vzCL(g;&#oyek9j@K7oaEZEs#|tNCcRTDA{wkv@3wY>qwt)NQsmb}ioN_R*5-3+;XAExj}UrFFIsZe9`5_W5e4$nDiWC~pjs-r0vMx_9=$<DGr*cxNB*(F>!s^9i3SI$`?<n?|(t<~(eBGoh(AKDtTzaQ2z4+Iqvsj@$eE=;^K6JP#kYec-|$>)h)KENXw!?bW)xUaiaV<D_@?vvUW{hjxD>@Au>P>R#<L<IT5DYx4wpe{Anh<eA;;+~*%^*wXfaa=W$h(VqCcwfgwc@7enknY30PKM?;;hVS_YzZ|EZ{})|tAF7t3pJ%5{vVRsQ+unHace&5k<oSeqB>SGHc_v;TA6#djPiSMjK7UW?&9}^Dn&*7XM$>I?mc3y2RiIZl>2G>snRfnzdrKc3ppB1y{i*EF3jOr?_emdlp_%QCnsR)2R(rXwN=@|fh0;f+m(j<6_K|)5!K$UT@zJlPk9=Rk_Q9URci88<zLe~f$Lr6r&$He@+lRZ{Z2M^Uo91ZOt5+Y*JL@e>(Z`=ZAfM-(Dr!D({9Wn0R+rcJ=d!jBc0FUCe<&*F4-~vL+wH?^_Q-wv<fYl#`3#aikWgLof%L9&{Jg5RH^!Wm^Smd0@V(Vpnm@nI-k-pdH?y>PGNg}8?40FZSKxB3lWwop6?iJ%_J-LZ%e|k`gK~VZ{2luI^M`2O+0R=?$bGncdzO12qT}WG$UCL9d7|a=WS@V3ZkD#6$<jxD$)BaI_pUDTd3bu)EN!0WI@>-pcZoi}(+Bc7S#!QNK3vY@AJ}`?&j%mKF7We_eNXs$W7_^aKW{GB?C;yQ-|IV1d?{Za8FJSS-|>m87a#7B`dUZ#{qj{=d0($-n%&WL-$lP)FP|G#TH4;}&!i2yXMemt)Nw(9pO0>w>gz-O59ay#$b?V){l{JR`uX7UioV{+X}iOB{DSk_-9B<}7j3;!;~sf`4ZC04pAg=d(oY+&o_oPf{cT_DIhj0O^MRS&<^CU^sLd08L-*=F3ODE{@5h))EA8`5ohq;Iv%kstn^ak4fB!YH@;v$T%RC*oN?X@J-8-M(Jl>pS7WjGNw^Uyr8nh_S&quQ6`1{ls_xOI_tp2{<$n3G**N0*>AL*8)tv5U(N$$_fEwud!tVop4jn#ei@mcT7=g&j^<oxmM=K$$L6(?xpLoc?G*Cm*#jSt65Z?1fNm3AE)1?8V3t<K4L)N{E0FGX&zp2MNFS2Z6V^O8RP<axQS6|3aB;&mT6F;w%R=dxGZ<Gr7A1}|Lg*C)z*`$YM`8`BH?e5BS;UmsoZYM!4rPE7arGpFwH^T9cte7*5$;&xxZ_M05HH@1GDtv5VL_Cx60hx-2HHJ5)b*DKJ+zpzpIg-7K4VL5-`S?NPFFG(NE`OI&1QuB;gK2qloZT`S&-K+jlpEDiLb#cbGzao7z{9xUich4yB^MUq5{r%oo^8CE>`QJOg`uy)5uRi~Ky!v~M^3mtYZ`Sr<_xj^*@2uD3RUdl2>O-$redzV74~u#F(Cbwn78_3=7W4F><5MbZcK2IgiS)sq+1frtuO-UQ`JESN<3r7o<mco|wYF$|xIzB87OGHZi+i3>{6=|S<i52<>ywQwirn7m6OVWL#Oqa`c)Zgm-uYFZc*m<g@pz|C@X<@stNSZl+vC{><%6-yw0(#U(!KM1!$%4a?bP~k?$x7i@ARR^JALT!P9J)_(}y1K^r6?QKJ<8}55416AL0X-8L!@Ztdl-CyH~EZKV_%b?>z#|d*^EXHb#1*Xh*KrZ^JG~UpZHsCoog`K<SRV-2E1PZrm}qSN-Pos^5xv`pxT|_buM})%zCjc=f);<DK^{cyp8V*FPWX-svBFv}SOZyFWv1Jf3}1K2+wXFSPkLtvuxR>b+tye=4EC&zlR&`Fi7-o%{WKwBTJ|AN=85uAh&jtn>B8Hu>IC`9KxCdhhzA^uYzm`?dAH+eE&%JS@HQezLXn=CpaX4?g_7d>^}fy?md!dY(SdQt6G|`MS?;eZ=jZ{luF^(wlvG?^>vP^?e;5F0g&H-ZuHU?rq%%&&uoK^`Z6U{QWJt`~7^l?pj~3-Y0v#dY@d(^FCSmV9u`x-1{8rS<imI9Xu+%^Zq<W_s)BGucr^aUiG2Zt3LF4)rVfM`q1lD9~PURK6L!$jtAZAil*hr_y6|<4{H0+S^CHg&mPpS`_;4pdtA9^wRu8^@pbYwA81$RklQ=^hBt3#JpB``s(aNxUa$J6n5TcdUiDA0`RO08SN&7W(?7}wlcaa<m-lt=>>J+rqcC5)udkGn*R|=feC@g{(7kh?dcAt?dA#%7^LXdE=kd;S&*Povp2s`SJ@5SLxrdMR>rmicZ(vt1Ilj!&0{8xe=48w9TS^|%_Or%G%{%*vH|{8P$lX8TuZuMAJbygidH#64dj5F4^ZfD7ubw|1?>v9JUOj*C=77<M-TPxE&-mQ-nbNC%2qx%W^+PdFKX|?B2d`KC;Pt8>yk7N#*Q<UgHb4EKd@%5izTUV3>F@vfu>1N3f4*~{J+6Dw5qCcr@6Oh|8n3+BS9;YCk!N(T`oZf}KNR!ygV(EmC^kR+;Pt8>ih24$d81kjZC&QMgF7|frJ-DJw-xg9>m$-T|BieyU;53`tNt;6*S+eWVxIo-deuK(ulmR9RsVRs>L0IH{Znjy`bT*)XQ15wfqUe?pGWGy=Jt_{R|?$TSUW}E&j|@THLv!w$+aE!Jo!_!{WSZ?@sV!-)aD63G<%2UnI}@Ezx4YL=>56;$aZ_)y#L~vC;0ms>EmMTzn7RP`|QupM&bV1_Hh)?ePOmQ-0t?ydhwC}Fh25M#;fx&Uw%jW4zWkw_m@$tQ1j~k@_KcD74zI*Ua#)2V)Ju<dA+*7ih1rY<<0ud<ot{1pKIUEcKgV$^pD4zxsUt%L3{H2d~osmzTSAc@m}BYjn41!oqs^p9c~{{^VF**{V?4-eIk4x?Wc2=y;7y^$m)h6s;m)bqz`rdXpWHLOQrvh=8S6bzxvUfmd%^}e}6QmsdWx_Srtz<fJNR0$HO(rO0dYA;hJy_vLY<<R#@cia1HnlvI#7*DcqFreFs?+{==#&F@|x4jDt@aGOv=tU*%YERjZni31l3c0N+VgfrDgYvI^W7u1tz^s?4$A->o`Mo*@5#Pryaw6<DpIh!VV=61;;F93`*9QTQ4u)^?3!!PQ*ruSN-OYE>7qGuZ_040j?E;7)Kdc_*y)E142JoD!T$3GPTXhC9NI$jWddxDqM$u@c9EFT3{oG9~z!Rolo<$>Z>+@Mq)+_%k?%EP{);204`AcPYVZ$sO=o_&rMSPBIGbguf)O!C%6ElHxl3$+6&DxOPq9Tj0A~*YYk(@V!<|uxg@JBgs+lD1Ln;*##a6k03k4<E$EQRXRBW9>JJ&vJ;#Rr;*8UGCh$-34W9kJeEv_$HHT*8chx(Q{hy4Xc#591K9}f05>En!42V?Nzp?$b1e80eRT}J1Q)vctdJ5Mv1%2$n%oAjhS!jv!fW8S$<N@o;djU!IEVfdES{y}xhS5G)*mIt5Uc)5X2Kcp!{iV+#j3wp^$^^j<Ds|^oWilFd+;H+J$VP*9&SLEgB!rNlIIP{x5B>}GLOK&!C#Y~z+c0=$hY8K@N%mLS@on<f29OJK|T*Z0Y67BhnF*t;K8ha5E+7BW!!Y~d3ZWJntT!-4L?K<f|ps9%N)z$UF2!kx=yohk-xh3;aB!aWc8Tq`&ONO6&W9MeV^mG4kFvRu1h<vo5)AtM_8}m-qxI*tm;JuVbL#L=^4S@I2ONlKkK}owJH|Bb{`ppUtup^C6~kEE7qzQN^lAC2Dk)VlDrWv36~?|;Bs(PvJPAo4v>xD0GvR!fD_<WR`s*0t5pwDg1eCI;V$q!WGlE8^9X*}s>iK*gc3Z4d=?%9&mjK?o&mo`{u6!;-b@~bH^T+wIk*7+iM%OB@=vh15F&3^7X_|CwuNiJ&By_;$ot?It>69+t6nBox_CFoE8#ulDR>Y36?qZ<3jT$x5F=S+MYxAm-L2|LJ^-)ad%r}!2sgK?nN@d_ZQ#4%Wabg`b|jPGWX1^YZ`DAn2EZvC_vai^$nLIR6FH6Z5$89bd;y*hPbH_p)A+rD&xp%pt^H^6Mp%^K3uJj%l;DeG1$eSmf3s=|C3qeghUdXc$u00wcq@4b-U=V(`yS=Ij^fpM9%3D5;JxG)crUz;48!Z-Z1Qh#HawG@49|qe8sg`#WDX%G!$aV~<P>-?oI*`u|EI7oQ>l4ew|VS~x{gb^&P&;se^7#VlSkp*@F~~cogy#79jxkRRXg%txE<V<><qVs+faf<-*zYake%T^a9{FXxG(${vKyRemH59>no)x5k=5aP@GWEo_!hW4SsE5u3T|jsEvp(+f@_nN;o5K&L;M9@W*M?FTm~*hRc8Lm%vGMM#d+1@d#m$o$U2&lNn}Gf32sR?hFij|DZzJ=wc$JAx?~l&E?mvEwrb=}a7pVv{!XkZMwa034VnAl@8LZ1eK-&Pz^XUMMdbVNBKUPm@J4b!yb=C_{0{yC{+1Ny`Yp$TZ?LL1S%)kM*MS3MDL4Svr39BI#X3uKEcgf3o(KN`A0R(~55OO~_TocI@ZYU^ikw5f0ndSFlZ)Wla2EMGoCVLK1TQ2v!VBRI<QMP;cpv#Kybu0{6#MuM$AU|^_PPWmxRzB(WDBx3+yZV%)`45Xt;hh}3T{o-g<HdID8co}(r`Vv3@NTt8IA@2$hA8F{|Fx>KZFm$ACZ5DKY|y#uH|C#X?QXGCMEb8t0s||<kN5_oIySXXTTH5Iq*by0y!I=0FNiL;PLP{auz%eev}eyk_%xIUO;Yu7r^VueeintbMhPbbNDPN`sOUhf@A5WT5v3Uo2$2OqXZ{Xf_qScA0S)655PUimT*tF7ugE#1@|Uf!@c1?WE;2-+?Nu3H(3w98?H~5f$PI%NzsdCITrjc`tu<CFF2q42+oH;CKtnt>A#OD!J8<-OUP&7CGcEVzs{uuKW5b^awItk9tn>iGvN_%I++2d!)fG1I1L_7PJoBQspNP#6&^;8gNMOG$w%R#aEKB-mNen9@Jw=nas9KO;B0ceas9KR;C1BZ#`VvZg7=bVjq9I91)m{BudC0lf@A3a+u#_uCYcD=gqvG+KiQp3gcG?px>JH5qy+a9J=`NEHm<~f`d^5zf0;4jzwZB`*!w&6f8KEa&Nr>OoPX@-)1##L++_VlJ=VU+$>I~I@o&~itvL'

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
