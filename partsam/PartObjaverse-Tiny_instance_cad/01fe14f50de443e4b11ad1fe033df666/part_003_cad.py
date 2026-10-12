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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/01fe14f50de443e4b11ad1fe033df666/part_003.stl', 'relative_path': '01fe14f50de443e4b11ad1fe033df666/part_003.stl', 'source_sha256': '52fdde6688fc25f0f9d12a9a218ff23766900417cb00f94479d60a62c22b45f7', 'input_faces': 272, 'input_vertices': 193, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2313297986984253, -0.2936820685863495, -0.10513322800397873], [0.23133236169815063, -0.07614642381668091, 0.18707001209259033]]}
GEOMETRY_BASE85 = 'c$}r0S!`8h6opR<h|GgUW+@=v0+pelP^K1?K?_(!kV&AHTV=+!q6ijnU>+TSQbZ<kfQni{23s1@U_vm_2cPl9sL=<b(O1u3zx~s$b4-lhWM_RWPWS1*?(XirH_gv$)Hp5p`_VHvxjiHMK>HwY)iOv6Rws)~7Z)Z=2CP`MCM9TF=evjLt5au8$)BAPtPa*D79~pxixVT#6QhcTCo<C$MJtO-iwjmPSXsO%>HG-=%Sw`=U-D$Zs$}@@jKSGMGSi3j%}jqj{XagMyYFGxq3f4JxpC&&H%@~ef4!Ph&kuV2@^zeF+r4$2f8&RSes0I3U&Z;sZ+))SeVzClE}gm>>+c`*xzi)!*X}C*EY1%~&eq2Ihf6Qk^;3UFS(Vd;__ggSzl_Vle9ggp&B1)l!S|6I%-0;eFFE-8N)Eoi<lueD!TXZKji0Np#N}YV=3u_&V7}(y`$!JvYYyI*9Q=JH2j5?E@V?~W`_KG4ha0Is)&0Nv>E+*_uI~rte{pJkoS*yqpC=mhx16{Aey+jyqjPw+qB?dC@gsAHADKh^$Q)W9okRS{9Gb6lX!q4QwEjAW=Ib0<f5~5c%is5r{MEPoeILo+UoZI|Sz28cm%sU%zxkTK`I^7)Bl(-J`FmgT_xF|jeSgW{`;x!!FZru)`TIVSzxtNH?<4v9>vjG=I#?My|M-#l$B)cEeq{cwkIp}SWd6<9`M3M({9AvWfAe+zt-sE{_<sJakIujNe*UeG&c9u+`+r=`@wjuDAK9zs>t4l=>{apoUbQ~DSH<^x)%xgOwd>_v8!r6tQ%%gd%-3^yU(RK|o=bf@m+vFzQs2(y`^dTc^>VI-<u%81V$Nm0p3D1kF7x$V>f5<|A32x$b}rvX&gHMyJ<zP8vhMlRJ%AtC1Nf0WfFIcd)<^dMeq;}ruY17mt9!uu>mD#)_ki`+Js`f{1J+0PfcSn7SRdU3cD?R_ebrTQ`I{ek9f%)!9f%)!9cX>@bs&D^b)fnBI?(Q``^x(3zA|6;mG#$sCBENR)<^f1_<mnmAKh1Wz2qN!S5Y08zxk2(W%!ZzQ|9aYDg4O$DeJHAr_9&)Q`TQ{Q{Qs)eIz&aEjQmsa`V^gp6^h7B`!DfH8=0;{x@IuKYnEYi|_Zp_0jz=zTf}WNB6&7ujfrvei?gS{K$Fn_2<-l{W<l0<mc3Uoj32xy!rd;?_cY$`J1o#TYt@8e4oGd(frNVJSQKz9-AkABv1TEp7@bGt&ir3AIZ~v&C~9yd0KzX(|pa-{Q5cMH~3U5>yP*P<+cis5>~SyEhs9e_mP$}-NQ8gBdx_l|J6rYS;Mma??+m%hTp?$VQr!uZ$@8-H^W=deef1|Ygid!^$n{N<+wB25AF<iLHom9;I3#U+!gMI-VJwyyN7iLIsm;J9srM_9FImb;nDCYv_Cuw9*OpYN5Uh}zVHY*8_j^T;o)HoLlbBQoPax`o#2jeOUiL8v@_faZjE+<Tf=S8u5cT;E!quk3%5hN!|mYq^|EeHIle8dG_(hL2iyZ5hz@`U!a3*|*y&U_2Y!fhJPUmko&^`63*iEI3Az||x&~eXKSw#<hHizo!TZsD@P7CxdIUZSe~5kn*P@rv58%si4SEKyfveH?;cEC(v=aUlzJ#8JFToelQ}9Lj0{R|&0X~nu3!jHS3F{pC4*D+q4tyAW6Fv;@MPGsU!W+>S;EnK8l;dLbMYtF)L0^JP;8OHuxD<XG-2^`kuSPe+tKnzRE$}n&v*=dX=^EJSV)$A3Ny_m8bRoO|o{2sR&xEI-Q(>oLV5g(uDez=;6g(NuLr20+N5FaTgOuY3&}{etcoI4so&-+}Ztl2=l;a7M<9jK`ccBURF8Fq|BYZpD0&NMmfbHQp1#JbVz^Q0!I2CS$wt*YLjnTGnW4H<04sHV9g0_cmft#YY!A;>?gPVKvR?2a+u$rSC&@{LM+z0Ie_kr(02g3Kj<Ix=0=|k{%cn0NoJ~|7Y4?lqxz)!%d&?T_b=ipWF2FmdsbQ`<}egoYPzX89E9);hA&!Qi~wr3qzgmo~iUFc4D7hHxu4?A5Bm%%G2$4PV%oP_70bK!aLbo61^={R^gd>`d_2<12{tikA5bR0a6USlc8(<sMt(7Es&xDZ_g7sAWX<?wQ{SVlQsM>*bs?u2*1<>*1U96nAtK7m%iC*ZfjI*A@aE8s)$ZgdyC8(xo=!DT#W>nX=8DaS=<5-x%tL+8Pd!H=NR;pseQk5G>9ryLJOhrmPOJ1NJ#(JZ((+^gPm--~kGGpuxU5IPth1m~h-VW-pJTsWU{JR6+@&xRjI3*pD%rRXx)={k5Ryq0pj9o+$MhYz6T@B#Q3dK^9me?&R1LQlX|@W<|4c`2!BjsEFR3T{3&xL*hj{=h)Lvf<md`d|5N*vr3(%g<}#c6|7YB(?5E$~5;31%Cm=(n?P'

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
