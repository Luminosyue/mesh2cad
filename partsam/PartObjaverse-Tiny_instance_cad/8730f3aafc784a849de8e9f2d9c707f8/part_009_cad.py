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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8730f3aafc784a849de8e9f2d9c707f8/part_009.stl', 'relative_path': '8730f3aafc784a849de8e9f2d9c707f8/part_009.stl', 'source_sha256': 'e525760527fa73d1d41c1ee606c96f9ef8d3590c1613a3cfe3305dc7f7f25b5b', 'input_faces': 348, 'input_vertices': 265, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18115097284317017, 0.2891107201576233, -0.2637002468109131], [0.1811923235654831, 0.4196730852127075, 0.16899143159389496]]}
GEOMETRY_BASE85 = 'c$}r02~<|q`o<3+l16F<X^3((4O7ekG%<~nR%Vuw=1}DIGi6jkam4XBV3-DqBWQR)aR4<3KtYA0f|i<K8VF9GUQH_;GDGY-+;6|{!wt9m*ZQw}S!=K7_dUG4d!K#w*=O(l;osMxmW#qa&6T`o_P;#jB}Ea%S#eP&1x8K?9T7PGweYb~c1i>C#ZQ$k?Kkj4|4;3dNy;?Ok%8k!M0$2pJ-Y{W_4HCbgCZg)L=F!h77;lzQ26f-A3Z+M=8q2<J~q(yxpk*5oxN1=SH093>VNrD*VY96Zu=v7HZ^}cSK=qyw0Q7tp<0qB`AT4mGvc#;u~ioRKKmu|^^Dua6!&&U2I+%}!xZnGLcSi}mg4p3qvY$&V}25!&2<fSkyhlBZ>BBddK+HndhJrl*An}1d_@K2x4bly<LA3lyruN+PNCLUCbR#%H@9=;I*L~=1ao`d&!jwhh{F!bKQ)Nk)5${Zw649%*A?~&$43t2{2{lgJw{F&j`#K8JjoTAl*hLj*E=$a;?<lJd+6_0-YB5>g?^M@IklbgTV5_B-&A{0yzZRE*Sj`@<EKw1-|R7#@|Yz%*sonkzTtH;oASk_kgugQ;Qq-jr1mIH;y8c5&$vJH?5JKNe?I5=-iz9!!dKUS!T!n4+|JQWsNc+U!#KZB8s`bV&g~Bvz<!+#-2N`@s6AG_71z6{9<@hn)FiXIucQ}qo;5i+)Sfm?*>Bd8ulJ3jZ4`gF3Fmh^dWzz&g>XN2ewfeW!HM(d`_T9?dRCCH|5A^~;jwFJbY1?pI6ktJ>&-q){cOgRlW*33p2mq~l1}46N!mib5__KN)n@GAe(1fP{aL3@)8`eg8|m-*&tw0c6C6LcoW`N%sdK$sxAOgpzC-<^PW|l=#rM3**V}3(-Cw2oQS!A93V)>j+;fDVql1&!KdQ5T_h%mG8x->OvRXXe9`D^mzu#d!Sbe-{gD<2~e61q(9kO^lTa&g>{OUF2D~THW>3;i2PwM1r!zNNc8|&AkP`>wja{RwqQ@k}QdN2L{_L>6}-z<o)YiR`CU$fzlCe^!S7q!PSa^HT^zJ=tQaVdOX`V6M~Wps)pU+cs9)vgCOP`x_>InSuIoX7PZwbMHLS{}u_tfKxmioc_N*4thrUvD#*=O47+;@^(rFCXLn8PkCBD6WmjH|@TqJbKqR>AtA%UCyO=-yz(dL#foyn(2{S{drej`<(jIvNL5r)f-mI^F!gZJW^MceAB&*eAN=4OYQeF_EG*VZD?F60io0$GuVlIvqwHZkNSty4|-A7Uh?nyQoJ>}oS&m{Bgj`~WOM(&dW^^6`L^V19)Ixja;QGn>$D|@^8ERj^GuI2`M#}U|J}wspFD1t$IsF0<ZIXc_<4VvlTO#0+n9arQ);I%H)1{Mu!3yrhXvy}|7=gnudO;rzH*1-mDoj#_<6`7Ut6}6;w|nSshz4{GUqwCo%_cpjPh8z$B=K99V1_Ly-D%L=x!W;H<I%wbfx=l>k#(chw=R#+~N>j-*eaYP`yhkc%Jb-e}Mdq0`kq!4|trPeU9gu!rkQS0}k{2nXIp*>vCK}zVcH7w{u8a%A+@($bQ~H_Ot$?_8YMgoM(3|`{(cTcy82->s4Ct{W`gb`yu<*Zi=6Gh~uNJ^c<<_k-Mw6)Aj<MN&VyVF8NC34?O;ddC>hbI}gsH_>><w-feNB_-sk`AYXs3h@T5*lg5vcU71OFu0Q1W<L14aDUWAaX7%eeA57qWt9L(x`tw{O^`|+cO+Mwhx`6!~H@M$A*5i3Bd?@*P2Y<?=e_nKu>W_`uMgIOg?*G6MG~cR^M(wQLKYF8Js#lE&B424`(0pz-&i<NyZ?%xGD*-$YHw&hEmGU39lfTBll;Xz3FBPAyIWLf}>{!9$Va(71($S~4QN5RAC|<d;GmYZ=W^bYRXJ=CTwI!Z>z3ubT$$u-6^AGGr{iQ_(r15wU<NG_vjjq=SDcDTynHItQ^Gp;yciQQ%$=7b}rR&mgAC={UHc_5~BRT)#9yA|S`R2G-^0gxGWfWgObp!qWfoB=TJ7&{!XH=d`rTong@VqfMnb&hO;?|Rna^w6tE9re>`K&+rT4^}v*^<lc$UT!x^}Ygs`CPiM*5nHY#UKBY=k2gg$EaSXiRA00*>qh-Ko-?&gtc2sc_y@_Jm&slnm3K>YmzAb=p=qmUHS**vD(Mb_|?N!Qh!<^UFf;iXWdJnJgpD#{qkMN?f0EQzV>GZ&ks{A^gJq#X{#uYV^6+b?^v48&1*^Q|I?Y;qpWbJ=iTyc+6u~3>`v{s+Rdf*m_v^*C%;h=$JaUcC4KJKdl~gpul9Uj))&zAT36R1UoSt){T7+Mk@9>T8c%+4Dfvd14%DA!AJ4^<uXjAhkIdx$QG8>`x8KJ7eDS*zbiJPjEF^#76mDnt1Zt;t<u&s4LSA<nM{ZHPvbH#ebZQfB|KJt8UTKrYzS}!I&(GgT@mltQd88A<`8i$kY$4TK5EDi1?YD;S*PHI->+Z)VllDxf_Nck3)E?y*hfva+yEr~n<vjiKl5^=kF5vgboMd_)t9<=J8sGOZL5HgQTHW1ze<xdup2*``%Jbozbn}V$xA$?qm93tv_dy2tTl6Mw=MKA2zZ%-9PrNtTuZHU~8)roM)zA-SV97kc8v0F5*c{_mLqF?%%h{LjOYGYV{c5<6R>yJV%lBQ~+Ar3xrg38Dx!A9Uaiz4L5bsyRI8-C+)4U>&TfJp}o^PaauK1KJ_p9N#FrqV8_|@<nDY=_hQC{hJ{Esg`k9VdgP#)>IHV4`#l1lS{SrSjaJa1TYHztuU&of%rwUkGim(0ki2E|MBnC5(ie0kopCY(v8znA7otxJDeH_7v=aeW#2@;t1JxJ>K%r{?XbG+HOh^SpKJAX>M|?+g8L0QvI!!s54--t+Q%$2@hEeEB_PxniO9yZl}=6Z83fCA|lg-MM@}rT3;<QcC+j`8}(SeQ`T|mfp)oauNCRd)#uuLhpI`y>GS*<@dj|PB3<b^Y5i~h1qL5t^1x@hYTG``!jjnVm-Bh_ifTTM_s*$_mSh=IsZpiUI#v?<alYlq`X+h`*>-6rEjccUs{hDaUOiWBCX%lmV?Qc*LzBxKtAV4|AyE3v*P(Z`0IPLKbF^xYC<IMo27N8I&UY(|J<JQxb)+G`(yQ<>g}&u4_oKukT0*F)v)jORL@_v-nO*p!TULBJ+GDzAz!mT<na^IgYqkPz9L`V7wC7_aUN+OVSHG?=P2@iWI_|#SIPStt7A9z<$X|})x6)8_D$OUZR|_?EY&lJ_RaEs%^2v!`#)*lryOfR>wS6uXa=W}|I~hSn+N}1+MgN^uaGbAXO-F=xV_T8SiN+K^GW+?#W|R+L*9>TUytW~p1gnGP{i}GwBOgqoZ>vv`GD3piSDO-o}i}oqUTILf6%<<@V-Ghudq~n!|~GjhCb{h`SN*)>U^1f>HNg7v*&fCbl##gokG5RK4VNf#=dl(V?A9?zI^^;ojseL`=`!}wnp=OAe}E+Qc~HM&ZCUVt?WzZSH`Sz@}D~IO25tZO6OzRH}}Yw&(o}Nk2qdBe>0mmrTJJsuhXNO@%~9V-&3cwB40iyG|#@m@zOb=mh}nem(CmY*N3w&ollyNMvyO`XBvCwvoD>08WR_Dd!+MH>o4m#zjVH8p4h>8r1MzyuT1u(^IOBMjPpz9z3QEt1=Yt})%mb>smI~!&u`UvvhM0dzI^^{<PRiYKCiZ(4rX6E_pb8gb8mh26s}h~Ki3<~WM4XOS3cixn8(AD=kxl<hdEw4&)26P<$9&_f9s%1Zm0Bpf%!s{BlKDNenGk4ntb{D2+Kzu$$#Se3;!p+m5EQEVJT{$D5BI+T$G^U)xMGurueDSn!l0>_4$8&CFAYW^?&_JMqEQzaos3_eW9;`eZd`}ZNMGDUeK4oUf`Ee1UG^{4;K0yxDmJk^jUBNaD5cPF3@^l7jR=ShM^6i^}r3mb)nCKg*t-kf*qg=*a2)0wFBFOouJQvg?fOUz;4i2!L4njsjYZI-N0^$@k9~a0ooocv<tWc_zmdm;5Wc;L3@CO_65HM9snH(7Wyf80C*7eAK*dY0B8`nKXfRH;1FmKSm;Es&`IDBa42*NI21e@Iu$$`JO(-qJO(@#IvqR~JRYipg+_tLgCn4m!4cqbwlV`c3pyD*3p@up6Fdhz7e#P1bRIYw{1tQ|Sm@W_ufU6-OTml4u_%J$po!o(aJ;Q7gBs98umMhit^%iklb}n$LYIS+z{$`R;AHT6=t}T<a4IwboC@9qT?5_(PJ^xn3rz<fu$2s3$%3YV(-4yd-3879?}P3E?*p6A{a~R5U=w^CS_l?;3Va+~1U(Hd0-u4Ff`wiLp8;R86)W^N6u~#47r{b*0pA4M*|CbrNw82SupPKI^ciq%up`s~><E6Wus&3nh5iM846d-1>(E=!zreS^ccBl#cft2j1Xn`;1+E1D4!s8!dK>&Z_$rFvbI=RmbKnwa8Mp*|68a<fB=`sD3GjE&@1ZBa--8c9kAQ_91RnzLh30{UW`p;FcSAG5InW&_g1?1kg1-fCg>C^0{RX@hycW6uEc8q8TJU@n!I97fV4)Mhk>HWgK(Nry!6U(6KtBV20k)tB9%3tfpzlLJ1HTXM2OSI+`XN~8yWoD{UeMlPq3?iufxFpCXItrHE8U^pz}>+gLEiy?1pXM>8~icYAF6@<!EZu+!Eb_npdG<J;C4_ia652I=*!@i;AYT9;AY?#p$)(<f?t5v2fqMzg}Q)U!S2w;V0Ul}<?l6F3lzbxpa^b-BDe{(A-D<H8Cn-C)B)@at_`&Z*9O-@5nKoA1QzNB7TOeC2izRm8r&S*7Dcc()DtYU16b%AU~h0w=v!c+1HeKDfqR1ALlOJ|Gyq(+-ueJV@Y^VYKS2>Z3_27nGz2U(6g&((96B0296SO#20Q{B3>^y&29JV{2Mdh=j{=85$AQDZ;mY6Zt#A~<vrz=cKxcu4&H)RZ3l<s;7Wx%f=pwMtSg_DIu+VsL)%qz0Met%2!Rw#~cpZ2nGzGj7yaAd77Mcv+0NxB;58e#k22BNT18;|J0&fTJgr<RoW`Knr0Ph6nq6j{UA~+wK1s1vwoDV*XBKR281PeV57Fq;81}=u40SmnZu38TjqX<5aBKR8gH}Ey^Bj`=AP_YJj1g#AgMQ|+?!S+x`us!&J!YbB1f`wLqAAoNtf3Jsbpa}jair~vAf`5kI0{;vyhu#I3ga3fu2mb;76Iu!W6MP5yJNORxSLjvnuiz`tbKooBv(OUoS@2J`;@{WK-o@en`WMx|e{``Xec~Th<-dIL7^V7OuCV3$&!LKcUq><D+a`B=nlO^ZNrdum10*mz'

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
