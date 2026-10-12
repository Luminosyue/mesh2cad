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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cffd007512a74a47b48390e1777c2afa/part_001.stl', 'relative_path': 'cffd007512a74a47b48390e1777c2afa/part_001.stl', 'source_sha256': '620c422c72bf396a8d51cea2d1a0f4046a8bb0bde0dab1b64f6cdaaff9c49507', 'input_faces': 212, 'input_vertices': 154, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.38660216331481934, -0.4615018963813782, 0.4082709550857544], [-0.3060290813446045, 0.1339041292667389, 0.42042967677116394]]}
GEOMETRY_BASE85 = 'c$}q~3rv((8ixN7fr_XoxTtmOpw$sY6p@P5c19FXM`0Aa&;m+jSd?pl#S5r|H;SlLQK@N@(l)kr&Dza&vu#{2V061Ry;-fb3s}-<dP{mqYO86}?m7SW&KbYsze&@MdGkKJ`R4rJ`OZJXjCkBZeWMI|#28248L;7-frcR!ZbTV%-s;-btGqSw6;<nPMueHmhu>Q>mn`(;+Kf7*-cjVOSyk;wu{&lKCp+Toj^fJd+UmlJ6_wRRUYVyCmeqJgUQ<$7<rP1VPe_^;XHSfcvv0Kj#z&a!A^P;yGr~IJzwdAg_m!3Z*J+Wj40@X7uJdC$t?K=`s!#ko<v&g0>ub5HPd!HYgj;6bem>nYH(ox=b6oeXdgQ9U;91(&=Sh5hEm!rM_L;fQ{pD%azm}{1_chaXV}7FbgD3Lb-={x6;-htJ{m-y|v|RObGoSKV&!1xbXu0YKc}HX)I<Jv2ELZ2~&!e+wol6%_v3|5%^|LII)(H#Y`|{`de#<6MzNVbdr#+I^AK7z;&u1{z+rs$y`g8r<U+YKt{Ca-AH*S7t&S73S&%gb~%zaTo{JQa1D9>5S&n53H<(+d+v-(|srTp?Mr&)dXPRhehoMQDq*HixWG+tl2fbyOKUcYG$<wtJtb8-B5#mvV!d41e%%5Qb@`r|bpn0dZ~*ZcFa$9aAC3Nv@zdb8V{UrD89-fMe?@@oZVzVh{)o-^itdRX2*VuG2waz16bee=)VR`tDab(^{UT!v-d;lB@i^Qj+aa}VoN%T=Gq+t<|fu=TZEtsm~To`aUF^&{q4_pjw@{h=Awa~PgxJvV!*^_<7LtoNnm>bef6_1v^v?dw=DtrK>Z&q2#o{XcB9ua7VDIcT}+=Z)K!&7WIuYWKs}X6{R{^ErHXgYt{>_#A$?PI*ftzt2Oi(fV6U`Fylo^@H4(cZk0(hJ0k^?T>8abJKD)htcoT`iXzzbJKEFKmAQJ?+x$dbJKFwXYL6zH~#%GpWBWXslF_P&uz~OX6{<IpZBBXs-L56wEoiPct2XM`gygL_7ypap9^wdYx_xdF7I!ryfK>3`SLdE|1CE^FD+Ns?P{d{hn?he__V>y?eCWH{c5?|@8|WDznI6*SIbp>zY5y#tLylDkhddOecoG4`GuZtb}n%%sQ+Xq?^Dawbu+SY-|pu7U7ShhGA@H(ci95!|CRoHedGpmwLWrR@)!SN=auWG`8WK+ue*8<^|RoOF1EgwtM!rlwz|4#oeIlb)tAkt{6gqI<<IK#kCv;?KU-!{pGOAqIW$eD`uU4aviq$iiRR-R!S6RMSL+-|z&iiwV)a^nS3UN1S3Po7-!_HLCH-Z7pCI?|SM{&u>T}xR$#lO3E#>F+QY_79WGuhWwOq~ronf?2YcyZylR;FUcA?8E51g--`}-`pM)~!DwBL|(eEplDbpKy1;d2=M-6gZ`%2ocl({eS>DPNg+M?(x>C*!)Ax1YGqUl&>)c->KMIN$EFT1VZti$3G|r66;^c7N{arTi}qe7^_Int88xBG218&D`}w3*XnV*V%Pdy+6lw)tryNMtRD+yuSB2+HZCuU;l?TzK%b?eTZFG)&F>q`cJwT$UW@aa?N`iHdcx6pi=$Bx8>r(JH9Gcg;AN`t-mU-p7yK0Do;(A`g^}Bmx&%85&APE`BC^h@T1@bkmQN*3E+v~SonBwEZ6}b2bO+6*a0339}ON09s{?7$ADuX$)n)+f=7YxgO3199|pb;JW}Y7@Zs=b;Njq*@F?(5@F4g=@F4I#@DOl6p&+49L;e?vVGIxo7U~Zl3?Bd<4335*M?#W^z{9~qz<+=wN8sABhd#KzbORm&mX6!ed`RvKj{rwt&A#wpa9^<Pj{Vr+q2N$l+XgqlyM&sB8X?JRg^Gk$3N42uFBM7_nk_UPlAH?nfK$O)kO$9Q4qpuSfER<);IqML;1qZ=I0ZZvk~|5L90#8cjsqt^l4rnE!85>f;91}~;6*~q;7j0H;4JKC34A43`U>z8@G|%+aGlT-LOys4xCLh;d6tk%C=<RAoC$sml3a-A6k_c<a2|XiI1fA@?gGyTKP;34PlUU`iQsAQS>OlYPWUXa6YPd(g5BVJ_+#LF@LEW6BfJpo-)AFy7r04ir_dJoZtxcHR-tY1J@DP&J>XVI@<I4c@ImlCNb+8I6L>Fp2fP8i16&UGg3H0V@EmY1crH8xJQw^BBzdOLgYa~C1~?s@4bK5*gA3qZZ~?dk-T*EEZ-zI4n=s$akmOqUR&XtN{T*kp9+F%yv<bc)z74z`{3Lu2_(|{qcq{k-xDAs06#O9gDez(VKJa1iAxQFm_+IdSa5H=dxEZ__UTy^LVafUMTqAIwOLoKO8iCh^WGDO~Bk($s`~W059zGKs51woU?up5e<S7QdXG%|jKWGHrS0$&x(~ZFUu;j(?Y$Nc#EqOV-zzF=lkX!^W0T+Q+!#9Ja*Mh5rDuf<~Bv%UkNvKq)7?QjOUJ0&5{TfK}I!N*ccold9cq1ga8j@TCe;ix`-ULamhgX8@!Rz6rM&Ld##Xdc5Tc4<)|M#bzz{4khL9;*f=+ERIbMJg+y!a5LKJ<Fr!RF_TKH{Hj_9OX;%J?7On&>+'

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
