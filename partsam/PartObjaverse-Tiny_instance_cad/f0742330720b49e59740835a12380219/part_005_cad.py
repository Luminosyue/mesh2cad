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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f0742330720b49e59740835a12380219/part_005.stl', 'relative_path': 'f0742330720b49e59740835a12380219/part_005.stl', 'source_sha256': '427c12ca02d52036b2eecfec3f554181612e305682312a6b505c2f84764ae2f0', 'input_faces': 408, 'input_vertices': 290, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1941036432981491, -0.21113021671772003, -0.1383640170097351], [0.1924542784690857, 0.0822395384311676, 0.4956601858139038]]}
GEOMETRY_BASE85 = 'c$}r033N@@8pn4~GbLhd64y|PAqZ+}D@Utn(WZU0HN{PnC?ST#R2~l6(&4pgXkxxW67v+17;_NBtW8zKbV&tOp-Km;eP{3e-{<bLbKhETy_dDV_5a<!oo|2p+vn`CBfMAXGJb@AH6TqwA7^cOh7cN+i65B|6F+WvR7^t4QDZ*vA=Q{qzl6?zy<ea3{yt;^nGzHolModj)Y%dA!qAREEgV5ZN5_wgj~q2*bbNFS^}9!oOo%c4gkh0mV$9FMZ927X;b_~mg=4DYfBdRwmf(!a&&@VfyU-zn>F^oH!X)4LZp?P7q|P*(?@mnIMpduhELZkj@ZBSJoREFpuO0UX>$%>1EyQUXuLX}^&*oRg6Zj5gywPCOI;u{k9w&T5smGP}IF;qg8f{ybYjIqP>}$Sfd7c*OtPid?eUHk%2H)s(>bUH?D--5xuXeYMH{csx7u&`gYl=6s@wc}h@#eb<{Bv#fz}JuGoUqjcpSYTzlzmr+OKINf(c!E0keDf~Kf1DBBbxgztXB_T<+VS;SNkJ;wLijF`(yb^e^g)e$Eru^k5!M-AK|P05x&|V;j8_z>QVY*M6Trd!^<9L<CE`i%$9uZr!S7Nd}XR+%RUi)yVS9A9^%vQAk&%0ZQ~6Bf2BRY<u{C)YOAMt`z%(EIxl?E%s#J{-Yt`jM}B9$Wbfw&{1WE|{1WE|{1WE|{1WGe;#=p2s7F0F;FmZzM4jrn0l&n#A?j4m4dE;221yA%%<8Prb_?_K#@Kvk<rVxnyf@*f>}&9~CBu))J{cIt_jUEkT-kRG;J#k;;tAPzwDf27YXLQF<BbsRyW@`A#ygYS@#lG9;St$)yWqEaVjHjf^;zjHzXo5;Z=AWboUOxsWox!ve;QftZCwPuQ&|_ud1D!yKQ%91&SM<pK53V~S@zu{7A#_V*WPCre6`PxIfY5gFE=^ER_AQ)lZ4MU*yfEWo8)bOwQ{e`V}7lLJLK_tS?=p^_gg3X<if)bnZM|F`}p(l-}qv!ZT#|x7;pJW68B5wkBu8m>(iBWkumU<b&<SuoxT4`pLO`U(r5k7=~>j*u)o^U%>7LF^k2pPJov(1+1KmuW6z0RHF3Y}6X9R`G|T2siQs*^m0=t2n#_Ge$?t$qLi*V9Xo<Vi*}9Z@o$yJaGVjm|+nL{#=hvsL$n>@@;j8NszPc{USJowbwSH?}rGDY7^;`Ls`rS2q^Yf@F&iNT<^TQ<Hwf;I^$LJa7WM7A`b!k>$8{avQJs;ZJW9{SN8@fHe@b&ebY<b-CHnQhWQ|A@FGOr`4@&-A-YtD)^Z~G#Abzg+9?u+Fs`yzaGU#xk9x@?m7#hMqs*cag&Ip;UY`=a%IHG$==UTPBizKodf!(_iI_qFbQ&)fXDf4t~*yp#K4JaK%zdY_m62w&}w@YViUzS1AztNpRYr+qR*uG5+~h5Krq#If_eFfZdt6Yi_y^~WRD%KaC<0blgr%9B)Xovr^>dnSZ=>%Z{T{tI92zwnj*>qAzgg?Z_}@JpN<@JpN<!dK4?_$AH_F|YD`TJtK;r|?TWpFX{}@Xz*hL-^{sA$;}Ru*NIrhBaO}H&kDo8^Tx54Qsq|ZU|pJHyp7mGQI7K@YQ`0zPc}#uk4HP)qSz%RnBwatLM3uUpdbm^D_5)tsj1g`r((TU-)YM@YSEQ!Y{EdQIEPV_$AgQ=2h0E1z%;p(c@=>eIC#-hyD4vLOwp|(0De_v9`?DTVCh&bU4M=b^GaMvhT{y;{L)6)<^e8MLbVZBmNw|l2;)6uKW3HJPG`2x@~-uuI&AGbvnoDvi#aNS^duBy?kFU-QaoBSL~tVTw5FE$i8FXWB%`&3Hi41B0pJM$o^es`FCoMW8*rEIV+FXZkFQj_w>#zzpL;z-}hb@Ss#tTxqQ8y@9;c%e;;D?#2UPQ_|BB(tPif2`krB*=M{5*%3o}}F>E)hNBAV~*#oRU4|ehVx9;+KB8%C0J#Xk)**CWR#pcta_waee_<>K@XJb%$w#_dS%KzT^pu8UD%}=ejO!nP5<@r83o8-v8qvtBNkItGQHlI{Z<bCd2ZMy91sZ}zV2Bot6&aOXmf2H3()}IIOo{@dBy)B#98Ii@-q569G`fS;E?B&m)tJ$!#wmemNJ$lyNrM7wh_T}e&{3DxB=J(>~ai4Hookq{{tbVe3JL{V(=|11bJ`eeOwDw|w?32%nnD6?Y*CTvm;z3rYK`z_IYspo3J>k4>R-PYv@_J$e*}RT>zi@xsZT|c?)?AT&ZDTj~{J0+tIwSjfc59vo@3oa@_RGw7ZaT!z<sJ`to?Ey1x<a;Gk$v~N-`V@+Iv>lQ!{xv7b=|wm#*?|brpdl*S`EHm*Rxn2?bqLU{zb+7x%J((RQAcTs_eWqLQnDcRQNaWo)+`>$msJ2-*=36Ogq7!clg@uC#g&mFM9P!bTQAL@`&f@!JlV6buh~>e3FvH=e=_$Q}(r6{Cse{6=5I0kN4SKe96f6;){9pKOgh{^ebZfNE-8dB;jjW*VwtIb-!ZB<H`HixsN=g?-O2st%od+R;7qNSNi(Dc>dHver|M#W_>25$pNN=F0nigyuaE2AMVfX$kyfFb&~(QjCyd8{dv?e{_oKSH<z>T8}ldgT>)qLziazlV)HtWJYl}G`bqBB9KfCvV`h0iPex;QZ|06@pT#~GRNy~<$~NTpX{R;5zoC`*xzcJc`#I+x*^-~bKL#IW>r?K3gs<NJ2w%Pb5x#o=BYgG#NBHXfkMPy|AFCea{zv%g{g1US<^IR2U%CIW=2h;0tooJvA8WnJ{g34<_diyC<^IR2U%CIW=2h;0tiCDtKh}8V{>PeEx&N{HpxpmheN*m#taT~(Kh}8V{>K`x-2Yg<a{pub%KeY!EB8N^uiXDw^(gm0map9Z=<i@Zm3wdDtM}f*SMR+oU%B@dzIyLn!pFV0RgZG-ZRJ<)y{$Usd+%`DZ~L6v#@BS!FjJaQf%uW3k<zdFs7b$sdjD15@OJ;zulm}x?)d-ys_z%GhF{INhoF1_`aAdlcq{Zb@K$gE^dYzad=UBoO!Y4Kj2Y=>Y&Rnpx(k{P-UU8l#$o6VXgYWY_!#sI_!#&cg7P;A$~U3g!8gH2rJ9Z+a@li3$XVzKXfF5!cqeohcqe!t^ayw#_^PzFs|d<h%s2!+1w9Nt1-=H|0lo&_4Lt_l4K9M70~djBBPi!XzX9iizeP~Kh@gBQdJ}vfybXF3ybXK<YJhKmFH8NsjG+9T8JD2v5tQ#j&w}rQ4?<6X4}uGzJBjD{q`Vcnk9eME$_JoViRbyJd=Gksc-|MvKS_J`6N2)7GqRyM&_m!H@JZ+?@Ja9w&}-lyz?sn9;7ss!Xc722_($k%@Q>g-2+GCKd~h*15Be=Q4}2U!ISYCboCW?FLHPpoKKKH7FLWDtFZdRMav}5vxDdPtLHRWFGWaz3dj#bS=yzc8Y-K>*;AUpDFr&T?56TTpb@*^?j?dJmT+igXW;{!HP;P8$6T<Zwe5O9-Ch(d<1Hm)`kv|agHAfwEK7VKc*dJUE5#ZyQqb~B+g&&9rK;8f!&zkC?c7JFP@#GJ}{6XkTebm$f^->Kcp8A8a?k3>I=t*PbZ45sM5sbXS$VGXo8B@%d2K}eRAL8>r!5=|C15^E6;(y^Y)i1y_*KEu)75p*Ae2j4)!>2sPjCeDaAt<jfV>xszG#;E}Mxq%b5R_xh7ztejO$3jGj)pD;j|Pv0E(b5ee2bw=z>C32h$Ye-iO7)%e<@-K@-C6ql!Uq$L*u0UahN|2eOZQ@;!!WvQBwV*u)dMtSmcaFj#&6{h*8Kp3b`l`F(cB9_o2hV?}H~nCxa(}=RiLN&jBxhehpp#PJyO@Q^1=Ll((3%8JY@B1E+!)Lcazt1b+hk6#NPJ1L$P%2jF4Q;oxClCo~eg){He~Btu=`Wbj<*m*BZz9XcJXgU3M=z~jJC(D%Sm-~kBA{mmE%jfTDljs}m1CV<C-XF#WeXMn$gehK~xyb|gHuLQ4yt^p4<W1`f<iRdxaSyInuVNa;em-c8r_K@moX-_HBJ>Lx72we@{2wsO+jT%=Ym#BF@)-)e;i#5(d4`!iO(UXbj*+i^O^l&J8JP;ZI9SV*BJE6nC^x3A*@p|Y6@OtoC#0IISYp}jG@WpyJpdTBE=UrK4#ysMArzkIg&Lp09kn$Yp1mbyTDNlmN5YIbKnVtbdpo5?>;6Y&Vd{T~rP9UCVnDRL2OyYUwDeKUA#Pg0&o(o+?Jnt0cWb`T-{Y!=~`nd}IUWHz4!X89of2a<Y_G>Wqb0D}s*3uvA>knV7cQE=f7`Z5GX1ruZ7w9YCF5nlSuYz9ycZT)>cLsMtP<|fz8klN#@blmo5tPHAFN4FtUCkio-!1+!rIZg3%1=T61XFzkra`%a4-d*!pnrg=J_ggEToL*NOoMV+=-*%(luP^YpzLF6xT$ZM@jA3G_;qkE=-c34;2zL-!9Bp;pznaYfqO#xfqQ~`L;nHp4SoYb`AsvbnYC6m!xvf!><jioP_6|n2c}vETnk(WS{_^nTpL;$TpL^y`ZTyExCVl9b(-I-wUQYP5tKWc(Fj@_S_%9#-G4KlK~Qc(=(P(W?aZi&pj-|b2rdWqg|-2=K^|YsQ33Ne0=I|O0JjI%hn5D{2e&q(F0=}?G`K2%)JZ)A<(61WORTRYe9D#0C}l<+1m#xHYT#C2e`tBIKlnNHmTE0%c`)r&Mf9%$xPuuEs2{W<n680feRaVhs4WEbhQP0k?<tFX4scs&b#Pm70JID^033>5g`$6<@T+3pR`5c>0Z@M_k3Z(|$NI&*&!H~SBT;8VtUJ7yPbt6B|LMQ-d%kqKVYdI+uYRZfT2TJZVl$U@Nf_SiDcT!zgG;f$Tpy(?A^!&YCw!~'

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
