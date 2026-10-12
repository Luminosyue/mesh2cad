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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/053b8a4984e340ad94f3b563594ff09d/part_001.stl', 'relative_path': '053b8a4984e340ad94f3b563594ff09d/part_001.stl', 'source_sha256': '1924e911b843ce3be0bd51dd39aa8c95e7ded9c6649d1295734f5bc6b01cadb1', 'input_faces': 392, 'input_vertices': 257, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0326073057949543, -0.5000002384185791, -0.20294542610645294], [0.12110589444637299, 0.20261412858963013, 0.205760195851326]]}
GEOMETRY_BASE85 = 'c$}qL2Y4367G2u2qM(4Npev|UdD2lJY+|7a1_(_Q|CmCMKp-HYyYLhQK_CGHA-G8(^aMy~LdeomL?uWl5)xLTs7P<3g1nhKXMT6b_`dhO_w(KFoIUr>o!Ob$+1UxfT`N?qritGZ+Rj&pr!B0hY25DBs%fJmVn+=Qix}Bt*zmFCv?`?YpTvajy}JeXFQ<*x#@7pv7#S8@?|HpmyT~^68te5UV`4|eh7Nl(CN?~R>o12!kBngY$f(fa5$w8tvzDzJ>&+W9)+g%!<L_?P1nY+lRyN0Xrsi<eP7Eb9t`x^}G;7^D$<gV#Fs(xwy1p)avs>5mi%Z<Pro>xa2U%`i#>@Otx1zI)-FfWG-gueE4tjkqwfB=L)NZ}eoqOn7(e0eje8NDX>$gv=_rxo@jMu6Z&L&;Ic!HxZW9BAm=lxz?&#almb+c{V_vn6n--z}cZ!O{#-B_8IOz|@&nsnVWV>iX6rv?#9eOm1tw{A`sx>>Fy-xEJEd=kYkZBG4WESQo>`gpIdw;GT_`Y540&&K9?;zxRQfBXymNcSb|rFPnr$1f&5Na$L|vpF6;&>OEu`##Bb>1NP{d{4aL&Et>n;Eng|#X%zoKWlN6{MUAEq&z3Qy4^f4mGmN^+v`^zBAhu+#2@$SdZoTANY8sYhVr~V^(&fh{rh}QdXCVIMqBee`fj0{Rpa-Q{`()h-MT+s>N9smy7OyE9YmfnXTs?E_)OBxjqm1>K3eF$*$XMZuR`How{EQ3neT}o<<<T1X9xH5<iC5Nh_5)Xm*+V>bv3Ol-EN<{*{vHPi%LAY=8ZQK=38#v`LJcNC;sLeo;?2ePPKZFUinkHUwifH9Jj93+n4Xr3qI>g@zE_0(*3?&NA#yQuO;POE9Sp1Wn>2F7ZW_XHhbD~()Fdy-Or1iI7-A<@#^NhsUqGtwV`{y>EBHj&ylX^1$d62`{$dC*A!jGYd_ba=f0>l-IvwofEcf+_1)?D37#R=nV-_cdQ~u}7sdCUc!cyCv10ux6uME}SLo4?dE<@Y!;-{v<c;_1NuA#D#LM<43*8?N-Awkz%lk4@yzzd0`7qM0d2f>Llk3t7ukK%$BAQH~a%VH?{+&MW(|j-k7m%(USWCK5KQ5Q9gS@)_&DMPs-~P_Y)Se!x;yJyvgW_#P*P`lEym2aV3i*GXK=)<Jc~$Dw<-D>tubATQ2Wz~TSLPP4Za*@E;*DeDKI~A&d^YbpGpnrmU~fD35!J7(C;D999JemlD-*i9j#+9v)+<Mihi>nCi*)~f;Hw|RbDiVW?d_e@-MVoyq{JPsOMT6n6K>s5^7xAOSZ>|;{yB;_f+|wHPsuOiEhWFITTPk?eb!K#=k}meb3Ego`U0LiuWsLwOY5pV@TTZDWnHyfOqxqrEm8Dmxd7^CqovS|cNUXwWLDop?f*yRcuyXz=a!<&_1wrkK)TuBKAJyH!z|Gc(0wP03*EY{#B1SqQ9n3Jywt7D6%r^uKE-oi4s`uW66sEtEb)HXB6Qh5#<|9#-&QwFaQB1rYZU1QbgP#o`e(pd%A>ap7J0BQvRgg5gs!EIeUa2nCEn8STAc0D<$g)V+e#i8ueI~W`|~9BNO1R?Iqg$gKcz1FP3pE1Z!~R6`#o)`H(u(-hCZY_&vc`CXq`AM)=xz@k}X>I^o>IIm14YZqCJYPhcyxTGlXs|ot)>+FLiCl8G4WSj;4q_O1!MsR^si?tCMbQ61sUuy!ei|G?w<&mZDp=e-qEsX53fi?e*?>Q_*F-J$sC3Po<Nz?imLj6wlEdq1(;R6;S-?4)h#p@!Lf|Jls$0hwJa9_0~{yr(Kp<pP}1X7~c*3sekkYuWlb+w2ba2ZMV<^MILMMKFV(^x)Z;H@;jq*JoCZX&{w?I;)L$>O`!QN_cKPEH{N_Zf$FszuAfKxsBaI7_V1?WNN*%`E#(6BgIO~{tPjx5gQ?>A?HQlr(eYdxVY|dWs$8@AVqSFon&NW<#B&PWDlMgY?O8SGJ*X`iynyo5=|b_={GW5&y4LHo7%x4FbZ5P>i1Nwx^ZIYpPBXn9J(vFX@`NSg{j2CsL5!%^y!|Pa!+T%$n;l(=)^Gjp+v2+w`%FjCZR~HQt`#pYamQ;zz3~?IrTS2BysA6tuM~UqK~<8<nztr&b>8~YvXjahUkkcAzE09<kw<yI=*dD?-!J+iExF9`g|3dTHGY6tx0L;Zqv~>>0R1oDM-voX#;1%X-7f!v*jLMa)H1KGV;^O$i4)(=_Xyp={@hk{3;T1Qlb&4G{FJ&nKlRu4B)gvr`MxuttM5DK(2-<!|I7E9Rw(qpyw|Q4k?vsM?o<q-b<d~hazAf1>M8cQ%6`CBbh#gp`d_{W8+&ybug}a7`)*}@@axL@;Jgt;>yYzBBl@n9`&ezDS9h?Fb+U!7#R%O$zP4BQk8e>Ykw;k%ZRoo4-RJxEndR<rm){Gfq8s>LFg|=#eBU<}=NtZbMVIl;`8uS_a|~k&&MPhmU7lA+UBBRsw}y!G3aQI;3>j}Id1Sny#QXKmaisgti?YP|k5B6Iya>7p-G5#L-R`(}g?qgG-*KH39p7d4{=O^8AByuUoNGCX?vv+QtrAIhMwA!NHO|d!Mfc&{%vtflD)J|8IOJ*1O0Vvd?FpGlx^c(GL+){OR2}1JXCEZp<WrLSajxh<w~k*gaqF7xjd$d^rJ@_XaBeB}%yY&6QAd8=_SP%&8%n&??TmA)slAtbiT$Mfe$VvkCce|{BNf+DKIL3gJL=WtIj13Y<y_QMbQy0=sI!jhiJM;NZjY_#{`PdQNat-f&Y7Jean5XppQiOd|6)XmyWdpZ*&asYYpHsZ!L%+Isb|H0ZAcsOorr!m6<vEp^ryM!`X=`{{+;fV?NN1k?)_8gXVm|t*TnhNs%<OE(q$f1w<c{D=a8MQ?x5%R@;I?SsrxL|XDGVyW<hdUx+&YaU&}75owlOuxL;MLJi(s7YW$p*JKcGJ`I+6NRnsCvU4PQxBL7J&`%fB!Tl`ml(rEr%v;X%`8Y!#|r<r}vY#_5YnI!{Lz+Z<i378E246}bSs{s55_-o7tz&`*!&ildF82AkMEoQ$m`yKcj_)TUv;J*PM=eOb0$_cy$ex1Q7X4in<g8#zoq$d0);p6-d_;}f0pmBbMj}Lqf%5Z*(*>{@oe+S<cwD%I)d<h!o7nzkpD@7U3FQd;d0!zVf!1pWgBKTE|&t>3g@N2lotHAHUZ^L&JcolpWv+>L}0`tH(f@c8p!CN!q)4CP#LGYW%c>{RaH9i;79~W`2axAZ)zptP#|8R}jZS?&$aIW7%%q^7XoX-_LXUYRBfb+SSj6O(4KXAU3nWc$&$MH3Ao~IEw$Nu2F%qiqc0{;|wIGzNa0&l|XSxr1290!84=4+LhRRrDvo`Jso2si<}75a7-a6I@&h-nS127WK%Dg&#5e}nOR12`VMGGctd3E*!a=3d}~;K$LvZ-9B=K9oHU%m;sq*(=OGfpNYB*ae(pC-5cUiNMa_iQtQYUBMTF4})<Y3VkQaam)qhzTSxCm<FDW_ALQV$2G63KJs#`1Kt%p6xbV_-%A6uontfbPT-w^^}&}hTghx1FdTducswu~JRUq1xEVYZd>L>h_yT4z%oYOYgRf?`75=U8Er5^5WCC}AuZBO<703A|W;U}$z<J<{z&{2K2j2wW8sNv^+_u5L4Y@d9&TJL46~HavLz#WRECD<M*B^i{2d)BNf!O814_x{dXj_nr^XAN+V%84W5WFX|FlIe~y})~bHwQii-VSAZ0>i+2z~9pqCu5#Q9LGpkJt4@;@d@xS#PkA&xaxlb`JO;7&iUNfp^5pyaV_{t@Ni%VcsO`8FcO@PPY%YG;~emL;KPA~z#~z2H24l&4@b;4U>5im@S(s#;4vsaA2<hmKKL$R4mh6!eKau-IIaWVg_y0t9pI}Fvjvz1z7;Vsz)0|+Xj=rZ4>*t6iN55R2F~lsg+CX*9jGT8{%rVi(1vvQ)8Ui-Q4jTTtP9TXy(#=n;gkKFg>lP5ZX5UUG|D}VGMs0kk5&V>f`5!LTLat%&es~gW~Bn-!Fju$MB6y_1@8mC4ww$k+uH!;8lX&Fw5u8X&ETttHrI#0K75?>IbR3<I`BP>G2mkn0-eY828Mu#Af`9Qfxi<H!LxDw7TWy^@JaAtD7zTA6Z{k0<6FSK+Mn-6UbYLc0r+%gA2MqJ>;^uA*-T~|fcwDLGuw-Ddr@XOeEZ<v2OsAxnRQ3L?#ML*b##Nj8+@DxGkcNQT;N#n+05dYy$TEhpNp71z$4(#p?n))5cp%v4EPQBIM<m4GJ71@0lY1<m*9U1J{>+D^E~hc@aMtX0$&1u96lY`7W^^PUmMs4d@!>y$UO$RIR6p%_%?7X_z-5}n4Jfn0FOd{{Qx`+evVlY>M24UgW)@jdJdzGAJJEVs4Ecly^Z|5TmY~GxNOsp!1Lg;?kM13@BoxGfPvsYqU;aAbKtLHOoM?hg6~0_cLNWD2OusA7zZARF&Y9K=eoDCXv0|KH!wB<7`FgukD(4;*KA-McpKDL8yEn79%FP4SOi|o>~m%lf$xHsFxwCRe)u?lnOSva9f38#JAzLFP6nR@UIN??J`r`j46N?rCayW&2VNb#2Jn7YJyVdE<1z3Wh?xwW;;R1`?uX-1@Xx{D1)AVrF)Lv9HSiGl!^|FKHWK&_IR9Upk1(qWd;mO_*(mr&!B-PG4<aweLhvdm_b{v~>ZyvHj{<9fk3by{0c(Ok1YQML6?`Px{1vbO{0nAZBHx$DH3BiC5jPrbEkMix#2vuB#iEZ6A>S9^Ujhrk3sL4v+(RwYQww!)evifvlr-&b80UAwIM;wYu03!nczf{onElM`CuV11oS%VlegSbjemn3i_;zp}`!8mnF?%2Q6Zre!yq@5$<;qv9@OS^^_s^fnKbk%N0az{RJyvs<Ji>DM57~mdR^sPST6y-557s6Ag|Gb^d82Et'

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
