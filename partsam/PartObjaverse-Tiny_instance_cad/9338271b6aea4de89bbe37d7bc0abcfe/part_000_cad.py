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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/9338271b6aea4de89bbe37d7bc0abcfe/part_000.stl', 'relative_path': '9338271b6aea4de89bbe37d7bc0abcfe/part_000.stl', 'source_sha256': '8d25614a43048f9197b453cddb238e87ab152532e7b55be50b66b304ff8c3179', 'input_faces': 392, 'input_vertices': 261, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11720073223114014, 0.20276466012001038, -0.40631964802742004], [0.11719869077205658, 0.3464761972427368, -0.26260802149772644]]}
GEOMETRY_BASE85 = 'c$}r03!F{W9>@21=2c?6ik$IoX2@&EqdEz<2{9_Jl#a}}xI#!MnI!3@q^lQo%5w;bq#=%?3}N2G5R*5PJn}4Z&szJt&N=&k&i#Du=icM<|NOr5n|0Ry@BdzF?X~yl)vaWyXv_Y@Sa<iHGvabh%TiI%inhk3j2=65P|BEQBSuY#vMOs|eT>d}@R1(9`bAmetmhghr;Hgix^a6~<Bo&xY#i@uJb2{jv7-l$cw*$}<P_z19XNbUir*hIWZ<Y2|IbZYwrLUXYIS?OYm)1K{FGNY?6)>-R61u%);&t=4$0pb!S`OP?C^c@XKjDns))X|a7$jO@1EK*Tlwy?2l6BNo@yUD+FR9z*zIR@bhP&_m=&=f<I8^B*Y;;e%G3BVPisc`oQQS6H+AqHNnanSZqk?SW!<E2@-e=woAk~38ei5&`m(*OkMw0evOdx`=j)l5VEeH>^m)04PLJq&SDndo_@zIv{g{dck$m?HPdVDV+t=24re5t^5XtwrVjS&#r&mR6Z+zL_y|`^oq<oAo^KrfOQck4vHNH7tckz|<NcE9^SbI?)>6?6vFY6<HbH2ux^^v}8FY6<HnUAcG^v(IY(#EDonqSg4<IVVTeo5bqXXDHHC4Dnrj4$Vx^ksWFzoakok@HLX=6q9U99pIO8Sq7}_6w%&*8cS*?OP>#+5U>d4&VJv<ve|TpKqXjtLx^K`uE$*>GtknaeG4jqBDJTd#lTSeSM3Hx~$N@k2|CD@s;ngC)D@M9A)<(v)R!;bxC}_zU~d83U$4DmR%a@xW<>q_3kTP6zRN-FVD-fVe7(3_3@of`$XrFxZ)?JMRnq{b)Bt~pKAZxr0x2=4i!56yox(@`@WO1wEuFQdHQ-k5~F>q!IA7x-}ms$T{<7{oE&}J4IAg{@6Ww)hyMNK5l(;hB;Ai^a--Z(-%~YVmtBYc*`dC>Oz%wHPv@$-A5Y=k3-r%(e$(weowwV5*Y_6c_7yAG`Bc0s*Wu3^qWke&@2A_lCT_KTQ8!mc&qccbgPD3B`F79G3-wdCUDxBe=)PQgUO(`r?N9E#P4_e9(VS4<RjZQDrzqiCrq1X6V(rW8YkYZqecOLu6zP0@sZTD}{VX4+^Ym1@p6Br2jn#R&=0D){XD_hl>G);^p}yN+7v0ZI6Ycp}@|^ZvZ{Dwu>*{`6Zm3_Bov7<sv~j%7$2+%Gn*MoNXFcA$&*nIM_p;S`Jh;xkmg{JL^_uSAop~|K(f+SBx_>KkxgHPR^ioT7UB)lf=bJiWa$czKYu(UZZ<k-m5B25s^>*mA#6E7a9*6Gew{t^%>!Wq{c)L_a=WjLm#_p%oD0{s<n4TBvr~Z1>uKyqRIef40guQ;&ODG8SixzwAb+7$~{7~OIIacTC>*m|-IBs^a_EQHX+T)}`*`@ktv7Q(|Y#rO!UHh)LTif@|xO?+MefOV(?Df3rC`Wti%i;F@v0S-4hhJxo&Oh~RTYH>r`q=LO{aw1Az8@aV4fVa5({w#u-*vFZZQO#-_4mhgw(B<LXkMuAo>axYU!1Dx@U7+>Y=4!fz|l{;H|+aw+B^A<e)=Wq`gryg?{@SvsD`eOFT0L?zgUyFLbq>mK11i5_G(V3?>q2^UMIZ+E<1epfnoM|-n$~#;ZJFz>)=gV?(lt+KC{==hn{x$u7Shs^<n1D%uqk|NPS&5_lc}5hhI3y_SZIa=CgZ`_EXc3XFL2Od+m92;#H?Vp|-sr>(npbkq_g<D!iEI$lp`X9?#QmaQLZ*yV=(zc6vdm@7+4pUT4moahz{z_vQ9@n?1_W-i)iFEmIu%6t!Ay-+v41I(&IwHom+s2aYT5%f6}?zKA#u@x#U;e%LrP{fKdBC5~SiX<isVY+fXOx-!x{HNKpu#+UOn;EQ?ct-o3OVfzq#xo-Gs6x+uY>z?uDx@Ua3?ipXMd*0U@eW`u94&#Td!`-`RU#|bg4_p5Wm)ZTx`w@QF{m8VJ_aoC@+>cy~cWOWE{)jK{kJixYtMvE9{W{=_`*pw<_iN+J`?cr$9@>}t1ozKLc0XdjVf?WDWT_XmFZVOXm-`vt=1=V7iv5!D<$lRC{E&TIx$i1-)%L~yE#S-jTgSz#Bb~3c?U?rE{xjf<{ipHe{?qt!|5<c&?N_?J*bf_D?uR{Tz1QfviT!rK7yE5*)5pKozTCIJGB#ZwPd+CKKk%H0ANHIm{J?V=e%N!O@B`0%_+ih9!k6vCo)d*H^9g%S6n@}+UB(sL7w;LQZ=SmYzIe|dee+yzeEFV1`sTfX@#T94>C5)=J%jXRKJq<-^aJmmUQAdYsXo#VYcJnZ2|w^&2tVvSmGA@ao$$lnQwd+T4|`7~e3?(!dn(}v&Np-Y`bhIj`hoX;_;P+p-;8JD%lRdJGhd7^=a=+ldpW<PFY}S}OZw(~ee0|Zk?JFT*<RL1`X(Ra%lb&)oNwT`;{CbtW!<DN`;m2%zRXkBP5QbHy&Qiv`7?RPx}qxnCEXw8tY~ZSz>q(gC{ulmM*fq@(ANLepG;b{Yx)2F$z-xWho}89hEUue9R~M@`=F!YKJa5`Dy(!Y{JKBh@W(UgbMQ0p0Q4z%0NfWH0{4ZVKu5q&z|W%3!_UHRaa@(hY;+Dh8~zOa0{#qMjD7<zhUcLx;d$_T=*RGT@SEsc@LS}jc!odT_QzaQ{X7XB2Ty`Wq8@l8JQV#qJQN;<4unU+FQDV$7vP!bJMc{S1N0O419$<t3SI!Gq3LiMJRkiMo)5o|&V@}a6i@NT5`Vl%DE=DV2!9Q4LBEH$z(1m!;2+^1(9hu?;I-&0@LG5pIrJm1DR45{4Niu8q7T45;T~vrxCfksJ_;wngVAa5H1bir&>vI%@gbr3W%Qr$%kTvBVR!=kB>E8iB>Xt~2>dua2ptX&f+wP{!V}@?=puMJ{1N&s{1LnY-2ktESEK9U)$nq3A-s@UD1ONwOGB=g;w7jLUIK3<6o1cm)pt_RWH^~?nL;S;MJRp{?Eyas_ePW8B(7m^Lh(Nc#jl~Sz)C-dUxSwsioZiQ!J9ab?+C@4Q6JpcAGiABcC-$BI~<4Bh2!9+XbjvGz5}ff-vKvA8^F!sW@tUQ861zg;CMKeJXPMc(1vg=_!hJgd<$F~Z35SZZ$o3@SdOLmCV!Oh$IWOd_-42&S{AMfS3}Fe)!-Uv1-J%W6Ril>gsY?F;p%WSdIKB{S3yg|Rp83xug=FpD_Oyh;wbb+I0`O_R)#Cnr{V;Ew6cO@rWMyjX$!b9+z@REH-sCZt>H#+6SNK71dc`Tgk#}&w7nG^Gm4v`9j)LPQ`{WwU<Jpd;yciGR&Wd}Zi=?Gf@5BB9GU<pP>VR~uj+Lhp}01BqZJ&7if=(HS;29uxE6Yo6&&Y^Z$)p0Z-wiiRpB~tU9=ip7mh(|z%g)rv?g31Zh%&Y8^HC@Xt*BiLaV@4sD<Kuf9&?hK|=9iv=BZFA4T`UN8#h>e)u?i5<LK)gp1Li;bQm%x)(kHA0xLS^38{H(O=+PI1fDp=fMT&5x4-}gC2vAaa_f}`QwZ~{vZ@zMbE)k;p^ym_&OXFW$Q&)h2oOvC0K>xQs@O(h2j$E@30ER7J3#|q4*j(U*<f1gMUS@z`w$$&_Cf*@M-iKe2rtBW<02|@)MzW8=4PqgSVo&@K!hj&4V-G?PvkK9o~WNfp@^W(7o_3I1Bw5&VqB$18@$UjqZoD;Y@TNoC)tl3*ka)p;(QjBh>3Gd>TCjpN3DNzl7BP7p{-eqLAxV#Pw8qFy#6wK7$^H&%o!<qwqQSJbD~H4_`!2!WZF7Xfb>VzJQ*9FTlT}$KYesLa`bft*DpM1S>d}5~!ilw(w3k6KxlAE!uIdly(TYb{)93N;`&JYsFb;dn-6L6z@Xsw1Q(v@eZ_&6&!ntx1+7C;8<0h!Fj3kY=LftTfi;R3^;@DD(>VDw?8_gcf(5Wf|cF_E4>$1dLOK`E3EW>SZN~M3GG5C{u`PI&$8_I6#qi|!%F+WvrsRg_$xy3IzsUpLh+}B;&%zfV+qBNp?zSr$17vmd%ALP1wwH}LUDOQ@ePFH(uCrYgkrM?Q*1tpOAv}np=DvU=Ko~{?+c2}y+iS3Lh%(s@t=g^YlLExgkrPiD>nB9#pd3jI10TE_v#i^BD&;%`Y*-7PpUeO<3AY7Z#rMAg?_V*e?t^_$=0h|X<e@p{(tHvR+8EUTK@(@E4HK'

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
