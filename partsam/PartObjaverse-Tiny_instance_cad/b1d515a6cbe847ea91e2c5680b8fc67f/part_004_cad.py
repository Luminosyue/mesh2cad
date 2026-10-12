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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1d515a6cbe847ea91e2c5680b8fc67f/part_004.stl', 'relative_path': 'b1d515a6cbe847ea91e2c5680b8fc67f/part_004.stl', 'source_sha256': 'e5a07acff5ea52e91866e1cc225ddde71cb9d9b64296eaa1a8bf655742ab561a', 'input_faces': 198, 'input_vertices': 198, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-1.209779977798462, 4.500439643859863, -1.074367880821228], [1.1976227760314941, 7.414896011352539, 0.7346189022064209]]}
GEOMETRY_BASE85 = 'c$~diX;>D=vThKg5~3ogxMs*AqG*D+;evBK5KS<O%P|^Uh6v&Uh=7O+I$}J=CB!wNX!1oPsJL>}xHG}v8pY!t#4zp)Y81@znvL82R&fux&%J-{kNZ8(`&9QkHC5Hs)ipB^7Fxr_Q_#;_)ONY^*ZLkpD7XnvksOtfG=5A}V*9xGX-=X(c=fB2%liNA{jlLqB3aDviHu4dli<@$^XW0RtB;@NGj>u!QbI)B=t&8YQHp;jA|^3P@`>Xj;-loewSQn&KP|x5PfOGOk3Ux#g5Ep4B45dSA<cCu&GO0T)ZA+C4&LF@9lX`9-c2<ZM*DIl?SFYShJM?rdwMCoSTExJS2t6<!|UruYHoNrfp;vr0evkZ=&aH=npscb=Rsmq@afN=sJUj&0x!1Lg}%M+stvnuhLV0vB;v8#O#dG9F+IR*L1T&Uw(kb5=Qr51{M?%;UKCFM330SM1YV5HL7XCE<O(%6N3;U3@5n|xj&_4js5s51jlmmp@}O_cj={R@O~+wR^!XZbiamWF;Qqyfz?->Q@T--+xTNfe%r73p|Jr2OH`ct3xb>kX<!NXT^mV-m`u3WY55ecH!MgNb&L`k+_5$$ct_xmRuUmgwPuYty=r2g6eQBI{0e+{HfH%WNG(wyMB9CEyFbBL<@+o-p@reW2mx&XJ_uWSO?iGxDiU*CsJLcyj59a1MUnza7uPgCOW|95OkFj4yhw1mhM{J|@e$oA(sFM@!;I&T0uwy^-pmoMq-h<x^Kg6$RPJvyq;t+W8OL9Z_ExPtC@>Vhfyq1;d3BLg!?S<a52=IC<(zpCW3VI>0|8W=kM|wlw2u%U6&A$cS5uHW)NtGqY&!X?a8)50#7t>mN4fT*Z1iUHM!j4|t@iP2gPPzlX;TvH`Oj>psewTCsFV;Ch-=TS9e;qfM-UgpofqgUr%1e>Y^5?gZhwJ^|*NAgLoft>z;`|wv{peg|PPSpEZ87%8u5*y$-!us8H_lGILFef(<<n;`)$MBu;4RnJTR=bi_7U(s7F>r6I7jt%B(xB7Uw`l-ygBK=^$OL4M@1>FZ>yy9{<>iy{%2|69l5@!2YW&=_S?>M{Soo_pMk#STCofDnKb1Z_!h6hulPQa>UB%TMaY5E>HHSt(s`cy7xX7>Wi8~*>fDLW;pG*%Sois}$g}w%=r;Cuo&QF})3&Pz^uv2!hu`hbb6|hu!Ul-5<|*XUzFiL9QP!90YQgW&H(f4+x0)0XpF8>n?3lS5VCSh%Bg$tb{F>f-9ndejPv_{XB;;9tYXNxe;g6KJrXl-KC#!pXiTIZr*e|2=wmaD0jg@P`r>@3163#VIKU(n}@Qz;5$b(rq`!4cd=k^-p`&lOKS3M8fZ?_k#kf$kqz>Awta89kXy43%Ub^vdB{eFx3Mb9OWQJ+v>8gK*o5yiU}!msn+DgRxD+(h4qZ*4$7zY{%25+bONT(6vs``UM=JV$z51)mbK6zjOt3Hzcqj6gh&cPD2ee+O*p8%-XgZ|ci(zJz|OfpqR-N8vo!F{SHZzvvk8^)nH_T`z3|;wmbo{pu-jZbiUn*|6VtJ*{i+d#Ee3d7rJYbGi-IC7xH1-$wg(qAuQ9g8elH9HGAS>ZosF|Mj_8m(ZsoKl;(N=qpxZT9@O}KFZrQukR>+H^gJT@IhT!e&@kkrQ^VBZjs>iU-}lpZwJc1_-7#TFN>qlAJray&E3bYAa4&-j=@j<466SIS+_9n?s*(`Iyzv-azBIp(pwA#Z_N7@eM5g^JJs!nPI&Iw{%;|Eb447^tz+I7r*Yr-K4gEC3q5CJ1J8iB!sxk^aEa_Rx>*GKbq-VhYqY|CneRB^`L8DmioZ1V0`fWGIGzv2@$+OqVdrh?V}a+f-g*~M4`y1xMZ{O}8F=kp3ieAcNJ9OK8*4~^ze)R2Yw3^h*YgrR4=4XY=O{en2iRHl8+hYUIO<<7J6a6CPZQzCJmXLGS#lBm-w0eneDOv)N7=*ad0~yfxzr<lsn6uLMV;$|Ucz(0v1TRZf9j{`8}=`=z#E&XuFOm8@%~``o<aP}7s!rxGW<FgPQL>CpEjgAzd8)Oo|l4k7?)hR4$IGCziwsG`W$aker_~HJsZbvg4a$yqdsgsI*56H?_%U9y93#GU5-9(xp%yZe17Ij=lYL0s^f^A;6=QH>ULc&&ab%JrUdcU`xSY%U)}+~)||uOZ6k@|>=Flmb{9WdpG$x0|JlLFgIG8Ry!NXn)lcR{oFl8u0&lyy(D{l^xrBAC&cHs~w>HyraQGnV&ku{hn_b#N-#)S)>o<oNgLmBhgZguW`vveD@iTa_-WmDPpUuR6hz&#Vd={=@*mo_}gPxZmZglSR22%eVWLen9+Hcdj&uD@5I!f~JJT-HBgE#u^!n*9-OE^c4u5sYCr0s}PeAMa(>LWJUnOREpQ27LPU|l_meqi)yN$<UdzUW87=M?poZ`$KLTCWD-yqign={Z(bm-6N_<P_@D?+HB*4@6LZejbi<D4MoJ{;W@eX}{)1Y{dP6(cra^*3=(r#o?T5qt}5qgSbA^KllOrKI}2o`?kxZ-~8(L&^y!`af#nFT5tK#EaY*LA9!s-3#zM{C8wa*c_j6%nwh9)?W5M{Z(7-I@b+n6<lj0~h<&tvK1=pv9?-rI3oWAlbBp+66pzC*40Wm1eN6o2<@BC5YZSf57Wai8bLK;e^W6T0$jjZa;Pu_!$g?BW1AW0r+fQ+I3!=L9x{`|f7n}ia*N;bi+TQ-CC&!l$N&lsM^an>#0@Znu7y78NH;(e~Qf<_^Ij1GP7dSto?~XUd((`EAH1J|+JiUjnKTqEk{nmlEVn3w!XXimD6|W844qnfFh2Dp!9>hM{pX>l{@9qyfTIam|xZmjkcymiF`feKC3VqfrXhMCr)^V~E5QOKicr6yZk<x|y{u+(GFNV9{1OMIU^c+l2M*p;ev%otJ1W?{;kNO(%^;%DS@KfsBCs(7Nn9j}bBQAGWI=`#m+Y7se{lVMsx1oNucm(y;bIZYN-(*ufQ8Co7qK|_&J-n$87yO9#XEV0j1Ne{C>A8PBgU;_x2Y9XcG5Ia|;5+nzl3``A^XMME7yaBE=gP6C#Y3u}GJ4-=xb-U4!*1elx|068r;$&`8$OS)4uASCvt|m!X&zbz-dfp(^tZggbJuL_{21|s)unyu)04ihQ-goP^_*DxUMOsU{-8&125-;YMD=4V#QUe!Y%6#z*M;&HVdX;Kw-CI(X(jcO)EvsEd#@+3bIqTgYdKG-zwdYtymcaszJCYj(erOlG<dznN$T@S{ztLz=azyu+}*LiRy}w0H;3;@vQt_KJN8dr$d8@v`4o1pjHh)iPRDz-;nxnl{h$T$gL~0;&D^C=soyrF@Au}Pqn~I)4};gn-Gg5}r|byyHaL~T@9tfcpP*bk$3<B?@ZuKbM_gEo_gX!sBY1uEIm-W>IrvU6vbvMLF`3@ygV*9a$Cx{U_<wDn_qw?i`2MxyW5GL4)88?~!BwY`pJ{Ov&&=(l-yjD0x7s9<ohyR+e?d9EvxGJkyy<k2-j{+}(tB*jdBiV1M(@?LchPryMh3<I?r!oMKM(!EXu1l#R&jye6BbXT@9O#MDW0oi=sWSZV|Y&x&vHrMcPrU>=0o2X%|r#(RW^&hQ|>$Cd)Q3&1#fH_Oz$Txf4`d__NTw59Z0UV{CFK96zT|1F*c&wpVAbmepT{+{!`lcj{jeON_$tvFkGT9OEnLd_(Wo=M2f^mEY*Cg#0H5R9xJ&`Vz5MjL>C?_878q=;vW)uEY*CI#1e^x600RLS*m#kU&~@F;cI`FSRj$gQq5Oztg#$>EYGJ)?5pN8kLP>Xe-6j6fu))kNPH`Ch;f9u!_4QiJY4O%C2@eq2U!0*_Op*s$efb<B@XiVAoKamA7+`)*B0`6rZY0D<!42;^=ELNR9+@aL|4m^ng>Z3yoUzQRsAlNh>{r3Qq7l1ES89rn8$J?kNdG+IFFT7wUQ|DH{SC^mdfuyiO~`xSgQFDiElV>+Znmct&~V+|H<rIjYHXQmH$wV`3s3SiFlT3zDE4JUJV{AIYpwoL|2JnjIJEFL*h%$uaZ^uSY`LG3^jg7;%km;J<EAK9>Te*%9)z?6m&+^^$jdP<#9Iq-oi4Q{eQ)>`h2;>=X~#HJXUg*p!)ub_5Z<A)m?9np(^jaIUaRZcS`JFY-KKz^FEp}ggMm*)=I2nspe^%L$%*CSq`g~PnEyvJXTWGRSertV;RGKa@p=imMeLz_+5f(V;9e>bkbO_%GSzidb=5WnH#~rCa|ok$249`3L}QO{t_J}-e=i~$4L?q5|dbt;_-(PLnX$rRP#X+<CsfeIgYQTvn`Y5Bp!$GeZee4*j@z3G>YZ>Jf0;nS7I8=**u=bz7kl@s-~09dg<&_jTcFL%-28WYic}4Vm{lM&vvTDi+H|>b=7zP$2ykf0FJj0ucK-`YW@NHn!)~Na4yo>$3*r&v0DB<sFvfZ`9!{VEZ<+{Ta7#O{taMs<al}rIuj#Us`+0ex-mC_Ww&a&>bg2Vs&57g>L~_~r!WHf-ax)rjay0hOLX9|lD^EnC#aYCvsBlbOK1|W@mR?gd{29cW)iJgs=4~rmT+RJezhcYiMJ*ESgN_|VQnSaNxUV|hR2F?mS`y9!Ej-&2HSOGS%ZBwt!CSg=Zz%l^ZjqK^x^T#5_Kh-Fx1#vq9)sPW7K0#twH^d&z+&hjU`^<wR^Et^H+p=$&#;^JZ`|(s`#30w;o@s()DFMU!J$(oU1%|vQ+by60b|VD)9!7Tk_n4=W3l{p-#@8HU77Mss8(Css#S&AFTiV&Og6CR==~qwDn&vlVPDX)%xW|Inx7IRf_meYbDT_'

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
