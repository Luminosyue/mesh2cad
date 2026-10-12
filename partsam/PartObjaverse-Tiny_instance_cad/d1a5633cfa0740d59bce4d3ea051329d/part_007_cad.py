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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d1a5633cfa0740d59bce4d3ea051329d/part_007.stl', 'relative_path': 'd1a5633cfa0740d59bce4d3ea051329d/part_007.stl', 'source_sha256': '48c8a4ab46516485b3516bd46fc877e2b422ade5787d73b527df1abf0c5e240d', 'input_faces': 302, 'input_vertices': 200, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4821814000606537, -0.4580686092376709, -0.22558294236660004], [-0.33209556341171265, -0.2945225238800049, -0.12326045334339142]]}
GEOMETRY_BASE85 = 'c$}r033N^88iuzRYo1$0Y@&@JLQ%6iW}zWwp^}}(F_TD0QR<i)Lk%g4P&OSx8bi>a4cRF*wrCU~sh*&v)zX>UQg{E~`yM&xu6x(I>)x#Ot@p{B|NP_ke|sl{^(k7cs)nz+TCoGyKX6phG!<pFs#=0GZtA#bXMFJF*cnB%isGv;kFM%FI5aH0h?bze8aT=s9~~FiP7mxbx=mn^9ymHCZfacA<j9z~QBLLeh?*GhwEg(8QL#?@`v%RMH4D;PGz`*b>;L0dX?qGrh5V~owwn7VUsP&T?ewWq*TppPwGQJiDRsXv<ET<cYLfWI>9W#ZYjj_HBWWDk=ai84T4-zWwZl!({<!mkd_H9&+CLj0zN1K5u6+OJgCjBzv$XiGlr_@7Blf2Fdd084Qfd|aDg8UPXN&KibV+=@WXCV%^VMFG{>_r9XkY5;WocjGHT1J^1^jc<G0zMa#@!kTKV-~#X}9AZ+Gh+9-zXb{^$uM3ndqGmj2k^r)}<d=^NGy+rMBWbYW@a4H&J~3dP|@7?wI1zzpG*k@wE^3VE$jvL;G)=`?R+fHpP4b>tjB5(Z9Cv9@;mmhko9=hxW;JrM)Asw)n2JboAf)7isU_TT^^@@m=B@p|#MyadC{RmqR{0jFk0SJ%7oU{?E<CJ|w;<{Wu<eFTQ&v^W@vFrM)@lJNVg+u>UvjVB8D0#COzqPR7+%braumUWMP)CHdf5^8?!7%opDZorQ6id@R29$z{yvxC?pm#|_LU;XM2)P0|1Dz3{`%q5sbtiSO|H3jWjs@G~o3k#(<6hd+Cd_^!3T%DVLF$8o+L--Z8xdER`dtk=D0dA?7ccW8w?DZdo^u<>4w?90LKvd_jbC;A!q`9<W%#cc7<Mv8B4|55VL{Qe8^tp_9Xz3+?L9fxr<`=R|`XQUrjQg`f6a&PqS|E2h*Hp$0-d|x^qJuU4vgkaw;-Ij5+^$uxo)a#z_eIMQ1BXGXcyJ0?&-{QWM8jC#4d@|qrp6binAb<AW$di7W_rd+xJr4VvotNi*Pqor@(EdzLp3i-}5P2HwI3vC>_!icidBGCD#Hl>*du=7(llJb9j)?Eb=!N@ndYbH~9<U$t`7s~+oYf8ce<s7He``E^ZO3l(|9Lv{v+_^kyRUvAzFvKl%-=orCeEv3N*?l}hO{?N!gtg(#n)=)$+*VRJs9`cX7SC3-{IcHz_<FZ!~FYRz&r~sVcZ96F@OCo&gBjG`l6MXXFB%TIM6`qp{vSbjC-UT^1SpRjN54u{ArhSyz|6*VItPW`eS6I$$mP9jX-<W88cy%`1-X$Sg)s^G+Zyf_Ix|ce+lbliRxHagJ*sE*Hh2Rxf{Fcq90G)a8ALvSN(A=3s2y_bn7bT?zs6B`uEh0XQGiO6RW{z9d=}8BX6Isg88#<Xn`*y|F@LKxPSa2`)sY=kGy*A3G~Cdp|u!}b)}W`nUCw2bZM`*`}>N|eJ|K?N`C(7AL1MJf0q8;$@OI)T=Bo*JdDAp=WS9^H_qJ^-)wRUd3fI+=l=H(;(O|nmHvXv$7%%MOvC-vKkg~*&G7HU_tZCQ*$}jk{04r72iPC;Z5h|`JbYK!S?o`ZE*N*{nJbtV>;L4}aZiV(WBw<ik%!k~(a&)c`>^LB>Oi%!$hVNqSG@Dn?6UoYd_QL`=98O>`gW=q?p@0y%;!ox_Mz+gEcyA;71+<AQzTD}+`nZ1wH^zx4`21h^KIliKEA8ReVj|r)!6@@3ovfEwsOAiADLGt=A%99r}5nPa*pozXQMsqp8NU@@%5mYKJ(PW+DkvKg|A@Wwhh6$wF3BSC%|{M#(n9%8~HOU3jGh8hPs`WBEIz~0)BRLX>U#X0)CmH@NZW^`;<WB&qsqWpD$+MT<V|1KAi1=dED8Ac^-ZW&k?N)+VgqjI8_n%u}piP^K$JQj(w=y3Vyu<*tal0%s;Lv*0uGn<dtjWKX6`=b#N|UhM}L#96XQ8*M{GBKlWkAWa-BkRSV~P4fR25eMR~)CRIniCH#cEEi(@L8Crq+yifYkbC#o@d8IJVTEC*7W{c52vZzo0j(~9Z6aK<;i1pBFaN(r*b$-9>-CqB7I@$-{7XR^cVe4qwAM4r;@jcH4>%LQb$D0LsPVl+l+8KfUobv_h9qYVNc`)*-F?>&*cO4ppeu|$#`$V40$3d7+;%Aq=&r5&zBKiqAgmtn0yQ>etJWK8t-yFPB=HqyT{B#$jq5b3usE0+rM!q>yv95yg`1ziE+?TqW@qNHrx$nk=Wc2fB9oo-Ao@%E)gYUN%<2DSy{kr=)>inWrSl90v$Y*n&_(s$)^#2I?<DL+K_l<iYKKo!ghse6Lxn0rz$9|aq{!w_Yr8LAjzTF%3e9#ok=X?X~TNB(nBQ+NO#b<r?(>OgGc{TqT%%Anvx_wmgL~l{=vUi?qKQBEl{VemxIkK)=za2h_{e2Sq6P<{BNbZDn^{I?;501s>%=Y4&QAP3n``AybR8zc{W<J8_{gd(gQMn+jx7tJTtv@62dq+VZoLAg^v}ZlEVjf5xHY$9BJSe5(9?kv<`+4Uoeos4<jB{CV8~M{K5A~XL-raY;tjm~n0qt+TkNUtm>292Z{ylYm_^Y^IMc}*ESHk{xye93<H%`HyI|A<;8}l%3^hxy3`frv?kbcYu2he}VMAWxTyr+45t5k<Cy?sZ)PVqhU*_b(6`ms)I&GkNatqtC<j7{*}FTuBB-@~~Fufw>k&&H;{;yZ3F!~9u?O|1v~JBu;yJ5i`hp(pXY8!;2_i#PjAKd#|#$$E{XIIK4;0{L@r1@3jXNx9zl!mRtrG5P+Ik?WoR?nj%&H(%|=^`cH%er2(53%X!k=l5dV&113uyE|haSU)YJ1lD_?1N=_+G5?fkoXh%_xjy-PZKjOt*wQrDC!cR6i0=*!#=2Nnt$;u9KJZ=;{IBs|<hj?5hyd&l>y;}f1nu|hx!(7}9X1~OP#*r{I_Byr?HyxkW1g&I*8J|`yDHcAxktv}F_{0nGHA~_W^`#I?e!m!_nx}v(ng_w^B(RY>yno9tN7-Ci<i9f(@`wwn78lA&&U4OLzlesP_N;SeXEgj$tQo-6oY?$Bj(Nerq8;J`txW5`tj7aoLup>>u>t@KmHrE?;H!Cb;F9-C%(R^CGsyl4dc#9&GPmg8=IZ?_RakPyoZyqu1Cwz{<r=Yy!$Z|D<1XsJ^grmt6XQaPeMQLo_<HO!hHVv)-(J@xozd`%(mkRt*SOU%Ii;W%9OOH{`)_@jcfT|{pqbmv*!QrpWdSFIlN>?D77a!l-!EioUHU2aw~EJhT>Y(C&{(Qm8s>)mB|&T<;WGtRjC!pRmuL;r^){0#?)uYjmhn(&y(Ac`%(Ll`;nbggX|>7QYVpP$<wG)$kWJi)XC&H@@Q%_c{I5{HI&?++@9Ks+=_eMo}suQLvd|tEplyg6>4R26>=qN1#%^FHELCIHF6!QKe-OM3AHh~3AqEc9k~N}AhjQPAbAYcNghLvr^b@w$*)kSkzXNCrN)t`lE+a;lgE*VQ2UdIkULV_liPEz6}PpcwH@IM#UrR~$Ro%j?HEPvL~TRvMAjLKYfxL0YmjSF+me;mCD$aEq?RU^Bo}2UE}<a@l-8z})(Uf`G}l?0eR*=MF4ta{V|Vo0iy_o-uRRRs9#5str-qZmxkvLEie1!^WEXj!*FMf;C|+R48`Rm<QRLa=2x=#C1i2ekCwC*aWGH@uT7&!qxj3~ZxhD6zI74v}YEg0#vgb>&AGHM8k6g^_oQhE^k&BT_QLB+lk;_o)kjs$kQ=5?MlO5C!WCuBtI*=Smo=Y7=o=aXrjVCW5ucp32UQJ#~ok~_ZpIpz5AUlGoEy#oH=wZhkO})oLXHa{PXOMeQgUP|{rx!!<06U_ny{Rq8y~$muLF6vv&UUP@<6S!rFcfD|)5uxmZ0c@uHu*3$m3)}IkNOUIA9)RR8F>vkf%+;rf!vq+GPy7LIqHk#=g5tyUCE8e0o2aq&fJFpYCUoQxw@wQ2@?7gwI2B?av(LB9LzHdqz)nnlAGD_8g&tM5P1=KD|HTeEBT;Sm^TL*iY<oX{dRmveVb~MmChi)O`cBeMOHe1Je@pKE6lT*)LG=2<aN{)WTgklO81c0k&~$(l0W2}lBv_l(>aFXBX%6M;}}Enaq1^zrJs`b+Of-yHyMhPs5{9?<dt@8vSXDUA2AeXP*;*yvV8_)r&f4(c5+QSImRBwF0OAE=ky_CFVDxKW>WW(Gs#=1Z<4o=-(V<SKusbqAkU+&)C!+Fie1!ITH$j_@qFqgt?;>~cq#Qg@>23@>SnF5HY!%Nb1ro;bu)P}c{}xE@^-SPRwzD9J){-Z7RA}rkF>&Cq&SP3LC)aWD2}mXxgCiN#oHK))jgZ2;eHOME+Q}D&xcc&lZTUEpvI7!Qa#UN#hz!h;s|PtR`^U;Je!)R6}|%`dY!f6E!1sVVLm8U`C?HIQn!(}ao&oD*)iCT@pim##|L)2#ZbJSnoeF%-bmd+-bmg+O(82?OWr_UNPV5WkUW+;o;;p&8_Q4}W=D5w2z4+ygglfwj69S)LACEw#II`6|MXu>3cp<H1;^(<oc!x2eSban{^V<RUypxT4(n4~z5CcNLw@p$RFrx`X#WJ*^UN~'

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
