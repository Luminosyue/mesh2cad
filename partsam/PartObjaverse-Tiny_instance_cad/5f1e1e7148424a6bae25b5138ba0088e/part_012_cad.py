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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5f1e1e7148424a6bae25b5138ba0088e/part_012.stl', 'relative_path': '5f1e1e7148424a6bae25b5138ba0088e/part_012.stl', 'source_sha256': 'ccc8a67db37f9c3cfb099216e9850804094164524db9c89940a542863702ccf1', 'input_faces': 304, 'input_vertices': 195, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08674944937229156, -0.08196227252483368, -0.3065956234931946], [0.08528368175029755, 0.033516302704811096, 0.3139341473579407]]}
GEOMETRY_BASE85 = 'c$}r02~br>7KR%|jfjehF>di07laVExXW@i8jL8S1h=?66kJdi*#z8fK#fsRqoYv?@I(+16cJHlT&|g9;#4IQ1(R~jn7mA7F^krWmPwpUQq$e%??>O%Ox4s3RezoHzFuy3-*ftPzal!axwk)~zuxS}Uz<I=+L19KU*^xU64El3FHT4wn4Fs9#rz}}f6DHOik%ug$BSjLH39Jn>5J0>#yA2(mW&Drb_6U*Ny|u!OJ10g7M~#a^KmQF6F5&_7MGg9KMxo(dU&wo*}!1OI>-O`=fj6!j2M3AvamP%R|#u|-EEMcI}&$<8K;D`dgou4<rTvuw{r7pq&@7C^{p+$o#_#^vfkdFlAG6tQvDW#E2YhRBsrV5qF$Ddx^YrIZ?ku!v<7ii-?)%0xix?|dn>qFwu@dw{C=Y3?uEDIIL%p3>i;xxb7!{f-x@QQ#_vqD_0Iw~QvJ!qjfak7vi!no;*XY7{kDtceAzpHrhdwZ8{2$N%g-aLiMJxoHqARO%cqCX`h-T&c$VZGlD0psgEg~Iws)QzTq@g*qw!d89<Xt%gx0~G`C6T<m%nURxaep2;znUv_NF@9x?L@n_1S9T#;|jen^PlbUQ<y2<4z~!=hm0x_}Pw)RDbPWxz5JVyJbJ-5aQ0CQ69CH-fwBX{OmgSM>$?&_(j=|QB2%?Cymyvd=l{_;zs){>i=v<ink8=w(+w~F|-c9=FxmVnm}<CFp%ceqrGh%*exd4!N~tk#(^{F!C~1xj`}eRzqN7JzJ%gu={J%a-rwz$^^)klxIaph+>t~5TcOdif9sz~ln>sC2c(^X_;IeZaifafm(w+a;&SA@B+=ecyiWF`xHG&{k<MK|+^N;)Wx38Y$oKsGwOYL&Ykc=covVHnH(Hm}>hWpZsFLe%eNtR&i}Rl-&aJJ)J#o%%QT>&~RXnqMV`;ucMYXp4DxE|1<H3>Ftbp>G%_OegulajgA0wQ&%4=g5<+b@3ah2EB0?KPM>kV5!)*xDcvqug+_sZQI84q{kX??(59bymaoP|?78Q&z8$mbgr4`$VP8@J{oekO#{INzu*m!IQl{462F#@Y3Js{i$EIe%wdi$eKcFTXF}Bm0Wh#j_4s*bhI%K8Sso`OrShs)(z7*u0xZc{&dLU>`P9un+epuJ&OThkf|gb$TB$?&&h#))i5l%-<@xJ1FglY`-4kIh%J<k3(10Dmi|aInCCO)q5<hXGJ9OHfL7J`2LdO+1T2R##vcM``ZJo&)p|%+?bAhVQb}loRx!Kmi_<mvV5-M=8)0*b?){aTchW-Ihe+81eVgicD4I#Y3E&}@qnAYfrr91?p_o^_2;iDmh-&5kMi*u;%303MY7&!#GMBlDIe}H*d?ErOV4#qanZi-zh;lL)!4TSitW5B#jPu|=(s*k7ki1G3$DhgxYN~}>hEe+C~XeKr}Iy}Y~1Qk@ofBBEAz@amsleE32H|3y;VWH#YFjiWSz%2yB)D{Gl0hF{2)zocg#)tKAJ=GHOGHmrN4K_%^F(gm4A@jDqE2$^Kf!ygU*fg%tD>Jid<ECT(PmYX`J5_9@Dw&vs}vSS(_{Md^fLMwQ-g2inER-M`eBNpYE=|*tpt16*q4B9o6H|D8AO9a}|dkzW!*1p6|x)k<`zEgBAL7%}WPuTs>ED>x<ozd%kxz&^j1zy>dj)N5@xg%8RqTZQR(<<%XP>b9cF|e(hB1zj;p^clW8Mbr_X0$@bo-V1ENwaqHnnLnhhca4p3l+kZ7e=SE-&`q>|0i=R6`HRxRBk%vFAFTysS*&A)#Gahiqxl>i)TK`5Q#iy&qSCV`BS%-b*ov&@2eM|e2`_;JWaDDv2G=67Yyp6NTG++1XPbF95VcV&H$4Ix0n?Ird{7%Qi_4x*2-?*21LcUM6k7eK-@=HdI9H-hRPf`D_i&-|#deJ%<GlEXab-;ekaLzP7$v8>##rbLw^7lS*^}S=g{XNxxNZcF}OXs5xLa#~tc&6l@dqFvUADJd`&%GdkzK_fj;+}g!SNc9;-XBZu%6pE^i4g&^e>V3ol6$^SZ{VCT`nHXm2If2L3mU)rzK+MavB#G-ZgxZ*KK!2MHG;n9&9E2bbFCjkY9&|anFlz}3<@Q#&NH9VdB&Pd-19yDIlk9oiL3JrJBstncH*9UN)4T7tX5%?d+rf`qjMT-OWgVXIvUU78MOYxQD2?k{Ih8tHWOFpH=_rg-`E!7uErtMe;+@ZZy9mVJ;jIaDaM^J+q?_|`F_9cDaqCOb~f&1*W1}Rdl&0)c&6lL<T3eN_R{ws%66$siNEGU=beHG8qd5}CHI`eM<PD6x1G}S!gvnncHaUUXE^5@J^R$jesF)W>gfJr#1OY~f2MUf`JNn)nS=UX*|ct@<7hm&#MOO=wZeU;bzjLn_nmteXr04}t9uPgrF)Hekhtf(8jACzo4C3k8Nbl|$lB0Pa&_Nf8|c1c<@K}mV|+*VJ7Xhpb-%MxalflUecbPiVBGKCAADNI;g!A=&-VjqzL8@k_uNBqzBQi?v2&bnjo28;&3Kd6v$~GfbLc(d>Yj`9r1hY6y&j*|EQ(K~qffmaht@>gmt%>0_N%ps!z9#K`Q?ZFI!s*Um(c~k1N@b^%4_o<l-I0Vn|fPbe~I58hPSaj*StgXwf2A~n$*vg&a`fSC+@jt{Yd$1w)3U&oES~<?^Pk!hxH<^^4IK6`D-;Sq48{ck@lr7UX<^rHxaiw&_21)lKoikHrUq(`#Ia%D7o5iE$p{O4RO!?ViDahtVZH$KQ|`gcb?E2)Iauf<2~Fj`hP^@NuEpl*uZNaUXHf?3ijw?*;1<=ugcY$`LiW)+D~8tia%xl{ZC-ahy7PSfjv8T*#G+zSRx<8a;^l}#qbm0PltUG{&e^QU`N9r0KX?}fB1{ImU7MIihv!*^*rnx*tziMqW&D%IQTDdy}&gO5`Hw-c-U~*7vL}CisxDen+Sgyd?#!Id?)<Lu+!mBhTji%0Q`RN#V?rwTzxU$zF<9J2f$y#wSa3r*A%YVT+hMIhd&>6g#RpTZ%FvVU>Cp_HWGdgS1wm7*CDPtu5(Z+*jlbNT<K5-*k-QvC|jekeOwz*wq9d9xJ;C7(Aajae3Y3Q+sU;NW%(N0%XOIRD6|`_nClc*J#+-Df~yu~r!*$=@I2Q^=nB{yTvcdOi@Jin%Jn+Rsx+3xm5s93HI|F@-47Llt>fClwHnF<dxfhAWm_~>i1yXc39tgLGPEf|-2#-0dS{@EV7swiWl#awMbtYFUDjBcw$A6ls_{J4k7D~VZZ#goaxhOdFU1aH-PLoCf~8`evN6xs;b(&vVm?*cnk#k@?@YZT#V+IBt9PoHc<1%3DK->40$v9l0u%lvE(<ybR*!a<AjO1V!*v?6z^-8KHIQP$ujDF+PJ^Aq+EhY{34agQHmDp-)ZL4+JsR7^mB%Qrgm!}M!RI_^8<^-LU#qW}h#QkN<)&gHrZ%vqTvklP=6cqY`-+JeU&EUA3dKZDq_d{IMKO_EVxP%?vcN<xZbsQ!jfvddhqBEY6MMi8l<m`)c*omOwnJlwuvXh4#Y(Y$J0Zp1<T}op_R{0vzeD{4u%+-1z%PM44qv?gvy9?K*tg)niGD9Y!hajqf^VVz+jyU^F^Ugi55hl-XB>ls?}9CdUyk}Nv=x1Ah0TM%75>YR@HfHkg1-y%7yb;cnOsSX_J$<9-%R+cU}wUghBj%8_Kq~xw11|dZW`(cU+f`M(Jlv{(_p8;@51#2S6k>Yu!&r;T(h7_U?X8CK?c|$SOXdZHW+pcG!|?i>{uuiYzS;96b2T|6~yHabpv~xs|QyLs1;Zz*j7+WF!9%ns~yw^tQX2#LLI<{!*+oBfW^S}fug{~dONtDf~J8@z<ZnljQ|@3I|6zVO!U#7%MW@AY$(c~gt~)?y53wqkRMnO%DY4UVBVN_8^{ODAN5o}Z8Y|zHXa|1jnL-n2R03#)x2hawZXb~gZ#n7_nO$pR>CI3kAjVXO@<$ZbxlRvmGD!wc2RgY4rr>zI$(X;qfD`uSO;&EDb|WL{dsFl#9T9ofr)q&IrJFR0!;WK$Go8CV9n89#js+{QLi=R3+9V8RL@n+7xlVAoxwU|tyRn`)*1Dlfu05vHduQ{iUl&t#V{xY>}j+Qfx^Iq4MktUzhNThgP>rIi9KQ{6r?eOQQVJ0nPOrOn!uWJNinf!&4ea^iG5Y<qv{MV{1j*v+N?qw;b)-U3fL6*v9PmXQ{ZQzO)~5X))cSFXqT+@5gqB(%)j}6`WKL<KT`yO?H@vZ+tPk*)?2pZo0{hm9Ua+1#4Qh+W^$rlB174~0GVmaO8'

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
