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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e56ee981a9504153b98e707d6e9c757c/part_003.stl', 'relative_path': 'e56ee981a9504153b98e707d6e9c757c/part_003.stl', 'source_sha256': '17047cd13c9c204d253d303b56f74b29acbae707bfa3239550dfadeeb6875093', 'input_faces': 459, 'input_vertices': 334, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.5, -0.06531117856502533, -0.13598117232322693], [0.2221076637506485, 0.19511090219020844, 0.1307310312986374]]}
GEOMETRY_BASE85 = 'c$}r133L_J8OP^kA&?M4LI{u;GLVpjrJ^i>uw@8@B!oZ|uwqeO2tjZ`B#JBYpki5V1;qt~$G(ImBxHjE50IS#Rj7iXPodIkL5oX`6x;jV`=6V+m-L*THs^f&fA{~s`R2~t<qbn9$O{aLHpEXm<4}`%kDN&`42q^kv@yMS+EbH@ic9XCGW9u^(VYAAW9yRPqw@>KxQyw>3n>$dONyqY^f6QVP3)c0#Y~y_#I&cT6;2uV#Iy;;<PRx)tfZLvC6fxL7PEG0_wGHqnB6;eF=v?n<4>sQg?}IW!`JhxiVSMqH?u6m;ae|<@1(YOS3-s2FP+1E_l)1E`JLYp`CncuRs1U(xbL}OD0O@rZgJmwWl5#tzn{$8o<}BcQGEX^-1n~-tmdBzuA;W@gIOEY{2APL&$(}-(x0XqxbL0ltyc0UM2hyo&Z@sXs)pCU+H<YqFD>N0F=OC5rT(V#-1k2lQLFeL#`3niXl9L4=lNH5@#{S}e6^B)Y$Ny0mw&xR@t-Z;&3$9HQs1|7I`=KFsh+o{<sROjgIQ{wPm{UtO%7Gh`|4%x`|kN!?dQedy}VuimRjHQ<UXF?Z?1ZOwv`J%a*}dhue+s>_h(dsQr|q=Pxy;AD!%)<Jw7qtx+>%AUw4E1X4;VTO8vee`*}O#ttzF?qJiA^cl?*)dw0*~zVEL;Y*zfR9o#n`TCh{8bN><UTXAEQe1G~4?t6#N*{<Zr)QS2FPpWka0}t@)TH3W-xet$IaNoDXQtFtm6>#6P$Kv_^9hW|BX#Lv0zJ8^zty5V?TaVJ$)|afKts|MQtrwZEtqYm2&3~D%&2#B%^H$c;=BM<vd1(9ke6xLhUfI4rf26O?2kC3$F3+otuk`itZB;6+cj7gEfBa_f4yW(i8Nu(5KPg(xk6g@s_u`IaO8(ia-1nTWQSyD!tA5YhgF=*iEBhzzyJsy`^Vht{@4xYNsapT<E5ttI-YfbU@wD&@9_0PEe)zad@qf8UT-Uqf%ALN|XejTeFMITMCBO9n?i+v3sZjik<D&m#uWwWQdosm7cB!?R|JqH_&&x$hf2@$MeExXiuZaHVcNY1D-|+cub_lCb{L|kG|A9H>itozj^U2fwQ6=B{WF+^^U8!pR$@j&2Sv5t?$9i$6c2V-JkGt{t?Q=z``MGJrPg|(wzix@|9pmY(%6WTLiu|$v*sA9D6612YRQ2B)A;$6Yo>Ijh^|bh&^6lQD_(doAczK(<E0y!!{86my_Mh!k@+%wharCtRNX-v_lKbYF^=kf_Ibwe94ysc8e}2t<WAX=D{aYe`@^PiUHN2CU56|bR=f(G$@mab$UK?f$f6G4gK2P#--<o?`oj=Ak?t8WI^0rCzDeDEkzc`)y7M_=+pLM_Z9;|AvoY#BaE%vJxOStdN2@&VbF5=g3Ml32*{FK?^d#F03Lh)~ei07)h{4Gx3a!umC)niPhl0RiUzwg#d$s3jYZ@(Ag(IdNB$=BAA^tE+Ve_pJkJ%Q_#d~JQnd~JQnd~JQnd~JQn{I=nIU3dnqs8RB@btipo-AP|tce1{=?&|Z^btipo-N`!IzAE#z^(gbT{Z{%ftq^st4p^hq(e`2K-(4b}Gp}dXDs{B|S>|i|fXvtS0hzDu12SLR2V}ms56FD&dqL)F`$PSC)%`)%Np8dU2hY%-RxA11z9I9q?;V+c{+jsSY?h?nH|_gK=4;<aGGE)5WPbWgvCnu1tyS{1{YvI*`<2Ys_AA>rzl#_9OwR$zy3qGA+t>Fo>1+F#tn(lCF?Y8UBLAHq*DL;a(c*bKvrHLxZ|BA0`G48j&5GacfOt-8^|mtZ_H(%Bjc1g3?w%XXeWN6;TwM3Ei~Rnqxvo5K+rD+9x$?X%eeHQ$`Y|rCui|-I`u&@Tzqgjn-Jtk*-gf`Eyjtmx_Pj0qR+q#$g*L5Kd^~R(-qEX-`r7lh^zpoH1x70Q_Vc!H&>L#LwOx7Mwte}$ov^OP>Fdwiwy!^L%Q~wLDbL$7AJ5zFw#RlV^~?J!&)YKp!f@qz+kN1<2FKU-_3@Q{&^+aRi1f8_m;Sw_qJNLwQqHT-2iYI1llWfFp1MWJA2DBfA0mBi{>VDo`w*G0%`2IY_aVMfsj9EdH|gVjh<8lRI>p!Kp*%0%hnU~LP^08)^Hb*IeTd<nzee%3c`NJSeTdO5UOlh&K1BN3JeR)qK19~n=D*C>-iJtETNk!(zYp<#5vSDG*Ng4z??Y@~Uq`Y&-iP?kyk4c$(bkvD51OUC50Sq1K1B9YTaU6ov%gW^hsg74>s01%aw+daq_3@CSw~yHR@Msfobl>|2YLJ6MHTxR@ZBpHmN|X*uD0*-`p+a+HRQW*eNyW5{lgwT#P!t1YNv1J3*VFV`9|fu>%ThOP`)3&SIf73BYf}%#ZT*Vl>5)B{j`0b)=#sS@VyUZtX29mp^p0={r<rB;{Lc7+{Nd;JKz$(Z{Fp(6%F~mQD>BVukDY&xx69Y7!<QasWb9Lai0f1QQ461D;&L5sRQ4vJG#0d-#sv4j^d{*;^X4Jx~Zxm-)Q^MW~c9mZ}uOut|8x;FlxF|=fttY4c3Qm>h<AUdVTmlz5crwkMQx*?vL#o<JJ4)hws+zkMuLO`*ZyTKJI>Pd~M$tt&XoBzPm^rU)%R$e64wLdmCJjnlINQe0{#@zCGV$9c{kpzM=K!w)L+0a=qJi;9K@Ovh%fhtNZr6m36dvtNZr6wf)=n8ThyDGn(&jihaYbug!nmx97h+uQva6-=6=njyC^w-_+}C^I!LUdVPKWwDa}-Q}gBiY1h%#k?z~;NY>HT(QSUFHeUMvtoc4|Ufs4o+x^kjqwd@5QP$Viqwe3f9`*fS^S#=7^xJ-F?23kb^YM_y<hv_sj`9A@o+_@VWMQe(_skN$zb<=rhBF_&JN~g9itmAcVmE)T@nobO=bH598fSgmH{jd#Wqu;^QD6G)g>TpQ|C}!BWTtH*-$Z@e_Y4%i^^>SC^Woe5m%arb^^FT-M4e?P_<4Q9YhT~z^xqM_KOjgv=bl<C>dbwL&tu>GOg@g%|Bdkd-{C#bf@<Mk8N1Qhf7|z57QWqonGfIYzw|$ckN%s%mxN!HEc!ok8SlUJD~0c$6(;^Yr!M6L_g9}@&+~tq#QQJ(Rq#uSMgA8ng}>kkUx&W45AWaS@ICW{?_Sb)5kJp`FS+mQTf^t8@8drEoxTCz+c<7Mzi&~AC%K;-C+f7Eu;1x>l7w%q+_sQkSEDK1x0;L>-+y=X+VAu|jfL-t`gGpD0_C>>p2@j3A}Gc%D4H12#>7I$uL6)sKejgfs{oUG{8zsU(4%Mi|NE-|zhr&5pT&#NmmGW_+N3Wycr@Ci&pUV&+N95c?`3fhivsXSv`4VWXE7W)3~YZ^038l406ztt=HOvylRg2?2M+^JMSBD|A6$a=2%NhF`m}>bqD}g&gYQL~^ce>ipk07I61!PE#Nq+ySnwDYzhW^C`XJc;%ncm}CSBy<1!#}Mu?wJc9sDb_NndgB7_>=WcJKpelg@GQShPuh<KTzTCY|qKH`;FWk+_J(coxOrLbNBcc$mcm@FcXy!z+e93@!%01%1cClh7tz=HQ8FlfLcX322ipb?|t!NndwxA=;#i9bAMq=^G9%M!Oh&Bp$>fk3}YQC^(A+?Jxbo*=P@Bk&EMUaSU-k7K4#L7{?G>EOJ;3fDQp?;#?Lq2b_U(4TR=`2jJL#(81sw96t~GI|t{XP5K%*7n}!v742M{?^Wop!CByJ@JzI`(1)4O84ezTHt8$}=b)W~J`#VxqKw5y&~k8d7Izu+Yg|I_1TSH+oJDKs9pJ_+y08d@b^`x_#a0$ap{3xX;P;@Lz)euA5i}6o2pj-4z`Iyfv#5bqfrD7MScE`>!6D!<XeijnVmFKZ&^_QV<U~N5fg`{zpi$tXxQ=7cLtyGxE&4|KdvFUJ8v|_xzR2Pdi}TQr!LcmjShR&EfN31!F&3n4z%i&93ylN6hig6r-471Hy$yo8z<<ECorE3({}G>^fu01@Gr?XK2cZYRXIY#>&N&=^2KS>D$JOE(;&v>OSag7<fWr+jADciMga2fR`FkFE5lmxRjd3O21x`TSw$OH9y5|>g-$_3NcR(K!p~>LGEKaaE0zD3<acGILAdLn`qa6ut4*mfBejoZL@By6TAoK|ML-g+~^c*-5eKVo$!6x_)XgoL)eF%p(1s})toPwSPpGIF#LEi`aSZu)kCS3=n`L+q4Z^CE9w3cbFFrcYm>Q@@>A88LT&6n+lm}{h4!PH;cqZ&iIfN2~nac@W~z;w^M;aW-W0@HPE!!?nXfoV?A+;|td61*GNSPfkR_OMup`$`%OHgJtDXh-mqI3^q#38pzsd*9>GN5OPlXB<l!45pj_<dIGW2O}>O`U~(Q$O(c5fJ2ef4B8b;pM~H!(#OE``Q6ANjWX)@MQXQ#b_Y+vv0=~<Fzru04Y4jsdx59pm<VVXxI6M%LF2%*?spnu{7EZ~`ZY~+;2d-Zm}<4ac}Qo2X-`Nu#9Alq3;r!~VxTR+v~R69#Cj#&2&OqfbE68n8k~Zf$<RLFbLiV2q1(YU=iW5Ld?bwp(_T@I>n_JNUqqi`(cf4cL%hlmbGQSv9hlbm7DKE9(rsY6j?K6h(!=0n^tnB>H@H1G9-0RB;@pYQ4q#f}v<}-qTY}f(KGs6_g6*~OB=m7`FN{+HGznaVdtM7&3toXfnb1Tqtyy~3iH6#H_HrC^2h;>_#{D`BJpt~?7G)0>cSG+2r?cqIVj$E4r$g_C_H?j?wuM?Y_eQ%n>JtxQk;kGhG#lKXMJ|ghXg)a0@p%@G?+eaHJ0G<M;n+NQxu~B9?vHkV)FAH8q8p2@&^y7sSfsJYfDQonf_8;=cklqT2cVYCX=taRK5-_Cp)C49hk*OB$YC)UIt)D6@%dmJ-v>Ml?O~{uiDQSt%R&92;C^WLLk;48(tKn}n>A@N_!^TCrhkJr0vpJ2K~um#(ws!S)~H47Le4Eis0pSZu0wq~Uo+_6!4$+Tq2Gfkh}%Hxz;&qE27RSIe*+B%QxJa#jRsRh<2p!NgRii-N^8m`G|?rvH8cU52u=VeLpy<!!70$r;1saws2d5521kNJq2b_Aa1gW+I0zgJ4FLy(!=TN;Vc;leOK=o89@+*R4^D!bU=!DpgnRWR?iU4dC+JsT($21W{tMa^#7WRUgGu9E^?cc=?+<Yl^fNGNn5&*YHR`XII2ihgQGb7kgP?veX{f87KS!H1(pAq_(7uBCLi{u1c1#0YLQ}zC)At0^>(IvF0OSNhJA!{=pT(kHENT%4BIjR*(Dq;o;+v>X=W7oA7ED3h3i=N)1#ukoCio_5#-Xp&=Nr%nFa_}s&=@d946cJT7W@T^zp`lS657EfI2PIt+5y}SoC@s%P6c;_{sP<)+}=^Q1vCcS0^AfD0WQdM1w;q_r~gh?|KoAdpU(eWrXQ)kdUhV!%rxp>L>J@*)AKTW=ndcx5Bc<zV*DG6k0hx'

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
