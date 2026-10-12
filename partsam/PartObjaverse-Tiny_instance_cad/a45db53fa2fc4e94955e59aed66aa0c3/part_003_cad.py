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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/a45db53fa2fc4e94955e59aed66aa0c3/part_003.stl', 'relative_path': 'a45db53fa2fc4e94955e59aed66aa0c3/part_003.stl', 'source_sha256': 'b6f1e5e752735ffbbcc059382eefa17203c8ce05610560d45cc0a37bd8f63d36', 'input_faces': 192, 'input_vertices': 184, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3036230206489563, -0.43637120723724365, -0.3777122497558594], [0.23459281027317047, 0.29448315501213074, 0.22767730057239532]]}
GEOMETRY_BASE85 = 'c$}q~2~<_p9>xzUq6R5yWLkM0(Lhwt)KEF(SWei})Eu~^s2D1NisE!MGp(F)PCF<f0%9WK@KTS8IN(5`IoqvFa`yE!Yt?JLv%mk>3-0r+_11fLt^fLdd}p71_WAGeULtywuTWEyPdzO-rSk;KSJPB@Yc;h=(eV>vhDRp^jf<P&p;d#gK7Z)4-u-(;4D!$>X;b}2L?;Z7_kYFV-+p9U|3HWT$no(L;-khzj*lM^t^BT0u?f+(pD;QqF53RPNz1ma0v#bu10B;H|Kq2M-2{EnxZ(r0x*ir6K@-1T6K1Q^X8?TNHBzp>7PMXYdO_Zo@YmG)0-8Q&2mFn>;zu<&r_^xe?NYw+_lfYet-a1dhh^<S`L*@M&l_Hd`;s26P`+dAQPgX_KI1FYQ?crP_}Wr=Ucvp7N*yU@b}HYDjfC&W`Vr4H%MY<oeyJtz<BGTdziQuuDF0q;kvy;5QPkgQ=`!VO58A=kLXM%G=9xN&k%yvS_+~2~)MJ(8A42)cMQ2d|N1m5(U#u5==i^-X)?4k5qyA?{ArCIkW2ey0EAO92`I#X{ly6O&3tyXX3VF5?JHR(L)Pb+R9&{M>ObJ+ke9oAT_t%Hb%9rbtbD+L8#a~#n0Og;F+l@S*JBj=n&8B~j=dAp7ChBij3BDHb@qXMl=6)X9S-#H+l=t>VJI$^`j^cf*hr+jN4YyGKR{!15*gf)|&EwDxZQ!*L$iMjtd~0=(jHB<i6~I5f;uy+Tew2suE7JC&T;nU~4=v;OWT<teIi9=slK5A1w&48>>t#cKHsD(wZXbab_LFuSKNiTi@?MMn`T4nh=$8k3#gDqa3H2`Q9*gV6Ns_NM6Az%?+^jTQzt%>|*V~J6s4vov<N8wp;=eX370>;}cMtk?!PDZmE{Aq%m+GS5HLql}&!}V||N4!Gcz;Js9DHs4ie&WD!6nG2Gba?jbK@?VANyxZ{+l(G@;?OOy&NTBXs`1^5ypWr?05XFrC!H8)p{Nie{!Q;sISvhjA!G+aqzW=F&Vi2TQu_MdUt4knLN)iF@ChQdocdApS=^&e<u>~o_f%3_^!=9n15!I1;_9n?Ng=vs(k6+u<J4}?uEnG`=v-8+qOtYeR)mAUtR_CRv%jd>xmZENXETa1m4FC+9v&c_u?Tu?`9I_rE|_@Jl8e3I()6}*O)iffxY4%@fN>(5XQOl;R%dGquYan@G~vUS4ZO@v`hCp4PW09iGFwVXmtYRx15A;)tQfSTH*K%)W32&d?T|2&vkxr4$n2SmPtLeZc2NGUW4zPFjdNzj7NVtdM(dUYVGSPepbvrly8}Wb-*>OrT9PHI*s-ecEj_nTFu0ty-w!i{A~1t7IP1OTjn8IS6od|-c|pW_%nu}9_N4vd5`?Fa)04HDSt5pzS%PyzBa1UR@`^GHSW_r<aye+yEed&y@Pet+TK^{FSslFK<y;tO<(RS<%@QW#q+i<l=VAd?g8|pb{y?C(q^N))+GSGHh<bS{GGL5_J=V8(SKT(<>+@S_#>(R8$bBQYMH<K<#enA`kD;n(dc*s?`8HLF8x@N3SV2jN!ID)QBu#N#p0(s@ScW841BBHSy`V#rePd88=R5+d#;7A<;}(Wxkj{y@0>ax>w(t7Tk;xt4)fQ%_%`OZ7SL@I%8!Z4M?HhXWq!7Q0sD^gQs<K>ANnQck2xw8`84L&f$w}KPv%vxiCCx1LvJGg+P<Cet%NqxzbW~JsK3Ql_(n_;e5=)A_^xoL__zFI+(h1oug_^Mex=$)GT!FFcb1sB@Mk1rKeld6lJTB72)=&md(10s5BIHV<G17b<=I~%?<d|se>x|9l8Jh58#3<$|A9Qae)oZ|&;3Nk_4kXVzpifFg7!U**bJTCRGt&9!`DM^UY7j##Xe)+*`AJa4X??3sc}T|N#7d0@U)aWD*mxcQtyB<*cbF|zE~&q&9Q0lA6>sJ?|lXLxiWIme|nYCSg*|Nr5JZ+L2#<%>&|6)?$fe=-tdxr!U~rDxce*CRrB`U6kK0?2>H=s99RdOV>ZIqf*Rsnp`YtjEc1AYiF(qzz_-TzBI9>|#yVWzBEIQ03+t8^aqs?q)$Un$(H<=>@Iq<d>?rT0tw}gp+SliOCw}Npg{6I~dy4o)w@;Mz|7fQ**YkX7-_=ZfZPUfmWy-hx<|6Vrx@U2jcHVy|{gqwsR9I<$??&mb4;q&7^*cYv`0*K5SjMm6gL!H_u2IIfIz`I*ebm4_bxbJvrlY#vy8*_9-se<78NZJY#)D-Q9xm-$jpJpX3XZeN_$}VT^9=Lep3=VS%mwtXm3|BTYrd4dF0534Ir|!N&K>({O4yV7{e?U5-N%Vht72-{6ULSEN{)<UxAAFtUfmq_gmG@&--><MeZCkQcEER^FV<i4#eWozapUrP2;cEyWt<x<kDp}yeK%g_SI-gRbNm<=XW>3)?KC+jxy@_SYZdlYEqu0|r_Obe^(wb&Cfe=3K1^8!-+etXHVu~VC9@96`u@&9oNvvB4|4H$aX;iotF`cRXynVd?!N9>Pi2emwtnhCJK?*p!>*Ni@ZHy8r(dzub0A9A$9^ZI{%iH+ocK#6<i%`!9=>D1cKFt%#mJ{=4v{>(+6Mh>g$KyF`&5a%@BTjU9c`YM^)^2g{cZdhCFeM|eaBJpIL4`U`=Fdp|Itp?Vb|KdDDSqfnOD!k|F?ax`Ca(>RBzmGhE~J))IRXXx!daCK%T9hRb}0ajDl}eI4}Eb|3T6}MN8nj@4wp34dT1+*Ap|P9=HA7`9Q<|q<`C7zHc3mka}X@gztWSaPBLCZ_K-Z_0C!SdD-{Z_mJ~+$!_G)y7;wxkEqi?=KrN8=oja*m6D&u>tsB+or{dNg;M_UBAokOA+_Z^mR~Hs`?;&ZP05$rInDg)p7?I(IwP`$JjeZf*tau$y<8h9Kd*|cd$p6rcRQEro;gyF+c{R-`9RJWZs%lUim!YRUbIoZH~3YN^X-l5;=7&0jTZyNuMi~je@dR5&u=8bw;uf_=f|9(I4>D3{jff1%?f3{WW-55X;;Pnz8CWEiXDXV)|n)nmyIQJkY{VM57rY`$YVJ#)Jny;b&cJO`(2&Zos|A9ka5!SywsonH|#UU&5?Lted$s7js{+*Q9kL2<g@bJV_^|xe*IZACi+*SvifRkU)5@ABcn?F^rKAm`9q)l(@#vR|L&)scESJePe0r2He}neouN33noiCle`?1^)K94C<TcbZYC2hICOM6qLETKwAaA0sBX1(Fr7k3|C4WqvMgEv<P~RmR<T!@nVbn<SFmgZYU&#H)J*cmddysW%N3u?CM{P@PM-F2sZchy%D{W0y+Kt?v{5nJNn+(PM8H&45gUL#pk(G8LcOmy>D2`w#ewo^s{4%*7^*M4qvLCe?*^gY6`V_e;*_&F4>_e?gtwgR&u1Kvwu1GG=Q0zf1NA@6VR4?t%k77^i(_~L_6>1G~6|yh&8M4xvWM6W1hT><bwa7|qla)3kKTCdrp|}G>aX9rQayYrO9RuwcU`KaqS8{i9ONQb=YG-n1))PprPYxtEqShfdBG;upPp(ULP@9k)<mPs?p|+qlA-_Tmpf({ZZ9rD~A~}HUPi;!}CkHVUhf-USL&?3Vy~w@EgQ-2qO5Y+YO&|{@PhcqifT4IEHJ+?=E_oh#Idv&nX)0OiR`PQ4N;_6iKcj9Xe@4z_DBeL$CGQ~TP&bfs$lDl-P3jV|NnT8SkF0byS?MD3V)A<GI<nHu<n`n&)J(F{Y;rc+w1sMt-?3wk9kF(dv}2SVLm7&r7>dU*6pv#l9#0)fRyvxjbS!x)HHkWwoJ5YHjwUM|PTpxpo*ldFaN04+jzsEAveFskL3WI=BifE>c1*EjGBuhU%`%gziR5Y2>C{AWBI}>dP&}XdA$b{f74<{%D)MTE;uMDB1=Jbj8GN4wETeQILvb>7COMh>K6MiLeey(x;vrNgc?h|W9j{W~pgPHKkl&^zk`tLb#SuL`%GE6YpZ<0C=f_Z+Ntu7-x!+m#*jM__-|f2obqI{;;i>j6dqXOR1IQk=l4}11Ibih3'

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
