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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5fad3a288517425e96b5cc4a86ebfb46/part_001.stl', 'relative_path': '5fad3a288517425e96b5cc4a86ebfb46/part_001.stl', 'source_sha256': 'da3e9b5b853782fc987022f290d2cd48f4f48c510604a8e8e1f8dd3e3f5f0155', 'input_faces': 156, 'input_vertices': 172, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-1.1137843132019043, -0.6821063160896301, -1.2620370388031006], [1.1137841939926147, 0.45515087246894836, 0.4465922713279724]]}
GEOMETRY_BASE85 = 'c$}qKdvF%j72gm-iqa$)lnA!2s7=5C1p-<d$*M>NMDqYF;q|4E00|8tK@bzk28$B4LFFwNRvw9we`;&2ErqOvnt`P7C5olw(GRAU(GjLpP}|Pfo^$T+e%)`A&UD(3`El<4?%8wCJ@<JwnKPpM4>8p5He+mT{FhFGVK4?6LyR@~rK^`O&MzBNT(U08ND!WXT5frC_RP$=QN|jhJb6ie+2YdVd(GtZf_suv&E$fWrK?NxiWjXcU6RlI)VvjC`NWqk%PYyJ=ag}Gk54rxj7&A3Hvh-pb>xB_-*Kghq<cE?g2=CpKV-0P&$bG0Juyo7K=8h^!av#k7vb+Z@-a(e;6t6v+n0YMyc7IDc>7${Ip#y3&HY5|&QCrovT3o{57lM}Z&hp%-c0EHz1TmReo^csKJ`bbKT$9Cjgk?<TNBPGe%P&I-yC;ax7Z!s;));BzW7}H0&k6Nahp86we;~Wuf98T+*L1c9LqiCwG%2(yxp98tf>!P+t+r?gl!)Q|JTAM(LcUZ`fJ@>DSRl;J|cYQS>Xd2*}?}d?@@kUUng-0wT&0vm{L<XS<M#vsE2pIdaYRav;~dg@A*50x9v}*-O#1UV#j>*mNQ~Mr{r*x$ByPhvq}zUc=*82b2~);V(ux?Kh>qi_xw=dt@#g}miBM_RE^`sf3%C8kMl&|`s~3j(J#Lyy!%|zNpHKFx2uy*dfT;rwoiEH>UOd3eBGezr_?Hb#lAAcp@j9_!uNvGUeEiD86MsNZ*;xi*yQ2u9aU}OPt-fd`{M2BcaD4Q1U4zZwZCEetIU?Z#@zs~=amCK(EZ|X`<jPtm*V~N*6FAGb9Pp>dE;Y)H{h>S@P9|wEB%5$t&@12?v%JWZH>*+?%(&Ul6Eg#`bgS2hIw47{MGGh-k^2h^~VJ7Vtx2|?zdOp8iRhqet3O>w|Z2+{rb9Hzdo<;i1j#H@gb~lKd=4NcEUWxyDvN1|FAyRi9_oH@!urlo~?Kb>qgH9vs=wGtLVL;cf3r@KU>d7jF;Kj@V3~W(<<#dUv8CtTVD<Rg*@jat9TErmvMB{9u|AX@30?CRO{VwMyhtszO4Ky+ILj+n|4=5=)+HA{E79l&W4@)K=|%P+2`Ct3oB&4FRfDZJotID__Jx$TIn~|pZ4E5bLxK4C;QUh3CbTgE+;L5N8GHQ)X}_d10!qOz3~Yhic4qS$@-O==ciS>#`Myu%)8{LJa;KS?O&b=$ogMa)$Y|dceroKb5T~S#2dV|OY!E4tkw(<Z%~}&8F99PYQ4DU8r~LOj|<j|^VohB@4<CJZ+zS=#alPj1ta|FQu|S_aqm{Vf1ZSb)$hu>U2wj`J1$O#;sXoMcX;DqE^PR<Ja2#IL+`lTixeLqUh0>F&sO_;c;4#y<LC9hnxpve{Kxo){5-}tFb3x+)?Ikt1K(?Xf%oqNn)k1FV=VSZ>?hj3=KcGIbJqo>e>J_uJ0CP}ev#hdoevJqd;k8X`Cj{5Gwuhz{ZsS){gd}$dA_XnVHfM2_ibsvSnb=!b!xqv6SoR)Cgikv{nxxZIH%3)Kc5TozVBRc!28b;K99tX|Gw0tc>g)&=<)O2mo)FcFS%D$d`*gXg#XtRA4tXc==d+3qwH732fg#(1s~WDAB>p)S@TZF^OUl7@BFvG+r)e4KcC~m`_A!Ryj~aJjf!jS-ubV2Q}dYrW|7)o9NLE>`U~EERqaEX4<umx(zYJ=>bu}wjB|K=cc}5}>)s;uzI%(CsrFMR{%<9dJ$6D>Dvl<_RoX>7HE%Cc@zy-=ck-OMzcFGRfwywh{uky8v9I~=T`qY4J<ZVLl#TH$RO4lWcQfamX!7v(Qnl|pleR?mD@C0v{`;Xx_ep6N_emG`Z60rF5BIz9{TX~;_f@f@@2ft2|2>xP!@}b}Y+hFPaEtEGVt<~xKRd_^_`WUtpK;$Fg!}&jweLIa)$c}(7kKkSbv|g`!g*;H>{Rj5`rB|G(D~qvr{>)N&J!Jf?C*W$3u@fKBMzGP=MkDWW`o!IbYBtuIi~oj+jS^^k^WSw{3U=qg7Y1<-h1ak;=ex+qI^pDOUS2?zi|E~?I8bhkzWKTUz7K)sC+GiyvEk&ivK>3^QqT93Esc2hE|TaDE%0Zywyeidn8?W8+mRB`7h_iBFj}?Y@Ag2FXz#suk&c+zX8g-MI!HZ|Eco#(As9<4dm&8c9p+}Hnv_7xmxA*A>{9Y_>L=TJ*)2kb|>ZUnGs(%-l{mfCKyXMAi_Xnh*6N|`Lw|#|FrD;)5h|&|L)Vq#7Y0}r;XRihy8?ogd(11gcXF>A%9GmOPEObE>9nnnOi_uOvodQ<`6=MF^({g@I%4`!WhDMl$o1P_z}mGkV+T@9mZHfE@1@Wn*{#;G6-enZYSJHxWnK88^$-Fb35eqga*PP!kZ|we1mX+a1h)9$Tz^%<DG+$4dCkVem&$Na0l>i9VFK+AxtM!qs($Qp_Z^2@6<x_d->4YjWWx<1P6L`DA%F=8PMB{GRqpmOVF!FxgPzP4!s(bYv9vn=p97)AbhI!*sF%z3{Lx11Njm--M_t%4mjP;Zb+_+B19AVq0Ewh{RuJP`a>GvV)0H4WE8jocs~|08eD(8I{=dF?j@uU;!$RqM7W6%hj(s*<oCW0y(E-b4krwS-T;&bp#7218;&x|L_z}eVo{DoKT@EVh;kx)ii2JZ$}#XM-eWHwG7g;fD-kjQobKOn$f4kLJ4ujSw~X)tVKrep;Wfez!efL736B#VMg45Ta&T)2_k)`Z{-=beft`e(5H_K_hwuy}w^IT60&LA8tbq-dFQSfpc^>Vvd;)E<oQ1YorlTExZx`Cxh5kH1$Uz${rxLP&9}s4ut_*Fn&MG{!&Qd&c-A1&r5u6RMPC44-x@`d0y#jFk2KdBvuR?A?c?;^FgU(j;pX*-6GwW30`FU{9LRO+&37w}9C+12aOHgK=0zA(GmkltN39!y1h%eXO2XI{m!1b1)<_pJ>=f^a}_94O|#CRIY<%rix^p~I4qr8srBx1l^G5W&XLiDK^<wxM(!)TwMlL<EyZYA*1d;?)H;U4%mh44Ltk87p-9l|8k^L)M=^}|qS5^jY27U32=bNSn_&0OY;sD4AD|I?p3{{6FMgY*93!~bUFHNyL557`P|Dl%up$UfJP{_#ZogjcokFIxUSlK'

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
