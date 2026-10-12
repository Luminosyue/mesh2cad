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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/42e5ff17de214f0d8aabd509f090a46c/part_003.stl', 'relative_path': '42e5ff17de214f0d8aabd509f090a46c/part_003.stl', 'source_sha256': '12c8f81795d0997eb6b3484de96cfb6d36856e00c4a1e8c436a9c07d97281609', 'input_faces': 240, 'input_vertices': 174, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.06870497763156891, -0.3058869540691376, -0.4132578372955322], [0.07174792140722275, 0.2318374216556549, -0.0005942580755800009]]}
GEOMETRY_BASE85 = 'c$}q~3s6<%7RNWD20{u-mZo-0j5GyBLQ|A&riJ)G4f9dDK~c#Uf|`MklcL}|P|-l}nDJ2Ym0H&)M-bm{P_wz-wq;tku2VYA)Xllwz1IGp!&!T}Gk5M~X3hV1{%4)Fzy0mCzx|y<T&#EfAjSM^t1LfJSbHTvQ7HVCAZ2b+>g?nRNok=oQr`Dc0@$ZNm#!NUKR9l*moit$2$`6aHX${nr!6FEQjd^Mwvb6PQ)j0p%osm2bz&0v0}`gCB^iF&l!TNd<MoSOyGL}gb?eZ{w!rp3{xvd&pqAwAt1wg#-*-0JP-n;Rv-H||A%}fs>pNHY{o;Tc;rk|?Bennb%Qa8mId5JSsoMFn@b%cKhxv2GS;AKjOxVru*9HsU{^-tne*a?mRZm}Ar>>%L>V@rvZ?A|dAzwSP{)(sXsI+}bzWtYbmqnfaVTU-sSH>kV&gW8`>@U4>L7Z>tcPDv%M*hU-t!Qh_@qbpp<976l<oVIZM4NTSJ?8n;i~K9;we3Na=?4#F-&Po6&THw*=Dc~A@%h+K)w|*8+lssKxb+(Sy2xKS;5?s4UJp^naWs>!pX2TQB46#Zx5}*7QRM6MquF;HOcVKfUL{{IhoiOdwRM5)JG1Xz7WHet-ow80K&{9>{8c%hm(NQgUt6$g6VKy`Xp!$oekq6ReIIej)3@Ib&ZK!$GOB7s{?+ce<f|VvxhV3ZzS~B=<6r$nzLvbIjIZON>hq#b+iQEdPZ~I{i8@zi?dST<hn^GuuhpOP^}X9s<m<Vc4)gWh<v1he=i%H69{<QiSH<=Hu-yr+zhTcQPhY8t;eNBld@in+Jw2<M$A35FB%jZvE@u9k7Uuo1aS-R*cL(GCnq{8<`j6OGe@@@a$1PmQ<F@tMX`a`p&g^T!5$Cx7*T?^b-~X{A`}%hM43Fo>r@5YXp$+>=#1*b<yEpX<PhU^D&)36I(_8r3t6t`P753G6Pv3F*49}P1{Qah<Z$GAUe`-hnab6xbfPLrFWg=gX_dCM%%3qUy?U_UTxmkIlj%{|1sgG{l5aTS~vXkp?yLV3bH}@CtJZckV{*rF1xc<%`&I<qXg>=5Y7k|Dk&MR=^2ELAe{q&5Ohn(NGvfnII<ZBNW?cn}g8*|#zSNG4_!}-}kB3~)bKEVCiq@-H-xAQ*Z{DB3vqJH1%BRtMK6;-1C-a*H?Z*Mmd`O2J=RXm=sY36gGAcOCJ{n2uMtvtx${#3ht!}q^4X6{AKZ+NSOefur;)m!E4D?a^s{EF9h_Vsfsx!>#s7i)zdnaKUAMxR>9uk$yUe#ttsFEgL`($m+1hH`&uv46Ye>D%*dW`8~`6TZ_smHShl{QOx@-|^aL^L}nOM&zrG$5m!O#)y2q<s)AA^|Al_LX7A4NbXN<$6Dd*p@rO^wmFJCZt6pGzQ1oH>ukThgI|9>@{AbIvug|a{8sI{DUUlpoBiRVPmB5$g{eHBGgOgpzy9$??w|apPKo@lFF5#mdEdSv>Q|QTWPjhrlVUtg+wJE1m(oSPJvsa!=P$ig>FF!ezhPf}5Gd=n$v8^BE&rNR)UU}qM!w_TN7uzTw=}Ed@uxpLDvnz+hx^v%@6Y+p(q)PCTH8Fu?AxoUUwZn=PlL_={-B^r<hOWiKKH{1pZ4_i7UuKSk?@A7<0!h%eP!DmAnQAG*>?n+{pIr2>>m8uUVZ$QsNbpq&#$d}mdr2uJI|v!W~|89vioztDNzr;5Pp*!?l<SKexi=;xhKu%%vbYeeq0&%n{qy1oUeMnc@fX=Vn2~@pD;a(>m(JP67z8StrY%Tq~oTjKO$lisk70@YLTCkZuVPEw9Ie(huLp|*Ti*En^o@O_xs+tA?A6$#(m}5kGcJz-RwKJ%oq7uqutzZPOo1p<oQnEepAXCiF`+FDEFH-C+vu*UpS8YO}o8V^qbyzDz9%^p8?VjOXKy;{>Qw2;<(2q^E#=99u)b`$BWE$wMhMh{h9apezUHJF5kKyx_s+;=<==Wq06_fhc4f`9=gY4Sr6Ugv8;#ge9L<1KCWdwbl0)0hwkxM*2B8v%JtA)-?ARM=f|=hy7MjTp}W3iJ#>%9vL3qYTh>FDZ(R@F^)2h6yS`;TbdS@r9=eZfT@PJ;-UZ%g+9!7?7ULP!`xMtJII@*|HRcC1|Jz#j)nSthJ$)r?^=TgOw=ulmcV7R^yuOy_yW6)s-_`hzyuY#T6I7oFbKhgxS2%Z#XJ0uU$K$bgi{tTYJ?`=T-nu{0BVXUg<Fo8b-M(cX==Lr9J(q9Y*SYg8`!|<w-KV+pE&DN-Z@Yhpzc1)<t51kJAN%q7IyVO#=ku+KH|tpT^ZM9rW*y7^Uu!y!zb9M2zqows_Y{{ezK_I-UqgOrpX2ZJGu|@7R|!%kC3yT4LMHvW^v{0^NsjohehLYX=<@&m6tb13(1;b#ZQvE)RS4oW&`-dm#o#sI4-v$<&=PQ-5$la8h30~Dky8rY2_`KElkNhSg3F-W!DZkg=tp4EO<>ZE;Efnl5wsM%#fTk7BtR3v{h%G8iQsf2-Zx@Ag7_Wid*FA#W1(}vW5J`LY2eY|x1h7YZ-L{XGr{rT5zy)25#V9aso-JYq0nUTQ1B4w6z~x6Am}9UAn-uwMDRdx40HlG2K)wsSVIsmL=Z26P6RIk+o6-dcJN~86!2njCNvqG30?}F3SJ7%f=&l#ftN#Pf|r9=LT7<jf>%S+z^lP)p>x1%!8y?Pz&YS`(D%XXz#E|H;0@q>BQ`_lL({?ip#z}lVAAp60wW5I$bc>YlfDKfeH}c_h#5w_i69;cO#zPtkAkLxM}fycXM@Lp--gZwzYQLTAfAUHUXLKoh0X@&f<J_&Ds}4>@fv7~Qn#iNuY%4{>efTz70_u)-I__94Sg4!4PFMF3|<Ca0!;!h0e@hG1G)o2oCr+<hbiVd6bnrRCn6^nK|B~b89W#q2YnYD2ObWc2A+m%OzdOC6Gl9TAa0EyeiqsgOxghaEVu=N_-SZ;a1hiRS|1!}gqIP`p!LA@@P0D{@ly!m=Fs}!`Z!*51o1Nn;+D{c;D$J#mI&fj2;w$SAF#g>FBstm4F;1w5B38$LJ<2xZD1Sf`9gibKA3l31aVsgaUTS66oR-Xv^BUju18M<aSsG>B(w#%1+GUVf;a*}+|}dybwv<2g?fX%am|`Sy}(VuFCvILAc&tt5C=d5!JVO@&_FP0GjJ%l3xYTt`V^S7IXE2L4MF@e^cgT|OYqC!?g-*npsm2Ia4la!5cfh5_lDZQq|bwUgQF3|eWAf%(igye!LK5SJ0XahAcz&HKlmjh8XFM;Rlo{zLZE)&5O8}0aXV-uFsUz?v@Mvl54aszMG(8ze`41&f_M}(3QXElse8T<yPiSBZ$f*3Nh6iI=NIvC1aTZR0!-Q!92e_VFUb2p{VTNY&rVG${xNF(r2N|8`N_sc^SZx8#KktCb;!73>hb2nm+oHW-~OZ%xB'

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
