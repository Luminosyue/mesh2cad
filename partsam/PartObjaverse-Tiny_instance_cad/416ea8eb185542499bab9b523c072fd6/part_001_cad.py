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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/416ea8eb185542499bab9b523c072fd6/part_001.stl', 'relative_path': '416ea8eb185542499bab9b523c072fd6/part_001.stl', 'source_sha256': '5cccf62bd777d43f2b84fdbd736526a0f0bae88e693ccce71b0eb19251c1f28e', 'input_faces': 392, 'input_vertices': 240, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.24511940777301788, -0.31816551089286804, -0.3049815893173218], [0.24684110283851624, -0.05343107879161835, 0.30293214321136475]]}
GEOMETRY_BASE85 = 'c$}r033L=i8pjI=c%Y~l<q)t@Aj+Z0p>l;50;mK?P{9DgU=lE#Ap`^yutPGSs2t%;h%jJKIRt`%5RPO(xeO*i1Vt1_R8Ud8R##oz-TuD%*K|)M``*6Y@V@u|&A+Rws;jE2s_PNczgAedkblj^-veEHiv~8@ah(Vk(-Tutlj0Mn-ZLqAW({#8`}_x8GVqB3F>y7-bdeU3kT^9yC8Dbl(S6K=5p9i#F_TkLQ$|l3H8~|Ak^H`+CrnMW{i)B4PENFc-_@a0`?f~MyW1MGjQ{cPTDuCq`ksnXTdk8LJ|GooV=E(V2`m^;PQQKdJ%gjSmAd?3`pePVdeZfnyUN_@%|FsgOI^N4`ODHvDZSAtaJ0H|je7q)5|U5ZR~t)RzDjS^ytt9_5nB@uxziit{wgkY`KnywnST^hdMh%5eLs9(bZ`Exd{aGdZtp|<T&Yn9LekIi@Nea-{Cydt4)Ak*+PgF){m3YOe&wtDjm=SI?)2ugGsn5!@XY}Si{1H%eU_{re3eh&+6=CzzjL_kA60H%68DqxgU|JCQn@?5D%Vv0;%OV*<r+;Ib3Z9RSZ-3|qm<rPORVSiYqf>z<++evDEs-BeD*IS7P)=T{JQL$UtQee_5)@u_Wj|lcgXvsZ>4ry$Nr+4C48UCXJBLYt%Hr;cBdCV*IUEse*CyJB>kMPR`c&M4;8r62hzu^;`{RJ?&5aaK6w}Sd&iON`yZaaliT6BX!gaj^||ba#k|Y9F79Nh%lE+#boi6o)p+Di_C?DZ<a0fAH|OK~S7Vvajx5>FA1z`(u<)lGu4hD<>}PMgnQq@dWdzsLpCx_shmw{2dwoZ4PoFo`H-Gts>+ezNJ3hvKU__zc-9F;tjqF?9vbMV0$Cvun3eNw^h289bx0UN@v{}!-s9C`6Z<yD~`kUjHvp>wcm;Je@KYS~49k)XuQ~FlinPr@Qa09MS0PU&#K&<pdN7<g@Xg2$1Nf$Xjdc;?9f5l8+%GYz+?sMm(eE&-6t9*=4nzC;-oW7l}NB&U6{gQnP`{seBT>rrL$7H`x9kPV)AGfL4oxk$^NzzyOTYYP@Zw>MA^O}caE35PUXR>8J4Z~#q1zWkE7TPW7|2b1WFWSwMbts$t!)tbiJTH9zA?d67`06i`{_;9S?sg0MmE#IR+H+MMng0umH;3d8-<l_VmA_~Hh(%mZe4qW?zG@yw=*GTv`hmCjy7Jq+x{%9lKTy6GC$cK5^(#hkx#qcU>|5n`aQhg$zTkc_`?q0V^nO;>KlLN-M{9WcD|}z;e4aP_Xiw#fNtrxuO|+-aKXI;mTzQfPpCI2qp^caQOJ}yZ`%(8*KL(DMWO4pewzF?k9OU{0dThy(<K%O$zwfEvcDa4=L3pvd{eynH;w^69tlx-zv-=h9U-QItUf28=GBf%2f)PCLiFxw5lrP?y&HZkqMe=>hx2`SY@h{Z4y6QgZH`=qq-44nZu{*cBecz7f=E(PVzZ~atV`Y6dW@m6YoANNPM#*v;%wb<V&_vE-*W_|~;ZI}VI+9V~9uHM~H6GSClm2VN<ouk}UA9M`lG&W^>UAOG(0_6m`_`eeo8042Z0I5VGt-OR{j2+`f32drGx>V9CD*$TAC~3zJTQax^xj<|<5~AnfB)}^(!cVye6LeFa61IPpY<&NPP`=3H!Wu0{Ac+zzR#O1--{t#<#WH0pUV0CczUP1Uz9J>atqvkpxKlZ_Ls)-dtns|*<Zg8V&6YLQjXiHd*pn$w&fJgKck$-m4R`ke1C&D9uI*zn6K*Jn#k!#*X8xXxDqY<J%0bwT;9TXInK8omHV+~;~(ei=MC9UKiw()%*;XjyT#9i?&q~qI!E(!sC|x+Ug7qG`<7l;j=KHezGdMR-nZz!IVrs&#K*qKfbUzmSo#^KLf%v5t99Hw^?tG2x8_9_g}g5+{TCeys`IUra-LNATaRZC;pbgm5;C5Z??3me+~=TQlyClI$^Fu~uwu6_Hn-<~2^g_E-T8>!_l5LhFrRPg^LX$KEGlyQR_yT5_h?tdL{2~H&yfD|=Urysx~gSJ|9YB+rE<A%KN`|*{@g*+ShIdEcGpu}d?T%AHRD|QRmS;G3)6d6Gj5fyk6YuB-LraDGycuVXW7@^m%zyR&vW`si}`&NzFu4}pYJUDX6+Us^H>!h^MG-AoW=Pkl=J&;_Sz@gp=a|9S)Wm%?eNE7_RW50<T_Q}UDjv(nmL?L&2b^?l<o)Tu?6R|xL>sS&}#mR^p~{a`iL2?%l;aAg?(}JsF3-sijU{=71r`{{qvud?ecD4sr|yGug%XQVl4Y+MJDHC)Egw9_sQhBT%W{%+&9+o$oVjTyY#hnO8HgRsatQI$9~i+@_qc~Q8|BZ&1K*34P!qL>y_>Q@x3o_dTm_}`r5i|gl%Tu`ms*PI->ik{rz>jyvX&{*K7Ftx@<l5gG{gOPXbTJ&*%HJeTDdKD*O6A#Q1!{Votv?yU^W_RebbgVE;<?^?j7`tL&q?Bxkd)?Z?c_8SLx(H_z|4EMZ^UA6m^GU|-))S_8`1*Y~B$*Y~B?`Ix2rT-v@j=xh64Bl{rx!fO?V^rPmhel#|pTgJY&Zx8y~zFmZMTh8Tb-y^<OKeDfXcbLh)v#)=rh@8h(xW|L4zc>|@!>WCMDPRBoGE1M&<?Gsaod4<<*st>4mv)JL{X5ZfxZNrq7ut8FnVG|WmG4vd`uC}5aV(F0?fX~x`uDGI$*<DazN5`g|6*VN?)Dsha5bmbzw2*$h<*JWz^ohav1;cA=7GOSUpr?oR?d5k+ebT>FiYNKUq8pN<|nUbUpw~@AIxCC$~nn7&+DAOcCKO$m?(Yi9LCpu=qAozJI_(Rex760_40Y1evYJk{TwOiYv)KFZ^zy4a@F~j^7Zp8&-TJncY1YhrhNU}Ea>a!W{c7egye(sI_2x<b>@aqheFchJW%=id0^02&kNsb^eU@<4yk<o9MV7I{-f^n>YP*g`Z=e6b;I}EzB(^8_jt-e^1->Q^7V7qps(5uzUL2bxjP?q-mCm7=e^2DKK}2eZ_Zj-QEfeykMw~xPgF+6gq)sF$Qyh)P~W~}$2B5cj2Z1ZIwzC<lvaOqp492TIy&#zrNjSwbbg;*huwB`f<6e|ZpTA*ybbN;;vV?j3ml2)f%{1x06z%s1nmg!1ila29(*VC4rqJuQag&My`Ve6EA3clM_=d&F!}j*Y=RbnyV}vkj?qvLcp=Id0UZDyZb!5o3!qC}+y{9?BV8YqQH1=8kQec5cEsDU0_?%>5h$xKv@4kEoPfIJ<9QNrtt+@It|uVRjcAwGP|ilwFCOJ}K^@~!w|u0}$2~i7&k8)x3Zxy5x-G@CE=4=2_SlIwQTH!Ey*$X<gZ%T6Pc-TtjXHHjIek#pO0=Wu*93UOkvEm`tQ~9Zh_Rz5v;%_JL=eY9*MfK0vCfWt&@^xwuJ41c1@8kF+A$MlKLd>cKLZ}(s?!i?2k;PZe+2PR<TDdxkj?|I1s6hJ1s8(%LEiwAu6EUVHJ)_`cpdZw@H%iB^f_=EI2M`&PC|WS5kt|&L-8!c!|WJi$6y5UlL+EOJF@M_vLg?g3|?-B&yGb1VlOlgoQL#YXd*Zf`Fo+0!CvqT1o1co@gM|oKj;{6Kk)s~Vc`40Z4tyR5yS>`FxUV$M-aDwJ_&9CZigW53{3=g20x4-9tcea4+M`#5NANMz!~6|5X2jx+29S}EePVh&^+*7updEu6hZtR)CYbKT!tV%0$mP10^W}x-UD3(-UHqW^@6v8-$W3<44naf89W<04xDMnD|Sq=<8eElvLg;U7W_1Hk{!=O=R)Jai=nHaao{-QL%ar>104$<i}G`zuYhyF#}LE^5X9S{nc!{UWeDOq&?(?K;86(TDCk&l6u1q7_;%=1;M>7X5yZDa9|zwCZiFCi2#o_b1UE(yH*vLl69jQH1aWKVByekRZv^p3SD%eU5T_%EbD?v=x!?i>@jI?Qeg{GPK7zOcx(ZwYK7k;v6wWxPL=c}u5Fdx;fRBUAp~t|p?08YgF+3amGIYIg#ys(x(9ObmM~JsVcM0b`BHjZn5zc!@ydV0maNbkmBhW*_d6$XHpofL??i0TUJt&;{f%qu2R5<eq@6Dmb!kKf3_d?$i&b&mt1^T*h<}u<8(D}ld>xf^1TEdwdiPfA*JRUkxICCuVK<E>~nTLrVhCV8sd7HR1w7YQTcH(x>dxf(W5VwHdEu8g&xH&XJIO_|s0c|CmHHf$+^e*A7S;TFj_XuZQBfcNnO*m^GaX;uI!dWYc2SFbb&e}?>)?DHV2x9d<68DBaBAoY^xHYt!aNcp^X3%?tGba!?f!-yYd4sqyw3Tq?8RCY}2;s~{#EqbL3uo>kz72Y>aOOASrqJ%fnGcC?hdwHtIg_{z^a<h2vBXi(iNcwOiAO;#;mq5_YCb1k2AwaQ`JZ?j^mXB^5yS_eZwY5jAwC8z7S6guTn;S-mxGT(4+>|#B0dQ{ES&j`xDt9uICCKJ3Fy1RnKOwipe4eYSBc+;?h?*CO#BXXvvB5W;sWS;;mqyCxzHDdGyfB(LuY|ULMK3Hfk|fzXKWMGc>l(ZFYWjadI9_$_%ie&_%iqs^egZs@Ym2Uz@+EEUxNb(;<L~*;IrV<&=0_*Q^BXfDG1`5p|^r>2G@h$1SY)>Tn~ILg18p+YH%%Z4QL&34X}XL27ie*{S5j!_%raw&`-c0gHJ&}1fK$@LZ^XK!406{;0ECO&>O(@!Pi6Ug0BZ(0}TUT1HKAc6I>I|cNMfYn8w2oLXH>G@4=+s3TG^Ri}oNr5B>)HIpRFpfb>%^=||vCz#l@VgFggMgWdw31`dbb2o48Rd&KmwQ8T>OfBLVb&Ywjc9`YYe^*ck4)!cVR+Ia;J*<$+F=5bTg{zseHI9e^lzX56>2YU'

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
