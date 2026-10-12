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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/31b3720044ca458d90461a4ba5a22abf/part_007.stl', 'relative_path': '31b3720044ca458d90461a4ba5a22abf/part_007.stl', 'source_sha256': '47ac368826ae378bed143ba51dec47d20685c8e3454a0f18b16c67f1ae08c3de', 'input_faces': 504, 'input_vertices': 270, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.0802779421210289, -0.157881960272789, 0.19092226028442383], [0.14760056138038635, -0.11363719403743744, 0.23296216130256653]]}
GEOMETRY_BASE85 = 'c$}r12UJzpx`j7YMNy-u*y6Dy1bah`8a<K(D@yDwdMseDp@1#6W3R-nC~A(ecd?=d-74OISg>NxvG=Ih1DLnhnsejcZ`?P=8}~BCKjyb4>-_6qWtSsKNJ}?&9|b>Um8%)*zO>?sA|jvSqYMv?j1KP;8dY`hkWns5LFtPhT^F?O5FFCQMH#M)_UjuO)hE)gzQwO$SUtbW7Qe8F$mqykgL_6q_6-$&P_Kbep_(7{Q?DVRTKlV-b*opl)bg)v8Eg3uf4sC3Y`!tO8;e@JCmubliFHCss%TrB^QCY5sR#Uu3DQ^B$D)6kV$xR&UX;Fd;&S-yg5W1bN#7Q+Qu@w5yN?N9>C`DjwwwPZeXF9#{`RVqWPj!9X6dUFddvRSTUBL$OT){k=i#X%vj5GFvcEm`j`S^4tH}Q9)=koPc72Zgy>H9>N{@!f)9j`69i82iWdDc^>D$w@Q2)dxsOR|gRHJVXsf;{ZK42Y^J|a(vR_I^sfXP>F1>xVwe^S;Huk4ZIS7?d#iCmm&^sO8JlJimrmXQ4&qdeg^R<Lf9eoi&|>cYmze=yqQJKR%Ed6f2E$kV4H`lohIHTss|jk3RTp@8gfubN-_O6avC#`RQ77L>koj5q3^`<=;G!)D9=)}@)qpQjM=q#s578=hkQ-xfwa0VA-F8~?;Pxl=^?w&PDw&-<^jK8eMV-;(@qedpQ%@G}x|Za0@ip73?3XWI8>e|vxU!OL)NV@pflK58cBo6yzdTbd1nzi1@Z+0P$&^6r5DdhZGO`Rmn@=VNPJFP#URH2RK#{#gJ1hj8BJ)q@{b0sTvNlKpK#R;<si5pvz^&sSreFSf+Erz^{IYjv-QamRJrEAs?S!aCnygZZwAl)iIRfb4HST2J<O7K(!((-r60I|}FXkKf=|td4rl^?*O@IQ)a&xE{ZljP>z2i*ehf;kvWF!@M%iN#FXR0qPIhgYyvKM4r?_s3&)}>~H({MEaIDZ7^<+2dPHidY}Q$+js7`E}lFy)vvBQo@(;Xe~vuEi=+O_&rSWUuD_)keS4{FoI{T<PGa3(N#8d3D$Z3Fe7ob#UgQ3%E$o=r=nv9YPJNC1efyYvo4OC@txrkpZ-;EubNcZS<N7!P|G|3RFNJgB-^S!CSC^rlnw~O`rL@~VS<i+k@B<%XU%Wh|Z>^Sj#B`nB%`JV$%yiRrq5GENKcoN5WYmAo3;y{%$ZrWT`|PiuH|ybi(pR6xB7d_mlkbe5jQR3DZ;AFnox={pk2xaGr{Z5q`nF5;u%2!yI9Kt3sK4?pjN7d*>X{vc{M%n+-L5vr^Tpa4bq2)ZoIkmY`+4s6=)W`y{=z>{XIdAmC-3w2pYNi7VmJ7cyP2L-&Lurj=b{vxe>Du}IkFG@uZp7n*!jrgGiaajy0*4#g!|$B%mk^kHy$-z?^|8=%REIVn9i*d=O%sqIik<Y*(R^_)h8jy<2eY|QN;rLjrHU_cXkFKPyLg~6aF+=))&}B`pVuR$n(oX={rh&k31_bV*Tq)ME(Zd(LZ1PW5#o3zY!{Z`?Y}>_gRL?&$%9td?wGcdZHil&yB{ojnh(1{wyo}Oa6GSC4?jYi89FFydJLKwFAuc&)bSR=MTcTUu5BYR%nR(!@!|fx4_=WlQtXYvuhOm5m(SZqBgGIro%99l@`dKJ{0q+Jp$`_*A?qI@`TA(mmNeN-}0!xz-ZLdr4sVkZ8(QnV~~H!YFv*+^5FjSXdKp|TQ=&PTq)J)TlM#-%6{@(IWF0ee{*irb6@wZg%)8SJ3PdE<0m73*|s>(pZ}O*^wsQp=)bPJslT)CJj`oH64rU;RQL^#!!JI-<mcQUc%B`zro;bslj;6od$R<2-Xx&@pW0x*&cvaAfzeo>kSyFc5?7%Aks0VexfRaU<keWuNriDfLn7t8tS<5BKXC@;mHq(hHurbwJ7PxTd74%p>-@tF<Vl``JR_&e{%Ugi0h#aX$)^5lCD((}pOR#HzAMGurEiIj#q+Vw9Nafv<&wUm>q7Le-U0RB`$qc8WiRCS3&1()-4gl7H-pdnv(3GO^wrj*aSq3RH2IEq;aH!L(s-V}><Hg&68fLHmTL5K-e-9Joi{s6-&VUC^4t!@^XOz(%*%hg>HC6he|O}clNb3DgD|fJHuP7@Vm&iPrx^X5>o<G}?t2q@BhRge*!Pc(alH@ji*;Di1^N4p#eQ`QL!F&IGks6deI@@1?0b9_%qyTj@*k^z)Oc<!<p;ulACL37tuWRtI|6<YUyRG=k?vc@tU;Z;?<tp~;LqxXec#tF#ppYSyhi^<{Y?EGs~o7a`5El{@nOib<2>rwFx=!jd#*?SxGk9P&JoD7bw94VKVs0o)HLib-+S$kJaKM=mm~k%CFmda3U$ukZd!l)?m3um{zUkRhp=v4b|L?zqo}9pVyw@=c+_(&3H>|R;Pd`t8+j7@SUL=OhK#{;s%;wb==aI%YmvXo1^B^*kY{6UTu0a5A`id!spm4~^UFR~`CaORDaiBwo%GeilM-eB=n?3DyDaiAn<o97_tH&%CSQMV*Z0fezd-sq&spA=)S`=|Z!dTk>)Ep!=2bEU<HoK!V$5&JlPZ0uYYEJ&!VuISdkOvdzNBm#1ONF0`1@a>&d|*m_xdB$zp@eX)L4;f^p)XX!7sZX=k3H3)XC?XI%>4Z*RNl-+bPt!?-}yz?;#gEVIS8#M?IGx;helq$NJ2BiE;Js*QM)V9mc)FxV8R;^PhbQ>)hoX@;9x5{#IX{pP&zk#_P*II2H4%m5KG|dwb4xR5n}s`uB0AfSbv;&7N+054UA1hh$y9K1ZJM@8o(q9=b~3{zEj@-xiB?IOZvRYbL&TD>L4nF#2jjxam5z?Z_>C{d>1s)&=ug;e|X^cVWJnaVLzv{{33*Uc}sA{~q0{hRN5z=PK^)u%4j>F>b@|$TRT_-s@hMl)j_xPK@h3ZuaBXV&D0_!1{aHL&odH+V-@`x4o%~aX;?CIeb<J>)C%K`mee#^V{|`L_J--Q2)@?xX;vV0iXY#WB+^{p6`pI;jegW%46vtdRYFxK>(g3MaH9lrK#|n#GBqH9T~IW^WVGl^JeQFCw)h=f8h6gCi6R&rbyqpNyWGe*U9|0qUqANly^I3oUg;}iu7%t1tU+&`c$Lu{If3V*?$b@|HW15>(4KHp{XX{{sH#^{W`MTypBBj_uoOivHqzyF>cHExSzz_#(79^qE7ujw%3a5W$kV0tLrXc{TJUt9{YXN!|&bt`;6{8@9jeVTv#_p*T;uV*E`>bolT#je*OJ?y|>x_XEDy<MHTB`?gi>B{1JJ4U6H>)2KFUsBKp7Q_n^mbkcankrT)ugqn~ph;PsW$zuYL)-(&*jmHrOrVP68qJ&+gcmh=JRrp3X3Q^w@$-@C2%8kqc?@6pSD#5%`#sK)c73^|)@^esIbq5onP=hnqX`qopv$nUic@1@DbRpa{W?}3)+a?-agkHI<NeZbbMg7h6<hGO4+>Y9B0-z)U{lHy+x`Ss^4*TGSy68Z;zz_=-mFy9L`QU8KLsPmuen3r!5>f!sL8Z#c((W4fs@w};pXQO|nazxH|%ioF8f3f(KY-hMgU!D39e#JoP+b4LVf818-+xz8`zB;%7{Di`XWIeBTAW!qc(pMVKkiI>msr0o4L4MCU@N3RR{}R5^xA=8Jp515Re=H$=`}t(}<+fnlYSl4r#vxgcb#)(nUmN}-^3R=iSk^y$HO3v(1Nq&m!0)&e>lrap`nDz!s?77UJ<gAHEc&;83IA~f_G?uP{3|uE{?oVNJX`i4kJZog?@sn&WsXXJTvKzMxf)1cZC4EIJj4@qb_kZfb<Unc#yXWR+rqy!6#cWdV;!D#f?ul*^8dXE`*pW7@_V;~U%LtNU+aSYA$zcoiD}3a)fc|Q)wFK*2K}Y)h`Ez!+%Mf%{&hq8N>&i|>%~y%TLzUx{gpN&fA=`)JH5U%t+V2ji2liURpYv;H7_84+%oB_uLfhC7u-cXrLId~{yRg6>90ZWD(-w>@zqjlkw@`S!g?A06eLXXqwBx_Q&4#A|JR>_0;<>kZ~qi@P^)2s7N-~|wKzx>?YoQ{^lq@NGLq<}YLP6qgYgHw4Q!vHCL6{|X0BxR)$`tEJC%7<es%-f8|Vpspv65c)>4m=9fo;`cu4OzEgoy}l(B|h68o>CI><s-k%g`%uOqM5;<y%vIrcH~TIzc8TJjp|YVvC4UBg(#dVV7xWe7gPSY?=t_}vM{V|rq)DTe+IdLkb2cPV83vyb@s$K<EfCx*3p!u7t-wSGo@Kz>GkPJKdt!d%Z8g8x!Jou`M?zsP^F&qLOBl=U9vd{WpyiG7o}AAd2{ah!ErYkl1HtZ_Z}<{9<4q5k8X-+l5u>M`<D&Q0IbHT1S<u}zCzT5Mul@J6-;Z)RKYR<;FiXIpSQ+k$tqEqE{6f)m&le1L7izq2hkk!`_;*cQB>ZNdB47QBaT!8_R&yo2psoZk-ec`eRrahZCCEc7&4Xc}4QIkM0TWTBVHLa&g8ULy;=NfzoP3%x}adYdft4q51*WTDr|La&mArjvzUBwyq_FLUl&*gj7_OWj01OFl#0NIpY8P2EgBO-`e3C8v?kQMZ%NkuOl=$rs3%sJqFR$XBR)$ydnNs0rk2<eSt3<eOwC^>?z9e2bb$zD2%GJw(1uzC+zlzC-?#x{v%P`8stE`8xS3btm~MIi0$LoKC(--A3NVy%hYT7Cp7-qeXYN1$Sjza2K`(cVk;{54Hu{*w$HSZ-(GdYB+fyS$Kol7CeM)!4Yf=9>lib{%i{lV_R@vwsjWTi`tVsS&NBU%%Dyn3ms1uI*u&VP8K?eEOaVa=ybBsS!AIxWTA7(Lg$l(E+h+GKo&ZWEc6$$(Ai|6Gs!}yk*9H<GdS-b*`7?ENbOFZNS;9LN}fO-Pwhe;Paa3@Mjl7DQ+tr@<VjQ;c@lXlwKsVxc{(+eJe@p?8cv=?j-d`D$B^ez2b1TL=TnD}=aUywBghNM3#fz03&``R{mJvlzfi--zmR8B`;upqXHt8SXOgE;dy;!{F9nPLvP%4SO}QDL(Gy&iZK0J7T#ap^RmfG?_F@#L=dZ<AT71dyqnDfQs?@K@Rms(;{^V+8FRCBekDu4;*S%a?G}YpJMmc()v0jDRoZM22)>^nyJ;=rR8F#8e7C$azp>AY%vZodm6!Ap{W0xc6qI!~Zkv*txWH;vZV7RazSMnDO!Q~k)tV{Tn*tZhrCb%N|HK!_M5iR)pisVX+7W{lma%*ZUa%-|!>maUmGip<EGjbbhD{?F5YQqp5tb968&8flUVD@RwIx890p*+1R+_PY+J2{x#hU#e;*ON7Ra&MYZD;Vmp!1)D{zo(WXx8~gRJ@uehSc@WB6xE_2+k*46EjS<Bg7dPivrunp0dgU-@O;=7T#RkOCD|5SifzH4vn|-dw&1dC3ogU9;L>ahF2S~7U$%>Ke!k?dwWy;-eQE$%Xf3kP8f2l>$wF(Ah1MnutxFbKk1VtSS!g4&(8gq;O~^vOB@6wIEHscT)Jhim4OwVIazoCuKIdMT?XSsos0GP&$N|*+<N$IlYCdu;at&%;at(5IsyDehxhAy$xhA<bwGg>Bxh~a*T$fyrT8vze+<;n=+<@GOT8i9=+?e_~xiPs3)k1DU{+3#n{4M!AY8mo(<Und^av<4CEkU-DzoGh)zaclI79khmUJ4$dMQ1Idsr|_P*dEImLvIY*a~M<T&0(%7)M)b0T8z|UIAa98&TNmRjx>xllKDomubz7j+dnhU0P1k&>um5kX|Y6$MT|&#A%=N~h^4noi{)ChrM4&QYtexkLKgZ1S!g?Q2XaR(hH3E=$Bra-qIM*ABDbfuBe!GT_KY7`Pg`;nL-0_>53H*#e>a-3jNT~ri=~E;MJ(m-N0If<F6HN!k(X2B$jixMtrv5xS5TLbSCD_D#*yQg>sN;0mE4yptZNFrSn5*pXwGpIbtriX_iQD#19>I+S87MYxE)zzNAArE>M%q7!#Kai<VDm-@^a2i-_!Q=#7oORnq(-@_vCk4e9*$v1(C-E-U}_<G<Ijar1z2iv#IaMLf?>uz9wgrv$XhIi%gFFo}59=B4?0aQeTr_Gw(~r8`krJ{E8v?E#r;yX)fY-t}X~MFX4%~dboV*|BjxBT>PB}S^sP<e%_7jPR(stE5TyDUAX36RN;9s1m~mXCg*0Zd<?<f+?TwpD=)n~)Lbr~<{|3S*Fnt3gZ;&xc~i5=A_V87W+|V>&0@`2+#A7}+&{g3!D4<PEnQrF-2Sis)#THUUA{CM|HqU6{YmqmC5)fUuRTn1{zwth(nGvIYA@QZ@?r}YPhaJK03;Avmj'

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
