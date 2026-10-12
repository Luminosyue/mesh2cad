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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2ef369ebae66464f9d2479057a6bf6d2/part_001.stl', 'relative_path': '2ef369ebae66464f9d2479057a6bf6d2/part_001.stl', 'source_sha256': '7f463c192c86a5f4b0c7a3dd770acd85528771d995a24c0f17d98b1418622383', 'input_faces': 240, 'input_vertices': 146, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.06071515381336212, -0.4732385575771332, -0.2984483242034912], [0.36519333720207214, -0.3787323534488678, -0.1366530805826187]]}
GEOMETRY_BASE85 = 'c$}q~dr*|u8OA>@-Y-D~!31?t;|f_70TB@769f^;#o(oiz#<o+F(3;?P|*#FA&Hm7cBbjHGj2L<r=502jem4((zt>GqAswgKr^jdn_g#namMI0{?VSZJnzYS(sZWNuJg?E_?yFf-gEhYZz#$O3Jx_UK2b(p{?o$P*@huC(+D+MsvXUBmDNqF>JPL97$JTxKjhyi*q&dsE5K+m4qL0Ln<^dF6pJ;rCdq2ESZf*_&5nxt@&-p$wdC0q`<to-Z>p_0P%ZwyVogG#%@QANv$R|O$Io=pf^+u#3+d7yr2guvaM!Gn;j4_Bw(xO{pN_rA#~W6whjSXQcwDPC-gTng%eksg{K|PhcL)8}Ki+O19p>Da+Bn9!VP;+8<ISN$@0W4=+p9dBQ=Ko4SM_Op-~LOyf8XYZw>hW&i96q2`aYl6Jw5jh=Tu+u)_=aQ)qi};%eksgyeH(cw%-1e8dvKAcenn$$6u#>kAJ*n>8FF7`~DU)&bj&Unl|43VV8$<8c*DK^!py|KJ+aZ;auGZaC7%xdwBn@q<db@sej^5Tk3WHyrsdv_U}V`_aNuyqmD6+FWjh&H;UaJ&S^Yxqr2}qU$1fX)E&-gy~NFw2iJN3#^_JHoKyeAjeVbK{Wu-7J)BcN#NFRZxxx3-{`><k=d_>1&6xZf+I@%!^l+~31GuxMKpSs)lH}!_#uGO$HT${!%`N`^UGX`CoV%8%jdAXbeow1!eE7)2x!NCa_r=TFdR-TOc!zWK{Q=zEeC-B5FZ+peUe4*f6hA(y)%WG3X<R*D;LhxrUOwJg@tKEn8c*DKmeH%-&oymc&ei<{H?w}x%lkK*!$vr#{uTfDu~y%8AI}Ro)hF&gcDPSFubHVDSLX$841C(h>st!PG*0!2n++@adH=o@c&@>zf8xfJZ+W!ydi=ASoU8K!H-CE5qdmVrN*>@`J-^`2Cz*qMy*``c7U#5H;>LFd2DS5gcf$bZ>b$_65dlNIe|PECo1Clfhv4qC4MW;_J$yRAxjHZ6e=hKIi#a%P{{tg6uEvA=!ngamyME=w^Yz{FevNl88|U2F)uz?=r3T;PT&<UQ_%Ut0&a@i?oYQ)VTW)t~_1$aM-{hR?6L;?Y!4N+$bK2G+&gr~}yIy~&?WgZgf6=(=AKbF&?-TXU&7HVE-;N&O+&G^;#<}^+XWDvQJ*$Q}r}Ywd+R}%$^Zmy+hd5W~1@8O)Ms2+1lX)6f&lk8caCBI^Z`UtsT-`Tt_t6e*y!!bL{%=3ulk>d%yzB{&J)BcNibr4Z^84m2|IMJrao>o$-}^wTZ$2&2IMpX^yxQ&M=Vfk-@NiD&Mcnt%>Jja}eK2{Db9LXqEls5(TK`*Xbx!>gZ<}?OkGK5c$u*5*JaN~`^>=wcmMgouIalXPeBqDp^7Yz3$?oBt)~k5#1+BiTJ-C~5b>F}(J(u+U$J?)IocbqzdGS47-)Zje=3M=LLOgQoJzn288lrR5CvNu~y3g0^`#7<Wb6T(BAN}z@@5eWJSwH9Mc?b7ZKGMd!pY87DT-^t7mt+2@*8kYaevMQA;J)*bquTi<X7+Ke&X@S@C0c#^pwX*w)K|Q?TpMp#bNVz+-_Ip4(%v>xQqKL(Jwpr;nkL>hYbw~QriAiC{^hTlbqW8~t7cq6?Em|!*&urOx_qqR&B(7J?-#0vJK)X8(oZ6v7J5hMbx7v7;BO<ph5RP`6!Iz5k=ZG9MyLaR7P$lYxX^3xH{fTH-#|VMoyGiTQR^M(44Yqi7yJzJ8T27@yU;Pr`5N+Z_)+BJ$Q|$_$VX5|=0>4%p-xEV!;s9oAepy9GH-`ueg)o${0eddBy$tgh;wMfd~`0IY=1i0zI9@Ko#=_ydl-Arj@$;{h5S{a7NM8n2a#V!F2>kmj4uXngATI#2eGdQQR^7g!uC~qE4&4{1%1eTK<I=}8T=4(8FDLh2=$I2J0Y37;3tr~kWWD}pM+#~zz-lhkn16tzXr*?4PJ)44Y>#^!+OfltIUgq!i8RhWR8N*M~*_az!xD)Uxu6{B)?U~!NZW_kmH4t;S1qm$P1AdLt&Ud47I|cP&U8xNO&l6DEg2&O=vylOh%4}ry$28$H7yPQ&C6eJwh2mc6cVT9l1iN6uuFjiM$ax4a&s)nW(iM%3$+LH{lt`8R$diN}+w2vlO`kUV~hLY=`ef-itai7YNk~?SR)I??B!uR0ywz*CAIUS3-4|zYewbLA7jt=~eJr<XZG0bDmH><}5_s3I7W6PUIc%T;yETky-u>T`5!o$-D)UneMsFbl+sAdnj`<Jl**G{-m>WOlRktj&n%Id~_})Y=27FzLj8oCFqIPy9IlYhrAj7BC>qWHW?Gon)EDW3vv|3Mqzvu_+}`J)z8AdW}#L-w2AGj^lbPh<W1;9<_$u-g>3K~WE*lel!JP?$OVwhRq)-&RmgiGnfE|4oA3?DCUPnya}p$TB;1A^iM$B1VLdkVDs!MvkTLO*9)LU*9t;ma4o03NG#x$#9)LUrc?LWPc?R-xkj%5-fylFvX9~@RPlE>{PeYyzH;}1snL~u;2t~jbATNP0hc7^0j%*cL3V#8<0Qm*vdGI;N^N^=QbFd$C(8nYw1p7A?J{KN>JQw+Scmy)_Epvj<TA@VvI^-4bSok{RSmZTA(eTyqb;zrcUxKeiehGOgv=;lZ7JXQu1nl1ucnmxNIR<$ZJQ11tmboY|ATTuOKmDoc^N-ViLHQq^zW9~;YXkqvdQnTgL=@#s^52<2@lXD8S0{JZ_!k-|>z)'

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
