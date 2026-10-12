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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/25a32b2b119948c3b905a21db1098f45/part_004.stl', 'relative_path': '25a32b2b119948c3b905a21db1098f45/part_004.stl', 'source_sha256': 'cb029294838e2ccffdd5cca432fe8032207318126d47a90673a3d15b6bf31c33', 'input_faces': 87, 'input_vertices': 64, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.20842671394348145, -0.40163350105285645, 0.4637065529823303], [0.23323461413383484, -0.3739069998264313, 0.48883873224258423]]}
GEOMETRY_BASE85 = 'c$}qH4NO&K82<PXL`6_9KUV|~AY2gQM+n3p?zK58{<_qfX(^YVOa38rA<UV1rp~Pz(}r`UX_vOt{28>!u}r+xCPbG;=0ro}rnM59q#MrJkDc#*UhCXeTdTvqz0do6AJ2WC_dDM?$6Dm)ZxFa*#gTnqRH*?%$T3A2M3ddoxTeb9khY<IlaB}`US9WOOX-s(*5y8;No+P%+Z(DJrUi;=QO$f)s$#0Cb2K_CHk8*ns_l|5s94`%*Z79j74>#4Ps+(oRkD&(l`YDDy(Y;TK0MKD)`IQ*&n}*k`Stc8%D1)=?=co$lDzWNfh&}Mdy0557)HFUa)fwGXfN^Vz!Ss^%M$P>M~QbOoh5yjFbtE<p`XFGJWsr3)d~7t^&{WUDVAoEj-_Xec=2!m`0dkZy<$F3`ob@rc#o|PIxQij?~KeL-u7}5@y_7^(($ZbNW3%R#sJmdy$w1+1>lcX)9<?M$5H?CBIq1SLp{xRym;60QPTI6o+f=~ObK*u-6nn2odEq2JL)W~L*FvWh_}5`5B+IZ(Erpps^9h2M&gzA$>^JLh}J9Xc0=d2J;d9->BN5RJxILxq?q)bo%e`WirZ0V%}(eH&KlP9%C!LW^X*qr&&Dp)KfDy{w_ZixF84ym8Hze<Gibef>r1R}-;BOBoFd-!&;ayz6%g;)G7<Yy`yKI?z5w*o+=sqBas&03?F651L!VcTqd&XM7xnj>?YDc-zdMfo&C7(ZwefD!i)%xjW8Jua#uJGbJyqz>*{Rr<{&eDP0nyMIc^&#LGx6$U2l2btQ?M_#LgGC~SE4`7H&Op+iCcfaSw2{d{c0*B-ttBZd|m2>erq|_uP7&8y@qq4E?J8@mmR>l`*<Dt;I4(vSJB{0F5|qM+d;hY!ZOtV_+47>bnF6uBn0cX<&(ZGsTDe-o6v_EBhGctF}MDlieE3l*Gs3NGnNfscMhYTx<0J0J`P_U{kR{_oP)ln6ZIGt;JoiR4`1&!qM!Q(`m=A)t>0he(_-{z#Dn!KJ5c|djkvGcu6ot4w8oIW5I<nwZ)f58)BipCQ()*Ly_>sne=doG&R!$&&ZrdBANT067eDHN-~EBum*N!SU1>vJ=fb(gO1xTWC0>m`312Z!<9A<dhA*FB^yk_$(EkO`RdMVmoZqZU;uYfs=yxo|dD;Ff@fKwT`Zjq5`meszr@#Nz#XsUcpZqTBnX?=F7&8ODTE7NA_b{GUUEx>ER<F00J1|e|@fS3Lw6|AHh3?fQNqOCmfB))Qll`w=UGsDQ_p58VRzt8hCU6vtB_E`XaK;ljk6>;p#~{XGJU5BsRK{T(1GOPrByEQ>o~X-xg?!Zm`|ENaxfP6kIS*mZkE0Lc5RUSzU<OC&X(oG!VH~W>rH44i({;J@5YISVmrFki;|N_oO&hZqhjE_7K4W=EZ_$hmx?FlQG7i<{(px0sDY{(xjAA@lmxr+L+3eHALwZYLJX4oTZ|RI<bh-4F!8lHrOK+)+<2g^$Mh<(*Vb8J5OFzksV>wS?&d4#E@f@Cu<Y;7^$a7H~BN@--x!D|}7-#XEiQ{a>xjdJ`(Zo29=h8W*FkZxS8649YFXA4|XPm+LLT%);*L?1U#1HaZGRHK=^LQ?SV>07;?DGM}37ls#m&kDr<4pFM%{Wn)OP>pPNN<Z7XK`+3E{|g_V{4I*ufgx1KF9yORC(~cKF<I8pWcr`{eO08T7Ntktwj^)OWs%edrphZ@~#%Y1Ne7+wg'

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
