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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b3a58da30f464dbba1c53c7f3cbedec9/part_011.stl', 'relative_path': 'b3a58da30f464dbba1c53c7f3cbedec9/part_011.stl', 'source_sha256': '94f7e682e3362f12c3199f2c007bb31e606ec0b5a4dce6945a44095e7d4ca1ef', 'input_faces': 530, 'input_vertices': 336, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.02851197123527527, 0.310838520526886, -0.26158711314201355], [0.06279385089874268, 0.5000118613243103, 0.26158684492111206]]}
GEOMETRY_BASE85 = 'c$}r133v`y+s7w%seP-peblb@SYsRe5`qRrEm0&XVu_v7p{S&#sLD%AQ)(-Xt+mFR5lgKVT0~KgzAeS8)#$6Ow))OF_ivadeAo3|-<Mu@|G)X?e$F#9=RRj<&P4aH>^X`V@>AZJw0YA^!{?wA`HW)5#9?vcUl}rNT&+=KrUV&<w6A~Acfxyh?cO)Ym}pF^GIZFuA#qhgeN~!8HLg;_S0!q6-1xY`qXvzR8#+w+?FWw>H_Y+J#S9)Z%-OCQ64J1SFQi%x-*n&q@h4dALyLMVS~_BO==qgWdv@vcmLA_Y_@?%Kx0{G>Ul6}uGwmnc$d{h#@om@tAzwhgnXy{?W_$<jo7PRqU-|J_rB<bp$5TDN`GNRmg^|a-`DXuO=k(_m{vp0UQ}(CEYdSxvpI_R+w_LxEKOo-@`A+-Bw=bR0+lOm?sJE-uk^TQLmp(4nxACo{T<P9?^IWp_BTsh~zj7mKXZ<+czWwc4y+5vR;amQ*#{=>Y-jU<&7p3>dc%!A{XIr6t-}C{x9oILq<4+rKJRm=zf<8ZfUmo3#HKp7ttxX$W(OSRhs#LFE+|+*3yf%8<-cVk&QMmT~Zx30N>h*K>l6EpiEYjN-DvAH5_`V$r?zB+bd8=#RXi!4@t(!NdKEXHEY~H9p|4KdCpVGZ9>HId$_NRJ$qm1~GX0!czdwE0co4wjx)Y|65v{bKux9Mfw?vR41Uf;$y2Nq1#?Hmi0_M3N<eq6aK-RqmlXTH(8K5kopf99<Aecw#nrrW>YLiYdDf-+vdnj`Jt8@cYt{v4~Z*XvuWGsQ0%vRAiLUHZX%cCv2YXrH;GrPpsXRs2`)?a+08GeX**H$tD!$YHZ||C*iqOMdVy>EAoax*yG{k>U@G*S<Mk`pfz{M)v1KXI(!@8DAbv_4vj~@y&Bz9&PFMFU3hc>`su+2gizEe4_N@kp$h3u5aO+hZ6RC^UaKTvOi6B>bkN*$4Y+gfx3SqtNy0@_o4q&2dS%i#Wp?3H!2s~q_>Apko{S(Qs#}?VaL3_eJ-2iZ}?32uf2SVv~#VL^l!dZd!^r|OMbPNb$?mY6Lnp=zFA#-|D;4+SN8pxlK)p3-A+>9^}2r_`nA_;-+rd!&Vc;;IpsWD*{$o!u0B`%{p+Nio?Uio|JDWh-p{}LQh%=<o9^|EBjVesu`(~=TURE@{I-0T%)>SEt=7N)Xu0%b)FGK4`WMo^QDv+6J?`uJvEC{s{<K|EZ;h#+vgO5JT2Y^8BW8uv559$;G;D>gAG=E>$zL^5#_#S92U0!0dFvfrC&umc{a)X8{hR5!e(X&(CBIWG>BpBdWt?8FEBQ-X%J|(EoD$$iCCRwhb8?l}H*V~Zd2d;^#X2uvLur51csUOdV|2Y`^&>ls(e-9D50&HHbwI|;66=`PHxo|D_}!AI``w6bA^wipx_**I<hD~izU}%kxovO0b-j-4f8srve^#`Xc9L63-9A+~CBQFxTI%QIGF?B`^pSGBA61lk=xd~VeH-8EW2CqA_*TC?;=dCib#-~X<Zp<P>)P<+a=pVhKNdeS=J;`MzR~k9xqh7)BiFkx;w9g|K>V}ea=pX1@%?AQk9+g&diC^q_U$V!*YR$3KhnQHl`8$X_E%lchSfm(=J|6{CyQ$=*8Y|z+P9wnM*268)U#2jwf5~Mxpe!H)8ceJyS^DJzHdsLu4lt+FW);iLD#b#KUdeY>sx<s)ODLQGdRub8^$K>+cSdGbh}C6^1WxfOaCT3w_W?`FUa@C4v>1DF;LgDX}l=;v+qd%TIY0KSqq1Vzu>COd*eSo=Jl-~KalI-l194TT;KQ!e^DblpdBkw>U{RjO{q`t&B;4AdGpOV2jx8f@%O5L@6CNt+WES^9$%InE&hXndjI{~U)FW|&|mno9Pi4EonGI*{etwDU3t5%w`{&OI*<9#E-^ga>pz?iiw~E&#ka;zk@{b|Tk1R{dd(BZ1^#2>0zd1xu!f9S^Q3X%`dP<?>t`Jo_JMJdf8;H>U)>re;|t%$_a}!P_vYKZ8%TX#Evefvzxq(xc_l;Ys!FNVsvR@OTF%2y+PC9+>v3V$|5(~NbWi&C#(bIQmu!>#i<xr2`g|{$=kbk8;v3a^$$i4X9rC>;67{&S25#2l!u9R#dv*Q$E7eZ(`sSzN`zqAd<HGu7kF?(>TE=x|D?Ki(im8&{W31HAk4yBpuzMbm_Q%Wh)Ys{OTxW}YB|g_#f0VIHpU<`#(th+Wa^5~XsK<-z+x55VaS?f^m+j3r8;GBDyO-_FH_prcB;`v?321+4jMQzRwz_VO375pro-E^H$@iO{<ooA+FV`1*cN`gE<yL!rJN{>B|E1oGrN7N}di(5E@vm2teqYvB`}XDE<a<M+7khnwNyD!{e_8t7{Jo3z%{OjI|8DQB``z_zeE*ity5C*jI`N+F_oO1J2LkdZ?3eycYnJBq&57chsm-L{tM$;nv1_y(@9W{x?|pko``jn{K3}K%-HPuk`Q7qM-Ts_!m-cTAmiD`TFZ002C>huIMmYY6sB~}sWAgz1WAlLPPoFCJHTDGfkIfHme%ATH-OsG^gX>pMkn=ykV?e%*?@#C$ke_uvd6@r8BdPP8Wo4e}G(6zE8NcR}aWQ3-_?+jY6YEj}eEP)~A1?FohB)yz-<SKJpp!C=@a-`><o>z;AlsX7juk(t?;sgRd8bJ`r$3dtt(YnIU0HmiROTjczFW`!($Tv9jnLNu>fd*<nv9oP|61=IN0Bd<)8oSR-Erj3hsMC`+BZ-AEa$&y#8IzryMEyaxgT)z-)G*Nwe3Jaerk%;e~Y?l0qxuPP3xw4+i{P}x+de%Sa3`BpLxc}ohbLW`0o7X8*J?I`tJN=2e*}R6#l2=Gf$e`9>{ezImZU=cbE1fe_4{^_1$^c_`Q|xck7!xl3#U;^lwIl?e)!S;wPPrko$@P`K6tg?n<4+r^)@vsN&Mj&5d%rL$AvHMixJ^&sDkKSXoN@?)A%^_v|mq$@g--^OY$j_m@|~#Lsd)b^WZ@(}#YR>#5bU=Y}VaU;M|$FaBfWadaQ?v(7X4kIggqS?3coeYJe=m22`mI5}Fk<NAhQ{G>_I0r~bf@;qp_O9{w#pA+r2De}EV`hToHxA;w6&&HkvxsKyoPbbTL?A8KlUf(E*pIji#+m7+K-0zvmFQ<5Y_kPd%N5)RC@80i4?y0Qn)@~gs{<<9J<ow3!@#y;Idhw0su}8i6?tQ75+gR<*cjp0rX8pwhKJ$h@JL_7jV&r?>`|Y{s<as>XSn)^7{kd=Uz?1;ry`NwBoLu*ZOp*4_t&sceG4*Y)Z=A=EtuOQ8;_1@P#4EDC*LaN{FXr7j;`d)7`x&uakC&`|WXJ7t{}8c2&I8Xu_S713pYZx(`Cguz?B&18`a;f7y*_6~y&dpe=K40i`&{<W-xc^=W*+Li@k!&w^|Ou_*MDrhREpU6#PNdv*m!aMzKoY85dry+J<sNxF8jmtvj6jC@|@mqrnJNJwVAVUir06a$Nh`$$@)Xo9NEu3lVyD)C|u@$d^3KjtYb7dzu)WI_`Z7Q_4<anG+x^It-RE;FH!Eh@GbnLa*0R1`486_b|mWhG!D-fpY;&qKyZrJch^0vZP^wF_&fJWJ=B%@H}5Tyc35w*qcipTgX_END!#)fWgV&aa%rdJEV(W;&2D>r3qPrGc3tP@+?CRP>HShaU8c%);o4eh$GzXU8!gv`EWU9)TCNN2WnI}_zcNGb%X;<1?bL~^cbWYTNuBTfUcPti4{{$kJ4WV1d?OD3^_X;TzR_xet{?yTeF6D4zI|?=<WFuQ_bII7`NO+NU9E4fee;2=6Z(3t*XxaDMk~o@ozP#gqwdFtzI%PYuv^!gnWw$@Ya(^M`Ck27?yK>QCR60Ty3nHiUf**4{EPN`+c8-GOe(xeuUndpJ4^oh4l>`)K5^9R8ymzoXPuBb#CO+MBR790brKUUe$GMiJas!E)$5zN#J8^}=yg=<A1{c{`fyT@ow5#zZ>@b>`f()dkVksU{tSOl_VZ#JsUO#8y*lYog4Ac#LDEjm)-rxiKeg#ee&pe&<n!@TUk}&SFC<G{?HVD!XC2<(cb2RxPI*=Gxqr68GWELsL!b40-^6>e&VOOHeDA=bx_*o!v(vr4ajKKdS7~bkd@CpK7t(9UdjvQCBi=6*3EAt-ci(G7CdX~_=DY7TA~PmRT{W36?Z>v0d2ICtsVmpt^`g{IVw?S5-#pb=*28b*(EV#2T_*c;yP(u<`PCbr<ok=QmU+STzj{gXlbL^hUm^9w`>CW!L-hH7=)3Qyei|X~JF2ac{p9_ZQLU+rch~3rm%XHotP_^CKGAusS4Y;)d&29x>)1xkyz<->He37xD+AusxxP_wW#D_dSLcZzIw9cwpzB-s?)yR4cb_}VnCKJUeD}G-jEa`)Y`%A;{XKO9-ebDHjqkq4bbagUX7SH-4ahgY-5mISv)<v&+7G)X$Mxp`y+5vRyZ-$FvaUPinB=#eDaRXiRgM?m#&_=Xk9+g2W}nD$)r}3vH=5(ujt$5+#+Q)!=Yu~3@-2M-`+rLQfivR&v__6=X-9c~jc?w;f48HIue;~O@7zM>^U?VwAKwTQKWS8c$!}eBi_Ra^TdoViWdeNT(tLRjJ}xx9W%q!;9yt4ZkqLcDIZswj<TZ*JQG-2yI-pGT<LZ<Dbl{cx|EoV8Xb@88|NEx{XPtfc#fkhu5{f&cW{|K7#jVk1u+oOG(vI*t=d&lBIEMZNAA|o*C~h1ip*Ymh7D1w!Y%4#L+>>x7obJSj=o<7StaKf`27c9vmz*f<L;)vyp-(xH4b6iVfD4eHhfti8Q2achxDEOe+y)+uz6uY9XQAuhS#TnH3{Hf1qW^|>!k1BX9xt=4_)kZlM%$yxZ_haoh1<hzgC6xkTS9RcRGs%OY%6{$NJ8<K^h-MYCH#S>pFSWIkK>#-ryqL36VY+-IPxbFil?A!;5D4bDV{!_LMZNo7J%Kp?}JW+b2#A~j?t1(>_ZLM2Uj4}PYX0VoX`0{S0^evQNW2RPJ|JPyP=igZg4o-6|V2JmD`DMCr&tV%84J*pWz?j=1zXAAkqJ@t^EHGiqD{@;4|<?gyIe833vniu@lMYA@l@%2)>T~2w#VDIs4MdiD#T>gyw>ks+>k>bNo(d8?-s>9%mb(73Z}T$L*eH#RWM3iqCN#&cNs3)#yiXFm;fhQ2Zj=5>`3^ei5FGu7+3B=43+gG;{;Jf%7<xP&~tPu4kZc!ZY9j=qvC5xF{M9hf_aA3B`rbU^tlLEQG!Y7lQktli|tiYd>@bJcIq{hZcoPI_JNG6Ms28-HEAA^mn2NT98oO7o7_Cg(ne;S2=MSU5ieIr}7<Z3B~K3_y_trIvsu;ei`i#zYMqa>}y*>aScLoE<$l$v>==v&4(6*^TEB*zHncTvp1hr+5(*fw}8i^tKji)lII*H5sJTZq8)QfOG5EoLo^?(ROQ~~GpFIZ@E7P>crEAj3qtX6&v`$N?t+iQx6yCl+i;U0(Z67&s(zXfikqVC;C38OQ&jD1Q??b~VgJ8?zhFP^pts@Me5c~~o!I8Y8-(IT=%?@^crm&iUJSp3E`{HLXA+7n^j+A3UqhF`ufYq^t?)wlZS)iPZ8(8YywM38O+!C{)8NDCR`@Xd8M*}i4Bmmh3-5qa(53KF&P58L_z3zbd;~s<ZiA1)pQG=?pTp`t{-5Yd^nG|G9FM*M$HOs%;wW?x90kXsi{V&!6#5Q43LcHlgh#`XgyKP{1rLG;qOZXN;gRS<cqAN$z75C0W6=b7EIfu#ya3$@FMu~0k7{KTp?JR&|3be-ZTMUGJ2Vac4*mf>4F3RMK|h19z<zWG?1!(SDX`Kb@KyLGdKA71-$Fl!Z^1XvRQLvb$#_&-mk7ldo%kBvhyD}Z2d_X^!Ykl;XgoX*jz(kPXt)!hxEmS;cY`~kv2aJYD>@493U@|F!=2$UG!hPjTN8>~p@ZO7u!#<YO}Gm>67B-OfX2Zuz&+8ia8Eb_9Ro+e-3i6R(FO2u_$_o3{1&_!-4Abu4;YVX{Q#l(dna-PiT=&@zu>>&2k5u(12|id=y$LR#ktWRU=@n9qgP-RiVf5ct56(-UWJw3gjFcci{64&C=Nz%z$z5yK`+576#s^I5&jLnXFM7k_Xx$mI*~I-^cve=!`I-0=sx%$yainWZ-M8d^WgdL2s9cV0rx;V!9C!{gyM#1H@G1jigtuU;Ra||xB(o3c7{XXnrIkY6Rv}{hU>u93B}dWR&X`ADr&-2;d*EnxE|aTeF1I?H$!{E&EO_z1l$B}gm#A;!L<m*?a|?Idw3}N7CaQ5gKmcBz{}AC@N#$$`aQe{&M+R0)eN>3-*>baS{hY;X+m)cRE_5nY%4B|K7dsyE`_S`T#8WaLvzDE_*pbN{487+HQ=&vIW!0kV%(M^6hDUs!_UDL&^&MjxIC)HZF#m87eVjADijw)e}xM&mJ0<v8ry{k#bul*j{aeY=7j$s{{pJU{{=$vUi2Wm7k&@j0>1~(Md!nF;bG_qco^IP?E!ayYom?f+HhGy@v~?{_*u9j8VXm0E29nI%5Zr!1TGJkMr*>Q;o@i=xH$YYS{;5GE=edZfmVY{z{Sw2a51<PS`RJ-KZiDjpM$HQ&EP6<CA0}#34R7`1V00pL2JQf;BtiGx@dd2F5C_s3b%uYpmX3M@N9HBJR4qy?tz!VyU`4IH+&ww51)sBHy+J3zq75ls1r5NnrJb&CR__G4cCIJq9x#}a7DB*ToJC0mV&FpwNW2j8*YF;3pap6(6Vp{To)||mt)?kODL{~R)Fil_0jTheYg%<1g--=j~0ZVhby6l;7V{cC%T6PWh<8bfBGk#kAAEm^?&a_@XY$jz}Gq6PquK{diZjudst4j4rF9={!=%qr&X03{{<q8zTp'

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
