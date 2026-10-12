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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/53d9d21ff95f42428225f906cd9a0a5a/part_011.stl', 'relative_path': '53d9d21ff95f42428225f906cd9a0a5a/part_011.stl', 'source_sha256': '7f08f10bca0a83a6be6b0a6866a5675e94940cbbf662f93114762fed948becde', 'input_faces': 266, 'input_vertices': 170, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08348420262336731, -0.031117945909500122, -0.08387747406959534], [0.08347487449645996, 0.13830089569091797, 0.10608071088790894]]}
GEOMETRY_BASE85 = 'c$}q~3s6+o8OJY*Mx*f&5fxFdkNCs{jS4|zFBMVng@_0OvY-p%6Bk6DazzjyU;sf7R2C6I0izL86E)d9?bOzo#59>{v|E$dOle{stu@i4z32P>$nG6G(`k3+oB!|rIeXsc+;f(Yh25Q9B>s$+oGz-7$pa)wL|@58N;8>Llh&A0p52_B;Uo<pUwk_C;F1-KLn57|G%0JsT2smz^8_Dxf^UNN1P^&a!WMI?Ic{_87V}z@@B`yErkFH8WnEmdNqe3+&CAn6etwdNoFo5_pC`2{sNS*dZ-}~Fy!&f|cpf>gUZ^xRlKp-a<Qq+292aV7b!Fe>VViiin!Jw+wN)0hk$*7nBBi^qb)R@vigMYHAJ<Ol+ry7g`oJjmFEyW|^yc<cRPNkJ_A7c{qG!Kpl#kJU9{WQ#ou_)9?^sLUyE2shhwo5&^}B{5daiS3UvjxX<$4qqif1+LoAcxcoa1)=Yj6vF@5W*FougaDv;2xmD!p6Eexn=JQ(78+MyPT;m;E8%bA7&5k}1DsE7-r&gUYo$l}+U;K0)k{uBCFNqNRJu|I(fPzo^{*KVN!@%CG$D9QohOy-fM6{Fv&aj2-$C`JbMDliKx5_(@8?y!j0IH>NaGJ?7=MJNRv`XQ|)wYROkq&$W{8Kbh<E_b?uxCq6q(e(Vk|H@kq^C#i`i$<NwF<*G#+C_m$@LC3j1qfb+L(<Z(~-+Q({`zH+49_w-+@~uwhI`Xf5{R*|GIr>$~|5`&W`9AIql>e3rN@wxCag6+NMyikU#ZCI2^=>o!w-Qd!b7Co_SDL%AU*=v%=@(t1d~HiUJW76^3;EVfZd5<@fy}<MMCDqFubiOtzw5<*c25iWbt5g5e@#pc`3oLYQ$6nmv;Unl`z`-!qV`n1Sx@<|Y^x?eVHEX)G<+hh4{1RQ`(;1VytjTkkbJc@iv3>w$|+s<0o<P-|Mf8W7m6soWyL|N|0Dn6=hQE@g|j$)@NxD(EhwUVDy~wy<Whh3y^S=Emc9#Ve3iTx*uNfMM&lT<ppn*{*ArFbN2C`}{qDz8x$@UH4v{}1n#M(*U&-_LeoGm(dvYY@uZ+J%`P)wCmvR03q*4ERUFQ5xJSZjK`f0XM>(sgi?%%8ICqLXo>D}Hv#s1|3T+i?KQT?+@sNUA?SBuFH8^ZIge@HXc)4hiM^Byl#eb%p|e2m?;?<YS!=>Yjx&rmz9Cj;5{*iQA9s~<E``n>wRT&|7wJ2hr7tt;h+5B6}q<`+{xZ|I<Yu^M7_lYh2w8~LrXX?|EbnhVI^bHALPvl5y(pULchcB+EvedaE$H|raF^U1$Ap40caO!ZfSXXbIgjb1?gu;v)mN4~ITC;1zn*+u%I%<H1aU!~`&DTUPDALdYdZ8^0&$T#ey_FBGwjn==?`&JJ5+p>6_&o;Nvb7&6xo@4h@`nl1S)IYtwGRe2CqW6N*dWiG6=F0wnL6lwz45j|DRBy}R_CBnod@`P+eNEkeJ&ngDk@`(ZD&zIg@wZe`_pvmO<ls!Ik8N`c`xojdUt?SYtvlNv=bOownj>i(zf7e3<&Jq<d3<|N|5$75Y5l5snMvgD{+#v?%N-}`f4SGI>$pFoX&<o~ukg4`o|Q=cEtU2O<CQ@)E|#W$B#`eLK<O>FOBx;gpQ?F(S`o_Q9yHxV&%bTvd9%}#>;K_*Yst_1kk`SO4sP!!Z$;3vJcIIA_I*I>Md|Qo|EnY9t8MALzV5vqPJVd@m8&dX(&XR=ze@GD{b4xQzqcRz<1bS_M(0Xuud==Nqt}HWf0Ntwu*}g%dfSQQMh74Lpe{Ps;NZX0z1F@ykNj0{^1gd#>?sHT-rL+i9?ta+e%Nc&Ki1ejtqwlM*OpXhaqum##L|2-HofHFpY4@K{>hiC9sH7EyUG9Yy($O4>H1#U2YhZ;I{5NH+Lz>0eH{It0_i;>yQq%k#@(a!CHwrd#la8iOY6usB&^xNSBlvWzsu|EwrjZIG2>;sR>{6@e5H?ut~5MmJ}5125r)UjpR+aW>*kwmxJBnL{rpthN16<eo6jz{6Uf)if2ndzqQP#Sbgq|2zHWUPQybQiuUn6@sWFLs-TGDHqqiFD=0oRtm!9@Bldsz!q=w_E<m>hmdGzP(>-Hb(!#gx@^!t_d`i2bhb^Dvq`Ke6ub^D=en99C>|9tyk4*9zMRyEvUU%x-MRqP;Nx1SpueO2;x`@izh>Yd!5j_(Vj$up09-TTFOzdWCO-TTPcZ+ro_SNHzv*~q@`eP>-2LF-EYepLGXeh)qC-lyu(W3=A%?_cAemhI>9b$nk-etGQc-tUUnA<kEK9<Y_Y$G-0TU{QZ_fXj6}Z%AKWFC|}pKAHX_`?~XtZT`M8o>z|NAKN?5Rpjf=SC)~6!(6W8c})GJmVMp1&SL(Secky`&Fxl0zV2KqPmE$;e~yjnN&Txo_ey(5vadTQ%QxR=Uw5vSf_fbzUw;lSI>)~5+-`}gr*)z~|I26F&+@uxUQX>P8qfEo+wZgQJdMs}>M!YZFSUOCG5d=y(fLcB-j96Muk>YJ@2UN%{>BQ*$5<E4_Z!{4Ol=EeUw4nQ^~hykcki?02GF|I-%sV!yq@*<S<4S9`?`Cv{2-rw-91_w=t}AI_ini)f_>dRT{^OwefxWTh{LZH#+z?FdB3kDiRdl4NC|OvKUD}*d^+{<KUE~n_^*Ddm_BRP|NB$LXsr%2wHOJV4(_Q%FVTExZ*X_~tv|FMSm+aAp-+Lu$4QHBP-pNVEe>n37g_{9DaJ;N69~a|2*LHx<KT5#q-e1bng-qo-V9a2o587Cq(cj!D!2k#0#(5!-~-S!@B#2HgkUo?1)PGqnh}CGAOuGs1g}I0j)ZOmZ$uj+5rU(kso-evYP)u>MhG@)u||t*E#kF^gXTiB!MWffL^j4~H#8HP4bDcsnNTCxh;lO#>Bu7;{kz+)-*?-UaR^!=b<G!{H3-4g&<b!hxC&YVt^$`q4}i<SFG6>LUj*kv&ER}+GIRs@lopLzG(j7{TeaA(#TJC%Jm^kv9=I4<2rdSfYEcQ@4=n`mgYG~G&Vd$!bHEwUo!|`cHt2TnHt;6sR`4cp5<>8L=oavLa56LxoD9x~7Tfh_G5Wh0ZR_m+QjAY$`#Z<0660Be@ji$UTn?=QS0Q~lbU(PW@5&MT?D7%32O&5Mx&xdAPDBV!faZV`z$R!0*aTh+-3DF@j)iUl$AV*^N#Gc86m&f}3cO0<{Y2;n=z8#ajECT3S{&8l2(%U~_5|^M6Z=817JgcUKo@{Rz@gBE;81WlLhvH!0`Ma6Y=mG>s2|u9?4iXN=nGIkupjF80zz=0#Cwj=)zDz6YY!A04GodH_DsQ%&`@wF+R(Y*3hvyW!=<i$Tkvw|BJgtX5`<tM=xneL_&KO2_&M+-s0Vlwc$8hgj6w(=A@TcrxFn7utRui9kf!sUFVq`420RA+=nV}7dxHb)`Zqx8dY1$sO#t$q3H}vy4OnPASf~L!6FMDg0E>PLLtjQfS3$$TtH4pv6;jt)5G>Zp3@sEbo`?E_W#|-yU@xdY*b6*Q;&m$21ofA?*0taSs3LXk1A;sE3c+)sGr)7fvk-zOAOw$vJ`e7!x8UJOHv&2qJOVrlDob7SMDQf&6sc=o2^RCt2RaQp1v~|PF%2Pj4s;%P4milJzk;B#;2`iaXbd<8<FyPScri2#ycoO`x&*uw><je)`=GAA&^cgV@O)?xI0$9Whb{&$Mj3+LwQ$wK4LTU?1|EhGEUpE8p#z|U!GrPr0SLhZwRjpj1nLSN0-g+Y2R{p)3Uvoh1y6*!fhU5;L5G3IfuGT0Jai~@7<d@kFccwp5JGStyEgYh2=0LpEdD<lve2oUOZWfuFW#<?DlQEU|M1m+)A71x|IIU6UXLzcAq#tm`-*n?=tc*YKZ_M2{TosnHKP'

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
