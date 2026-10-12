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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8b8e14ddf5104c579a6dd100ff8c0bdb/part_004.stl', 'relative_path': '8b8e14ddf5104c579a6dd100ff8c0bdb/part_004.stl', 'source_sha256': 'a00ba0c0316d59b2e346070a8bc0bc9186ca7b11f7f6476e77bbe8848cbce8ef', 'input_faces': 360, 'input_vertices': 233, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17237988114356995, 0.1579466164112091, 0.11453168094158173], [-0.05004939064383507, 0.44317546486854553, 0.18967801332473755]]}
GEOMETRY_BASE85 = 'c$}@833QETn8&YOYz<B9<x4CPwG$$=ZW>#xi7iNR$zm505`?&74Ml|^Nb1^yEF!W9iHmI3MywI^Dz#M6S~_i+&fNF;|4n1g%sF%BOq}QZfBEOh^S<x%e((2vxrf)l3Ki{i_;S$g_m~|yx~@*AqK3{+7a9;ecdB1NNV{3H7nIZ4im$#t=%yhf2YZbvrwi4EJNXBM_ys$;X-+)@U7gx!PJuzebAu<&nh+H1AE5lc6K8}3SpASG6K4llzi-v4bLTc%XXiHBV(tI<Rn0mD{aV}nQ&zQHs&>7X`hJ6rS*fl|NuKzrx*PI+>!I+yH;S))YLEQZ?x#f8jS}DB__z3`y*I?yISfagt$#@!<MSw~qu=caf7fS{uNx4PBbrbRev11w`F`f(Y^CP%PjjXIG1NEOxMEzJ67en7UPyg?q%-Du`iA(LZ#~Sjn}g&V78W6YgPYXXM{k#LjcekOZ>Wy?jq6Gs^E#9Grh9FWpSfS^7#-r^Z+a{F=Ia?)@5UI+v+FN6)%RNQC8=W^7J+eXM_rZtU#rWwrjGNFAM+G_>t{fJ^5!7F)<di-DM#vC@@HaP_xI?JgBkfR0x|#jjl?&*8O1kT_e7nGo-(d>$PRT%yCZ*ODf(YUcUpY!7MRce8#1mrp`p|<*))UyrbO1IKROxf8t#DlGoGP8YZpr$^QZ>MU(;R2)tzgP{6%%)kFADze%%A({#ps^(ghWZ|H@nT-MG9w=DG3$uEUYrQ0K4bXC?pKdCcGWgw)Yz`~ZKepVZM`@{>MmJI;%5IdT$pUUkMiWAl-pa!%G|nQV*er_(9;4~u1<#%asWNIwfQQ0K~TSl4BD@s0bF#Mc~)Z^`#RRK~i#je?(?g6k^oxa8|*8&PM#L7a;TPcfh45#k%lWuebCzQlUF4@3UY1k7`0I{ZofkYDK(#x-ri{L|aQHyn}q8=Ondir*Z*Ht4F%-*{`I_=cFq$nW$G_I>S7GEXh10rG2YmvId>2FpB+@o&zEzhgD}KdNc2{CxRq@h#sa%6xQ7I?8;s(kt-mMM@p>g7WBFwi$J5WTT(a+og{F)Jfz!ZpL+zV}V}~FTUw%W{Kq2b&>gKF7Pc&x68PC@BZjd$};3n^ObdJ?!%>yrSBq)TQ3mjH_tgw@^8-<->`ZO`Z+BJ=gWCI{PN?_{|oQ1kN2lw+=3%G*J<8TM>iC{xxYDI>a@#|d~<tW<i{+*x@<NgKW{kZxoSK1CH7DGJ^k20@PFHj^+splzVxam=HEO-=4oy>O!}ZJ?u`0I1MUwmdlty~{nrkdf6D?n7rM+esc%VZf;!9g<Ni?PmCVQF*$Cr04#56CyMz9;Xoz*azKeBTdyGEhR6`w~nKG`{tpk3(qY~zm+Y#q(@&v56dO7&lHey}D-m)&s;y0(I&d3p1*Y@gC-*ot{_?9B}r)i$lH~5vpuh9bMYkerz8+a9UChnAc{jC7xH@PCd>53-%sEe2**Mm9Qj5<|1V!e}Rq5p%jQ0LNU+y_D`N_}0$Oz{o3FH1kQ-y-v|jtt~GhhkkVd~qFyq+;Bq<FPNXCggi3iEmDxEPXLgwP3yBJ5fLC6P(ASdg$lg&8Tyu8TzxcmYiSnq)5~`5RU#D{*XHQq(!LXGFs+i4mgkN`Q{w)^<Flz9{r#0Qb(_wj6T>lLO(Cv#ym6qQRlqf^|IHM`R+vISBktX`G3vFeYomy%qL={%tvp+JdJS!(Vs_nUYi%LmY-`o`(a(#Pf$NL8GR1#i#khOu^-2}oh|DdlDo^gG|L3smqxo|UC*Cm-ky)ppXc2%ZpD{4@2wA_-pba<9}|V^`|tIVZ)ws9;|{8gd9<60I%%IEKc*Y*M|azxZ^7l@e-R+Qv9tsHlmBj(bycl{{`Yq{Q`WZ>`bpok*gtUJuKc(7`gSpx&w^PPH~XFV=31T5&jUW_r}rPo_l|>~>><83{0-`_zJ}*W%o@x$_ZjjR{)PTrOu;;#Tae%Rn)Jt#UI**mcTaqSU!m-mX@ooaw){Hs_gun$^`9;Imj0>mqXx>l%mv@zJ>>o#^da>c?yDQRVxF(VQ2#ETgC>vbs8fF)^0W5h`S|<yxc)r?#n-Z1N_~A)F#2|L68yzmaju&mLjOK(1;6Ke>Ax|#5YMAY4KdGWEAW1`+y&<#pbo~3SdRNuk8j~mtBm~A1vqzx<LGDhvr|$(>niGx7>euAK3{y(^eLE6IbZb6KNI=8v{LcsWaIf&KR|rT$~fFN=GDS|HSO0N$$$5|tk+WbCC*po6Y(wKdhBn#65QX0T}Qsf2mZuIGJh?v5cv%|VE!+QaPE2>L;mxTxIX*1;(Z`-2>fj&=<}CX(C3V<sN>&M>Kh9@q`t9yNAV4ZobcW|HV*fPpVPCY4--<Qj^SiHo?rVC;6MHo&(j9;vA>>6#n<e9$92-(j6UD!g8Y+9QKty=F$}FQzGcUc(ob`I9NyC^<ee117}ue$wmbS3nkl|Ewg~-??~UiOO`7<IrWf#j^2=kKkAbt0@ADS@e2spZw;9AYEs94!7yN|tSGOm|b*+eVJ-;%}`;k`2Pf3t*jR&4#-#>YMLh_?eqHl$<*sm4$#Megb#(Z3R;9Q(Kfc(+NuwTvF<9_v32>i|qrM~`XDC+MREWTmTH1zZ5=zQ$^l`N^>dl=@EUK{V9rHSGj><6QM&rI|`YMS__dahXS?x(n(=effl*%IUK{1yA_`1f(CQyPr?wKwrx9#<f~#o-n9Wp;Ip+cQUe)8%e>Z)~^<*VUU7sH3YVzRAuF{cn_p{3Y+OuBtEa{M31%{;ET`|J?V*dHnHKrqr32h4~CQg#CS52><XfT<4jMv0tqt#W$7nz9YYXIt%CV@+jo{y~R0A?1%eU;$Y-&LcZQR5ZBdCJMlG#aJ-lH;PW)~VTSmTj;NomVcf^r;+ujBk)L!2eQ2~5zTaBR|DOLxzE-jd`_(NM&!3}f;pcjzKYbeEJ{C4rd_(9@I4@hW@ZRY9d%E;3`3QXH@i;FjCE}YL+Dm=YoImk?;l4tAEj$AI?&^j*xnA%m{(^BoJZCpF5#P|#9r@qk?+D$ByJ=<5k^aMb@9}i;4QVg1k5Bd@zy4D3Ez`r$2R^6Ffg$2+HSu?c@n{%)hpF)EV?O#_@8RDW4?lAq>idkseqFbRKNrszLvRG{hi+lVWZbbwaG#(0xAfU`?p&(Of2kMzF)p|duRkEZHt#F!Z`4k_w>0t<->|tr=A-rc9Ooj*2YzfVTvs>GNF7t3LE>Ak8*wgv?vMPA%`k4QgII6-1l%89+9Ka`xQuIhJs9Kao*tF@i4Rey)Ui;0Zpsti^!{tiGpGoCa62l#_P`zfnQ`!s#Gy{HEw1xRPjJ4PZG`{e5$-3xF}VNO%opDh$m{CxN?ccwzNl{uhF`D)`EQ3{KDLc<f8PHR^=EZLeta6v>B<<~=bc+&+%=xq$LHy|A3n%Ukvf$xqMxJM;r?*iMtm(M1b$dwJa@YM+Yzbb$@^8W<+u;;{X=}q?CH3E-WB7$C?`{V(~4;HGs?BFtZx{Rf_)j&8|U=NLDV^a4%fdSNakbsCPI9zLv@*tKJNwQ6P%kYb>4JA9ljSC?+3zvFdqK+ei(OtdGSr-#^XJF^?SS@o;sW)<9?rwao1GAb1Lkh_?pWZ<QG<ue3Q#o@l7|L@b8zwIPVVj$Ukq7{R){b{kPnz1Ha~N?0c3G*IVAxMDacF_nrCvV61D)0r5=-@f^_&OTl$pX%GC%{-`sn3F?QhhwpO(^LM(8>+q&Qe9PT!@Qtr<{oL~s-@x}7{kmM-Z`*pne^!kAJzn_y;cPe5S-%kTaSW097*^XO->wk(dtc)@)#-ME_%n*|Jlc=vk=9}t{Ly%?Gd1UZX+_Fmsh@3+zf;ocV!d@t2W4F?JS5)|e<HW6Z+JTaeVFn1Y*}C16%IeV=10EeOeFTj?YlF*ygvF=S|2s%w4t`Oq%~}GcDlfcWj>NtruzDz|NTeOQ@i}HK9cU-wZs3zN7A}-)+o<VT!EpuDzze6X)SV9ay^FPR@7!>rJcyF$UPZ~1E{0PN*9s?$cq??H&Hi`A6w&zHSSP<AS*pXzC%9EP`r<Nh<u3k_E9&Gm98Q0Bk!TECM(@V-b2oz9w+CJuTj4zD}6v#`V(2{Bl0!!E$U<PW3KHML$R59ntYn`HdFVI_i#>T>NT>TH6~jlkUE7tjXIG!g*=fwlA-u(>SXfQ<S`7z!>NAcuc+M_ioF<$CsF;#ew@c7hGGLl@%S?HRy@@jVb%y?C|<%)ypExGr8SJyAZi#njJ1Loiia^2cVj3XKn)=eAdj`i4C(@E2swmvTEI}ef}wabbsc#pHIBND97o<lT}j?TjxMv#XolkT48`FL#s1VFauC<-&rsZ#p}0M@8@UDbb80v8=j1Nb0pu>^-qf+=-em7Gee`B1p1@E%hoN{ebpd$+d%BpRcr8QmR_bQ*hhA@GDBjCZe1xGmi5f>vA}3I{kQ2!9)M#=%c{g=Ec{kZ)jqj*Y)b-@`+_NZ#;`t24<EZ{*f9}~hhT<<6irY}zlRxZb8;0Vh48`^g#h+0>Cx1q6PVGW&PHs!>O>Rqep?Z^D$nMk$WOwpFYmA~!r%oU%okN~Zp2tueNnK1<x|SSC-pEiKOWjIVx|bYFKFCmflzN1Glzft*IE$h91T~3#f}BZBAZL;@sPSZ_yU7{kbcW(Is)?LNPSO2youx1oCo>dpXDD7pjUp?ZPhLfy%TPRmI*zRL3-SnZSB7FIY8$fBrer5_V}@c|sy(@eHL6>q4%L=y%bYq4#r3J5k?WHksLja^WM^tyvNO3O)rH)V>_&AbyOBMp1IZt*V-JSnq1G5g^`VX;E1gdEA<twe4yDc`D~%+Fl9y38l9!RcWhmZ3jU_8RNZvs{z)+k@JxW%3lAKD;W+=YMP<(-!MZQ43%urlJJwaBQNiHIvr)H4Plg}{}7gE#7O4G=N<N|66xqzHcO(y4)^Q@6eO{6B1m2M{|l4BT(ms3}fmChwECkHbW5221AEA2`iLhj5^+>+`<R@#`{l3bUexF*$>th740CfSCexEi$vS*abl8u=53;zkU`O&E$BP-~DIkUyo?AuFv<{*>I1>OgKtcBDF!9m%b!9m%c99jI>P4rEuV2icXZXDIfh4kde%`|18U&x!|AdodLEpbjGUAb-hF+@I=0Ryvd1pX^HwCHs<RGZaTqmywlzOO7Ca!%)19x`V9r0C^jEKSS{`YARW2Hu)I&6hrYP>P2!f^$PVO`3m_q^#b`e*+RWcR$4^1kbh(-e#lUKkD<7PdY-KG9Jz#igQ55;wUDf|fP9sFouT+9HJ^NwTuRL&my+-5{<**0WhlPSP<)o5_%Jn*tTcvvnEWpc#Y?Hn$x4ICOUbhsiu+K9kd<~O_aV1qDAuSg$x7>zHF9l+;wsddWTiIbD&$HG#g(n$HLzTHy9)o)e;NGe%cwr&_~<_n{@369_+y>2zq!R)>pwr_@fui3jjJnf{ij|eJE~7TbpHY8igeo'

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
