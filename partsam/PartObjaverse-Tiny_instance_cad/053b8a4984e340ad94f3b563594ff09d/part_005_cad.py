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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/053b8a4984e340ad94f3b563594ff09d/part_005.stl', 'relative_path': '053b8a4984e340ad94f3b563594ff09d/part_005.stl', 'source_sha256': '0203698f6e8e842b22813207ea9349f64446df449567c0d51a8bcb91f4edfa48', 'input_faces': 154, 'input_vertices': 141, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1456577330827713, 0.1962369680404663, -0.16398748755455017], [0.1403495967388153, 0.49999940395355225, 0.16509535908699036]]}
GEOMETRY_BASE85 = 'c$}qJ32YX}6&@QK2W%+!5fXcy7#m`T)bYU?dodV@jft`2*yb?n<2RUM;{yy7u$QD9F?Fj#B}77DIf9d#Ba{FJaSWlPNhOlf7B>ZwY+I#O)JTccmZp)Sbmq-BW_OiJRr^by-nZYrdGmJW&CKp!nBOmA1XI6w))n5F(=&)Mi5ND5wT7D4)K!OCCN(r}2xCJ?mp^THFDNM}EDvL?Y-3VQsHM6&X_}EVqjpMCijh>ix_M1=Wy7-7%{3vZ&#7G15)yjLips{2xSo)jo|<B$O-wO18~@{Pph&^_<j9*>gta$}>&=!qbso);*1oNDYdQ3;MAFT!O{AOQU)=KgbLRy2#W^<jl(bGjxBkLT$!n+cIQPakYI4cn4(R49%3tgJaLsLs->vfD@9gH@e4O`w^*Y&r?hfpDo!VcUahc+$eR`AHKl}&sw}X1cKJwSPxhwy+*WV24@HhWFUFq-smEy2Om;6~!uiQ)itY)mz$9$~xxO(#E)d77`qVms;yGVIGl6sf&4m(gz`MiJN0zF^ySkl?`AJDj&#hvH9<H-xQUnX1R*X`3;)Svx}ouu=cH$I>^d)54!cSrY--u|Z>G><n%o}~K$-Obr?g02_GkZxXni*#e_r{r%3boa}OlXTq`O}d?+bi4j<C$l{|8<hBK@;?}PN!6p@-<VQGakS2_4!Q01=STf<oTy7`9FO|_wQer@$2s!<`)7A3pV*0N+{*pBwXp0G#kug=8Pb=P(YW#G{l_W)fbMP?a-90>SE=;YaqrRdJX(5z`~$jEJxtAOR?BJ9&GR(B?n|qBD6fES^p2<JF`6fId+WivxrfvJCco~ie1g`A)BWsg6z9m|cPO8uYTk_(_rFT|%2=iIM4xV=e%y}7u94mD*UjVyu2DYDJ{2cF)*t_X((T#9KJw~TUZ?WE>Hd=ZurA!E{kmJO)`gLMtBc}%aYFfH-8or)-L=%Zv*x@@I)CA$(y^|!ZekyBn)Y6$`?-F92kTwydLPjKR<1t|8@BE$`Oo(IYu#A?^(&;Kp4lN)x7IqpZlgY}dW&?s<E;<LZ(}~K7k8CkcR#;G>(MCgKJ2YSYv#vPZ$^<{H#Y63dNW_0wTt3J|5(k}+iKp~%q2e}ef?q5`KUvOC@(Xh?-_H5u74QuJl)5B#VeX=eE4p^?*4NCjRSkCa5vq@{$nL<rFCaRw{LV&ome<uj4bG1eXZ)}oT?uu%kR%{?(i&sd|sjUJ@f2yq?-#O)%Y(^`=kwB*T1dLDd<l8Z`AzmRQ1oH>v4034?av*$JguP{rKzTcg`Q*J%aNNdf$16_-2nkPZRq#@A2njVBOj0{r&QeuYOK-c-|ks&;NH3$Fe>1XpC0#>jrd7&+pFl$Gp$W?x;F(myG-w#m7ElWB;+126XH{{3lyZXM5_<L4C6Qe%;-u>eDVMdn4OZ=N$FV1G<I!H%E7quGf)?^~Hm_J{Q_{ouT_!?`ACC6QJvL&9UBjz~93Dp!L4@1o#{6{y6SXwGUYBet)gA>-Wxh>xBIg>k+!1UtK45K-cqY&i?X@Z(Y2N_qT|(7wH=38k=8A=NfBk_319oLGx^^8ozbw+;K|kdsO}Vb^AhsI$xiRQ|C6$Df4A@ewk^0o!?UD7h4u{g>;;QmOdW?x{32q>wNfYcfI~Rplg3Nd5_Zfl&bff_JiuY4(jvNd2Rk)>3#JXqt16bpfjBBPX83H+Ml9vGc(i9dUgI$j@tJQp8YA!d&Fk$&C@`hM&p~LoALcs{x5B#_YZ5!9qz4Lt3kalY2A%c?>QFg+z$8~lhyl@*7f_3_ICnt46F;S+ZT&J@b=3CakM`V`0IX+4_{X6M!#qF;=7}CAL)Jj@aKtsUGJaRpLsxMdOw72Cm}xKIJ16x^_#}Qg&xe4|LY#<tkzNU)%47<D}}zVzTWoXy**Llt4?5m`0A^z^nUV1DK~Au`IE0M{lEL<%Siu!Kl!%FQWxkD_`bk*1vbHM0N*IEMqnrG_rS*qj29RP`w;kafqa2X*aGkw0*L}sVdKCpfg*trY%%yUfhK_}*f#Kd+$(^s0xv=z#jsPso6*M>*bw-O0&4}HM?McDCuyU>$K!b(g3Sb%)BU(WEbJ8Ukplf?y}%9v-yu*Z@B(Zt__G3&1WI71fj=X#LSP|m4S1M9q(BsG47l{!4nJva@H+HS3tIv{3As*#HNYQ7-&0^0g7-(?gJ7e;BQX{+u(9Cv$e{(}m5KYA=wk%NHyZs%qmPl8n-In<glE`+xtxmUn2KkRT+V$J@~y&HXx@hFHjK*(#4JYKV#KIJ%s9l2LoSn$a{=-$Ky1ke;@KkE{hE-xm8sg2>!ea(xxi-FZQ!!z)?$3tV!R}uDUc#C3wAPi8QMPwTL~`j%UUmlEdsA*s@B_Ko52g=Qw?i@%bHI_yhOy3T-Lu_=hI;`*!}fApQ-gXANfdLig;zP%RRYQ<N2$Ri{x@YX~0-DVC*DcfVerZ8Q=|Q^Bv@ofm|}+r}qY#PZR8B@G$}p3Oos$4*rBdsz5S$8m?2pN5hT<?<Wv0@Blc&^+W-ACd9)gfj=TJLEtf16FgTSPhb)367bmqa}aM1VogLF6YWg2k$jlID1qUy3E%?+A_RuQehYjk_!!s+!Nc(^17IV-hX@SD^A5%{Oa7F=w*?-B9R<ErV5PuZ*m>Zq1Xc@_!!8D2C$JUmwxZ2a%uh1rC>?W?j9Bx~|2*_9c?HJsY1lmQER0tI>;&-j0*z?bh&B~ylZSSBXp@Dxn2Y%+%nu76(eFR~)qDSE%gxgF$8WHu|8>FJ@}7v*_wrDfA1U`oF-hT6%%8~JiTxV{F5w;'

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
