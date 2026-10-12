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

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cbb199ae1edf41c6898c997ae785c4db/part_007.stl', 'relative_path': 'cbb199ae1edf41c6898c997ae785c4db/part_007.stl', 'source_sha256': '63988cde266d3ed4652eb57763d70788cda5363bd97fee1334aa3aa1d8f3444d', 'input_faces': 220, 'input_vertices': 167, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3749772608280182, -0.25712519884109497, -1.1500598702696152e-05], [0.020834308117628098, 0.1996600180864334, 0.16251179575920105]]}
GEOMETRY_BASE85 = 'c$}q~Yfx2H6vq#eW%!5^qqO7->eWK>LB7(w_{b6=5;0RqkcWyOPf0TEW)Gi{L@HL=HNcr3AIj1ko9agIX_}a6rq}r4e$)?rtQl>3?0xv{-8qX}(-bpn{{QpaYp-+8W}kKLg@W9~D^i^PpK;DFyMG=&DcNy!40BSPmdeKFP34tMSzGE`6P#q1>mQ>X`9*mJ4<tA(&h}tMWm9=$aBd(tuWEKMGZ3t*Yiw>T+p?~%v7%D*yUJ>sDiv?qSXN)Djwel<IV&?TV{&F-N8msHB&kb?ME>~h1EtXmnP(R0Yidiq@V<wKF2WBxXBT+5vpw^DeH?rFCVxKM`StZzz4>92f5=}a(pMAJ$DvhYeRZPn*ya8@p^sPg*MG0M&mI5%+*|Q@I6J-9%S-oM_}o2D__b4B9)L%0`|4v~{;6)4mx}t9FZt^2csy|I{Au6yn0#?Pp{4cxeBHNayxe&++2ziO&Ubvguj4cKzQpy%zV7GF`rrNem+y_69~eI@E)N||`bRG7ht59zshgj3t#5sz2j;sx8Z7$Ici!|Ymj@pI#+UEBbLo?K>uI=L&(e4EKXQ3eRc}1*ocYPeV?T~@d2C$GN51;!&h@%__DetiVSaDC>o+`*;rRB6lX&^VxcO7g{39PwXZakL$DZBm&%gEisH>AN`gn9%Pd^vyV0rA7xIA{+zdjLonEf9vdG%ZGa~J3taUvcMy;*+J%VY4!HLFg?<58Y>TW4gidq0k>4-bg?hKGh^obuI&huix1kK_Zc2QIHCJgx6DeOx;A@(wSLG!}mDo;SU$-OEd}hkoJm)NPx6`CHpu9-iK|&%KW^>F&Ol{YrAvuMC&{%5d4QY`*AM131r@<mUOZ*CYCs<)U91F8h_`qF)&<`<2ZX{mSs@rG6d}_bdCDy-v}`B$wxveaxO$^fALD@B!B&`kTEk(cdJO>o5D8<fgyb^%VWh)))QFa?#%;H+{)+(cdHw&}Sr<>m&Q2<O9wt`l02bAKKrS=!XNixK7y*?eACi!*l09iT4~yZhnu3%jd;#`Mg*zo)^RA^J2K%|Mt9M|4T0G$o+5Yi~Ve`Q|xES<vPgyEV<dw_I|~Fw)Mq+wp{FI$<4m9T<k;12jq)=Xt~&jhRb~@x!rHKI&ZjKyk{jh?^(m;dscGuUbA(?dsgy*s4w5Mw!V0uN-obU-=~Jl_o?CXeQNW?`!x1jL63W#;(LnW@_UNm@_UNS7vED1m)}zim)}$D^@#5&(ZfZD-1`@OLvr)H7%uyU;j(X7F8YSyvTqnJ`-VNQ=o^yDI<jxr`l4^x>lA%Ma=8w&Z%A(XhP_|WH*9^;H!K%@LvqsxEEj!4@&WmxZ&)t+hT*brNbdHH0^eU5Rv+&w>{H*}bzJSFI8|kyKQU<NZVxp6pBOe}|EoVSOrJjW|Ne;~tgd02is^a@RNSWGVRR>cyNX9uWTI0&ekaE}nWOza6;G>3M6bjr;s>FF@q1MqVBP`dXun6reiaGm75D_agAT&)rq&*GKmG|7PpO!R&c;8^*zM>{yv})&Jgu|vQ&h}Q@d)}Deus)(DzeaQycwH<X5n`+HyfRSzgfjZ75AaV_!TNjRE$M~9$(CHF>}mVka|J*&D1KUUNQ5vzlpp8v;@BnKiPBM$&8gyuY^4911d69tVAEcufdN;Gw>@pE<)Gf_4ovs*0p#Yg^X)W!xxb=4xNBcLo?6`p6gmmjkU}#WPBpbtp8eK1>-AN-wDhq<~(No(-==9Ck<}y!@K^4_~9yURIvcf!{?~TS8)wG+T-&$&SQ=l8%@2@@Zr?Tqh22KwI4>_ooGJ(Ui=u(dB-r8PrZEdw7*uxC>4v)yYctnuSZAW7je88y$7#bXsU{(=rX*Hg^X)W#xEx4Iy4oZjHaNe_@(46L>J>zS*vB9^<PHhFrLHurZOjw^O*HdW;~gkWVpEx@A@yq*Qt0&#fxY+{+Nm$74_&gkMHKVn>l7|8}+uq>!{UDy>8}fzlFRP&>s9re5>cYt<-8|UMpPtMitE}UP4dcU&e1moAFI(Biih#(L%1)F1(K8jB9PcN62YHTks8NGuq<0t}beHG5<K@55dg(cM-=JKgRmDFsGaInDuX9yn&nsxVaDS`X9%ySFu^eGiWFNpo*g^%F!B+@8r0XIcBVedNuI%)as;OC-b#0Bd-lTihmwo>p5>NwQ8AH3)j9<#YPp+qKEK@@te?%_$ss#-H6|yqFTjs=n=e*cE+_<;5*2vLaXr==mxYJ{~USkXa~NUwL0Qi|0Bdf#t*W-)y(PSJZAkX7_T6w0&ecZyZ-I?kcts1h7j6cg$~8fQ88b|Tr`9)Rq>#TThK}P`#D~Xmf~+vk**>aU4_rZFGpA7uU0Wq#U1DpypDN{YfZx6LC!q%E_^|5!l0DIzx$WlUq4~}A<p*?I62e*G1@z`O4YI-sta-l>(7$vL*O9y;cL)uD(6p=_)l>'

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
