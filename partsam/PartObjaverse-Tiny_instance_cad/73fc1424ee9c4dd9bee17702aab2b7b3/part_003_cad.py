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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/73fc1424ee9c4dd9bee17702aab2b7b3/part_003.stl', 'relative_path': '73fc1424ee9c4dd9bee17702aab2b7b3/part_003.stl', 'source_sha256': '3d6862da30ac7af8b3f075a16f233a7ac2b860569c45023595f77a4b0e53bd6c', 'input_faces': 130, 'input_vertices': 85, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17489151656627655, -0.22391317784786224, -0.31791356205940247], [0.16083389520645142, 0.1456649899482727, 0.03336431086063385]]}
GEOMETRY_BASE85 = 'c$}q|3s6*57{@Q*0}zvlOv$#3k6px75X6MQy`m_#i7P%UMi+8Pnyi4#im0n*T2|U<N{+}{nOZ3-WJai0qEZVX$6ji+y)2C$Rx`b=d;aIYd1-8>sb#+T|L%9b``zz6?l~8aJFHWzB7gD9!r!u|-4U)R!lIN|<#u1$Z6(+H%7@&1>zyG=H2mTh)RlQtCwQ(2QEpc%9J77p*OxgmR7Ym<2!~U36yH*ITUp`Fvu-Jy?Gyg7g*TP^On>>D!drdjb;5`=r<yv@saC50^%rTD;C;8~)qSFt#-#^^s;#ycga%GcZHB+D{57Hay><JA8lNUKTjRA1=K);Tx|?v{U5U8XzdW`D?G51u+Pi;jxJ>cSh-*N*vSuIrgVw$d4HT6?Kb*T4?K7(Pig=~uD|vs;jnd!q#6I}ra$mvq^xQqxI*qgy$Y&f+M?aLF?nV(GSlCbYV^&=~+8eKU1MS-jUJ~k!&xc<-oOlTSrg?3MTQ{x_?W69Ib-uCzbq7)$bsh3#MWg@5;9qv)IeY8(i{~0`cQ@jC`4RZFU%xvj`|GR}?OKoa9cVw`M7$ENAdj~B<PPg|^~$$pe-t15+S4a6o?4NCdc0c(ZAV>6TTqYDR)hNVZ9muIzGpw%gL+bBKCLPhe&g3f`P{J6yK(=LC%0LjtA3dEGU9(8xfQx_5uU3Q#6O9=??gQZt(pmc;LQW5U!V8fX6yI_vfHt4{OaOO&;@7YczRxx<5D&4X<Wa57J0nh9++S6*+WktPu6xhp1rQaJn4B4)L85E*Q{x_`t_J5IgfkSV}1BzGHR^j<BeH`@iO+rtnaW6*Bq}wKiU)4p{~y}n#8sK=#nbj?`&O*xFvUB9=-D)#5&P-u3im)*Or$=y!uR}To+d@h2QX%$n}4?6m=R0kFJDvt44lh+gyx;qF?<e@_nSq_?i`1KYmx)a%+FJ`wY3xS{5uj-#9C|S;dIk`nw#rCk|shD2_#i@L!S%f8h8@8GmGV!TIK0@zl?BS@P?hHpx8U(F<JXTc7W}dLR08ydCxHLpN=J|C+6fk>^ZXhjpUNZd!u)rSs+cUfa6`{({(L*5?M_FFhyXA?tI4@1wpt>S5&N{-XqDRp9wauRj8{Z^SsOlkS)A|3?igJLKm+VC;Hq4dN5t!uaU({jy&b7d?*a9Y<w<bK~EH`lqjje`>WH&sC4eebV259sKUmGS8e8>|e_ImTL6#gJavEq1Pgh(f#5Lc%S3aQD>mK0sEwJYQRRs9WIdX@8VFo?-qXnzmcDTc~W=IIEs2Me{D1TZPVns`ti(D$WuCdtIM)({X>&6&iYq&S%+2!RZq`?-}`&gcKEr^E5??&xUcO7>7P>}=XZb$`;qef<2&F#nfE+Y4|Ab?UH_fXidO8~ftU!nZ&x0Z{!<e%@5VRN<vdP4Q;++(pDXb{;2cpmyobE{r&)46_vwoLO3UuE3w583!TL~#e~b4qQ2O!<$aC-FI>gUZHX`3AeRt#fPCL#OU6tdmJ3rrTeQxl)(^s~`A3PWI+FE(O9Xis0`<9hpJiMiO(toT7@4r6D34b6zUG^*Uk4Ecw2G3coWghw;IQykM-&TEH4gKjSdCskGmE#okjXZCBC-z(8wFR5xx!d}i9G68!s9UYfmhbDZ)y>xaYRx~^@AGu{YH6Nwx~Qs)xr3V)VScp~7g|19gj4*2dj3zAl41YqlVxaX^8fs1iM-0J!DHHJ>Ui>K@<?hnd8}y@87p)O*+U*rokSi_&ZdqdXNa*gEsG{N*R;vh2~>?NERXF%^U0IRSJMQ$S(}@+xaprl%V#b5%r%LY$NI*RbEp%@Ipi@^jXZ{&NzEV&O(yp=t+#15>Sg3XrVS+vO(9=My@(n|?o91LjU)FUt2DuvQ*C6S4zfy3r8>x|<WV%iPO6P8bTD}obu4u-c`SJ%O>i33Mz*oPX^ctZT&2<PrloLhQ#eM!xfblA4kEkASI`6}P;F!z$3KBFLi<uLBljhDqxL3uBZpIalEcZNG{N1eHnPwtaws)~8buBv2Y-SisWx(OeMB-wXc+ZEau~TYHMn;Am^Q#PJ9QvA-Lw&8p-E(+iDaSu$wDtB3++X|n0f&<hTMtTg&ITdLhecv98I;8?aUv|7@-l=UgQXJEcH@yEV&=GKe-<{nVLvWCTCKU$eH9Z)Dg<LcVBQ0HC;KkR|pR7CxWk}+Q~wPlgClBsl&<H<dHPN!>D$$o%1-1F+zt>2a<=7<EaD4@#IUWeaIenNN8->Km99y?x%|d+u<Mczu(#MIJDlm%gpuH;plO9#*r9m{*{{gfY{NLKLG$>PP+'

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
