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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/439ee7ebf11d45739dbef21b91669c1b/part_005.stl', 'relative_path': '439ee7ebf11d45739dbef21b91669c1b/part_005.stl', 'source_sha256': '3ff94d54e8b2c27b92a9eb80f8f97eb206330fe191ee556964ca3fa6e0908fe3', 'input_faces': 126, 'input_vertices': 93, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.09488184750080109, -0.24509046971797943, -0.21280810236930847], [0.15452995896339417, -0.06960558891296387, -0.09104567766189575]]}
GEOMETRY_BASE85 = 'c$}q}2~bsK6vwZ)B%p~(Ad+&i5HSR0=OJ)GQSr&<8sX$)6h$kwhv6<)o6NOF(-|w%J2E+L<D?HkN#(*5WpPPMTq@^bO{r<F)nMv$zjOZ7dyUOB^_(;R-~D^;`Odf8``(akZrjdV;!mLTF#7Fjaqf~NqLbt;6&G0NOrKm(6gG4A{5Fyo`Qp>6A7qZp$j)se6-x_)rxX-Twg#Kz;K5Vlf<xutsk5wetobu1&9Y7@5dN_I*NX}azo;;Oc7bu-FFrC<jtmKv7t8<k<6*R*3>bMZ*-*=Yw;HNMPfZ6%mC`2iwa03`xVD^fYZU4jG~tl&W$V^DajlyZ$=7^0l5g1)#(s4I`O4tUoWFSl`C6=reElQ0O5r;KCY_=BPkd{resug{sx#OBH02j&k*^%F9iciaV#t?jGb_kX-*lAnix-`w>o1pcevMAPe0CepE6ndWjT?|#Me}ODeuC=n^WlEG%_CoKDXpdaifo#<)PD=-f0#`7J8twMUs+N`zO-lu<?Em3v;W(V?EB3oU+$kkzP#2;f10nxn8<fjETR5o%u8)a;{3;{l&@TEraq;-6wZH8%GX=wQC~`G2Km~(0?Jp%ouvPFtjZ%_4m-#Dy1Ja!NAq9Db&6*kqdI=}I%i)kS$}}~@#;hOX^~slPrPuH{Jnk2*H>&OUx|Lg``2R>ubclauAgV6`i@&W>YRP`h+an511?g&X5P*H-zd{5e_IouyG47**DLA|Q{Gl{gR`%M+YVAc-;8BHc^~I5xkP<x>Au{jX5)3}*}+c!oiy$<vV!aU@_RMiAHACQtG3dmAFaoE@*M|t&Tna?ew3`_1{c4zpV~w|cZb+l*Vy@-wEV#5?s_%%x#lY6OTqEHKRxX{Zp;(vM+scP=gNGH*R#gP=hL%^>gWq=`J60UMC+_rm+`)Lu4n(ImG)67tL6TKnz+x;SF@jVg6og`mdD-Joz_RPda}Rp3itmYp2kz}ZsO<2e$(YVSnBF1UtfOLW!?0uHN2kJ?vrmh<VNR2T`-*MCq8mnPd)smi?1H3r}a@h9`ZTKZ(B|4HghiZukT*T<Cc4puU)=C>mcvEO#MpfUC5X39OrZ1=N9?O8$O($Ii2g?yTpABPvQJ^9*xe=qXyrSno09l-~WVE^BBhYl?uNfd{&dnPt4>i<r#F&<@M)jU(~sIoWCiC*ZFQF`vXeImtHHSe8)b1zdGJq%JWS-O}?gmM!p>Q4(C^S@^iPr!q4xrcgc6G%H{WlV<*2KY%6%&p9?sz<Tk$t($;YPtHbzQovGyf#*OUP+xU5mTTAy@<SpD!<vHH>G8;eF7k04Uc`@ymcK-_=r(tik^Yd$IY#?7*dWhF^-tY$Jb#}Bg^SIyLt9SPGlAn0K(`$JDzUTLi(tL~8xpEgj4^f`9u4-Ki`}1bdwfyld-k*?1yzj{e`JA<Wk9^gshSn!!gNtw38%w^{w+D}x?M~x3x|qmUPDI*ho>Mxpe=do9DSkVjgHy9<e9Ovo&hN+P!*XR3zlZ!Y$X7R&Qytx{E1%oNSzIUfnvI{kK=wCI<UV)qr+rbT$vkdE5!Z=5P5a_#4Ci&4uz>4~=}r4$>4@hzX*uUd)zZGG>rGr|?RY!o?>W1VeA8j-Q!gweU-z1`pXzLFBwtxOi}U9nAYbiPPQIgPgWb7Li!F`!A!a}4|Jq1>>Nz9%IcO>8`s>SizrQwf{n8V5=RO^`GwoH`F2A})G+#_C>>x=Z+>KvdQ}dmEatTv>TJ`Baxu!?`tDjthB4YmMZ!VAaMh~KuXApwDpdG<xBSsoA0wH)fLU1y47+7c;I2jy`5bO<&0mon*Z)iubP<OC5I2zgwEHu=qekjHi8tc?UEczV*jf2L5g}w-m0|z4ncZGHbcLhHS?E-!l><R4*ZVPP(?F?=Qc7t{T3-tiIf!jbOaBm|9(2-*e0}BlY2ZH+|1P4H00tbNmAp}Pu1e>7YU=uhIAvgsZ1`b0{DbQ4~&@tc?@MwhKT!i3P5P~NfG2Vy?Mr0raXCnmXKwkz6%>(Cv$3iE9$AZT}$AHIyheA`qshH1Dgy4Y)!F`~;!Gn#6Fd_lkADjRVG2#Vi5VSvdAZiSP27!Z+GYA?19tdsiP4EzC1ULdc4Z$3TVhx7EYh9BeShFF>&w(a5t!IMM`X@N;i{N-@2)HNI2O0uyoxcx4a4%>OI0*Cag%JEaLa;BiH&|#O*ca@N5G+Icf`tZvWpEFK;O7v6{h<B8e&9%G6gUa0K%>A4I2~#Nr-Mg96Tw1Lz(PlZh30}YF<ur_0V}90INRLD&AaVC{b}H@k1Ad)E`KQa`<<>|Z_alX8<&56*=3vC(^s6E@$XHsP~y!l{Q>8ov9S'

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
