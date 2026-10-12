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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3acbbe6269234a22b93f7e44aa8b1798/part_001.stl', 'relative_path': '3acbbe6269234a22b93f7e44aa8b1798/part_001.stl', 'source_sha256': 'ea7924f922aae0ca4c68e3fde90504a3691b71427583de0ca860db32a4c78c48', 'input_faces': 488, 'input_vertices': 273, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.021103398874402046, 0.06987911462783813, 0.06601709127426147], [0.037531252950429916, 0.17436222732067108, 0.1768130213022232]]}
GEOMETRY_BASE85 = 'c$}r13z$w-+sF3|-g2J$MtbYTHXn^sataMKI}xuzigI`>&oCo$8sikg#yFo1mBX+nN)b5@rP$x=P>4<nQ9V-PjU1CG@As^|erv3?ufFU0uJ4=cy08DwzxAxW_I=-bt^LegwNEQjG|`ejm92eMswdugmt~14WhGieGqVTx?vXjDcK@v5aaKa$iyx)A?VfDgzDt}n)Eb$bkvXVGc5;fH+_Y!o<XU!e&jHzkv(x)`8<3rmDf~y%`wq&C`Gb0;XJy9zU9DcD`nBx()oa<K?Em9WiP#eC%8Tc37kX*gu2iw6I~Ht8)%@sNRd?&Ye@lij-Z}fA;j8h5{;3LqAGw+u`0l*<fgkzu(mZ{hNRzXMujWy{gRka^UP=pmckNQcx9c62^UUdD%<n&TeWUKH`IT=?crft28*Sx0lZOZMcrR2o=69biFa0*#bM^7o@-6bZ&azx1KkdpF=zd{-@a>fOx%&K$|Es*O<UYpy{`ux|{<|KN<K4&Q_-U@p&o9^J>ht)AO36B&J2O{bkNfwt8+Bi;NBPk`ugul2>sDGL>sZj=m|xY!!!H~^IwSC{B@K=1+O3Kg=)StH@}r~A&oS1YSxc_J%i=l4`pLiY3)dg=)jX;$?xWd;?-Usz*PmR=nBQ5s+wcqPg>RR+JX;^{jqPLjYJ8#JrRJpV!SgX<OEAv^j|ZQNb~gP;mAN~E^)@&(G4OBAdq*Gd*EfCZhumPi-{G5_z@M7FIT+utwain<w@)pU^S}1w_`tVTy&L%TACdDfH+{E;7mRny78|Fp)7^bT-gg<(w_pB#N8n%iXsof$7T4wcznH#%=c!=4+oYPSuQT%dk8*s9>03#E1mm4%(J{ie5<3Nb<DG3N^ZBspTUl=f>-SdA8ZCV1vmLT8@4a8vIpq6w)&%3DJ$@Xe=fNBNrOan{)3;8SlJi$AGcuUx#H6jk=d0J2^M`z^!KPrmeW~vY#yT@M$bI*s>3di23&uOcIu0||nY2bePeVig^@egi^+pcXuWNs`P_DnO>AT}w$$ogh?m)ec{`DcUf8RBIt9w6Lul(P#jQ)HlOFqX-O+T_cI~X4+7}#I0WAv?#a{PMJ_t(yp{WIy4K6;*`m7B`-j5mG1$qG6DZ|!;oe(UveADnej=B@tBp27Wk3GeB?`_bx5BmbpJ%6(#w>3feK4(9h8J(Hp5IWozT`%MGWcfR~C7#}^BmagYn^>g%y>8pN@d^_+-ef`$B4EcN=GkyQ)Xj!k)>pBGUbpK$ZalflRc|yNmKed~j=MB?$D(1*OPg>M6xZedQ*6H&o-}(AIWBzE1w$=3Os^>1!*z|3lJG*aAxm0a_`;8jAbYIP{d}o|F-rKZgr|zrq%J-j3>YS?er~PsMZo^mm&qoVozxBdb`^iHiWgV4IUpW^ea(r*;tA22fRFmf(zN)*|v7+ox<*VneRlMx0e$3yfh0%vjmO0)lcU<;=mN~y&e3$IQEOR}PoOk8(IM7_b+h?2{KhV5izf!Njx3kUs_;XsxeKp(6r}Nk&a-JH4B6?liHH~-azN(Azy_)8D=k1j{b-%E$@S`(2q^D~A;|^&hpO=}YZ@sx#&Qox?N2=D(k!izaA8rZxpY@jG&t_z#YR{27)0N}TnZEOJciC6omcGXNE8M<I_Y2pLZ|9riBhIHgbzhBFzI#W7Ed9RxZsld(LcVolpPZ-Zxxsp$sQtuy(Dc=Q;xGMph@J;^9@(Dh7oJCFh7HyGP3><!zRFKzRb4sH*^s|}oy^<W&^+vieuYy*^}bd6ZKRUvtNk`Q;<w>?Kdb#e`eMju|97g58)-b(tL6C;sbTt2&KK)Kvr&5gtMe;z$@E>$FTeQ6QTlVC&PThH>8tZG;&gZQx;UJ_(U7msU+=pEWA(hL^W8aN`cckzJ27>fkx$+q{E+YS{@@p^8n0hh^+Pn|tA23X{GOxd+2{SoX>0m6??2Ayz7zCys`o25<QKkQ?Ma+y)SYw0-fQ~m9C5#EGf}UjOaD73OkefCHRp>-dL7mKXEfxi_fMyw`eeP19`CpIX47|gzqLPTA^jz1WquA8llw}@x2xxD2tIda!DQpP>ku!`jgarIoU}paf5a3c&+7d=<a@lINB7U28qAaQg}kpem*u&7!1V2P^W}Q3$4}GqR``7(?5pn!QyNVV{{2eD_k;fa@U-0jLcVvuC)a=U`gA?d5%v8g<lB6IvEtj$(DSUuJ7J&iM_$FrGxR*W{hkT>#jRxe_Uu~ggU>bcXXts3JpYtD&l{V5^tL*|c=uw)EIn_|k^AKMOQs*G(lr?GmCTd=s=ac5*t%ct>mlFsx5)ggN}3(~_r4FwzDn6E_xo*aX6yNM(-P!4ANJP|53cK!EixyVXT<fuw;OQIgnYNvURn39tLEtIacb?AeH-$lpKh1)55F)+U#E4?dvagjyJD_Bzr*i^ypZqycwXkSa^GCNE>4%n<oD4e(|4Dr1m|b;-pRRoUHpU1<#S)#^quN0<oO)AnrqZ6rMP_G3HkmGSDw!k+RW4QX}x|_{{A8CcU~jM?>!m#exsai!MGdEWqpq&%-8egUL7L$t*=9Vu|(O2=TheD`Sh|fWPR_>n{VWke)B`V>bJ;*X)o#P@w-)&bqx9Tl0LHE-fy))&x7~$Q=4_aa334J%<v2IeC-v}SI_&SRRiBs^Kf7Ol*I+QU-(=kZZdpzUn&n#<saB$<k{M0j<;r14f0@bGq3AjJiSi$3;X=^LDMG>mR-m2RUWJ{C)XO|RUa0)VESr5+?+w*wpgg=-+SRH`Tkzp^dl4M2X(P}#^?Q6-6J7i)jc{oB~PEn;d!^ln7(@6BXctHjJl9#Kjf=?`gv}io;OeR^Agin{cQize950ZM_$<HIkGFSSn_AjsTcCqbLu`(eyNdv_5r(t=||WHB3-I3)$6GC8LO-5d+amL=3kc@`DY(<L%zp87PZ=YM&8&DtvJ)S5AT=fLc$===tK5fKjd4VvEM#$z%$mP_VbYMQD6Vrq<lTk>b!`Ce2??O>eVP;UuT4K#}4`aj_twx-iY*k<M~zRTG;1Yb8?2}8}(KF9P(Y&&u<^j*X!tVE?a9&-@09%%XY!Ze7%n9+;>90!@2JrO?lPG5AQ90$oF|~iIiCWs=iLEt$dGiL%zd%RHRwbGJTy6?{#j-_js@K(;6+)*J*tr-y5SL-x2SP?Tx=GwM_r~LZp1`lCdamC0aexwLd8dQ~W6X^FJx|Zt%bQlTw4mjsL%YQaTV@!#A<`nh^Xi^bGtj_$qo0z6x7$Qsd(!ixB*8yf|2d;9t?-EXg7SpGJRzPs4{}u_YGo#$r4AU+{K#Kl(AeA3lN}h7U8R;9ar!K-3gH4oBh3=tcN4d~2N4zr;xvAvhrxmty_}(Jtth@E7n-Lh$Zb>_rcuU&4prv*-o*7xWMG0{jPDEKcerSm-Trl0^tEjh2N=!)4F}IDz{rLkPZM$q@WADsu5NA^1D=IQ%KP4?PYaC-3_R!S4}*H=(=WP4EUn@E$_&w`dgp7Cw(&hR?%A<D`oE6(t0hLKEOpa7nZ*ToNvV-U1ha&yjmkgL8!7gXkCVLHI*-C;TB?KnPxs?uOUH8?}DgNC@5<i_c>5&scndZiTlp<`Y8jSLh-5EBFWWEUbF*2SV_Vgy8GwAMka!c$`$xi^b{5(r|IO1X>0zL*JF)--53Yf={A9!zbZm=y$N{#bbov&k4ah(0%YedT|FKcpD*jHM$924ZntNfM0``#o|qLGr9p5x(D72A0PyOgMJHt1D`?9!)M@YXi@g&Yj8Y$UJ8zf<Is|D94z+ZlJvA-5rTh0MNj`k2tI-ygpa`c(GRVg`?KKfXn}QeKNq}(5c~$Z9)1IU72OEG3NJ^u!pq^e(0{^j!SAD=!SBN#5rU5rf={5Iz(T)*h5i5w{SiI^t9b;ULa)Q8;NMa4Jp7K9fQ4RRjEF0I?kM^_dIc7G5*B(47Wz5-J*?LDIrlAe2P|}(mXmGdN$6@VZ>!0x(ATs)zeXK|F4O9=jJm03L)Gz3>bwPg2YnNM2lmm;u+RhWld*Uz7XLt>hW`QgM+d<D;TO>1@C)!zbQnAo?u+(=`@&tgu2@G`v<uvYF<lw+1Zxr68GafbfDVKQz{Amz@Njq-IszUB_d~PbesEW=E7s8o?Fx5gOee;)Vl6@+hdaXq(IN0acqBRw9tn>?$HF7vEOaoO1$W}QVjb<#PH-p22zKGw=va6*{0bp>0Xhy|0M8)=k4J~V<Kdo!;I`=Fa9j96Lh$`)EBJo60U@|4+8%BSw;=>~M+d`$x##Z8Q;)fY*4M68pS1{WqOGk7>lK=&tv`+X6Z)KXzt52ap%b*6Odw}MbG01il2@UNv^+1O4nh}dby-NQgwEA!H<$YqnghFVckWl*e+t?ZPJvsaZQ#~$I@%rX&YXfDj>RLf=z~5F_km}i)8H9!KDrdnhu6hodMu{K;u-W=_!-zC1UHMtqi6(u7LLFZ(W&rE^d)pE{1Utboem52;3e=HbS=CFej8l}uj9VnCIr7s2%dyagD1hg(C6XD(3a@)@bl!oB_X&GA^1M@Vfa4yUP5pSLU3=i58NA`g3f@az<FpsoCmK$*TJjcmFQY{CA=8*;KlG{bUHj4?uI@CcY~Xw4%{5BLkO;gHiK)ywXK`|RGSdoFcuwR@lY(<p$*}NjA=&*?tw<&9`K9kL|FCWi-h3Ogy4DTOYl7Sb#w_VbPfDEyaIh27Wy*00-i+(9)(VVN5PqBFIe?rCLy>ZAvhIn2@7omr@{{qf@`Ap!8PGz^j<g_t{RK#XkGMPSZE8lE}TXPeh%#oKL<}hr@#~7Tr>~Pg%_c#;6?C4bS1nHo{KJq=fXMYWH<*-N4vr4aBH-=b#s3foPyS|ZtmxT>k)#hp|#*@a22#RTm`-dZ3y23*FYbFYru`s4sc`m?}XqCLU1<P4i?%27WyJAbTpg|t9b;ELFd6^;Q8q5u+SB-&{^<&cnot29fZz;g^q%SX2L={!h>M7wvODl&{SCH16ocVAWuSTYI&<kUWF!Wc}}JdLaS<ZsY>0{v!Uu(ojTV;>!a1-`fwApE-W++E*Famu}CBY{|)_5_-}9$S{Y7)ZS*eKhX0C|h5rhdLH`1mfs3JWa530Ii&!^*1jnN#;CQ$=S`IG9y$QZE7PrUZ4nlBgLU2h!@NMXw@NMwjgy2eq;EL!Sa7DO0Avggo4JW|25`v4OCE=p*Erj4w=xuN*_&?CQ;r3~9@rgzLr~l>S=8qdBTK^wF!k;vMt*?Lbsn}eFzvOS9R!r0|R*d-I3(y78ZPtGS^_#$x'

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
