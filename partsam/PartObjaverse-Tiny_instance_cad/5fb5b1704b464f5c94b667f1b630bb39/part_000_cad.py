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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5fb5b1704b464f5c94b667f1b630bb39/part_000.stl', 'relative_path': '5fb5b1704b464f5c94b667f1b630bb39/part_000.stl', 'source_sha256': '31001a4b47046ed273a9ed937c19fc14cf4dc8c78b2ea0870ee2b64fd3a6ca10', 'input_faces': 284, 'input_vertices': 300, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.008945394307374954, -0.45198261737823486, -0.22479009628295898], [0.26526445150375366, -0.3017512559890747, 0.2252446562051773]]}
GEOMETRY_BASE85 = 'c$}r033v|Y+Q;WjYA=UUN-RUkYmFs#IZUY~_T^M-t2anWRS;`z9h_QXjWj|CL+NQHYAq=uuQt?nNF!n^eS50as^wU!y3jNCbN?r2p6Pto^<CeW>-t~!@BQV;J<rTMvqbdm5&TRAg}-Vl-pe~H8C4a9@~l!pnHn88dCbV@Nnx=Q;yp@P;pxk&Nxfg`)pw9bnX1h6j*6Z%GS1sp^+v?B_BK?#G2`PV$3?{sA0Ia=ntYe2w<blKe$wcu3DM@~y5UWlG*rXuHB@J-|HrSA<`nct{pNKrtG4aw<!qYMt)r*2UA)nG@F_R1*SU1EgIk||xu@-3x%$A>8!N7J|FnO~esLS&wXr*-`55PGbDzu%$t$y7boJ`7i<d<Ip!cQzdc*UsKG1ul@Y<MosgG~;2;l?srpw1C>&uJu+3#5*?{CG=gg5r~m*=^8r|?QhA6IWQ?=5+KSQFs`%?3#QwQY@fe9!*!c3Zi7|BCY5=erhCf6F`1ujQTR*YeuhKHUGeulYFlI&nc7@9<jBNHJb{T5rDSv+OF5-xDV0qZP#b-EAHECmND3TqhSlaviUizAU`Hb29gjsq5;k{neICSSaRs{w4NnL&bQ-zfO36%?^_HFUu5O`>mbqA0A^L)mS<XPOt8c;Q6Pji^aOST~&DBw{3;@x85wg+Nh%BwGzb=#P{2j6JGhF4f`oug%9Kf@%YNM_;@<JwZF>X?#sl_wZ2|ppQqCYc7==nflVD&itpzf7ha92A^JOgVgEAMgjeh4@OkmpJ8Jj(ijo)YUhgs`QEYc*rZgX?_w@)9^YML?C%o}Z+y#3dH8def%%|m6o=;Epw5zwy`|?A=>q*Z^eT+A%C5!F$StrfsPkvW@K94QhvOjvOK-w>O<;zrQyf*$P9^WygKssLzUwA!U@U9kp)~}KJ__pN>@84e_Z};0hDZ;;*D|u~CuJBq=vhe=vb$LGU{*ZThyQgdOdcJ#Zjqq0z`MmF`!}Gi!vetgxsbA#tx_vm()%#Ya39sKgCC}&Qbm5hGD+}z`(Vx6^z8u~<FHY}k8p`*Xq;GjXKe1PIFJIRuny1?5scg(<-=veP55z8CXZQM>XGMP_B7L3xIIG1z$Pqs7SK*cF=cN7hU7fsM9ET~%(megs64u+#qtz#{drX>rJy`qe^j04=WWDgp(QoAA{7JP9_VsD?*AKk3!M>jTl^gJV(&7Jm-?+j4ttV1{<@fxJ_Uo(ge&X<fN?yKRZfJ(^?OI6JUEuaZ!+yOR;o+xUy)~bK-c91T4a$-40|}b&&ijw$1EY&c_aA>kf8q6EpGnu3>R%zeb$_$=%jp9t4R}5LI&`y`C+?rxjrL;xPH)XW5MJ~>F(2HY3(v2^`_?q)b<!e2cz=9(exA<l!Pm=}PVBopFZn=FSK+Pah~@R*LEQgXWyu?PYlYYI8%xifz_~0QU!k4!{Ib0DTnnUj=j}SYwZF!=BRtQqBcwjQ&9~UkjAZ|Id*0vD@ms`vtmnA(Jau^WkB)pFD|<wE|JEJ69z0$7KGx~D@XDawl2^)|+ag`>)_ddh2f`P=&)n$h>I?5n&;2a*F{*yV_n$!dt-`M_!|zKm{doPC57}xTuYZxw{T;sW{_h-bJs+Lpv0cj>wWEahrR7LoY0{ee+&n3H|DjfV9QG$l^U)()xsEqxwP2sNN}hjRpLkDJ_Dz+%`oR$4^|MoCU#BR)SFcNv`UiFu5#IOlYFF<ZZ^TdI_th%n<>NeHGGFg!x=Gtr&W(5Vh3~!Ad3Si{dHK_Ovcp^N?Z(q1CxlO!&+Dpd?5b=RZ{*DFX7_6J$$Yo*`l)02ZsWB>^M&_&Kkg&>F3p4ww2w=a`lLNPC&s5%iIK*S$rIkUqQ(llS2|{~uQ6?+-3PoG!Urxszf{_<)c4qjY?&(cud<r`-M}JgKKd%*m8|-+C9kbK$Jb%4g;F2?65+LkVe_e~2T$<(nmXu;@H5J+aq~)W@3-w<`=#KL+j#5uMCW+@iygwNd8Kr_51gIH>%2qb6lwfAzApT=`bhKC_x9rP$zzhGc`kd2e?OhreStL3WvzKWS;gO#`ouKk>m_p4D!cceuFLy1<w&B`e`zRRM^A%RitPtKJS)zxewgp)p;c4eyjme=W(S+s?&syZjkmmWyua3BUe9e8&aiu>d~;sUAs5%!`}jY*!|SA5)&%=_y~U?kx4$Gy<FVd+k1h?A#)mEv-q4FAN&6Kuo!8q&??AiP*No!z_ISz)ssFCQ+$XK{WU0>!ukw6OZ%>f=T<^o<Uuh=JyOPr~*KNCMt5(AMzgy0I7B&j$VDn0qWjsEv_~pYkuZJ(?@nwsb75lvneH`=DrnSj+J3f|o&NGnPmi@f}+<#}XxbC$5?Q&iBw|)eVFEy0=d^khg2mER9j^pXS+CJCqy!dZ+%ym1z%IlqS-PVJ#|7D)f%4<A+)ArTk`}I3>pWyF#e8dgO`&)h|yjmh4yjHG@@LFOJug}{R<3!)|Na2lZ<#?SBd%`}m7mt5jme=|Ad*XW6rvEM1Z9Qw519?8l(}Y)=yb&+X?>nz?pWojR-e>fh!F|~~ua`pquLV4Q?3=<H=|gzCVXq3WRae)F<MHD#;nh=FyxsJ1d_86k&vm;_17k<9e{fsAe)Hbo?M5bZpF^9tf9KJ>-6tuM*D}Vje|_|MdmqdH>Aq1TmgjjXvOt>8@OU1-ZRmOXc&+>_?q5Nb?@J5V2h`e<_rEopkAJt@Uy6C3XlG=*`MbM2+Q%zlL6_ae7kbBd{m1=$UtO@Ksoh)uuBa{w-zaVOk7|71j_^j=y*BY4zgOh<S}*yLdF;oePO^LT?mpqw+rG6@|FD1XzfYdIJV%;;R1*8q6<15+Z!hNemJhQQNIvim_gB-Cr1_|CbDyvu#C5F%Fn&&>0_pr7o5S0EzlY?N{C9c$hyl`bN2`#+$E|yU{5&eQp8GtTA$c__jlJXfWpv#jdA(~faXl(w8zpbu2b^9ReP7&vv`vojSXWByCdnJ2#p1GEynZK1ye}z>K6G6Vdh9mW^`;z8=j$%3zpK|S^mFyb?7psE|7&kouUzORd97Urud6Ks<n>>3yX*SY5AJkdS7E!@ul}5W4?5B`)$aX^4)A+*&82JY-npIwn|8Uc!`MCSeRFxcn_DN^y>?sY@tgj=((e65*#}ytO5VAieaH8@UKdKOeLOxgOu7$P-g$q}lJ~jZAN1n;c|MPpvmbi4m8f_2yI#NQh)nMP+HZV3Q@W0|dwu41{=H^tSMmO=ozHZ=Z&=>gag6s1@8_0RcI@Tj78o{D{9LzBg!lc<f7j5m#!VCRI{1m}eN1V5fcGn|y5zN4C-5A9BCRWR=Ox~5?p^7)`Ch!tKJA|5)hAzZpRl=Cr1f0sd%nJmlhXZMOJJ|xzbTDZQ*OE5|CLd9xKGNND^i~e?EP~tN?w_GU+NR+Ja2Bco1Y#nym9h@yxm8ci$yK@Nb>sQQvCiiNA|wsJ%#sof9(2PQx3CNW*m0)>bL{)bFk8{QXfqpvLU;#^w-VA{@EG1rOh*Bri4;KiHWlPX_KTleW>n#+8opTfAy!$X04n5fB&@k4|5LN%xpz{A53)%cq{ll)Xm`cz=oNPW;U4Fgld2dj3NHFnY(80nR#I5zL|8?d*FK*la6`^O!Z4J)yv>?@OCqg%{(%b0iS{GJODpLh<`$T1pWn|e>QW;%oQ^QW<D}=9^X3;mw|c(O!X?5>NRi%n0g*EbI{Bl^r61_s5`*<;4cv3JcKwGAwG)`pGJsJq3!~o0)LLW2mCoW8}*=#KQ@zv5FbF@4?X}sjQR=qFxZcp3HF1JAjF@d?gM`c{tO|`LEQ_^0Ut%(4L%A!hPo4c4163RK8X;YK#2c|5T8Na4n6}uhY(*th%X|<v=&#ISz%@sY9e?QI0^M#a1uBfbu~B{oML7z>N<ot4Rtk`>Kbqwcs)X#YG#?4S!R|a#ETH(1qks%g!mnVcrHTxHbOiHA)aj}*bMy-jv&;IV5*(KRC|J{P6r2pXQ9ppKWC<*neqs6B{Ot8rT?c<4r9vUd*$FOA|=tAY6&paB4Db|fS<uW1mS02z_u!ZE2F*$t_-e?5Z6J7LlI&xYJIR5+yJ!+xB<8+YD;iaa4Uqk4MH4&5O+ZB3hn^zh7k8b?Fa4y?vMH!xIcIhY7}@7*oP30K#c~E0LP$C1jm5KBE)YY#N!d-2?%i<>N0Q~INny{T|N`j+V5rNZ)W<M@t7%#5SLQuzb0|Yz<I!b!T0HNafG-SLR=Ifrmq=hrkI(D+5<cj>_P1grdkb5H3S@je#Cz_v((IDGYQ}&sPoaA>O3%29js$c#BZ7zXJ!;a9E&;$91EU?IvKnabqPW|6?HP0dXB+%M&t7v2=PeNq2Q6=A*chvL%^>f#F407z>(n22=Pk@v4#-0MQsPB+8o>#9FE!u91d=XS`XY1To<(lxGuOBLR=FeRuSUrsLz9|gR3CK^qTp)nJ_cMQ5%DYgNLCu0}lfaMr{Ee41U$j0My<H@yn<!z*Jj<Uk0~Fi2rKliJ7NnzC!&2{59%t2r(_<uP}!AcX*G<)yz~eQv=ll_TXn~;4^W34~Mv(heKS~tPMO|y{P29_)Hv%8URy>>v%ZCFM2q{wLKhS)vRUAls5A(g;N^eqZ$IHS`|#SCYWk1FxBc{sw$XzexvYqD8zq3{T56iF6-eCSN8C6{uRgmYw&f{AP@6(@OKJ__<Pi6z*LKXsrL;tFL*e_&v`h+6;OWwQ;47UaEL2;IK&k_9OCjG4skiuAHfvjXHjp1Da55b9O9B54si+8TVM)taSw;M80t+hg*X`XdvGw0K~YpXCd40_Out8cV5V;mPf&&6|LMQF{`X544+i^xe0Bb${A;BBC$E{k3V*5W+oK3QXUvzBAn`E#f!-dJ{{T&&Q~U'

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
