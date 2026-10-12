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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3b204e1c8fa34183821cf925128f545c/part_006.stl', 'relative_path': '3b204e1c8fa34183821cf925128f545c/part_006.stl', 'source_sha256': '793ccf293d68fdb093364fb964b88888f39bee57119bf2dcf435a0ea56441518', 'input_faces': 160, 'input_vertices': 102, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.03408527374267578, 0.09865093231201172, -0.01777985692024231], [0.09718894958496094, 0.20275068283081055, 0.10861730575561523]]}
GEOMETRY_BASE85 = 'c$}q}3s6*59L6sSinzjxn;5<pMHU2Y#WgoXSP&6K*A*leMOlO;99MZ(QZ`{Z4k`u-DitXvCMqggDk>H#6`2*&)27F)_R=Dw)O03iY|r^VLYtatYMKB1e)r?-|K2_4+{+G@#GdXN1+M_bE$QlJwU?rZQYjkc5qm+=l1zKy*yVY}Zi-sw;?>1UbIL4Bs+;nN^0+R`UYJ>+i_q#KvyHkitu8yapr{~Yd3tU^mR;oW8ID4`D=*B+$g{hSgU9K^!?fc=!n99l|Km$uMQ!2s*99+KIuR}S?w%&egk0q31CPt&tgXnkn_k5D*pu>jXgKo5;mD0Yy(W)u4mu{;SyLl(>rx!2{D$!*g~)9KaNZCd`>d}<pYbj7*l~pUoJ}$>=|G=b<;a!fa+$ZRLvC&YO)+a_-f;kZVmpsWI!`<;bAA44dA#A^QOVlZN@QO8CEowD19bW!uU7E6e(XRW<<)3OTPw!>_Aus22~ETGZo=ofRF3{FKdqEBdSRTq8PtBiT2iGtBf09iS1~_}*5LeCS|u01a2TI!!3N~l@&3!FFb}rKa>@2}Z%X>!;OBj~0(ly)Q{Bq*sy0emKE?bPpT~J^Pi>a0-;eP@9B(>NgLU=6=lWX3K0#Y0t@mMmjuqfK^<LY-81y;ri}wX<kaup!=Zd}1i1{i)Zdiuv|M~Vo?876-J?qftox$ics9^`@@$y@e=U2aib^H>!>dYz0i-wJI{Tc_<$>VGNu<liH6*AWjL+<z%<C~^Fi~Svhyw(Hb%iNLYO+p?x2;-YyL2jIe{3CCSzcL@WGZ}eP7|+|WLFU0V$jdgO&%lQ;{`>*tHSrj4cyf)*)gK`5EJmLHDdw&AJLE$g$kkEU_q9JFSHF&R+HnJ{joOL+aX4>II?iiaioEDU^eI_VjCoj&+%^pNd)7_ttBNAzD@VL7IpZ|;kEIg1wHNw-(un@*dgLF4Bd-cTUVRpMLMZY&GuGwi=g2*sxSqC^tFT^QA#eN)<J%4*SNvX<#|@FlXWl@c6|u<cjJUsSeH_>irN}F0VZ5Od^PIOAdGl3#uE(mepWBpOxSr`4A6B&<*FPV5&S~^7sWaiechpNpMqr<-$LHbqYms+4G2YmU`_tNtyv2e3&f?Xwzx7w-IbLtzKIV0_d+(M^JB$8}Co0h|4tZWC`k1yA%08v($TjU4Z)(7EC-_C=&Q-YYZu#T5z8N&xuy1nK;l4{4vqy5pn^>0?J+5ELMQ(bO=MBXEso#dYdJC?9#qBMa_e01XXYl;VK8*YQ{L;NRUn%-1znHOJ8<1Oqun#Bh;`9F*<R%NQ)A}B+v;HLVCJW~IhjUn0<zwX9Q+RHi{RPL)fCj9u4f9|q#`Dgp+lT&Fa6NPT@wqt-dGK|NcfYhvvNRKUV>!mRROLwO_aU!(zYXIT@5g-n4jR{EzwP$IeO;nCfc33JA4_R5?w=_9KJpgwLsPIn%94?vYvX;ia5IU#Y&zz-(1PdWxqRftj%LaIxA1%|tw8R+3w>-y*J54z9>V_NJOr1%AX%G?ymL4Dta4%<=6;C0{s6`|gkqkD`0zQs9piUKW4$aRk?T`&ooyQ2cNO`_+dI+6aS`*}VaM|(j?Zlk|9<3rfZTc+`5MhjxF05?pSqp*uO0Iqmx;V=D$kpX=Uc;Na78Hcg-Q53K6f~%<~%=;jrnR_!@u((7=Ls>j&stmPp=)q_+_Ek=e7&TzhLhF#KCCGUEe0Z`Tfc@#nYv(>f`!0nVoURS4sH`MfsC||5b8{;op6gykGx+ze-LOQzNF8C43r7_ySj@ld0rfdMZ7MoJvokPbYQs>GVifnMi+9M;E+@?oU^<gsWJ>y~#mzZ@MoTM)#%rk<;jY^bnTt6mkJQg>JiJE^I8}i(QpQ&Lh+5^XSQBDm|G#lT4zAld)tHJ&AJ{%Mu<zM$#kblkb?{$t>Y<u1X|lvxLteP4pS`!K6RkpKCCfCA>dNcpp+l??HNyD!K=~H|b69P47$k()-eVNI$v{eIOY^A4ng<5*|aQ&|~OU(nhz^GswmC40@K*z1~?Y;R{{$AZaGk=w^C6IgcJsk0O)lQS=GqOnTS;5I&k5MTXNy(X}k$L1ZjlFoGUL4<#qlL+J)Gj^4G03@qVBS4ESv$VB=qx`mugx6tor2_HkwppT&sB?r?5`_qTg2e5>Dk$vc0d(n#}yqBwbk_y>F>3#`!BR%MDba%2h-JR}9_N9B$`;k8Mesm2vkglQMOAevmOHUwU=n3@sq?JCOo=IlVGwF6Ri*BbcA{WvZ(dQ`L`+E*c_!QDipF*ER#?vR!Cz4V0iF7?Vf!?*h^(^7{xoSK)mK;qVOCLdwqK}{tBenEl^pPy#0b~$8fIgfhJdg~f2hxK{13j2Njx^H8(H~H{?-}8iM7JKAp8xc(sP0#Z*noHaW9qN(y!&g%o$oZedj0t&#FFSC_k9o7Pri$5#Zy)J1D>Q77y'

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
