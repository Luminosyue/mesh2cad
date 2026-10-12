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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ec56d0baa8f492da805fcf2ea98de4b/part_005.stl', 'relative_path': '8ec56d0baa8f492da805fcf2ea98de4b/part_005.stl', 'source_sha256': '0f4984b1af32e3fff4385f8f29981f46b6e20c5e7b1c1fae9bac1411a474b25c', 'input_faces': 144, 'input_vertices': 102, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.09522231668233871, -0.14501938223838806, -0.2991243600845337], [0.17547088861465454, -0.12034554034471512, -0.20818060636520386]]}
GEOMETRY_BASE85 = 'c$}q}3s4p38HRsUG@u|vL=lk{<svtcO9U!$qXvTrhpTcCIfw_U6E6khXq0vxHBm7`Cnhm9F`jftTO~6!jdql%tcV#+jEb?=R*c6OXf>%5Ll9yTTlRb3v@z4pblNks^FBO$eE+|@|NeW1oXmlP{1iUp)r*b$&iQyMWgWwmpIYsxS+%6nQ5(B_<ytr8Bi{OampifxvvP{v)M~XZe6gdpvL-xL3!he%93HKOSFNa7Ra3FNd_~P-hvm~No~(8B``RB@taSAM95E#>K3Yqd6s^^1|KrD+g}u&xXnKE|bMG8)vF5Zc;;fZM^D^=3@5Qb1b4;pu<+Ta^PaCA(6)-`(zW)IF+;5P2<yQ!Q<(PPT{#2>g-Q&^cj`v~9>$^WUrGL*$7`Hb_yuG|$`sg<gig)_{48C%^)VsFSpOZe9Uly;aSyJ!vd<j0;zuEG}?+##|)32SeQv3B-@%Hs$(#LGDpBFzaNW6A+y!6q$dZk`<#G$@whV(JN?htQ2l_cKvY!}XJWa)Wap9SLeJ*Cpe{#M`zGX583;#J94GOoViuJkb~&tTjuzsGsymPx&qegpny39f(CPsJ-+7tX8lV2kv*e;4!5aDT`0&fR-3&sRPbuiM@fZ_X-`{_6FaxG%pwBwlZ8z<po+>iaUz-4pQFMq}LdHq>8zSG-ERFZD+9eyO(yo)fQ~8;d^OuZh=lzrnaZ7ja&`&Ej3VzZGu`t(Ez!1fyO0lnpr|<8DpC`pLR1_2%p(@vg@WjJtKY)a&cF!w-HQ=T#So`{mz+K0{NneqKz4?>;47HFe9lX7y58C;H^e;+?iu%s-@Dyt8@hQK@hJ73MkW3mMmNZ4+<K^um1hzVV*)bK56g+w%+Y_A{NB=a6^A>ppEVPiJR~)T_2u@y5Ia%zx#VGEcqcEb4czka3+2Hr&S>e-v+z=)*jhx?x>y`4aVCZ^SyxnlAO`<mzMMpEK}$HI2r788NU$#yyrI{f!;hv2Gj3i+8y%MgODi828*%@p|SMtlRp97i8RzGEkrROI(NB9(b;s=Ai%bCh6}Q=nFsmmU#30I9!L=4w;WS8Ei`Z&#SSXH`dB^Q=wtvT|02!ReQB~^IjS1dty-UkuLYk_;itYXHylP_dzk@?H|1&UXSN>SlEpD+x{xv?CwOLjvn-Hgg3g@WB!M3;5prO2Yv1xk^WlBU$7pY@jWi}0XFf@qGVjRPezH?Klt{T)MY;=-gUVSUhl$uYI<cpX2F)@xc-~5Z}@*KUiH0={-F*$*H=Eq{d)E=`cy|^o)w>=|AkBNZuezeb!ss7&-bsO&*m7c&m|*2l;6kR5U+XXVjVtHCF5$VyU=IMHtYkZ2TQ%a=9YN%8$b9-d6;L`-_WOO4c4I+BK797KKS69SSNp;DBiUh-bl+wpTmLTjjxPWxsSn4%(HN<TxZwyP2$zIH}E{BZN@q|^tO1d_pF?+eiZ9LHJ=b~tlE$Bns5N~+;>vEYfTZx_1q&~F9<&&^?SReUi-r(_zz>mt4h2FRn;l<IjF<0O~ZW&!Tr*sGR3=Yjgxw(ZwKm^WsBF2?8o(~|3th|vP8V|Al8r8oq_dps#d)2!1_^PdE$**Pm8zL^kUpTtXmbg0rhEdc)o@|gmsme+$Qs}ZAbmnx6%LA8RG5VtiyiT(+5AIK)l|A{nKc+;k-i2#XA=@U_V!tc#aZG)bB#Q8B~XHUuY9=Tx`cW_u3}jx$(MqH7yYLxBUfNpYl%l2EJc*HDFwy+v2rAyr+zUov42^<fNR}>v;c~SJ&Zr{A`MNb1(K8y|Etq@T^Yp+NEf`7b3Ags|okS+mB;^P&@CUk3IcenU7}->K_ikc@^i2*B4?xSDQjH&&H+V&G$aXe0D^m{`8aZ*YLiuzcvN;{o+&TUytum=E}qiEjbT-n|!PExqN+y^$JnSqyO7vRmJzdN?OwTe3$?JtK^cz|L&_~V&eb%RdP=M9DdY)%w;}Co=eVVK2ElB7CD=2W6mVo$XPrr&SXv}XOc6Rsbnh?$r)sw8BNy7NzC!&Byt>c3^|S*$$Xd`Ne*LrlEcWs%pv4pvLDl(>__(DVexS0Ao6hXFy;XA04|$hJgkog(~ayw9?HXFZ{|R<H`$jtm~7=kWM8sB(~Im+)|ey68aaYFmK;HjVoo4iIfWcWp2oxCbmmlYIysLygPcd6$DBi+M=oN{B^QxPnb~A3ZRAq&0%jI@0l9>S#l_4_axr;6GlM*zoX^zB`Q+KmB=T%>8Z(ZZMowWyl2gd>%rJ61IhGkrjwOdO{m7x@Af^vFh#bHiP7WZCW)35dCXZx#kVle7F^7^zkpr3D<UsN`rZ0IMIh^TF4kyPjHF69&ff+$gASW}U$W~4xCzEq{SX{tNCl`>*n0e$fayfGzxtv_VEFxEsE19KaD;JO}$qr@-*+E{+!{SBEV)7!gojIRuCog2?lNXW;nX}1-<XmPNIhXtdGll#F`B7#(`BCyC%vkax<jKrX@?`QPW)OK2c_K4_Jdqq?-MdV;0e%Dj)4y{5^)al?@_~Qs{O~Uyd~JXKFSGl5{qrTBlj&~lsr?)G0QHmpJZ-I1^$$Sf_~-'

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
