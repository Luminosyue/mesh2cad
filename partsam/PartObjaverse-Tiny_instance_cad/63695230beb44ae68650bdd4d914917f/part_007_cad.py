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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/63695230beb44ae68650bdd4d914917f/part_007.stl', 'relative_path': '63695230beb44ae68650bdd4d914917f/part_007.stl', 'source_sha256': 'a89a1bba1127a6c55cf98534d94493ac36d2b1aa2349df598f6be8ca2537442b', 'input_faces': 198, 'input_vertices': 132, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.007782880216836929, 0.37265312671661377, -0.13867442309856415], [0.0510893315076828, 0.4906315207481384, 0.07842972874641418]]}
GEOMETRY_BASE85 = 'c$}q}2UJy87KSgP*g#Pc6APjtQZ1AyD&n=F5zC`ku}~f$v7isf5>PH;W=ugzRMNmeutsA5yGFelhtb4Y#+8YPv0$6gj5WH9$(T6r?Eg1DXU(iNYv!%B*Z<w0efQbtoLk<*675{yL&K+&R#ADlQJt%%sc_Xiw0Wtvxfv;`S>0yMUg)H`i?2RUbmgcqBP|o0w0T;#uQfF*#pc_`+czRD+&9SEH!agP*OoMEYNpMas{E*=8Cj`zKWkdj>{R=)UvOwhkawtmkoO|*|MAmA^>DW?_n^}GZWsF7#c(UBQmUQJ65sq|Z}Agv&#x5!gbVz<H1W-8qbtPkp0Zf#44#TQ6}>+dzw?7d$~Wp=I<Jns^T%%!zwV6qW`psP@9leXllZYsbCj<a?38@tVXN)ppW1AbI-9~IU!PEp`lmB8B)|5N<d+@^MW06=O%wlKJJdh!wMG2Du1yoae_Qc2?~u<h-<9#we_^rIF;ASsI&2vcC;5l&i(eN|i1~h9-B<Ess^NPs$GH0F4&vwEM4gH5$hS0&ljFJzm{+5Wt>Q1ZD!y_3ZLH7fp%`~mL88nv&MLls^)Y<Uv(x1GwKv7r()ME9<ij(ij&mjaNtZFN!B-YYzLt+VnVZp1`uIFK9y=WVjhCg4u{rYha=fJl`ak)1)X%u}hUhPw&WJX-Rw?tmWO)mH?h)U7q4rbp$8ReTf6ABQ8(*H^ApV?*Z=-&i`1;L)9kQ=~x&+^Ai}>F6gDNEdi|Unf{)5#Rck`?&$&da;d^4~d{zv05Zr3@h<ap0=_!~+~B|oF{YRR7xgMMCZxl8=BJ;m3LbV2^tp?jpx>NN3<M@jH+xa^etNzO%*AMh6XZ?s0{Wt3!yZ^q6+eV@DAaX(CXU(WYg0N*QL`qy4xD84bKIsA;8J<s^}(y^YeoZpD+%<}^|z8Q!7umkVNxEt2MUl)t~RkP9O)bwKMuYm{pjNiffo5k0{`=U;M?H0*z(_@XC9~6N6gnj7qTF*7O9)plyd;{yYyPx<*V5?{QOo$d=|JE7n_UfdCqT83jud$rQeOUFG)H(JE{H2-jznZ^E>NKy0AG}<A(->4Pe(Xi~@egYy{|}SilR7@v&}ZBA;_GK_e=dHL79Yv+q8Bl*W*4zO!KLDB)32jW`LFXFeRJa-)N#*TC;s0~AirV>`gC0(>!X*sluG`^SCAhYdqDZ-8F%q@w_E7{vxs*beIv{b>(lwNT>simKk>E4TP5GH9N8+qdm8HGhN6D(;xZZc;tbTu?}7gJcPWxStFln%=3c4eJ^7g2r)Jyv@V~i%{O3#dieK<1d`lnHPaP@uk@;Xb#_hLL>eSsCxZ@fB+J5*eBeyyF=KZVaKO|iC*VIbkKTMGN#_-L!PKNA5|3%y3mxju|>st??{(bDDHsag|GB3}==<{F<{PpfhxX(`@KWYzrZOt&rfBh8v0vqbTm%L2;A8O%ya^0$S^Ep!ozxz?~OIz9SoEhL!CjGygk2+WXQYh!ObSuMsvJ!Rf_ri1hV4(Phenr+n|JW1j<~$Vn9${yt-kmn(Sl<}rpWA^t{>5^g8SCPaAAoVq_P^|x^{GgOU-1p{KRhniv$k)Z_*!}v`af}7_C+iE2>FkW;yS!LcenVhw`1J3-^1?`Ecdm(XczK-^_4o_>%WrcnCX8C`6G+54m}skxMuP9823oH%uA~rzE;j3-uPo&hhHH7WSm@YdX+1DYXSOq%9VMUQv<~}xX#))N72vwFNtsNjYR#^w)LWGqu?KQLH#LRF|X`R;_E({Sho^adF~k<b|Js;0`}#N@_mv&?hyRPk;recQR*0lU!k8hUg&2<l+@852gtr@1Lnd%nv6P&E#+88H}q3iCB6}mDZcUDSorC4<@ul=&q02-aMU?fhB|JSQU8aby#60x->?0Q{Gxl<uYd?VXI4Eg>usJqj(KG-J1G9;A=rmu%`vYAe@6cP(d(p-oYmqd{*;IL2V2G0Uc~b!v9)<f@^cHt*H2=<^c%b7y{=tfi8}k2z<1j8o@mUw$gjR!BN|&N-zSXQw~_x=t@zrdc$@rvW^36`V`Cz&+bt=$o~De3|Ls8W>pHf;Ixb#<{V&G4m3ms`{b$@Q65q5g#riZE@*%E|67luVli`<?yd&oamcj3M3D2urHF!>KtAYQ1EY@vR=xcI(>?hP;P=odPsYb@trZ?Om=eP60d!gRXnUeoPFY)zdU9pb?Hp=%Tt?Mx4&uRw0b-MJU7eyn#a5U<;{Fp1_ofrfELN@%koHs>1=7?|3i9nq<j%P?+a|P;Kf|2i@*juivi-*P6zN^MM9ClkFc`KG}l=?sRMgH#od2+qoKPA4obQgRdSF32z734o`g>l#YL%#PLNq(QmaegWCD`({&v^?|csI)eH_|eApJH{T3?Z1xFk{o^-DN}u(=)eDIlo9sd{WR(w{{Q|o%CYw_*B;r_S!AV|WTgwpN*9x}$$3<RtTdmjbO~AMB61#iA$1;E=?t>cndDcgHtI~W(pShzXOorAA=}9FslOvD%_3)U{_`1%bE!Gx9L_nHnn%uKPq_}g=2C5B^&7OArhYDKS|h3(qoqCE?a`Flf}z-xp|~}*CAlTfZ_QBbL3Jg2kXuokk(;rnRt&|>8HyWI8<HDPov97U4VmZ6P+X7dO0GwCa+tpp)s5^#)~N2<(~si%4r^4O+Jdaqh3s#S7d3SoLOYUQptfhUvquMebf$VS6hF^U{2a9%xgF1cj-j{>wG+7wxh=ILxg&dO%TVmiP#jJTB~PcuP(#U~%!{G=lP6O9Q~k+7R6nXe*`NLSIjoT%wLRI7>_hE9_91t1SjR3@FS1f!a;iO2?2$oDC#O-Z?9Iw~OeDuJtXvN(^QSWuPot)j(>ca8hT^IA7-^4}?J<lRMSh7ILX9G;=xL9x48=pJA><I|D;`XZphl6SI9>#`A32!Xo7#`uk9oZriia{3kD!huk7VB?7>X?n#oZj{*^L@P?nd^db|w3gyHEqjPp+phsvlXY54jIDkm^JBVU0j)06BnT1TqvyQ-_eF$-2W@>(mJHlQmU5oH~daOjg>1th6tA5IK_CgRHbWS!pk_(t+ei@+fLAveE%$rSW8?W5}b(ld17!rBlgDQ^-n_$dk#5)D*JPRPq#RGBuT~G=u!)K1`-s$;spi+SB`U0yT_0fgGzn-TPQ-AUTlxr+6GSjv7sl=03$a>|Y#p5IK%KmKsTp<T{R}P9{(0oX0X0CpfH20yUYO%=sixW64kYPN2q-$J=9)Jx1HZ675va!}&k`i~Q-wP%pY?{$c*FXFmJ&(eX?#`-}0nFO!z&2I`$>f4SC^FEyRiTSxmRw==Bg'

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
