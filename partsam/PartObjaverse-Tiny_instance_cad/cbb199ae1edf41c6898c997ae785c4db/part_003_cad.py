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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cbb199ae1edf41c6898c997ae785c4db/part_003.stl', 'relative_path': 'cbb199ae1edf41c6898c997ae785c4db/part_003.stl', 'source_sha256': '6c19722d84a416d5504da2d9974fe4fa15f67a66af093332ebceec9f627e6d72', 'input_faces': 228, 'input_vertices': 282, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.43022480607032776, -0.3612685799598694, -0.18749578297138214], [0.37501537799835205, 0.19590117037296295, 0.16557998955249786]]}
GEOMETRY_BASE85 = 'c$}r033L_Z8HOhd`xbUkTQ78pSfFfesiKU~Qf0AG1W{YLAtaTmfC&(YpjQxx2uKSeP)kP&ge8bj3PcK-K!WUu%BGawYAxCdkroQb<~K9%H=X<5={Y@Z&Uw%K&NKi2<(q&0Ookh>`lY2eGrX@h#%sH}_WAq<!*EpJXl9Jd%^x!&C%2&E$k7v0j0~4MU+Q!39W)^8p%i1B@pR_!+=86^%-bTFJ@UF|wvS}yjmjUBpFMKusQlr%4)2rwL_x0bg2%E)=gRRdUAlK^AL-hzePmMPfBdQ|Em-@DKPY#4DYZ8B6pLSJw5~kBW8il6xRRbBJo@6vH9>By@whRhxH4gUMbS=o{ME$zHhBC@VtwVY8B~9}$L$Bb`jIAuUj0wXmb>G}_u5$=;I{qJMt45Ac{(rjdX@9_GS}<%>(KT3<LP>p^Yt><>-Fo?^~Pspc=cC%-`6_ZxvD&b8yTl7gWT`)(&>ac%B`}_RY7iQpHyGD$@R6*i&P&xiu%!&ZH|TAFXeo{tZmnihFvdny<X*fz0CD`mGkv7H@QAtFLS+KYy1|EH#j~wc)iN`dgHeb3cX(D{{00{y1&Hz`wO0Qe~Fu1pYJbmz25loGw+1<Pu%YxJgI-;7S&JcpSa2Oxqsr?zrC|}X#dQ$f92dibBpS8|IAIUPyI9Zf4+9Vxi_qT=Gwn<?w`3u^|^oMCfBF_nQQ-%%G^C+{WI78m2>~hEvnD`GdH<D_0L@UH;jc9Vf{1L{*`n8%q^<V{WCYYKK0Ms-~V6qwnO(naex1VC+&aY7S&JM|HMtM&-<UazyG%{Ugz<e8{B>_u3ldr!lQk!t_|`Sc)Y{awLL?){psrUj>oPPx$|O6+qlQ^3toNZT3@-b4C7HhiKD*p{)siA`-ix{f54OW4{?A0fG6!A;wIPU{X^W}KUKvmLiZ1GfB%3d?H}S6)lb?##7(Zx`-iyy`)k36%iN#)VRLr5_X+zaiTCsFuW}3AZtvY+=BD1?F_$fu-_vw=us(AO^_55Zf}=ijt#4-EI@eu?g&npz#}U+LZexEcx4~oBpUf?;|H9+8d(8F0<5WKe9;N!qW4b=^oZ0TYRq^s*|ID?%avNOhGuQqjulAkpe%}M<6V`{h)>m#E^tje%uJxk}W{-96V~>J_^<l2{mB+!gK6724`1}W6?iup)#oT|t0#ACsBJRImfhWCR5jVL$zh4p8pD%OY!yc#iVdY8h{~x7VVb{ytfBy$hdjBWxzyE_Lz5f$8xjw)D6W8mFO>4WvJ-_!(_kF>B<)rr<2akZ82d7sC$D6b6@ctdUAaT4k6P(9yx>OZ5-rfjK<BjV}-Rm)FeDs>fd3@}qc{{?!$8Yp_()iYQm%00c#>ZND+@SIHip3jUzL5Ga0mpc2(aKd}^?gqDm2-WcQ+<1h$NBlmT%VuH`T5CQpAUW=dVVsGQ+<AZGS}xrbYRLGVfRZp-!FeWt*6gvJ&i5K=CJ*&ocFVG-k)Y;!w%c$%6XqF=Y6Z3_pRN|<4Nx!#QpaW@TB(;;{JOGc+z_aag*!wdkAs=J+|u^ug}ij_l?|FSW+I~Mi=lK#+C%f8)v;b#{G%oO>ncdH$L*@nS^zS%qjNP4_rSVGd|v18sz#pn3cY_G+2i}2UD)=5T*M1`B<Fl>*rv08r7%I!OVG`E5g=CIj@h;X?>LQ`q&-1RD`XMa$X;QJgtvEp4LaX-L;+j^AWo%Z+Wne+0EnDfWm}+cs>2^OY7;^r}gyvq4o6ZoI(9wiT&8%c7LxQ>#1>}{VV7Gm2-W+4%LshSiQ&XbN+GnbB^eV>u;5ZaI5V4jv$Xzl)dd7$1py6s_#CxZpOj)f_0c{9cyyi{cfMH4^H^L%A?>q-k3Cae^{T)c|7;&j|aCgK9*-6aM!b4|AhXTYyH^eMTcBo^Jee!JRMIwM&pfvyAOwrSFYpZ$IIRgtIwRrbA9GIKDy-G;jrsvZqaz_k=X|l?mKu4++WXGtB!=-FXk4F=lkW4r~75is5}z7f53VFD7RPiI25eUT<e=dIvow$&&(|vZ_O;;?{XR+1CQ(Vn#Qrv^&xK2_@wpG@xk@UO89HpvYhJDPW24KQ5~b1k(V9#Q<(#uFZJ+0m5u23-~FkqOZWfxPh~5lhf2|QXoqMid>OLiE0G;vf&9AY4bgh|2ISv~elJ=JUl+(5aJ&I?^xQhsTL<psQusEwjqI#@g=h_YE%F-VQn=RGhPmbN3gqRYRiY~RTgW>_yF?}M)yR5oIlKh91Y?%NS0PuS=1%x7<c~#v7oCPzBcBm{F8V9{vp}xKaW&?AhB?)kSB-H_{!sLZ=m`9M<Ri$3;m48xEINgGr!dFKO++n3H^C#wUoo6*ZWvABEs?(|x>eK>-Ua#FqOPJ$__vV1E4oc|C%hN3^YhhP^ga0P$bCe8Mfbw*NB*&Bpy)^Ne#j$5`J!LK=OfP*y&@U~FF<}(WQlge_apBS9T5E*{u=UN(ZixV_|K7lCVE`-Ap8+z=PO-Q7v2!rc@#7frNC<-ryv{fbmY32TMym{IaO5CaQ;N^c?NQts20xG!nstObH+4)H%2}x`atv%{8Qv(q7yiO0_Tq6oHOPx@V_BDkHl7@ufp3R-z@r?s5!hf@-3qFqE7H`$el&s5w(MNK<+N;Au{1VK)y@#L(%u)cOc&_>MzQIKY)CnXprb0_yFY5qA{X*@CC>(ix!HWf{#UBELtMk3qOdwPxQ9vH}Kyg4-x%D^cegJ<PoALMGwJ$iu|7FUC|-YA4Pu>orK4c-@!O%%rMcTq8aeX$S;bfh;raVk@eg#cn<Ou%pD4U6!{q(Z-l>zyvcC>d2ATZ!lxkXxo6<dB5%RmDe%e28*#h|z6E)jXq;#^ya@Rv(bJ;o@WMbY!f_Gi=($4FD+Hg0T1BW=g!xV$E{cj~!k<T;C7LSAg=Zt{x#93!<f)jO4UZznaJ(7*2jnu*R?&0tsmOXR27eBDE9OpxKaac_$7S%X$i<@ZqB-!1$iEOx61@PQ5Xcj8JP~vB+yvB{0A7q*6H#v><~!N>-$FNvYQyUwFB1Jq^mX_*kgtiHhhi!oj_Js0q8g&>hUY2Bdd``b26hc&(lIU_wVa$Gsx4{-Z-(4j)LhgUUI)1`at6FMax2Vj4R4NIS5#lr0^SO_CC=A_H$bk3To+y+xdrC74D{#ZnxclHCh!)>O>w>!yb*FO<eKn?$W1V}X`nwRpOd9JE4l*z7xGon1<`r<KakHOpM#%8zJj?|;TMpd^ZyiGgnxm2Npu-CvihZ@HcR_Y|26I3Uoq#tCj3V=o|*WX9-P@xHlzR2p4G30^ZQbMVWxTyeCI94_!2KK*W~'

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
