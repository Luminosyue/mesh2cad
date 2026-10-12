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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f222afc918e14e93bcd98d98aed5c698/part_007.stl', 'relative_path': 'f222afc918e14e93bcd98d98aed5c698/part_007.stl', 'source_sha256': 'dae3409a71af2b9da29e84d960b5ab9362a747949b2dc615cb257474bc9f1a5d', 'input_faces': 402, 'input_vertices': 332, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.36363595724105835, -0.5454549789428711, 0.09090910106897354], [0.45456162095069885, 0.4545450210571289, 0.818187415599823]]}
GEOMETRY_BASE85 = 'c$}r133ye-8HP^)7ZwpAiwc_SMhJ!o0TmHQkR&QprM0$NK|>`}Q3ECsT&j&)Yt?F{T9>L7SGriWZi%tRtD<oMLllhCB5^?x?P9Clq@^>S_dlF`=ftN^8=v3rn|J2?Gk4CM|K6KC%$nJ^Uv3co>=hKO`t-78g+btBP>>reuB~r8?UdSv(z-?G<^)4N=l;j^+M|y<YSsxk!Q$ZjqItCqr_>is$`nnWKe4DJQ#5~JePjLHx|0{y&#U#kdhQtwwT?HOI(Jd6YmXW~zN{oOzPKcFLFRw_8Q_+X?WpQ{(y!&D#<#pSb>^=xPvM#MTQ|gc%>!FEd=al{Y<w%uvv(D&Ps?vy^BC_fPsMqg-j4IkO{MF;hzG%(cjLV2D%LCcjcXp`z2)h?v~y#RbzU@QP3rpLn%{VDd9nkm-;eW(#f_b5d5r5ijcb16z2$G(rFBz}^RPC5Ra$=In%{VDd1`Jb-Q45#K2hDCx({$&r*X}1T=O^WS=F4D-?-*CuKA5?{-Ar>^3?r-C-w)P*dKTze^9ZhE#<x&Ps|HX%nR4oYdo=@b=AwuQ_i#T#CqU~dEtq9Z#ld<H9tI&AD(!<@Wi|u8=gwd15Z5HTdLaA)??iAWLC^xla^n(<u~429^*E?sfFiR>a%jIpT@O5E4SBWT<f!P&7<{MxxFsqTA!8c>(%<KT=QssR&M7ZTBp=!<(gmXvvNDn#<e~x*L7-rR^D5FdrqVCAoW?f=GXeH-0DyCdZj)q*L7-rR<8NAJ}cM!TA!6`eyz{S6Z<3eS$QJA)Mw?1d8Ixp*Vn7{IpR{El_%CC^;vmhUa8N@6Zxe+D^JWT^;3D`xt98@JW(HdsjJ2l=eeZ1%eOPZ*-xeMih}UE#Q4^#t~B2LZ0Wi*uJyKJVmNMDXH|0=*YyOI1?#_v>pG+HvQFc=PUE)D?mX%g?}xTd<(Vq>6`s94R2^?z$5&KVwWp0YuH%E%;q$KJjVHzji#~2k8xPm<P48DXm#2(39*sYtU{%`lrQDvch|6=KT*vFVRj%Xpd@8s59?dJ~M0qs6BfKBo^=Jp{65e!0V`m!AwuJe!9ntkY&Xsc8XXAPvjO%@mxZGdkdLNq(v++{5g-3NmcvL@)YrPeo7_aqHcp{IS6XS`xCtUOB`7xfThr**eBRr}n!lSwePt-l(I&Y%x3D@-`>YMPWzTI}^bDy8L#?D82oM+)RBU)F-xjS%c+fv3G*YQ42c`y0P<Kxe4ZAo2^a2+3vov|d;IV;n6MSE3853cJMp2%N1V@Y{hez@jOyk6m!Kl@&Fb7~zB9zDPCL>+)9>VR>r18}VaHKRhV=U=&<H{*Jqm1`b7&&n--W^cIMU*)#{5tsX=+{QQMh5HrE=Kc0Wo)5UzdF58;m0O)xZuz^n-oK?SWuKMXJ{Z@1R<3z;pOssFw^3bfDf?ht_d&VsgL2yk<(5CYb;-w5)6T!}=-k2+=O3Op|Hk$F!}a`Ebg-|o9_2b-*JE7Q6LDFO@x*$@gl)Yq#`V4^xBH^p?u+v1d@c=n;(Q8^&L=!^K80(Z#Q78+ozKeXb5@W0qTKe)xZW4zdS4<g_r<v0mrMim%Kj_2{a0@LZ#)<i)%*4|u6f)m>zbN29^Tvd#Ju^@xo%J6i9GNq&k~*|IVZ}adJflfqFnRnIZ+;+li7Uk*19A-s!MR)=ZMRGDz`k#ZjV0i_c))*qjU9Y$aUY8N3RR6`=(s;=)NhBp5J=D_e>9epP9|04hXNgKK%WI@oZjoSK4^vHhx(Ld31k-+x{5W@6pP2ync^XuH*H4wDQDw`5vuY$LsfK<x!pA4CniZ-7n>KzapL&-p}ZLN_Zj<T=VETRIcOo94gm5dJdIa{_LlGUy*%Ko)|B$SGkVY*Q-4GK9$4gLFSFVuL+O7ml>D)qFl$@ygFXjx$JVDGkH#xN6#HxpHt<ZkDt}!ulq+_*MG|K!-Bv^{~$M*KR5QLeGmPQY5Je`Pn+;x{b_%~*#G-a`*YkHzU5*zIv;<Ri@RN1js7s^e@5HuQv6cd*PzSs)^{~}4gOAY%|}niFX#HZ(7W-ro;%Px@u$;X5F5LIT)wXsU4XxXIcm{`_<LyIj^2S^NV^Wb2VYCyJhTpP>$iPa8uP!T?e$vxQv5aOkMKUvFUalnZ2Z}@8_}QRt*;Jk#9!y)$1cu6&&6Nw;s*L}pwIgz+TTI1$6pt_?i`r+_qn*Ayk5`4KkVWW`X8as`-^Bdp%3Hli(Pjv%zOV?!9Q<((7rK$7;UfH<0reA5`;fqb7FoPZLizmC(~bn_QU5eCP4e)D_vB%*b(g?^GDG3ItcIAHl6i(-67@=r|oqheh}9WM6GWiegImH-+{jE(E<1`xj4$j5OkNA|1xc_d3Zn9k<9OPr<k8b+iNa9kLz<$>&wLtLyy7Ro*aV?!|%j3gV164on6dyF&LeJx9f(YN8@dujz)*#ZLWdnQ2cQ&zUE>#boZG525ql<;{9v<3a{I1e$1ah+v^^9+uP&O5%_$@<e?+*ySn(QivsjmyzSqyXaU~#`|Id%yv>!14#%J5;+rn^Mn~dD(%ui9i?{cMz0m#f`_mpBY<s`(-oIyLXlG#aW7lNR(fE^H)VSCO-4}l{Iu9L%w|vF4J+DQJ@x_es{zMmr_`=v2TU#MojJNlT(dYsA1wqgE5zBu7?b2Y|`%7uC?R}vb9giPRyDZrDeo+>CEp=!a-mV#imf=rzahi(~bPWC!auvmL7RB<7b8&`?u`bR;$Kl5@=1lSw;frEpY;Bfv9Db3Dvs_F>4~h9k+FlREA4+=?+JLvdiRdJJ9l6TT1Mvsao`5dGTi-ZzLhLm(;JqG<KbZDGXg%Kg#-az|r?@wUau;Rjf%vJkC!<sF(_K`#7>7>4SJFNVosOSCdpuf+_c^CApVx!&6||?K<#>PX;pFpr5WbprC2Di*>EaL<d!Q5Xex5^Jj6gH^4DCX665h`<oc3_oq}VmX(L($#%sm9%18?JZMu*{t(H<JhGn8C|X%B`K#;zHR4#od72<QF>Is|Xy{~m<8B?$c%+Mfm6@_6ra{VfRFUO&TkIDON_%jkOi?_6}dScP`tJ87>*H{gHkVkPaBunn<mR-&u%zYfB=A3$Hm+xTCh58)r8{a`H5gXFrG_Pwyxv1{%{AH;u~xz9%*z}xsG=!N(TX<rb_a{;*)(_Reoes{O0ySW&N?uQ?VAB7g-N8v}K#rV<q5_Erj3BD8^gD=I8MGwIL+pXzetjnukllQ-O{-Yr5|A;Z(|Ix)CT=)-`Ubo`^L|;x$sGfQMaS-<PVT@<qzwi8eK{(HQ%;Eh9E;f;C6LWe0p^MEym~S&Vy>EB%ToC4aj$Gcq;Np4mJx?z0U!-p{`T_nW`aVQA<8N_sGxOZc9Nz!b#jWJHl{vh>jlLJr7x2sIdkK9Je~F8Wndf5W@cz5BFGVlGe~-S)&`a^(r|)v~GW-?vU5Q?f{{ekhp;zK_-M#7OA`jgTzXR=jG#9_Ui@x;trO*5RXaSm!-;rzjqc(N`x+_|MA4Gen*f{S8l4}s!AMfY?Bna2-^;5iG+h2mP-|Hv%jZWWk@mKWEcz@lyc&{7r{<?SQe}_Krea^S(f15t<*SUC&>tADzja>Hz{td=$<hs}Cf1SQ}$=OAJ7kxJNCdPUF3Eq#nk^UR$^FHh1DHp#%pNRR#XnSqOH`9I;ZNX=`t_6KG=AWQ#*L%Oh#j{-ZEc2Ovoc80)Vcz$(qAT!^(bs~u;#ZKb6>Y&k?P86KHuM$zGcNq^z1E_y;-5jEM%Un9VN4tPB>qXRv7ArG=32{jYq`ezBi)%h!o^H<27VtGd%4&b-5Wn^W=@~nzP<gEn{7W$IsX6ge}JP`_WX5T{K_|7uIQJ0vu1ARzjp_H+<*Q9=~@0$d+;BXQ9bG'

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
