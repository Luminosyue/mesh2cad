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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b8915325eadc4f86af543daaf10702de/part_003.stl', 'relative_path': 'b8915325eadc4f86af543daaf10702de/part_003.stl', 'source_sha256': 'a477e035c9e83417d1985f3fc49d0792d037ecae7770d9b23a69052a56eca49d', 'input_faces': 256, 'input_vertices': 169, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.14464086294174194, -0.28705090284347534, -0.1623493731021881], [0.1313629448413849, 0.2812930643558502, 0.1623634546995163]]}
GEOMETRY_BASE85 = 'c$}q~d2AHd9mfX<hmA=Lm@}jvleEUc90uE%bC(26z(C9ujuKeFHaLJWwqqb1UholeQXpW0IW`1{sX`@`S|B;F8yk|8R4R(9R{f)rs~&$;g8tD%J=C;2JD=b9?ay1OY8O3yKK|<GVdl+yZ{Dnni~2m4X1SjX>)gL){%lREWjQUyO0#N9t7^)(lvYoysNC1fN{!{tM|g7SswKs1ds(&C{>+ln>Md27GwjS+Wd)hpc4pbGs+y`z6&rU|m6SSp;ietcrO~{4+osCW=+EPF@~3CpQ?s(|gZBUUNsgXEu(`e??3~MQKELZQSTX6*9V3rSOTOzf@=#~XXJ&oZH@~_XPLPLw{_CqgBbVdodda0ekn|uDJMNF}-#5=k^59dC-#5=Ec>M2Sv)<nO`Q>ne+*<bKWuKADadf@pQXgsj^KJ9G?AiC)!U=L~U1ytFFW05(C71eO*_K!ytV(+j*Z-0i?D&a!z5a!NY&YuzKghZiPLOvsjlbkGbB@!ao?Pnf+}w7v-$GXBC*cIS{jl>BvtIg5*L(d;eb@6lZ^il{dE?jS^-6A?*|s&7%Qzqp{m}Z_><6nf!>zAvxgM*(ayC})<@Z{@?=y1$zAtW?{bSqnZzRftDTOzDW={X~sF(XfedMn*ZkpE>xijHHI6)q)%(-CJhvqkZ8oN%$pXAoVly+Z&T>3#D-|HVa{w#OgdE>K*@u%`Y)n9I#_1^eY^^!}ypZhG=)%EDs$KeFImDTpKS?|qj#)r-$c3!(#@6C5rFS)Lle$eM5xtvcZ-MydQedoUFJaqcr&A58G@4B8`>boAg|G)Hu%nO}+^MYK?Q`bxG&AatCu9@>C^oP#Q*w0VAe9fE}U2P5VIrBpDVCnW&a~uYJUv-$dj6=yI|8&=H89xzO$5q}n{oH3hBbV``>%Hd!_4XcjJ(lqx<6r0Yp?`$UdKnM8-dlgD_g{C{Kkxps4(hxs?@#S<^>Tl8y{w<q2R~(A%KiPDJ3n<E`0dP_X1#ZRRlVd=A2>WZw*JX+{PW!PQRkt_6}QZK@49%d=-ggWa@(x;<|*s2&LedXB4)k!+-KjQ^T?ov4zpgyn~YnX+uw9_#vPyWZ2z?JZa6{iU(|FruAX_}|K%6)_2hvSU&hxnFM1rGyvOmG7yA4q*XQr;b5#F$^FsBHx9+L__trht|K2#%_g9`@>i){O(&NWle;7Z(YMv*0JgeLr&*VMEv&y~keAL}{==rE~nO|P6=A+KN`MBKO$LaM%=dwOXuGbTtd+W(B+<mKF4|Oi<o8)>u)Vb7m`FFPZte)$$&LeGKb(r;f-PXC(+rQs%&1cLbc`oSO&Tj0Ct5?qvolAY>%yl<c&ncbDd<i}4KA-h-Q|Iy=lw3a_1B2XsnSQ?OT%OlnuAbx8BlmcEKO?!`&*)tCCz9)Zi{yHL(#89M-oNQw_G6OkeOlmm?mW}`Or6VkmR#>Yb?(iVX1Aa8{@KgbJ~>dIe#;zJvOm{(<jIyuT)o=Q>s;zXIqtfp-y?J`>t`gxy$|}mMsofB60COnRloO1uHWzMI=7#spJm;XT>4XT{}}f=q#puD-0SpmuGh<h?sa(c%UQRJ<Gz*X`{VRG!4&5fSXPpiW|eI+zLIc4%d$Ks{z{@e_rLl|VoF~A|NE6hR`eXc9c|Ci9QVVga6di=K8er4XTxvdvvD8%4(`L}!twZAd|tG@0CV7YJO>{MAIC@H$?!2e8Sf8!;r;P}urEFk9|fPlN8wXoHa-Pk2<PJq@vX2F--_>{Ildom!S~~Ja1&mK*Tao?J>Cdk#vAd&@Voe7{2*M5AH?@X+pBOjT#K*97r^K71^8t6EIt_@0SDnD@Fds=Pr~~_3-5;yfW7en_;8ql5636LEPN7P2%p0X@t0_huYrDi4ZaS}!PnvI;cR?8z5)914R`>~#RK?eI1k^9mss6%qlD&oS+s3~i{T6SVtg9R!KdLFa3r3Ar@>@A4Id2q<Ad>Ga3DSm9}7p}WAOqw1uwvtz=ik{yc}-D%kgTs2d~E8qB(vH?#GYeCt)3a5^sj}cr$(;Hsa^;i|{ah5pRJ9@fQ3P+=rjSPgvb^?*z^9ccbl1xEsET@5Wcb)%YsB2rj^j@O(HK&&O>z0=My@FbN-ur^0@CDn0}bz=z=Ja5$ch=fO#M9=-?`;*0Q=@FjdDUP*Jj2Cl(t@V#&yz860L*W(B9Al!fl@dg;c8}K7=Gkyd=1WWKk_-n8Xe+{p-y61K+&GD*etAMY-ZTKsAF<gun<1^tjd?r2>X5drtOqhme;$z@od<;Gg4#UUcxo|9=i_d}u_$+)GT!Jsdx5ILLJH886<Gb*q@Gbl({ym!G@55vG`}ha&B>n;ZA#BD!#IL~f_!aykcoF{yZ-p&*D}EK8!mr|&;R*aQehI#dU&2FH_u3JnIesSE-iEKkH}Ti;op3k46JG&W;VbYLVG;f!J_F|CGw_Mf#wX&>z@hjv_-L4lkH(*dL-42Z2{0X>fKP{c_;h?JT!b&hm&29#a(oA@#CPCLG{@h7HTWC&J8&=l4t^XSz>nka!65z~eik<1XYmX02z~)S2M^)r@YB&&T-2*~TA%;)C)Msx(Ag}<{ee~gX8dc9`J1Ps$MRl+ii`Tj_H@0Y|C|A}%z2}*{tayNs38'

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
