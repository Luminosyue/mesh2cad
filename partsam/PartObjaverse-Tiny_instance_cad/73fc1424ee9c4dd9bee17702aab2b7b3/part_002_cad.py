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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/73fc1424ee9c4dd9bee17702aab2b7b3/part_002.stl', 'relative_path': '73fc1424ee9c4dd9bee17702aab2b7b3/part_002.stl', 'source_sha256': '47a98f2c8a0c0c6a7618461ac87006562a2d7b73a08ae3476335223d0631a4f0', 'input_faces': 296, 'input_vertices': 182, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.12526634335517883, -0.2262578308582306, -0.14609405398368835], [0.4571632742881775, 0.22625774145126343, 0.2628520429134369]]}
GEOMETRY_BASE85 = 'c$}r02UJzpn#Z>a(Wt0VVvo6Mkf7MG`z%+*20}22J?d2iY!3`rz<Oc@)TqRQsPUpvnu@V^PlyR>ED^gQFIV$kqNzULBr!TMbN2uHGaP2ktTk(fwZ8TLoj?12XYX&9b1sXB&<b9@N`4wEb8AlD)h{TeqpI>%Go#|CPl}96Xcapxshp|-U;mWod*MUEB1V)`Gu0gb2~i1=@%~*M{@tQG`v*GwqvPVI$B&C08y7zzO8foBO-+ch{Dg_)rbSuTueR+R6zFId5a^ia_&@$swz}XvR>?fA`{HxY>}iR6c>QDg+Oy*GqwueWoz}kdwY~fFwQ=$IA^10QKhnPH8l0uC&6ZE(_ooiPH$R_yLSH-6+vVf;Pn%2o3f~=p|9g+!(1nX|U-eew?fCrQle^%*ShWECsgipT*AMo<SC<=qrhU)wxYOuoP<|dhH)c0{cj%K-xL>Q~@YRDV7qstq^5aQ;?G8+WZ(a>YduLoPjNkadJI|iq2rCvp<XA5J>xa-!SCdbU<NAGH_-4Xn<TrBm;Jzv?JICH1*SB9uo<4`Op%s2bd-s<I(cajxO8l6f7_ZC!5%Rk#1dIRdtn@$TM~qi(>X2<8m+9B*BYo}o!zbI`AN9vE+}G2uT9*C3u9*gWca2|mqOM(z6`~F+f0A)cuek&5!xAuF^XFl>ugm+=2k`$sO6sum5$<bVJ^<gj{SNYYzK=tljdSxqu;({_3P&Di)9RAvg_qC5ukxp?w~$<!|7JT-2i35Sw6C>5{0qJxqy3Xq+}GXl*KPKBaeV2*di7*@#NRj``PH4i@LkW&!#BI{mGxP7)B*Ue?c(2_at7o2=oi$%G26_<{eOr-e~iVqWj|!p%Cz_2bHA?CC-v4=w2v-E9>-)~*;h@@!#9Gi!*`CpEcFRbk@gj{kjMRMC)C0GG6=rPT!Vf(&%J{6@41_@1%98?=#TjihwMY2f$*Iz)+4_;`2_N~>fPUDuY;q5m&|+I#*Mg-Cs*3Hco+N8(JgJGy+1DR!LpBz<)y>_s>(UkVaT7TgOT48zA@u_w0HV>P&eap+6HL<vvO{Hz2zh6UkC9&xn59a-G=X4kA5zz{|V-6LJ{g|1fG7+eqYa`ak76OZd-%)FFlcZF4!gWVhn=syz7*6Z0l;AKkkbSRw3WTm#}`^4=Ty|v&8i-#<$iFb#}zQb{Os2k6sBas)qiUqY_a!(^YjT{4LL<Zixl5e_inlk?;3nIj{UX6v)1KYT);kyCRQsX+G*>PW(~)zcdrS`cUcr1?PO^S+qj-U5EY1qkgV28ST?<BER$2a9LLaD^G+DcOs9YNeb$t(yxWs^LSdUllG3(mdLwx5b9v`oN-w8dz;><d+r&@|IG|J2R<*1M!ScF(jWhwvflPon<DKM>gEY<C+*{pEQWvYXQ_kFMyZc?<Vxi2^#FN{nxBeaSVPwLcO5@QU5+}iUL1S&%X8xIg{X@eGZMb5eS!3ER_(L0?v9^=U;l=j7po(Y$C%!FC;HW86vnCMK9hY_;GczY%ny-$KC8Fn@%bhj?Lt?=SAIXpxjz0b?&}WqoRM{NQs(v1ec7)g|B!VMRuTCf!|Gt2st<3;IzByS584-A$V0zhYW6Ag@WjvHkE|)<{mlj6oVleC`~1h6a;_vif^X#g3(phtjYRl{BLwHEdX^^Z$X#FR+I_b8;VUG6#?3v*>y<0#VBG-hS69Pjd(r<sA?UA}{yf^N3DMGzcc#cViq^e@b(FXbd0lTjJ!hXUqxn}jFO0P>pGW(>eyh-rc7AdmuT6w+&XM!Tm@^pdRbbJ1`#h=&NvY`X=KJtHIi3q>zv_F;uQMYI&rziYJno^}wfJKn{Oca^PX)_;FV~ZLO}#JAb+2EM$GK|de)Q+F+I%kF!~2NJ?4At0TXexbFKR~c66Eo|D$mP7SLM98mVX)Tj5-(5&--<;9-Kd|6MuIgeC3sc`?_PR$aCOOn)n$5<oP^d{w3rc^&5O6Ki-Y|h7=^hAJYcES2G`fiadwBaqaoxnfT9Lm44?Z%6O(N$NkkqUz}$~?DrYSJAd0{dp(_xhwngtZeN3Mwn{#a{*3UGdNphDxvZb%%Vhoj4fE}qcNe~==UC)114FSM9M4|6f_4$#4MqN(tdqzSz5Gg<{jz$kJnz+-EB5_j)(OXR-H~)c^3<)Bfc1Ig&@p`e^d0fd)b99v)neH%W50%PbZ&upG)9)kx^m6<P1-yEIT!h#i$9Eh&;DKf8m&g4UG6S<p4V4J_I+oLIfVBBXX`HTmAhd-=)S%<kBkc4#P7V!CF?v0{qZ~(QB-Ch&6<e$aUG76_NPzE{Ki~dg8M8;DYCB<qxRRBFEcnz{Jjgtp^lFl%X`+}3dB$R0{h*4DiPyyw*FN7<fnMPsZ*C`pnd(P;=8iK(2q-xWk23iS7lrwBhc?v;c~7It0(^b2Qe7`ca7vZxvi!6b30=_IDMaCe;UPo#UJxmjK{s8NcKbWF!;vTS$MDXtSv9=spAs(&d|@~`5JZxzLA+CdAvTxb5#ZA9D;v;r}%}nW!;W2<vr26K>UcLk;uQRfy~Q^D{|l733#7yttpcA`sO#%zR?xb%@dh^6!i(X58pMpBG$jN8TW0^$MD^kU&p>v1&ySiv(z>GzWthMn7`DA^4v+CBL0aKtT)$k?-Lkj+ws@!`$hfR>`eFxE3Qi(PYV3aAFjvs!haXPt-L>~vv1EqKUz6%*!QV=d~iPcliuQntn&-Wvj3$%My;;!9X0P_9lFoUx$R66U!|49^GMapLp@v_V&J>V`O5p;)OGS+H7i!y^ZZdoDYEWHErefk?is#O(mufJrmT}ZtOsZBYgi}l8|gRg^XLj_iRX?dFc-cjH2WOprKmg3AM@aG_{QkR_`c#^Q!MA(p<1_)FZ-g5YiB3<9+1`@zIxac&nfdp2A=!o>Y?IK`*tSkp=Qc^Kw30>=fGNck1?<Iz<KKYcHJ#|-JE|`J&x;To8fyhuYH2?MkQmNn7NnWn?dsZ%K7F&<Z<)~xQ+W%Ivb6;c=tGh@f_(U{!hy@kZ0wFZSXt3ciX-W)msYZv#OXW?f<a}^>w$E_jJdoNAQjIo$x)?IdO^`{ofIM2YPQl>ghVyTiz?LWZWsU?}p6VjDAnggs<{et<}Ec)(|--1JB&CuYbcGjrOW>p|n2~BHtHhpFn=MdT__S?~L2+w;=z|&+gdg*SOLI=ee{0;V+=(QGD+*-`*_m8(WXUcSJ>^&SvKO@LeOmfp5$mkLRXi$WfdR=7Uzn&|hAV@6}#a<-Mo%_G0^dsiSqU-_3q^i_6S=|1Ts@K<_Wh%wy!;!#yL){55C%4fTern$;C6o>#sqdYtV~Ioi}eCHmk0DQ8mq|J9#zg1U74|Nbe*+v>y1R+MLGevaCXtksKLo?4FTMJ`8H)C%M(R_MPM>EY@U)w1FRhUV%F%|6tcWFPYL)N17C$(5*;$(6_zt$5Lj`s9k_O8l(WM%4P`M&#zySIN!E{?x`~tuK+aHY5MViq2N_U})~f(A<e*(c=uDwjc+PJ5oE5JMpucgRSUeMQ?^?Cqr`=YIkxMa!b}<*S#&ZCAlTrv}K>W@jk)iK8$W`*NuJZ&gjI?*5W-{P}`E*vW@1ZR=i?GJ!)NYJ#rOBUE5q%=6qJB{~|-PgZc{DL9Rh<K(0!yO>ID~O|HYx+>p_L{cXTpO<8kY>s}1aJsFz2QoE45k^@=u>a2HldM&A4$a?*>Rx;n6$sMU}$Q{W6)F!HQ{b;Vq&|Ho6ti~EwqhC_<CLC82=4#4l!y2^Vy&JMVT3b<DlUuXjn)P02%z9TP*I+c}{M6_Cy-IbE9c-gH$O=DIx;HhK?0wBXtf3F<=R-e`;m6whF;~f41aYpkwkP+ZcA&N=cOW-oX!d7lZcYs%2eGf3XIk;L74xZoCC?`>qfR3)Bd?$)kXMjbQs<Ial2aI(mss(J6(g;1S&>McK^;k+L5`&kBgc~Cs3XX6<ap{>ay&VSp*hNmH>u&&vE*>_K<WtcK=J_UF!BI$2z4ZRB*z)T(EJ)h^C*VqF;o|M40)2RMw1wtXIt?ubqzI<yoS7<I)l8Pynz}^-auYQjU%rkucgM5*OFILlgO*ds~DQ+QKQK7$P;aIFp;78Eh~moU#GrFew`dj4JU_^`%wpy`;q%n2ax-c`%^>6A)Fh{L#&u=MFcgP96=sL9Zw!a4x^4Ehmi+UCy)n|hcYzBSh0}0h&qA1h`g9Oj=Y$hOdU^7CNHN(lb4fIsgud?QI}FDlb4dGQiqVIk|UL@;Yijll77iLA7ZO#1i3%CFLjV@UIuaA2C;S}^BBf?4rA>~=3Vpa)S;?$ooF7;&^($NLmo|@VypWUhURyyNTa4x7n0M-o2ZM(o5)+Ki^*Hb+o;LpZRAYqa&jg)gPKY%nJ3LVtk`eG9xJk`d#U@$d&&E#2g&=$`P2jCeDW^phvZ%4oea&nR(wFsqJBuuBIi&KkaNhpsRzls$$8ZM<oz6H9z%1<`KI|@hUSgbJ>-pKx2;BQhUU$z<!07%GyM!kHs>Lmbu5{ey_~nbtYgVM?&Cb~V;xK8UGpaDE>*ftG^bN{s?v3(IgO$DeQGZGee!nO9BgN3-lF8})w-Jcfhs+pHLs;+snYXY^EzsdDn0)-Z=mj0rOyk^>#2F<JkE{gSys%kVgW<5!O%RNI*S|;TCTirh5zYa4N89u{ROVfKOX$oPnP{!YyadWE7yO1$&Cp0*53=QFN)>y;xoyiul@ruJPq3'

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
