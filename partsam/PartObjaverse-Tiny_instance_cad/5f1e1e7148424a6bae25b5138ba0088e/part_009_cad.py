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

PART_NAME = 'part_009'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5f1e1e7148424a6bae25b5138ba0088e/part_009.stl', 'relative_path': '5f1e1e7148424a6bae25b5138ba0088e/part_009.stl', 'source_sha256': 'e81cdd8b1998817f7ae64af0cb4b8a79f47fbeb2e189fa2c506feed58136085c', 'input_faces': 198, 'input_vertices': 166, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.17617444694042206, -0.13626991212368011, 0.1873663067817688], [0.2708835303783417, -0.048400700092315674, 0.2474101483821869]]}
GEOMETRY_BASE85 = 'c$}q~3v?CL6^0K_!>b}t!pn9*B#LMf9uWwTAsR$6kbuDiNthH89w88tG=fMNp@Amy@Bv1IgaKkT;sav=3ra>?3zrlXmZAmJ(JmkOAgjxwR9ope=l>_2VcE61+RNH&|MShc`|R0gpL1_6X_MNt?IG~$FUspK#&_*1gtE?}hbYS{E}cI+ujGbBMax==u9~Zt?;oC=k(!p(N|cG^F>~@tW*5hdHe$x)kBk{&#N;n7E-lVoG;4A3oIJ%R<Ss19le}bJZc(1Rz9v2)VTdv8+9AdY<9~d0lqpyrt@~q=^!CYD4m3*d>|gvRb!~Q9ueldfq`5tyv*upEFgFY8kEv^GG<nolzteH9-q#f5qAF`|kh>}CL-UH0DLRf_0B)W80P~if*7J%IaI@QZ9p7AE+7#rL-ELoyJNw87FMCnPZ@f)&W57ckzgovPF1t*}ccy^b=l+iPb<ZHqEO0a99X;M%bBoT?dm_xeZwpYL)8O8OuMyukgZw`QH)h<2=X&os9Y+k>8k*Ob{4Aa;VQVP96E{(hH_OA^-LX)|x3X$N&n2?>Tytu|`SfHxd)8|19G|4;wKEI!yk2Q-C{J@R@-+Hx4~-YkVZ1eu{Oo+qt(57g+mi5jw|)WEeJ!|{)(`oQdkk?lfP1e+9n?HB8~JYpHxhrqykmD`{Da#=brZW#H=EqsaT@Egc>(IPgK>_$hx%8bo<8^M*}@Mn|JetTr$9Y@?$_Dp_G^q^cph~=bSlJK>Q8PQW*ypItDn~x_&(wv<8$pFsJZph7l?B<oTvK@)?IXVF#c$R=2ql;)TbM`SNSsfC$|IU?E~&^xDS0^n1l672RFX#h<R^G)pc-+z|G_psPnvR)cGDKl&5Goi~hfS&0!tC$EKHcoVr7=>v6H*&Tk6zczf1I5zQxni;CTcbR4%8`g|$llzph<nDwL4pBu=ZS*6FD(Y08wj%zhHFV1;M$N4z<s2<l1+&-Cg2=!?~{yA@8{ODP(j<dRpj^iE#7qQbC_4wx0H}ti56FlKX&E2;fb$o-|d|<GS;~ZIzdUgkQ@46ZB7rcvl_F|k1P5QY+dO7NlKwed;^Edz6T66F7ZAbL`wj1cr5e-L!+&FgC-XJ%|)@bfVZP#(!ljt|62;A>CYfyAkklXY6{x-yGIlfaV@~Izz{&|-1N1n&JzpxeKkB7OL-bb&yaRS^L`;|V2-3v>QzZZ`0&aiQ=PU@$h+x={huA4hxx30g@80JpzPKfgnxVTW=h`#zz$MxD@iMpOjdPVcd6yy^H?%lRTbN5!9hen6+csG)deKZJM<R|O(vTMKB>*RfDM1uY1zJ-1>&V&2?=Dmo1bG`-l_l5g8_JtMQKN8#*?&H`O)(znPzOdW3#yM<(`}@Lc=DsK+=f1GBu`i4X3nIZjcO&R?>r-&QpUr+Q>PhbRvvK*o_}u)C<NbXRhkap*f=IBR?P~P1mk!?2|GVEo|Ce$+``jIhK6k#ZXbP^cRo_wPW3^q=6s*5F>>oHsqRF}LqS?bfNd))TQDkA=y)oeax{E(!UwC7~<LxZ0yEAhI&Y>fR8}z&n<X|6txDKD&RZnQ{Ji_xlbtBG?wI?(eJrgj#d1Gk282&EK`F)#1+&=XV;+!~#c~?bt>+$2*=e?W37gyG6evZ%82V8u2_({zdv7bkQyF=RQ`0lIdTkCf65!ugaUe3A|UlRXp9_sb>jjspuG;8s^)~W7#{mo7f;kjCWjy#*e-LmTanm@k-{cs-K8T<0{x^A1g>$px%5A5%nzAxx}wrtdKoDy&|d9EIBZrY80UIFfo?2hO9Vmazi2kw90^Xm5Kd5s40Wl^Z}!JDwYPe)_kgq_H<W+wLUo8T?$lE`|##qm6E#pdUcXPaJ{`{$>)pXX;hxZe+M7xaTM9^9OfuAkSA-iG~^2X19#;d^X$G2$P%Wc;4qI5&=l<C_OoVqbUoC-^6;_4<kt`;kuqxM!S4J-_@I^|=$=Je#S<8+C6Z&ST(qrT45J|CeU$mz|8?Fh}QOR%T-Vw)z3<JF|3;uK!#Q{m>EI%UP!D?0)UyeD3A*XLLQyst?eIS?|9YTo<zu>mn+^{W`l(qt5mt;4S@`$$h;QyrurJ+>g7!Tk1Iq^>_Ay`=3+hO4i@!{<`?wyClvDuFGfPdF?Y;7q1!I{~R~F@N=Bp?<=3%uMRk_<NN183eExJQ*eL3d;I&z{07|L?@olDQy0m(-|Y(Qccc4N$AkObZN`2#mu4Ifu8VUK>mnWn_t)2a_XFg=1>El+QFIdhQw#3*q4Pcd?lYcb9G(Ma4bA~$FXv@{x((=0=QYOXIb*gvi_e8K;QqN`?Zmm^e!}q;x%j*94|n4nBlr7RJcWKXzF?m0XLkzv+4DKi8SyuqGgdR_J#q#9t{GH=y0xFKxqr@hzsEUabOZO#F}M0D^g|4I%Q@L~XCx^t^lL(V{d-YIItZbxgXkgha|1smD5ze(|M8y^<`4hxeo7cM^8fuQVS>ydLE4=(rKix}K&|{u)IFtLF0D1K9q%chLOn{_2x+&{-$s44v^Z(kOS?|mAZbJCucyAAV}{b=7%z^ol<q9;3eKs#LEVlzh5qN%Db&;GucN+>b4;TtoyA;pI9CqYDEgt);}|!cej0T;^&RwC)T%w&OB+Z(j(Q;VRkU%e)78}Kxo5G4chHZZzJofQK8`w$?@i~tKMBmKy#E?cHd5M+(k9X0LVb<2c%fQah`!RUl{TEdKXreO8BU95ym-b^x{I`KoKyLjKn^j?L;0UkkEfnY-<P^C=a@`WdOCBpIG05>l72XKGUHCApG-ZKI)i>Xb$4m4qz#}?rXKJk`Wjj?pZhM>FoXU^>I~|s^zqd3eD74w+mUlBYr}iWCsB`<mMLwRv`*5x^1kv{Qn#T_qVGqYM4d|Chq@2rrP60oPn4F;IkU-?{;9Ofq(#$@p^m2RO;frTP3c(rH0oIDL}@dn-7akgeIj)t$IM_H^`0Tjc`)-GOg4-@mU<ZVXvUn#coWGI>0_z0nMWq`Oyb;0tVbFxmHDJ{><s#u)T$;O7(@A+sY|3SlJ+b5ihzEc*UCRaT`O&;wEO8dQg4yASy}<DoJ?6Y?<xNv^(tvArOl^bK)qJlE@@TN+jy;X4X-zG{8svv)SKuX+QVc^r4{l0HH@{CV^(q8D$cKTl(e?e#?qVAzm&FI+8UbD>lp6=##~B$H~l*5bsVqsJ<Mk*bs?{nE)854GOt2D<0|G~#N3O>96tB9z%%-+kbEWmR_fJUqkQ@T>T2G5kUpQfkh!g<FQ?wdd)4%-sdw?-7W!)HQr;`4-$JdPy^8m%cu(nN(sHGh(J#D2FZ>am7tnKft@JN=tzyn5^Yv`zu#EFpQCHHJQCCv`TG|Hs74&7)b<(y=dzAJV**s|vNxP4JJM}zzn>Ls1UTN#471QsaR(uKPQhG73@8x}Uoi?de>mF_X(|;-b`(>*`J@g+;m%cOn^)dL)$ud^Um&vqA?eu4PYxz$lldeuf@h@S4KiU'

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
