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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/da0ea36b7904452dbd00952aeb4c453e/part_003.stl', 'relative_path': 'da0ea36b7904452dbd00952aeb4c453e/part_003.stl', 'source_sha256': '6c37356b7c8df213050e2d8408a78610ceacd9852f828756da5c99b86074c4a3', 'input_faces': 72, 'input_vertices': 55, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.12481182813644409, -0.40864500403404236, -0.3862503170967102], [-0.08540265262126923, -0.25810468196868896, -0.2736462950706482]]}
GEOMETRY_BASE85 = 'c$}qH4NTN!82=x~@o@)=dI15R$Cn3)=XnQeW_7C#Twva6ETClqcT9+n^NvA|vLm$*KencB0y@XmC%HMb=`e!(Z%LcQR)P>VQwm4ZT1#2YMQQK*{GO|$)z<1|&wju6_dNgSeV*t4-^;m5w2?*yD_w~+b@sliQxs`&icx9x_*&{}Jbr7Fcbi5@AYHBy9(b&5gR4TLv?}cux5r=Ov#d2+*43`D<eM$E&At|2Rns%gKDS5eMO6)ckI?;Fs=OYt&nYa-H#>6k%`ce$>(a{_j?Dyv0?c(KV-nS`*Nqciy8-<}59!LInWQVXza_nAV-D#7Q!(j*?W3em-fo6&Q|9PqcOCR$FX_&{Pe@nVBT09bKZy7%=aApliTM79QBP!$bZ18%^oo~IkLLvGo7-xUC+REnar7O;Pu;jk@$K2jbElK^z;o{*&x97|mh3~Gqu)`y^NtVkn|4FLT8j9!=Wx!ho#;318;Vz|Bao-FgLL)v*ARF8ZR9a{(eKB(&|CU3*CmaJA0I~kO>WG`UXM9cd{6n+^;gkXxf}K0)FJ*S)T1<1q0Vbo<nK^1pZ!l^4%OXw{=^Xcw@RU}A4I=3MW}NqALlkrBd$@8dhSa_zpe(Hm)JEHuAA3f#2m(Zac*fc`u%a+C5qdAaDw(-anS9@@m}ta!MQJ9A0)kLIqJOoD*8J+NqWy<5cw<4<NT;G(gPoThPc%y=ji4=KOlecVdUGZBF}-PRF87XgL--fkY~$&%=!5`^xN1*`sB<$^m)aLb7rbZ-#pNc_@V^Vzrl+9#SYZrs06-}je5EdBEIYl>WN=Ky7TY^`ufz5__F!|%Kw1nOFGZG65mz3n{?GykG>v%19^@YlJ5L<2z|X}NBz3!e!{5Tqz8T*8KwAT8qx!fLcEt*E%Kde`+&|JZM{HoT`yxkm$s7Lqhyfoe4=jxb@lZT{?h#g=}&q`D1PH!(kI^^CS83fjr72ZM-Z={{+#ewIr=(cfPQ`_>1ui<^h2{}D35~sN4+_Py4<Hpclvjso~bO%^<*z}z6aE2cU-_co<^QTJDyMcndT7iI7wID%)`EN2i2+Gx_p}Qq|MUadDb=(bj`Wt?~Y!cp45tz!eYfOUt1M+#Y<7H5dQrYUsv$2uK3mV|9!>hh#Kw{wnSL2u%*KC*d&*JEAN*xS~=FrnuBpAa|iQPjD^e#80~DU*eCf4_7^a>u`Lsp&uC*`oUr-A77B|Iwm_JcF`l`WxrQ;8xrVvI$p2{xBbduPY5bhTlrS!RCdP%#O<YeZqlta<xz<!R$&(mkm?trppO2m~RKJmZQS1xVuV=r8>y2WQE0X(&=6y74AufFeMjdkl^LyBIJezp#J(ewn{aMV@m}l@li?wV<6LZ;nX4tGUSx;gf^2>cXqmg+!^Tomv8TD+7*_Xh+&>RxkAH}^Vut`2o*dpf9%;)ib5o^he2Ik4k&1?pqLkjmEnp+0@<s2-$ca>-&jM{(t3Hav<(8~<}LHO4v=Uyw}Pfm+me_S%I5*>XD5#n#FKn?wh`yB%8T0Z'

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
