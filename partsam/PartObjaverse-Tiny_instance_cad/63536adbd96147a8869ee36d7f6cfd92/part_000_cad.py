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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/63536adbd96147a8869ee36d7f6cfd92/part_000.stl', 'relative_path': '63536adbd96147a8869ee36d7f6cfd92/part_000.stl', 'source_sha256': '324427adb8be6affb899cb5c1358d6fae21e2cf54b9b17bd8f9cb172b9d8585f', 'input_faces': 240, 'input_vertices': 173, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11938588321208954, -0.21231308579444885, -0.10400950163602829], [0.25133752822875977, -0.022366255521774292, 0.13469389081001282]]}
GEOMETRY_BASE85 = 'c$}q~30Tef8pr=xvP`yA=vw|2(iB6bl+v*!V`-rnjT}phB`wmR@E=@^A*o1V90pk$gk<kD#>CiZFg#{XLo?S*W0}El$8yj6zF&9hKKDM)eeONa^FH6t|9jr^{@(xZ_xmprGNf)j8$~`2O6D*JzeCLxg~Cd)QBtFmQzlQ0p3!Z3;%p10Is5c^quIm5hlRXnp`<El&Xb~NOiXt6Rh|7}dO5qP&M^teDaqrfk4s3N6it5M_-Qku&HjwI@rlvq<1RhCJ=|0e7dLgT`agaen_DniXPzjfUb_9bhE%JUv^Ic_?IYONHHkXK`ov}rsc~T)_O-CHW&At$-G%)9gvZDD__v-0)>3sP)iG{f$iDH>=ch^4?DzxxdkZ)AwRMlq@b^nIxsI`M3-)yxr+HlC{pTB4`&vr<R-Z^eH|>tp^fiw{K2|Fec5>dp#Yb5`Q>CBv*-NP(UCv|9(|zOpIsfi;YBnD~EI-W0jW6+enZ_D8Pig1KzS7KF>K*%XIcu8DAy%vBoM*BfB*#_860Y+^k@MQ|?K-ai^(i^;8~$H%-j-K0`MCP4eSCbfiu+M=lmzax?Al)b-eI_$x7(80ye<Pq&f(+w@A2<UpV<}F^flMuBAy5J<X-k4=Eyixd$X@!v|aMMA4%alZLf13{mmDWf9&@e?7uUC$5;Dr6Th&Y_)iq}O~-x{|Ai@ueOm|KAExS1sh<)n{?FxH->~Pl_=c|&xu4r!+>hycPpK2+k-+&Ec1WFT_ar}Y({%RlMepZ6L$64_(RvEkv96H*U-uPX3yk6X*N3={Vboah6K_qB{Wg);L5&NM`X*Bp=jZyeum7(1KK3(rjAFk*=4V{zYLetDsr}er8ppocYn0?0+o@c?DvawGI&F|~O)-9?T5qdjuCKR|e67(y)?ORAj>+SU<aaF4vp$WHd8n+jpO3p(PhvglA$1%dNF8O1_@`Fz^`jP-NT0JV$MLus!-{2pc9MKGej57=FY>&pSw2#Kc>(V`Wuv>)c{xDxcaBbCz0_Cyx;-U7qfH8HyD+K0cASjs>pzn<p<);NXRb<}_nkhdRln&X$uI29zE+tb=QYSv@)w*JKQc)6;h;Pjx86dz4(zLBU7GI||5`{IYwkv_V@QY)fBNxsu2a;VeRXk#_-+;RSY3YMeQ3zLDSp_z`K$$3xlesXwfJSOA99_ycJun0iW(h|^9)`f{mkV3X^OQMziI~i+MsK4UYqQs&UbqjvZgKN`BA5K6+hi1{*_<ZHzZ#W|E0%b)_J8;XJfF;&ky!Xxc>Uta$b%jW!zn(#NY4-&zrvO9PuwtWM6SD<@)+xVx>+*n~ymEa*@=De=Os!XuXW}wj%pEviLwPUn`e&9JO5htJ{~ehT4n&Op`hd12edO&=OgfX0OF><HOGfr8-aMS=UtRq+H45{HO=G9_ttL@t(VxG7omV?)tj<lHa24D*pcZ$Hlewvv(Bx%7at8d0nEqN}arP@$amWK2HWo{=567j&Edf&Gpr~UCWm1=x@BfYGIDlY11Kxb=ecSAC~5eA23J!eU-9Lx?Pkyvv0All*V#DhRfeb|NA~(%{n???vs`0q|SP$HLR8uG7mY5<aZt}ex(cc;dII0J&S!MC~J4E{rUV{E^CwSaviOED1PM6;x8+e`)Wm~)VXWR&wuSsndDE55dY33c`pbEm;3g%BkU`47v!<-9<g8ct%vw=XY*>+$3D@D@360V#qFy#Z}nc})g0GUl_~kdL)LMfoUt-L4NkJJ>)M6yms+{~7u@HquaDBPaY<voujmfmV&8OqEc=FgUD!9~EtLGiF6^sMhn8^tS@%xJ_4V^%&THww-)pT3IbT00Lh_$^7$x81gzW#&6FlC!VD@#nZ}EGMKHHP?^{E$6a=k?xzhXZ;^{`y;m)X}2G?RY(%eaoZ;o=u^on7STzA0j@oLBrG>>C@-E9W|Mnjh!!l7B5{ZQ1oK=Lh~+B7Ju~&DzqH>lo&J#Mis_p(p#wrG_VY+$5O?<B?C<*A;B#_Y?K|yVB=H&#(A<+b#S)qaU%3=id|%e3rj2a^d$Dlf@Wb51sE}@ylPz^*Aq*&&%larTBa2i(hn(`&WisVP7*g5r3Q?`}(X3$xk^Z_l-STDbG*xw~{|)r0oAEm7H%hRZITuXvsg-{ur-&(lhb5y7GA$@)z(vFtm6fb*9giI*}P%-|(pZInLkYFZaEJeYuV{*7;n`{&fd+vJW=<v9I}GmHw~Fx*LB875}c~LGq22GdbTB7bA5VddYSD=>8GTOP?mb|8e$>4Hw9MdOua_WTnb|$@vE7D~ajix6a`DT9aLp?_>~vU^97M%uVBbUBEM`|4kU@>kc(2<32NAif`>B^YGY$^NnRz=ef@LrE*@`cX&VOcC}$&ac{)F^3;;+=)8MKet0au{~Di`NI&1Nko^2sGVb5s;e1obdhuP_vTs^c!u2(WGg7C2ko40uTdv1GSH!>Y3Fj;GdvF~s>;~$m^SGufuXsP05-P=i^W0o}oa-1Ws>OE>mv!9cFY^##ae?ba9p*a9t)FDQZrHM~)a@+q^?luC+;g48Zy7B6ZNzrzGk(7Kd1s}c`Hr%0yK7RvzqR;&D`nk(6<=9)U+SlI<8ig;Yb4*PK=Qrj%Rb+_MSQDq@*bO1B-d%s9;vhUuIz`^9p$_Vk4XNkDw&7B-{O2V_>}msa@p6KJIOlkJTHEatFn$i-sFCaaosPn|D+lJJ4bzRw6vzL44uUJdb>Q{|4L6!@!fJ{|MxO+9eui&_>QY&-2<~^f96Ds-_}ybeRrqqpEj{FZkZG3s})tUKi%RbKYET_N99w*_evDs>xHbN;{>jwzO6|et1o2VCLfggkt-$Nxr3aS&n`YM<zTM(ljFILu7g~^#*JIV-?de)$3<=Bxp4oO_^UU|JoLXS_l?ul;<rC9>$oMB?}w%-ze_*of8p~o?08Zt>;8xMB}e7{)9p0ZH|bu9e{`_SgSWlZ->O_<#rvDd{*m<Gv9b6;)iTc|qj>*lKZvh<o5sFA_O?7n9ySr*(nsnaU&DPWKiP^uwvX(e5!a6ggw*=0$A-ixTjN{isWC?*#YTx4U*k_6WYXu2{`)_9O!oY*{^a5A+5P|hlgB6K9@fyjB8YPl#F@~K!K4epncxfr@ha$2FzHJ0D)3qaaXvH$oDa@|t^j9&7bA!@=tp4Ezk*3W1e4AKYv4Hu;#6olm~<AHbOx9-5u6H6Mi9@0CV)w&gGrOXq#uB1g3}Ph3!t;Xq;tWf^TDKxzze|35X7sYOTeVd!KB$>(me2L@J0mjcIY}V=_WAgRxs%<@OE$^f_NKrCzx~xcpJC?LHsFn3z*aZCd~ztW`apGz@)3dq-(*X`QT5%>!DfT_2A9W4d4yvbu+X8T!31{&gSqihbMyAA3>}`5c?pAyCaBQ5X2p!&R|<}v^9qc?Evn8?^UQX*cpAO2x4ypaUj$m?2rBep##9AL%@OH;RxbT1aT08*bh1YJOFk5pgv$9oWCD}xGRF#3F-oN!Ff7CJAgZ2UYrob?GVKFP+PErIl7pm6N3011aSb=6-?R<OzI0J?GFwBzl$Iqfgm1;AnpzI1^c3IZv?R$g4hx23U)<*j!*~iU!bj_4qykIXKMs;D+I9}v^}^z=E)90+!8@-4YdW6s$gqy8wBy&2;yD{;=WLCFlivTFL)?|I1D-*Od1Lf1BWAsM?>EOlfDlg4IYCa9)%!|KoF0FMuH=;t|Jk|!3g3((1GBASl2-a;(iEXFQ^;X4eRHHAa+L(cUJyf@6HHf8)$2AYpk&i)DCQiwX}g+gRQY<Hqf`hHsGEJ;t*&ra4)P`2y`fTDApzf8V(M}8iYW{fX84BLJ-8m5X6I_5#R`{!C+`GI2dz17}^iq4|6&g>JE0tJPt+>_kh}fdw}~udxCqS*FMl;;9;oM2fyuuV|v!mbAz5AQRWzDj<M#btI!Lid}7Tp)f~|X;wk2cho(TMf~P^_pi{w9Q7aBXJPAQO5gHAi2p(?^J#+#z8XS$WCm@JpYV;R_Af9ZFI_9u2M`NfZxH+^L)Dqkb+!R4vA8G-v2W<eg09#<Z1_)w$^=<-f2(1Hd2)2SY2EXag3PIe0)^~_S9h<uU>AyVx{Akojt^WZ1*I(BDXG6_jJ~h|+=RYDshSaC?HaAy?UnC#VlT7&s4q8Ph'

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
