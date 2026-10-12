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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/3a5ed2b8d5c5468897e797dcaba508a1/part_005.stl', 'relative_path': '3a5ed2b8d5c5468897e797dcaba508a1/part_005.stl', 'source_sha256': '008210bd25110f964aa19b4c8e9548d70a3264bc2e9f6acfba0f040ad0762420', 'input_faces': 390, 'input_vertices': 222, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.025868291035294533, 0.24041742086410522, -0.15593090653419495], [0.11512760818004608, 0.3207644820213318, 0.16109751164913177]]}
GEOMETRY_BASE85 = 'c$}qL32>Fw75+njib4eqpatZimas&i!3B`zQDhBEYNHgTkO&D-AV5I&CCJvYQxK5#QIsWt05ya{Ktd80v9cJHMRZa}>9hrAI@TE-$J+b7_nq7OpZuNav~T9j`Of#wz32PyJ@@|M4XG*d)f2qfr<r$t=*|aI>w6xowwK^d&CHoHW<=)XHrW$r#Cdh2JU-&r4t!xi>X0~Zsy8cfWai`%If<P@iJh}LBqoItvnJ$B$;rqbJ|SmhCiq?%<0fYse)8yyiJ2yDk(`{I6l&ixDKsbaKYs2t5+cvc+0+eM?hLsIAKo;&?4-lzPU><6zVcSRa`^Ob+iZ^VUo?#7M?PH>%@^KVza_?h-ObN8X&jv=)blT8?mXVB!(x2vXQT6%92y#%e|qhhp33ggd4w08k##2n`B0>ukI#+Y6XkQ$R{8jFR)c8W+#VhMb@{v{w~v(t@u5GB_T`tf9vRC|`dc)=^3VBO-1SKx^j+ymhnMw9|DvMI$8&wW<T>T;JhDFNU3W+4kEEZE&EMhXg{VK48{048W!)}c@bg@UP|bKh-{V?L&&*UG@Adj;MO4R`Z+vy_x;?+o$J=#iGQHf#r_7G^Pt8^_{%*lmSAVFaWvniF+lR}(3gpxGeq8GEqCa=aZht=Yd#6(Ub)}!bT38myU)|=*7yXgi718|gw#M6|`QM+u;GP%D%X1wn^7Gu6(5=6g`grz9ZofOeeCd<Q<)8cWxsTz$-}2ATbqF<Y<ez8u-HSmw!?V7uaL={P=ek95%6-o(`yT1C+Mmz9O~1avmoI(mZCLNimp;i&UgyiV>-^ntfBvW?zWc{Z>=_B_AK`WXXkPlq&ZGLr=Bxg(`Ko`a@a!Mqb^qj!KjPCb=hyP;{90a}U(2iWE4)6x!t3)Zygt8{SLZi9?@Yw)Te;ta*Y}&{)%|99b-$(e%--Q!2j2g}>-%5xa{t?T)cr5KzW;5$y8ksV_rLJ^{ttx~?Qqve-jBlT_oL<2`_c01{peNu)c3q{u7%g{>)f_!c|rNY>-@?kd3izlh1dEmuk?F&%JPEtQFy(NnwNdF^Qe6kUhiXM$=Lj${uEyKr{#5jme0%&I;WOb=hX7*oLXL;Q{nYFO~3Dsuddv0!t47@^K!r0dDQ)8^VR)k^VL08^4ZRPQC_|8EU(^omRIjP%d7XD@cMmc^VR##^6GtO=TYxF;r08@=BxLe%~$U`ulS|?LHi<nmG_R~?R!V&(eE9}SNl>j?Yyt9^r7WdA6j1Zq2*N{3a|UH<n8PGgU*rg`W%G@%`XT#@51Zzu6a4{b{=)!!-bm)Ts?9x318)2UH_$Te(8twqhkvL`BobXgXR~$%Ds2<&BCDP6<$BD=H+?qJnDHPd0+eV*n5n;UVpEzcQ~j|EU)^+@~TfPukWkG4!-&Ay+ppsy`*@1FUdTr|3hon#&~tlSYF*TmRI+T<<&hSyuN2_zPe{DukIN;kN&&*`@4bbBfMT8&CB}OdDQxZA8k<-w7-^D`)hf%zn0hk?kj0q6xeU%tNdNJa)H0D{GCR=%HL^<w|}R}Jo?}1->&rOk@G0LK942iihc9j`~RL6#X)>zMp|*u{KD(`!$}#%LC-6^eqPPX^V)gT^X7h2=+h(XFMO5X4K^Gv4(bQXtA4P&>IciKeh5$fhi`t{&*ZE0v*K+(%RKsh_t~K1LFe7_>bzTCop;Nt^DewT?>1kZcgw5uZs$?wJv1=iuaoN|yj~y8%lg=P^zRsxKKIRUf9DZi|IQ=4{+&m7ectcC?OQi{-pT8J3xCq>L}34uuhRdDxBV~ksQ#~9)&E4$c@)0NdG}`c=8x`6s_)m>6Sp5*aqa=ngVpj9ysQl8r&y5qh!6fLcFdFi)laeQJGT3Oe~SHu(eO)SFJR4$O*J;w*c7aZv022gG6v3MjQn45%oJjL_lU8&#_&6D1IB{ktCMSG>}g|3j0M9#$9&{AG}fB2VE8A9;jtH884HF_C5G?Exw|^JA8RGicR<fD77X8p+VNbqjm0q*3}1t~p!q&yO&JS@uSZ?b{EV>_#)9E{QWrG;+*p6cg5iHgZP4`)>xUft5cR~-*J1rQ2iKvVru1!Dzo~=UQcnu~0M<`&@Br%RPao!*^>=XC(F)(r*u#tk!~cZ3YLIKjSn$KlX-m!EIx-gAj5!0S8C-Y9f;%!NOwHX{KkVS{%xOcu9difpyPmAuky`4ob`3rkv_8jm=)nC<;hH_cb;cT3=e}T1>T(}zb8J73$JlNhkFgCo9%Jw2c#KWrc$_Wt`P0O$83Q+9jQmG9rWG;1J7uic*b!qV7z>6!OzyO?_l=!pEExVn<|FqVV`mr(hCfFP|ADc~j0MAgObmaOb6<AwRn|I7f6-VOW5Mw6QahgOsIfxEg5is(3!496tdy}}_~X<C%@>SaV=Nf{BkF?YPmEn>EExVKwL#ZO)-QALN$M%2KgRln4n9UbrS#`nztq9!splH~4c5Qr;2YF)oxXx=cHO}hj#l{hJiH5Iv0(T=QdbeVa>jy7m~)<*!Chi3xSTmRs2SW9#)2;~r-GWVuzrPuuQ2Cb^6xSC2EY4=buUrNG1e~Pb3yBeT!)L?&ud(>b6jVv@nP-@_N18mc$8zWay-U<!0{OS4##8c5st^$vmB4Jg+70u_zYv<6O566iepX_<GT&U))-r1Y%OEK@XN?;Hn!8)R>p$i^O=v_b;h<Z77V|Q7=Dkj-HZjpA0md|&$)Lyct2}xrGLxV8;k|RZ>M%V*D7O684HGAPF>Kv(%44Eg5iHlUC{idu>!_|;rCG&G{0@^0As=Mzo$0ndY$#(aPaHYvy^@{>o0ZiYU<fYA7TBC4vtVy0sTSNFL3Zd>N!Bamuq&w!FwI8@H>pHXDk^0cht3<+$P3?*E1(V&ER%17QBf$2dNoc9%I3~n6sCf^H_hcgY%fPo%{~w9^`lXSa%n-tY+=yd@g9s=Q_N_{Vd>`ZR0v)jhAs>uqSJ{kE=L#KgVP29*)P@bsUeeD>xoww{kqr7W#ZA@fOCwYZ)Vd1IKJ8#&=o9h8Y`TEQ7IN_!r5IGd9gwHe<o?^O=v_SB#BkEEs+QG5j23vl$D9UqTGOfOF4w@B-G#rk`PKG-JW=6R91~^|G-v#)9DoQx`P9WNZ{;!SKVW3!0}JTgX^2{A<(&&A&0Wh_PV!UsD@&jbQ!J4jw^0Y4k%`Kh42Isb>`ZB-S70;7Qc8kbW`iFLdx?>RCiTmut4j!E+t0@HxgtG8PO!nYsp(8^c)eNajqUW^gkZ3m(Iq#ncRL9%I2XnKPG~=du1=2hU^9MDjVzUCi%ZW8In5GL*Fk^SPjPKG$Ie_j4iFYy#IAYy2Yj1$#1#`}i`)F5q~Kox|}M`wGWn>=2H}*ldo+*+QRBBOcEfID;|rvp8lPF~0keu^$?%Y3u>Ug5j%?d(>F6vBwz;hW{z^k^7*r#~2HS|1mNAv&K3x77Ra-7`_+h?&RQJto1nklg1h|77X8<+VNcXc(G4S2gAox7c~FCSR=-Q;qRv|Xl`$;H)Fx@J*W$spEuTrv0(T?)COG%tl!wd3Do1!*J6Fo!L_KT5q%=-H*#<y_4KCi%lf??+?RU#(0AsV^>J`#M=N{_WAzyehHpt-@#LB?7F?e>iPQ}4DaL}EFsCmygX_Xr@Kem`OwC<bzq5n8FsC{B7R>F-?|QH<=1NV8tCkS|pZ-hYzdyP7hpO*CDC&{^pU>QpE6rT?$F$Ux8t6aMY}KNd$Qr2g{sj;R3#I'

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
