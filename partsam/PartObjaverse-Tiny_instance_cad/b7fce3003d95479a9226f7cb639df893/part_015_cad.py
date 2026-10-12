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

PART_NAME = 'part_015'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7fce3003d95479a9226f7cb639df893/part_015.stl', 'relative_path': 'b7fce3003d95479a9226f7cb639df893/part_015.stl', 'source_sha256': '94e14da4d1f1ddb60916542dc9725492040274eb0e636dc0a5843f246c30c4f8', 'input_faces': 184, 'input_vertices': 121, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3680426776409149, -0.21616530418395996, -0.21244899928569794], [-0.19880898296833038, 0.017557859420776367, 0.22574196755886078]]}
GEOMETRY_BASE85 = 'c$}q}3s6+o9mX#p62J!nio~ebL>?-r#1}!3O9^Tu7*r4tkwsioLVSRN)|$Dsjl^iFhCY%snQUzwtu_s6On^N0iYN~uVG*QBn`Q?iCMIJlajZ45?LGhhx8&X(I@4*_`R4oGZ_l3lKaYEsH9gg9NU+4ONz!wN8(#a9za$9_lY*skYw5O)h1Rm^o3`xqkOC+dFPB#@%}h(r@sP@;T@mZ7Wrd{?adJd_QEWt%98t8nbX#e`ru@yN>#QPQSWr@C)$_6q1zW88b!5!LF;ViYDN*un`G0)*=_NQlt9tCB7WMApL}9DL4%r9EwR!Vi5$>FO`?4{YzPa#*eURMpw`-?_D^)#|tNlN1A^+sB2ke97(vly)B-+c}KjeOD?jADM<DL)H<C$pgC#dFxeUMyH|58Ks6#JX%l;1BuZ674JJy`t~z3+Ra+jw8sc-?c?cvVXy=SxpqG>+Fjca2w>o6&8oQ+_(?q<xTF@d<sC=VzL^AB@*Mca7KLf2d1bYu?+N$a{y|>HWT^IKOq}0^KKI_PcZ)jy&x3Msm;3-WP7$nZfyYy_Cygq10Z@h@o71rjPoS<{YN>YGerI%1nQaKA+R|4&~c?xP4`I9rc$}O6{HR+`B~WE5ciaTe8C6qjvkgqFmjxhT1!K9i@JpAs=yG{BxQg+rEYMRM-8Nxu2ugc)zV`*J$19Ug!2-9OU_|jJ4DJtk_SvwCU`xsh)<<>Av!+J>1@F2hE!ja{U~=-?!D&Ub;G-$8~Ho=RIx5sQyD;XKA0-XK_7ue?^~n&aWp|)8}*hr%PzPY@y9mk1b~g=SSY<b^3Hae=awQ`)Mw0<@WPyDW4I@bzV%P@muZ`bN>kv_p__+FkLU7N%NqbyVJ?@S;YIZCa9jD$Lo|!w<D;3=f!&sbnWQt9Be<k=dS%ckh?v<?z!vvmCn4~X<RSqcEWjju9IKuG|scqbA#$pJE}X4^Q_E#k=ko-6>xq-rt#SNW1D#0*O>F;UtgfQQkI(Q$8+SKyPl(gd~O%jsXagHq<xUw^_&jm^5$Y1&xxwj_Ca#jIWv&Eoipya>zt8CBy+y#bAI0HenR8b0uy+B|B*)f$62CKu6D(l=0VOn!}Bm@VyAH*%5S7LQhqCdbM;5G|7|aI@^kR5kLkWzYEUzcFSXx6@Au}>`QV&<p3j@*UpP$jAGn6vOPPHR<33dWzWpp+|MIHCSih|`nA)pHI=G*sbv&-mTIk%;{@7^h-+91F?X^9}9meNHJ$Q=dUt4$t{e1d1UGHDObvFHu^XYr3z4S~?E!}tDZ%zGMYNM!sx#~Au=P%CjIl0{HP4blo`Myan)43;wB~mVpf0p~16GZ2Q=2=3y`uhrQk8@AS{+PxkMVC2@>*CB<P*2bAH^mO)b0Jp^IYV`Qx5hM|7K=i;_Rm~Xduc%?^>4|J;~eLMe4~;2mrsp#7@sfgQdSG^w_6>i=XAtr%9Sl;9me}g-pkJOb#8~Tex*s{b@5td%59f+(>ba7E$cAV`G=vjzoe?i&HcYTj`v+pBIh`torj0>eQG9hoei;c4qBQ%;qxqhB==u=h4zo7vX{SaqyPLN@3#gzPu1GT`1{Al`k}ENt$HfAe`PV{%ALv7PR?Xkn@4iq-^cS?8N<($_4)_K`LwO=y-3gf&5tNo>K>&!<s*L7Uh}Kt{G>1KAJsCN`;XmCx$1wHz6X`P`}zLfp&uC6#reS1Hk!{D{?%@p&l|b?eOTK~x%TDHcs%bVxAOiy-ENxaylZsc+H#JY`{};P-wV+RruLfG3(e$l)7p*et9{u|=d*Nve7kYKDcX9P2X({OZKnP3@mG{PzwK@_)@g~nOyiPL%G-?3wX`>$&)rvjTTS)kPUpXCPTp)Wt>d{ge!eo#@qC0X;d7w+0Jq<GjPv9dY5tWRHQfGQ72n4(j`p{l@1WfFd})iZ9$Ulh3-)x=uYy<4uGlI2ia!}8$yfhXP*h;}NgzV;a{1st2{z9D?|u@*&i;RY63o(Tn5`>8*Q2_ApldOFAy~Y(0NDcMf@k3~vmwEW@Wo)^kAstFdL$_sJ{g=0UIYmahXjv>1doAF0*?WU=^qE52A>3;22O`3f!D(G;7Q;l)RYGaUIPivhc5!>gO@;pBjMrTaEu`m5`4d|2jHRbvEZ>7TPP$r1QI+N9t?Jke>5a`ysilNRQNdXRB#G>8aM@<4NnKV<|`W#{FJUzcrkn}xENdr&jaUS9t$DCR!DFWJRe*HUJnVjz?Xn6-~vc+1|&EJ9tn=bT*p9yWy5;Nkl+U)!OJ1RPryULPk@&~g45t3;1H}$8hkw1wN7b};Kv}rE8tVXE5NJaDd5%MC*j%PY^=?bkl-@I`jtU~cR+$G;Kkr#tXT!z3a$W`!;8R0ShI3S@OE9>;2YuV!RxV>8{q}uZSWF!0k{BbTmlKs#Tw-r)-Knurh;SO8Q^)k0(3nB_XEf3iqka;?hg*sHA2^Ykl-PZU~l+Hus7Hj9t8G+`$N9y-xqC0K|!b`7CaXc91R}{js{1;M}SA5?kGs`94HWTFb^C6zYiP$_Jag_LV_ju5b67uU=O%A*c)T>FpOVtysqJx<2bNuPKKkMa38Q2*aPyxJ%tZ7)G!n^3Lj>ud6;1=f**kd&xZt0hYtl$2hV`}fPGNk40t?vqOLGq6W|JX0(d4QI18Qw&H``HwH3Yvo&(+j-UJC=1y{fd?!5{UybKbY3ZDp01!qEnr$B-qf=>WXz!)Ba1V0Q3UJ1_vuLQ4yZveZ-xegM%Syy_hhi9<YfBG-i?_a9e2&Vslb^oOK&objD$LJjm{E?QP>P>sdQ~xK5*eXtH>EF|(&A<'

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
