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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e12beb2008d348a9b48e6d2beb2121b1/part_008.stl', 'relative_path': 'e12beb2008d348a9b48e6d2beb2121b1/part_008.stl', 'source_sha256': 'a25f2a750b320b00542329834f22ffb457c2ad3eec59c34aafb8258d8c1f9966', 'input_faces': 468, 'input_vertices': 272, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.32467368245124817, -0.14705780148506165, -0.11858607083559036], [-0.015356896445155144, 0.40584060549736023, 0.12138763070106506]]}
GEOMETRY_BASE85 = 'c$}r12UJwox5f`*7b{qTDA$S#YQ!#<Yx&!2A_zuh5V1sTpxE`=u%M!`_fZ7w1qD%5uH7j1nqV0<Mq_U=CW`*&?EOuq$Xn~J_hzlVzTbSaXWw(rIrpA(heg*8&N<x#zsiZysYOZ)cQcy9MYxHmu!xa^Lc=0!3>`k!NfaTUUeHCI{X2CHauQKuyjQ=l$j}I{Mv7PC{tdi*6tDinB1T4p3=JL@(JxH;twX{i!_0o<z>wi#=J!>6>-+jBwX6Cl6P5qtE5Er3%E(h!)6J?LP246`@7c1aR56Hsy>UGGTK&5{n@MfVzE*h^`C{O~i1ciH(|`ft+4({Qgl6X(>-dFbS6_9y5FvfN_DODMy(8Nxe_^YT^lW_P_@EG(FU}n0I<d**n?7CZFV!%Xef2T>;=rJRGT(SRo%7@OkgqO_8bRNi%f9-VedSE%pzM6rclHQs=iXm0Q(eQXEmY6>(NFZfwpYp5uB_Wi?Z`PgTi>)O>L*#p6n>HGJnTz#)VvD$qG1B(k36}VKL5099`(Z*Bl&vT-7P$h59iY7B_?rxPG8D5jEk6=ov*JLF_YT=X&fKdtt+?R?;QC?2Vac4Pj&Q~zU)V)Qu{^A%26`ku&@@lXT>S56H<ZtM|7{s`87Up{=~m&{^+Z#kgv9L<9^8e@FV&AN^_kWG1Sl6){Ic9zm$Ekb{hBp?Bo4NJ>A*QjHdac)XEo_ov*F_K9Jh8Z^$L`2m8@+mGc!gQvQ-b?2q^7dARgxoXl6?Yvb70&OeQ#&%;C5kNQmKYp76-@=ZgkbDiTKdAyeRuBG|=q#Eb1F2VC*$<Z}*o?kv*q<VMDQyo)Q|E2W3TkLC1ovDs-UjL<3Khxf~<g0z)FRVayj2j1Y{-YT7FC5|PeQwJwH0~W|kS_|(<Nj}5ihMD7Jo{ay@puKV)W|<Qn(K^;=J{6cj|ntS8isTJo5z%|`IH|=_2LGyzxgfChr`21QM(oguwVY{4xSI+(fF#70cig*@{MkhJih+laenTjd_B(03e3*eXT0a}E$+mA+$(O+vxQX8@G$EF`FqNqrQ=OqoMh{37Qal#J<V+MPq)e-Kd|jC+kAt?fBR*ZZN64}^abi)*U(hE<JMtc+u^?7Hean#;3AFFtB_>7_P|$TzDcpo*Bf@YO!M+{_<{6nd}9OeeRjuf1b_H%`<i9rtII2<+4{z9F;}VnYy0+?;0uTLD9tm;SKaK-*8pEQoUbWr<aP3c?E6z0&A#@=zCR69^4y^OY4+n~gs*uxjMwc0<g14E>+R~p7mN09u*<Jm{U+sSR_<Zf&y~iLFLIuWv+D==#(MSQ?b>O~B44?|b=0aKc^pN4nxBR-y?DOQ9KrS1DSUke%ugU4Ka|_^rZHWoh9aTl8`=!v_Ah^Nl8zf3nApt57wgNPq4x=M_uA%b@RjDRl5O+#%`eW={7ij!z&2mq!oK$XwluqZ%e?xt_95H+f9F;8=ZEat6YY78&VRo{efYwmzG2P`8W$zezWqk{2Gzd(BG&U4dhh*5yj}lT{NDEcqxRWJzVQl=i*Zw9uJh27*Nd`qX})Q}^*Dc+AMYPRN3gGaIZyrYv>V;Wlp^bmbiJ<n$o|w?yq@|mCf@*Go5Sn1>6>69eXm6k_6zl=aa5Nz+SJU(Hw--RGaavF?_}G2-Qp*?rP$`1N~h3xsTsKr+U6TP*f;e*bkH{c-}}a<9}e5*TgFjq;hJt&Kf{m4OLwTRo@3wOSU+JuUw5VK+i!xe?{;Yal~5WN5qdVku02=bFR||*Q~STkS1$87iqNI!_<Hx}>#L}9G>vbO`Rr$O<MHk3KArs2eUX2c*YPG_CQ!RCR5{1v7suD##y507F~Zm2Yx<i#G%pjq$XC}K=KaZ&8<elX7ZyMFP0CltR3cxwH;L|dTKPVGsXscfZ~S2b`Nq^qq1^8tTz}Qeos>U=*E>hwFq79i^`(|Uc?U;x`^UNP{wQoR`TDs)y3gpFe0lwx>Yb78JcR$%JcR$%JcR$%JhaqtoQIY=j`I-ySM$(P-*Fzo|7spu>O0OuOC85~Xz?BAp`|^J^U#v-I1g)mI!niON#}jevDX{v^Q8CWi>hmQA2{<J?K8jfyS$@(_5S-aG!KT|p>Yw7A`)$VeQF81pNj_@={{-k#WeVndL`TDE43eU|K}^7W}C0W*EVLP+11Cmn5OhNWLMv^Pw*&w*fw81Ql9%izkPiTzHq3ot%%|NcWA#3U!7>*el^aE@8`Lk6YT24*X!H&kJ>zy^KqZo{6@3i&gnFbNAdz*uUA*+^9u9hec|@QbEsZeMXvAhE#LoLTxU~$`m>*@&h9(B&)k(Uh2Cq+$k(cr+fDs_nx8|BVe{C3yo|4R*KKtDI{Kzk@pS!~eD9s6_LRB1ljp_cRB8`=-GhBotI4##G8X%l{i`Ra{mO$Cl&`_p;F~_LpnQF6FZQ+7y#F|!K<zb_2;k%P)cCxVG(L|uPfk&Ot>e5uxpQk%cD|Bui>?bpP2)-Oi%;bHRfqQTX#9JPCEv8BB%QBVvTi!P4{pr)*N)TiL^19kN8jMi{Ub`>JVANSi;=JUuc!T_HueVj>Nl?Jk66E->YP4Jz9D879alYbfbw<tDtz(#0m@e=&f)qW{^tAYgtN5IR8z)te!zX|H@)9|@^z;M<ZHd(^Y0t;_id(rFw|#1g?;tJK7Rhb^z=CCgQfQEOu0$EKDXd*+xF<Ko3g(wkmpH4)A`g7-sRZ8k;LaUvBeBJUa=3yxLz=|PZZ_;bo33Sxj(f5C)i)?$LF(Z1ND#SltjLvY0_@ne$$F|BVS4F#{Sk=`kpbM3H$R;Q+t%o@$7fcN4_Y#k&l}dN9QFPy+2CtPq`=Ap0Ac@B42k6;B_!+DfOq4n|(!PUvIdA_gQO_j*$OPUs_+advVlGBYXkha$NP&D)QCWnMt<irNCF<TiRptT*!Xk81~C3-2aycvG4VY&&#t0_kUGyKJK<XbYBxi(Ekp;!Grr>zgC=l?ag~0_t$Hwo>DYXCx3bap8vJFa6hERlW$yEpYyfu{Chy|tF(TK1vB}46VKCir$o&nUp@Yk{rVs2x>KBslW*9tpV!60+)hVdo5%YKrQJ$e2b58<<m-E<@O{REebsk9=U<#c_Zi_G%+CjzE?gh?CA}K^D*S)%OS!XX-O#?h$^Emv8J~B{EP8GbU&?X)(JlD;+VYruCAmB24~|WwI?e~l*P_>R|GT%Rd}H;M^c<|dsmss9nVVwhyh{4hd()h?{P}?7X;kNPeR?mh4(0QSd_n7x@uznwl;7|*=daJr&%d{l*uOrT=h-CQr#bq@`P`qzHV5f^)Xnbf$9AXp!gUn)%i=Y3T;*^$KX?0f#QFS5$JI;U<ljNNB+$5uq`Gw8dRnf%bYA=7*l*I3ud4%p((gH@=%Kt1eICXA5LB7=AzDB$^7V(u>A2d+99w0+S|pJD;fJ`+Mh~hlN{-|8<8UJyH$D6Y{Z6QsO5y$P@&n`>DmA6`Q7b0+_ofe-H2$UuS%KO4VgdSRcmbN%+O1FIYw^|Seyo<vL%x#sg?!`cIy<TVLqcg?5-n!4zsH|^#laU({kcvnADS;(@GbK7Xx@*RT!$oZyCS%bT85r0^*U4I`Fno6Pd#~i9nF8Q_x!!a2EIPte_l!F?RTDhz2I3sZlk{_UmvoAeuofaC#6&UXKm^CG^6WM@=eXs$k#ue8bj(?jq~TE^8Mg#=b-F-Q=Ya#biO54ETndxxlH#<by!_`zR-FsB4267z9A#CFCD+a2=cX*p6r)hOZPGHY%uwH$6)e}XQJnmE*wC<A*X@sKcB((!yG-y7x{aWFGhJyrTNw+h<xL~UhGednoP&rRge8gQ_0sR80hz5<#A1}lQxI%_d$<_(Q!64TtNBhYdAmD7?ho_j#<I|Fy>(_U$@*I)9utSs(1Aq`Np*G_<Z%MKT`YOO(x$kv?iZ#LfKdvuebKTGToEj>tDu@YHfVD{*8Lkr1hit^PJx7$JL^K(1%5GdyZD+cIK-zIlZghUyqhgnSXD12_a<U6K<k^h|Qmlq$yt(&HhhEgX;XR{&ZBQUW5PdpN_Ve+c3!-i3rJK5t6$=yMeoa%R?)H%YzFeB)dW@gQb=PyMkR1lJg-XyF+V$-NCh><H5DS<DhY1sYdWPa3pj-I1=0!ItE;ohEa$T&?4XxVEOm9T+rMI$pxWBzy-mU9LYtY<-kS370lrctp+UzE{8T%gZ2e`Lqnl`!J%LSLUIUn4A=mTf{p=4fj2=Dz?;B(p-JGq;3H5Sd<1+3dK!EN{0sC3_!sbfgyehBTVSbwfbW4V`I4U^BtJt)ehmE!EcFfe8T2jm4frj%fD?!09MHeOQk|Wc3qT7&oxz2``JuVM`N4Uip9OPXa31Ivunfuhpt+rxWk@az%?U0HE(jIif?yYfWGCpKf?4WounRtahxgKdhmia`^db0n@UPID;9tRKp+AGqf=?hMABP?VpMV~N9t9r*ry(RCfTn<@?g6Jklc9US$>7b<MDS+tXy{n*XmA~97jPZ00xb_#z=fcN!G*v%5RwZ(UBOaaz&W7KP#3T>I43k8I44-}@X{*}G#^;1J2(%x473)w4ES5<IIz@6@V8(eXkW19e(HmeTnbtOTnd~QnjdVr&*p_Xft}FSya>r2&@$jMXp;xj2ke96Ngid6jpo<@-38tN-U&Sn-U&X0kbE8?`2s?6I&>E}9lRU55xg55kB~e8ItuIytqC0kt_iM!klYWt0o)H93*8Bh1#g2M0&fHFM@T*gJr9<84SWuK75V^t6>Kuc6LZ`)#|x+l`~v(E`T+bA{0brYH|RC+Z{X|D^WgIsgX;*%R}hjjpy}WY@ImNq@ImknXgqiacs)Y$MCb&tWy~fbB-b{FC$uco7hD!x8d?)v8tewG0(JuzLrAU&?FX(1?h1_scLh&|ZUavSZ-wp$Zw2o|NInHU2R?`KK828c8EOJcy$!w$zKD>V34H?21V1vzd*}z~6YvM{N9YUiNAM@;OYkRf7W5T33;d5c{)Rq>z5+}A4g4H@7kV8m^$Ped_zptyC1?it68I$aAowIW6}khQ3f>M~58e)5fRH>AIuR_jHh3hsy0Fg6>d<e%)xll}$;A<pouHmzC$NB)1xqb0tS`wqp>D#uPDyr#78BNWO|oTulw1f}QCQbd$qKZqu&%k1>p&+9>l!WDvW`pM4BaZM>%Qb<=ss{7^cZv>Sn4UT)XQM07ln1NBH6Ofk$e`KDXe=T$(H?+<lmu>z?SR5ve%L<_hK&CqZNd{7uNlr<igMo!n!|{oDcd@Sof2X^FTid>;6-6UTBuE?pGz}hyDY$TuYX{u4K!8Sh8hbE!nc)mTcL#OMVJ{4wiZsEcK4C?)fEKo&_ZT0=*=x&li%<Ku-$m^N3{2GmGTC&{VM0?ZW!JBY6{afv`RwNtVw~252aB0a)rtu+-{csb0eR>?YY8A-MvyIJg2>K0D@y=7JUnOLY>~{gd49$bC-_a|D^=M}*{X=nvp<@K9)P@KEq@XfSv<I07Mg1hfx$1b7&<7kC(W2(%}72zW3w5Ih(>2q8JZ9F3qVG!U$UTS0q*TY=j`dx6`6J3;$^JApexgTcY*i_Qqi9icyfJA&IlgTQUTEulTYEx}F9(Gcnn?E&@&4}|^*9tfU>kURq#4xRy?2^|Wa37!od4xSB;fkuF1!1EB2=R!w-=Yr=zhk@sSXF-R6XMv-kgTc|@>Ci#o>ENjd$pfGP-~r(7!a7&FBP7=|M+0bMXd`fAa5Jb1ZU$}vZ3S)tZVhb<ZVhe^?F4QQ?f~r!mf8{A0o)GS2HXz(A81SPf56S5O~B2;O@(!CHAP7FGe>=BU1&paUGVo%fAII<{?LKo{@^LlY2Yc~pAeE4LuY^&gO@^Qf|r7qLuZ4RgI7Xhz$?M4q4U72!D|tc*Ffij*ML_+=YUs%S3qZhSAds6qruC-OQ6%iOTdeuQ^D(?3!ziN3&9$609XTuLA!&)z~4dZfxC8a%HihxKmDtN^`+4d2DbnB;P_4ZpSf+n+0<O?-yglZcE}~yDDws`2i*YvkWb^{zmkrSpa'

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
