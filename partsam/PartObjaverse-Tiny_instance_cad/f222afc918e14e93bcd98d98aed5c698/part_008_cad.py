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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f222afc918e14e93bcd98d98aed5c698/part_008.stl', 'relative_path': 'f222afc918e14e93bcd98d98aed5c698/part_008.stl', 'source_sha256': '075cf400092a23ce2aae2ef701b2cc05bebd840baca6db28cd462624d880d0e0', 'input_faces': 512, 'input_vertices': 321, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.27274906635284424, -0.5454549789428711, 0.3636308014392853], [0.27275538444519043, 0.4545450210571289, 0.818187415599823]]}
GEOMETRY_BASE85 = 'c$}r13zSw>8HV?8QxNlp;1x!J8ITcYxQX0myv%5kI#_r~KoCJO5`z&_Qil>WZv|MWsiC46X_}@er2$?*3zS4rbYwIb$<owJ%}6>Q|MQ*y@a}(Dt(vv=df)Hedw=^o=j{D%*7_H<!&|oM5ORNqglnc<dG1Y}L$KC9bO_TYOs$(Ve!{fg7hHHrQP^|4ZhwyRP8xY)?HNU3dYDmq&V*^>r<M*XE*&y)U};%#>BK2h>!yyo;H)WA&zWF)&A7?aCM5c_^Tu5`A&GnR?Nd=!+_z_0@nyyT<6pa^g!;$o*8a|F8B_O`Vg1^U4V4A-;)ZP-v-;Qvw{6^+KDMszt*pLmVW);d`CZpMt~Zyb>e4N5XZ7NndvDm89>VBNS-t-H>h*>4yRLa$Z!S;cthJkWsB`A%bvx6S?N;+nR<D}Q`<DE!YaZ8|%TvGC(k(lD$Co><-kCmje(!g8sPl=Mm4))Vu6bP7JoTNcmlPWBx{eQxM=vT^CweqKRBd^(K%K6qd5)=GS#Y0=p6)~RXrGIo?jQ7MpNp<}qJ1uUx)0H#eJ*;sf6$|SF1qH4_POZkKJ+?upNpP;7xZYKi>`U1eJ*<ReRZFUp6(y7Q}?;(nkU-l{(jicnkU--qHCUL|BD`t*ZnVgl;_stmsA!Sj~>;zwR&Zt@vi&$s$Lf@FI2zkUVo}fovKIUrB2m#d~<cW?&HVys993TA5{1A>$>`b>VEEASAS4l^Qb?l?&sHa^#|4c+_|p)pt|N!e^A}eZ(67LgX+GoTvvZkUGu0vsP5lA{f^=fs_TAGe^6cXs6V9dNBlu`&7=O1)+y&p^=Q2KgX&QpId`ef`6^yoy}pp%_)PB&h4kngiT_07wH`UwslIvI@`ClCYdwD6o71&U^}T4key?WyWLa6w`a<iv9=)IAIyDr0pXffm@uOoGW%KxZP~G#m?s;^)uG_fnfvvU=)DKm6zj9suP<8hi*VPYI*F5Tns=Hsgu70Sx`;6=AhpKBH^+VO&uhKfj4^{X5=DPZ!>Y7LWP<7w8>30-ARNeP;TBrD->Y7LWFnvGbhpKBH^~1DI@k7<4@#2T7M|s2#Q(gQ}_2?XlAF3YJBYvoQRFC+f>RONbq3T+v`e8I)znA!7x*yc9MAv%MC)4Lr9}_)#|LUL59=E8n(EbrUt>1OsC!$B=^*f5L<D>T}dOChi&Gz|`KZ~CFCwk=1qNl!x9{IEAnkVvS(Nq6KkNjEm)c4RMe->TyME)##>YrYx`m^Zi{zs4eS#-@4`LpQhclYn8{w%ughsd8r*F2Fw`}<LU7G3j1{_J(?`4T-E&pFcf>AJqp$j?QO*4<FE{X9i^(4#!+^P;CdBYJcm(WB?`JX(+53z}b_OZ{JTtuyj}(Y1cpqjThWr2go>(EPd&^<EHN>x}LNe_p*8M326g+zZ8HFIrw`pQ!H7mFn^xRoC(Q-c;A|`hHaR=StU=_n>+@{$jqX+#{;H&%3Voi0baouIoLby5`Y)M0NLh*YzGz-S@5QdXK2CdGsDpJ^hYer`#i|r{5P{?-A8CkKQAy`}s=0que8^yAP*z$~~gG=Fxj3eLr%KsIGbR9!cwzdqnkUyxb$I>-*GuMD=K0^#{?TJpS)J*>A4ve$)Fx^=MsuKFWh0?OXr%r0#$8X#b1<s~+uh^(E0GpJ~pQ#Ge=3&}ns{=T+V7bX}iIbsryIs#{xV|ETWItGa*pRG06ry4Rz6w61*jRG0Uly5`aEuKM;owLAQ(ecwHwx2@kV8IrWNp+lHBF7uPNiT3AM_$Td2{r;<;wEI`|`G0@XE-nh8OVS3?j31e_0bpmaONI|2HY|mg5|@C3;RBdA7%YMNoX%hgyid~lCank9GsF868<xTQ5%&T6!pn$zf&JjN_Au5PMh@dci3fp$;XR3afJ5Onr#s^Y!)^RgU^lRPhF1|+QA>Bw;={m7c#EX9OqzMM;j)nDZHNt@3OODUUX-*aLJsY0Id4sDxFY2EQ_Nohdfy7hEeBh{1G!s)%i&Kl=Lv8*eAlF}ZPK0zIea$cd3$2R=R%HK4ZH9>hEIn)-;LOCRmgFF_IBV(xb>}K?kaTSUrPG+NZRj14*wAHd~agI7ebC(ZM##S;qxKS_aZi26LS0o=C1+0Zw=#CgL}fCr|&s%HM~R8zi-mkh8+Ge<oSNYhA)R4x3%`6Zo?Nto_8WPTo-cOpRptO65RUMF?Suh@dJ~-gOm1Z$l->N;~R)y0}q0G-+J&h_yI}(Aw@ZE_$K<B#0_9EeE$Sr3Axy?0q%2N0UO|-B<<6rZ3G)L{GY^zP4Lf%KLJ05HxX|JKZD!aU8&8mk+ly+?*h7?HZpD_cqn``bv4m8hI}r=H!`)qf&K>TTQlxnZ1_5{>CQ`u4L37?Gx4U7_gmwg$x#Asg8Q7;!A)>~Z~lIoGW=h}hVR2aC;kldcWN~pPJM>&k*5s31oT?pW87cCGWgb{{X1zNfFHuYNZK~~x6x<(W8%MqU%<C!=6!%>ymzwB5k<MYh99v;dBQ7-a{U#IG5(K`i$4a-;k}FU^FE{w<J<qOpS16TS7!KA#D-VF&0EcLXM*3$@D;>{v*A}Ue>UiSv*EKs-nVCwe<txvwB_WQjW!$IxOuwy_Yc5pGW<DW!|UNz!_(Adcy)%aA~w7Z?$5pwycT{nW3B?Pg`20FfBz8tQHH-jY&Z{YwLMRLhBsvR8e+q_@OjLi3wqyN_?(dU^Eu3!OU}7y#?8~szkdw=B*R}OHoO^bYrV+&hBs#TI%30{;Qov+f%D-vGG-n)AO1+v9!=V9;O!ay7_s3U@Fm2LfRDoOAYK42f&0C1D|kEnwXoxT@hbdw;@d+09=R>#{r{)n0{8;rpN0IrVBGG8TZnH#Ysl2^b>5NTONk8^!5=4H0{XMrTJJE|@E&**aRcZz-9vmg*aY`_o4~u_w$^W{!|<2z-w;0zE`?jpzp;+t{qXmRn?PUte&YMU_u)TJ+MknlFSrH%R?_Yyz7uT=`rBxC!tVnA1UFm=|3%XNlC;I(yKtZPF1Q%JkU2hgG2Fb;eDOr^qzu1`*l+~gJj=XnIQZ2JpG|C73m?J!TG0Dy;U|Z@AD&G9;l#tyW|6BFtrp$5d8PT{*TAo5`1Qnwr@^g;tEtQIlnlR)*zi=iKl`=dNcbs?83B%jn^&4Io&kO%!{-qjj)q%pH&CD9=@~wk*l-klH1kJ+-Zu(<X2|>GnamkQ&QWN_%`43p&jQD0_|3$I<Kec}jjV4tCc|$cHar{d&p00(2Oq<j(cn1vw2(V9Q^9-Tb`~ZRPe!{J{Vuf0@Na<&;f5E$FABMRUl;QGzb-RxF<1wGAZZUK?K1Fkczx0yPTCdVL+}Uae+aw+emQe|?iHDwze?IA;HB{IChgZrn*lxye~|u%!5Q#Nnd5V3!0im%c|8O?G{Z*_8+M1=S+X<M1uV|+T4KX)@b1j-26|sNc-N3Wr(Mb4g}4ja$>i#W)(zdbonbq#rC^T?KaJS17u;$%g}Mw&GW=9x!^7bI>?6UR@Dj#!2YbTp4BL4<9PFLpqlpbG;8xq|)Mr?h;iHHR%i$HwF9*G^9DYQ|pWh>xQ%=ruG~;%L$0n^W*e}D!6B`~0x3$KwzG0sXKbzQa0NkH(9M~V;hcOjkfB3mcJ1=R+g2!d}H;D~v;5Ee6;Q4UxI~J^lPbAkMa0q+|@nG;=xc40e4u(%)t)swU@L|M5!AbCQk~WZdAljtNoPpp_`1$f&H5vYGV#5>QHSlWic(~=cklcn<@G9a;a0=Y(odQ<Eea=v@5^gnohcykq0zUzMJosg}t#vUu43B{yLwqzi9qxUV;L&jNCi9^dV9N~ePHfl)ZXQt_a({+J8QzW9ur<65^IL=7*Bag`<o%}=`2%r4>q@THXsyxh&%DWeXjiaphW8>iY!9~@N~p_lmkd9Q*l;(vKYLHG9efwYv;o_}&6~`Jz69=(;T6P&d&8}^GU_wjJ;Te14flfY4sQ?c2{*4XU+Dnuo8d<i8}0|U8v0O&;XWBYfY`7Td>{DUU`M#0>jS`p;Df`C=Y0_TAmRf<-Ukj0`SZI!*cslL_~4K~*T!py7q#fnvbq0~m;bBZzCpA9K~HDy__IfL<||3A^hc1|;jQiaCWoWN_QN{I-e&j@#og1h'

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
