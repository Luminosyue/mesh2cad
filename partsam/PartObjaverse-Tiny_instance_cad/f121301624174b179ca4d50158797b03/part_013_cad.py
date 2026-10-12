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

PART_NAME = 'part_013'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f121301624174b179ca4d50158797b03/part_013.stl', 'relative_path': 'f121301624174b179ca4d50158797b03/part_013.stl', 'source_sha256': 'd9fcb804b5ac9f293a8de22510800d5e4a1831afc8742d76110c2f242a14f608', 'input_faces': 491, 'input_vertices': 303, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09132278710603714, -0.23652759194374084, -0.02772381901741028], [0.014235183596611023, -0.049920231103897095, 0.15814250707626343]]}
GEOMETRY_BASE85 = 'c$}r12UJwoyTvbJ0Tq!VAQ~MjcCn*DnAj66XcRPx4kGpniW)*3jlD)Js3?xcii*7=G9dqGESSU=HDwYLqfujvvFn@r?LEWXS?{g&)_bh=t^H$r=FGY0e5YNOkrA%NeHHvvQ@#!@yY6;nMNy-y;;SUZCrlg>7oXT@?D(lJN_p|sADb@g-ltn+KNlrQNe&tkpBR@A)J7K+Iy5Axfi7t1xP*xbv112~OBfQb`ki7&C&pX-#Nn~y<E_8fX%^h9fv#EI2D%j8|M91^wF$bv4Tp2BYHnsZqpGpbo^)09^=gT4EF5xHbjBCrD=FUM>n6uYd8O<t@pV^^9FltGj{ZhfLt48-;p*oG?iJtU)=+$7@{J?nkJ%``QuXR-`97b#W2$fdY?=7Fv_bHX1sqp>(}J1e8?Ts8N&U^L<b=!TQsCEkB=zea55xEVJOTCmxl4Tg#Og;?Ul}@5eEs%s<hjhIcsv(<L*`xiUW>7!)ML0mSbWQt?r48{NVa@$lR>D*ElbLqW-OQIGQ9p6{-jv(l?xr^x%B!-^v{F>)L-J9JeT=Y7u4^op#LwlT$}6Qo2R^$=e6vOmG9N{_yFzP<&OGSzLb7YmbFDa?<Pxmqi>khuRrp`L21vj=Q3^<j|wLpeRHu0eC|P0jc-g?cR>FAZ4HgD^nbQb{ypE4ukm*c+bi|l9HjNT{JvXs>$*IRpBTCe?MgLEKXlI*U#IIW{b0E`OZs04JS@Jcgs1pA*N<f!&7(JoZ|S-X<34L~wxh4>vRL}ZnDOeM^jpYk^ux?v=(kn|<YDeo^h0e=smGGvJ;%{k(u0r4=kBdI>F665n591rJyY{Feyb?t<NU*#^7_JX<a?hiO?k6Rq4cx9-3DzvK_kRBW^d7cZ|zb0rTl<l+VT-|WLyj%_0^U?=_$Ux{);?~-}B@i(Wwzye?_kN=1)&+>Q@4NWE>5TdYd)=#5P${|D^|-dX#hVJEXoA-%5GC>tc-K2oL1{=-U{_!WrnF&}`&+$PLUF?`h22_87<J=_gd*vU)Pwnc7jxn~$!RaW@9XqCbCqsF~O185fYpd;7^anj1Wo{;~N=lXT3B^3C!cef^#otRHg%3mkoOpAgK;mfbYvl>txi?=J1M{`vOsua(l&qx8;^aWpRX)RZ@tT7dCN%F5G}AKV1~!@ZjJ8z&Etd1pN6sV%=kk8y15qb+Y}fpM==$E+z|$4%y=VO4!?`)ifU6yNO)#<Aj2JWt<bnU5y7r7}-VzwZ)X7uFK%*gvr{zQ!jR@VB0q`DM=BCgWx3v=H^&YJ_!lMY7C0-Ri00n_l<By88SI#{Fe9%D?+wyB}3-gYml8NqkF-Ay_x)n?|`yd-QvI%erdVT?6G4&ElH}x59pLz6AQ`$vZsPy}HtVz3z#OlZnr3-@n|?VEi@?m%LKW`V~0(w)`==hG~3dRS5cZN?omQ^uhey^W8~}pYJ2%Wop(~>j$jbDL(Vf?$=tfUFx~&A^D&z%}0BBnbAL7SIswfi*F7{m*+Ap?3}IfSM}Gf!@D=Z-&YO&bD`jvqpuqf0Dpc2_Sq9F&_C1nV|*jOK>aSMs3#*$#@F!MGg+UF9T%f~@?^~4Rs)Y}{B@JW*LTUqxSyYmdan0Jo}B25ap^q`?HN8=v!B|0eM$h<`42lwz8O{}!#De3o%zRt?~NOe?``-Y&LLCMPB{9O)B>DC%on8}ba#itFWn9M@0%6auV3~<{@g5&elEQT?YtC@@%r_#<{V}7ZTp&~sSf9a{vl{jkO#^?yDq-rW-!`c(gXd|bOYAI96$JnPDnkbs4!`#vC%E;-#l;F=8HbzH{{>Ra_6L93zlPEzqr0nQ%|@*`lszxluv(o8s#e>uiVawuOtn^zMNS%+tJs*IF9|d`#k9f{g(ys7rG-)c&<|}nZ-BV=qJ9i59c47Z|IPKdVX$s%+XiI#%R`go3Fp0p;_nczSBBy^PSgud;L!9yxn(N=k31JI&brx*Liz+r*+<5-f5k;mv>s{?d6@;d3$-Mb>8kft@CF89Q4EBi^%`)%#v@)&AsqDdy211iNg5S&O$vk$75aHACu$g8{S0Y9Nz0K&Q~Kd(av%OlDCFG#vgU`?ep=yCphP4Z9zVG&yxA2tZj+&ZBCl_mgp4ZN!9nUp3hwf|6n-gQKxSu-^?FRNB!sSp#4L$aPJtLpvf!CX?M)K32|uWo%8a&rnlbMr`q;~Kl3~EPv16Zk6Sm?pB;^LEIJ$a1^+PgTVSZ>+^(Nm8SPw?jCE}D9a(40#{=No)`5o^;_K4hA`g5*H0M&AuM|J6IhWeYJDp2yzVo@%<~yHD?e#dFOYOeXxzz4EolEV$)49~{JDp4IzSFtX{=81-QoHYTF17nk=Tf8bGVU$4yfBWl%V7O+D->V%yrQg!#;%KyS4+M|d%_N4J)b=v`J8bWei`M6<9xLF&i5>Pd8d1p&3C?M*?p&bmfd%{XW4zHdzR8-13v#z!&8p=W}31N`B3dU%*Wg)nUALH$?&h9z<g=3I@i%R2M@!!y`e>Xqn{q-cMe58AEahG`o=<coZGMci+<i!7w!4`59IlQ>)2<fU6t|Hdt0O))5vj$9DVcmoAAABBJf<F<cP0qJBxebv|bpOhg)!ddbURDQI1r>`DDs^@hxLq&&&5DrsBSkoesZXf%rz=BMjx{!B?JQznk!*Jg;)HxA?kOt?;}<8{&EUg`s@0@$mURME5WV?VNuH>m>J0OS78Dd+y67-glID0VscKf#jjmx)AMbR{_s8)}>H>-yMbbHfKCg&!$E=?{VETwD}kLaeD{qzdT)h-LP-Ox5QqS{?xS|gL8h;F->^`*MC#J+2Wgjyn^$?{VlS78uG@$Pr`d4U6Y!}P`(s=-mi_1)*?@ao|XBjTl*aEi+KJtO*)?CSdTHXn0&7#Fim{Ju=_ZN*!G1kBT>HOLX0ohfBl8Q@MC<X-)!%NEK&VY&)H6x*Y^YDe5efViuGb%C+Sb)(uvZarp|X|{us{<M}Gd&RN7;lctU)0+rzlma9>bfAA&#U0nUffJ+Pk^4iVq-$QAq4;QKPZ`luMp&-Vjxe(PEe?T_z{@2xvmv;OFRx+3R(C1o|v&+R<1&zhEruY2<Y=BaI;U0MVFjt=r%%8(7bH&ur3c^l`|!FMq(0qbOav=q)o`^yzWJ9p2<x~aQ}yxnzA&h6%o<Ha|}pG7}UUxj%Z*GqiUfqc}z@;Uak>CMI0=P$**tW!_y%Whe6{!n_hM}G1gZn)83d`qeM$p4LTIM4spRea-@?=VjT@8P+!+)<wEiEivI?C*EFZ+C2`tv?MDI>TS$BK4Rzu>R-a@Ndl%U*SDMpAm@rRrz@2Vftb0@8i#GmG2$14f}}4ESw*j%@JRT@k4%&e29K)H)X44e6vPjd`q_2>Nvj)ecEB3ex9>M>MyYv^XuosxSxKLu*EU|jc(pJhewWrKh0a}*WU<(pRN<%c2C!3W@7%<s3^YvOc&H+N;;zPBX(jOH;tCOvfR47S?Uk-#Q7mR2=5uHuMuDA_Y!$>%0ue6G+7|N@lrD02b>AOd&NNmQ9if|>S>+@|5g<I+V^m7`tTagt0{W%bw3=(eB3xb+tD{ZjKjWEVj#*dY@%tWLHCvTmLtVc-lYfj-y!R;|MvKMll*>TKi(hQO~ZNP>Mik&1JbZAO{#)(@0f4JSNuOiJ9qbzdJIob!+$&o_qn`S?AHtSp&p)pEM1@FX?&h@OeYG^&h8JtlHYCbKYw_c?dY3ZD9A&;@3r}gcPP$#<$UBmVhUaYpYI<Gv5NS*e<I-X-eK#1vsWYWjXgV{Jw3f}ek&HfQOfxg$3D2D7S^9j_cloR(Xr^~TA{cHh0PRS=^d(l@8R+R{O5t1_a5dgl~7NcN}Bf`x{C+aOCENghWguA!TYq$H#4OC;~3PxvJ9TLL5%o{X9v{3^C0ROQ4Ri?2<*?c_u;c$;RpC*-A!tUaeuoA>%ps~c(0$Ek9I~kU+dT&<Br1^-@LQfpWCJ)&%O6ZdCTi1*q;NQA>USIqI{Q*>5laqYlfY4^p%6_kXQMG#5YB^MEQ#;cz<wtEb?Sh0Lq8@<9Yvlo#*HqJx<|y`<_AhneOm;-Zn*d%X9RV_z$s9?t6syim#Whk@6kS9B>>LV|-osMla-fo7<>A_4R7;e@(zS)D(yLxbeRDO5R;L7wBfK$9=ZXyD?I}*tvt6^4Hyaihpx7?jwt$;Q#xoujq>aya$TY!T0SpM%p`M8~SrtDE!=w<3yE9IB#Yi#rOL8C8AyPr9GzpBj87WpClUc4EuA9Jot6qOqS<<whrg4)0N>T?wKNaw0jWVbN6nH@6C^!8t#x+rX@)@ug*?O5&f$(_S>^Z;di?TKjbOSFWW<LPZ?Qly7(s^$-Zq&@Iw8;G4KxsVqUwy!g_Klcc%EeO3Hp{dintM$JU-LI`tav(`8qo`~<Igc#a&Y-~3B^<Y&jw`Qjf~kNZ&97pP~V`y%vThU|y-_YzS-;v3ga!MSxp1#@_$=C7p3;(pmN(_c~4a94blp|K8sB2`WG$EN@NpGZeE|6l!yw0Y|$|KC56KDM^uwK`1HXXL-ge^UP@|4F_@y-U7D{+)W8{5$zahRPP|9kPY|EA<cZujHSozmR_-U!wj%zC=Dt{f>N=oJ0MFoI^fDJxxADK1ltRe2{#cdX;>fe1^|>hR=P5zO5gwvY%AF?$B@7*{`bJaOme790yf@b{H3xA5(uLKPJDS-Xy;v7juE$Bdeiu6>23Huo^1YpjIZ=AlIS3N3KJzN3BY(M{Yo^PHsSM#8A05RY$H(u1T#%u1T&%4I<Yf*QM4ctJ;v<#QKb#tkIm>joh5vlA&^UYfPdhQoE58$+6T<<XG|`hRPkOO~@U|I%{}Ry{S#e-sEc3=HzPR8q}8L8sypxm0MH0lUtK}I6PYqhRRc{kw#rkokU(vPNgQ2Q^~WbvE<q0>C{2w>Ey8tmHSaUlKYW6P<7-E<o6u<?mdReWvx+yT9WEXE=ev$^(L1h`%<fseaRK5HOLjne$?7zKe9hV<vP^X<T~U~Y7cTKIg&bs97#@g7@K5<%B!uh)f#K9v4y&tyoJ1(nnvDC-b7ta-bDV2no9nPypTGZypX(rI-R_LJfAw2JfA#|q4H>IKk{gDUup+(Uvhiud*t@y%G9#t%4Bz?C@0(*Di^ng2ellv1i2j9i&~QGMfRbVBKwf5Q+>(R$u+4J$Ti8esD9*H<RGd)Ifz`Bp>hDV4mp5apBhT8PY$C-lEcV7smbJ?<P_>^vZ`yzDdcGkl{2VY$r<Er)<~zWp>8FwA+MrtA+I8@q;4j!B(I=uBCjAXqkctRMxH}mNS;HUL0v$eK~A8~Cnu1{QRk7zk;gDpo=Y7~o=YA{?Mog>j-s|FN0Hl6E0f!iD^cCamB?<?;$%0nt5THft_+pSSfdKHD%FErmE4$Gj@+0WO!XoMlbcd~$W6&DsMX0W$gQX~$*ssC)LP^aavN$8xefV!YF+aC<hBfz>rn&9^~e>e^~n{<4XI(|hGadpCs|MKMNJ{AI*r_m{4qmiBQ=9;B(JA#Bd;fKSBmD+c81F9tnoSZGio~dGxDd@HRMmpQ>m-SQ^}L5E6J0|Nz@hOB=SV+GV(-n9CZ#kjy#w;gFKjQpeB$F<QVEWat!$s>KO7T<PRAt52Vf|4<yG^N0Q^o1E^8t0p!lqcI3|FX4FdLX5`XTH*#sR3)PkELRP3{l%gM%iz!8OwHQO?@_fefeD3n}ZT(P%{iJGDhkmQdepR)xLq9j>IH(%zFfPFyH&vS|MdPUQL~0AAXxvp!qP9|s@<ipy)DWd8uT-8&ZKD+Bp~|09-&czAR^`vAZIz-tSNU^>%Hh;{<ZyBWYDIDbav-%KIgs3lswX!he?aX;R`p}@Qfut7#!l*C@=o$Ts+qix{Fb4zt2Hr7xj+l~yXqG*R4$+%CKr&ise8!T<oyhlH&U09H<G`w#xUwk>QeGd@|V<|<S)s)sQbvf$PcM+$q&g-87jY{s?Yh3zpGr_rKm58GgNl7MmcI(YAJGA@?{08_Sa>G$`_~w<O}3e)NJx8avpU*IgfmVp>h^=BRPw_nEC~IF?qN{Uk_)f+{YTx)S=X2<e}v8)S2Y*<R#QE$xFzY)LrCE@_p(<@_q6H>QnLq@*{@I&#CXo&&dkMuefb-<CvA8x{*te-5ti#ouRUqH7Z)e*BSv-FLD6cpIVOWPcBa_OD<2ora;v^xW-WVBJ~3KBKbV^6!|>)Yib_(YjQsI2sxj8f}!#OY8Lqbc?Wedc?WqGbvStzxj(fJxj#9=A%`LuDtEQU5b6kOG<gJh0(B^P0(lX2Jb4k>L|sBQk#|!w$-Bw_Q16rfA^%H#K>nBfg8GR3g8Y)9@)PQF@)Pnas+xbV_`Aw3%*hgD7jj9eJGmseG}Vjj#at}SP`M04Wj|^~vL89n8WpHM)QV&uvNtt=>`nHh`jb7$9@O$=5AqcSs^<3<hRWYlFOt6}pQD~9pCkW=`Zf7K<df8V@=0<o^#nPWe2k&;QR)HmQSx5u4)R{|2I?&G2J$FsfAT1DZ)ya&H@OS7E4d5#Bc*6=s2myLQq0%&fBJ7uML$M0k2L@3$@!DoSO1Qmto@!+^oM}Rh!X0%1na@Bm`u1o)Hiy{e*x)WY54'

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
