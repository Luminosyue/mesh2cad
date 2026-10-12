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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/11ad3b320ee74185ae4ba26ddc910b52/part_001.stl', 'relative_path': '11ad3b320ee74185ae4ba26ddc910b52/part_001.stl', 'source_sha256': '37af8b82e75c1ecd3eebb4369d7e89c9e58f307debdbfd2ba206a298129662cc', 'input_faces': 574, 'input_vertices': 340, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0709121823310852, -0.3120002746582031, -0.45386236906051636], [0.049769725650548935, 0.2756817936897278, 0.03151857107877731]]}
GEOMETRY_BASE85 = 'c$}r133N?Y+sAhdHAV+h`>MBB6)j3Dl(vRTVvI~;iWnlqJT*yGO+8veD>O(<MT8*KJQJ1NB<3KAn8&MVX=|*hl)m?Q_Wz!9_x`+Vee3(O)?UBg`QM#=_dUZt&pjg8zi^RqLjF_{g9kla6=4&CT4_;EjEsto9oQ!-rp~YtUwVmGIHw;s69PL01c!Nvkz!1ZzELrKqHBC&tI@b$qZ+ksHTn&Yj*ad;tk>}9zEPC7>OCYT%9Y0q=shCJwf(M7{SRu}eBP^V8)y4J{*<IS1k~7+;ev7gu7fBxZ7Co+Y8T;Lq&}4S@tMatubjD&Xis`6lX<Yu3C~>2Je|&Yt8^YG;*Z^&8<Pv<INytWqBAW`_Aj%Z`x^rm@c8x%qh<e!sk?alQU;IXT>XXYzjO!p7xzY<Q1Zla+~3Gq!s8fm9pyN0_;K#IJzCB)vboH2OUU`(@H^?5izn~yV9r}A=ksAxnK#Vh_jQc5$@wp=FZ25+wsXI*&v|@f`8zTn63yc{&hF>=i`XhMzqUY*v%NXLuWem9nKv%N^Ar<XaBja|OwM!HS91Ko)^eVq&o^+tORcvs_xI=bwP)Pt+$fsPxqaaeJpYL9w`4y4;%4TzpYS+F-f=lj&9Xec`1PezJfFq+GQVfv%J0|YD9_(EGF|4sq{w*|H0Ax^@Y^Nx&d1aEeaF1Q<2WyG;oRPD10Q!=Uh-k?KYpF;->|sc{}(H8e`89L%)g#3&!6U%Pswo?$b7btj32?D*LG-v+&({FzR$ts^7A$wAoD|MJRjrk208wwK)D|l4dMOjD0+%Nm;J$qGCwjvzVG(k@_ieX=iE`?#q%_-9+2bA`fWYG9@cXezy5fQye{fq<=kkqRG!cAuOH!lw-?F&4c_7XX<wYg`^|W@r_B3TUd`Ku&&m0;e7=tJEon)dJ7VPVy*W|lM$i&|zaH!5`8jpG%(pI<pDQj)j=w!;E$1cLq%e<OlH(t_wnm<h+5Eot@=oq=Uv^C9H8W=^pQ}_^nYZgYm-|KD;Bkz#t@!taPwX=8_pH=0&KuO>{URJ)=JEFMPRHbRvtnU0%7Z3l({^&h_HoTTa=Y(hK2Mw#L;863H-?Xt*LB|?XDNADI`7Zq4zrgi<NH?N<CYv-^hYHRE3%yDpA)!I$-5O#<o@S3ZB=sPs~$YBTh-H)yyLfXi4kIbx|$DJ!TrBmm8s-SA~z77vtHh#<Q*cn^5<U|w@=CYzMaNQt$I+&N3Kif&%H4}N6G!-GCBV#;i!_gUz^S2U)hkS<ejqja{n8Z)#K75XFt#Xc6@=dpZo4Q$ge*renQCyPtW1}>C}@-9^K>!=Ux>~EBUDWqdb1GRcAbNdq(v<o~L(<b9{Wp|03s;b%AqH?$UX_-Y0BZB#&1^-e00iKkgUt%|}W6`$0STys}kWGubm2fn8+Yc3QlW`{m2?ZNv5G49{^|4CmZ_!25mATzqy>-baQ$N%YK(VHG%cb{joI=^tKw8~5+Lb*Ykf?IzcOz)8u<IDTKt^=4GH)k^<~eR-X*k9e?B$$MPo^Eu+k#f?hdrLnvo4;<Q{<Pke&^Y+E2+myURSH7;2&(_(h<l=Ef=ABJxYHlCG$L)`$JC(fsj@g_S`ZPoRyp84)ZO`kZD|z79<$OG*-po|;&VH$!e>+gkM;%|!*HJ>q9wl#fQeIy(^Rtya=;tlO<V89AlsxpLyzUkRsd;45P97(<*Fh!kpCqrx6*mqjd2DrgJ#H#>Se<9R41V7Y3v!g>+rpQx(}>+UN0t69b2v}l)kDb*|0uqG?N@X1l>Py?IXAA%RdOSA3}4scw}!{m{aI`u^F|RRH^L|I_3pU6szB-A^W_7a-}*wyjXuM99WWkLIiciHUWd5<{kzANd{8r9AM8(;oK(gidV+JulUOA;KD&LG=~er*(m!SjuO|*sNXd;aCh&UVD7O2Il7Cq#mw&I=95o;JOy*@eom0kl1n@dzcz>YeMrIc0_Hw_U_ss2CkFYKkaBfW6C-d-Bc|P@8A-5<0BH1mR^W@+;KX~RMtSslw9u?&KeLH8dJT94>8{PUX^2|l}beTt;l>J&KB)_mfa(zDT{J)JO!l%f2wwgRo8Nchby_7qAswOLW@HM{P9A$@mt>gjk$@R9*!<nAB!|xgDz<0-Fc;?NUb8Z~#*;5%Oy53Kme_nE~XMbaetn2K{woFs<?xT5KvxV<X@ytc%=UfllW}i(``nNnQ>x8lIuTlCNYq*|@7<?gB$$KZR;5;{Slahx{l=apArW=&J-|IYYr!#Atk_SKL`-J`U(k)6ZCUoTOdmrsma$9l?(Rri7P9^v2n#jkwNJfT|cb~`Snd9lw-AW#Kco{Jwu5Ol+cl}$gw^OQRDtYWXa=lGV*rVjl>un?^&xp%b@}Q}5y-o7oujHNTZR7lh68qHs*-EarE0-Kp^8Qccdb>R3fRe`?+s(&qbHHIGA3asBx9dCQD95+O8?r7+_s&)NxB5%2w`p%2Rr<I4Sk_BdZ|14{t@0k`l~^?o4dM0H{#(~$$~c`H@Oo=pznri15AP)Ft2>7Zl>R-N@Oo>%)ltnOeP!MCu*C`WysFFVt+;>mxRMVlFYB?tvra1G3@yy-s{KibnvcllToej8tseKSyx!WyrBh1(k)34yR{Y`_B_G|E*Hz=C7&RZ8FY_`Z&w1u{M<2O<dV8yR=2}??mMeY1Gk0Wp=kqvaH_G+4^#VChtv)o`g)ZTK`g(|5U-z8;t2x)#XLqiz&-V7aWPg2~4=B8p=c(17?p&`w&0MQL&2hB))9kO+pYB|*Kh6GH{b}Y}{b`P))t_d6t^PD~t^PD~t^PD~t^PD~t^PD~t^Txfwf;17t^Tw=uUdav$3?9_&0MQL&0MQL&0MQL&0MQL&0MQL&0MQL&0MQL&0MQLt$C{Tr+Iv}`qS*M)t_d6t^PFoYxSquU#mZ@{i)WUW`C{zH2Z7yr`cbtKh0dLKh0dLKh5#A`qS*M)t_d6t^PFoYxSp@YxSp@YxSo&zFvO@l#>1R`V+Zcf7$|l<v7~+Vi7ckb7$^-`TTTt4xhKlK`F9--UInPKXHnZJ9Gb(`J7j|?sEpMmi@K$)*hUL^IUzN<IeTxIqqD4o@3_P^Bi-0?Rk!wYtM7cTzj5l=GyZdGuNKySh@N<$IP|oIcBas&oOiDd5)QD&vVRNd!A$F+VdPU*PiE?x%NEA+|Szc95dIR=a{+nJjcwn=Q-wa*PiD@gp^8=$LpM|i@yJd>rY2WRhj2K<oP8hwBF;HJ9F>J^KfnupNFD@55_se<2a`8&GO8RunU|=#D6U7($EFye@gbBHZ#jJH~Y^RD!<2c{9T!kb5_MYp1CvkuKYecZvxN9*4cNN=lJ$%{j=2k66ektbLIG5Qe^HMB-h)7CUX2Pn~?`_ZcC`5<sqDl#4hqW?RrJ#d5`3LW<ARG%-!>}&0n%t>5uUpvr4JsV0?SxaQR#%tn6|*{}XclaRFIsE<cwsbEEuRVLmeV^_TY-%*V<@<>yVDz~kGx`EqXGo5FQna(sY%Zqv<Q$(`}xFU%eB&E)vq1|wg}xjo)T%a?I(n=w$16P}>V(?08WEtm6jBu?MsnOoz(m#yY<{D>JbvcBt{t@W>}<+8sq<4ew+-JdS^JdW=9xN~Rj9URBidzJo}znJx_I*xW;S-Jaj%~W$7-{d&oEHziJQ!BrW<GxFIU-##=#aGdC_4r!3+z-h!#>l*f&x#lAH!D~7TXN4nD_(RQtz12h?p!~PR<0gLd#^aHzmJxy=atbbWyOomTRnH5x5>R$E4h3B*dwx)&*i?3tX#d0k|VCHc+qug<?3}B(YtJ_=lSLy-<|90hS^_RH>_M;H|&wVN`Ln{X65QSW{(U_ec^fAXS2+;b=At%b=4kKYNh;K>bmXD^>y3m7rxSSeDl75T)!`f0omxU-FJ}d_Z|Cy0%bn#`<gq~?`y_@-&elqy0Z@oT_wj+>oj-%KkBqWV~~5)d%?<IC;T|Ad&dElTr+pI5~7^w*W2Sy6DZ`51-|%C69(4*U;Sx9gNF70zkiz0z)OgRuGRwdgKu%o?JHN?4vvR!hi?YQ!8gOVf(D%UHGC_42RISF1D*y>hNr=Q0>6d-1WyO2!qedna2nhJ&jP=PXTkS?GvIsR`@mW7eeeTdBK!dS5I6^Z2!0rx2R{ry3jP2;3eN)<!t>zAz$ExF_;D~9ejI)hTnax4KMgK}pN5|WSHRE0&x0%B=iwK@AK@3_PH+v}3I7>f2mcv<)zy9hH-PKlzkq*$o8W)Ie+4(f>0G6AcLKN#J^}s>xD);jd=j_|J_$Yr+zp=s{|?N6e+Q2PGvRUY>0mZ|Iy@fS3y+7-1oy*d!V|!Q@C5j5Fb6&xJ{LR!p9`N4=E8r)KD-95hhKwV0oTH>z%PTV;g{i;z*X=|@C#rn`~v(OxEy{Ceg;f|pMjqOm%vZKPk@WzC*TF(B6tBjA6x)mfc=pV=E6t0+880%JmNSHr`Ns&Tf>QU;a|erfFHoyz}tZz!rQ^ygZ1F;;entJJP;lX)`thfJAe(~9pD|okKi5Qoxz6i&hV~aBY0PMH}GS4H+XmO6L@!cPw-QCPk02_7#;zS1e?Gk;eElT@V@YVU^93>_yEuj9{?W&Hir*_4*^@ihrow{zVKo25uhJ@1UwpS36F-yy4pyv71$C!65If8g46w%?zPv!t?=vco8S)kP53P^4SoxL8~h1=8-52&hu?wU1s(9a@OxkuoYrkxqpyO6y`*1-{|pxLvhD@sPSDHCx_6LY1cjG%uOUAV{v)h=6Zu*2xv=hK<fp-B!n*g7p9KFF*1eMaIQUdp_g3;_;1glpi^=oAzl3$~CO-;37S_F<{4n@PShWH9A@HHFY6<cK-~(aR9_0JL`@*VK$oGJM!vDna*#l<5>D;1w?npH9Sa1zI79I`$D6I3Dd<3{sSm!_aFmQ#it{3tl;4)!dU*v<prNX)%$p?VR!n%IR`+-Tqy57nAf(wPUK9EO(KL~3*A&&s(32Xf!?+MNk)_O(W9ZVF~`bORjoF%OFki086Ls;u4d1vr@VXe319l>eBTA#@~fK%bbVE7lV_PLPv@Qv{GU<`acd@cAHd@X!6I2^tjz6u-)C#J$_jcSSa{{sFw=m-BC9s~NqW8j~GE#RNQhl9=G!{I|gJA5d7FxU(}7(Nhe3LgmX4>p1Khev^p;Zg8D;HU6D@ZR7j@ZRuV;K%S@@E%|zcn^3u*bp8L4+B4fhrzpm4d7kioxu9=PVi9B2ObI!0qem-;6dPr@E~{q_yIfs?hn?5`@`FUt>JCqqtVF6f}`M6!_z&FYIdqosUCIL|KxNJAzpz~BQFGAhEpT=0x!X-kqhtwoErH*$j-t4fj<Y&z@NjPfv4cl;D3WB;D5uPf(7uW@F!qC{0aOoFc<z8{4sb0{uurU%z;0GKLiiLAHpAi`{57Z_rbmJ`|v-(Z1|t>dtfH~9{ettA*}j={0_KVSoH?^ZE%;c>J#!?;7(!HGvqhHZNjR5$ghLj;k0JbvjcaXOdbeM7FJzN-X5GNtU8>$9r(4d>UQ!rpdqX}pPar2i~+}i2AtMUS~oX=8{xF3(fXB&M!p;z2wx6Q0sF&K;7h<L_!9VHun&AOd=c0iz6ibm>;+!{pAYtc&xg+i!-e(TlYBN9CamwO<OyIGVSTqHp9yvn)^}m@cra90-<`>)gCWBDu1y{X1_|rCIr(>BfUv&HlTQKth4tN^d=l7JSkDT`zX3-J>)8VN1aK^z_?3r`!ZvX{JixX7bZ|9)khVj?V0b7z1Z)ovfd_)^;DPWqU@LeVcr&mGycxV2SQB0i{u)>T{u;a#=nXFgFAA1`7lr>OB#XhRk>3D|z^Re{4i<+~BYz25N%%|f(qI{QX?R(%BD^fTI#?TC9c~Ak!tL<3U~70=co66hcOOggMy^)J)jk0~hJOU7tUk8MKft!ziSL6|;Z@*u;Ka({oA5WW{V%W*yb`wm4ZaP32ToaCY?FV8ZSn@#CU1!CI{1tY;l8fc+|}L%KZO(P!HG5C#JAwY*Wtu+aN;X);>&R2t8ij@IPncQ(FP~J2PgW#iH+gJ7I0s%B^tRO*aA-15nW@o;KU|q<TcUAD}dhc67X7ZVlg!GB535r!IJPY@LF(UMX)x!DV(y_*e3VKb}h`kJ)9T}CkDU+@H^zyUDsd@SE~im_S<mcdmgWm*9PmrYhjz(`^d>_Vw=XOhO8QLx6^BHA*%*|3wdQ%dl%d9z-xN+q1VgeHQKI#_7-w#Z@SuR==&zJQlPi1mGQ_bz}?wv=tC?AF9j9{DSs7Ce8uCn5@_DYsg-xN*U`5;vJzl1kY2CkvHddIE6C~ff5WNS1pU*M^nYXfU)ZjK-z6`JRtc{c!h4hiUxs^On_e#pr;L6I!wcgz@|W<LDXWNW^3vEYj8+`KQySYv&<bPhH(aeMva0Au9_;T`s9fRy_FsstAA=|9`5%h)-&Fs3&+|8vTw|I4*ca?yls<!N2NdEjvd!rmqxcUTW_Kz'

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
