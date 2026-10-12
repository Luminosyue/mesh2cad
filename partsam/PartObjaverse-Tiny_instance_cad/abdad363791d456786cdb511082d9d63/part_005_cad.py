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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/abdad363791d456786cdb511082d9d63/part_005.stl', 'relative_path': 'abdad363791d456786cdb511082d9d63/part_005.stl', 'source_sha256': '15b114a4643b6c3a955b86aae5c35a613c7f73e82bd8096bd05210cd23fcc6b7', 'input_faces': 192, 'input_vertices': 155, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-2.3122780323028564, 6.687406539916992, -2.5493834018707275], [2.8588345050811768, 10.331822395324707, 2.4152417182922363]]}
GEOMETRY_BASE85 = 'c$}q~X>b%p6vt;14v8qBQ6s1fBpQ%l3<yLyc0d!sa6~X73T9&1#Q;gjVU!~>h^QDjybzDlwe*9iW%0qQ%40{tqe`VbJ|L9HqToTPRS+U7m;HMFZ|v@@mZeL*`v3aBFFoD;dS-fy^0Le>*;eowV10Gsn#z-USr$c4E8A*`H8$5&$C@sxTeLW0^_D(;SRb5PF{OM~#A>mY=Fg2aRX65eX6KKI7v~q)`SJS3=EkbJ%KFB+G4e~R7B<C%-*j`;qL^q8DjG4Oz#cxhz;3nw<0nfDA<?!x!x!r3ROUKDy@{v19aa67o_VV8%=#=szJ2v*&38vV8d3XkN)LaNOyj#7m+aT_(SN6W_?+*@`%2#}j0V?rc%1E)Iv%H^zwF2K-O^`%q<kymW9fU}R^+Pvuy4;Fs`c-$DY4Y+I$w<4lT72gdGGun$5W6cegA?dq;D;MGgDsgc*lvPa$V==uTsf0zB|U1{jksDG4t8yeCNk60{^+i(oY<&>_XQ~Wxsk{uE$ne_V15d^M~vwvoY}ZZVLK&{+(c)4;D$^ir+1LJ2xi#@z?!+EUDJ9ckAJ(>T|u|Cyab&-W%;n)#tjycT0Ck-+txAfwG^H9daDr%e#*z)jCex{HxqQhVLYPIVk(t{MwPETCa6yrS;uWJ33@PUlt$H*1uP)=7;MH-!byV_zxr%KdcvgckRgE<-DzFGC$RQvs{16pYxl{Kd@8I*E{uSP>&hgJJfaaCO>r|s``9C!uO1P_nBS6_>6q^{kE(Qb=|y%RmX$-NcY_jw*=!{I{c8jZeH!2W0ap-qWkW9kIQ*lGq$&@>*GEA_0g!}hxZqJf4ZKZ`sp0m5Br=S`uz*P*Y?$!3o{(m=Y0j=GxGiMZNdF-<g;&WoB5r#ujaoWk@|`5dqX~w_gmumTlQ)DZDCH3Z}{HD^|HRs*6e-ieEnUYSdQZJeA!QJ(etg-cgp*Oea>g!-`}=I8-MkdV7~Cfb=%Mo(R^Mv_V*b56hAB1)7@kAGk<!f=5s&nZwvfzKjbWv>&AY#9}GWS&xW2sT|Ur#zvO4R&er>S|9<L8%@5ZTz8f2~H=1TW**DiS5!ds%F6^82^2=6B->kboS@(ILc(n`mMbqpnw@&xNeVCl^UDWElpF`i=&%U0|_eJO%_lrNUs$HFLc;CS{??)?7&kyhSJUyR%r|hkEbsfUz#$?^+=ZrP`p+o9Aq&^6qOP=9-jlpxw&8_NC=gZH%&^MlkZl0d+O$nZ>q0i4-_^IdK{X^Ri@!&bnez+gt`<wK9@qP^Y-K6KUZ?71CMB68LfBA;*76<Pye`U>4ZJ+RaaFy=6lY;lARk`w*wjc2R4SnOioN)Dgw-4U$uAa}nzis&mb-sLVVc$H@SfA?o?zrGQ!+y9v?6+je`^-F#r3|0XW6u8d(l^h0>~}ivHN77A=6SMN_uYv&PfpvdT{k?J_P<fyujY9;^v!dxt>=g5WLwV<{qY+j>Uj7ZZZ}_%q4v|sH_r3!+H(1v_P$T{mEZ5U{Xkm(t)T~1-&(n`A8BgH`VQ4keg4CMbbi9F7^wC0a)s8vv%WAm2O7TrqIXdB`MU1$`+rq^zOL!>b;JHgwscE-UBeHrYx=xCrqA<&-)WqNAFdDlPUAOxGym`AWv+8#@7L1z#~ljBx&2EyuTDPZ+sVg#*|&>c3g-2+-=XGvhu-){-|Rp1ssD2ASM*IU6z=qTh!hb$#INXhmGTpsO!}~<{|Q}l$-nyved)0O`xAPj7{kLN9ulz;`iO|fL~Ou!k3k<5aUYFc#9d(0HWByJTtwUnCS57w9uccWJOCzLFJg^|bt3Knldcf4O2pkF)`Cgz6+z3JC*lk+>8S|fGr^>%BZ$ujllDU&=i|FP=o$Df8-4VH(%-d;ST14-n6w2RwQmKJF2i?}vj9wbGlIAhOgbAuJOfNxjv#ixq~j38BfzAi5X6JQq(czIeZi#XB8a<!Nl!u$N5G^R2;y#F(jExn95CrQ2;zJ&>4ga5;b78{2;$4Zq~j696=2e<5yVws(m4p?S}<u1q82r(f!>N*QT=WQlP*TBmMBa*AGKPbFzJn`Ri(nD(^0D#3X?`rD@S3{OHiv33X={(tp+PhdNyj+S7Fjj)T*n(q!wxwQJ6kmP^)eVlb(fI<tR*g0cw@6FzGPVYPiCr6Hu$m6(+p~wW?5<)J3hT6eeAWy45O7x)e2BrZ6eh@)i-diD(3q*2ANA1DLc4-%(B+Oj?Z~z8*|E6G1!`Oj?E@E(Md8Ac!vola56Y4+WDJA&Acdljb6bdxA;(Ac(tzNl!))p8_U54ME%=OgaETTmU95L=YE)Nk=1yuLP4$LJ&^_lTJYp-vB0^g&>{>CXFHHp++$%)vQiLGiq4}rMlgOHgi4db}ib>)u`K5Xfw}5-L62JxeRq1gEn&s>UJ^O%wtivfoL-qp>Dm<X3j<3ve0JkgSz!boB3qa%|@H~G}P@Pw3!E>ZkM6WT!^|&M4Ndu>NXi|=1HjAb!anBLEYw}%{&WrTZA@q40UWqo4LXI>wcyCvlUEA@6|Zk%%t>Qy&i35QhKjWMVpyazGurK8QGbC_g^4?eLVTlRR2T7{7e1Vr~YNB=qo$~mX~#v&)p31k0u$RC${w`#{V0i'

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
