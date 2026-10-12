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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/da0ea36b7904452dbd00952aeb4c453e/part_009.stl', 'relative_path': 'da0ea36b7904452dbd00952aeb4c453e/part_009.stl', 'source_sha256': '1255d190db8529f93ed17fafcb57435d441a5c3a2003a7ed74e7ae17013cf2a2', 'input_faces': 484, 'input_vertices': 415, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11017286777496338, -0.4086003303527832, -0.4034332036972046], [0.3144465386867523, -0.2926490008831024, -0.11176969110965729]]}
GEOMETRY_BASE85 = 'c$}r133OCN+J<kl2(k-NkVP7z1Z0;eh={F@Yzm^HtV#ohMbIz=kwu^hn+Uj|fXHHlh$6TRAc73^-~uE8F+`IfI*o#ZqNt;SBLg$Hx}NV^x4Qpx{`3FgeCK`o&DY<ps(Y*I-g`ptTg#S9bM#LmXGG-zAB@a!92HfZG-pEAxbdTgW#zPbXzZkbQzPN4AJJ!e-QBZy|9~^WnUZmTR?e_-86ATeorZVFXc5d9o;_~-xFHV>&K`Gvmh!s{8IzOc`Z*(qjLmXCH_dE&b&FuTW-WqKga5~$N~#S#GI#89C6ux7(}eE4TkGRT-c{<9d|8yrkAzqH{8){>I{&NjC8_+#g!Vq)>CjW>uWXyrkB|ArS3h!JS6yev<dRf=e9lr|zO$^)cBNtZ<rLH^F@5Q;b9zbQd$9!-6Mm5XIz<&rOkc(!_Wf#KzKnyNAI6vbkaK36Z+zBVP?E}z9A4|o_r}f27hm$7%?r1g;~D9Crr7l3EAX%0?8}#Nw)11+Oa7k6xB13-!Rg{ue(Xn`A38iY;Ya0skuScSM=$^E*Y70i1b-?`_{VPl)bt}6We@qTL;T=-+Y5cyL;a7prm7>pT}OPoPUzlAzB<mjwZ*CYNc!0#)0g^A<kjL-e(0R@iRsI6?R>92<U6zHz3uDQf*HlBd?&YoFJF!u89ui-r9Uv;moLY)^F5#ZSd(kFnDZ<0%79YSm-!Vb>aF|TwdxjgennpDT59^<I#WE%moM|n&X@Tm`H@JuExvhl)6J!(AOBMOv5q5s`B9liR=&(H$#>HBY&Pdt=!d4Irti(Kg}J_bZymGpz4=9cDC7Oj=6rD`Wt5t}H($EV^yNEq^}Mt5z4=If?AK>DCGr|^oj9vXOy9e%_63Se-@8sOd$A;yA9}HZFW<XPtb9kVXY!q?mHh3gG_=I@z3Vx4y)WNu&sQT#Qu@no_T_u+vGS!oUjES;8_o8FHvU$U%8&i9$>)3HR(kSKDnB%IozIu^8|%Nc)b!>2I_YV?eD8Xmv(=X`*K_3b&xOAFay?u5-hN@_%k}JB{G7i&*K=%RO<#Mw`Cj_5FW<X=I8oxOFW0|aU#@?<zN`<iwL5(I-uh5-%2!|32Rq+eAFO<tFZTG$e6h#hThHg5FG=M`_H9e)$2R?xx=yE!{{G7PZ`Jp%TdTfYw|0H;z4~i@S(9>p;U~>6{G|D1`!ZkfljfHk*PdUWezw}z9@Zc6?e#}|d;PI}Z#}`c*B|e=_WJYn=~d=@l=V}5d%YFkUT?*>*IOs^<SKK1dFwxZ(taVny<gzl`-PMH>&k>$`<?jqekZ=Y--(~J-;FF>Y0gL4f5o@=Yw_*<T6}xIc1|?bzIFc~zJ34Tj6J&4cb&-nkL7#!Kln-aKejLTKln-aKejLV)fzwRJ1+N!wlDXG;@kI!w(s5V;oJ9zw(sTFd~cC&e7Nrw-@fk^-@fm4o;|f7WgYyaI`~O-G7ru*=a=`qfN$Ubi=Xs-VfkME$klVr`Q<&o;3qxrh;Kjd;3qxrRO~y;oL}<%W&7Uq7ry<xX8T@#G;gLkzvTH*eEWG*eEWG*eEWIR2|X~woL}DaFTVZ!>$G_#$2>3IdBjh8zJ97ljye9eZ$G~~PR9|x@wEJ;_X7uCz26)M+qd68IPt8z%zk<AA6l)=yFqEOt`oea{s*QXqK@Z}eqHCYe%gMBc6xrV?{z-co9#y#2hV^1RKgE4&bA+AoIStg6Zy)I)BbpN?q1WEe#I|+`){T%{j&3e;!FO|OY+VBMypKQo5~MP-R{c|GY)pXH$LQtp3l!W$0vTz;JvB*V7pRZzKollACd8t{J976&G8J!@7-(qA@SEA_T|es+xebPer!yzAaUG&mmW^|PuKXs^rNhkwjW}h^v)xGe79aFJ^%Rn)b;U`>f<NX$G7W;Iu-lsN7J_NG5xUk)kf?#{TRo!^QAp@zO*O4=Yu_|{OIm+zI<t?oiD!R$KL9>-)w)d-@|)M-)sMkule$&{dT_Bek<P_&&AXCr1Yn6_2qlxY~_2t<mVmNb#AGz+n>8}zv;&}OiAqD!HI!_gum{5!gmfg*4M*#L-w0~>}+l#Km6s}`3e84iU$(o^XA1mzxglwO+Qrlu+DGPUDrQYIpNEC60GIqo4%|kvG2$3G<|QKwDN=AzC(Vy8oCbaM*Oxjd8z!+<Xm6AtS5H9tS6Em`nHv>!@3b&w>!`Dqxhi@Px|s@J+bp;J@N9xZFGBBH{#oN<(a;$C$SfP^5w@^H|%^_PePkc>HOYZ626n$L|?aso%fr5^u+AM`HJp+CNa*TAN%P1>9rF1@d{NBn11B=xI}*Z+z@?!2QAX=T%4}!ztMNU>Bq8$C-%j7!13ifTW9L)q~7cLxXV^(Kclv;bLyM@rXT9mKT#)|_f&!DM;1=d?LXF8*Z=NqecX2&==S$}VZZ4I7ld`4%r3glq`e2s`5xc1ai8hSd=C#CA2WTK?{>boep>n7yq@yTzEpm+TEv&{&1);)Td&BEZK(E<+5YHfnfpxNTd%r)=garjTPxpNudIA;y?r9IFQxzc8DGA)-dg#dPkyLo6YUqaN}QMA@)LT#m$cIDY?z+#!yU)y^E-D%!Vm7A@4tRZUex1IrHRge{kZmfy`<Zj7tz;k-E>_iV}q{$Q9XTqzBVA?$D33=XkNF`Rc8}*qP1!y{LryMpPJWyd}ot{AD%r!w<mv{&fm~1;m6BP)W_XiS?8zqN%+ybAJzS39gYV2Cj3Z`@%p&!`xof*KRV$Dr_a;=_O=N>{6)4t?kA7=jvLG$chKx_c>ei>A1+;}^IPiq9`1HPxAV**oxi$;ZqJD$KHqt5mu~;)ExOLJ#kxI9F4yDya%O?)$5(IF`%Ckxx?f9I>+zg*S|9hf4|SbcYxOu>US1z}T87SV|E6xwznbd$pOyFd!SXwFo%_DX*XQA#gXZ-gTskZ-l^=h(WS{AK^Lk3RSSmkMe%db6_x5+IzPAoo^}Th#sxQ7>U)KNVlox#clJ!4S|Ej<Gjw}0J(ckk^`Jo5i+Tp7&`<<2V?RQqb?04ajYkc{#-^Fff;cJiVcXqz)cXqzq4@58e*57{o(2py8?UDNdJ74Yx?0nfD?eX;XM{7L2^||Q5yp;aHWBXG1;nsa(sr=ZqMZWXvt>;#K&$sG}Z`T)J>PL%r>i!=2r=E8wf6)C6pZwUo{$-sP-`*F*xAz6{?R`OfdtXTMS?9&K_k|>%{NS#tg}(XAJ}bVxFN<&Q%i`PnviSDCZ2Pj$if`}BwlDe7{QiaJyq5bk@$LIM@$LIM@$LJ%_?!WS<~)`AO!4jeQqQ;UOU1YEOXEjJ>H5}vwe8D&viSCWwfOdZb@ad(J#N->f%x`wf%x`wf%x`wK`=evcm2q7nfUf|ocQ*0ocQ*0ocQ*0T$0aonfUf|T#_&OmsU9Bo4-64i*G+ii*G+ii*G+ii*G+i+rB&(i*G+i+rF27VFO?L<$Z$q_In2L?e`4g+wU2ok)bK;i*MH#->xryQvICyhs^ma?`_1l-}8uXzvoHv$&a^MaLAm$^4`hz<-L>m_IoPv?e|pi8S4(2^HkoO*}l9t6W@N%CcgciEqMIZL+1RI_kQBr?+L}X-xG>&zb6bY``tJGa$dx@-&@A3|Jy%qmT$io4Sra+$Ttp_Z@+g9A8S}-_RIEt?{$0o{z~s?nJ;c^Q`>P=T<D}Z!-p7uqNhytBbxe8^hRa=@BT!uL+1bYPxPL1+wim-^9jWdqB-z`@NhH>9u9X$Z-%?W&Cx4hr48WbaF9^k0&N1ffP0{Sf_uOt(2=mx@$d-vAwuy2bP>D&UW`5mKgU=oZstZqH@XsvhoV=)L*dbAH(2Q~cr-kZQ2Z=923GnwyuyvA+?a@tgD1ja^nO_BO>h|Q>_#2*a-uW8tHbAtXnj~|I$RM}m+JNCjYMsJcRim6qeEb&e})Icj}VHNqff%i;f?ftBmI5~UWz^muXE!SH*(Qga4tLuy$>D)w?VIh+rU-OYH$@efR=#+aAmYATp4bSwuM{61JQfof$$7;COiXv34IxU34V+Is{a24eG7hz9L1B}SmnkXHy%Z!gyL7xRd5G4`nl1HP~4GFJb>s&y+`3WL_dx>8NLVY0INEeP+MswSZSJZ+%&#Z%h5j<66)t-Lj7DoIMllYu0%N0l4ZF(S_@WnuBEopmax+H#&O&8ok?!=bz?T6cnYDoKhc+Z*TOA{zSL?D-;GX!SHkPvcmb9A>pA9na%Pji$&J?t#j6O#uM&!*gyPqUO&sS1cs;rjUgO4EH>RNxcp7{s+6TT9&P1<)GvOL&O}GYJ7A*&tg{z|%!PVh*=+$sL_zv_g_zrj~Ivt)0uSQ>lSHo}6U)BFN(Kp~X$Wc7jjVIigKq!75?#=JV!o3K^A+!@5f*YfCVWkz|#&A7CaU=9nxDk8<dL69vcK8PPRzh($`Y@agFGQEY&(p^Z=n{Adzu!PC<U8trAl%}{W$112WpGn;6x<Z<LMZNu&V`je1NVd<Kp%t4x(jq&H)^8|VWss9zMRiWo54yO7~I^AMsOp3r@W?oR-3_pT)D*6OWnB4jXHrpKG#9h`CZVBE8WPz&)|28>+`ujc^POEzN3!U7*BoY3fkU?_B19Gx8Qp%_-;D&t{@b*M6ZNf!oAQIa9#S*kf=jnE~Bpa>9nT|W30xdHe;c<KK*Qf)`RP#L81YDl0Hbkn(+HxoC9fdbIwmoRQlM=Xir(%RGZ^oLe!%z4xj75b@)zMxGv+`oOU&*9g53y4AsYTZhXTvsPwq=M;*lu`VUxz;<I?_cV82Vj}eMbpx?kJ;D4j%;6OlY8T1^i;vDS>@VOjX9xhKm%JEt8c|!5;wDW7){59TL^gr-f*a`g6rW0tnz#r{bd<;Er^!L0m4(F*o&&_$xja7u=CFtYu68Ir>D6I4r_#yaaLh<*G)_*ygRVdzt=EF+gg?GVQ&^&kxyc7Km-U)w4D84D6^-lrKDilA64uKzp7o+pwd5nePm2N!i#`A>YC(tqQ6Yy~KMtC@U1EKg=N9##PvkJv~(7(ca;BDw;cpLm7x&v1FE&L(;3mOV&{srzF&^j9K3}>Owz*+D@bS1o!u~59+ji=mLN+^B|9SJ`MhtX@{Fx;L{e8$oGgQHo6;(h4f;C=9R^lf-MycdnZd*RdQDfl#eO+aghfM%s5;A`N)=#%hZcrLmeUd~u3p6|voH&zge7oiK_MeqaY{qO_ub?Ei5(w`m8*TFwIT0ek)g5N{mf!~9-qVL07;oayz;ob0$gyN0?t(^jzRVW^X4ueO*PowkU`HY3)&)qtIccZ$?<J=hQ#+_(y_)a(zZ3Ab*7opW*rK+alYHrkU;|Rx5$NLyP2!9NJfgXXCs_!bk-PJqXXiYs;w;kFVZcR=*+OPUE9gV=#;cRkM-9Mw*a5g!Li`-*>>c#~wPjcfCH~OP};r{SdXe;<CxFUK1tW?!h{E4f@ZWM4Fb-ev(0bD?i;(qRT2Ds5Spgr~d3#n5fpjn0DtI@V_TfTcW?N|MoiKpsLMkm6P;aTWRcqZSS#dv1p&4eEzvKfzT#<wqVJL7RX=d2Z44Q>TrKvd&ARO31-B91UNN4RbZ(9hul_!HuD#^`gd_X<RH#-=*gaa*Dd<Ds-S+z+0Jj)liE78B8#@Lg`)?M7GhR=6u%6HS9_!f{9ImyTu?iVM+0a3OpY{R%z`*9vI8IG|aD;%?||a5uOQdJo(O9*<6d$HOzwTzCeYLw{BOA4YTF9C8#t>c%uT2BG)CgW&FHPq;f=8LbLehD#l-pE;UUC_aFG1RsD)(8F*ETq&TnN<gy;#a+-Ia2I$WdM`W>o`Oz=r@*u6uj>CCbuHZ*D3ez9fBG-+fBdL*$?^RMdHb9G*YxH$*SWR4m-fAHEuVPLRL1?MURYkFo}!)q0<THd4g'

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
