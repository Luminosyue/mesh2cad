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

PART_NAME = 'part_018'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8da95b178bc641d892f296e42c0ed8a0/part_018.stl', 'relative_path': '8da95b178bc641d892f296e42c0ed8a0/part_018.stl', 'source_sha256': '6d4e61dd424abbc42e1772f68efdde126459f921d7fdb6b3d009055a94264374', 'input_faces': 288, 'input_vertices': 180, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.34759432077407837, 0.1203080266714096, -0.3073991537094116], [0.09256511926651001, 0.47584646940231323, 0.3066805303096771]]}
GEOMETRY_BASE85 = 'c$}q~3sh9q8pjWy=q2Ca3rq)J_&~)(Bo#dhf=Vh<hzRD8;tK@=!Z02OQB*8cKr9p)Nih|HFkh+72#S^XA~P(s>2Yt})NVIjsoAo7_V@jdo$0aGUH7uqxBkERv1gw>d-nNe#E@Wz7A_M1xJwUbrw=!Flq6AYBo`?qCNX)*{FtPnaS5q*QU~(lN6UigVbek)?4%Uw6^{imN%IpuMjJfFF7);AG<YnGPfSjXj++;sxFAOO!02U3F{)2m9GwuOJ{~aK*UQr|VxXrX-S9vDIH^mJe;IexES6;7@6>p)ru>l=W}UZa{)JEWQ+6B4zP5<{_un5EX^HDcUhz+{ke6N^MdPmaByT!bTT9;SLz+kF*qywgt3w_6vYRxI@_H8@Kir3XV-<~;KkC5a(^J^bJxk-|9**qY2iNMaD+S*Bn0$BV(=_i1|1)}Tg_m*%ouS`{e9iu5=QB3GQ#1RPIsAB%Bc-Kv4g1pV_2hplJZIK>6a13&bF|K5Ci2GfC1>gR#nad~_iZG9Y^m+OHFY7cWZq}*bEs19t(tcXucYg^w;^xolg#f+_mua{I&bU?F9p3v*I#N!UMh;R**9hM-OIH9x392we5+FLt(w0wg{~_vx<lS@*{x1Lk6d<}{hDrd`t@ku1g{+Qr}fAKZ}Rv;Bi=8kvu3^D!rn6M4(+S#^bN0PRX)$(W-YB#^M-8rfZnuDDbdQ_^(uQ0Z(5J$O`5N@qxDGNULkM1m&@lNp%ty?vA@q=`RZS^9?Oxl?Ct&Nv6OkH-mLcy>@7bY;PtP4m)GBEGMxv>?}G-j&Kq3VD^Ar7^!uMpJWoK``{XaB(0FO($xHOSQIi^JT;&4tmi6PvTQ(PdOy1wWUhn06_Lf6~`J861x=8b7H8=5noqW=)^Rni1CZ42pzH@>6m=mAUWBEMwjX(H=#TAsB>e<VopYb`#<MS5kb&l`HH8$s88vezHv=6Co+TPcZjpU^OsaAhqXx^xK+!xa2dh(|7MK<SCxpjiPb&#vg`P95|Fni_KKspb~iVZye=zShv-^}*~yx|ypQ3l_SK^Z(x>x<lH<`(n(@K(*=U&Ql=rLylAY;*n}`~JZ;=U;g-p8cI8JWoIpuLs_67e1{W@549qc^~}q_&h7|eE#7L0qhkwKVFY#FpuwE!rtV<>(RU`dnxWAucyI_=c$^*kDtCl=k2ktW-lG6=lr%muYcDGI?vLC`F#H14dw9dre37^zHnlnll}qu)EP8h^TxI8EjLHecq!|L4`}>@0Uy%y&)>aZ)_LR4>}C1-1sd;`PTtgI#CaM&al}Vvoi}u2FYoRD5skl|%=5&@u^-xl$HQ9_*jo$R^Z3$bJWpCVd1*>6_g{EZI(wxmo$h0$>BjqXzg(-lM34QP>HgQe1>Ty{>N3rDxPiyFyh+~j_jxp4^O7Tbxz}?vUa5J&{WWqIukYxy=gm5Afw!z4&Fk{{C-=W0U-I~_-|~2P3%s)a62HF5Kk)m1tH&qg+YjRB!%Mf>Te3QFpF8(CkIy#p_+f|nyunMW*~`Cd=YBcPj=cPpKlhny?iRDoTQtABHT4x`;CJ--uY6L#{?29^uX(8nK4vBNp|EK3mh`A*dYm6$ZT>Sqz^|I-zZ*zizIc><^DP?x2X8(}<E27RUeA|puG3@mLn*HVkADzn>))GIN7v12;Lj(mAMUp&ZymSil-?`#_iJgM*f03?cwVj4dz0oLt>At&`z!L+nGboMEjiq;;FVDLv~a%u!W-m`v2WRafB1I=&)@eE`*j_w^xmrZ6BXQ-7VRW&Xg<&VbMzVROYkPmyBG0wPnGg`^mDB*J@$Lh=e536v5x2IbdP<C!utSk)%-p;-iO}l{JIj}KW(!Q@K()ZACza}c>Jv<_D}ZXbF2B=?Bz{u`JA_!%6{TG?w?hSeC{>x&tB<$oY!x1W`AZf^*1HVhd#eGZ>nc+JTZ{&Z>jj+De`k1x$m7EM&mVajbtzP?ZbU#=T-8?pFSrqjla%)72b3YzUB<~;VseZkKN?Hu)Ko$p5_h5*&FwmxF3W^@cf-TsL#p~TX;OY)tSB3ypH=y(hT-9mhpJMPq|OR8)ve&rd;6fI}c9teVpHd`=Cb(_dR&IfW7kC63(v=upcv%9$OB7%6%1H8p~dO@&eD7{hgV9A993W&%84J9D$c+!h5dg&yjL7c}qa6EA)88V*Xr%S0=Hy{5qXKr|xFa_bkc&1obz`SjXoXUV)bz_jBJn_bhvF7ydrxkjDKTUK+_>d1(QEe$IX8IF0XBPyJ2#xHIje<|PArIp`7h1BX=h4~OvgH1B;p9$taB?9S(YFlf%Z<h4E)@DJ{jzxSUV<i2;?g?-x`_B}VeZT>TVc=p?rdw)1aKIo)vKfJPwy_4S!8-IV>F3PB^Yvh0J$)6wY4sX)?(msQITUYjr50p{%>qW0i`R;Hn&(n4%rK21B&}#NYfu(eQLih1{Tr+FPdqwP^Jk*}oGwU6mw;{HK&qK29Is>A%Q5tviJf(3wPwkJzlyy!#KF`GS$m_`~_Y-XA34K&R{&p<AE@ejxeqGj<8_6$q<n_C)<@G0Lucr0qM%vEfdn|*-fA%A<=gL&R?j@gOT7SfP_HT6Nbt+Da=-f1Y&E6}5_E%~hn?}AmmHj@$L7v~gfF8G6%KqUYe&3z8Zl&`yp@~0#kM^O@GwF0q8TqIHe!nWl;(NgCDta8am&Z>H;`13%bA+zj(1Z7(v7pWzV)NITA;XH3rFJT+^*6~yS{SYS(+vGWk{;)u|7m84_kZ=LnWubx|KC5&l&Wjkq1H~M2`sV<yc4_|`6hTbxE#3)EOHOH9K0X74=nNkct5xjSp^nZ1Fi&DBM*W_z74Jh??t`^7Fh}|#p~IN+zs9fu0WQ9%dx%+WF@!~*AqNOtx0MnBGbSt)k;w-0VOyNnGB8tFGem0F9ydWUjoO2Uqr3|zX(o634TSb*N~f$E5Mt<TaYh-w}9V33Eqxe4qlG6Zbu1z9VNIBnF1~ZZ$hpFZvwxH60D#Ezl=-(Cn95!3E)`p5@Z}W4*R$SC3q1^@KR(vI3D}B6eV~WG8McGoTOH|T7lps@L08;R%?`6ekj4-$l+jb@HnI|cpO+pjt0x%0JWwfCn86K$0B`@qrpDl5lCOKFRncTCD;ok_$lNl@F={tr%-}NN__rBPCz~lo&X+?^aGCv&qWE2MhT8VdV{^OFEJ>=FQ5cJkCegBgXbUvz;nQ}bo(ec6d8h?3Jw8JMot84dp#K$2%Zdn1|>KfnGVhdXCjlpB2&R4Ujb)=v!vhd=PZ=qwaE40wcrgX!5fjUfj5E+kek5;;H}6l;H}_o$Tz^-z$M7-;1X~#@^x@AxCmJYE&}HxH-YoPdB|76dEi`>;B_d$IY<SZ1I|Fc4Ay!|1~Ltt0bYfi1YQLWMhOl=jsc6D01g8CBgcdN!4b&0;7H^=<XrGP@O)%6cs_U`G6uX5ya4$Ecmddmd>(8BM<M5cqrkI~v%s^#&q=@CKhL2APe+D;MNS5bd<HBs8$2Dn2AK&KnFSWP7A$fDcnw&aX9LzEa-(i-8+Gg7h}S2wK=*nJupc6~>h@<V_D|$Cu*eeK-j?Y0zXb1($YQX_BHepeq<en_M<VmVk>GG-9ylEQEHW274Y?Yb3l_N!EHVcyG6O7f6?ipx8ZsCxG6)=wYs^Fmo}pXE43yw0$RMytfAAD=7%~E^-49{NaBw)T7lxbxZlP97wOXMBw^6G-@(E;1a38gLsns1NxC`=0a2IfAWH)eUa93nca96M^(g1b^_eKfstJWZ-C(;1+1P?{_1P=udLv{mq!}^Ay1P?*>0uKQXM)m;@1`kwg0MY~52kZfMM|KCdRjZ#Q{*l8a*bV6pcE@-(lwfCM7qBz9BeFBNBe(-fa3^F}a3`<}(iQ9i?t$zL7TF&xvK_bw*a`UrSY%7E6WAWv0&EYqllaF$t=338upP#<MhSLQD<s&?-o@ds{%ilYAB85@|40AtpK1HgPW>}?sB=C3M`%cJOL1Lw(f0Jk_L?{i(tiNE>*Qt'

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
