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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1b3e8b99913442308aa989e3f87680b3/part_007.stl', 'relative_path': '1b3e8b99913442308aa989e3f87680b3/part_007.stl', 'source_sha256': '6ebcdf95696a2703c18fa46205d7f0adedd69a5dbff3594512fd748976372489', 'input_faces': 262, 'input_vertices': 174, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3326033353805542, -0.2811617851257324, -0.32491838932037354], [0.3639674186706543, 0.39740830659866333, 0.3408743739128113]]}
GEOMETRY_BASE85 = 'c$}q~2~bpL7KNXJBCcpaW89t?K?E@%F1Un;1~)`8k!WzCQ2}uQ1x0af2)F_oals8+Tu@vy(Wr521yR90>bS+UR$MAhCW#Y`lW}zVzvnoSshO&&8LDob?>~LtefPib_3H-0LmeDlHT*Q!>P}9My6B>5Dr#!3T1rgP<oHoB$-W5_Q!8mM;;Wz6n%h4jEc}y7T8cKqb97Ads3gzMx@XtePM$uxXKZ59<fQ0?sKlhvG0N{5Jw7?c?kA6lo)}|axAN;4;G?(m^3iAM|Km?}dkf~MK39*aUUFVuQmQwpULK^@RUckdYpdniS*4bl_0B0ZpDGpKa&2_6Qd6y{OOpTUu=v{92&?G5jZ#lb=_S6||1H!H3q*cKNjd6fmdNWV<yR!X{=rj9jRn0V--!LgWy!DqrTAut9GvGq{p<qd=lF?QJM4#_vmW{BM^B2skN%=1;%l8z-+JB^epWW>?9Il$!`$Fko-V%S$M<mD`iAiJRQN4?rH*;@ZTJpTE1Xwr`VRb}6!hn`75y(_erYVuo1K9=C)nr8k*E{>s#J~(xXXUv8~FpJj<NFq{PrgFx9EwS*C=BC7X!q%E#HoMj}ODY)ff2(LL}cj?+E-Z?^o!@@Miy01Cc)f=hf;rf*<0A{ADr7U(NHDdR9Dd-)8U&TcS?pB+S|U9{h0k3jJt5G5<(C@%2p;Fu$=6;HTF{-ONnn|DAr^OPQC&c^UdSa}<7+zhaJcdf<LMat!{RhwyXCaQ@ZB@Mqo=-xTPDdFGVB|K_Ur##gzxzx|uTpK-B5eZ#{Y{+MGG>Kg++;6FJCe|0PL|114qoX_Mo9`{3Y$FIeo<%v9}Kcjv&{Y@=#{hlYnFQR``7hi9%7Ip65LH%Kk@P2p}ggM;!7XHC{*yk49@7j}UsPl^p`dKhr`ZW)ChCjPD&O1IG$7Rs(U0v3;Z8vd!9KS>T4vxr+cgH^V((m<L-v8E9Yw&(t8w~&Q6Fe6R(WlY9JN%<}#W!l8zA>RE{2jN%x0E$UUyXag_v#_fDQ$Niu2=XgzAw7L-^b_EQ~H&CiZPe3QNK0kdDBaLOW;`CSL;3C=Xexj|NfZk1?F#PiTu<Q)c5m*pZ^a0DD-1K5Y0Z_D)gg`7zux0J@k{!=Sr$K>bzY?d~3pD%(Jo&{HYG&+d89v>(W^6>*WbK?|nbar&An!@0;SA^o8ihR26l)To+%j8UWv5{nD%A+g9(yb%~=t2)@~GF!uX`bv71@uMORg`^v8de7EDMGp{=QMt<<S9m9FUUt(XK==&Z;pLfF1|25Xx@Og#)wKHR|uksz@8}~lOJY(YFH(Z1K!~8s1H39yn<rV51K?(31%tb$k!Z3$cHE~|YPqE*OWvKrN{U-_7*U#NB|H^ggj}zaTQI7j0jehp<3iXZ8c;4xe=)XPcn~&3v>sg_`d0aA|Gd+<1pbYc*p1yW%Al_$3%cRfx4X?`D{M87h=KJu?A=~ILnW5C?d_;WX_HX>WOP;ONa%HD{AJBfTfqXq-j#B;drPH#n8nxitzBNmoy1S9zdM*5k!_$;nCtgPW2kYQ#KA(#3ZpC?*U%!I-$1=q~_k(<2Fp8g`AM337(*Mijl5f3tk>_<^Bz->kN%GAzFQSfVqWId4&(4Vd_9gnK7ArN~yC(VC?lYW2l_hfCWxJ6dTn7Kq_GL;9rv%xT@dKZq7l*HuIp~wbH*YzD`j+M5TieZ%?@vbh5AgF=!uM~0`umTvpFfFjJK`+!(Hj2<-!>`_b2CdF>*ur3Pu^GJn}$`Fd~@g=_%3I~H$M$UpYspU|4w|{zLU7_P6z3~K%JBz>BpE$f5@VI*;n*mWIoocbJ%ZQzD4S!K7${!9euv|Tzq5vN~vSLOTXV;@y%0i<GP$HME!s#@E7dG9HO?u-@Cg&>b!Rv_wAXDsPm{qeA9$8xKF;ZAm8=UM)8~N$9_9sK>qlj#J4rRCG#;Nct33Iya{tVfa{eUg*uLr;+qd4U&}FZ&i;j>eadma1s0>ufmPyL9>Uk+KazaY^H8h!1&?H2=1ad^lsVqCoRH%_Y<f-Bo!jF3aNtAnEq@D_wRK8&sc&uNSt75mE0O1gb>lAier_$ciEo|s<#nm^z$C{RlbW5B{rZGRedDxoR`NoZif<`jC3W>C9_WAb1@X1V>-LDAPLt13(__z4>H9bBk5cE-uX27PH&}e5MdA(F=l8?TNuKU@O0>GS^kZ!3kA2OH5Z@NjRpw$W^b+5^Fj9Q2RYtD#^Kc^W7vDnht)r1|TH%fP^@4BuWd!Q)dG~@GKkhg2^-a%Yzm~ggq)(f3jni_R33aT+?lON<&*U?rarAFYNBy#C;%nV5>{5ML!V>WP^hJjF<`Kx(JNjeJ3l@v7yY82|X6L`jJZ(F6BYy(xuPl~6jc4g);-B!9{>^jGpBF7%CcdrRBk{GIVYpt=d&M`3{c+tNCZg|G`{0*{imxBiaDU!?F23$jjPv$giFJ<_a=(~IMZ!Oc=ZPtDDDI;N=fpQ}+avWXQAy$(gV4XNi;L{fT5YEIdLs9Ar6uMTx~?4WBl=An$$V^XPqB}zU2^}}nmmyGYK>Fme$k`LaX*ycd!VJ!Zt*Rq6>=T5Ti#N~a=E!2XHB~;bJR1hqR*FoQSY#hIx8Nczr#z!Hy$s*eH(mE`Y@_G;yU!k=awn`CO&^}1c`4g+lO_77r34gamZg>iu#M1U|)xl;YVM`b8wOq-bYd1a-8P=Ws$r-^F^V$e~kQ2@So!MOg$z5bB_-e-$=y$V;P@=b*dHb8|N=}s^j&({>PM>zbJ)YGFCp9EVs7oQNH$U+-1C9+8&p6`_1^imEeHB_UYTD@B9r`%)cZ2)Xhaww_d-ka-Tomf&0j(NPd6U)0`~Q{~b?UkC5{Pvc9+Lpse2ymHAq~87KW|W1<cPg;)4%NSwRFucvF;pD6Zl)?BsN=r{fpqD=MkTL1l@LgEAdt3QSKckusz{}hs`W?_#)>PE8CZDgf8$c5x0>Q1uK?PR4}$wlNX)J0^andD5?-NO7WTvxG2C3`s7!_gj<IpP)eSY?kK>SD6edE^}O0*2xY>ZfF-^T`?HxeUb%smsYqSCbc#S27gmv9~<-wTirkx|+O(yq>z8yq>&_p*W2?pFE#^r!f@IVkl0h&Lhv`T+$hemoOCPQ&*8!vA=wV;tkaG<hk5`1~rSkfSN<idgEGTaW*T+d5kR1FN?Jl7udtXbLCUlQ7z<k<V_64n;DANQVYmRmy*|#vl)tKQ0I_mkW;DC$x3IFQ^_-_x#XGT&ltIH^qI@v^QlXyx#V2ddVP&%^SaIExnEyL#jmfs;xy_U?e}{_@iOXC@>0&?^*vU=>srA1DsE$sCid{5zC~8i*dE^Gx?HPAnR@(HBRAx_F1^N7SMpn|>r8bcE3N$oH{!ajrXH*4t2vKp!#-3!U#d=SXOEUVt|gCY%hyznKlNR5UG`Ls>P)Uiu1T#;ZqB-H)J9~TdwiGLklc;)>Pc?HbqKX9)tlVc9v|A{18RTr2js5Q5OOcp9YF0#4&`efQ3sG!PAB%!iL+7Mf%SZ;-sB+WbRxIo`h6bbPxU4DWPbz5AzXh%??Y;TauE9qC3oVwFZcXDwF9}8J>Id0C$$b)#oPAqAlKr$sy)=-{9UN^$+h^}>l_zy9oBWC)+0NSYfu}ITic@<`)bBxTCopR&x_iW+=9pWk(+U?UVo1{iru-c#h$8Coybny&ugy1bqn^_jNE{07uIY_uFrLMdjxW3f$UvzFtsDqgB)%T!ydiK{kS&B9jU?O9;_Qi?N08)*9KC<$SS8j`)JSEC=OsfFRBMw<#b_Q7tXac^VR%1lfAg^&i=y4!CVid7f$U*?!&r0sO`xHYxgDxa6Q}}W9<>mP(02a6RAnmvE(FjB13UJbvQYmY+@+>grPWs8cmKMM^eX;Bgtdl=xGc?aSAnwoI;*PO(ahvPoc(>r;y{QCbEgW#xWF+W+)y^jUW#u528kr2a$(R$B>7RW2q_RSn_1*H1cHfRO%G+RB|#kjvU8clNpL9FcgoX4knKxkDv}Bk01}F4j~UEM^R(RQREovWO58SfjX6(K%PWRCMUDkNmSL}c!uJU)Dh&7<YCmI<YDBGsZr$c&`OnE9sbk5gn$1rt1t8w{z3e&M^^mx>CGc++druP`O8#zXchI`v;R_1SvFNyJ=L^-0CvruI{'

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
