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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2e5436e635dc4336984c76a5f92c7141/part_002.stl', 'relative_path': '2e5436e635dc4336984c76a5f92c7141/part_002.stl', 'source_sha256': 'b4b9aa71ddfc160a0c35d31d11e6d6f8d56dd5d2ed9d8d2bbfc6beae3154e6b7', 'input_faces': 258, 'input_vertices': 204, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.009584452956914902, -0.018321443349123, -0.24410201609134674], [0.025031547993421555, 0.14242783188819885, 0.49345123767852783]]}
GEOMETRY_BASE85 = 'c$}r03vg7`8OJXmPk9Ilf(W`iN_ZO)A@W@0Arit<inItDLc%K$NO&jIMc!I0gjXm63)BJ%2qA<d1lWL5sxyLR%9L@c=}c|4wx!NcJ7YU-?>+nbZufqBo$0hYbLRisUrxT<J@>KaoXN!WdJiO9u~$dy%R8l?MUpJbX-%zUYejbcviVur1$`DTSzX6^$av=^xpVx~jEU3hSSzf;lsVZ2S@|gg11W=Z(o%W_QgZV0m*r<Jo|TtBC)@F(Gjj{FZC@}ib4j-SzFXhae!T)ub?+5e8~7hzP3%Jm*E_uaik;CJ`z{P~@^6>!m@K*fisP-c>T*9HUbmtm-iKej7j}HG_;=_1e7JvlrFmbr>r+qv0WmNAgTph{n!o!J$J4&SFZ{ffyyJGf4~lPH_ajq3r(==%yInpmkFTS>)Da&Quj}ldR^it_g4gw<(qHO?Cls1GRh_)!gAX=uQRNvQywxJ+-SNMDa+Tu)g`GXeFFuHu;}IW{{v40^+VRaR{pwf~@T$Lf_w#1lT;{oc?)JD7@7?p2RAuU0c{K&bXa2Q3zQ6bYUiXj88(iVnKZ=+B!Hvyg{z~C_&vk;gqIf=+_U`qD4}4Qz=~pKxUeyurj{n}3`R4eCtt|7LN4&NAqUXGekK*0y<b&Hw%=L4BnrGa^NANNZ;sd|DTjAF~gm=gJ{Xfq&$6tQ^yl0&8VSGaWq=l8f{qb)9FKctm=PmtxS^Rj458|WAvGGjsjHme8hUry)b*x7C*4{ee-8#qrHPehw%@^n5$60)&;h2l@=S6&|QOvvjKZ;B>_4|+UjvGFJcgF!AUjK(mzy49Y+yC<Y;imp?7J0`FAH=)kroDV#eC_Ags{HC$UtIH!oASC&Flo?Lzy7Y5`aAwP!sLig%RHYK9}wTF%F{o(X>yfce`|BhyVrTf*ON@055u1GC_eJd8P9nXANu<l?|JNB5;E_He^%-lPkiu?N#5~P-u=Azu=H1TqQCBN(XW54czK@8O_^(sGq>0?ZsNn@88`7(Mx@HGe-JO@7EK+s(D;w97MtrL{Pl-de7tq9+UvWdtuy0YJ@jV0x7zjDYQ}rOJx~8Yw0OJu`Sc>=gZFMMHSfCyJ?Be&<j7Z^^CdoX^efN#3YK0dF!fWWdd4kUv|zdU`H|V4aT6aF&$zk$+uW-1?T>fw$3gpFHa{=v;eBr4gJqMw*Ev2UzLmF5uzqcoU;i*Z;qU%-uIKZLw^AEc$B&!aAMf55g@4-MH$LL^__+Pm__+Pm_(W^3Z}dAa!DlaT@;&ePg!7Kq=iM52Ym47?tG!&eu2<KsczxZ9Pq=Ptf3?;3e#9r-kNAZ95wGvZ@X4arOh5Jf5wD*=+Pm{oyng<;_0{u7yng<K{*txLjDvcvir3Fo@%p(My*2xFQ&&Cz#p~z4c>Vl$>!|0yRWCDkp7i%4KH>XOdwHJY6TTm%zW#nxUe`(Ze$-y-FX*|$q@F+E6Xp;2g!uzr&mY3mYGQTNJV(5q=ZM$yobZ}c#ip*BzlqoLw*)WOEnd&x-1=(%roB5q?|(B^U(Hv=>-nnNU(HwD{%XD&ozP&H@oK&;UeCA1>-o0$g!%S}yjUHzE)cKR1>*I(Ab5FK%<J_IK4HD1ygQ!wg!K+SVZEcgyWXj&iPcx@JMnsbCtk1b#Ow84IJN$6<MnzIpRnF6{)h2;y)0g@m&NP#vUt5-7O&UK+Pn3Kyt&65ui6I?ulE7OC+q{1-;LE#`y1N3>w3K2-*Ee@{SEPYf5WY#_BTSOy6lY~f9bEi)EBS!Z9<KoFEL*2BZ=4hNN#_<k8~n^pQ)?%uf*&9tLP_(_j#@>$4~U^?j6kid{9YK%W_&{E7{7)jN96Cr1O&W-`bns@4wsHdphm^-P)^fAHxH7Ye_x?w}iWr-+{Zr1IYgH0C+6<JUkYjL4F^e0naDr!Smsz<Pvx(yq<goUJvgfcf)(&W8_caV{kQj5w3=BkUxW+d>_66pP@NiN`3&B!l%if!>8fH<aPKke1NQi55U{WH{tE@267j?0bWV2gIB@}$UJxfoJG!tv*4NJ_u!fEBytQq2_8v44UdG=$S!ai+>>kp_k>f(dT<Kdj;sT>gWHl8+!k(6)`i={-O2iJcepp%67CHTB)h@`;nCy(cr-kP91Bl@L*xuN1ZR`;;cPgUTngvHtI757YIqa52i^o1lgHp<_z+nQAA*mPH()2vz(?V;G>6ZTrSLiU9r85%4t#_>3?G3Hk_X^}@D6f2yaV1yZh$w!tH_n`DtIBe0A2{sA+z8)@GNpBJPV#oPJ$=HqsWo)DEJvN4SojhMfQYy!QIFdxEuT^*$#dbeuQibKLU3k+ru5;9%Og82i%A34flZukptmD@N?v7_&N9matizcoJoe@OgM+khI8OWWG=i2UPG>i*T9>}P4H%TCs_>dgd^l3I0FBKJPJE`79MA}p>`Wjb9e~(Bs>I8B?E9O{5Y8eKMp68jp1bYL9zk-Al!&-1~-D6lWpMU@WW(h_+hvc*$?gnKV`QdIh^bV4~K`*9PUeYhWo-D$u@9DxHZ`fZVfjj8^BHBhGb*7A>4#af}6mt$N=05evEt)ehhws911@H4<^UKPG-Q)HShzwrIUs5HoLuHw;$3R-cO!__roX2O86vPLDs+(@Ky2}d=-9=yac}oUm?%KSKxB;Ew~&$LGFW3z$N6Xa0$GX&+cRq`6^rlucbM>h1>^kf%lSc!F%E3<aziwTt;4k%izo8HTW|8E?EP=3rERHI0|1NPr(=9x5+o)x8Wa?+h8YOgD2Q+gcZA2oa-TMx7TS7KT9r#otz6h`4a5pMA*q7?EIY{+3jV!eb;VN?N&hM!_)2dqTN=|99~XNgO|h0ocif?>L%Cwwtrdp&ns*uU-AFIpnuc59E$(VPwZOm;%H)eedqqRCueod1m|qPdG~KCZy})'

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
