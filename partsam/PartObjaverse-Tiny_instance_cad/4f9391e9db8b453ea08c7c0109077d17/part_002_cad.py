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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4f9391e9db8b453ea08c7c0109077d17/part_002.stl', 'relative_path': '4f9391e9db8b453ea08c7c0109077d17/part_002.stl', 'source_sha256': '55838fa90d396a304e0b75f923f6bfecc6707e1d4787cd952a02e9b9150be1bf', 'input_faces': 380, 'input_vertices': 249, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.11653336882591248, -0.37855032086372375, -0.293631374835968], [0.031335920095443726, -0.19324900209903717, -0.1459079086780548]]}
GEOMETRY_BASE85 = 'c$}@82~<_(7RL`F4y9(!qRDY271Wf1aJr^x4jI`i6-_PzCY4|yPUY*W<*blmq$plzRB%8@bK>BLGANT^CSFMsb0jr<TK3Mj_y68^KAvx_x88cJwb%c5|L*gh{q6Ieb3QKm4Rx;GNa3H>N}VxoZY50>MMNE?kuo(TVoGRGNMx6=$updk`s9lryRI1i{@Z?|os_A{=kCEFkwFpezN&k#2|n%~s{4fSh$#_)VFBS0!6CvQ82D*qi0(&D44fRIe}1{U*Xtf?kB%PdEcJi<c}_3E(z@tyx~^(x-x8sg9e(H14ZgWaYw~TeyYq#b7N;Db&u!z+lZM_nD^zpeO}^^xO1^r#H|1;Q9pqbbVhbsMsLNTSubpd1zNs`TPpFdc_y_vD`dSg?cO66HSR?O~uWt6He5Lmvl&}4DC5`g@>txgC>Z92AxkSEcg7<0CYTbDJ(=nWXvpLPnbY^G1<afJLO#a0)<eU3mOeGCCLi4iTdqnlyE|!pQ9p9UL%kDSxjlOcJ8v7Z6>^CYT-!e9m>Q_%Z%r*LIYzy+u1AeDEO?&dl*8+Ykpgh;(<Xe8UrI6pVgzB``Kh5>eSU|pYL~rVY>NJM()s(s9o2@me4_bmJ_h<NQ^40N&GU@m*C+^P~x1Hn<UPa^Be3NNCD5IYyQ(YMf<yn24xy~A^Wq*Bv<U7X6o6X}7nwUiAkISWTZG-OfybfL3LF(TlhsFs_=5dyJZ6|%$nCiEBcaeOnYYx|6vl@?|>$#1__1Z`MH;;LE*65pjUgLFptv|2N8Xei6^(U=2r7{5hbR*w9cNSk4|9|8febd5rybh;U<{5qKyg%rAS+1SnItxBXr1R~zao@`a@O<y}A>VrOIUc{87yA_r6ZtqB)uVP<#Qvblty2Egdy;P-U-3y|-}2j5o_{&56Xj|I`<}}r-?C{&zR|azS8L|V{TZh6c|HC?$D7~8eLAlN`Iex&G+*n=n%uX?2e;7YoTq$0x*VtLY5FvUd@Z>HT}N|h*F2+do_HlwT34?Il5dN0mhLZ0*jVx{ZI4p@+K^T3@5|pv{fbJWd{gW_zU~z{<Xfh9=JhbAU%t^-7d)W(nmxwxIOC6#Z=14^``r3zuF+R^cOl<$f%~DXN#}8<*W%~fl}z?)x3toH-fJK|my|b}lCOI9lAlXggA(X`Ez2q2ydi`7ri}C_Up*Ae_w{LBCrYLt`N|7l@_o@{Jm>cuM80k36Y8hs<LaCr)s+3?fAW1dtu6amkJnOO|3lpOQ4QJe8!!3hI_D(cF;2i@_UlHjA#GiQ^CxX*-x5l`B`t;5f4g7MhoD%}%UAilhiqr)bLwdFO+9b(^JLoFe1Cs8kn_jme%m$e6zLZ|$X8pr@O$Fxl<a5uYUz#><j<bJg6fMNOxH^*oWswz;3?$We(>Y>(X5|&oZ^q!ALP&Z`<7&p|5hN6lX*jWPbmjSl5fhN!1-Gr<vq(+!?y9fJchGh&{KM^Ddh)ZXxtaPxSq7yInVO7y3Qxb&)!PD+M^$@&(d7(PoD(#@m_Y+Q^j}Gvpbf2WyCt^{qFGnhjKkzH*tQO#pGL?bvQ5e2fpe3R?>dJ?wenFkL$nb&H1sjd7Ld>&rAKUF`dtw$IorY^@4AST_x=+l<8sQYjMrweZ{aN(RAJqhI5}oE=s<&mM_=i;wk&xn)CR0PuYEK#UuH?fUh)@pTkvs`}1GPyt$CZ-+PYVI~{6qACgMQ*Ag#~Z|QuUukVx;^36`XFH*gtc|G@9LcZzlea`>$LC&*$Q_JL|<Xa!lq4O3vmq__ld`JGU4D!tx4N9c*Hi{=-acxy1)%j>X`KGBIN~C%Dq|c)9m-7BVdGJG?(N}}A>9ftVj^vv+X0RWgFZregF8ti^+9mmlN0sMN6<@30j{U@<C^{bd7R!xzURRmD$XBx~>9gv*i03uAe6lfLah}ilG4GIX_FKXGoPjggS5}13@$pXlJa1dUeY>~G+}Dt=YN4DzJvmJH_V>H>ts!|v-~JrdieF}5I}u^bH>G;z7=5K3uRrbG!}NYo{<taS+cJFfjJ|fTnEQOAIr|<TPoX-oPcU^2z;h`+O8BN<O6Bzo|KIv-9y!A}j<#zs`@4J1q<q{L=7N*iMqg`R!sGarbNx!2&yC|K9@BU~*6z_PV?Fl$gWY%3V=m)9Cpmvf<A;|@`zvMBnK?ARFYkXWu9tF*zCGXE{4>tCPMvGKj*j<xw)N}2hV`RuNMwKe>+|{=)`K<wLta;j*T}aGyvy@n7R~t`1}`*@Z{E;}{n(Z4Z#l~Ish@-TlNOWz?nKUSf0W1Xw0{Ymx3oJy_YU01Gy2xQPV;rQ?^_0DEs?J8xg^Q|xBIKwwq-Pa<2$^bBj07etY0+E>v1KnZ=vMd?_cxyz3h)zM!sd#Bi=uM<eYExwISd0eHvZH`LmQ5W1meE{n=0XBF4C`tXmrA7=6dQ9xayhF)yq7iR9bYq1w)y_a`~m$hT<Q<b8|(UCy7oN8YzYRr|(x|2p<9%Nu`V?7w5*QpI=dTb5>!Z<}0C-nX>OBHtX}Sl+jIm$Ki{P2RWst%7`QZ)bUbQpI=d2cFhlPW9L2^=7VV;rt~{mmAlW7Pm+8?e%NvG3+;Qz1(=c9P5A4B=YV1I$LerFYxW_M0;gE`^~0F`R0UyIYwW-ahdPC78CipcrICCTvzHee$Uu_+nzM;^ST}E7blW$e@{8CZ*U6vCbu8u>wEto`;C5<uW!Ax<SUcz@Vs7`k^L-R>3)r`Z_!isTYk^iwN)nfXTZ={x-NMBSoiSnWy<rPv!CcCuZLA%k#AY=E3bzR%g8rZa337|$tu2MKbaawzAg9-dHwWXPrkL*<sxbQRPi0_2fns=81GAy&g4DI*MeP6OXD=EA@5_yrIN2c{<TP|2fn3eeR*Gc`!Lu4w5hz$oOz1J!S8*J{?y9j^QJs0lKQ!P-b(WA?`8Y*1ira<9Iqey^WjvrZ^>`q#QSI85q!NSWs$FG+5CJ9JeU0}-x}D9`~OEF`4&rYfz*eErR3YbyG_11WN41jw=`MG_e<HQTu;+-uBR}qNa}wT-_d{g+E14Yq<(IxAm8*PUG6`8bJ#BhQlB%b$5A~;PRV^9UXOg!z8tyF^S#Kozkkh7hVc8nai2Kj`d7<u<Np1V^X=bbyz>e7dClPO==!c)DetTIk0sx<C_&y=7lxB>E88aTt1IS^ubta3@2ji$j(u{})m6spuBeT;p6YkVx6DxZdkj+y&ue)l`L<CS)o*JX&H1l3iKlTo9+&Gs=0?8tR+e0UX?ON#7RmKLd6Rs_rHsd^xhm&bzSf}jG4hXOk*}s@7EAN3;ydOWT28)gLvgWm-rp<8w>&8;mg;QivWEIL@@BC#ul(268n2_$_$BVcw7=Lt99JyWU&VLSAKM^-#vimvu4h+!_KT9`dU|&y-~3UkTu+uyg0UXQI(%=yI_jI2&V6X{2G`mDc`NnDoqhF_xZHF<>8}D`r}f?C*FaH3)K(fP69Nr?5)h{NvFo${BoONLU;Rm-hflZv!=D5cCq15nJ`Wb!0Q`v_pXzZ-kIQ=eB9<XS@C}6E3WVT?2*KB(m%&19;OpRW#IJh%hWHid4MiPg&|BbJ$SH%CgUc~y8N!A!Lct$FFM~e<Pk@$!CxAorm<YWBEd`fi{#T$C;E!?4P3RTy73AE6J_Lv1n7h!M;G4*~ixB((dL4WnbAEsjd>{H7_&)eH^cMIQuJ3K=B=BwU9cUOh40YUrJ^(+!IRtmt;}t!wL36=EE5Vnb_n?*Fd*DZUT!sD&tprzMEWtlP4?%Omxj6SBgy7E5?%)p4jtIe>pxwdUQC}xR-JOsxbT;%7csBSe=soaP;Q0u_ze68^?Q{MeIYJjB1Yd++1z*LSFB*Dr5&1%wKz{-+0WX3c0xtr0fZBWWfgU~d7_CQJJ?iW6B0_LYgy0$o!SxV=+d$ibh5CTofV~lZdc2MB!+AeM9pj**!K0Bg4(bi|#+c&}J{aRe@N3Yv;Mc&dp)Z14gJ002I@AUFBKSqj-vwF&Tn)!KLtVfw$Z>|&1J}VZb)n8+XXMmH2v(tOz-=&R6(RUl=-c2|!CuhO;L*6gUeH!xFR&Z54!92LaD%E~73UEAz8<6WIHpIU9*6bViV%DpA-E7B_(z1`BhW;!&~4x&;0(kGJ&F(~aNc)N#}4Q*@G<1<fM$R*Fy;=#HjMEOco;MhJPbS(x)nSWJVcM-(CyHz;H{Ydc4#5^Z#d>CbUS!Ea*jfO1dqirS<s{4qsYlZ2)+P40zQH{UqA>hh8BT~!Ka|dz{hZXPeI3kPl3-s$AZVAjx*2;;0rj1;1PPfr-!D;Mm@gQV*^6)4+z0$5rRt)g7-l;f`x7Z?*s2g9MIz&;sDM&7<FucYG4gHTcG>F`!VJg#3qa}7(58N5j+Sy5V`?85d5YdZ$URhH-I-_{+pp^!SCXjbm(UAX5^$pOThj(<}@@NoQ|B+2*Kx}`@s7!=ko}`dC+s<Jn%`V2G($WPeMn6Pl7X{{$PL9kqJEyK96$<PSqn`k5zhj>fxbBAap!<JpMfp8V?Qx2OtE;A_ONxQ^CpLd_7X2yP>JzRGdTbI_S61Rp3>q>05;0AgBj82>deC6Wk8k9wFEr>IwG5+}xo7;Py~6GyoicIhzrJKSv1u5}FMD5<CkbI2)P|w)ZF-IYPfi2u^^efK$+;1Vir<kS}xrbRBpBcn<Vi@EmY3Gzc7o9t9)py-d?%jUKD@7@$XgJwAg*fFtnlpF!7vKLdv&1g}I0-U&?u?*td<u@|}rng&k8IRsmwanRM^)u<^BAvhA+9~=pO13CcQ7ivNX?gt$J9)P*^gNB1m(8<tna5&~X86o%!gkTGFC)fi1J3?>{v;b`HQ4Vs1&O-=Z58Vsiiyo~v^lm-!g)W3z!3)82p>g23;3?2Za3p#(1!3={s~#=%SPqQ=3rzwqgRX@pf!Bf$>aha)9W)7?gs}vF16>M@0mtCnOA&&bLtVj5piL2in?YT{uBfk>q3&kL7a9d!295$xgRTWn15ZT=-UU4fw$FJNa)i!62#$uX0I$HDqYb@?M!wLQ&~Lyq!PB8j!PCJ_p!VMM)T4_Yz4UlV5Ajt_V}#(^2*I@wf*T?Pw}id~7TOKm65JKxtH<jIU!1o$>gWUQ1@48MKG3e<t{Afqq8rBW8|qZ8k@J80FRK6gv4}5wr2nv5^+@?^EaQ<)^o8K~Qp<0si}*c8|D~lGJuudb--MNa0vl7k*8'

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
