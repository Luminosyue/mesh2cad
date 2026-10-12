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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ed24b6e27921449f935509d9f3da043f/part_004.stl', 'relative_path': 'ed24b6e27921449f935509d9f3da043f/part_004.stl', 'source_sha256': 'f1d3b2cee7cd81f3550574c6a0908e36ead443baf4e54bf3e6883ce02a0ba786', 'input_faces': 178, 'input_vertices': 100, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.004707615822553635, -0.34083449840545654, -0.09297536313533783], [0.27748942375183105, 0.23241275548934937, 0.06974638998508453]]}
GEOMETRY_BASE85 = 'c$}q}3v3is6o&8i0ew*lEss)LW}z>z^uep8P`W6kwOgQ25n5DsX_torLJJtg#{eQikyMISP;iL>L0U>FV2m*xsuYx0Q8b`L7YvAr3IwB)VB(xJ|Jdm;CPpVY`M>+`nKO6p+<RxT#ZLc#D4`v8@r(H83tzAh6k#GtEca9{onP*$N?o*gg-t}TPlv9xlcr59F13l}Vr5c=r>eX%DO*Y!Gbbx4MM|3UROQl2_o7)(RaSV&pWt3l<x%~rdG5s?wVj-io}MBN8<ZkFC;i7Gg!<qtsA?g#^*=_cyxyleS5<jU`a<^mgs?9ZZ!M{#cg{3Y`Pit>Si_fZpnOrZB#qC1<o8cVeLFq%>~H*GpfO)e-%!K4^6q&4eY%z}zZdx~*SCkwX5aJLDfX}AzQS79`~>-qpdBZvEd{@{m)hQ|zb+<K^!ljd>OQ%W>-^Son%dq9=NfAJwihg8f8U2^x$e)iws4&>w&h&E$idfD_G)#clJQToKko+j(-m=QGv|lCv6AcTxx~JRsoTK!t<*lp<99ouo$IVy#`&Ussm%Rck*xW@yuFLt=TEKX{5$*E7o#q|#n;;w%l#D%XSu#|;`(m(8$Z+hb2GH@sj*kHR{y$|e@DKw@yVU+Z<5yWbut3aaGmU1tN8q&h3h##<{;-gnqF+=JbUFv_V>qfeaYtHI*y!>SNZqWiu3G86!Q5}+T~jA|AIQLPE1#RF0Ne?kE=2*Q5(<DDfKN@e);y@eBbA0zRq<<w|}YCiFuKqSJ+PWrE6Dsd?a7*cQ`Nc)>gicID0Ffzqz`J+sW&;@$Z@6@;s5x+757kcC>BlG*6=MG_+Xwa!J7+o-fsTZ?a#%gs<!ETgLO*cYEdz_Wd_$*F8RWAJ^YMmY<KWp`6D@PAjN0`tsCUTAdG`f5+%MDqhy+L-fshqc8eh=Kd=KryMZ)dOxN1-ww1``0^j4>W#j>zFek!eV&NBZ|><-XV(nAFXfN6PWL6m#iRUOu6@np?E9&#!D<}5W53^THE!Ozghs3JH~aedOC@=YR?pE}QqySl+#Ts}9k7}wV(rK#t9f{jk9p`#Dr&Nv&uK>vTCNLsuV$-t<aN86E!W+Zwau36H1=e()w&jwzteovKH!VI%Kkn3#=PN&_`0Tj#?>~Tee=E~uUgN(c^?xWojIh{>%8wN+rHI&(>|&EctfjW-d9)mKg_;qA9f^+INWJIVBc20TEzZ6`+UzsS{>7S!4VvN#5m9O_lRrmB=*hk9Y@N;?3>?H%G|A;^7Z$c^81kYxxVQ=D0-~XeA9c=alF@Yu2ZV8Dx*)o-(v7ZndZxX7J4oHgKgXSyq|Aq{^^iUxvtr->BheA@Nus1as{7cf6Gh9xXzOGhm5`q-+}9zeWm?Q4UcnWtyZVG<utcn7<8n?;LGsE=0|ydlMAnD`SG8$alU@tZa-@I?xUKI`mSzeXV~Ap_!Rda{gFejYX0YWCs+quUy*C@#cKuZ`!3yV;&J=V-p>Bk;#Thes)z<FU(S5!S+0M<t@%Zc6UOmZ7JbCNd~(Fc#yVzSWNCGji1>5tKNEeFebf=<t?Y}E@YcWm;!a<Oy8}Ey7lMSK2v)xi=eP}@hGf#AtM#Yh{NexZ(=apZ|9%=e)IMaZk*UTw8do(&BSyg^rF$KN(7lmp=OS|84O3$XcqDw?BaKJg4=-7b!D>iq^j4!Em?9FMgdA#jgQs&(w8PYhLc1q^(>>B2h;Vp))rdel9KVrwAN;<E0q_Q(&wBrLFC6(HU{d<>&r{<eH6B0^=Oc)nYK(<WP@@n!5$Xgxkv|bZTm;Pn7l8|)X<*VMZ~=G_f;bS`A50nq4g}i}!~xJyZ~(Xq?mZY|8w@WB(FM<>3-a}66l!?pq|wk&a44=94ebw(2KPe{OVA|IF@K1Y5ya`xG;lh21cG=tG!LAI=QkWVq?ynMz?tCD(0tLcj)?U&L^>Xt56;Ik9*-Q-2cb@|K35(@4rvZ_EI0>DYb-%%b2Jq?3_J`usR-f>=mfAn7c-z);0*9kq0Rdgp{<Ae!9$=!!9&0!p;@A1PaqxxEfgJl3-LJUMDRGU16l-jfU}_m;B4?<=pZm@Ab2o15^4iSg7v+FR6uQD(g4wM5c@&9fJuYFq#<BGaCc|~nDjnycd#8A4<=0j+rf#@RB$SuQzCRIcqpDtB7!&;Isi=C7aR-j1?>Uu1@?!Afx|Es{s=m{LjAygxVNqd;y9=sY)Aj%pt0asTsscx5AF)3b{{oj)EKD7G&PFVn5@R*Xg`dYZSW?;BP}uTB(xtxzJ9LmJ)*`8HKrnWDt?;^zXUM@`J^r|X*u{Y@N7gm`bO#ola_)X2kZAoIt5w^o&uh(Mj3P_v=m&5x-*eOIt%IsyU~wXP#3ri`Y6-|cHusWi=8&VDF1)@%dF#&c~KevKr^4&`E$y6W}Lc!{{FZsb_UX#Qzx09SfXkMtz_{RIZ3hi'

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
