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

PART_NAME = 'part_021'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8da95b178bc641d892f296e42c0ed8a0/part_021.stl', 'relative_path': '8da95b178bc641d892f296e42c0ed8a0/part_021.stl', 'source_sha256': '04a35ddedf38eadc0c6114c3a77057f653451e558ba7a43c3daad1dd70c60dd2', 'input_faces': 416, 'input_vertices': 231, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.10112559795379639, 0.2695373296737671, -0.07859188318252563], [0.26032137870788574, 0.4988306760787964, 0.07791459560394287]]}
GEOMETRY_BASE85 = 'c$}r033L=i9)}wVa?2qihlGG=f{BDPBI**k!=WRR)qv;(l1Km{gb<DZHkSxOf`VK@GJqh5M^FMmf;}on60QJ2K@JBM-Cf;%=<fRVba$%z>&aAC?|b`p<NN!4`Mt_acU5(DcRf7AYDcutte*~A%7(+eV_IsOs76`~EjK+oCv$xI^e$7fX4lf1nz{I~x%#o>5uTJ<TCSECot8d*e0Fr7sOX0?dPm1aMQ2RS&dE-l^4!$yv~-aVN}W7CJ(y3QkeZbq{5__7k8W{MJvzrl&5QaUe;SBmc=qdqeS^?jC!Q75Hbm|-!g9ZzC;aq5->_W!!|%_#wNJEj+UqBG9x?Nj-<>n_K)!Cc<(@Y4&F@Q^cvQ*<{Iu3^%hS58HQTq^WaZUm)n?wcL!RN57q^=w=!<{wn3Pv-ea&#oZ(e^@&|6Ys=Gt3xt=t=*W4PrvW2c#azqIO@bewIPZ!z5R-Fto3-^U!6J|~dyis6=5onK}$ceIt;#~JZXp%Ipcj=$3n8wCTSO0D*NZ@p$x&zfYo<=)J6seO~~U%IxpbJ}~GT`+U~kEvGf*CrZnx&GJj=I5vWT|TcN-PRaxdD)Ar&GBkjyIelbb_)%+e0`xVwGSPqqrIIw+UvFRt=w1myy2GXYf{bj_1ajUQ}_5)E8me}xaEmO-thLJe&`yrz;Mg`!(X)KN22vPNhMaUm8BVOxt=-J{QUm?<l~I`dA{M6>p$h0oSZBlr<OF&aLc^|=LkmqbB6rAz8!N6x4h}LndW@>+X{JHJY~xbw>&0gnbh7M7iW7rcecM#ZRLsIc@4K*^Ct`XzsWaqzi;c+@b*e>w;!=d9+z3eml<w(aph98{q^nT(skXm)tiP}zWKm5vwiym^0<_jzht=O+TbPO?L+5P+-Zj4mN)H?ZH`xigVy&ZK6TOhoQSc8Tb}r{C%nD?-R1O;+&+|Rj`nuHaXd=S@%UaoBG0QKYnK>qx!z*2dH%;PSh>B9T^s5%!t&7icBQ(={Jrp!JP*6BTx7WA6B;fwk3Z|G+z-WdvkkZ0TW?Bu`%pjl<@PoGX0_MjzqZEl^B=hG;!_N_T<bSfF!24q<UGnV#c<2DqzUHn?5R^B^>bCJdA%!n*OI*O_Mv&g`k>_Y`jFh%%I$Tyx_q7Cmj9*hI`jKpi>#3P?PjdGJ}7xr`poe5HS;P?YG2dOv@hsYA@#$mE7tsX<~J{z^G(0)QR_JEb*A+B0>dp|6_GEsx7QhGdpoDS|I{Gsd+l{#{f8?Jx4gXf3bTExr$V}}S>KeL_05+sszSOhSbvn9^~W0+Qz6asS>KuKiIV%$&Gp3BW0E{i{J&WDBWHedt{&b#G*9gNsWaz(s+H%+<L<ZSr;;aH^V7~l<6b4V59Q2f-?X{%xJTv8Hr#SOE7xq_yu!V`GpD_`tjhKHm7L?ZbLa6ZImfSizHselJ9qZ8lGD$DZNGILcO|#SeZ-IM^U9gq^Qz;YUFWTm+w*q+FRs^xl5<@IW<*rFU8hRUbr;GV*Qt`**Y%&8R7&H^x}oIuy7A+^mD2dKjww0on4LS<F(qdm^TzkKj?=NODmm+F)TO?a(mb)(d1r2~^W@4p@61`}z3T_c{lI-k$+_<YMvaqm?rTcUeNF!*Q|>qJvr5i=*3O;xStaK_8~DwnN@<>R-&b<(`~JgIt=#ckVdu{03jObTrF32J+@j<>w<OM4A)gn|T}sY#mz_JGyOdmWw0AsrDY^aJm6l&AU8g)}Dml-YcJ6%6RB}GwyS2zVFUNDQlJnfFC+xDm*YRAf<g7n>(SG^7cy3p6p4$V<O67Hf^-9TEuR^)wy+g^J?H%tOO3v{_Ej=U8L;JnSncMG8t!~QmiuW=l=e<met#d*eN3M4zx1a0Co$r-O&U>Yv7kfgU=hl0!lJlNx=g#+BCFea?8$aNLG%noll-z!<uye<Iy^=fHJKyV-ocH=bqv6))IQJ!-Ir|ccW3wISW$k+?Ir|>|)&=r;v9F@!?5l)w$3Bdb(?0RG@2%XiFJ$M=eIftx$dl4}vG1hh>^lYik#kbIuG!a8a`v_SrwioIVc$&2**EizYII6EPJ3U@nX@maPueBt?E5LXz3<oO@+s*!*;iC@_7!~xHl3Do_AQm1eM_zFt}64mocpNc%04Q&vX4qG?W206UFJm*mt!^YYq07E|Cf;(w#BU3?V$S>b7s%~YKysNw}k(9i@BaAw!$^70c?slz?;K1cyoLZ{53uZFM<Vl5q=(?z|Z5C;RXCMeidHAuj1F>7x*>&3j7Sef>*<ncs1_he8u@UhV}8rcr(}#Z-%#px8rT`r{G}xDSQ?5;XaN*cto)3@cs4h`miouA8!bo;0^KH`5f{0x55T^1IFxDO89M*@ZN9`-Wz`h7U4yV**lc*&*5eKbNow6_;q*{zm9(eui;<e0eA(!!k7gp;TNF~zlgs}34ag{#s||+55gw6__-xmUsJ+w1nV1q{}$fBZ_wsjSR4Nq{|45=Uk=tw!P+0Ja<~t^gzv+3O8E1X@aHJusqkey6(3ItUkvx-i}B*H<0z(t9|_iJcn+51=kQ~2AAStq3U&N7I0x#u&iTxtgioS`KS>E62%p0T;_)yQkH@=F!XJR+@dxmSDB<aFF`kYugvIzmd^bFT@5Vn0>${IA;g!LvfT!ST{1ko`p2N@LRqz;Ig_pstcp1JktlxK1!Z%UE^C{u8;T(K6J`GO7r{QDZllT~X1SPyb9EkVFV_`fVi?^eMw};*E_V_*U0sJ1kGkgf|jNeZQPlD-q5}rv3pAQ$}^YP7aH@=&3-AoDpkP_~PmAD@_w3>M!yic%(1S<_rz|-&ra2~z@-v!^m1rOr8@War+4Zim<CHzx(3jY*84$tDp@iVXrKZAb)%W%P+_$T=La1;JMz9U#~!i{hfz7bym^YIn<OgI~#iBE;oaKSP7R6K<eJ`9e)hv9uG;g3?nd%^yAFZ^y8iwm~H@5b+-gx?9<<9Fh%;XQb3yaViv3*L`+z@sVQJt*Oiz$E+;JQ-%<$@mL!KK=qe7jDMq;%nfC_!|6e=*Qp2OQC_6;s@YC`~bcOzJc$-SHpSuYCI24!1M6Qa0osb9~G>JVH_NS$Kf%s4<3VeqJ$^FG&}(x2N&Su@I`PJz6gI09>xVf#oxnA;BmYJKMK#_NAZv0C-}$sUidyPxC7sdZ`W$B)$Nq<ZItj!l<+So;h({c_-FV@xB@?kuYxmi!KwHv+<ul8-WH~4HP7C{o55jP&9l1j#;~te^K37?5heUrl=)r<AH@ZG;fZ)pcsJe??+EX}JL0?xn%)xLi3_&ITjH%?2fP&?MG3zbM&tM5-C+;BJN_6Y{BigQ{y6>wOvazU$HEuzvG{a27oU#LfNSs>_;UC*z8qf*OYyb%dUya|kFSG!@OAj>a5erqz6|E!%kUgH8PCD9;V3*Ce@3fWJD#D0d+1va{p}&Q`~P9aM=%Z-j0qdNn6U8`-U@coYUY4&F-M*b*3e)L*Q~iGm<WezHFH(CJ-3D1b6$8;N_ZRiG~Ncc-{S?Rz^Cyk_-HsBAC315JHCFD@cUp#T(AXxAAT2XiQk1s!cMqg0v?HXh2!w9xEC(Mz4%i29xhmdFU3EANAVBvL-1o<a4&uce+zEM-@*&wHoOqu059Q!7w`@EEARyV3Z4rK@B+pumlB=@N8?%eNZ1eW$9RmSgb#ps;REn4FcOcX-@8!4pM_rhS$qjxiZ7*qmr%mDz(e>U`f&>-{8d<pzlyJf8}JSE*GfwGESQVu(l4_p;S=FVd?e>TkrJK(yWm|o&kVQ(&%j>{mS<S4TUylqPya-<=0_JB3erDVb^fKi?HK--8NtsAZ9;m6)e-wZ+AYEV#KZCyF{0YP0s7Xe4*'

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
