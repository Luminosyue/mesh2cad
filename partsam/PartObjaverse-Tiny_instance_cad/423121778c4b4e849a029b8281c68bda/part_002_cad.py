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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/423121778c4b4e849a029b8281c68bda/part_002.stl', 'relative_path': '423121778c4b4e849a029b8281c68bda/part_002.stl', 'source_sha256': 'ec233f0556786e4b93a56e3ee195da97e6a2b3ef994b4c9ad6ce3b3cf549c0b3', 'input_faces': 294, 'input_vertices': 170, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-24.160306930541992, 127.92284393310547, -30.784387588500977], [23.27977752685547, 172.69541931152344, 16.1780948638916]]}
GEOMETRY_BASE85 = 'c$}q~3v^Cb7RPTS@d$~8Xa$Lz5D_8?qC`Ay5k!&-ilmAg@@QIZNKh%^qNpMf?|ObMMc0~o41-ebZ9DDIR%@p9n0oY<Mb~JDsz;eIUGts){(m#KnVGd_&19{!_TIm}&%Wn%&pG!?PNsiAxF&zm+O*K&S0{&RnktR7aBX^F+0>GWh2@FQO|J0MLc!IaPp*7yWOh!TpEg~a8COtPKCvvWrykd<s7G9a9#>RaHnlAOx$&iC1%-+a%%4<V=;h^4<xej3+U+}cPfpOg#wX~N`v3SB<ZXh}Aijs~mG<2yCm3F7_=iO(+mo@ayOP?N`rwZ7b*QrS#ns@(ywCF$*Jh{0E88s25+1z>TyNVoR@v5;LEz?s?a1TVnHP<`pIv$c&t3dAxZW*uQ(q;mJ;GlP1GnzA>IA!FEVy<#dm`fJr`LsjJP+LISRw8F@wy-C-FVOq&u@MR?QxQK*F&DSz6ZDKcM*Q;P7L~6`i8`>xhKy(7Say=4ek%_sXmB!LqFLW_5DM@jc$9<9;3~*X0Ypgmx6XZKNxw;HLoY5{{FAQJr@SbxDERRd9*<%!1bC3CdTLIT*PY~%Oy`jI`UgteZwHrMo6B49}A!Tt9xqPjK#yijpm`qZw@_-an>&llswhTWL~swf#Bo(CB9&;jKimsy24&_1yXzCU9?BP-z*WlVvqQvQ_(NO`k@K>QMMf1x-?(%SMEW6XZ|8^^UH6fJ$b!gJGUz(PrF7E|DLP|b5cIIJ?mrS_gtA40slMo!S#j71>k2g?!T+zAOE%s#-Z_WjDs`wPzS`Vdmr4G<B|5S8=ipt$Bqc!)dl&jqL-S%|JqF92X;$)nxB>NT2ct^Ob$W3_FAuS`2W;do}1bL?J@oD=!k3HLgF)D#dEca4IMEqJI-L9t-Z6QU&~G)PEWDHo&K$m$Jrc&{95it;d_^%U!I`0t>K?D8{C|BTjuL>0oH^0^C_$s^WZXR=gt|?=wGwXz@43okzYUX#m{P;IL>>r9+!S1?To&Ub!=uG6#n)+8Rsqgn}FZj3T`!RjQmF44UCVOy<GTL)iTb_4RHISDS0jh$@-kTx()K(i2}F7ixF>KXo`9D>^qPIepc3r=jb53&!)d7d|n3PjaAoWTuz5!J=#6_9%ZynMLUKx0M~2Ip#9p1yY8xWVpRSl`^S=@$m7IjA&-7%BDnEEJmQVuI~X_f`faQiPr(|Qmr=u7Drq0t0PZaN0R6HL&yPiWU(E-%*Bz7joztrw`Zu#2^Kb6{R>uFLKjzCG+7n#gRwMgHug)@m+Z%#=?mQ;#Us=%({W|qI*0s|wO`dyqLwh{uk!#p@opDEGzPgk|qW;aj;QEV8Wxq-)>xq7*z5?#qaRlvjP92qXKIKGv@E=<jBLC_<>?e9fHMnj4gm^u(CLZH6;6WUCR0_BjGg|iFS?9s6mx7VU86DmT?U;4}{m_p$mH7BcI1ikp)8N{QJQ?SiKVjU=b328{o{)KoIT!<(*g^96PnPwQl_m3jI0)SS{)&uGz;(3KDZYX8$IMQX_?vz3TsvvJoJ+BhXs0K5Z3{g2=<>E`SL45qhy8~aF+SEeI=Inlg1nFRBMFd6FSkKE^DoLeOuU70HqV!Wd;Z!2@#d<7h}X0taA#5uo~vJI*$8<qY{C9#tQKyi-@c^Qt=={b+>?Gz_L-Z9WS`uW2x&KZR@PPP2D0y&XRr_H-(^U9)?Mz6=iPi0-2Nz8<|S%h80_K|62I}+a-P;)mUC^*_STTQELm4|&UAo0+Y;P7eh1vj-;Mb)_Ebe-97?WE0H5?n>?c}Sq44>2Wghp3b%MX{lUS#A#9*|?98(|foj&<$ON_&%5y)d^zlHhIC!7P<_gHAB*5Xhi@&%-TJMZ+6ao$}g33AY1S|CsSQQ0TIT7hw}UN{M^jqQW{hTkaMdz@jr!L6-RWnPX{<6N_g`aO*J47rCm<F=+@K2`=|U$mpsWna2iCGXdv&oHi@7iLMn3Oap&{pUa~xbfi-;c+XZepn8;6a2l5&)(y>hZtWpl{_t`%04h{CH4hvWCreE=9r_>-!0Q|j@TE2!8Ok&Sq}m67-!?Vs>T?%;wG}rkKe<-;T%i@_Y~_A-{x-^PwT-mA!yHpTj;O-WjDOn#uImg@tpSDuRc1Can|zZft#5H$Zw=XVxKo->Ish;B=2KsU^4O#xY-c-508=Y+}8@@uZ2Agu5Zo)*N(p~_tEzwg3!+4Rg!<~c%0YHH4pA_&ZQ%AUYt1A2YCu&z|G%BB99R<q!;oG?Rub(;vG$J^KM_6_Zt^KP+YU`NPN`@^jE*q^<%{i|15dm*LFhtjo+O56nVZ{C+o0xJ>e&teBKBBJS_7vvs&im$1^99C#Jo;N5Q)=ZgyFVFBG?Cm&*Lk`yJ-jPEH0lcWjq=*&itDeBUW>&%=L~_b%YR+*daoJB9d~R<dq4eT;q2$_+lNxZd_T*-s|?R?goygT7MSG1kaFKO_Dj<nLc{4(-2GE&IcwV^`JwZ#UG=qn%S^UoryMW8E6ZBZ3UqyqKI9t$1EA>{{!=9(xzO_WIG^PHT)jwbr5iLlt=Kb!&VR9E#`ETIc%c4Dj0Tg?73r&fD7WksY1`{x9#{Te;xA_f+@2r-wh2JbbU6aq?d4dAo6L`1TFwkn9^)gC`@=5AJUs?r-L~mbk~&-aqYi+rfSNt;7A+dTND^cGTLRty^z``}T7W_j7A=BA(+r7n~?L7wp(HaNjwi`_7TCw}AW39jBk1JC<J&=FN9bIXtJd&f{_4@tvD`2+z&)JJAo{d2R8$)<aLrdA?lEcXPR%@5b!&aftKX6Gq8B!BciZ?lruJc-G22MC)-)&huLL9Aihrj<9Rpm+YLL;J*8n$@`UFSq|>Ik9l|>vu@m$^PKlRbF|#|oXiG^GVXGpwBMKer0u;YBcAtUi}z%Y_qzbR)^~yJ{Z2uBey3RcPVsoZYw(-}@?B$}mhT!PAfy|{iQknPzbhT@_bKZ0`&9FNpL)NSQJ>$-8o!s-cQ@ks-EFAv?wnuzS`oUUe8k`oO;e?T7OoZLyMC%rQ2qJjzyGPCB;~*QsiI42%K!UQ#p~WSyyh*hdW+JxyX+0#vc+58@Rl9)DSanx6|<gkud?2H)=_K?nX0#yatHO-C^u5y$hun@vyDvIn<%$YUr*mE%1zWa(6^e;-auWk6)t@h?KNb}C>2}kvX_#n_$AbrkgsL^Wz@IO_E29-UCDLSm3)Oo>C5R?IjX2v(Wgo^W7d)TY$X>_S8@TFidjf~A$?WMKaX-L^@a4!r<_N95q&c$6|1CPNj{(PbI6oEn{p2IO3G&`=TM)+x)$Y9>OS8TN{f0WeI<N$C3RJAF5{MRUVOHa6RA&Rp1F*f#e9lA!CcQ$pG$uM>&>M;i*;YtWG%c*dkW)B>L&B3n3as%M12+WDE0#RX8M%A&1Elk#l1{>CH*zjYshCYuF%!iLNeu_;j)V;XHYMoZx~}=qOXR!VvjR!82eg4mP7k-_Io1P<BaX^vXwrRaf%s~KJH^f7&DaPXp#-3Kh<TYlBpbBU3OR2RdEBo<q_(sw1<$TGB)02D}6NUtJo6iiakYJ=`*P-Hi~Q@?a^cvj8kk8b;TCYu3%CAr&)aY7SQ)RO9lNe()T=dC8x6}eG=u<)TdKEN0vwXX+9^9KE<A7ndIWi9!r_!((_!ll8><{{ZZylXWS@`O}cA7(iyA#gDKOgKT2OO%E8nhrR+hb;=5Dt?(!*_NZFlw56bqe*Nwh(w#R3;V_bK#c9be6)@8?%#ZynDuO;=Cd{#U9!^qlEk7eB^)SI|s9%kM4)LXMCJ(@8pwm$XxE}xPODC<+N&-g&fCe#)8bHxPGjwTDIu4EjG(wkGNm>^0&>P=n#rj&}eAXlsnZKX%iR(cBcC>F&Yq70&*LSJW=DDq7DI#X9NiSi-p8T2KQshpuMJCrfX?!=Ph;>sT6EfZ)DB2)ej)H{%eGQU5iAN3COHKz2Z?#~#F^Psuv)N#dVv{g(!+D)kY>IE=HBM)FqE80qrr>$gH>Z$}YrXKYG`a8N}I?|_jf7(j+rap{%f5s^mLl#3jfWC&5G1OJvG{*L(u6%V_ry=_mK&E_=<S~qoq))LB+99sG%GZdcE`5#ZQ>?A4UL)!e<PolT<!eS6LA@vABB@8RO^PKjZa95u)YI7SLfSsP$Q9d{Ir=hBTlz-QKa#$ltT&Q=r5Dpy`V5zy%Q_>;a_OH&Tj?*+&Lw+>rI@@gef_BSWBbOCKSP#FHkE7|ZKap8JVXBg)=~cPl%?c8HlA!UODXFnv+e-u3AFRcR6U(Mne&lA7D3sJJ{6zMy4kdK`ub32Q*TCJ7s@`=$5GFw?#nlVd>r*Iw9ClysgH2ks_o_E`P9qF)fnVt`qc^d|4;ui|L32DjmG^C^x8Fl`T6RuxyzgDA0M+hnStv4@xC~9aQW@5PATp0?4`J='

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
