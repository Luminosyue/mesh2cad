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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8730f3aafc784a849de8e9f2d9c707f8/part_010.stl', 'relative_path': '8730f3aafc784a849de8e9f2d9c707f8/part_010.stl', 'source_sha256': '2126ff5913f031ca7a7766427d59c91528f3c6e46fac058dd0350442d9797724', 'input_faces': 150, 'input_vertices': 143, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18115097284317017, 0.3173943758010864, -0.2160804122686386], [0.1811923235654831, 0.4216236472129822, 0.14698368310928345]]}
GEOMETRY_BASE85 = 'c$}q}2~<?q8OI+AE)k<98q-Q-Tn8g=!40FCCn{=C#4TXm9<qrhs9@X)Ph0{j#;8G2L&qj2D%R9}3oud8w8rhISTHA<)N0KsHaR&iP1UAz|KFcv=7pTo)6O~f{D1T3d*6KbzWeUIkC>>s{>?S{w9z`1MHSv|tZAwRYR$EIN$GP_6OuBzrp;dHr!|GIJ~g@_di=<k34Yo<ZLvKuDI+1>-p^+5pWN3TYO^QLN}rn^pEh+?dSa6DBjaDqNb>j@)8l6+dA^7A=ouDj3+ohW%e4KEpC>#en0LFKDfOu9@1I|DsG8Qr9#N_n+Tm+SZU3ykn_qS~47EQzjre9^@SSnfjw1eiC4Busw#2XMfIP1IWfH%8qvU_;HhisU8+`5VP5ADF)5zoQINv9~x#_)w$a8MI<X`(Xe0`-q>d|J5lRW9;k;j<+t<)dhTJj_o!nYkikNmEj>N5ECnjw!d&)kQ8Ov{I_^_ngD8-BPS_4r>rseH5UVae|<+=F;~E_~PZK*YPp?%Ip|1x-Ie{MKQT=RpJHH=-`M5dYTiWE_Ua?nYg4gW+pImn8p`Cz0Pa>@OwgZ+M*4e`?20T(@CmiFf_x$xzg(yMjx+`>S=GggpAWjm60Syws^(Ig0Ud&Pg}{Kl2#kU7gNKf9vl#jy(5%xPtFX7P|2F4V%S}eD*57|Inorbvd>lLw`^H0r6VT8HhLf=fHPWorP~}@sAQ**ZURty8AJFefoe;;2$hMiulwKG9RutKH%-^S<%w3Z}-c53)lu<yILT>8`l|mjPoBIfq$!;)Y&{5zO7Z#VfaPwil4P!>f9a--)wxb0(k>n7zdZV>X3JS*Q2?TC+8*jX4xBvcO`!*^LEdggQ$N_5b~R&+{o{|nG0XPa|iLZ9#6_Rr%i@$c8@`RbJE3=`1_!%2k^UNmm^+V`4IQZ_V1bdkzZ>o`CF!-9@A~WH?@fvA7|?nslVXXKEyj(B9D>R8RKsZ`eL6?e;cep{m$v-yWlULC3QAfi2JKmmBQBp{bc^6*1_|rf43RFwnfM9>hC>12ECFe@!y<~`9C$d2)`SiSpfguLFv~b1LI?kXb;~E-y-v0(@&tDD-Sj!e%UO^^HuLdxGrEfd@~@T64!^V#XNWYtx)_MfmMjh588x$AMMUZo{AuOPW_gh#kfrV>>c<m3njkc=WpVB^w5py*Pw35ufJc8b<n-lAHG?A9r0%Ru@8}Fbn1He6_xOvy}Qdi7;ayOd_&hueBvQIhsK17tKqL+AocVwKt0-TD{`QVT1h>z`KJ)KFDo1Vk~Gxg{MR|uV+MUT9~x1FJhqY@$YYEt-Cm-8zeOd+*~~7Id0yi;DwXHG_|^#@|ItCIXT?t6JRw;!4#5?__l`HK#CJ})aK<}c-`Q8{|8(6cZ{N&|gzsu#FYx)@vq!|=Qc&y@zx9;l2{^IR$N%afe0SBo13q=qcg45EeKB8uFyB$z_}H?t9kq>TRCSJ{mhpE7%vtTI<$f7{_H~Y0?ynXycfF&Q`Cv<Lve8k?{4v{)fp48}TF-0mIBJ=n&J~C99ktA7tz_3`M=j6AkG|!(aOORLZ+*UO{_Syptk0wI-4giL=htv-*ahG6ygMfq!ndvu=HPOPx2z|w%YTCZv-RhDH}+5KdZmy08vf7LxAO+pKkItvJdh^qqGkPb{_`648S8qheQ{IvpY}HpZ#3FkjPbslE9;+SJ-2OLBmJ<h{{seMT&??seqpMtXZgWW|A-sN?|duxuup%vA88Gf<h*0qzii9*OTE_pZpNo_-m&bbHNJH}wN=N-`fb^ljg$|LBkuieGCr<5xG#F~Uij8?g6H6h`C>g+xK7=MuMf~A&(2IaSDa~xe!DXLWxX1hAp1i0CivEKiz{UZd~-&njPr%XsK?wJEawZ$`NuUZSA5HP$@%!N@U7=7_x>UHed~EluRbmQrkipfhaQvbKe#CUu$=46*Dgyx-aa7rH}PY+zjvF-zHK=ln%S$c|69+K#{G9sdOt@-k>g{;PrU@+dM-6~x+VVpBJsOiM7&YFsSLj5eCy1rF7qCrn)9&hddG5^Zxzz7ZO3uH^}Ea9o9jBt`G0%0%!Bj$#IJWjp1aUXm{0Bv!Kc0NOU*f4FKq{3@7G%HZ^<`^cb1KZZ#~Z&A+Zu~IscnW7f61~`+_r|Q1V#bFU--WCEoHrVw6`(e#`rdp8d!tf6e=j_I=11sOA007}W#5&-+x2&s$=jKW^)lQ(x0mYv_4POpf<@MO3Ex)M)Lmh^amQyH~_s-T&WL#0HuwQq%mY0c3x&My;d$^ik|btxHx~pX^7jM{Pu|M}C4$aUiuZIgs3h+LYXc+>A}})6^%)N}nP>O>RMLPF5O3Zb5Fvrr1VpOIF&EY$La4QyfBlo~$&K9766&?LqEJet|lW`~o?QI+z?r?nR9xD;-AeMeai#O727MOC3V)OAe<FB8QV-q(+dH_9wqc?(Jzksr{(^$^FO!*c9v32(r?b$vSyBo8l3kHijBQeVH6Xj-p18BUpD7o8pnwA>@(dXzEaMG<g(t7<m+VG&PbO$@?*yP4PJDK=L^9Sn7E4SaKZoH{>|-6zU|hQiD8&JdI6pGBuH`bOt$@oXVy+jXH;{bS^oKoIzbgRyvQIL4KW0@dD~%@&a-uHH(}{HrW*CP~Rlykn^ak$x7Fd^T=zdx#YFvRi3tzx}2IzUQS*{T|riwO<qP`N_~U8l)QvZ@j~i+@<MVtbv8Mj{2H6$nbcY2ndIqgic_esl9eWrQ^*O_c(T&T<OK3mHpLUE6Ua(mAx|X7QXS-2@=I)ryHUH7yOBFnyO5Q3B6lX+sqM&iatAiWZK%OyrLD<r$j?!KO;-90`8o2lp7twhOX@S^m?*zG&FlWszj}ZAm}+zL`NyyIO5g3@`^t`<4eH0kKulDC+7CUOXdOI!U#s0n`wu$K5!e'

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
