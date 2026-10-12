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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8d3d39516f7b40d5aa19e85226940899/part_000.stl', 'relative_path': '8d3d39516f7b40d5aa19e85226940899/part_000.stl', 'source_sha256': '942f881b802c32f0fe71923dd747e830ce30ec0428b4292a4cb751578773ad76', 'input_faces': 929, 'input_vertices': 530, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-34.801231384277344, -28.717098236083984, -25.56500244140625], [37.064414978027344, 1.6946672201156616, 40.36996078491211]]}
GEOMETRY_BASE85 = 'c$}r237k!3{Qu8b2V)<y=E}}x?AhHED#^&2^;*Wh?~=MIQuZZ6aqSdIM6#WdC~H|l$<-nyOQob#zxh7T`?+SGd;YK2|MmOn^?kkH^YJ)y?sK2zoHKVyZjmulqND$mbefOqldEcV$B{~K5}h$ABS!V_l`^u*kYVHFoIEO*KZf%jZ`U&U$v9_>Gof7Xl##tgl&j|}*Pu_Ga(-XAK0`;08qs4&_n{+tr%2wc$DolZsrkr$J%**EeqFv+jjDcMjS7C>MBo4NPxjPPaA)>;z)fX1bfbbW^xdN30XerykEz`Ea`|#;^YHP;Di6N0Pqp{$_&DAx57h2gPUUyXs62B1pR%g`!d%(B^1#H7s(o<vjeyE`&nlhv`-V;(QMnW9tBxP6U-Z|#9=ZGSg(PY3W;vwtaNZPk9ADs2Hm^L;rh@vuzByZU{?amaKEX{Te%b4h2hQzQ$9D#FQF-7_ygE*#V(p*zdgOsA-BtVW%I5k!CwI6n?du9`Ev0hzj9=xxr4@2`<?hbU%Bu7C=hgi);&yqJ@A)dx^~y_Ts;T-j>9@w}`|Yfu&fgvIjB0P^felw{sPn8iQsu!Hj+Ru%D>CikUXMI*YHJl~ANi_<$^+LImr}gaH^1wVhZ5GQ;|JCkYov~IbD%oUK#mIP^~K~1zqwx>|8Szp1KWD)?|X7sUe_acn^jcD51qf!Q1$b_E6b?AUvo|Uy`8(g_p9T(``fDA9hOs{=k0p>cy>N>pla_NsoFs0_n-19hJPyIdgVI~)>g-FKc~Jr-<j*wJaX!`*W=X6L%GJ)SLgp@Kb41Gji~YCoXMx>rIouAJLvWaXX@#Gd{p(L^G}`fu2(+$r+TXY4<4?o^3U_C^K^dORMz#%bCgx>ed{`@+?{>hukt&M)VOuuIbTP;Ut=3r^U9q*)pUM;?ZRHUTW5tY-Eq#w>-Lq}74XdW&b=>f?i+ugs(PKX_vQ7<1JgT~PM2RDqH<sFMmfFmz|N~>(&pig8Fl+PCE~quXIQOr>5fw{Pm<!k7MZ;AP_K&R)4i^xnX9P3PyQv&D-Spyq-$^b-&de?oLBC&x|y!M@A<QpypC^j`}n~e$0~ZAzsc?McZQv*;MG4SxBDm3EUtoA|C`+Ie_v8^dC&KkJm&p9a7fQDYy3oWYy5;aKBaSOe45-IpW*63-JWqC+BIDtKfbb_zkhzF-)Ad#b8c^>+HdTukCWV2&);(|>h@Od{5MCnkM#fke%1eGy*)Bpjf<FkTtU@7{Q4l3hrYN{Lvcg>;%W2X)Z;bM_D@Vs|Cl^daFWV>3rFYh%H3<-%cjkJpF1iKy5IcO*dq_ziBw42KAf#hb#=Uz(>`qMk-KGn^QZg1NzbZvAeeGa?aOxVhQ}qPJN~p8YMzD*4t89R+-bR?YP$1ho`xr7&Fp&QfyIrhrEPEKU3ka*EUrf$cwl(C_GTX0$2Yls{9w-y%X^)_$?fwGe-J6_)juY;`zM&IZW*usH@V&a!HMTfdA+|Tx8GmiV_)j)8EgEQ+#WxXehu_KWsT2hZjI02h^#tiK8EZ3QCodopqko`10@dW_s7nc*Jvp1owmhlslV?%Ud_|so30vnF?qKG0cjstlc@6G;GXJuW`0HUsr7ZvdS&Nky)wCP(!pA3`z_jj<AGXf``P4ywF!!mMk}xE^~eKLZ&gWq95*p<P4zlXy78_@?tZkbTDtF>=WF%)Lu=p4?|S4;+m~ykZExmXpuVrL>ybM<F4auiKDuwt9$(D$%5&|mmG1nRNA9#m#a)lw$(gx!+V;_X$2xvAw~lY-g?;`ek2!y*RB5mNF?me?+}c&rtN%@I_rJ4dni`+>`)hLh{S7sGO}$QgoS57mSD})}izr&-)8zK}bY|96xtU+S7jCO@6Bx2tz20!wMQU8c<lDEX`4TQPRprjbB6^;7&7<1ex$pj=s=eFsJ-u%w@7MjXIlo@ltvs~vVq<9^`txT!{_0Ls`=^<Y(R}WcdLQO`!_Lk1hRNMR2lRTwdT8fnJv4b_-<jHJ-(Nd7@2|<7w-)OD9<==)*CP*1o?bKE`7lqNER%h%M;@qrv3A<_(S38`U!`1+-1%`yowV(v*S#5wmUTUHx6+2X>CT6F7wT~`UHj;K{4%~?y8bcOb=L7sZXZ9o?^x$=a{K(vJhJ=8<aYl!)4CV;?0<5*|3fu87gGIK>-}`^ugPQH-^g-xUu};cliTCR`Kv=d)!)|mG`T%Koo;i~eXp61frTyg`*k6=zD_<?Mvo&a58t@`fNI|~NsotekLrGIaz~FNEB96WUbT0AIj+V*u=8d$PlH+e>G5di2}^YQxY9bmZ@j+$z0_7;59X|>?_0JftNT$iPfZ^Fq@c>peT1Ex`v{XqPWD&#qvkrt&dqg>$=w#M_4>fNZRcj)jvj~kYsQtGn{j3G=>8k|w~XtR7g<_2ZF_S)>|V)T(e=ok@S6JR+MD~_d*=FGkKBFthX(0hubHQT{*_&iJn(3nhUt!P?z8OUliSBP*L(K)o7_JC=>BE(Pc*ms$ILIg|4nZ9zq5aIKCk!J<o5gPyHGhnwX?>L$?fsutNU>lMQePT+#a94BY$L4xp^M)cW-@Py>Wu-&tS`3dOxxAq-#y2eQ0hCmAl)v==s?5qQ0)Q^2m-aRQte!<@)(hh2nbM%<-Ter&b=EIaRfHTQAV>_l@sV|AtTK>s@zWifZSZvRprBVxF4Zy&Y6}^!b35N1qRnhwp^d{5AJ4c5d!pOm60{xgN7~b3GRQzGh!$zp!(&UqoLQ*V|@%n%rD(oADg|zTD>qKA&I3Gtd8H!*s{tIaMfeQ&ra^clWexobLS1^=-a#)m)F<*}Xqqd-EK_KEBEA<D2^|`~0K1b^hkM(e4M6+x-^Z*R1|Gc})K^zwGzd<o5gP%Qz&1&>lY~x5rO#*pGjz=k?b3G`T%KgM&`oRL|>~r_O&n)OABJ@Rgb$z6!(j{$S<7*Oxsg?L)a2=<AP16Uz!C|30Ai87mLQPgU&$|5nx4{ktaWadc>j8mBRNx0?F+`6lRn^!cXxdZtJ}y)XUsp<3rc4Th`d&1RmOJTl#{a`W8J&dqZ_lbiW#o=e!dc`jk{=)TN-R!q))mdT^n+gu0Qxw#HBdGtP-{m9PEesnk2&#%n9uyZpnOdfqM{ZNJKu1D^>)hm#$f6P3cx;|ZdlLrg0O4mO6T+uqd$?fBt=NtC<o7_JC=zW~kKPI>PCwe_;^}osO{*Uf!*83aHt@qc=FMIr$+#WxXr-PT(JhjIsxjjB3d0)AZcAkb>J*}>TgHzk-`-s)e)&5}T;V-j4q>j_Cnf`gv@mcEi`?}nt_Y*rW_p6$BPPO%U)W6SkOYc|H2I_Ud&X2yP+qZfmxBB|f9zBo$Nz(g|^UxT%4{+ygPd`t|&HOdb^X=R`&o{Z*m(BA=J2%f8qdC{x=J|=8o98DckKRXfe`n|B{?6pl=U`lC+PS&TjJ__OOPl@9&dq)oJq|xtiq1PLkIp;O&*u7ebfp@uM;^}oeY*DMdA@yoliSBP&l~OYk3NUA&fh#gvHQp5cK?|BJG=j*_kC9Xo9oP&_t#v1TJNvf@9gnoa(n!kd1sH$=zO%sXXN>R52f2reH~A#^Ph1_KYv>_ThBWyk911X^EA)G)2ja$<W&71sn=b%xAJhog1UX^_p|E!vyIiy<tlB~<J8K-OZVz|`u4ZyRerpYe(uzGgr2A6TjiI(4;I^`^2nabI=^;U=k0#bKgS<5ppI7_X~a5E?5N6P_GR*zec8&R>mGT`zHH^ub(K73U$%3zZj;CC%T^xU7szAwWh;;FJJH<Qm#sXyuaU>>%T^xUH%&j-`?8fs=dbApdtbJ4`}i^YvX$HCAG0r8x!pf8`?8hW{U5V0+qw1r#_Y>hZjYasec8(G@oDeNPKST>`J8R4?;qHg?L4|KpURM^`oCmI&+7&Sb$cr}`*Ns6jr-KUd+#4TPj~iaJRVhfB&m+RFP^^Wey`kjtcISaTZ)xZ=d=5$Ugs|a^t`t6@VFOs`!}noJiKLrzF#-@1y*kE3*5E?^>OU`X!4l*Xe*E2r;x|oM_YOHK8QT#KHAEo_gUuq+V{~`9=(q<ugkuVCXcy~Hs9C2kG6AjA8L+c-$z?{^gh>|r+pu7<<a|SbN=>yw3XY(kGYSwbL;$L?xU^T?zfoxXe*EDfBQb#%I)_z=04iW?eP<HA8qCK_>8%ao-?qbdc8jt(LWa+U09EoV6c+POSRF@^EWoG?Ue^FOlhLNUipp6!`H9q`Pd|)=ev~$7oS$`owk|O^L5|a&3ZoaoGm8jIa^?9lFqH?(k8c`OWV15?q_oQxwM^|=ZYq`pG(_$^yi7@IM#D%J2%foO>RGzj>&oM8tn(`xwM^|aU0F8=hAj=_PglovYt!Zxw#&W9>;nvZRhs!?dQ^VZlAyXTskJV`p14QZRd9X+s~!#+<t%U=hAj=k01NFw4K}I)7%$CuS@?fqJMtn&!Deo);^)%=j(e^9$eKxUEc-|rquMxBR?<FKlfR4Pjz9q+KIC2b(Z>Dx3}`(;_p=ZP^YRY_my9wpHK61D?2wow{nuUtM$z3HA>y*1oPaZ_lMS#^w0AL{HorM$dY{3z4CDTVfwo6nHwq()t;uu!^Fk<I?&34&9|!dq3gNT`x&{Ktk0j%hs5N3KEyrrxBfio&GmXcZ+%&h_wzsMpId%+uU@Y+uCC&hhvxaz=ePnT2kGm+|61Iu+83CoKYwK9q1P6w_Ri3GDv$hrRe#QP$1&ADCcpNsK7OII`g5Imw`EnwPy9u_j?j`z`tzhuwNTGF0+&<Dd*yECIK6)rn5eI3^G__G@?7Qg^B6047WGi=oxlc_yOZLJs(fc_eP3wj*T?AZcj__ybE*uZ)O-lt*HM2i_1bXtI(*+Rj#KBkC{)rbcN@)6??)(5SncP&BERQQdHX#2y57p2hNt!Cdz&Zg>-syB^>eiurS<*2l?OUTbo>2nRUYXue3yD&a;clXeqYpFjf=<&8?VdxyZ7cw^vVN^KGUCDZZlTr?>G5b-A|vJrLMc350<Iix1g!ouLJu|=<5PI&yZ37{Q9?DIv>|2r}}<@Gpc<|&ga7e|7BP6ELgnFE%p4MV43V*xqCjJ{yb;%qAHJ^_*UKT2Y;J&W3NZ<mV8UESKE5&<8&_mw|d@VKKFiPjLvT+sOySg(O&BF{C4h6xvY*8nl)eLzK+G!xDD2*tUv#6<?bgJ_4ggVMW0X3Q|kGF`Mm=>4>W48*U7%Qny9?sm*1p4&rrcUI`4Ass=6-vWJSDJ9;iNC_s_$XRqh)-L%lEN_ap2)FnWM$@4PlpALnrYOMBCNU$>F|d7ZEIW_8`B^5k^CZBnOn@xcjx$C1kBBszV1r1@173FVKW_ph4tulfJ=t0r};*Zsf#s>z4)Qd4U&CH@2)g$pa;Pv8}(O6nzRmcoU_@sfC9N<0_52N&kWbK%)3@hmVmF3f{x!Lw1~IblIuSPajJ7ox;{@IG8v5%=NcDe=~DBraTnx5gJy;vc|$xbP?Z1N<^2o;yx6Z=7~v9XvN)n-cE|yW_$j-WBgbiBE+u;=;G^srV*J{4_j;3%|lo<L4>y@8Gw%@F)B`{0b%hEBpl){)zvJ-=@SfWYGK@7djcVONnQr#B;z*xG)YEX2<iuoG?2s%!ud2vryvy#A*H&r(O6P{tx~;C4LS5j0?ZVui-yX;t}{YF8l(I;AbiEci`K&@Fn~md>SP_1@^>+-S8=R7fQSqydM|l!E52UDDfX0%^w}@!VmEuaF-H)6)wgXv+le~i6>Ly<zNN80_#pWO1uOmUH}%x3$yMNpu`g>@yswgo}G0kGbJ8JiD!b@@NBF*nJDoblz1X6gcoAnNu<Q@rNqm^@_2dHowAg8D@uGJT!b%T-C0P9@1?{q!OQq%)}%{(EuNDSuL*18!mfBtyfY;}8TP=1Q}N08%ar(LxCs}Y#y8_<DDeyMJTCkWzkpw&#IM3DxbRo}Dt?m^zXNaMLRok2@U?hmN<0B(!?UrzB&1n)5-9P!FejcD&rONP!z_3f)}eU57XObDzXgBCh1c*~_zg<@NB9FSjNm`w-%#RT!n3&W9sEmtD<wVyPQ!&$@EQ0Elz1oD1sB%BJK;4b@dTI)7s^_bz}Mp6Q{sD|i@U5fdnoZSl=$N?8Bb=dd7Kh2Lx~rKCGZlgHAN}${FHb+Ou!RZYvL*KjFh+o<M24v8uLe-ZBThum;=wjT9cI$&qs+Df%oF~vep!##7k4+EnzFX6>CjPN_;dWz8mhv_p;XPro_La#B;=H${HjttcmBqt5f1n!p^vGGX5m~JS9FIzKjbu<J0jil=wM#1{Yqy&*2v-@yqZMF1(6g#;;T2f54l#@DBb5{x2n-mGwy0pscJ#33ygK7tD)iOl=>RS`{hr^6)=LdwIMp{0Em3FAe|3rNr-pw{a<PAH0Q2iQfxv;!@(p;BUB;coFyuE+t+FUdN@x3&N|olz1Y%f=h|#gFoX^;`!k<TuQtEyn#!J-vfWerNj%v-*GANqVNw~O1wDy6PFS%0sq3K#7n|ExRiJ)_%ALcUIxlSQic*Qms%BI2I$}!@Gl)*;%A{8>ntVy1-yfQfuDkZ;ivEu@K5{%{u%rO{|r9{f5(sEN8qpc5&RImfgi#@f!FX)@B{E?`~bcmUcvX{AHl2mNBGC^I{q<!5dMN6#6N|<;h*A%;Z6K7eiYuqkK)JSZTvX?Is6;{96t&F!B66+;eYsP{0x+};|yPmpMx23De<pT`L&~&nXe_!Oo{tpMcj|Kp~PFm@_1{!6)cOl!dt@9cuTwmybo`IKLUODBY1OoFWww)3X9=Q@dsfM{6YKySO|XrZww3Kjq!#s5pRgshxzdOcwLwuuZ!1%1@L-!19%VK0B-~f<BjkDEQ$y4Ca^f(1b+yYz#qb!!IF40{9#xMe;9uhmcbvzAA{xa$MDDF?yhBzQ{u^~^#rU0E8vyzOfUnU2|w>>%G!6H65mFNZ-r;^t@u0e3;Z4YZFmZQ8-EL)z~90*z|Zgv_#5yT{sz7d9>Le)Yv3V#4ZaF~g0I3?zytUSJPh~aVSFk42w#f74nM|U$Ctr__%eJs{1jh~uY`y3mH29S6km<6g~#!=_<Hy`z8-%Qp2Xk8H^S5SMtl=IgKxq&!*lp%d<*;v--5sE++8c*rNp<V)(#kfU*i!xYn-O6r&%fSD$tKt!P~($csu-AN_--0jZefUz*hJKd^~K4kH^Qt7Wi0vG<*afjgN%Q@sap&*c2a*4}}lnL-E1z0emn%5H`jK;{9Pmyg%L-*2nweDX=b{g7<>;@LqUt*Z}X1_koS@K6pPE!296?U=w@*J_tU955kAQX7~_%7<?EXhL3=c;v?`;@G*Q8J_bIHkHN>mWPBX{RNURQ_$f;K>C}1#wuMjNZSl&m5?&e40yE)R@C%Nntk)MP@%P|1{5^awB|aN&#b@I);XC+Dd^&s^pN_u_-@;$Ur@{^RRD2421D}Gw0N3F!;LpJ|_;Yv&uEIn3GjIj|4E{6><4@xg;8J`7J`TQ)kHg2pW%yWpJY0^C$De{L@u%>Ka5X*=e-^IApT#G^_4p+GdH5#&JU$t2#3$n~!cF*#_)Bmz{t`Y7Zo#MFGvK@U415;cj?cp9ICt0jIh6Rk)OrQ(ggfw^_%|?ue}iX>)0F)n8zo*9R>7;{9bh}W13n2pi%-HgP~vaEiTE4%IyeDehp&O-@iq7=I2K=puYjZR6?hnq#KZVfI2>P!zXpfmui=Z~V0<yY5Dvr_;tODZd;vZm_QmJpb72ZT7oQD#;j{6Xus1#vp9TBiv+y~vA3g`42M6Hu@K@j<{1yCFI0SzcUj&EYi|{3I1il1+9gf0Z$Ctq|_%eJs9EUH*SHh?8mH2A-G`<>N8+UgvSxbqpPpvm$2tI>{@b<7R-X2eamGLAz9%jMg@r#b8>^B!F@%Q0-`1|;LI2WIf52M6~z}ff^d=Q+855fn)>G%M=AAA|_hxdU~@jiHOI0f&G_k=ItJ@FuX4iDnpU<mJqcY)8~UGPruX}lBO5l+B6;_cx$ygl9)j>X&JZQyvk4c-nug}1{yz=?PV{7LvM{v_TRPQp9mUE%Y1SG+r%jCaR-z!&izcrW-8-V0BG)9@6$FPwq*#rwlqcz=8#oP!U<2g7;zV0@@^cdr^si4RY$5pV%~1z&*gf;;hD__y#I{98PGoTlt&*(vdAuqs{+?+82K9r5SjB>XviBiw**#7|P<C*T|S3H&p-4*v{42G`)n@FQ>)egr=RSKx>6Phc4T1U~?m;s@~k@HKotz7H<O_u(JFh4=^fUbq0?i|>Z>@!j}NI2YfE?|`%M9r$)Q6W@-%3uoc);@jXHd>j5AoQJ=MzYkx*-^X{sSMgo=9=HhKgS&7E?&2T9*YOYWkKi)=Bm85y9RC<U2v_0<@lWAu{8RieT#FyZkHYo%QT%w^-M#QQCH{Gw9^1l=@Xffp<6rza7>c_)U&K4Y_HlRTmv}Xp6nA$%if4!Mad+phxXf?i#WeH%BI|+h{WR;t`>Y?r`DxaZ`K&j>VfYCAvDEUzN8vDBI0W~@hv5)hI0*N{W^fQL9Dw`bLvR2t?1%ed6W9+I_QCxy0Q=y=-nbt&g1vEJPuve1z@E4;i2GqZ7{rC$a6haAyWzqvxF6PrU2tJ1+z)HQPPnim?uXT3M_kw*_rt2NJuYmE`(YK>78ka`{jf4@gA3c?ewYN?;ld8MA6A1MaN(1<AJ%|R;=<0jAJ&4MabZ{75ATOvabb7d59`A2xUdKAhxK6(T-Xcu!-lXIE=<AwurW-*g?({9d;s>vh5d0qd=U1>g#&RvYzhbB!oj#7Hiv_8;ZWQUAAv)0;c(m!TfpJCxxQ%uAH&UBBc9wME<<9*|JVPv{_Y=HL!EU06MOq#rvC_X+J8AD^;pplBqz7XET2<zGNk?|C-|<+Oy_?9oh}H`'

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
