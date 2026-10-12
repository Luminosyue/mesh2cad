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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/144bf300ef43437096e4be61f4575bab/part_001.stl', 'relative_path': '144bf300ef43437096e4be61f4575bab/part_001.stl', 'source_sha256': 'bf80fcfaf9ee9c545ea4c03c4bba35a1e49a75518fcadb31c1567334c96f2318', 'input_faces': 392, 'input_vertices': 233, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.04645984619855881, -0.29517486691474915, 0.0735006034374237], [0.1765454262495041, 0.2281430959701538, 0.28802040219306946]]}
GEOMETRY_BASE85 = 'c$}r033N_px5p1c(bO0rZShtRnuwB^r;|`rkVM<m>_nwXH8erYjxps6s^(H&v{FJ<Ma*&#A_PgyLwS*)N?R>oO#OP#v;Y71Cf{B6u65VFZ`WS?cmAI2XP^D-^PFKdBCM2$mxkXPT5SB5CcV8iO_`_WrHze=8$Im9nE1fhQR7Q!l|)xRw_nur{T>m0N@!!XiGD+3;y;Y@YwhrB`%z230Egd4BjZNLMaK>r88;+G>7AoT#K+ir{KwIwV(jAvO@o3096=2O9FraY$6t9n1#3xGatD>mfTt(YZRdCpo2QP=sD~-aTW6b|Qo1Xye6Ea(9k*F|z1LRJ^|N83n;+NPqP+9|>XS;h&fU%teL~dth@U0ntu`|e=ka9GtrLw-%e+f=oECkBDZ1;x+~Z0&yZn4g;_OKj-At>NDf2E%m+{u7-H6ln0~xRXH9^Mf&waMa_*zdTA0y~C;^+1hUHiHV^o5TkPi;bq=*CRUYbA7(@%oACKZuVnhkVj?iElmZAiD8NoSc_gxKPf^@}H0K9@TRsAIF~($DFrZbnV3;nOEN(fbq)?AkMa465kd2G3Kp$Np!2n6&Y`iiA9|=uR_nr6y32C`MB;r7u_+;Q|f74T6$8(jeBXE%$t;#rF7@#17*DSc1_V86*|khn}6oYcw<B-(Os+7i*6bH5dY?2jF0>lbq-6B@mi%%MR%^tl6;)q-;{dleJ3MMvWJY<b_e3Td{>CB8&i+Tzdv|@J{bw!vFEhpY0a@v=dOnlCpby+agO;X*4O{E=*DtG;^<%9!n_ZEMVy7cnD@z3$<ti!{iFCZon^c^^cu$B>M6RTTshRC-P`Ds-NQw<z6+M|j_Me1+#e~rb8>l!Z_HbaJRdC<UE4Jb^G>LR{yg%7==#MV=?62Ry~J^Z97OyY4Uzvf<nMfT6Z!ah%6Lb{7|CCcuDo6Hetb{jJAUhn^$qnB-DvNR^LqJLiDNBj4E<3*<WqLPjCc72iS9b~B3t^c)2=MZ`$8+xt$s_T4zAmAGTzZ93gi7z2W!;}<QY8<@%6U2E=n8dtGwyRb4w`tHlmc&!N~hubZ1lSGsdAp<nt$VM~g0~bH*#UE=n%MyyZ*D_2ujki}f1y4f1T?5$lzp9T&aMQRGv74f6T&7S?5bF6Nzb3H_7)74kfK2l~QykWbQc(VZ`1Q|0d(?3C+B^Dxn$TMme>-<g4Z?EZ4p`3LVE;#++tx>38b<YR3aFS=uU16fDohkNM5+G|C3&Do6jt6F8qxGC2}HwR)r)Sd<&kvyxFN|W=NTL<;r_&N5IvQ0#Hu20C7e3G6WlJOaXMb~O<L7rNM#L>eyrQz?=Bp+?_S<%g!XQ7`-lsMWi&-Y6H_1@Sie|I|qeS2|rri@z@D7tgg6YK-6*U9;6cit7<Q7=DF;%M7<iJsF}bSu$E;<#p<J1ED_MTm1fR>tcE8%5WfuN2*NB?o<YAs+J<Tt|F;pXBKZxr_51a7T2r;$qaH^QC<fC$$mgpM4njsR<V(Pcy!W=*HtWkms%R-J-7>iScP(sPhi=t)87Gy4j^2>h@|X*4O)%=+@L*(4*ctDu4giZ_rbI$2vYJl`e7mG?RI(x2_<cUPIBJXP=9%xBN@Sn_i7E-rsYN{QLd6i0|qq*N1kwiRi}8$Ebhi*b|c9Yb{0BP6VOPx>Uq{wr3mB^}5rrpMUxc<Kx4iUmcD6R6uw1d3wC)j))4fKj<?uvn3B}1M&%8DDyh^rX$Y7Jm_s(N&WS|zrlT>d?o24(;O$dW9(7n6$)MVZis$cwG8onf-rvIJv@ip+KTb7w?sciuax_OvF4eK*CV?^_k1DwTOX{&_=0yuHwIoseS99tcr*BY(H$wHQHS`cqHBo*kdGcH=c_qu?w9c^VxZT&i+%X#Ld01-2J`l4fI6gQ@qEXM?yPl6^3;YlNBqt+5a+jA=-cYorBAFutB_CG-%<ZNF4WVt8Tk*5MSao+A<iA>+Wbj)-Y`S3-eb2Te$IU9TkW|Y#)nvl|3wI{yS(iZUvr*8{@Lm1s|O=c|HO01zv)t3N5B4o`_6d}xt@%!e%L?XY>54{(QDANO<XU1AEIxQeMNUP{u}#`cd{It9`(dqdkb*BCl8=*1DlGjmDnhC(<jx&yaU=J&P$)+x#e5~)W2L$%)4`&te0cQ&$18bDSbtE&GJS58xv5^;C_fx0?&bF`BY2viX$<;cMIGf-+X|4%n8Wzd=BdKdKmQ3MC4g83C}q@@-VN*VvL`$2G3*Rt3|g?rege|sgjQ~t0J!V#0>0D7t#Obrd`<gv#+5}?`=hW8l1-Y`rknQWis(x>isI7hsWJS{22=nXLLNS3$F*zdzQlWn8N#x_Y=ff|25X-VleLeEB&P3t!<&`&wZYVKeVOjT1sd1Vb)&mr;(!TeQsgiM+=bu<Kdz^?sh~yGygyz)=d!I6>=H<c`sAuwI;8{bvC&z;<Ozt>t$`-Ai8tc9Ms`yq>R_YHY0wOKhV$h2jcn1=O@vP7s;}po4@7YIjns?^rfH5zN+`UiRYtjk1_9T+&A^nN04W7A?9s%2+yBSPI7<qJs|Th&BVNk$FVL4>x-_nOT|9((mKS6(?xgITY>Aedlc?Fq1{C{<~2t@RP;msUb95Enj}h|&eNV4U*apo&+^88_<lOpanokxQ#t_am2e(;j=u)|>ULa5QEQ>sEfC$6^&I=;i4T$IKYiqSH8K|Cea)vM?rZl0a2*e<in@(lk31HIV7%91tmBgQxbL@(6y5b?EBYk!o5Q02YoO?kLxa!{R!#J0+z`>Nf^AYC$5JQyu+u2$PafiVDQXY)$%$)3*DgQ6e*4CK)W7qO$fw^)<ay&?c#eL05#u`y$8*c3u89BOhUjLQ(Xwxt3)>*huwS4@Y8XFeF2;8(Df@)0^!Jjd79ApWFk3Vi-CBMCeX?PJJf9d^Ytgm27Ot;*-%A{$jDhi+O5#59d%n!;s5A!gjY8D(h=F?EngD&~ROo}x;CjiOC%WG7+A-0ScFTC9<3`b)H9yDmL&^lq8<~rJuEPO5hs>*m>!|8I=#w(gpLJf5IF2rX^8DqBekSv}?nj^wHzV;}7I+uWE$7N0pQinx_vwxPOn-uXBWWP?=}D;D$+vL4VS{)raVGZXpNGqSqSr}*?)xY9+ZW?;KMTkZ-I+21&mj-a;C%nMg6GGu`?z2GzmNC9;V#7S*&y|C?7N5j-wnV%ov;Y~AHEayPY%XDeXpD7&Su`YzNU@G_-~uwdT;opJSV$8nU3epv_9N_Hsk%s3EkB+mE#*reAkU7h_k*l;s;cd@y=gXKySDS`&;Mnd{567-E_s{{pISXcz;}wBf2B<8ODF-CC5h3^T?;LGU8WRiTC%vFG0`lihi5iPU_=WaT$M?iuKZdE0p>;=DSdbQmfI=6Tim#_V<wM*wt$#&a2UBJU?_RBf51m5B+d39`Cbr${$9bR6{<`D&sk!z9-_$pNTkIW6&pmRYII*c~}=OU(~-%4bjcnm(aIU)39GTTOt0a@uFK*3go@X%#DG5Fbe%s{*>gYS009WUoXVITG$Ksaqn2n`(6dE<69EnxHA>{Gp^VDzpyTYr$Y~4kNV#jgZxLW7TtLT^)y<{#{20%)?xe~_3%9>V<_tLY`y4?8T%0b+GRX<WgHXTD0f-v@0f7`&k6lq$UmYk&MV~w>Tu-|=Y{UtRRQm<0}4@xyv11e;dmdn@~L01fbU%%`_Ly>pFppG=YMT_HumQdeo|NGY6JV>FU|4&=YBubdwVyz?yM~_a$c@8@uFLEFQ9)KRfZnC9q+X{HSnFJ;34YYJYRGpya%3>CsmO56xXR=Fur#)T<>2tL7r`@%Jt{Gc?9*D*8|@NJ_*Kkc{>O9g_hyCz5<(xZqz80eZV-EhxhbO!!SOa`$>Kcyzlr=!~3z{Q{;b)@7L{<@qQd$8|&yh0`F7D&LPgmXV_=1?#H_C@|XLS<L52thuuphjx(>Z=(;u$bvWAx@!!DvqRUwa&ksLE;k+(KBhKdhqcX1<D&J$B3Bz$eJpV4<gQi@;_o(tKL^rG9y~7y$T5gAkfBPz}XKno3RmBcvTRF{3`zX5DCut?BpWFZUpQMKc|F1qt2eoSY|NSKWmYqX@ZST@IAS+*wTu)95tbA><@-@lIze+B}Qk18uUqzbwRi>%mD>U`<ps8O;n);QXX^b6eTW8yv(iFc*Q{0lK_#K+!k7<er(G>Th4<(njt*UJm=<Aa!kn7U7BG)B1rw=DLC%2#vBP-vQ+=ASMK9JmmT!W^#3N5hMxd$@uP;xK&w&b>)uNN(>*tv(X9%0PSU7v8)ES%@_4t@P%^{met*Jq8~HLuEbXi8s&zACvY>+3!j#pSrJ<+#q}sJqu)aY_0LT2XH(_MopzuFJZ+dr9#t^ewcaep6hTzKK@UlZq?S*U*akR<XOEYcStZ<Z|>?$ey;nWSiO&%952<hOD%g$x5q4R+<l4X|Iue80#f!qih>!+lMs8AJ7!PM^hX{Q{0cHcmz%H82VA<>bCjWR*l}DT#f8a-<Yg?Fxi{@I(;+p>tqLg5ZOWYwXF_)Bl;k6Lwfi5He#-$$Ybb($YaPO=$jQg-)5{qGv?>6Nigda%=3w&_b*mMf7aEXb#d3(kG21hz9GFI*^f1CNK;&kYpT2_eRZ-Yxh#D(a#?a2dT+8f>syAV_+@$r`DJn?dS7xSvQM!!@S!PwjaG;GdXa0<HzK>&NpXMMX4p2Erg#!f@j{y7RW!vbXo~+qQ~Viye{!B}Cu}=p+g;o4*mm2t0v;>A!DGc&d93&{j}>3zvErLNR-A0xI@=b}6wjk6UPDv7jixxArr4q>-cFxPHf@_?+xyJ@Cg;t!?Urpn(G*{yzfQhFK1+Xre3twp{YmnV<SjJCd+AS+mA^>dOU|+F61|K5BH2a0NxR6}T_aznKSjPwzDj?Re3g8I{sQ?1xq$vU`8sP+KvR5|KA(J-?5^t_=6i>_JO6y1Up{MniEDF->voB{dmR<0(_hhw)>`p4`m^M-th>866tAJ*q80UzVs~FDUPQl_yq9%%_o3qCVr!FJEN{i*HT0J1t50~WxDSsN_vW$U0X$YblE;dt@L2H@+rF}GCQb2Fn&LS$#b47De@9ciiKh5l`X%HAw#~I|F-`H8^pnY7l4sEr$J2jAjwi>^_a(=Whto%shm$ALk0mdm|CXjWiKaM_ek?hWJcTxvwHrwuKp#yWK<-W7m)x7&hyEjSAMz*klgX1=qfcmax!!YG)A2OLCUY~HuSwmV{{o)h0<J+4&pnCjmPFmXj*Gdri@7%LwO0H!{Veh<u8q4l6wjfL(Te&<@l^WZT2YTFo=HEE>|Q6u=QZ39)V<&gj}>S0SaAlA6(8WS;=?>ve1gY{m)W-7w)r&0U(gggX^J<}6mO;}PN6B@K);NfYuh>7j?)w$qd!ePMm|VWyo>$_c^5gAeh)d7yn}uxc?Wqn{eJQ?`VBP2M`?<)==YPe$R}v~S-ZpJ1N1w|2gn)pd&n8&Z2BYQZ1NfU)8x~v(HYt~uJ<|C^gK<m`xzmR`Q}k~=by{-%jFsz<+&f_x*etNUdQ8H+v8jt_gWw0`XA#uZKU6&74?Q<Cw;0`)IW;9px>bt^_b%M^t;LKbyD2Pww|^{&=kkg4<)y=O?{_mO;g;4rZ|MY2RVcsY1?f2A@n`SL&#m|JCHkYKE>VWyVAEKcO~n#O`wmZ>BY`P=lSUz--*68c_`1*peg>8rg$`cC-P|WIQrJ)apVO0Hsl0y98Gb1`Vew^a(DVja(D8uVs#uwQ~V80@oJjlmGnc%E6K}gir=R1LUz~sZJOeawtY@NoxU4+I(Zs>S8`X@dRnoynZ`P+`mVL@d)t<hmvYV4(hntXwe1Jn_Su$cTN*hctVBt#QvcKcvRU*q<pWRg|AF(r{^h@aRxAFOOYK<y`H?Lmth9Ou(n{L@sh5Rq>a9fk5A@TR_y'

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
