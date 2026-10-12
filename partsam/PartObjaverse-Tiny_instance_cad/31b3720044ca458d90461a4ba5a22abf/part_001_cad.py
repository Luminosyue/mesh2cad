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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/31b3720044ca458d90461a4ba5a22abf/part_001.stl', 'relative_path': '31b3720044ca458d90461a4ba5a22abf/part_001.stl', 'source_sha256': '7d54357120cfdae0bd759492eb5431ae2bbabde9a066fdcbca99b5b7424bc550', 'input_faces': 492, 'input_vertices': 279, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.12388049811124802, 0.0828191488981247, -0.14033497869968414], [0.19590798020362854, 0.3817424178123474, 0.1348549872636795]]}
GEOMETRY_BASE85 = 'c$}r136vB?n#Z%7yEz){hLOXez(LeuoE<<B#ibXy<XS)&JXk1>X1L@Qa1bmJ<WdF%bwtntxfw)hZiFg^vq8Z=I8=~AM?6?mRt`mQHowSUBvDbh@9o=d-uM2$@84fWMMg$OMpi#Mw=YpL+wp$tIF}oAIJ2^b<49C+vYoNHqs9#Cmpl5dVI!VOb1ExeezeZ()V*WpN7J0K&V>5?b4T|ZRsX(F{bmF1t=}M2f57ljV@CBE)_eG<{<-3}?lW|BuIrB;*k?qpo8R8BNz(?QMt3v_O$_}Xe=^)IBo=Rq#YBIqSJYf|UTk?Rzz;WWxvaV2M=HIl{G1jeSH%MS#AlaQh&mt5P=09T$iJ)ltR`z>0e(Dh`zo_OXMUI6D!(^lMJ&J%pP0SOtWT^NR}fUM{gnE}Uls)QNBg=z;jKkG#g8^WUnqGf@}_Fv_QRpyEKjOGaKsyjlj&<?0e;TJX={{*pWY#U{M^{>DxcjtFBag3Kb^kbtdCy08dv`H9_wNOetgl%wPt<jjpqx4>a}mz+vjWh`h0!gI$ztj&)4a7TXE3&YG0pkr1qKjg64zm>+7q1dp_8{t`EIg#q+1s-KF~T!n94X06%;(f1_C+&s|U$RIhzqADP*8yV;I&<cvCB+Yc?Sn`hSRcI<lX>-unu9oy76SDjF7USHeyukW7i%8!4)WLwgFuzXz~Iem1ix-Ppa9yRY5+t>F?PQ69Sj~<$??(6XI-*1Qo_|e$NyrlY0R|*2_@%{SD=t|YkrZtZ%zx=9qV*!5R@pJE}{+Bzdu79HI1a)8JG%2|y7T|}cwceampRu4QupZy9k1SQ|rE_}v4wbjLM_nh|kH0#8n^~XeI<YvYUi-S<Db-Z@;l90&sq4P&F*QE6AI?~$#wT9(9_5Gjo!w~G+rD4_@Eyy{euihxQRkcD_bk|K*6V)S^}bJi&c+3c)$f-yQlIM#%T(9Z_H%Z2*<#j5hNKk-)kp74FAl6<z3f;}z4mo|Bxk~0(+^F$RgI7BhY#oGCDq?l=6GN|zOHw=4VkSz|Fx-y)$zxlRO`O&$Lnm~Vb(`3%q<A2*S=pLpFKkT{>Vsgo-cjYd)`@oxK(MjK09Xy_f+k?^riaT==R0CVnP1-7Q4*)#KmwyP`&T#`WbT`QP<_+>-nnxy=trHsP+>d94$)n%eHB!@_#;lFzI|P-#=e`XZ-S_pnC25^)=H6sq6GhJJp}~(q-|O;YWYGt2oKe>=04M^?2Xw|Kz>ud?Tm2DL?elw_f`L_b5MS`NNY{-lxeCb9_>K#>e;f-CGb?uYFyg7_0oq^vZ|S=Rb4VtH%#F>QH3*@jkzsru@dk51H+!__VM6#I3g!1=ah$zP^2W&R6~VTc`Jv=7a59_0c+O3xn!?pZdth`7f*EKAxw>Ehl4=w~w^^c(>S2vp!UiQ4mzGeO(`~Kjn3GT-~qtsrr8`QP<t~&-Ol=<Y(1isPZXU`;}g)5i|YJwRWmLa;myFpTl{J)cO4K=lx0Z)AIfKi68l~+R>nT?d$r;U$-egK5p0vb$yP!Feet^$LlnhrP}|Z%Ny!*x4z|l?kBsw@yAarNIz=&k@FLk@AT^OLDG0yzCZr>q09z_LG{|#^`T!^TdexiWa$Cb-mDAibG08{GP&6Fom0n^AL(B<KWYBhzMgORiCLYCgX(=>&$n+|FID}1y8S`3KE=1{qg&rD3aa;g>cgk2srR06lU;|*@v(h9KH87ey;vAjuYG?$uU@z=Xg=7!o)6Ki;c6e0lU2CaoaerO(%EOuXYEJ77`@M&pSGV^cdSQ{ujj4y6J-|fGv}N3L-ls<H?O<)o&60CnB$z{GtSzNFPoPiRPXy%eWGT=r0Zh)dYt`!_8$CUP`&o;`oy67ivrunPpMy;Q5@8N-?#c7%HA1R@B3DLbj_ut`^#_thv$;k0e_sQE=XFJY~Q}V(Q?H}>!I&&IG41pMmKEnu8Xw~w0*r#OPoCNuF`|;HhJ^t2lbwn;`g{)X{ey>22W3U?LT!z?bB>Ol;2e4(al{q2HmH&?_V!``#!aOU7z#HR@E<iok{Wab06PcXHtB<?$y5Fy?@y2r0rYvDeI)|>ve2UOLZOWeWvZ}eP-kr@4DIRy!P#NKJ?N9TUBm7cWmE(j^NwR9ozTEe}3Do-nb<{2eqH_9K3skS8qMXZC|f@w(mc$@$Kik?c43x&;4lIBIWCSh<|_K+xw7ciECav);`Dgt$j}7mBH$JC41jx`+7XJZ|}Qo-+!)kT%dgWJ<Im>dz0^5?^(95>vJyc^}a8&_N6JlzQ6G8eQAoX>-${s-g~Wmb&7A*+xzMiU+*jaFx%TtS^IqL+xz^;`gz{--+J#z@pb#!x86HaeEnW9ve3KF4j%H}n|R-e&noi#4&Hl^em`=CmW-R%QLpE=uh;YNqzvWT?`7Jz-^=37yLs(c?}@gr?<3pS_mTGP_ea~e+p*s(6D!{I`f0uAYTtg(jr3gM^~ZYePVx2i!nfbMQ+&OiH|y?wpKgE8VEOvIY~Oz$!B6@A!Sd~P?C&Ka)8;Ba^v6y~^TGD@d~mJ~-=mJN<*iHp{IPt${_s5IC#HVr?LXNMr1<Oy;<NIVA1yy$?R)ip!1nci!0Gan@^e0U*85&@d}w_v$Uo3m?LVBpwbk*7>OJ=-_22US{^L7;xw$x~Ui<#{RJ)IR`|q@Q$ISku`1B{|xhyp=Lx+ZV`{cXkd*7>Deqz$G^=5r|)10E9dhM(F&Pjjey4q&d`8mIG9EoyHwlkoQ@h2`Z<wtAqpST7!{$Krxt8vqY|KC4x-RJh9t{W}T+YAnoi~h#od&xy}48D*2KH3nz-;JhjJc$0A!F9+*>lu72xoCZZ?<c>XHiYkT<6qopjNSwP-i^E6_ygJmuI0wB-6)NgHMlmpXgPy#Ar~!Ua4qs$v{43?<4O|38E82;11^u2fy=|CjJ8UlCE+|bHn{OFx*lFno{{E7*)-1+E=Mj}1};OMN1M`yc)G21=sO0>aqpm&3@$@1TG3!>t0KA%uIfgX8<}WDgR{xAX+v{0a?#2LS0%4X8^TrGxXF!DXla8hkc*ZyxIDRN34^PUSD_8zOgRrXs-wR$xB|IoHG?aWi{5N-CV3`p2+NQAF-|&K0<K720d?RK<Q0ibyb^FaS_!Vev6awtxT_nx+~|OQV({O|MNb<1Fu7<)gS(P<rHziL9M=y0$l#OYq8}UFkzBOB!5zpu&_;Vyj%$maH~3?6(QgfIPcHh9!R^S~(T1?xM{<9aL-SxcM&`?Tv;<s%IaeO70+(i<mO?Y(M(#1cbK?Q@4uczzi{5T<Lvqn(1~(#aL>t1ge#p9W6PgXnnj`B<RW!@slH?_+6_#g!toJq0%5V+F>NY~S1=<>J0q1aR4#!u9TcWMub*QWZE%7U|E(m8be!}|xEXDYj!avV(ZQ%zPzlR9nn&|CtO}GZy%s9tpwAGBZ+M*A^@?4VVSQ|pP6<QB&1y@1q!&Ts#=z~Uo9^^9~q+Q*AVLb;$OQUUI3E|4jH{nXGp~CM_+X}wZjo)%jeoLQ(Wi6}5+>rSr^Clau3Rk5j8@<`NG0(D%Yn{zlW>ZrGt!|8Sb<VpwpIsBJ3X5hL<C8^Sv-rF!Xk}RL7rB=jqK#nreM`>!PWWFr_vXfRY0elm=l8A9mc})0$r$RnD?HDQm)w|$J`KyhLiQZDptazEZVYha5#lktD{g$@#s%~YEWdl6V+O!e(AVK9@B(xPya3)!o4aXuH~ty=FqVEi29HNyhR4INpat+N@FDaHe1*OX_jKb?H~vHn#uJ`OJ{X>ku7an-E6_dg3OI(Ig+)JyKPUf@xQHj8{b&00C_D~b1CN8(qKDzNa3O6L(rzKXaM+DWZuBCA$DpslW8nE{K0F^TLeIgX-@(1zc+!nNgzz)y+we2+YP1+$4IgylKhf{eVt4@O@Ce$=-~pV6=oEMo{2ICdehrrM_=0oTjpoDo)a>Rn<g>=2W8ksy%jkUgWw-z>f(zg)=y&ir`tcol1@6r_>iPL7-k<QNqR+rn;Z^8rcon<{JqYiC&l=-?mJt3C{T}X3AD%?V!B4_(qif-};bM-Lb_&sAxR@H@EpEK$#!_@SycC{`z6j5SpF@Yk&%vY7TzE7*672_%gr7y9fd7I%LCnI7qO*uM@HU}u5ZmxJ!TZop;eGHi^egxnd;<LjJ^>#<6Yv3e3;LchmT|^RbS1nTei5AkzX%UUhrq+(T(k$A3-?32!~NhV&_Tu+4r0tirx{~7jWH8lXpG@P#!Pf4ybb;o{S5vT{tCSce+7SoUW31Z6X-wS1pFQvH^%Zq#!U2Y@Je_FIsu*m4?+I}9s>73yTCo*?&!b6-Qhv#<M1GO8u}DG4PJ=;6<!GML_dIc!k?i(z@Nca(SO2M;cIAm+KutMMlNv~PvSD;cbTyhmitcbuO-fn`)!GH;~rb$+_<lnp!;CaW3cE6So8oax&<DI>UBU^uNA_2JrQ1tZh<$u@s=Cg(PakDAs2nY;K}5o!weopF52JV5#*wM4UUkD4uyx3&n9N#%_M)5ScJETd?T?HPk1l6=qZDbl8b(6@Nsg{uMOT$E_&MF&E%UIv(u=IQw&{U@C)Rk(+wU*E;`uY{^X*6G`KIhXg7n0l8X*BcqX~%^9C;>e;$4v-3q@B??6w%qGt^Ll3esBgTE#h{n_Bt<f5M&yq$czb7L<#nDgt2b~d;hxo9VY2a=0E2A|>cFQC^A{+V1<zVx|{{!AYvF5=0&l{vi_oeYc4fkoefMK{AE&<G){=ee+++roN23-2X_j}pSi3E}<dX84F3mmF_@d>Fonrlom&5tj23{e^RMU>OI||AMc>7tr_N3-BTIRrnAr?<<|#r=@3?_@DmE%8j3h`V!9k4=nbP$$thgk38$P<^NHjbNf>A{jQVl{*wjrU3n{Y{u|5_gc<'

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
