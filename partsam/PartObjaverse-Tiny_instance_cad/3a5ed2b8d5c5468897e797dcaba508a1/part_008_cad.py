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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3a5ed2b8d5c5468897e797dcaba508a1/part_008.stl', 'relative_path': '3a5ed2b8d5c5468897e797dcaba508a1/part_008.stl', 'source_sha256': 'c3e7352a374b83e0477cb5d5f6a99891fb537b2923a78c5cb57ec0bf6ef3916b', 'input_faces': 438, 'input_vertices': 261, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.26898568868637085, -0.41145843267440796, -0.2822171449661255], [0.24722231924533844, -0.18449532985687256, 0.2703901529312134]]}
GEOMETRY_BASE85 = 'c$}r03!F{W9>=#KR|t7lq+QAgDUYN<&aEU(UR^4$95F=l7$V8FO9~NEL>{L%qvkTDOL`o}bA}m@LKH{2N-ybUdf=|L_jjFH=RfCuKKFC)d_Mor@3+5uJ^pL$wI6F{x~7*dQ{4%EE_LQSxw3W91&*VmqEp=&n~^zY$bgK|O@@ygU&^WCbNyp<Zs#7Iy7nyPjCCfY4$K%mATu@1O>Hx%Rcd25b<l{+F`4~`_ZyKpFhlcO`VSkOq4?<g`j5;|#|@gbY}(juer02KqWeGolvgQ4D_^(kL#6H=wLa47ja%a%8y@Z!@aU>vceb;5XkV?M+`d^`?DEmQ0gt6u+-#SR{7^G!FYDMQyS!(3r{=4Yai`DmHxlxJ$8v64)-DN;_TKxZ&0WJ6ZrJGa`Nwzq{FaUWxSU%3gY$5&eZak;OLp4jy>UbK_`1LHZo7PJEWB#xT?y?^{v>g{aK~^nUcqC%8Lw&ov4A^oF<!yr<Ap~J7vl}(Zw#(O%_E!b_M>_5>3uiZ<s*L%3Gx~g+G>|~;qH0sHYbetp6)x7ju-C9@xt9cV!V9=9?cQsg?n<mro0(%pDjWA3#RPz)vLGm!z4U(Rn^tWxO321W%Jlob@%#tigpYSi+1AWX~(^GT9Eg|iGKT$mK)Y2<IxW?63U0+-tvyw?JOS3&P*6r2`>6|;Ne<NzG=4;xu9vnxFnbDgyA94PPk)zpGU>G43CL%x$uw~*V~T=`G30FzwbgOAHhB5xkP#L46X0PeQ_e8of2G>kHQ_sWw=|T(C0D6CAsrqMnXG|;f%}qIX#%qufN;xw=*foM{<{Ol_-B8$TQrfcF=GBp8fXvk=(2w!(({?H|xjnaNoD~+v`Vi*>4CQVSb{^yh6X->7D%NUfA3hf=A4KA-I|U$fDbP9(to!a2>Ahur4Xj?UiG57am(&X=YMhRQtJh7I)y0w7gZxc<i-z-nDsjMkr}MaW3+Sz?~(D`4}$q@!&Ea!%aSpb3@S1mWLANS#syPU_BV_!Cls;<YxX255uE1gX>#@FALU>_k62h9(wdRV6SJ%&3cwR%DReNe!9TV<7~r(b|m*$=aNTQ=aS3zUDH16R`MwKMeNznwk69)a+8nbCLhU7K8DMDB$xTf`(5&==vUtFhRge1@|eg|-tUIX_m|`{ANl@@w=dpbCHTR_eB^sda#>!!r{Y|^rzDSw{N;NpKF{L)Qi6+o<ohMwzIeY#Zr(43%lAus9>nuOa`SwMUoY`|kX+_3pARLtc|N2+vdzBV<Ie}d<Ie}d&HZAyd~ZrF+mY{0!{v9N<RQ_H{0=l+eg{e(7VXIIK*QyCj^v(bM}FrRF5kbBM?^a%-oFjc^}p-oKFDyn4~lcK4>DZtgW~OreURaDA0)Zi2gTbL`yk29KFDyn4>DZtgW~1IKFDyn4~maV?1SQ5?1SRt68j*@%|0kTF0l`i+>_%K`=ChLaDQJe_w|O$eZApwUvIeF*BdVP^@huRz2s(JAJ0eZ>m`q0Uo$SbufMate?8^*WC_mqo8j_%vIOV*&2afWDY^N6i}R23^L;MziF1)p?4y8tOB3^n!d;P1#FQ8Lc<?CsxL-BN^Yy0*d44;2S-CcM;Gx2i{`z-b?&$OAsbF0>iw18<#@$J`Z?t)2wHwUC3yI|ocSQN<xmo$i${QXp->YZP&bPV2JT#c;bMMjdKKBZXg8K;`Ewwgj{*s&g4VU>#?uha-f5}aGx6WRlhgLQV-g})Y<R;^xl*+;VRrjRN!#hs<?S#8roSTeCozubZZHA}i+t=4SnYO{^=K4nNIUKZ~IXK|uzT0lkXRJbw&qIgG2lL4~k=$jSxcx5KZeN#BwK^MY?!le5XZ(KM<yUUEuUD8nCHKhF{Vj95ou`=x$;~{3Z#}*}*>#uPTzA9eb(h>+$I!g5eeU+|wZopbIA@-nX!d%WoB4NV-@he+Kec#^y>7kc_wKOgImCD+k1$?u@(Q1OtOs-54L9q=Tz7BB>K*oabGcrU$JzwfE9%xONLVMV2g%KIBRX<eLBjfBT#+#g3X-i)!{z#PDjhAb*Mpe{$;~{3wwx}o*I|tNOY$)Hmow|a!er}2^7!)&UgG&CxFgD!c)kf9e?F|}U1(n~v#uh$CluP(#muMk{nX_73m(rOULt?N9Z|kS{({Hz|KpWH`})S;FYtu-OV@<In#^7L^n2xMsFkGRT&KD-sK50m6Ak@kh9>`$$&eQR)t^jSG;j6){>h|FDaZLk<xyIx_FDf`$H!Ittl|e1M>#fL>o+QPtN294M|%D^HeTya6}wbyQK9E*568x9EmZN9iv23SP;r7|<F$V61i9(Fex!eWZ2XVpa}+&D|3@u<kbI)(R{D=xek=LxK@ZUX9?KsfpA+aw=I(^$wVGVDey`$7j*Zv)FY@{ZwvS`uzog7oa@K4w$HwoY%mH%N>=?(!@1@L1ay~}?CoO-BGJnFqr|bdF71Hlsaydxf-!Lwn>rc#!o`e0&+ZSB_D0BP?*F|5GpSg}dQ1>h9>$<zBuj}rnzOH+m`nv8P)c;)Rrz*a60{=0`+JDBeF8>{MKF8~GM^qeE5kn8*cc|E;q5$2D-=JcniuHu{xs=JJTrS+y*-m>}^YQr{$Iv5qtwngPr|>CioTXI!?gaXq6L_7&HuBnl&m*=mrfrPNjPDoxVf?Rz_Gi%3_|1%^fY?aB8|iO5nup(xKY|{%=J;3q5quGP2CvmA75F0j?`R7C47q8h^(<b;S?1|1bELhQ>rF&H*JnMt4b8`I!yiIpPVt&Jg+GKh^YjaO`~p8qoFWgczgfPB<07u1_V26cqT&OzE54(Of2z0*U4!q6et@pA>UQLON2~1n)bE0J#IIG6uHs$vc6@skZ>hKieH(u}`Y!smRkuCo+goMVQa>GSk6)*vlZyAy&iD>0R;#!beFxteeGh%ds@s9{9jvnJsNV_gfS;%04Ha4V2*>($td~(~d<BkQQc+9A^XPf_8q}?T&cn~6?FvK|?VN``k7nUZbFLQNl&!&WgeXm(FQK*2(pG+1oX@h#=BQYrVimd=Urt3;M}MFMS`GiYiaIKmp%>$;Qnwnq1iyqnsu4M~b1}LM&9T}n$N6$r*{U2bCd!fL>u4P-Z<AjR=X0#G*(w&QcoSWKFQcN8igVD)_?K1a|6X|oy%1lCx|Pv|_=WUQnaHM{3(;55Y^%*OoG)XQt;F#Hq6~Syj9y^nZSu?Je703~rHVx={(-)LFRP-8ioc-e<6l*Ak&4&Q+W0EeJs(|!Uqm106Dw(_Hu@U6(rU9T=gV4Ut8n}RQI<SkMK7}QHu<gO{7S2={?Y&ElY&;qr{GthOYtl4%hBiX%kd6c9$!<%i;n(xr$Fc9m(uQYXnFj6+Ny{;R^1hxU%|Qg<oP1~q;T#<tM7{V6pmY}Xs+T8v>U#+ie4((pzZK&@Ry^h`2N%xgtoyC!Vg0)#}C7gL9fD(!9R?)#6OJxJ9-CR_Zz0qFuC@oZbQm8WNfDXMB39j&T4-g{c9a%<ui(W!}K=<9fTi(AAt_T52Nk~^6f_d-RS%8j6IcnQ^{5PG!=DKTu&Q1r&)yd&!7|W&){!FyWwxdUxPNsUxU9CZHT`VUl&cq*Tr9tw!>eKzYFb!zY9MZ4dW-{pFoG;pTJK;N8qR7XP~3-qnHcryQ^rS;&146_>hXeD%zrb@C`V31=<#WuZqEx>w|BLK7enFzXE*_e+9k?IsxAVZ*tN)37vq~xecJt0p!t#u{5G=Bib_cbzP6p{vq^1{6qLm+8j!|_u>bmBk_ar51^U&Oxk&XzPi(Ycg8b`+!~Ny1Li{enJQ+hc$(0Dj*4f|x#(>CGw3XIwo|<3wV#2`#LvJ_L#I2%YexGg&?lYZHKx5;huS|*Xg`I}ekwX0KNbHJIuk#Wv1zaGoy(l!`%C+#g!awQdU$<LUE&nqcb9PfGJHMM#q08Eur#>wtvS~B-Q7;{y?Hn1)9|g)o_PIyxXCGghTO#5&&5BB-i)8je3^UvaoW2Z-xHmJH`m*&N$oxKW~X=!Yu_DhhVPDVf!4#fz&Ao&d?S1Vv^Bl~K7{tfhwy#TDfqtl0q9ix0Q^w&Dg03UNc3s^NPH$b2S10o&|a^TrcUv*x+(L06aHqj8NQW@YgOEd_Q3a3agT}{(7)nuz}H8w#Ai_FKJ*6sefZ&Mef)6zSoCWASo|YsEBqt)$Iv_Ry5E8HIgniYQMWN=8#6Xj|54i0I^Jr3JpF4OZRInXd<W9s{VKYqmrAK#`ak{adGU{@H%JNph%Rd;{`%Ff*;0LY$A1~yHT@j@t*Jh=Qv8?Ic>P3l{tX(_dOi'

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
