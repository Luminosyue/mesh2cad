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

PART_NAME = 'part_000'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/7b7b140d42cf447d87ab5e1ef407d9ae/part_000.stl', 'relative_path': '7b7b140d42cf447d87ab5e1ef407d9ae/part_000.stl', 'source_sha256': '8e5c298e14dee34f11d07ec9d0547a220934d911ef0c3ffcba7340868f303375', 'input_faces': 174, 'input_vertices': 160, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.26153630018234253, 0.0099601149559021, -0.03561626747250557], [-0.1903383731842041, 0.0684429407119751, 0.03574594855308533]]}
GEOMETRY_BASE85 = 'c$}q~eNa@_8OASPsah*oi1~mfS8GKgwNa>`5?F)L1SCO>Qi&gnutWp}StKF`E-F&dDjyn~Xv%79YpO;wlj*cc8<+l(+3b#BOaGxAC!48GJFTs$ZCcaD*z=zAoXt7M?M$cLnRlMwdG_7+o_p@O_nrf##c}Z|miSDy@@Aa;y_0BJ6ceo!tHsmQTwCSw&fe148e=7KpFUCto?cl}x;n;cvD(tBJ>IIO^aXZ$UQKR#rk!5X(A3;ixn+GrQ?-ZuC6)DF5A(enD;qtmJ#)^yM>FlLj7<AQ`+xjQU|sOX{_OHa>dW-<t^y|E;$OC3RDJi>^W?kBgm1O}RQSJ`bb);P-24vS4*W#;-*a={zr4bswkz&O!jCyC{Fxn{ynW(=@Q41)efL1xZfZNTeklAS)8F9!wNLl(cIJ15-(JFfdv#7XZ$EHM__ICSw_N@Ec>faywDWSmlz2e%abC{Lh9BB2>bxR+=Vp&y|LwMeJpcV&T7TSs^7iuc4Yz6iw|lz#c%4n#wDWb9cJ}l9{zh$ltlFgmynbQ5HlDuGG44BQo3!x{_vIeu?eVqR`C9SM=|0ZammqxSzRnTu-}3C?`N>lT3shfT_sPPyR<w+$^?e`b4qlAn`}gMR`KaUimyr+O?m~V-(};Fn*+nAX@O|$*CHm=lencCe)Ac;x^xbpoMg8!K5p|rMo2Ny6!?$;y7WLB>j;PnmmwZRmH+=imPeuK!sUzCF&B^jzjN-dKnd{^EjUNxI^T(A{$Mc<`(P4GI`9fzzo$F_W|B1L>u1BtmI?}f>{#DoY{F%bPD__q4Y9n9z8Ad+t3m@{GDSNbjI=3@V@b<=a+IfYKZ05f6w}r#%IQaWc3IFZ1VRbyMf-&LWiW^q1OZb`iliWZ0;U)F@+S{fHfArcVZJxZI#eJ*mgG=i8gp2ZYALC<B&O2G4`tp7$HuB|tk%auLJ0bPDSj8o}FXw*|{Hy;IzMU+d1LqcV-`Vw1C|W-wzR}N!Z}ijjBmK<&ODO927{1$^CF)PSA^b(Pns2SS7K%3hrth0SP1HH_8{uF7v3UO9NfLDuM?=xBuj#u};zgYyzwk$Ii~IM+wG+I~vbRFf=8x&y@nbySY4!>K?>S;V|Mi@xlYA@`ZGM`*v+9({|8<-2@2L{^?`vCyKe#;<ZT_3SuVS<4PyDmOzp_)*PnskAE6YRC?l04~ex50gn>tIIhmreT`sVXN`sVXN`sVY&^fQcn<N09vZZm&Jm*zW9#A)XxpL?e7?>!^xJQSmioBj9?gn#r(P#tIaTs3|FKQ@WuJ~<XtucPx?jqnrS3aZy#KF>`*@;rb2&7d}~l4giHe>fIY=V9bMV)&8wNaf+6HqYO^D&9vayMpR{A>Uu7A9;Vh&>B?lJNK!B!hg3RsNJXXy=nN7_vVxu;o~_V-@n$4D&d>&Yr~J^zv&jfxqdMG$ofJ0=K8_#<@&+NuMj?-tKp(_QRl;z!Z+4A5#LznI3L8lr}js#qweziDh_M;=K9L;-G@ZJH5~h%Hg0nLX869;T#;XYJD^=JtOHHoSvxks^MCtMK%EbAJ!$&Bn@dFg!+#8@^H8o!P2WG}^z;0s?+4WRFW0xG?@#XT<NeCM98m8&xlT6yaErH>=T999sQ0^EZ{Ot)?>NZwe|J8hUKhE}H+|>Aqyt*MvHmxG_c<fq+!q*r_$=~=2K9boKVtgfvc7%%`}4ipI7Id}re8m=o7X?ysg1MTADO;$>$aHhZ!~MyQSP%$-}!#(Zk``gr_Gbde$DXhy!K9>U%f$_hjQO%`Yz9EhaczObpdsr%l)J2JHN{5;PqqIYS&TjPfg!(F1Ks>=DyYNtsN}CRNK8Ta?W<29%oq;<Js=Lrc&9ulSv<`(YNlk+5g?vJtzDB-MT->`Y?sX{m^^C_k%N_>0r{YgGqD1q_e;oU|EOwK?HFcg7_f>v5g>}2AvL0U_pOph({2|vG_cA9NNUOERw*9;K^u{ei2NXqWp$51~I|<>_a>rngSjVPR23lyGaP*FCd5~A|{}}<G`Oo5Z{BCfOE}c@l_U&KxczVzXm3K6ihk?Oga}#ngu4E2mUg2DuVc71o4*;#Hk442N1;fA&6%}=YdJH!I}7O27>r2N<WBqv)Ip~i^Wm!%PhVHK7=;$G30lmP1>P+M>@#jMQ{h|5_co^qxJxcKD76P58=0M@JL&gx}>ini1$HT!K5#M>0FNB`y)6WaXyPY7AslQvZ!NG58VQ;2YaDSU@v$Zv=O`w+zed_ZU(P_=7Cp$bD{a*T=0CT3p^jZfW=}KPqA1ET?SqXE`mM-E&`W8%fKbzQs`=MDYyc<23!GN3tbOh3wE=pf^LAW2X6qEL)U=U;27o5GH@CCS`J+XUWRinM-VT8E(Vh>0xtm<LKlD+U_1+vQ;2$n@XMk3;Cx)aa%dx%v<XbQ1x#88_CPm6>%gS7VA2}!Mz9B31+Kz4dZ4oQE*5)O^ssn|#kau+SR4eC_X@b3g##w<JK&x8j(7*!JqQQKX<@OQ#W(T0<M{qKydLOw@OISdK_B;m_o9D2=wmOKv|l+F(!<bx@MA2VWwDS&HH+t2tb%R=lWqo+ZUvJzfE!R}74$JMX#tq@aWLr<VA3bSq{U#;r@^Gl!KB{+lRgI~T?Zzu1XtqRh)auOVpHP&)4wP_`#ALS)c#>%{!(8aslR-O)ru^ZN{bWdeaK$Sv3$Tz&`QGkH$>NBGy'

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
