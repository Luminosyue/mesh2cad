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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3acbbe6269234a22b93f7e44aa8b1798/part_000.stl', 'relative_path': '3acbbe6269234a22b93f7e44aa8b1798/part_000.stl', 'source_sha256': '3f8121274f0b643ff5e6ea3d3851a5afadb8b6a0682f1685eb54608018397067', 'input_faces': 360, 'input_vertices': 242, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.03051917999982834, 0.07779692113399506, 0.07318591326475143], [-0.007782200817018747, 0.17382721602916718, 0.12224428355693817]]}
GEOMETRY_BASE85 = 'c$}r03zSdQ9>>oN@@PVhnwxU_Pc_XHr3{j|j*@7^m`bLUBW6?>HH=H69BELL8HO1d{Cnsz;d+i|9Ms$tH@Pl7#Gj&4qT6$^R^7AD{_JD#fA_9+*S)jWZ+$=WwP)|&{_TBUd&$nKQ@5EVe^RZFP7O@CHpQ|;Bw5X@F?off9~zuD>Y9Q_#wA!y17G|ooz?rU+p}{MtT9$``jEU)gA3C;M$$XwcSvs)NzWfyIJ$69!N8G)L-K^*ebDexdA>jD!9kDY`M+nhY1^h%B=gEvk;fzd<4+?$1$UUeaI?sz?{90m_~Ol6UL(}%{>=j6+jU2+)qN*(>jJ&Ky)bEApp6TR_HN4QKx4f&RO#*AMY$USy}GDMZy%lAKJcThr0=}7(F^{*&&CzHAGxy07Tx!*7#jHAp_euWdB41Nb&zNMRM~(1UjpB~bamj{3CU*vEvBu~ebv8PH6`#PKmIf?=zqeomBH`5`>i#6#*G!Ya(;(*nC&~H1?{c<o95~HSjUQF`|agMd*|SIS?~F64Bu<nP}a5V0%Kfn%yQX&?1ATv_JgMwz8W_&qDs~~=b7jAIz*3T)#$#egEgc_;JdxX8~xkMl4bu_w>NzE?qPxNG*2@8$hOXMKb(4duJEI^eS`j;u_?j7$M!xt*Vu<wRJ|GWx9!%s`aW@H3=Mo6Kb-HFlk0<g*R(WzXL@R|uVNKPD$V-Tt~Y$@8R;-2@STzkm3rNx8C?V4E-W+qsq7r|@AT>%_|B9&f_d3ReS-bwb#HC7w-0WR<7U>Y)axIquD4eARsFq;L|Nz5Pb!Rlnq|s)CCoN_@9TX*|L%#04c|#<DBFK4eKoFkvYWgv_S>faadP0twl*;Q=)_@x?^e7r$7tW@ba1^mWtE0+Z~ImDQ!;*zzP{0QM>YlPg|FIMAGMbEnQ_h>ecio_UJBYfg*irh_pC88|A851KFjvV`#|@TvyJOLCsF$L;o16nIo;Fb{Y?3)AFd0l<DS5eE?e++kbgzhYQtZ-$nYa=Yt3;he_gBl;eCetq?alEXkyPTdOymKOs%`k7&oJOw!UwzW8cetm|ks+Yn{rK{iIgO_ES#>?d?5VgZ2@8H81;E`_;N1Tbx!K^mD;nS?A`@nf1wQW%w$8)sOO3{?_o0W_#+U+Q-f*H2Sxf?3DS}A7bQVAMY&lJkipuv(q(Luh^F@%z1e~uQq(fb^r8(>>uCxrAyGiTRvO*hnpDl3ftqWc`4u7`+d2dr*q?RIbVF$f9(4#na}op<;HwF9F_jY4W{2aC773oug3Mxn<=lyWebh|BW*sE^{Fm1+S_CM$^7RRl^g5z-pN&lPu<*}$4y_Y7ww}JL(Ts2ow8h`4(k43PtOYc@IIfPwORMo^&Z*YK>E|N%=u<)ll#A<v-Dff3-a-rObh(z*i^%JpBQ5J;rb3pk##OiHtKA3?z2w!)pcrb$O?RCc)fD{y0eqIN>x7BSM;YQ($D{SR^Y4WV9&4Qb1hH$;dPXGTHg2Y)qEpgv|eraYF?KtmGin|r_sN+d{xkYEN7?Dzf)B!pYOdk8~vz#=yqQ|OWzOP?$jFH59=T2hx_EtG}C9FsP>Ni(k$cpWj{wc&Yq>Oi@Hv|wo}Y`-J2ZT|0DR}ytr>$_~AZmcTmnNeV8%d$g7)WJ)8G2^0cS9az8ZAG{$unRR;Bp;D_rqqgv+QAWix_N1{#M4f2WAPcz0<&si%mMfP7ZCfMip<UR7af4YJ6Z~rCudx!UG7eB2318MSp^5dzQdfmKzN!$;=nW@)VUB9s}56m>y_pQT*ANC*blfQbe4*Ox<otqDu{ZminyPxfvsn^quwFuTRc3Ar1{q4Qh^7*^#6*C{6<FW0PMn2(v?9K6J|F10!*2}^V-xHdxmiNz^0;6u~{v5?u{j2A!U7ch2k*VWkonP)|<Y|rUD)U*;-pD7iCqcgF;D`BaN?xP;YP}*o8p`KaMTW6n(H+T#AMW$4rt-QjYi_KIY9IRQ{RH2ho@C_db=oQGru?}3m^&@W$lppoDDx@#wJc~KcRzIT<L|4=kH4=*l&{u(ezjcpCr*|b`<(X;w{VZy{;5Lg=dTU?_~%IEo~po)f9^zbr5|1|JQtL&##Q^@>*bc|>tf|LHT-Zt#QEX<kn7a#URb8DSG*tI59^HNeX@s9PxW5yrMEKc%=>c`KfK>o*UEk_YHH@$>Row1Y?f%wE8bV{QM`|ZzPf+nM;iZ7s*kI_7pw+HOZ7a}b?u(sUaF64TMrt3xX<JKa9n)n#|@=Mp7`GWN#?lfJ2&2EUs?N#O7;D(-jkzyr62#j5PdhdRNw#MdpLgl`@izz-~X++_ThVbO>4ss>tCI0_Rn{Xl`?OJ;qyLh{rZ66tM4Z3i>qen*NghjvX5M4v=84)cl`4?{W?<Lao(oA&l&A`zS}F-8@_rEjNbdxvxd(;@iHcxKHs5U-8O+A|Ggir)5dJibJjih>2$rl%Q=8^K>BJOt)Fvb9hQzT+Q&E_uwLjp-Iy2O>B^7)PPh8KKF!FJ^MUBu35M@*4&dUea|Vxd2IuJFXY_q#b1q@;D-C>geiAv=Jm@dFvePqq|LT0e9<%IeeSOvWiB}~3_;Z8UfU$<}a&8dqW<Ra3yE>oomYkSkjLSKXgCBq0DgSrpOH=0={it)K*kco>==HJH`PE%5jrI=bQL#?nPuA-e<9y8eEq}7!-Wnp$$0A3snQZjWxtzWE;}T<C)cN7cO(n+lK2o0h#a?-_#MnQa*V*{LJ8#5~KX0@r_BQ+Hxf6AJ8|~Hkr#-rj*}w9$4?JbmlXFF<MS<bloKJecT=<l}Pdv_JZTzr3=b!G<M<?m~L7nT`uU<Y;?<YJ5ez4Lt`d8=7_l<Xret7SVc8pCh_M2#*ZJf40wyEwC=UjhEel)b2S^0ysqjq76AEp2PsQsa~|J6}@X8UXZ-=p>?{2U$^^FpiOD7+MX1zrljj=liD4ws_Oz@_j=^bvR@+#9_E?hSWEv*51qt!N+kRyY?O2oGdFx#$z{vwlqRV?H_^7CH@{56>e6Pev!gli^Y5Xm}Jn038YsfOF9M;2ii)^nUnGIG;R4-s8~m@HqHkG#}3AZw1?aT<=E*Lhx;9Pxv;t0387rz~$&HxEx-BE{2!DE6|nj3ixGo5&SYd34Ict1mBJJgYSlKL2cM(ZnqGEi_qKP+n7%gS`L?!cM-Y*UO|3E=p=X&c@$CK`x)PcuSf5LuZMf0L*btA2y`?&0-l9VglEBv(P{8vcqKX=UI{Nkr@)KgC(&{6lW;%uVOZ@U!TtT{W}Vref^*PL)|ve*cmR64b!Pty9)%9K&Rj2oC!;g1GuM~kd1$qD=6V!7A6;&pxn>1Fi@pRu3y()#cs!hs_J{j3w|v^a$iEAn0K0I1+AQbaUxb$tg5N-^;WywibS7K|4?~B;!{A=%?Qk#nMzj-rBYZR34Zaz^3+)g0XD)*O?8g{C9zq|4AA<AHA#fgCh&~Dz!X@Zaa0xsEeGZ-hS1_)~V=DSIJQbdeR=^eft>8cT@drO{LdEaNXd5^gZi=>oo5D%xRd5pA7;OnRhR;Q>hR=ml(6(?2d?9)hta26H-H*%t$V4xJGvRB{7VtIjwdfz=YvK0jrEq(=2bvD|fcv6X!hPXv@)7xEpxJOXZ3O?tkN5m|75yvxD*PI{9exd7h5ij*1#d$C4sU|Dp?l$N@D|1udAyHqgx`n%fo_4f@VA0D`0<G!o6&>tX83LNEBI~r9rPRc9k`Z$M86-RtKkpfPtiBwPvOtdx8Tp<V`wd0%UFWP`mx53c7)(}{WyYtObFhIu7P*L>(R0BdiZ%l@E}5PN3<Q>5x#;De1RWlqnDxW;CAG386mhiA$YeohuwtWFZ}ot{Tw|4e-3|yehhyE??89LJK%NbdUzc?7kwU{3p?l_*nw|AJHj`>Y3LPj8hk!_0en8(NUL2VLhxCH;QHug@MYAlKDry;O^xakUugZPTFzw->(CqE8^~4FB#oM-k*liV`PBG)a#b~Nq^(OM#%jdaf-C)az>l?PXZSon4*2l_EHpxVK%2F+7v5popM#zU*Z8r^k1mAZRCGU_3X9LUCTI-Z4<Gg85aS%eJ50nFGe-LZ#C~$!&v+jYyU2YP`Kh_oP>)J@4m^k2JOB?yYv3B@HkdYpsmoye&O{e#)rC2$dZtpZROWmh(Tp0Zx|~A@Za@fbh{oU;HEKv4(%K)QmWS!<DB1w7<3~L|9z!pNg<b~>y%!d`02b=OLifNzzlMc=3qJ;*AOwF$2tG*&K8}73ABXp$d*FTWR@8&H!VA#_@Iv?=^j`QLxHWnm+#0?Jy%@d-u8Y=#>%xg>9oRw>&^mA(>XLw-fGzYp^aLz^is>T}R^t|HxfN^q7i)7Y*6L8K)v8#lXR%iEVr^ZD$)T7$1dDG#@qH$~)3UP?5}VcePyZG2%#RyPQ2&pS@qcL^>*#-3;P(|C@?>Y#J4+TeF?jiHDBg~&e*sgZqR9'

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
