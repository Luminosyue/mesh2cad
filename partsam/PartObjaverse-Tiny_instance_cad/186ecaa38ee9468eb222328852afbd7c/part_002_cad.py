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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/186ecaa38ee9468eb222328852afbd7c/part_002.stl', 'relative_path': '186ecaa38ee9468eb222328852afbd7c/part_002.stl', 'source_sha256': 'cc44eea9154e2dfa268fc6f2f2b48eaa838f7be94b5b97357741abeae47ddd6a', 'input_faces': 256, 'input_vertices': 201, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.36885756254196167, -0.2887628972530365, -0.05223008990287781], [0.16079369187355042, -0.1772441864013672, 0.3114396929740906]]}
GEOMETRY_BASE85 = 'c$}r04_J@qzsDcRnq@>7n?K)>v_+AK8Bfdcr~FA0622lrk%X|#GnPh04MmfE<xl>U5Tk#3h!UA0``N#<?6)=M&luYpJIDDx@6UUuoa>zHI@dYh>$<P^>wfonKKK3H&wby|{rz4A_&2s~t;okoIsU2l=t+)>Vw7e|Yh`J8Ozhm5;fs4Mh+f`Eae!}p{?<)nCX5c4+(=oftaO<bzIbMg%RrOMpxNFoZYG!63u9tqW-OS#FlJV`;SZY;xj5YFFOHZI9d51n=;P7b&E)CoW_s83fBd{;?SdZq@jptfs=C-*F;qEmJ#~mxv~7v-EfXGm4!^}WTMb`r8wB6fyHI?OVTp#X2M&c_v!PD>)TkZsJv=3U@dx4$?UaW6Eq?q0`QOMDzej#1^7|CQ*B;Fg|C_S+5r01ozOK8A|J8o<Q|&YYzH&cA{J6Ajh@a#L-xS_f{AO#S4PSZTm+Pp97hi@(7p+6Qmj%8)y{W`cE!_;ibEL!{S|{<Qmxm&*YB+o?`&IGV4bae^zv`;-_eP7vkE`8?c5BbVS0DWJnY0_S1lMn}Nc`<M@g2UNhdeQX)iPd}#qT?2E&R|<@U=d}#J9Bn0C@|ZTthwa#wBP<XfSkZ4t#BGPl-R7z8w8o9VhYCdnCSHbTah2Ao!}AxA+eh#-Sc%2VZwd7T;r32>LVe+Ex60NfYr$&fEk&mIq(ElwO6pd3QXne;5W|sk|$`_dg?WeWE+_%ocxR<E_wJ_VD#fbr)qmJlTM{b1CMlS~*(cBmGvPUYZDBTT&tM)w{N%elY^R?lwjIgFQAQzG(;MIVAq!ryoKCZ(|;4)vn^FZnq$AS~+|@vE+h`&w2Dy^Irj9?a@-=Tf3$r&Ub|5`6yZ9OKxUC1DwU**G2rn(=xFhzRbtG(Q0GGpHjKSQ1kpT@YTFuE8#~u?LqwaO(p(Z0({NyG5T5Ky-c2W*w+%je_96ey!!;tNy{5Ae#)Y3#3z-)SJ&J*kH0@0ybJjqRf!+uEAcI_?SOxDg^c?fg@{*1?A?$2EhfU(R!kJXcq;m7-e~t+ytXuSC;a5yxKHig9Ety_<Um7TS!E-B$F6&^o`beayl<@J$vP`}x?hoc<LwfE*#8s6m&J=;)n5F-UAy5oo+f_oM)5b^L;p>Wi^@?S^`hKw{y)-jzdfDH8@8)>9FunE-#7=~-B#jz{fzNcUE<Edw~H6wp#bw%xqGk-I{t>_+4mLZr(WtSe$pz5e^@Bvmh<~*)Ze$2@rdZW9C@AY>(G?fCEngG4bO4GZ1D$uFY_U5C!V9;eAX%S>&Y6)GqfaT2(H^vB<nj^^6b@<pn5a-`qAHIUHc_qf7Tz|EI_^aW68htDaJulYfe5l|3{5WH{vz#&yVBp%_nfag@hWudaNIOWoDhs(_+^{=+BL+e6)K%Tk?EXcK~@x#=x(!?;`8$<gjaqFR+EL{*)@~W7qYo@MrWrigx!-lXmZ{-HHBttUdzY^#R(|J-SPLP%wPcwwAKK*B46uR)vR=_nBh_@|;LdL7rVf@D;Z<vd{l91@T(-pLwXaSu4+Xd^pBmDO?F(+Y^j-Yn-F5Aiif_E}rusFKO3uU)p^T3SZw8iFhsG2>PixK01j0Wd4ZpF|BNL0`Xh#iGQX@*6aNI&*86~1>gK@wanjyRx+NBK@#6(7RE<Ee(f-P=TETyv>|1<Fa3Is^yiB*tPkz*739}ze@Fk7z{Gv<+qp`+xj$Y;o{k%_4)pR0tb0pUMk)LRd+}?!$haM}Lw?;R2J2g2d0qC80iDYbf37op^{x)TCampeh!1Qb@#A_+e|-C*Kl-glSU0Nw8Oh`0UJk!F5x!oOEBjEML#4zAi66cbzPh^XBHE3L!E@98Edk@N`i#c-t2f5V{{1Kg@%oHVjI&lZ7W<8&*2;Rh8ZYCMwjTSX8q`k4q1k@)UmM~1G5o<l;5n)`j#cnCW^O}X+i&34EbEDWYO$KU4~KsVUtiI`T*h;r_z&{%eAV5z@f?*6)8)OC;DzU_W*j;Ozp#hIe_4%vK>wny0C{db#6G7F$UuJW>dQL(Uuxki538h~IqvdYW=?{yb@i3;ugjA8)?{i5>duw8Uz1}y%m?MHQv&?6S@Il*gyVjd{!_Jv&qb@4i~ChxEsjM!xfH&+*&^JpQaxr)!}*|(i$i}D(+wZgpT<kO?(5Kh#o>Y`e;*?A{Pg_e=zo`-c&Jx^>@!dH7ok4-AkMSq{dTh6r(|JY(x<e+{-=DODC3!Z596r~?3)GOcbvSJeEOd>>ZWxqcHz2jeI!2JUY^U-FZbfQiX7ROg5E)1v$i-Jer2@m&j<WU5Wnqq4(8qPf%06!9rIDI@yNyBdv=uggvqDjhaAm=c1)A_zwV+RYWK(RbtfOWUr$Heuj%@a(ywI^GS9P<Fg~XFbC2M<F;%k9dsJea&9w{QYj)kFUGpD!E~c^!_<Bfpng6$rq2H$XpCr%7OnJV)R_}qo+u<nUKg^eSJ3sWtJT(Ho;(inPEkDne=cu)p@$R-xo?}$qIb46kPy9ch$@<+l7xCuH6X5HWS7iJLetjN!e!eDt=Xa6cy!!4L_+wXpihk;osv7#1r55<g^-;)E^YgO`)H57UG#m$uYk%}dP3=Tq-uwF7xfkF^eTaFX|9M)T%LOlqU)569pRc3jPx}q?U%l;C(6IkCM<$_N%dLwN&-0kNJPPYb-5XVi_=|mIe+ZmdA^q?yYS<s;UYO*+8Vg^ytHpcD((4=Sdo_RdE{5-Q<bw1kSoWXaoJ$(Et8^SM@iP<Qt3LPTeP_G$66z7xCBD^QnJ2|=h*vNDa0=rWHb~~xxcjp2b#RjR!@~d>H*<>Y^NrqyueNWFJnHD(vTt~ImHp|p%@W_{nY8=4oA`g9f5L*W|L6xi#jo&}`&z$6;=AR;*H@pH^*f?J+EvyZllX+i(*L)fTyE$qNu4C#bW-~Hox7~RM}e|$H~$R2`j;nsJ@}dAN%6xzS+i___{$E#H~s5m$^Rr*{F&d%`+d_K_~s?~@Rj%^*@pwukw^XLgtU9hTjo{RBZ+VAhWV>{&Xs*KQ9-=fzCV0D*(C45-nX9fwYKFlf4U48e`n#DhU-GlN|SxQqb}>F={fN)y@~god9?@j3H^Mce4nUEkoVwks_fJ6J(2x?<88LPMBXRaE9IPXMwdL1A4~k3%W+PyjJYT8_osQ{JC#WO&7P8fbAhybN6t}}JV(5*_3ZN!zsyd~8y_{7_<ygKc2Dg`yxGQE-tWC`!B;!{BJE~*NxO3%z_;9#?~9f_QzXChBZ>bYTh6f+^W|JOz~(Ic*opG}wRVf-|HBr($stnO{cW=3zhVzxw@pEQbKNS*@6ryw5|V}fm>#DgUftCZzGnYS`V*Zg`E5GGH+z1E{H77_Nq<s3#eZd`^yjPga-JO9PujgWQqI*AN@RQ@2g0`m2g>*3J3A#$!8pmYqeOlu*>_XoznCC-mY<W~kp`E`eche~zh+S%`F^k7kv!q^WPI8L!?z3zk^Xm$l6FsfNW1<`_*@bs&kwuc*JQei|If`bKHoYZk9m#X)gb}T{VJEFThg><)+Vi`snS}RJ)^--a)xPq{?`BgC%L(O|93yhdG-7M{v>zI+J|Cm`IM@YKP4AZ&yWkrr>N!RQ{>as3i4@k8TCB5jC|HwN~!0l=gH^D1uO=aP%FqK<RWT0xrls%dWL+0e4MJ2kCXGM#pHbQ5$Z|u5%OW`QSxE(A!;7^5IL8cL(U~1u$FA<L23@!(EVgX_mU5i_fdC|_mTHdE#y7qEb1rZEOI7wJ2{h_LET2qAg5E)$m!(G)J^2g<W%ZLaw<8Qnn+G2ucv-UUQb?2jVG@qucB(?RpfW5YsiLvKsNL}@;l_^)D>hymy)+wONzC8#A5IUY7%(^c^x%@ypFt@#o+g?CC*xwS<4b?EZNYxWJBkX4V_P3LS9UbBrhh%Q0I_i$cw16$&1L*)Npb%c_DQcc_DcLHH^G~97UZ<jv~*bP9)DH&!CPY&mf0TN0URy!PXK$^{0*|`;&*W7(9YHjy!_wN1aIaBafv{C66VKr-qTolP6JUktdNuso~^MvY9%YY$i{q&LK}HPoqYXr;(>n=aZ+9CsXH<CzAuM<zK92n6>z@80>2;L#;(6`;v!H-y#no526kv4<Zks_9qV@_oMbD_al2!dy_rMeW<<2eaP<AH^}Z}H);>E8`+iWOm-!Ar*<KCCwHZGCU+&9s2#{Aaz|==a!2y3)VAbT$*)iy$*+)GQys{y$t|fblUtITQ(q!CC)-o)$oAwHskY=7$xW=KF|`rZmfVQ^_s3uxsvX&e`~vkQ@(bjq)R)Ok$<3$^<Ywd+R7Y|Paw}?Eaw~EhYI|}Uayx1Vay#;C)XwDB$epNN$eqYeRA;gixf`_yxf|Jq`UcsB{5rK4`E_znYHxB+vIn&<*@Nsw?N9b1ds7FJy~%G<-y*+B9!yoqgUN4GhmzkWk6|%*6pO(lslH@Ghml8;Cr|^)hR!1!I+r|w9K>R91T~f%L0(E-MqWx@&SLO8)Ht%CE0y|py}_%f?<)0Y27}j9-&g9-7zVGWCMfl15`&YeNlN`0#^6+Hic){(F?cg|i&B3^GB};ORjEHy8Jt1=SgAjQ8JtPoq12z*49=qNRO-)o2JfNnCI|R8vT5D;fBKh#`j2L82G9M2!GFE-`L8_<uS~P%`p+*x0sc*ly}`P1*x=AH&Scd715rS<i~'

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
