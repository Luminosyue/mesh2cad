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

PART_NAME = 'part_019'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b7ce14aa504e4bbfa7122c444150999f/part_019.stl', 'relative_path': 'b7ce14aa504e4bbfa7122c444150999f/part_019.stl', 'source_sha256': '484f42422ca4e4bd3df6b4f77194b57b6fa1b2fd31c8d534ff7c8f42a0212e22', 'input_faces': 366, 'input_vertices': 250, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.14888280630111694, -0.1974746584892273, -0.2560144066810608], [0.10612465441226959, -0.15095074474811554, 0.23268401622772217]]}
GEOMETRY_BASE85 = 'c$}r033OG}6^1XMmcfDyRjepskcbQ-fe0uh6a-~5-~b6z7?O%InIMW2PtaNwS`b@oZ8eJ8s32M~3^DK`B!<u^q6Psi5d}o0#R=<bUF|t9-#)!(-`BOe+N`zL|DAvDx8Hf^o;$oGStA>r(k7_?=@5*qJ?-ujX9a<c(}Om_!n}e7vu5NK_MAI^QG?)&gl~UDSB<%LbXInQU}123>dd^t83m~WQc^F=@0Z#=B{hFu!GeNmbEnQLn3-q&Vbf+8<{7{6`f2m?%=m)deS39JN$c7@<<6A<@u#VoLTq*O?c0pTFIbe&V8rO%Rx?i=el6^$luoI!S{Lj~_(eJ65`HXwOrpLh`$f;soijaApSki0uTR|zBX%b9gWBem$^7`hqVi;Z(ODI*Cf>ip4c_}of9*?u?Mr{{OaI(?`QH1+(#Ne%<_9Zg&djjm_j;-Isjt_*)E9N>;rDsE;S<UHSd%Z;SwGnLO}W>HdhJVn?E0t5z5ZL5RVVdVSJfo??3wHLr#|9Kec^@m$LE^%iS?};m7UlR@m&pkKfbVjKfM2SJn{N<Co2;3?4OgU4{kl4@MHUi?M&(i%__rwUB$74pEB^fszl!#(>%ZK=A6o~A55zD-Zv<`Eis>9X_eO}w?&obOCRy$yLWi=ls?X9p5n(=mBzhwko~EAw?CEd_NVe?f7azc?azN`-`!!~%^yGb{$6h#WIo!L`DkC}qkT7@PWO28iIwlF3Hvf1@#7<wc%RFiFUoi4*CTg%>o4=yzRX|yGJoyM{Ka?kZ}ojuGCz0Zl*(j&QB_uX(moAmmW6${4ywO9UaG(Ny1(nA`pZ6ytdHzZy*~Jn^}(0*NjWgWKYux1+Lz-MbRF&=N4Z`pU#?em3y1jE0s3oS`in2?9E>~s@U~=r?8q76dRaGJ?|fD7u0MJ{vYv81?>`{v{?Wc1U+v5Bjr8I8im&&N_H}=~e<FS8pZict|2T5Iv@gdivu9KPxKOWsUGI*|?U_#|^J9;ct_}O{xTtzJe^u{}i=K}hN7-*Dg5>*0`?4SKBl}1D)Mq~S;I^cnSNU%K_>s@6e5tRyFSaeb&Y2HPufP7|yYr6wc*N&E?)tDk(kJEFe82w}Q#WQL^VjSx3;Xi9;$8o~F_|CR)X%GT@2mTZPybl|i@f)ZU3!20eO7!qzTy|R+~)0PdH&Hp>yWwg$*tl3?s--D?s--D?s--Da{Y9^x;|?^(qCPlweRj<m-O=9*WFK*@9wAKtLvNgr9SuT&1K2XckRph<$QHMYTrHI4nE!MBl{uZvmczV_D{r@`h9o2oDrVCJl|?xo^QpM`RjV|<vdzj>h-DH(|LO`Ke%^#rRU3j(Dl-v`dG`h8^V3$^G19*U&L4I6Y*tz);!?#arbNGyW=IkI=<SM`l2JjD_$S=oA%xPRD88RweOw>mW)aG?t4Mb{_3QDheb7E-+f<D_0Fe0e%*4fPtg?%wkPxBEm~KGeRuy=_2Nr?=HR{lI<Vg&zFe>H_2-TF%wK%{c_Y56*ZV)>GoRS_LkT}}z12STMWx65b>n`aeYszV@77J#yZa;c!HiZV$<9aZ%lRd~KEB$Q<0Za6zS`II`h3^E%qO>7hm!ERNxk;n^(1|4!jIhdwJ-bUpHsch<(@Z`@19TaBhM$wm-?dD=X&cb*Pn>b^+){3eo(&K5BQP&pnP4guZIy|u7@k`^w!zkU$jqs?u2FDI=kbgd^uk66?^>k=Xo;X^E@fOe*TR3^8DHCu)ojcd06@G`5Zs8AC&L*1Ab&bC|}n{p3jx<o*&9S@zzb&KjO>&dHXB>ypZ3gDc?Q+kD0j9TL<}mr+jyR!H;}j(7t?Mz>j=i(7vjVeBV^Qn@>=`9{T&W_TBw=+zXo%s(!y0@#T8n<+$g|e%8Lbe)c|hOJbj@-#12l`sY4)<(6<CcYL+a@r_?S!RsUQ(Y`ysHf`{H=^ydwU)Szc?|t2RD&L(i|G2Q!dtcel%1_j1d4DZvzNGP<;+8>Rqe;*v$e$MaQ-L+@k7)8g70l}MU;U{dEj|7J{ZqkgGlw}Q=A!f9pP9JN#B6j9{Bv^i(b@3*<ZeRe!}pP!gWd#>H*uYb)@UnusENx>oPoB4hf;SrIzCj_ihL__LwQ|m@~z29&++8Ple7F&6L}^kqZ8qLa+A=>@Jw<!=p;Cg+(a}7&NeX>o(NAyr@)ipN$3Q45}bo(!`bw*yu`#(@=M8CzK7ftbOL-YxvA(BcqzGTbSgZ=#7|7LK%2w8Ok5n;Ka17t58+<aU5pM1)io#IoLnzn*MfWta?*1M`61*i&oD8~#7Oi?csjWe=twx1+!g2ucpAAY(JSELCPu@f=_5Rf@hJKT4`V!xKElHp52uIayG$%5znGlm7`ajCF!*kAqtQ|DVsgXL(QpqF-Ayz@o5Ed8q?$Ml{Q=yCx>U4BsIDpbrsTTtx@P2?k&~W1$oC*;`C1cWO$<c)!`G0z3>^q(k?V(E29G7zAMFSCH8B_-OdsJ)#+mdH?!&kbeT4fm?n@8Lx0+Z)ei1p#caY0O`@naS8;oYci^%mw2gBV=To~9JM!hzMJDWJ)#3|^haA)eyN4tgU8k28Kt~0M|LcR$(>Di5ZH*%J*HgT1SOVLZ<apVS|m%?MnrK1DjtH@n~ro(9_GT;pQ2oGXBh(5x-8TY1-a2n$@dRSg);ui9^kh6Rnxj|@e_;zv`=pgtOa%pG=+}^~GO*BFq!fj2Q9n}9=Z2-5W?rgMusIDRThUD7vx<=$1k&~Y7$+stG`63fN1N-<<uPJa>a_6BP;0wr|i=GGfB$tAo3wJcp3GPH6;dYGM(MR|k#^=ySxFh3^^ss!ri30Kk<SgGvt{r*~Tu81H+72!t*AeXme`Mk<6Nk~a;luF9=pOiE_z=1qJ_LV+z6IO*BlNR+G}QknHC8`_KY|ZYZ(m=B9)b^1Q-?kZTm3Cu2OmLy2OoitqQ8fa!XKiK!Y57q*~GW#LHIip$4vYU{RBQp-7)l&5T9gxl3L+!8B1T`gNzT-!}4Ae<tFx_+u?oid+2NMdvGlphil=zXgO@__tVenfl&Vg)L4BN-V4`KZ(sioS_{`w^A5Tiw)$)M9e6+b2)rLYfc^$P0Kbc_hEJIIlZh|T8u%L%ADH+WeIKr&?gRAw5T9Utf?DA(7)xK_8pbvBu>87-mrU$LUxs(WRp=k#D!3AT5w3(^M_+<%pIxxk3fT6kCSOf%Cw+F1-$Aa5*Hn<NASb+vvDJs*9dI@JFkB7qLVpGCf-BHf@aHC8HE|p*gTFHIrim}nH{der-bCLB@#l;`r&jnlW9chg#<+|gmN%MMV`4M<G`tz!ggymtf=kdR;SzWwx&|&mUm+})qMPATcni7--U4qxOW+cEZ9snsTm1#R0p5bH2=!dSds<x?n!`%^t)!RbPffgF;xlwT{8tn9d;ee1t?+v4wxL@?{3+v4sTKZ=vGf&Q&v-pOEI(`FaTCv@Pr%Q^&!I)|b8s>G7+efLi#`q)qkkYQuS1`Q*THMi=is&QGiWhfOs{9q2VtuZz|X*I(Pg2Y%Xm+#%R_TmPQT^!vV60N1t!iy&xB{0xWPml^hfY4>TW=94%MAW{!DU~vqm;(*rw5c`j^mu|HKjxeBpl()vxq_JrsUrPxIjCep!??@>KhM$~^crO#ITMrG1hQ{sl!UFUS'

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
