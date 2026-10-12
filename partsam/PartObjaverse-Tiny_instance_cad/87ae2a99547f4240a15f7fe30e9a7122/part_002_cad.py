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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/87ae2a99547f4240a15f7fe30e9a7122/part_002.stl', 'relative_path': '87ae2a99547f4240a15f7fe30e9a7122/part_002.stl', 'source_sha256': '6fc5ddf99167ff67a16accd77038e06dc01ed42d3fb6a4719dd62a3f5cdd04ef', 'input_faces': 272, 'input_vertices': 182, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.052947044372558594, -0.4038293957710266, 0.306447833776474], [0.0411340668797493, -0.3285467326641083, 0.37237846851348877]]}
GEOMETRY_BASE85 = 'c$}qK3shBQ7CwSvz5*4=e050$ANW8GNmH(ZC?JXmYQDIl_!bRR475(5h@plL<e|b5#TSB#nv-LC)s>a+CuWx2N;4`epCh)iIcI+#GpAWIYt5RuYwfka{q6nlfB*ac&wnnLh%o1x?g~DhN@#dupR9(8Vn}_(U6~)3Fn8L-xWvx!bKb0>xCw83s`Z*7(cuxV*HGpwDc+Of5+^2j_p*4uHre0X$KpMCcEa3*3Gp$r6DGwOeDH*siE%ogICa9DINfgN>)*}C(!ITpWs&87{M0pSa5OJDYN#W{*9@&Scv=ylYjs{@;qCqNgtwM1x@Pd!t2sLjTj|$Icy-)O#P@wicw3aS@Q$h&#6N2&yy}u&A$hX*O1$;RuRA2q{Mo|W>iQyn=V<UrZo)fa(vkmbKjF0tl~<*%`ijIWk<+#twq@f7sIzO1#48hj-6pn2AK`6{7J(1`MR?1=jo{Z`kvyu)E#VzOMUr0|T!DEnrU|d@C>LJ!Ndljlfc(l~)PH9f_@={=fA{agD;Wn+=iSe@3Ln!;c(sm?#M>(m3vWFhi~e{nk$A^BPvMn_>zFrvDEgCFPk2Y<H^SR&UD40n;9`m2lZpB_IAPwL0b68z*{8Bzdj|Sr?SE#o*xupT_cZj!+V-^Y>ZnreZ~d#1$3A@s;vb!sI<--eh;Q8$@%9E1Z@G*0TF$u$Z#|0o?W6tCpA+8{N&W2xp>H2`L?1rM1%EIB{aKAZsM#?^=6$jFG{L&+bQ0bk@B{eh2*gkE+$4PYS)9Z9KV#p2Zz{Yk@)*|Tk$`or{ZupWujAASiMON{2(P9Nlz64;64v|UQsM2{J~(gLQJB{WeD%IK0%l{q7hV)z>3>w#Wslt|yv=g2Q1b81!#Tg!7JVzwgtwi;Ik65{h<Psz7hZ8{h;#MRL#!*_zFzX!ZU}GjcSZf<KNQ~9YX;WasT=zI*$3d=e?xz62cn)<Lxs229FBS4`0=XDTlqz<#QQ!*{h8UqtF1p5-d>S{eXoBI{P_yut*3uS-_Cpt{=&zIPqbsbD>6{$^CuCXIvVHj<SwkM^$EoHdxAR0A4MOMmI<#;;yL*uN%Gs{lMsK~59exJ4Eq1G59+Ucfajw7C5g99{c)Yt9p4=B1u4Q?a&8E3cl?NRb(7CmTlZD6p63@LerOox-Q7@lOQ?eLFnkKu``8WqceuwCuZf6vaz&onsknbeW(e;%R8M$y$20WvdM@(J`y)&0xlkeXC>^Zm&)6#AtsWh)?>CoWy<;8;uZ(#geNH+cyyM|L#QQ~|PRr-$|Gl3P@Afy`4?XVUJXB3dH}^-$Pri!t7M5=AkNRB~%)9!Nv_JLP`6AZ!dZ#q=ekptABTqM%H1mF0+Kfk@@hPe1^QLxPi#)@Ugtr#ryxA%apr1SD2yaiqd9$uNiM|C!39pR8d9wv9#XfEi7hVg+c~fVU2(R@D#=JkH4{D1e=+C&v$>!(6aitRZx3qjy@&w_zvnDsd^VPGS@D3+DcaB(`AN4I4;jP6_QKxHv>|^-XV`bjd9;h>K1p2c$C{V`xe1-dSQ4n~yjs2y*z(eTU%IV-2RJ4)#efyx#t!`Wqe#w#HvW|cd>~A#Ax$;e?ky6)td>%_G5&x?9D9K~Lg7bEVd`|Kt;ct2%{`C)$=aZDFvOhhpV_juDCmkD26aCTv%scBT>j@OzG3f)zZ@r(6c+Vblq@D~7_l#==_%chP?9bm$;(jPX9yRh#lJMRA!T<0b;=TMA1ep4!1@6SWzwJzx{m<x*b5*hm{JIOmt974zCh>`#ktgQt+oHd{jPthjHqKjUZ&l(`&Pu!^vt07n3uA=0C6wd+n7u)G>y)MMh#rCWi{)4e?$yv8!aJ5FUza{SeTH>au1=Hv%I}JKhn6Cbf7oKtQ9~tO)iO~3m*6e;f5Y>b@;UM^%1Af&+3q-n_+PgQuX*gme%(cW`{DAXlII5($*(=ZJ#St0i}1D+Y1o&E4{`o)Ib}$EA3NgnzCiw!*OrN{Q-J;biuYmPqD;wmY=y)t*KO!$`DemwcU$7#>r)HQX=au1mcU(D@4-~$zcqU~>S}`XA5(_<H$M_y=};v5VhNuLzU0bEbN}sY8e&~bZoMb-K0S<iFFNCS&uW$>{!)BjwO1aJJeDwD;kEmoQjg<cf8lKzD-b{OGw@|iabM+Z1mE`;JV)!ZaIO}fSS58e!@euwA*l0{v#YSa-iVI~MgDMYweU}#;(LYK1n;jy`-NBEorm)rzD;;-&L!dPp4;*LFgZx_IASB$NPMF;crQ0SBfJ)S6?}|4^4R-fy-zBISGGOEbJ2Yt)}<a^EAbU6xc6pw;l1f`QFyImU(}g*67vqc1O6vh$zvP07x`}mWQ%{n0_1tcihAy62(RQXL_cdULjHOA!mG#I<6Ko;xh&&rofBU3-iCRdk0Jk-$H+77IQrZ>0R5SfxlZ^ySyGQRV+rCzi-os(<>B7=^_=9_qR$9l{T{c@If8vTwJJyWQ>l{Q{&F1Z@3A`v=dL#T+2YJ)JSX?Tf6y55UyVb2XZKw3KiG|XdocUop^5NXJoeYF9YlOTKk)VyIJa&+v95{-$YYDg{hW9n{n>giPx=<+A?vm0H$(g}&wPo$Stj+^YW#-$Z3YUjMxT;+<<V61|AzZ|seeAcSE$d{^0_Dk?-hxApq?M{zf&f>c6u+K(+dyKhb?=+pDaZG8{EY?@jrw-9kB1(*Coh*y!8g*lYDW1`qsiZ%)JfXsSWD?$c}w+Yq3$r9n8f!Irazm#{-48Z)lADJywi*LSHD5^AJ=6bq@R;eJC9Pe#m0v`AZ?<dp9VQ{=7d4_xy<msIzsf@Y-2?|FK=$An~>($Awph;k~BTJ%{_eNjpvW)X~V(r%2+}IyT|8^||2lJ`&!(>HAHhXEnz?Uv(9EhJ_bNKfZUt`5$#l;+3e$!fQ{{Q2(3@xMv<NLHy|goHuJB@{GMCy!z!l^k?2p%=_T7@ODc+>S_55b-sTKeB52+uRM$Vf&QCC_r~`nOCs(8#cPD{n(Hm(&%S{=^S24Fgbc>>70h|ZofqCVxDM9)R~za)@3%$xstkUwi^O}=D+2ttb8$}o7!AJgqVP(&1N$;y6!N6I7EAn%V9a|o`bt2=pMK5h{j%S8)&|BA)!$}{yE1u#>8Binl=e~o`=4^A_4u!T%IVhg|Nbdwj9$YyU1n0xG2scc4Ly%IN|#aekD|}O6Lp!aOEmTC#L>i&)KMlpmiAcYisIPm^iQYHz;kt3sLM3!1mbDL<Edjzcs}j<tS^RRQ|V8o&%l#(nW{@X^_#@;#B-?^n(!jpi<oO6$IhgGCVd7Trb~n_qp3#{k0zc(J(YM2@krvCv?JKRk<?>|$8&unsD~4eARa~?K^#pyoH&wp40|=4I+{2{mrz~8sfQ4U69-cdG~uDN4Lyk17#l`^7<~rrqDxm@`celF_azRY4mDvbZ7Xwya;z`?zVsQ`N0&~zw4-iM+>W>lbypMaK)VBTb>-O3^mnGOJ=bik&!4&%u|Kg7bte<<O}jU9b>i4T^bexX!2NX@pi3b2VB$dHe$+uG98No&^#yTk2>l`S8Q4#k?z+52-G}%!;{MbFOt>%YzRWd%W4qAbg+2qnqDwbjdQf*H?m_HF-Q9%S(Qe0F-8t5WejoZea?Qs2UZw6y{3`J))ZI+jpSC}9b>rAz`h)2+aC2Rn>e80_Wnx3OF=0>I27ZaQp<59fV?F5ipwGaybaB?jjrw`w=Q(#ZZc5w0b!pdSuBIGYgZ>)y8Q6H;)X}9TwG*)u=dQ-iv<<A#R+!6~W1pk{Ir^NqW@CLXP&XlN!nvz)9ohzVr|r&MbvU*a{jKOTa0^{p>SCexCbkf_ruH)7wzS)_J}-`KPJeUy3|vo_+PXBRZb;mixCM1f6LzER##}8qwif-h=reF5U0fC8-#gGQ#Px~mQP(!%nzU;&S8evrg*h6~=fX7`>wA&98S#t6ji_Bs_yyW8FqbRGwxPcbeFomFOR+91sn-y%Bvz@Hm~b9#LuU~iW4F@3l|BRS*X4jNyQ%jO?<U?%U2MX;XzyaKVva4Rznne;Yq}KaQc7J$TuQv3`hW@Vq`i~54sh%i`nS+m#x)!3TTZ=-csa2~U1Y*Jv~!rNh-0(p&!W%3n{-*KOCfP4Z9}J+@LRN35@!;tv^SI6M7)yrK3%r!vX{7ob_wUK#+zuDaBntIZzkSP-#+5qv<r0ErppH69kh3F&T71mb}8`=;{CKWas|Ytw2if;aqR}qpq;@vt8oGC<-{4p8f}%_Tg1z0=j*ajmv^b(BYu}SkvhqQSI{<eGO;msJ^kzHGw?gQr0cSdI+u7IaX$4%6V9fc&0HHfb{YN4=rgcQmpEN!P|qfw&AF>_I&A|lpuK>((m8e({j=zs%{3eAi>01I97}AYjx*smXurW+aU7dWe=>arUaiYoUEZc%OdJtb!^z$GKm9BHpC8qDf&J+p>;F3P&wsX=N1oGj{o{|gh_G75eXGCpoTRuA;|;F-9V$XAbp'

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
