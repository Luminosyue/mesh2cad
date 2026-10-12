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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cbb199ae1edf41c6898c997ae785c4db/part_009.stl', 'relative_path': 'cbb199ae1edf41c6898c997ae785c4db/part_009.stl', 'source_sha256': '6fa23688b370df55d0ddb767f57b588cb22f4ee2c35eca8c54731099f5611063', 'input_faces': 544, 'input_vertices': 528, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3749772608280182, -0.2935619354248047, -0.14268574118614197], [0.47083398699760437, 0.1996600180864334, 0.14263811707496643]]}
GEOMETRY_BASE85 = 'c$}qN2b2^=*X<z-lEVTL8buLF0!tEv5fntyB0*HbAVCyFSdxh1kOa{W1rr9e$w_2MOAvMjK@dfPfh>-SWbji^KNI|~y6!8x-pqH-fBv6y?zwkwy?R~URb8*>J&@5Zcb-y?{!_*2v$9KBryfbdwN5E#^nlEfkMtWbqV~{XV?$0c-}nE3U+&ngL&p6fXS6e}TK@qf`ejzT&8^mKVB=~v-D(3L&m5WAcW9r-Gy4xve(SzNMhqZ-#Gt;z2GGwpH>lURrdz*yP4{W{|M;gM4Z-uS9*hx(PuI+Dp?J*I^|62-hwsctJDn5oqfge%QGP_m!w=^yTNd=4aoSJJt6=4c>>CnSepKX%!jFhN>?f8KpPR~e7CBzf_uz-SSF)}fXaBB0-))h?cNZ3!8}t+K<F7g!g1)!)qVIdF&MydFH^KgeiwlDBk&+*7O?kiYou&4D#o3qRfiK4sNiVd^AOC=^gJUWDaM}}tt?`eVq5alVrpHqF(Rwqc``l~UfmHLA<p0!lT`E5^Z1>ur&+`>NTV-`h|B*LVrSjb!U$02zN4D*LFJ=7tF^g0A&bon%Qu(~DlH#$h*q7@^`n-OmA73+aaVkG?b<caL{7A0Eid24h>YJ-l`UP%S9rStKMrVAsHkHrohkd!8O}tpoW`4g|?61Q}t5a_U<30G!=5udZ@nZca`EvchPg+0llhzOWa{aI`*AHJ;t{;w<>j%Co*N=FA&Af>BSNfh@5By%s^}yqi>w$f_9@v-bLF^mG|Kg;+ua>2)d33+jzO$*EHILEl)j#y(FPxZX-7ouRzMU70cRm{A`_B1sR(u$~d-@40K5?MRHh=sZ^S&NS;k#K^U$e$@Fyj01?E0_8QuuD|##VeHZK3Z+PYt!+YqzZS!#51~to&t9_<rJKUV9&aAHKeT6(2eB)^`7XYge5WOXc5KX_ocg9XaCrks9~TjHU418`{sb@?Tf^BY*w0`pbUr;76MNYR#8Zp||fxTi#;Dhv7$>RJG@~R@x5#zU~?}J(j|c*B@)u1-Ev0-%qsMJuQ~PkJtHXnsvXG-q3!NV%Ge!AI>WEdN4j*`H=P-HMi!MefRyA*8DnkXYTZWuDv1}OX0f}=0>git-H_n!#zrjx5l4Y>SO=;ykC1(N`Jx4_B>{G@%`|Mp4L3dx-5OJ%O;Pg%hKn%?ACCy{5+yAC;8Y{rO*2+`?4-4`Pf&b&vjY)T$hvLv9C&>>$3E@E+@sKF0(J|vh=wwOP}kq^tmoepX+kcb+Hd8`PhfqmvveCyg#!q>#~U#b=l0XsLLjgsLLi^)a4{!t{+jC&Af=ZoaD>(BkHpBqjLR-x-5NHt{+jC&Af=ZEPYR|2T_-$AC~Ju)a4{!t_QwfxgJElHomCW?8|y>o`a~@W;~)^voGs4`?6k}@rZgYeXiGLJfdDppX;^BBkHxeUs1139#OB&{fc^R*0ZSBNj~bed5=WBmOj^OlSkBR6EEtudH$kao98d;wYgtWucgoR+B`Q=ucgoR+Kf}wYw2^nHsciaTKZhC&HajcEq$)n=DtL|HscrdI>|@9Hscrd+RT@z*V5;DZSshEEq$)niN7-z`p-dpZ((14Z((14Z!z)Wdkg#Wdkg#WoM7^c?=8~j`YU~|zwFEJEoPjeE=!;5GW)U)n*5>;ns`wM&HakHX2vh-f*Fsf3nstVhfRL5PNdK4#Ef686Y29h3BUZXe&0rn+~>!2>AE!*@T2g<O-5a59`M8PBOSYL4d#jVJRSGryV`kN_+F90R-X8S+INsAnl&H(8Q+gg?7Afu@T2e(JFl(``eF9-gtCHp9Qfh+-L_cyfBSijKOT`k0zdMxoj?97;zj-_d`IMu9%$;HGdz(e{FU~j$djnE4CC*pzf+Vi=s!31od>k<Oe(lF81Ibf=AVZmov(`p<Kv^W@7-E97L1R4T*W`%M6!NcX~pl<zSH<j#Z-Q{%7Eg*JTCmm(4SW7^?~th*!8*ZA8pe)mckEbdKp%{yT$k2;#CL5Quxtc?FR+p<EIwrJZ0R>SPDPVEIl(AAN_H%?|T(nkBX)6Bds176^sw(@8|mo5zoFW;uHDq^!>OP5BrIx_ISKKHS~B&*!Ro6)6>4+Xv4}n|8e_yvY!}==lRldJ<j;05B)rc_H2j+{CG_J?(cgySn=UAz8|SKINOSEp?$B*kZdcy)@pxU#+!P}Vk!J^(<^DIe7E$(3c)-M$KO6@S<vVAJ-k!z8zvsUcVD-y)_BhL)bD$nUseX=UHH-A_ITJ&9G_s1hvVD+yfWx}#V7mkl^5Ukb}&x_zPoM9+g5zXqB;Ka$(Xs$dY&D$AKm}rI_tVK;{LwlU0L{n75{?vBhM`Oz=|(W#*d3n&d9Oi^Jzblw^NSwd=_ut<j1Eiv(`g+k@lmrmssl|I^~az{(a>i60_nbYd<md(U_ILN_ju8^G;W5{En;rXr(UJ_`_E_>EA=NE@aQ|7417y3tIE*Rk}vk(a7}8!T4xJ?Yk46-)ya)cdq#BIPMO!;=MWAPk2M^__AI7eKN7Aymi0PH0?Xp%31fDSh-1`%bMBi--92|zM7WG_uhzF>n*~5GqL`=xc<KC-7VHL{KR=XKl{;scK+zS+K=Cj^;}}Le$MUs>c2mqZK&@Te!Q*rBfILyg7LCmu%ER5yYT;h*`HT$Lur4#u<!k){pjH`8-wxQ^N0O;^3G?^55|Ytzp!S$6+gSTo|jYUv0!}Ub?t}qH;e`2lb$Dh`Fz};PNh6=urJRW?91~8`|`YD@{98Z`|`YD;>CHxj7OX|j4#d`W}M=@;ne<7=Wn)ZzyBPbZKdmm@SQ26w+8(v{P4xmTU(^^f4f8fJ^t3sJ5%NtzR3?iDZliQ-z(EypKHbb&%WIMrO*36`*Qy`zSwWsm;0?5kJt}Q9<d*qc(EUvc(EUv>x%t~eYszmc(MM?a}fK9^m#uq`NjJZu8;AH^D6uDylQ-LUS(gNSJ{{QkBJxORq6A2m3_Hig)8>d;}QEI`*J^IKWRMhWqxlFe6b(0FZV;^i~W#&xgVN%u^+N8_e1uR)&u;cdXeUQ?mwR}{yw+^=P~$+7TS+5`sP$lz>mXsdf=P}Kj~b`@$y{C@$y`1@{4mR$IEl6@XfhY_~u;7_bbn(d|i1ig&$%6k4x5bNII{=PdZO>9(kVRczK@W@yPQeUss+dIbNP8`8mk*A^Y-t2tVn3$no-g$m5siH_ju^Z#+(Ue&amy{Ko50p2s*|p2vi5&SU)i#d*xFf#>;k9e+K$dGilX<wv)6-xBoW`AYlq;{K7(iVwq&$8~&^ea`=5H~sxV<afUReOM}=$0L0n5Bpw;b=&;-nV+o*<_WVu{F61o_{6k6x(<G^bagO34nI7p#*yX$KMFs-VA*QxzVhq)O^EyQ@En|r_I-KcxtaU=FV8J9^ml!Jy6-kCfA}%&J2yAA;+=VV|BO_4a$Yb#I#>Hn&bWD2{$oS@=M@*v!GZ6*R^ECJ-cjvG@f@7@m!+Iv_T~IapXXQlJiqMA`8C%S^UJ=RU-sqvvM=Y?<QMa6#v|re`aHkpzQp{pFXz`>SIn=;Bj(qPU(Bz`FXq?e5%X)tFXlIL$FgI7y!hTFeg58MeDS?Y`ux3%efhmh`ux3%efhmh`ux3%efhmh`mTtV-@ByG-@DkC-@ByG-@D8>#rH1h^Y^YqM?AOQmHodLxCb8A^#OjO7yOGo{CQ+Q4nMrUe|9iWxWmyM{y4AH`XHFcEw#w^-SqVvg1-0W?Y^Hlv3yg|kCqyy-@78~mj?YX{7BY@rNQe)CRNbqgi-qU%O)Ov;?OPD_+5@q8@t#V|6eow_aY&m!=Ks@kFI9riNcR&+s`4|Z-joonzy&|cn@hmUa_qmzp#`4e#MuJnP`n4zEgMn#9(~<oA31R=||i5>%otoEN6`~!tuD@NHgcSpTBdVz5e*~R65Z-h40;2pl_;pufdgJDf6_=9-GRK)Gj+AmG3t0HYMmsd#%#n-`5tj#>0NNu00<1otpM|Or93@c-W6tx5s1h*Vp6mGPEz>3-;xE!M=Pi*q7^>eYu|5m+RTYi}lRDT+b$6tY<TRv7XI1#d<crSkLUs^=#tBdN$(`>)AXvv7SwSv7XKIk?VORp2JgEZ|9b;4*Cv!@4b3!Qu&cKTP#0ub%kC(XYD-fyCRQ?Z>{qrs$Or6$IGa)I+f4kWM7U``aDkd<@+mret(mEyuV3#@cv4l-(TtT`^&z3f2Ggwuk`u-P0G{49*=x~lk(TM$7AM8JbyXAN%7+OTl1S?{p*om7F6EslqX5J#wq0t>>K>2BjphXPW?|u9!dY-{nL^3^#AWa9r-)tIE8aL&adF#Lt6huxR!qY8(bLrH^Lu;E8rrzw7yCxO8P(GKSNqyLCjTfQRpw|-VYEy2Y&_qIrM%&=`RU8sn5rR9fX;Lw+RcuS<ufDULm{-UIMM)p<VF{&`S~XD)<%X7r@VhUx9uXaUOUn^oxYqg!$n2ptGRg2G53m6Z|50HuQYNy${ZU{*>?);SBf^^e)1F!YS~N(3haU0`G_Z0=x^nANmyHega>D-bUC%H~~Hny_m3?@G|%vXmu}hFzzhqRft)IxK;4EkK$S2IncA9X99Bq^R4nO0<VHz1id(LJ*DRnmJ?=xUx%KHwts<VK&zN#h*SI;^j!Qr54;?D0bvE<CGZ;oy&6CB^WiqdZ-L)|UWvE`;1$s42)__M10RG|b9VsqbP4)0VlE@@GJNi%csKX}^ls=+fdip`)|twC7JM1{EcCg+^^`tM_&4Db@aF;j3x4MDbDQEX!3Uv#M%-!ezoAbOE)qTh?}Jur@rRIJr`w>ngHJ-AM6A+k4et%<b$lNB0&-qJ-V5;g8vD?9AN=jW-oSPDhW>d^&g1&$k?RNG0>;AEQ~F!l*S;ro32E*Y(z+MnK|(d~jnF*^_o=>)<{uobyOQos_|DOM!qK`X>E48!z&ArbK)7E$TSxOLN9z`(!-S^bX3%#KS`uytH;0}^m`<1qeh#`Fp$(xlxG=QhlF*8;gI4h!5UaQ?bag^4LLYEH=o*ANXs?5|>S$9jeZd2u?<8ap@_?_0&I6qrTm`xnp%eObLLa5C&@-w;{5QBF^ibkSgvY^?q4Oi=Pe*ea^bq1_2&2H0pbHU-5{iS%K|f8HKo|=i2mL$cx`sFu(p(%m6MY^9kAc3M(4J5PTn1Wk1!%>kpjG@mh*jJXIzs4AxCLAr`WEP#;9H>|A`C>of#{=jK0;MOUhoajcM&=hT7&O}b_g!vs-w9w^f2NngyG<4q5q<`vcv^KnqBD8h<OYgg)TuTPq-Fb4EjmJQ-ty0iO{*w=MP77LFmE6PY_0e$3q{awxfi)A<Yd!TGt~qBph-yA9J+kHr1~l+7BY80pc1U7xy`am}9usLF8$GTn%t7r4Liv*M#~Z&5c4@rxO|zjyRf+J6dy_>X(l8!-#2wxJJmueU2mMIIeXVc^V;CBU~#T_xBC%RdExHQ^ntg>nctl54Rmc&ck>HDy9kInjjbVNgyVHYaK$KCdkzU*HZf7kbaj2fk!|Of_?-%68aqF`VV1UNb`pwt=ACZgfoujUmdL#esgrY;;o2X8`6ExB8SR#7Wl={?TTZF%?|0l=aEC@QhE#8E;*W&r}T!9?t2kAR4%1I2<f(;5TiV$H-&Vre<P>Lq4dU(Zu=22%2RrCNay+)IaLm&*N1f51;i*%>70<xbs0HTj>~wCIe4x)Xg`N%xE{}OJ@P5-(BCaWghL_CheKNDC!LS*O-S?ckk*I6hrq|7b5Trg!jX{Xqam%YAzgs*ZAfz>r1eqo5pV)J55?pq91CgwI;3?W(gg|Mhctf|()w%gG4OZLgXq?xYOcV$ptlk}Aq)pU2hDARz{8<GLEq=V(LkT)5c3@TLCCWUId-AH(od=NLD&i23;iMCGeRaf8=Bjm0%t;hhQ8V04S_z{h{=Zk6!Ppvj=kuwbY4PHLK?UZv`c7A$PX?C&24$X`Jo%5Z!vJuK%ZiWDF#0;^3*|&I_R%-VM1v_4e&tdDun)o0^pL++*TM|0J=Z=mIRj$^eKs$lJE;7&p_lDi2h3VB=jY`4_*VkjF3g>0qzaWZ9Ty~ptI1oH@Gi!SHc61`X>aM--Dh<SVG7EcZcS-uHX#lCFt87`~Y-&!o7rdzzd+?BzT0o!5yKwtv&c|Xb*img71aClW-5=HSpWevk0>ZVQ_0`Zo3m4hMtYSt-<#|t9fbZ=ryeP6==22$77BZ*MjD@8sI9><I%SkxFvK&LIc83@Uzg56Q&X>fg3_|TSags=&9)25ZnOzIzoNI5b$K^#|Tph6~O7x+;$zf0`wI0O$XP9E=Q<KcoaMldN5&<qd%1?t_RI+<-p~kC!udWa9!xighqs6;Azmj@44W{0X+>rPeUK2a})9rwt(Z%c^vhjPq$x#w%lk_F*)FE(CQCu`_3ltX6O)dIpAE-n-KE>I0w3)qu=v&;0@5L9ldWx!2O}Qtsgi7&3kNrFz+3_zYPLMp&ubkAe05)3e9b4;IhyY(Dznw9q5sS>4cBKpF-~->?Vu@&xGc-k>GLAyU}+hczU4EOvKEDKN5L9MUGF=U+EEq^@Q!<J<uN$_7R>2Z-nNy5#Xnx_o44b@cKZXjfmL@e+2UEL5@A>uXG_oal#GYCeXJK)HmpB!6l%%tq}NH=oaW(0$e=Mrvze3z%PV6O^~Ar`YWyepCR>``+D#I=$eFw2}QtVpt-FexCr#a=vxL{D$u74V#>fTh&%(3V*vUqeLtZOVL5me^h&~7LND+`(A;)ExEJ(V^nD222f8!iKEizPQs~8m6@+f!2cfyGGq@Y{3iN#td>?dMLMOso;JMK65*89VfV)6*TU&4k=!NLp1>6bx4niBk%iuSlUnk5V+y!n2&24vp?}DC#zU{zmpw+z8cJvxn{0y{O=dWUp6t{xrw(G$)p<hMcR^ZyuRSCBdMuDG)9!+?Ga3i=WG`Cd+-w6Ez`ZfjM27MEu8DR|gU(inwW)P}@Z-?f#o50neXQ1!x;AYS_6V&g##)4mjev<GKp*kU>T_{(n-2d&r9{cBy`bObc{}Gw&Y5&?O*t0q1GQWh%XqQ*jCn_$v`~o;uos69S0q?Y6G5'

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
