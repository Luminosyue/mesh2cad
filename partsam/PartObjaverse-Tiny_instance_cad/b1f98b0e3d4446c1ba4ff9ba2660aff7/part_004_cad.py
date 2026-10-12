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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1f98b0e3d4446c1ba4ff9ba2660aff7/part_004.stl', 'relative_path': 'b1f98b0e3d4446c1ba4ff9ba2660aff7/part_004.stl', 'source_sha256': '055193f041dec09bdf4e215d240b4616702ed8f8f6f7e8cf56c0e5bed7c09c46', 'input_faces': 462, 'input_vertices': 285, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.2099677473306656, -0.14268025755882263, -0.33871203660964966], [0.368632048368454, 0.22771647572517395, 0.1493530422449112]]}
GEOMETRY_BASE85 = 'c$}r133yaRx`wM0b_fK40J7M?2q?%X1O!G*D~dC0B8$MCD>O^k2N*ULR9Zxgq97`ZEYh+I1_A^S2;_t{vPQw}s@QnNnen=Ba|OjYb?U9^bBfG;?lTjg|M}kj_*18rzv>i;^y-#crlwF|jYRQJ&mV7JPY4-RL`^X*d(xEA!?Gv08b9&DkVyA@`K9&wp8b0C8W<AO#EfRcvnLOm)U0E;*)1d5H)|PgHe$l0DU*hbA3R~w@NDUK88U8iw(CzGHDqG8`?-1R_HA2++g#T&{BZbR{Ho-3A>1KxEX&oz(3Cw=!=d~)3Vps<e#!HrqiUV;`w@Jxw0DX0BlxkD*Y|ntrFB2+_eHAmBY(U3l;4kxu2dw|DQNvxpdI}9+%YHoemM8lgWmT|%?;+`i+WR!2lD$)KT>Kwe%Q*7EUEvx*MF-&aeT+>Pb7BxaqqcRgX4|i$E@+j+PreYYmfOf?c+zR`HYlYd(xYK)+N@i;ACm*rG0z7v~RDM_U-jD?O5xj{dm!#{iQuO-g`=+_uP)TZ~A=)KU};g@LbVim*f3;&zxXC@na(kPX~OfPE7x;Ix+o8bUdKO*CH^k1b#$J_r?{+x9dv#c3o*dJ}Bdm_kB5!p7r|)?f-D%q~8~-(~p#vAHk1U`F7o!{#bQu+HdsvQU7>N`}k37ymp<Naanb){pi~hR6grv`hy>5y-fS>j#KqcJ(zazBh-VLxA-CDQ&*-PYk!&NTKmiR*8Vc%vi6s0-`ZcI`k7Ou)w%Yawb8=Te7pWlzE%I)7YkCoI#0a6^3Brxc+=uwzO`SpZ|@iL-0!|s`TZsY@)P*srQZbd?fqi%t^H#9b8(3B+g1$ZNAR7c`vUp)elhJ^`^EJCmnNPczwwWOd~sR%iBIYV+ILb@kCd8UM)~4GFyG#frvKJ{H2p7s_-JY4P2eZ2@!I>*v~TT4(@t8Z+F#asiK@zvSnFl)NA27D(e!^}6ZIbcAXsk>zGKy!y?@Pft^I5Izj<0<{~F)g*WsO?oi1&EMT%o3-t+#MZ|$#e+M+kSb_cv&5XfH_IrD$|xvRbRnwas98rR=zpY_K7=5R-Tj-ScN^ZPM;k#pbbET12Fw(%b6C%&v&;LjKHmG7L(+~GZ6=Px_I#mn2)^FX2BU!r`c&%u5Ee5Y{QT<OQ|TX@Ky?`&0mxL@-ke|~&Wk=H-R$`21!exh$MKel%0PEW1=i1o^MdaM3KbU!n@dgn&uYc*c&C-9>ms_|++T)4t}Z${rz^QrwPer&dyPwhMJ9`^QitotZ$e38$GD}O*|uYb<GjCEN)KeDRTKIun`R_qVt$CV%7dT^IN-}&K-t=>3`%OCRRi|>{19$1b)KiX~Pv)=qyn0v&ZAMdREuxNPDpD+40S?fK=%6IxJKk;jWKz{h-;MctNto|fUDL+=I`V-apol3m*OB_(+)qVm$oTtXC{pg(!9roHEaAB)IKaMZvs`=D@OdM3_UJo_@@ejtn<$Zqoqcz_A-yZbCb2_Z{{QKI({eJv$<%<TNOwRJRGw{ddo`3J?4gP$mzw)D_#w-lvH#zsTH!rPcZw}-)RKAm568GoFu4_Ej`}2Fw=lSzvos=JWwCWmvzGyIPkvD&K{x!-MR=(4rp7&X_vHH^y-|A2F+@MXK-#<9s@JGszjtGudEU%j9>EPgeMzmieIG@p#=RH4hms*!ZwOrNzAGdh*AI=K;(H8l8y?SmuDA(^Nu2+8eg`O+3{O#oZyu<6q;ul^Ew7*69u_yLy_2-M-_iyypW&P)cf&87yk1W1ww?98>)s^-mR$Xb|vFggSZ`GCQ&wyZEnf9%^GVNP+W!f+Q)nndxSAA9#7}upQJzr#ADhT9Tb!dF64oyF;IyCuK9cn-R=Z{|Y+PC@>pQ8L&n_z$Jx;4I4w<4YSvFcX)!m3;CCzb{4R{LSAZcY1E-D*FYpS#`b{{~e*+K=zRU!>~C_&MX%IG3pUH2#yykIYf^Y5Jd1!#gKq*Q)wA{lO2<Q}wTX=P&8%KHQD>QQ62lUcUX_!N20YgP*Y9JNRMiy%W{#SnnO}i#vkv9h2WD_}<Ze+<NcCbUW62NBfTT-qF7O-qF7O-qF7O-qF7O-qF7O-f_};spqar^XfZ#YtVN_zOT-gZ8zol{Rn=f%a&DHK0h|AmCCo<d9I$fUgGg#n*;6O$FjG?{p}<^9=zN07mVHO&rh6Je&o>w`TqQHVdGt1zL>i^Fs}W|kA9uEEzr+R=e>SJ$0dsV`LPYkj}?Df;Lmsd`u!#^f6Q_xFs=*uhX(Bl<PWI!l;=0Bb10DCRrw-gljF}9+sn-H>iNU<2Lk<Br~KH)sr&u;(f5aY^PaHt&naJ6`OfT--u*9b^(T^}e5aP`PeS|M$Eo>cyxMnqC_jEsjaU2O+>gEcXoC6Fetfg?V@K6|n)VmJ;N5qfkXkR}FHwH@E45z6-}^?Psv}ho#xGF5TPXSdd}qfIZ@-8fRd3oCJCz?Bs_M<;-%z6d9?kh<+K)F?`#E3LzxHGJqO+=h?I-4S@$S`8eXkz=e5w0I`*xih->P%%+jVPvt8SzCb{!huszc*jb)tQ{PGb1>x@+HFckSEjXnboOjc?7r_U-w1HZCsx{L#L3Pt*Pt=Mw%E=MuhsuhYJLuhae&=aTmAb4mBpx(6EHx(Ay6+vk$@?Q;p=zBiiot$U-%x6dV=Z=Xv#ze4c-X8fOn_czmyb-yycb-yz6Z=ZWQ-#YgaI^VkIXy3l)X#a|HPtT`)?&)@{dy(<2dy#41KKHb5pL=@Vtb3Hnx9(A<pZ2+@+p*6*op0T{jPE}Wdj)>$wzSsro113{A)}(GDMk$O{mM<6@=I&!zj7O$`TzQrTV}h~|L(8cWVh?Ok%88OGvEg3HE;vC5!wW91UEykg`2@G(Cgq9aBK7ixHX)K{ua)J+oCtZZQ(YA<W_Fniw;C@ga^X?(ci-T;XddMa3A<?^g8%%xEp#c+zq}HZ35p3--ccT-v)O=>%pDi4rpDt1KbX+4Yz~aqjli+@Ga=o@GWozZ3su;JJ81P9dK9lH*i<DCn34H8`q;v(ci#L;V{}54#V})hH!nj7J4;Y3$B6Ifu&vr*MRkx<P@|foC23YGvG3CIkW*>4z7SUf-At4&}MKYxC+_=t^!v@Tf<f1bTkuAhpVG);p%WTv<+MhP9r4Wgtmfjf?JB@o@q%)?(Ie|v@d!u+!r2z4ul85{m}k!KlmQB4}1^Y1HBvW0sjH*2LA!R3%wJ*3+{~G26u+D&`xj`{5!M*{5$w&v>kji+!1XLcZ6?6Z-H-xZ$~5W?Qj?L4!8^ad$cS3d$>E=6YdW8B6_kuQk%oQ;g%w~C-wSDmg}E}Rz|OfE5jAhrf@~LJQ{|}!)4L>a9KDNtp%sTA+!c8Rlt9A<3HT^Pd5g+ai1H5-FU){$K806kUSTC44w-=gFXsB1J8HkX*cG%@f0CB2YnXKf#;yl!E@l*=mK~)JPVx<&*!<b2+2zc$;;8l;N|d3=;QE9a2$OCj>BuvC*d{lI&?0)4&I1918;<1Md!n>!kf_r@Md@m`W(Ck&PAVvbKy<sJa`lQ3i>qs3cMD53SJAZMswiR@Je(Jyb@l4&W2aO%g|ZyEY@ZjA^CYi@<MbuybxZDz639ZUqs{Zi|{IR4ZI58fUbi#z+2Ic@K$&``YOB~-hpn0cfdQ*E$~h_AI*jH;ce(9cpIFDz5?gL>(RCFdiZ5@HT*KX1YHR)ffu1G;6?BY=rVX2Ya{uT8^5}7%#E_{L6Yi5MYKFz5w47;!Ij}^Xmz+6Tm!8I*MMuIb>Z4@J+wYt53Yk=4cCEdq8V^aI32wTPKT?YRpBadCA0!u2`-10fy==usDM-8%R+_ZpItdFl%7VVf11yd&!A;s8Is>YE5I@&zlT<ZWk~)Iy$Y5g`8=8d%aD8ly&9Gw`BSt$EJN}qXkA!_<OEs^mLd5Av^p$9^1EmnEJO0!Xn9zM<Tue&Scc?N)UD)S(X#Nb)Nv@J>R;*-v}`E3UnIYbRtzQgm*n+m<xp}zO3p*8g_8SM@;0<aD7oJy=cBbl$@4+-PPASqd7en#fz}Bn&mYO#(VC&;c_n!(njT7?Z<05lRYJ-0Q1U9YQYd+TN`4V77fPPDk{6>Xq2&22c_AumU7zQdeP@c)i|A$eGJD`6A^9hf+$TSwufspVm(XMIG1mAJD%bTApC$hyl4~z{5q<gvy$E0A8In&>Pe;*X@KN{({t0SOYKchJWC=AZ^{hzN@L6hH>VJu3%}f3OJtvZTL~;WCSS0t9<WJDQh~yrW{3-f3k=(PAFQ9)F$vrOlJo?`vc_v8y5dBCb&k)J)q3?_2nIrif^evG*qa>d}-w??&P4a2<BrLU9B+tWQ*1wqfK298A{g1E~l83r6Nyz^XONhyC>~Ui%S^!Ul???B;_rnjO4*VcI13duGfFDK=!4JbT-FU=}A~zmF3*m?0>F7RqI{W~-7k&Vq=Ef9sH@X-80{sfz3x5TFgYJXBfxklw;qTxd&?5K;`0s?|gXkl$)EImaK8((UXEHyB3CaIUNd6H$0RISok2>)8@VDrG_*?jEv;h7Z{u12-e+hr?#%Jhj=pI<=WcW4s&u$DshoO_<VQ@A&70!l7qW8li;nC=W@Mw4}Is+aH{|S8<{u4X_oe58XC!#TUB0L^_1Rf8MLmz_2!DG<r@ECX$`T#r%9)V7SN5I2HvZjX<l7|wKClQi&p}S#S_qzzm|0C2nEVTsv0`Ao<lu|SGpZ(L0<X24I+XDa4!~V|TkEi|LIn8a${II%Lx3cnQT_VN(PZr2~@}~phABWaehX'

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
