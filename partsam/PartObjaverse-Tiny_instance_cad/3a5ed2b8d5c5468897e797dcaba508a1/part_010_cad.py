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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3a5ed2b8d5c5468897e797dcaba508a1/part_010.stl', 'relative_path': '3a5ed2b8d5c5468897e797dcaba508a1/part_010.stl', 'source_sha256': '29a5b73546dfed71522a01de5feacfea2d28e6e74de80d08e978fe5be16f1077', 'input_faces': 458, 'input_vertices': 269, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.03569871932268143, -0.2257089614868164, -0.2833749055862427], [0.16412650048732758, 0.11953872442245483, 0.1945188343524933]]}
GEOMETRY_BASE85 = 'c$}qM2Xs|MyFH->=@3ec$OV6CKlsxns4tgZ0urPnk`p0dAoSi3pb(@;4IM5m3Pd`A&~gJLlmG(K>*c43fOI4%@a}wjPyUmuZ>_i9%UZMco_+VseDh5?=O!y*p;@y982Bk=Jm~u5-1b1jP$iEMU<{7zKQO9G<bV%)_Z{YE6cAngXq@$Fo91C1{EWfIh_YQH2XyIQwzi|}$K7g`t>`G*txx}f{UdsZ_vzm?Qt1sNq6b8J^#NZ+^o{h^%T=uzT+vajd_~77$N%x?EpG_Uw;L@_QnC2oIHJ%wr`~}io9+(pe%P+NcTae_=WqO4_w~C<G+G|=H-4@ErT@;WH;F&}<`#+TQrbSjDrcYv7hWR1jdfBLdg6@Dq6bdiiu!l^rT_VFi|(A;P5QAWW|Mx*YyIG_(qx&8`(3Pz>)5;m`j%A-#P7Z-{W#;#Lob%%l5tCwka4Xhg|>)3r)q-qTjaeI@eip3{beN?*EyowUg<wy2hpu^^CYiMM->^@>^l<vF{v^y^OLO7kMX4bR`KWWv<&Tw%DAo^&7fDGxk7wnV-HGPwHJx*UY8*8SWmm8*ma{@;C!h+I4OB>#V&y!7ANso=gv$2&Pm&$XZup-YfWx0{dmrvLjThn$h;hlipsp))y^WG$9-0cKf#cAT+YA*>1X{ni^VtQedIHEgXmV{XA-{|7%h1)a$ko3y>m;&H)g%~J*Vq$6My(~nU~|Yx|r9_p`yFrtdV%k!(}8MYuHQCjgswFiEnC-L(>19tlLHZ;fCm*iJwcHW`)|KTO(dc{N{^z?EmDJ+wJ?!*<g$0&0YC(=pXNse7g2Fg5I+)^xsQL-W;Lfh`;Mv(VdrWBL4aZMK|6%fpJ^cmwoGKK1<?vwH=ix{fwO`epmeh=x5Yq=rIqm&ui7kxk&xD=+@<tGB4xtWQpHeTXcu`PyZ_Mn8*4c|J&P(ZatVACwfdJ$%7{?9R8hmWWPJ+^-YuUtFMH<{vVhZ&!c0!8+yg7IG0b_%lUSnxCDK6u=H;|Jc>L!(xE>~kp1o|KUU7Yqq?zE^jl6@e{*F%+!H5iK_5P9k<<%zm2s`sO`xCs9P@2l@PJ*nO5egc%X3-!aTV$V|L799=UQHpJeVanLZ9@R>=(z<8Zuw&^*-pqO=W%DwXaA&R`Gl2KYaz_EEIE8;_vRiOZ@3)HY)VI$SS(CVUXxn$)&QdT#Y;6-sn{x`prSI|J@%?#d(iu2|f8M$(yT;g?sW$FX-{ba4w7O#eQBs4ElhXo3VfU%DCpCiO>_z$h~1yiNyY?H3NF(`LbW!8%xW)Jf9^(|Fx3L*SsEmOyXL%6Z5)Q82hFB6Y1X_{s;Wu<dS$i&C*3TmQ~p;`s;I&PfxpXvcB$Fp`sfhf8sn2e1Y{!9u9q)iSxK-B=X~$3jOgm$&V{v=M=kc&2Eo<_`DSE`7ti|OSP4CalE@h;&(h)4ga5wG2a6dev&vt<DqYl#d^L7$GnDKL_hJZvHm;ji{HFfa*z1BHjq5H?~jpvVzz4vz10la|DIiO$U|H=(TyzWvJc&-zc^&qtwEu<pB~Ic{}&SAzjQ{{(fqxb#BbJ2guX2S_tMI3k{`#><Ir=i#dG9n8|3HbN6_!Sl=X29^B@nU^CgL%-yiE3wdlCyJD?o&);lB~SJ8K|UTZ@{x8k1Tx%6<I^ke)h40>#Y^zTeNg>%|>0{W@wkNa=QFzMfMBnJB1MX`^L{2;n3?FRbkg6D~mwYTKKmE$G+K^r#6=Zzd#mt+2J(IcnIIy%=hI3fP_d7$qoBl9xjgJfMCr^`bRbjZ3ms|}KVtUo^#-73Bc`H#vk{TRdAK(9VQ*4;fWGPB<7jO+_%NFT|AYf2~Rdq2bb#p_F0_bol3&%ew#KahSr*Lp(VGY!wZfX2vw{$7Z)!!GQ{lM9ibDc?eWH68i9@<{rzc1(tDw#U7+?UneQ$7Vub{0jF{e+Sm_lSLReva774`OmMguUf8v|6X0J%eQ@H9gXC8_!sv^9s*k+&!;xS@7RRrvtujrbMX}Plflqi97p`WT|_^AqjBFy1fG=mn_hul>V&MXYvi{W_m^MLPrI73ADqPkWk0x=-iJSW0p`2UBjdU+WJwl(gZh$Z$2WO#9)HUvx)od#?+cAnB_8vg-0(jNLZ0(PNk5LbeDHT{EBnO!^rpn)IF%oIwIb4wv-W!A|3YQxM=Qy^oQn+1E3qE*-s^EM?r#hK?fMw^`a;<!?wGcCUX*VR|NZ8e@2CB+PdqK*U%pM^G+)0Z>t#J{4}IQ2_&<p`Y}c*4PjHU>3d?-0(jDP1wm|L!=lLPnZ}%hNuhd7LQ)W^;&P%;P&<}^>9!pKcb2)4h`uTAu?y*+)u+J|{fj{aQ#!VZ7_`6Jp|7acAKc2Lvc>V^>f&Xz%<mY&4$(v*H66np!;eDfSAnucnTSRvix`6kF(yr7Hn{H`6e$xTF?zmPXS=#&fGj#fm_(a56A`0&z`9jh#uN~0up1`{Q+)i}&j3kUZ%7ypex94JCtxARe-fr3d?t61^9)CWNY(GavBY&B%vG=IxW~57=2iEIyh=;m6`zwjlq;7gHqMsh~Wn8n{THNRJJQ%n0Qk?6;%du~JU4wtag9G;dweAUP=C=3ms{4lf^FE$?<3Gi@&X;?y^z)<)?vsFDB@dpcyrLVww#7NRSr6wZJrMeDg|IHYLnQxN_uQv$7Cva#tzEq(9;c5#L#N-ITwZkd@_oqL?WU=Jr#o-w%;b0WD=F{OrjK9i4*DJCs$txhcd@=V+T)yR{mm-bw`TJ+?EkN8V7@IA@qFA<1N(ntP3Th>%Dv=y6OH?AMicatG#ux*Pb2Z0o!Y>k(hBb_Q;z;**RALga(-Rg8(?1@fv(SmD>ykN#HMGQi+$4%+I7AEEgyfzxuD-%-4F3xZ6)X5rS~Cq=a>z9?fb`A3*CxYhxdnVM{(ZMra-TFTJq*To*VaMo9XCZzYl!%O!DB&I|u$X*YSMZ`U&>=+<EZl$%*q=7x$QR*Amgqf#LZ6tj{}jr`GlTK;0@oG)da~_%n3vZ?gyEo_~$~Ft-ox&)8JxiC5(Q_q5uBeX{Zb`e_w{_k`*}I7iJq(0SgCs_P~HTG#i0d(n!6c3s~Co+_FBT6fWJUATq)!1J#6gVyyup!b8;^*vzu__dy~AJXq&z6%fGJ!H{syhpA11O3<f3G+>V2m3jw@V-p@N1r<%-PGrldd9x;@oQb5Q_r{{^yArw-#6?phjATcM7JVbc&|IX;HOM_ukN_tJ}!v&lNB|gKP`myeS`NvD^GLuU)&Gh%RBYM^ECK#_?@wt&V|<Xd9;p4r`UCU9-Xgm9<=N3LM1ZY&sz6*9%njVT6glCnm+yO^Xu^G-`VZS9(zBo@4i4hW&Xr_UBVHZyV@h6XYYygSn3w?lRXA`7?*(e{0-;v-jy&P{ztWO9*=Z^ztAH1*Tp2-^Piy~SuEq4mDBKE*KWl=`}x)Pxz_dh)%Us9^*J?t{94!h#0cCC{n#M<Uc{JyI6I~wp6mxOufbRFJ>~E*_;2OK_ra^{;qP%A>&54bK3~4NK3`hb&lk(buXTOCj4~%MZX-9|p9jB(=V{q9h?CD#eQ#)8KTq|&p>_S-)c1z3uI~+_%p3GyqXOo;VlJLv(~9hudU_*?$9c~m@BcBy_uJ2}#ryLwI`2=d>+|dM@n`7tTd&{6xLNbzdsDz*$-leR2hi&lkT{(!mg64I=7j#LI_{<MAL9HjY_Q+He=^P&^^E<a--|l7fSzMB`ma3?_jW={%xlMC?C10d<R{MDZ$IyPKWN?e`Kxu`=dZ7>_k%leD*D&&Z+f3o*Y|nGxuBl$UgzW2x;_`~(8cJ7&mH}qrgi;1((h?n*UufNk3U1#?{(9bqW^^ju`Z2EV?Q6-0)2CK{QjX5z8|^Ip5AXiM|!=qp7H)h-81gae*6Bne006fGyKJ~q}bO>zb9zj_j`oaeZNQiMOXf?On>$1m1^dGQN%D*$z=o>-6Cv%@=>Dt(fId&@`<YczxtC;^%}MQzkl-i-W$UNZ<*&U*SsasTaJ3m@2qRC@Rql{<!2Z<z2#3e2i7%Lc-vc!5!K&+eqdd5h4Z~-B5@YSpJ?N=7|-{_-5mdW8{f@%ekcCnExG(q*Ic2FRpApaUSyn_EBuLZ-KMsgb<Ho*Gm9}RZ4>L7Z>DEAV^-P))-~Tm&mWBW0>}Tu#xKy5lkq>HcQ-$q$8k3?mOUK%Hs_^ceZ#z{93(PtDres@&nm||xGri<3_q;n3%0$+_Nwh7wpVQzv%PBjZ?;!$v$OpXZ*`xy+%v$}vaa}k)|LOhfi_CN&(9usOBSzo!;7h`Yp!q?wd3CMo44ffLtS%)etz&P?^17xXM4>RPA6Bm#9LBW*IeOFa)sA9Mv9GJ=U8f7g}J>Y59^vM^yhrkyk2_oB<G^J!aIyh#k|H_Cb6!$!i9`W#T?@;t6A4v;R42`Vm{$5>8xw6@D~HIskmNq{5&@Pn(>?@x;g$y8+S9FNyOP4f0B*QW<0BjNgRK*jVCdlbmA)mIZL;3g*sM+PrZ1VacZvcXU27h+E&&zzf8|;#;mk0tZTlNo+QSsv`egOzJ;DwjQJABe`VvB=<#R#Pw7qKXA3y)7RKV{*mpQD6{{cfpmMO2c{{=NpTr#R;<~6c$-+JNl5MXuud3}5wpVSJvb}11gYC0$->UZNY^i;&_PFBltSg?%dKR9$9P~fnXX?jKeNN0ut}r{f!ffR4drKK_DN9uKe-KNMD}0B%7`fI|y)ZE!xx&0Qo{M#b{^b6w=kS)f-m=|Wh7wPc4<+wO^pN)???Svn-i5q7F^#-C`2gZZ@&V*iIiK>Jhr;)4b8~R63d@nJ{8VSV>TIL<+ia7U+`+oaZ*8`#%{K2d4@KxN!Zvxi7Qt*6%r<42uYzn>kZt_AHdWcKD%&Vtlx=d67i7I0+q^?wm36gVLG%Z)O)mD=fN>~nNUr+J!#EV?Cs+M_#C9LCO)&c_z;*@LrXXXez;+ebrYd6yWV=ANDa!RJ#m`IevmmZRMSfn9pDA9FV>rkwu>N0cQ=Pmb>uMc}(_frz9Gr7Q`Wv#1;>9>lK4K8LYFmiy6~0SenlYCm4`5x*yFT-!uqC;gcW&lOVNUYT7(+wyMy#uKc#Gq|#j%TXepNVb6^>ns`S^h2f55RnV!Ra?^Sk`40%HweTmg)!0Ap>*cv>>1hKw~Q<I2gH^j^u&eCKD3imUVc*uZ&Jc#~Y6@qPyG0EI)y)9BeqJV4%)o}t8P<QwUkN?b`kl%Bc7_2hHOw-Zm1Zzn%Z{FQtv`y4<VM}C?f5Aiwq0D8I;2a|i~xk7wQe#Tp#v5)0!vy$3#>WXLcLtWux<3Btr>#8VzlX#c;Q{^smqwp~KVUDBua@M;u<}Sp3<PX_i^{x0>*1LI2CvWLZG|BJMbC{Swu0H>o9>oW;p1>FmlTTq?eZGz!#pkfTj{FR9FZo{POY^I&tNw<wPsMw&ewBHAM*fKP;q*ik!^s~p2g>t^c~SM{>~9>)aOQ6~+YM%kW=^A-yM8Q+4<Ys@A3{Ej_%-=7^7X`Z<m<`x{yoJ!oT9GyXy#=Oc^vC|$*&R*k*i#dVh$8`CBI6~BjS1TUi5?$+mk<{=OOVNc{n|th^@&V(sP!0kh~K;Cb0wgS$YzPtH@1y1`;F56X=;j97P_^HHaqf#JY+hnSCqVK(1nF!oC%Tk{_gJ6>$c62YMojt;ko=Gm6-kJd&Q##0c`y<Z;9i<Z<MOh|9=FvCpo=j^u~vIZxb1-j$yA#1`b|={ZMCCLhRH=MYDew__X;<ULp)LB5PQo?OKi#W5AOC0|C*HsT8Mj`Xx3HYVRjPcrdG@)q<oAv(#E>DfSZkvE|ylvsy+13fc{W64A5X+>;GK7*dV#3=IijHxxT3Au``F2_{(A-RezmSZZMN$#Yl4zVV=i=MH>VdQn_X-W(sA4^XZ@k{ci^t2;3BX39EgZKq`5AyNE{^U{Yvn?@<d^|lXh?B|N($kn&m%J5YiXgTlugCG4k+)&}3-bQNugFylo!Pg-=H&h9nM@o>9!5`H;wR*j>4_zNOJ0|r4~f;tW9gYm{D%BPdTJ6Ylh34Q7;zAJO?pCzHOPn2^Cht}`3lDRBQcg-#a4@BDy&4VVzW4=!ZGC4=&4NnC;2z@3?lX+uS`!3;=jlT(bJjuIe86w>JdLCuSed7_$hf<s9%<VtpC%$3jF8CQeUPs{o{ad%gn!Swzqul?JMJ#&tak2)%P#&m+vg{057j*X#6*B>?m9'

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
