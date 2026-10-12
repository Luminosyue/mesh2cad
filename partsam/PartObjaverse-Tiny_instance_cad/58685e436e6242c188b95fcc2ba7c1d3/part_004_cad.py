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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/58685e436e6242c188b95fcc2ba7c1d3/part_004.stl', 'relative_path': '58685e436e6242c188b95fcc2ba7c1d3/part_004.stl', 'source_sha256': '7d5570d764fceac31da0b6015c5f3f1ff5fcfdd71480824d03840d37172c7c8b', 'input_faces': 228, 'input_vertices': 177, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.5, -0.32187381386756897, -0.28613993525505066], [0.44038131833076477, -0.10923919081687927, 0.28612637519836426]]}
GEOMETRY_BASE85 = 'c$}q~dvF!?6~{LaA_(#*!D=bxg3yaRl=nlyTx@*QlyGSQMIc<r!z4(6gi?Z4uF6Z=3N08xK`#Lz5)yGbV`oZBRv{FnfC8h81$tXcM?3Abop$8k?%DnPHoNCuW;*T89KIjEIXU;YzdgU-{^llL)Hyfb@~%PFuBF@FzpamDN%XMtt<~kVtEx)N>+Y&qQJ-V=c73^wZZDoQBR((3T5UZQEi11pt&QFjiB7GU932^nRxGbwRlB%m(em1|a`7Kr{A69Z<JVO#UQzD+f7qBwlSW3y-8nMybmV`$ZuUlzZgc)g?$~uv)Y{YQgSITbePGDRpl{(PCJZ@Qkj1x0^!gy^C-#(G$XW+q*NK$8b>98?^t0{3e0!niC(fN|59Y`IJ>2yp#lJZb%uoNz^And(o(SgKZ(FW!pIdM|n4iK=^j&iKSaAIKR>^|n!8*yKi#~KeSIt`tKlONZsE%cP<|lpX!0&_e9H|;{wk_bB`Al9Pem0n&qE1Zb<0r^ZEZua~&8JRk=f~d9@zdLRj`2@E4CPbDR{5rWjQmtX`{iJL`_Er~)E4kfeXI4$k3#v>NvnKQKi%Tx+ed!!X{i2yxcA)f{rcBto)6~RrjE+@>;K8iPi+19#ccJBulwKly8n%@$K%)e<MIpH>L-k^>Zkv({6e<+HomDJJ9gw^w)JIvy}nWlHoJao-!IPx$7B2me)6*m?Lj})==tfD7uth$lK5skk*?2N%(i}wuh(znvs`cdQznMSWBeGtb?M59pl?t1{8+`66Tvzue1HDWed6A~-XDyw_lNYpnXaGA>mC}9@niUr>+c*7`sps7pV;uu@n9Vr-;5_!yeXBfzVUT^<LmmyzfpbN|9*Y7FBxC23(KD8?jL%b#@FLCz8<IX^*HTYtIri=c`nA+&n0%>3D?(sVtm~v#@BsfeBCFJ!ujrgmeIHPx^I&^%UxfuBjf9JWPH7jjIY;G@-HuX`>|Tr#@FjQaeA9qU+-i18T%N1#y*Chv5%QLdLP5j*vCvAy^rDRea!yrj*qjA-}o8(JbuPLkFWdLKHqpLRG;^b@%4Mk&sXm$<LmcS>|oia!TRPsYkd8l_4Czx*7*88o6cSTyWn&5&k6V$=LGzWbAriN=LBo&l~8^E9H@N%{Dz-#4phE>4#dwm2bz3+4#dwm2jXX(1MxG?f%qBcKvPGb1MxG?foA;r9BAf8p99T!^f}PnuQ~_XvClm}+45WW_xm3_b1dK|-`?o@=`B|`wq@~S&t2UZtYa4qaDDr4>l%XjDg4M6>l#9z+qmqs`?-UQQ^9<Duji)*7N<h>|FOZn&*Y)@{h{&TN1EFAhw^(?zVD7duc|4Oj~~meY6^{K{g6{`oz`e`Xgtq*exf<r9L!JGyyu;JT2CDg-7kKm`PAWHexz!)+fT92OIw2Z=}OPHu9da~^OMuAx&4t;^<((yL#qA@>)-S8!{bkH_Iyi?KY6L(T{r)x@cbl>4zj)bRr9=M)iJlu9qM^a?DuPTJbw>Acf0!jU%B<Sdi@ibaQEeG{bqdKZ`wEgW_;am#@GGkf3E5`zmDoR-&g(Sk4N>JpRfAO&sY8Ck4N>JUq|(u@pZrX_pAEN_`2WxI;!9NajJeZzV0`_zUnu>zUnu>zUnu>K7Oimcz$#r`gK$v`tzpx(D!f9hsoQoA9elH|2%Un9{N`0iQQl98{OTqB)VDoR>k7LS1Mx4Wi<O&DplkEtFKhXj-CAfex=gvjA5%2Z=yee--HjMKY|a!Z=f&0Z@~M|P4GT=FS-HV3%`y&55ErYL7#>9z^|g~;8)>Y=+p2n_+|7d_+|Jd^oQ_Ea0B`b+yL)HlkiUX74$jy6?iwg9^MVVhHivkgHz~cI0ZMNTi`}`Kl)>MKYRdv5k3Gnq1)gl_z?P2_z-*;{TX~1Zb7%hEpRKk18#-iLXW_AI5EJ9!RYO<Xg^rA4=mal9t?MK;z=i#J29IOevA;Fg|38W!Nr7d5n2Zq!4DI{4>+-u&wGLpE+vE)5yJD)+3<Y$dzNesmNnFg96~r39R`bzfOFwIC&oL`)rm1^9y|uV3mpO1I8o`uGPDd9O~9fHV9~koGI)*?5yt&>Lijd9IG+&ijpo3;VYzxbA^YYngz#4g;adseuMxuEAcXI8VvQ43PSm62u;^k~bRoQu->XLp;I(KqAzVQSFCm0W&;qywjuFBG3E}>P@K*`pzGzRlFWk%W)`j$U)QPc9jC0~{LU<%P3LXjHNeF)vjlxlC3QM0zUyMdaz@y>e=rDLVJOmvIN6<m&P+0m~`utJ!G5Aq<209BCErw^n51~b{=)<t+1F-1*@I&x)?q#CYu`Yzi6T*|wd*Dg%z36m!IyLX*SxjK=$H7z3$?z0-8afr81{b2=f<+&M3*kr5Z^Mtkar8T|=u9{cKaPGE7M%yrMdzUNVA-Q&Uz0sjdQW;q_G8(5WiK{;E8HI)V0HAi@IW*Qi;jXvF<%4GDOSfC5ssnLtd4agT!I$Dh0H|>8i(WDPf6fDOV9<dXu|4Pv%*WzGOJ^a3s<0(R>wXdT#eRP9eaiFT67sKx&juhg+*7vqCbGw!u9BCSoHgFJ-i03gGE=uD|v=%(50|EyS_ZnesCYO7u*Ln?^Mw)gz!y-a5uCU+zsx5_Jn)D-O*d%?(ofoa92V&j}SKRK4J5&6qYMql+!7{^Ns$5*>NS^7f<jHn))}x$MoQD&UI?}hxT|;7a5l`L7m*meplXt)_(xRVd)q'

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
