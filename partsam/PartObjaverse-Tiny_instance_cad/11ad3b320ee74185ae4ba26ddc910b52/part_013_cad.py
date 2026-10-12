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

PART_NAME = 'part_013'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/11ad3b320ee74185ae4ba26ddc910b52/part_013.stl', 'relative_path': '11ad3b320ee74185ae4ba26ddc910b52/part_013.stl', 'source_sha256': '2ddeabaf37e635dd203f5b3080c931232b1d003bc0771dbb72fa66e70806a484', 'input_faces': 556, 'input_vertices': 325, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.12061205506324768, -0.38311052322387695, -0.27019649744033813], [0.052943747490644455, 0.4999995231628418, 0.4538463354110718]]}
GEOMETRY_BASE85 = 'c$}r137Af0|Hp6H61@>636GM=(jrR}gJUZ-XlP^!vs>cTFqRbc$X02g2_f}Z$I_q-W1TsS*^I#$%piHjM2acvAWi+B-|zmObDsOodtLwQedoH)_4%Byd+z5x=ef6Y<`NQIzCtY_e;SIwFP;v&Szib`s)<@+Ld@84BcfvBo*ErHshp_JIsI6S@71?w$bfQUf_Nt&Iwme^Y(QIAK+w>@fab1%p>K{IH#TB)*qdXcV<>+iVpLp=FOM4@5gX$>f1>5Ht(&`AHfipf;`%Rt?(sFjJ=&X+N^Qx^+|khoPrE~V`TU8TokaJxu6rmCe}6<eotr}^Z|A&yE0c1gTMv`-!=+m}Us@%da@T#iyZQVrugu$>$)H@sEz98Y>z8if&$&M{o9n4GAdSzbkKfGYXRP4Q^@JXizaJlz#5}krlX7qQ-P}G`)8bA1do!Ela6O}PGWk3;_IoaWJMsY66aNyo-xEEMbJ2g%el8y|QMSKQ-Ugx(@XR5uzfCB&Q~c4Cb2E4?=bp6WJzQ_%3+wpbYtGxt*Bja?fy-rYTFbn&F^_Vy-Tiz&&F%p*uhf)t&*C_4r%@?uHP<(FGv5buZ`npZuQ_2A^UF<#`MwoR<o3JkmzVk6OujC6<aBu-`<+@LfA487A09h3i}S7fmh<N(xnw=Po22r2#nh$D>KpR8{LE8)y~h0eId^Yu&AC~#viu%LbXvmo73`3?u^^kzm(~4>>lx7X2-lOED(_GHphcX2u$FUAR#29_p0DRK=Y<^Q@_$d2{cXn(&c&9^T;8m+WFNODW!7A-XVh0*-cxA>f38s)F^9`n?|zK$!-8G%`&!*%8nbze0{$Ln43PIBuJIx+clefU=fIceDEaXeuE&V2x5hs=ym5uxo)c|1E9KACIKlt^SK|~VzqsHe=X2MjDfL{be2Uw%e6Z3U^TyC0Ip6YlF6H5IZDjsV!2vFpGmPuA^Wk;*zL@FNPWb2IwFvGXhWTxwQohSdQ{LY`1xopdjAX87vpA;YZwDoEzG2o8C6D}a9@oFNcD|DLzw|M4#V2`6KB4&r9v9CQaX)p9n;`RH%eFHcPu!>EUHa{2K6E=n$zL7J^NDfK!Zan1Y$xZ9KkqU9bN865Jgz+_6Spem&F*qs@2v72mm4=z=4IPYGtZVCqU-aHn=k9h-p%91=vBIq@8hIni@Dy6C3$>54<-D-<tESkO19&3uE#iAlmFey-DO_R&7aP5{bI^|ndj~0`|FBn8t<PQ`OUbW8=h9PmGXrj$o@HD##*KPiOZaOM&>3c`RO3;2kuk9ZuZYbQ3B_#!ud)5xq0^ZasK{9PKr{`&o6R6bKm}Gms0-1AlWZJzmcZ2v*ZBhVorpT8<%tVeu<SUvy}X5M>#H*)mCz|w22%S$s==>`fqw<zPWfm_tVL%<aJG{caZz%zGnRSR&Kt%fX9)U<56<)Mi`GHk$&j7k`F)5^NTy9+X?^N=$9bJS88mblJ{*W^WA5a+}*WAj=Sv-7AWoM93|JA9Um#VJ8B@Wb7oTdQ6&%SAjj#Jz+*}~-yOA{>)+7hh>}le^eva)xJ%97xVeDax#rYiCGX!~_P=#K^Od}N^$(cKL-Uk8Fl&zd9@Er3_F^LU!`5#eQ1YOr8~Hpi_#j`;lnj|iSK@gfyiwJCN<N|u??b`^PN{k4iabArKR7o-$-6G++*4<8rjqxm%=3o#?v`mv9-1igs<+fU;&c|*U)np>KX*rc#`BD)Y^bS}kDbT!j9GX&St&oZXD*MgA0xIY<x^|({9|nIy-_J|PT<^3-Ny5h@$NZUK6{Q_ue-Ea;Getq{l>YwAI6V+!V)f*b(7~E^H2egGuPBDGSA$?xpD9<B{wo=pnSfZ$7W=F&3RUp!(9GQvXYyb=Vd*4*Jb`<yyuSPk?ZZT^8ZwiJ2PL-n+H0p<<p1BJg@30nJ<?4lzwu&XJ0?zpNqF&m*ahZ;YlSQxloSxy^D_f=f<!la=d50tJLG}Uo7`qDQydtJhWKuSN7CX>T!1q;C+&@&3jDAJ3TJP`_8lir9DFr@OT$VpB+{5!FzZ=XC%ie^@wSqybl%YA3UPuV_NY()cmeg&BtXe<o2&lIIQG-hRglbx|#V(9vC~F@5i$Gc}gC%`g6YDEB{pUQ5AT+ds~)2pyVA_$?@KH*FhzZn$P1Q{L$sv>i4pq$Gg!aI7i7l<??v*)@qWW-sjUi-n|d!WGdx*ALM;_c;)OpO8LIO@Oby!J8Z8~K0JZPyK!Y|ijv1<%l7?!#8mP(2g~P$qYaalJZ=_`cX!eA+m(FE4ZeQQ=<*wserv|_cz31E{a$Hj);Kxd+f@2ODZj5Oe@{mAxo?zyo0lN>)p3jDe%dOZ{}T5nF}>Dw|6CM~l>KRP`)`%<C#rM5bVZk~RLY;O&;8!(mHp9fXHh!mo+ICH^3RR4J9s>Z3JIx7J?CS1T#1{jb}HpBbd>w#FJks8?I|gd`-)FX_9*pSPULyPv#Msc(w?hBcwTTVU74xWUs{d#37%~Qxk`R3g>zTZnEguqe~y#;w{tJ&DY>>kwDZ6ImixNm4V-(rpXA(IG`Wz^^Aopl`(CQMROat-?madsS<NTO@`uiD=63Z+<6NItt^6PJXODc&#hIyGPx$dCxBBO1(M0*VxleNaMz7#yTwYrjtXy9g%wAElyf&YUkWDhz)+sC3*D3ESJ7jrn-M4dX-M4dX-M4dX-M4dX-M4dX-M4dX-M4am-M7nY>%LuHTlekq+PZI-*VcV^NWLtu?PIN6-^beJwSBCeYx`I$*Y~k@uI*#3T;Ipq?a}tJc6n_dYv<ZN)^4Y^kF|4cAM0GNx{tMUZ69mr+CJ9KwSBCeYx`I`*Y>fVkdyMdwC6Z0*Pr9;^4fEpU0!>Rvvch^&dT-YI4jqm<Lr90=Qz8(_8e!oQ+tlH>(QR$>|A?}v+LKM<Lvsi=Qz6_?K#>muRTY*df%4!;mkBSf1cbepZAfQMdLX)a+V}<xjrqI^ZnJH-$m#S&W)^a?oZy*d2;_Bn$NlZ9>5cN66M2W|GQa|s^$@LKD_?ClK*2J2`!en_CCbUwf7-*uDuVjbM1YImFw?A?DE?C5TkGT6@1^c_fB@My?3&5{k@Z2UVHCkm)G7q*}3-K$<DR+PIj)ncd~Q+y;I++oa^uX>|A^AXXW~PKfAp4-p|gp_kMOg+Iv4M*Wdej`!<v9&l)28;h**8x?|^&vR_>*;r*)TwJ4dNna=%OoT|6YKR1iU$#p-w6Ze0!-*VZW)JNt1^SAN4xc+|YQ2$`rpUZ+wHIL%lb2TwV*0V|GsSRa4zbEeU&#n5yOFD7x>0gZUF3#PTjw`v5`k3s87i-9R2DDtMmM@p$pBt%-I2RX7cJk*B>>|q-*O%+x^}ea{dk&U))*#vbvOcDo%j<GqnUSL8#qzn%dwq;r59+tZwK;I4Qr=bip^}?t8gTBpUQgEZdc1O7=A}9*{<(Es=7pm>mGY?HxUod3$Ex3btqSL^L1}9HOV=p5Ro;88j6c^q==Mtg{$rkMzs*0__pw%P7RAYVHM?PwQV*`nxZF^w{~!I$&gJ!nU(DU9)PwIUysW>el-K5GCy$ozv#yL+ugm&gZX~9vx!O<c>$1MDYqw-QgIlh;)BUt^{eF6eM6J5h_iN?)_iLBezF#ZXzh5J4wo=~eZ&t4NH+R@_wf*SNPOkQ6PuRLucN#BFu8tQw*Y2kgo~GOfYy4WdK7PX^Y9^@V<@{jf`ut!-c0qY{{;_g>{&7VH%ktX%=H%-9W<<WK)MNEqBWiYn|9G+HTPxS+TUT@r>R0D;Cs*h5@R+)*Wq(%p6;7`1E5y)ttM522hTmQ-+o|r0tX$t0h5x(mT3KFwezbD^`OzJFlJkE&&)T{AJR3fy?mC(K%_kwsU(G*$@5hum5BqkSzN3n$C5A@${mGm{`muQDKbenc_5b>ldF$3~{?|X5@AkFfZQqdwPKKw!)4_M)>F`X@4bOyUgYUz$;W^-Rcn*96I1|1B{vG%M{5$w2@FVyp_-629_-1%A_$fRYz73oM-v&<vKZhs6bHOj*x$uMFeE30l9{43Z51tP$g6G4Jf?vUp!VAE!;RW#HzT+h50l$Wy1b+gT!heGQ04{@%@g3`YM;y2l9tR%}rohL;CxRw?B773K2R;e@4!9To4txrj0iObY56ptU2cHV=gHMG|1NXzH!DoOQ;WOZ~!0+L+;2(lX@E>rmPJrLQPrwVoCGbM{F>o>b82kvh5Pk%H7+e593_k?UgCBw)0OR2Y;OoJ;@b&QR;Aimd@U7q{@U8GI;B5G8+>b3_5`4Jt80kAkga7t(`nM6_b8uo~_y~A+FaX{i{xbLk{AG9#unD{eycgIM-U}WAHiL)2`+&{iec++slkiaZYv5Dx*WmrZr{VqK1HotD1L1?f7VtsvA>gy{A@FdpB|ID+3ATbq!lS`9@M!o@umOB1ye;U0w}l6R4dFrX4&bBk4sZi}3~s<XgN@*w;a$PU;a%Y`_>MrZHTXC@5cGgc;otg>RlegixE6jIegWJ8zW~1o?t)*0mw>7868LZ6ZuoET-@!Ea@9;}tI-KTbnv0Kvf54B!3&2~#ne)kyf;WY;Mv&)&H-xjMkmrG=!dZjJ4}#Z)vu2U!g4cwz#*rt2MZ#GV$+v;O3TF)^PX>Px&YDZU89XnXHJW@A__J`<bn@@ObHdpJkZ%Cb3TMwio&#PL&K`q28@wW%JqdXxco}{f-%lo(4yQgweeZc3<S&Aa;4i|vfsetv!MlKu!n?pbfeqoE;2l91yd%6l*Z|%h-VSU7ZwDU+wt^3X$AB&2G4LqxS$GsY0&D?~fQNz4z{B8!!KdMa;je>F!C!|D0H1^pfcFEN!~4Peg3aK4;je;C;jhAbgH7PQ;je&Cz+Zv)1Ownb;lW^Icrg4W@Hsf~4Y)_hy;&d*@)y9b;4i?tf{TPRACh+lzZA~=Np67ig)`rhcL2W-&iqUs1b!}@`JB8hI7c}1KlxDbQ{k)^<k8^A!dYL)Bf*b^vmTL$gC7WI{URR%&J@miM?MIgE}Zp|d?5I~aMn}u{-9ep>o56h;Jd<EugOEf$--IR$@_qB3uiw-9s<54oc#lNFK~iz_8a6qz;VLapOC){jup;+hP*o%3nz|%Q$M2qGzuIJPY`m=qdhzAQE5MF?eoe101M%Nz;A)a;J4s6!6WdS@EhP^_zid|cnDq!zYZRNUx!}<*Tb*Di@@#hBKWW1R`{>*U%)N!U*PA#B=~vw&*1m)pW)}gjqr2uv*3RCS@>0OAN(r(3YZ1I0>2Dqz%RoufqUVX;J<@=gtLDj{|z*Sv)>>u0aJvtKOw&e?i9{`hWrA!PB{A?^3&kAaN4(1-=lpzt$noSEd`hP`HMJT2LA@^2LA@W1ndG|0$&Vvf-i<I1UteP!WV$;;S1pNz;^I?@OW?-JRUw5jDgREe+EXuKZAb)M!-LT&j!Qbv*90tgW(^-XMwK^=XsNS1~@=C&!^<mz<$Dco+Y0O_7%?aFZp}mtHOC+CZ7WK7S8iE`8(h%!g(Gip9J<4&htC@L@-!5&->)#!Iy;det<j<d_y?z6UfJaqu|6h{d_piiKF2`<$Qg`ceDlRyerrq-WA>%YzOZQH^ArN2D}5<3f=+!9M}y09Q*;WF8l#_nUJgkr-S?yDByIEuLf@m>2#2<0MEczz?Xww_;UD4uo%7)z6Sggz6SmySgxG(AK`z2_rU2OuZ^r8yf!=#Yz_~EcLZC*JHk7GZQ<5;N#4|VH1Hiyf=%E7aLOLXIe9~zTTZMG)`Zu9Q+6-T$*bbra^l@!HTb{a4dBH4!CG(^oU%u8ZaJ|r_yoKuoU&(q$1}d84)_$D_!yk{5S(})oLC7?tN<t81t<P3q!Y^{Csu?LE5nJ^;lzjG#71!9({N%7__JUe9ONy*7I5lU)aM>4C;Jkelh?yJd2^hTx5hbnTbw_FI*L(GG5S5Z7h{9`48{-nZHzH;Vih>CE}Ym5PHY7yJ`X3hgA?1si9zrnw3VFt^n>M`{!ea=5pruBky~Sp+!~MM)|e%?#x=P$_Q|dJf!vxy$gO#X+?tEXt@(=Fn$yUwd5_$h8_BKtliZqP$-97^;FW2vpnisfydn<rDquA@@n7&N@Txe-?*nVVi4VZ<gV)4CUK^|fuM0i`)`8at>w$IPb@2Q3aF9QYgZv?|2D}E^_Ye;92XT<s0;|ER;reUgAip06d3CTd{9dpUSQ%a!_qP%b^1E=5TR-Jxcjtq=0$34V5%;|U4)VKwM@VqFyK0sHPyYqf`EgUl%6|yee^dQ4nE!9KX&{_GiiHGMr0eiqz+JonC`V78;{O0@U<Wh'

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
