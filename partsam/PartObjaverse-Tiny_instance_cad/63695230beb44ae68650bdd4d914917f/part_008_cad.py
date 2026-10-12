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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/63695230beb44ae68650bdd4d914917f/part_008.stl', 'relative_path': '63695230beb44ae68650bdd4d914917f/part_008.stl', 'source_sha256': '94f5f756964499a9e325e1b26fd80b0baa25b637d9fe4bf2fcfc1f9da8f884bb', 'input_faces': 158, 'input_vertices': 107, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.03278278559446335, 0.3703908324241638, -0.06953081488609314], [0.06227089464664459, 0.4248684048652649, 0.05070990324020386]]}
GEOMETRY_BASE85 = 'c$}q}3s4pJ6~-6D7>OwARSTkkq6i{_4}2kPR4@h~fQnK@xxiJ45fLQDM3Yq$C64G-P@@DD5(p|SMMH6F9JYx%jmc<qYH74d)L_+`X!EeXYTEsu@1tBh?M$b+GiScve)rt-KmW%rJ0vEw@vv$51Zsaie*aRTr>3dspxLw+9C^#LGadQiIk_v{G;i_Mr$vjW&YY5%>ZZM*y&Rn7$j{6R9vu)Iy<lW;SU~WCrFqNq>^bw7=4CmQA8&s?-(mUri|n}$>v}+B#E7tfp&?-bs{{VekLtp__Pc$tmg>8bKU1pB2+UAwJpDwuQgi1z@r|p$cgl5}iQ*fd*CT&?{$9E6>0Ke$YklB{>|N8S>P8F^-`v>mqWI^U_ccoWz2fU<i;&;;M4?<)eFOigNXa)Q<i8>LX}#W-ykVy=h?Wn1)73YM{gMBmX@`t^ah&+(s&I_^UF{<Ar_K^zKXmzzqRC$sE8pB;hhLqI`nykVminPf;TIf|KGXM{c_-Gz*XjdNziGu5sq?S^{nS-pUbfRtd|!lqyk3F-sj(R2l^}oAZj5_<?^YT2>sr*m{{#GHzwOfh=40@?+A!a12G-}UiTc&mQeR&-`Yq9<A5p(+De7zs-6VC6caeE$4TIq~#l0x~m-xUxbwKI_T(@EW9{Gu{-+Xid`+sPijJr1!{)Q^#H+YrE^?@;1r<bB|ewwdska6oLi*K%dfN@Wc%8_wzr69kg3civ0y7DzM4fzi*!2i%o>X@f;FmBpI_<eKp<oB1HsIzku{Penf>2rD|@_Wz0`u{50kUD*9;J<hS`R^sn6D_L6xZOX3f2}@O@;%REeLCdAe`)LU^7{#2!oT2z@BGUY(GNT-<@<(4_`PEm%Jsk}#W(L1pr0`@%cReh!{EQxAm>v{TeU~l;c$%j+K>jUe`4Kw$vZYpd}GyioX`7fuwOljkpG8`sDG?xx%jU-D_!q9{p%w|^8Jls)H${mzT5scaej6p|KwLqxL-K##&YzzvKIBL{<a_UyMg?*-qL@1{&&Sv_x5en-}IT((XPyp{nEBRLY=Bf7&ppMC3zVhqUNCxoS$>u<v!Jybi?=6>EiFJ$&}}jc5}4&`oXbSw@$@!{*9nG@wMq^FmBWsyX@ng1mrh5CEu9il;@x}ZyM^KA1C!M`FF<sKR5;b+)GCNA7<^4Yb_1F-YkB=;3hl=&t}3u+81^DFTs8I?GE@^uSve?8CUA+>!sDGU+F8)Rr7-~`0r;RzpQMVd_S-pzW){Uf2#@4@hhLgFUsR{c=!sL@8Kr+e9oICLthu&avT2KkFY+^9>jgOxZS%_w`UOgaeuH>@}fJ6uSaf1KYp9vk$l@S@y%t?7<c0**^;+vIsB_l=riafp8w_+)K82=eed*9Qs==g_%+ATPnXqrK6@O5@Ar4)e}A@2&O=N+{N+CI@A|J4zuy<|$Bjonn+M7Lt3}*K|APW?u0HnOEq-7~wd6G>A%Ah9Q~KOeD87Do4C)_=mA`A+j%N7xx+1^w;Va^&_QQSfo1^GI_OG~qBMQYg%HPM|9cP8Cn{jSC{BE<cK3nGF`S!*M@%73Oj2kx)=l{bq;+va7(f_#oQt_jjG47qKsB`D&dhvUC9gzIye@H(@!sjwy!#+TKZQVZ9ugj6=xz=$a@(<sGf5F%$`5PMGzx<xmF{gxAivRFq)T!{mI^1|`my8=f{-9h>^F=@5>#z=IR*J8W#Jo&*uNqh1yz(vbYop&5f5d9k`F=g}ubnLszrI3zWAF;}**kT=tXt)uP-o3q)bXAt=fucbR3rY-Fys&HQ!ajobK>i#%CRqNkI4DdYrhoVDDgm@ka(G|mh=tk{I~#hYCR?2bWZ;T?x#lV`;HkhFS9fYzH=w~kN&OfyM8`Ld_8js>K7Cqkopy-_{JAEv0wR@WnRX`Q>arGk8xKAOFw!-=r85EG#z#B=VBeg_K0sx?}7YZ-;(;qz00*SuFnb7Kk-RjW8!0Pv9Hz{1=rhIZz5K-x87nG*j-*>m8m{0`k!B6vxog}udu^M{?u340IP>yRs>Ol$x8c>mG&hEk$Y47kd<~L_oUjW-N;IxA}jSKD{V)%kvmg8$V#6icP4kCdXberK~~zH+=J>%ZBK5`Ir~xr$N`+EFC$2{722B|NcMA?vmez)wy{?~Y8P@#PkvNi@-!<ZSTWIxXQ`14A1nN==tu3uXlq4BD}F}p%24diQ0zu+OK!{GyD=1NRDZ4Yqqq&#hwQ_i+AtJ*QYVr<$^EGl$P+lv{tU(A7>a*RO(Q=?bx_mDY0Psl6wjefB+nryyR2z4HIkf6PN4de6UZ?x>mEbxM2;bcP&<-C$e}KK6H4t$4kZs{C>}uVP98+<K<!TM&b$s(cXFH+&sZ_pirH4ASTT<}m#j2{tTdfGkDNu#AS+!+UPR5NE+j9Y+Nlf43;BCHbw1fnPNim$GuWTv8Pp`|T(XKp&T%q%CN+ti#Qd4m6tdFk<eB6t)D*IcNmh)vB9_{+U*lc&S8)t=5_uAT-*Pq-Cs0$g)^nvenL3+1n|si5CKb=2W@)YGS+T=qKOEF-t@U0|{2W7ZrprEMQtjkS@+@j9c@}x9%YICyCXuI-<EfL$@noI)3|VO$Stk!;C>~6Gnmk0qxsTFX?}sRA1X<}Qauj(iHG-^kBw6WjveGf+vE<Rz;bf&l$x6e?N=J}KlcTBOWTj!`!~{2YTbuv(udddQp&rJM{p0K3fBE?9h3hX*TDAW5vXPk3R{agM9uDr>GD~l$zdG7K0TSfQz5'

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
