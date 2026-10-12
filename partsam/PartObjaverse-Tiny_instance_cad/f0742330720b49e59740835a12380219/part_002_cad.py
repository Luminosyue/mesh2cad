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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f0742330720b49e59740835a12380219/part_002.stl', 'relative_path': 'f0742330720b49e59740835a12380219/part_002.stl', 'source_sha256': '15d767f56dbce13941a5cd20f25b4b4be549e0ad81461ff8542f4ea22c32f1a2', 'input_faces': 408, 'input_vertices': 224, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1941036432981491, -0.09479482471942902, -0.09114803373813629], [0.1308096945285797, -0.008716106414794922, 0.44138699769973755]]}
GEOMETRY_BASE85 = 'c$}r032;^A6~{08W)&fTBFjU8umluDi)iI(0Tl$Ih=>Y#5rPDigapH;@IX<JMKQ<{7GD4%VTZ&J1j5BAvM5-#23coxrnaTFQyrbDwf6h&`+b*t&%2%Jw3#{c|K-p3&OP5b-@SS74XFca)J(GCKW(gO1=X^nO)N{tbykv<myt6mb5urd*9qBEt62>lU;h}*A2f7e>hNk-o;5vrbVlx|oaA1i<om|-Oil?UkIBlJl#@OoEh}eqhW7iVzmS`u{M@nW*%|8h4&A%=ND1B9F(vd$=zsjFuS$rFsyci?*Ro(ru~xgZV&?&mADa26jn2Qfsr32bT0Pf0exvbaUjItXxE~!+yvgg^|H@wH=u!IvuOGp;uKv8)m;a}qmISSj{Uh$n^^tF1%y(WV>WTd&?pq`M^;qBEIM-Q!<+5*ImVIuP*AF*36ZbzFSLEz#YeA{kw-4gC@4wCKhyGgE>6^X3yKlXPA6?O8yD!f_zg_M8K5gjkAm9GtjWS;zeCtxyCa-_xC;Ww{i+p){ET8ZA6`~&F7x?S3?)hbo^E$ELXwSHBCCB$0O<fn*ALGmZ7+?0s%_I8b<`MmozUhyfNA$<|vOjJf(H}RD=#T4*{up2OC(^ty`2NCAxWDid?l1g=`wKte{=!eVzf694f8i(GUnY;dzs!1hf0_Nt`^)&^{<8jl$aa38+Na#9r}q69dV74U_f2uXXv%r7Z`Zu)oCCXm$(LR~*0L&o|7`E=%M<=;bKHMynlF!4JTvZpSL)=6R!@ujKU|5Qv)v6Yc>T!H1M%xtPCf7S?KNxS>qmU!%M(p5cKT)C*3iilx;w8TXurmn`!&AYue)B<X?)oSH;<^(%_I6?d|7|w`L6qdu4{a`K0J5i-k|*&U+&lVa=*rx`*QP(`MUYVzU+$&cQ}6C7uGuU{;jeq$hR)cJLmQ7I{3W?`|`w6^9zIWMDb;wi1Eo2{&~9dT(Mj2b^P!*KUR7D7{1A4{HR&~;4Qv9ks8a^1my|i%RH7@Po7Zdo^3(vjUVgvLxIn~VewYq`hIu${1ATh>x(|$%_G)F@!j=lS2qRCOZsj-_;OyZFZyhJ*-zuk`5Ir&(e*|Djc@uBE^F=Im+9N2?*e^Uk4=AMo`kuWeHowp_V$O0g63s>IWObOc^O~M%U<)|#-Q_Kd|7Ag;IkWo=3;z#{*5o^WqjFx<I8%CFZ&#+v44Hgd6T}$V|;nuj4#iR@#XWu`0`xYRU<a^4yZ@^ZlCcJo>%w@&nx_d=M}!J$6EID#@+$*GQOOb@#VaXFXv@^IWOZU+!vF=#X;+hpKxEy`NqHAJb&;Lo>%w@&ntX+{-Zq>ZV8%~^i4g+m-BLc(P!h!ei~oS*Z6Xdt}ps;eEGa`>le=}>C1ZL^UAGL%*EZ8d|rLsZF|tXjGyql!cTZ!;mdhl`Tm?gKlK=2)@fxf+7WpE@e|HJe!}_3PdNYh3FjYQ_St%P<j$b;CVe*#zC3Tnm*>a$^7&wVd9JQ3AH3J8U%cNlzI?xDeEELQ`11Xpn_s-&bMuS$d)AcJ`y3VTSB)><&l_L9Pd2`Mf9vM&{-)zwcg*nRiPX-FuRn4%{&!(VMc{hl+rJb#pU13Ov*P<IZ?xZ8|JBO)`a>uE{(!vr=icN_K0mgj#K{wGcGl<HH!X5}drB9_k2TDw2%4Ai<-Ck9=jE;!eKx+Fqnk(c+07&7Xnfg!<A(;v;{7@N2Y;QHCdSt<OY-@0F79<(mdE>c^Pl~B#9Z8Zw#<wBe{AOX_SoGAg68G=VqV6V^D=(Iyvl3YLFdQ#vQ9heNjqpR#+T>c_;N1Bm;HD1i+bGrqR-*93One$89(9kAb!H<LHvZzgC@WHJZSQJ&sD1L+uM@a_x>1btWv6|XC+x<(mh|@YE%Ch4gTsjv&Vn+)oqVEdj7v(-9DoCpxZ@g?up(7YyCBRkBYlhJb?ZNegOV0`XJm-MPC*7q4&b~!QBbX-SpVeUg*7WFSrld7k)^^{cs<+7kRYaiQW(E{XR@x{a}-;FZuf7Kg8a{o;t(S-Vc2Q4a52xJ-GfIa5rAtjeOnkHCL$Er{b83<0`&TaTq-YA7hPXedhM6_#FKV{v7@tq4^YfPLbmj{xRY+uKyXiDp-G<wI|4R5<LZ<VvX@naDA;uJoOx*UakA#Ju1pod`OhDH?6zjeehxQQ}{4^9Q{3f96pIw!6)Gp=sEZVd;~oTAA$Fyd*D6PYPgJgwSEAX!@JQ^Sl4r!>uWs&SHb7dv+z0iDEbL}6yAfD!3U^oFZv<87p_3}!6hnoQR4@2DY_Fbg)7mI;Y#>4dJ#SipFuCdXW+BwW%w-o33>?r1TI5M;1X&rqo<|Jzm%FjB`WE6B{gZjpyIrWkI;kgNAM0p^L7>6P#Zl6+whm@dH5o|_>%aTwcF60=*RG7dU1ic<jHlOeCP2mviC!tIuB9%1@tm{2;Rvow-LM8#}2dv-32dHF<-?>6{}Uer(zkp5?;v~%?nh_Q?UXqfLFk42+f7$DI`ZB{z{^N>lct~A?sJOb``l|Xdzt48so3x`dXKI>RC#?THl1{sCZq)T;g^1ru7YYKD-QF4ljdOqZ{GXa17l5$KX}y`|v7wDf%wF6n+z(1J9vW!?USZ>#OkV@EhoBu&!r4*VnoZ-T=Rku7%%+-$fV0@4|D?+3*7DnupGX=fMln`S45?QEGe@ehr-kzXrd9E`i^H*P~nE_3%1$3%m|qi*AP3!i&*-criR1oe9sR*4gw_*S8#f2VM?uMAySbDvDJsLf?WH!7me<Ur{jweH(oXejDC|7Q<WV#U^42YiFRd&?WF@dQn7d@#HEdUorkx_MY#lGoRXv(9LK*Jd0V*AfoK!WppMQg`ZI|Tt%je@hV<ak%4BynXJ+Lw2EOWo=3;R&%-YenzP80MUE`|Okyn8A4{%hSU;Y%<H$7u&4RO7WBhSkU+ZX3J)@~t>r?O$6;G&ml6Zo>X&nj=hcnPIa0WaceF+{9Pe3QZ6X0=ZE<6q%jgEpx!%v|@;33p%IF)*}J_bJl4@Dn`bv-#;U+YA85}b=>!@2M%Gz}gF4?$Dmr>Scg`XoFIeg+*54^%OT8XtonM+d`?!x8j3I0EOO)8QO=B03G82xp^H;cPe!O^4IqRCFLbkXlpesjhDf8iB{aFQGYbo{GsTo<&E%&%*r)%>z_CijG7_z$4))=wx_0y_iBg$J$5H!RT}FRC<v|O!MTLOuotZ)7g8vr_OY0&qJr8>F{7?`6w}nee_2MqJ!Y3DjKM`mC$^<irdg;Xao2L6}42{LTK)2>5u)E)mcRoLUSFo6<h~ygm#2GlBW^ZsK@nhgS()O;Vy7%v<BQ7PF8U<`YW^se7%ZlDw-3T+p(8+?5`cZ=Ic~cS8)@exjottZV$IW>%uMI6ndLNzf<s=(yRLPuMON)MF>qo>%)2v7W=yyZcA-#skbfub-boF`9g3f^hUT7+!Cz`w}d;;s}A(91OD|~w>@45xFy=clcxpOX~F)@byKLz^vKkCEBn@ZJKPm+V_iF=rf-@%qg~+6a4WPm+zRf9Cc_=!TdZqm$eeS{?a;PxJGi-L2F+2^vzqj@I-$8CS{rT%*F}@yx^PppKHL;;fHr{}z|GJ)a5K0b+6b-(H%4p0jbVMyqz<T7J*mcj`mdSSexmw@@%=|l`AYxSg5FnFs9f%sgsB5+=^m(NRd@b?tk6@j{ta?;Z)y'

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
