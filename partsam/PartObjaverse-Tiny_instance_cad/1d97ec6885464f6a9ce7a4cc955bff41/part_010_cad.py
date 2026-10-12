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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/1d97ec6885464f6a9ce7a4cc955bff41/part_010.stl', 'relative_path': '1d97ec6885464f6a9ce7a4cc955bff41/part_010.stl', 'source_sha256': 'c30498eb023d6b9584be83359b829055199541bcf59276c9a170fea0ce4c4028', 'input_faces': 136, 'input_vertices': 121, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.5922054052352905, 3.184648275375366, -0.6011466979980469], [1.295830488204956, 4.452774524688721, 0.6616527438163757]]}
GEOMETRY_BASE85 = 'c$}qJ2~bt%6~5rgCaB;>)tiXH1s71`UapEu;|7X~X!JgTr=W;D9^f*@Ta&moE>m?}lF(-`X6hC(8f!56#AssNLPD&Hl8Z~!SaCs<G3nI)=R1d1JMB!TeaxBj{ogzP`Oi83`TzSa@xyD?4%PVcg7*Gr+a_EH&@_@jEmX@(bGg$~(sDY_o-@x!3jt4`8ohSZxRLP_eY8AnL1b!LPKqnCj~?02*()+ik920a+%CuLsadYnG~$OiX62+QK4*qwPMR9Gi;jto(z~^f(iiIg<Huix;7zK&dW2$G?g%!NGF*<*Sf#DfAHaKZjx`|OJ~tV>IkOzR6;lp-D<SVR@!lpy?5B745b!tj67a?EFu!C{0P)^U$yeZi?nd^rbhjVu`%Edsc=LMjUZ40t;yovaU4{Lb)!@yPv#__9Zv2eKcJsH`zDM^U;?39VU59=1MI8Ttu87|ZS_<C#iHp~rG8A!o^BWg}|7#ZW-$fu!^LWFHG&Tm#WPaoV<ZB;$`x@-^B+e_zi8##>0XFP=jpaBG<-osrbX+Cbdxi}HZy(}y?ZM->!oI1&{uh6Z_`M?&cs#i;v@tidA?mYdTRHjBj41ZAswLvlHuk%Q{2xYgJlB@O-gC*f4EC|DIi53tyl&8^?Du!!tUo>id&4X_iM+C!GanZQdr$tDgQ(--Fy?Q*23|}28}jwojlk<$&+)n^efN<cy`TZF+x7|U^*zTg!QMZJ^Xs`6_IlCO{fIv#fa7<kgV)v_{0i%h`o0q1SH6LKb*K9{@?UWdyuEHW_Sf()`yBSQJ_m0s3gLZ!<qCK$+ED>Nivu|R+XuLBmh>sd_oe>a4-xx0j?0ZNApX|Oo914QJNj-J=4JYEect(y>$2=bDfFTG;Ejtr+0Vh)Gw|cjydJh)_BRx9>4B-dzl&BOUn}+D3FMVjkK-Kkf%v%r-g0!}b<?@-T7!$=^^CC`zqJtgYbmF}dtCF_e#0&9&x#Mhd-qiHIqkU_`=UK6Tnqaco%?@f828&J!Qjn^FLCb7j<<4gzRGfo@qK14_tlyU@UK<u2Cwh9$MJWV&;B2{4`JT@smRwpmdX43jdd7&P%!)PoyvI?jP??5FB^(@tp3|^Z+Nzw;Jqt0BOaq=r3Z2E>U|#f)A#{wUsVEoyW2qUR?<4ydpCr`UOUki_lg$L7xucRobM&S4&c3QSMj~nWM={LkKBTDZ~Jop=uvWC+`Ir@kD1N;UQ&!Yc<bBXwK=!g{w)J_(A{Hj4;ibHxc~3Opbp+y=f4NPB7pD7%hOSRJ-8gay<k7zdzbpZiTGaXcpLeSP4q{dd))d4_IfAqp3@~9e~X}_u<QHaFW@8Y^Szy$!F}s|1l|a5#qqEFme1RopTOH~;<&H28q62}4Bm{&;QlGz!TWy2=Pvk+>)daPbmVKd-^RQvk<WFPMx5`OH>!}w(JGFoXgZ(AnDxy6=^EGV#}@EoRtMZioKx<?-g7sV`y?(DyjG9xt*kKaw}NlM>%ZLLd%OKK-mj`F;H`02Ij@_+u(yW&;Q`j&@B`ngPVPf}(+A+~!b;A|^oPAsJ>wz#bid8<zc-nmH-oal8xL)c=g+kzo|tOzr8i-3R!n63sy^T?gYE73r+DsI1rr{D|N0I;Uj|0qz<l3V!F!f1#{K5qm3Ip9yygJ!-MbIZ5&L4(FW~=r3V1zkG{+f!f$tsX4EEn6hM${{+{d^N)4^-YhoG-K?ONkGVy0(+H+{JeJx}MOudHq}**-E7eQOWuSb_KwW`Q>bf5rLU4P^g`nc(eq^Vv^%(I)iCvDwVO7mj?bRz*06`u1%0Ux&}T)#IlU)JM<dywYyKUO#>IWB9+4&w1_e<M`v=MZf7)^Vm;Z5chf6IXria+Vh#e_6zEuPrJvzAAbK^uBUY$e(dl8cpljIUg!E(4dK3OR-4ar;c{Mg+78~YFKaD9KGsUE!;@%^^WNa^ux_)}Tu-AN_sN!qtC7!R=Czd*x&NCS=HCx*ZsPj1DL|aslUw}!yZScAIqYY)PtL!L_0ANqpGlQi*Iwwt{i|mea^1S#M*rx8%D4|VGq1%4$nT=;Pcc5SmH9J#Us)k9q93dWe`LPj4L&ai6Zw3d+QIQGd7pm|e3Wtu@u%<PeBbTJ@yAU$0lsKA+aE~f_@A!l`%~Y;yn8?U$sBwD>y2aHv+E?UJK_ZVm;?8+{o@L*XWhsA`z`Pzj<fzo_%Q=p?&bS=AJ;Q(G~Y{QrRNa;dFHKxoqUd5?GeAx{{Y)}8Or<KIsFvhQ^lND@;ua2tNX>-*!bt(3Vs~9WvyLTO;O^f-U^(KXI=@2q)(0h_pb!$-T%8+f^IMWzpn&MRSd0^v{cembaN#M)JjUS1d}$E1Sv^X;t))l-fn!9)TVL>mh@D{nl@eLgoqB3HE6A02__w`q>+*gnbSygi1;F(^#zmmlQ}fEiD1$#l=zCBpJ38~@*UX(3ntx6NiDGp6im8-5`P)jVA2g`p8qqLbYmqQl(bdSMKI~kvPQ7jG!q@BWSo*@C6fh{o}#3`l3y#CAei)csrOj1b%-YWF~U0pJEYciWgim+CrIrQ#V%EFs?_>bSu0s^vaB&t?4}EzF8fqpe42tysdb9PJ3;US@i#~2X9y;psie1(K1$*QlO80#$mcY{(`0Ybl_bd;>7rAlw%JPDg59#ufil-A*eQFNqhzYYlp}hM?9FWP6(+iw%%Qn61e2z{&yqSP2~Lu@a+RdX8o8o#B(9nAom+IS<Vy4N1m{WIw7yH`WQ%socVshH@LY+{DL7wnzQj61uuCxMSt2g+Jxes@PyJX&Nj=dt?k++&S$G=9h$il35yJhHM2Q{Q&{awMUUSxI+*&YcT`=hv1e1PIFzGgeNk<4K{gPnPT?LcwDVTJuVA6vHlO8IV^lt={9xj;lNWr8>3nooH+)?8*R&x*1I9f32Ng{;12`1e`FzLR6NmCC+O8hnX(72so((MJ4?xdub<W-X=jR%Mj9w<DG4UNy)5RK2;5E%~>A^eI6;SnN)M~M)Q7a^P@LYVqFez=csXs!SBFSCDsEP7}>_Ybsxo%#G@_1T$Cl%sz<WaEd|!L!F#{ZSJ~(@m@W9R{N@{{'

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
