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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ed24b6e27921449f935509d9f3da043f/part_006.stl', 'relative_path': 'ed24b6e27921449f935509d9f3da043f/part_006.stl', 'source_sha256': '408b01596797bb4dab1d94634316a94138cb610f235e3701d88b62b20044be30', 'input_faces': 396, 'input_vertices': 266, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.006974485702812672, -0.49999991059303284, -0.0773891881108284], [0.26855623722076416, 0.1639767289161682, 0.1589249074459076]]}
GEOMETRY_BASE85 = 'c$}qL2Y3xx|2`2lSiNnOu}ZAX+9<2W8od)NtF9X>(MiFwf>BqEmMB47QKCd7h)%B6merR}-F5YDt=|3T{C@Aq+>!e{|L6PiJn!?q=bbZW&iS1>a}&_qGh=?ie<ej+yUnQ~MTC&ZA@Yl%L1BaY{1g;kVPME`50RUE`DgH)R_$8`bn*~G#R#9CLE%4z`P5W={DZ6e_$ofZgTe-f1rF>!D6D6Y^cw~C4-eA)@ZNzTL3+AerK(kZmC9fGDkGKu^3O}Jg4%diM5?UI;^P-3Ymp5WN>&TjZZFvu`TjDc@4Q}HM_ymqu#MTbCEwmmez}<qW!jnhCHbOhqbaE--*IpUmG8_EGhXIbTg~n%S^VOEfv%6(OV8D|PVOyzdxyS%Q@T~mI+?cRY8^%#l1SyKSK?+%Rt7%|r}FYtK1cc6M^ib@yzzsnUa^~~9OuZ6TV>jLFm5P4H%A+^_gEs8)2_kKRDQ#}=c)dmFXVET*~xdzj{A%JT=TeHUZpk4AF5LQMdSh-m3yP)7|Nfu8r4VKUDu!Lku!jNao&^5pNjmikCCr+*iQAaJ@JU6_Uvgsj(o&fx!fem?Azm)a2y&prFc5Ns{bpMm+*q>sdgwHP51X7Iz_T_pgh+nf7RLKcYa2`{nS*BL$9SX>AuhYoknq*(29I9q|Zv?-yGAa{2jfh{*Hz(=Fok6??=+}ukXJk)Ar~rNtEyY=QGUx>)a7L&&9V_<objzil*nr-X-6bry7rkuYJ}~yAM>EN%g<`hVt7oG@nEDe)y7nTh&;O!=}W=6rW8^XHos1j^;Q__-z~2?@~@`w<2osI2o909dRARW8Sx1pVAxa5!XG!{&R8OTpzUpp8w$kkMq!bd#L=nJ;=9peL~|+3Gd~g=gkTyUu_%A<NuG!@szKqEy~=Fj<*wIC||MX<ZIg_c>F&;yPmEWpGN&D&fenr_<Bqd#bdx?@@>_8ss4_l-ZUP>n-q$-<M9h_Z|CPcP7=Kr&~uAbXMfxK71WMJG347859IOixZhH$Pf{}Z&dbFqzdh^#)zew9(juy-5&u^US5doz>yz*Fd`kVO{k>^r9h0w2t-|vq(*rxDdz~j=&HaqyA9!&g`4JPjKRbQR<1jKImi#CC*>BYSFg<UbV;RL^8(&w?e!=6U^i&=<S1yom|HHxk*yA>jXP;&?&xBfz@~cbta{1+)<ZCOt@wn|%m(t3>4$Fv>zvQ?T;QqFs7)8FVNEGE)R~MU4^%z;6+O3{>&v9rGur}4?iy3z~|D>1=X8&V3N;j8s9EG}*Zz~fRXZD@nzM*z$9k(Qz%hBTh;r<Fh9F6+qJ;d=TR&kz-KkWefss1kID43^e!VVYTS;3FT+v|#}>AuA8xSWufljI+No@Dm5l&E7=&$x_<F8Q_aBUJ9;Q>$G3F`cM?wU|1~iPxXzaxm{4D}UHm$Lw3yNy9hxDQ95ty7YXpt?gE`|8f7S|L|9r=U)F0`@zpPn0;mMFq)_KO*>qC`_U#mf9H+cV=mu5WInBv%46^CF8<Yq<csNBlFYv2<#?W7&ub)@%eVC{!|O?=u}fUy@Xrk%58WrOG3R%9KBE3|=JBHSQS3UnD&29L;mNA>#<><0ygI#kVGn-0I=y*h8!{n*o?E#7L5h!WJgs}8;-iH0=BeX+<hu0cyZyn6b?MD_<-&RPE$fE8r(YuVqh<XueCzt-%wB_h>-u1?GkiT=x2}7K#*=SdCza6Y<bSdrs{6>duD6aZKHSd_+tc`0ruCru*pv2<|H*n@@fP`?tmi!%B~u(M`-^g|ANkh(LaYiU|C4=fOEmkIeMgB{$i8KNbY_Yt-@2dLuWjc1^&e5Y#F1E<ziPD|<XiVUE#fBm)_q(l@s@qde(DGl8>k%1{%b2xkbLVoL3vV!eCxTw-nlOM*7M0n-+DedsgZ9zS7>u5vTr#r+3%j=`dH3g%F1WtThB{sV1bSF-14<(zG(FVG-`KQZ}u(cE;Zv&@~!7LMcuK{9B1QvX!s(r81;*`w*{?l>YEGXtEXa*Q@YY*-XG83<@}cOq~Tl7tM(CM6JK{d-x|L4Jgjue&G}PC{YmxtW*7B~v#LVA^;~TW3nJfs)bA9<A#5k_I|urZZ(aXwjb@OqjEXox`DfLj_&7b*bNQBYzJ2O;u8-xtz~22j`PTOf#XDmPm1BJ$snUu3Pu>?cjY=_(w~y~T-%TOk`kvx=^clTZS>J;k`>K=ge0Y`Opxz6eOL6GcihS#Pmh;E=oZs?ZrnE1-h3ap8kE>M9#W&vjY-`?;Z+%a+Eh<g>ut@Dg_bb`=^LlFd+aK}#2<=Myquot@$I&C~CtT)rx!!&nXHLTp=|=mOa`5=ZRI_i*|MnQ43;f>k^_PvNQ@h`#?>qAp+E3};0lc3)_2>7Oyzt}N^SNN2Jvr6vTk<;>^<;lU32K+E!|Mc&7yK8;DGpkppQ#+BUVrxQ9pQB(7oRUx!%rMQ@z&P-%j>h7{I)+wvHxf;y{Br&oAdf>_`_z7ru%!pruAHNlixl%mi_4-{ND1Y_EhQ@!{2>)H`Q-b$)%}g-;!TBu$27@ztg(u{N_3DPln&r!S~k;rTL}0$?s4zA0Xe}p7vMGD--vx;XD80^)zcq8V{Op9`dz(&A5LrsMBb?x$(vBQd~|{5vsoy)@%Zg&o=BAjNtDM*Dmn*H2k(WPsN?3{nTDBf&H%G)Gy8<^QpcL!>?O|`q5FnIIUNXZrj-JeuLWMNWIAW_4FO=&++AWO?pM=J;iem`{$Yrr+WME<L?!f_Oh={8$mp1DUVyP^Xxac6h-k}P?7g(!_O@!{vs|j?bk|;i|kKXol4_ia${OIY=)m}3HSSiMX@yB%iLtY+zN_|Smrl?%8UH$AkW8r^q%7^-eIYWKeJmrrT6>Lc~NzfUv-mTM3-g%;W(P_4iQP`D%J2Kp3#0Uu56`ouGVeD{=izieid%AhWa_A3Ht$)R?z+4`zg-02SMa(d%MtiLR4)?`=i~BuQ?}iIUOoc|2lt2rt^&5@P`lQePHPaI<Gon&at1n4bQve4OB0u;m=$?nCgARpT>!D;}-i}m(#xDTseZz&4&MXm&H_%N~0-G&J&N>pRsT!<!f?jj*EX(*+qP_V|(J0Zt{0ge<#1$L4JR@8Etp*W1{GMpemJDasATIFLDhdUmG0F^V93eco#p1#_zpl8_@fU>L$PHCciClJ3n`CR@yJcpB+ZheQtc)kX!6O_2cvS&q;jVGkmQl$M@Yj8s~O5`E5JzvfopQqkd{ya5>e_@Gs8h^L^~I7^+WiuS4Xo2;ENY&*Dw%q}`1#8jfba^;MqFE!&0CbKLl%#XR;KT&4PHeJ}9$6T`n=jn+vqr!ei;j&<?mYqPv5o;Lptbl!Ht7h_6L{KXynSmKs<*|*K0^};#jJiR9>hOgD)edXZ;`i`tV{+IpTPv?`rFav+rGW>`w{M{wb!hsY|!(U#P$8+Gp$W*i6zY2ek33)lp#kZ8BzRGr((v{9E=XsXWnew~w)h7+uzdw%JFWxp*>G^JaWqu3xzsgDdrN!^1@2565zWrD*`{HP0idT;?-cJqRS*jz&*ZUBi^BtGwvOlcM1mcYOJ5u?_w~?>aZl6NqQaLt}(r$c*a)rxjFofbLyw-+L|GM!-{mg$5*R0Lw{-IAJsJ?D|M>lbV{JdY%`9p-=4WV(-G&}p9Q(fZhC|861N+oGu6h(h(N%4PM^cbb>``c0Zzjq%*aV}Jz{oHfu`@LwANaug`*S_p${hs0_iaGm{A32u&q)Pl<ZCn8x^+RUAlavm)75=fD0GD5DmiJwoFLyruNjkEL{31Be^iz#AsT$z)f2!$I<^T0lP30Q@^G`Jo^*X%QaU1*!TJkgK+t8PRe{|dgKY@NL8{?r5Z?G))J|Oi~K<bl#)W^ZMp$~!&fp0_K#<Qi~4n7LL41E;(H25a8<iDUL{{ej(dL#Hx=oe_uUGRPAyU=IBSD~+>J!b)_cLP%I0w0Io1)Xeab29i4bTag2K<Z_t_AdjZ-U>bny%pL4J`H^u?Q;N9$LiRt<3BpiqwTVt*8!<7fX_l-fZhk*4ZROK5s-Qnco+04=!M{9=!MXB@MdT`^nCC#==snqz+0hLK(7TmpdDzd)S2}0`C8{UI<n~cgWz-qUH_}|Qym#~{akQ5LB~oRDLOLiem0M^G9+g~IvcdS-_wK3lbqEft!&8|k<JP&%l-}Jr$EO;uhX$a#{nHlxF&H4-VJE!Ee5YKrQ=L#<9_MIpzIVp>o<7uh>L8S(SFHJK<Yc-*U*wbK;MCW1W4_HSU%Qq1@V>T-U2(JkLdVY#~JV~=v&Bh29Wxgjve5`U?;Q_^^p2^@Coo8=sT$22|(&ofYjFjsULu4J02h{^*fz6p-y|i$DsE>Z!^_(8zA*^@L}lX&|3hhH<;S60ek{_1N2VtDd?Thseshyz}KL!p$+E%sqcZ`LEnRZi8jjiECHlW0B?g%fL;k+4!sh30eB1a0_dgS4bV%W7lC&|FM?hTPK90#y&jNyKlmK<Ike{@AoUIKOX#LLCh3@~!=~dW9qqtvpquOHqazA=n?pzAetB;*9bq~egPY-cB+43z@*|)}!k1ovjzK!wf+KNVmaPvrkq6I}=_cSj(6TO`I($$^nQj60fu3Z_+Z;L%;0Z4pb#4ksodNJLd9r<902$!r&{06g*Jz7uM;V|1uD8MUc7W7Xzy+YIKo<g}{t{dUTE?%JDTcievq8{p!QVrFkNet!%RtZ4@w1MZfYhPj*3hBQtpKS@fr~?zg3bm=of*%ON4>(}%+Q&Ur!crRbQy2}xV1<d7m|Mgw}x(wy8Z&51w9Bn20ROT5ZD-xlKVmTGxd+;ve0GGcV)o&0I5B}WuZNxjWH*=CAchfS(M)r+z+}1xDU7=bRXy_a3pjj+7bmwJqbJudJ^<pK<a4lOz3FnFmNbzDEd1Lkh(D-^%vk$(52A##=MX^130rtn@3W608-}x=Y!6NI7&TCM-3e{fvNDOgQo)X;PucEqGK%38{Q~fp9jo=7XqFGjD^=;M;9GG0za6%9w@gru1T*JuKxh|!|R|!z9)SLbc9z=M^7CCfVw7csE%pC0C=5oUq>JiUNATi7!FUC(O<`SV4BGbM!w;=CcT0>yi9SfVe%wr(eagz(n5afWE6uZa6K<Pc`YMgc-3`O)lmVc2(Kd2rGc;D)j|xb0@dMF)A6k-o^{~WLkvp*<>8e_IxFxwyvjO!QP#I8Lwe<O<i|B%llM99{|r#zDM;rB%E6QWiC9!ePH-;hoY0xT*`YH*dxJ|tdqdX-tI(4BLf3{K44wi#7<vYH9P|w6iQsVPiO@p;sk;MGcN0AJWZVP6-9*~hlX^HfT%?ULsmFuIL61Y7jPWV;G;m*$HvXj^09HlXe37~?Aax0FNs%@NN}|t7BBsU|$c{eCjz0JdTvVj>Z&CE892>qOZM;eC2hI<jANl<NslNdifvyU!04^fZ=7QA5_?J32IHyRPYf>9?N@@YlB+~w*_5yoDdqLL(*M^onSftH&si%Txh_rQ8>UrRaB5nPY+E_EC9t$2K($-$7jdfD$AHm&4+PW&Wv1Ur`5AFut4RQAe`$795j{c_jN?l1uBOMLFU7;lpgl-7k0IWebfUXZn{i}`%;MrgedN%ZA@IdIv(4)a!p(T%i9t|A??gSms+#^GNPj~<Noc5>5&C}%{p{;kieugvOnW&fb@uOTo^GtH@)i>r0wBf&!BU}6*PhdZ2'

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
