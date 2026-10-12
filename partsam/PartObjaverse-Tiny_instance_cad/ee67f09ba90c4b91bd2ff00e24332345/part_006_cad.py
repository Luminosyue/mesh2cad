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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ee67f09ba90c4b91bd2ff00e24332345/part_006.stl', 'relative_path': 'ee67f09ba90c4b91bd2ff00e24332345/part_006.stl', 'source_sha256': '482a61f0f25c5a668ce9898e08b3920be43489ca6a3098da03f641391d442ef0', 'input_faces': 368, 'input_vertices': 215, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2970508933067322, -0.19435547292232513, -0.0425589382648468], [-0.10896091163158417, 0.13427311182022095, 0.16352830827236176]]}
GEOMETRY_BASE85 = 'c$}r033L=yzK08#2#R4b39CQ>Vn71O4hm8tAP|HAfdL_*LrB=dmas3eAP}-(AP^RVKqp~G6a)zZlFC8|AqfeKqi1HM9eqA$<~e#CM&IJ_UiZH~hQ57z&Uxp(KIfkA>tAl)`rq5PtEw9!!W;Z5ShF7;wck8EnReX$)YG2Ug0+=#iOc85#wGP!ymU=Ht(oMW$0P0<Kjn>x>Giag+Pcs=aY?a>p)cv7L*fU8hUua4OA?nS#w?z-BymohCm$7)kQC?6ljg-NjdMTm+NXE_FuiZLFnxpme|$XUF2VY;{+%K>T?MWR54E1(emKkxz3qeB@;qcfxrbKD<o%x98Tl_tt_|&!;4e2*_MGtK*364){|;d}@^_!yF{4n9>kKNq?Ol()@bin3yYeJA!`><N&`CX7n_Wt-ZJoBnUv9OJm3o}NS)|r8rt*j!-zRsj%C?VN9<PjJZj0U}{e5!lrxdAQiyE)g@3?*Hswa1azb?5R9Z+nqk6pj3+h8Tvwk%!dFE{tRAoUv=?bP|UeNpPyeDjzQQon0$pgPXN^*d#LKDo9yT<SOHKcTFH9x*}cx5j=`C-X^octuG4R@cvz-25sk$#4Fre>*Pqx2~vD_M6_LMD|-)d7V<{#?-^oue+KXIo}sb|G2_B@A<k?zx_nsuaeWsajkkgvgNr?u0=Mp_j%B!I%VJPeNZfU&IUXGx%ovo?xX#dxJ1dd=;bT?<wl#6GGD#bTy-7tZWl<sE!EsOyj$jFJcv=|t2bIJ^KwOwQpYdbyhGkcpWNJBeOA`r*<V>7Yx;SamzLc{S$|jZU&`ctuL`usxn-P_<1$|(F+g3n;q~l#_SRGDnc7t5<@CuN5BtizoZ~fReDi+BDu1~(cCM_OS^S4uWq-c9RO)w-|Kq&W?u69uSo>M6GXA<RvgGwXxz#C6)<?geSF6-nZeEdfbM343UN^_SXc^x*#Lo2w9Zt)-ZDM_%*sYB3Iy59-p8MoRLFENm|Dp_K94+UsYy9T@+Ss3$y0lvF_1CX-vG?cpShfG8jBRrKEHyU|43+tsyGASPX+=G4&+Gm`rB1!UPnTu<+E8VEw931dtaGDI%J_QuoIHD<s=09?TIQ?&+(vR^K!ALnE!NFZ(nQJ4@iW)^&7ZA4CgYs@>X!0(xp1yj-mgWqx0L?59W#W!dFl^mWZ!<1b<4X>D<f9s>j>O*OW8kve@o`;N|~gLqeZWF%0BnaH+}n&)On|u<mTY1dxVenNqo0k-s@@QM@s$9`7PD{9sZK+FE{?MR@TAnQB&icYvtRw%HMr*EBv6$*UCFqqwI&k=Ve|-a(<0>{mz*;F3CPLX4feDVc`#QezxvSQpPv)0}ly(a_8kGvJP6;_VzdnTCR}eunx|v0ZMMA-!=W^W=dz7uk%Q8wRfG4n9L$s=is7h@BZ4oyPIYI2dTOF-6&ZHeaMMwWj)t~%6zT#?bXV@P2Mc?)m)?1@y|CtAobo?bJwu%&r6*J|6L{d-DRnAJm#yVe5>SUgFc)5<<@gmN9FIeHC5hq>OYpq_1AdqY?ZQ~7X?Y3X2$|$9PR7Yo1~vl?reAe1F7p#{;2-@8$OoTHSeSJHwOMKSLWMH%}wWgd%jusZc6^!Ap1UMBliR6>TW9Izx;z-FU*ANH<fw)uwTw&W?_*sj@jsNioe__SR(7A745vKtXp=K+~-*Tx?bt8r4LV*<N4%{pLAIV*V(3O|FFt^vVVPY=kLEbC$AfSr&8Gu6FS(}(}p)HmG!R;k@@O>IwZN7+~tUj!}>U8WGcCK=!Gr*a>w5TWxhtp>Pn^l4lV5Y#*b6S88dOUJom{RHM8HB<2U~5hIej`G39-5_~foR<7B?BLw9Z{?|a4pId5n|7jAghqqplV*G<=`7&~tg|DN=(h_dVb?L=jKXWSI~{_Wy8rN3TwE!AJ{>U&IHXH03Pj{jL;qCEG>wOP5RrT<?mE0q0{-$Lql#-FZG#_4E(A948P)|>YC5i@IVg|cqvN67WUmETDnr_E0LdKc7Ea;y4?Tz3uDL2nVD<oX{SY5sD@0z;0YkGy%^JJ+@jpDUlI5k7f!mAy_63$H8hV_1lsC#}e3*Om3z6Cvk4vv-0rj&-J5?vo9l+`QUB*1_uh$8x3r)-wBg_hqSl-yHO3IWK6B=KJ+oHE;4uy5BtS^TRS;X>Pf9osQ}s<#S|xw@&T<Y5HV&?voooJ~$<>yJIMInkA8PeshlMtd4WfDffpCpWI3??f2ox(QDqh9{WJ(xV_?<vi_mvvj3g`F;8+M{Gse`>$<%T)-O}le1etfFE@6~lXcL(d``)=f4??V`n%NJXw^>U>zv$BsnZxd(f-~VTwCVd-@KHaF7x%tjr1?<>tnYWO0K6rYmb*Zs!Umjs2th<R%HXpwfbM%`-%CwW<4nN&RzAFzU?p93w|k(I@_0*dLP&MpCj$#e_E#W*K*QgWSo0y?rdY6lsbE?P;&FF>2g1y`Q+Bdfihp?Z_SkBn&H#zx_)k`j-NS9&WF}FdrBlfwO96~!F<iKG$nW49=+XPt}jlN`8xi*uEcwM$G-k@-Y`O<l>XZ9f3bhZ@X4)v)8uym$LB$6|D@J(z0-YiS6y5CdY5~r*!#G~=3x0;SWQnCEB*g#mi@gryt|U?&*<`bH+OfozlYC!%Dz7?x7Wd$6r$u-X6g=qxg#n>)<Hk?o#maI`v%GPLDxYwH+C$O??G1T2_@H#_ehd`>607NuFCme&&;xvc{RLYzt5M$mHyU+)%N*p{qZ8Do=@w`emC1sl-&GXFS*`3nXmb9u##&pZ^-tSI|Fj_<?n00zv`WvpYNCZd~3CuTcKOzzSn4%dR1BHdn@dH(s8-cUrX-oka_y#u1hoIJZk)O{S)upaAn!w3(~*4;+;EIx$N`&@4mjQjPH5hBa~k`&wn`Uq1D{o)!m-dg0=V<ub((Qq37|4{(s_}-|v6*6KCH6gZ{riaUOHmaKzmXz+C(Qz7y`icj9R<6;H#H;W|7SUk;by%klXz4xf)l!x?xqJ{eBLC*xz_D0~e53Va!V1@8x6#QWi0VQ0K6-ht-v*6!94c7&brj(B(YBHkSz2w%nr;v?WFd;~roPQ=IK)8Pz!Ivxw-@K}5iT!t^g*T8l78axH2;wg9*+<|A|`(Q4<4=;d6@B;ia&Ep@yWB3R7hwgSBo`lEnleiNez@7LWxD(%lXTmf*6E|TpZsIH9a(pG80O#Wg_-q)B&&H?0$@nz<4LAmW1Ah&^g1?3jhW+rtcu&|B?}>MT9q=yrvow!~z}9#O-duaU*PGKk-qhWi!B(&(-U{yoJK~-2Ua&jf3x5d?#9zWk!V&mLJOYl#Bk(ujbo@<x4vfX;;7j2md?~&buEE#hTVM*l1>X*{@a_0Ja3B5-ei#<uhw=B}Y5aZsBF*E4@B_RM{}_IVe~e$z9)Fgu&^&(C-7I(kp2siXr{GEa6rKm2cpknN?!ousZ^KOdZG1B{@y+;pxDsEFC&C0g5nljj;|uUva2h@fp90^&r{H7ZYxr2)fP--Z?+<(8{qZo^1rNiYhtJ~A<Lzi34}u|h5FQAd<AL~-uqpl|-cWn|S#3!3cq7g8&#yLvVKY1!Zx37H?eS392@l2l!d`e^d?<VgABvBLBk|GrBp88D!lU4ucoaSl&cWy5NpLBigl~Xr@eTM^xCP&eXT$AyHvTSr2Y(ko3J>E)@w4!K{49PMUc@is*JvIug@t%2UIIVHOYkyy1uw(P;Z?jGuh1T!3o2+HuXMMYuozl+F@6bNz%Suv;3@nJejMiE$MJ)3FMbfufp6nE_%^s1--d63>+wzaYM6+x#uvi{_+mUB&cfsInQ#g|6OV*r@kl%z8hAMVD(sKHiVuNd_z=7|d>-$OcZ2QlZn#eKcncVWx4;|2K)f*?0H4GI@CL9U-T<!$8{zfv`r6}jO?{fjf8}mZ!Dryp_%nE07>u{YpM&l3=kOjd6z_o#f_?Ep_;5HBAC8ZMqw#V0ui+&8*LVz!!ej7-a2~!8UjdWw75H0l1O67C0k`5A_->eu@5T?ockx5`33wDgfuDnC@pJem@G|}hejQ%Juj99A9=`=k@mqK`EWxYsDp-bB;We-vufc0!1zwBaftC0j{I2%+Ty~e{@q6y}DXfDx@jCnlEXHr(Meq_{gntCj;2+`d!Q=RQcs@Lc=i~cf4!$4X1-Ie5@N~EdPscaH)%Zqy6<mz3!k55!d<i}m&cx^94j73$@To8ypNda_ui_K%*WnQSb$l4?jSs^Iz;5^eybsjzKKKhXkGFv>@HTi8*cfkuKLG>qCveXrBD`Mx;0FKfzqmbqn4XiO@*m!OU#b3V<o(KT+@1dMBT__ofamz`lWBeV;{K)Q?63U~6c>O|'

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
