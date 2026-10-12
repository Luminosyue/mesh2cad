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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ea7259d5a16544c08369264acb581f89/part_007.stl', 'relative_path': 'ea7259d5a16544c08369264acb581f89/part_007.stl', 'source_sha256': '16118822630b964f246250919109a71eb6c2639ea65a07792545f92317a1709c', 'input_faces': 72, 'input_vertices': 85, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1294732689857483, -0.21521753072738647, -0.04499462991952896], [-0.03202725201845169, -0.16965971887111664, 0.06415387988090515]]}
GEOMETRY_BASE85 = 'c$}qI2~bs47(Rd-@>EPxTzhJY%M%456)>(lf(p2dOM^Z_+*y3!LP}l{M9j<u*OXr13L{}En#puEchgZ@gi?Dgq@<FLnNDSO&iDW1v#FV;-poJWcRs%Ropb+l?ww0igj+2yLBF=5&TJ!bemx;nnS_^^8*fXU9v7eDo0y#DB0Qn1Uk$DuF=lwwco#8OEby5epAu*D2{QYHOzG`oG5btOvZdN$6DK9vCdVs%aO|v<c&VpMi%pJ~<4(N;E#{t`E#`FdfBn^$OVD%I7#~Q~E*?3h(C9REb*REvQ<)lzjdf1~wY2HL)8mc+6IPxEy60|Ieye{s==#3-$gvyI&_$5z`^Y`Jll&jKEysLke|Qi2pykkY&snRX2QPvyMmmrqJbGk7Z=8P!c%z(hUb$z-IxDiE>rE`=pLpJ`(6J#6y3r_;?rUy7{9?pB=wfV7=z3A!O02hX8s%39Az!<`5Pm&OBY*b_>O;u=c}my%ctN*6K6U~*_3zA8y8TS*L5wF}KMQ}%s|5<pw}wI&1HzDF#8}p1{ICmj!+jX}C)hGEwp}O%E(@Xc<hbud?)_8Hg{g|}xAa;zd_4=H>leD8fqr1`VujYs0`gaPAphufcA77W@+)q_uZ^q7Q0q6}ZVp{r=uP{wq+bU5dAsTW#%}~tezM4c&vcaZm<RCNy$)<cfA-`<H`*j%Ui13L1?Xq;4CrD@F#L`TZ}^3^YCrskTB8s8)y6yE`{Fz3`j2;M{bQ5SPvM;dUGr;C`t6O&kz>jtf6y}O=c5ndH_|eoi?FMh*L*Sz^IEGC$X}99=W5mQmoUC)rTi-wXn*^}<Y4`kk(5)Gg?-dlA72Jt^C$nX!<19J9rtVG`_g@_A4cb`S;#i{UT#P87L?HX(<|^?2y@0h%IQyi*yp(ddQroDbRIS#-<Y89M4uBX-i0r8#X0zTmEnH1Z|u;G??+G{-b$i#;=TpCxND;v@$(MkWam;&mj-kmieKD{KHVEaIlnEY`*Nh_0_Ox!PIfq*hd|3FTxV@ex^a`vPq2MAo{LW&@5MNM9`08=QMwEBRvv>c!UM_gR}X&2z+KR_4jT2X{Nr5g@BSR<j%f$6FXrOOYjJLOM?*K_meO;2U^8^xWTJWdM$o<=&MShyY-b7d%GI>~^2jmB?YJJganeHmmVMyY%UeR%vL;d=%;#I+`ma_MV_evSbp7Z|_`4MBf!{lk^e<D>aURUk(2em^Y2LU*oGZ=mUJ>+celK+_%!5Df9CYo$amsl#X(67o(lg{gbrgNDo33nu-+w>(yFQ?txLGAQ=jTR4*FALf$I&TmEBd+h>q7W%=h6LMZUw(RycD{qHjrbDzy1#V(TkuPt#4rc`mzaG@W)OiJ%Re5J#3F0QMi6L#%;Xm9D05_2;-F-cj5Y5SE&!yrNNjd<ssg4M&@kNg+3Bkbp!7Mqkjo>W9HRN<hz=oYoC2i=Xu+TrP$wY)$|<1?VxitKQbHriEK*x#zt6=(QL;$?AN!I`SATdg!1<kY`}dv4nfxn9hBd^awX=?+e><J75ZtdTfH6o7@i4TlzGtmp=b?s{c<4X2QGkaKKU#8H_Uh&x&CA6x!bgB71qBd8oK_bjr7o=n~;+<i1b#u)SrhxErD)H!+Tv^@S^v|rE9Mv-w_X8oAV3&j;K3pL!+MhYI$vcQh>uv{z;a*{A!sJ>-5Q@MD?q|zyD;J9`LU|S$g^Z?@tyFxrP=(EtIgi6Ys%eh25R_03Ivs$GomAZ&@CUEu6S7kA3<28m{qJ<1EEpIZH5lh$lbA-5A}Ox0BTqZ71}1;-NfN*w=|i@>t;r=B;J<ah@MvU&DiW9L(3(@Zmfj&RL3^ILn2x9dj4v4H(-pZzHRdtd_E(Wet<npG)zMj3LZBGH=M(m3c$vD$guSeTxP$Hew#cJe;u}^Kj;)7%j|4F&`|ej;v>7)#g&X8DlTz&6o!=hA|IhK7>p0C|S?SY9gx^V^dk4jJ=tAGVjbdlzC_71Gy9*DXW#N#<HH5)kjtbSrJ@{k7o2@KAQO;F2%cXd2wEQSzTm3$LQn4U*NIA04M$;kE0@7T)o`>>0g>BKV2P=r~bkD>y=NxR-CUam05qjWTGN!tG$vBlB<|4@e*eF14GR(0s'

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
