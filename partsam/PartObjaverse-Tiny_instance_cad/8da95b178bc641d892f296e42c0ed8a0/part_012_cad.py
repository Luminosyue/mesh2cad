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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8da95b178bc641d892f296e42c0ed8a0/part_012.stl', 'relative_path': '8da95b178bc641d892f296e42c0ed8a0/part_012.stl', 'source_sha256': '79df6ccbfd99566d06a698c5a48a0549b4df199d3c3489093fa77cdf1e90e480', 'input_faces': 288, 'input_vertices': 220, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.3136984705924988, -0.2624208331108093, -0.24497848749160767], [0.4634816348552704, -0.10036034882068634, 0.2452368438243866]]}
GEOMETRY_BASE85 = 'c$}r0dvF!i9mh8bR8awWYkgfRuV7SON<fe$A_XE4M5`8o#3Vq7NJw}Hg02w|L9GG;0l~{7U?4`Q4_-<(A;g4`1g$(o9qtUaoz|I7TmNY5jM_bWK4&>+Z#vUyGxMA8$B!px&+d8Ly%{pnlUjAQ<WF~N!vUuv(#5hwU1N2&7UmYt&&$p&y5p&W#R=B6z860#*G+hMe8yu5)<Wx<-Z{BN*@eA_MtTpMk=i>Y(tF0-!uf?+Pfed&n3F5~=&UD;ay?%(E2|*a`|myj2J}mb3`|amEQ|b)KUaA}aCdb2e1w;F$CV#fiZNBq@l*MT@<XZ)=swl~-(&Aa-A9#Qzkj3OZ*{)!t%?8q$oG4S-Ac{JCg9s#IIMeD`4f+Rp!=xu)|7JHJIbfD+Nt|Y<zM@-SogN_?yh2eoDt=Z{ItWr-c0+9KmO7!M}>DL+EtaBkL{A)IyCK&?p@`(e*U5Eqsl*#Q>J@I`KIqnb)Ttxq#(aVZzbpJ<BTZZ>c`R+{f?{4{QF5>Ew5V=JL%t7yVQnC&D)!#w^rH>{(TO=WVE;LT;AwE&+N8m<@zb8)7Ovk5#?Dw%3I2_ew2@Oz_Wg=wq1Pho=!WWuOH>3%CmmrJnKjKOyyZWah~;~ysbRzNBM~ItRLkq<yk+<$C~kJiRJ$FGJBlWpR>F6_9lPaN5@Kk<oPCjUX+g<mR`+^^6t|kKJk5fv%R|ruja8h*Y{4p<U0L%#(AD+oacEepQ$|0GtToomA94WdB%C3XPoDGIw^DHb4WdKSYL0-TgtQEly?W?S#Qca%Cp{-x0SEhbin`bv-8gy>wjFCKM(GAtK@aZB{k{$LV4%MqyF=E@R3UgW&7EsjrzPRANlI~I^DY`Pn+vxL8oTl&-klspEIb@7!N-B&1%0N2XDXB|D4~?mG7U@`w4uXw)IB;MFY?2_v>VhZuZCDXQ=PpFPF&s;yes{bsolf&O_xL<v9=IJm+DY=RAz_oQKNW%5xsZdCtSwf<?Z!M)x|U->>q~#FBbBPU+o0Y&M>cHGhiXgZcV4+kc)`nk)NxXMKa-Uir*&>BH@<Eq&$l54Cqo`WpQ^jqT3+*PYi?tMBVL&%TcH>}%yC%CoQIJo{RCOL_KnoM&Ihd9|<cu>w5jq&@Nm**-VnwBIl1q4JqI(yQ}Lc{`fXtnWwVqjOI+>H90_f5mN0`aTN!S+Ste*e}YDt1#9{;Bzh-^BeS^ebJa-<(+RX*6Z^d^m9r2aC`g5YmIdn_<iYhEsfJTzE1Ab(0w^)|6beDb8y!d_}&RUH#_gx3IDq7&F62;!mH1hf8@&cr7Pq-ay~0>DbM*F=Q*F1cX#1ApEJ`JoNs9#DIeZP%7^!n^5K0H-M#sIOZ!^+@V>TJZk7Ew4RU=R|HdD$^3Jr?($_Ak*L|k)`zF`u-u<Yuxut&G+uoAiE^RRS$6Et>RU7`h>C)F#)wSr|D^BP>dS;Sb|9^huq|sjaRYk{*@f?^ZKX?9kU8B(+??m^zhTr<J+%H$oFvg#$d|s|O{&nsAc22(mMn86!B<V+%nAcUGQz=_o_Me_Gu4}9Ljkd0C$vac-Fs^IeaHhq6VtW(her#jjm#h42^S;~-<K^da__^V&?dEf{iss1u8=99`AwE1W4^5Z*H#F~o56ye*#)#ZsBh7W?;+^oiTJw|K?=|N7j4Uko*Rl19xy~)+%guFe_3vAw_v3UsCVlAhSNZVgZ}j@aFO2zB=kUK;`9AJFNBPiuPPEtkz7M}gDIb21iXF_A{e<4fB72wlKJL8^AAYZkmXyo(q4!4R<K7z&y2kwm?|YwqE5{T1zMy>g`-1Y}?+bwseP6I{?{LAmU-e!(YVrkRJdD$MtlaQwJj#c^S4QUD_m$sY==@YZ6K~J_Q?1@Ue69xVL+7gUv8mF#c}we!>xRzNp#RXhs(iFB?Jt#?;}4yOK|i7MF!1}Ow^!fPXxvxm+zb3#>Fw{g812L7VbDHw9tQ10=UXuT(76=!6FQfI=NURTf__5hhVtR_LHY3c5ctsf5Ls9t$J48uoENno@R8aYxy}c^Sf_id-IsDd*8aZU@Jp8Z=Y#cJ^GV&i5B(sY&s8@!=w7W``(k&)J72ez?N41}`crB3djHP07mR+Kf;9QQ^tZK!cemUt_vxLxOuwe1Y~Q0)j=!$G+((OlIH`MQYPLLo_cj>bT{A|Gr)#zJcX#>PZ?F1)xw6W?Uh{6>+ew$?=f{0lRr~E~_W0iFTVAiX5B%IOWc%f<{PxkqZyWtv$6oQ<$12JU?<CAKyxqS}_A~aYsu3B+UsqS%JmfD{J29o+r>)i5nvtdbY1RK9mK9{ne_G8O^xyqyH8u7B{nP5*-WaBM)q@-di|h<1c_sb^djlo7A0>DU*%20P`ty59@YUp4_-eQl`D?fnd@DH*z7@WUd<?z|{slP(9>aJ9Cwg_IS3jo&-$4l;O<oI&Hh1!SiEtb8mv9@n1NkW20q#x~z}?|N<RkDPI6{twM>C!X%cYf9*HMD|Qi9XSYhaN#!fEhie)l%(@{i!w<b7~!xGnh*+!nrxd<wn^9zafpCv#oF310ootLrJjDU{$*WII^2xt-rjfUh9$hp&L!lfQ!7!?%!g;alK=<iqel_-1kxJc{uMUgp&juim2s@23Pm?bS2nbL0~EIrw>U8T>rFf_wp90k0-k!mBkFxkmGXUnO6IUxn9_8{oC@da?vw4{szl!yDms<R*9>{5tst{5t#!`5X8Z_$6``{1W^!`6B!>yqqkCm%|RZ6n5Ze$;I%q@H5n6=I3cx&7<JoQi4Aqm%<;whsa{MnDHH=1b<8kK1QyBS8@NxD8VizxSD(eu7+#KO>hldOKyg1;S*#Dd;&gBZh()&Rpe`M6<kTKfh*yo<VslN3-D3+FeUgyav3c0Jvhs&ZC>S2f{Vx<a1p$S61;$X3l=#GUI5Ra1V2dH@PqIKau_@T&R{$lj4=xyK@NjwdiADP^C`g#$*u50xRBfe7sA<;;3p`-nUvrtxfPDWdnm!%$v5FQ8Q*qFa31*poCn`a2_8(2ghi&qgW=(fZ8+l{j(>uC5jl}ehtuh6A|-e{`2ai~o<z=sC&9Vod^pvsUS4&h1b3kXcO`qnB8S3V;hvUU13j77p7>#uU@_NO<aBZ<Jd}Q?Q-Y_Gz2K?v<76uQI6RF?wJy(lD$jK|JecgJ%|$onP2>=59)~cu?|4;eU0x@Gqx2u;no;~T@@;KAZ!<=bW!jj_wEHUKzD4eYv&e1aPFU<yv2V-CZSXeQlv9G=CClJ4#_=vCxPmN&OS$I?O7L!S4=i#!yq)K?n-ZK)4uSLGK4dpoWEWUuSGW(HObNb+><OzicMmxWz6YL7z6H;Qcai0AInQDjC3qhtcrRH2S8$(uDZx*Y`EWk>@FXR84w(!mGuAoeY<M=~m_zP^_i;VJ&0d`j)u&#4?$z(SYN7-;lApn!(YBEie2P2`pXM5ZKk=&0s{@qa_bI^#$$D7iN%$aqgcAG_*#MvS>YP_!dUb*Pf;<PGA<vTM;EeQy#Lh|o>7V9Y{&B>Mu<;Ld!oO*L?bLsBn%7tGB{U<wwRqR|zSt!CU!+RJH!JJkZ^?4D'

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
