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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/55fcb4c56c9345e0bb18738061aeb7a1/part_004.stl', 'relative_path': '55fcb4c56c9345e0bb18738061aeb7a1/part_004.stl', 'source_sha256': 'ad8aecd1d8a01f3e150ace370d73a529b5a740e68c7ae0351b4a3dcdb6cf3789', 'input_faces': 555, 'input_vertices': 534, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.046743571758270264, 0.027927670627832413, 0.00783739984035492], [-0.00806046836078167, 0.09480232745409012, 0.3087376356124878]]}
GEOMETRY_BASE85 = 'c$}qN2b5Gr+I<gD1VJSjFpi1@MNz>lOA{4A7#sy;0A~mTNDv1k2ttEMkeo9N3~`9V07Fn{Q9w};0d+-p9TSQPP<L6wF8}v+-FkH2SDy2q-8tu;@Akc4S69{hUUk(QhSa9TOH}mC&-LDYcT^ib`A*MMl<_Kh{kvrM>)xqL-`jfk8RUDH#C83#aa!{y9!-7H_xgK-t9I_vw^Mf2`%|hun00T}8Yxw?p2_Z)o!R@TXR<qYQN3|y&%Rwm@7pc2PZxPz?XFt2YoyewUL)m&l>hRlwDw`|k1KXbh>qE`p{~aCyjgV}x;OB{m5F-fi&ss)KWwH`-~9e;m+lR0>})4ex!0;hJ?G?M(@y)W87|#x`{Nv!9viTEg-eeN_%*5hNQr-%_Iqbccj;b}U*@{>SoF>n&ivj(@)Gro{gw0M?N91I&82(q9G&OVBXxH#cjmW0oz#BhyLLt&uw$xIuRCYHOOF(EUhd34(R_8H?sZ*g`hQc+sZM>$O$%IlZ0xnmo%!WwB()zqe%yTSFUO`h_16b2aOtsUe_7_#Z{C&Eel)A*#`x<mcTREYM`kQ=>N`GL=G1E+NS>cM&u?_~KhUZFR_Fc)I`!YnifwexztwsEp@-(*=JWi2<`=l?C(x;Wtj_fl<Wv1bpM0>uRsUA!`nNjQe~?f0pL1Q00@wX(b-sVC&i8MSPxr4^d!lKd)*q|$`eSuof2_{yPevryv`_12pws$kbzVQM&g*AJ!#vXtt>;z`*7HwCo9ozM(E9l64jFk){ZQjIiF#!1NORw%=jXWe$kR)56ZN9p>IJTRt8;$rleL>%`Bwk4{80a`j{e7nG+!R?=jglF#r4yVY;)<6ucJGh`R8A^%cbX>x&1X~{)E!6yY$#Cb)9<3ZCCAe=2wpGbLknMO?xX*k3Kdy-!(3)^SFY18kg01TtPmK%j!HXtMj;md>WV4d0eqkV+&m4vO13|$ft2xoyQgA)3~h8<FY!BE6AsDS)IofDQdLYS%=U=b!hXs4xxwY(B^X;LJ!p;^iUnze6B<2!MMI@xh$z}({giMdbH%YTxb4<^gO3tu5eAF9-W+)?`q%b+<wj*nFX$VtB3ky$IJbP{-^oef2*VaMGf{ZjrWuG+pOF5+3LLC4(a&5VBLOSux`IEtj_yw*6sHl>-PJOb^Co6d@k*`S-0QUtlRJFP(Hq|t<L*x*6n_Sb-UjP<zv4Qd@k*`Lpt_LtlRxkC?ESJtMh(4q+`Fwy4~-E^0D8uI`6kbI`*rq+x==t$9^@aTiS1jbnLf7I`-Qk9sBKIT(sW~>C}JTZ-;d1Kkv6gI?q4tw?p|n|Fqu@=~O?w-wx$d{qTO9b*_KjZ-?@!{&~O6I^Vy%-wx%|{mc7p)_MKm{Wj~o{_uV~q|^Gz`)$^F{p9^N>vlblOe{3l@rp`jeV99|z@^7NZgVJ6k9I#%;K~p5#wI^nYn@qVyp!>DvZ!DEgDyQ*YT4mLJ^K4Vd~V52F5NqDqR^#t`+@$*`gdJ=<okYyoS*wA{qZW*IFhJ)w~sDx_0#IyPpfl31D*P5b?#^Ixzx|#bE%)vTgq*6&JT3kjyGzRX=nFkX1rTlZ*}Pzk>l^W^w_kAjwI@~9=IK=b30bI?L>OF&yBZV^M14c?6q)pl3uHx(R-J5>ai<puSwD$XkqeaEM1(aXVh&4y@FGZ*1La+OSkJrsGXj%q|c2t?P2tpBXV4Nbo$<;_G4*-Og`2P)}x&ptWDHYGA0_m&e=sSJu<FIZlWITlV|d4k6q=`BWYWc+K*Iu)r@!BwToPObnwpP_NRPq@_(<g%B4p?y>wmDby;}E<S*{D(4|L9UcEHwbIVrV63>r*wbG@>E@+q3enzGHOn!?G7r69T&5lX!NAG?*u1B|RS?SWf>qjNEAFV&k=-0luz^OMGpVWR)na!sC{FN(Rx>tRAQu~og`;ES_{Q{RBX*oA}e!e*C?7!8y|K6PPg|7YwI`uzVrg5Qb{;kgQAG;#G&^7;7=lPF}8C~eAAFFfyM5oU$bk&d5xqfoazE<d}f2(u-XKX%N=&FCKbN$EmoGNtQztH*q%@|yKtLy%?I^Vw;$10fhl-D2Vy#Az2u3~grf2<x_e~wo(`LwQDo!8aaw>3>Zt<Nbx*D*S+t5)ZAHRVi0<eT+57HgBVZhLR%k5ANtb@=l1m!1013nnG%cD?luRv+WiqhHLQoT%IN(>ry|D3=~RykttE9;}n!wj1fvqxs{fCXLIkdnJyJaO(RXnwB&!yN-3(G2Ep`uR5BPAFMxrlppTYAFVb$sh@V8`S@7Wsds3Ylpm}Q)PA5-`@uRu{kM9k|MtG7`3ZEMAA6tD{0H|b&A+|B`1%I-BVAv6zi|Bo_Yv0*>YVE{(5XIc{o6WES$Uh8e|kR5x_vGe%Exm#*6nk-P(Gf^v2LHsv2LHsh4S%Sj&=K7&g%Spm~|c(KObhD$HmWwS?6)_^WjiFjf<ZTTb-W|v(Dq<=fkY?xcK=n>pU)gJ{-!Yaq;uv;5yRtVb()+NY95^57i+(A7(vNhxB|nl+SfY&xa$$S1gI^U(Yh@#zkeLiF$CKLiffTU938vM*^MBBdpu+%|NH~h}HQ#!n*z5WIg!3A-9A5fYtdt!n)lL1Uj8ZShxEbtMhq;b-SOjI-f^axBD@x^Ld1IyB`bMq4Nmqc0U<h7dnryZugVH=hAtEb-N!9t_z(<ShxG(pr3ReVcqWM1D(zzAszd9tMhq;b$cEO#zp55*6n#D(CIwFI`^N?BO#so&*u@=dH(r4!aC1CpGR2d`r-2k>s&v49$}s9pU)$#bN%yqgmu1u`8>ip-@kkwVV&0>K98^-T7T#~!aA?3d>#qfr}GHwysq+jBzo-Kq;=cw)2z<tk&ur4p4It0!n)m0TAj}$tlRyn)%iTay4?>4<D&CONXLFV7#E#KShxFmtMhpzq~p90^pnmbAsy$Dpr3Re3F*{6pGQ~^^`FioA)V)k&Lgbz{PTH)b-uoQ9$`IHKXe`m=~SP59*NGWlM|nR+Amq1_e;@%_2wnzr{B24sb|jG>C#hf`XT1hW33PEap^fX^xNmsi%LKJj<fyKKOJzkf5!{&Ir~{7`>;!oG`#hQOOK}SPSS&Q=9=x>U3#o^iJdOpdp<Yj(u;-+-Q#S(?~VJM`6upp$EBzA%01w0=forLIs4PR?qQc6X;9KRUa$8YqrcL0cKrSt&?9+1p+^t)O1|!-2iKSL?R6yG&VMYkeq1jaoSjsMDQjxR^~kM5lj_9kDI=pv^~t)eL)L9QSiR`jh@`rTw5&4QRS&G&dSKnw1M9XPLhYj-Liwl%)@?n6+Ce>p`h$94-PS`W-_}F57PI2|q?ma=c=O3!E<HBjo0v;aY5UP@&UVVZwcDi^{k-jUXZ{CyZ#eY{bN9G(ug|!>PQB{jeJ(wtRL?hEdd_$4-g1sBx7q%<{@%PP@%k)}fB!oC^e&ek%n#|o{E!~Z59z`DaK4=%*6sXoKkfXmZs&*eV17ss=7-0H`HA@>qOSR2-Odl|b{<%_^AO6%JcM-2L#RKP2iEO)S-0b5oyW`f3+p^yzAsqk@$!8U(rLVWU$D;O<@#qmKHk)%zh=3m(YCyiS9+eJlvmNq%1roE78Ui!M)#kxbg%vY`%{*??)qQ<l%<dK;aQz0#CqTZ1kVW`LTm*7jG(WeH=sOQ&|lCG?;8OA9AY+jHu9AZ5)2eHL3|jzv7jN^>kn?*&{!X_A^3A>vk_tg@P7%0`kwa-;`88t2uAqE*Ekg1lQ_yZzQz&YB_zJ=8~<hGD8E23(Kr4?c*@HNrox{JPx&Q+neb=AQ(j&$8~$u~%F796!Jh?Bd0D|U_|xDiFC~}+e-b?9=LyEa9|uplFBlDfG(6@1mf^h!|3!Gpe-(Wg{9*8v|3feszQ$qTr?n1z<7*rY{)1j8-}o8_fS=IX@{O;tFZfr29=`E4J_G)lpsR0ujXl8sCg|iFUt?GBzY03|#@E;h`~yKd-}o9kfPW}x?;BrZJMd2g9ev|#Y!6-}$nuS^u_O4Gf~S4sYs>=wM(-cr_!^%E|6Xg|H@?Q+;HUI{@QtrA8(eEzYx@*pfACfkAJuj}1Lc_#TL{_+9`Fs6H$=<?&qTiR`vnaI%{>F<ttECBWC)({4U{)SYz^KT`O3TDJ&*e)>U$nXyN`P2b2Q$E&ul4pSkT2YP~J}BBZ4%+-M)eHx`^$-+aX{1Ujz>c9`g*8r%UW5=q!+>HxA{gi0R<z$WO)lTY9EFjdjqr_ASdZ{nhxGe~x#>YmI6CIo=JgyJ0@k(1$j@>6b!zPh7hmxSk5-tr2^I_e6ec%*j2znJ0zvrg}X*6Ys@q)$hfeH^aO)gReXlwep~EqSnfT7<($lp9;SYpu90+qXhl{UO#}EYJ}Qsj@J#r8zHs;Zv@^Lb6p45vJSL|fX28+jgg-UwD8Ye-xiqP7Wj-dKy%DnbM&b-Vk___I+ub7pu8SpQ*e#-!RvwF3)J_|)wIS2i1oo6fHy;I3f>Id-e1ZeM|=eQaqu+6Cg5q{wiY!$jMxPHVeq<$5%9X;_Wn|S4`My=dKjDXwz|&heFP})h`P;0?Pfyj0dz#|c0_(ppp$p5{yX9R)YulhGk7}g<#gPW>CjsOZBe6b(Wg}4Nz`-;@HU7Y!8@X_%G>L`Dd>Rs1b7GVrvT-xfG2P-H3M&o_&9h|aC>hmPeW`Eo(8UKSQo@B#P;A>;9U_rfOiG&hWHeCH}LL&@(jdQ;2Ge$W;aKC6tNX}D~wI~Z*uK_6r5Mg#EXj=UQF;$d0htaTktayi%a|tu`Kwnf)c`iK)eY2cft9>Pa<9dUQ*&863Zc;0@wFljQ3uQJ}IvtyrSS|-^5>h!+qfw3jX1ncqw>ki5}kLAz%4fiKWnv#tPv77F;0wG-7%1e_?FjBmMyX8^-n{;z{s7(AFu$)8PN{&1e6F_%pcn%}4)y^j*2m`5DZ+#_zx@%Uc!-QV{2YR}(DpjK2h)@*0BW@R!3=e!CzKejYsKwFT?ouY;%jUcpBA8{sK`P_PC57I@0_OtlUEHh9YG2nyjB!c%^qpa6aWJmq%@*27;9Px&2!)$mutQ+}&p1^gB8lvfwz!q0`L{3gL7_>15vzg{p8{yccfuMy0GKMS7nN`h(dr@>QxsbCWPN$`}H6O4mD4xaL|g3<6t!&6>L@FM&d;VC~)Fbw`Mc*?c32E!i=Pk9N!Q20aPDZfB40{#ei%F75w!5;-r`6Ysv;lB(|xgMV<!k-9F`4xhx@TbC4ezjmG{F(5Sr+B8euST2+euH4X;9A7l;8g@U@N?iPzge&p{!)0#ZxgJ9zY?Bu{huk;z+VGT`Q3sI@HfCye!pN7{7vwb|3$DB{#JO(9}sMYzZstLdj$FL^WiD4C0Gl8Ej;Bl1*_n%f~Wiz!7}*E;3=;vSPXwLJmohE7QkNsPx*C%Iq>JeQ+}0T2K*WDlwU5G0)GlT<rM@I;7@?3{9?ga_+#NIzfkZJ{FmS<FDV!fe>gnl#RV_Ge*vCy{dpe#^YE1G*TE3@L*VJp`GP3?C_Lr*e}s&LKN6nuiv(lfkAbJWykI>1@$i&iCYTI=GCbw__-H!(>F|_mP0xlu8=mstv=93IfH(yFKiUW1_!^_&#UzgLjjwSe`1umY`^F!S9Ob12lYQe)hNt`@!F2f3;VG{mm;-+fJmr@P=E0u_PkBYbT=;Y0DZf}S1O5zn$}bd5fj<SF@{)oH@F&1iUR*F1{#ba*&uY!Ue+i!Q-?e7o4~M7xjMfZ%jl;oz77X%@uki)&lY-}b<7*rQ{+-}i-}oAz1OHmk%QwEpXTiS^boY&~u^0HKf-b)CHFgL8Sdi%(Ut<^Wj|5No#@Cn$eoT<z8(-s7;C~l%_KmMG1N?JAH{bXgJA)q=^z@Cdu^afef<C_SHTDGmQP9sfzQ#V_KM4l<#@E;nTx(iu`zOSK;8i8A72Jfl8oat-y>I;W@RZ*o$cLW~Px-Ba0{8{+l-Cq&hQAq}@;d~D@C)H7uO-+9e;YjIcL{dD-vLi~ZNYZ<+u<p{Q?M2OR(Q&97i@vQ1)lQT1e@S*f~UNOU?cpE@RZ*y*Z_Y6Jmu8{>)@}0r@V?_4g59mlvfty!Ow%I{06~F_$%QlPZ2DKzZ{<OYXwW;FNLT4YQYltOW-NLQjh~b2cGgP1PkFWgs1#6!F>4h;VHjdumJu7c*-jY7QtTxPx)1X#qbxyQ+|yg7k(~0<<|+8!CwYX`SpSo@K?Z7exqO&{8jLjYfZ0)zZ#zMBZ4;tClLP%zE5yi@HfP7z~2+>6?~0&6nu~1kl^o#$HCtfydn4s@k8*}1qTJk5WfUJAlNPV0`UXz*97kfK0*8({B2)<_u_e<A-)g3OR!(?F=7$;TY{Z}PZ2)?Z!1U_yn^^D_-nF8yeT+@cqD=E!)uMNfX6)Zp6!T-!1uv>1#vt0UcmvuVZ`?n_&a#5@m=sec+W1x!{BcV-VnTsxC8uk!G6Jeh({CnTX?PUAoy;)XQv>wsb8#O@jv_T*v|dv-oQ)x&)N8$$-nwaeCI)FEBHlNYSZ&{FC-hKV)0)(P0%L_-v0qo?U5}'

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
