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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5f1e1e7148424a6bae25b5138ba0088e/part_006.stl', 'relative_path': '5f1e1e7148424a6bae25b5138ba0088e/part_006.stl', 'source_sha256': 'ee561619f3bf67a7bc975c2ff9d36d7e1f76043a4602251710976d90de99a57c', 'input_faces': 464, 'input_vertices': 316, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.1454506665468216, -0.1254376918077469, -0.26135843992233276], [0.26926037669181824, -0.007073145359754562, -0.1429632008075714]]}
GEOMETRY_BASE85 = 'c$}r13z$#U-pAJnHRH}uoUn5n361+@(7%-2O+_7qJu=coI+V9KYM1K7IXFodPV}cJGn3088Oi^+ju}F^L{9$QB-J6OqVm>RYyUoLxA#2n`#kUSo;lC&{J#6M)?Rz<-@5(w-&1zKi^``f`MW|bZZT)F(?BU>l~uZ$oICM>yY9%H)cU^rA5Kx#eQy4&e|F%I0og-S)MPa^V@&R(J0@mybuzk*?VQol$rw9f;sX<N?i)2>;+R~+d*$3aDOdAJ<8toL)z{72wdvT>X?JByXPWc>{7chah&zk6T%&zrY4+O9rcVub?cN;b2ioR`x#tS^M!vbu=jCD%9@}uw>tUW)K>hkZtn%yi@3zNyXQOa+`0T5G{VJPFjCa+`^4!^lg?{}h4faI%?<cJY^W^0(NBS9Cb#906Pj}yHcyejMM*lkRiEUx7hWzqkm?xX|@Ok3)^mqLB=P%zA=4!zkv%}oW5}wR{`Ypfzr#tNnbLWw*OTyf_QMipmObyuL^SgQOgcmpa_ZOVn8RoI!iyja2*dt}0n~}XW%!B8`9Z$IX#m6$fSI*fI=CRk(^TJ#`Q>Ome7x#sEP#>OrHX66sJ#}`3xs6-Emz8<nQHM&yJa}KYQ&J{w6^s1mCg65_)$pvnVQ$CQ@_15s{I;qIpC3NHE6ml#^M4F;RkiOn|G8&3yymxCHM!ldpYfW{;|~@2^VWN&Q0C7J_&;x6?DG~wrT*9X+x_>QvGYy8-6pe3!#qB^&$2L2b}85%p8x72=DFp}f6L>y!tMO8b>5G2JO|FY_O4=G=S1sU?k*N?*R@wA7U6bXTOR+A`izSj%DTP)-#c-=&+E#%wmewx@Z|IXJHqqX+a>G8ayy?bcjpKX_LH^!{dwya3J>O0j;t5UgLwsyZ>PRp??dwTgn6*uEiV>s*M;|w*;~Tgt_#bZBhmVaQduvS+xh`N7VVF6WW88!`(wF#y3G5g%X+aqcwe|vb6_NHD!D=8Tz_CB{_0cNH!KhK6S#Xf_3gU5wA<b=57r$#<_Qnh-LuJEVIHhIxbu9O_NzU)EzE=V;hr;iM|hp8<+4tlPgm^-uT#}j)~WZ>>K);As<yLEtB=?f9<SJ3#uskK%X0UMXnnOz#?kU%pM=MU2@m$MB8k5{R=ACS;sxRixAC_;IaPQtZ;!FB!h?AWcji#v&Xax22Y4_~;BF!PA^u*8?4Op~_*)(?7H-GayHUo`ayz~O|ENs+Tjl(<JZK;8lp7i8zuNre&M>$Aw>(~ZWF$Unjhxq(2kXf479%6^kNqtBjO8}|0q;06I*xTY$KU(1)Q>~8$7G-1x!a#t$-}~9HQE0sv@Q1e8F=@%WuD*HQQ~u6xSPM!-#@((TZI28+^c+0`Z;U0>;nx>`8;vH!P|cQAD5SexjM06eV8XZ3y*DkO!nvAo&5Hb-GqB*pO*To$H~6ko%XBN5x(aczyI-Tg*)jNt?}pQ*g~0ay=mw5QBuFg44H3zs9%0zk^kKOAIf;all|npON?49?F^*;v_;a+fn~Bk+)RJ&oFsf$iqBoRbNd;I^O!Nx&k^*e(Qdz=vE$ujy^k)_zFSA)HjcP8=qvH5w_nC<s_^)c0^yTnKD#r7yUj=V&rP)YM&{?dQ_=Aq*}y+HoiC{0@~E6&tDlnf+x#o(XYP-y{eHgvobXKHiMrp*d|UT~obQu`yL(-!-|f%B@BdnO`4Xvrva-DIxBYkf?WFx(_W#;dWS^`*z~{+UU;6#`h7Oas-5^|5&6oIGb41=ZTX--(XUhC^ZW3<iXQD{vr!!f2Fh4W$O2RytpK$kK>i60%{fTG#{c-2fKJ!x@XMQdg9?YvLGOyfq)VJearMv&W?ndG9>reT4PGa2>8LtHImA*vU?@&ql0}tjyZ<!BHDeZJ1Us~qLeBMtx1Lw;3(Ss9(zfXNTe-^VJ9u*$UlPMj9e@r{fEAMvZRr!I^4*QH(Ap4AyCfx2b-VoVm;w$cz@wNL~e>q1i5B4{>vrTw#zWkMQ1Rk6(@c3cs+x_`TIY%rH_Gh^BlW@C#CN7hFJ`NAgg-1DG;K8{7cWR86IM}@6g5>R%2YH3%8RMhvKg9V0588((M~sieL5<^k5FVT(aA(r^NSwWceD}eFJQkjOWPBtJv3DhpO)efEjptO!S1k|XY598LK^}5W@)OI0Jmj3sSEKd456Dl7qxCI!27kQAub=rZnJ0}_$UJ;Tc<f;I8-DwnSIInFPyIs&<b9nA^1ZM@xOe7+?0e@rzU%k%5bcb;LGrZ5kH|iGmijaESIT-^DC_qJ;mLkQOMTwtoU~u>6XAW+<-2KoW50c;iEwvcPk$fqj#c$}JX3h=L<7kKPwkX_{$}Cvz7=F&&7UFr=O2W7l~N@i9+@TkQq~EnZ@=Rj$hvdK2@ifJsmu2iJouf&@|nVe@1vufYqO*E6CXV)<GzIUZ9boCe^(K1zc;-PW|fAy?PtKZ(vJOJYr^;1)-wHpyO(?+?c49ux%@t3x&1zcC!4_S_vTLdeJ0*QxVvqdv_F{qKa=|Q_o(B=yCdBG9tDs0k3Kh6dx^B4m%7*Qe`z0yLxuG+AGQfkjCrNN=bO4qetS}QtYN_me*5lL*@wRso_u<NoFl!bOTJn@P59K-{yb65hRME>COk1CCf_3}P3CQN;p(B6WL+%zP{zxl{)MmQyXN35*|)C~9=mpjyl=(1(*9uh&CWu<o&1>+pB(t+O|rfo%a#4}PM&+uG?|}W7x-~-rwDiJrAnM%Z!K|{PJeR8&i8rYUGlrc_Uh7p>IHwjBpOwgbD>-fpL?Y#i~RVcRFM6l(c*oPc}1RPc`&bR{?<%*@H@#e))72dUzWF~efvAW=UFlj+m_+=BwtE)gWL7ESk|58!Fq(pdqn&1z4}f`nA`pbd{DIgL@xQjplJJ+J7deduPeX*SRTAD+?_yuyDoamItsX57nV<?pF`guf0lF5a=Y#<R}V(p_eRP33b<XraCbV~?gP(B-X3tf55SXuDO0~*!#xph>%-#<&-pw!uLqG2z=QJ|?j8^x<O2uD&*4En0FNJ`ef!<LiSIjj@ZAk}k4O8XvgP*&%Y)w~;Bk0xzAuvV-T78{aE|xm_o$zQ2YFWyes_Wgc^BNdAUrttck;UvJUI8^UitHp`iX>`@0JI@N5P$n=Og_|q>=~1ZGS9}SEIiDo#B^*rC}cY&Hz_eoR7pu9pv|@X6Ga0;_c>l4|tGA!QBy^_xtVJeXq(`nJ4hXneXKsKa^4&=H9%oS4OxiJlH39$Ud1IOFNtw>MMTNx?6a#e|ET9o_inl*+0D=cgz0yB<*t^sVvT;r|7@Ue`ZMj<ISWU&XGi`RR0`_&7%J{f8Ow|eDBPq{d+%?^)*Y*cgthFE3F9g<g>IxewFx}<X6t~!fk%#&6NDgeS!8z7fK$r;ql@yj}=ZT2=n-h!fhVqrIAOyTBe;hdz6NG&<;FdIp?xBPtIlMb^1>}=56ZgKQ{)qd7yVd^1%3VIOn)GP0sP;@@U+=PudlSxs6-E3mA9uN!7EO-+p36bX?S%dnL|=(Rrxmz7yeg9$K!}&`+CJ441sZf!lo5%PyAwyhZ=XE7W1hE0P<9I~@vTeztUXg?XaV19@TYzRh?|87TYz@xvuyo@mi2Kg{C^IC+bgHe1HMnE2T5g|>Vzl)#JLlm4WV@4>zN)_Gx`+|T>k{3lEDpZMW2{cLlxILw27!ebwliNoikO2RydgXJIcT=FaRG5OUOaQnUUu6*yfKk;7ndnZ%Acif+OFZ;byv6JLok7o%dUrIb#Uh?@l!fk#PTdDJ_?8v_^&!5(6ORSDA(w3^y)!3ZSKP?+*{;dC>|7rQI_W!4UT5jL5{eSvT%Z*Z$s-~?9)<BzKujsyguWc9J)Y--LK_%tJ=b<mr<(0YL_%7&`x@?oSe_&lgY^}B}cyql5zY@JbTLoSJef%Y8V<nUupO3Cg9fhxeE}<+Ruh1*$PYJ#<dJSdo<4e%yeb(@<YhafUHxr*<iIa)fuf)fc<>7xNUTbLUAifHEEoHm#2hnCc*3$M`n9-++pDDL-Yy>y&W8;0A=bWb8XcOnHp>Z+#41Op24Ek#`@9{<Wo#;BctxDROW7SiHy{gN8&~^ZC>Kx#Duaa`(UqW}(<yE=g_|E7Ry3DMz6If?h5xfvHdKG>JdWp6R+TO#PXS~PtA<B)Pk1o%%J7O1L^Ql*ra?4iGpF{Yn=v9=xhd+ci@3V@2tb!SRR!QtCVJ2Q@iI3qg;m;DURkXDi-yB^?*#Z1sv>A^=#-I>ZiE&C2%OdW#%)HMD#=Sb@k)+&QSJ3)uZB6l;L;CMrn>Jg*n}(QKf){CPfp3X!$-J_<h-)(^GvF;kth~01wY9=$pj)9g;kTljQMLuY32pu=YP%BO3~l_5klw=e25nctuMDwr@Fw_oLV5$&tzilLJLt{C&CYY9Kf!NDe}X=x?I?aDemgot2lsMqt+4tjzp+wX{+$xP2>q6}W7-Pvty4rBzK%B6alIa2fbOd6X7LQ;TZgnMJ5QZ*=(x7SO3JfBtbpep#%H08eL(pKJkx4Z_5wbRHqSC;<?t_{*K<#Ocvt#q-v1{hu`#|CaavE^efU=Bb@ZVWzYlHVyN-6&!7eB6M~R`0qh;njk1>w*iQQ4k&GkvGuh9N7>@y`SQ|p%6I%rGR_B*Z{YikOtrL76<DsA;(j<!p+wM~(>)3nv({!H#|9BLySZghLvx*A^#eI>pvb~VqrI`qt1v}1HCz9#0-7l%6bosDmY&qN#F0^N@IeTH2IYe5{3VV0SD?Yc2$nTg{ktf5otH)djTBDC%-Gx1J_)~RJCR`#4UW|=ud4R1<$I^$%{TvOJVI!%eaIipQk6Y4Z(EWc7xR*O1Ki0g4BW%a02i}C(kN!eA@smHjPar{_G`RD34X2$DFC1u7eGvj+iNtrRr%vgV@q|BIQW`2FDq|BIQW_-U;QfADuZ<O#<%IzF6bK@f=<=?2^*guu<G|Fo-j}5O2GrD$)TpQgfMXvu_>({k4OcB2uZLAsP#{Z~9*X6#3_-5!gDcg;2h+eIvY!7}ndJpZc#@9wKRr0JocvEKdXl?x||An&U_@(Hj)G<0+TR&~{=yyfl&-i(~^E~PpeY3V<+Md^TPFsqu_cGqFmnj>D&f=ciF{78^pGW_mvW43Ig<poh9eq9Z2IF50>4jV`);1D;k?zmW@SiEObq1qdZMQ1<2KiP=?)^9XE9h6KWAq?x1C)F(n0(xPBjn)?%cE=nI!D_;B{`}|Tug3ez8!vm<>LpUM`^oFNj_=vHIqZWgkOSQLLH+!a?cRV==u01=%JLEGuz~z-@(6w&BqTx-=b}VlJn1;Yvv4m4R6?Ml#M{&!gXBRP1=TQdrryud~u3!<Da9>bJU6B%{_hbeb6^j))?OxeJy2;@Qu+oQD*MHL|b!ZKBdL?Mqhz$gztmy!@Wk=(w4?`8qYAgHf5dZ|8kybe1G&!=xgzv(Ve;1=xVgp7T+12PFW`<YtyW=(fEGo(df4LPUueDYjjQ8is3t<Qz`4EWG$O@nT;QY&PK=Zz0ke5*XYY=D+}KXU7fOaO4e&Tcssb!4XJlMz8$(AW!;sm%kJ>*aHA_xuLHh2x;|ysDOuNMjgG|MiXMsXfWHoX9rqetg|;&B*P-iB)<wxaVAiyYAAokznfNZ~F5GMM<+ODTz6<(N%DO7qH_RR|2tN=#2z?E{E4nN98eNsP+TgpQ8&K9$$v$KDj2!%J=p1w#d{1;w?lrnHZFR)=ME{Pm9!mC)9`GJ;qaEtqfbW5BudN2<X8$pJ$x!?V^icE-`1YZD9dupV>4tBQPNU4M;kc50<Q8l=b%s;k4PO`CM(<ZOQsn$J{$lig%9i5|GuoWVCQoRCuYq1o*?xQ*^czab-o@`n*Wms)s1s%;7b(U}nPn$K+~{rE-o}51KZ%~MZML?#=viDFJ(FvrpW*sxZBN0Tf=`D(3p3i|+UUP<{iL=z+Md8ahBp4MA^kYlrv9I)YxJMEo}ldy+H&z@(T3j*GkPM|Mo;GYPHp$X?uAc)Pl6dehHIlA;`$M7Q?)&SzaMS<_z*Ysrs4k>(o?uLeZ5QDIP^VS8~q^HM*kPrxxAyfew4Om&^HtNJMeSScc34@&p^-MUZd~R_Aq@I$MX%#?w3+7{i6TvKW+N$&r31?AN~)W%HA3M**bjZNZnTOBX)Mb3g$NwRZjoU4BQd3TGhV+afIlv'

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
