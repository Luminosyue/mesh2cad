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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b3a58da30f464dbba1c53c7f3cbedec9/part_004.stl', 'relative_path': 'b3a58da30f464dbba1c53c7f3cbedec9/part_004.stl', 'source_sha256': 'a6b85b685c27bf086f866e5731b24558842d14278040220854a74ba6770c1be7', 'input_faces': 226, 'input_vertices': 230, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18954920768737793, -0.4999998211860657, -0.25274768471717834], [0.057330422103405, -0.025795966386795044, -0.09502823650836945]]}
GEOMETRY_BASE85 = 'c$}r02~-u=8OH}P0<NTzXx#c-pC}rGM8zsTA#uY6wV1f00&1{GKyi<w#wAAFca0)Mao>W8yQ7GCPu50*3o4Lc(^g|NO|_m_?VJ1kXFB)8p3~F5bME>7`1|qQJ9qB8n?!_rR`yfq(^z@7yXQZBUsn{pR9F0z<e0=M6UW6QwT(}h;i32nU;h}orhjC=h@l=zvNFpa9g{RJ(cal+?-JX|9$>S_PEMSXI3|Ad<izM0-S07GQc{fDPns|$A;$f4%fR;S0&MO518j3_|Kq2s-i8)o&U0>Yym+)%*Qhz)oIhvrOMS}Ib+xq%%Ch>lmR(ZC?~T4A#cOu*6}#t2tFMH8uvz?`@0S-OKa_k&_Tb~Xsv}-(@23CUDWgREd*-%$tFL6u7QSOvV1d<F>(3It?P;78@7NU~{L-Dz<vhvd#o}k*o|mOO%1Plzow*_T+Uyw=zbwZk#d{5)_~21;o+bVi|Ce|v-ckF-P0{}K9u$A0d#dn@4p93~?a7yX?}froecrJ^^2a3!Uz-}s;`@-l?QfE=_}vrj(drD6>eY^)C*M&b`Rc_F$@jkGlHwot622{Pu-yJlZwf#4;S4EW&8Z@MrJk3FcZA%c_>w<U{~UW?^3@-+C_eqV<SQ#D3%_(%u1oT_^`ZE+eMP+X$a9DA@8^qth^kp9U-CoK$PfNL&+2PiBZaTpP8LY<sz3SRizHv&TJ4soH}0Iv>O0a?sXaf0$^OmN)c)CHbEJ9?Mvx!&gHx)v%ufD4{v<t@cK@0fKei!DsehDu<X;<4@1^P2E~~GmyhDCQD7~+m?I?ci1A4!w$I1TA9BO~{+mydgS89Lc73#N5_I%0zZllznhOa&wCH1En|4B0%=f%mAudVhK{h3;v@3Q(z=dDt|nfb#u(0I!YmEzT%ku<I{A3LS|e{CXsM|_d=Tx#DksXvuYXQ-XE@P4<Hxvai=W(VazGa$$6E7~gRw`Gx1yd%CPwf|ri<+uM#{*O!Kc=+11rqs@mOp4F-OcU|<YKrzm4g19<`3?6`d*b_w_NdwA!dH*pr+$t;lqdP#8u=?`Nxo9lk>2B7-$Ka`s7CR=KNVPg$3uV79!-1CCB;8EOY>oqVy9GZ?Wy!!_RDfRr^Zu1Y@RE{J5qcoKE1ybuWUL&?@Rfaz85p9r;C1D{*c-kl9gxm)#b-%y}0v{<SP-Ov@Ue5RVewly{I2L6c<>1N4GZgyqn`(Qv94u`W}5+;*{!5nM>ch>z8t*b`DIWahtS8ig$$2JgK@mOYutWi{g2sjy$08&?k!g#m(va60q21_0^91sXrV2>XhPpET(bTdT)*t|F{OlH*7@y+6C#>ah^Kqxl{5ps?vK2t4iO;!j<HoveWpC+~%_SN<W(Sw4^k8kL!l-6wiD38Ld;zr{!6Fbxk4p5n+<=2)ENZSh-E1<hT9xj;JrAw&W`hg6aD^p^?k#Yro`E`^(duQoRbjFLiiN$=8-dQ$NI1%9Y|*JQeRHwQQ06TwC@CUkzzR{WBq&{1-21J`769v---iZ1S)6l6-YgAdSz^R)tcYk|*MMl~ixZ*Sd72{!b2aNqMlI+UD<ZN_j5KqvskhLh{XZw(ObIe$DZizIRs=BwtO-B>z-18b7@kP@ahP)c?l(2472|{gt-iveW9TKTW6il3Oh0QQIieeCt@alKe%7=(*|_Iwk+kGiuMFV9N7gE%{G^M0-j-6I@o`@#;bv|Jj9<-#<I!W$}j3<F(bUjF+{?^m%&<iZWi>KkzH`5Bv)KWB9Cp)I)#Ic-eR}d_LX`pN}^)4;ycW&&QjYhmAKg4;yc0d)Rn0^Rw}0=4azgyH{zq$j{~z!{_sf8PDbu(`WOE;q&>#@cDdV*30G-GoH;SW;~lu%=WPPMC<9=BjVY7YxsP=RX#4Fcs`#SKAX>#{HK(MuP^W`tS?49Utf%Pw!UaygZ7Gk;OjN~3hOoe3hTAu^Yt2jh4tEq=j*jmFJG^XcJlSw$j{enBR^ZOwSiM9KiiL)KHHBOKHra-KHHBOKHra-@oYb4*30%|rqA|cW`4FGGxM|km?M11J`vCMtESKPtIDJC<n#S7{0jTw(ybKF_vi2{?9bs>*q<AD`2IYv!G7Vh^N#7W^N!*3^NtzM&O3(B&pU?C&pT#*cHS|4cHS}bv-6G_&(1pzpH>vl&V#1U&VyPV2l?#0Y54rSsk9hE&&AH;rq9mfhR@IAW;{EO8$Lge8$Lgen?5^_oAt8uxLGedkDKxAJg$Vzr~K@G!|?h2hT-%34bx}$8)``110p}aFEV_7Uu5|FzQ~Mc_eJn4+!w*Ga9;$!!hMku&+m(jdii~kk%!$EX%mN0Ji8Axe10Ej`20T5%){;j%{=Tr(9FZ`0}Y?w2b%HhKG5{peW2MM>wRE^bekMMv)6#S)f7c9K8l|bJH~RAteg7B(3f8&PYn9+u95>g{J&Spp6)ih;x3h-mBG4tfIaYNI{(&P+PI51^fzE{un)90*azGg`X;zBxH~i)+#Ng;`StpGL%V@{gJYn>!7<>u&`-c~!CRm^!CSyzL9@YMfv-aEfUknTg_eN71)qR^4L$+>44MJ{3_K6|DR>@uJai;@B>F_>Sa<28k2@5dZP2!08`ul_D%cBL1?mf~0&WBi05<}MKzo5hz{8-?;9=k;(2u}Nz@I}mgFgpfgnkLW2)+gV27C*A8+rwN8+-|R9DE793%V7&3%nGnf|r6vKx4tN=xd#ux=Wy<|2Glo>)`6(8qhl68sHYtAaDzC4`>9q2Y4*<>-F`6hJpKmCqhSqCxRD1Q@{(r+o5~F+rg)yF7Rpab?A5C>);#E@4+{~XQ8>^v*0x7esCIi5p*SZ5qJ`GEO;#XMCZ=#(#c(hKnH_|fD@sU!HMAM&{^Q=;I+^V;I-hx&`j`Q@C9fg_yRZ!`bTgU_z3hE_y~9%bQ5?Tcm{M1cm_BL&#OOw187Td18_sAKe!<{82USKFgOzW9yk*GAv6h`gf{5h&Rv?giyyQq*bn>~v>Ny|@LSMk;J3j2q3?kEgX552uP+qZ7aR&61)TsM1zrZ74_*e|4c!Lb4R%6Lf}P+}Xc4#+Tn4=cE(2eNo&sM6?}es<_kveI7lK!S$3Wx2ap)7BJGe_1cNqkIA3O*g51j&z2hW5igJ*)*Lsx^>gO5TFf{%jpp&B?JTmU@}E&zW4Jp}#&yb-zvyb(MbIt@G<oPg)mpT8Bf9=H{_HMBmsHMlFZBe*MgDD?N>q2Q^|1aJb{pmTe7Y3?p{p*6vE!EZoof!_eX4Yh;c1`mYx1P=uN0r~a%-h~bTzYC6negKXFFNb~%UJl*|-2vVQ&Vil*=YY$hH^JrLyU=3rU2q=s95@er0GbXy0A2-M3|<8u=PnW99+mt&|I?pn{QIMd&8hVdHu!JK+i~k}_IKwpH|G)Iuju<A_a?WJnCN!sJ5=Rg&x6^9'

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
