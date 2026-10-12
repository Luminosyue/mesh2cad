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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/439ee7ebf11d45739dbef21b91669c1b/part_004.stl', 'relative_path': '439ee7ebf11d45739dbef21b91669c1b/part_004.stl', 'source_sha256': '8d0294f8f058ecb155a376f9df5f34b85a172cd87b62a11f92652283b5a66d95', 'input_faces': 126, 'input_vertices': 117, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.16209198534488678, -0.21022756397724152, -0.2623680830001831], [0.1639748513698578, 0.07896632701158524, -0.0909048467874527]]}
GEOMETRY_BASE85 = 'c$}q}3s4o;8OIMO$ioM(6hsUQDI(Sf8Uu<bTNP12xcESM$)bX&;Y|#-apuA_lhKBm`bZ2I;Tmg7qV<7ROh8#4Vjxv1ooQ2v$*OTC8I!a%%9OO&?)knymh0G=PJ3tm^Z(zU-+t%p*|WP>ED57V`w0F7iJ@<s*H^d;AvIR`h#k45<y$x9mdz|I-svDbh|ABg?@wC0(vs#Nc8H&bZq6;+R2mwkghuDh3!Scn<`tEem*x~^7nN?#m3&#wi)FbcFU!v<&NaVJojp5py7GM3bY++FKYrZIDJX@lovo&;F{@5XH@cFVq${b7#H~Jqr-&a;zaZWA;1qH3>XMUo^}P*Tzh*Dh>$j(VK=q%#!+cMoUA=z%2#?z~=GP;+^|e~A_w77E<9No>xYo`$c-$)<cJ=Db-P|YV`uozg#suzvp^CU3Q$t*2hEX3eu#5YA@q4>^wJ(eNq@H`1=3Td(`xIyJd`?u+{B56Hyh#4pI_B*MxZdd@)r)&6JZ{ECyFN<pa^_73sE^{h`x4bRNAkFT>LD(+k87pAX)kd7!p+C2&viGhH$u2RF`m{(-J?;xGC7EOb;Wz+qmyZ#*04!D&w!cKM>s#CKFUE~=H0Q>N8eJ#<9d!~UK2+3#+^XoHe)Q$C+_kQ9ygZH_q02Y+uL`9uiuBfZj)V@KS-weXs=G8ajk=b`>(ua*GJhh)Ir}j+&@Mh^j$Nr>))A|Bv2oH<8ta_d+RQ7Yi~c*TeX@Nnvdm=T))~NZlqiyZoA#a{M<1b*EpE^Asu(8f%_cYLtF`OA#SU!C9WT?<ns!;McnY&OI#?Owe-DmAJ6}{Rm@LMAg<%O8(-{T-W+7dwe4GYT>oa`;_H6Czp~db-@oK7^2Lw%zHm!q{=PHSYu!U!KP!s+7aXnO{p(HloyZAh-ktph@v<hqUJl>3Q=gl$`{?+``~L`Wy}9ZPeg9;ji}!y$*B{$JT#t6XLgPPtwvDfQNhAHct-YJhcYgr$uj_~_H=4Tn{x7Ph@sHlCrsHR)U#EWg5zKG(zee64LR?MuAg-N`<i6otulk&+qj@(B64yJ%6Sv-fnYb}pq4}xhuD#Un`Xb``{_VuA9qzrn?q40IJ}qDNP`%~QHSz<W6W1C-s9t}`oBQ0}O<Xk0D2S2gb#)%qTYEM!?;Xq|ero~qhH1>JOLj`G=RQMRXmy#iF3&}tBYq-NC!WPzUHJW3$<??LT6d8SZiy$ZeRq$qtIAwBXS_sx`m}3y{87kHB)2MQcHC-wP)YM#7sWgp^?@_2v>p#Ew4P!C_$%}2x~N01GoOR`Y~<&yk!0ibnFT)Jd4}(&9_Ew51Mkp&GMbj!agp(97q8<&<^jx&oADpfai?7DxOTz)id`Rn=C&0Y?-TD|@;oPEotL)J^%Z4~%r|(YK5hNg(%cgI{+GM7&id^fT7Ojpyh7`EHI}c-=U?*rr&rg=@8TDHeQmhD>aH&4f8hNfupfl~0P~Z)e+2fA9>2IY=4t!Q{W$UAeXC*Lstq@YKe^9!|C&S8*LdPSTGYq<ohR<QvbXDq<2ve91w8Io>Gd%quA}O8knfj|2HS{NY@_p64t+z{O*<LcPUk<xkJroM%GalF5pgm9U8+;A7SnOs?iIw<sXyoAKg(twH$>bR!~0wFn!(TOibuq)1#j~CUdHc-nXVmF|8kifH>y*Kixa=&eHhik{Tj2l{>D6-r?DfNpYQqk#C4BydR}SuAM?1?McilSZ}|D<b)L9Uc7V9@UL)-r?QATsM?@pn4}47TCp{&e_sQUS?!WIm&$~Z?c~UF$aCe%g==cZk!=qP-TjyS;_m=VJBp!GDJ?6Gnt`E+jdRyXOiK_uA#BG<i()(JJ{Eh4Pj_3Iot)_Zw-}gMv*d%%nYs2d{;Lu6)`R97B50BvI(%MSqJ*)UVfO_Fu&pf(?>J4!9XXl6uE%Pk(Kf~`ATSGH(Yvn#WuDD%dp3`N|v%82J4ZO}a^jB8h<@$%b&cj^&)i=b|9uImi>cjg)8RB`~Z*O^AZ?XH;UQsja^?YX`q+HEk?RhyPezHp_Kg0g?pX^)b{&zpw=S2L!KiSjGIjl340m+;VUym$(BXXvxG*emdbmT1LZSV}_3>>!&lKDkQ<`VcuWa*obOOQ(;nakmM$kI0>mm`-!G8e;hkPA%}nc4!$ycLppJG>aV7{_jha!@N>8*!|LeueM?NalP<=3KajEPVrVs;MQW*1{JfCz^^jl>lFW9AzpV-{Zk#e!<inQ!C)hk!PD)2DS`b=2@n~P5s!^8u)5RW)&WeJj2vXQ`6x;LSALcVk#EC6#0301biv-TzH(R6u1S7LtPwdWKK4fWNHz7A+q#&$kHQ`rO!uBhOdNVj)Bid4mLH#R0t$<C?s<jB=d9dU}P6l@_*s3@Nvk}Cn38cd&4Iqdm~STWDbC2eio8B2$ETWWDbN+LJmasgO5WVhxz%zeUW`}9)9p(WIyCUcnER`)@69C&=K<q9WhUtr$RDMgNGr9VZ3RO%s+%=_J{i-`(obykj&#Dncd(n$R2_}4v_pf!bc-JB0IsyAdf*0C%6l;3$CRTB(pOlvnSje*%R3ZJ`q`Z0J8KSAWMG+*$3GRl6eB$1K9)THUW}(EF|+NQ<ek=N1svu=}$}l{#a>|M*gAc$s_GwZzGR9Z}xipva=*OIrCyW(t|ur&R+Zr+ZS_R'

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
