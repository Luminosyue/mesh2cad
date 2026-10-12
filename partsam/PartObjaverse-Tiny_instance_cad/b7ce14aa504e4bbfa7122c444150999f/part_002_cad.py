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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7ce14aa504e4bbfa7122c444150999f/part_002.stl', 'relative_path': 'b7ce14aa504e4bbfa7122c444150999f/part_002.stl', 'source_sha256': '94512b60a5903c022e5be7d39e70c49dbe56b87f0176b50503b4228d7d89eb6b', 'input_faces': 446, 'input_vertices': 402, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11971638351678848, -0.08391337096691132, -0.30743464827537537], [0.08065281063318253, 0.3033706545829773, 0.020769886672496796]]}
GEOMETRY_BASE85 = 'c$}r12Xs_b*M{#<r70y45eO5MCPg|VC=7-kgg`(#3?<C~K@t)=L!?ANiXcdnQF;-90DgkX1reo_i70~j1r!kYtRMkI{q{ZkJ>xwm_h0K@|Bvfk``yoZ&%SLkAw!IbE?gwU;6LF;f_u!~MzsvXQfVW^NRJzrmNX(Rwc(ht6J17G!L2{CF6rLqg_!;>Bi)!>dt_Ydh;g+e-L;>MZ&ka#yLNoaxU_M@#tcmvH!{xR9fyrdjU%3#IBaYj^>vyxYEs|bv~GR(RQLb!Pf0oj|A7r3AGFS;Ny=WU`hK03d(er078S6nXWlZweUq9i`2rkycldb0&3==Wyv~ie?M2@FC64DTZ=>YRb)`NMxxK@8h~uq~cjV@?^~D^2>cbBO@A&h(_Iv?8sUBZfiHpn&O;+aXT+VlYeS*2qrQ{26%s1A4z`V+iZQ{C456yMrMnX-#4`a46-yW&tbuROH4`wk>Jj#5rH`kFP??0X{xbJ>1WxmdX`4@XJ-@b3NIFEb%a-FzmahS;aYDMvJ+e9h(0{nC}zMmh4Gr#t^lGnMMZ_F>x$Ia-Y<O^`j_da^-fLK4Va)aO(d*nLuv2}R<w-*KX4XiD=w=(B-F7tV*`+3ge*~)yK8%^u-{fXMfb2hhC=IdO}_n(=~b80MpN7Q0navk}qaK7HP8O*b*32sJp&UNB4@2eNfJY|bAzW_(x^G6hOqlGeG=fU%tQ=Pf*=3Amxdp6gJd(tZM>!EL1=I<0%@;cAk6~g)NZtWNRi7IQAyvF7Hyxre0Z_`YfuX8!yA9sX#CHD$(z2_owow(7U0^gtJdznW@ylKztT;|;;mN1{&UYW0RnKxI?Wd22xGGFI1pXVLN{6g=gqED!o>%={q%klL#8o~UjNlWZ`oy)xW$w1~eGq$$1&U^d3Qwk4Tz1_~eN82$^o28tO&gFb#Srg{V-crs-=Q8iU7|#68ur1bc%?qKY6dtnsT|4*xcKrkU`TI(&KdEq>zvRaF*!M+^U${!}q5lauaZj}eIpVsycVZs)(rSBN=f=SMBJaCUgZcVi%6y&6`JSy6m}f>P^K~xgdn;etC-@uR`Nf=W*8)!5D0xTZjT>JwFWUEQdtT@MPPauqZ`xkwolhw9buQ=ox^HB@zLhdx=W@P3e=hTVhu2x$yY*tgiF*=n@b!K+nR)p}>+N}+n;U-M^NH=t{KfUke4Wero+mpqKN70U*SVZ;tggn~U1F1%Gve!j6ZZ|dCh}(Tqs*tID|wv<^Z7UU?^OqHZdCFbmw9*2CFTu>DD!nL^G4Tf=B-<buNR~0R{<yP4gH><SLOB0w{GRHul`>KoVd*U-pgeEbC@z;=Q8h}p2|FWzA|6u!TGLk%)?^E`+%q8*?<%Gx4Xp8H|JUAuN~$0jaSYDoVd)p6RI%JiB#t6T;|OdrJ2{?tjyQB%==H?+#}AndgYzsy4HUhaN_3L06(vd-!ebdLvZ8Dk$@AId3Tfjd-y(=Q0D7g=1tc&=4(94e4Wd@Z~3cy+`Q$x#C7f38*t)As|$Sp6DIMT1*Zk~{JbaN#AV)lyASi7S;~B!%e;BA3m-S(urgog!Tk7!Jg4RFyT$A6g{=W6?p}6=ueU>W=2z=w+w(d%b5Ha9oCn!rz1TH%zQ*NzW7|*6_f%Ep>s-$FEy>;`)_acrP|S&*5pd$Z=DYZOMr~qVVw2!zmM`GMWj^m-rr^HtAxd87GVckbGe5sv$?II^z3sa2ag&OFEO@(V0VnSHX$QZa%SG}WcRMAobE7`z^EN)tyw$yr?0KEb`Tq10%ztUD%-6Y`@2&gmPQkYiIVk3sNdYG=uh+PLnfZV>1ULUo3^;Lj>P|lY1*YJ}lpe}_oy)v$$S&qj&sOH^T;`1`s|7bN^fU#pGd$qLeQUPx{kb`xdE?PaUgt9J^Ck0fKklsLbuRPnm_a;eMVyk?xy<JkYR~sA{|~`E>%0L+{^BM+|3EY5-9rzF`;#{`;KXI#98#9~&^x9*uXC9<S`}fw?=fY*&Sl<r?yL92*N4k5xG`u*z=?ZvHt^S1)<Nd|4hZgFF*xAFjmJ3e^QXVZUq^4M^EEE#(*WjXwlZJma=!cZaKX*U*u&zv?2HLGapSjDeE%C4X1;iglGnM+=XKdHK7TR7x+-~{2j@S0oB8-Sb-u=B-q$*gd2-=TME?730VkeU^G$v|T<FOBaF~+Uxy*Zu72(gD0)HH~=XD;Ozu~I*Jj<*bs?OKA%=?l{3hrwjI4xdR{-$RY{$+(TcJ3Ma#ddL?al1s`SQo1DVz(W+Z&R}~cJ5udY`guq{^<NO3deCJ_eAgBBIehf_L<<Z)dNo4jGe}>!@pJtZcbkzc<}Qgjmx~JQcvcK($)DI56(Z<iuv$G>U@m{^L;`D_m!&jx%hf1&7Vi<+&D9ZpJVZd;&UtCrDv49&i$o1Z@9DhbFQCCtMfG;oF7=pyh9yzzQ*Nz&tHA{bGPHi1ve{~2{>{8fpng~CW3kRH6^cenfDyKyGhh{52^Dt9-N<eUT~wxC3U{WJ@?1+*Y&1V;M0zYuZuv*fFn;!<MV0cW1fFZ{Jd|btPD7DU)S+x6+ZRU4#zyW%p0AiG9S1?IUk)HyHok=bX=t1W^%fcFTipBM)|5dr_CasQx@}ej`_yOs~bfPuX9|Se}#NUZd^;@`(Npl;ATdY;GUj$9l6XK&&*_=<yPlwJUIVyGV=kE>U@m{=Rc?+xbNXr!F?z1ICAr?(foW@6cOAL>pCIk;PVHa%e?XFA@Mn^=ilEPx94>poIi3M^A`7%yv~F9b@77xb}i@QK7G@Xdk&7^*Yoq8nLm=P<aKWRIh^N=Daw550(HK|gY(N=UoZHrE$V!Y%lYoqeaw%vIcah4ch?=cF<}_Lp3A?<yvhJ2uXC9<+Vo+*skxHZd2s%v7R>*OQRizsIKNaW{+zm7g!sPWYj@R=n-iW^`Q&-ddGKI9Y^-0@(1!edaA#=1kypt-tMHx6ob!?+?<-Vpt<(AIT%J#mYv-?XnfK1>x>#_$?|BQoo9o2=DW9HJINtXP<iQK%<$V~pIpD-SofFO~T;2yg4=(fWGx@W`>-}iAfZ(w+a-6vT?gZusrpy%gV?n%{*LX0$GirvI^L~_?*SO4k|DNQts(B|y$?II^&8xKpH-`L{Bkt#cOh@jyh40su-kC1eH{Vk7I+uB4!Yt;`-&XQE56=JM+i7CG$B%*=|H^dcHK+3H>hRZsdyF5I`8t>LeY5>M$9q}LYh32dCg-P$^;Q?u`=fC^Z*;ign3p_wy`Egb%{o`q>(x1~*PL3P`NE6pe2oY1|NRLW;yf!R<%+MzUDubkb>i9W-w<`f&UCS_#4sgafXjUGrGlHIUQ+WqN8YpN#CX92!<Bpij=a&jzu=y7z18#AIr8T9MQMV+9<AgHaCtsm(gZgX`>5xmb9p}f7N&~(cB7kmK025AYR|tU?wkJpukqmfx#ar$zs7@k^H7pF?njB@>)Mz*iC@ouv`iG&+j|th4?MxIALEDj<HdRdcfkI7E5Px3Gg|Ht+>@22&H*>7Pf(6)tU2Kob9NV1=j&X~zcP4$sQULWoy+fElI!2UbT0Fr%@N}KH%F@HqjPyajmCP!eGdy&^E#LLdnX6Bb$Y%U4?Zu+_2;YcV1C)y5#ql4+o|WHb9p|O2PN_IsH5g}F7uvK$>Mk|@xG1k7dn^UFN~AR#)$o&<g0m&2lE|jWQaMxN2uqcbNPP0^~)^LYd;_9T>iWh<l4_iIuHIlRsA{s_e*>}V1z8pQ8+#yklbjsh5ua>pG%mPQWY*ge~{daskp{I-&eV>$}wMZ|M|vy#C-g_aGsg1a{Rln<nBYs%<=Eep7Rq`j(>NS+`namGT;AmTa{zJ;4#W?o9#H3F+H)OVOT0*gc$L|Y`<z|LF<pK&cAAw)a-xvt7gqw{C|JdtQeg`AyQ#d5mHfHhE-kgrATEA>sRNvJ_`Q`$@*Qj;;1Fy%b<T0z6APG*jL=P-|`hm*6j#Etps0|RG#!0YB~6d=qtgOLmz_m3by@LUxieSR24N0{&CV1q)^n#@YT?V!B<9K1^Ys6`z`+@sV3<u)LQUvQVmjd)NuHk=xf1;qkj_ns@wKkz6d>tVx*#|#o=9~!Y+PLRxJcy41IC<Lg<TNpJCf?`O>6ENo7zUgD*iUMS29aB>ZE@l|n5EUk2-?ZTqdh5~(671U?jfIZ_2uS=93ImC%R6mq#ChePwO?E&m%`#;>Gb4EDFt|4jN1=|}jV(Eo=1HvCWMf5rMQ@IRujO2-HzRYR=~UxoBIsWSW%=)=%ghkpWnRqT5lwK9Aj9peh=GU|8mmq`C6eS`Wf{1x=y!GDYXGS>5K`>p;5(oND0)LZaZN!Ll=qh5o*iT)P+HS{;I{)275)&E8Mlk^b&Z}h*D{vh2!eE|O#`oG~Hp#Kx=4{iIceg^3kQYPw5_-P~`X)5Y;_?gK0P^ZIZVts~fztt}$Eg`**x)go^X%Xo))P?X%&@Y8wi2ik~FShNs`d3NwNOMu=!_OvVk!GRJfuE0D7U~@MSFvxFZNKGXNxeut;d`U+PKqJDfZ7ATH*ztkJ>Yv`y{B!z)%Pb2Bn?0v1pgwbAE^&&U-*IO2f_D6KLG3fZTqc$7-<A)IO<6FAtWzpFzQhFk;r*bhr$oX`Y_vmtACl4N*afn20w;0mNXhQ1wIvh8hi@+aae!Zw%_WLNXev^P)EVXlM+dBs0r|+kV`~OfKS4{INN^9PbN(wO@yC<KAkjyG#)hrelq$g@EPbQVSS=)ztwLcZ6j?(-44H*w1Kn{eiQm_=(odfLcbO3Ti`dMKSnx1I*xi0{&Ui&q@(bkp+AY-=cu2-AIJJJ_@n4okXDgaqOOKtMtYO<2I_M7Rp?j4FGs%;>nm*gt^N?{6VhSSBk&)SOwvcF2jM?Ke+2#@`oma1WZQ4`2T1!#AHaWzejn*yq`j!`!yiEZA^iL3_hbD7+kUHGM|y|!HvD?@Z;||@HK=Rh*CXdgT?_v<_N}q)w|p)sK+1vt0{vOiDbi{9Gw5^Ce*u36eGc}WLOl(iP1;S`1-}RVPSU%i9q{j=&qluo{yp@&vAzp_2l{%X2Bi9^4dLsMo+i~stqb1(eM9)V=<8u$ZQFj!cOZ2lbwuq9?;$-;YKz(qz7zV+@a@odz`nM&{g!V{dXDrgY8&`gq)1Xr)Cl-C$VH+?z_-S}mbU$tZ%S%TYKGbZz7eSj=^50<@GX#Qg4!6q8P=QH_FMheq*v+hL0_WIfxk$a=i+s%z6yVVG}p!JR-Fg`6)DTb>sFl$e~vWU#p_nhg13%g9qSzGZ1}FEh2-0#z6RfowAjV#R$T}mO<LsQb*nCh??PJO;&rPof{!B2ck#Ma7r<M`u#OdlIv;)>&Up^5bq?;uJX~WI?u&Ij=W*Y@hQEORJnqj0_;cvbW8XRWIhZ#a*RcTCzZi8P{35J%HU7Cb@|vTKf37DAygk@!*k@f^B&juN8tQcTsian<Dew{KTVhWO_}1uKA=3=CIs7!toPs(Pz8NwtP+P*chL1pP4j+NNtx>1L`$#iLlTataPasXi`b4Z*{v}ef_1Zvv0X~WpPkJ6c0sSP*9EX|;pNd)1C!>EE#~uqm5q&&njzxVLeljwts4v5(!Y899*v>Z@=a>v0h3lJ$c|A$JNipz!(8q%Hg71mmT7MB4%lAb;lr(@e1b!g;0r34$`@;`Lb`bnf^!<?=j5-v4Fpkw9>T5f%Se#2NxaFU7S--nQ?~Cy5(6<F^1OFU)YrQ=(mhXVR2dOiuJA4=Po#8v8c7pFpibg&fd%ELToiMi()}-%(z6<ivIIp%im$t}Sz9FeT>7K#$uEBmL`An>5B4hbkq*q+L{tDJC{|u=C)*E2W^7m<0zQOBOZGfzG4C`3;QS;%O&{`u>E!3yr$B;(3czqPsET2LejrGx3vwTxhW2`sEn&oSgYGS=6)|%oNPhtHjtXY0MDUFnYnhx(pKMZv|{BUHvsA=#cux~hOI{Yx~9f6twUxVZ(J&76)ACA5*Y8{)ef!?Z5+x(O0ty<6K!_kLhMm;=Z`TXT`on?Dw)-%e)GrkLd7q6X6Jog6Jdk@e3E}nZnp09kK@;Rm0o<VIq!^U_Hqfi^ckH*><<eOr>F`ii*DTy=^J`sIPw5w1^;s5D>3I6Ag^*(JV|AVl;Q~h|?zH<!C3Vzrd6J6B$Y}F`4|5-mUmb3mwW&9UK?(a_'

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
