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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/78a7c30405f64b0f8137c3922c1464a0/part_003.stl', 'relative_path': '78a7c30405f64b0f8137c3922c1464a0/part_003.stl', 'source_sha256': '91d28e617eb2e74bd289d163f828390c4fbfb2160a728f1939cd7bd529114eab', 'input_faces': 160, 'input_vertices': 116, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.10240208357572556, -0.042870908975601196, -0.13796046376228333], [0.19592511653900146, 0.008884251117706299, 0.019342752173542976]]}
GEOMETRY_BASE85 = 'c$}q}du$X{6o+qL&=#qSZ7C?lskCgX1zSKsD0T|+?85~tqP(WUwt$qj+gcw494jbNRG<k#5@3K<L5%?tO@zvB3n~Vq_=n;vW{o052oc|jk~rs_-{N#wjnPSN&Ue4Ld*;l&cczp2O5@_wlpI;=wakR`Mjxf9U8B-evp>+ZY_Y#__{#c6Vw8tH9g)~pQCaT0H%2w9Ro*53#>D~eIL%vBJ=UAAd8_LJO@XSFi|PVP{N$%pt!VVyzHw<)z2ENV78Z`q*GA^$Ypb>YcqH2;gcHUbE~Z+v)r}O*@BT;$Qa5g+c+dWN_DL_TiRQ!U!`D!>+7F38knlK<zxFccF**~Eu(xs^qZmRSx3?mBzJE--kzB?3>&9;kM)7*{<yJoLyC~i_=wbH1Nd4Axzl*O=eMlnmxV(lunwH<mzF<%@=UG?W9E{?Pvj-pK>$Xf5f2xr0*YMzeXFVbQ`&^Sf^0>W@JjRJb;?EVf@Vuo<p70xAi1!rpJcmB7TN}-5ee>3GOg%5&oW%8nlV>&sqj+n@F<xh5*ah+Gw=y30aP5|0G~aK=7S4ZR<ePH8O^<SZ)MLC?Bi{Pb&-WF{<MIl5jKQtqH|4D6yocIbf>C_vn*}@{;pJb8*Do#L-%sq=5RBqO(`q(wz8&L^$~+%zaE{kHSHWlVysH-~*GKc(>6G>SyQiNQzv<fs8mC{r)E125%~siOZm(^9zm4<drUzyIyJtA_xP4^2v1Oom_3ae$%J_`;t=n6h+cxrg9<PUA!t<bEyj8kYyzyiW=l!{CLo^@$7|)B#Tfe99e42qFA@*8^$@O4;-CoD~hQ9EMHy>Ee_l5a)do^9wOEu3HuhcZogYj-3#`>DIbK%!a<m+|FI=a1qb<{to5^o)BaPIS~e5C&Fm&I@T?LnS*>~ps_@!Xl6r*Pe4bGXifvY*{voss>l=ARZHT35s4kl*bM<X4+N6<?6|B-f4iq1%V?9@AUmy5zn-TE*kn%KOLdjdSw;(Txo8+VRy~5AwUc70KVNiPvMQ`MOE+o^gAtR^Bse`Ay>M&vG7BEBnp7;a2g!XL<e&)amv*>NL+5i4PxM#(taRQE?UGJys*H<5TeKXQTe{^86>t-yOHtGvx1%*=vpX+>TbRBVY39_iPrgev<bT^0>W1p3p}}#3wG~bv0*7p3qC3Z?QkyX7Tt9Eg{Yme^UIyGdsA>)7ygVdz}|wv~p*U@h)#}&p*oN4`;m1K5x!$uG5p*#eQ&!_z~T^ocYc4DdM|-*ySAW_SQ4Mc5?ltbH(rPXUTo}Leae5XEWDhuG=pD(oVVG_ky8lUh9A8O+KG&iGTKyJ-n|bt>t<`{`bWnAGG_Qyz=I8oqE?F;$N(n@ny+f(Y%$GDc3D1d58V$AME9E2lmPM);jSQ1AG3-hswi8*pF-w|4j{hH6gnznl}fY<2ua~Ux^RrbU5!zA8<x|)}p;V>Ua4o^=ErdurE8g*O})kKNR!x)l~7H6tp|n<tmSLF`s!_ymqwRx$bVSVck{JHu0-2wD;JDE^lIA=|?Q_2QJEWBm2|yllY^rb~yLH+Z&PnpPKeA`(ZzJT*>3>@pb;;E2s9UL>ujvWPhDkS2;e-`GiteV)Re*WuyMxr}^lD|NCi9W!qJ$Yte}NBBp}-f>RK$2d98D5N`xi9PHpc^aq1;5l4V27C3k;`UT)|h!er%z?1D(Xt(ip8;M4IJK_}Z?chm>)4-F!QxPYFCnG=cK-!{q%b_K=+ii9mf|vu&!5HEJc1u^Z@Z#wAy%Ceay}_}F3E)_;LX1;?9mFw+@!%M6FT^Bp5^5kGWw(60Wy4W@S%}%-Y>dgmebIfEAWi_6fXfkQfXl%Zh^62Pa2eusa2Z&~HL1QLL>;VSOcC<jVYfTMW#|{<+IJ#WfXATLV#IRrt+=-_h$Y}0ob!TjLq8L1=0(f_UxzizL>vfCz`1L{$>_(yC4v*skB936jzd2Qt{*ra{Xtl>euzonY@8bk9)SLE%;`|XZ18Bz?{LIX;4+-M1FWMz9qV@!;tVjw31EuDz!ZmoDfS0b><y+E3#O>Rbi{xu_5xE(2UE-fQ_KfbECLsyZen_lZ&vawPX$Mwed5UbfjIIGA-)BTSVJSe0gX5fjo5=moQg(#JsR<iXvBGF#3Rs%$0AMy2kh2pw_3z{a09pzyaIjVmFQDk?%<{9Q>+G8ftP|8qfa~^eToYmT!}u#dmTIzeTw&hec+kkyV0Ko_JQZ3KL<Pud>{G?z;nQh(7zwN0K5eKW#Ie4HRu!9p-=Gv2M5p(V2+9Xb~7+POTkr$^T6{kFA<)N{(NvH;$7fMFwaS8Ol(@*-~DUvufwDVqQ^h_+`sJk+2Q=<PCM6?j}TvJ0zFUmgBQ!2<x|?J>Q5<$)`I'

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
