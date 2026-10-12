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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cffd007512a74a47b48390e1777c2afa/part_007.stl', 'relative_path': 'cffd007512a74a47b48390e1777c2afa/part_007.stl', 'source_sha256': 'd1a2bbd84d18b24b7a3442e51976d484410fe72b287ffa59987fe746229abf27', 'input_faces': 106, 'input_vertices': 90, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.30456018447875977, 0.08744737505912781, -0.42183753848075867], [0.3833792209625244, 0.1329965889453888, -0.4119775593280792]]}
GEOMETRY_BASE85 = 'c$}q|YiyHM7{}js7ujHL!y+pK){a4UDPuQwA1%-hu+SA9gOT7iSUVPUgLYXkxX{F4qWHyl$r3&oj9+v?zwrUqtqp>Ui8_L^1!E!$N(2&#Vvq!)=e+0Nvp#1vG5RJ?{=fb5^z`Z3+p~8*PfDsu6PHyRyEZp|f03r~TB4b>VSjL_|BydaK5+CEgO;Ove#P@0@19-0PJ=eAov`)#Lx+O4MvJXEP;awaY=ObxP_Sp9YcSaB=f1V)rI4Tb(BYn=e)e;5LxtT^U1GP4SpMsk$!EATa?Qaa{QJT4JhjK;HzpJPoq+Bww=XC43;JgUbl?5U=Sh9|QH1)hgJPX~my&wt!wKpy4~uo~$CCQ!Z&BTc|F|uD>B)=w{1Y=tz0>xI@cYZY)qUixani5&c)#YT6TWq~?teV^S5of`zb5<#uL?i6Ka#k<>gD=xo)Ug!d4#O5c)5PpsPLo5E|7l3%YN5K!dq)Eka-j@=lOLC?|YA~ulV@-;Tu<lH-AjlSH0Z-FK2}xyGiy(^|F8R2jTa<PxeRk^79UA-|7BJ(?v4B;$?qtn(#*+(EU-o+@C;5cy}tf-&DV#f3%Ixqj)(_+*?15B<+V^&_DDjl5`$;xt~8jye{tBtO>IJikI`>`cwD^F*=Xp<vi1d8Qq7v=;u|u?ElIrywybaQ}J?shg0|`b~?Y}Wq++p__IIJ`$zHee!kTweD-NFzv|`u-yacv+(GA8yqsq$Bz)U(I=|v&|M?Tb->sP-^C(`<(|uO>ZFkA~s+a4#&Iv#L8C_rTa)0uoc;5_i9;#mUr%wt0`W1RUD_+hM_j9KvllH^U-=Eio_jOFt`;&UPKYdxVx-Xoj=ego#zsD^6*t_KKh3e%zMWwoT9)3B>vpd=+=FhGceo=ai_$Q5GoiE-NpLgZ}zAs+kzqv}kcZ!$$9BbEo^u5k#;yU4T2Sk6%hxEKvyqtgRMX^q<F-F$uIw|JA<R+g>+wq3*1&`;wk321%nRWFaPt!DB8SH5((39|}#3jGtnfy_yzvf>(Dpgk0{?BKn%v3gm5u@{w_!C?zG9AqQQ*Z`WDR4QgR<g=Qan47Ug7d*8D9&X_JGcy7jjRFlYz9|@n^2q`D9%n+TacTO&EQSoT4W8l7F>?BgUi9i$Wm}Icr|h*cr|z_G6%dA{4|R55>}bW3>4?Z$Q*DE_H;3da~6toE;1jS3tojR0j~nvkY!*Scs;TjydJy}*#zDQZb3T0E#S?pI#|8H%8T3yevZ|4{C>74{I2-xw&As#!8=%aSUt~b7mD*9R0rG&R%TX(NGrGyT!dT$E&^8}E5TLZMq~rH5!{O6?8bY$F{1~(71;pZ3a&#|g6qH=kZZsjz-y6K@LF&I(hM#DFK6`(av9PLHe-*Lp*TOw%7n~At^ntOEyzN!1-uSf1YQTOKvsb(!1c&Ra6Q<CYz4c(J5ijyNH;jX?_OjFcsHwdR&A_&$i2vR@Lq5yit|3+?=cunDgX2@?)(+z2Ojx{SA8Wt?h{{G&VH1Kzt5A#&r^2T8nt6AZ}JmC`y0qhYy|'

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
