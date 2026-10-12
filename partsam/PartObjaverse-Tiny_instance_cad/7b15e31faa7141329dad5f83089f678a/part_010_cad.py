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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7b15e31faa7141329dad5f83089f678a/part_010.stl', 'relative_path': '7b15e31faa7141329dad5f83089f678a/part_010.stl', 'source_sha256': 'ef63f01f48c6805cd1b2610718f6597aaf92390581e69ea7c16e43320fff118a', 'input_faces': 122, 'input_vertices': 109, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18198075890541077, -0.09302279353141785, -0.4331169128417969], [-0.011371072381734848, -0.060115963220596313, -0.1507118046283722]]}
GEOMETRY_BASE85 = 'c$}q}3s4nh7={;6K}8Y81hhPO!wV_l4T*430TsogND8DLE=L6w2?V@EZaU_@G97QDb~H;J8}pLqph<2-+Tb`^N{V!$i)rT6WNB7j+W-6Bwf&o#Y3exNywART`~Kg*XU{o1+LL`61u6UrQ+9nj_f$nQMG@t%1SzG?qB(gv&f?w$h4Z|WR^*G9scTcxM%&Z9lu~6uc&@WJrzkwe79Kk_Iy}M_K6Q4{oT99PDYJ`mox)Gdnpx~L{Nm|Zg-+wR`(u%VB5ZwoMA*u0|M4ZJP`f6dJTCOuXpc~(T}kb6i?7Z4!cE5^FP#(Wx|zg&ukYQ~e$&@~zec_u@BWbb0wXzp$O?}&$M$6e`^pAh_bblPL%Yj43v18N-xqfyU#Zy6>t5y@$9G-0zjGMplux`s^Q3lWzhs}=ns54Q;$HGyEj%=5!`oq;zxG{TcX&GGsJokR&a`|fU!UtE<(PBoA$L!Z`Y(}k8jju~Uqin+zq;}#_8V1j|Gv^%$v^*=G^cG>J^5<;@g8f=1OE<RH}%t?I?5}%$n#uuc&z!RukD%SvF1PMU-7dvr|By*S4#Qn@LJ9p?j_|r_MhXN;Cs}s)p5S*oBLAjAJKJl1%Jf-<qODfxE6Ps`o^A?*42YD=z1!-mAqfIAFZn;w4r$#wp2*_YOtN5e8;TA(mZ;_S@N~oL+oEpaZ5Q*9F+3S_tDYvO`d1}d1)TazJu5O<T>6~=n$G;k6p?+2YPbOB9(ks$s+Ezos#+;W6HSy=r4Tzvp=SJG*1c7x%kFmnr~o!4Qa<YJWtP!Qorlh>6{b7`&CB<@cUKc<aL*AlYRem&cCPfoKfe<cl?mR{a@aub@layw63eZC;J}$Ji5-zAYTjW#_KN6qkiRH#Rv5FK}|S+moMM9g*CixGat@rx7%&?ZKH0zPyW@}l%uYyqMQa-9s2_UdCma~FH!!nci-pvwYTW+gZcBU-8{zq^E3E9xiFXdZL8LjuU4+6e%*=hqj9syS5mw1obEj8*E{8NepR*G>bo+XoZt54Lv$Q}ozL$zkkw}g`HuUy`TT5O_H&C5(s|xLRMWl^ekRqwc$DY7<5y38HJ8}$TE^d>1@~!PHL8w$rISWE%EY^L?1*`t{eZ>?=)C=2bgUj;S8aWNm3O}3eJxqTe%xoguN#+nU)$$Z^Bh5xqizf2Irk)T{*sgX$bWw1dvyNp_Ut>ZkgpeKkgsV+NtNEic>eLTXkV_JU3?yX7qs;b_I*m(H^1K|#_@GHUqrsT65mUDEcxo^{j2DBauVkk?ImBgM^y3gYQ9hGTi9>WvP#NNE+N06#J|d#uN^8TU)%SLZp~LBD<oe%eTDlsy2-a)Dbua%DnobI^XIx$x8CPk(oUYg#|+&%k5>0A=da1*9DEPx@#Wlqyji97dYbvBuW$XDug~7sd0#L3R$AxL(l$!Ieq|^3XRPBn9gR3Y3BPM4&v1XFSEY4M)m9++=5<q-&E)H>bvi=F*X_J+%@oPkGJoX!sL4G4*p5f6*T=k18p1jpvEC<o-{q38;dwxdUcxyyf{$45b2V&}<SPaIJfkh&!28|Y{eboQsD){=e~`bowTr2|?i;}ete+Qs&jRi*Z%e+m={?SQZ6V*cDXqD`I+XoBtGWM?0M1XF&-*&@0^k2tLteG+SG~Gb^0ilD_<jE^TlVq0uixkEqvyo3KjEyDZ~AKFX7<<Q^8Mx+vDE6TXEG(<Tvr{KQGeVnJ@t;NFY6uML{UUFHJ*B>W?3G2g(+U9{{16wUcZ0$$Qu>)e;;{m#tbcu>VOj53fdIh3LF6S1qXlwQG&%YbQ7o#O0XBy7wiT0hBgIzgPTKJf}4ZeL2Y26-N8b;frYjKw*xna`dKplEbIE=Eo=mB4D|yy2Kz(Xfc?P_L%V?=2KRzSfqQ}bK_3VA1II##fn&i5(Ba?&@CfKA@Ca}UbR0MZJRUk3JRbZMN^p)*Q;o_q$_dQ@=b*=l5}b<?JOw2<6*>+qbTnA#7_iVZa4J}2Oh;}ubP6~dJPDcx7WyQ35;zk&5iB$VoC(e{YKBoWjmn2k1LuPs&@8Y6oDR(ZXJCzVl;8=_vET_{J2V+=2akj%fk%Q9p(;2LJQyW-0CXUD0Jsk{5-hYQxDU7ov=g`oI1CyL4g&|F1h<Ah1b)=0E=F}l3GN7e1T3^IxFa|O+8W#%nIX_Xa95nu86`Lr8UhYMzu+N84K*qb8V`;G$3UL|$AF`ugTO-jgQLNHp^t(4f_tL`heIR45tut1CAd8_6x<%%0vZUmCwqAZ`TWy=wfy<g#22mfA1{ABQ~tTKo_Wj2dhp|APi{;<S>DFKrwz>$lPG@x8&hND'

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
