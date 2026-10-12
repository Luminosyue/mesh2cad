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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f1150d2342a8470e912942c49e978f28/part_007.stl', 'relative_path': 'f1150d2342a8470e912942c49e978f28/part_007.stl', 'source_sha256': 'f13ec8b3ac518a28db2d05873a6692bb292dee97ea246ea720cc9b86bbbb157c', 'input_faces': 106, 'input_vertices': 95, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4850732982158661, -0.4862179756164551, -0.46204355359077454], [0.40281397104263306, 0.49963441491127014, 0.34958744049072266]]}
GEOMETRY_BASE85 = 'c$}q|Z%`Fg7{(Xw1q3w^Nd*M9NI*da6qPH&RS8i*E^<-He@g<QmKvx-I*m8SX_7Qc`=CuT-UK7fDNV`$!%|F&6m>-@N6}kjHl^c-v=7#o&Uw$Xx83d5G_^C&ywCZabKX7s?zxA>QDm`3N#c4!>RG(6x-L|bxCTj4(#D$l^(&XxG>lub?!^Epf;hjlxMyxfiK8+=+9+*KuC8fVUY~4}lXGgPB&W&AwQK9w*H^7swzj^yhVz1|=Nf7lZ>XzUSHs#V*;#4wgwbj8OY(oc!q^hL>jvIxXHi~O(woQE)O^F!uH$ZS`@7pH`gq`Pw|HAF{$>Y{%9hPHIalA=)<x~O4V1^s<?z<8dD|6JMqEjsahdKrJJF-(UT|ehFGY>ZSMJ~BZTG{hoiuN1p~&Ox6yvrIr95VCzp$R}tG@YDKdpazig>QIn+#lT5?oarG*A8Y4smbO26|psskpDZ`G<b}`qj5CQXVsRS>uVzt+)I2b(ZgL_4wo3cz5nu;;Op)5<TaHHjh8<dQ>aMJ3bNj%_^k&Nae@p=lS8v?UMbp-e->qKBG(2rzfBCo4M4OFY5D3tKqq{_oZ?3`_j01UuoRDuYBW8@7Fhe<^ig|{ZaT9e_Z{}y3fE(`%`Umiu_Z%X?=2YCq0++U?y?<B3n1{y@SO%ua({q{YO8ic?rAw_1yI^qK*0wt`_h2)Yenfu3UPUekYxweR+DGs2ri^y1VbHfgfA(Aw5^*7$e_h`H1S)vdoajwSV$aYP(KfG4KcZA5)%l>BjN4CgReF2t$6?nZo1ZeW}Eygi1H9dqg+=Zd_+8uea;C3U1G6xoqI8PIlA#H;s3JyS4EH7r&q9r=A)&*Hg_oBF3BQ>Eot)`nai{K5nX~#?AHgaZ^2g+*D5=H`UX7c;R^(H`)0C{ca*N#kp$YvbCC?S9$(cJMqkTI$!OnsUAJ|W(e*bxkT*Sj!c!tzn0ia?UZ_tKkmMtD8|nj)j`~{vxV|*?-snGj=1?8)42DpQ=DTh-Cyas_PbW^zwGhHwR6ngwuZR*yw$k*yw$i8RxHl3q%t}O?6Hj<`ueE$)pTEtYxPk=;>7w}R((qA$chtx-wuf1yIg$fs$reGwtqpq=bn-0^w9oQPdvD)uaA9Xkl633(S3TZ94x;i>OHzoUpIH%ri*&+%m3xi#9eQX@6*@Eo6y`v&vj_qH5&iz`5W}yi^O?u=3boVO2Zz(?+mB9*?$-3<X`yr;+$0OoFT5f-qlZWiz?3B>*t7T=ecz9m&<yto!ipJH+uD4&fY+I?1vk781k%eiSzuB#yhV0eeWkOi1kdIF7}(!Y2^1rJ(X8~^ys;~ytwzDxa(#^Z=S>OmG;@*rqhi<>@OQrDEmsQt<rs>amX(%`u{{*Iq_e8qGhB{`k&uuVM%NaiA)m_GvG%vjbWM$aX$qy1%3+rB*Y~6B;=Tcd^~R^Q!-N)(<sCV@T1_LLd=BE#9Z#vm{OU>GL1ufER|c5o@5%2m<~UX>1m07CW}}AKL|by;y$0rfmnf90AGOl6%hB&FpXpy$`pqf1z*lohW;}2aqncBhyHo!E61ED^hcr3i8*n)F;4i!OiP#+Aufe~j46U?Fk(3TT&5DHQp6&7zISt(W+N8D+nBPMauBD&Ps5y9h_m4%(U#$J(Y7*Kkk5i#HjLxBhQQ~coxn5<Y#4HBJ{0X7tkZ^=3vYwBB1XbTVy+c&0Q>-~N%N1RJqyn}4KW*j8vGDM3%mt$hae`vCt&T|FJ!7@Dn^_GKc8s<`WK*&`{7K{OtDNcOe2`$5o6(FF@}47@uMV=DF87T;ywg12tFG3kPvYU(cEC%GZ^=a0gpir2{9T9#2NxICLTFskv9lF1UW;HHw2t}z9;RH*q1!cfam*mI{K%huLS+vha(P#FG61_#QjXfaCjag;2lK)fl-#f``7x<%f$;|_($73(|FwLXTHapzQf;96cj897%08KVkKXV^apNYX#f'

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
