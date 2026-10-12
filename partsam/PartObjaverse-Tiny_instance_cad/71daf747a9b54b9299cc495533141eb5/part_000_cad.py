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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/71daf747a9b54b9299cc495533141eb5/part_000.stl', 'relative_path': '71daf747a9b54b9299cc495533141eb5/part_000.stl', 'source_sha256': '4f38b800d62f9ac58ef043ab25717578fc1fbbfdad1ec9fbb136263ef64336d4', 'input_faces': 136, 'input_vertices': 108, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4976252317428589, -0.29313597083091736, -0.033588096499443054], [-0.37235695123672485, -0.27664968371391296, 0.16411015391349792]]}
GEOMETRY_BASE85 = 'c$}q}4NTN!9LFC(5J3bLMUj`kC>$UvZz|&3A*tvIf{6yAfN+E_Qv;=3Yx|ozUkXhLHbw1NWSM5nDdi+Rp;}7`&otjoyk*YK+;Em}&8&N#-}is~|L3)}I`{1R;p4;ae*fR|3~po_JbDB&dJSbiEFXBy<ii+Wy;&fuGFGfvT4JmmwQ}`3Hx?i~e<@j$m7AHJ=f<koo4QhCWl4oDRnko?OVPziy0TRjYbuIY7Otu&HF7__ctxer?kmfSR~zkLM<>Lm#7Rjpanf7Te|+&S<e;lJPuo-PapD3`cGb6OiprbYKPG=CzL9%<XS?w1!;R!W53Uiu%q+az(MaAquUYuR&B7Ob)hfLH$3RiveD65D?{`hY%V$=I`f~C?;Z6Ihsm`ocQJ<~-gz9WdCx5Q#q}cz|MEkcMA@83l-j}74XUEH^{!jbGelx4pJg;mC68*5&UBXL!@Vp1>L_civHmV;fV-6dr&bE#8ytg)x|8>#(qMvuy)BEoDh<r#2&B0Hm{g0QBFCSJe>hE4bbH2Hi`gvAJ^$Uxs&-*KB|Fi9@MV&)gw7+pZ?e8;{=Fl~Re8do%b9t6o_@p%I|DloUd^vlKsQ>$9>L+tD`H}@@wU?eewx~Tj6H9(l9-en5?eFU^ysf!}{GTI)*9Un~{~0sLZ*18j-fzioo#GrP6p-K5i|Uu(6<%IHm;Ag_o5c6O(IGtZGLR3v^0wHw<(TlM2TXW#@Y+^U$L}-YZPwv5pO6ZTmp6A>)Ly<^Pj${sq54O1HJ;UdYf*b<+$6ky`YhZ}oyN0;rz~o(Ke~$c`%a}k?>sys_SYqofAk0KuiDfm_Fo%GecHn49G}0g@zOh2ENah6L&@i)(DT;K(Rexdv_<XZ3Qyt9-%~&A#6XR=g*RK&UeCI2i2CQpQ~m2VXg&t3@aCQ4s7}v)_2U08ofY0@NF%>4b+_<^CxzFePj<blPJDf?=MD87^rPFq7X4>>Q5}iqAg7+xc=_yQi`ttz+{mLJecl$0x8>8hD4x|kvx;+9`gEVB@ix;ji`vU|kF4tY@~3VZuhe(=!4HIIL(zZ6`8Kt8^bfD!bKk0-gM6`t&ar(j?N|J|xCT)-t6q3Xso(gEN$t%_eR#e9ZmZ_Jq`?|5Dfbp$&Z)I(&aw8deQM7dFdukx%}#CoTUYAU-ccW(<?hh*&unA%sJ+s^;^o@ynmMp>2k2hi_OWX2$(}BnKfE$e^A5Lf)ZQ_Fr~Qt5a-xOqPo$6bo|IN;ymBAR)d?E!=;!eBHnn%0?-%zp-qDZKex;um>MQpX{m9{mu4~S#+IRnHm3Kb(7d*~I@s4w8xNCChm2-i2+|RX%4X(W7yp;D<&ey5_3+Jx9uk-zM_D=mf?kDEJVt>9Y=3fwX!IifaO61$}KTvzK;)|O0s(sPH0P_73OfLPCWA$q9n8TBNlS`kNtJ!Z#zin|<-{GC=OVyVwuKIU)r~b|Fb!g_JKYCHy5BJ%cPq#HK_Yc^-?4z=;UiMG7WyPwGwp@y1L%RNGyEOUVeY8y)`+q;$j<xqN!oHHRIL9D|frp95B8~xvBL{-R!Tpgv!906``-2A{dxHmngY0V%G62~d902x4dVoDJc5f{H>Vb3v_W*k$-NBw<FQh-%3)~ku7~B^;1UV8s1Uw3ha~g6AI1T(V7Uy}$N#J?l`N)aj`QTTuIOiiLgY&@!NIkd!ycjtZycoO)`4V^$cp-8+cp*3sIRngd8aNNU0GSS60M5m;=VBhY@XCDBF+ZN8!8}7$vkk$#c?PQHABgke>8Cm`Kb$8|U)A|?_C)%y?)$)5xig%-k$qVA9pfB;?8mzAC+9)PVDKPt1adey0vwBs1IL2LAjg5nfM;WI&P0v}XM(ek6Tn&EIar*tk*VNpa1JsBoCBVV91ETcHXxJ12JkHVnu$zACWCp#fD^$wWH?v{4n_6{hl0b91He3kz+qsCb^lC}kP%=B9F2?x^GpIqgA<S$;0!!l0v6|ZWFj~b&k&ErIT9HPjs!;`!@yzaFA5nAj>h{%A>+Zz>}$Dwm1A)(!{S_u#d!%9=OQf5g;<=6u{f7taW-Oceie)JQsgplB>Lk0WgFbw13mufPe0u+ng3wc{2|EsJGH-7)!*4^ujTk9n{DtEzgpex|6a4_Q~pzc{S6>fFNy'

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
