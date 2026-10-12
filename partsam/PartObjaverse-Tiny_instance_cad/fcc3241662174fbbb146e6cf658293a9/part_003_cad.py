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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/fcc3241662174fbbb146e6cf658293a9/part_003.stl', 'relative_path': 'fcc3241662174fbbb146e6cf658293a9/part_003.stl', 'source_sha256': 'bf57f2ecc92c45700ac79d53cfbd222568a8c561c40de0f4a09ecde68b355d95', 'input_faces': 560, 'input_vertices': 298, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.3556981682777405, 0.04262831434607506, 0.4629926085472107], [0.361838161945343, 0.053052984178066254, 0.4652012288570404]]}
GEOMETRY_BASE85 = 'c$}r13z&`78pprEVBC!{?%J+nN-l|9vr8#Nx}dvp8FWMA5=Ct%NlB?x>Xb$@W=v9~h}bAXqEtv}N+Ak$N+s#+cYnXNn)UAQJkNQ~ndjMkzu$kBHSb#A+TZo5Z?BT2(memCfmhJB<@KZMdY*hLcxm4F?3}ST56K?WV&v$FNnVwBE<a}bM4x`W`(B&mjrZ=(7@9q1NKQt_P)6rr?K7H(GKP)H8Jja`<iJrmL$f9CKIpbF*|B`gh(V*XW8UnX4(*$V+GI8lO%DB!KjmU2gx7EQw5x2t9K0~TEw}88_;%q&C(qqh7?_7Hc`KervNpx@NdNcqiuYskqSk*o{YNj}63=r(ALSMAU+1QOn?L`rg@NtKZTtP(oH`?i@&ofw^S9%<w|PfA&+74AUh(!i*X_NoUoQ-5Z*tQ<(&;0=pXQgi^F!|4Fg4%FhkxwnGp=#wN9T6_$+P~<$q#C8ayvhvPvUt<?O&bS{x93*=Q*C!Ugx@fIDKnidz0IGl6O0Q*UrO)J%0PtDb9Y;xt(W|kMEfu*q+?9kGB5IU$><zxa*U=Xv$hA_a5Bm&*w7*&VJFk8JEeuV-50y+MC?AUtZ+rzrE$G6O(7ns^YAZXwld4JbKmf1wnc4xqF@V-n0At@lGn^)~|9~54l(2o&2EoCfDu5Pq$kXZ@+<hDtznr|MQ-Lpxm_gZd($VhwH3x^NvqA{fF;8;MX&!le12AZuYy$vyMNSAJpFDx_xxbmj%V^)VZnC{@u|t7X`I9xoID1f6y6k<oCsad35GVf1V2u`TbmVq@Z|vo$L0Iy;BwiwKutKKlD3)T+2qe>qO;tznlEy>+=KKlk4{0f$7eAFnQ#jeeU|Hci7)Acg=R@U*~q6kSDAwl_#`+eRptsa?{@1#ozsWn)^K^_g=mzKPV3$JmJ)@bKSrG9+^BedGw;7eoSuH;jANmJ@X5lb)s{#-%XyiZq=fo_9i#&BR#(Nk29~Ga`vOiy=Aw!`*GC|{(9KD-rbKXxBG=Wcg{<Tg4&zh&fB=7{yb!T;I1q3$Om)X<3@{P{<yYWT@aLe&!!eS{Tw>x>|dQn%Jt88zF#W0-!Jl_$L{g-c?E%a*0*mvdGvxceqJ&!Fpu81&dEd5QsUzZ^;{5`dtKH$xtRyuPxPiNcYT^XxlEz64pnZ~;k@I1Ugth{y_r1qu)E$=Zr9s&Kl*vUP0o7Ixjn8{`^i23n)OK@>D|UZE`=8d=jM8bJaqH$c<zl~7?|t+O&+cqb#ik(X6skEu0QhDlm32BD-6twa#p+jEMDr@vul2EzGQ=2=ck+9>m`*(=dN*cvwpH)49@lZkn4G{>$BmzP9D9rTS3s@HS18<Z;ng$`+MsN|9h0R)447(dG3RU<GH=BQMuXgCJ&El>|R%>++HV;hx*-=7u3JWb^k?^$K?gqd0l#b(6~Y?GyMHN?d8Bc%Uk8-=J=!gx998Cd4YLkOVk~2o7?k)#$|FnuG~!%0_!*TJNCLr<@UH?=BLlRz`twrmF{>$wHCV9bt>2UE4=?@f8OfP56p{3yyND%+nwXK&dqV#&gbc(!1_(D=Pi=)Tj2gO-<N3NyudtRyrw<hBb{gMeb?Pz^STrS)nC+XSV7P{nB#52`aJxRd)=#Yy??_Ce{qlhD!1nglMk&~7}USXb^p=zna+7UoN_YoxZ!O$8F;=hd6qg~B;@A$mRz4Nbgui?=L_4vI$!AAo|nn>`9kOBd|~@h=Zl1#<E^bzoiB85)|<`M`640L^P|oeIydJFlk4+^&DC{+&h0vx^hfY@h|2ACNZV6^*MTP2*MU0M{pjmJoty8Y$@O)h&dv3k$@O)h&dqh8$@O($^ysO;>ph*@>vr;l>*xGG1FyrqL8k++^L1|b*Gz9${P*hq!sH3}FDke5-#y9C)qR}F^?jVl^?jMi^?jMn?fm@Z_G9N$<q7Te{i(`r`xPbPxxRnbxqbd-a&`Z%bKPFwr+Yai{ain1P`RD|Z%R4iwci(&+vES-WPiWt=R7L6=Xdh3e$JzE`}}Y~X}=%!+(zg2`n*b+!2PK6g!bzBm3LoRe}43HIhEV<3wgqGIhE`7dfkRQr}+C<JwG(LetsApQQq%gJ)bnWem?2VuIT6bd8x{6o#YA6OI2>y;gPC-Kl=GCdBXGC1*!h`Q9V!AxqZ%0uAe9C+^)A8X?{QYIra{6{rp_z_I{H*;rY4B?L3@HcmA&Z{;J%zUtYtXpNHJ{2qxF>9Zas@FX-IX|5YtN*Y7*X_4^L*>N<XV{r*MecE6A(ynj)--7g*LJM&<V11h)g1$H&?*S~&0rE)uO<PrUTO67KbRyX!@{l1Jm;eFY-Cc*nx<@P?}`eupiu&?vB@{{F_$3<($x`=&Jyfkmvpkl8oC6pht4SrR5^SS@ktID?RTK&JTDld)IFe>)x7yAg`hF=U{3TNTx;Vt1y@GkIq@YVR`a2NPG{2KUj_$ItBd<}d(em>k6?uWOB&xbF?Tf*((i}6-?3-~;|6Wj{!g7<(s!I$G#z&+q=@SgA$a9_ML+!H<@Zw+^b+v6?Z)^JO_1AY$N3hxScfIHz=!d>AW__gqr@D=z~@U?JHJPcn2cg8!yVYoGZ4%`uLf%n3@!yWMca4)zkegoVez7iK6h!3P*!#CnLQm^3w_yFn^z6>4!cf`BHm%-=Yx8sB0UifJEcDO&D1CNGpz^B7G@IZVFJRQCfzXKiv55Pylcfgn7gW!>Hcl`C(XDQiI>J@$!UJ8%KUx8nRbMVFREAVuD3A`8{gTDqZf$zYDm*LB(_YUeDN%lH5itobrz)NxAt@u{z72XVQg<rv!!<*s7_!f9MyaX41AAg^^4e!QxQ}1ikw~TBLHHsg^e}H%4`{0A{R(vnK58jM_2JeNJ<DbKy!CUYz;m_gs@k8*J@NWDE_z=7YKY^cw58_AR6YxHKKYSG4i+=&{hd;x=fxm!1$AypK$Ea8MSNIrw2tNt`3jcurhW`bhz>mYf!AJ3L;p6ar{A>7I_zPV40DgeFg@1$(z{l|4;UD2&@xS2T;gfiSB+tu?eVQcsoPi71!DV|!F|Lfuwi;X(t_)YgtH5R9G+ekYF56HsZivga8QcVJ2xsE8VxM%fbm|r^2dBezaN$yTDe4t20hfZy;=;*zGIa}=hm+yDxNvp6I`!72&W2>Qs8Re6&vy?_=l4Isk_ne%EW+R6vMt4!ieSlvOE4DU!?<jd8PmUD$%M-@mQ%1~!qpj*N9~e%)F}QC{-EdcAGq+t_`{6B@FVymj74}B{0LlxKMK!+597i!@tKUl@C<wgV-S82o&kG|<xIR8{17hO25&>%!WY18;79P@@CEQJ{6e@l{3w1dd?7p&7d{I=i+X2L-wd*5)F@sRuMD4w3)jW#Qm^5Lcth$HZVESqd*hAZrtpQha6P;pbsJ8_Q>oW*WxO&q3Mb<w;i`CfI2o>s*MQ5z4e=0M18$1fghOy6yaHSku7?Yk#!FLoJ?cv(D@l#wNw^0m<H9L;3iTSUj#sB%;W}`2IE1Ieb>NzKIXE4zfD4zvOHgkG>MKp=QKNVnycC>-3s=M|Qnzp|xFTE~7jA$zpkCqHa056UuLReI%i+Rh@v_ugj`~WFm7+%RYIqg63@%(BuTQ<gjp6!mEj$Bm3^%}qo8V2TSNIIL30w&mPQ%lvw-WW0C96V>;?40)xEe0p7H><vhP&b2s8_fT+zrmaFM|8PO>p6McsuGgd^UbI^%~B^GpSMdB|HyqjtkGl=Tf)fr}3w$S9mu3G~5TD1J8yp!e4;r!0mA11^5E$ZbyA*ljTvP_@8)ElFu*U!aw6bQ@7zG_z~(A{t7+<&&I!pzk=uB!oT3ZP`BaJ_-X2Wf%+DZ3Fq;<8cDv_PV)IreqRBu0sqXHO2d)~A7M--VabHQVk~7~$%MaWEW#CW+5Y1F%{6h^o@Pw7;hNN%gg1?C8<90)42J9B^%#TUs(4k#Ae;hMg-hb8a0*-ouMelf74gP!eYhsx6mAUH#xw9txDhUV27U&08?J^|qh8@ka5XpuPlGGLskm?m4^gk-W_UB|txtW8$ug-?{GQl8SQz`{dOrUH9}eFG-;77#;qZO9@Qb)?^WpXIi}1U+@JG08KQ6{mT(<8N<6JzK8ik*XeeNW?lX``-;XC2s_#`+Rj^NM1li(NeHSlxrdR%x1zJt1jSHe5sDE=h863)fP;g7?2;=)7lA=E2;7d!->gg*=41wV%iuf|tXx9|t>YIp}O{3iY;^%{O0f1DbH$KsE{<M6@oSa=9N0UiwBg+BvNfS<+Rf}ep`<HFnUZPYFN2D}Y^6Musm-(>qZJRW}n9*Yl!$HRm1yWyem1pJ@y-S9KG@Z0#?)NOb>zMXo7SHRohH}DnI_y*g@;EDKC@OXR}JP{s>PlkuVcjLm(<IhvK;kEc$>K6VGUJGx>g;(LLsCzs0tsr}f8pZF$=fM;45%9h6FnkI;0-lV|ho`{L;~U`l@LGH)yaE0YUkC4mSK;&Eb?{U8{rDpIUi=pLes}~v6}|<Yf)~J3;raMRxB%XOe*$lWcjCgE@J-aalls<?Euu#82k@8S`|(@h2jE-qY4EM^RJ;(L1{dJ(!G-Wf{8RWn_!GQuucQ)bCI8d^s`vL#BuV~T{D0ij|I&SJR{USS66?#pMC;otS?+^kHxnh|4~h%qEsghYEq(P$'

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
