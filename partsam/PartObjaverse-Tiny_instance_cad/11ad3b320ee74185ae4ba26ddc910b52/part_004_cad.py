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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/11ad3b320ee74185ae4ba26ddc910b52/part_004.stl', 'relative_path': '11ad3b320ee74185ae4ba26ddc910b52/part_004.stl', 'source_sha256': 'aa2da35a5d47cb3f887957c6d3584e77c6de0787bfd7a4dba6f9aa553bb1b60d', 'input_faces': 138, 'input_vertices': 107, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.008949659764766693, -0.3603430390357971, -0.29284191131591797], [0.09420602768659592, -0.34648722410202026, -0.28594452142715454]]}
GEOMETRY_BASE85 = 'c$}q}Yfw~G0LL#c6+$ILh4OJllf{TYAW=*%lK22|@vZsT6&4{41(bBmMAOpAG}F>7A0Mn{s+n*`gdWy9Q#O659H)|d7e}(0hG8A2nyKmWrM>t3F1u&hW|~^(%>TDP4(FcNz2}OvEG9Nt5ub6&Q*XC*>`zb>vm`3XO0%bNOI?+xDXV_-_9!LE^5)0RqZLc$J6A+0&B~7SYEM&DWBN2TeR@qndZwCQv#D`Qqq~0Xrp9WI=}X-kn>+#ERO{aC34C|tWKYRdb2Bp4o$7!5SiQ(yyyufZoHgF~&de77>({KDoM(BL@rvcWy-!$P$v(E*Ox1VA@|ypM<hzY_(N1rb<P~Et?Y}A4*PAV`_@5NMvUZo%AAP;JuKzvZoes;l_<rEJ`z5dWzU8_r<@)+^+HVoQtY>GW@!Gz{I8FV%!q4e>%1YnIT=$sd?eQx9os!p#gY^HL<W*xI^$!YP*t1>q{~OwWA<Tct{5MP9t8b<Kcfx!<?Hm=pz#-bv7l`ZLZkN2GYw~;+^lY=n<@<|%?v}jQcU#o&T_}7;?N%|*RrIG7@38z?-;Z+p_!i$y#<f}Y`YP7tRpC=>8$$c(^?xXNZ)c7?Z>bK;Yh4M~rFFsE<I;L7gipI#AG%Mx{tJ@V^h$Z3q&e%wJp3Z>lRn=o-!DIX?H27Urv0`sUrzg{C9mj(tk)&Udpk23?;+vuED-H<4Q0GLB(HQS*Ts0tCGYk9Mmx`h`8)J~BiEf#5^;X;n(n0kr-bjBQ7qc|S)QLhA2vVQuc@KytK9xbc%?VSx?j5D<#ojOTSt7q{m^;2yhz%g=Y_v|xuPi2{=^6OXM^w)+^dU}2=`H@drgtmpFbJz9?1vqmqn8Aci)|Cby@BAJqHej`LO2zzTb1;LTioHzV8z4yexUmcwT-keb8EKjn_CQ@AFTyH(2wd*U0xZ-lZ>-pAT1BH;8$&pU(#*Z;z|*`P_J-!St%{GwQ!2`QUl+mgM`!+q+HprcTQT&z)-Fx1}`6<2ohz;JH?Bd98D6o2Y+=`o|^jGEOkwUE+M~+-G^!c$WHS@CVvNe>xb~Vaa=q^HTq9uNb>%|2ff5y-n2DH_7KF{;Xar?GsIZzfH{ZSJJ++z2f^^+RvI1by3_GtEK&8dzZdcI`1?iPSp2xOV5p<*O~tf*Tntlz8Jdy?Rm4krZ1Gv_n<G6=HGSW3w(vN4{fjNv!(Mwy_wS<sr{gzNB>WV`R_i`F3-cek`JE;@ArCpq;;`<a9s}LZ?s36|CU?v9b*6NllRZ9!5yLdS@XXrd9Tqb?;pHkJT0wz_pQ+#Vn3gj=F|2r<9P7B$SJ+WI>w)T?e_tSVwU*8TWpOx<Q3MG=Eu&+udsD_|Lzqwx8VQ2!af-2!~KCWfnu^sj)PS=g}e_=frpXzz{B7n<WP7BoIu_MC%}p1U^o#@BJYNi;8gNnI2BGK$HQsxB=P}x5}ZXo1ZTnd<il`2Tu4rb&71+x4U}1Y&kmHlK*{90#?R-%rDPFY3Kx@)z{T(sG7rw<8YU;RPANF^niI(h@I-hNslqD1KZ-Ql7(fn#2f(r95I7cANd9MLWpoH9^4-jV@CZe$Why?2pC$3Lfy`+Mb3cN*W5_gk4D28$!45cw%z|^^0x}=Y=UN4<VIk`_3vc(u{62?b@;q`bJP)2tmcp~)nPf3M6P`v+fv3T_WHy`&r;`)mba*s53LXs)SAuIioMLi3IRK7_<H%Sz4vr!fI0}v-qv05M5IGPY1dk*~z$4+Y<QRA?oIyI^40tk`15bvhk_GTo_))S1E@3TAt`3y-fl@;;xsH4su7f>fE$o5UkyY?I*hRWw7rcgC3$KA!k*ncV@JjMAcqP1qTnaCNE6Ig$B|M*W!t>!WvK%ghE64?K1-yt{3@?J0k;~y_@Cvj2vZ(0fn1A}yPw>-XZLZKi1cm>meB6fq=9NHOeTT2JEY3P|qXYjM0{Mq|awvZTV)b|k'

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
