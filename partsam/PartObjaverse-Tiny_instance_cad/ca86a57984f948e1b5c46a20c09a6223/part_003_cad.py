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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ca86a57984f948e1b5c46a20c09a6223/part_003.stl', 'relative_path': 'ca86a57984f948e1b5c46a20c09a6223/part_003.stl', 'source_sha256': '61f4a942aeaa4d9bf704ed55cd093a74678b19ef60343064667a6b4266b8fbeb', 'input_faces': 138, 'input_vertices': 139, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.28819769620895386, -0.13012371957302094, 0.09541011601686478], [0.2624080181121826, 0.10431142896413803, 0.42837825417518616]]}
GEOMETRY_BASE85 = 'c$}q}3se?$8pa1Tyo;?`XkNy=fC}Ey1jQIl#S1EGii*mhfMS3OiZ_h$0$#vds92&+>S}11lBT7}R{~z~h82rZlb7nONszfxCiczqKD%pscF)<f`*G$xzyI^S^ZwuYUuNbbXjt_cjTQN{Rtl>Ie!Z%`qS!}0rLmF_5jQt#T10&3*x3tRl!ox_&)+qD#Mt3M6I_%8WwA$iMEtZkkKU?>U!;$Rm+BEYD{gLFSZwI5xbO(u9~2fHAK~=lXN1j;aJD_Wz2NJmzR<x-U84SvpE}MG9M|St&9(Jp=m}f3zCL;Wc5Uke;2V34lhCyr#9!hr@n%_WF0Q(HzU^yCx3Ac3{Z6a{c_P1rZ?swi-^}(ri1QqM3K9R)YWUWs9f#mQUw*;%9W7Uge`_!D7+bfTMxKVz@U<?#9)MoGjXcH|GbDfe#fOon(;eh7nh%zG7MC7@U(!wDGyEmbl?U&^@0oTH{Z8r*U#T%!>Y2Y?>PhP={-pxM8+X2guf66j{>3rq*Z4UczB2r2_>S@zsdL`za=rcOZ}ycsjjfXZks|dRO8x*k=4Hv#^4?`!SKxKjuhls$*A-j_-?1iB{HjvPquqwD9hi+ewbs6JUE@o|Pc1_|N>CVlt^726W7)cF=;HJ6l}X3pTVqzB9>?d)QNQENG5G3;$1;x_4@mwI+3<Cj`A6YTNRs%p6!=Q{M$Dt*<?b?W=N5@SD<TJe!&ffhy86b+b>(zHzsk;&$Zu`^@e=AOkCZ&GXNzBO`y%Sul8$jO#>HH*ef3C3_@=Q0dCUOUtF~`;t|-Jf{NRo})}V02n^l?cm2uw4V}0}%;`JWyTtNJ(LacK=Ym4Lw8E_u$@>tBHS##|*#D5!c4)w$jLmu@&v(HdZ-bnb4?)8yJtz0hg_Ya*#-4}j%AN`i@MZ7in<1?toEfxDtzqkXw{{4jl^w*>k<7TCg`2zVz73ZVQ@moGdz7<2^>$Q);ckIeVer4rZiNAO*5A6?!B9C6HcQN9vYp0MW`Fq?4tcl&=n?HJgf_7y+*%t$%|AIP$ePy5b*?%0`a~gbY)2Fyj<GGWFSKl}W-?7O+eVS(vtRHo3mBi<!<9ws;wU2Op-hUInaW|P)Z6VgDUb4Fcd3*-qdW`6aAEGX=O!%71Bw0^hpJ1I^N%`=N(br_(Mr7<qo(Gor+kQh^Ns2m#_#wscmGF#A)LAj>9n@1&<2w8kWt&j<=wex)qkfb4pWHX1UF~2NzV}ol{&Ha=+S`)$pst+{Bwm~9kN)$%#`Wp<%EaGRFB8}Co?iy)d3CSU`LO3Md_Six)|;NZP5dj%c4L0BR~?r1Fa-S?Emp%f3L41zOq(h7Sa<g!fBi@~Z*~hAw?2Dv@V!eS#!uZ)L&iB^#rw!pR3z(U>Ot{C(#1a*3}30ZB>tnQ53s&=oZ5@^wA&B!sFb{U9D3_B%)54?jrcdpPC)lH!8+03E`V?BuJ<vtVm;!`-Z#YWIyV>bArbr0Ui>T8v$iAnQ~0@yFz?3HZ{Qm#ZB9YQJ%sP@UV!zi%=Ck=1m4BEQeWB(U(E^<Kda;b>d$%WbNK#Mc#b)4&UhE~KTd}4*zQ*V&2l}2{V==(_Nlq+uJ~V_K)ltmk?gzE4dglIk&Sg{&F>7~n&W;3-!BZtJeWmgMYyg9Rq&0&E{HdZ8X&*+*^RS^Kj<st9hLAQ`kQ_qzWMoC%#R+U;eMr5?|Ke-zUU_X2Byk=>CXe;>*f^XF_%?*gghNaNc^oF@#|aS2aJ^XoKMi7ep|&nX@x=X9qF$7FrJUMBfn!`q~v+ys>Hj!jrmqRR!E-q&5&1hZzp+nq>5jB3jJD3!x8T&{#o+8X(GQCT2v(abo6;>&A=l#Z_3ciXeUmG@9@8W3~m1m%&T^P6@0B-@p|NM(F=7cIlJIn33Jibwy#6H8FJ^m?6ZgsXsbD>*9v$D-%R`ED9-o2fq8YP3Z8FjWghA`?ggN2Mzw|N9*5<6-4d}M)JGlUd0sajzCP!ge81*J@iW$;e#g9TkY9<F_X4dl72}}K?S<!v)izZ6nU^f}Wx651kr^*}0yp8lq@@i-yq1tG?+f};)Nkc3z<K7_RZ@TcO89#AUG%TVn(!^JQ26GT74Xfy`{g}lR*J+|HbB4HWO<KMp4CyOS=0vWP;1gf-V27W#J<q4K9Knd=?CAcyMH6%O5!m7dPjM0GJW2ad0Ns-=5c`dN`46Ps7K>azj7!`e3$PezgMWN+jif{`&ZL^_@;Riby^<s9;62Rn2!EhG?H;Enj!B;Bm2vG))VEqe|sK$Ln(#t@b{ASwtlm`2OamsIO~npAl~}61>S4a!j`y?DODrox~7el_nkIAazA-kQ^srgQuta{9l2j^+9B)ektOl9hGPGkUp<iVD7|?})_Gs}>V;^Grxtuq;*VUC`Ul0qSDRHwy@r2B$>X<9#x1QTe8;3LiT931+q@{g7QA1c*VkW?b^2^w_|~>^_|~3V@Qta@!&mQamHW2qB3W0h+ep9Rn=wAtsQHq&GFkdfNyYP7X<CK*xcb)(;s@rTPRG42vVY8-GTxQR@*bO5F8BRs-jVo4Yvum%Ll0TsF$bjIIcssBSMt}&J{opj{GUQ){QISy_7D2Queg-q_hTwuojo~^+Rk5bkzr5#gtJYQLH+kX;i7u{mp|cr{@<T)&Frn_Jeu&ZxiPg7xiPr`wGP?Vn&bxLdej=^dgQv)r^t25Zq!<2TWgbT{S(=ZT%Y<hxjwle^%=6Q?&NCD!^L@2=V7xeRUs>kb>(4mQ>r_;DY-fIIkK%S$j!;Es4dB@$gQa=+1BUDt;ubvZOCoO?Wyg^wtA4;lRc>&$e!d*)Q)6Zy~v%&-qg-yZ*o^^7qYG0$X&_ZsV|VblY3HokZpaD+>_jk>O<~D?oIV2_a^&M`;h&}8r7d{>&s+~Jb)TN9zY&U9Y!8Z4x|nz2a-oogUF-Elc;0JlgP2u$>dn_eCjmveDWgdRPrM7V&}1tI-5F`Jexd)8cDWQCr=><Qzw#x$rGsI<O$>m9yZUQ&LPhr$57{yZH*?!kY`d~CEGfVJd+&4!{)Kn(PUdg$z#c3JZz4m&LZ0yPmUwc<zaIobqU$l*T{+FB<eh}tt-h%<mJv|DRmijC3zV+nYxCYOkPc0MP5x#p{^jOkPYervO!LuMv)W9)2ZXh)5)(;N0MJ5kDv}Ek01}B4k8aB52W@d4<z@azC`Xv?&~~)hPhO0T>U@&>+_!<12^d>{}KAHXa4bV`{bDg&RqX^_y!Go3itVH&OdvR{(=m@13Nb&p8'

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
