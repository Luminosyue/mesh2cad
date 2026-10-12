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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/87ae2a99547f4240a15f7fe30e9a7122/part_006.stl', 'relative_path': '87ae2a99547f4240a15f7fe30e9a7122/part_006.stl', 'source_sha256': '8674e7466ec07d933e3c5632fadf12c7b0a905d1954f29fb64471da7ee296485', 'input_faces': 368, 'input_vertices': 217, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.21059550344944, -0.05439947545528412, -0.12404771149158478], [0.29456615447998047, 0.08988363295793533, 0.20502382516860962]]}
GEOMETRY_BASE85 = 'c$}qL30RfY*8Tu7M6VYVXVc>Z4rD3_IAEtz^QtI_D2VAn#CbpvHAMLgP(&doP!aM7Dj<%im}2ndfT*B2b+ytcZ>CxPYIe)A+ueJu_v;>x+~@h9|EFg?@4Mc$_S(a@_cxsMA7NL|Md7~=$~)#4={JQdt&!rQEQ*L)I5RvVy63#e_iPj=(&e9y8%G8C`G?pji<G5qQzN3oqulx%+y+kbadS7gO`9LJFe+@`<oQukBcwhwY)*89(4%LBMMem}YoFfU?go!;?uKQC|Kp#d7=q#AvkPy?u{^)=zC`2DXC-9<wY6O@l79E&G>PgG+fu13_lB{)WK}Tb-|;;z^_mY&tUt~RBYk7c$CMu*&ibRc6%w@%KIb}<r;)CnnzWwq^AjgXUp0gEFEck0et+a7ji*~N*D*%Kk{>axnEGvSob~R1T|({WRCAr2ldLB;N~C^096yq}`F7_@(ldLkp}gDM4%gD}zenTO8jd<j^}p%HdS205>8nq_IwsNRI)L?G*73S+{-jLmrh7)#e=FNe<L}jx*1=q(vhGxW2;ujOXdP-Ql3D*&O(!foOyf7UN@e}o=L@LcGlfM|$0nV0^?CLN(tmn<km@|h;{5BG>9jsR&yP@@z2CAv?e21#Z{KTleN8VOvL3KwEsfvKj@G9p?q}AkX1q^z+I6G)>TUZf>NhkdgZx)d?4^2_ny~)X*O}Dc!Ja(MK|QK?zHcWHx^AHLF%RuUy7BR{48nxjyic6QaQ>!Mu~e^ZFt2}nAn96C0qqmT|0`NIV{$O(cXU}t?MK|D@oWC!tf%f=P5zVcLYlA5A|7Y#UottbAdl+5xr+5~zWR{rZg}MY#iMp{oly&-Xq*ox^Y!Xe$m4HWzLDB_?Bex2T+I2#jP5kv8<n&U#=(_be@f_Ps(a{XnwPq%n)RuHJpTG~cS|%3xyyAj)3PbA%SSoXZ|ZYihnyihsO~?$D4_Mc<8q1ez2a6=y#Oy-Ppz~C>sz8{Q~mS{C45d>v+m(d`P#&Kbbgg{ZCQU5K>N*Xo<i5%Xz(RnwL8C&`~fN4f7iD-|4L34wLjkDFz@H#od0>Gna1x`wT<%UO(ETU$MXoSU&Db1>e98h)5{5;&)_;&8|PB}UoP#WbuLo5-{7oh!k7@c513CRu^!{Sist|DA@2uWpEWL?`Wyd(_JejRg>}=|g*2Y;GU(i?8#B4zRaa@AYK;w@Gi_-O>t8z3byRj9+)DE;DImSZZ^j|Zd0FfFymVb{-oJ?EUA5&<Ssl9CesE!3x;AX{*}Cdzc^l4I>iT-B8MBJY>d=j8=7PF(b!yMEb=5Jf{jFAg^?I-3I>!(FrSU_5Y5clwHGV_3?XkMnQ`hzNRL348-Pn38?YEjI%V^&kx}4+d`?#FWkJ4l=-T%~P*Gbn_RMLJ@G8SzobiKoM{<)m@+s(LH)PCGIT&GuYFzugF7ipiX?H=>^e?Ce3K&|de=U7d9!ubm_R#KhHrgWdt{`Hjm9oU=uUFMTY{mpyE`H|<Qk#2i~o-gX1pSXU%1GN7XkJhx$)pr_PraJFL?;?HQ5468@U3vQf)z@<DGs#bGeVO<3COU`8*Xi_}G#+eAy7A%Pxz4#p``@t8wfh@LH`?vZq4o~0oWJ)O>1NNMeDclRIDbzMT4ycj5?yx{y4rIH-Pe@<KW?IUbuZQff8_hd*4OF&sum34@qaa*?!&6{oDWFvFp_om*)(oLze%*;j2A+<-(!BXzDlox1k(G5a(>TKbX~RYUeG$I(2WCT&^}S(F4MXxttWB*H3PL*_jINEv+*kQ*Hcrej@pIhr$$ZZ@$asn`+#vk1nmbUcOH-DP9@bh?fzvSwGW-o`pFdTcc^VH=|4tsok7m|yie*)pz-N?z6YI8Lqd~}NN*5Bx*^DEzvcedb?w2LgAz^WwKH|;#?qM;minLf+cEz-U6)>y-Qzszzb)oEW%p?O#!na0b=L;0=JgqJp2r^^oI?IU=#{xV{?#pyQXS82Jg?Z_>3nH<xwJ2|#O<74-Fy$7-?VmoKhyOdiB!il{`?kdzw0pT3zt&9TG4-hEq%QQ>8AL>v~P{gj^g@y)AiNzAMYdl{UncPY&zv@(LOw{pmNSX(u&XB-hKSO@WXl5T}$ab(D-Z{-B;DpTdXG+^7-m~f$u;5_SMw?tV%vdxBU3I>C}*PrO|CV4@$-teBW?)W_?}H6!It9(!8}TZAe$69cVm;#_hR&NC(cpeU{$Glt+)=Bi*kH=XV{=`+q<by{D<S+*yCncMIjGUt2)edut!kwH6cU9I2yCw6AM+cys+lnS6g+zxV^5&s(flwxsiGdhywzT6%&bt%G5<!#3KFD~GZEZ7$EV*ROQ_)pjF!JdJ~?j`5x&oeMK`rRmpvf53go9E<!<mhgTX-ISm67yLQ@(`NL(WcEs+>!_xVVcl?dkL7vMb;H4%RM({RK2w*jta@Hysq5#$l;v@{F5U3(pLAZdr>v_@(&;^1x#C0jLqq%o)~`j;elwm8pmVM3O2Kft-ipcJm-OgKynhDA@xJ+C5MQ4^BDl`6`@C;I8&2m-*Of>I(v@p!GM(d23s@g_n)9pe=^QDYSyxL!X?(`&p+$U7mva7OjdjQH{k8P07}j5P;PVx^oa-dD;{EJU#qX^HRo375jNiYny-wG~Y+A#0p7x=ArPw+1d#~?i-iOx%X@3}(ou_$gxAM8pb|-%CD*PM0hpLY>)}OTDIvHUqUH|5%x&DSvd0%;!(0xnGJj?mE|3lA5wb?6t4!*2ny)2*3xpI9JJ@-v{H*4*4^^fiJyf%B(@O7EP<5q5z@jkqGm-BBW^FI8?V0!M<=z4ArJ=Zi}J6dPM7eBE6-E2Ci#{1s;Ep@f?7yLbvc!}5f@grWJrVqGZqtcJ^O^><Gqo1gbT5hEKfzkab*D2i2^)q65{Ud*6{RDsisDW!~pD5|}R|xC>PUlPYA5&CIUoo9@V}LX5AM+vBwFhSlEYFv&|M{H4^Tk@%pD((upCe`T_owR8Ri8ohJB8s*N77Zzh4zQydp(i%myHvTGi55j*LGjb=UdmmZO-@8?54Dy=6x<)XV!AoJqGdm3~9;p%Dcz)&*X<t`|?hlKW`_$Pu?%1=bh=ho?QReCwyOP?^#q!51P#Td8@-#s{5-C>Bj7FJ1x(bt}7*tSy!ghIF&qK&R-tM-#<6r<@c@*$2s5X{-*2J_cv=@zrX3a_5ICS*Y9tJ?g3Y8U0?L8>(=if*1G;4qU+Z0A=bLSPfSV0q+5SyS?l_Eblv(p%UajJQ>=CUJLM%E-zmCo{hej4>)%-~<>NccTGzj`{_NN4JIh*sY5Z2-Sug2U<G23KvexzWRNOzSJul>2>y+<b>sQh84t<Ad&LSkNf#RY}3$yr1REqLX$GU$Ko$2|%`bpHo%jf_5lW4g-^1`ZtmEebj9T4^junc^*u$jVAfos4&K~6dF40tMX4gn8<%lIkuC$R!t#`mFy#E-#cU(-=T;%e|R<eUMX0$+oi1HgUYzQX#UUO&{DiMFL^FYz?EY@34i68D44wgb^#;tcRpXj=ii2)++(KL(b9Pe<F;z!Zx<*CJQqL2%iZ5xEj)fy=(mqCbh3!S|zWDNqBSfwn2Ywcw@5ISo7u{<^TYgbfmQMcChkRY4z$*bV4cpudgSRp>H)3H&N@-aww@1K?jk&L!wRh@FFe0eXML&O<*3eGp<*&}F=ru)$cfYr<|~jimk#VxL0427L%(*P+XJHTZSpyoo%?ec@Lkry6=c#44ayLLZ3OMd%gKjfh=_F5?cu?1Z@h{|fE`-VNBng8v1+#8%+4Z9T;6AtrePVfMmofeN^SzIAQ~U;f#^w?QpCw5^YLeZ=HncVQicH3K?<Hv?|~w71}m;WtJtd$ethcx%L*Ft@&#yX0Nr_XY0`>}bK;!f%UO9nrQG;;j&qypgcZ!kU7=3coXW0MNsNyTEtBxID0SucC$nV$yFYO#c5VXYg0xJAyX_HnQNh@NH465!UV%)M$X1^!o_wBy1#j8~B~Toq-K4cr*CTP^%%<t_^B*N30FzX2RSh_lIu+9|`PZ!TZARi&}lKPX4IT4KeAr6gEtl0sJ-i!@!pSr+{|`e+@hUeoL(1YrxLn&4slP)(*T0{1)H_U`udE@Fw6*;X6ZX4(<qlqA*Wk3&DH9_XKYTY!2QDya%{5{E^Tmf_H*1=N5;#OTHL>9QZ=uL~s-MV(^jh1E5U-H^FxkHeXn8@L>27*IV%A@P~m1gD-(^faV5141O13uEN~G+rxJS?+tXb;4R>{KrJ_{U3=7MhnV!23JVjK2tEpa7`QvI3%DovDDZahmty@!0X@OjV}6;yH1IU^sq>}q<G|Cv7s6kTwMqlVfrkhiE=&c!2d;u|2X3?A^Wo3O__m>KZ^U~eCb^$5Z(&}*p5R{KA;94l+!eknY7IwQcf{QhlRQh<7Gbf#Mc}dEen4*v9tJ-QwY<?b5%EOC7GchEe)+%;!SlhhfLknhCj3m)+Jd(05nqp(<PpN&6}Aqz3Va=S9x%s(tMFBfF9&Ty5D!62@(IGm3L63Z8~6zD2;jRG+zY-JYQ2lLeu(=aCb?Nywy=2MGVplt3Ba)yJQjW|YK=wPEX1=ATZTEy`4t0;z>C4nz-$Yi4?iEZve9-s;@c6Ee6Fxf!WMvUgfDTg1>XaIBd*OJU><k`VspXQ!4DM{C~Ok=X!wEP3xIRMM}Ut8kAOb`S}6Dk_&bCp2+IXu0Y3qJ5-`+)$HR|Dtx&Ap3e+$owgPiIj=4*I4E}NOT;L81UJSn&wRT{gj-f^#V$zQmwpCaR_-6PLk6Q2}@Hc^P2Hy)m8tb<ixCwlYu&Khv1IK}nL!Ua2h93w%4txRpsaU^pz(DZb!jgp*fG5FELf<-{3O@ln349X#-B`aQU;?<D+eyq_@)GzZ=u_vr;U5Pt0ndeh1Z!0SJPsZyEJ|29Faum-p#?t-e=B$f_)+*V(4xS%!k;WGT-X?35O@&!)_D~C@!&z=G4R8&enG(T;5&uw681iDCHPA8t@CjB$>1x&=fE$3whKHNej(=f5%2`~3G}V=UGPtWp8zj_e-zqb@RRVT37aSE1K<X5{}DE}E_VOzpTzy=Po)nb%YPte-Lm%2MwTs`i<j&_e?;;hVNc&zw&Fjz>7C_UkMeIsGl6g'

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
