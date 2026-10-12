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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1d97ec6885464f6a9ce7a4cc955bff41/part_011.stl', 'relative_path': '1d97ec6885464f6a9ce7a4cc955bff41/part_011.stl', 'source_sha256': 'c916c14444b5acea91d2985716a3c36c91d1001af011aa8edddb4b69b1e7d9e8', 'input_faces': 58, 'input_vertices': 69, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.5911643505096436, 3.200204849243164, -0.6011466979980469], [1.2919421195983887, 4.43721866607666, 0.4713906943798065]]}
GEOMETRY_BASE85 = 'c$}qH4NO&K7(RexfFKZR0?HAA%g@yixC&@;RHhWuU6-~r(}TcO{6oPMf6`-?q$N39{*s>5YD#V~oz_@#{b}Z$CZ$oz#pBN+HBiKfX=UH{ysxFLwpQov+4J7#yx;S^=l#C(<IMHx5T?-4OKB^sK78jfMUm*Fgemh1OXe2k7nb&&HG6@V5)54)5BQx?V@Ep2c`5UhMYe*%()<!zrfM7HO1Ifno2$5FZb{y(NyQ}vg;F1$H>0#r=%rKhW*3V8@%=OGYHEUAeMSARhrcMnsJnWxR<K!mI7kz0eKnyjOV$>28oD0W90=X3&nf85CUj%z2<Xb$ilb6Db4YhLE%ZnJl2PAC-92gxbS3YKAM(fTsfAusN&1Qx1ElWWINl?5<HXxEZ~jT-Tjd*$U_RG!()|a+Uul_HhxvXfrh3lDz(@Zg<a_yF>!y+Z>er~#J#sYtpD+-tm4$^!-T36gbGR<e4&AEg(HZ_523>;xO&isDsT}#{S?|-x&x)dYPIL-Joq?Z|@0$_C`)ZM|>4%P?KL@&y-n0by%9!6Q__j7)KwW3nQ9t*tIfy);qtLab!B`jlS<g}AZ#%Ldbw<uaAB>XM(PyQ8FLZs~IrPn3JHm}V&-nHS$=a#_>T|;sT(3JW>563ixiQpF$B*#QT(^D#NAyIU+Uhf?!@Z^*y45=yx_gI4dd*$vx_ugSqo#_kEAm(9=C!rtQ+K@)*R%LO`RuA8pV&7VknizohR?Li(9NalS(^8?7SwyN1?yr|PoaI5@-FG0UP8WlI~@61eA#vQ@0?ElzROULX5R!|TbN7!AqPm`xRvywZ_&C`t~`%EwgudPKCv0|n#~2Y53<9cD;;TGqqqy^wQhBVu9l^cf6!|9>&{5%*1R3GPnLVb-z*qS`l3YAEALZ&-Sg1(P9Kwhaya^?Y&k>z_pYHHD`7J2C#|09jEJZDlf$ttYIOto8@tJWkH>?3*5ZL~jJ-(xY3hvnRrRG-_^(Nz^=iFG>$rL{bWN=y|N2m>=l%82_1J!t|7E#F_hTjb#B7JIx3?qT$k__rz5XiQU#>~0U)}f-bZh$s>YMJ5dX$RG(9LbnQ2n3ngTI>HMEbN<wC>Fdsh_*=kbiX%)ni{k>)ST<CayQ_3hke56X<z2Yz}norbT_O??CfzNoj*#*Mxk%aU4B2QqxFp?N0u;kD$-WF$Z+(=Par}Fd4c&aR7AP+eQ8{n^BKhk={o8xq|w${UrKh9>{>MEZa}l+wQ`BVYXyKH#Dl#a^A=D%{`;&7V=jP$Ng)@N8!0-q)sQ@X2bn%4NGdodhD7*y6+}D9}GwPA^3RaLpQ4Y$S3=~Q@Gx>%b>fB8}vMn81fzV`Nhqo=iH_KkDuQF-`XAIf8qstt_DX_J;$pkf5iv%{M?g&Jj?mWTXXTtj+}HKMUn6mZ%tR;L$6FJ%Hsk5{VTI5?O(kz9qIr3mDx+w5Gl|br4z>rbQS0(5XEs6pR;jZEXR`L`Mk`3l4Hp|1(F1w;@l)=nLk)SwyX=slAjjnBap^p`Y<Q4m-Ot;v1C<XfIxp9Gk{r+^AiXb2;o?A0O!c_{WzAKE)c_h-8q&V&gWAFGC0oQd~bmc0zMo|_7dp9<HI?Y93c=b5Xa}DnR~Ezia;jEnLI}T*W8(7$$<ii0txJu$Q;e%q)%UtB@Yy^bABSnl9L636!}S~D8o3GoXz9xoYR-t!RKYZKgW`Xau1#m2<14Gdohs5J2;j+h<hZ@`*JK<9*+wQ5zsi6+>s&UERH41uT5vJmv@-YKYgnHc^Gn%M?PHtI`Yxm_2H5I#e{#{yv|%-eC2wJ-yFd^We1es0ekd#m;'

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
