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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/00200996b8f34f55a2dd2f44d316d107/part_008.stl', 'relative_path': '00200996b8f34f55a2dd2f44d316d107/part_008.stl', 'source_sha256': 'e292afb319db5636ecd9ca69b8472a8abfeb96b19ec5d278310f5bec890d1018', 'input_faces': 290, 'input_vertices': 233, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.23930774629116058, -0.11902326345443726, -0.21181121468544006], [-0.17419591546058655, 0.2263525128364563, 0.11228000372648239]]}
GEOMETRY_BASE85 = 'c$}r02UJy8y2p=ojNOqS7UI#MSg=<d)JtMPQG%#JW4ox>VpKp73wl&y*C9i&qFz8jC8&sqSm4-Ev5(PM;<ckDYBKtKL}P~i{r?Q`)_ZHcHFMY6>;JodzPrypdw=^oW#Q{xrmTa8PXlfG_ou!a;;3n=Rn{D|u)yHy6UPLGw45?+W+|<@`07)r(LRIw`wlIog=w>0#|DOs33lzGyLyc4?CPewj++`hJvd;>sHwqY1C`$^U~))cfgds<U|L|o_a<%IwR6+kHFeV?^ndeHv0w=H__*`gYAg}AcXwCcy&IiY-)-eq!hdBXDPMd2t@xHKZ}_{8r7GW2f6ti`{*apom2YiyJ4gEQ@q%Bi`vK+afzwZ^??zM?__fS*<(rnp5^ovq4F9vXro{J{E%90hC-@65?2~ckUY7A_*%jcoowrTK6Ibu7`fi=}{+#&BJdP^gxbnjZ8PEQA@MAZum;RgXk$%huui*RU&yevaE)(BcHxK^vm02>*sAeZ6KKC~KR&S3<KO>$TllY*6;u|$XPb%N`plr6B*Qr&AU+i*3=Cks)<0bqWZzbLueLGWqw{Knw|7zF?8UOO{kEri@a5(%yQ7h$m<Nhq;wD%2x->=pN>EHdHtczB$8~lA&WFEBfPmaoQd%9qpU)_-7T0Wn)OZ;)p@RNF-l6h`%b+3HiSr`564h)rXp8iq#w~wj;KYMnZ%x}g(Sx0^Rja>1Ex0e2mPUW{s{}(TbZ>$bKF8x$&iu3yA4B|h|-68!v`B2u~Hvbg-=6x{_=W`BAKV25V|84eu`M&n~krMu)`ccxa)=tK0T@Z=mZWxv--}7cjJ{Xll;lHntE}EGm>uB*AkA5ECmgCw3-rzXb{ozk|bU?<pc!I32mg<LoDm9n!=`G&N-?hu$Jg@oEkM&Z6)tDC#_@9Mm$#~B7*eCNjrvv&~_e}D@*flauj&nyx{1_*hH`8`ENc@R45dSa}zdvXkl>U;-Aiil&SwGu`J~B@0&#%v7ABD@h*nb`_e>Wq3g<oq&yo|q_ujG~9Di8ktrE>oIz{m_aUiJg{LzXU(yh=MF>t*@$G<>%qGSB+XKC&*R$6@%(d?e589Ufr6oXdp2xlxk*zMHqKi#cMS_=Z*$`P1x&of6+M74ccUHcCI`B4j_>Po^OL4d%=EsrS+1zV?&%*D@ZL?lMlR{|@*Ghms}U&BVS4Pk<llEc0(UvE`7=Uj-Zdh<TXjgbAkjP1nJHvhX|cBOXit_P2{M9*@@Yd;QzJGA^^;e8m5?n&gSq(q7I>3!Df4x4}}!^lvK3KC-@^4Zryvski#xQK(m4XTcBXwMC9It%}qWZBaOm>$4B}H?pCuo0%Ad_@sxZ&to%Chv!X(|E}3~@q>0_-G_`vKZ)D0@7~>#<Jen|=6UtpBj^9<ckH7NM!;YAnbd9Dk27RlwDm*L|M8Dx{MJviu&;v$!GCxU^Xphe>VsZp0DPa<sPi!!ab1|~1;6@*SQ$@CU3~Lh4;<GqJH7Zk=qo)DZ(N@%<4GAP=Vgp)4gX~SbuzzxZZdvLTtoC@^^kSf>pDt4m~HAKK388Re(ZKRu6?F6{0ch_iK}~E`qA$@pr4t8O6+%ANDaiVc#842o{e=pSPgziB=&9kOk6MeRfhklyX<$%q6xBJY_}@F&$uM>rqz7CMzqnN;CDJ|lekj3$n);6a2=@rMy|8^dLQw1rx)<+zu7Lw8$BG?wU<vA?-?n_^&EqBbkBny5{SI@yd(K#oPGe`-;nFOd1;iyTb|xNgZ(>2>YFXiLH3QU?Jf9o#>@4{KDjpLztT1M9r9$}ES(~xZrBdxqW{pEQcr9bk08(cpN1cqDEBS4If?t__!m>)x80N|-xKd;$lrfSgzr*W?q{s|@dt|g#zYsHXXE!4Q)GSJw<7+-RT5{v_E_>!ONfPk`M%r_SVr}b@!OBZz;`_>^;BDO5A`H;IsAG7vhKEzUSgihErFjDi0jLY(p%;4jpt)L(Fajymt;wuu}_(Y_?`Xbe#3G-Ho1Fo-)qnrIj<L$Wj(d)Veof-E$eRcXo>mR9Rz>Y>THRRcay){Yfr>+t9HY6?Z3<7IyQPd;`gqSd9%#FiF%tb6!Br6IpQZrBOm4rLj0QvlF!;?=h>oF1|a_9(Q;p*EvPMdZfxw2cppEh59Z|AQlD%Oz2Q$NpDF$O_TMY{8|DT7sju{Jua+<S)tc1{{imd0A7%Ey_4-bC`0Z9=eV5$WCF<G@{p4gHmU(D@bdQW{e;34GXejq-dPJ<`myy~M@iWTgir=@D%(I#A2H(vE`y%9ES_!{HW88Oz?UnuuedE)kr{%bRcx;k!E^CVT+STMbVlBN?_NiH?G2(fDq6aUQI-n;vM0}<p<FoEdmvyoJLx-=&%6VG-x$kr9!vErite2VhT>7&()ItC8d*wQ-JIBlQ#~AK}_$OV@N<TZV#Y$dmafBZiCg*ET_^%ZC{<8!8^>?vPzg}^oguiE|te^4Xkc{VFzHN=nv*jP{v9D*8gWum-`nTP@FV`Jwleehf-TF%Yn`gd}{bhXfE1m;BnJ4wolD<mL%N%nTej=`aTHq?FCx*u@^poo?`D(qqQR<WZ=SzqWnjrh!b|)D7zR=&_Qu0R|{V-0n<3;$L?jc{>1R+o7o`>J^H1_lPV|c!)dKP|TKlyHK--tT7`4s$@jU*q;B^_k`%!c1#oOhz-yv#H1Yb8Ey8{%!QvLEdMS%;**w~2`VDj(x4cLQ}}c>;W|zLJO5aU<}Y)O8*Dnd>R@U_Txs^<HztbDr_$x#Wp{_0~3-r&CK2e{`pur}q3L>Yo21_-CVV-5=_QdfQ_({HfluukHB@4`Dw1(ElHkB;M#0x>Nj_9*7^b19>=UjI4`!qznAoTV*`<x}R*8?-kwQUzsEQT6=l1ez?HDmW%U!)lBlv^1BY-yP4E&&Fz8Yn{}KMeAX*#pM0rTmc=#Te^5>8rlm!`>|bk*(wzSYsbfahipZl``Ep-i_;{i|_}Dkd_?y2FUrV}~CVpxb_CeXF@OfWtEi+_&3BTfi6UEQV_U01$|0rMj*S>6m>-H}v;4d04`^Y|6m-8~`A4NZnqhx-~7zgBGr8LAJn1t~=9@ruM4N67)+TFO$4fK}0w#OtO{!VAq`TLt?e_4mkLVOPw$#ctwG1%AbLlK`7hUb?I&-wEA@?#NSwgH}(=Pbtl^%;%$$C<dUZ7z-d<@GuIGwZSLv5vAYEUEp`Pc>cE-R$Fv_X-iM;ZM>~Z}YFn{xAnOho2lJ_aByy)n&X|lRD@>f28E0C3+3=ut8PCzke<J$X4T5*+-V&Dj<GAEb6D@1?-E+e7v9dH3si1M#V|~>nESV|H+Q`Dv@olPiNf4efLX$xxSmpUTaGDPRH@Qle$In-&lJC{<9S1v%jO{kIjA^{U^j=JV`I)I$|qz8UD$!ay+{cB>AIt-48#c6n<Z3ldPAeS`vImSIKj0txb}r_6i%|2j<E3%)aVwatYt>34R~xi~FcA7r}RMlKeC(KbQR1oaexI^Ia|DNS`kAV@(N%Z_Si>*B{N4yfeFo!f#(&;`P8wQg6(WQ{X>8BYA7Fe}(%En-zXuDOp$J!5?^T$Qud2*DKV+nt8GgTALB@wV>WI?okU+w`UH6-`GQ*f6efhxNmAU0RFQ1(c;(bAoHY+>jeMoqurv<8sYh-Rtxy;)?gma*OYx~PihMP@Cnq_z>3Jn&W+*k4?|wIek0>C3>WxoE}(v;{U-Bf<}_rUxXV7YeVh|7=Ucr2;w=xx%DA89>?`3fxr_X?FUI{$oHP1qbW8G0%UUkaf3}Kv@1ix2!F!l5-yk3SYQnE`8|$5F$UGR$tHK}jPVP4fuY+2n(&+#3b-eFNUM2O@;`9{H6RX!qKHGZsl=`E)--q9Lm^{B&Ql6xh@Vop)-sc!DYtoDRMszP+H)HzaeZv>G5Z`=-+~3;kokyO=-+;d&LgKaZ<z>HUv#-M6)f?k}_jg>MD_w@)Z;RX?8UsCLJhu0l@W-sg^Y8NJGH*uxH25iD(!c%nRjCi=_*9Iu(OtPeHzz-o`zY;r6#NmVrS2KG{7`>>#QO~GZ?)t-i8<-2_?C=t_yHB9Up*M_11weg!S7x}?$d0+zii9)E%8=5=J=ZOPE|EcwGT80ZCpUHSJKK<pF;iLUrA4F|Nna>?cVx7eI@O#QlOx9qq>p1kvmeGkd-zicO-XWQ{0Z)lB~1?xgEI`o8s2guH@F_w$#34rTxim$?e$`x1fGbZb9x%9ZOa^ncSQF7dFK`s1anPe<k-I4`Ne1gt~@2gglzMnXGghc{KTJHpPpnyU2^l(bRopr3cB;<PB_!<Ef{}N-vP($=|UlPNm)^r;;<M_sNH;cc}NtO7qBf$PcLJ$q&fK*c2yFlgLVEkQ2!B*%Z&BP9Q5?O`b)L<v3$G##s6p)F^TWx$u0WI3G&q6`P-VoHM0gk(Ev@HlI_A&Hq%ciPB+Yr2~qs*MMT{JAmu2^b4&h9~6(Keo9u_T`S5T#fAB%co4OhR+OKLdr&>dN-bJZJ}WNFf5pA2pOKaJ(Tetq;==u<xIML>R<s`#x1|mwD;=yA?O(-(`(1G>>Ts>7J}7QS9Ya<+PAjS>iVN$H;*QiW$x1`CqI#vcu)ZmFr-qZ=$z7-m$VwNHyO4XbDfXj&L-r$2q1wnwcao=&W7rgLr5+$Fy-eOp-pi)=2=yNM2>BfK5n1VD@;UPNY>LlPZ<5cFbE&t;O0SS}$!FLUpQIiqpCn(T=8!LvuTxKu?FH>pLCdCICtqib;w{we)DvW-Ddg?sxzttUx#SVlkz}Q#$Ro(psDC3XT}PfqPNrs(l^!K4y+%$Z?_pECpZX(tKlu>#2eQ(KWTmIchscT4t7N4+$Vv@zB6&JBkUX6{o=x$$)D>i<yU9w^$m^-;)HJfv8)T(_Co8>6PA6xvDK@EgvYl&evMG+!it-?iO>rc3J6Y*m@?5TKB%9)iY>Jmtr;(>|&6cw%UP;|U-orIp$)<QM^$>Y2c@s5}oXC0K#HM&Abv$_{IgI)(xp3aY*c5N1rjye-ryHpz+2nj}WK$eOjU)$=1E>?p6FC<F)Rp9wJkJ0&#gnL;$eVaRlh_o8Qp3n$98)MYh#bUz6}uKRmx5+xQ|!a0*pphD>`87z{gABGk=%ydj7@O^YISl0ay@EQveFvldgMB6iXEs`$VxvTJCLifDXvT{Pp(WZOD#iI`X_Q(ayd4|8nv`m^if=jT7j&zCb<;3BAen$)LLYvACW7O|IDV?iQ1g(M6OHiOjh~{xh}arn_`{nMb^pARBy6UU$Qf~A)Dflss7|f)S*;=@)Bw=)t~Io-v_fPUdE<)Db<_2lst#(MfT$P%wbc!kWKMyYG<;qcd612W&W>!bt?K8YSBvk<J15AWy#0U;=f#7(AU2nPJO-0sr)KPj?%K>o~T`<{S)rn5@7'

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
