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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cbafed33e2f7412c97ba3941c399b2df/part_005.stl', 'relative_path': 'cbafed33e2f7412c97ba3941c399b2df/part_005.stl', 'source_sha256': 'e673450cb493ac66eb3b1a646d2f75a1fa2fdf93a804243c60b7437581a4d76b', 'input_faces': 128, 'input_vertices': 93, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.08445453643798828, 0.23315122723579407, 0.0006479918956756592], [0.10166025161743164, 0.25540891289711, 0.02671853080391884]]}
GEOMETRY_BASE85 = 'c$}q}3s6*59L6uOg1{;W2qGejykE*o0$BwGd5WwGhDr)41ZIHXkVfTVDK;Ywg{dh+q~vI%W1$9S(+>G464{(eN=<9P6x1wj#?-O)p6^4sP0ciQnKR#Szxm(q{Lk5Y@7_U|ZlQ9LaCl1N=hmsBttCkwYRO5eEGS=9ytJTVVoBK=Gs#}~@-e9Ov$HdF3(TZSsmgCzLB-N?zbP6&ZDF)uu*R>jw0u>0e#w&3@?{0GpOn9%qQK-=6y=u{m_GZ*L<DOh0)jO!X#VSABllozJQQb=_?9)@vP#({TjPfM(VK;Dcy%}Yye9a^_X|JX<`jJWF5w$4FG2l<N${I?!*}h3KXU-St_A*@6yfWA2DS*lY(MgM_o5%w1JqwT0{`A0$eE$qCVWE&az0Oh|6K~|SDZxs#T@iGq80w8PT^ll7-3Z8@99F$tTN=pxg%eF7JhpT`uXiS_-*Il?~FnJj@4U-`gy)%jf(Y-=|lbDCe#O>LQd8I{B7y**V(||_6zzP?uVR|GsyA3h5BnDSXX8f{DZf#-hnps|D*kznD+td=PyS8zt$taci3U!JA0tsSdW}lR>F_J@+I=!Qjz1WK0I{2($pyAEOS8p`IX9fkGa9`>xaLk1b)0fa%#Qduk}KXF#!J6B=`fzm43hm^fS5&Il&Ra&#N`V{?ymN&r8I-aXYY|ojvdy(%|38Le8R0_(wB@f5~>F$ccB@3_m3k^=|~BpO98w4^N_>tOM8wDR8^co?`UV;i}9jdKx*WmttP^3HZIw!fyyipNpg5x2;8f@p1U8i;(a13i@2_qg-!q9dcGw@VX5}y}k)K$>%U{`F8mBJK=}NBHwNwaxU#f|6hdSzQ`%!ejY}?%}dC?Rg0YS9mvVOiGA4L4*$JQ<Q$1bpAA~%<aQ(H^+eQLj6!|U1>}_0Bfq}~{%4nkuW2{Oey%tLzu^Y<;nGau>%AY~duhIpoVMA@eN$O}D9&$e#y)tB+JWm(E&Rdfz{7keC-}QE;Xl*P>(CcD+Jord5IYn590b2~A?BU54>_Ts@J}6r|GgIT>LP^SwA=;zbNv(4*TukZ%)$QO$;Z683x%H-;tBu#Ce&YBBz%KUA=Xvgr|{!DPGa73*_hY63iV!iK1gYImt+5{k$*D~>uoDRPIC?Ff9^s4*j(gfZ9;x?xpF^M?+RZt5MfkYhk32Yaqn05Gw5rtqaX86E3vOf;rFk__3(oi>Ko4Bd#To9A5#1He7lH#((j?ZF$(o<H{gfWqEAgA{I6`<M2^<dsOUe-Mfiq<kI;|xu@|v#9>O1do*3SCM}1wC@S95U+>lz%V7>P<P#<kPEk19*yK<;+$k>bgcU0^%4>>!Xk#n$y&y(ldhJIfU?~9GqiazyE<-RQZ11<1>KcT$e8@k~?QGj_*RISJNeinZB*T~nVqTZ0$F3wknA^-fh8-;Jb0KQd^SeJfW*9PJ5sfPbrGS=JBx(?U*Tf#SV-tH2gfBI%E?ynEvUtNcsI`10cAH9N{%V)cAztrl{r{xjhXLuq%ZT|W=o#L%)<j1=<=`BsCn1;3Kt*bD9$Sap@%EzGo{VP{-<iC353JZ_^pYL2Yxuza+Ok)v;%nLYVo=sgymi2M6tn<mTW|3u`OO`dAEbC0NtZ`&nA0sEodutjQ95Sa-wd6E%3UvxOg`7y8Oim<Er-qTIlc!Nb$kWI%)Bth}Ig;v2jwFXtCy+zQ!PN2OV6s1T9NC}jO&vq_CVNnw$R1=j({Q2MQ=Q26WNQwYZK-3(wq!MR99d1aqmC!rksYZM$c|)ZsxR4@>`DzFyOQ0hA!K*5h8jlJkiDpr$zEhX>J+jcIf$wy2azXI<H-}r;nW0jI62BRVyVg01adN2N6jGX$k`k+&!eW1=aJ`7Q^<43nbbsbCV3WhI(Zg3l{$@_N=~B2kdw$WsFCCu<f+t9@>Fs(HJBVtj-dLJBgm7e-sDN-K&l5hknBTsBm0m&rAODgCx^^qO=C3Gf$BnbAdjHhlShz;Q?1Fv$-_8gwxHUQEyxm8Ej>D9Hlx~+&B*3dN3uCtMRg{t$d*)BvL)Gy>Q1&I+fX%R8}dl17kMOklxgVF&CH!F{^?%^j}E=O2*p1T{(7eJXK(14m8Opme*|^u!^BUYx#@4ENyFsbm;MBeQViY'

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
