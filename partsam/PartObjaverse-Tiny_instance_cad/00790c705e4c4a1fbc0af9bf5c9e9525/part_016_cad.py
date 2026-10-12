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

PART_NAME = 'part_016'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/00790c705e4c4a1fbc0af9bf5c9e9525/part_016.stl', 'relative_path': '00790c705e4c4a1fbc0af9bf5c9e9525/part_016.stl', 'source_sha256': '158fc4643dc5abb0b716c03c055494e3904e94bfea320c633f993eafb5ece406', 'input_faces': 144, 'input_vertices': 124, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15800262987613678, -0.20833466947078705, 0.15535062551498413], [-0.14960265159606934, -0.19877490401268005, 0.16163191199302673]]}
GEOMETRY_BASE85 = 'c$}q}3shBA8pk&m1R)173DQW8nj#NzL{v18<0Z6|#|0-q5;#}6$eYWBL6mSE%|{P=IF7l>%1e)N(s9TcXI0jUQ`a8$ux3)ztUOXn#niMSmupcoob&%%oLRNjtm(SW`v3f|k8gkb+xza#!Lh(UAVT0XMy$LNFi#pLgz*d$5u(-QX{lc7YEEi!ukaJ$rf+<%>gL?ra~zBOM5}0zt#CCj^~BDSV$&*9V-uy=%0^F%$JtQc=&5iS{#<8WvunU_u5!9v1OJ~mB{?Ngni`iVbx8l`C&VbFVdnmBqn3S9ZyV};e(L^=0hM1*HGSzG`1<A))7OLH%VqFI%{0?jv!<KAayj1gwZ|N$ue41={to!kDfq%pzc>Knt{7?h+W8dI_qySW{iBd)JAE7S$m8-6zY)H?1@UTVG~#zAn7)4Y(gE}5P6nF3^auFb8u+4Q2<mB|KMKBj)E{|fz!%*YO<yjxAx~dC=35P4oDt|-FMTZ?eOO(OzGc8y`_oW=GJJ7g9Ojh_Up-QXaSLNm&%P6==j?YrGf($u%-0{jzPQiyz0vTs{LfJ5;cwvA--!Hw`4n|3Uz@(#83q6KJgiIS2GmmyUwtJP{eNe@>3hTB%e!(=XU{tHfBkUy_Jhcud(O-+I>O=4dC&BvFVAA!`Y`0rei!rlW3TCJ`Jw1@#XG3qamMuJ1V8jM_a)QUD!xGeH~;N3|37gb#&v&={#5+{e{7jqrxN-o`X2#bSy7Jqv$tU#weJz{QxM<w7}jyuW#8a&^_E!d^ZxHF<LbvJz#j+y>b&GVGqH{v`+S4vB{Jb_3Gg-VF3jsh6vo~1t;JU*%u6kRucz<CewGoh1%6}k)eSx9XT(M1S^2o>D_z$hfB9Fw!TUrl%z-}~zJ6*O{Ak2Wz6-v=`$ryuc#(G2l3(t?x_A%wq7N~fkmn<OU$h-(EcqoF@jv>?gNScLyx97=>C4)B`2GE6yyENe4gQ{b?^h6?PyfhT%(oly-dlPs^~iar(a-*qKFjyI9eLEd=oi*w|L@&_{4eXsf3;30^EA-!ZNNDe@+{_Cb^`mS$&GX1)}7dgH+^RMQu`|8DY=6E{N5+<o9{&Zx$xz+^w|e}H@-*G(BoJa&R4z!Uq5vW^KEa#zM6CyeS7pM`pI$i)8~=@0r<k%ih2qVFJ^pXsYlPd06z%6daMQUFW~%9vyNECRXQ)i-+LJA`!^5vzYXV@x(dG9*$jWlx2V&8*pgqoh4adL{t)V6o!SkTuz!-_Yb{NPe;ax9z7OGZT*Z#_P+9i@=F59W&27SZHNKC2X291=;HzD)Ax}^{_CwNN5&tg@{?R+J?m1of9))&e-8Zemx|ckMb71d_7?<~~da#4%zzgud<o$by{<NpDUO^j>=kL4WcXcA({~ny%F4Uujc@fY1S3S8F<Jz~QpXctyy%T^sm7z~yzO@M$_c_FiD;tnMY7_EQVE=0`t;4){uj%7)FNnUi=tKHu)Y*!7$$l5|teTC!ZN_~e+t$D@*n)B0h?nylQP1^{ApRiEVeOxF@Oe)uv(~`>x)%GYbQ{JU%X9m3HRk(<19`@*M*N;C#6SEv`c{kcUz{nyyiPxX`M&ue`dM6r{g%}Uzw80z|Dn)wUr1|KBL2ccjQh}2=yUHz^tlJV?zaSWzTbv(;Lv>dHBX|>v6z>4<~;Q0_|q6SNJT&Mvn=O{^06D^zLkk_lXoD`Y3v_0(vCXMHDSH(Za^QhZ^pR8{)G4sJm^Dws%77*iOb+$n1TM+{26{E$Nee=`7>4cB^Bt;i}3Y->_q+|{GOwXo(lhC%*$)5!o1#{Y_0z|^SCBk_N{VTIqJ_$vaE~n;@tLjC8D0?&!Ydko$%KsTK0)Nrxf|q8Gm3S{NTm#zmK=9qnM0%?csRKzSUNjp#F?F_*=2Bv^|TE=X@;k9C(Jm$I@5f>kGGHUI9hubJ7IFKffLIOf1}=;jp}2?0z+Q;5ZQG6Fl&CQRy7?YGIhh=c@kvt3`Fn|MqH;@~dAhej|)mAR!|77(9Y{4S59lT0RDcP=}C1$bnQr4kY_g{mFjh0BR^XfE-4>jvPjgq)OySatw7QIfk4{%_XOjbEv-~=a37iCFBBfF}0jrOfID^C6|(&)GD%*T*=4aI%)&i&}MQS*-c$Rc9UDF?c`Q+8+9eQjl7)td-8H}6Sbb)M6RV)lWWP#s1@X8<R#QH@)Gi5>LT)DauM}*auInU)j?iJ&Z90M=aJ`Ar;+EAlc|a1WO6+9CUQJ^9Ca*t9C-{imOO?$o|-@&PmZJhmK;Y;qE00zk*82^CQl*HqRQl1<k{3)$g|0I>aAouIg5H5Ig31(I*&Y;oJpNS&Ln40)5#g+H0lg;8aahJnVdqNM4d>UM4mvskvxGMO}&8}O&&#!AR9V@Jc>M$dM$Y*`FcJE52uEZhm(V;f#hKFP^uq!DA`60Alt}6)G%@oIh-0v4kt%ZW5`kD(bQD(X!3Mw4tY8`n_585Cg)R&$@%0$YALypd<WG@zJsh#E6EDk#mC?pY8}~7H@Sw~NNpuIl0DQmvWMJ4T~2l^@Uunu|I(lKe)_291vK~%egFNF)@yt4PnHcN`tcHXEEr<mX|{oX#$kEP*kR&7C34gZ'

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
