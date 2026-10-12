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

PART_NAME = 'part_011'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/13cc3ffc69964894a2bc94154aed687f/part_011.stl', 'relative_path': '13cc3ffc69964894a2bc94154aed687f/part_011.stl', 'source_sha256': 'b9d2d8859266a5e67798b0a9bd4a2b126b416c12530a2b5510ae9a5e265ac66e', 'input_faces': 261, 'input_vertices': 209, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18671779334545135, -0.10501710325479507, -0.3077515959739685], [0.1543869823217392, 0.09990356862545013, 0.48045024275779724]]}
GEOMETRY_BASE85 = 'c$}r03shBA8pn^4Mh2xu1!8qniXcl7AL*D}%g{pXnu@6@mw5O{<)M-o>0uCjD~9H?yoyQrObq2A+ykhoDYBySktOPkvzla<W2?fMX*K8j_WxYYIh|Q+*34b&TmS$5-F^1ik8kgDE(>Rj&s_nM_;iyJqFP1<YDEe^DL~3h&X_wrF?r52v(vKLNFABeN7uqp<6@l?+DMtw+o4Ixa}qN`2g#v>Q=Sd&DTk({X3Wh<m>r**k(5k4I$`FVWR1_6mXMaLm7na>dtgsFGOVZkj{HA<I%r*RO}X)zhx+nN=F%uC#~->7W#qjDSFC(Yzx7mh><%&Wv4Xq6<)UkXJDqvVvu83_Z`KO_Y<w1#rL$u$n)qPBWpH<d2mKkmjr(&v_&jT7rQmlrxVh~Arim-yZg5xS5mEo*h(d0E$#Ldt_Y%S5e&YJBUcStm>OT^E{=I2jze5oB$2B=maJ6X|X;c0Q=1q%o1y`nx;qr9<OD0|*xHLm>DLqs0TP0&z)31wp_#r{`|I6f^T)wOEYu4UVME(2|E4e)Mw5abJEV!d!2w&G+aLL3a!QJ3;+Jor-m8snS$1?;^@D=x6p1+Id&HdDQJFbGe{C_*a?YIXPbN#S7?q`#HOYr(`8+e@4_lkbTj1#<KJ+GtOHH*1p=ktP3TlNvR8?*Mjkt^T|xReww>UZ5akIOfff5X>(9wN9Dm&)VvuQ&6Sam=Or1aE5YF516+joX(>!o_$Sd@(Nf0#Z5Yl&Igh;yCjs8&`3?bJ5J@;v~T@k4)$KYvM1P_yxfo;4aTV!Fw*u=KHss%3Qe-EO_4uMLhnjmqq>u?>@%-YG<BL^?QH5uR~rfxU*_Hx3l$|%O*ZTa5uQCc9P&1zW<Q#=XdW#BUixP;L=(r+WGP=?*FjAaXaod4+tK5Kj(uIc1)ZDzkFZE{FCn{GM{%x+_$WjxjW@r1*vQF%`+Yw?oOO9%8yPK?aW`p^P@(VH1ho$!vt4qIe%Oae#v>O3<?ok&B$dwu35}yQV&!6@}3cO;=U2JT)*sG0_Vxts&Au={1d^YaTdN$Ud!`)WQUlCd>`iOjJAiP4E=Ps|G9?ikB{5V^EkVP`>AsUTn1NSZj1UicVu&(jR`mNk>dRH@|>%JpS&{9mbYKG)X3Gu&jg>pE!CF)seFa0oo0{Vfhlu%e%`&#^B~_Y5`5{OlZ^Gf+%;{rk-Iu%3GV3pnk}z-rNGqAx^yu=JInbTmM(1*{VX5N+%a=W8T02-d7iD@5#6VO*LQEUXkQK+X1cG=_lkA&j(5kP8dH9T=kdC_z8xs)`^m+8A9t>aD`WGvbNT7OI#d0qln=Ony#vnKaff>m?;l5DN5Q2ZLyZ0L@_+6!_0zref-35_+^DwWYNM&Xe4|Y8>Q6Uv`J0H#Chig30q)A(q1yGw%PswJ%$TX#&9j$V=h<(NYL^dQZq0`?-2~5>%;%o_*Ir`Zh1{>&<)N2b^3eU$FCJcx;f3Yg?&h;!cx<>-U&Q$%rJVQJ?H4b%>=$=<k;iU7dbwpkD(~fZZ1=m)E&JV(oGJLVh8)xW-S(2;ILFk+*S|AyoMTPk^2eRf&z}>yf4_BS?tZhSny<$>=C~frd8;hmTy5H4xgQH&lvHh;H`kCwV%{#?sba;sp~?lK{my3vA0@`+_^SC^6W8Al!5w>os_fRw5x@7Sk*noyzON(C$z1a7rSSYjcM|h(`EsS$7veoldSSIKm%-(BDV4_Y>gSB>c5{Vk|4#i;%tNQL3S)iQ_c1XKU+ovqGn^;tUz7QKP(GbxYDeibMLh2x8ZYYo(zV!FU%eR1Tt8=;O71Y1mq&_r)J<vJzY-7k-}UR^a?^eBJhF1{^B3HEUZK7eU&7pRRWd!-)ZtqM?{bUBt9EoUS1R(#?bb_rKib6A{%3f8<o*51P5GwJ=j=ei<L-!j+Y~G2^Yjm8Vn3SS2V4PP9I;z3$B;x5ckCX_?KGYGd#PPNmHGk`cf@|j_1)PKSF3I2^LHHUrE}$aP_Zq?I;zbrCT`6uE7$Wx=hk)6xph9h^)2&b<@)@1+p(UL7Ou~a`r_KsC>!n=dfUXk?UW`SiL$%ziZ4vuyN*L|in3+h-IE>``DDqHrqnLt9FMzi8Rtt?gvi4!eMNoC{5S%JmmB-3=ciJbBid01Y~*|mX%zj8$S=1Wm+aXh#&6vhUzZ4OU9Y)EnEx)XEL`8GI(IdnKg{>*`41CU*Zk!GkN@$8vqr9DPWq7hadZ4RBe(8%E0;FED%RIIsv=6VIe&cOm|M>)*Y=4O#&-0)b&NbvVH&T#FP4^77}s4tKh-NYP3?HkhwPL}yF8Ic?m22&NBz05F|f*Ry<7!})kdyAzm)V%)u#N!^Ui&(rP`D~cs|OrT0FM-VBz|Eg&Z`f#<ae8&(yi~JyYk__e^hn%X_Ak>+hMapGMc%&6}0$@6U3rPpxshdY)Lhe5<Xf@9t4&9GCt(%d!6TI=lU=q|dFh+o!G}#dUW3uIa~GQ~Ub9uyXzPqt31SMd#N2qI2b62lv>uBVD?}`$*m1;h3quWq*0=$N3d;KM&44ZsL~xW#v4dPSal%izYwkf7DNsDDII0q?821pA-qwM_2nlDNgVE-~CCkf5iX$C&m3*AJ%HI2D$)#4Scp1vCvnb3*bjV--0fHe+#|<x)z>vKYRiFL1;BRX%+lYEh@D*gCPGog8WHn1w3814cC$u!XJd!?^}pIlI9uuoQE-uf`1c1ekOwad<6M?1o>sqLilCy>k;HPL$|?ihJPPH{u2cG!wB+6pjGfR?tNMufUbr=0KW=BJ`4Ibd=`8Rg8WFt+gS5h_-yEE_-uGRPss0u?t|Y8e-yC~YqbykuEaPRFqXqm6+ylh+5q2xYw9JD5A}xj$yY<G;5TaF)?yQa{0`_L_#N<{BFL8^$d^M);Z^8iXsKb1O0jOGxJF;cLs;8GxcB?ejZ*8nlh^Zs{CemHc+wS8Yc7%3bBugGbTK?>hSZv$<mW?YNv%0dp7MGG)CHXdKMU88kB6p1GvL$VbD@jjbK#dmSHLfae-F9=egnq*9&{7@XIkvi;uN$P{uKOa=tuCU;m<-phCd5`4!Q^a9Q+9_wrX)qiw~g3;Xi=i4m|;X0@rRwKTo2Mq;>EgLRV_hON&KX^oI6@?+vf-NAg+FMN;dYCBF)~5Pl)rUIpDHweEfL2cUIQ>-j*w0(ugjo@X^$lt6dFm%tYx$ZtWAUk7~`o-_x39sE)R`9C7aXKFDV`YbdDJ_5P~nggGMdyrS43lU2&2TM?AC3GkJZmh>v=t}sNsIwJX1HToXa^W5=?$)9Ml*;#NahDc8;6C8w+n`L}`=Ly}Jv_1dQT9i)2k(gQh&>2TteX}AU;*IdA48eGe;j4<A@Ia{qD+3M7GYpv;N<(GOy5sOc{ZXy_&fNH*c>h9fz1OapN2AhKMv*B5ozGj_>R~hcw$eZOkURFDX^!&$#+GWzJD0yKtxyYPWUbm>+~?#J@CXrwdk%zB!c`i2=b3;(HR;9?G7IV-vt^9-v#~&1o=J)@&lle@T4=~2f(Ky$j?QPpN1gc4;l#{iGKG(kbe?Ez6bOX_#W_&BFH~r81n-N^7kRgw?mNEKjhmY$ooQr;C<mAf_8y_2tFA41bi@jIJ6IZIQ&2a`LWOe@B=V+<fm$ptVIem5k3Vz37P<(1pfwfGW;9xQxFrim;^S_z+MBN1U~^92R{LRJoHug@$h31PAx`*ISuS3@X_!uLx;h?4F4kZdH5IMUqJA0N3bXZdk)+IKLq**_#yCvsXsAo+6MUir+=qt{U~(Unf|%LdZqa%lkv(pt&;Z#lryFsosU|QwdI$NSUTaPe*=St4F&'

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
