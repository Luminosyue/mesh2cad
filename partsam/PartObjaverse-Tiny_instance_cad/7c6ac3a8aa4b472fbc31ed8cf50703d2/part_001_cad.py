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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7c6ac3a8aa4b472fbc31ed8cf50703d2/part_001.stl', 'relative_path': '7c6ac3a8aa4b472fbc31ed8cf50703d2/part_001.stl', 'source_sha256': '30ff5b3c407d81fd9f110c45d953f8f17bb03e4760af725b347104beee5c167c', 'input_faces': 160, 'input_vertices': 129, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.3026430010795593, 0.23044368624687195, -0.27307504415512085], [0.3089861273765564, 0.3156347870826721, 0.22198279201984406]]}
GEOMETRY_BASE85 = 'c$}q}4Nz5O8pjVHCJ2g%f@pat>;eLUAPHgj_<^W|q9TY0T*M1rKt2_}^=M<bQnn4oG`sC^vnZt<1o0}$h8OVy3L=UbP3c@Kr&iO=KDLj|cJF<kzx2L4?M&0&nKS<%Kc4%%?>U_Jz4wrm;55ujqL-hP`TWa~uewQ+{cw}KqzZl621Aa%JhZ4}i-Y9By#4hss~4|GOiFW*Dx__iwfgd$GEI!EiOrp<36?dv#bq1HvWv2c%hu}cetvdgx!&f>*JYRJZ9fNuPmd0kBLaiv9rEvdx!R^+Rx<~*_PH1=efCtwCtWyW_hDJgn?rV8w5MEUxXgR$`f=t}uebVnZ&jjLAKlWc7kRJC7<GyL{u5I-@8x@onAbIUbn#wkDPrE7|5&Fm?%Y?Xez&(p@DpxP|IfZWEBN<3`dPn&%i4wW>W^XGcqFuq_v(mL=FMXQTZKM_In1la22Kg{>^?x=|4EZj|Dcxoe4N}Y)cc<%@4d58@L4y>fB42>!N>nh{c8&k3D<2f<}%BFx9%0j^+;u28hCG+miK?#&Ad^qsph@)>%TB>zIn2i_vX_lsQ+!bj`xaRAN5ZdThDuW(<jU;o`)NRK84>={jEJsyjMNluCUbpwON?w%E`>j<18kjJ~4uMWAVL{LjPMy)MtrjEAMqTiplTHZ)1ILV*X#;VfU^1M&G3~oHs|h(tZ2f4}H8>OG}wIt}p84z4Y#%n3r>ldW1fWGF=BvXpP+)pEFSX@~_!^l$uE$TFxtJF7&>A^Um>JI^c`@G0?)s`7~dckMzMm*!mjsr-#vc*`CMNuX3<}{Pt!#-_cty^WI!_oBT{uKkpTN9Q7YL?vha7kjVN=w|lyIZ<JnSUQV9U#d~YeG4hS!okAbeAkDKg$RhMf8PD!>U7<sVFrOte`su#Vwew#0j*ixENqn2&t9MYnkG7Tf(%buK9ku-ZlrW#MEmVIb$|PL31?Q>$tu@WUeEL6S-s<~@MxnmIoz~ZlhQmUCr>V?a<+4LUpE?8c>JN2$g+8+?X}ttTC2RRU3!7=3R-LWpz4UQE)!)BYEBLhA)c>p5b%HN(q;;`8vR?2NKFph6>uV6kofty*?VVSfcyBD7L+f<7rJ46iUJCkHO+tV70_yXfON-Foc|ZBIh*sXK4M)iDt7;SaJb#XPU3|S+@QK%%x3=GHXYZd^Nd43O+5K$oyu<G2hhBATpmiNt*~@#SVUX5!NM#T2%@-Hbbq<PV>)QIlej0bqpQ&G5Uze8i=Fg6j_xPxr_tv`>@_rA_^Im!LBf73vH9hR-yH!;8Qzhk@fll5_t=~}nJwq=WFY!ehx2ppE|H<|Z>jUy?i<Z{MNx4JtZ7awxj6cVF;~RN2uk%w`A0_i8s;l{yuIFnH*#7g-E4wP$x;82s+5V%B`XkLJu$#VDO!L3Qd#Njo)vMnh?B%`cxr+9g`v-e?Z@qtk>JtaMg+5oD>GM4`tV{5DKD2(nitZHVvpSg8@A(-PVceA|RA21Y!F$D_g7$~>f_B~;-48J@f1BDS%(Lzc%_n17tI+>cFV+A2(<!0<wI6BRka&~eTiw|GrpqsB7S3yK0DZn>yxb_%-$){#d*QG!pKHbRIj-4vNa*u=HSJeX`WoT-1RSM4uAlD}>f3vT?-fJm74jqX-}8Dk@68r(+Gp+z*79Dy8&3N}X>6TP@3e^gmC$<LORhR$UmEhdjkMkk)lGswLHmh0?rgKrKfRXxhu2NQ{F{yo`_j<$tRE2er6KS14V~A518u^%Rio*8zx|F`7<Xv^jkD)VwlB#U=g4pVg8Y=@-MqJkI$hP$>9PGmai{&ldgXnp-&Wtnd-WAxs_*{S1?Jx+uUzk-^?Kr1r{GsduzKt6SlTz%cas0UiT*wxyl>Ga2~RbjI~+MGjj*BZaIrnr<Yse^H0&3WG?c&oNMnfnZI3ijVgK(VO}uRm^KHjtIPCl=G7kJGcoK3RcoKLbaxQox*cUkm><gZNoDH4;_CYFOAFwx43-$(&M?M1{4<3h{1s(_XLdJr<z+;h5gU5nBkuhLT@Ds>q!B2q4Afv%!z#hn%U=Q$U<Wu0$;8DmZ@F=i5at7EP?1qd4yMad{BfulUuE^<NSFj5*9P9!ffeZtW06&7927UxQ92p884t7R{fStj^kip<#U<nx@{qnN&<H!W?<6uAJBCsFW38?`)fo0@WuneATI|6NogY5`HI)a113z3t-lkwh#IP9E;!_KKl4LB9N3b_cp3Y?Bi0H=djA_KrH!K;zM;ML#^WC%C|oQVttXM(ek)4*9^9Wo5817{<{!P($7$m!rU;2dNGI0w8I83|qs)+1+t_267&6gU^0hkOd02VRGq30?;_Afv$sa6a-`a6Y&I83Qf=7b2eq7lPL#W5MgeMaWs;B5*PC8E`SU1gQm=fJ>1IxD;H5oDD7mmm}wZ%fTCvbHN+H8<F$C8^IOGIB*4c6LLOy6L>Q+9=sX61-Ssc1)PlZ2PcD9Ag6#=fK!l9g6+8+oB~#H*m);%DR?J%J2DZx9lRB}7`zp{4Y>ro4ZH)H1l|GOg<STK6C519oc`CpM1Ogy_Dx9m2kC#mQ~cV&zw?@{(a@KWqy%UCer(&k9NEn>#{TIj{RgKpnH&'

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
