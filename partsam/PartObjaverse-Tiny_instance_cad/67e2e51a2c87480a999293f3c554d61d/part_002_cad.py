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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/67e2e51a2c87480a999293f3c554d61d/part_002.stl', 'relative_path': '67e2e51a2c87480a999293f3c554d61d/part_002.stl', 'source_sha256': '222dddb658f3a5db6553b99b0feccba16e4730a12face0f22a8077b895cefe37', 'input_faces': 104, 'input_vertices': 85, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.19402822852134705, -0.005280196666717529, -0.12585943937301636], [0.21169604361057281, 0.02202814817428589, 0.3737880289554596]]}
GEOMETRY_BASE85 = 'c$}q|3s6->7{?a@1@S=&ihy!76i8GQ6!U>cP(o0+z9#Z9f_ep%l&4y#ou-D-5s@^}%<QHpq&eXm1?3o+WXvd*l|#Z!DHY4GkZ82*?)Ux4OH(sV-I<;L@BU`*?ss<g91eykTRRuQpZ>yh@WHOt4noM*MYxES#<Yy2MaJ}@%Tr#m5zgf0r!BWe&z@#@!A7hUSw4%6>5I~Q#wb4HmW=lCSA3SNNXtlzU%p^P+G3;h;ql4oMvG5Rj88FIzWa_I>8}L(`73Lc|N7}{DM4?%T2(G<DK=%w)Rp}66D+Bf_Ps#f(2=~lanh&KD>rg0$yfEukQrC{+GXj*fpO=^tHJ3q%>l;Gq}S(!oF(7nm`nYft{;`D_6ueoJDJAOGU~}|k&f*10=R!xZ8`aZ$7jd~w9@#Z;W~RCZ}!Ub+&^qz1?62&_N@n~zrJced3|VkDfyz7P1LWl#YFY|bdr7RGO9=Hct~E4oX5UoEsd{L&AUMTyUk|*)qEOX{cS#ZQQ*g3k4clMi1e${$7OFSA%FWKjib7cqxBS#+3Xz}slOgQp1tS7l6LFn5VM+ow=%ZGdfkL6le~VX;uw8*bK6Y)g557sy@$%!mvB95vIqNu0Y|z1Fdo0zVKdGDyBqr*HN4J64|2)pO*z7TVk+(XfyOWBch^b|lTXyP(fQaDUnA2zIH8!=b2`;ya=1h1M9H4dKK3||vzNV|JMVz?I*TPv@6x=k(d?^uoyA8s<jwZUg?#<RG;iFsbyw)RYJB&TPdUQ#hTr6RV%^y%HmA_<&Fs}O!yaB|J|~)=r%vDRzyFr?eu=vE1@!%K4*SFkT2BpLufDg9yjHz}#=m>(OS-Pk_jAavZ=^a+=7DryXge=$B%k4!NA(wJRKHrXjeSZW)oBWSmAoF)x}EBX4Ws_%uH0XLV6%gKqIW)x6VBu76J6OCZ(m++HNHNx<sI^7*B5Dg@9(KjbH4XJ@)5i*$`3BI4yLHHh2)!(c;1HZXx)^`YWB{HXdLC0TjWiF_ln4iD5|He{<ws?56CNpbX{W0vE8(8rK1j$Z^-8HGw<>9q;))dEi0MoaQ>0cNu9?Lt|x)7w{i{5D?%LT`5{cdE~WK9+(hS7J+bpRdH<a>zFO={=U<;&z~1?rWmHFlAN!!H6Xew_u76H<uIJF4Q<Qoas$Z`^PxrYVpThq0y*&P-sdWEpyH~L{Z>90o;n93w=e^0^#QP#{zwt87+jQkL`P;A4yn2*fHI4Jj{ZgKHRTAx^(;9l7i0X(k>v=Vo6n_4s%_y^;S4>G|ubbI7^FE57!``EL9^GOucpt@u2=e0UjWd)vxm1sK=r)a`MZ2GEH*du$dakM)`?J4{d0S7jKe&;-9iIoWZWf(Ct+!)&yK&NNbv~cY>;><OT4=}KF@}9k9{105I7a@%SoSG=PPDqt<i*PB@^<ytHuK+wuNUjq>)bZ4Qk27fS1SAXVf=ThcK<m(CwYmq{%R`UUmNP#E5*ES59^Q9ec<u9lJ~hNfzDyz7CJw19!o#weGljLX<2ZP&b2Y0_s1}o`s?mSIwz*L2Y<r*R!RFVD&sfM{57-L2Xv$U>bEEP@3p@0BA;6xN4x37*H!Dr=gu5T^^2O^q6vm}Z!J6Pz3k)cEkj$Hqvfq-Nxao7i<I)ymVf`sk`(l>URj0*1pUu<7Wv8|I$4?xvMbmI+yPCpEz$*S3+{#{xi``aEOQXJH~48Z$<Lrk4nz(C2ZG0;NuG)v37!g$Mw4tnhJX#=8EBGcBE!Km!LyJN;9215Xp&=)W56-sX=svzk;A|;6>u<kFdY{mJS=Shnq*I;E7%j<3;7hd7q|zqGq?xX2~Dy+(hh77?u6_JmgxZQ1a?G|+!fgcEVDbfE7%!LvJ0{&SY{uv3)me^vKO)+Smr>m7kCiT2RsPuhx7;gfrlUiz(c^pkwM_$;E~AD;E~{G(Ikf;$Ae{tf<wSzXp+N`lfmKO2;_6($(d3uZ2~d^9DzO)&?HYnlN^Pd42}XvqDh{D3<Zax?kQ-JCn86KCxXW!gTQ0KqmTjMQQ#3sfA9$KP^1rdDA*S{5bO)~M)m`HgZm=;fct{okUhbMD4Py0w*T}m<&%#lA9(Hl!Tjql+dtN=e|f?()}Ie~LzKO|hb#}x4kFc()8&&<`~hec^P~'

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
