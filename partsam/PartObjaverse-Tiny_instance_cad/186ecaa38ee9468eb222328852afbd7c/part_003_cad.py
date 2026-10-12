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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/186ecaa38ee9468eb222328852afbd7c/part_003.stl', 'relative_path': '186ecaa38ee9468eb222328852afbd7c/part_003.stl', 'source_sha256': '4b5e9b1875c78bf4e958da6d1ff687b9d7f92768c91ac322b0ea45355b32a096', 'input_faces': 256, 'input_vertices': 215, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08286596834659576, -0.2753773331642151, -0.30960988998413086], [0.215172678232193, 0.05867687240242958, 0.27483847737312317]]}
GEOMETRY_BASE85 = 'c$}r02~ZVR+J+lN9hay<5Y$1hMgbF)xZtj|hA1j3ao=;1O<Vv07mQ208*xP?iVGK66^t8VM9@|d5D~#G8spS8iK8U>lV~(*;w-n{@0~=aW~%=Bf2vNsPrrQkJ71qZr_Z?*0YhurJ1X+iTDj*vxPO-I(r677M`d0}bZmG~NKD6ws5m>NF?{3aU%GYpm|+1E?38)RNAAHPF+tJpy-e<XLVLJ-n%qMpqhq53BR-6b4h}K=fq}DPLTrA_^uVYP+qFmMPTroTF6}){i%tK>pL(_u)ZA{z&lt4?J+FWkwExt{&|BrljBEXe%uDbqo*yuL{fg^h_~l2h7^;2t_=MqWO@7WcuGKyF5pVj)PJEvN@h6uc-fH*!4EztKAHe6GH2CVJ@#m30cF%tF7w0MY#|0Imo>?=p5LcR91^-I@<A$#;X_{$Vn`6epS6>F`@PA#DVO(3{8^c#pa*<z~WDnn(T2_hQFF1nydO>_T>Ta<bzE%=`5&ix(BpKJ*cI45gT)2wsw$0!xk2J~uV$3yY^3uJCTXqt8l#ELF+Jo#}P)oJk@70~+`*neDF?E*wU6v!i@@uo5`2A0QcrN;2=I?fS2ky62k#VT%F8+aj@Gaj)OTYeoq|PRb6VYGt{&M8e8%w_hIoshE_d&c`^jzZ4r@&WM4wUEB<eBv2W!;LnPPOrT)!SuK=jG<&_x=KPYQ1yCzu5@Bay|Vr#x?$^j8jOPEzleO7ZG2)MB=L#Z$_T@o`|;`jeO15?$ts4)*}&;Cv44n#8)pV!FB&O5`VQOd?jsu8Tx(NQR1I{9uK{<1NCbQ-<J4Uo7P}Fs~%iHeD+?6Umvta#_><6Qy=(9#<kDd)#&%oWBAsDZzR4$o0amst`;F*|8FEd#JU0+`w(@i2lj~n?7=eRUG0K+y=N2gy)wjquN&gEWv=4S9S&dZKcW=lGbd5{9WqFRrWY3Db8DW-I-b!2zN#-fkLxEp#IF~(7<sEz#B2L@V7!&R7Z>6F6P}!dA6sAi;7tqB->5>2kMc#|a(S-x;VYAWLLN(V52@#XeH`kTKM#5I8>8j@@lD)(j90x6kVk9xxJ>c~$3n-~K_2tWwQ|2pdcZdg3X(j&{V?82$0;$mZfQmyb=yMmgOj6>-)W}!X-SyB%A%PwQD0DP8HeWw(2wF+Faz4Cmt23IRPw5?rCae_lqPS<xcT)AM!%28%k%R2RK~%h;Y3`&`8D#Z<KLG14LCF&^^cOgn%krcull;XGxDgluSi|$Z{CO>ZIwI^1LeMy7X5sT&;R%iuGQ!&jE7>Lr5e7vLq%S__>K<$aOfn&f3a8U9PK9ewZJzN@eX%o-1DBFk@=k(hWM%TWIn9xeoFdX6^Z!ZZwug0s=wa{{kEQCsJZZ#+)wd#8K*uDbMbqJe2j}$m2y(<>-~9#Z}PY;br)7jo>~6$p@SObB7Rg;@%^(Gpq^@HdH??~`v^W4>bnT_Z2v^Yv*yxculm2Qm)$qd!hg5MQsj&5kSp`+Db|nj(**ds+O!bY<)&58tcxpfUzc7=osXKzd*^=sO4KtU3+qmswjH0-hGoYiet#Vq-%0zhZ)&xcZiN25ql|NdO?goLCVc&?JE<}c-SHmLYCCVieLcF3aaO`|x1sK+D)_qQEcMswupM#BUL+uY&NZp?V9TwDpWYm*r<J6^?_Pm=^j%GnPo0`8b-uCBf_c>bYvj{hx+dZI<Yr;NRuATXf@`%h1=j=qatylV4t%xMnk-p2ZRGO<@{{B_-j;da;&~44Yv0mc$g{gt*4OQJs6$H|u@CXfQ?c(U?a!lb)7B99`jdw#SO=Nms7L=f9=_&#Vh{R%+58Bu^KQXcf1I9$d|T?^e4-`Tr$SpS$M|VmPUa%d8}-B=@f7=y=CnE!{gwp6SLz+c`$;_#dKAxfKzbVdUUwEk-QJgT(Qmgikf$U^*5~L&s7o(&Lq6qrA?BmGPuWR{cb57dw8Xxo&&ihi`YliVn`QEzeQ*u?w_5Q(@YMuQ8PBMRa}Bk4J(Bwy^S#U;$6BZH`Bb}X<jZP|d7-pSM4ZJn1HPgxo`?IrH#8mo<$(v``+YJE{rQf?dCXeW@euOsCfWbv^+MD!@hE)NHBt7>m*2}cro4b}DU<V(Ua$xEWnPqf81ZY0<vku5j`1{2u)<fq8i(_jdSe65U8WoN#h*VN?^!i-J<fHeuiD}{n~I#}oaWaS_2{Pq;47P4WZgb&c@DnEEckk51<rBWhA{Z1^GV`Qbdzy@n45#^(br`j4e2N6u?5RehiTOV`0C(2@*aD99ph$7YmEEQ*B+BRb%vb6{W{EpujR`5K%0G4&dGI`!B?02O1yv2diVoAmU!JI3F9`{QY!1`8hqvNb+Ing(|69|I@uoUPig0}7UQtHZV~!TYy{srt{?8l9Fcnoah1*z@9|3z>Ph}q&aobYWgRCz+>HL8<(HwJqzRIzhHAm@Q-)o7)z=j#%xgWfK=KcYhOhn2P4?G2D(W;VWzuiTY}~K*q%ZO*F<(fYCa!WmjEKYfQSLq!zgvamc_RYve?7tr>(z9>p1e;z<4~u$xu2}#hUu99dYiBdxV|+6zV_lDcwTB&xGw$1!MA?ofbp@!c}e{PYGHmUUDn}zZ5b1Y@l>8U$oGl!cV!={xP@^u|KKXVPi<MR51*nQ+ZPk~`cF|<57u+75N~-LCiB;EI^Lfaml+bDtijj1RAPNu9hR2JeXW-KnFDtqkH<*N2lJJ!5+Ad9tK>f|_4GU>^#_ddL;tRyOMLVR@i$e=KKY#)`7Pn+#Miws{+6&Dd=IkRFA;y@O*!X=d0;)73;puo4^`yc6Y08J@{fhD?_Dkay$Ia5<=UdWSJ$tSaS-!M8L=F`s*lHWF)#lf>(OF81z-E_j_mKpmt%dYPR;QCFiqSg>nNcL`PHuX;49yMh<T;gyo=|q&R+W&>UnWi-b-cP@GWz$ekRYkzSJ|<VYlS}MdH`Z7r)_7**~g1@t)QWM~PqhH@rvHNngTOJ$K4E&w3x@sb<X1N1jVv(XT#oocPCv;(efP$&&T{?hNU-=34QKYf1j&VX~h+%!026-Ie<L6<w74+2ZfFllbo%Vc)dA=u`mT`v}ez*2J+A@9Hb>>4!a}p8JuQ=hi1h@RjSer5^hfsb~5P_?kmMIiD1GB3?W3CiW9`!&HgyHBIVFcZaWaoFe|##d4n5lpy<$*FEI1^v*9weRcz|pQz0m!dHi-!MBcf$GX%4$H{o!E8i{iTfVO=Q*y-bJX_8O4JN+s``?iB!_X+aZ+`!~#POQgf3+Dq;cK41ihnR#&J#6KU-x;AGCO)=KB`^9<$H0wQi-??+3>X*Pv!gOuwn46EAu4&&I=j0&0gr&oRWX;)p@S(OGLcx`xn`lT>RzvdMrRa)-NBxSMrBQJ*9D|$C}w5>r$!zv5a%$B;-+^s^TyCRqEMP4c~lXgZP16F;A>L?@GVF9TLBFA@Zo(x>Ui>EERu#9eLj-G!(zx&+yfinKIu>X2Ms$ek%SqBltZnRL(i>F7m#dxDR<uPZA|Q)m8l9WQlLJLdO5gcCY(dm7E)ky|7-D>?}D)^-qxJ=ss5bcb<#Cd#&U#PZhuX7x8^tCStu?V)5S6yzIqyx+v$w(gg7jjS}B^Bl1}6c8MP_Qv8>5kw?oe$2!*CqHxYvs{bMN?E4(PR_m<zd~fJGzY;&=jQEA;kViSw4C_)GzEQp}y!=$=b6#8Ve_Su|%NpT4tvI>C*CYEfPq)384;y^3Z)mrlNuJO$nLh(Yiofs|iGOc0@|ZV=!&m3!h`(e7@|Z`Ck^TJi3AtbY@1&kOL9hGv`{jIJvQGBNZZYByzOdIP;I+SU#wEuVY7J~9*jio1Q3(xv<xiZ3iN{R+&wt_!@A|*{6Q_5#|L>nT>)UFmZEN+YwaE3zb*c8`y5v6@Lqx4XwI>@|lU#$WQ0>TPZS8`s6|osyLM<hikjto-$Ytcq)JpPY@)hbe@)hz`Tf0HMNxeqCNxsfza22(ZTt%*+ULseJ%c-U0a`Hv$1@c95G4(9Dn0%gkf_$EQl6sVUl6;JMh<uEEn7W^Qn4C>bC1;b<sC&t2<Ya0hIhp*4t*xZ4peB-6kmJ}4-a*|<-a)odQ^^)`26aC<gPcP>M9v`}p&lh4A?H$0kaNlT)U#wmi^x&7HrLi-ZEc#ZO|Z3L)RE+2WM66k*_Yg(`T@B=`F&dpRE+NgiZaU9CQ*Z_X7Ws1`^eV9*bI)bwKcZ3$<`v-3|>f0ATJ~@p>82BAupwFBrhdv)b(VIyv)`XQ$MDzCx1*{&1P^sbt5^Ryn(ufyn(!#nn2!6-b&p>-b&t1T|?eZUPp}~$8g-%u^GIG&ERP2OmZ}N1~r&GgB(OPlY_`pZEXy7EStfTsb;dFf#k{LDQpH$x3zHUhtxo_p`*wjk|(kmJdXN4+0YNj<H#e}3?57kAP*)Fp^hXEArGZaAP*&vW*cs6gQ))GL1dNcM^?#wsRPJ;$-Suk$i2v2slCZv$(^V@$eqX?solvP$?s6Rk>4S=r*<K?C%2=%OKwMgi`s$w7TH8~C!5Hw)HY;Sa&u}ca&xjXwFTLk>_~MXJCfg|I+5QbH?p;cR0paP`3-6VHiH{eoyd*JO{gy9Cgi5n7UZVnX4F>XX5>Fp+mQcEZb@|~w<Ncwb|AMVx23*IZcBEfb|JfwJ*eHt9^|*F-N|p0J*hp&o@6g-Z?YG;GqoSNGufLufb31~N%bT5B=@2Ellzc;sKd!V<o9fCAay)-IN8wA<niPXHiJW{6Uc^6BZrdXsI$n1&Qt!_-wpoPzHjhKYAo5%xnx6EDSw<D3{9f0A}5h|u^GI8&EN>?Tyg|?HZ_WD=zQ{Q@*L_~@*MJV>Q3@<@;2%o@;35r>OS&ratbw*oI*~g9w4Wavuy1k^;7Br@^M@H%+~U#1>`*PDe7tRDRLoICl`{>P|uMAhT7F|toh&mMdObj4F~sE|6$|bKl%FCo>xElS6k5UUxEUL)-t|l*uEIlz`&;%D_Qv`&64p}'

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
