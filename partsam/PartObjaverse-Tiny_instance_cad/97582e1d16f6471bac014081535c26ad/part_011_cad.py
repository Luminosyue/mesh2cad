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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/97582e1d16f6471bac014081535c26ad/part_011.stl', 'relative_path': '97582e1d16f6471bac014081535c26ad/part_011.stl', 'source_sha256': '90188fb21e693e85f561002a6b4eeee1a57bb4980b78f870f9ef2f2633b9bf02', 'input_faces': 254, 'input_vertices': 188, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2562795579433441, -0.43050408363342285, -0.2233247309923172], [0.2562795579433441, 0.49965476989746094, 0.19617633521556854]]}
GEOMETRY_BASE85 = 'c$}q~32+rf9>ymDHWH3NhzEx-cn}a!2?>NlG7yM?K*)koKp-!ga38r0D4HD%LLeM5ghL@RkP8GkR1gHhKmq|oQI|^;d|n)C87N(rT7}x_ufK=yHEh+^ZmRzE{pNdpO?OXE_aq^%PTdeq{<YQK+4y0Y9;|618fqb0c4|h}#OG5pADx!=qMz0TzWDR#()h$72_yZqY;9I(N^0iw8KFJ((B9)BLp$lA<ECe1Wh75anx2u8D*Tw_DVeE`pE)5pE!DYh-z74#lisyMC;b)ufBXw{n&A3&+^72-H8&poT&OYNtv$Ftk$haJ)$Z4mLfxHLAAo;3?Gs$P9>?$Y&`s|P)!z0$hV-oqKaCRUR;8{(`ow@ED7SFUap7x+a+io}*Zijs3)SsE&LH2@Q8h?+_4py^_Aul#+ce#TYwd?>XjJ}3C}&Dmo>153_R`P3fp%+$U1>i43(_~P6dm;TU7e=vMEXO%>8*~^*O}g2+6cb8aHLFMnv&-2>-6nfnO={+jDFJQEUuRQGCs}QH*=+LUhz$DH(>kAebd{4zU{XH-TP5*O6*CrW9EZzqr7ty;Tyr*YvBJlvs|cqVQnSK$%~Wy|L)@@xIPg8-#k=x3illpj{bN5^37h9)4s<cwByvY?Wi|*1AHy<=g-i81s|Y3b99mP_a{}O`~vn5eUrYy{xN?XunYBV`SvXCqombGs5f|o?BCJfA4UDq-|s;F<Naj+UTT5-?&Lrldh|Z{#>wELsMnm^7wM}Cx5K~G4C%GFH3y(65%0nuIs^CRIyoNqW$w+}0{_QY_-4gh>wWz9%iwDdd|!$F=sraH{eQuInRCyg9=mAZM)*&SK)+}mx~{-|8ExU~m36;B`ut(Y?;h5#0{3;GDaOUL_sDrZbY3~`qq5#9l)G>%(&_camcjoc{XE+9&)%rt-J&CWt@1NDe_}5r<M*bur6{jX+7VnIZ@v=0hwOu|1&sd+_13g6#CW7HhVPz~d>Z2w^V?d~TRT_Im)~EK^;SlsUf0<hc)o4zV_aL2Ip`<rY9xH4bjcZ%f8iwR)%$mo{-JiVKgX<D9_8iRXKJJ$_BF=KswqbOcCTINH|?TXjQm;qEVT3GzF)#$b#ylR<?kz`@4kuqvKoZT`9@#+rtBQ<Ys1?8_<iSxC{G{N7{0rE$U$%4JXj&qSAUH3dT8t_q|c5-`R>vk2fcl*e<adtclE*iv^tc&iGHpA2<<nT{RH2&p$7e7<a9xL`&<!xqh6I9pLy|L$@w}N<r_QK!*@3?LOJ&NmIu6j*YrAPai2@F_Cas_V>#M+?u1M~^eW2N4}G!>?MaA{<*!OY`|MFM@a?6ga()I}!~J@ESA1QRum5%$<!iI=hHnJj!1`k}+`IwxC0<*Ke#?!N;}W!aKJF*~EPTsKkn`&6d^w+r&tu*h7gA)s39YN5ynL-B4E1W8rtd|69_a|*9*`sF)#UG1BVF}#1!(87j!17bX^rR9y)g;C)nFFNci;Cp`prIEfcK9Xx?c8A_c+WmV|x8X=;yV4F)ps~EUcp*-*}@C^WO-MlH+)@Q9k@rbEN;sW;u?D*B7AP4x{AwCNx4hu9RtWP_Ju%oDY|eR(bn&`(bh%U%F=x?mOv*oY!p!z_$vnz<2Gq2;W^b2Ic5U<4}&3yW(`E$T!{(>xR*H9LB}tTY8-A|8rli^Y-1p%|d@_6T7bV_U%dKvVSgGYrTE5buT%-3x8kW?dy%g<a*Nom@LP?O||fip*>NK>(v0cPSCgWhs)=>*Xk;7Ut1q9$GvXu9v{Ew7&*SN#k;+IBPA96?}~4A#M^gUIdZ)U*ml_4xAy+@HPW}dVEdFm;$QHMpiKDY7Xd%_5!Yc;<vP-B;6We%wH9){D%>&O+qavaknfSByQ_TCe<#;r^I0A1(JlXhAi4fG|8|SF?_Rf0J{LF7Z^n3cpKwL^TJoYV(Z3g$9rO0hlAzOg4x+P<_@qB^8t-fUs#fjeuN#c_tX+9xmyf?U%f@rndt{N1?|Hvimxg0r47xNs>JIbJ{PhNWb>5op$#bIaF#kQiI{)p<*B3<H={YKFoR9p<b7$8HT!i*0&#%W<pI`Igq9ssu9k`ZMfO?g6!}V%1e081CW_B(_eq~*9Upx<AUEe&uy1u!3e6<wyD(j?C_d5LB*44$q%jA6ZU5B-@82IXX?(x<2+<Nkwd=D${3)6qYO0-vb?|A&%-aA$M;j8a2*RM73)%Tq{v-C~Wue=|v^w?EskMf@N__w`h{dX55z4{)fufE64>nkjzQ}+q<)qR5P>`!p5>{~p(x^K~s^pNS5{g2o$A-%F+(nIEzz*qKH#=s?|Xs5Ct(}HW^tNS{uWydm^-*+EqJTex(x^Hx~%ftCV-DeuZ`&Hmt*_T><+ipaAm3^$aY#{vG_Px$N8NRYlHY@X_ukN=!zOvsooP9e~*|%HHJ|FGO7$(mho_+pj^>-kBaZlMlX@5*bdz^Cw(ktf(quB`ft}{B$Ax2;_&K<UMPC-4&ImLF)H7Hj(?|6Lmyklioz_$n7l;@`Ph4P$M`we{coTZ-(kmro|Y<Vsl_yo>n+M-(c>N(DG&V49HIrrJlIT7V3=R|kE%d(%8^Qp&I&!-+=J)hq4mGh}M7vuLkoR`ra^}OtyyU~8-{C>+<&hH*yJ->VW+s^OW53(HfyTR4t=y&xygZM6i@|5oq;yVV?E8j81cMsI7e)qVX_6hny`A#Cft02AdT}6C{L4NP=FbO_imr7sHnJ}TDrirMpg=piFy*@1oQ~Y`K&YzYhhW}Temck;!|KCqbB~BaGInkVYAGwheTgXC7ym&LOH#3ii8}hm#%kgj{UN>SHg10)c&566H^~vH}R|E0bP~Rhae%nfYmt3Fe?xF^gw=&H(>U-pE<oeVG<fcx%<3tncCUOveYfNoI-pF)8)TZROnRg@g9deLYzQ#=F;U>Ip!aRb@ohTLaggTLYH}ziXMDo4lmJGp@7=kToDcK_LVhG+%Ehq0Lf9S*x>RM_!c`bQ7bpqMb*6|F%Eu5%F^`qWR_9JW5d$m9R1p8B4lKshlVF-SZI*BZFGWkJrdxqdC48cnof>%-}kteagRx$){r|u%(??eYDLKuP{rlyb|CZ{q4FQ*ogmy;_Pg5PrDP3l5wA$cMBIcf?yg>^s25d0YRe)3~v-HAm`Jnuv@^>K1Cxihsbxik3zhTzr=!L6um$gRltP<8S><Yv_S$<4?C48e7&A>=yLU}^|Cgnb>%5d07|mHZHS97FI5>T>c5@&;-Jc_;M)Y6ZE1WAgz+@cRtG>%GQuJwtFAbv3z+yoS1pyoOxN5c~#1@Dl1G@*<9(;9gF2cOu@2F;0wiB90nQj%OOdoty}DB7&aC-<29cj$j(WJ)MYjq8mMtKb+c)+>L1jCpqDAVhBBve=v0jc?i=CW;;c@)2W%{baF0rE;*N+M_oY9BNtGM$OYv2)O_-M@*L_s@*HvoHH(}<PNKTV12yr#5!rve$Pv^&<Op&nMj!T>(7t4$vE*3xS2x~oHv6L&$8sP;@G$CF@-Xr!hTy5xbaFb&oXY#1!T!i*eL2)Tat_&~7LW^=&twSx8+8U*+{<5iKRwAqsLzszkdqkCvcG4rebcBJ<P4?}Eaq5@Cg<J&P0s1w)UM>-<Q~*eawzllU<iJK8bj{Ra^t8&$#LW{)RAPN)5&AVnba4_Lg#w%Y+lbLFQC3gUO+Bl2+pUzN*4MOS?D}+4Erd7I+&b59!+(TMcy>#pGVH3jwX+0dco07JmbV5>eJ*w<R__#<o?vBsEOoR)S1*oaw7B3WC(tN`V9F6^2-dtBdF2j5oEE)e}o!FjV6bYyHE#_yO1BHK1uf6&!Y^%9i3=L?MLlT?nfR@eTwY4|KSY5uQ;)c`Z{$M`E~MQF^+M5{vmb#)4#y~{4>Qy%;z8CYEIwdjd#wmPFc4OI|*_1#J<egsQF_d@e^--?cXZ@4Ym'

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
