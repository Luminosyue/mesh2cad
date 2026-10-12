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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7c8bd48528554b3da47f2510287d78b4/part_002.stl', 'relative_path': '7c8bd48528554b3da47f2510287d78b4/part_002.stl', 'source_sha256': '47d75ca94ffc332ccce7a40960b07d92bd28adb02aedb1333c36bea1579fd69c', 'input_faces': 248, 'input_vertices': 277, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.05258263275027275, 0.23323704302310944, -0.0505196787416935], [0.13752977550029755, 0.4478275775909424, 0.16818062961101532]]}
GEOMETRY_BASE85 = 'c$}qL2UHf<wjNMyNEF3bg79O!0egwPF?q(W3C3s?V;l=8v7lnXf*DlQL~I}$tfOE7R1^ys3lo%(sEDGd5tIDEC=k23YS3uzIs4n>4!*p#-n#c+>sx2<@9f!UpMB~K`1LDS-c7;JOUZZDLqqE+ibPe#O_>=mZF<m{fRN^sr_6RxsuM4NrDgPcg9rExb5Ld~bG^p~gp8Ty-O1+NC9s2cQ=4~S@U-dEMok_WJZ)@%<a>^q7!n}(kny9Y1PI-yb^G>BZErVfY74XdhrcQ!1kL?UV!DiFP<XztC{&llDYCRzizVLN*^hXAV&*|vY89IAAl|!(cx6Y(J}MVGf<JeJc(d;r@}q<p+sJ>zN|%XWS??72$!SEq-hDmsM!7R5i9efdkbOeXb!yjR(>97{@>=5c2f@VKecszZ{vA^`l6}OCJklp_A^&P_P2$a`uJEsZOuVgV#0JURS8gZX)}s>f`j3y+O5V11H2iN**-iB>H;6YEhJjByv6I@-#}co+A5FaaRtUvoUTzyr{y&^c@#ucJ<X?FsD~kLi)<GU-FC*TZ<wv}I>mKk<Z4l>lpCyu42hWE8h^rKj7FUOOeeDOxPl$b=l~-r3AzsVAPH`H|ix*Rz{k_0n>2rX};Z2Cww{FJx?kr3t-h1IfvUmC667i3kWRjnhLB!i9en`A+!aU-2dw1fEf%B=qM&5no|E;_Q)Zbip<ay>!<oU}X#Ot$Dh}U|)hdexP2m3zzzNdUmx@8id-!Yu*$7Ea~KfW_*p6C^8Ri$`-`iSDu9xkSMY-;HBZt}Tjh~GZBT^U~U{S0vqe0Ivpt3x~xXY>7KcqLh-cC{z>PL{E6bBcJgT38ug*>!;8*X(ypD{qYUxkmjuSG5eU29|*D-sM;s{@x(0uU&6`Ri<C{wqv~N{gzs$-D|h8?v5rMvhudh{+K^`Mf<G0UNf9{Gw3GGE3-rm_x+nZt3z{$SAOqCyuDc=@#Z_t7x@0ocqvoQf`4V)%~a=wR2E_W7@IMFjHaCz`u@%QDdo+{4X<Gzs7U^`kU7Nvulc#H&LZO5u7drz<|jz+vnGPdhXatejdduW%9z!QVV{8f#4e-tYs|3|ubzk}Ua5P9_8;wjwI%fYE9*{;YC-&~>(s8bSWV9-9HYD`i6bd*#?DOeQ#&Hh3FnBn?{beKzxB6MKGnF3nE&<r6aVV|pk~yKCjNukm_IIs=~O?j75G>7AM^32G4xzmXXK&A(<9V=wef2yu6pN*H)bz7WaVGo-&F5Z@Kc<@uWE6?%G+zMKz<f|O?lHd+#=rQ+y#96ca%5#@WZhbSN{XZ&-Bj7!-eSeq|a-K`4+u{cxBzGEfimTea!Qs<A~p*k3sc!KSjUVuc39JN9Pc)eu#6*Y+at>RNCJsUaMLM@o(Nv@#yDjY^C<b??Aipm9Vb8wr|BeXbAr9Wb8kkwo(6HJ=bi-$I<WMw=j;~2h+IdRV&BQ^Inr_T-20d7?<VCh&O-jP2*@@n{}MZg<a#xJ}D04n;CwT{BP>Co#GFV!M;>ED}(I&4I$o0QE`qR>W}>)`VR57-fpl@^+x;y%I~1(UOBI|@0);s<$O02I}>k=cfmP$u_4aK)D^@lo{^LXeG>LV&8se*Kl<vE$ivcNT94-1EySD2V{u+TP;f4csIrUvf8s^`Rl8QFJlN`<C*HQcVJ@|6{0RR~@`=}G&4T?9cgl}8w0;tmF?%U~+m?>|th_n+F6K$&iWG;|xLFd~&qdxMGDx@m@-CHX)&`1SpA$s!>wzBFFV`<VNAd2d`Ze)61Buto-_YOS7~0SE>(7Z-l0C5RJv)W{)4BT|sxN$Sp7gxE8CKrrKldV)F~?!QY%=VJthhk@(OPAA^?4rU$8_Hee#Cs@wN|Z&SK|UOpP%m7OL|@|_R0RM4pUx_yCzfp;6Uu#`THmy`{|>^>kku<pVrAckf)2VKYT5l`gIWdb1AQ`&ZqIUb@-M1C^=nlPjt(ryeVzsOe?Q9=m-1yuOt59N3p-Q4yF94NvV`)dtm|QV;g76gE_WIhLzW+hf&^4*OoZHwmpNN261F>e;S!#<;_+<Qhp5g>ey$NIqs+Wv%Z*beZGhPe!;}+F;U1{2M@}dT44$CM%Qi__YrMr-YVe-VIOoF^YghQ-JjLO7sPABvT)w598Lc9Sbti7Mo?$YTLkg8OPh$-?HAzx;d1PI$G2m>+7odfyBdprRlY&IS!pBYm1`5qn-Wt6`}Ca}*k?=w`{d`ZfiLl){1~lcVBgILe7U2<tGyqT;myiLxmahD5T{pb;*CXq#OoV7U_Pe}hW(N%6u()bV_i7?iv9S#f#}yGlg?#5L8Cm`iyI+7lWtJEwk|&quT0CqdQ5Vr_?15%!9MLI^;av1q<LkZ(tyq}J*+RquaCZm^VG8&@k-x3tfTSod~M}zLmwgjYH65nj=hOD)iIb4(Tk7=rvVuMNq2Kd@AC%j4@Qp_SWk17qQ3`c97ccRQ6>dboVw>@*sF!aD;@7*yq153bG*%M;*DWPk)L}})K5LR4)xo(J&EGinzyBX=|kJ4qTPqYD-HEByjt~7ir+Tu0oG|}75U4ah57H14n8{o{%e1Rc|NH+oqyVt2+Ws`6NxuAwZOS@^I$5*)#oZb|8rN`hs~SLX=Hz;F4k}IUK)2bZ#?lvWOv$U)N!8FUoGcT;>}a5k%zDu*#GaQ60df2!Fn&(i1MZu9sz$Ojm|aQ97pXMeeZ*Ra~bCC*wZ+7-hBxFoBx6H^!ygO2N+eHu%3En(tI<+-==u%h1H2SHab&&l)WF7;mu55M|p{KPAg~X5wA5`0sFb<$zI8HKZ1Gs4DSWI_tUwhd=o;vKHv%BcQyF=1e6BeJ9PKuIQI{oN1Q)6;l6$KIo3~O1?%R5c?s*>1NV(AFXBymE6ktX&Uhc6*_C+piX+bJBIH^5HWYmEd}>#<ry{;%^Kf4tokD($md|isiCv2Kl0&iZf2bPu%YHKxe$IPh9eo#pajYIl{m`2{!M)wZk9gzd1k4xLOw1p(nD$5ILN4+4z&_}&!<%u)^Cj2^Pe6ZL)+ayuoL)4)%v>+{nQ{T|xkD3)SJJ{T|5JZRNSAg;e<I!por?Fk;tZ^Fmp90tcI6T7ClzBbem8y4PW)?hzG(45<foK3)@`JC)bAS~wc2aRhj2f<yASKlHWBx`&^X+C@9f6Dd2R{vv~(NJ{hnucN&klJB*v$059D*Tj(N$v{Z<FuD<)JRd#&;r#AEixx~`DFUGn;!OYlE1AAUADVcwMTw{vigH1pg^{rdST+TC&iaT=e~xY$no0)E}E=$HQ{%9}R40<AOKpFWsZOBZ85`rVs&d-h1|lMhx+q<&5M2>V}tE%0uYW{};e;aIQja4y?>4x;!K-*NEYGLP;L=7I^4)K1BK;<bq@Xx~tlx~xgJ@XCkoSVs=Ck!PQ8z`t)|Kk+zm*ve~rLMi|Df^G3MPa1rSc4KNGpT)bjT6x_y2J@sm?%Q^!T=)<D7<ot<hjVBX_Iu4~6yn_Q1-`#9Z?@};IQ@I!{t;A>*0IgspT}!xs+HG+Vkl0f@RKwvuXL@2`H*}rF5PP1-w)@hdj`d?H>yv(k@gh#!-F@lzcX(SI)LvgbFbk0-RAz-r=!{<{xkDNTX}mz2-eZHnsmRke-MasY-L;Q!x7gGl;PJT<NgrlLh%?Lp@{!u51iLMlxQojj>Y?hy1y;fbwwTR_N;+;wCZyyUl&)SzdZ_QUKuNHuOvNj3-UQ73HF_S-e={tm%m^>jEG;KZnfWqb3xx>!#F;<j(8$2;G8|IAGGpD<M%Ot!usQT<(6mQceTSg*u6I1i<q~adx-l$c;!V_d-YKo)>qCGyf4?Nf%80SD#oj+`ynfD3x0@u@BF;Y=@wpb>xlU|EsFZ3-t~Z=!L=}dRwa_3Qr@@~gZ;T-F20}UH^hBv_q)hX+hsIAOL=A00>l&8C)R4Owe&%|C0V%lW;eq9E8#bsv(E}}ugz)#KNI><9*iTSwpn>?^S2nU2M7A5TkRJW;63G-Ki+dfdgJ~QSrPkHvxB>=yxG4e)>rFQo5{{I0DfBC#5nr2O0n|#+izXO{MfoK-OA74`Ecs&a^f9>k^g{f+*^u<P`iKe-{HHWlJh0rLo*km-7g0r4>cF0Sb5{vAlRqX9Y_9?aG$m9&&GHiJ{4o-_2-`O)8>=al%I%L_!%_|=VQT6T1VRCtr*9)zaXD0Bk4T-ix2OG`Q{d}+sbPdvWU0;ae}@>X|-`rv^ATE{cTU?&N6)E-SAW4la17ll7)Ciyu`hz_)KKFg||B=W1eium_hUQb~eVV8}7HZsF(y_3$Fz?ho6$sbFKDvzj=6X%4vf4y@e0q$1xG(=yZ8$x`o%uIicMbn?9p?>;EU>{3pIAEB0VokIDy*cn|ohBHI0_Q-H69SHt5lA4YzeWaaI74UwOg{;SCDu^0Fac<)nx%EEheUQ>KOm|u)|VsGQVJ+~kDrU%e&<E&}){NqsKwc)36-{_9-lG^Dd@E=y2c=KQ{`VOl_ugCjMjU=pVw^1>^er5h@)vbP)skW*jbpn+YHzjbC<xf_Ul)uvQ@Bd^K)aL*9C#yCc{@XuU#mcEGuv}o3z~=%>1vaw2K_H6xRm?}REXyyr?sJyIS=QN)&U!e@vYgK4LV=kqf5Ccb-Asn$W-u@HATA|0-lC6Z+XY-VgXIvelX@VRAuLbhn5MHV%W;h9?0Y`j$oi?Qm&&pXU`*rZWDJqq_7^OdaxntS<e0M@$u`j}M{>P<b}RFnS&m^nnxBc{x@eYVeVo7=E@Sw)Wh}3;jK_R_Hj2kHSYWikB!Q2)A3>ZWnX9n^Qv|{U=CUly$qXsa;c_v{dpQmngIxC)1o9Y#0>3g>XyGN7D^S37r@1U(yHfoa;{yAZ^^e)+4$B2B%kq0h0sGh`kRp)GWg5$W3RG}Vl;0Kk85Me|EX!X6eqz7U-;V-W0+|9ourB2*te@gCljVn8mm_eK^-@`u-wNcjE@f8{OI3l20@s9oSKzDy`3dW?Ebs8|I$7EU{t&3_fchJ(KVe8-K68V0>92@wBzK0(Z&)s}=r`CtmFvD?S(XPGQa-`uHI{D+ykuV&SubL|<hC!eF8y9+8_6B#@+ixfE&4^aza&u1btdbV8O7|&Wc@hnFSu<9X9vU}<th%)U$Fd=eZ1i3r2Le12`2~GJ!Sa?$99Hu^9TEvc|XB9kz-Xu=xzcv`Pt|E{A&UZ0_7M|{->ym7uX}Pn<3@>0^7Jwa{B}l1a=Cn5Lhj+gz=fcJb^_55dxtC!v#hN_z8?*eHcT^?{VqJ@+h{G^|J(K3w+8x2D05cfh_`SS>DF_NC8b?qQECC58?77mOo;BB-==Cu%)gq%d+fasgv>`f!+eWSpOdZmF2#y_hK7g=H6w#y+8+nMqD;#xe?1XSeB(c>b(Vg1ZoMi5qL}BA6zf(T?NFjDdiOWWa-GVvp`Kn{!0t&YBJYOpu5030&Q8Baz%j(0xkk?3N#dWL!g;JE9P1;FXhexUAew1*Ol77&32mvwhMeIki@d&cCapGLm*LLy+F3W&jKd}4zqreA^CGG%kl_w_gR<ab(YVuoWXJi+e@1gu9NtV>!f^(^%9mPCzJb#^%B-^u`c=ZET89RW%;$hS1ey;y|nHte(oykQvQu~M+eA{xE)7s+r<HT3Cq=3uf{e~uH=9^X;X>I``oT<^APv*JC<eMp0Uj{e&#;s`ySWd<GP>OhwR4z1?^Vnw&l4j&*2FI{RBP~_&}gP%aZHCx|DmeEV+)XOSu!vl54`cl$)|FxdyCD*^6b#xwGDYeGlcf-xu%~7{In&*jGyd`M(s+1#GNK*^}i`PU@{09s(_x^I)z8%k>#jeqEq8>#s8;Ux!OimS5wt8biu;x%6bY8kg0%lyTLw==Het<hsi2S3XyT%j(RRa^+cfV!0CQe*GLA-OBx6{}T7_pDyQHnSYRb^~tiYCDtbo3txY|r1<r7l6#HVtQ_f*>ne9T<zEjeu1^'

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
