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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/144bf300ef43437096e4be61f4575bab/part_008.stl', 'relative_path': '144bf300ef43437096e4be61f4575bab/part_008.stl', 'source_sha256': '7bb1add401669c52febbd92fa3918570f03712cbfae57d9ddf1bc7e5ce91a6b6', 'input_faces': 430, 'input_vertices': 259, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.02518330328166485, -0.03897053748369217, 0.35815396904945374], [0.011734068393707275, -0.008573772385716438, 0.39588433504104614]]}
GEOMETRY_BASE85 = 'c$}r02UJvN)5k9=#Mol2sHm$^5hZphiea&0rPxv9qS#^uOGJ&imLPToy9U=N_8x0Ax?&W?im{Lcb!~`X?=AY?Xa4^^+4no&cg}a-*PJ;s^V`{Z=9y>i?!8Mw+vd$zLc_mGn!U&D=_lMZO-UiGgf^yM%&0+q`;DwMY(%V!R#dq9=g^5AI=2t)?xKy+#(PHf8`(F;vysU&pueA|x5=~r@R(6Ck;8fqkBRE1c+1EkBl{VA<iN-g{S3c)y@vkYrutsqrteJu;lBb#3HG%ommXHNq(v@M+TNpgMxde1iQfn}1>{?<wEjFmxVFD0ctozmo14Z7*9%kx@3eS{($-7$5I-zeeDgw0Ubm!o0{7Y}+!A_dh0-?f9>Q%cRth)0vkKQ9_#(d6H^R00XC#kp{zUK&b&!9=Q{npPWYmAAD(Z;K`=h)*Z3^PIlo76fktzGqZr`|~xOH#lV)5_35N!$f#=dfQh_7F$iv1n<QMlb>t#GsZ5ajFH4*82t2mjh5N%Ura?8|+WaO<nBvaapPD&(Kp5%E*MlKkeVF{uBq#^6tPOMZL$N${*{$P@7%`M>FgJVSC832&Go+|uZK;g*05;aazf=-=<hP`~}OaGNPvxGmpO<UeaeeCh+y`i6(dGjl8Q_c(_>C!Ik2p*e_OlMWqn5B2mIhx}o;<Q&a0-0$b3!Ambd{ieO>Pt6$NmZjE(lBc-a9}+)%m~gv$D$XG!7wbk?P+wp%%x&2!$deT;-0baYm38*)$GU@BfqR{hJobbmh`$zueRX^y_1GH5V!tkpgqt$Pqu$@JFWcmL@b&Sst`^<``Ad2s{>VMdPn!p*)6*U62H9i|ZNJyRoRlq!_^CxP4>=={KfD0?*l{ziuWhMZ_nGv?+_f+Eb#=UO>+`F^Z4GKly#6Esd~zmuwSXjC$CxYq_YC3I3(c_K4Q-MCRXXz53c_`edI#}Kk0ZW!Va!idHue>>8To@(;QAf41pBIz4F1&^$z$t=c$@bk;imM{xGuvEBhR^bocH`CvM=+4L&%db3H+CWn3Mk35x;kwaQm5P*{>-+1@jy|M7aLYZ>8weYpCC+2KXUe>a_e>75VE{7H)BMTP5o(oGjcFYeIbSUnGw$+k$yGT@LHczKQ-H1Ghgcg}&ukgwIKrg~-#p1oC_=kI$bW!_kKa#Sou!3ZI7)*oSRz7Krcm0@q7<%$42$uyF08o2+X}!nv3y91w0V(?jyxUt`Wq6C#A`<#gGX_0=HM|9yMm*2KQ3=TITJzO2zf$P-jfxc(M>Gvzixo`NRnzqM@<i8nVbh4{r|ktYpvXv@q<l={!xa9;kOOT2wml5pEVZ>e7&dKCR1wM4jmewxH<VffzB8b%`zzZWdEu&(83U*Y;qUCzbSA`AU-yPhELuN#g!uNISdTd8xxZHuDOPapKzvhl2N`;2(Z+v7NXuI>_U?vsM=o%%l5@9{0dtzQgZf%VaUEqEsKylsT}&-9act@|LX+un@$?nS}RgdzXf=eXY6HAJ1WTM5?>Jd$|p?MC1s)xmR`;T$WQFwa>Y$n!-Q&V3R3pyifDorT=c|403BE?tYEo(=2p`LhuH*Hb=4{qJtdx+WccGc^M@o%~GJ)k6j&zrPFWd2L5OZ~LM@pFEu}c?U$J|Ni)Vw!FL}+`Q&n^z;2B<cYa0+*)NL<|m>A=J0LCeC)TpoUir}pL^z^i-nt>?2x{hwz5CH#vy;tBAAnO))UtW_3Y@6b(aO8{~KS;6CU{pbAFHaEl+ahVZBhvZ?4$|eK>VWxV~$F)MH*e3-QD23O8T-8=s$1=#OsBk31#Y;q$?5B<c^XG*jZAK3grXmpU)^8@Ayd(<JU`S>dKJ>ybylKVH@i9P*RA?*zV=wH*_qCEip?xczx^@IEesh4<Vh=VeR4{f74Z(IDw_{AJm%srq|aS1b0#K#6;wh4ZyUAU@;l0Ew>@Ec?<^%Ymm&>L>BGeYjp4Gk^G%D2Z!dMEYad^c39ZR9~sDP(Adm%?GS|Frtst;V~5XJ3mJJvh$G=m$V!4ri$R!CBm)i&tp#9J#dc4zeW6yQ!sBG*oTZDi}*V~MV-BH-=cM?D%>2m81uiU6!KIL{#y9Kak#$z4n@3P3S2*eIq!wf0qtO(Uh@8sMBHC_mjrhY?J4hfZ-qLqx`R*f5N;Wkh`Gx50)4P<>LGoY@=oHlPjH{0x%)*({w}{rJ(eyD!2LFLlepKrab0_sM*ePQ;pW8Y$n$Iq@~^2V+%o7Sz6TowBhP}^u9E*lMagekeE{52Lb&A<S6nZxOMy3d*GcxZ`!n>d)d2AIHNiV&2)DZ8b6zWy7AA26yiw=<;@~4Zg_~kG%DLDt@jiLTsZd$(&$F0^cl;c)ENdt4Z<>t$C!4|J-?WwYS4hR@gS#8}l3Btn$8g<Qmh=1l{D;=)S1rkJpD+-7o|kY_Tw{sXT=;pey>2G^F?Yvxv}YE1mT+_IHC)#%f99MlX(I9SkE5Q+w|M_w$Y1KXXOnZcTKa&G_|;ePjBA2*<JgDLdJV)c*BNutW*)eGy_fh~yJOuVT-SQHisX;RbCRAL!aDtnNuHa%a9<ST!#YFUls0?ee9bH7Gk#h@rET38;`{gRQ1bRggxA}Sb*ILYM-;_;rQmt7*h|ctW-q6-eyB9=tFO0b9~#z^bu;Q<uG)VBZd>gmI%+WPZ(Ga;H%Iv@ZT+JP?qlbc1h3=bC;E@En3HuMv99};AX#_HAv`yI$93JWHIw>_cg6Q|Szbrhv(1Iy&5!54JAvS)oo$5g>W%w(*C@_OPzR~MU^3RtQwjWW*>I&z&97n3i?`vtEf=okpM~e6s+^zqD}|f=;&B~C<9<xbe24h`2XVig&GRbc(Mf50@%nhqJNG$wK$vjzoN9Rfy|xQ{>OSGN+0&$c>j9oi^XSe>TRI)Vb88FEPp8l>l7Cofe4kbhV&4*koAPS7uQ<*=pV%qfymtZOD<yCqenXzJkMUe^d^_`h)m7r#cR-zCod0eUh3gO3<6QC_NB(^ix=H;<3u8VL*yqz5x=a3k?=U9?-I>R;hx0k=^ZJ7KoGe^lpNsqIOwLt&Hsb5=lXy#9Q_fq(p2Bl>VSdW&<#m_GBJ1XDg1(Ktk2>4*6mGiUkKY>}?&N$97OuN5LcE<kB1X7YBp%OyHTe5UTD)-U@i~~cs=OZe`9@0L4&K83@-F=TppES-+}`aD>Oac)x%>d}U#>>~e_;QkV*ARzRz8+~+Rd%NCteqBy+0cFrH%MK>s~TSc&!tBzT;e(L;H)~{+-OBsni)>7cB<Jy6uv%uLS0=kuXsDU|xy)`ii{XH?9I-hu<@_3wRFFyf+WTb@3&xcWo2;Jj`p5#D7@;_nRAe|KQ^_Sa_Q$n5(UMSbrbk_LlYVyHUAn;MEQek@#mRxZn243!Z&usKnnYjOW@>kC6YhX}IW@jqv%|xjy1^E(zD?%#i0ETkU+DlWgIp#;*8X;zkPc#O5C%*IoVbazAM8l?8sbxNuX8?vlq`r8V-LIV0S5?i%iATOUEZhc!m}Gb#UU;WIM9k9Qp@_3ZFKp7CXnr*i&L5^pLkd9-z$+ef3ptCq#*iPvcGxeJ7A?*lNm+j78NHVfC?wxB;@Z^6^<f*-$#-#>h=g8M!}{{7qK+^rcaz~>AcBl>Creh=ARme<9IZ?Ue1`~6C<5Fb2$tmt<a!DBg}JI@O@57{I4(U#h~5g#`oR_ZC&70;=kMSyRpGEQ{wnbJ3{@Kf-D9fjKhhRIx63SI&)uonEwEx7J}-2v{EBV2FzYL4&;N#OSfj29kq9(9(E=6zSXaINa6@sfX4GI)_06C^$hzw1~U?gVeQR=CzB9_Oo(r>BCu9KiFg#T~r1`*))AuA46BRsL)6&`!dwRVLu~gVMLahfbR)`|=z4gXDQM8N9;U@1>rY+p;gq4qxGVM4*noM$MA=;m5!`j1_Ks6NKls54o3x7f1xZkUR<d8ixESONE;&L|~qGO$WcR3h}i9F(+|L!5^m}zSFI_vhL-z;4eR&g!!L~J`X(!K0R8vP5UcO&UeK$)cN^d#GB?yJ@$6N;I-2xOMJ`CGo;RYZs0A$r%1lNJEqF{j;IBmGYec#kp5^Pt--5Vh3jv&VO_tu;QbB?H(TdUkvfxuQ0Ki8Q|0wNS$H1x3I}i56ujJhsmJO$1bN;U`$2Txs`6Z@d)dGPn}8SmAo;a+6Tq`Bf|q+Ob?R>>foI<rZp&ykS^8h93+K6H9Oh@f%#X#p0{D4f;pRhYC69fi7kKV(h(DDs^J6yqfalL2FZp-Pkv!IFU9SX&{@Y(c##NhmXT9Mn`BW>R^^bJ=6UchTIrRVjCy+r6{$GCrX;8n;fBPqp&oot}rj;?IIJNSt8&XnTcGMM}Z1q}E>Z-K84QXUZEko+j_NG)L`+~M&h1F3QlFyKWv<p-6F{jd>IN2I~^)C<Y@`h9~MExzN0d2)@8FI&vr_5cRF$HNW=0>f!ixX4gO6JP-T&P{Swk!MOu#3?z#y%>$GW*k*+TY2p%zahno{O@s!ej+$E9TDrmyq#-t(b=)pBqxzkW#cgcn0dMYVsUvlYME3AJ4*%uPNKhkQ%J725a<Ze+#iTrAyLQd;5%gS2{oK+RRy<+K+a1+EuCjX{(ylOsIJ%M_aLcPW{eHJ0H*1jptQ_b`|!&2z&2F+m*djy=*|;n08M?EQa(l<ZEh&-+`}prma|evJl4gBx^|>!aVA=u7-qCJNyW~9!y)Y07L2<Qir;NlU<g6UE1|2L1an?()Kl^p&_1zd_~)rz7K5^ZBN>s%<IW@lpW4JccYG=9nL;<=Ds^{zwKy;Q#z3;-I}(UJ!(hYfwrS}fz)Q&fwb#VH*xAgUHYw9S1@%1ZN+<#wKb#}&mo9*TS_2Vd)kUc8q&v*-iGw09m%~!k}K&>)}4D)b{F<IjQ#f|>q8yJoDSB4TJerftSS8#%-@l$Dc9=G{kJAF(QnHBG$CuQVFuc0n5Twht*CoYx1k+L-G<VItPAT_b}#l>&A`{R6${~+sx!Q2$OA*}vhV6ly0Z7dWNL;3*#7{&rfg5vS%JC^ZPnj!))&sR?ZLg8*$buH(GF(LR@4EsThVS#U5B=+NzH+p0SoO=o^?m|ybtZ(JlhsLJ0IG<JOdy0zXk24?4j!ESJVw@JNmBnr@p5$HGEg)YWTi#*zf2o{n(JdY3I^^NanEL(7(xZ$fA9N{td3@urulB@V!~IU($bWi2CroPx~YNd#p>H_bW|3%D`9pts!|_V85dOlFVVN9LmpOEh_(6Lw+|Tov-JREBhtudgauQm)z?c+HdLKV@|cN*R1g=?Pv6#(SJeh;_{FEf&K^9?6BX{f5!ZdJTK_q<C;%d=ijX973=+*d&pw^8=g%T?T7T=vkpf;KhXckwNyPHc^)swRb3jn3w!&V>%3s>efq}@In7=x`>2zz^k38$Xe+sFNH*;Y^skUP?A!Fu7;@f_i?q||r*S=peUyF%-+Pg^oxbYDBSWszen|gML$0x2Wj~>>?CbRH)YoZ0qMyO_RZcZ;>GU7*wX3x4^#9~Kf01RgHal}?GtYVM<qmWHPCJu+F4uod`x^aBzBirr4f<!9&#}jBuJ<Qv$!2{Q8GoC-zDWBD{aog_M*9x^N37)u?T7SlGT#l_SLrV?<VQpH(@vnjmCRxPMqk;d=qr08{q58nX`iIO)R47?Y@?k>KauM>>;(FI_}*=_Q|YTcUozyFA$twkV#pElD|{`PH6Ab|#gKFKl|Es}AGA~Gr;<7BOZ4}!u4Bx3fc_=Ec8qo^{S>bA8`&w=oXXs%m}jk1j}zJ3?X;KD-bnv6*WFM1DE$kp@iOgm^wsNWTqBw5>}PGKSVszLJjJ@VG5#di-$r{o{f(?Kk@i;l=U9`Yw-@MNVqJgGzC!;D*GZ#&jK0l~UwMvusg?f=wR-($C$^hR#qFcLo3_%M4OwqUtRagHS;ts4E32v1I?J5cBtv2hnNB^C_FQV^FLYu_hAbdkK(6dzh72}jkRc;zD>jY3vg2t_W3Gv06UpPbUn^_dN&9E+e<$sOv=uvK$S$&7<jP({y_s^5@kiNvHA_FS_POj|l2d#Vb0jfl4P_zUx0<yrqn_hrucWVZ9PN3AY~YzJpgoWIH<0b7t=Mv&r8>tQw3ky>lC9*Pcd!qK=^rLjb}W0Z&gDDWicK+OtRZ8_W4Xo(>P_Shwt{RG^<mnFx%MjRpJ>nJdHzJbigpZpGMHMYy^?ku_o$OCW^K!<b=s=`>bg+#u$T5~p7B1Op^f%0?E5nId<*S$^e3_ZN>8U9Wk`QR`e~R?Rrd($!L)a=#+}qw+CQ-uYp5ObsMd7M!aUlJ>u(bGK8ZYz^{JUq*YF0~>)8Jt?EQM$n|QYBoTl;YR%riRgR6KBD`-z+KL@d=gSanctGO7ZVK$<vl|PPJy*}KDO(vT{Tj?M8-f#K-3Dn9TO08ZW>BPP_WV|7>sAtk%M6LY!PHeUzGstF;D|?_J-xxB$kkPai8$w^%Q)w#}+SVmciM;>U|LXnEKV5#fasD5_|K~gZ{pV5Vce<6){`s*qw5_Z9El0~^{HL05PyKqO{R_J-a?J'

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
