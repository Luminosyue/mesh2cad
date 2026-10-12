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

PART_NAME = 'part_014'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_014.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_014.stl', 'source_sha256': '7429c7efed2dcad931f9b4899b6b2d118ffc60cfb3530de7615c429fd6428310', 'input_faces': 518, 'input_vertices': 309, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2289518564939499, 0.14311785995960236, -0.29744088649749756], [0.07537272572517395, 0.2797080874443054, 0.15756821632385254]]}
GEOMETRY_BASE85 = 'c$}r12UL{Tx5YmcQ3Na4f{{THEQq2Ql^7kn#@JhIaZtgE1r)oESfjCGS9B}{HAHMtDas%!_TGY`V+;||SQ6BrNqlq9-aKaBdT*__-s8XSfB)EC&OP_s@_hp<-8&a`bl33ZrG+{A1x@`_(^PZS+_lJ%@JXYFg+%y|n=s8mD=WVGD$wYzeY$k-@1R9$Gkk}KL<|e}4bu5G4{hq}r}GURA3iBOc-)Zj;lo3e-#&P3M2OXo7#Tbv#QJ@$Mh%+z=^EAc)6LTTAHPakQ!sSydMVYa#;|86TUu4W_sLPE+Lf=w*RL#_uD;hzydb{ub|>-8ryogwV@%IuqS<Z4H*_s0{f+Hgi*I?Z7hkvMhV-{Yze4<^&oOSzTZl8}BKm&_!nmF%?BW;rTIdV$b>8zOj;Tt0_!$}Eo10sZ=RkkNxf2I}&~=Gph^YsEY%$5x?4BaN&dX1H%V<yW4LO@7j>YI{7f1hdkn}e>R)fD{mH4J7p^5VEi>o3ZXXK+_mm+a==RHt|etGckHI@FRYn4%lCyU_U8k21258Wxg)@{4^=B;k<XJ%tw`x7LNp?Z1v=`#_he#InP-*C<k>loyYde$z3{(BSA-!WC<8(+F2|JIM;XML7r>+5^9M%{Air%3z&`h#8IADM~uedmlgmL-T&DpkhS>z&|F8ioCE-6`4DH+Hhvt*`Nd1M<J|2L9cx$Y;af7iGOlPmyu8_sb<8-8b(q+OC(bQ|V*2zHXl*`nSnUvh~d`KE=APd4~Fjyt`<-AN1okV4ugm72g<M75lu?4jESq%R`*}5cGFTlsJ}se`4J0WyCl2Er$3F|A60jvgBzPGzRN<<dyiQsJ~I4@;x!H;<*=X>r;@YvHNd`^SlS@pZ7M!*4LVCL_SNZW4%^qi*Jba65mp`H|l@$SB%^ISJWq=-EkSWB794B5aLW)E&a8xA7j4jOQFAy2l5|cLI0>>$a9LH)Y-iIKJwhU6n=g*&Qb0?tk;6GI7j9OSa(18#vCV%+cpd5{pfAGbu?zh$hg|&OX#2LcuM-mKE`}2okyO-OJM&Wa+iFxtPIRIp$E=acs;CFHTe48Y1j_~Hc1`yKBo}BV=(q}%5Lee8<~!JUXR3jooXfdSe~V!4uM9=M{B%C;+X5fH?Ew5{aHB|>v$j){<4zir2pT$@$XZPBhQq<;+q?1q27rp=<gDZd<<HOt*<S~N1aEFK%JW>BhR@NQMaF_Ngeb>64C$Q5yY7qEd8~GM^T3-I_#^Rhp>*$M=-D2O;P9EAtxl>vcu?q*9ZNNK1j0lwJST2|GxLg>&hYI?{FUX*ecHyTi+CL?yUU$z{Z$wuY*{}oA<C@&(=tP^X>f@w?zQ<$qWBvTVFdd3+JxUG@QH2@GXr$O8yqt1;~Fu0><t34*3*)onq^2-Cmx<`Yyq~*s>4xY}^&~bnb_9F*F|g^G=xLZ;5V(c-eaqXXPIB_k5CU>l=zLM}2M<mArJn$Duw2&*i)ivM%O>v50esb-CY2_LcFoT^P6FXpA?^A<5P^?fXgMntBJO%D<;=ga4Di<f*yvIpeYg^*l7^wEX<%6Q#fD>PEz`5@(l>?(RCQ%T?DiGT$)`&7uR>!smN}Zo;}mTVGe)4f`h{9_#KE4gX$q8CQR^gxS_NJ$fSbF}!rcIgVY0`Yeveew%z!>YzPYiTcD}%#iOVpGgyay9D!UxL$nyM0eab)4qj&B16X2`OL+*|183~-0Uaw(r0UFc7F02@wKYQq`#KF0P{VuR_0|MW59WDKOg<u*Oqb3r}PrXcs>gIu;UwvqpPw&e9N^t=pW~aeK7qy*`H=N_<FuaX}26xY<;t{EAEZg2F$C^Y}BXzR=h`TIwtiuuAhZC7l&Y<Jkqcat4~8dN1kAP*Xr<mtP_bik(H%BTIXhxk2ZF)-Th$tqBWi)?<S!B4Q5I{`X3Uo{>|W<bh~g*w!NEd>zkiGN1m^u?R=eI4DQe1p{aKL6YHFpyywQ^9LyMx{vW2we%8B`L_B>M@*LV6_rvFr65kLt*6#UhJ~7G8H}+qM^V<c_NuARe_%q9kZy2>7>(FsD<~unDb-Oc4*2Pq6q}_8|+ZL5%>+3$OMLh=v$h-`zLec+xdCX_#Tink#Lg2?PMxHJys80p>2G_f|Cm(IV^StkH<musx@8756-rg__alZD(xz6;IeQT^b6!nRzD)rRI`{RE5CKz$fX3D-bI_#GHsW%z0Pj1)1xd?K@{`Ve&bxD|w^VQY|_k7qu)aQKy&eyp0W;_4fZp0Z9BfdUi0LE>x0qgf-ZIYe8eLT+lj1|eYzG;3I;skF_v-R~c&2SH#@xeXtx<B%-tj9bbd`z+Pd$g1|#%Gmq9vk+zd*9GkIEr&O>1*WU9E)?e`3my=t1sp?b}R1r$amOR#d~1A{@IW7lCfRx2TSR$s9UHL?n9^Jh~K@7-F_%|PcT&M48JYTm3d<>-e>N2grAD%sl~q|>Ql2F^31~LDf0?1_<=1^pGg+v->@$3o5&W(|K<(&H}U*2ecl}L$Bjn)E6q!>^>y|C!9Mi-4Rvw|!n_`N;knZ>OzsU`n`U;;Fa3;Km~V+D$fvj-&%s*jv41WHBL0E762}-nP3mUysf#$e+c+;H>f`?RuZ3~FO?bZhw#WIJ;tk&%iThzS?i+n#4aBea5&PuuYTQ>Js$)Nlbj0&$ejmx-GTRINb3!Cf)BL+w_aZvp|5GK7rE)cUe{?p+{bnTQ)z%a7_cp*iwhQksTFFllzt&|uFZS<Cv-1xPMV)`Bi1l3NfjWGbiT&@tPWqd!e1iD(8zP^ex_IuCgKxNBUFKzYTE%SZo3|{+y>zHms;zH~I4k3t&*C06^s0jXXWGcPW`{Bo-#nnA-FY|Uua@|xEfvsz;CAG>dI!$?P&dAx{DS=!_5u6thcf7&R|)Y$Jj}Mfwr(MwFLD21y(X5zyry-=y1&iC^S8VPf6<?)TkbDdmv#SMka?Bx!G5ca_hN192l35^FXBA*ymG?UFWBe$=rK6o!}8&8+6I3So^J)dapxxNlMW^A`kMpW%ererj5tp(^2FCa>V^I0dQ|GKO@Af6DWnVDKZiENeNgN<;zvD{{+5#caSwNR20wEg>fAmP>)SO4eho+252nM0G+W>7VZyz=EyvE+KGwm!9)E><rBAl_mSzu7|I@FrpX+2H&el<==h`NiSH#bDb<q9w7UyopZN!;ePkdvesi^<Qn;18~BA!P9c;7Rvx`a6Sb+J#H=i&MGG+lf{seXvlIvjOQNJBn@Mq}Ld_<U~}w;S=3%i`Si?1_55---HPc!fF_xeGsIt9|@6_?)c|UW0tx#$mqej$poR7b4EXD6G5pY~<g|h;>|Y2mNo%M;xcvGq&g5wEw>BH~pr0@IyVYZ*Runp4@H}Uw<+k_tgd?`j40mKf9awhB5iF{|#lwiLbdGNB<dVc-~D27T;WS5Z?d)eU0bQ0fXJRhPTV``KWDw#2-2e`Q-cJbH~E3;Ty(CeBB>)a1Rgcj&WZn;5|w|0r&r#cIfY)jr*-`1^j;Fq+WdEux{vo!4doaT993QefMh^_ihv9AHE;{pbdCW_6o$flh)zAWl>*zjyvopzM)w?++)42<2|ZFP4P{9e>M*aMgFZyBcH5isArKrl8=5#N#w)#3bW;c#Mg&@JT2pX@*MT-r{Qzf%(vp}1J`2QPiNut)QD{HO@nlZ^UFEREAk=Ytm=dPv(O9o&+Pl+8(X$T{G>a0t}XakeDl%>#0e^c&r=i5qJPFf)S=uF?305Th=05;*0*&8KDT~$2Kn4g!aDZdiq8eTk`O2J818{PSMfP|;y%pF%^UUS@4<BKzeoS{J%|%H3G=PJL43;}!>|tveqRx=R(wO`2jqXzMeZx}+~tT<;alWyG~@Rq#g-xeib421xOpzdjhlly1aC&&`1wmeX*%Y0JRhIed=l_`t?uIy=V4RCkNpyLyEhtf>TE)u7k1#iE4nx4J30`4tsha(TfGqH)_BC(`%AK|uU~N@!?w-_LpRK;uQU2boI)M`>;S*xa?~OA0P5eS74muh73%EdjrneAf^p}q#Phw!NIb6(`onk5Lw|mbHrA?wIG=c-e=dH1qBW?9`UJUQebe+<-#2dX2X8|@UAOc1(j}1R$G`AgF1ZNz#@qZ;%GaHljByvdM*r!5iLXESCE~<)K>ks0#5WX=!?`dSQMank;O9l-`BJGW&PA*H;%lk3&)LN(o+-ZNZ$FId9))`#^b+DMb;WrpmxJ^2`Dw)A{h-%%!Z~eyQhZa}`^fX%O4PsFQN(}Zf&QnP<6dpI9Q{3eVjW8*;huRo@04BLBI@$@8}JLxuP$sQ&c(E8$TPDC_HEA??Ax4B@y%I?Z?0dCpSwd)Pu|0N{vOE~F%&-U8DrQx+_z2x5hv*k;;ha=eJ*?rfB7raC%PN<^EW*(-!I;swLRC`f?BBChV7WIWjNliZh6_&+1z~_>X7>h*Zt8|$>U<cd8v!JEaGg`*^O(O`aWIa>|clbzePCS^DE6fDg7UelsE>516QSv*(=i|{<VSEP`6z48$bQH%&TL0>2GZ3d_(-!-z3Y=B}Pbp-Aj|?W1gI!B-+wjeErltm!<zyheYXr|Csn%+23$}VoM*De=oaRd_&K}5?4DE@ssp-bwQlo;gY9e?Ck@Rr|++b)889)U)5#5^!Lk>JT1PXu1S5CSKnhBU!S=L?+p%dyX5CmeuKY!yv)}WF=M;*pYsReM7c{G<M59r>EG3aaZg($Z)5AhOC=xAtH{42&ZoB6?<?u=%JsT_MDo|tGv~;7jW(ig<@aQW?>l3j#I4mF`E>2gzYAVoDgMvn(SKvE)W=*hGe*`Ut&#Ya>y_|+_IT(v**7h_Vja7^J}dLO-Y#DJ<L<~mZb2IM$L~Li-@K9JsXuuPd3vrnDE(HP5#LmF0iNHc&WEIb(iF_g`SOL-?sk8*UGmZ^{cL4TQ_Wd(*FuAB{$#66^;Mw%{hw?{1^%!8WZO8P>Hqgnwxz5&6w_3qn&w0;LM=uvLM}=zNiIruXDcbwhn69Gk?T>*lk1TiQY(@hk^`w#$${jSR8MkCax1DgxfQt$wGO!rxg(omKdO$bv=Z5mT!Z>4xdyp5wJup{BXVtWH#WrssLjX&$it{#l82GUQu~s}lBZL@CQm0vQHPSF$P1{$$qUHeQokX8OP)*ZN}fxOpngt{AdjTBC66SJqYfgEBQLYIbyOpD5ZOo$r+!5aC$FV;C$A-Euqoa^ZBE`mo<(g>o<)wN_8~`-r%;EGr;z7SL&)>Ui>bln#pI<_19>TVK6M~@K6wtcH+c?uBDFPnA~}@$899_Zm|BZGnB0?Eo!pb$nd(FCOzuGSC3hgVqgEidBY#0HNB)8wL@i4WA~&IaLT*BCOm!nSCi_!Mk^RXvsm|n@<SJU>9an`-v8%O}pgK~W$c|)<T0|@SQtUu2N_HT-P~FKc<jQP{1E^l)0CEdzJ#q_j4{Ael4|0EMAh|zz47DYB40#&06?qzYHnk0THhBiMBY6fnj7@PDsvlWt4RRN9Cu(i7(r)BV<V9?Xms1Cjmy=gghmlv3w@}BDw~)6}r<1pnf1pN@e;^;AE+8KuCs4m7Cy@70=aTo3zo$l!zbD60N0Q^nyQt&HyU3fV%gCF_JG8<(bO)Q_gVvTv-A`Rd-cOFD8p*NbBx*Q0iF|>&mVAMHiJC#aL_W)=_%w9``84?`br$(3Ii4Cxjwf%UP9bk2o2c{1Ch|_|V)9P%Zt7C<Zt{=R`Q#tT`>1os`^bB#6UlqYTdASst>lf=!Q_qP71W;O733w<&g3QJ@2DNf-;t+M+mWY|M^L{Yk06hy29d{;XHuJxXObsV8<QuKM^pXDqshIfHOalmO{rDLP097CuH^dUYFgnPU5!m~X*R{hsg7i&8d-fgkd?ZSl~yJfCwou>$R6Yd)E49hWIeS9Sx@dq?N9DU9z`8P9z|YAokm_rUQL}%UQJ#@ok3nhj;4l@qsbGjZ54GAHH@sZ3t4F=veHH5N#s>*iZ@Z0lQ)sqQ&*DLlVhk`$T8$Y)a~R$<RjD{$VbS@)C1&X@^NYc`8fFmbr1OjIhFc7IhAat#*xkBH0myL8u=J?Gx-?#Fm(s{F!?9yLGn-J6s_>?PGM7=Zf)nNr>KeKQ{<D>{p6G6Gt^k}8S;5*68Sv&3iSf{3i&ei68SRuBK0i!BKaKKS>~(sG&!A|LOp6T-=nOD(s-Nt#It@%x7pNl8|$sqWK(|=*GK72oAuhs^;EjsW_=Z>Qh(G6_k-dS)O}jv{!x6Kx>qaQZ;F$tTeZUdsrU$WqgJ?|6(6Fm&<gjz;uz`@t?;}kUQhi_D?DF{H&Lf*h38T6D(VQW@cb&CKpjt>K#r!))C%tq#cQaOwZc0`@oMU5t?-UgypY;UE4<SbkD@l!3hzM0{iyY|!aGy3o?1;SykiwNpqADO?_|Xu)Z*mdt?iAqy=PPWk@`3JBiYgVfOu!s5?1|3LsMLmO|d(*9QhM!C2BcxDXJ^A9Jw5S-jz*p5jMqn98=|y$EG-&P4QFeKV+pZ$WO_StS#5t)I%>{3Dt$Fd>1yw<*CKU6{*Fk#mE+Gw?C}yIaPVjsl~{}80$I5$z}iN%;_PU;!HNh&#3w2XXLk9;T+!bd&M6#G{r^P6qlyDkX<;3(rk(=vnlqlnX?C*;tFhv%d#nUq82ABRkd*9_lo~yQ~Vp%LjH~XnEEqW={@pe@~>=)pHLr>pO9ZsUyxsLPrPDN{4Z7Q<A3?RVrMqRWvK4tGGsTKz3#@ExUo)d^gXDRY-(7^rp}dE`+~Dkuok6k)=se_)s^f>R%g_e=cM4wDt=GRvpM5=JokA#GrzMb{)J8PT{gw{*%W6{pOT-lzFBOFZ&UA)?{WQZvnjsCruYukLbmWc+@U@sKjeA1!>0He^#S=B`6k-~o4GvT{C=nAP#=&VFjfxr899gin);Ufn*0~_16iqBv%jd0WTk(zk7|lvQs0o@Fu#}79C8lFd&!@D$?vaQ+f{43VQqfa_&(NFhfT3Bn__Qk^P+lEeaJd$4XO{hCbbsThg^$XmrZd!svlWt1G3Wk<a*?WY>ES^4akAyMpQp?BXR(>4mp7APxU4HlWSAG$+gMVZR%2;P4TB}imOmP$p!VQ!lt+?wFbE=xtg_g@9a>-z3Bh+pRN^t86DLB+x~}a|Me&B|9oQmlSizv{_~G1-8&bP-^~@V{!e}2PE^0;)cymI181c'

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
