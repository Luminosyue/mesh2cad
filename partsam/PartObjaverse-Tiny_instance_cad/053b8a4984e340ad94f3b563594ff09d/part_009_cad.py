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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/053b8a4984e340ad94f3b563594ff09d/part_009.stl', 'relative_path': '053b8a4984e340ad94f3b563594ff09d/part_009.stl', 'source_sha256': '31004ceb007dc922c0614c985f51e9a014af449b38a45f8185b91a17088667bf', 'input_faces': 138, 'input_vertices': 123, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08485013246536255, -0.17909736931324005, -0.15215885639190674], [0.05913810431957245, 0.16545656323432922, 0.15326674282550812]]}
GEOMETRY_BASE85 = 'c$}qJ3s4qS6uu}BDVmxHh~$<jKEOo9@X5jtzZoiMN?|FB@RO!I1VgB-)yZ-!Ewwjgn_(&#qZyzG{+srk!Wu1mSTkGASX1WYOih+q-Fxo0w7X+7P5sW9@7wR5J@?#m&)s#&&F&uBpUL0V>^gODM?@rJ!XjCJRvoBZxwI%yHM*>#HiY#dUHoj^I(z=C-24z$&F)Sp4pbFYCQMQirj(>6Bq|9d<&`Td3(E@1D~kg{_ZKd&3UIw@Nnu5RUk^_nJ1$WfHzHA4t^CJd50OL1f##sV&(9r76X-vlF3|j@VZYGTd!yRLwLWkCK|+ttx@8;`*T#v=CV~2cei~;pWgHDUi+Ji0r>@xk=a0OU=FqL<@K4^o|B||$ryc)~3417?$>V8W>$8p9DZWS7Q$n@}9Xi_)M)@eGlj<q{MYnFKFT5CZ>YKlzJhgM3JDmRN>O+*L_H+AAfriIlnVG&L=+M>Sp;R~J*T&s+pC^u)GiGPdsl(qWiQi56PV_elGz;V2pgPQ!bug^=8pyvXiF6}+6|GD2=t|{xSl3514?A&oAK~F)88p82Og)XCy;{~YaoH=h-YrsRzN$@>M{3VkX&zf28A<Ece2vXc-F&B$)@9^A-Ad!o?fx;)SBfXTdG@HBf3rKj`dd-6Q@7(=7w5K8oj1GVTOqPPwFhGBWxu^o>(zWm_R_r2*_n8%mpZyd##`t1XZNq(8+7Pu(_qTmd^c6DYn?leRkniiS3Le|<WDU$|FH|S54yj47v*tlK}(uLS5Ler`{AvH2WZ^(uPvbdw?-~(qxyBa<5+!TD88-RaoC;F2WZ|-Pn<8K+Nh3t-8RCGyrZN~388&A?{n+wcWqP;v*{kvwL=$<Q2cqa57m!qNH=y}B;AY+qw}bK=+UccUZDK^rBZ+VPtvtzU+tsuEUD|K+m1Tpcj+hENmt?~%J^CCIO;WZl&9+P*VZ@Cyk={m)Xl?kUDZ)?y)AB?B^{G-8hu+x-+ksy+UGarc`<iM-D>+?)&aVndD~{Xuj*s+*M54L_Lq5dW^8z#;`pR)_nZE~cG@4^=kZTjLiwp4UCR%&$n%3Z-=m+$W|$N|L+T8D$Q~Lg*O%d**GyS(DCp4D;gPaF8;?`J>FI9W9I&10&(huVYR3ngL5JSu|6~k3hjrDRk1{Ias8jFq@7zfJ$(~xL%X7R>*7<E&XSSsHUdsE}>!j;pYwAcZaqHSMi=Lsl`}4NaxxqeKE4I-57Ieja9u7?k()_P_{7=rH=ZUSe3D%2r|Au<1Gi#Q*`OEKgZjEW%<T{$&@zub$hl38??jLLYO4@g|#iL)@o95A=+jUU0<DQj$>&{1;s#E<<kH3{2QAg|W#8)1>pY}y-b?48{)yjQob^Dt?jG{g<eM9KEY}c8E%lca$-FjNq-xyT0)0q!DiTBR@hv|LT)z7I#^jy`U8}@U1&06_f_xS724W#G4mgn|2Uz^%a`*|{S59!+$(0bT_AL-hJ?mZXE$5OZZP(%N#(9O8Xhe<!Use#bruSCmpVR-zlwHN6<ZhGV6T(D2v`Pk>e)@^?S=R*B0PWm^bY@#@I=R3&nf?GFF?eCy@_YNUloAQOM^Algte(4`h+9T_|nC4S1jCqdyHq^*@?Q`)do^Q~Ncbe;+x&fV?ih01PD-TIs55!O%Y+Z%k_56g+qSIfN{jpZ=<C%lYgO|{aJ*O*Wy`^s6Q?SG7@6~O8wcpoLFa4VOOdZ-w_BC|<)E~0X9*u3J`SPbX5w@4sP~5T}tAdx%wQC={o9>5hGE4q{5B^@A{BvDj5#d>rK0P1Kn6S(FS42sn;}b%N;%DQfKOvTm|977d<5K_cCqxy`p_JPS;BxSp+;X@r1TF%fLQ7<9Do_QV3O*B<1AaZXDBKr?djy}zZ8En>z`@{ma9ifU0`Ob8-Nx-kU^cjqTNbyQfO+7x+{(GF0+xa2V0;m9DY(dM2y!2SxGKzt`+T@32RTne-U1cyO4M*AuoPV6yaag*oCTiFErVMc@EUO8qrp$$Z19`8&F6MIFaVy*Z4TniL9BF)37-;RF?cn%#oX=$YTz2K3xP%8qJ|aFDxfdM+S9Q9G~_S1pIavK%|xz(*I+O10+xf%!WyRm)4;`ET#MQZ%yR5Q9`-K}YZ81qw^VL705iZBAn$x&06YtE{lHA{V)&E;E5Hk}_FUi`@VVf(0E@tHKn`<(bHHa{uIa#3@O;cS4>%uu9{3DkCipFwYXPtV{3>qUxFx~_7muh3xE{wXnOi?@V}VzKj|EQwhHx7N6MP`IF}O}aOc8rLtUqEWgNxXsanBXNf#4#K>yWR&zTiW-#c&%2j0GPCo&X#OK7w03x8cA+;38%c;tISBJQ-u-!IN;EjP)l0M}zm_CLY<nfnnf%5wj049Q-Pb#RL0*_v9AJ#EU^<ckteb*%KHFJ_uuRz@Ff}u>MG34EPnONiSe5_+=Oi2lfINe?yAq76BXp9*LMefYIP#7z+jV03V4pj{wGli+&M3#DM+4bF)Lb_3!>qe|r1-r;7ltKg4<ObiZz$clvptu9t6ab{M^KyYYYG1y@U1{RR6#V8;'

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
