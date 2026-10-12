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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7ce14aa504e4bbfa7122c444150999f/part_001.stl', 'relative_path': 'b7ce14aa504e4bbfa7122c444150999f/part_001.stl', 'source_sha256': 'd741dfe93a889fac2776aaecc9e34b242b74dea75a8c52f1410ec8d79116fab2', 'input_faces': 556, 'input_vertices': 468, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11297689378261566, -0.16131183505058289, -0.2736198902130127], [0.0771278515458107, 0.28948837518692017, 0.23951679468154907]]}
GEOMETRY_BASE85 = 'c$}r22b2|6wuXzOf*=wU21MEsXb@DCD8uMQXmV0AP3VShLer#fGBjLJKoN;5NNkjxp~>+!IU|VRJccLYC~s!O@WwYfhM761`a3oE?sJCq)_b`2`v3ZB?^9K~tLvWAb(ig16)0HR%lr43S9|o>=1Da?Pe)O&v^Od>W5mF|shLj=88$Yb_n^=9Kcn;8c52hUTRv};H$FZkHM4I<e1o|7hW+Zt*NBVnH#B2JM)Hu}Lo-rRHE)`no|&q6=78j3scO4w?Yi}A#MP=+BQ7iM|M;(nI)zBFFAp46n%$sWu2!$i=F=}YczD9v3z~<^4)J;9#;Rk{`I4J_Z`G*1eqP6=hokc)H~EqM752Kum)zusBE7do^U$SFA}(&mkz9`B4SwXHYaGMnIEI^XZhr8m&HnbpZF~H2n#AY2cqCzY3=d@`JM#@U`H_7s*ZJd2|8}2${3g|$Jjma3X06ZXH1f|gsYx?8PnaCbC$8Az%r~6;(9T<HT;p3@=8N$yPJU8O+8WpON*-MA(jQki`y;r?4=*0K!gc-@=X?S#&fntZdKWIrcJ@bdnJ@bzIr(w#l*@KqujJ->vwx^G-<2=9$q#*3X`b`^B{%19xIBN!&H3L+nd2JY;xb>1Z*g-!Up_s{c|Qmq+&|yHJJqjmJU;LF@cg4WE*`h&r${sp_x|jtD?i}#j_ruy<6GUGf04G!|GB_J95=%Fl7~1S!;?6!%nvxn4LHaBw_Kc0ctOsQyYcXEO6-Z|kvA*cozLFAH=29vr{>;`M?UMhKbps#xD&Z6uUGJ3Oy6#Gx;uYk{h=8C^Z3Je<Dp?yWBMPd-TKg7xw(HfR?F*~_`HxjxIf|Y^Fs3A`L?F;t9m>8+Bm<@p=N*G7R}?XmUZ&*q;K=aPsoZHC!96V=UzgGyyx($7O(in`(#?)=WO$m+g&`;Vp$ANy75)sectB192bwYdtyg4_pW#Lx!0-tP8W}K{vw8Fe|*TlE-x|vZWj;roDsvrSD!uNI)B5h^S@dpk0-C+<Km%|x_hH}=*p5@*Yz51UGJ4SJ`W9OxzEYdF30ejmkQ>(`eV54Pvp`M{(T-A`uF`V?hT)IAf^u&(<82a8ZP@8x|o!gKXTSV7Y~mvcPNH0T6fshPs3$Dy+w1GH#R-&;@-pyF+BYC*h8*<23+*hdpp_ZUZX(~7ms^!OAL?9o$G&2#WntilV>+ci2Z$;)8?SF|8Uv=(98-4oc)Ab{hWShpQ}HH%l<^B9Ng==Uc=?}h9~`TkL!93H`g1A|1irRM?4=SH@{zo%jbjS=J&;L`FxPv-2aBl=Y!<tel}b_A0)TVUpyZqH}|vQ^7$aSb-m*GU~%qe!{zfqa@imGe30DSpFtnQ^FeaiPx*Y1+}zIr7taUDWk2QfL2`5d2j?lC4;B~wl+Opr&F@RlH}QOs-1>bH&j-n6|K;;Ra;u->`5?LMk9<BzF0WTUA0#)|>&2Ct;BSlhiQ#g7Vz`{21YFEdLRFp|?(<FKF6-@ZuW^_B^PaY6n6Hy2_&iiD%je<SjeQ>aaav4%ctPR3{P?Lc`QEhDq5l4lyZYRlL4J!{L;U=<U1G=I7Ruu{vSP<MGIy}Q|GNpX$Ia+6*m>MP)Jk`qr}zA+G+*boi9Mg?(|jH(-8OcdNbW#?|G@#V`9IYg;OBQtkIk>Qxu3uPT6#>r;i2Rq&iv48Bb?l;I41VEqbsF4kDIfouj@R$4?pVTysnyW^>OvV%Px}a>|63<Nj_g9`aGpuZ`aSoYci~t^XK^TcRgG`ckjZTMAv=dt?%63dEB(Y-JIw7<)SXG`_>zBs*~$J_a=VU$KU?u)+PVAzf5uR@D}pDwW<ENH*Ut}3m)WO>C@leE^|9JUvQZpdiWb>zTrWB=lC=~ui)pg`GU**@Jn}``G%YP$j_ap`rGF30HZ7C{T)*9(AcGUe<v*1WxCJ#yF_SAV>ch070da%gq3eN`Qeh+X1K<;xXc&hTbz8a+_jmm>y_MGZ@6N;Sz4|2Bivd)!mahA;o|x1Jzi$E-)}KLl-$g(443mm$<2Jpa5+De+{}Lrm-9o(&3wjiIX{%#I)5=gl-$f`443mm$*t=Z^Fxa>pD|p{4<(oVk@G{z&HN<jgP0#mF8e9xhmxE5Ou)tbP;%K%IX{%#%zuLO6!Sxii+;-aq2y-16!cBZ4<!%gONNX2q2#jva(*be)lV@$lw9^l&JQJ**DL3Tk_YqQMH}Y&<H+@+;KBL}Zmk~$57tv~YyBvAus(uY>qo(Z^$y%xKMHQ0zg#~G9;|oZ*7{L!>w4w-QF621fm`cG!DWA}^`qdy`o;7?t{(-L{j}DPf(Ppz!{z!>aM@35{U~^_J~HPi*N>8mep>5C!Grab>6=_X3U2+r$n~S(vj5ilQE;oDa{VZ{?2om66kJ}fwSE*lcpfe(KhOWYlj}#gwSI(K>qo=I{3P7^q|fF1Aj!@9Aj9SRAdB;!CE((Hki~h=5`oM2L6QgW7tDEz_dymn@1YDA?}IEZ&PTovlH9!aF<ib6vN-R3443bNBscGU443bNEY5qMpl{-Rki~iL6L9f9NOJSuC%7*0KFH$c{)r?m_LX_~&4f2|T|C^Z&=D7pYyI3&7Z0`F=H?y#a?Hge9S0qE<|lrA!kOQr|4HY0_APwc#l6(YP993TcE&kQdb_jEafZ)6=Nu=q(0S*1vfi=s&HC<G;u4>;&WdZgDc8kA%|3VXaO*BdoxIIlH}6pDxQj<RwsP`tV)2ts-lLh5NBUMf?c^!RPVNo*{*05SKXcZ}Gd7)b_9x@Eo168o<Yv8WIO|rc|7JZa`wzGJZ@BEg;j;g5tN$in_TO;Xe>0Bkzu~g~aI61@%l;cK`)~Rq`!E0gAi4Sbz`5$nT=&1^rvH+g{#%^>Tb%w&Zu)QK(|?Q8e`_52Z*lrBx#_>f>A%J4zttc5Z*lr>aoK-y|4VN5U)=u|m;D#_zvNc`#r<z_*?)2WTU_>E-2WDr{TKJY)gRe^asOM~^#5Y{<vtgmzml8JU&+nqujJ<Q*W!HsN^U-Xt$aRzt$aRzt@GsbS90_DYmLw6uQd*zzt%W>{#xVk`D>l0`Fo?x=kqsvdrG!e`F&2w&G#@RH{ZiFTz;QZaygFtK4+xz>P@cWN^bJwHtpEzU)QPAG2eHUJUGv7p&aLR2_EFHK9u);F7bU`$^HEHG2c#JcY4Y<bIN(1j>2APuU~T1SCci=|BSl7nmn-f|LUvBb?Vgp|9&<3m^z1(Dvqnr{sh}vk3{*SY-^1~`CPUSsnGq{gYLzjV&7@}VYV--xB$PvzSGoQq;@a+^!9EQ2UYCCA7ESS{wTkXZLK?^{7$xa;CG?B@gJ!8P{k$uWwy1Ri}L5$)_Nw&pJn?jV;KJd+Xpz-K6EGkGCAkbv-poy{7%Jxpx5y?R9sc@d;B%FKceOe{&#F&CFctI5&l0_e8M=NFxKxm#&z~zXP?QvPTqCKH^;xhxHsV17xnbb?|B8$d+<fkVrU`!#eC}8Rh&mpMR~pN40-{7PQ^*KPr|e>pvJmaMLx6;ULVV2+k+Xe_vJ_L!GFl{E}`e~nqP)p=9t=lz&Tw;FW`%Eefs>gp5<KcSN=ZwaUVU>{xthfpeOM<N7tO7_H@2~c~e)E<7i)q>o0~D!572p^U!*V9ye0{w<=yl8{-?Z-GtCSfzZAwp?xz#`{so9EeP#fqOI_)*lvxs!M9V<7S<N7y?Ru79aMBhyWlnN4%3>5?}_$66Y;&-?iH2S3!VhinvCy@_Cb^JomF&F5%Tg>e>P~}m2=ZQ>_UIF@6Ne4;aVEg*B+dk?xofQ`r3<g)4kN%jJ_suuDXX>ThPxwoSW{U)>ia0g=^5g)Y^u=rgA+gQP-J5nEh?}d8Bg9tr?>=KbOArswKxXKi6b>+MIK2&VA6EpFvZusVVnOPkwey=s^?ivqXNzFVZt}Uv{JaA$qK}5x%2}=lPjveId&0eGSo<@vZfB>b{`u@Gqh5(RTRXsG0^U>Y>l!>!S71=kV{VnxiUSK{N4F&<r#aKLvdcJ%WD^|2}#YKaafmXeM6gY$s1^4nBjLBk1<1@p7ooVGQkmrLLiZiiglr_|j-ev=qKHS{8i-Ul#u>v;zKN^2(s4@H(d)d0NZkOH%U)S}tn5^3<1S4DBncsOIVES)NwJ$Dxm+74dOsCA2EO623B84gYKM9!D$UbxsxXw8rBfrKT!cC2G8Q>f;$h`)5?tQSl^N9bW@|0<Dg(f!0K8<7?udLF?e3BJXLmI$q~IOP<zR_$R2TjXoPSUM=ctF^2XptLUJjJ^B*9xQYkZegJ0tgKR%Yz40a3F2PvF7iYUTV`!hCe^>Rh1Z{vXtKtEDU!%qGIwyhc1Xyuu8c^4O8togasHdMvXkGlnDvGEmgWiv?N6r0c8T^aXK8zN@H&RhcKikk}@ugMVqv9d-UVJTT?nNKMho~)$-h+QZ#nURDN1wu%RFPjrDYO9oX=)0frSQ*FTN2HWe@;bp74^|4@I_VpUHyEDq5r^Fr$%pUErzd8ZBbO$XkSM~yo%ar75sfFepESy(Vy_~)aY%kh4Hniy${tj+CQV>aTPVuU*ij^_^Zk(gno~IoEp8YwGh50wFOaKqy3XA9#c^Rjl=5+>UUbu|G_^-jo#Lp4_|{?57jl=S5r|@MOE}s{LgClf2;Tf{R_S#HF{g?FYK#It*+CmYqYPdd<7Mi&`0n;sD0n4_#65yUgzkVZ>jwo`zleZ>$K_`?cY=}RmDv7ReX|)t}2qzZuqIxbVHNzGpS8NyW;1nn66?DIt`zqqPvPzG!Z|YnnW}eKZn{Bv^)N76|bv!3w;egKt&G~1JR!N*Qx1=4#dAj?Etg~{#_Mss91>3z^AL|rD8DJ8~+A1z0tw=h18~_z3@v_%vP}korNE!qK}H<XkYwnYWkwX@k^*3hW5d)P%&RcHaZVKLPb9nBhmi&`PB4BN8+=o9f9`4uTil;#cK2&{5Tb9D#oLO@C&FJgpS9rrgj{fhF_;*v5K|mBK!muLsVp;L-C8L8H#4%*HSwH9fIGWV!4X-=ra676&Wffp_%yQ)MTQQ@aw6ah-Tn7sd!(-M)W;=Sj8w6lhM)m_o*3;PR4JfHjIwK-%;_Uim%bH@GbJ??Q4a8jc=)<dA>ZawFUkw>h*rD&B<*UwO{Mk9HRyGcgX#cb7`jhZ&fr!8{*5Ucu+-ov;<z~G-JCNtOPX;scT4$_FL33R;k#GuEbAKF-FBJ=vchY*~0b~*jQ>-Qn!*C?K`RHsG<wn8NZEvIcOLBb`@LkTgl6zt|R+9vTr+K_UAB8XX>^x_Eu`NU#zZqzl!nbApAHq4IP9Zhb}_*;TPc-qx<nQ$a@1Fgx5Li$<w+4pGM6-bbZu#8>rvF7}~$9Vy}v^=s^4!bO1UKKL%Zh?!hm_zl-k0zee8c=s>*ASxcVQb@&0)>_OK?jkk{ab&R3?0u{Sej7Iz8N1^@D{`gVoJLoR_JNO0YZu~UzrlbAwI%hR`TG!zFQL_tO9W~w>>en!a_DfY9RFQ=a#!o=g(ZTo$=o0h*ehGdldJsR8yf@Loc%8G6JguAX>C_xRH%5)OiTX{9q5X0dhgD2MhvFxqL(rl4iRd!)5PlhcIeHjBi@e$BP`u9BOrF*)_#xCBLN`Z^w}tvGjG_Gs6}c)Vqr>rGbQn4uA4ap$2tFIX0?ozGA#W}^9Itb>lBabWei$_obZgXj+o<2h7}~E=aa_ezbR_;&bObsQ|0=o?J%(S2UxgmWzeV2L=t#WI*+HJxo%j*d97A_RjklBfos6OVZS@TOvx?8qPw}_Vo9L(bTj&?)pYUJcZ=-+4|AD;E(NFO@=fB9)`bT{GR{8RmF7WUES3Cdur|$zV=6}2+D`Q`SMOQ9UV+Ak8+P5mC|K{%HSO4kB;z0eEK<}UMWlBN'

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
