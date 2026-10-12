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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ed24b6e27921449f935509d9f3da043f/part_011.stl', 'relative_path': 'ed24b6e27921449f935509d9f3da043f/part_011.stl', 'source_sha256': 'a3c67d7fe03751efc101cb0c1caa0276ed3724b4d82f55b92d072cb879ac666c', 'input_faces': 394, 'input_vertices': 237, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2472923994064331, -0.49999991059303284, -0.0773891881108284], [0.009421834722161293, 0.1639767289161682, 0.1589249074459076]]}
GEOMETRY_BASE85 = 'c$}qL33N?o+dZh#(9h7Ar$dn-)kqLybCgITMbJbja)ZR!$Usz4$4o*Dp&^>MNt(ngkst*3qUM>ZnlDOewKWwV+J5JKo_&*Z&zFC#fBk>D_S*aG^G@e^=UagR<=%3Z_^+{aIkSG(!kUsKP+4-8;=*Glju{ai+d498N*Spt`Qp#cNqvHP2M#JD#Yt0LMux|Zh;iv8yL5@@;Nm8`L`;a87!wv5Iw59cxbS<1jgJl2{MgZ9QQ_LNtB0qTo9x-bO`b0QAOD<08+>!lSOn*KWP1yqUBe`vtto>~k>96vI{EcS^d^5%OZEp_z9qlv_QB#={kaMI1(P$$fAe05U{j&Ye)SgY$NUmS<)k)0Nq(oU*~D?rriu5~4dvMHF)5MQX=9Y|ZQZV(pnAFnZ5M2oPtOy+>J&-7)au>cf=vbHc&ax%g8hfHQ>osNvYo`UZI&DR9v2<jZ=34OzMFe0)f09k(ZL_zHiPPmdijNeKW!)ZQnfXaf|YjF*pI)mO0XPKDTUf&sl>k8c`KFw`)|`MdOu^{W-2%S@+vCN<<@cX&n_4#Sn+<m(xUfmc_S&^u8M1j<zwv6Y?M#@z&y*M^VMbbwo!duwoyE6r_(uo-`lyAzxRM>s(+wA`!@=xztmRl-#GXgK{QTG_u{FYrYCOfXGK%|r3&>Dgl}$Lnf<HFv#7t*{!Fpx{gHA8#mB!U^@CZyc8vTc?-o*fE(A}f=a!q<uYIOK`0|C15~<!h>)CH{BA?PPkD>DA)hXnw6IW6kRHvtN9Q?{E#X)J_V=a|;I*iLnSwZ7akv-Q@d22)2?{#DYwZBZJnRsvw_Lr>LL;dY{Ey=-e)od^2zZVij<2lla{TrY0xbm2hW6}FVzFki7&7Qi6(hvCSDEZdT6RABXyR5h9{i^*YQ@xQz8!2x6H?Tit%67`1{!gYw@8^5$r2Zb5N8?bLyx=IuC3HWvv%SxJ8W*p|a{9mpS(L8cp-m2cWM`_+RNHR@aRop2r~R2k<=iTyaV`Jo!~XBH&D0(#aVw>l+}Z!5Xd``Z!{Bs_-d{SD;vyY#Sx@C{t;oJ>))sosbpM>55B_z8xXRjn)Xurzq&fKU>n#+Qg}!s>yOUnCUsX!y@%uK-Gr9Lm_Iq4gL2+K)CXedbbC>-e{iYBPJh#Q7_tiyHDcyv0o;S5_u>aVd@+%AeO>rysL+{e~v|6s_Q2Ons*#Dph^^3JbL+amRe@N^uYWJj7wC>ve70Z7A?`hsyGcM&?^#1pAHuHSALUB@kd$PZxj+LHcdd;Q&-r-5U`d+W^s2x|7Mf7~!mDAg<FQ@rXv2nhGZw{h%s7~eSJ4_u89wy)4O7XOIil+D!`>l`CI%WItImhFj{p{~M&iz%;nDQ0-i_1_u<wsp<-H?Z-v%jj>3`#fp6^|>s|LAKP|LU0lDqlXC$o`hkDW2+v$24Dy{a)uNo@$j~TF;a!^VolJW*fyJJ}S?m_op`6LEjntisqwjO-J^z?%9&fl)l&>9Z2z4o^_$|V4e5)5XH~^FOKueo{K3y1OFgjiW<6%+I{2<#o1Q%A^V$d(tNRfe2C(#H1}nH_akbjEqVy8Tk?w@>|4fAJLO7;sNb!1y?FgiJ#&@nPwcUV+c#<#)t~tHP5RCUuXrBE4|MQNdG~kleCfK2+x7A$_jAv9!RAZz3#q@46jAxM$|*d*n)M;y96a_0)!Qe9$79)}JLx&CfPCBZ5L(x5O$*7FzU*>^%A0zS+Nq9NMZR@;#&w?G$yBc?p)2{Os4Y~law~(@OX+L_E@!*PkL1@~!{7Vn=?>z`{Sb%KG(P2+`{bK^s$Zt}NUy$Lw}aDh9ORpRD=40~)5tfUaz9V)irGW+RLL2{<wPsgekpOaiN5RCj$H5Ma$J6bqi?O~MeUS+**u=cMXD>O-}HjMR|#&olKS1hDYqwhH?`mNv<#gu%;TKNSI(!=c}?+HNc)v3_Zgpua@KNueEq3k)T8<ApHJX8j7nch{Pm~gOGTroomQV0w13H0+mdhn>CiRGx3U7SZ=Y2mUq0ND+wa_-)(P|5)&lC+XEV6{a}Vrt@aOiSdZkHY_<VQb%L0AB+ltbXz4gAi4VNGN4Xq#Qh*0uP)x3C|eBi?S@Z7%S%fGy)^ro@_wErmUyvaBJ^AC^P=wE4nQ|@%+a)vymaVW=*qV>l1uo3(1(>QJgTj*S59{(y|A5ZI>d9-gzpFZMsvHK%FpPo$nmh#2f$d{$g)E+gm3hgh-!|yr$?rBu7bn(ho2S2$Te{a+LkIApSk$jWqeV(VUX6EXB^|^Fe9|!ru4Dyx!5j-DHc+&o&q|4-6pS<Aq41Uh@RDR9pKQA}(t@Z2iI9bZ)LUV%-oPO8ebY8RlR-Sy-9-n`&Sx5C=d`;`0DK(PE)su0wKPXk7^SXGmA(dl}IZSa=p9hg|K4Ind55G_2!J5&J)0cZj{j1(6!2ZU*oY0o%SNY#)T~voQ=XJX3pB%Tat90&_M^$FOXDFR3<;_+)|0vfb_6L2y<1lek8ujDCJdW$7COm$cCM>1$eJAifuekDhl75iVt35AMf2!F-dEAcaM)Og=6VB&|ycQg{8pCNE+EP1_Z>qC`(kts5&^g)W6-ehE730&IJ@7jR-?0AJef#=s3yauXnlJ6@U#Rzs*X{1V)48s={GWbcKjP1AdS5>H1&vR0L6L)RKIO;jdGhT2`tr?_R?+$(KdHCd!N2W8zO;B}uHLu4oWtYidB;uq@=ar#@whENYb}pMUvB3gcWIocq4Q{*7yCJXP@HYmoM`_vEy?5c;OGNdpUnwjJTBoYQ7Px>{h8;vdSBhX;xuu_TU#8`tFbh%mE-5vIruXN@%<^qo94STES3F>fAhHgguln`OG_Sbzb{DHruU1-gFKY)ckr#XLdiEZ3(L^^wsx;M4k0^p_2t;(U=Ey@s!y*}KgQ#^L7QX;f6-y~EnOVSk+I$?n~EHKTWfb-A6~Vg{mz{CIH$DnZ0&O_r?l}ey)z)EwD}@c+?!q6{4({k@qNXxKB!%fWtKKi<tss%rOkJ#QTxo&=DWJ$CfzfQ>xM091^LGH&F&l5CA)82mu!Urbe=V?d(wvr-*1fTWFg-}jO(rRrWfBYjq7&n*?hmb^s~dhVE2vdxzzeMzGq_JQJ-9*eaHHE2>Hf+P3b>~?)S$1(eD4({!-45eB(Z=mfgnZDZ@Ucl&R0Yalf<shW%7cd&>8C!+xqR>`A`yydmY@SWWFW?BmM(y5t+r32N1=^t+7lTw(HxCEs}dvHQkzOR;Y_x0sq7PNrwW`AYI1M!xY}WR5g_P5Hv&9nNXeOPPG*xl0+BM)y_Yxl!7|=VIeNqGlv4*Y|tz`4GPGJZbyr)G{i^aQ?I%Sxmn1d}}I*Bj0$wm5;oj?=YT|&4<FsH=e7lZ;sJD$$0)(Hh<3dC&Rhj`g48qjpuxILpQ$H8txs|y$2GgylS32u7XxlIf~O$zGoQj7q;5<7f?G5_Zp?vqj~!AV86d8>&z<UGu)e$nK9)5*S+c2bh_Uf?_cVhMPKQC`+ZIET}Hnb8t-??^O{3S^HtZSKBd)bs?s;cyR`2;k`d=!N<5YQ0kgf0<0sJJSMU5d*Y{sm*G8;{cO+*iB24#_w=iiqgG>L(draH^)lc4@9oznYfATJaX1@i9zp{Y%D+ewET@LzPK<IY>p(}&mg02kh1TG6*7G*hs--Y(m@R5c#V1J$NqrpdmyM{*a1-iqljc4&LP=l{7O>dpoUFY}5J0H|#uiGE*M4M`8s0nTWT^U?W!`t9W(1OcD3;q|h;Oh8R!L?9+EtD;|K6FbB^)$Q>t^r*GY2F8fZlR$g*bQ7Cx<1Nv16PM`4R!%nhpvuxx&T5q1B9*%2wfFi9=a-Y1wiO3;7ZU{pz8oaHwA=l4z33M0k{>o8gw<pU+4~CS8z?}n&>ZAK<Fmm8qhTm-zMOe&`qGd!S6$RLwkZ-Kzl-W*7ZkcK<EIl8*~74S3u})y1wZKc7g5&?FDWI?FHQq5LyP;g|3UfkpZEd!4;sLp(_GHzXz@Y{T_5<a2@D6=)cB*&}{*s+k=}!w})1AeXM|6K`YQ*0HJ$HCH>tC5V{lC6}l6&2e=7z6ZD@4AaozFCv+cZA8==AA83DY0JJ}Je{fgm{?NU_-Jp9z2ZFtz1EGDv?Vx?3y8}YIgJo!U=tf{?=tj`B!4;t^qAzO$LN^3AhHeP`A-FB{htMAbLiYr>hwcg87py?{h5iKG1^N@{e&Alv{h<B8ouK`odw@NlJ<xwbZ_<#jVF$1U-ZBlJO5*>sNYZKzGc~LM&w)<T5UgP;(gni{LS9kEat%u~!~#L^KGQHpSKdrK3yg)gN<)f<IA9F&iE=M!xQBX|!dnV|8QQT&!yUA51-vBaJ;<Acd`ZY_FCz(ggLK~^_%8HaJm16f0et5H-TSK=wre<xZ?WKeEO>Vov0a07f^(s_L!Skoh8A1|eHPjR6rudFh}Bo%IOsUM{|XTL8*mY{sCS>P&jn9`o`U$tfx|W2(r`q>4M1osI2qas{WT!;MDXX(6QKtILWiI(QO`JV2y_V2i~}b_$AMRYlXbBdd;**dos71g0N;YPfX{<(L0iD~zP*Zg?SsApJ`a5d`U3bC^abd9fY5irH=yrA9{^jSt%&0RK<Fia(6Qi&&=V0;`y3QH2pj?(1pO%>v<VyzZGsL4e+Dgh3Un~Eea;D937!Hics2BD#BL?h3*H0X2fYt*6#5qpKWq3^!$S=Z@EoaOn1)Os1Ktn~1MqH`&YPuSx`qf~61>qG1|rV@q#cd-5qLLH=Ot=bq+u?w5Z*#OPX}hf`&L61@+?AH;VssXpdklX2XCW>4H~`xRCp?$hXPUX;x)`hSqUgZcr!GN$Gh1&FADib0$;-W63^p-8Su^^w)Qw*hi3y{2kyh$rQxWCAAtSvzQ_Cfz)$dwf`0;jfR~Sa`+*(sMC`<VwFSt6w;3_C$8#$@5xd<Q4g(u>-YE??fy40fkZ&tc2yZXA5I6@<l<}R0AAy@XZ!glF!@KWLW)8{_T%aqn0BHpu)8##e{DLn*3%;hS_ZsRJd{FmY2k~u!*X!c29<kT}{RMcMR5JF29tsYXO2(ehBf%q}1;<Dw<4R~Tj>MRpt?L(|=Yz*Xk4O6XfY9>*p(g-B4+oEc9u7Si911-cIvP9;IvP3~ydHWzVw4RCeH?rZ`Z)A$@FnQm(3io-pf5w81ccrRE`Z(%odwQ;&Ot1)!1JK9pzZ64&~w2Pq>^<>X!}|ubOd;~RI&yNZC~Gn9snLJm8^$C4+BR_CF`otnc!^bY{baERtS9^d|N76D}=rezATlj2}0Y~0ik~YpOi}06QS*Eg3vp_JEf8{t<YP*S<u@wm^GvWLN5S>o(x_KJsElwI1PFfbQmCXDj@U~K<JC$wa^!#4}s0lX0%V}z<@Gkoy+}C|5UW(Po*EI^#5?wnA7p+Hhs?LT3N+Ez6A!97r((sWwrlAXSNWxdg(vc=+vY'

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
