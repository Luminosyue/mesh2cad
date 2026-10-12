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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/062c791e78a643f7bd380c336f809389/part_006.stl', 'relative_path': '062c791e78a643f7bd380c336f809389/part_006.stl', 'source_sha256': '3f890415930deb2eb010cc14fef0a0c591f8308b73dfe41673b0f876b496f52c', 'input_faces': 608, 'input_vertices': 344, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.34715840220451355, -0.2033805400133133, -0.3421453833580017], [0.44231364130973816, 0.20609711110591888, -0.2303871363401413]]}
GEOMETRY_BASE85 = 'c$}r13Al|_+sB_RGS3dlv?Y!?nKB&CCK)>BF?z8L$Iu`l%1}F%G8Cbds7;bgsZeRKk+F_5y^`o_qk5GTy}j|i8oqt6^;^$*p5=V5@A^L1bzlGA^SAcB*R$5W)_w+hr(IL9f}{V`bdK&X|57aII1(kC3eME@NmIs;N}t?#!o-IHP8sFPAEQfp4(QQ)aKM@B%t#)cK6%un<Tk<NlrgQ68wQid+&5{;q!AN_-#2M=y7-+(+%q{n;ZGhnVq$vYxNfuN%^L=r)oU1>75qQ`DVFF${OB#8rzSMg?(pKB360jAaYWR4x3luYbqB2Q`l0@lmG4aZaP`&vVDX^x<3pGG^2fG)tNh@I*LD7^nlI(&N0N&^;qzO3pz}94zt;P`wr{@I`7A^E!3xi;^5!vq<m*18y?*GC^U4p+sj*jmZgj;QuOFL#Ncpj^-cWvI_8&S=hc=(6^LXnHpYL?}R{8PzKl=RGp@RFAU-9qRzC2lPDnGJltZE-!ROo1a<7WHePOs_yJ0+FxoNxP@@4WCM%kG_=>K%vo$|yg)BkRSTSMg1L<45{!crw5C#y9Qbv#RPmmshX%&X?_*`HGyYrTo|%L-(kB-!9AX`k^<AsPT;b(ID5?e&k6tZceAA*}nGU7VKAl|537@$Avd5KX|5d)Hgns?~W&aq}RwP`L#E`X&?S(g!1G2r>*n0H-2Q$;yJ$Ye{7`kqjxXft-gOxPL9`i?r*2YA(k>G*XOU=sLm@qW^lIG53e0`K;?V*obqFB#_0AX!>@Y#WBaE6#*YqvsZVM??TzoAZ|lW+oV%~v<XexkHtF*%S#hmz{aU`sWBl+V?Wd>a)86=|edNG)-JfPBcPanoYjeGR{PH|Cp3a6B{eIGLH9o;hwX=PBsuVk@@|4-3$1Qe1fA9CzH~7X4KYH)7MZSLSKc&ZW#SS%J;U*`uRQvSPdVH+?#F=td`!^)3_Q8I|v%P*Ssi)pICT!30`Q4t@{+y66PwcO^^}e+FtjZH?SMUp!_xOuy9HOn7`~1+}KXpIv8K2|zouS9|J~sF1EMNOBA+^3jAMMuTb6orJ8ohmWZu@Rs;Ya2d_SL`byYt(#vhrhHe|*zhSMfE~lpns>Q_Xv@f0JCVAKiIL`LT>WK0n;|f|~d6k;_?LKR#%Mn)m3rg?juSZ>Y!ZgGy@L;suBJeCM^9dOfyUnB(<BJBI1`{b+2K*N?2(qxbpqD^#A)%=WrJ&z0Zg9XI1g_C}U^$0vHvNZp_5Yt(tgr_adt`p(B$dfvb7tiCr~e3Z_!s+j6$y!4hFuOC|1LhT!o$}?4-urp5gXX1a}@b<^{-Suw#iz^nS=GPwIUDpp!(|-JWJzqyx9QOM5dI?URsoS@ltJ*uqjvV&-@%?FPULxhveZKR{V3j9Y?hjv{&|_6qJv%-3YQOQ*I?uHYbpBe!GrfLr$2yfiG{5m-uOHfdS^ER8%l7)Q2OiSvrPz8s{^2FM4$qv7seC{6%Jus3E%Ws}jy>)3gCmBiI*cDX;mZ@QSLBe&*KeY(!yRjM{wKTWJT;#8`LX*q>h<35(;TlKIoDX#VQ_VWEMNPhOH@6?kA(Gk<-V@_^Y{_f|M0eyOs^kJU90kkYuxN>?@a$oua`@|XL$Wsi!3!h!4A*rbvJK=9*62{w|LieIQFp~=Tm8$eRYT*8Ghk;-@4fIsUDxRb9FzH#$|f__}U@5pP8Mry?(4*nqC(#WM_E&$l)q_{XRQG@7vkAI#2z8fB(09cYni=UbxfuyI}jKeYEd+J<i`aY96DD*JpeEXz{VC|FPt+bG*LOe~R8uGAd<x{ZRX3`Z_1jL+7b=QIF5BX=;4pg%)Ib{ot0Wx=!}r;cFi&I#*wJt=p90^+S6H@73crUVU$9Y`J6V^S{5W@<(fp%Jure0=KL43a$Lj=f}IR(!aB74*K#0lhRb32dfWN{fTd@tJ_zuuJT8^y`Jgyqep(y^?xYc*FN;kcGZ7p^^y#)AA99VJ--+4)Z<pIqw>SMK3Dle7q@5o{0(jOdS7rh$Ll*=Us2;99$(y-Cmy~=UstRQ>HZA4Rr^Wb`0CvD-TNc_*yVS8^>6&}!~q+w=DXM1`1XB)@uOo)J)4?O9^+q;XUVQ*zIFHVFx~$b0=ll!-_7*;(f&EQo~KR7_WGgpT)oeCot@$JW5G4LuFmw+`$J%v&NIBoA=Up0eSCiW)msiIzu&A3uOA!w^G-ECcYc`Z^@E$AQvGxWj?eY^r}pc*?eRgj*AGu^s_S;bAHMd{yAJ5zuU{tm+ke(juhUaM=Xiam+zEZYRzD*d8`b&R=Vjkl8b7pTv%aq>U)VnmspV9?#X6_>`V)QWUA4X<xx4-CM~%?ytH(fn{Wkj@?c4jC<-7YE{uTS1<-5Q8OAqM&Tl=~3?fpEw@38hC`19aSPdykv{(d7p@6?a$TXkrByAF+S*P-$4I*cAXuJc>JQ?~CuXZY@HzWa&mTl<Oe?ft~~_I?uUQRqu`KEIw+<74(Q<HuW-RpVp!J=eGPPdAUXe;VK3KaFqipWzi%bRKK}H@?098{gjl-S*c0AM9U4`Sx|G?Ys46eCxW@_TBdJmil|I->U14-!<b$hMnFo$L4p?`1bFqo5%V+HNO3OYJB_m)Oo9&&SPB<7~j4gFur{~VEikt2U>U4{kQHrjBnp}1VbZre`-zD^~QCP@uOp3+pot>Uq>0=z8*8aeLZG;`+Cgy_Vt)^?F8N4x*s%txKY#PsaNsMI*mOzTldGlZ?$}P-^0J+zSZ*G>$)a$^!LuIug8t+UgJBNgY~#^ooxKr7dP!y-^=y3@$Kty<J;HaZhq@J+|6%YhsV0j)p@M@2;<xL5yrRgBi#1ZeMI=x<vPE8AB2C!eGvW?_d)pfeNgmBROc^zME@>u|7HA0|3PY;&HbA3L){B%pZh!G$6lDD#^2lz8sEN8G`@YG=;pWX6W#pQePaB=7M<sdse0e${?z!f&RbPK&Hb$LBURV#lVfxL>*kq%TKAv(W#ilT(Z;v$qm6IhM;qV1kB&aEUAJ#sQI9|O@5YZzx=r=d-0vITeh%Q~v7ZC{>m%LXdj4j7`}te=(jh$#)^if$U-3Ky|BB})`1W&>c&lSNkM%s$_TB4eeEWH(?YqyrX8uZj`k$j3KT>V$bE#MH&HffV=^R(*Wj&`dzWqEZ`ba?e_VX^|+t0OvvC_)7pT8O3e*WgRx1PTl-+ulUoDtOhx1LwqzWY0lZ$GcLeYgF@+WLE~=kvz5pU=mW>*;Z@o|n45^;|T%Py6<BSL0vteDy*H<=fA7UEg}H8(Y{>f3Nl2*!cEy<M_(kb$jdib0j70cz)|Hw0D5+zx{s1^4<3%_*c9iv3&RU@$<WMJy`F9j326%x-j)BzNz!*im5t}_1?<%-S5S>-&@(f-QIq`V0`=ig6muF7u-D7`-SMXhxGVc@9B(hzo!e;epLI`dqCTF_n+_I)AMD$_cXr!-ZL8cRQJbvuWJ10yH7?^^Yg9uR&E~ay_M@*@2!k)zqbni^K0!}?}d$TzZZ`F_G7-|6RcS5gzAU&KGFF0`$V_B^*+&UZ@o_pIu(>}zXvyd<gXodyuR~j6YX2?i;Zu;FE+mYzSzxUy)O<u-tI(x>)rVFbB5TTsmizC?;AflZS`!gAOEW73GX;7zqjvSKm57vzK~Nbfr%*URB*<O@ch#U^%sugYX1N9VSMxd)jxe`*`(F~_n$s|o9M&867f$$_%iwjd>Jkf(0WZkvxM+}@P2nR|APKb{EBxP{gwCz?=<{5dKCT~K7@V>AA&zbKY~Amx1evqFQIP{EAaLt;<ZHlObA~W&>?(FK!@<H0Ug4(2XqMc4(Jf>AJ8G(H=skfdq9WqZ2=v^tphrQuMg-DzCZ}?C4}D~gr6XU#}KM-gm4Q&xGo`Foe(ZV2$vv)OA*3V3E?_~a5F-<D<M3Z5Ppmhj-q?uTN%fWXg4^W^D*br&C%X$az%-k@or&mTB04{C&=?SnhuX9&nR>@d>!*$32h0lW8BS{OOAD%ujJ~2j)H$C*H36A_!H*R%;P$|X5?y$c7gYhYd886e1SaY(NEwy<f@G}g<od8_7J=ADpPZ&-p=DyVZO~=OAhf`)4mm287@Wpl4uq9HtM?*+6pc~Z52mL!rfULX=o={>Qg>b8Z8d@WnJ|_(_pD>`AjvmG~Ayx*$?dlCp&s=m~|m-#p}&_?uGV)ThP8anhbZNj?JFXi<<669h>#ooSK$-`ydgy%=x%P^uu4r-+chTjy?{*4nIu@rxUaATCx_362j%tZm?)g5BK6&v^Jbhe`gWGccIPUyWsw4GA!B?{)BUtI_t%F)+U7Op?%<ba2+%at^?nIc7kt!E1<353UG0>GF%)!N8L-m&e6YISjO!vW7!g}gl5AM*{n~|_u-%5-OTSO=6D=D1Dy@efajwx!}H<Q=x%s7`B#%)YNsh<UX5|@33otC!yVvuXmPk5+!`$jw}w;DDsT#%iq?ix;qGWtxGDYY&iTr@O-JX!J?OXTX9%wtb9Roo`4R62N6&|;^CEaD^rH>h9$xF{^<&n~0=(MPTryf89?P7WIg&n(rKY8yebF9p1^QVLEe2=P&n)x@xHWxkg|>lrIC}k?^}ZIbCTpe^nhf`0Y)y?xAH^H*==Is3=!<s)YvV?=A}lo}eSHtjg4@y8wrDFjmwx7;JK*x{A4zB}IF0%5M@S#Vo9XEN#q1~J@#?U)>!LTpQZuWm8_`!h{65F;)Av`XrFPU)JNh1?j?Qr&x%6GUBGglPB8l2crT^{GG<X5^WcJCKc=gz`>Z5hx`fwpM0L%CMBk{Roi5N*A+Y-a@0(|C1;@^1f>CXs4_#PsSv6h&Om&Clt_laI|G`D4bhoM8@d5q-?gzzf#J$M!T4)Go}B(W3k65p3hIDEI%_?kp)<2&WM+Ym$XZlqS_oF#<6cXU)_y-6I$bNCK3=7spaHGJO!VmaSEl<#X#jKGtzI!0Z{x%|NS?1VE=`TGp?82(z$X$QIs-T~*JnQ#tl_Bhew9B0A{sIldQ@LY5}JQscx?F&B&KY;dtAAl#IAy{-IEcG*%8k!70f=-7YfuAI%Q#<ph8}S}a#GFJdBPQVq-_5b`aE^uV<XCtx$AdZk8yfcTy&MZq;dlzi5kmMWLij~O_*Fu9D<K>sgb$-%diV^-!WTKd$njr<aKV5M;Xm<y^YC{Z3xC0}@Mjzgf6TG)+Z+q8<XFag6~`<2JF|Y5F&E323o~DHn8P{DiJ4R3$><~}uLgwgLGOk~pm!6)oxHU)g5%-L;ZQ<&h-Y4h5W>UIzrn-ck!aY-tI?4hOWcb$0e-;As{>Q>!jGa6CvS}i&qbed^465_a`Z(fZ|_*{<kiosPTpR&#>uOtt$5quU1$v61!tm%;Y|2A`XziE{vJI8{~JBy<kg?qGlk{%Li8_KLbwoGkiD`HHR_;Jn-0gqvTuw2=H&f;T;f>bJ16h=>>nIUe1Ufi&OkqdGvJ-*$4=gUEBp@nHoOXbn^=jrArVUwv7Zo*6T&3}I)tkRbO<*L=n!re&>`F|phLJtK!<SSfDYm60Ug4n13H9H5yA%v;Z20_bA<3igzz1N@NI<f&4lVRA$$WNd>tWNju5U$2nPw_`h@UJgz&9|@IXR%8X>$G-2j(lOiQ3u;D<P$2hl<BKynR0r^0b^eT|lYpJR-cq7TBilB**+0NzioedyQlCUR{=m%=xZt1;RU-axMP=sx%$xelNk;risNhc<>6lj~V@J$#B>C(#3NkX$v;da%@(e5Mq760XQ+lF%A(b?UMjS_&>lO_W8G;KtN+BeWVUbtRvvgqDR{upXMDjbN!s`Aki;65Nipl!7*grJm(84bYl!GuB~KGzFHmAfIW1HZaT@Zh$t0WgW?9I-yPAs;vJiXaiVkRX#Ha?F27M#6;%qS$Hbi3!VxOKwH8C;Erf5xFg&cEe|(_>!C&AdT<T25L^RJLJPu4a9Q+PxGY==Ee2PDYoZn4ns5X3Mz{go1ib}r0(U}t!=2zk=>6~@_(Ak}_(6Cn`X;;--iRK7H^K+d!U4?(;FD+&R_l$mA=(x$1y@5;;c9Rrv<ut_ZjN?^o5Lw+XE+6JinfQF!VS<ia09psS_7^Emq4$DOTe=CiT>TuEFruP-3;%8*Q1NzMbx@*heV#9j7Lw--|#?=2Xg*qY~*+l(bY3Hay)?Oj3?ZK;~t#9;Sk3m&R<yi_Dmw~BPP;cX>$|pZem=7C(^Dn(TmSWn=-U3!?+1cn?|$~Z3#=86O8K##!*<>RHmJ1Em;0u+HEH`<4K#sv=c24Z|A%=ql;i^Q-F4&MV-98L5>4NAv|G+WBF4MF3fiqL9d6O;ky^2@4{shiM~o`IrP8a0_3^|Edn<Q=+E4oh~8;|0u`?LpZ@E3-k*r-toJ{X+n@BmcJ+Sp&qOZwC2a4sLb9JFI#)n#B(3ER-}!Id!d-g'

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
