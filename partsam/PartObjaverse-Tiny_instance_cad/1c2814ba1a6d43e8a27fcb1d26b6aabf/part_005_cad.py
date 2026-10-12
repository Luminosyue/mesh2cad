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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1c2814ba1a6d43e8a27fcb1d26b6aabf/part_005.stl', 'relative_path': '1c2814ba1a6d43e8a27fcb1d26b6aabf/part_005.stl', 'source_sha256': '17be7ec224a3aded9e9b5d894be2bc6d9f7e54be088122c117f1697e13983956', 'input_faces': 280, 'input_vertices': 172, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.45842525362968445, -0.3752433657646179, -0.4260212481021881], [0.4584486186504364, 0.49999961256980896, 0.36559054255485535]]}
GEOMETRY_BASE85 = 'c$}q~dvI0N6~+$<pgaW{<P8@EB9DduD&e8IB@i?LOhG_iCIN0V0!auEM1tHFg@`-~2oe#v!~hnj)3J^%R&8!;i?q|0m#HXH(&;~)P9HOl)0xgN+P%;Dt=oMUr!$>4Gi$zYeS4kn?6c0kn|&`O#hLB1yx?!B_lLyj+(Zx0v(eSd^6Fx>>nm5p*5y>yY-;EA@OAqqcwo-_*(HnGd3E0A?3J-~D{8YRN3y3@<YkYEWLH$zuCFbxDy^<v8MAs}`Ra8sqpy3iye4Myd&W&1KPEC^<e12o$p84)*-WABcMGn!SS%iQF5gb=Zw1#{LiDo!AADpnnmOY$tCvm7Nm@)!Ui?W*h#vju=G8DgapT=fVLomB|9siiqXVy=4f7XW`-`sqMc4kxf4u#^pU*2v^A|n-m(Q<;>17}O;!>DTJmZTr|M=LWKMV60UHgl!{ZsY$dwbr!7S?~QOMkR3{n5JgM|9nPt!sbXf30hO-G8l1f3z<Bxust9NB3Xr+F$qomU?-=UAXVxzxOMfM^1bdyho+Co%k|TPyBVR?^8BycB`-7%nau7)QnI)S-Sp;tH(>Gp3e`_y=zh5Uwo2pt-ccGuXXVeUHgl!{o8iLF8b@|%dc+ueK~vG&$S-;<J=$n{kwYOC;s~2zKN#$FNf)6hhtY<J<5Evp8PbJkN9}Umi;KqU+dx{y7m`c`^Tqs_+h@|BYn`i^iA}r>Zj=9FFxLu9q)(vYh8Rq*Z!hw|71f(i~l|{uYce7t6UbW=ZR;1J$~uExBUCQ`KL>+o*eb@5Aq$|8~%>}c}PzAAkZ5hyPT%4>h_+iC$qYqOY^Th@f%l9`J;P>4yM(|6ZIFv^hE2bR#z7vT`#)SCpNyEKA+OUG(9yR^knnVb8g?-T4Nu(y6!_tSA9qnJ$OEC{-=X}itdeOp6JP%4}YE3hvhk!T|M=@q8C*C)~$~&pwH;yFM8tCKhx?H^XUV6YCh=RGVem@dqLOzkEnX-e?--bp1hWEA+*ovxAa+bz24@wUJR`lUDbOf6a0SbeN5}JkF{NR>9YG=kwroOMVG#bUY0xRiu+vg0g0ggOg#9!p4@uQ{k&_vtT6aoiym)Z6zo?@kFGuZOZW30DJX9Z^Vhogh_3xb*Zyrcy=(salYME<;-9yK=<#ul$uQkJ@#q_&K0C*}?dr0RX@AkRe`?=T{wW{)BLmm^dRakm{)s<yyMIp5x}0aUF6SB1ql1HUj`k5<`-rZ6l3xVp8LvDzKWJUfCt8>DiRkg1;M}5pMAtr|i%)#lzQA9dXX4wArt3#KeiEk3xk&4&^H1?l)A}jrOs&f~Q*`N@t`}X`OMm1XsC799iY|T7^{M_)pYVEr7B+va%X~!F^Vhnr*Ynr9o{yft)}_Af&B1B&ly$3hS+`o3bt}4F|612Rdi{&8*T2?f-D+Ldt>}9FYhC;3^`H2Btgq|+P3yA%XkGT7TYT7mL{FXHl)vcOUv%xC@{#@RkxAG6=acXCjisNqgy{0UzAbOzt@R~oziw1sI&ePG%?z37<Yjpk<?c@#-GVZ~@Sip+@BOcS+8Cdg`~Uv5G0)6lxrs->`S5w*qhN`{=aXAp;PB<-7FRfY9{D^xET3y)hKXYE8}K6gj!b+LoDMGni@~`LpH4m<FX2)0DE`8W$cyl>e6fkgOgs!e1fOZ5(8MBeA$%tIFu2&^3&|JaCA^Tl5P#t_$!FqW`Qs**nkWUA!B?7C!uS%#ET3j#wuyXj7Cawb0M3Cg!E+Wk2R@7Imw-#*rPQqim%x`&w+x&EFMv-2XTu+No+F<+tAE$T857?IpM!tP#N8&|06m8fBe&QN-j4hX_#C|4M45>k@au4?$pOn9zKwhv*9gCh{4RWi4<jFjhvlP9j4_c7-UA<DVz`M>;7IrgFdH20@R8&r@e)3qd^rBXN05)e!}230UNx~9tcP!gKMQV!KMOww9*1vc><D-a9`WoJ7}Q#f!v``}4{n7IVr&ao4<E`{9NYrmXW|7D2f!EM2jDM(yWj`Fec*n_qd&D42g6^4?*fOw2bkDNJ_IiJ*oE&d^!?OCxGuu8S>DC7KY4rJ9bgam0BX8`UEz07GX#vlyE8Tz90Ko;S7+yborx}7C%)a$yK`N4$74UwvX9tF&vxSb0@xpJ=hl<?_2m6o-i>D&1P+AvWNaun2!7NH)@1@b4)4i5x`AEcaW7aK3Gk@H>&ff!viumHN5EI%Tk$#$Cg2B695S&1tb=cWKMihzKMg+&Ho`YBb`U%a?`xtTwHBX&XE9a>Zi4q_Y$I3)@5k6P;70gv6VIF23+{mLg?|TZfbRu&gL@p0UesE=6TSo90QP}@&BS){K5)551HKLDd#LHlb$xj@%QH>1H*p(yJN!0yAFwaHBV%`hec-+D%W!-%h)k}_<eHA?9l5Tf<FSW1?<Tg>o9*~M5B7rFxpiWGop?|3oLSs66K<cc1K1nPf_Gx9AJ`lIvKOq&SHMPiC+^(=6mPpGHd3>Z>xI{m*WqRPVLT6lhv1v=Y6M?_KVafP6O+Kn@H`U}O-u!+!1KUK-~$eyLOumA;S<Rx;x9apJP!}cSD9FC;tB9cc!i0WiKoCycm?<bxXR&`<dt{{kCDgl7hXYLfrsVynYiD?IB+~X*Th&8_kt7Px!^ePK8H^rpMaO}vE*a%7oJO=i-+Z>O{_EVI=CL*Y@)`*YhX3J8GIc)?eJ>yYP^Kkkk{ZZyqUZi56e%QSZm@GSPO45QDx!;xCY(?o&rxgd=2>;yo6VgSK%+biM$C9%S(#eWn^Xkr~kVC_g~yUfV%&Yt*=b~TIgQ+d*hY*l2}sQ!R|L^1Iq9x_Ky7*+4~piHOJW'

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
