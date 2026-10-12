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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8b8e14ddf5104c579a6dd100ff8c0bdb/part_008.stl', 'relative_path': '8b8e14ddf5104c579a6dd100ff8c0bdb/part_008.stl', 'source_sha256': '4fea8a9a7436375da671daf24120cc8b776535f2a016117db56664c2187de1d8', 'input_faces': 358, 'input_vertices': 214, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.05589953064918518, 0.1579292118549347, 0.11134546250104904], [0.0782357007265091, 0.4365940988063812, 0.19443124532699585]]}
GEOMETRY_BASE85 = 'c$}r02UJzpwuU!iC5f@1CfJS=1r-~jVr*Nn#)h$j$N>bwC<-VlYCKr6i>O#}E7-8ND6w!<ELadwj4jvmOpHBh^r_LSUe^47?}a;Z$GGD?GUoU{e%6_LuC?Y~d*=+jyV)0Y)bLY7OB+zbaZ&!SDn8X5wdml;F=0W$Q4PXJPq5R<h_8M=YC_L`J-i3mY0=t5m!ZK?L6I(Bn_OCjc)GZmTtY@gj)@Ei_a7BGG+6na0!Bmy=lfBi0i%QSe|L3n?BQl=Qpe3S+4O(>aZok<oU|=HUu=o#SKH>RHE70ZrCP_=Ta|CJg~0E#U3`mIC-KcoPK$5Ehl_8Nc7$KWO?+KD4d0fND*oa~@h#;O#n*$@h;OX_rci!cIb(~|^S95DC*Ze2zER0je67K*LjK46dUjmlJPDb|U(Xlw`eeiAzq+oaWBBI3s#AM#Fh%@6Vb{d3{>vHBk#7vizq#}cxo*`dGTv;7fd6F3b@{wUe;IFXT|Y^D<DlfRHasN0?b?c^QqTV1WxVBK2gzfyHG-c!R`T1nRX!#8`uHcvzNGe-@uufkAN_wm#7lnbiECKjmZ)>(-MNy-mVi1lV@`_y<@d3YXYM=6qkpm*`R|k)FY|rogZ$(AVIAIwM~lD4D*4Sz)8RXf4-?<@ndG<J&OIT%<!yh--+hJn);rfS#6NsERQjU&Ys@$7GhElF<^;LktL|908CT&iTxbzLZWY$8NoQO)#&52yOO-*$zke0-|8h)x!;~t%mU0mFWMwXpy4PI9bq{Qmb<o-tjh8$x=A)mTN1-1UZWiA>x)IiA<Pg;Jy7f{S-+VjjxwlMwOZ<~%Qs=rN;@dnPV0_1b<?v0YC*sI48Sk(heq1W%Yio~v+16o|)bUkE?APVS$Hjl#Uwm`*b3e)NH%4F`28~=Tez!Z4$5w9^)}hZ8@r{q`Gi!<D(R_2($oO^xk$<oz>tpHp41P~f_!V|x-QEmKk~*K-OMYuioYbkeC}~Lk8<k|;Y<Hi_e67hR#W&69BI}^7_yhAg+I*dSu6T2)PrvFZ`K{B!3;C8y9mLl!rNK|r#W!MoP*0T#>*acBcCrq--Edh4YlT|kTQ^OV>sbRgBENTMj4w77`~GIUtiSd2uj1>uBV@ecl!A5G<dH1nziNj5H=9xKnbzX#vDjBz*b|IDz7hW00Lf#!8jt$dzeJw)hU76%e2?o6tDhozqc6sH`APQ08rw;HJ>gHep0)Ha<UiX*d{c4@nXj?-nOtB0)E9Yv_D20<VsPDMqmXA}AnyMd6Z+x6c=11;d)nxC*vE|B81Hu<c^hS7-9m36f2lUOPi8+xojDIsPoMEJFXO`;TsQiQ4Kkl>^t0v12=v?eKH}?>&Sr|X@kKpN{lz!DlF<KE9$@^q2#i0~5cQRELOr>w;WyCF$+(-#(J!Ub;a|->FV|mr3;X4r1OJ?}<T17Bj`g(ViEl35=!*QE=bN5(Q+(^hpe)Hhu<pr%zUk7Z+2U`BK!5o;Y!t0_5q+P%0r?lV65l-bg^ahv9mDtwL&P_g9f0$*Vj$L`TY~s{<uh346o1Tj$YJEa8!Y>1iob{czcOf(_;vPTzi!21{0=kxmb2i`kHdPt3KZYCkLQk7v8nW-);3stoB3vre6HiCILDqwV*I{P^xN|qm|v$7o28DT?_^%q60K0LUP*l2{k-h2mQ@`6n_XFa+g@K;XH&pW$kW0FeyfU-M}JcU>-@n_e5<W1_IFW7>~FvX_`RZKU#vcv*xx@U<GL@e%f4G~$6@@`sTl7!5BKTUebJxEb1~lDPkh5?E6&x2^D!^oH&1@wRTJmxqC*%zt*5NN_T^@*bGuB`-!1|B_`hA@m$!*;EI*IuuiIYS@AdzL@As>$v&Ca7&coc=TjcXgPUTAe5rJ6$mhR#k;iGV$`h{X%)8~t?kLinb99;+3P1*=Qr3F48a!=-^M;t*O_cT1GDy~64Y<vPgzEn=Z`^b9NE>-*<*)rZ(TpjB(qb>Z1nU|&B!M~ut?)iwX$KX9ooBjaLwMKs8o6pon|8E$M`kg0>Z>{Bme)b8#zHE<2{@=G=l01pqkpD?C{HBkwZq}QqGx7|4_j$N~tCh#R8-Ko4u6tri9_GIjc^oQ=uV<h?tsl?l{Y~Hpt(CsAxHdzbJG{iVIbV={F}{6-K9BXm_!?&PXVMwmkM5!HkJ(+2&wpu$I-_F5H`UC=`{b?S=!dcgk-zDByss9ii+bF0#J4_wg!9P#^FqGaXR+Lm+TBSwHv;Up$={zR;Q9BiHqPfJQQ{kIYUH5bry<XQ#BI25&*Qn^Tmk1m;C}JVcVEkRV`Vn_DkEEb(=bE!U3(dgbzbxe*LB~4IvtMSx~9L2Z+m$g^K}lF{JLY6?ULUP@8SBYq3Em6+~6<DmUT8S7<jUvZ%aCae)z--`xrC~;}`cvUv2M<I(sFGuYWfY@69Vi(f?`d#W#X&c+a1C8|(jOpZM0nN2DJtt)FB3+S?d^B^BpDv6ncvzZtYc{%&o2R{TDX(&hKt8{xa=;XQtk*Rg`WvHM5qPiy+Lj6(j%BeIX?UMBQU-YM~|7bZwwS>M`@7xeY44|pDBpdYMd?!!O0Q0h0Qjm7w)rFP2S|7a<FXw@HLUe#)fZ*KNTu4~G@U=`o9rTF^3a&mqe+T0`Zxq80hn+~2v|9AGneKB$*^6zPn`{@2V^iPu%<jH!EzS^`H{=$pm8@0<y9&5A%>iH=L`5&~x`E&3D_9gBX#-|*<jQu)^`!4x4#+N)T{a`7+0`EIT9Cpb#*DJC<wwkerWu7<6h;K~)8{U&IwwCJ}-&GLbG$I&%ey@zo*VM*MeEs$CbI@z3zoiHK&OK${wJ&PQy4mjZ7T-L+zs$=rIbHJDdir7fK6~WZUPtoSB8Oo7@i$VB^`#5)C;FrQ>&fV=yDO0YKq&I`>w@RnDW{`S?}%{JpFL9g-?)$@^R-@$z<ghY;JLhE*|CDYZNPK9Cr{V{zszdn_o|EY>iab~x3vu9nOhtC{^u$5$^J~#`Dm%sqif#j1%2D&>o|vhbHq7QEf0Bam}Q+!FYJ#N@{K&4&kd)bujX7uJ^n>6qJQUMeJ))`{$IM|{iNa)smJ{EA;#Cum3`M!{AK;MQ*SW7X(#N<-ekG1$^AX*AM%^jZ*3kYd9;Sbcgy(1H&Val@oe!;t4hJ|J`nxM`P%B07T=WBO!Diieusa}S$yMd9{SvQGS0W1?ilYh0`ECXW=WmKhHo(5sg3lrzBWecG?xs4zcx*L<Le--&zLay+e7jG=`uj-G?ot+UmtZ7>rl6s_?EON_@y$%H>MuPIs~jhJ-_}T^R->CA$6LjuE%_5eTO>l{4C?O4_CxDJ7mlKs1F>2{|{^Z4C4<J!}F-`OZ4rQ7Z`7^q2CsaMZf+29=_)byypa?|1HTy_ej3|uDGxF^^^59`j!*lwpWunwU6^!_LcaiF}3hK>hdl6aFGXmYiY@2TiqV@r1n6bLyypJjmk@Z8uqd9FF3$oSW3oQtF9E^eE$II8Ttt4>KFEVCBIP)>oCL><Ik5A-?qRGb%q^>A5%?y^M^NhjwF^xo~6x^XT?>?V{xd6`=xq!<oP@1tKaK}=g16y@r~{|sK;Y1)@}W0jDPu5d=sy$4~WM2*Ke^tKJ!t}>!SOlo`p~0zry<K?MjGmB>aYXJ^b@nTkk^OW@aQGs@0`z{z~UZDa}y}2`KPYrZQz4sDJ%cW|+r+^;Kq*rk?-buQH40*I=I?#i(}VV&tM!jjVo(kd>Aq7bTaZenM92Kvr6UT!Pn7JUu^R@*|15kgRk&If<OkP@F~0BxjNHs29mf&yn-UISj=a)PrQDE65q-tqjGxsVm7!H<Ndh4>J@Wq3$9pO(h>8?_(%VrW$0Wi^<94M26z2)QM!JL&#If!x)OYQoYGt$t@X*TT_RSTa&+KC>}+fNFGI=LtRW>%sI?qC|<-+oIp(_r*e%F7>eT=if2(blQ(k@W-%0h&rockt{^KtNVbrdF%%!7o+B&0NIpb9#!$SInn_l=oxGF0fT4I2bs>2YIfNQRu9Y8d`O%Epi`<MHNDU!}@Uwx`>Eu9iSbls*olTuiR+>bfP2R##e1e)zK0(f=W|5WVk+aE{8H#hMIpkdO8EOVu=~nU?@&Sh8AE>*@N)MBNAX^!Vk5Z42mF^=SC2wOW-at(zD@`PCATMVqj-yT`D;-9TBZo2+ccOMBD{V>cL~hJb>`84+_9XY9eoO8_4xo-AE1g3QAdg`v9!Fh79!DNeO&}|cCyytOWhf4(&LS)Qo*Ygd&QKgdwUCuABS(;DFchz*9wI9}MqW)`#ZWw#x|6JQ0eLPtlA*XibrM-=2)RGGEkkhwYA>=<H*y1VO@`tc)LLYv)yd`ZqhfxPVJNP^Q0zplOs>q&IZ>;Voyb+Gwa8V;uGD5^S8_du;`Y=)a(i+|Y8bgA*-QJ^`QpV;+=8Jvh@p5Ibv9Y)7V<Q53PbU6>It&aZ1QpP1%~2F)XU^c<nz>AveGl;^W>8Z#e1m-$a~2<s6UXETFE=eX$-}Cs7J|4w~_adH!>8jqi!H8T~1y{p3hJ`nHon{8cLo__Gc(=N9{yb+L+vq+=!vLDb<s#v<JB<S*He&b#iZp;(^pL<bh;g>Nv8}@nm1JA4BnA>R9q%vJW+!taLcphdh9xcqlc3taJu>C^?#;cqVl<S?MbBOmZwkaTIkfS!pCWiady+xD~ZOS!r8xD{_5?VrOatveKGlXL1#44YJb8<SOJ!)QV)K<;a!D<r#`U*VI4NfR?6~BbO$BMlD1Bj9ivlfn1jCNOdARlE0)@C4WJ!My*O#>Pl8xk6evhm)f4Jv?E!m7r8FE4z&fj4!L%Id`0!3wje7FB72bgG89jsP9rN#Ax|JLVJO~DJx*47fxMr5ilO){^%7a>dGcBEX@=q-sVB)llGjuBl9lctuP3i%DBeU(BX1(Fq3$6o-AG<TUdm8BkGhVmbUt|=c?v`ENa|#=Qh)MDavy3tav$>748;wpjmS!yk{gnnFcdeZ>g49+Hq_qaHslV}fn=q=<PPM{48>ije&jCXZq&hKr9R|t<n9c`J*fl8J<0v3L&-{`$^FQ|48^0VGs#M0$)m|57>do*D6-N)WHb32hGKVWE3(r1WOuR)L$QhKO!n?(SH#i&KmC)kfBjhG%Z!5m!0g{YS@`Rlf}hOFAN0>JbG*A1Q{SCvMe_es4~^dH6wv+wz=K_V'

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
