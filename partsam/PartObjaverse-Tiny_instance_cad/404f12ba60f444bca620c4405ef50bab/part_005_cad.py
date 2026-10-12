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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/404f12ba60f444bca620c4405ef50bab/part_005.stl', 'relative_path': '404f12ba60f444bca620c4405ef50bab/part_005.stl', 'source_sha256': 'e883120a185e5cef9896ac8e64daebfc653bd63300ca5e4dc99f768480a32f23', 'input_faces': 224, 'input_vertices': 216, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4397062063217163, -0.3972459137439728, 0.3717057406902313], [0.441436767578125, -0.16929897665977478, 0.38674354553222656]]}
GEOMETRY_BASE85 = 'c$}r033OG}6^0LCh6;j7m@0V?APfN{h5(W@7pqKB2$>)Z@**S*M!+PDfpXCT5^U9?Nv$nDNMsNqpaqIRazP~wmSV+(mb8snYKH|>S#6;%+un2czi+co=vrOvTWhcX%kO#n?K9kS&%KhG(!52uqE9b%zW8tNI_{r3zNW&}vfP5A1#@x>hb&sMvYEQu^Yw>y%cRUlQ?r|?WvV!4Zf@b6f|v&aF^PF2V`2j_d5a5*3UU_BUR*FYSNmgg@(Xiazi@uel3e%i{&B++VgvUNhz+a>{Ewe@ZV7hZKK0eE27Vv$3#|>wOD-k5YCRb3`Kq-09esP@!S}TWE%Ke>Uex}fD6f6+#v<X{9rk+d)t}*i94YdL3RViA>v6iT625(^ihj3;;iH~FA@Y0?L3uijr23ELdcNH;Lev@Py+Zh0X9&K^>r8o`N%Y!V@68du`XZY0tXfWaHnbJ>2fkV-e6BwP-zsk->I{`Fmi}~%e}-&tUBUQglCPZBp5L&R`sM7kh3}N^q4t&JJGWbkel`3xU-;?}^(#1YE#)a`M!)+Pi`rK%p!VrsUiSQX4~ubTpZmq*W4&>U+K;2(4X#^C{?wbE9~v-&@=P2c{J^j=o^OvVpz%C=!}HZ|AEEqlv&jGKI^{o^P4l%ZUiiU5RA+D;twU9O#q*uwEXu!ng7DQY%5R5LzpU!ho^Rh1q;X!9ApF2@D1WF0jk8r>bGh;OhY~_GKDSO?7VEigyYP8_)y8e)N1PJ<3hYZ0e(3sS(Jy=V5%PyT?)j?A2;r+9V`+S@uc!WgdRWw>PVACCt}myn;p2L-Pw$|5{&|S{i+K#($`pQ}`xG&c>W@3A&Ixlxo$Pa+>e6Q6^Y1p~?4kUvc8WTK(<{l3-XZ!G3VW00WmW}^XXZ>Ahd*Qs-(Hs{)~EWsjOsa%E9+z*bq3BnPkx6oF^_ine&PH3VfsFrmw~0S&XfaG&)k<hzoE@6x-LGMA$)6iy12en_;_lMeW0Q5QQ`ACwEL0o+&7N=+J&^9PYoA-sBX5{_t;l0vc&$texRJzzn!#Iw#R;A4?ZH>V}A=SJ0^YXpP`<|h0o&?h>|{!a|7oYF@oBcJR$o9KR7uku50#rAK?9yeePF)uV47Q|MNKe?NPtgrCQd5`W^N&5-1PuM}B|V$Nf<)t`a`4bKCT>u6TUZ%Y8(C&g1*YZ&g<dpYu1EK40&g=dEZO|FC?T$DYH5AKV-i_XYMthqJ_e&Ci4TNN~e8;rsU^%rE=?el_1AzqT`t|0<&%_*M<oqjK|vZ{N%k_iMjB-`8rl3!m%Z`C^~1JDzvH9;|bF9@S}AUi@Y99qMG?tdo7SPQSfTC;Mid?3;Buo32tGV;<Qz=aGGL9{oJVJhE@jBl~>4@c20SzoYiXy7hf?-NxP$?frRS-?)z0H?Je#H?AYA<8AVd{e*pUKVje8PuMs26ZXyh#BXoxCw@J~eqy(2d)fP4V?Sr#+|SuJ_jC5m{oHSF?B{-aV?XzOV?Sr#+|SuJ_jCJC<eT?3_Rag6O3b46#(k6hCil&-X`&wg{(E(rsE6<4>^HfOpU$T7G0q9TZ=4gH_&myQoI}_*&mq>A^JJZTp856s%Z=AFpMUHV3uxYr^A-E%`O2<aLE~wh-`F?LZ_Ya_MLm3O^nK&p==;XGQLQVcI*s!x`{sGoy0($V%{ULU-{d@e;aO29pSRg>a^8M>lUP@LZdYX`l*c&#vu~dNowN$dV?1B5Z$4i*Rr^K1`1yr>^ZCWvet_~+(s~Z{nJ9hZ`N$e{oW=+HHt+N7o6m9f=T+3-fvF-t`<y>GHJ$Q&SR?ia|9n_>M)sG-0lxX%%6^mQ)>UW4_3PiK*ys9jy|ZsVNBix~=jg}IiT%ny55PB{-<_n3)Gy;bfND`I)*;U$`#g`lZq;Yxo9`vqH{VOxm6xc!@&1H;^Zg0?=KB-hH{PGvORk81@%sTg{ZmmVzvp4U$$Oq|S4Ext9*KSPJ(BwBs;m>f9eGWxEC2p=`<l4!_<D5euZwl%UtiTX<a)q5x6Vb@H_q=rFBEmF7wePnr!_t68;?)$)q#{Jqj$ZS$D4SM@kw9N-d=t$<tgbe+J~Zg(m2Eq67{HxPSVGC`gwjeSmfdMPWjOK#{Kp43?41=+fUcld3kD+WPb<NdA_nOk-wqU*}CLZ@%A$^`rO}Ddl%hktHM=YPNP?!-hWWa*E_%ZToC`?z50xc|9@Y7_Hb+H?M6?8<^V!-40HfE20R3MA9x6OICKPfI5-h%ffK=FpcBAjz!Ra<z!SmQ(8s{p;MoYxdC*+2)+fMu;C$$Ea6Whi^jqK+;I#<No1otXYkdj43H$=|RqzYoQs{PYDfmYS%@xocV6AU}E5N&;Z-IA#_d<_=_k#C9PlL6-1J?RBcptbDx(8ed-VNOe-VJ^oS`L04ycPOG@K$gc^kr}v_(kaR;1|Iq&~@Mvunk=Ww!tf*i@+<vPeSK|p9IfCXbwViz*=X3gW&1VN5Ip;DbR0%Q@{@*G$%nvg0&6<CxH{71HlR4q0ngXP;h^Q=3dY!@V(Hk&?s<Ma2M#;!Ck-+(C%QZ-N0>?{$D#v?`WPzfFsc6ZiME$ppoFa!0n*-fZKsvLOX%Ab^y17Hb-b~rs$)!6|^O|CBEAVp}94*Be*rV4YV^j4B7&rxjnQqxIH)=p}7x2b3bTDu-3lde&AT>AaE@BerP;c>u9jnQQ%nUV1(v4=qPX;_yL6GWQ6AN(9vM6<G|y=X>O!Lry?|GxiJem8JY%8!*?emG*5z#1y2G`fj$hL0#1c~1FZESu+~Sxso)IgOt99+!KqNruQ}6=xzIV#3~&a%I|re8A#?$FA^0iiV(?SoLTE8q>(gMZ8^ML(BIq+<t=|S0LOH+Y0ymaGS3`@yMfmP&gyuES_24z&rO*xFrQl@<&Cen<e+QxYIp}(@*3IDOz+0f-18)Jp0{uQ%>uX@GA@D2UA0RYuLufvL(0ma38d&RL@IkQS#xdx-2+i-iaSB=ub-)h3TaD0M1w90=0w0I|7<?Rj6uKX*^-ZwWpMZ~oPeM<Cwbp>oy78VHXP_s+C(-5%Lh}dEbKnoa=b=9Zp9f!n{tT@3L-0j6e(uIc&<o%TX!8+5b1n2^a4opbjntH8Vd2gH(?1>f_s8}&`Nsc{!2G5>b~pa!Kio$CAv`surM?fin|qjd0gVdizy1YB94}u'

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
