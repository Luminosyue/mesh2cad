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

PART_NAME = 'part_021'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_021.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_021.stl', 'source_sha256': '0cd029555872787bad35b7d88f29f0368a488de145915035fbd943c08b78e2a7', 'input_faces': 78, 'input_vertices': 100, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.25653764605522156, -0.2682928740978241, 0.21959568560123444], [0.40895962715148926, -0.09848952293395996, 0.2705244719982147]]}
GEOMETRY_BASE85 = 'c$}q|4NO*57{?Ftp%{t*83yR}i;qNJ6i^gDt||C|;H!y-_;FwHRhdo{nD#OBmb$5%wU+4S%w3yqvF2*I(0Ea<AW8Tlm?c_PZ-!=SxiwQOhn@4B=g>LtYHM}3XaDE^&U2pgKlk4Ea&hJc21OBm3??yMT|fIm31JaNqR2*fSw%^)yF6vx`j-MoKj7>T`c{5Hp0hB3Y$UHFtZ<hXmnDqX5+<z7Oi0!eR+g4kl)2U|D=k~$W<1BWw%kp5`D)jCH$6`rm71EYr6nb6mD+zidNV7rYuYC>FNdz$^;ERxD{yXJJpyX$>8BYtJI=wm-dM-S_g{m0JAcLnc5c0XhmTKBfqGxI6Sz_N2)GuNSg-WYcEGrq`k-F!?;AcFxORS3z1-h^Si$SJ^|9stdgBqUmG|r9{(4m#pSSV)Nx45M{e}DLDmf|lC%KWI!Ms5kr{w<DJr{6eRi;Pj-~JkKGiP$0+}}J>&FfEec;x=Zt_IE<YwG0w+M}r#!RNj(kKD)bZ07vtdmd%Kn`=0aYi(!TIy}M)eKs@zw_I-k*J@%oFT4!g=k0$1`Wy>sh4b7_ULVuO>#K$Uw-bXthwE`*%*XP6?bvYO_Ts`?*{5|o3%K@XQmwpS{rVK()~;y9zqx-qaGl&#{2TjraGqVQ_%}*E1n&E2gyLUYeT@4F{$BBKK92YT)@_M~dVTQHHmIwc!}+YkN`F#Q0NfXHP4Q!G-3pvUT~hiB?u+Ey#_M3exEr|M6sKP2h+DvoTYt36ezacqc>fbgicjrE#3j)3E$Vf+I25=!%A@)`oDW>jc~|x6$AwRGcQJ7Lx1ZW&pMqP+4ZQD0N-gh`a!T=U$F=|`T|cV(Y7g(=_qj;%<Ija3{ip-DG4E}~kKj6T;m5bI5;&<cly$91dwBiooeI~(8hCwNXPfNDp9??aMkn_fIuqUl_8wj@xQ<*r|Jv7gI{5Evq~hP73;$$~<1+La>upnfmgjMPFI2sri<bk}^smk<*AqEGZi)BjqGH~svYEffG~UO^GJ%`($MN?k?#rKdzki1A<?DK<waNPuoFLc5zJBoXK3fi*SNu2K25#?rr&aNf+(It=TlQUEpY^TMha7*%*S&rad=lio>YyvI?)^=t<$VdRBNzL!x5aaw@u*eam*5(5u`hdplk?wav?|a4tRmpP=xJW?Bi^6LZRBEKc6urIx%Qg|*{476{yXca;Oj04Y>@X$k~i`C#+Ma8R^S1?FYiuR*B1M_dzAaEJ=>!AL~bMRettTS^F9Y#&cXe{{-)0ZoSZSv$o>WQHF7Tcn9Ub>pAU96D*lgu$M>}<?Niy0-~_qoW4wQp?>G2Clk(j9aZyhW{mR#!RCQMA@5e>Gw)Zh#ciHF`dB4`S@GoIsH<FrU|Hhhl;CkAQX1SiYlYwh}FMra_oyyl?b$m$w#2`Xggwn6Wl`iSikU@3`{rgYDlJtM|X*f3Xe|{Niy@yc`1DPMx!I&q}7(!zh>Ojn&rqPea0MsWje-`H@pvGg~ALm4)4#1qPGnB?4R1Ndd?9r!@j+%mb1`P*}J8+EUVKn;C=!+VTc@p{^fjS)X(bz8yH4}3-Hx%bHeFF2TG{)1IhB^WBY#I}Bd?Job#ksw3KGWWqr=aIl)R9u|z;mXfFke7pHjVkHd6*Z_$j9+~9AkMfjQ|=wQ3ElbfZnE{W?{~12-dNq2j<IZ7&MlmF2Z~njUpT`!ZDTy;o2dnJu#1^5l7=0)ELY&@E(jqO~ahkJcV^kBQbZ;D5kLxbus2I&{%@wOK{AEbE9xR(+JGx(kP@c19cAOGif+++=*jz@mfv9>&5gr%=7S?KaV;O^GP(O(-?y~8S}A(eFO7x9miPCo)z{S<)F^OJR8SyQFAbN<_7eL3jC*kLH{~TxUup-r2aG2*ONSRAbnW7UslfCV0ItrgVBR*p!zENRgpgdJz%H4'

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
