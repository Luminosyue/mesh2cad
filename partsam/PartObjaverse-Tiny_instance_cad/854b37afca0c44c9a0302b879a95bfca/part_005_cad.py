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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/854b37afca0c44c9a0302b879a95bfca/part_005.stl', 'relative_path': '854b37afca0c44c9a0302b879a95bfca/part_005.stl', 'source_sha256': 'ff27e02e8c185c3d8e6fa5a6bfaa055ba834d0df354c23cf1c58de0e6cb4113d', 'input_faces': 171, 'input_vertices': 155, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.19133955240249634, -0.03679913282394409, 0.04062347114086151], [-0.038487523794174194, 0.2962782680988312, 0.12723961472511292]]}
GEOMETRY_BASE85 = 'c$}q~3shBA9>x!#=Bw01B~ZJm3FaF$6%bE85JeFYLBsSSf-gV>LP5}jnPx$ff?`_UEJZ~U!54;d6!A@I%U8|h+$4LrG_xg^kH%qt|IZn0&8#(RhPD3d`<?IX``?eV&))kif&!fCIcxIwg0|uNM_n5>(=-)LHD@h3Dj{iBWK?30xcC$YtvP)4_gGg4P8bt3$w5oj7P?Q5N{mc!_p-SAL=SN9W^s?6n~;<c5jS;i!t^NR`$fbgM%DU>Gb7@oYOg(d_v_cq(x*!|OS<KM{A*m>1mkS_iSk-CJI5R!tgg2`_nA_?)m-?RtHTL(Z7cCUq|`DrO8l!8@D1My2XMc7h~#k`ds1E7yZaqPdG`+RjoFUJkhd_e4CQkUABP{EFXcZhEQf!)T>PIFoI?I_JEVL;8GP$xpGx?tCraU8NR#sK%tU$3p#bf)y2ioRPv1O>a<K!X{m)H?Z;ogS-w4^U55M~)Nc`;kM{xbi?|abRp>5$?F7!otGj@xNPw2PDQ18QKr%~TN5A;`Sb_Txw>s@L8)lBruzNAw8rq&9y$2^Vpn?;|&w|0p^y+)?ze&h?cS0caPVffa)RjAjR@E7>D!0!$t&$Ud9zx}~M`1%3ID&+B+iSp*MV##xK<QZJ&HO4p?E%GbtwqK7NX~MVu?I`j`Z^gCdEqOGDgYYfM2I@60&n}a37z<zTll3{u&2U0{^pY`0rQTI&k8Pxm^5*eQ@Xbx@zQFbUYK*@bSY3g6l^b*x{k&d;@i)@G5`SbT8As<U(w@G>;(s~gOFY+zhXuGlst~^M-Pe*QXnhItIOV~&Uz{WTDk_uqmo0&B?KAlt$~m0dh4v<f!?(37Lw<cu<__d*6#!o!e*xvK*M=2A2RDIl&htTeZQ0nJ(9SoGpq<6LKg4xm0iLfd<FfeuD===Ro+9s2%{lmn%dj=*SLJ?`H-gW?*CWng+_d^hPxw~1Jk)Ey=Z|`=-yD_vFIUO9kDgv8`SywLl>ZL$*ndJEONYJiZ7*15+}1DHi~DPK!Z$k)-VJ~9c4=opp5!^<k&JRJJxZVOt1cps>9kyacQ`}Z?>S1wt?Spt7}v{b(%-B3n3r1E9eFORQY4SPcpB<YoQ(Y1do#oz6OQ)jIlV9+>^Gy}+yA-``Spiy$#YyeLCSx7{SEZbH3xYN*HKdMkXN&j|MoTb*51QqJomWCbH8*P&)0n9BIDqY0^dkp4d2$<S@ML>mgma%)U3X681=fOg`wYOyxb4_LVUwWlYXX(A9qUpwR17PmVzXVgK_$V_#2Csp#JU4<+*zt7vE=EHpV427QWv60DNP0i}!GU?D{AD_+9JdJ>4q4`yTkZe_9^$dta3N9T!XaB$+o_m%nrV#KE_gXcz~ZdpO3~yd4bRzG<qwj{_bS$@A?4-#iy7?_qw8tXK71B!6!9TGW4XGu8q7A!q5=&aNwQzobmohZ~Khy!WDw$oD5-`}((qxF1^z-@3WRgx_+Ptm987;JH|OT^HZ7$co>Goke-0RjK&rE0)7=-Acx1=uYwN_2fDI)CA*Te>NAsZO{$OH+zc&8HW#6z&HLLAnU-68ks-$mrI@%HMzJxk|X21VLp6)Wy}Wr&anpb+8UY!-|qM5Bly>U5dT!HlrL{5<Je@IJeT!RQg7+>9Mp5OiS#SjSL)4rxD3B**ICBrPIvfbXfxSgH@eAw9ecMN<%_<Wf_$GQ$^Q85E%8sC-Gn^P1fo60mDBL`)K>CbnkR@~kR|0m8Yc6^{{xv1Po;`Ks2byD^Ri&vv|BNfr*gZ@hm9NL{XXw4<wGx_UZcU)J#~E}uoJHBYeM9`n|SdM%D*0$g*=&;kjHlB3;23;1^S~W{*3a*vNKZtk2D+F-~JZzX_b-ijg{QbDl+7`r?^P@{EBtBzqq61zfcdprF5M1w|N`%*Km4p5cSR|lJ>=XBkOUGs)KdskLmcntS6-l%20kpqO3Ckn?J>Uy+3@zqpA2k3uK+&`QvBszq~5z+C@KkUmIk>*G_yV^)B8d_5Ro&{^R|^>=1>0&8WV00PUI7Q~b>@7oxvo)8X429G3a~w#znXztQk51Mf<E)}8qT>ggeV-ZAt`Yj_Op*InJje-t9?YDP8k=zmm}B7gEy_|_{8wm{oAgm2k8MdnGr%SF<!2m8_AUDssX2DZVzul2nRUpw7U-iJqb<eZRI3SW<EkNrhIG*HH&=y}QW(iQAe+E^X?k^Qxq`!ElFo-O&Wc}V-`b%$?TGzI1LK^L)}nQp;*k!SvKInR8w0`teb5D5SAKB&3n%Y2ycEB>)yIfwOmi1}qrxVs1SW_sd$V*OQ@eeG_x_`j6noM1oln!LXYyTaFR5101j4n_NIM}8|o`Ta|zJ#YR|BI8p9->5ny`)r)E?587EiSId4&VOy<c`kiWEd5#}^;$od_af5^zCIum=Q=yjZ<fNeT^OI750S^RrJ?wv{o!kl%W-bB|6VTZcBAt<kw5(geC=L$8MoWV#NYo5&a1|@8mYJV{HMs1d=lqjef&5%pNyUe-}>NnIk(>#k8#j?I>9#<`5}*fDP7jvgsX+{r`5wb+}=yxBmI&Se9M(t@QoKw%JZF=x&!|FPB{PTyCY=1`h7TjW60Y$Kil5@5zo=gj@yoL$oG}<AG{*xSZfG;J>Ech^ZN?4-^^IE4So+leAn1ApOJbuUEV6=d>`KtW=R`)UOkrP!}psn-xr@0%J@tQ6<@z6-!-{2Wc}ZHe+%ZrdK2Gk)+7hnhu7YOub-PEd3<GEG{YWjhVRo9-)lz8sj}Xd`~cr*HV@y4ns>3Z^L!Wae=Wp!oY5{r_D%ne;`;}~*Xzr=t$n=vW3<P=k+f&;w!MRcp7@I1b<gwW(uSI*qEYQvbaX_WPiSSTzsLITKcQ#!{qH`Z`}h8TKcORP+c3R0f~gb8N?#$5RMWIJJQ<1yFcf=JgUP}Ctv5q)7iuqZ7jj$b^W?VV*3>rS*5qfYEyzlnk)I_uXDDvMP~4cI_$g{rveHImrS-^9ku|CV*^%l*bs#IPPgdHH>_l!reTLkC{4}){S*bJmX>v>IbL5s}7wU^-rS4=GvMaSK*_G@@?Ll@Ux2N_bw<lYueaIGa2Wm%h2XZ@x;ujc-J*Y2}J;?nTiic8%kcW~3sbk22<Vn<5$x5ThlgN?O8RSTEG<6O+nmn7KIEFfx97B#}D2`_+PN2q-6UfQbdE{hr3iWkz3OSuRpPWu!L|s5$M9!e5k(DkXXONdsSCE&HS5mXcO5Y=|B(I|8l2?(}QS-=3-zVo#*HYgnD_uigOU|aQCM$iHtn?jnHaU}__-%&bw-}1wq%J2bT}pnF{07w^zd>HiP@GC#NLHFeP9-N&XOR=hGpW<bN+ZZK$y2GpWTm6YN=K5Xl3!ye9!B*f4<mQ0jq$bNUmJc5#Xbzh18c*JI*RH~9z_nJjwgqZ!x@SvG86|<{m4P&;S9yTR3EZ0xi3R;Z|XpDZ*uoK?e5M{{1SB#`6Y5^hT={P#e*4&$1)TLP`$`r9E$*k;!tV`Ig~tw8cv=<p2kpYrA{PU$&(q1!>B>zF!DI+aPm0v2!>*v>Pyzi{iuD(K>-eq&QAa7-vIymGqCy9{ind6fBEFmr|vKPYIFVbAQTi(U+sIfo2Vley!vXF(*6NeWUI>'

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
