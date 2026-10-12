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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5fad3a288517425e96b5cc4a86ebfb46/part_000.stl', 'relative_path': '5fad3a288517425e96b5cc4a86ebfb46/part_000.stl', 'source_sha256': '45026a4cf4a32a57fc9f4d0ffc0538377463062d9925964d4d5f4053937476b3', 'input_faces': 170, 'input_vertices': 139, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.34685060381889343, -0.3468506336212158, -1.7881393432617188e-07], [0.34685060381889343, 0.346850723028183, 0.15587806701660156]]}
GEOMETRY_BASE85 = 'c$}qJX>3(R6rQ&1V9Qcg0k5)@LRs6gR^A2KEAUDIMQnK$UZGH-w(RRIh){o+5LPvk7f48uU;JQC=tU6%RBaKAF+d85iT@R&|D12;n{waunize_$(i$=bLX6U=FFM7FIt$^CR6C&tK!nHX@v)05(3mkWQxu4>WvjE<29q!S8YoXT@{X>;fEJ2nIB!2A~uU1S*zkTE3306J6Q$g6SH!htnv-j8>`FKuh>w%Dh_;BS!GRJ;x%i^s^U@}Ha2%sj+2|6<Lq+&<FAtpp}Aq)kM)RU#wTm1>ZrWy0o?!di}ec6E4dJn%=ziiL*UIzohpT|J#}5-U-nmcthnl0ePAAgy9PJ&5N}>wbuAKNFP0Feee=<M4-~%Q?A7{!UxWLxvsWVl-0k=C55S%B6Dm&c(S@&+eaX}Nz!Ob%m+M1t=Rw`&NC5YCJa1C|4)(bljNjn?0pg6`;BH-?yO9uk&)_D{!%iwZQF*F{`L9y*tghAg_`^E>?|=JR<!wfd_8VP(CzuC8Tr66CCzyxC+8d1ue{}0YePI4Xw=)X&qNf#Z<~O)od|Jm%yty_*;ZEt&+evvN?yXpQJD4{=dZj_dpYc~x{NC|eh5IQNZwBKrxR-YEW+Z_7U5mAS{*jx(cw)r8ydyV*@jL5^?kT^={qteC_nCh_I8VZ?>(1v*%5Sb-FM~S<mlc3`V#HhOf^oLO^YuJ#kzOZHu8*3hg8PMd%et-8xX=8?_GUCHd*(Ai+-JVUV~sn{3$%UCGe7uV{_h%hMm+PA);Cq>J#nJ8Ay|hValv&^3Ot{$^Xr&=n|u=YyA?Mi<<t11e;arHD7c+eSL_Q3x$lE{_HEp(%OZ`trcapqv2o_#W50+U+xH+T|E26B$Jkex|HOUW7h<JP?+5eW+^BKWCtC9VSnn%$-HpazJ{|5i&+I?u(=XEd&Fy|h+nf9>)VSGyqEX}Sr@D@v%A$M0yg96IVd~nfd)^%7Uwq5H&O9U%**Y%v@0NP2|9nr9J@YBX-PsLp`lxwd|6J)#RqyOiCQk2{?c0?-_kBzJ2ZwJ_{f2$c<RS6!yJ>13={LB(etL0U63%*XhkP?u%_HLvuA}=TXC(SdEc;|rF#pZx(hGnmimo&S^DO37&jRkt_X@7Bcj;kF_1`tMO+kC)ITDg*tV<+hU9gUkkafhmM?%&ebrK1w6Vz2Cq^?khsvfO6MBRehb&EPzvQ_8U7s}q+7uZM2ueFa7Hg5WJvBvFv+HB)oNAv;ZC!{~9c&+~6u<wWUAC*_D|Dca4e^wt$5V!jt`lOoA>XYcJDnC|VMITmvtv>7%xBE8wyppXx?-IAq1)L)a4>@0w@cb9&lzKko{8Ij{^9$#o(ubUnYJTf{#5t>E>zwt8+vhUQafOGR?@Di<?@_%!?Rx_56}o;~-#2vqCf_%(-;^A3pHca??lZU->2*rJ7x~29Cwl)GT$pvT?pF?R`#y&IoAP7b-*DekxP9N-!F39`XR7%_?wKmikb9=$_C2#i_l2-~uX+#b-s`eIwz@wbWxoiyhpRZPd$_~>ANF0K*QND$ftoMmyFkg-cY(w6!2TY=_lw?lt-otjoWbv!Xwp|);h|aatsR5_b(CLm<z<0SIDq&W9{veek@xRD;U<jvzn^gZWDIGNGF9k8jFmJ-QU-EE3}2gVX!n}Hr>VxqNg71Vm6S`Yt)z6$fnPgfd6H(*$9PGziA|O?kJw=9;d?0cz(!IJtOxb!91o>UAKDG2&mOetKpo`HlKN9lp$@hkIZoxc7j4_q4)5QIdSE?i*NORPPn+Hxcjve#Z3Yp8Z5GEvB<0X9i}@Qu+k9e>C(sV^RO(<Gp$_siNmD2zf3vubbD7@)^3fcRW*&x-@V>8*_vN^oq=A(29@&%!NE$_X6#c$V{szaTlGaPwDd|H=b&@`oR3vE*<BQU+T+#~amPwjH-CM*fB<+^8f&3#$+a+!0coXG1`rJgH6`b#FJ_mVCAg2BF4S5IsL0&C%JwskfA9#KjeLy}SbS<NXmyj?<9T$@q(l>N*a_Cl)FO*cmn4sT6iqoc=yoCOCQNNEIdXM~l=Jx>g`>3lWVZ4zx2PN$#hi(t~Hc2(i#eUlCrTzob9@?y?-BuEG?~zwZdY8F_-6~0o$zijI95z#F2YrMb`f20~gszpD%;kLM4Y^&;+$`j{jClZG$M>z`dttnmu|tkAPRQ>tmP(G_q+f8<^K?lggzj_bd+3AM>*xy;h2Cd~agxye4|c<a?w!z~o?YrPh(q6&^2?IC3jG6?Ngw$23;4uyj?nuX&!tm_z6)c5??IH|FPE~*T<6k9J3cS?9+1&%XEWF6weu)XX1*a0rX6A!N;}9SX$QFn?HrE#&=$NuZQ-v2_28YU2k%8Y#Fa{YN9xSD8|~WD2DY83gWQug9hr;nwCznhGaf)&<Y)-(vZ%v2hc>;LyL{S#PoORM6xt%k5$eIGQ4c<yc4L`i)XZGwb}|XM8BH1~Ui9exeBWMtufF7neIPmF%qB-HqewaQJB2ZzrlW-^shMg2^w;x?pNGUI{Sj?HnS9*|K6y*d)pGfX7PiHj%f(4mO=26~MEnhRJ=75'

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
