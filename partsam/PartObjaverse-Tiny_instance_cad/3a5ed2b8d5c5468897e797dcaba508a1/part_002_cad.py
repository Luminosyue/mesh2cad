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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3a5ed2b8d5c5468897e797dcaba508a1/part_002.stl', 'relative_path': '3a5ed2b8d5c5468897e797dcaba508a1/part_002.stl', 'source_sha256': '80bca7e4774b5bb0aa9870efa8358081d7630f1ba04d4a7585bd739bcee48d4b', 'input_faces': 438, 'input_vertices': 267, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.150098979473114, 0.24041748046875, -0.0810670256614685], [0.1587013304233551, 0.24946552515029907, 0.14119969308376312]]}
GEOMETRY_BASE85 = 'c$}r033yc16~|v7gr(TJu!uz+)EdwbWDyY&qXL2v2rgxD8wd#mC?G)u6dVPW3bs`Q1Og6GSwav5k-9Pw1wjgmxC6$mBI1hR0!r_h_dC-!_uYP9zjpY}cmC)9&bjyh?wfb-of``BYi2g^{7*A)`PI+dGp&i|iPiTSc;kx3j4dfFD$N}^dP0VGY?7Cc`kB41=~>V}!yD(_nmxFvv~Wyz$4GXk;ttt4k?i78W5$jdIP%6(V+I!q-)-QC(jvo`4jnkU$i&Utv_CH=(zZoTWK!gR{M0iNVmGzlaFJ*k(PO*#NSi)Y7dd!uVPzU0`?9~E|8vQj^$tD}ePNl4k7xH<>f-a}^_lD9t2>UH?QB1L`XHB{SmCCzE<W+x)`wlZ_uH!%IommM!wP49<<`fOdRKS$$ET>aKMs2*SEcd)Z0z4x@yp5av3c)k<}w!_+xPJtC*PylNN4-)7sQ?X&W1^yk;l9G{FFIqI#Yb+QlCeU&8r@p_s|n+2R$~gdZLZ{`F!bg|GAX5u5$6-(XDBGY<8L7&VUOm);st}?)D`vKJUKX^PKtZN@uxvFXy~#T>W}E>&H9!r#3Hi@sZkZEOPOQ@w+Qse5_TkmC3qo*Zbq}<Kb;df9bhZY5aux{(Y_L_vCs9A9?$nH7-7Sa&Co-uO7B%iHnb&(0ZPWPpr6qmW%hEJ*BTpr`MzFcqiX#??M-!*s@`fi;u6}U+K*MuCqUGLr0{|SFwFrRW3g9>7g`U-|J}8C;joX_{70aDxCZS*-Kn}-iC$qU3}!%(;sy4UfzLkI=kA*JTl3p(~C`9;NoND6U$wEeD}GPE<Um4U~=4I`8WIgx>u9mH=Q4p_s-vy<aHjid7Z~>KFYii%D>#7H$v?*Z-jW}jl5}7eLk`&ZJn}tU8hofmv_?EBb(Rt$mXN0M>g+W;IBs^p7qG)^H`5UdRUJ_?XVu%ysk%~eAc6QVqV&MlxUk#<>I4dN78v+kG3b0-+!Br{jzzri;oZZwZfU-^0!M|eDuE8=ezjow%^Wl@!qO#*-pOYrpZqIPhGaa#YbyDSnkZPd1|GLPh6R`Dml(e%hJ|Oolk6D=aUrAdZ+V7h-cogd7U>xJoARld!9dUgm~tS5YN0}^Ez+Xyv`dT{mdKDOO~h28@f&@pL%~;r)*x=DVx`I%I0;Q3gxp-*?gRJ%I0INQ#P;bRETGtvUy#nLjAH%h4NXa@&;}2d2eIdylV5Q{h`I{yc)`9UJbRc`$L=8c~yDV$LQgG2^U|z^Y|Bod}@7}v0(Lj7vHJxau=V-U%S}FNBT@DbLLO&GSkJ!POo=`i?2R;Q_Q6^QEPsgi}ya?U+(0aZCviW-wkb6rHxPj-Rb*(&A;udw0*VB$F1k6e5`x=b4;~kJxAsBImYgMKYbnKeYE*RtIg@Wt}ncIHt!Ah-#eR+^WNEfHSb-hou~cxF4S*#|Gl&MM6Undh5F^a3$??07ix$1F4lBk+P+%nbDP)sJjLsNb@-df@43y#ndd`1^SsULJRfSGc|OEP{dwNzW6blR_L=8HdYI>JKEXU6;+f~Y%>6#Ezt`AT*u3s5lu!NMVV_|0arOx|ulod>_uBdUgb@FnzfTDDo8#{jLi}2PpJ4NO>=SIhx`w|`2(`mLA=atJOG&T$XFWf$_|*9cd}@8!5lOC(HlI3IvG};2t5|$Y&sFSp^jyW_6MC*<@p;WTSF!W;T*cP^Jm)HQzk04>>(_G?yB$4OnQ)xX>poxSRpoiFQ}e3Dr{-0Q*Yk={J36mgyw0of>rV1{>vyHi>%5`7{rfS*Ge6k8&JQ-PzaMR0e?NxWVSWhZGe6k8?gMRJ_kkh(%n$KH&HZs;KdkGH&Fi|8;&uPYx?}UY?u7DLcWhqIB|`bEJ0YHRC)5t>j?L@36KaQbC)5t>PIN`C&+G3pJ@2yk)OnZk`a7#b3xA(%@ew@-vv^O>!7M&?4raHb=U^5eYsop7-Hx7v*}R^E*}R^ES$wsggW3IZ4i;~8vCp$E>pYO+b-iQ%Z1cK*ws}3z4CS+b4z<tx5aO91sz+Vs^Q?oaQ~A_+AbM<G_1L`5SD|*$WAmx~{8a^M^HS=Z#Nt!uB=GimzRjo3Pb@xleq!-@o^SJdo*!yo&rd8~&+|k1dVXT@sq+)N9X&s>^JU#BNc$_!*A2Q4s?*T(#OittyyAg@Kj8=|ANB4(;gq!dul|J7u5E|^_fI(27!BFR&Xrp?*4$VPV}CTZ$k?6oY8m@Z#AbNjMB_#pd&cwe#l(U~5ljBF)Jz1+wdalPHTH<Hn}`*Q?+16QvFD5(AXY5?Gx8<(EMu1tD;EDdu=p0nMiVO*-xn;toVG^?a5;S)z-O3yuaV)$ipBqgcDb+Z#-<W07QYf*qWL^ynZ%04pNuZiT+>*4V#VT{qDwSSF}96ZvG~V5Uz_N9pZ+CQ{62c7;s?|J)Bqlgo=kj0`p*pDhUjUJFQotW0bGclZTR;XyKMn1UbTwfWNbFEV)1`L*Gjm{i51T#ry-h!>p`sea&ijMEZi(&#XZP*56!da|Gfa7Mb1y~o5(HXT2uP%ftJDay^{M9t)DS2G6sDaw<$dTOvbn$&qbceUY_H2YRjpY+7{GH?OD`I?IYAn?E&iL-IDLQe8&Y}LM-?uV#$A=np?qgP3GNw#vU_PN~~D?0Jz(Xy<qHnV#VS=Ctq@Nj9p5sSp2bI@n;(wL#$YQf3WyRX?sinKT2QU<7=9G&&=>+#o~WPyWH37#_lFoEdB{}iRSZ-Wf3bDe=52}b1h>Xh!u-J1zn=~E@Q6|D;B@X^R<bt-SjW9;@#-E8(&QScL#7Wdb041=szof8=<EIzKH%i1aJ|0Uc>KV>|P6C@v2q)E5;roRxJLn=z0R~3Sz|%k<$px!sQbyzJi=0Gz&L}SaCi%yU;v`{&xlN9CCh!e}&v4uAM@^`DiJo?<cq~(fT>#B4f~>al4D>pT!st;JL^%*~fEyo!UpKm)f(bm)acarS>uErS^O3<=v9+xqQb3UrH>vlvwiDQ*#?wu2mV^Z)}ONn~4>RzYcDav4pXM#EQj#LB8bX8tX!=Sp0Ed@hy#wB~~o{TCn)Vv^_R}7t_~4d@XbDSs8w;So~qM%YD6JY#Om*@oUf}nlCU`hgh-rX6O>lwT*QoRxCb(F426Cu^q&U#jo~!ZKCS~`j=So2k4oGA4>nz0(dBT>fjsGf1LnsjGm78A@tudfQO)G2YwG@w<CbXt5)%wjm;xgEdFokS_9XMSn)h^8lzdbp2UiKkuwC%!p$XC+>@L=Xr4>|djfbaIfvmllRJcK5&G?kmZ9{$hWiq&Uob8*2G=rf_wfAdFvi#MT;!ST=Q+MX?PBVswk7pan@hdaE}>p(4^l7hmVD0>o{zf_3%;3H@~fzs1eR+XjD2NnnXy}l6^p+CZnCi#jU6IZEdERKCHEX-U5OQoKOQW;m9cTeip5_K7Qd9X#|7|G`Z|QKZSK8Jh94^ye+2DvUvC<_msqj*wdfMf7aFTatXTZ%=n~C!jddbcEdDffiRM2W+exfg{F9!qO>})o{}L<y5Iy(ehtdDN0Xz&n_3$Usf4u-c5j~yoCG_7ZfJ@M`6JO2P?F?Y?s#W|JV`apO#ov#vwQvQ*ip$735zWH&CRSWPP6?WYn@_B`H#ya4o=^YP0X(0aBk)_uE#cZ}^xGRP!{~c0_a$1tWL#tnu4mk2%#LTAWsGm&xyUp5is$$ywM(g&+E&y{?K#v-?K0}6_7L^*ZprstzT<+s5(~bCSn@YeGZ`$`UN-iPvE{}l5GxiRg}dF@OU8a6RxJK&@+G&8v2MhQ#h(Bc-`d!CV#VTb1dFer?ePIzL0>=M>zaG7m*K~X#s7kKxv#g4%^+4RejU0*vz(dKCsr)}59kujzcJRCSh4ss&?TCu8+(gbvG}JvUz_OqnEoYJ{4siF;78E^i~t^ip8EJE^j|-Ko1mvNemMPi4&dSFc?<s$WA|17i&w4UUp2OnSh4sA(6tWkN@B$e$!UUS;rb9OzLK2bXcle(vEn}De1zr&^#4%+FCga^_*cmt&b2e>w+~uI(Dyp-OSFE?xX2jX$hb}C`PXNRqdXURCg1QJ-=?;LdZ}$qz0|g$UTT+9FSS2VFYlIo&*eKVxErzH3B;2BGBvk@<=VH#{%-6OW0l4R8k=eCPsZ|$ok`Bq<eg+pjs-6>)|TrY*QDlQV?P>u$Jj<{rR`sh#f^Px>>tLiqCRHq4!9Lw@;J_GXYBXXZKbv?{hS0BL$B1lYwST|-SPLK{TTE~TZ6cM6n*ca`C<AwhQ2-eA4J_9=oWof6St%Pwv5-A)O+0DQSuA&Gio%b`JetP{J%f3WXHk(7;jgmAHN1GH=4Fmhp`3uwd8k}SHt|1!;QMK3V8nl9V`<y'

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
