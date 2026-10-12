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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2e5436e635dc4336984c76a5f92c7141/part_004.stl', 'relative_path': '2e5436e635dc4336984c76a5f92c7141/part_004.stl', 'source_sha256': '5cc9a5eb308d761f5dc0ab06c52a2739fcb2b2ce90a1ade9f34b8132395edccc', 'input_faces': 246, 'input_vertices': 222, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.009584452956914902, 0.0548369362950325, 0.2841681241989136], [0.025031547993421555, 0.10948467254638672, 0.4999998211860657]]}
GEOMETRY_BASE85 = 'c$}r0d303O9mih?VKbnZP{EA}ixG%`EKym9pe&6c0YSjBObAI>6G#F917%o(6#)rhNd$C&vK0_Yk|7JrAeOSI>>x#8+FILED{T+<4^NMD=FaCn=ic{vPEVV2-uZs!lbiSM``tJ1-FHvYk|XQK8lj&!WB$F-JJMPhMsSNZVvV_(c?DB5GV?p<%$grzJR*GXM`r1;Q7LI-BaFF5QT*i0{EWQ#UXJ)aSue&XIO4N%^9u6Pb0+5IP0kGZLFqH{GXp+<O8TtKz~^VXb?cVk=-wg0vC#29{xk`6!5z7E>G5D+#+4uLAN<_==$-yH-nr<u@V>J9OM>3{!VzzHd)@2peeSu{cI~B??VYK;7Awbn@F3KmG56d-?<x7JO6jNO<$k1hCnnd}wU^%P=kGR$e9v><@Z*|(Np`j3`%YgN^!`=#y>{N{*tsU$I|rnM{P@s$8L=goMSrs57Kr_~yXm#{>ql2B-kn+`j$6}4t%K&xI^dnn9<H@(FTGiZ%lqa9y`!kD(jV#l!<yA7{`QD@%JoyZ?vAbJxW@Od6^iq^l2R33AJhN-OQmjx@rv-CxVzr){ad`;Ki<7_aJ5}~)5|)foG(zuC8joXUYXItJF}9M<66ADp7Fl)d)0RBO)vYIdm>-dIsIF2_;IE8P3cn|?w!R=L;iSCRe1fScYNnn$7N$-o;a`mg_WY6?5FPKxJy63PPtBWZ(djDF3%G6zdu^(zx1xFH<bPx^^$T#-OBch;~H{&@xIo@waU0RKRZ*5*O^^a$~fv?)>Ha#R@B(GmtM9%`%Sj+-cwadKc$bEUZeQG__IVE4*jt*yw1}58z$E(zO-VZ7?-=P)&A>V_6P63)x6fOz3FB9-47;+e)|4g5k9^a&v;4iX*i_LZa>nS?Js&piGC&yQR{>EExoJO=i7pjVn6dbsN;)wr8cTl#`oC$0ivG2ovGFn@Bh<DwVq$cwGlbxVCcG)_0hdNFTBIGSgoh-W&4uv2MRy%j@XayQO*l*yfva$xz1DmIb7tYZl%uBd%ioU)LHjtozv%x6~C{4x<aWN-c>P8ty^N5OML!1My(s(ck8J-#UGh7S)A8D#;bMHy{rS?fAz9jH{H|TnH`@kKF?UI)J=M4ibtuN^WN#%;=I~BmAXmq+4gs(Zn`(?cBwi~Wb{h4Zg~IRol4!DhYsh9-*5k-BD_APj~}Jht<+l}`Z=bPS~uOB-`|k;Ol(-Eet$JD@2d-@%@LosO;YM+`o}IPbu)TzS|qZpqx!wZyK@TFI^bP@IHR1e^qv*1)brB4JTJMQ$`R`KLLN8DZ`)6I-<E0}bg%8-^JR9OT|eDpYt`#t)}d>|BX;|d-uylm{dJjLolURR*)wZ!vE8^^Jjaz@A9stF<L*CIY<C@+Ub_w*!v`(5yUwMzT<1y0mfL>6@RskF=FRs0&)>HFUgP!ewUJ!BLi9_&&*)x`7v6H8(Y?HX?pyGV`1=hp`^4w-T`t*qBWk(oueUg0>$Ur*^p^W)vx1f4_xk-Auiu|tf6G`U+H21R>GkJ=?#=nwg-NSL-L&VC^!oG2)$NUU#b@pLXz}v6c>Vck@p8N()7Oa9pVxT(dF|TQvP7JhHXo4QG9Q@MNqEbA1Fz3F+@ntjug`xhUfu`r`us=tvb|%&C!zjm^EZoUKho>-H;b3YeRKa>aX#97QhI$p=}bH?ygpwwy*6KUe6XTacy0b{@v{HYYx8G|m-me=<-+UpdFl1}yf3xEI#FlseL;H5`@+Cn;q~_yi<i$q>9zM4-JAEfW9x*syiegR?^D$$LSB1cliu>aHus9~`un5B%X;GV_eYDD*H71|_2PKid#hv1HsSU6Ws8^Nj@RFpEnXgX+|H2K-rr5Hy}x^6zY6tJTOY7^IbLi3CA_}=Aici+VD#OwL3nLFMEB-(g4fqWbZ_2=y*Gr{*Jn(xt<Sjjx7(<Ui}VQz!t3ir((CI*uFqPRiT!KqQKr|{qg;)L3a_t^>E3)E;q~<~-OKi#WjSTx<7Lh__9T~!)Yb!aZ+`Fa`g)-5&HCToT5flp=w7r>Q&wYJjcQliDB3WBTVo^E$Vv}eiVe!(k4*ce*r`4KyQSD3iU03X?E8T}Yzb_K$X~*T;4|cD_zZl7ybND~Z;+qEH{e_37w|3kCixrqCVY*&3SWcIk!Rs^a3xs*SHd3h1K0zvA>W19z;1F8?1uBnJUAa7NB#sJ2d9$5;8fU2_J^Ht0@(>pfLoBUa0|Ez*%)pDN0Ig6C^&*N;0QR9tOrNJjmU;@BRGb96pn#Ak{#fVa6hsy9LyBBADqS(<niPi@OXF%nGH{Y7mz=N7r-mY)$mHVoO~ZHhxe0*;QjDN<Qe!Q_&j+9J`Z0cZ@?Gf>*Ou?I(&(|315OQkk{Y~@JaF<d=mbUtb{*=-y=Qnd+;i94ZI3oNV?&L@N6<4o()eR$H5ce;bba29DbQ}!Y{*J$ppA7`~=woegbYrHi4VL(PR`H4L2Yo;0EwRWF-6$+>~qtH-#T3W8lZ(E@Vfz3p|kQ2M03^E(~nb1KTvVAg7a);B<H-ISL*L4<?7egW;FRUhqrs^JF*pc{q-21INKnl25@;!Y#>Ga7*}UvNilP+?H$yw}rctJ>c$eZ?X^E8y-sj7#<40PL76Ohcn2@a0Z-1=E6DfJaRrf4=yH`!^QA=as#{`-cJ4;-VX02_rZJNI`Rly2m8nqun+#2{1yB$e2hE}AA@ViTDS(@L;eEZ18*g_!CT={avfX>FC~}3OX0a>AsozUa8Y2J71(C71v!g!!CCNF@-=uY{3<yJeicq4Uxbt3MDkfU5$;Sr26u*^A)CX`zz*_Z*a5dEAA#G$&yhcZpM!gn@o-Og0Qmwu08S=ffs^4e<Op~SoJmfEGvOKJRCoqlK)wkVz>CQh@M5@x+z6Mzo5&sTCU_TF1@D3nkf-1S@L}>3_%M8w{0u${SCgN@)$l>`*YH7jH|d3U!<)&S@Md@|Sq86#myqwkOW-+V5gg2!@XrF<TY>HEz?POAQ7<;~KmAL`4?k`(aSQ(k5B)FI*N^bOTpie#`7)B092I;91}1s+#KZhz@Q!c%8vq}_;s'

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
