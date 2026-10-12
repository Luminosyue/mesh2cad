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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7fce3003d95479a9226f7cb639df893/part_007.stl', 'relative_path': 'b7fce3003d95479a9226f7cb639df893/part_007.stl', 'source_sha256': 'a2295b01d53582897b484f184f33b884b0fa218c0c6890746e2c28028b37b16a', 'input_faces': 130, 'input_vertices': 82, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.338782399892807, -0.3895587921142578, -0.3349038362503052], [0.17160801589488983, 0.017488598823547363, -0.18173085153102875]]}
GEOMETRY_BASE85 = 'c$}q|eN0tl9LEnYB5xwfi@YcvLAanm2r6I{M^sd<;LWtcoL(lFI8(eJzA*AwTbVT+V>UHcsFiQotZbNTdBfyQK(2Db)Yefqb2+U)bf($Md7j_*;B%O5t<Lt__jA7Id4A{jyj>19tCx4EMAsPUt$9bbruj+|i$Ez<sxEU>l`k!;OkGv6!9xn>KD!KUC|XcxEB278r5a0VS>;lPWr}RcS(ar<mMzOxJE|NdtCp;Gl$J3+zhq@)neJCEFR3Wg?-R4qljV%0WVu%Uub01Gf_?WV?vuKzhrU10RN8&DhpBcvpZwU(+}Czjonz{}bcf$JepSn#Ybmi^yxsi++*j7Vf#>zTOzkheNq+e;7w;cB|15vcPaC<f{`xt+=Y!=ukJGV|`_A_DyuC81kov_GkU#cIuJYwf-rhd^7OzV_b%CCr-A?uRwo$!R$0>j53w&Ja`L*0vZmK-5_U;mD|J-6z9@!Dj+beY`+}AGkQN6*dDc=p5`%;#|+ev2*aCN4~a9_Q;j^~#e{3%~+1iiPVoZ4j{<@2D;^C!RfYZ_<$U0#p2<|4nBM>kQOy8@`5%cuCgeg96%6Is;F@9P}gZ+zHC<FvGr-(aCS{><XOeBc4SXKM^s^+Yq(aV&wx@oJb$oHyr3J82%T-KFRCE#L9H<3c(`U-`I*wE7pGPpxa}5%-mSYd+<%?l<LeHmvC2buZl9BaT;j&rRcet(x*I*+%0ywV(Fs7ggMEyq0%?x367%M)aNWR=4PDe=O(`$E&=OO7lDGS*rW`$v*zRxV!BpKd##?`i&2>$&aj{_pF&o>%C(Potup|uJ+Op%HN#I-{(B&qJAFdXx?*zXr8Vn@cPxmeQlyISzdCBzS8y=Ur#CaGw#d3-KYJy=mGh+YuwbYrkD1`&*aB#r}@5|M*D2om2T5M_bes-;Sl%L#$$AjiZ9Z+-M5eO4E=`YzpsYQ!>6_6d($~mGk>S^5Vn!~&Jc}{t8wVzcG0&79qAQ)xoKUOIR9G4iB^-3`8Ry!N>``2f3!P!+}DOI>ZE<rM*FIR&S7I+V5hiGv_1D)Mc>#bhObVa&-aV-L?LhQ{IJ<&@^4Oai@uiTf97%Z*r(NYi1lcDlIZv4eHS0MBDeDK%F(x6qA$PR;TC<V-~wNNY0GV1kMa9#_)6y9UeR~vrICLwjm|~$LYK+!wYx=Mxn9>I)?+Vk>k)mU9>dqvg)QRzs2jY@KIX^p)ygZUP3zMBHl2^Ac_v>vSVZTttN7boc7L>d7tgzQYPZSH-@B97HDQm-<X3Fk#`A3YvD4&B%6g`1s@v@6MAdWu<#FcxTW)aQ?s$iOf0TQtA6HMmKcJp|e?UF`{(yS={Q>p#`(iyd)7QrHQu&G<K9a=3PygCjRw8_AFq2(|KK@gqeB!_Q)R>Tw_CLQh{4@0$p41})nhnkXPliqbPX^~ep9bfE^Pmbi4?F`p9Xta(4LTLf^eHf_Cl~L}22Vlc;yq7;6+|xb<suj31U)9`@dSeLBxpK#5;zN*2F?OcgvNs>f>WU~I2Ak!8U-E&9swN#9s!PlCV&%AtKmn%i$dN6XgoL`^(8>l!RZ($V^2K>OOGzb-cWyVqQpLtC271KDbSJ7K=2?ve38!+JQx}b9t`$JFdhyK0W*yN4+n=q<G^9y(Fn##(6L~q$>1b#3L+V`GaUyW4^D(yz=>cs&S*V`=@E%w9DuR=VXS`ed=UW{UjW(%BZgtDA>asTG&lkrhls|Q#)6Zfk>F&oQ9ILcXe2lib%aCx!0cx#NRJ_U42AkYgTOvu4+LW`L=fgD5IhnZ3T7G$9tk$qB34+VSgdC(`WWjQiZu^KO<_W<#(rRI>>0+!9%Jkc^#OZ>C8!736FLYXVU8rU@k4lE-YigK?BSS?aI|4;(_^+CbM+_yGjEO_MSA2zXMyM9-Ugi`v@ZlReMZP#fc~?<`3S}{p;qu5JS&9G6!KY-(~3Se)HB<t$?D-5>h(|mLO;4xKB3}2)B}5({~U@vSLwO>|2W#LgM4UVJf$_dPGzeo{S9FKXMg'

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
