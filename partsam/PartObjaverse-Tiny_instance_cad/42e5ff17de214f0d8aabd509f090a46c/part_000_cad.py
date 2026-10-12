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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/42e5ff17de214f0d8aabd509f090a46c/part_000.stl', 'relative_path': '42e5ff17de214f0d8aabd509f090a46c/part_000.stl', 'source_sha256': 'f90329039c445f2d183459ec1d9622bb8544fd2d3e4bbab43f6639810f1a6fe8', 'input_faces': 192, 'input_vertices': 104, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.13535746932029724, 0.14563845098018646, -0.44408583641052246], [0.12340745329856873, 0.4731988310813904, 0.2635062336921692]]}
GEOMETRY_BASE85 = 'c$}q}drVVT9LH~YGv5=jAYuWvpaldUD1xoL1d3P?@G+ED+Je)l10P!)%QbE+ZqZ;gbNjD8vc*KFbJN8PMyGRXqT+m@2%2X5!_7pqE!mcsMb_WB-&5{Abjh;a<d^T~esg-x@BYrY=iJn04GoKtlq*S^?isjac}bEeMoKZ#c2~>R^^LC9j7?kK&`D#NPZ!q%m9<N4t8~(KX{XWYYHe&W<{FH7?)gTO!RX%HvbDvrsbO=A(?x!XV`Hn!@3%HPwz&NFsadn;m<+SiOoleYf4nFQuXFh~-IUVhwyS2p8s0tofZhA5nQypN&3q{-zdx8SXJ#nv?^QA16We=*wJ-UyKbUX1@_8TKd&_Lh_ewF$_u2FV!F+kJnzgrdRx;mrZpvly?HlU`g8AOVF-rf_Dwr=vj{A<~^LWERFrPo~FyA<MpY=PwT*>FQ?vi?3(dXm(bft>FXVkaq=MsJXT=uOcO8%|Zi|V?GKChd7L$Ts7Id(yvf56Y{xuBje(dYB!+Z@qNDt-3LU6$vw?O&T!zVGzjUN-LB{WnNG2X}R`c`V+0o7Le_ZnxUEgwMFc`akiTroFws=03ZZzUWf>hJ;_4FXv~n_HtI-dDc&(>w7lt*(cp<-<KS6i{0z3J!)Svzxjamn;P1s_B}83{j5IK_pY;g^yHmk<LVpO?>(m%dey$iT5*%j<I|2FP5apF0all`9i3|5d-n$O4S#j8{w=>poMP*z<C9(`pM9)9%cR{WS^EduSe@<dA8UNMz3(2&`@L<<_nnJ7&gyp6!Rl#0+^O|fJY{wBo@!ve{JQBV%kyWGl1EdsSM6Jx-Aa9rb@ixyPrCIX%X4gEr>6bW$IO?Dol1W-`A1ltU$nD%m;bnaQ|%iXuk^9|_)5j!oqm9|uYS(v%U;x{@qIUH*nG*?3Y7c@|9rHF)$!G9tlje+UX8!=7|TP>x!$Apy}egi|CX|cntsIf%zbfQ0{xf2!}9S(nzjDa6G|PPy!c8p?vJI9SU+cKl=`emKVS~_yzqxT@8bL;<{<UtzF1G$WjbmOHox$P%`g06^UK={^XoercibFoy>VYyZ<eUtC(XguGkkG9TYiW*We!q*`=z`y<{<AQ_r>=y&|Y{Sxi7wtQfl0JHomZ*a9`X{xG(M}+!yx~!~46G{Y=;oxi9XA+!yyl?u+}O-5sIiE39Yki~F<u=}u+8OgW@EuSK8l|J?WJFKEtv+1sW(M{~T=56&ae=jV~!FDw1@uGF04qR-DedGPISWxY5x=eX$e^HfgRqtszlt>zpT{XqVrk8@nM?PI?8c!}m57yZDv8}=*t^jB%lanTPvSNlO_UdlQ&=eXzx>h|FW%(w3we^E1Ef*+W#!-te{Kl*9t+_!1IKFeaBt(T+yP5lw=|N3-0RG*$?(#19Sr|0@P|L)UsLH7Us^rUakk^UGhQL+k?H^LuLVA2RMX&9I^1RR3L#}~Dv14lz65yasL;!vm#yq0S2k2TPBU{WWT)D0$W0+YJHq>W%w2bi=0Oj-{nT@5B(2_~%ruZ6yXAYO$aUV$L4K@is>h?hg_z!9h~?<Wd<M_~^5SR*h#=_v48upK%EJO=gRJP!Bkz)olk*a>z+Uk1CuP0;b+Ca?=S7VH8yLPvu~qwbtX;@$ynfJTEG!1d5ba6Nc6G#ng`d0LGcu0UNQz+uoDa2PlQS_=*VOVH)g&_%4nSfLniCAbc%1MAS9xX>SS{85A;E<g}l5X89%;`s>TYy@!zg4l#0o{k`%iXcuw5Klu88xh3m2;xix@mvJ)0tE3w1o2{MA-KdJ`Ti(I5a&U&z<J<V&@}KYa4OUQCY_?<1l&&nPlD>flfV<9vEYf|3D9`(1aKTQ5gZ4e3{3`;CaHKP?vubXpgG_f;CWCpcpi8Wv=mIb1WYw7LtRV2<<O<za&RTI3S0@UhAsnFgKZeA0^=<KTcI|v4ehO%=OR@<MHq*)Ks9aw@*=gU^0eSNNOM)sMVt?v56%Z?L9@YG;529kI1Oxon!pBd0(3e!0j!5k1?$1F&=hbiI379;91l)}8o`O+WN11#89Wo337!egfzAczfX&baU^BQBx)59nu7EBESAcEMLU1AGlF#>SX=ptVFG3LWbxX|GHZfoS#FG)k{5>M(?;0_GABp)pOU&PE;#34N-yewi9zx9b8R9Yo@lphF6@qvf)C#s)bs;gK|Mb`4&?VERuK6QT{H6A@PyNfc{Cx#J0&UiCI+y&1O^EawO&sgtZ~u(xng'

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
