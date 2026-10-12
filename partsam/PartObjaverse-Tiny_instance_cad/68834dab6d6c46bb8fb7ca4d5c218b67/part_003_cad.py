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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/68834dab6d6c46bb8fb7ca4d5c218b67/part_003.stl', 'relative_path': '68834dab6d6c46bb8fb7ca4d5c218b67/part_003.stl', 'source_sha256': 'dd53856dce48897fd2267c2214797389f6d9e5727fd0e676fc5dee0aa131b506', 'input_faces': 100, 'input_vertices': 93, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.22313451766967773, -0.3552725911140442, -0.46081265807151794], [0.3268255889415741, 0.2344847321510315, 0.1552523970603943]]}
GEOMETRY_BASE85 = 'c$}q|dr(x@9mfx#MtsEhN}8C&3qC-3ED;PCWcLCJB0g4>poxyV0W_J>h@iIA(774YnYM`<CMG0dI$Z@#)Ud1y8Yr+ADJs!KlbG7pC~KOGjn!#m9+R<u*n7XfuPr)srjy*6GvCko-rxP5$35rlU3Y%OfH6w0D0Oq>XV=mqm9on)HAZbJE#L4=acM>3vt^ZG>K^#^bxU7aP&nVcEKF@un`25!D~iiw9@AoGu1brE*J4(!E8kG=eRk!#@{&^9&+)FQD7E~Gr@dvRRy}q`a=ey2C0?u2e&{vC?!!CVPX#S8lPkMz)q4~EgnC`&d$uZv_Yby)E`0*u*m<D`akKvcRiE|354|@1IG%G<B3`>Z<u9o3Xgr3vtf(IGC&M?Y&Y6;bHR8>yZ=A>d=eEE%o%2uF>bbfRzAAau4?i&#@#^{)pCZpwrSOgP7p47w?trgU)AvqW(pSUxeARWEe=Cpg`j`tC&-P-!tG_%i*TTQEU0?Or5+8f_?~(tTD&$djZ82T_^xqhK4*s3v^$aQMlsr?BCv@#Rd~<x`F;_qHW=2gv?&@cr^+`A3tJrAd(Jv>$_rzc5arN`Qe2JCsx%zv*)4V6)$6Rbh+@&CVE#*9XJ=cqMVfN<2SE<`ix%yc@z8M+s!#`2;N5oe;J7j)q;j5(Y+R)y`f1Shq^k(r-lptQMx!8*MjHnOLZdd9j=;xB>>g{?cV<CJ`XX{zy`FY?sh<6rCd`}zlXq&g8-H`Kn@q-Bx@BCXe+I4lpH%`1D{al~ZhIm)E#J8>c82zcZ+5pWQdK!L<|0Bc~?`pw#Gn3()U4`hUTAs4Uu4`GD@I!~kBHouZyc6wbc_qH{9QtFv6xfb_WUZI@rX3%`cmGz_U3Rs^Fa7HWn1^l?_qFUA_(pJ!<eBlam+>C5YvHRy4<atK;%lsHeO51gU)!%RF0=e|jLX;+eg^R?{(c(m1&5r${avHs8!g>3-jW*_uc}LeuOEpMKYN9Yt1eIc=DldwC>V-$q3TzPf5-t}d8)8KeDyW(P5&UY=QGQpq59uRyMYSSwO>3MME`czNuDP%&`+&<8}jM955m_D)SZ!WhRMEqEBiyJYYW;ltG>l^=38#~%2f<s@48R&yuA^=sdvi$&3az;^V>DzXO5J8loxjt^}T<V{1et<{CeeOydSmiOZfVPBKV=s4w=t=V?V-k(V6hg*@ft*zCR7VK6%_xJU_1&`F-!yz*qMd96|ov(}-6M`^5iz|31WT*!n)SVLyEBc)YCVMbS;j+t4oYm(md*>Ij#4YUq%5yBt`zM)A@bjHlrwe53Oi)|D~_Ozi8c*H&V`8U>Mfzh=Xy@O{BNi7%N`i~Rm?B))y8>?7x>fcW1@{?{Y0&s2U~7v|f4L;O*Dno(a+(}lW!_{Y%J@3G#DrwXtRO@9=8{oQg|hpuJ#{RsId!B;)$^@z{Q!+h$E4)LFk#5nb}r%$3^jmhwRha)6U{%Z8cXmr8Xns>|kc>E^D>uJo9JY`?Ljyym0%6kv25&y=_2K2XV=PB{m!Vd+iW!@`_@V>M_nZ#d--;4Ow%W%FLffvQ^*t`?<g}s;u{eUUHyQdmDI|1v#bD&H7ZQ+N|4)=TLz!&1bd7~Lx+K%-bIyn9;>dSjx!FrsRfc&9@(c<r!)`IrjRXBe<hvtfZB(WXsE!m2BFq(cXeoHHS)3p%u?`zsB{x6RPpqWvo%ws_O_A5A-)%rp0n1|+f#V_fV-^r{C@*bP7oRxX0#W>B4&W@n_wy&<NJ;9=+fz~gIRU)mgu2tSXpIo+SU$?aXPp)TD{;yB2N0O3$<Tn>Sxx%ax&SLWbY6N)zc@T9Vc@TLp^)B*YawK&K`97=I)ASP-o5xZ|lE;!qQST;?B9EXBC66EvqehY=+3qmvaI&rUkcW{+P)GO4Iht+SdT*aT+{-@N`T+R>j>qQNR#|Q@7wVJbIIB3UGKHE*o<g2XO(0JuPo&0^Cz7M7Q_0cfC~7P@iaee=i9DYC5Oo6iA@YM(8AsKq6UZ9b$zrokokZ5jnbcTvCOMlrm7GnUMU5xVBIi;Q$hqV>)I{<eaz52T&L_{a%0g-q)j@XfJ=r{s8bggEkK_37r#?)6nDu1pBjiV|lFE82y<2SGOQ$|YPABJ3XOeTsi>P_zMdU(i0lAR8tj~B-sME<Q<TUCGavC{<>LO>5=ThgBZCyZ~OLnu^yqLO#Y-<sDG5K*8o0n3bBrhdDVdu;b3m+5lzy9L>_cH7Q?6yC=cRqRhG2QpcO;+_khqgO^pnc9+hhw-}Z|Nob^ilr?Ct`bi'

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
