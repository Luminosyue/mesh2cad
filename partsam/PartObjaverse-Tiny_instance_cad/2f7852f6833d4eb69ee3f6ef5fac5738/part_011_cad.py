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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2f7852f6833d4eb69ee3f6ef5fac5738/part_011.stl', 'relative_path': '2f7852f6833d4eb69ee3f6ef5fac5738/part_011.stl', 'source_sha256': '4ae3da1c07b3d6b1e32820fc507df24093ac5af4d29b276490b85d70ec02bfaf', 'input_faces': 119, 'input_vertices': 99, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17554950714111328, -0.11446139216423035, -0.17242518067359924], [0.08097947388887405, 0.49999964237213135, 0.12162439525127411]]}
GEOMETRY_BASE85 = 'c$}qJYfw~W82-2^D6NPHmWs<}EE<ByMcBYST2h8`QEBC(u*y21rUG7b%rjofNyZGd!bXQd2QP@4fR`cNWlIdT6w0x|LToIp{$!2gWl}red!Aj-Inqp1%RKWu=Q;0r&-<P4I%KAKc?U817shN+q1G?`7~}9~L2Q|=Y)Q!+TY1#N#Vb8n0Qvmq;;re~Q!;Zr*fO@tSY#`oQ)V>jjmdKpjgfle+(l(e%B%|u7L^s*xSwiWP;Qg_@?z^^n{*wKloY9t9TBNtt^cpTKD>tF6|HuO#D{kph;QvaK)mYg8P04?<x$Rs1N@Je`E|&;FX(>CuUGiBSnJ%*uZ5DZ&ndoh^Lg%f-yC<?tnkHmo5*KlN;gpaf<K(Z#lz%0E5EBUD||88{yoKqF07@zX=~+p@9muwze8vt-}7xb-ZuC$`KggqZ*?UjpZ%D!Uscb;`}CYxxxZCePvPY**`H9}s*HCSzLno&sMx29-<d7P*ITGgAv%!m7k<#;p!i)oTa@w4|E%m^zjjIKJ06`PUr2axNmXaiPV&V%ON-JMqx;M8jmz8V`uxD7N?$CyF8fKzpU`t1zkEjTE!omQ?+tI*Z12H$<#+o{fz3U}!*|8&r#WT6F8(6LN9dZU{<c#msh%5EUs0THjog0QJ159@rjXxVc!$P^e%I~e<j;0e9=-EJ$|G*=B%eKQYgc`@J-3b#SLC;=zR$UG^4a`1$rm1tKBV-85m#jY=Dm+qzAmVPUsvy)s><WIu)0I}J%x_dja299Nb=d$t{rrJG?9GPUivlp=~azpg)fHKsa>LBB(<wLYta#kUuux^96GeouJi}B$-ZyIda9#kr0ma;`%7=KQNO$Wb#lMBd^QF?`d2t#r1sH|E?>BpvQHWBNIg+wSNe!|`Hp&%>>DCzU8wGL@l&(X&!2gk>S@1Ee)sIL<cpRmr|5oFOtW3#v-hpk&yH4uT^aA5cYmF(Q^l|S`2c;-qD>8|{O3$gYEPEsm@3al0cR*rbJK2Bo>ALqz888&olwQEzuQLnYtm~~@tr@=Iwp3UJ*kQ}|0%C~_ZroC_CAo;Jz>&um0#LL<3u#y*r&|zFg#F=XO}PJ7IY}bKid>9w>LSB+RHlMaw>hcr~HCE-j+72;$y;S-U+<}Ta~^eBk3E;Q!Lb~{M#F4f5WyKm4C8c_UA{4s`sYU(R$dO>8Z*uq>s8r{_=484(@s$Jtp7rd;CGVt}s^jG;ZC#X58un!>fCm7j9oWFSgt*BR`@`wVp8FtJCN`nstd?U$=sM%{nH|J6vg2)ahC$wZ3~@a`~EdRqMOsFZ<RIYuEoZ736F83pTHweC__i&UMMYc0VfkZ4c$s>|a8_Pqh@M+3&>8etRiivp=%vm9nqdPsR0H$!CKy4k+Ut!SB(2tlh80;9cZv_jl2rS4Y0)oZ#}GIwxEUJ}A!z^*O}lKXnd?zewws_B^BCW|8|<bN<l>Hp}a}^1PI(It3c<9w`p$#TbX5bPAknRU84i$$u{H`3P7N_pgqCF){!54A|#YsfH{Gu>jZcU<)+oMCfD*uS+n2r$KWrfHpxVfM-A_K*xcnLq~!$z|)~KpfiE#s4ENF0-gbFfu02}fG$9NvjDEAN*K=jQ^H_?>p+0(0pKv`0ni43>u?D#fQNy@poc++g7wgPygL-&`gsXS;IZK0&|{$ofd@m6k}yKT81O)7&VJCN!5&~gXa@EN`$7BRd4GUwKD49pObpl`+8_600Ipv|ZTx+y0N3f@9Ox<FH^4d2v%ywy4s;Hlw*s#A@i93>!cYl(JV!|w366yh0rv;TLUWFX?hoA;oCw_)+Dk$Jcqlj#dMNZu61*k!!F@02zF?gqr%v%+9cm1L4rcPa;2a0mLF<q!4&XWg?9HCcHLgwgJ|=vlA<+H6-q7BtwIASWYlH-&gh>F`uSrOeFj>MlfNKGq3oSs82Nyzf&W9ckJpnn>kYh4*E;tW57rGEU6Pj~2bRl#;a+;AN4LT3}GBoFj(0R}^fr-eK4gHFQXC?Sbcn;vYH`o)pH*_z6>t_J2eb8nfd;=f&TxX_vcm{d>)4vs-{6w0_%6~FwpHy!}$|rkCgT=iuWv2PicH}AjmGZ{&o@ajp<x_W4'

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
