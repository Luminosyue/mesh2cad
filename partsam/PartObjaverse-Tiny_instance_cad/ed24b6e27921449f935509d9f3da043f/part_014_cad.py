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

PART_NAME = 'part_014'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ed24b6e27921449f935509d9f3da043f/part_014.stl', 'relative_path': 'ed24b6e27921449f935509d9f3da043f/part_014.stl', 'source_sha256': '754036dbd714f1c385b653199294777c5af9d12f2bd07571149b928afdfd1658', 'input_faces': 272, 'input_vertices': 199, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08356200903654099, 0.270345002412796, -0.1589248925447464], [0.07275880128145218, 0.4777456223964691, 0.0825880616903305]]}
GEOMETRY_BASE85 = 'c$}qL3v^Cry57M|6cx8BqU;>nkh&zaC2Hi?A_x%?T9=INlDHJPi6GMcG?luvi6BU%cABcXg(N~us{XWMIyLR|ik7mgb*Y(-`*BY7jI+Pzeg5{hm$TMc=VYyCz0ddj?|%3D-M??I#6;C^&`OiPAT8{Nc9C6LYMMe5t(CSQA$9(&X$fgP<|Qxk)0#n7e_p#bdhE!U@qXF@Ei-s}LfW*{;C^~=|HQt*-SptZq}2JTQ|3)hN}Zmd^dVE`q$SvT+RQ1*33j<lSa^6hy?57cdY1lw{A*;VV2z$$b=bE0&d{$SR8BY6Em2m#duE@~jqG|~s<J!dc)2RO{C}=g)+`)$Qt6(HXY=vg<n_??qpeP;vg@x`SE#ZT`8af|_)+*9PcJXRb8n|tAkORoh_8JVxdM9AFzCj_PZ7uLvZ@5{_h`_qgFk%^zkwZBA<uIb@-lNTOFox6yox-+YM@({oxVo=no&~_FK;h&y(a7%lsj5$RoU}lp!ok3f;d`-pBMV-`tnftd)jZvMLt(*_rm|qH<IVYbmZyLa-bUnDo(-g>!Ujm=ZU4FudEM$&+TJwJa;%n;-t?+`x~>PmqDKx4Bgzh8U9Ab%>u;94H7-;oa9-*_jajIdx=wV_A|r}=!N&X+qIDQw(WKt{$1A1fnU3S?t%SF72<25ac|?flpmlQv%<vx*p(O2&U16AS4w-XdSD~$x_Qv`u_N(bcTU6g@SlFZ4Drk3q`uYHw###)pzD>hC4Z}bYt-lNmEG_^Sp(hO_f|UUn|dC)QQRE5tA5>TRn{h)--YMq<Vrp>X1#^y#^yoS{Wl?hclkxMgISlj6V{58@f^KkE84mHMA0WTlkw9%rx5L(JzDhatB7y5)JpOD0Ewr&i=exg443zIE|>RoI3eRdW(3BK;i-}SIkZmlyj6~NuztxDJ#-}UG$xgpun(m|H^2G=#)Es$trXbBqoEsPddobmz7vW0_(0`5h|{T?w9la-JK&$P4Z0OIU;Ot*;=S&nJGLVJrzY}oJ@sekMvwW>^>N#zUdM`d;kkO3OYz<l-K1XWTd*#8b!%ZM{5_{W!+Wj&h!FkwalF^FrTI?8ZyE$$zui{y>7OX=81>zoh~KwJ=26CJ<YNw54P9@1OvcZu=rY7_oetd$3PV47*zcYTe=k9t-fJ)pwH;sVKkTDha~phtaarMh7wxvngl_h`gnaaq6R=Kc=L*FC!WZy&S6;(<=xSF_bpMI64*2IE#Pg@Fya7G*AJE;UiKwr3q7b@~7KVP&i~aVZ9Y&np06q3wiT}mrHxa+*lURrJuilmR|8nqd#M#|Q^pQH^n0toQBG0#se7tvmmaH3_mU=MXlWwkoKJ`QCuZNqL<GI59qHoSVjq-O5(2uToGY|DxUn~7GAP?<q{Jt-Aqox@Cny2o4v}fstT=;i?QP%BM%P~$o|4J6U{YuGydJ^Ke3pTzE{YWj=ZCAz#jC1#b!I;P9je&^o-d7~`O1-)Y^*ysm^sQGU&kyHAx88b0#`*h$KR|uQU6*|(e!v;z<NkNFgXhO1vJZS(fp&Hs|Kqj@Uwy;NGHwr?+=KQQ^oHoCmrA?c{@X5J-I|*9E&QuLKY;kB>T=LN&HIYJ_dqrDr?x=19*To*6kdnFb|M+Nd8--nbTynId3KIk4t-v-jKi)=(O+I&j~b2j!IRaw3byr#R}eqxNAVA7R*7~hOUp)_w%?<jwQ~_z-`wt?rHHd=kgO+-7E67X{MC&(%daC(S5^ZVKaDSE!QVex`u*BO^ot()ODb$cL#fx~Z)CotY=Le)-5UO`&T*J`)?=~I%`UIXxE(oJ>O13B3VwI&<6hmUdsx=z;?8Bh{^rV`kiY9nS=Bvy*+S_r&aYqNM4yxWH(?g?F~*f7!%kg`_V+aHh<sdAufG6&%<Ox{kGnQ+CiLL{LVc~gVd5XR(Lg)gj)A|KIPWn0Z(JM$|9=gI?#?U`|4$-DL%(oQ+HK((_-k`IyYAO7+B5GwiT0_UD(gm3cNyo8Ump{3zy2K`JQjYzLuFp<ye9cmH)pnxJkN)T9{b?)D1Tjn_nH?LV?ERsJTpGxKI2MDD>fqTH$Ge5od*By!7`rXYo&jq?#zHb@CS?s<KtN5uU-9dR>XbgmzGjG8@gkjdUfympdGx5ap)?DnhX7Gp6p+-fmkQ?@FMJ!ddnhNH!d{5II$)SSp<K_`eSv!y%@S<9s5<^R*HG&N^@1*qdV3&qfbdDe&@PsUAv5R(i(OP`-atYh~yL5R_4)|Em_d#ERz0RDdW%@KMdzA=Q?bbxn6>Q>_}N>YS!Rf;{G^eDSpowDf8>?=Z^U5&UN1N@~s@`x8r4=j$a|`ZF!`eqlYd+eDh8R>`(4vgI|OH`(3fGX(c_8kG7x|x^w^X>gM@1((lhbhIY^b%r($2N6YvewgmOnPp(`GKhu!@&G`!bqBZKZ0q<>dME2SEUvRF_W3J=8>D+$}D-h>3=RR%)^oH)-$30Vrh`zr2NokKz<mqbrt(^ND=LfIuJU^I^oyI-J46MNTF;bVw`AtjO4F9`LWSkrc*dx#Fh3-7(=;5Ko(toX_-zyS!`RdN|l65%+y7PQxjr#fx#CM$2td|FGL7YqL<s9|F!QJxw^U#g$S0(?Ax1?ToLvW9Ao)5jc)uJcb-_<5x`enL~{<r@At@tO#KsSfGa9*~mmdm}b_=e2ujE`_$bDm@Mu4kb;&%MTf-h}QvC%bFq{B9-wEb-Ugkn?=@Uto>u+SAgG(Q;0zJ0t!lzDGZ5&34MT^}i|pA0LtPdGUV4*MmZEA99}Ot;BVrH_4E8DBX<tW`ukxy5k;UB@IBmjgNw4-1d|EuUV7|-Aq|8_np5rK)<^0w0H;acidmJ;7HN)vk=Gd+l2Y14a^e#lZ(<0%{IP{ydK{S-3&b_`J~ABbafgk<Bs=P^H7kS|1M6Fdw}Df<=&bq_Z7#z%*xLZJt<!9afa0s{$=gu9uVG2^zR2_eKBq>hi>%$SmN}EUJU=@JQ**Kd?f9k7xfDK7L<$s>PvD?+mMFykQIJS#+~E7X}&a3?itQ|>$63oJMO<)_FkDcj{CA+R|nmBzjnocCc5K3?s{#4>>G~zyZe(Q=*I9YiL<HUCYc|ZoZr`^9ZtEhf0zNUh`;0efUzx4bjSAuS3v{JWAk}K*5|>O=AvFzxw0RA-d4t&*%9ln(dSPx?;YPatVh0)eP+Z6iF5V4;Yv6D{5^E%cM^T_6}g8wzN_fr;c~8Yeuv3j2;F(!bGIFhbA<DIksfPezrE+XQ_MYI*>Zb~YU6s)e#FKDS}QGaiq9uDC8|HKz5ge+Sx@}0KC$)c)9e5HiEWUb!&5f;5xs2muo0^2Y9oZ@N2$%XF~P<l@-a4M&?b||sruQ7Arz0LjUtaFkGGLQ`z&n~`LpC9L=<xfCGSD&BJV-okGTzEUW2H4b5wR1Z9np4+H^wkXK4G8_hbBLXyeG!X%lGU$m3Xl#WQK=(8iEw(!M|&LmtC6dVw~cT-hY@7sxYx-l1|?W@820Am7Go)Cz2r+Q=m~^Y>-+@jkP{r;nBOjt^zM<3m~Rm{3+{A1T{}P&|<KQSw0YVA@{fy%;~3P`oGY1oEEb6A8uF(5@g~LtaSx8o8?bd#t~*yL{TBlx<N;eKTz#c_HI$rp+f;Z8d}Kr))BLvQIyxvtO1GnS9<m?vrQ>$P1WL5^X+tKA%;*y^V%8>XR$`7@>GO+J@viZPeNLfV_xhWp|VB=I@I4w&7=^CG%1FEw|BElQ|i}HZ1VbL)hmnY&5sgf#^g{eammm-<tbqwKn$KI6xfs(MoK*O&p-sjWNCPpQN_d#;ZR5CDhci9AKk0(TrMS>aB?8)b`n^woyscP&>>V_7OGIQf$n$v6xVNHlg@<Lh*65DdfsdAs<IRmQZ{oq4;##6!Pihi)a^<FSL<pBb!kC4}{|V3B?D~E+kiW8u?)IQM6OZN0CPpiqE2*Mm~+PW)X_NM4L@M&qkJwm4xE!3B@A`#Rt;PBUjcSA4oowb~5=;@)3mMb7>87gR$lkioZ;|lKha3KiPPbQ2ZT2@hybnduR`lE4za{$VLMj4-<;lBNX@kDgJxfAaZ5@jr<WCoozfw`w;nq<i8^nZ%f;mT-nFTJvI*7*hVP6olrcFP`r%RL#}K&`Cc1aZM;P&UQD}=+_bUD#s)(1*J&4!Z?rMm#!?%pHU`*unovBPwk!E?8(}uO6N-1C?MVJd8$)cUb6OvkBd96<JfV0Rq4<l$bJWy&^uG4nzVRN*YQ1|vlXXn-K$g|Iq}G#GEH|c);sGqHeAF7K)-tu1skPR-$0^>1Tv>l|WrJx|>}Eu;&u^;iUF!m=1+pAK9>83B^Ihuwek?!1*nZk?Ypmi=5`OeinB=1?-i?^V`n6$vZ@&I~-k-W3{hG2ZT97xQZ9?9Oar>|@4zvB0tsz%+Sj9RhUd3`1%j#TE!Ls5<SXR7{WyPymuB5HzZ#C3*k?-Prclr3LaiR9ZH)vlWSJq9g>=N?#Xy2t>LjE3YEupyD`&QdHs>we0D!F%WRCXWjQSG;VY#;OAN8MZRBW#N!)T@Z2Y`3F)-zs7?+qO5kcMPm%f3IdvlW5nHt9hj6R1R$)@;>}MhjuNwvL)mttalFWyW~0KDt1hiU%giK|EGU(`0dZF2HQRV@Zfy%-fNrhlZke$UoUYnQNL5`u)T2C!^Zoau1fz6EW?ee'

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
