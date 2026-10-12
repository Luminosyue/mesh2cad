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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1d97ec6885464f6a9ce7a4cc955bff41/part_003.stl', 'relative_path': '1d97ec6885464f6a9ce7a4cc955bff41/part_003.stl', 'source_sha256': '9c228d2055f5a27d852f2e53087f8a2627130cbb36f6d7fd4c439a74073768fe', 'input_faces': 134, 'input_vertices': 89, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-1.2021538019180298, 3.540040969848633, -0.34514111280441284], [-0.4946216344833374, 4.035427570343018, 0.3451409935951233]]}
GEOMETRY_BASE85 = 'c$}qJ3vg9e6}|bDd`Tkt5SoM=B)mX=r1{fFa``k3rlF6RG?mur3n6GrNFX2>vE>Oxpo$vP>6G8}(m^Ozq7gzn;|Q+`mIhNuX{uF``=AjhU}!<5m1#X^?S-X|&NzBAXU@87?YGZ9XPtZQop@?OLK6(RGK}KqmZbbP+%R;DHWG}LEgdT!ZEjhf*S54X$cO{4uUmch+=g1u7lMqH#%kBXmgUVIu4$&ry{OEUW4ac#cdY1WYI~%;V_}QttD0Juw<v!3mz$QhsQaw4@*J~pa*p}9`M+L~ssuaCeeJO7%_(0QZK>XCyi;1K`=8~2caq0|_n!`I*SvqH3%vEwTf%2#ZpZzC58v0l(Px0SZ>)F;{HAN*?cy`wo%3}s>pWK6Rq#%BNv!5g>*kC4-nZcjc<=S+V>IvUy4ZvJkv|Dv)QLR4w#|oh9wT=cyg#u?__={YsH5VK694c_<o8Fe=|%jK9;xTxD^kzbkNyI6bngLgmD-5+4s`C)@xC8FBYEb354>?`>jBicx>4p^YJ&F}yN-fC=MjF@UnS2^2iIdgql;y}?#-B&b2Ru@7;jy^<Udjf-iY4$3g#1*CH%@F8MnRdRphxbLF%tLF6+GC><8bJCgbK_MjrF<+pi&iL7edWo|Qab%{qd0NWS<U@>k479`k6-0P2tX19)fEUu50doBi->)fVu^s9wYyFFbVu`7eJPym{}$ILtS{4gPwo!-RkAWHi=i$9UA^)PH;x{pd-k)0%!9<N8CdgE#AgWIZQr9>lm`x&q$c-74!@={*Tw2F?lJw@&hW^Ylrq%kDw&-p2=JzE#f-ApVj4S7m<ZW&P6^zk&I5>;!N3C!v1xiN4nm?{1g;KdO~|zWvElh>sgPg8sR+n3q%YHCeaLkw2sU&?MQ<Gxxr!^EfHO`)3cyI<#gD;{N?3;C-=c5pPFqJB4+t>H+UuERZ_C<&tr?tP_6vdBi)@;@?32yhiZes%Iqr^1e3_AD%1uH)e=0n-Z~Z){RS7Fn-`;*>Bf-hY;r-yoBEc)k&Qn%z7R3*}q%(hEW*T>Q8zL>yx?>y!q<$i1%l9VP01ML*VTb9TLAgX$a@W61T)3{|NC`cNgYmekT^ZHSinRZ{P32I`|8&zKc4KHOqchd64(aFTvXvQZO$^jf?o|AAtAGI)Qk<suOubycdw?pqy9UYrUw)cP$;fwV@mJ7;1fx_t)3YW4?8k_;_U>e6$uE1Mi<dBJu8c>>sOd2Y9<@m+VjF7xIU1kUX2}Wt}6piH~O=2Jh@OP`{z}gN`@X3h#Z|FXx`xKZswqWEkUK+9>Cn+J`#cPL3Fs`RzqLwyzJ*m)|}74%T(!i0s?6#n>m_o)^FycZSJ6QO^b9y-$MopRJR9wf^);IaiknANrWYtLF~)?=^$>&K?q8J*To>wczbdKauCxeH_o76_aufzI0_u{d=A|0seR0XAy4(P``I+vmf~fI>B4>Wxn>2800awWP|rznlApTa}4t=kC!})-<9}7Z{zuOBJTk2+!rOjA29n7H}dxYem6nhFSa^Y5qCBK-hOC~_^8fj)LHaH@V*R3>O45O9&w>Ngl{@1`%|6&@O^tac&nmH>iqfE1K>~Hbig;2$hfa}?!tUCM!-9P1gT%Wk1+0<?}9hoPs{lhwWb&GJHG+mzgFJYPHh11K|A#c$<zEr@K)<)ya#>1Uku)EwIxsG%@?sg7ZysM1%Hz|hwEO(c%_Ztz2}A`|A#AH!v0+L!5QdV<=n8dGx0s(3+w@JwaNR}YX?dXdp`A5G-vg;dyd^<7`jEMucAdww|x?6QeU_FfB#AJXwiT5NmNi+^nZR6MP{oSCa5-1wQTme<Wf`{M?8+2=HgU~C61-0IX$Hi;t*<@3*ypn%Fr}7O0`hpP->d{jB4@3@zgYTr)sIhsnj(0S=BO$GpT7VN3}fSJZhRNQmurzgqr5us#OqIP}AIO)vAcAsA;ZNH4m|en&#%JR!>|{O>_6Dc0cj`)O3H3YWEWBejd5$s#OwKQqx?qYNf=b)Qag_K5;&^T>3VNcoMaV^ev4zjoLW+Himc%wOINVP8?1xguVq62U9cXTLf_gwNUz&K%77=p1!3Mr&CL%Z!TgNwM_apm3S((Jo;8fTt=;gzFEW;wF>%HO<YZ_ioVqm*HQD(w?^VdYPY<cM?8<(Jo@%IV%;~8)4t6ho<XgWzLgV~Q!Ax!1;ho^^66U^aTc{n^ld!xcxq|%Es;2p+8Fv4NgPQnoW6w-hfxcrZ&Aci)FS9x5^)l>1o~zYo7B?j+hpR&)LiuKF5<hWO{H(sh^J92qi?f_XHm20TMcmywQBnI0PzFV>gd~p#1B%t<z)kL1GNVFHiuaEpC_k%n@K#A+6?-3H}T!n%IRAnaUrz=`Zk4l3bicymO-3BZ9IKTCQhc7NZ(?JW2i;aw`k&MYGL$kH1TL^QS@yr@mOk}nxNo>kpJ|rfln?UUIw@Squ^hE`RUi^?Y~S?xBq;ZdTPS(J_%NT%T%AD-#W%W02u&1eE'

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
