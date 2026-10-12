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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1d97ec6885464f6a9ce7a4cc955bff41/part_001.stl', 'relative_path': '1d97ec6885464f6a9ce7a4cc955bff41/part_001.stl', 'source_sha256': '5f67d9a817841aad2954e078417eff70bd9e3d1ab7b54a33db55eaa9751a310e', 'input_faces': 400, 'input_vertices': 247, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-1.4725902080535889, 1.914178729057312, -0.352276086807251], [-0.49835440516471863, 4.155126094818115, 1.2421441078186035]]}
GEOMETRY_BASE85 = 'c$}qL2UHf<x*hDshFudiza_DEjXjPUD;6ZNw_gP-f&zBbQ8Z#VB39H9EZ7@r>?4X|L$HgAqhjwRCgvtLch3Gc@8!Pr-db<H=UQi-J$oO%`Ode`oH_F^y}dGLDWu82(%L`%aj|4<QB6}Vw^m3S;};Y%bf8~wwSbZ1Jv2}7>R(15(XmSh?;al77;R#CU%%jiLFF5|$~PWVzkC%}`9Xm}Awm5E`UM90`YFCufB#@VhYudof25ytU7=Q;dR1JtD^_t$a{V9wedeTK9bEA1F{jrr9no~vm(KB~snZ)HdV{x&0m7e;f2nvqe>d=2tfz<KT?zHxD&DFV|55QqOm-Q6%X+SO`;YzLwMRY}Z!hzChxo;ke^I>M)c-GBA8q_h^=82{!dG2^IOdzG$j9Xw58m*cj5x;2#_#cW-|qdOcz3hA*%j|Tosxz)D<i?{1*aj7J*~CG=`#<!`Es7bxpWtC^tV&NTd%_q$GG)PD#k~Kg4c@H%7J_;C*DK+-H+cRPJxPY-%qu!fj91ecXbKDc>VI950K}i2;oD@W>UO0=L_&!)GzPAFSwo!_dQnWGU^%e7`!=Ujl>DP^bm3Wv}JtbGKgawxpiOh?z+j~?G}fTkM^L`UBt;Ryq2X+7K~3#LLJPUyTQ8;|A_H=v6Z*s*Msfg^-M3pySnGbd|h3-N&MK(;H}c%qCW2KorSMi2zeTJx*;EZMs4s$NMYpZe!CC6wx^`btMh|=$TM{BLDW6;{#(RpJ^{R0{P)wyqtk8SCzbZZePahjVEk{1;LS#5r2h3nZXmw<1bCz0QmJQ!VJYAbSrX@us>oBzJ51_-Z@2KhcYwEB7JCf7;#}}naCYRc|FfX@SU4QK9##bTxLy{tP{$?{WqhNmsI&e1Gt^o0@sWI@FJNA-JO|FekA3Zhf7=Xk%qOd2k;m8?;I(1}Fy8KICL`|ta>BoBEp^ED>vq(?N^#+fgkipBObg7{dQb?wyZE2rU6qDi2VXmvjK5P)=9|AlI(R*Y@M*E&U1tWO4)&w>Z!q6kV{)U;$)n@3erDVR@4iwO`RJzx$K&t23UAq2Q3rF)ukzd-x+=U!Gl>&Y>>$=j<R#%-Zxnu5_C(Ze>M`*4c=Ml_=g|V#Ppomfz?)TzaUa+y`@r^{5+_ffte?dNQjkyhX7EP2+{n|NcJ(a&{>}y&->Z(ych~o*gDbP}_AOtGx1UBWLmkZZ;9X~XiC^2t>_OaY6Qw?{av^_X`MRALpL4X-XKa%2Q|ewo-F^#@{Lcr#7pqiB_@$eDB!0hWd5+reK>e+K?S)T&i1F_14dJ6}W^;*?S_9+V-cuz1W+f&6RSBqrUcET#VB{|@<1_Egt9Y$I*(=D~yNJ~1T1U)FTh{s{{{Ce_$-m<Ssaw?Q*~sHz4jJF9zxdwlYfJn}dkwyN6{*{dw&!sD!%gt6skd`szNw$0;b+flGTt{p;_oeseZanv2;SZN3F_u@9ZN=iDnx*{lRjcS=z|}>z<fW3gSS2_E$@rutypjN4&m(%Lr^!nTpa4`J~<h@w)vF27t$W$ePrJlB;yOumwi5Gl<Wh4_{sR$pUZx=yt&kERU7d7^@*|%6!zZ>zY665Z{ACj{b%|UdG6vqyu$eP#by6#Iv9TGYu|%6FXu!YBU2oncf*wq-iV(m@vjAM!r#yQ5xnb#Tk5uWV*>KaH3htNY@+x+^!{bkvC=4s-*-Ri?|$VIi8}Q26W({e#L;uE1An#;cz2n1sJ~vJ(IxPI{Q%x>Hxch^JzvS!c<x%allz_@j(Qr8(s3TJs|)Y0&`R>Jm>=swPj4Z-*LYcPp9*9DbOqLyI7$6wzpCPe`)Z>KNZrnl7hg_?i!a+AyaYedQ+%&{RD9363cPXri99d!d~c%urxt^^R#%q$7CUzl^PfEzygBWIyf+)%$3CxL2$%Q|=F0Pa_TpY#|1}M~-Sisj?7o);b#}E1l<{T!@qF3!t6oFg*b(5h(aWUH#+MV2U(>eW-S37;J|90NU|yBeUm#AO8;GOtE`c~!vJKu{(S(osaqmT_|ETleHP>_TYyDHy%~kH4jE@;E&!gv*Q^-5!ICwK=y4-iNhUeGL9}V6Z-b2=5wQATW?Zj2!T@6De&aOD@^ZL1o5@&8EIVZdfzlA#I87KKaDJb#B?!f+Ir3A|O!U=NTXz?e`1ID7k;H|{vvQ8F-ZpL+ijxw*O%}{6StZ^0dd01WMRd|Wy+2*@FsN2%7h3_TrNBx-J1ze9TCHX9zCHYk7eH8P|dG<NxwRKcB8Gr2x>K12#cORB>o%Y+8I8WL`4uaP+EfhX6NzQ>gcY-%7Z;<D%OCRhH+NW*ct*8b(zr{X6oE1wY{>|009yZs<`^C&ZS;kN3Dd(#JAvX9kzH;As_2j+px{7sc{nP`z(QT2;_luc7<9ci-@LKuhSSQA!`m0dqqKzf~v&-^6nsz|eNqRo;c2^IH@9@ZPKvs$Wv+U3M(L}5tE9{SF=zo^{jmY||aKB}5z#CKi<aw#KArW=)e+AxMYOKsR><->9M&aEOr)O`uZ}HYxZ~8CWz}sn)WW6mebOPg|1BH*MB=I+{!9HmQ4G?}$r1(2HG!ECZ`$+uAZ{>ZrYYv_x_oq%WzS<8GXUjBsPkFVIJiVvMI^4A4IIb7e6+S=D18Ey@KCupeE^$0|Aig<1=$h<fAD`mBzLTXs{Q~5?G$b9omOV!H;W?q3!H1=Rcb_OJ@0XM3u+EL@!kgEk<ecDX;CySnybNAX+%E6OF+1dZdslevOb4k$)`sU1XW1o*U#`2%YlDV5YpYXad{Mqf4tT*YcX%>*<IxcDW#C}(J?J8Md+#WTlQ#@L>f@4Re5~x}dg&zW4|dH9GCs5HGgka!?DN|BGvHmtpUA$^uN=N>%*3OTkGW9l+&65$;@v$rOFh2~m-F+cm3Y2fzb}yZomR+w7gvtKdY(N+@)`FW;|*s&#JEbsg|D|##wU0$!gc9>5@%Z(Sr5Z3SywGOOP-x0WPInfyD|QGTdC)nw!+u!g*v;&w~_p3caeIQxQcVWIk~m?7}`hTS9hV#+R#=qzWpHaE42~otbgB9^86xD;!N)*=dteJNj`byIWm?;$BR$Rr9MfrZndxy@;<G0;tAqkIxO#t(-(0*ahb=!>x<h+{I~b9{;eKI!JDsrB+o^gB>%ogz`O4El=166;JZv~dsxQr8YtsCddmBy_8}QR)nEAED<gk*gM;9$;1F34dB)23!uy|P{6%?Q^c_u*zg1_y<lk$Gyw{4HyNGq3-IO?m?#grFeva=}ty84LX*^HfF9Bun9(TR#AoKNdN&Jm%#ormt!P~9d$$HLxN1ls#UB(ZeBYFCj!#Ur&-Wa@l=s2l=&R>wH9#;*#@vJ7_7gw-vYejQNo*wC_zx`Wbyl1U*9>TY7C(o~QF2Xvm`RXz98J#ZgyYh{&Zq3_i;N1u0d~Ub~!WVZ+DtIeuf%x*sCldT&;f*FEW&Fw-sIxmH0lZT<si$*p#B+BbTH@!PBKyy=1D9q0S`FSDFYDP=eFc2C8bnF_VuPhVVJX<3?U-4TPg~Y4TZ6TjZ@^56b63{C{c$_atL{M~!0R{UJJ<a45T0x6Qdfz;v8=4;_w$mFcX%i8uIbUTpU-N9eNt~gejeA)gl_xPeeD%qQqR-Eo5y~``OQvkE90-!kaJp-x^k}Ys4D#ap^|@c{BadWzfxB6^pbtmeE#$_{QdCLBjg((-#c#q7(7Sjg;~PK$a~YAb{*d}Mwu}1uCA}-oZx)d$UK9<o4MqDr{De*jq8;Kz}qJqNc}IAz`kMm<OOd;$a~Z69V5@X{_r96Ub3EzKp#AJ)|T_&-B;&`zxyxXJm%`MU&c2LmN;{-&QkL-9`^@tcxI70INz<fe$@rM)<xd$t`+Ncf`3s@_=aU<e=g*Yb*nckCGpqFccS*}&<?DJ`HAV!OUB82(|ZZVyJ~C!Z=2kgzA1SaJ|=Gf?~W}h^BR_2-cvJ7;m^r@)$a+&!+R=tqwaTdejeZ@@vHd?pS_06>%wR}7uK(C;ZrLJZ(coteWOlS$+O`$satS9tV4ZIEAZM}IX}3Imt6*a<md;ouG`7)HZLm6y8V5i@E`9=oCQ5)|2#VYyt%uv_}(;K&hwXhf!Ax)lKEa}iT92cmj}FSRz7)-Qp&-1<Ew=Gm`B0;GT&OW;g^1K2Y9=0DT(8A5Wg2`pZS1y1<sWBqwzWRZEZ_iiF0L)JYTJ<;k~9eZUbKLBj<Vj;a@QrSE-haH$O<6f#w1Dt3SJkyn0@iI(&H>zUbCi@a`w&<-4hPCt082{^0EjX~Li1ITm&C@BptROqTfV6L7AxCZ^iR|HujC>E4-HzDG(Yf!D^&mGNuaM`3>}F&Vr)u#eQof1aHG<GM+l!DVH9(QaEYF6YC$xW6Is&9r+_$GrdTSN<xa3suz%s-KoMEvHsU8`S@AKk+M4{mbb8`=9uS*7;xk#9yaIjsNdY{2!ehJ~-{2(>}8Qh5d7<Jt0>8YjSB$OC?UFrns|CJ579=n&M_TZ65JFYO3~MJFPac>f4k1!fEA*%TZI@=T0j_T!xzBN;vH+;;*PFuDsK}A^wJ%;+i|H191mxit}^YFydj<6gSst^NHtEQ`~u{og+R+O>wr<ZV}(2rnr|*drJJ2n&RF&?G5o8YVYa8TjICWGQ4?B{F>Tp`tX2Q_0PyDA8ruepq5G>5{MJ1ou)?%i5F5++#sioA|6F;5Pkce_<L&Y>D#x&-%_hh-|7(8p;nH*RVA)UtqgsuM_iBESM;qJaWiV)(6=tcU8r@SZ$ZRC)P~WwmBcHl&8KgP#EI0-(YKq#H>o|PKQD+?|B#&W=N0iQY8jqABYsBh8U49Oton3v%AYI5SE${fKNhh?ErI?-5l2y5NPor=kE1q<{tO@<K<#__<4x>M?OXcOg17~>I`l^;)~QvcKP`z{QmaRQIum!M){Or668lo?LVqR@PoNe=e^wE%qPCL$oFG0yEs@?`CB91SA^mwotor-pls}J&A5+WlES)%=S~~r?My&eV<di=bi7!&SLVpesAEIW_pVh>xsYTHrgV>-pj{XD?2T&V8fBF&kqvlP2dJy-Z)`I@{5c^Qm=}%AMp43{>pZ>)Csdc75BZ)^+^QAx2h^JATK!4T{uc5Yz{v07bLhS^-OD0aHc9p(eC%#VYK7G4Ge23a2`gWK2F0~9VZxi39cALIkAXa?}Ipy0a;#1Tv(ziI`IBJLJn@Ma^TTS0)63?V&(6><HP-+46Etoi%T0i<WoOn339`tP}@la|$^v$2xpIT4)7D60Ctv`L6L_CSwNct8|98PT-eOpVsmf9NnwvTupwIlTH4DlIi$@DFWIEmVI`gV!<616+@?K1IYY8hUp5T{T}p>KzYRezkE@@+5iUTUZ4+h*d;)Z*w{G;uUFlfFd|M^Kwd-)0lfrWQ)yW)RPy7EIs5h{LE2r*Bh<r&1eA-=-5!r{+)JekA^pS_plcLp+DtB>J|TcsaFj`W8zZOKmNE+ey5W+CKWWpLjpDGxY5!@lk3?^evt^p4uh)c9QrcwG1zh6CbCha$3f@EN8FsU*fb#)@lj+jM^!FG4W#7c?NL=aRhx?%D<mVJeBoa#_J3`o%dFA*ul9UWxt<u*iJ2;{ZY<g8?}?{<B8QAw-RsVxGluTiB+%G?PgwQVAb#C{nfoT5^tnmJ9w`R#2ct>=Y7@_ucx++_gzQ4j#>=yR^qM9BbwJ4cnkB2<$abBFQac8d7q`kOQ~((eU=a}p|+m)jU<kwwwQPw@jB)a!Rrhh!@LeSO??MWBv$<xatEC@mUt{R#qDxhAaNiy#VvB0o7hcFaZ{YuiMSIr#SL*<6XGV+x;m|u)4n8DeI;@YoK}pu7&XP!a9R=KBGeRD#c2hJ3sO^Db*B|3E=)~v^_^CfxF|Knedn~2#3iXI?gyt;B(6wJaf6-Kn7A=D#Z7ivN8*mu6t}=>eTn;0Q`{z}jUXODZ4-SOLp+9>`ZgJ;$v5agUJoKx{VX<x)pw6NOQ>_<efH}5Cb8<DvMH>-6YA2BO6=>>v##uwm)SJ+LxHA!My&em%u%hKpNUn!o19uZdx-Z?Q=D2mD~MN6Q=Hpr<B7*pQ=D2my@`8MYr;G$6RW-v=b+Y3eqz<T$f>oHmpCsq#i_NEn>aT$#i_NEgE$8@#i_NEi#QiG#i_NEhd2*4#i_O9N$g2Yacb?9A}&Qutq-*pMiZ;P7df>Sej@&f+6dNtH}P(2yIJo(#H#N`PSv|Rad&EaSnqbk?WnC_y=xKIqL!a^%0jIA?BrCPG7)E@mYa3bh&5_CSSJr+4{Etsr_98espVmvvJz*dHk$KpO|1Hwf2&0|;%?Mby(>7a0I}-xIjy17+G^@2GQp}Z&c9Q2YD3(HanySBa#~qp)mPJGEvhxCesc5n^2k&u^Z)c;Z2$A0fyw{<KivM;zx?-~?f(9kkDOTl@gttMSJrG&;7s^X?yoY@{sqHp3<d'

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
