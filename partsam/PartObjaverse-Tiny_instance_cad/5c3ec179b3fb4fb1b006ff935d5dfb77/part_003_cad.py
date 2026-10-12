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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5c3ec179b3fb4fb1b006ff935d5dfb77/part_003.stl', 'relative_path': '5c3ec179b3fb4fb1b006ff935d5dfb77/part_003.stl', 'source_sha256': 'be868933c7284b954657094f594fcba8c1356227d8431ef425f5a908efdde15f', 'input_faces': 274, 'input_vertices': 256, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-9.761539459228516, 66.50186157226562, -10.512603759765625], [30.486915588378906, 100.03697967529297, 15.468334197998047]]}
GEOMETRY_BASE85 = 'c$}r02UJzpwuZN;BsMI;p2TCtO0WgH+h|O|9z`@74<gu6K~0RPTZ!fxdr8#TjwSXQ6B`k>v0_Eh1V!**?;v7Vd~41B=V{(}Z;UtYJ!AZ1t^KXJ=bCe_!a?j1kUNjJflqm3=EyDSRw={KDrk5cBSRyG_YVn;^bH?6Dwk12xc=m{bJ}%j+o4-7W27<Kr%z~PNQ6%#hfkBR20k?%K4C*5hDQX4_Zkw>Csgy+!Gj`06_4x}JTz22SFKb3!<vq|)oMD%IR4E~ejUn<i4|?tnzJ8vHT83YczHISMoVjzY#AiHMxOG*hmOE_`=P>(gk!?(Lc@hSj+O-<?payh-`KQ*Zk=%<;G<WU5&MJnguC|61YcXYtk^faB>tR<!QgLK^cMT<RN*eqAHWAadq?b=|1R7twh=sVyZEtx9t^%<CHUNW;>UUtf_T#|O1?(tS*7)}dq;ib7ZMM9qvyNw{J4;CYv~=>FIy{q4F4An@lzuX_J4#6H<Nx6Zd8eZeTN;1ar*s~A;MkNr-Ltgc|*7>T)0*4Ab8<C5|8s?JK@gaDe&)?F7eolYr_7~8Q2$yKz)jW+dijZpSVG|Yj|<trsF*9&GswxypH*|%E|bQ#^4zZGn(u9GM5RrY6pNXPra|X={;Y#o#_Mq>7rYj8=)b>-JgemJHsDn|E@OO;3u&=cwqDcZSR=*v2Y{M8+^n5D>CoQ%=a~S^xOb`cw{ND3ri4gAId;py~n>N`JCGUUhyjU&0DC$q4~ni-F@Mw-{UNabMjBZU2XS(k7$JbFf~fJan*zKF1x7h?G+W_XI&Q8vDaSl(=tisH<k?tj~e(0{<nb-zaJ>P!S1ud{VvM7xhr>s{oIHrx<2-_Wx^egM}uD|{6y+-Y`SpE<2w8#O+KT!)#Pj8=E=pd|GEt7)71$+?k?)k>@xG}B;5IOGwg@uM}1NoA)eV!VgLDZiQ7sVAm_$x8x8wLzde;Y6b3hDT|hiR-4Z3Q+Fm%XRrAA7k!wd}eaF8e=i6B`3HI|xOC8LaUc!xy%i%x#yqsVA%-h1<=O4n)oMfD%mL9^bk`rMcyX%?u<GS%&&WG7z2DndbNwMqt3(j#*k8Z;2?329gRXE>{CT(GF&3+;0F7pqmpX*Q}>%91H?ccp|fpB-)B-l5LdoKBw9WV2kr!x^}KmzLAe2j2=x;MD9;67Qevu%VsL%-ws>it4^j49kmSOH$g7wa<TdI|BjocBZD8WM+NR*G<QZZ_|k?UI+{<*VZI-i`6FU*h>v>N9yI`2369hwck9@5CVCjxRdFzUtxUQitHD$Rj=-{yh$${=Ys#T*HpSzQ<{t)17I;9ZyH`9!Nl5*KiNHGgpFVjfdUGZE;@)-9|k1il<4Pht$VB{zWja-7ZG_94U@?jywZzwGR8US)%M0cW%~a<$S4+9l1}ql`n$xE|7R^<54lGf62#~x5w_w!q;aCcSZMs{i^!dSFxRiyK{MhyBA#-`^)8p+b;vbgHAmb-X^K2<mLDkykipbnX(@|*C*in)8+oLqP7Wl-r>F1XWVV^6R=dcYgib69<9Os&~=({^GRjKb39$*{9qvbSANC&+<%j{H|q9<eI9>sU$0E5b3j%RiU0SX!N=B<^I+8<Raop(xzF1ym3!N67%1G4n#B8XTC(QOu+d(^+s1)!@s<5#rTc?#+Q|Fd@3yvgZ>?TX=Iy&0yh{S+%|EVy*iZc%yk{rz<NV<7x5d8mUhw8YW#D&$aPw$7c)pQhZ}ffnmiP;ui+wU<0ruInBEsDly}-YmBKGcTg*|1Sgh=q@EbO!O(RpROMKb(XapOMPJTH&50rWq$z1*9wvnjbH9>+`AmkO7A&^dUDhs?hxoZlZze1GWgET*5G&wlEtTeEvgb=}&Pz87w7kL#dY*Oj1J^4x2kaQC&IV(%VN*;nirZ-JlvUc%LR1@9L4j<o5&h##X_Vhx#R)3{Rd{{0ie&Fu7=Vs~r2aO)7_v726zc#OX$2zOjuCieD}RX);s{wUmxgT1k`A9(f>_@5Arc+Nyg{Px-v!tKKE33qHRCvlqhb_#bj&y6~4>QYhcy8i+HgW$(J+q9Cj`4_z}@8A6cd5sIMEZkfn+^nz)dHwRI#BY8}ehYD0yW@phap1;T<YnaBiugCK74E!2`%VLdo2l!B+sos{-ugaG>Siw84F5l){$}qr$hXN(_z&uZd{?)@I-cGK9^VIbj&vcfN~eXp8^Vv#f0ER}IQLZrX;T=_v^iLp`XRy{uModk>wv^*{0VN?iA9_Pr%QcYxkH6JYn%q}v`ON3*8;bhubCYte%#Sv!rgbCVcjcV7JIA9K;f>KFA@LbAK)iw2;yl|3~{!uB6&HcfV;b`L!CPZ%09GP3}s#+$am~Xv3He;ka!)p8Bf6plCL{<1lD<W65=t(%DfJ*k;3h4uH%cn62J30xMS^J@U7AE>}>wEwAL%u(~0$Ut|#|IUdFyg$gA@>_^FNf%|1?v-!%l>Ji>k6<SOz#32wO!)MxY+_-XyGs;J`y#8aT3aMy8g*MuI(x1<5ybh2>kAo8+)`(5I6Wr4ej?nfQg{ebwqW(#*jy@hy6UJ^gfI}sAEGv8grU&9Y|TencSqYuyTl0>Pq<KZIV?!ku;XX$0)-`#96?5{JP)h>z0@c`V~5(q!fGVuPF+od(u@m{L71a<J;0X}v!{Dgdi_{wjQapT)7;H7Jz4of%4J>f3@DeCji8N~4r+-P+Zc^%t}dAn`Gy>gfPr`HL|%Xtah-S{}{Yp=n6$h8IbS=>KOe?*-Z{09H2WwDN@2cVukw}UTW{CB!yKNtAQPyD!A!an*G?%Rwl!mX{95l{Mh+#5C1ggd#ucI;%C*D@{(cb%LK`_`zJ=?iXsvjy=7^}xJ?J!;Eyxgx0lwMf)4_M<vdr;&wtj|JiUo*gLMTCx@K@A?GmcXhCEqwze<JL?|i^?6WN=GhNF#+at?GcOB##IJ~_RDG;#g-602?cvAvI}e^Gs=l-n;m2NG4RxqJM!3~|8{)}T4S97Q3;q@3Nj?le{qp$B^N%>EmXRjwXbb>%H%~@9nfa@rKH$~}`Uzfudomr|9*B6%n`Mz#bY9qpy~X>y4$k=oaOXqD*`OTayiWVhF7OI9@pI%|PuP#-ytQKy|LkcE#BLh-Uc_TA1h>6$KUiD6s-PvG+Z}b=d<prcfg7P*m%PPM&oa}&e?<Itw}!YM-vu|PbKWJp5PxHEtJQCqw|Z&phn}>b$GnQxMP4ULG!p-V5U1IjaTY2m+&+vr&2os-{t(<XnRQO|#`len!5s;R$EZFBbyy2-O<?>38NX*K@VdX_yhIm8Jy(Mp^kcP(LHs*u|32f-*AVMo>8r*vPh<*sCgL~xyTD^{k6C@L;2v+WOt{;R_t>U<*e6q02siE`9_!NrI4^?^3b)$0V4r#ld2Kxk{va=SW;6JI0`87t{4X}bPygeHCv+w9&D$RF7wFSO?2I(<FRP&b(Tjw;&wc?v2XYHH?<^N?l&Xa~XZ(u&+-0qBM|V%ym+1|D$D^s(wcmmDjeCLbOS|(4x4*lNdHvqQ`RZI8_IY`q<ZV_>_#PkOW(<FB28_e~)~lv)t2Vw@m_=eRZ|{2W6Yh&R2baORgf<cGTGyN3Z%1L?IRjze`xxe36A%7Y6y_}mZszsH_oYb_5&yxnxaX^N!T#R^Zhpp}cYP~J{AT0~;f_gvBHzO$<mam~U^C{;cMtZS-l%`l0od>V0Q>glc*I}kF#La!ig-T5_hjSZDa5n(GW;ALitqoeF9>&z8wNke(~;NP*HDM#eyC69>Jq0_@ge-gyAkK-y%2wuNANR^`~0vc)+GSkUC9YQ#Y1q8sy#;h9nT}q)|>GC!#0|U9|zXUir<BNH{=#>1!G^C{#nR(fhYKK_&0y?MZRYX3wQfu!T+fBnAf`)xF5g&<Vu!#%~=lNj@uci&&_!7vE_vu(f1M0)G5eoX(i0t3ij4bPpsE%KjE$e?NQID!Ptk5>I*kr?YaM_<NMidaQDn=h-dI9oX4Fe{J%sUi~}36URDd?c6N2tb0WS!+sj&^Zf&}P?~1}c{O&XOPlA6t*A(P+F#!3t&I9|SQxT7UN5r4q4)HWtfpss@34Z)>evN6pFz?tN$g8La{3mQfeWr{+{4=V;{>mhr>s3*hw;s8z{CD`rUoW;aiTf_7korwVDWBnOgayCxrwa}BC#U`2|8&v6-v94U7ykAB(?4BI)+JUNr!-Y*0-r}I4N@ARG*szZr6EfHQktpsz0!|LOO<|7TB5X)&$Gz1-EgHbN>OaTXMdp5FpjTMTBEd@?Jw+aP}-!lUTL$^Z+u=$wua9e`K-scyz$OD+VofIs}!m<T`#@TB&B6aKPxR@42#I-D9xtr&wSQ4BlY?#ea-iEe=PlL7Opf{sgF_^pTjtJKicUSW++Wm`hoNOz?c>*%~M*)d0k5Lsf8R{PP>JScLnWS99zixtzZr3a=v+-YaXA+D@7`O!`R2OuVWd_=V@#$jtyXb;e6KpDXh~ZwhLG<U8`u;Cz|6qwTj^QUrMKxPAEN4daQIu=`Pz#l<wcA{RO2Yr3AkF7sp;GWh$ld`7&*F>!$xKrKd{I*uLUBFUW53IfJ^dbY1Ch&go|VqEZUm8??#d9Cw+|8KrYd&pDQ^^n~p-j-6+I+BT8Tr<Ib~zoPU==^p3P&#9d6KA#^dWz+W~_BDIS{IZ$fW9FRB7_TyZH}lS54PG+d=X^g_X_wMArQ=Hbl@2k7t7IpYZjv3Mjecjl(hfua8?s>>=9(R2o5Wh4eS_uL9pt)YGPd89_9*REI>7qIQ@VeO<9ckbf&KEBdFwc0l(w?nLw`q<{$#92=;r`yf12z#b4=#?oT1$bj_0h^Rj%WH`ix<Ffb;1Z{L1(bGsbx4yPMDVS^Gz<oBp@oKUfQ0pQEgmUjKW1K1QZ(_R&6@>-L<_di{3N{v_AuA=m39b(B8$aXgl>9b_B{Z>-f}&U=t?+O#>uTI+YO8L#)nagLqj*fz$K#W?kz%wX=i1{b;J`dp>6w%Xqlwl|qu&Uw;)?($i`tItLX<4s}Ay6@(A25oK_ulK#~>%I2Oczq6DF{T&B>pSBC`+9F(pijMz^_`P*-`u7z{rs2l`mVafu{6eeiMeT?Id`7kSLgWNIofD@z3<MGon~L}$17a7ROXt>e6MpXg=_tUb$i6;d(17H>@sVi^U-HR?@7I1_5RiSbT4B{V~(1gVqSYVzMFZxV4iv}Y~^~#(64^h=SH8C<Lv7>^jS$ZUZ1&~{L`3kB5RY(nw+PP7|!!2<IvAL7>jLSuf`j%@0Pt}_nEh@k>11loapZkdQa=Ku#a`jIcEoH6UUl8XH7NR$#=EgA-;Q$bw0`GSlU)ns;N|ks;E?o{Zbrnr1XJO9rktGSSd*93#E=!d!;Vycj0&^rB9VUr`jk5vLDFt7D`Q(KB7J)*ZP>_AH89#zt)ykdY`Ib=&!iwm*;o`r4N-FQcd}83;Jw8-h%xuj6Z<-OsNC=9XQ^BycN|<sX6=2IbMo2bWmlK3bS9B<F%A(DAlGuWDK?0)?#gRt=dsvu%7MM1~ONjdu6Hy->uBHJm=Igl%$F)d9m-saWC=`RB6_*1Y12`PpQ6=FQxZPCH5<EJeQJ(Qf~Hjt3Uaa^sg2L*w^jbN>!Eol<Kmt+v-YRDfLitvaj3TO2rKQU#|=!Kl{2ZqU5h+Dz#=`w@sAZQF>45UG{ZbRLN86Ev3Bd>o$*4HKlS&W!cxQk5YG~u1ek5*X@@|J(YSXg|M&NV5PQ7EtNiDU$>o=It1kM@Xq~z{g<-WA4?bSAOFGZf4=$8U+3O@GgkTf?_cgZ1mxBEsYUUSUu-(+Q*HbgS3*Yo'

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
