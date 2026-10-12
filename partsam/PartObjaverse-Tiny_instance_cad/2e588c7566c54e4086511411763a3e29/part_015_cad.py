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

PART_NAME = 'part_015'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2e588c7566c54e4086511411763a3e29/part_015.stl', 'relative_path': '2e588c7566c54e4086511411763a3e29/part_015.stl', 'source_sha256': '4c1f5e76ecf3e981f87d70d6d6af2a3b626f8259aefd9ee4574e6c20b4bfbafa', 'input_faces': 640, 'input_vertices': 352, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11290062963962555, -0.1527678668498993, -0.2128078043460846], [0.11938479542732239, 0.2431851029396057, 0.05684556066989899]]}
GEOMETRY_BASE85 = 'c$}r237Cy#|Hq%P@077`2W87x#=g$6jeU%<gei{ojSATnI`tw%h>)mbtE?f7or4#>C8C82or-u<lv3K?^Ly^keLVL)^S`eD_5aUx{jTrleEYf2Gta%>_gtlR&YmOQQ9l)(O~3SdEm+ZUBnmk3&V-?3#tk1lbZo7WqbJ8XMO<Hgv@S~N)it$moHN0BqUw;LV+W6^+SFII`LM=SYx=4V8#QL!n1Le)j2bg!sQAeP9~nC|>W_VB;OL>z&(-QRNUZ6rSG}fhs_*~!lP~%R{z6yw9gJ#t(2PT(!RF206^&ec&-H`J*TY^v7{6cT&wkqQBU9JAzLTw>;fG5vQsoRNc+kk-IYs67JHOxSJNp7Ef9_mY0}Y$1@2#4o{Np+Hdi_vBF;!0ce7jw((?pg3+t+Sh`0~6XZr<@>uY3LAR^O>4j~`rlR{6c03^%`eV^#j(Ge$Z7jmtJ=<vW+^ul4%6d^=zJI^RELwJK-eT=)G)S~qvUH;`wMQGU4WpsiW?&V9K;USF4Q=f}R6{BY~puJ26xHSGP~;G{{)?={z~-!F!^zW=@AX8le}QRP=JZ`SYAiORp{JEML>(`uN%*SyEJXXOVLo?PnnW51V`uYH~G|F*n({>!sAxSuOGa=+LAOmUSzXSva?oP)pYarM{2M!O0geQ%F?AH|Gz<<woe$NQX-sS|f(<vS^l&-eQJIqm#dy^tSRF-JX5k3tznd(NA#`~rz?UbuJz^_-u!Qhve`v;9oG&-MN5a~QsVb7}RQGnbn6UOcyYp1&#@^&5Ee``xNP);H=m{P~65M!z^bIwLFJ=^c2|>&N<ql^=T#<ol+dRsQuqjrJ3`c3Ra(WUX1hv-Ya|o*VZW?d``Gm0zQbQNK?5VpYzjZcE(n%~wyo=U+!De?sNm-u&?JL{(0?3P!y+qw}czz%H|1ZvC;#ct6Yg?8?e_Lj7ub{n-1l@?-CZeE;?}%D?@JS?}HEDZgO6;X5;?xW2#q+Hh9BGvS!=J_FYuQu#}28TtNa(^UC4I+^`Fy@~R>#~<+e!J0l*{<Q-}y+oG&wbT7vt-3j$=l*%8_x%J%C+x|}cb*$DCCTIK_haYB-kZ)JaaQ^M`bPcwKYh{lovXFY`aS%$`ke2o@qQv3-^nnZ^NsKJX6d(VG&jlP$DY&5kNM<>PK1>I^Jb$SgTv>j=V@8R?ANbMR{2+V81)s(GfX{CAj$0S>$<6Ob`3x1^?ef>D*vejqaFi~msaJcd}P#P`10+y+|M_g?DhK2w<lfSIosZN&yn<n%I}<Pj&B8~z2$vxfw)Ecv+|uQTNfvJ{Mh(!<;Uus{9v1lYTSLO^hTo|YZTdGls~N8!7Tk#k>yDqKUTh#AM?rgADgk=C}(Xuw;nS2aUDb6{8%|we#|G|mz3uE&fK@%_TcZ>LcRa-t(2d$i_uO(8|t{e|Esg+I1pb>m7hMy?C(?aDnEXM(N6rOf86H!lZG1YB=XHCuJ3HlZH(LDN_&<6OuErd!iScqa&n9^`{O(Pm49J;hT)HkY&H7VkJrLk`Ypd)o#gRj{maU~)9+M%sKY_mcjiqt+DUkXe~ZyRS3PwoD?j*i<8?_MKh{32{Mh%B?>n$$gSQ-i$()A|X5oiVC%@*+kIffWer&x&zEkM<tH$%s8}H`ZzW>!c>%IB0=eP1>-%GyVzj}@P@5}vdv_t=dg|2U}Pn@DpxPEv{S;O~j9pd`I>FbPk=<AxI%883N{6P0a<-c^soOgN^SN_Yxjdtj-c4M{sdCDrI9R_E7xZ3EC4bL3T(jPZ%Lz2gj^+zi|=93@!?YQeZ1NIy3JTPL8${&8pXy;+yiB)d?xkhULz<$KvY2iwvJ)AFdBrD&!v}$9L$B(rKEC0@Zg#4L3UNFk9n5yz^|CceFy!o;6t^Alze)xmivyJw4YLqI^_P6|C<j2~Zl^^rTkIWu4#&{299#`vh%a82`EkAg^^k#24vG-$@WA7hrUzZauH-Citc~hIi-hQEdC+*guto&f&SfgLW@-O}t&dRsP?O6Vv^n+RE-~7THpLPD|TYIzegQ*qv80}O0eUf%&<vZQVZT7a?n7^co+b$wy8>(@jTHldLS+s{tKJ}}8yFFy`b^A%^KFeE<Zl9Ta-9GW{_MFKlKa@Ufu~82F%l38u(!SjvZC~d*$0n{Y%3++z<TK7_-yWAT`Q(QmuC>}*jvnW2Uyt+Jx90`h*ZINOJ=eP5SG?&WH;?^MAZK}Z-m}NIK*q<eZ;ywOGJmZzo`?C)_Vs+HeS3bi{n&h(9RI5OJl6Oe8QaYD?fD`c8l>{A`6akwn)0prD6nj~@~!#Hzc@pcZ_Rhkfa9)j&ySHq7gRacd>VQ7y6b0}f8Ty>y-~lcLu_BKL$q(NTWmkJZb`1T*(itgRVJVHmG<rRSSFu*XMB^bMmuLcoXKZBtbKd^oXOYg=Nmh>xt~+EFZ8xgXVlScM)|DsGx@CZwQuhWGWmL6FmmX2_p`Om^zY04rkiiAd&7I{zG>7W`yJcY`yK7u`y<<r?T@ZBSH86l4|Evl`u4g#R3xZ;Yn|`-UsUB-`+~rlH<WMhBXS*6zBPY^-v8M3?R`pU`4#oO*1pCWdRzI{J}A_0+76=~vhU91>wP!Ay-&~N>->!MZyDw2^9Re1oj>4bI<K&No$vHG;`+|&3k$sM)4#4`hU+gYzQwKIKkKOXJbb$Ht$nV4?bZzM^XT&>+mD?u;oIj?wy*PjvkLBXKMz^>f~%aT`Fa*n{?+!o-0%6mmKv|RHdVfL4iLOJQTf)nLGZbSJB{b({LuFG`Jwjh^G4g(`GKSr>U*DlIPAX9ZxU3$%m0eXx6U_wp|J9;^AP9dld7EUj~ewA^Pf*N>dRSiUitQU%e%LfZ=KKhYZXxM(K^rZ9j)N{_W4h6ejV4h&x-;#lU2TTz7!bWWtaDT>ho&bkDXWJ+vnT1uk$07)70~n>S448XUBZyTjy*}*B4YdGk-bk{`X5Y)pM3wrt;^0XtcLL!bRgb^?iZu>-z%j+xH8$AIo3!xAId)n(gFF$=#~orkM5X_?2&+EBbdP?>3&3`x@KV_chwL?{{oJb|3V1fAzh6Dj4lBv|y^rx6VI<ch5AwSKnLNzP`88zJ1SS`>}hm^~;TN^u9^^_I}DauvYoj`EX?KcJ+Ie7-+N~f7&tSTj$KalrL2|*12@3^ktR5ql9t(ADsHT%D2w91M!9TxWA`$9v<FMN%_{fy7ujJb>H}Uu5X{u`_6S#zI~pb^D$M<oDpWb8njLM*1bbu{y9~Sbx#raw&Y&*Jm$TIziSKSTlXNLQhwLZbZ@d{pz^JImPnCFsvPTHCbE92%D3)u{GTjQzICtUYra|e);*N-LD==}d#k|8)2?sdbA?ZQqn^iFCx>ds?Q?zW9xd=(J>^^XZqBu_u5aH1hA*vD`PRK*X!1doZ{0J7E*@9;*1cq4{AViPx+e{<{Ym-Oy=pjj{{8OnYu&>JUoP+Z_PwpsAW`|&J#S=b2iLdnoqb29y1so69<Fdem1Etr2TNU5`PRLB_={WzRQ;Ow_@N7xTtCyjf5GM|-~Ky+QE4jQ`nv*u)4{H9{~dzw^aNFo{dWt_0+sLmJBL)`uQwWJoU0KmAN^0!$m_&A!v=c)bfdgV)0*|4ZVa#gzxvaShV|?GfB$r&c3gC*k47CrI03yEPJpYT<>9KZ4=oP+;F4%=xFnnx{o7HT7mh=3!xF;3;r#^v2LFs+fq#bogMI=32mT5@4}S$;M9;w&;ZM;I;ZNa@(c|#P@W0V8{BQU$x(_}KA3%4(2jD&E4tNiofo_E};O*$k@OF3=x*T2wuRxc;E8u15^YAiwG5RdL7@mhd3D1L{LZ5)2f~TSr;i>RsbPPNh9)}Kr$HBwU06YvHgr>uT;0MvJ@PlwSG#Ty&cR-uK9pGkY0^AI)jaGtd!}p-2;d|h+=v{DGxF}ixE(#Yy^TLJTd}u*9A6yu{8!imTqh;WDxExv;E(hO>)`IVa>!3~HI&gEeJ=`4bh^D|D;Z*biI2G=X4ut!|gVCYzVE7;CSok0Ccytmx9)2910zVE<Lxb=%_-S-5{51R=x(I#_egRzyzW~38z68GruS7%eN_Y*r4PFDkiM|ED3GYOA!#m-<=ze%Fd=NbZAB2yfZ^K96chHaEci^+=C-7PLGxP%d8T>i=CHy&j3B3wmg1<p;!Qa5YpufVuz`vtToZ{c%Y;j8Sz}et@XbCtUTneoKmx3#zRp5$nHMAyN4X%aOhHEp|)?%K0#ZmL>y>NNvQ{m#wp~AVDH--Nugl`kVKM}%L2;naX;q!#>IYRhDLiji#943VK5yHC&;T?qVRzmn?LU=hLyo3;bo)CVP5Pp&neu5C5NC=N1gohBq0YW&P5bjC{ClkU=2;l@mxDp{;nh?H=5H3In=Ou&-62f;A!et2I%7kz&Lbxd*+@26lA%q_wga;DBLkZ!rgzzLncnTpLB!uS@!ixyurG)THgm8!u-bM(&MF{UEg!dD|hX~=f3E__j;ZF$R3xx2Ogz!~D_!c4jD<SOA_l5J&--S!i$Av4<uZ647mxXK6e}!wK_j&s9YDe|uTCnc>!g_oV)?<jU9%qF0SR|~+D`7pR3F~oBSdWdudi)gDW2~?qhlTZ6Ev(0LVLj#x>v=&~&mF>gei7Dlkg%Sog!Nn|tmivnJtqq5c~e-=t-^Z#71ndKu%5?-^;|Ek*8{?O%^<AT6~cP$A*|OY!g>uOtk*fhdMzZZ*Gq045yE=iC9KzG!g~ECtk-zLdL1aN*NVb=Jt?f$oWgotDy-M8!g_rxtk=N8dYvq+*V4jzy)CTQ<idL0F09w~!g~ELtoI1QdLJRI_Zq@_KO(I6EW&zUBdqs6!g_xstoKmDdY>h%_hQ0&zb35rbi#VyC#?5|!g~KGtoNA0dLJsR_o~7PsPtRmSyA2)jrD}^N%TGVBz&C^{w^Bdq9@Sz;1lphbOXE*o{i3eMIVJ{!y}_{KiV686z&c8B7`47XTgua&!Fq!XW-Wf;Zx{I_!N8ty$;`i?}}3)Tm=0NmJlu&cjp}mO9&T;YOXk?*Z3^{HA47Z^aT7ayb0Y1Z-VEbv*FpiuQ`P9D9<|`MF{sHgxe9qZPDIvTeuC{3vL6qjz%lAC)x|{MSb)ngdawqfggrvqOZd<;nxV^_t8`E`|$VZ4fuQb?l`4VXTpuphUi^zL%2R#1g;O)Lkq(7;JRo5xGr2H?oNHzAcXIUMj13GnhVYef9)uhHt{tfd<=aTJ_c__H^H0X`RE*Y4s}1D5FU;8fk(rA3E@s?JGc|vkPxnqwuS4%_0TqOJ-9B~8m<f1^t7j%gz$aQsDUP-t>7fM2ig<vN!#i{2#-K#!Xw}r=xgu{_*FvqH2OY#8vX(O9{vF?8mCm+Sy4~>D@q7Ajz)Vl8Eph7!|l+9a67myS|4r;w?^y1t>IQ^UAPsTgw}wQ;Fjn;a7(y}ryVyTgsVrR99jr10~dn-a+KzTC4?`d($+5%!bj0#@KJaRx*6UAFF@zR^J&uy2;s-jzVKskKSH=O+6nFqH$of2iD(tHAzTHnh}MTI!alSf?1L+yb>RwdDYPbB3NDG>2bY9PICuI?2|~DdG>W0s(Hd}dxFwndw}jKs9<b;LI1L_-&VYx*)6rMq>F_#2_zZd)J_FxGe}Heo@o`F}FU8ZR8pH8$Q%@gjN(gs|Mo+W{+8*u!r=iJk8r&Ui2X}{4(YA0ZoPxH7Q{b*>E4VA%1x<pxz@5>SaA&v;+5~O`w?M1IE#L;8zS@8gt{jchXkoM*To}%d7J{?Ge>h5|KmS1pN6^b~1pXI#6#f_d2D$})173(OfJGmJ7s3<Je((f%03qB3?F@H;{b(at_iaBR+&CHy(5h%6Too>lR)NdI`O%7SemD>6gY&?-(F$;GI2T$9&IRX0OTszf9B2tR2b>)(4rhn6Id{g0Y=m&MYTX~vB4{yKv^rb_u7<XRtHCYMG`I!a9UTsLhaW<x!w<p#MAyOpgx3<nAE0O858xlsoA8ftu{fnNb`&Foo1snNW^hNe1Kbhr<r!au2cZ4Yo^XHoL9_?_Ap8KD20s9&qut?jxF4Dd_k;VQDR5u7584&(1K*E!f$xWVqn+X2a5uCK+zsx8wtzdqezXDXhnu67;pT9nXKYF&geyg(ESeuJ4d;h*poQTa@So9oPVF3*Ek67I^uHds^AmI%zxRJcVE;?=+S~gt4@Ap~U4o}}&MEyh+NrX+1Jz`|eEKi+@{H~'

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
