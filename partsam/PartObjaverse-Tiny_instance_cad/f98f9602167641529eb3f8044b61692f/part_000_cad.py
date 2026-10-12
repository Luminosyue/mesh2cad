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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f98f9602167641529eb3f8044b61692f/part_000.stl', 'relative_path': 'f98f9602167641529eb3f8044b61692f/part_000.stl', 'source_sha256': 'bb58669981d19b952d4f5df78b73139cc50cc3909e04f40eede7dbf658c95c2a', 'input_faces': 84, 'input_vertices': 82, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.09663727879524231, -0.3816683888435364, -0.09890446811914444], [0.22725580632686615, -0.10441673547029495, 0.193477600812912]]}
GEOMETRY_BASE85 = 'c$}q|eN0t#7{`B?d+~(~fe6CaL#P)B4Uw0dX<Seg<n5A~qs?(|3P>-!U9=LU^GB(xa6?%cTXCl$%QRs#K*(_tDtT>Yu5<*qu{Hl_*`zfJY@O#h54ZE&+1Bc8pZz}PyNBQTopXNA-NBY=GzAOo2p0+M-LJ>a69QNug2n#A%Bqsxh0Zml<*yh-0OoMaj>mI$WZUu$V!x<1?<sWdt~9Tg%o~a<<`~IbR90D4=_oBItK3rv`4-0u&O$YJ?sb$Gs^^iGxEN_&RE%^``mcwdx&+yBsWVv}ttl^l*8^(`JpM_tKL05PbIEdt<?f7(>yTR;YEQBHRY$KuZV#;JWA!`puR^Yj_g>NG%HfU?tnZp^>e0`WSdY2b)pJ^(yOWM!uH1b77^_bY)#~d~&awImUo8)>+o#XPSoSckKh4#~^6l}M%SEpqVC#RbWeBgk_snIMZ`+8uYb^N!TTk^8%<Vs~sMpuaL4OWn-N<2H-*9^XpY!j<?QH$o{g~Tl2Hs`Q?R-T)<nBR3r@me>ZN*&txY(tyx2JvmCDvQ-vU=;<X3Uj^At%{7H-&$J_cfe%k*(*DALj1fQU1OLCqKvQ*7UM@T;G@VVO{7nyRO`ys^!lvV)f$v;mf$5n7bY9y%e0nT)Z5??`t$!%ZJ`{vicpFpW!@H4)#2i11m9iH;=RDDd+yugZp8hg}oPLS1ac3##Html_up9zOUGK*#1!*M=_W4jn!<QIF@~i`ByP)e~P;4Zajbc*D98O9EQ1wJHz(B)HWA$*J~+k|4aVeU0Obb@5S8_GJLPT_T*lDJ)3*?wWr>zuRZl%eLb5i0e#qa(xIb#Jw5MXZtZ>Rv_5w$4O-qZ=a@dXUyZ=rb;tjlJ{Qx0T3_c)Iayx(4EC>m>QI|Lmqx8xUnd6Fu=RWOwP&7^49w*c^98nkQxxXz@Hgu9_1=B$sb4yS{cAm&)6UlU?RBlMV`CfHdMvfrze??`4)%QNwrhPY=eXE)N5-`Not)@o*X?S<T>dcqB&#1<js2_0mWymX%^{fEZy(_A>nVY`2>Ff8<0`7b{&fxfz^*GlnXC2nOctvb=9^kyk591sl5U;HTn>7g-IsS?d*&J2srBzi>Fjwb#yHIFH#W29skE9DeEyNk*?SR<SFo>LWgoEjsI=X{{<TgVWcx>PwrG8AKEd~oGfC^~gg?%*=hhUAx#%n4>sR8if2}88V*6k2m9&1hjn=d0BYlH?E#(zA_1M_g#<i^G)^d{&z<l*<qsXEA)PN9<+40_=8YS`n?o%WFe}8Hi)iuPZETwUa&ZFoYMvKk`ox`zE=SDg=(j4FkDvt>G?9xUba=3ki%4!;;$xSpapfN$`(R3b7bIrPe&J8sGtefcEM00=#sD!En5#YfDcnAR=Mu0CSz?Tu=5&`}&0ltC&UqygN65wV6d?f)ML4@LV(g0shfG;7y7ZKnO5#SFJ;13Ysfdsfe0e&9=KA!-eOMv?l;ByG@c?7s00e(M?0py7)R+V)G_*w$|Q38Ao0Uk?$#}VN11b7kwzMcTzK!86%fTs}Pn+WhU0z91n-$sCE5#TulxQzhMBfxVB@N5D+lK{^kz_$|Mn+fn#0z8=j-$;NzPJll~V<NdN)8G?q{HK47{yt=AAoh=v_h0g#IsIRjs&jdM^lX{Fut(J9^AQ#57zVpQ`~?jw8nF'

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
