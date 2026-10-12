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

PART_NAME = 'part_013'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f62a1cee604c44f5a4e969cd8eca06a3/part_013.stl', 'relative_path': 'f62a1cee604c44f5a4e969cd8eca06a3/part_013.stl', 'source_sha256': 'ff9655e30eb81850832ed6e6d9622887469bae9ad1303528a0bfd611a59ca4bd', 'input_faces': 208, 'input_vertices': 143, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10171276330947876, -0.11845007538795471, 0.14520281553268433], [-0.09607154875993729, -0.10061866790056229, 0.2845601439476013]]}
GEOMETRY_BASE85 = 'c$}q~3v^9a8pn4Mf`}1>C>2NLg$#L(Dj`QSWT-SmXgrb|aw7?mNFo@o(@;{>YFSG3;Z9lln08dlOd>|Fl#v7>w@tguOzX&K8>3W84U?(N-uwHXI49M$X3gBSzV-j*pObyQz4x~tcO`L(M+aX<pFu2U_s!)^-53+$&3sw0y`U(2fxU3}lKho!%t!j-W9W{A<f(}%ZmgKC3eK<>E+_~dtprDBjtUM{f;009iVD(~q~#T4*o8kaeQ}|k`-NHQ`F8$uNO)9as1i9OR9U0^j~_3Q!^JK~KjNZ|&8hrI=2lW4!^PIxS^Ca>xze{Sy(WD<kbK*)F305WYj0cqtjki>50*;bQQ%4KhkQZp#q7Bt+xPa6KRfEK(BG~7s^09|N*d_*O}p!4`w{Nc&b1Emy|y3Ukk32UG3m4LG?}MX`k`!}9cZnP?>kaQ?af?vM)=y<`xakMI&#YFD}OsDedXk|YT+v%-jlw*Ynp6de`P&AfAOyL)iaaHAN>cJr!DB8<ge%?^HhubyJVhE-Kj8-r#_;e^wq*2$bT-6`tj(Zdb6($TukGc^pfnCv+OqI88|_<<NPwJ+Uz^Kj;l2HS8?8==PR<PzdN_mczS<Nd9KW`jE^(rru1!dzM=8H+Sg_FS+8`;(=S!NSJl3w_V*T1o|TO>?+0#BI~!AJ9?MSCxOKZs<2mfE%u~_7ll@ZP{DPjpyN2=^=_lXI#{Wh7j!RAQdB?Y2vK@Voi`qH;KFz!Htn8P1qMn{F`TS3EJRGeuA1&%U<r)7L)p?4)%wL~fN4~3-+P4pr@3lR9j{19Wk7YdDe7{AO=bdk!rTiQE(zwOu)SG=rd><Nr?-ywvZ`acEjXh~yG;Wspv;O2OtGip~MPFD={f%m(=aYxJ%)T1kmFl)OP4>&S?KHKMJc#m1pm{NT?I6}`P^}zK^{=Ps`Bjl}+}Qk!^=4mh=tR#a^gb!`KjEZtsOd)e%nkTh`gKRC{cG!~PHKW(X5TR*0?+rM`gcD}<52BSd1h8t$@wbz9r-@xG>?0lWj^ffcc}g2(~nDkWe=Cxx8=suIFtp@_#D|!>!MQ><#Xe8*}h)&I`!**oNUK&!JX#aV>`9~S_tiLecz@1<h5-yKAu#EtmP1`_m5wo_J{VP_1?7ol-XzB-lF<k5$Uq{0e0!DvE=Jlw~}wuX<Z*0Mf2!GzOz@or4F4Vw@{uxUa7Fu8+>IK)*0$eowu3l<gKr$4qL)qW?v8cvcg=4j`h#e&ogNq>l?7H;X7(+UAFBr@08N>n?I|t)Zv9q)UW%WRG8~czq66@4uFrkQgSv}+GjTh%er#BxZbiqC~3o87XRO#mVHB6zScVLs6)edyo~)%IV$Ucom@@%eC;pmK|Oqj&NZJ^l*bzbshyVHR6pBesQtZHXuigbbeVnQJW@Nh^J5#S&P$^#zH(^=`A5QNUMj}XxPLl?)=S(Fi?6&-=ZxN+_GibXvDAKEZ)(Tw<tnppn??JpqnYMW@q|D5@6^u4@+z}$%!|H)>PicZrk_1RWu0rUmR&IW>fRry&g1viS^VSYEp=%4TKG9jy|q1mrp7YwENKk&_uh3nFY2dMn|<wx%a(Ov_>Si4iii2?mQ$AcY->NT%2J0v@lm(7m7~djX#kCb{zvJvhSqX(ooJty$?>$c+%JDv9kQJ*<>oqc-lICyD*q*Y-Jj}Q+evlK8t;{x>)g4R>Ri8Zi+tnW6%k?ajdi5eV1FL-eYtsE8|Sq;zghaqxD?BN<t)7^eJ!bh_PvAceAJ0jN#mw9+#nzOQd|ANH}(N#2lj!M>-1jiSLy_+6T@%6FByLO{m1az?>~;6{~-U9v(|gjv8&Qo_0KK)t=8B?<GJw?`3paweSX9@luxR=WuJE@e@*?Z_pzQAVV_y%U5#?kdaQ9#`#7hx^K?!zuRoKIbCA7vOg``2S4HpbLFcKh75iB22^t5Sr^*gGPxbtA8fTo#Y+oSlpI%2Sb)r?#{eguart!x;!Pw_*`w!83aqb)Qt2Q6Ryw9LIanb$9;Ripr=HWi>8^*jV<9<*1;J#$kiQ)g`K9lht<=OsTwE0~c2i&jP>IZ)N`;{Z$ZOW%{hov6$T?c5sN?)<u51m)`Q$C&dTke_6{wh6x-D$a(DuKJn$9XO9w~3Z-iPx^oyRY)^ULv~iZ;6@drmu*q7d>X^!@nYCNBvh{5hKDz{l8xkH}M>n@_3#{DKsCt6r2xE;W3m)2#+Uuq(dh_L%>3Vz!Si+&_Hl3ScL|Fg^mNO;Mvd=a0>F7jSyS_-2@i85nKQ+gl+%}%>x&L)1c|#bo3z&8VgPXr$SY*ikwoR1>gd_BUP3NV~_I~z@r~@B=m9cNboEkFYwsHV>yrc&}GmqV4<7A%fLm@t>7YXF?1VP=n8N#_!;Od@GRu>3_@@;bP!nRKyWm84D?a3&{5zq;JMKG;Q8poTxbz^E_fca7+j2;=0T&u(Rhd8sXRvWc!GxleGEDp{1`Zx$8UIK@L0`b9W)b~0Twz9oC!{Z{u-PJo&=2q3mp!g1df3QgM*Pz3_@@MbShZrVsHX@5p+FRXbE@`I19QCybgWHf+m8qz)wRbfhQrSr=bbp1iVAA#$zFmH5kt|7_&9-GY|_gW@7CRW)If7(6P|LV4*|6W5MI0Bf#Uq@z6+cB<3I<A$U4;8h9G=nT`;g1J%Gnp9ANBmq1IwLi52(z%!vK;1u*>CUiV_CU^!k9vqLHW<YbmIe3TQwLEfpJj-Z*6PgFj1?Pdq-WJ6pjK@<vlAx2JVPK)Z1WyJ}goc7Ag5#h=!9t$|$AN9^!TDi>=7MeDZ0K6B&{g1UupPP*EOY_b4o-$9fs@dOWavb2GI$O&4jhM^=0LN-*?5QG2p;}Ce#K)7G#u&=4hIio^l{_i0qqF(0Q(>W_vO(a+6USZ+y~qp>IUu({sls?JCuRl!JQbLK|(u28MrgJ1JncD0o()X1NLO%!oyfMgy3F0dP2KGyMVib{SbnCLp{O0!M=EhFW&D9-^j-k`Fi5rM*iK<zkc8W&|csH;6bKb2O$I-XO~cKXiu;=*bCYf>;--V>IZ%VJQN`~1lk)M0uF-uf`h<;rm+y5IK|D~*W>5@Me*RH$;mhW!=n9PTCc6<zYO9<)OLwYoYGN@F)tu@dExr4s7Ur71H;J4'

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
