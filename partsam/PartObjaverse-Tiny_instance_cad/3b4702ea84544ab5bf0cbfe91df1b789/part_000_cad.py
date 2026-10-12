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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3b4702ea84544ab5bf0cbfe91df1b789/part_000.stl', 'relative_path': '3b4702ea84544ab5bf0cbfe91df1b789/part_000.stl', 'source_sha256': '1f3446ddaaaf21fa4505bd8bd95e3dc78d6ce7f1644078a84253d0c4e3dd1ee5', 'input_faces': 280, 'input_vertices': 169, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1590866893529892, -0.20344872772693634, -0.43690165877342224], [0.1590891182422638, 0.18013599514961243, 0.47687870264053345]]}
GEOMETRY_BASE85 = 'c$}q~dr%eE9mf|CU-*pp*02#HK2Q`y@yTKoQACMG&<L`qpn?ItD86+C@fBbA4k%ni#l)%s#cJYXW3?LXXj}h?@7~yUrlV7vj4`&3HQnEDzl(bhH=Rs-o!@*v_seh3IeX68bIxAlV}0uQOXlYtDgR8@Lz9|G5=A4)U&>8$%%43yEvHx3+{Io}Gxq6Y>GrV`<KicKNx9O}pc!d7(;Yzr<)Fdo5kbLnP<pmwz9Tg&CEGD0jr{1;IXP*DpEE0UZkqAEYoC4tg5|Jo!SZtXfBZBwn&5htbm;=MrG2PQs&q&{6lth@Dv^Ds_sOqF^%GS`$#*@DU|-qgW9D~Se}H_&H;jGPpW0pI^46a?M!xhSlk>DG@mJYDwY!ph^{+{~y&S3TAJ&no*YLeSF*Wz{CiZXmpCgrT_?hM3DK6ye|91Q=mmjsz^g}|ovj4tx)?Tk(p0S_m)lSP_a9&pQYA*NJFV4I9i<hp8wE60i=V#cDZo1Z<FLf(9ZPqtrtKHWFqD((Rck{JxHlO1D+*RiseRpnLd5`<;Oup%V;JC<nJx1MSz0#e1mt)vTZb#^k_b%9cr`+PaCtnI^cG2#;K6zQq{>zqJj#TyVKDV>F0sC@L-en%|67>#WcV^Q`?!U)TpL6@`9yRZGb)4yk4z9G{m-17L=~p$m!sR}De4F#HT|dF~ZrD}9^@JpxW&bZ5+1FQIImG3(Nc)nnTi?0LQ@<(SmQ;Eg7v*LG`})bPPSz$4kG|4u*#*0Al`rO7zLhTxi+3+)`%H6uUBT}49=~RmAF}i)-)BrB&oiZ0!9(uX^!7*ieirZCVILQ1OJ#+99%@hK?~L@|%Z`}ex%udaTKVv;e8sDv!ai@cWA%1<^7Xd;%>0oLcs%4+9r^G2g<pNj_4ExqWS{5SfOAEje05gob)MJvE*-S@r}V?CVvqj3g`BVL%VA&H@QCZxvL+tp_7tU*v!5aBZqHHXtTO&yox}4}`|%*JKkDR{JRYv`al8(=t~S5L`3-KF<CNXr9OqZ}z9!!_=@|QR(+qPw6aT^GXipcL{>!K4x;Hn1%Te1Uv+qpnV%A&T{2G^YKhfznAJ+7|%JZaqX{p=%`8wn?_MfkI_ruzF^mXrfSM7ey{1ozQ<}>n@*V%5qR33QPldpGqYUXFBl-TEwa-iO)o_wuKHRr3}{ZQ=Ie&mb3m|xR=A>Z<?d}aQ4kL5VStBX9<D|NoRgU7pc4bKyO?R6e6XW%gQomaySb3HS^<nfZeQn#~T-0&J};U90>eQUnyK08i%^cx@j4fp@amc0MysZ-2-EaCyztAC%z_v5-bkms{&(KW7DdtJ%<n>M%;um7%Zmfo}bs$&JO!|KPWckI68`}()sj{NV;b#>AXGe2{KxnCR~#`}d@mCL?fb)VNC>EBBp+I`hGuZsKka)$?`a`?q3=cU@~lI4s0j^&H{j^)?dccL>NotJ7qzm_kq=X&>8^SjUwmM`{$vNL}x>#N!3diLkr+|Tl)R)vus#zhKB+8*g?+~L<6chR@Teccf5FKy5So>$8DOI)vd<u3c;JXD{&&Fi#!qoKLqEy^_WCr)5r513}olV{`1_TQ;4iu5qgUE7}*{}SJNUMydH?nJ-lIc=eqcq+&8#q~k-Yx4KcEwz_#tv{k~tv~9Xf>O8p!ulrq*7|1o;(93hR=#|r)V+MH!%jcd$ttYpPGt%E;`*<BcFgpJ{X&^?i+$Jc+pzB}zt8)NeB`C+V?WY6yv5}x=Vq00dxiZ=iAyfG&$pWWE`HuY_J#dX?|J#4TR&r;t>t5%brl5ixnA7IMZabr-}AtH53tSyQ;(bL?Sz5~R^ePB`qsHZbyb?aaLy5Z>)cY~3+EisugU*=>m#hfI;J(~S?M-^a88pl<K2AgTqplC!95@6L(#X+hn6p%Cq>`NR~wdA+S_l9uRJ}l%AQ{{?n#?ZaJ@JuyQZb{Iazvkoqh3K?YtAo>$P|emygDozHn|=A8le^yFG&Ep+4~#`_2iE+1JNtZtJk(*NxXjabK`}abK`}abM74qE36dU#IuJ({A(7I_H-^KVzR)HSPaa{=z<gYWd>(!V-!5NqiqvntyKk;``$Zf8M9X_f7qwkIv-_@29SRC9yBQ&uV^ibbGzl`>)<M>=O5<@V>166miL3j`e=+>XdlN>?im4aixAT`)=>=@ov9L%=Y`fuCuXmsSyn%e<?lH_LBse^s&_QPZG2H{-U2GLL++rzduRD8*QLpN5(^&g2#i$LH)twz#l*Z!K4$wEsc2Jh&JGOd`~iB7u_>>3cl|#BGHIX5X6&=XaRi-nh4%)L;|kc1GfG~+8mkyUT4HaT(=vX0PPI!j9lVOBWBPPfu@1igSQ!xjK7VAW`f6pqm4LZ#9<@K5ybnU72y5gGU!2Y8Q2Lu0Cs{)jmR}(x)F;J#3|6JVA42n3V1X$229!yJQ^HkgtrmClKCO6E4}#;dqL}gy}&-u`e4!qU>|TD^x-u0-!$~?jQ`?OUA<8@X{e2t;XCOPa2a?%bQ!pl5p9i#fQ|yEBWEPEH<-qq#(aYjtBja$L?Ltocmr|@Q5KaM4IK-fj{BJkO$H|;XDVVW#wQLO104k(U_=jzmKsyrf!_glg0=;Z#JvoF_5e%B@rJeodxL$UJ;1);y3pR>{phc9^ub~D1L+}fA$S$E99)iTt$tmFaaaYPIKzlpM&v-}frl6|$cPcp_rSxA7-qy^=s>W;h`C10hRy_&zX{%4@W%+^jnK{D&8UAPbRIYZ_0NL72c~w)XyYL8+X&*0&;W1%+S?I25Ih|19R{5VrnNwo%(a1ZA()=KaLIh$NMpf^j7T+N2Xra8wGn-c=nEYKUWjtTp|M~ZUmEWU=uU72_#nzYfbtK(+X3APPC+{sLl;SJ)-+;T=jeH%=Vt*l7o3Y6;xy!KgDwDX1MfsEK)nlaEipY;^nCS$_6PR^hoL`4qfbV|>kI7<u7kewfwq?3tb4??M$)rJpH@&WuorS#p$%<OZd-W$5v@>HE94W?I!J3?eP}q?iSa9gE&+#v!=Veo2QX%(P!&8H_n!hy1=D<r#eK)(o{58uc-II&1aU(IaU*Cqa3gSIXfW6h*K|b?cR>($hc*It2ls?F26x3ZYZ1f+2;zKbcW^#fgZ2ck#Wf`e;(Z9>z0iE{UT`r~1DD{MH3;I>2;w~GUT_|GCA1j42G;~3R-<3v1$TqyfxCf&p)0|`;9dyg<<MgAa&Qq;18;?{fNEe3{YFe@=4>NEpew*DkP`xJ3=RP|fd+$v(Y_`K;-S#x;Gy6wXc0II>_8B2vfaZb1o39*3h-ud4m2B_1I~a(f-}G)5X3{EA>bik8QKI)+8!)}1E5X70pP*Vq2R&b;m|DbaPVxX159&<p0N%H;wWfWa1{6>=vwec;4RP+@D}hK=o;`GumTMN2cd2SLHr>!3LJ&{K7?)oZ$Y`lwEj$%%r&SFcnpF#6+yfdL99Y!!3xTwa^qvYy#0NC?!TPhd^B3T-Tnhwywd%((0=7EqpX^j#Q0cWK4*Iy|L9;bk4_2Fe*g;^Zr%'

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
