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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2260799ee4e342398b64ab4ce8af1559/part_001.stl', 'relative_path': '2260799ee4e342398b64ab4ce8af1559/part_001.stl', 'source_sha256': 'df26399b0bab4e6d0b6be57c1cfb298ac87d9b6520ff55a24c0b7c3e86b5c6d9', 'input_faces': 258, 'input_vertices': 163, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.29183894395828247, -0.3487766683101654, -0.3655930161476135], [0.2352532148361206, 0.4499407410621643, 0.2201244980096817]]}
GEOMETRY_BASE85 = 'c$}q~2UHbT9>zxzjU`r8#P&p1QLzB_5=Rspim0fF?ODKr3W8$6GGMPO0yY$%5M%E(*hW<BMvdJ>-zKppt0t~)5)-p?zyHU^?AbkM&+a?tf4<**@6MfD{`by(5EA54z)h1+HEm7*+5^v)&@>grG&e0iB6j@9p%HQQ#>Py}r<H`SK6#oF+^cIy-+WrUmQZt8MBLEWn$2xBTShjm>0_%I867)5cJSCi(XqoKl;3{v=(q^Wj~g*KCc?V*_HFF%WAm@&W1D9CA3sH`Cg{_)UpubaV!Y_oT4}|S8`ZU8oV^M^Y>)xJONmsawyzh%*DJc5#`j;w@5FWZ)GN>y1>qa(rmRrq?H+eNL%H}1P}4nan^H$uuJ~PkTGtxB&jsA~Xor;ht<p)QwikCU!hf9w-<Y`dqAKsudvC@4p{e4R?{ER_9CtMh&wUVl3E!{ul77s8un_GV(Lj9ftfSC|wT7Vlx#IBk;^#0PX4crfN}a|ddA{4Fb0|OYO$^FqehyzN6SfZ;UVI|dxk&s2pKg|Gy%qYA5DVW-dVB))O`X0J&)vNR{nk=FS3-kJ#VfUE%@aT4$O`DvlhN??aQKcbE2ZDZ_9mg7V_Qi1j(f+cdW{+}YcXH9pP$F`SJlA$IQOJUKSEZ(*Zz9)bM&WyV;SoADi7Z%{v*a&%h1o@zWh<R&zPQY68?gmXlPuR)OVxfO<V`KCqQ>K6n{}w1NE2MehBln+Ee^*H|<7!#bQ21`C-Oc_(yz^Z^qj}d*LsM7JtLxL+D4R#1!c6e&Tz%CnA3)_@TV5*JHF-OMA5m`gk6mYb)CtzJBOnE_A}S18C2^H@MdP?xOv6uegJ#-@m(*TQvR(>QCDKu~Pl)E#$Xj>+#E&&w%{f(cbhl$@@_o&Z1n?PP=el@+4U&-8LS@b>NMCXiwvC@rU1(d3^VDHlBAQMEsmXtI+?PG~|WZb<-()-(x)H%Zwi>{tz#$6Z6uP>-c_4q?9uQkY`%$rC4uz;oYb3{LfC9@GE5`p&hHU&)_+aQ^ZfLdmYykA7Wn2F2Sbc`_RuZUKL~Zpns*k;Twa!E}{RPJyG6K?w8|e&&D>=uJwL7D8H>fe63$B+HV|xxnB9smu})`URa0cy!!?DW#0Vm82r~|rQXwXP1F-I9ljZpdRN-vyBv8tbC;~=QFAbE&O#dc>%5yHe!vLivvI6CzBh-A7XQgJT<cqXQC>TE<p}C)T2JP8s>cz0-+Ns)+P!Ex_66M;aSP=_>wJoGkDK2^z1!XP!+&-Z`KnENwIB6<8*>ABbK>m*tS6TRvfq8@1K-HKwqMq}fqc{UJd^#@wFrDOyqS#K?6^&6Pn)OMcZ@Z!F@KKCHW)X1qL;KUa@aNWckZgA^8MpIsQ*RT+wk|iMcz7-%kMyY#>B}!;2Vm5J4f`Ayb0=z@{auvupZ1hzFD$fx*@;p10EvZZ83hCXiwlV>~ngt-!Sjy0Z;hO;@+rV8|IF6;W&42J+8|<#B=OFbU2Ul+h)Sor`XYcJ)#xz&EXs(<qJH=dbbs+EAu(7ulSzs4%9Pj<~fYRJAd(ydE!0feA*xFbkzR@<+KlOW8NKcOQro@HN@|-6Z?YwgA=Dwf6~4T_%k2oqJ6JIM29?Di}CPlatrfSVAV0)x2`}s{O3(DuV!kr^e_2oD#oW{JLHMhH4g7n=l#lfFPWX~S8;#!cd|~?znh0~xPIXaw6o`VjJx4Cb{6!*+VIVb-pD`g?ME|F&!7s}$4u8s*%-eb5$VvTizR<5*Ok29WnU}n@?)9zpA$FZ`E_48(C>S{BCpJ?GLKr(N9$#MltVt)?_S)E`;WR~Uo^by!Pj<gm;E$lGJJc<D0!cIuSOo~^?u%na@$&7lRSTY9M7p1ioDk5>`g|0M_rL|I6F-IH*K)58K;XQ&-LgB;^%rSL%HVpFkjk_lhF^YR^~yBZ-*Ar{&JpMq4l3(9BtF@p?*DQ_BQyHzQ%ggyZs>h=)`?kA9_$boCoYzdt%)hliYUTdF{P%uCQm%*ad%1>Q2;Sob8I|?%ajEGH&I<H)~yzajstt<7gCi#X8VB{)BUj?q46{ZV!lu@9f<G`J)9L`~=!|IedHH%kXX43-MfMn=GlPa}=)i(>o<^0~=y~jGI2PFO_+{SJr3y-S4;Gb~9SucSoCGotfW<VE?gQ-;Di73m%B~s?oNG>__LCVBc}HdnUd)1lQ(<mp7qza`wsizmWC$>^}0)7Wz!yd+lbR9$RFe?I`aWCi~;8vQQ(+CjIUmi)%-hbd10A!MDhBTelqe`d>=mJ!KXyi~ZTwCl|gMUIXngE<8rN^nK^0{@yobKg_No<@$UDb@m*8UHbD5?^8WIR@Q&N9@3w-fBzWYcPW5;GSBzGdq+!8kn`k#=Hdr_gMOKJH)7v+>=`KM8Y4*FAEhtg+BSTLyjKIC$T%E}#yQ9wepmdCS#rL<+5!2dC6&hbX-hgv`7!>OKW$OP!zlm2L*~hL!iN5ht|ES~r;^73bJ2ctOndRew#xhFNOgJcn=hq(h6~P9MzeKjhyMH()~j~RAN!OM-E9Ht>s}7~oKYql`>a{{l;nMxTJX&m&G1~?C|7y^&*%<ci#&4~_l5p#1Io>a5dYi+oYTy9o6$bw=Q#20{rlrOD^$j1M7H=ZAK-ke&p9mqNgtdGw0Z7}QP1)$wA*++Rs2cqk@uS8E_~;dh9~g-)gpM$8;-S!Q2Pb=+O(6Ro(Ze*obW~1Kb%$k&@U}5ZXCuTYPIYu{$JdHwrU{nlbqGqpNvW4<UF}~E}m~c-Br#P_e<lvq9un+K)r=x#9z864Sw_zIX|cTN<Sb1&r95c{lW3%H}RjiZ9%*5f0cr~O5px??~(L(>(O|W53C5^Y<fEf<I}L5)Z=B7eWLCuIS09{#CgyhJrcfN#v#9(W^K2l{wLo^`R;+Tj}^O&bAzplH{OT(;~dG)+>JPAn>};oT)93Id7@R$miNTSg4h?eI_I!InEt^yN0?LG;F}%;@%}Il*U3P=Pxs0`I%BN-e#ts7>v39uoEKuBOP)1bg5NF9q<Yv-jh#Q>d;LI^yr;kUUiR5SO{D%tb2h;DXe7UL^tZinz2-jlXY;;Y{06NSpuWY)@?JYr33;rArp?85hwCekhy3BM0OsbCrB@cSetB9^SaZ`N2fz0x0A;FAp8oqk0gP<;U;PQduTj(g_fG)Rtv1ZCVhTfX0yU1TbR0Q>Jc*%r6m>9p6nO|kaU^v(S!p~ul01ProvbvP97!EQjV3D{O&-l>D=un9uoY!BH3?RFTT#G@K2~(KBG!r(RxDz<2zu?UXh^L?jU~tOUd4V^bho0Z6*eo%Sy71UN-jjs`zX%OP+XAOgzRmFN~7k~g5-iM)10ArjLIP^)>^TKx{kbtoNh%bHJPE<!BCt@T}RF&ucxjhuP4V)$B@UcJuwW$&8V(qSB^_FhT;}f8@UC!4Yet`4Y>!kJGlpWBt!8;&e38`=6Nx_J`Ba(sNKokIhTsNvRrFwH*z<YY0WZ9>o63%Q~k((Y^%HWdw#f63z6$kKcE&OE7iz#sMX0z8!{Bv&?I;Nq)DEaB^PEWE<vqCE=+Y{C@w>-M6SfT%TTM6U8wn})ydV_&U{pjoR926&HvtW6&IiuBrA0z7pCU*OL0-E8(FD0xhOf9p;)IjC+lQ8bqrbQTC&oWWTi97N<+zZa$cRGd}b)i<+VZa3hGL-(lz82<V6g{%c<$)yfwU>b*ggHsLRRAS!NnT@d9cxc>y_5lQp9DyCiBNIgw?OSVrk8YBE`=gRC@@97|oyP@F-{Br9D{&LFR5D2}4Wkd-zgD{Vnm+J+oO4x{!UD;-G=BQK#&Bu`{pmrygv8En%MY7{w)s;)~~QPGO>R)ky8+lsLa#giF|2Qn0QVJHrvhLe4)_{fT$)DUtA%k*R@9#0)h9#5XdP`r>jnY@tvXNKZA)PdwV<bGCkq6Se1k_WO6K@7#Ms3GJK_MsI+ab2npS!p$LU9uOoJh?o_*^BB=_9FXIJCQrFO}^At<W_u!FYoo`b!RIYS<!)7o2;}WxiYWS_qD93XGMS&{i%H!irZ4_k=v3RTj5EqO07q(O7@`EB72alFcddnC=R3skn`FU$WT1OiuqK7+MjHYr&9Zpr;>*;6!)UGCHEq?qc$eDBe#67&n+2>>swKiTAJ!fE=?{*tx7INE<*Jn7a@O0twR2gT%7Z!=C1;^6uA_?uRyIruEO!Hz-YiaYLh!s1Id9L)4W_!I*2-goHqx9SVrkkhT_@O`Q)M0c`UE4J2Mmypw1%?AkVd8DRmij9(fr#g*uy@LQbR3Cx-;(%kSp$pZ>M^`^Ugb{{4S+{_CB8{5kagodvB;^q)VDLV{e?``<bc<j0SRJL(jo{R3{MF0u'

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
