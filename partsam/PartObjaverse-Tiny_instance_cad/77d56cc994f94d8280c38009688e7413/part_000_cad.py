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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/77d56cc994f94d8280c38009688e7413/part_000.stl', 'relative_path': '77d56cc994f94d8280c38009688e7413/part_000.stl', 'source_sha256': 'c558cce04015d281accd1e2e295de362827795ddd2c1111dee99bbc1d5947b0a', 'input_faces': 276, 'input_vertices': 164, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.19560569524765015, 0.02563243918120861, 0.15750467777252197], [0.326294481754303, 0.20557132363319397, 0.19316205382347107]]}
GEOMETRY_BASE85 = 'c$}q~32aoy8ONV-2*qGdC*cfBAsAB=cEJV8x#ma!12LtXHf90aU;@VYqFnAmIYYu_Fvdq%a6pwJ1&RvBm}5zTI2zJ6&@1#XC`}Z41RB(os4d-j^Lx)T6IZI*l}7*H`}^DPee=z{v3H%C68%J+C0{+Q3BID64Q(w;jMi41Rh*Syn6oIW;Q8FV)lpVE+ZQiKOQ+75k~$~KDz?_fXJ!>F%8wuBi64<YG(OQ2pS>c#Fn>Yr{1y3`S;Bu|!Lov^h+nW|L0(qmy033=Qle*2LZWBA=YM>~L`n!&w!C&RqTv%UwWA~I@A~e$qnq+$@7uorv&UD39~_vd#ec;o-a7W4?T4?;JEg{d#V0;ED`@+H9@(e0Jev!p-*K1b`#X7UKh$-dUXSTJ@r(PP6TaVj|FF0Y$2@4#w?6N7S!n2vNBX~!et`U@@7DjQh3$t9j|-{!P2b5Mzz+<lu2JJn---8M|FT~A4gZvRoO(>(sV8(r`r*e_HLCBKSZVvgKbBRi_ceXzzK-8;FYahl@s97rTVr<0Jk!dn)jCbz?OQkLTX|0%)z&NJ;aTB(GEQ8x<DB&}{P16?)A7@nRBCk^zB?~`tET_4rs5snU9TIT*nYSwr&67l={xl|T$a8SlzE(Z(|6(nzmJ!7zCXG`+Yg5C?gxD9-X*=x!mhUOFS?}N*Yw@~50rkxBAMTbH+^^iba|)FzOT`Lf4d8|?@36#uC15hJMq?l`no2cyC1$K<MSVA&sW%YK*k&SP2b5MC@-yRYM+EkrpkDu&!+FzgKze^A$p9A|48q%>AUCH+sU>cPWEekHhp*hbl7;Nsr~Hueq%p7zPX=G-;DPg&zI@D{rs@V_QM`y{~Nwr{|C~y#u)qG@ZEiN<94m^1LnD8`0n$IA2!b=!*}P~`6ssTpRAutjvtt;pG$#<@5}h*@?3J~YxwSbyREQ&^ZYk`r=BprdH$Qe8=t#S`epk0Z~E@}xlH>0a(Vu{zb_2mt^ciwwd(We)^GUkb8%sW?R%0Q=)WHg-(BCwJAP(gPwIBg&eJ_X^8@(dAzxgv^>Mk3AO7PyHQw<9_)fgP_#}DKE~xR2AH;X#``omBPkpp@U(c_8DdR)OYqdHJ--);W@mt#ue;RjI^Sgg;`_>Qcp4aAer^N@h-sl<D=4JS9p0p0OAE=mq#$FGn{-wQb-}=SJ^>*L4)m^o(KS`8+Zq8ZN59SZE{ow4?7u7tTnIolteD--QPtRm|-}N!}-(4Q+bo?N`HB{zlm^(w>_hg$o?Y=#h+P;7LLoMFZrqK2qyn8RG@!=~QWd1ka)B9uiZXf<oF7t1*&Zv3(_YcYXznrAShpXO}eZIE*q8cA+aaH<V+n!SAYx++8{(=wXd}DiQ^YZWeO!{>ha-TT!+S>l6UB}+em$Z4|Tcy%>>-_aIwjUn1L$Cj%XKg<i{;5`f@YBIE&pTV{)%=d{!FT)fm#H%U<q=w)!T6an|EVvu`36$bWuDHrf28)u@%{Mjei&6E<F_2w>TH-_D(gI0q|fWoQF-4zkM(uO58*rUq0BdB{-RK=wtw#4kp7-k+PZ}Qd`tHKbgWiSpw*vbJ%20I*4^<v_)Z?{@*~?1%vh`Kw}v~>x9p$aZmrcBJl4tf{kQ(5Jzs%_MB5KHY|!Rw`tCk|(<}X5r?ltG+BL}b10V0J)#AG(OTW__=d?PPOqBJU=%eq4V`;bK^L6%u*5@AC(yzI$odc%t_UH5(*@xfttJCUfzFWpu{r#NkdlJfIJ+Eh6RQq81Zv5>EnSWDEz3N*#>Sg}nC(o#POy6CXsGr+@D0=L9?Rmiu<Gb}YyGx!2XVrMqx8qZ_ZwKb}D!rE%8~KD287-|iD|><R)qpU?%h9I48puiduf7@>IArku`_+IbLzLbeeG+aN8P7$=*U;W@EI)6JKA~_F*HN^>;b^XfHdDAI*DcB2j9eYKPb}OK?F@H>yP#i(yTHBBZ@|6aM06OO2oFccz{BCO=p=Y7oPvHEPJySRv*GFR9P~Tz9C!vg8J+=8LC3*U;PI?QKh~o+oPd4{PJoA^<Kgk-aoDHi_bD~_lsbLNTztxWeM(P!O5c1+Z+%Mteaag7ly&qeYb`jAA-F5U$Go3|`!RgX&&PZOi@hZFRtq!=ZUH~Z5G?j=a%3b$#%PA%A!vVi2;A2akGItBXn#1F_xsUNaJR_t5aZ$f-5CS;xzOho9>lfKfeI&colNe5<a~y_J>gDhJGc|v9*u$9!>!OZa4Wbi`V`z2ej0riej4t9_JMoA@#r_<cz7^60v-&HL|=eM!Y`sz;TPeT(3$W{@GRD1BI_{<o`6n+C%~!bEO-`q9QG>ty-E#UrB1Ih7q2p3uhJ8*(l@WtTd&f8ud+s7WgWfBS_|&W5bW$#uhqDpz07qYJPn-%i@hZFRuVb@PJ;V01dBbpC^B*)BY-Y}18^q#GMou7Mf2dLa3NX*7sBh%_3%1)Gr9@h4DUo=fp@}X=q|Vnu0Z#}6>v5467$SO7sI)50lES%fLEj6g;&EtbORiOx1rnNZSZSoDf}9|7d;5?h4-V?a5Zz;PkwRl?=u9iVhCQ2u7H=r3(>{!LU<m!2o@TE=fP=cCY%P(N0-9$;cT=J&W7_Dg4d$!V4<7gweVJk;63P0SZEo%2d+XZ;41hqy?T}YZGg9<<?wd66g>o&!Uq|LSQDW&a1HmVMl0Y2^g11#2dBex(KL82oPo}VGvF*V8_t4PqWSPjcn!K1UITAIx58WC-RK^8H(ZHU!If|bJq(B7Bg|LKe>u9$YTT28SE0pL;~p+%t%Pp08u$4|)=KCO_*J+ZJph-(htSvILvRgx1U^E|HO#Aod6&?a-Slk>-b$`Z=>JMMgX<F3F#}HLx`aNY!^^mKxP*C^FwbJ<wGr<C*Co_{06xNX3H68I5I++v&W`U{jpvMD=PVNJoL7Q_48hL1C)ha~1v}@b;2ehFB@DqYGX&=`1Q#&`uV)C}#1Q-nL+~z!;C<+RI5j1zSzPpg`d4n_D`<a+QU9@PzEl60r@r&q$RAnmhrZO5=Hl<o$cLL|_QGEizeTNo1IvRu)&'

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
