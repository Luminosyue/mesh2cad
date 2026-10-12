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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/68834dab6d6c46bb8fb7ca4d5c218b67/part_007.stl', 'relative_path': '68834dab6d6c46bb8fb7ca4d5c218b67/part_007.stl', 'source_sha256': '19578ec26763a93345e981ab7ff318be73fcb720c136380747227b086a5a19cb', 'input_faces': 242, 'input_vertices': 180, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3045603632926941, -0.35624921321868896, -0.49999961256980896], [0.3437333405017853, 0.4438479542732239, 0.16044075787067413]]}
GEOMETRY_BASE85 = 'c$}q~2~<_p8pjWknO4tKEOW?1npCKXqLPUBfC?d^C?XCSmlPC5R6qfF=26Qb!r7el67xI?A`V9}b51ZPOt|Jey=F*LduM;&pZB;d-&$|I$6DX||L*_p`|a=Uef9wOcv(MZBk_-|bn0UH55`uKB;qB>Mw%BC9vLz@D57WB>=-NQ74pSTy{;SK=j}7zN}4Cd+D!?Hm>h05K(-qg>}1znwhNvW9vL1O7BDM(N|5l~14AQ%bU$KR;Orp%_1g|ky}HYN-svtckpIV@7J3QV-34b4=&CjiE)Xia=4wKvyI$;fKEGS2vS`{4gDCw@7xw%7vXAt`)k}mg-DyF-B5$Y9EB)VIO?vx$CAI4^=OE=Bnog?SDkWdBpHxmdf9wIF##<@uJJcMe_LKhDK>glI;5-g@$XA2M?xA{bts`ISYjuR$uh%9U$X{dOYu;}Zar-#(C8q>#KjP>Hq2`;PTKHOEQ99Lgqci&+LC5Lyo~4JVz8meiPS1Pfn+=obd&@U$xV=}v33@-Yx{Upo+4rtt-|v@Q^ttO+T<0kJQ~bRyZe{;*1-%{_caq+pH85MK>3SXc(wO8^T(5a9`@fQ}`L#SvepKEHF%Fvf@fmu3(>as+y^?l;+E>pZUv=!cpZw~3<V&Tez9qk(GmV2>V|%foFIBgpaWP%h$k%o~Jk8^9hsHszF_5no29mG-RguS^J4^YMyscb!uiCxze)XT+Z`LaQo_%7zrgk+wD36lSl6>jMO#1%Ds|D<*U*>W22&8_s8V{}~#g%;N%3!KfxgT+vblaMv<p2CD=egxrMg1?ESkCR8sl8nL=M~aLW&FJUVx2?t@sIZ3^Za<{Hq2wHZB|YBKX##ZQcVOuH;)(B&}*sak3kLE%XR&#E&Td^pOjd(KXWaa@;v>^(y!{8Eauhx<f^5Ads~|DO^<h4`qF|N^6UI9`qk>5uM)mGZo`p=zAAP9p4N}QhlQ_LO(WmrcY)?dj`Pi?b^mk<<(KR1D8Df-mi?Pks2=m5VN{PfE{^?+*ORFIlU(wR@z(TtsiI8^y?%0>>tE^2exvb}*Lvj|o-zK$6K~~_Uw7sbslNlS<8ucK=(W^_>NomTQ2o;ROYB>XAYbzhAm99A*+IiI=3Qw$vE1;C=R|Fj$bN-2*I(yG^_bdrKFs4YhR5gUEXreU`#$?s-}5-sz033Rsx$jHLuuUP+S`=h*zPL(KQ+Hd>f49vR6E%op}PO@pm|hAKcsz8>(qn&hfCP^`Hc5byER7}j$8fnFZFgk!Qabry_ouxooM*I<OeC_%Z``HZ@lhQ$6MU~=@9z9##_B9zudRwN%9-5Uvpm%_HRe>b9-+%uhV{h>{lJ8@zL(blP~pOMSkP`L3R3_{Tu2zs>{oT*0buo^%Ui4w9lx6CZDEu$M&A5`eIk^H#G1Y?^mjFhy7zG(Y}D%o0W&0r_sJ=bes4s=P#u8riG^u(0I7bVE=x*3-o!<Yjlnn2Pcp(J@|lp>4OmRO@m9=_n64}s~_?HIph@ijrZqzzw!R8e)ZBB@*msqb69nm>M|xevwtQtncE+v_NK&P<SYGyD8KniCHI>YPJZL_LP?6@JU55%b88OZev?+Pe{mZ>=U3Bse@<G>{-^V3y_&v@I!EK3oXGu7aG`TX{(2>yXG(Gb`Eq{Z8UCJDv_7@ub6ii~`BaZ|Wh>W{@*DZa{5)!}4QWg5)s)Am)AAftQmiWI{R!TD?tPub=Wa?1@}<0tGSY8tzN3CpZOPa2%Q?UMX3DRm4rPC=AD_S9w4`(0nCi~?&#xslxxL2spHv^tZ<tKyl2ZN}^(&{%X8+Q)RBCs5IMu18ZRGr}t&UNCPy0iL2EH0mLHmSq*q`qQ={e*ph6R-0RPM<4gY*mB-p!u!D4wpAN6NUv?YsC>eddGv`QDK6fcrJX9Odyz=JCmBQc3Lx$50-lR~grn(Ycbx*^&4Ev+g{<nfBzX%L<QCyRbfVt}B^NoTpm{dhVs+HIzrq^dMjB5<&GShpM=qtZAJ8d?-Cv(%CkYU&)F>9tY(4o$?s7mU6#cW>OycuosU{b^^Dzi{kbpVt60V&f@%8YxmG|cXABhYqR&Uf7LmI#%F&MzCUH3VE@Yi+Hcg+&3S*yspWn*S<^ltdD+vxWXyTQe(Myv{~1SYq<)p0r<^CfvXq{a<B#}WnA7eo`8zk$`Zg)?8vC!af1`}*F&=n>>M`eZWWQ<=_cO?v@8h`x$XDA`QoqW`eCpSj>%x9m5WO}X%%?oYTzAeh`_3k+FN*JT^}brQh36-_me!vscO19Bevj&r53c6<$_r%Qrdu)fJIaO6v%FCD9}T2?fjT>Zo(E&z3id-!(EORS5FY2eIQI9)CeZ7VHB_%TFA;UV&viy`;CpBOQT7*4rgKjVO+Uf@G4{1G&g1i>oY(U;<hew7wAdKh56t;D*x&MK7irKwdfw%N2kbwN<of5-@bg^o6Z_@9U(vXXUP0g2RM74_@)s6<Lpp=+spf*t?0<M{9rZiB2h}4N_F}(DC%W&bk%@F~HWs?FzxfBMM+<tu>#uMa`z1a1(Y%g{r{_>B97n#ox&xn+qxknHt?(oCo6h}ud-L;9wA7*=)5vS&t3}J%-+sQBUQgRe=aQ)?p8d}b@%_uyR-=4HiQMlOKOd)g@(twsRZ%kg>zniW?3vB$Z&y0!DSngcSNux(p1Er``%`KtujF=xo@aH}N%oiCq<&S`!Tf&l4bH#rEPY?u!=Cb+cim-w>Q+8K<__9#;qO?+=W}!=pKry#asIs%=)70_J&&+o%l@+7`IKjH1@)^Iw>rnqHJ=xX|5BPCQ*lS~)hSoGom(^BUyHl4zulY9^N1bv`?Or*$o}*g-j~Nl(>%x}ec2EFk@wlLVYHsql40C$ekJv5_TR((mUy#2YaQ=vevx#K(@G|Co*)CCi|);M{CCgf_EXdOJd0XM;~?*jX1}1{UeZZ-Y5uj{shlUoK=mkdU*+-Kox$yA#PdErarb(9zqEw?nO3~s{I^j3#?sTAXI7>~ou<+&?9c4P`_lMm$|LQ$$9@?0>+!XeN8a-n`*R#<y{UdlDF=Kk{yO7x|L)$4FX}fEJ(^24QgC2{Kg|eJ{M75S|1=Zg_+R~Lrnh77|MyQb)_M&u=+Q(EE9mpk7r@Vh+aLtDhPD8=2EPJ*5&R0c6|_0H6}Tm|8Mr0*Z_uXTzky$t#GkxapMy39H^mePZl}kqdUQev?f`8I?f`BNwE?#WzYcv3{5rTJ^bK%FaA&9t?hLktb^+Uh-$V%R3VjPK)B)TT+#4adAGANXAJ_m@zy|OTs4sX3*b5o}_5yqA;jM?89;2Zi;L%`zs3+JHpB21Kk0d>!q3glX;8}XSt;aih^n~^R_XImb-v>K`he8K~hl0mJ$AHIy!=MwuLIc5J;CTqaDs&on8tPRMf>%J-gYEQqPmgX0!M&gZz`ejuP<OBs*cCb+><adShJ*dU!Fo*AW0W4D(6Qi9a3pjRI1;=B8Vp_nj)R7Sg~o#8z-thKH$s<!g{}f`1Sdc@gN0^*#j_!vm92VA)WfJp5HtiF1fBt%1D*knf-V3@ffqrSgN4R}7lA)R2>t@P7Q7a9eSr|X4!RB84fFaILa+nW3G4vw4|N6i2P;rNumbjl27`UUVvUKlDc0dA#AwX3P=D}P@FZveH~@JBi!~_Ln;k;%dr)Wad*A`kq2K{vcj!2<J9s=a3_Knj4xI-M2ggEHa4dK!bOm@RcolR#Sm<W3SQlaq7!iU)ppoDZ@Eqt8@Eq_0XdHL}csX<pcsV#8x)B@?UJFeCuLW;~W`Knzf!BjKLo>jm@ZG$jMsSQCTlClo%>@5l4-?)u;XT3jdN}IwE<$i0gy4Z_FFyYXbPD(r@JQ$f;E`Y#=s@s5<a9wzqPA3ME;tpO4$T9ngHxb6;1qBoG!2{x-UQta-UMC^-2h$<UIzUfybL@ax)3}cJR2GTo(-M~oerJ~{!ou$(BTNdA3>*sw_x0NAOt7t(Or+em^XW{BXkhh5$po>0lR=lLKiofuf>?p#pve~s0l1;$VOe+n6r8=!0SwKF0>Gw3(kY)gY&>S&@6BcI1Tz0I1RiV`XzWfcms4Lcmw!z=%?V%!3&{t!3)6=(3#)}@O0?M;OXFxpd-K|Ft37rysVnoSpTPg+5Y=S6_;*{f8aL$q~)&@4L`X<&-JfgE_}S2ihH_#ac@E!SiZRRO8*4tz8@w'

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
