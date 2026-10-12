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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1d97ec6885464f6a9ce7a4cc955bff41/part_000.stl', 'relative_path': '1d97ec6885464f6a9ce7a4cc955bff41/part_000.stl', 'source_sha256': 'b40e9de4330a036dcfc90d0180486620cf5086045499b387e01c2052ab9597df', 'input_faces': 318, 'input_vertices': 213, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-1.4725902080535889, 1.6972113847732544, -1.172926425933838], [2.0443062782287598, 3.0856263637542725, 1.2558777332305908]]}
GEOMETRY_BASE85 = 'c$}qL2UJzpwmsOeCMueUzQl|A#0Z*1Oze7$jo3A@AeMsy_6BNfi6@eXH9nt;4fJX(#Mld#h};+}0wRjN9DCPTqA^DOd(SobA%FZo#vlJP#vE&&xz=5K?X~yW_nbRu-zsmuQilBb8Fo~_sL|?Dqo`5J7!?sUqJN)==;}j;jqx&yL)U*fc6QrNZQ6%;8KaDG{^1ePeWLv9y8P=$*7gr{`9}_o8W9yXq}R}>@CdCp4;vI6q4el}VZ$QSb(I<)1_io;-V1bn>H0tZ6;>s9cFug3qO6&fY?#{m75uf4vi9Ka&^>l<(bM+a)4Exr3v?r~xR=&l`)WPZx~KY{r&_na_m=pxo;%1>IvKjB?ON!b6~4&t{J9OfalIq*IP*I`LVTIb-?Z*D8uS|1yX)W9*6njh^lA%{$Ng(H<Z%_>1KlqE74q2k>OV%E=MtVkckaAGTy*za$g^lJbkk=d@;DP)NS+=upu6wQkUUuzk;ndW_G7KPMpVp$`lpq<qIK)lMCkVLdikLDOhFza{<lYnpLwzX@}yKfhW^aH0o^@eNkQ~yeAYGOf9Xhk{R+r$C!f8H_!61WjeNn#Z=cCPe)HQP==O-xh_@alA>IkBAo1RxBHlcC2l1YuCl3*yVxtevlQi_fcyb525!qVS#hM`TTdqKN_2`N|m_B8mAl~{#^7NV~^Qto7DD+F4pgY~yV_r_PGB=>VHyyes+8cG6uY9C$4aSLHuNvxf{<w{Ctw3L?=dBpzcYogm`8`)kLAQKgLU&aia8l+~MB>lal5tB^xeDDZDEfs&=&nP3q@L_szoPyt_b@L{vFWJC=zJQw$H|X++)JLxI)0r3-5KLX->lswv7eps+a<nEP4vx3nlF7Dy%D;*S{d%cRoFl7^D8Ajw5HUv@iWxv{(XqVrwzfpJnz1P`I_z?&|STjA>MAi9`$>YT8n=58saVQy6A%|_7ll-<^#lA?I$3=S!MPE)SvMb^_zWf+(rD;$<RH8{p3E%TqF16deNOW{gB_Ov<3B8d%uEitlls8%Y|#WPn}bd5?}f|jO#8GFLjnG2;F_@g6xxTZpwOXd2%23-3njC8;$y+PP;`*=$^EJ$Zuc2iu1%ZG)VM}Fj@D&R#{k=;Uy(c+87!4z+_q9wO8&zA6H!F6|h^*u|lbL(6=?ik;hCqaUAi_*FyKi*Wvw`cpY`Vv2rK!e7f;ZeE#@K5BAOb@jDPd;Q(~w{iXZRmm#s+;ZI8teZ0L5pU;ljiufiMM4wqB75bo&n-Tx;JJIjB*CNj+v9NZ?W9a5rH`8$)aA6hl1WuCpS=HUpAD5hu&uz;05_P_=ktzE=_FLF)->{xLGjUy`#yDIL+?E&pUsC6o?Ej*%nD?%=(Cz0xWkRpFe>&>$?3eg8iP_Mj?tKTlpg6{LIwi@tQ+?x+Cvi36-L1~0A<k!H0`jbyBK3@I6N^3^-{*#2{|w@-3TfCU?v>F$V*SUhlX^TphcM2ClhDoUrDeVm!!fSMJ7_&V_w0d;J8;Np+0TtOO5f+oxaH2xMxD1lOG141cFF(Fm-~^oP}Oayzho)o_gu`*z`1iWb~~;!<$SQ_MxMdvXTRD3{rXDTCq7rdm-}|ZZd|u5B6S9jIgI<n?_~<=+H?@(noUFYVV>c=JQ)AwPg3Xg9vhLTsQ=HnUha!=U7h1GuJyqs(MS9#`=qJg0o-r@8n{Q+D@*bu+Om)BU!i-R-jw)tb@!m24VU&}9+S?Y9?!nLsK;FSLhQu%<b3W|7~?u8yJ8(|>yhk-x3?ZZ+~(j^jCU?b;@?g=g}jxYVEwIf1?61*;W^@*{>#!4zrGf9BkRlw^r2SB5!5-aoaBi!aqT*>1=d_xQ}Vo;j{DcjTN(S*bGNGG>G~$l2Q%&US=h!aB>r@m=zf0Z@VSU^iBGsB`+U<X=;n#565l=z_k}aK;CaL^sv_UN<1S~Qo<0RHVBFjP$dA5#_fqO9wnX&gXR@E?^~e03kk=RSIj>;E+nY|}KC&0|bTIzh6Nq=l#-Tr+HPtS`UJgUN5z-9(F;+K*Zh!LGpAuIE>tZhbOyZ~i{sK0&B>HcJ&5`&PYh{0C`(vK=^*HE;CHv627Ke2;zC9?q_e#k#ysV77u8BO49DXTz>RmuzJWGd(p1&XJv@+@;-n=qLo=5iec_HW0F!aZD_B3=mCIjQTQe!Z#)wdzOht2!-<-U9DLcg4!mdo=(v)ahx_BF9C*8N2J-aZ;4{rB3HE&09WdoTQ^^wY1G^fS*O=!PAR{AT}5<hQ)GLw6<CMjqG5EY#@?KQH<Le~fD^T!H;#cg}lF&Ltl?2m1KP`PLyup5s!zk;i;J7j>F{tP_3dFpO&qJuCZQ{buOS%vSQ;czh)GmHq4~bdQlH&u{L3VqDiUZ+tJ=m8Qu#5V;~#=HY_wx)mgSUc5o#H{6i#v5J<=_r8g7J^9+=d(t&FRN_lpsM9_98FYJDO*yX$6~{idb_d_Y=i(PieEKr<$Gq_ibTjM`_JcDoQtqE3zeBfOcVxXj3X%PDxVAiRo?9aE4Ts1%wx^}&m79s)y({*u(>UlU@{HLb-}}!8U(n~3XG7#u>Hi?;#(>$UwQgS?1l`@dh&TFHY5pbXmGeA9{_FsGzN%j~TkG!o#h^P*2;yDSHeS)XG4LsL^XyC6S5u;nYTXR<`W<=hFO%oMpGV7c$+7~_?YIQwamTg2rgfLQtmxH`%ecS4IuCtOP3Z221(C-yrpR5bI~lblzQihtKUL{0>PfE)-I?4R??Kj+LGt_;RbS#e=JS^QAK_@-Dm(|e75TM1AC`+bg*ty*DB~Wefq3KP67<I?kty?95sP(qUCFqG_$S#Czj!O^G>%#Fymk7l#3x@tJx1afc^?R`_#Abfi<EWQ5_$sjnj0W`u^V#kWj&DRncIQTO|MYYV=b6<8TnT>gznydMAqe0^XpizPJ5x-8w0pMU)(^RVQJ6hd^jxq^lgSZT{DhDH|BgK&w<r~@m^$&KMCCxdK2}y`#5RHfBcl_Z*-IQj`*v`(T4(8rJgs($iDiZ0``f!@EwU?bzbzr;i%J2YVZf@sT3-C=FCPOE3zqc<L&11K2;$<`tOYD0^M_@x_tlU&y?rs-Z7FV@s^zbzh&b2!98Riba(6>>06$O7}uP?47yXdyFA}c{{-VYJ=Q_Dy{1Z?3!9*R=bgKfzeT9Lr?i?c`^SDR`QLhl`_bBwjQqx$*AhRwz0|p6FY2_s^Wr{t&A2Z2Mb!%EzcH(*=zIIh^L*RA@_u{Z{TH&IpJ853a0~R`?9@c`<9AV~UAZB~wH^$T@1elKat>JEVqUi2Xy|73>9U{y{RsQV(=$%S?H`VL8Eu+kUiN_1a()Fz%J)vmEYxoXoP%!l&oA#g3CXC(srNwgRJf1)PRl=VU%QJ`LSJ0<rb+yal{im4v#LqIdQFf%7pR4L?0!w<Ic($rsV9FF>hV17BKpt0<T)^8vGmhOg6<x%S@Q3nauWT#yGzc;>~Oi?J64qY_s=I1AI163-7fPjT2RjYfHv}cJ32<*_o~Ztt-YX@?9UGE<oP*<&%3uS$+?mI8t1C%Uq<w*jik>vmtREw$V#Grep2fBW7k#0cm7!32a1)H_=BnEkiYb5(bMZnU4g@~zMh25l4o>9oG0#nC-DAeRZbSY{3Q8Z!h13HkLPkxIgi?nlXIs3lw+vp$1?J}Mz<g2zVN$+{yX>A%6spvLo(lwccGt-Ym1y0Tl&elJ#`KGX8K;1--)U(kv<LXk8{Q|^M>s2q;fK^Nnc@J#z(g$|D}d<K0n=z`i%~cB);QNIe&V+#yM%GpFx~!L1p>em;!R%ZgilVOFxHo-18+*+;#c=t7~KAaYdJw-%ai|kiMk<BJ;Rd9`CX4{1RtxGURuOcK2nUCwG(2_v<V9y}!Pf(*AG1T5gMJ(4gO&hM`f&C}l*3<@(7|i~29e{`Wsw_OJQB`pGir!`lDfpDZh@8cHbmC=^#Hr|?g5ZA&WnDg-EeNUm*pg|Z6O6e^QfW}bHyDk;1}u5B5P^KLG#Z81atv@7G4ATL4PhrD>M`by@isVsR}`d#F{<i4!aPoaWBX>x7#a^+L-RwziWZGJ9ezFb_}JPLWK8|3=WOQ8Vs<Ri~Ve<6j!^cAAj{`VBBvZnWF{ip>gd_b;kApKQyacwJd9u;zNZQoL;qEJKOecCEqr)uPSo%A~U8?wg!yndTp+kcP;FeZT49}=2Z=a?>z>*93{Li3LliYUCv{=UiUV&vNDeeec*RDf1r7bV_cO*v~>incs!@uRKD_`<n*UzFn&Auq;Wm1myvync&3XC4U(YZZPZ*EU|^XN6xB(#W+<rRGsMM1F`qt^K5MfcyY`THB_OLY_jO);20^CErS4qQdtIOUSidso++auP}{V+Xd8SD@-AuLZ8<Dr4UOVOP|)hQ<y|Pi9W6UTVXQ!Wcsu=M`0@YRQj~GP+<o74EnUTRACYMBKp+vYHU~7L#}NSwOtAa$q&-Ei+xWePo*!F{XR~v?J;V)-&y2Y^c`ZqkB}ds?*RLKnEWt()7YoE<l4ql(|wvrK9jy!_Gvo#bowT-PqWBp(KnfWnnym5zNzffV)DiG?cuzSl53lhs~5+}kI|?5y-Z;Zxwb15Rw-;y*h#MK7Jg3mDU&>tdGvl<udst$+hjxbqTZ9M$+g|gah5Un8rm%!X9L%IC+%+LThAOjXg4#r-v4fLZ5MEyCAqk^%Q?3-)K<_gXRg)s<<z$&S4}&}chH|qzLR_>>(sqYSJ+3c?S6$gL(YqMa&6~wjpK50ZD(>V<EYJ}oyB!dpl>m)_OCPKTuLBMp#Lb>D4jf=b!BoLv&gkQLVsp1uI*vYBRv<_cCR64j+<+sxnBF6b1ISRw3T)}*Zc>r_Yb^YM6T^p@(spcdr)5|5t?se&r^)Q&cS5XlR|r#J=W`<bN0n^t(TMk$T4-Fa_%L4y@GrNd%1^eo3j`9a837<XR!CnnR7X>*O9Mdu4MLZFKu$JJju-6QK79u2)VYQ)LJQYA@4$;)><fZBJV_>);>{aN8XM;tu;_+N#2q^t<_U#PTrh8t<_OzLf(Wvt<^H*8MqE@6KWqTG$L<ApVn$CG$wCMpVsOsG$U_DpVsOt1d|8Tr?rL(t;t){r?sXE9mqS-r?pQNI+J&%Pit)yx{`OLPiyTJx{-IIPivnkbSLjlpVmHC=t16tzR$USq2!_Twd6YFtVc_(R~Pc;<juLhA>>WSn=n@>xk+v^e-H9T<c(NQck;&Mjah#;@@C}CINz@1!Q{d0PiOMh<gMAyZxp^&7*DS4IBGEpW68(Tr?syYz99dCKCMkqh$fGwPitQ)3?&~*pVmex3?LsspVo#eM36_&r?nvpeaQRJr?r6!VdP=-X|10^FY;dWX|1n9Px7AhX|2DZe`gSG(WkXR3cbmD)2Fpz3gP78^l5E`LL_-4eOeo%FqnKWeOmiUA&NYTKCRgbBgse7r?rU+qsd3pH<9Z%j(i+_7U!2UPm6sBBkxV#n|<p;9!?(4K1Yy8l1Fk~29OUXAIx<eN*+b7Z8Q<ZnxkpIAV#w0FKEXSqdA|kw0a-5Z{?MzRNnvTUyJ_wv-Jzz-~Q3)zkc%XulKn>nWTdL^JTw%tNi+1M!h)Z!3GS`Z^Xub0Isk+Gy'

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
