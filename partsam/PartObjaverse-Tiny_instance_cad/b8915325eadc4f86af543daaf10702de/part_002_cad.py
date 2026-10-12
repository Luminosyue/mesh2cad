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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b8915325eadc4f86af543daaf10702de/part_002.stl', 'relative_path': 'b8915325eadc4f86af543daaf10702de/part_002.stl', 'source_sha256': '3d5510cbd4be6fbe29c8aaa3f8879bcf3dd5e8dc4cdabd61c518a3229bc028e1', 'input_faces': 458, 'input_vertices': 269, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09541725367307663, -0.35411161184310913, -0.14682763814926147], [0.16236352920532227, 0.348353773355484, 0.0954313650727272]]}
GEOMETRY_BASE85 = 'c$}r133L=i9)~+1DoHpLP)-@nhz14a5`knFkI{&WayhQZa0CzmkxPz6hcgJ`1xN&i0R_Xk3xY%f%s>D+RPX@B6&*!Tm&1!w6nCoX`*%7u+4uJChF9<V^2<LpHQiO!-IGVhtkRcMcFb2DC*}CtmGY}Oj%uk+WoKme(BY5t&K`Ed;31=voQgVEU&5L9cInVDkmQVX#-{bj9@cwkT5Dfgo4&2m(tT-t9~(M+XwSht9vj*xTjh8395^gHo)7Eab4Ygl`)hA%aZ9@I=0@qhalZfYD>*)dSo=ZwkvOBtJw8+n4ZiW@W=|eo>wK8u$)o35ulLqRH#eRiDIpIHX*xf{lS@B#z1u(anNH!G-hN^y^H)Sl$el*(R(R{BAG=<1sSo!4a*gh1V2h8v?^p8hRiA$3eZRh^e_ZXY5BodMiIkL|?=~mHlS@B#y_-`X+%b8Tx1Y?k8<s>$$bC+eCEj}J$F7%L>SHI&@sQ&d=D66o??mC7-g-H1cD>|M?|W$VQhh!uJip(2JSC6iH{I_&o}uhV^St%ZV;i1}l$3Ya`do%5mwxPeH>W<cp*bGz@qEV|7dwwG$XVsBcaNu4FS*qFp4jnvv2ik=?Of)w<nB1FdiVHHAKGYsF8%mMnL0an?%Vmgx86OE=gqpZ^Wc$N*L&;T^JvveZr95=?eR!1<8h8B&DF2Fx7Pvhe2_dm`jP|Q`4Bu^kn61vK2|LhDIpJcOAcjta_Psemt5*I?=b7nUGJ<zJCBX{X|=cB-3P3C$)!HDD`mEKoY9ppJsT+@cV5bQ)>|**wCg38`q)u3-`#oDmw9jH!Hhw9-g<XlS@n{;^?By?Wt_1+W*l}N8dqVqw_e6+*SqJJ`rrU_e%#}8)|{t=JTH>#t#^-)Rqy6fKfb!TE)^~<Hs9Qw{xeUS`InF{C^OgFkGt-=oBb;xpR;mlvDcOP!}Y_?qoG4<iq*3oGjB83S33_k8JzE}m-T4ZyZf_UFZ0tHkGqdq<8jxu^?u#ldcSh~?c?d@*6|Dv$||<recjEvwC6)Y&iR$xo(~B*_2GGD-PrTl&Sic|ZqH{scjt2_bDgo*qn*q8lH6X8cJ9`P%<I_uiJi;-Ai2Gt*txs^{ATVu?ETQr-TjT+-Vg0u>ch*;d9e3$JD2@ga(h3wb9X;qWagKBeUaS0zJ!LE>uSRF)XLrKDS5*6)XLrKBYDF0)XMGpgzKr5%XorQuV18puhqc4y1%=ADbV%zbG^0hL+sqWuOJWAD!*I5&I`Xry!H0|iJeP7;UsfkY2RPjx!f;FZr@+oxqCl$@UZEpW%4%7!g*Wte9ScK!@h4!$hi-6^Ao8Bdi)uCwtDOB`^kiyexkW%|FiFJCAaTy!`GST4EuiD&gK4Da{GSU&ZR!I&>ScGdBM)*{$FzYdBM)z=ZkW8m~}t2@;+TR`W-!=-JE$Sd32;%_xAHqLeBG!<o5GXLQZ{nyt!W4&ufy~&uh*}bDZqwM?072LCIsgcJJ2xH)~elt(Wy;=l1iaolF0*2MgEf@4wlxP1j91y(!|!Wu8kOJZkm{`}x|=Wj#tBzJ1C@-7o7}a+&{jZa<IPxw~)7*}mR8AAG*s&HiuYp;YFF<jj+VdYM1e2Pf9n_b<-Kc`J3@;<?d?H{YJOEW?wBo0|I_`|}FPo!tKYbY6B}vHFD1G3qog@Sb;BcXlr8PI8$KcD>|MAH4m3ojc)z%{upQ(&xu{aIML6o_SlZ$N8N$>%8xAlaH&S>z(Gkb$ztOsRHkD4z6mnsH8kL#at)coa3BOPcHSb5iK_A*UL|fXb#KK^DsQJwaMq7(c=t`UaWK9Q@u=nU;9luPrp@<GyL={lW(2BK_8z7QgnUh^jAzibDQob{BC1C4`Va(OkO*nnc1X+dA~1gF!{+Ldc5I`*{1(F2k2+CK0d)7*PC(XHPqv9mffUZH@f%<eLTafJDNOufo7;{k{N&JKAVcoTe&ZlT;`|DlY)@x=e3Huf9K+*dR~P#PBQtvn9egN9n}4Yw#+qo)0KL>!3Qhp+}Xau<iBq)=XpSPQ@?Yg$(QWc?<+c^j2?ez*cp?vZ}{47UsqD@u#ZSC`-xre?laWK4wg6btRSSvAKKr|oR_a#nf!^f`u8#?A2Q=V_OQwG2b<$?)hK-&q9+EL{HrGBeZ9F(k3ahJ1e3Qft^4sk{ezhgXJ(naLOFeW!nwET`rz4Ildo@J=3(T7IS!W}Gx^>x^y|h-U1Ro#E2@~fsdwq0hu+$*>oc#uG2*QcH~v=FXV$#a<fo>Y^?i7re!rP@dYHURH#46%e4_h_)$M2U?S`?R4(WPdgU3x?ub&=&Y*!s~A9eFOlOOTx{(Uu`*RShqbI9Z`&(`A%f4|=J^V9{?uk1722im#Z2TCscyxeEnx!h+;F8jY-FS%Xs?qk+?B$x4IzIItue_!?|-A^>Rz1eRUUup7w%guT^vCABvH)@!?d7)YF7cb+y%riOre=xgFeu?=6b3Jf#t_unEl1qJPU(|a%-RA{zxn9WgwVliJwdC&ofPBu-`jsu-^%%SOmH9l@%EO<S`&!9mJ=*n>yY=NKZT0r!zAm}cyYK6*JzKr=L7q45T%I>2ckh#}dUu{sA5NcK=shn^#qRoZ13M3W_wdqU^_-W4dbz$!{l%??#l|n!cXBx|@_9u<&gT_wF7HeB^Sh^PD>hC$m+{E`WapjRy#4FEW3j*boVqoVb*_rzs8-gg?DXyF`IC<d)t9j3Klwb;?7#YxPqXH&{@*|OJRKjylz3Z8Q@$8Jg)hbz!oT4Q@i}l5J_mn3-X_6;a1=fe?*#9|JK-(hb$AQh2d~0?_?7T-{7Sq$yaX?gr@$mU1+M_h;1%#nuq<8)uLG~f>)<Wn^>|CXGrS+~j1PjN@j>`x_yRr|pABEbXXEo|%9q2x<IC{~%*P}6ariNQ9KQhng<rsvk_>;rRa0IDp21a9emVRJS50|o_#LjA@;}Hv#Q(t0!?*DB_))kLKZ<XH3-C?&8}arsoCz1;Gx3S=Iea4iD0~8c6u%dC#P7wM!$x>>yf&<Y*T%1am*H37<zQ*N9G(mvJQ+`grSMd|BD@r@h+hLM<JaKL;I()&yaW6T-T@x~N8$tU3Gi8b0{$XR`F!{iJ|ABJ!}tn(9ef>MhkpR`@DK2B;Xm+i@gL!v_>cH$xEeo={|uMnKjYuS#rXI5M{ptj5xySI!Pn!f;Pdz@e34VMw=SY7pA~N*I0jC_$KZY7K)es$1$M%_;O$@wyd9nneRw)vA6|*q$7{m!cul+-Ou?(+wO|Fj7Ty3>!W-a?VI90No&j6p8F*LN8Sjc`!$Ej9J{C^K$KvDRY<xUE9nQn2<1=W=Uxmx@SMjwlg0IE*z~lHH{4BhHpT&QNYG3}H@0FKjuP%d^#Z%zrcnY2hOXI0{GF1C=GT$q|6rRUbQ~n#-QT#Xj6x@WL!gs?r@ZI<tr)ck9LsR}rygdV_!k6)>_>*uZ{v<vEPQ*vxz2T#HZ~Pv3FMbc+7B<J*;%Trpo`%<hSK#&V8n7H*1Fs5`@v3-rn2J}&>%xk7UA!T@25*SBfz9wXcoyt{XW_lz0K6AI98SQ8<Ky6q_+Xd=U&M3pTsR-k#h1Vp_!4|0T!(MOkH8P`BltP^Eq)Ha2!F&c;-!)dPvfd7zYPA2tET)C_&u(gatD5dtET){vi10{_%XN&KZb9Hi}20(GB^ughR=11t`l=<%BRI!Al`<=TYoqWpGHl8Y7~Poge#801Mnd@23PEZ2VghY2UqNZ2jCsB3$EA>55PaecDQ0X9)PW3I<8nB55SvXeO$379)LH(nz&*$JOFQo)o{gHcmUoCYvGCw@BnNN8{mqK@c_INHpUe*@Bn-OX5fll@c`@&yW)!3cmVc<*|_3ZJOCeoV{ygtcmO^Q$K#6A@c<kKr{jt<@BkbFXW&EdY4BBi8a@}Ub&BS{@?~(3Q?y=`Z-!@`qV=Wx82sHST93+qh3c9r>$fcHyDZmKS??+A2Ps@rWq(Lz|48MUD*H(?`%N;}RM~%&tNlq)T~lShQhpAea*Fmh<wxLdr)WP^z7ei*iuO<COW-R`(SEBu*D1R0%Kofe?caXK?C(Qi4xU5JP-+w(gU{fKQ*l4+2dCnSPvU;q13rl>j==r!uW$se*c<o5yJ2r!@gCd{Z-@8bifwT}{1a@8E2iOocneI!73<-C*c8^o6>H#rcmu3~D^|t*unDY+D^|z-uobM1E7ryRFca3r6&vDycpGepE4IP?@GjT}SIolw@Ijb`EB3<u@L|{sR~(M}VP7~LR~(1Sy+~i$V1DmVyd8+Q7(9r_@UP)#_}BQC@KgLt{BxS}{qeRFz6U?W-^2I9&+xtY`|u$CKE4Ycz<1&A(3J0khwy#)KjZBy_zgUSe}kWdG5jR{1N<8Q0Y3r1#82Rd;pg~a{0o}$PvCz16Z~Dzv3r-Md|SM2fLq{Bd<$L(-@^;>9dIwc1K$qc$G78K;VyhDUI5?03-GsT%A@htF)OK5<<kG@zX}w6h19j8*nb?bf3x_<&EDTU6YtCY@VR4F8TGl2Q!4&XT~r&X74G~Skoynr'

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
