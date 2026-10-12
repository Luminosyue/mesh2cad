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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/78a7c30405f64b0f8137c3922c1464a0/part_008.stl', 'relative_path': '78a7c30405f64b0f8137c3922c1464a0/part_008.stl', 'source_sha256': '48581539ba43662f420acb59e433a8fa191452197533edc59e8a3a0f6708e531', 'input_faces': 320, 'input_vertices': 184, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.22760751843452454, -0.4999999403953552, -0.27738359570503235], [0.2046087384223938, 0.4999997615814209, 0.27581191062927246]]}
GEOMETRY_BASE85 = 'c$}r036K=k8OI;DAUDfpSQ#!CkYiyN!nH6Ug0KNrE<r(N*@H72y9+FG*oY)6LINrY5F!J}f(UX$C<Pi2A&CeWB?b~)qX9*$QWayWk{C>X{eEwD`t77Dl}y!F|KI-Rn>XFBU-$G(ZB}NLs!2*eTB(A`&D*;Tl#;5glGMVyf}$BYd4*l(%v)SZ)%U$TOujgB+=#4+mDEDDBqcYmFsC4;Pbj5dey@~Hp_Kf&1w{qfbEeEK$juW!BztyYp63gvXV1&?{%+r`S9+&VT8B=dWugD^QOnzeaR1hqPJ0>s_S=sn%XYd~PbczycV3S7>dS^V{45Rj8z1Ty?2mr(w+|Eb8y~j%!#A#9^T)CJjko)qNsTV}e_Q>=yY~3w7oC@k*yH2ves|O#&L!$M-tJceTe^w*jW4tNhcr3pZ?D~tR~c4+xNOmYME&@%)$dFj`YZ9SJwL|V;}^GjSA3a0KHlzk&fUF|s6XcI@qhj0dkM!k-tPa+U)~q5c3J(#_t*W(92eGYXk&7~hw$pX7MBOa_y4}`+rHlv?00WyAG#Xs505K8pQt}PR(reOx%BZ{iTa&)w72`+U#vWvaC?qxZ}+RCU-;`PWc8~f+AF(%_Ks5t`)6uz_dB_TZzSq>rfOed{15jW_Sg9p%YRzx`>_4K?Y=sg(6`aP!Z`E$9!S_fSNjV6#WnUN>@U*3LVxO8`uwu{v$T&|{qE;A{B<7MY^{eo+AFI+Ty*6F|2(z&U3}SP-5<{Q^c}zd+Jz4S>)-aQf2U6u-#foseJ#G<_94?>=cZmC|7`n_?@hnuBj)@nT5{UY=Oez4n(a4!jrI=P@77b=-#s4~-}a8#o=UlTJ$dJ8V0$d@#LoA5Tl{(Yddt<|{A=&x&HRVET;1vaojc-}{`2PgWBI7L{urO9ec7AygX7>sw@UT<bX!sCZ(q^;OMXA&+umG1V}1di@olddKinW=um87uVv@W*!upK)u=cK5Z^Ksj-aWG`aDA@e&Gz8KXSI)-?XkSsp2+@h4(Rs{ejeH0d>+Mo1b<SGZ~F-2M^9`#?E8xufzOKyp7D)$@MimMZ??azXyP0GJXoI>#@nA4vHm(21K0DIuYECaJ&#VgsQvNeK!401OAhw0`TR|PUd|ml7w9+stoEiqa;fque}Am=G3KrFF?u`cwC`_R2;5)U-rQdqAHI%1H9s(p@vb>u#y`0#a6e{y*BW0<#-9w1?@rP_YS!ClgLS`keXxD(da^*d{@<V63EY3$-t4dO?jP~&ukFj&9(O@4J<ekn&d2Ys?alrgA0Cfqe~njov%gO9Dc%2mdf@tB!JGZXyLgB7Z~L-8G5*#&dK~NX$awqn$awYVSvTX?oAD0btT(k}!WsYXFaCNxe*SH5zAqSGc1QaN^KW}I|7uCZ_wMMm{&^IMjUV)GY<%sVNAV}k_}Yi@j=A10nWOvv6%DL6+ndkFn7>QE`Mj{a%lx}b-_`!wt-$fE;2Ga|_1jy4<7<0!e8bDToYm*)nZW&k?alpw@h(1Mw%_vh`05`gZU*MZ@)2u%$Mjp{8*k<(y!O_4f1TOiPi=3$pW+oh%K9<B>@L^y+suDf#@qh$?b@C3*CE&2m~X4SxxaOLetg0AE7Ah@+cEE?1@E`p-}b%gRua6wHNI;};QrQ4+kerYhn^=6#rMa2y7saDf^U4U_KrUp*dF8eXdm02&(i$+6;(6uNML)6uc5seKfEwo`>(g2h#x=ZztY}}Z@kle?6LUqV?I@TGrse3s{j4d{=RH`^L^QPcYyX$&R^plyg7ek<5=IXZEwC`$HsYxertS%_wP@#0>A!5{yt>7Q_pMls-{X(`Pp$l{fLx@$;3bX%t-&Qe)>u4p8Eg(^fTSth8bQxL#~7edDTaDlk5x2^DF3)bl~Z6uX_eRh;kT1@)20F7cAop<N0Ac=deBIJs)BlR#JU=on&vgH?KG2jbSXw(Qr$z?)NI2jKG6<kLlzLIM=H@ucneYa1O7VN=9ILubsT#X!sRMxRl%lm%@9<*Wf+y>*Rh|av%IUyq6N*O}+~6hPRVD;O%gf{gVBhM&`r$JU@*R-bU_#Wj<Rmm-oXVO1L%I25t?vCELN0DR5i(0ZO<%*#T}3cO)N#JHnmF&ah+`xD(u!5>6$%!KrX}G7atyr;|Nk$?wAHa8ISzx2*HNlyGmdC)|^MVOdK#%xg=y6_vxB<#5c}P<hN>9>=L2xeaayr%>CNvuzy54%80jO!8IuLAW!y50=~ycZR!A`<XMz*Whk&8o3KjgL{xWVaYLY57^9+<S=p!ENd^M^m!P8r&7YXWNSDV&L`W#k`KW7aFi0>PPSL&=aKMkvZE?L?}Yb~onXnXs{EW4Hs`YN9x_#xUk8Ls$?mHBx*_}unGQ?#ROQzk;n8F-Sn?5gu~)@jJx7+n2gw6u30%x;=8$t?$yx9mcqS!WL@t1f;AhEIu;kBS$u002uhx3Ck=z7JZh$w!FHyql$o23#cqzFImYfVPg(p$MW65#wSa>8k3LXg$Co^HmiLm4Z_$YIIgggLG<hcpt5qOAK1zrs%*T8Go|G|`Sn0yHi!~H4Ye&jm1AKZdm3NK|YT2R9GQNqp0v2ZiE2{{sO0w<Bf;o<CG5+&SF=|^Ry*TEL}SxUHwtg6b_mGDfmIxKmQDqoYrW~~YrleOStxP+_?OV));-~(iR_yBx_YzQ}Gzl1A!RYjFQs<0oG;i_acxGG$otN}~bgsa2%P&L_h$$Q~iaBZ><ELjh(4c8?bz;$8Sr-zkZX9LMFEZH9(2oIoyGsu2$2AoW`fF<vPli}}B!p+HMaC5jR*#vG1Hzt$dB#uX8O1KeOAFj{-Hew%TpNEh`VYwE`xmQRQzy&;CNDhVNnkLt{O4KTja}~H6xd5&P*C1!Xl5^o2a7}71$5wJNd@o#wd=56(`a0A>j=AJfxE|bq{dkytDTLRO1L3vsCQ5h%IRM@OuO~C$_3$z>8BXTdFQbGfQ^MoO=I}Up6xkFW1!t0t;l>>2OiFkn*#K_9JWS-+DUPQ+w!llgddjQk$<^>-@({Tieu~%3Bj>}C--qYHvnk<)<RW+>`~&ibu;f-)@@4o(Uj5js&E(Hu$)CcT;h#{#FOV<7FTl&mr(ww{@N)P`N_af^7(5=%A|Hjb;O~(mV96(7$;aX2%=Izy5c~wsJx(5jvob4HPO9>s{&l1L;rItU{vSE)R|dcK$G`HfH&*ONfUL}Fa-H@r^p*XCd_wN*)xQB%hf(z'

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
