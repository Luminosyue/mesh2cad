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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f98f9602167641529eb3f8044b61692f/part_007.stl', 'relative_path': 'f98f9602167641529eb3f8044b61692f/part_007.stl', 'source_sha256': '1d6699a55fd18df5c0fd1c269ffc16bc5c7422a7fca773244b5e26d5930eff3d', 'input_faces': 130, 'input_vertices': 87, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.13191723823547363, 0.1045953705906868, 0.01292012631893158], [0.33019503951072693, 0.3282357454299927, 0.24034951627254486]]}
GEOMETRY_BASE85 = 'c$}q|eM}Tb7{=!~P(fQxMXe&TSFI<AfS>{g$|8tX1WpmOn(9%7Xll?NsIk^$n`oM98&id78vj5mMr%wzjA^O;SP>AkR-m>~qxRaS+O$S%|FBJKKX%@E*4-PgNz*QwJimQzc4qdSnRgani8C^eiObE>n~uJ8cmQL(3}SI?LrtJz^@^JM)Vg(>9Lz;Nzf9d-R$1zM%E30U&7PGt^(z7%uj0w8&Gw`yp4zp6hCp@Q^0k4LHQX<*UQ=IV`1Px**VP#J6SA{Xl+2_QWsCA(uNXdtH^0&I4N>B~U0k)qUr*-Se7*6HUasoQjcr_mPVXtM&F4D%=()FCr|G$+h2$$6U+ARgD-M1@_Z^qX*ULANuje+k*?nd3@7<)|x4&!mSz3bVx6XAYq@CF7)GsSNN#hJQCR2MX=N8r1N_U*G`~GG7KPTUv@)6ZrpGm%UsH>gs=XRg6`~E<>h(pGScc{NDRigbR&JKF-&aJKVdvpf9H*0Ai^`~Ca?Y@??i{4kAzgV=B_B!>ae0-nOU%$E2?&}9Oo}=gP{?uak)f>xt=)UFNS-Y<--be4%eC_ses^_~Td}k)bLHVxgoZVNBEV)Q=8Pa%y`oD5r__>Q{yh`D&4!f^k+fVc2*NP8PySoq2?`p(Yiih4^+8*Lx{Z_<%$`z`wuGQ&YU%Bl=G0%I%I*WLp;;WYbDdN{RyxZ=xo9jQNcGtx0vHRN7pIo5vMD99o_x0!F>Ae^W93%hWWl?|bdm?VPzdCRC*)v~KeeJIo-=^RF*F-z@ezCq^9oc2~m6p8}cXo6^BgOmc*)-nZ)dE^KTGhTzyRSPsL_bcI#;+czqvy3oFRfSQ)|@uGAI!f=abZ8cEY^*4w;1o~PTD_uPp~b-Uv!M>H(zkK+kMveGx@<I&z=eKZ$*p#w%zZt`+7nP^`~~Qvmx~--4XA5ef{<jzwiRh3p-r5GsI7+rFqeR+5B0Ee{~1NKiF|P#MdXxxhUe@b;Ry#J&rGEJa076JgT>s_JoZa{D<OJcBd!YyqLZ`FKp+y-f;77`trPMlgIalTUVwpuPb#%R&Tg<Zu;^%H+^}Xo4&lxoBJOZ?HqnZ<S*AHksn)6^@ZD~4}58#Dt%)qkH~qz^yNIDj_`<lD(4yaa-PvV#ln~Jp6SbZ&-CTIXZmv9)4adY{X=;ezMO|Owo1fN%ICqYo5cJ{=Yr|W=K^cpBHEG89n*j4+;JZg>s~qsO<z6-O<z6-AG9N#gUzqq741mpuYdYI^5yf||AU+Mn|$t@e#p7+3;D`f-ZipmZ$HL(i8j7+YO8IZINaoyso_6yR!{j?pE#2<)Boo;PRv+i438OQI11;1&_}@o!A|HPuoD~ueFPi>9tIr&9tKvRkAoF(5_AGM2|N{=37!g8p)<fLxCA-}Tmr6u&IMP1=RuzY&jS}g^T7q+Y0xQPt`os|Mwx9CFAC>b&;{UGU>~#!>;qRq=YuQ3<<MeqIk*U#3oZiZKqrB7z{$|j;AHS9=wR?Da4fVRI2IfUb$}zm4BDSr7w0JG5O5UO1x*0E!0{-Y(~Oc1O@t<Z6TxxNA>cT0G_*fB8XN(2fFr;Ip#8uDz(b*f!9&4gprgTKz^Twl;8buHG#8u&o(U}m&jgo3=YvbZ3!zouh2S#i0&p3)5IP%N2+oG)fwRHsD0zr?8aM^&1y6)dgL=W!zy;7*%-Tns=RtkU+IO5Qpq0$pr<_Zm<;>dGoK<KMv+@Avsn8r|<qghB&}3%i8O{oH6tnUY=V8!TX5}%?G0;e6<vq?$C}UQh<kvuG6tnUw=iyKnv+^)!H#8pX22VtZN4(=PH=IWrWt>r-K;i6xjt6_d8PLh#4DfUw{}M+;ob#Xlb+;~!HoW~GdHKoE<Iw)(4Wq3Ghoi3~ijKqx<L@~`TX|&J->zQ@bN'

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
