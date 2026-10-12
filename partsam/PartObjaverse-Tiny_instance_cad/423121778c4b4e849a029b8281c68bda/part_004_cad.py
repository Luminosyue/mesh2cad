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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/423121778c4b4e849a029b8281c68bda/part_004.stl', 'relative_path': '423121778c4b4e849a029b8281c68bda/part_004.stl', 'source_sha256': 'ed69bac17af4563de957e8386b0a131d6998656f1c2e3b74c8347d47d52670cc', 'input_faces': 334, 'input_vertices': 240, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-19.59832191467285, 108.45841217041016, -22.677474975585938], [19.598621368408203, 150.4280548095703, 6.587879657745361]]}
GEOMETRY_BASE85 = 'c$}qL3zUxK+J0sTo52uKq<0vHGG>^e$YI`6lEds7g=p|GMvde!&PrZw<X8$JhhA(%P8FrH^H%IINSR8GA4Q4iAS%1|e(vkOzD(ctul2A0pSA9FUC;I2-~F7AYcksxD_+UyUxL}Td2>%w#Zqf=rji+vn?EcsCwFM_z`>(qOgwb_5ocv|?wHvv#*8qJ)$N-*G$+6A?M~em{hHQIa_aUQls_!L_rP9*^84nB-lq3}p}AHc`f%^Txi(!dwQ<8FC++4WXRPyo{3~sX;Mbp@7FY~=%;@b}bl*MXNID$XR`s5R(EXX|zi+kZ%r35aVSnhMW|QhjI`rs{R6*1E5$MiKiSYMk4Tm0_tJz0%Giv>B>GHjDKJ-x88`OWoFXiDkAw}a1e>VhuMDEuTC!83k{`(KY-?-O&fjApVKzG~zto}2q*OatV=3*nn8}&4F|Bd(<=#BS7_flTeI6HnzllcCM1<;+uyR<wdV~>mOZl0_DU)Iw2_ij7@{mGE(TVk}`24~bje%rD%&L>CU?-uN;kM@jhum0bR)i}@AE{Xgrwo-lBdg!67wzW{t&ObF2^rw8-3*~oiJty@I$`nBNK7JeiUfs?YMRy;60lK+f;|DkOEQ|E{X{xt6#(w$WG}<k0IP_qS_KS02aw(Lz<}i)FcqZbQk++nF{!us8`)V9FF7cAY36Hx^^@N{MPA_+7d6f4;it6o>wcpQ<i4hF{D-nA5Sc2B~q1wez-vO$-Yny6+^&L_XxU!O#KX!nY^Q~f)QNJ~Ds@Kcba!%`wb_+iqqxm+Rs_j;K-A_`^P=l{h5PxZ|w*R6d6;NL12y}Do5d1@XkNzb68~nNqdib!f_41}@e?8n8y7$sfZU2I@7tjv1YeEm^Pt*EVKaTkRpiar6J2^G9zQYgQjQkEZg&vGusO3L<6zw16O>cm5)_P3Kzj{B~*<?*@pzWWd?Q=~k;=7BxKsOa;X*rk7zXtIVGN6YloKt<kwsP?AduI~zP5TVG8PNmt#oIL><J5aLD;wo(^mASKt(yfsRKF0qfBF4-lJ;j$SN~%#YP|}7P1WDOatq48vl8Mvo2wy?^K%>M!AOncy*Cc!bE?Hc_jjg2ch{`bdOqI+?Gzq){z1eko`igzZ~p?_|E^CDlt1NoBJ`GFE!VQ4(1UNz)zdi3fkFS`TAt6FV0{anny>l~sXgJJ-(1UibSuzH_`9}$$J&^mrs8JkZd?NVL#xgt!0-4*=>F#2D5t;wQ*D>2k3l!Z4rsk@NUEjnT&fP@EXzbWoi~3+e}sdlY9s&Ijo|Mb?tprEqlZHG1}xWhOG?E!3qAfmzPrn{-MnGNbR4f7roa2!5tPTIev+j9aU1l|hU1#=j4#m6!M-Zc{V|@_E9N?#pXZ7}5Bq1}9~#jH?dC1Ki18BIcR=gAD@EJQl+tl@?FB8*p1fpjhoA7fpjK7H@usDr-TVp%q5B_P*8V+}q2r_U7U-t@V2yK1$G3M|4%Sz@0b;y`PlcPHd}~JCi2D6|pO*8fT$JCLm|7k2-uoEw-R>K8{?9p64e@Wxg1`S{FX;Y~I?&ymsoGz$KI-EZet!evEK1bzV6w3Ph2C2TJ)B)1{-(}6&G(1;s;7PiJ-qe2j)%6}uSdRJ?^pjz2L0l<nho7QuKjDOA4I$Pb2~$K4$abjOm3{>WND_xd3LhS)1&b^&MKBvz4s*ehvUa%+`8eaRkhwHwBM)IfbN$&ejVynQQO~NR0H!NoV*IUGwdeB50=f>IQu6<cgMHX_=D24oLPq}0q;oH_HWW(_pKwVp$Eq|X*=|MMB67c2D-V>Rm=aQ(eWBOP!a8V|764uy;wun$?W)e#9K1}x;Mbl{r-(?-QQ|g(D>)eVV;<;SHvOS_7WO@a|1npT$mE4?SG@j|1q4b>20NuZ@-5${&%xA-yKy-AfHlmblod?N%x!4ci<f1CRWz<r_C1KZ!R7)_`dfC?XT}9=(<tA5a%HOz8N~sudl57w~zfx^iaV)+MXvXYkBgfT*kSn=F1v?Pe=9Nz4sUFO9Mt}{J!y+FQ!tpOYoocjrL>c_BzmiSn@seA2W13cUr9FFYI|5=NE5<`d44BaW0-biF4MvFQEr#KGyZ*i2~@MuhyxaehcQK-*#YO3(-gYs&UG{gM35X2Y({E|MoAcZ(pS2YF?YqM0d6u?XTVAF)wUMDqw%h?xf``9%wt5dYRB$ey4gtazpxeg+Ap$-8ToVy;b!Mk6@qQxlreI3fFDZIv@M<)>pB<c{MtvMe3D)m3o;QPC@^#cChW1ezkV%zV!R_tF^Q3m-MUki|xnsBK_z_`myA5ml2=+?(FXP$2dVbqsNIISBS%L72>#(afo)|ICLW8@Yg$V{`#+RyRS+K=+Wcc&I`olya+fiJUfrz*G1=%6PZVL-l2V?=AFz_<i~mHe5dm?crZR5aiZq6tONLc)H>kWbpvst){VffGbkU|nSkqzYu6>jk6M>x9YcMi)-lhnd(flSJ<qO_NJp)c=4jQb&}X0EzN71^Yu90vGin|7?Ya#;YTfqiIuAW+o%ig%fc&ENg~0A3NOK=?xsMpT?;yXZeJ8N{6w*=qlo#^@boT|_*TRLFy06)N5PI}JX!lM0K5E}IcArH%MD4R??Wh}(j@p;a_kC+14)<}hS@&_@?)ykb@B8+gfc&D)39dbFz>nt*6FG0#^9k~cI-dmgJOjTadY<ulo^cARK=*k5@h(?JIYaimgz`t7m*ji}zo_$-oX3!F)Ok$KZ%Fg}W*X@E&Aj^*^yu?m$es_8Z`AoPWY3dm=h#1=Cqwr92|eok>Dcos{G!gQp(=s;J9@qim)3Ps&cpb9)Opyo=Vzp&&d=c%Vdx&u+vbd(w~alYL+ANCNY?Xt$e!nsjy})Z^FQ*9I{$|+wYf$8|9oF??fnAz@qQ8B$ooa+jQa57eIz_a?;~=5L0sNn!o0u8eFy$g_Z|QBI!W;VZHV5Zj~&3d!9Cjqx?Mo^-nS#8IO2D@6M86B?^8h^y-x*e$3ypa@6&c$F$epxNk6ap)Jf3YFW>qH*8MIm8lW9s-O~sD%VV&<I8`#B2a$VR%y!)4oE}}Edy#uz?}fPc`56;ckK7Z>>pd}?G9CIK_sUxj>izvv0rXH(1AVV}dJNWI^X~)d|Kw|0p5MA*y>LEknvC*9?yV`uuupiyJ3;sQ@SfXD@44aA<x-$8=e>BtZzxZ&s*~z%=W4tCK79w;r)y``BlqiH%He+Pw8)3<H{PW6a$l&7etdJ8`XAvveZ+L!(}T?cboXK`-Ydc<TdqX>gd^&InD>3}Gu-#xxUbZo?*o3qQIym4ifIV{$a})xjd)LR^W&hKTKfLr71Q?zGw@pIe&oHPT}ixGgr`)}I0-$qJZ0ZriZ~q-H4fiBoJsj;|8V=-&_hT0PO>Ti?<DfBf;ds{DrReI=+3THi0?IR@HNgK{qNH_k@uN_1$dtc@973Th`i@)(f6F-_n}&z$oo%z65fCOGQ**VBkx7AQ_%0>XI{|yR^_`>nI1ToyJvT4c_Qyr=eyyZ%5;orgx|H;qWb=<YtfJ2-v&KsK3e0yo`809Pqu{aEYSBcXYoDy&U2_8bni6Z(_XBHes|Agsa~k>Z{C@mSP%ViA=Tg3_qw3DzSnvE^Psy!PV2fcZ`}tN4;$vH{}+7sYc>z>erCo3=%yCm30GbY<9xqqla{~Kz3T7I!uc#*ZNJ9hd!t|dcn8t_QWv3zM)G~KYgybY%z_fBD2J=>nW0as>Akvq9CRo0{#mL#-amuUDbUSOzL%cpiuY1CF<<q_`|8$<`o21KICSq@zQ-1>!+WghyF>N+`F?w$2JS8Hp5kdJAK!b!Z6?-{IH8hlp}X099}b$q-xTCQ_vSpM@53{5aNl#&=R<e+&K&Hw_y5d4y`EnzfA*ew@%G?v?JuU1>DRl+)47Q97s0DPo#!?FUp<|tr8WNlKArcoW$0t=0h;h`#NOoMGnAU(5OTp$)&>(tkPo5XIO1dEL-;+9_z1atpJ8nZ`4svKP9`5m?pb@q+6HTXCrWw~aU*$SYqwdugDB}H#ANaV)=pbHN&ASJ@Z(IEv{u|&46QUZ;l-F1EMct-c^T^08W{k_Tx0D9@@vWCn2uxGu~va;;WaRnR1>U9{;IXj*49{inQ7sxm|jCoxKCU{ex0?7*2<IDW?HZ&`E~q$6HRzE>Nn9>urB$h){a>FoLuld;y=m73iw_4J4_ewx1W;lV|t*qLDohRhm#Lrx<7Fs`FLxStWB^sn&}BdNsl2uN?w(1dNZ*ec|E4<5NnVhG&(LmAiiFNf5f!l8%6jorUl<D!nZRm_!jwFOm8LbCKud6F8B}fE!GOH1;l;i0r@+`0`fCP$N4#H-!d)yOY(2Y1-~K}+)w<3T<k-B7d$~O7`FB`@d&x#7vv|HSH%BorcW@|PX6`;`R7dklem+7ueHyt9U^{1Udvi_Yn90bucryGLM~W|ao)AIjrcbC$Bes;xR-powdbroL!4EFKg+b>TynwrM(3WOPcGwF#`75B<K(h-j-@u1x^P)npWyc=_)YlVnD&UH$fsF*+S)|=Oe3Ghbi_w+GHo`s$*jX{;&bGJ^NQ%=H-&Y4wg{iWy3VCGgLPg+P526?S1`Sn_%gZRx*~iP(}FLO3$7%Wc`x&PD)CA3r->7ZPm;^tu-@ptA@~xx=o=Y#BV!9+!2VoRq+b`YE#|S^<}tr%?4Ku?*Ar}W;d_j(+wT)!CHJkZW_mTX$hV{Xo#5djT)w?VTupwM-%b(Fl1m@VVLo%{FI@K7Vf;Rf--LItc8|4u>K(|%e<(G<e&oaWeGc&ja@pTyoDL!mCx3?RxPV-6A#E`=!RN`BGrgYp68Td`*ZAqgN#xJ-+cU)J<Pv`=V=QHy#cZeZY%9TI<kJ5#4%QN1A(yc<lljeL{7H<tjBy1wkjuD}arroL4Ec2a{yE}2a``U%)JWn$@|A3hO~m!&3)zNCiOa|(kFm^Oa3Z;^6LJpoh~vm-vTpOtmH9J|eJOpqn)n)dCu<qj{z@*`nbw_}VEZE9#XpnSjy%`szWxxgKlvj}_a)|%=kZ$(u`hW~qvzEeVqOuw3pK%R=E}LYBg@c@-y-RbEU)0b<nsMKrn?a3`|Z}!tfdp1kW2kqleeZ{M1O$!Jixq#KWMG1wGgovx#XEmEt`5*)+?K3$)=z1rq&u+Ye=k5o?@*9xnN6j`QFT05;2ur%G`#&ZRp>E<<H>v41R0P^5n2AIqVnVrL4tTD`zd9Y2i0AEj*EF;kS?{k_#sDTLY$VB^FI56Wt=b1Ji={lec3(v?aRa{pd4{*nwQeo{Y0W#KGiuS!-@|d<))5eh1s}E@E?X=}Q^c4-+3Hzng8?iI_otH}Otld-A5lM#SdiSw_c&jHAv>KS=9AO|U!p-TZy4B5{S6HTqYI7)vhWLdJIzF@;>lP)q*4C1VJ`mu2`Xu`{{Uy+7+OIFMZ8$sB1xY)#&Xb*xWpM&6R`)rxpGc{BDws=0FaOEp)<dI~X#T*j!3)n3G0^2q(RH!+X=KDP6{#4K_dLo#mK5g#yD#+s}NE-{&0#;)wMw-P&$r?I?Eh_{hvwvUOeRP2BH7riTgo?J}-^bdQ{zx?y_MA2Wiva$YntjKJCjofMN0Ek5cERh?Z`41k9AMX'

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
