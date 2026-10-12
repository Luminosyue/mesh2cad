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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/0c4e4a0b2a374553ae762bb33e8dd2d0/part_007.stl', 'relative_path': '0c4e4a0b2a374553ae762bb33e8dd2d0/part_007.stl', 'source_sha256': '1ab47e37e8d731e5cd8ba0362d8c0cdc98426c49d95ef65d32915a2597689d1b', 'input_faces': 354, 'input_vertices': 230, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0995887741446495, -0.09234020859003067, -0.2625713348388672], [0.1287904679775238, 0.49178552627563477, 0.2640974223613739]]}
GEOMETRY_BASE85 = 'c$}r02UHc;+J?s(P-Dds>lh1mMKN|6W3NF)6k~K0QL%%HVm)H-4LjmN6zm<vhDQyE4bf;Uu}o~&=rz~alMr*+@Au+=VBLSMfBpBY^{w|gFZ=BM&2F=27Tz6m<aE>IQ(kL+I&4Y7Vw$ERpXR281O$%_^bZ(QYvkzAY+6D1>XV@>y7cJm?Uzjp(I&YM3>f1d?A};+Z#t-<dkx)v(5T?C!Tm?}8x=e-K>2O@4<8ed?vEMLe{?|l_bPSk)v2M^t6D>!qW?cXdD2rbW2PQCnXbl!@tc)8&b+*!RGZNSzC9p&v{L=>efU<3ck%dMw||sUb4?t4$FphhZC1~X_#PMn-<bXWFx2<)di<_V6{-IVfAR0lUxV^5ubhWoN;?F<Ucx4{m$Usv<gxoIe64v9+O>Xf1m6~UT*?n`xDvmQ8iaamA+yEzbg?7PJB3hQudYiy&B|_o?!AtDY*%CBpm{5<gFkVh_~WX=*Pb+5jo*7Ug|Fvbdk}w5>KTswUSCJM)^8#3jY&h$uDxX>+BFjDz_*IGjf7SnFaE@92asR+4bne<HjzAQ425r0e~tdplU}1;^VaYCah-<WD)@_HWLzeO!ngaLT!G)UYAOD(0QlPc$;ijHx%?&ky<s^iUwbg}F=xG(eBPYiC;cCXd>p><@U1Pq;A;(XtcB_$#rJu(7v(wyA|KnM(vp8#koe!O#dtZ2C!k%&`(g0SK4(`r&mZkndH6=-g2>Z)wLtQG6SfESdgPb!I@wz4=^C>efBz#d#>*D=TJqnSxC?*3U3Ine(>nOtXODNH-kXs!pVyC0!S7xr!`F|s#W-5OR+D-{E5g^j=OKT4U`;9ipyv*hzus2ndCfbLkJqH_DDRah<M_)|__o!nw!uF;6ys=YEGgw5L~X_O_tr6Q%~l(w-G~<O9a{><ARoQ*Wz^#m8Vf(BH}W?hUPV5RiSa0B`^^P;>XBpNYybGy7U+#%(Ql@AUigN01^DK#e_|Ysv^A3F_OG%2jS3zZM`LvX>HpbrSclrsc{^pD7EQ(Xp5w&tKNR^|5h<7D`g_1P6I^7ztZIky#y=m)ev!K&+BbTRmhvYyM@hfF#C*5D8Yksv^@4BYnT`5vd0eC)n!LgMFye+{9XmQKMR`Y=i}3Z9r9}@em;TvR&o1M%YrV|ZLh$Vaiedb;kA9dZ*2D3*UVFFYGQV3^$Nr=bibMT+)!y*!<B!Suz7-AM{=yZ$KK5@}H>YQcAG=NVwVa1BPp!>;;9GtzWFFicEb}F29r3fBLmsxKcQKyEi9c|?W^_CFX7(ExcP(%(e7#Y;j8pDP(tmkfrF?QZ@!QwJxZ9&balK}fek*024UqOLU&ZxWh1`~*-1=x-ulC`R^yjpdi{Yn@!v1FuPLgrib9z2BUkdgQ+rR_jC+KtWyY0s?kF34FT$cH&!8Zzh#Qe4A^hnL*&%G|=+<AbEZ^X+v$m5GDvVU|A=X^+=BkeYj{qxQ_8Q=Cc@gJmOU0OQ_OZmE{_$`ZId~ANjWnH{-^~dkbCgM+MA%6e%1K`&mCH4RHPW<-CrmV-mWPJs#ka?T-d0*6@@*LM|d!Ap`#a!23DBqwi)`hmVllTX-cfj>$|4Z_8go%HC(pWE5Z&aPz(7CD7Zu5f^)OYjcCXAOkwY}^=!{5L+mM+Hl>e?StKF%jp`L>3Ea(^7P40#%buZwR~m-~BQK4~{TZldz7k>xQiTG6&LE;+_eR=)jAN6b&_aEO#&cnH2NSL|7(j+tpkGx_#*_mQuM?JV-_>0`t9C&O`F=9pC3XQD#FkpI&Ux8O%7N`ID~IzxTelB|=cfByMnC_iNOEacgFfVBJ2?S!*$e0VPYXOH8ZeXVt6<YPA%CTH?X4wF2`j7>tjOTy>j`->qC)MK8<xyQ8L%*S}#KO*~XneNg*@7)%lo)X@&k7?CqzSRqWZ~OWx_AC3oXEOh99)fQ^$cF1O90!rV5t=CFgZs!iq5ClDhl}+W!XKF{0(m^YEA!lKmH0K+$vGsbfsFfv@I}by>IggXkA52O<?P4)7LDteu=!vn|9w96zp-`L<xGC(De$#U9WJ5&JXS14z5erM9OHY-zTxMy4CPuigm0xCm-|a>(dDSO!4uSDyITPLW9t#P0_DfF#&{X6UY*F~zb%e&(Zl{scJ>{dS9-?0$|yfHRK~GuE{vl+!(Zc)jQSIEV?Jo_BH<f_+hM%yQ`}|0ZC4;1c}M&5ewst}`2!onWqg~-{c7qKjElW&ot4O=u$P>d+-u8z+qoWm?P;{kpJ(@^-Nni99c7y0e4;1slJR=&y$a>q_QyVL^(-oWWE_0!>Y)VuE^TlE{=P79E%M(x9{p_p@u1wN&TNFQ-Kex4<&AHTdpY^Gt><E(?L785`_{XCH}O0B^3+WJwwp3ue=WU$zwe*8PBe$Kn|r(LC%GoWH<mO;zZpm0iNDAbd1$`N<h(cUpv>pWxgt=$;2JqEweBVRd}!W?|G2K{>si+|eMhS->zaPnb?vzDIKp`y>2IIO{7jm)0sbQ|xvufsWM2(Rf^UDePVU>0<7C}!b&W(m)2Cv54fhq;9~>WN!#5|i!+lk6_)PY<OC>j=9@m<(kIkNf>vH6Yf}eGtv@-lG`>OS_a1_4(l3&^loQ(a@df^G*m|aWye@(LNGgW56*B9SK|7$aL$h-~y1-@;<KzR=G87}>w=(h>|wskk|BZga18Lv_);`=Scymch+Mn701nqwbvlnRq`3h$eGTqJz+<r18q%@QYNemYidK|RaT)<8G!JmKZ!+dO`bh5pO2CzC&53FfEu;Yq5q?|9or=I6O?DbBvp{7?8+$EW8}ZbcQ$d#ij5_F-e#0_mUR(Xt-++?sLzw7JSUF?xQ${4}b2N_p?9$WN=08~x*WVafbiJx}t^c<$IdMf{&0!*^I7vOo89lX+FJ)>hPWR-O~B-&dl4v?WV-AkPh5<ay+q0O|i@7vX1|Hylkn$@+ShZzslg=}Z~NLWLyH(p}*jJm)*EB}lvN7l}XjBJwmA_K`e;6X9DOPRqHs*(=Fs&d=~QH;0Vl{UDjo(|hlRpJkuP@U!kS8GhD%=98agpK<hw*bA*-%JWLw-ncGn_<s0C-iPQPyJrjOhl$_A*U#0={9G{eD*TN5spH~-6ldRfYRUQcypLS(!aLG#rH|MjjOm@_xnR*fseh_J&WC2LyV4IHk8pii@3Wu$Ece+@ewO>}CqL_bwzcO0XrJ3Me~uaQoH($r_#0XyPpjHZ$v=2Be9bB*&zHU<r5{2<;Oo;zOFzu<mGl4PsqoEtt#O{wTlq?VP78x?c%{g5+s!kw-fc7C+uoGJxHw9bl5x=%$DusuzkRE_tas0A;(web>xj=6TCbdk&|jq@WxN*mlYSmm5x&tOT+UHXew6t+<tr&ad?L=zMzwnKyklz&U;C~!&d+w=QIgN@>xX3?y^!a-d4I`!iB}#NA3aBTIky*ymwYOP$hc*^@0!(J@@W?X-*kC}{>ga0w)g#B%Fp&eyBYg~J}3pgJ!ybE-}MTX{%`a55#;mvJ&c#lCr<JS4?K$eXI+u=IiEMpE63nFst%Fo@;;?x-ln}3|9NGMubE(%b3*Zw$Ix%967f84xa5+3{>y6c&1^36ex+d>8Q;^{WxYmsmiypGFL@tQcoclIet^8+nEz4o>~adeaq<TG$INC&p8Dj!;XC|C%KHibO42`TDq&xD{Qgp&Yj!V?{9_xzH@cL<`y0bbk^HOw6TUY2IOdPJWShL#8t;R1kKJq~^R~!$lIOln;`5y5nDG|A<L*89=Eu46y!>FCtd}$wIcIl>MZaadpV9J`fp3{p<ULS7UGkrQ4!*6(5AvR^&_{WX_pG?wcXu7azG|BnCGY)mH-n$?9#Vf<L*7G{{uaL3xB~i3?+`2REo%h9w^vI<p7!OglBefn__p6_Ax~S<H<wO&XL_65dq%~sB?_gVMAO4nbJGU(cY2kqO!djo|NJUB(DVQFD!E>L&;RyS^3e1ghNZ_4hT=e~jT}gxO5H%7N?u3ZLtaPTMLkO1MUJN)A;*&sQ+JaOlXp_rlXsHWQm2vElBZCIl85rzGW-a7L&?J!5xhPdc>^PY*Rh9ulo7#vkC1mWBA8bM+fzItJr<_NaE9W^)Mez!<oVRa<oV?3)Jf#&<dM{Y<dNjw)NjeX$=+0x>`nHgP9RTUu71p6gj1d)oUUaA%lMHq>Kx(J?g*#cMlkmgtXJ`v^q8F<!3@Q7sY}Uo$xEoS$V<p`sH4bp$fK!!$fL=9sXfVk$-SuGk$aK*QOA(SFxP&}A;>AuAg5~yVwryAj5>py+6{8bEr_`Xv0lYLrpJx+NTpsOE4@HYC7-7zlFyUBXDCjfI>-s+IO+j%!SqmDRWWLDaxrpgY8kT93gpt{FR4|@Uy`dZ6njwXkv+&wsm;hrTa%lTTT(lbTar676#G!SlYPkk)Bv*5@nnB;2z4Ggggld>cqMfec_lfDx{0iG8##)+l^REmWB+euD2`<)-p^2cis~SrA}3K3$x1JflgJmTSI8I1R~d?LQg4uNlJ7AT-=+RYzDvHtQ2Y}^@pWn{`8xSBL-9H4dGa~(8S3|Br3vIS<m1#h@^SJZhT`qiZRG9bXzC{NCXQb;L-A_rJo0Mt0*2yH>UeS}c@Q;#th76M5V;$*6S*6?BSUdpYHM;^a&u}kveJ6w=44N5RkA0!8bfhKY6Wsda#?B_veM$@vg8ufLgW(U!VJav7>e^U6z8E9B<CT!G87kJC@xAZMlMP&MJ-KM`X#v(xjeNBxjfmOp}02HgIt^3gxZv>v?aL-xfQiDxfQt!LvatP54i_<0M(zYG=w~WJdQe(JdQkrp*Wnnk{nL9Q=`aAx002{k~dOgsIlZ2@;>T*veHxJedLqWB=Sk}S%%_E)QjXx<R7S4$x3gMe<0tY-Xq^4-)AU(%uxJ@q4**7F8Lw(0rd`9=}+Vb<exS5TrGN=`V(2{b@FZUHR@&ZHF63=aWeHBIhlN#dWNj@IQcaB81)eO82KPW@eb;C@(%K5YBX8tYVv0C8tMY_8uB8B;)&Ey@<j4r>L9YxZsft_uGEg?uH+63#qFtW$?eHr)aGQRo@6g_eQGsweR6e%;!4zt<Vs|nT9&M|1X(ASq!uQZBo|>Q{+ybR{5jc$p*R;cFF6-ECqr=#Y94Y9a(1dKS$(plM{b7V&#2kS*;)QGhT{Cx0%WB{$@$4{)KX+O@)r!n<*4P!<;az(?qsF4$(6}9sZGdA8<T62Yfu}Jl{O^TAlITcAlD+-VJNQ4Q2Z4`vB6N>f}!|pYD4nZ<Tlhs<VMV|4MTA|Y7?^3R^)c%Z>U|!N_&vMA^TDXkbTMh8H&eJ$C1a9!>BXJO2f%v<P}sqS?Nad3i5J>;z)+#Ez}tD7V=)|KC;r2<h|q*>EYcmTXwe`|J%Rl{m;jyCUT~K*vtCM%&%jdf7vCyu1_y#ygTMn>mz+JWXFS7l$w#+zX9q!aJT'

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
