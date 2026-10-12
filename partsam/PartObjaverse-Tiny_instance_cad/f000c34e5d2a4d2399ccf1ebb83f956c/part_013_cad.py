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

PART_NAME = 'part_013'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f000c34e5d2a4d2399ccf1ebb83f956c/part_013.stl', 'relative_path': 'f000c34e5d2a4d2399ccf1ebb83f956c/part_013.stl', 'source_sha256': 'ab45332f40168239846d9dbce5099064e69fddbe832c2983f12767a96765a7c9', 'input_faces': 214, 'input_vertices': 135, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.07992784678936005, -0.3162822127342224, 0.4387797713279724], [0.0899021327495575, -0.2766067087650299, 0.44906437397003174]]}
GEOMETRY_BASE85 = 'c$}q~4Q!QH8OPt-QYu|HperBRvA#&*f-UrmLRX;N+QPu{QLr!y3~r%cKq=jADPL=O%LZ=F%q<c(9m(!8vPCyFQ($UD?xGnnnIY}1Iy1wXNdlP|jE;2CWcr@>{GQkM++kw0$&>%D|C~PWInO!gdGAdd>eI*NTKZ?Eb>lDZ|6}gmmZc)w%C-7hW4(KJxArXP>OK;(CV9U45&g!xO=}yPLRO!3EZoxCvpW{9vcpT;D#Jx~xa~l!H`d&>^FXYnRrxEMJ9}DPzo(<QyVd=DZfSW%kzGEo$nLlQ$Db^B3W+&==a#z~`R28uOX~N>w){c;ZoNHd`k4nj-(LS~&$lXXc)oM0!SkKpyl48~iE01hRnLzP{oKf(=)G?ER@*+$kJkO!^P`JSC6ynkU9F${$B*^+3Ejh<|3RbYN4_08?~R{1HXIx;zKoar_RLA=gZUHDMTT#k8#2~4dMVHJS(kOFz<93YiJz&~&)wUi{cCIVx@N64ed=kgZr6EUd^Ks*AK!jp!1JB7DxK%e!=CRvcQk3_$B&LrGsfH1UorAKFRd_qYu9))&+V@pb&FgoGyG_FhxV7;r}LbC!Sf@<UmXtCEn0t8=imDK;ox({_s3_on|}CVV;`gCuWJ9b9>cftzN_=U`(!eB9-OrA>3P1qQjb5oOwV)phkE?gTl%>(iuF1C$$4Gpi>GxR{#j%A{<&hkiI;w?^IUm*C|EbE=`GJs^n^!(>k{8CpFR>C??is7^OxA#f9j;+Cr0wL-~Ei?$8Y|~IG^#kmpy;9Aw!S<=oQ14^~$<@U*^v_OpLvw{q6CjQ6GH&zDRw<m-EK{ito>pIwan|Vw_vKkK)U|%l(R89yXrq%zskX^SO6*ea4oVb;h@cXN?5+-5GdKkIyOheCx{B^m%Bzs`F1N)Z^cH(eUNG$vsL`T+{P^eS&`O;fsbJzmc1~)A$7U-TBsZ-Ir!u*U$awnPkw9W_+mU-`JBh?j63IXRE$X_obURwJ-JTdfxEu^X*2R{qgKqqGPw|%f04)IY0ZW(Fdgd_SxHJKcW8dr#?3GbFQMbp$lFeMz0%vQhZsL)XmAsyb!!EGJo+Cw<hUxPM`Gs<A2ln$8z;NKgjlc=h<AH=fgq6mpuNu@a-RjMuPPeU;2!7d8c0QuO?my-WNG<;>&qR9WV2g`y#&7-@g}c<Y+(dS>rt@zCWLo@qT|}UE=%w+z#t~ccxzm?xXZi-{-l`)BW1-$kTb`{WbB7u8&=ypZnnCWbk~(GsC)`(pTww;>-O?+&p6V@smwP-;Ugxr~Qe)9SYVV^1C8kPx^qIXWyp}`+3Bt{<1I8SIV@X(jR<Z&K3Ecrz>=QQu>DYvhQ-v{qZOMWYpj4tJLQ+rJsnO+8@N1I>^4qS5%w#i2fOwU!&)LyU*w+qq%i@d}`mo|5V?=w|?>W;X93&doBC!ytBrrzw`(3Q{RKux%GNJDepn?Q{RK}7dCqSr`~t?iIz`{eiGTY#ki;PUK8K{oGIr7U(TWb{@S?BxOXy7@l)Sxqg6YM^We<huJgauY22eo&S{<JnV8O>^0^{<_@HsW{Jx4W>y>`!kN^HYy)X2=c=3RlpYt4_HfZJ%f7A2EzRNs)U-}IFA^OqFx}HyLF#FqUubaMn-W&IcdEe!|lT3dz=zI6H!T6SywPCFA3HQ5;iV5zwthVOBS1e_!AJIF1#oDv*zxs+*R=V*2{fhNPcMg->*yP3<H=5j-;YJQ>qfKxVV{JllE;<QTIv&o2v(V4LO7DiV;Cs=}!b<1CN~ge6nBTpG;>oBD+dO+Rng#E5W1kz#2*uTe;w9)FSZN!)1g=7Nz*TU$8)fLj=nl9GJ%H|j55T=>8{EdTdkMt{(S7hi_%NaP5V{vW1jh))t%Tym=rVXQJeN>hidMs=a515{2wegf!G&lQTt!_93B?70+7+O)-~#wTLh(vBR-?1gS@3LlAzB8PQTK&};%H!RqJ-jZ@^_QF8-FFy#az1BKbf22wP-Kg%Ra3o6mLKe!yDj@gyPNUA$T)fkH+9Hp^u<3_z`#)+6wQ2E6~O8V)na&P&|kHbI3ghzaA}x>*394abV8HfprzLR;5LOwHHwvrG>E40=R(sDt^d~qi!rkJ7A?N;HB{WgyL!F1MoC>Cb|lq30D$|ce~MpwxFxvRs4Mmp|}xU0XM?i&<=PT+(#%LK##%$@CickAo>tI2zL^Szf35uL6^cca0#I}54|7GgQud?;AzxoDxo+Zt%UR8`EKlVW4#;8(fROlcpX{^uY-@EyJ6XbBZT69^7oUwAAdcexDIWB>)=IbBizV-EFu&~&^|Z<HxP=qq66?&ct3gqZblvS1nj_%qJ!|G@D{Wa?qpxL5Q=NbUrX*<{QYPRydU0*mIUTp5?EIWYgL*TSbH9|Q92b?njffJJ~hr~U+d8I@NqYexv>BZ!wcXHbR4YIf-~R{nhA&C32uB2osMS0_o4ToneaVu8fw87&rTy0--U+ZyWr0ginpW3;O+2ZgyNHg;#25x_!Rs&p|~Ag0Jp<mAQWe#8E`h7j)ve6bx9`_PjsW9K9rW5{-6F;@b4eTD}L}F2dRH)e*6voWt*GJ|1jK8pD|t+JI#Ap%~QK#{R`o46T|'

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
