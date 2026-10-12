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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/63695230beb44ae68650bdd4d914917f/part_011.stl', 'relative_path': '63695230beb44ae68650bdd4d914917f/part_011.stl', 'source_sha256': '9c0610241c2ff2ce38e27120d428a8b3274b5be440f234f2adba4866b53b92f0', 'input_faces': 336, 'input_vertices': 242, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2105851024389267, 0.33336174488067627, 0.01797136850655079], [0.03954373300075531, 0.49689847230911255, 0.13332340121269226]]}
GEOMETRY_BASE85 = 'c$}r033N^8yT&(aOj}WNTO5j1s~QqoHDs#@nubWJq11^CsG*t=vu<LJ#t@Am!a;->6C}tWyQV1G7}_F=qX<$`_4lvRTkihe=Sg#N*S%}qb#K;s*Yi7%_q^Y`zwg`AX#@Q$JXcG@Ut_KFf}G)=bu~@J^I9z}DlB6B$dIteR%6FaE~mMRul`Cju2;W+z=7qoC~c}oXjo)OgvWa}kB;H*dbG58gnu3}J|cMR(9a`6!<6qAJUTMW@*_tCj|;Otzuv~XO-q|si<Y+Ow*TW_HLC?@<iiuWmKvw}{pe$<t<LaeO6^bIg<rG3`1<I^@k+Ij8Q+S3556PrmsLuQY5m|ox+cE4aMEh2Q?-lu`r_t4Nu7Cz#n;BpJud!85BQg-uN8lCY@YJ9phx1HZ!B0Z^^bg%E%i^Azp6ev>+epGe}DJ4EU7c9=@t2$H)W$}y=?Kd)b}pP_j8i>i~c!Ze4~=zW$AB{TZ+`{-3a+(I!GPI{nRAsEAMuu)VF1zzQ@!J(x>CB_}cmGpC$j&^d0i=&&MGDQ3n~<^vsfR_4pp*8wq!1T-%_+&C<_b4Uk{#Ep@c0%4zbw;3)^Be*6d-S9@Ac^6eiE5MMvj5%o9bOMNZ;ZSjqQcH-+3ryp?j^(}5PuCryIo$|d0FN<$p@sfO}{Rhc+EPb+H{6~41pXl_hq74hh*SyEU|7_xR>Hp?1@r{i+m*jIsr9Cq4l-9^!dRC50e=#Oi#x1<FPyFU>(SM^`GOn4D20x$*j`zgGZ8FaC#o`;Cf~AhR<f+V$K075t^1ZstxMoeabkS3j#W!DgOX}MKwJhnYeH-Mrn}K<5GiSGGa#6bEU*00eWrjc8CHafD?8ScDf^nZTmg6#BswTd!wSez^bgzu_+m=0&ziyz^(d)OB`VPluX_DUo^RHE#Dfvd~zEtsJV`V?<Lnq3<H4e8CU+dNieq_^R`QC+fyCnbh7UDbl`^bK9&X3%M`SC}7lcHqIbC~#Alka3coi%f|NSzi1J0-vOBkc3)Rb>C`0f)rbJo`!=^TbD+U43(Ii1_wLn@~S#0P=e#NF8I&U|BE6ab0|UWuEwY-)z}GdW{<J(+8u^b2-Uamz_JruXr4NzI$HkXj+o^M$$XTcl${CG#+<H{^gO_C#@^Vel{LCwo9LTx=FtAAB%8aUz;Jm)*=;sh6c#`I()tmUq9swe{X>7Pa`n|eyks^Gk&9F-i$YT!=L+#_}c9?vj6Q_zipFo8{We8;dp}7w=Lba4f`Y-^Dwq4&g<MH_-%&ac$@VV-_~G-_{Qrt_|L6I{)bD%*W4Rp{u2+%bw(>+ANh6KqR+j>(vKtWMdVLCBz5ebVQCnr9L7zqg!LWdF2`$Mc3`XYe|7-oAu~(%t?irL;u}NSVLq#NlXbN9T8sSiH<9n&CJpD2_g2?_jHq~7NAuou$Pe}s-}bnw^sn!Ik|MruA^Q9~1IKIIlY;ZqhIQ}KUi!3sxhchUy|hv5aUT6K7Ilj1p-x~|TnG9F!;ct%aeK7F`8cU(ifjK`yZ3OsRg1Pr{eNM7^}`3{e0Mqu#n(DzVSO7!i*I{&L40HIr&zCJb7Wk7Q-b*B@Mq%NE`E>sKerryP&2I8v!}9e?H*C^Bd?;Lg#l8>@oE_A|1}5mywp>C=e|1dE2JTRzE6hKS$Tc4_+9H_f40q%dA6rzim%7b!akhadY{xc4fr2_fI2m*<33fj59;tfYcAh|b;<Wb{`MNE6IhJ<=~Ex%r+DMIhTM_)(c?RcZw~zd_01)i&)W@9=gsPv=SF|Z`Z|o4#n+nDhJPjq=VMa&GW|P(iew&amA58KzVA?+7YDp?-|03|eEse3(0}5oMEPD?W90u)4*RpIH|h`j_a^Bxm+SHw_LY{uLwv2yJ@g;C9s6hJ6!DGJeC&rk)nxw7tW`<kSNQ|$_0nwgS$(Sb+RRwgiSo~I_4UWNZWz_KVV`swFTQ!QBKo{C9M_-GW8gO$i~ZIrLDtcEy&dZCx@7ls$No9+V58*E49ETAjSe`jx;MqwBXGSnL;9otYm3D<8k|ObUib7Zb5Q4)i9UIs)j~fLUn{x@|JYsJA5S-d|M_b8FKg1L{_GWu+xH>%&#--)WFAf&+aP{n2=e!xk$iLAEb)yIozZ8;Ls>7~^ELR(`{4YV_%@!q{-`Iu_9Cu(#?zS@uD*G+J@!@pZ!!<&noH|t+ymdDPL~_fzu6*Be8UXIxW)v`f1N!J*ZFaTSCspsmiWH-TD2E&opD=_`5)lna9u~+p+LFcIlf)AR_c`h1%29ENT1q*uhvLEU*S2^XqXN^etUxJ@tT9`$#vEFT;ysQclLPnbFB}adwpV7$+$l2v5r0aiEm4sF8)8)tEsV=e_wr->;Bi8pONQtGqU|E*YiaiH+r4))vwk{$)6g8^Q-$yc+Pi!yh41>xGS#5Yfro(zOJ1_|3^p5bG7r-W#scZX;$tb&(-FWpTsvZ1F=tD^^o~@4*V8=#&sNT-*6n)&Aq6zqczT#AgA=H1=PT}J@C9?OdTli3%2I7;>G9v-8RO}A@!Z%;v4;&;CLI=!1I{9UHp>gA2X}D9Iuh+k2=3&{%zfc;5q7~FZ{R@xF7xNzRZK3oc^`czmNN)9y|xfd#H=}TGD3BgZ94Ev0eLax#aKaf&O=VA$^*6-ht2St!-fz`fOcAeC-DIp^@Gi?-v(N#JQeFI`0er_~URNu~%HO)zvo>I^lZwIo93u_gg0UYmT5!szdgnQRz+bOYZMl=ux~kjX1lsOrPB<<9LHom%5&h+AD*le?6nW_?rI{)c0N>{g`L3FOmF``{q^~&O6VamS8_8W8Px_#B;@K4aG0Hk2p8<mig4WSNlrVMZbgm*Lq<dqMIxdpZ6n2W<AV9=gROOZa{uitXzMz$G^r%KP{W1|APs5KJQm^p7g`}rm^xo>b#XdSL*OO<G6Vb_nnQ;W=o&EzZgRX;JGefqWI>gxNbNP%|idf(`QLOueWCVkI_$%+cc?Pa^3i|Ca&|DZ6`^-`$aw%Ipq0Ji!P3m`n;aoI{uA1;|jV;elhP;$Aj@)x4mUQnb(s0Z@br#-|H*8_#fdqso#7i_eWz}=ehEk&k5$4Us30ATX~N+=N~JO&vB<r(X1%E-+LsBuWu=aUwbe7fpf$+bKJj?&ja$s*Z1WXU>;K>Uk`D@@A@<R=qUKRpO<~75BpMlTiXKoo^9Y~XCwdBh2k5xf;Zqim@K~i><0AncQoGn{|rU{Cv#CJd>;1o`3LB8RU_2tvJUwV0&!f`FQLwj?HIT5GSoRX1^Es3A%8*^{KSAVzVXBj@7JSK56U>jImpl5Ao-59p~$b`g#Y~r)bVv-+#d@uZnHqCWAmPsDSoFS^#6Bz`0LNf`?8*V5BXi2if@0hS&rnVJ%u0p0p{&SJjR__QO;wnRe8yGc#p&LVNn&F-%TfBe%_hHb+3;5)vo2}ziziOzIOFT^gs4=u4vPm$nRlCos}yw?vMtk-}Aos&Q`x;ep)p}{>HuN^UhGYpBkrIBmZ!J_|0ZZ9dmn6_-`zN@7Edq%m{?P@>Mx5y^k$h@*921d|&i)wU6oQoADJf4-fvr?=!!L;<&ypMxSXx=yO>F>Ld<8o!kD{SEr^S|LE8<`$2DOz@Jb->TB=a&vy0AL-jCjy~He6Uyo>j{qw<_vhIfaO5}UqM*Yb#=<|aO@bmg&|3^Q_b@h$hBKR?fu^;wqg1_Gn{TIy7E#t4id};?PW4-R~LjM=P!94#`dw&_<s3m<muhvKZu{rR4Lojb0QgX}qzoz5-dN>s0uKFJS@M&fG(aWF3am5xOKfuKM&V)kv_h;g`DqoUyF)rUho!j{sclX5{?2CJ4=FQ=?9Q$GCefWMok>6$XL04ZN@)zbIz6H*^x(|_mYaZ$}bd!Aj_7jX-DG7Z}&d(|1pZhoJED6W_^m$rlpBSwMNWR&)qTGj#)tTt0>lD=aq`LT;{Tk}j{z-m+(~rC)zBwX}*U#?RuD&)J>t){=Q`V2bdFqTw!|!Y@>)`%>=rra(tF`!AxDEMJF`s7kewhdT9S`JpNJE`Y&!bLFpECK5#orz92`uw#dw!Ez>AJi1RV%7$wY2bHm!H~|ss2jzzyGOyr1$^or*<!|cK_d>+TXQ$=xl`#^?kC^Ze$;_A4733>IY<{ACh~K2Qm~7ruHE#4ImFD_h%^XLG4afs*`(=J1`WtrM^d2+Me8&+=l8+R_aM^Lw<|eimdbv@>}E<48_f<9%QAjlbe&9F%-9?zDZWvn%t7?MSX|tMeaoHNbbnB=|uG-kG5ir6~R_~OdZ7d#ERZld_)~e{e=7p^M*1Mhf#ycVdM$aG2}5Edjdo8REFYl)KGGN>R@UpIh1)NdqeR+YOq$iuN3!kInG|xL0aiP9K?AU#N#a4!@W6IN`1+1a}C;2y~tgtU8!DVFMh8p)tBtcx?Nr7T5%;SDq8UzwE|hAmZMf6S72T_YI*WYR=jM*i`1Irs?^%ln&g_yt4(c4j<jN|6`wJNSrKBz2&&zR0aSm6;y`K$IglJg9Y!9;x<L%ZeW_!~eaZc(!^!=r<EX>Q!<jdZp}1s^DV{=&Bu8?*DGbGvs3GJ@<nb=YKb~qQk0+00C?4W6M?<LoWTidH6Rr5%ipdPcpE4AOQ%8}%phi$fkw-Bvf}uEyp?Df~B6%Xmn?_wuu5LvgE7X7OtwpVG#jDgtn!1faUt=h?QR|cI^Sd^N;#a73$aOg0D-6Xo7>b{#x{)hWt5Ds@Zp^E~P+W~#mt2kfg3GbJK&?-Hf$YvuT+ikB>roq#>yaBU6gP31qbAhX$V!`%Pg-%*iX+qvveJFzBjke&#d*{N<l|Nxvm)P$YgU{m=abJ;uaTAhLOw-3NBxDY^cGp^CGt7)57b*^r8mgmQ-7r1AYY{xQE!lcqZU(dkZ-VVG4&p~n0%Ldi+qcH-=$t7E4@R$OD?2dBj2Pt8CR_M*@~a2rx}XRFce>;ULjxM_b)OOU#1q43pws(YCbui>v)-=IER`=&LO8$kCD^K`x%O}smIC3IYu@^@i)}7<ZsBPR=Ph->N&DW&ZYi9&Ltn#O83EG>W}2Z<Zl^@3$)VxQ9vys7m$BvD88?i?wkA6V)A|RuhhHbyPWr58H#UfrE7ni>LlMLU#I>|zD~ZNmF|xV)YIe(<nI`Y4^dB$4^Z={C&(w5mq$HAK1e-6JwsM{Q7gSxC_c$he3W{btTczLG*c_R_9)#;%_L_sZ!be}8a17)_S+tQR=V5e-;}0OcawKBFO|BByx59mRxGq)0d)~W@lxtC@+vFhtyoQ6N?yvG)zp>b%~ou+ViRMd6%H#lP?M<}$s3uM%ut*{-AYa&Z>Me}@1*XaZX<7F-VTQ1Eeyp;)Xn70950EXcpcS2UPn$~C|=7@yvF4?*HBlJS95;WP?wR{kmIaKv|@!7Ut1At#S-$@<gci)WTnyMxzsPI(d6mW8PsTUG`~NCI-5L$JdYYnj<I46c^-KtHHNHoKG~qoqRuBTqAp-4UPzr!p3hnf8HyJ(VmM#R$Z^zp<az8lj`}ruE$2Fc8b^*}P6BlWc?H*_WUUpK>;c6|)b->*|8nJPRrsI&SHIFfL%leZ`5*uO>o?2(Y~lLNu~w~re#8j$uc+Q*te27U@}PQ0z42=Q2@5@5`v'

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
