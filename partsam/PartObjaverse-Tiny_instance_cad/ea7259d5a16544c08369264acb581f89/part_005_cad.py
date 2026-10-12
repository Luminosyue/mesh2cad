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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ea7259d5a16544c08369264acb581f89/part_005.stl', 'relative_path': 'ea7259d5a16544c08369264acb581f89/part_005.stl', 'source_sha256': 'cb65c7b25155c6d68ff6dd262b117b4bcf6ea855e76147393f3caf25a04e146f', 'input_faces': 288, 'input_vertices': 255, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2938312590122223, -0.39755481481552124, -0.25239816308021545], [0.2438640296459198, 0.08121618628501892, 0.285296767950058]]}
GEOMETRY_BASE85 = 'c$}r033LzF+s8+&O;Jk}(WXC2qe`hY)H0~0mWtMr*g8^Cu_URerL+c>gbHmcwAMi@i-<LnNFrm8C?zdw34^LXt=j!bY5#Md@7Mp;|9RhY-t)fBdCv2FKKI^d?%aFl&YfQb_AFV-N5j9`TEx1AT}IW=G-c&AA8lgj_z7X}g+{#^9yz6iR!O+}_t<~=R{!3C!6meb+Eo7$p;7OR_iy9zZ#y!;zoEx}WW@Lh<A;a88!>)FsN!9RkBtg-dDN)kk)du}ziEpW4L!|XZs_^g^MCy3?RLSceYh~s_4b?(PAYHp@IR9G1lP!o-kl0NxZYFs#zEn=YkZ?(qx!Tx%A2t#!IP@36#ihTaINMM;dXv<lGNKD5B|n{)UO+}NX2%*4dG6uX~NCrH&Rt>4LvK|`mhS>4;wRI@_0q<l{|I4gzII|AJ6E~!u19Z3go)Gdu^2Zqk>U?(@pU8zgSW~#uRS!{Z+VUTHi#u-qeqTd;ZK3ZmuX;Dse(K^7wBQZdB}(BJD?P5N=<I5Uv$9oh9`@ueDG5Gh`(4Ok5}TYh+dzZmsGEKBY+R*Lk4~>R0HC{)BGcB=OXT=#Sr>15*E5M!fW6Nu1R8ynR-<_S27PQoqz><oWGK@S$OA<hp*tcZm<kL!Jj|%Vm7NpCR0-yj8g4SB!B;n~3_U8<A&4;AFYp-Xh6www;eWUJEx%`=D&$PPYldZLMK~<jFfOc|5nrAy0!YpG)4s&+eD<ox_BC2DXuLusu6be|~@A#%OPuM`PfhxUb9y`I2XC)@Ra>A%k{{pL+p3WlogTH`Ysjk8ct98-=odtdJz|&rb`t?p)X){NU@z6S7CRbF)3JTW<mSnYcr^F~yPl)$->EHzMZ<H>2}poSmcsjN8d6;OS#zy&0P>fZHDk*Mlm_I6H$+3AalIp`RzhP062CQr5o_(i2?6xH&rm@})eXGxG0BTq5m*Jko#ba5L1;^OyB$rdJZKKWYkYU_6~%kK{4#Rsr|zEAy*=KUKIn`^J9hr#I&}Bv`n<?y7Kmdr$(N_vw<~Y4f9S^V_4TxNaEuxn1Dac3HR1i+PgA8owSq{J5-JPsikZjK|l)wE>65OT2y`_KmCwsK4-yFC<PZ#{HTR!mTrHq@Q}+GVCV<gHiw1DLfY;=cK+}HxT(Jw~*)5No{jLu7A20?(1%{Jg1&fuL*aKwE-V{2J1881@QRSz|Z12)$Z34t{=FuPx8kdk$uD38Ux<>D)^4DIN`HmrJr{E&%*U*d&_(|U8YKXZTmsto<>z<zC2gMq`v2R0rF_&#!9^_39>&pSJH)>^{~I0k8&iB(P0DfCkA4@eX$Ms>m?!2E0g89aNaAzeTA<CALc9js`kNm$n!3^xqA-B8T+l3GavbrdP+a7dV7#(NI&G6p7<H&;|1(v+na-z?;-W=^uO>PIagP>9Udp+Z)OJ-NWR5YQQvc2#^3PjCfqaVkG;af4`Q7R9D)7klcU0&T&xG9RU6@2O>ix*lDwyE;~U9i@7pij+>t8pDZ6lqaAQU;>OcLy%$L(Q9s9iBCe$yB@o_3;7hwKZ2)B+`#(O7o5#BFz0+46TczLd^7B6D|IoB9@ygJHyHaB;`em>7fxN-2btXo^J3x1-Ca62<t)|=7r5%ys%eUFU)bv%z&bUOCQ9V>*}MR*?d=U1YBj|IZD0~=*tjGB9;KiZ;5)L(u{_CveoTH)rr{=&^I*k_!$io%^$U4$F)*k_z<?9Wbqb>Y@9?0cSFZ=n8+XHfs*GqMgn@oka+@YBd&=4I)>IidshpS6GOmizi(#~Sc{*oVv9+l~6|aZcFwGWHW=9qONWDEaL&)3KkVCJ49gjg~xG=1TAu#kSn<!u6}9KWWkHWjux*6K+NoV;>mmi~Xqwd7mP@AJ^6tuJsEOu08lUTKd_b0OMB=T)(>#d7FWIyxs&Kmnzq_7YC=~d1@itT6j~|mAS_hu1y3tA01jI?GwO_QV;SZ&$$fgr}o_~;kI>OxHIt)p7)L91s@65>;*y6f32OYBXbeBdFM^UUf>?@&d76Msm!nTb<#HB1)Y%R=*O~dopIo1%zz!jzgsHvqD@N3koqQh@$YjbE&=Z3Z_kzMCO6(9?e9Fq^Ewt>o7ZHr%+G*F;0HSi*Xuhno=!nhrnLJOTpM(8w#0|P?IhnE;cxYkd9tb=&64ZSBp=fFQ^|Ykh;Zln#%w(Ask3FBddkYUIq~35`;e^??<*tR`s3DiT=#-pSG#<FyOjS#zWW^d84a%gc{WS<>1Ei*-YK6W{33b3+cG}(Y;dj66mBLI$aT$!EoIz{8Q@yLwOARCB5=#Nl_@-J3igxt9w1K*aJ~96Jg0TQtzB(}JBRtaTuRH8@tFaxJ+%${@bBQ}Cj}XjXEoR7`?YsS{y=cE#$l|_0C0QP8t}eY=bCSK)c-9ITpup?Wz>6L#^12PwV5e0{!SHeYt`y)!poNDx%JtV(vLDzh3oy6;{0;9aH%{$mAVKw?ZHxCPcHmg_;dHtg-=<F`Wu25O1vghxSpGW_gl>lmaMz&iQqH+aGtHWFkZ?VcN4C8H<5K~IFZ>h9xst!XfNwlO9r<FM{boo-CN_jgT@Y(d7l`wMe^PK9q)md19PNaezb679G*w}auXSUD+k<tQOWabo&YzaqQHMCjdRV5Uq~MFT#L=p?^Y{tPU&A1EBVSc7Oq*BWxvwwSeX}-+|IFN-P%*Yb?*zCq+i$j<2}5jf2gdZSR4G-Y~){I$@65+%Motf+lu$zM<)!)_i!8PXM3ZcvCV`VwFZI@d?4%1$~N+39i1D1Jo#s^-<BIL+`L>~xY-@+%9@!1ZiQ`>JojJ1x%Eu(m(u_DYl1&4h3lqn#rIQKRpDB@cX59CrL(-}wUpA}i(f(gp^11dpU>H#Vo$1t`KsMt-k+YU%Y|zxxGy_BPM$wK;hl974`_&UXoIVA9<&cM6Rw9x$aRg%t>rsRk2#nkydVSlPrfV9ld-foN%BvcgnsV6hVxzUa^dzNepl7I7b*S!b&PO5Q3nrCo+$Ix)DQd^zT31m=^x2;E9_5{`17uKzNS{3DfRyuE!?~~5j^!1IWOCF+J7VUxBQC!f7MIo$E@ln+>R=bbKIdpc+a=KwMOEW)3APgvV`m9W(hZscR-#JacjYQqW=7LcpgXH|5o_-YvlXKY&#s^izlk=l>6PdR=B;z!1F$Xd_&2_a{V!JM<tKHx19gAYGs5wSHL|6c~+dPC-Y7&p7%=w<hx9}39jXWd-j0auZ6Cb`a2imJIr?`zAsMt@Z3D(xb$aCKYYKGu7=-DBEUUoz|F{7a)0*B50O8x8T!-jIpJmoxLKe4;RWGF)sE7Ct44Lnqu02IJdMDeCg7%bp^U3`-52%m@5S#V!?KfQ9PZb|_;f3c^X<7D;d&J6d)kp-n7vN&b>;W2{iD41_4Co-(_``7ToPP6SqAUFh}FkrJWJHU?<dvDu1CMXt&ZSkYjCG4xbqCSJ#RD4!40a(xH+>g$vM+rwN<!r(Ffxk5ALbn7w7NXk0p;0S_0?)`rvw_Pmn(ZT<_Hz=bmG+a=+U6=j45Dx2q-R4)eur82_CmWIxw}!L?cB8Q@0DXn7y#BiCTxxZO+Mv!1XEINxOOIjz23xSa{E`GFgwz)gP#=Zu}xa9>lyWuG_Bl*4&&cU#Qks7&E@P_exK?Y%4HzO=7f+fr}vA2=8E2Dj44=jX`zNXzVl{?}M7^R1mCZvd`0U4wNn=1X}G>lI9lPxEM*U%Sl);kHi@*3XO{;HUEOK0h!;u4`H~<ayLTD-^CpB%=PE5S$xNRg>}dl<Fp2Uw#z#x#(5Q!=y?W2fyx;$2<vcoCbGZ2iNO#7q0!a4S8DK!MS?FT=2OAgxhyRgqsyM2samei}CC@74;(vgj?|+GfxN9|0V+S-)aMYuj-HA=l&ueoQB`eN)Nz#DuwsIHjn%m>v!IQ^TMuS7|%ZS(T||p;Mrd2=d$G(-?CkCUYneS=lbF?@a8A6zUqF8Jic$@J8uBEHVxcP=mFl*!TLIXN`B|nw?yNd?9&SCC@&QA-l8JbWfr)ZH3GZ|xE<VIxHhE-<5T`P*3JIC$kS>T_J@NT@w>>`>o`}=`V-eJh?aG!cj_eP3ui?-`dKGWxYlwec=KT7FWVeE#v|`}V^RR-t9>UtSGUQtz>T@!`d8_~wegd&-&Sjm-!0aGTYbQ-e&EK0Xn8)YA(hde#(wGOcb0Hx`Vv{s`o7ip4oU&nBf#wp^4YqqN9%`5=zrQ$>5nJO!a5E4Q0jZChRC=%b!N)@#N7I{^v77-ALsm6!SzPv!AF7H*IRxs{y%=Vf6V{(yM5r_{z?(k#3x*<=t|d~(tNa$!=LyQg%oJozx{vzCyKD<|GPg?1O)tl|3tCL?ZZab5?%YswKc9SpkGP7fO;YQ3hKpbTwGg1zv>D7Eo0@sc|vbsto(ZFuU%Wse5=|1v0lq~E!#iVX^hjDOX<&<>ofYr)Spp*Nxy_T)wLAY*3pzsrYW7|+C10hs_CYWrJh3_!?wvRPbQzs_OWD1tQ$+6!Z?Mw9_v)bsl4`My^irZ=2rR#*G{^2pT3w{t;?ORWzuI;|L)pvu05c?M}63}BP>6{GNp@{H=n+MI-fd^ekXM%uXULI2=yQATM_+9>Idw@AN0l4%I>mU`76}7S?>b<Z`4`r(^mRC>b>mW5A-Lg5A*(Z(;uhKWZ4$_-PBu|bITL=xrJk0%zhQKPq*3EE6ja``IX+|+K;Z~(ic9V|H)YSThxWr-_c*B&Slv)`tPW(y7r4}*J(=Mq`yRclllhzW$GK$*IYa2+E1>XcI`a%W2WL0^bWQ1r>IXcKFgfvdCeQ-=c%tTzQ($b^<~DFnd`B>#Q4$^*SW-dJ3;@`6Z$IStGtiL`a0w5yr;+dCgYpzqtZJx_4hSR+ed$Z`e)aEb?p%S_tY7#<*;22+bDg<wWF^6gZ|(XdOKs~)2R<q@1oyKeTdh}pwFQ`%4?jVe@MNZW&7#RQ2&G1I7YvVTKy~G+9Ucush7L9)U{>w3DnD|7tzO4FQWc}em?aV)N%CD)N$0a=|85PO+Af%BK0)tN%S93Poj>bA59%eJ%;{0>M_(K=!a8}pbnuaZMYWUS{v7zQb#c!>)Ok%y-FR%_*2&gxi*A)CS%p^4YpPKL&h(&Z9V#t)T&(&+bV4`R_%JRt<sYjt9CE4t<s^4Rl9y{tMqins$C%4Dm|64YFC$Sm42VGYS))-mHvpaYWEJ?D*Xv#)vi9<Dm{v^YWEh~Dm{g97uP1Z)|P%ewaPb;IhCHlSmkTPoJx;l{1$U|p`Spl@-=5prNbGke8J4A^eo2XIOmP1BN&Hs&YM$@Wju>>9!&iyWA(pMo^!1ZeQoN>u2p4uRhB9Jlxvk(UWsK&mvOBE%PX)<=~Ave&GM&NrnHx9<yc;hWlEQH&70-kEK|C)rv7^k%FDA%>9Vdp!}4cXrnEZBR$+M+mMLA`HD8wdvP@||*Ir=x3oKLm71#V(?$0u%Te#Mk<&9aUwC-9<mbYY?(p_C^&GObPQ@V$1?OEQQWlHyUts~1jvP|iou61B}2bL+_&9&EA{yNK)?(AACmbYS=(gChDVR;jlDc#Vu1}tyDGNsj;sLk@)ENjTIdx>ME{A<)6&ht~$wHUw4e)Xmv#<)7$`q8(eR_#i$t<ujj9>)9VNj;RYAKSh{-<?{u^I}`2eHeFR+s^a@sJnCCUZL*8*o$pT(pRJI%(emaZ&UZ-Jh!0k&seo9&9+L{Wc)VAHGuj}#%laKX?O;eZ$_>1b!ASa2Qyar$}*?Y&ogewoOS3sQLB8FnKQ6w2``_L|I>eQ`>%hddLjSqKfL{C%fEkiKG|}uo9o{np@BV1tNC>Y*GpcK=haHm{skD?s^|'

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
