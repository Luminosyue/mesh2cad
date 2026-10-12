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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/144bf300ef43437096e4be61f4575bab/part_007.stl', 'relative_path': '144bf300ef43437096e4be61f4575bab/part_007.stl', 'source_sha256': '820fbd3b5a038c74860fec56ad784296dde2be833974b38849b7fb4d941bcffa', 'input_faces': 242, 'input_vertices': 188, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07342582941055298, -0.03897053748369217, 0.33425164222717285], [5.7794153690338135e-05, 0.08030688762664795, 0.412453830242157]]}
GEOMETRY_BASE85 = 'c$}q~3shFsw#T<}OnLP1kw;7Evouf<L((Kgx8{o!MHB)R{ZR3ds0c`bVjDD6e1P}>5%o)apvcQt`RKHLTu-H^YaKh19_zErqbFZ!mZc}pTL1a?Ub^F+G0wP`G3J>6_50?YYwoq?Uf%{H27COjnIS)IjBeF`+~#Ov7}|V{W=2{<a_ZCx2`PaylG5uLPk`&6hkoVIsPKr`dPbTt$8Tan%7kRUmmPjRCw2D=aQID{nVgy&KV#g?<cSHI4~S1pNl-jxN_<j+8v6%z?;hX?ZXe*tbo?KGymSqoCwG0I{bjFVy_IuEReY|!qc*k%ylv`CJ+^(H{)_hJrQ&LEmzA!)>&|V&yMG=p{7-8pY45(V7u<QwS*6ETS<HOo{cbGsIF7tpiTL97Iq+X~0k=+c7QUqGYWP(xCBECL3O%;Jirt31CEjP?Pi2-P|4z?MdhEK~2;5zCYCEp)+<!Xixt)S~EdP$+mNhpYpXYcZzx&>#GVt>~st^|zjy%?1TZ0>)&CN$0E2@#l2nySVdUAWNfRDcjZs+{8RgcZ1r%}J_+HtwBV{zd2ntar0KR8p1`g^zE0v=qm0r|h025x@%@@C9i`f{@N&f+Pk$FZf8aNiBHaosPC5bvt+0JoeCH)Fp3^CbV6s#3(aDvHAR$8V6wOd1XD@bIn%Pe?_){Zov@H(mP%@{fB|@}Kh&e&v%)@SF9(9a}xYtwLii{KQOfBRX#r;y!7V1wLvjxHV`DxRrjwg>mp0S^t*?fg716=qoeyf$VR$5XsYX;11O1eo@w^#1q_|mxgtAf7lK2#;1=+o}~$|<GK?kCI9XZ-jP1vmW8^L&PqRfZv}Ux&t4&Y@t*8^lVEWBP<W~I<<u`Q|M#D{z_%xZJA9gfo1Ln_t$?)E7+<(5&(Yapa3kv5rSNN~OZ|;<B;Fo~zA~TrTGl@+S$NARaF=I0*~jljOCI0Q3f$-G%cRaHPH#j#uN3FvbI;kb&a0gpkY{z(QpAs~C-uh+1~)pqzYK8)yrur1p9FVZC@jErm*eC)T0D9^;*GK|duhI*Lh4T&E_`ErA^cIP)BXN0CAdChLmB1`2$B3bp9*jO@pkb47zl24I0$ZR>kIGLvrF#l<SH4r&02$g_+qQ{+uuSYzMTX2WyW2Wc^8~nCw*ySAI*h+Qs<R_6l1*JAAMr2tCs$}a0T4*IhKR@JiTOnKJ@~(58hgZdB!x6`m;x_1)n(wedw4Y&zJp6L=pNgc{=Je#(PNo8)vXC&gctr-$7qWosIqkZkayC*xx^_k#+d~HE`FFL_Cl7?R(PCDGuTG8ma5_S-G#K7crlGJ#Q=W4n8LQ;updPZ&`=Dci)uz>hrnqOXb)XyTz+g|G1C99cTQppLX_4ssGvzte2xAU7jbSTIvay18xtPFa0=g54iowG;nid2JY9jzX$R-UJ~xGtI=O}uN`v!M0-h|z%i)bTDe*3@%-aTtebCFc@DzzWPQBK!L2>VQnB7=66L;L*d%=2T{%BbSIN8&W`i3IM#%Ymqd?;SGY;Gl6Nmh+v>K`3Yly^$<;pqJa=)B=bArL$Bkm#I(a@IXqH;N&6LawhJbz}U5AqvtF9tU<){n)!S98H#Rg=N(=(l9v<N4ChH=N+^KN~o2TyZ7xy!(zu-L7#Ru>R(cOOVI8q>J?T{y$4!T}hPZy;&zYzhZLme3{94(hv8y;d{<qd{WN8>Hw)HZL;u#AIbA{qcynuNCLQZJrDh0ebi3+;eJo~zVy!?C;N~l_nX@o-1eU?`D<M=@6fOFuwEZEk@LG+&JAnPJaD_{j`ZjGOxfQ<eZWocfm=|=wJhOPmzE>%(HrwHU;IS*o*g<0+`Kgq-*?7=84~X|Y8m497rX`DzDDYI4F<RDUT>qnX3O`ESvEw@<-f&Ae;({0_w`Og;fwZRf2{>CN&jS$dlzJ29g~|NkFhpn3G$x!1I`UcY=HFD>Q3Nhs=s{S#vGIWk7y(O)@}J-ZGKA5y*rh1j>km`?^h)C|0P>^gPk((3F&8ZN5_TO#}fHob)Q-*&(X|Q;P$PjWZtwgS%0%ONBX9Xe2-nQgx`EZ_?;Ot@8J@;-}8;IUiPdb(hr@3&LY0?w+j$=?h4K)vr`PXQF9L5?0X*PrTf=0!W-@bcRtuFb$;(B`HPak?fg_ZhcYCO{bPG@*Sq7;SI$q{%Kn~xFdySn(KvU_$hL?#A5?%l{9W>V?d&7_xUn4E{rWB0->(BD&*5NjbJjO<u5V6|JdadmV;tp$_Y+tAaM`cIAaJLD2-e5ka#->|{^VPTFT8;|&D>40j|Dg9Vcrjdk>5OdP2w*GfZJiG<b1ojM&f@8m-nj7*0L|pjh21!pM&=*$FeYazKT4ATUY1c`re6hK71(qZcSSV?p||P>Iqyb-*@FFGEjfg39N%VV}$TMxo;v*RjA}2HdJ{3N5Gx+5262!%d;f^<Pmr;bawPdo#qNTAB@)5(y;E=@5}qeo!<+;^gOtA+gI|R&X@0zq|JDLb$Znzzw_H1;fI{^UfZvS<T)?z!^X}Z@g8iK?g4kaJ5YGR5AuF|?!KJQNeRNot(=AWy5?YBx5f9;&@6CkiHE%3CChyoHS@r2M;qzSANmQ8e2@g5Gj%8W(sf+8Pae4O>+(I|K6j=5*ko|4zK482p4%qz$GjzeLN9ra&P@=W^mqJzVy*mH&Y51J!uw50#Q5kT`ChJ&_cvpCAh=y($@|@qM#2N0m-xQp@m^}qtPr04-8Aq`M-lJrTq^m;*8{i5RLMFNgb2_08Sl;3@MV>_FTVzy_j7Rf_7c?Twm+8mCeKa5_4h9!kL4UC{Q6Vi4zC|%Uv_K|?iDo|@%M_Q{sr>hVk`|8erW*Ce|ySjGVjM(3E=j7(r-OjXXKfQxIX+b>7Vjj!tb7+fcef8%K8V{!Y`5+wv_tgq8Yy*+?an$);UkUe~m+<#v{Jfbg47yrf^qLJo>!s6ynVmt)$M#V@_OOR$t<K9+CLkKH#oho>G6@b^d<T4&2NslzI0xmpuN1@ZMk^%8>Vge?&;U)m*rBxJ2@FllVjR<8b}3m9oD9PYQ1lF$UMS7$|j~Zz0@OJ{tEm|DL?RH@qhKTXY|VJkbZ_yp3KZynA^J;_mK6e$$W7^{VvO5dZ5l^7~WiL5WZGkHY%aCd$6wy&}A<<4DvqvKI5Y8Z?$X)|5!ZAFq_>x*xgE$HS3-a)8WxwW;tI)`PnqUoPiT&lP-*{J<UQJ20>N^C7|$PedT@>?g7>_b%~%eZieKhspa}z&_#m?Zc2Kr-$@Uy>EpZcVEH0W~@9f`*^Mzm%z>RFXh}Gu$%i;6pHv2$ED8fZ-l$c+9SR)R^lIHyb=Bw`o2rG@CA!%dq@1{uS?fMpUbWFRvo3x(`aT)im&shB@NMT^#A*xmZrY=Z~bYh%Zpw9zkgcVt!g-^Y%Be{)a#YKqpXm=n0g1bW~J1cxpb?Mts*bwXM3o%-%Gtq*#XX3qijDv-$T8Z{s8q}>Rqf&*Rq*@Lmj=GW9`>cS1PMkwo}<Y>PqIXCaa;=EKAv2%H}A`q0ZucWifY79Tux>h_VE(Lmqh^<FvMvtyZ=~*<5Oixh>8$w+_pvUr7Ft<&$ls&!cwH=W&f5vfUgXB-=%%*QQ8Wxw1vnYk6;rsI#b-vp$Q=BG2MpY%!!CHc@M)_q~eyxs&^&*Sw5+C&v|Bf9>C+E@wUO(r=|+#afE#3#oVUUiZ?MQtNph?tdk91@l+%9xKS#vL@XJ+YIT28nT7l$2{&s4%uq%M+x^RpR9yyy_;+!nO?UgT)QQ_H?4L5=-!#CY>G0cvQ+9Aj&)45vIy#Uj-&Z`6m>ku!<4<MtRHm@$3vK-FLf-(G0fql9#$u36l0>uBUo!Zuh%+-<9OEYq)y>j=bXqIVt8*8nXfN%4r9G~yxoxg*}=7WQ&}djo3Cshbt=aN{CqKWHpd10Jezt2$GOTfm`CfkIewElGN~7Eyn?awsdG7AK)slLMV<Hp>TIr2CUpwO*{nZ>dOpYVxHeO$GdRxWe7aU2W%ZQ(PFVwG^_A)W6Ff@qNz>YczCN|~26by?kJY)hHT5!OJ(Mk_X+46bb#Hn<>fY3?=)I{|DqEv0j(#w89Cd&Cm#F(w2hu-Dov3WKvSj)s>O}e(G_9x8k{Q>Od2~IUl?_rBO4E82P3y^wd6r}Cdr|k|=Yv>hAagv+YXa#*sWpGx(60oB`sNp{*+6BlDH}@DdMy29>UPSyC~HsCx~sC$oI8|j*q>}A$Lr`vQ$Nf3AJ*QB`NvYfOy7puq3juDjg`$(_PVlgGW}UFeJAQ*>YmEpP&Q3jI{hT-0m{OZ4X011PG`(;?oU&$TOjqb^iNRhp3=S5kiHSMt}&8zhEw;XMY6_c=*QDXQb+Q7tsgPuS@L4dudrV2yHkfz2hg{q4xoOXrgby==G4uo8?!dOZZFcb_NRAH`%^zn-<Y~F^E}PD((2TZR;SK1u5lB_x1euH-GaIseRpbo?<VitBzuLvJN56CwPg)YQ~T2g)u}(I&OHY4zO@gjvqvG^H|<B(*+;Es(a)sT&xL*-I?#8e*5_77WiJ?V?&<UKQTnH-wfCidl)5#|m)Gl<=Q!4W47K*-sC}tB(odl7NZm(S#Nc}Mn|b`Je>wm6kEIXs-~0pme_r|9UnlBbIacNRuU{@A1~<_Cs}A@2Sg2XLO5>mNfEw8'

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
