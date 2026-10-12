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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/6499bf2bcc024d419bd23f4d2eb332ce/part_003.stl', 'relative_path': '6499bf2bcc024d419bd23f4d2eb332ce/part_003.stl', 'source_sha256': '7bdd77684a6e86127d90a29aedd8a08b8cf3d7d925b4f86a9bd7a3083c0e7ac0', 'input_faces': 252, 'input_vertices': 172, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18041756749153137, -0.046718448400497437, -0.4410935640335083], [0.18024277687072754, 0.18463511765003204, -0.3993871212005615]]}
GEOMETRY_BASE85 = 'c$}q~2~-qU7KTefP((mP+_e!AFt{Nu7$YUoDB=R*5;STfLR3T)R5XlOsJP(<f(xKD?n_KOF=LjAv7<JccqAceOpGQSO)_d?%w#dqxJ=jme@yk9nRDjM^f~YRU;o^`b>FR5)vubkSQl461+M_*Zbac-i;tq{!&C87=BH%Not~VM)n(S~g>@7k@%2}&ZX7XYcwAx~WxkRVJT)aNIWxGgDY##1pWrZ4aB4>8+{~m|lQS}>rs)22Ni(xj9Ddfcq}eHs_aWVThliPZgoc?Gnf}L@hoc1b`(~$)JJkB_`rV?TTR+oP@o6l+@_Ipq=$T)|w;Xj9UwhDhr^Kh#h;QzExk}<{ww8&%%IC7Krs_}O=ghN+|FAy%`19hcGeh^t-;4H29_vf*A^yOpl3(rcrTF%tJK;CIS1!J}z2vdRZGpeXuTuPRO~uzfTOqy{bV%~6vtB`+Q?lXPlXl7H;=jSX!loima`bjlk1oi+c_iW!cOw6Vmg1YkLV4T|C68M9wd7I5+rmFJL;7Y74##}|)(HO5@}-h*bRY3mlPmI<`R@?5HHYtY%O>%5j}?+9av1!(m&Lc<3&8nGxq|c6@`Cu<t`O<7I=w6UQ1uS-{IqMeypNxN`eWWe{GDlXT=lXy;@hngU!9zQ{KL<oKXq0k{-=D&uT=+0y#0DU^1DW@lh3V9hF_D0_>U_jztvYk{mWtyUw(Fj{Qdi>sOM%B{EP2cjOWp^*B$<eq$1IFW}KI_Q>Wy;+j|=&&%Duy@0tfc>wK|jMKt>F;kH%k^7K6&CF}XGpG$mt>=yBFT&>c5HL^y0?Rv&$`CKOp{LX(DUrEc_B=PGeh_C#5SA6sDX(f_xeq+SjA0yr)R(w-#XF0C6>Ld7zGo(J#)t`~)D)L(j62-SvoU)03r_L35ujI-+?Uut5Z*{pR@%FZZ#W#g4M11B0@zs@i(l67E7m@#wi{#OE4;9~1-5v4M??}A$SX=SUjfSJnEg!@8&My?daVzAR=`MLp!HI=V{rvtW`cSx0&a1g^was{3)3!z8TjrdTJlcsr&<B_0>*eq5m)VT-GIbmX|9&3k>*<C(x2xAmp4@3T?zoGH_gO2xIj|?<J9$XFdLUzs_{Td*ygL3i>iqG$0?BjxTbnVzl67CM6SM7W%s1~5`uWy;@$K`<5bulnErT*vi4Nb2d7Z6~K6~Al>(=~c4E#t>@$K0W;@dNGQNQg|^!feL<uZ@J`!-`9d*f!}+eb%9ytVm{m~T#ezT`jnio~lm4>7Oz&MlMp`@dBg*N^GNQn~M#I~;VX$KoHq#JHZVd%fWw?vW?)r5?z$x*`0!rJCr?b*TUP71Te(UwqTaW9ZL%1@Uh2i$%|lME`sJf_2+))*|tJ-QiEHC-K$}lXK+nSKf50M;#Ei(72whO`9M-Iz3zBfA&Y6zk6Z6Ew0Uz`j4G)T8EaFkFzBH`d0K)`3m)1tjH8iO+-DTf5&-$*>8^IIpl-+<}|>0dFY!V`La)-pElH^?tG9Ye-E6EdY1X4o`C+-MZ31c{UOyCd8S=T760BxHskfBSwkksajg~{xB45@^OMIo`CPOa^#|a*Tk@V6CECd!{+34Q&$6gtlE0)1$GzSRb>46pDDea4qMwy5vHk-__Lbw_4sfbpxgHiO@o${Rdb^D4%U&>ky#C(OZU^ogWw)>no3@x3WvH`u9cmAPCr26TtnGt!PMJB%P^a~9Yw^wB>`00-)Tw5)!*QQKFeS=RXKnrJABo9PhB|B4gEIfOEXiMYyVG@KnG`rz^6-9Ddmd|j`|Q?E$9>}SzE|7NTHh4(!fE4qR0od~-*Rde>g?A6^E$aTSK=SrQ0K<xSSO3xEEd0~pHsZjyAuAYRQPX&BF_R}Ey{4csDE@sd{Te$O_}vkr@0OKA2UOI^XgIXZ{j|ncH4ybsuK8v@V#bj+G@4rw=cID^QfP%gztaRW~@gk@hp(}HtdKxdv(S69kD@t^W+7nb3qvL_&pNep71`_+uA^!-%Dw0Bz|U-)5h!FwEv{|mLX%%XMW#l<$E_so&$YQ=hgN&Zu(>KEqVDiV?CzGDTR`M{wMH{M4+Dy-WK2fehBK>9gg#Rp>>h5{@VFk4^9{V$$cQY1^m3Dh#&2WevZKXM@jJ7D1CnC$|;E-AA<b8E5x@Kg<>5h_e4E4j}g!Bcg@}x^%pEH7XL42QGZPz95?0x{MTBb&);Ics`rc%spo@a)Zf;GdP;9e9ZGd<5zaUEpXSmatjo2(Zj-p9pJRXfS_FKr^YZ<#9S_8Q??d!m`{)Sv$%m>X-t@t<h;I`o`zfpDg8kUFQSc9+!*fK!3GDxi(~zh6CE0(Pybs~H39}GiaY5>_e)j|Ry{q!zCq+s<>eXQEGjA+G9`4(%*S^9&b};rCnzwDQe183UJYQHgAkV1VvcJ<hVLxn1+z!9<c|4DFx*+jd+MDnj-Ih9)Uhg9R4SfG8XI4m^TFHIHE9c;!&Dvn>o4IWb{G9Kk9&Ky|>bZjZmzK6f>etrXMn5lo!9GlqI@KXfB#$!U4*bYtQm1kO&rPbi0nWGYHK|k6&Y*9(jj+BOc%#lEj}Si|_Z?+PH`#wZc^=6OtTNWA{$n4`S2tYe+R9k;`Tmcn|Iky2fA~s?v7h$J0f;|efI6eEBhRJLh+mK_`#9_RdWb*5efFWlsQ-tv=x636_(?O$jeRy%&BJ_)j!T`^R}VV*O8OVY#&xI$Wuu-hu1<ZnY$}4!=iJ(Unr`h!9^0#B#&u}f_cG!?Np|jY-M0{bt!}ZgKc)vK;ZJ(m;<P^B=J#L!bf-RR>0cuM>!0i}u0u8d2jq$PvQ+Z$c~Dz?4}RmjyPVeN-3IucE{d@juTv!)-)Gw5U-mp%hjC87Zp@iCW>K7{qUfW6;-{o08GhQ(P5o7?|Nf_q=@I|cPaEMq|L>nRCOB#s?HJ=ZbWWfSCnu1HQJ*6ZBM+iRkq43cQ~QwnlY2Ramt(Yaj3yj9x2Coyw<ZTtgUNy9P-<6lD7ibe7r7UY+nqz_9vnJHQlrSas^m!W(;PYvpbjPvAP=FAAP*srq>dqvB#))OKpsn;NS#WaNKT@@NKPWBQfHA<$?4R2<aF{}>R-rn$vM=O<Q(!6Y7uz}xqw<iE+DU?ZXvHD7g9^fx^5&Fl2>u)yv8xsQj4h@$;ISyYALy#ypu!cO6nGJCD}qPAzR4Xs6}L5x01J!cW~%jL0wO-Aa9~BB5xw+Qs<L%$=TElayEH3bsAaM>EzkuIUG9ApiUvrASYADlatAb)C6)Oc@%XRc@#O8I*1%g9!Tv^9!Ty-?M3cKj-YlWN02*HgUOxALDcr-AaVe;B{_iHoa#l^wIR7V*^fhKcgJvZ3|GgfPjx4|Gp0U=&Yn~+vM1Sx+Jx*wZpxu^GiqycGjbbhAh`{>BQ=!VksL<tPS&*tIgH$eL+75<NV2X^lY5eTbLjjGbpZJp^0U+-<Y&n-)RE*EavXImIgUJzI*~k%Jc*h_o<ufNQ^{s>3N@XaLY_&TOP)#2qUMmZ$S+ZskY6He)B>_bUPfI<UPfL)EhOu@ioAlH$D#95>KgJ=a=!BCeK4Ox=jD#En!16ymb`(ynOaQVOx{i{CvPY3q3$H_As^(>c|Wz1yq~<6Y9a3>@1|}e>$-!yn|y#n=Y7-)@;>q|>L&6oav3$3Tt;3@%_c7<FQCpQ>pF+LfV_}H=S=Dhawa*AnoLe3Po^f4CzGG2jv_x#j;F?w<H<v*1Ia_l(bRtAXmVd_1i3FcoZ6WjPJW6SM1G3gff_*WKsHgElXdkYo5<}rbZ$&_Cwo&}sP1H4UCA!wIvhIJrMi(7YCWnOxgNOzht3|<`ea=_$sXiJR3CC9vM;qM*_Z6kp>qprGja=ZD{32ZD{@<EM{-+o2sMnXYZr0|xf6%Z-Kaguy7nf=#n!3o=klNa)%xd4(;MvckJo?wr1N8p@snRTay@ydiHoi0hLchk8xVbl%0B^+G_(B'

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
