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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3eac61535005406885ad708b4eb375e9/part_003.stl', 'relative_path': '3eac61535005406885ad708b4eb375e9/part_003.stl', 'source_sha256': '28db8b24709b4891c953292d7bd7d599e8660a5449419bdafb84fbbf6a7b7420', 'input_faces': 64, 'input_vertices': 87, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.050571560859680176, -0.3958725929260254, 0.07818611711263657], [0.03330647945404053, -0.3676883578300476, 0.15645846724510193]]}
GEOMETRY_BASE85 = 'c$}q|ZEO@p7{}*c+FoA}#N%DcwiK?kXW@=3y<(wTia<FiCvDMc)GO^ZlxVrO1R;iIQHk1Mi7|d@30|wlHu_0PJdU((ulT_a8UunTF}<29f@$mr#J2#>%=7HJySFArH+k~^&u?d+d3I)Qx(x<wb|--=kL14ExM;{h2#XxzB!|MC2iuy%T_x?2BNj4;b9O2EdTqnbV55Z`BG0*6!d=asuJwYeqSfzm3$E4!od-Lc+Mhbm*%D@aOViU`VamJqHATX-UFa`!3u{-og`>iMy|P#hFHQ}AOhqaUU13VRAB|L+aN+C+vX)1y9^+ijNa*=9f+?4eEap7v(dSpVnt$_g&V_Tgpq^`m2{SI0|30qe()7<T?w9H3wVXUUY|2ADgQocvuI7Kc0p9Dfk8_boaWgJma*S#@$t;2VIR!eNTzUN~{@kZ6aWii0FE)P1xnLMq;p(`~*+V?f6A`HM+AFddC%bFmeYZJ)x9x}i(~ko`Jn=5iTjMq74Q_pY16T7$MhE$Px_5oe`SX{?wOqcP&AD862l%NsI46HJa4sylpyR@tG|1C#gLV9^nsaII9a!HF9~skf@oEBi?or@3^PrwRcAh7>qh80!*a)oSaY@g+D}a;9n3l^g*dV`S#aZBY2YB9&O|Z|s-^8?BK6#t3SLkvv^#Ac3=fraXxW#^k^O^0ZwBr*0jS(#u6SrX9eLZnAp3Jb0>iFj~oQw9sxEWXTAO51B=M7Xt{l1@KS}s=Kg*=ra)SpcBYu6=o?8z}LkM@m1{qY{)krSMUJR3O=wfz#)a-l2@=Ch+5@?YuZJUNf>{L%jAF)fewo`-!{_Y&|}dmran7hyj4FFd2=vhQX19SuJVe5eTc{LeU-Pv`4+w6GWE`Dz5XnBC3Wl{HYOEjgm&IB%hgzv{U1UZVB2xEVM0SLRvvzaKZ{%DB<Jr<tal+Xk+ltH_meTl}+M*I&kSJB1t1Z39>H3wdvHExE~gwA7z4<H;M>$F)2ZnudAkE7J8BzJJe@OAFpH&987-$-htHJmq{wuAI;6Ic(tSIgC8z+%|Ay|CDpvz}0$4udYt@@5{`$Q9eHtQ&7L<q-@6JvKp8Nd5Ux4lL^SvdJOu@=>xof_mG~Sn8mr!@|Hfof%E)9-B-?r$=*rHMjxS(NxyPhn>3#|46;j6^G}>M-@p3AS?BxTpE$*|hUGL?@U<YMfJQEAK6*FXo;22=deJ{XgFWv-U5%dQTgImXbSe7#X)LC(1a%Smr8rI=YCd`&jde8EqL!jxjpKVzz32<@9o(oT=!>z|<*3Whr{R)W(A%+X!?qRGf}Sn$LK^p>E<isY+w)MJ=(B00)5t)dh3!miJ5V#wSJT)^V>9YD^jq-WL+H0+`(YXlG<KuzL0?Cs9`D!VJ?1yisG_kEbrX6K?^U9&!uEC=J7@$^YtipQtwmph?R#j<p)m_}F8X^>=c3QSHp^L#d6+(kp7mKpV>YS_J<C~$d6*WVXEjvN*onFxeSn4^>tkAmo{hZ{>kS4hR;TTs{zduwlGrBD{lj8>Qvb8pKKTR9r5*yoKpNWvbVFH52h{;S%3plT2I~'

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
