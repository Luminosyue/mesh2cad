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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8da95b178bc641d892f296e42c0ed8a0/part_005.stl', 'relative_path': '8da95b178bc641d892f296e42c0ed8a0/part_005.stl', 'source_sha256': '6d383a326d58e42b1d47ca95ae29001eeac0b5cd7d4a28177313388ab76df077', 'input_faces': 416, 'input_vertices': 234, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.46064823865890503, -0.08003942668437958, 0.1155351996421814], [-0.44001251459121704, 0.06820809841156006, 0.24082142114639282]]}
GEOMETRY_BASE85 = 'c$}r033OG(9ma<}NDvSNl^}@*LRb{p!BDO!i=;r<RM4;|5Y`aFE^>hc2na$JHi1My6bPG9#3jiiXh=c`yV8O!lucV}U5fT-tIgc`-RGSlJ*TJ5IUnEeea!p6$#*CBg?EUGtWvdsP+uXU^QN?%_=ZAA1&Rh@c1%KI+_;#Tk4%f7S4q@$a{1+Y+JIsGqlQ-!v&Dk2@i8;UC4_Yg4vUEG64p96EOvTAV#1hdqoyZ}kCA!rF;iy7l;<-ij){*cf83&7`wp#x+lRLfUKsp8e%)2R1z*nvpXJNFjF_C-LwfJ~PW15RMfKC=W9uJvN-E0jwBS-LzmdPune#~7VlBU^aywd_)bfsbna=z@n~Su(6ZzE)ef=P@(|NolMq6)_oBQ|Ye=E`E*vmuSbaL}`SCAX8Yahtk>pX5_d|wAuZW-T~o&WtlXO7XEn_FgY-<Rxn9`{oFw|(I%{~;sU`+fQII)N*le8OABT3%P>cIZo`TAn&0%~_wcv`EX-$OHDB)bi{zTb#$=9yzY%`&4dinp39b?sZu^LtF3m@B1-NUthXmw=>6>Z<7mi{_r8HpQZZ#Z8xu>@85SS@1T>%>ixL6W%T1q?SIJIzX<x_vh%u^1|@m>_vdGBu5g}zU{A4@pH;baIl0ux)z4SptRio2ySe?rNp1btX-?0+ZM%+Z`8O&T*H@NlxqHqBMr-Tc{_Ti!+IoA>VW(%?oWED)zH9n?yX$Jzb1i-Uq8s@leg9U>4b`*JkDCj#pN6yb{s--=xPLb{`*(A*|6g;xfATx}ch{T!ySdrFo16W+^UeO<-0a_-WA^W^H~V+joBfmD(Z7)kvmdknqiHIyo~ifm=Bq<foc(XjF4pojD!0B`TB_v-t2y@>`_|kdEkC4kvGd)NT0Uxry3fqtb6m?ulh<2TrseK^CS<I(-hcmzE7R87-|koU8FT)3<i>ovWTDfuW$yok%6&WZ{rmDSss4?A+*}y__~NH%{oC2|)qL~*@8;(H-_6bYznh!)e>XSp|88#H|J~fY|GT+)|0loW{_n0g@Bi+4^ZxIyH}C)Mdh`BIe#iaa$StEE^ZsvF8t>%6O@|$FUgz9PK5w2i;QqbNzM|*kd2>6c&2}e$H!WAo&o54`XuZh(Ws>uAY0MWT*XKL?tTV1a%hO*`KaWA%KGO2CM$5Hx;^qO<S2=S6KP=Yrn&gWTOSOF74Rs!_rWa}XeDb}op49SBAKdEX51l%$<rh_M$Bik|a?XRbKSf*bo)hb{UD|rP(+qV#3^C?+R=H)&w{O%|=i!R6|C{7{^!;1$sp{v^=*OQM{n*bo(awo4f1o-)vlqVYJdf+*=2@FFbDY25G`+x^+vL`^(n4=8&Ng?>oAqOcPn&Z_<-YE_inP4htv$}XRyldz{7R_G#onvM+UvUKbKr$sZU2o`Zmk_uqOEU!Gqs}mqM6Fg`C`}jc*l+Xi!7Df#{R|iusKe@MnB@F%7xj_Crg%i&%ZzaxqXWF{QL7izp&bwzrIM{=U-GVZcixH^8MS?zjtb6>-#)Fo|JS_%Udi}=U;qvT+72%Zm;TDrseKA=Y7ZDvzzn2<IijNQ0M=bzv}bvR=H))k36LQ-C^wCc5`F@*4snX{m|&g&3%8@`*GjD{O5mo50y`Et)G8#D|)DN&PB~d1>QWE+<r8-(3{)ee0k7$-gk$5+8lCU|CAzaecWz!&KLYMPutH#mD^Qvi?#Kfe|tixzMk{%3k)yu<|1=UT1E5ittvO?i__O;I&SP=l&IV`_AkClO>iCu=>3SVRc;ymh=|*ZwDa%gh1sjL^Y7*{Z@l6>u69x1XDoU0bER57_oWQyu_)5_IZx%*s);AH{I#Fe`G4~sef@To`>r)9({lIs<e$$T*ZOqxHPK~yUP+z*H;nm%Rc;&e?bs)rb8egapP+JK?B6%OmUEtMqaS~6^y53SQak@5vb}oUV`p-_=ii^t|K%;`c`<7XD$4D%dkeL^&pzjz+xcgG-rOSh&5bMa=2vcyQ|CW=P`)=0cJtKKVr{;A{wpue^XC5ZfA}YT{jx99Dw;2n$&LA9z`y1=`!)72`l{SE_AioBCOJJD{fHGRw~T(o?0)mT=ii@q%FA}vmwv9zx2sG&;LIQUg}T0Jt<?MGjH%l7a&xO}r@Af&cNBPYLGD|=vCx}exe=r8SMzTBwE5(ss8^Aemo!w@<%fOw+MHtYh!}03{_7QcEzg_#uh;5gef{NS=@rcvm&lFzV&%{m)z7!Sf03ke-*J8a!u~Sa>DlaOh01NCAJHW=(R;nDmf<RIS3~RH&8_F2a(cFYI$WTwC-+4p7kYDheUR!o<bk8w9C9l-q{y3(&Me;T%;{0x=gqUWk&BMS+I;u-rS!;rZ|?Rlrmff3i}oQI70tIFBRA#?U!v{g!TSD1uF8e6e{m(etJA01k7()Sw$YF9^_=YQKT7+wIxG8jrjQTIRkQq$*fE}us)f4_ulS?txDNl-N7Wr3>-7JARQ*o*9*WDAgBQWl55YO`I{W~<4t@nmUXAaASHr9Dz3?hH1>X%ze-loDS0KqN@jbBgY<MO7GLpOo-w#Va2(N+HBFU-vTd?%E;Z!&sKMbeC>yhLQ_`C21I0JtN&VbYK95{!5CC|iX;OpRZ^gaVgo{q1Er^8c`<jMFdcrqM^r@(RWM0^E25uSvvgeSpM@R#8!@HBi4JPnS=*TV5|0-g#dz=?P|oCwdx*Tb{nIrs*64m=CbfHUZKmZ$ewNb(Cv@(6qeJcF)BAj!`m$<N?Z;b-8X_+)q}JQ$CI<LG@bk~|1W9)eGTC(-*5BzYJ<4ITzRizE-n<Kf}(^LPUMJRFTD!in@AjU<o4=fI=j(Ma-0d=@;5u16xtzeSS!;UnM?blne0?u$PI_l0{S$xq=!;iur9_+WT2UH3$ipFonI#D~C7!oBcea4)zI{w&-Fei|PRKMhCX&%=>$e>@uQ4-dpg!2{tad^8*d55PylBk6hok{p2~cf<R^-QX^GU$_h03GWT}rt3~fat9>29o`e}N!RU=<j0WY_V|-<d$=Rs3+@Pa#{0mX;jZ}8a98+oJQ98!?vD3|yTd*3fp8Dl!lPgd{tZ3=9zfTUAHiGW5pV>(w?>j%;$7gDa0?{4Io=6w4u|3$;86G>ydB(*-XB7eLy+W$@%He;a5KCk+zbxGJHugcINlWwhg;!~!>!;pcz3uvy|+P<A4QVe;udVtZ(C3AZIR>$k>nt}HQbu6gOKD0@D}g`@O?;fL%ccM5N?2n!l87{@0AYUgCy6(L*ROFef(j#K723U489j`gonY6;QR4#_<p!C-U@CEH^JM$P2i^Zqi|C=7;g)=rR!iM`EDdR5D$Wb=r<5az6-w(z6-8_Bv->5!VT%S8j@TENv?$716P6tUQhh`CAl(QAFfZ=m67DCNOE<&5!{Hbt0T!Zk>px<W4JM0*FutOBgu8}rf^gGt%D@j#qWme!U1?797v}Dcn!D)-38!P;41VLfD2gAMF3tEuFCfufY*d;^1TJ%wc*-)50XDE*R670z;D18;B)vj_#Au&zY0tLBYXxvg?|R0f=?pJC-6(K^xwlL;1VRc6u%5h{{vhKmm$fg@hh<OKf$Nrv-oxREPNin37>~QL6R@xpTp9>fG@(o!*9X2=w0%0{A2u6_+$7OegQrPAH~nX=ji<?lAMnu=i;Z}Q(S{wB>4j*`91sue1dE69+G?nNq!$Mg-f{x?<2_{BFTC9Y4|j~=OM{HB)I@T51;266d=hTA<2dKMff897J7OwM3Ub?l3&L^hF^zw;K$${@N4){_$a-<h9qa=xo{@D75@O<3crdZZ^GY$H^Ce6Bk)FeGyXoj8Qy|_2ycP6;d$^jI1Bf|S@3qe0NxJo#6N;}!n^Q7xR9=QA<4^;<YfGHI2m4w?|^sE?@}arF`fx8h8H2p3-PV+R=Qq@Brm`>!3*GdNb+2KBfOEW=OW4Tk>nTgE$|k)ei2E22}!o`EI5m<Z6tXKz7t*oC*ix`BzPIV99{-bK$2teWH=U%!I#1@@OXSNyqK=XBgy0Nh446dEWQ993y;C)!BLTwDmSR|pZ=@suV1$FhUxu}ujVuLj~%_w++RM+{~=^lWHtF-TK+~`+4<1o3;7$W_&1-*LXH'

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
