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

PART_NAME = 'part_014'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/11ad3b320ee74185ae4ba26ddc910b52/part_014.stl', 'relative_path': '11ad3b320ee74185ae4ba26ddc910b52/part_014.stl', 'source_sha256': '7e47be9171bea445276629381640f93e0c2d7e51a99c8cfbb24331e3dfcfb33d', 'input_faces': 416, 'input_vertices': 251, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.053080759942531586, -0.2938106656074524, 0.021691283211112022], [0.1424267292022705, 0.3925711512565613, 0.4538463354110718]]}
GEOMETRY_BASE85 = 'c$}r03v?7ky2m?8W)ct;d5G5qM==`_P<e`CqyZCz7zmHNAR!4caTOoPOI??BTo=8r%XL{+R4_1#NkAS7NdOg069`Nu1bJ*wK-R2)%0d)&Nl>qk?e6c_v8&;pbI-k;Q~rPTubQf_zOL!%u9%v9ahpz>{JU1G-GAbWn68>;l}ofv+ML1}v+ge_oO#p3)1QdaF1LN_pQ8)Mq@|>0MQL-iC*$ueoLMj<{`Nrp9YurVdk5l+9+@#~M*hROkIcBY(DIY=ADmfe`ZIr(KfTbb-_UPh-`;`#J$nb{2L6x#+L|F4MSWIPnHq|O_F0;jTe@_p6<bkz+t(t$7QbJ+kmc(|(Y7CmJT3m@ImOcdhqvthb?@7LFthYEyZ^oO#IGG<``Um4dz@fF4*fTZUlUa>ewytEBa3W5ux;*ox35Khqx9Db5^diI_Y{9hksW_<YG?6lACx$&N7>`(Q=^%8lkJC+o_)pbH%8XlzEQAYndKY#%`5GA!d+~?v0ulK_)WI2*HzoTUVBxAJ#YST@gvVk9tJFw_2xIwKP=;9Z?N;G=hxH!4>C@qu)^&JBEOY9B&AE7dGlAwdV5IxH9gD4pC^7~m5ftYT%q{k-qOE1U-FroBlFhYE&T_bl<S+DV*6V7+r9R@`8#Ak<R(fUB1<HmVLKK{|AdvYf0oMl=PIkD|3De1ZnNa!`|Aw1@9dx8_g!s2I3<qpUzYI;1}zi6o5UGzE7x~>rNlp_vy%V3?FUt#{D*d(kvvRkztX+WgVkxWAErc0oRK+lU78=QQvBM!<n#Fow{L{wr2puoSM7Ooj;xS=JH$^ewS7IOVTF5qW9zjtZ%+LR_jS|;F0u2k<y6{!pw5sy{Pd3D_O-|?S#QE1JO4)Z8s@E+dBe@}J<2YT{^7Isb<}r^E0_Mo(m(R7jPp~(9$(L%Cw}cniKjlc((P-t1C{(}*>j0MUcHW!b0q%SJC*N?J~@qeTI_i8#+EJ?KSjogluCYnI%Oz+_!`Oot_C~*+T=vypD*KYt6A^%wc1;ye{}+Wg7|fnvL7O|8E2r36aHzh%>R&le<#H$>(z!ISmgHguus-octG~&q;AB&Lj1%7FN@#V_JiRLlIM|0uUyD?zAr{rbD4XbP|E_z^Q5LSxxPEa|Ne4A`X4Wo@5@5TLrRy$Zr}O7JJ&aubwtLAJSA~zmu<E4oYf%XggbG+T_F22tDf-}h`*~=_J3AQnS6hP;<uzooLO7wFZYMM+Bmzvky%{kzV6O_K+l}dIC38_h9%i~(=z8u|JniKZ$BZ|F>^L~sFOVWxK!4akt5@Tf3(MMy&q<zN&niR%6heogffY5y!gA0SGfH^t*)%gNbe)#gfEtOCTv(DejMxlv*iC=bCuh7e(yr#eQN)3S7o0Y>D|cBcYBrZdwR6(H%8u}{~^UU!Z*sib?fB1r2kMV>m4rfC$`x6G}4+CUyGzvD1JCr`bQG+n`}Q6?k@8tr^|gTt)W!nzgpR!!HF-)IQ)KT+7EJlC(f7t+|L_-TrKOJ@KCAbXRwkteL@=XL@E0`IKDISk5a}r#vLz_JoHfV6C8J>M8=6$_sO{W61lz!N<6`l^84)MLEp3S6SuF0zmfaHo{tpY*!iX0SNAq6esJf0+2^~5tNm;46Mt{JBjU^b-k6*5p{%d@klWX$y&AFCyM6INw;#+rT4Rs%!R;R_eq#Jqdz^P04=Cdl?cQXMQ}JShRS(>=?ez<-*YUmU(#IsfVUM$OgZLjluK4<ndE{rm?HgkX-nd}iQum8Lx0|dt((AC|KaeZyt=V(X?dut3_ImZI=^wlO;9X6I-T%EVAKCL}EPvDPUv=Fcdp%#x-Xeav?Q2!nivRT*#drGWH4U@<Q07tk2W&rh`k><LRXuFK@l*#HC#!#n+CS<8x35=SZ~NM*rp@;JlSWAYquphl&1v@j&zqEt-_7=&-`Ssi>8~~4Cij_1)0F;!mgg1U`0N_n4>fm_aV9TR;xtZQ^?}=W;xtY+Y*zX+zJ9J)8OIqvcsADd1KHcu_*+&gzSF<)><{+5joJUL#G{|NR`H#9@=n!nR{A^ZJ-4RH?YFM??6)#bPXE#i#pC$ictTSON-vZj$M@!^wZA7nj_=Knp8JB*-??6n@4a5Z+~sQg?1!Iybw7l1S1G=;uk^fa%DSBW>G<CLnU~+O>_YqB@xA+BpE{!KLf<dP_kO?hsS^~x^?TapxP3qN-k(ElzL4J&&;8tJb3)W}|8H#5Ed4#d7kac`o_9RIFM4!4c`oq&9z}PweedsAF#1Xv$Mbt<M8`>g&+nrV-OKj9zo$lY9~sB{yX^Sh-{t7Ow(or&aQyRr_wl{Y37YRV)}=nTIKKC}rPcR7pZJEbUiEp#@x9MWns2D>pZDB_?|tsleIr?y`uwK*MoE9~^PVq7+C9&Qx^FD&QlBSv-vk-Q^ZXg~Ww2iLc{S+EC2#8UZP1s`IO_9o&{sfz_4(QG6_Pjgc{}90kA0;+pND++a~;*^dBZo2@jcJ~zK6(z=Y0X+`+m{rn@v3Gdy3b0-cuTVk169g?>n0RN%E||H#xrdy-D*wg|EJUY5u2W9Pj%Y{(0|xPJhpPU%>wiajNf?t-j~IGT@)5TzBXFRP#T_{`9=h`d?%m_5D}(FJRw#-lOro@6kd3%dAU%9}oIpB_8$tJ?LM;_4T~(`-`Q&=X@aOUncQ;&J%+E<;1U^KN$WJ#!=5JLjE%5RnIpJ|2n0=v#wU(bADp@%b8a_KWX$=%6|8p&p5vKJg3pWk$BYepH|;<UZlmmtK83>^Cc~23;WG;P8Cx{Jf3qceDC>{7PD2kKRD-OftVVuqvt#=W+(f^bN&{ymwl_A<K@NdSMCGOIo{8{dL9^zIja0lIp>Ow?>$#EV!j}s>iMJ*b5hB_bDn9$G%5La&OaUhyz|nSGvrx4cXfR4xocz0Ia!zI{8o#Ns+RSt=e>d0=xWKodT#9a=banJ`o;I0KkKm_#P^(68?k-qubyukvHh#v`@uO6Z;Tztyz2S6)^<p>d!O6q?WxLN5r(!Oyh^jGW{EZbQ<U%e6N2XSLofU%g!>2lul|HEpzomn@1GD_%ox5k%RkX?;D4Cq5cNZN7H^}zAN>bhX_gi63i>&0wXH(8z^mY0=%?^5_&9nBJ`T5_-@<ifIYunUh|^+&wr%Jk*ox;(_)YpbY_+XLSHWxH?dUFeJKTUCha2Fp&=&YB_!#<6ct1Hjihd1$WR_~`)p%c%!)kI?O}{O~zn1l^Wz7bkvBo`zegl7mo`k=qzJ>ay=t+1jYpz3&!JpFS6nffqeZFJ9?-=_V+E3!0#Q%=9RI<)W@^X}X9%If1@_39nPBYJG#;|y|Sw1n#LG%QC)+}FA{}RvQFQ}hE&%y`H5{AR{bNmWCi+575fJ@Mga0&c2`Y!x7yc_)l-fNZ`VyPici~mO37wDI;6~}w<d-QYIYFm$1!0X{sv;;1NSE6sjmPTB>n|cJUK@Y-b$l<@xX84F%4pTpj*Gvu%le5G0+e!TES<iab{5L*hjoXBtfcNp)CbSveNqr-_4_?oj_o6lMM*6&q?r>e7&zbLY#y&y&KD>SSpR<+&tn&bQ`4@StVa}E0v4%NzFwYLguy~zW-Z#r;bPxQQS?a0R<2n4XSw4h6qrS;3@4)ZS?y%JsLf?Wz@DlWOcnQ1|eFI(!uS4I5H<)ELv8*Oei?`DDAzBYx@hpdz)6Ze6Z5bMZm%*>0OW@bwVst5746i}g!E4~v=w|q1a`<<&5&pm|Rn)8S8p&Z5Ijf@ITg1PN^(<q}TltJN?qAV8a5<m-E7}OZMg4WO9A3tnH=wKG*Xi>HTIRYwwaiz`*n4O%$1BILWi6Xn=O*&<cjhW)zGCvYnmNjtr;ITyzQ`<5W{E-Dz*f1Ac1t_J9jM2ngJ4T1z?LS$3Gf(n0(>=XH=$$TOKIzj-ULU{)&}kDinR-|Sb8&j9XtrV4Yo8LPA8s0%y02MXgYioZMUNLz@2G}LvMxK&~^zL2glIX1-%4rOHQvu<6)}|rrpvWa1ZJUXd-+wvE7EI!_GCk7;OvpK%Fr!qkb9ntI-6w3v0X?y$5c`XD&srhOMzQ=GVA>7rExp&~|V<Yq=5~4979|CGf4(H9i}KUJ9E}^jde#dh8eN1zY6`+Aa0Ne(JGkC)m>du%*|-mL{2{AKah%2)v1C5<HBy(db0DJ8iwt(XLnr5{soh;Va-y=r3SPbyz2!PRwud-KY*vq%94-8y-#Dcr*>R{Jz9C8m}*L_9Dh!cos*KQy&@&Tjd(sE$s$(quvj_9_~qOzd&`^xn}LrXxJI6J$eIt1N9MTKX@Q(?1|nD58yMy&=IgTR!8RV$o0G2HAhEu0PO4)A9@Wup1J$NY1BLN+3x5t_(ro>@3(iNqhPD_q21E|aB+aT#l5LpnhaYy98Q5Jp~-L-ZMo<q*z&W@k_qQhABr~$&346_N-UP%1^0n_qqoDBX22Q5)0_D%o{VO|xwK6|C&Ssa<)BmGQM8RkbKpB^OGU@RSCPxEXaKg#5ZW!h1HOZL3OXFVi`Z^QGvFH;_m}8Zurt;#(UI^->RD(CoXQ&SLMOxH_)I361zTg?!u+>z{cd#4aSJ*Q4zQN4=n!};IZQ>Tz_;+(p=c)jXS2L&mOr6ZeKEQaUJSp2E`VQw7oji0i{QVY^Wne1FQCuEFTnHA=iqtpQ|L4BQ}E;H)9~Z)9CR)`2cCsK3D1IOqQ8b`!n4uez_a1U(BHz3!B3#SgP(wd=<nem{4DyP@U!qA(Lca{gkM7c3w{ZH8T}LNTuX}|GRwVYnTAe<r@;@S`S8Q=185%n0Q{g?3d~XnKL|g97Qv6e)6x6j>F}fIui!`F8R-3RYI4*?oi6^L{ukt*{{^jw4ds7G_I^@5c65I-$sDWo5HdA6+WK8EAC4}vgL>M!+iCv>jv{L}'

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
