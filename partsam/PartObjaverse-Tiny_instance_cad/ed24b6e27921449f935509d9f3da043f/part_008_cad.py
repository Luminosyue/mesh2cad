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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/ed24b6e27921449f935509d9f3da043f/part_008.stl', 'relative_path': 'ed24b6e27921449f935509d9f3da043f/part_008.stl', 'source_sha256': '4f765ad68d658a8ad90211229f026a4b6a50eae3e46bb887645aff4a0e86e5f7', 'input_faces': 196, 'input_vertices': 160, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.08794846385717392, -0.20602527260780334, -0.07551078498363495], [0.182463139295578, 0.24858134984970093, 0.07942015677690506]]}
GEOMETRY_BASE85 = 'c$}qK2~bp57X4sEF)C^_u4LL3j4QarCDLC&1wqA86JZdVC<J$w7DYz=2DgZU3J9oRi%U>M0g00!kslK^E*VW~CL3nb*;9@&)F@0c8Zz(Qd)jn&da9;os5*7dJOBOr-n(!6T||VndaSF$e|?n;^B&CAyc9*Ez0y@li%&5xUKpP`d__{ao6?DV`Df$Yne%2uM7k+yN`}v(_|%0dJ`)T+&nArX8EWuJSear@iCYo7GG$S`^ryxxON|$PYGPbcyeRwnjU74EFlz8n!#czN_}5N!!E`nAY`yGD<@8dc<mIM4lGUT>?7!Lnv}9{k<IB=F-I&RKtXeHu{b|c_$(BnkuS(WB_C7<;*FANN{8qK>KYXuNvL2jJLG64$ll@r}FH`+N;hJPqKc$AsZAVbMO3UCQk`3mi)Sfct`XP$*@ic1JFts!LH>(O|TrIxtIQ28Xv5NfBsQ+bBA+`5@Is1CwZL*$a)xlC4pZ+-cs%Pv~s^_5}Cja6Gl~h0a9g43sZm0fO$7XZ?t`4e{zJB8aYR7ba0{dUxtdhPptV<d7tIfm;@}E=ds6T2$H9ZfUSWbS@<9U?#rnaw8Il#Z%J`ZY`@hIi9uIdE6-yBK(RJN(qAFU{v@}U@-R#SgoTt)RwJ7dbo-xZom{WrZx{k1-GmBy!y3Znd*=9j%f&mYb`>?#kYMMEf0O2<3&z8Ytu{u_et(72T?t!du$^aRSI#Xp>V-;3m{bt`EcT9*#&NA%92IG^m|JT!k`A^*cHo{z6GD2}Ohn#DeEhR^5LP`g|2mXJR*W*^PBwwmV2T0Z3f`P#@+G@gHaa*Ez-zPHzYJ!?^3^jwR(w%30BD8mAIeA9~aU9C?;Kvur}yjab=e$;NEd&vK2GOve^rk|lW*Z!VEeqghO%Cp~~`PEaV?Id3fGgG^z3gtzMoSI4gYA;?#G2f?9{n_`|IqcIl_tL4IXa1E;{_=9lkD6wzvG=u>?`XeTZzWTH9@Sqkn0&SOplSy{x*N^6rF@E`uePkDc{<qDA->`pO?gwjW>-1X_t;3|)xRh@?NC4a{!yC0r<U(@@Q-w%eXFm}Epvzye2&kH?}AS|_+{x7SL>N|#v#t`cq&^9+OfY(neQrZN<;q;ql-KnR_{wQx|kR1sHO~~i+R+3w7g_=G4FbGD4mzTStsT+@}1X}vg1IO(ZxDc-tD!+=wjWfPt4%`?7YtJHsw><X<ukRdvaW-eWbl#$-Zshoy_8W=jmNUzSBO{{#wQU=6c%KT6hlUZ+Qc?XFCThw*6ZXxu1NebHkMQRxy>G&Kb*R6(!V;)462%<+H;S$N3x!Z#qI{r*ls?2OOia(>ZDLwXH)q{~hxvzS?~LnEia&&f7;m)`|Xn_ezKQPUrR`-#3+frK*<ZN3XwJW}koC`L6}kogm-ozA)VGTu#2z{h}2opCtdT?r^VJzukP&Ro;}A;k<vG@2~MkDqQ8?)cs>#PfquvrRDHx`}L{a@}qwK#>f3@xar61_XqB$y1AI{CvE+uD*HS?y5Gn1x=_-?uM!_`r1flV{JPp<{Wmvo{LpS^T<s%kPAvPG@7>^a{UyC;iPhL|xasg6q9xvBe`z=RZqZY=(RYjK&%Jnm+?vSWIX^T~|5Z1&#=bwc?;<TTn0@E(sLDu=v-#V1sQg7B&*O;rSIJ+}M7}bvFP{&0udtu&euX&VeirqoT?_m1Kfg<H2Cm`!-R<`puZN&Nk>BuXF8NWz*zaNG{MB9GMe!4-v46ph{ia<sF8$<I_CIUOacq8@8MWj;TtL2d>>>N9&$EB~8qKGc`+&}E%WDPf`&V)NK8D>?e?Tewxj#}I{mH9&H1ACp&yoMyeaf5eQ9}F9dOM<y{Pwr$zR=Fz+eGo7t2s}8<{K2p`WGY3n|gUuJ^6=5(KytK2Yla6nxK>a`6tvL{p4J#Zz(y&evZcH(WP?!&da*Oeqn@}%9RUdQ~qy#&i)SH*NHa<ujKXj6Z|&hTebe1sQsAHZ;~I}fxiom+*wQeWpFb43HRvSGL7)3b}jiC>>oct>qWhBVLO$*i`YN5n)0Rf+_aCzTVKZh(bl}~4sd+s*pKYr9ac>BriT_#`+nyxke?KNoY(b=OloIN1N()S`5wxf#QStl#9QQFN~Z4}{hTlP);8DJU(ffkDKca)jeG4E<ZJ70y-n=~-J)~JQ0)FTwR7dpTNJ;xn$8KEuNX>~(R-&0HqiVG8ODCdPaCP-JPYMhtJuK)NjF+YYWZSXZ-%lO_VZHM@6gEO{oCv0YYX@BzP|rH|6U09xk&YEYx#G^(J<b>;{wUo_N+Qj{omQVi^|4XTtA0@C+Q7W`1`FofqeDcvpSXQVoU9P<-L5~_vQm99DMbkv`(~d8|nMrTC$Pje0PNMX1!lR_p4#TCh~RDR`Lx&HFW=}SqC`I#9zo)`c9+yF)gfOf0jSz!8)DRou%ar`<7+2j@98W^Zx328RPnx`{`GlP5r#^CHr+cf1iGsNawS%V&Nr@vzza$X3pm$fAb<bpOly+8kfa;8T(zop?gg0GiwX2tNIM~O%IlmUs{q*{f}DD{?{Mj{A;H6t<{Iwk4}4u-ao|kExo5+CO`5zeP<XlKBc@_&W5l*&a<B4_IQ0a<?&t=`C3a1&99cd)MAWq`1QW^o3@5ZPqE_#JjJi~ggCpO?$VThHg^5feevl3?x*|svH$N+_tv5h9s-XGbOCn;dq8&qKMC#!{Umf>@F3{E(A@y3e+NiykjqYBjKH&i)KdYeCxFL8Pk^2x5DE?hkB1Hg&jUw6&x2k7egRr?H1q=KIq1W5fpG8~=sBnpj{ZxY2}u1sI2t+vybv4>9gVi7o(p~s`~vg~=&RH-z#-r$=qQXc1Uw#E@>u8)=ox_2&j^eJj|Pv09*g%!gU3LR!I(#bheMA9j{pyc9trjV4~Ld)fR;Q6T5>;V$pfKBf(L*HLJxrM1W5e^xF59S&d`!QpgV!vfjyulyFp7<pygkC=urax0^<a{1%?Uq1`mO519k_b?g1VG-2?h*K<XfYNP##36&wT|ggPpC7_<r<07&fz_J;O@eoCMNxINe#+8h0AZ#RbafYhFV)UCko(C!#dD?sX=;HRN`LJtO{4g?252SS^`anNzdiwThW_kh%M!78+hTu40|JP8~C9e}({!kqS3cwXh64HlRWNIe;lTF!e%fwltO!M&h+Ax?L2FT|8QRQYw?_#>V_{K;r*nm{Zd^(^pY=vmN4@K9(Yv@alaA8;?|KG0t1^J4;C!Cuf_s3Y}@0)G&Q5l9eNBoHsKT41F>qQFjp?E*W1mjqrGC=n<YI4H0SyxXoUpYIXaB#;SYAzqrmdVzF-KMHI_c_Yf2K%T$>fxRg2#q)gvTkvc%V#somz$$^Y0@(ul1@gh`pyl&IJYO!bSYQcQmREqysG9*#zMmtoRbU$+bF@YvMIaT=Y_SsYJP~yg;jh8Fl5?SR?PBL3-cs-q^k)hBv;@8xoMYElGsb3yUkJ{%8*?G@Q3&6boBbH;e)t*SHPCC&{|sO;@}eQ{YtiRr$VIB%IApzKv?F-~wB#b_b<p|X0_c3`Y>YA6Zhi}(*Fwv_*w#uOxB$8Uacyf#@;-18bP@U_bwrq(d)HR~>0dR!{%Lf9*#G0k`Ax^qMEf_-i&&378Y9A5%X>*2vhI|m<MJd`{tZ(XumA'

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
