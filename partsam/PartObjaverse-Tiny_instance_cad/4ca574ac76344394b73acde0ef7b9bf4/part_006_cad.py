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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4ca574ac76344394b73acde0ef7b9bf4/part_006.stl', 'relative_path': '4ca574ac76344394b73acde0ef7b9bf4/part_006.stl', 'source_sha256': '2a073f3652d758959cd745cec0448b68ce45392c2f7c8cf255d906564b5296c6', 'input_faces': 537, 'input_vertices': 405, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.40365129709243774, -0.2245139628648758, -0.4743756055831909], [0.4036719501018524, 0.15754041075706482, 0.40539777278900146]]}
GEOMETRY_BASE85 = 'c$}qN33L?2*6slk79oIuOAI<}34~SIQON)?fFOp5EP^r-0)~B&0J1eI2nYc|G=j<?Dk=(3Hf51C1W3q`7?Ax5j<`K>2Sr8n{dKFpYP;{W=ltjY!@1}C`s-U&x2mhFYnelOuksaY8|tr~k>B-&ccvv823b|3wvm%H>Cx<AS(96gn=svH)Q~#;X<X6g{(I5~`HUQ6M$+)C$-^ckb@C_OF``3KGk?;E@sl2%lsRtb_({XFNKeZgGdWA>lOM^PkR`4gw`tY3nZI?DX8u|J|Knd35kg?h@zePNgCqT6LVwS41t}i7*=A#z)Ms2gMc1KEb|04aFLfyJ(#?g3T>g=fzlXj2wXXexyAoabL{2=g-%Gc`w@H8FaLGx!HsTHz5e7bA?$$T7DwLQw=BO-piqeDK4oH80lU)T~x-nbjqje)&<zvOMd~!cN;HCSQhWE?+_wL#2)XhK3Nj)@X#9=QzFlep2+|w5dWPXkN9PrYEy>=IR`kx(D<fTXcd#c!}TigEHEAx4Nb%B@8%eDPkxwbzmSL^>&E^h~|^LEg>l~&~l=~mfTsYh~K%l0>x4m|4A1KZZ`lQ?U<^bh@#>e>EW*X3%Rw?Ef)J4E@T9k{OBLF>Goxz6+F?acLm%AePlx3d{}=Y+ie$gkS7@aCgV-HN?l#&3-tF5A;wrS#BM_*aL&*6YK6pz=2wT|DB<Kd`#NF{l1_{*Qbl^Evj@5oi8ps`9sW<Zp(Qf28jGBhLO{UHSN!Q@8uW*O#P!u+?m->+#L_Vc||sJ-5B|_kTN4#aUQh=3^c{bv)lgH*&r|DC67LQtJNWOAg6$3yc$<`neaC|C&Up>v7EJnJvq;b&O-yqOQkfJ4{!)Jzlk6v(u^T@hWgD^T&9_bv<4Mo_KA$Q@8ucwZWa9dUiy{X=Ewg9{+FJy313aSu@{DH(u&@)YE@@6IcHB_k!hb>+lau43^1yZH-aSy+voG7Yvnpph2wEt*`Hdo}v7oIj!oIJ4E%Xuez1F>U(mIiYGlq>PBe=)eqY~t@>3rr3aTO-MG3)J;&q8DxcH&DxLv5mH(AEsYiO`Su$PT^u1oXH7YFMqu`BOKa}mWajt5gH8;q9$aTv%UiOQ~Q_D(S_4OZ=?Hug4wA9%?W*wy)3vx=G?O-1GT<Vb>eM+76wGwKndcA#5sjI%Nl^#6Ou+&*!V`ewyU+uFJXSv3!Yi0ia%b%7w<20{^pcj_7;>opC{3&mhIG>Ao@-y}Qy&NiW#$(2Puj&<6x{g1vLFwkA6)OKbRl6BS*B{IG(1Qi(hn#xk=bneW{I#zABk|Kpob6x^xLLKsubacp`UdJHt9a(T8+P^Er<)vA{&`_%J6H#LsCLMj9(J~ao`)D;ObEOB=kgrYJ_$<K?GtD{RXyL-QDJBN=DfDDUR)0hX<O{ngQxB&^zzrb?H}kKcD93+`?~sGcZhM-*NBf%dR7Hj`&d^iK)+DzdQaCjQ1#t(xY*SnE~Ke?Wfc^=`e*eF^pkzX&h|0tWuQN-Dt5i6qvoo9IP!RrGajSO68SzxGL&vVuj5MhkK9${>bIvhNIg(vMUkr?Ryw1;kBgTVxt>d!(nJ5sE^@`Qw2F%JN^|u+xI1o-EN9~B173RY>iZwcatp@E?~MKZYG3=~d=K49`C+Tf@8nYXov^=C3$j1<(#_ziE%JVDO{v@C&(Tq5ymYhO%3ZSlSN~G;uw&g+|LF7Kz7&Vf=jXQnm1e3vvXeh@>U@4~=fmdbS~ss|9`MRXe+NTNV=bp1*|Nz~=ksT->-nl3Pear4tS@w9>lo$#CG<SiK4!n2WllY6y#w9+t*Po?-=JRFpRa@J_Ez;_>nyJ8byg&~nrfdr_4j48Tpvd1h0o?Ybv<rye_MyYIiX^KQ#T7np7PR-NZDSeZjV3AU+daG@Y2?O&U)GFP^R1KR_IadR;JtjU3yDBY8}mVy^i*O-QDtfzFOzcF?2@h{C%-?_Fib6_j9fD{;YN0Ke?{^r}=(G`5p&aKCb#<$7Git{A#8gSIqb3srkTLJJw6TT@T3ljam8PX+o>Yx^=R>s_&5H1u~LPdFke~pQLVBEu?PVyItmEHQglhF*YZyb@h|=3uS+c(p$&pJ9WFCFn?Qze{lDekZi{u$?`o3Jy;;0Z<N01O}YN^KXOp&f&Ag>JrA^$aR$$vd&x_;;(I>ptZ(Fv0VQ6#wd&y$vOU@*KI<&k|4Z||UV5a;ys*S}G0!;PQ?q<nj?Y{VTD5mNb^Co}{`Ncv{zm4?C%vAF_2YNn?J@oy|BcI)<adPY)*A`ioVxveX*%Sbmu{?IBm0w)-SzW59{o`3ydRo>#DCq{aIDvMCCU7`9vI&BP1!Dc%%3}Z^jod-`r7{N`D$H1$54h<;-%|;u66!=xgM%>R6bv8?eZs6JmLwgsq##U$8+bpevVq_&z<XbKRMCx*%XgBxvu+R;JpK(6p!`^RlO2&`s?>AO2_*ZI@n;XGami^M(KEewa(x7C>{QR8ZFj&wWl%o6{+**6)N7dKE<P-Sd(MrI+gcNt@HjF_$Ez_$84OpbvDjxosaWc=i|KA`8dyYJ<dncx+|T1r?k$$Q^D_h%l!Cvkn8$8Xx+U{y$|fW%ys>p)jIz!b6xwJQ(_BT{aMcwm~PK2phwLsn6CYeQ`Po6-y=QGiPAC8(K??OMd|Pl7WdxoYzKQkoauU=7OMK!ey{$cbw01Q{rUU>I-ghD`LKDl)}!Vd(D}St>rwL%=zLzybv>`P<KgobrtAJ3>IR+lXRY&jwbrBNW7?n1t0OPhQ2V%S9mI9L4zj+=l{#N%ab2&ojPTflvK`nuj_Z0I7r3T*p?W{u>qM^Wbz<m6wXe+Ao7U77Qs?W_;0H?Q>)F8G7mJ+FD^R^meV3>0lsaD*M+O{II$uXmQ#xOFTRE$XU2$TaZmugRcE+RE^+v}2VrTq%A0V=-q}Um!-Zu#K{ifI%r`~6<`o@Hv@#uXC|CdVV`xr*^9${ykdf&r;aa7p(zU%!HuIv31t@HgBuG{_>#)qBlVDJA_nizIHN9_NE`aTwRy<d2*gO&2a&UVoIPDZ88u6EG-SCM9$UG1RvulyCKmpI!&?}J5_E?4s)w*SU;dp`|2-+$w}y<azNZHcRYV&5-#Ug><FFwk^EiK{<gU(q;URO0Hl*oQP~oiA}ccfFr^Ug>;4)BK=Osk0sQzNkO{o>FI=_Wo*KpHf%9#r~@Q{D4wdoN<*@d*)3kb;XJO+hE?(QdhslKCtCmR_csj?*j*7wyE)e?K5*-?=uG{R9Eu?zK_jxy^n46YFg%cf3Y8KzMfL%>bH7deTUNdzIx=r)G}u~=>7RX$NS1$?=SZAtxH48T>Vp@3v>*Yx!MQk0%o5?HEywU8Cz%PGS)7o^K+0W9p@li*XJNn{y5jrIzI=A(%~QaLFxRQNbCHZ$o6OFL|W(PL|W(PL{U1<iL4H-R6gunEK1ksV(F7qKJ46$>-yX+vU!$@pPlPP={VPmteCIbjh`Dr=jVpz-51q!;pdWCXXldU45jmPPpwCtd)C-^!kNE)uBvr*t{P~sbbfBDb$)IenU#7{=Eu&#xvtNJwa(AMxvtNtqx^AB&2@cFt#y75&UKzYKL_XfKjqKs%g@0hY2!{h`-A>nf!6u&3XB;gs$P6QR_lD<^&6!}{r-gM_U})iNB#ap`}5zQK#%(U3G}GnpD^A2-Gwff|NeyO_U}Nrzy2Kv)9v4ZK#%(U3DbGGQNKUo{;b@n-=8p@w?owLPnd4+=U<zo*8OZ<#&vuD{K!R@uGg(x*XvfT^K~xQZU248)&3$|cXM5?yVG62TAQ}0FyZYR4TG$*QQH`i>G;VSiS(z@`zLGJZT?q3S!>(6{r~qTYcoX*Il>kSdqmiHVUvM54!#iA4+<M3Y&i7cxHlX+@q2-E-CI~!XoM-?_kxq(b;246t0Sxnuq&_;IAJ3AO~Mj{B?G&HCxbT;M$H>9tTC_&coX<Eh7nH!CW0q{-vA?iJ?vU&gtfr0L##D{ap2biYa^c8h$SApI<O{qO{A?3BVGgbt%15GfL8;?fmZ{s3akQN75o}u^?Zg=Uzi_8ye^FREyCi3-6$*pcpZ2G`1Qit3+pJX9gKKO81c5knh9$vtU0hDcysV%VLgTQ64nDo{4N;r?!r0?yHi*SuoHL+_#MLP2&*V875NN8-h-g^MB2`dm^-5$opHZCFcrKh>Y&?-cs*cy@b>Vp2TMi!r6Qhq;EmuETYtoL7kCfE)(-V)hj#1)pHA@W1ie47A$U{7*AQ42ye{rHMEMo*{OSVx11o~}2QMdVzOZ@1CJ0*~>?vWBfD^$N30o-aQDKXPJ&k%1P63~S`-6ZB!3igWPey)&fD^$dqWnR?dEkS<2O_p75Z6=Sk0S<($pp><Ux>J$1kM3}95@#^2Yfzo9*p>G;2iKd$a^+$7C7NdaKahjv%w#u=Y@AT+3}teZ-6nV7VrjeKknZGYyw^n<6}+Wb>K8^)yKG1ALG&W@UIWw`tWOn@vtGrs)mkns{yW)fQ`Ycqx^Va6Yv>^`c}*Ye-zh~giRDS9XJ&{OV|)$gTY7Q`XNJoV@84NZ_YqNeLn_)_rY~9VRsAb59|kCS6FLd&4IT%cpF?3-Ufa%(zF0J2Pglo@Fkw&xK2R2Hqa7~HU+-KtKs@)@Vej$xbA|q>A=3=xx$tRn+===J{!C*FddwHo<@Fz0SBLtYr;Fhm*D;^U^@5$Lw%n+15>~|gI5Js0}mk2IA9g<HmK)qz!u>15z{;v@x{O;;ETbR0&~F$mpS-CTrUG(1Y7`4_!Rit!ZyHn1M(pLmaz3Gb3I}r{wC7sw9CLZAk9+XV(>SR<|*JJ@GfYhI>0#ar!jU+0geV=fHCn2;5hI{aeowWH28dsm2-h(z-fFNi!pL6##TL+kA?48_)owXI3DBWc#P3{%pQ+e#v`6dh-VbW)KM4{iPKzxzBjjk>+cWEC1}1853C1Ha|8OOHUsa7Yno5ccdR9NGOp>{Pv6My;QE_Ma|4<`bO!bWe^^*h*a%<__%LCaxSxr8591#Bj08>vr~C9B>JOfYYr@42J{8wF@SO!7#Pw8Yi@|enor*lV0SAKD78dJM^Buy9;QC%FunzbDVHJ?R0@4ugC+xq5x=&aEzTI%YHZT^PVx@V({Xif1EZmz3ydV5AlrbAP0DL6sISiNyUKw?%gn0f!OoTCroh$}1#lSZfSP|SnY~`U<M!c1wl>_>~DeVPA-6#A8oXY(YWfOi4PWQ;CJn%o@bdP*00WW~lJ@PStUxCj?o6G|a1fMHz9~AZka6fn_VI76t2h0F36!y5V1HdQ2$!9M7<|2;__;i9_C*<)Y%AxY&d<tv$6z?MJ0byN%gTbo{tLal^5f-9cN>c;rY9LJ)q#2BKgOQfFDbj?6b$}6X4<kMYM!Z;9Es^FypSmU-0#0}>I2m#Be_7Z#VcUUY!3kdi-wwV_SUdH2j8}mM_^aUSVD#5k*ssDO!W#RO5l`|dBYqi1{1ahAh5m!UXMx{?lM!FxQ%3wDfvW{>L3~>fBk?i9Mx#!nQ6J)4g}sP6y@>j6N7}7OzZKdxq+N~ltC9Cu<WK2`0at;K#=VDu!@yVL-V4Bo!O8aG{%Y_o$a5?5T?M`mxCML*{E5qbA6#3|hzEr|kMf>JdBpRCWg_oP#JLJS`S8m}9xuQr2)`im&~+b!b{vB?ei<?3A&xxcO?;)W=M2?H2ww%iOISri^)Esn_;a}TDzF_m`NYDH&;U<G8Et{<z{?9OhjbOeV}aekW5H8_Yrs>%S0e3Q$gezj8t^&rH1H5`CHP9@Lwv2US8)9bG~zvk#UPIul#vFX9`Ne{Ed-wm@T-9O5busMx&hZX>Y0l6N=4fkNZTFhyTg|_y_07R^^Ow$3{LNFBfQguiQx3U|6-{3neZHV1pE`=S@6rqlky{Mgt6fdq;Kt0Ncp#h5x))C2>dqiE69WLx&kA90(chu1o%mm^9SPk1KK&@SqDFkbcDyiDgWOLRX$-W#6of2ih2<Kj=WDG?G@l};FP8n(zQa`)@aj2v}+>T;#cJLJL38sF%hRR^G`#KkAzo^zsJyApBi5Y)4_*=Q#!&wk;fAF>2a6xq4AdRUZ3K9e2V`Fjqd#jBmNU~@>>F23cdt97q|>O7d#!<7d#!D;v@VC_4^5BX?_Xi6J7+Te3m0U;eFtJ!6_Z#CFJoV(o(#H8HoKM)OQ7N2{_%$Ks^Yb0iPh!P7yW@_!#&D!m@>p03V9$p2F@Cc0X_ccq?H|g|!54hU*(d88-{N3D^L<gRmyT+JLvf_3gsagav?igJ%hQL|8WXa9l5^ek1I5;2q%a2-_&^HQ?*ux5K9rurl~-@OcKf0(>L#Is_~Nzeki^O;~T>HQ?WgdtV6q7Wg^%be~Ey4cHsJD$-N|ehXfNw1<FSfYWbxj|zJqM*KbC5%BlGKM;0USb?xjK)Nmww%MWW6jmy12e1sB@LllDz)iq+!QX}7zhK0713v`c4Zcg*X<;8DUc!Ha6P^M;3Ql$SOxQ<=oA{@={uI||fak%_fS1C~BbLKRM|Dr{<ttaa{6GEo1b_e08s2dIX9YZ^`-sSya=XaOJ}^q}6(hg@<-|YQFncLLSN{XnDkJF'

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
