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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e12beb2008d348a9b48e6d2beb2121b1/part_010.stl', 'relative_path': 'e12beb2008d348a9b48e6d2beb2121b1/part_010.stl', 'source_sha256': '2799a6668821b4c802d7d0121fe621a360e7385e905923fb817d2e92f266ec4c', 'input_faces': 468, 'input_vertices': 260, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2544323205947876, -0.1970137655735016, -0.24052616953849792], [0.179918110370636, 0.19637009501457214, 0.2554171681404114]]}
GEOMETRY_BASE85 = 'c$}r036u@jzK6>cA-EwT$h{O9h#?4}O;ItAA*Pre*F3gv^IT?<7+WL8LeOHKXI(TwYmyivF`OXgdAj$K#5?uh-|lnzJa4VH-s`NrzOR4w*|lr$UAyX3r$L=GX|o&ZC!g_W)jO^~r(t*{labx%-!Zyx*Y+LzeAuh^pj5`|l6yazF`qT5*PwYSqrWkvK!=Wf+D8{CXBMc?DWX6Tvp}cF=)TeIdbN#=?$FW8tGDaXr(+=R)1_VSj)C6`epI@65wqk6Ma*I5|M4edpbPebnm@*SeJOr?n@6`;hX$1bv`*hR=KXFDIJZgiLgZ_fOYR=oaX|jPhRXf<bEx{X<A1(VQRl@}?qn~zUFz4Hk|f6+sM<Fgci9>rnsZ#U$BnICeYZkGl_#m=x{)7CeVyC%$3J0<s=uh1<o@NG56ZvSRsA$ZWjyk-^D^t_PJCH?f5z7&H{(?9HyUk@56K<s`*WS#EXS?={7~q5`7=kU<LI2@+V4NyB=x)g<4|b(&e`o7<3n=YzWJz})VC+6m*0&NYCO%F*S?Pr%^7F&WPyXy|IdC^^F)8_S9hv$(s_UK8P5+$e@3pB++sYPgGVLzZMd5t_2`fF?=1UeJ!H+B5Zb;!@vnXHp*ijQn^sEj>N`36?F((kX%o9ojyvJ@w$Ssk&pkOBADVMszAmMYNq_utTSJfQq>q&OPR=>5FJ^6$9QTiYTSL#w9u=+fNii~?KHZ-Ng%hPebJlN4F>YypmH9}{Y2TXq_F)<4PR}-`XlHH3L$cm36<i|qN8DBOaw^9cGLJiUES5a=v%QjECf`<H<r6YVd(Khv$UKW=9OGule7kp5Zk$=>NIwp}vr2f7{M3$x@_T%l!_wXp^45{_<o6v5q+kBM<k`Bae0<vN(x0f2Gvi;9J9RpIBlWYy%vJMxRr+uBrhZr+xQ<l)rU`S@x@e}(OSd1Eo4Wn|zS)vzjF$6tBB>vioAs!_Wd1A}m)#MorCv1k$t`lXHubk(h?V?Q78xH?w;z@}y8Y<4VkDneW2sQLPwviDxvkqj8Z$}$J@U>3Sr^+G=aU--OTO>j>GC<<j?VY0+|cbjdk`h{E|pgEQYJ#?Tjv(JGkn=1sb8v7Pw7X#tup>jY3h?(<mL$KM_lPF`Q;31J?r+#-AgLBb^BJo%2IDh9vOe1ZlB!Hxo+P&P*gtu^u$`BZeQn5RBq9}J+{{UPmJJo<eyP4@nyMvt$tEyuCHtVql3pnbNfTJZ&-Vq{g@)>x^|}=R`;i{+%A7JF-5NT$%BQCRC-D7zMb(0Ip0Io8w<}j>F?3m$h=?Q+S;QvWR=?Q^|*!QjvlwZXSz$ipw<e>^|+C{^Hpx@c}ZG0LO8otE6Mw?u5>;@<xVZu)$%J7<vcoGmVLt2?d!aQ$_?HA!YNbbxIH4LdGxR4ynOv*q<+P&Dff-AJbB+3Rd$B7b8Eb;L!aI^!gIZE)J&YAxLb|CZa*xyXx}cDXQpud@KGLpj6-t1kz9{M6?2xbP}%h|4!ZrY+|cd!E-SfN;Rw$mv>%omdf#|{PqlMqn(PyPJ<d8mO+JiqPCZY3E?;d~50>7S!g5=;UqAC4p;IU2zDI5^tdnxz%hq<j<kd#Vytw*)R5Jep>A%%i#^3#o+>VjlUiXf)XRc=6+b@&ct(ac!pXQI`Yic^ei$|A9|8;-J?F%YT-X{xmk=*?@L5*{gYR5hBrK&$aPR7%BoBqt-p!SK8kJm{3!_>dNO^sifeCj^^kp8sTr|SPcS=OzsuM3@DRk_7_u$LZE?Y#N!Sg9AG<|{dWL**{>WvBXMiR2wt$$i_$`Rd$mPp;3m#uwiTGsMaD>mJ~|_Sai3oYqRl$4Ma18ZWugcT(3B{n2?3mFxbv&Bn&b=X$kYAob`^a^6$r7X5K|9s5qsf5>9#uRl&5*Pp>!DgWN0zC7o-Bgvh*lG|=Ad46zse(>k+xmx;j|CCx6jB|4SK;?!W=Ox=Dx2rys`?I6RP3KiqZqiSG*IH{NFJDAGM~+d)b=>l6<#?OpmPz}|Rc_vGEV-{?T6uo8`>XbKZj)Qp>Cb|k>xAQ~$oRVPjDNSh>!tnJ?Te)!dOsnzW|G%rehZhA+}L+U`e|`oom=EK$8|r6QuSZ_vO>6&{=fK29d}8dz0&?f`g7vE<n~Tutkl!%LFao^?&$sG@WTzlT_a^&oyD}%r}Rc?e?WURZhbi~a%-T<UCzsTB|_zO*6)#Voy>Lj@h;U)vyIYEgY(t7(Ol&&=j#NXljZYa&&gI|LHT~;+`S|7;9tnPdR|v@-|!VXrQUR|>$b6y8>zN`FZIf@uacWOAEL&=7kF-$^A3BSPtL=h=Y2EwtM6ySqo&Jo8E2haw#seB+28D@>d*Py^8MD1Wt{IlRqbD#B<F3<V}8s3sq)n8)%C~t>)c4Aa$Apou5_E#`EDI8=gB%u&R=Yi+~xXmYk#2f?WWM4!+f1Dq`s$)dALQ|ovm`~&ry>57cGgGdFV&`<mO_Pn>Dx|1K*oc%p>2MoIKT~T_;mt^?j0g(YZ@*3{~T1)od)eF}Aim_gXu-uIKhv{i}CHUB`@%&Rv}|KJK&Cs-6CAc1ceEb#CdL{+rob%6kGU?L?U`llnTh$sOt&D?6+A3O#bkJUaA8=SEMJoAk#Y_`WIahkf5P%%Q4&*3|Q)KddXA+u6ujSH1yDRQ(ES9r-z~&Mlqm^UAnX)!&jsQJ)vNMeb7H34C7;y)N|k=;S=?d$e7+%Qk7(PAAX%`Z+T>_o-YzXF7rJ?~;dof4A1WD&y-;$*J~p)``xIsVX;FC;sZT%GdQ&->V03e+kRoYOIINH&ou^hAsWv#`Re9mbyNtUs3mGy?>IMF)Fw8{#p4o*>{Z5PhFW0z0ZW_dOc@rD7j;1RqtQe4|VS9oPHYbPgMEx{Ic)Z{pe@g1j+3#gU3nxdYpCMjhu1zox3BszkYtXKRbHABDWi;+|=vJ?Jn1Y*)p5#=N9LsbDP}O=T*YmEx%8gu|qzm=ZoA=?&$i9Yf0|xd7<uO^hf7@azj5yP3Wxh^E+jH%t7o+GbTuG#70C3H<4$UFS##gj9UM?eR5al^v9UDK;@Nts_R0}Be_vU<*r_DF^$x?OdT%IKR)JB=RTcR*Y7vZs`08`T%MC1{hX=u8Y(ySb+M+htQ%u!HrWsTBh-2M5^70q|Mj-K7t{Asojc_EerjHclHAQ3E8mCwYq-BO+oIZU=u2^b*SSru@9#!JcDYYGtM{ka|8?#sPu~AOiB$LdLhAjUIgaBlpDwwX*^zap_hFs;bWS^NQmo|m>sQtD7yZ<^OK$1=;Fv_!pU1`2{h9hYH=n57puX)-Qs?zULW=!R=YDd%ANmHIRsGr5MV`}rJP#X#s;Y56UO~ps{F>*Joc$#KZ|^hH9#JfnMXo1z8uMG|nB>m<D0RLL*ZZ9GvfueLrdR#vIl(HLK|M$Ix~lp=i#%&y^&I(<_pXwMy?6EA--h;6zrXd~_ey(V?|Z%X!=demzBdkSU%xl@-akwKLf=0(Nb%Q^+vzIp?VZCgypqAlZggrF@~06m^nNs7{-=?yrT$lc8Yxve;{W@nk-~vKyz89~d>=1{mxKlJl6V<d2rq+|gJtn@cq8~3-Ux34zrfqzePIv0FFqRD_-OoVI063}kA+k5SbQm*fiK0^!@2l+d@KAG--_>oEAU<T9{3%;2j2{r;G6M{a2~!9UrF(NR-mkco8UZr6TSs5!MEV?@H;#n-wjvbyYX%CTYMY70nWuY;LG3)d>K9yPQ_>9li&n=5<Ujn_!zt&?1A^g+rlsKws>Rs8QvH#56j}^@d#K5kHAa8f_N#sID8*3ju(ON;zjTeDW1Ov3*+zMMFZs%SOFHsE8rF^hFf@5SQ4*_e-6vwpW{tnIlKwp0XD)r;Qe76ygxn^_Qi+d)8S}*I=%>gjW5D?z*u|-o(PxXiTDY)9zTJfg<J8n_<6VsKaXF8d+>|+8MqlggP(#M@l$vbT!|;)2PmG;hO_Y5_%tJUZBL_k{!O5K50AoC_)+{c+=QRTe}-G|pK(8o$Nl&PxEsHK{{pw+zu+g~2K*#`1TMpm;5*?=d?&sbPQn-CF>nkXgAarK@L~7>*cKmvcZ7}cj(Ag89&d^_gb{c{yc#TpSHnMr#qm$^im(V?5w8S4#4F)dD4u@=-@`w`3&5gy0lb6}+&fB8Jg*!m|AZ~zCwL3I8LWUe!&^ZMZ-x6{RosVnfuG}D@LsS9-U}ZHJKzKH;jlkG93KmZ;$!jUa5}ym-v<}r`|zLO4*VzlGEBrT<2T?5{04p>p2hFu58-+IA^sR%#2@2#;TilcehZ$$Z{b&A5`Go`4IaRM!;eusUjt|3Yw*c%8a^2x55K|3<5P^_-ZX{c`PxAF0bYXN<CpMj@F;!_zYS00xAA-MXZ#-i1p4tO_#=1$e}q4Pzu*t>oA4xl6TbqF;8*bDa3_8oPk@W@1UwGL;BojkI1C?$kAMU45%?h35g&v{!lrm6-W4{)yW;I&HM||(8h(nm#+$>6cyqiZtc173+ruh&d%QEn^9JxEya8Ss7Qjp6AHWj$2l&UZGX61M-w5t~^(mfr3Y0!D3jPz1!n?y3cz3)TY=(Ekd%{+DPrNtu;l1%_*aeTq2g6?YV0;K1h!4R>!QuEQ{3|#X{|a9Rm*ea3!*Cyd7(WMp!q4H?;br_f{uJK8pW@Hpef$~z96rRK<A1=%_#gOx;9dMb_`l#S{9pJTcon~c{|<k{f5(4?$M9eAA1R(6glq7F_<T4SpN~(3<ME03NH_%_iGK;#;$PwmjNsn7fa3Wf`gVx^9wOKM|AF)Kcq!z3FEJh-uZ4`yHO9~5?U3=j&3Jpf7c&0$m>-W%LgwoU^Xc(X$oxKH{yjc0g6qNar|_l`TtA*)hgXc?dh`4oJZ=Qnr{{-Zf)QNLp09&(MsWRm{uLZ&1g{s*N5K(B@cQz62pnVtuSd@Z!$>1|{dyh^yBfjk-SghCoe|t0Jnsox8^Qg=^KP)Y5!`<~?+#lU!TrkfDA?Wz?r)y=ft~SMf%5l2sY&rXFMI>fi|2r8@f`T86wke%RPYs;7JmhQ6TX4JiRXcT$MfLzU@g2JzL(<pev0SYVNHBBtO0A{HE<K=#ZCMzm;-+c&kSG1GvgU3o~MQeo*GXRGDc}Ao~H|xKRplpvJkq4a<6z^2iC^x;Q8P`@O*eqm>tiFXMySPEO<tk3eSlD4Zec^4bKJN#B<^KVIDj`UKiHG>*5aFi#zyV6wgzqQrwSw#q%_&RN2p<dfbldxtGqTQvM=P{tf5A)%YB|I;??L$KQb_{tliSzJ=$;v%<`HR{S-X0e=mDo#J^Wm>SQ7r-y0q^msOy4o}A%XQO!jcAzw<lPY!gH2>58${+l(<suIKAN#{UnesJv=qK|87DDn%?*?_!$v%)e@SnE{9roT*8UF>GE|i='

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
