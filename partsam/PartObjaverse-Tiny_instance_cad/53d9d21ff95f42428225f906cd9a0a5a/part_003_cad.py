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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/53d9d21ff95f42428225f906cd9a0a5a/part_003.stl', 'relative_path': '53d9d21ff95f42428225f906cd9a0a5a/part_003.stl', 'source_sha256': '5123939a495911fa9afdab46769c7f34ca75742528da15a099ffe610c9b7a3ed', 'input_faces': 273, 'input_vertices': 249, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.05761224031448364, 0.18127399682998657, 0.10166158527135849], [0.04047705978155136, 0.30678069591522217, 0.15498940646648407]]}
GEOMETRY_BASE85 = 'c$}r02~<^8-^LFPDb6ESnqCd3M3N+D<>ah@k`qd(*AyI5Bfu#T4>`*qgQAJbO$|hHNW~ev=9{7@mX;H#*UCs=Un|Y=&3f7Y=h2UQR^M9R`d-%B>-q6(^S}G-v(LWg91HL*U!k6cpQc*Z>h41>HqbQHs%iDKnIYkklgEcdcuo(S<D%6PuYR6o>Y(BN0i#^BnOaoK2_X^V!&`Q-wConzsilXdW$63ik>TT}k9|LULWuHx$4!k0DfJPP#)XBH{@&^h@6H~U_N_fEb1nbRpDJn$LG!jAR@pKCluv0`V_rC*QoEI#Bi?aNyq4#3P^Dv5jCkX0rg+=HlhWT(!ICZgUEew_b<XuTB$<18v-DqfM*17Qk4qiRYm0a-c%yjz>~isTProeX?PFulNxwDQ^5wtJE69{Oz8l0_5@N+WE`Il^_(xsjbM@5$c`~jmo5gEwbn#k?m*AtPz?Z{u=@Zt<I1N8v_^H|A9qv=aTkQKc$#@ciF`n)f4@;fjYKk`kW8j~jmGM|czp_#4xHxdU)7+)M{b3#PM)NPl+qZ;?*Ilcj|E>X;x4;q^r=?*<^!N9{aXsmt@8tdb#9O*%Nq>9plMUj7(@?+j&r;v&brL@G7W}VmF%O}+@Y{~yyl0ey_wj_!3oex7THN!9{9T(1HW}wPAt&W?6L*N$qKCrQJ0*22LAu?^-?@kNlW|wZV<h;&Zz?K~x^Xp*l=Vhr6&&xv)zaUxsW$wN@4(+VEc2l4e4HWvqzmRDc$bV{FZmJPT1o0Vet%QOV|{!DKK;fC`TGh-<Z~TWF2MhK3G3n5Qp`i-R`@g7$7P%kEI982g5V1_7UK7vQpZ|!WW5}hJq`T}N-)k_L&WPdR-KjO^goXCp8wZ6spFO?{k3bKNq_4L4aIByZSeDVN`J>2pRSeuJu1s_=_ixrxGa6v!+-0*@uoy$JnN$1uYM-y%ii7l3-K@ciq~2#Mt$#TQeTU*r%V41dt{v2FVk_pZluB6=A!?NmKgu$f#S7y{c&73&ZEwIf3A`K4Pu?<!H9k+Ui-ic>-<1f_>7zIHL8m@wqBL_cevV7=jS7+-_H;8&@uMovg5J;@GHjo#2fx*d6@^}^PjK|t9gpoUT=+cTQN-L!I)V=ygqoG)Yof8;W{n4zFO*x4oCf48&JP`h<L5qqpzjzH&-wZUV-pkBhcSH2;;n01%A+U)c^2p%ujJin$&-1tQ@axY=6wdZHIU*r91qPhS>MoOn~>O?KDok@BNihXH1BEuKuV7)<cgK@b!~qoVsxe`#{7z=l<P_u$~Kp;q7rat_$T*XH;|eKNg`*Qe*Ls=mz5T<c1gzk5?<dCsld-?(OKmI0oZvr;FFew-9es-Hy*)<0js?8-@LO(BOP0zhx8FNylZ__s+PWesLp=Gv+7M2|k%3-m4z!zsz~qv`xGb8z{%?=r9Q5uf7od$LvG@Nh5K-mJSoI9UFce>$w@$&zzKG=^yKd<Ek?b>*1r<lCci=d?mk+wZj)z60bMi0nhbm-@ZFZ>et>N$L08_3$FKbnd0rPBc#54T`!!k2dl*!zb%pe_9kvv4|69i7eDfv)YsOdzpbQ)czZ2B@pgR;_RkrW&|m8-UUxl#{{43+%6RhQ#M_#^kK;AYCrJMuelic1#f#uK79^nmP1I@K0_Qz_BKp5xz<t|-eJ_6${LOx-^WiA$!!J&cm-)Fj6XWdC1oQuC2l3k7`S2-roUa<y#T$R-qW<iA*dOf2<D~yuPxKEAlK%SkityD8%+E0w%zt6pGO086cg(-uEWfPRQa2aLID7AP_E~?O5#Q)B)~9>UQt_)-U?2W^mh2~%smtN(RG0qNkfZ4TI8eM1*9zmz%#d-~e7eE!FE8GjRg85$!4v-RP3!}qPx8uo?Rzg7r~Y$q>>C}6mx#YS3EyjewT_nchDVO{w?{3(dCBXE{zWx#T;(!QXJA$IUvv%UD`+3S-*c}omj0geWSo|(9`F~>!MnXC^=(|AR--Nax{ER%y{?~($Nu7%3#C5yRhvr_siS8mz}IVz>*d~`n4dQH7l;q&BmJ$9^Wd*+7q2boj&Tl6gx5B}m%NRA{$#9tuJ!nrGo(&x06uqeO?*GL>I(1UgYUIZ99Tc`J0itj_Qt-^Xb1L_theAJI-*X`C0NfF&*tVU|3`a_v+W*d&;G{kBxj%54WIkqM`z#2AIH_a_7NxVRg5}4wJ)6ftF!REAF|Ear?-~*x3uVVw5-=YSSa2)Gt9{w?eAm#RLyekpByCfY5n}XbN_%CtmpVVr*Z0szr%W7RYAt%$P9|~`I~vOC!T;e&9ft{(+r=#IWLZyN8wH9(e~|`Sn1bnpNvzp=Eyi5bNm-b|GL9)pVr6*-)^#aZEsJ^b9xBsZ?eIg){kLqgEy@=?W=pJZ(5(mrC|#t`MslkaT|VMJiKY08~I1!P1l9p-D9!O-&{v}<OlGn`wDU1r@)VLz=u`Aef!WDXK%WG?RQ+4$mg1_ckAU#;?4VswQ}2~^1EsOajY95-n_qA=S+YvUj@$v{d!~mYb2tMX`gfyWW$^GRjo<DGO5$A8$S1&5bRe^M~m0ocA|c@tGKV5z7qXS`}{L+-shit^FDt!F;0BoVCnz-K4i(hIQ(6uBCL;L&fYr!`|X}Ps5AZ;e4Zcb96aFU&EH>^T~*`7yY5H*DjL4O`o9Tp`hK*u>?Pi~R!PQhfAj+GyRMFbpO`J{S<f3L^KUyeRlNE8SD$+m^?OI)dU5o{zCH3`eA(+xYk=n|{oRoX;!WT0_U@tZruzYFLJoZP4H>5~st>;Rn|%v!y5Dg4w@MVh=PK%?_+y<M84JHV7}v|-T=c)aQ@r_p#`>V{a_Min|IyAih4-C<<MO?U>pH%>c=LUf(R3pEo9?@`r;*~dq#?Mj4^4*u{s;Imr)56%8+C9Ub;w8(?{)CB)B17Q4R5+Xw5+}YKmK3XX9mS!-;4OCctbD3{J6znUA3*0EWexXKP^Ywi8tS`+M@iDvHlBjA3kCS=6T9c)cO1n=AlU<>J%oUj!!Y}&r|=%FYC?s$y!<_`X6nGbrn+|>+0nT@E5}I-0i(qu3tT&Mv8dXarnNo|B3ZkJXE~-{@l2~75z>3`NsAW;?2(mj+&KI#hacZ9JlL>H(r{EI=!OoPTu@HlG+JA;vD9`em~r|f8-<H{Jdic>zi73-fWGp;kwwGB3@g*0PFwO7F^e}v)~WR$37okjQh;txfs9cIZJERW`)%6G!5sm>Rw!rODBuhCdcDBBBnX!XI2<|d<@3pG9G@5`%1}A!f;(!aNeJL)AOL^m0)<&^P}S*G4ST+&E=`^rsq@Js^6Xa^Lf_l(;!XihI(S1+!!JAV2d6PZ+b4a_L~jQ=W)k-opD?qCF0G`-TK3S!~eAz=keKdO-AEY;tO}+I<37E-xuEf#cLnuz(0G>(<2-G`M%C}d6m7a*BXq&{O_uT^HMn<e)JHWuL=XOuSVTRoz4c{C-D8Db^eIeWsmFmdxkL+;7#u(9G2_i&F?X+d#ZdapJRUSvCI%}ey^hCu3dxcDGB>6zrP%(ABZ=<&#~k^MSs)#AFJ+}F8w<!Mt|;C)+YntP4AH$J44_{F2a7eBp3Tz$F%ga<9zl$%5wTJyy^XwWyiy{@;l$BS@@p8nl*Nv^iN2}zS?RQ#@}todYKo~`#MX7#~Jdw>3ySp(*8}7W#116IQ^@D?^B<qe$`9wq)MBsR!<8ZSLUAtlvF>@^6&piV6ylB?VkiXw*PPcNno8?+NEtjo8la13R&e+at=9_xrCfbj$_7><H!axf~;~n*&xqjP9o1E$FM1$%Y2tSmmJM}kF4^2vdT!Z$|$nR#pGym5;Kvkawj>7oXe)TkXb-3Bo~*qJEiSrX)9qClS{~#m<8lZ<m1d8<m2S6Y>MNV31pRv$noTb%n!*6$+OuM&t%RZ&m@O4KOn0dK@KO6VpHtP96<IZ`!KtceaM}d9mt)?o@|Oem~W6(zDD*SH)m7)DzgRoRdQ1{#f_OQ$&JY`Gux9@wj#ewZo>2?t87hfLT<pO*p1nY>_)E3e34w2T$A|{S!F|VO>zx3#kHA@$SP}*Ym+N8>yTBtk}H$TGb@nGlU+3Ys4T~<KrTnF$gD!HNUqAJxIVKUS>-F_`eX~6;&#l}$tt^$+mX96`;xno`!ENS`;gyejwHWL4rY!e2a`jY6Um|EX-q458hJ8vJb5yC3Y+2(<~Xv-AaV$K44dLW<`A+<KXM>BfZ2;2Kpx2KMjlA+$)>n7^G&kKHssD^FE+*ME2|Ro1vbUim~F__$nMNH$?oK~%x>hi<c`c<<c{PXOh2;9-sB!+o!O79liy-f+@I-B?oS@X97<L>jI44rc@TLxa{_rd`5k5$`5p39=11hI<oRrhS1^~8SCF%qtI1j9UCd9(yU6*>-DH(}$SMz$^T{WeC&?$s7uXbEWEPPxk}sFGN2TpSX}ia!_!je5@-6Ze=Fj9S<g?7n<g?_X%p&qp@?Pc<@?P>5=05TkvW>Z&Y$LB>ZYHlGXD~C#DmRi<ZX&DvgsgHcIfJ~4P4Rl>2J(9HHs<H#ZRCT@17wwX<b&i>OgmZS7i5)Z$fwBHnAgeI$p0#B51GF(uakcv|Hk~D{2ST9JWW>l4cS5dkxlUp=C@>(=g2q6KQO-}|3LnZxu5(U`D<nl`D^k&*c4|oQ^_jh$l2s%ra@LYkDN?SW5$qG&LyXj)0xrabn;4O5?N&~c_sM}o8qsSh2*cuSDD3Rl{d*($^T?ie3yBLe3yKmP4Vw+if=PZ$hXNqu_->!yhJ`vKE^ywR=JgYjQklhp8Oek8FL|d8F>M7HhBSg4x8dxr7ghMrCh!8|J(nb^*=v`+}M=;pS8??>HG*+_AlK^Z_u7U&;|HbRNsN6H$&y*26>&j6V?6$L&@wH'

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
