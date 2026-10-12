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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/77d56cc994f94d8280c38009688e7413/part_002.stl', 'relative_path': '77d56cc994f94d8280c38009688e7413/part_002.stl', 'source_sha256': 'f7615af9cbd7feddb089550e1cc34e29e17a17f9065dc21604d67723c112fc97', 'input_faces': 144, 'input_vertices': 126, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4996337294578552, -0.32605189085006714, -0.1931827962398529], [0.4999999701976776, 0.3959769606590271, -0.14392432570457458]]}
GEOMETRY_BASE85 = 'c$}q}Yitx%7>1`%Y*7%D1w?L(qAOafExY9=?Qktn(3P8V5n5p@Xl+Z2Ttt&0k@`oBiINyZLX2P{5loCGY77%dX-O~`tk{BR6Y-CU{1S*Dt#i(KzTwOQiP23?-e=x^`^~w`eCKS_6+Lrfj`@so-1?ffbRWl2t&bCPHe?#suU(aCEUc~Hoa6M@zWRv1{rIAJ=_NVN24_oRb*6DuLt<h)@mTfvL_s`JUDvR_p{jOeUBl{(@@H1nG-d+7aZOcyCb)i}sJNscK6Xq&{MGn>{M;IJ!SDX-mqSXMj~!L&#OEJ5Wcih`mJ?;_8sF>wRr{UIEjr#$dabr!8Ee+@Uds4x_fL`h?(ltwZ9g76qT`(r#`n9vH1TIDjz{`~@9g;Sq}?C4YZvil$0PYef3oqD&$imWvtzf;<D_ol)1P?PcKUxv_uor>)oS~l1HRGycT4cE&NAaVGsN6CwL9Yb@4R91ml%J~mGeLAyqC6pXOB1Zcjx{P8Sj-g?YoyYeP_nCqSf}};>$cp{O(I_X1vk(&}Y2P<tFX#xtKQnN$qO2egFLvI^M^3FTQnF|Gm5Rq`odX&~hVR#ufVe&Y!Z!)p_BSvu2%_n)u}M)*JaUF7cgx9VSm!y!hd`E|i))SBIHAshzF1@9cfg#FrS~JO9xct-0TRZ^rd$%Z+@0B=3dz`zzWb>vevo_MP0%zBl7y{<D2qFMM}@QF~;)vVF$2=Z^-Hr)S3WCu!Ct^gsUfM|-{Ezm<3BxC4Va?0!1GP0_x0;Bq8?=Q%g(^S<mkSEzmWlfCWs^Bh0jbV~aNCv-&KBYgkhQ<3||PjAz{chJ?o)Q!%LttQWb-`nl?%Q?N(tW#c1o6eVt`V#LG-`Vk+@#&8z&qHuueVu=}%{=E`Ys9BNPKo$U<~hr6*YU2*8@`+Wwf4Q?lD~<5W=uba)kJ)m2X~ar!|UY#+2k)i*&_3-^W2g!`Kc%3%lvy%PtHAJ=C{}Vk^8E3)bV*+Odjf?TK9-A{l}Me_fpaL&<~%J8Rouu@0$A-ebHk4@`x|<7WzDgG7svxEwi3yH+AiKwtX2_=<}SrCA-4+Mf<#8p7q{EeCxf_-{<}EQqlO(XT0it*Vj@9tomU4GTzXqKFE0eKTFT*d7v)&)TM0S8E(cazSJv^dZp@~j;Bs~Rz0+R->RQF4|UQ_MdQVn@y3I?t$pgbPo2;9J$bM3-F<(UJjGe@)PI==wZEuq*>^l^-_hTf{fK!GU-lze_js_c>1*~upLG{s_D7kAFrIx-*8MtP);-vl^|kER#jJalFY^%kvX5uS<I6mB{$2iy?&q1I$L;ZoFXsne<{>y&n0RyE@Tm{tOT5$vr>jZ(Ui0TiBlC$Lp7%n3yUD}($B{aWFXtbrx9S|Fea>UPb?(w};#=o5{XFb=-}EyTjhFM7XPpmC9&<kQtn;C{?`$(~#iss<@9g-%%-eOoIZw*`t8=LtZ}ZVeKk;RL!sj74_v-s{9(GgL&ci0&oQGu}QRixt-<*d%>%6VkF?Q@k<ay}sCco*A$G#wb7(X`f(~(~zi%JUyx_PR!J5KN5*GP4h^;1Nd>LYsNpCW6M|L&(qGWmahiYy8GusUdqXo@S*^>8IzkG=}m!<%V}H=(b<N*m!#a4q^QTnn#2pMqDw3($G+0(f@N%Ft=(Ja`&B9eo_04!bnPbI_;ZIq*Vs6}%8$i8jD1;X3qXxDMVxQ@jz~0xNw9-UzQlGw?dN3SA0U!Hdx+;KlG<bOt;Zo{CO{r@~3}5jY7Kq7TA_@I&am@I!C{y&F!zBhWkG5%54X4;~2LhUUPx!M$jTb5RFYpIhKuI3Mi~=feZgA@BfrSkUf6??H#a_rRmjyWmmqXmlt%8h(JLcqDo!JQ5y+_J#++x6>5&L3_Y`;J#>2xG&rfy%km(gZsgQ(c$o5IF8;A$Kf$(0XznN7=09e7%oCf;39Y|It3mJPev=?$?z<65j+c?k5<C-;b+i#_!)RDP4SE9X81+82HgbLz-!Q2Sm_FQ4ZI9p055~n=xjI*&vdTUvY9l+j|Ht5O`&CQ3Z8^cgD1h`(CP3vcs%OD<KYQ3#ii&RxD+l&7sBQ6ljutLNq9M02QP=KX^NjmH^9%sFQ6OY7vSg6b#S^Or$?;k&Hfd5?c?bpVgF+=`<u~i+y3U8L85RIPgnF(wIq1idgxB{)*1c*Xmbex'

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
