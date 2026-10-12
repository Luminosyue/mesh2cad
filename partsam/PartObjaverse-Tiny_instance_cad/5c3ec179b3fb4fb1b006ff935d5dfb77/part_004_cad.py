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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5c3ec179b3fb4fb1b006ff935d5dfb77/part_004.stl', 'relative_path': '5c3ec179b3fb4fb1b006ff935d5dfb77/part_004.stl', 'source_sha256': 'ebab10cbd05589ac94a93f360b67e8f170a567f0367bdaec0504591323c94400', 'input_faces': 274, 'input_vertices': 242, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-36.88883972167969, 66.43317413330078, 9.387020111083984], [23.023876190185547, 70.3666000366211, 15.468334197998047]]}
GEOMETRY_BASE85 = 'c$}qL33QHEw?5{Y=T=cZA;O<fk))J_m$uYA6gB${$u$p2rCQVb(-8bge?m>cXAFrUDOE$nOF~5rHP8B)=c$IP+RMMsd7fN)*S%}qb#K;s*8833?6c3_`|Pvd^PZLVt@7k8qwrTn-RRPJPMvp@(kP<JsOa#>F9!7wkE%U<<X5>=3B&8ZoM%GY&TZOv%cY{#Sib?`QT-$R8o2yIBkKDFxcnkUM1B$3cX*!>kpsdt->mP@sBqz<2KF5pF6|n1gX;#kf@%i1#=HKHe}%*Zd(Wt*jy$dCxg9M1e462}pY}5Fo=-gOO?y*-pMI)X@aob=!&@1ZjJ$gscxPS#=&=KR&A3|Ny)}!1pIITm$d}-}J$o45u5ro8JI_ag{{r^dKJ(1H)*bTJIWw>NqfmAI^j=!mMDuoU$gA(OjXl;t@-LRa&LAJ7$I}74t0(NYU-=n%ZxitDHn880sA}x-X00{66-oQ6*EIIqv%q`z^@Mzr^G03`1@G!g`#UC@dA%LMtMg|t@18uyewBU8GWy%m{%Yr7e@*bt0obn=mNa_Yg~8i9zK36{>lu01<(r20#^%Dj?%Kv4S4;5jim>155@zi8lp%k;JNz2H73+2I2K0Xfdz{KE5w~>k>e?yTf9$!D_oVn5-qn!u+a4ev(yKxK%2U|it|j8Rocx+J!#g#aL4F2!tI{&?8|ow9=2eBf#W*kY7(MR#;H_ZJ+j<q^6GYy10`pe74!??*KzwrIu=jHl2Q~HAM#lc%!Q1&p8s0hT7+x((g*~ggVPE)xcYiYr@~w6lUL|HgJ|1?e6XTH2bHF<v!7t^v*w|@T0PiXNJM<U*0CuMAFub+&7p!kcmf@|T;9dUQrw2TU&%QY5?^zvu#u{V4<!t~xD?S3><R<J4s2^tR9JK-Sc4~`!yI;@n&gqJXPp=8kb3MfHc3f}hdDI(rJ`aYTxC5}WWD@wh;9cp(pr_%xuzxRk#=)Ao5%%u^Z<nWEucl+ap9(U(b?7GYt;qY>cRRqVv(2G@)E#5Lvk|=W!FSM;XU*S?{@4#g&3bLP3_V#*;8%k!4Nd%iE`;@ZYY)~vY@^|=G3&5iXB!}HpR6;yigsh(DPiz8|60R4TRulVgye&r7gC^SDDq0ReOS%#`^cAL-ad;m{yJO0+fVmm-uOi1PYueyS_=CkzeoO*Ut@UhOZaPhRvLeuq#)R{;3DGe(*u63t=_=MZ)SbF_YC|jU&Gt3waABsEs*C$!K-3@A@5%r_H3_ec<Un8*IJut{8HO|ApakX|IA@n$1>o(9kO6g@@&+}g5W)EnGc<|L;hJ6=o!`xdPY^jdQAdvcRvq1?}uamo?2Aj@IlJRyL|@NGW=@rG9ls_IRJiDr2Gu{<s7_*b*Z_)@SgoeFz?&(@ayG#!#n>Dztr)euyY~#M!R9p<1dj9Ex>ydSg%T@BhFd#FmD<7YpcCj$IrmKCY^?z`6t4!LEl0DO|EZZoLOIcciDPIe=+XU=b^?<YXSL+{UKi_8@vm=DuFmy(|REe$4eRBiKU&7ikP@LrAtCj;XjPLCuWG@?VTl{=PvAVw)93E3V?UcX2AZWudv^b7KfgC$1v}wsaVGp@NO5^y}}mgNhk{WD~$6m^RRzw%nUJc>stcrvVU<^{dC92gAW`4`3sA%UaMvp-Wi2@<!aQ<*l(STHN4k<72@CYH^g%mc+aDP$e-@Xh{J`chIbWoU}x<RtnWGSYWRMv`+^Jb%Llyo8rSPG<1=@P;oZx)f3K#X?!Afue~bRUzZ?6vcClb%e}Al_weVx(mv>uX!@CdVW`1@wagcfg`O~ONYV$<czwA|z=B-bvV7)q&uWiP)2Jenr3BOKWL7Z>C1fNR#J6(l6r@(uU(#}6Rqh5Ul-pbE)d>ijIC+$ze+Y{1}4=wyqH`Y8fyeDcW;?{i`^8DG1x+c!;_8>k(7a`x;O$F~^e%}5R_Wu%Nc;_tFCFBDWALr*WhF8UzpKVZooQ+=^-p<YUOACd1{(Cg^Z(RsG56{MWrGmHa^W2qzIC%REF}$Y^>YhF6xR2={8c@o#6NW&4(??jBv@pZFAD4u@-(Dl{T<>Fe)i@Dx7&rm>Fvt!07p$M%FJN6(EH}K@hkp4NLfz=O%J7~a5eLUN5Ou6iGUTuKGV<Qhz9w$YqEzV5qW#$qz<29X+B_d1A5^1bI1d~NEob;6%Ms_1vB-yM(S~<7<@$Q+V85@QXn60VLy&*@0Cn&7-wkj7MEk=KPjzyV;a$ICUpO;xesl8AF}$^t`L<#p_?L^Je-htE$HyVh*DQyf#oxnz-%uHOa(|2AJ&p4qp6ffCb#c0<L;q0du}*}cP8Le6WX9j4UlaSnFKfBsEg#ekYbExn^)>n1+%Ma*QBQV)S0~_?DwqcQ*R3(UJExv^9E^Osm~41wSvK;2>Lt{ZB^#iB0pGLzR>R-WEzsY!5ByDPjs0>o6MQ!6p%dkSU)7Ep-uof+s6kUq9MqZKKIVCW_QWM%T|)XB-o^8VRcjCOb2oUWF6z8JBp&DgJmH3S`yU10alNtMTMK;7`^$P6f$yNn5r+5PeZjoFg7Z@6A%^#C$M>K!Z94RH9RYh<mx7(msvEytGr)Vh@%`SZ3(kQ}M$#|TPc`ANk@u93#P`r0+EZi__I1W+tn)0qe;o_wURSYb)UB6X$3J)B`{D+8*P316(<Y-`2=9N7KhBf(M4TVojd?D3#W=gM?(P)w`Qfk1Yyf{dO@zKczOM(kjbEM-;H~}4|4^J;T!+EiUYviNu~(tzc}xw{=KIJxHXr^riv{nCbCfDP5Z{9b!Fwj5-dgV{@L|&oZ|~*%Yts+-9()4cQxfMoCwV%)@5;_Fy!TJ~Tcn?ncbx?9q!xyqKkdSMt;)C1Q@J1bZ*k6a-2-p0N`akqTH-sm*et`l#_=5c&Sl&u+>OL{WWjrgn|~dwWAZ|b8^C(9_?U@<>uDms`-lAm{qHV?{f!nu{s#R`!grSIF?c(*3-r8r2)T-j@jeOVIlsdrtV=EOrTJYyH4=J?dN6Mk-`9zun77Af$S1Qt*IbNsto<YS3HV;K`;UR2RdAkCUtb0Pu0Pgm$=ce8>!(=9(#K)vQ}F8JTZqqrU9h9udeqB%%#%KcOnf|J$-l&UsnO-|-F+Fnx8XtP30#f!ir4`CW%-^h5`#R?l?pvixR1i-AP(iz4DTv{bDFcO7xvHmP0(|(0{EkYvA(@FgP+eh-2EK;y>Rb3M!yH&xz6Mxcz-=iHN2hX3ws`<pw1Ncf)Avf!3$B}-Ush)aRmAgW@7*U0Nxe%9DE~ur#tUm0$&;X#d$my`!fK%oBPGdn1=VYx?*_GVcZ*7&9JUkZSeLO+%s5Rd%~|_xdTnRGS0o~dKA_>qiJ0;Z#3^KI(CI$&j!|oKfL#Nj(ZO$bui?cKjS@EbJUA(h8W(H%yqdG1UpZFw-@7n#@^Z-c7_i#yfc#dymJTSuYp&*|FLG?$3EFJ68h8H@H-v*%jxxNkl_>NfX|y7@4@?5z`tO9%S8NDq2COz9^>B08uL5i?DyF4P8Rpwc-(8*Wu6$`wSo08Fc|*M1@DaJy;->s_>~Uco{jUKGp-c!!RHzD@LtZTa~AS>$A*~pKY1=adlr6uNd7eL_nhgt-?N*5w|Y>|3)}~)yyFb7Vt5~wgnLEj3Hc}a!C$Wie*?!G-tNwO%Um^K&s6a05zni0tKhuRX#(VVFKV6JhdMGaZ#~nV!+TeSdsj6Wytgs#SFPW0zv>JFZ;z&)zVl)K1Mtoe-izMCy{<huALJu=58SUV>|YDs{gn3CuZ%puLHSO+XZFE8vr{oY<a6$&12g=s_J6r;Pi#CTyK7N72?+|SGAg3)8&~a`)PFh8|Ng3dQ1Jims=Z$D|M#kWnAi}l!z_pr3=w=GC@-jH+)*l*K;Oyd7WfJ(3Ema>2`UQS<I|UX1wnO=|2ILTV7Q=_;A25kK}SJf9S6$j-#sa#xi*3i1+@gV`CE@|$a!jU4sCOUU?`toQlFl0v_SjUTF^xBk)S2#*X{m-&jg<fdeNrOsH+$IBWPDI%C)4vmXz1_HV^~|>Imx5-T=;5kNr*PLp{n>W&EmA-k1Kh6MVuL3=ni@Y=*Jjj(wVcpYaGKKIYhJjF0XwEhsK1%(Z!koNgBo<Pp3r(CJuAP?mi~xvpi|Uy<X=vM)d7^HDwz=P9Xl(qo<qY!@J>^Jt`CkYI$Mx!_YlV?jSb7eP1nxyiLBujT$G2o?ki8gX0*e{22&g?!chE`>ZEC>X^#N3pH-N7I%Lf@XrY)Yq2na6xB5Z`#tCb_^jmkUDevdvI)L+S-}z`hp-qU4cLC4B_wk<n?@EY&YgJgyU*brUw1;Cu)+@F>Jv&bz;nP4ExZ}esA=3W2`KWD<UW%cuQe_=T+F_dhhFUR*KJZlq<zCh4{MyWec)hi1DvXUfbuxwaCkP6uI}Pw=&!McQN+AMc@6{cS^8da9D6ia6)iWa8+<ta7pk;aF^UA@_O8_0<Ykv;0B)$sl&_uDS~l=v4XD!F@nDf)(ch$mIyKhTLqhFi*7sQwA>oO9Kn3Sw;Z#A?KpCJo~44df;7QqL6+brB8&c|QAYRwLl7_cPOym2rL-@Gea8jI1V7W~GlGMB>b?W)J4U}R3a$&T@OfWwhqAiwyx_9n9OHPIau*rn+vIL@>~+eW<D6&s`yyj}o^##g^A7De#=dESNrLf$<$?`@b%HH|U4q?j_^_M(y6*=;qF}CI2FEUATkD)ne!5@`*LXVnzT#Ss=iI4+B(7N!+j^cof^A&qJ+x;F<Ez`5{C$9Z+c<VTpW7(ESdgHQ2MKH^zA@ioK9`eEpsiE*OrSr@7@M{9U&kYhPaU5_?ALudf8rT~xr83C^CyOW>%LzU_R~?~w8CD~dqeM;YkWQs+@q}SyTHC%3VTlXJ!1O;Ijw85AXYF@kSzFKuv#JKcM5jUh9him6l|y54*u5MKLzsy3j`kOSU~-{Z>C_X;2VX#9Lx3urO%VtGg>x9VZScn9J;+yVL$8r{Uhhqw(RBn`k5iv$JjXR*EVOfKl_dTeQa;yTq&GuJM}MAs26dxdjYwXv}+FiTS<NvWxt_cGs&$|s29nE{+-Tv=-RP}SjCu4W*q*(XZ#y-ODU(@IrS!|PNj3b4soqEvz^XyX&kF<oI*RbAM@#p#<%R>%9!NTQin0iB&XZ!IbO?sO<Qg19!veYhUh%h`Ka?#*YyYFa_YU#L0uDd9_rlG?}uCJ^?TwLeL6|MPSF-Euj`@SQwPW&q`haz9c2Fr>d^I0*Ee0$bWOa&_HlB$-s!q|mh)fc7+ovxvaR{s9G@e5M!l}<7pc#yUf0x{oGa(OcAovZ&guH5Yn`qux-RJbuj`Sn7eCMs{ae?r4dk?(u0gss%;wm+<ff6=wL{mXaq4xA(({brdg*>$V{{E%!Szhy99o~QojMOP`CHqxjWNw+oDb5joEp5IV^S%vb?LgP^GfGg0&Ubbw{MjzcbPo@)4xEy{<HO=^e_Jq^<PK+^>gmck;6sTe}3GxZ<SA<iRA#5+Z;4==@Y&B7bFg>1^'

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
