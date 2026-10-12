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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/053b8a4984e340ad94f3b563594ff09d/part_008.stl', 'relative_path': '053b8a4984e340ad94f3b563594ff09d/part_008.stl', 'source_sha256': '65261c36803fde63f45a1006cb1952c7c0bd51492cb0b593eb702f187edcc7a3', 'input_faces': 162, 'input_vertices': 185, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10884334146976471, -0.15031500160694122, -0.22028197348117828], [0.1263389140367508, 0.4025064706802368, 0.2202719748020172]]}
GEOMETRY_BASE85 = 'c$}qK3se@z865=T1Bg#lViVR!MNw&dKN4|8MX8_|Uo~lTQNcGTAifY*tJO;Jg|V>;t_mto6-4n>7d5BRND@g+s<rx?^u*TY#Ar@i6JyeuZ|>6F?Vp~WmUHg8ckg`r&CIv6J9B>G$NKuUVe+pd`|X<Cp}%j*m_Q(F!!i<6)91}fOp8cfyuydIAYc4hoHuTAT>La2mcdqq%}z|4l^Qlg341wdP*_hTEGZ>5JvAYDMoQ}JMBzs#EKEz}e%joG#fkj7Tkk>rdn$dq_f%FZ|KndXJ_NPfAJ3fUtZ#^}63l#84<9D{uD_`f*Gfn~@|DxM`-RV3KKuH+eS*y^TTfD+)(1){uCdIc!#9hzp0fMwQBAd@-=^@-NuS+%c!sW{>!qI(BmE;E%KTG0pR)UAS_xgNImS7`X0kJ0$+$)1){~v_TIsZN<lifyaj03rXDM%^s8ba8U{|GmzMiizUze|<K9<kAvMm%hI--#3;PQ<P#)0!TUmyMHK^kZ9@FH)%e*N7d${&+=O!(T)PO@(1{7Pzv&swB!ru=aM#~pr`fJ0QD2PM_St~{!zGxevs^DMd~`*G#bn$M;>dj2x9!torN%jal(;PPYTbJXCoCU0)B`-&C+_yWz>@;&v4?_FHw)wkA(l_!5-nYZWS+2i!B=cs)<fPD2O_%~&|;_~(WKKswxd{*R7<5xcIMbFps)ae`QK6<_l{<eEGFYRGnkv(2reTL?x{p~E()o{ftv2s0FzS_-?)~E7SX))dB%43dy@eqw`aC9lHzl08NQGLeA`WUsr(!X-&1o@NayhC;HTrHtI6}>24Nxe_wH$11wH?w?CQoK6<9qM=cXN5Gs&pT3mv`^&vQQ)%?X|#UK&o9clZi62lDA(cFv#RaBdAY7i*5wuYUTE3Ux7MeEb*{i?E#>+&vCchN@U8WUb#7$2@?f27S<XB<*16)!qhg(#6`2Ke-<c;Ds1B24J=N>W$u|x^CEpD3m*0V+=kqBq>TLG%yGYmYwcVM>lT>T>*~C(+zj^kO{BC|cXAiYo^^fR&kr=*tJ5~1EXKO9J?|0!3-bs1XvZxy3rAgb!AOFHBxz5&Iru)*JzFrqD^TXEzgXmhDT7R0_Q=ReV!p3r5sm^$HXU=Jwk2`)(!ezSNJ0Xwq#onO$sCRl_rG5?Rt2dw0xQ!m6SLpe|H+F}}`PTUmtNWzyx%LfRd-kW(_dtWMUK=Ot`Hw%<$aZJEdbbztf9wF_Lll{R^Nm`Ee}9&IFPhAueME)Nrd87TmA-wh+I?&Mo-0pizWPnSvSHrp@A9qsD}Ru_RZkuDXSba3R{bsCidRs7#T}3O>)Y?j`1=tT<+yjzK54)=B7#i1Klf3E-Pb;vbDr-1HuMPPgKsJwX}@Gu!;aZ~wmX^XWh|KD@YT*e<o@PqRAu+|&WW_osJlYs_rUTyjiK+azN7NE-DefM4eB@UGWjgeIWIFbkiK`8Z_P_<npk1?nHtbp`ZMJ7%yZ7yvvNDdt9j1(8V?^Iwfok5J;lxC{+j2UFAF_eY4@%9njh86dgM9hYt}C~ZuhPE>N#u4H(lfRjBbB|#<eE6oW|LBpnN|M&CI83_(oZ4s)Oh4*A2VRK1i3(_vAK*ufNt?&bMdeen+0`S@Jwsut4s!u6|8pG<}cQT4%p3$JlH4t$x*heul#j9VE{st=rQ+Yx&CbrBpX#-6)5zcKRLdTW0p{BD>GZ!{q+`FhK6BYn}5_i;vQI!1Aqmna|yJ_-x0<<#hd7q1+!_<21KyqW)FaICWM-zUCUI`b~V1-M7Zc7G=qEpsQbVZadoF*_Tmroa=|mI)4#5+ndkA9xohb^VyXSrrlRuzLm%F&7k%4T+AnbPx9ugL*GlG`M}qwMxL_AyM1@OdM$_Q%v!xW@4OdZ=`wMNJ>Hl$rqWxy<-6mRSJ%q#$=*k)^gg@&CP9m+&hWL4TG4;>k;n2qWmWPyMrNj*_u^~e)6?zoEUnW<Z}FCI#d|JYlYZttx$nKdgwB2DTTWkT-s3FQqxQD+M-IrOxW}t$eKz<RpV0Y12@jI{o-1Bk`o%%&AHJIV9rdTxwWEE(booZiCOQ|g3-0`Xu9bC)rhS8zOrmwG-deVb^0|DaHeea87x?CskLCIHdweU8`SyjQR9E-8=(6<P=b{E5=OP{FB7Mb|GLQS52LIpAY4ELcnvQdtJ|Vi=J{|?<Wb<NLwLQOQl00v#cY2tV|H%6HiJw_T?HYVNf5dy#&-K3!xBKkTJ@U1tBTMbRnw?(nE#B<9iF{9deVN05aE5&4PHm0d_pI#jA?3-<F8AhZ8=J{<plduv%n4c#x@%rW*M2ALe#3aSjx2Nd7?1Yd${M@hFrK=HWnO*Ew_!X(R^71AtHJjzzhSR~<?AIEZrJk}uKecVi*ny{<+sLZxbus7#XEi#+R!U_X!|CN2{dJGSW<%RCm~^qKa0KpBs8zzfA^EnfIk24PeRY|F?8n$0QZ1?j-wMt2v~vs0mlzHI)J-CM{soJ=mqWw{US#<jvs-$LJ#B^#PK{h47!kG5=R_(9Q1yUiK71CSD?c=28+i8ehGRX?kNNt&_fV2790y52QCEfgAT_%abSCFEaGC(htQ)qqB#zL$3wr&p>p&D4}&h?*vl~*90M)x$wzxW+6v$opq~Q7jsiv_r{JN`f+L|LF%Byx2JJCu6FQkAg<~~Xhn~(c1MM@=CiFax`5cqMQ=qdrveBN6HlY`AEaaF9{t5J2j&*2Xhc=-Xb1dap1O6Fw0>@0W&qSNhvp8mRWPq1LXF#t9Z-D+e$3~7t;3d$Dpr?Ufh5iM{FF8`dY0#<AuYrFGoyd{Iu>!mjdIj_*a1Qh;j!ceR@D}Jf9COh=7i~f><9MAT9a_WnW{$1!x1vqx?Hq4%yaE0d^c&E>2JeQ><Jifu4ZH(-7snp7??Ic;Vx3N4a!m;y11;XQ5lp@-f`1Gx-q|R$N1;t<vF78EFCMvs7Vn<;CWM1WLW?ym-l<XGXy|an3<gI*8%%yf3c-`0#d|QE$@fIC3N7Bd@fg>5j42;;5OdiNo(LU-xkrMBL-*qd<p>6Z4g|M{4utmSXvHD6me$a{aV@wHbQ|ct9PKy;Ah+QDw!ZqKf06qI<oAaT0{4avf);%?<`CPJFW3*-7rH698FVAefr0&@n{%|_XbWx!%@E@Q4uWotxjhSR3Ec{9LEvYh1JOq?xGnTSj$)2O(1&qd&QZZ}1bh^_95Dx>kKkI|U&2uYU5x8ejw+5a=;OGq<T%Dr4X%Mc0euYmB(6(wkGMa6tWTphzTfw+rhonEqEL>1Jh|_59!KnVw&jIvIGn_f^%rLW{_q;n2XCG@0kD4pHED5>'

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
