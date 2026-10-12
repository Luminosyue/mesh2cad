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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_000.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_000.stl', 'source_sha256': 'd979c2d5540feda725acac377b3255d04b1de2a230e7408b7c6327058418ca6f', 'input_faces': 223, 'input_vertices': 159, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.09904488921165466, 0.14901934564113617, -0.09806741774082184], [0.11988582462072372, 0.19745536148548126, 0.0980781689286232]]}
GEOMETRY_BASE85 = 'c$}q~3vg7`9fxlcR33sr0#rb_fRdmw!GI70bypNb)93<%JmrRvkPsjt2>}ukmq)A+0X0a(khng0G>Qh1Sc`3TrfpiBY9BMUGc`<ZAJdt(Fm`NbI_<Qz_uTuP?Y$?bGab7#XMW#)oIU%$=dpK}MDkMxr5WC1iZQ4+)=_$sVTg94k!I8uSJjji6<23%tK6MrjC8$t$ZUCJc|l}Vl2L2ar*AB-E~-k;Gt=jn<fdnu=_M6aHC2V%)>l+*EEaxI;g;%R$5)pYRu((YGw!<ko=kJrj7+n^{F0BMP6^SZHSdR<v`40XSETXz`1gB!-Wuik*y#!GbLq{AtA8jmtn`oJEw%sLMVDRwMfQ7v{`mNXneVydE$q1D_CLDLecy0ObC=FXyPGfgz5T68-*fB#;5TpReE1g`-GOlm%D?YEAKrh~?=5^h=S-j;`}7}s-RHI0t99N~#xc)$ULD7po9E6?>{75!=?%5c;=g%bod<lFd9Z%>@+I9mO0TY?^y)fFudZXFzp{>r{^~mZIP2SPJ)ie^^?dT+g&vJJdp_>+d-Knpk2a*V>wI|n<Q8rJrb#U!oxhUY?)MhnZ2h=P=dIj_E(FHOt@rlN!L1j2G~Ucye$MYLyfNy-S9RX*9NDDvX4y?mA&rm4FTd*dG1<TGv2$8qxb<RSoY6<z{Txf{?C#O{=-9qazmMVV>Gz+~`qx+1>byB^MQupq!`Bv`3hW2zdq3^e`m5jQ4%FZNVXwA+>DBu2M!HhJ?0-tBA8$=n>c^XE{nD%T<JJ1@^L;;X$5-}G!Ylj7e8=-)W&cQTzY*L&(wn8h{Ug1l>>o>x^J#GZNN*_n$NX!Z_xYflU+FF7{91UkF?fEZx0Umo@CSnDH{tt&=Qk$(@!<KD-sJpR%`?4uPQK!vYx|pCf7Qp0#lil|_IT%L#?o^-Z@=!%kMw57VQ>Fm>Fd;a`{A?Q0so`R-u_hk;|KKbV7)Se^++FA>-ntSyT2&cD}9vf4IiBF9oMV(S;Z&rvv_qrRUcQzA8=n*eB!<=y)yr*m-C;fll!$%$9-AxiTgW#!2MnJSJqMWa$OQ$Sx42Y{Re!1P`s(sIpF()^vZrveO#HJ0pB+iZz%Jx?jO|;*gxv`6U8UKpZvVb^|4>A^Va>hDemXV06#D7yx-gS_~C19Iv@Le)-j#87iS#{X}odmYMbAizxKSDns#36KS&AIpY==ETPNRsw@2gSpMCUJpdQ)3V96_5pK3JgeDtUPIuz1)^PiDd0(EBdzAu0Dmd;1N=z2FW&d@IJzCY*e#U721{jC2@zc+``zdZDs&d2YYw_oRDM&ACA#@pjVulc=&H}>_vsq^6xXD<fE=|9t}t6%!KQon_dDfLTlEC|*wy`|JIeO#$OhPU?y>z7`w-;OrA=QOJ9AL)%h1^17+*Yh!D|44791^18i@t*|ukM#CGg8Rq9N0t2}y`}6QbMW6iubkh6SI(~`{gL4Ll|KB3;Q38><@_ebxf(pbF}$Ii--H+EHxl@jK5cXV+`l-#eMKAM{7Nq=^!-E^Qaohpf1;Po{-1uL=j6=#e}AIi=+v;$Y3rP}#A%zHwu~%?A9mVGr#(bI4lkq6W8@b2QKxNSybX-Cgntu#mXf9LQaHl+;{Dc=UxU}eh2$e}AzVa8;0R+DQLCsqpIigy!v&-T7r>8_8{pwi6aTYPOqRhL$W3G!ya_HRx5DM{7IGWB1upfC`vhshPr$3lHSj8UIr%ue99}`Lgjc|;$+hrmcs*GNuZK&>BDe(JOqRl>T+3$WY7}!&25%)t!=vdhc_h!b!JEku@Ce>p@-SaL!>Cu}5O@gJCiw>6_1?gIh`io6Ki4yVA_v2RnQO^Iee*w*^$|H79?n_{9^<rePD>@f0*f3Ar^4dnB#BHR$HHTIO$vD(ob0qgyw4!sV+>;&utC2uymlO~AIED1f8A+Eo%SS6@J_N7-U(NbFTxdYCHX8|3GX7GhIheHryX?Kb57e!6TF)|0q=&llP|&B;VSZZxC*W#55aZtKBqN1t;K2kX@cv?Hn<+HCQriEa1D73u7UTE&%k@&15P{av=^M#L=)UVw!;nZ4zdH@0oRhp;aa$nJOVeuPqDstv7RFDfsewic+qbL`6N68o<i<~r@%Lp74XgQc(M{64^Jg`!BgSe$tZj~oI^eh=fHX7vv3}~fP4{N0N+Qp!mV7pV6hKp8Q#7VIS+mgK7kkg?jZNVcfixg-S9Mc0=XTY08b>V;EC|9WF34foJsD3GvV3fA$T@CpL`yk4?jS@1U~@ZPo98JaP5M{dAZy0&WFga!YyzcUi7<@+z;Og-$vHMx52lN)$lFwB(esc1WzaTz|-L@@&KF#&mo_I=fL-p$KZS6MdV3%5xkIWgWI@v!Qx!cHN0~yG6cT>x8p^>Y_bW?hSSLgI31o$?tmx5CRq!ca0b~3XTUSbr{I}zE_npbg~Q}=I1Dc)JK)9egJe70&b14U<R>MkrTn))YyIaD6*s`ZAGy?52ES_iUwPUYEAhoUl7F4JhdVdEWcQGLB0hbLe*;o`+qw'

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
