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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/439ee7ebf11d45739dbef21b91669c1b/part_009.stl', 'relative_path': '439ee7ebf11d45739dbef21b91669c1b/part_009.stl', 'source_sha256': 'ebab6da04f3b1f4b880adf144fe59a6a7559e85ee69c144fafb9e4f48d5db47b', 'input_faces': 142, 'input_vertices': 107, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.01576271280646324, -0.41403651237487793, -0.2183043211698532], [0.164701446890831, -0.28380805253982544, -0.00658233929425478]]}
GEOMETRY_BASE85 = 'c$}q}3s6<p6^1u*iKxUPfha!GqmlrM21G?r^cV!JV1k0gSM>6@1RMqw65C)Bk4~K!r`1GFEhNUPMq?^bOs&|E=piCWl)Ol*t(t%_k9O*#+E}&eB)$7z|4A>7o$0i9X3ziKpLN&XXP^C8LrzwpD_qHEuxg34POR>!lx`s^TrKrfJyKTWsUBIe_^|*L3SWO5-EjY`={a)()Kax9y4X`)R27|KL{BIg7aeCrmsD0gQdLl~u(GPyqy3D6@@kLIuP!ZE?D2h%Nr+F1GZJItj3<o$@uNp!M@Bs}$){Fn(eDrY)GW+u(W)AA;hRzQC-iss#&jG0lAk_{`2FgX{_f41^|Dqgb^C@%c&6p>)ieFKLa$thZ{IlgJH$=hbOilGjM|7iA4Va+cj%16TJ5wa;oGk7{s8~tKlb_isy_K7zE|{l6PlXw9P&g~{84{5Ix2R+zcO(X@+>-!c<;GiA4I?3&VX;NzJPc$v-Cy8UyuAH^0!r@Up4$n1N4UYR?<G1hu6<F;W<+BY7sx71ka_$KKwTF^*IOMikJ`IjBR=g@q5DRFrJ(>nCH%`p@;ChzK6u$Ux0DCm#=Sx-*(6I$nQFa@z}e{wnN(vyny%e?1hgJzix9Y{EL_1TUV#!xvb(7wa}tHo00$8dom9X+ItaC-&`7w=Q2Op`#R$HhIrBM$4B5>$BGYNy#4dUFH6FB%nxk5U+?(K@Xdoi#(2CzYmQ=E3x;h)zkh9!_gMG&bI22B!M6s;d-N8ae-(aqhs0kx1>b7@#)~{X>$f5PP&M)xo{kNepXBTCRnr#9^H>eyJHPp-_>Z^Cx{Cg&9{CdO?a03(UB)w|W<By0hP;IQE$d|-g3j(no|v2+$Wyfy&t<sU--Xsy?ZoqDW}{!T-m@8g+&cKysSy%idF>ti{fY3G;jaym_xM`J&(MFuBKY=G#pu`A68Z|_=RLU#{q}Ed$G9gqVqLihj;M!kotAZ?GFIVtznu@?>i(TP?|Uoj@b}=1SK%));oGa4cf#LuUi@7Rvfn=&hxMR5H4X4TGh|)O@Ek|~ksrc0Q}<y!-mA-xAzzQ&eHj1BneFmkqcA^ez~t8ufA*D=vcCUbgK@6Thi?V$#(30)Et{YTweVFyh>WxBtCyhVtrB0}h;bSNSKvK*t0EiGZ+x}v$1A`2MHj!{7l^mE=Sm*>)>C_B-+i<O?^jhbKL2Zs-|e}4+}}6bSIPWe4esjyITpT=y$#Q6|D?Rhf1HZrH22pw`9GJJ&!rwZ)8s!7-t(M?W0#x!=go|ed2^rXcmwe_&9l{3_~xzNi&}9|{F~mR9hY(#KHq!iS$XgF@}D2}UniEcPNsCT{nu4zo2)B)cyHT(9opZf%Q`%B!@kwJRbSuM3_oqH%+JVmIM3Z*PHgsH|K1m6{ad+t&0Y3OgX|Zz>rwb7_m^_^SKH&wUH0Q{*^hSV(PsbstGIuy*oe0f&;4$@WWO6@V&FUHgOw)dgPk}RzH`nfo->YbFOzdd@tiRhS4e)ISE^XfEAN)A63_EZIp<sILHN#jsCXWlr{9-&o}cboIX~ThJ1yhkd28{!RpqWDh%c4%*?M2jXCw1Y@!RD*H+i0$JB!5Uz0jF2_k!a)_d@3xxfj%<%iufri&-T1i@SCue8v07<bCA6aX|71%KfEyf2oFM@p<1V=e`?sQheTz7Vk$p^b_fq_o>1A)c(swi61ZbZ|4}fe^p>a3;g49kK4m|kJESVam9OFCEhDO>j67m>H%wGg7~Z-%xecwKe%fu;hU^C+@DIlVg2f9>6dkj$-2eyow~)%y2Xs&Ao*GUn5=)id3BP9^^(bY$>_C1{Pj{_nd_v!vOoWmjED7@Jx%H{_wn10!e{+vuzu^j6b|31_mr;pa=KKpYxlgnEvCCty7ll?u_Xn5C9F2}$I)Atuw|qFyApQvsQ<Tw9q${%eZH2$rg<`(=Bd;Sveqo}RB|@;esVVX0XEIK)EQ*050Z1qbJ#Q&Qr%>&50kZ)lC>6*3&{)EG|#0LkhK<*=aLt)Y4%Xd$R2VDbrHFQJe&Fuc{Vwd`Xh2CIh8t*oJt-`9YY>Vj-w7I$B~Cp2a|`A!>G5D!^keGBD=^z)Bv*9?&KhH2%F|mY7es3+sL8hUTm6!solt01Ib!@lC|DJ4kq_u)7+ODN!B`$+?PCnP4gh?56N1i$b-m3sL|vh<QVEmvetXaG30nQ&56`e<V12ZHHDl^HmQ@zCOMrtm7GqVM$INqBTuJ3K-QW|o=(nT(>#khhpe@btaSld>s<0Iavq!JeCk57Ru4I!JdavJo=2WfolTxko=MFl&m^Z&Q^{%M3DmLV3FIVd965<Rf;yBuf_x7(jC>EdAJs+fNA67xBKIc$fK77*HH54+lpI06lTC9twHH}yFj;FKvev%jaB_b(&391;khKmX-$gdqG~Z1fLcW_EON}9GjVH&Fhp}l+peB+N$fK#r<k94DRFgc8Jc*i4o<yGFYdKi~-NFO^)4z)T{ju}`*5w~ZH~+Hh_3Z!4R$s2~FYBDFAboE64y<l!iGFas8q~i4_|+dG'

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
