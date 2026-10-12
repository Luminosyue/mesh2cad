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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/13cc3ffc69964894a2bc94154aed687f/part_004.stl', 'relative_path': '13cc3ffc69964894a2bc94154aed687f/part_004.stl', 'source_sha256': '5bea0204a58724bff63769c8d2a205491fe755d0d2644bac84d0935aadbc35c8', 'input_faces': 248, 'input_vertices': 180, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1961110681295395, -0.005533069372177124, -0.4522181451320648], [0.18673676252365112, 0.1607653945684433, 0.4774329662322998]]}
GEOMETRY_BASE85 = 'c$}qK2~-qk5^hui;)UmW+b9Vd5fn)z9@t_~QB*weK!F)`5Ta4RI{|G^M8zX`;n^ypAQ3!KfjFpuF&=mjQBWslSEH-BH8C-|{a1Z%ruXf>w{I6;z3;29YpUz7|LC4EWI)ww4J7_^lZHq$)|l!_lCYXm18J5eZbr;_%XF_P)8;xzuB3~<*O)RWbYRG62Wgh{vBw0<^zm^XU1g8%QGOntvPaa^xEXQgDUnm-CRl{t$2@tuMc1cCo2OZHzilVKj-GPocAj#A{6GG==q1?RZu<Et9o3qZ`+MprKR8z|e5rXY)-5G_g>D_!@TTyUmp`7P>vQt6g>D)<mEx5*%UCa(w^itBxWg^s%h?yt+2^-CE#r92dd`qPwl(Ef7p5EXOJNBVZ%a#Ky+PV4iVwR>`L&E?hWnZ(*Ct&#Fqw3vm-`{AC)k1S+isL0j~4To;-%1*hIpla9g0`4z9^yV-At@Ek2+5Nq3>9~&|(4A(>ATbpy!k<q5PQ^($&asNmtrz<a*90=2P4^cQ}5-)lJm@bA!14b!8>?ebe$f^LU*~IX=(jFpc-|n$yC!?kz5{@2AOmBE{SM3;4c111Vm1Z(Bs4znDk5HDfjBiT|E_Q(i9T&)T<=;_JSmJgVa{&NI&U2+iZL{THa7i3dsy^L6Z7p2vHstY=r>Lh&meaXr;G@qHgRqdZ#fyc^_?Sju|So1{zTz85Jz-NJcZuAqKO^-R=HZDv@BVZPREqx)+6gN*r$S5SU=aC_D}-abnG4~@(>=#73O-Bjm%F4ezN=KHqTw~_L<eo6J4Zq(sEzwu56<%t-_>)h<j@kJ-osc&yB;B|GY3g?gQd5rpSFrMbiW_esp*MCgVDF2jFp5LHHq+1hv=TiQR><b+KfOI7ylk#ZGQ)#{0=AY;Iq;QV+Prpp{%qwI)K9Az%;ZD>C+pk&0_WiNeY|4Er*~#@dA2w0`*4~u{J<C0g;*Wku{a32YG~~AqX-N6izlL%A`!2I7kJ}}VPYYoEc~C0FCubS;`Yow%wnqs@-J|RP%}Y05quzBsujiTR)Hmz&Zrq>poD<Z~W7}ySwb{*3&v!dW|2eS2URSpq-9z{NwVgqid|qTyKRf@y`J-#I{-}I0jVr&X!l2&`*+6yvvWe>)=EC(H)=rY1e2C^zo$ADW3&<i}-8_ib`CbQ(|00HTZCPO{`SGuc?E7rnxSP%;t?e_?mFF=uUeg&r?*HzK9Pc=f^928rN9)%65XYB0=FvX#%cu2Y&B`$5xf)1$v~rE}Osq@s@_sK`x26a2e180rNavMw{3|~9e*chl^F8XPeD@5WdoBYxPuw^86rZ~I3dKzf=J;1@X@0E{DV*op+gwjlb&A(~KHzcr*Jr&-&}WqY>to!{p}(EAuU~0=ozMA^ch1`9Q991ybHMoo>5?>*o)=24%JaB4i{sy&aEj*TY?rGv-WR)Bzps(54BbI}(}tvS9;MzW(pNU4{bD<wLb~b`PUp6=x(AQz&PvX6emCdu@D-mk7Z$VrLotm@*_KOnDqH4q{`>V08urm^eWV|)f2Da6>86#FS^qUKhQ{N&y3(M_Tl-Pn$3jR~6Cz2s1|8vk_RZ(}dWVy4n-^)N`|dY$9}32hE=MJiE?p0$b*tVS#d=Q{j$c3jw7qWnIg#T_PSAWwYeV?HT~6^iW<JXMt1Ou74Euc{_2*urN`u~R?K;Xc#+Cc*+K2Ome@*?Aylk}2ts#D_-%LJE<LXxRmO&5gPU~6o4X1NY>eGbl-*biPRIUfnc-202IKJGI@+f~)a(qlJuE$o7o(s0)0hI>*QBOXv5^8gupH}DfP`84fQ?|Sb752K~dYAX<-?~tKQ>hcjk2#q`_2*<(*z49G%-pwnYxsHUQgMdz^oTB?{14jkds<u>>9!_UFkeozFRZhRNS9lO7E+!LS7<-VZE{Gr241H9BA>6r&xMb-kuI46={asXd9A`;S5-HDZ+x20>$CqStZ(l@?*sC?GW9`r`H1T**hF=jmPK)$zfWep%~e{5QkTJa&x|Hr>z%@NX20a;-REYGuknKGOzzL~A`RjDb}gp<D?Og^`BT`H`|!NQY0}&EqjOb0`4hi4oj6F(O(i~_-@EqTCtaD<h~`~gx`&_3{Ypuf)UvMhxo6Rp2EAnzty}rbB%{8g3$0sgHw&+mNtZZ(k`v{Z9_I1-3_MG^CQYU~wQn=|J;7W^C?8lwx~cR_djGVVj_`T>)*X(|9Yy<5E8W7M3#@X6^vrzTchxr-^ZfJ$?H8?r-yhW*gLvI$dGNYTOk_Rb1g%@^$O2xse&bl5;dg-7Z493$r^9%>@3rJ}$?GAXtGB#aFVC1o^}7F1Y0yU%(0Qe#A2RCBhxxsF(GjB_lS$86Ys)Nyu5KPq&mHxNW{l6S!Rz7c*#_O3(3IaF7XHX}w({io)4y$|apC>vwXVkIq|toY+>LtP&-|V+#evs(ax0#fdl}S!YvWC{Ze?{*A?fD6XQ`gXi6`uJ*>yJQCbtP(N9t(OZBJ8JZxccDrI>E<^V@2BpW=G2x<lg_a*6hpG$@4Lla;b3x9R>5>hbw_?%8-6*Q?ePuioj;`ti$V8qc+{q??wU;Pc|MBm8}&qEjX1+4GF{p)_*DPQodLw<ym@pVRhvY{Ls~8}v`*wNy{;F3MxO>3)Xmk6T3d3w^@+y0)yVr|CV-)bKjx*ET$2J?Bms<(>JQ;#Kol>WftVkmtQ-jhhsIY8C4tysp%(6%=o}y^r;;_}sQWtW`mE?Q2>@y6@=S<j?I-c}#sQtXBrd()_HBq&)KUm8`eDmQ4QTK9tA$!JEaTOCzRIA8K79-Bh(b>&??<65d}<x)jxm_2{I16gOb)4a)cTP}Wbbr#{Hd=Tbeg^?TMYxl#R6Ocv?Z)=nif{^d*Q{aMr6Qy$yiW~A$1jQpt&Pu5UBrP2u2mlo6aJ8Q4=lt)@Ij`iynTIX7|YhRMzYBB3-^f1aBQ;YK03J>vpL!a{Z7jI{-Kj9e1m-kB{Oe|vE?<DI^r4+B$n#B4~1+05_r}3&q&A9#*XIS@(oJ)9d7}cr%ai4XsS<9$zk%!9-`mlG_Q$3mP<vl|Tzs_t<+H*m!sozq!>QVzK%53-3j1a}&Yy9^=&BXZrS3k}8`1<|7Kg~?gYY5YAB1~{IEJ8O6v<N#b61oL^5-=LPwQg;6s|ypnK1}d8b!!4&@J_mQ)a_lE;O~g3(#;pVBYeSKb#taxGd2Nt1NQ@Zg9{7*_X8gb90x8i5nSM0@Ic+h>oy1`_=mbB>6Q#W9{z{;tjM(jCirAv0Jy;Z;No-3kSiH{B`^^@5xG`kT+Zm7Ku5dYI@<NTnr@AuRkPFHfZiCq1+WHq3-GsLg16MIJAA=Az!$t9xX={%f(J>wCKO;l@M!qrdJOzf-KK%Zz>h}EV%>)6wge{laA14z;ozRYTHv1GwPAw00G+^Hz@33r!JWY!fezq~;MHJ)OXy)W@G9^n^zRL5)!_@?6#c6XtO4EuzPR2FzTm2E({)<_i~<)p0ek`YOyETDIN<9&E4Udr5quKj#Pu$^dFj?1DExuIG2jEiX9LAGKkzxw=fEEe8zcR>2fHA@8+^fC;WvW0L7$6UBF9p2p(Vl>d<pcWcJ~&VSkFEZuXi8#VjXvfFL(sF(E7m_JQ7@JVTcj_P;jAj0vB2!e8Gpn7krAuXT%U-Ab1jdaeWc|g}N;VUj#o1F(2WY&}YFHyf^ME@^%ClS^#{(y}<+QdLiQK!taE9BJVWdRPbrwVo%0_&jii_pJaDE8rR}52g5NZv%v=fJ*7X_lHgvz+TdQ`&0&Izb>Rwh0oDe0#x=pkz7hLJ0rmh_z=ME&z=Oa;fg#|b;No1Gq1y+#B>+v}3E(4vBftd?02lZ^_(<@sz;56I+k$rmZ>F1g&*-IFFmM!jFnBCX@Q-zy4-5y60uKlG2lfK@2X6%v+#T2x+#TElCir{6VDR_A`vPOZ`+|?wZ60tHFcv%(wXT8*zQ%4mYhZ$})onE}9ylL79(*t`9DFc%XP`g0KgQe{Cb%q#|5jtH18fD}3caWU6TBWw@CGo!8v;GR{{nmq=mGA5-U+@#w^ZFW1BJf@T;K+~YwKWwr@&GXvjOoNVS;aiX}ax!rrBxYUg^+xK+~Y@fwl{NI{032f%_1b4!#e1HY`)O!_YFJ9R@!H6Z{}d@GO|%8Nf8~4Dj91_re#pRkxksyWsDJzZ0>$?0j*3J52CRz|G*B(ChWk)<Ihj{s}Mzd@J&A2JQeCW6sg-Q=sq<pjX+@_rn)FWPn4J237ylfBpXXr_zgv{eJ}i>nDw0OYA?nUC;H;FDW4d9O>PqivCY*%ID&VDg6V+fbDz'

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
