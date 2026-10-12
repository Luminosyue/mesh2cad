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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/b51e3cb5e548409f940eb38f8db551d2/part_004.stl', 'relative_path': 'b51e3cb5e548409f940eb38f8db551d2/part_004.stl', 'source_sha256': '37526e6eaea0438d5955644ac86e77da7cf5cfec90229e5b9f2447e34561ed3e', 'input_faces': 516, 'input_vertices': 312, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.14878952503204346, -0.17105725407600403, -0.29711276292800903], [0.18171916902065277, 0.42762336134910583, 0.2244570404291153]]}
GEOMETRY_BASE85 = 'c$}r133$xs+Qug&MF=Ue2V)HqTS%(3&Db?gNp-UX6U4rT#@5y}mZDm1V_(O1j-|B~RqJSv<;WnGMy!pUoE8<eAN}6vdGG(5dEaZk>-w(mq}T1f=jZu9&pZDa$s?(R4g~|lZ1SV3ZDV3lucwmDMk;0tv!y1dj2_r0c~t#jBgO^TLYdQt<>?*Ydn=)9fGyQFA);^cs6HtX&Fm4c^=ldtWsm4LJY{rB(y(5`Q~D+oZ<{n^RI=cs1|*G07LRK;ZWJA5Z(JwJ{;~c4`4LQKm|pbfeZt(KnWy4}I~P^Vi1X!5&;P=YuWwGJ$F_lUe`5aYQm%J=5hClsorTuP`em!f(qnte%lpZ5ZcIN-Jf~G>u2;P6>@2Qd_v3Kxzhx+M_qHxv?}=$G`&+zpA6Y*;b0pWV>c!j{(p|3ycgOUT^$V8D`pLN-KG%ghT<?yEmG$7xz!+KI!#Ro`dn)W?o)Z$s&&!?o8P{9f9TR_s>(fT{=K80tWuH~Wx!%=roU8}82bGug54-iF$BxC#WuNDvT<^Fvp6eA)tSIY)A0>1D-(ux?u7+v#inppF>%-Ey-t~CqK0Z&zul#(Sj=@~7cx0}8zEj5!<omO55_9*Kt6Xo-93t-zxU=LPt=`q9fvkW2fX|Z?xL5WEx7V~~bG>t0Yd(Kao4tI_^nc3tN&gM<{1(qUCeQCldYjL4q^9J-M`Zn@jq*I;?m?$z{pke>d_M<=`>nUQJNg&Ben#^>%+Jo3=fAaF)`L3(R>}Hn?hp9<k<pSbU!c`1Zq(b)T-?p)>AqIpw=e&Y?|*RT?(gOOS=A_k-(U0ccJXzQW4S(O;?)d|f1W1m#~yI->p9^JbN7>pT<=<TBg2>5t9>r(ZP#1zIlG_sTd#Q68Ct!g`@Nmq=c`U!?+iGT;mdRGb(Qt@#0ci$xy+r1JL>h|IkokA&!IW8e_kTrH`m{5c{Tn{|Fc{l`m8VewDmu7pZ$?s@19@I>&u<Fv9f;Jm?Z8qc$Vb1V&v<xqoUWB+uwA^`ayBM`J5qBW&bWsxZYX2g4dV3cf6t3N3Gt$^*;o1ea_ktuP=9(Eg|c($MoRmcXW~D5e2#4QK6XEm)oa>==HJPWdF-0`Mx>!b@%#mXK>|nTtC0_NPb=qhyTEQ^JVUD-~5)>m)p<&Ci`#MGmQIHY9aZ(oAUgQPF`Q0)9JpfUpi$t-|zptF8RdUvOY7x>&xwH9%%Khi|=pe`n}ub{cqgD>&xvo_se?w(!qSrJ?}7gcHE)WTRbQAXIWpSzz}|Yh7{Pw{L&J>KklxRy}sO8Xsx_I*OF7&@BF!y=a$v$E$)n4qt&~k$}x9;H-zh59a6o%+@3W?*4tN&=HK5?)Nj4T?Zr`FH-+mxi95IO++*+X^RgG%<<)rop69v#ap8~U>yo*d`z)!(_0GQQy}mr>d6cY=X*YrUY)x57+|lIv0dm_s=ZSs3{LTH6-w)Net^E`J`tKSzO|L(CO7fYn>h=2$F!v0J)%oe=lFz!CsqsancwcaQyFstF-{G&@jzYaO?rC(Dxob=hz5di$zxA%R`y^jjT(9r4Rr1~?biO2-zkYf?$<m*1wGig6<)7*OXWZehZ?=+Cb>88Y<Y|-j{&QCD^LKw-?=6w_t7CMYvtYM;-p_QN+fnkF>-GK#wV1oYztef6>i+Ayo#)T@j<}vWZ=TKEwJ}kj8+e{S-?+ZDpVWBquOvTyLa&cWV(y4It@nS}&3}Dd8RoY5DLS`>%KEx##{07h|M~W0#p~zke0r<j`&MBwb4UCmou8Y-+;;A<&TG6a`Or1`+#B(d$E?-sUw(uC{5e((*3VNhZxh!a2-mo+XAX1M=&CyZD~q}3-O4&2FlUp$`(_KCDeK1^*ZI~T*YV?+FZ4cBW0~6~w%2*#y3Ac)y{_|)FV?a<TIzhEd#%6wX6rM6xu<uY&f7j(!M<#d-lyzn=C1gGM*sfIJ^P30Jf}Hx$EiL#kGiy+`wXq1^TyvYchnEl`O+J6xqjqzowq$Shq-r-&fo3B+;(Y(&ad2`&GoO%*7?&`%x$kW*ZIs->HK(JYomW*7oYQb!BhJCJZS=R$5y>QbNv|h61#PtJ&w7f-7cMvt<Qg-aSR$_@aHN1-nX{LcRr1y$7$zuey?*H^YT}9zNYQuIDhxY{WWvX=yaVotMLuj?>ejVa);&;cb!_S^Ux>EZCe-U+!;TgxTDu8{r#5s5p!2ow$9_9Ft;_mp6QRfKg>L?@xwt2xPHVny?%QdbLYy-$Nh2p+M7o;UMr8ed*=n6&;4j2*Wby@(0JhQ%-w(8()rldi}-nUE_g)aDXGjo(KekATEpBiyN7<?ZX9LqE**YY;~RP`;r?-%`h8n7i@Evr(Kff(QtqE~MZZ5~$}@MB^UpoGnSQzRV1|A_1LrcgKe(Xtv=z*Ao?OxI=lIji-H(3O>+hFb#(j!r>-7WPUgr08xz&TY({n|?|5s+o`Zw<CypGMy{S&U~{A#4+D_{J}A9n`b)%mZjC7<+6=L<$io>f|Zz0z06{_)QaY5Z@;n0uni9@O~o#mo8i$~dau|7&^7?d|vJ_ibU*6@Kp<cuwdg{rOJc#@zOPu73Wp(JT2p3m@v|jPA+Y{d*{%Gv}L@hxmNPzN)yfuUg#PS5>{Suc~@uUsc@LR~0w*RmF{c)#B#9s_Kn>)#B#9s_Kn>RdHiqRnOPhS5<#wUsc@LS5<#wUsd(SzN)yfuPScrtE#`TuPScrtBM=@s^Z4Js^%K|s^Z4Js<^SQs{Y2ls_Kn>RdHiq&3}LD`>Lup_Ep7=eN}N|Usc@LSJhl&Usd(SzN)yfuc|)AzN)yfuPScrtBM=@s^Z4Js<^SQDsJqniW~c?;>NzJxUsJ)ZtSay8~bX0e|=w7+}KwYH}+M<jeS*dV_(fbr@pT$ZtSay8~du_#=fe!v9IR$*Z0-@_qo2WDsJqniW~c?;>Nz3&-Hy(absUq+}KwYH}+M<jeS*dV_#L=*jE)d_Ep7=eN}N|Usc@LS50p1tBM=@s^Z4JYI18|RovKD6*u-(#f^P6|Mk-MRmF{cRdHiq&Hp^6@2iR%`)dB{tM9A%=hydD#f^Q{<kr4wa%*4BzYqGps<^SQDsJqniW~cC{^wPFUsc@LSM&e8>-(zW#=fe!v9Frk+E*1f_Ep7=eN}N|Usc@LR~0w*RmF{cHUIOlzOS0x+E*1f_SO9Nt-h}+?z^uhXg~c8ySt#(rgAnLsfaDi)-TEDN52H=!*c&W`W@Kh|Ma8Zm`1Vx?T>yti!&t9Z5Mh2{u)HNJv;%KYU04i-$MQya%cEE$eocB;BO-*AXCrRG4D-yd*t@0c@uMAL+$IBO{}6&d7*mnI>_WP$mFjgHx+6k6eUyvUJjyM8{P!D0%k<P>mf(^^s9&dR_~^G{3>QQfnw0JJm%Gb*G8_5nmU+U4z=Ymn^=TUO`+!SSCGkDA(OX5ZY$JMsF_eLcnyehEW9OhEzD>JZ;sr|r(bjQZws}<_3bdbCDaN%YhvCj@L1$n)L6VG=GVk*%8i8@3AKT@Kql{iOx_8(qfoq1YoTa(Lx{2i9*-Q28Li=MkX!roYlHq)?~Zuf3A5v&4(Qnk^IE_i$PU!Bz}$wYZG_pxN(hArRfktWCXYlWZ-881sIE{oq2lmj5ar77y2!;bqZ+(Aay6fR)zRPTT_2AdV0K+75<NpOuL`^}a%I$1!Q5h~4Z&<;g@l5H%EC(_lUG6}uZnCJ3KuFP^b$M}qFfRlj{Fj4l!2E;F5}a$Ec)A_s<^%?W`{$S&@%}0O2JDamqbk|%nd|s5M~oAC=?)66kY_G{AFbF(#Z5>B~*z1ADsel>w|J(cqnoK%m{`TMGp4qR}}rN-eGuL8nZ*8m(eo-^NPR=BNs+Z5zMurHUP7U9TGYylmS12OnwZRJQKO6P@+&*q4(hLLX^9}6OrG;jIQtu<gPybGSI&#l!@yzF*^}DhMos8?+CmLau?KC{2=BZ#B9p{5;`n&0)8Bs{4_Fo7II&q-a@^EK7hXuQSJfnjr;*-^n#y2?&Z_(1p4=dvT%JCX7`3pqvv7FI}Y!G+ygZhKaBZ@F`M#HA+OLG_%F!h=aI=TA`ccCD3mPJ9o`M1+y_1oxjSYg!_Ocm`}8}5{)3^5xc(w$4}{L6rx){nf%ie~gBpu_G2e^Xlurqr6uJOEhfJP>OnwD<gwQadK|)DzCq#Jwd>C>PW(<N~Kpy1N?*jUdfUe;BE0{eD%0bVQn0F370C@mvEPfL6PhvLZvqITISK*hD$!{W)-$ouI^r6s5q5klG5ar?U50U$0#z^>8<dHu8uA=`K=r*pujoBYUH_<a2^De`OBM(Q7#j`O#8?!0@Ds)Nc7W@V>`R~Z&cac99njn-aG!#ArqC6Tt0eL89q{43@r~34}h5jEycX9n)%$@-Kj-Hn=?*@D{@@Ujp{1WD0!feXdg{}$Rf&Yd~{s%Jo1LQQJi9#O<je@5@l*hv-B9Fq1kKlKZKl15!2mRBa2e|$LW>19vK+kKK_ZxgX@_5u({2Jz8!)(g`7RnX+6P|}m{s@`;De^R-DMFKk#=*xzls|<}K^})0li+_MPx9&aC;Cr=p5pqam^}r0gr2#Wmk0k8`BT(bJQwqGF`M#zp?gBl;7^drUm%my7j4R43e6OnZlmvEOaBC-{26>EvI{e&!=E8fx8?VHhW=mTG3A-?7w9z;=lBfg`~+wG1ndd?g%7`n`S&oJ@?)Wg)H*==U&!P^0Wy;pLY^ady3j14sqo1V<uBmr$Wt+67Myy_!egsn0QyrVQBH>kA*bU!U*Noxan{M0^A|iQAfG?P{D+uLxuE#{0z$#?!pP*skjX=k7l~^Y3e6Y#8vYeTc`ke*^4FL#A0CWMvib$1KV=f-h45m?B+As2&PnqM!{;K;MUBO&?rV5K<o^gg7kVi`dSHOe<VBFliy|)&HS>gK3w;is0a5-2J`eeG%$N<Q9<%Y->h}`*QzlWK2QPw5qWlfcI|FB(fjNQry&?hm{5j@7$85?Qh3NZEOW^B~$=4#2FGemddQ}uEAygIK2%=mGUJ;pUXhsS65@eFqZwdNSCQ+^kUyDqlOg-tGG;ck;5^^QfSe)vr!Z#v+FWe)v9KHdW{99!5rO2V;n#w|@glfX0A<A}mW#pQeQ3}2snPl}_j{a6}@}*!jyD~Us>PhFMc^lw%WIJjo*Tk7TcwXOwZ4<s<Xa#&TGWmDN<jas>7S~h}3KNQeH-;!zhgU(4z>F~X3S^SiZw2~Wy~&q>(d;VVl&L43ljd!PS4Xan8jDk11biFvcHut>t%PquCf|fi?nW*tuBj$eTBtU>2}HRDyc%+C%qR_CiA=KktwevyB+Av`n~+JAsVAM2=52x3K(2ur%C&K(pYXi4gY6Xlv(Rez56I+Ok;zvfml4<05-KYc1&@I!*MZkUj>3$x@YTp9tKVw$w|bMW0;Acrz$sHtIw#Hh0bU2W4r(k;by4u0$a{qUQ)mr*7c%({Wb(fwmlN026{;ZA03Hibt_QD++yFBwz}Fy?tbS|IpE8MZUHA@U5@qU1=cIYN;PsH}p~m7=*8si;d9UyTLhInWk;#8VCjSR=d2vmoP`FS-_$v_Q`tV5PhL{l!Ux!Sx`mIBMt2g;Sz-V?PIA!Wd=cIYN;q{U0qsHP?*ATuJIiW*9fv|%A+dp;7|8ND+ufG5A&Ad|oF^TV$FGMf(Lz9FKLG*nyTLJMO{iX0Web?CbKfA-+nE'

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
