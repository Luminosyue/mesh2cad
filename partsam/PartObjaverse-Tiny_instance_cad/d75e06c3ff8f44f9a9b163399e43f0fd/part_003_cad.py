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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/d75e06c3ff8f44f9a9b163399e43f0fd/part_003.stl', 'relative_path': 'd75e06c3ff8f44f9a9b163399e43f0fd/part_003.stl', 'source_sha256': '3c46516d5a4274bf5a20f0acf5cf465130b9b4b0c1d5c372e0ad43d87300adf0', 'input_faces': 192, 'input_vertices': 119, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.01576417312026024, 0.22450584173202515, 0.053657740354537964], [0.06505973637104034, 0.2675151228904724, 0.13207603991031647]]}
GEOMETRY_BASE85 = 'c$}q}2~bt%6~{l|DY7b?#0@Xt<FQ9T6ma39f(xtS0x033f*`W=L5yhBo0i0+FlbCMVhBE@M4K1^jYbjm+PIP$lQu5IsxOHXjg4bVI+%`=w%l|6#%HIU>9lX=oB!|qJ)C>KbH01u9W#>cbe@7gzT&TiHFx$p385`#;VIS>n5v4G7gUCqRaD!EVdQI{$NEOv!qkjx8?i>LH>@bATy8SNNrowfF@{jdP*`rNGUb=$m77)+Xns=u>dJxvzp^O5qF~^AU_?Z0s1y|xDs7Pd$B*Mc3F`WBTjRA_QoBCYRJne)Q&TmvV;g-R@-_M9g$V~WmAAe32KlpE$d@`KidUR<4WyFzOjG0b(hn%l#LVrKU#;alx~2~DAN-blx%WKzs$Mxj-yNklNjG{@9yy`<5NXZY9hB$729Do8h4ZX)X{75e^PzZiTj^nn_ibeV+-<&Y*M6#B{nK~ktDgILzrXLN`i1L9J4tuF$bQbgcKW{mGWqI5&M!O`d`S6U9o0nNA3daa`DphCTyHJ=<|gtjXKE<F{Q9rRSHI3AU)Wc_M{0SSd}Xf}=f4qtg!J3tZ<BxaH0NKb=lWNFLB6_q6Z^Xl?WefYOPk4`YeRV~V>-ES9);v94tCt1f9Q^q|9RRjx{ed-^s?tUj=ayl+hv}wdj##v65?Q{f1lRQ_2=!Qc_}7|d^zzh=kdKx`6ag~^40#obDfhKXfBeUzU8So7X18uYhT5FE%8UXDF1~Z@|6>PoX4hu`md^!*q?ZV^Z5DGe$9)rTCC5f`GrzCCvt5q=l`*T^9&o!=Phb0`#s0WH@bFGpN)~;yRGvpFU+R7n7tFom;D+!Pj=HWs`qdv`Qm6V=eet+{TkoDyW4t>ihmRJ(|pgRmEw&j*iZ1MzL}M9@|D+4vVY#4>an=wk}uaEVgG7T=Tm;z$Lt@tMb}jyt>rxT3%H-f_1)yZ-pJR@Yv%fI<<mL0^tt?+;(vIP=WaiU`Y%oQCSUbY*>6}+eU{E<k}uCY$bAkxLUR#28`*#PET5CF`nmq+KV$!R2+wOw-Eq<u_crqJ91wp=p}9zn68TC=F<-Z$uZ#N{)Mh<LqtgQJb3i)BAKS+DBsI{yEIama{<cHxyVTQpQ1n+g{>CZpgYF{DMeGQFhrXi^YFIGs%RDiGe8unbCAwa9{RxVHWiH2yRb0QZn&xN;ODA9bDvIm>^gf*vHG3=hLcYZHoRp|P;-h|!?>@lu+SttZ?+-zH=(-ozaD1{o@2e(@eEDV^&;4{M-!C7Rb9@A!H*;MUofBjJR`%~ap!y}lLpl$}^nK)u7w3>~iQagU;{Nyr`RXa0t8MoW^8NmZ<G<X=eyWMj+hYA*^4-(8Z_a<FI^~`X?1$=jU+1c*4|3ft_6t|jbw$7+>ZiQ!5&OyOIKOx5hfn!CdU#&lBj}t6Kk*xi>plDlX^mdB_8;HZ>hVMTd~OdXUtZ$Fb2;-3%}W{F$$9kkJm0d-)E_0XkMoS1&v~vz^Yhu)^<B~td$`ZHYiM3#XfXN8-7l#gORp{W^T$N?=UuvFeV*l}EY8z@j`ub53O|>AS;g^N#!?<*UyX`6aQr7ult<}qru#^V>tnynkNbQ(oc9&zO20Gm)mPacyoBe~nnk|SIFItn8P~ba=_UNTG-nal>F&&ZxK_))b2s-*YT)0a7_pE3y{DJY&z3mamuk_Gua+<4`&5djIVzjH$ro+EpzEq0dui^fPcZwVHeaOtH}CKq$2V~PQJ1-&?V+?^c~djTS0AHz^PTzJpMX~K<r#Z<E)R3~zHWTPzH>DDp)oW^^_DyR{wUw&b3c2t=zNN+68Ylue#$Ris;B;_;jQf7tK)t71oM4*We@vF>D<qE6Zky;t)KlFHay>uB$|tOMNhxmB3sY<H5^f`{h!W{NumDB8=~01Rz&d@Lj=XE4{ABj_h;DeilRD2d;|G%1D;E_oeuN$`Z!Pe7QXK;6!N^bd-MCw)LfoRQ4{r9tjZ-{xiFRMyywJy&M#qq$<5zUTx=89FE(<X4w?7cWXp3mUEz3-%aq4>x|#dq_AUFn+^8Nkw}JXEmHF^<`mJutZ?1ZY_iKzIUtAi>=kTpzG)HAf4Ey&|xX!gr)CVakm-BpINBfdmyQrV$(l(BdJ;3+7C7R!hPVM3N9v#Jt-RF<TXFT<mzvi7k+)*5~S1KVK2Hx@u^Q~U-HB<XM)_?zsUp(Qzd&Q59{C{8Ziw0^~KCtq!G|qu81?Pb0Ll=SPgOj1@;AHSj=v?qj@Kopw@KkUNbP6~I90i>Sjsk~4Bf(+dKxim95bO^f2lfY#flA;p;Nb(y4eAY*z~11oSQ-aF$AJUD;m}ZUI5-*_362I&hE4=e22Y1h0Z#`fL1%!Iz$wtV;1qBsG##7?&VnuiXMv5-rC=kt5V{;(2rhvZflI*USQ@X!(s(5_AG{Kri>2{GXbyNGI1M@<oCZ#WCW8~f@z9yzcyKIqDmWG#0gVAifJ2~B;1IAL8V1&beW8J1U+`$CKX^2F1au5|1lR*Q9P9yh5l_ym3zo*(V`dQ45$XnZ1iM1L!LDF0=vc59*au5v12h0^0FQ@;gU5s8pwZwsZ~}BPH~~BdIvqR*oC-|>r-BziQ@{(r+0aaIHaHKO1<nJnfEvLoz^kBz;8oxXXbHFiTm>x$SAo}HX<P|i4Xy<L3`^ru=t^)YxB!|9E&wmV(s&+pA$T5mHZ%=98!ST;!7_LfG#)$&{46vU{46*K8UYRh`$0p%e&A71J$MxO8K^J#8L%gGG}se73_1cl4D1Z`06T++KwZE?z=NR<;K5)!@#Ma;!_wGB@JCZy=pe8ySO;|k>%jI<SFk<U3F-xQ0=q+fz(b)Up+4Y|;9#f$91NZS9S@!Wo(7ErPXo__CV*#wGoW+88Q{gxRPbW(bI=9g=fKOL+2Cd1VrU+?7+eNj0WJfZpsT<p@bl0La7MC?t*708`Y+liABBc%{U5gf`j=0?_F4bsHv_qTdI`)(9;BV4fdgSnH+PFRMe$D^LMJH'

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
