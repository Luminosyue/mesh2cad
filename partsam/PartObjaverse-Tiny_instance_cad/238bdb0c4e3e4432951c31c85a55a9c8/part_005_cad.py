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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/238bdb0c4e3e4432951c31c85a55a9c8/part_005.stl', 'relative_path': '238bdb0c4e3e4432951c31c85a55a9c8/part_005.stl', 'source_sha256': '7d2886998f2570fb94eb7f132305919e830f5a10c9f578c5647e161dacf52466', 'input_faces': 258, 'input_vertices': 218, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.41153597831726074, -0.4145633280277252, 0.00973561406135559], [0.39356690645217896, -0.13714170455932617, 0.4906608760356903]]}
GEOMETRY_BASE85 = 'c$}r0dvp}l9mgjmgaQd9G_8*c47QSlB0>@>MI{?hD1=B<h=2h%LZYZV@*qesx`Y6t-~$3ArsyJ&5?TvEp&~*zmViKL2oT<EmOpwpR0=uvfRe0j?{DUNXYRc_p3~FjobUO5_rq^z@4a(p?wvVgriVwwY35%)t?r|nQEluaDN2jeigOE!X3fYg95iR%!Z0ny;Pl6R&Eu0YGN*)T#oD6ynYo2C3gU<B@ek(>iyx@R=gloBD#)4h?A(Hxxx`23yj+;ec;O2<^K#kegrp(E2I|R)1NBn<fBfr4ZK%#V|7Y^+u?Gzw-&UR~aNo7V4I+2FpI~s;rOWk(XI*Fzxpr}t%&V@S6YI77(ngW<dd{_qs<UFfufF2A$ay{It~dLf7VGsB`%a0R*K_V!P|z&ayDyiX6*;fxTt8fN*r@;e5MvzNH@>+b@vB!3h+M0w@k#aHx&0F7_28Z!-`CM+Z^|3S__>3Rw2It1j>`FQz}-D=8(bf7^^D0MGq~R4Z_@Gg_Royp^+g|+c;MR<vpvyuGQYXwl5zZ~QiHn_w;RU~v`4gxT+^qvm^|ngxwr2KN3O-LX?Ehim{LdXiTL8EV|{qJBX?b^ZE)mY=SbWYl`r?VV??XS`FI98MoZjx_4Wa=UXPk3jf1zn#V>L`4l3v4pmIJAD(B-6Qjc-qJkWiLa^CkC+}k}(=HCr9$Dw<o<9T;=yS>BsoUj__{d>R2bv?VqiF^CH9Jv;|zS)WUV#=I(#F3+pJbbk?zqYr*iF>{-l(^pQ<_>W_>m8k2MQ-)CW4Oev{wmz+ufnbVD%|R?%6WfP&iku!-e2%Q*UM5nt@!}X+o^KiPL=a^hH$hqgrl7nZ(Y3E82^9#vq8L$JpP57#p_ECPB5>pOJN2NB%Z{1iIg}$U+#_`a(zODW4%W&XmR42KG~6bWA`>YabM)PM#tl~)gE->t{XEXu3x&nNo;4JW2D4+J5|oxsdC;<mGgFn93SoE+;{Pu{JZUbzsRlMRe7)D%}(5EkHURjJdKW=x0CZ_{maGk?(XQ>DshaP$~}61ixb!MEJyB*-P7#EeO+E@bmWmE9l5J*!$C)W<7tVzmqnI~^V}VrEO9=cy&ZQ*-0E*|yu_{kD%|R?!ma))-0H8&d4Cmd^%vYzp0`A7kKS>`FLK_V5Z>!pvlHj-R5@>F2uC|PcfC5gOrAfzTSac)H|~?TJ+I_?dtS-ho>vM-zf^9|H<{b>O6K;wGI?N8|1xp@1cG@Ix9%swsS@YyS2=Hg2uJ%>&fBkY-hP$y_H*tjsaY(~lUsg~+w(->);y89Jx^qA&l81P^8|eOw6&?iJkdM4wu;=|55!8`USH&Tdwr3)y}roYUSDKxuP@5+t@Xv^zTvZ__VD$Tb9)_;xxJ3a++IgyZm%QC@vU{l<lcw&Nx$oDzw8$||J@LdbwuU7Ju2txNC-zeIoDmY*QE;Ai#PbBd407MZ<Wvcw|<e^_lJK=obLnGdV7DEEFGWkyVQDn-ze96`=&Y8bFS8Fu~p4Z^_;8qftV$Z^_;8qzKG*To$5IcX-`C@V?F0;z2{negHt`{yx!aLfjpk=O@5JE<EC(Hd=zetgTk%;s>k8|0@u$L*NXE>52l*;z4O;=#d#HIzv-8F!h4R~eqNTj{k*KyThGffx1X0~Za*(8_15z;=eKIb`Olw^+!y+66Wi%-KPGYBPL=a^s+_k|<-DCC^=K#Odh5ToiQ~_oyS-a_?ltBS-jnFx?7S#(yeHvY54Ic<>)ls^=OoVGtAKm&X=^e#f4_8o>uHf&@0Y-}yKkKk>jO>wPKlh?Tm0S&r^I^qp~w>=x86r_KJdjeV!f~E^<yHp-j9L19!NPW*1M*kJS1}KeI2+bsgu#~K=fC~4UYGCoO`0TOWc(_*sPB|YQ8^vv~7vVJ+ZrNo+-U8{e0QV)XFGLBX!l{w7eYQRVhLG<L>;bbXLlL_o{U0|NW|T8*4)?(;wi!N6ur)W_lhz4Y`JC3)5Ek?~os28p1RjJ{Wli({`ryOpBP7Fuey~kGvi=lpkSAW_lQ&g#2r!2bhMz2O)cyUSWD2z5w|(reda2_<ZD-m~xn2hChcqi|JXW7vXN?Qhawcd?oT~<d5JRk;5<z!r`5e$s>@%kvqd9kvk)If&U1(3vyR@H{`C!-QiKl-I1f2dNK86iiIfmfJY-oqn`39rV~sp5apBb<H#qGo8f;&Zboi`HzGG7AA=u3K8Adh=`j2&_z`59llwGtUXt%ern$FQGv^=q7s!Q7Z{l3dM_vj45P2o?M)+sQ<a>}eB5#6!j!bR%l<5F|cPG=A_^y}9hx{Qv>r63BiSRh&MC1YRpCAuF{w4gU$d5BU%9H}X7kLK$?Ky~Y20R5h134Mq7n!^dax!ufyf-pk%lByJ^-TUVWV#0L*39dW{4V5Yn8q;WG7Uu@4Sxpt4yGUD-^u$S4@DjWe++pHaxQ!(auL(3OmD$IKz<9^3;z?c7ug3tggl$6oM{exDKec`I=}T0<vP?<qHZa26}%3)4)v62uF#zM3q<)7cs24T$nP^PgD;0yBNLy;G#7a}KIb#N!BhZWfqal@H&X*dc^7Jai@Fua8{oT;ccGs0&zVLr{Q{z#iZRN<_{~P11W!dyMLp&Fm|RT#A<Aj!!({YpF7ngxG~_hYQ;ugE$&>(59)&(n#dzc+Pl1m@9))_!v`)}^Q2~D&xdOQcqRj6%TX0@?B3HrRMy^6$3SXev^JIZAX5%n6cVSEi!Bde_QN!0c@+aWqke@()0irw|o`sx+-<%F#fK2n5?rC4b_af8$q<iTB_&($^rV^%g@OP2dA^#Dg{IO=vJ=!1bhJTE_8+il#UE~eOE8r!XJwHo?b2}dAus6<q5_}Z$DAe$M1Nl?%@yJghzXVavflo!Air>tEmmt%1v>*N3kG@f+Jp|o<Cu-)sl=d+h@QKJ1QImnOqW<rIZ%3v*1g$-r;hT`@-brg)HheyEHu5xhG4ijN1~N^6{|0#iavnSz`9Y@p@xA-;9m;2!&M}>apFw^ezmo|ci=2u4AT$=oqkG7mnt3m{6Kn)Tc@lgq@+9Qh@M)TTpP^h1FGem$u7s~bu0*E$G0pROjA=dCCip60tjX8FS0S%KehprXO#4{c*OtLckQXy8WLgV<2YD^>Hi$Cc<B)#}QLcu+gItZg9KH~FIWoVGrfcT?lGbXv&klyCA*Z2+@6pMhgr_5CriXQk3;&`20%HGpj18~&A41e`%8x_hHwUo|j`eVqnckW9ylkV~$+&rk(GExZ55$i5$^'

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
