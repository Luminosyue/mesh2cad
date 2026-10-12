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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/9338271b6aea4de89bbe37d7bc0abcfe/part_003.stl', 'relative_path': '9338271b6aea4de89bbe37d7bc0abcfe/part_003.stl', 'source_sha256': '01fb799c3166ae3446a041cfbba9b74cc1b857d4b49b52a23f88709f075d47ab', 'input_faces': 448, 'input_vertices': 282, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2861103415489197, -0.25643301010131836, -0.42565101385116577], [0.3051408529281616, 0.18939945101737976, 0.17192046344280243]]}
GEOMETRY_BASE85 = 'c$}r136vGpwTA05qks&}AY!~I(tr$s#up?&Uoe0?L<vCzjBp!hCJ_jOXj-r^f*2y=Q<UTp-$jgwOb#H*)YZ@<Ad?D;F<c^T)F(osh*8AUuKM=Pxrdvzvfk^p_WHm6``lgU?6d1sHLZgOR;`xhgkLS4?afDDb*8!FNYrt%oO|+T%$hVde`d$2)9;Ho^#fnNRG+xzwn2kOM4Wq^g6whmGsn)z?jFtVF}_=N`)Ky~X)|Wc$eTKP+Kh4e;`hs&GBe-zXHLwUp6`F(rc1Xj?V~wu+eha{|Bqjn_*3v!-g>yu*F^rLgQCvsJ-tH1PYxTqFU`-}7mV{5?{1rU!1P_s({`e3`qA6NJQt1E{MUu!6C+m!ej@rwnP_ZbkKnqAkGAd)=7XQy@YO!kkK;R|YOe^ccf3aM^H`@wVV=4L6{hc~zu;2O^phR&&rW+WZT#00c4f-roeTZAl_!Dkktf!$?%qIkp5xXm%$4h%U%V$R|M~oIefV~M^)<iSV$93IxCf6`q^<YpuKlL(u`Va)#s#Jy<+`pl-X*_teK_7}w>%vG^uD5CK4<Hdn!ckx^He|iROq|y>Te42H*XNmXVAyNxcHSrN;3N7Q9pt29eZSRFpvCi%7g2Srw{9OIAZ#7`q0}^xFy&0wGXZFG5S!)JKK+zoBQIndnnjH^|k)aO@p5eboe`gA7y{tbMC5K!%rNp681;$?~2XwE`F+R_;GyaiJaGh`E}bB_}+%@JHx*EbFt~W_?k!k7{0S)a*!wfT~0W@+YfdGKkrvsZ2B>L&7;19?=4yx<Z<_Q3CFYV?&c{Krth)u&d@dCeRTF{*w?y`8~c@;zN>ytzm0)EWMi3GH@DiZGSk=kxYO6Y6wG7Psxq@a@lMOjOkeBZHFtvh#hJSx%-1s9FK<%vtu$Zv@#Hn@WglZjv%>2-*93KNY9_+^<Hzt*^~aCm$7+5a)GaxCWSB?q)AOAVntnp>(^{v;<Qjf7bv~qzPu-_ZINrU`t<2nCFSk|rJ-+Uv^HgO}huFf8O3gm^Zmig6`kLP@o%6duA72ytT89R|E;W4z-@U!Xt3kfIR+O53;`Exc$Mm&NV&DAg`C$F!GfT}rNqU_sOkexNIlXdipzr6EntkHzTv2ZN+9$DZPpuE?c;b#QKmCx5PAxb6D84)Gg$?2NZA;VYS$Vw7^tGPu`sqO*x{p?tnDt4niI$nZ*2lZ{ba-wTZY|C<UVVFf^w6B*jPt>_=M#ITZ*ives&B71_FQgprh2Mx*E8`@`{IoIg>Ubdd!lM_rhZW0?gww%SGzOyoBDRYMa$mUovEMIxBJ<1C+^O4zo>8DFK+GryEEOt>f86P`u6>+zJ32XJKKl(t#d|w`<zkVK4+Yk7sB;h=b`%cc^Lcl%r0}^^}JQzK5w1j<-5#%*YjL``#ew1zk8Rt@A|w@-+o@GZ$GC}d93G@`u1}w+3$FfSqFV?s&79x)wiFUvFvbu_H$f)`#G+@{Tz?)t|&75Q{OApx8Ez=E{}!tx89d7^0}`1_WM%&w%UPjzrU$(zrU$(zrQ8USA^@c-ZRy=-!s*>-!s*>-!tP6HulW===-qx_WQ8<_WN)=cKwdDdGg+_zWx5MzWx568gIS-tAEja@a^}1_vTq|1fSRUjV%R7P2bVq3rf##&y{%`T=IJGbA6BfdwAZ)Yqkk|eed;p-ha&WV~mgYoL8J{_%83g_V_68y-^+Cf7Tjvp0Tx8zFTPc`ukUGM|7X*>+fH&8-AZKeO;IP^}<5Q@6|lH(wx8hLC^OK4L|jJWzSXzO+WQ}r8BLgnJ2a0xsg)SPw0BB{HfnV?fm+CsFgoeAI*QN>Jz;(?2GNE@-#oWGB<-CKepuc+zfdVHID2FKG$dY*4&^@HOoxjxiR$J<TIY>$M6$RUh=Z($ML<-9(vLA6ZJ}ViAJsb9)7~gpTtjE`PGk|O3xqf*{eM8t^6*&XXQ`eN0+7N_jJ7GFBq{m)4Dw8%6(?tV$UuvF@3vk>f3cw-|etzhgpC1?YgON*C&;y#!IDU9n{zQxYj)F`lPOF)yEq=A>(zEmCfD^#+~Tk1$it#Ht**p!Mey39dX^88Ta?4`GN0dvA>PChwndic8B?EEcMLs>c>WWQ*7pU7uDS#=HKR}<-t#o-+BDjwQ1wK9|+GQ#(TRL2EO~LQ)G@;KQ{W2V0;We*<$tnO#80Bz3=MV^;h4nzdP?j;CoA#Za3?!ezHlQvb6E5;s=8H+;MV8+IakA=jEkl-I7NZhrWB?&L9tUP+#j7yM5RnOh5L>pi;AL?kk4^-#vF%c>XS>&iK)*y&^M@`d;>)-NEN9KYGjCC1#zS**6_D_eJxlA7@`Qk8^I%!A$$2zP&H%yC1gSX4Wk=e$M9Ynfz$Mx?sI=?yuB%eEYi5sbh=G`&xbbeplbVUs8ECwl2<?=lH87=KZd|ho7+KlUUU$t$$K=IQ2zl-|E{`9{XIqK>ZKp?J)Z)<<AfMP5UI}U&j5*KB}*M=$&i5DsB9a52Wq8`f>VG`$zp)-g{|%o18P~P^P|8-|nkKqxFX}^||_XpQ~^8d1}1X=WgWSp-lIq`u6>(zI{JNS5yYReGaH^p96^vO%8|aNk3=Qzv!G9-RE$o`%8WM{!-uWANB42i7p;;*xVOAht;>wVXw_&;XJMLUw!-hPmQ<E|HOn%fp0%|)W7Jtv#uh{^XZth`&xbbzD|vwnVok3CbHfM*K0oqqt095x~y}cpmyNf&tLWJ=das$OvXI!-4BO(taD6#`y5k0f$v#)biH;S`+ZOSe>ETb982Y~&aqS;{9wI<)Baj^_>}=Y+{XS;KWaN!&iFjzPi11tmuluel}+mUZ~dvPYu9f7-#?Z8$)Ce<KVC&Q!K?jvp6{Q>6F%ujr5{Zrp*D+zywT@ver!Ou!dv<NBw7i}XXLY4Xk$1FZh$s~-|#=Pg`6AU7l|#*QS>!<HS>MJk2UBkgz#o`6WoAnNj*fR7RrtMxZs5Py%VzIbA-8zUJk$P|L7$@)}!m-_3#>E9oH9K3%>ws?N_tD)%d#JwMHF;H=^s{bzFNR^*AB@>PPKJsF$E8U<u(%BVh=C=!7-@kh*@z_$}ybu+&0oatwVRJ_c8yd*Ei&sxjIGZVWd>8^O{u+x^&!?t}NjAETeZAH%XgqOv!_70h81x*2Z5JT4=IzjH#3z~7PQFR0}G3n9E8-3RZ73(@UxA-n^99o_-&L^s1b;WyDe@SE@-(f8p$!spTN;q!1k`d4aOj}WepHi4T^3*p+_f6^}vxIdD_pXdY8SK-%S>EEXG(@A<udgvq}yw&Klt%UFf`bv7JA$=fx9IpbdU=M}2(G!*Iz4Y0~^jjr;QOOwL5B&JE9|s8GU4*bl2=69@4-&#35yIaR!nGn{2-l5-AzU*OhVVCx{Q&;Vk9Ym}Uqbk8^d0zZxC}iEm%%0I5x4{{N8f|X;iKs1@KN|QbCBzON(di9%iu$BF<Jr_!$oL0Tm+Y*N8wWVE%Y?}7JP;|oHObp`~_Mq67m;tl}M;{;3{x+v<6%qu8RKM3Arl#l@sb2_zd&;iaC72zI_J&6_xA#mG6bWM61IR!e66R;jg*=SyZlbmJt3MdKx~>e*KL($n{R4U&3FK_Y`^-KFjA$p`XK_q3;r>=(Ts?!^A0i>InQE`Z=8NW2GM}(BH$)`0+n}{0{wZSmM9<`7`j7=#}u3@KtCP_$s&>>cG|D2wD}6z}3+oz}4X>`UD(>m$8;*tY;a%@Nz$X%esHdxCCpFc|S!6KZaffKL%fqR)epHYoZajCR_up4%dKdF^8qhV<o%{{SSB<97Suvwa61?&QG(Br`a>%Yy7y3&t1l6gyp}zy3~)lgm67H3$6z@A%uIPKZZre!ad=9LU;lCD_C?fyZ~N;{u*8aKZ-sAKMMZ_eGvW){172L4jlu_8tbs`OW@jQW4Jclh!F0M_JDhkuRA&hmbDbHZqd=OXm6t?y^UJ+rmmt_!=eq1nm1%0L>n0U(ttII);IRCK5G(f3D<!e6D?VXXbct|1^0l*5u>Q9=r3W>g+|R6vJavU8~gGw`zE@`*vCce^CIfC1YH2fm|q99KHLFriZ+0o!p+cza5MOF^lJEWxFaFl7wrxAX8-yU!gmnD)6oLBfb~o#gy*9V!}DPmT?o7I1L!Z|2jFRh@JMtNJc@daB!qv0c7T5ZcS4)Oo#5tZGq^c?1$sGr1>6Gd2)BTLNC@{w`@(&xU4KG&1R*>Xoeoc@UQ-F-d8iA|gXf|Tz;ogI(P{Ag@ZE&)aC9U*l6nm%g!`eL;C^stv^m@vZiQX}w}P)lTfo=Ct<fLCt>G?&@Bp+w+@IPFAcSuxgr}fW;i=SX3L$(SIv2hVz8Ae8z89W@-VM)z?;?bUp~K<f)N2?ad=uIkz6s7jTfsSSHhL|b4YxsC!)@TUXcxFG+?5a>hz@`UP`iPI@NI<fWONEVg?ddUgzrJ`h3|o9qjTWd@GSH$cosZ~5FUySgNISCp@i^%qB-!*XfHGe&Y^a_2;p{U8@L^O9oiPY4sMTjh1<iqgzzAAAUu#d4kCnqMhNGjli|tKE{_nNiOz;+!ZXlW@C^7D=p^_TaGVexf)0g;Qm-LK9fvUITUnpzjj-qq#@cV79-`fh`gEgyqCYa~`6KEr+Q+DWA7hXDFb~mNV9~+w&F~OnFzXZjIV?KfSo?VDAv(dR&jjixI?<@-MCvVir&0eqjXk=P{S^Hv{8Q@nGjtIA2S1+k<5@o*M^_NStI+4*!2=^zva0^8|JC82UvBVAg!w-{*q==QXJ7M^9sPqj^^d@V2UeH&bpIEXDnVgBk(1Z?2f}o)LI'

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
