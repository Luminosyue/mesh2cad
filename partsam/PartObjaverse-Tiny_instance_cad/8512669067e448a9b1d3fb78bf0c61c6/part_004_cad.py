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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8512669067e448a9b1d3fb78bf0c61c6/part_004.stl', 'relative_path': '8512669067e448a9b1d3fb78bf0c61c6/part_004.stl', 'source_sha256': 'c1a513ffede2ef85e670bd6621bdd7b10f2383ffaffd25791edf563846cf90d3', 'input_faces': 346, 'input_vertices': 194, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.032805513590574265, -0.34545326232910156, -0.10314252972602844], [0.16777795553207397, -0.019880026578903198, 0.011935509741306305]]}
GEOMETRY_BASE85 = 'c$}r02~<_r6^0Mugh6lsXU%iO0Y`AaiAS8HMvNNg@ElN_2!aTx$Te|}I1*>{A>tfGzyTb%I8|#RYSY9fCV5)5w#KMQYZ`50@A>ynMOM33SIb&^{oniFe*2!g&$;K`_cXM>dubmffA!Uqo6h!`Rg}`<seIJz@aS1nCWObdii}EdQ<dQBzam}t*06!0Bi+<&HP>%qc+7-ozs@$lu9G_X`P=*^y%#+zdR%1Kd(jiawcmT(^q6qVkBJx;6>hz5+BPWA-xko!-<D|mAO9*?LvY-_><qTlNKQVNZ>cRWeV10pxz1_uQ`^H=1OB{CtC8)q1AeCqCi0Gq%F^n(+9DmkXWi5KwK*nttyX8JtMFBR4C=VL-`ayZedg^%zWaA)^=o_Bg)OM}<&Is*ukZo#?G@%8M7<N0cf+sM0>1O&pxy9O4fsajb=0xt*qk^{z;^L_M@XHt>QX1bC4TKPm*M-*K)!L{f%t<GP{+Lcmo<2QaNr*Jy*~dfUO$|&0mqNL1Yflpg*rygmF@W4ikp)Ea2o0umHpSDe<5Cb;s4SO`6}%u>eyO;w-5ej-=e+|TWSa1uRMA`>Zf-`zBxNMP4Xk*8#Oi|-;CSv5&HJSCGo>v$T)v}Ydz|$AO11w3|V>={!inj&(}`Fx9^$;--zqK3h&ps0^dj}L>))ewG6z!=&|H`Hjp}ji#B6CkE$F*ex<T<UK#P|r=xQN_$oV1#@V?h#&3*h58sUOlH<<(5bMO2GWy^vedzFFBj$1VY^ifCM*KsU;5++X5&wBl@t0(+M4j-vhfwE^c@4+)ID>p6v`Hq$e<~fmvDITa#_JOT-|SsQ&TB^dRMcM>4_^(tUkLxkFRM|na0z_lUaZXfC+BzKd}CKh{qZxUj@uZl2iM+PQvXp;Ip2l_IIg+*?@~Ycx%4M*FX}7z)WfL%>=BM@UfPZMat$khuYP;6P}avmtSe{l8{#MI#d+Byv$x_nYno=^xJII!Z@;8P_}qmc_{NZqSK#j$g>`7Z84q90xDDUABN*$@QNmX_V;16bN7smd;7y#DYU_=@nXOXAzvRMsso)BSkw5gj_%B*YAD#}z^=15AF&lkrY8QXVbM(_J;j8#((HPInQSgn4bLG089(6Qd*0K0k_kD_f)mnk^n?1IRA2U(*v48w@1o<jM>Zf?iI^p>mC47VDYo5)AubM2Db>1uE5b7A`rT&<{IIeO8;Jj?xZb<&w_hnvsM&f!gs@)O4emIZI{-1mxbymh+LY;e;<M6t%R}SXUcan^!^7v%TkK-tOV`}boobUI}12}HdCHSg$`!lH1yH&J)?Hv56)Hzx2cc_!N73;*|dq1c6b)+gi9f$KT`$GIioutlpeiQU-$7IhVIPUP_*#C_clk;%=+?nuIxhJTv9yY;#tNP7_Z=Ud%@w?BF{l8tJ<R^9e4C8+B1NII3<du>iJ0JPV<H9Dq|LvEOU*;tG>{vfxKk~P@#P6Fcbsm2W-#PrA_zS;<Z(i<$easfw_$bDIw=fs=ckZ8o*T-YUZ@&Haavk2u#5nh^fN#z#{W<)1V$*T_wBwRrc7)uIc71gW@Aomq_YHyXs1Yi@c^ST{a_kelZqs};#ufd>arkv_7r_5(^H}}b)vB-fBkSUP?de=64+e@K_od`-3!abp-IXH##>dDvo#!!5R|#JwE}IAS4$6i9XtC@+*{*E#M}>-Cmiy12>f=7^DB&x|tj_SSr@%LkUY6^3bFlPn<!15k1>$;fmG6${1a;YjZ?CyV=J$&x@8i6pF2Xmz54kSaTOS$Etrz0^b&z#6@@x|7XS?U2zSjfXXVuz`*auXU2Yi+H6ytHR5B3s%Q6G$o-Nc{w6Y4nU)WLk&?+=suBOTX@_uow4Dt^CMnV09+vCf?>u8UuI<|686%v_4sPu)&H{rAds9a#$VW%CSyuP%Iz`?UQ;7}ldXJXHM1(J2^zSS0$dW={}5|Fq1z%JD^iE-sP!2mP>a?SsC;{${IvK=LCpCBJExv3Q-BEBOby$vTYqVif$Ke96CG8|&OG9gO?3tN+r|@V!=iBIhrCaGm{3{DEPzuF|B>wsR%?B<ZuccxFE4-AqCM&4&%JPHZa|!#Acqmhp6M_c6|+?rQkzH)CYI-IsM}l=KZ*ht7!Y;x`;6`%F~G0=%D^DgK$|@|^J2k2tRR`-&#~yXP=3j!HwYKAjgD!8bO4EcbDqms!GB2G`FYI*A|uK<*1ux5Og9RDbwpP<2`7J9+(Xnj-mWePumd+%z8k`_ovb<4N>oe_;;BHF%NKS^o>_*k(4wbzyp>iC_2x*NfT`mWcfBS#n-J7ms6n0m<0sZ2{Th9~~j<Gt;dfK0lyt0sN<@u+Ka9_~U-9di4`OV+!WQQ9cs;r<yQE{7VJMH*E=$|3f%@<DEase*2H3ScfWoy5y%8U>zFOj^TO6Y!WAa+j27RU4FuK;HVuhb^aKE`Y!*o*w2l93*eipzL0h9y9@VO^LOhc|5tAr&w~wkeo!k8N&T9~a9sPrYq<Z~|8|YzaY_Gkr{aF3{&F3@{hQq~zj^nu-s}s%lKhQ7i(h*`o+s5Lk25%Kk4dOwr2L5ab^N^>eD!P+#$yZm8`iVy#oLl!=#G4I*<be}zg&dm|NI%|#nr@~@rwWEH!}X=Kg#orSEAHez5snQxUT-?SKo~~_9si^ep+p<_#yG|%{sd!|LgTq|707C$9^aaeRFNvD)}2*;`()_%X3jlUmcg{B1e@y;(zFYI?jw-Id0wiQh(lMdCnXv&vlLxzDknkI$LV_v+x`L3g5iiMZO35R}sJHc_t$i&pB#SJ^1!gzH-0tdV+OgIvT<^K0hnRos=iv7b-Uwf9M>^uijq12i<8YzT>8>&k2puf7hq2<+vMuBiBpg3;14aIs?Sd47^&rKPCO5{-~P4Qol!I^v5>j1?oFb_m=#y4l>S1pWyqE8aYVvzcOSVKd*=H5vt?cl7DRZ)#CH+`qK!>Z{;n0yS$s<??y?!=bvT#$K?B|k?eqP4m~aR$Hy0CzUIe?f1@kzvyRy#ux^bpbEJODG&!#UH}QSbd1<lq|K=X#+i#DRIyW-qxVJp854bXtF)wQVajAbh7{0w%71>XoeJ}OzHJ3iDt10)98&9N8ZW-xYhh~!B>sRs5JVPB-bp`fwM?<%BsB`xr>bNG>mwli{DflXMhxB3lr>J9kx{JT`8@cZM+o1o>Qy%c`J`U_Nw)6tbuRW`R<flK9=c_f(@m%V7y}BGXAx7#?@kJf8Z!_`LM=~#J5cW4$)sf=o9g%*H$ddX&3*@+GmdX6ur^xRHxoMI=`n4-EFFla&e3&JE^E+}qewl)OUa9iu;nzAXeK`C;uA{>G;+qSl&rNG#KQy1e3*SCy8;)zc9xvb1^Ap71u|V$EUR^ijhraS_SK;2cD#t5XE8PkY<)bEzEA~^DHgOqH|NT#0Qv(01pSl79JN&;tb){Nk*l$G^^&na6A#xV^DD`8q*6rk@<R#QZ@)Ghi>KO7g@&IZuS!*w{)_!EIeaQpJ{i!|3TDy_^lOw33$r0oa7@Fr<@g8*qbu@VdxhJ(7xhJ_dHJIF+Jc>GoJc=AcO(e&VS5UW;SCBuXrjkD-zsE@BcvCq~^Qa$?m$27Gb2N?bPh%g8=63);Gl0GOfEq#GY{hyj)-pEGn`y;6R?MIdA<rOBrw%4hCr46;k|W8{)Zyf4avU{`97j%IXdY)pXKDv(7`X$vEp<4#E!m$sl<ZG#P902cPHsURLT*8BLw$$bhTNW^`CaNv^1I~OR_vf|qRu35BCn^;Ag?E{rA{w4N7Fe^)7jq*j7ZL1B>TIWp*fuzM@}d2rY4YglXox@INk*IeKunp&#!21-leuL#vO|Fsy)4?Ry4EXbw)jU<*g`ZMHwsHs6~I8OH<2{^=E>t=*nnDZ?P3itypQrR;rVsc@1?b`G6JstT;i<BWpFuS_{a1tQc=a07G*phUP)kDDoikRO$lqRB}9Z5xJ_;w;JoQo9aidO|C(0Las!uOl?B0Otx9kklK>kgxr$cn(9YxO>RW3Pi{o^WoWKNtxB#%_NG=Ldy_pmr~2Pw+^C*pPv*EWG?!s$F3-?hhgy|fl|8D%&|H&RgIv@v&E=@2sg=lzT7g=LT!}rcz|dTgY9m)9S1;E0>I}{LQKBBTDYYTFDLIJRk{m?tN^PxPu6fPPsEx?Y$gfj<)yr$mm&dP1_Mz4y`;e<sy^D?Co9E}vd8$aQK;C1;F)Q{mG#_DTK4nEdHJ5sfoJ-zD-9z3+-a^eFZy{$hG-q0|lll=ggZvSBBXtjX568NZp?McW^Kt4C@^NwwL-S$kDe__R$ztbxlA-yulKn($0X3goKt4guC7&Q4pl%}{An&7YA@3vSQM1W;WRsE2<7cy9rx}?XZ&6Q+#=n#2r!}qE`KA@?iRP^g%_|w27c(@krtT!~<UFlrXkJI%NZ!b~(Y%zphPsQqi}SRGq1j2zA?I*>nx|OtwiQVX%@Y`!yHLB6wZ2B~LawW1&(T_*`Wm@tuc<~YORh$4MQukOMjc3PM}CVMNNq<BBzsWHl0C>?)N<r<9G4gMHL@2ugxZ}PLJp<AO%5ebrcNPGCNE@YUPetKYfT|9BQIs7a6VU4lc_1>Wbzzp5_t}JB6R|JBH2#uLbj6|Q|po&lN%J9*9O#@<eHqn1`N#|sjbKz$s>!+>qv&?Sq#mw)Pdw!vO~R`dj~`FScc{|sDb1+$fc+rWDm}9DTZcuY6#h#{3bP&9Ljlplc9M&bs;(2ib+<?rOqeMXU<%PW`nwntaT|_>teD&exIRv6?HXPYchEidAX8jDy@sC$>c@kc<LN-Jb5a0qI&t9rg;$6u3kRZY3@XAtX@6`Y7U?_P%obqHTR)*B=;eYr;a3#Cr43dk)y~97_)eOT4Tw}$wfVhW&gA~$Xdr1>+M+fJG8%BDIfR$^j~~l{u%lK?Un!VQ}UCq{#;W0liypl{`KQYX#X;Lf3g;3DSQFCrJsJ(KLNHH*vb'

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
