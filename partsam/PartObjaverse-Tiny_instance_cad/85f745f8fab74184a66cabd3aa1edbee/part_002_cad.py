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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/85f745f8fab74184a66cabd3aa1edbee/part_002.stl', 'relative_path': '85f745f8fab74184a66cabd3aa1edbee/part_002.stl', 'source_sha256': 'ce1336b30207d0483dc7cfeb981b54c06eb8ba051d8308a6ba4c98c01b403dcb', 'input_faces': 148, 'input_vertices': 109, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17337720096111298, -0.44095176458358765, -0.07902094721794128], [0.14286655187606812, -0.22500254213809967, 0.05863681435585022]]}
GEOMETRY_BASE85 = 'c$}qJ2~bs47(P$ITv&4j)OSG*Fi>#?1i4x%n}`PHhCXCbM2vWdW0pKiEuA7sDYdAlW+)X&nHw(GT^q|>E0>u!n&~*zRE{>IWu5b%@6vtO*GyAy=9}+3-}~=>{&UWM@4Jwh*3zp3lb=v_b@%rrJK8cP;KMqwih{E8qPzlopE;%TEi8b1@zHr@M)v5;i56DD7KG;)*z?N5<CXA)!r1UACA{$IvhuRrIn$ml%P$cA$lTfX0`A*q=9U)laYRhNxF}^nWR&u}@*h8<3R_&vk$s#s>*%kE$7>q|JMu!vcc^LPv+lQwiQ9j6Sg^{zJ1^LF|C=>Q;<~U5=~pD5B|d+E^4OLnOMk`+8DD>O3+1^n!Y!U{x;Tr*CBGh`Iy#*q-|6FeOXPReE+b#v^a1%w%(O=0y1C@rwnu+M-^U%4`H$JjXMa5WE#>Rhem!xUQW@_neRbzc&l0biNWL?)lJc;ItrN&!lt{i~gykz@?^kN*`^{0Zp4{~muU$O$9`VxY2gwf#K278I`>dk));99Bii;GlOuI*Qs`vZK_`I`Jk1eBqohM%%^ZN5t-*Z15pnQ`%lh4>Ki`XBw^aA;gGrQzI=lIaMr~!w_S5J?m`n8`UKcw-QJu<#2mh!lstJz57pe^KU=MyMiy`EA<d8XIOd512P>srySf#Qpok?&kT@f2~tXxblTTeQso##UL+E{)c!YzV}>Lnx1Pp0!rww`JelPxD3Xmi<<8S;oKlz4TvcB44T6u$ua9(Mj?hm-A^}$J)nf|CL9MNWaoXK70AxDB{W$(r?dXexH!pG;Xm>=Ks)N_Wz|%sc)Uj=aH}NKPb<4$h!+DF0I1NS3drc&Wp`1Ctr!%bB^}&^O0*solYfL`Yc5DXMCXC=Ou~cyDo*wemik1mA?1Aq0#(N3+P;&N4GZ`eb%u^`awtOzF?hJknf1JU!XYjkJ)!*$o^3(hsgZ)GxEMT5m0CJRiFK`uQsR8r2DR9)?PZlK=e84(S26`8u>QV<EY%VhvwV6=36<htjFwY=x3$6t@K;pr93XZ9{B8+>vDhUP)}fS6V)H~k?d#mr|s=5^0gm!%KH?3?yPCtL4MU|vY&DPYVjAhQQWnC)Q3vL%Ejc@z43|BXXT-d9{tN*->3a=b@&7N{?*t^G~bjQ`Fwz{-hNNsUxUJ{-TbT^*$;!=eOJ?Q>K|>Y%;WlexAd#tq5H_WD1_o2r+RKO&db;xrzc;v*Df;pu9HXQxvY$^8+~W+3-a7YEv|L*$2(-5W`BM>`HmX*JbL}i;$DyL+vcI39zE!swJ+|IuTIIY^W;17N|)39zVVvV(|XOmzFyrouUGfY>uvT;>uvT;>ut_&TCdq}UhkFVYd!Ue?wk9h**Eox?wk8W=@GG<>hKAc&$o=b)ka_W=w<33<~O(AEnfG-j=!E{@bx}-Y>(e+jJN6iztOva`oA$`Rg#BuH2clx_-6(^@6G+}^y;!Hi9LAVJ>cWMQ)@D}7=8WzwIw!uN_F{<`I5!~e$^CbpSvxI&e!)O)!8Lq?mzo&JFUB<UjBY{mOlHP?VvgfZ&DuinxE5?@3h*MP@ZEi?xebIua<eLWW3o|yUTbbA)$%(W9B-y{AOQ6e)agC-L$SF<&;N5ezR{we&?a1(x1Oj?gQ4VRHyDGKO@g=y{^6Y$k&dfe?f80`<8Nm_UFop6BIA<WV*feKB`S$T>21W0&VzPZ(*+Cl~<VJqqFB%-lBp3?v;07?Eih`?agcG$ngjuv_BwpYp^f0FP7OF>;>JAqbEmipeL^D2<;12pcPy%bO=Wfz7N88JyDOSBMR_GtUu-q0eeAv;d-INkS7#ug^u6|;OGMcAXac2=r*V=46Hy$as(nr1atrpi0cHmg%)gqwjh_#eNjs!5Q^&pq1%G3&{kY8bbF2-94)}Dpkp|CaYO?`cLiIat+-z3M>!tGburMr!0n*hVcuR~D|BDf-3J^2-5Y1t4;%&U&Edz<5@#g%AwcNPU_a<?;4WZ4=q}LR0ilDz-q69&`o6S6?XBQjz%8LI(9BSu_;ljv&%~dtjCBAH0E8Y0?hhS~J&gv(K#ONZ3daaQ=yZ;892p#A!RgRrp)<iL&||>K;1uX&=waX_=wZ;YfY5P((DC3A(DBei0ihoUr$eWsR-s2@4QU*sI8ssL80btO6>CaG>{#$PXffAgm|yU4Lp{S$uV58A7MuuHp%bA;0V?K9g-!zxhfaeY4Sozdi(@>;1n^|&Y>p>6CIUiF0-i+71n4Y4=qCW769Az{g0rEs5H}tWdN3gLAaDY70<Ieb2t5Q4`YCWWbT;aK3J`h<Aao9R67(djCkH$kx`?BYV-|R(K~Kk6aK1rL!&tD*pmQ-6oM+Gl7z>_Z&_x&*VNRiEa}>iXMjg7Iit$v`A#`S%rA3F9|MV}azdsIoU>pBoWxmq=XWn?_9iFTCM?W*oTReOC!>9#&hVwe{gk^sLs9i$y'

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
