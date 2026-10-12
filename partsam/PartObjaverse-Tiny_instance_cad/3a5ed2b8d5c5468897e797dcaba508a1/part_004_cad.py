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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3a5ed2b8d5c5468897e797dcaba508a1/part_004.stl', 'relative_path': '3a5ed2b8d5c5468897e797dcaba508a1/part_004.stl', 'source_sha256': 'e98438c029e90699845755a6c374bfd5d04f9b86732ac4c806f1086605e110ca', 'input_faces': 458, 'input_vertices': 277, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.025868291035294533, 0.2399137020111084, -0.15593092143535614], [0.1400822252035141, 0.32076436281204224, -0.14732854068279266]]}
GEOMETRY_BASE85 = 'c$}r136xaT5r$tgY$^ySY7$9oP2!*+Mnxe;LK{Ry5KwW!7#NmeQP~D0tlDt{gNT3%0%C(G3W}mID8tgCVBEj~R8+tbSzK5YP(T)QtNW|Vdo`VNa+2ZHsj9#0R{gK;efQnheQ4V<uVU>W`*(V9>4|4tG3Zx8AW|);9Skfi8ql*#VgClb`wor;H8Z&UsUF|@`m5Wvj|BsRq4`}4`*$hIzc`+MNw>!N_2c>7`V<W)>eRbqpQ5gXf?wY0_Wp$q@86?S-$LitJ-<<-`tb|SsvjR7{~!O3bre#KhEHlLTz0fyB|0&w#~VwXE;!g=viQj@r)2Qd#<3ARcx*}*-`_NYr{~_1jUQAko2Ts32(I~4k1WlJ$5XYUdGemk;K_DlGI-gx*;B%N3fdfA7RHrN!Im|d_*B6=+4#omS7!9WWE5APr7NR2b>o%uqIk1)+5AJ=X7QbKo(SiUr_YMuzMrFh$cYy`_t~;Y9`Yv#%*@0mrq+2f<Nv&TWq4jZu65@YM{%wzzV(}B5uCmyuiBA`5AvI*a`9K(^0&D1Pxe|6$)kPtxao7jtQDzT^H|Wl_q1H=M{&D;EUxP(9=~r|u5}w!*cgfT>-@Fb=4J4HP1a`kD1P?D44$l0CxfST{VP78Ll$TKm#v?X!PA8&XY;^cam}BGzr_>qS3FU#YX(oT{!_E|NBAV^o5$gkWc>#%g83Q0`H?l5Jj{#Yo+tC7xYkXu{tNOONAe_CCyM*Nu}&<WWSzvvkI&W}vS&@W&x-r}tY;q&&jjn)$J2)t>)GS<AsD?m60g@)@cq{8{qpn9oY$qey)KLEbtTTITb!%UirYS?(&rZEoJYmYJQh53Pc)C-7vOeXSzOnZ;&xr74?Yy(qwCz`W}T;RFNx&Wc}!QWTapV;4Q^MGE5FB0{zUywCAqFwaeKWM*Xvc>UT^Ziya*rdzsF7g%O)%;$u+-<+xb=8-bWs9IV_u>=SX7U-bjAG4#CT<LxcNu2(I~4JV$~}Z5HLa?-aN9osT#7osT#7oyX06r?|cEJPyyqnWska?js`WC*FE?lqdaB-1f)fe*Xct{YmxP9LcZqt9ZHl7u?RT$IbkvYHW}6&EM~eoAs91&~$Om^$%Wd{Ttk`e{j40%f_@?oa=t{xV_(l!IAtrFJ%jtr!)9%Eh5iT#nTTrDb0l^zFEFHXCC|f-Sb%%?^-2#{#3kZROI}rcw%&&(p>S$Eged8#RuDFtPb}<@$`<ZtHXWpdF**WanrX{t4-Pb`wnK$Z_J~|>6@NsEUxDnkKa8ZavoMZ{n5##x$<lOZGOdV{=}57rMdD4pHE#KUWY!Oc}$!9iYH9|<c#gB!|TxVG3(sdHS65sHh;N&{(@?+hu4puGd<4w(f0+#b^X|QT|YKn*H6;K>-tHW_;Sx3#mzpDu23_J7rz@hS1az<75kFMStt7b;_=hoioCxlo-RJ}L9YCMU77s4PRiw9G^{jN{$T0-*?G78bzPbKx=s=%fAY<Wnf*Cw^4ope^Edmp=Wq6HkDGnF?E89={_FdZ;(p)bxnpsCKk_*J*Y`Wcwf{E1-#<-$#mnWV|2Dt&KVkCwec0qzJZbW4|5GNveJ=aD=DBQfo8LZ{(=*#=<L{gwdH+@1&kN@kAJ2WE@4p^rAJF$-kFyVyJ-9g<&wZ5O+~RTOG0wTg<2P+sm5XO$(w+};;eOr?f4%Q4f8CcXf8CcXf4xu3@n@Y_{)rJIN^|iH_706auRX5o%J!f8I$`_IKAAH7b)VF8qrWcpfda!{*I~l&PnXqLlZ&T4_xe2M-0S1bx!1>=bFatEx!3p8oO?ZP&b=PD=iXps&izMmyZ=~R_Xm%g{YP=T|9IT&KNc^S-|RmgH~Wv`cK@+>(&V@MkH_tMf!4L}1qQeI?f#S4^;FL1uj2Ok>v8k^^|*QdDsG>@9yiZl#qIOg=Qqz^kDKSO$IbKCU$1%odfYsJJ#N4EQ2yrm>-n4KugA^vH@ReH?(>`C_WTB3?)(N`?);{C?D-A6-1$xO*z=p>_IsPBOQY*Vzqe7`oc}GZ=W~yn^S|Qu{O@sd{<pZzZ_od}t~vkvcys=@c*5kj=YP+~ey^o<?e|&+xB1I`UwY)@$okRuL64jFN5$>?qvH1c(dRMmkBZy(N1w-j52m>NKKY`Z(S2Uum%+=uUxSx>zt%kA_v^NiU#%u~yLIyZlY&6xn4oshtyAbHD*@$Cb?%?6dN%y8ezIzKVdMYzC#$NCLuDs5om6mgTp&NS1%dpc_G>4nIQfl}I!;b=BA0o*larmqxa5jXsyM0Pq!MFKWxS02CF5o6v5c3od5o8_Co;a4lV3PF3Ht<mv5&!*`09+Qg)N`G;-u8c_fp3dIOOzZCto;u*~unirV+Q>NwJf)PJZI^)qEyn4mg?b<Vz<D7%REgI2r8Z0VhMHb}T!-meak!ikwV$GQ`P08F!GeKT&5ln2Zy?GG@G!N1V(+zY6zx@RMA_`1~pOjfe9A>dd3|YU&STTrYSFzkc{bs4tujQDYusAE3riYRsn(YpMS#^$u_yLx~?x-d@y}eB<CW9WKT6VK;UA!L1j34l##o=>L59yh4pfsIver!@y)NHj%rSS~IAz8}4(N-%{4cA@E+z+c08YChkkPY^E>8<dT@N#4R9hGjn_pUpP;L_X0kDl^R8Go=ePFK3_}BT59Q9SO9(yK3~FTI&nHrMZ_GSm(%J05PG+Uetto}4sZ?Qn5zTeGIktuqhnuTyo}vM+{<tu$92r5w_};pe&7$_j|CftJq`S6C!?GUck(E{+M@e|z2@XYCnfl5i{3-L#6IR^A->w87h#Lu>SPPP+M<t(Wo^-i$t}LxhpAP9{@BS(e6>X{hPzzXT~2!At1Wr}yoB?ePM*P6Tl9nQ63!nvIfAdY=)Ld~&L=qe8DDMD)nZw0!fOKcXNK$v@ac_CQonb|PQvFI^b+bn6S9}U=LkB0(~*!Jz(=@=-bT;FS9@ECt7v%!PsCSSbQ)d*z@Eiddm=GQ;4IiWe6^n?MtJQ7`wCy}b;N9g^H<d0796#|B4#o8Qep$*_fmHqT$0otz;y}NJ@nyY=JN>iw}?JVkNYz(GAE;$$GaGNnDH`pEAt>@A7i|X9nN?eTf%s`w`84vh`kVB>__n>{%OX%hAp2x=VY{#e>iy@Uv1HMfW7YI6DM!rt1bEm;w5&HlV$j7i+&SZ^fykv##dW(^;p&x9gAgii?6omAE+z(Gbgk0)fT-R?s8rCIO&70w&;QI63%x!nT4;m=!f7XoIiC^A(r*k7X2f<g!73`^5Cwv=;LEqZo+Fa^=F6d$?)lezL)xaLiWAznT1{fk69sm1$=~?=!(=AU+s$U$wPlj&+<a{w;`^g-*PeqUv1I<g4aN>=ke8^Ld*&{3$`9#?dOT92xq~z<Ey=%7~v(Hw^RSy;HbTwnC0Ma5nGY?AE~<@F85M<AlEg8H6?wJ9#p4q(z7?|^QWwrKFrBz=J6iJ#^`Hx)=34%PGbBWtiwKxeS`6GZ^=6U1bZ32*pK5&{Bw+X9a}zo!O0jW_c?h2Uv1HU2YcJe1}E?0t1WsT@e(`L$vgOJi+&GV^iC%`@YNPwBbK#ASBhnGi?6omebg2Gxsw<1)fW9e+~vAPIO&V8w&+3d63+KKnS-yk=!fAYoHshD9LxG@i{1|};auBE6}YP{x@IiPO?W*?{TD;_lkn+_9!dSaA$ufz=Ac)?V@}9k2_NAmx+?X>SGy{Fs-Sn#vnnBbSBR_VRZdd)YK#5=UW341!dE**%t|;5R)(+kOT<)#vtZxht6fHn@Dk47QGZu()c%f`_rX^YTb20z)GdR{NNNw_x`gXK`XD{1LEofj@6qRtte3vb$r$Ew1Y;}F*BY#o%8Z@Lco};i<7Mo-jF)>$*7*kPckso20$<`^V9eXt@>yFaS2?-dNh^G{MPCNi&dDuKZopStbXVdf_G%~B<Et(DMr_fYoD|@zE&5h$(cQ>h5VE^b>jrcOC)eVuE&3+7%XMApq#3^2qMO4@IA7u98ho`yw}h8){+pBT_-czTgqLu>-ANC8wME|sH{sQq`qzf+*6?YDZbAKKA-e^9u0gk_{xu=HJ$$;Ods4r9$nFWB9_Y^WtVhW19O5eaW+!d%)fW9%cr^#R4qxpy#I%RAU>)(*zK)ola2Bi!zS<p$=?v#C)bAX!yAX2|_|3%j<g-HRc7#g{YB%S)glkv&(1H2vPS0+n&(h<|m=~FotC+_t8QYEVGPV=rW$e|Am$8>KUdG<Qc)7O<g6tX>`+9t_Tj5K5TgJ4*me1-t$#?QwCuiZSE&6n@bDdo1<UD+}MPE$3#GdWs5BO?}J|A23ADuMDS6g%fTl6L5ZXB{Nq1JimMot>wt1bEhxXX3@K9JvsvcB4)&w!V3{+*L^@YNPw7hb~oA}3Ao)fW9HcnRmfIQcWa+M+LooA9bf{RSbs9(>~HGpQdB*=NG%9CSnKpA)hh!lwzkDfOFRw{01#P&@BG{a1&he@S_7jQqz3J2Lupb9iL2%jLg(Zriewe9s$HaR21Xm#<~UgMR~_Zq8Z'

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
