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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/98c26e7d386c466e982ec81e89d42b06/part_004.stl', 'relative_path': '98c26e7d386c466e982ec81e89d42b06/part_004.stl', 'source_sha256': '35095c9957aa7a9a87138625ee445523794b0caf0b0b0dad390e46f43454d4c4', 'input_faces': 268, 'input_vertices': 201, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17066055536270142, -0.177668496966362, -0.44821494817733765], [-0.12051542103290558, -0.08422168344259262, 0.11453139781951904]]}
GEOMETRY_BASE85 = 'c$}r032;@_8OKiulr<1`*{=x@uxzqJ16)wC5SFkcWwX32?~y1aG=Wfvz!eb%*~9<=0z7uIkcEWoAs50{r;5xt1zFnHYC)U|P8YS<YR~e&*K^LKGo3aw-~4~)|4zPp?%BRahUlo^#vO?Gd72FBJY?9s_Jpu#MLLjlZ|aKV1aI1)Wy@Cwkx=flA4lJv5i>n{eh^6~84-!zw1m`%u|`CsZ*;@}Bf^)Gx*|1h+2WMcL@)Cv$1P3sQa>#zZn>AX`wboP>;Pj}{{hBY<A3~VL5E-szje8eYGC?+i%hNVdvDiCKKZPx@bm5|zW?U;7ns_2zx-I~U;b<1hZQQmk+6^Z=9JZUWZ&{m;y#&QtoZi(|FpSp_gC`R1zWjqP5kbblHWf{`0sbVtK^@TRL6hs-cZFi?&qH8`PbJfdHgv$YkB*l62&JAuGetwGDXSb?{Ti0zn9Nce3JKd6@PA<_mn(V{g;*ebK_5nZ=RgYef!w=$~>4`;wyOnJ|8K*fApPl-aj)+nIF%%fx<tqQSk%i*UEUFi!;>uPhZ4+t67NZ4||6D<`_d+_rQ{-!oT6=ejw<An9ud!i1BYLyes?GwMpE!h8$FU^YC>(PV&3mw-kR%Fwbw7{_BqHd$#R3$NRUu$$dL}mzal&9b*5CD84QGflUj!Z#Dh%$Fgq*ea-iY{mBv~PvDQqV!vg~Q2Kk$WbplCoeL=a&5(caePVYCR{C3C`S?CDKX{___r!k6_k%UKhtfYVZmXEL)B>fy6~2tGyA`xY?f>`FV&3kDs^i&ZighoX#^=G`*Vo{>IKI9vj<2ta;|IPOUM`;tx4*Vtj<2tm(PVmq=g9H(bL95d&XMEm=g9H(bL9HkIdY$?og>HB&r9I=@=ILz9}~~-F3yMJTaF*!t8{|gKYycmkD*_c%l&Qmfqn~0W#0qej(L1e&STx^FXnaRsmi(rd@DTXtn8a5*+Lh0t!~J-pNuG0-mB*)^*qn&(KX6A;rq{bD^l{nx9bL0$>a27x8QzY_UB3-6TTVxn*t^O0pZ(OzgP0uN5gpC@eJ-)EBE)qx7*KC@|f_=l|8EEJR~bp+z)fq@dWk?-_pk8hflK0a+UdquaDE}n8@!9zcz1<Z)@{rz$Y!j@|AHq{k8ct8pVkFM_We%pM0yXqZtH$Lu`SP2flTpO{KCwAB^O6(68+)8@{dWD*~Uqe5gptb07U*%`R8`)^G6jGxhxs-{`OIf8z8{nR!;p6C!*|I~VrQ7sWlSoks%S#CbH*BE|l^S$l;m`a6DL{BG_W-8WY><lEz}mdL(2rx*9Fv<p?TZ@~9F*j_CA<iiAU52feVDEY6$e|=`5l4l&&b8Yx}B@cXSWn8}O+imCab3|6Ptdo7e<6qmHtBl|AYe}s<KhC+cPc2gOIKJ;ej*<sHc{EGO;}82Q-_M3N9t*yyj|aXrXT?c54}q_b)Bos<*w5PhnDA|Ve!dVsX*BJ$oX3K1)jw4u`+;j$`2O*0>*a@U>+1!dgpSQq@?1s#nj=-RZ(N+o^V-_}A&#%@AM=9nt%c1Bl{}7LSyrJu_wxjPUs&3Hw&9cU>V77Uzp<uR$@5V7X8gJ`#jk8vEuTAgJn#w59a)tp>Opv>*yo+viSHNiE%<iQs1muqf8;#W^Vdq`{)Xc}sV`IVkNH%L>pf4E+@Cz0AlB`RlSRsNKNCJFIaH}U_g=cFQ@(d<<o=$+d&K^Kyt_cj51+jGU6nGP%pzVdjET)_mFL2@GOS#=za9Ibxc?unEtLD4@U8q!N`5n{sqmNPRLlJXQ-x1@n`e~#f4j`jiD$>-VrBgB&9<=>a)0aFdt%(BA5_TwZNn%0@Jampo$;ipm>1jw&i5j-%Wd&I?Y?#Vz;A``d|z^X?H<;B=N@)^3%-SY>ps`%kA3U-`n~P=`n~Nwcee1!B602<--d7F+&R8}&%1fFd)^&Cd<*x6JAU}2R@@uzIJLUqK3A&??l>di<KA<h3*W}Q=l0j?h~w*Z#2qJm=iYYbS*tH@eyzT^`L+7u=6CkhUv8XG@@sX+&7;*F_kFdx<L1%ojys=P-Es44b;r%4)gAYJwYuYuN2@#TKGEuq`&_N=xcfn?J8mAW?zsK6y5qjDR(IU@(&~<zN2@#TbG5qT&VyEW+~;a_$IYYF9oN_DjyoQ??nEnpm3uUo_(MbJ4AE##IuKu+^d~uH^67&%{3p5O;s4#A<VKGEfBz&mgpOe_jSy%n@Y6KH33~ydt-!tTSrce8a1VSI1Z@oNiO(8A3Ahi92pVmn9l+uEECd<~9s=zTeG2?z8bfIefQ|q&zbibZZNSe$TSMD`yVK}~adg927!Rj0kj6;pAaFRw(F*g>9COhN^U)aZ8-#am%JvM6AL0FjF*m{RdO{5_`&(&C8e!1Z;4pA+Xd5uocHrLNzR>nyrk%ij!Tq3}!Av`X`+*}69Wf_;Fh6W<x?n9rp&{UBXbi&|4a52|E~HUHBM({*&I6x<R)bH0k3s9e$H0f7_29$c1JJAB1K@qoOW=LrY^V*+2K%8kU_bacv;uq_d>UE`J`K)CFfO7opT<ix)<HK&yZ~*c>%miKOsBC7nkw-uw3()Zx6{~#-`j<Lj5pEPNMkH?6nHC*%`~2eP6TJt*hynHbOtyUngLxU@eH(?rb#>%ZKf#_zlb)|r4m1nHq&H@C!)=CiNq7oX6luA9NJ71Bp!=4(>RGoq0Mx$#ADEA>XA4SZKm-Ok4KwnqQoZJOnnkRhc?qBi6^7Y^cC<j@D%7|Fgss)@LmBYK~I5`z&_|Pun(LFJq%6+$3qW*<G~*2KClP87@7@U432~P!ExXO=y7lY*b6-k_JWr{^TA8N$<QKjGI%Mp6ucCi0<8e2fYYEg;56_ms105P&VXJ5XMop3uY%WuH$dyb8^G(Jb>Ma2HCR)&_Js(>CD2rG3Ah}Z4lV~*L)U=UAU|Vvhs5CX7<|T<-6w2+O-4KiZ#(#Hs0n5|9{e`=EodZ|=@{@^;Ef2z&fUb$>L%y}@FwtP1Y_sUVt2<@=v44l@J<9{b|<krHWq6Vi#21smqr#5_g^O1`Q0ojXO=XEENN_6(z|3y@0cacNtQH+jCUaz?}6?GJ9lm-bb&Os1?b20B{0+Z;Jsj$XF8rS3%Un93mgNT4`zFB4ccqqF)pTYj>Z{iCHM?D2U-ix0iS?g0G|LKfnEk50Uv~310MwMhh72i2Ool71Rnw)g`Ni=1)qdgflq>Sp=ID)Z~=nxSsL4DY@zW2bQ1VY8gJ0}33N1g2aR`WL_ueQqrl6dD<qzSHq&28{4=zfz6xGQ<L5Li=<5<MLYwJp;N3Ldp)nU44W0*G3tcU7G}=s8N<0m1roWW<r)V?%g~TtQ&Gcn(bW~8I4#EHFzc~ExWAQK6@_%^He^dQunEac2XfF33WzkVh*!OPwrMwXz*dGkm`Zx4DPD}'

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
