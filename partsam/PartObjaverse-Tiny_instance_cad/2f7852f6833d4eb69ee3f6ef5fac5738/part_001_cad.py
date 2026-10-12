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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2f7852f6833d4eb69ee3f6ef5fac5738/part_001.stl', 'relative_path': '2f7852f6833d4eb69ee3f6ef5fac5738/part_001.stl', 'source_sha256': '5def16a91ac2aea089928dfefe8c4b7abf70e2b98f6cd8e3e06986bcb211f733', 'input_faces': 190, 'input_vertices': 136, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.21353685855865479, -0.5, -0.11460582911968231], [0.0992995873093605, 0.39667123556137085, 0.11151005327701569]]}
GEOMETRY_BASE85 = 'c$}qJ3v^9a8s3RVkq|`<MO_sV5}}D_q;e>!2$5)lXv0nOAfiH|BnU^D=&TlFJd1Ec#4EH7A++RpQ)LoVQ5`Ams*YB(mQfuu9dq`#ztf(ZW!9QCbJzOT_nq(jd!K**`*H5QF;R8uwh-#mLEPJZJxpsXgoL+fA!ep#%}7s9%?_G6E!RUdg)cuAuZWHx5tHB{W{Np}DXH1XS$?4ozp%8vet{0Zw9Kp-SxHkTWM-wLN<SiLN_ML0XHQC+mTF%6zYx+p&=Jxl(2?i(A3u#`4&CC<Rmha8PM;4q+2OHtr@S`q$H6xY<vZuU3tvPJg|DZ~sgS-_(Ovo7=%1bq-+Af<<v*=_?U0H$8Y$m+cK9c_fAyPOwA+7wD|qkZv+#osY>@HQ^tJo3@b&Jiw!(k-cnA8qqkK{5?(0=`PN7}vEh<m%!2O6{sC?n0d}m4kd?6m5#Qi^2okbn$E!&6d&%ZvY?tdBPmQQo~CrXf~aa(MEqQBz1Ey%~?@o{kC>WjF4qtyaj_w$0U<pi98U-`>gwENev3S3usV|>-UAAJCSPyP}3*Ml!fc0MTFA$?c*?T_JyY9GmK@owBUT>o?yzH4688Tcz7?}9(wfbW=FjDE%8!5FV&-3IvD$*@mQx5|H_KDu{MIohr6h5n5t8!#?o(lhW~ff1_z)i0wCMnK2`#5=a2f8E!o6#blRazJq}^zW!yh3D$U!xblMsDnN?0Q0H8_TvZWukfIn$4#RT<9TcEDSxl>jSI>bP3|iHtFu^V)ngl$!Qc2-_|^1{1<H4|JqceMx<d6+&<4If{}_CITwx{hToiH${j6}ocjZ5S3G3(WP{ccb+@#`{D&H}qAN=aWjW7>Jami)0&pfjfaWl?rRqIMr<9hrjC3au`$@>etuRYqS;y)i!1-?8vP0h#DB6~k#TJC&2xBWS_?#5qJd53o^!uZD3+l>2Hi_|)-AG!>F-@g>%I?wkC+6_Ox3VdO*3;Fw`e}?N9Hy2}GLfR@n|HuvG*Zmgy7tUtNPx65;#s%wGpOH;BsXSu_BEHXrji^&;<4yMbojyyqp{^}kZbY8pp2*Wt@<R#oY@oe|xU~n7r*UM^I_%5qv1<@Nsr5DF`9uE|;G7Z5p17_ew0z|8@F?<h#(cD2t<yie<yOzaFUv8mGgW!G*4vN4_1p(@)cE{!?eRuh`F^{vM;^QG<_|6#1%INKnwQvFD^+_(Q{;c6{3`M~{|~iKy&K11+{>e}evGY$upWf(#IYE6lk1ol?YVpvZ*)n-I37HOx@p-hi<R#=6?q@~wo=tUQ~71T<iM}4KN0P2-rorhXtEg3Z9CyK;$rq;-bBs&?_wYBn}#}z>#?bbUwm{4`bl1N759hi*oEufVmb2cT7-40zr7OcO?Z^S*JF!ReG2QWz_sST3Vig<gV<-$JN6<zc;RaJ_3M6)Iz7l!>#b}f{OWJBuwO*UDfoKo!1r*!);TGb=<6{q-_xj@s9W<s;<t{%d0qRw6%~C7RQ<oMLfl7uPu27*Q1!ZX1>@cM@Izb={sO*;c{3Z_<()smZ?0jzSI0Tkyc}$Yap?tr--P}TsD4~6kC)ngtAAtZF*jf9uj*Vo-m1S9Z=6diM0}C=m#A~ZP^@RI*<AQyl&{;kjBB56#(n>$Y9Ez1z`3A(U#a{7(=Xz=jMw7Ax1b-cf9?BsK1P4*4;8ujZ5r*Zu=&>cX8Fbfb$%Ge5}d=X${6*&{*dR&dgWJ-QNA|5ncBx!PvL#7pDtDJ>xP|hJ{hIcRox=ecO&n`kvLbx(XXo9@=uF`?`qcf&**31^j%N##T~xiYx`@}`@OcW^_q!uP`|lon_E6UkN1SzeC>+zUF`+dq1Lg_cHF=4soF>9<1tUhl_L1o`K&GOf^%Q%Z(yI*{{EnKIDzxhu`)=V!x^`64r;5<q8=is81HR8;}Z6v*6!wR`+SMwD+P%6x((ktZ$-_ydB`ts7sg?|*YulHR2^PjruI{<?>U;Qp4v~=`|H-Ab?|refbXn1jQ6Zz)xVanS#_@EyR15&NmBiP_MKY)7cZ%EjK21>^0ix+;k%|sV805_B&;K6n{oJFpe<Lv7V3nr-A#b6?>V9TM@P@w_lt8^W~seyx@TY1-|`*N4{q4~>i%!5eff9*_M-@V71!GSt;*+nR=a;eorB3W?)`tzZy)+u6OZ%5dOvD+g4I4RJdFEBSqRpl!8{!WCzM~+;JkhPSMPqM4A1#0QSCcpjr!hnh5kL|YfF^xXdMS%iyaT&aZ35lg!L-^ZaMll7XHo6*B&e1r7K^%@iX4H#^7fz*z<IiW*kI6-@kqh-0L>ZQ_DAelHqId-xP$$xc&NyNPOz~NezXNXlVZWN=vf+^pd9hSp4LlUg<smyPsbDdi=jXy?o3Znwe-yNc}Xq4RyYWG!xl`)UOayzeFBS{Sx&E6S3qJ@_6bL>U?q<^<on<Or(-WQKwSJnCNRF!9*uQYJYMD^;jWa`R3OnLh2lH59%I_%^_z{k2EpZ#0!MfeuUKFgw&aY)OqBQ)Kg5nY+?u@bub}yAR+ZILh3o>Db#bQ-yo!(Xkr{Wojiql3ZIuwNS#X_N}WqRn~*w=kh&KkbvN=5>Tc9Q<Y4N~<N$IobpW+5IgmP>>_-l?)j5#04`f}exfsU!j-<{b&!Ntv&LqEKo1-^ub0>8ec_MWf^^3OpzDP*jkC3`AA$0;dojQR!gPcp9L7hXMO`StMmmDX4Tenh=C8X|6?nT|3x(B%%bq{KPauBsYbtl`LS^KE7ZCssg<L%5Ebmm-IH3?wN0yuwRwt1DhyNNC)G;#!WG<h;Pf_fl%5;=l;5_J?Ibx(2^>YmgC38_QL-Kj&V`;awiE2ln0G-IQgN2o17sYjcbYGM#Mk~)Okl^jXkmD<WP(l(YzjxUmZS>v5*8;jHf$fKzTQ1>SfqPFtrPlPZwgn3wPyRz@D%t`7xLcXwsc#4p^J-IFQTPEH#@hZ7Jb$iB0-Ofa!iPualATJ~*Qg<YGASY5MvV8}#7j;LnAbU~QB{w2_QG2ny)X$r6m{>$et&^Xl)~RPQ-h=lW(Dx)es2z-v`gbOpn`ljb#-`=H7UWjc&zfk->sHj#m;c7rHxX~5iI9KY3Ned*61DVSXN-)k$2jRF(~qYfZel+5EF#$!o5h&n)MHFIO-y6E`P9EBvTS}9`xwI*tDkA?qcQVHV$QSp+{V=2^sR9WXFDr@C)>*B&g1hWPp6hVfjWzN4BI$u<8?CMm?#g=7Ips9U*x}ibUCSRf0);9>HhW3-g2JV*RNmpVxsEFahVIm6UlavD?t1k^ZgOU'

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
