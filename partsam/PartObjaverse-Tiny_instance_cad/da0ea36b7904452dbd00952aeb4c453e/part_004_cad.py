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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/da0ea36b7904452dbd00952aeb4c453e/part_004.stl', 'relative_path': 'da0ea36b7904452dbd00952aeb4c453e/part_004.stl', 'source_sha256': 'a6fb2cb9a7db0f8cf99ecd8efe8ad9a957fabd4a2e1310b9464895f36933c74e', 'input_faces': 245, 'input_vertices': 183, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.352628618478775, -0.40864500403404236, -0.4999995231628418], [0.32526880502700806, 0.355213463306427, 0.4999995231628418]]}
GEOMETRY_BASE85 = 'c$}qK32;?K7JZPgM_CLIFu+d&gg}Tu5(o(LSd24l17Qcn1o&YOSs-EOv&%X%AOQw2tYH}e!@g+#03sqPglz~BGHPMTjHOb_%m4+`_x5?6-|e5OshL!rx~I>*|Ni&7``*|8rEkxGz+g-Mg;^m}THM@S)3OLbR<M=r&YUuClshXXEq!`9s|M@z=h!uU2KMedw49Y~&5RuF&Ki{&*})arF*PAF+7+2PIde*8O4^%~Ge^5gPfVGZ<raF@*pzg)7&mL35F71^jf!^7cKwfkRmCOb<*dF@D6D<u)Q!%<dXk>Sv&~t;y7$tK>om5;KWk0a&Y8lx=aPqY*Z9gC3;pOG_l1pQz1f3Vx6Vzt%6SI-@az@(-i*NOtamuPpYwi~U)<SOPq=n~<G*cNT<EKZwLQrCk7G-;_(u0w_x_MvqQ$qmafsueKD(>M$J{&Y=vsVy(h<({kBN7*__(e|r9S?S7T@l3soy$(L(^ZDx>Z~%=QZQeHP(wF*K+*5D#e<9Y0Ns-zuA4O&{zK|H<#nS|Kzq7Up$!S*Z%&>Z7n`1XglY5oN`x-4{E$q>gjj2_>d<%<^1o`uO}pM7mt7W{7X%*6PnNQ-?l5(@-#f0FV|&EiJs@1e3_@@OD#V1$!^YbGvS7&H<r5hW*2?lLWB3n^-U?!;~&cX@XrZ%wD^d7@5}X?a7T-8l35_v>tp?Uqoi&X-{tSkoA}99x&QNcKik;nrk;#_?wR-@>z)fsugP%;$D4Yo`?y@UiTh-pbIWC2M9aExO&H0#bz<FR&NFH6sX`y!1KpbR)hWKtF>{Li?W^Q58Abl~k2Pkf)D!v~^WC>f?<jR=-<GEKk-F>WJ-+Lu^k!0b)~if^pv|+=qaWz=oZ7X>-@aA4u@Cc7yGVUj-A~z`xp=wINB7K>y8Y^>f7bLFQumy>%JXNZHZSs5cdpb>sT+Ms=|*2ty3v=EZuBLk8+}RXMqg68(U+7Sm#Fn6E49AVjs8&Tu2tl(-j#0DwbG5cR=QD-N;m3J=@Iv}dMtHU$GS&reM#v?-*D|5eUaC1&S$)iuH@wxe03XoX|MZ-wD{Rl_oi&V!1K0j#aVy*)>^jstiOF?C53r8|6g-%^5+Kqi}#6r{9+-0Ppt-W{Mq2Y@b^4j&${RSK^b2%l;_jRTq5;_o#gYOa6RkZX$h>Cj-1Ew-VT*ye6JAJtske${BzcFeoyolA97reM9$-hs>JK-UEyUtZ%tE<w+h@GZw;Hlx>fNtj`xnp=lphYXPIZlX&GOkvFro4FMh!KvP#@<>@C&g^$Z-(dUB^o+4o~w%k#nhc-HMFAIUsB+sMAU?Yq-F?thop(;k>6@Au3HtlL2~WuJSczSIX*lko*D<nwR%FVcT!9``?Qze!hk{3u7xbBl7Udt&3|{5%feKJF>VImy>~HJjtT8y3rXxRt?ro)ylz-T%1EllajI_D^5U^Y1y9!q@8^)?4aJOSr$-)q2SLiaCCq?W2txZx2qF{pF=@Qm=ZC<30O^$oV{5fpvTCaJlYD*X4E1I&+M#=ck!G_H?Twum9~Htb4-4<outUBJ<}yKFa&Va?5r6>1&y1^bywWtVQy^zHTh@xNX+09nIx)W7q<DUxAkjd0!j-(+UXkvhE7nOV;W0-UjE-a~&FWr*xyftS%?NU~8URx?GdG@tm@|-j{mNlWnX&PUe1Sg;kdIXY~K%uxftwys!wV7cbHJo)z9o>Omc~KBM%ICt9De!sDfWDOY<g*x@~-ZuDV0yr0yKzGsIgIr+7ItMob@wSKE~qu(k$G*0WcN{@J`^;J8(zu)W03x8ee=6T!E+y1Pdw;kO)Z#%l{p?=<W^i~(~Tzh&~i;sDrpSK-7K1q9im4;_t_P0Nk?mXW!2A%HgqyOsp9<fTs8+~5su3&ASE8RGsl;tVU_odE_5gVj#oR^f|euQ?u@<eXC!hYlY=IGXmT<yG<*X(bsd(XWk&xhxqC9;irD)SiUOjB3q%&00woX0rFn!0n2Ep6H1s=qo_x=|NOH|kyKMm;J$=<iy+m+5+)D&0J{C|&OZN;m3D>E?N+EWg$Vly3YUQ98~)>O8D;y-v&W80R8KH|kgE#_tiOH=VDYt6eeOullQNr5kmvbo0FG=tf;D-KcA&8+EO8^SoN7YxS;l<M*=C+uhNAU)!;{yuYn;<JfP1EbAgK_OPr6<GqBbJMSe*W6xic``>uK5qE`k?R`jJ?Jdv9f@395s#zAHiWO|7rue+#A(8$Z>;DzcxVZo76;GSE`2Y76&&%Q(779!e=p?X+rW#lT->U+N0>QBLz=QCasz4`vj{FS~b3ova0`DQ;0pwf={vP~!xCXLQ!57fB6-cM;1xw>h@YaCi?<SBVFb9^#9g!yopUr_roR;7Pixx@3(W-%WM1IO$2lfT<%>o+*GGNoe|0J*<-?<;(w*c`w5c>y#wE}Mo%n(>X`v@Su3ObEv!OjP#Ih>90eDGPAuZ5V)g+BATU0|ocK42&2eG7bhfbH;a!8jlGeefd!hXjs-9~RgJdk}mR>~3Hee48+S7j`fBe$2^UU<dSc%+ms3Bj$Ccz%+q*z%<P7bok~1GvQw;u-r#qj@UH<zZZB%ps_%>K%@ZG^GgD40pcy7)3^(40yyoDZWt$klTLet_KLHwh|_)w5ojP#2_Q~;tu}lWfDrg=W9))`9=x1DfF=KkmltRR`y6;(*or_S`08RD3R@YRYPliCmBC4;+NU~pdIE8(^{xWl1=<6|ss3&F+5uhRZ!QqyqsJgNLZGQdZBy>$smRqGJP|evJQ1AUg=GuGV;m2S_%eYB@FzmA2V2XB$74*kh7XU%m~4G;>H`^A<8I)z|Dpuatg>E|246FQ$?!*kldq*f5BOWcz6e_#ygJ4;VWYrng4cm<4NiNK_Gty!=fSCVsfJg<dcZ4VO@d%Mfm1)B9<T@?PQ9Wc)~qsYdvFi(I=yHQK0`H0we8d?ajI|H>r^w9U=zUS!SB>5@!jwx;9e4NpTwz$QNPNA-2hJO7mD?*2i_1qikS+V1)huX7TE3JwBB`*uNHVHK1Xrcu({w=$01mY5UdmN^_J{sn*rj~<I>>E0M^4_9iOcY8v?!#F_U4_zz<=K*TSv>r#f$rb!(0_BTjX(O<*-_0r*nbt-xydw&J^&!cGRCi}hIvdk}mj_&We`dOpyeq#pY`YyfzmKod*u`4_>dCZfUX15FT{jX7Ti<l;W4?}g#Mp981+rsvcy+{-T9PXTgLzDBU+!1IxB3$P8};q=q`ur<J4xbE73Q@ihCoi@R)v&x>0n{XYQpl`+Z2O?h}^0;vQ1-PyPTo3Wz2*e7!1`ux}Fi~K<z+!<(0!swm68Nn^Pk}grVFIrU41%Tc2!Y=T41hieoP52&9Y2lx0>t|R#CwC29Rd&^DDVcx!+{~tN5Yp3yaE3h_(lUG;U5Q|qo+b6>jobOJ{C3wd@T4V-1`WOQ@}|dD)1)8BQOU;VUxg<Fdl$;=mS0goc#U3o%!j5*un78{rBxzu6%I7fBN@u*`J3ti1yE7^OO2d4&P7S6S>q6kiI=DP#+KlQ=S`71L}^}zX6nA>Lv'

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
