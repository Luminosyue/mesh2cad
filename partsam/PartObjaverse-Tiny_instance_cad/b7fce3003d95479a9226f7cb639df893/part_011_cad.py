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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7fce3003d95479a9226f7cb639df893/part_011.stl', 'relative_path': 'b7fce3003d95479a9226f7cb639df893/part_011.stl', 'source_sha256': '4f24cb13192e6804f20848f3183e573ec58d93a03dbc7c2232936d1c22e513ba', 'input_faces': 342, 'input_vertices': 238, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2025514841079712, -0.3890073895454407, -0.3699715733528137], [0.21507757902145386, 0.4999997019767761, 0.39479395747184753]]}
GEOMETRY_BASE85 = 'c$}r033N@@8pn^h$U_ZLs@x>i5TTSvV!Fo=p?NeYYG`wVgfs++B!+5_sY;O|m1igy4KXVr5|W&ZlE^$sD6W{QXtl4a!z=a9-uu6A_dV|Gdh5Nr*0=t@`@j2qd+%@Wea_8Y@%L-cu&u;iPSW_PaV<(6C5eQC)K-cL3SSg5Gbo~0*n%bXq*l}?FRok1P8{PurJfWeEpwd}6fra0b%4QjP_UP)yTLVhe)yvBz_5V%;j@B>KQeG`M3Cl3%n4i&q`mL<Mqe*?L*MT1hUJF;@zsos!Q)YWI?)@(45KFM^!PHP=%*&+ioUt7Df4GGE+p^edrxe9RX$lR`j-5&d9-~GuVmWJ`w?sZ<D^`%Uu8*~B745{RIRk}F`nnz!{_alW^HoCaVi1T#rAyD>=>K&eEj<M+~@7pkViQ-^P1DBMD&%h-xr9!veGY`w!aoieRb|<W%hh!?~ZaCKhmM{Fa1I1s_prPg_)N{Up?elWv^fE>+@TEU4G?Y<J!OSdB1X>^h|sE%IfR(mE`#j^_BFn3YvFZRHZ%NGG;`r=&OG`yJ4?A_j!A{gJ-6_`s;mO2dl5E|8qX-p!cnHfUmE=-q+{X*Pr|P`s;n(ui^5L44UWQT$)EdT~uk$Hxxar5q-H`Zmqrc+<&h9;rJ_d+r!tlSK2?jZm&J}t?ds@RqdTG?(5H&>glZ7JMVhmdVb;S&%55Yw!bzmP2A7?{-gK#{m1I-?pJ!>+J2u$n!Ww6_xXP2zJCAfed~EqdR?%$AM`%2Klk<fLGM4;Ubi3gzP`PFKj?klUP+&nBCaEUzHndv+>xeqO%m6|dY|FG{{B;7-cS8!sYSH^&fdv1?+^F(()TyF7Shk1SESSTKQ%McdAYQyqV4vk(Q|0-xO=zgTT<7u`>Df>9rXI!FIE#ZO>xT+ee;aAm7;Gt6}O${iHoD{<!)!QMBj8`Q-zHm6t_hjzm#(;k><bN{WGe^m$H6~j^~QLCGJRt=u1y$ucdjjLoN|D+)ZZZ?SpBnX}j}*bY4=@KiRp;Xh?n4&-*gHZf3Jw(U*RISZ?FHKVC}PA1$Qwm6F@D=T=f~v{)ZYOOHI!=k>ArPo_*0>uk7I#r$5=Bj~>P{%cmxEv4)^o#Pi}6xPvDUVfJPacij0>ufHW&hm_Iy3#1rL9ObTO6yS4ZjDi>gBrbw`4gQ#F^c1v^fvpR<UF1F(iuON|I|qKyz~p(O#R)SbexK@CHvmc&ut4mx81|&x=7vJ+4wzn?Gp1_+^(LZ^LLtS7V}#gbz;wtSrhge#X9qS`}>-`tPZiXz4S+Bis;Khn=5SmArAY+amv|sEPv?2{o**~W%cMjl#XqSw;AV}czTYc$DIy}>!R+AX3wG1iPV>SwWQ-wR^3Xm@%uPdioV=u*dbc~i~Z<+Q@m%Ti@yBP59Ok-PR=|^$NyV2n{VjDRMA(*9Ip_4OUcTUVtot`rA*Q1_2Is>^TA1R{D!NGRU04U=e}I;m#@V7sI~2B9i&%ZJ|+6*s-IY$+r4y}j<dHfyARA9R7%^|JW8bPe?CL&Al>_}n5t#&S>hW)YuI{CuPmW?q)sVfdwD=MJqJqDo#(~&%85hl{`a%%1={bc$#lM!*a$Y>tv#r3zObC#2gY}1>(*od_2maj89jG1cC-F}kE6cw_%xf>rhQbEEd|s!WYy68%7fM{U-QwaG|!YYnn!uJ7aLdI1nMgRd2AiOjA!TT(t=d6K2m8HIxltZZR(p2Zm0E9N8e`s)T(K8{7)`Z-|}7z^ZP%fzBI?ThOSq7T!H8-L*A?seak#gm5wtck&aWU-9tY&^$cKsZU|ea7<V@Q!%@sXI+psT>=)R%@m;El^HTdYVf|KbpuTjt3BH$ZWc$r2mHLJ*Nwi<fst0U+2Gp=TDVcP=<>H=fpPsm@iglKD%wy;8U(eWhR%OxsVCs9Iz{YneuCnp-N3icbzfPskO;dtLhUiOE6N^M&{xmRyoyR-0o@VEpg`#gU9;p<4)jOI!rx%@L`|M&lyKk+RGHHG<nbpn372|iLzEa;mhvwUrlwso^^(+>BOYBhQf8@r-Gq7u+=&Q!yD$zFt1hMvShO+uS?v^3?YHdQ9=*#dWKil@)SFYH$H$-owzGbODotM1b!0uZYw`Gd!E~TEM_f^B4f=qFJ4ZSDO_EP+h%s*Vq_R|-~=z5xeead{N>TKGt&-dp=UphIUMD#5wW3$BdwPcwxMW3%P_YDQ`abBc}?j@qn&kOg>>!PTy<}YUZwh61Z<>~4yaUYsnA1Jc%u@AX#D*Kt`IaJ2Z*M)U7pV{lTEU|9#<ZZNWYTXOj;`x$a^r81jbyy4POCgi#e9h+Y4AECc_AU~AX*hgcd#mqj+g^2QpDm6@EtpK}CU@;%GakvSC7p*7V8|BFwNe~T*Vo|U!`i3CvVAwIMTY3hS2mW4z6@VVXYDOIUqyTFt4<1Q|A!YlU*jC<K2k@oXZ?mHU8Lvw@rN0rFU^`#Xya$Zvi2?R()!4r3o~tepYBCA{{53IkIUz@Uqib<wl7?hvc-L<ct@NOeZCL5Z#MnH>d;{U+YfKK(7KuSH^~vtg~eiK_52n-&V}@WPnziSbHROi(NN~M%%I~lgn6-X4jz{yo_Fc-(InC5=bih?u6a2&`_nh;6wSYH5Az$a`<Q84%vl@%IJ=K=-yCUXzFQ`%k903h^p%9MMWU~+NTEKzubNl<%IYwyF}vP*1zYbuZtOYW;=ukcb=bl39h{bK<NHPyi@rI30P`EN=e{(r6RXqX3Ay4vG_U+3MfCYTwECs%bH(#zDX&bn@o~Pa{@$~>;{H?&r75D%_ovnGkdZ6yE7OAfB+<7%zu=qvP~W;}Iv=&wZ|r-*>~^$2{ya6+jb!u9?|xBSUrT6bI!?u5iH&dgumjz<rUq*+iswbGD@(TVabB$c;B@8(#IW%!^kvVBBTtxbPGryfgD&j;vB8ih_N(q&%jPv<DD$09vFB{CA8jvxH9VjC-z}rQoM2>mJQ}e58o8Fuzj`+N{&r~XB|6Wmm)ZA<U#?Z8``i2)KJfS}9Y1L$NhF#|ZKdEq;iqt7k{4I|KZS?%`>%cq@7wQ<|M#cxhT0ffXz@4b8(^Y+z@xPA(4s$rumgf{188$_eTht5lF0Au{h+=G!hNAl!5-+NFJcthjzWL@+WyGbAAR>jI3S+``frBdV`+e~)kic(-_6l?Q)pjsXDwdQq7(FG@L(;5XfY5v2s{X%4}`u99ta)`eFZ!iJOtVqJOn%l+6nBgMGr09pxwbkwHT&_5h{aad~Sqx2OGgdp*_Gu!NZ{L;9+1H>IUwu#p_!1g7yUaXfaZY;m{G_5%_#Kv?q8t*a!ML*atik+8aC)JObJa+*ONLwP*)z3vP?|EfIvfK)ZswfDO=gU<0@nu5E>Ut%TezTC~x^8QL1$O$%2oUV^p<x5xX|2v@Xs#Wl{t^)Aqtz%F3kPaEWGBjkQjBDbGE^E)A*6XwSA6MjvY?`sIcj=0tl`5fUB_ST}K7H=X54?qxp0YSJPf^ZY4H@J}&9i%^Bgc~CWdm#vqMiBOdHUc-o^-T~G`jn81kD)Qf)fjpCIK41-FZ99ZG8*$6jehuiJ%u@VqknH<EaZ7`MT>LLufgZQNzkj{BybwE7F?`F8FE|!e~l<ZTcV}ltKeE_5x5qd2Hg+-5`CmYuYmVyk*dXR=vnY?@E6cC;Jwfb&@<o)EpBOX4V<h+CYX5T@W}fNXgT;FS{&74GxUJK<g-iA!{AF`3-lt`0=^9`0Tayy-v-}+9s=J07eM2{1>hsl&EU-#C*f=@PGh`B!3UsO-~-?z$Vs#sngy-~mm{)JpDg6cK%7P`PowW-L^f(p^fEXTTmiict^i+$-UnX?--6x&-vaZsyoT{!gU`o*N2uE!)b$Q>@jBnfI^0L!d|mEh4ew&Cd`$^of@XuWQR_>X%XN%#r4}o+NI($Y2weq!pv5CCzR{uvdJp;tyjqJj$hQ)_0{Ss{1$Y&L@H*&vFwq$BI`CF#Ja{YkAcAlX^c0wAAvgzIgDAw<iPnL?0Y89#3w{75^E|J`7A^7-gkv%HotW!Rcxw=`m|rZ~e~j3IxvmGtK+l6?!10LlnA0h6Av7Oc2<BraS_#bu=VKg|(4Amai<?^P(qa?z1oS5O1h@)8_#xsZ>hlPE52}KR=7H~l`C8-&Ym|re%)>Q&eF<-c?gI0%^8G-V?-{~;j}hJoJptYbPJmW{S3*}K5>TTAwAqQMLfyWF^0`-{9+hZAc$*exEp{LXABTPgJ`PTSCW2GI$Dk*{$H3d6d%)YlpF%$ee+pg;{S3SoyaBomybWXBfbp2oe<JuK!i;|QfIml=k<W}=glA|GqQwLR;Q;7dZ~!<E8UzjmPr|i+$TtH#8TxndWbjnzB=98UA-r6RkF=PDAUp^933v{8K2!nE2hW3k2%ZNHM$Y%p&vNhw&|q*d+7n)=MWhxH2*T0OCE#fAGU!t9GH?`hF*phw4qXHe2fq(p0Dd1l8yW_l4Gx7a1TVx`LouF6^uH9m7!iqn7J(NaB9Si=xd>0x!e5Ii2*Tr`W5MIWW1w$=$AHH{-v*BZzXP2Heg|xVz6&;iXF{ig{r&3IZ`<HM{Y&4UFNJ==7XQIdf2HluAL5lQv_Dd;KZf}GH6q`~wLi$~(*l)|zk;NH0~JA}9{'

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
