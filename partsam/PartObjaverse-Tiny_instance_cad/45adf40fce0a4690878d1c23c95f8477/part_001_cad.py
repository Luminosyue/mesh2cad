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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/45adf40fce0a4690878d1c23c95f8477/part_001.stl', 'relative_path': '45adf40fce0a4690878d1c23c95f8477/part_001.stl', 'source_sha256': '60bfda583a12278424d44014e9a223bf5c9fe23fd79c9414375850b7d11d01ca', 'input_faces': 188, 'input_vertices': 177, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.04449370503425598, 0.32292598485946655, -0.05956663936376572], [-0.03484955430030823, 0.3802415132522583, -0.056087419390678406]]}
GEOMETRY_BASE85 = 'c$}q~ZE#f89fvOvNI`5sQWh<m&?>7o65ed0RkK!0PzqT@Oz|y^5F&~!O(=+(?2<&IeTy%x(bf_P!Kjdg8QY<?PP6@B)3H;R#Dra~<*uLdk&kIRt?9jco^$X1Pj+WI?arL}J^S#_@0@#+CCd`tG^e20QjZnZAELi2T(;P<+_lguwhlHl9oVz8p?TH5{fB2+i!$DQ=zM9*_RZlPv#f*GlfhjL%{!ZdH<ku(+FcneD-G_BG#zNF-&YrD+STCt4fT7Q8yw&KaQ*%U=lRuZDk{oK*IiRq+EV&IJ{GuV_-y2jVJAZN(o~g`@gs==_qmns&v@(H?<bT`3LiT6XTx{Vb5W+pYO@Wm`eQ9;PAMM|{jru|;dTEEZ!by-Z`UY4mKaz2P7VmqdEzZ2%vUr2r_6k)?ZSZcA4s3BQs*3dU;6Xq__)y%z`uu|65cy!Yf_!(d=c~S%6WWfY$WHrKBw;s#W_9yx9Jng|HkN_!Veog+Q*F^JLBV{zs~qr+w?%T*Vk*c+RP`J|CKSHVE(tp{D?ef>!k9Z4vBqz--CY#e}SHE{OOF3w-pU4--RE_>0|bFDbe$31YfFt-dd;djiTT4f2|e$zOTU#ux~)^`$>uLvDRtk1Nf8b{<H_x{KwOMIsGS-!pB>S)P4Rqk;k7=-o8p*Z+pdHwztx^8-A!y-G}8ly_LRR`c!|PdfhEEd=Gw!(bI)5%IWnvt!O}<Kh@cn{rxh%KELOaQTi9E?_+z_p!5OeOT@gsUeoLA^?WKKuFIdVQ}gybV_)qrHhOCLe!V>|=JDR&tH!*Q-e~Mw!+e3UZ<X@tJJo%T2I;8~`<gzK-b_z5J>{a`n@<L~uFsQlzKEW%?3tK4o;@FmmaCp~lNldB|L>e$_jrE7rstoTd8?y_{sjIXh99A4TT1$2(G!bSu<x1U;&s$sJDBZtkLSnx#k|*p*XQwlkLdAzcb*>n`M)RSzTNcPO-~i`o%Ebi-`|cp=A-mXC58X!km&b&8tEA@dg?@vH~&#>o_^(H>Fp`$t3`i2T1`)d=rO(S@qM|`->CY>O6VVy{bK?A>2Wz9$kSgW?vFQ**Z1G=neNT*k4I}%&*)Td&YrOg!h7?0-S2xl_xxzGSNvRcL{$H1g7ds%oJV_pzkBl|z2bFY_)vOlD!1Pz&pCQV^!t8D_49k*?->&Nn)7;J&!6p~=Uv&Oz5OqF{<Ga;Un^ESApLvBdAdZ8H$U2mpEmAKC+Fnv&yGWRygpA<?CYOL`}nx%!N(^0Cvti3eYNS+TT-$=LjUl1ZvVcqZ$w<LIj^tF_l@HGrq}Op{eJB~$m#X<&gkcQXLx(Iy#HtG=ugQ0M6I}9uLmC*`=jA&#5rgBL{6{IGt<wN=hQx3ZTKquhCH741F<^#D@6YcKV!aJy-p`iPUP|-d%m%6ke-nAAC@q`(C`8L0%PAIF>iV+eY1MKcSHxJ4;k}?oPTIS&MWWzyVdl(e=~jDzD4$bIDIVhb7&XKd3@ZiH2j5Q+2`?ll-K7mz3!heZ(p9f-(H=^ugl{rjs8jY4I1;d*w>%8#lEJu((9%FOOpPQJU;0Au=rGE&F3o%!t*W5UGuGCYj=ItM=Gv#A3Ae?q_SuIfA^6}W##|-k;)3^428}rB@1Bpcyn-tZ~<w-1#l_LeXJwD2Csu}X1QEN-U?U2)#UAPbq)?Y>t1I);H=H$Hh439CmDvre67nTopst-Z;}J>oA6uYAp915oO~NT4!=eogI|MRA%6+K0>4Q941N)Qfz0NY;1}S-WIKEqeu9j`Pr#3nP4Hvz9&#VN2i{3G!aLyy$$I!f_+Ih>c!#s@ch*DXZulX%fqWQlfcKK$gZIJ*$V2b}_;IogejI*|?1G<zpC^9`KM!}4KZm>FSIJ+%ufngBZ@{m^y`*OSyq`P;yEz2+!zanp@U_lb<E%3B>u?#oio70P1(%bRa5=o1yb)dvuP1MU*TXlE--K^~Z(+H78~H8xwk&pYLzZ`WBe@CQ2;V{0z<0oRk@vuN!Q092z}w*+<o$4kv(`H6I@Vh5>ss#VwamDGwu0sId~yyv*IDzN^(=V;cC!z5^JUo0PPoTeN0~j!oc_9_%)ShFk}a^Ct@P;UF3;jjt>m+?>t}Puxjdi88BXwLCvYwoIqM6~x`ez4z64%OE`S%qOUQ-r5_l<jF}xK15~*1~Uq*frc5@ND48DvkhA)G^%yN0Tv%cZ1kh6m1HE<AKNnQ=Fgs&v8g0F;2$gjdB@D=1&;49!u$;;tO;Q+ZDUe1|a{(-Z8;;d)LAH&bUPm@1_pN5Z+KZK9KPmvw)Q(5e0EX%umkbDw82se}8hnwO3ESDeUKD+mQ3;At$3%r%Q8{P`vN7lmk!FA+!;W~I1saZdNgnSf!1dcc>ylK|#;yL;Li_3q++!u-X4=?j8<=eRIue`_U^4`>iH_dflSI!G-cIKDWXYNm`^&ha~$WZ'

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
