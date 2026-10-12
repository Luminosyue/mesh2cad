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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/25a32b2b119948c3b905a21db1098f45/part_003.stl', 'relative_path': '25a32b2b119948c3b905a21db1098f45/part_003.stl', 'source_sha256': '607bf2108a2f94eb5d2d8bf578d459ddf37d96d604316a029e72f4628cce603a', 'input_faces': 88, 'input_vertices': 63, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.22501936554908752, -0.4079030454158783, 0.46754395961761475], [0.248854398727417, -0.3799062967300415, 0.48981162905693054]]}
GEOMETRY_BASE85 = 'c$}qHX>3$g6n<T3r7dOJPS@%3XlbYI423eKl(LOM8?`P2t!#=;cff|yY14!NIw%r_5K&SM5y=o!!61+-F&Gf15e+CU{7}^Dv=bz1p<xLXL`vd&=lj4JqlwWsxjEnc&Y5%1ckX?QqcSYqsNkBQn2llAmPaUxK4KK3($U~*Us2c4R<vsMnh?bxynfxW+aG=W5yz4cr9)Y3u5W0obD7Ik^Q^`)vsE=Wwz%3|HLIR(an(2Id__%jTZ6{8Ew5SKpw073ZC2G*U{%+v|MiN}O0c)|o|>y!Z~c4UeWK3~of**Q&I^9wm1T#7S9i7x?>%@<c>BdQ;CE*Z>T`F6u~+_gb(`?sd$SS$daCdqlLh&+9~=zgFS@=J{>@0??Y{ek_s4%O@t%|4NFL96hw$!Nhs3*cJ``S^w*c$r_hQ}dwcs<K0Kaal#H%6Wgm?e=B-R~$NaB@!S9}s@s|Ej5r||9_d4qwxntE39cn{qtyyt}`;qB^D;hoV-(KqAs!YloIC69Aa0qS453-wn&09|SGq1WAo{J;MSU9*R!9wqu+#82ENypoxKdTt#?op1Z0H`NDSmB*m>>`&-(mK*hSe}Q^V)CuqRU6=gc-Tla4xJUB)k0qgRO+SEt<9+0huwZ|!1HyX`H%q+dQ?JA;uU){pT|GDt=d7q_(J<;P8A1Q|KMcL+E~B3AcJy;!y~NvhrSwUj&tj3M>YCK){~$|v?}8@Ozj7hYPgt(-?u|;n<T<|qc~0gb{^lt9FgSpEMoN%>`#S7z<t<+z@1J`B`<P@xoi9Fy_^R)bXY*v}HB^B=a~l0QFbVznx>|Vqksh4quQE{2mPX+{S6{|H9zB8cU};5s<g4gU&oj7RuDFC(YzbKRHqS}(Cg^R;$NBNzkorBvFQJ}9lk`CeMIZbXuON>jRe1L(&WZEq9eqLP+;Cg+sIIpVKYtVY9KQs*YWJf*nIl+tPZ8?edIY@Mhx5>=;(RVYj{f&u!akm|3a>o-CHNvA_MOiM&yFGFxx5#Bi0MQ9LzmE>@OijTH{J9F@^|+ut`+CDd<43#+i>4?Rm-~m<2SHw%)ubN?ylt15^vmtK2KSU`r~E_@85V6_r=ge<li|*c=!2Bs6RFb`;xpsc%^e$P@U@HCgJUKdQs;`Z8#4ZD}?u+Ie~M+=dJy>R@C#{!l3${)m@1HI0^lXL_N->M^Wcy1J<=>qt6}vsB_jZ>OAWjnCl37OGW+Cxy2K%Ev1dI+FPozCg2sNllpbX{{1UzMajQ<MU|EP?^jfsRzspT#?g)?PS%F*i=-V#97o?6+DPJ5y?2WKT851y9#3C5Z47ZVeWA4B#1Zr<w4ucJXd_G;vBV*q8_7k{h7p_SGtfp6o2WB~*uZ%%xis2D;)(Pn)20#UX=4&KO`>KUr_(o{HkCM?dXk98a~@AFf;O5sMH>m!lt9fo&Z5sq8%u1a&qQk^o=jg3t%-OleYvzb#8atx3UO}0T%}f<Hl|bGbaFbj(3eh|M{J?CY~u8QxvoExIEnKNatXBY#1rUCp-mtzq%Vs$g}9hLGi?@eF*TPGn>n9BZYu3$;u+LmPQB&STuxrcGqo|Bx@R*^$J6Mu(AtQnQF9ToC19>=E+Ee4JfB<!Z6<L(t**O78&+zyk}D)%NUdemHjB8J^Eu>Z(3TQADnmkzVgK|A{^#Y^Z^)nz^1uEw_^}xH&v&$3cOR0D$}#fw9;*FXHM>Ec27drS%zAA'

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
