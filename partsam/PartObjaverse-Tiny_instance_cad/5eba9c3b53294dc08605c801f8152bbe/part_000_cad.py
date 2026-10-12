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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5eba9c3b53294dc08605c801f8152bbe/part_000.stl', 'relative_path': '5eba9c3b53294dc08605c801f8152bbe/part_000.stl', 'source_sha256': '361cbe73a2c00eeaa780f9847e6fbfaa857e71d061982405d2bb164427af9667', 'input_faces': 174, 'input_vertices': 123, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.13615629076957703, -0.32226133346557617, -0.027281461283564568], [0.15303951501846313, 0.1416199803352356, 0.48388952016830444]]}
GEOMETRY_BASE85 = 'c$}q}33N_p8pm%UBtmM7HnD!z2q6ifgvzx=3?fKE$Pgkck&P@exY}bWsj>9X3K9`hN=WUEC6_AE(J5nX6|q!{5?#<y#@zS+{IxO1oHJ+U%X!cLe}CU|pZmV=ectzeHz9+oIk;-_X`vN9>HWD=ZB0|Hw&tp3#H3A2h>l6`G&LpLPOA&9KF@V|aM;k02s<r9%kh{LlOCPs;cxTk72Dmz%jOZAoHi|O!qoA}X_I0U51cS1J;vhc@e@*FtmAgRox6D1x_EloX4?M8kF(VUb7|6{GS!!XYxf3NqMzCHccoF&8VmQC{Z0V-{LKZWM)4gJJS1`k;@vl#S86UQ623it3*v9sBv1Nk;n{!PjkpFE&*1w;dBXQ^+yg$g^fcl(E){;v|6^Ql&B;@U&mk}D0dBr4T<>HEpOn89@gpkHAML>u;pabJr_@&e`*k>PdVk@e-)=(O?N#TH=k|><@HcOQ>#_0ZXVkqb;Ci!#hm{(A)~?5O?j4u-5kWHEOaAD;Eq#q}&8-vSkK{@Iz1hOOI+P$jB^>=Xe$5izt39}RJ`6nSl}``i{D>JR@O@rI5%PSJ3$9(bDcAk8<3*(vDdg|o1~+e#-?kGT{BRfek@;tFUPk2s@U{g7=tn>OD`?Go!b9@Gb#LK%PLc2$KW;!=Sj5-J(=b^0z5Fwnry{4np#Pa}!rNUhfG%>7JaLY~BL;kg{xlned9E0_V?X%A+UUPt+#db34cCQd%~^@~ulzACz2Uxn;9q=gf}gsIdedFk37=Plde(C1A-|clT==ukHYhbuXQG}9hRhP4U#C!Mh0B4>$YY-)JmdlDN85Hc7vnxVSa@mzuB+KK#C2_l27w#L;=%PYS8(lQONp<DmUR?U?@MUl(^Bv~Zdez_$kwP6ZOc*NJz8OY^q#)xzcIZ~_}SNFyg64<Z+hY&;rZvvaQ>ZJ5<he0$Kc*`QMYD!!ZyT*Ed<x|W`WzhyDdTdvm}W(d<G(a<Sz8bI2<M1Rz4Ye*ZDH;SLu&?aqKz*>q>9EQR?}|V&S#?4uD@@iu<T9X)3(aHq?(9_24A<BJ!-Q!o7ss9y<z;`iJB{cNFt!9DlS2{N%-a#6P=_c`!Owg6lacSTDxpti_m**;gh0=LOgw^nIVAZY$0mkod&uh__wtAoIPeNa8~y)*#Pa7u0P<)(^YE<Ev+bmwtdeX2N#ihcB!LpEDbEWlM<{Uf5pNt(z(PUS(b3-LD%szt%69PqW42UEu$mFY9aKX&Kj*<HG0qpgs%!_6+l(eHRTL)mYYD#Z#{x=;!p2;6}z8S&y&g%txLYJta@*jWsw<jF&nrD%lC1;){LFyc3S~rA3zS06!Xwbz~$D6z+0NxO*J9=_FitpDFz88(Yzz&6Rm&FX6V>#60A=l_>nXY1o&v<n!3K3;ZI5J7!6JF58QKX_xnJ2fsE7>(jja3+B@{GhFzlSqH&4P6gM;^by|bl})JszC$h{&)caVVSaYbI)rh(U5vUl7bFXxM?P1$&F4}H@(gRd6Xyq=#(g(dZ5Muj#6p~(@+<OJEJ_8}zfC}0>31IE{ud<sfE%l9hjIRxIkI0xZ`uZavxi)_>r&kJf(OCiT8kfw@O@hc)QLVZ1@ovCcwxQk4wJCH%$kjampsJt%h>xR){#-@F1*(R;hDnCdv6va@8w3guC{oqJn#HH!L<v^=7BrRk?}hIv;}-^Q_QE4-VWo{&#&AJUcO1{wq%aXXX-NHL4kN4m~C=pKU|+F{K;aegG1LaE-i!nX7&fj>zgk7_DrV_!JQjo9<|Us%#RtGjDAF&%9HwE;EC&KE%$6h{FXuk>!osNXB^vNvF~e3>g`AV@eQO-o|a?XYO8OqK;8k_GTvodgm>GAeM~EEE&JQ<4~0J{mHq8~;ri?+@|^g-ay#N5ZI^zoEfYSxQ0iy=1<b#eO`ft&c(`!$tvunG$#`z+lRc$wBd^JGwBURx`cYvo&+*5l!u{TPAMue*<hgu0NBF#P*cXhe#j^i|b<PJr*iFV2P(${agV(X&X`>Udj<n^sWW3(vSIhiYAdg<YLGI(ZFIItH94GyEeoNv5=Aa+iiu*Fpb-d+yRQ<|(;JNNlGww3RWz;?+{JkVx*EmuxzeDcrTL~VME7x6iLi*|Q(-PF*u5)<q6^vTBqU<HSqCtJ!Pp$XT#mM73Pxkkp8_2#_T9O8C|C#*G9CJ!|(AqyiSFe}-pn&zWtts{$&D9ORiw&QVxi919*iMU(FX$UQZ?&`hU63q!j1wz9K|jhKNuGWd4|(A&BB*P6wT(`irdmzwEh2V8l~)J_)#tgs{1qa>@4tJ6c-`;+eT9g!`Vg<mml{j&r^aZtq115taK;R!Cete&LqC+>k2-{2X&-u}_38bouTksMD}9w-X%l*Xsu#5hz0%j|l@6l!rw*qMq90B_N|lY(Qmi(fI=zZl-}R+7qwh=KfZB*&X+!$)%o9zWMjuVzlNvzZh}w`EKtIrG1FY78+M2#QwHviHy(%p`9xHXHcjx!d<J_4;X><DKRdTnrntI1<Lv^BeVn5n2*8sA%>}v;lrLRz%)3>EMvv2A=d#W?NGh^(j&FP!7ul7_s`o>mM%dZyIfxZ^K3$;4E3w<@JMqiD-F0}^zB&#J^Z6urWqp4HqN7F}8Q|Tk<BdH1WO2^W-vRYHC{eeySVN?(LVe}!?cJv|iVbo6aN=H=jt~_?-e2rjJK91UhK8`+tI<|`M%;T~2kyKy$NcsqB$13yCk@KX~o8FsqI-327W1p2yr4OSIp(a)tdm`sX>EtSNHJNj%bRvBZj<Ykh7JX-WU#bheFMUU9HTsV9-qgDE>OR)seN(E@t50?Mrt}_E2YL_sc2rk-SKdG6CvhxE)XDTo^i!yb^i$|lsZ;4w=@Y1N^ewG6*lLc{3G|Nib*M4)b?AMlq4aN9t*h1Q(f^UhN`tHT-aHPb??QE>cVmt&%u|m{{r9askL%HQp$5_iGH(~gbme)q={>2z^q%zUyqcPNjQ<|rg1MFUqVL7n_Kfl5c{S;6)IfS0y*jVI)zYmtj!pRtY8HJ4eKvIleLt(EF-L#;bZRDjI(-&(MwJ|y%#+D;vf0vj%`{#kgF22rWU!sRYqkIMuhQQ?hT4>0_{ZtLpZVg?qpD{HT8V!9u@o}6I@XZA^`{EfQ#}c_e*s>;W)='

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
