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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/67e2e51a2c87480a999293f3c554d61d/part_005.stl', 'relative_path': '67e2e51a2c87480a999293f3c554d61d/part_005.stl', 'source_sha256': 'a7daa0cc89b7f37bffffc1c6c206aeeefc09a69d9f2238020ce41a9f9f9377c1', 'input_faces': 238, 'input_vertices': 177, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11986872553825378, -0.013245612382888794, -0.37378817796707153], [0.17695969343185425, 0.3966901898384094, -0.12111175060272217]]}
GEOMETRY_BASE85 = 'c$}q~2~<_(7RL`@YT}p(qM29I5X5-^74is*12Q-elo(eg1riVx2NaK}h?HRtkTQ5hL>zFae2&RcP#jSZG1KbS(==1FR%9-H^3J#SA3MDD-db<Hch}nM|GR(o-DjVDzVF-v_<LJ5v61-IO*%EMQ%%Qqk|d&~WFsX-B+QKpi%9Gn8^6#(YD>O&HRyWZ03ZK%Eu<tV*&#e4F)YDhxWU0K($&G);1C&?FgIaFY)D)}c!co1W_*wsq4|lkX2eHm?|Th!ad9>ba&$H<G5n9O7Fr9+p?xPxg?iP0HB#vFW9P(s$+v`j>C|2Fr5vXV;=MfU&o70l*8<p&*hu;6i#qb<R5$X?m6nt*E!}dQ^rrU>;mhMLQ@+w6k9>92K=Rce-MN0+@MHAz7J*bp?!STSzwS!DbjY22!)6Q0S8siEl(d5d*Qq#4`Ep_g`O=enTqn|z^DlUOPI~%6HT7?~@d~}K?L)q_HKm5?lxLDJzj<~a`S;5x-xRWmd}Up$68hZOv*eo(uDnYA)?fF~=R6lt9qH>O>>sKiUuxbnL#W~Vt9)F?Uv|^a!z;NT{}7&=>s9jQuBlYVTs4j7GvRhI{oHI$qx|lhO3AOf#=hDzp0w?2<f}my?BAN3F4P>qsEp5NGy65W*HZn^E7Xs<M{n}g7?t`_jZdnne*Wkk)MxscYQ8R+7wPl2ON&UKo%xdbd2oW~bN4X$%BHAGw61D*k#8Jp#rd}u&>W;Q52?Q4h|_j@-|OLO(zunE=<_!%x6%8@iPWcQekSFsKm1-mKY#k&b?V;&*Rf<a`O?`=tEm6OS*4A9|DzkJPA}{7M*ib|TPQ!U>@=P4kP!A;hAgB0LcCP+U8bUb1@&WSKe&?o<NoZA_N6%++!oTD4PLJ7yB%Fm$5m^tH1bo*Xl}A&InQnV_O0YgD*5JX0d&4nc0T)gp)^mUI*R>!P1sMW;yS~_s2|hM|1eR#pcu-R+l(MzZFx42@~3^nbF=%Zir%lgn9K87OMR*#O{?|3diZ<FmnZM#^EK_y)%U5Kt)n^y+o~M$2cM-n%HqkFDZfiuj((jem-~>f95$|?`c9{4T^U}jtkL_*oq4qW4YB3yw>`3)>TGE8A+6W**J*!A-SWtnTOX%7#`(|5S7){3{68aj{Y;v~`3vh(Nmm}EeoP&kkuR^h!G6~enwvEGSDJ(J*-G|<Qu(}|e%RPY9Ybg`@0Thc^3|N1G&f^q7_ZyVq04xmPTfrP7k_i5k)L{;uVeWozW*$Hp^!$}@P2H+pVvtfD@8wN<I`}uF49|-OZ9U$S$nXryhXlz!%Y2{YCq%smHQ}#=W(9$)qE%RkNl1Oi$`c~()h10>iw7dy6y$v2Yj|HA?^4o?Q8Yi9lBpBWu=Qr&y`dE%AMoqDKD@%ndf$iulusj{Jk?bo_(Xj_fM;i{C$yVzmnb?=komRY<Yb~3}L_7XFUItR_w>LrTzbMJ<pEi^%m^Re#8D!$6x04lS{sme2eB|c>E*p3;Xq}$shhL`HJUxUjGr_^IW!0<Nfu=R6g$ezpT~wW44as^-yNBj(qHQsc1D{mxKMuSAxTNy(Q1!ecI2N`fgZnrh`B6b?-HteXKY2?XP(KSSPUGd;%R`?Onv{bIRon<loLDUq*dt%+DM2=WDdv$#vTK(EU+LGF8$X=5^x!Q^K<-f51-m>#M1b(z@#=%3ooi{irtVqk*S*eLo1M^`Klma*5|QK3Ctr`S{H%dS7wheUbXvQNjN7K+gZx$aB7Tn)^H#n@7IiQC>fj+w*Z_dgPP8*1L-8)Y|dByFP;M?^0_&@}*OkD)s)$@4MG3Xg$kw>N#Hu;<>ed#NUt4CT=5tY$87=q!rL{O^;`gFMFTl=Y-H*<QvkQ3n{<w9?e1C`-JcR(-)F2TP~(La_{Z5U(Ay}X5Zl)@0Xp$>}U1ZPIW%*kWR-PnO@q+4=SO4W&bbf`^y;Z$iC`A*G+z4Mc;R3x4!I~yke-IY%8wwgA4nv;dEb70%iKXGpCPY-ypA|dDYLM?=|zZ&?2h4Ydk-<M4#gGx<7me_4knP!%D_Uo|`diH`jNg{*~I5rH%aOYfSXHBc<H`pd9ummSxj*%xFga8*db{@4qLS)^T48uCse5`zCkl-_(61^>6HXnEiBn>R-AL&;7?=E1^CL=hrmqKd|XudXMKlwc-q~L$CP<>HXK9SLkyKDz1}nC_1F~)jy`!(){A;4pW^2?_8ku@JY>ey|0|O!QWFyPIH~j8ArM92wMO0oLRMcU$u|ob#BM?W$$yG-`|#>d-oUfee#P7<V$;A@N=)99X~hTi9SYt{vv+PzpZe-@9bk-Ka8KNm;XZdXEi&O^E)i%eYCfp_pfal`z0=PACUV$Xa8m$`|=v{m1x)6M*dKl>Zm>gc|ML)k5k^Wjg+s3x>xIcb+Q-bo5#5D{!Po`{3p45+~5wE^}hV;ILcQxb>jPc@^11Q?qkN;7L|Hm-amo++0~Tq1Iur)9}-6MZ1_D$d3ckLJ7+xk4ZjCTGx5Az)Q#&rTSs$~!!EJE>S<*ozi#3QdS9K~X#P@&ANjIxIQzbjc>bA>IKSSGkGpsW=RbW+zLG3)pPg*^{vhvHDbJ?QIhtG4-)UW$>kqKs@BUS)H@A{}Q&JiGPVwh?f6c4a`-+D*<ty#O$v6LghVv(8()yI{cr^0Wcz3=JOc+MKlz5)~&K|Tc%zf&v(Rr<Fc9QbO<WU{<z+>89Qafw%l{KEc&KKNfzo~)!QH7MRgxXf>ec9QIfB(8`O}@Fj8|M$WO#4ph){%U}iZ|J>*~fkEXvO|QSMFz~A3x6|6rR`na?o#dedVM)@{LbMkgpE*qw|vef1~SST9#hM=l?rhcj@6?$~Vaw<f}h+<$d&d0r}=7ndB>;X}nG>#`D~suOna1cIWk6?n%C()dS9V&7pkrEkmW=mj{mJKDXKM^GS$jIj@_+d_Rd?!u#=!G3+Nt^8ML)4j)%dVgEpX{(hg<gXg?dAz#f(uF}s_O}|UN@`WGGS?>9O)|E8wC$6)shUeV!JMxXW2TxO-V43fq6^r;jkXLku-hb;xz9I7d^-}*ve^qe|9^qMRElDC?m29NQ8M;5I2vfWo^xywUC2H`0^(U2qgIxdLKdJ1}df24JK7`<%2*Dc>f|C(~7a#;LMhMP=?gH;Z-Mt9G`=L9*`@tp9jo=dSdT26uJ$NB>0eB&JK6Ej7K6nu{3%m%tLD%aB=w9#?Erx3`10i@SLhvYr;O+>)9T0+FM+hDaodTYMx<LrR;n1nzaPYg(QQ&vMp3v@KPjF{w2XJR_8|drcHsDUs!Qf8dfx2D?LW98hTBK^R8zFcPbQxIa7H~fDObEf-pnJgEz=a6GTcKOPTTpi^Lhu^Y{20f{2d6^UfY%_ufeUnX3UtRU(DhTG>$w2+3h;Ts*;;JZA{QZe2SRW$v<O@b&Vzmm&I4yaSAa#$)i_QzcsVo!oPm77Ia<utA{`n6P6w}o27*O?8ggfY--oUQzYl%~A$S^eGk7!VO@ju4L$#QvMHoVG5;Ovw1dfDyfg{0VpzXk8z-^({;I`lv(AMA<;8t4nhYo<Y1`hxaLkM<)T7#XyU7+p2UBJ#zFR(LsBs2m%5<C$)4?GbZ01X8PfW6V1H~RI4-_U<3&My?R?vHT8xwZl~%*0JMH#gmE-E{MJ(_JGs)OADMF!UUNb8?1ufd+t`pu?a6x;Y2nJcej7LW{Q$f;%Dv_d*Dk5rX{?g5N_3_Js}s`)Cmi_65HO_1AsYAN7QK=<0juj_ZM5ggSzS+UxqXNAE%%bm!uL^BV#k3UvSv1rI_9wuRb*ZNV*}j^LJHJE#ZP4m=v_4;~FRLW99Za4ggZ91EU~-ln79>F^u+_rdx3VAg_NwCJscD?)G|Xb*57a8GDoa8GbQs5`hH_-*KT@Y~=C&`ID4;K|Uj;K|@|=xrSO9S2`<rWQ-JSc?#>K$n0Oa0+tP;d7bbPoN)xKLLLTO#!E%j^O5!c$k!=CeT;FO~4Y=Li+0^*b-_5wgfkYHUl>WH%BzXab{`}two#`@mkE$VlFfeEFw{h51=vNc>HV@^aJoLa1=BK9EZ9yp;6$O;Am(JI2xP)O#~<6cnQ!ra2!4(_%$usYw?B_1}(a3@h0>Qu!wG2h(~*WZwpHstN-+`)4yH{T>$+*QvdanjekARfASrz*2`ZO{Jmch*F?KumNblE;*Kf(6Y}b<9{'

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
