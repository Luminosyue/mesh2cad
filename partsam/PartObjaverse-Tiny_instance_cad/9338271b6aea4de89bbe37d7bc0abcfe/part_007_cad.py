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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/9338271b6aea4de89bbe37d7bc0abcfe/part_007.stl', 'relative_path': '9338271b6aea4de89bbe37d7bc0abcfe/part_007.stl', 'source_sha256': 'eda4f0f2df949be9e2180c007df531d501c5f7bebb4e247f1f3784da0a51fe5a', 'input_faces': 448, 'input_vertices': 303, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.13558951020240784, -0.020221315324306488, -0.2821078896522522], [0.1355983465909958, 0.2799679636955261, 0.10618088394403458]]}
GEOMETRY_BASE85 = 'c$}r134Bdg9>?!XED<C@B3hMPu_P3OL@k}+YHJ^9w6u0FA=;{vO0-(qxt5{~B`TF59<fA-NGu6axlv0NOQ<eNd6Zf@t#wSToqPW0cV6y0-h4junaSt#|NOr1ch5Wb?C+j)iRtHEB~amijg`1PLw>&UjH0lpr35PP#ZO9lYjk{Kn+XXY*pvYB*`LrQ(S!QO46!NiDO1D8#3zoP6y8M*|MS>R;jPs0u@fgHO^Tf`YT~3Z@yzcTJ3cYq^b_BVO^7!?M?|)bY^6rFXr+Fn{*QmYW)ZYMh87nweSYe`Zl>zTwj3(5_;&clh;d(8eI35@?AC4Uvr$l$d{v|`s&a%r->Kr3zcy(^xhG%0y0eu09(@gKK6>-zN7-kkqyJvI&-Juz<j;9<*psgyf8jgftBs9PPriow3SYg!eFy3*d>y`y`nvA>IHH{HJJLP96TWtir?(GJ`;w_+mHi0w?PLBZw)zHqW6JEEbiV`N?4j%V2PhxIf5$$n?-2gfhC8Sovp0~h%{0oWJk2{$`x|TL@O&OzrTm@K?ZsAKhi|mqmrv<tcI5d?*u0&}kM<Y7(#=t3?HA{-D+?+8n{kJ&^%A}vzNnY8)1Sz9qzpVt<-9n+@Z{?soZm(HZm7?Fj0a`y-5g5aD5%gnPSg+URFH2xqVFlII`Vd|^|j&Ak2qIA<qJvRzWQ}3-B*ksdnR3XPERG@h&_IYmt%B+wLH%H6&onsxNZ5oeQH#=)l2dnsF$<eWb*Z9<MXLJ8K@V0ZH&gtgZkR%CGzx5d3sS_;TxlQdJVqn6`5}>r(XBfRg^yb4E2NZ<ERSjczD9ccyLTBr}5>ezLtC){VRL}zEh0bA-UWa{S`53Ak}-q`{b)7A0DH8&@WH;=od9Elziua{RPxMXlLPT(Vv%4eS^8LIm@<t8V~k{!Q?w94Btih*FihLH@fwveDr$oZAbY0{zp@{`U+o#FY0UGTAD}ceL{9qecST-3g4c1`4IUHxUXMbLcZ}zVujnhmV9LzpVyA`IXwTE3olc;&MAkizIuIcCgrm(hsLeFey==F?XTRj@$$U5c(=8Egs+Hp^Yc4l_4Sk4hpgku`To#c%D;Hoa;hiRVc{$LxG&aW;cM{q;YFox`M_7P4!hESh4fg5UHKp2zJ_(!mCs*`som6(?&+QIb*#f`>*!o-`{<<~B~$zP&fiM+9rp&M*RX!-Gy0ORoc?$<_xZXfd}CBU-jDFrv6(bqmG~2d*74x-d(?It4~_+G$=7!Ov(Vc9!dFrs9HjfgHx@^2AwT=(T>4xm^Ptt&k5An~^*XYW`o(B-Kb!nh(R;`*Lw(^JzQ-tky@dOYxpwlE+L3%dq91kt4>yzEI!5cW6YHV2ENBy@-|fAL>V<LQ^7p{U`X+p1PKTq`aV30hF87^c-Rl;gN%sxS$)S9(4hUb%@ul_LA=ZK0?f5#;|Lj&ukNGZqBW4c$9w~v`S2FIe_cZ?1lez2YzTI2rQF;yi2;cGTIsUsJ0N?K~<SR*~OUaL_mQ42>TE3R_@tr*DymR??r<PmW!G7m*2Hn@UQ<1ei!Z#9z9<YuFb>EmZbYG))cS?Wyq2cBS^dVo5<mGWx?@7L~H*5!$vlGT4e5FBrnYCW_@m}QH)e$?~$^+lH)T_)|9_72Mt3AyxHKafHf4H~9Iu3=e&bwD?9f!_o)u?|Qp<NAYKEhW97wotC%CZM3RIa;TZu3a^#{Hy2)^gf!bXiK*(|s25`OVwS<)?CAw3|_WZ83c=jr`JjU*Q|c!`<eQW<Rrt@_Cn!2kndg2k3K5hXtfzo9B7*jZM#`TYbInS)HzT%9`fMSA*NFvHIHKjI(>$^-J47x7JJe%1_)E^>X=xGZH=Jqb#XDgT?{Yd6)k=_r*Fd`(mAU`AfMk)_Iqog7jj4A^cSCi*?@Rr+vDZe5|)FUutJpJ4|_D8IAAjYuw7C-5!wPDZRSXAm6zL>lJ)s-B;wh);IW$Ax$?@`XH=7@STTeZE{<G;M+syZn3T>uJX@mxz%I-r*rZ=rPn6k&a;klSNi8SY_rZUSN^L$*ySm``jN87WBSf_-N&<N&-I;4tn<j#KBvOUJ*Br7PAm76UjH=RZT)nWzx{bypEao+jEMtjomYI^)2lB9@%=)edpjHUZ1Rm@_kOV-^s4Zbzca#{KX<Kj?|1FuFz&}4cN@3*jHUd!LK^@2>bT={UwM4?o_U;)TmD?(s_)}#<csGPSNY+K=N2s>>$k2fpNj84ru4PO@%<}&y~{xw|Bg*<3a!2~^cQ+=an|JNRo`kf&y88{^7en&YkHBzSKhh8`!P#NW4>cnAo*(QNZv2iv*>qD{kA#z&S>r{$=uf-hD_t*K5C|0IpI4y+;dpV<NW1<PU)rfP5AQqrZfngPV3Q)C_Wzi(%!fFddgAq^&UC=c|K0%{;OepznRgSes>i=`&|0Gde#DKIfZY$c4CFKoJvvx`FfQRyxmH6@O2!%acLuOw;nH~S$$>q9X|d;KcnAEEhhNyl&&-HFOk3fW@jpg{JS80`FBCdJ-dj~OY5FG>ol#8j>(UB`)q!Fw$;~0^yBko-0~EwueVF#^Ch>?LFH`pEBB?}JK@W}clN7~Qb?uWU*XHYzxw<od|f{EkjAH@=9v97-cDX8UwQ3%nYEoAy-uZ4{=P$KJUAln)4oYf3{RtSJZkUO{?4puzE7Ax$*ukM4X0OH+f7G4&PGe9eeFjUxwV^i)MpjlPkIg!zWf|we{DDU+WC29*7@bAQAobA2mZ2G_`LhFjC_5<*GH`VqTioF^ThB9bn6#KlQQ!4EjRf&O!nhc<{J;VZ^XgJ{B`z>ruLPeyM!-4cj<ZC$=5HwUT&S&>b{*kpVQnI>wtE@h^No%&)0!kd_Ed~T;u8G=fI`j)PM5xr0}13o^0ET`_l8O@a5-KwdZY~f7*$|d_3@VK<k)Fzu#&~L*Bnw2UOpm$(NtEg)cvE>oX6pC0}};clpxuy#6q69px|WBZM#SBOK)q*3)NcKVmeD+(4hDeU0$teT_P3G@T2``zGPb`zB|0J^s8R?c;<m@7D~YK2Im@?}RV!<FsZ|HdA?|{iB*bGMm0H?KjoeACNEaTZR9`zIAs8{#+&Pi-j-mi<O=2s9ofJxA5hCx4v*A_oaQk%a```>ViJJpQLjG;mhX+&h+`@%jXaF;^<sY^GK;RjQi3#jPT`i7~#w3Fs^*0a~M~8=^VzDzjO}c%11hf5&jeBFtfdAKFH@$!hd2v4qrZx(zANyS=&dPciA`2=J`nHX2O@x%^WY4@$}L;p77;!JR>KV&d23*Md8cmih5Ex`SSUsdN-8TwI|Lw;mhZo`meb=Jk?iAiKKI3`MlQ=l0?3IZY=yK&W$rC^YqfWwD9F~X~(hA1=jnD^Kj)(Ci(LDxxK|iYA^Y`UCj$B^w>V|<@0}S;d8Vu$nPnHFTbbIx@YqA()$su+<z~XPkOH;`>uU1eEGeS?2GqG!k6DG315D%<hrl)Udffe^j=B(tgm5hH&=bTRxP&r;(eU(<@a&2FW$%5`wVmUQ7_@k?+1nN_I@zN?JcSP%~QAZATx;>HIzVQY^>!KDKpuhP|vSO--`OLUXeycb^3o_k&ZUY@TM7WK_`RX0>20S7|ir<;AAt#oAEh<aUwJZoCqEZ)xcxHcIW`G9sCCL9q=3ABxou)3H$~0H24efe&}8Be(-r{H5=#i;Gd!YR5-I>?1cURc7nfxCWDjF7K|5}F$P{Tcs#Tlcsw`;8VQa8YtZgs4LkrE4;}!12f7^m4mcJ16F3!o8d}}P`84=0)E~@(aW!~V!PUU5ZJ1s_JF&Qcwz+_|_yL-1VRr5B2*$raSzf>3Gvh$q#~&OBZV0UoZU_#t@jM6PK8wI(pyA*#;BL@H;BMeZXaqPC+#Na;+#MVbT?LK@FNgjEyd3-!l$G}<Xmv3A_X{=5=z(DT5`yuI2*y5Uc(Xn;qYBgqTm@VeS_51I_o#|sEdChV5R7X=dw^?#dz$eHbQZJ+xChEQ3&D6Mg7FOKi{KgH=?KOzKz+bIs2k%JX5m83Xo+C_H1vVO`DySCh3i`I4e%PYkBav52G@hW2CfJ02VDbRgM1i2Hlwk5zdxX1V5UvLESiXhg>OSJZfZtrXe($Fa1-R&3c>hUL>StDX=6*9Fm8chtU_5?ReWar2yOld{qP9&5&iNQ{q`7jm<eTd5Piy6^flv8pf)g@k8D2AK`_1tW%KzSJ~M8FIo=T52pj<o0!M&DplmLM;4|a<3fEQO```?e;jc>N`onlIv_5z+I2>9H91d;-4F)#?M?m|7BfvwU8Q=_*hjCpq>X=a*!MHcH3z&_K=4P}(Fb;=$gTuj9pz9RQRlw^NuD!wQ!F`}zz)YV9_W}Ds>w@c|tbR}%*bnSw#%wcsDSQlk0`3W|1?~y13H1VdAs@!9zRfT{T7#QHy}(VuHYmHd4f+Xqsj2Uqu>`?*BJ^GGMDRf91n@v`U+5%oU+^I46!0K$0`7HE;rCw(E{5I&7lRK&AA%2qPeE^iPl1m>zX2Zs?}IJ_?*pem6Tk^5X9~*6>c1GlcpP*fcpNwy+7}!R?g||Q?h1YxngD(o{5EtM_-$|+^c!#*_($k1@Q>i%p%1~ogMDmVZ-QAc{uk<aMyVVRXV52SaQ!6oCU`OG{~3aDEHoM%3+@E%3ho4M1AQ6X2HY9?Hn=l54w?pz1FwMo2wnlc1pOU+30%v@mDRr%f^l6at7lz&W?U0`2F!x-Mb!Nw+T$Y9F#gVrb7pLYZU-MT<9jnsK+l3tfWL#Dv+xys&NE}187s{gX-1S8!x4<zL0f>^fy1C3z+vF_&{5#_;1ST3;1S?-=r-^+)GHmq_!{&a_#DcA4eDp(d<|U3#<d=}4!8ldHn;&e0D4*B%=9Xl1>^cQ9*loAV?J~N^eT7(cp>yMcp+Gf?aSy}rtIDq@wqm}LT!{)jE#C2JM~aEF_!!=)|g&VD#zXxjLj?P?@Q3{E#sE)3TPfU5B;$MI!dV=|BU0H9hA!X!niZEg;F`c7`K5&DV6h)aVO|VrE>l<jz#;#qRnFAi#8mIHfB29(&od_C-cEWpzXjzz|Ejx;AY@wpzXoWfSW@{fSZGdLDRv*zz*m&umk)Xl#RvT@R@Ni#%BX?F!&j005|~Sk8uq%J~hAZYvaNA4ubKk2*!UwF#a=w@hb?%x1lUw#_SoO6`p;VJ_TlaUE$mu><wKFX2EzJyw}0&z`dc3!M(xa8HcF?Z4B1Um}bUY=!amYAAp%o1vC8!%yb@@X)c)Q9<UDGieOxbVEiR?5BQK7Wo8^Oqlp=RGUI7z2)L;kZE?LVt}$+CMkua_;u_;}GY*<jVMeJL$IU2#R)8yzrUYpWTxYxspZ6lKB3v`@Jp*0^v>cpe#!=*Z5L^QN8e9S{g?<Yz1@D4pgLi=opqs!2;CyHnI1BgAM>%()jQOZf0kjBQgfzm>M}6{<PdWM_5N*sf2+aDSC9b!`wGi~fv$*~&u8DpPLBE9{55@t=(;pfLZiVl*hCT~!4Gw??f&KB_R?wDUcI_#Ak7-9ROWy$38{k?1zVjTeKZk4nC~pwz7leDaMP428y^i<};|*qPF(VVY1I%<cnCVV1(;P6<jo_GmHm^YM|MXv6D*tpg>D~Uri~LRZV_)kxo12?L*CB9Bzp8A%Xl`u0Xk&4nt=h`J0m{;S!2'

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
