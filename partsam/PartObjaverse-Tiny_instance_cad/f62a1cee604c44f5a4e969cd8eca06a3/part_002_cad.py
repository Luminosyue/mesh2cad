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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f62a1cee604c44f5a4e969cd8eca06a3/part_002.stl', 'relative_path': 'f62a1cee604c44f5a4e969cd8eca06a3/part_002.stl', 'source_sha256': '667e6adab6d811265dd86460de2d3a43c485a318ddfbd0caf67d71b14890187c', 'input_faces': 128, 'input_vertices': 121, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.006972006522119045, -0.00979735516011715, -0.43704789876937866], [-0.001958227250725031, 0.021065253764390945, -0.3008401393890381]]}
GEOMETRY_BASE85 = 'c$}q}3s6*57{?EYqJTUMu@n`MhX~?=n1mLWhh~zBqM|ACTwoDcSQgMwyP&3qVk(qFrD&E;Gc-dvY14ysd`z0wFwy{`4dEk)Mn}yVWtymS&-vf&o^@-Qy3RNM-~I2m-}&x2XYcirl03x8oAAS*xOR}fE>}X7a3kKNQg1RFa`fd9C8g^fh$r)vL)Co?mn}$H=|Cz;bx5whJjWCg>lZRRFD4}1FC@=sGMlnWGK{8Nz2eW!Dk|4gzq}x;R8P+*M@B`4`%MoG_uJ_A9}gGWf~BQ?Lz|+9J+~-I9!ZxKmCXU`|H+rGmDVtQ=V}N0{7}m}rWZeYm1)7`POUHL^7q9l`rS_ETfU9q`MZAO<D5?v{SX%e)61z>m}U=FF}>l%^5sx-r`DI-?{H0N6@1cmzLM3w|Erkq(_6v%nl!6R$d6yk{gc}TU+&Z~pUmtO^PRplv;2d>-GYDCjrrt=QS`5sn^?UA9}B)**IdfZC*BtG4+Ryo&-*5b^N_cN%_n(bJG(CF@oDbIB{V3$ymXu3%j=HW^~uKj%qKNlnJ?GxV7{g45U(G#PxOBdYh>$qrk2m=q($7XiDf=<mU;cpz4^F>mw26uHwE8vYy%rts@pC2<a(c7-&+6VF5b_gD{Nim#d*9RuQ%-b=u`F#tF*hH;oI(KYyS6N^L;zCQK%yy>}S4ZT!ZLio^5^dG-<S(e<F?dId3oD{~z9C`%Hd)vv9pn_*gGXemwVQ++@Ey$tgha$*L|r^D}Ds{uvxrp<NftU4C7vFU1bn_0@f4>sznaHvbd%M(w;=^RX`KJXpu|-`l8NcUxcGx1=qN{jMzc8fuxgY!-a^mLv1!>NA2bjjCtsOL`MTAM0-Mb?(yoq~k}K>7Hc4mkyp{zQv<S@MXgho_{>H+n#U9>KF1Ye;9cF&aFZ|NjkTQjpNoP))~Kv-KV9{2Vy?%pVHi*D?<MM8vZ%%pYkt#<@VNH^=;Q(^+|V1gFWAN-L3gp_b2jg*4;X;&AQwA>bf^446yqqsSe%E{E<_8w7%_islL?V++fdF??2Xk+vLIPv^=U~esOw_;M@LQ;M>+$ecSqS#1CcK{>e`ftiE(VsLWn{)qkSCZ!3RJnCrH)IyZLqXnnPRc}k|>Tj%Y<H0I0mW|!LC54Y-#+B#$~i{<x@8f(;!E1CB&KQr!w66VjExRup8e}dO9(3NP%m5%FpojdJC!aN*^<b94wXTIz<r<UdK?iPG&{lu@teDo=`=kR{s9V`_3{~}lLZO4_*?kLpOm-{We{sZqqZ9nqWUctA{|J}Fvb<Gbm2z8F07JTcv9MSVS=FbYWb>vg~MIU`ywngzio8t?#{aA`_^7<Dq=4;25a?kPW9Z1X9*0(e?3BGloSLO5i0oU_{`k}W4-#Y&@zu|SN2lPVzt$yCm(Jgu*|KSDESNmD~p6ILlq-;8$hjtIK{`+@$KfgES3hSP1;J>5gtvNz|<~_l;_S1Ta*LiJrj?j;LGrz8`CE3EdJ3r+8L>RJ!d0x@Z>woH!DUAE}<DRw@;jQ5C)n(V^VKjxt2>Mo#m!)|nP)y}e)&47iA^Kmw62$!9SAtQrhi7OwAr$t327rCQ{?IV6KX?j_IH&{-154m|XgD|?oB*8)P5>uDBfyE^B%=J+ijWC3#?TlI9S@xVRx|`W9vlpf1P6n4(79km=YVzKY0xBa68f2jP&g1e39RT?a3FXb^eM2S-r#XyU+8G?Xk3FYG#Km)4ua~yI`k9-4Fm^b422zN_|cdMcEmXWE8Y+q(KII02&M4?jbR9dy`ay7y}+K(*<eqw2Xq$L1MCis1-pYsLSw)q!EVs!z;0ky=uEIH*aiA5*abWSIs-fcJRCY5JRIx{jRHG^heD&l(U?1hQ)n!p@iKU^=KLiZ^S}#mz6?3)_ZHHa4{ss7r8H7$ETZuuG#Q!-P6jWbQAEQ)qlAVTYJ?iVMsOiQ;anPPpn9kQY(QN-Lg4}$YoW!^B5*Od3|ay%1D9+1D@Q0?Nn;(f3Tg&dfh(X!a0S=|Ed-mur3i)dpt;~YaE9jkGY|^DLSrQ~9l8db4$g+^!FtR^HbUVX&3xrR^T9dbOlTH36TBL_3asb~@M>@xbO~6|RB#%2IgONL2S@KAfA=S?zYbZsAqaoqvi+v`*wcQ~hZeFv1XGfSvPYjI{iiH`yYd7ge*#g_a(('

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
