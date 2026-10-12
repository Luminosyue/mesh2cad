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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/a45db53fa2fc4e94955e59aed66aa0c3/part_009.stl', 'relative_path': 'a45db53fa2fc4e94955e59aed66aa0c3/part_009.stl', 'source_sha256': '24bad5d7610e65ac91d76e959ef6b53531e0ee531118d4cece1a00bddb725eb8', 'input_faces': 416, 'input_vertices': 337, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.31441715359687805, -0.4309016168117523, -0.490466833114624], [0.31439125537872314, 0.49997678399086, 0.23695585131645203]]}
GEOMETRY_BASE85 = 'c$}r133v`y-^M4_)>f3-8L=c0g2ujOs$Pm(>ZPQLiJfW?`&L6mRBf@g5<2#Xh>#%mr?w!1SQ;dFYHN|&Th;Z;x&OB>$@KlM>$|?sb)DY7xt}v<&Ybzr*(UAUF>k(7n*6J(RcL<RtE{eRDizU6Y2yclj2$*$&=|kqQIkBh;_%hKSGuHgk4{|!J+$%K6t97U#taDYYNmU&7~I6Gw(d1}WXRZ%px}NZLk12~e%qiCV+LjUV}=He8kBYH?eE{Xw(jp!Tc4)?AO97~s)9bO%Ed!jYHaQU)wI;9(BR5Aw)TE`0mtzz!jNxk3GrWaxun#!Fkn57PZfr5uUaDIoN6AWR3Ds)^Nkh0P}}Ss8KC@69^hE-mmm4vul({S;9Gb0e}{5zdT+<^lmw|q$#U?m*In^AFT)nUl938ObJ*87z7#Cw6zU-LxnCnLAct=>xOfi!)|)Hg8-Y@v$f1{Up10R-++X{iQcmy?sCls7cGNSah2$UoT^h>S*lsWK`TlYq`dQ(txXurS_TzYT0(>pa6YXa8PTZ}^F<x6Pey`H$xZda&htN*#zJRY+d2j{C4-UC-zYqPT{Gr27<GkPNY(%}<dcrrX0m=Bi>MzSx`L4c|r2I`Ir2LnGhf!YlO443IB~VY-#9PO4e!0VF7xVTK<kxF0NW$^4Po%vX=1r3J30s2lhj$RaR`U}mr+P{Z&TCv1zU%p2sZSk`gD7X8-x=f|S5&SWrl;V(GQWUo&lcgjTE$cxyNXs6ZRB?Z{_-mG@w_~z;r@+vGmgUlbo>rnC(lk?&#1W$^|7K-alft&$4<dds&G#HSRC8EnnATP{n5TwmmY~YZk8tJm(RQ+adsW;W$WYM8-Y`$o*n;yZ^rLWlIQUN_h;?jhU*w<Go-yDGLPYSXm?!C3e?~mpQfXHv(ssb<Jf(84w}c^4Y<$h4MrgUkK5qup<{4ed+8I2zekhdTkXaj!t<EFWusDiTPUt)Z9cpo<-GB9CeABA3cmJq^-|?qWtZZ9UB}Bw{W5Eu#Q8ORzgB8)-HrCO&Lp9p*2sZ)|7?4<_(4Z^q5RB-(r)RK;k)dCN$@+)Tq<$=srY+`rb~Q|mG}6;yYTJjo4!N+`^VsU8Od+KH$x9!Mm-lymGZybk2ugj=$R_lefbgUxjIqe!`pKL@~<C*cCl-&g74Z<1<y_Q&nxf$lwR=7{WmWnf7hNT;oofy-w0bH?eNq;N~wFGkCaoYunX6V%NvjPcVZ3rR!A503+~a|(2lN3`K0`e*fizqU$v4ro&Fg2r@y>;71zDEelz@yKf*WD?_R-u%?RBG-<~P)YxVsW`Rz1m_vbC)y8}*LLjIIuh<h{o&bKIktbYdlqvf_q`=5bt<e!84(yok(M!n`Hek<{GTiSE<jup6%-BaLOy+<Ri+~=0<K>n6>q?~7w^1dX;rb>J6!LeC&H{wJuTL$m9y>lyktwo!yxDU_9ct4DZv*EkGHxUnJ#2<3rPr=g9*$H?qu6u>?9@%aBz_))$yMT88Jn$@zx3v@B_c-cr8_QPV_YfVv5#^8jwWcR*hVCjU^(nsMQ<UFpA^H(l!Z!4~?&O2lkWag?66N}QCH?XBL}|}7_dMKphg$HpA)jr-^~^(PfBS4Y`Z?F+j}U+ER>6pKS7aIZR$F;bt>aPB{}f(%0Di_%+`lpKX)@Zm;sE$AuiJQ!tb7fn|9aXOz8?5Rs$AC#_p9Gqjd4bgi$^?I4-bW-zP)Dd!F38Whi}xsy$G6?g7?X6{X5#(DAXL!(d}9d-}+%L#x>gtJB{*(+{Acjzn6X;<<Ggg80Vij1K%3e9`$k$H1U49{$2=Q?{6ah&4eiQCwkxZ;-^O8IodUbN&FmY2wz)q81n|xlyOMw5w{D!kKHK!&$vR@aJ(yWSI+p+qE2T(lLo=JLp9V>%M6-?=X}2wd@ZtSDE#|dB!2Su+=+5q_LBL*zUdO5kG$Z!*Ce7}vL?nXL;XY7CLn)Y_(7DLF<!>42Giji<>#fqU-kif>sD|0uCjNI!;h5l%!>ELyvA&n7yX;-*Q4vv9{C2uqJ8eSLAx0@j;ukw8s9@d;ojUy-uHHY%D7YibMb$!iT6z_Q{W8hne?Z$<J++}kiW=Zvym_DIDFUjXL!EW;ytLZdr4FHc0@d$i`A%s%o}d{NdEJ4WZt*A6Y{_EweOcnKeca`{64J^d}FAGj8AFBCBJcN6UrGdNa|heJmSh&Z~?x4P395yqOQ4o>&{#}Cv8?0_^z%o;z#_5{?$%;hPZg;Yu9ecd}#P#&Tqy^`IAy59@1VeMmujCB>BURNx%Qgeu<yzou&MsM#<7n-iSBrZcXu9Y?1i*_N2t&i$}Pg<@K4g=W9={<Gej5;Ojn{<$d@#2EH~p1im{XNXEfwt;C-{9KM!Wc^=-EGO1_}J)u8*J8Z4oXO&RocSrh5IrVCv$Mdc+MCKb6r*A-hukdqtj!hyZ&Rdp%Z}hz-?OQjm_+!t@{QclZ63=Bu!gt@>3*Sf%MBG}79^t;tLY*Z4Pebs&7}2}nyC)1@i{EGUmUzzi4&#fqDPlG5W9EFsvsKY&6Yj58^#=#l@0a_d9gM-zxUW~fb<J1ihvD7N<jik|+tLm%pXJK0&C7>*yL(H8T=`v<ESaC59dILOexv(Z#H;JG11UN4TjgV9esJ42SAN&+3bKAVIXQR!bW8fL%8hdQ#=?)}`K3mm&gD0Xm3TfgA(!tOuukIYTHoCFwYav#;kvWea@BwRA;hgUbZjnPJ3dk7FNxt-bG7I8e0WdIjIx(<<$o9>ao4Bz`CNYY;tTP-qRXe|DreB=(oY8Zoz3Mht&8|EPM0{BtDbB85I<V$mAUd8BV%y?R>-1UzPV;1;?^vmCs#RcyENk5-D^=U-=4Hr<^yGdbJgGed9;jorJCpR%?Dc$hpt1HqjI*tes!9}?S+h(oWA?dO6Wh0<H29$^zGGuOTW5Dv(SDE)~^ouPjUWW_}YN~@Lss5eSrSn`5u|GcEfkRclsM=CBNf6H7*y$I^iGh^`g(=JNp5nL=&tJoc)H~xu2{X9Q}-?jfC&)m(1?R;5+*_S9m6TXMd>AsD}1%_Mg_l4&podTcbmN`2Xmi{}>J5*`FH^qNE(hxbVt%jtegDbCTaNzStg@rF_SDWG4Io-#LD1WeXyXoa3F<!w<f5+<fIb$4%3(5q#(PYlR$<avbBe-7F90v;P?1*N4G(&Ihb5KZ);{Kj`1|i^csq<{QROb+Dds&QII{d$A61AHFAkL?h(4ubjhr$X?J#);0aM;JLW!eUt!o%zupF8StI+CG)%u-#NdsV$<Q93vVHwwa{v^kKj{lC+g#vr@6cJfbX2wxu;t2?dP8${<YmR@%;5BKC+H=%n#jOrug^XlJ=VL5c6}FHWa>do@uO&h5wKF>a)~c@?6*Bx!Nl#NL=-NBIQqcDf=f!dgHlSXNzEeNc&aRdwNKN%hGPT_<m6`POb4k`FcBV*-xsPfpvo3tB9<tUN)Bej(N3tK0xx{sf75`liSGr>fpQZUC}3`Kf3=|_Kj9_gzucU+q1gBH)~Hre7e5xE%)1Lf#i40|E<y~@SW=gea&t7&h>>}Y*iwT9qSRT#5wrR^^0|L(;htkwha)U#ue!w%rF=BLF|;yvcB#bW8n8;K?iWZK9401ee1}&tj8en9qTVG@GJPv^_r`9GJJQhyy+-^!}Zzn+<v1k>owPDS*L3o4kEry|KAXYMvG;#4m~<s)`w$GO8ZX#{1oavemQ*SI@IkEE9-N|x>bwphJ6a_<WI6M7&l4E3F-^~AM5BhgW)^Z-C6II>~}cU^~P%bTWR-McrIp-R`A{bN`Y_2_rtnZ&)@Kr#LaE^&V32jd)i_6m6ymkRX0rbNdoe~ca^Dv^WB~w%6s7Xn&j^mf#+ys{)Kt1D_=4AR{lD&&i?fz`WwAMOZd)x676{#_-4H%w7*&KnCzDwpCQ+E?6(;6=1V#M_K|q==`H)Bk7FeNmHLPuBYB;ypNn4=|KViWZ`_%F0_}eK2f40epU2wpNbbwAFJv{#e+2oR`$*qZhwt2XGWAyQ^|w={Ki^OU>t6k<Kq<$u-=)<V3Ey~s<WcyQ!m$oFs*Q&4J~>hDxBhV1?>Ib5{EIixo_4)X*bg%6t(EJRt1tcPr(fW{+(&oAca<wD<8HJ0Xa{TG9{A4vI`htL$sd;@@0Vv?Jb&$JY1GfTAE=jn7rt}<&|dN}e9bFf#>s2nNPiJH6uwbAM#hy>Yw&*SzfOVg+_$t2gh{(N_Br)aiQ+r<Ma`)v<hl>4NjnalEbS8aM9Pm^A^q6qUa~LrjrTF+uU<U@?OPxK@3Y>j1$^VuZh3zP&qTe<cScHn$NsH#dNzFLey_V`l$3LDfsDIr(q%qgr<mx5zoH}_s-XXMuk_{bLuLK9xdir)TxMe#zn|@qecJ+mOFUoPEBPJ!)$UXKW&YZ4i=2NYN#g$K6Upz&hx>I$mqY((jQ7C(Irqce7kY?aYrC{t+$`BAZ<U^u^ZB|WDq|jFG`J@I;ylZcPm8LL`wFj*`s!Ai%x|mu%5nH<iN{f^<vYZqaEb2^FN^Qk|F;IbF8im=(iWk8_6^=4=Qopm#yNiSy=X!l?$h0{t>oX7EcIX7P5Sj0dnA9|G5BtwZM-}X$47h-?^c5=@OA&Hn6H@Qn#+6O_)ejh>LPycBGM06>4W>XXB5P^r1^h|{?P86Df5qnWbp?~lkZX+Gz;ypB31krcW}Sj^Ai#`@0XHw#pO5U`@@M*c#qtzJ`>;h{iWamnMaH+DD$fC7ax}AQbER7$9Ei8%~0t#$EHZTZET6_y3>;+|KFj~ZfX8fpUZVIpLKpevZF`Hy8rN>^1Sjckp8jtPVp0emwkZukH|Ws-LA7J->(JwLG#%liT{wdW&LRumHF1~W2nFOelr=LB9i2LVv~x}fBn^7=A(}9U-rL8i0}AbrdOT--ws$U`!yfj!1${DSP}Dse|(SI8wlU5Sq}Bl%)994^;P|3zx(V{`JQ;KH_9>W#WK%0{|NI5J3R&Q;|g0L<xlM|`+61gWB%d3=qd9L$9F?*raye=cSd{ka9M}<eFyb1L#|5y-*~+A`!71lzDj&F=3%a@b7Y<A_>O7(vJ1W|zN)+rbwja!FlVPoeV)vge#Sis<BoZ*2Ied7WkIr@YV@(}Yxiym-}xO@yY`{1qa5FDjiJFZ?{R$p)qSSG*X~-f?wZj8`?LBeTYTsD<w85fcYKewUOtfW9pAg%eF|e7b$%bW{-`YDanA4TU32|a!H&7Bn`-JXE4`lepTR*n{-i*Am5=(L|D<48ga6f^6f~&c=>PjC1@%2NtzK60&Ps`z+8)ugOIhh5HG{f`oI&27m4;`fIaz5gbw7DO^UP&ZJdc`4o=2Xal@?HUQxnO%$!DpT$Y;s-a@19EJ`d3n)Q4oHWjuscQe2JdP4;FxRAW-?M{P#-BR8bBA}ck>4arTZ?~s)?AvY!0rPd+WCD)>Qk(JgU*CN-<O694Z)EZ<@a%JjU<jUld)cj<ne`>-d$wjEYkX2Hwc}P<Hguj1JR_Z1{AwQ<xCO;<s%%u1Q^$z(p57EDQe24ru`9Ad&`93)<EA693Q%{kVCXu7bo2kdho5@ksqvR;^M(T0$M)D>m#T%$6$s5Qq)MRoDIe~hStn?~5fxMTRO5RJ3r=BCnlebeZkhhcLsNa#}$lIvr$=k?Vsh7!H$+1j|w=gL_L;Z<-hMY-#!$UZeT$D+11!_fd1#(qtb#hhm+tdc+x5>?^Eyzk+lbe&<Fe!eI+Lrttxf8V=xf8hywIf;S`{XX<uG9|XuH?>4irZ8FMQ%@iml{BRm)w%tnB0=wh+3cAi0sd#*q7=}_9a)LmLXRm7oe(svjC43-_%4i$T!Icsr$(X$+M|*$V!KkXOo9!rLNQusl&-1l1EVIl9kRQk01wA=aYlUBem=?W+ap1QCVp;bs=>Dc_(!jbpcuFZt^bjY3f<>Y4Tm_J@TvZ=`N2IztkitF2tm`6tx7o6j`TMBP;bI>*U(hhGeBp$x7>zYm<Gbwa7|ql6}bKJhI0d#m_X+VmvNSE=DfSr1*6v#igm9<kI9y)XL;a<g(O~WTi#OWyx<+HS(L}!c2;P)kM{pq*&==@~`B)9-=>!RZ{FheL+@9aUPHCu}ZPhg5*5pzcfjTpHhF<gq7YRKPBIw9wFZ#U#A`>UngIoeoMYWKEb5eMO{yJk=Ide@;dT2Op0ewKPS&352g+x4<-ju1IbGNO%5V=r@lw-PVSbK-pNYsvr=Ow#R1fA<ZjF#z@)el)gUW<o2=BA+=%Q=^&>0wA$yZ+QtOawl51rpe`*tI9kS9E<R;`U)DOsA$OEYZ$V#V^mChg!B=@IUWTi97N=<Tqawlp(awl>JYHxA}avLVat*O1pN;{L4HXyeqSEp7ZE3HCSTA5s(tTQRDL@h^FT9#aiT#-p}8EQ##8S<Od*T`>@3sF7DO7oEmk&9%dH>j^u^O0XC=Vwx^Q9ZQme~R-^^OEzB3s4J^3y=#_i;@eIi&0CEi;;^nDK14VO)f=#i&~!i7P$hoD!BsLlUjr9N%o@FCVP?VQr{)lCI5>_aUbf(<UZud)T!jj<WMHXVbqD_F!C2nioc{zB7aF<M4dohL=LBpCx??4Q^%1Plb29K$V<pesh^UUl9y4(kd;m$FC#Cf&Ll4<ub^7w738m&6n{;fLH?S&k~*Edk{m((j2uCZq)sD8l2=hbA+I8@W>P$a`Vn~uxd*i!xd*u|lj4@thUAvyrqp`mrsU?-`edce$j!;EsPB_okvlRe?n&)S?nxd-9ZMcYUQ1m=R=R_{mVAJkLOwuFr~W`rC;!N#_!0GY@+0zZR5d^Njrtl{CB=VG)f)H@CdJRG_sP%65115Rqo$Fskq>FvYvw~t`*J+@eT)UA(OPzFD2}9V*0N(saRfC=%Z@$8E2$f`>{wO&HFcAg9ovdu#lPYe)D2qpJEC|wHAc&RrxY)vCXkix)w175#Y?I2TK2oFcnNj8mi_K4UQCVCvil0f;nZzfcHg3S5p}DU-4`kTk{V0y+R-CVsl5Nw|B{sb&%$7n^M6oso|${wG3S{dW|j5dn~+^Q=2zoS*5H%}3!rc{a%=wuf4Bq3'

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
