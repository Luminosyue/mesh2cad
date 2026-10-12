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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/68834dab6d6c46bb8fb7ca4d5c218b67/part_005.stl', 'relative_path': '68834dab6d6c46bb8fb7ca4d5c218b67/part_005.stl', 'source_sha256': 'df783785aa37f66c4eead44916e309810bdeb0bffdb57ca4a6ed5a1033340541', 'input_faces': 120, 'input_vertices': 111, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[2.3558735847473145e-05, -0.45385032892227173, -0.16770410537719727], [0.35758915543556213, 0.45629990100860596, 0.4999998211860657]]}
GEOMETRY_BASE85 = 'c$}q}3se;68HNYMnuu0|hzUkrwFV8uyPyPRQEtl$;spUqbP;yd0E&nbYnx0OPbA)IlNt|g8n+cqL{M2!?lOp%dP4<?;w@Wia*~=`r8knG-Fd&)1asPRdXn+{zR$e-&G&!*H~-GgA>Q20!&{MKsIufli}j<PilUERinp@Hnv=UM&AMvz^6a&4N?-W;@j%~*ONfn6c2m|U>-^HKtI~4(f(?Elw#j}020z=1oZOt$<%?G2q+4}AGBtCR)#a~Rnwo8OosS$hZd`z2!l(elFAU%FkSfamJ<avM@s{U}dY3x?QFtS?i*Gp}aRvTYgWvD!8;)hR>b~**{fB&GL-{4$*E)AS<g4!0*Y$HtbhD$rtM4&U=9_Cf1pi_|seZ1xZA82?>TSeptql(ST<z8Y-#8~2@mjm78vdWJUDwYo?SIGT_Iusykf+H9^{XA5Z%REj@wKg})AF?ubviv9M{r%E3G1?Su7j_6B{t&o8=qf8eIM>@gWs<NzE-=nMfdHWHC;np-WTC3Uv9n%{n_mU$k%_sF~pztxr~0^>5q7)&pP<(R~?9VMlQs9jRQ8ox6}utPQ&MaL%d<A+ev8K;j75g(ybMF{i^<i`Hz>Oezk4wd&oQT1Nhou&t~-Nddy|i6;OW)pI24GH{6&HUmMeS8g;a!wPC%DO&1U!9CZ%ypZH5$qW3#kS8y79rG60VR8G8n5ph$8HX-gn<OQtf<Q4eFss7@Bx)FKQWrh1tm$4nb>gYtg{p2SSU$_SItFe!r#kw;7g8I}w_uy-@hn_?IOMAoD_W0sDW$gB2@U1gsoqL<5t}(0OYpGf2i=pT<@qPDHpibKs#2bs+;cE$fny{|CgRe>aza;;>-I!OI>|BlOioTXSvo@hlZAC~4>Me3>mOA|ruiCEsPW;~RmDu;s;QEBSvY(5*#Wyb!Kl5gd_`dLsraPx`-$S3%phX6WkFvryn5vE<|GqehZ%b;H{#9;Ay~WEUzBz3V`n==@*6S?ZDgMCy=!0`{1^QztIVJU9Es;FA`8!ch$$N4>d}RajM(l;!_xEc-p3IINxZb)5`L+E6#cy7Rd6o1&(&vLO!dJW7u<s3F2e2;f;0}rZb#oc=EcpEi#FritzvUI=vCIg=yvEW7@zYOj$9-D71@)_?P2$&>?dZ#NH^i%@7vLKcH^}{s>#It9i^L~<EcZ8j<QrI5>7^FAkNxC6W_T2f-zxPdd!9$%UVQv*#Fbu_{Bfb!4@&Ys4`W@WS0(?<0^DD9^{^wjuJoqlH}!#UiM%g;b$l#-)F#|tb#|NVYsaUOXJX#Au6?sOI;Eb}A)4%$h@()4`z7Q_9&ldj+4f8EJ>V-TrSR?H>+M~AV`3iqqlV?bjy^lOOT4yXA?lv?1n2D``R5i$-!i<>AJyS0dEy(;2jhbA72@}n_}Br`pS)Mm2fL#$eAWCb+5b_YN5%J%Jf?Q^L7A6#9P>MdNIm(EP0-a|$YUuB6MySHhpgkwacEgI{e&}^XJvLi>L@Ric}IMJzFT51HX?udI}%?XQxA>IYCznfCaHf!C*rkPX>wl<w@aRlFX4HltarYE{d?F0&uPW~NR52I0^Y?wt?(Crw5=A`XU!}^d_^RD)$?i@@@KAxuU5>I_+B@~H?^TZO63~*AHsK<Gf=;wa;@a)HMku8%-vj!x+{Mp@wSt1Auh5*z894{#BXcI^WC_*81aUxa`B_LZjkSLne?gZEaQj2i+O)uyC3yeofAK)M*;FjXGxvaABnG2+7Le@RrY!H9q|K$u%GQ&x3ONOx?TLS%U?mBs8O;Xs{7#gO|j%)A8W?#^4zHQ6<?{Fgt&;y@?5GOCVtBPt(bSsZLCYF2^9Z@yVwWDIdAO}KS=!aDQ}{Gd2eE08EeADSI0~I^bUCr*JO#`l>SH5lYXlT>#AKLe!kZhU7bncyK!EdEq-=#0piyN)=T_K@y{0j0lq1Eo38fS9peAhV=wB7iNSsTuCL6`ehu~1?iT;<=6%qFTs$ugbtU3AKe<c3mzA%FcJ;4>6vDUqR%1WZT@wF`W4Iqq^KZ+<Z>3)=_sRUltEi{$miS+$lzcO9{6lZaPq$AhH~h#orE5IudP}yYc6mkCP5pSF|NRwt*~I_v6?y#FANq>y<Er6t*YKkDBYTm1QTvd4ksqNxN`8d=;LzEP>Pgnso$Su@ZX7!6@9Q3}p|_?xht55yKPLAe_oWUX_a*yMN0EKW0n`|B06C62jT}dwNgYR?Nj6bOlTG9a)ThZ4$YZDm@))u|buihVJcRlrc?fwB^$GGI@<6ILc_6tzwKusx`7vrwa!>YO=aH`A=Ncg#IzLN&iu^1&m^y+SOrAm=PM$&zqW**&L=L15BL|WvxyEGbQ0g#p2<wRA&^eMCOpYW+P^XY1$l=r=ayWSgHIO`m97df)4kL$lsWp^pB+qh<*{%`Kq4PZIeDXYU67{F#B=RDvg}jKIPPLKK$<I@llAkAMQJ0ak$jhlq$jix@)HHG?IfI%?&LCT<&ylU<#nc7l#pH$5MDjv%3N?Y8LQba6At#gPQqAPK<XA=ahOQx0v-0iU)_Ej{&d*Tike?xs<<NONHG!PKTE}zfJds1^sniAJ1?<IC4xOiS=p0Q=CC8iH+`YT~uRp<jd#L(D^`Sq=eD}(Sf0nvl`IPI+|ILq7ytzAmn%rIgR=V_M{i&e*2b47mw*'

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
