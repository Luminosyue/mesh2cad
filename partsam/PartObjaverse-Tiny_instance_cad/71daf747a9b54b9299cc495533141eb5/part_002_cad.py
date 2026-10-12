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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/71daf747a9b54b9299cc495533141eb5/part_002.stl', 'relative_path': '71daf747a9b54b9299cc495533141eb5/part_002.stl', 'source_sha256': '83566a05ff80c79515d9e8cde23616cb979f62ad6ce95bc40fef1cef4d065602', 'input_faces': 196, 'input_vertices': 120, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.5, -0.2925422787666321, -0.033542439341545105], [-0.4462026357650757, -0.27664971351623535, 0.1491309404373169]]}
GEOMETRY_BASE85 = 'c$}q}3s6+o8OIMG3y6RwM8xN=VtA?u$jb*;ML-u245(ntg187u!7PN-X*zS$Xqz!cD~gs<EspeIl8GdZJ55QmSIsoZs7*J0hz69@PBYdtbc%^ds<nI0_rJ?Ioph$tuJg_R$Is)p=W*}lj%D_sanX!EHg@3Hm%T<fW4tD?Xx8p@wKdi`Tjw|L+!eqk3eP`g9xAOYDXR)#?d%)zTb-?SuJ~MQ{F3_Y_!Mh=eT%EjRom=nacy;SUr^iB>h$^6hT5G@-_HpP(^6Bc>4_=UZ(9Gy&v=@}u!m1+wBdc8dfLxU=J`@Pd+$2`nKe8`{>J&!-0Q)2gxB}36rODzIVi@5+!o%tc|ZB6k(07FLW&fx7mf<w)A2*{Z;zgqy|%PU@!G{(*X4P#=++L|*Bqa%czxZ6%6L6G-z|L173v@KI*q>)-Y0wG(oe{Ll-eu%o{M>3IlkxeJY_uFI6(86xsSd#Y`t6d?A=w0*REY6e{whVIX(4|?DeK_)z=&3-|HnGTIH7g@b{8c|B{=|<^4?IwckdI`5Pafp*}O>Xg+6~XuTPyXdnL0sLz^n;(OT>Kc#h<=YFxTU-;~k<Y(E)fA?sG=<`Jn^|=NgRYLoaOP-ynr|<p4@qXF&IIOC_f0X>Q1=J^@s7Cf$I#ayCI+gR)y)k{VH_y@Z>|6)!PbAL$)RA7<`_I?(-`Puku8wnmreF4K#G-g(?{3=X8_$rxwfV5@YyKLhczxf~)aSsD$WPC9%ie#!@LGgU{qJlc-!P{^_QS?auk4MrPbv4E|9XHo?>p1$<-64T`si!DviIND@T{^`d2X0}w4*Jw-n1Pw{(wQ_yP9bJx9^F0>USMt-}LJ3>U|WK=$5_zK7wc6jnv2N|KhucWzUA<6mK|c)#pRP9JlOiR{fFo?e6}aV*WM<?a$j-@AF@XKH7_=)Tj4p>Jz!5U-s7KP{r%%%W3~VbyA<77q`itc|P{a-nhMt`h0$eeBA~^jQ>1aeICw8>X*G{J`YX*%T#6Gm@SU3+p|eDAImWHzqOkB2avapE2Z&qx7uZIyd0u<_U+lKPwUtxezw@?d%JMm9=`gd7;m3S=e03~{DkD^Jd(Et{n;yfV^S22zi^rSy<{;@EyhCYEh?lwyWe=$Bl(_5zxK*r-!ghlobTdCX?#Z*truQ1&mEpM{6%={kzbLocyo{F^T~DUgXf{1Kjg`i{BQ=YXL!RkKz;C>)Yo1RUi<oc!ZV8<zrO~)<&nG*<@L&5KmP{xuSlcu1t03N_g_Eotmq7_>(oRV{|g(9zuZmZ&2_z8c}}d?xrh9wH_5Mw7hZd{h5CfA5Pgh~K0Pb@p5MLWl|8%bp!HTK()fE`#cOZf@XB7lUq#=G=clpfE%L5lTJJ13&FA&W=f(H3ks;ClH#xMQ9}Jz7J-h1h%3jw#5nli7OX~A{_;K+)K{u(7Z6@u{Xx%Z{8|L+9`gewf_y3;ytWWeey><Lmuk3aEAoV$zMg2pLb$cXlHTM~wMO+<HuAloSsL$^&(7H~%M&ozoc8R}t^b4<*XH)+VMvlnd-yhznKTY!)#(J+5cgkLSZon&h?dA*gz3zXI&wk~w$V)#Ml=oBLm2yJ(((XZdKlR=}^~m1bPt$8rU4zR0SYs9MpFg}_-Z`l3L+5=umqQ2DJ~sxsW$*6;&ngcn^JK$|zAt<Kxx?$7`<3;wtRHuI%9OYN;)uUJ*cZkauQ1=+e|@d=>dz(rnEBPO{*4*`-K&32=KuTZAK{zBL%y1X;yl?`bCEXWLtq<t7BU(fkBmh|gLzH>$ATY3akij1k3&X)$ALqUlfa?i87R()$jRVDaHh1LOcdwEzFL9IK+Xkcfaf7?;CbL=<Sekc{$v#AG+!-4<{;z2Ip9=eEI1bXl8WLy2gNxGX#q!p15g%Rf)?zZ`QaRh3<U>*ryys5r+`<YI2Rxj!3E&e$V~8Ra4~W*xENe6?Rz<j^CP~hK;|P?fb+pw$P926cmZ-Acma4mG8vqVGnkL!yhu8yMJUdB$Wm|~c&)ECA*+$4;A-$j6lXhf8JK4d*bXj4rh*H>8gdR;15ZOnfv17PkOAN@a3qRzFp`0T!9mDCa1b~IIRzX7o{n4zo(^8+s~V&Oxf0B?0PFzQB3FZJ!A@i`*a_Z-EC+7`HzFSaH-dMtv1@AwigS~%wj<XeE5Pf(%aQru<=}K=7C0T8f?NPj0Vg5ngLy6jCxI6t^S}$iOOb2AOTi^<>{={Aajx>!7Gyng6Sy8+hpYzIfgeL|1V09T6vcTx(hlZX2wo4aL~7tl@Dk)S@DgwgG7QW!5*!1b>Z{qv2au6qp26S;z~hlY;PK#aWC%DMJP|n^JQ19LTm?=57qPKxy$Hp5D~j_@6z6871KbS$8j5oZvKHI|ejMopKMr;ww}D;YHe@5X4cw000p{5RZU;Y!;`{^~yH7Z`A{&s~!42Rt<T`K}I2XAboC}Uarh|E=faAbc6z7@9Brwl~;F;iukxRi3gR@bb*C0#4Yrq?jRp1Ta&1~$x;#_7A2#gN;Pyf|B_R+<IR{oFQfB%>2Yoh!w|LN=He`zeU2aDh9fxbWd@Ne?BF7_`9>9PR'

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
