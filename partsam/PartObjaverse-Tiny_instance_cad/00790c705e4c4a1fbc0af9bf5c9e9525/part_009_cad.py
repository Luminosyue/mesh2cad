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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/00790c705e4c4a1fbc0af9bf5c9e9525/part_009.stl', 'relative_path': '00790c705e4c4a1fbc0af9bf5c9e9525/part_009.stl', 'source_sha256': '37c26d77f11a82f2af9721a4f85babd8f6ea3c979c6e259e5c204000c13f9e4c', 'input_faces': 410, 'input_vertices': 258, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15762859582901, -0.20754915475845337, 0.1557007133960724], [-0.15079385042190552, -0.19955094158649445, 0.16115272045135498]]}
GEOMETRY_BASE85 = 'c$}r02XqzXx`rpAgGvb<gh5I|2SEgBgD4^hgf2+g0Rn^?2nj{XP$FRH9TeG8RXTD)5oBnhz`@9|MCIV1A{{~v0>WYM_u1z%XWhHjUH4|Kz21kHk8i&J`~Ug>nH{2AX31L6&`%j-@u16#w-hyuz~?EWppg_id_-LD*o10B;zx%W`GS7nC#3URcWf2iCCo@N-j3`Oo6viB<V$8`gT8emtC*2}hYlYxJZ4DGp~L&c2K;6*gA!sN`w9JH;$t8GIqLZr>Q*spRjgu;Gyji2xgVEcSE+hvU!azWg^mW)zpVbD#sPnN75QDW2Yvf~WYD)FDhGXEWyL%34T8RtRw?NFH!I#ruc$oDD=L0+xuEY3i<Vy$KU<EVZ|te8{MqF@-xUn{R{MrQ->4d;{GBtu3jY1Z!a?8c8mT(pQXXq*RmInlZ%->5^nK6ix^5Btc6Wn$jE=>0-J2DZ$JTXy)f*|#gYv4g)t|w5^Fay4FO+Y8qU+j8)zyb6`Tm*DX}sxeg1-N9ImOpdekXrp_2GnktNFcPerr`J#m_1m^v$OCgTAjt8PyXd-<?-RdEQfgGqQ~8Ut-E1Am1p2zy7@PB<56|Cr#yVc~SkGlSkv4Bj2b|OMNI8t30EKzjR4?c0LpIec6alzM}s8kzeB)QCjikuLXTKqLA`rlv4bhnws~Idn>-pv+^^l%eQ(desc-=ovNwN7ku(d6qlb`Me!?os-6eM)aR+c1+VLWPUEt_z;Av=^{>gH@eaq&`%BQbU&^ZZM@2R7X{XempAGr_<y(t?QvAZd4hH*qFhc(9bj2rSQJs<Uou*B+9vY0&{H7OB{NC@h4$nPOo}TiZ+>LcVI*H12Fu&@#ep2yC4}$T&8S?$d8ff0TC1_l`^2wj~lJ1K<!<1*be7kg->M#3eFpuTtmEXQ@Fy1^qMDdm7``iCr{k(QN7;hvzt@;yAXx&~{AN;5DD8BeH`S!h_@0QN3`8se!_1Df+{S9;Kx^ah8PtjY7Pt2kCc84`z9hJwblU?gS-+tw(c3pn=Y>J;C-&aWajpA9f4ma#o{sPMH{1&b}Et_hcM~&6|ek$L2wwcyd=?S`D;^q4<G?yPWN%2wg?M}+?Yjro6-!4h~XDzjEn<i^s_JpxMTWelMPE($3hU)xrm-^gH<8nTFbTAlS0zX>)x2il0`d0Q-_2KiY^1t{?{u=rI>FR?sQ2xLBzrKR5n@zso-LCmsenb6t9~^vgUW}j0DSn>(P(R(N+7In9#Iru_Hnns=wvcb+XTEZkRX-aN&pLE()YN?uCO@>^%tbY{zwNsp^qq-E)#rNJZ{4->t(~gJY@~hCT!>FUt$y0)-Ld5PoBH5CRn_B%`eroFt2__ysh(%HDSw*Qk8wl38@pTi6H2T8lzX0j8bu1IKgsvJ^VPnH^2f+G+HTdp;jnHS%C}c+(RHh4=zcl$r+n)1?|Dk=$}iuIRvt4vm+s#l@_qFbZ?x1t?29B1`<`{*(!AuAZ?W(B8+!dvJx03vV`bh|Jo}+x>s+(W;`h*gXdTdb>YkKumi}Jr<RRyKCHZ#WO^WXrq5c$*?~dH4{64KuE4zGWn0)7m?mPEprpGrj*@v%Ydh$3ua;wg_iI3l)@lMF@@$EkHt*uY1{vqCYtC8+Ux7&Zj8@eBj<99UP;_EfuN80C&?Oxv;qy5d_UcRr>C#wIn_Idx^+gc|-f28`$>m0Yfm2a1oZ?4jL=Zu!`_u<bB(>iR3KWClltj&2B;mz-VRqM?T^X4%I+>zhomM4!d&&{B37M5?HUnPH|)}fUT|Kb|m@9T74xR-8foxHM|JnFx5M84avmG;kqQ{`{I>CIDH^KSN&?<*+ZKTrL1O34pBw-|Z#Tx6fWp*(F=r`1*S;{J-iWu^KY5w7c=k{^0ra&z*0wN`%U`O10FTI(bcKhHUhD?`51S-#JS);XK-uKLqbzB}No>iJ#qM&@--fBYj@S7)z#>Nk3Et{s=}-?&0`mSBDx;BWV99nQb6zTt<)8#+(zuQF7Bu?{-#PR~@GOEWxqjCxuR#!&gbwB@S5lAf2G{_^c~)#EJUKCMf9-4Ems(0Z_EU(@|n_&u%L&g#GKS^4&`&N??c&egb5uX^&>A8UUwqvadP%Hw>g=Nu=;RZpGv+H2ZRE?kj+XNls6Jye}Z@~z0F8rL@U%@}yali!`E{@d;3+wU(^{)_65g>N41s^_%R3)Ih~OP>7B8|uH=PQKY@k^0bt=Zd!Yg%_xv4DAp0%8RNepZvi25v;S0{LuT0`$e}yPx_(!zL&XwYsj~|F4TIP%Km0wkk5OQIjFn#=ac8P9(XUa^7qhuwUX~EHkWf>=bBwnzT54N`je`7|ABL=|IsYfnN{;;&yerFbzA*;OV9aE4*7PeIlAr$)_;Sus^>zA##NB@`O9zee|=Zi-J<bYUF93oJ87S(He31Uy7IeezWgiZX}v8!t#O6kTU*5`e#JjkXSE)R&$meNk@6khi{0@9H1At~R({^Eoh<{^hsi%FPgpPc6PK#bP2~Hs694NU<@qLE@!PY>FRtfy`{f@r-V?E^=koiiGvTEAHbr&%`e+^cj-;th-n;D!dXI40pHTch)nm?E?D0e20~o{fo??G{OydfDpKv!x<H~hZdG7U<|LHQV!;W9+y5B3_9HaLm>+3IcUsNcpI&Y8Wdx^u!Q-7f9OkK|TzF&D>(0H9c)PHlL{LuS&=sDjx?I=&uP}RTAuj{&d<@3FPxo4c>7wnOLJWlZon3r0+)d#-caGL6U!Jl=9?yufMblrUFzcD6N;~HOHd3M>#vwfTTHoAi6{lZzjRX*><zLOJGXA68ILF+2!1LaTKAfNYZ_qoYBj|$4S257u?gz7iCu2<g{ja2?ge$K~r%ER{nZigwVGjWZ^+hT<Leaz#<l^SnaZSBuP^uA+8$q&7sTG@FITK|FiS!uNT7N!2!>C1K90d>@e-tVXn1Lgb1XuQ^!nqQ~p`>LP!Wiw6r?X8RP$1DEj<(wmn<numm#wovfbD`=<8KrS0Yn|I?=d+*az0a(xcsI{n`5B4I-+jK~@61;Iv3jpGzoGt)vlPE_oW^@j`HdSh<cHo9TfD>mFkSccXRoRc;d=ftGp4Bz72a0-^SZ9JWUBYPzOOzQ3*S*apH9-au5ev9S$TL5wIir=kF9y^WXoTweb4w|g6ib_4ZY9WpN&_ZE^T$)`SP8Q<@>|O>V981OL=yVQ=Qe>CyNpvKT6|GNmf5+=zMqn8tFMVjY?XF)&%)hdB%Hi3ePzsJ^gWfdcJa(CVBQBUjy>wlJ9RcQNF3?9MhNR*@w-=x{rLR!#(T7%E`R+l5d6X_dLq)78>TcUz{skw?MqEyZ>GF^P$ciBjlH)Kby1<SY3yB=EZzT-y1k*1}mQZ&?%vKe=mId9o17RMfo2L(t6-ru-9on@okQi&-%1SbH5Lc^XxOuSmMj{S3QX_>ccVZV{Xp=p8MLWt$KVTV?Fchw>9tnlChqB*cqYy(@O0le@}|m?Lx+zBH#a^_F?-)_S@|~&pLNnQs*e2cYli+uXPgE)3ZMq=kfjBJo6H&-|U0GLwzt_8%rPXM-0}yw3qMCE8o65$1`60aA)=N*i_|D(fQ&okZ)Jj{bFn!qxp*Hq&k1sxcuR7%Rkj#>+1S!UALp^_ivSN-_UsN89GnxtF1L(r)DTmP0rIp@~uN!S5B<XYr9S>&DSB->6`M{kM{hwqe`zFO?E~+zM~(1av24UzA;bysv}?qenR@+|EeRd_W$Zv9kpxL`2YT@<Lu)a{(Stoj{XH-hwq?|;5+a=G%QSf4}O3eaNrZ*`{+YM9QXt{6TJ&(!Z*+>@D2D6^q=q_a60-8oDQErzkpA`2hq>qgYa&2E4&-tf_?;Vf!Cq$!|UK>=-cozcr@A-9u0RvTfkl5*U(n*YjAV)Ex0+{0UZK&fcvBG!2RLz=sb8loPxdwr@-^k58(OmQgj6z(B<$_crLmKo(oUs6X03sLU<ND6P*Lkgr}kJ!qZ?I9Shs=K(seJ5N?Y$gxkXP(dXg%a1FEyTm!CzJ_lEV%b*3}GH@X@2V4lwjfTOw;Vh^DXMw}ftZ+D-3oQ)if{UZ&;Noxv^d-0gTo0WM*Mp~`AH!4OwdmjAweU97fw#eX(XZgW@L}{@_%Qr6`ZN4B{5_ulUqG+J0lfoXfUlwV;A`+r^Z|SmzK!08Z^O6HO!yX@f!=^K;EU)V@J09(nhu|Wze7*J-@!-GgYZ#!Ke`*<5AQ^`z&qhh=sI{4yartcuYs4Kqv0j+D6|Va3VsuP4So}DhBk+r!LOhl;8)-_Xn(j39D|OBW8io+1&)U&qx0d(@C<Y*9MHM&3^*B`4kyEjd;&ZHodr*Tr=T<8Dexq88axRehuZKscrZE;9t?Lw+rr&o3#|`ZaBZ{(TpO;AR)VX;k!Tq>5;oC7un8AIbHhd8r_e0$Q*bsk9L@%3M{~j1;b+j|@H21;v;tfLjza6fQSgiCRQN@BBDxly2(Lo7!K>iS=w5g;ybC=H?}87YU&9CBW9awrG592(0K4b~IH1>H7e0sHgwMg3(A)4O_$qn}z6xJPGvLecdGsQD9zKJfg3rJ|px?niz-j1FI1T<1-4A~We~#{iKZjG%O>io_5nTgsgjb_W;MMSAbQHW89*MpQkAyp+&EQV(tLQ86t8f#v4cr8N9gTrshdZP3aA&w5IvMT<C!sUofF{F9@BlOs9sv9J1UL?z0LQ^Y(JAmyI02mmC&0teaqw_>5IPth1ouL_!M)%&Pz!zoZh+Q?8^E>D>ToT%8X5^#gUh2PTplis7J*B{MbW3=qHsPm8=Mc$iDrj$!g<hV;5={vv;<rLE{R6LCE<$bi*QA_4muI81CK#h!DHYL(arFO@CI}jyaC>U9)Nei`_N<XKKKZF5<UX|olk&&L|r(b=indV)95AmH2f=i75)|e9lZ?y4*!Ophkt{ALC?Uyz(1isz(2wNK-1uVz{k-q;p6Zj^mF(Sya!E%_rTlHjqrAOJ-QlR53fWQ!z<wh=ty`0JOb?mkAOR(ufiSSrf3tmDcl%+9c~Q2jCO`!hFhck;MQ<YGzkvq0JtaI4)ww9;Ff#>+#ZdC+rvH3p>Pkl51Ih?f%~Gv;l6MzItY%1yQ96}?r=2v1{@7HLL0!1;JRonxGr21tp?YGtD@!Ms&HAfG+Y)gg%*WN!Nt&ga4|SPniI|sKaJ*rpN8|I1>n4J1X>b~fS*Mx!q38$(K>Kt_yu$f`~o}-{SY1o`_T=sAN~a00e=F2itdA>TZV-f%<@0|7w7-_v4bz`PyUDJ|NNKUuM402mscO>`uCTI(JiwD&WFbj!QsI{oC$o(VEhYYV=Su'

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
