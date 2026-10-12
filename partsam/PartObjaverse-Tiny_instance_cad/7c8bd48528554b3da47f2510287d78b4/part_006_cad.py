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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7c8bd48528554b3da47f2510287d78b4/part_006.stl', 'relative_path': '7c8bd48528554b3da47f2510287d78b4/part_006.stl', 'source_sha256': '6229438b857f70d606bcc621af9ae2663feebf1640c6b0ef6814b8b2489dd2ae', 'input_faces': 248, 'input_vertices': 222, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.04218019172549248, -0.0993310958147049, -0.04434053599834442], [0.04227536544203758, 0.18943539261817932, 0.041364796459674835]]}
GEOMETRY_BASE85 = 'c$}r03se?m8pj7U%u5=ENGdd5K_n4$H#GDc?<r`A;vF4S5JVAy5JhvmqbY)bs343YV1?i%EJI@y6*a?anF8x1S!-#!t7e?tZFlB*{%qr(-E;Qra?X4HzxjXf_sl!*`@EO=G|<0kGe?2{x(FRg6K4dr7X-7k7953yu-N#>Ibm^qqGOiY2``gx{xxd)xZtsYQ|*KVA<1oSSlpagw}GOYU%0QEr|1^GC^kMeG<w#e*tub*KQeSdT$tg<MTEwL8Q1PUK0cmezh0i=3h{sZYiTq=-nXNm!cc98?^&CnQdD8MsoKu5?BBdWzA*j;*}PWaD=y!jF@3$}$O7|Pc=S8+h2k|_|Is%JUEhn_N8j5WNcEMr`-5y2UytZoMZWjB7`p#%C-Q~zEUK@yvtLtT@ul^VR9}DgU@2W+bIGT6UUH`TVrq1(c`d>h0`jQ7aP-mux}R&*9{PM{`Du#p-`kVE4_^^aP<`>u9&x6sQ#z3^f7n329P-9uss~^H<1>n*G~}+PdOKfI$rn?oJ;L;bIrP1!c6oH4qT^Iw%&wz${?niOl;c+&9ZsKLnU_ob*1MGIOMVeMt-kiNLj9~(Eu#2pOXqBgx2c%wtF^8CD=fb7(N&KBUe;o2Z$b7hYG+{$xBtZhD=RF%dfDzAwZCaZ82O#=?xg;%@#gl-S(riNAjf3U=XnpwmkS<7S6F=MOgZ=G{;{K}{@O9@Zw%r7$*kRD_4SYeR9{N2<#Afpb~`=SxncCY+Mwd+eC0_H=dD{Y#S!33y;kvag}SR&UrldM&m|_h(>Q4tXJ*iSrCyvr85?X=5580~o%1a<D3aoh>qfquGlZY_cvK3-UuDN}iUK&#kG;8st`+vB_G35??cZEtd(L0U@gMdJrE8D#+bI5#mYgRm#_h6Md}Z+_ZfA=?${T5gFW2AX&g1KOaGlNKOR7q~I;LVdeSerc`RWTQ_kU&GY^yJvvgh$~FKhVB?4Kju$rl$iaQ$Jw)($r7_Y~47zFT|hf4S5)rNZKCnX7nQzV(|zpF18&rTX8*a{Za-7FvD1OCFE!saf+V&Ld~?)lv6&ow++Y-e&P-FCVHe?pjIxEOws1mA=<2k?UXYww~&BVqbGQP)YT>ZlP<nBl~K}os)FmfFIN8`QghWoi%FT*-f0Uud**4&puB5P*lqE#2N8_v_Hn}nYf#trvus(6IVv<-o25>3%>O9_8}UVDMgfriWB_Y>|$zv#ze|<tv&nt_$37tXU#><fB0IfLYn`=Qpdg2Zb!uV{?pCW|DX3FUwegpLBHil&s*(4z5rjjI%6~4r%x5HckSRGSe!%gq_@de9oQGUh0uE6*nR=Na{Aq3it{j+pZ8_>$yW~1wcl3iAEhn)sk6(decNB7bxKN$N+G{XIgPJgrcmAr@YQc7vEQU@C28baTz_mUo?qWBq4}u67wdRES7*9ypn88Bu!a1t-FSVNeLmf0@zw0HJbyPer}a+Gccy+(>Z-|?GhSIu;|yQg8NhiMUBdg+&qW(4&aFXIUtKk5AAJsAYdw|Pqs0&6{V#hY`NERHyl-ZDZJ^KLi<_?@e&#xAhl_tQ-KQ#)=S%the5<c)>&NT%&k>vt@U^G?dEOP=&!@a-tnV?0_lw&Rd&v(FXx`}Ge!|aNQk?vppEjG~D9NKX@jU#6+NFm);c-blu+3)im5bMTJ>S)m$D`rkT53;^Khb;?j&{$rS$y&D`8<EcbjmmBr(oJw#c93yc^}>9yoN8l{~bTqg`oE+?#wRa>p?}_Z<VWQT!o+7(|JT3)|U5uuQS_i7GGHw%J-ezl=FQ_Dd*ke{k+~TP1r&TUth!Pm>%T7>qvrEBGo@y&+B>8P+A8S_;UPRZfC_0v~LQ-z2oU~@iDj4i{t3S*jMkka{Ld1Q>p&ol5qOmgV$~4LhI*zAs~s*18>~ob@P1J$>eVd<9*@d*ZJHAUz+Akair6))4C%5_&AvQZ~SEHA3Y@?-|7qMLe9^q%apf`z7%Dne3J?S_`C&Q@7#;?Wa4GcfA9T4RNtwD&vk8rdHsQ}w)vj&K}*}8N6#_(#j$js$mTpxg~wT>@YRWt+z;;Fw4O+(D@RcM<lEd2(bbtYi!blJ$9dShC-0X%-WW>leEKT)^Uv+l=yUkuOTX}V)sNu)NqutL+z-XYH+Wvy71Dm8Jot%xxn)!Cw{h?6p!N*BN4}EZ=M+8Hj8e)geSJOon%^|qUnEB#K8M_><2aMroS^=?d7jUs?q8EH^oyYVMIGOr`dLo8%6?cS?Jw$zAv7*>^+ooxTo2QD&FEFY&s#;l^xZGCzsN&xvcK#kxAVy%$^*G(LLuGvS~=G*(P@9tFK3gldLHHYf8_l|`Qixq+PZ`6YxP~}y5~;v^*?;T@tX$GJk-{YBVX_>;QD@^JbpXAqV|aCdE5^UU(&T?@5y?9C&wvqIzZpQGLD~jL<aeK56{DNzkuPq9_FTSKR>xx#{Jcd@=bk~%+FQ1@EG~_+qnOC1x}}a^k2^NF`LgZLN@zi?>t@y`t(cX{@%TauJ3o|{Bhkwz6M`+ddm6VVL$KFJ`ZDQJRIvezSBs`PaVGG^d0Y0S9jBW<-8S%G#+gVd0ncVNc&o&FGak=d4BXEuRpK$T}t=Qnak(2>LkiH4Zbe6ru-BN2hlvzmU}4_$MpfP!&w!%R$sN}bx%suDGvn?nd_&z@x1VOnc5@5*JFR+^`Th;?Tcc|?zB(->pHBgwOd2}puXJxpi#6wsPNU;ncU7Tm3yteuri$EM~>q6N%+zjUs`|U{7T;MX5^Bu-FnF5(lCwo_eNiN`zG(d3&Qw3RM2iM#c48=&%LK}czuH}-1X)DznnwuR1{zGl~EsYKgYJ+Wc4MldECx`4`@FUeGb!pu80HpJp8Bgyq`AucfRI+xZp+S6a7?2iYIk);rEM{hiJc0Kd#{W+&;(m9jtRd!WXmnJxFj)qJ3AoJ)7pIKKwL4?-#Goc|wM--fhOdhY#hgzIg)eZ}O}_Zs(oqRXh&ttNAB++{^pZeyMrLTe+S5T>7^~Nz{J$^7K2rPI|{uzUu8`czzT_as4iSaaLanDP;e8^B5YJhAN(CkDKs&P;g?l&EkvR+c^FsKc2r$>-jmp|CP^O={_Mgi?62eJk<_1qxV^1U`tx>#lI!<eXA}Gp!hLq<ZCBI-Zxj<CtH0bVn3fV|5C=kZ&d1Z-qAV^;C6nwobUJ7gOqpLsSP}@bJQqmCwyhz5YD%d#mgz)p(Esrb)&ie>!<Ct`r2(iXKD@8D9^=4-yxCDZ!S0JJ-5*pK6K^x-2OMHf5d_FDUY<&x!nGb0;qqKx2ie68isN{cxUoD3153Kf%|iCCZ7*SjMzcfk9zX+Hgni+^`-vNJYTl9qw~BNsL=kQxW;q)H-^wUBf*y@?BzWFH8|VqE4f{{AC895?;VZ47WstFS00l%epL&Omo|ypv-vvbF?=<BFrO2y@cW%!=uEyo*@>U`QUb*nirAO8Dx6pM68O5=SN!|I!W7=$b2=}x`ufNAJRidyX#Q&T@%%eP$^~A>>V>(cuhj14-#J<p^E^89jMje@zAD|~`U4+rv-;wpA2|M>pJi59e0lkC&a3c8{N7%cN8=;rm2>^l9TdOOm)@%3{U~z>$8kAB=R4WyeO~7y{rEkh(XZ*maT+{n9dGoN!UsH#ZT*s;^S@cf^CjqYI)6)LD`~xy<7adKd-R)P^;KJc9>@1a(C-7%Y@K|e`F8G~m%{k{9lop!yuJ+yTTkC}DWLO;w8)?R8|Tjs4t(y{*!-~>-Ne>Lml&mm;3$NLT7HT(P4ll&|NT#~k^TR>pJMy_{=YxPZZg_1!YCV|!@(QD$<SfoWbg*)Q1Axudgu`Fdhj}^1YQST3$=mQg4aL?gV%spLkEFZgI7WQz^lLt^i8k=UI`rtUI~5|Isp7Gcm>oKyaK!&`UZG8I0^cDa1wYK^mpK8;HA+1;HBV1Xg_cwc!^PVLT5tzflc)Uo4>WcXq2|lm%tuI5slIf>I`lo@LyA?9k{nq`WU4z^mT9xqqGvte|BJf8EmRKC7htIg3Wj@7^OM11=ws`Go#o;n}FM+ZEc~ifX#SajM4+z8*I+qV@4^19t4~E5%_(h<Qb&^x&v%#KKQ6nJ~hgR&{D9eB^JK|UIk*8LXUtyK&*Yx55cAufpbwW3%U<%>R#|x)Y}5h0-Kr!o@<miql81>0h>AxJO%Y;K*PbNhJxd8zjvTpz@}~nzlB(V&>3J;CxP8jZxl2TY-#}59Jjt0yI#<d(7s?(eZbuj*9$rdY^pbSG-8d1js%-J7CaU8LZIWprcMUWLA@|&2-wuw;CR$afQErhjR2cDmMU<5nVJGNbsP9&f%CE$S^ze6Klm8x9fTHxO+5fkMVnHf31Cy-1D`NTwowkDn4AfX0%w9_puyl6@HC_Jgt|h5!LHzrC?=0XF?l{T3LJ%d&qpzN5A+0h5BMbX4EQAYbLeI8=iqD5ufW&9wa}a3T5uioOK=^y26_ct1HKMD3%(A%06h-A0M?*6U=6IIm>daR0Dc=91YH0Q0#8RVc@Z=Rya>D<dK|nRd>DEbd>C8_y#lTTpND=4J`er^dK3HwxElHuxEg#BdKr8Xd=7dBd=7jHdID_fA@C{iCnzQtLNmdI;0$OCI0L*GIt{!SJWKd3*Jq)aJjN(pp&g(-!5zR3P*<=6xDB);xDB`+ipeg}abOqlMCg3*L~t~84>%gU3wjc~3tSHU99#}Q4ZQ|F4ZZ}e1z!T+fYyO;fNw!-z_-9(L$8Cs2496<0AB@HK{ap{_%o;q{tUbu8VTMFUMT!FmlmR!Ji#chK|4X;26qB?h6aH<gWaIh!ERuG6q9A>BCrgOg>DDOg43ag!GZpEO&pv4r~m5l+n-_{te*RiAOHHz=U+>#-%K%L{qrRy(EkPV++`fVn$RS;XP&Nve*jc8BbN'

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
