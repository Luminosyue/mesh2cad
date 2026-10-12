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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7c6ac3a8aa4b472fbc31ed8cf50703d2/part_002.stl', 'relative_path': '7c6ac3a8aa4b472fbc31ed8cf50703d2/part_002.stl', 'source_sha256': '83d2a4b663f9ff9451363d7d2dfc95e16dbf01f2d26960d228084e96ffce4250', 'input_faces': 80, 'input_vertices': 71, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.30226489901542664, 0.21519500017166138, -0.2966412305831909], [0.3308299779891968, 0.31874334812164307, 0.2674768567085266]]}
GEOMETRY_BASE85 = 'c$}q{2}~SS7{`bEtlXvL>OhZW3v#xUQk0RasYrt%1hK6wl%>!TKxjzRS|=qcp_Cfidc;T<(nRA$#H7)nWsze+goOpGEm*gSskRY}VyaOPXWsWm-<X;ho#f^J+uwfk&71djceWtU$vIG<BT@*^ookME69jd53xPtDvEgX-L1SZFZT({of-m#xv6^T07UdU|I0#L`6S@jx<G}`9ny5>!Ox4ATy2`qSqYY)XrF9JzM%Cw*)ifFv-&j>vZ&Y4K??{Xlll8IUlj46pJe4Wf_dYb8q0VI`obt5~MlyI`l+4mld}UPQ_wAuP;xeYDxI*4s?Zwi*)NNtsb(fIuH&Ff4yFXP^E`69@Z~xV%rs?yG!>rC{AM;X7GhH_)V1oDZ%JY<2KWe-%(?#c98?-XthkC;;*5Cf})ge|_zn}c;J(M5jO|tXE1JtK#%trH#8RWhE-7NEBm){WYr5ZEkp*L9{!z6hzVS?7d<Tl0nC6v<rT&rV!<l~1g@!ssxO8p&QH1l4n>119ycC}wqZ+oA4!|m_^wtnSC@}UpVbvAus(Ri%Cc>3}P@8#eodjI^-qrA6|x6$<rquBlm1C``c(#UsMhk0-M`U1UQQ^EFEYCJ^!f47jIPnzJplzfHO`|UusU(&`Z@;!R0H!QMsmZ!;^b8k@Y@3Zn=nEQpU(|Lfczp1&JeBmOk+Y4a>yq8Kms837wpr*b(g!;Jahcv#xZHBGq(nqYnJ^3*884O}xNC{#4E1f+;_0J5_zU+R(tnv9@(&w;$p6#Q(t(AP{D|FqQ2@CJd-*l7rog3l3eSV01<nk!*r3-Vk4>LNpU()<Zs#|)NvTu5r_d@SaRKHM7-^W+maDFhmFS~W;1n*@JJ>Bo=Q2Ku5pQ3qMnlPW+Y~Ae3<i+q5sy}bB@?I|AL;V}dCpG?ZG4tl}kC_+WX(xYwCG%2o1bvS#JxA-%-OKLN9Q?hlkM~h4^m%o4V%`upO80xSi+s(X)<6Cg`LWq4)l2@qG>?`}=ItHlY`hm<`hs~={ClikXnBNr`NT<D_x3Y3-b;!7^!vEsT}{2v?K95Ki&>)iFTX|CwRF&ZEu7VO@!}No@>4ymkLmg%^^Z2ue0m3Lytg;a(ELMYHT7nP-<UT<q-*;mrO@X<e|%C?-&xDN$*a|>dilZF&+fGTt6nJmfqapp#>+Q@ssFd7Q=0maLh>g%CV4O3YGd9$J7DcA&^%>hjxF4foRujn!$Wz>R+e#(SXHXWYTo$~TfOaHJz`T6{`Vs`SDC|o%E&=V;2dx^G6S3q&O+V`&H`s5?*V6m(=b%tg-i#lxf8q#oQm85P6ekRw}aK(22KI5UQ6X9WHMM(MyN9G#!y+03<m4Ln~?$F&EPG_K=2l@4jBa2fuoUY!O`HY$aUbY;27k3a11yW83K+4$05VOao~7lI5-}hfQ$qufD<uPj#9>5$Ti4F@EWiuG92s)c1MPR-NA0i5U?BA6}cYl3U)@W13QBqk!!(@U<YIn*a0jcSHGeH*a;Z`b^^N~gTXFf4`e9V1MH0y!QNmm<OZ-8*dG}I_6PeRH-Y`YzQ~PWU$Bod3i2Er1D*cqFaBSLtS*M;5C7lK)c$PoXI3h`{`?Uu$a7KmM_F`7;ZY^8t9K>*0XUPPiU'

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
