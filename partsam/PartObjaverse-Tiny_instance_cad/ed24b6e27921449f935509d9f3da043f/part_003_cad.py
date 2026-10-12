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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ed24b6e27921449f935509d9f3da043f/part_003.stl', 'relative_path': 'ed24b6e27921449f935509d9f3da043f/part_003.stl', 'source_sha256': 'eb33ee9845d42f4e01428ea183ac44c327215c9b258a6609bbeeef8aee5a4878', 'input_faces': 196, 'input_vertices': 132, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.07593934237957001, 0.17786073684692383, -0.1022452786564827], [0.2462245672941208, 0.3575563430786133, 0.03832007199525833]]}
GEOMETRY_BASE85 = 'c$}q}3s4o;9mWsfGXe^tQBhb52q>Z;7*R}C4WJMaR7AwbMR}?`yr3cqY+_<+V={>vtfR<P+r-+YY7iBx;c7GqnzX*7X;QDYP1UJRlGa)~HTInU|65(Go$0i9=9}-^AOAh~>^W!8?j=3dql2H|Pmmb#M$TxLrw~e>!cQ#Cw^tU=&##CoEnn^?dJtD1)7PhEPD;;q6HCR4u)O?=`S!3;T3ABC$goH)tf0(ZY0oX4TV~J8S3D_qQANJw6-Bw_`SLhCdU#BvHasFytI__)&r`As&ST|G&q+7DvM(yv9;7&0mET=XT%VrHyy3OIiaVaU!u3P-Hs!WC4F?pr9r*+Ek}<?x37s40ysGE-5g+SA?KrRH{8H76KfTQSmCt`oe3#cjD;KMoJGvj;O6{C(W$sl@?K=iGw6t2dVREBxJJl6UZYI8P7qw$6bU&o(owuej-}x?amuKb<s{h672dN*2C!MBt_V?lbfQuu{wP$Zpe{2O?h#MCph})WisC|<=!S&>|)V|g<yM@|G-TE=r@18*8W^x1E82#a9>eu%xnQMbTq2mLy=z2{qf|wf_?tH!14-nTMyxMNQ^gEq?MSt%-<UI8&F73dRxb1$weRRE>wlVLU$L-8sM(wx?wGZfgJ&>>KM`v5CT#RLIB;DlxoXTWwq!Sl=Kce;ESf0)8)G^ohe@y)`=4~LZN56KK+8O!ReO7L)TT9$k9(K^mo#0|~Vk4b@=mT!2G5#F+mGN7x+$lyAH|E~vad?b7Cb!V{YW`tPs(Wyd#>bcuK=sbuX~dm(t`c``j%cQN|NC^VA9jt_p%JsQ#mYrAbLS2RjgRZXYOa5`lGp8&b=1De#m>rh_mRVG3-kD|&d_n=R2qlJxjubOvz6=M&a0Pbe2n)l^Y<<vMC)H`jihyJa#77(-?Nq0t+S-}QL3MpPh4!_aW=UaRY=_UTO{>IFN!DbT)epbIs`Xn+ldSB4HZ=PPaC%rd+j2xU*3Q8fo{j>?`M53(Dh>cO)k!Xf6<rj7wyv?%v<7!yMl(&IG9`qH+omBr@CH!x&E8;G(JXXHs9~y&WwvZo+sLxtz1lDuHCy$;~)a&5I2TS{tca%>Cujh?=pzn5(2pWt2VCRH;uUVW?8e9i>fT*u5*<e$VdN$`Tb%Z=PmV(R&KN|;(g3(JhlI@epMOQA8K3IuAM|X@3(Co=zE=Ei62s3yf@#!D`U8wo5{rWOP;*%HRbTUzn4N>gm&lqw<L|%e_8c$Ykx#&mxESr_Q#3+T#u<?{`3C44!3Qj`^Dr2xQ_kYXg<vK_5Qq1-iYFT1KcpVXVPYCy|Hf(^KQ;<G!Ip++zz<5XbkUTM~hET|9*Uu_l@9hw>)R%_f8SlE^p+0;8rbh(ewt*m$CaLs(;9ryv6hATg&UVaT9T)_Vzixe;S*u+-dUU*tcn2Z#vBNS$@RDgiF+p$(<&@@?8U8&kg2_$1*>2p4Sz)urt^G99U27hj;#n*J&a3(=oAx#=+zUxN#zo_p7MYT)%J|-A4lV^}q4%d|zvGJb2u9ETHF<h{@vTHMsZ*b64VBo)`ZJ=C1DT-a~A=Dwxj>r+V|bX>tSHd~RwR(&^ZF?Wgoy(7w3W)N0}4_spGNE`6Q6+bhiDLg>D>i5>e}t$brBadB+GCi?r4M&>v3xqbf^XgoDzJAdyD=6c89@qM9P;QFF_bicUpo?~(yT*H0g91?Pp$Nx0VmunV3e;?<@NkQXm`>Kt&7&nfe@84tGzV<#vbzvL$`8$=LFZ$1Xh&#bup1<XF{!S|R9p2ykTr_Sb7vanu$4k~yyO9}OKOlgv*H)KI{WQ5=7s$`?yYA)W?@#CcoN3_x{3Dpg+2mq)BlGH{jr2YC^~{@EKcnNi2(FK-=XSPzPF%ly{eYE=?ci-gXgrOp=eT}R4fCR&+zz-XVeWXV8-1^l@-_32<Fu|Fi`UTmfNNOJr^E{#R4-ziXx>e3JiDE^7XE<u)r$*=>-Rq4=gZFey-(sIvZ0dByKQj$c_X<$rEc%HK7kwc6Ial2r|aC##B026G4IB@Biz5wQrflikiR*J+Zp+7HJv|c0PnMUL%VitUNiam@lH8?kLy0#@AgOD-`}3V_wSeA&~@1+zD)atSmk(BpWg1*(GNY>yt=2W5K3L;ucLxo%TFT()yMQF|1>I&{qKGn#gF)Ze;O^7eON5@5~T8rQe&jl^^KAmkK=f$GO1drDoEuOP$gJrDR-%kQi(V}O)3*^vm7VF?a0crE$1cTyNAFB!4r`aQ9lTtg6t#ZCG|9ppGF%)ko&>CkozHbL%)@Gg?k})gm;E}A$#HbIzv9Ves|>VQlao*xDT=q`VnmDYcM<oIT$$<QaKr(jhu`;3(CfPWMfP#Av@;ChPf<;S0PuSrWiHK^Wb)5JLW78%0%rd!E47{54B*UrJj{aka}KfByzdbGO0TF5~-Dt$vR1SNOh5#g!7Z6a&bHzc>&rhM_vZ6KwgHt1U?ga3G!@6<q7bK$P<tULMn$yc}w|9^?`iB2f};6eUW=0dqBRpE?>0O1=p+mDY!RsC%7lv8`%@NFT4+OU*t$g<-za}<PcoTVE9brNVqv)2^jMP@Fe(5<e3=LB+N+?<|PT-oFnD=@CxJ#%u_zJ0JUn}s5M}&hZn&Dqy|Vm1CKyf8Y?wLDq3o?)C-WxQz4ZLq^3y~N~J?8&wv*p&p^(BRL+7IAQzy`EJ)?y@Mz>8z=Pn?$kFJZ%6{-bsW7SjQgQG=<UrJ@tiv<lLC8U9GXp*qIRkkPq;d(o0J#LY23~|*gmI~XR4#>2LoP+03r)jZOhHbCrz58#$3QB_!e=1IA`gY<AP+?z2B{nc&qB_^SVvjrAPQ2sH>7e;co4EVA3Y(J-2{J>cYymLcR=n14@B;Ttik&uYsmiaFl2w^aCjVYIPwVbXzoWqDvuNVOjOV6c=$Nvai~#wJUk7qBdh)2CN*C?dN$98>&VJ8kd@CtR$hW!244s-K`w(YhnFBLuR&IBAeX^w;RbRo@+wGWwMUf0tKkN+fp)9mrO4&*MetJOa`-%WDYEjp$mywW?tUKs>0jZGJ_aoq>p#XHKePR7qV>!G`9ksVr7=CVquTrB%Y-|<oOM-i3F2Qs62F`'

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
