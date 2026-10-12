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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/65c6ffa083c6496eb84a0aa3c48d63ad/part_004.stl', 'relative_path': '65c6ffa083c6496eb84a0aa3c48d63ad/part_004.stl', 'source_sha256': '34613b0f11c7d710c3cf9bb7f8bb129ad4350c26599a2338dd3c894de2dadbe6', 'input_faces': 366, 'input_vertices': 263, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.24849122762680054, -0.4298453629016876, -0.3590067923069], [0.30320489406585693, -0.14085471630096436, -0.03352455049753189]]}
GEOMETRY_BASE85 = 'c$}r033L<H9*3uevhS3AOF>y=lSLE+i72S7g$F1okV1=q2v`<HL`FeSKv5K=A`(CfvWS4Pwh(AbOPaPxC@qi8h{9741UF=pmpk(f%uMe)=biU*&i{Ph{Lbyo&7J>bnx?V6iWQGm^hb<RIBiFA(^`rms+<z7OiM_dGImtL<W>_VO^;A2X}Ne9{IKt!KCwe0lxfP0Ch-ZAM<q7t<Y>})^g~TrIGT)}m^dXdZo-I(iSY>{?-4hCazZ$tJSJ{ZLio68+YaqoINCL9;h5?8A0K7HOHdc(=5-Z}DpjyQOn0Q?@P1RSl)Qda9J_wLEzOk$k7Sv1&+w3zhjyRz%5pU|F4LU5D{R(s_vz$pS?*c(@gd9eu9>Lki{pK=TunTYVb0Z#_4Iu9-#%F$`mL*Ve7A%7+VPNiIkH^Yv@6~6ywO9o+<D{M99iyoZMbE;GxE|AZG6v|Tv_gFS<f=wHS0Ak_v~qzE6r0XS;nhrWu@~Qxqbf7)|Elo`i<Pae%I^=gR=cGa{K<c7M={q_TR|u`yXmJKOj55Ms7d9&da?5vi>phBK`Axt$?gQjojX!p?$agvi>)6d;dE<SN!Jd$hrO_zt;a7x)jKA=h;?T?pRXAE6bf{nrE4F<;N=eJY^%ZWqIgYmrQf+{`!R8=P4($Wx2X%<RQyC3zzBF*RAzFS*}iBl3~t66T0f}0~cd+WVvhp#dOQ_zH&;xzSjPbBg+-nvzGCml<`{bDc?O;mWQrhPqXBMuj<!Di3PdReA0Hyc;h;9MkVFSa!2A?%XnpCq;&o}xov)>^t(aX`i<PaerKP$LD~KoxqW|>r}qS8`)}m-{Z}rz0<!aK<o5IHtXw}J>mMU8(m$up`DOiS<o5nlLtekE|Bbvz|JO;eTwm&dB)#AEZ7I~|IhEu!=gI?f^n6x%pE-B_*iy?qB}e9%bI<M!?K<)dS)FUi-|M91%93??=G>96O200md-%<{y5)-2pYEOSTXN5VhxI<ckZH+{ep7RT`s=>2QJ?3VU##yN<enp^^z~%LdS$u0%P*Pc+*!Cse_aD-WXp1Q!?Z(|eC<>%SCw~tvfMLmYlb;@pL6JWgGD*A+<o?|bjv!ge5Jo{l#R=k<?idJ(=7W?yMz9|G`D7+ELShzYZ>o~`$E4j`#;E&<*s#`4w`diQg!{jB%aTc<!aPG%lJF@--S2wr1|-7mhqlJ-v?#$8@YXcH9j^dTfdRp*YDhz7Le_ak=yr2$$v5++kYds@4xfgV}9BBHFEp;RULEuvi>o0d;h4H9`Vci)5z`psr*{UFYA9JFVg>&%2@Bq2RG^YfZ+wQ+`X`$-p^4Dyt3SV+mU6?T@h{d>&0IqTb75C8)uqx&ntiFef#UJY+0^U?RLnL@7k*O|Ga#kEO*a*A;Xf7AE?jYWloMPcVz8Nx9o%OqTc`Ry1BAkEsU{_U-`0reK}|6%5q0WN}4%WvTo|{Z-acfvOE-%Xc=!@N6MKKxw72ZDBdzYbn9kNHouYE=T{rQ8I-Nx$nEP_uaynT_Q%NW`=bn58<6e4k=yrQDX(95_Va7x_VXL+9TAZAkCEH^M@{E`W9v^NxA&*B;|9O1|Bc+<|LWxBmg_6jaA-hVf3J6r%5wLZ*Y*A!nJ>*l(c`krxo6y1Eq5lr<(1`*z^+Wo^LB9R<1aMLmgSCx)hy#ZlPl=gSDypfvfSNl<{@()TAHo*|Mo6EX`ZfF#(SQetzTaYH~3_^df~$i%R2kF*5_IEn@^Uz;(J@hySg0Hudi86b7Z+=ZVl^r<34qyO^z&guPJ94uf824o!`jq^LwUvgR=D-xqbc0%xOW{{up_Y{b}7QDBJ%#xo!WI0T%+Y^K0Zq&hMh#0a^bTxxIfJ&%Pg!^{0{B`_nmWMnKm8MqZ@<U!4>%Uq_BUKkNJ7u2a4&cg1$l`>KDOG!Jb*on@IPy@8%LJ$YD`yHAd?jCW`Kp`Z87UA?m0>HRy?oI6UU>hI?_Rj({pXQW!j-+BM<x6CWc)g9|B<K6o@OXoLo`~1#Z#iZ*ua{KyS5yykF{V{U;{<x;51*Q8>Zr^|B;{8F(d5pfO_h(v5{eJrA3Tf`DxH`+6dm?>7*?1$rGd`hK(6Z0HlMc&rSM#;ncvnGvOMd6`*YbWxwDY+1%@f+bjp)DAoU8e*j%z<3J9wKpcYVJ5nD)Ht#f|3NGrgSlxlDDpNw&<>zOR12NV>JkGLNyItJex-xijWI%XsGp8};k1U#LKu+vZo69oK%J_LLk_Aj|FR^mJ3T_an~&J{Q_@`|DNDEYbGSJz;*nEVu8QGUAf{KJ|UiBeLAS|H_cd+V2@kQhGp|FBq3<S?BLPwcmS`<a_+G+|~S#1D5>aRPA$!r+unVmb<&Xkzsk>c_j~8`sbVH_5Ak=TA#R=Uf5>NooQ~ZPn=61+iV%%_@;h7mburNbH}>w`o4FXwZ@#^>F1kS1+v_8ZR=`t?y3K^{`ZrCTMA@(k@>sop94Kjn-|D(`#L?vx9Rt-tZ7GOx&8Gz*BsUMOBo!WFUyPUTVzN5@0i}^M`XDt<lkv|-q^>r^Q6q$6p-c4in*zl+__%={dhrDzbp^AY8<rWg9@}`rS>MDELVpu&akX==GeP^5^MRE<;4asTw7mRQACwiqLtBcrmt8;C>{poU$KmB|6hH@(yl{?|Mx4F%i%TrGhD}@I6e-q;DW#6f+z439G`^0;evnQf~WD*9EadlT<{t$cm_Yi@el9@E_e$UJcpm-_(ymf7mSF|UGO~ld5(XE#c;tWT=0^j`z4NlfhBOk;<(^NMfZywUx1Ogpn?njr0D(=$Nz$VE4mBb#0AgdXF2{JUdILh!Uey>zvK8@_$My-J1%$%-xsbxxQ;>(E_e_>60Y2E`6%IDcog^IS(NZYl<;(T5YGr#TDUU9l^?F0aOJ^lJP$8`hw;PwTmekO_roA1`~XbD#h5~}Jm`mocrH8&3-Nt06&B)!%$v$<7q58(Ovg9i>nY*M@F1Rye@+Qs4L$g3+)WApj1vAS4B(&QpTK?iCwLM}#gp*ma6i5rUjc*o3VbCzfUm??QNq{2G<*%dmJ+@WX5j1aFDT&~VJ0qk7~hC*ri5>S+4xqt9cJT#IruklC(OZj;=5r!z8l{Q^YFcR3iRVC_#WkM&+Vav?}A70UHA^@!@q{xpbr=H;$Oipp%)j-!oS2f!43E(yfP)cB3zGG#LL5EygXhOevX&LOT*Q8X}lzK<0bJZ_!%CB7lWVT#qbFD2_AtfFiE-l5FQDa<B@oAxB@SZmw+qr5_l=N3NMA1fot$GcsaNhFNarv>+lMACHMti39kY-;#KfyxEYVetHUjLb-bo>_d2Ob39k*e<F)a+%H3<GE+xD^+=<u69dI}9z#GE7ctgAqOu-xBF>ntagExS?@CJB2xC5_;*HP|XOLZvWwcs|q7G6WSdtKF_gja)K;??k~a1$<A8Lx^zKnZULE8^|&Hn2S225$|^;;r$Pur%HhZw^c1&GBY13U7utfyMA9_`NU!zZbs;D)>EkV;G4y#+$<8cvJj7SOUKfZvji;E$~*b4BiUAAC|-K$J@dRcw4+Ztc176JHRS<2mB!zjX#8Ug4OX(cxPA>?~FeJYvYgLPFNRr;@x0<yc_;Fbl{KUJzzt;2mS<Xgg=3IhcS3}{4v-7e++*V*25pgyTUqnSG)_Xg?GUphBfeq@s6+>-VuKgR>cJ$z(<B_Zn#`<4lej6?!t#t!k>dGF8DhB96pp1{tSE#7km|e1|Lib9|&K;1*hQy@d1?Z{%|TT_%hxf{|6;}5S)$+&cFxZPgBB&z?rz<EPM$5EG2vxd;=GpjSs^|P{QNjTe#pnJPsd42~U9U;DQVA1pIkQ_*nQZF1QFEi@!h#e-VCw3x0^dh)<-1zXX@yf*<2A;gc!hQ{XaOa49|oPo#uTf*;|6i}6YL1WNdL_&zT99zGr)M+qMT7vh5R@iF*lN_aec8yB353y#F&@mNZDKj^~y;eFw7yf5AdK8N?gd&8l4Z@d?L2JeOUgoE*(_)~Bo{uKTs9Dv96iinIZ_MiTh_U=Q~Zf@p(thN87_0L1*pBx>Y>&_pGVtYl2`&jtq7pXPTQ{qmn{2N<8L@N'

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
