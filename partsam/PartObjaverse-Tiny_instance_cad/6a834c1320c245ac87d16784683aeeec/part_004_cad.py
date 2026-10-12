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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/6a834c1320c245ac87d16784683aeeec/part_004.stl', 'relative_path': '6a834c1320c245ac87d16784683aeeec/part_004.stl', 'source_sha256': '8bbc7b273c741a7e9c5198876fcebf307d949793963fcedc356806f3b4edce78', 'input_faces': 546, 'input_vertices': 465, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.36576205492019653, -0.15369312465190887, -0.49999988079071045], [0.3589450716972351, -0.09126943349838257, 0.49344027042388916]]}
GEOMETRY_BASE85 = 'c$}r22~<_p{>P6v=PZ^(O4rOOLCw$<2ae`!rsdpV*AyH>1u=6xC|NlVIN*43C{a_?oKoT-2&jR8fZ%wuG<{l+S82U8dwZY#-KVoRySM)9|6J?4z8}74-{0A1Pxo@Q2KFmmrk2M3G}LbRd{e28zot=D)@o_fL&B$x9~~0WGHl8RrL^i+PXBOU{pyhZ14oq7rfajBjtPkv9o{s^)wEM+`=<V`rlFI=r-hFSduMX^m=K!x95pE-gya$9MokGJKQ{|(*Vf<lVsn4j9M}Kz&l98z`p$6|lW1SIRXj!AJ@)5gNs3%Me0_^EcU>EptZL75yM20M0d?cWdsc3&{&$9u#}rz*8Tm|>Gv{^wF1PD^vbI3ke<`>7Bj<N~HU~R$J^m)E|7pckXM0b%@2uSGH$ljGfBr6)>y#KbDVO_c=jf+del+XP*la7;b3e1jLC&?J>#5G1*OA-X;~bi2wbzC}%D4J=V;8G)u;J=pMQ-}1AELQ&eUFvvgV$K&X?ic3s@(H_SeiA?#c`}o)`=u%dpWn;d)ntapUa+iDYwTTd5Lu*<-EO?`?T247G?8Pxn8t0+nIZMb~aV*d2Y8asx8!U$286eR^+ZmBeJY<yY!TmYa`B@&h~QdZ9c?muj?1`oa@=%FUaM6q~$Ki6Z)A~m}7bIR5AbMey-(jwqbP+w_tT<l+FoO<sYrGa&w=S=UgXxkArzu`=bvpsK!~&`MAlsy-wshe4R)+A2&JY<IHp3Pq{yK|E2!O`$Eq7z9^AP{kQKc^`GZ*|9NiDyIh~oi=1O#cy3ns-Bi`*xn2L{Z(^MaRWDfUFzJDndt3B3h5at&{JBh5qEN?p{*<*I%r7FWT$}v%QR{k0(pjs{x8YW9T<K=bm$!1_8C7n#pYieq=Q{UX^s~-YIp^mp&$X6*%Jw|B&*7^LggW+lBIWjZ@?4z@s{P1wc|RIaPqFpcv#wBI&Ut+!qq>muI%dloxvJ;ox%^ya<sCwMJ`OyW$A{-~Kjqx+=lspNs(xw*HVOCTb>y7aF`KN-RgEXl<?-aXv8ki*{;LJA6x#FmU#;`(Tw$HRwS%qC(fyTm^zW)G>zJYEa-4Pa2X(CdqQ93e<XXEEtp3a-A-B&@<XYc}LT*HzuyXT2fN(CE(Z_{4{2Y_>ziZFWu@ZToSHDo^P4}6q+}`g}&d(V+=jV)^^K;D3J47mTO`oc)&vUsxA2)e?^gyq0j>$QHE~Cq#Y+)RJY+%i=$LIU=LY^}Ea*`r9=f~!&a;<FrJXOx;OU_+)V>7MwxOGI9Y975eTM4<Re4ljdxt^#ew#Pggt;&cw=G{H=cBV5orc|)T-#zYzklX9Fz$4_IuDz`BcVC-zPT23a-m=agIp?2mdG6U>TiM<-ILCCh*YlIkI_sD#AEhKY^OPS=XYQH5*vjSegy-^kBIo?Pl5>7u@m#;@&&DC6mymm2sI08dbNf7OJxr*tKiTt`kViBWa<5-|v7Z<>Ip^cXb9tQYTpDM0z|}LV^{nU25^`;K&{buQePLwJI3tW(q;IN_W4?IqcJ(}?nlGNq^Tl&{oV|0p3+?$h%Q>G%p3C#db9uhpQ+$Owp7m3X2|4D=&dV%Lw|;IO&*m{JgzYcnu6KQeT$>p!v^VS3zTnJxdpoc2f!O}`!#rnhx0iBvrvlTNyF=a=>KNVhLTAqF$T_dWbI+V`p^kPny~vsKI&#kI@Ld0SqWE0>JXch?*6Gq!XKp{Q)ZV@?+Pi<ccv@KJOO~_q%{NuZ^%YCm`|@*(QdR4}M2_{Zon4+H)G_W}Rpo!Zk5o-o?K@8#`9)b#N6zhiH~!)Qp?z}96;*DxkL>)Zvb~hs&vp3w9jbon*NfLUbE9ILYpUF?lNS&YtY|Oia(mAwJ(RiL<&x>FWAy4BVdeOJ(5^qS!AfU+KEL|>F{^^LlKY6~@;>6Z=6h1uN7}lnLLGfYz(r?n?{_KZb?iKOv3OtXciq<%>KjExMb6ybr&4b3Q{+a+->uxcau>Vr{&m-_>kkI3cGlN=AGG#Si5&Zg=l1@R+ROV+k6st!oEPoDTI;@Mdbu^udEx6yYrST(FfYHyv2jLjj}LOa@v+U$=Q95M)2gpUpAqWl_i%n9x90`9zV}<9y|Fbk$C=yXj9mNR$QEI};l5_?+1st>dRR(Wx2}%S+g0n_6R>2vP{-Z!x-!Rl<~jeqi058cjL@Ff=Q$rAvu{VMzPJ9KgTj7n@ZgFn=XKoAmp-i8NA9@jBhK8@^GcQ~H&-rEw%1*nHU8e|AG7?{hphj}-(3^(8v9uLRX43%+sJagkmW}0TS9I>*X$7ms$3hBQK-zjcD}5v6BNhRbD4}|mg{TT=a$T6*RA#6=bV_gDYp7!j4ZTr_k(`P&i0<eEceVq{yWR{{a38qNc@W3w;ZeEx_yn+pU84v-^_jIxN0BiIn7R3^=IB<&s7QEA0l@pr2W_29CRT~m3!B|e^QkjHHPl8UN<Q<(Hg&Xo&RgDm5umVnfsPv--lOfnWS2ua&E8B&Q;m>aN&bk`=3@@<LO$8ywPB`eh#zTY*pP9_IoKdzh(!P%kyrut7!_)`{+JfZ;`$%Uyt#;$8zIYKe0}`m)W|i<S*uLW?Jjeb*?S@J++#L?e~Q-RzJ00UlQ7zQ`~Gl9|{uM^ZR;#?aZEQbId8{bGe`Ek!sxs-|HHof3n}R8uk)$SIvkFRqp<%0sFmsILp1>qbxt}C*=HdHP1ai{2|ow1U;Q;{XFxrSm&#HLT=YV?)k9eY3De&{C=_OyTbYiIsg4y&dmqUXDRb$9THS^wEHbmRJrSM)vv97f4StebDYh&EiS8aJ#M@*=ksFc{C##^lgp~SL>+0}dLAti`pLf!k#lq7!W>n5eh$mIw&=A2Rc-`ED|7SA;zDKa<5Q%(?^yP{CF<WFug<X_%`K@`Zl5z@%h|cq^^ut4{E>5h{%Bnui#g68_mSFZ&h_bOmSU|#qh_5nVZZpLTDdl&Zklu5^7bxo+cal=Ps*WqYdqS=rm4nL&iQznw|`*yg5&HQe$$oZ%=vwJ?%nkx``!-UkGZ3tVeRKsNEe<L=YNTO;bH6icX#y{^TsFGID12c+#Y8s=i^)=$2hy@Z547)>q@&VFLyLu7|%Pk*xz3aW4S&4>wQ_?KhetN_dC~0mfPn{n{sS?9^OlL?nmuNiy~ES?`xj(&!zc3MXKE1zmHfhuYWn`>)+k3Nruo*_nJ&+Zl8z9y&G9BpXYMU&+`)b#I?#g`j(w+z10uTP_7d>$2u{pT{`QmV`jP7^M3oYkZVElm#lrH%{nKv|1sany%RTPDxXWr?dOtn{#;US7S=0L<yymI?7qv``&EhemuW49oS&br34ub+-*?<2x`;W>RXNvU`dRzkb*tWa;l6l(aeZ4~$ocz`r|?-J=kH&h)Rtn7_d9oHvXC2lU&*%Cljn(S)$^Ja#|XJOqz?N&<jUM^)i}#JALkNzokVM#&GufQz83Y^`q{i+KF7JPjDD4^bH@CzuaN8WFI(rQ)@*)`P^U{1_I*ydwaPliqm9Zsa&CYAEZ!#8;h$rr-2NQ<%^o55+`h)nNi#|4r#;TG1?+uTI<Jg5-;4EmKK-sxhp#s|=ksoa6^nItY-jtld&OK;f8^XOx1X((3IVyQ@zEc*5pw(dmvTNnhB-{EAGE@%uN`|USJh8B=i_O%p2zCEwAcDx&3hN)iJYI?Jl6yEi_eSwWwb~Ta=yRJ<_E-nVt?uNj|;gczVuG(dF!4K>x`bko-5k-f@+-QoR72iV63{mlp8|~tG#i4u2=`ZUu!FNh&k4SmQ_1XSU>S|*}gtoH&3|^k(XG9a?aP4l=Jy2(H`r^sIo}N`TCJ_`}4z3+wxTN&U1O*jmw`2&&%gm&h7Oe=YHxsdWU3o&J^tua$`ckR#k4VpBaJq*7cza*xy%ubNy>&{tx#4#B=^!a(g>Rd-Ga;zH{94iwV~ExpJ<BEm~^j=db0f#zBuN&UcQp=SKT1Rc?<z@)FM_=lr>lmv}BY|GV~5e@e{zfnwpgjKDo{s$6UHN4zqx`{EH*ZVvB!RGE)oXex95?`Ndkdn*34GGBD}Yi0h*u1r<#8Qwwpy!N><w_1T}U-Mkv*Cld(4of+IKb3R)eOYeL-xmTqiuL)vmUDhSH0n{HoJT3=^Qae2W%<2r;yC9-7O?C4gn7~5J0RA<yvsSC_Yyhg-TdV@<+#bYHEsiie^q?<@tVjw^)!vDqE<@_9p(Hd#r0S-?&^P1JU;OM^iPW02DbZO|4H$hQe<k0=E28+=Yc0clwI&=z_T^xv*6EwsVL8cKM$s!qA{j^5=?y^cqaG*i1G}GaxBp?qV+__;j!RYv^fqx2|f-!LG&d&5u*GR{3Q4*unA8AC&7~;%BSEd;8Wn!L}^5+MCtI;;B@d6cnUZLV{`@nC-PhHAK-t2saGt;_y_PkjfrvvqU(h35`70z{vLh@{5|+KMEM`k9o(P#P4F%76)3~;Tp4(7>Sw^z3&3gMvk>LWP=TYLl&_=yP1MT(pMl>2-@)^of$rk<1z=i-uF0`P;~~oJ;Ell48-l5~2Gcb;j%XUZEqEIES%|U=-U>Vu?fAZ!=C~*I=OM~1;M2e@z_fM<(R`v%q9~#%L{s6MUm&VO)B#=(OuZYp19%cV5=?y_xGqr}qNm|O;HSYaLzJh(-vd*h3vNslNYoVG3EUK{LzE-nlfl#%fL|nfj;JHN37C2?xFa|W9u5vif5I?+bR6G@D36AB0aNb^9s_s7yMo=|?(ml2AoSxsco;YgeW3hLB0sV(8<k={7EFB{xDohSqK5GC@Nr=3OTgp7ONn;EJ@6%94>%5@ycj+XJP!R>3{jp%Gz~r#qWm7wMEE55EbuJ6b`nJSUAP~ZdJFKo;L&h@@Mv%dL^%|q902zP2Y_1=b%J+>D7S+9f~nU4w*t2&8VG+4qWl892AFzv@C)EJL@&atz^j9wAgW6ANMoY>2fPaS7mfLEaGL*ypDF(euMVc7`~Y49Ohx%V+!stm`Co8<us_C~G8N@wxF480UAvUe5&cMX6kZIb|CLmL#?B(@q2Q_7U*}dR_F)wK2>1wUM8S)}#n>~Hr#QSbyc0A9X9jOG8H&O=5`{XH>G`AM{AdCWhDU&d!Qt=);BfF<_&>qa>Asx{e-=#7OnO$<gD7`{C`ZDlgCoK7;B&#$Y0Y`sU*`g4>IT|SQJw^!2%ZGy=Rf84M77~hL6l#DC{KV-1Wy3Zfg4~0{g{KFDbvq}v%xO(cRbhy=ASJo^Us`=m%*2U`MI_XqP&ABgXl2P8Hn-`_zv(6v_Aq-J_<hu{u-VMKL*YOXF-&Y!*_zId%(xRUlN^zpM@x&fP26vz<c3w;Jx6J5amRoB%-f~w!ss@iD<J8z8Jh6z80b!L$n&c3cd}z4X<4VQC>l`622UwypU)<JPN)7yaKO{g3kgEBYJ~qDBKOE8bVZ?=qdPM_z>{h@R9H#;E~{W;6uSfQJ-=cd@|e(o(!G>Q62?<13U`+7W_@{)97Cva0mQMT?Y?^_krtRji?k+UwBt=GLcEN9=;B|9y|v=8$1U*9Nrh)7d0uz5`9Fp0sb*~12__*91foe?nM+q^fEjg9F8`WI}!yFm4+z$;QsX4y1{+GK4{Yo{xY~5cm#YVn7RQT0Uiz+7y|>(HU}Q-7@t^-Uo!j@JQjQ&o()k>fyaVlF<vPU<y4~6@J;Xy;0+klP4Ma9-S9mS<;_ItL}^4D;hVu5!3!YDA3~I);hVslaIa{H@(g$cxF^y3L_OdifO~+u!)JhJ;I-Z1y};eUZQ&ikFA=pPDi2XE2T?8yZwqdV*OrBs22(Esen_^=W1@e<e+Snj*J=?}f+$ymKMAH@8T=5hqiy-?DgT6;Kf@n`2asz`iTcBz1HVG_Dwz5J@GhbQM4!U<gFhomAc}_{1n)<?1o%PlA)+scK8NoE@59eqh(3WYf+%l=e*tbn)Er~b9OLjLo`XJ5W8}15Gk9ZgW3-|C5gCgQiPpknzzd0@HFiB3*C?+cT8-<gacv=96NBq9xJG#u(MqBn@a^DFh(5;kk8zFiMxqV4z5&-h!E3hT`gUBSyo_imQ5@U@UO}`3*O%ZL<>f?+aeXnaQQktd8P_-C+H%yQHMhaHg16!|oHyg=enfqU2Ezw|`x5oW_1?Hfc_`5kTpxmKees$>xIPHiD32g|o9K1;0Pt%>{fUOd-vqyoHUr_WfCqwKgZBpy$7_e7KE2-?@L}L#X!C~SH3QM+bzFZP*)aHU@H<5B5{-n90{3%_(_lO+WxD40dZfMvOxFruN7OfhmuY{^e;np#1?G~^^9tmYeTf<nJqdpXOuzE=BdQ6n4<=hit4LHDULEX1R83=ls8;~j$Lq_$%Y%J!pPG*QQLao>1%0W4{!lK9*Oh~p2h;y=L=E(%2KrMG{Va_>@cwD&7wumq+^Z7qQw3ZVUJXpw^(Kw&2kMK!i@|Th-vYl49sqw8JOJDr-VEFvTn=6qoJEvLv<JQ$oKKWTl!KhM%ZBHGbI^wJ0ip!FE&+KyYSEhe;Gcu{fe*kFz}IlUtMISE-x7U8bOWO7#WgQp=S5EWFwr5ROYlPQC2$e^BDe^g2fqN$181Wzv`^>Z+2Cxnq5LV)PNH4#&%nFDyW#QR-QdsRd%>TB6VQM9JO|-lfDeNA!xO*>c<p|SM=r+X8aNZm#r<>9zukD=1dK-l>K0)h>6~RjlyjhcnCpF*L(28Y#;8lw0A3&502~Bw4-Ntc!@Gck!M%xICmKZ558fNx8*M1}BKPh=)RSmnzfwN6O8?#es^+gh^s}!f{EutoSBiff<$UE(Qp^6!se%2<(mh2E0UzrNn|Rs_?LWKaY$N'

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
