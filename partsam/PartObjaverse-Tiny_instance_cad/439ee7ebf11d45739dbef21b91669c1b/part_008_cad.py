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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/439ee7ebf11d45739dbef21b91669c1b/part_008.stl', 'relative_path': '439ee7ebf11d45739dbef21b91669c1b/part_008.stl', 'source_sha256': 'e54181e4e0c4a952fb26f4bdae927a1072bfcc6de788885a6227b91e387a863c', 'input_faces': 126, 'input_vertices': 90, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.02528025582432747, -0.3719462752342224, -0.20026542246341705], [0.15518388152122498, -0.2688028812408447, -0.044445209205150604]]}
GEOMETRY_BASE85 = 'c$}q|3rtmY9LN74FOd}Cf+DC#MXxB3yp)%AcnBz<*9X3EbqVkliC&!5NIPcEMOs^#&X#&3e5C@K1q#yxn2$C$QIl1uS5vn(Yp7W(ExZ5U?|bUvY-@Ggf8Wpf`oF*b<NVL>cd+F4@GuF!hKR$DLYumLgpkcon8eCb+ls}-r4`Xjm%ZX9{K=P>q3=y8$hXXO6DvifxumqB*k(>v%&7|!&5??ELAh;(t!U|U<+hSi>1P#{Rg^mYibX}sN}cy3lg30UaS@TqD&@akzRoGAeZSlKj8nCs`4^AN`-rAisakEo2h!IqRbR<_$9?}}<QLa&BmbAP9rE5jTd$L<!&g_DE>WDzbw^3pSM8wqnO|R^``DW;)PH+D`$b(euH(r4W{O|uXP3UX&_;2zFH1hBaZ>J(uQt9!aqON|Uyvpid_?`9UC8lQsT5y$zev7%^#zJ=KRAZs>j4`3{VHi)x@XN18XvwEn#AiWzI}lFmTlD(|56mqN4YoWGx8riWdGIk<lD{d`(1tY%tIPi`~6BI{Vu)yW9lF1L-Q1OSDc{v?(nXm{d}#N=A%B^e3<_Kc|Y>C6YuhVdS2T{aSZ>D2Hv;P4;pA4^DmMwHdUXeaa;Db(eKg&c2fM^yk70+_D`i+PluAPmFH7`>$-l_-@3Gw`>)-_^FOzN_djOIZt~Zc@ILJD-%I1d*UH=}zBu{~&EN6cq&>6`8E^BtqTe}4TDY2gG2kT6Gp*qi{jRy-6N*z?O1|S!#YvjahlTrS+!`PDLpIWLSB`HYU$r%~Q{0U|(tbKl_1aJIv!i(2g@bv$K3NAS{&JP(udi#_<?4$qRz44v{)fn~z0Lji)N`EciG0p`&NxW(d3`$1Cm{R`>DYGm_dlTdI9BPruC(Ao6ep{OeCyuRv@ZLb;pB^31?(>wO1^SsBKP00mY>)5&U*4=wvw;sY~lIj#*wd=o#g&y4dg3fYv>&6wvYz$*Vpm;+g`P=n}25~$LR{J>*imv^FFLG)w}wlZ#=KdzJccHFnq5L^7XE`)2_a5Swp^9J&yOGf_?S-2--I#ubTEvf4Qv5b^ZeLw;tZg{$uO4djCMaiv3ZsKaRrQ%{1;!-cJ?#snvuvyY9b={a5OW*vIqI@w}{^SJ{8;`Rb9$$7x)g2gfx&4?^2WzP_2ykB0LjEJ3>KITSdDN=CfydTtft+`g5ryPk6$=UjNa!Ts@G=y)%b&R_K>zDGZKwUCeZPT;+>-kQ+j`u^It^ZRS~#{26y!tbxzv4?%+0R?$L*Upo#B5$b38_M;I+#h*HMV_%2-r)HlFIkb7w1}Wqii7;7dvJa;d?UYU$ZzVrVDgPTDUc_v)#KR@;JoU%!+BMYo5y}7=VyWZZ1@8CSw()fy4%=Cp4abko>v>+XaAfh*O9AvO{5LAJkJ}xJnq>xo#KpdWFK`zppF>6QFk=d9VO-%`>0bY>XhSNE02r1CQ#R`_r7Hxbx=bcRI-EHXuapTZmOu8YV=U@Rn%Dxb=EOtB>6^NR#2DKUBw&+_1!Ux>$~9__1)3Q^<50?;Qshd(D0q0`(Nhx_^wdocZH?f*U~&aVag&eA!O_6{90O2<npN`O?esm<WHr=@&D>mDJFL8|NK_+m1~*kY!lEVXFw-`Gr-wsl5?R`z*1*{rOp6Loej<fPeqeF6FLVx6I=kD3oZcXK&OLqz^Tyj;8bt|bSyXl90h$E90eW*9SR->4uuW?hl2Y+y}^CJ9#8@H0DD5+z*2jFJ;A<clKr4wV5#n4slC8bp91@V{m~?wpnbto`+-g15a?jA)FI#yaDOz(3Unk`0h^%_U^93WbPRYDI0iZn90N{-P5>u@RcHoS1!tj2o(#<fOU(sKoeGvZ6FeDgffj%*;Azkt@HB8HG!>i)PJt$XQ^4`iC~!PD8afOd4GxEfg2TaK&_3WWa3ItJ90>M-dV+nxJ<%lhhWdh~`hlhTgQc3ly}<#{5U|w#-~ezin&d%H1w05m0%``20FQ=_0*?mALSw+O;3Q}wI0>8vRl#ZCJZKhJ>SVA~3pfv)51j_i2d6_b!Rg>+XbLzP90!dD$AKfE(cnn%aA-JqICvm53_K7VB<Gpy=5FfoPk++?eQ7cwb^8PV@n3c?Z?3<LcHaI~>@2ySRN~y7|CT$oU7kqsCmETFtN'

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
