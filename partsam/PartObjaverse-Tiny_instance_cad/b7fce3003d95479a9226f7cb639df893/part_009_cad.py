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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7fce3003d95479a9226f7cb639df893/part_009.stl', 'relative_path': 'b7fce3003d95479a9226f7cb639df893/part_009.stl', 'source_sha256': '9fcd5541bfed9d6f5da6eb7398ea00e2f71c1ad97350e1a7335f2ca36f6b1f1f', 'input_faces': 342, 'input_vertices': 231, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.41735389828681946, -0.4999999403953552, -0.3863474726676941], [0.415873646736145, -0.1412997543811798, -0.0876365378499031]]}
GEOMETRY_BASE85 = 'c$}qL2~-qU+AS0fu5k-4AQl=ylmrD6m$;PCi3_NRy8+Xv7;z<lMva<6G;u*p#C>ffD!;*9BqB(u>>!}fqF}T&ZkdUr=8vO^Buu^UyFF7qXXcza|Ia!1+}pQbeeZkwt3Cw!*L7?q@t?aCP`z|T7iUQlXe_mo7KKGdhffcSdV7Av5(lXn`Qp#U38Ti344mvBEs{R-oDmi^J<_wU?AdQ-Z%=R8bLN7`=*ZCdA1#QS5hnZ(Lgz+>>3-C#(1<Yoa~EH~9^SH_m$$rJ{y+XT)Kicjr&eX@tQEN25^QR;@S0%jtP||l*4`FuZu~X*N|XI|zC3q@h5Yng_Hl|l*#EFM`KCiLHz`h%6UC9;d)WD=X?rWE{JKAG7~?CBEhvuc@xacPde@~mrh@bv#(L#3aTG`Hw#%-(Hc`G#d^^UjymHEid?|XFov-cPPW4LR@7*xwsmA?MPS4%_<GRt8dU;cMtM)hYtts`WeafR@R9>3@)ULcK>{ccDckbGiw>nf&{_3OB>vsJdyNSwMV?HNeS+=8^%0+JG_TG%N^UXoNT<`Nw?BZDG?dQ)khg~<eSN&it#n+B`aeqADL7(Mqk!2M3S$n(k+MmzTXLVIgrLnv^aYiXUH~klm*ZMqvKQ7@aegERGcIBl}0au74ODgU1bbE*5%g@hL8v9Lq>A;^a?q+V?lg3A~v?w$BQo3}_=xb*a$TtTRao)QuB}QLc6@Ja=OJ6Rrt5@E;irc?$v0c05LDkgHYW&PfyKy}5isG4@kLL1i=Te@^gWF|B-<+0jG5U(sztV0UMReeC^{HEFH}1}7c%2^I#(CcwM)9pdD=r&-t<hgBMqet8y=FI`^Q*YO{us{d`|<ZY-#bn$vGeauuo!)LWR1nx56XT1Y;`ZS82dqfR?6+{Tf*&J?ak}L>13(Vm%?7N7=3HfE{k!z<c6NbM&CAGHs3TX&SLBzWpr?*(YNKJoxW3M^lkaue5=b~^3{2c6vx{B7?;=lEXH|j8nwNM^6T@W!Z;62;p>WxzHJ`beCy4k3S+(2;C4KZ3SxL2hfd@CqqAvUsD5)Q?AGJ`LaJArKC;3%ugonDUN-u+d1dph%a4@X<sV%{`6wG5%Z>G#YaejA<t|t4`oZH}?#H#ex&H1$d450NSU}v&jeL2|b*kT5GK@Y;o?Q#6p1-B?Jm|WIKAY<L6d22EO`FiXGWqw(H<njthjP2j8F|Kfm4$6ec|E?XQMo5KIZn{l3p_s~vM3L)`Mf?uMqVQSwlDe8-d=p(9P35Cv~*1-ajHMZKbv@wo_9N+L2*-xIsP$!uCJsg`BFbVpVXp0)Go8{rgO%6O?#T>lAk^9oUvZ%$*UZy=gR@<#APeFKPSZ%7=0-@vE1lu7Z08_<|+LeMsZB@j(lhA2h&wI>MyzD=I`wC>=4ZTKhi&q;w|8FR1Wxafzel-+$)T}Hh9h%`u<!fud}C}s2`-FpHk^_b~w)qk7wNPwXx(&%UpQge)KTU=qoi&<wjo%_~W#(pB0}9YL_~$JNe3)k2%lpE%`>@dLg6S=qn8upQ7*YB+&epyR@Z#RO8m3H0H1QJfiV69dCNln7>?}LB8^`%?V@wsQoVG8GT#-*nF)z=eThkwXpYdjlOLh|KSfcA2W`N96pBPn7iydV)V^FZ|3oxI^r<-wVAXY%*h2b50r?AL&o-+T5h5IwI^TfH<nkr1kt!Cof0z!it^`NxxFiVD87_XFH`th-6~$Ut9aa{x&5<*Fa5PX<*nxa#N$$(NWL=g68Wa$Lo~0f9<4R<3w!YX;=Y0Bq2ERF%}2hV{Zz`|!t=0Z;RVXaD~#$@MkLVswH|)LevLQfFR!ZQeO1oBNcjYh=5@6xkk{#W*Gm+CYB#=5G)m%oNNIoaC7;$bKg`7$951b2Hs$%CisGssZFqc}xsfl;$)bHhIXR2#tsa|0`M76OIcb4~+qL}y`O1OGRG;+xHq~#s<dREq%GU7nX};Vp-^JuBmz}5|&A+Ad{bcE8E}s-g`=IjM9-hA&JLl239IB-8ur5?+U$#CBCtqn4$@xf6DZaArF8jCo@V@;1hkWj5-OQ)_a|TntN$xYb{~O<Czu-FeOMF9Ww^rD)fa;B$!{c4Mn#xN@za(GHucq><_CYq)`_%^WrK@B4+*<WUF0adU_M7kE`&MQh-cO=(InJkR>3KQkYZ`y6rIO3{OCjI7AcW74ZbJ&mFP=c-XiY2T@p%$TzPh-E_wfdAQyle72Kz4KsDISq(R`n|S5Cg>*opVwoEyA8u39+$s~nE+<jC#5_`e({|1)ZjwR-}^Q5_l-Q9lQ)<aJVCBUVrBC0}ZGg7Q~0s<@vnr;)F%$>e$yXLCNM9&-8Em(*|OypFsM=KWYq{^`k7UYq}j_Zipt67pXxp?RYo9LV$TtHGt@J123TC!W*%ky`yszVh@FUhm^1elF@(negSY3;BGB%i#H$>wSgdXa#(3R?VRGr6#W;UuiOl*L#Z;%FFs@0{L1_NA5REXP(zhx3K?KJkQrL@f`o;KJw+g4at}LKIHfw$2fk}2wqp2Lpc8aOwK3BmCvK27M^dZ1ss2PGL@6RU50(AkjwYJ%<I3_jnCa7CFHB8e&=)fjeLIYz585#!(aH`v*{4!X{vqgD*20NaeuxuhT|`FCtq1OlJb`p?WA+i8sDAEcMl=o<UEn%drl%>ebSA5^D{3#cbsQ&oIAmM9!&M(^Y@!*E<Yul=k4ILd>?4Nh<vNt0KVUawc+)Vw~XVo7{T|Cpd`ANnB`dVH5WhLH|m2US96~6&gDEF+j;-@+sJ;sI=r7O-NEN+$9)_pe+qpz-4Eh>TiqYYH^r>D%Ijz+<s;S9E2n%Wdvo5FWjtO@Tad3lxXI`5@wU`&n%g_%YqJjUJ}`eKv3cVA<eN9+eEfVOmtQ}M<9qzf^XKd#UQZ1_F6aJl!uO*6YiS&%giqPu`Xi6ysCe2ZtPdA+9JeF9zIxVjy{WO}%QG_g{4MK3{b{Y-%5j!o;dP$;nD@8RZQQQOcyEZv<NIgCd2ZLM`Mlr7@p&SJmvZ^v0{FZ!&7=7sWjCmx@`HjXuHqEI>)^?o<V$1Hc$`Wj_#BJ(;__SD@x5GbPV-z2?!kWAQ@%I+G>F@EuP^%pEPQWiR7mBOfYIcu9a`}|YwFJP{Kd!QD=S{{zEin_=S90{@=cTe#P_jh9r(VXC35+<qxt;Zp3Uv9J<RzZdW+vzm;cW9(cTw1pXx0<|FceFebsP2!CQI0B`xK8KWb~CIO~)6{@Hdjk8f&M_Wh>vc*Wx!%oxjluP}c9*}><RT4y}@YC>OrFRR&0{b0&lO}>&D!SA^{+R?bnWjop5h4<~D>-gTg^f1SnG>7kpPnVsi=Pp%o`IU)0A2z%sU)wVE8nt(NF3kh=k%`aQDI3X`(tLRyr0pf&)Z{dmf9%QY;>r~s$LXo$E3VGm?^i0Qz2*t`IL@HWyuTzj<^8kr1^KG`WIm6oe&_d>F+P>#Piw&YNYnPb@AcV9zIHo+_sOpHX}qj{2e`ar7s}5(#me(5`5~8Y!1n~x^aean7uB$z<i`8<<OTHpV0G_so$~j0;rteO@;N)#n|$dPe(#cceNA~PUc<;Y4LQ!|(Vlzso+c08MZT7+a=$F*{H?zp=J-x4xn9>m8b?!H5yx-$nBvPrKjeN(e@ea@c$fP*G@k44?|Osc+&snmMb>WK-yGe^*HZX>((F^r@mBUEUyU7Lw-3v=?vO8acBJ#yG`Ju4^S!5BejV@2>WFfhhib~6DvICjSKdDdR%ls)cE2+FzckmZX(mYm4Ww4m%uvHm%)%6ZHvacNF^Bj3uYO|o>*@Rd{fT*z$U!U@@Mh?x(96J^pqD`}))58%3cLyWE9jGe(3ilQp)WxffD@n#pmV`rL+3)LgTI7Mhfdb9S4XUl{it_8a@h~xmRl@xkAhyHV?I~~$3n*<t_n_uPDZ^#-_&tU$1U&;=u91XI<mpV(8c&Z8+-#g8#)tw4LTD#4}23k54sq93p!tin41^DXP|fJIILp}cpvmWe7^;J2Ko%1*@8Gb3|<yuWTC#pKtAH-BbLyWI<D%t4z7Sct|LRoY48Q;3;6ytxB~h#^l|W2=;P2C;7aHW=nLTM&{aAtI_`k0p?}bEPse@m1Lz0%{yw-G`abjzU<<Sb&;NkB?!l`<tb2&_0NxTE3w5jngkA**{TU$iCxFm%0HJ3CLPvm?Ku7BMRL5LE=y`z9(SXn^0HHSkLazseUJj0gj>a>#+*Tmp6?op3{|2;a17g|QxE}3Zk9f9zSdKP)f_B>SoP*rwpv|_n%trfWqusXl+WH^@@gl*?p%3ba*Kt6{Mrh$})3Ha#7vMF}t97i?5d#SQIXDhl@LK3^btLLY0fhb^@GfY<+o2C2hdtmm&?(64TkrwsZ=n;xdknD?(T+s;+mPEjv~?qNJg^S+twTH40ISh<Tl-`1>_NnfgI)_xflfi2)}rn&kk>Bg?cf;b81$LYB|3_9Tm~0HpV0B0j$`0c(3iodP}b-b;<-Y^Isp_RMiJ`!4k$sK62uVtu8!L}tl;mV%XF0MC<R}EzJl*d!QVrdLYIMWLzh99gYQC@Ltg<~p%3XW>(~w63jK|aBRY11lc1CE{Z8;!=$+8tfX&d~Kpz1gf<6MB1l|p;={Tz+4SW>(yp9|lso-<a=kR?h_$YKL^m*`E==0DyU=2D4`W!e7dWw!2Izj-Ur-5fePlFBvgboEyhYp1f22X|#h8_<NgdPt)4m=WC@EGWE&=bH@pr;_$2|$RUe25`_h#`j%L!KdMM+n*`w3iNF9o~S@eZak-`#|>tgzgRQ0o@zA8@LN}H|X}@4$$qPoxyFO1<TOR&~9KaXfNdI1_<355V||K4|I3v0pNbn1E2>2LiY#vhVBpT1MUXx1N|nrJ@lK<?ZD2^&d9YLxHGhjHhY0PKzBfYd4YRC_dvgUfqkJT>i9^<$AHk`;18k0p=W_dL(hUXfk!}_peG^bRMayOIsiNgdJ@VDJw(R`I{X2lgTO<fgP_NP{{%f2dK7pt^eE`zh&c@P41s<hJREvB$_xF54p$wG0HK@cXaV*FyF&YcyMkSzyFz<_-+=ajb^(NL4ha1kxDoVg(DebKoxn|?ouC^Va%~I<-4f5%K|H|@hWHMs-v!(X5V`@_0b2Y&k@$NZ><IljbSFS)@p{@6To3FBT@Si0Sc0w#T?dd*w*zzoa6@QYPPUwdZVi4Nx;3;rxD&KH^xHc6g5Lsng6@R8-vWg0XlPqUK<KtQ21(-oJ9u9BL3;uU#zXLX&@G@_g5QM}+!I>#Lw)p(U?)RgIiW8FH->JE=WPAl68W`6%%(t3<Sh6d=vL@2+x!&T1MDvSa}En_o9FImYoNbFomO@K)4$67^G~J0H2&k<zdmXI^M~=tnR={${1_7GUr+Rh-a&Qfg6}1IS^7Jn-Rhb'

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
