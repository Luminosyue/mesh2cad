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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_007.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_007.stl', 'source_sha256': 'a09b420c8d9cb9468f4241aa01f756307595b5aaa654122b9b0211a6568df973', 'input_faces': 378, 'input_vertices': 257, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.052585452795028687, -0.366482138633728, -0.2725142240524292], [0.3284217119216919, -0.2657351493835449, 0.11578924208879471]]}
GEOMETRY_BASE85 = 'c$}r02~<^eyT-SPngf|-Y7Tj<6dXcx0tI!WXabUoBF-E{2xmdW6wz%?XgOsnd}W<foFPF$$f4ti7~#O6pEw*-GiNjPGd26p|9u|5&bjN}weGr?wchpodiwM3cfbE(?{lzUU`3bO8h)B+Pko-$POhhEDr#u8wfM-`xG@otQ#>Y4o?bzFRebeRt}8zb3F<ebf)=kOxQ&jS5)tdx+2rOE<>l7O<Q6q4HZC@NV%VhE(UHpU6+V7Sq}`tq9X>hI{@?CxJ9xG-wQJtWlxX@t{!~*nB;4NG%`T>DqfY-|SAAZWQ%bcbkGCt|e65H0Ms)s3@%y-@Dc|zr_wX-Gmhnc-hv|~1{~+WU*$3nAy}U#G)%(QP8fh3ms-O7gHEqQ=4@^2CzgMeEhK%o<kMZW2lE=s$Bfhznm-v>d(+kCK7n7-cExeKVrlSjf694`~_|G!Mx9zwk`L*NzJH`Lh9sa?&1xl^A&xvo_xgUA9w#4|0zw8pfjVrEur}vMNKP);+eD8Ire`sse)9|+V=4UmL$It(`<mu5lTl^N=kY}X7)M@psxLbVh>(Uq7D3^R0U-CqJQ{r9t@z?UCKb4#0h(9|)e9OYSR`C;?!jD{qdXE1ob!umyiEm7pC*!U43xAOD>+9soJkB|U{2g~36@Ot*@ogKwLj7~zl04SxZr@Aa%8uf?M}m*Y|6ky-NAj$kit*d8Nc~2fr}(z@Dab#i*<s03@ptjH1<A<c^2b4`^MvbO$#Z!D<|S;yG107U`=mdor^|Tr#VRu1C>$WZDIpx=bHmY}KK1s?_$Oo0hk2FdzHAvy#kcmID|t+xR5&2xk2d~6>PZg3_!Y;cP9rT{d`o>_%-1XNhh)4@N2~JnDXnn7-IGv%)>!e4ke2WVjgkE3%<P}U|5QhvwOnL<Xm@kO*V9j79|Z@?JXz!13Z-x1_py%}KbL-)clQ$C{PHrXUw?2~)}<xmIsB9v$n*F%)^Tu+6LOux3fONmM@W9#^;+UvUU?wnt$RylU0OB=i*IWig8D~nkpAl3lHmU{9eoSAAo;ENJCWz+E!<aBA6Ylnk+~TE`W#&MRI1FYUZY5S>$*$m^TLL*KTUn=o|HN}=tWYGHWvG>thM+C_npx$0{h?FOMFX<NaVls0{begtN6BvM4THw3uV3PkA{h_m-a>e${}*@*p5VqZ_X&fzE~cL`U?#4P1Bdjc)ep)-0!eC;#;%d65q&;N8i>jK|Q{kQ0MPk<b2cu*WteO5*e>$9GCkw-bjUCGY$Ex-26^{zc>s2)Lh)xy%V^u$0_uoY5QX7|BafM-$SLiuh+iAJdQKTd10-71$mZFL7i8V(NFK+;k%k7k727UeXxA1os$2*7WJ5q<?V9vcQ!yjH=mbvYmKTSzIMtgd2BB8P|x@V;#=K2qR+Q);Q4XCx%j62kHxnPd`I$FR&;{@FkSL!*<VXN+ASaP&C$VFC*GY=XR~g&Zb~EM?^b~OdJrSNK455x^iyw+`cpsVb(2v)`(_-Pjy%B&<+>KzEUCvdIRW)o55l}`e=K>dooAt*b9w0JyQgJ-ttCmwpVL>aYu>a~)~B{^kNB2=?@;IAYIq(jKaA_zYQcZ^HO%jgJn@ZN;poH33bG!|Q_65(b)O->%kf=~zA2)K_||2|@ErQ?5$X^AQ+(622<)%^l}?Ke`V044t2O%UQbT;3XAk(<QzVa3_=@<(=7pHA{EK*wdejx){8?<N<iA{o{#@=LzCLCi{H%pC-ZHr(@;uCgzcU;8n|H@`iw;Sh#`6c_>*M^z*A5RoBiG$L5YLHvff#S=A-*v`3VvEY@vU7Oim!ElL)O17EEIX%y~MXB^pbPH)O#5GCJo@%h?nzFiyDslOUEEj>Y6=H{={sl)0Y0O%&+Ysd@U?e#_JJnCBM-o4CDK^ME$3)XF2-DhUU0#NJy@uuQfe`c^^C%>u`KH#`k?Debdk0k^9oGM56zVMxqakJ4+r@g^$Fy<kc15yk)h_i*aKt>iMyr<Tvvivvr^7)MwpynDjyaDhB<0;fFe##Y-Pd-^U_9>oIp}hIJbihx|_`Vf<${^x^e*)ZeQ=@<-zR#`0zYuDhm><gsQBk@M3yy#V?1H;8Y%eN}v|)nep{iIY4wkF9dQ`ue4)^KdNg_r*oL-_&1;buu#w*X8+dS+NG=E#oo2xqDGh)>`=Kz0v0l0eHTQ`Ucl6LH*X${&??cw+Z>Ln{nO7^Q2DOpfrpR%EUez9*X|NrDNZ1PLlOw88ZXt=Zu}0$3H@me@7DTt7o>;I?<NS#(S!sk3NqK65mwdhILh~0OL1iqi?m_O8rJkfm44hy-RjG`N6}GfAnp<FZL=#o->Bjsol)SIhIs{`8wAOb#|PC_mdNsQBTGC=!2z=?056bE65)oj{KL>kiYpg<o6zlb7^j>+?S>9UF6@_1@miqBECN0KKfj*CC-ft2XMb(Pcgn;4Dz4fihc1~g(A^ceXuX?Z@_hrR4H=Y*Vef+oc*V@u%3UZf#>p>I^tW(24Vcc^H^6=b;UQoScLJ_-jjK^4m62xZ9M^f2+bE?Pk%>z;|<KC5qK8+>vVHm_Z!xk<}UND-EV>X<FJn`m4?W8v%d%GspNt_thgloF;8eOzIGSqkA>%_seVVN`!(EeV!n=gV*LFFSm%vv$oyJwc7Y$<!)bq6Yx|>~q`}xnyHDagIS?Setw}rN&$=pk^h<%bZsb^u=XquI>Wlny$Dz)a0r<R;2fuuOY1dxGds=cR{LiPM&*6pm9JqHxk<-3j6@&ZwR~Y)!JR0@5w!w89M4_Hf24MWUFC@RU+j!*9!FY3{o!EEPCSiR32k>8Sfc;w>gYiv1M*k01*@gLw!+l-vjr};ZK(4EKOoh*LRqK2i@7sa#SSLL@q0X`()PD}X$%f~JX;3ECN$PaeQ{Mm5hH?%Y4QC<G0(a;0|GMGaht)|qKdUc99-bTe3cTN1dM(2IW=3G0A5O#mDuHkEs|vs51m3&KmcrjS1o!pyBlPp~O8A4>2b&Mx^Bb*3A5uJV-6dTxzus%$cR+uPJa-vyjZc9;sTKOKxy$|PzF#@*7p?nRoNqZ6r+sP~{0z^Xpp8!BO~YQGZ!z0(zoUcUKS{v3u`JE0&(_?#7+*OP>unOAgIXJZIUn@g9E|rJjr&Ua4Sjy}y;FZI_hR|{J%;%zf1akf?sW8R(Qfd!9meO8?gbdn^V7W29nZ&g#i*ap3)|9+-HyJV>We%*hoV28=df;<jzIleI^px?iVMhpt}E(~Z;ErT%O$7vU_1UQ-lP0)Ab)aW^erVD?{&}bVLabM^iwA>e$7*-bHhBQ5zfhG&z#1ai@x3E=$F4Q*;Y@GJ{W$_QGch_sDI5hyg!fn6TaRD*L|dAIQe{T+REDEeYNIaSXV>vytZt58|T9wtyt<!>C1hAbJcpOviKI`9psrGh<)*Am14*BraxbWc@M3QJba#-*L27D&t1hg$Gr(ZI8pLzbLt=up9|)CAK~-k-g?DO`zsNj)6M7JEOuPa#=O0FE}w7{-^d8Wyjv<^J$ST1Jw;8N=20(uzu0j-+xY%(1a~ZU>`(c;l>7R2%$IdeF229}%hRb3<_Vsdmv|qH=Xq<~`4-<>z0(!rw|c-o5QKG@314d+0zaazT-TJ-qu6mj8dI;}{k+t#*l`^i7tcyR_5HokH=aM{!VvUlTmbS1;=RS3@+s!sHxzy2Ibf^y8ur}>!;$|a_O;0?QG9DDeeW>L%k3<z+i|1Bx9&sz+8sZf=gXoo@8$X1R75==k9V41-KQo#udSNkl*fE+0-i^+Vx0PBO7TD+Tw`%xE^Tq$B0sFRGjZ@O12JEhy)chaQ*mAPK~H{;b$B!p<IA5@v+v61P20!w&>ub@O&9#}IdS$Pr}5?Q+qQMfoa?u3LEo;fMjwu0|LVm>c&@ETMjk#ljW3IFzorz_$>*R^XEmN{(W&Ue<l*p5U!woDH{rVUwGWR<{n}^SP=6g?r~PQFzul=n=7v>Kr&k*4EI-dr)O7MqwJ_eOIX&0WFMm!MW7|tT+Kvodm*=xF%?ICWSIvT7*xqS=jcw<h_OIo_TloAt_#)QZ?^r)Zz{XvUzG>?FxZlN*@E>X=a-Gh6Z&|Pz{n=kpeEnbxtOv~%-?s$0V0>sBjDNfg>*PHA|2*$Lu9elTpVMD8a!Yf6_IgdzR8-Y!Yf<42f6`E<`YG4{{!bcX+W)Wqq|wgP>;L;Fjp^zZ>=8*FLyjbePzRAi$R9Ek2U7czmHLwd$saHjcVQ^@rS>BGlD(;3WN-5O_HegHD|@u2zE5sVZcp_hw<mX|_8@mAccb<pcO&<t_9OQs2T=!-gUAD@;p742!3@PysRnr}c`<b!c`<nfL-7LYbn*i7B!=Rl)JXDBaxg=205yahK=z}4NcJP^)IhRM?n?cD`~l~+D?_oTJ>H|Xqjn)H^(D6>cc6NcJCNH_-zO_=MQ%%O&QR>eQ2Z{{o%}AjDMN7!YHM-}avN%UavO3-hT=}t&g4#HA8I$U54k(FC%HShH#Lado7|r|fUI;dxj#9Sp?C;G@p$S~@_2G0L-Ci?#pEx^-%?kQl`bHEOa6?ZcrtYoc?dO>I?18VNvvJzP=|XN%KKIt?9hi`_DN}gL*D|}SEYUqefHx#DAgV2Md!RJ?Mhba=`g3BoagejTR!iK)w*a(ZAN{Mth61u8M!631Gy#HgW8s?v^jaEJwCU`G<z(hE}?!-UP9h%kNx)8V~-r_R&oy6!ce@Lx|zJ0c~&zN&!^5L&nHJyr;(LLkfX^XsME+wCz6NRW0a;ovmz8vU?`4ZD2}CmM2;oLQOA<UGItzxA~}vci#m;5-qTqO#fuor?Xl7xDb)20#a}TLCsUV`m-F|NsSC-;<h9f#<R$F;T884?)UD*LoJ+;0?Qzx~1=M_U0r?QsO1AR%4pH}z50QVO?k6kFAuByh{)v2sT0%ZUzDm7JzDoX$q4-y73Hev@Ifmln)WhWC<XmbFIhUMGwUGDOL%oY-P_xMy<TX?aS?OxB()r|1s0q~hWTnyM1akRVs(1)>g!cEDr!<N>f~<5bIf@)c{fHb!9!(uZ9!(y}P&}MEj69q?j%p^4BTu1DAS;a_$5UreW5_eev#GIUrEz4Xv&c#pk(JIR&nC}dC{AK1{*=0itaK&$Q}R-V;$;lQtF*uO?JDXw<W=N<P`8u+LH?SWN&cF=k(x!`NdAtYIE|rrCpDA2le~kvoxFpbPW^_QPToRIAuC-^-a_8QP@GErikwQ`KusoZAg^O6-bGzYR=S(4)Jon(-b>9V?<F6ko+Te7pJXU5qy9`TBVVK5CSN1pqdq3zBj0Bz{)2j({0I3i^=I;3@-Ni0<X^}a8H$Ujr^!kS$VKE6)I;PG<f9D5KT>}pD?LO0k^E1F;_K9_WTn56uakdgD1J(PMppVK`6*eefKdE`q4+QAGxA^L=hWZG&&mH{D851cm8|p}`3CtsLvbPXIJuB~fSOBInoU;v16k=l@&WQOY99F*`4mI(1!^f-sf~Pre1&?8e1&|6`iOjo{KOs)sSl`+$PdUjskg{C$(N`$@+ERHwUk^;K0?hS=kcD8Fcg2!P`r(rLEc9Gg1UzM1vyds`<a(WO&}{BPgXx_8NI|%?7~o7nOc!tnOv1xiCmRjomz!lo$N||nXI%L*_B+Aq4;%b4f5;cI@DLlb;$LouafJL8&GSJ8;~1O-yk<4zeTM}R{AFSEwYJPpKKyGVJLo^+K~J<`5lJh#tg-^8H&|cNBsgTyi~j5|MX93|Nb%5<T(Aq+W-2S&R<tK{${B?*MGje>K9l^&8>YAyd*CI{_2yA_HP)HZan'

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
