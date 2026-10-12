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

PART_NAME = 'part_022'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_022.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_022.stl', 'source_sha256': '9cc59ee2651c7d13f022e12cbce1f5332f99d6e39c396291ef76ea6b1a72ac78', 'input_faces': 355, 'input_vertices': 224, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.20009827613830566, 0.12561990320682526, 0.11658842861652374], [-0.06417141854763031, 0.27049970626831055, 0.24326762557029724]]}
GEOMETRY_BASE85 = 'c$}r030RHk-^ZUs3K@}%vK(85CX*OtEN2)DCE0gQC}kJ2Bt2w{tYz#u_OTPjHsvHLWXqoISpUr5%wRHOjO9J|@B5t>@Abad^<MAWb^WgI=X|@*{rv9ze!2<`vM=hY;isAwS-WMTUS88wl+s+anDFSaQ3J!r_>LGg(M~HPzWVt`lS8_;5AA8E#b~i!gTluQjP`15@M;nf;N@fRiWnI^HacuX|B=yy!j<1TY}lA^n?EKpY*e`Ivv>Xa4SWp#wS5e6hX3PF36(?ss*^`;Vu@dHvbjx7?#r^3nwPE+-~8gvDfQX1ciai3`m{v&A<c5tXG5K>Ir4kw8RBchzsOUcwMPSvD>cp?20zg#<@G&fP>)-r_y)IU@;u#tqx@d`cYpYG?WA6<SAG2cXm`|8zwa6K+4`bimiS4X;Ll2u{I$$$;#(?&h_6r1#q*-Qq(1As0P(G77D#^9*T2E<<q!W+ywsy-1d5t(`=NhMJePjZO=pgY8sKY9Zo;qOBl#OQ)I&X<sq$RQtZB&WrMLK|2oEV|o)RG6(~i|(dwr$fjD6kE?n%z@`^BA=^2>(EbFD{8A)hbDOFvjn7Q=WoFNylQY>>~E+McInd|d63=kBts|4F9k&R4lozZQr7I+!SVSzi^1uWt`U{{;C<p61Ed>2H;M48Od>_#Vs@-<VQK@-fYDmiqOl+u<*Mj{MyB<2m21M?DK1(f-PfP(F7p$|rkDzZomuk^HSLsmOEAP56d)c<##u;#+pjKPR6@$4Wg~>qPOj>N(<TuM6e5hTkT@Psx|(8nfqF#9tOEzI9V^lyf;HzqdXPLq5UVrQeO4voL>`hoGK2ze*ljHMi`Ked8)W=^vxtmr}phKN$57-6`$ScWgN-+M*fqKhjF-wfx)`<6G-X_}c;`A8ptc%!jD*c<#C@$fv?P@l9zi=%1NZDR2Dj3C90#XXLYM;CcD}t3Tv>+S}iAB%jskDBpe{*6X5t@r~0SNI#m^_m+Ik&rXQ1-L56yH#nco{n$6wIE8tYel1;e@xdI7?;<I0GN<Hx?3<Em%6hOC*H3@qyUxTq+B{a&RCyorbQpm3HsLDT>$6jQOZ;`rkEH{!UbEMWZ!U)ZGP%S`UWT5lkbh7%+W)dS_Nyu@kbh1!tfTfJXqQtW>Ip7~@@4GcKa4}3yZgxaS_)B*DQYsxhqz#V$6djEnAivT+n1Hk#!IcRK9+{!xzl~HFAW%k`Fy<t{h650DGji0st2Q<1udkUC9$)7Pb(h)zpw(vJ1iLU*X%F8;eG?@7o*QInTM8eKje9L6y{HlZ5X%VzGzpsr&8WhqY~D|WN+l-kb-?SxQaZ-(6$E3JMO}I8|;Gq2{mBcr!2>ME>T44GuS!fxsM&B9<$aB?Q$%EJOkR`92x0`@3nJ6`C0cR57WAFGR~$XN7TQ&E#~v?I?@k@TXv}D>H)0lT6Z%<J3q~qc@p~?dFR%Yc3Zq2h;OpQqTjPmVf-g%iLc*@mOQL29I)PxZ$v##N9DQtV_%HJS{;6ZpOiOb?3e!3@5hU8xYrE(?7NHTpWTzh*N*qXd|f<M_5rKoXymi$49<_b6{X$go<rb=rDI>{5iISnJ_tviOZ%YzmpqhtsCVuxzIn}KjQh^<=!dHv@mwDr>+lBlTg^KNez&jD&cZNxu0G5S{(;r#|Le)vr%OAby`etxeM`lG$T#Bs2`TUX6z6w$P1<Fd{D=6)21~HNRgOb@i@y-xk~SUtj9Wa;-}{eH{_iC?H?Mw${cp-m@%854qW;5Ir5<C>HTW}cU>zPvM*bx-#J6_O$N4>`G3I%2I`Z7%EAvTP`UUjPe&ka%9{a_cs+dRKX~^f%V4REHzm<8S>p!5LT@hG!Q@k;+uBF1ivJdx@BE@j-`z;aQ6!SOsoxGA*Uj@^V|GK-fpJ<VP;`e<MkiRJ(`$nV6*lz+Sz>k}X`7!em_RpUOA%ERo=BG9MFZrGp*BAM(4wQP$Q+rE)n^PK#Z@7?-bLGTl><?AHLj4zJW1hRe$NrS&i*`8`V*Xrml=9ZxT6pdmZ=B0*zDJ&}zaE$NCKO6Nrg_CMo)Kr@&n<;<ba^b}sFh3--{5@~c}A?jysMUQ{Nr&q3}1+Iv+d?A$+O%+oTpj)FpeEJh_6j3E&XpSyBp_8kG0~POd%N8`<pNyVwQ++IdU8GxG)v_K-^;SjWZkLp0i;g#xX4per6ZkD^|r~UKbfJzV6f;>o9gI#&gJE<hiaP`m^$6jBj*1`0Mv!A4{Bp{jhJK_~r&_*w<>7kmpzy)kOW#)h<Y$UMU!t<+G1TyWYFwp5eSl`oZ$>K&IsRvZMIMdbMz#Zrh*v@%%A5<VinR3ipU_2z7<u73;(3Fah;gSIGAb7qjy|@f-e$atltP|L4SruU~46eV_ZP@nW?2=8R_e9A&|M@=28Vrb~mRzf6%opr4;dh_7whk9ECoHO3($48G$G=@;|dm6%6odZS%)gQP!=)6D4S{#{Uir(F0OcHmr&`wsP7@Rk15zCMcnOlpDh&0Mjr2i1`0=;g0lq<lebth+xB;XF$HB}4q%9Z*l`d5l}a3Gt01?qhsQ9K^nDJ|w>G?}ofnZk_$ux2Bl!{x#GQ_s8t5sQ>3Tc>fB1BmHmcxJi7&y-2CwY~3O4HH=(=@*W{l&K&sy<5DCUe(QYnTi{Rfe3R2c@hyjwuwSjfd!C*$7x|ankAClwi~CxQZbu~l_3fp-`pdCc*V~^Sminjv3+*jE1pAiVGV%3iBavtJP^^!nWbw@ln_^$J-y_e_e;I~)?2cjIu6Yf4mF*|K<;`W>i_)TTUS+it-}tQD=}+e8-DW5sd;sgPy^iznSpfVC9Wn1cwqd<Y^Fuwy66JXYo_FR=FAhjP6<bMrO?Ms~$Gr1{|Kjd>)bkMYr=^GZmd$%Hz7cu2&-A(dqttKggLB{aE!L~!3h}iBjH9OghWY8;3*~RGLiy6);oN!G2<3mvL_a)uh5fjakN74}ca&e#f%me~D4+Zk``(%sxaY6@Yrl+3+h=HJq9^j%`n&jA2-cg`g7eFG?g9K=J~$s|`(xjYDiGfsGF0+2+gHXt;Z45yru{kCSL>C>eRHKreB-_Mc&>MQ>^EC`iEnA*g8SzK+#fC1U6E&EN$h(uf8c$k=AZjyy?8(3`tOSKw{D^M2G6&c_a1?`50uG+-@Pc-?a#Om>s7N+PYZACJ1sKNZ(~P`uf=B~&%qUukHZl0b<dq>?}a9)$G->apVk}e_s`oXAJY`&pPSGxFDIh@Rla!c;53Za@$0xJdesr%lGhadVAauY!5;A6tj0dp<%!Hg{i>Vz##UF+u9sHillpqE_~nXY-#Bp;^@raUUwfB;d8-wm-{zbX-_YzEtcO{+|7!K-i*K?kKtGJJVm@ciMEMGbu+MuW;62G>p!k-kikQz&?%-bF*9*@LT`BX{)Oi-_59}_!uJy+Gbg2{a=@x|NPWTJ+=RgeJtEM=j{H))xZ<K3;^?vwSnml*36Z)t2F5DaY+!tS~>w<m!>^ZEjUvG$Sc<m|UsI}>d{<*gU^*pVI_y1p-VjgW-l!keG5ASdG7jbXuG!^AzZ($tsQ}Lb@IRSptbewC0;?X~&#=*Zl1pS<e^`aXFh;R1aiuZ@nFVOD2y~NkwJ4*i6?Adtlc-sW^<c>i5I~&k%!^@z2nM;^&QEkx=$#&vfQ}^P1{)=49tDL8Mq+PXgvCp3EjQpS865sOf8SX=Ey5N0t^(pv=tT>mO;O{7w=i^XM=|jjr#)y6%Hx}i4VIMIsK6UaFzc20|#uavW4=emeeAC1F=>HzyW1o+2D!!r2aJ=t3b;LQ+|G{n<-}0%rhqPUb{uw$^d_&d^><`5ZxDO-_7hfOx7J0nuexiBkCx5+d7(eexO&3j5;iS205n&(w=~kKQ=O6v=|8yJG;D7a}TmOa)|G$5_onp%&N!E|;s!xrlCXr)oF;Mj>Lvej-Lvl%5d}#}3YJIXZxeT=-xh%C2wIR6?Ih;C>98MljjUg+YK^{+@#Za6={hpjcUPVnMuOe?|DBi|UY-T84Lj9h+ggl)(gFKx)h8jbTVLy&xD2`?*?oX{xuFpR0&rsZtp|~EkB)J~>Gg}m+7NM3T7a?m@XYIp}VmoRXvK`s}qw!N*oLYfemaMc9xdQoXhT=$SI60C$kvg6{kvy9^i>x$-Je$0jx{AD*yqvn3yqvs|dXl`6oJGAt&LUs1#U)$h+oFJanS7bQFQ8r_7m%+}Pm-^Z^QfE2O1F{o$UCTJ@(%KLhT=8UCFC{aWa@NsGI<(x3|VP3c^Y{tL-AN@f3nhk<gw&&48>v8dgL&&KlL-RKe?RtVZN4QC@yV_5>zK@F|rfcfm(#@KrTwv$VJJHR6DXGxfIo&{LlO@MRg^YBD>q76}6cyjMS=Bcd|RnS7j*voT1o-TAb`cu0pLqu0n1@{hHi{Jd_$q9!j1>ok*TUPNdEzD_u-ZB+sWVC(kD@qi!TGBd?=ok=K!bqFx~XM9!sNCg+mRG8CVp=95p6(;12_)JtRwInx#=s28c1$QQ}Cs0C!D*T}cXHyMi0Q}f75caYDM&r!FN&yi0v6mOxfA#WkCrY4hDlNV8^k(Ev*FCs5wC{Cb`B`Y0AP9V=@D4swKBTpblQ2ogf<UndUav<4*TAJ)ZcGEtrXE$nja)>Qj+oC14F1aPyhiV}EkgHMM$Zo8&8bh%cL$N2d1lg19O?4uBldDr5$koY}s71+@$Q7xM<cj24)KX-n?&N>=ky;GJZ5fKYFckM?DDFyaM(#=u)jsS;p$x?xY|)we9o0zwj$D&km8|r0@)y(^)X&K^$d#!sWTjQemC3cKZOFCB!3@PCs6)vk$djp)$dk!)sEK5y^T~6_^Qg<n^T<o7>&Q#VYpFkx*OK>8bIE(iN2zDYN6E(-iVsjvkq?mfQq##>sk^A@<Xz-_R10|@`A2Fd`A700?ZZBJh@m)xdW@VwK5UB(w)nvo>luo7Qg@S;?kDdgr%?}*)5u4thslTetRoD?*$l;Js3*uuFOtuY?@(`%mEI)Zrrx05Br82nR(g(ngM6KOntYvnm7zF?x`muW-b7tZ-b7wWT|`#8ki3$-f}wZ;HG!;jCV2sQE<<rFbpkn-Je(RqRvJhiPHso_Ah#pep}LWk8pw6X&8c<CN?VhgliM>C4`wLtMhzi%BX_q&FKQ=-;vi}WS!qjh5V-|I@mEwIveIhgugHE>FR~xmm+DFOB{!gYlN*o&Y|+sc-`e6EY5+NaWxio3ZbGe2ZbEKMtwdH@k=&Tvlv<0dv@N+Qxi>@c0EXfyY8SH7zGS6C$Wi1`wirzvNgYBSNghV+OCClZ#8BLa+Lf#{l-!5hliGpYliWl3L3Tx4?f<8LkNfbWtIPW*|19@kzxnB(W<LIAhOMsu{6kG>P%(A3+g=`uNC#9_vqAe03X$Hn'

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
