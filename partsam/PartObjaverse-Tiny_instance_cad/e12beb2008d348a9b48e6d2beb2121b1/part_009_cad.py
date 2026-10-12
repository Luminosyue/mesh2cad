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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e12beb2008d348a9b48e6d2beb2121b1/part_009.stl', 'relative_path': 'e12beb2008d348a9b48e6d2beb2121b1/part_009.stl', 'source_sha256': '7bd30f4adc029ca85cdf161855235fdbd6127e833d51cc1e7d9a9bac96467f6d', 'input_faces': 348, 'input_vertices': 218, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.28875651955604553, -0.4295533001422882, -0.2534472942352295], [0.2544323205947876, -0.05104730278253555, 0.21224302053451538]]}
GEOMETRY_BASE85 = 'c$}r030P0*9><SlY?-0y8e%vYvLqE|s7!xji%1#E*v3DKvXzKIaWF`unvq##JBBFPT96nWe_AA!M7Ft(*$nQOG52!kTE;!^@BN-S|3CM6?sIR?^LxIZ^Zmc)J@5X$=R5`a*R^*N_+L9g&ba*kZ`vgb2f;~L7#g)8d|K#yx4Dsv>j+KBXMegT2aFjJIKGasP*~~`5;}icl#7?>;xoOEi>v4|JtAsBRPfv>5m6zb%pV*)dw!_q&kqZZ4ArhXdwTS76?=AZ6=TK!@vo6q1o`Qb%6wK9r@+0WOTJsnRKDBw0#j*A^9-iu&n;V-D$k!(Fg4w5PwCZX)4!nfeP@#|{Qfhgmt5N~q3fk{%en8fkMe0cZ8vGhXJwRb@sE^`m^eu$|H{nsl>g)#`zim~sS@SC$A$Y_Pm(X)t<Lsk<?-)GzC1DJ5NYnRX_W3)sg%;4Sj3;Z#DVTpd`6Kkl;#!Cbwux@bnWr<99=u)Q+cG*4|cKq)!~oHm)=mwH$8c<i_))b#QjA#a_GLUA%QHtc}w>a`aRV906lmA$#~|ABb~`t_Z%*w`-b!MYNN*Fi)q|fh4&BBbFv?vB@O?M@)5!gucCCTvdNd$wWe~*-FZGH=}Yc+ZkI{vio=7cJXv3mZ!T{`zOW;BDwTKGlVZC5h?ie&GB3x<N4=y@zvoanJ#TUU&6@{FyDZP8_J^;u=Ds>`c`oUP3EbcC+(P-7csZ4fN#sk?7GAG2yQy4C_?yMXc95?g%QpHl+D-hs7nMiy|DCRd%pZ9Fj=GkX{}NwJs!pT!v7F?7Ja0E)(M-y}#z%XalJ3#Ck`n84-=mW1Bl_Jgq~Glhk_ySZUh?|*ETb=>zH(|~o=@6dp8oOx8lNU}bt1KA+A5xYS_=8*Q{ii<-C7Od>F<o7e8n*>s2}Be+&AqWPQH1;?O;kDaGl1ngnpD79H(oc)fKM4IP&%#v*Q?*XK^+8rk1aBf8LH`q$~DwAM--=PT<$E@jRbD{zd(3jyXrqm#+Hp-=8<5ev}qwrPDa?!+qfcNAl&qhtuizf{|w^z0bE)U!~5@BuXFaNxt%^7nMi7|2?&XBs3;pUHcO~Px!9T%+d>0jmS6K{lMEN_awE0IqUvu${*uLnN>#D;@q3u@AT6(%4ZWFhtiA!^3{#rl#jCcYu-MNLHxelAS#b3BZ>EKv$m&=?W~skX|eJb!XN8<n)<8qA^mQid5h{R-b<$T5n6Fy7_IVtFW5}&Be#gQ7|U;}9BncB62`y$;pY~bN97^ptEI8mDZedPe=;WV=c2yKpFh*Or~7(4D826;p!AnqEyj7FCOYu@bszIWXf=XAcWc%us?X!8G=HR9JE`4d_yT<Mvz;`qOb1iRH~rWoo6n0x>UTLgmV9$iB>8IoRqA)S$D~un`6b@*K4tXv`DKodIYsmOM_=;QoIbQ}n)Pu~&V4cJ9rBf<7$<Aoc>3sA-md}c_;_Cbr$Wy?&)ZY|es_k^*V|cgPTxn*ZFG|RjusjxW{;87zb2n=$XAZ#lP@<O$H%|BT|PZ8xFL-b!M-Q8gUR{GN%GIn;p3-zHy{7)hLEqi`y8R`ZNKt*JseEFc;AbBHHxnT;?R_DNTZW@eREdO`Yg5PzR5F@e5qmut!JiXUMJ|<Z9H$cz;3)AXPi$M$B)|k+Hs>V>f<M9;t3i*0iEb~;n8I(zc@O652YXQERX!>?f7#Sy+`e%gw@S6wzG20!q*@83fftGG$4=C$Ni1UtFOb-jfb?~OTDk~@tT{-*X_Oc*Hd}aw4=s(D%X#o{a#5-AYb%;gYr>AqF2-JPow$$SoefS9+X~e_JG<~RA1rca_mp*u$cQB?~e)g<V#(f(taurIl=esbZ4rMoHUxQ<%DG3zL?kInY*+fD=C>d#&Syb*Nd%utS6>VTb-qT_e$pb^SwyEA6?$Z&qvcAXItgp;aQQDudf>i`xUc%RR1i#uR8pbpC2N-(RoIyo5AO^zCXrnE3)$AxUbZ|Sw!t{bSL>jzX4QVDevK48gDK6{$RrVm5wL!eNOi=e+9qtLY7{x_l)l!i?eAQsb6}mqjEaW<UYomImCyrckuObs6L3HbxCk^=jqGbXq?IiTJ!UgLmZt0OcO`*d6VrhmBv-o$K1CY#pl___H=GEKX>8h28>T>&|ej!Uo$>0wxRV$j%>{5_l>7C&!p6@v`?A_y3#z5rraQ3S@RESXQlE$D*4rAJbe@U&E)r5nac0;=H)E>c00Aht)Q<d-NC!GewZuIt)Tk0=t;gfwHcMq)X@?{?Ygdb2jzF+KKatvD^y=OsDOM^>MwkKa;c#Dip@8DMt(^p-yb4+Q+jD!GWnt}_syl(`8e+|k9_IK1n#%lM)OFpn?SzMXfp5LXqS~#{*mL!m&5q}Bg8ITPWK;roBOv{@^KPlo=4;A=N>$t<MDj`AAdW7eqTNGw|5QwqQnif7=7D)Q1|uzGB;msG5Y$rQak0Jw#pyAob&v&F}*&&go&?}=D)-@H+X#3%E!D@H+q#A^U>EC^Nh7+#`OApF}IjgY~}0c$zA)4t;&z}P*~ch!kAv4zp78NRe5UWZ}G*mR{3E4QIgJDm8WK1^1fSQ<zrovin^YoaVT`A{m^#4=)UcIVe{A5(Ei4G?JK-Eui3icE4+L?@fBWNPuP0pYiI}KI_7I^2drbVwodvAFRq_8zRmh+*4AfVWBXv;uJLWwZB<+Ut@6kEuWI{_ukhl&BWwGYF@JsklC^!1+S_Iy6vOM%K54t3>b~uMYSQ*`Dv!<nuKTw8yP}<cjQQ*5BHgz=7fISVjndnk-*o?l^P6_gr1UoD&l=z6{3&VYSY!G1^R4dNo^OSU5R0*#`ud=1=W0rCbKcf{+w(R%=NtRQc>Xu`yMF#>?;XbS=<gluJ;nH3{XIqZ_2-)Yc=ZgmzxG~c94GpFS&e^=`*P8Fx@PZ#R^t=zgEhWBe>Xm%Yf*b|HTIYOKCAmLyw7Uy#l~@{zZci|J>XZl(6w26zc%)-{@z{V+q`$P_kAkYOTGipe6{%wz`irkeKy}2)L~D^xBb3R<J)}SFt5ty>!Qtf7506`SRVcRjPC2@QCn8gJZIl|=suh8JnVZB<!|%7NZHY&^kwPUcPhHi<~x<{OXzns?g*_HVn9-<vA)9SFn-?EeLPp3eTS#-(7cTDap(P|KFQ$yru*ne*{M6d-<b~VAz#6Br6Kt4boox%%jzX<^Q)leB7dca<_B7REln-TOs{CF%}^~G3QofGV8f?UX0ktBU;e2yyw`vAskCRW|NB#EXRQn$YB34Hcmwov@CNW6=x*>HumyS&T&l$hEiND!UxHe|7Noy~V0;mJ6nqhUR*N&xL(rq(L*Q-Duff~E$<Qyr$>3SgQ1C3U3HlD$1a1rc3%D)V5!wXo2o|Bu!6LXnv=6vHcs6u8cs6(=^h@wY@OJ1<@OE$}G#8u+E<i9Yf#!otz*W%G;41KC1mjBRH(;j6!Ij|i&?DgU;35R$Yy{&B=nilOcr!E+yczrnG#va1I11_mjslN^wg!&_`$As>`+|ExTY-Cl**S46)En9g%(N-k8{8Ax2;39g4cZRObP~85*bLnOHiMI(d%#KHRHy~a^aMB+oChrh=Yb0mSz7GXA`Q9^ng!km&OtCfhG1L<Ed&=L|1t#Q3g`uJ1-Kf)_$u@gnCV6ERqz$)S@0Ebxlp@alp`3Q)1nxvK+k{`@B!!{@B#1^=r-^c@TbsZ@TcIp&{^QQ;K5K6crds<v@N(jxFysP+!EXYDuO$Jhd}#-hkzrXv%wMI&!8K@pMkeRw}ZEW4?;7+2f?SH1>jTQVnhMjn`sI79Jm}>W$3Re^e5BHLT&#t*2e(jYG@^x>3N}cEHSQt774ZEjj=u^86SgYgL9z!q1oX5;B;sPI32tRx*5C)ybk&acpZ2VGzz>3JP|q$JP|w`>I)tY?g#A!?g#dVz6<sTPY`O?vIz*r3$<7aod+EYo(B$tdV`tv1c!k`pxwYs&EOF5dT0`OJ$M&170fgbybF97S_o#k7kn6;BGj&BDbTOLDd2eMTJT!bGakV>0U8DlLmd*J>%j?N8M+I+3uTg_Dc}@5gE1R#Y;46r)4@zPftjuYGhGB`IuXotIGAZaFjIdp(+Oav3&DEd$3edWe}%S-Lpho5gQkHKP!Cq0W?FRA!UgIHb^&{6(E~aV!PpP#31&JJ><12ljsgdPgP~Kw!Qcf5#?e~L)MCCCA0QY{fkuO)k$wt-aUgUQI1oGtIutwz><;w=d!jAe5scqNFm`}813Q50AsD}cVC)2S0Xu;^K|R2FTX#Y*eoKos(C*M4;O^kQ(1GB-;1LMMBcXm^KlH~)1mnrjVDMycBy<5d5*&kIybKx*UItzcoey3Pj)l$y$AXt27|%d39s~UVJO(@r!8iaq1v~|PAAn%&1sw$T0=q%o!S3j9Hw0s61mlKK2XI5MJ+vO!9$W{(*be#%Sb)}rz5=cbZUA)xHvqp5?F44}7Wj4Wt3vG<dKJOAF@kY@1mialjJrU)gS&uxL;Hf6jsW)tzlUJ_K7#Rh=twZr$>8zeInYS(9Pm<T40siEH8cjybQyRxSb{DGOW+mISnvw)8t4-68t}(jtb{IxE&(&00saU&4LSqNbPRYJcr=3X0O&CA0Px$;05DT8@Y`Tls2iB6GuRc}6~VZL7J>eC?40WUr+*!*{gc?>wfaXg+dHj4qZsdW(_Xl1KB@%z*JEQ@8|ZelQTJt|R`@qE8c^l'

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
