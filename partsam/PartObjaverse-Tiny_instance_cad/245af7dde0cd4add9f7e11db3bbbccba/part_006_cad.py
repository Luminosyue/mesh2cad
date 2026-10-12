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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/245af7dde0cd4add9f7e11db3bbbccba/part_006.stl', 'relative_path': '245af7dde0cd4add9f7e11db3bbbccba/part_006.stl', 'source_sha256': 'e44f4363f8178e0b0dd48f9e73dbc8546dbe20b258164441326a03e518972f01', 'input_faces': 380, 'input_vertices': 253, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10651209950447083, -0.2746242880821228, -0.4879723787307739], [0.10651100426912308, 0.4950055480003357, 0.22582541406154633]]}
GEOMETRY_BASE85 = 'c$}r03!F{W9>@1!N@YS+u8QN4L6T;~VB(OguJKG6q|7u%-f3o{ny_gwjKR>LybgLu^6E;1IL2rcLgj77+*0(SR5y=tKX<RSzUy@MI_G{q_jB+0eEy%`cmK|Rt+mfu`?1!V>6K8iQcX*J>RItuV`s<JvMdo*teV!?)U=FYDXHnrM~`_i!m1{H@zFZ3$K&05^^dT|TA9&<Q`1w@qT70+<A=mWH}gafc{VL0EqU~yXVV6!3cpM8$n;dlPam2*Ce=A^9P>bIGf!-jW}fk$|M7F9a|(7+=dC-$xnvFBE!6u~gHoYMQy-GPzt%>#|HP6lLhWu{T)yY+Mbh^_f7s=hl{eZXkH1WnzTMzdc>m(?5?Q{!^6jDTx$;AN@_nAF()ZucN%~gLy`|xN`&y>VPZ}Ae{M`p#`KGV)y?wf@mB$T}mH%_w)8Tw;U=>%sHQ+(j4{Pg4-&)pL`u>Dfu6j&AP*3XU6;fBnN#DO^ob=1qw3ohp{Xpd}E-MY|uN$KJ=Tf}%t;H){`5`{}-gmAomwv%JB^|`L-n3z#Q2*3rKACs^&?#~3t$0ZKR>4r|TMzhTe%YDLD!=cID!=mqneV%!z4Vh>M!4!px_`CGzv5da+i$&4wfjmV>3jFTDt&*aMbfv9<f(e1@|VhXKUh^NkH5*1zP;zzBIzHVC4Ju$^Q2!E*;V@fDY+lZei{)W```4fkq1k|`TiHGmxS}ZrCF!K)^oh%q|2X}Tokrl{E&9>L)yg;X;;@nyS@|qURTExRR2Uqs(#4dqWmtCm7o8t>d$c_rSF}WrGD>QBh~$){m9`(!G2klwhLuFd81VR@|e@XzBgl1QLyi;dSQV)t}sIN+qNAg!M>gUN>Q+HUyPkE^Jnx|<JIb%%eOM~i-LWxbtPZwutZh=XKhMd{^A8iF8^OQ&6Ro~^R&E9cJx#I^G1z4bszQI;~Fo+4~&=L2gb|r1LI}ZqpuTuD{on0xOTN~wyS-!UG1Cg2I`?*t9#BIHSQl229K|OW}5ON<Mssm-s|s|zJ1r@r-QE_d&;?4GH*l&<wt$9SKi0vyQFWA>m+^u?LE|e?H#1@v#u5gUnknPYy4X1x~`gC%$3KvzpMO<>N*Md<1QBlUq49+vC{WmiFLof%0J1G`O}MwgRdX$TQ5iNa$Q#kr%2zPyR+DJ{owl}@7)#bm*rQ@mVRQQ`#o4xS^CzGOI^OTam6H=|8#|uvR|xB^<2fb=UylMvaGMv^_jVQv>L~yvOn!BpUHks>KiM4|Fz}P_e^Z1`Z=e?U|G*Y!wv<v8}L6LwLaLl=T}OR_53~ZplpZtqv`ASqxP++@=f9LwXgGi%a0{XfAp>UrN6ZC>2SV&ZwCBI=eCB;$JhD(HEWV&URvEx<#FDD(y%`7(|~{NJAc@G?dyCiZjfyE=EUOQehc_dZ`|b?_sJXk%HwwP4u$irZ*$fK`<~YZJSLC7x=Hmj^Pdo(`H%Lk#IHAn%MbYE+tK@aOaCPO&pgER^*kitH$A&GY(9P<Kl5A<slU`v{mgtL#Am({@F)E451X%j@;$5Ky2|4Yk*@yNzPClCBG>(1@BNPQc-s}%^W60HbJg^{>(q1A^!+uboC;eH&((nMo2T-5j%nZj$AH3czIE!?o#D<?`{sFS-#kz4o97v*N1tc)F4DJ`l&arb!h0Xz8d|L|*!NCs&_VjyIqG-u9M-;FEu}EnPpX?AFTd~FNA<sc-r`$Tx~X<~ern&oyrM9i@7=nnFt{Eo_r9(jM0?M<?=S6JF*98Em#@d^9>OoHRmF9Gh4^}Xfp3lfYE!uUfKR@aSKM3p-bZe8-Cw4!?-%V`y}sQVE?@gP-&djUW5Tzes_DAFLVP{{*M4>P{T1SqpY-E<ePw^Hao=Cs_wK6by1%@`V+YB4)*J5^e5=k#*Zaj9vN}ojbG_?a?-$e8?+fi){jY2am#=-DUpC-Ka&SNE_k#8V{mgsB^aJmmo)uE$@9O4py)OcO1NZwP#3$eG+<dS+pL6c_h4%f^Hn`pw{wuZ9q(Aig6GA<=Pg3in#8~Nj7oL}X*|D=~-gP7<Lw>(~wR-P2+bib-zSsoi-?LWwW$R<qd?2=Rw*0-uJj7e6YPM>}J#X>8zEAqzvx{Us*8F%`kEi!F<-fF0&G)JwR`ZaF+osF&GUiL#x6<A7CHweg>6`O0?VIzlvig^EWd8fV$$Trx@Al6y4{U;eqVY`W8}m%<oAXRxK}@dvUB<kz?C4Lkq|ba<KMw=Gwb}KY^qu*6wyfV+N0`2To}0dYo}0dYo`=+<*M0crI>PkLb_44Lqus#z!f4lAM|h@Rn<M>uZ<F)Yq&3g0>vn(DJlQ|nYpZ!|ixPDmCf=Ga)m*P>-&n6%|45L&xgHGoQSSAir+J(CvYxg5)w*LuAGOZi{G{~lj(yera`p#xzZCo+eZ4-_*VUhXR#C9;IZ<bU>Ie7wSNrDr*MDoj*QC$-T3;stKTWN#1Mk@{n!hgFHTEk^Uyq~d>v1%FJ&qyuFpdG=*sn1CkaqQc#WzN~dcPvUXxG@U@ZP;$`gVsw@;dQ7lcLr^@kPo%m?C}8y1nZ9IltE@zkl-GlfmPweg7wG)%6zlk*X)QRQcr_<-Ug%Gfw#<e^UPJb!xvT`ewDx`XYXX{NC6%3-R?lHoN@_bw9fI<wAU&?;S0DbAQjbp!Q06J|Ewy_Sqg;ug-Hz1L=Dw)K>duAO2OH=k2>y{%gC`{@cR2svp{ZCVjj2PUTl_tn$4z-;nj~*e~nxC$3b_^OU=!??1X%`c|jb>i&JH^IECKzNP8w`H8=I7wMb(rKWG@oBO4n0a2S|{l-46=?C_8Z?39*V;|V`1MAjmjihhxGl%$k-SoZk&3)_;U+-hTx@e1R*VqrY{<cK=A^YbU4{eqC#(uk}M`!7~_UC)K{_0Rzy6tSQTbvn;6E|2jts%)le{v9}_-GCPCx>Az|EoVa#KyJwfB)pr%Q=VMPP~P_4Zj8NLW|&C@JaL(d=f4}OW_juEcz{c7XAVK9{vIT4m}5d2bZCz;WGGB^b`0~_&szD{2sgteFt6zKZ^E&AB7)sq6yj=?E?$#1b2q(pbx-8?}F>Vwb0vOp|``e;5*UUu+YE2Lhpd@gqxyG;3k|?Q?w3Thc=p0wkgMtJJH{XRCE~JkMD+}sc^azW1Lt(2!0hE3BL-@L5IR~;F)MD{F)PsotTc!glCd79UTTQp-e719iC23E;<VKQ6>+~g>%WtL!X0JQYIhGgY(GAN7LbS`XZlLKpjHggqJ(<h7<Fgc+82uP7Fqez=?eK3_2K2bK+UbE~T#7=sb8HIkV9b@FL3OptIrG<m8~wzzZppjpo2P<Yc3R;nyiM1I>oB$(ex;foH(8(BbebcrH2`o(s=M)8I6I^L+FTxS|s`IT3+g58udl*P#(`Pbb8qyayrp7PKmS3tR=g4z2=MLL=Y`PE@wkr!t;}M!*rAoA}&7nMl-vEpj5!YVggJi9#dcNOGdkTjA=IsewkpQRLJ>d%`{GiyA}^>Ja)j_!}oaaN>*;m!0^<iL2=E@I}7+CwdiL?Zj7<{h7Khpl9GS<Xk|1f`6mTCG-M(ft*X|KjABsDMv5Cm&hqcufo4l<`1+SE+^*?^mq6V_&oX}d>;N9{RjLt{4Tm0Ud?ZQ7yST!--%b8_>d4h34H{f1bfjIuorIT#69SJXbbp$GzM(}$G{2bBX9yd4SfZk25&&$hd01`2*LXZ!3WU~;e+roLa-m51pDFfs23g&KZrJiAA}nP^+h8>a6KpD(2nRma7XxI^gdYk-NS_7u7u!jgy2{-29AYWq6u(IxH~!x?ha2yH^5Wjb?6>=9sIEqyU}8F54?vlC?*8&B?KQp55foFFVJJ~m*{cy7<?SwiTdH4@C0-`JOOTxJ_xsmqtQliG+ZC82iJ$&1dVGOLhv|3@K{2yjdp}>cryAh{4irYnGl>s2%ds=gP%uRqut=vum_EWJ@DOVOZaX$9_<dt!!M&#;g{hZ=sI`@d=&i{J_>(s{dwI8E<m@SyWuVHT0-!8v=|n;7hVr<Bm{3p55Sw@t>_o9zRtE1g10&G5qcQ?5<U!{K##*G;6ijKTnJA@C%_Zo4rqJ01Kb#mh8x2T(E4x#xGmZSZVSJFj)Px-KO)BQ`-F~#x52tk#?pU6?V$d&>2INvVWC+;W04g!Mp=xf&?&IKj`dgz7UTb-6MuIi11*3H_&x)D9{ww3TA>+m205+J*6_WQsf)IPTai;2^}x+3(-5r-*CnSRdN<sKGVRcYa6@w1q4Drbl*vTf!R^S&L|=wCQD!@u31^bC9o+$cMwuh%c6d8EN6@42e##s|kHAOBIfQ-=>-+f-Q9vC9jGy2XCz72=LZ5__;DLnT{)FIRgy2zVGCT@?4o!idgVWI@I2|5?4ur?RdQB;`A36{o$T{^R1dH{nSXVBy)S7Z8JO^E2{kc9BEY`0J&^OT)@SE^TbQ!!7_MwYmAH0MREY_?~JMokgg9yP-5P}C-YHcWV2qAbl`V`zNA)-RfivQ_fVE_Esa^VsD53y!R_cm5=$+1pdflaMm36Wy0<1ADv$N`KHvm)!?o?oN?'

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
