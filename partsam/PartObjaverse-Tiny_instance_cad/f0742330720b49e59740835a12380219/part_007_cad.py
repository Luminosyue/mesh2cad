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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f0742330720b49e59740835a12380219/part_007.stl', 'relative_path': 'f0742330720b49e59740835a12380219/part_007.stl', 'source_sha256': 'e2b472ca370655a188c3c527cbb03981acd5e5845dac577d17cc3d38d81462b6', 'input_faces': 332, 'input_vertices': 217, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1924555003643036, -0.2111300826072693, -0.17070592939853668], [0.1924542784690857, 0.08874887228012085, 0.4999997019767761]]}
GEOMETRY_BASE85 = 'c$}qL2~<_p8s38DJP$aOUM0Z+#lReh;!tT2rj(ciY8M5k%mGv^r{h#Arc^!!6TN{7YUYp%D(FE0O&l=Ap)7CtO3l>wY<kvv`S$+zx3A|Mcx%1&9&3H;`|fxD`|p4MXYYNEXBi#kU9}05e{EUPPsuGV@s9#^SQ9oQA#vLH(FsXiCrx>?3Tr^V_*48r|3NQB53Ryxuvz}`2}z?9{X-o7p<{aa2RQu4OirAZ7&qy)$%*j^!tWb5F)4xjN#o+CB=FB2f}ZFZ;0W#*;F#n1AOC9c5{$Ua<A*ux10E?A%+_4H6lU@rw^p1GtZn`JyxDjEAbqyz#ubbIAm%9LtF^-tZ@{<b*HwJ7&sSz&>)0cY;%(y^9i(q8w2sSmJ)cYdYMI~lhtDzb*%_>73wGVRO5-SBgRgi0zL5MD(Ir%W%Ml-2;^7<cE5zsIWL6gMg0JHB>wz-Q$~5xX>xM!7P3=m)rZ@hS;;ubc6lU`E+ZhyZ)ZTa49M4WXJ59u~&N;a>-(Fp0J)swhY2M$IQ-0+ePkv{}>s4m)wb+@I-w|}pl7~H7JY9U&^ZTz8tbNnjlE--Z0@b5@SEL`+ulbc4mHG=xE%7X1E#+s=emh&RGpM8Vv)AMkpY2I~aDU-1=fyse{rvs%7iOOw&)rOQ)@W~uXA6&z?^t;w*X--zr}mKl-X*G2`38J8<a?@9U+5?OJSMNp!Bdn+`Fic`l%G|P%`p4y@dD`&jnrwJfcDaVBX}qEamzJ%9pUS(dXR7Qz9{>8-dFm+JtqBMn$x_L@7&}dpWUsYn|&k3SLUB_iRyIDX(#&@ep_Dm)B|(PzTWt50sXE{sU_YB49=#!_uW*d$A7n1wz*DE{$FLCdU*)-!QH;CTvzFL<haYutTX%W2)Q0u^Za=hKTGZxt^1^Mv(Fk$OrrcBeo6Is{Qcj`>(%5v%A=odBkOD*bci@MzRc{i#r@^DS9V{u#MkdlzO#CQCEieV{#ZZ5;;%X<_ix{6y4lyg<@$7v=~QGH*DsvvcVgdp^3-xu{mzuymUvCgE2|}q%aU8m{P!-&acjm}eCE}du8aQLurf<L@)*O9%YEJEG1Rk$>R}UO%Ps!uqja7a1)ZrLtwjr&C)bP4FT-~$_03)ABjcCdk>}5V;WVzJaZ@=j|48ba@$#3nPhAHaOFsqYUdCXG*Ww$I?<oC)&MS5_lkz)$bkJuV=d(L&G<`PSnovY>t>ige!QUd+kMdpKt;yGCPhCWH-`hp=Wt*FmuT2QtNA)egPV;r9H;{hnUh>)ZyXAiWp)UFA9COq^P5p3uP=|b@>L3?=Kc<-S8&B1i<Bp!bi{`0cEwcFMx61rEz2};J7M4f8-m)8AU*}(IO8;aZ8c!=oCsw|Z`OPlk)Q~UD@p^cDs)v2%Z}GLqn{A<SOLD0H?&US)yl|g#-rP(1m2YgQOY6#gcfZAF#h2yzv+Z4L{5bTpV3ftzruUTd?KfTC@4l`k<EyQZ>nL%&>}R02%>Ux8M9P!0)9RnRLf6swd?(d!T&yDV-@GOF)i3w2ntiA0&z}#-cj}CM_mjzTJ+Ap#uICO9<nu@DRO*kBbdjzXtILkixWm7a_lu@o<aK=HpYnR-$^E7Ey(-Ub_-yQV(vQC*&(9sd%lMmK)KAANBdLDnvqRmepYA(f$@|gZ`*PkH^|FZPp0xPdJO85li?-&9JcrpoWS;9jv>&xQG4dSP@~eDKnTzL&@A7EAu9tr)H1|#GvXgx6_n%~*-M8eva^zTi{jjW)od}kF$h;@dh2*31`GkE<``sD!cbR8Tusl~s=E*wYI|}mT^HQgA<>q)JqQ+jzzi|(ptL*2y(%=23yuR`I@_qte-&~jCb^pz@UmSgI%W=;=ko$jve7<sCzb^gT=ugina$NY@4S8L(c_H$;r^@FwmgXy;Tl$>)!s6pRci}$h@qKQ{^ZcU%IybbR=F2*9jyZN+rn;1GfBsayD^U7c*veAM)9`>C2j`wA4}AOcs`Bm6tIBuyNWVgUoSzl)+n#TgZ-2h^<k^J#IPyDV7VjY+^V08jJ8Sm!F4AYS0_ePAA?eh2S2NU)c;&OE(znO!8&Quv9?umj-o37?Jg?*O*OUKoQIXkaH)_tIJbM!^P=8+i8^viU`5&3%mG4|CeS5sI?Lm5F@oe<XRbl4%n8+mZ8+y$=T$x`_`dZ(Z%N9TN{?nDlJEgDUnPc_FLxQuH&Ns&^U*9DC3h|EpqrxhQXMWOG@p|_YA#@&~&njN|&Q{-A`lft)|2=-$mh{Se`*l&io>sWpT&EuBH;l$j+iuw}%Gcnl^{jjb-}CP^m1os<%YIS5`-AP4_36p~{&vgyRKEQj@c6d%uY9BPkjzTs;oIwX!nfCN_z%gftbPr?y?$5wA(s83)r*kNi}v-YeEa%TzI}Zv-?l!DoRSUny={Lf-@d<;Z{J_ax9=~P?*><8>rMIgb>+$*OXs-#{87IB{87IB{PD!w&L4JhpuEr7&O_zf*MqjTT_JsMKmXxZIRD{SIRD{SIR90C`}wc(+s}Xa70!Q^$9Dd^y5B6UZ2c?0!h0C__WPhC|7?-D59&GJ<J+G9^)5?_&EqPc#pae&);Hzb`{s$a^+EaeKDa~Y9iw$?d+(%t`+W7mna8P4+xs`=+uy$_-~Rs1<J;c9Dc}D7%`>j;{hRXb@83LmZ13NcZ+ZU~ZFwuYbivYu1`QY!sL7hJF>$6>qQVq^iYtF5I==gV^-452IOzX<CAyl|@CnEJ;E$o-hfW2AUM1QoYUbDheh+#F^mah#zi_PN$lzE32>l_)Zt$nz4Cv(?=^XC@LZ^v#gLi_{p?87zg7-l0h5i)08+rxCTLxYWy$pIeu+}t2I&!4L-vg{g-nFJVEl1tUz$vEuDHuNmeOZB;GElGJb*B2)VSc-y(~vU_Inv;#0PB!<9dZd>n~7KRVj=Qd7Zd-?W2_dqCUi~22z`>{6vt_fQjQZGXTYbSPb20Gem57t75o--E$DjS1<)Hg-sIQ}2(5$rLhH~Gs51gJM!>HL^u_#YL%#ri6Z!?{+2D=Pv!U06i=fv-=Yv0k&WApRJ{&_2j=?_-e1`s=ggy=~f<6vyfHy*KL@x~V^$2<^xET5jbSd}{wCMRf^jPpL=(nI3fEPj+a%6Mla4hB6#<2vv6<Y8X=q1n#!8y<ip%;L&p#{%p53lzET*C$M>jLv}JtLrXU_N>=AGy>z$wq&&F$V+vG|+DYzUqG=dU*=^2sj5i2lF`s2z?a175XT29w797@HXf<92+=X9Jw4>9Q(kT(1JgL-Uodc?1DZFeF(e(T5th-c)bOm02e@?fIbEYt=6s3>%kk?!*wq7Z15cD7r?c_bJ)ZEC3GD?=(%7Qv<vf@3kW?AoC!S-`fWhycfeWD2RKShJuks^I07yPmp~Uo9|B6y%M#>Ly*+^5=YkJ{4?rJ;-Ve@$o`+gzffqr~f?fz-0{u4Tu?V~vdJ*&z@KR_o#x{&Ec$2A~O{g~)TJ<OkIkMm{1~wt@Cgc+O5sn%h7XYCzaa;sf2iJf;%TdNr1rS>Nd4WF%mqB}htAWd*t3g)>UxdDZ@y>zIL!W~_3!FENQHC64@XLYo$a~&2r?aU09N62G-y7q5qc0awQw`KBxT>lCs+gY_G(%2?91OlUP!)NrBA3vC96lT!IT~|_$HZaam!XG2CjmlF1^0uV3OxxBdJK3F^cd)5a4d8(^jPq#&|{$!z=NR^php2h58-G7ZVw&|-5xps{3>(+bZ>AhbZ_YT;6c#!p__yILH9#1nuD7_M{z`RJOv0H1Rek#1nmG1g?2!<0fu5uqrjuVL!n1QPXP~ro&uc+j)qQzo(YbEo(UZX2>l{Q2>2Or6m%5k_6*|1cN4+=p(jF52ZVNVJO=gy_lNd_4gst2<2hnD#sNYP=Xe(UG&lx&I`YN?PSbZW7(d2T%QTKij>&+~FL87Ohk+xZ$6>r_z;M%dk*F)uRO1^Q136{@LchZC9QaZ2K<LRB?+xH3({}?=*FaN^-8n`g-*eEfU@XDo!6Ttx=a|6p8h8ZsYtVfFp~I0s9KR2TKN1*$oFkA+XkU(&9PI$1n}K^mH-ioZdT=xagl@~xibMQ!v=g{3bSLPp;2zLjp*sRX2ZBSPLou#8{{*)H_k?Z%-4NUox*_xvU|;AbpgVIs4)zE8Li<B^0k?zh0B#L#2i*=mY7Ge82pkF>iheZ$gw_C|dx6_Rw?!X&0YX0y2>m3u6|~@B=;){_UQN9J(|@sg_@~p2$owC!?7y_WhA{uK886oJQX)F4nz&E#o17QjWa7kW&i)M+h{E9'

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
