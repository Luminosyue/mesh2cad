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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4af3caebbad24f25a04e4db48a85b74d/part_000.stl', 'relative_path': '4af3caebbad24f25a04e4db48a85b74d/part_000.stl', 'source_sha256': 'c3c994ebc995b5c69106f784e7b4941c61a29523530355db967406cb5b99a73d', 'input_faces': 506, 'input_vertices': 290, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11470112204551697, -0.08959449827671051, -0.43746650218963623], [0.12169398367404938, 0.14648830890655518, 0.2392374575138092]]}
GEOMETRY_BASE85 = 'c$}r12UJv7w1zLBpx6>CV3fhGQEaiqf;U7XcI;xJ4hnYBV8a&2UL#_`ijIn67fUR$T}$kR*fl0%jfp+QD4O_Y@Bg0%dF#Ek-g=L<_WHm1@1A|mJ@?!_cR<6Nd1WhT;3vpv<72CsTGTKkavKGWVbQTe`t*n%92_%fgop8-`tsw}xh>nb2#@eEh8d&EMnw<q5nHy7t!%xXwaZqtmF+n&c1UbwOt*otQPJXm7TJGrw96mdJ91F8>vg$mA6Kbpt6sjMZH(>z_~YxEf+J6t{Rd?(rw+$Akk<>V{2;Hb)h7Jkn>xg|n)s`4boPhe+hc+F#<72HX#V8$`_%8-yr=pV536tfGE;p=YNDm}8;`oKuWLlY58X9W{ft4#zh_t9cG>5k)_L4f^UW4tsBiV&a7cW!c_;O)glZT!+nX-xA8v~IT)n$jG<{6$e)XsPbxrHs{y}}C;IPB$2ftF^Xnsh2M{Ug0$T?H%8?)D|Zw;Ca|4byty_SMHJ+2PZI-z%v-*`U8z2~j-cWmknKXo?hJYTQ#xAOGCIy8cB?q9b`{X18AUeTOSs$Lhvr!%fg^$7Ky0do$hzcUE+ziW&6+`g>!jdCU6S7?Gdk+t<Yn!7_$r*AFw?cIOcr}NA+MAyN(SPk>sf^|qAK)-e{>IYf6ZuWEV&7Xo$Kk!we*7>NM)_2tL!#uzKQrF)K%Ypecd=K@P4AnZ;Gx%n%Yv1beQl7ehti_M?IvP1r;P0(JUj0{rsPp|S_3afWX?<tjDY%ZWrz4-&%j^c<Iy?>eqp=^-H$A_q<CdPHzN6z8Iv>Xt<eO*4sc#m*K1px)Lh~JG`>Ah>{ZZG=I6o2f_w>QITa$G^8+{h*{2euWp?)o_r&)QD<~x>jSKnHD5cT8Xn}zG5PFzpj&sLQo*w3?kG5-s=FVaUR=zOfdvZH=4+!wYV>A$?bN9*u9+Q-Gfe`Trf^uzwK);_{{l|G=pZ6>alInV>^Iejncq+?%M0gpA`sJs(CucKMm6Zu_I;hWp^zOYhr;X0mL2;YCT?sK!X2hOW}U-caWalIVbH)1|7LNK2@xR1<`mGC>)QQv%q`^d43enejNt(rJrD|9Tb@60W`^?3OYb^n;XnqdC~tx(^vRbHrheiw1QUQJX#z0D8vwcgwNnCJCwsMCA+V$DBt0_XLrjrz_a^AgoBvJiES)j)nzbDqAx+IsZ2l=qO|?dC#UkD18-IWPR}!;#<oHOAd>VVBM)_md@>_wXe0zd5MBx#8v<%^SZT{_|z(TX(ACygELFKVzc$j%;lfW4u|Y-zG+V=em&?cY-(W-{axx+ixt?^Kx|9g!8pk!+boS>wL_>tEgiO#C%rV!hH6eg8%aFPJMqyJB(X=Db}I-9rc~L?&>-lgL7cqg8S7sgT`W=KSm#LJXntW#M*jZM!UaJ$73$?y}~g6wP!HTI|J0W``yDj$815J{jHHdD+$-DEk37=oQu9u9Wes^w(6xHa6Y5quk=9wyt5DUY~LQfbrXHB>q_|JbHOiDHd_6o(Wp~3X$SW80Q85s1(E-CjQYmt)X#O_c7BR^Ub?$o{X-3LAKjRQ^Zn$E`evU6xQ|AS!u&hVKz`w#_#7Yn4&y$Hf&bObv0A6pLyWtsvHFg@7j^!|inH+3{@$kfi?2s%eV+t;UU=Pw-}jGk>L(mQ-yR#UzGGHre2!mkfI2_eksnn^&&y20^Mj+rm96T(DTdF@Vq0-u@dwm*%$|eK!ToEne_CHo)qJ1ZI<9r`DLyy<S**U99FM;GXc*S*b&UG<eXr5q;@iUS-dBCc7s>d1d=B3@okx8uaT@x@fDY>0Zrt6X8Xcwm(D?9o9oP2cqWTV>f!g<s3-l|jQQr*4d>mb;XdUN|aq2sJPQ-jV7Djy|W(&^iJo@TM`nHzp+tXg*^W7^7{%;L2?t@i${^>#An6X*wH%ZgaBXjFO%;&;5_03hB&-;VmFOA!b`)m*9A4}h-o%*&BJ<$J`d7*wlL*ysKpwBnT2H)@ACY@*8aO9`rxz5)6ruqig)9@IrzSFv-zGF;#)M*XhmRebTXAi8iqxEC`9I+h<RNwN(Iy+v`uk>c4=65-d=ay0q)Oq(peX|nI*P2NG<U{ox%XXvAefZ8^VW<;@>*8pdj{4K<t8aMYx;XaH537p&J=j-v+t=^|$|3)A>?_Mb-!E;0j=K``NiWqG{*TMmcMiuoTSwoj?>xB}`SY=EW{MN}&*Rm%W@G)Wet*Lsx?;V)?=1F-H8%-<<Av%Q_qk90px?+;-%%0su`e9S=a3!KMbpbY+O7VrxB7hVNPjm~>w8?@BfhhFXZXDqsBb%QdawHHKc*i!N%zBw7I+@})f><EX2>|rKepssT?b!0KN&yIcIddBPHDb<*+=kO7LU_9U31|%?c6AQPLFvpROfT$q0TdX(aHnrPktS%b&|X4eC)?Z?ZSOERek%G3p#(BkAeI`yS~)?p(i!p7JUofXC8L#r}e#B?$SB|{q=Lg2u|#&^KaD*^GV)_?;EwtglV0@i}bu~-{HB|@Z0*SYTYf^{}m5f`ubY!P~D%6(y%|b_#RT<Tv12I^*(|6oo-+q9NP`m+vTyZ>P<x*qt2rcdE29=@U4sRPvmQ=ufu0z|5Tp<zf{d|oyVm6m`_|&jQc@S2hD%!jeWAUDe`kqi_q5}+R-Pc6+nJ!v_6m8a_7YLnihoTx!!Mk>-BE)g|27%xFB4wZMMEzKW-T2^UDC#KNZnW{gs>Hum1)9`bz!vbs5g{K@`R<b1Fvji@!jAMor|e@ED|i7}m$wyA6JPKlL4Fx?z1@RzjW6PJF5J-r7vBZ~CS8u}@a}57+kxV4g-tu5+#X>YFXk<9aP=g*x40MrfY(9QnOlBmddQBXPeq!MGd!kl!q3jJ}STfj%5~0{N4Y)Hicu9gJkI^P-FTIqi6t9oHo(9{HdAroOqY9Qx9ZoABRmpQPvYtlmx?Cu;0kz3=Y)27mA&_-)&&Zyxz3LC^o6+j<{a&PH0tw9THQ*YWCU-0zzo9u(iYw;TSnE<1GGlngvibvdfOZP{V;f!rrF-|Tb^ex5tXpRyA9N%!XJxEKH0uD*TCBF%4AeV+QBjlWU9&_z7AcIl?ReRxCkljigF{xzQu(&rW1(mCiS{a@qv0!hc!PY*tX{b?M5KRU-Eef^Oq?yoAo_`W^kG5k5VbRCQ`OLZNrEv*-8-pKaoC*|?I%Y1lDeOteix;~DZxL>T&Z`5~IwKU%`qYnJ)$xGC~-Vps{bcWs+=Fbn*w;jv3RmXK$djD9hyD!z(;RE3NmW|cxT{=<ybl*_Sze6al%awELJ3D=ss`(G=<G#I<eVJ;J?Wp7V(-3{VJ4JnG<=I%bVQaMSS<(NfZ$Eqh>+Cy7ef!GgPR%?1PCsXDb$8+S8g(14(EPk@aowx$()CFn^F)2yfKWYO=j0Ua5B7RrCF}X+_r`Pg!&t3nZ=9;W(;BYN%Z~fSFpjU!YMt+;d75u+T8;dfh1GZLpQZWcqE1+kbxq;-Gf-!rH~dc*s&8E@j{JyI==c3ssBerdhWSjKrTMm)l4~^o@l$+nsGqFkrmwE1zH>qfp3|#rhre{Z`u0zKFwaMrzcXz=@)rz8oq}IuKMuIAzL^-P^RdRvN56a=kfQ$6c=$`ba2*yz!C(JO>!e2x#5$ZGtiJ7&wfH{K?ko7;|Ea#Uc?8xW&pe!O#y`k!ABQ@%v2M0`&DY|(C*ph6<)Wzb_hj{rAvv%<&rV>T)n}`3MR=nAz0tT{FCVCH4hTg4#%ws>7J=*ZeZ>>7{?5&KUW-1kP2acVqV^-JNF1JPqA#eQ{_=K;&c`_)&uh+i>YK?^*6Fxg+Tgj>Yl`*}=dDff7pyy?{?Hrn3y;Hd(97lOTTegNeq_(HRsHle)8RiTruVbmqp3dUS_@a7(K_$oo82nlx$?>?_06fp)whN-e_!h}m?!<q$Tu=tG2ekYYn$OYIy4XJuOA2ByQ1dX3cz>xj7Oa~)OXx^i2U*s;9p_=RQi7v)BD*f+5-6zzn|7Reu3~uR6>3Q_+}9s{O-*)-ySdu<5s3`VLnEu5$ao&g5a;i{LL_rvzp(k1biRlr~AP-Vk@D)cyWF5hn~~?0>SFrNAkRCKGl3{F8uUJuJhebG~cXIS$*>w&({a}MzI8pyPoUWYQtIN)6c>Af4vSqKPSvl9QW~L%x4Gv>#Sd4lKMv31E|xyCC;}!u8Y}#{`z3ex8~%+x-Ero7Q_0R-G0V(IdG8UV*Rbk@Xa+rdOuk$SU)ZqbsCqz{dyF>u{0cY?DR`iMxE;|;h%tSZQy*uP{*1PjL)s&+z&kyux`ol&C%Qs$?>?3D=Wi~=6;x01nYma3j8Bn&uI9L!&TvL<bG(s9QpUE!T05UC=K7S?JWFOJm2%UF2<#E@HcV(%Xz)3o=3k4<a+kUb+Ou{;e5w%J?rs$U975o#X81yEBplY>sG_};c$*S3H#7&OMf%RJ#1p0f53N^;yOQgjP-dQi0^6fow1&EQuIDD@&}<$KdFQD$pzmWS^~Ze`Bp-P`c`5|_+KI4-W|S?F&_Qc`W*G!Mxjpr3HZH3@p_og?C!X)M^D7}<Y#SB|5*d<s|5N_IiKJV?1xz;_4}c%ZWrX=Z-Q}GmE`x>_87NQC+w>f_{JiB4=x#o`L8YofBYB7FOY^hhu}K`InVN_V;(P!{B-!nz4Ms=H;3W(?}|DtabCvNBk)g!AU_bkRqH6`xugT;|7(4mSNrcU?qbe!AABRVB>rx66ZMUNH5m8%Qt<0E!0!WoT@C+}vg%u>JEFeV8?1i^_{M3@C-n8{2I2quYhT^!Z@Sj@bA1zZMNXrj(K9m3pZdg<AGiMZf9mV=(f{gCeKo4o{Qv%`@0M#0KgqH%gl|xPB#Zt)zCqqgJwO&sC5vt*?<H@ft|N=CC5vt$i|!|HB!5f2NxsQ>d`sO+&gY6;uE@p^_NL|~dy{ig{mD7Wg{URSg~)-_56OY#vec^NvgGpA>g4j|a@1<%a^xUtC2|nC2(>i12-%k!K=vj3Q1g-VaV><S4f*~fe}YB`=ch)I^OK8F2at=AD^Q1$E0C*DN0F<LD^iD%E0S&0fn*!G05zH%&AAHqazzhUbYTd0rS>FuB}Y>Gkt4~ysj=kV<U!Pt<U!=&)G_4Y<Pp@d<PqdJ>R04A@|V=n<S)s6sYA$p$=#{_$=%7_sJ+O&xE9@bjSCx@`$5>fXN2ARO4z;kgx&j7*u95^-TPeFeJ=>R?-ybBJtdrt>SJWyf29oEXL-r~4B-+C;SU+YRT;w78N$^V!j%}pr5VBj4B>p#Tx8ip#f{AUChXpm!tQ-5?B3hL?)@+9zDI;}QwtcG_fw34`zDG!fFV4TAv}s9Jd7bckRcpRwUgx<_c1c}gRpzg2)p-{uzT+byZ5KCdk+h{_qnk9UJ!QQFT(D7O1KNPn~{0{4K{F}^(6OW2*)ynM>2%RFoef4guh}4k7fuDVF>qU2=}7)Ab;VCj;`oTZB6b>j&MaASA6b@7S#6S7UX8sw&Z5y=G1oN=H!;t4&;{PaB2iOf^!i5$Q2*BBAA+o9850biuYVm*%h8tKe8v;puTTp{s?<e3z9v^UeuywFLDlQ8FCrULHHY2tarsO>IU*I@@`k`am5i=?4%wh?<DV_9wP4`Z>L)1?c}Z0edMj=P1N1w-JFB)6jwN0F^xKoJdHfv6*FA1+!a%)3&~T-lc@{HlgX2)v&oal6R0!E6UgJK)5+602VvQtoeb<d*@vwR>{H<ud@b6HEZUqb+LA09p5^_bt*PN;8LM-a@kHA*gxfNN+cAVYFoYwhoyoFqOB&dZvOlvM*uTP_d@X8_<;R08>O~gKk>&lOd8j$aGFEVw@kIR?!tXPL3o?X@GK9-egUPa=<(XafsqEWr2KKe^PQDi1K^EOk7Trn~-IV41q8q52$THThEaQnDW(Xf*=ywZ-@IHp{Zt5<w?DMY;>|fc>6AkQl;i-HrI+-jwi7YySEIK~R`$fl5$CG8OX<5b-UC0n#z!09z5T3~po=%-cmgjkSPM7EP3|G8y#ao8(U(}c6zsSE(ACi9|->2Rq-zVRt-XY&5-=?OMZ<BwfJ|O>0enNdrenNgteMNpv{+pUX&fvKTC%a;`D^eK3tEel;tH{f!OUTQ}iPU-IMDiSJJb4Z|fjWzvK%P&XOP)_&N?k-=N?u8Il2?+~P?O2YJU3yR>xM7xia>^NQEC9WD7i4TAh|I4ed>GU_sMyvxygCR`KWox`N##R`N;*ye$+x_KXNhZ2jpVpAgYaQ<GBfkxz4$%D;hI|KchAwe?|_aHYA6V>roq!>yc|w>yT@aYfx*GYmjSFKPJ~C*QM4c*Cm_OPst{^5jBh)#&Z+S={n~euE@m@&Q8rn&Q5-3K>sno62iYze<S}+enEXkenEateM){#{*(F#`A@Q!2h`I8EFtVe^(Om}eW^LgIeBivmtA$PxZ*lP_$u`x`6~GW^*s3k`3&_W`3(64^*izj@^R`>@^SJh>M`;u@;T~h@;UM)>i6VJ<ZIN+<jXuaVd=xa8tA(($qyOA_ZY%=sOeewfsxr$<@IBR@GEMDk=ZvN8JWFQ*xhf1-91^@-M59^y<OPd|ApP35yI}z5#hJgzsbMyJY^n926~tD;Kc^|?`rzuEu+7L$CBtJ(x1m;N%ZE>kLNMrSw?1$PGD{lc|LRIGB1hVQu>Q{EQ#Jq`c588qPK>AGLI$EOQFA-$D|JzVc!iP7i1J+e|?Xfo0>NZ=g-npi?Cl7B7Z=&W$By#S$e5|mVWD>r6>Dm>D&HUdb@v?{_mgVGeX$?IpWV=?9cH6Ifvq$hy2?Z>0Q!;KQYjMr8kGr3#H$X$3p1Uqu+qXLg>|^Ux&v+=+&TKo5w=v)ujJ1kA={yOTRvkh0rtUf68Ma^cv9*<FOEWjp;Y#G3i+zS^AqtmL4eV?vujqUMlSFx5Dn8?BS8ww>`4-b`SPP5B5m+=YYY!pN%X%UP4&<`fp_E<<H2{zn_w&Xa7O=WEkwt-sGIr9ON_uy-RxVSp)r7dUG1R3-r(PSQ@=E^iT3w8od+rzvHnqddKM><*_t+r|2K!G2zpEE&M%SOWrxYPxKNwjeL#ym-(JFde`Y+;j!>$9-alg{-^(9l=<V3b^6zTIQp;e{P&+LvcB`FtJZ)1@glrgcKJP@>kFQz{*ozDzM&ca0pv!y!2'

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
