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

PART_NAME = 'part_012'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8b8e14ddf5104c579a6dd100ff8c0bdb/part_012.stl', 'relative_path': '8b8e14ddf5104c579a6dd100ff8c0bdb/part_012.stl', 'source_sha256': '47b3affb9d331377d3c8c382cecff91a44ccaa91cb9e639b9df6057609b62b5d', 'input_faces': 432, 'input_vertices': 291, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.14645156264305115, 0.21337208151817322, -0.08418648689985275], [0.050715453922748566, 0.4508913457393646, 0.07271888107061386]]}
GEOMETRY_BASE85 = 'c$}r12UJv7yM_;<*svjDql`v_EhwlF74@J7V@Hj>4H8hSh`o=B1q8cBV_^{N1!8Z}WA6pKlK77rEZB{)<hNY*`@Ol!_}{hex|g-S^*-~?H{aQ3pS}0&b7m3T+%c!CCVyqL%rj0&$4hIP3TMq#8y*%lG$J%?h|j>tQ4U&R`0DQ;o!6>;%izuq+Hh@*_m5#iLZiIvn7jkR{k^N0yu$}Y4UGyJ*mF?Sk73FW3h6&2EXyC#CnPc~>vaXc+P+mx)hkvpjWhip|MF!u!FaUq;QlPNzT0)V0nVb&O!eCI^jG+%ZL6-pKiqwmdaW-Q4d2{x(pC7mFU6_XwsXBC-|grn_-EJ0sMki%Zc@KqlGIt)Xuf)F$<<Qw|NK>s`)cbv^;&Z%E%l#_l=>f<ir@Fy0p$CoU4&n+b~NgY%oKmdNgUVm*Ty;UJ=4Xnn~dXH8n0W7cA9R$w|4NqhB}kWO~vsZ?tyPhJ|yiqm0$8**GruvgU}w!SN9jePgo`S$8KIg{?60m(9S1QC4X5>slU_-{bq5PAo-bh)8J2EJQDrmGE&-e>#CfWrvv(5>)1`|<hXGjeygOR@NajNI-}C$d{5^53D+gi7rwD<;5p>q4;=tMsH)W2dRN-HW&CuU?=c^#V>>799GGJm>IYYr{DEuHZ^q*aR@Axum9(>}5ArP+=i)kQkG$l#{hORYo#0nZkYCV6@@GGn^L?^ku2*Fzsh<=o{keNq0_vQ6YoJ}lPoV$xfBE3J=CoJhSH2_t&|&{X)EWPW_%r_{{Wht&j4Q9J@J-R_a$ZqWCZRn(Y4DA>VbVX-3(ED{cT)WCI!gP;cNhYH$71+4_h;xg%dR6BS4Pl0Id0@-8RwG+E{7jAk?r@C{<%7A3EDGu9DM7*kJ1m(1u-7931h|2%#d~#|1bmj&LgBwNWbgwI~8t<{%{*2?Qwb`{g81j7RT)u3}5dYE9VuIgz;>61c-kkM$YR@cj<=~6{UaThe&<@Ry}asc3+Es;+FL1%LuezTk9z89I;a7QBbK>$ou{5e)v5z<$Mc{LI0bJ?G!&QFV5FeH1FKceRIKA(x3UtVjh_T*1$K-be8d1E^xu;zO_#ij1xV2@ycxZC1Rxgqx+A5KR#aa`x_WP#vg%br!gf~^1YrQ-|{5KM5VS`4dLs9w@SY)9w77d)ysYOT$fDgw;@+>U2N~4!?zuNBgfS%j>d8N9f5D|c1Y%<e=ypqui7a7?n3Avz4f&f`23}xrB2@^QfHqtu9q#b34H5emm6|k)%rpG3W)FYwTz#6nV9dUDGz_e=T5$m@zc1?GUS~<E&i}`xQ<4YZxY&5cnf^<rU<EjY1J&HrarUan=W|BxJu)^UOo!GwNoCsF1x0qzUh5i@takWI*~Q1qi(hOQop9GGkW98GJn(G?1gSmmGhnWJLZw~eI|Tc^k}J5`2GyEH+?pI-8t$k`qMQM<Hwp2C;2nhBj0i}d<nFCe)y&XiLzcz^xTBk=0Eq~bG@cZ{@qE_puL}oA6r|-)sa&haJ^%0!#6txu|0FJ9vXR4B;R+t_(21Hh89}~-;{hAzA@o#GU^SQB6VDTk?)ZT=^K$Zy{P0n6p-uX<**j#nc^t*+q+Bu*Ddxl`hTl~<OgxSzb+^1u+RD3=m)Qy=uf>`bTW=t=M;QvlUs7Wo5o9f+8dJJCmG{Y?^zz_YYEvSe!ioUKiaey??0U={?n!6UrVy!_^H*!pZiMA_j&OR@VEKGH`P2P^Xu#=tQ&^6qxdgUWZXI~L_77~4|btW`4t$SmdtVJ2lKWQ@J+X#$#EweN%)+*6~1-A5*de2hptBdYzUM5A&%+rx4&5j{UucDUrLvDHt_vPsdayM_<FbY=VYF4!uPwyDNyQH>L=H?=n1T=<|8w9qE5UE>YI=6T8q!!8wcMUksH3T@7fCZV*@3>%YLb|DIgs0H<`8r?QBw2+F7q>D)QS*hHu;VLC)7D*L?K<v;pwVH_Id6y2opcQk!cH$=_8&jyuLP1^F9ZZAX67_A*YM9Zf|4-?#(c_PiGIO|uGZM4bwUCBI!IsXypIBHrIRL-NA|r2d=)>CYB-x1s%Kg2Zp<vKs9@)eOGbqYHeSc?<G&7a#GRL*QFF%#`DHFC>1w-qN1K=cWCtpKnF|$o^92SqA#Y7LkB)VLFso&MRda*42M}Yg#S%dUDrQpZm6UD=^;l$7MHW%g<i~<IOaEPU`2rIU)e_!n!DAOSU?mBQbwXZvwYv^Sh;Dow3!A&*ocKhhROiw)D#8n|g;~zMJ3sXRB{sIT`cCG(!6&Tb;+UJ{z-ctjp%_xF>$%gv4xht_RAvT9Pm`o4+PT{0~lpKJQO+h#}Xpo9BXT{rn~qzMi%?F`FO%PW)cER%Wa7B+qX+uZ&fzKlg1v6czt@;dR;a|Mq}y3vII@Tm9b~!8Z=S&F)(!OMdF#+3WO9hp*o&fO(;}u8Z}+_%Ist+UTAa>x}7@H^zl|VHIgl$0M7db)3aNE$3y9zJu{;-a826%Q|=v@-3|^!nfvXE56@j8K1k3uE%lC|0L^fso$kPr}oGCp!ewl-<o_7b+ih8$hX9{fNw-^Ks)sZeek_(th^4jemo=nTzlIp>F@IJZG(18{Sxk24^72}$vz@riOesTqKojpdp`K)egoyYS2#He?>C=?@nYWTC;PhI$5Yg6OK?1V)BQ4%?^z!AYue^8@hjcKJTlC2^8M(4Ouo;{U6*!#U+EXTzaSC5>HHyC_uMXGKd(CtmHZz&VSd@_1aC(DoCPF5W1rMHQ~~o{J9rkKv$}7?yf%u3$#pI8z4)(vrGAz9Yw-CJjp3WdyGuW>S%Ny|QSR_<Bd1~hTD#xEywmT*V4rS&5rp|@>+~DuomCqT-xix9<6*Nu#)-vN7QU%*cln+@vI6~P6j~$upgS9}4p=irVf`{Un=SsH&R7RbKV;yzroX?3ufJa}`<Z*L(!RA0@NJb>NdNcBlyOq0=TdymkK?fFO01JM$NKnQwY8lq{pMK}<IQ@d1ojI?o)NN-4Xlsrr*$og?>Fm_akAdl8;kjCiF>mU?LFR0>I~?&9G`0!Df{lt@_k`xSR)q49b@4B+t%~B^#92g*l+7kE5f%X4VHdOxPtMZk9>jsn#q5%_*<84#`Qerhkc(daEl!GPFeW6TT%F?1@-X#ZXBAw9`$G3nT__;4wrHJ_yyK;i?$WM?Z5)=>wIw^p>1!1_0L+nvaJ8>W@G$VY8H^^6Y*nY9Qtj=`mg;Eg70~2vsbb&O?Zm=riH)2JkaO%ISoH*v^-C!<~t4fZA=(H#_glnXIdH_l;;Ny%Q4<;5tlKpw1D_2$gk!r`y#JAI4|wdcku1MueFyKaernGknv+4-bd<0B*V8YPr-OIzs-SpWO;Yof_}5#S1gW!Z>&Fo`xncui@2`Z&8K6~o+6dyx^Vt#(>`FIYt9`i`+?Tp;$OKrOy-B5tUrmD#gFS7jQ+9PM`hhmT-c}mhkcrRYA1|8yM3VM7SRj+Wxt=arVNH(RQ4x^*8uSwWDG-{{*PoF23E!TtetQj4&QE{tc|Y$|BHQfqb|5_vo(IleR5x^llQvZ&t<sCbw67U<5=tQZUX#^9&$gJun6PN(y=}E#rFGui}~Xe^e^{sra7_6(oSdGf7m9Rlzi<QnUBvy#kaq&nKc8x{e6(;88aQ{<^4qJczd9Z_Vwv_9QXC&8#1qdTq@^Xc_!+6ILo}QR#5I=0_MWER=FVgh1%h`TCS0DUub_nnAB`G>f7BvS|TFmqP}YvX-}C7bMXG54e$+1lJw`>TJn6uv*SF}@r;!^-%dast@uIs#)$lq@3U}@j9VT1V$&i+@>|x5gLVm${fpiGxFw)1eEa)%t>LtVI8Xcg{ZVUhe_;Q7z;a_6?uX3R%E@utPnY^(JK!5*>q$HHWAZ#|_i6O&7td9Kd!k?MpTlTwBjB6z_mKLt_C!Gq2V6J%=Q)~d@n!HGFP{3mKefGe;M+ehvRvtnbzML8K=Lnik3@dEO9^Pd-SaNviGvmW*?EQ3NzG`5{7gsq_Rr1qbsq5TpR;KvM@s(7WI3+2SQB}FDSZ3qcv|1w*l&LEobXnC`1a2gja41s>wiT`{kG}oH+@kzsS}qj?cbZ$8}-NZkvdbCNxs=rp8K^PE&E)%=buK?vAiG3{=C%kZM4*}d%kMP{ZahV3#9(J(6MMwd^Ow`+CRV5LmI+2y0((@s?#70ug4_7w|@?7)Y=38i|5AQ?1!%x=q<;67Tfc4-&i<U+No{JiM$6lq&;@erS)GQNxr#-v}aFXB*srySJ`iN$}RnANg0cN`&b*kakRA@H?ms~yk6fGzWwuXV_q11>%|Mw59d2}f$tj+UvF1R=Fwg`uF?Lk)Yr|@{?xuTkaxxd>!@vNy7YtT-=XOLt={nMpXXbOM!>iKT|m2T5#R221Y^Jksh?I)&i7t>8PB#1sh@Mdv_CSq5Blx&W6AGvS<d&Fj0de|Wvs_v{C;tHm)t*1=*s84&#<2`b{vuXaYy95d|D4j{U(3H|Kj(N)M~gtu>U<pi_ziRKAe*C%ERYZk<H-S|1P6f377nq2ebcvF?B6```>r8N3C(6XT3T_+F$iBeBEyeeADVZa@=O`q~9Lw6yNUmBje6)sblwhlV*Mf-@JX69JgsR?9a6NALRb>wju35RRQaU?sgORf2M|8#lLt#o_nv%FZ<&BiSqkGbTYoL^#(QJn-XLnrTM#{|1Ei&i=T6cv}gYi89(D5!ncKQU_bk#ox1t8_+2+j{)U*?{lVFO1zeu%V-X|krHZ_os}>&e*-wB5^ZwEQ{1aeAjsMk8fHkW7{eOP~ROj?-Rve=qAuByYK1M!AJx@MIzQ|B~je3==^mp<#vW<F&Y$M-iDE^E3n5^_8`7d%F2MNV))PfGeN?piq<dO`<rKm;7O7oISkzE;z^HKk;2`ha?R-xF@K|=96zW<D@^eOor`7QMk`7QZ%Ry?O>QXi3(-X&*}|6nM-N&OdD=@s%#avJpnIgNafp?Ej-IC(dD3-vHr=^?VxRPqw)LTV~m=`ZAk<oVRC<oV>q)ScwT<mC*-E2w+PO81agkdvr8$Vub`>Mn8uIgz@JoJd~EP`rq`nY@U+fVzRKbUk?ic^-8gc^-K#buD==c@9JIZ0c(AY;rtxB{`lPN41jU$g$L)$+6@Z>QCeu)MeD4$VxYomytIy6d$1OCo4ThK0rRnP<(-Uj;!<|`2zVe^&0sy`36JrEvk*I^gj6(`62Z$@<XzNgQ!|l92klVQQgRe$fX&Iy{IM0CAp4xF%+8^iruNMWLK^u?hM668Hx)~9mz`7I#PhI73X%4P@I$cmaOzOS%u;c48?zIpVl44FQ`wb&&f(N$xp}+7>aLG{~+HcU#H$AD@`L`C!eMsB%dblqwXf}Bd?)uA^)@PtYIjg#ZVl@P&|aXkUWGulscb0lst^Om^_R;oVuJmoIHZMf;@selA1&wNghQ_Ade!CrY4d{lgCh(lE;w8QWufOlE+aOkjIh7Q|FP#lP6H;k|&TY)H!4ec_MW-c_MidHJ&_)Jee9to=lFW#*(ASQ>ZcIDdefzr*&#7L-90*;+fQC<eB7E48<wbP2?1^K|MfLdXj9Ak5Vs?kCM+a6knoVCM&%`zC`|wdW-xUIfJ42PwGSRpXB@wqH4{`&rn>PT8Lbn>`5(6_9T~~dXdYJ%Ti6`vSbgcJK3FUmIp&|32Fgy334%p;=<J2<lJ1R3NsWtGZZ^f)%xW`{hO>pvF0G5_>J~yT~nOPK{N;T1zG76vI@oT8H!(0ACO;??@@1)m0l;`Bd0SIpQ4^7pCWIk?jvs}CsWsulgZPmv&hrQgQ-zu@2v32igMIy<Z|RP)T(5qmC0qu9t_1U)Usq3a(-%Qa(;4Nsv9{k*_m33>`X3B{fb<iT%P(3S!o?|d9oivab0RdveKsHy5#Q|id#_IlUtD6QM;0rhLGElyE7E`W+;weDDKBl98T>@4k!0wDDFXRPj1il^<XIOz);+r+K}9k=ii*6xG_U<J?b~)dgR*FugG8Vdemkp_NBU!eaTg*rO8#u)v0C4)ye+U%4C0XeTL#j)T-o0<UndQvQi&%AUPl_f~h*yhpdxpG89*!dXv4V?o@BGJGmsa99d}@a!Il)LvdlM2e~jg57mXNG(R~HITu55PHJAVQfG2bvJ*pbL27Zb((>ejWKV|TN>o3x(z@hI<XQ~H4XEFd8<3k&TacBuBR3(pWGL=P?N07U{*l_797!ES?M+r1K^{aNNbN@+NFKmY+@BgwR@#f)pWK(BIE>nZ97YbMb|5QlP7WoT8Hzhm8<RVc+fwV1mDVP=CAVfMZbtPbHzR*ftwL5>o%}ty6+`h4RDZJ4`s5$TU8s%7UC7-SiaS#S$w~vroyl#qPxG@4LvbI5;+_n}K~$X_ME;gqldQA?`CD>DhGLWUX>KbnK`l!4A{QkWp}LcckPA^ul9jrW3y}*j6z8TECM(TD&P{e?DAuUC$Vzi+pZ*kcn*+{4bs{S*NX|jd$5331>Pc2wiCm2QHA8U?YAtebbB7$Rj{noYKz#bMs0L>HhY0&mW`At@`6r#SI{3dIq6Rn5rOqkqWO86*<Df>i_Ft@gEHM'

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
