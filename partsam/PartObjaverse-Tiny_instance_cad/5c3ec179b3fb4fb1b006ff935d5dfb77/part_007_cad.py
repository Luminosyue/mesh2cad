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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5c3ec179b3fb4fb1b006ff935d5dfb77/part_007.stl', 'relative_path': '5c3ec179b3fb4fb1b006ff935d5dfb77/part_007.stl', 'source_sha256': 'a137d6743da8ab270a1ed3edeeac662e027e68708f6ac42b3fa7f621bd112df0', 'input_faces': 148, 'input_vertices': 147, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-4.057546615600586, 2.050689697265625, 8.719139099121094], [1.5202646255493164, 7.39093017578125, 19.946548461914062]]}
GEOMETRY_BASE85 = 'c$}q}3s4p36~~t=C;}=V8u5802uM&tNF?~WRigwVMbY?5^s0alh!VJ>$ir2MB4R=!ncCXuttRT2$;%;z@s+Ff5j7@gtP@CTNOc-DQ4|#+qW1g#|6^)8?M$b=GymD$-=00+`OZ1}?e0xZY~>zc@YmZoTkcpB-`+5^e2f4iH!a&SZ+2Qv{{>ljZiX+o{yp5TPntM3d5W8nYvhNfrsd4e4vn*h4oQy<jj)EMFU)pi&s;ELVRmYo=A&n3=A<c}Gk0cInmP`PiWwAPjqV#^EwuiRKQ9%6c{R@0rDIvKt)oqCTu;6duD8yFe&oB>chSej$kpIxNiTAHUJo4a?GT3ZyStKKECjbTm%`o^EPPct{MeqRz03bW2k=XqIqn@F@VdFp<e4*k;D1=r0BkdklNTTI#_`%)5s359LGtns;Ky8k7u<UAPJ3{lO!#rFTZVXy9&eKWF^loXT?mGKaXES8r|@HQ4(+42_QnG8kk=W1w-(r&pUoz(-2!{(dr64XI(V}1dGx<HAMw~42a<Q$+YZN*-7#PDT`%&0P3;liU5_Y?yL3-GaED(Y^5Q7$hwGwZ$$e@&z`i&hahl_9`hcIP?~M6gT-G1))RdBsx()y4h7aN2?E5_VZiheo-foD*xSf;9-(G_F4ZkywV}4JBk{3^F1HT;?ur97X<gv_;dEz_Ro9BCzdoF;zt*D80Ib$IY+0MFeHIPqd-pAhHL%x8$kzLF_ytkHoM?JX9S%EmM`9<W#+kD}F>r?Pkw<wqVg>CJbulRwm|NSKLbDR7S-<561gRME9-18Yv91lB-y4ZX5Cih*B{xKF+!@oW2G4k94m~Y+92;{kL{{=7bh#T<Z+8h;%?bNg6S#fO<M@Aa!J0ytw@UxGBH@o1+b~%vT`h5W6e770%wcYASespIi@V(v0XKif@KDre3a@{|PKB==^_5}Yr%pLK+U4VRAH-1ZAw3hV>oDhWb+pEbhy#af(XEWkAXCEUEzTXP|dsz^_b9EK@p<%4!{5kMbx2b}>WEJjHTR}Mb!T!!ja^L6S$2{Xe|I`&9Zv!4)gZbJ!K8JdlU3ZX2gwTE>`^Pr@53RxNKCQuP&-4DhxPrW(7vi@UbY|Uux6T86M=9)$Ba7K5T_=&>TFLsxZHR_HA8&V#8_vEx-2y-MkRMuse^H71%RE)j{P)izpPbA4y*h>caQ}t{{6pSHw!<fSBc8Xa$V1+OALoq=$fq@Y3;8JCN3L~W!QOQ=fV}A-@?#{Nrk|x=<j(QzlWQ{=e~pg;-g1TW8rML+<iY(<_3`z~7RKKO>xL1zoIK)|8^)WOi}@Ob6Yqh~-%bA$*J51bav$;+99$owv%t+!-N-Xd1N>Y)>SZpnkXO$Ew_aYzb;EMF1-#-l&i7hA{p{LFemxrf<I4980>3wn{FWEj`P$8lC)khtr$z8@j=hb#m~GG91y_xL{6`*VUj<Jguc(5(Yf>JcYdIn0)q8P2n%^|ik9T+S$@iK6s*T8}(Wa&u{BR2UF#0y*T=5n8h~@BOOC8T~_x;!e{`up`vn`F!J0tLG@`2N_&O3{IksssdO7aZ_$a9^!8hvHVedZ>3r91EIk1`ogN^Cv2Kl{gctAY8sI_nyEm8|E*H^?I{Tmhfu&-wO_V%_fyy#Rh-G5a=Y9LLS@B~R^+ah+e-Ic~)EzkwIKBYyj7H^#qn={Mj;J>#tP!+mEQSXB$2Ucq(a{5a&zIQK~n_@1%Ivnwc<{!8Bb3wTo*`($ep?MH1PFW%4fu;wV^ubM*c8OeS=(1v+-)Sm^<=Df@=$I?&ivNN>5X#p?Kpr6dcr@^mOp?{3}YV?CqS#pZ@gZLcx*u^+q?|cp(Fu|L7tfT*mjAM**JN?&;;eA(Cd4&De8r=2eE&7ic>H?qJg80p*Eao#T=>T|HDf_3~f_2_7H~oqEnFVe<*vR)BqcCT<-fUUK{@K?^`;s~Pz+ZJDZ?@#?9JgiIpTS4PdSTqtZ!!<oPmhA{-UWNtG(Xzge2#-B59kX2Wq$0FHxkZ(U-!a$h1tEDekwe_0`I<&&&Rv7*bmN=XTi(<&gcHYP}&#8pQE1#$g?r%4EeXswcw6Q_Rqm+@@rH63ce$eeg@rOoX>qp-sK4HQ`^PH2<AEJJb27K&Udhd@r2(e59k0t&bBWx|9kwu1K;LAf7Z2rK>sUe)G=@S*(aY&XC9`W`X0Qf6Z8B*BK<fm7r^_!!}rYPC-8hUQr{<EQjPh#Mx=0F4_e40`2K99?Wg^Z9v8t6$@68&KJtoFKd>%0`M$cx$+{o;_!9Wn+dbfa+<NxOl!7bZ=4L+k6S6|USHJutc;zv^mkwy+d>eZH1iqnxaqe8oc?BkrCztd7+8xYs^A21EcNW6G?M6G^kL8E!*$<cSUgSz0!u#U5=XKWWedNb@+JGPP>PYgKAjIQxc#_Xs*#Q382KGbj6ZA7E>?Zg=*4LPOkn^paKpw;Aj+vfF`vN<;lixMQ)+D}Hr{~@V4<5lj9KiU^en-i>@IBUOT+8Q3{^&;V$@0DM`8tm47*B2y|0iFgee=mX;0^qaFdcj@n4w`!;Ek_x-RpM@?_-8r3i;1cch6Iyw&Y)Zg?9d^#F5oTy>TkFRbQd$GavZ`)lmN)ZvXu!=)9Q!@)I=n|NR7=uVR>~G*KyAX|a-K%Vl4)5T#B^y_EDceRVmM;&hqie4^~fiCrhLOH<0x^HqvgicpHz<xxtO>yqX8d8JWGBbDYTCFr)1{dhT-uJo+ZixTrR+1G5A96zTtUe`v+uCz+2NNI`EtFo_Irc$2pOo?Hp9BZ4GMDrxJRbszFxVBj-K3|jlbz-+#@|P#RSIGWinS-8_L*}<k_BGFyd@YdN>$znp<tx1`b9`CO=ZlTr4^r||>ZlZ|)JOI^3ip)y^pW$P!rhc&mBPeFYo&INoDY(7p~5>!z50khy+2NT=zmpOiBEmK{<W2B+KKN#r6{EVvK=XP)x4WhU#0F!k3C|eS%MsETipw~-bn`gt*26?!M=M|_J=ABGuR75MUi6rl)+xKiQnl`hhn8QQV$)sRbnca8tdA=A^Wc@l?huTb9GnpkojBWSpPbRzlUQi6W@Ks{}U32KAx>KR%x`-LZw%fOyT-?iX4}TugArg9;3HXjM6}*{^BP_YzE3WDN0k7#wbltdf^c^TKI4oCspaUveh{%P%2ScD%UNQ>q;aaI!}d4rDD5C&gnVK5ccr8*>de#xwcen%fvoa=4;B>rp&j8%+p^fT&b&47eoKu$9-?5XOxC04OaS%%x{d?Yu-<4<1O{_dc=pfjG_H^mTS7mH9ceuf61xN`3M>3Y1vPa@xz4;mNCbOkA9M8T_1~#`LJ*N#b=Dv;9<>%OC9ujr`Jo}_xc{N8|-1d*6DRY_q$%V^;)af5Z&W?oz`ovUXS$JqSu)<vekXKLTq#8x(xBFx07VQyZF)TxxO#;qbpFh-DF?ew3hQvNi0vweou*IzRW?dY1wl8qQtC^^?IhCCHg+r_iBKQtFMofbCHsRILSjViA&q2$sFu5UcBUIvRtFr_T)r2OF*mt^q28Jf2O{PfAt6Qzh3$4$NZyLu2Q~!dFUr6dg#2UVq36qN9nFI{sD?P3F8'

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
