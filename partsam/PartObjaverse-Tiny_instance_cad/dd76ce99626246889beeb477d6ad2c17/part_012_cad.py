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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/dd76ce99626246889beeb477d6ad2c17/part_012.stl', 'relative_path': 'dd76ce99626246889beeb477d6ad2c17/part_012.stl', 'source_sha256': '790f9d3e8f04667d780212069e9500d6e134099b22aa37abfa3f89d872a707a3', 'input_faces': 412, 'input_vertices': 296, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.02952529676258564, -0.11810751259326935, -0.22229556739330292], [0.09908286482095718, -0.006100565195083618, -0.1596822738647461]]}
GEOMETRY_BASE85 = 'c$}r133Lwk*T*Ne5`vJ}5;93htU;)TTE<$0NNpvkCq!zikl11!TkN}7f|wveE0(I-8L}c(q}1L=w6@Y(QmR7!^Sk#u?L6;!-*evczRtP5-~0L9`OR<cZ<*(LavB<3w3wU3|GcH;31tQ<o{}W2jN~Rw92Px(#L!_e0b|C-I!Wb;i+`qH9nz<JXn!YZqBPY%Vpz=3X#W<nf6K@q|N63jWK{I{=<qRvqoN~*3EnAubj&b=#|#f2JIsh{2R3h3Uv5&TzC2z2KmKzzh9KYlIPsJi(!*{?g|~(2S;A}a=^KTYTvrg6%F5Z4cXJtWb#DOY7m1*JsY7ede{k|UYF|>4^5vA}3B<>zED_%Bk$0Z13!2SbTD*+zck3x}d#Sq{==z+4N2vX!ME$FW!!|gK^YqMYE0=DKm`B(5mU75P{<xmneaajXUN5_z`jK0&BrauqzLNS|`~}@t37<$@yYE8xwdbD6q`bKUnD4qsTpjm_xaJ<h{itq>ss9q*)Q|qenYesYqj4%hy||v`o~@(n{|G+Bb?Ct3Ny;OxWK=m!*9Tvr{%wI*h-+^uJB&x|b99~cxoo3*QXOoQw-A?_j;80bz4M^)$Q$Pp*N-peIvgm&_q`j!{r{1`{o7AuTe;-zN#l_cbNRmUe$2}ppF{n$X~WMu`rcZ)?#>VNys}3QuZJ(@5tlkmRVnX<AI*!+V-Rum)KMCbwtqX_SO1|YalOtiy06mXJaH-Ic|7@XL%D9#t5g4axg_Sh{MJx^Lu&H6>NASCz0*t@k9~bh>c@V65a&xz7gAo#q;tH^f1>N9d%v#W=Z+<Adml$!zg~gI`F1JS&7&;ywV6~meR3Svf5za|Jl`EDU%gX;xYoy$xNX8Eey;d<u5*Lyt9YH>r+h^j&g=Q^KH}1#_uQXrB8^A(uFibXEE>N$J^w7VcPPTV;cj|9+f#+-#p4vM1Ic!1D*4ze)Q^<9pSk}&dR|*z0rexF3nH%7`HT1atA?m^QQ~^l>c{AQd8s_VNq_S7-wfjX=I3dh*aIJO9k<V-`>Op?XgpGA6mc!;4Da6&zWlt=y@|^MVtKze+r<48Tv|@C>s6|Q+_oXl%Y{b7wcUl3ue=_UZRJwl9IAtI=QicrpSg2>^SM-iThFhlfBDAdrM&;0sUPz^k-df!mnNO2d6Aa=mFd9sMCxCAwBfu1A8(&R{jD9y>+0(QI`5>5xv}(|=6;+$fVgtahxdE=9@$oI&aaj*mF7j;q7YYeB56Fb`xvUft>m-C)_tw@dQ9A2_sU}H{3-+Hb3g6gFXHvTpZ24@@G`HH=aZO!rcs@>4Lxa}DsF?Aml(m%J8c?0ml`sP#wYcxxq!wIFrM;_1+>6AUy|1uy06-9FLSAMymg-{Vb|sp|NQ&qyst*`eYb37{;*&&@rC>7zIwfnnAa}k^}aHL*VUo(apW6)JCl6%FyiWhy3F(MlDFkP<ouBD=aRpZOz$20*?T;mHS3uBKI8Kw>LT4&Y46IsIM+e(@Zj-WNTzd8@=4--oNMELo-bnl{t4Adjw(fUkiuFp&*O7OZeES+Q*Xm;e%@L%PVK15<J>)N7WsX}Xq@Ws*^WGNFJCt}fcu$#k>*tzh;yS~KS!<w(mK@7bmH@*_Dil;r#P->ekER?b+%8p*1<dv<pV*?1D?@)R=U)f^0m!6pD$0J(S6kve_n5Si<swM;C;3ri0f0~HjP8N%lp(``Y`3|ac?FOKi-+fWy86rZ1!Ou+l<a374HQ-XZ!@>r?4L@EaQG$+f1-Nm+X|r^VPQ$^Wb<sx0)R1_sidzF<k#NTJPH69nAAWqRGE0%jcHMPCl=4u8t+X;vLmTJ5~9d1IP2)+TZ8#XQV|EKceva$LBfEOa3Gquj4(uevXahehODNCZ3VX?+w+L`#E3GuZ`eq%Q*5wx&4Xb^M?K^CDY3FqVfD5$2q1>>u96=mBabm!+EF<_Y9}}{w*lqJZIGF^NCA`w^AL{t!=puK1oA~SIVMwtMqQp>*Pk-NWqnk%jta~4gZDD&)eZqf~!$6)W3ONsd{P*_0wR`YHNLzVp$W2-=9zGT`O{c`N`nP#0xgld7!kGxDFo6Vrl&5dkXIby-UL>G@jt6%<<kax!l&<;q#<^DuKAPX(YdQerv(!^OXwIh)47}PBGqtCYP5r=g$M?c|P>jbe@-5yv}#*<@apyqBDuNZcF{xB3f}Baz9XsZ_VcUUHSt*Z}P!e#9wZv&qtci2wvy8eP<J2u!hfpLyP#F8I{63eL0=GO2IA8pY1i*`dnHu4}RX<Wajf$Q2)x|DLlWOUFQ*x$)L}Dwi^$aZ&=6tWeA@SIOp}2+v5bcAL!1XCm(a&l<fHnXx@+4q32cBz00(6DRL8kp273l_Z2J^+%{R_&)W;H^Lx#u&2sCyvK>0W>$aiuO6sTHL(11?rSs?We%*=NlK1oHla1RQxOP4Kh;?7+nPJ4$cCOq{+kX6>eKa+J@{iwe$k%q2+ep02o}<=%WLIp&<uP-PSoe|gd9%&d@vAGh@O_v3#Qfv5Bi4Ok^9|7Gx$-~e?^Ut<Ia6QxG4mgjPB^T?F71e`ZB*j+Kl$^UDs>^QS88>_y8dmqhZ0w^f2Db`2l3}Oea%Sj|5k-f#7jBxx{98sS?AH7!1a{sEFo_1HHG(u`FZT#Y3_gOjAPdQrIfnL;~BmBsKb7F<dwwh>Ir>+vc=Tqb2w)`^YAWI2YKa08jr2hkgdck&EfA2_`a#sxk+5cemCo^+;6ju#)I#V^4K^0Irha{;!<cs`aY_;pE&EldpL6YrH<Q)@0h^*<-k4Or`5+0*F3xNeX%~3_Om(v2A>1AIYoIN$(xxk=ks5hdyf0@%^|MGw&CxOKhNNKym6WHZ7!6rne!+;V4k>cxwSr0w{pqESKZ|A*HN=Lzi1`q=>_~g$|>N_`A0pOCwAud^`3XU-a=XvxBDh=-Aa_^^}NGp2j#nu-Aw(|AH(CH(~7tf-14M#ed^D<GOtkMq;-ATFAO7Y>v+duecJP5x&M<->HLu!7st6epSboa?u2#S%8}m@xBFE&VO@vz;lDC(zlGQBhy49Q@%2cd`xf`*bIDwveqD)6GgA3|fqkuyizY7bX?@JPZj};iI6p0D3(Zr{zq!sQ61e}t5BU7SxuM+KLtI^za@1kJgG;R<Hd^Ob`}8<*d;f)8fAjPI^njg|-!&@HI=@=mU-nV|K|7NuZ^F;ad;iY-v<q<+-#7Idg~X+4?TOnD4B-9sS@r$I13U3^ZK=TPwrLP^FDH%ij~wBBadRm1MN4@6XI}F--DWe79?Iv*t~>m`IF`EKI=_mo2G_Gy2J>^f_;;5n8T@(a(tYN|@Hsqk8s{td%qRUwT)!U0pFj6FeM9`O-SnQaZ~u#*cX9>d>OpNQ@e-GLT{Wu8e10L-LBABn>!)K+?&oS>%GcL*<Nm)L%)Iz6&APAkap~V!>#4U*;rxgy2dMv~9ovZC{gBT$-GjK)rq6bYE2lC~>&iT-7uDZ9AM}TxGjF_;&L#C>Y0l4#<^HR*rGDf@AD)-wG|pf4n9t8QsXQLHOU$Rw;@`<uMRGrJF5ePQuDOGr%RDDdzOWVl4u|g-+THTZ-(2T>?7M$>{kQ9^>rf7@L0om2M|CjID?M=n=dX57ru-_K`Mu^chx4!GQ~wJ3u@8?Uu6);ke?PhMO$K>+DfiQ34F3*!yeo03StjSVj36#u?@wG?d6x4FUK7`!pC)eGp38iZ$1ciix|`3j0XLYh{fW4Y-$hNX?rTTuMDkqC&lOzAyw@%M{q5`5)W15e;z8o){OP{7`MK%T9uh!Y8hDH9BYDN}`5zv{`A^GGzM?;;e06*~&hP8Fldca4$#UQ?r*hr)*XQ&3Vn^nATexlw%JJ`w34NJQ^!|$OduJKXSE`NgTde7BUeElwNR9Y{dDbi93V!#~8mAD~Z5#K|^^4DDTDkh*?H<ZE-y<FNbABV|{WPy7TR3nvJYz3kKb_wf*DmuoQ+s?({o`D<g*|58a!4w#Ki*&Rm-*cP_KG~e!EsbK<)h-?39i}q^6x^gz4-Ins*=Q|nS}?b4$F3>Te*78H-&h8uPlfBwU24u)fWqRzYMC%{mcA2su~rTY2`|V4pbkTJk)_pUj|Zr?45V;d*{3#^X_+Oy{SX4@VVEbDUat#L+VHW{VtCu{v*!+eawDd{~P!mcHYMMQ)klr>gMO<#B}C!2T<MAfs=6VJ>!1Lxl{j2vUjEfPfetJxyhIOUVHZn{fy!D);WOp%cx?9h*$LHb?dc>>M8q{W?r-t@5jkwncr|_ULu|6WmV-&E0^BXraIU!=J7Z`bSJJquFrKISUc0orDJ=j4$7D3vaDRG6++LYn%{%!t>^qu7p~9!9G(~b2=lFZw9ZxYcf#B><`o0!dG(y}y#7n)@%Uek<mdG{&-=Q@6VCVX;(hUZwM+;8Rg^<L)yA)wUru*CH%#7hGoKsl_VD_ASitx74d%MFdd%lrS=Ymqf8j9IK`wbF%gXg_%^d2WxhkCBasoY<9qUTZ?nGSuq%p03`-IPU9S$1K{q)Y^dAwSe&ri1~?&nrp9)GWmd=8I|W}a8b^N7DksLvO2|Nd3E&If~ees`{59#)tC-tluoKIe<AVIG>w=a@Q=?_2GA?mu`4J(oQ(IMd42h~!l3{!(5)VD7h+>LWdxlV#=7{OfzI`%7_t!TB!Hv`&;M6S+Q<3pxK{Q#zM)rzc$JQN4~3FPX)4#^=d@`07p$=b<)Z5OH-{AdhE8bq6lFl;6vBFuoUrI{fu9I$-bOixrI#7*<MhlOn?{e|i*<h6n%O|LJi=)Bn|<9-B4}{Qv&xvAHpZ&W4F+3NWlWw6HFQwL^O-V&Ol9?gHHvTKJB*rVDgOa0T{>VIP5gVqqfg4&5C&!uK((19X4HW?Ki`zdz!xh|M;U8w?Y=FZ}1weW8cIh8Y$CHViBRIua)I7wD%yaz8~~`lD8#Ar6HWyrf~34XbKcF=)YDpam<ASZHTx!74%vRvoc3yo@$K=!(!4k=q#D4_f%PFrk~k{E*)SzBcOC1hs4n9gMgM=HVmg+NftY<aEO|Lbu1g1?z=a=rF|HV2yE27~;NY7jZwB(1T!MmbnW<egxVC8;I-0bs>iJ02_>WAXqPG!CHg$fEH~ZLx({7BNkQ{&*Kkm^7gp4F6wX2gNVK0{h`|<7CGU#j~HW5+)u<d#HJ2Gu8clhU_y)aR7c{y901)3aS*i0dK)&tu!)AvG;Fjaeyd_F*hXl<W*N2?dL`Oau$9o85Q|(5@if>b@TrE)28%^J4NQX`3ohC>V+`VcUm7;fuxOaj(+!(}*wn($lX&k9m3W_4GtAepT834Cu7+6X7Vxd0y%86M_ePr;i#|$$3+4$eSUJQ(yFm+99$GM0!zzK5MqD1u(~>LVW-y_f!h~)F?+QH}ehhM~tO0l<<TrpX11+qcVN;OT0J;Hk>cN+Vt_NKox<2yjgI6)EA>u0VBAx_23Hid0H*6K!$Abx5jhxkpSHVQi8gLQsfnNi?7j1iBg71T^H|zk|dN8455U+=xVAux46W}-C+6`cnE%8B^&<U^&$eE1%7VsZJw}7q%UlY0(w1@QX8ubA4f%brQhpz$c4*daq73dG3o!}*C3G-D1yeycA#eA0lD+4BCv2IF(xq<~^{%T-6fzUO;tALG190MJQXAi`6F&0)6-UoGyL3{|cPCy?qn8R-ji<fx*g<lOl1@T<4c(A$9>tONdW4U1q!Gxa=Js;Nyoe2LeY#pxs4sC)RF>D*yHgKVLBNpvD5DUEp@p0G=@S|uuj%QB*O8^&o0mdrEz7(<0i=YKtf>`Kf(1NWnY%$nkaG~Q6ufV<HpyxmfHW{(dBPBj}#F^6!TCfp_g&qYhSW9TZq7Vz+3OWk?w}Nf~EtoiKJ(1T6aZ8vd`gJiDcu~Vj!;APYiM8;rrGMLABNqI=VTEXW4K4f&c+vjQ5}R81yYM3CCiG44C&)9k@K52d8g>o(CStQK4|W$h*U<h0xQKs)zi3!4{59m5ZMR_8kYncMz=S?$*h$1f>(D3B{(~h)_*3wLpNE<3F!Drv0<qBF8+ID{JmOPe$Dohl8dHn5{jfB{z5+`F`wDtHEW@xAune%vhFw9NhByNzcouXPt`+P$;w<R1(87O>JQ44LWq}LJHf$$yvn}i=!!p5t0?P(V#x>c{$>3Yz)1kLQCmEIsufv~#PKQo{zJyrV1>~Fo7x9nKX0C|uK?{Ead6z6&_+0o$60fft$bV#MGuNJAzrhzk3llG+mtaB*_JQHcIB{HnSORm0mY|)Xozai*r3`y-=y!<U!@Hx+%oFV*ej{;?&~Av`p-bU9Z^Xi6!%9MXBNo@VfqQ_Lffunqv_JCAHg~l9qD@#W!~CFq5zC1Ez$zK$V_0QqUua)Te?GWY_-Yni32`-?jitd{EL<=zTvN@Wg|7i$-mr4er4gHL<)DQx2Jd9pD~WY^#Ach|#o&v>KQJs`V*NK_vrTYu{oiO8x(H%nzZ>>5^jpLa5DPAH-&)#5`~q6|KXA=kix&Plyg0|7Lcc(4wh8_W*F1-Qj`jE)?eDPWo<Y9@e+hev{qYz%BG(Qr*lol@|AJWPJK(qRoOZBZ5#K=_eg?}&Y_|W7YwXbCe&tbHC(K(R>Qw|<JbzitrI?=zP8=79uYtCj(1KNg_k^x#iOZso>Sz<JDzsn~5ew}KEm#S}6|oOp!Tyvu7WxhJpQx9J|3nQRL%#=qj9eLgxnloS1@i+74R$KxR`h@RUlIQOr#gxMTK~s{|9Yk4&xqD5XBd6`^P^&DaB=b3+xTE!guV<f6yNTo{{ZoUuyg'

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
