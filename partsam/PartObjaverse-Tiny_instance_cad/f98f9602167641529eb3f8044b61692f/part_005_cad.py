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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f98f9602167641529eb3f8044b61692f/part_005.stl', 'relative_path': 'f98f9602167641529eb3f8044b61692f/part_005.stl', 'source_sha256': '5046ffd246f46c8be8484a53d5d8f1c544aa53a19fbb15c0dded06d1813d572b', 'input_faces': 152, 'input_vertices': 89, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.49985942244529724, 0.08965182304382324, 0.1892324537038803], [0.18330048024654388, 0.2094208151102066, 0.2542967200279236]]}
GEOMETRY_BASE85 = 'c$}qJeN2^A7(WPzA&MyYg}@6U7lcRz6cP0`h2lfKh9J(8i*lXjH<*ea^_CiQntjbI*Xmt=l+~u0D?bW-{Q?vPBVCzjcda!yr!%!yF0*r<=SSYtYHM}3XTRV1-E*Gjcb;?J>nrZ!z@SLMpLlUJygusdZbGOC6Om$tw`TeLIo{gz#Y^h~L@(0SrxRbDTsFx)BS5SWYh2ad+Br3@T*H+&H^-G`xaKaYSzc4MxN=ENwO8o{RSRpqQm>s?wbU!e$vLCajLeiYW1aC|KcUis=i|HI9+qgdZ)qMU(Z2S=8HJwATbk~?zlOhG)y(>&)>CS1zWXB0w|{NWbkFQ{G~Z~exukUKm+%v6Y<*UKn)Ka^G~H?LI7#c8dR<hyulm#xns@s~3*kFGG~N1U0oRGxd|v6!_0jBa;rHzS6-(2d<aR=_&wY;ct5=Sa|LxalzQ`%i_0kTWe?IU_rP~+J9;UiGGReQaTWGp?b{F{(Tk@L7XL4O5)!ja#mGrGHP4|^1(te#Cub)u5IJB1cJ9`Yxx7MCKrgXD$=jT)}_8F?{WE|6U5qyX1zL54d<w@N{{WRWvp6kB3;VpmNoV}dtit7=tQU6za9h(36W}bg{{x*Nz>|e+8?R#74eBXKXAo&kCNq)rb9hz=lnLy{|h>vJL=H3OzXg~XN&(i$&Shp%ds1MfVz&4r}x0mO~)lvU_gZk2ZqkbRj^^U`R_=)EGYWI^a3a9aYzo<LI`#ZpT{<Y&YZ-|ff<w-h7x_vqP5RFqgzx4y_)~7?cpKa{Z+TOtDu{4J7ZP;|$uT^k}^IT(}R_JP~>$Duvd>R8-H!dF0e3}!pxIcG}YI%GKoZohzAl<jKC;4<-$dlQ~c^2OKl;({LqCN<#QLF38;5^RhMy=0g>IZa=)}|)T)7HTE*~9(u?P}8e7^C4c=#=J1n8=^l!g)5&*iU(4;WMj6^Wzk99*?J0I~VcY8NOEsTDAOU1<$wUwXvSpMET8f)SdeU@2hbA0U9?Cq`KCCcJ03Tj_1(xYh7s9?v)68j(?Z7oYVX}FJr%}&TIb7i3d2(p0BjJ#_nxA-*-W~S4Ilw7c)Av^YU!q{@e8(TL0}qt)!dxI`n&Zll^<Vg-ui^VI}R$oKisd)9zkGx@hjrzbD<J`MFqMLb|<m1MSz|8&C6{t8UKoa|`WDBz5I`{`J%*em*Pde%imk#J`7|OIdG7;(Z<EJVx;}(mmV8lTXLXevIGBdH%P_lt<()=HK}br;~0xv61_q^D_TF51Xm^u?tvt#?93HILnIp{!~7$<?*;Vzxl~5(tY(q`2Lh3&-P00PjTozTIc2d*xy%bb$zoqk0-;U_0y?1!p}>eDy^<PkNsHl=V*1UMaZ+Mn)5ull<t)%fuGl_wYug?&SS^S)ABeQSvStG?nGba`?;R;i>DW8_rY^>3g73k3$=5%M!muR?%i0V`7sWopO+Tv{a<#L?^}MYcJ6jL=dl}}()#J!!~OBiS)ttrE6&|K&aJ%_9c*8I&JK|&WIQ0>isn}Ny%H%=eLC^)Uy0^t{i|1^jO^k6^PMO(PkI<DV+?R2_!w|gMxu-q8L0@xvk;1B%6M2tp^Whe#UDi|K3T>z8PjFB5sH^16t6(7co_x234S~V;~4l-{6QHR$ggm!AJ4`(8?_ZLl~D%o3P<?ya*P$`fJe(1gx)9|=f~qPj>Dc6AA%kw1Jl9NfWv_4;KRUk5b3C!j`brDsqmSNy>+h5K<*6mA`O@Xo(7%_91N~70X!MJ)B6ydLn3%QFabOsJO-ioKp6vo(ZB@o1k{U03`YM3!_y!{5_*|0_}&x&C;9PwasQ6x`<;iviNJjDM}S4Zd~kI?ri%Obb1G^moCdDY4L%9H2si~?VF`E<_#=L`O@!hTfF<A)zzYzH7t44ISPCowFG0OhgyLmDH+UI%IqIsj83P;$Zpd&6eqI$8g6HA;0l?1lRL`V(Hb(<Tfvaae1%6ZfypP8jJ`6O({oe)`dav+7@ErIZ4Xp6XukvL9OTqKtYb-DtT%A`oJZ8h^bofd^j}<0@tN)QcAfpQ~5PYbNTp6*zhroNv2*<i`tWmt5jQ%o)14n}Qkr9b?kyxX6u#B!Ug1|#C4uB@WgE5YUhd#ha@ZqR66qpMhA)_~Z^@gW@*jpg-2cm}hgvscEbv>{q0-i$feF(l&JPP@S0*8YKVNED73_KLP7cc@m0=YVQKa6`q>jR7e?}l7GfxW=HU?2Dk1AW&GYogG<D0qxTull233j2chz&^VJgTdX!0bL>k|LIR2_dgaj)c+44e_g4+7Wl91D~Er+B)E%%RsZD1x`<^Ge^fgae*hN3NW1'

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
