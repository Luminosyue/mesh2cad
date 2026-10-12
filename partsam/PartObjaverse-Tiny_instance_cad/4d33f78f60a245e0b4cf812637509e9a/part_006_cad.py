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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4d33f78f60a245e0b4cf812637509e9a/part_006.stl', 'relative_path': '4d33f78f60a245e0b4cf812637509e9a/part_006.stl', 'source_sha256': '7b3138107c15b26baaadac906bf8640b60b967ef88d008b19b7c4f7d8e5509f2', 'input_faces': 437, 'input_vertices': 319, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11343404650688171, 0.3707423210144043, -0.053912386298179626], [-0.059921279549598694, 0.4068044424057007, 0.13933904469013214]]}
GEOMETRY_BASE85 = 'c$}r130PI-*2mus3ZkfJIGbV)h$0T4LOATYnkHCyP0LEf0f%xRRIWH~H4}#r!yykc$>0Er5a5Kdt!`hL=5R&Hp-!55Z)I7j-3If%?_U3txLNmkzUTYsS<m{vzyEsIS^Mn6-W$lM2=`jPg1*{`ti&@-rnM15g}3k(@iB38r%#HR6ErI}K@&a}S6{B2^315=QDZa_FBbYwj+rwl&i`>g|9(?K{R92{r_7F<8#iIr_}OujV-$aC!i+gFlFykoAvQ*?I|ug+3-k*P2=rU*_kaAVD@QQg>mI3)+1zmc{6Mw-?slHaqJ4R};$pxdi<^7hcUb=WEi4{A<c`JlfU{W~7lYgjtbFy8!-{AAME&*E7qeJitFcvY++K9Zdfkhos;t*t8kJMQaG}*pWO;g0GS^2Rw;_-1pESGJ;`;|%+;4ez>hsL<42~P`{v(gA&%3h6%B9_j4+*9E?$25C+qrB08hl(@GTWz3W**1Q@8Yfb&2v8=wBG-q#?)ul+Zi0!r~F{esZUL^xOsLC)pvYpR|UiMjq}nuF4hKYX88+mj$`?!>k`=4UA@i0ar57Q%i_3^y)mET`p!dzZ2hvEC00NGCoJyNN7L)BoM;`dotr-`O6R!icx!MRZw(%~JAr#$V`s60ooCF_ERLI#vhz8vH$PFx_CI*nI$r(Um;0^raQ-Cq-&bIL4(;4<ySkd=;@8VbTpwfRH@Pf7SHGBj-B0}wTG_^(uXHl4`Q0ikp4n_K9oLq@`4tQ|8xF|fxQLzW;JC5gm*v82k;w9|3dVEui20QhIc^-8p3L$YucfnnhM(s7k{Nj%H%G<pVfmeGo?jnX%+7PBvXu6vSln1qOz*Q#3B8{-?)p5~xmfU964%FEd^eZlMuTR>92aFF*5|>nac5bO^?5Lc##-E&l}!9@r1g2QbMxdv2gk*&Ry?2ID4Odp=K4%xc{d}S<HpPzEI0qYd=J~FteEA-6(^mSZFkBP_p7{V@#w(?bX~G>v&o<gj*A)hH?#b}^HW*=;gosY>l*&EwsKrQP?^bbbNkiZZ2b_oLYB8kEMfVpTgupZqSFss**<^jp(7mEFO5HH@xmhFDch+&DKvxQ#;4hNY<=Dix<8ihuz2*cQ&gY(4&5JZJbGS42FH!#9$Tt&16&lhp33r}ug@FEaO1|JtsK`sa%OT|O!{#*+h@OTAzL4iQo{CMxV?<y=FoiWya;=rmp(qiaou;ibzby46Y2eVbS2HR=a~$S>!0t<<G7eoM$cD$PM0b!JO_Mc)eY=G&sR2XjP+0E>dh0~@;GkXZC_lS`?>mi^t7&5X77i&S+^}+ukNlOKF5#xeD6=st9JfqpJc9Hd>)#|_6h1%%yIp@{?<IYjXOvCn>241I<7zbsgGxhb^Ww+Ki!eTapTsLsT>!Lt~%KI_kUQ;)|*Y9<>nDpiKAE^wlRsFKO!WJtzVbQa{cmqxomyz;R2R#`iA9t(2qrI{h=A9EMM~m&zouo+2cxBT+VTG%yx?l8+VRtXmUI==eYI#WyW7GQQUd`CF=7*bGnb%xPJSIbdHN-G4r`T#xx%X%R9Hv;<%pOCZC<>M(;w7i=wwn*#0AP%Gf?W+v&bw=W7a&aNI9vG`&9^FIimQU6=Y#b<lIBjf)Y(QaNtKe(hlEt3(vnUpW65#qt@$(pVn3o8{)@V+9=7NBzoju|1)bt#@o-xf!;uobA)H$l`{LXI`qL>-pxlE$)|s>*v|_bbqvQ=g6niIWCT8&gc4w#7+*je`rt^$Ms3w@;PokKeUjoKbl>__75*AWBZ)iNB2AXoDuIH;ke(ear7J#8%&?WrtRo`DD$J|SR4QIeqrN!)Hnyn&Dno!<+$tTni|}Bb}ToKSkPf2$BiRF$t;ibOK1DIo|Em|bzid|S8mTeZ2wIYc<#Cn+WA|%=z3fB)jNudEO&Z;KI}^OJ3D{2dk)9Nz8D9`^^>((?s}hV@P7^)$IT<+$4}(AvABOS%V+dSXZsA_%=7did2F91gXnoFv8~0O%{Ej0`QLU|FkC;`D2L-__n{7si`aY7Z2$1P>p5-&o=ju8clUIToBeC&vHb^sU%+v_cU%5=7c4Ag>*G>bF5>GPWak;Nw49y)=`D2qTxF~8<Y96=bEiqyhaIPj75DpKK3yNKd(id4#*O4>9UK>Nb0%<ojL2(gEDs!<&T+j|+rx6#_o@AL@tjkmetG&sTz9>0qoi_<n_hYJ{A1&p$B)td`n?@R)^XQQr9S?%=zeYEBG$-Z`RTw^j_bFMJJ|XU=sC6q-x(9Z%_E%qMzZ{uz$BKh{dybAUC#sdIs32A<+wR0p@8KfyI3ybKPh7C6ZBHHKJEpUoAXW_VCPJDvYb6%W2Vx1xAU==DmWg!Z5KUPc#W}m=9a~DKV3DCuIDzMd2&?_$BiB#sT>z0&N^6*^In5zj)>&u5mlX@WBI}GB#s;TB8}y1qgk%sOUvcBS+cf(eO=ejHTFJx&la)uYa&WnzI@U{+;qL}*b4_ZZiI~}XL*Zwx=z}-e&^c?jvHr->3TRfqR{$0H1WD%o!`6XtoxLm>-T@o=D6_b<zRU{e(z`J;l_HFdoM}jxbf{}p5Hu?%W>EDV~zeDKV!Mx;8GD=kMmW7<9yY4-Fs&au>G_2a+Ys>fzFqmH~FZ7<Hkp+*7*|e6z;Xo<I!*E^K&R|J<Gjsr?DJAciXw%<_5hF#SimnkxQ?u?X`Gj2Ksnjq30PJH^$%3=D0aK%)xOH7a7g=58Rl>ar0hPE?bZ9$C~}=x>|$363cS)+7|~n?)tu~!Fx`p^D7?a`pOFx1EU`LD|PsxFT8)3OBG(iS4^2u?N8Ldqt2E2KT%H)`Ct8sIwZL7|MySS>M!M;Weh-m7Fzx7y0MHl$ep1dmEjNHAD+_B!0QL?kM-ZdK9uo4$O8~c_ebsr-4FZvBiDr<fZPVTF7#{}^<<2Legy0BGGf7F;VB(0<2CrN!Be`v3}5)Z@RW9!Q5$}3c=d6rHTW7lrQKxIf?o@sz+7&a?Gboxn8`J7bhTOPLwh6FgRX~t-pB&FKC(NqfPPQLX&GV2k<e%0y$^jF>wkcK0DT7Qa2dnFhr?64wTw>iJHb=hOGYF3jo>NWN=8Tc9pQOlu2z^W5?(9J6jp5}*DT@Ck0Xachhg92$X?Ll$gPpRpc~2)v`Xe*p>qYTeKcafK{v#@kw)xyXdkRs%g6)IgQxWKGN!?w22bfg8BfB05}wkdWlV)X6<#1_%7vc`Z#3p!B_7P=nq@U~BJwKeRoIt^90<J{`FZ3(=pSTw$YWW8oFPbiYUKS0?Sb`AGU{l=RrZ9=gl9l2PpwDDm<T=*p3(s_2Erc*Pw6Nb6W~vP7l4^E;Ag;#!u(4x=TFE6Lg}T*OQ4rv-%{iNXaji!asc!vGJ<84Ll4FJh>YXl$Kfgcu8b4#Pry_9X?VS%Phj0##$(`*!Bg5(Mnm`w;VIors9O;E?cjN0rlIhM!fS?^T=Tw*+#8{E2y!rVF!qHYdqVd{ZjS5;{i%#TGAf{lVQtDd34Riu(nn>Sf`1C0(h=}Np-*AmQbq^x4)Bz&Bf|&24?Lw?$Y>A0J-j-YX&C%r@LFId*StrOLlH{%MeYOL2mAUW*MSa2Zi!q6+FO1fye{+4(Ak34|CUi-Bd)SHbOVjNU!dz_odfm;wDQz?l#D6hQ{XAxRmKzWpMa<Ib24J!$H41~nX=($!+Q>MyXO4``3;29E0JG^ejWQ(B6o#;19=p3SLojIIL^!5Mk9Sg(7KyOtgS}6H`aZ?{GhvG{h8eJPeEMeKB(C&^*%xVKGY~ZM@E7mKLMW7n`9KiFNCM`4S46F3$bp4`CT))X88=P3R%@uVgDxRP3T>P`YOy&1+Mf#86U~$f&3KoAsHXT{}`Uqhh-dte+-_|L*Vs-K8AHu^`3$I!Bg5pMg#Z_;3?fi9S{7r@H{ZnQ}CaH*90@U<~@wu3!!vR<Q~vHu&*bw2XrswrpO-9z2tj)R_0b3>1%@4!5XpF8tGnGhk!i_9gOvLLF}9$9fF#TQtuVS_rg;;PR4ve{(N{!r^wg?e-FGk%ybR@HFznQTY0XTT4RQDV3o+KrV@Qppi|Jh67`jsp%PqaFS&P_%(tPl1g-08#O^?QVSQIdJ&m}^b)mPzTLG;+wH_&BGWcY8N_UZ=!`I;{{Z|>2;7@|r1v6#A&w}??%)JbA-bG%4P<lD?GU#R4w;Z_(^a|vW$X%e@$>Ru;aY0c2mmu9&BkwVdbP(2|VC|v%Vtq;O`C1THITST-OI<9;FGh{hb7d?L<S&4y^cERK@QdIn{V#YIpo_3>huK{-xn{Wpb`e?CT*Uq@&|A>^BI++<hKt}z-;>c;?q7qvLy-PM#v>Z}DmR9{FT+<OU*$)j*U8uke<wVp$H;gE{wwg5?k3|e@c#l&=@(>7hd&*j(mUX-fu4@_y=wE`7Y}Ax2fY?~4fGo9TZ`NcdL8l@<ZjUF2f!vW-V~H~3DTOT{?`Tao1#W(HyO<|@|(d^dcCxF3-VQNhT4~;o*~Geff}WQWDFAI4}z!ki!xq?|0+DCcforT`c<rj_F!JOYO|~dOF~vPN!b4)^o!`7g!&}RkOZ!@yWHDcMzWxsFG$ytx`jr53)CpxQX{W6bPKHCl6wjSag|%5W~|h+1o^X2qjYx}g9Z76;VJ#HjG6Ff!c#gQUNZDdtlhN-^VY65%UfU@kX6kF?0*^hW%S;F`VE+21Gv&%<lg==t_aHC3(^BL^15oI`(xb`ED(AC)?djzw*+yOd!i;?>H~uO1E^8@Z!#7O@)yHXI!(rY`1|20{XM)Z(EG9Og4ta&xn}ta>?*RVxr+U1&}ry>74=s!!&Pvl{pH@rWqcth-xQ=fOC7F}AC4NO17!5m$nOVF=`ZD;?*#cO_e1SAsmlcUWvEd)UdAFp{vvovr^+aWUkXp@oAADXF2&kkdoXW6wOPIdb0Vu6C-$d8r=qtL^-j#-1XsF)+}mBoWkLBHLAs;VJv8!rphoF1jl53KJ+S^<?)g>_S2+wd4yj87`6Z}PdY+7hg8YT>l-?@i9r#fZnwzitfBWY>555d_ZG7k-``C9r{43Y$JM(0(KYsxm6;WF~7YaA|pZW#gW%bjn_zy|I8i@'

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
