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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8730f3aafc784a849de8e9f2d9c707f8/part_006.stl', 'relative_path': '8730f3aafc784a849de8e9f2d9c707f8/part_006.stl', 'source_sha256': '1f2a340bc58173bbc819210594b1b5d1a3489fabde85b7c5ac2792d581c5fa69', 'input_faces': 192, 'input_vertices': 173, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.14362332224845886, 0.1191975474357605, 0.10814153403043747], [0.1436222344636917, 0.2841070890426636, 0.20156027376651764]]}
GEOMETRY_BASE85 = 'c$}q~3sjBi8pmG|<C;rK5u4H$iApY^{kc;vDVHg?9TgE0!YDr1+%FU3QrMv)gr?kb`8aNK27@y*8D`CFgL7ugad%wD%-Qer{EhlnXRWi&*=s%P|J(nb@BQBQdEf8y?m|P#S8x>kX)Ic{s^E5{rVui!2}h9>lQ=DIOw3fDNeQ#ciJIig&wEYlKe%6LL^+WpW*ehprjAK81{#c=V%r<N4aV5XiPI9JCXJe$7#$=1o>B2rV{HD^aZw2|w(re++xdGN{Jp#lDTe>?Q^nQ=%{2PVDcP4y`^zSq80H%_Q%V0^-K+AuCEV?lRO=lh`)SqxN_mAzly5lSfP5{m@EYZL?JuIgJ3Tv1`RNfC==+^CZvVtJ_BZx9C%-H07Laer%_d)M|L`x=?(1-F-#3c=<q_m7L*3b5-J1QIcGQ1y?(J!*X3>KE&i2$#wT06eYCpq^&+BWTacNt#DBqB5&;IQJ+|MDdoUc66$WQu`#$`!;Om#4y`icF5j?{m1)EjEYl3C1tm#%cYIQ@X~Ek_TKuQvOh`mY-Dxt~>1*>~<qzF6@I_vg}3_Pye`AED8lfBnQM@}In-@rzjl*l$0G{nTbOF5$L@>olPe`P$dtQ~$M1FFD`g-bu>88p`wWx|ns#AohFQ_=4Jbn#=ui2_#?CXnu+MpO8<!_S}p8r%S1B;$P`Jz78)>kpE2+s*lBg2>IqtKa;PHPrgFm$L5i5wT>WP893@HufwH0|2aY2PVs!|pJMzc*Q4wD<CO0gOXE^zy7PJWjAMV^1NIM1=k`~QAYa_MP4l5-4Wo86mtfAn=)-kuP@ej$<t;l#{WSUUdCw)CrT%{V<|z65oq1i^6;ZzW>of9&{{*U!a^g7o)=TF&zxoBPPwGz2k1yi<E=5!a<+mL6^EPn47Rkrgi6S*5#&iCJLh8TT>^aZx<Z$w}f;YTA7v@tx#od0~jz=<$%jz?cud_byj!-*U{^TolyPv1y>TM@qbyuk!^Mwc0j@D`IVam_F%XRzl7O(dy6AzJJsWo2@MXuzFPrb=k<Flv^)(9hw+tRH$`|So%-Newge4W*HC0|)s@jB%X-NNJkxg6)aKjQj0zM_7bw>&N+Kh*vrwG+whTdy1;Uzy*Y*H6VjuJ_-v*>AO$ulMAgJl>2|<coXhJf2ZE$Tv7PX1}Hf*SG0J&d;ntzUGz2bzbShzDO>h{O>-aI%waNr}LVZ^!l9q8>>!I-mpN**M2>lPyXYYG+y;!SMn8?k>o3HJMw(F{KEC|ZOr-kU-P;e5=i4#t~s&4IF;&Ys2a)jIP=Fr^5-~zMR`sSxIbY(kgq=A;|;e4vChwDzj7w82Zxz_-err}@6YpXb!tfYT0j)HpFWnxYY4c-^INMG`AWQn?=w%io@TpxoWEiM-$&ZzQoiE5>;SbtsRG}RwmXq;Sk#JqQM7>SW}ffJ`Q2jjcpbV@-7GsVbNfZx_fb2Z3fC=t7WLD*$89g=&zsKo-{RHmpIX0%@)KTBJ<XTP@qO+Om3(n~Kh@Jbw>9~OaU<EE8Nl_-*v##m_TYAUkKsDj@uhtA<;`63d+p`tW?x>X+Ot&hg|7q8_sCjb@O(C8f9yIMulD*Z&)1}?+)mbRUT?4aah;>T-A(?|J$%2Le3<8bW>xlY_u}V=mnZvc19E6yggezu+zR09!XYc0*7LS*)KBxfdz5bpY@0>>sdt{Q>+<!epVk%!caXp8KJ`;Q8_oG$mu#o=2G*kIuQFp5*P-%U@<qWVuBY2Y@-2zOIX|lp)zk8X>tGnugZ=s{*YnsVKJUi2nbc2*0$!hPqj~*@-XdT8-G}OF%{<8U3>(k>yZwCs|7ji9bM0XA)rew#uB0Sz{-*O5^5>*b-L$$-xNZ@Pw^2J?yr^#4+__x0^dGnKeD&n}%w>OS$2{*v2DM{xrRRnD&J1opwt70{M-Alr!_w>2zM8jp4f&^o__<rLkk{dk-t6OkVt8iHb?B0?n*8{dJdY>yxIcrP$ybwmbA2|C<No;8QcKRGI;}Rhqxz(f9}vdxPhG#{{2zwL@%44LbpAunX!4gw^84BPW1Js$D)XfDFFc}rvCpBjk9_l@U8Q`@rw?DJQ&LL#>Q_EAF6D~G<2vjSZ7SouhV;ldQyKjfHzQI^WsPe`P1RIJ9kk!QSDVVHoBD7O`T9C5v%=Sy%9t1Pg2U|V=22->J>68syj$D9$S{?)PNv-7YAR!0*`8b5Ol7UZ4TpA+>aIs?R>!Q8<9&bqs<U#l>3H4suD%V-q4VhP4}J}Exj&`vOTyWGFRAXns(S9)$6ES6Y}q$HkLRoOeOn3iJ3zkfK5xB0<{)2ZrJpb6E9QJUPWODYe0P?7{qs}=1%FPed;VGr=M<Ej$M?@`?f8*GYG42UaIwK5@^$Yg!k9q5{{2UJns&J4`h5SsWcmG%BjoGeyR05Vj?(#c?{8+~Wb*azdxq$h$LPE6y;OV@e4M`P-eX1b2=evsy-L&s&ey*uuM0Xs`MURQaqb_y&UE_)i=heEQMbR)9t`1r>-HmJiN?Ne|Dt(D(0BcQM~PX&zHWbHcFbpAx1UmfyTR@1_Fo3qyX@=sYv%OF?CbV-qPQacUB4ex)4bT%?;nSG^Z9lAP3;$7_I3MH>+;d;>-Mv%{Vw)(`(I1JH9oIyzpPGq&c1GcEgCoE^XvBGmLM;#i*EmJX*-&I-R}T@`ZJt9{0<OW>Q|4L5i4h_mE|K}h|0oI#733)$wQj*^IpsT$s?}KfA^C|2fzRKCy$-BKJ2i?9)#pvXeKxpybB>Y2f7WM1I~tS0ZYvQXM?k#>0qgw!CBy~2+13upMf`k*Fir8uLG}zt^%(GuY@iGuLLheNL~b843;_{ya+rGAvpy)2Q2jya0+-9Lh=mgOt93c;2Gd)&?(?);6#MviO@-4sqx^6;0XxHanSMLIB+a91}t?9I2Ig@kUSJR1T3`=cqlj&A-N~CD_ClKa8Gatgyfb`Z*WVn5!x7R1UG^<05<~Hh1Lew1=m1Gt^}<GmRb{B30x8C0G3)EToG&!tqQgWS3pR%gH{IHfd%v<@!=!69JC6!JhU3L3Rr3#a5b<a)Btt_H$+Ho25k;*25t@Y2TSb;ZVe8E_67%ndqD?-dw~Z*M}r4}qoCu!QQ)!A$>6cz1cc-y=yY%rI2k${oD5c>bHOTjA#?$FA$SQi6}$wz0=gV5bv1YecnvfSyav1;A$cQo6L=%o0^JUlx)&^UH@LGcI@zKXLb4Au2<!v)wM84K0u2Hy;Qk27eW9JeeZj%d&fs8hh%E-#qMt3gAS9chA>a_?n-G%ypsm1uU=M`kCQu)66R<nf7wishT4Kyi5t6-Z(E{2I+6LSX+zqOLyMYHn`-2C9M<OH-hxP>z2S-AK!I9vPp&{Up!4c4Y;0W+A=m79A@Caxacm#NqkiYx0hC{=^;ou$!$=#s?zymOs-4T-8A|wYuO<)t|F90Fg6Y2r>1iK(4*Ml|z*8@92-N8;^XJ}KfGuRdC1$G737a!)nK0>maEkZ-e**TW~Pye#|@KNPWx70td^hcI{?JIfY3tL-%z66Gb*vsdJ?Ezp%5AcJsm*U@U@A$m'

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
