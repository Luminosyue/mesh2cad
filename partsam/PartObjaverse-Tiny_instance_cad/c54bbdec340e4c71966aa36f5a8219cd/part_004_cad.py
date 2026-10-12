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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/c54bbdec340e4c71966aa36f5a8219cd/part_004.stl', 'relative_path': 'c54bbdec340e4c71966aa36f5a8219cd/part_004.stl', 'source_sha256': '45e21b1513eab502c3c9eb4a38a567c684a8025b0438d65500caf8dc70dce99d', 'input_faces': 192, 'input_vertices': 151, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.03999602049589157, 0.298626571893692, 0.08165250718593597], [0.028010837733745575, 0.42428281903266907, 0.11800780892372131]]}
GEOMETRY_BASE85 = 'c$}q~3shBg7RC?wegcY`sc=*j70Fj5Aj-9bQU<x=0|AB0%ao_`QXa|yQ67S!B0fsJN|QO7Jv229yVaB{(s7z{#?)nZ1{uv&`N*ZE&EuT?eHM_j)~uPk)?VLte{A-D|M&l#bGZw1NW1o~3SNVirtG5EUhSzUMs!zPmE5Gv>?H|FSx=-d&2vzkg&VJjx@qRzP;;b%lB*PWCMIPiWP19mo&k$|Jx8mai!w5^Gvm@@GcpsC3?3Ypnw6yUti^Flll1o^#`%mJtxgy@T3xCBkFTzJ3%2O|m*3OXzS8`8psuDb?jAN&Y03d#Ggr7RzvJ8T^Ne)imYu=Kx7<K}*BIgIhknA9<gbO>cbSD-r_UCyof;-}w7|)z@9%~B-d82xW_3XRTLV!)=^Npe)$8`iy7u{~<B~3QY;{G#?UmtJcY0PUuFgaMrav<OSTgd@g|y<P&!UA}?@vMfxJ2ZC6%PLNSnzxEkpF!!`bkx>ZpWF(zjwka>z<keo_j{PQhHdpW%~l`xBfixgQ|pE<A)=^>CIML-4zM`&TXvQDN(q6pAY!a)57h2qQSolL!Yi)j);1MqfY%ZShw&d@&kN#%DRIwPt&mBlCKuJ2)B4xkiW)HxFvMM4yn_K{*}DNsQ-1;i;~|E1%544xZ>_F+*%WlI%kW8Tkl`mDm<BWP973&@As*2wPzyu_!GiymYv8ygnqQd53%l{6yf&I=b?W8M&YLN*XyL8kqc4h%5|*!+a1E~lTlwAa1-l(m52Pzv6#aJaODkKt?)?HG0h!tRPsOD56(WdDpk0(!eLX(eB0R|;mV%d8>Rm=?(5?a;kL-<HngfAmL^<H3lMJK7=ilhGFoxV4z3%Ng*pWjz<bAG-L;v>Z~pyysq-V}>|86{<akK9bq>$Bd}}NIa9_$t+rj5QSt<FvZj~Ml!Yw&Ngxe1$p#Kj(6t2DET`u{z2VIo+^PfkZGkw74I}2Bi)FZ!o^cvxfLy+Gi9rX{p3RfNaAV1}I$Zx(|D*Qov;ikK{ke^mB+|KJt3%-VP*;^#sdKrCc$8VsYxQQiFC(Bdn*xF^|yvp5$TlV$Gy6T&#|9U6k*7`13cmEHle=em^@+V<k)5lK7Wd1WegsW3HPoKwyTc52cko<ADFHB<x3D>61&X@cc-bXjU74;vfE$eHWy^()nM{3LK!DjMDe*aS`!i#t=<DUUncD{eIMIEKYuN7C%ppNOAVDNx*39|32ubdZtXYsqj`}Iha`@l9;xN>vUNzuZ6!Y#KJ3fDgH0pE8R`D6EhUv_Q~9^;WD+`9mE9&|*0<rwfCo3L)<9^~Kf6>c#Hq5sBc^y%^El)y*r_uJakz(>s|{0?~AdH&SARL*V9I9b=``4?GN`^ayZoLj&B=rd!X%t0Gy2CojrzFgd;f9;=*;Cthde`O^0WxFWcvYhjb?11_UJThg!XNr)Y`vBa{N4V;;75PD1Fo&U&a)fJ`gK3v1_Lb(gLij3tjw|~HgI}1LANYvtO1lv*+<IvY_WOrPsPEJu+`h*T{OC#WoX7&<?Zd!#<Gi%4vBIrBhrknqah;s05#IJXS2{QpN*%Wp%<YT|=F{XZyzTv>xQzh+;2`SH{0{R^f4;EgIX=Aal&b~E4=Tqz-)Tbs=e7v9Mq9D&UyFp>3ObYsZ*yPUW(*bH_Bo(=`w0Klb0co{YT>E=sNa;1IsB<cxTOT#=IDy^O}dKwlpy49tP^fB&ncDsCDF(~cNu+l&Ju3@{yprgVX)M<C9ei=`+W1?ExhgX&@}0N@Jq{aT^+uTekz)=Zrus28~TaVH@$gBc-!Z#mgclZ*6qI;b;29ar`AjOub$iYhX}U>zlQ$HqHr!zqfn>K^I!YoMw##u1?!evNB`S<mkV$6IbvHf4!q6hj#9p-Qr3Mi4eJI4U~a+f*U22}asQg;+i_lZiiKM{&qn^Wc$`bTbCuNjX$j7&bU)_yNwjcv-&xdo>GlcHj5_3ZFT*_h9K(KdzXXr}6#VmT=;w(aP^ao;)bC$~bqBguOFzx;qJGpU;p#fK4K43SC8izji+k}Ka2<xDe!sn_|K1Vg$6LVfj6gqb&Ko5^Zw2a1%LFfu7j6l!Ykj|X)q$5?L_f)iShs4YaO>2=;J4;rKC2F){^ir)Q|_Rj+sA8#caK2*L5(suO?BQZeV)hluX&`QzH_c{)d$ZF)2nz6m>&F1xTUld{m=46pU0=wNk7BuQRjXz<{42f-164@sMB{4@|_MK|KtVK>Dz#Hzr3<V@(-{dhgzKPgrKd`XL=mwIrk~_Q*>Oo_1k6O<Bws#UcTF;|LIkzbI}2F?sZ@ru77;K*e1GwcWb|0)^+D~a^Nbi&-k~6tIZ2gr+K0DV;ku9qU29Yz`pGN0{?NBaQnJ!@P=aaxx?!vsq@AQsQ=h$?DwmK;4W|QbMVr;f#z1<ayun7UDvwksd{wLzvV89Yw;D=fX3^gKKd)}k|+PWueg5W|KG2;*?JENdL&Zk(kIf-qlVDWqYtG%O>gKk^r7@KsX_EJ>CMz&dNchj>NNUU^kLMg^oIV1K8$_=bw2$9`V{K(^eOcD)D`rGmeA+Zmr~c!m(o{KH_%to*HG)|4c$y%L;nJ`mi`6$_0&!D>*=eh8|e+LqOYc3OI<_1mVOm=CH*S;9BMXwHqSeUVfZBKJo+U12x=&OD9<&5VfZMjnLdg>hB}KrhCY@WMjyuWi)9!-gPKC0L0?GCr_bj(6*3IJnp#P}n!bWsLtn%5s9+eroVuRAoW6`&O<&EqmoW@qL|sK+M4wB|q0ixba~XzTM2(=2;2ak*44+Jmp--kyqsG$5a$ac+!xvBs=?giR0*2v>sTK4U+<!5{@EWy@zKr|S7=~X?&85%f9+p#+>6g>zQPb$t*i#<0n7){6<ned&_<pP&PwC-9KaTGw(vPQ(p?`w!$I_4C`*c0x^swlWsYj|F%lJN(KTqY)(iuznJBG&7XYps5^h^0ZT#sk<n5{=AJ)9Kd14B`|QeCJ{^e*&$^%$UsyB-7e7(`X6?({1C5IsEg@X}+19>b}ls9yA==)Lvu(_^w8{(4NJPN7bwpF(e9OxNQ%J?2m&snh8r>7(^nqQ_!A7E+_>7t+t5PN$ziA4oOPo7h7j!|(xAKl%WAU+R<ezVs8Q-t-gbM^nA%N7Ij_deV=iA4c_{A4WfvI)r{G{a~s){a|`G>HvB-`p2pL=^v+mjM|s}G5S7KC;C40J*l1Od(wB-qdnDu+KJwQUZL{O7kL@pQTgTCb)<HqccgDe?M~m0zJneesXeIO>3h&SGYsF0+Ks*!y(_gVy(@ihstbK@`hI$tLmV7k+x@41QT+1Ki~+Rzheg}pZ2f0n%isLFUhC&S0?i>EjJ@hZag>M2ZsW9+e*-_|JQn'

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
