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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2f7852f6833d4eb69ee3f6ef5fac5738/part_012.stl', 'relative_path': '2f7852f6833d4eb69ee3f6ef5fac5738/part_012.stl', 'source_sha256': '8d8f32418ce1628bc799c36dabe7351eba389240633b53444f99c372d191f59e', 'input_faces': 78, 'input_vertices': 80, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.21225076913833618, -0.11446139216423035, -0.10622555017471313], [0.11149003356695175, 0.2969643473625183, 0.10070529580116272]]}
GEOMETRY_BASE85 = 'c$}q|Z%h<N7{=!S=>Zlko`SX2>rw9xI1!G&QvRG2sE8o6X^F-L5RMkx3LHq&SknDa8)HsOYGOobJhdrS6c7+F2%INsDYWz;4GE2iAB;3<KQxUgB`tR5-S^hn%{6J-O`bf@{BCA;c4l{WuQ1QoPea7x1yX)<`Y}<{NVS}3NQ2c@UsZ0ci{4-Jfr_jI4hQ=2g4gp4cd1ANIcTV`)|J}~DOy8nWwODfHB?sH>TPBFOR8-ZR>pJ6-mSAzUiWrcjg^*-$uTBvT!cy6sQs@;ARU6Bjv5<gUVY^24C)rYxn}V3E4P5_awd3A?76^6?&vKj|NNkfxziOT@{t*lZ;f_9``NoL@aU%RfQK%ffbv4U$j?uI%ec_z-vhrdzvF~{?%(?!%I4Zbtn6GG1a3)O1U~mLy@Pq_uLp;qe%90tew?MVKV1i2(bNt7r1l>h_QHinX&tiqBOwD`>m&EnC$9|;0MA@M#-CTXsqTmC8cA}?`0<%OsQ-A>ExWES=6k{Id))kWStc8Mpr0YrB-H<L_7p2SimE%Ip94CPx3?db@vu>mtBoH+`_qw~{PjA6tgv1Z$LsQNVn$vi*0+pR0JkipUEsMhr~e!)YqODi=J{-&oO|XIx$|<0$aTg}#vT3>S2B3M=glEj*1G=yKDRdsxKNxw2){SS!n}Jp(b+FR|9=j(@m%;O#RcOoD(>a`Av1Sjy@bg-*JM27H{f#%J^eD?x(J+Da{GAh)Gf-^OX4kQ;{3aAf6kA`GPPT_UJ~D3GRfZ$Qa=r<DcL&O4GwSXBJr!@JbSpaMDOsn?h;q5`&`G`Gv4kii7W0avTOcRaCfcvTo*Kp&o6QzbQtyxK^J)y{LuJO{(cs+G%e7+_Y|DRa=2DDpCo3(hw%G5?}^XRQcOF~EfLcqf4Fc`#)CD`zoYe4SwGJ4M)AB`QcnYK`rQWo8)s$DBZ;pqf^qJ3!T7bV6EJ>ayp-ehxgN~5!|#fHfV^S;47@F2LTn!_&cnVAk>ffNeK+hg632Cv=3z&t$QApTl1uxNhb#6mC70?OL&Wha_D}Lj*BL1HybsqajIHkCxnR5R=I2xRL46Lqt@s8%e&HiKaOJ*D_FV?9+~+MTAAAXA&vT7jm|4*Z{bknO=KFD8eCsRViuZ^!GpG&9iuVq=x8@R*XO4}@p5L(kPVu}M(7)&X<%s<SxUlYk?0x45KMDI2v0jtCAGIL^aDL&hN8K>)`STZ<m$n?a4)tropWG*fvag5iK2^HWkFE$+0R4KXEaN^M7=-0Q_x|Zn75}e39g>p&_ou^Z!ai{b(V$okL=VCoh&cd#E#?5sVJMbU(bF-fVopQPz?_CT0>yG9yS=HB*}S4y&O@=Bi()wm#qu`v9hjN##LPS&^ES+$w)xm!KGyT}zZ1{tL-jP(G8D_fD3<+DEc>EZR-^l1W?aS9S8@HQxc*hx#s@P&_r<(|%Ae{fDg)ITs%NPZs5Vl?pt6u9V9v(2tR4M;C7Y?jsZ8j4%u(nsqU$k-pszyLW7cE)RVbF9p^Br5rb<MyyamPb2ErZ{(Kn$-W8Q>07CjC#^LWg$n9Vq5Gmh7c+=Pn9Yu$`F6Fm-dCg!c^iI|_GdY-BP#c~dc<rEalp*W{HT!W36W6-tSnlRsvuEo3^^D9&@QN2uMq*{l*o~kfU<)iWar@tsq4gqc&{tt_?rF?thTc*>#q|K@@ZyCGK=#A(@YN?-vv-}Mxj<rS'

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
