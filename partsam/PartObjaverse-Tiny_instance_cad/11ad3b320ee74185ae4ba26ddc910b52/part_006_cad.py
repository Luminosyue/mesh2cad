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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/11ad3b320ee74185ae4ba26ddc910b52/part_006.stl', 'relative_path': '11ad3b320ee74185ae4ba26ddc910b52/part_006.stl', 'source_sha256': '9e5342763e3d9517016150791665512db4c2393fbd05c6d119b3e8c08cea2407', 'input_faces': 280, 'input_vertices': 337, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07004956156015396, -0.36272355914115906, -0.30224186182022095], [0.040552858263254166, -0.31511324644088745, 0.3880465030670166]]}
GEOMETRY_BASE85 = 'c$}r02~<=^*2fEt&O{|@T#}%~b_<FNqG%L@zQi3x(F9R5XrqD?6(b<7A$gHFnaPZaint_VFb?qxxbK)j9|9&paRH&B8%;-p*~F}7F`sej)%_Q|>gky?=leM4p8Ky~-M)3-eO0d?=XB)w#`m>l^w*i~etrJbhi#0R)`GQVOXHH3JU1sUx$mOID|}ch!OcJE(<eqnL{9f%OWCS`xpB#Jk^(|)0Z+sa4(M$Qh<`q5NmA^hS<ffUjWhY^*oDb)oG1S=c5xgZ_ZTqX@!qxpJ$u_yZU4u=X1s)~qFV<}ac{V8R+`>c+wT40Ubwq<px}DZHNo|o&JN*g{k?KqZJ6NpqN{>uxjt9&d-AN>V1?_hYFhVRjp2<O_ihTV6_rt*n(j(Ho?O-=xmNRlgYsN6ym7|9S2(Nrh1M-eIP8tPOV%n}b5$ty+ltOBT-MKu&QPCg`igb4N>UDc<My)|g1ZY(qs|AF`Wtv_rGCi`*KMVKPcG{>3XfvlV5J^UF6*%uZl^xD3MhYz;3Ab9bl-iS1mA?d{YKoLp6iY4vE_nmg&UMQHQymc-ni~NMsQo<>sU8msi%SeLvZFh9Q-w0*8ti-_P27qad)gs;cnL*rG8H?>vx}Ct?Uz7zbBXVyHBsAJT-%qdOW$Thn*gcb$_Ki(VMn;<MtWtGew?)P+V6(hc*6R`1GbqyxaAYlE)|*q;Q!hs~`}0LLC2z%RG8P7dqF@cc?#pYd-MCb-#4M?FH=xx4RtFf4{W~*Ibo|&s4bX+>ZD(!L@=16)yAJ3Yy`$R7>aL)7I~M<MMgM3Yy}%<WlO9-0pHJ^{|59_KR^%7v*{7$=Qt|3fElawC=qsL*-?(pV=35-i<r^sm?Ey`aQX<Kg;-TKb@oRsQ$C->AV}aP|u@Eot|9QDY;hDlH%`OHN0{6y;};G>$0<n%DVDC%Io#y@_KdS2J(DE^}o7r4)JTm@%(g`tT^nAXPw=uaIL1fQokpc_1EWdeNE4qWkGha-;Ar^x0UPi<g(9p!%6oA-&5|Fg60sf1P@f|lw7arM*aU}<}53h-`B<qL3369l~Si>lqvaTe{9AX@E%HjPcG{;P8}6oJ_lIr&RlO?i@grM7xnz8JfA(ed_HHL%EA4j=dcm`mB^!?dRO80*j$Cn=di5DlgoPaQ|~DI&}b1v-&3cytNRo6*iXHQb%T_3J-MvYIJt=K7oHDnMYAoUk0<9V+`Z~Gg)?U=?UMjUiKz2rJnH#@^2`{NY2`9r3#di>Z0y@sw4Yamiu{t-=b3h98^zC5&Z&J>4&sT+=dG;2J|5>$)-So?JV@s^;FA(-e&$?3&%=NU!R;q!ApQX53HVy!GF}U~4n7rqruPuphXzjHU$*F@+pOH}`dR6lc5(`?w~f*t$?N0MAKS@^O1$ik<ZkCt<$AS~;W#gS9O}B^xZWem_1aF3M*Y1V)^*+agV6sfs>knT@jYVX_gA>xZ#{i)=0Aq}a+&f!@)CF#<$FZ)dxQ9jx_wk9J%6;n2E`GtRe08tpxEK!{+9|a-}C<+mwDKVV!`X*#}-GtNBbxroZiQb#5IB&%lGV~{rN3jZ(^L_`todr>q*%PcRP<Oc|5tEI7)DB`C8<;t>kCR*X*;Ni~9Ua{r6e>nYFBBvluUJx6j&7`^xYwR_?A|hVxrY`(dds_)>}wC>PvFxx3eTPHoHYi2Rbv`zzO#+;ASkxws_qu%)+^JZ$BBQIF*E{K`5dmwEJnkCi;kxk{<uNU7UP^{-Uw*Hda~-Rj9yPe{Od;#W{l3#A@UZeQ``W-B+G`>^f>>RU>M!tDW96s}cAQvD$V&l4{e+~!<E@gV~gu2n}+{*bPMvy^=B2}-=aBpZ4D0v;^5k(^5L&W&_m%APtT>Pt=mPpA0u*@ElIag@jPA@!$xDtL^-?d3}qt~u8!`5X8fRDbzQ!C7(`ao0H|e*-_O<Y!4u=sx0kWi0Ma=PvQ?9_sTEoTC`p|B1E4@jWQdk>t#kr{vKRuk5j&Q+raX!W+&h<!6b-h`)vN80Nw2lss%vlRb1_Ud4X%r~3%5SI5$G@8;D!@%e<iyD9!p)X$JUbRWU>YCG||-w<E7oA!Si_DKiY4+*uqss9<o>wXmR4V?CayRQ8SD`(Et*q^<WJbHBu)nDfnd9;Kp;D4a&t-B*QODHDp+^Ve067mJNJGUt7O0GHAQl7Fv+Mf%Lfd38qC!F@x!c6Lq>mzl)fy;d;^Joh*c3bzY+=r6Oc$uFqOhtS#-QV(I;3?D}SCP7(7mT9os(Og_NmkxPaen8;<cj*Lx)V<uYKS`LMS*t%A164QH%f4O^$e>2=4tBNyfB3~#1q%6r=!o;lz6?WGxaBJh=@1h2P*OIv}l!A*}%tucc*ooo7DXYu2;`g>eS=?bFKSL?gz=`{*m>2a#_C?-!9j>uVkHCd=uo~pzK2ye>aEtdSzX0?pos2Q)oYD9TfM4%}oWLjQe#$aAQsi_(bpn;Bnv)$a7q9-JVI$m8wp(Zdxy@)1CqTsB+&mJHF=~*DJ(*S+}N8)NiNfgkJru5?{}&x+wYUx#OD1<6f68@))yH-t)FkB$xX^<~L>~yl36FY<)(dmFtd=MSgu<8h9My+f)D7?^L+%xGLg}b?XJ!XT_kNXk{Pjv!cMKD*H{F6@fZCDD|*ecz##;DeG#}OLx(_HDX=+x@3x<o)7L)>er`b6R&!>(%S!e?r<x4jA@y>y!Hp&vp?FjwSsF^Z7Ws226@_4TKglpUilX7hs@G5Vx4KJ;9KebW?m88h)$sVjtgG7Ubz{0&Vt7w{=DF}?R5&bS7y-t%B&V#kB%VjC|B~c=rH8Dq~y_}D&D2*ZAJHG*Ry5fd`0Dhw*;T<!CO#2cTE>ue<mBeIpXcaCzoc6apgw3FPV9??&RWZsy`jq`w`VSc~3U=VT%%PL}pVS$3>;jdSqs{w|+|A&`-**MXp8sIi=59<Qnj^YCk8%5U-d>`E$CK5RU+#K>f@O7Mx8A6P#791|O(!ts)$GItgw}90)!Z@j>8ykVmIJ<c^?qC;AI+t6Zbx*CzUczoN#E&D<$?#TdHY9AEH^owV*~y51ar$}={V;w#gX>y=!q7_a1EV^elouS@1J#w6@i`w$Es1OAfI2YpNw_=`#(*y!4KgundDW#RLVm5TULSHOQ3T+1sKTpLv?xV!we;I_O&;KhO)m-|qE@;*|yyZi^_DFn|)d~dqmJcr=M$ZYUnC67Kb6Ff+XXT$sK5WM_*k>5DJgYpdX-$Cnsi|aZ-d4~D!pzHckiPwfTp*)xSR#5yA%0KLGmi4-1A0(H3kok?UI>ZN7So>py)q?lLbrlc~^%q<(dsF1mKXqReKC~V9R;u&U&ji;(n}BaZ{KtZ`C3oHy^X2Ce{{`h)@+EjF_%{l-mt}z8Af9}JczKzUhb8AA&qX!Q^EunaxbiUdXK&xj!%e<uCHMh){_pK2I9oJdaChY)+RuAKC_W(+@%s=TOnhF+HmY+YuD62LotLwX`j8HOg?RkRZB*w4r9YDEWt){eEPnnrwQrv(yrIv?9~X}JbKqBr&se!t?8{5DX+PW=T`v5LaPWBWk%H^f13lu$5udtJ{6Fo!7)<Bo*3-nJ0>S%%M^pYNKf#TQeZZfg__1GZRCxr&k9C3vf{&;8F(<(LqMor7-?2xM^_=R*mQ{-T_|WHzt^3?K_5$(mF3h%`Q+6zp_%|0~t$En73B*62WLM7Ju_)pnz8z!D&yGzI+&#J1PSe{ijix#aE>?;7DMP`ZqWfr+3a(FiT5#>sNW@nNZcJGqIJ@*D;>##cblTrVp0d?+e~tZu+oRJ3XJs!^-;6ziyQ6c#b;KVL+%~NcJQeW=tA<A^zbcqB>UMsXFW&;(?q_XTe5~as1tv8Ar1$=lg6Bg1tDh9~AKdT%`;&r4cnzJnJ<6>gw_t7|@B^Xax&4vb^YDq#TexL%dmBCrx|<Kr$*r>wX&c5q-0tIckCA84x6EzC?JM}3&>wTV#?1v^1AUQOIk%7C&q5b)E97<({uJ~cZu_|9z~@4*=eCjC-{99mFX6V7+dTOB(6hMB<Tf3C8uTP?6V1H<KMLC1C&Rcs4nGKb47btT!r-5P-pp+iw>RKlhn~p$G>Kb;59vsZ$8np$EgX70#$CA$;r1BxK#bdR>&~q`bQg>pb8E+~DRgU$zvgQ<;r=^Dx{(i!KjHdYZl5#Kbr@gb_8GTI=&Kl?=2pS282SRnd$|>HI{<B9oX%}Ox2@2-G1j@g%q<OO>ecXXTJ$=Mlei^wTLClmD)=;u)-jGj+-&G1jK^`C!z~JPb1)wR{RjAQ(4pKWb9)jx9ODt(p5ithdML)va+|>|7G`QY`~-_0iE%2o7r4CyGxdw`u@?O-#&2=kfY=TAyr~az+s5rEbOy#__&pxQZ7j^xqhY4*??a!-!{-h{ABLIQ0bdPmdMC64x(a6MU*YdUoBlWGU!ngOX6hgx^8I{B_d{JlFjEJ^kAe>5){9#on5p~1Og$7n6uJ-Q2EsoM-4Sz-LI+~(57q^~D|8FYJpk>8u`gI___okLF`B!>NZ*gxTCRWL_9Y{I8{;p)>fpbIF2&qs=<67lfnA0F1o}AU@}WyG{s-6v_)E~)n0pWU7{>ntX273@{wudvF>m_6L#J?C#^~IdJ{@`r=BDDaui<mALjMV7>ILx2pqJsZ3t*;x4t@%BG;-_kFGB}nt}k>X#zA07@X64RakF9G^u3^4aSPzq9=bEe4}pclkAwa_w?>#ZeQW6ZF*g)G6uKGa9)xa;aT~Ca@FSo*a%+zH?%cXDdPbOj26TVS4Mtoye6AaKN0_Po;rl}m!RJ!pUw~eOx#iFUFkT6k0lxuyJLYykFUEKzKLaCt==n4P=i1a^+=k)Yn*Issp4@tK3xJur2dp<fXZqpL9T4|0bWe;Q0`r6K2;CfWzlVMV<DYr0zvKP~M!J~~jlXBaZo~fseS^`Q8~R6#uYg^LuZ2Fx?L4;+V5a^M{tEOB=uhF#Lw|tz68KW+_c3<_`W(iGz>dKmhu(#`ozN#R{xi3CxUGSH7vltOuW*aQ+$)&>GxT5J6QJiJ_Br?k&=K68!My1gLXX8<B>WWUKA7tP{WQis!Fs_5LU-lXg<A)hsr}%4T6AxWJAieDw?VhXTnp%~82f^?hHnLZALbZzJB)q68pAh&egJb#p_^cAzQ_NL+r!W;F*e`h&3FBN(48<g-{Z}9{dnks7@P0$=DYqD=tPXqFnZ57-}g0~ohN-r55w4e=O5rh@BL3<elUCpbO>Sw!%RI0z8iEW<ah+W1GG7B{%`RZe0S(J_)IJ4&KS1@YX;vO`aaAt@Rs;o8|VkQMUMAr)VA@z`^k92pDu2c^#|mhpH%-Xw0?3b&sG0VV&wQHP3cBA5={>_ziHS%0k(*ox&'

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
