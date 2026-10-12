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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f222afc918e14e93bcd98d98aed5c698/part_003.stl', 'relative_path': 'f222afc918e14e93bcd98d98aed5c698/part_003.stl', 'source_sha256': '8cdbc518397bcd7f475cc847ec99ad43541db725d517ef1d0234aca10d370919', 'input_faces': 290, 'input_vertices': 189, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3295449912548065, -0.36360350251197815, 0.09090910106897354], [0.6363639831542969, 0.4204549789428711, 0.27274444699287415]]}
GEOMETRY_BASE85 = 'c$}r0Yj9Q76~|9_h^59L<^{g4S`E^OF;WajA&S9j1S0}P<dGO|1Pn<`u93I5AP-3hh)5C9VtCYAwX|qym6>Mz!Z=zTY8^($4>)5x%yg#HFa28GJNLJb`~LTF#<6#1&Hr)MURitXb8c?#q@jN3u;M89x;h&E#M=6r(NSdMqNq6PPIqQjG^e{Jv~{d0h(-<i_T})|+4E*KJXjEQN9!t<rMsFtE2g9>rnb~nRHiCg+B-9yO>IltJC~)cKeMT|D{cI)<xL%FqsQG`Gr2N#%MF#O4XN+>8fjWMH>2#6zZk4-JpBH2t3RqcJw3rs9nGBa{pg=PA138HKgd7T|8ZhIzUB}7uk@3oeCNCT?9#XYp8L7Eywp9pe$}rX@wdMw`PrtgK1$3lD$A=M&q3-tU+X(x>&N+0Kb~9Af6fp4&-r2h<ZJ)ObMp%N#}E3)5Bhic+P^zT?H@nrA3x~d<xBne+@-$rwZ8MUew-ilUw1aS|C}H8pYy~1$)|qpKfd}n>HbvT)mPuu5AvnH-k<7geZ4<}{Gk8*`&0d}|NQ$i$k+bm{!~BcU+&K!U;CH)Q~jWSxj%z^sjv5^`dVM_&mceOKmYzzKkPsM{tWV|9~B(VJ9qbftG;``b-up;s~_ac`@i~{ukZiryZnI}nKRbUE<W?AKOgnoeAIXI3G$hb^9RoMe3n$-`C8xkT0hRGeq&+Jhl6uillj!&uljDk&e#2_@A^^S^%LYvKe}J_wZ85*$k+XzI{#VXe(~eq@7wy{PnwVVny>RwKYl+KKYl;geE0hTU+1H~*4Oz2`BGo!qrTg3s$=Hqr2VSz`cdEY6Xes6^L4-KYkl2skWc+{|2_Y1()p?%e?G+5{i^T!QQ!3w<V!!gU-h-V?l;KS{mS{OAHN@VL<33lQD5_QKI*&v)pz{|`R?}xzRpK|t*`S5@}<7cNB#JD|5x3~#OGc7_<0mRejYX7J&*Xo^De&D51x0;cl-T!$?J*dD}H>w_`&&#AJ1R>c>bC%{RHPLzSa-USMznhdcNYv`#szBa^if%*Zg2U;>Z1qANQ~Mu7CVsKH_WrU_P2J^@I6{AMZEX{hw(``xQU#NBp=S&3FCa2m2LY>j(SQeE0dbG#Z$maK7rh{l>n`NBube;Q4nG>pNfTh#!B>%x1o@c<8RWv-TVgovAyS<e#g{)p34mOzv}^^P}>`UnbR2U-R?oG~|8j^ug@YpO;^3GEMv-Dvny3ysw<BIamfv{>o{^#P9T#Q}yJk|Mx4W6Q+khn)n0w7W_>U$I-{}EdRZU6L=@^Eq~R-Z|%Immp%SFw8f+Fqv#{x8}L_I_Xc<b?$#UvkHB9s@f#B_fxq(j>u8II;fK-v;A`+#Soa#(4|i)`0{h{6O+05}2iW8B=g}5-!S|#0g3rNsq5Hu7@V(UA5B9-(ShEA{gYU8Tl8No$(;ojN+Tu?5KJ*^&S@=$LFSrlBhkE<KUij0j*$(!?51M$<#BT5zkN+BN@dfxX^g-}N_zUO*;4%0?>Ky|Qz@K5wZtwtn2eZq9zwr1jw8bs(KAE#S-!15;y!k)HwJbV|*GH`_cw6wZ%*f7eBlx7pccLwBhWE;x-T7`tZ}R59iEA6t8}WLnwHa?SzU3JckDFKtKI-u`Xp8Oe)#wcPIJ_O*2Cjx@sJ9wygFniem0%mZ(?pkv<=_gBKY_Nm3f_(G1iRp?(5+xMypwv}U@LqDYnFqp@bxA(MD}BE4j=RQHnhcc@U7_e;0E|Q^jdH$d_DEHf@|TAv8DrD3t!3X8o?%yx1%kl;cYT!cfM)#GH?FNxYmen#A~Bg8ZV9C$c*glmViq=z6x!z8Qv;$cIVrSe%PD;!(3Z}UV_(3t!BJte9PyWm}lZ1u-@YjqAlJBUx1zq&V%2Fo((R5&!yf1a5j97i3d#l47}UpKSx`f1)q<e13mzsg}xV@51&K5`QW|qMJ5)TXaMi`_#<eG55Zf|i@?S3htLbb7Wg9SwSWuZ_p_z}TnMi)@naJ|1dHI~(bt0&@FMiZ;CQ&bHWED&Z#=b%@QUy)zs|%Bk^SJ6!$SBt^pC*n;DzXmz;SSU?Lzd0c;l#5h*yYj`2-U;nHUXT>hW997R%t(=n3FW@G^8MSPh>*y=t%&ekp54gQf6F6E~U|1zzIuo6#0a;8o~K@J4tEx)`j2S5mJEEQVjgno(deyw=3+QSN22z~eK}7Kg&`K-Yq|!-t}WfOo(PxE6s!;BL-to@E}t6>ae{_#|{S=+59W^jL5b+?~%Pa4fuxHKpKKxSO+^XNkvug0?sYJ`r67x-%GqE(a&V-T6!e%i$%gDF(~oQ%u}u;!5x;k55NiycRwUJq5fCK81DDz-!=FvGz*v8hDL~$tErbukiR!(H5_UPes>&li@Y2n+m4jSFrYSFa^KUM4gFY;Bb%Mg|;{XJ`;T>SO*`0z5tvFAI`O5;05qMnK)_U9q?`VpSgAld<Wi8UofP2=(qhV!#A(&;DhA<V}q{D|8vw|*==gYf1Ebd54XLV2WQCOhmQB`#G<bO2#jGy'

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
