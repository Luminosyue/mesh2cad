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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f56267bbe2ab41428f4d7148876eced1/part_009.stl', 'relative_path': 'f56267bbe2ab41428f4d7148876eced1/part_009.stl', 'source_sha256': '0971af7eacf578e9472fa668868d05151a26e7837a72c3caaf53c0293918f2d7', 'input_faces': 280, 'input_vertices': 250, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3200252056121826, -0.3753493130207062, -0.1466415524482727], [0.28779155015945435, 0.2529202103614807, 0.024180332198739052]]}
GEOMETRY_BASE85 = 'c$}r02Xswozs7eG(U}<0X85wz3?o{M8nTTNgd_+?KM^F+LK1`^J9-&4O308+i0Cb9l&wS%(FLD&wCF?|A7jRs^ZXy*aM!(S-F0tf?e+Z5bKdiR|NGr<-Nw(`A&;{nf8~|uU6Nkslu{JiRakLWM)nVj2np;TUSsI6(RPXxeB0k=jrHl=-mjaTGE#|h?bkm%FwC`)>gq9|fopZubwFrXL|DMkKA~a#`rG_g0fWQ)=lbEn0mJ&|e*U4(PqnJ6?p3R+<JAA-UqM?A-cc71=8D#9!eyw}heVqi@0-FmlSacgqmx(S`&1_>pK%?ku6VZ^8g%{w{E!RqjSl)Mo9bg$z&G!WJa1ErlVdWzKh;P42}9r;K9Nb#q~`FIlBXn}_BS`duU#F!#b?DC)VIFQI-6RT|ApV1jwZ@0D*`s+`zw#&TeD+P-jX~5^;*+!Nco~ZmrzdqVGA@n1-^3k=1J6B%Wnhn4~&)kRy9R=rBfpEQ5%HA*Slm$J?VE5$2xtO#Bn)=IL4e_$Wu-Bg0Gcam<Ek#BKMV1L4L2LO1$shZpQa7{yc{`KaWIt{pvT!$9VdO_#J)EO8c(aiuijj!Pnkpn9!?rkdHBDjg+75f%4{I1HR?$MEGXDB`B|F<&*nbG**0{jTtC+ZOAr!U#K&D^>Efs#0^bAy;^uh_{REhlvmoefNz=i0rjcX2B5tDO%G|G`|sf!gU%g;KCZVN<)544Z*7hCGB&k=ZxoJ$uiP7q@_O`R#5dN>hHv@yiabx>11X4KXN276xMzn@e`Qtt{k<gq-P&vMIpm+xZb9Xwe8p!m(9+I3;3pQ8dMmlf_x^V9m39Th@7)#g&Dq=0K1T8_^fO~X{=N8pelL_ay7q&wyZDWj=hg!ErKP<)E&VELH~hqda=*c^;H$6JNc;cU6mhh`=kWC&$Cr89zW;p$+SRh)g7_VBq~Fv}g0D3#A-<iSU@NaXcS1XuO|vqkKUvV9v|(BBEj3QUx32U+J8MN|?D*0*HYO~__YRGbuXg!(rsU<l%@*H!@tQp6Ob79=RfezpWg@=1JLMGWpPD((<{KY}??Jo*+u$3!LQ_$Ge7xlEod{nKkDi0?Kkk$EUuH<0oJnYZ!%jhY<>)80m$7X5UgXnaC+gL_65*R3VTaLft3SwdsT~Vnefnw_exLV{#0j4SUw7NR(N<pTy%%}vDI+Al<K;N`u05pvTW4dOo0qZ=;l46^p<X>=8hpLWN3^p!d=Bc-pZ1mV@9nqXxs+cdaTW&1d{M9OG0!i?g+8O3_%odMz;Dn8`IvW>ok0GDkEVHkF)qw~G4PG__A_ul@9W@sSr_#e|F*xxDLGr}&Gdn<85;7}pCwEA{YQ_Ze6>?2(VjQH$G9=OM2a81V=<oBlz5c4bclejHGE^*e2cZe^oM3urTnU$X`Wv^NBx$I_>ap;{FBAkz~4MB9dTZ#qJ6CXI}zWo_JyyWD}y-7;1XzOqf`<2`b4ix#J`oj5cx0Nf_|(<=0|+3_$aIkX7q3H74z*Wn{PhaH6L+~&6D}4LcTp;wu9RFFU-Hjc;6F<pHp!?e(!u5z8RsS-K?kP%D8Y@Ec11Xd1p}GD`yni=Xe+Kmvuc2Kc5+dIE~%lD`}&Uzn)TS8Ok?)eiZdT+k6!LcBr3>i*W{gW#J;^Zv-7$g19G^h+k}rw8QQ4=%<#jIQV+$Es{^D?<m}NiC8HgG!*%m6GLOruH}15`O4!Y&z$WGQUCNON8qpMDsf6ppN9PGj=@(W@}qsUxCJr~jW(pb(+lKd?kO<=?YP4SzH;VI$+KzL0(_tCE`FZ7lF#rSvB<~WP5kt2s8_$`*ADGHx`Oy!E26xfaAOGkW6KW1A6Oslqp8^j^4WG4^M&5iRm#tDnvLi8`Vf5WO3kzIUz8h){xf9@d?j;~)O*2h4%$;2D{)pXl{^oYnU8uZ2TS=5%f$b5#2#_2^<{m{TO9Gtsn5{gwBPf?S3>t7PyJAM0zT(|a1dH)H0m|`bnSrOr#FDF2jxgV@$86sQ5leP0Di%0^1Lor?uUFjJ=_QXLpk^sr@iR6=BoSfjn$iu!>?Oc*6}f3QeJI@@@hba?B7a%N=5mY!WpQS`w%U&HGHM_Q{=B!v7o%-(h9yA*$4Bj67&-JDdT*xE*kY#V1844lTe?wAQ1DJ>N*SkM=vYur_#w?{2Tqy|BdCr;!j>G<8tH#$!C;5=2fj?N0}!)@1-N3=hg68FP=~I_8jRC8;;0+pk{CU&Tw%+9P@e=S?}ttmi^88_bF%}qaU8DHRYJhTh7%EB98APJU>g*99d_M_#Z(WO9S}UfzGntCLTaLXgS}Z9jr-qvL41gl6ELLQv55yvi=`!2j84o0_|g&@Pqh6o6G#Os2qIjsFm1vsO9rve*4dQno(KyN1Ya8e%8{O9F}_9VgF^$eTjKhaVrep+`0|@LVNNP^3)rjLq6uip77Oc39`QI+>Uz9;ZtNk+iySmkJ+&no{Kg6x%8KK$KOzY<V300;kcY9UfiCBJWGxde@zjLOFeYtKKL7kq20_+iOW&`<W$_RB_$H^%{77W)lOrOk5=T3<Z~!G9{CTwD(jbbS&S2F{fCp`drUxk=vC6B-kJj@;j`OT<f$)D5P#-Q9iLltK|XraOv%U9jE2sxCH?tcQN%a%g^Wj@t;3LyIyX!5nd*dnp1P<K+DAD#P1?tE;8e6%;5p=}o&HPOImmrB?ms(N*0nw_C62EP<{LeAleEtif9Y3&J?5gm_#ni$UYslOC$7Xitq-|@^+Wl2sodB5$VI4c`!DD(O7KqcqgEy&&VvMrbEdt-8F2%?d9s}J+i5eUf7W;i-&hxgJWV4}^4zbjgWvz<0(>qMCjDxk$9m**KVkD%e$nBZP=4AadA>fOvY#=xZHBM>f%w+8_c4!H?=(bzHN%!7AM3$g`{7q~!T2-|c*y#`uc(aQ$wA^jc!PCUT~`(LTAsdwuljAp{9v?vhVgIdr0l?FYXtTm)^Iy1A3R%pUB&$Kd0sNzU3TMh?~O9=#f?C}Hw&Ba)vKqGk0tJw%(u0d$bPHa4z#oO+Ck>qX7^;DakVb)+u~nc)}fXau@5#Em&Uqc&5o0E#)Ej-AA4Ql{J*dd;`u*?uRlI7{)msVu2nCzAD<UolJ#YvJJuKNUa<rC-Lq8e)AUQ}XiqIB4ZdD5MAomKzOt?rt%3RO^SWlZT=$ppw*kH}z;hSAfAkNT54~DS+`(b8&bs;higqoL0N;3-E$hzwS90!iJTK*|n6e*O5{`asjID-oqRjG^dSjC!(Y}ovif^AR^SM(z<`Ju90erLN4$Q;aL0#6H&KWW<Y`QP|kkDRuk6~$RFZ110FUiy02jf}&E5D5M=`$psy@zEVwWyJtA3{83opPNh=jE-lB#uLX?2G=`j(w4J(i8YbTp#oY-Fdm3yR%%8pXv~Ue)ai$XTA0#d?nu#+1D)}gngaSD?@zl>-1UYFuskFS+d@^=a@21%S(SQSwhy!a>Zr8{bo3PHFmh{Bkz|%K5FVXd4JL>Qp*1;82wjMKFa!+$5F=l%y7iF7HTZ*8B;;#-#1M#E-kfhqr5u5hSXQD6ylqUu3?{`-d&saWj<zNGg;5>JQTme*&UL9mYka(J{5oZlm%bKPZ}-fqQEIKKk$5~7MTiPYdTV%KhN(*snhWFKaw#Xw4+63y&rv9;;7~tXydZ7zX@z9^TN}cXb0u+1&O~P1im)+t@&m9sCf@a`RIzjpx)%?l7DbIe7*O0=^svB(*7x*;G5k~pxxAw@p4Xd^uTy9wuVdlJ9^4_G;z4BuMWM@UzH{*;_G?#!dLBL<h(JfpPVc2S|!fB{Fv{Jwo!<$Ja?6Sd1<SRw;4S#-zt8!r5|63+5r7DTIwxx48D2sx$JYjw~4>viR?e-B;s6Y`7Ki7546YgR@Tb8WjWSH&dc_7rQfHn#rkGx6)JI7Kau_yFhkzwtQaQyvozU<=?=57uh%MMN}hE}h~Is`yw}?{P1-GQUHHa*`=#i|pWi<;E`#x-jJPD{#WNYQZ){f?z9pjo-XCb?W=Q-^HDtV%DvmtN^f-yXyPlj6?Uu-Uv|`@!eqc~TnHNf$@*X1H9`~(OY5`xJmxTJXz}8ZJUT65$Hf`j6SnSQcU;5hYy>f1tk}dV#_Q8Cl^j(Vb+PC#FKkF~Miy!MD>uA>l5<g<B?AM=uz<V$?s<q^kHCg7hBmQy@UbtD_pDgK&c}jEpQQot543zzO`6!vchB>3%jIoR5c}<)IUs?Av-hXNd36js%qwuX6C*{3J-($$f3~|9Z$MA}j_oZW_Wxuqz8GQBaD|xT`dH=J{SI%9{@5y@?p1YO#W5qus@8669iaZ~?xe{lO;}w+8Y$N-$VRxkbp}z87uvD7tD^i@#;eJ!I<UL_TJ9+LChr-uGuF8Aac8}z_q#N+nYp%%O;;~%T{aP>JTTA*&JJfWN^GkHq^XMl*Cvact{tuW>G`B(UjYIMt+d9-^|3Sa6{<Wa?smGU$BDqC!uL6p*G9ciKe=4w<w!hE%-~UrVNZtS4KNU3ifB#cKIi##8&b(|~np%Zinp~FpBe^WO0<{jg0=Y8vCvs(SHEKh0HF9lgQ*v!`ed^ET`s7B`R^&!xPpUWBliZxzp4^=5MeRWLBDbUdLT*RyNbOCwX&-V&a<|;87d4RDha5-_qV^{Tkq1);k_VH+sl&<P<S6QBauhj+s*_{LQ+e5V8g(*x8u?f1OtMYqk!?DM{404DFB{LLE+Wq*FQ)!RUQCXst{}&g6R4}m3FJiTT5=*enYxLbOx}=tZKdv@ZX)j>r&70(ZMut`N<K*4OFl?GO5IOBN<L0C$;ZhV)WhTq@)_ze@)`04>Iw1%@@492@@4XM>Ur{YvXz=ewvz8t|4F`2enh=Renfsoy+?jVeo1{ueo1~qeM){q{+;@Q{5$zyylniQ`ilIX{EqsZ{EqyV`k4Hd{F<6geofAy-XZ6ZpHOd-pO7C=uaO^+?^3Uj?~-p*FOqMQZ&1&XZ;-E2Gs#!Um#8Pnm&j+SY2>ryQ`AG`Q{;5&0dhL|2z3wn2zg)bwVRqk-9t_xZ>DZ1Zziv!ZX~ZGucjuESCf}h4YEy_ke8F=s0+w(<XGx-ax8fUbs~8Nc@lLzc@jCAI+7es9z`8WwrMDN6giSQj2uZGLk%O3A&=!{;|N|h9z+cx4<Zks_9G7<2T(2K0CEp%PjU}(7hX2@r*<X#lYOXuWFK;CY8!HEax-cRax-#cszz>1u1obG*Cp4Y)+5&<yHRVB-N>%g>SR~4O8tSXlE0@`B!5pXMg0f46uCI{J92UIH`J2kZ^(tH-;xWF^HGbC^O5sV3zGAY?WuXm_T<lhHnyYYC)<%7sD;T6WJjtK*^yj;>P#*`E=ny;E=n#&ElVy&E<vq8E<r9stxPUMcA-`yyO1kUYm+OHt5WNetCDL_8<A^}-Km~rcX9)2b8-W66RH=v3ArV;9l0gBEwv-rrrpSG$-c_pdqH1bHtx*J#+`WCxH~nF+@0K)8bt0(4yFz!2a|_T!^uO)BdAg25#({y81gvs1nN}s1o9N>Eb<icY+g2=Pn}DiPhLn}OkPM{N{uHkB`>2Uke88HQWME5$!n;|<Td2=)D7hI<SokId&DigY`in~^7FQ{cXs%n{#UTS|8(2n`|5uT`>((J`dIkoFKgrurvDrg{k$D9&h2ymvu)}N*iKx^zX48I?p^'

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
