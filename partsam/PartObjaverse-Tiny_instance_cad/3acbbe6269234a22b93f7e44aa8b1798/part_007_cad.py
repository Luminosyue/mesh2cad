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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3acbbe6269234a22b93f7e44aa8b1798/part_007.stl', 'relative_path': '3acbbe6269234a22b93f7e44aa8b1798/part_007.stl', 'source_sha256': '3eee9cb5171f8386997110d994a87bf07b1aeae8db7c1784ab472b930946079a', 'input_faces': 226, 'input_vertices': 150, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[1.0840454933713772e-06, -0.22125768661499023, -0.49533146619796753], [0.10686757415533066, -0.008375927805900574, 0.4984809458255768]]}
GEOMETRY_BASE85 = 'c$}q~2~<{P8pp4S`+{3;xqOI-3yKK}Zg>@Q!6nQv48ac(6h(G3T(1g>=ALPp4!3O6CS1rRsk|;pqG{#eigIg8v1u_IPfhFG_y7C}m@{+EoEgq}&j0uQeZS{E@AJO*z4tqYkFDj=Qj<R~%_?7#yRnI;sc59N)Siq_&rFPq&*+_;npHz<3Sa$I=ra={#)nU-p*^WB^qmo(5tr^e(B(TgA=uZ?<(rU_o|zt-JS`=CM!fPz#wKONJATHj*wlFEbGL{3_3?8BboX;DcKwfk4V)6pyZ#44R4q%2b{%s>_pMVlRQXE+;p?C6c}@9N%;lTP*R~ZO!g#+&&naI!ANr9}^LWJJs=n=iwM40F^Evp|#J=#Y)jO}@I^(ayclo|rtUeo;0<YtH7rvJ9ce<a!xcm3uYd)QiApbwMoW|#;8r?*Ge_!~n!P)P_AEd+A;(Eb1FLghKJl`%A|EB=>*6zF$_?&lA{H}xG+lwAJj?beTm*IOmhQoLNcKSW|Ur&K=e-|e8B={~v{j2uEw;GI<@r$|~g}-tid{>0{+K(3tFm8DPd@bSA7}Zzz<lfc#V||hAR=$32_6O>-d(6bk>a%rQd?R#yv0N|zlKN~%d;?z_-yeC5ygu;F_vgmS_z+o_FK1mup1@@Iu7M+~t)pwC_{QK7)z(oT`ZatjWVqxnoPQpl!{`T%hVM%2ScLEQm^&TU4|)!D>Yw$%I+`(a;!tPAC|So@o>wr>;M)n9$Ef0yxNgsOS5e>oTQiZ*vjO&l;c-j$Nwc`wxNh4-te08d;~MhxvXk(=dwb3z|JjD<gC2P^8GX+7hi|)XVP5v8(iG&$e&rqXdH9Cw82`iERMh$TA<2^;gZ{WTCZ%Cs<p<zfrJ2&tt@J-V0^fZ2I{IVm5Z@{}aaQVIfd064_e_Vbh?M?JPL?{~m;>LsFckB(>I7bs{XaVc<Li8Y{bR1Zas&CFzXRX>_5$n^{ZI9=Pqbm(Gx6{Bp2q!aEO`g_uO3q_{;t<>znfv@;wOr4kDMgyvg-!&xSDpGhkBlEfjnmW+j2gn(*JcM#v54;aUa=hZi^r6DfRsF71m3?@%j9!>#I-wPS(B9y%5?X3hU@<Q5WlI%`@TK2Wy{|`)6ATuDiamf$=*wVZH2xR9P=`&2r59<5tqoCKoYY|G9hx@-#SwzG;UJO5g6hngd<#jd{68pTNBIDP31${Fx-w@0yw@_mO7;eB;CKkYC%H`xlIh-<1m;KOTM1XZMr7ovyJ48hRe{wVFj@zV_9;r!l|gDRR!7O2a<4LprU+^}A%C9#>RNS(l*S;9F-_VZDsoapFJz?mE=7`bG3X`|-Z)|H7zE&~xqNe8_kOb()(N!nZrTCHrScDEi>O+G8{F`=rRar?iyw@Q17L_5Jl_pL;C)MD|(zXR7wixH<}b)3PQ#2frv;*8Tft=)XPU+ZWJ>#P`In-&fAJl8_zv-ohZcA8R+efa@92JK^(uu!8r>y7$`&Uw?V9JTHp!QICFNs)@RSuE@Uf-HP>cU-5ns^`s4z{P&s`qmF(B;)mrTk30AiIp4ng^2Ms_V${pUI_mBLyD*Q8A#(q234b5{@QLu<HCoAiI<6JY0oR7R@U?B8vLB+o(N8N)dl~t8&KR3dVn0}8e}`{8H30eDmj=r@e6!c9$e&hLgz=xIBEQ+D1im(J2G@73^zEmw;9Gafu)g{VL-vDx;B{!T6>|T+U9%K<&Yys<O&unEp7K}Z*H0D0uQ)fX5jU_utz|WLWBjJWa&8pVMIIyXIQ)w9#A@Y%>zWyPZ@^!A5%pUiyRq(e<X-sBeJl6r7!&JaFKd~P{5J#SoIl?4Blye3cTLZf`TFFe|5nKx@U7ruGCtrE)=^t`VlTdTs6E~XjGp7sf3tY>KIDJQKpxW$K%ec_rQ&bjEA{vJ2J<z3E#40`4@><+pGQ5~%dHOJx;&rV(KFAYzRZvV)%v`)jXbZHG%kQ1+J^l0y4LW`I3M`N(TT`o@9;Veze_ZHd+t%WU${RtuUN@*!&}~G?k|w@ws|6a*J2;6qkZNV)M=f4y`bv)>YKNs|L*k#Z^7RcFZF-bUHV`Y!Z%hOlRC3B>`!-H?}N~S*Q5_V$>&h#v6zEZ=W7}1xKG{rV-BI7iyqSdh%@rOw<7|+{X!w~=(dIVx;IC|*VFvvIZ`A3L)5o)E_`Fr-ItJmdp6E7E9gxb-#H9<>_Hdg{`Dvkzh<P=|7$(e<GS{X<k_+x?|a7Xqp}~?2Oq|Dv^hI*zm2|!{jbd*SIyV%4a9Yg?+f8O=eyL|;|V;+%`FX&V0^oocn`EnUc$L#&kBHVt}Bu{e{L`D$q&qjZw<I4&xI~QA0Y4Fwu>Jy3FnXQU*`<^Q@RJfeKQQ>jUQXf`|#y__{Q}T^w|t7k@uOrYf?{1EY2C1?-$798rk)2<l*_R-MfSP&V7F_d}~8(T-TaVSKe36{qVIn^W?d6(XT}I#~Ju$QULnkZsdu1X+9l}A|KCTci+pX$Gi~<-{?{<^@sj+0oS=HzLo4H&%vB5%*!gC1>bBqPyFOd7;h9MNuEZ9cn{a_PDY*Xd_%7L?mWy_-@Xsy%@;PpuXx|q%ah^TOJ6@K`(&}qx8nVF)D_8pB<r23zBR;#U-8~$_?3#^_3z@>I*EF$Zbef6?=1>(-35L-khiS|`lFZmSM#lIWys^c9su8*-wnSPtWyt`!ap%e#`E`u9{su0e{fQDf88EguYHeK^DF9i|2Yc&AHPRdzgbq*ujr4Kv%l<Ec(q@%@7<a{rcFalQ&HdfHJcDy<)^GN)nA4F`=7Fjf&bM{*}i@I|Gz(FmpL_LsJoUrgFJ`qrbd#LK2C1z#AYWvsn3!<$xWzR$Vyj{n~)nZ6gQ+A<c8!1)J$>%a((Jda(!|=Y7Dt9wHHIN&QLso8bfaDM0+QCJF(G;r=3{GP@LmLCnrWY5k{Rt4kJf16emy<$qD3ihT_H4Wb$J23hE;A3i29i4mpRltzjt6Whh?FP`sA9k-XlC4Nh!gD1L^qfor>gV>dI_a&6Z#&$En;T<0z1Rn&FlRb+#jL(buR48|g^?IO-Ulab7|O=iDlG7`CdiR^U@V+z-F0$HbyAdlcW>kP%csO`yhsdcFB$x7Rj>yT?R6niifH)Sa9O6^VV%{sbLJCT*PB6lS>Wlp8FsIADg$Tb;?A7Ci<qIM#Ck;AEB<Z$vdYBYHoc{VkHJe!<FO($oOms1y$my@%pE6Ca8mDDw4rMcv%oS5gtlMKZf)HHGpP5!!5dyu=62T=!;2azXJBgvD=anu>)IPzR-204Q@D1O+9N1Yf(9Yqds;vpwOs6pf){(A^@6gh-Eo}oC3`Y1VyJe{HV3F^b-C&*(MioF?%J5z^|hq0#4)Q8BO$sHMreW(Fs^?VF;VhFV_S!o~g5b{8(KY1W|0JSH106Cc2jT}twPxT@Du%7-5#i7&?atM1G%1}I!p*WTrMUG;BV;PE*oJgU@Q>T-sv+wZ?#ZwuI$5F?S$C0~Gy~%B;t*PGR*5sDd&g7Ql7SxX9j_gYdhT`VbZsg|VX4IbKX5@BMe{wtWgVa9c2gx0%eaRijE{0-XY9QH<+K(DY?nfR@9ZDWfevF}b5_Jf968RD8K=LExu?)qdsRPJLgUO@GBdPt#N<+yb$r03v<OuRCYAkscIhC43uGm|t48`-ESn9+Qt@4?!xZ+u_cqMfqc_lfUx<IQuZxt`6&etl>XT@366s__+S3H{<uT`G^il<ShYL(9m#o^R(TIKUau@|+AR{1<qte#ilV{6oGS?fRj7g6P(fy2J)e;EDiH><ynSN-OBC)Xb@=iy^(t7o|L;H-&5+)M3j?Vkp)!wL'

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
