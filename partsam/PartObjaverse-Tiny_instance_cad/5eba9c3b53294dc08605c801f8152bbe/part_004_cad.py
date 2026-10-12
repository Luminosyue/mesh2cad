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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5eba9c3b53294dc08605c801f8152bbe/part_004.stl', 'relative_path': '5eba9c3b53294dc08605c801f8152bbe/part_004.stl', 'source_sha256': '3b529905c36b7e047673ce0cfadfc10c3926311091697e07a45a8310cf2d3113', 'input_faces': 234, 'input_vertices': 174, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3038893938064575, -0.059316486120224, -0.19928230345249176], [0.3567603528499603, 0.4594966173171997, 0.2170930802822113]]}
GEOMETRY_BASE85 = 'c$}q~2UHbj8iofHBVxhc^;%Iw48^X|Yc#}$A-2SZ7ZgNMkfOo1jwlxFf<2lm8WFKZ#2C;!wy4-^V$Drl6W0>69+Mc&nw|gsUKBa(IeT{RIp2Ao`_4E2eDk-N3qd`L6|bbpr=B*ku~+grPfb%%TC1c@2#bv$H9Rb?dDOUxE}AEN^~u+i-u(lE2D)eyw8>s0!s3R<dbP87bqH_c<!$i_kB*Ix4T%~S9XldS`2itg;=)WnE+S-HnEAblZ|fG`7XPN+mZ_Hi@l(nyL4Oc?(P64_=U?YLDK+}7S8Ct$@PhL7YLDP+1FEFs_>If(tv&v{guFH@H{y8k3i!sRx|h{={i26mscqhJ@gKE9zO7l>7NypiDd&~1y(sn#zMm`m1=>5b0KVb&1=_J^?cWXc7z1D5TLZo|{R2OouMLN9ZP`Nn4DoGG21<TXZ}_%M@vT*Y#1D*=_P2>|X%iszbeRp`xkG&Yd`D@&`#Si>F8WospF^FY{?g8#+nbB>EgtJPqd#(z;ahhHioee-(@}))oRo|HF?LLcultUa`mMLNIEwH!*JaY58xy3Reu<KQJRA9ief!+8$k+D7NjoRn$#rjLY(<?bqt6w*Uwh6Rv{Tr(ln+2VPTvUe>t{><Tp5Y{!oF=~9m${9S^8)9F^s$ANFc6jk1Hkh+`Az2=e~14&O2P@Eb>$PA>Vdv<N+LicJd7JM?~C&zhn0iT>tHfr!kKA7hFfb_#VnZe&}fNCy$o;GjjLh_^Ilr<+>iy57U|+gr8C#zOgn*>W_;2(ouwOsovvD^k-yoY3Jw9q@7OhBfqe3zt;%)&Yzy1!tvE#O8bKwBfqe3DdC2Ey~aKG))rT!eQ#If7xwK7ZsNZ5$2Y_;^RujrZr|^96yfLhgSO<D_ygl5f6QH}zmV@dbr|&+H5y2rT^3!%^|Y>7r`9E!<UgwZE!y8cH5d6gi%%l|Y3n@Xr#``Tjqlvy>;2z6j{LT1+2{wi(|Pch)VYHEYkLkMKW`Fz<Ei^a<c}{6-yV7Q1lk{$bqaOXnuGbH|KTbA49|1Ody;G5JlD+Q@T+B_9^3O`sMG1!NBlJ*s7LGI%)#}1O2XIQNW^umN3#y2{oHNGaKBgAp-!9sXsKuASoqqY2dKwL=wdhu`h&%{pYcOI`lD~YhTq`2j7zEPTt@+4r*CAXqE2h}S;@cuyX5bliTr$Dr>|AAN&c}s@tqY>r_pYx<kQ!_7hk{A9{CpkBk--kZ^73R{E(mT8}yy^%OhXw>X7`0ou!?>N+CbrH|Sfp{6p4b<u&5(?TK;Gs&q!b*?b=yL7hHX=x3wZ3iPwJ?+@bF{|WiF`E`(Qb^i{&_FGn-tl#ktw724n<Tu=Z4ENLW&H;SiH2k29i-!4Ol-M^P#|Ly5|LZ?+KX&K26x6rH2fkkC`3dAVK8W^>m?n}Rdh%=3GiHOdzp*;onT>tQw*6)X#y$8p#$Owm3*Y`#u?+OX@ul$fTg9>O*h;%#{@d(Hl7IZ|)3~pknTKBUPl#`fiA6tHYEP1O`VN)-<cG+ka^48ZU%LkL%;=b&1wST4{NK7D&$4h8>bI_IFTT%u^qc0>4d>afdx}5lnXJS1vMwxsryTINu9xx4t&Q=uU0*H!jkVa9^%QU1xAW?AnRj<Tx`uYgb&~e#M#_9o9fEz^zBLH@jP+~~d?WNR-b3^fcceY<7GI!!?;Emi=l8~Q*{E9rzFy0UJbQ45L$CR@#n(KWNxxP6b{G8F7v(-fQg-8e^S$C<90=cbBntbRp6#*|*S(N}dh9jh(SO#;bMgGwYVO8+j<(Aw`$w$`=`vnP_->6@BI`fj&lBHPeH!{(&s?z<^|qdcebwlhf%&C9y|fJZm$J}r#*f$JIe05U{DqJApdR1!eU5_uV)2dC#C^!`8@d>Nc!jUfZs2lRC;5Ja_{N4L>8HF^@i_0uM65e!y*^UUl>HN-nZ3|I+Tef6zM1cD6<^Qqhd<*NL*HqH^=#zIcxm&Nq{4r;{Bvlh#g5nf7vkH~B4u6AXt)afczGtCFU}t??r;?0>*>imkY7G+HFSs_?;ke*<3}9@eVh1}<h>Y2t$pvcsIPW3_8(_Cmy>AkVYf{<?q447sg}x#c&@zkTZ(UwjKMykN3F#BvR17F`b`hd!n)I9zmjzyqe=bc;*hU3zbEfsi91n;{a!uvn|{65HXLu%8S}v&^(*!X?Z7?pOLm)tI_mr#^Zcd%^nLiwbLVA!U8u4XzOJ{z`fIyM_TQKO-{9-_Q!u{9Q@i+glW||xhCWz7g?;0^ytnIf*6)IU?XWyAPVhZ>vJ2LYX1_BH?d+<5;x*q8Umxx%{q{p5=Bu{x3f8}U(LGr=k9LZm8-R7<{L3Btj4``sHhgD?85oz#)iHlw`oD;;wf$ArOY}l{U&{&JuJY`c%V0ge^!JKyne$xc`LDOd?~p0;QQIZs@}Rq{r@dF@cT?60nJ4{wqb_Yt9@dfV>P=Z6!4u>;+3!8fJKK|Qu@1EE+r{s=1NB*!%et`MpN{#i&kvLLv01n9eADJ<i@$V=Jl{Lt*(dY%fL!N!syt`2i^==&pr@EG`m=SoA7}6jjFa*63-N!?!G3G&k%9fLu&-^IiF|8XC#kndeau_?zUFC;B7DoFJNW%*ZILYdN6C$6k$-7C`p3F+^)YF$`~~>$KE{0+O%BQaSIi5(rA>w*_mLp`#~z#f4jjULW9@DDhR;K3Cm|Q>#yIp`-Y+AL%KN~RLDK%my<~hQ_~X9xPdDKAS7G1!i!BrRc|+hE^EctXH1DdPI*RZu+h?x9@nOT^Ys*{7xKFOVS<ch&oYv0<K<$C$P>*#%WqjAVMTx#UPM&LdyX1RT^D}6_iI4P)79jgbXI=8<4UqTcJ(==c?D|mlllse+I*Ri1$}L6RMwa-VVR()>16yJo3;Xsm4=|3FMr|+1yq{si`F{q=@9U<Q<vs6_8}=pVZ{~UrdhM?v9{tzWN$@b=9L;doDrw;%1^yJGO!djvqW=^!s>Ofxrw~8?|NBoNDP|2*%$Q`xaB4Vp3OSrSlA$<`p?E1Zg{*Wfc`12~8R=$xZpJ3+8uA+EY@)6vr&BjlSCiAJ>llhxQCE{!krz;xkQb0AP$!Y|?|%YAai|#+%@||GZ0cmP(phAs3(2#|(G10jX3R5Vt{ID{iR47)EMkt*`P7Bvg}lam<|s{~&LSs~6R4BP3FIj17;+Rjj2cSrLmfg5C5N(4hA<TOrG}IHk_S;ok_V9oQ{%`h%vf*6N`~SzGq#zLVa8@^8aa(Qo0+3@3w1qt3;8qZ3i4;<Weml!48=33E6Fp+`SV=ya)x3%HH~a1XHqlB8LU<DVol~#G*x|1rG83IC2yc^CD&%3)uFycj?vT}scGZQh%{rE86jqTK<&p+{4sSH`D5}xhT;JX#l6gU+l-cG_%jr@qjn>=Bln^9BKKlDeHe<v7>c8)k=m;{sW^c;UVAl%6(>=3?bV!DJddIHZ`2s_JnCGA;zVi;Ihs0(8bglZ^+pxw-%->Max`@)HH4f$28ySdG0u#5GlI<+ZHA5Ks^bw<8`;L32x>ezp6x{NT&2^g<H*To%rRpsbvk)EbEZ<Kk*AWA8H#68<H<A0pHN4WKOv8$29w8<M=%tBXoim&ZOv%KP~4sRA-Ov_kQz)5B==`1{)lQLe?$&qDDKTr+><(#+>_jc`T^P13^y~1F%;LJ)*{y+H>diNo0Hp6Ta(+61E}wj1IX_)6sz^*Pi;YckKBUnM{P~^BU`AxWDB__wHCQ1xdhdX?8f^q!BAY>3>T_KbtSv9kJLxK0;&J4RA4A}r&c7plgpdYfZB*!k=%&v#ZX*@T8dnS>_M$W_8?a^qY1S!wGz28xgoUzxgoheL$N2-o$N_2Ni9z<NiJ95-pVl)*E8cyYI}y_cc=}>?~prD8<9JaJ5#;LU8qf|UgW0aYSb#^YUI*X4{~X8b!t^|b#k);ecFtnxGO{Py9~uvYGbmM+>zRl+>zXYTA$p3?9EVIm!Y^a)stMAT$WmrT$cO>Lva~1f_l2RRx0+N{)PGKqpOMk+CMZ4pZWUhe!(-#niJvW%YRT$H?^M31>=eb%R#m3w0{Gowt5H'

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
