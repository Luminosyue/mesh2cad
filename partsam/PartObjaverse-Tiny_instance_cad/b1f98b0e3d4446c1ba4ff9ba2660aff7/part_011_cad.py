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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1f98b0e3d4446c1ba4ff9ba2660aff7/part_011.stl', 'relative_path': 'b1f98b0e3d4446c1ba4ff9ba2660aff7/part_011.stl', 'source_sha256': '455bc6e84436afcd5cff97647adcf89a1420e76237ed17f9b670932a4a9d8f5e', 'input_faces': 138, 'input_vertices': 105, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10418985784053802, 0.3296484351158142, 0.24062040448188782], [-0.048403188586235046, 0.3592959940433502, 0.2548805773258209]]}
GEOMETRY_BASE85 = 'c$}q}du$X%9LJ|Gq_sTcQCb1nLgCtSr7eA3U)Kc-EwqKB(iSR6YkNmAKx>PQ2qv5ONQ`JgNYn_D`-3RZf<>TG6T*p_h~Z(3cZo5=5lB!7CcZT$=+5kSwlmW;F}h^({qV`&-0W|Dx4WsYE-ro=v5s_-kbc@&mqZ91$z&So_xJAD(&6u0w7q9%44KS4J$UY0)zsiyA4B@dE?1|&ucOyhrnxEt9+z8l1-g58^tNx`)ZN?Zr+#_+);_=K`?}hD{O12N^Ye<_T0xdudsh382VF%dckqLAX6hG4B2{K;xiO#9G`@U>d879j^U<CR=G*-F%!g9;GavfU%RJe4XN38JtIP+>6Rh*&MwkzFUtnIpk;A<H+wn8hYyLkizkfXQ(HU=?5$6eADzyB8>i3<zaW=>Dzodr6dAL{SH%`nOX4iXXWmsGf_v$*e<{wY9^LG@7#p~jJ%=NAwu+HDRGc4A}h_*9td>aUh_2gbJIm|psULl{a)StYN$9!;aYgpVb?nAS0S?m0DwdD26oQR`W_C0v#hf{2x4X;b};a<PDTdvR72bqs1ye!uTK6vw5Slln}+xiP5PM$QqB-JxGJ=<E(wXdZ8<zC-aChc$V=G~Lb=YC^-?{|l;h(7dLWkmF3&Q9jrnqIZ)d1OHHTHy`rx}L9>eDsr&h?6%C?TLu<1Sc-A)-(8~weRa&B_C=qBBIxyy7eCW-s>B!emH+p^7^*hmM=(=d}vQz#L=gojfnGv(uSEQo+qs9@@|uS=*0o6&f_yAul03DoIE){6cOi%9^Goq6Wwjq^Cyqw^}xZ1=(R)ht@A%BmFmyEUH{>`mql;aU-9~L*X8=x{(OSXU$#oFKRn-;&^z(+`PdiLYv(RX`xU%8bV95ruaE6fAG>Z9w};sGE}JFwr|r?V`r8*Ti=Owb>Vv25$^D%5#gJG}yFcN1pYytL&-+&Oyq<iXQ1$5{sXx(g+}r)e`|y?0cb(4XUOnIV_^;zm>*rowKlkeTxmVY(zjfufQ~hnP)Sr8`{@jnLf9uj?PW@ner60)mX9u17lY6y4?emrX<X-Jh<MO&er{5R%>hFtt_4mcS`uj4nE)6*SuE~v(0kIDJ{=mI@pW$A;&)D-Q_Zh<-J}UJU?r+?y_et*6`=sra`=s$l%TclZc0J+M`!-o}>WJ8%_HzV&%yR^O%yR@@eU2CnpB@(bllL3<(sRuxy_H^h`at0KafHy3Xug#O+J#qAD(S(~`IU4_;lFz&E%5x`SJD!54W;JDLFR&U!1K*97wJakf^+d1HwNWm<ip@%u#Q{?*1@&N)!<riBXS*>=A+<7a5HifxEb7pd<@(KUW04}(_95!1FlB;z}4X8=2(ebi}Zolf;S@9gExXZknP|O@MdHucr&;Q=?8a#1IWk00dN~~1Go*`f_wzr0&YOA05^aukxRgp-~wa`xB#4m%mHVC=OO2V=Yi*t(SDkPLHQwbXvlQrTyQ!#6X^!iECy$S7bA7>VsHhr7F+?YM>c|KHiPTIb;u@g9k>R$228UWTmxQ;Tn=6e_L9+l@*>N?UT`5Y4_pY&MlJwngENpCSVQeHFetl_ncz&+$b~^UA6Ws;2bUx3!S$#`IR@n_WDU3m*Ib1`*@N_gy|^|H2IWP_Z15uRLSzOw1M6Oh%m*(77a_~R<yc1%(gXJ3J1EDRBi<Y_#5!okA>+Yu-~{A2Z~{0Hc^^0tJOOz>cmjAj@&WL4@J!?k@J#S*<b&YZ;91Bt@GNjDG6kFpo`ReNo&rub$9QBCauPTRJQ0KPWMm3>GI%O74LlW0AC<nknAmA?|MaJv(ZgUHA^u@U{iOW36+ii!IhXzL_0=V?M{cb7?@2Q+(8`j(0oV}n00'

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
