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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/238bdb0c4e3e4432951c31c85a55a9c8/part_004.stl', 'relative_path': '238bdb0c4e3e4432951c31c85a55a9c8/part_004.stl', 'source_sha256': '0391d2aeafb34ccc7fbfb2ca2517468ba4b2a6953c807bf93d3abf64836f7b89', 'input_faces': 248, 'input_vertices': 233, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.41153597831726074, -0.4145633280277252, 0.00967457890510559], [0.39356690645217896, -0.13714170455932617, 0.4899284541606903]]}
GEOMETRY_BASE85 = 'c$}r03shBA8ppSaI1)atgXSain4^HAf>2{vdNVZ>AJk0dGcThsnyCm5XuhsNKGRY_!5%}t5;Gq&(~ON;7Zp%}1my~f!nHK>5m~de5p*^Cob%u3obR|>Yu3zN>s$YyzxA=t-us@5`<_K?OcTE#roXzf`>8W8k88)6T7fKxrNk%An=v&$xzFsx1&vs1&8shw8KYks6+6BWOJNIxr^P2vO$v@yf}cw09~`CxC(KEjmlQX9%ABNW@v0vd_gZp1_sP@a665*5L;6KVhAEMuVaj6Ve|!a~b9i^``7e0*dbX%ila0KUKFH#8LyIeAo^{Re%Dh`im3p7!WVy88@u}1^|Bw=Cf74sV(*8O}q0D=3o+z+-=jITyUgy~A0<C{@Tibfe(yiWHFZJensW;ba>o?YG8{b&3t>0L$t>0KL_2znY@5y2G{T-e7rs~}}Kc6E$vGqD_e{$-mpS!q38$YLlc=!0cLajf0r)``>eVpu%s2`D?q0MKLn|RNp)FQ2a(@Z-4-0k{xH^th<IgnxX?z-NEGVlEEY610Q=s1%?vaR0OPn$RP6W+ZsjE>_Pdfe)r7cb?@JiD-#cxTqtDl$$|slMLK9O6CsnPpmk#x&}aek!qgab3F?*A<>^c$kdi%1_b8XYXWHlJPy`biXc$c$X)dcyV337uOZux%$zw)^U{6hby%GS()c0<Cibh{qiX4%bwA^C;jsZ;!iau-k6Wg8}ku9d3l+&U%4=#(&|OO;q%`s()zDQX!nEb`u_98U%PtD>Xl(vzOeS^{#bp1c=QYJZh3#d_V1{b+UM1E@9A3NLr+vny|TnB^NJED^~{l3E*+=!5~+7LSyU|bjR#A;u|IY%_6Oe8@~%G5p4YIhp?ZId{bU^9?R^)C$2h{f0vBuE7kWm&PwVg1SiLKBFT7tZ=?_^i?PtmaugvFm87TG4kx?%5p4N+{-tBj&SlZttUFw}T^9rQ?MjY|Zz`6Q3*Y4{3(=bq5uM#+etSh(PTVwTNU3M?lW%puTb}!cTKtI+cyz`+@-Cuu}yuXGQ^A|qg?mqhd-mf7(WP{Wz$|SGMGsmWKnfLgeES7oqjpPEWR|0PDv))%qL(^KTH^y&>Cf*ny-q-vR=@<JWyy!Rf?PBw7+I;GsEY$bsz(wM}`&R+=jka0$O=<A2B|aom>RFqza+%L{9F%%bGk1yAD;Mu>wT|O!7)-nv$L_^A!h0^9qvO=q)L6YSj?Ek62*12Xx^*914XtX4$3ECSQ^tCwzD;Sl%;!2jlX_3H`6W{CKUnIWx85(5`tM&R-nHDH&hy?#>cu>5-k7J&8}o#BrzfOY$59%t)>yq5$L_^A!aElYdxP$O=US^5pCea8cjC?cr~T&sQ*Z7+_2&NDys`h(oBMC`#{TQxx3CA9kMG_D;>CRIUd%^$_v<^B(S5#CWA)~K!beZe8pN!h>*lpqZ~k6#5O032X}|gTrQUrjuTbWl-%lmp6FrNJ?`s%Fy!pA-eeQt6q(8U*QjOJ%e&L<ol$~_FKM`-<KR*-C969B(e&Kx$k+oLu@hdBq^$TzBXMWkze)rA%0;#{Tkoa8h2XvnGr-(P^1MfRum#3w1Zn;god2XTJJh#~TjdKh2=DCG>^W0+VH_k28o97mrH_k1(cU3>S%Q_!deJSzcy22~9cQh}~!^*wKYl+8s*zU!7*zU!7_<?b79=3aN9)7^%JZ$&k94kEQc;~dXANc;_JJnVDKH}`;JY)6B>7)Ahphs2{@2iOSYWv=~f_PVDv$Iy88=7Bf_3W|g3esQXug$~RZIIXMbB~YKJnO!N`V$-V{vQ5k$$U=M5HGGPJPUiZ(%SEtx3pC2@BIn!&J?faS)W_9KehLlT7TcjDywG;(ufz=HGLH6cfN8)d(PnLJD!d+y1o8;r|$&n2M=GbjT63rc+bRM`Z(bq+WMz!{VZY&_0z)FXyZg2rt=w}raeDl{l2yJ$F9-+HR^|yrD@~zYjjRuFP>A`yz!jM=H1GCsrNaG%ccF|IhEb}_biclXVV{xrM|9hq0D=3mKIpOyI<pTWPk8nPI&SD+P(Yk567kc-+PI7MuwB|*^palR&VYn_2zz3Z|*1c=6>4xjs3KFV?U`k_tWN${iNR9Pwr#MQ|X%#YquzY>Q^$xnzJC55NCNLtxEMJQvOJKM$~`zNII(j|NBUK4xhtoyq2O=o{vldtN8|4&6VKgyi$3kfLGw(S9pEH>msrSJRd*10J#eM5wE}S+KK!tcqcdy`8RMLco*_h@GkJj$iIU>2Jhze8LvIO4j?}P9{~RYxf{G2KdbUMUSoJAAYI@Da58chI2oMA>s?-1ymnyB{k(FKJHR{8qw<Hy9Ap+a2mCfF3;URbYpg=92d@GzK&FAyFgKOm$VB8Ua3Xjb(gj}3^!I!TG8Mc8JR3O^JR3X}rScSBV|k6@6_1<(jt9?0&IHc|FGHq+mx15mwV78YukB2~ANKM30J$B!9X%@l8JUgD1ZRWSqEudi+zj4~Ypy`1g5T%$9<L1K25<)WO=LQF2CqrH{(w^XdE{{L^WdS#0pPds9<M{L1jq6E9j_OWL%@4^ZDabqzlG`d`c~u~@E-JRMQ#Fb1#jfF2Kg3p6L>i0J%ZOOykdAwMvefFK+k044De*|tGxb%oQIqNex289UJH?Hzze~PkZ*xs#M)m#J_~*U9E%(b9*-P{Qh5w=Fj&oJz+=FpkxuZ-$gwDuM<JbHH3xx5fkz?-f?q=Z9yJnsITAfF$fv<E;1S5Dz$3uJkpsZBynMW>c^&3;gxBXNm5(Bez(>Kyk=5Yi;0s6}xF@epyn3Nj?v8vI+#TEzrE&*e>VK*2d9_7$0Czx7Ta?NH$WGt@a64pAa651hUVV|_$e!SEa0Id!I0D=crE(auJ2(s+jO+*w20w;UxeKxbxC{6ZWP5NB*2$0oU=ObXUim1M3y~$@LhvbMDfkq)4EZHk&2n%VxE5aRD@Lh&5?KO12|j@=0G|LKLwdl+!0I{bpU8tq5BMPX5HcTp2z(f&@)2Yq_z1WNc?w(vu11!D%dl3J&-410*E!@>@Huc5)9>-qye=WnfG>f+LRNsk0)LJ4g1-h|MxF&<246u|g0FzTK~{mQFgKMS;?;<$e-@!<V{jn21+oda1-K>B58M*m3fUCg3fvm$4{i;1Ae(_5;5JM>6f^c~UcW-N0k=Vq%AI*V%1c3Z1uNigy#B~*0<Y;Pl_w&HfhU5WLp}+94jhgAEjSw7ANe@AKllk`B=`w%6tXus3fu=70`3D2MRo&+f`5bT3XY9w)HtZgFa61j`EsjoGWi1-`%luZCDxzZ$j36iq{PNFRo^#$b2QctTtBG4t=NA6(ESGw'

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
