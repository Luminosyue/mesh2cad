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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/85f745f8fab74184a66cabd3aa1edbee/part_001.stl', 'relative_path': '85f745f8fab74184a66cabd3aa1edbee/part_001.stl', 'source_sha256': 'b81294ed63734849ed9bf16467f48393dacbdeab0113800e84b8f0af24966c0e', 'input_faces': 282, 'input_vertices': 161, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.01830829679965973, -0.49533572793006897, -0.06921051442623138], [0.14772149920463562, -0.10136344283819199, 0.06166338175535202]]}
GEOMETRY_BASE85 = 'c$}qK3se==8s4bj3lYdP#q?+(ph)72BcY6@_y82Fd@F;1fPxCg7os?t`Q)JpC>k(nD85atL`_EPrj}Z1zOH&ZJ}Phb)~)QRS<U|UH#z4-Yu$A(YyIo{_Ba3h`=5XRd(WIjY*hUQEtvT0z>XxUJ{y`d#?76zU~`hQW~C)2+k&Uh%ywa(r1L)m*A0ImCU&d~o5OPalag(TS^i-b|L`eR{~(M1lo?sGvJ$4p&&Wzj=6Ym8x-D7PZK(+}ll5^xNbis!OOL=H%R<Zl_}7HzkXBn%tAl09%4-~zTjNSNvM;<ySBejOLgQ0wH%90nW%pgf$J(6~^0!ZzNdC&;n}ue7<)@V*j@zx}4so9F8%)^$w_MUw7v10}EgUZVdw-ir`Fz^=AEdYasVsu#_ewX%QLELhq;IRAME6ZvE%NtBRY?E1%Xk`(6VD|DXKp9I)RX~qzmey2+0~?f{je`b8TqjE(J_Skv~ctDN~Png&AJL*dGDLKG;iKhQ5>~=>vg)0`WU+O{i|20ZoT~1I_S?&yh8DNJL>i$r!Ug{lThb*sna7&byM=Uy-L?F-L`SvayN(SCYN=qBEKd*6mvd|{h-#?p-Z;%#b(|9!AZ(fSr=e4>uPow<*Af7>PDXOToFh6HLIBFvHs3cTF>^PucYEJCG@<-drr{(?SyW>zP_}sJe_qTPeXUk)6oBvXZoSCy6R(TyOa7_E$@Gv{1%l|)tYn#I+OSHrM#cJv$4+l54uub*Sg!2d@CdB=pRFO?jPxsPNX~cp;SIl_&fEj*1WqKQAeLE|Jp#h^S)5dwtgj|j(w#4SW5bz_Fc>B&7^lYN9(AeK8DVqGYR!6vu-ih$Jp2EXT7N2+R8!iQXHRnp?8m~GUsEQ587Cv%in!lL+ge9VfEv-nf;A(M$4GH&0J^WTw+@jsvY9v98;1Hk?wr%Y2KZ-({nvI_#XMUP9k0Q4cJNX$DMkIo@<14yIEJDvrVUS$**(pE?Td9=gyJ;6NnSEeji=mzyCD#8RBa{wA)X5!RsHApKG3|Pf7&o>~asvN6L)bW7f4xLbn{axR%D}Rve&wemN`p8F?DI44svUJmtQ7NSB(A5P4R9xx3b+Gw8CX2gO&DZwmj}sg%Eby!F;vlg^;Cu;fvc&%)4yghwya`Jg=SA=cyJaiRaahMrgXI&c@^{;Q;`9e0zieLl2+;_iI-I;~g2IdLA2F4{|e)~RpMb=TGBDW4-Q#T3Ujn{;(lvk%Pmm%g1#y3*)Aoe%aip4-ei`{r}f*|z9Z8h3q>bop$oM)S56eJf?Sze(49_I^aq->s`SpPh6KI<o|lt{f{9=hg5XuhgY$BZ?N1zHg0)qk4W!^EDbF_Lav~(q*sBl&5y`&DUy8I@?i5y4?EYCK~_34so<k`GVGw6?)LQ>a45n<(Fulsu0pypOaKiZB0|^H%)zpbjf!UJ(sd^Af0>4wMY?XSqbTE#YNh`s<WOaba}&N(lzf4im%RXFV4-dRy7pA$z*z7R`oXRA7yhC>8vL066N<(Ce=afxrcNmbT|3S^O84Ho)tGpS8W$WJ+Z!qF1a5kooyHEE3NxM#DDmynD>4PeSfe?X@}|ht0ykdyi?tFQ2$+-E%f^rPSNwD{|%i%XI9bwQhq+^N}%oU6bI|>tSiICx@#YJ9ijZ2$@IL+gYRixHmn`#TJ$@jA8KM~-7VqaLQj3gVSSaHz9LRg4n41G^a*tKc$(0SKKc2Kh_iTyc#mJps-XPS?~-o6-a+h(GxvtkzPb4;=@#ZAzFWe)=)EBI8FiHOK5tPR`+Je%y!~-3>DuwP$=|Z~OR9r1XM%&Sg;wT}UZs#O?P`9R^y>$<P`(v~q$`gx(wVyteHW_loFtuP=Zf<R`(4@nv+!ReJM^dKtfN1*B=@&Szmeq7=k~wQ<-#!1rMx4QkELMC2Fk;IfY5`EiaaxJ?4$Ur28uY#RB?`-_oMfX_SssY9|?8X7ix!c(k=h#M(64u=Rb7&S3)<=f7weDagMH}K9r32*V$7-FFi<oB_Gx(AIYj5qj@%ubv(zMbUSp-ubOoBOs>QEpcJ1aUAq)c=eC4%TW$EyW8%52;=6YNz8{u+Pr7tIQk?TR|Lw;fi1;U?&r%$`j|^RVSLhbJkK|oX)l&QmhsASEbQj+(K0}3mw<pzEdc&W-bL?eNq_gp@#5ut3xlnz}&yg-AeoVTIed?@BIG?34tu)GK&Nb1`@ein;N@#1+rPggkeYOVE`^fTP0O{=hYr=oQ`_w1W&$oqt0?zYmr$oPnd`G%6z=i6g;(I{3<9S^4#UimE_Z%EU`5f*<y4=iL<XN+PKKak<OgeigbnVH<=$ur33=;ltb`|@#&)cFOzLH3ns&~>kV+n~D=SIb3(v=!Fk^ipAl)oBZCE~xo*P-8(x3-h6wfu<UsP1+;XC&)=5r57Qao$#6n@ZUGH=(Dj5$m|)Hs!-?t|!d?(xnr04k)&vq+4#CIYaS{_j_Wx@Mm{KoL{eqerR!?bVZ61`?1}<X;hDucS+aU$B1)gl(wZd*5OzE{{4RoJk*RaZjJR{^-~f|Kk2#1{|v1ACw*Ga|LP}wcWd|m_a}XSJ%>KJy#O3);u6LjpEvPk7;{WD@p6ng+Q2vHwh$V}<tE-2V~+hzyf?<Zk%z&<F%Cx_Mvi>E0JaR;0?fS(SPq`6TOzbX<YDk<F@6?#7(5K)FyvwI0T>TJ4hEl$@nqy-@LY^@F(>D3sAcq@4ZyD897Di427$K$T7W^|iHI8kj0TU!{Sm;f;CwDC#$CZ9U{=IS1UG8H@oAtH+=^IF1KWV}oI){f1O7BD6!F5qjhb=n2Mh%dMXY|nAn;t=6AkPK-VZ*}zz}eE-Rd#EA%$_yfY^%k$9W^5A9y41KwuB>K=59O8Gw1*!F_?fz<a@;^M<;0*3AXj6P#l=a2N0f!0zA;!0QA3!8tYo@1$E7-I@a3!1;A=_;7Rucg6Mku%@QDnj)8`h~t9%IX(t-18)fI4CA~#&<)%TIkks%G5L2v4Z7eNdcr!P1{{OIyMcFy1)~Puc+QSMe{g^Jbi|ql;+X;ww<&av4Co5p80Zaj1@}fgqpvs*K+Il<+X*}v7yupsf6jT&@K;DZpa*z8@Mgfr!JC2m0o#K6f%gDD1>OVP7xDRgK0se^U-)o7PPZK0#sFu5kJfFDZli!pz(;|n087DBz!w2Gfye4LQ@0tg5zsPp%hqiea3uH&-R9|50pol<jPpVm=Tm{tfmgt<62^HEun@cmd=-rIc;HlUUX$s%#pyOdw}HA%1IB^J!Dkw<415ainGc)>J|BD~unfEmb?1CA?jH}F4?Z8)$HO>J0Oo+_Anyd^IT$$(#yxSs1n>m-b1v&PM7N1p$B9_yiO`L8=X^Ab^B5+2B?hr#ppSzML2ZU$j_Fumj#)q%T*iD^FwQegIb{MDfe*%WP618;=Y6N@R-)S^-O_Yh3d{%3$MvN!&es4{a24}#J`AxkfJ?!b;(7)!6Fd`nW&pEId=thzpOMIAB(!{3Hgd^^e+g>B<IV)mFmV;*BqsLPYTyj;)!@ZI6`W%wcrxzK1Fi;Njq7<Z&es7e!7Gs;=dp-26PO2{hwC$eS>U|?c^_1;NBvO&<UV|VM=`O-(}DBA=fNi(SP34FdsYF{*`xi=c@eM@JPEmu0LFrk#5xTFP698`ZKG~4V|`vmEmiPJ;70HYU>R^Dco}#OumC&<d=`vzg^6>R;}T#2cmd{H0^_{YlwT?85RdwCoC-c$x5c`>2;+P$a4tB<mrQ&##vBKk_;8E|fj<Kr3(hgp#AjnX8*@h@)*#F^2)=89k>HW==ln_CTI$vg#(68<ymWg)H&0+Ia8K~&z?R@1z{i0t!DFLb>b0o<SO3a=^r!HTBZq(NI^XH|bJ2X~B|X+3KOSSFT={pC{y|WWHuq`%gzR@@I$nb'

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
