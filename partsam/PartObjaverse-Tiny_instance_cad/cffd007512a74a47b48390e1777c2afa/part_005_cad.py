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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cffd007512a74a47b48390e1777c2afa/part_005.stl', 'relative_path': 'cffd007512a74a47b48390e1777c2afa/part_005.stl', 'source_sha256': 'dddc35fcb82a21dec9e69b79acf2e321ee08628ceea8e2058a0c8ac3638ed765', 'input_faces': 444, 'input_vertices': 265, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.39144158363342285, 0.053573042154312134, -0.4000004827976227], [-0.2976210117340088, 0.1720733344554901, 0.4206109941005707]]}
GEOMETRY_BASE85 = 'c$}r03z$yT8prowLR4f*;!Kl?L6cm@t(<%~<bFnUqcmg86d9Kp1|j1zMY>RtlG5oW(LpkyQ=fYmosuq?%D9wE>4cO^a@IThx7PQq_3iUK=Q(Gd=l{I_{oC*U@3q!mdxt5#d-)0pp8s>D_hIR`X}8t#JW*9I!7Iql8#Op9JHPR;5#!>#YGqu0bbX@N%{|j^kMjz=@hO9{^Rx0&u1iX3o6|ZaH7O-$c;2YI%wcy8&l{92ymRKz{A|VZ@5vmIt&STsYuO?-sd>ZHq=`xY<InjrhRh3gzNbp~nL3-=sam>VUfHqB!&eQkcxXQTQ-0YR#JxEaEgs&T8=Mc1$uG?f&WD@)A(egJ^OKEMzQavEJgob5{<v~}f5~uroDMfR@UZT8ax^#NoDk>d%uTfO9d7dBVcoCu9d7a`pW9KEb7Y3S4h}c@@UZUJ`3^VvMQ8n-F5B#UhnswOSoiDvr%w2M+Z;Q`;U)(j`fN^Mj^<{ZOMdiuK`%Ss;U*s**8Mu);U<6GKIS#h&Ud)UhljcjwDTQq@=t!`^W8~yzQavEJgob5zQav^{AQmoYHjB`+~mVUueG-G9d7b7p7Z$?@nwAB{HJ#Yagz@Z!%e=!O@8*XKHryU=R4fw!$bQM?fjoIeBScR1}n$mCI=pdyE)<02^)iQG<S1CXA<o3jIQtZAFN~NINapGLx<|vITMnD*Wclh?@V&=`foq`RayVimUfQAO%6N^cXKp1&+)qxKHpW>&Ud)Uhlfh)+W8JQ`E^Tt-g1bY?{Je355rA<(=U8}PhUI7;U)(j8r(N9M{_gI8$a@M-dkYjJKW^ML*WH>{(yC?!)!ap;U)(jhMSy$@A>@=cH21)H#zVy+~ka0?e`a?ZnAP5ZgSvZxXH<X+wY%r-exPu;U)(jhMSx*t9;(H#GaSKO%6QNti+yI;R?V1zDD-E9By*pq4ACEc}-m&JTHfv9C*yUj*a=etbWjciSSVS!d>kG_`=i~K0i_5^R8Ff{SJ@m?>{rRA8z_jjq>?hzr1esJ3OYpWc`xBez@uP@_b%zlb!GInEpwJmjw31O@EbK_yRlM;W7R7E?yeg4>$d_?)G_ck)7}GnEsNcO9T7iroVQM{oFfF3gk(xrv>tiMi2QsG27?W+uHq_pX+GnJ3J<5c7AX_JSHD*a+0%r-YV73ak$BGcudZb?qxh&?_ry>4l%qq%g^sJF_6df=S~eCCp>1Ha5K)7OrGy(d!IPmJa^4me={D<^*ZbEJ3OYpxc$<=`@+qA8)jJF4Kpvz-RI?SGhfZwZ)QB2^IQs(AF;VRFNeqE=<k&~9(c_7;bxrI3<zFl&E4@h-1IlOGkAR*ZtknOyRRH>`kUPm{9b78?tjho_d$=};W7R0d*Seyes}-3?8kU=?S1ZWv)?p#ze}3C-zA5e_0in@PC7iM-~Em`JZ3!ZcTDq_yDkl!FWk(x&F#V8?Ezhb*UjN3M|1bS4mbT7UF@8pxq&<s_pHrzj@z&AtNVv`v~n_r3=8Ci<>%X+oS1&N>7Uiy9{<*k!TiOIHrL~K`!(17Pc^Y}!kan=^1{XIY)(#0zaGEtFRf;evucAt9?INfb3IPCU$4LJ-+!UA&Z&WX;n1&bZq_+9kemMQd$(Kp$%%nH<MO(Jy!7VpgZsPvU~@elH(&1)Hy<98ulsfWvQ_r@^?V&}=Bv58J`OkiZ>_X*^z(AKd0v{k&)4Cm|BolF9JAjXZuXnz?*4SR>90839>0EHT&~|2&E5CQ<+{JhV?Iw#EBo%1wkWc>{&PaxDS^DS@pPM)^eN+ByUBq(^5=Q@i}wcS!(;L%jkm|yaEiTe_4mr*=6j{N`+ak`=}(*J?8DqZZoapgyWeMroBlRcgV$ekcl{l1)<<)9{T&|p?_Jg4^>=toe)RgMTfdbF9lO6=`X!zxs_Z3rIhj$vk`X9Bx(5GBW^men^(&dQw6y>CS2Ay^F}$wy77|}fU5c0bBEA^^Ds=(=Rs8eRC-KkYAEiEwmpTpqh|;r4bCCGwkocF7_&1RFB}n{YB>rzm{Cp(-2_*g@Bz`9K5&TU214#TV>Kyzm{0r3Q@GsyOQD4F@!mp;jfq#QJtVZHjA@M7zi}8z@+e#$<73zHaEBI%qPvD=y&!9eppMjrBor#}{FQh(zpQ7}j(q!s%{B*J=qZwq#c;+d+hQz;&#6OMZk@p~eI+_<X&UwsZ9=YOW-@c>tCUph=O}xI>il{NHh+3-^tmO)>UrAksmuL63(%+GIz30UjGlpWWD~9WgcX+n%z*kcj;bku^RC)}Fe-w$=@6p1j`!0+c&q6P<$Hc!torNz_n&d_H^CX^QAznZ0Nm0*E{1hbqek6VxwFo~Aug6>zHJ2jBQN+E)A5$t9=Xpm}EwAcvRpY2f@ki+q|Eu!nsrn1G0$wEk7@6Ybn%|VKsOm}j<@!q0llYVLRN}rejuX^)yeOW$-|!U~+i~vyEA=GxIQ}@-pF}6fI7*+4_kE?UN}noiR{BtBJynkXskDRhpQBH?M$Uak?`Ir;skEDGO3@CklXG9wyPtChsr$K3dP?Y%x)=XFbuZWa$Ti}B=J+su((@DkFz0`#N4yv3AIrJZ^!`CTO|SHvp`P=6f0n*e)YJHXabEYy@eiCk!gWVDKBRPj^SV!t_i^q!dcWg%kJ2}sKfv)$&hO*gx74qq{C19|e;3zC{Q|#@D#xGDyB&Q5lXD-_yAA(=(iVC)P`A*(iSxQoj@NnqUXgvak-7!Hfx3l0>0gh;>-{JD?Mvzo{FnF=>TY}qelK-DelPwoRqvO>_|w$i@p>PeqMpH@iF&rD@Q0}S86Lv#p?-_sgWpB{3cm~g1y!%Tel{Odx8Og<Z$evGt4~?4_o<ulo9Pj+-_@;1{O8oKy~sN*zSN7nd!<PHLF!NVgLrwjWbewpK1)4^Ka1Dz*&p=(jF<Q94|>GQ{*k@4jk?{7>_hQ8$(Q>b@FMTb0VMt#>Q4MluKk9&Z)80_#INUGa_<e)b@+9h-$2#-cZ^cLQUMa5M;(sO!w;k0iywv`g2dm0#1BTfQC$2`>PY-h{0Qo3{0RIg>NvdAu~B{^$7Asms88W1;OA1;;^*SmP{a5&c=<cZKdA3g!+2S%`&hp*`0>=)`0@D1smt(><Cl}Qock<?Yd@ae;jE)x(~(i@H<<I|n8QT0mbt#mn3q%6;@5JGzRz;zu^g`FC0_4^eC|0CKbkrYzlOD*iyzDJSk`M4&s6roQ2a12vNyyJf#-3Y$8~zWm$8<4^o@cSaIS#+Eu*f9TGM4b!)0*sb(Lx;U9QwfDG}C~<7P_jmAWeRP)b+2OR102K&4xhZdb~t-Vt>?kiH&Ve+$>9!#a`OLg{*?8>sE^H{d&w)0Jx*Gp-iY*7!!8tIs?d;bnd`nPUy+C+9Cxs^s}U;wvasVVnaQYiq{Tg7X(e_1EP3n&gVlQR=6ZrPNy~L+Mtfo=P2*IxAhRbgfczsvM^%$zT7Im1-+p0Z&E=Fv(~~P6qe66=iYn4DQ{Rez|uyYF~Ued~fb|8TUxQSEg3OSH{O7@$pD}RmPXXxbI{vIn1#o^KFiAgT%L`w!^o@ci?%%lV1TZESr1eQ04dzY7WmYhcy|9vUsLhtkGRad>?9Gd>?!dYEOI*d?#vWd?)-3)OKEE4~uU>ZHaGzZ%n-w-xyz?nu4#7Po!RfPsG=tCg5w}D^V-sE8#tAoEQ0tV~s1|<GslHd?ym$k9rHfAO2Qqx)<4#;(JrO;(Oz}QQLcwJt@8e^?G~<d|PU3FS1X>x1l!kBKt~wb7~_mviHPaO|6T+8lOzP+>5+-;%ifD;%nnCqh5r+3}1~}1z!y>d-y6P`DeR2N~uaouqGU*DRorpuGCBECZ$ZJo0aZX>aR3_D#wF3*NbazqyHw@jpVgb`m<7q+7TbZ-$+h(u5H3tT2ZgVr*f_VV^77)oN6(zOPG_KudZ~S(gjN8I6fa$=bHY^<2E#iIb6qBTai(nj9T17GMXw~qtsC8Ql)xIe^RQbbg|NfO6BpwuB5*nx)k<TrN1b3QA+O~S1zIafBIkKBR_>@FHiLUFz;Sz|1)m%m2*{=`A6OK?(s4|HMw$Sf4I0(-hA)hpi8P-'

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
