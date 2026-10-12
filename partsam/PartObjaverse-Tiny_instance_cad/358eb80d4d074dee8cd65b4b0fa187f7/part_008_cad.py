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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/358eb80d4d074dee8cd65b4b0fa187f7/part_008.stl', 'relative_path': '358eb80d4d074dee8cd65b4b0fa187f7/part_008.stl', 'source_sha256': '696ea4b776b1b1df3ae4bf7ff9c77c4c722c1cd58985fc22352185f868336f84', 'input_faces': 206, 'input_vertices': 185, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.25738993287086487, 0.10633206367492676, -0.25838059186935425], [0.22331656515598297, 0.346245139837265, 0.29162541031837463]]}
GEOMETRY_BASE85 = 'c$}q~3se==8pj7T1+>DT)YKYKgOu=*8dpIkGnEh`)9Y112NVobR5bEII*NKlM8rVx5grW{G|0E*>kKN2sHHtDE7v+@-rLh#nO0`qyXX7<bM8JT?pk-<dtCqZee?V8z2}=fGkaz*DZWY5V1<7nN_5C8%7?8KQcERR$w|+inK?dvMr78s**;1jaqDNtmlH=MB#rV>a+JAY6Vhjl&kpOWhDB#Yg+-`g8B?=oW~XM2o0>f#-Qt5%C(lS1e8zLB)6&Iuc#o*w5$dB4N2o8U|Kl$}l;8-OecmaeQ6F(CRz!2_rNd5%E2o(&6(6sTmAJP3Z_K;(J?d<XUr*W~w|6CXJx}BR(0QBOUhgxMxXX*HA!~^n7c#0E<Bp)K6|}#!evQ^|bMN|X?p^;MIO?~#cl|c^uHWX~^?P%>etm1v+vM;0<SezXEm<jZQ@zZ*?aAF9-1qD`KHgD#J;upmuK2H5MEm<ZkhmJ7^M22Lv(<z9mGE&*U$(`AFJkU^Grp4McgW;(H2&{7^)&wMFH2)(p8q0oGcMz>NBj7U)71Xwn@41Beh7Z3E6?+iZ_iTuNz3VYwf!>-oDw&cLgLENd3!u~Llhscmby^pTARMa^`df`A8lYMal@!~(sBJ(^$zvB(>UAM{J1&h$A$TEbFcZ)Cx`NW$Hg2Y{za48Sc#j5nd?tZpyM{5@;NJ?cNfmP&ArdNn|qyi_c%E32F|;Y`TH5Fw_OLWM@u~|b8{AR^>d|`uJ8U|5!V8j5LYtx6~{{4=)hc!DcVW<Z~1)#jc+bBX*+?B*XBlteB#>n@qE1g=ZI^$&k@%@=6Y;yTw-p{^PzgotOGp0?|I@%;p<e7&CR=+tEUR79%E)Mw=ao0<Z*u0u?_Ndr5xbv%I4nJm7C+bGH_kF$H8@F;JR{sbNO^*_l29|zHs5baC6)jD((xL|KYyq+?w0}u&sf%N4|T&Df2Cr#FZsiCVRB+SaycSuN(iS+}@ne+!%KxkIus<ckp#F_Cg);5w+)KuH`T{_Z_2t%J{N+;`@T$CjN5M8mG(~m^*e>ZuH<OPU2c}=uVlNT}<No&kwAp?cDcHQ5@Xv1dX40oc3#TBZ;~Cv&r{m?T(Yw-tP*n+nP^4uh-z(Fy?B_XMA37`<-m8em6(`ChB){)UTs{o7?p}P`~51qB?3n_adD~Bju;Vu`)0GfX{FJluF{Km)13Qe%;*b{JOc<`L((C`Bl^AFwcxUNynAQ^J8;u4|CU$D>Of@sT)raf9xQi?~g9#dGN8|-%Q&pbMwI}Ua!{q?DycUw)6cpEp7_cIdVFWQ&7(5EB9b^ti;XYjr{!0$}OW<K9>0>A#@)ZVK)!UT)P&^&z&*P(|nrMDsg)~cVRtubFAk|Hm~Pyj`iGy_1rbZm-m}+i{C3+bffjpwE6O1PVsdf#dZBya-6S|2{fO|nz>~%H|oGw@$qU+M-n%C2hx0MVgAQF_(kUWPF`0W0S_@Bd6dsrX_N<7+B%tk7s=~%uTICPea;xV-W<R3_zJjIKbp99;{_gPoRijF&DD*sx9|vR=jNNb6Iajmru$YOTwL4OJi9sOS;aiNxz{{vi|?sz?0R!^uj|d`-q)L(dtGnl<*O#eO@%z4D@ODC4!HI`bMrzGk9Yes<~x4m^E!a%!RF@V8_fUC^I&`(!0mT^_ZA)3y$Kg$C2pPucWvW&p5xE$rwrqHUcmLZ`3C0NL&ba?+un52ymh{d-zSZM{G76R4RbTsm+S1alb$DLmuP-38pQk6Y~G5wUO$xT)SC?_u0>9Ki@6VtV{>yEbK`>nv|rcSZ{MKnA|{{uoAb}p^VXXiH<D?cc1*oQT>Ib#t&^_4fwcbE+$_Gye9rsyo}q4T;Po#$l#jQ|N?yNheuBBS`WoLawTZ;l<XN;|MSC>CgBLJ2AN-Zx6Z9&TpP!o#(s3z6xE?o8IYiu1%JrCsni1D8<nw;h+R^=Mb4U0x=KVGuq~rK#8LxkrYq<XKcMi#1y~f-zn&(G<LS=rX9lfupzYQpMO5D}DJ#j7DMb91A$E}E)1O0j4?&kTixi%tzpI>u%evBIl`-o?K$j{%O?yvUX?Jp5mnsNO~$d~**ar+fsCo7vLdho90e7)7*=J{N7gs+Rh$N9W}@hR15b4MO?b5t}Pmzfbv-#xC9=I_xwOj^(5fvZ)_RU?4z1Kmh^mD*nk<@TSgrMhjd59~<XSbdT1AN8Zn4&t{m-=*VC;qh(mx@!_~M>>zMrR}EYydJlh+qYTA^8)UwVy^Du@wNP*ayqV;uhM?ax;S3X!ClvxEA`74QC)sL>AgVT(e!<4H|2%nGFM*%zgT{Rj<-$vS{i4`QsU~Z0cB2!JGL-4ZpG4ji#o0Q8uEV`%=L`ndTj0(HH7O?3#cCbABiQ@uhm4J&tY7T%^l#TgX_`$xnLEwZ}BzrbdC0FbG?GOewORhI@Zwpwf<@NMe2|DaDDWF>qo8ef4THtV_aAJzb|t~(B6XBM#gcu&d_&;{hZS9oN{wKr!+jLjDkxId_Um(0^c1rx4%2o`S|YmDuCBrd^ahN<2wah!*`Q`?<V!tQhsj8-<3%oe-)Z|&`}W{AfBi~{z|Ztkt+R3$b#0-j*b6GD6`jp^(Ud8-TVB%e-hd!YB(UYTgb}yV%v)Qksm<58*vZv7lh_oQ-(MQ`AnfX@aMp@a!qJ3{K4>MqR$}sgWzfC^SIPTL%v>UqtI-`dC1oZmBTNGXXUem=EI*4Zyox~gFg@6EcBTzwV8!{i_i|Cg@`MVR|su~za5^H=Lr?TFM?NrJ}cm_fR~3p3#B%B$p30xCqn6nnaGz2t%AP_o|R_^O@coO-V*f5gr5m71AWq^HW|oMg`N}Yi1-NdG@*&`C&IJxPC}9JBjKf?&m-_3f!7IrI!bLiAs-_&UZ^W#59FhTCcvKn&&nf&dcyAsZ#4S!fZqdN1p0K9+C(5<E>t4)G-3+!LZMRlrSPmgQ79RHGQ2|cNr9gNFA;s7mf9pDe^sbTXer`q<eP;m;a9@5@_eB+@YlfGj6SR3uZEY8K1-!G`N+2ky(UzQScZJ7P&NE&cvikrXf6D;@V25)8T>MME77M|YO@mgD?*!uUP3gGZxC|8cfhmqT%iT<7r@(qJ_dXPUM~8)B(=#!zDQ`9&=ADo$QKJ0z%PJj<#9qI;E#Z}7=4Dr9}X`LeTGPF;*d`kdQs?M#BRu+7s`R31JBC42z7_w9p3Zk(+z$%cwNxvVW~|Q<kN*l3S}ey1$j2|sfarAXrTc@{SgOB`BT`o;!r71!nPHMNqIE3qcO%Xs6X2D#~4=rkdXC1Bw>j6AP++xig+LLHbU)%+9Ez6<-M_O#mA)lPuR9%Uny^c?KT*rFVq%o+G32yFh|y0O+g%s+=}CnTQLiHC~8&_gOOYDUgTB`K|V_8&q6a0ry(B)FAH%7@+XC!5Q;^NL7pHK4?iBBl|L)=4E$%{C7@3X{1|x8qED>U=2_%HLV-fzh@Fw&3oisQ9C-(!c0%_fwnpAZs2BWR@T|O_P!#+qczw{PHT>4_`k~MLQk#CreHH#SLu`t?8S*<ID{qeIgS<KNCPLP$+Fe3^h<76QL*5ecZsaYI`$JaVLg-PU*M%O0th@%Y@|}>C?}DuS4WXoXAK&06|LMOT|NS$pqCNg2(z~bU>#5xHK5>(|UsjXi@1S|}75}V-WVUs8DgOc%e*TL'

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
