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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3031b834ab514a0fb91e0fec151ed0ff/part_005.stl', 'relative_path': '3031b834ab514a0fb91e0fec151ed0ff/part_005.stl', 'source_sha256': '5b57ecbb005f4268d0c8b71590545fa38864cbb4133945e94c93d2c6c0e7c98c', 'input_faces': 392, 'input_vertices': 251, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18131309747695923, -0.11409980058670044, -0.2949776351451874], [0.1895156353712082, 0.4999997019767761, 0.223650261759758]]}
GEOMETRY_BASE85 = 'c$}r02UHbT8pj8WCdQU1iHJ&`Mxxk=HGu8KmMEgwyFMadLm`M*(Xqz1RxDVbprC@H2r5MwMFADmSYkz4dyhtqMqS;x-}irHW^~Wlv&%W(`TyoWckaD2x6V9#yo!C~An{){X;|BV_daoyBoU=02Pw=yBy{)?|1tGP2T!n*J|kcJ*>qXwp58uv?W8biQcXYqF+)OXdYWoB4{)zp*HkkgC?qt*cl6+(5I=w6xAzSk<FEQ-hWQ5jtH-q(Hfd1T)X252Dctlw{(Y)eL2lb5CsWkLd)=8<swhv+Y!)h)8<j15^U?5A;@EsEeG~a_E0Zt(vYyh*evxzN`fd*o3sn}>I7#`u{$r0&Y1kdTe<YZE`N$#irI#@$=y;^pUedG__M6?N^yaEA(Ui}a?d(qrxIpPrZjdimSwX%$YXaq?d|rBw&Uc<pzLc`~gTDEf$6U|gq2!z2ETsFDqY`FNd1oBC+`i8^|8l8TO8;{EAxiIkkLoFn8ZwpA&4?pk9%ZI_N|(L}CqJYg`O1Z-7s=mwY9N*4S)bE;Up`L9{adaibuGx!)qj4#1UkMm>LBHJ!X=-4m(3wmj}qe!Q2v9D76`wv?Cb<OAJv0=^O-1a-v*Zx={PY<q4X<K`F?ZKcTxVHlgO9W9ymsRrRj?(U7rB*&DAUZDtuGRz6s<vws1ZT%v7$_+{r@MSL(?5v=~M8x3n$0g|4sQM!wwf!FkGm?y{Y9oOXXd=|}NLsa;l&TSdo*CZ&-czDD&aEcJ7&&i^j;lFq+*G?m-YO80BNy=X7_)i;taJ=l6h_*R!`{CqstlCSt}rRSi8-AJbN9VT-=5pC&y%@=nk(e(>Par!yyxPK0IAzuy}n?icsJ%{eM^L@GxDfjU{^2>b5{o!m$%D>2;U-pW&9p&zi$d@u3Qa(z{L3wn(S|F!)4d(nOZ6K8<_Tlue8qu*lb2+CU@__HVYyM%X=h-W{<TrI7Uy8bYh}yB_iep@Uw>^|TavP;HJ8s^<*PrA1uIhQ2o?E$2@pQZ`i=R_K^(^u)*XMlT+v;PwzLx4ED;expH&K0*a{=tT#jt<cjpu<gtN1zh+K{Bp$FkJQ>DL|Et$of`yE%NnBY$8&zXkb)8$3Dv_8jW(w)x6jZ$LU7kFA}k8}GB8Q@hId(r6q=jh(pNr@rKNy)uh@rS3>>cayC1ZR6eMOV4HY^GC2B6P`={pv%<XC1+2*uiJi6I^Q;~ZT;j*L-yN_J)#{iMSlOs)GkW0BOkBMO5plm{f+X89G_3e72fTj`V9N{BHz~(ns=lhqvPl~1h%L9Rqlpz`jJD(m(ou0yiwqutMhvWoh9F|F0BXB*jnT(-WRS?{>>)y_zFF{RXcvAIt`9d`fdle@N=k3>5Jych~4aeQ{y1r@2y*0PwRN{l_y{GJTrMc=X0zwjeB#0NV;G1<`Oh-O5rnND1H5roc?|b_RIVkP4)4-$@Lk!nCJJ2uc;l(4|?)A^@`0Pe{CB1O7m{K?j((2zjK7nmtH)j`AbTlq)*>=8~b-9Zs&Ec50HP-o#tgJd$N_(sWkbLRnF1*AvaEQdmZ>y=Wh(<{D1uIBpnCdqVXzqZ%g-O?r`Eb9oL%4{<u=ypNGeCJAM<jp0rLqUKfXd&-EE_b~R~34_b#z-D3E;)o>?Y-tsxk+vXX`ndFzvizNNH68TcZa`r>Q$(QpglCK1IVBe<``)=$@O{%iL^xjI+g5p#k%l=qymyAO8e>jy)<$8qj^W1S_Dc@fxua`AG<9_HoeKED8Yd-aJCFnA(6O!W-TF1<76!PWHaqQ0-x`_K-I*$v#ChVJwvp+qB^I7wl*N=~)7m`kyvVwfK>bxFzD)A4}JtLQqzTM3AN!q)BpOa?<-M8~hzOTT1-Zwq?gnY%ajQjbj3|<FHhM%MQM7GM*`AKugm;UuQL+eXni^!LK4(fb)hl$ol#p;@>^N-gjUn<^7=PSRoWB=7`_Fo3E-((Eu|1aN6oj<iFrI#!3<Mft_-RU_`982?q)%_ViAL*GLrJI*e>zz{N3j1<!BRYQjPCsu*XSz`OjH|R>m`XXvWNLh=VQXHe;{Qt2`m*BA>p?`uUahZ`tVr{=JZVO{E}s{tc>i`t+OJFhb_lNvZ^~w9ee?O%yzf=!XX^YLa|=FLpWYAXzT__D=6=w39KqvWInb4K;2Iw9uIITw$PEXOU!o25bLq*$9G#DGA<v(drt_akG>()u1=(6(URajOGyhimh%UWtUb0`4q4P1H$XmZZsmsSUf8Kd<Q0tr1E%ZDs&J_;p@_BKCo~P8SmCjf4{OEZW-Yq<(OCOa(<IduKp65O53HEK{<w$sz&fgM4<4z7cnWOVDPUXr@Jijf@^(B9E6K?Nzhx15#I4suXZyS$cC6|(K9KVOYU8*g&XuMZ>w^Unh(fr`xxr}_{eDaeo`^Nd_O#=Dv%~uOOBDjAT=C{t_E42NjXg(aUaE-Q~6wROYSFO?ZlcM?d)%5i|z6|p}eA|3pG;dc)B3~KqsGsNOmEJ(<HyPH2SAOIx?aJ%dk!v+KQaa;$bZr&+O7l<k>sPU(8@2tjXuVtBJxbfpi`G;4=5jan>nVJt7_X<MxU<~P_nnK@jtlFvmRz4IucEm=hV^}W`Au5CXg~1EL+2OmA1+QH|GoXj#k|eB@nzeeqz;ay^gRswA6M5cbZp#58GOsB0}7YZk9>K_2+GIe(u&(R?dz>{zVdqgK5EFkZR8vGWANYG@3oGPqjY=E>Gyl?p4-WPewz2;j-I(%Um6xd>xHzT9`{?viR2sirSg_RJ1HORV=bqy@OyIoMDmUM<Rag=Pi~ygzHy(N(0>;{H^cti<{S6tY4(Yfui?GG=D+t|knNtx<r>~E1_W|?!~25VHJ1GM-c#PT-%ZDc_ZsPjKd%R&wNB{jS+56w=P<s<RSHg_`u`qrQkNe7d+)6_-|*gQ^iAbQaeq6OLcVmm1>f)evHadxtamE+gU$TjZRtnvpXRq!(<r^+J>9&hX&OHVey>;D*7EvpeM!FY`#_Oz_&#7hzdW6;Kk}S>^XM#k4>k|FOTP5QIrbYoBws#XVn6wrKG~$jBI&(end+qTt#^C#`+f^ooo~K9ozwSeMZVl&Ki8*US$+>LK3bQ)a4WulObjMpiM>Ys+<Ij+otJZ0>hs_4d-OxTWyNgHC+i{mTkr94(EYXa98QE~l0SYQ^#}8saXeo}%j7GGDdbD`LF{*oV83QM`SSG{NdJWM@kwPL`x(<TZhzx<9-D6)kGAhcM&Gia5*?f37P5bQ7WHS7M+g3nWEZ1o$C35*P<ro`{d2k8WP92NDqV{&5x&x|7}d-8y-OK3mG?cS<>XuI{E6=$e1G!Xi3QqzD1Ek!_fN*}X))RCw>V4fYq{e^^{~Dv;Bt4`@j94!o%65jMDwZA?I_Q;6XMCYT&l|ctvDKYg#(iKJBPOy`-gM*y*n?Q)Ax!e-}pVy^wS~wE@Qs&j-QX+F6z&g*Lmbi?>g~3uzCp3BW*5Z@pD<i?Q&>c2AA)|;{e|$rTTMcQ@$%Jvv2%9S?50chVP$>{{tRphVP};JAbkN^9BAc`gBhWwR3tg8Xvaru2TPr%ejBW^7kymcUo)n?VKLpjiuyAtLT0!KV%=@jm?vTcpn|xpU0EoJGN;~Fpn#I_m<9o6-oI#Sjyvn${XIVZoEm)-Q?iI-{J86++3z2@0(UTa64B>;`guMJbIp%(s*wv=}h&p?Dkh$`RIN{@ETmhR9IduLXDD=gB0Ma`3XUo;?JfZ{t01t<NxX>ghn0>|KFbwBGfvBt1(xN6>6+eV<9vGJXt(8QCH}4@G|fU=o;`(Y79`L7qlmMF3S1|IsiOSbPtr%A7xC&H9c{@C(aE-y*45bp)y#MACL3#I2VEZrlO8Q*MpaX*FfXJqF!B4rqK4_aFjIw+664?<%4p3P{tHo(;nyB<6M8#D+YN8oemb|@4)#TIJXh`O+y`pt^=<J$3u63MZG$rOrdSTGRo=#?Fbh2>W*@{ql~Gz&Ii}F#W^3;Yc28+Is+`q--YwLa4rV<%|ac8ZUC<X?||+Ci+c4ynL^Fr=_sosv<Fz!t1HUsiZZ6*8Z*wDaZYf68i8s=A_T97js~v=#~}pogiZnroeACvPQZO9ppFUfXP_*R?<R!c&Coco&_wVi=n{nBrO-t1Qt&o};8=v<G-w<+4s}g~CV<nx$!LdU+()wJp2TyVjkXeM1*ajMt=weIIV<wBYV!U;4G%RsKwE)FsxeB9!3e>Fph4guq#cAbLOUS@dqF#ZJ0O2Aq!HQ&A-FfR6}UI}M}*+kP!F)smf+Ul?<MY!Le0>Y;6BJV03kRK`Xe|HJQ^W*60|kAHS(Q=5NzvPGg1CbO<hEP?}m2khBljp=id$Y;Q_YQwI!}=319F^HHN9N3OW=V2@QY_1rJwaks2eQi@_tIOQ4IvB25&Ig+^=63Ec#Z2KQ5=vl@M&-rzpaPEc>~FkCYf+E-K8p}20SCJ$fSg9SPQJQz9>YP+YExc?}`DotIZ@tmSH&&(IscScw=b@fI$-kLH+9meB12~7eo0!Kkpz#{(^xUL1R8IH2tao!#01b-rljfy0Fgb-W|A-Fj7Q?RQVwbiJJ5d5_o-#}|YYlG`U-JrF>wUL(_v>vztu4xE$1G^zjLue!LJvIKR#&tD*g&tKSUyVXFP9X%}h293=1;2pa1it{kg5ChX0{;cQ1^x?sA0hZW^aNPwG4OftIp|UFIq+G8;NK8}FF~(^ujAe?L9@Y^z*%ZcRAZ|e!3e?Ip;_Q8q!&C#jen>yPmTF%{G!GJ=sfT|q!By>*Z3igKhFEZn+Kf(uC7K!No<u_zW`SQn-GG<w%Q3=79rRk`UTh?TnbtdTnb!9jnAQ#pcTOtQKw4KZ^4zoRn%w>Z3g`o+zk93v^w}Za8qbCa5dapQ-t6q2*J)!2e31^hUQt+fK~<90M|tbc2T1p^eZ(gKpmkjU>Br!ggSwp@T>)wgMJJx3;q}^LG8izc<#18!FJFxU^{RLP1}?}2ri8f{24-Ud1xhYdGMFeD&Q}{l@WsLAOw3#f48gPpP?bp=3t@Cz#-r<2*IJy@4!Nvf<wV$p-sSJ!C?}wP2(h9m&BYb=IF-Ie&Bvc(-;~C4nsbTq0V5THNcI*?g+sxpmo7QUBI?}V_P?bPJp%p2SeLH+ku6C1>T~@K{e>xfh2yOlcWOZVQ>NXD$*TM;{fymSm-tI0dNlVD)=h$$w3I-j}V*=Jp@h%ry>OJgDT*C;Jwfc@Luq4gy3AL0?q|rh8BP?gC8OU{|>zh{vG@W^cwgN@N?(|@N@7Z=n?QE@I`1QI1}x15g|Amx&@pK7HdH;bOLk>cmjAlLU0l^6P$@QOF{@vf#!g7&`!3!i_n$O{os}0VF<zFpy}Xo;4o+^I1D@%x=;Fh3<|c5Q^8}Pd%=6r#<uY;*ftLc{uv>74>T9N2Yd#48GHtO1tItj^da~G^a=DK_zCza^mnk(Kfq7He?p&w{{+882z~~A1bzm747~`x2mL4XB3NiP_@o-g)i@2#!?BN-oxMY`|MV}mfB(s1LD2oft?^3zXEp7W?bW=BKC=0E6&GuWx(L}*<M@ghU-~yCk+8V'

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
