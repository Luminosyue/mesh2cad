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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/77d56cc994f94d8280c38009688e7413/part_006.stl', 'relative_path': '77d56cc994f94d8280c38009688e7413/part_006.stl', 'source_sha256': '4d6b533b58a5f1c66fa2a77dc97d5d4b00300f7cc27d2fd43d20c31c0d8d7ecb', 'input_faces': 144, 'input_vertices': 112, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3172624111175537, -0.3962932527065277, -0.14450475573539734], [0.35244011878967285, -0.30923107266426086, 0.10987837612628937]]}
GEOMETRY_BASE85 = 'c$}q}e@s<n7{|{Q@dy4+6wrhNC|3$a5K+YBB#7cwyej@cO%KZDmxy{Hnl<&<@{iQ9OkJ&J-AzqJQ%g`$>)c#}vUDkE6F0jnT`udN@{erPI`4bG&&zr5Y-@G4ci+$X?l}+7dEWQF=N)cWSkFi$c*QHeGqH6_KMSqVUx`%eJ>I&?wVvAXH5)fOl)>ER7j$po;(6|3hf=S+;w<&luJt;ns?KR;Q=BQPvuuO6&RbHmdV{yr!~Fb`>RONG*H)Bl^jP;})6&vY)QQO{>K64sUJ<N@-h~~eCB}h_TTBDVCq6Z8z7Aje;aYQ!&DS<vX@63@3SULMe{Y7A-`{l3Z`ypyA4qufygi=shsINWKjO9f5BR+gd5pVFpP4pa)L*~*f<2z{hsINW5$~>&@+;YMFPk=>@*AlaFWTcNzZMct`6=EoT5j0$`{TFqc=9Q~ze~Mjj~D$3i5LArydJsdI#b`am|&ml4_`2Cz5(AC-SZ>f|K<Zyyc+h?CDZ0pyb-<aLmp?ImE#Y2&zm-%;+2P)XLvpH??~}_-XDDZkT3G@Uv-S#s|67^r1%H>&YCt~<UbP0*PGTpi2M58mACo(wq57%OTGr**Y@pcet$Yzj{nue-<N!f*J^j1WcPvJlcjh)p`gXI`4q42T>UYxd)W-Ber1x2uV?b9e$AEi0e`+OSIV!p-TcI~`IKMz>hN)%H>XsNzua}swE3c*t0#E>)$`k>deqDL&8E$#dIDdsIm@5V*(K-y?Gc|Z@+p77Th8apzx15kpCdzgJ>-jihVO4;_ey1}+@Fe8-XHR*9{-lCLp*QBkMexo_nD^67yVf@<S4JFdSJWszQay8nKqyDt1mz1@2hN&X_xX3KF-%0`C|QS{fpPHccn}5dh_Iqrp*`ibZ+A7E%4G@DPCRvIj^65iuYGtIl|{__fn~Tf8%$&Kje$`Q`>QnzwfTCa{aGe<MoqI`HhG>!T!JTzLZ~o=X>5C^2Pq}sFnA}s5mL*_XU>o`pFmh-+DLLf1^{bXW!=FdVnwb8I{WG@oV>_dbFZ_!Tle;SPxenhxzj@jt;4wqu${9gfG_T)%A_M|E>fnKHz_w?^ooD`X3JBzZcDy*deVS$8G+5Az$>r;TyjH=xy0@J)SZA_e;K54-LKe{%OpfC&jD#`|$mWd{Ix7kMGaEF-zq5g9rF}BcI~+pZoFk=0CMUs^9l&C!a6!#eN&}9$#<9v7J)9p7bK0FY?8HTbaS<OUpVX=Wp!_?pN?d{GMXIU#YoY$noVn`2I=0sK+^)@1MrK4!Qr2zU1#qKE>;q<|%&P`8ep)cmGd(H{sKFQ-!ZLHs0iY3i-a1Zy=t0gM5mgfbTeb%1^$UlYGmbU&DEWe9BM0Mm~M_=^O%IeD~q|f2ou58+2ZRFZz&(^A&tO^n3+hoLeYfZ;;}BIPV4E)8ExYd~v>_b7M(^RF9AOZt3*=deNv9t+(~4HTqho=du#p(V3a-B7O4FxiaJ59i1~W{_oLwp;g05Yq+7y!EW#z=o0W8a2|9nn5hQN15bx$fTx2qq0fLb!Q-J%gU5r%VlYmCMuQW;v8bQD&oXEscp10|IvdP%2Dk{E51k6m2Ty~hgQtNfKvTdIz@sr3kANnDM}UVzRq$|dBs3Nri+5za$QmzLV*zvpcmdc2T?%%AXF}(JnLZDm3C@8|0_T7yL!Sjt2B$(tfm6ZB7>pC4G2ldS9O`H9Qw*ICE(R}#7J!-Nf)|5lL9@ZLz|TP^f}aDYLC1m9z+*5NkAynGBf(M7cyJVW7&HzXhj(Pm);3$mQ<UKP&jjb;p79*q6EmgXAmfD?j0-Us&&FUp1B3BYXgW9rJO#Ck1v5<mr$Cc17^@hJW1$J)WXxq2<~`ZQOlh4k&VkMZyTDmsrnH6`FM`fjy4MA}FM#GM-D@EW^PCNyh>?Xk90zt{WMQu2!Ew+;aJe<sTB8hu@fzrA@EY(c=uq$~@DS)A@DT6-Xg}}(a9?O|a9?mZGz=ULc0hZ89bg68OX<EC_k>1(dxHBw2ZH;6`$L}s_XiI~Pb$%;a_~Cn2Jkv?4Rk%Y23!rT09S*nprzm{um`GxJ>U{+xLuAOkzxPzudD9MU`>+#krn!+{MoiYIo--7KH_dyc&}iidnlVMZDE~J{syH<O(F'

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
