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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/358eb80d4d074dee8cd65b4b0fa187f7/part_001.stl', 'relative_path': '358eb80d4d074dee8cd65b4b0fa187f7/part_001.stl', 'source_sha256': 'bcd4f0a4bc269af47b7bdf35ef2f9c005f4a8054e463c29cbd525e4360d55c37', 'input_faces': 224, 'input_vertices': 169, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.24304604530334473, 0.009710520505905151, -0.08451198041439056], [0.11545589566230774, 0.24825003743171692, 0.28237056732177734]]}
GEOMETRY_BASE85 = 'c$}q~X>3$g7=}*)H$XOv3lu1zwkl9It0GD*0z#owg$jx?1zKCA+q71;!nHsx*a8Ap)Pe;BmuTWfT!>-ff(9dqCi+87nwS`WncxqNF(#gG`kXs+zqw6}PV(k``u6L&-}%nW+{v`4pm(2i)BPB2B3C@$x@3?sqW&h`G?Yf`D^`})O{l6_mu3dVb9p%5Tex^Z(b6>2U^Zl}Dy>@?&6<{(HNEWStZ|uHW!2I8Xi3%b>gcLc$!C|WsVlX4U3p1Osr@;7QtmC|GN)WOF0(Q7KR)_O4`VXUo)mxohC?%~d3z5ZKN*tewVr<`EcdFj-weyU2CR7_ERQY!<)yH^v--88q4|QEX9M|&>?5IllBe|P>UE#wDSeWs^yzZlr^|cj(|oz9J&;eB^-jEA_fH<t{kwYIKY8Xr)xXOls(+W)sQ$@23swK*T|M+~-fe44&b@DX9}nA?%RRL(zh3Rj<$7N(&r|#I>(#zouJ`3~y)T!W_rmvO@*AUp{H;;3`1*QZ<Xw7S<Pp6uw~pSI%k{p<y@hID<gqhqU*zV5+Ly~`1^1Pg<%Ra?@|fz=<+@KlSADv?OZDk;-KU?cK4bg7`!s&;CBc6Dyf)a6%e|stKQ51*4ff-5b28YEpU+j#hu4cwg<aR>`noRH*LAtRuAg(=Nag7>@!y~R{BV4oABG+e%gy&`>yz`?SHE@7;m2UT%gxW-^_^n}bi~*BcGpMoeXafbs~I7=SvKVB<lHNJ_2aO5m#5Tkd*xJUJ-M#W`*r?jVf8LgsrPD6ht<d4K6*N=KK4QJ7vb04@kQu5(_TLlukRu6dO)r7@~N|7^)7eyW=U22`4T&p+da?U|2&tR=lwCSdmWemb!B_ldFkBk%jND|yt15gVY#l4HC3Gotykyea(ym-e*THi!q#!;rE`5=ey+|daoz6oN?C_<iS&^B^LOj0^U}Gi_Xf|c2%EpoU7s%3^Vhkq*Yo%5)%;zq=kMog{(i3J?_XEV-_O<j6W0yS->+Bm*SVgjp1;mrecsHR${8W^*SYJ{<$C@)*Y$e-e!ZH%%k}*IT+QFl)%^YIs`>l5nt$TD!TJ03YW_Oc^VIX#xvP(y7}Xv&f1SHNU9RV^b6v0J@7JsOyIjxT&(-|>T+QFVuA0A}tNACc8=Sviuja3FJx@J<oxA$3=9By5>!|yM%k}*t?_9r*(ASH~{pS_AzQ5}{rC#0Nb*}66{axoN_3Hkv^VIc&_i>%;dVPP_x&L}`>*&{u%3XbI|K6kVx{RN;h<E1R{z-D~ZD~CbKW}nx>&_3u>RleFFA97samUBU=9_*Ntu8U?rmQ6CD~b3ojPX7ED~XD!|LQA=$&;u4->)Rb*dDI5x(Xi%55or|;X(L7So|V*5PUIiV0om$;=SOD;Y(Owd<YWmi}!-Xd&7O<es~}FGCUm#_s9Fd;upaE;Y;xgVetX5_~r1W@K7W?3cms#1!v-;Ve#wXO!zu{5}b|aAmNGlBv||=cp{vOPlv^Cg~g}Ax$upwFFpYYPsOLf;<vz4;VJmdu=r$Hd>lLl9*=~tLBdz#H^Aa!Vew(`)$nk9Ff2X<9u8;Vm%$nE2s|Ag0guFo!b3T~k$5&d63)VN;2dU`g@mug$HU{<^R;*eoIxML_gLL+wGZD5AG11Y^)mhvEblwFS>@rk!w*?4w~C+#$rfAPXSD<slRaUz&8iu-knOVCY1M{ylihFifYmazl<Y~X9ah^>E7@v(zZ6xFJ#1A@Pv!J<A3aHLrFa><f%RI^Ml$JflT{;XBilvKn{f}8-XF1AgO-t1F{cMnC0Vsq4KuA_ro!v3*0JYx>{<9R=GTJOl09nGz^ogX^)}{E%0A1O#l!Ttnt4^w>m&42MSqp_RLu-Fvrms%Y@*K%%xfdPuBV^J=x;4ONtSPQr_~)ucqTp@o(a#w?}BH+bF3CxEwCy=!iD&JxDYPD=fVZ>JbVs3hxO;N<_fN}5H7)^a0y&%b;Rl^s~3^*9{h2558Q;;!nLf^#NQrfy(91;yc0eIzknZvUw{u-J#F=jRXY;ik3S3Vho8frho6Hx@B{Dx*6(1=tz746cne++Z-MJL>w8W2`RBun@Rjf)cokj;*RhVUJSXM3SA%=7oT<F73h{_ZJO?5s@jQuehAZGGUIRzrCftL?cf(DvJJa1Jaqhc0EAck?Fx<&(TbR9gbJAHfC!JR_v)l^T;|*{<EHjbUh`fH>d#`XYo)70U-(q|fTnv}t4JPqkAzY5Hh0Eb}NO(Km0=KZw?RbYtyl)G);s@b_%%&A@gT)(7;yqc|y~l{J!5d-mN|Si+6_)qkqJp$u>AidUmtNxG$%n_lKlt=t20wNu|7E*f%l{BwRB(ZOzOx@Fd&OVe=j79a`3JYVvrz'

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
