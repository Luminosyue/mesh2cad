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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/97582e1d16f6471bac014081535c26ad/part_008.stl', 'relative_path': '97582e1d16f6471bac014081535c26ad/part_008.stl', 'source_sha256': 'ad2076fc91258215a82094cd30028db617fea61dc7a0e5377828cc3a28c7320f', 'input_faces': 254, 'input_vertices': 204, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.12301620095968246, 0.1991277039051056, -0.04353012889623642], [0.12929506599903107, 0.47292423248291016, 0.19257868826389313]]}
GEOMETRY_BASE85 = 'c$}r033LwU9>zzasG?CRZBshdP^nr%De(<S)GnxsrA$I>B}fpe+7Tp3N+h;glCdOW4Y8#WG4`dDQmJnGwWV6it-89<-s^tz{2y10+;i@^H|M<P`F+oM=l{O*?(dw0b@49ktH@tXB|R`b+^nJ~cB-KGDwCpOCX5^s727C!+>}y^4}AOYzNU5W(=DuDDP@u})qiMI?2s7$S5^Nu!&>?WsQ$yo#!QHbh#ovPW@wb{cZe7r8|Cq1M?{Q^^8Bvfv~gg7+N?o<I!*l_|H^x+p#NjqzI`6ml3Sf|*;Q*iHP2S}ge!&ciyFaK&iie()$;8HU%A`xwEf#CmxBD}^6v2Uyrb}~xG9D3Uyay{{H@1+j5ukF5l4$u;p_9-Bfrw3)LP`v{jC6g<nO1DFDxH%tPa=VtC82?D{Uu8JqLNgS6=%ZzWH=4eC@=EJ*fZs22!8pl@B1l|1$XQ<4Gss*Z0{5?J*X<ImLpnFCUtPa#G7noC`-JznOyiDD|%9KUAOjlcZc%IDE@}PTHr)F9q?2UHcH_hNYd9`nN}Y^y``MwKJ8@<N0mZ4xyZwWcb##&=dIG;zBm^cTSQxd%`46V2HF&r@`<|pPipbd-Xqz^4|-FuRpou9P<Ad1Yh}mQy$8_H3@NyO^+dtJ}nKt;gc=zb^OjkXh0NvCAHD#XvYP2H^D#U58wRj#0C70*;s&nm{UXYKNX1l#=zHh!avbvH`=XQtB+96@IbVKRpH7mlv_IpakMjq`w_1~rubEk$oN@0J{Ij#ZwY)QT|*o#NI@KB)Li)br-|^DkgFe{{Egr5L_NDrgs;csN&J)?_*%`l&)^RVLHlbrdck-1f2#=3CtZ<ti#odl`GcFFzpPp}kKnl~^Tdz*o3#JgI!A3)zaB1rV0Gy)&8ms|`6O(|d+kX?`zX`f?!|M_)8V^ojg@&(rfDjEPaO(hJy0L>QQa7Y_-3z~5@+Q}^soA@0bg13doJ4N8L5x)WdiDNC4LUyXjtw`JYVz`#+5tg5PaRg4dUxXc?a>_<!tz>b{zfU4%gAn=B*@&|7j@N)0nmx@!esGl7GRMC|B8-kNjHjWca4(lJ(?|vS>FYI1;{g=NB1QpPb%^{Cg@&{)wHXf4`_G^>2538|v9F8SiUuFMzKNJOf`VJ?%K+Zpny&9y<iznlVepLxawTWd3e|Z`8Vses?#Fl{n8Vm-tHuOZ%+(8S8^FU><yTV(%}I@A{GL&;gU-n>~M%{=FBJfP7v3CC=1MsHax9D%#VmT1x8Kf4{6t+Ew(I;l8;Q^*p>m){Va7(LUz9#o~8&V;s6`_m+O&Sp~j&ZVmG5p+$HvH6t+x@8$3P72;ot$GU2zw1BVdHZgA1q9Ml+?{3x>)Hka<`o%IQz}L!lgs=HG5#QZO%8d$!Z@!#>bxGOu&8U6F{qLWbePro+w5NHoF??lYmrqe{`)G-OI&m}n1uA^w&kl&Mb(|>v_2;D>UhkKIxGxM6Kc^ku%iuV%=6t*feq=Mm(S9;fuG%{lz8M`a`@+o{^1fqc!q*$ll>O!13x|vQ?u1Nv-(QlEU#%W5{tN3d9`qeYccc6kH#fo$)e*<K5rF!;3yR=tqYDwoU1yQB+sHpQpq_rq;T!9kpnr|tRkD%4Yz*GZ{O5PrAJr#w*CD_8yo{^TFD*uSzST03|H$_kSJu(8QqLeS`0A-YWnRS0mvt%gz#7D<x*F}N{WWVX-rpw)zV(wS^X1I5bMXAAyQ`3Y=ua~K7pZ&jT;6RH<<^>odg?#ElZ*0uT#^1+?TvOY8eUCD{EnY4MgH)WGEQm-q`|**4DX?TSQGu_zR@1-qq_<gAx?+#GEUyglJ~mn1>b!+4dtqwcZ&BoiFfEtnMe07%lmh|m;!&xJ*j{4cI-#$pE>X~zcXl0?OR{Gj~UV|8ST(_80u+sO2c}q2kd_b>Ngzo#i*7m{WxREXN4H2xo9`THwXFe`^vq3(qBiro5g+Iw}#YnVW+I(zH#6#>Zt`a-&;JsSytZHa1Y;s=LWr$>?)z2=K5_oUpU`O@fnlmDxrO}vdSV?N$oj36uvSv<Rapqnv4F`e?Py}RYE_i121K`O6vFdznZQR#)<n%(i&F@<IQ~MAbjWe)TaFmUw`*$sZU%!=7s6&o#`rJoNGViu5*<zU$ieOV}EnbFQwg`4N%8?G*_L$x?(gt_BEbs7q%JoSooRjOOAQ%uJ{Xl=Q?2Bj>q}Pxy~4&v*0_|8STY1_|El8i#RRkEa&=`H4yc3u7}F$Sn(a}r=B%ieCK+5z1<d+=UBIupb+sL>%8(!NBEEI3)3^<JNFUmT*DkZUsQ;3ZXE22^O!zqHhkwkrPuV8_0O@d88HEJZ)n;d{h|l=S&z8=vf;bOFT(jyi}RCpqg(-ez1MlfS5ih{o>;YS%00%h&#J@kz&G-mBfk5$*{k5km%{$<+^_XKfB28=@9A;yo#z3o*<rb7IL;wP#%YP~IJfAVZ%cf~ImcbE66TZhT%_%J7QXuR0-U3?ag$JgYfB`2=lRM=h?6*u^O#wXC~+L;H>E`qeCK)3@;fZ+g!A0^_s`)w&zV-GKO~OhT&kD4C;1DP;e2I$pS}$F_6@=M<UIGfw;AxA=VV=#_0oCXHX8TB{li^9Tkdh0$uf_sU6Ol=<6dB$pSugco%e{;CGeg14l^zj{v-F4id}X~IS=1=jM-=5D;wUDakaR#)F=8kIbR&f$9Y>V48eNpUJ`}-rStx!{*(sad0#UlH_Lt0alcb`C4GqJ9rs85VlsT^eN#DmP4YYLty+BFe3}0b-*b%xSK&MF#nwN{%Q?bvkJk5$h3~v~n`z77JMZaQ#S;?8aj!QP-hyx4dmra{HMB3<%{<|S{onb0K(C%5{_BHquGUTuK)>rtF2UClPs+WZc@EZ1Blmj2L+^F}`@^rl!hhs@#VHm0x%2ymmK6ct`8`Crb^*Q`Q$y~R@0~?`%=df{Pg|TW>r7BpY5z~!!dJDKazB0Z71@vPxWxC~hWVv^Q&;ZS7rRM&JHF4T;XP$sIKJoTH+D$=%BvAytr9KmmG^_x$MIcA?_X^np8sy2v}bTO+D)AlA^!HG@D;xcm~YC+ci}s~JE=2Qz*l-k$hoU)?n?NVn_DQy7%KOd@IU1{!>U){D<3Tv|JD?gYu)Mr-^jc!>sa~oa=yAe8ooAo1@fDpeJt~TZ!&yq<qi2xlK1vrSJ*>e_gbdbSvaDCqS)zi#a9^?QS8&6ZQ6hLwd7BGBLn}tPkYV(?@xO^o;ui7uf=3@eQFi5t+mOa)TY$h<fh~XRDW^<^2^j$$uE;zQ#EpHayx1layxQ&YA14cayRNr<Zk39)aS@e$kjdRDQX4kb7WheBv&App*~Kw)tg*~>_t_`UgXl$QsmO)C#a8+pCDJIRw7p=*P%X7u0w7~tw(N2?n&)H?nw@(zD^D&52n6J9!wrW9ZI%!BzXvV1a%yF1bGbgUGf-mEOjM0mOPKThCGj)PTfpSCudVXBxjSiQV)=~lJlvD$@yf9x{qv;^E~NoPnzmUGdwAoI-5F`Z0i#8Y;p#5Ejfd{iE(Ysp{^xwpsuE_C9fu@QkRfZ$&;y5$&<-()VIlT<ap`~ay)r%vG<(IWb-0VT1H(#O(rMvomWsZ$ScU1)J^0}a&ED<$ffQh=aLJl$H|4{0_sO(TaS_p$a|P<-pOS1e(DMGe)1veG4dhuLFy5*t$WD_$-AiA$-Btws9EH7<b~8UvaQR>3&|f)XOcf4&!WyD+nPk4MV>}YBu^txpiUxBAV*WjlcUL_sBe*N9Y!8Sj-n1EN0A3n`;rHd-=Kz(-ynCTzDDj!Zb5BJw)I7F3-T+}#$;Qok!^jJ{0g})^%-(qasbtj96)YPRmsiCZKyTLZOATaEwZik$u4q;@?cL5VY0cGCq;PD08i>q?M3cS?oACP_a=9wHYIl?x1u&6w<0&9zD#aJZb)rSZb%NIwj&3TgQ?xg!Q>v)ZsZ>1&eSI4&g4L9b#fs21?9n>{Q{HCPkT~DYB}mt<Z|S))Cy!<%aCpLB9|qXr<Nv{Cs(FEL9R@$L9I%zL2gE^LvBWHPi;wVPwqqQN$x}LM-3<UBkR<`WStyI9YVHs1UZsCoH~X)oIIKuOCC)gOPxm^OP)?mCr>A*P_xM?<W<zI<W=O2)O_+r@;0hP-bUU{%_G~IL%zR{?q;%ihbL{JuBUDwuP2+-)nt=ApPEXZPo6@ZOrAoXNR1;;BpcLtvO!Lu&Lt<1mr@szmy#DN5BB55Og6voNim-EjwijxWb*<~3hPqJ%h&rq{R_f_Kf^wdKJ*U>&L<zf-V}fGq9@kBFFRpf9<%3`XCirF1DUSczy1YBwuSB'

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
