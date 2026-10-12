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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/a45db53fa2fc4e94955e59aed66aa0c3/part_002.stl', 'relative_path': 'a45db53fa2fc4e94955e59aed66aa0c3/part_002.stl', 'source_sha256': 'aaa585469430f7eddc22917b87dc31ba6f07fd59f998d0392d884b5b90f2dc4d', 'input_faces': 320, 'input_vertices': 223, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.28348803520202637, -0.4999998211860657, -0.08202420175075531], [0.15437357127666473, 0.3698757588863373, 0.199249267578125]]}
GEOMETRY_BASE85 = 'c$}r03shBA8pk(2(-@^RB_HEKO+=AYib63?jcNI0N=>xJg9?IA1Rs^52edKp{lL_ME(pFAK~u!XJ%VXIO49^I(>smj8l`EfHMwSV<(&PU|GD?>J*PFZX6{<w`v30#es`aJzWq3xt8s(tH)zSMR|p$>Z**+(V~p_#WG&g8#I#u{6B5%Srl-CYz=Fu<FI(3P8#y#CK7h?(^Fk*krcX!<?W2UoBt07%u7oDdNSl?GFn!#Nw26t_ACNFLJ<;^jlM_-C&G%h<_l^u#BE!O!4CQ}(HRXNS(fNYg6#f2+TCPUl=iZO?^No#j$=9#`yxhsx?%vJ!_g#Z~k<Yr;W;*%$ulPpSszQICC4G8@^i2OWNB``v_=SHja`F|)S5FVI@_Pm)JNdd)2isRm%8Q+RP4cz8^Ovdp(_%ku-%}v=$D1$p(>O4Re7%cUH?J?%&G<)%)lRK6UhrK%i{s^K)Wpii{b~>Pd_j5V)?Ot)M)dXEWb*Y{8Cg!gF>+&}zt1|~w&p{<LlfN&zE+pL)jwbD6>jCXZvL*@!B^kR*eT@O;~2j#$L-*|Ub?Z%Dc_L&3sbE+1dG>I;49K~_0*CY$`2Ip%l18Y#QQR)^|bQS#JbtOBGt`^Y(T!z2lLR_V6|V|_y+a2pXe(;zJHzCpR#+g+s|kJ!S~dJ?TU5EzbyJ%ZTwf{-}$V_za166e%sks&(+^A^b@`!`K<BMYt&ARcwembQ1aP7znSdsds@N2@9gW>Runt=F3C4euD9lSRQ)Ax2jA7?flvn*d|mSOkong9S1NY99eh>tHQSH4U*X@53SW_Y<?9@4T`WJbUKmICu4Cs*h4HfYtLtq`-3~sJeD69cI{KlLuVkGqi*@i-$yeZe?o}Li^4WdS*Fu_E>u!a3Un+c6x-Z+;WIw%aja6^4&I~@2>ghSlEI(QrclgFb;`rLWNAg`6L#pZfb>ckq`hOLD9lq<TI1knPf#j>wdRN0@FOk-X>x;p6eJ-vey)fWQ`aDfs?;3oyT3YYluewOzi?*(-On=zA-@@*+Uep-T*Y%&Q^-{HMj+3u8NGbC7S@;Mm|7K>E+rc-w*Y0r2_sD+ZB<uVT9ks^o;2V=B?{UiaNWOQT4=GvacJMua8&v9_?^+gV&CfpKb#?eIseP@czcsIJiTA6*SET#0eO12Sg~itVIV9HE>mL?<PnPAY^~L(zz9#v`57WrkG2fIQ7o4a3fKBv#(ff(MniNVtThn2M+s{{Qzhk2kA;0#dwf`qXZx!-w|J<Pi{`toCgEa2i6M3cn`8s^#m*^w@`QH6)?UKDh`}X;5T30vES7+ZjOL-3-2=`_CMs9}Xk2tf+?dQATYbDM12<^C<SkK2*1GoF<E4F{DvfMvkyKv2VUgZB&Cgj664zE5c<lE<y><9aVeEYt74Krx{-n{gw(|FmwJYKdhkC!)J8ZU3YG+wqZkC*Ms<7NBuczN5G#>?COUv60Q8SUtkH=Uq7>HK5+@;OKL?Q@Rp%jXu`m(M4@>kcR1h!L-=Bn4RKqSU~V!gX!m_3ak_d~Ib%>wFRwy3Rjeg|BYuQYu_mIzM>xrE`Kezv7a$9~un{{qr^W+AjtBg#Jk90ogYW%@yh+|9vF;u6wl~3-yuC1HL*}S^M5Gv7ZdSBK6aLzOxXq4)*ii=poiYNuOiwZ_kQ#X7D|mr8-Bfr{^hKD~_WE-;*znqw@XBR(>C;4tOpbcf@&RKd<%ArFkViuVr7U7U%81J+JRpR*}E7Adh_GChaFi-X`+(;N$!0^X`AHr1jOIs*>L4y+VJV=n1K`U%BSKeT?$ErP4Z7%GS`i&bT?i@&i(iklri!g!^hho<Z$=eSpT#m|Ay?{K63OjiAU=)Xu50ZRG2N+?0Q-oa$&?xk2k%TNg#`dUCVB;O{-7BJ!wT$z8}d`YE*E8AF;|`|2Zg6;$VWfv2h8eS@f<o{*e_<i8q7*Vmq}K1rVkEh66)-1idQ|I9lp$-gqb+^WmKV!Hn1gyZzNYZ&>;Gwm)=KaTgM{%Viyx9T`__GbEi<tVyeWmnk8lwVU`P5o?8noI2j{$TCj7e`q8b?|cQ+`D)T?SE=!CG}sOGMeUt8Z?8}pLR9Ny6)*$Xn$76CeVEMeAB;%{HKl=(DirLZKLsMR*%NVb)-4fTmNbk`Rs1o7SfEc6I7q=`{+K^rpeSF*Y4Fc&aQ78(>yhd-e;))-`%t3!=3L6sNI#7)E}0jSm%6JoKOAPw~YFu=7dsxlv%g_^c=r_>v7Z{#xhU&`)pVzdakI$KRe;?d(K^^_KmH#%lv)q;hoez8*`cFsb@j~{ca&&m$k36>LK-04{k)~9r?brHk)Za%JtE%-zHzKr)TN7-LVe!_e7-9{vnT-UOaYhti$*!C%V$UD9;o9=y2+nJm2&m6Udk6rz>pX!B~g+?CFzDzC8bpC%>b8QC=@>aVV`nd3`A*Pm?dNM<ai*^?a7ruPY+N`o6T@T`Tjfc`xq|GY62$`-!K~Jj<8%A9Z(?wQouLmC~cA${J^Jf72FLk}vFsal)^(<qf7B(VLqenbCx`WJw8rKhbiNzif5>i8ke_|LP~&$lg8w-=Aoyc4kyS4}rPv2Umd0%-9Xx1Kkha1Kx+=Tn;@1E(afm9s?f+S3*AlSAtI<IG==m3O)%wi{Shj^c0xu=U}eq!Dpf8py$Eoz!wmltD#?ltHGC{m%x|7R}q}AL2JO*z}KNyz}LZFAvo7UzW~>QFG5d)FM`iNkAu&Es}P)zK#zitfcHW_2JZ#$gzf_G1aCud-fG5nXbE%|nCk&>3HTt?4dz+_=2`|m2rgy5`Bw_v0p5XYmqJUx2ci7^Ml;?wV;zF?8U*JR2+qq8oR=avFGp}*iQv2z!FfG`^9KmdA0apwAUGEyIJ*#>^PwBT`QS|m&L2Y8fj<Q2Lf3$E!K<Jvz^lMH&}HBp@O#ju;P=3bq07OG!P(H2;B4>`=vwd+@M`FK@M`b|=m+2p;5_I@;5={<v;bTL-V7}SZw7CHy1-k&#n60kK5EUmw;7>k^n`W;_XJ0p5s$prpgqB_fk#0j!K1*Vq0fLvgU6Whh8fSBp+N_LHSl=oVDNbGMCfqvL~t@R4x9|03>^lZ44woX1fB$*0DTcW0h|C;!3p4T2+lEP@W<c7jQ=wxV~xR0;dAe|2+r-G4}sf(+dvzF+kk_i^}xa4R!|0R1#S%u0JjD|4s8H_9NZS#7~B@z9@-SlYt;p{9FP0apzWA%967%MZ3BJ-JO&yJ9s?c?ZN+?ZhVv+BYv!9{oL_@J&U|x{b3C*yI3D~uv_1HBFdsucrX86z=I@&Eju{J~Z-W<tGof#SGr<d>bHEG08PHka4DfvDZ18-r4xJ0u!CBC^z**o$(0Sl_c%O#goC=)_P6bbg&IV5hPle6`PX$kb&H+yWPlLV*o(7%)eH%OjJQMm3cqTaAj6Y%w?ER4Q2IxZO+dnz4hGsI~e#?0YbOH12&z!TN8O*nzb6yOc&wTqo=l7sG^F1#(=RmWV@A<-c6?75vJ&!o&Vk~&wV-cLAq0_<9;2zMa;2z*G=oD}mI21Y!9189RodNC!eiAwp{3N(9G#$+Kci?a{x|;Dcf^#ouD7d>B5oSDv;2Z_*1C9dsgZ2ma1HS-$8T<lxAoLaRK=2Ug2=EZ_aOg<zaBv*-Rd5`5DD?N>q2NK#m%xL-FG8OKzX(>L&w^EO3^W`ZjyiH42Yns-H1q9Ioa3Rrz)`5zSOn)kKwkj!|1ra#K`jxSA4PBuGUGSkCJ4?A5uEEGINLAI0SM0Z5u6(_>si6M8G`d82+l2_kAYi&yC66}0c{C>0^AAuD7X_i1R4Ym0e4{59?$!vK%0RTa7XAP;Ev$V&=%kp=wD|9=OifapMA#QoC56xP5~!EL%@mP@z4(7_UNB|#^9U)?Z|x3E8dR@&?Io&;DCB9>;Kw+vGToiK7hi1xRSpq{@L&U&CO<8-X8(t1~=s6ZcdbXw0R`(J7@m_AByNH'

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
