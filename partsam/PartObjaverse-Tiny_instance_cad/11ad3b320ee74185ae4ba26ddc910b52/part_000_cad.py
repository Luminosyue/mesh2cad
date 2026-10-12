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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/11ad3b320ee74185ae4ba26ddc910b52/part_000.stl', 'relative_path': '11ad3b320ee74185ae4ba26ddc910b52/part_000.stl', 'source_sha256': 'ddd0359a7c8efb2f3ea367002c4687b0d5406d5ab76ea42cc5634f6fb2e43eb9', 'input_faces': 360, 'input_vertices': 217, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0692555233836174, -0.1505555808544159, -0.40754711627960205], [0.037209402769804, 0.24548405408859253, -5.699673783965409e-05]]}
GEOMETRY_BASE85 = 'c$}qL2UJzpw%xWQYOrF7L36PLWACD(UZZI2*bqA?2-t%SE60j8sEDE%xfBZ)#IB%tus1AN&?GAQ%}es~5?lP~zJK>z^Zp$E_-~9i{%4Fe)|~UKz4ku4pF8mDS**Cbl0Q$?DX7ZkdrqqDUFEK3ghWgW9}_aQ(WEJ}il}nX^`Fbf_8HXMZ%7d}L(TCD4w*V8!mF*#%V(^&R|A{Z*vS#oB7!E3nj8@vqV=vp6Q+hZ^{HV&Q$n1)ZnLJX8`zqE)W9~+_J8~<<!nMhX6F7=x-Dh)WovJQCEV8DZeJjJ)1GPCoADLyLw_(Ex>03E7Wku6x3n+VJyYV7k0FnGIpa<tef>Pd8&{H$U!5E*de!al_SdzM-&i?N^1s&w@#eGH$YYM~B=Nu1Jq912e7lhT<KC_C-tR~|n|2Vr^=Y)noNK#@yxVGvJ|O~m%r7pW{q}F)mU^?Ij)M2;b{EeFyvacPqi%=bFNC5!fx~}<Zp?pp5Pn%(#H)~pqTjuB80Gu5zHimljS;)xcW%6gxaMC<d|&|bsPBsAgWtF<@%1XAJ?fjcpxY8}ivH3r`P*MZ`yCUnNuGBe9YFhUuFfx{N0x<dB&DEUN2!aFXNdnE8Mmc~x8FZ2x=)nk>0b@;=8hcEpZM<vKUogCZAP}}e@nr5saqY;&t{h_(fw~{BF~(1`Gxe|aeKj!|Bikuczg)DeQbt_yf++I!87(typg&D+()55&H3q~=jWuupJ;<TfxUN&KL73!__(e4(vAet<COTADHum1XRYvWVjSRmVx)h5Uo8E0bCcvLXe{r0d4a@#wMp80X`8H<&^e-4tD6E|dV#!e%Sg%7u_5x9>$C1zbu}V770*}vbhnVc?{E_ISEUgj*da{x%bDm;<3)zdho}7{|Il@^E?xzp|Lrw=CBEnn+mP44^<7zKO(i}z4C}&v^rXzUt2H=3Lv}zPJnN3Er%KSxTSamZ_w-`ERaakbmhtuOfp*#he%^<;@jo7i|8k(L>vezMC-ZHj>?gnMk@eg7sl<PhEc;JP)m*Et4%bG0bNTgqh4cnr#G<}VbJ_j}q7T2l5`NAqiBGvK`rlV>fH$8>KikiW?oo6t{HUUcSN&5(x5X~#sPm@05&hZcqPMJ#b!Si9D*c>4PV|5#o00dKx8zSBEbkRNUG|@$;gV-kdFb}wis(;!&<N=_-#0Rk4`pH>Gt8+nKRvz|{lP)3FNfz6^p85Y7P`^DvE+|@CV5uOm-xep*w4(Br)52s^%cFK=2Y+(FYn5H?;yIe4@LRTkutu+s!IM|U!8=$X2E@{u8jNu-9P5KB2sT$Y0=BYO@*EjE&E%wJgjrIJp}X97}n}qA>I4_LbPX9Guc1euakYD^K<M2>a3^CpJgEu|A%drb^WRj-i2-y+lBaoJp(SFJ-J`YzBcU)_A7g(0vWH=Jkjgrth3HTqtjK<(@J4{154aRJI&G+Meh-?5#>jJhyB*La#iwv<AZTD2fVm%)zt?v7#CZe=V*^n!W6yP#cjHOT>F@P%UI~f>^(AGF9NQE@9iq_&8K01F#jx_hxnK0<@~UDZ9+e1{Vem%;ec+eTrKBp#8($(ea1?Ba7H5Py|rBSCHH92fBG&K^W3kq%!jXSqL15^g#6s+%@5o~_g=jUdA?gJ{eRL;^t>49C-;1`-~3M{`q<?uI$m{-llkyo4%WX>asuXqBYf8-@aKD>tFVe#clPQRWn5Y|65Sje4?cMi`oYNa5?w|1gCF?<<6_obw$r*!18c6njD9OWNOW^G`qS<aa0C3!Fzk0m_*LoudhM=&FRBS$<u5si_JmZFb7%as?eOM#Q}Wh54ZiIObmil_8}G~W+PuF|^j-~jqCb5H%XroH-)<cjWn7bc(doXT`&Ze7c4U~+&QaY(Usf0MN0mvI{@>&yy6r|f^k(sLj<;$hI?s1wbYGmOMz_kM-~Kob<NoqDna|I*;GA&X18o&Mok2UtEE4@hn*-<v?=+bYYM$su!~M{oddc`kJxBklRX<2Sm+2w<Rin$I+csi;7A*ecEb<gQz<Fu>yi)duA^zuNeIJFc9P1||e{q#3?W-^Py(zK}Um0;8<xUhA{aR)0!v(%0v3}L_)MWVnkr)@l{hrLLc9Ei|rb~bR<1NuEgos|hUxu}x%@N+vjjMT>CxJg~l6@wvw8T&Mz&tU%C(Am@{2u4G>i+E^)azD5_SKYQqCfmC3-6WHRQ8R#0ZG>Jvish|`ZcHa7rkTt5#%4bTjtfvbGWals7=R^e_9(Emp}W9{%C$C;&aZ6zPXp^{eP2jX<HQQLak|@2=DjDr--i<jQM8#<8N}G&WK2W-m;jiyQZO{zllr0JbB$w*2{uvpF>Y<jeawFRFeLDJrugJtP%Fff-0xw{-VC!g81vrWPR;^An|9vOptZa;)u2XjaF$GSM^Ti<IsyulYTBy59>s2d;0|H9pfYSflJk8zv$E#^V#vB#|gxBC>}5KQDq~~!E-V$pOwe{uBJ4Ofc{=wZXx{-uhY=o0%W{uAKM`B^|pz6)c~3Q;ofr3a7;);eCS)!Z|A;`gRfs92m0ZM5}$rd^pq~>7uD~hQ{Xou<E-<|aeENfqsr}ydyiUJ4)@7|rq{6#naw82J?80U2l{hY8QC{(&y11w{1fXwaCbJ=oss;@YUs5mV;meeGh`h#_*Kr=g5M|VJhlZ1GEV{;%Du|t)FR|@n{%;{ZXYB2L+x6!PQxoLL%z+^&Ov{@NbV0&jicc`FQDJ-O`_!7kL$h^J}p<~dG#Np-(s8K-mk{TV?L|eZ)Cp;xx5&@WR~1ZpDdE^x>LbupBg?^#`n)+vQK9B#682XJI<os^V!n>sZ~Y48inyS-n7Xtq_>SZ1AR>ixxaPEjgoay59g!fQfZkdABN3?Z+3GJ;uC91|2IgAfdA)sxo?L*lJ7iw<uLd<N3h-<iKFGdv%cLx)cgKD#5tlT$#+#iA7AK>Qy1}GWe-Y!`rYXO{zoU=w*zlfk?)m^J%gd=1!4V}J67SGQnp(`(5o#*`;892;rvzU;i1rLMPR>DquNRPA6|!Uq)$gb*so+uf4<u)OxF2-T!4NtQ~GCY2=;3g@XH#^ANT&)C)L*d*k6=?E6fK~;i!yzlgiU&{fw4%(brAR!BtP7t21%3-c=9W-&EEoGZ25})p_VE4#@hAd^}U)cpo^Fj(M&UcFl+GQ3m^xeaC8?gR0(xDCpa_V4fIx!(`rmU3@9#pWCPCFWdVg<vZ+8zi7ngyIn<|pC3y9d-whf<%_B-@C{GO_uAHucz+dNAM4ri`vt5&$Fe$Wp_jDFdVK1cRY;#X?h<_EiE@sYJRrK+Qoir@h06C^<$!fEF1;}C3*6)7zVm9M=)H=cx6XfiW-4^G{2Io~JYPq?2ghy1{ZH+kjs6LI6^8j>zRnPR(O}t!H|&+~ai1RR!B-8y{$U&CA@`tPE{T5Gfq7y!Y9PN$bQptshO%vo!FqYz9{X6}lYMgk`2Gs^0abs9{66#R6Nzu}cstsYJsta!<Htc8pbxu=b5oV`lzVc6Iq}F-V#0NJd!;YXo;o(1Th4tt7v3jH=4Xv_pQHS)q8LY2q7nKzuyjl8o2p6g%kV`qWuDJ@4BZU%mHqeE$8Lz<6pHnu>O7Hk{mmBa*JgCItgFKtu}+OkT``{>7js45FjwaP{k}5as{JH+_WIy=9&=)x+^b5uCnJ7FknBs}%6-+|eJFIbZx!aPZTUGFmjpxf@J9H)3~bRzexF$35Pgb2?g{pt`EswQlqq^}7mT}U4#d67EdGV)hl26m4*L!HPF?d#bi>Q8eSxtN=V_pao80f~X5t=EV0?D?lwYA=McZ#vO9IO~L!DMqxvQ~3mY+nmsQ+C4fB#7|yv4uulW6l+P5!?>i8gVzp{nkFr}+?Ttq=Vt!~-l``}e8&kPmfQ7iv?;HJ(g9fYya&CX<h+4PZUX$rlr^Az#BXuJ}G|%VP4;wDHtGcUmf+r!tquJDE#sC&*K&EhkQ8`6Es{PVT}d$aBe$P&-cT2D!#p>2=I4>iT)6(@s*mM}CXi2@Bp%o=L2=ZN!<xYst6sU0m<9o$sXmI^wm&+leDMHtWbWo=IKv_2e$BeHv{o>rbQC?Kw+++Gz)g&yuGxCXTt%7!yaFPJEE~Aj@u~uC)#18t)=^VeL(t#^-72%wv+@p+8G}hxo43ZZl46c}~lrmP1|R3*>pk`^mK(V%%=0rBK^Xo<r>r@n=q3KrNm;g|YF(+G3rS%-C2<juh%zGl*BRPm-yvBu=Kji)EA9&SYvDk9FEqmK#p4@u%blZ7TD|vP}m4r^F+OUD^ni*S;5V4`Qu_IBgj5IC2*r!92rQW(4tI@(^OJ`4SIuS~p^s){XIl$b;!ai9^XlEPMtnlzJqe%^=o3ntqzome9{&yzALg+6=}lrQbroNXd9FBA;%_HQf@IKwHB21p57qNg&=zo<ST<9?iO4&$K^G+rqMk>CZ9dF!34s>%<x4+VmR8Bi>Jbo%|;49AmOsUO&G^uJILOtzC9n7PV8<uTVQ>!TZQBk?V5Dh_!ZrF`Dls&tlA8;-lo3s2!trkzVUN_)POn#9CYBv>0lM)HhK}Bwp>bBx>`>HJ(o%LrY?r`Q)={F{~%ZX%nbTV4MrjBcDjDwITF<iTy2n0`vK^jOGKK7DmlZuJOm@{<JWb`Ix*j&7bu&C-)$3X^9!a`aQ^7(K=Ia$-J63W4&6dMXvFO<Sl7-mids}Mr+CX%aRu%u43WZzeBUJT{f2UVC;v~DzRRzRV3HAGI<qREtaWF?oO-1`fHPyA@;Pylx4fhke8sjQ}<+E&1<k;t$C4q(ke2pA$e0`FAMi%{q4y+5x22$?HkdWvRzGCt_))vQftHVU7gl|ysgvf5jP-j!x%4?ZNnHZ%d_^Zzc;zY<@t`TcP-EN)K-n-QI5DGpO+(cBX((SjMG+!W2W&(<kg9*F}Av;j%tkmz-jdvSDpMLnzz$h5Vs?*L*9br+F71!-k4UOx#}>s7CpXWh<(YMk=reC%~+qWrCfi;bfoU$+7F~Qh+NwkCF@+{VDf?FVT=v7#Ll8VhWaepGN-Me*F2g&l6Wrp3YMQmEtoMbuAjU1PK}euS6DP%$7W&&V;tn0`8=9<Gx1i&XugkLYZ(^4hqjse9{Oy?>>+m5w~y~Kmu=Kz(T;tr$5qc2J*OrzZXV0(v&nTvB{5GTvDQyf%ckiz=yO!x8TB1O-;v^pwYG>@Yx*7$LauEb<EK*}$2N9jJG+tV`;xu`j#6^x)3#8_J#ry=6#XRPmE;>(Zj$A>=HbNQjMrKKc{s5jaiEfKk3e!imeF_)Eu1lP=;IhOhgj$9&a#2@Bk6k*_atvk-+{P0v7e<KIzEEjg|(kTKUDqo?W=hgOC4S4TN8I@`*a`lqaRM(-NHw492WB3T;D)Ze8&yMTGRJ0J?8owLVwTb@0xt|*Ed)`O@D{oqn1f6j_;+v&DQZf*3eHT?!xxhCDva5Uf@Gsm70zzMO=z{RpO#Fjf*S!)4rI~-czzqdr^CfdTAx=raa5N&FAkbSyyhXvjU&jRI;DyXMR146m>85ul{B2uRlW{vW5PE?SGam{Iia=WM${!@ZUf3`1LHI+wFYGqWA#XuWtnEzW@$M&P4'

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
