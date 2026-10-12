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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/891c88fa5ed0452aa5e77e2e98a00531/part_009.stl', 'relative_path': '891c88fa5ed0452aa5e77e2e98a00531/part_009.stl', 'source_sha256': '2e79b46c1a98a6e2117c15b119e629d8b7f22c55f8188fd05ac02bc715cc55ba', 'input_faces': 390, 'input_vertices': 299, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3458224833011627, -0.46056896448135376, -0.349764347076416], [-0.17530708014965057, -0.11396554112434387, 0.2790190279483795]]}
GEOMETRY_BASE85 = 'c$}r033N`^7RT>Rs41#Q(U?9}LZ7M%S`;6T^r;$ZYH7+xBZeAds3G*DiYlt8p@ybtd1{EMsOb|CAreDHL#U`nUyY@-I;eN|Isbd^IeWdg)?4pot+V#;|G)e0oO{2U?0Zhqp-p&!NK1ZIu~uw6-)33`%c2osMOvf!B#!9+MxWue2M--%TaO5zzT7ysU6-~Uy4lt!Yg}}EpW$yLMmO?BKcDbibS+<W!jQxfiM<B*9FiE{hy2)H1Bdr<{Neq24ejIT8g&~stmTWTS<5%x_dk9Wb*7Mfr^>0lG?%<ZXDRxN6+hZc^L-zl&Z8K5>!Rr|EFpZ~3(b$|e)2*884+_wntsJmrzr-i%r^Y|MH_O(@doc1e(3u3Z$$pV0frx(RZsZIsWr{~hk_#dZ%jAl8Mu?3BmC*JvkiYhRq02>Wf^|vgp*=kf85SAt~cYt*W&ox_`|yIU(#Cm`My;d#&uoVazf-c%S<=wL`4fff9aVtqs~jqkBiUYz?oFtw+dAielR*WWZZ}Q$;ZU;AGYr{=HLHu;U|x~w8O|B5O-Ag$0NTq{J_*~asRHxZZhW6byJo&o_B1mai33qcSO`_k+RaL(=S5$oyIIQ=F{WZOyN&W8E4#w+kwNvuR3eWUfo~(&LL4R{LWI{4@4};5IQV;wUIw}#X&LOIek-fKe_N{>Ed|34O@)-r&11x*!I?T!_QnV{9x3C-A0|ZS!v?Bf8Q1|^2_WIey~doGrx1V@O@WOQgz>|&~Cq|^Zuu4hJSIP%$qwgUHAR3=j{{6OUGsCe(;Iv!q1O-{;*MJ-vlu~-@Teg3_oSK^rLR&7=GJ}dqtf!)v}HHZJG$*-?*2N9~^mhk2o*2)G?z@!E(Y6Y}|U%@VoyZ?u&m)+2cl?+X=$Aa>|`B{Mzxt4<+6B+VFF02|rk>gz!T<M#_1W$P=HJwJdh8?gu8#6TUyZdC2fr6cB#?mihaPI@W<S`Ey@CRrh_rw2+_E_G$YK|6F1DJQS^#ru+W588R<s<N@6euIwcI!2M$BMt;we@^f$8<)H4n&x3Ep6~hlLeN6b)&ZiF<`Iqy>^(0SDH~dihH|2AZS|Zc<zIz(T=W6pB!w=ri7WXSZ@3$jHo$bqoAMCt1%gApvU*?}*kYo5s9fj||GQjZtMPlX8&#a%bjr!9n2tQD0!BOM7ZXOk%YalwpsAJ`PB%j+!V~-jBxnc4-h&grAn9rrQvQCvFW`3jd;<*i_^fvS3j|<;le9Unp{~xP_@7r6|%ztgUtn=F;Gr!L3^5<pU&=ZC~u)F+u`CzH>JO}5$B<ok(W9FY|E$f86BJ*GCE&V^k&WZfWi$ouEeczRJqK_x{$~OG`m9?cmrsQ$m50yV9`gs0=hKBD;=_vd_&B2DB-1`^V-&@Z#{kp@1?>oQ2@B=TD6@LEckeUDF+|zQN$ISVZX)681JhRS_-QqnVus+wUv%A0WebY`Fe*Ur>;yuBax6iDzajAT-n4Mx??~dy7y<*`Ev(5*(vY#jSGxLWe;QghJS$}7F*&kYjne*(iR>mK<8=s36hvQS<W}oA)^7m=)%I4=7w^{i9m~BUm?;B_*pUbT|*}5NG6Cv|IX<+(QzYx!p|3T9%V?Of+$>;3a%p*pAY$^GkGj3F-?)&@Y$oH8+n-3fFOd2QOf0j)<WYmvrA@eKj$S{2Cy7>7Cj1C?&?!$u3!q30-S-NpQ@AZ;?R^Wg!pF_2!A2}(_@L#?l-<KLT+HcgapCbHV#qO!b_0~<0`Tff5GxEb@Wd5S2AtV1x)=_zVf9^J(=W%_dU$W;e!*6s-_FcTEsd=_f625PA>~^F6#e3rSuP^D`R-;a(71D3ge2d{PtuB23oueC#``q}1{QX|OYKoD6x1)S-$bIGu<9hEtkneBZK3`?r|EuF=|5(|5x$(JAt10|ok;J7&{)N@zeI@kMn{y1mLMQni^Yrw0jqh9fxaeoe59YMotLGmWDf`^!@)LDGzuRs3p44jCJl*$Qo+JEV-<C^^{FS!wLvzorFzOdwCi-r&owCaClL`nw7!kA1@VhOReLZSWis5J4(jQ-Lv*E`s5bp=c?_J(v%qQxBd~b}OvCWwOu7%QH`^pZZ4&F198{XY1er}51lJCJkj}d(#xl*k7z2W-2U${Q+7p~9yh3oTvq3W=H;rhH^D4+EU*XR90<+FaF=EM4hs>Aw)s>Aw)x?a{VR2|kY)b+A{q3W=Hq4HV3Q1w~AQ1fK{LVb>`UwEIR*)P<5Siex;m-P$R=lw$YtY4`4uzsQPS-()vC+in#o~&P}`mA3lpY;oMA6UOo_mlMtH6PY5l+XHws?Yj`x?a{VR6gq$DxdWW^*pnFp?uaa)I3?gQ1w~AP<2?pP(JGy>OQl6q4HV3P}j@)g}VQ&U#QQW^$V5H`i1gYzfj+o^$V5H`i1(wtY4@)tY3J)56ym|>a%{KeAX|N&-#V(S-(&|>lbQ1tY4`4vworKuzumYmLYw%j&^;%j#fTfN2@w)9qsyj9j$z}j&^;%j&^;%j#l|>9qsyj9qsyj9j)@&I$HUO6NMkVUg(rjhpn&GeAxP0<xh#0`FAho7}v$t-7250yH!40cPpQ*yVZQyx?9y}>uz<uY~8JVw(eFwTX(DZuywb}XX|d2&(_^4pRK!9K3jLIe75dZK3jLII&9so^4YpOFlwm$`P|r6yhnwKhspj3pYNZ$KHooAKHEQceZGILe71k?`h5Rf&6Dk)yFTAPSNUxJ-1YhXx$@cmx$@cmxw>AqfA0Ex|6E-c+do%z*#5by!}ibB=fd{S)qP<5=W70J|6Jv>{d48B{c|-RwtuefGuuB`b=dy7nh)DQSNDPKpDUm3pQ}1-|6Jv>{d4uavHf$E&-Txi&-Tw%9kze2^4b2m%4hrM>T_iK=gMdM=j#5m{d47CnkoJ1y-(>r-&a@l*}l5+*}l5+*}l4}&-T@o&-T?-9k#Eoe73Ky>acxv<+FWt<?H+E9gM$XE^IlcSw<<#qEW<(v=Vx0f5Ie_zTEil|Ag7U-hcHc%$SCC{@*`gK5jcL!kNbfjLMEC?|X+^SduB$1lNTBSB$^l81X-$DL!FKrbzmG45~riRfl77Jl67ZiT?&o@hOe3LsP77dwdo8DryklbofR1FXB9xUxKDsN8?-26l>ZZ--N!28pL-TZV$gb&U4Qp{W8WgI7a+4G{q-v$rMT7!Jr!C-F3JFj(4!U+-Kmo!+09Uh<}2nSi|=CF7#d0AinKzTlj5pp37~ZDc08bM`()Cw#T=jZ=(kB4ToF9Z;kU@egT?dEsd{1Q><o7rbzk*2Gt<%io>mNyp`qU61Rk=_@u@^KvS%0dwd1@3ThBvcDOnG<~Yw~KQzS}8ef8@SjG1EGW2ECAin5uGx*JLp36<4DMoAj9W+Is?eRtEi>N`I?{E|NO>mxj4(aDHs^b{(d1#82Y{?W!=VMR}^1gMrF^)I3yxi*W8(~z#G2(O36f4>ue+&IBY7n1wxFP(8IL|$Y^m7<b;23cpG{p+GWQwHEVo(k8&N%!mjz4R8xx@{iDOT0^G&IHXw#R3n&!7fzuEX`=*T;G8Ii%}hRKYRgZ=fkYW=p0>Iv0a#kax=A7#xqWyj<eC&=h?d=Ri{|XG^9?`V<D$Aa9PtC!O&)VwCOi*U%Kp+8%!hO|i1ZbD-y-9`S5voB*FduFJ=vDVDK4{s5X{C5>l8&qh7sS<W~HK89SEk3v&?)b@BLG{uS<&w`$Xdc-rFkqyp9uFF}_6eDeq--o7HLE{<FGf<Csx-*V|k096OOlXRwZI9oBrdVF%>Cn?rk9e9h4ucOP*X2Xd6ieBXOF>V?h{Ca{s1=1+9z4Yv8Q=`$x_l6tVoBTMccCdhrtuW$DX2$0*%|5JbmY2x0Gi?>w#V;4Q!J<PWa!DLM?A?HY2Y;Ey1XBnVhP*hiO>|wYCH*g66z5LoskMoMXt;Hpea6Vd;B&u#WETPp@XPLJi!?ua0t0B?}esV-1c}pG{r|Xo&Y@o^@x+4u?M^dxi0U9rWj#+JPw*-q{d0mNvKCW))~9NyO8VhPH2k7Y>&r4Q!K6VSm?2+M?BgYUxB|uuFE^1DHgRoehZpnDUC-%k48P>QO?*7-i}<Cw?R`ZVtYIinqo<fM?sH5J>n70_!9gja$VjEO|h`;@o;F0k7zssdIahbCpu#bcnfk}-V9B#knQm>Xo@8?PJ~WGJ>sFx*aY5$T$eXOQ+&wwcnCDbhczAwJrwnb2RkDLoPu1JH$YP?XnQ;enqqN{2SX1=J>r4RSPx#0T$k5DQ!HS6{3bNT2#p6q4@5oU0nS(pUW;6pzksF~ZhPDxnqo1H2S5)%J>q`OSOZ>zT$le2O)<>&xGyxtq8j&u?uUBB3C>szUX5IrS3y&>ZIAmvQ!Ju!0(1iE5yv~@bMWWLb@?-Bik9v18_*OBYa9<9k9x$tov{+U61gs~fTs9B<6h7d3u)XNx;N?(2b{4Syd1eMe+o_UPmOy*Q+!C{0CWH~h<jM{HwDSb$aVP>Xo~kWejS=(L5+Jr_dpHeIA<&aFGH@&OQ9+Lq48_b6bon^2OWnR#NC~-1iS>fE-!|r_`Am4pecrH+#R|*Y7oEbjE}(|BiB8L^dgMk;1Rz9O)(4{2K_2VIJ~aTSO{LI<q|J|rueJIU7#u28h3^6iW<b7oiQIgAGt1n1Woat#+{%kS{iqT?u;7lS4U^e!?*{JcrG->U%(yO*kO_3|LI@(y|1A72Kqnt^E1uuGyTkTr<U4G>(HhkJ&Vo_2@_4`5baV}{{niFMu7'

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
