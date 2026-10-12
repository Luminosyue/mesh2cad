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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b1f98b0e3d4446c1ba4ff9ba2660aff7/part_005.stl', 'relative_path': 'b1f98b0e3d4446c1ba4ff9ba2660aff7/part_005.stl', 'source_sha256': '8c619a0efb59901de22ae65b9d6e612952a64925c704ff42f31d9c0a985cda2b', 'input_faces': 280, 'input_vertices': 187, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.23230630159378052, 0.10159891098737717, -0.3216607868671417], [0.30082088708877563, 0.2166697382926941, -0.22538866102695465]]}
GEOMETRY_BASE85 = 'c$}r0Yj9Q78HRTf5`qvwh#&%bB1j+!7$HCm7!IgW2*HSnLRB~kNg#kpJc-<q0|gT<QdC3<Alq`0yT~nq+8i}isv-zf+i5#<ezbpj`BAO?(c5%ip0%>~=W(WE&&)UP!#gW$fBQS@T>}|Pi<7#f8}28=*ttEeEwztf*ww>GH<na~n`-A(H;$@nSe{_?c6|Gz^rac)C8e_yj3vg(%&O|fdEv~0K<31n{LGv{W=(y#DO^!Ew?14|ZTm$PiyNygzi~lDL$&qi;dkYa&k2kfkrP-Q_<^4rtQI2U-n}%*(pY8U1zQ6NXTE6n_`%)(bbO<A<`u7RzTfe)c<arXP3^XZ3XWg(`ceGA#S6|pfpdSn9B&`xM-PPB<N0!bz5aXlH(p4JI`8+Jy;tM;=CF&-`k?Z&+Z;bSqve{{58_AWw_o=9(Qm$X*O%A(*2nMzt$+2cH)91KIQt}KU-zxY4;m{z_x1CS3fCXo&9^>?A8mclx89u7ufut6%Ub{b%K!GWOTPa9J;d?N+{b<EjsLiQ?DqqF`$v<KK8m}(i|ZSI@UJ)a_5LVcKSBJU=*R5(^N-`bZwx;s-q*<Z^T+Y#8N?5XdB)Q6e&MM2zKou(9~9qL=*xO{y*LjMd{dkUvth_5&VIjj&zqhbepH;d;I9@teuVR^pNk*lJnQ~XEOC8up?$N%?_Z2uarPDYQobqjrPqsm>GdLC%8zaH=S%tD$(QnFzVN@3FZEoRFZ`&?ms&6LrTUclQvJw$seVMhLTZ1JFXhX8DPQJG`7&R6y~vkdFY={*kuT-TeChs0zI6X0UwVI$FTKCWm)=L@OYbA{rF@w$<;#5O{zbm@+(f=~pCVuSxguY>e~~Zki+sgedwdZuU&@#H((6UO^m>sm<;#32U*=2uB45gv`O?o7`BJ{jmtHUOrTY~5(*1~h>3&4Mj9u(6@}+#4FXhX8DPQJGuNV2!>qWk_FY={)nJ?YH$d~S4<V)`_@}>6|`O^D{eCd5ezLYQXrF@w$-M`3}o}0**?o;GTKUd^S_b>9LeUYy~+75UBSzo^E&5`zx?|aYbbLCf8y?zKk(!A}8*N=Vsjgzln$5+>U`~2PY%~gTRzI}??-*=wdf5&yNZ{kP$@4w{Rf7PEpbk=YD^=Do`uwjCGPJ|zMXZ}U!=fpl{%1CDpA<<_PKPLK&WtD&GJV(sI$aejxm_y{3?|kZ;bLy*c?=kJmzi;Eq`%3xp{!zZXf0Qrp4eg7(>wQG-v@i0ae0l!$dx`U}_Yvn=?<3B$?o*swW7%J>I`4m?%6I=O-zZOxy62XB2|v<IzLdZ8Z|?f-b=SOpQ2D?6`m)y#{HxNLXXugC>s~*EADz?wxz~>r4t4LzLj!$&=)*+!K0NIABgq}^Jtp=EZ5r*&Ga&kmC|~p$IhOH>dv5)6F!4<>hrp30|NU^Z@LIe%D__o8`fASF7jss=oU`)foRu%<tb94=pjt2Htb93Vy<W^&uNQOHzL>M}<(!o-=Nvp3bmt)MVeN~1So!iER=&K4^*-Vr*1ouhl^+rJu=1ng9#*~~?qS`hxQF%r;vQDMDehtYTyYQU_s#O(!}_`2d$`p1Tckm2MlLebtVdbZ%}6(DDm=eJvQ7J=H2$xUYV-c5Um=ao&;5UYg;Z<xP;J#b%I3Lf1w0pi5`7$g5}u7d2G54e(MRBN_+j)R_+fa4Rn1l{x2gqQ0k^=L&{gmzcnkV0yaj%qvU!bF7tr(Qv+#Mi4P6Dd!DrDG@LBi_x*R?OpQdbHhBm{?;ODG*0<A=w;Yzp$ZGmgxh3F=DAzX)Uf$QJ~^m(`eeu}brGr9)e46pXgZZ&1|+g2S$kD?dgqwo>*JbVN`gtozl;DhK{_#k`$Jp&(r_oJub{qR1kUPn)%r{U9l2d5~Tm!i+XOW_Tk?`Z>N^DL`=gw8>qfaky=v=R=%RcH-d1usAs!VBQVXdS#5u16c-dUz4~6ubzYPuX0HZiZ{&jp%B4BfJuQ8(s;YGdj<~Im+fYta=q~MGwQR@NV=dyc^zy9)WkkJJCb%PWTn{Ap8ov13dumfL})U!!N_z(S7iC_(h}hJiSQSyv?eu=w9@7crSbsJq6pk6g~+*gKmJIf!Cw6;Pr5s(Ru#L&`04ixD=fUm%=6J4A|C(;1YN(`eS%4+=MQHZG8)Fg5N}c3cm@P=u5DzFTf`J8u}CXHFyuY72e8x_fR&UKu^Land1q{=0<cq+z78j%iuERwT`kmf|kG~%q2qE97dbqCf+|x*?b%|VUzbfPT716-2?C89gd-m@G<ylbRE2oo}Na-aF}P<Jk_c@teTDvho{5S&|&a2xCp%+E`q0^x5884Li8565Y9)_;e0p`?G5L_xo8hK7tWz<PPOU=v?tmF?g{rnd&7O;erP(}555__1-=;`gx(4df&=L7Z~z{P4uglnndoph6CQ%z0S|$1qioJVr@|TV{Z`$JK7dYzAApO|>2NXpAUX|x5WWvBg71Ta=oB~zPecphiEsg$4;R4W&^&k?JQ~e~N5iAg9C#F*Wz}G-CR;TCy$2ou_eICUec@i{7`PYQowE5(tL{R_qGRB(@ZIQm_-=RtdJjASo`g<@C&BkpllcxO^KSQ3gZa*HLkFUR;el{}bO78Rz6tFM-vr-?_JVJO)6nj48r;pQ6tpYa9q!JIx>7c0d*+ypj)b$}5oi{i#rHb`O@&9m$wp`XlhG77g=Z(D*>I9oiALwg<^;40Tw0uvn4a`~|3#ql6R{Wj{=<O$N&i0!y+2uG?WO;bSX!K%;x?1$T+|r>`%nJ`Sp+_Z'

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
