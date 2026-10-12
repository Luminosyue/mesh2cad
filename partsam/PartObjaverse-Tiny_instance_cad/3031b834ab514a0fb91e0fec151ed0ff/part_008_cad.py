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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3031b834ab514a0fb91e0fec151ed0ff/part_008.stl', 'relative_path': '3031b834ab514a0fb91e0fec151ed0ff/part_008.stl', 'source_sha256': 'b2825314a6e52091798476e357d2d18ef52834cbea0cb26664c6c4b8f5350872', 'input_faces': 392, 'input_vertices': 245, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.14577169716358185, -0.17867472767829895, -0.04866337031126022], [0.14577171206474304, 0.12791353464126587, 0.21976611018180847]]}
GEOMETRY_BASE85 = 'c$}r033N@@8pjVot0*O^#@whjO4=G?9&$}lA`(PO5mybN#wI919Ycb8idNN-=#hb2LnM*J7&*q)SgNR?F3%9v8e1K;?|k3>pV;TT`__8vy}Q=8{=fUrzWeO6r?bzu5)tZC%2yE|f8~Rav*o8$QxuBwimx(xc<jVcLx;z`Hg3Yy5=tfZ>0|20J^O}5^e>@IR;C3E8y+__HlVd5pzVm30fCNy5#wVg#ts=bczo=z;pB%5851|$@Z&}fnK0b=UcX6Dvp`4FR{|X~9RK6z8KVhWx_e)Nq0W=v9U|51H^>R5wnfFTuMdi|_^$Lvx?J9Mx=KFzdf!}KF7F(9ayR+vqSr0u^^&1$$oEXUSYWBY{ld@KKYuk}F0T|7?k8XKi_VwJtF@P~ujiH7Z7DzL%tBJF+T2}odF5#Rd0ejHrXBqI)1z2jm9w`}J&s{X+u2VJ;QMwIwdDJCq}<&mm)C0?-of|fJKO44SiX+i-=%w=T#s{Sy<ObSq{3Xeyk}j4&gJJMTYM#9^kVM+nXPl>dOSbPOy~Zu=_mZj^R}{f_>kML&bhr+_8n8*+sSvHIJ{M^N88h5FW*;#d`o$cU&RgF&dm$6<?_n4uNQFt4@k(C%PZdpC3F3ErdxdHi2Oa={(>*ExLkl=Hh=GTS<D}IxbQR5Gx+z~sa$UV;>yC0&fs$TpW)no<)n}Bmps_QekmXBPtWQDnU?ZVWko;7BnZF9z)UU|SaXlK?qo}O<=6q9x6Y^u7T=*fyP5w!u|=jlubj<8j&S+gfuj7V#5B48oqv}Re)D|3uC`$%kFP%S-WK_OJ-Ki3-(8i9w#f5S8~w*&zJ5fTEtd5X^SztL^ZG9tT+gn+ZG64hYka@TZ>KWk_B(T8cphr;IT@Dq*sfqbfA5r;A-7+dRE^uEy;RBKt5tKhS^Nd<c;0*F`SG}@iHkPNzV>kTCjPs#)n>UKJui^k<E&Fr_{}S>=YHw?P>lQI&o{~aqt@`}zpJ@RgdfzMzbmoj_<kL}-GuL$Ap8ryJidBt3E`hz%D%^cu~=Wuc^lb(VI#Lw>9Lys?#hhZXz7O`Zr-nyftefRc6y?Z@OY{2wQfuM%gu4~eLbA%wyfVi?zw#5!7o~Ty~#%hxc!ljc^s5dXT*LtazFuJH#c7RQ)1Xxcb?_;=v9AR$Nu#Dyl*Pyd++4_Zhceu^`7H(=u$3;b@yqZ@E`ul^IKijPppHuOyMs}P2zS(b{75ldoAJnwiNYute(f^JO7c+zA|See{XV_$4k@hq|5c2^T*lrhVXMPb9uFFj_B{j=Y?N%d>OYhcpBHE`=1hi+ptw!|EJO1e&?4d>=*Ad$0khl=Bt};?PI@ci14vr=_^7Hiu?UbjO*@mv*dNE&HFY@ZjWB(d2Xj8xFAjL2esncS?up0ktWx#JeV?vzlS_)so$}3cAi+*U!}_ZrfwZ4>KU{-RW7f!x**2oZd$6PJsSsezq-~hOqJW?x~B5}?9}h3$n`kGpXT|XXB4K$^*Gv271te=XeqDW`E`@UH}}1lm#291J>7TlxOhf~rpW75+rB8p;=l1V-;aK!zIa~yUR^8qgL0|yM)nu}rLljfE6;mZ_+)O6b8EKnvA;ReqIv$iMz7T5b?UfYUGwHUCsh#j&1$L1{opKrldr3uIgu={UoF0MsyAP0R8yQQMjjGA_6=vheQA8Zzvl}-;5ojYR_X?iizlg168j0m#lHM^7vA^ucDGiE_2MVi<Hh4*|G51AO7@2oig`b$*XLZH>bru+DfA6pUcaWV#B>+W71#L<Uj49`Y;V50%Rk3b|HM%CU9a!w=bhuvoy#rrKkjy_H{ZG2#p_P>-ynSb%4)uDxx;*}@Pw>fE|0tBQzy-vuZA_^^4ik(mRsik#}R4XeAf?(Xz%2tPb~AlW+cxO=aCPW$-X{nfp`wyt-h4~L4)}Bj%q_i|D1ZXnEPSMVDX#?j~CBnpWS>;R67h1{TbVv=ex3U3j0dXTkI=uKji&HpOKu%e%pGVig~a?Tqi1PhPQR3mK!vd{XIW(z51JvM89=E6C=+<HQupL%;&JT<^I?Ejp6dnn$HOT&wTDrz33oc*O@fQ#s2&w;(S&olFREY$9H7k-A0s)>?!t>?HBItk;cXGj$1eV_KI{43H3iF`{udA6?f*S>=*CDfuj#ueDnF({=@-`Z{N@1+t+omZy$Hlx6PAc-<-EUN9?uuwtc|vE7eL{+hg1J?7k!A8*BZxaWD4Q^c3syyT`efeh42Z{I#iKpDgui0Jj6{SLr%E&m7-iFXKz|A=t}&aC{IZeB1n?`4;SLzWELs8|-C%I)0lqoy$G$E7nEG5xzh5t*jZrUhdbJ2#Kt=b)l8sJ&%2?M{|9-t{fBo)jp!#4exF>*RNdOT)(sr1bdkev~L7^nGdx81WWVW+<(-%8-#D$$7tV^`_0_<X#eEjVShIFPt#ZWcl)>fSsq7uf0liDfA%)++SwDy@_3o^*6y3nFJ*R1P3{NtIp{H-o9x@ym+|~%-}d~a=eXQ&=5t&f6UytrzAlP=+j)S_74mq==MZo6$GN32MQ*=&p79vxAIrGo{6ps@dA!W?5}mK)dd%~cZk)&Ddd%~fQst{u%RIsPjm~>=dGoxd8|Oy(y5_mjIse-<%XM+ibWQxrQjd8q)s1s3|K4_v)s1s6`?h_O&d*|fS<la!ao)Dff1J1Je9pe@d`{<l`F_oFKD`&n_f`B}V7y20ciVdey^pYOdmnKc?=S4z-d|if@nXK(-gneKkA-i0Kce?3{=4mcN;BTq<oR#DuPIrP8|8U!zTY{F_eAz>?}?i6Udg`gz0#4lMEJJ%P<o%0uWP=~x;nJlEMM1r|E2e6*_Yq1*|)u4J3D7u$``+<U;iaTUZ-Xrfbt1qUR(1CPW9dvd7Ya12g+B7_FMB6>g~WxOFPZ{#>5ulceZ?p8Z{wPUcYAkgz_!2Z{}Onm;~Y5@-vR41D5h;KF4{|hu4!m|3mpAOL^prG<SHGe7|OXiSkjbwtSR!XL`20zRdiUXF!6*H}hSTH<NucZ$^1GdHtGsHp<J%<;}bt<?$@*8vX2;o181pb2A@E`9s+^^M{m&w5$u{At`TZ@y)zt!%aJ6-^_nfzEqw+X1<j2tMa&;`Bjf!biQ2P%*Rsx)>0n%Tgvy!<;{FA<%i|+#rfgBxw>4wIG>#U$Wq?SKRcpg_F3vjzFJRr@3YiTeuO1!f2nuZB2Q)Gl17wOe3cPHq?A3G^fA?Y%6?SPf0eRt+N#O_o3dYJv>}C-12h%91U%D-$@u;bf;a}T1ZDnV#AYKtfUXCRG-8wy6QS>csh$z2n{*O*u@Os+_|%Bi&~yaxI_OgHYWyt;ng*U?#CRj-L*E6H#)3)bfmcF5LlCcl&I7LjCnJaxp|RjZ@E`<nGX!yO1aSoPUGTeTYXpM0ixFdtXlKM&Xcur7lo<=10)8Jl13Cpf1FS;lgU$O_5yT%uKLdXR)u5k&4;iu6i2YCvtf9<)1aUre4LBd115F0!fU^<AhY`dZpo!q!&;)2AI1yuzfFSOQAbtVb3|s};5ZVmf5F7^W4Gsf$hem+AgF8XHfV*J)IzfZMZJ}+T!QeLF*3fof(lOxHU>AaTI&>`9oD<U##0#J^z@#cz#TYM8o{aqh1o1Mc1}0q#UIunU4}sm_BM9Q72;zg#{osS(eb9XHK5zjv2V4N&0nG;Q0B?gH25$p@WyCe82YMJxx&ds?GY^9J3uprP3-DY7aVuz7FzE~6R^W;V;_}Lqxk&sBv@)~`n6x3dGPo`@3|tr74cZ;t4cr;p3EUanL3uJSJ0OUiM!XJf3~dW0Z3Au$ZUSu$ZUSx!b%9@m_Jg{>{lL?p)4`+*z|+7Bq07Jv!Jk0g;7`CA&?Dds@EHVgA@nG?5PS?ld;oe7Oj-aw0M?;9z&dyjf_Nu%8+a%9Ec7ezS@3n`$=oIW9(oIU4NU3*-vZx+egVD-K8+xr4V?=nZ3UhUehFF;{1W&n1hEgaJlLGmJ_zCx2;$NR;tJ5p;0oZX2;v6Ny5I)jaA-GhIJghAGq?}9C$s~Y)Cukh4n+_*SDvhg<_O|?2;v$D;#$zgVA3YwTHrd+reJez)Iku}MiBcUh@+tWz)|3M=rl0tLU25I5%d%ABJgr(26#C*6M6=m2|kY?z5p!*UjSc(9s_>|Jq|qvJ`UasJpd-v!F$2m5yW}WJ>WcW7IY^#3!Do*3(f_ff?fxo0$)WC7b#EHUJ-)$E`s<Wg7`l47MS!V_&)eY=xOke;B(N~;B(+v(3ilo!2Zyu!2aMe2;!1ZA24YNa7nQFAua_i4SpJ07Frry7F-Eh0bB`O4O$gU+5lV){2DYI{2DkC+6Np7j)wLGM}zxAL&5#Qy`as(y}&J?^}sE_jf@B~qP`KYB8VN(M&L#$?|{|-JHXWu#5JL{z@&A+q_x3;&;V#{FsUCn06YL11s(vN3XKPoE&@*le+XR;{t&zZnh9P3-iRRn8hRc~dI9`3_#}e(67(Y2+zT!th%Y0EzeNy#13eD@2K*&-FPL;Y_)G9s1o0+l9+)%>yb1g{f_Muw7rX_00(uI30(=E}6--(Lz5>1hy$ikpzHP)0(0kCkVA6-+d*GiC#1EkN!K6QeAAs*b&w>95-32`d-UXfmoduo)ego<cCM^Sg1MG_+eim91{4BT}Q~}ec6u2DtIRx?Z%9A~axCiuQ=+j`*vf!7&uRtq-Ujes75Qjjkfk|Hjhkyq{Bf$f~anNXR9C!kPcpS7pn6wvo9C$Re1$Z=gFtibPF!)Vqeej#$zR)0WU+@qkhC+uygTTX~Z$pE?Z$UdkgTNiZ?V+!NBSK4*^!52q|I+&8qw>Q>{s&k4FRf`c`ImV{UByYZh|tnBzl_OLk`pSY=qaN73&+5FWd'

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
