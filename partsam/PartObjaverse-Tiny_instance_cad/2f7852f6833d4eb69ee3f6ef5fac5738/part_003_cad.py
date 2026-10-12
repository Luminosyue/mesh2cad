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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2f7852f6833d4eb69ee3f6ef5fac5738/part_003.stl', 'relative_path': '2f7852f6833d4eb69ee3f6ef5fac5738/part_003.stl', 'source_sha256': '7bb558c107743eb3661b4361f7d5ddb8a29bb398547808608ecda55428e2dcc6', 'input_faces': 78, 'input_vertices': 74, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.240427166223526, -0.5, -0.08875124156475067], [-0.05203554034233093, 0.39667123556137085, 0.11151005327701569]]}
GEOMETRY_BASE85 = 'c$}qI3s6*57(VQx2rexeYT<(=K~PszM0xn&211&otI0HJ6A-eB8sM&DIgEA390${I6e@E@Ta`?a5T#Vc2NzH(1Sd^_G@T8{S3ai4_?jB&obUW=cbl4N>N4Ma-}&x;|NEc+o_j89n`ZP4X7UJQ8FM;n3;h@qFtK2^EZ4C#FDKU-onN@zhXuhGhlfk2XS`s0*@rD-MUnGzojH!kL`&oZdwitT5@|1REOlh(XBIf-<qAJ7d$BW@`_2W~g}Hnj6&Gu@j2UXRtg!soBY>Bn%xpSUCu-U3Qz1CZ-nA=<vlf!q3V-f|!-AFU;yuDwx*A&G-y8jbV9hW1Q{k({cTS42dh^B+@Hj_}@Y%w3(qDP|DDs@xz8(I_82C(WeO<7t!}JOAzcg6-)y7?j@39zpw6Wc!Uv}dl#)+L<aNl9SHN*dPX(jG6z_b$i??gzyWt56K4;c}!OnK#N`0isx$Upd81@a_?O8?zAN(H-X1F8|f^}$#0?YlN1&(HTiM10U`_}Z=4zQcIzWtrdOn{(hR8CT$I#srz?j9o*0y=Hv`9{R8ebw9fFCGyPQx&glB2z*wOc|eRULyn^!b<nvJ@WU?DB2G;W!Tk(P@ZCv<Gnm))m~G;G)`C(Q&rjh#)d`=Yp4pl3wXR7Qao#$2Kk}Pi^o}>gZ_@jg>36@^`z$70#xJ;f6yt#ABDsFTq<^=)4&%UeJHghC$8mkXwT+0cOnDRa_D_eeoV(G1xHI44xmY~@1L-TBXW=uyLGW37>S=Ii@@C|HSlWnnys5Sg{!b_0Lj0qRjrw`9oo!n%pQLp7ma=Hfi!Hjm9(}2~)_`%|$0u-ocv~g<x#7I@_qJlb+T44a(Vr0o(vMz+KC;01F4VhsGJG|CRx9Gt`xFaycSXV1PPNE+wPxUXv4Y?0k*8)!8}ggGst}(qeWgwMu28lY^(-&<j!(<`4CgOSt=G?2=^s#ovFWDf<=<L+1buGnl>RThQKvH9S3dXWe~^AeO$+LC70mz#zXxAEeM`<O#l0H$-|d92l$)@ww6rOQP|v~;naABJ>nv&5ulJRlRULX?C0{!z<6V6ly?kZ7jQ991M^hcv|LiQe{%Z$f-?03+s!o4jrQ-fRa6W^tHaq3K0&cEBpF=KTpK@PwT)=geP36dw*bZOq?%R&@cUQpI;&w>iJVUM%V`dq+YKPnhXO^GGJhmB2;TJ7~?;ci;b*mPat;f8!-Z`xAgOa)%`>p!UkXqEyaP1qMk1N=T@%0@C^v_YVAClv#SHAFC=i4sI{?E&YuiUT4I?u8l#=erZ=;}WG`=T97#(HMgtE*8b?I)JX+gSh1$62k<pJgtQ`~Sod@U?8Se2?bDsED5(CH>XM;433L(Kls#NfqK&gty7}qw#%=Qy=Z|s=sjg+o;1`U*Yw>pIvAN&o8gg$E&Y4SL%KBp6SA4-{$qTwheFvMfox&;LpF-_H5m!TA1SS@ZW!`^J4$qr#k+Bf2xP`8pd*rAP8+Gjwfv;9YXvJ=@8OS5rpndJeag#f70T=lWrWn2to%CgziafAl;L6cVb4`NbEz*Nc$4^AZDZ)UEhNsw25G#`V4e$e_}t<{-izin@RU3?U}oo`XM+-*PkHjpWtv^Kf`rB7kW5x5b5Eh!-&nK!$?0(>_^&<dMb1vM}Lk8;!&g{NRKBSMX`aThj5G}jwOyF9ZPyVaRlinI3hU)5QL5)2tAr(BF7Ytp#-5rIfikF*Jcty=w#x)q?1Xf5r>ivr9489;Yj3ok|6Xzg3uEPLO(|k`dQ*Jqz7>%aKsUWRyd||q;jMXE2I^QNg)V5nRp!O$)uAALPryX?n4l|A8`WdexxlNwrM_wVB<giB>3}CvGDaj5dM0l_x7Z}vWn+=yjj_%b;G-5;D1Xv_rhKN0Ld4s9{'

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
