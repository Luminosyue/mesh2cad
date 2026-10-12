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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ed24b6e27921449f935509d9f3da043f/part_001.stl', 'relative_path': 'ed24b6e27921449f935509d9f3da043f/part_001.stl', 'source_sha256': '0034a881a8a27ea4e71c48b615f2dab616c5f9e54339203d5b9cb0f00b96cd2f', 'input_faces': 199, 'input_vertices': 139, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15177811682224274, -0.12229961156845093, -0.0820169597864151], [0.142923504114151, 0.2768372893333435, 0.09225323796272278]]}
GEOMETRY_BASE85 = 'c$}q}3s4o;8OK+7h#-Q9i1l^x5kycUngr3vh6pND1w_$^aFK^EK;CGKx*!TtO)_dx)Zi)@qoM&pKt);Ku^4L{lZ@7yJI$C;o7l#n)lA29&-eXrdhZ=N(`oO_H~-)LbMD#ieCO<*vqVMO*?UU-@sTRO?K`c^Rgy&XkUXV=)SSGf$*H-cGqYB8k=)4_AG2<oIcG-H{4P>~wAwc%H8(lOH`w4iDJ{r1z~Gy<A}22=DKl|JPD-lq!;{i;Q*}RgNm5p-{(Z#QaT5Xz<NN{)YYhM6$5~IoP?&L{O;_da%d<kI_U)M=LMyz<m+A+#3Dxetc~JPu`#+o~zuPSGRpZnB^!pd{HPWYHXUO;1eN?oUudSzc(uk{DNl$bC^0|9_y#SYOLgk``p9tSDWgYt+&)7Gtt07%+<TUx74?d>+>bM`{eJ}QluTgvB@QcUDPjR$ruRW2g$+tg$iu}NB<jaLq_R{zw_ONe%Z##XTeflu<XG~|`;nk~@pP_v_>Hc{3Qv&EZrYCofQ(iloPm&*-$a&Uto~E5s+4pbfcD1PUW)G|OT2nOD!PK*%h5X>B2Pn^>D%HWXWk36Qm#H5u?qLnJPmW=Ka0UC-%lA?K$Nt<*{@8Du=z51xx9TAFy&jTpI_XdKkq?a{UwO~@y7;cfRPCa9|NeOs)#cQN8`RIp&C95tgvaDd=UTY`9`RI9lhaxDkA+bFN>$%Fx{hNd`HJ_0&!~UrP|8zzIGx)EwOpZo!%XBG_Do@aYa@+QiF~J)@)%rlg8W-M&y(+0QApoM#geZzG=D+)6nR%sK1cny{h&=Wzfwa-16?QfVk2Guh8<m3wSR3t<yl(Z$o1(~L4Ut}sh;|gE;Z2izYM%U{i|^qv_8X)<V&GfxenO}X}pqO82h7sqPiOU&!WGpJxs@`pGT*tAGNiJuB*)ZihSvxYq_6AHAkrqF8<tJU8+&LjF;JbKc1t!q!0I;qIKC4RzmZ*xPtv3_f!9-41en1aKVNBVMn;0UXQ2_rkwgZ>fdiM&95BTSV0<_O}=#fA*~OCe3$Dm_VzLIS5{x6^|s(DtzYBr7e~1c1ypBK<zybO|7!M|zM}lKw!d<JGj`Ql)w$avu2<~#kNJN5hV%S-`w6N?-sA(Ek2A0Peq47s=WCUG?^S#~)s5P#!|Z51O1t~<I+vbN9ktDoo5)wD@;uG+r1r}Ap(W%y-T0L9>(F>U+8m=oI`g*{&n5p}?LNAmF}T6XKlYf~%Qvsn_?7RbFC>3sJGD2A+)DM;+G^56Ec5Yty*{KfA9<R*cW2S}Y5BZvF8_SIGhZ87!{gdFw3z&Y2&$Xx>d)&q<#YDmT~5AwqKWf4o?S|Q?I5~;wU=(RPHcT8doA^EaBAF2{($K`k7Ewg{iE)6-4<dozjC`obu$K)|DOCtm7lj8N*Y5t@zp@TX6nDZJFQ3Cc~tL|vHy4k`O2Cxv@T7JAMFgWSPxplSgNP3Z(b)#P>UMU$-2^7U8s)IAFf)hLzAButzYGX8hWnC?!VA@<z2kbNF9~r8*1lJo^oAz4bRI2ZeP+t<F)mb2OrURrE|PLNkf)VJE^?x2(7F14)&k-<KN%?j_ybGX&LR$(w0~nm;Awxw0~*ITiLJwl>70iq4lWt^85tzXm#Id&4KK<<xzV>;(eNTLuD!Z-|yr)$KR%X*7V5n5cz+f&hxUbj`C3wbJ@3f4j4b1c$oZ6)tu)Sd-?g39$(A#w|>q@e|w+K5w_1O<4-r(H$Nu>%jkJw8h(KClAIgae>9b@r(Jr5?jI$lEA6*xWh<?7xqlq{AI_uwQ@wtR>R`B7QD@aZp2Nm9t?d8qAn&(xWXeZA??~&*{G3;Rn8EAr=l<;5><h{^M?ME+9O8Cmdv{Piaq@A?`^CKP7$=3Z|KfA5zwuHP{cg)8E8o1o%Zu)_Z?oTNQ4+5MoBh;yW)=Ik`?bem_HFieHICP>`CMT>KWK|8Pgwfqd`w|({N3h!VmdIJ#}m`U=e3wtTIYt)1a5D0&XF%<vTt)PQsnFG+nl4+f86B$UDLV$E8#RQ!wkD-%l^&hF(op$*|MKs&u>-5?1vXoKZXmddB2?N-9o<2Inek^9Q!usNwsAS`!?rK)%!gAHs@8X@+SKU-&mb*wV{hol3#Pr>O8DI4{qi9Jh3`ItNFXwcN}DO-j?0_oS|_mcj(-%E%K_S_DTr(w&!+f@N#aSdw|=QRvqMZ=x~<&x#i?b@dFM~eG>B6w|y@d__B?Bxr5I8+MllMq4r<;@cE|kkNh6ctDT;|>X1bCcQjhPr)W#s&rx1B?;~>7GxjTnS-ro=(UE*!w0z%*vU-b)_ISGIR(JhmsYiGHEiNs|;uTJq;$zm%U*VRH|L<PmCj8&8a3k~_#^~V-^#l8Yhd_sehkyq{4d8*`{(Afd+5>6;_W*lAM}dX<gT26g5rPNl@rE8#^@!9XLXSy${8o?EdgSV{23i1q7n%bt0I!0sg%*I<f{PG>*Fkf^>%i~nu@t%-nhRbI&W5fAXM^*hYry7Q^AUnqKy$z=z{@PgunZwMO%Efq5V{In2wo3e3tkT{gBF3yz~u<Ro1p8!o4_T|_rN9Kl@>Kxi4dHO5Ii6ACo~?q6ucC5j7JDgK?u%(W`i@pnb3T2K5CbV5S$KO22KYjAp|dgrhy}&bD(KpbKM2M4V?isf@eY#p+;~bI15?`&H^jY^<V|O0a^y$04{}=gUc~br3k?rp(Wsr;9}@Xa4|R!nheeZFVbTcGzyvwPR3kDLBqjO;8_U4VbICoFz}mtyaf$~P6kiLZ$hE-!RGZ83Y`QF1;2$5JP{fJo(P_<M=W$MGy)ufe&<5t!LiVHpz&a#Dd1RW95e+S2Tp)yfD^!rp_$;t;3WvbsnB$ADtI9@3A_+ITaReyJZKVF=mKywGzPi=Y`!02pi{xo&}q=A;A!9q&^N#nz%oK`2s9EbbPm{jkA*;kz%n!#8UzjoPl3J-o&uf;HQ%GJ=`l`^v3iWx<8?g(C9#3)M*}_F5rTUn1owhEg9ku+L!H6B!EVrQ;BL5v8$z%L)E(>r?x)9Ks1wv3>;!gz_5?eC?Gb_<p}oM4U>A!qxF7`kpcb#{5dif8`=Ct#LhvgH!QRl`U~jM|)D7&0ae5*I_ks2U_W=(@2p(xsmywu1p`)RL!K1;$5Q1HyPGDEC9n=AA2krv32X_IRKZ3jJ5f#~`tEb(6`nUeSKZ@wU>Yx0!zqCF|TK@8~-q)`O%cw{PF^BrayV3^ur8qfB{{j%a`wj'

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
