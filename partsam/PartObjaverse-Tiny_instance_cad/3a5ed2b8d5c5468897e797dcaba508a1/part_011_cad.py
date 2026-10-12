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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3a5ed2b8d5c5468897e797dcaba508a1/part_011.stl', 'relative_path': '3a5ed2b8d5c5468897e797dcaba508a1/part_011.stl', 'source_sha256': 'da91a4f0cd2d4f9a4c5a3358cddedd79a071a2b16ec68f14e1b6f915fe84c641', 'input_faces': 406, 'input_vertices': 237, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.13831642270088196, -0.2674086093902588, 0.1663578301668167], [0.17735664546489716, -0.08428721129894257, 0.19451886415481567]]}
GEOMETRY_BASE85 = 'c$}r0d6X2@6~+s27g1r{7?&0!0|pfZMR1`tipU_0BB;3a2m>O>G6T3^NCA!z6+{7zBGPOsB4Q9(bikUGO<)jLG)%jJqS60ylAMH-ce{SK^6GWxoSdXN_uTJ({k`|TdhgY%nm&{iw>Yf83qNOjW2gVKVg1RTC(+U?@Ftd(j~_9ltm1;vV;^qjosi|_qj^rhfj5@i-prfmO)45%RxzZ!s7IpcieZ-(bxITs8&f{Myma(EW6Fn?3E!)9R7IKLEAA^DTW0DG7kBB_Dbb~4r^Ig)|KsNvV<9<sO?6L`6C18-eBb1ByL3ZOi}#d&WA$d6Pq*H?MfjAX_mxNQ)$GXfsp7@ieu6_C;(S?ptMER2;(@Qialf9kD?6_8e><%vJI-0_vb;aKXG2~-)n<#$Xa3we^aG!IvSXI_4!#}wInbveAMYPHGNum}*M>eFz4A%)$qxqB*z=j`UR`hV(R|j<j_Gwi(~drxPxPtf<HG)r`bTU&mG_zkY_sPrS@m-0b6JaUessNDUe~K{rp8{c<i)G%^YPw-C0lIXXB|CP4<Eb~>ixa@YwYz6xL%j{^?D22)W)t?=ilL@^@5M)!O<(9LhpCKBjmfEvD=<c<#io{#!>Y#J-mPDyI4QTYpZwK^RK+0d~RD_p7l-APjKs!T6<m8zssxt^!<&s_P*8q=JLAVl-GTmcJ#{YeoGX6QfuE|3D(!;Gpw)jdf(}~r)Qj6XRnu@GdVo_P<dT1-_b`rdVl_Pb+LJ4o-?nc>hj%>%DeZY^6q^XY?xVR@6Tvm9A4KYC|*!!-!Ey-s~nzlNqN1GQm$Tk)qnbNoxQ%gZ<UYEE1id_Kh)Xlm3DYtuSkDt^Ll&UbiI^!p9{*n&jsako(t1o4Ewo$R$aEAkKd}#$7fz{*<kbjISZ<@J{`UCfvc}PabsRRysHnI-d&sZ>FAYDtA4}cu%Fi&vp$pW?yI-?L}gRfPr~7Y-p_5!%P;P^PIwRAzkYf692k|1^{;%;yML_zNZ&Z2Dj)Bich*|F{~%En>euxR=f7!oUf!G6sln#Gn!(}xJ9_0aa~=J#Syg%U@HzURTR8u&9zH<t9~<7s!P#GCefoc$Tc3~j9_<j*Cl4LW`b;@`<ujAwdhha;8}sRv&(Y5tlwHT9tA`KJXSVN(?Q^eSczr%TNDYeV)9mw1o48*0f7;Op?DHHwysP&z;XV%>z3zV>y}#)5ke}4DKDIyMleZPt#P%V)_semc^6|+V*2VUJru6$z|LqB}^TFlyd{934`OMh);PQd1fB)pFyn6T?{b|8F+5O<^;q`n-O+6GlAJUbn`h2|i%bhWOl5@j%^m?9Teva$C8^ZI%)$2KvqhAu9GbvZk`4gbeoa=?}iJU*t{&e_gf5K-tm!ka!ujf_T(fgcNu3pbESD)k@3mm<kZ@NEI`&%{G`%}*cm)G+_dEK`uN3Xoz@5<|bcJ<1;dfn$qw|{s&A5yQk5BZnc#qKZVqvzwL#d-Pk@fERt(zSoD&DT%x&_%KPG}7zy)agHZ{yP09cOF%pub*V+9-H#<dM@Skug`0z|6uaL_wx1QJ@HNK+=zJ2v9!~F^n7>w|7^}Xv3`=_`<I?G(f)DxX#c?LIg@hq%18S_dCr*}J$#Oyb0+EP;dTG`UcZpn=OFj5%j^BCd`h2#ZQ^=;KBgUgQlEp4UZ0OSdVLPMdU(Bm6HEJtdVN3PymEOxKb24D`-!8E-cNpx>y!F^;_CJN#MSHjiL2N56ZAn{S?rwA=a<Xt^GkU>XM9JmeBkKyoN@KayLvrmQf~k7(fe)X_}D&=-f!V`KPOzCeVfCxKcn~C!INX>RkS}HKH8t~?)#7O?)#7O?)y)qciw-Zah>;{s2}J3$19u}dk*UP;PQGtD6h}Kl%rQ(@As%5o`bGlc~`H`!K9;CK6?K={Mqoj_5FnRZI{>gf93T(#CP=3`^nt6Uf)Apee{0f>Uj@Ixq5v+L7!+^8au~ye=4u%Rl?!*T*~1&f1>mMffccHCh72co+MnJb0df6e2DsA_;&nx&Hd=|dOj%c{{8Fnfvb1^{&jg*@BaPk^4asDB=)QKxWYjTXSDG=iKD#&Z&<1Iledua(VYJ$?-5=9tDn5PcE0rg{mFZd@z7vmwTZh;JR(bGq8GJd$%9PXW#UE?*O@4zRxEj-iRC69Hu0>9dTPaz|7c>riLXrTWc>XW-ie<%<f)85$HG(b(~Eo)<M*=gP53DzPhtEr3s1pMJ$Z+T@2C~;u)IpHHnEsmvE;e<S`AlDt#~n-oA4~$IBLb^Xr|y<xJA^8$D!GQ=S7Ua!@`Tud<9>Pb_(AOWZZFhnabF!xi0bgG4t>p>siK}-N-!496!Rk$eMh@IyTUDIqjwGU9^|Bchg?lzD|2-`zP8zW8(KFHh>?X7W@RY=-;KyGhq3y%EV_T-Z1eLwPMMS!p$@Bo{4?biY0%FUbHC_qp1~3?gy59kBKL#6-%B3mb`+#pS17_#@a_dVB&jf#gf0qyIj{66VFpCmb?aE;`u%ky{Q#Tz71dE`Faz>sTE7U6<^}{ITM?y6-#~_Z{n+w@xQllBYvJIKgRgaTlg{j^d{fT_`NNBGk%7Xr!oF;3s1w(X7VoPY_o-TSzaaAm{>}!Sn?n6wFYiHwc@2{ZpO2471WByqnU<h;g(P<u0XR3&r2A8mxY(0`5L|k?KHl-m2oTZ@)%>U;kv}@r_93v)^j*>){l9XIewINku~{@b=*SR6||SO_t0M2rf4s1-=Mv;-A8-5w`8Bc2Odo=_$g}9SJ7r3Siak2Vy}reP0XTJEO|2A3nn(2Xrfju`E&H5z1PGTYQ>WKgC&=mm`SZz@^8VCSJL-P3$J9XCh`v^4pJ+Y{0-jay0)2^Ppw$;T6~G;`%UzrRxEiizQpqlCPq*zmV7(D#Pf?Lwo)sW{0`p4*N2RM(83?$XFmCH#-DHD$MMsLJb>~0Sa<+_MvyBRe}siA@w1h@n>pKR;oX*3$+ae4p;j#UC48-gn@Fwr6*L3zEZhWY#S_s~;#s(5)QTsd*^TFAjKAB$%g}rSUyHVq?`~(@33z#&vDb24;`MXp;Rn`p1asD(d6qez%(}>$>}4Id(RL;6rEMwgrR}}6m$q-xUfMR%UhXZ~=NrLes0GiW7X2pLya1N(0ux`Fc+13WYQ>U$xCJJ%@AK4(C4Yflv_nmdrB*Dt1T1-oiKnR*Oa2{L@+$g%+QO?CD?|R##81?UC4Y-|xvmdPETmQ}c|E?w^C%O2sTE7U6JO%F*u+R`#ggy9mw0~J#CB@MlGou)e0{|DKUw%A{46BTVEly^o`Ijf<XafOuZ3^H&q(rg#vf_n>G;`B-ou=2x9}dztK>QpuTd+OoW|FBxQD0}zlP=(JPY?Awc>}+OvkfuuTm?15X~MuzsmS~Ec_~(Z{h3EPUpKj823TE%wX*GT$gzLf_eCn^&H8Zl`zjT$3E*KYw{)Q_yKKK(O%jPp}n*nN_%Ph7VV{NhW2uA$v%G{JeFGUY--U5v{?X_?>d|4VWOjnGpH3yJ_Rme;zAQwQY)6+9ldCeHPM<{vE;+RlI8zholdP-^2uPy9q9XX3wL0wE6G=zxQ1G><eqq!>$=25J8H#}&&QW|KHfw#YQ>U|!k2iKPb+H0@;MS;;`wY7U8xmI?u0k-bs6JdW8us2(~exo`0XrQh@WQUBN)G#g^$2bD{@=LZ)M@O_~}aS#+-Gva5u}V<Sr(Ps1-{-2VdvIokXp;2+a|A7OsF=@kwaf;#s)%)QStxbi;Fd#_wj~_Go&-cR|~h?~Y{L0=yJ5_W4|wc<s(ST+Mp6V$Kd@p5=22>mqB?gLS-wwjF3MZI7Y7v^|#g(zYY*rR|lpPk7-zzYyG-TJRavqVG(b1X#Yi*u)hker@6`YQ>UIgZq_<i%eWatyuEq=tX;+i8j=VB_9r!+|tCE)QTma3YL5xeV=LJ^BC(Y@^4IBORZRP67O<dmzp@2TCwB{@Fkv4G|_@uvE-xiC7zp`IDuMlNpZ901ug#5e_j3e$ImXj{U2G~mhqqe?3RBqeMLV8mJ}bJy-%B)fAS;D2AK`-UvB&7C;'

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
