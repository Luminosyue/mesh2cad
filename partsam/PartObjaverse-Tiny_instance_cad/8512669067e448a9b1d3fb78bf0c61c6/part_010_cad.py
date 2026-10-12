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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8512669067e448a9b1d3fb78bf0c61c6/part_010.stl', 'relative_path': '8512669067e448a9b1d3fb78bf0c61c6/part_010.stl', 'source_sha256': '6b16d25f12a3cc3338e8a40492cf4df7b6cdb199483a941451d14be2fcaebb6f', 'input_faces': 192, 'input_vertices': 111, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07243925333023071, 0.0876394510269165, 0.0035385042428970337], [0.0900089293718338, 0.18981829285621643, 0.07428179681301117]]}
GEOMETRY_BASE85 = 'c$}qJ2~bt%8NG;zASxiJ;F9OUqPT$|i=fX1L=brjh)RMF^`S(o5nSp5UW@w@1%qo9L@{x<VoZ&;d2x$N##rN0ld41~Mok<$NnPUF`=9R+NT;3Yw2%4boOizE-@gCdJ6IAO>w0POX`_WDxqIGq)ih;pnwK`+mOC|Pj4iLrq<3aIXztL}ry5rePD`?kaL}e}vjfK3^2X!_M41Ajvm*jJnF6vW=T6Pdnlx&1?pT}B<FY2^*$h2zeAYWQ<9lFmaBwG6_YR#*`KJHzgIQ!PJMf7@@3@n_6<%Ig0<_E*ediMB`pJXPO<&|dw>AhAJ?r3Vh1Rnpq1(guNu9p#?<uqg^?`0)n<VjRZpDa?h!nk3k?65e(Cq=g+Yf#ERMC57tOI^G6}tAitJHUmgKmu;1HCGDgXr!RYZO);iHBY`-$Uvgo+tW`;i5mCEqagZn5XqZ2k6#$;i4})2VJ*J-h=trk9~^z86|5Knqymv?)lmdeZ@4<eg3{1^D$qS_>T8Q?|T5ceOAFS)ZJ#m{Ixy)(6z}|P)8s16!CiG)Loco;%^bJ+3K$cZalja`c|{(OOAYi`g(=vG3#U>F75w4_Vf61=+>Ajp6|EN_23DjKT4H4Kg4}dTQ^nS7rkG?`>4NT9Q3MJGo()P)eVR*9Vqel=3~8j{^A{opBM^Vf8~4%@n84fi1~PXK-cW0Qs?s!tjk>Tcn9|9lkY?yHUYZscN@Cy+3-)$tNUU7G>LCIOvatnTE?9*4!Sn;n(Xu4McbioxwjqhxBUMs^FFi_=RT#i=)3NmKz%pcCdAKlhF*5_Idr`^uN3hKQ!20zS&q^tOCQO)%qh_I6x$zBC%?JuPwQCdWoJ4g-oDVe41Jj6E%84;LA<^t1Mzm(OWUxYK7q$kXXjTs@Zf&v_OC)^+<HZFzDL$WFKd(_`ts7vh!4qvUbW9%>b%Nd0E|k2u7@m^^Yty9iuI;MiT-?@=ub0eVxDa$Z-ss;<RjE?^#t>@dW?sz9ZE%g{fIZlwN_?qm3_V-{ePnSB<N8cp_@XiGM^Js*av;i-^vlcXtTt--NAhHlFy;*1<@E+TR05+ToqRg-Fz`y#@(EaeXw3Fka&kFhoL{ZhVwNK8w*_<_yoGy&jP(_T~p}Rv-wgdy-3cbqF{@hOQFp3WE1p*)wQ?i(^ej@-4D9$n=;g2I{6UdZzW+qrX8oD>$^JRe9do9#JFX921vY9kevICS37F!WwXCTee?I(($9YVMPH&xe-4==>oP@`O8w8!&)Vr16H(7OYcuxwr$tg{#TUB-pKZc=o5{L#-`w56ouSb6X9KX$=Isd>SBuZth;bdRqaVz7=IntU`g8;KKYJ5&dzaf%CwI+StSe~o$B4_!D?r}mHqiAeE~1xLps(!lbJsvW;41gaDSs987b8kA?!y>a@2&C`z*Vc>L;W*H<$ifM&6D%*3|;rA6g_ltA@mcrV)Xyb38-U_=vxjwqh7J}^D*fw|I3TvPk3E~b^Ux!&fVeSQefK4RTy{sS<#PqEy23JJ|}wMPMQCXrKqp{v}_sbT>Vz=(d7k**KYcX{+#!En{5&D9^YSr{@>G2=9yk^D{$m4==#}(M-g|;YcKSIy^G}jwh=w^JaqlIRrKcZ{2l8db+pj=nCI;x?7#WQ0-U4W_K!m7(<<d$UbICWE$q@f)H#`p`(l4M3+Jm<e5NCQu1)6u?t-my56b4E-!ATjZqKL?ebs|p)Nws8&&MCW$9lDhcH!{vZYICya|gW(w9HDuJs6XL-vRUU!fn#m?X8ISJB;;edE1r)@5YRVUi3ij``+`#wRP>G&k^WvUPfPO(?iGO`~E)AwYa~o1YUSH9q8Lso(mBlVO)Ji`fOmGQ`jH7+cN0pu5tN@AMS$r*cTjyZeRI6`d$C<q^#@GV~PK<RF`@&GXDp6L~m3_?q$nlJRj|C>Q*YOx?$Rf`10BETyvX??`88Vf!b;x==T0^NS&ZF`xRQRl;GUWh4&8tLq-ceNj!}@o;Psr=If3ar|jb~@;l(1j5t%_8qqtJ%5(GOQT*O&!66??e`m>a+-W-c#H@dc-#hEjd(!{$Z;Ae;EAEy3FAGK2UzYc_{OT?F4?m^%&|M6dVJ^m7a&}g&S7arsPc{DgSLB?~|LzqzGUWe#MV@HPA;+-sL>qawVdD&Y+pymdClSYyE1W>?V3;GfK%o=4!n))N>u5C}#hr;R<j&+xh|S0yIYxbAJ@WeGK145aC+4^k>yx{Zw;=kE*WvtJhz-bH$eR&;$=h&V&1fcSfvo98YfmkJ<M`03H52oFX>DuOQrMN)ncRVUSC8mSUXR?1*re7Rns6RXShqb*@i1an@<95+iDBdc^z|Tylh@^5Hz2x_Hz4;Vwy3qn7F=fw)@@5uJcQVT+(chzVhDK{=iHj6xCgN_xd(X%VhDK$@>pUI@>ueL#BlO~<UNUD<Y64UCr$CDG{qYeJ;)oA`x85m`;*5JW69&llZXS!lgOiqJ;{4=>}ZbFh~E`@ldG|U=ntZ=F~>@zKaoCvj%A_WLSG!m=tX}o`jR+?H~rr9DV}B6Xv2mPQ_0^lER+6B`V>zvES~;&`V@~aESUaa`V==C7Day)eGwcZmHt%v6z^_WsA27he&h`eb2qFxu@!kc#`GulBky8ZH|BL?PDA=s%$vlK<jIB&X5L`tbfHhhj3HXdhZ~m8ymaOy)2CvF5{HoYF|051`Z8xYeM7kJAzZWKX@*5|U!ur^iJi!U$>WIw$m7W~iKECf$ww2%l8+`&C8m+5aqLv?bt|r;71yA+r(x=O+l!{Sg_uHaAx|U@B2Od_B6cJXB5y==BX30RP4p!9<k*V0<6d+pMv^yYTtlLpR?`mym^Xkq)%~Vox)3{RHT^J(d83$9-ES%;nK($R>4&k*8_S&Pep4~Si78r5Kcq1)jXBl*mcl(x;r{mF+9H`3$(*5FZy(0>=9;VTPD`F)EAlrq={tpf#Fpgh9>g%uoxIwoupcpoT-}2a%<D#8?Nd0CID%Z=gAC>kCRaX7qC*`o$N%&%&YF*o2XF0vc>ZhVuV4FWXZjlt!(UzkEs0KecGoffrWp7QD*O}YsOC8'

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
