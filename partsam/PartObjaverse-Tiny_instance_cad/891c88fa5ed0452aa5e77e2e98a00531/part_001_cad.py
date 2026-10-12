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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/891c88fa5ed0452aa5e77e2e98a00531/part_001.stl', 'relative_path': '891c88fa5ed0452aa5e77e2e98a00531/part_001.stl', 'source_sha256': '264d4c92454ab6630d4219596e1de241582c394ad7b9039babeca2485f6cfc54', 'input_faces': 452, 'input_vertices': 359, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10655926913022995, 0.04071544483304024, -0.336747407913208], [0.11308960616588593, 0.36912694573402405, 0.005454717669636011]]}
GEOMETRY_BASE85 = 'c$}r133L@j+J^fQ!oCS%6M-AHurCQwR%yhr7?6O3O_pX!42!@dzzj>^0_uPRihziS!v#UY9>Pvonmq(02_%6L)J9NQ1qV?u1O8p#_jXdZa{qJw^G`T+-uHW|y1Ki%ySlpS5)~OxG)UvWV6A+$?8t_7G)<&3T97t1CVujmQ85Y4Crp~=(kc)ae~vDFJ-S!aAeS~(n-MZPCSg>3NIQ2(huAhDP2C}}6XPexkC-rgV*KbB!MlzapAcj7gt!rtV(hqKSa{o}?yyEp-HGo1=U*xN5Ujs;OFd$%r_q}1PU4u}4>)^7<^yjK_uic2!}YZ(xiU9;o;yJ0n+@mk`vcNsZVvG>f1#ZZ_kOUOxH<IfS28!=e?nZpv+%qR|8hdEzk1x+r*q}<=95MHss7NiT>rdBCuHvaIFh)h)^#6leOo=(hc}x;-1uk#l{Z`sGG(p}KF955tn=aK7b|mR?x|2~A8B|}rr_?jRW8b0*Un^e`76Y|m44n!{H^HobUcqzw#nSnY8G+t_3<0&e0rQAZau5a?ff7tOXlY3e%zivo%P|K=j!Il+<W~1mk-=@k@nl`{!y7*=Wh_#+{=8pr`paOA3k?9aU(39&P&f+yHn<RtGmoYVt3H-+#1Qe=@dFncg@vVGWSLV<;q;E{UY<d!58R!zg&Ak=GLy>#67N|)Sg<%o;_6G`ba+h#F7_eZnU3AT#w&P-1BH9as5%b463L2(yjiuH)1EXzxLY_uIElQ+OPG(%zZL<&+U4Fulp{FJtyDdddgSeb~b)EBy+2DS3aI{s}IWD6CFhD><%nzQk>V0>vyG6dz!BYr}*P~@vvk%zGtO~YaPdMJJg$gSmycz7u9bKKTY+!jaqcw^t}0(h$pAh^X`c`Mf=ghbmC@YB0Z1Vxf8^_r&crXd4--w?NSi)9S3rJ>M5-ew*tST>uc^VagzAI?$Ui>JdLG#^y9ho92u`1CvMICOOCu>E9oe4Eio%c-mg(r=liR}HhvzfU!(iSm{W}T!3sI@evRG_xt)5g$dUJJ?f!+hr5k*l(c_N#@M0PK9L=mu_m6(}AaOJLZN5)_>yYG^#~SO1M=vGr8I?!Z%X8zxc7NR4@3+l-on{jEp1(=g(Tp2<Nan`PIduF+k+yUl%>m<xYYWQf$n9W$(43EFTuJIrti@Wk56@^p+}Lx4`I}9+o?lOLe|YWDS($sPT+H#|AJ*dIDfenR?e~M`*)sQT=t119UM|O{{Fq!iFYo-JsXn~=daB>^&Sko9&7q}<yJNGs-O@k3D03tIA@{2T#_@iCFG^hh{iAI8Iy&5aNXwD0qi4}^x(?pQGq`->;xw6i<}AqZ;e$=$#*wR3-s)Z>L*{z-+c`4V)4Fo`9&4z7Fq>Yb<JZ$0aQP*dxu0*Dxxt4I38eeS{Po8*6o);f_k;WMU${MuMLyh{@gL&eMwOQn|LpoU&JW=C*Z3N|-!Yk7&+JjBsQj(3vt{m0o<&?g@h6ubmrUGv+&zohfA+L3#3xST^3SUCd*@cbNtwHYLvnn0slmiOK?k`%Up#Ra@t1pX{f)lh_nN8EeXCois6RF$&e8FhCsUUYzrLLN>BKWRKILz`$9&I6TLpJ};?iVpF8*aZm5*x1-2DfghdJTfZFHRN51#YK&E+SL%Um0{GMUP6u5->WKmCBq2jAv)%4kp5SBqGb<Bwaj>M&oBN!;BzGTo=V!u87inb%F{dJb$pM$hAbm~0;&^#gIe)iS=01Gh3C^=GC}{R%hkZsU56e8KHdY$d<H>h(M-b9bW+*)lhqHYV=rlSTVA54B%P{LDk@&y4On=(-!nYGljYxsFyucX}SpvlqGls}s-t=k@_pslFAN#N9my@1Xe4PCOn{xVwIfRGI792`R+OEz9u7%_~dk{cEmF=Ho1Of}f*KiDM~0d?j%$v?}+9anaoW1pJ-2l`{C0+@30Trvx)^GnV&T_dGpE-YSze@_p8k%m3{vKNmx8ACS4}x=rnG1h=N~hB>Jwac_^$xj*r=ruVD4!P-Q}zh%{7YER><i!!&eyB(qO#Y!^Y>}9@r9hLXG(mo>|v68v9mHUT~PE(0n^SJ(AiMyztUg=r>xL&gBP9NSeaW}QYfY2;|+*@PNZsIeC68AJp+d}u%57X&6HEaGv?PL`HVIS?c_>&7Vx0;&!iC65#e6K~^yW#RWzW?_gm$@gX8a>xq;JtJHcz*dlU-N#muhD+J`)(!4+<J15_Ul>Rf%-4=9*-0C`74h3+z$#j-b>>9|F^o#_njr~t^4>N#PcpD$;a=0l6pYqo;!Ke&lpc*GW~I<ys`Evy-$oPqYlf*qjIxR89E-L%n9Pw#uK<7Mt)3u@+RVD$5ieQ+i&vv@OK;1b@x=w%aXa#?VDXb<&$gj`z`)6YER>(P`VF|8x?rJs~S*ydfU$6`*2tJRrK5)2<7q2z<PZDH0V$HPQQ`QpRHX<?bfV8mQVXD-05%43iCdt{l~w`<B;On`(^IV>%-qE=W6oz(%dsE<m+N;3y;g(=>K@5%&iic^d5E}8GlGV9+i9U&!qOZIvii_uboxyS#WKY%=KmZPJiVcu9mlIU7`J&f%iZ1;YrziKV;OP_pH^W3-9+eYp+i|3ip0KfzIFjeLeM;PWxz|%{eY}ciWGX{BiYsRqpIJpJ#4P@yESOTt4lra`)YoY@g$)pTO<VYUC1`8{5ZoJLG-f!>uK4vi#NWaOb_8f1DlO=6-wf*!@2H9X_4!D|{#B*VB6fkC)!(?|O$j_jx`KdAO>RpX;LX{OeLX;d8(3tnmDLz}5Ro<!X8LzRKsyePzBojkx+;sN8uj%$RAb<@+lCxdSis+)b<QC9XWz4p*ORtK*l%)qX?ePQPIl4Ok;z7pMQRRtzCtsK3gI+eF)|{o9%;#MS=Lj486&@AY!H(%(8<?QhNWYQ)w4Tp!Vw%Pa2%l{@bR{a%wTa{D{)7l*6wBbDcuzd3`r`o7b@D^25d^}VTb=e?<S2_>$+mmRLYm-VUPTjk?--tP`q#{(+QFJHbB?^hXzI9wfv=o5BxJ<51Szi@@?QN~d!cg9iqTp35H+!;sdMep<RDC0MM>?7vNcu$WFr}I?DjSg4Gjrzzb#MSYq-fRh%SH`gpSI4n><73>u%6M3R#NS=&xLW1TxLW`9XTE;Q_*`FDg1-0E@w`5uK5_LsLgmhPgu~VE2$ehE5&EGf%$4sKeSUX79_2eoPmLsA=sW1nEavL>RN~|9d_8=>%N(wLms#tI@OP>5-KTQryU&_bp1JZ}na`E)N~2>CKj+GKtID1Cqfs)L>ruXoRqph+#>5cf>UX-zo$qvqtKaE`IKI=3thXsv=M5aL&Kp>nQ<CND<;*`=aUXI&sLWSbpIl(B%x_pvFLOQ0e2BIDd*bT6io?};6{C4kx?k1#8Ea`pzK@l89*3**JjSV-#MSvCV@YE!ugotQCpvO@WuD3!(wmP*neVddFXVcZc{Ycu^JxxO=ieNz&a)X0l9?;>ehydX{fz#5nJe>(4p-+Djrr-!m3dBwtMi=s<&}BPe6GxM8vQO2SLa<FuFkt!_bzk)rOfN*b7fxFnA@28DQ|Q|Zik*0--kc7A+E*U<$31TV-Lw(pF4y1n-Na)%*L*cJpNYZu~qKOV_P@kxPMgU$qRAJlUqTnh!>iNcepYSZ*^NuT%FH1tYq%5mHB^b${);gH{{CgV3Zh7<63on!CLb+@j~knZ9XAhX#Jw-7A~)>cUT!FadmyfIx&gf_v(6zF)W_Ay8dDuN#pT>vR-2iTTkPD?Td-L?(@Fqu*~&C&-nRzV)AwT^+)3Bx{}JBbtV09B^vjr>sbz0*Rve1u4m~#cjbDNbvKne>u&mc261&=&*AF2o<7UsaiOwq=x}x2(A=KK`(48Ql68yMA06(k_*||JzgCXMdFuM6el?cIf6BV5!_{?FhpX$VX6GqfURmdLxVp~kaCMzmFSC-lvW{#{Ok=LBQ#)K;r#2ThNu_pH*T=yNt&fAN>*M;r+Y(pT>m9DH*E_t>dj0092Psy5hv0DacL)wwe}~|3^>+yQT=^Y>!wdZmVbViB9_9BH`CR#Zg~NS*UlHZ=E0c>?^Ufq!)-;hyYC&4;2<ay#0*XIJ{r|*dOzZ#CPfS{ehyJ%eF?roSh9P$94IKtQ4Dshk{{$2MAY!41;9s$msH+RKH@qm5fpS96OTL1OW1;0F{{mv6wIm;cSZG7Z*FY?^rsOLk7FtR2&oqvO{wewUh=o3Ye}Fh0=`7e;#0QX4!Fr-CdO^Fu4?^BxXfOD;kv9Q47(NyCu0dK0HWS+<LMOnlMY)+s4r^<lTbP|%L*4K%+NqbFnm~KP_p{SrJG}uN1mD5Mb-e^_4KK=!LOG!$;9tfz?V&Hhi!!k&Co~4WBerP+Z4WQXj6^x1!{OUun{a3wcu{63$_X6;ABt^iL&M=knLa2dGzz`}wy6)T4KK<>pq$WG;dMJTvr{K%Q}}ZBH4u+_S!fXa3wCO4ry9^s@NMkW%1)8c7vW22Tvst@S$I*VIm!tQgD-+@T+m|hqD)hi6WRj4IJPMYb-{}=%}`EgD12#bQwmxXUX*Exazex5t6`g}&{FWC%u6UI^fmYpY|{W*6<(C-hH^r?!gsXO%XVsl)EF$-P7Uo;2ii#T?GX#@Ao;e4g|?G?Fydg;A$&`_p_<#N6|{xqJ0lkQisZW@7TQhnEfKdw9m3baaaBYT{&{Ez_~+pVLfgR)gzpQj178Pq3Ev9GRUJwAAm}UbLGZ6byTQK>9}R5<-wJgJzuw-*E<1e*-3|Ytoj$hHV(4<ouSdKdWrd%HZKgvP!@q^RIOufvQ+CR=(`o1>$zMe*^c(nH*k(8MG`uMDZ<G`IQ1V4x919JUd@;mAi%VWZEYv0Wa~j7&zmohu#6tJO$Kae}p>gn{%xaVq>V+SNZN@`m;a4Ni3mp%iWT#Db+5p`Mf80(-?Q{%k!i&5e*e(e^1!YoDE(P2~o!d~a(5>)Cu#dygWAJ<Ibiz)1p(iDO1o07+J&8Iuqh6s~B)<po9@HWH5<9K1(=zBv$!|cs0mmr(``Bh7bQ$~?$Xf?p2)`Y9$<TH1qAf1qJcVXU{xV{rU&AM%9XBBfzf)@KozUa(Y1sD}XfnL0(?Y#Mzn6R(;xv@~9_PHuPVYb$!7oGJWavBa3z0VxIvM`&$QuqF37?7c`xg3><iAEN^moaBk636)SAqWlvCuNE0)Gv$&=Rf!|1ZQsf0O)0#6o|Rd=_G%*Wv$xa~lC24!;z63D6PnpCWG_Gy(oI<jsf9gI|uk+0gm$i;*`5IvajE^7=!^z{epk0@@#5oXaJgkI=i4{|2$pBCZ1e5V6q8t^zOmxytD8>PfyhVxf&C??NoJj^y(+j)gw&D)7G|7FyNCJ{ITJ85#jE`ZJN&1KJsW67r&;J>dU_yl7|?{9lk435|vyhP)S{k?_v9QyBC`_%6t60S$u}=kgz%k5Dl_cf9!S5wXzLlCOnW=u57GvABpEBDDt-z9wR!Z6sd_vCweIi|?LrXl+-4e}Gu17z+#E3+EOJZ2>R7V?<s!G!%XU@?L|6!zUuIEA%z^S;%`6+7*5V@&-cRgpWsFU+6&izap<6v@g6km!EMyLZ5RL_+JnU6=NXB|AAPj80R?t5n`d$Tm}9%Vxi?-1^x<Rp-&~BgIMSt$!8)K`YrrioZC=nKlqQ3HxW7%{uAWQflh>9g}g=3Ia)zqFZ4a=2k?`THx>FG{7B@DhE9bajywZ88eW`-=-0o4-je+9h=o3pyy(}TKub%$3}T^WC0_!u&{C2Y{dy_rW6A%BSm;g3Uq>wT2K)$|+bF03pMbn6&{6R7koPWh3jBQJEr7lYKO1=-=mPjL$Qujw!1qVq0O(lw2;{vA9RM%R<u1-g=sn4ce*GRaK=PFl3#}sgdWePAg|CaaF;XM2#^~1@L4zef0I|^il8;0z^fk%%KrFO7ysmMdAAuy!Rj?l5-Jv>sEjv}PQ%z`j$@f6q17(GGW1HI0n(#r$s|2kLUlw^~pq1c@AukYG2Hu4{4H^h9&hZVLr_jEVAB0%wK*^6lEYy&E3}T_9B|jXo&|#7vf>`LAl8-_xw72A6MJ%)nd{LZR091n)^8q5SBs2iND)Op8OTsrmUVUg4_<G2z3#||TJo2hT>%zaGai7^2sSj91Z1WtnI($^5t4L75|Mp)B3;sNGa`JyLRJZh<CYHC1wd=~CG>(c4r2C+V{Z9-u`iL1K?SB9vPw*-'

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
