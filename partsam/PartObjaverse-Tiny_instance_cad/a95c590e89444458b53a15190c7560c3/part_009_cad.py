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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/a95c590e89444458b53a15190c7560c3/part_009.stl', 'relative_path': 'a95c590e89444458b53a15190c7560c3/part_009.stl', 'source_sha256': '428a22210cd6470033417798f34b2f6714453436df2c8db42ba81226eedd2ae0', 'input_faces': 120, 'input_vertices': 90, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0929064154624939, 0.1192205548286438, -0.08370286226272583], [0.14712989330291748, 0.36767953634262085, 0.16105489432811737]]}
GEOMETRY_BASE85 = 'c$}q|2~bsK6vr<ht0*L(0xAzA9}*&4?8p-Z1;m~T@~~2nB{US`JtcCPN8z}PHkgr24O*0lEeIrmrt%Om#093@a>{HOb8NJ%F%28*-gExcy$_pd>N;oszwhsP-#z#H&Rx)^S`Bj*`0y60G<Pe0vJ(U;90gZlb$+Q~S#G{QaAirkh2TuSbPVc_xfyBNEDK?^utuGiug@)2N2}Da1(E6imAas~)KHqUa!GM%UcTff<rL}jMPFZ-Q<5)^{i1>bRH2gtRO?j#^>C1CXzOX~5XIPct0!Jm&E0oDlvJ=k*DCo!-yQOWfxP!f&mL=`{AS@KjRV8Blcu;dQvUsE-8BAPTS>a9v4QgKzWziS8@uW{$?r+3r+l3!pLgfHL*y5h*O7mD&M_Km*DjU&Mz=Dq=NUr->8nTHApfb}<23fIs^fgOYRT6GtiM3xsy}jR-t3pQl1AHHq<VH8ZHbrr^|9m&-~Yn%-|O2#^LyUox_fU_bN)B$$^X${qH(+9YWlrUGlRxym+8EwyZvqPa(_o5&%b<EEosvSrKG!O^E~}(J!xK34X<}u2dSZRV~5=DKE?h!;hPnHWdzUTtgn#IV~n}P^*0pND(3HN<aJKJSFe~Sv6k1f|KMK5JpE@*(D-&&vm(E)oc1@n6u%qHSND*w3G(ew_zx0zA44k}6@F#&Dbnjft%~`#6!(*ETcPyZZ+uF+N8h6G-_m?0scK1*vK|k|^EBS)xlf*N^45}XTI16x&(}Ea;{KT#zg>}EeUkl^9S0TpDdoJsx+~Rk-{iCj`@UyCY0IMehwl50#oTwd!+5<KUM%U5`{sQ$=$rRd&F1&%dd>SYC5O&Gq@R7xa$Rv7j*=est5W#p_sgJfe!sX}YT`a|JtOIxAx(V#+~LjK$2#&&c4bFsytS5nr(*8Imm_v}$b6GU3GIt!V)apZ{*e26l)%p|r!P*E+NAS*HM7Vc@_f*3<ox;Ds2+_?5kG&ncC-K8VxFfwnCl<-iv6n<<eQdea6QMa9Uy&0L%u3;B(Ll2z*f>PYdQbhLx*X+Xb1b|&o}r(o^Jy`u>b2SzV8Baxo-#kDOb;NAKa`Z|JweK$iLG?=gq!g(?$P(;sX2LVdNV#i@44!R@6sEYk%@J>-5}r1yk7%-plom4B`6EWwIZ-oA+^1A@{$-3*3+9&-3T^w^M#&51;S4VV%M^e=oonCZy1FKp0)d?-lr(!ZyC&^}jVJ{2G7mhi4sle@j2-`B%m9KHgOG{L8(#-p<!~9YSyMb-ngB`I?F-e$E`9$L9^1#MhzE;(WuC+z&ws>=&=)`A_fVepqT`|KfRGH(>+sbA#>2q#hf2-R_^^yp(MA&EK2716)_D1LYgrAMknWr_z06)XinT&W+D&aHoA6@?QSAp8eXYZbiSrHyKxO|AYtbByDt}dWU=uz!x%Odr3{cI=OGE4B~w`aBCB(`aI`P%j_d<vNgnO6<<qBp1yCVvJr0?G3>>!rGgyUr;=n!$Dls^Q)yY)zxq@P4*9>|N)8EP4Npkhg^)N6Iv<<{o&%i+o&!#X&IKof<Dt{Q@!&{kC^!-v4h;l{gCn3*!4cpn=;Poh@N{SbI04r-9U-v>ng&k8^=P2U;AGUTfkuKOQJ)4H0ggZ&5=$*HT97`OIV84&dVuY~wqjUA-Ju>}ckm2^#4*s(;23Zi)D;{C_7~$(s0-8;>;iU%I)a_SBM=hXK<&UbU@NFC*a~bZyEaRN#1;Y{k`9AfgNK2~Lfye*!HLir;6(63XbgBEcmXsFya23)`h&ILXxVy2BP5=Tka!f-1?+<L8U-Bz_7!8I7)}U@y~T)whCnBRL%@DeU$7r|3PR!ls2Usq4i;kqR0UOoRbU^eFW3h>5+ShzLgL|2C-88vJ=7a)5B8E>rx$b<*b6)!nhG8d9tTYVj{|!`W5J%_G0-6J7_gfdk3c6ugTRx(k0B(U35^BM1gArj!0F&jXeu}poCTc)&I0S8abO)d0~!L(0M8afn`&X{YV}WlivN8W>4uX3VQ&6Q<!ed)%Rq7X*Go#9YE7>uOYz@xqHdOUSNIcjXyWJ'

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
