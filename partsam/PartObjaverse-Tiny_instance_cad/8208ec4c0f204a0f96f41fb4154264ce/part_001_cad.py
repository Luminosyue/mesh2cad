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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8208ec4c0f204a0f96f41fb4154264ce/part_001.stl', 'relative_path': '8208ec4c0f204a0f96f41fb4154264ce/part_001.stl', 'source_sha256': '97c17b606fc8fff77255bccf97910290cdd68af486904619853d81c01ff3f9f2', 'input_faces': 1016, 'input_vertices': 622, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.0072652059607207775, -0.4999997019767761, -0.1193392276763916], [0.3249409794807434, 0.2768213152885437, 0.1355399787425995]]}
GEOMETRY_BASE85 = 'c$}qu1$0#B_wAkF7AWov)*u0b24}F~6bUpyfJq>@1b4VVkra1|4qDtjKn8awkfMWI3oR|d;mtXFPdnlL-&$|I$8Vi=_SxUL=brod{qE$~CJhoL&S>CYUL*3+kf4hd4MQZgk<l0!(YJrs4iWu|_lg{1G14h7|2%qD;}(sYw6YijjbVNrBl>md>sQh0SGiMpKYy!Vr`~=0_YLdSzIWe_5yA(B_2?Jj=KFOCi;QsFh02vG<!>!r*xx$B`v3SZr8@;z?!zOhiLROTc8uh-XwD4L)}QzPB)s*nE_an*n2>i|ssz5unWg_DAJ?mUf;b(c?}%+)c(Ce!;*HDYM_2RWoiQJfPqCM46U6uMHC9ab_V?s(7XER)x4+Z#Tonh*^7eN;D|1Wzzlm>>H*5*x+iUl~sr<!+`Txf!%-@Ln`-bvW6V}hayenb-*!CR1;a&gE0KcD=zcl|h<$rQa7HwbPKSkphPp>H-ymh?#2i8^IR%18vKmKWgXxEVs)3hF3CZ4xum6aN&S`&Rfd%D7CufdNay?JADV65`3uZ<RM+cZRZ=fbm^k2%Pxam){I5a-nCtLneHxvBiPwKKFniyT1v=Fhi6<7^&0Q}fImbY1-_{JdQAZ!~MRw&Um5SJdA*bgtS{PAl&`{44V5_K()5b4~CZZO5QH@b5pOpXT3kr}EY}W#GTy$ztV;J)E!ijWpn2e3izvPd%|fwSRr&AG&>>=5_vy^2XusP(Q(e1H5_HA@ZN5{G#^4)C)DAX4ABOZ1$8}v^;e=<(+xI!hgeuKHj{U^{MtB)0JYY^0#Utj>o^pZjEp5oeRF!7w{h|ZPENr+*IE6FdcX!Gx&MWl(&W#(E4}!ZrAwcwBw63pM3FXm)X7axm;&ID{uX=o3@K_>Gus7-+qhrz8-&nQ}eN}YoffX>kEvp$e1A-zkUz!oj)U=Or>^d{?8{UZ*(F5)~Wr$C={c-HTW*#G%2R>jgvQ&w_Q(*c5MIaO6BK2O_)zg*JjNpA|COVrbqm=`!v2epwf~A^^@$6o$B}HrSfL+zj5DJEi{gC{*&^~+b_XyibbB}jk|@>e{PIfqt~zhVX5A~&J2vZkaQze@13o@^DFW+FOFH^%{wYQ*XJ^$$LsuKRLtd2e$>><YDY(`*ZZX`s=Vvn5XAp5P5ZZVa4`Hm@e425>CM~T^+WvCdDduu9RCaAyfP5~>!H=^_x(=g4RaCV&%K2_)9hE?I&cc+H*>X)YvcAQ<?Ri#;=VtR#C^+6TBf=u=fh6XI{sY;H!AP?`4ihcL$u!a;S1%B-CN;r8KC#IFEW;^e=@e$uvPoi9@1QSXZ#3^)61w&Yy2VQjqpLpze{OtN9*wm%M<jI%enV?^G5jvmy}QPYOBWY_yX|<1>m{HwNiik=Laj456%JqHlxtr9z9pyIQkX$y|+p0!G7*9<!wFl;kiDQ)P8GS^cDV_KH|A1<<t4W5!MR*n)8gaJ?0HZnRhD_^q+|4o3(yc<XxqF)7Mz<ifmNgHNU6w_Nyh)Z+qA^e@D!E<;|VGSVxu=AE)&;E{V3k>(93rm5*<~L+!tdEAOne63=D*uu<<@vXk=Ga@*q&zvVFXkB?E_9M=o$!smw$&1ch9#JTuEpUZ4qBS!Nn`xf^tk{0|9LwWoDY`<#xhr_71pCU2;bQ`L?En5Y&W0Oe-HLi1=@}{SKtMpLbUMd3PGG9H^&-7Hv+oI;ILHii!KbC`=ly9{{d1sZOc&_t@vHqpo1OMOF!T(Wd^*0Y>U8~nM?5Ojkt-_dXTA%%kDeuU3QOB3L)3r_gYE@F+I-oMv1>deaG~V`(h*NAK*6}}DZqz(d%u(LiFop6?>(AOB>~YJLH}_4&e0X52w!5vw6~swgQ0vWkcIi&E^C#tvk@L0Rno$_1w&hdS>2p2%8PBz&qs|XTpM}a>``ESKoFD7%QvUq`<;@wP=qJZ}=zMM);IH$O^YKdbt2f1d)pkF1O6$q7JRWg!+qUcdw_H@-GymI0-c;UU-a$L$7>fN*_B|UkznDxI$Gi4vKXgvYi+T<!k9oRPM)aRX&oqv;cs2M>9gqH#Y4~>SXN$Th@4WR^`-yEpr25;}ZA6@Daq4foSwh!G>$8XO--vN)PH;J^dGW5S6|s+sth7g;b6a6uZ=GCUY!}a{ztgu2*5SXlVH}MM*{{!4p`r2)S26V4nX}d3zVQd;O^$b4s=msbb6P5Ity>o3x@al*@7f3cVM_GdEC+R7HgCN{KL0$!c+5Xp$C26O6Y{CE`GVR*U+vcG-;L4v&#d1W^V_z>${UwHD(~pM3H`Z)P5X~4Z?kO}@13>(m~EEne%qM5OnFCWW$+cF^?GNK1MpwJ3jOWvTIG!wmA9k6*Vle-w(SD{N8#XSbkKh83~z>Zc|TftW59jzPl{@PFzUyloo_V4c#Q9@<I7dCzRqWMXGZkTva7W}JIY34p1bFJ5%pr#=XLJhqrCC{toB1Q_nX}s=a)yyJL9ioUzB37t`oKj7OfBSz-YAZ;h+P`=S{A>bx0oc=Y5wk9+IcU`p_o{{1>F$t9)Ee@XxBE-$q0skLe|qcMSH!Ja%9M+C91+*4rLMu&)cY98$Y@Bec)?B=E2Ke2<oYX^nAT>#Op%7tvZj*47co|Jqsf=ZVuWj?Q;MoU)m)PQ7Zl)0_8<BWLk*h*P7-PVateX1I;<va9z_?{Va8-|A2T-m@P&R3!m#@A^B&W14Q-zUH_Q*snEChWhL|aFg;qe**8BPgaL%p02lnn4fAi#=Q458|<&Gw4H7HCSV>rS^(GIACLZ?7w;Wr`rW!8vsamcesQ`J_DiWwYCm&iJf!2^jETlRu;zHo7kB<q-nQ;n#6OV*eAhMF&c^cx=!bs{)b-TWAXa(%>N6NGXHH@rkBL*>IVd~E<Hi9xe(c|s!2Tu6bM(X9<#iuv{ihA~M;+Q>TwFe?>xCKEQ+eBp3Rqt<%+dA5HFTu%PTyRJpC&2Rt!KYtzmTP7f_cVRwtt^@e=|Ey1E0yc&%51?rjh8M56>aa^ZV$}V|VHJb$0)ApLe@^=1J>ji|z+qNn_9tORqt@k4&q){mgOjTOxJ-bR{VTKJ*>>dD?AQM^-jc{@?uu=k0%a&-~AI$Nq5y_zQ0^|Gc+=?>$<1&-!9iZG(Ouze0Iy=cdT#$PMiuuDFZvk7|JaGwK1}b93IubA9NHetWf@u9x=2&!WBit&yRo#y5-j>GL`BEJM3&%A@UN`=tr^P4iKolTKouy%nas<IkknSKKOw{=dGr@@9&!n8(I+*LlzO%0!%_P0_w-@?d^D^E2kH+#%@aH%9AvZ}Xd@ym53D`tA35bX+)^ZB*VqY(4TUcTC^ctXY%kKFjKN1aZQz%~k&%FO@eZ_@JL}s*X6Wzm#{K8i987J)&_P!Ecl|2IWT_YtdTjSF5w`6J7I5VZG~b=sALGPdDX_*lVbtkqxmg`ZP>=TRirSW|2nN2R<AVlc3*T&8fV@Z?^K*+H<f@g&$p~{kGBN81H^-T;GWO=h|D?x3=Db`Fwm`9e36t&#}+#QxEwEEXR4lsHDyW{j>IUJZB?6^wU)TV82x8jmB|?mxe#{bnf^I`@mAwF>V(1K|TEbWT@J!YhnBa{)qNUT^R4bZChcyK0^M^1EDwvSTX`U-$$IGgTaT4Qr^}k80|7O4dxfWDadog-*~R#EA%|YxV-~$0w!V{MHyQE9^M+$74u~Ef_iRakGY5V^)4g-=}-0i%Kpb=?02H$5WjqlVH)q;_qsl~>J>#hrfZ3LhrBiO?-+O6y6Ag{t#C>3XL;^drZLvhs#s_KeP4bTiub#Xo!}pK1^wsiz15me=PtOfr`;V7)Za+a2kY(I{&=q7)1y=e4g}Bj&Is#(`6c%V#Lt)n@z>78dtJjZ$Y<U&tq0pdw2SrHj6(_f)$Dq@uXYYvfH>dv1D~fZ)|d9nl(&5`&`(n3)p^Y2e^_~A_BOm1#H`eL)fRaLdFI@Ye%|Ajo`czn#3CQhdB{K5&)d>GhJW|?V;XP6C9P-2!WW0U`=?p<t)7e8^Z6du_KC{~zSlq4KmC^PaDw{JJPiA!THh;gEA$TW<L6IQ|73-f|Mxs+K@V*g>!twsUtEInNnJG`Ym!Q^J@aavbLwvfG*{kQcOvTF^L`f;2LIBjPOI)UNaL8xx*qnfH{(-!eP6Z}>Ww%V7o$A=Ih@<>9&k88KQT{ZzqNEY@;ve$?`yl>={cus{8;#V&c}8%(*23Uxm0=QdSB%8^v7|k7c5789(#j!iN=1?erzA=^YI4shZ;S9Qax%v_`IvY7qDylS~niTeYsCCs@BJIUAlri2S%g6#0H@ra>pfTFXOvJc)xm|{fNd{z8d~FMvc|$ALmxyGmjao`;XQ54(k!`eqwBzH%4{F0!I?m+r4ynADifhI6U7lUe=rE%^QomVE?l%Q0ISpwaW1KoR@mWMSPPZ3G(0nqsDP|3r0R)=-+U==3_tJ4)KR)NWh!3Mk#L}ml5;a++{kCxjs!--dcF2em^mMM(Me+Yx+#Y>9|M7wb>y=$Ay`AE}nM@`}5=o&By$G5#kIzf_*~rSUumfU0s3vJ$Z)qQ-4?6?aG_O4&k|$eAa$$M4eII7FrAK@@^dR`~u#(t0wrn;EkH+@La{NVg2lA8KriiC%A8Z8}>O-b95ds?mxwS=RZNe>NpGM#o=!eCvNvSjq@To?t9|{;{0A@5!$7X){k{_ilgcmP!{w5z|fx)@Fo3`=ckW)zGNSgQh9r~qToYbDQ_)NOnGb5Xxw-Iz`>f|kSd5X1@B?T!M=Kb+m`yuJ9DqbI7vKrIO?mL@{Tt(P|t}=;X6z3D8yeg0MA?K?j+TvS19iqT1DH*EV@+RM_eJBmABR0r{6`4hr5wy<YDCV?RPZt=C|L`zU4jN(a5_xeDfXc8~)$#XyhH=en<1f|Moi?dFQv^(L8a!{f_2|^X+#u^7e1Pqmj3L`yK6n;}hoZy#CF1v~PJ=!uqj(^Bv6^coF`Cmf`#$W5f`>U(V-fms{938Hcd`x=P05xlRY*Ty|9D1==5~yn}!FIl4X>tH1k2{ck4Ib<4JR@pQfKGn~g-ALc#gU7wzOjK==TTl=Rwu5s#|#QELFGVtHr5&isLDtr%0Uk>pLM<{PTz;`11@^;FbYli50Z~V1-j%a7aFvJ=7qpmB?aDIo%5so;~$FY9JY}NBq>&U*yr($P(SIksSpUb*v6yhAti}fgV5}cFPSgX8a??B97(TVkZ$<gK*@<~(^=aeNj>3gpAqYLr(2kQ4IBQl_yUO(g+;^bI|=UsDF&xP$JQfs}~Cw0O(W*o+~qeWKbZ8PU~R^C`%Pwl*Uly~*Ji+qk`)_k0MYAWwsvjFwjCa>n>4DE{eua;omOTQocvGzT|=Lxnezbn{*@i9z!bH~CZYS-<F?=JgBD({GBaZ&xdd|jx|+iEJ>bwN((G+FlPeJ{;Go`3n_d1oZo`<iEFB7P$B6UlG?1^z9KmgwiRnrr#H#mZa%JdJtp{%d^a2wQ{at=SU!*tRs$cA2{oc~-8f->+<gmf(Fb?N-!h>wZysKc6DnZ_WLC5vRZ<>^n-_)N>?z!;7dNe}C-{PFvc&8YkIp<deAUOwIG-8m%WshX;86nNc{$?;eZqOu3%nd5v@W9n}1#j?OcVYUxiX-@KlFZ#LFe#QW***_C%)PKJHT;1S5@NlxXBQ}1w|I57pj8;$IvymczyV`2wu9CPJh<?Su%IW_)~TeFn^ZG`f+J0YmIK?n7{&$ccK{92p?8MhW{y*Z;NAx@U`c%CEI_5IymZ<X?nv;KO1ZC)LM{@Z>l_)&APPtSfu<Jg}%@w|a6^&H3csENk0l{=02p-FWeG8+2!)jU7mMLjg%fc5nBt|;XTKZ5_Ecat@rAb)%(?)WF_=g?F<?=6fY*Z1#m-z1rJKWfz6xJ>Vx$T*2{-CgU;NL>-%FPEiN-a0Qe;;gXYd*!Um;4@doc~j3pJ5g_i!KW^-^=q_Vqu=q3M&-a4`E@A9ExrplhE`JER_d!hmzlM$*1x&9yYkMKp=g)kxezDWK;`Y(hRsHQ$*J|`bPPfMvr}UpuHOv5C)hs!B*s}!?2{hW)_Ky};*|2nn_}pvqtEHNim~jT@~(z4N7cXj6^-X;{2Y0n{eW?CcYyXg+lfDL-!qkTT$tmRDsRt_^pwVloQ^nlQ}+Xo&gGSNFBGWH`$=^lWfZ8WyfwPvaplveo~HGAsfO~7z$b`PY5OW~-umhw)`c5K^?cu!v@ZM$e>|rC|GXQiyek;@UEdtvcat0a)o)%`@X69^y&JLkuIg$%RC#-)>oI!2;KBO-Xn!At_@nM&{uw?J-)o*vN1Xiobp0^)=hEM=7#(ISZ=2QVlG^@l=WCpybCJJw2Ik>Kzu~<mcp>h4F9h`vTmt)q>B~`{lgnYAT=7ZI#~hZG;Mc9!@5$z)TRPu*c<a@&@NWcv*Xwl&^XXJU-&33~HYjf{9ID^L%#3^R-ko(f{NGJR{g-O3?d7<A8F{udkmuw8?1vx!4nA84{XL3VATV0<8TS%=u_mbJ<WKc{!?FEu<mu<H>ywc)1pAFyZ;;Q0And<aXVh~!$ACnbf3sJ_{2ep;fYwj`)ZkwZ(|OR`bzSF4YrU+>+sh`wdyl2xevO|bJNoNan`&FbCdxbGt+0LZJ<J$ZSnuoM%^!ZydNY?7Lq95CSb4{OeqXA+9_NSlqKK2JDf(f)nb;Q<tONf8B`}}Y&!qRYHmIw-HEEgIT5qS*>ipn5*Z}?)_v1TZ$uYX_nAuw*pBxQw?ml{&w!5uQd*xlrBK3UAd9t(4XV!pl#J^tz^>d|!){o;Ec;kGuwxhY?Hum#hdn3-oRXB$`mkRATeKO*F-x2fD+jrXUY*pug-y4K=G&Zs3>G%NN{*vRgZYj;vw5~w>R87$jLzZ<>zhOJjj_Dq2e#VLz-KW_%A3%L}44t6<dtc)FY^sys_gZl7mZ2hkKepi_>gPZk-R~OPuj{_Tu|Cro&GTe4+}Ab}=RAFjC~tP`q_&xMrq+YgzqIm(XI|<*N`FsaOf09o%kQ@CdyLDs@jIBgRp5W`n9dt!+<sjb>}P5y@0?Nbkov!~X&jqT_YC?$3hcLDd_{fkucy3Y{&kGI<Q3K5+NKrmyXLm`E2r53--Sm<;J&%*pHMy^R{O7G`8oJs$%FOo>M`vX9^MRZfqHm|^A=mb^QfO**)i@WPQv?3<1%M8j&Es<(}3L_^m(eTR^AA#fqiy6oEun!>^eW%=e0)s(9)AMPLCeSJE!$R|MB0f?P6;@6nx}v_$NQ4>!)q(DDbsDt2U2i$9LZhb20xO3q}8py`=9qw)UHpcXe)teO8XFIFA~)5B^4o){jx_t@bO|=L6@^uZrURe)W2Me|>orasD`QQuC<zN$c6en@{heKL<U-x;gnc{4?M?pLyp!@?1|oDg^UzN6ZtBWtVZ^=SOiKKi<T5=-WBZtN(8oFrPTO;XEh2fb#aZbeg{{Uo^hg-1LKg_)5$(>F}Q7+EiJ2bI42`S4N$3ST|R7P~KWAW2EvI+vE2c3pXq8c##YJF!m?B7d+Vw|B!pSPckZgr|&6_G)I*;$|lBrI&Q;$c>D>qZ7<uQ9i2mPPPpL;;`{UWWZ~)X{q9~I;v8Oxaj_{cez#HfFXf%xqOfl%ithrBXRlEY#hT)~dyd3fKaTpJk>~Ej*q=4)tKVg8&A~gbPSf?tc4jp4ByYBI;5~Qg0L*V`zoI^KCc}GW;m<nnS~vM#&^Rf6)9a16VC-|dr2`+f5x<k_+ZF54gAB@>eIn35H#bt=$eK-g<5gfA_50*d-qA3(@{YmrI&U~_*oRs(l~mpul@{|`zMsaceW4WmkG{hD`-8q%M?MGQzMm3deaRE9&*j`zL3vx-jQGBKdI;9LB2~aQIzLtQuwD3W?o%D{uZ_St=!b{{-n{cr2kaXYPdO;OnZ6eM;}2mTs2ha!e|#PIpW=DK{eC+C8(Zor@2Z_i=UJn4faYm_sIR;|wkm$dv1f(ywiBU<6Z-?s)hd0|d|cJ+xbMU;^tXse-M_d}jzB$BA2UU-|F9e1@%w(l^R^#|`Deif{BG}aHnnY*2*k0@Xrpm!7gXLF(CxJ5dB%qC2q~*4^lw&E&%K;0YbtNQwnOI)qwz9~qi|DsSFt9_o7pcQ&gU`Uv!us37@QpY$#hZ3Z}u?N&iDAehy5jZ`@+t+Z?9l|-?UAhs=Rq|Eb71Vr{Vg%A+r<uzZ<LXP4?cu!r$i**0tO=tdGAqale*RF<<3ch<)ZF@b>xS<G~wcj)4DA?u^E{9<SrlwemOQzttc8GiWV-KUVoR>hs({tk26^;&(5TUCKLd*Tnj}_&Ux{PCiDS?=#@sCVHOs3s<*9c%Dafao+q#X}pj4CBgpeX>ZK`>qp@CH`S9XZ(r62^YxWi`aRmQlzh4>Xy4z<;P=Ka3L{QTLA<}$Ev@IJ_CZCIcZ|<~eSW!#`2BNW1>{ro3EF-BFyudgyl;Q~9lA00q0XO1VVm;S`o~aj1C!`J!uF^-_z!t7KefxJ^MG?yE!_9-AK`C(W7GRaHc;Mq68+1l+ZpGR8L_TACI{j?c6d#Ff3!7kh4^Khm~R8H{u-a!;CX$^V*Wfh0l#PK-ClWH!TUJBTR98o3=Qq5x8jX4eyb+c_ZruOaQHtsuFq>*IbQR(E$xFmmwu1;z6zsudGn6E4=_I$jllWFu@R`Z9QUwZAGT=z=8BQX^Z6+Bi~8Ge-qm+J^6|ZZJU?E??@-&$M0~%Tm=7Bq#d|@Q`KX5_7qI_``iObYu>$uk+ZXFg(H*+(nV&Wy&V#X-m$F7-AHHid{15x!d*F{w<?WGMk>|n&`29=TSgaeL4j@kV@z}SfZHD=<)+y9anBOV%ha(u*87?XB8hZf!$~C>4=2`qN)N^9)BR8K$K25+oZbfK4m<2B5TsQS=#9!M>`=$9MWS=*0d>w=FvZ)v5;rSm?pZN#kJj5USCF^%z;h(PyzPDU|fH)&FU)KA69*2JD+Yi5I&Xx`QkoJC>_tgoy?ihOtCG`Kjh`tXxeTyk?&k=-nsgzUwU1cgL?`pXU<8jdpea~{04^rM})mMLKV0*g>=P=0|EAO0N0`uyX>^jfeAA@&<_+X!NeE@#n`MD|LA1H+VM$*?fhg;tb@e8-perwB=8^60tIvnwnEWkJ_^jgQA?P(PJZxzEnsK71!{^#-}<*jynXEqi^V!tqEGW<u8kLwM->r}+=K0?nC%=UwDUbJtf@@AJz`kriFd5QP+xZS9?`jObD?fe0M_mT7f;`eW(<J0J0Xdv402%fh#et+r7$A0qIW%SDkJb#bIWAuKj;&9)q5Ai$hG;#P{Yqndc&(O^H-c)Id*0XiMWAK?b<D9T+3Y;7K{2F}E>==)$F5&l1ecvPh3P-TtoodCo;*rnD^KnSH#`zMf_3Rk$b4B&>dDvg=4aIv|p5)+@KGgSOBl#EX<I1E`-qm>z<{zFT8Fju>-t-xO?^$22;ygblBm7?%LHpkMO~0Gj-{(-?-uNrdSM6vQGnrL+YsoOIN55Rb@4~Zx5C0jy=+CK!;`h&Eiz;tyYu`t8yXE+Pw70DCwysmKzj~P-zvpgV9&z5kt)l!v%!kgB74W>=N7?cez`5(oipW33T&%OfI488n2ZJx0O}{f46T<X7&^5aw;s;j4x--zg{Qtfu@_gA|_Y+34zx8~=Szs9QT>m;u`ED-E=P@HtpNwNf?r5w2fuq4^o{RJKV)v1c&jiG;UkZN@@vMcO4_UKMga6g9_`T^*p@{zuyu&#N?`!?)A<nhw$R{uy^}A~%*1OlM@w{DkVZSn~AkJ4u?1O*&M4X#7tcUM?r_Z4tmZZix=guoy57uALBhIuR(65@d#X1>w5&XM8+JB6og8Dtz5pW0b8x_a<OeB6M<KfL+NwA+W_UQKw*T^^U52=LncJmSDdFvPStNc$ePNVwjc(<M~u4+97|AF^{Dor$hXS0;bJEj-Md)AK1IxkwQr&Hc_Hx_Zs$Bi_f3)z*orhTX9#YXw-x<7Pv&4oBo#V`+?pNDhx;uYYZXamm2><!i5xK&+wGw)iA$Ee1rpZcx9514}IwLhw(x@~*qjXUe$A270o<~O6G^7g?8@%J{DpXqq?@a9P0rD(@#;2X?FJ{fwWKm3^szppzw56?TwfpK&*3x3bGdKKa%9*A-J=OO*B<gn~UJ|_JgH}!nO42g#Sjxe0(Umc<CYl}UD`bpLpzo%Ie5EauT!C%8(DDdWvH9%e+3?qe+(dZQB^{22x%0G|(pZ^rLYnlJ6KZPwBP_o?r-`~QfbXsJK<=&pS<)~ZYiJjD+$p!epKIoPKEdN5=Np29a=n=#t7~kXXWXuD+R=5w;K|a6-yzDPt{)2g+{lo`|4=~0-V(}S6A1U8QTkxOMABgwSUQWE1dO5EV{G9xA+H&1_+R1(XD?3kHaA6<FbNV;-L78xksjE;+x!~^Pf`}t%S7E&bk!$S5|H)_Rz%sc`a0A*A#Bxn>;ts^=X*VFwPn@6r`N{ub0e<b)1-;4&lFLt@f86qdJ}+1o1^L{Ki9Of+!}=1xXlhUWd2I3d$t^$AXD@xC$*m$5y_0w+{RH=6JMN@UAL5<l#jhFpT-422=CPYo`Y=W=+F7Y3k4DtZ>EkJD<W(lm@y5XQQvQ)xxZe%fg8w8I?k#P>uW5VuY8I6FSb*OWi#9Bfx4bT=1!clzw7?ep19`D)6AKqbTkr^C;f~Ud;yr~QL|u*7du;KmNPZA?MdmEJI`Lp);RaI=pj70wW9T!O?NgncTwk4aS)FAcS%1ygR?EqY|6dmL=i=<If}c`Lnc#XXmobu*yx8?<3(ig~+z+%pSaerPJ;v!uEn~9_ZNbfWO;_^Gh^>q%W%+3T!18>=!u@7}-+c?Pm00u>3&hH6=FmsVXIfx;@O}Euq5UI8aAS(#*_4^|Z^^RR#G*r~rTm_ky?`>CyyS9@`Jbab$IF)b?Z$elN!-QD?#_9#Bg<+MccCq1vTg`}nEml6`@i)4N^Y6wmUV8iyQQaFMoarsi@k|h^fs@u9u&d9P)5^7<b+$c6W^rmpuL^`+sJLA&o<%}v~LnWA{L$22eEE?VbQOs{k?Eq+IfhDlNfn?{wo*Uh$6TEwfNnz{Ab^wJ=HA}i67C9qdk%SH^@z7c`$Vw;$Y%@)a8lu5vQRD&PI`XuR^XKxhiaf_T+ky6MMK@29g`@#r0s_52qeazv0BgXpg7-!Zs?;{!ouO_arx!ZPbRkC-L{JOR0yZ#KLuET{opJK-`J8l=q}9xCgOtVYCIeBNna*ZNYxT!d<q&7JQ9ZII+)KfM>X6F7a8~m&sitUhS6awCB>kMlLU7Un7=#h;B~YoOUsa;FQ#IeM<78zaw{%yolg8v_*?gPG0jJMfjH%@M0U(!Wq=!6GJ)amJQ@idU0~Et>iC~J4tQ>^=7wBX8C4vTggrF@|!{tekAn};*rF|C_~uiM0X_~NZg(}h`2p*6-s^!#zGLWhZDOMvFL{M6FUzjKlz6Ak+x4mzdVf5on@`q_A`jP(;iCPm3k=qM|bMEUS&Zn-^{Yjv?o)BvJQq2clGkSPJNL$8T)~>ZxUkR-nq+ikjp{dgR9f7Ml4(+YPl{E%fxO=>`xp{yBcwImQ`bnaQgKiZcd-(wA)d_>C=P$ov7;)*QM=Gk=QbyzhZvBTOf&;v*#Ygc)wzNM$g!jdv0O7$@tE|u`hE#9Us_Xlnk6Jda_J7nS<=)?BoTvpe^OKXba9oyD6m>`R`dKoXm;2$jKTJYXKKaUhpj1QXWp*vv$lPpO0n2)gTrwkaj-y=Ro3K?CV>oXAtM1E#-A+_u{pA$OY0C>}e;NuVoFCd0*CnLl&&Zuh>S1h_{m$yC?l+oj>K4v2NKxEp{ijTp$+S#|K!ra>T;bCl<~|EL<UC;nEQcca<@PTS6>cUt-}}5DV9UxCL`MMJ|wa(122h<#kwRohZHdOubmgV<}tsTsw#_P|otXwh&*S?dh}foIdQMb!cZ`A1p_%1?$C5U5?mBy9MjV#(r6gxCQ%WA#$;-r(CSVLc~|e$FjbzvM<gej%6QQLar}yIP0-5aShtxtiu-M0%;3A<CYZed!_b)7W)c0(H5_=G8Dl@DS|DOTW<fqd5v5vb{dumUz9ivZ7F|1y_@&}@g9ocHI!*?nNDsRxm|7<MSC~xX%yl66Zhw}{mFMG7TwLO%%t=u-;F*Y)J=&)h;44^=aw$CJJW7T5xy32E&2=BmUb=TGAt9j9CaDuGW4lWoXIV@smqY}_~rI0OD%nxItO(o;vB?HsOu9qA)Y`zj(7s`5sKhrZh1@lJ@qkSk*{tk?*s0u7cX2{N(mouqThO5SHTB<qFWJ*ZbRIL*L(P2a-x4E7HLmE;X=uUlJ}I0-IBO9{ae#+NfDollp1cyNUjFCs>DB1i=CA?EB!rXp)AkFGLhTvXTD<r&PF>U%Y@HD-gBMUcP+r8#b5Mdw=5%mOxshojBy@&l`o>tBH9lrf;0I*9`m|~<b25sSINr`q+}u=NF7XFm32^w*H-l^6TT#41rm#HLJ6dAZI%faLfwkEwwHe}`I6*wQv{cyZb;maw!|nyyE3)drM>)0dzFO{i<W+xn6}{5ytXp=)WpXvu%(X+K22M6YM=kg5;M+53+7}gUu%Kw!Kb}qoZ<ET=(CpdOg}FydOl?>uWie+`5e=2z3_aF=lS#%yo>Qi@tzwk|INW0dB0=ym**(WdML^|6gw5QaGAYq!5=N~6Yi25KeK=notx#k8Oy`_vTa?&!YyRkCE{Oci*^w&WnXuZUrOvEFR>!XOL+(42#%MfUfd#H6Gq&DSaeltxvr*{?ZKjRQ;SbsV$tQi%F0oMw^3SKuol%Nwh{NH-I{nIaU}gCX)h!ez22+Lv-Sy|M2V!&diqP<n)I8*+<SZ7KZ5nvn_8|(&1aTpDogBHr^*snCKj$8v2Yz}3tmPn+)CPlZxai5hqkADF|S$7wrNKR<2}j}SGD{%CyJe!eKif|r;_Y%6*%@~o{{xJ)-YK+WZjf;Bx6X%g^UT=7sx(G#)|Ayt`OfMK0{mnC3j0wYWXMsAF_#wlj2oW|0U+}yFo4yv2aO<g-b>(Tnb|0QV|Q6hFG|?#KNT`7S5MgxYWeH%+DZK!F}^0ZYe}9w!d4xCl<Z{v2X>6h4Uj8t}wB1MTvzgMl4(jV&O^>3s;(0xKhNz1rQ5YoH&5_RUl_`KSMdUly^&Q1GeCn#BHcs($8bpCKlb3y1H9JsB1Hhr!2&)ESS0`aWL_Z6v1{%W4A;S*Q7myw(wJFM^cMDnIiaC>b=Cj5}%-cNPL3$GW9>imx*ss;@xtETs%3!pJ|J@=o3%gMg5rgG3^%=!HF!;Ux>eu|HsQtYJmv;MBgXGPiQ}+eBrgi-=WVP+WRR_=)0TtbmBW+K6}0DZ$JH~6AM3$*9bR=x*zd0+SBRVkK9&XGlf{VA=HD2r+E1aUQaD$!@cYolquwg)2AIpaC1rnay5uO{1D!^IdvoYG$*b?f8k2e_F&OvDK+Tt&obcxXnU~ey3~z`BdPllH>NGRGI3>IUzgYQBbG5%jO8_HSLU@fi7V45fLg|J1^SjFCsKqyMQB%`h)+{Petv;6;Y!o4z_QX_zRk#q?nT^`xIabkY`4s#J)0u@97-RzEF{;5oWyKNyBF;~lmYbbL!SW@nWsh)x1_z0_9Dsv`ix|GPd-aa-lGYhu_^Oy;`Q8uf1n8NO%dFe(uCJ7W|?qvX?t*A*2g?z@h`!9{J{DyO|AfK!TE@V`<}MoLd3$Aq3uU0M7}u7gbN}Tt`=><t%-$eMO*MdV&Q&q%V2VY$qQaUTgo@n7QCId;IqWSU7#)a0kLo&+;WfHJ@SIz(U$V$7TAK55DS;q0{c6PVBu4;Ot`<@zJD3uM5khTD*6b%N+0pvWx(D?5gbdoN}t8_+sF3ZMNZ~}B5bpKwDYn}N|7r?UT_uKQeKaC8A=uMK`axlEpZUrp)Ikr!!UBg$P1oNTgo@m-b|U#Hd{bEn03FA<)?|yvK>wn-z66A743JFyX2)EUXhbJPQkXZkWWI+LSEKBS;vG+OgjZdcnkRyY`0XzY1yWU$w~WMVq1#-gZK~n2;RXm@!dvy9`QxmJBTl_YzNzUF7YnP4#qi0|1HFiX<sCMLHvR-x6qb*Zlb-A_#EvmET6-&EyjQIr|_P6bsKYB#OuX(C9!ZPiG@2vdnNTbmOUmG&PCgUPx87ev=8waUa($860v<=5dXn8d&xc`ZTOO$XTS22BKQ{ZE&2<0jrJ|#W5lNn^uJTIkMSD8cPY2%<MG=_*<hfrpCa~fGs({<9!5QsSac}yFygk<4T#$k*P{roLLa%l9l22Bzdelb!>Q$dGrVli{zv%r)EkI5@EMK~A0vN^b+wgvEBUSDcT?XXPQ<Y$Z71`V%uBLQkbQ{km-<m;k0<*V*>}kPUiKGX-SXZox7~7|w&3T)9!~6J7GTlYEx1nX?6ieX=N4bud5Pb9`J^MCnL0hOFKv-5Zm|-lqn)0%@J|g~Biu7$;p8`}VhcV<EZi*GG1QM(c7Ry8Nz}8556~99lYSG4g^Qw|L_E>USMUVtaN=;<9VrueU4E8zBo^I;I*Rc<w%~&F>q0ELJEaTr??PX}h3O~d8Ht6<Mq6+OV&O8;7W^G~vC~T%k`tYUI17C|d{Hkh3-6bOITvJkesV?m>|%E!7Oo;~4=&2sooIKa2(C&IoRd<K{yC{7_sp~f=O)ffT$OfJ+I1*`trWpoDY<!VE|v+`jn~U{W0+qz>Z-&Jx2$5h=<&qk>F2?nXip#>PyaQ<Ygi`u4DD6KakNG6Bwj;2fxL`I&$x`^bvub4QR3)xo8?Ch;P+nk8Q%9dmK`M)y@z@gpW9;#K0-g?ZW0T3oVMWe#KIk>eVqC_%bdjLiA6_K&hxs}ZdpcdHT4RL;B}N}`Y&TFu}8aQEV(7Lmyugeyo}gMpJlv{N&h9pqJO3cUP@U)|55al@*c#(btM+A1#Q9giG}MxEL<hpg4+{UqTP^KbT#5UZplGhjdmq+fy9A~B{+=F-=2IJaeMM|zX-RCV_8Ys9vtR%-A}w`9I<d~iG^#@z~YlJ(f{c`we{aWIrB9V{D-%`y)xmSC3s)y>wc(z|45-pgCugEY52JRCoid8W!5zQ7k=y^x&'

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
