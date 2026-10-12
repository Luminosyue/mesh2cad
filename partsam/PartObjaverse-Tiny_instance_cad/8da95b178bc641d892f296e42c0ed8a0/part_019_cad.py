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

PART_NAME = 'part_019'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8da95b178bc641d892f296e42c0ed8a0/part_019.stl', 'relative_path': '8da95b178bc641d892f296e42c0ed8a0/part_019.stl', 'source_sha256': '9c1ad1a164e9076d715a7744fc3478af54a817f77ea93d7e87a965ea4be1c459', 'input_faces': 416, 'input_vertices': 236, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.06409922242164612, 0.13625618815422058, -0.3097637891769409], [0.36479079723358154, 0.47584646940231323, 0.30899474024772644]]}
GEOMETRY_BASE85 = 'c$}r034Bf0zQ;E)s~U=4rNmQ0xhRTjs9h9|SJco-Q87eGTr^45Si2f(>@87KiI|6)TVoq%ONb#s2x6!>hSFQN_ftOa-ny@S?K^AzzbiTC<h;-4ecnqy|Ng%Fdsg;dXYIAu-q|00dWMy#YROMs>t2N;8&a!VmZ~SLs@BAq_{1?IViKB;n=rYURY`mGV=}qdfY<s&6|*K<QzJ&kB#elUXcr#QVN~0QCgBmI#>Xed4;wdheEi55<+}|Vn-Jsk38RNii1BSVY|*lHlkk>}nuJde|3Che^L4>FJ9@Xrm(lCypY5c!8|UVF{JeL)c<-XjT$NVR%ALxG|2kLN&pNN$8=v}L;=K=!N&EP++S|ugoY(E$5*Ivv-a0Pcig+wprQvqn{^4?I|4f*)$6JrYhxh+k+Gpf#)BfAYi@N<{&pD5uckuSmP3Ls`=NfO-``^`5d+R?BN_)I({E0Qv{@RW$+NVB!S#S4SpY8GU&RX$qoq5^%^AgoI>(9?tm-eMor9IxkJGrx^{oHw*^!{V+=4t=b$EQ4g-X101_Wt>lZh!l?4Z3}eTiRRWW=VUz{miYv_K!c;-WvSjRlWUt?M#oKckp&r$xQuu-LUm~{}n%w_7$Fy_ISGzenxR=KYGVHy`TDZuIv8qU!AUf{fgRqv!?0!V0S+y^8_D#M!f5!$vo*Yf35y}_9A^=?U}!x_xO1iZ+-KV<l_q3JEdys<Jz^C$#M68wnq2U?Jx6T-x4{$c<U&B=2SVqOS?(?zT0l-?caLu)!95MMYrEqF<)=b?!8WDcHC;+pRS4Gtxwv>{!6dYerFXq@0}K8`+H}Xc)NUpocFGSKi8i}Z<OQC>?Frcf3#BOZ#mh2|ITt;d#?7*;|YPsoild1?*Hl>nLl-Bp7QrD-dYkX^P%r=$$CFO#_99uq?C~Ji?{xcuk_<_-QHXBFWSeIlJmQ8yo__=M@jm)^9BX>r|qE+^!~3ulJ8ag-ddeGtrK;BqUMU9c5jc)@Bwe=-?RDz?#C(jjvlWocW-b$)`#@b{~_a3CT^PU-|orc7e18ntW@~}J<oc)61e|qC+6wxEqT)Z`}=D{`n_|d|82V@%k>;9{+E4wJfVE@NAkVOEnBAh+4;&fy`5ApLucp6723CI8rYxPX{&TU_Y@2C_uA>>JBi=O{;gSSL;B1H($8ai^?100yUKOCy@Q-zygfv``+hySeivj)`#VcyKMSs=dP4cWQ&V+r%h{-p`&Fd)%Kc;<g8kNT8HYF9Z<gyjLj2jU^nIm>-#cr!%$Jp0bxztX^LEVuna_9!@5FVG`Rp9ouD35Q`!-<Qk_PV5+ugRx_(yg>>hB%AUA^g1y`51_j{j3<+0UO^>3$aRwMxo%|BjLaJBa^br_9e_zq`+Rz5mEHG9RDZcu8+(d9yrz-oabTPh{zQF!X>P|I0bj|2w}N_V{@#4}T*2u>SovBc%P-^Wy(Da)&3BXMBqIy`^^OjM}Tcon1@TfeXnQ9zXBkt&}M;pWC-SD97t0>+<=Z4tYZP*1vD?_qOrY!ZxA(+6|pT`2$A}1^9Eb#lLdtpeK|MI<8}U&~XcW;BgCl<4p$xj(fabZm93;7$4M6w{`d2Q2n&p;Dh#Wm7OKN!^TaXP(G;t1%86PDWLx;r7wl-r}07kag7h^Pk|5mUe5TL;<t6(;tA!0$JzKv_cjOY|C?x;huwn4Ck_AhtJ_0*bG--q1`odI6w2RN7x=x_Y!-hZXx^r74!Dkr_~7FjZ?2<YAA3Z`t;aa=8&=5q`d8dpkDqt&PF#O^zTQ+^ey?;w!1ZOkZ9M12c(-rI+)(YUejRf|wGW;r1^Wp)?*;pL_)@^Q74*mW{mhfEYe+^;(cWn>#P#@j2XFt@#nszAUzYafdQbmO&xazO>)QC>^`xkm>$-^FykEwB&TQ$=^^u(4Gaiqhca6Wh+N1NzU|DyQPX(?^c(>W;+>k!_I(lxO-k(!{k=)m!yvIF$-o;zlC-w7~bHdi+<gQK6(c3Si<aqqNy-vKfe35+K^nLM3KU~q<-P)&n{Jev=57yJqb#{%_+FSi^Nc&&Y^nKHK8*iQ5pzoVji45(dkA~^zT6;<zdCtds)5Tl2s_5~s|GrC(GdeaeU>vH~l>5nroq7KA(0JQ;+S}CzYVQueEWX+A`u=FVH3EN9?vM7@QQA8%<^}BEc-MIL@6H%@Ot)V&NW4|^n8(k%cqhA<-nM5?m-ahem-fe&>-(nhuJNDFkni((ZF&B(+sgAmqm?H-e%`@bt7e{%`SVae@3_yexERpSFQZQDd?){+|MxQ98l4}|-n)0H_D)u*Oa9|#ylXt;<{h|P+6S!<#s|-5_egpD{NkAYlu6R_*?7|*cgk2jpTpbNlJ@8Fq<sTRw>RF!yN~Y4IBpm&^J&n{3p)SRPd^_T@8DgY58bNA&uIUT<^k)W@viY^UfE&#??U@P!+`e2JI0&!u$f2N2R#oMAN)Mvbog0&cU|RN|M558T90S^-Cwfxb!?k;#`GUwWc~U5n)YsNw2V)sALaQUZ^wyuXI_%|*E3(*KO7?MZ^uY`y!}YL+rL+)^y88oFX(<`eDM9q8`n(s8?>Gm@vP^@2e0Qvy{zX&JnOmDJYM_oDfi_(c$=U0`1`5i?S3`nItfb%?2lQ0g1vd3#20yvE#i5e4EE-H-T6ZNYtNqdpAW`6#xozR{o4cEoBrSn+ME6q@!SW$FQMmI^!|DJI&s$gtlyIupLzg4Hecpzt0nq6_m)l9&m~q)WqA*U4=;!3xJ7)*m-_D@xAbS)r|!xS|9H9nzQ%{|#xEWv^Zy#{>mQWop+>o~p5UV!h`0ZFNUtaE{WIdTrv>gm*qi?2Q;j$M5B8@2c(3uMp9{}P|2w}c{jAYfUq=PLi+FoMJAECcHaVc*2Zg8I)a$$B`G<aAWPJ1ye9L^juBFy!sP7-)4>!yGt;|35ec5;~-kF*&f6snBP<uCTg50NLC(HZFU~esG<L|x3r&it4sZYS$?IzBuUo5rhtFpfTjT+|nYTGjH$k4C0$F%xiz1nW|!vFi#_E)|>eB-NhavGct52O?iCqICP!(&JX9s|Ee&V=8C*N~sXYvAqV7I-^+klYU+gtN$WIGw&`k+Wfy$KWhD+gIa#HQHC>$ammz@SiEgqbS8gDaFy`Xm}7gj8Ys!j)r64IC4B32PaaB6DY;;<T!X7{fnm*ze_2eKq-zTN5Qf1NJ{Y#O7Yv|Q21^5EixK5-}x;{@mz8qJQqGeo`lbm=g5=rW?!xJ)hhBMc%iR8@l~3yw)*OTulA8?a2jp)u^*LxAwPjXBxjJHz%$_K<U)8loI$3+X&gI)Iza!=!H3AL@F92yxeDF^r;;DRsqkd-LwGVgmYe~Pg-4Ln;Sum)G6T+_uY<{x@JY_oU~&+wau}>K1|AHLAmjXw8%MuXCi?X=k?)~0!S8!1o<zpOli>F$#S_VQ;fe5j<OHj5%~3ptjI|2aD8<9ckyhcFrg$JZ#420^6-SY8!z$l`qu@E@Tv+7^cn+Lt6<!0G<QX^<K2B!CDv!Y`XT!(gkI8}XK>GACIR~D@F%*C1s|~(dMk!9A6o28XugN{+26zv=j{FQ>2QQ)&zey>cMJ|J9!3)R~SY=;W<-fxV;8!TcFH?$pk$vG_@BmBZNk2>Gk;?v7;k;5ji5y@R&OODG$-Y+MTveP(rdWm7tl}Ny7gpgluK1AOn3^>~vAX`$eNf%=wo!@?lLz6$a1NOT=fD@pZ1@74OP+yq;fv&1_#%9sJO`hnpXVvXN69_#QFs@*4pzAc-UV;+RUfiDxd>MICfprX&su*XBgr>mm9yYTxC^-eR{09t1@1_`40nXvQHtA>z2Nq64{`vkvOnAdevRx0_at8@`@t$F!Ybc`Ux!zdYhabz;MMSY@-Vy}-c9DfM@W~<fxjiMkvZ@+IFGyltIUP-;475ktK>yk<$3rje4RWBUx#l{iaq2mSmh?z1Aj>=o@y1&t*MmaI+Wt)D8-G)?y$;Ea3i>}RXG0|Q;M5Viknf2TauA*OSmoB1#SzsCOg8d;Z|fjxE0)iY!7#UZL$Zf@-^7ZKbunAm3$rU3eP83!}H;#<a&51yp~eDliUrPIk%Hiyph}sZ-jf3Q{dikJ+d}j4}OwTtp1HoDY7P68?Fg2Ca1uQ;Zx*Z_!NAHJOZn9VU^#)ci?>T8k`T`B=g{#u$R07d*NH;RrnTso4gL+hVPO$V3i(N<(KeX_%t~cJ`E?6b>L*Umaj^a<;gm5dAK6^99$88ifja{Yz#jIKTS4)pN5~M6xS!4!S&$=l;WmjOSmcAf@}+`Yz?=7o0F~J=J1PT2lz#}Gik#ryTYB}Byv8S1TP_%!YbFoOW;q*ov_M{@TYJ$vNzlfZb;UH8^Tq{C*dk^B}(xVWI6Z=xQtbJjg_Gkm!K4zAH~JVns9Nr2Duon0WT*{!OP)Gl;ZEmJMee#eKH@u5C4_C3I7%Tf%L*EZ^1vn56Ii_1NeLLF8n=wk30?EgD;cG@MU-fSqokPKSL=FvkI@hFiLSTN^wa_aapoFTo$fCR)j0SmC2`Il~2Q!;cDcwa5eZ3l;Uu*J{%6$B^$tX;eVqPN03e72>6d=3s_}y_>b@l<cshNa2v8S+y;J?OoCs9-yoO3DnEtafL|iJ!7stjlMP{&Rp960>SQHYWmULO&tk=^hW$_fG`8@^Q71g$AIb**X5ec_|KH5_?W^D=WS^cT^|e~u_n-PhxrSPKt^Wo!KOip'

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
