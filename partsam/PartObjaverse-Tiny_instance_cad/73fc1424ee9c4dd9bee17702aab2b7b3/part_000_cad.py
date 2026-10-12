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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/73fc1424ee9c4dd9bee17702aab2b7b3/part_000.stl', 'relative_path': '73fc1424ee9c4dd9bee17702aab2b7b3/part_000.stl', 'source_sha256': '9f0f5fd58ceff20240b7d0438de2016cbba73832d6bea6026d3546af2506211f', 'input_faces': 226, 'input_vertices': 131, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4972233176231384, -0.22165678441524506, -0.03051178902387619], [0.38414937257766724, 0.07379573583602905, 0.2553296387195587]]}
GEOMETRY_BASE85 = 'c$}q~3s98T6~{jwA}AtJP;n8LBmyF$h@gnb8WcrDk)ntXSmdGjK*D<g^%LU*Vq$z7r!#&rMvFy_*3zJ;t4Y+v_&`Oik9KX9X6$GZV-xF(e)pXJ!nc`rrqeQW=KtIO+&%Z)bMN<9O^kPN^pN<^SDKmQvh=L0B#Cg9JfxEBf}-5a?84x@e3PBzPQLiF>c&Y^6B1MHq!OvZKP$U1v%r6Z-hX7yaQ`5^f6n59qJoUP^u+~P*}{*_SXh{?`i1i{^0U>?0U@CwLHf}CLHZ^7|M9PrT7r4`<v*WLRY`jEwNU+ry1mgFUoxhTi`M$~D{RJ_8>WAv^{wOE{CB33Z%%o7PN-q0p;qfl<9k#^YkW&p=q+u2=}N~-THl)A>YG>A-_+)p_8z{d^{x5a{EpQ(ZPuHVa!KpAtrxyjYq>%GP5<>YE;soI)f2VO#+U52|3RoRs^*4vUb$>y1Fi4q)9b>Qz3zM}J}V9#8fhMheQO?LZNMq=6ZhDRH*cT7d47D?#y5<fZl-!F*tgEB=zJ)TB|U}xarX{U{u^tKlAj%CGq1et9FNa@aZNj3e=`3BtuOV?HSN5{p3iAsV}7NLZz<nOeNeJz+vJhI^*+MucE6^b*D(9%-;tkdZ#!?3<8ks6E;QSmlY%L~C%tyQ*`^QvcRr(fOowcI<7!{3Q_jt3w%JFQD9+=SVKZL8d(AP@wHL42?Bg~)<xvKFeN~%B8TgFzo6Br`^WzBWoB8CW%i8lMSB%<mLgQP{Tbm#A@n!9KmiOju)%tDqz?WnFZ1dN|ZrA#4`Qa<o&fnNvk98%dqcwh8pRN9T`_9?q-<^L(>$l~HZ(QeQGv4s2?zGmoj<@>ySCgCQd?h}ZM&oPuQ2&+vCG3}NDWq{9d-1-Q8rkpFy-<udepXNCO1|?Y`%f$8(tQ2H_`IFC$-cQJit2a0P5UBmzRmv9@zwOX`qy+_C|=*OKW2Lw)%i~k8gDHAnSH|#mDE3{0y^iGzdmPQ@s6eO$${)=dR!*o=fX<Td*%kdj)K|$=>wYA82ym$1D1kN_BTyiL4Mj%%3~N5aao&RIyCkq)wv)E{^4>OcjqdfPt!v7_kKe8l^Y+@bz~WQfPL@t%gA5Yz}M+F2iZ5&8>pXhKlVKv$T#~==X2pue~{|>(<vTbc1xyxK3>M_J${z`-OqN?XSYFgJu1Js&Hm#{t7!jz98C4dU0TRj%Dd3Hu<SZbeK0(G%;Te)D326)y`IMFeqw({I{Esf&eTt1@8|3r_aspL7oJid%*S4_fA($>joZJH?~@NZUm^d82F`y!gYE;$OAq!_Z+*n)!H@6r&A#j>yU=-%=SOmX+>_bg)%*_4mo$UdHDWgV-?vuK_sd$T57MwSoBaB~6q;B5M;`k*aeUpCj-fut`9<vOuP>(lN0d+>l;bA$n{-@f>r3i`{82Ugj-Rih@j<mTULUcO{Y^U*8u#+*VN#!c>|gR-LZ2^I(0a`+$Jl>z;ccqFvCho<a-4nlV^e6~H|c0zbB9yxCz@u^KGx~zd>Y<A!~TGsJnytloPW(%?7z$>UrOmqbz0`#X5TO_lg5Shrhb}3EbPb4qVZ;BJ@wO)+`_(36P-g#<~FLwvaOYU|J6Ha{aFFDUvjB*mHeUW^XdAn`JVINcVU11Nxq*No#}aGKIO-L<!Czp^4LatE?IOj>?`hcy(oe6>AqpCS-^f{HQgVK@AC8A7+%P}DV3ftau`3qEE`MNfB2w|^!=?guYSUE_AM*+QyukHv|olJyV#G-{Vi#)Ei_&ZuVw#>Rs8&I^rL<n4t&nO^LzAOWpv8r@tIf1m)E@D=jM|0T-TyM^7zO6+0gQW&zqZt$KTsP>o>>R@q5HJ_N9A#Uody6B-MZS2z{&CNPVlB!25gmDf?qx_&u^~D6LER@D=;J|9*hx*>Hiz8&^9t^L5>a&a?Tk54}$+>zv4!|1yp0l)N8t{T9z=ZJqMN^`y$iAkGunLj9B~TKK)dE13QLPE?Py;Q{wK4Zhd6)Mv}uqkMn(Dun%4_xDl#O$Y0F9WgwwZxG)nt4!Q~w=q1v+ZWug$s_qa$7vS(126J=d#<Iv8A9feZ;4LlJWtB`J~1SZ$Jg}c_oB#X&J(eb=QZK|Fq6-xJbg2d@9N0sp*f7_-=gsN1>1SPx`lkseNT~Zc%tKT-ujTAgV(lQr#xqRkZ<fikk7^6Hs7E+y4~gXhgR34(TO&{g1+<&^X%1GJ)vs2sK0`8GBiJdgh|I2`tN@N<qrL?egX{{68``G1R5=lgc=#p<=_l(8MF#4R0azj3(kOw&qg)!)OcHsWoj%DmjiSuxDsrFmV-^;LTC|KXaTqoybvLH5kl~MHD;-is74xeDmYb*5;aOuTPf-)g}($*g1VN1i}C$p<SvFk3z`ZRngC9~+=3^mF#~l>1*bt5gVVspn70@`D288-Sd4xYfpeiVz`5XL=p?YviQvI%gsTw(9RUsjhe5}I!@x1ndEgju7WN_w`;!IVx?l4&`zv?>bR2jAI379z91k7^4F`_`N2xIqIusfX4#zqL|4I#m8dIRr;3?pV(8=J5;AH4ra56X-{TEsQoeM4i&qoN(hE4`&gC{_v!4trdPy;v;JY0=o(6^ulumS57JV%X8HB#V-b<T#SfKxC=@DMdZk$V_;I5Yx092^Oa)zlV?+J)w5){=v@&WA37=1A?=tYGW4EI11q3(f+^KqI8~vnMzV8Y;D)Rly<9Az-0{!I|h$I&>yD9XuT&cp6yfcxW7WJa{BRa1?Y5I0`%pnk2QKVZrgxe5w7+3l`Ue30euwm)h^2f|nr#mqL@krQlTP7;q{$0U8I6!`c!Mf)k-L!HM9h&^c23Jx%Z=XbN}|cp`KP_)RtJ)##^&KePivumjW{JOJZdpdG;7)o_!<W0%z%EdFgTNR7@I*BLnmfCoZ@z``Gd+(P?<{lWbZ{Zady-~i|#Z~!<Mxr32E82&)$08I@YQEw-(6Vwju1eVYb2|bbEJ0R>dJ+#BR?U2g_YVC)g8i8s!A_P0524~dn3_l1Fh;;;m1E7AIwfkxM<A-|vFo!+DQELBl#QGdDpOdBz!D3IlNW8D!;NA$qy`Zmw#ooUz@ww;@_CyHo3H1T@RpSkO&lmhU;th=R0qdcC!Fq5X%-sid^?`4#voC7zi#Y^~*To)ccp(Jq5Is;^PjEMc;I2>)a98ka2oKcafxNvCUZ|@NSP#`{)}q5&b(q@+J#@!D2z3R!fx94FH8r@RE?0cVTBkeK(G%(kbqBj+KEa9ccJ>|)|LMOL+W%y_Ftq>C@XK%7zK(0Z>7*9k_Hv#W-$9%=^?=&bi)*Urn)ELQ7rFl'

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
