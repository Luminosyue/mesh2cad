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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5700259eeb494b8f8a0b8f63486c59cc/part_001.stl', 'relative_path': '5700259eeb494b8f8a0b8f63486c59cc/part_001.stl', 'source_sha256': '3d64eff8a873625d6670cef08dd37866bea1a454544fc1c5b4c7c683b62bf644', 'input_faces': 208, 'input_vertices': 146, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18149830400943756, -0.05718119442462921, 0.2893337607383728], [-0.039878830313682556, 0.03014223277568817, 0.39403754472732544]]}
GEOMETRY_BASE85 = 'c$}q~3s6<Z8ON80B1%9BDin=Jt%Ax!g@7W;p$R@9JOn{e0~Z0`fC7r~K@Psq-~$Lj5W$N>BWPkwCNFK(6KfKk*2GF@qA4}EnaQNuNhWE>P8yx2XLtV#yLWD9I_+`3`Tx$}?|!>y&z?PdhKv*s&j7-Y@ub+d>x1dOgwXII0c2}&dF8so;);mUO)t2S;moIp(3jJ)Q!{ei$X2o=q^P)}uskGA3yEJnD<n({SzT6MSzb_@UshgJO#S%<8!L(}zhZ5{ref<nbVhVcm=-l9OxvaXkH=7}3tG;ckFQWI$$OQm{^x(*PO#MWAe8xJS^8PoH{Kq{e7&KF=YM=z@iqA5QFJf!9|mwge6L-uW4=Cw`R0ynR-gR!noHmCk6?Aoz8^ngd9BTMxn1EqTDULTbu@j;d_CRcb>+IEuk$(;-pn_G@3{2MSA%<H-_&;T>#c86^6l`Al01IBTP`u*_<9ZNzv<R~TlRJM`r~YVT}BV{ZGAWGa(&_J@I`&Ix0Cm?(W6DaE=RJR=l^OX?|=5YE`8D+&+3qzL%dE<d5b)r!Z!oCFUHe;FpKAhgevu&ebFChU$iTHy~^O@bD>_zx1WE7ji<SJFZcUWc>cLdt@8K?pTO@QpWX3%{Od+{%5`iBgZOnd#wq=G_C-H!U4*y0qPIbr|6e`)ke%PCYE$~z`#0`4)HTZEDSQH7jHlUtpXYnED)U761b+WKxp$BG=DWHwZ=HQHZ-sB@=ahLXd>ec*Ze-u5yiQy}r<^Z*JA9F^72M$cjC#9C&ey8n=k0zzUw!VXI(dHkq;};wf^VMSe*be++`;oJ&MNDJvoF>M``AWaC#&<Aa$oXl`SsrVNLjChufy-ZFQL`E|IKeI>z?pQbxWsQNBE9i+!u97^m^|9{ddZ`s@1OI{k(ssQ})TfY`p%A%^k|~2;ZE}eNkUqoXh(^ZTE3yJiSwSe&MzwavhtI!msPSFFKUxv@VwWVxEiV>s}=9&nIV2DB}j-yvhCkaeHC{uj5hJF4uRIkL7ie=e#1{7xH^I?$^B0qV&J-n``WRRa~3gu2$O0eDb)uPPwk$CgwY0%IcLmZye!ul7=+N?b_-NT$AUC$Tz;*!+gVM@o}Zy_P*b+^O28QUHSnDN*yiWkIXkNx4ta5tJmFSzIL7{{S-dQJNS}P-+hY9cFA{>T(+xck9XOwc5#gBcDsXIwrhW<<tqFAzAu$_?f*E;d~$Q9(k_{7Ty@nh$u4KU?FS#FU9EWyuU~ypX_tKX$YkfE-c#lq$-U40=e?A9t{=b0eA4!(4t9P&_Aa}RnYVfVvF*)re~haac>b+#8s$1>&S~ar`N{Q4yFX23zTp?&&gRXhkMFQ{Zj9%3#s(?vYF&T1%<2@aYm@VB0k@cMOpQAs=Q|o|FR}ie@@tjziF+CI$vQ`?oUi*O{F>#z|9P{VZ!ek1d=h)|n4E9VnRk(0Pp$owGOt!V$$ZBrY05fpj_$j_`uW-Llgj-0Ll^V)5qsN|{0BRkZ=Q50`v?8EDZI|1>cetBjnU!EcO39KD)-Y?`QR<q|1hsDSEPLN+;!#~Q4cp?k@C%u<vc$s^0YEPZ;xZXp6Rac(?;~Z$?D9k=u)1?jQz~F#XLBrT-T2&%(rJ>Qr3C>%aYevyI-H}R_5WNRQ8^*y>tDvQa|GRGkkuAGVR|#?AgiBBS-Q77w<JEU%c0}^I`1V%>P2UE`57t5A*%L;wtu;%b#KAMst?ZE?IlEoA<xFO&(|MPEWU-FZLDAzSvi2Glz1&JeB*{M>+dqAElrAo{fvqeVX?Z`#nAUGrs>wTcFf&_C^1l{r>vjR`U0E;(BEqgm3EH7yBriXU8vHwd?Hn?~^}R&3rv6p+~-7&c3)`jv7zqn^O~&@pSgZc<OOKuz6|R4eL?n$xrLM<b395C|{e8gM1Tp>l==SxAnETx<LBWq$WLty8hH$7yVy-YR;TK>;L`KeBSEADk};QlnbFn;6iXQbTzmbyau`!yarqfEd!T=H$gXpslEuFVa04KVyu{K#Y`)vA}Bu%jRD6X|7ir}S<pCe7<4*<ay&E+Of>-<5B>#$@-uWQL+3yfz>&~t2+Fb01aJb{h(%D2hRz1h#`RO40-Xe%0iFaNhoBsSpd0~>0mopxA`p~A5tKFPWbiO60<8!@P!2)_B1Z#@I)PICK&d~0Qa>q=Mo@kdL3t>GvNv=Xcrf9I8*&CozoqPppzMR7><)DUyP=Ldf*xK_Pw;T)7zE{!P){&bfAC1~L<HsWR{R_~3hECY3mt)=JOt_w_D35-5R^Tj1WYh4l%Ih5K?j5Vz~Vj*#+VKRi?MYByJ5V%p+mt3t*Eo&F!U(+fE9<VcnLxI2!e70v>sfK-!(vwf-9}qV8uoR<$P!!I3Jt~T?WntFM(!(mw?luY2bA5Lg*s!La+{f7OaEA5tO5>m;jxNpqvDK7Mui5hAsjpgHxet;8buXGz**wUJ6|XUJ70b%>%CluZL~`mqRO{8^9ZI4=NCptDxJ!Rp4C+%6kc)15|fHw}E$pw?HewmAJ>0w?a#x8^I-D8#Etm122c>f|rA{p-aHo;0$OwI0L)@x)8hoJP)da=Yc0e!^yz&PFbu2l*d4$z+$e5^@Q?p=u>21y`d`BCCWa~r@&N$$-w$X*%$gVGOz|x7HcDAvEEV^>o8^U9-%x18cYV>IaI}ait;pQFgO@}67M_8k<bZXs&mP}yOC-lbS^j%JRh0_o)1oeCWBMJ&p}hc&w&?1Gr^0&Inbrx9PkS0O7IHsI_P?^cz!6qU`4eRJD@e-9pF7y)I#?|Yrr-5&3>o>-Ur<cHNd;U+o9FqYV?D0Mv9wzfX9FOQ^&wzuos~GhY#mps@qoim!(#%{!MH~${_YmcDMe~joW?twkH1u*4(1('

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
