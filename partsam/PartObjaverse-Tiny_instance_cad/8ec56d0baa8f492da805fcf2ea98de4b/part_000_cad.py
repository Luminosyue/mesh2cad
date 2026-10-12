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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ec56d0baa8f492da805fcf2ea98de4b/part_000.stl', 'relative_path': '8ec56d0baa8f492da805fcf2ea98de4b/part_000.stl', 'source_sha256': '6786b912d34d6ebe5a9fda74f1f1ecf2e97c9203d44d3e04d8321b5e911eaec9', 'input_faces': 300, 'input_vertices': 174, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.23630046844482422, -0.16263729333877563, -0.25489771366119385], [0.12989690899848938, 0.10585017502307892, 0.14909818768501282]]}
GEOMETRY_BASE85 = 'c$}q~2~-qU7KTePf+Dzq;!3$9f`Z7Vf)<LnArKV|ve<-0MGyttg2pz+Eh_E=m8HQws0l$QiYO(U8^&cuG%=bsnK;>uF)_(#G)%vHf0F8)nRDjMwCA1w>z`Zq-MaN&Re@oXELzw}{OKjtS0rz~)=rYdXd~H4ixSf_=fo#w44yZCX)~!E`Qp>0+e5-9hebA%7D-u735gl;=}yCCC%+_LCs)}iDJ?xSJ#OC2wDg2T;RnT~WF(sWjM;JX6HVU-4Ds=Fm4`aJ%FE^d@zYw=;4tdLN|We!KH59Vq`LC5)AW78?JGj13H|m7-*7H~d}Y)$^7REP&j{6ZK7T@}F{K5^pUN*4@zOf!eTu*Rw4UOFuh$4wFRU#SYRG*^zFL#Sd3uIZ9%XbX`BHrW<xvL>q&({OT=EUNEXreO?@oD?_!*q%)-1{+-AyT>@73MR=GCnaJ|tBB#?owF$@wD1>%X{oS({(i=@7-MfA_kq%_IHVF^A$(KEI@m*KeyQU)QbZqFMZ!&N<YNIR-OdS>sH;9J!W!>9=66=V|p$>UVhPMYH@5gUOe^^Cw?vbU01l19W*5KjhkZv-4dw_dVe&Jy)F9=22oi$=65DJg>dJQs2NzihIw4^W6WD*TYdOmHM#aXq`5{!TQ_3(7gK0I&D8y{q$25S2w>-dtKzrB_}Cg%a}TCJ!;?y$|ILKn&pu~0w~^?<!BZ!WqN!->#d@$R=Z9No2n}4d<SkLUqAj3*Aup-oW37kXcn)ZwSnS|3qotnu1n0*Gqmn(yv=-lW5h}7>x<5{X7$*Pp?F#SnU8<5hUPU)b5v=b372ZLeb)cD?Ks5+Rn?gFZFfo~U5DW1Jl_kM;??0sjt`u{c^rBrP~G##(7rGR*|2}|w|MIB$t}F^{$X9C-Pg(i`)bk~cdO0%@8wrYajCbewRNfmN2=(&&VF2Fwyr!IDPHF?o&9}{Z<Fr-wU~6k$SSk-X4(A!<sICbe96x$m*PBg_LAC-IA_-97R3jtu1&^Dvp#=xG*;{XzE1w+OZhQ{T3<>YRmt-uvH$V*M2hcUc~)D$>OY<Plx}xcTc@FP0Q(0UXg*^>0;#gDb^)#Heb>&It)Ho%ldl{vJ7czgpTEDKuJ2`kGv836oTBxc(e;e>`YI1S$|(N9{R(Zo-1Q2t_vmdE+CJ!flj(k-k6u$@b{$*pJVE&?(<-#<L^;@v@+*h#oYt;4y}F#@rB=I7n_c(jC7ds$vzf2-A9#w_>4kEwZ|pvSp93Wo<=T1-sU@^8bZ@4XYxk-C(JZRp(D)nQKXCt%8y@gJ`aIA;^^UdRb(fbw&l@!&o_zUv8vD<}*stGCz8aLn>+4Z6KcAZ07g4@;$9X+I@gZM!?n=HiF5(>T&uET!J5WsVO9zp!);e(h@C)P{o?PX5Kl+KEH{ti`I_n*uP`u=MpPsMswyp=Lo(^j{&wV5L(%v5AEBQLgBY$%9L!L(_-_Wa)eC0tJKet{P$9c}Yp!>3NVgt{s93x-<U@Xt;#d&lmzGi<_G3T*SIe*HIL*!3%;Pbt*pL}KiL-Lgyr?@{68~OcU;`i?e-#BO&`D#f6Jr~twOG_wE|4USlT>B;YI@^s$$e;Ou`yX}hD#hR34}S^QdG2HKmBS6>8;{-Q=S>v9m#9x3a{QSvuK&whoM+w>@|D%Q*<bF)=X)dQD6NM@o;>g7>lCl^R>_xKviZDzs3zZ7y7XO&kAKGXpDQI_p7oe~L)%=wzM**>|2Tx6pT;YTc;4a(biRsZF8PM)JkApw%Kcdw!0$0W5j^kFT3SEGUeUade_BoP(v>=1S0}$=f8~c<|H!aw<l8=Ce?%Pl#sMMZ8(kgWr~1G0;{1<-$(QcAkgxXL!};yfsDA0OFZt4tuAKj`<0)Q=7(>2s_6$DXkvhIEgR{st*w5qj={K6^b$FTXAG&KdcpYvSLB1|4mG4_Org5GZwe+5(&fdWBPm<Z6>rU~8(R;|(cV5ib{j1X)e>3(t)$iSg;|s%iKR$Y$e5ufb=e;?e`&R5s_bo$lZ}xXsbN!h^$k*Tdj?PyncOc(jUqHU@`xuJXAMVC|vn=QP-&O~n_q~qf%PxiVo}$M3@^yFer8=duBjigz#B%*^@+Ho<^#huB(j9&-m6p*yH9F;yujp&I|H@6?zXcM#??{d5{CrEw=KI4kOY+sJ8+o6qMeIL!BVRsPPVw@X%Y1#i^Lvw2x|j1$t!MwvOuA3&8=SfR{78NuZJo@|pW;YfCohKa`{lWma_Ud-U+8(L`aIzG{>D`Djqm<UzT9Cv<<}=?kgwL{aQ!h~^LumrGV-O7<G7xjP~N{)+2kuV`Q*!i9jFgFeLng6r{l>ttZT*hr9(mVd{BSzp!#*?t`{g@%T)5^=oG47SJs?-`TSUVzmpH=@bf(XAmuS8$5!w<9Lm=>$(7!Bbzi`5=*0KufHI!fbr1P!>OFp6xZ0i9TWKM`Z`PjX^G!Q(iR&z4|I_un9>zZB_vWZ#_D3G!`(E80j=xmHemTDfDfj*PdGyvD^7VZ>@V?&1@84>X4Zm;Bujl)~<1F^y=taIU>Ilti^vWh*x6YG%sc#go|66m&S7wi7f7G|!w?zxcmoGMO{?G35_1YLs>p^z?ntWaHKI((g=byYEvn|h(-@G&LqfTzTt`>xmFEtFM{us|%^Yg3y6!O)#6S>bH^dn!f+DX3g>Mz`%*Inp3N)tch{PDq@|J`SFz0^;ik+1K6m)D77KL0**(S_cl4I^^7Khd+;ul6V3_-qm1AMBTrZ|pXSd^OO9ujAt0-2W}X<jdg$xK8V-6fdVu;rN3mdB3!d;`LJ+$MIFixNm>E&i66*T=o}Ur~JCZ$JxJX#qTwD?{IwX0qUFD=)t}#-`|W;tGNHSe91RfUE=;I9k|aO{m56=p5**qZFwI}p2B%N)^mLJC%j**qS+5j;yxrkCtqn9&-shG@cCNR^FC^mM85pSVUBNmo8uQ5$d_D(uy5Vwa%Gs=Uqg<i^zzwaD@kIslI*0UIL)6zgeg8v`tSb~GRO13`cueIclZDIPa#K5H5?M#3`6iPr~$kSyb<~~cq4cvbUk<_I1Bm)I18KsT@KCw&w(xk&jIV8sbC#A7Mcu>1<!!a0?z<PLX*Ie;ArS<a5Q)(GzB~p90yGU$ARZU7lG%3Goi18Gr`NCZ-SSB*FZObg>C__0k6goycxP1ycwJW-3!hE?}6?I?*ZpS4}$Z-1<=D_p(Wq~a1rzfxCmT~A-E9w4!97U2R#7J1Ls2bfpfu|pu51Ez^kAe!K=Vap)0{l!RgQ}a5^{<ngLD(M?vR+qrl-%9XK336&eek3J!(N0EdD@ppoDZa2PZi90r~Soe7=>j)2C2Bfv4xx!@RZ0yGnx0A2uH23`Pu4Y~#_bT#-j@L~+XE1;XfLUX_?z-ys<z-z&8VF=y|%?ED<Z-W+qg%*Lgfp<WQ!8^b^F$8ai7J|2fv!Qw5Z16g0E_fYS58VXTgO@;8ftP^iLzjZ*gX5v;;CS#W&_wVn;3?23@Dy+`G#nfZo&=o=o&=r%4FyjCkAsGQ$AQN~!@%Rg6QR?<6Ty?A5#Y(-m!UD>m%-Da31FcMz|+C6LSF;F3Z4gD4DM?h_NL*4A$Snf0Xzsi6hp8Fv^!YnK(NrkU=Q#R94o$inZ`)d7-1TLP%p3-VgfM)`$LC-g$@G?^#l8Zhnt3{Y516in`!hnjRB_73F-!RLrf<O!9AhAV4?0{p|0Sb;9jPom`0FkjKUD?jT*d>&l|oEhTyRnqu~i10~Q*fi4Q<6p6H{Grk_4IFDIPSP{a*_x`EvgGYCEDi{tvj7c4%_(2u@|vxjy9cS4Lk=Jr5sP1nd5L$EEhJ-98{7upmr`ZfZ+6gm>zbiUs3MVuGZ8|;l3FHJq3(57A}$Qc9;1P6hgp)TO2`hB2HeHQ;?XJZ<zq1NEm;FqA5;0`#ZCA2lTCAb;%C2%vaJ=6i*9XSU=t-%AqgP}HH8}xUurq6?s(-L_tk=FrrI-<sQ;BKbT59$JS1pDJ>flwE4JH**x2<~bcy`lY}O}U%a#xSTIco^6Z+7;{v9<Iqd9HTet>W$ojJ4(Ff0-(O&Hj?;dg!i;NxM@ENZ2@fs7UyM!<Jy3mekQaz)Cw&6X`$(-h302MC8z~h_+nr61WWiX>a|6UwwT);b+$l!3mnr^`eVKIfOY}*06RnbfStiX(6Qil=v^0RXK)vAAE*o#JspGCj^L)B3mpv|1C}vYAMj{=Z-#Sk3AF%Q;M@eaM}4+X@x3k1#Rcao)Di56V|!?hwFBGWdt214%`18xHmO;2JB$DHU;BT2^i;U^Kl=ZCr1`JG+9PdEh5Y_YaoD7n=-iu|{)q?pN1}S^U(O`~P5'

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
