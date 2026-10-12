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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8da95b178bc641d892f296e42c0ed8a0/part_010.stl', 'relative_path': '8da95b178bc641d892f296e42c0ed8a0/part_010.stl', 'source_sha256': 'c12250e05c5b9c9337139bcc11ee69e1f58e656238002c8a0ec02df91bd6f822', 'input_faces': 416, 'input_vertices': 269, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.4186986982822418, -0.26242074370384216, -0.23036259412765503], [0.4634816348552704, -0.15753747522830963, 0.231439471244812]]}
GEOMETRY_BASE85 = 'c$}r03!F{W9>>=(#&{)?MCpvmlw9SJDCI;CC1Vs_6lTiEtBj!{BU^b?DDOn&B=SsjE0S*en)jSRq+BACcOpu;dF0-`_WJI9_FAUT=YH;;&*$Iwdw#9fS!eCN*4k&L)Q;ujYYFv}B-&)pKezUBA!Jn*wZt<SS;GfBo-wS+Q<)><#Kmqde>~1e>DDQ=N1S*@j7sjCG3@cI<Xc0@ZThuJZX8PPHzaF#R{B$YhGg~4koi67gNJ1}`LO=!nHkRO>zcJ}-8j_z`o^Krq5tuxvNMFpZ_%A?9i}B;w)qQ(R?hzXF9NyMQ03x@AM)D<a#4`G$!)*4Lte0bC|~8_@tyM8mXV9*6AQI|s(-uD%~Ou#X#HHI^6<|;<!J56?fe5pTAto<V_D-5rK#K;e>l6IYM*pk8^1M*JogW6{AuL&$!`jRx%Jqr61V-C8?}BS=_<G1YN7RGky~{m`aF!vc5^XXX!8($PUYd&74&%^7h^UT2Xp(jlBk=1zce@4PwB1X<5uQs?a9L}8fx=tcl)E*Z68{-A=r=IRpnOY`cZ8@m;dJG;hc{)X!#qZs{Of<+IYNNv|Oq6Z_Od!@uAj_mxt#+uZ=&A+-lNQ8-Lhqzb8o>r}fBY)xO3EZ9I{lD!1!Ato38fD^mGK+1mSBho4aWJU3qJ$3CQTkvLgvAMx^49rXUctETe%a`buLt#bRv0(~CHt&*zx=c;<L$jy!G9;u>o^SWE)=5>$cPE_rC?$bY4j>@fbhxGf0-2UvSc0Y$Vwo~nm``Ic{xp_Z(`33j$f$LR%R$pJG`&DkPFPq$4Uy-|Z7rOoIoTBw(w^zBHJzejI+`6ruzD`TtRe6`K1=@I`Di;m({X~$P`-zvE`-wR7lIrK?zWP3JTIJ#G{q=o-+%6rY&09Eitm^0KUfMXl+`442woisT)Bcl8eV-(^FMCWIXJpIMs(r4$-`Zc2oBM6+{q8s{W1qKLsodP>!{p{ZZ(Y^f&Be7-wENSluX3wkntq>qdBUCg{xJ58J8o<03x!{lk&Au$xt3<B+&tI9<mS0%H~(DaW7cT%@8wpdn)<voQ+aqrZEfDX+)i4r-zP~+^2?h4aEP4w4-IX<ON~GJrQ5%ei{7uext-EIH<*_;n(v<b_O?bFg1NnFs5%GRe{2VHYx+g%962*@V=xcbDzEadTI%h+efxYfE%)|qv3b7MkC@%5u&npBXQ@2=%9VQiD?<5Yj=!GDt$j<Q+WS7eB3Ip?`aFcZd_Z=QmfzGUH#pDYo_p0i8_!W*ZaznOx%nLB<>qsgnS1w}-;ePe<+nGUqx|;9bCjPO&mmrJK8N`2jpq<AH=iH;+<1QQ`!}8+{M>j>@aNNbPVn0s=f2<GIA{Iw80W0t-Z*Fd{*80ZZ*QDyW^T@pxzGFk8~eQ9-q`2;_Qt;Izpt^c`t6N<)o*X?tA1|ms~6<#tA78+zG~*)zUr?RV_)^#8~dt%y^MX;%)Ncp&y9W6%)NcppJ!uV^~YoGtIuSXx!%3pT<>0Pu6Hjt*Snc}^WgVmtarb?vEKdm#(MX1b6xxGjdkti=KA&fG1jj?59U5^<lg%A`!Uw9nfvF0Hy&gC`u!X0*Uyc0YUbwWHP@p*KgN3WbMu_?#%Z2Y-uoKs)PG-No%-#K^>{(fdi3v4V}1Gk8|%v-r?Fnl+*>bxKYy|=E;xU^e$4aN>&HBQz5Cfbf4$s1e?J<l=E3{EIX+vh4=?xb!$n=}wq@kuW;5M!T5rFoojcaLN$z>!=UzXV?V@eV$nD$5xYxJz=jr<S_1bH0KYs4DpLd7qXUi;o{8zVhpPNFf=jiXde4uJSZ?4u}Bz1Dz+cz%M`=3<PZC`rLB7NPpvo{2DQCMB&BmXGY+V^@~t(Rp{Ew?9iQ0t}k26g|}eNSJ%yIMtqd5He4u3v8m=C=3!wAQy;9)7!*`hIuacCCMFqOHEa)E}+o_JXNu-96je&C{wccJoM44|QJuUO6Y2d*cr;sOjcb{1V#7t8?p-<3+)|^poRiop#vi=JsiF?|r)s&k5$%#6fC3KH6HHkH?p)&(-m?elC-XHS|CJcP+O@*HHO{*=n8cU#8y=?RrIndFlNrYChNft2mh3lTNDftUO;7%p;7`eq>&5Fi$&~uFlsFmT9@Yq?&4<IY%3h{Z%EE4;!oHksaTveW1r#ci%|cv0NYj18bteyp(=K&n|go<@Q|<X?bWuiQ0e0*3A#*f;@c7I_-U}VQaMg%FL|;zpDMD!Fv6E?i`5*^U@K`)qPd*W-Sjd&QarU@Oe%!7hXQ2NpUc@GB>IB&1#ibX5M{uq1I2s=d^K#rc~RljdNj2i95cQmuk7Vqmh=|m;SEKqbaMS!92n_Vt4PA6U@EyC7d<6IGBfOr>OC~n~)dG1-YnspimpnEhqAV<F}6W(Z|^*$=yH2;6eK5I&r6#+h>QWePCc-NiY|eWT^K&+BX`^OJ~Nr@9X^@&+o^}`MsatPxY6y^CfNCENwjY_kG;=jZB!WkH5n>HxE}>px&4BPK-L48_ey|>+^#Bo4GeXX=lj2bF=fQ!eB14>S*&Ub}mxaYi(<F9gnRn4(1}Gk-Cm^=exO;yI760=e24++YXOv`IjNpzR6OpeK@Lq&t*+LQ5ekAx=+_WSLD+rYCOmGtNthMi3W2q_iMG^ez#rShbx!r^I7fDlCpBEBwfoz(?Zq%xKmm`qER_D{;vy)gL&H2Eoz)cw&rU6d-<lgBCVh1{bQdiRr{;Y$NfHRDCA40Dmnk?mmc_&kMP>Tvj5~Wpv8anC!ZEgTmHX)@+luDL}jO{QqoTe#b1ST$yN9%{6nW6gK2OTo`&~^EAig=qwrn)QM@O71Mi9VaH^|Q-JE)rl0KD^J_A0C&%kHFzv8p-Ij{%bgZG+4NuLWp!X-b(CBMMu;%~uRTrv-T3!e{*aLHnPKK>5eh)Zt9-@zBbFY!hAV)!*K`3=4pUkbm)C3oRV@#Szgz8rtwsTHu4lD-G-#`oX{;4XX@?{@%xgG=tiC4a;Z;K$%;{1|=~p1~#MJuUqYvU0qZc{xgY6<8Io%DrEO*V2CziXY;?;j2Y#4XlRg_-gzE*a!arUkH2Q3-LGMBe-ODT=I2Xavm<Z20sDU!Zo<$I(#Qw57*)A@f`SfT++sK@O=0WTyg`Rj~BoQF1Y|NzzZqqQTQGn#Y-sZo8S_B6TSs5!zKTTZ^5@y(s#gRxa10a2mT!_#lOQ3!9BR-0sIht93I0Z&*I1Nb0T(+o`dqfl>TqBI9|&<j*?ypR>39ZeOZau(oYJ-)wtvb_(}X1xDfvZ{~5lCd-s;~igAkn;`Iq!axMNlJPg<3-u-u&lKwp<eJfm#OXlEP@vmS$E?Iy}7UGgo{40DLEWsr=;hVTuw!!WAHhe!N{UF?d@8JG82oK?hxZVdT=|919_)qwG5xe&1p}gMbc`aQyRRJc#I6RJPp9tkOPK3YUzi`bG<6_q`k&>PO<uyx)i(ShE{+;w6$PVL&xqd%T()Yrx_*SmLUbqe4#+>e@q#uO`@q^6KQFtDgl%M}7ucgNa<|rN};)#5QcuM*aKARl(5yrn4-%G#JKX>Xgr~c;DCr*7zJ>gWmQv+c|d?5ZLtcgE~4}q8AL-1j+J}#MzKLba?WPBuklT(f0H82^!2EP*4$FIag@G?AvUkYpDm*Ul7MZ7v*6~^OL@k&&@x;!qQz~k_~lyvVIPx>@C5TAz6giqo#@!4<)J{y0Xl0FX(!{^~|2j=>1N_qs2#3T3un2j&M<r(#|Q<I$<@6=fMyi=p#2&bNgSx%LAs-IH{Z~&fw*MNiZ8h9O;iPypF!7RKU-Vlz!8{#)o(%Zo2@izF~l=Kd8Jl+9+fRdgHC*!I3LzMI`PIZD4;AC9#6<nV0F9>y3zd*K(lD-1Ig0H~ehm-O5@#XMk5qrLsz7&oZvFBmwiv!ovdzO~I2tF@j&*9SF30!aQxn25vI6}mp`K7-lV)umieL?zMm?dK0HKfmhnIiU`Mfxl_7?&I%V&8qF&w%|z?7Nb5`CaN&*cbN0CCiK0I+ZThZY5X+mdC5$7r_MlBD@x?f!D&5U>!UOzXI07ufVT{4e_h->*0;~^>}0025*cvgLmW2@S9-={ARp0d;o8ahhZun#@oY(@b>tfunT@CeyfPBjaw<{EuCr(?}MFi$qD#<_!#&CF1ZAkd=Hn*#wADMWANMIO}Ka7+z$VO-;Un{o8!$H(>-tup5atEr~1PRcz=8lyci#ZKLu;!PvJvhU0m{7d?-GglKw1gf=k|pKZ`#{NgoaG!X@v;N8=VHeH`qFOLoS`;V)6rC&34C$rOAdd=aMLFXHz*bql-$rr>wr?cjrWJG?FIjJL&G!H#$<yal`$Z-F<3ci~O(8{lpD4fu7i34R^k0A7nXz%Pe&@yqe6U~T*={1SLEehFR;R=}&_m0>x&GM-3D7cfJ_exyH6NuNSVe+~A>U&E(6mD(|`T&?nd_P>nBek{4UYX1Yd`Csb4b`1WPr<}h0UqYsKtdO8SKsk3oG?lX~{saG@P?-'

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
