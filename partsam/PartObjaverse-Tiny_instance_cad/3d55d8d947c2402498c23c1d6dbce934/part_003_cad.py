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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3d55d8d947c2402498c23c1d6dbce934/part_003.stl', 'relative_path': '3d55d8d947c2402498c23c1d6dbce934/part_003.stl', 'source_sha256': '43af1dee8f75dad629fadf5e0e2124c0ceb4303862d0ee4de7a627fefedcc962', 'input_faces': 132, 'input_vertices': 106, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.40730804204940796, -0.47298264503479004, -0.4260145425796509], [0.32808828353881836, 0.21695977449417114, 0.15413829684257507]]}
GEOMETRY_BASE85 = 'c$}q}UrZEN6vi)$e^C)C0u|I1!NnFuz*<m*Q4pyJZdE{}tspFFYk<N=W2$jtViVKE){vAMVj;FoQ=1rLO~e&ps>MI4kh;5wtCpBHKJ=wF(e|M)cFxRq$9u;$Y1$zt-*3Kq_sp3y_wG(`mqm_?W9BiB9d7R|XpLfwVk(PcdpvF4T@9Z0#m%kzB3O*!)4{c)qO#mw6T$Yd4_u9&_J%gsa;Gc5Dc6<ZbTzfKdE4rnx3#o2ddM%S-`(!f{q~*ptseb6J!{Fb3}?>54Cevoe>|uPtuprR0M$~nW{gxz>NC!{|6q&hv%gjbL|=PU91J(V2fh>YS@)5Um|yi5-4lJD=Q+Q&FCgaUeh+*r|1#~4@%gI39}7vlu8$h$$M+gOa};!vuh@M1d~JM+;n(G#H0n@?N^gt4HUFcvp>RGMHs>qpzmJO7Wv6F^!ujgA`=$9-9@~8Dx_o}_$=hO`%864WqHo>r+!LX2K3o1+nr~gV?_nsMuiEl(UwJ_u4fXV-RgZ-0gWc!%#eI7p?7r29()lA|9~hpC-RIAd`}XH(_pRr6ZYU_#-+ygX^zG~CLBipnRFBPnZvNF<SHtZK?mxFL=1#w5^!KNu=J}!0e&ad(kYf0C4~Op?zOPF1)o&{9iaztENqLm`!tagwWw}xw_46#r=XtoV%{pM_>HhU+BmeBr`bFRQC@&=XYTF^{y6V0?KEpqARLY}%`dAZvo`?Ia@0eWY>{C9`x9Wti^`A87=T)0|YQHn<`QohPYd1q?e(z1gS9m|i?q3%DI^IwC%JosX{+*o{Mc=9)K6~^;t|#el)4w*+Puhb#%AotQ=<__>*V>(aDbL<`)9<eHOMOm`?ltP!w!<&2ldKxax7G=K*6^WUy05{r7ewE>FZgP4hg{FS)kgo7uJeAepW2Y`is<uxa-Ti9CilTPLGrCWz}Kz}OV?$0d}be}#0I4Gxxa5f^sV{umFi8h|I}fwE7w*zPs{ELqHnEp_}amD15%&kB6~&O>N9*bsyQI->l^3J8~FoArFyjJE^|Hfb_JyV{P~OITm6BrUGxRS{;LBYUlD!Yf9|s{BZAU%oV?y#pPOd|r9PyM`b6LA1AHxgk({S_!2I5*Ul$bX*M|R)e4dB<?CZ*)wBH~1Ul4t3zjNQ)B3+l&4PG+t|Gk5fuZ(Or_j~gvL9suIcgJPX=l$Wnwy#6#gL>!KCDFI`1$<@tSMq#st0wx^eE8bfZ}R=#n0ZO`t^0+~nx0DY*@9!5=v(WJe7E$rI+j%3cxD1)6qEJ0)uwvkRh3LSxQ2gK-L>@Jy{hJ9|KC^DY`q4$pH&Fr_0S6NdT=%LEpRn>JG2SB9oz`r32p>$h1P+$f;U1pgExXppvB-4@CxWM@Cxt}=&Rr*;6(`Hbm%MKbg&DW0d|2G>aiG_1<e3wf%BoSgY&^_p=-cv!JD9!;7#CKXg#<V?1AnAd%z9Q9pDD=7U<jHE#PwK25>oewH|p;1-b!D>IN&|0%!%8v=CeX&V*)zv(eK`=t6KNI7jGp4m1y(him6R3&2Hstka_mL0p9(eg{Fk4MALkAbt};T#6uGi6DLrLA(?}yc}8t&eh`$_H4Zo^L0qf*D5hz&%}Jq6Z3sR%=Zp4-(SRh4-)fzO1ui13(iEJs9)ps7_UbfbOCsx9`uzI33Y%Y!4U{zemIcNfn3D%^hnX;WoQz3mLAC%PsSKAeQhRSJON|G)AfkOcr3<<C+iV~@hFTDN9z%T@feH|&(I?t<M9}aMomc=Pr?|VOXqVD#Hr8}a4OgdO$Ix`iO>XaB6u1!7Ca3+2^s~S1fB|w0Z#?bgvNv8QR__9Fb6fxhCd&g3QonG`KVzEYMg`5zXVMLCt?n<yDY*H7x|)p%{)6)S}f8(YV4nse<sCGp4M|&Kbr2c@y1W3L;rhU*W=VF_7CKr1YH'

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
