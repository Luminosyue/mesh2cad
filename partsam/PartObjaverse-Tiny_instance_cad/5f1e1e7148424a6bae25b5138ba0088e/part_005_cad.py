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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5f1e1e7148424a6bae25b5138ba0088e/part_005.stl', 'relative_path': '5f1e1e7148424a6bae25b5138ba0088e/part_005.stl', 'source_sha256': 'cfc3c26cbc31125368a7ce0efb390efdc8a6cd88ee7eed2ffd2883094ddcd1c8', 'input_faces': 352, 'input_vertices': 291, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.05760375037789345, -0.11181987822055817, -0.25220829248428345], [0.23234112560749054, -0.012692581862211227, 0.2547709345817566]]}
GEOMETRY_BASE85 = 'c$}qL33N_Z*FG_eB&LWt-h?*Vnp@f`_4=u5gU0mLQ1beSd8(jh7uAT0n$-|)f*3+fp+r*GOe#{!XKL#;G)3`IV~X^@=RD7id#&$Z>tFw$wf5T2e(t{e?z7K6LqtS)!9sxoKOti1WuMMRD+?jTPXvn5Q6okU=p7YZXXx;;KBAQ3<&UN3x9i+CqN|S>EyjoSiHhz$BCN41tV!Q@!fLs~`VJd0azwA8k;6vxiIRM)UW22fOg_4Qui;UqU9-Wv^=rA_e65yiqU-<o<7=kiYC36CGgG^VblJJr)Y@k)vZd`g6r*@8xtZcc_xBaA$6bYgml``HuNNx>|FJg}?^ztAcq2RSgtT2z_YkL%FZe~d;M2ONDF0SfQYG&hyh8CtpVTdipO*NY^6&OpruyE3or)LwFvYv$BNZ>E@7rR}-y1YS@y6Fpw<;aq4sm|2dQADHgZCcsQ~rj32gMtw!CT*TZ{T-tfVbki2QYro_Z_@v80sdfyzhvk)#(bpGx@NBh!fu8NA>=I_nmpZ-VXdA@cP7$k<XrB<X^+>@E3npRJ^Dfj`%T!5I?vf{G-}nyhVL6zu9##-j;10`G}Odh_fOn)t<k18S*y{IeBe3>SLS-pWi=qS)UKer#i-42jdmpz~_(GALBI+J9)2$ak<Zxcf@xGwnRNII^%nrA%88S_-@r-BZsFce*O9^_5M>QZ<O#muJ{1o-S%<0u8&cDsI>*JPj>HC<JvOv2ld@9;Jvx~(~!?_6-P`2?;dnZ`Mdu9TYcAvb@JlQ4i(2(2ws#KyG!xAJ_euSjIW>jK*iB^JM(cjX^!=hMt=OS7;oYQm5*`B8Q+K-2>+U|DBf_rzDLF1wZg$$>(S!fJ)HhpWO<dRHW<A7?UCuq|H@>Qr<md7J+m94&ilcOziz91v^=aAi_h;Li~rXvj(O2C(1+SN@LI}4<X>bt=H*xL-hfcdZ?SDyzmHzxTVcPlcxxZCc;l%vzPEKHRR@vh%ty>a|BEuOI>zO0Kf=N1_bquXgnVON)yI7r^X2Y6caO?5cC-4fE9fBjzTm~x11e7uz83Q`5WK$Yg8Hu4_ygY^L;nIzR2+BLO!WU`@a~%5Dqgf2h(6K4Ym0UC+nw>Mp6;*6rwl^=L7C{2nc!VtPDP*33PAmrf;SFp_-@HB(EkQ_&y63Izj192@;|^lR|X)TZ3hr1oBo~ltM9rRdoix({O<iom8bA_MVu1zkY`Rd=B4{(tlu}m>)L4a&-T;khvDFjGGAi8PM=Z!p092h_W0Tq#Mk4%Tk*ALUeqB0ycOTo8Sy>q!CUj_UW9qnw}a20m-C#L@4#F0;yR3ZaqZ%FIWNZ038;?&-pbz?#r)4RKI`dfa8UWXu8?Q{c&np-JlB{%`^Q*<{&D}w?{eN<|2~E~KVW^Vd5^-pd!I5N&b#aSXzW)dZyWY`*E2BhdJuVQe#>Hh^^_aP_otxkDxb)mht=~_;PsMIa84aLen|0`z-yt$mA@8S;zv6#Iz32s@Yl(A+>SV{x*WIjdiT&IJMX;<-rY1E{W-MJF*S}{e%J2|`X_EH@+^H5{;yu$qWJPP@ZB=tJvG*<eN|gn;fRV~mi`6)v0BB?S)Zx+s`Q_HNzIpAELZ-XVDQG1V6|^(x$w7mk+bx>|HQkp5Z~fmVT?aI5&Ox*;#qcHlxw-p!PjG)BF&J$-+Tve%nC@h^ZI-AFBFe;q>Xj(;z9g!JMV1*Ui)(f^55ED<*7GkoWO$UhrZiT=hpOJ7YYB;u|L>(<HM}g4*nx&KBCP<)c+Ik-Y36dTs7(`UXNgXy6D@KzyFOaJ1?$>r#Sc?HywTGzSKnZryj}gCOlDf)=DJfyM38wXe{Ubk?JegK=68QL@N6Ku^O*#@mBxWipjR~V%*Fm2S1GYcdUqU6~3k7c%m7n;ZDr^7!7?DOaGcZa38LH8+G{lrlZfbW~)xvd8^OGM@1aG(5@ud{ap)gI@eLp;Ny1Q2nhMs!SA7e%s9+rvKRF!`G>P^!!xlSOF4Nh?g;#Y!F#@63_fK8{6om!IgfR^@+(yzZwv75-}|jm@$01>RsK`KYaKpDohLN_KaFwz*#iD8vK8-L1m2sOrTmS$MHTOfr+<7d_`Oe1|BcMQ?Zx$q@BA+6PhQL(v{}VZS%QApNq^t_s6!(kj4O@#C;6y+v{_G(&k^QRtv>SHbP@TVX8g~es`V>&UqPRE$?G|4AJC%uBcE%mL&YGKr<NY6c-JHP7yl4>&RU9fTJjeB!=7wVb?#aaaRP7g{@Vci#&PtyryBWD1F`>nhW_+6VVrrxu<q(5pbq1~i?Fy&D$c9B!Ea`qcJYf8AH53u;geh3SC3)d^Zc+*a~VHnx$+kwtFcdhco%U>w_Tw8hcrh%<h_?eQU9#{2UVPQ;I%<J)p)fXfr|I^B40W+PWi9PQT2DNAwN7<?T5z3v&g6PJ@9k$VwL~780?3w!F#ikRQ_7#*#jz0PM)*>vmUE{@Qx{}?h*O>>L~83_uAmz=erN<x17KFuBS>{+*9iB2Y(s$aa99v)kh0Sz&TYPe14se>8RV=^yhvk5_tZSx6WmY_cjLaxp*D>{L{<mhY0e?YmooU{aDxS8K3)-k%seE|CGFSE=0}v!OrKO3*<c>#<%wQUe~kieEvR9UhmELEyK5}IC-(?^S+E<@geHg{!8p9{lVwo2kP)XFq;0>IUcql)6VCg<K*>8%#-J}7V4X2=dJVF;=M88^Uv$X^BsKtc}-rQPk-xt+&tF7Tj#aKdls~H^p&{8zFNpUd)!1Fj-n2pC5+E=+`W+J_%i1_YV#9M*!lc(guG{&vz}UfVfZJ!l>a!K?-uV3--h{(<G!(qar{<d{XPyw{%h%P-3L1GKCq5;>lclAi7bTmwf-f32KHf33dhxnb$DYs>afGPF5Lc2vF;3xHyHoUBU+!t{;;3xk@o>HoA&{Wx9$Voc<z(WzYkdaNzO~Vc{uk+jlj4runyL_Jgy<mkzX07_9W!<s20}Ut(W}ccwUpwKgY@I_vz33t>(W2b<SfQo-M+-9+bwuTA&^3->@V6BU7<13bk{LSKG+@e<kqNeO`Nm_j&Txecs~rcfe~=xoZ8oOD)8_^zH<n`>nQfI`W*-6@8_xM8BOohyAwNH{h>c!~E9c{7&)7viFrHs$-wrJqW)CpTDb1+c-NC{)fmPehcUF#Pd9_!MhK{sQAXG=hb(;$H`m2FH~QPJWnzX&rPi!&P~@P`qvZcymq(m4gNRq;>;A}IrS&Z`(4IK|3mG2hHC}-?H>Kto<*FT#^|3%;H~pcJSdCv?kRX(KZSj-SPaJdoN*GLW4w($xQF-+=D!<7sQ99$5Bi}Dc<bI}6vMsCRSmqm^&&N1chng8*QCESj|(Q_+<%S!yibbTm#}_olW+MP@xyT+bJbx!yjK{1?Lr;iVSL_0jLQiQKL4ID6ZZtqyWp*Rf_4M<1kWdoQ>VjHl~3>%_(y<uWuIhyHlfZP=+FCub`bXmZ#2I<(2M(C{b|@wCU9KMs;^Rf%Q*N?qQ7;2&OVHJpGLlG62|rON{nj}zsviH`xx&hD+W9IT+|A|I!y+z$M!=#->!-I(#JdVpMw1L#0ic%yW8OY=AF38u`aYWSQnlds~vr43`QTi<|ZMZ>OJPDe0qM4@3u*Ue|p)uDo*Nq`0kQD&N{^4_XYinbO*0B<?j)(<ayuL{0qSU8}Q=uKKO3@eZ-%W?pW{QIo7*(DR}MEP?eAPr3vO`S-Nu{NaQ{cPoDQ=_hH_XkET27pp|$J{gajMSdZ?CynmhnuWx;X{A)Z%{9n=?{pOy!5%s*9?pTjnTdYU@I{9-gk<Y$|ILCc59DV2>I~9FWD8o6wF3hi|WQJqCXq$PjCU315BjA9_-&G2{ery)<ACiIkR|4;eS_Zyj64v!A8IJYkZh`fs*CK!7DemWQ6u@}vW;pv~2l~X-F~hNr#6YYgy&K~UpM&rA+jDGhgyXM(-H*>YAxfLjl;R>#^zCK)6QFt^M85vde*zrv*8l2HfNwTz@c;c2;6O8nNZF2*bU9R0rkHZbl%b|<Gv%MA9Hkyfe3bYMbuZ#G#A($1h|`GAQh!N&me`;kN<5S~NIaN%rBl8qH<)-d^$z0E#8at{5Kkrkf_f+M7sNxT_Yw~w9z>l%Jk6BDrc7jxvR<dCClH?^PND8WoI<>tx;OD|;?2}Oi8mAfL_LvsB6E<~!@M#mzmoG1M^mQ~M-vaAzDO)(g(=gCr_<L%J&bxf@gP2%Mm>yp3g>Gu?TPdqL_CDLr>)LCIS)NKersNObKZKhUe-MJ;5_$WeXV()AYSyw1m+@pDUvx2v~jZEM(|nWOWbyHQvX7{hxQ0ce;X(DS?V<LqPGn`-%k7s^&#<M-ASBIeM-FObBVvFP9grDcn9@v;vK|Cs5cWIA>K)m_$Oki_fjN2Oe}Q<^*-^UuOznmNa}Oc`-oGiH&HH<TS0p|V@~5cQV%2EM|_TYI`MSAEAcK<Hkk4q^(7n5rY-d`8$L)|zI%ec2l;FZ_0PmopS0l%v`?Gz1G%4xFEEZ3D@$NcJWhRvSn7Y-@K)N=|3~@`H)Xv*KS{mEhWFDRE3p6erT&aq>d7`dinjFE=-Y?S##2wS;W4zO?ry`M)9%BV(pNWSwJAx&F|?(gK`i;N$Vohow!~4iLwtm&YDzG5D6!O)Y`6+-sr`wiE=er4%jQ#p&t-f+#+Epcw#21qKQ;6Cw<&qlzY$CR9yy5%`oNa>A?>oJR4}D7aS&~ZtI?La46)=(lashSZHX(=o@>TlY09_M%WXKGw#2JwOT3o0e0L_fJl3}y<te!*rW7*mXVlUzMqS+J1(vle&YHT2<vYKda$f)!@PRGy1KJYbq%HB^wB>yG`rw<sw(m>)H+}s%caq!4Z=Dyw_i0P)rJZTYI{KU^j-nn%e3kFX+^*8^ck-FElNfU&MJE@)+J#VLKL)Ut<v6EO?ur*&0DGVUpGoeT`OL@ExdQTBfJ@?9@lsZET=$8eQ6~^TBYwhoQm>(%V8im+U)1tDe^G+@PB7>73G)cx*n;`qHRf1>;|cJ2!9C{~DzopU&vV+6zfCF2=Q*@5Q*N_g*AlN{-igdtN+Q3J$mhA#w}}_hUP`^hh7)N^J%?EO$MgAOK3hb+hFI!lHvA3k#f&3;XY<)C>aT4$fwt6fHoSoLY{rzn^Et2csAFw-2JQKLe>L#}+C_Y@j(;N#p<RS~nzW0u_sS5<{tP0%C176{=-EH1Z`kl%+EU*lmi`a<{E;bzeO}CUVeVmtxsOTwn9l_L{;=U3+EU*ke$2S?`4v-=O*tU2mnGYJCfU|Y$&8WAcXFuj5En9~peYTh3lK|rgU_WdOkC8I60(-m()Ob+MqHZOm$-zDFHXCvDP>KmK<!KHOWz9gDaYsXy~=!7>hi>rFGEi1K;l5YZ{c#ZEAZW_)Rk>mK6{(`UE)`S{8d$mcc|Ya?q*6`Q(94fMEqZ-G&SW@>dwUS-5Pvf>RQCLXjh{&Aoqcg|EEESj@0dm8_+M5Qiog}+BGSS$+a`(JyV)dBFHtS->a0`<Z9CnrZgh=z9}tC`GmR)aU=Rwr@T&1;xO7$zeU{Aln+hmN*zuteO{xV)OBsxMO*6n#H~&F*pxQZ9f+Hl(%h6z)c+u^WJ)Phf~W&*xFl_<{cTu2t4LjmSV|T8`O~i=V^yJF6>=7q&+1XvCpMS4`thgTkiJ!jt@sV;8xihPAh6*7^k1l7{Aen${XbN{{HF7tUF>fbF+ZOFk1!G8h2<JIH-rM}g4<knf%tD&>wVD'

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
