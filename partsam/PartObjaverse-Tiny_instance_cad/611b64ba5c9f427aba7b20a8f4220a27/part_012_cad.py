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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/611b64ba5c9f427aba7b20a8f4220a27/part_012.stl', 'relative_path': '611b64ba5c9f427aba7b20a8f4220a27/part_012.stl', 'source_sha256': 'e8b8a7083bd2c03c83e0a348b5985907e72df7df85bf48a5638d008ebbf64db1', 'input_faces': 520, 'input_vertices': 355, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.05923353135585785, -0.47051993012428284, -0.38550764322280884], [0.4356149733066559, -0.408598393201828, 0.18569661676883698]]}
GEOMETRY_BASE85 = 'c$}r136vGpwTA05bOViy4KjPXfgXTnZorXiGtUh)2uR>EYfNN}5e2Le;{e1FK|tX;BI1N%E6~Cf5m1mxP=+Ws#0kMfUyKo=_-fbr&aqC}Z>_i9YuEPw_}#s0pHo$*CM+IMu~Md^ezKgqR#rQ|JIiq-syms^O;cvgxqi}=*==u}F*oAW@_qTy`rzOZgNjE-oSU3mb0<%kJ!w|%WzpO#rgqD16V07Eeb$^=6K)(oeb(eD;`g5Lo7q!5fA)0~W=!$^oY$$auuZg6ew*n0=>PGjn%9DRV)zT&JdO9O`>|+j*-!hn1^gI(YQ@O1^89G#Yo$To!FOJJ>8b8P|KypE%B!FHSoz`l+7H)H;D_s{@=ldoCyB4?IIs6t{p2e@IrGB4pr0V$Y5AOA-&uOK@4Kaq)Ob%u_HPULaeTd9?Z<S!-Y$L=-#xy`s&D3hQ!T5$o=>;OzpQ*SpP_s`KRVx?(M{z)(9o}wTw2r5*M8!D<+~fcw)6G;g!7pnlRvPXnxEyzd_QsWoZ7$mF?_RMLcZC*_)&cKqZMkrm77}i<GIz<c=2_<^TR3C&ybq-{#tsm>L1_C{|mLA4(99mkN0nC<(v7xE7!``^B>MP^RM$;r>XisHBogQN>};#F?=&WA>YgoepJ`lc;KmEeZ9Y&oF-O%b3A{St@<hW?D^n)y014-`S@o3WA#-2;Nr*q{-@SB;n&OW@!qz8AH$EXr2nu#qTy>nKZ@^EUGS*Cf77q>eHTA9u*9#geUsm-)@nb0Rkq4soUZCuE>ijUF?{FKIevY&YBS$=UaI2z?#W`+KYsE><vXQkto*pHug4YkS2y;@<+M+?`gbc#d@tym{`b%E`*%lv{g^+G)Jc9kO7(+p`rpu6jraCuxB375Tm_Xsc#c|ULVjw@F}2Qoe{O+aA3yrmReOSd9N($a_in#_-zCbQrhK<#fXc^@;ybyu7X|a(CI30@_xnXxD_{HWmfOmLejGpA^+0LRkKsF0j^AbVGq-KI^<((q`r40$>PPWS{Wd*(Ke@P~Kd#u&5>+SUM|Xa!>O9iS_nqpws?Kv~Rh{bR=Lg4|$mpl~4Ed=y#+L<sJrD86&y)szGY=1+y*pT6&qKJr9<Q_2u5aciRNu^luJ0c4{p9vM<)`ho{5a!v*A%Ml;>Yk4v*wot{V0C?sXc1DW0&}Tiu&>NiDl*aiCv$l{JqoW2ans>%_Vz+zBz6uJ)w@nSP!eu*ynvz{wLGsS;wcYgKy?p*TFZ(TPWYmTPWWg4?px#{_bY;tn;*Lks7b|^?6Y+!18}_Jm8!C7|Q>}{?)#o2i7a?>-~}}OsV`IrrjExx76_A{&?LEqhIVE=qJ%+;D(^Dx0?+4y1sL+$oHL3@9=%Se`8C!s{AVVS@~|XiSk!2wYD2Qa;fE;^IH3DR#<gn|313T-|nfWtvc?94L6kMC+_&s%GdQ1p?ovmP=0(h{r6n&`|k3McK_FHw0zUQ_Gj*~`j0kWsOmp-*!T7Ellc01wZC$YS@q-keiC2TH~xTAcKvQib^mbV8LLie;~ndQzFALR#m}z&Qm`NA@<eISH}ko6z2%#E)BeVKFIoG2&qm)*obPJYkL_D(`MSQ|uJ%ozx}POiSoKr&*7|;Yz`8B|d3j5YnxBfRcly8Af0OT<^<iMb^36JcpE~h|??;bBP6YjAi=^-C^Um3{-uK<U?^yMn8S5-x*AM%;j(c*c^6%f{`+7Zea@YEP{P=s8AK$#n^36IkbA{#W?P@<+n7-Suqn|rYt~(m^Q+>G~9+}+LJ>bXmb4MuO<-RwZAJxwhdC%DS`g!e(GAlo!@8|QMwEJ1c^Tp|nc0Tu4$yr~05X^V<{pb8XJA(O1y<fiEf7qG_eSYm9zc=Wc>qX(DW!AX#@pD7<WYBl@{teaF^B=Bnt}mhbjy?{lpW2n7`sDc~xmnGp_8t8AMO$|T^OO2MbMO}*1oNZ#sm@pKu<|*s+|%zL4(99QEjeNA-k=}T>(#F_tv+3SJiooqs$;I#&rY@KnCofA%4NYisSNV7tNHbv(G65TJO{<LsN+QY`nky|o?KR*pLDmE2L03pp0jF{?h4kA>F4E&>#h1O&&$y@+pT<a9_2k}<?Hh(`o#{rzCMpa`T9Hx=bQ5=+>d_05$=ccC{}5$-4EwcYRzUlU!O-?{_#ODU!O;*8UuG&{qsDP%s*r0yF5=t&lFktW*y5J@s^dZ*Z*qgp0RxW+)?AmVXGhf#4Gi!;~}Qk=LQq^2J_AN{`MiOjy~UG6DC{vdi_jJA7b^XuSdzD8SAX$O4r|U=Q3-5>HMrZR-a~l2=!yGJE4BGAMQtA2UDSb%z6^)N3SR0exh%w`!qLk(4HTC|F*G)eco~Z6Z_|NR-Z9_Uo`wVYrFcominl_)xWuaYn|=)AN{gLx$B$u!|R*&!|Ro)6I!pdA6~DtA6~DtA6~DtA6}OdHFC;bZ=HGh<z8pCAHJSyKYZQPe)#%j>T7@fxV=`L&~-}t;p>$4&HYKJPWXD{CR&wyy*7U6x*R*z;-Ft&uLHB+SnlV~X?ZYsez}|XTfRP?wI5xPb1-=PIQ_r%edko3?>npm&fgwZb<$c{^~1h7U+|-8ZGAsASKT){ZPu&$yQ>}!9?$yu*F9U!_sxBB#RqI(&;PPJEZ^L><0sG5vFfKP&+`3PtxT)Fu48<CAD(}!<(uak{OFlRhlA%uJiov{A7k?y+kI~7VEJZU!cRWd#OgD)VyfEi&ZbtMiPX)uub(^0rdz(bpMOL7&iqTP`pJ_W{q4GsMSWl2hbJnxQ2lhuvc}~U*H`Pz&Md1Rw`RpREnh#cwQ6bQ>+xzoIj_0O*X!HzJe6Owg<U5-vs^zlFYV2sZ|aBg&3aCL>@nq=_f%)UN&5Y~-O@fzS~XR5M&(%BbryV=4Enl$H0<kjZ&YP}yYYFszVGPk!sGu|+wE9jALmbgZu@$?g=a0_j4SNx<A-rM=l*om->yEdU%s%||MTIyjs~|I&FH9(laO!TBjKC#bX9LF-&}WiPZ*ne_ff0=wwIR$ee=Bh#0e|k9JlT4d^2A1-S6%C$<<fx3Hs*#;e4$n-2=Y4?uYWtdPRP6(IS<v-@obirBnZG&*!Io{P}bj-E%Z}zL@&>W_{N6o80UB`hAXmuNC&4cX#;XO}(Ieef&gExAW^qufETk2d87la(zAj+BfrGXIE*^H}lqZj6W`uujeOJKfJ$w;n%h6n|Th^H_!WRuC?lz_iW?VS#`|(|F*gRo-qFYeb)YRJ7xQQCZ^nfG<d%2<NO!Cdq^GUiylyQ^nLQJo%aNN^WJ{z0(BnYoB6MqW#yZ7Ous+W_4RSfdll`Q`TvpkpE_U9Td2Ny4;HF#&X-VqGyl5&`%CTP_H?eQkFVE(_)UY#%JbcYFP8>=bDTf>s$V}jY2<Oge(1YQ^x$aU|Hb#6Mq_<H{9P&8FmC0W?^zp;obdh7cehxxW4<5$KB#^D+?vqW&5)n!!a9Z@{ywPv@b|%F(Q(yJ=sT(Q!{14@AO23N{qXnD<l?_r<2B!Hr=3*!q3_Y!4}Xu2o;zvvZ@xz_PTBqQU0(b8yS$z^?d$LIdfv1j{w|+r`d4eb`a8S!t?%!}*53lD_Ht24s)4r&FRD73&eREkzXBqr{AexzuYg?N`G56SKngpy|Ns6KkW0KC>Uoii)`WB69JB^3+7ixzUqM^IqA$au#Sz7?z(XTSe+7$<gNMSy(DCpvcsLq|MX!ZLN5aG5R~@B)aTJTb28%ueKf{<`C4@JkIdBeR*oaE68_{9#Ft#l`$crNR?`Us$DEuozcqAcw4I$iz5bl8%!B?PHp+)dja10#;@Au*zFV>(tVbS&Q8h9LfEqpCC#-W4Yac~?R3J+y$arD=49DV|Q0Tw+1AEDPL&^7QHwkQ0!7f*XJ9-ROeqb2ABxC9<S2u~!0H=s|$8{iKJ;lqURKJ;;TAH0hYex48>i;joK!dD0S79Q@!5HEV717OiB;hu0Wv^(6L8okhBxEI_HErCmzi+<=pxF6gX9R-VyfydBmU$iIOlkEvF^WtGgmP8f8&ArG+SE3KYE8#Z?;Vp#lCUhCR34V<beufaf1kHjkf$I^%wF%+6XmhwOd~u*}VOjUz^kOyo7A*QKyc)g~y&M)Tghe~Rm%^>lrf^fX*&5A<Tf>i_E8&&Q-6QBWcpE)Ef?f(|c#-Bsx)&AE3TPT!0gj-R;RvjMge!Sb4XuJ!hO59;(KI-XKB^MJjlJmPMLXuH5bi*<V{Y1!+mvX`JT<1y#b`QwF|7BmaP7eO_3<FAj}zgVgm4YC0$c;W2#vrO!PQX*t`27s@>7eDpE_tIxDH%DFu(QD25^122_f7bZ3DN5I}^ek3E?hYbVUo$HgEyl5N!ZAppS-V6}TbX2(1cNW#2SH+rf?CwrD4~6Fs#>3*Z8_AsqE0+lz+?;pJYeK=aUSI1kqImK~VqZ1zJob@hIU2KJY5GeUSR`VhPpE+vFtCxkbn%i+y%S)gy>q!(MgScR6sW#p_Pgj=C`a2{i8g*Jg(!QIgIuxMvk^fI^`{3yB(7TpeSr`Jc(Rq!gdCp_4T$zBX2gr^e1^U-;*=t6it{6{bDMDIWs!hb^lfG&g=QtJ<d@U4XKBy=)73GR;$hOa<-po8Haa36FSd<{Ap9R?3$%%ch6>j>cm=zMqqd^`F_SkJ}ngz#O2@NqBx3q6G13E#;a9U_GH2Ig@u`Zl~5{u=!UEc#Da^jr9A_#5<Ju;_R2cl7rSdI&zm_JkkwVyPE<(1Y+E_#Ap3{t>-^o`)~M{~?6`O$Z-D55mXb`_QHEeem6c@M1!E5&9s!2wp-6KR^iYK=;5q;P26M@b~Z!fpH4=^DZh^cyTq_0lpgUg%-ly&;qm&uHeNbUNlDw-~w`*6T(?&2e<><&O)2QS#Tw^A}lJsS3-Y;C4?)Z7vKx*GhtEbwK6?7hnurK;f`JudC>*!4R?X_3E@kL-poxmxEIlzx$I3X;eKd;v<U7GUxjvr<#|D#4NjxGV9}HCX}D!XY3qpM*3@W;c7$8Pxo8)-3uDVg8^gKqSx4z9N3rM!u;^j<Fg=|`Tk^Y~d-0_gEh0*DB8uCgozNV(6Wo>%&Lf0V)R0;!Lih+Fyq^$$2mKs=2i{2te?$nkiYS$yS`orm2KpB6>_vMoV(8_tXkR!6cSrlceW=kLZ3lOUd!U`*PRvCQ^fI^y+!O5zi?)H=&}&aL2FKW*@IBsm6JFd)2tSFw3qJ`TK)-+wz-LgoX+6WAg(DHA)!+!6fnEe>z%|hta80-tAzYUbu1yG6C4{S>7r|BFbhH{=jsDUJ;h!88!XKkDwvP$n-RQgUyUf>aLijmC_<r;r_<mTg^TK-l7ha6s>->DZ5Z2cb;Xf0?FQQMvFTx+92jBzjn-2-$zY@Y}>_6F0X@qcfGy~3H-&7}r>kz{A&{}XkxIQ7AiPnWP;Ra}JSoC7J0USk}z@nGKqV3@*oQ-ydJ9BPiqs`!KxFOmIZbaV=(M&j#o*JT2_!DmqKlS38hzj9Ro|Z(Ee#W20|BMhWBZT#RzVPelC(h5$1;YAyLHGnAJc1r%+an0!F@*30LU<xN3Z4j$jr`oVusl;Fz4$x29Txo?{C9X@MCpKtV$ngc=wNstJOmvLk7k=g&=PnE{FS3r=I$%zunZR63U8&Suh4<~?ldoc<HZz0_y%+)d;>fK{T)05o{ioF&xYrqbKyDg&8Q3C4Bv)61>Xig=EZyH`{+~f`|wdh_$5O47Sx4rfq#$Ah3C@i?+M{qgz$9qckp!hMsy}TlexQ*5dJM8d_6i1z8)S!2+MoH;sKEgnHB%1|3&uaA2%ZZ4*n0b;or1Bs|0^D&3jlkA6beARF?NiP6h8D8AO)6adZ9~pnZ+S'

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
