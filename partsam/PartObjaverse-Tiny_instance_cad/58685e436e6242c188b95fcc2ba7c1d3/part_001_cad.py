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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/58685e436e6242c188b95fcc2ba7c1d3/part_001.stl', 'relative_path': '58685e436e6242c188b95fcc2ba7c1d3/part_001.stl', 'source_sha256': 'aaf69b9bb9a0fffbf90739a007542daf2a91d8e72de6aea9f210be50e2d6f8ea', 'input_faces': 248, 'input_vertices': 180, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.03558870777487755, -0.2066982388496399, -0.04004346579313278], [0.484433650970459, 0.27856773138046265, 0.14443150162696838]]}
GEOMETRY_BASE85 = 'c$}q~dvH|M9mj7Hc^V*KK)?VOs)k1p<YkCJRs<9x5DOwNVR<A1@<<avzz|j_?*NfU0_4Gl5*`tgB2MXmkS(PTrP`rWTmAsLMLO~a)Q+^BQLOZyb3f<i+>>;s)9%b~z8}8)_IJ*``#qb@CNm@Mp+w7lbhmEK9zHbK*0My!TZz`ntlZ@b=Vj$RwKQjSjFljL@ld*F!Yku5r^Q$+t+$frXXVYyO-{3uhh?WGr`XBa%W{|J&RIHpS?>HS;g6ZKI4{fb^A^m>$#VYP^Xb(7DfYl#DfU|Xe|)rbwh*mJJzOXDayRoAQro9jrE7llj_U`qe{xRugWr99N%n93wo>;4_`#E}p7;4Pdb$0{Rbkz?@k3jiT+sc<sK6ER?{E))zct$RgPZ;RR`GG^TkA_JeCy(e=b!e^Z}ofW+v&X`jroCd`4{E$D$iER>$!4J-iPp>rd7HhQ2v8IoYVc#r2f*kcO+N(=HQ2>Tsp7&(RWha`?mV43f+(3+wYcN@XbGwD)$-5G5YbX6aN0l8#~<otGCN^-&*YYp_^UmeDl9N+30-;6xFzXc2$Y5A3w4pRo+i~*0!)*ck)^Hde_}KqWfXxU;pzt-M8C}k$z<KZ^F87;YUCD^1RP~G~LZl!h>?%k9KhV=+vtheEnYymivr0^Y;hvBU6n2xb?1oKdsEyk8f|vsMGyW-*Vr5^X|i^6|P^npu{)-x2_+)HC*1e;E)e08q1sV&Ach!%$qmI$eZ%byeZ$zn>XLco7ZpT&GU`CDc{VScU|Poz8$~Px2};xuiwa_*Kg!7e7D~<xn74AAItl;By-CM%?~!8DgD6jVnTI|_>tJykUqz{k>K_(3hvVTqu22d26yTG;qfIO$$d4uT&(wpl;7=gv2XtUd%u=*&O9j7`y=1De(2K&Wxn}urnvpr5-NTB$G2`LRO<cFmg9aUuj}=DhxPt2elYLeVZA@teey5m{256{^nM#ZoSk$;?+^TKvU`5_gna!LzI7<%>$h%Aa&u_Rk9_X>A!B~{o7a9W^SQvk{~*3)>^~4*b5Zsg_s3HH7ykPbX!*g<<bHnYzyFr<KQZqAnFQ%aoBLm1<=b8TuWul^BqHZ5@#jbRc8Nbf(Qh-{{?GjRRDSqDj4z*oYXjXm1+6!VoQDdQHJX3roB20=m4D@%`B%P~f90F`_x5At-<xmbU-@SKz4=D|z5N^c_x5Sz-<xCP-<xCPU-@SKm2c+XyDlUDo^RyeyIv#z-ad`|d;2u<@9oFPzqhWDf3M%jzt?Z%-`kIof74g__vRb<H+_|V@AWeBZ~7|#-W)UkZE73OKYoM!8@`u+{08~QZ;*fd2KiU}G4rqHoB79YkbgDb%)i>dnSZrUGyiIinSV9M%s+mE{HyD_`nmf#EqHm2-rwL{sOvS)h1yTbB{%<PFR$_4AM?DZ`(vILHOD+J>blJHqV{Q?7qzZ=UR1w%UR1w%Uetcf^J4hkc~SGt^J4hkc~P&gd0q_PJ1=UEabBW#3a(54uSss6|5z>OD?ie^(9P|+UB$W|9QiLdpAU~K_w`?_cCYvEW6SF_KiXltTsKr*?OxZ%6K*uNuJX-wm2a-=^&9Id-&{8kJtlptNvvEqwC~W)bj=SZ<;it}HL=CIZ%@1Fp1bcpEYtnag-deX&=((;>GN&ts9ZO);LuL_|DWA<_gQpS&X3Hj-kz@c;p2T=zwMU2x^MmEpj_AfM_Q?`e?Yv<XXHj&sXjkEGhgl}aDVe&-486k>*l0i^>%p<{%QS5&hI|WUAJH1=5)=sGd^;!_x`Hgx*wUFCjIc4v;(?tz7KeFIPc-o+D#)g-#qW$eu|dL>k3w;9q{e*><xKckz1>F>we_QMCn^`g`4X#ec#UH#K*6)<DD%y)xt`&vgc@D%?MLGls5j=%)&wc)mJkE2BrSLU(MLg9v*S3E7}(B3MZj$;3T*++6wLrcS7UgPVi$+bwOLB@o+3^q1+nz5FCTHf@9z~v<(~wH$mINP2gteBXBdgg;O1zdf2IsXiK;w+#YQKx8S+$Q5zQhPcW|o{5_|hMhBu#zyslal;9p{N4O)id!RPl5ABQEa9_9&+7<2t_d=84UT`wn8BT_uL_5Jx!adQ);GS@AtN!)wO$kmxyTK{&Q<UKDP9>u4&~9)$I05Yf3vCUnJSCtH!3l6Xw5c|;DQgOC4hwx07Wz1x2zO`CLI<Fa!$SMR2c3GysY8_DBb4B3O7LlP6MP!}F(vptO7JmC@L@C`7P=ok43|4~z^MwScA!6kg&v26o`Qwez&qd#=)17cDp+V3-T<#cOW{>;u~R>EYO_;sqg&y(;dSVCcpbbJ-2tzK-=YMsrUbu930{G2fLFlFDZwkL4eWOxugxBGANO16URdaESZEO}bSJzC&PNO3e7FGJ1{c5~bPF7U*HeNwI#uh``&NBs1dAM1qbJb!;S=z2O7JPP7Cr^npeNxPSiSy2kD@2xqp-@V;P=p4xR$*NUgOksr=~i!%c&(!E#p3md!L8?0M3IaQG#Dam%%T?6VWB`M0h;<20R|lKo`Op@L2S9cr5$^ngzcAk4ERgqv7Y#Iq>uFbLedNIXE4C4NixLqch;)@U!SN_*r-;`YJpWeg=I7eg+<lPKF1=gU~7PAb1Em6&?boqSN72I1QZ%r@_O}S@1A;1R8`#zyWkF9Dqln^Wl;3C^Q=$1&=`&z+>PS(M9l!@HliaJPv*dT?)ShPe60v32-Kw3unULx7=(C%|mmo`uq#tM+x4G=D>U5-RM$yH(Z1+hKt~x=puM0T!=1!3*l{OHoOhqg3gDxz#GxI@J4t&8no))-vo!ySyugfpx^>@rd9u*DL5aU4hvla3oWtg-+Kk`N6X;-a5-8Dm&4-c>M`^vT4~k4?+LD=1c%WwI1HDfC2%P$em-Vq#Kb1X{ii?u);~hxL$U7<!R9mlzn19FtZ-&|zocYlG!dVJoDWa2@=f$>@#)I?Hyf)8aR'

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
