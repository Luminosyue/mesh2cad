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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2ef369ebae66464f9d2479057a6bf6d2/part_003.stl', 'relative_path': '2ef369ebae66464f9d2479057a6bf6d2/part_003.stl', 'source_sha256': 'eef59a53660a3dc041b9b9a6babaed3e429d33dc2d63a7c6f73c3ab0bd989b57', 'input_faces': 472, 'input_vertices': 323, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.1386723518371582, 0.05727069824934006, -0.04341357946395874], [0.1651313453912735, 0.13102422654628754, 0.04140659049153328]]}
GEOMETRY_BASE85 = 'c$}r12UJwox5h8l*n5q}v17pkD2Roz_kuNQ)UklQfg<+7O6*v$qN8B%qJkiDqoT$x#-8Yn#;$)8yXJ5F&)MIH&VB2>wcdKqwf6dcd>;2bci(-^oI5N#w9c5RpoTxCwa^Ub^PKul(^TZt3TmN&!D9yZ4-Ba`V$^syEwA|MPr5E?*QITT?rvJBHnHM>z>xmI75yv~>jn8%tZJzkG%|QhaNiMqMg|WERDQF*!$Ja`e#oG{qXL~jyL)+hRke6ks%n{R`9J>2uI7+Q|H<De#{CdospF5Z$Q1SS<umZ(=810|GH;>sZDX&BZ(FqvzQ5Z%@h{%T_&V|8+g2Jgm2dg<3Vya@;_D@%r^xufwWHz(rHXIVjT$B6t=Yu4UG>F$PG(-Be0$ftM_u#l-J)75)$$gCU%d<RoSuvM-?1Rig<+Uy#_O1Wcoq16*x_GqBlEZa>W4hjS0GPO|5?h{qWs0zXUt2H>(x(Nu6+GwbBym4i}^g9I#u%cw8HpS4`jS0XjPQl*Nx5?zh@Kj4}CIPeD49K>*}Ry)KO~h7l=F;_Z*QrgcaK$<HCkv{#iVb=Ypq0e)b%V@vnEwb?u4ISIGRIjfJ1~Dp@po!)h5{d>s5Lc_qIQdR6k<=iA|*nJsx7XLqcZzfTH>Utu=#jJdf+{$85{|LhR)Z7&AJ$bBa+fM2pG#^<;fE%hrB34i)y+}HAjxNgE~_z9a1%X9g2-&&KO@0j?G&Nq?&Qw;p@W|GI&KEUJ~zciKlSbh$Y`sfF@V0_0~$iLgVPR2Fd0sli$@h#q^W92%t_QUr|NfKSZMaJ9i9fY5AmE4!%_dEvkOMt&^gv`gfqWcO_>mm5r<E5U4?-Qw~7M%qD^uQ$4tF>I$;+_J(XA|+QoqxwXhn<8Ub`AC1F?p5bd4C$d-&2{t(Y=4H$qy_n*R>^Ik~&+bpNAhhCQ*Jq`9$(N_FjO0^#}1CAsr--Eq5Ax|1r33<(1Mu_V8Qqcl+SFFL%j!WB0G{zgvAs@+U1@XY#k@mOR!$GuN2>tfTQ9$1ah2YIP0xBU?xw$Al87&#uStb0sH8o*H-8ntb+;9@Gf^mg5=xy%UnKPHrPl)C>6AYf2tR&rNb&`|&^F*E))RF7A!-Q{KQITo3unUzGgTY#-2XOJ>K*&uzPi?<l1mlW{GBq@KppyRjxe;~Df-5#P10zAZKY`)8&0Sl5#>h;Q6VJt*_Ic0`_|<whptX`2)Ctg{XEuay<!)4Ixd>vlhRUY4J-WBebTaouhM<+`?O`QV>zb;y(_a{=T@?R`Mz*KC^ft<}3A#<!X!&rAQlvh=y5Um=XYTT{mC$*WDip7j#;lRM|o|B;2^?+8Hu%>9TumnaUu@I0xTUVj4i0ngI#msL)1eJ<98Wm%uh`{if9*Xvw;ee7T8w~tL^y*QG~Vf?jHGTt_H?lPIrv+@{Uq88T6wmsOFidTf+VKMsWOr?$T?_0RTuX*?ov^?sW!2|x=#aJ(yx=H=@qTaY}<nev-vwPPyCci@EIMMP27MuKz2jn^0er+D(>g%=dqyIOJmVPs0eBc*fjCIs6SjJn^eBmco$9x(!mg`!o*M-l0z|p`<?n^7u5ZApu7xTQnW`Sr(WBAn%NuTRm-^qPhH#9+>il?!!Hq_An7n@>y`R39O#&tKTr}nuS{7>um%D-z+U;4zJ&>DGK+{3=wHaGh4K^yoF;*YrYm9<bi_;&-O{+6^i=%3&Y$bTaP=6~j7gsZPl?1lCFdA`ik?g(JtMq<58e6UjH*`q7`@W*&AZ^mFfMs$P!=(jzhcdjj!@r`~!{zH$kZ@+vKZSwP##r)G!qz`SQdcl8L75yAH74tvW2l+jsq&~KsiPKE}H)BxGkRHojeck4PeW1dR$a5eN{`C~}e}`Mxx9<fZ&y*O{=ap}?tFJd0jr}3E+FFy(&o9T$+OmEfBZeT)MK7s?t!Ir$x!>ra@F(=b^R3)vvi$sEIQ&sVvF;`WN!=V>N5OxyPwMYTT7dn3=4f2E-za%r>HGE<zi|)T*MgHchcpO<pMMkfjr4sr-LF*!>pF8@=|kJ<FkJVwr_9r+S9`3~?fnG!H71E~jVdhtV04}g-*YPZ!L4AVtFOO)Vd^XE^eOOv>#$qYBW{k=Gxs#)$!(SAXh~?X!PVEd?ZSB=IG3zP>(CkSFI~nylYWjmH4AxG7e<|<s||7W_017DUoAQ&`So%?VtlVB+<%_Tll-0LVEj`%=Fff15k42=Qx4$y2CS8R(o%O3#&18gOZ>!2Gfn>0e<!&1m9cy=@7IvJIlhf|xcd5|kEZ9Szg~**XR_nDJj~NY>JzY>{*Zlmej&46eLZ9W_OUAYH=6tcS#V!v=gWOrcdaz-GmfJ@q~C0HqLKf37ToWHdw9MB*J6CV1=v6Loxt;rT8Hr$E@D4?dqmck<G8~-fB&sbQ`B>LwH|rqH<r5Tdhx0Lu73C|th<&MWS)BaSmfEYT<+KEpNw_7W0Prrv-Lb4F5`W+A<vzm(kDjP4eSF!+cExqQOu{xmcSGjU-v4N>{=iD(jEL<@J4-pzbN%Fj_yRBX<M;R){VzL*={fVdY90LOWI75Jd^ez&zgf+kB6^Ieq&o4{37pAhhABw4;@(#!hiK{r;H1U3X%M^<B{Js3hQxXq+C~Dd<f$sn@GQ<pL@Uf>F*Ksd~m*fk%T-qo3ak?$ECRXqqf73c{0W{KGOnOr#9~@vftX;96|mCQ%vs*maRJcCcj~w?wO8$^FGf0>?-$bl>B~{jE_74e^?pxC*LpZDJOB=#hdZ@axhO6`tlS%XVXxh`y*|xz7Z0M`n&ZSD%UM>n&*l+vfmmzt@xZ8e-{3-(>Pb~oRIG8UZ1gkdA`-JoTrcXp!D|wt#2Cq<E!y`$M*<5`4{AmnTh#qw)K$vDt-;)I~kb&Z(Ho5Ev{pHQ-|yiwk_`#NxpG6O!un~^lqu1m%i~P{JL*tUp0>Omh+P3ms`jad>-rZKpVVY)VK{lM-O~%_O2@Xp<})QUyHyzQ+z9_{I(}|k$>bCoZBCC$9qt^pGQYO@BD=KnxcOo&$(POf4$K)>1SPgV(MqT?fT)e?y5h9@3shaxDt-f9s0(_CFsM9F*eun#?TE|ceCr_{E+xB-q%Oe?dU4J=RSJD^WIIYFYfb}B7d3s(^_pE`mO0pehw~{{lo~LCHty%!)u<m=NxkFbGyfTo?~aAo>O<ry0Fgq2>(M8<{x-_jMTHxKgiR4Fy^y=<5ZJh^1bOjPH+5~pVvcBpF92g%k_h`<MQ+2>e%;Q=b2{m2OPxb+Lv>koA~<W23U9J+sb|ERWid*8Yb7Z6xuHRZ|RW*dAd%)dYP3Z>%|_C75*d*^@%-TSMzri$YJuooO9OZhW|Jj?}K`8d|sT(gX`WaA$@D@TR%eb{GAv6^AWh;-7l<CpYIF6k2?i_%Us##)BP{&z0g?fhqDU8Z`1?zxmS9&%40oH2!77r@LU`NLj7I+u}g8Du?OS)mcJ<cUq0YG#`A;yObPhz^U;UjHNksLR}1__nXq5kTP>2lomrZ7UW)#2UvZeLZwybx{8PO~`n&p{+^~*vCC-=Y#+8BJ=N$4k&Jtzvn>Uu{W$&J6y~=O=UKaktk9aP%_u+fL)$W*2-!Rm3X!CLYF1~SOG0tP!Y`o{buMFRJkoeY`8|A%2>*8_T)aQFU_LV%-tHD1t1J`Xc81EfM4fuZ_!F`4OE#GGv^}OJ3Jcau@AGu8V`pR0EXQ?b$FZ^CH-8Y(-#rec@5Z)8h{fU!hp4y}{8`OCFTOad07lwL^ma7B5W<9CfmwhbVZ_*3rbDsCKJ@qi3WgSts(J?_%@7wh;{#jY{TguC6=re!#gV#wO%br{EeW|vh5&WM|;<<l2<a>E8CmO@I#>0ObwMy>ybrbgU1oYvD2QhMA0nOp>c#ZMt=O}v%%ro$a)XnPAU)EQ;Z)_cbJ`Zdpb+heiY3euYv|yY+e{F?4)4g$S|EZSrp)s(XsSfF%7nWB6$YY$xd}>t=^LO=My+Hjh^$eEvIHe2x^zQ-I)n8}w$6bT}XS0QJU$?r!w@i`!M4NIxR_d0mJLXepzs%Ftb`;iKP*3;)(Kw%br^vpS?i*7d;2ibWSoHI;Uhtz2VV+@qM$5nZtG8*r=%ot}NpbOwqMn%Nfk*OvzI{?Z)BdBky!WGM)*$#R{**df686hFwf-~&{_QHb?$fH$Z(sa#JK=9{Ho)ZbdkN#gX8HYs<Hb<!!wy*&_VClPj<oNFb6>53{eM#n=}*VC(Wd^fy=XQAbsB^5;s3(@^7j;$$WZfqPX5|N#+R4?pWoY9{d^asxcdIy*f+9HmA<u%p9H_oT&(wEM`XYK;^#ev{Kt~yTx8!o*}Ts$yesR%n#qoN@*Jg~^Bgbt<r!{%j&t{PlKK>%jq$0Qur79Gig5J}$2#P%*>{5UL(2&G{NBS-x{T~s`o=l%OZduqwC~*_eW=x30KfElJooL3rJrqm7Q!$42j-Jyy!^gHpT7uxt89C)-aF1iKP|;PXD8ymE~E}|_0!Lj#?4mpUSMs$41VoY>@%P5<M%AF%aLd78k`ULd8EyY#`qQ$FwgiZQ%wHwrn0__T8lQyJRhw?o@+CZ=aC=I5A=<@m+(IO?w<6srO0}IZjR@Bgx^3Je{rMfzKlMXYm4^Wit)Ma*gw5TN<UlYY=fU|xzxwvzDxSq@^FVKzy7d&JE=qP9@DwPcC(E1xprY6{IG6v&e7WWZIb8mDGqre3gNv*i<ADe_Bd$jD<kp;c~5ji#A7_q$;Pox0aCa41o&|l^#AP7^JSim4x7f?YM+q4wNyTe{F$%fbM5ob=-YcISO<JRVEE;ce$(=wf<J2?uItxH`o|i526^~CrAHK>B=bCT7UOfQl6u-xr%E4ccP}63y281x=w;~>Tiz?k<Ff~OmX{eW+Tbed{|<GY9)SIA`fZH=lnr&BvPXVD=*WGS_3VOu>1?7rM}6gebAJB5(#ZJ&{_f8>2R`+X^NBwAFXZufi~f8zO7;_L*|(;;rN0;0qCRuKO++7F?jd!vymCtw|JgCDuY(VlD&O$QF1|jvIX>5pYU8Co$8uqOrxmDAId}QIc1+5j>RNxt?Pn_`f0nZFuce^Q1?Q|y>0tUTc#Ar-Lmh>k|HK*Dw1QetUzcBjD^vYR*Z=-k;Df#YSHA-H_VN7x{tCR3oAaKW@ox>G_%CV^vI@nIsJY216#u3n6ldb!S0*bhLst4x1D|o~Q)gUpMuK`C&X~<myqJ2DyqLU#dXBt;?4bTac96GFZ<4o=cTw+>caaZJACnJ|lNgF$IHQL19tu0dgPM!%K`u|tN-j?>Ma@7iMJ`7Dpn;2#3s7H>RVdC$eN0xNI1BYIS%qSadXua|@q2o|kl&MEQqPfJlAlvglAn|BQFZb?@-1ot`4;(#%d_9(jB(Vd)C6(@dqQznYH#Xna&K}Fbul@JJc7D{Jc2xy>L8CLPo{1mPbSZz?jp}3FQ6VEFCZ_aCXttt*D(|yqrM<3{XjlOK1)^oah5+TzD&(ZR-yPdH5XZh;y<W`$to28OG79w$-l2bE=l%whLu{MT7z7lT$k!Wu1of%mM8m?Yg0>+Ym;kIi;-)Rt5OS)tCA~HbCN5P%TlwD%aTh_HF61ZA*xyfh4{1LywsOu6^gS{pOaN6&PcsSR-yQBdbh}blV4M>kd;0q4{=6&XM{RqlQZ@?;~_)wTj~+=Tk=2DpUMA_v$;VpkyR+pPrXA{q4-<sGqMWB<*4t-Dil|7LnwB0YCdOFbH+E+3gmCdpET%qWEF~EQ45k)D1JcAK~|yo2GxyxgV(=ERr9&XP<(>=jC_KeNWDW&B=4qPBJU>0Qhz4Ll2=iWkXMoCQumSPlEbN+$l>HrmuJ7m8EMpCshh}~*b|B~yFv3%ACgrlE>3+*R-w2w^&hed#qLzqEA9-%)v5W()ycJ}-;!&Q>rl&)>yYbFtB~uF{TYfqscvL9_JAitu@AK%*@x^${f_KMZa}R-Za{8GtwwH0Zp2XRMa@U{A{TYT8As`#)O=(WitkguA*)b)ovPNrb%x>#)K}yS<m1!_<m2Q+)EneO<h|63<h|t0)Dz^*<ki$f@@n!z>TdEv@-%8Jc^Y{<brpF$c{p`0c{sTrHJsd!+=CiQR@$EI<&5v0;Y001_96RG`;-01{?wsle{wTw2)P-#Ep-yPEx99gI=Lgc8+AUp8`(x(PPUN;QrD9Ql1DNWZ)GSx%20fmx}1EN97ml`jw5fUPA6|C$51DcW5_G1A>@_hMbx3>MdTl;{mDO)?bJSGJ2{N{JvodV%uw8!>P1#so!pt+j#`!6j@;52KTsPvqb#)|wI#VF$15&KEkdnIE<!FwtxhgR{+8-R{+3*d>O(F?E=~0#mnK)B`jab=D^r`1E0e2H+mfr1J*geZo@8HYH?l9e0o6usKyFMONN!ASMIA|QMed+|J-d&ib|81)m~qst<Z)#69&m+vhPsuk^r-grJyPlK)T89z$=9fd$=Ar|sd41<<W%Z*aw<868beMY$5U65<H<Xzi^x048>v5%H<H&<?c}xOWz;b8GV(lXFnJz%CPVRHYG<<2cI3h20o0b{^mU@Rr!#6hV-U4Ic@TLtwJCWtc_Ot9c_KN2+JziJUPA3fUP6wh29l%6+o+?++sON=6Uh6?$<!I-Wb!G7;z)+#z6{0PsT0WE$pO?+<N$JWY9P5e*-Gt2wvy{myO8UUy{T=;-eeDIQ?duyom!vlPA)^OO)f(&$xvK_+LNrb6S)St616qC61ki+@>A9S?5Im^LM=xw$MK4XQO8hQlgE&!P&<*Qkmpc)lIM`4sDsE+<PFr(<PGE<)QRLB<b%`*@<H-X)FtGf$fv2%<kRG<)NSOeWP`e&Y>=N&lgUrWZ>XopZ^)muuV?)<s`AqKcc;ioBgtuG_1+Ll9YT#HEA6X&eeYD-g4&ndg4~eWo!pRIj~YO(N3KO}POe3+Nwtz|lB-bbkgJf(Q@zRM$rh>y*+MQsbtjh~7p0aV7bO>>mLwM<=VK@?POU*!T8UhoT$oypoW4#J=X6E^XXJK97H52;ef^`@jhapS@^zhX25NS4269Gf4su3vCTcEnCURzK9&%=KR%%{yht_Tx3TFJD{)^YwKXx@i(|`E-um95gwYclQ%;G!*efg5SL+i|{9?l!fAPe+&)g{`00L{Ug&H'

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
