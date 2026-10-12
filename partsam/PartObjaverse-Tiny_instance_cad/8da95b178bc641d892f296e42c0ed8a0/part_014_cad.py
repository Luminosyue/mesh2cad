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

PART_NAME = 'part_014'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8da95b178bc641d892f296e42c0ed8a0/part_014.stl', 'relative_path': '8da95b178bc641d892f296e42c0ed8a0/part_014.stl', 'source_sha256': 'bab936ba20cd784e885b224c79505d48062c3b028ce3610f42724c5c4164b2ae', 'input_faces': 40, 'input_vertices': 45, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3453918695449829, 0.14914743602275848, -0.2778949737548828], [-0.17018502950668335, 0.44997507333755493, 0.28411075472831726]]}
GEOMETRY_BASE85 = 'c$}q`ZA?>F7{?DFn*}E*ohazIOrW?S8BP;4X1mJ_##CM1)Tks_gc6JjtgR%z=K8_NHZ@^p6ZM0BFlw+C#rYCZ+aL-kN_{~We5;x<-4cV*N&KMkod5Gwi@{{k+dTRIpI@JQ?z!hVJ+)b*`k4h?sbcDbZKk9BgitX+m_?<->0VgmaAlWOEQ=8F;OYwLrs=b$+2%%wO0mLH>~Ix1EfX}$#FAV~mS!m_ce<U0W%J9O#SX>u3KzQ^lDkR^D;zS<96K&c`*Kv4wn}@~D@IPi=t{cklNvm@^7Pj#KeD$;<@(`&JCxe%8k-dtarx)KOLD=Djkf}*?_NTDciR=Ee%pb|;IWr6j$br^i{JhR7ca(~#{Kv0#2*@0!H-)Tz~|Ro#B;w*JOwU##)EHK4<6j_A)Y<P6V9~*%(n*i;`!It(Ks{yB3^&3L8+d+fOsIU1^GRH8|uHC4Zfr5F7f2$#2^1a^>xp&KDyOJdT$WTXT&npiT<s~L)@N1+}?5gBEFAl51{_1r|lTGXAbfZ*M1@HZ<<Q$TH^-yZ}|Qa?jKs)<_qKcM&<{r>G}45+VTC-ogJ88!s;^^=g`9o;GUj8Q8%OG1XQyU&+qC)UJ&o~^~D>#`!LRbIm8R9u2Wy0p)aB-4*j>kIMJ(L;>xkJcrSM>)=Mmy=nd!g5D#?H_+NR6Ke|gir{JV7j0Z!!bo5Eo@A@5lM^R-f__LcAz-KR~`pF)=znHX-)}gC{=JTNJEb>M9s24k*v|^meht8`!cq<$0YV2`=>!m-VAHkWOP_cR*@jvb$*Tzple~rxQ7VvM%vCsAH9_q{CmEivRR@(n%?RbuHzp5F$;U@OKzved0bE&(T)=9sH`Zcxq{TY|GoI!nh4D}`YiO(0t^$g~@r+m=v72rnWDsVk#t)Iq;B>ro{4b-K@?DzG>z4djd-`;}Xt6to8<5k~ny-q!oCuy@iQnpTpNuGKog<(gYg4mv{eII!X$Ns+~?~C_7^3*ic=^Mow%|4o6CyF(KeVmMsWDJt=v5XI8B(i?MUTJ^!iR_24n%ECvZ)P39-poFMHI{t>`@u5eSqHMlvLDD^o#Pf6pUFt(P<|L|7W-lBhjJ*N#QHh=B=*BuGuaPk{|Re4`w^@utm*8Pj%1(0USmyVud)A>L-{n;k?hmhXRxNT&tN}_HIu!~8WCxZdfQ*}>&s9L?)3-#=AFH_b@-i6<yfyaxy>4_`Y$5o=SQj4YG;U-F5k}?'

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
