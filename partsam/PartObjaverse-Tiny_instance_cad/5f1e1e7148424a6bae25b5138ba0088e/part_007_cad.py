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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5f1e1e7148424a6bae25b5138ba0088e/part_007.stl', 'relative_path': '5f1e1e7148424a6bae25b5138ba0088e/part_007.stl', 'source_sha256': 'ea4f0c03bff978d4fef4d7d1936fe38aade1756c79516ff484cda71a684ea034', 'input_faces': 230, 'input_vertices': 173, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.14346155524253845, -0.1254376918077469, -0.24400323629379272], [0.26910701394081116, -0.05093882232904434, -0.14296585321426392]]}
GEOMETRY_BASE85 = 'c$}qK2~-u=86Hq$M2%RHii(b6z&!-wzC9HM#07UTf{!Z14Yh!Klo3V5HSUU{gW?8gjJpzb>hjcz+lfh9o9I*1+9n>WHjUQU<<9-Sd3ob$&*^FL{O9}TyLbM3=fD4d?*-%IDpU+m@Y6_f`-lJSxWA&9R!s>|rl+K5jvtef(R%XKSw4!t)Xg6Y*YqFSFFwIXnXb$U8=I0bCOxd98rC_reOOC1EOknHW_t4E(NogLrkHx~<VhJRLeChNJT*l;H+{EVWJ@)&Sxa@U`ak~oi76P*MxE_uVr1UFGXgbN7ng~Sx`|SEPWbC#`CPP9>P86l&*mPL{hQ4$mpBo+7Bb<OeE#FzD<<kQpu4}^1wAm}l8Nev>>t(fxYUy_N?p;QJI<aemgC*b#ki}XE4`ax+-~(RN_`V_{qjiod3^fUa@@`Azk3<<Cx5>z$E~*&dcr=;XN_CxS|oHM@1peYs2m~Z<Lp9x#leGeenYprZ2E|d{ocCfgsvqWJtB2qhm4P&P5pYh99KE#gZV77_cvTw^1GBB)PsLGApK@9l>U`N_IWD5S}x<Pmc8b``WYDqcl~YXzcU`|c;LCqrr(Mv@z(WgvFBxcUJjG<acn8MAiwt!^}i&Ykn?F&Q+}7>(?{yg22)SUaor{IyY#Bi6{DThwbQ?q@ihFQYsbDnj<^lM_x5G~Ro4#5ag#>Mag7nsjWyR~ek#wpN?lKauAX=%zt<R5igih$et#+AmJ=fTyC3g@pOu|XNk4zyjCnqX?%Xi2O!`^87WrR$H|AOK`%k5xpk>I1?$F)2Y0|%=>FIN_JsP^cf4f{4!*}v|_@kfW`K5B)8TVv=V;OX{)onShmU|TOJPh49RsnHqbyCh>y#d{kv|FyD;;Jb9YiCL>*z&EpCgZ6;g6_$aCM#r~C}E`+yz^O0D0JC$=Ch^i!>C*NQ|pCYxAKR&G77q<zP6#h9GRu|`P4#vY3HC@d8=JRT^J9jTlv2N`LDjR_g8|D=gyV=T(<s)`<|8hLFmSmjc25u{4L^h3A*#)J^5YQ*DKC?>yF(4#ooI575$6~I4#Fj15ro8{iW`XUyOWy5HHu)p+VP&zhy|B`;5At{dbnibysTS$aQq*4R(3gozWU~r|zL{)!h+)nJ4Ng=vLin8K^tAi~X&-8;H77%b{C!r#&1j<KV13#N}Og#?u6h8vxy^J4X)cPOS^wsypRL3F4qqXWbcfP<Q%`11|46Qc9P~`RK2pd+Mm{6za(56PI_LYI$4mUB1w*`qI{=$+)Re(5?E?{7_%&RQh2Z8O90hV@siX>L>wq<U9%8vk#nKgFN?7yzHGPj@8T)>Q<gux-%8Jl@G=S<b!(-bSr<fuaH0bCFoY3Xwk?M{SN&wPqcFj@x8uDm%Z~@IrAsvb6e<E{yT#DVV+gKy&~6leQng&^3}+PDCo|uu~^5Ln^>1b=*BP|{a4jSeI-Np#4WQ9^5+`;mpwsUZygIikG_MSyye)po1MV-KBsP-o6WJ$xWgYok9{fk6JyW=^xr?J+&i9*zKExK9=a!<A2FU^Qn%uh^9Al9FX_jMXI7`{(ofB_a$B9gx{EpuOSAW%iTJw{(`@4^<Mv*a`aI~K_+P{R<1S3I&u0$yANMinR$eL3nO6z-uFC$~)3Kl2z&Wd~g6{Y{9`QVL0QHp*-Ff68`bXu+?{)tUx^ih0_Ko8&<T|R)pleG?K9>F46ripH@56uX8d&#vml4l4(3QlCIA^nZVE%)k>wPMHBEPpJ5Azuc-F<yN=9689Jn8fYe3!NVH{kth9CXk56@>eea|v~8pTCWB!MVcT-?)SOlDn8X<FDlNyePAetNn)erE{<OZ^Cor&4=i3-S<{E!1^|!&T~+^$oo=r=+=3s4B<W>Ztt($y@Y#UU%P)tZQL6@I_tutKdo|I#&dB#?nN;RWFG1j{h-fjE#t3*j)dL;x>2|qdHdrq)ca8A%0CORE)~DQen?%<*@t^eMkww}A3)cBEX4ll+ZJ)24c*!HG0u_PLoz<jxzHVvKDaMMzrwz~j(Wj(+z$_wA)gC4{~P;p4&IKyx->4lVOy7xT=!7up8VOx{E1+H>)fx4b$55BZsk=W@8MnT{<R|hzA(Vv-$=ndN=<!jTqo{P&MDNb^^HM3cy!*2JbF5G&%Njt_8DcG-H$dJdE#6^-O9st*e5-@wSQ7~FMF+j-G*{q^n&M7_v~W>u<to<LHF!?w~)8ayY~J{JnkpzQ|O+3EROf6m(;C&xNET-SAFA!O*g7=f3ESu=12R-=h&}8p<DaBR*rpMAJG1$cb;fT$P;}ybWc97LO$z>(6zOX<o@RP!UuUW0lFt|YaK>>CPMe*?PthaWhQkiZ@YYo{MiWI+V?a+?0fD_oG14^hx;VzWheb`UsZmOebv2}dQ4T^x9>;d-29mSS&v%b+xR``2)~#6u<{W5u=5IZ>%7qJ;JnbTQs+LPL=4A$`y0lGb*;5yU4O^;Sm($PoFjU*4j9)uM=ptTB;NK{kMdbx2gg(unJ%n~5}>3ed;Q776lEC@|NWml#=rMp{mCODGW`GjlgHa)4nG&xnb?fn#GeU!i)M0PVg>R#!h(eP5o?h578Yfe3ULs5BVi4Ny+`ao9z<V_hz-fZ>9Z>_h`cL#6yG1j{)4DBA_kGSrmrr<uH;?FdlRF`{rFBD&btHk4xC$WT0{D1$i7{Ot;t){S1n<~_#8p3MgAtaAFT?ty265mRVDh9#|euSHh?&gJXDw}tRt}<c`Vxo5<8LybBs`;O5T)X^&ke5_aKiYhLXR-ce)XKkar`GBgT?f<vVpb?{?JNaSm}bl|EGV?M8fu-1Jj}&qIX`;o6!wf_wzq!-+MNpK{84zY?(`c>uq;rLf_|rbK_Q*qHq)6Me|5@wpx`ki3tuXkiXwCvpdQb7D*KHp2P}3nTU+4<oO~e%0us8a0R4cqR|wJAuS{<o$)U=Uf6fZXmG}c_4WRF`7J@?}l)0{W)HLwwe50VJ(F96c!__m$2@{p5#5*$K=(8)f85r*nqqR+sr;~h4mBGgcw8KguFhnJGtf8<h99L2^%Rafxb<ApZtBcw;)#c8sB_hA-+LASXd;#sV2X<0kJ1}1M<eiUgW*_ZexDSV9tFo+e|)J*oVT#5L3uAgnb}v4*3K=n>>xri-m3Ha~j)BZL6@I!d4SkkeltZ*=I5ND&h?CRpiTsEhVNCXOI^O+a;`kwwu~0VVi|%#9id3WwG7FWb$HRd-=YJJIJR9%M~`6xPv^MZ4-%;y!d23CkopnY(BA=Jdrq$HkR66_Srz(L_UvgV~HEcCv!gYh<nK=v28wa9{Fyz6%*%^7cf5SiJQr@*p^IOPd<shvWNxb6WOK_v&f6swu`8d7ja$FX%oG)9gO!<j<JKh$ZK7G$v(N{i-<GH7m=?NwuCs1IFno#wnbPev4q?yY@M(LM4jBU9JZU7L|!Ot8{ao^4|%4rWx`U4d&o_FJm)Z;&*O-x<i8NMQP@IaA-QSUY&UT<`8M`hOWa7F&9>3RwdARsPd0HI`8c*MBxaMBu&t1|kbDc{lTTbnp2M~zVm|pe`pO}0As^4S1;iZkQnu;D1>~h%*J)mHw6r~p_Y#h=hrE=}d2F9b%p^B$7Tfd4KN7ZvIGs3)JU-6HH=x3Q`me{Iel+vIw*5!s>u=hx@7{0zAbfc)^YL+&<ayvL{+Y=>%RFtAe*qIR{&x'

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
