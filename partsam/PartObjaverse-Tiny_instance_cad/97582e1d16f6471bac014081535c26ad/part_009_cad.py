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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/97582e1d16f6471bac014081535c26ad/part_009.stl', 'relative_path': '97582e1d16f6471bac014081535c26ad/part_009.stl', 'source_sha256': '2288a55c6072c2e3417b13858181a99ea808729b8d345c2f431e36b729387506', 'input_faces': 239, 'input_vertices': 175, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.13146190345287323, 0.21267975866794586, -0.056481413543224335], [0.13146832585334778, 0.48859649896621704, 0.1918012797832489]]}
GEOMETRY_BASE85 = 'c$}q~3v^9a9>z}ut$37%Xhq|AL_AUy5e#x9qBLlNdWVxpqA8L{LJ*NdMLZ%6@dzO~Leh97sj5nqxKyK~RhpFQ`;Jz14OKOkS53{`-~Nm^&8#(RCTs2W{mysy{qO(Td!K#wz6lO;uG?IZe{Gf9)zxu7H&ql-8Y#_{d6Dsn(bFRny2ZpTa8jDW7k>{md(<l<gC{yE^OR(-h{%NL@m~E^uK`hgy}VVgsMz?#_^_C1vGEa+!XFwoD<RV1C%hUK7wNd}^n$OCx7w?-x0<5<kAE(X6!eN}+fj!ar@cP+bEv7@KOoe2s}#O^tZS9HR=>Xbu26kQCVbnX9<qM$+!CR-^bF~5`=wf3E9DE1z%QExUz@h|9O{4ZDdMXIp|ah&K8SDAUn&)9Km4-v3$K2LI4<X8oSDAxm5*}~N4>EC?dk!2;Oj<&^e6m&7;(HB!?!>8hs>wJu5I{y@V29f6B35{#)!A!>;FuFuVwT*i#&TIm*aDnF!;v)ljjk~{Q~kg^Tx^g^KK$f!?(VPJg>RQ`WKI)z7|l7Jne~>D^UM@H^f)Yxxa<acOQVSH!DDW)innBo4KQ;Uw-lo;wCMqK%6yx@Kxu1Xjl8*^Y~-FwhVEMP~Uv$fM&AYjd|z?ZJ-<KYpEBGpnkju`oWf3bqs#E3SZCkN4rWNr=7^B>yL*KC;gKz(4J2j?n`z40lpFPEqrDDhv*;ebQOHPvM%O{axo_ke%EsN_Tpr;tHebmA<unz@RhMsWxt)7jC|}X(q;WvSIiS-#OOu%e4#4a^~jRrQc<}Qe#k%G$2@$n2KlIg<1sGkg<s(-1r_j(V}9so?bIpw+OE#BpL3hZ{%o-75d4`*vi_03twnvm3Gi+9YScH*yJyLH6awEIJ{$FI`@N9A9(CnC<R6^<3Gy7|kNEo4LipO*Cg=xk-<1>i-rYR-`lgn$-!dDnL3_ie!8e;8z_{CnPWlk-rUuCRPi>O({O5u2l`FpRZTG*D&rzPwN_>C%-E#O#eb8^Z`xLZmrtE@m@92j7O;7(1@ICKH_{zF&U!q^u-rEcRv=@By{;3PNj^88a?Me?>|LNYSZ%la+^TFQb_CbtS<ssBpD~4cPw7_ck%I=x6|2Nh}{$}Tu(y#E4@kd@uhkq&vzS^?i$EZJ{H~Q1o=<>UW-+mzKYiBFa|4O4m>AO~bitC&?3Fvp1hSJw`^s|vWBNy#ul^ww6ZRNP@Q-`2`G<zC+v#>Gdp|Qpv^|fC{!?#bGDWAL5myy5iM2Pe|6=U3Og&A^OBCFoP_X1v!&t1Fgm1xH`Q~Kf8<oH%~I0=nevLA8U#meWge$REdPL6=D9`A(pMBNjK`sRi|-o|}ZZ21cL{E)W=aniq(e%B|zM!oaj6hm*UhOc}ci2gKEHp)B$!r^Oof0N_>*_l0PXMQXA>bGm*YjN|oqyGI4`w-{kQ1qwmU2_Ne%gqVCHtCogU+wS6)A;?)Tga!}=Uc?TwE}Sr`*rEt?#XeFEm(rjgU-O$+I7KwDf2UQ=!b{l>!Z(ogX^r<@I0!&yb0evX9LDvOLG4RepNnvHK&1m@0@sUC-SWCE#vo`gnaaXS9YO(etH@5@p49d+mB1J9_sIngs-}X%XaPcV&UKK0$({_fqphV7_k}o-zzFbK1D7VFPoW&eC&5_m7v|%T78H1b}W|fk$NYjZ+ipzD2t0yaUa9x!dI@gmg~>hiTTLC%~a`^4Msl3!|@ukZZAHMS$Z1deceO0J9`;?`|?7W&u<yh@6%e=&oPj{l72Z2aonr+pdWgDgnYEY!C3!|F|NhP^ND!0YyNQ&?=`#E%_8`F$6`KcyLT7Me%TD)SWqtS_u~z?Uwi&a_-b5ljEgq1*DlmAx`uhAFK&VQM$#d~*9(usSKJEF58C}SjH6b5)0Fch4f*IlFM1n#yD$g!zij(G;)I3B`POmaM%3@$U(SaV7u>&oXd-;O^F%qH^#QnlvnpT%;zSIQ`J7&b`0Bkn@a>nf(XM*6azFadIW8OVPK3(&|KL&~;=I1;iwfa4_mKYj;YBrlTTYP7r|p%!HGO-(XxX2)^7qvA%_n5LhJD66el>hGbv*Lax*ytK)7QELq95!7wiF=Grn9sCYROYs61c&ymiyJCCvWttt$)rX!?*UQ&3Q+TUoHKwT+!w8kv0+Wm8-Ueh_mQ}9e%ZqZ_2Om|1=*ut|;=WW&UU-Ti{#gn?C;{eC3RjY*#6|Gf4QQH)NdsQ{?>5dVU1v<%65>t@GJToVXj;%fFKEyYUm&V!TTN@%-tPWpW+!zqkUvIbZrpvRpSVPEJ9b?PuZt>G?X+3h!I%^QfFjD3Sg3_&T6w9EWdRH;l8lrEghhlpaagcN>3=m;0R4*_$z5)m_W*xn&(QvqqK4_2BV!&xrSy`&rBSX&-39x30J9lZWNFS=Mdi;29amvd-JuUx#mfFQ_x_O5gGxvCZ(@hkBOxk@o(x@_DtqzjUVu@U8DnGf>BKqo>OLQ99khKFYq&fNy;-8|~BN`M|PIQ06tn`N_K9Fp~<UZ`q&NX014gYs>yejkyKix{p$0BjkDI8yA`9g(lOH=eWM_;r=cAK;!HT_(tXdxew3vOotzt58t}~)RvAvggBOcuQ_)WeCs~hSbyVv)VJ)zjU#QaPqgmajhpH6+-BM58!-o^Z#gfReX9@4=j-wFh3&M8^P=_qqJ1_9=O^p=$oAbx_||ilQvMUvdS26A#vg@mIrk~ii=}TlKdQ^N!nd9`?V*irQ0w{hk`H|AdDh(S3*UPFwcU6bzV*Cp4+xdM<$P^kng!o_9ygC<z_*^?m7mr~-*Vp9e=3D<{e3{YSuNYG`Fld}W51G&>!<d7r=g;V(m-jhM1|G(iA0#<@1fTI6G?RM|LP}_p1u10zdw<*5?$&jt}KF^P@f<-AvdDdB{w2Br9Me+N_J-v+=4}LbE-4>X=;6{Gr2z5iK>vD$n~go$o0sLsSU`D$*rl+l7)68w<dR{`j9)5eW?LtU-C;Vf+tfal7)tmCzEv+!BNy1WTCUkQREmF!3oqPve1>}1oAQ#!I{)I$eHBz)Q#lz<XlH7ag<$-QpzHDFSUTYmt08AB^Q#nQ8$vek+)JekcDQGx01IwN)B}`HJiMaoKDRk3pL0>7m$U{C#RE_Q|FPFlNV7Jk{6MevIt&Gol8!oCQ|2;6UnjEII_^!$g$*T>NIjRIh;C)98R7>4JJ<^k9U+HY9KY397rBU4Iv91NghTXMIA>TMIJ<bkvxd(PaR4Y`U2UX+@0E%+@0(}eU2>DmFz)oNo_)INq&afi2Mw>4Yet`4Y@tlo!ph$h3Zc3LiVJ#APa3y_9S;w9<5)USOj}H%3r7hsXfR-`;mnXCl4eKVG;bYqr5^LOC3%gOV+6U$QrpPi{K8_9^?*WmFh+IV*V<N;AYhN<YwfCR3~yn@>A4$<fq7P)W&2tayx2kayxQwYG<-gUvh8q0P0KR0p!svf<vj3$)V&3s!kRfMUEgxvIw3@jUfw7AkQSvp)MoOA*ZkiUPH|!uOVkq*OP_jlC#L0s0HLr<UHywavpg*wS>H#yh9QD7OBP55^^zl54DtBMBPm-B@5k4-c5d!Met5)AzA1)ve2#Mo#cG#7IHp$v-0TOu$e{hI_g^TI`S%NI$7v)@+$Ib>LT)L@)GJ&@)B|ybuszjJ0Oik@CrwHotjKdB`1^Psfpxx@+@jBS!gtQ7Wq|bIQdobbm|oHbn;Z{c=A;81m)2?V*-odG1Nfv81e|}FtX55<Pl^)>L9Woc`((VEVMg$Fxi{xK^EGQ>`m@QeTLkP{5-V{`FV0LYI|}oav$Z<JD?A>3%L)uFV&OWm)ze`f`gpuG<W__{}z4pXJDgR^Pi;FZ$5rhsQJx~j)nH$2Z!LGdSb10Y-;OZQE4IGl*+#Vj!1WP'

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
