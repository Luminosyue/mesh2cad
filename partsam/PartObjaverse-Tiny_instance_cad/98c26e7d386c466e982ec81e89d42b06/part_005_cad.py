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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/98c26e7d386c466e982ec81e89d42b06/part_005.stl', 'relative_path': '98c26e7d386c466e982ec81e89d42b06/part_005.stl', 'source_sha256': 'aa43b4156b5f1a90e9c64434f2a65f856069a7c29dca732f9c22550440b76cda', 'input_faces': 602, 'input_vertices': 373, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17066055536270142, -0.18100745975971222, -0.4503387212753296], [-0.10346607863903046, -0.0744839608669281, 0.1886397749185562]]}
GEOMETRY_BASE85 = 'c$}r22b5Jswub8xBq}+lOKNhEtb$xXksKwXHX=<>QiF^buUQcW6UI?nKm?2o0*ZtShzdwX1wp-raZD)s9-=d-Q~T6c)wim7YrXXzYwh*_^`Cuq?NfD5_3mvi2lXvnq@pta>Z-vD>vg`azEWbPRYf&tLhkIz<0s5&Ic>(=m?|6T^3UQ!1BUe<G%BX%s2dtxHDT8H+(zfe8+Fd<)Tnv9QO@+-*}3DUT`@iPstKa^9CyvE30j{uY21tndfd2e$F|MmZJRWY-xU8p{wt|dNVYq?eY3`N|K?i-lQkdxXmf_HzOHWc7e4m%ybu4}BA7aM;)v(JZimt9z2fQd@sCG(qW9dRnR;?U_efWxR(X1A_vuumr<!<iQZLVs^kla`4tw$QIvRa<m1AD~k&`w@_kG;P)8k*Q+!V#XWuq4-Z^iu^qw%5Do~}mk-4J25-d-H_!m0I9{4zT||Kzq4Z$#JQ|M2w0vYwHiTJop&yoq^Nz8?8EJml$losO=H{2%V?twVN~7Dj*a4o^?7dv|RVXX^leo#%{=^kng~eZ6hdNKc#>_x3kEv6#{KPl)t%Y>UzNT(~WocYiNWPxU<4=r>jM^hC$sqW33pu;0;4J$d7yt(otG)#DdTiuBZxtRr6h&Ml39Yvt+LcP=vTRoOnrym{O7iu7ceiJorXpVVvFhduwTZO!|Z-QUwwzif}*ljNdZUYz6|#f?7dfTzcA84<lF$@`jlanhxqcr(%mwmIzk|7zZc1+Vz=-|Zgh$<|N#&-KjSXy4T*i~RV%wp*9^-a7wzh1Z(r{oPyV>;((gL~%-e=;?VS*S!|qxAb;zos;V(M|!H<Du4aw{JuKUr+?|~yUO`I(i0WdM0)CP51RO|FErnK`&FKvzH5xxuVUXH$<!0EQ)a)un0VCl|9rC9uNww<{@E|x5Pk2-HEGX3arSS~cb%$S*z-^Rk`wJ$V$Z)k|LoykM&EU^RV~jy-DSSnuiTeC|787X(f6B-J>vVHTyFO3tFnGR4<^j_`%1r$%(~oZ)+f>Iok(B4^nFinw(RXF{*b3VJ+*jAq^q*)KFHM7)J8@h^|Ys_cRpaw^O94KX6o_B8XNsc4^LOeJ~!*Xs>QKPJ+Wn}S^up+d;Y2J+0pvP_w{<GYv#Pqn(rvR_vqW1dftO`&3Rj6t`}cjHYL*4106g)-mP}@9mPjAd^a;rcF}L5{fh5i?9W>#+w51vs($=$zcBk%X{i5Pdx}K+l6T`UFHUx)7o+be{mTJQPcFLBoVQO-^4G2QebM)oy8C{AeI9<<d`G>edHb%0myY!KKR0jp;*TpAeMjlLj~hKJ=ZxpD)x&ex>ft$T_3#|FdUy`I_`x}B_3#{a^9JXzixZr~&ObPZoquo+yZnQ5*ySIb!*1Pzb2#7MKZjlX;2d^&2IsJgADqL^KRAcox&`O3)x&ex<rAF4E>3U`TRl97<3;<QvEH+KSnpXqtoNLMQ14kitoN)Q)_YbD>piCj^`46#)O#*|Q13bapx$%O71Vp~xq^Dn`PW(#y+4VZgr|pfpvxzy1Fas`fld$VKsRqt2U<O>1Ks`xb)d^9r~{oI)PXKeSO?y_-<<C)JG~X@C;Pphsi&5m9qH<`t)8B)J3l&?^4>gs$kXRGi}b|Y?>zs!F;AQK@chP}o;Wls(&Jg?=U{s3@n~NYA3qeuNfyaEn5h?-7d^Q#Va~~$w;agS3(SkIwq0xVQ;+!m>s~bH+pYI`^Cr>5`03>%wq)j+m^s(zEzEi*OPt)3spna}vUv`xC#~M2+G<Z{{Zr}m-b_8)>c{``R;C`e`}OmQ*SvXIx73}(y?nCK6HC6^>cv4<mmOZ^#bJMws`@@Jj@4`L@bXDmedt4LJb(5@-Tso7Pr~ZYcK6mtp=Xc0>+hb<`;!>`xVJv3gXq__^zz9=SH&)m)+ae^k*P~~-&B<qJ2UmvG4x)^O__S0)nor&>gmBcTRmK7tB31s^#t#;s`beZFHiLJkZ(75d2ZnSKk&h`-n_v&yZFI6yZFI6TRpwid@t$K^SpfW(DN!><mHo%o_OrGJWuC4$}2Z}*O~P2dE@BuRwYtr($!FZ9hCikzsXwe<-ZpHgZ}#D@%@JTo^ADD-xKHwyYCa{nD}A81-(GO1-(GO#rlW+7W4xB7W4xB7W4xB7ORK-78^h8x7he$zs358{TBONVZX&bSJ-c{{=v^*=O6ZAY(8Nh2E9NZ#_C}o#?Bk|VbBZoVeI~feHfch*oU!t*oU!kf}g+11{WDUsQ;}V*8f%y>wl|<^}p4_`rpM5>VK<;^}m}psQ+D@p#FFMLH+OigZkg)AJqRY|DgVN>lW1i`Tl<W@8SpbzsobI|6Tl`{&)UC{qNQ-sQ;}V*8eV_p#FDpg8JX;1^O@}>zd~c>Nl&0^_$hhI?Cxm{pRA2I%(dYm8pZ7dRSjsy+B=eeJvCJuJwLhhn{%;f#|(Tmw4Rhwcd*MJM5oWJ?xWMJ?xWMJ?xWMJ?xXXI6<Gp>S3S6<rDNt+`K`b#64HgCvo!zeG->v&?m8a*e7xG27MA2Kj@RV=L-5HE`HD_v3l4iaq)vbiCdqbPvZQ8K8c&R$}02zAG+Q15Bn$Ssed)k8}_l$3-qzk3-qzk3-qzk3-qyV{IHLWUZ9U{=MDSVHcr^bw*Fxs+xmxnY@2`B$F}*0eQdjKVISN12YqZCKkQ@MJi|V=jUV>0t$*0Zw(A!5vC#|kv28wKAKS(W``GB=`I&Ay*5nz~Z&nZMH>-#BoAVFqH>-#Bo7Kbm&FW$O=JcR`bMb@v&BYJuH|HPJZ|=E*`prF8P`^3<pnh}yLH*|P3F<eihxMD&gZj<Q8`N)B59>F#zd`-x@(JoUrw8?$ixbvw&Fh&wf1GW8u08SG!Aw1lo|v}mfTz=cNNxMb^S6D8yw16vzj}1emNUgkwmrw|KcoiKHtW;v(`{$cZ5*4YO6-XCFYH%XJ?vLlJ?vLFJ?K|hJ?vLlJ?vMwd8rfZ?`1BI)%m^5>Itj!dzp(9{66mD1iz2Fe1hM{U7Vor;o<~+50_8S_i*bx($rDu*~fNe>M5(=IxFR^Cwj8Yz7^iQ!SD5M-r)CotB1eWJ3Z*1xO{^CiCc%Df8yfU`mN0Z|GAbKJ=L{=_gs1CiRKSQzo(}w>@?@aBfOtImhU=~9{+B|j!Zp?uEupqol!4;^M*`4Vf9s~mY+#a4E!U{)A_#aduVlKb>2glXPa}p{y-{qW29&EJ=!={k6WEMR##RJ;wXF0us)%#SRbpWen4k^3h1nl)syI{SIzo_x?+8-?)pND%D;CeJ@r^uFCW`4O00f9btXO8=cPBjd9DAy@>Y85iLUN=<LS+VyuaFMc-j0<UazT?SP4~8<&4YtlN}M|pT#r($<E|<|EoXQ>Cn2(|MyRJPRmwnyI9*V+PZ4{73>E8Z*5(;-i2$z|4Z8iT)%*8!aHlb5bZ+r3%E~s0=y7@O4~_do+O6we{1_w+rKd3e}IKzhW`OCtgQrC3@ilip?xmVb`d7L7uXNp3*HwT3>O>(AE2#|w*Hv#-k9*7;KlHZS;L-~@a|w&cvse-JL_?h@k!Ptk+DYI!QbHB;S&2S{hR|e76JRi#e^%cH(X5k?`S>YJ&E}{G3EZ^nDC;Yf)|CyK)El*Somr7@>g;{1^*2^4L{AC!tc;_o3`&U;ooZeQQHY^_knlA?}Oi^?E*dT`P#aGo#EdR<96^ixY(V_T>lP!ocPCydmLT(z07w9co+OaJ;z^_nM-g!d>%Q?2fM%}w;z<ruN!&(%vkiFi7)dlAfCjX2QGxqgWm%#fG^<Qdzee+PJnVxg7rx--w$X%f#UNM@$Z5E1pgkq7jD<fuHgyR_yl|QZN~n6Pn_>n{=7f(yg%~H_SqM}yRkN1SzB4_g<w~BS9}(7&jR=(+V0oZH)c$Dca2lDP1ZI8oDP3ZUw?u71pfxVIA-p9i2Egu@BuM%?QwiW6Mm`YBVze61fKy#e+C=?A3zM@lFwjrx(pl*4u&sR<{4fFXTZgT{~f#>K7f2K#zycwf|tU(!)2X%frG(I;e+9$L3y6h<S96w`DEU8;CT3We1xy#zEz;aS;e!<^W=c?oH^`KPDTzn<d}m`FJe4L99aj+V>!4Ez8t<7Tm@gny^BG4=EW+1EfzD!a(o`u_JFp2F=N7eXdI?(q_!88!8~QSnDD2xEo1yB_!Rsa?SHklTyQ3Q1=n5ybKzHMd|hKU_!_)t%;fSgIZ190V^1h^T}=2u@*PO71JQ+FK@MXu;X}Zy;gW~s^BR~9zk++N!p4xJnDEug*qB)U`ix=y#t?g0EI&V+^GKd;B-eYy^4Gl|I3$+8FT#5>$1>)8g|%7%z7AgjUjnX%ujbw*pu`m}YashE5tREUvNjW$dkDNYC_cTxCGaK06#kgz4{GZlGba2Zjn8X*Ntx?{Ps69_Yg4t&24}%na_v=cHhhA{H#A-eu7zI`GxIEBKABheAg(>B42mXvxaPWSb-4&W3yS_MI0!z77{bSq=U7bmP;e?-a+RFdf>*-FanA&7EYBe(e2p?TmfT)~565>Xd=U9xf{o(&M{)fkY&iQcoO|uQ2=Buj&ok$%tmjJb4fsm<Qg97?4fhI{=azk%1j;>=SdU4}Hx%9n6rVoeQn=Vs-k+t!7v54^D{aj%;Z4CdaKX0lrtn6X@GP(cT(BcN3tk@+UJpDEF4zfP58eP1-VkgL7i<S_2ycuDZvvhR7i<l00&k89Z=tQOwz#%$l)<l+;gaWGG{LXo)wEUB_L(x6R)$wYYXk07`RgaRi?Qg!YiV9n+dq`SFO}hPZI3eJJ!rz)5~C*gCA=2vUK4B^%h%=J4&WY@zds##CPC4KSJJ$qwvUy;W6JPKyek#KX7E;w-%-Ydzpae5B#vMu_%^N`13!jKylu?64NZ7CZDq9`Q3eky!^`n5mIWKZn=#(TT*9|1V@-+El(@n-bL}vA1TOJ5Gv{VB;kC8Z(e{-x_)lf{K5e^|8Sh3DF7NF=eD|T%Ax?W@wdeh|y4>3y+^zE8cft1<i!Qvn<~6i^t_*&m43}#=lo{_p6W)#(HNY?6)%i|pfbC-Wy4-s%xI^WCPlE3<7F~E{&8ukpL>c^487|khD>L4XCcHH<s(_!uEAw4e0b9rNb-A|%xE<aczqc5RF1)<v6|{Y%3?5a6%e5`ajJKc(Z%&K~;8D25X+o?f%x87Ew+Xlf-Wb0WW6_15qj?!^A1H$#D#PX4MrFnu(S$c9Mj7x!xWs8ltcJ{Ib-A}8xDnm}zYUB<7hY2HQrZqEg9nx2a&5gb<Mn958xW%ucn~ge>Jh6R^I2W)tp~1$*T?To#-a;9Tl3P|-d6?>DZ}gITN*qB7ym5o$s(@sMvUd#6%)Qm8OtJm7Wco;+?$BIi8+PK`6lODRWJ>gb6(Ezs$eU){2Y;=XK}D2yc1(N1H^>ySH^^Y1J;G_<=WTaH}KEMVJGkYyS&S9!MA`r;DYbLx4=`_d%PclyWzXZZzHykcVPp3J-8pfpIp~tds)jj;hVrcaKT+Fe=l~a{5=xB72FAzpAmA7zXNWCZ^h>wFb!|7t*y3>;JNUQ@bkb{@blp3gRSA`!#ja(;GN(dFyZaA&C&K3ZL=`px#0D1!5iSY@adTFY2eLp!CT<d;8$b9r+~M@1(Wb8@M|#PQ^A|yf;Yma!e?N@XM%I#g4e-k!e?W`uhlkATeh|=upxXLcs*DqV?6}Rf@R=0fLDP{;1j^6U=#QR@Mf?=#`+0X1S`NNYn!C4CD;Nk*D5ovjMjoU74fZzHi<a5!f(aT>MhY)63gz7U?s3JJV)C^ZOy>uaJg2Vae1`n#HoaDCA5jexe0y~epYXW){Izo{{_o|<>5Di<H5%8E5Sx!W4QR7!}uID;g@T>LR)>X0sL%jr5Kk&6Mh}nt^garCC;_*Yw@#seYE<-5<VL&36_G(x7r3SSPVW|+Zb(iz&N}lK5?)Pd^Xp{fN{9QnF*hXpVjN2)ghMf8Q@u9G5Bz8Bec~3Yr^GPVaA2gY7*xxe9uA~L7b`ZsrXsF23ieb3BLv`1Qv!5(Kb|D6|gE?t|`U}ttxQ};ado8C~>C1r{HJxDri-RCH!hI1}gY4ZI^1R4pxK9wIYm*pj9JI4Br^qrNo&ApN5~+tD{vXmhkCdQLqSnl(v!DYJ;`la;-Sy;%K#qQxxB#Xd{V}3(v*R>b22o6HE9kumo5fewnth+UkLI;c~4s<I-q#iBkgK5@=(IGY38gKdaY6t4A#1gZjn_RV@5J{jUo0|0QJ;y#H}Qc&GoLOEd3Wt7EzUcsi(WQF-6>OI9fQfL0`A^dF|7F`f'

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
