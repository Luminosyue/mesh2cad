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

PART_NAME = 'part_017'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/63695230beb44ae68650bdd4d914917f/part_017.stl', 'relative_path': '63695230beb44ae68650bdd4d914917f/part_017.stl', 'source_sha256': '92c1371118a764af1482b65fd42b2770c2f732d1963b113ec837bc4bfd75ae92', 'input_faces': 442, 'input_vertices': 282, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2748660445213318, 0.1844649314880371, -0.23527784645557404], [-0.010877303779125214, 0.44023650884628296, 0.00944218784570694]]}
GEOMETRY_BASE85 = 'c$}r12UJyem&Gq2ps0wVqI^-GC7@VQLhM`(5E}|fh$WVXVk5?e8jU4SWAD*eh>B0e7Kt@hEEh#ZF=$jIw)pH{j14RHx&N~_1J0URYt{^Fowa{&dpP&s?|qjfvaL&@(i(m$YgJb6E&tG0(^M4GN^2u}4;|LOSMT^b0|$?C(!9i1KY2R8eRM=*XD4lhHrhY7cYLp*{*5jEP5U(TuVwM?Gid0rp)mt{3>q5STlwKJ1LAv|etf@}!M)AT)$2E`U(3><MlH)&%m4Am!)$`lchMgQR9j{)JsM()-e%x7`J7V>eygg-m2ZFdY^(b0*y<|2ZFG$In(Yws7i!3NY=XbKzW93R{Zo>E;leTHTm9GkraoK7T!mk+%dvvjwQtIX-@38XF;)~pomW}#TWv%A%zjeGapnO0i!LX`U-VeosrOz7f9tsn<vX4ZK>I&g1AlN&<fm>%`yb7Rzc5F9+vwq_vuhgsuPcae_gEp<wH+S|fBo>^m2U}4kbLdrckthY%5`mb&WdlHIRgG1Psz9Tc)msIS04<2#8L6Jp%bM&w!}F2(Zw^xKeS)!80me)*S=~k`Sz@~Xpc`@_y;p3-&j>j^6j(2;CDHQ`m;tOe_JT(Kk!6<BQI^2_7rZ0{1=T+O8y^j(629=AV0M^>iZ3o_S-Y-!+-Zg>R5KTVcc2=piYvzjDyj&C&oF&ANkqsk$=7~`V~R{qj<Tly=pk>yZOC0kJ`5e+LKlp{*^A$9(~+)>6h+T64xE#dP>H5P^i?=TuZ>OJxc0ZpSeoDw%8N?XIEr=Y$vD6I9PmKQ2$_e<Ud-yS=#wjL;m00rM~gN3;kX2=%nQD?<v04st&H3k|Vz1+gyA-*IUNH5_DR8ZFwxNYri4+j@-?tle<l>Yx%mdw8s{=5&rLKG7eUc!q_hn>&4fb>_+{Nn$k{7>E-ZSOcLK#rabnM-+Wy6WC+^1soN&>YXb6f%KstzWzs#VW9vEy*Bx94>mg$f#vvpQ{aWWF`FhJ@8>Ky29Z<h=E3DfAWwFj9KSloAbh)m@<wLaRdmZ`xx}wguQNPOd!h+$~PnPj<47YD7=o|YkV*D%2NS6JTTm|hcv;h9?5Sd?Nu@CB`G(*2`yu&z;E`|PPr--j@IW2YUN4-#I)nV~%2mh3Q**++OI`^l@x-~3Yu)p-2O!@aU8<5{TNybONb5(q8R|M8ikT2$ClOev5wFL9B)v-Z7$E}9n@}AVO_UMi}&MV<Bx+%VK{q`?%-GoH(^-bO2XH*p5c3>Iu(`#Zq%nz6GbWEBLzf*h3x5S3Y_&e@?kM@7t9^<^=492HgJp3hJotFA{??^js%j3|mhSQ~A`Yl7oM}N{2elLsU>z#(Ill;i$Xy^SWXs2;;jf_K15ZZIZPx9?im88F#r4H&CGf-#R$hFen)8*igNJ4u&56gVnoJzr8uo3;OwM)jqTCXVTmoF^&j@SlRhx?xWF8LlMWPRFJKEk|Qe=5FlaTnToByqKj!^ii<w{>fab@Jfsnu5OmJmiejY1~fQX>_}X`r~}gp#4{*j-}dl)IU;JeC>R*^-^bZCi0Igmv(At-B(HbqYlIW(2eJCqKvb4=pfot_dND5$Jy{qMSI$x!}!Flmw7kFt%bjTtX$XF=PdQ@ml9Cl(}8~Z=;AvP7NC9|CyZyE9y0Hiv2)?yoR9X`zlM347>|CPayl#dbH~}G{pY{tIHw{1<=I5>OZGr}Rz^y`5mRxcT-VVa{uIoYcD;waps#&BUwoVElVy^(HWdEBx!6Y^7}6d`xt3^Wldo{y<Lj5m=U5%}%h$s`T|PqktG#ZDI`2}XJvKMgx8L$besJ|Hsnce|BB>MahW_$=&=&n9`Hn`fPhj0%!g@&YTPVLj;e_~lr#+|>7&k}8b6tk`#+Zb&7|#!X6hHGg>exGB94dVDlZ;#Y*{Cz6C)#=4HchTuVcZGKSNn64zv9(6snf*|evfvjKO<nI{Qk|C8KSi!Fg~G|he`gdv+xVGMmry-wU_I>4uD@d40XQw@(0l_=MQ6l;~cjBg>|pH^%Gx9-GFguJL9<Yb8d2){Clx&SSQZ&(j{+gwD{UFf4Qz>db;?IuY-_(ucP?Z2gSv=KFv8K`7ytVZ~1h|5y{KiFTTFFu#AJHVHW&CyTrHobQ51M`$+0ql7B@0<6+3Jl_c#p{HCG)%M9G7zFUrd-5Uqrw@|jM+xWKl{RN#+|J7}&<M1gWb@bPv@CPgt-(Jk)sML=rA-<6?Rq9w~)s*%)ys{69UpgK2-Iiips%D6<d%qB0E3!g9+xL$_es)Wo=WegCK3WbG-`45wpW;srmd}=`Aoy?lh;PilWJsM(KB!ZvviSC4^~ASL@e*H~Ru=c8YChOkJr}2npX+^I=C?%015)R4L-F-8doXS>9gtrhzBbMEg0w#+dcXKd#gN}URqE*JulC9~?Ab2YH-<NYUpIV@<VSo1zeO3eXGJpBcW{vSdZh+Z-#C`NOZ?*Q=*I^Ci_*^OQQ})~ACc>8%fFR&+B2+D$8uw__(s4b__;0NhwJcrt;O@h)gsupLyE!=+==ThOULu=&R_S5#%+}KX%r8Tb!&G{hX3YQ@$C(2z;FMH_=fud_}}}BueWm%U%xw1>Rac2i|3yklVzN=B_5df&@Hk*9V4URhy5V^)l<jGea#WDIYs=Ccv*+G#6Z~>wh<fQU$tTV->HlJ^0bTi`r_fZZw_{m`nKEu65lo`81oxE6xZ#3Q|8CG_fYCs&sCE;*23rB^R<t+<Gi@r5%c-QW$}$oiAM_hMk@Vj%f;6|sxH1>a{%Ujo4Z`sus+@`npF?`rM@Ql_CdSF*LK$w-+DpEIpV%UeA}2N;yZ>k6W^A&75<@IjOW4M<-D>rn+LxZ_i0ir>dXqmbxVDN`_Yi;$p0Y)>n=)@edK7=2KA$U+J)<v7hhj}4f}D~Jn@YacVxb_-nCZ9xY=gG?^;-{YrlIA{pvLpb*hGoZ@btZ<NPol`J0-{d29Lb^)dOJ-VN<ZU4Zk)SI7MBZ-@NbwWU2;;xpNYwuvo~|7Do?w%EJaw=+K!U-O8=_y_mLdG1yL?RoVO?Fn??9Gm)lr_?Do8RyLXM$%tvsqOIRHpBeB`9#h`t^2l}xQ>qXQx(4PA{P0rw!^Pq1pep{@r}KY(9XN_aE@&K7yPSUnD@S!(qGHt!l<8J80T9RU!2dbZ+1xiz(4T(+58N~ZRrc~^<Hl<Uq`Fr9CSV@zOlU{&ZUjPa_(t?>EdhaTg&*^H_Skt6QfYSS{baLLteP<&W@-vxj4pWdkp+rk*G6oBl`96D%?Lj8X<q$8jOGXT-4Xgpq(LUs6VeS@>7Z-zt<}4>-+bxk3KJg_Jrr+zL0Sh=l+!^^8He~KM(yXRs;Py^Z?&G4|l}))Zc*XTCRz23<yDf$)cz;?kws|4V3%4WyxxsZx33)pLq@YV(CcS|D1wR-!D_@81BR5y84Am@D~NkdbXFXE!Wl7<>LF?ge38;eH>EX2)cpy8GeT`o>3mSZ+<r!?*oq1#C4mF$8*X0?~#AUg6Get{qY>KL`QzoV`-0lY=GQ99LE~L_l=Zsus+U^eB0APsPilW_q9>W<Xo^0evS7xN4MgBecK89F7rP8mXEMLpLk-v3T5EFamyF`_w`}4=kjmxPnVYVIKG;JajVf-d}F*Ho|i^_Ci}uVydl3&<9=bR3dVfjtcdGAypHqyZ7)1W^?iZ&7JF7pzMeHm_Ot!xwRj)XWvTc!&zW-mT5qiu-xgg0_oEJ}xF7GIgZw)lScf6irN4&9Z1~p);T*ev1J74=Mxai8Jm1>Gld!K7yW+jhfW25h-hITktO<c%@hhy8U~d@*M@%)e|3)#)<L`$gU!R_e?|F4c%Xm7{$Gzv<LQ=3V>h;9DoI4=Cv35W1Q(wm5el%tR{Gyex&WHRe*R?KdiuzBUV|-rzCFhGJpgQXJYlQvP;5p929p1>d;rY!7JCF0fd<wqre!LRraLZCS$C|BzpXDO;Es;^;+b6~2y~_kU>fdjR`%B<ud4FR&)e-lRv1_s4a!-q|Z!dxNU!9Njwm)5bZ7!cf67FJO>>7agKs&qQ{^(gkd`CYW{#$%Mve$6KxjNDfe%}4-_EY&jYpi*P@2M}E!haBsb#-Gu-V@Aji1W>5ptRpu_8Q+)=gmiZ9wp#B%(;yBKxd}mxjpP3>}$th@ip%)*#+z9g*}m9!GiBEf1~|IrVIR+&e*3@LuEWIkN=VP2YSV1%wydgJcm`jDZX~t{gUJd{wVEs42;A3h8nKYFJtHh*%ubKzQ{iwiFLklcv?YUPl|faH_Ba;@6(z`Pdt~#9me|kWdhy<{aH!I$2v9(^L6#6ywA`}EWkYay5jkN$~y6ltXk4eBXktrH@1nCdC+>}+%VE6;r=^*o4hB`Bkp0p?>#Qhb4EgrywA`qrKOJL=1A-->uvFE3pc!XAGeJ35nq3S=WW}pF>-D@5<1Cy4z2Tbte@7iabKtxEq>l}vesdSJg4f<+rYQr`N8t}RLOVvg^I8Dc#d<@Ya+h?JYAI}?TPin^KF&cc+Q*t0^j2+%$N5$_5~H>y^l4uEBra-aURa-isych+Tz=i-$@<EwK$xo4gJK|f18SNUXmjHvdu0d?<ew}dmSGH;eEmKzvcaec77MexkoPg)p!Z~`*ZPkfh4^5u?_zBa`DS`!uRD<tL1xyqstNTZDAQ$S2b$meiI#z_ZIIu;CcI(viRQ7xo3jZ8GjZ1-8}$xW_XFOXDyXFmMxc1CoO)l=((DBK8Y@a@AEVNS|IgiH;{AKl6VRC_bW@}J%k?Ri~e@a#q;gt?&9aYuhTmR;=b%1FkN)%H9VhOF>wFN4xcO<n~3+Z{iYl{5c%F;%P#-)BBo&(O;b@sE3Ng3De$K<WvZV%{qO%&)<5Wf^{29+p#S%u$~Ky9NHXIW>I(8N<V1$zpQs7sIn>3}1aboN7BdvDqHZLwBJZGXB`Y<^JIIF_inFM{la-z!E4@d4WX3BqoSZbRs1vjZL-AYl->#c++l&X)x8%3{y$94+^k1>=1BT-B48?y^{~_<EZel2QFciO_{zLwUzyE@v*u@E|+Tp@bT-+(YZ^fxa$i>Ot48?`0&g3T=^flF)?94pHML15cIVQKsugQNi6kla1KE_a-Nxe?K&aum+o+odkZlRthpXV5DDKMs6sGG=2XOq{MvDS<|W~hCdV#cow#c9+7WTn|;73uulJ>);AY2-BKE51a%Ma?FwcxuKwhT`YcTjX2JSNxKCpPEhnH}x7dn|zL%LCq#-vp*TsgX9eI4(b6de}5@nMg3LF-<ygTQ<stFP=BT_BQIm#&kV)CQPaq29Mj(zikDE=lGk$nmN3?EUT2fH6qw^}48@rY#mA_7$a^?9d23Sf)dKT(m3oW(H#KjaD}F+~MZU#(eZo+z_K;F{?k{hu7uB8Y&O9%ER_sB2PFA5<bIM;IieGXaC|05P4MXv>0_)}(^&0sZ`5r@YmX^PsvZxv4Eb?LM4)RnpCYdq8jPI#q7~h#O(v0EMcr%7j2Qw6pqK+hwB9EqiNB)j=M>7<UqfQ`?BTuAGB2QvlCo&XIV<?_aokd<v{gFD0Jd1fhG89jyP9RSv+X{?}jXH*GBY#UBN&c2Rtiad}qsEhmk%uxA4=OOegQ$baN(YiFm|-!aG_?%5EY*vlxD-QiF=`pI2i2MCPS&V}sP1HU<`trrA%~gK+KeXD5OPCm5H*DCXGRS(8c^$!>+;_lP(#Rl&FF1LFEgr{QOS%dW)wD~s2Ro0C`t7;qq-Tj&8TO_N7SZ_Ps|86Ba#|Q{e=7p^FkSln^EhLo002NYm;m9+V!ac<i^zI)BtizY9nd@xfZoDHGr(*U+kkdxgxbPxia%BQmd1dRwY*?SD{uXS0UG=)+5&>2NxLAU}{rxFu4UaoZP{TPtAy+wjj4)P6V|*IfDEJHJqF`XNo&fJ5wXcD!OY}C%wpBsh!E4nXmXOYBV*H9Lc$lrnV(VliN{4$x54%KclvyHX}FV+_%#5*F-C7b8;*4mkh;GTK-yzqBbH&k=rm7*U|FVP#tPzavib{)tjueIN66>f?AZUv@p2@xd=nC6V-*RQJtwSWEbW+GZcGJi<8xPrOp>GE&rVIq82CT?RhV%x0ZkIDK1N`NLE^fth5rjEV(p8aRr8A3q!FVLvamiHF7o9twF7+<)3XzgQzvhN`uKk<c18zO{gu%N<SqxA%`&(w`M5*oT0cQwF6mc1i2%*3-t?f7qV5$-)~lGXR?(XL+wS5A;(gCla=-*$CCRo6n{<aPaZ&xqxL8FXI>mbaUW_gveK^PKIEQS{+{nijVAXb_n@{T_aJxE^7nQ(YAdqRFUcR8QO*qYU(9|$^)$nc%11omB2-^3e;+9>K`lov$GUm@PI2BoRa}P}NNz*bse$A`=IIQ@A5(qFACvtH^ueF%N%kj~XDD_p&`(#Y6FKiJP&~toDQ3(wBh`#kW}Kj&C7&SwMLk7UdYOEe`jC2=e203GdYOEjdX##Ze3^BRQjd_2lDAV&kx#MRidRzY)Ks#HrR?K8ax&FUwlhDOdV;KUFFBdKi+X~*i+q9l7x@DDae*;<OnpdxOm=fZD9$M`b~)6G<Q(#8hT=m7#`F;NDESb19d$c-9eH7av0F&BlNXX_Qs<GCP9e`EkEM<$e?uKX9Zw$5yb%n=KQI(er_LbH;Ps|66fdGClao0Iicgxc&y3w>tfwwuC|=G`yn(upypO-XfuVROL-9@O4YI2fG?$-mkZ&+Am!bFybvOA6d2@lbZl*3EE1gR&W?rkX86_Ac%_wa~8LE#N<*4Nuipx?<lgpAzQA?6bvTiAcVox(7+d4UycKM(F7lr&En;a?y|A&SD`kU{+t}XbRb<Bt5|9p8H+16E^Rpx_;vwYcFp`LEF{{Tat$es'

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
