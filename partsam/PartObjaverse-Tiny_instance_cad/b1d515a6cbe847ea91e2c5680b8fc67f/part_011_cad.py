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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1d515a6cbe847ea91e2c5680b8fc67f/part_011.stl', 'relative_path': 'b1d515a6cbe847ea91e2c5680b8fc67f/part_011.stl', 'source_sha256': 'a2c364b3ad66271893b45985b60bf3bd621a17afb7f144891b485f383991c0fb', 'input_faces': 158, 'input_vertices': 158, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[1.414669394493103, 1.960235834121704, -0.43474942445755005], [2.415203332901001, 5.459913730621338, 1.0246491432189941]]}
GEOMETRY_BASE85 = 'c$~dhX;@X|7T!$GDTshL?j%7IO*6~H^hk!Yf&+n}9%N8ZLE&hkB3rKmT7m-zV&ows3=6}|p%At?goP8DhM;bZobu5yExl#j?|awccIvtJ&;4=F^Q>pB_3n4CZ++`qd!2nw;3x;jHVS>7R=h9VTNv0%QKYm`+9(U65-c$hQHj0c<|f%G&cNlTL2nv6X-r_Kow7h#>=PN47?I#JK=m0I-QUMo^@)y8uq1@XO^Z*6jFNaj`0T_efhW!kpBp9oZhiXo_f`9L_f?bC|MAmIq+nk1-Y<h?E<a?tn1s^(PnMTS|K7M?C9c<cw3fKF*R>M(!4<$w9Tqo{xE8YQ4*WCbN4UP-4so>GH;%&Z7Z2RLd@uOQ@0mA&mm~w%N{&&SUm|}(oDt;|r`1ZtQ9g1yFY_^FpCkPKUT5&VC*(_9f3*s@$?s5O@IT1A4qjyA$H4s~6p5S8dL2g|g@M40wyS|F9ou4GO8REtR=+em#E;3miu?P1PJAbK@bv@U6^L{CAaKn&4D~VR&#Qz#qXM`dS_r;oMC_7z8ci<%SAJSd_`^F^#9vFe5j(>bc~*7%68Pndgun4L@-d9nr?775uN0>`5V(FVAAJ4Qw*Le^EU+o?EhV?X-`NYe?w$v}H8u7K;#>THtCjg}z<+rS)#1iK;?J~F9p0R4ML&EJOz}^~fv@c?1K+fCGR27wMgGdR`8&XGA5OUIOT^FqsucX7XyB$Nw;ZspSNm$zE#3m$d}0i(yYJ#I?0@n?;Kq@Sh@)g}`B=uc4q8fl`@(vx(|8)rMc<!F{CPp>AM=#-ZxKIq9j*KLGM)R{ic<8C>qg3R<{K1$K}wOt)p=PI|EDg5-`#|DP5${*A5#wUG{sczM%>g-Db9Wm>cfi@sn4_b(7M|9)IW}G&Y+IH_EMhtAEKZ2HxC^}-Rw`%y4ikIhgO}h;r;>Fi9h}t#n0LRT<=;>>spRdJqO=4u-_Et-*DfheZY-j<AE#Bw+3!aTIwiqHOIFKaXNYeSM{FYE1tK?flulLT*=Cz=P@(tBJ%9+MR>0i+E?co9esYOCvZI?7jd-aHK@ON<OIs+wIb}xys5H8^39ec!skDvdU`%QCUGq=6}Yywh@Rj2zEro0EaIzE=-ijY9Rlw`A#n4q9$43!?1ui-#uZVX%NAq5THL#MPOWpwiQj24J$L&Tod$ovIf`EsZI69jX>=I*MECfe=41roC?mtDo~>U5t`E6D=e1(zN%Ym&0N|!m1+?GmPM-ts9tGSQ)faiHFT8>|qnAblH?+&tZ%Hk_1V3*E#dit=Zn~dHeg1J0aCMT=2zcneTI{DPjrhq`;G4e-BECmDaPy6)Y2B0p>XXVXv~Fxq>{oko@Eh#6U>D^-xtRKMZ)faFsoO*GTfR?oqqqR^wGJgzAG<TuS53b#XkQ0u-Bks|uU8J?`Q2Vl`FHC^bLnu0FA%5o35v6B4xP(q+29-XXDA=HHT3+ZwLS)ZL>=Kj#?qYmus8b98r|Xv;@``qIhhcM{I#ncfh)KDoWTF15$bR5+y}UMa~1X5?Gs-i{|D13&eao`t6JgETB`d-;HIprsGGISsRsAge*oMtexviM^{&9WZ9gJ@?{?suG9IGN=F^9P>tW0AJz{!l>ILK%^fhoT&Z`ynyE42GedBtC@N{|}waW+b{Hn7J+Sgz=s(;HxRR7(z6hC<peUI!6sG$1Sb3RAtT<(oPK6;SnABcZ40DYyU>^%d1L4V-Z>SUaYR(kUU=HbJ!z?Jg1sQyQWe~maJf`FS{yfCk{=T1}Ix=bLx?`nFEGPYA6zB7x~{qP3%Wx7{cjrf*0;HIhVngJhpmcEzEEW|I(Lp_!I?uW6@)Xju1|CRdcZu{fNf1DM#I({6@&pqo;A%0CE@oV=}pIc04(dUnf2@g&}d~LMl1kN?_JmI&VAb<T*9o6~4Rl>`Ps6K8BF=v#R8?@hfwKP|EIpX_HUH>C+V|qI`iJNzH#Jak>b3OIv1=L?}68Am)d{^L_r5X6j`Sr+0e>ecRvE(f3Z`fS{Zv8oc;`m;pd9v<UCHk-~jN&Y9PknX!SSHqWiUMxkol9|^O2qqyDR&m()jrLU&s=ZJVRh#U!Y?$TJdcMWzP>wy*6qKA_|sEqZWp`@+!S1h_}0o;;=i|@@;Ts0{NA_dePH${G~e&1(HzLRc@F%ur4*;P13iyZYJNZ+23(;yMN1GzQ4Pe=UFwKmSBm~og171D%cCvnIS+Fuewz{a9?@&t0ax?Z1J}G};Qh+_l^=c2IoYFs^p_(}<N3WC0^B%QNb!gF$i;bl6i;)iyb;A;rff$Z2k86KRJV}ux6kK;@3Mm8H2#A2RkIc6ZZ)j}ZXWi8o}=awz|99Tfm<ieML!tU<=>({&z95srR)3j99_D37V!^!L+kns1Ye!t2)?<jg4V5h9`i?W2&_V%jIE^nFaL~vX<LemC9V$nj_Tt*+KtX78}&5BS5rRLt@J+p%`Nng+RvbTb~y07dW1Qw>i4(~kyHntJ9zK1raz!MpL3)5Ezcpow#<><59*o_o@}9h_|yfsdZ`+HqR(%Kxoy~a5P!^7n!_zx;T(<MrxJhjFW_5!_alzA(JY!5KcA=g#UYpvT9;Jd%C|-I+_ew>1h|q<{K)r#Yd#~fFT-aCecz-f5Wj6R>`NKCht>_*MCX#1gMF!kO6a{|dlB_dL>%6Wlv&3p&L2G}j{Bnm<mq>r@_Et`bu+D6u^;tZd!61h>Mh{w>rZ3OE2kb49ur3IZ$&*nL!QGL+r!^nNax<HDf&=<{TblqiJfU~Xxrj2C;LwZZaQ8>{3AN%yzwL%xSDGw{+x4|x28@9DULpm=1d=#JoL$@Wx%zKL#eMaAEQ3Tl}m(&9HBax=iv99cBdA&p++E%7U2Ii>J~hn-giAii2rWI=Ys?P@@sthz7gYZHdYiVO~tSA=y02#;u4gf2K}FZipRY0|N1FDTjVfTNF0l_6NSuYe*tUhOKuWli&!V|wUt6PDstSAUT<UPu%E;JRv}x2<g%U1{yRc4SljyPLe>h&mgm4C?JOZ{WGe~Tz*_pLLe??1iM908guEr>Z5um{uca_|HR}|{lWndy`0~CO=Ek#*VNMilTVLKYRLCSDA#6)MT!^2Lv3$*swY;vf9?te~v=(6<nA^dIE3bL7t+MUGwg+?FSbOmGfoyxQ?a#J9bKTe;#MfuB@6Yy3wr4VD5Zg2O`YQHUvA@Q~mz?FSSMjwCY^Sl_z-P6b{kLtd%k$4vs0T9Hm*=0#{$|$F|A#{TvzmDgXDsaqUb`W`2)?HuV-5T6$Jb=toZ0teJ&^0~Y;#@uZG{A|-Ee*ZjLW{6r%)e+u>Csgc+R(>x7PArGI+lk?5FeI(*Nc!6%xqW)*mmV6WdR*?!>qQV|J_^_?p7D9c%fKqpOjSt~S2H{u@HfLVQ`IJ%n+MeKXrDSZA=E!G0Fs+tp?rUyc*PbsEm{I@eS_L-JXRVO#1+EHPZmNvvfIIh*7RTgh7ba+WPrXr499HR)S;9baB6fNhyukn-m&T*Q7X=NikocV$~%>n6lo$N<*TZ!TnlkTF6cSxaAj-@L@y*6%Ll1tGnJJj=Qr+f9V{2=QY53frzi?1eb7mcFBqVM6){d7gDgw%vuue~a6*mVQeiE{gn8lYcXlE%h@(`U>eHqz8+%<yYbqA)|!6##;K}LY@=Snd7>%E#tq;cEfe)_Y^WtNPi(F*3uur`N{v2TeEJ+S8`rt{)_DQ=KCh{y%X7=D&$omlZA|Ak@j>UON4|9iDoVR1R=pfrU`kIZK>x7Su7+>$Y{1lGe2;YoqZdJ|Mr*tpC3&=Xn*+w|L=GH_4UH`&NLD0-!B`1qnu=aio>?YP$`y^UHKRE7BQ3'

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
