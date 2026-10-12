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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d1a5633cfa0740d59bce4d3ea051329d/part_004.stl', 'relative_path': 'd1a5633cfa0740d59bce4d3ea051329d/part_004.stl', 'source_sha256': '408bc7abf0c7ab562c00f1bde3535200adbfa01dc362be7be3e01ece3576080a', 'input_faces': 436, 'input_vertices': 312, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4950654208660126, -0.3561931550502777, -0.4999997019767761], [0.4950461685657501, 0.3576563596725464, 0.4999999403953552]]}
GEOMETRY_BASE85 = 'c$}r130RfYy2n3MObv%{Hq?!1CV~@cWdon*(m8dUGgB*Tlj4BofJ5h4)|Z`I$4o0dUGdgYG_4d7R8X8?iwqGm%8bC)Qd6A08EE2N>s|k~U3<Cj^W5hgdfxs&{`+O^?_1Ni*7|DvsHV+27~;p@n4dQ-!qMF@c=#9{jHMA#i|0&_STtbXg1>qh?a1dpQrC^0G-mu%FJr0kPTv_3i>62Q9bxPH)Xc~G2HE<~oFBC~DtzAS^P^@&aQ~0tZ!U^p{-W983nJL>kA@5$5@ZYM7i3#*`xk#&u}g415?`Cj)RrDnKx*HWoa(`M&Q3WHs`%Ez3(21HrSHn`Gmm^n#zrc~czv1pT=QdQed3mHMUL3-DPQ_B-`2(ZB$ab4fXcD5DhgHKTCgKo^^MMnRg|9_UBuNsaYa(92jBMU+I?!i5xsMlr+n$ld}pUP;jfz!N7p%V8RhG~`RW?Vk7<9hQmtnzv!F0l@nwBV-{HHhQmr>fMyyBQ_~8oOuk>ZT$^01KX!4Drqqow1j^CK*$+xELNutkvmy2@dT;3<@+gU)Lx2>w6`^j@qy;);gQ8~JAd#M|hV{4mEzAe9A)c=^9ds995#!Iaz-`QeNIn`fvY$;vebNlwBdho6BnR}@|Tl6B|UXw$<`P>f5*L}zM6y$d&-wG`}%73>%_bu|>ePhBw%C|LNUZ(aF$FlDEsUCd$``_iO`Ldtr`L2G2e53i&GPnM-tRv;?zVp3Jl<)LjK)yZuLuyyEW_cOiN0U!W)pm3)sme`Nd~5j2ySZ;Ji^!wT@79&5?PZU8fbw<UvGlWCs<*qPC2s8%Rd+nqgKsTeLix5^R<YV%#$5lLR1dy6KQ@Qz;ntF3xAux`Px-oU%>N4c3yanEa?bk_{sK4Oifm2gSPc_|zfj!2^>$diC*K~nFM-Ordc9B`r;hUn#5jR3$Eoz4SL(<&(t}0*g^O;!Bm6+7C*N9lI$8CtE4d;+W0M%yby=06Za&8Q`4w*YuK5$b{YsYm^<ND<8LIe>@S~ZYeAj)!H?L&kd!tbgNmRb{t;iw!Ro`~$i9)w}o+`da_Z`!o&!W#SK7?`x>{svCtaB8o_vN_Qzl!=*-t>HR+*v25(s<B)N6p4EHD8W9J>NA>k?+iXC0`wP=E;eaulrU_H03*TCkuc5Rw~D=UQPK{ZfL%G{pRIpx_<M=MS0?T6GeV)C6!}j`{$|S*HJ!O^mq7j{5mS*O6fW?Cee5`b4pH7xi5x&o9e;0N4)txjo*w>x$3w!OS5U*-shLMrt-~<fw}6qc9bNFc|r4y@`e&>$FvWQyWQ8Rk>ynXDYJ6a@op8oM&nKQ9Yx<1(|sM8oTH9+t6-v-FLb|XJ>@%&Ovq8kyIC-n@^#-TT1WXtV)YMd{TSv{N2&+k4ExDJ<?r;)a_i5>I*ak3`x&p&^Vi(aFHLPn<Ck{SpN$P2h5tqgjR*5qWewd=^tGdI<MH?4TB^5o|8%I=<Fs#}>(hN(L_juu|Jt`5>is%uwuye_7n?%g8+A*J>)UlT^!dXd3qLciKwQr$x*nH5_XX;=)-5Ob&Tfl@pFU8`1GleIIreU$<lEE3#CW|uh}Lb=w-(+^R(-46ljJ)xwut;&Td5rBTakhI-p%A2oq8T|8+R95i+P~qZ-?FL^UfA3-|Top`0LZfc(3bD>o9wV+QV-3eD^NZv%SM!;mdjBVxKD2cg+v*W7-`%q_(?JaGl!0;Zt{zz9+xs3HrOAAEWh+-6!XuI=-wkQ!1!@pS=gwab%tuNxrT5pAJx7^;$75s^i2u!@KPPxA9W5Up)7{n;uZdg`;MN@V%OfdN2El#&gVw`p;86`1Wa!e@XR!Yb>qvth{`2op<6yd%-u>j*e4(`>hfC#C@eAKSI<ed}D1;oa#FpdI*2|yPN6nE*FXQcS9@kZN-m?=kS$MQU481#JV&5m}sv%iDLgyf0owQR(L%5*4;}~zN5ZKth<j#i0f&*fqdax<NlnW`eyx)<i{MJjQm~V`s*{rdVk#T1l4!mSS!}cC0~i_JnN+PmA<ohwwQO$-4X40<2~~2B`Zb#xijQDuD_h9*1vOl?;WWgd~-?IPRhR~*4M7_zPR={wb$jbdqqF_T&$y<qsm3SK104ylPu=RQxj+&c3v8?SM4X}sW34=Uk)VStT`t7Pi=@;Xa9VY?%&L66!Syl*;>`NW{UQdzIo;{`9{_?F+VgO67_lJg79aGc9y;^epswqKO9{o_63@6n{+yn>fvv1#kkc^`1SpCUyYG5p=vqdm&v#F3yBT&RKDiR@?$oi7wf*PE8_a^o~?EB<@LjNZf+pon%PbGcMgg1vgHo>W|mQ?`nK3$+E3h9&pU>ZueXaC`!xA_J6f@0$k*H5zN;(UhwFK<sEYcDGk$8KdcU&2>Avi5M#2Z=>;2YD_(If^*8ioi_y3rrqqLv1j!zQv>fIZ)ZvMDu5>($xsu26maeol~OU^S%)nZ?Ge3sk1WZ!p5l!JM|(U>U8*>{J0Id52vmqh*VYf1ZWeV#G)cNhD9ZC<kWKS92km*O@*NZ<HkXq>x0hI}ipK;-{EL-Ysu#@etr)wid3C9C!Cnx8da&d)|#L$ca`tm+M7U7F^9K<z(P&39s5n%3ul=qK_yk|6ez#|DdY7uRznQ9LiQvk#KGo?lN=`#Q2q$ak&x&O9yJH~Z2-Q9oEWo|z>4+=@f=y{_lu6|tTw%souMyPnJbRL?Pm7390t^B4Waa~8g9-45R>tQPrrj$4ge#C%fptH{TCz|nYD)bojvN644!`HL;79A~M2inz`iu`c?3uy~G?_95SvKD<En?PZh5H!>5%x~1V8v3`^O+-JnPr6GoVt85PWa=&KXJ}uTc@MXSv`;_p@SCen1KaF+KRVpW@B17ay`HFSHtqbJau6;!7Q`h>oW(&2Wb?s~N^>w4}%XOpkrje%Bn{_)_jF;b<rMcDf?JBVzs~;iqvA#8b@e%vA2fee@c9-kq`+TgE?Y^}?sMjOc;kqx^;ili19JT+Og&&K3gx`c5wI1a9U-#wu-}IZD<2GKfzqrrG{=)7zjeJM-7U37J6Z41PtQ>V5$$gFP%YBVKpbwpk82Q)4d{}y(_EV04!MW=AlKU*(m-{TU_o!UAaff}}eLnVa_TH0n-RcwjMBSJBM60iVp4z^0A1Zx)A8H0o7Ux*n{?``tO1|5;!#-N~<vuzlXgc}&zFzm`K3)3yzFzlbzWMctLbra1a|zv-=Ms*MS>ilZJNJ;je(qsy%tgL-ZsYQ`a~t^jxs9=@PMlk7=Sb4m&yl3BpCj2fT^Hx#+WD348y6etI;F3lYsGy3La|%D;oMC3<++);ePOZNxWoCI?#uH!Yx|O7b==8wKi!w-e)jDj6szM)o-69UJXeg_RaW9Qj^w$e=F4+SBfhRg9Y^w9RQKh%sI_}lsXAWdxvTW`b5}EIX_?yp<$15}%ky4)(z|7D{U7Jax-ZX@rLUhq>%Qy!Ik|he+Ai`uT=(U9xRKneTx}P5-md%dyxo>Ouv~2yd7iKPuJinqV-;$<$oB=h?|NU5QdOb0i+mrU`|^E+^XU3YwY}tf5Z#yWL2PN;D%J5T->2xleE%YS{r!vXyWZENovc*HqwBqo<~x4qP^9MH_nt`eWxg$QXO&xj!}}@Sm+z;{%)~0Ueuej6x-Z{<Nnd|oru#DAR`OP@TfO0ZpYFTf_rcfS59+=vzf`Qp_4k{)FW*;6Uw^-;`;<T4?d|XCz&q`(vR`?$G&&eF!<ARRSCJ>x^Q+%EL;qi|eust(|94;gc4pV`fWa?R1m~vE=HRB_CeRMxCg6vl&w#l;4({h=7>}{&gWwzj9S#lw4}m@k9s=&o;<h2w3%@@KHdq{I(qIV92gkEm#bQ77L-1Zc#8_-$v4O?kSu9~O6B^0lZ!8wF_!JrmjzrF<(7%JZ{x|qjZ~}A-cniLla{-HF7CF!aZ~}625S+_!-TAnueB5U|v<zH^{CMbIFxSoCc<?Id2Ji;l&nl%ZRzcqauL6GvT>$<gi;*n;gy1|5F%tE+5F80L!I9vZ&`|J9@LPybd>_}Rz%2}FdZRspvp3WLdxM)n+ku;beW8zmxjqdJU<D0k(HFsa7<3SL7<eeO7kDW65f*n1p|_yDz`-mAvgn53?8l-f3;th)^nm(-dw>T+2Z9HKUqx_!85#_J89bTABxrwVFt|Us3$z=!3%DzS^TSX-uph3K^8gluSWJPw0-geX2f7^m4)`<ZKfs@XcS64d?*yko9pE(ZIq1*ebKnQPL~w4&^kEj=Sok40w?c4kf#BQ)!MQ8+VQ^RQ1JIV>2f(NBef)b*AvmW%9pDu3x6tpv--5q{{sa6a_&w-y@O$8C&{x3Iz(b&ez(c@25rfc{gV2`U5d+Y^U7<lrdj}ynzXY8EehIt``VM#*cn$P3@EY(g=uYr1@G)o__!#&+^c?s+xV4v1-uA5#oO>cTcZaqF%l^?F>Id!#?E&=z_W=7qTY-JRzZfDopM|yn^WgjwQ>P)cIezDUbL4gb^ZI|#5aW_-E92fc<=h|I%eXhLIZr}xe$Ei{99LgxFR(AT8MKvgZ_ecG4Sf*I>m(TU%C)^x&zyNXaJ{ay%XPFH?*mKGN4P$(^qJ?;r?>_veJsGZHx~sc*TJ<tGyoiczn9Ml&W|EEKZW4D0J;>s0Q@0>^GDES;AQBqA0db9egx+v=o;`E^y4JtaLq?>&V=p)??OFgLa&4Kp$*XM;0AC2>YLYl0HQsfUG33MoPAjYDSbFd85coHUND|-!SDwmg77>GLRq~KzIev*;C#&x{hzB3e)q-r@Wpp?E@6Hpi<1b>H=(uQn_zD*5u7iv$YSw7EPjMu1^);xhh74ggHJ$f!6(4!&`NMRcssNNydAs|!8r!OITm^n91A{-;9Lj239bV-^%BbOvnhgeXBGol^k>l#!TBMmKlmYVTWDu+XOz<x%I}|ZIMZiY%tmmY&f;}w2=rNSC#XO4S+GBNI5ZqQ9Q+~+3;G2#9Q+0NYv^q7*WiC5IIo3H2d@SHMY-<3AUMxq@ivPn7E=+N$Fmp(9RrO5bDaSm1AYNI2RsMmzkuKz2n_+t`U-@$1qXurLR*8m_5s^jgt3^2;5-aE6g&)UgZ2a4z#Un%fj$E52mUj3G_)UhG<X7ZD0l++HE0<4HSilyJNOOoEEZouKZn}EpM&3rP6WRXwh)|OgboA02p$f#8Ta}dXMbo%<6i&lh<1?m(h1Q<X$P)8&^BNnaBt`%U|ElxFR*CB##5Ccg7dG?PGBCKo58bzn}ORv1Ho;;?O1ex4uA%N2Y?460x=&1qOAT18|DKWzS|$s33CJ2Cg9HCrci!waxUV`=c>cdL(mK0L*O0ID)0{QCIshV=&#^na0QgtO9g)CTmx+b=E3<Qv>liS=PSm&y5r3Ch9P(?i^VMd1NtU-ABzkY2cdc3|75WOxhs&r82R$^gZPZ|Wft`)qaNjC;B%h$33NAjC5t^QK7bwof6QVLi)a>GStPQ^Mij9qWl;$I9l`kyv<Q3$+=wW`b=8CAedghs^5E}=W`nbF4ZES=fOmsGfkuO)as8j5etEq;iQqgRx&picx$~imz+5B1PeMmPBfulTPartY19SZYg7aL|?_AXVT=*-Y5#R`X_e$u;V6N-IE5Uo9TftjVUwfdXVA*DS5QS*(1K?cf?_jRKfseA_XOMBw@4<24)zEd|)!@G(IKPYF{9g#p+o0crw}Fp9Q^7~T)d<d~p+~`|!Dm>EALZ4gL(~83f0eoSV|np^tN-JS{+I5@tm<Djva(!<uH#2}^D|4M3Hyg1MD^oOV&i`SL6JR8'

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
