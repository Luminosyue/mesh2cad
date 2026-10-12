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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/423121778c4b4e849a029b8281c68bda/part_006.stl', 'relative_path': '423121778c4b4e849a029b8281c68bda/part_006.stl', 'source_sha256': '95f2e022175416259d009a1a96a895dab4fcd1291b737dcf6b4097fdd5b4a0c8', 'input_faces': 146, 'input_vertices': 142, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-19.59832191467285, 108.45843505859375, -23.3806209564209], [19.8560848236084, 162.25352478027344, 3.0668985843658447]]}
GEOMETRY_BASE85 = 'c$}qJ3v^Cb7CuRkc!Y?=BZ;_PNk~ZiB0@Z_b|#W~G*OQtxOqx6kx0;Zgo}DcT9&3{M)jf;HE2hbviM7>Xw9TVy{8vtyn<qRw#+%--s$M9nYCuk{8@YL?|k>1efHUB-+j(aLO-_}K7xKN#q^Ia-mUNyLP<U0BPOTkPs~b9FX%WvZ;FfX0<V76dfC7s0}_V2h{<AFa9VmnYJPBcEx1QUba0p!oROP9F+X|ynB4rdbj8OeXBVVPz92I>FI~1nIz>9dw9f6qv?A?){MC^zSfOQ|ol-kTl_cv@>tCML&>mR?-X7zZ0=~|OR;sPNTZ8&njzfQ=+q@w3^Lye@+C04j{mqd9Ug-D3Ch%hTR`5n>#e?3;&Xf%BR>XSZOS+N$ZMDGbagPkeYb62T?Kxj{f}LF-V_x(6)iCs%ZGboTxRC#O0|PPd+A|SK8-t@#VZYeB0qoTJ5WMwiFYwlgX^)jZ&L#!mwV>wU#io@lF`subc;_!^@Ka0MM)Ush<qoj7v<kd9@Vq_xFD?(obEAO#>6?mpnMcaNn@bau;7_MV!LYk!8F(YK61?^FKnU!%{~q@AoUQQ341Q1-ey{o~c&q(p@cQ0{@ZVhe3H2}c83R9e`oq4S`yqJe^A%)gWCr$EdlXCjn>4Sve<s$W`MZ++^3LG(&0D~mQRVHhzVCu)y?gU%zuy}L-hT7;NX%O!4E}3XwZU6=QbwVF_=Ps$d)jzztt|lWynYL9<4PH{^R8nw`1~07Z@Ih$UaTBN`!y|`{P5mM>#Nri{f&(`uwUkd?KE!ZxA4b0{yoKg(KPVF?G&xcFRV5E4!IHpza}`bF3WR61nrjxcztaG{M2?m!@k?j`EAkv-A=Hho$HTvnNteDo7w9qo?(t~tZVuKJlEGzJk5!2;KfH1Y22Li@KZQWP+paH1#fJ-K=YPdLj0W-O~6}IO<J!@WB6&`aszK$H_+dh9E<(6OWvXN4Ub0LoE|wHG2hAuc%O`lQxu;g;fRZN<nQ3cxd*8<?}+9Y|K-=<t!$4p^zYWe9sPzKB>uDuc+t(%1>=MVc(c)cTJO;;%xm;JhW&Ad?k4-!rX#*q!!z*L`uZv5&y|6cmv#1l7Y*{r&Xu8*huceAz^`Tl@P1jP@lo*qL~Zc;gjr-iKM?!wOc;ZDU>p=F=-=pkB*t$p#QOB-6%@Dm>Gb~3bp&AC{$ub*AF&<#rI+6Dhd<2|(chXq2E3g$0K9p0E!kiD1=Y3HLE!b&MU-!@7S*@Ap?(<WI0@d~cboDv?qD;D>tOKWp+G)Z%ZGs1&Mu=o=@?0QxF&)6FI_<O<ZoV--`?)TC(lEF+iMo;qi#2CO6#~tc~u+;-l~70G1lu%@weU&#QUZnUjSa8)syVxcBcHfQqLFm`-NcN?SU&?F)s0(5A5~nP4Vn9j`H);cJM~ywv;E!KgIerV=8!Ye;E0HPf&jAy}|2O9F%Wm?r!Km?4mdPjJZX1VC*b<-;7h>jlm1xr}04`)rTZ6oIlp)Z185bM(4`sNuGG#wjss;c751!-d|Xc;@_O?+_SM>akxn>jPod^`t1G?>k?D?xPWitOZ6>w5AmUu&-ST)ua!_fH}j=)t7_WMiZ{OLOYywyOZLD0%VWhmvkPf|)4b>$@$rACcyr!$+83jH5cs>Re*%ARAm!DdRWxtq=xd7C&GpnjU>(`n=D896^ogPU3OkAS)QTHl*+cnL_=Ng5*bDo{h`bYuw{|}!{^0vme}#Utml_`sNBa_d!-e>(ZPoc>zugtQb~4eA_>cs}i=KDL&u==CpCWpY;tjn!-5>IjyAp2<R=mFC7I=GkMHk`&hA7^uxj04f&H+>D{!w_@8}S;+`EZEx!AkG#gZ5?4pU-L`f9&`j;B9Zt!+6R=D|IJ$txG$KkF&q4(&pAz{o!B5TFh&`L+`a%o*W224pBWZ9-c!z(Tf|kz_`U!f2`Rp=)FF+9K7)7dX-D{N*{8nCE`+t>Y?>r5#n$ESk?;d16*(CuKWr2lUs+ui*d}K4@DiePu&2oea?0JFx73X|FYI-ujcx{mFmCYxEzFe<LSK94tzxKsr$ST@EiG@T}S7vy`j7v<}Igl-z=hYU!?!3J=%$7bg#HE7WLY^cLuyYh3_pB?&IDf-U|*zyXy|RUuDGH!96hT2zV`-?n~lP3iek!t9O9kGx&ZL{tWr7^~ev0f03WzerV}`Ks~Y-`b5Bf%h8lSp1ao|Z|;W^|4K))b8{;4U+jAsymn+G-6x|vT!lZohJqLS2hshl!OctR{jrY@2k%V#f%rXb9wJ}m{Sf1Sru(7w_EywqGd_p-CjqqHsxq8^R^3V9?b22hf7gW`XjjbyuOC@W_CNUZel@SST}=M;qItCqUthz#LsyagCNI&xr&rykd*Dgp<N4nE*c10&F~Fr0=IOBqaWju6HiADh4e;h}x<5N(=>Dv4+D-hSr*sbwSknY?KJyiL{R_T_`_Vnz{3*?W@gaPl9~+JH&beq3c(aPuD=N4Ag1T_{BJn<-P#o5mUO*i={Rq5ug1;l``=gHQM{9Hj&)*$(?A##58}4!7^`uIAzntArf5kUh;LXzcRA-i?(z&vv2)vfe-!(DA>AsRV1H6&x0Pl>;x`TS!yNvqt_mT5B-B*l|vovpuuC(4qO}(87zxf(m@#Bi9*WHCsQd@ovW+cDxDX2*GtJeSiQ!p#?zx))8`hPzK6QmDAq$Em-kkUy?PuATTN3d?sx*Ov_)=gQrVyw=QK2qXToVXpw@(OcG|DJIKk8k^eU4=b3q_tSPGHxctPl^|7U&f84wBhk>*oMMU>_ZG|ov~W`YrKA?hcfoXHVV<2bw|ccd5sNNw_x0c<JFdR1Y`9)g#A^zIpfAW&X=_p<9I0prSxO{D&qlChD+(sdJyAY9Oo$3Js5Y9qTZ>ltY2mvB*kA!FzZH){n#&m*3B8uma<67eAbH@zab?{N-ATe(^*DI$z(l-aVF!jtVc5*&F$A2D?N;5Fmp;9jMZEdcy6V~F|M|i!P;OvMM{p88LY=MRytQo(F<*b=kb^sjOTD$=@O2?9DY{9qHr<mxr~b$za=F}O0tv`DI>X^!ji_E(jypWOUdKsdHgJe=T-9;vYyR2kH^erUC4MW#~_#2H<ocG<MAAmOvdSqa~S7vybIaxIL6~R_7m8rLdMl`%3=Hl>j{kKaa`xJE@G_8pn9)eSPRDOqy$Lm%sTu9te$zY))>DeC00rY)?tkM^4L%*zvFf&KaXWDjCClB>hHrkfU%N>{JbHLQMj&9MV_A5=4aJdJ#%ASld;-o2k*7gk&K%#uFu-RxE?=qXI-DMT6Z*a(LAOaCviK8ZAWs9>hgN(vX24mXC3xiX>Z1Lc}z{#^%&RTF*R7bF`h2vO(_#uPh~tw$}}kjtS7&KC-JyRJVxP}Qu3wDVr?>3wPzu>7cy6k)qA*rbur_FelD&)ZvW|DwEz5>D%pPX58Hno`P<|C#gX;pX8d}%C-kd{bIMizsia@6D!TXw_w;lX'

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
