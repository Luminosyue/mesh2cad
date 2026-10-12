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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ec56d0baa8f492da805fcf2ea98de4b/part_004.stl', 'relative_path': '8ec56d0baa8f492da805fcf2ea98de4b/part_004.stl', 'source_sha256': '5f3a0f0628e3b4c737e9a900a78074655c582042cdaa4b77352f6c640529c2b4', 'input_faces': 150, 'input_vertices': 118, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.01347561925649643, -0.14461734890937805, -0.2844507098197937], [0.1843251883983612, -0.12007734179496765, -0.15130454301834106]]}
GEOMETRY_BASE85 = 'c$}q}3s4p38HN`{5fu@{2vKoS;UFS{5=A7q-X(|v-tdO2Toh0w2c_QH*_axQ#0we*O{qQJk|L?mICf0Ea8STIs5QnknjEFl#3=Eu?P$`o@AoFrPCL_SkMqy_@c8lVxBu?hb2Kr&sjH77uK=aS<MG_}trW#vtrZ`oAj7&KD=i~GEH`hli_#X}eEpak$4p2_oa~|$C`&Er8Tn~eOSEc<$&9jus+P?8)&<s?xijWl(=$vzV&>fZ45!bZGczy4`EzhYL{zBSw@0Y@OZ9(zwKQkwxVdnUGwe5ND=W-Y2A!zDjH&OK-WZxGe!V7s#d3IcRsW;r&)P%Q$DUjR-#8BS>X@n;_-`hxMW4c>@Q(X+;=5Skm1{v#Uolkr+&&7guK&hv{;XfDmil`G)}c@8A{^KLw#;MXPhXFEH+Ohj-8HFiufrQ1cB7B|_~-D(>W_<XT<>S_+OLx3xH~NyOs`#7jy_8F*Tk1xhgYASLcMMOl4|r>a2H;wh{gQ2?^eSrpZ*=*=Cd93j!%+~!yk&+XnMW9CiCwa3vY}w;En3((to8PeOf<&*J|EDe=T;Gc=w!lP48$7l=`5p@LIlS3H-M6s5eFh%lXz%g4fptqh58;S9RHh^QzC2IX7li!FLOV*DMWE@A?aP<=sQ#M>d5wb}y9rV}YA7e@TBi?&?yhe^3UmMQ^Tv_j^z3&lH#9etYvRsejKR`>8(_AFvzsN<^@nZ~Efj;k+KD$n{DsI|iS#7hXG6D|7DHC;sdmc;)VA=wrM0iTJBiZRlSVAot;^EAaN90(jLkN9H{ECA{`S%r?|#7oc9*WX1gItx534q?M@GhULL)8~k?Sy2osi{kb<CeRQ{Qcs(pc=HE3>eEl?d<Fuz--z{12>V-YxOa6xbx_yJp8Fx*5{4AM&ZL#=~r$4~_lU(Kf@@fy+=dNGC+ZX*&_IXSnne)NUa_rAaxj(gyd9puWe=L5mx4hr?rO7_5Y4IWYKjQTYw@Q6!J9t~~9Jzmdi@DGF@Oth=d0#Ky0`C|azZd=8ddc~2FNC)xPlR{GZIb#>L+Z2B;BC3z$@QJ{k<_=EC%)8Go<DD_mHqTG#7~Qp_gD5ong62$2XUWNt&{6mP<k5vY7M*+`MsQ1)E;=fV;#I&*GcN{Z;|?>r||Z+7v+4t{v`F&-43Du+XLjek#HGad8u4{t7w_CIQk6o=90rWUw=dTmv1?R<2zQv+lP9{JY_rKm1RZn#*{|6E=&IauelwB*V<OebKpjW)JI>GK9_pnxQ@C{rM~_%cs=-u95>tLEc*4HeFS~h7;@j1`^x-(UIlM2mOlF2e(;Vj<0>$J<TjbJ(Y+S+o;Ts`=lo@!uq&vyKY1wrFMpN#?YH4=H(T4W&okbX>%O<)B>ujWC%p1d-WRr{JK|6K!#gVPN}r0m@JeMcym7Z$j$7FR=c`*Z>9Z<S?uTZ+vd`bng142+=bFQ{R~`0e&?<PnR`x+Tn}T|K`ETX886ncg+ba9K;=1@Y@_bgla^U*fcYH1LG%UmW*Kwd8-gwKa65emDoL5TJIn*zkD*oG!a$oIrm;Db*7vJQ%T=zgfxeu$)!P~A#A3f#~uA}3^C3wx{`y=@M6U}j5Y<KjdIIsOHq)+aB^f3lzil3b)&#?shiZXcP^C+2fazE^ka$q04`nVSTwZkLe9cT1o*oT87rT+&Fa=uft;BEV5PW65q&e!oYN9qf2OP~F><$ZA?A70CNCi4d+%l<@0RiS>Y?6ZAIBfM5R1YUo-6!Y63K7rR4CrN!#xLlVVPq05)>r{9n?XdK(al!s*i_~h|C;LXpbLnZAobQKS;T>BW<hWOto|ohFlKO&1^f9_dq29O^0dFsp`(N8pDD^2{z#Ds3$~+ANWd30{;MGfVe`+B&P_MPQCG``m^7*xL5bBj~|A5ykd4HBXLcO7nsKGofdr2Q}zY93-<Z<v?syrW*Uk6^0xw7Hyr|!skZ48zAlXJy?CC?vyO9Z@eaiR1td_(H<BH@+d^-@3NhWO2wF{d&7_wcsx&T`zydYL~Y;5g>V3Og!w<1xSTEE?Vzzg#}Q>SxJ$y`KxOU+*o?vEa3`KN-v5ZAHhW|LEU{|6wh>;`>0J4@b7btM9LaSBt%5&gErtT^^UnJbn4T$SOZyk@&*5`O9Hb3s<>0pCHcV?))~NIrF)%@}@LjKjy#xDxVek-+h&TCH(*WD&OBZLqF#l$YpXgGm;!lj$yt+jv>b~qsX!3!OQ{V!Q^4gLF8fN1m+NO0y&xa8abIfkvW!Z=4A3jvd(34I&&J?%$ekL@;qh+c^-K_m&va)=a63~=QFd(X3iz&lNT~`$P38}xJ<S(v&dF*9&<K1kDSX)Bj=JcnbXOc<XOzA<XPky%t_=K<SEQ?<SFC{%rWE%<V5CBaw0jNsgdK!qnNLfN0CP`2a-pShclze!^tC=G31ftIA$z4jy#$<m^_-C#2iLWB9CV#kj+dck0+-vCz4ahsZ5>h;ao2%=0Eo(+ml<9+j5!Qf!T@Nf$Y!hM)oIncdig-Pi8lAPjV=i$$`vH<Un#~W_xmb&f1yF<Stw$`!YSqzGN@wYQc16dXPPM&aPZ0H)XaZHzhacGTEKWWN&5%vNzd}=}-0}tIY0Xl^pck-UV@)+{?Kln7x@H<lf|PW>0cBxeqgx+=twk%j7U-AUTX|VRj~W=3ZO4Ozy#Dasbnp96)}V=|z5--0rz+(~iqzPv>gIbYr$4yOEnPUCFMzPEEK>R+!C|pI;`saGBhU=}vA&ZpmeG8>Tn84cUk3NA@9iWUAzj<gUyha#wP&b0x;RH1TQrpZ-hk=a*p){=$FI{p)YO`0@YzZ`L|{{q$uZF}@l0rHS*8`2kX7?!NL*&0>f2'

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
