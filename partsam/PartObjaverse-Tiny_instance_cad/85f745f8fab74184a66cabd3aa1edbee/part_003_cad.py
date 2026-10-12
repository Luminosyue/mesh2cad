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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/85f745f8fab74184a66cabd3aa1edbee/part_003.stl', 'relative_path': '85f745f8fab74184a66cabd3aa1edbee/part_003.stl', 'source_sha256': 'b23b80cb46ca93b81e1483e7c53c9c0dc65a3574a1a7a9557c6e063989735a95', 'input_faces': 78, 'input_vertices': 64, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1727108359336853, -0.44095176458358765, -0.06921051442623138], [-0.024653486907482147, -0.25007688999176025, 0.06166338175535202]]}
GEOMETRY_BASE85 = 'c$}qHYfx2H7~Pk*h&&WfyDA4lE*K~(ae0WHX&jQl2S0R*G4ldm9wI(2jMk`e`4J<fL?#*-bp$B{6e+cMC<j5EF?)b7N}XXQEvHGQa;(N4)81=;<h?~RO`SVy);jBa``h37_CDv_jC5DGKqik+Hgd9Mr`>}w0Us8~wpeW?1v%E@*&8;!U||06#WBjSFI%}ZBh$dPux+Nb*5VwSDM>Lc$W1UsE2i9ywh~*`hBX^)Ypudh&01e<<$iH~)+Q@IkBpCtR^~@VD?60`dU%Uca*XGC1gq)S1hX0U3c-_3oE5CHTUP~JejloNLhwtArJq+N{pK%^;k@XFe!+V1z-7Uj&+q{e&qi9{+dDjl1S_rCZwP<5t^&T=)Pi_r?wWR-@6Cj-g_a_o9X<XG{IV38=Sjn7VE0|s;1F9M;vTfi{M$c5er@~68ThLve-38%48m7a?!vd<iMxWlCr$65&hjs$f2mX6*J>Z!uj=0qUmZ-vy!v-ht%#d?48DGK0etoAv`WNh*U5R4UmV2ss_{n=UswTOtIr$&$Ht(3<z$SUci(Y2Z>NraDh&bB?=mBgwl$;<b>9D`7k;^h`t`w?hp{dzrLRVJ%XKWeDf8_AO8UFH;4764=#O6Zsmyb8E$Xq?E;@wk5$B{|YJtyoUU>>!S|$BSOy>77uE)7ch0NdT2VcMOego=#c`JOqw-4*0o8R7sxb!VfzS4I0Ao8s*fv+T<!hH>2NUg;>DvPDhjEGm00vhFg&XIY_nh|fgZhH&;pKwP<zMulEyEgSa_MyFG2)@3gANx)1Sc?6o?H_=zO|YQ<_FwKdqd(8>fUh1pa|yi813s%+B=i4v`?B13d7DvRsaeMR^veBqcu79;6e#fR<|Bx=Ja4VXb(fnx;En>!tNy&X0rl55!B@SrW&Xy#R^<69AHF`Z$ay~`51mH8%B!8$OJN_wSHllDt*`FZ2cIRLciNxBMeE>O0_x>@o&TWS(Pz!C!ncg}(=SZ=n!oI)*K*WvFYP>q`A*lM5B6ov2Ybfw_2qkZfG^g;XT~<?=i)VQ8SnJ~^A2D1e;4Q1e(grQ`zxs5(q-6->uFW+m8?(XbMf?^Hc`)TKw%g1h8>a5FFmK0H&?*dzwMCk6MC+-X%{--cV9yu`wHJC?8EBz58+pykk324e=L!a@4>&7cO7*+yIQ`Nf(lz5eRbceCP!Z*-+tlytyo8ovn`0<op1x!NAnDXH#z!@{iu!QtHpI?IB&eIjTzs!u;y>|WH^1j(rR|QN4ha4Fpht{a<d#hUBVQ{D3AT=Dv0}6pDuI4|Ne9(@fuP%5{Q#YCy-9$SjZuIyMQ>6bRxwF?ZXko;mHxqF@eL6*psv;#R&a4M-+{VB46k@(Hjmk`64cs*i70?F|m|Cn8pQ@KdJ-hT(F6>$T^GV3nJ}H975Wcv^$3ju|IJL={X#;IUXTQCGRngNgQ*Dr;#4dVc-ZPb|Wp=i*z*c3}P?R2HIM*WtazPH_~3j;~d5aew26|>6skUIpPUI#}FGy8>v@9D;yJP+)UEbiM>e+b|vjf<At8j5kWZ=(h~_0G){0R=}=lHZ(>){@l?xvLJW<IARS6<B5k7aLeJv};|QlU6KgkxIGpqp(vyk9NRKBr5{Hovqr67KJoa#J363S6M>>{t6hY`&#NnjFsis-f=XmN_Jl(U<8R-U>K-Yizi~R7gW3xE^VgBn#=hu_t$kRO6pD(M7ba(u_cHzIxVxZ^<`vai`jr9'

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
