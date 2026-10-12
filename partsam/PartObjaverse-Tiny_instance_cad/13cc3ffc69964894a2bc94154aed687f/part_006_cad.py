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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/13cc3ffc69964894a2bc94154aed687f/part_006.stl', 'relative_path': '13cc3ffc69964894a2bc94154aed687f/part_006.stl', 'source_sha256': '9621d7fa09bc2d072b6ab5cc3ec59b5c739fcd98dbd1018b85d21d6d756e8da1', 'input_faces': 266, 'input_vertices': 208, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2126201093196869, -0.17666971683502197, -0.4016725420951843], [-0.14663439989089966, -0.021814554929733276, -0.24681736528873444]]}
GEOMETRY_BASE85 = 'c$}r0dsI}%0fz?>6rX_jti~HOq6D9yqDI}=Mk*RY6v4NP2x^LmV5n~|CPqo3vB7G6Um~DUj64ELG;&2y>kCAIMSJ4@(UY{cYLd2Ta?&KdbMJ3<cZTUXJ?(nN-^a%|_wGFR?lE?{ciSLhy`Clh>%U7N^hcv~GXBa+&RDY|DLHdkTKYOK;%|EMh0Kka{c`MFFOo$zge*<YOv(ruuY|mi5*ZSvgruy>Sd)>Mws=*>(q!tVCZ=X48$NS+VtTUi^Wae<BEyvMAz{iU<$rv2Fm6E)9($vT=1^y?nc4ciDi3e_N2%%6<bp<-w`D!J>*@87p{94%WH-q?>G@NGr&nhe*T}9*Udb`N?auZ_nO8e}$6ePpC(f#$KciXZ)v*!Wb+wit(>qI|nq;1Yj^o<5KT5c4wwL^Elgw*bJGl0hmqwUg-}7U$%qvk_?{NL2&8;@?b4qTr%-i-q=ISd;Z(cI5e`L2q=GBQ`)^q*#`2ef_vOtH-t83D@_U#2@bo2MVKR9GwZ+wGmU;FXRDzpB>bcf74|J9Xm|JL^xO#j!(EizA@+PL=Z8@HKW>wU^0^GbCiS6`X5ywc2^_!gNbhc7y0UY}IWwWA(gX8D<+oVO)LSIF*%dGUU1{`bmd@0WS;{gQ{#WwQQcUhGejyQEY$Ud*=|uYeuJviZQgI3M)Tw2x%-jd^jtX_4cKWb>JMaXypdpPi7c7v{zFq6FGb$krqC;(8>rXB5cRJM-dtSLVg!o9zqx3G?E9qHbA#%&af$SImq16-oZ=1M_EL-&6bkMKgad?vpo<A2zSQli!D#7x!V}H|daP`}Q;4t@?UGjm(pOjx@dU+?Ga}*DAcY`dV$ZxsN$djA@d25*~fm(<|X!tbMZfVUx_;dgL{5?dW~1{jedkS>|niow@pY;n&u_^v>gEnJ2NicQ}9FX6;vvQ4X2ceaG?jZ!9tQ8GYpzhs-N!UR-^)pV()<?~wYOC-t7*8L+ZK);{xM`^5XbGTHqzFW$eh`%$s1f0!5hM?DvDTGs!}i~X-XN%>GVzRZi`>&)L%D4Rdbi}T0!usL5gKbdbeKPzqdp7UG@*RPxH_B(t<=GBd<rYGN@ZIpSZ^V(fcuQflgKL6Y=Xp(u&>p=tO?O$1+D+Xpa%e;Q}r#qfr53DfPg}UKIhs@jTlezj@(r9bF1V41hysa{?p6iGD&DOeD6xSm2`lc|hzA|9yr>2j;R>$=Z&PSzUAMZcODVNrt*ia&CUk|%pB)d;N{c54?{pykT^JM)-D(#14{jcUe*e4xdcyWBmuK2y&Jh?yNvUGfz7snC4)p)V`;<&)K8W+L4`VF3qi@o?zi_E+FpLzB<hm>>mTa6?07)P=FR^!V&##g-mR^!h42jlLVw}Kb@hs_7qx)8kB&upH!)}7$R@nZAGwXOv(j(e+lC3x4oV(kd?%DM1!a~_E2k;@C`4)bih*!jY|c#beHo)@BL=LPfPc_DgsUbyZ@I4?xc&I{(n^Fs9Oyl}lQ;k*z%J1>|Q&kNDB^TKsq;k-~E)mZmm-|vdd+fF{Uo|jjhYLs~;wec?3&YBeKx%kz;HE@2bPp!0l?GM)HuG3%g?No2Ko?Cqf@a=3%vYvmx7|hjoHXpG*r`4o$^_8#YTk~;s>K#vS_uXq{N*(WOpIFb2JDTdb>rR_xdhLg3zW(qSbH7rHdbh~DefTo29o_GW^_*DvC(e^^x>@^M)S?!dSN8<-?K~|s*NfV_i1TdUQ|G<Twc}bxC-&7#eRfCAJ0B0OkhQOUalTx3pUjK*N$&ZT$=<KNIlNTXZ_Kyqx9B0ovi{c!{%EboStlJbFOH*@7j;TD?%FrQt>?1Wf*dk0&L4gLz~i#{rWFKO>+bIfO)@XeTU&{0J~uh<Eo_#0VgBpmhnmk*%COyyGT&+)mE`0}*ZZG+%;zs>&dw&O7uGKsSbflJN7x6L7xw}3b?gDxbz`}256cqQPWiSIA+-3BAd-^k@zo)f^u<#C)!~YW|L&{9F=PJUuMR&j?xDaadB{R=9{3pY1o#*@ANe6TAAB5n3Va-V5_uYY5?q8V1{Z<PAj`mKz@^A?a4EO~c@|s&u0(zUt^{8|ehR(-u0rbIDsVOOGPoLi6<G_u3ciW_J@_X0Hu5_7Hn<LX4O|Dlg{%S7yaC>Al;0R78in!<<on<m;22~sI0hVx+yjmU&qVG8&jiOAWr0!V8RZBH<wM9h;6va8$awGp@b8du;5f8Td4o|l8Ra7s$|cAx;1cl1$ZYV(;B&|~z~{i{k=wxM!55L+!56`okU8K>;48>?z*oRGkUPOUF;<jcFv=vOtU;liWt3G$NjJ(66v{)9tHDFTBas>4k>Ih&Oz>Fn1mx@B3E+vyEN~X?XCm(5Io#JOa2oPia2j|e@@L?c;8dd|870{$ZBZ!uA(w&uz+I6mz+J)JkiP<V1NTIxf>Uu_%5*K$b^9g?<+qU4;J3g#kXOMwz;7dOg5L(ei@Xhf7rYB&{T{~q7Pt<%3%m>U>(D1{&`(L=L?i(xf)^vbz>C3lq&L_OUSgEjjI!J)Jy0kIB2&PD;4a9e;4a|y$R*$<XrD6O^XdNnYZS_Bkte}x!RwGk;C0~j$TQ&e;Efo&t;D@QQ?5j+#J!(Wu0U=k?){%~DRLutBig4t%P6yr@>>+j`;ZCXec=7bx#0cagUI>dgW$u+h2X>BqsT?zqhJlW08H};c$!h7jM5#2ascurZ~(Y7^5@{r;Eu=_!5zWvkdwjfz&=PD*az&3oC5X*cR>CE+yUGPIThRq?2r5<*dH8(j0OjRdm(3ldx85RW59jE{gJWY{@`HbOmHxG5Hb!t2po!x2Zw@(A?JXHfkz?dfk%NOkPE;O;7H^ma3pv<av^v;cpP#*cpP{%axQo@I2@S(4hIiM&IS($KaZRRejXfxd=(r59)NrWJOHd9Uj{4Se#q(Ie&F87X<(Y&!M(vfQ7Csq1`zkTK)EZjGjX3Il>Lw$iTm84+!oo6xX&rdZIC|THeiDECGHnxFJuR>7uXxw3G5ASkMsw(2X{dR5%)e!IS|>4xc6<!J&=8gd!MJ=2iYIo2mA~&82k))AaW3RAb2n`6g(Ilh8zYC1CKzC0*?TXK}LXMr+c*t^8Qc%<-+|^X-9JZ0Ym(k{NtAAzno-Lay@*-PWLg#tc~%9et=p{Kedp51HDkmMg'

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
