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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7ce14aa504e4bbfa7122c444150999f/part_010.stl', 'relative_path': 'b7ce14aa504e4bbfa7122c444150999f/part_010.stl', 'source_sha256': '4b94c258da1475ba2c12e343597c0841a2c8b24ef8c2c49fc6ea892bafe4049e', 'input_faces': 380, 'input_vertices': 267, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11437831819057465, -0.13510477542877197, -0.1279231756925583], [0.08102419972419739, -0.13231754302978516, 0.04146505892276764]]}
GEOMETRY_BASE85 = 'c$}qL33L_35}l9)LJ|`8O@RTU0m8oT3`jy^fJ78o120IB_}PQFATWpsDvAgQD#!y2o3bV#7?KQ&5tKy~1qAd7f{G%N4~Pi(ySr`=Qye|#pZ_1HPTzZ{yQ;dnXQtl^smZ}16%G2-HV(8)e|T0k!;ltfR5T`LjGvJCXhv3}(PN(uGRi7lesnvpSD&7#{ez5&#-!L`8Cj2xk8Nkhb{O6!wt*Qte9ZU><I_hE88d!ZhSU?%M`mRRJ!?ez*bKqzHfz<of!VxX19P(ZKYqeR3eMT?`Gumj|E#l9wU;tibQZ0DP*<g!NpVUyGKVSM7+O>5R@u8rkMBkL@v6*^)&nUONdKt{=`l-|E4`?U(w!qU|5o=WS7UJl9mAAvv^JUUdpeZznOT|g&%L7jIJqU5|2uV^kNw9E@*j6|2kQ^r{N}RK{ktkq+~W~SxB6UEy0N}G)6EaRQMx&*3+cZU`=xGQIiYmBUn2Q`;+oQp)n8ED)tyLBsJ~40Kl2&+pC3<tK5NW$*Z<bT<fqm_=HKXal<7u<g*<;yx^KXzO1G{iP~4#xnC?3oN&Vw~Q+2Zsf5htmJrKE@`X_WGKh0~YJbj4{&8um*ztzp}+p~E&)AK3+LtRPl*OKXO{ws<o&%zIReeTe8J#`%d*FRwW?T=3?-D<Uk=2fdL>6=GV+;N-vx<I$qZD9G^i=wFikMHw!sZ){Zfobhn9jutOynlWS^&hf|)l<*QeEVHiAG^VRrTf2HM*Z_!lU`*I`7ghe$Gv%z`uAMS>p3%6_4m(vkk>!-*1O8jp<Yyn50glrd`;>8@E*LLdt$Oxo(V~$*GQ)R9cn4vsMDOqwf|kL{Mczt_&Pp*LFs`-4f*|2uVS`Wck7l@jp=UPTI^STd`If@x~(lzx>2?+k9+zDrn~zG`S_CW<#p3>U#P?HBjjoAs>Smk(vs;qfBVOFN_T!P$JeXQP8HXTjplLR%u~8EG?MSbey3@@-YL!NbLb?k*YT3<el)6<&i3kV-IhhsI#vqdbvW9X@=Oilb?a51>37D}x;roAY0kct=gr^E=i@)~*m}JhtaN+D**xz)H@Y9C_4@X7o;QCx|1j;V>VZ7(eXaL%pwFp1HZSaFqcCZ6XV1LMd7Yd>kFNU%`gS2bF-7UxztcQU>AuL`O4sXd?(fNTcikJMFkSoi9j>QzdqH37kNWt++bTWKe*pQ{_vz}^OxJbL`TJ|8k$<ea*|ek5omE3=zSvhzW)G&jbske!>E_4`rR#m}luBm0JFnMLnXdD3B4cS@O-8W#=sNhfk79nTGcA~|_m4lm71e*rSjt~NXC52Ob*!Ur-w>v2|Gts!xQ;qI2isFUKYfb%G44-fy1QQ4NlLd~o5cF-db+xP?&)=}HjT|oudj1zI{C-**1vop({DeY)0pl)AM}10{vxZtKafEA#LZ@Y{8Qp7pN<PDpBF<Y&kIR(ehPYv);;Gct?RIEO7|UG#rj(lQ|P?7WG(Y=&$z;L?MM5!)7SBR;uJI8e&;6bgZOYd=iRrF=DYVI&1Xjlofpq<W_9xg?Pt2KkM(<n0<Z2qmztGRy0Kvk%irp_FW;*N-j2q5|5tiGW^JQ+eH29XkN%0CgKhHIez3C6Q$26w^L>K(y1L#c=f7vV-f#XJ7n!c>V;_vB`s{RAeRSRYGj_B69~c#-=4(Ar#B{^1#&vyPtchT{u7g#Z&c{yFK6XFaPZi}e9rF$3>}I;V|MMyrcy(P*x6TU>^5=%G4|MnaRouFO>3EJ=4O=SR9CVmH$8<fluIu33ds^uM^9aAc+FYPIpZ$vR@s+1}ZSP9YleNd$^H$eQ>v~`5`D)$G|7;l31Leah|GT@<eLDIiTNk}=?ccv+`@|m6OzDBV?^)gSKGeGV++P0!)7|s%yNxNI`1AaEh&+9zFYx_2Fqrab7@VX0;QNApADP9WN;jW~V7jxng3<#qmDqgES1MEgTV*M3a(Slf?<sfo_iqd%eO(2*55BIcbp5^0vIcM+>!{y%T6gz3`umpFX8G&)wK1_VpYOGX)W2ObmZv?SG2O2{I<o$D$`N|bl(SfWqv#;rzh8D$y8eC|=su15zZK8tHGK;0=YoMs*WZhEo`L5ED_wtYwU%$o_v-$(QLMk!J)On%cg?1JB8D;l*7l`L*Yon9+Cul~{7hD7E92Wj6{r8m9JbH3e)(Cp?#|DnlpfeNm94MVeRE#n^?$ZV>E^?)(R}sq25|-XUftb?=x<k@M|t9R4Bw|~sXiwc(0uW`hf{Jj)AjEazTtUH*YmZ{%~k&W%NDV?TDNmnu>Bvf_Ay=W2d!H{@3Z+@@6BhrdtZ!MsC4I}^=uvW^UZu|6Wc$=l9RMvy>cl}{QhIroI}sO3Lmig*!^ddzIX@oW4FIRaeamCKGM3?`T*(r{D6IE+&IMcm9c9Qt*`Sr+n;yp`dksHnnUM@q+`s#ejf$OoM8Q(iw^DEQNPkYx#OH*HM>N9?l>oyc~@z^c%GXNT+8?B?)Q<-7QK(A{=s#ei(FlQe@Fj7*k4qCeI9;2hVnTOl<U>q_ce4k&jYpToHI9s`s?pm=&yBseh8eNOXs>rN-5oaUw?j+@~j@tbT@zK?)RhFi3NYBn^AvqKRBQ0{bPR{nd_~;dk%!I-$&Noc&g8eXqLZz{#YZ*Q(T+_?FvVk?w+6Ts!#8=hLxzl{+$YS)4F?()z4?>Zaw?Pvi^Er=9R@%&r4Nuz3c9T)hh7ndVl(R8Z>Te^<3}$qM!5jGc}a%o?G;LR_oZ$#>OC8&rT-gufK<){#w^{)_%0^-j92V3%$BNkLmY|9efYlhkE}Td+%lY#H|l>_kD`ziPqixU%W#1_3XOjM}NP=bIH~9x%${~rtAHt?-%32IF`S=-zqg?_0i`U^Xn%3{(|l#r||uTbA?&9H(PgSTxGicW?x><8p{g2x_jU4jHG!F9>Dq=lXGdG)JbFY(SEe<eh-R?qWI^A@c!F2(fW?bVD)#d-$nOdixI3oW?Bt8x8#pv{e97uNKeRO{q=mE(6`vUoI{IfzMm}S`r~Uze`q<c+dt?=#2d7ZIa^phTK7G<jn8Z4N?Nb>c`Q$(`#ic|i~_EoUQtk(%KnOTs_NzrspSnrT4|%AF+AP#Cmbotk8c0|PdJ$^{;NOXG;h=7|NRrr5s}09avH+U3p*j~0`PJ0uY~<1>?rUL;BwqmVgCj`4=%6&D(nhy0Q_@d2ZVhJ{1v#2vtQUD;3MEy;QK1@ui!G*W5P}Xe+zyHz7GKJ2megiVPRhY9|V{4{7zUg@Ck4^&r8C-0saa67-Ahndl>jL_&$mDG;lG-UI4xXUW_=G(0&7a0{A=Nqu>YO@0cf^<e@=^@uz5S0f&Ig_7CGW4hFwrP+JmQ>Js0A77Ba=JX}~9^f36BxHQI<LK_Smf_}khO96)ihXI!c*S^AmOM-tQ;-3+=5A7*n*?#1~UxM#N`!(7xfj>ce26!*{MQE3SPl3y8=Y;(N{3ZBB;8Vcoz%P5QU&gp|z-Pd<Ux|AN>n-d-;AHR-!UhQ&2%G_)DeO^U!+;+LA0VukuzqM$fFFjB-oQh^r7s`i%Jw1PKJeWScqn)}Vmu1m7rY0?rl9Qu+!u4{1^h7h5ac`pI30W_=9mfW1Mh_xDZt6#GS^gLJ%M|JXTta6z!~6=c;+o}e{ea^$Ak?A9tJMwnI>$wr@m>3(HrA?!$*Jk?Frw5kW)|i9RS~h;bQ<|q(OTOancZfIJ9AiJsdH5B7T3wk^BQ;tA*_XUI)HP*!#kEqTLECudhTOiPwX##h7g1_rc|L2Yn>o1}@)ox#*vZG1-Vyh*(>3tq|jOVeB^Kx(l`%{dL|NuLNHS->Wb_8=B4|8|^NPEyOj+#|WDuY!uqbz_R_92af}nHeT3B;Bnw%&`tp!3H}_k7l0>&%WF>xdkT0Q_;bLMfu96_!E^lujC&Hko`R<RO1?<g9AU2mF9f%RO%OH%?GwObg*`2767Xp7`NCcnHWPRO_^a?W2Y4#D^fe7}W&0ZNZ1{c|_*w90;QMLdm%tZc>;km2fnUO0<^#V9J{37n0DcDiS<G=P@HFuGh_L{8A-K$Sp0GE7=YWrfj|pg>0DjRkZ;5At%Xv-|_B`+;@GQ)AI@+1Q^AKy6XPsuj=M3aC13A3`pU-3b^YAefF{VS)@unkw7PLu-orSow;8Vwwc!#i$h3x?@051}jFKjp3JYac!Gx|vUA^0X?+c9oC#uVY2?6VQ=7T_F=*#Nv9JP+D#;2iLc7`q4U4&Xh=Ww$5q-H2NRP3Ncc*$BQ7zBgga2KdwQB>qv@HDPDb{thhLpFQ|GxU`$XegnP^{v+CJz`ubT;!N`w^uOTi8m<M2YbAmRUkCpk{jQ^x+I9E|f-eK(B$vJ<HiB;Zm3)b4-xIdXAp9=)3SmoytpR=;TwZ?%eI#BEzF3$a{rwoT2G?YtxoF=4eiLI}0rrEx4Q(m#o8WUXb{X0w!0(~2#%sXe0e;Vu-x~N?3~eraFUFWx;77-kxQnm^Ve!CS!8-`+ChUIT_TbHhH4)YrxCMAqVQqyqL)#9xGkhcfcLJBbIwG!YE#TJh-3+)DcuT}+0^A1NLaZ*pt-;%(Pgk^^fjc4R4!|wJTVamPfjfe?g>UV%E4a+{0bxnN3E<7)y9IE2@a~>@OPmNU=NTugA#h`GInPGI8hGm42yqe-D*-+d;Wr7syCJ6}_-zW`4dJ6HVl;vlhd7N8zX7zyh}{4&k`Ol$aU_?Y62d~zh5?5f@{7N^9aS3)EU#BaABiKus|YKDab++j6xYMiN8*y;r7$J}xD0p@Vnv`W1ssmC2HFz9AsC}^D0pSy5Kn%g@KXg^IDG545%8nq$xm5fcL}QwTn@axuoz+Y0@nk-Pgo6McLT?QR}dC0tUTH%VCkzG{K)nm;5vvI16&onB7Bzzt_fZXF=_x;0<Vf#Wq~V#SHfJPfvbVnM-H)QYXR599Pb0J10D_EQNZQEP2^h}?Onk4Ax124J@C4ix14Wka!`qi!T<DMif?~xwea5mV0`CD{xg<$WRdXY{-~9j9IEzK3Gq)JZXc9)jPV~Cnxj7'

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
