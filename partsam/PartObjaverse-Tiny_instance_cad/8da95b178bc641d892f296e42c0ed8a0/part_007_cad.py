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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8da95b178bc641d892f296e42c0ed8a0/part_007.stl', 'relative_path': '8da95b178bc641d892f296e42c0ed8a0/part_007.stl', 'source_sha256': 'ec39a5be78d87da0ea89485f969058b02306b7ea412abf26df93608bad0c00c7', 'input_faces': 288, 'input_vertices': 172, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4406306743621826, -0.49999964237213135, 0.18751001358032227], [0.07199671864509583, 0.061702415347099304, 0.46973714232444763]]}
GEOMETRY_BASE85 = 'c$}q~2~btn8ON^+wnjywxK)#2jS>|>K>-)^xi7e&QBk7;vWXg07L^$56&2AaMxWqPmuE~OD#TP<wTX$(CT(3a0aGV2NQl!oNvEToCS%i?jOjb){_f+RdtYWc?VI`L|GR%bzI)Dh4)-3ONr}yxhib;ByB5;5ccmvp(?qn^LbX+yc?CJ?nfZ~qD~g(EA<`EgQ{7W%O-Y*DL|dh;4bRBTPtOY<5*9uzD?U6TEIey@UO`@3Zp!k!j7;H=OIwzo>GSg!r>)5JT|YM<E;=GCrgucxy0HK8^Mn{fVocp7q5F1~jSxDn^YsxHUrz|%C9b`TzPW1kwc&=Z^&Wpi@ju;EA+GfsUtdxD&kSF?H2$XImu@{Qu3cRc)cmc6ujhTM=1<pNm)A2jC11za<NAN3<k!DjDX(qyb$l1~z3#q7{`}fkt$pzO$M^4+^{aolYV~z|SAEP4HUGd~>6f%p^0i9*pq}b|zvyv9)?dElisComcl(o?Z}wqbw32W3!5jQo$=A>18uPW+KZ|d#KP{$8*0+scH+}o~Pn~~D*0J@+^fg<5^uoQT<@H#j&#pebjr@5_cU$}K_ph|yBd@=2do7T!yTfiM{#Tdw$vTn!uPXk1!`ByRHx+--`?AljlLxLSek}f%<!Zj!=YyF_zS)26;WZ^+-_qUKhxYoV__q4`Y0oKHzn^XVZyUbLHh%rmqiR{l)*sV%+57Y8+FREC>%VLNN13nB`%Gv<R%UG=-#dAKoz>Uwwz(~RTfVmr-^|}~;SVxD=^3L=M0AbScRijc^F5|NZHM%|uIxHxJoq}kzdpXJP19S-c<?oRkC{JgfKfm0NjV-@L`c2WPwkm}+v;npTU?g+?eyKJfqX5tP|4Q^mU-p%sEeN~^TpR%SKqSES1a#o_|+AkEA{cc2kPW~8@|p^@?B@Q8-2F<x~Epw4>Rl341HhbKRrsVkDnS9{)v+BeM<V?7cLw34Si5!^<Dowep~T(&wfwd_tANopW6CFZ6M!!?{1yqC;#SlpnMm;$ILIRz9{o^e!Qdf!Sw%{^NG@jf)C%7{`HIXvai|3ez5xu><7PJT=lVa|CqiDUpMprb?+USxA4pzr4RV7hv$s(nEt^8!;h-Cqs$jy!}s^c%#W;<bzJs*eBI11>im28^HVO~mE$q@6}}cyRio^;Ud0!r|6t=?Wk2BSDPPqn`{8d<=Vkp)L2AC~56Y-j@;mlCC+lxGTBod+>EHZwt+HN!|Hp6TeZP#XQ~GK8%ZA)i`uT99^u61H>Xd%s>-heD;-`L)eoN^mei**LpE-R_%j?HKexd9id>6id|KO({sr^XyIZMrNIBfX-{gXPeT3%<@)+_6U@3~*`v9eyzHdM*^TrQLOsb-%||CKv3Uo-t94^PSKlz*%1g|9zYUZdonkCDEM{h)ory5M`+5B~MKH20*ebL<D>ebV89;)lJnv{qTK@?hz^u3T5w%jWyn3*Wo>P_43F_&UCSz2eWh1J<|sUR%DSKE9*={ci4n^Tl_}_q)Zr0`?Q%(a#C@b_QH8e8+l?8NNN>elUIeeweU!TfqH>@7QnsJ8TTN|M4CBAK$V6@g4iWDs_`k$L}w`<M$We@%xMK`2F2?e~YYRf1a4W{dw~J2gbSI{=71M`}1ntLwW9WJP%FZ{ydD0KOoiqyv27sZ;N*wly&US^A>K8P{(@&-|-$X^X=~uGvEFmdGGE~d0+c`4d3xzJLfqj$8Uen+I;^$xsdmU^zH9))3?9Jzy0t{>D$j0Hs3#A)3={1@Ezxh8;SD#?KtP)JI*;PcN)I^9EI;VNA)N%{$8@5>+l`tI()~u4&Q#R)Bn=>ZK<|%sp&h;rK!1R<bCbuUVP=;o1}cZQFSeLrWWi&U$oRhwX8JDR~zylG|jJpzuL$d_+Nds5gi}@|9-Wx(>I3KeeoJ0xDq`H3q1u_!Y2s9$I#>OF}MtU6)uBcMt=pr3@;%BFGe@Pi{T7Ha5}mX7OKPPa2EO!oCPoQ#e84P^F=PY49<nupfABfx5I1TZG_;x=&#|u@KN+lSm+z@QP_hXfIV;pA$TkL3cM9wO$aVRcfm#QdUPMW9^QcNhd02*=uWs8UWe|0*THLjQGk}9JKz%7jlKp8t%Tk1A@l@%2tGmxE=P~S<!~ul1`B-|E`?VSg7eTNa2}jW2%dv3hUdVu(F}MtJQ+=gC&P(o7MuvrM3=!r=fN}KA%x%w=zLh{R9NUJcmkY&j)W87Vd!{x7(5t#9v%!&^u;1HjS!rPJ`ZQYOVPRTQusym1^7jHIU#rfA$S@(1)c_vMn}RUndfLi@K|&zJQki#2u?xg!zu7eG#6e87ouxmq1)g>cncwT54soL10P0@!a_apVfY|g0Uv~S6M{FRTj9-cKDrvths{2(ruRaNENfB3S_xfmS-bVDt<VjYwHBO)7Hf@rL+~PW9lQw6M%TjGaE{ja9LXUBuOJF6<1b)NLQ5=jETIQN-IkuXEq!y-OQDA>y*)(lg&u*0mRr`PoHZ0$YFX1#t#RE27ow|Rp?O;4J`ubUP1PFrnBWxVxPW=*pbOCju+VAnLO2N>4JW~42*Kmfv9QqT@Hlt|ngXXVwi)Ogcn0i3XTvUdI64^~4i7{V;el`rIujN;1df6GqZ44E39!&%aDO-o9Sldo1JH@^0C<wt_`I7$2%d#z!?WOIGzZRMJ(3B*BhVyx1RRHsfyb~0afIM_bOt<w{>Br6W6|MoEF6grgd^d8Xbc=fzxtt3a6h;&IsonqN28PAN%SR}5Ihu3hLf59P&5u63J*f#;dtgVh!7lsM#7PdH3IDm_hlRr=umhNDz2aP#V>skN(gR;hQaON5cFv{1P(^K!NG8Av@6^iZbb-ggFXeff!m_bz(TvjZQ&;g!R^r=aC^7|+7lKU4tIb%p}pZwa2K=>+y(vxA-FU89NZc1i1vbe(d&+ADBKZliME4V!apMf2caQw5Znw6hJ)#KGeU3^La>Imf?Lsd^CP$^A-Fl(7H&)5n-hXtpzYxn@XrasPoN#(q{JpoL!157e~mYObTM${Kg#Vtss7n%{mFV?E&m^(Nr^#XT)v4ll`otwVpnPZ0j4>YV*'

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
