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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3a5ed2b8d5c5468897e797dcaba508a1/part_009.stl', 'relative_path': '3a5ed2b8d5c5468897e797dcaba508a1/part_009.stl', 'source_sha256': '6aca67bdeef12dc46883542e3cf2eeece2fc67eb69d2e273f995751c1699d1c4', 'input_faces': 350, 'input_vertices': 205, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.073580801486969, -0.23354202508926392, -0.2316509336233139], [0.2510182857513428, 0.10262134671211243, 0.19578179717063904]]}
GEOMETRY_BASE85 = 'c$}qL33OG}6@3XaC<IJ`D8plF!q`LzlR-W*NrD)R5J-T0h6J#NgoIF;<N=WxfdCOK-~&RK2?T@?hP(`9P8bwQ)ylV4s#H{#LdBM@zI)ETzwbX%S63U>U3=f1^Y=OT-1`PTM1<F=>#Oijdu7I$-~Tc9DMb<E3B^~L7neMD*0i{kp0ktYdnrDoiyw)bM~{6uVuF`4Pgxi+JuYQha=-vJAT+*TKzB7DJ~4T2@|4-JiOJLBgg$)A8!2(7o-%VvQk*#td@d-YyV|QucXhG)KmIfpH3Z+t86>d(Q@ip_Fis3E5$ODU&PmdPNA4DL$A*kjf$GU!te@KVo|tRKm&F40`lCJ&y4E{=ub3-KGs?(szz))t_*UC#{@t}Afi9ouGo&|Yc!WOZKdOR$UvQuGl(K__KkAi~Xa3Kuw~N|GaqH`slfJn_F6osQj}k`S<GevJtcMm+UcGPx=l#&<Ea^d$4-3>k8bW!soF%N+&8NJ2V1LT1Oxnfz$oHsD{XrP#y?vSWq$T@F|5C4_J~jP}bZutZ34w;!Bl1_CRr4tRUfMB%j%A-wKV9F9B3<iw=D0vL@E+xLRmO7sxv#0;>b4}(9X}*+d};^UH~qdh`RlziIX=6SPW$v}C9PLoZm{0{7Vq;9<GIeMAF_V4-2rP}<LalZZ|R>!>-@f&`sq|3vVQ;cDazYrDdly>G(AW9wE*hB<4PLEJFfO)eZk@#G;cng>T&GQp;u&6-hhKtkF(tg)>pqu`>ehnLiISee!}{ISyaE{awzp*ozd_-=?`yEpItxIsir>MNFZH1(vr_z%R-7*_RMEJC7t@IEli?#*Q15(vm$RF<yBjd?kr!)@n>()`B#GD=$yOyZDKuWJMFV^q65{h#~bXk?RpmZOdL$Q+WZ#l^@3>Mm9deu?~coLFVKAP9XeOa29^4z><%Vf`{zySgDYwoUl*IhIeyST`25fPiF`DDJ;!eu&-?zMeX&)S=S_`y$ot;t8tWUvsGsWjKX6|CYxbGfl=`XuHJtnKdAp0GPaj76Z`@tN`w|t#dgLbZah=bicqJ>IbjAB2ofG5wB<jDj&so;boX(_q<{7%rsMS|kZ*X`I)mJ_C68UubkoBMt>ZjuSG}W(s+#;XmbH1nRSE&f0`dz+(tiP5=ebfEhQs2}ZC+j{pGf98#Ci_g&S-*OV&aFE5D(~Zo^Q_;##@GAaMC!AV_$Sh})z#D=rTi}C)$9Mv@y{No>sK40QXkaoT@2D&seEpGrIN1I^kKcxRO*k~ErI%@FL{aeeX+D&E&naP@A*4f-;!{M^n?q1ebuD1zVp#(fzD)=&q>&E)<-m^eb>L~%j-H>Vp#WAdn1+iWqTFJuL-C7m}YF_`_(5OvHnvr-5-=k+xfm1_8I%Mze?-X7p>ub=KY1^<NWA4a^3VMT}y9JKzf3Fp4?#{qao|17ieA1=<a-<>C=n#ZV!%eA0qfZ{O0qdYgK*uKG`*r@7q6)=lE@9biF$Ut|HxaH;&_bB+`1F`A5h{9g@m=MJ%7&lCykH*6w1TZ=<RI&OSxl&vA!X-x*JR(1V?PKRI%i^)|Eke%N#n`+s%3ob-})ynka;iU-xAD}66}=#G=v4_my{U43egcg(we$*LP)?<uRzN9uMTsk?oq`&3YWI?tv$^+rPqYt!B9f^I}^;eEBmOI_BZ>>bMbx0Coja`9$CZMw`Wbyrjtuh$kYb(vR*o>0N(zKHiDa6RR9W-nm>JK>x+Y-fR0S0?7NKXhZwIno`Y`tWnNL6oQ7ql%wH&>d6nuzvrAYHNS&y4-iE8{d6gYTXy9>(JG*;4-VOq!pD~`zdv2&+fmd+x;ETrN7?x9>-Td;{LqSrl>aEP#)1aQEI#@={&gF@_tQhQef4U?O*V|Kv!>cCf)G+rpn`7*>v~0g04^VFY`E8&^73Cy~dE?>~qtovYsouF7ry=l`y2tdamrc%&RBQ;B_^;TV*|0uD52A?(|BpvYsocD{m&1S<jW$ek1FF(N)%SC3S7gfimm4(k7oHT|L#d%GzhCYnQ$#^XPMIyDIDXcRba)(5h?Dm4W{(A^l-;m33Wm-|f2GcSq<~>~reRp6A@AyU#gv*OevJ*8badyN~m4BdV?YXxHsNN?V_5YyaK;AD4Ud*<EMFQjdO0-LYtyM?c;1yZU+Ti`0$4A4{$K>(0A0uhe?3?7C*F-$+fXRo9_AZT(Tw+x?>MzTR!R;cQm!(a*#cCAIlT-R|Rn?)J&JL%JFhU2VNCwB?7Z331=h?hPok>hgY~PrgOxP<h6$rnYk~b^AFt)Q&YC*JH(@qS|!F<s^QtMLB9}yY8fJzwY#sSv9p?*HX7%*GBI(q(655vFYyn5A?_GKQ>*S2j`wc>|?us+I4vyN!@<`l)C-?sU50e-F82hy8V9c@V`y^W6wLA?!FH|f9!b&{jujA^v9le&>wr=*>t<V{dwmoeZ+ZjKXkp^q^LIC>D`RZr*YT!GX38EJ|K15`+$}aMY{ccL+bYT4fSx$W$Sg}zK*W1Wgpx7l3kbQLF)GRCA;o^p8h?PboGaY71rxW^EF7fzX#fNx$jc9zX#fN_j_Qr&lN)3d$L`Z=SS-H_hh>+_ua0`_gksk-;?dS-N)lSIl|*xzx<44<G=Dz6fqhpzDoQQ%U6Cv6h9Jc|H^Mx@Biv6zg{6h|L<3Rz04YVnqwev0C<0M^fN~fU^noAh<OP(6ubvw+5y{ucQD7Z=I9Rm6?kjpYYW~L^Pb=XfPKM54I%Ir*adt5Vuk_-fp<ep8{jkGLlF}O90A@2F}^?_@G!)T1P%xHMND&GQ}B_9c@g*mcyq+G1hxQw5i$LMA>c2e)|Y`{;G*VG)FN;&xTx6=wFqniJ_0erfevsV#54sq1|N=?7l6-$H$_Yf;1l34ASMJD4Bi4Ut$|O2w+8PD><r!&yf5%M@DO-*0d@rMi<m*cQ1F(>-4@syJRJ3jH8n(TQCA;)_Bq6e-;V+g1|J1J3>XR?iq8+jXNMri^Wee2-r&LD9f2x%M{qyXChDpOYz$rxygslAczy6EfqvkA@O%>e5;>j$`hf?UL;TA_d+=76`<tTyYHR=>$?ITV2i_`bZib#d4c-~O5q<3h><r!+F`eM!1urkGM{)&o1?!jG8*^{umb@<Jb>T00Bg`8iXEUs|6SP*SwG((C<^qRVco60SM_Kr<F&7wa;Q^Qn9Ae@AnERuzg0D5l4s$F99syqrJ{x!#d^UIj@OR(|;EON>Ut^BV=7=*#HgF7hHh3BE74S0f65w?367XXff-g76tN468Fb+H(d<$?h_*i`AbznUB>)`JKw}78A$8mF10n5SPMa(JSaSPv!`DUzB@U7;UX^sqhHp7xv@L9l_-~uDTUk8rG5d1Y@BzT26a?DYQ`YKV+De#lP9Pk{}bP_QqQP;cR8NjXJVt=P#{{>D3U#IZ7SqrXXen#Ola2Wi3%oo6G5%?6$7s6vP_&UtR*~^7bF1!R^4UaY83oxIJ+7<&Bg6r_w0iKJw$g>`rz&+q+QS%w_-I$9!Z=!C2vEU-leE7|W*E;0MgHIm3&Y<R1@LL711*q8xKPS8vqOM%jwg+ChsA)I+cEf8m^fl=D`_RPvJmSuR@5Nl?Pr-TwMuUs|saTJ|cfdvdi}1M!FTq#9YZZ73<`d!N1W(0WtYshk_Q5L;b*(~ed*QVTHATZG8eUH9K`i<g3vDX$&qb`j7;uq)9@Zmp1GvbakM#(=050;cgx^Ydr6B(#_)UUWD%O$(zbtrN#9A`pmkF;Gs3``1G4Ps*nl`|11HATO58grl-hs9UwO&A;3&<gOnmOJ!M<Or@e7rd(m}3qw8T_C*4w<6}SPZ`390%Zc0A7NRGe;EsqTnU?MssX}-zInoUSN(w_!YuyKWa*XUlP2=p{8W`CBthYdNmiHO9W2?t^`j5-w(_L-w$2@yZ~MRUIfesF9JUZ%mP0Mz7e<qd?WZA;5_g-;NyXlz{i7+1IB>IU~S`2LosSBM(+d{&w&Vqp9N!quVM&31{eV@a5T8US1f!Q<^rc%_%h4|F1PTbm<v2+;g>KMSOPAdpW+!`g&}w)hTs(#f|ug6rTBa)biu_lH5-1}(96*iamG$y2%Zky1fC8)1DFgx13Usa0XzbHG%yN$H25@N68JRmWx%(=mw_Jz9soZIehF9zehIu3SPWi_wUwe*0&{>Tz;nR20@J~_g3kob0G|mS35)>WWscM4c+VV5F_&E65@_4ZvC|yqFqd552Z$H3Z<yn^m`g5jGPuCsm_x%{a)EDw3)~KG&BC`M*Eyge))DUI?OW$R{nw~}|7i5$Z~c!__D_0#y<+|31Jld>WlKbOJ^K5CxA{k0=&i)xI+T9_7Qiiy'

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
