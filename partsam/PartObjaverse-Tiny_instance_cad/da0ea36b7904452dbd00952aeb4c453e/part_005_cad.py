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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/da0ea36b7904452dbd00952aeb4c453e/part_005.stl', 'relative_path': 'da0ea36b7904452dbd00952aeb4c453e/part_005.stl', 'source_sha256': '09a9830a6996b1e40d4f90514d0ca5283a7e8eb856e7c07c13539dc137dfe82c', 'input_faces': 82, 'input_vertices': 90, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3567792773246765, 0.03695714473724365, -0.4999995231628418], [0.32941940426826477, 0.4719806909561157, 0.4999384880065918]]}
GEOMETRY_BASE85 = 'c$}q|ZA=_R7{>>=%7G_T0Y$;OrND95<GjLM%bRkvh;4c4iACE~5p0)83lt90V$@{68ciGHC#z{L5Zn4qS`>^QZksfw8qyS6sI?TX8qp?(=m#slggW!gvv)g_H8Hx$KhJ-EJ3DXB&g^ceF~ycm__3Zec{AVo*-i+PgJhE<YIvx7zdGpc>wh(gtOd>vBfi_x)*RZKM2?WxoCnmw{b6U7;;iYaaC#JH*WvI`xU=u2!{Gxe;|-lXgDT~NuXOgS^t`0f=TXXC9_0<?zaHtd3;OWvT$J@?IcuSohFE>ZSk%OW%h|y7y3J!OYQs7&e{13!cCK`cpN<NA5;)oCIKyIac#_w1`|EkAr~TAKRN&V+-#0S>_YIG7KL7f4=+BPu*{B5%ZXY?zV&v#MoKJr~2mNck8-VLahk$ES+AQ?*p#4PDf@|u<6Hw29Z5G<`E{#J!R_`uG%{<Wh3H0-~o&}-2f9t25A6$TX2mZJU+~F7n{%7Z6t-uRE<h*}TD4%OP1?7IdbW<o_c;{p2&&r_%fp1tE<Lw@Tc7uH`;M#JzkjDh~3wez7<^T`gx+df+)|-udPROs`>j19bUJ>$`;J*ub)OuI0K)dtr3wccN4}?4_z25`Zr*A+WNr>k$((@(fQxV8l5c4SW4$Py{l|N&Z$C#SM`Gz~fyv5W^&K({hFS?q>dG24Qd0ysk3Ovv%<Xu<oSWk^m4>|tD1*>ss$Ie`^8kfwCadjL!30%AQ=2f`ACl|`gJf==Ud3}rRZL9J!m&=o>c4589+*mIL*Dt>Z;|jLnx=USmzSg2$nH%kDsU^V4r6qA5ByP+@EVTi+KC}KB@SVI}QsBE>Yc>A{m+}}aXysgb9wG%Va4zMSxK^jF#wBxOTtQdbOsz$JWp0cs;ws`?dQM`l3gE_iG1igH<Lk)X#OuLz8fzbcb(-MfI#t}efgAfkd_Q-$3EbEpH22HE$&VV;6Y27N1kZuHoA)Qa|D=zJT-tw1tFG{T{WQY!)v+jYF^_RB<uT5seKO9a{3_mh&V65<gSfg1?Z&yZ&zrdLJVeUJ`Eww>Uu15qm!N+dxcr{d{NHgdz3*gh<TvL3h1dUW(GBQVv-cd#vwww`$M>m`cbOY`*Zl<gC%?xNTzro!feii}|Ih*TXqa~;ki$8CCm4B`IpjSgd@W6W_TuOs8zD?-^lPcB)AXstAUlj`{i)RL|5u+%6=nbXQ>m5qp^Ys|jL);NVcd%T5voV2axmtZJiC^TF%><FDd^MD+wnd--kXD-UAu>{i6SH!quu1$wS0^Zqi69!^!e!XOl>5i^6=U-R4r7`Vcdnj3eTTFwP0E1>+pIN`f5}i-d~4xFkeGeiE~wn<(O~A^AM^M%NldtjB3MrcA>Av7(`z}<)-prd>p+8{U(eR=r^IS!u!iiV=2SyES8$emzwHiz8L3^<+u=IG5TUG!@QGfBb5uqyceSnJ&RjRz7o%?(U)QLp)W&UihU?F<(l~-jHT#{&~L=(L(kUdZmN0|^Lwdssn~K|gE0yH9;#=lwqbk{Jv*|fY#1Lx-$=ES>M5%2c+R|o>VB#WjBC-~M|Ce%Ce;IY&U_Qq4yp!>PosZ~DnM0$VtzAWTMXU)sr)GB%c<63RH#CYNy*tM|MUx&I5akR;fGGXQ{2wXcY5h*d~*vmu3>AGF1%ziK;wBfI`TIL6h^K'

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
