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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ed24b6e27921449f935509d9f3da043f/part_009.stl', 'relative_path': 'ed24b6e27921449f935509d9f3da043f/part_009.stl', 'source_sha256': '0f0402ffe78935e387870f2d569020e7a9d89ea0ea53c0515b4925fb3555a9e2', 'input_faces': 174, 'input_vertices': 108, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.10053260624408722, -0.34222105145454407, -0.06626608222723007], [0.07917043566703796, 0.07195007801055908, 0.06974638998508453]]}
GEOMETRY_BASE85 = 'c$}qJ3s6<p6+MrS@-ZqA1*G6blusmnqJn_p10qln1PluJ;ZZ;|{s<5|PSeaK+Gy~T6hGJ&^(oa50V6g^la`ie8k3BlN|>5P>)6*!%XB)mF?FQPwBz*beb$xxZeM3Q?VDM%)>)jp@4n}=&l!sHef>g(`o)NY$!F7?K|&D5h)}V;wxMZbb#3F!t@S%>Vm$lwGx%U(X+crBO>7t6im$0{tZs-;)8ZGdUl5<9#joGi(9}@1wQ^fSO)dF3Rht`YrQf)rs=ijX6XwibkfhB`Owzus{f|G&!rt8XUO(kxn{tWRbtG)>Vrp-wQ+`+w`@-csNUVJ}_%5-2DfKe**zGOUUvJ;fzH8;*J|K3VtnDV>`Rm;t{l%)5*NB}vO5Rm%)n7k5;dOrgrMo|7jyiIc{m&Qg=lAAzvTqMKeudkCFTcU>J-k)*H{v6X`>$o}i{buj{Jxs}o%~%DiR|mueb<@qRvseX{z8O`<Cn?rb-khDIFARa_ip%t^K^{A+DiSk>JQ%G_?@@e7m;l(951<pef|FQ0gki#dG7DHyi@f*zw{L6vBkl@{qzpyUyOZ|^RBq}3Xj`oTiAE)NKkS9a^f`i-xaOme|3(1k$SV8<M)TFI6c=nAJ@l!JVU;Fzn}6yDO2P5TFhSlj*|Yj`Mc0x+qdZ?^WgW`cg^wtC3D)B&7AMuLiY9L=^t^txMe!GKT*Ct@&d=P_wIU=-+O4v+ve}mhkwKK<vj7lTkO|Gb3U5Q!S8iU70M5o#r?&@#2@l=p?~-hw@Wr%;O}g&-^b&B^gHb9o7>cTBS)+C@L(JJuF^O)kHN*={oefQV`q4Noi{FU9z&n=cxvuR9UMO=gncp4dz9nep3}+W|9zYCqhsD@Zr$6<-y3nem*10ehu5cm-FBY)FTC38u|6Zd>go65>nrj)`R~o$%I|)T^Kph(@IKN9yL#0=jM>BE`22}eyk3Te&U1g?11g`7>bf|eOP{hY)_lzQi+e3Rp5o{W?CW#0c^(~Qov(BM<O6ElFUN7-uIrzwdAXXV{NE3#@63Ok$HASI-o<`>u-ZQl0@S`U{DemKMek3}F=srb{BMrqc&=4p{2pgt?^(`g_YAeJ#vbB)9Iq;0yFYY;^Z4_zR<rN!ss0r|H!H8r?CT|8s&RYo#SXJ?ui2yaQN+D&vo9w9j_1o2TYTQ^8}p(K4D)zdeb=pp-DcmYV-8DyV}FT%{-Dz%&gn9qFW28c?DEJ*+`P!o4c$`XopQOu+kClhIXk?~yYtM%Q{L8(He1c7bsbuLV;#Dh-Z|-YJvXU3VO{@vVDkxY`^eRr$-bUGa6|3W$Xy(#ZqzYv`}E&@W1rspu-)5!w+}|Qar<19M?KMo?;qj(jQUeCj@O}Hb>)b8UyCQR_`BRo+7GL^o^?zQ*nWufu+&5QX!k+${2KMs9e$;i<6G<PfhOf!>a#v$8T;0H?oQOc%l$0%U%RlB&rj?5qQBDiDnD;IkL*2L`24h<U-qM}ee5r@dz^Q!!ENk|uAh3Ik3si2p7lJnKUmV@v956b>UTEp;rN#G+U}G6GWV-J>~X&9`H?%#`{>bqV0C>nw=MSv`_Bs4x866z`?)Wg`y2NY@r#E|{JiBpqxTiobK83V+1IYvvQEUc$$b7;*Ol|PJ;!+-Ec?_x{BxdXYu$U~Tk5Bt(RY@8OTE?p6vF%4TA#(knLX@V>bxWDrmDNv^WxfRj%z(n^_@?@#lHD|Qsi;F{l~nvrJVtCg-Ha;+wJ-))76$tUVdQjSKE#A{=2Jf%Dn&gYCBoxFhycIFi~PMnA)kP_G3UOyfG4!&<@4l43BsMFcw~v#N%j>#ox%&;70)o@QBkS<^qP7LhAsz<w+EvO~^5Msqj|7D}*jU`x&$gfo1TBOC**9hL?+W2~Y$tTVfG(E_}nwHszlNkDgtLejyU0C42xsiBSOQV1P6&nF@(gi8bId=rz!l0O{4>#n8mb(5s;r0HpoF)1ar}o&Er68`uxp1}(ro&_4Js<44+8VyZ;AL@d}B+82Fd!6DGG&~Xy;z{Yrz*1#dq8nm&_h=af(&>_e#2z`hH!9LJFn1ev{A)W*t1w9Em6dWu@_5x{RZxKg>gQ0^lj?v(0(9zIS0MgUJ$zo)ml1>3g+rf*)$X+0w1CU+<E`ug6h0X!zflHzDpbNnjVr0LNHuehfDsTmK33w$ydL6g|ns^QLI%o&D68ahN3UDR#3g`mxYUl#!RPX|5Vt?pV=!sw(^hD^#z(S1FJ^GCS`$CU_o&XLPBXy5-6nLr_sc)pIj!`Y3nvf1ofKEW4bb$1Ha4a-&9JH}F<^!ZNz;mIAv!OGfi@`<EMVO~z@H*&X=yI?Fx*U3~X`a@CmqV|G&Ijj0=R;?K7eOz=H)nz8LuWx}f-|5qkY6Ua9J(Cu&IIQ}XMw3bN8)LTrzC16Hb`ug_=ZHaM2$oh+N3v0JS(vtn)=rP&%%qBNR)U|;_DK#Bo>0Hy;LGe;%gG)0MavnM0n#RBA}DNG2jSjiZv6lXTqBWj<CFYHbD9ba0K)d&|%>5(8Q6@Mfo<LP~ZRbFT9bT&YQ;k4?XLXp4TJulXqmSN0+6de1EE`vJm@-=OkaG9VPw+k<%G$'

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
