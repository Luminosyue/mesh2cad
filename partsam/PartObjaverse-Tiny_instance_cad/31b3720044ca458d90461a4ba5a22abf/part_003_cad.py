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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/31b3720044ca458d90461a4ba5a22abf/part_003.stl', 'relative_path': '31b3720044ca458d90461a4ba5a22abf/part_003.stl', 'source_sha256': '3f6239f1b3f9752a84dc830be700134d3cd0e7978953f77dd1426ae0dd8957e3', 'input_faces': 308, 'input_vertices': 210, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1296284943819046, 0.08284348994493484, -0.11132298409938812], [0.175540491938591, 0.3685843050479889, 0.10745313763618469]]}
GEOMETRY_BASE85 = 'c$}r033yG{7RQeuWY8L-QR6{KM4Cj5ML01hrVwKhCn7ONB&NjBD@qAM(U_VzK_ZD5k{|;~E)o<q)bzB}ttu^jC~dWPukY@){@1(r_Ils@-plvx@Bcf0>#no*+WYJ~e1iK|uHqu`UsGv(S-)Mr#!E4rB^POKM9l0d;SsUkQPFXgq?+W5Ka*}4G<;z2=t|ODX@UF1h}iHL_s+6=*T_!pUb1`S%$V6RVNv5}#!QS5exI=Eu@Oc;c5+yBgz?(LuZ^#l+_sgMyh#2Z{~V1aXxW?eWk!`B`d{fTu1C8c6xXWPdh+#qAC&$lU+y?1U#PCbEQ>tSdoG8{Z1{%KF8TEOC(}7k`O8xCcx(Sn@#<%b^19pd9Y-7_|6VBhhM)|KdFcwfay_$BEbFxLP50F`tYJB?nDj%od_!Dz9@Wv;iR)2Ymzl>~`)`U@NB)%C-IhQ2KFv$+aH>rB+M4AS^;r9+{L)u$<g0%~Skz<fzbW2S&tH7hqw{TAX0tz5zA3*h;6W+X*?OvFyp{jDKl`_kubc405%PU*(SDP9tR`Q6+3YCw<@@v8pA})`8^&%dGhbh8-?YBgzG+|m#mByqUB{EJ4{A^MHQfK5;&rb^mD=3@R{rb#Jg+nPO7=O*qqg=wY|GcGM<1g7VBd-J^b4`bZ|$4%8)~|8-*Pg_%=f>wZ+d<e7iWt)P4QCpvl3eOs31%K{h!H~eI9ZjZg$AG<;%tMsXxm6o8(K+TVJI-PZsb#e5;&%-LL5-)W`gQ!?t|Gx~0?y$*YWf?RS65qaVJGpX*vhT<7ywRHwYNKIKs_#FMYYms1`oA}HUMul88Yb+(#rQK!x$kK(nIaPkc=j&q;GeYj5F5#;M{jN$VzyfW3P^Y`TXTSc)S`5yII-PC~nmAm=8YS4uCl@?LOqJI6fc6|P%y*NsK;70EM?L6w6QndG|c|E3iDc3XE@0&orns<fQYt<^tJgz@-d~9+i-RDWm!;~i}p{To=uN|8}zTPpmnC3OKANlIl#pEk}QVYqC?n%Dn+Ms~0S6)6+X2X{z)urcHSx~;4^27&nyxrG@Wj1`t(2(*gj>pN@H*=tCeXaYH-`ZCmdr*F<Zcp;%<sI2S@tE>UyA<-3wO?}G$1-VN%F?G9RPWc1Ili3#U8((q{hZd+7b)Nb_s8wZPO7uo!t2z}Mmfb)$Eq#l8>%OfuTRhy(d$R7Az!ODkbLE05Y;a&f40LskJRW}s#70zhkd6y*LnYs=lDOH?=a7!-#n4y@7E^ZF#7H_s>k^|sz-5+OEb@-8y&}ezB8SCdDNE_ue)7^;-&e+$X9Z^(E7@X!%<tlu2FyPGkkeTTUsx@)Yu~4<SXBdr+B^ElYA}LzK~!44fS9DSm8SJKIG^8MHcV3K)*EedCAW8xSu<lbDkd~c%6J-(7NdSnsS{(`*5B`MZ8`k?bG<V^WyyzU!B+UUS*C?Oy_g<)n%^h!c&dvc^1d>{kaz1*V>mZgjmGu6Qj8gaV<FB@klDgzX+uM%S&>p|GMxT^0kwTd42b_;dyP}!SVLayiXh|c;D`w%kg)TIggJkuh);$*|)z%{V{k&avr~q>?f|^eU(#<pU2f6?C(2I@yeZ%oM-E+6zX&0Xx`5kGI_rhK4<^TJ&Kn+yK)|%yX4E?H=uZRT?zZ~Md=i`)sy;T$nZL9%U3>%qW$pNpW3W|=cQQ2!`C?{aQr7{$k(?1%6<N(68m;vkgsfuqIFa}&e8sn20!3DP9ykv4{gZ4{wMO~F6}vf&)2*kwpGiZy0iJ*(S3{O-r13SId&tT@8Qq+-<vmJ|K?<#Z<BW1e=A@4#~jP}9F^+V4E;F%NWTN*cRkDd$@_A#EnnwUm(Q!v3FIqtqIf^gDd6+a%2z`E;P?$uoTnDf>m)aRUJ7!_H$2GV^Y&&Z?!T3<D~jjmw|m6_^Zx7B1aSR5>e1&!+2u6%A*2Q6QPz8sufB5O^*ZNOWXo5wF^@-4{CV@5%<ntT6KG!6zH+sk&xeO`<QrxM^Lf>FAJ=2$>uNsXek5%mUl;R~*3l5Zp3g}uUm10U`_tTx-k%Lsck%pRzRS<WR~`BDujfkk7q{Z|ict9dJZUuV%bx$__;qK=m;CVlH)aK&4;{YZ&y}@K@j00FA@xn)Xc^a$GK=TAHJ0PcH}JW3$c_D`)49)&8e{+6rn>dguN1G3b7z0)ex6Uo=lq=djw4^o+{k{v8&tpHrlP0#1aCe!uB8?TU(4-5zMK-y=R@TtbS}vcda{4(37^lQc@(cs4kTYKTEOSq(kfJsK?`F4)-jGR9!7bzkwZ97*o^Du^=n=s9KS4|&!3LHIZyT|^0lyTeEzs4Q~h$^(Hx(4_L}*+$c1A#eul*7=l9t>-`i`B)Ah&+{61KrQGR*XCicUk+3$CN>%6*;e9dt-pPx0BasHd9I6iwb*V*E2?$5!$b9{L!=ZUqa{;RWUoFM-(*Qri?L4A|=`jIa?^82##@F~|hcmVlo)^D8W%mS`wNjUk2p)WXoZ7{`ay=SmLwmQF$)K<A~i5ED}m^1u2yxMK@)%2_6E06A-r21?Ajqf|^KG$>qOa8o__=xVS-hIsV>uylIyx~6g&GQ%b^Nx{kdSB2I|H;1p1<IoiK0*1_viHmBem|sAyl!S6u5+?K`Et{H{5jlv0N=NE0QrX4`F!6}fBw9ygp;q?8+cxadhvamZQ}gJ11aA0KC8`1<@l_Y?6>!%JlZ{teD%u0)8xN%ockG;%YOY=Tz^I<?tgL#`T7$dQM?*<k@F{9BwtxFhkPwGgX)n}u5tYXf1^BxUwp_nINs&>1yy)nb@Mq-@DJ?o{i%ZPbK_&4*IGNe*1F%W;C0?qZ0_s+e0iB(_e^GgL0$6IHZ}OUyHd#YkE>6<e4`3~ukrWcbxdx+c^p=rHuu%NUVOig9eCefO5*&j{kR^VO8kAKOI4n4L1*%n?a|zy)h)TtuDv<FPHo=L!&3Raj<dL)3RlXb)KB6%dna@J@3r{*(d1>EfAJ=ZI^{+6dH>iQwz#icr4E1piM-44&fb*A^m$l)r_xD_b^LA{*R#Wc*F*8(?@fkT-2YUUlNRf1@&~m!X}*8t);jJ_!$98OSG#fjWiR-?gH(Rryt;7TN-pwq(UAAIR<+la*UxFN#jlN@HgQXP@|Glt;UKw4kzr;(H40Pwnbh`AjZ@nFS3fnj_3iZk{?xd}Si@f9SdAfg53~@x2YeW+2OkEPLUX{S;B06bSf~bGfcq`N5S#?v15N_(gB}L&0~bL{!A0N`&}{Gt@P4QU7P<pmY#bTJaU7ZnUTz#4jUy35@TbtD;7`FN&@aFx;PcRn;Pc>1(Bt4s;0kCaSZEeF5%*hxA$S9{1iS%!1bQBP1bh~H349iO0a^jR04{@Ofrah{mw^kQ>EQk7Z9azJUC>mp(CuKcH@0F;H1KE8$>7hxQ=wzQQ^CWb-N8b;fyJ7ppqH88ZP01pZQv=;!Qd(2fzY;Kp+4YDygmy<@D}J4@D}hS=s@r!@F1uUSg0R33$NdeA$SvX5_l6h0y+pB0S<=xfrWMe=NiXOiJ#XTa2j+oI1RiN8VTMCo(vrZo(vuf^#}W7ZN_4)#k%gm5S$8~3Qh%2hYkl%2ZunrfkVJup<ZC2?%-6semjQX8PE{$4Db+WSMU&UN2ohkXnpW*tVcSA;ACh7I2k+<8VsHY9t!OM9t!RPbpi{m0~UStz`VPGy`XMjFK}yU6R^-$U@xdUhT!JVR$!rx!S2xd7=r6T8-s<qfPIaluW_`%5Zn_w3fvPs0vZh-0gi&|z)|3(&~@OY;Pucv@OtneXgT;0_;ctf@aN!j(0uSYa4~cjxEP!P-44zGr$A?bQ^3=pL%`F(gP|S4gTZZ~^}%hywW0OEwZYC%7qHN`z-<xdgCW=v>I`-SSBAa?7FreTgE&77!4A;MU<a@StqK-e3G9cs4j6)+pc2>#Tm@PQEYu$C1g(Q1xCYc7Ec9*gd&be*IND(d4upn*1Hs|Y`QUJHJoF=QJU9XR2{-|~7J3l87JLAD8hikJ40;B9415w=06q!Mg{FgZ!8@VJ;GN*j(23y9;7I6Da3pvbv<r9`*dJO4><?}LtpRQTei!;SSZH0aKjOM$2=;)!3-$oJLF<BrHUYOc4sYXl2U^pNo8ek$H8XCAYoT^#+z8h~tDA94Tnnvb#%*vd)YXhT;aX@@GwzIQp`K>^KCXqzX51dv?J*}AzIaW4=m2nk@ObDr@ObcC=xp#@@Q2Wa;LfOZ05k|Z06Y%*0eBpEHZ%r28@v#@7~Bax3WD|n2Z29;js|}Kj)Bes$AA|@mw+2#Ed!tmH~>5b8VVi*j)l$v$AUkGt^$jk&5%QA53m9bg{t6C@Eqto@Eq_e=t{82>5Uvh`+$3ZRp<n;3Z4gz1J47mgf0WOM2~tw1Hiq&BcWr!Bf&GFvEbnTmF!$9zv;i`{QFNwZvf{1QOEj~mS3~YUm0Z#di|w4xPMh~t{WdpJ6iB9;uDGVFM~NC2>'

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
