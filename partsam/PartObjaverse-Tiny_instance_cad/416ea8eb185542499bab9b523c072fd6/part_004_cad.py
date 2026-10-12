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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/416ea8eb185542499bab9b523c072fd6/part_004.stl', 'relative_path': '416ea8eb185542499bab9b523c072fd6/part_004.stl', 'source_sha256': '767390e2b960e8d332208c7ff9450abbd71528391097ffa45bacfb8e5d921c10', 'input_faces': 308, 'input_vertices': 208, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17299848794937134, -0.3885408043861389, -0.2707625925540924], [0.22722779214382172, 0.42829254269599915, 0.26946985721588135]]}
GEOMETRY_BASE85 = 'c$}r033N^8+Q)aqOj6BYs>m^hN>FoDl1&XMLMRbx*hoT9LlCrvO%r3yb4^F0h72T;h#0pRDrQxoR2^-#T3V{K-`891-TVLiPaVDYTkBi*X06BnxBurk&-?6mzwbWh>?N|Bdr2Qf{%R>n?K1on>(Gpf=0AzC36tW7$4+cKcKkFqr4oGnQCIfp8xh&xO-WSV3y6uGI6NVstu3HkT$_METR_~ngh>fQ#|{~n5EE<porjK@7;E|yM-CkyYaTaf*0fEat$D*h+YH-(_*dR+LBCY@)KOE7_S%UsQ*A-NypQ8=&!4nZpOJLZ^7VSt4noTX!dG7!P-q=15zh`-s@2Ne0YC5BMZCW-A=6T&#Af(*ug{J_>j%KMUrc@>U$3`rx23kMMDahBd~HE@_)5}HsdMlK@*N3L8OWay4PQ%fAYZ*y2EMxW$#%T&x6h=XcI)>*SN$k{%pK{+9sytPc^<yu{pb*M^&P42mj~ZA;|J;Ie$8~eUO7kVbh<75%o_#Y;l4}iRQnlqv<j7^|C0;h>tUr1BQLN3`L?I^;j0%b!q;0?M?dzfRp4vNLyW5|cFV%+hbqXpg|{%S`gQ<(+rpne!t2WerOxYT($Gi0oAA{ex2{90ZNmJkZO(~*=MSlWcro&A74zZSd)-BS<*j0=Qz{p}Hcjf-rWfM8)B{Uj@U<cx^X3TeFa4yoK|ji&t2i(9vOj!B{^!!q%H#00BbDJR?!%F9SDMSX*_Ghi>bn)<_=^Tva{V7~L%zpX(&wuY@Qu#5;2W&3eX&ZeSDB;YpMDv2)X{OM?|702Uw3P~599o~4*lErtb(r&zK{Bv+aBbryOxW;s2TE&#aA$&j>Ku=w|x`7zJTkYYmD@{WjxMHZRIQ1>zn2>?&_Q9)0o>%u5V^l@t<vydCT)mbM=klC>i(6H<*9>ywZ~I;e+#13M!+HJ^WrO^3rF?c_k-EohF~Bx{j-)Dd^K);|hFxweMtI%?_4%{whCJ)@vQqcX;NZjuQ7?s?5hDng5TT$$SRK!B_k;<$Sqrwd(z(pFS(4pO|!9cV(AN`k8!9&Uc6=eQvBS`4j5Nbq|sK`<LJ0H0r2bZ|*|9HC5niUN>Z2^&KYt*S(X1<D#b0|9rVF_6k>1WL-U!{d?t(?7MUOB%gJZ=+DrPHgC1$Pk4fSd(|x2zhf6j{*td`U*8=o>p6T1e7$=!=|4J4u2;*kl0Vt8&vkzEa{Z-#|2A?R?W5)X;~oXyh;%=KJl=mCzxS5<L#FM;c!N$MU;m}2)Gwa2SI)y*_UVb%l0R!ce8p{>%tQWb;#Uur`6;nn?%U~&;442=%g6YC?87{3o9m^>{`gt$+xMQzeY<~2_>R0^<bK;ETlP`#)2+x$m?Pu*dCL4We+*w;dL8quXY{~4C_xX!ca+EZ+J2la_fNMQ@U<sTW&T$bXUg#v$uI4Pe7kQ$nTI=P;2VpUU|fguez<dw<X5yEk$v1x>Ljjxp&#4Rx|koW>l~@mB1PsowFv#&I?j@O|7MsUThUGVeEB3?^0!>wEBi87?yILd$UJzAK)%X-ZL9H<9sP~DChK-ZNx6^t{s`ZAcUcb3zuOkncdX5ZuLn<;ahG(I`|6@}$!8s7<TdGkY6^U%=L6|yyNBF=n$Nb&`%+Oy3BM%$JQ*gwQ9Bpo9rJ;2-x(_7b}g3q3HFoy5^s}n1F~hE@blV;s`5g<W7c)~Ty9-f@{2!~ag)DFm-X-1;+k)K`ApW~*XPC8&dK@u)D&NxCH~{K(r209WPTzm!Z&V=fv+aS%XPQsZ<hU17V~NIN|AoXZh>#~E&*TjS&II(CbPxAS5fA_j$OvR7A3x?e~w(wG@0i!k?_@Zb;Mu%liUxLN1KrUzK(vhE3vXpA~(QSukMgOAJ>vPw__x~Z42phSQ9xf-;$DFS(82&O_ux8ncEwY|KncNQSMEX{$uxSlzm+!<JJh2`^n8Q@YQYS;oG_Xl~dntfPZu%>N_4!l0F~m@D0DM@a^6E$vV04^h4CYI6>A`naw$2SobmT)l<3Be{Phl&tiAU-|CS5Z*7$8k~?)h#;+QIerzi)CR=sveoe*yxRR{bW-F!6{VMSFjz7tD$+>~^)w>j}llA9?er%0G<UaXlBk}$HUbr7RcDTXUJ2jE~XEo%$(dz74<acW(_YIF%Fh92RmMihPF*6(E_D;h2I!5@fz%l1d(ely1wzkRw<bU@Fb+!MUBK^<4Fb8=%!(^Y=`8gYP>SoMF{<+TCvd&kcj&fo}5A@Oh&^63&>-8t_zDq~CSjV<8-tbkQ&G>$<+%Akny@5xrV;&vtkZ=FxdM_Mz@P=>PYHy&AfQP-&Z-bGjqjXs#=MlQB5B$8Zi;@42<Yd%QefuG=Ry%xN*pItqxcY`iA?g}=-z9~)`09jQ_-bfKj;n7x{9Hc&PLEA?_4S!@ztg)c$aeLW4?o3qRk<FF-?zMt^K}H_y!5Qc_`PDh{mu}~Prdk?IFCAAE+fC7y@vcvEpDK0U?2F})LtWy-(WF({g2Sgc;Av4^Dyq6#WG*L3X)uX=k-#Dhst&Te#?BEZ|Dq}2fs(zuD<iSE3@L@8_IV};Cnp9_i+7pS%*&l@9RgeQFb-_?mryGxHY$;AE*D<I{d~B{WylyT!VgM4kBNvl#%V~JJ+)j+)4WUr0Pa!?FRDuC}V<*Pv5y8wVw6mb1;4=d^OP*pQp-$`RK>#JNLCizYO0o=Zj6q?|T~GmyB9dvR!@W{X_{0lYX`@v%|L?KZt(rOZ~t6?>EW!?N*sG54{I(m391D0p_RVYWV8Z@$iiUeNe~vGCJGUS4Q2<gTJt`thbP^DR|v$(|*)pKgu=FROs?cm`^QFu8-4qeqO87j>`9<CE?qVzaSI82i0<`GF^S6R3654{5D5EH?IxdfpMMvH}aS7KWAexzHMgICpiDIr!V34nHyz4z40}C`-V{X`j-#jYjNLW9jlEF!#9${b5X}P7rs(0NPgFcc;?~#Y0;>o|Jo4wj)?2<ZN+PmuV3vY_koaS;{Unq3f{N&SNWZ^#%-VE&qW<uC0{%*aQx~8-_iE`CDd6QE%&Rdev%(i0{P0RAiS=r?cm$5L}Oe>aZS`wZft<Be!KG`^zcsfqjaB=kGv-jP)AKj!t2KW#2?48Uk>gI>Y_sz&`;{?c;2BmO@<l`)8VT{<K)<T)hTFqJA7m7efUaoQ@Ov?4T7)bmXhOHcQK9<GWP<GSN4Rj)J=i!=<^2llcRNv^zpanC-(J|C4Zn7e9e9w&o%Ua%$5AX!;T@ZL|=S<=$DVnbD2T0(&vD8<$iPGqWII#iofui^Qc$3G>-q}dCuS_@RcJOr;%Uae;$4QF;L$B_vb=tauM>E&e)IFlin%7`Hj8}Uw6L;U!PJz<}It%8RUOG8S6za({(M5PZz+~AB4*LJ6$Zox?1$P_yf;iUW{W&=*JdV{w#cBIo7W|sh;eYvrFMCUzCNfJvxbe!@EHI?zPd6R<+}C_%{m0Z(f*%`n8v0JsH(*i{CI0zQcF<28_4)u8jNO8hqu`3oGz?DZg_#?o~zhS<avGT%&;-=35C!M84`h9_QgW=PUka-S#5CNA>ezkuN+wY}sdNw@03eVnsQ{M~NHi^61bqtv{#!`$vcIE&gAR4x9h?j}E7sJ<Kv=rWp&&$TVXi!{VLPbn;H}4u-|M7#8oN8e~iJ$@|E;42$!qr^tEa;|z;Wo3Y!B3^TILI84o<W{`8pd#GvTBh)O0#e1n~<VDo^)HL#Z@(hN>v#A;6*<_u%o2-*(F?PGm^Gwd`O!}FO-JHMOJhya4Hs{iL{sy&xY>=IEY3WI70r@1kh+*-^42us^50kApWX5?j&QVWL50TGO&oC@5G~)vGBE#bS42us?PmoWr<^hJq$EXL%2ie;(Y7Y4r`6zV{*?H}cQumYhbBv>W?@=DRDe_msjNxVsGviG&tmo_1%y^kvm;5rh2DLG{2DyP5uTk4j8<X3RdowJKpw=ZvklRwLk=v4+Ff6V_El;+zG`SMllVNd5GhQ*Hz8UQq7Wbq!CHExvWmw$Kj26^DYEyC`*`HdU>`(TkzC!jTS2Uw6)tmYX*_+&q+Me8l8bxhSjv^1H_9PD`$5Q)}W6ALhiw98Kkq3~&UCuw8Ve#u`yg_YEZ9#5L4x$E<gUGe0{^VNZ%2Z!+WwHmgBH4pn#$_JMFf4YbmLywRn(R(4MJ-P*MJ`8unOu(SMXf>hBKuJrkp0Mwl;``Q5yRq^W^|wiQ(q$olRHz}kUNv3slCb3<dF=EW2h1281f)$Tk;@sA8HeFA98nw#R1exWJ^8Cq14(`PjYQ?1!_rh1@cSOvSdrW$uE%`Qk#*Td!Ql1;x`!<4`*0Bf*M60K^{XLOddlXM~x+qBTuBplP8iVn~_KzMU5wqA`hevAX^$v9!Ty=eVyEutSZm<n98uY3&Y~K85Z|vSo{{XHTf-aH);^M8@Uy=7P%GqRcdAOtK^zg4{}X%RcaY>Rk9D&o$N!dLM=tMv>dq#xjNO0T%BBx>PN0eZcc4PZcgq*ZAtD#j#QrS$w-F9{W!P%IN$x~JLkUxuZg9>F4riS*U-|=F4xrJfz)W_`5Lfz6m=vykvfSwl01o=K#d_MkjGL7k;jrpQ~QudljEq}$#G<jVR1)l0NJ_cJ2FCD@+}@}#t>=<HI!^=ZE^_NMy)`$k?T-jB3s&!Z0VciI^;0wF!C_=5k?Imhj0vw$D1+Lj9v_jCs5xbPasdDCX=U;=P@i^PF+l1PF_o0NnT4%rLHHZl0TwuB7a2QPTfr2PToe{NZv+Hp{^sRkk?RGkk^oxQ9mFrBhO)2{Jt4U)Fspp$V<qps4K`TINmCT#UD~Pl0PJGp>8H`A#bH_B5x(zsq4vh@&@Wk@&@v1>SFS0@=|Itc`11=^*!=j^1IZj<afza7#6={Mr1d)5<c$#*MGHn{-@*1xa)ts`TILx{F&|g&QLSyuOHo!-AY;CYs@e8C9rtotsSEL6Qedg-2'

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
