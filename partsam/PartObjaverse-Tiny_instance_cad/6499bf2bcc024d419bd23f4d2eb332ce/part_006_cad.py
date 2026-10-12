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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/6499bf2bcc024d419bd23f4d2eb332ce/part_006.stl', 'relative_path': '6499bf2bcc024d419bd23f4d2eb332ce/part_006.stl', 'source_sha256': '22fe2e69be13dcc308793d105421d647dac9677797f1fd464f23893284db02e9', 'input_faces': 252, 'input_vertices': 207, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18812237679958344, -0.05588884651660919, -0.42890822887420654], [0.10122663527727127, 0.24179308116436005, 0.2409074455499649]]}
GEOMETRY_BASE85 = 'c$}@83shBQ8iqHhmF6`q@3u7+EhH}}Dhb<rDJU{|O>uic!xRt@5m1iCc*#UmG!T@dB8Vt>!TW_H;1$qmOvPIsv(lVWvoc*J&EDVpnw(iPYt5Q9to5z;IWOP&{(pb}zyGs23%|itsy0yY(^9#hPTY5=zM_~>Q)!??28KlhO$rQm3l5#*q|_DP{CTFUh79-h8||b-DlsmT1H&hUx%5<B-kH+f#Z`5g5)u{>HX(R?NZ8~+(;qNldU&AWhkrOBG|+h6u5(8ZSG7xfS9PxXKmOD(reL4k;8cM*m&XsXOx1F-%1yQ3t}VW8^|j6N`}dvUPpdAzmYbF-eu}^Nw$O@`rdnqFZL7R~CrEsC*KhC_lx~st<>!lUeewhRX7&uJbN2ov`F-=-;wv3<WL(?&fs(KP@fCda=|-u$;AhN7v%`P8K<a1@1K<~3fj=>HlZ^92lgpx$FN<%hvL;9JFL_A5l6g^lE$F29mg`e-T>~y)p3668%j=4x<*0WGb$ZU;>21C*CikeR)^o+kPktif+MamJxb~ek_$#Z*Jgs-GUUKlGMr}krXUVs@AHw|GJ``UW=pw!rxgY);7c#IuJ<-peJ5VR4Bl=luu=rX)HuCS(-DS?t)<0F|sr-=zKmJy_^wYB!#!b&eow7ADf3@Er^iA80{=}}_R=IEb%}vOUTqnLIWU{0GeWF$J2TnwtqI8UVdKuQMyYApyR<}eS>~ZLGP9prIt{bFZN%4}e`p3h6sG-jJAoO|GT-2|46aIBq^yjr$_ywigqz_;Gg7u=WwOA|t(dsT1U+Xyw`FjgDIqZ|G;qX&hua)Z@6pg;cgu!oLN9L)VScUmFn+gBk#8j#C>pIC-0)jFB7WHtweXwu;^t*i{b+m|0$R98sbvhTOiNCr4zR&yclOAML?vG_wANakm=E(K<|Auwn=MBF+NygO{9+7<ONH6#yuIuIfuU;2lfBX*oqU*Abibn+Q>t@~HpM7DC)QL_;{|~#vZ|?V*__Gh8PDLlj^=;V)b<#Vc|L^_0*PNf)Y5f_Q=jJx3)8w99uW~yN_hbLoysz_;<#pgS^nXVkhdO%OH%nxF_f~aSFWbV$n9s;6$d8-5PsS}@A>&$l{Bc6^od@og_cuNxzINrQ_?B}gv7cv+#yMm85&52t<$7(Ke}KR6+Y=7!)n>J$?-{U4`X1f^_w}h;Co0d!I<%3@UkUmOe(62AF6-Fc;_Dr*ILy<&!VlM5=OX4gr%Zg+<*N8vk7DFIeJ=Z4KX^*6OZ7g0`p!`@uKlGn$+u11g?!(~vc4AgzoY-p{8<lH%JsO{!n&W_BEBuYw~VWQ`nl9mJES{|YajlugKzU$v`1cF$Sak3)=9;DzP*tz*Ryl4_?92nAiryS>4SY-y7;#4OW;54CHboV9`Wt#;^5yZ#D2(GD85=H67yMnPUded`Vs5WHUxc(FOhj#BMQ;~>L0;hu>t)YwN>iqe&aCDCO*<Pz1dXECr(5C4;o?rwE7JB*>3Rd9x*bnnNC+^+`DhVAG;<}>UFt^`?q!*_|rozq7PeK!G389-{<!*$>%v>|DY!3GiIaAU)>pl>)ljwT=HX&g-YFlIDhnTyZE*oU+KTSc|w_J{`KRidtZG0PPF*iqbtbopNT%Ft`gr;ei8NUB_Z;@(Xlw6e?NyheU_mA`^QSY8g~Z%*s56Hqo0az+p-_^JzhmW6S^RO#t!(o)6mcMQQ}+cXJFiIL2_NTIpff`*Aw6${1WT9b`<i%rom5)lD=79>Vxys_rgx;>(m;jB=6Ax?0@&A;_F}DI4OPE6Oa9{c&hm7(o^DF8wOzhtA@c}aYTH*PO0SE?cGslPOkW>^%eB9-CN?@)3V_AZ-V{rroz|LQOCyye`gcacU})aWjgMQ;o)+gT5B#oEB>SwSoaCz@SJohLVRm*8RpZxLe4M!Q8w<wC37&JU6;hSCPu;c?Iyl*^ceiUxE|H@b=1)gqfXxuICn1Gm2s^;nec1%Mc({m2VZqgf`50csKq~3e0x+7{C*iY-!81ixc9x_cNkDw*;lvtz>j_ijcg?6yZu&x^vCk{kgKvUVr#)aK1O`)jrQVe3E!v4JU{VAzGt}j_VkhzjQg(mwi8v6Z}%5pb!rE{-7Va|-E-x0$lB=l6WGVc#n(38k<SC`>_YLi0o%m4wQjXot|O20<~gR<8X~^h??v>>{{hYur^(`5SKLGX*1=f!L$~2~Zin@5-wXRN?<wlLK1Lr$KH+(Le~IK@9)a-!Ex3PMR{KQiepwgirkaCw856x!@&<Vz|KudBb8x3+*x%DI&#5l>d}-bCGx6trDf`X-&2`*I_4>fC{}cA%6*s)Ecb9B=UylL#mG4unpu70CAO8a1cN^xpdx-cJzb4}AnJ?nL-aZ<BbYJ9esKB|A77c&T1)LjhhjAT=iSW-iz&YkIMCPS@{T1eO=nOtj@2?TxlG}f)=!2;^|7%}FewAeL^`fZLlHcm@Scj(@#kYSuQ+z#S9<KKvMdGVh7m2Snd;{~m{I&Sj%@L^6)D`pW(Ndn<>~86(b1wwzn>-GFdK~=zH*hXZ+atana0LF6eDvqYi}Ji{bx#uCIw%F}TP;+4_2ruwcgcP9*|!{iW*+Jc3cxz*o3_h1!T!18Kl{Af^0K_Plz%F}*L!ASe>QP}|9dx4Yk8sc%@#Kbe%50dNB`-b<SP-u;wuwkrH=JCi{z^}l8}GVitAYHg?(~49sc$oFyHvD*mr(AQ0Jp)<X=m~b(QTw{<YQcmw$~qUcbrTZ}vOq@jO&E3jJ)^8P7?tx59l?GY_ASgFe9L>o1RyAG{LxMMONFZ{F{U`?Ow=<m(yyJZ{qv{)gr0{}(pY&+U!-)3X`Q+ZtcMk8;Df-fhs&!kh4UuBx|B<8z_nJNSvc;JZg+zlBtj{i=OcctrfQ&C4qLw$bO0;QpG4ac`>dcV&og-&|T++1FD4CceI*2>IvmoM-h)E0+9GD)zGvo=5eGtBW1#R2z=^nFmqlQaxEOt!O0b`-a1Jn~(eGkMX$Qnr<qtJWuTjo&(f{38+6T8vO}K!??d@Bmd(9T<=vpx7j?C(1*k^IEO}MVcfUfG48`&sFRe3>&jk)Iy|qGdyn9s-yyy_uNuyWOgzWf8tSMsG#T}+b#T6vSujtpyI7x&({N7t?M40Tz0rrPXz{h!rdXH!)2Kh?C!BY64xrAhnK*wuQ{*{G8=7%Y>dtS4bszXdd|OnR_||zbm``y9@~6)b-|nsByubGDe#sw`0KZRn+^4C7#n+q$!cWOU{en37C0$Ve+%Jy)?(vvU$@l1g$5hm>*$H(PyyxI+$GzZROvU{*rdWJyUTiVe^Dyp%yDbhl^nXnQ^kJO`eAflY=jWZ}(LC|>5jp7F=+80kjO7O^udhDL8|UqLoA_#U2I_wt&vT>XfWv-Uv<!Xox($E*I@Edgy!!OJ1C{r`e)UGFx1YnegkNuORo}0sqL@)#X`oD*Q0Xf|(=>mc>A(MqFv$JC`--q@=l{c3gvyJGIZ<d`a&>Y&>Z{~><i^xiWK&y{8<U$cOm<<I>_+WCHr0>pMjmQJI5mRmM~)yzQvJ!1<k{5s$+O8()KTOp@*IZA<ETB!ruHF^Badg8Jc!zzJc!(z+KJqo+`|YDsw=e<+0-}4rZy$JlG{*UBAZ&D+=l!%qrPlKMQK5Og<7Bd3i$=<OJq}>$)-AyUm#bb)*_qQfLx7Shhefx?MPP1U8!BjUCEx*cgUV(jrty0Bl{Zh0d+L>J@RPs2<kxc2=Z`hfAVnhNa_IcNb(r!yW}zCu~Z-OSaJZv<RMfqvZ;N^L&$$&m^_%;i#(XzkJ^pgkL*o-o$O6+Ppv_2Pi|;LBkIf48e~(ekWH;hewl0@T}`O9sa46QRwtWUk6fGl8nrRm)Mn(@$jyy-(};FPw52vDH)l>;stdU-`7I;dshz1VWK-S9rVb@{CJ$4dpF6{-v&i{I>@y;dx|^Iw-bUR?-bUVP#4aOpjL4;ClXJ=2sawfg`QGgelb170UP0YWUO`?(-A7(UUd=H1AT^(S$cV#6?57?iA7qZnpHi1n^T|uepHTD2pO6<*w~-f<7gD#97n1)<%_jeqyoj1ZUPNBPFnI@c7x{n@dyLpi-9g^L9Ftd46REq%iR1)oE;)g`jJln?ooi!qff1*SI7U4~K1MF2mXZs}#niLpV)Ain8TmN5h+0A}BHI`ypEhC>bu+buyqTOuEhA@<w@}ZLw~#ZbrQ}R<2K5X%gS?S?ioB6*Wte<|T0lNQK4QdY)MRP_IhnkcdW^i5oJK7qr;*oFi^=QB>D1%obn-fC5qTXsm1-lWl2aHaAEllqA0?lxv^FQH8^|$6%rGL_h!7*@8xcyikVDB~)OqAE@=R(hc_ulS8cmMoSiuaFCo@c*$T0aMY7E)bx#W+?(-<blDL8*jT|u3zJU_2YUQUfso}X_fFQZ12myr{wvC8xN(d0zxJmvZQYw}8}g}joSM4eAgBClbXynq@)UO=91gif764Ixh;PojpBCy@iGVdOyaRO(FfRPq#RFgciOWAevF1Q`)e{gCW8*vYv;mH+fF3(tQn=0lvrKQR33J01Uwsr=5iM$(^u)c6gqW<DDl4~xz+*`2ES>Yv1=3_}'

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
