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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/01fe14f50de443e4b11ad1fe033df666/part_004.stl', 'relative_path': '01fe14f50de443e4b11ad1fe033df666/part_004.stl', 'source_sha256': '9f1d8790c74c532f082b46605537b52470074d0211db542a4cff742d8bef9303', 'input_faces': 744, 'input_vertices': 493, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.39869987964630127, -0.29368218779563904, -0.26846760511398315], [0.3987024426460266, -0.07614642381668091, 0.26921796798706055]]}
GEOMETRY_BASE85 = 'c$}r23AmNx+Q;9W3L(jsI5;aJLpn4_8CsM?Nkl2rN&}@yJ0(pkN)e@^fn+t&XiBB1y(%GT!XfiEmBKlv?>Nr+&Nuj;r~SL1{jUF7=eoY@`#RTs{eRE@+}-Pbp7pMGc)WCIdr0NtsQgczsOHkrU9UBWA|FRa#nF(Sg9i8R-m|1Z|AE7bq8bN%|HpJ%`x~$6(4{CE5)H4{qi0F?LG_v^>RsIH!g}=+^?D5$G<Z<A{<jYp)T5{OTX*YQ($o1RcXb=s(~Zw;+^kXkM5D9nCq^dzkAJGU7Sip;ep2c*bIXwTy{1|h?<|e^Y4Zoq-cZngwPtDDPvR#UE*f3P&rY~?OpBPGu>5aYmKO5U^H*(%`w@QGl*G=spE)pY$H9E*KV`o3pTy5d|B?Aka{D(w8lT&L_Aljr+1I)KXYf<fe+oZK|Cy)imiIINm2L6<&5z8dfAh=cmHS!xH$Q`)xuCp%_0tcP_iuj6>d=4a2jBV+{aC*AAJrK2UZMW8N0<8<=|6+7{iiIyX>R}KN78@7>PY_)ep33+RwtkS6BF0&F0}sU>-w9o>u<iUzxuZR=Ii>0eq{YaKeGP8m-RPa*FW?l>mT}&^;bWV{&oFBKeGOzA6fro)Tg{3e%G0)4R)0l@Y5YD?~ME5JTRw5P95{3FPrbmsn72>tM%>oF7?CjRO*{w_C;=eJATT_w&&C_KUt+mZvT8=ns2`4r;h5HvkrECHeb)rc|PB-`Feg<-_FnG>-kxIJ3pJR=jYJBoS)6t^K<A&&d;H~oS)UV^RxMSeh&S}`8o6>=jSL}cUPg~Q++!=&DY~oeLFrw9XUSL&q#eeKGnD5(|kQX)wkm<^eM-u`j%hT>%^Uf)<=C?pWw@U)z3)2_OHJ7qy4KN=G%03`FZxGtq1!|F8FCn+)v^su6lV>AwOHRe{I}P;FnF`v#gMxTCsF=+>h|nzy5tei$eayUslEavKOhJS-GK*AMHEvcHB>&`tz<r^D<xOmBKHRd6^&0$emXbKl5ttyv$F@yb|Wiyv)~mMfSNeujDD!%j@X(g`bppCGd4#k>$(0%+IWp?+ZU6^C~;Jdck>R@v|~7^UHpadDWh~z0kZ8_&To$KdO{Fud?II{j|(0i(j@ncU~Fu|CT$iG=5U%mBQC~C9RIkEBfX1tq1GLyvqJs?x$p4S^R{|D}$evd8I9XZSK5M_!*g3((?5<w0u1d?Q>;b={J_XU1(k@e4SU)e3@4QKbk4Wq2<4kJFl|W@nv3F{IW-K=as?Nd8P65<~8%YHxK6PyztX9ugna5t&g9P`q{~YHWsRHzSfV-*Wb}3>ge${cxARwee<<`wuF57UV<;*OWOQw?)PGT_7^$cEMLAC^L1X4<?FmMgAewX)p_A(WM1iK$(MPVU#7>K`5WcDho6>trRU(wyv$GOyewbm)p^v4gP*JO!q4iwI+3sQ!cWYSd6~ai=7pcsdEHp<r*vNUNu8JFGp|IKrUlOf=IeRDd_51Cujc{t^*ms{o(Ig=^FZiRe%B#ie%GPC{7yrk@;eQ_{O&>>`Q7FDvJU#YQ{R4fVV&i7r@r->x@JlF{)F7es&DtP!I%43^)r&M_p$1S=RSPBk5xZBS2j7Pv{3)*hv#VX^|@I5jO6D%=ZdfW<UQw#AMV>PUqAn#%KfeS$&1^(75DA_P<^|<N{DawC+gevJrdupk9j`7i?WN#{bb#l>4NJoepr9=b^XQ9NPgb>iyzh>KX3iTxBT>)ANH>=u>R`XI-9TSZ@#X-`MUn0j;z1=y8gk}^&c}U-J;O?iyzkCd|iL>Gm@XT{^E!A$In}T@x$+Z*82G^3ar2Sw$A43`kSxoZ@#X7s3YrdzOH}pW&O*huUirC$DY^B*XJGc^?4!Gk^61)^X^x_etKP@&ow{qISW7UImPPeeLnub`rN$xTl-wSFSYt|Uzh53PHCazR{e0@F<-Ac;%6j3@46#?I1cgit~=s~{gduXHWcb#{jfh~zV3I4pOO5${VVacpS=Am@xyuVxOJNf9Y5yl@ngOoKcS8sKj!Q46MQ*-!sp8I6Y9(HldiY?or3-2=k<@D*T2=#{_*qrH(&d=&(;2|zVx5z-*nr--+|mGo3HoD=Ied3`FfvhzTPLBulLF3>wR+QQ|^;PpXO_y_(|;(Keb-^WIYqwCw^A@l>76LFZbu>r_Gl>%}+_6NqbH&&F$0tNcyz<f9+GB3xY4t1)+a=F39txPkk;>-<}IX|MFa*zV(@IH@p0Mm;GV$b$?iW+aESx_lMQD{bBQUe>l%)|H}Nl`#15!`2k<|ht=14>He_#wm%%!LH38$PszM=e^`B;SKfKg>dXGH`bn9W?hl9hvOlc8?GLM;ka_9;u=%<_tbRB@TmP~@9Qv32;n0ul4~Kqae>i-u><^o-`@`Wlk^SLtJjniV=wGip)~D<bhdyP0IP@v|!=X>v9}a!W{&471_J>2CvOgTwS@wrR|9aiD&z1e*@VRom3!f|3yYRVky$hc!*SoN8a=i=dCfB>LZgRZ~{p)q#eAyok^OEahs4v&4P)F|{tWVh=R$uGu^(Ex%eTe1D{;>L5U#~}bzI-owJyPGUN8x*y>yi38ue|#}^JRZn{fx{@_lMOl)8kF{ht*HZymWt9{glp2_J@Nn`@`yIbzZVRtiJ6JhdQ!9tbS7GCHuqbCv{%3Kb*Pe#Pav2<he<Gdu|H8JU6MIk$in_Qs16~%-828^}~MMyLERJ>R<iv&;8BUf9@}SM)LFixxe_@Pu@TG7vJ&|wY%<)_i69dn6K~E<oWjA6u!P!qrSaYW4^vu6Z(<&WX#w1WI}y;PsV(GPey%vPsV(GPbNB|PtN*;=X&wObG`ZcTrYk`^7EeS#ShQ*_<7Iu;)mnm$+bCkY(34__xjA&_xjA&_xjYg_xjA&_xi%;%6od|>w9{kzPzUw>dSk2>PON~-g}Y@>wZ#beaz2$?-W1py;J<W_fEwR@15f3y?1J#tM8HG=e<X2_4PectFP~oiXTZox<1LyV?T)>=XQQDU(XMDKK+=l=Lhxe{9wMGA3{HJelTCp523!CAI#VDgZg%UFhA$~&>`oo_e*;XSdco+wcz6Ls5t7?E%wU0H~k;e!mqsdZv4M`<-KX+#{b_}-hV8LqVHXlqHEx+i?uF(LifOH$Xko<iSdt&e<atql(E${Uc-0|H9UXi;u9AipxfXNU2HG%&!gq~DZGum?dYd5{)+Ke<Qjj#*y<W@W4w(Tp7*)<*2Ow>HN4)%YcBSq-@&WNdky_A#`_rWBiDExW2<Ytn(=CCc>co0$1ZlETjBRzyyxOebT_<}y!X)EG5&(_7vvi6Vr+Gdw=&*J4bOXBeC^_ObS3<Ti&ZXuK)-=klD7)|CdPXi?<Lpxb;efLcqQYN)bRY7i$A*9fo_3!x_H;c=jcc97V_RjKZ@~Zj6WmScn4#vYrKW=7HW8Y)5S&?o6rsLi!PSCcnN(0-ay`R^o1C|$@oojjW;p2y2cwAZ=i<fcU-*X;%#&@yu!uHE?z}nfj5))GWtr4-(ma?xyElZwz|ff8E>YB=VM(Q<Dw>71OA&kH~!Vdujnsu4f4F_^_QrEk7exj*QkPPGPb(LH5k{Rp6BBoALpVLS`7cY`~Uv#;-Bb0;9~N;=k*^^1s~7Y>p!CkuEp5u8W%Gzrk>|Tj-PY!Jh~7*(M4?+ze7)e7m`;SJt4-67%w8%_<6=w*LWf0h1Br8%*7HHOVP#fDK1WO@q6@Scrke=p(n?98RKQ-8ZTvRb&VG@UQ7+o@4GeH>0%eU1HR40EiP_HZ-sY|cME!JjNfPcKDoxb7+YQA9gKHS!}E3*@4489ZiTzLxXH!MXcu@Zc{ib5V!WO4c5;okF}AwKTN!VqhUYylzH{+C`YrrN7azFz2>lTLmb?$p4`aNC@g8!Gzh`W9jlX65Ej2vvckzRZedu2J6Bi%5_!Qj@?<MbJba#yRGu}_G@jk{@*LW}Ez0~l0or`N+bU@p|ja{7Qq6vCF+>X5S(DP$_9pmfBHSWOJ>KeCW+>RQaJG;2iMJMzIxVei9U0j4VgKr@3LbO?oJ2UP~u5l;ER@e9j#y3#I^O-IZE^4DS;1gUN<Kir|4qSu0W6(M=K9lj8<QmszY;}!mFs?xj&#hcs?BXyqf)97$P6yEy=p}GOUJ-gpj9W2oMXvE-jIFM5#5kgc=hiMRbx{qi1Rvqz5EoaXE#OMz9fG!qacjn{$u+LV*y<WrVqA$Dp3io1s*4lRn(*&j9P8p7^fb68dB>us#rSN-XOnAuB4ev-T$6E4YIyGG;#wEiqwV1fTr_mi6m0~zC$AyeD8?NbcO=*Ndd61QxIN?c)bQ;8P2)3MoPySZfA8XW7k@zO!L`Uc9<3MS28<h!YkUf0t7}|~aV=_iuJ59*i<8h|_+%Hyxi}X+9WEyCIP~-w*JoUxT;r1%TV3N~#>Ld|+{Q&R^8dPaxmJdca#6*_Rp@1KW%8<^m&LdZ<2K|PAIaG28dqjqnHrw2c5%6j>S$H?XcvdNXp6RltCDvp+A_vhGrpQ!<LZp9u5neyRjJ|mKV1B$iyzUS;2+`72+yCpIM1CZ?sw4?eGqO6Uy6>0FNLo_C&CxFNV{l49bb1idOkcH9)UK5N5CV|M({{@6xtXb1&>CXz)k33G(Gv=TBDD`t>G)t$KWgBHs~a{4SW?k8NLd>8hsqT8g7eDf!o5Z=+Up&So9KjEIa{i1-IhwdVbS=XV1FW=wgzKH7;hLS$GEgG`bPq$lraMeE;{?qLbmZ@ayQ~@aym!=oI)3cpW+wUI(v7r@`ytQuGP<T^9>oY@tU#&kVX5&cJigx8S+(JoIgN9y}j?2c8cvK)1kK=wSgp`QA35GvN*JCUiEu34Rw{2w&*FvlcFzp-H$I+#J0OZVq3BUJhRbUrcyz$#K<^<E|yX9fy~5oL){XJ8m!IxW0_fw&Og>?;uI9_Pc1o@8$~hQnUr^^}?cx^MhwQhj>1Z@O(bn3_c%jh&G2C!i~_2;6`v`^kTR%+=Sm$6MjQY@Gn7I!k56UV(aL+w~Ib5QiSJj=-qHP_ztu$d<Wd!MGv$e+86Ez4<S6?i{1_23lB#7z=Pouv^QJ=4{~u2dKcOoz6-t`O~JRroe0mJ(Qa^O_$KrY_$Igu+8yo!ca5z@SHknnE^a}4qCMcAaDTKP+#eo_4uOZlX~Oep^j>&0JPI9LRB;{gJQ6J_s<`fW9)S)js<=*h9v)k3yRLcm*S#lPJXutJ&6x;4icW_gg&#v_z>mR`(3$WgcrrQ*o($V{#_Ln)EO-GrADsoyhv%U);d$^}bOt;Z&Y;ub4E!wmB>XHq2Ymvb13%+pHaZP`0-gpxf=+}VfgeK0!(JbRAA%nsJP$+fhljxf(R<*5@SW&g@SX5&=<V=r@Qr9ExE*>8+6le}ZjW|`+r!tQH^JA!9ndat2lzU)D|{V%J$f^IJ>0RV;<wk4@O%T|`BuVnFSIAz3m$;>hX=s-p+n*O;4x?#9s`d<$HHDGz~kVD3C~l}DezSIY4j=Bj(g8z+%-7u;y%LjP;@jr6dr<(f``EOx)_X(L`T6R;fDy%<I&OZcz6Puh9|%eqhsKQ;YVCdL?1xMzz@K~(EH$F@Ib=z0CXrk0Pc?tf&0V#(0k#2aNpQk^d&ss?V=A_f)0jD;1TFZcmzBSeFz>0Pa-@|M#saG;m6Sl@Z<0l^kH}kJQaNeo(fNkt@Sj*v%l~2_o5jWiwMt)(Yf$qcnLZWUIH&g=fg|kW#|HU8N3`_2rq|UaPcDg9J&yG4t@rm4L<|VLTAFW;3v^1;3wfn(TVV*@Pp_B@PqLE=rH(x_#Sj1d=GpV;rUK<0DLFh3+)g0f_tL<;GS>~v@hHP?vCCKcZctYDvsSd2+!SIq|n}IAGkL>2rYpJ!NbuJ@Njr6Iu0HSKZZ_%AA_f(GvMj)Q|Qz1Q}7)0S$GcoJh}*e9)5}N{4%;2ei?oRT>`%XuRxc=E8thrW$>%;N_08A5?+PA0Iz~qM-|8VYV<Yuzg_(7;=iKu{SB`_p+Cbv!JiYJzi{y-`X}^f_-E>RuH>#62b>n6e}R2?j?h2DK0N<Mjo+yA8##X>{><lp34ewD1^x;yLl3}Z@YgQBLH`Xs03V=l&vl%h>f&(1b2aodxEg!}S{FV7J`z10J`z3(Jp(=puI}P!v>ti}To3*O;kf~NI@|z07p)7Q3)e?agX_cRpr^v;z-Oa%;IrYgT%3s}&^mAeJ`6n^J`6sD@LU<K23Llwphv(};Hv16a8>wF7aiIbRVqH@U;QU3EB^TVq$uY<P^o`2_qCq*-~83p3NQI|Xj{ea7e<xb|NO~#ir<Nj{s&;Jmu>'

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
