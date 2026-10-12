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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/78c7c67eae00428b9bc50c288776c75b/part_002.stl', 'relative_path': '78c7c67eae00428b9bc50c288776c75b/part_002.stl', 'source_sha256': 'd7e7265604227f2093665fe720137deda9fcdb98c4f1714c40deae79be770d65', 'input_faces': 187, 'input_vertices': 140, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.08331939578056335, -0.46474307775497437, -0.1182711124420166], [0.2531859874725342, -0.1475358009338379, 0.043278634548187256]]}
GEOMETRY_BASE85 = 'c$}q}4OCQR8pkh+5u$`2Acf(GB!ZfwLZXu0RQv!xP*KFsAq2$_7=geb^&%>%S#7zZl{y+AhFO||VB*!>0MXRi+}bo}%{0r}+C1f+lc&A!|M}PAp51fy?9MsQ`Ty>Jo_XHqeeOHM3<>eAJv(di=&m_miF(h~Uei>x(>iN;Y1z3MscAV6XF8wq(EQ-5$FKU*gsI~bl0CFMtuSm}T25+q*brM-OnP)!A6r;@R(5W7O6J_G?0IR*AC<B=C(ZJ67Nj`Stm|I=Bkg@`1H=2+mfQZvM_a1}V^QLv$1F92@4a+PT~|C`tJM6Y62A6T(HV8EzqjPDQq6fr@^gHVuZ;>l)Y7+&IdD;3yKV)%qtte~Q#JhkF7YqbO8xZx@LeH$;M*K?QOD&~1K)AG1M2Hh{SKfny`lzncJD>L{#_P)cVpCH^fP=MeC^nNtn1#kAHH#Q7<^+{QXQUO;aiJ!FUY!%(CPc2Giu;#RpX`4l+bFtuKJGnJF+kb_k9&I2kntM<?E$Mr{S+^kU8Ylz;~BUMji8yv2V*fBaUEScIihOu<|JC5BUndyKR*8^M2G3so(A$<Tp%|{(tm%3%cuq_;XSu|6+6%>aTMgMW53~%Y1?(YB1La9<0ZFs)oqAo}=sWe0aY2pHGtgwn{vR=Wp1LVa^}e@4k=PVfcC{=|@X!zaRa~7-J%T>I_-8!0`t9y1f;?F*sJ{P#A@|*<Sw;zB%?;sS|x2_4SS)!PoBWkacUEyJcVY<1OdlIzJzCHavCswzAt&KW`Z3saHP*-|XO!^Sojae6zR_zVYWcS+_@boF8+T_X(T__cr+ModLB{zqk0Slf*x~@lCugXC-`nLK``sev2f3X*qnO=r#6Pv`6+;1>b$6OzQkJ2IorOd|c`b%8>U_;1<-;KkN1`_BFIEeDl^O<eNiv_-2&U(JOzJ{xeeHYtALeclSQV`g<k+^dUJX1IlrJw6kyBRbTfUf%B=)xCLMTI8*8@TnOK_ul-5Pq1VrH4yT9Uyt#fC3|}Aepw#*13)I)I&W3OPPz>L3#S`a5Uy~~N*^%OR&nt)abHaBdPKWP`+lczc*ea=$To2zC)ePTuvQGMWOzNB8o<tp6`q~D}Vf5CM*yq@rF60%K!PlS55P$W#ow#n?3*RjJ5x!Y}a2NdJ4U!+RS$uE5*HAa^Z}5$``~3m_(Q?$+XWx=_gT8$ieTM~a$92I^QvaL>>KJYJA>Y;%)Y!6)R<x!JeYOgLubV-VU;RD$bg$?q{wF7;fAd}B+sX%u-@K>^{Uipxiuo0!Oa0!tsBb(}hJCq?E`hIYUxj@AO2tmRu4%pGPaZA%?Y0g3)j!-I{?K^rOABw_hW$+3D*m&5QODSN+lBKI_@?+5C(62RvmE`;td>6gugks$UxRN}){EbLp3JRH@ecHP#Ds6Y@WlzN8?*6c)HT{SL3b{aI$Mun4%&KO_}a&7W!>}F(Z6vaK=OUA$=sHORv>RmsQB3*NuBJ{-=mN8o>C|G3f482m%NHTvclk-zm&=x3LLmEuBp1@zy7e?$L+l;<UGxTulFyMb(i{LzpnMmrOw_s>9f}R6?y%u;`iw&b7*}5b1**NCG}(K#Q$Xn?xQ=lN$QuCNdFsmVGizBJ`n%Q)6%ECv)sp|;8Uo#Ww7{l@#x=n&v^Kn*K+Z5lTqJ%E+4+x$y@rb?C~V(CsazEHzH2qoRlT+#W}iD2VXy&f%D)pzrp)db2gl6d7ia%Cu4C=-Z?AvQ`<Mm`_bQl>*HR{$gjWL2>;8U7Gi(R_lkesDRpAL&4#ayYHoSowK+*n)R{IBz7gSt`nFkB=tqAoN$MQjF8Q{~;pjJJfz*k;DfJ(66v2OSsrV-bOFxVMo{G95MN)tN6!E)WO~E|ge@W_>do|<rU(dkbLF4Pql7C|y=BD`_fNz%Wk^K2vWDfZ|CBI>x<R|!u-_-sY%<bA4>Bku%@89TDsnhzr_&3@$Ab-JUNtnaB%ToW-4)4K#Yl{>4wO1uSy1(RqSCxTvZ`_dlzz^g+c&sZyzDMY3<k#-ze)q1z`m@vE>p{=SJg23uM}EJj#lKl9^}nzeV;;}1g>SC3%bWvlzJPrV-3s5hohbW#)LDu;o9ZS1`|Z;I=NC}Nk@%tHfA?2;pDsP~A~gQ-Ggx<tuY4{|9Iy#>E|kDGx5P<(|3-Z7X?Hd-f1A9I<~;o}^0T&x-xQ4f8f)Ho34LBEgRl8?K|jXu{LRo_jZ!}`68kkg|Ac%;PLKCx4uhnh;f8!pHjjaC?6J%FeDP2P{G%)2Ye92m&dJwyU~X+oq|WBqSl8Tr0(H#fDyj3>8mw#P79ig-t3mPy%tU?1$oud;#Bt!9<g*{`)Ft`5+3{2OX5AX`6T>sqwe5S~v&e7r7wP}_2Gns^gupjT7fYYxQ&30u9(z{K|9r`RBB2s}b&QkzvzySTtLF7GXs-qEwGn<&=Y{K8>e}7cC3P-658qvX7T*JnZw^YGZjJIeleq--ZF!fa&+H1Rf9?m&)7H@L9P)Qwl==fMqK?fB6TfeY_<fG7fDVj=uNPgG`&iv>_pyY#e%-C!ws!eQZ%tF-ZT-4SPigVfPMPZQtN#0+b{UcX-A}vdLI3YhyMAiRYI_XDc4~jJ(uc`*a$jn1a$j-;wHG;p+>`ncxhFY<8cbIDAX(`H<Pfrrp*VornXL3aasb(ndN0|J>`iS=_9lB$HL@qU4Yd_n={@8&WG`x4vKP4nwIjI$IglDeR@#FcNbXMUL+(xvr`pMO-h*&z1UZ}>#!wte?Md#*`G!($<WTbc)Bth-=XgIuaVM%bxf9uk>PhzGynGmneW_k#FV4u9p|}e*kQ~TabYUp&Mhz#2bI;uvin~%n$)VgsS86A6SF%6VhwQ_i{Ha~YUATrnU+d57c2;;;q5hMTYDJP2^Q@R-#e6HKQ`5+4e11ALi9Fm2^||w?roPiyUuUgYV?~A)nN}>c;tA?vY9?7}9(gf2hoSf>E7n?3Y{e?-O7coRzlx!_keWv>BrjtqUP{d*XR=qtOQ;TN2H8QLOI=8wOJ2}op9>g@Qy7Y8Fci<EE+)?;r!y2gsX62v?#;<ioXb#LKwU{LAg`bnlZ&V&)M9cmXI;Wjyv~XZ)Muz`$<L5iQ&*8!lb2Hq$%VWJil3(DQ<ssKaqjso?uX)RE1t9>i<(c)XHFK?LCzvCVkn+Pol90an>>r0%uqbdiYO}{u_BT>lpIMOY{lc$Sn5!6EO{JNCyygfqK+m{B2Qr`p1@E%mZ5kgLvajMC+l1<hWZFOhCGBCMIJ&P#!x(np?DxQk{ro>4rC~fZZV5!hT>7wSn?=xJars7o}56PL{1<lQm2p;$y2El$WzIasbk5L$>XUb$>Yf*s4?Ui&SeBc@fhkb@)+_&hT=HtAaX*yN2|`Q|I@$M|M@V~2k~A1Z2#9+-u>0B<tsn4YW?;_E+M{+`a5rZ3222k&}{YTul)m@5kg%'

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
