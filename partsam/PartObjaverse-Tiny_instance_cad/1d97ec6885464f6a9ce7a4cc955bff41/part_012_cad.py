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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1d97ec6885464f6a9ce7a4cc955bff41/part_012.stl', 'relative_path': '1d97ec6885464f6a9ce7a4cc955bff41/part_012.stl', 'source_sha256': '1ec6e1aebdee2a6973f401ab7746de6912084951e4de46fee734e37274774799', 'input_faces': 58, 'input_vertices': 66, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.5821442604064941, 3.184648275375366, -0.5849499702453613], [1.2766921520233154, 4.2420454025268555, 0.45865482091903687]]}
GEOMETRY_BASE85 = 'c$}q{3s4nh6vsb6<1NU;7mAx)yO4kaJ_tlMa=;=PESo^b*c)C7Mno^Z9dx5m#=<OSR2ssogf)(%SQ?=P7e{nbDIb}^Rk+${Fe8j0(e$+MJSc2xrm4Mi=709L=R4oov)}!8(^FlB1qeDG7H_>bFT3_3A;7#ufLLR;tjf(c7e+2$vEE7eB8Ov8%hR5lpPuO?)`*S9rRKtHi!n|y&d!N7hAYOL0?R6kX?a$GWvLl>vT0eNS@Ob{O)JduJap#Fa3v-zTq#oi>)`=4bX#vWO3^o`c&l*Uw*5?^6ze?Vw(mB00C#LkyA0fxR)t)cy4*27^P@)OCn||=S?meiR<Y<haDClw%D?px#_Mq}RO5Neo5;27FOWO7?mmS)=T+h!b8ueKlYbG;t^R9?Z@=jUT+JMyd4DOO{2d0IS8E>Gigha)R8K|@#%oV|Ixuc;3f<RJ-y(PXRQv(tQAewkr}z@~!8U&Zo~z03H1AG#>Q8j{LCo9RegosL>?D44M-%cWQ#<A__Vh*GRY!H$7a`YPk3w!0Av9mfLgbF}=P7>7cFH?74Y^)fMDdY7V*R4vNs3>*pZLeyIxz0gT;xj7mz2jl<T}>Tok;bx{eWCIpJ>DLEpc|tchLj6&2WtRk~9{%Bb4H;?Z+@)&r8C-YLS~MziSKi^Zvj$I4(I0xq5Cm)-S^DAXk>}p?NO{QhccqxxQd7a?Sr9-PbjL<l024N7Fu}{&@OP{)&34XHq`hZ$;l#d_HRjXx@djSf{wt`!(veIaKHIC#aspYsi(>2D;x}XQ;nX-Ctq;e0R!Ud6?#{xs6=?IiB)_ndrIPx<LFD8_oMh3FZ+!=aB2o-y?Ul9H2g@+AkrmPM|y?D(10OH6yq7eMWql4fCj_r*XZjpSn^0)`L{frW*Pm+)SeUOS-Xdwz<Sb0L`l=*H9mvb`YQP3Egj<3Hv4*Kfi!^)-RzxSN%rMrLzIKy7yg*-#>!#cdSINC-6E<ZKmf{pV&hGQ>s%5JV5I_=GXJcU+ky&hCQ@?miC>-b(P^t_xsHI6kmS}xo(P}_*_5YBU+IwdCyWkdJ#Rx?DNR2mh}|Bs}t){Z=6IfqW4iBN^@zQWYr^Ad(YCm9ZvYaP}>h9x7FUG^*QSu>f63kby(;4eB6I@O9}3K;_A^l+6U~oUs>Nyu_5oTF2{PJ721Ew0`16;`ykg0XE9!z(zzPA;$y!J>ezUU_Pw@*668um7w)^~Ptra)&btZDwfNpU$PIUWkgv|8eJQ6Oxf&Eq_gi*_*42*JdT?KC>Y?}}FJZi+f7D%^XI(V)ZA2ONP0P*e$9bHo9_#%LIInGCK5|Fs2IBT36^-c+yzLf+_g;*35dzFzzU^{MLtb?N;TY7vf7Rtq|5vZN8L|KSRX0o4;4E#Jv{|f=NehIfCe4R^&~eg&_<Ya@4Q7QHU-m)AKwmj7nEhaEkq~hEPSR$w4;ss3VC+ctK}Sn7NPC2H7+4{XQCb9FGqM_Z42<<-A9Sp=Y0{?hm}#sqZaiQ2V;|ICS`^0_*#~`;EnHeO`_X)T6p#039~73x1Zflb+62~7oMVc#81`d0SBSJpJSK#70$+#tF!n*GOPkE`A?$;O^7Y9>e9%Z96E?&Logpn=TAZ}U*#}jnxk`htv*GN64r3p_m)zKQ<2Ww?i=WQDSRrnXwAs=U*auDIScvmxAJmg`!aUCGgTj%X>f{{Y@=u?be;zt4vIjmm|2p!)zw6MEJu=rHf8O-e;rMmxEPpGdn(!;}cWfeQ5&'

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
