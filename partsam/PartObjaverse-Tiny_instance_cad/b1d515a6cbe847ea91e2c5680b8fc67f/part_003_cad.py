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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1d515a6cbe847ea91e2c5680b8fc67f/part_003.stl', 'relative_path': 'b1d515a6cbe847ea91e2c5680b8fc67f/part_003.stl', 'source_sha256': '5d8317d82fa719eb0f5f1ef6b1ac5eddaf34a6a5f9b08bdc7638bbe92937639b', 'input_faces': 296, 'input_vertices': 229, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-2.1569700241088867, 3.924858331680298, -1.5123482942581177], [0.6592787504196167, 7.39937162399292, 0.7346189022064209]]}
GEOMETRY_BASE85 = 'c$}qL2UJ$awmzUHid|69sP|YR8i@@>u;6dOh6PL1SPu$Vf}%7PMUTBV)L20M#ex-U4ECeg#fAlglml3D)u<6;iShDgzP<k^x$C{P-g+0;xAvaz%-OSN&z?PV{-vL9k)lot{nb!rXI^^xzM`T?lv13O$iUF>(IW!G8jKr1*-j}3UjEtS${yc!_xs*XiBzVz1_XwU2z70ty0!}Pbahi*gF-^XL;c4M3keMflzd13;IKf!hmG<dA1K;&n>6uqQ{C&isnP2H^Up!JpigdVX9#HoZYXaN(&9fL=d_U4oQB}FQe7)Z-WnA4Pw?9N0x5O-D~^&^j<!gZZ8hu<@LKy0u%p&WxhLDk%sB97nQO3PxO@FB+e+m*#6O92!nm>3bHUGj{z*zpo(cPUU8h|buVWqXrrWS8uv1&jK>O^+zwmr*1Mte`Jt=tKIS0HEyqN6A{BR%roIJs6ajU?q-G6)verY}8&y57H@41aQXst_={hm9if6FgnU%5N*BkVUmQV#t+=A|J%!~DRTt@~lVmSSFS!KYRK6LHEsSV{6)@nFQwGRpzHe(VJ7n_JqPL_g2VAHdhlL>!C~6CR_TbP>GfeG0ra(cITY+9{a;-jY5V@i*qjJcEC}v%#A$PhwmpDe(;2$)l+MrfZeKziB*K+A&5Kyu<kCr&R=>)$S*>H|2xZ%T|CL{l{JpF|T)1!D~Zf;J<ZY>C+fDHUPZh-iqScxcy6v8{QYZ)vZnyisx*^-?(2Aypa@vd0AR_MZPJmuOoiOl}O6Zs4DN#-nRq1S-iV5{45y~54(+OgIB8tl|?*VH#~uzKV$!ZJRFby#`5;?U;A|pc(Y$I%-1sd!7u1naU6I{oqn_~4y$g!zGFx5hH;Sczt_N(GH&K~Z{NV)g)<blFM=PT-`iyH`UOAO(N;u1fSu<P!CNL>{0jD)r67M)cMZImH3qzOZb35a*7E?bcus`>mf@w5Kgy_D)ZcS7@=#sX1o1I9mmvF{j+1?-F?ksG&Zm6%Q+fsMmyUyDrT=>Q4DgoO@$lbpYLQFpvJAZD*baGOIXm(s@~zz<>i?@xRjlvp3Gl}n-3z?=^#T|0W9{~%|3hEmwYjjbCdObtS}V3Af0EZ@z4Vu5(N<EM)40paVO+gl7vzIsI#U0v_n4Q(vE&`_4a$SJy0(Nr#<yiLU*(KFcr||=`WxL|9fIA4uU^A{pV#1(K_@X^bJauQn~egm9_WMpq77jF(Qw+=&nxh{n&8z_d$2BgOP8ByU*1LhsO=Qzh%E;8S4As$%`=+v|6~&4qr`=PxB4BX{dli-D)_mh!RvnU#J{h71-x$$;*-lF&X&!~pHRK+0N(I?OZ?VBWar2B;LY)A;FT?N(j>1P_a;Br^@0D^XPb8-pKE&&zho@sPyOo8@%{{V;;;C@e~WL^7l^agfb73@p*Yl^cm(!0y3u??9#h`h+rxizpbB2ueg^f#(m}b3`HyuWJB`;<{=01b4ex(+ruiNzO?DhC=&!lhQQQ{if>-^$Z(`i944gB@(=dwj%y+NQZn_t|c|L&n`H`qg>ah95yHgw#_e0s>_33n8?JEP`jDKKKe*2RB-~i;C`Arng1?%=M;4OdMN1Tl>>r#Ci(F(lk9Yp<G97Voap4OuNNvVi~acY7|`|2<9*R4FQ`}rvNsfWHI{#<GB*6w*&7i;yC;FTc>l+R0ttcIQR)x;+nG_UzdbdC(J1KzTq^3(clpUbENzdM81W*wycG9wuAH+ob6ub%rzeh&T#@lghw@XHc@mg2wN^H;=Y=Oyq;r>!*Zk<N&NWqEI!$L?78uV#O^hx}Z-5qV_Y5D9;@xJDG0embpxKX0l(mK*4A#;w7;wS#epr=^YkWsEmtA$a}p9mL-()r02$>;uk2ZQ)ePPv@{Z7&jv08SSsZbUyYBxQO<N1Uf%6me6_k;_`9i)ek=qUoVmBj7tZ)w>)(QZ(VR2anpCr+Km0)*@5^K)5-qY*;rq#Nfh0u{1a)u8(ZFz{jHbFgIAlS)4qG-Nb?+DfVdh<-6;RpM!>GJ`XqSe&q&l&{YED0l_g^ecr`W*=Z@k&JPG|)`h&OBq5ei=pR=gXmiMS1YH~X|r+g=YR~I}4Zygy+{lg1z@6s2ifY<zHQhhd-XCi;5_64si8|dDZ-W2DWawv`RZp>cHSKkm#>yj1@-ZE$hotq&mQI{+$nuAy3?dV>i)}VE7@EgumCGKTan%C9~@Gmch_^^DeyXO8n8}Wbr4(Gg)(+z%V<BC#Vz0U-%MA7|I=|2Vc9PNBOc+;U4`TwHXVe~)OmF^46eZd>=W}}|#jXDzFpeXe}6>tXp&vd^qKP@5qZBOEyQagPOUccRw?ze%TlCkbJsuN#+7M(9Wx?jM2ix(&VYxG5b({9dw%=dvEjeF=<s*~|!e#U%18FbE1Xhwd%b;h`sZu`M&eb3W9wptH5@BCWQIq5Nm?&qhg>_flgGSt7I8`ZtF6HLsj`%}E9?kGa{I_JdO@V|aK*(-5^@?>Xk%Gb)<=pIofmF}^wx#+KrnF?O(-JkAzT~^}$pxvBE_VrVg=dMZE|7Oilvg1&z8tiO;gnN;7-7mPO8-I0y9reHp>}w<A4DtO9I;Vo)-9<cGEzF@hpGtKj+4nr+lM+F^UmwIl&9Y0O@dCiBOWY}*L((#kpCyNaS2{PPIK1%6gdLy3#QPqgd*h}7RL>6&BKtmfX`kji%7Q=j8dLv4RcT%gOJkna)?b0w$1b9ESri5T6~}zkT{E$O*1eWS_lh^s;H|ssq0X3NI?(+&ZX)$hws3ro;NE4fb;!cJ8egY-jzj)o*bk4uJk)A6X@8{zpw5`P>Jy*Ukn*RJ_b;dqJB!e~^F8RCvbg3VPgd)w6Uvik7+32ThW>gUf442VNc-ht80G!QYT%7?9WY<zSrghXqaLS&pWlJ<<R6XFkw0N^xTjn9&ZfB4xJrKfD;B(Ao};?@`rdu`xi1L3*>(xVv#9+8@bfCreLw#;-P2O&JX7B6L7X&KFW6TyRIYmksAm=rT3>6AB3LioV+43@=SIr6qPdiZA6=;aEoe{uV+xQD%D|2IKGw!=p?lg&w?~N2o~3tTuU8bs^XzWaNxkK7h=(=Ri}q2*dy3Z|C2zwYOB0IQwu%@}-*Jk*FBj1MRjcJcM819TJ@K^`QT+Q4&4ZtF+R}IYnlI_z;?a!a@I2%e<drgX?yvEO9X0nozK8Vs5metC`=CBpE6$+rq$p>a@5tKVjp)7CVdsJyo%;=6VqATf4|v_T73Jr(<*3_w;F@dj^Y_Ixuk3o@m1SeWTZ1OjxqNUPoyXo8m(c%UF73P1F?6mp??vbNsT~y0E>`S2Yuh5=&D5`{-Y(9ib#1#1=ZU`mDxHJ#U!e}_TT6hqwCC@^gk-8mm3+>DU)+}R^ZQb?zG<s>V|{Pmr26pG8|$maH{JpN>wD5V4r-T!dF^|bfN_S<em9F<Mcm9sufbcNb*4Bk{Dl5`(X<4ruV;zhJq-I!T&%Xi&hM_YUfT;OuWBS&(f`Ij>E5zA9QD)Ea3Og0c^1`^Dn3V1-`2O;1pilQ$REuk@iF4IqhJI0sq1OK*cZdOtfoH(Z*4P@zWWMhJi)q`coc^?zgbKBw5%h=t<;Bgh*Lx-+FyCE5H};b4DPM^g(l#2mrqn5{93Po44hB*z@E8?kCJ|P5yrKjOL^P8FY-zoUspr_)6MAnG}NE+B&T2o-fQ4NaSm|A_qZ|1CkFF)+>F+-qCfnxcA2mi@jGr(J*oTx_f*TugiYvQrx)#`u|tt3W^i^q?BC$}R&Fib1Ik8kgI_nYX}wx2^t*)nvhA?nc?-=esVnXGs-5=2&b4pod+l95ja%vH0pvx;74$n&&t$p>X1bgse@f9g^}!W+Vz}J~Z)A_6x?L&&ymj8jYgp&eohUzt7Nt5?DengSEOCnbEK-N^|I<?XUMzWs^0r1K?t9inQK+w$B^7DD4+el&d(=RkR<<`G-eDDePx&7}-Bre0$)EV$6lc$ISWh*4AN{T}ybjI_!`Y;Do|aAH7QCW*J}jQj8E+nUW`C;t173hP6VvE^RrNs%{0nhIUZ`WL(YVDjuEPEwH^D2xPw9R&z!&vPE%So-H2R&;I(;bJ+tWLv{^`@6lb@-_79lRt$EYs0@TR!A+@A{jH(ap)w4`w~?ia=Ho%Z|Nuf{X0=4WeVL>GY)ijxxLU+5=eNy<N){GWd^9^Lf+_LH%f$A9{h@eH|i0?Pz;2`m;^!`RE*Hi0mK8H}CGwG!|WXu(ppTMBfS%Pr88rECuo2omVWT)#rk!vzKjgs_zDp>mA`Qe?`pyve$JCsbfL%i(O_%I}7-v~vFq0vEXd1#X`c@E2$=*Mg-F>mlr)&0m{e2L;y4HDf8;hXh6mj20NfkopfC%Viv2i3!Z@5jZMvisc@Tb5nsP0v;@7`&*8!jO%v{sSo5ekZY05kop;ZCi}EuUCO}%M+9yNTxWTN{g-i>$8nigD6aCo4g#H7%C@&cd2y0`KFabW$Il|riKP$6b)3L-fu*cVIho@mWkjL&IF8dqftf5Pa6IGLUz^|Yybf|aUx99{cPliu&G+^!rC-eiItsKEaA#d|U6`{ylkKkjtO@u1mZfYD;IZV`-?Kh|(VMwmEPJ!PUTm`$b6t5JOL;ESSuW){M{o=xxILQVA!D<c<r>yEE0ou^{Fd$W0=pH;)wv9*%N$-SFjk?xEwPQcRF1DLzhztIi>*f3@^u-HdstwLz(&@k+{dw!IozEg^*%i20)ar5V|m<LJf_XxTRirU3hm_}hScSrT*z}QoV&6u_krA7XISoJpMwQvaf~I#F(>U`X1h|RurBw`VD@h;>tXEcHlCxD$*jx$(V6=VV=3DK0wa0sSv;oXG?u}vODSu~cz)lXbtz?C@%gv+WLxIkC64<(Mly49ugW@LtIOW(;{u+;Mwa_nmo;>RLVG`y^=OXYGLGRgZp(APRtIhKvgNO|AH(m)aC;-$lk0D*V}Z<hF>lKcFMb})&jXduxf0FKW#1MIseABPG7nd?jNx%Z`Mr6Ce3JSxf&BspSeNp+K%BsQffbBR%<T|J5J+PD#9XYvDt?wwh?6#=1g5Y)h3#GCcWpLg`wIIK$K&m1DSetMFh^h!>r(2>#d15A+pBoYsoW=ur5t;bKqNn##8N(=Ca{FxoyKww_nlTqpTqAYvY$48WqX~#HJ;PYEU)q0X7hMatVeM?R`Ix7841k&%({)U*;~i&&u7FjcY=L5#&SRFXBEnW!>mhrQNU0>=ZL}5_WTm}k#$7g56`od?S-r_<o8drG<aO;hwW_K%kA0h<4lIsWxbX){|L`5p5<27WlWZ`jA!0<7EWS)65GDc@7io#=eVz9pKSNIHQctHwbNLi#%nvd(3q21PE$UgJ&~+O^4NEHo+ntB^0q*Rz<q%<)}?$P@Qc7*fpmd;EM+^B^&FO&+*iJn#Wu28X7M}M*~WElU*j?Fun+fH%CU0=Oo2Rshb&D-CUZF~GkJ_$9y5=nY=5oLJ)j;-*_L+zd8d$dwE;^v*5$K03e}}L+?MZD6OjK~q&UNgIaQIL4vJEVrEJ$0a4E!9;&x4easm~&?ZUd`zhJ!_>r$2ys4O7=e@J=OrTj|3Pry~6A?s4s7pNuh4@G{~l9X*{fnxlw&6aGJ6z~-2uh3mcq7!r96pDcdw_EUg^3R^7Y}*M`=XsQ7S%LME+_wbFlKhVC{Vy2uuL!?Wf%OXfOzMp|j@4P#WL?I)sz7s=vR#+^G~%|(dR^{Qnfq7fw)~_k%6>VpEXwn8WL@@Y%yF%v(EYE6Ks(lZbGt9g-i!gveJM~@`J6vecjD*1yaxTbujKrE?d+Y3{BQrI>GPj1o&4K>aQgQ*|NdE9_)QNHr2qcN_46%;b+8xz<VE$C%wpxg04~g;Cj'

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
