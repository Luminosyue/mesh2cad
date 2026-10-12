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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/01fe14f50de443e4b11ad1fe033df666/part_006.stl', 'relative_path': '01fe14f50de443e4b11ad1fe033df666/part_006.stl', 'source_sha256': 'dff9c836537fb55fb8ac164c887709d9f148fcfa058203e5fbcb72c134b1c425', 'input_faces': 340, 'input_vertices': 257, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0014662055764347315, -0.29345273971557617, -0.39995166659355164], [0.4114905297756195, 0.2528783679008484, 0.3999682068824768]]}
GEOMETRY_BASE85 = 'c$}r033N@@8pn?iEmfsLmDW2!CDc#^5!3ZvQ8hFrhEUwdQ1g(4n%!tkk%S_OBDW#tAt8iP_X?h%QpDJ3U8S^2YH0LT`>N;L-+v$HoZPq8TkmD9|N4ICclSMapS}0l_eg|xD_zD<;U9k`?E2%#<<%91QbF-kCPv4`508wFYdmJ$<Wfo{;ps=#B|ZD}2n{c#OjM=@L`BC%#s-9_0c~S~0~)FUF=J!nV<W~485<iFO}=x)sJLj&#|?`Z7p)x!HfzzUq1wEDLv_0PKmL^0x?tPm+ux;CM@-pFs<t&*=Uhe~$zHjUb*_WKD@x6e=-7Fy;G(g;qOw;Sox5mifAiPXbZoD&@Up4>Blhkg3oo16&*-&=jve>ro;S5mWbcldd*0N(pnN(Vd-Cp@`%}o?Ua`pBpP@U}isRT`=KhRe@673C?oacR>&10duU%kj-<rKG#lOJR-sj8?I#%zeoi??9mc8x$wA04+j(&|#iuUclS?2QQ7hGE=uH)BsnW7(Rj_Lfmua{#wzx0l)0jBe~gYtHY_D7d&5Po)Dab3DU$=?2Z9dTVs#yi=fUaPaixK4Cm$X;J3vAuQ+|7|a)`20bMJde`fVDBlIFXqv?<4TV3tA1Q-oJZZSW3SKSr$_e+9~_iyT8Gm2XRoirQFZo-<Cn{c`SK)n<$0IhpS^mvtC)8+`yl(xeLfTYACMs0>wYJD#hD=5JAKBu#qscoS;l$M{V4WwUUYx^k(d_+^J4q<w_I_Yc4v$D+(m)B-lWffKOe~Jt!Kg!;YS2+HQm3`N3oal;;8x2QQ?Cwi1Ac1Q^maKK7_raI91Gxdg943;lC?fB5IRDG0wVwz}_BTD8|{-zha*7Th55_v|lY2?RCG4y}M7bXs>QOn8(+XzRNgny1&F;j+^w#dzDU!&r9TSQ&I*V7q$HAjbeQFg^T&p{fq29e};?sQjVvxPkzMr`{Gn?FMTR|<x;9>?}<+OQuN1pMyy9QBmRub=-0y6j6Y*+?+$Eon#VbNrOS(Vl-`%<%`3ljxqr}$x2-&s=<WQTKlZK^?<<ocywb4=?*oSd#QM>F7xs>_ynft|Z?f+?JKH$^y6?_jj=%1Is&$I*<4&TVx}VZWcw5S~IW8~W(ctzR(|Hbm%pUum)w?mjYQxL<!k^9FMD6TY=eqxrz2`cwb0xDekK>6PvEH0fX=0u0{xo}~a1HN27w51a+M4&##9(n<(mV1diFK&7bh=$ef1JIocADFG9>>W6yG{Fm^!e=deL#Nh>Sa8hZ*(?&uF^1r#|PtS^)`&B?kAKJ<Ke`3mhc!)`*T~lKgnIi_1eN-6YE6xi`d&w)D`Q*<Dbnw>GQp&^)LNGc)9-JORRs3*Vn(by<GnmudjcLm+RlNVTbs9$Gf?v@z;G=u4(+GS1z6A@ekwi*ZuofP2+F%a{P7Qvy*B3OL#f{k@@Ur3|lTL_Ep`du$TL)^56>hzjEz;#_`v^A3Vlidh7UGy&V4%?J@pVFUQ~N_5G*V=d7ruR;)MPr@H@r`Fi7hst&Hk-gojQ(I0$Y=>B>3PJCZDhkei9(?{&*%7sPZzSjLs_G<S<;=WdHROaWGCRMq8%T|0{(wCpRU0hdOgTpSPugKm#r2b*!c^p2);=WM#)G08wclffm;d#k6S>b&s`8V->t(J=5=MCvo+1olti0>D7qw?%Gb`Z~9p8Vyaz3wyF+x%AW_gB~o{ysl)CQJ0=^G1AK@Jc}NHt~7avyQloz7BhJ%+4dm^C(&Fb*A}}ehYg!Uyk(M?9Ya;GOk<Qf5%>b9ynTy=VAN!EynrP{T}vme(nCN*zdiNChF}L;<|KyurEJ9WM&_A8GSB$+v;6MP3M_*SF9h;u$1$r_OsY4SCjeQ5sL=!eHQ#+o2W|%^L$BfW3OHw%=7hT6#I9B`TS2l;rWt2oW0U%IX@pN^Vt_2J1efg)C&GyfOp?zZ!cc#HhL$#dbwG!@jMRM{?t~t(c9paq72?2udU+GjSoo{KBO6cUrTR0K0usjR>(1z(Yy16SI4$KW;)LwscFV}*L{U$X~ubXgq|{8uaZ4d>{nLrPD}dA=;b)5;la7yyrXvE7e+6~$Gv&!d~e=%{-p)R{>X7t3MwA-=Iu>;<r=*{o|D#p<<&bUiG9#HxZWjkT}OH^6g54FzsIFdTq*7gwWxib%jg%gcTDP#XF5-T&o<-zqWePj@_zB8+l9Ap|K_;pj}Naa=~Z|q)|K?`ZR~ABd0pw}fmgAvJSV4`&tH6p&u{VS3!O|}ey*c1<d8S-u64m>^s+zpC6nX4dFR!c6HWb*{l8Vl?aeE@!VZb?I^eiuTyOS8Mf|;K@wTLS`9?3-n=-oXVQ=33`0Re8*YDGZx0ibL^R}iM`y<zz!(RG;H?MT+d)VmZdb35P=X>*>O^?Mow8tDa&5Qjre{sDfe2dDbjb6@+vM~LS(JOMka>}}lUSB`H!49uJaDRfaKMpyMue5TR`YC<P0Wn`T-=9tMBKJw@t^1_()_qcX>pm&Hb)S^pdLKz|y^r+%SnebJJeK>&J+bCxZ}U>ZV_u}U&WrTcd6C{aFC{$YMSAPJ=>4(Gi{j7UdnN88i`VZX_!9S##q0MGe2M$W>g9a|U*bNpczGY$Do2{eS?*(2FZVI&t^1hO%Y96G>po`nav#$_*RqdUy}pm7eZb@FTP&VS<@1T|pJy+hPt=eZ=Ih0JmfpIarMIqU{XCZS?C8zE_fj?nZKf)pe{`S8UOxY*-|uF>YW!kx{3Kuep2acf0DEWXOmUtX+j+dDce8h7Y&W;heOsKzedios#|jtwapmL1_5R7vIqJ+joIg5V)DzA5dpW7{*T!`#pHHk_KA%W$eLk^z`FtY1_4&l=<@1U3*5?zem(M5mD}7A;l>4Og)_qcX>pm&HX`c)={Z*r8+su{YDrqCDrJUlY#6%eWq(M>)JF53TX$%kgul}UbJm`)8_fHxJXo|Ibh7d17h|^KO0PoV0uVo8Dyb~clf)Jlah`&dO?;ylC5#kF7@ln)W;Qd;TYxx!-{sSRaN^yvPM~J^ch(AY&(-7jt2(c4&KR8RvDJ`23;!K1%7a=Y{h_55WKOw|75aM$P@nO^~@IEbhTCO0(j}hW02=Q+SaUnvy7a?Aa5PysiuR+}h-l647Et?SH?Fg|OAwGi;Uqgs*BgEe!#AgxWL#R8zIa-cs`5Gbq7ef3eLi{U2d>J9$gAjj;5HCWASE1&Bw`n=4Wg|ko6(K%|5PyXbUqy(2M2I~I@o9wEg}M#ATgyMSTtbK+A;kYih>H>8iwJQxLc9VYUWgE{MBNQ8(sEzR52!yI_#uv|{$k*JIHvl*z;|&>^%j`Um4weJ0;ix(0jGecp$37cfm@=g;FjRpsLz3^`huws$>_%|@B-AS;055xs4c*g!Oc<q!Og*cLoEZQS{^)4ONN%UTGne>XXwK^jLAB@{s38vF<guH{(@u}=7Z`6)C}+ja3bnFa3XjT>O}A)@H+@`4=p{lbl38Mmied?P`iVvb^}iU$D{TD_rN*h5#l+h^T6|PopVsvf#-ndqOJ$8N1x`RP5@89XAnEIe4=FrYASdJc)FJ5S`xG@L!Aj;240Ff9XuWHC8i%AEia+I3VsP3h}sYw2=0O!4ekOSgE|X52JAp);W`q~@3E*Kg2#g2LX82x1+I_U2wWdr9kmv?Iv8J-f=erW4^gd+S_@no+!D2s^7MWro`xEuJiUL3Q&2xtp5E`oMX1Y_r~3o(ebi;(`{0MDOTiDp_fS*8_rP~iKLOtbC!@{+CxfS=MuVq<Tc9=sw*dR2z6$mSmqGOb_t!E+%P{aeI3BHK5d0v#HVm&(n<&&U@cUZ&X&H_h4(^H927~+II8sY*_}+Mp*sdj1O9a|P;Pu|%cTq#Z!|_=oPzQiVfJdSZ1djxdLVXWB3OpKh5I73gI23&wiq8%O_d*Q=%P|^_8U+s4(h=j>5o1T(PD^LJ-Wjh2W1MJATA|v&!!a&$3<rZ-p-pSlPT-N~_Xxaq1l|`3jzG18TjRYUsQ&<mfZL${9oz=o7WGYVTW~wn&R{vFqtLfe_-s3PC~6dV5Z))pDj3`k*Bp-88XOKDfEofG03L|i2HXaH9f%OWhuRL@4*ej0UCY~A0#G}E1Hg3=;-(03UxYXg^=)t*cs4>j9`$wbcyJRfub|dIeH~l_Tn#k<Tn$_WwJx}_mKU`6p;iG`K^s4W_%+m~;Mc&-Ft=1YqBaFL#Wl<IPIVG$UvOVszkCKDPDGupJbh*$re}&DP?Jz+gJ)xmk`Ur4s7=6Az(Iy_3_^%ig!nmxxEyK?a5?ZZsMWyFfS*UL0<MDbC2p^!tCo7G4Z!ulRT1KswbVpyjM@O)7(5QOD|j6EBZN2>wLLf%+y^0k10k-1S`S<Y{32>qa3$1=s8zug!4*(n23G)=HC$U+g!oy7pH->S^J-|fQa*mA|I>fLeEQ>{2L#i9$h5xG{A&*5J1=PG(tqg@+Rc~xqJ25~h=r3tPbbP>G?fy4'

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
