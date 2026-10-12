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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3031b834ab514a0fb91e0fec151ed0ff/part_003.stl', 'relative_path': '3031b834ab514a0fb91e0fec151ed0ff/part_003.stl', 'source_sha256': '0cffe5f9bad591b2156478941afc12ed5bd5bc48f565d83bee5a40efcc9eb340', 'input_faces': 224, 'input_vertices': 150, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.263334184885025, -0.01864573359489441, 0.0515395849943161], [0.12015947699546814, 0.3781944215297699, 0.23209090530872345]]}
GEOMETRY_BASE85 = 'c$}q~2~?G38pl6eip?cO7Dc#bLQc5g0!k=X&4oZk5y&krAa0=&xS-JZ3AihZKrRFLN#c?^YMPl^-7$9&txP>uN}1K9PEM0^suMQ%{Xc)2%gs4w&dfdMIsf1H=l!1d`JVT^-}l`^OjOfm9-4eQY0Ku!J5bb8(^R-?9@_lWjJY#XQZu{HPG9JxwT7=g4O%iPZe+}OCvCo#9XKU5GbJN1%oG?twO?S6DRAnXjJX*}vlHiJOi5M#u%xuiRGXhUJt;lacKmd3-=0CH-d%%CubBSFkE^W&W5M-H@2OfmE^mskiMez5ex=%p<KjE7-=L25glzc6Ym>#Vi7mqTpZC87Z828-5uODYpPT?+^NAGy{>DO_zwPF3j8FTq7Jg8VB}(<m^tY97i9IU*rLZjcsVT2xeB^@*@NamPD7CEddlUJm9TVSr7<C#Rm2W7md$3vj@Wk~v)=t1T!e@#f6J3V+mLEN+)cS3T_{R$2n+g_7A68EizjbaYj;nJq-WZl3zWY1yP2YWt@paKX#dmgHhvTyG2atb9XYqUH72|rWyWpGt^rZOZtKpk2J}G{rulP9u#rAphHr}k~7W!|>T?}8#aTk9@7<|j2cg2r&VIL;J*EjgVH=lc01AoU*tcyOV0DhgvXX2aht%|Vgvo-ya_*siq!jH%n-|w9G_tV$l{ES!72kV$4;!hvD8g<@o1>fAMP<-#*`55POU9NXuhWP!yS%N&R?n&Q%DS8k4AaC+z_*Fh<kmuX(@au{{{}|W#VfJZUhkMmK%D4W#<3~9EFB36d`{j?vly7?8^D2(VynPC~CFH2`jlfLF-_PS5&T~0(1pBPk`3n5~3(sO+qg?#=Q$ECevtE__I|AUF=X?j>T3&$hn%l+081H@Zs(eopFt2&}Zuq9-$?z?;r=|YQ3*JKgWhuz3PpLeC@q-T@g8y-r)HiJ&##^scz&GFBegXTk-5!~@-U7d_aPKAL$*n#QzbaD3e|hf%9EbcM_4{8rh<eiJq7Qm~CB~bbtKsWK_vN}wx6aAm`@y&LcSV1UzU~-r&Hv~C=1mN^hU2TFrO(0dz_+x$j(IIVN1;yr>zi+2-p^8GUHp28-)_i$<hh%N`s<cf)!^@4D)*tD6=&qw{}k#m&n|{<>2ewQ>mqi_dfi(E-+c2v>d;q>I*Ids%!O}+eu{aGMNLl2dId=SJ~MH?)j41KGjhWo?9ZD+FXH&lUR<x99tPhiyM+E2-$#pIx_1}WYwBq9)4b9L_3B0%e3Ryl{usWlvhGeVz7GHEc+_tMzKQkJ1_i^n<b8>KZiKCrb#yM?iR(I4j&Y{V;WBUcaqz8&b1%wz?T|hl?f~ENPk+>@#U;x+RzD8kcww;gKcQ0kfBC?6<nfbzWj*zS<bQFN_~s$Cvfq}A|JMNc=JJQ|wHJ=c^?u>A4SidbFLl)TOa09+R3p!tv&e68377HC_qQTXd@1TTe*RMY%Xi`HzAKR5;#(@db@OY;v&mQb<$plxxn2t2@P8fGWsMDzb-XgG3i~R$M*6U%rPTBA$1TXyzcuF7KN%$X-v7ox{TaJ)zUiS^zF*fXHp5^09nP-{dQ9@fd%@Q|*P%XRRF(K?t16Md#tV7P>zhkI-i<HE_2yNGU(reYVNbxf_}0n&=f)D5cSOi0<iFsIKImP0$aSTsZ^U(-{uTE<!+X5U`(e8c7~k!VTu+x{lE2{iddwU7lB}aST>kFyNg4KG-xBOMQ@}~=6HSkf#P~61q`&iKoNwfRnjv|6xz*VF)+8s{KMQ9z_P;8Wb@$9_<m;!t5&ufp3yu7wzsWwYE<V#}-d%B0f53hjf1=x~5s$hq=Oyre*M~MKcyFj1=#4&W75l{hYP-DmIQBU_bR+UMtCHu1DMa#3IwS8-j_X+UpgiJH>t2vs5%H*f5_Au~k<%ahwyt)X_*tzgBObNi2KX7s^XEvcd)@b^B>#orEfJ5}&xO~j;5&R@v}qS#Lx0;|mU(9c$+~atvK8k$eDAbtPs4Zoo@z#uYUFqLUTbfRh5x(zK<q*I#@e~^d};N)_=gj>A-}`@MC-l{zT^Ez+j>`ghx?WGQ`mM~m$69h10jLp2i_LHqA%9n6#qc-Kg`{My!EoaTJlQi)7h2qe|KNKdKSLpeOMd$ljK?7O4jAgJu<$cWGBWs-sf*b?ZWZdu6QogJ#|C&TgMOZzU=ti(KgiY!Me=2gFL1Or)9lv=kJB@@ch!lJoaHd;`<=KrD>e_Yr^0=K2P;qpTT#0{_2V4@}9f)6U=MfVwUlS_?F&z=(E1GQ0h5fi}!BJv)<@~ey)Y&DZDLyR0R5O9yL__$t~r5ut_)R!+<^Vd>kAn@2&6cz`7VauSva+9mo5)Ht2Kd=l*4KpFDXB@28fyZ20=1SQ(#M58v^<NFNw>2>Bh~qq^RKZ#kbW?`cKu;`^EL`^G5#LiW|m!==vTsfUq&b!%DoX7i;#C2shAWBMpWuJ?m{>Cdli;hUr5vHvY2@5s8mv<bf9XUKi#AAC-|T7Lw`zsmF4njItWEqO)9aD1+}%sX+J?4Np{caisqkL>g98>P;Z$Kjh6=1M<1w>uLN)9BZ1!m1K?&CQ0kaIyWGotk9#Qx<>FwBPj6KV@h1`LBM;_UhH=|NSW&XsaQ>79rF=WTnw$r6b89<mafP$j^~SFcgnwC>~FJfjpi(g`qf=nm|@MjhsrJNu5KUNzP;_&SEImsedFZT}{@>OQ@^JN>`GVE+Q+PMP5Q)K%GHeKz^B_IF0%uIgOmiP&|=3nLLp^jv7ZEM;=a%A`d4Ip$;PtArGWJOCCrLrgkL<lY3F0CMyjjD-9v{A`hTGM^-w5Jb*lip?D~DG<hgFhM{-@bv$_jIfXifoI;*WO(iRxNmiOko=wi7W|5WZWSwiALtQ{#z;(@`rjc{V8Pr5_204kLcoKCYc@lXnbsTvtc`$W2c`!MYI)prg>l#W8CI@q!La77D1GpZc)S={1@?dI=-Mle&wZ*XZ7_LpjwM^i(PT<-!Tzd-pk-{~|pyrU5+hVCL<}(z}v&CF$9(5@>kGzJVxRAP>Tu3gqMFBORx}2O(UPzr!PNz<%&L>YNCsXH<lgSplx-AUFQ*H4QHJdt@oK0R#%_A=+FQcv@FC(vIC|*Y`B(EcvQj5u@<TAUylra>S*rJHKf?7acLC&S-lXJ<hP#2OL`l#4!i=MU!r*<QUllxPjA@?WuV<--?MQ5ss`V84b?nLcI?nLfF?MZ%$+MU{y+@0K)Y9{w3huI>MI)-W{k0HlX!^!dFSZaTAEctnAKl1bB2!`U`)F5(iau2({^k69dgDsw<`cXTR{m8yl6WN#Ck=lvek?c?HLT>1z;x@K;!WQiqiai*LTQd~5q_!cqB)4KHZcA-PR=zvODs{0t*M+&2wy>M41?N}lZC8&s^D1p`S95#LrPPz`$+;WY-L4i_&Z*Ry>_ToqbtAVRdsBVL-sJYw4&?S^PpTK$i*q-yt6eQkIj2%5vNPF@+KlW*_MtvT_91tmK2GjH_M$c?dy!qKP3>xF!a0>{WGAwkGbYNZiAU4_^sk_Qe{`H=|BoTZGaJ8l+n-r$%k|q!cuZ7tbxpQ{n&1KMqPnd83lox6>i'

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
