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

PART_NAME = 'part_013'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7fce3003d95479a9226f7cb639df893/part_013.stl', 'relative_path': 'b7fce3003d95479a9226f7cb639df893/part_013.stl', 'source_sha256': '2a09fcddde788298588aac281914a823f6f62fe76ca90518b139b38b613cb36e', 'input_faces': 166, 'input_vertices': 129, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0525616779923439, -0.49889716506004333, 0.10112643241882324], [0.25984954833984375, -0.21300733089447021, 0.4607907831668854]]}
GEOMETRY_BASE85 = 'c$}q}3s4p36~{jzYETpuqN0H;%2UxOB1)jLA~8G^P(dMrEb<T{f^tE8pjpSJO<J2yCW%tp;_al2G0}|1nEI%);P~LJz*U~{nvTw-Q;jB_nrf!g{m%ZEeA{VfI_;e~^Z)JN-LvOAdv=#KE!p)MZ)W`bS?;Nls#<r(c(^lfwym(DvLwIIHm7XMjuFh0eEu`_-IR<KX;~xKHnuCcpwO0I5&V)A98<I?I7|vIDzB)l$Scb&uP7+w{<6GMTcPgTiu1M<>f0gn!lS~Z`JrLbZs~vgjnPYxbH4hhL05I~SM6M-4KWvEd2LCdNBOq=aB~}1XLwu_`D1@!7x!nSe>zM4r;&$fyL)LXSNqwhOWb#sov5X}AEi3zxS!d`SI;kgpZw3x_Rx9uAG|{Tp4)pZ=Y8(xdCEWcyDBli=I+r*{`!mMVt)2Tg5mdOZ{(`f2T*?I^~<Z|`vklfE1Xv;kZE0N^ZN(I{iULU%jEml*VA$DT)9d0C&k~O?Tz;>zWrKw7j2h~{gA7?@6s*G^Wr{>@2qQfh`#DFM7|oC*h_hW8g7U_>yCGbzLq2%CqE_3*ne+)x9H0~ibM33sI(KL&woYxv$yYciM}@S_dTL7Kb~|_tY14nsz>zA`b}SZ68Ndu2YLEh^3~OIJ`>j^4UM<>=DJLu#kZWc<T?A6ao#)a<f}ooRF8evv0mDq=CJsx^yMw8=WE|T&~X_(#(A4O`$V7J&c12!TWiUeF35efu5-n`qAyoJbcnv(dE|_EUguHgP1?WfbGi?l%bF=aJ36Dy=ugr)+JDoUK4ZNu{i3hk>2p~8`yZ0e-rh<3s~J0PS^S364$)VCokRDBJeWc2Rond9Eq+V1L-d*VAo<$ehm>FW=6Ijz+f!tR=xf>YFId*qP*3Y(#g!MtKC=mb?H7Hs&!(>)N;IA;``e7UdYs%Y`s&on4$;@Vu3fZT-?f<obbMWA1I_QUC&u+X{(7hAGv#29#eceweEa;ke)4bpxmWa6p9ejnZ?Bo4iSwYuebX=c<~*3bGR{W6>b{8TQ7Zd7M4uhXa#;NEPQ$NyMD;L_pBwX*{;ejimkn(nFz)BLM&o*ZOZ7NE@9Y(QWz?}-qVKHxxKW%3d+yiQEk5R9*x%F8C|(zJ`+SRUUKi7sPtR@==aUt#>$murPt(_ao75!EkNx-?l*b;i+v2N_N{#2L*W62DAEfV$`O(hAkguht4bc8i-=O(t6>gWsJ}7_pq`o;**3tWfZThLP|J}XhOOFp<5&NllyAIN}U&K{0zj9!}LEDLWS1tGZPZra2()s<ptKxa(-WA52fBZf9(t+|pn&(N;l;3_N|C-o0r%!K}#Yf*vpDp)jww!m#-;DRd*oEXPXWYJ^e(pI!`KA6v&Ei~XS6rxm=c!%IVm++>g&{irk3Vj<^rt%Bn75i^&0>G-Wv@6y-(2soAMmJIykF$Onl8~d?-$c&eo~8=U;T~UIIomRzVhJyZCY>8Uua$O!MYa9dTVzNiT?2O;giY6d2>5k#QU9nlF%di=KXH^T4_Qn{X3px_HnzqMBjXlnLZn{yj84II$1;YsP7H7iv5vn9~k%b0dM0yU_Nid8oNb*_<0MT`5Vty^LnYNcc>5Aj3M&P_lP}YbGPW5?-A2i@5Z!?^QMHJb69-Lo9SylwsuSXC*L&QJF9oLi*uq(JVfsW`S82#;&st_GmJi*zt?W*&yyVTwSAL2EP1|M(kuGI^WgW`cppVac8GK3%pc_teRHl%UtJp8A<l#1SViw;cGT7(USBnPeUIpy*Vpv5I=4=-9;t1o@xJhy(kbSb{;}Vf{}a<JKKr1_$g?1(Q@oCLWv<b;h=ESAZ*un#`AW#->z4VC*g?+|>2S_<%RD^rHlDYA1=qzqQvXxBk5sMDl1EDoGVUYacPzft;AXr}mET$N$oEh6$EI1nYDT*q+nDeyV?5mSubQGf;gg1&{AcRF|D-92`0qYxA|wCbPnz9&4V(4YgWz0-;Jg9BIU8C8&IYGLUj?UwllVHJE1<7}SAg@OTfkhmf%Cze^ms{+SM*3kaLzz*E`=t8OTp#P)nKk`z_07Ei_ZXbCs+m7KzD$5;J6w@IqEA%&TWV_sF~|p@CNj29fI>JXgYWmI0cc8wWgzYiRc5@7-$msN6-YQ+51R6X6rE%8UUUNmY{xMuFr!durKrlurJsj8VL3W&w|bY&jK%m&I2z5M?+_WXQOV;%b;=4NN^lD0y+~M0S<yn;2`jHs4v(Tbx%id4u;MG2ZI+t7lIdnmqMe#X5CA%-axEx9(Xn)5WNoo`ym3+??CjIbFm(IdK4l!XF+qoS>TmW1-ufRiQrrS-3TrKZ-rKZxo!t<1y@6>z}4UiXfe1LwN@ZFzlPwP3(W%Og43WY!D-;-2+pa{OmHfAJ+uJ49$W(53N8WLpw-}N)M|si2Cl-Ii=ma^O7yE3s(=+-gJNhNm_PQP(ZdD7nL$UgAAX!iK;6J2z^>4-U{~;H<Q#?bJPRHJ9St6h{W*K+;iboO2+mWXlfhHL)1Xtp)4)E^NnjtaH*_M{8|(=k5B3DRL&t&L!4se!U=P$f0rhy{{8PY_5MDUXMDTco7xH-_7w0HF=ISvY!8sHf1`Y+!fW8Qx0S<vK0*8RZp)xoeycik}UJQO2x&-_(I2IZOjzX=R(~?KHc)R|m|62Xwr}81P{737*9%=paMLhDRo@n@wnY84Qe5Uk)bD<k3i(e7;Pc{L}M*'

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
